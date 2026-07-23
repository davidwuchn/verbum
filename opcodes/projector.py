#!/usr/bin/env python3
"""J-space PROJECTOR — the full Jacobian construction, matrix-free.

    λ projector(model, layer, pos, k).
      J ≡ ∂h_target[pos] / ∂h_layer[pos]          (Anthropic's J-lens object)
      | matrix_free: randomized range finder on Jᵀ (vjp-only, batched prompts)
      | J-space(layer) ≡ span(top-k right singular vectors of pooled Jᵀ samples)
      | P_J ≡ VᵀV | workspace_fraction(x) ≡ ‖Vx‖² / ‖x‖²

Closes the s269 projection gap (state.md s269* / opcode-jacobian-jspace.md):
every prior J-space claim in this project was a MEMBERSHIP test of hand-picked
directions (``broadcast_kl`` = dᵀJᵀJd ray samples; ``W_gate^T`` pullbacks) —
J-space itself, the *image of the Jacobian projection*, was never constructed.
This module constructs it.

Method (randomized range finder + Rayleigh-Ritz, Halko et al. 2011 flavor):

  1. ONE forward pass per prompt batch, with grad, hooking the post-block
     residual at each requested layer AND at the target (penultimate) layer.
  2. For each of ``m`` random unit probe vectors u ∈ R^d (target space), one
     backward of  Σ_b ⟨u, h_target[b, pos_b]⟩  yields — for every requested
     layer simultaneously and every prompt in the batch — the same-position
     row sample  J_b(L)ᵀ u ∈ R^d.  (Batch rows are independent by autograd
     linearity; cross-prompt terms are exactly zero.)
  3. Q = orth(pooled row samples) = the candidate row space.
  4. RAYLEIGH-RITZ refinement with the TRUE action of J, no jvp machinery:
     J_b·q by central finite difference — inject ±ε·q at (layer, pos_b) via a
     forward hook (the same perturb-and-read primitive as ``broadcast_kl``),
     one graphless forward pair per q covering the whole batch. Accumulate
     M = Σ_b (J_b Q)ᵀ(J_b Q), eigendecompose, rotate: V = Q·Z. Validated
     against the exact Jacobian in ``self_test`` (FD error ~2%; capture
     0.75 → 0.88 at k=8, m=4k on pythia-14m).
  5. Top-k rows of V = the consensus J-space basis at layer L. Strengths are
     √(eigenvalues/n_prompts) — per-prompt RMS gain of J along each direction;
     ranking is meaningful, absolute units are prompt-set relative.

Honest scope (inherits s263 discipline): this is an OPERAND-side instrument —
it characterizes the workspace subspace. It never feeds the opcode classifier
and does not gate into the VSM tree (S3: observe first, null-floor later).

Ground-truth discipline (the move babel-codec could not make): ``self_test``
validates the randomized construction against the EXACT Jacobian on a model
small enough to materialize it (pythia-14m, d=128), via the identical code
path (probe vectors = identity basis ⇒ rows = J itself).

Self-contained: depends only on :mod:`topology`, torch, numpy. License: MIT.
"""

from __future__ import annotations

import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import numpy as np
import torch
from torch import nn

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from topology import ModelTopology, detect_topology  # noqa: E402

__all__ = [
    "JspaceBasis",
    "capture_residual_centroids",
    "jspace_bases",
    "jt_row_samples",
    "random_vector_fractions",
    "self_test",
    "workspace_fraction",
]


# ── data model ───────────────────────────────────────────────────────────────


@dataclass
class JspaceBasis:
    """Consensus J-space at one layer: orthonormal rows spanning the subspace.

    ``basis``      [k, d] — top-k right singular vectors of the pooled Jᵀ
                   row samples (row space of the Jacobian ≈ the directions at
                   this layer that the downstream computation reads).
    ``strengths``  [k]    — singular values of the pooled sample matrix
                   (relative units; see module docstring).
    """

    layer: int
    target_layer: int
    k: int
    d: int
    basis: np.ndarray
    strengths: np.ndarray
    n_prompts: int
    n_probe_vectors: int

    def fraction(self, x: np.ndarray) -> float:
        return workspace_fraction(self.basis, x)


def workspace_fraction(basis: np.ndarray, x: np.ndarray) -> float:
    """``‖V x‖² / ‖x‖²`` — how much of ``x`` lives in span(V) (V: [k, d])."""
    x = np.asarray(x, dtype=np.float64)
    nx = float(np.dot(x, x))
    if nx == 0.0:
        return 0.0
    proj = basis.astype(np.float64) @ x
    return float(np.dot(proj, proj) / nx)


def random_vector_fractions(
    basis: np.ndarray, n: int = 200, rng: np.random.Generator | None = None
) -> np.ndarray:
    """Matched-random baseline: fractions of random unit vectors (E = k/d)."""
    rng = rng if rng is not None else np.random.default_rng(0)
    d = basis.shape[1]
    xs = rng.standard_normal((n, d))
    return np.array([workspace_fraction(basis, x) for x in xs])


# ── batched forward with graph capture ───────────────────────────────────────


def _last_positions(attention_mask: torch.Tensor) -> torch.Tensor:
    """Index of the last REAL token per row (robust to either padding side)."""
    t = attention_mask.shape[1]
    return t - 1 - attention_mask.flip(dims=[1]).argmax(dim=1)


def _ensure_pad(tok: Any) -> None:
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token


def _graph_forward(
    model: nn.Module,
    tok: Any,
    prompts: list[str],
    layers: list[int],
    target_layer: int,
    topo: ModelTopology,
) -> tuple[dict[int, torch.Tensor], torch.Tensor, torch.Tensor]:
    """One grad-enabled forward; return graph-connected residuals.

    Returns ``(captured {layer: [B,T,d]}, target [B,T,d], positions [B])``.
    """
    _ensure_pad(tok)
    dev = next(model.parameters()).device
    inputs = tok(prompts, return_tensors="pt", padding=True).to(dev)
    hook_layers = sorted(set(layers) | {target_layer})
    store: dict[int, torch.Tensor] = {}

    def _mk(i: int):
        def hook(_m: nn.Module, _inp: Any, out: Any) -> None:
            store[i] = out[0] if isinstance(out, tuple) else out

        return hook

    handles = []
    try:
        for i in hook_layers:
            mod = model.get_submodule(f"{topo.layers_path}.{i}")
            handles.append(mod.register_forward_hook(_mk(i)))
        with torch.enable_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()

    target = store[target_layer]
    if not target.requires_grad:
        raise RuntimeError(
            "target residual has no grad_fn — model params frozen or "
            "forward ran under no_grad; the projector needs autograd."
        )
    positions = _last_positions(inputs["attention_mask"])
    return {li: store[li] for li in layers}, target, positions


# ── injection forward (graphless J·v via central finite difference) ──────────


@torch.no_grad()
def _injection_forward(
    model: nn.Module,
    inputs: dict[str, torch.Tensor],
    positions: torch.Tensor,
    layer: int,
    target_layer: int,
    topo: ModelTopology,
    delta: torch.Tensor | None = None,
) -> tuple[torch.Tensor, torch.Tensor]:
    """Forward with ``delta`` added at ``(layer, pos_b)`` for every prompt.

    Returns ``(h_target[b, pos_b] [B, d], h_layer[b, pos_b] [B, d])`` —
    the latter from the *unperturbed* read at the hook (for ε scaling).
    """
    store: dict[int, torch.Tensor] = {}
    b_idx = torch.arange(positions.shape[0], device=positions.device)

    def _mk(i: int, sink: dict[int, torch.Tensor]):
        def hook(_m: nn.Module, _inp: Any, out: Any) -> Any:
            h = out[0] if isinstance(out, tuple) else out
            sink[i] = h.detach()
            if i == layer and delta is not None:
                h2 = h.clone()
                h2[b_idx, positions] = h2[b_idx, positions] + delta.to(h.dtype)
                return (h2, *out[1:]) if isinstance(out, tuple) else h2
            return None

        return hook

    handles = []
    try:
        for i in sorted({layer, target_layer}):
            mod = model.get_submodule(f"{topo.layers_path}.{i}")
            handles.append(mod.register_forward_hook(_mk(i, store)))
        model(**inputs)
    finally:
        for h in handles:
            h.remove()
    tgt = store[target_layer][b_idx, positions].float()
    lay = store[layer][b_idx, positions].float()
    return tgt, lay


# ── Jᵀ row sampling (the matrix-free core) ───────────────────────────────────


def jt_row_samples(
    model: nn.Module,
    tok: Any,
    prompts: list[str],
    *,
    layers: list[int],
    target_layer: int,
    m: int,
    probe_vectors: torch.Tensor | None = None,
    topo: ModelTopology | None = None,
    batch_size: int = 8,
    seed: int = 270,
) -> dict[int, np.ndarray]:
    """Sample rows of Jᵀ = (∂h_target[pos]/∂h_L[pos])ᵀ for every layer.

    For each prompt batch: 1 forward + ``m`` backwards; each backward yields
    one row sample per prompt per layer. Returns ``{layer: [n_prompts*m, d]}``
    (float32, CPU). ``probe_vectors`` overrides the random u's (rows, in
    target space) — used by ``self_test`` with the identity basis to recover
    the exact Jacobian through the identical code path.
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    bad = [li for li in layers if li >= target_layer]
    if bad:
        raise ValueError(f"layers {bad} not strictly below target {target_layer}")
    g = torch.Generator().manual_seed(seed)
    rows: dict[int, list[np.ndarray]] = {li: [] for li in layers}

    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        captured, target, positions = _graph_forward(
            model, tok, chunk, layers, target_layer, topo
        )
        d = target.shape[-1]
        if probe_vectors is not None:
            us = probe_vectors
        else:
            us = torch.randn(m, d, generator=g)
            us = us / us.norm(dim=1, keepdim=True)
        us = us.to(target.dtype).to(target.device)
        b_idx = torch.arange(target.shape[0], device=target.device)
        sel = target[b_idx, positions.to(target.device)]  # [B, d]
        inputs_list = [captured[li] for li in layers]
        n_u = us.shape[0]
        for j in range(n_u):
            s = (sel * us[j]).sum()
            grads = torch.autograd.grad(
                s, inputs_list, retain_graph=(j < n_u - 1)
            )
            for li, gfull in zip(layers, grads, strict=True):
                gp = gfull[b_idx, positions.to(gfull.device)]  # [B, d]
                rows[li].append(gp.detach().float().cpu().numpy())
        del captured, target, sel
    return {li: np.concatenate(rows[li], axis=0) for li in layers}


def jspace_bases(
    model: nn.Module,
    tok: Any,
    prompts: list[str],
    *,
    layers: list[int],
    target_layer: int | None = None,
    k: int = 32,
    m: int | None = None,
    refine: bool = True,
    eps_rel: float = 1e-2,
    topo: ModelTopology | None = None,
    batch_size: int = 8,
    seed: int = 270,
) -> dict[int, JspaceBasis]:
    """Build the consensus J-space basis at each requested layer.

    ``target_layer`` defaults to the penultimate block (n_layers - 2).
    ``m`` defaults to ``2k`` (oversampled range finding; the Rayleigh-Ritz
    refinement makes moderate oversampling sufficient). ``refine=False``
    skips the finite-difference refinement (raw pooled-SVD basis; cheaper,
    lower top-k capture — see ``self_test`` numbers).
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    tl = target_layer if target_layer is not None else topo.n_layers - 2
    mm = m if m is not None else 2 * k
    samples = jt_row_samples(
        model, tok, prompts,
        layers=layers, target_layer=tl, m=mm,
        topo=topo, batch_size=batch_size, seed=seed,
    )
    out: dict[int, JspaceBasis] = {}
    for li, y in samples.items():
        # Candidate row space: orth of pooled Jᵀ samples (strength-weighted
        # union of per-prompt Jacobian row spaces).
        if refine:
            q_basis, _ = np.linalg.qr(y.astype(np.float64).T)  # [d, mm]
            v_full, strengths = _rayleigh_ritz(
                model, tok, prompts, q_basis,
                layer=li, target_layer=tl, eps_rel=eps_rel,
                topo=topo, batch_size=batch_size,
            )
        else:
            _, s, vt = np.linalg.svd(y.astype(np.float64), full_matrices=False)
            v_full, strengths = vt, s
        kk = min(k, v_full.shape[0])
        out[li] = JspaceBasis(
            layer=li, target_layer=tl, k=kk, d=y.shape[1],
            basis=v_full[:kk].astype(np.float32),
            strengths=strengths[:kk].astype(np.float32),
            n_prompts=len(prompts), n_probe_vectors=mm,
        )
    return out


def _rayleigh_ritz(
    model: nn.Module,
    tok: Any,
    prompts: list[str],
    q_basis: np.ndarray,
    *,
    layer: int,
    target_layer: int,
    eps_rel: float,
    topo: ModelTopology,
    batch_size: int,
) -> tuple[np.ndarray, np.ndarray]:
    """Refine span(Q) with the true action of J (central FD injections).

    Accumulates  M = Σ_b (J_b Q)ᵀ(J_b Q)  over all prompts, eigendecomposes,
    and rotates: V = Q·Z. Returns ``(V rows [m, d], strengths [m])`` where
    strengths = √(eigenvalues / n_prompts) — per-prompt RMS gain along each
    refined direction.
    """
    _ensure_pad(tok)
    dev = next(model.parameters()).device
    mm = q_basis.shape[1]
    m_acc = np.zeros((mm, mm), dtype=np.float64)

    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        inputs = tok(chunk, return_tensors="pt", padding=True).to(dev)
        positions = _last_positions(inputs["attention_mask"])
        # unperturbed pass → ε scale from typical residual norm at the locus
        _, h_lay = _injection_forward(
            model, inputs, positions, layer, target_layer, topo, delta=None
        )
        eps = eps_rel * float(h_lay.norm(dim=1).mean())
        w = np.zeros((len(chunk), mm, h_lay.shape[1]), dtype=np.float64)
        for j in range(mm):
            q = torch.tensor(q_basis[:, j], dtype=torch.float32, device=dev)
            tp, _ = _injection_forward(
                model, inputs, positions, layer, target_layer, topo,
                delta=eps * q,
            )
            tn, _ = _injection_forward(
                model, inputs, positions, layer, target_layer, topo,
                delta=-eps * q,
            )
            w[:, j, :] = ((tp - tn) / (2.0 * eps)).cpu().numpy()
        for b in range(len(chunk)):
            m_acc += w[b] @ w[b].T
    evals, z = np.linalg.eigh(m_acc)
    order = np.argsort(evals)[::-1]
    evals, z = np.maximum(evals[order], 0.0), z[:, order]
    v = (q_basis @ z).T  # [m, d] rows, orthonormal (Q orthonormal, Z orthogonal)
    strengths = np.sqrt(evals / max(1, len(prompts)))
    return v, strengths


# ── residual-space combinator centroids (no pullback maps) ───────────────────


@torch.no_grad()
def capture_residual_centroids(
    model: nn.Module,
    tok: Any,
    prompts: list[str],
    labels: list[str],
    *,
    layers: list[int],
    topo: ModelTopology | None = None,
    batch_size: int = 8,
) -> tuple[dict[int, dict[str, np.ndarray]], dict[int, np.ndarray]]:
    """Last-token post-block residual centroids per label, common-mode removed.

    The s269 projection-gap fix on the OTHER side: combinator content is
    measured in RESIDUAL space — the space J-space actually lives in — not
    pulled back from the gate register through ``W_gate^T`` (the criticized
    one-map pullback).  Returns ``({layer: {label: centroid[d]}},
    {layer: per_prompt_states[N, d]})`` — states are centered (grand mean
    removed), matching the house common-mode discipline.
    """
    topo = topo if topo is not None else detect_topology(model, model.config)
    _ensure_pad(tok)
    dev = next(model.parameters()).device
    states: dict[int, list[np.ndarray]] = {li: [] for li in layers}

    for start in range(0, len(prompts), batch_size):
        chunk = prompts[start : start + batch_size]
        inputs = tok(chunk, return_tensors="pt", padding=True).to(dev)
        store: dict[int, torch.Tensor] = {}

        def _mk(i: int, sink: dict[int, torch.Tensor]):
            def hook(_m: nn.Module, _inp: Any, out: Any) -> None:
                sink[i] = out[0] if isinstance(out, tuple) else out

            return hook

        handles = []
        try:
            for i in layers:
                mod = model.get_submodule(f"{topo.layers_path}.{i}")
                handles.append(mod.register_forward_hook(_mk(i, store)))
            model(**inputs)
        finally:
            for h in handles:
                h.remove()
        pos = _last_positions(inputs["attention_mask"])
        b_idx = torch.arange(len(chunk), device=dev)
        for li in layers:
            states[li].append(
                store[li][b_idx, pos].detach().float().cpu().numpy()
            )

    lab = np.array(labels)
    centroids: dict[int, dict[str, np.ndarray]] = {}
    centered: dict[int, np.ndarray] = {}
    for li in layers:
        x = np.concatenate(states[li], axis=0)  # [N, d]
        x = x - x.mean(axis=0, keepdims=True)   # common-mode removal
        centered[li] = x
        centroids[li] = {
            c: x[lab == c].mean(axis=0) for c in sorted(set(labels))
        }
    return centroids, centered


# ── self-test (exact-Jacobian ground truth, tiny model, CPU) ─────────────────


def self_test(model_name: str = "EleutherAI/pythia-14m-deduped") -> dict:
    """Validate the randomized construction against the EXACT Jacobian.

    Gates:
      1. probe_vectors=I through the same code path recovers J exactly
         (finite, correct shape) — then SVD(J) is ground truth.
      2. refined basis (k=8, m=4k) captures ≥ 0.85 of the exact top-k
         Jacobian energy (measured 0.878; raw un-refined is ~0.75).
      3. a vector inside the subspace has fraction ≈ 1.
      4. random-vector fractions average ≈ k/d.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32, attn_implementation="eager"
    ).eval()
    topo = detect_topology(model, model.config)
    d = topo.hidden_size
    layer, target = topo.n_layers // 3, topo.n_layers - 2
    prompts = ["The cat, not the dog, chased the mouse."]
    k = 8

    # 1) exact J via identity probe vectors (same code path)
    exact = jt_row_samples(
        model, tok, prompts, layers=[layer], target_layer=target,
        m=d, probe_vectors=torch.eye(d), topo=topo, batch_size=1,
    )[layer]  # rows = Jᵀe_i = i-th row of J → this IS J [d, d]
    _, s_exact, _ = np.linalg.svd(exact.astype(np.float64))
    top_k_energy = float((s_exact[:k] ** 2).sum())

    # 2) refined randomized basis on the same prompt
    basis = jspace_bases(
        model, tok, prompts, layers=[layer], target_layer=target,
        k=k, m=4 * k, refine=True, topo=topo, batch_size=1, seed=270,
    )[layer]
    captured = float(
        np.linalg.norm(exact.astype(np.float64) @ basis.basis.T.astype(np.float64))
        ** 2
    )
    capture_ratio = captured / top_k_energy

    # 3) in-subspace vector → fraction 1
    inside = basis.basis[0] * 3.0 + basis.basis[-1] * 0.5
    frac_inside = workspace_fraction(basis.basis, inside)

    # 4) random vectors → k/d
    rng = np.random.default_rng(270)
    fr = random_vector_fractions(basis.basis, n=200, rng=rng)
    kd = k / d

    checks = {
        "exact_shape": exact.shape == (d, d),
        "exact_finite": bool(np.isfinite(exact).all()),
        "capture_ratio_ge_085": bool(capture_ratio >= 0.85),
        "inside_fraction_1": bool(abs(frac_inside - 1.0) < 1e-5),
        "random_fraction_kd": bool(abs(float(fr.mean()) - kd) < 0.02),
        "strengths_sorted": bool(
            np.all(np.diff(basis.strengths.astype(np.float64)) <= 1e-6)
        ),
    }
    return {
        "model": model_name,
        "d": d,
        "layer": layer,
        "target_layer": target,
        "k": k,
        "capture_ratio": round(capture_ratio, 4),
        "inside_fraction": round(frac_inside, 6),
        "random_fraction_mean": round(float(fr.mean()), 4),
        "k_over_d": round(kd, 4),
        "checks": checks,
        "all_pass": all(checks.values()),
    }


if __name__ == "__main__":
    import json

    out = self_test()
    print(json.dumps(out, indent=2, default=str))
    if not out["all_pass"]:
        raise SystemExit(1)
