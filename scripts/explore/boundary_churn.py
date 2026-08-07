#!/usr/bin/env python3
"""§P-BOUNDARY-CHURN — optimizer↔type-boundary identity (§6 item 4 / M8 corollary).

Pre-reg: mementum/knowledge/explore/type-systems-under-llm-constraints.md
§P-BOUNDARY-CHURN (FROZEN s320, Michael-approved GO).

Claim (M8 corollary, reframed to weight-geometry): the base-FFN TWN-marginal
population — the r≈1 "insufficient-evidence" weights that s310 showed CHURN
under quantization — concentrates on the type-checker direction (the
§P-TYPE-GRAM-1 kind register). Do the marginal weights coincide with the type
machinery? Register (λ measure) = WEIGHT-GEOMETRY (directions × magnitudes),
NOT tape. Heavy-negative a-priori (types are tape-resident: §P-TYPE-DELIVER
no-weight-delivery, s315/s317/s320) — either verdict informative.

⚠ BUILD AMENDMENT (s320, runtime/build-forced, pre-run — instrument-side ONLY;
register / verdict-tree / a-priori UNCHANGED, pending Michael at GO). Reading
the persisted §P-TYPE-GRAM-1 centroids (λ assert: runtime ≡ truth) exposed a
coherence gap: the frozen construction assumed the kind direction lives in the
RESIDUAL d_model space (→ down_proj columns). It does NOT — the type-gram
`register` is **'gate'**, so centroids are in the **9728-dim gate-activation
space** (Qwen3-4B intermediate), a direction over HIDDEN UNITS. Corrected
mapping (frozen INTENT preserved — marginal weights concentrate on type-
selective features):
  • type-selective FEATURE = a hidden unit j (gate-space coordinate);
    selectivity s_j = unit j's LEVERAGE in the type subspace = ‖U_ℓ[j,:]‖,
    U_ℓ = orthonormal kind cross-cut subspace reconstructed from centroids.
  • on-target weight population = **gate_proj rows** (gate_proj[j,:] computes
    the gate activation that IS the type register); marginality m_j = churn
    propensity of that row = fraction of |W|/thr ∈ [0.7,1.3) (s310 straddle).
Space/matrix corrected to match the persisted centroids; register (weight-
geometry), gates, verdicts, a-priori UNCHANGED.

⚠ AMENDMENT PART 2 (BC2 null, same build-forced review): the frozen BC2 null
was "matched-random-subspace." An ISOTROPIC random 2-D subspace has leverage
‖U[j,:]‖ that is EXCHANGEABLE across units (a random 2-frame) → it can never
correlate with marginality → BC2 would be geometrically REDUNDANT with BC1 and
the MARGIN-GENERIC verdict UNREACHABLE (same bug class as the idempotency k=0
issue). The correct MATCHED null is the **shuffled-kind-label subspace**
(permute atom/fn/app WITHIN opcode, rebuild the subspace — the §P-TYPE-GRAM-1
TG5 methodology): it preserves the centroid magnitude structure and varies only
the KIND identity, isolating type-specificity and making MARGIN-GENERIC
reachable. The frozen INTENT (BC2 = "concentration is type-specific, not a
generic structure artifact") is exactly preserved; the isotropic-random ρ is
still reported as an advisory sanity number.

Gates: BC1 CONCENTRATION (ρ(m_j,s_j)>0, within-layer label-perm null) · BC2
TYPE-SPECIFIC (ρ_kind > ρ_shuffled-kind, matched null, make-or-break) · BC3
LAYER-PROFILE (per-layer ρ, advisory) · BC4 SANE (void-gate).
Verdicts: BOUNDARY-IS-TYPED / MARGIN-GENERIC / BOUNDARY-UNTYPED / VOID.

Reuse (λ one_way, no fork): results/type-gram/qwen3-4b/centroids.npz (persisted
kind register) + verbum.dsp.nulls (gate, NullDraws) + fuel_theorem (spearman) +
transformers weight load (gate_proj only). No forward pass, no wire.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import itertools
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

from fuel_theorem import spearman  # noqa: E402

from verbum.dsp.nulls import NullDraws, Register, gate  # noqa: E402

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §P-BOUNDARY-CHURN + build amendment)
# ══════════════════════════════════════════════════════════════════════════
TWN_THR_FRAC = 0.7                 # thr = 0.7·mean(|W|)  (s304/s310 TWN)
STRADDLE = (0.7, 1.3)              # s310 marginal/straddle band in r=|W|/thr
N_RAND_SUBSPACES = 300             # BC2 matched-random-subspace null draws
N_KINDS = 3                        # atom / fn / app  → kind subspace rank 2
N_CRYSTAL = 9                      # basis[0:9] crystal opcodes; [9:30] X:kind
N_OPCODES_TYPED = 7               # K I B C S D W (each × 3 kinds = 21 nodes)


def _orthonormal_cols(M: np.ndarray) -> np.ndarray:
    """M: (d, k) → (d, k') orthonormal columns spanning col-space (drop nulls)."""
    q, r = np.linalg.qr(M)
    keep = np.abs(np.diag(r)) > 1e-8
    return q[:, keep]


def type_subspace(cent_layer: np.ndarray,
                  kind_perm: np.ndarray | None = None) -> np.ndarray:
    """Kind cross-cut subspace from a layer's 30 node centroids.

    cent_layer: (30, d). Nodes [9:30] = 7 opcodes × 3 kinds (op-major). Remove
    per-opcode mean over kinds (isolate the KIND cross-cut, not opcode identity,
    = TG2), take the shared kind-mean directions → orthonormal U (d, ≤2).

    kind_perm: optional (n_opcodes, 3) per-opcode kind permutation (the BC2
    shuffled-kind-label null — TG5 methodology: preserves each opcode's 3
    centroids, destroys the SHARED kind identity)."""
    d = cent_layer.shape[1]
    typed = cent_layer[N_CRYSTAL:N_CRYSTAL + N_OPCODES_TYPED * N_KINDS]
    C = typed.reshape(N_OPCODES_TYPED, N_KINDS, d).astype(np.float64)
    if kind_perm is not None:
        C = np.take_along_axis(C, kind_perm[:, :, None], axis=1)
    C = C - C.mean(axis=1, keepdims=True)          # center within opcode
    kind_mean = C.mean(axis=0)                     # (3, d) shared kind dirs (Σ≈0)
    M = kind_mean[:2].T                            # (d, 2) atom, fn (app dep.)
    return _orthonormal_cols(M)                    # (d, ≤2)


def _shuffled_kind_leverage(cent_layers: np.ndarray, layer_idx: list[int],
                            n_null: int, rng: np.random.Generator) -> np.ndarray:
    """(n_null, n_total) within-layer-z-scored leverage of shuffled-kind-label
    subspaces (BC2 matched null; per-draw per-opcode kind permutation)."""
    out = []
    for _ in range(n_null):
        cols = []
        for li in layer_idx:
            perm = np.stack([rng.permutation(N_KINDS)
                             for _ in range(N_OPCODES_TYPED)])
            U = type_subspace(cent_layers[li], kind_perm=perm)
            cols.append(_zscore(leverage(U)))
        out.append(np.concatenate(cols))
    return np.asarray(out)


def leverage(U: np.ndarray) -> np.ndarray:
    """Per-coordinate leverage in the subspace: ‖U[j,:]‖ (j = hidden unit)."""
    if U.shape[1] == 0:
        return np.zeros(U.shape[0])
    return np.linalg.norm(U, axis=1)


def marginality(W_gate: np.ndarray) -> np.ndarray:
    """Per-row churn propensity of gate_proj (n_units, d_model).

    thr = 0.7·mean(|W|) (TWN). m_j = fraction of row j's weights with
    r=|W|/thr in the s310 straddle band [0.7,1.3)."""
    W = np.abs(W_gate.astype(np.float64))
    thr = TWN_THR_FRAC * W.mean()
    if thr <= 0:
        return np.zeros(W.shape[0])
    r = W / thr
    inband = (r >= STRADDLE[0]) & (r < STRADDLE[1])
    return inband.mean(axis=1)


def _zscore(x: np.ndarray) -> np.ndarray:
    s = x.std()
    return (x - x.mean()) / s if s > 1e-12 else np.zeros_like(x)


def _pool_within_layer(vals_by_layer: list[np.ndarray]) -> np.ndarray:
    """z-score within each layer, then concatenate (removes per-layer offset)."""
    return np.concatenate([_zscore(np.asarray(v, float)) for v in vals_by_layer])


# ══════════════════════════════════════════════════════════════════════════
# Pure gates + verdict (what --validate exercises; no torch, no model)
# ══════════════════════════════════════════════════════════════════════════
def compute_gates_bc(b: dict, rng: np.random.Generator, alpha: float = 0.05,
                     n_iter: int = 2000) -> dict:
    """b: m_layers (list per-layer marginality), s_layers (kind selectivity),
    s_rand_pooled ((n_rand, n_total) random-subspace selectivity, within-layer
    z-scored already), sane. Pure — --validate plants b."""
    m_layers = [np.asarray(x, float) for x in b["m_layers"]]
    s_layers = [np.asarray(x, float) for x in b["s_layers"]]
    zm = _pool_within_layer(m_layers)
    zs = _pool_within_layer(s_layers)

    # ── BC1 CONCENTRATION: ρ(m,s) > 0, within-layer label-perm null ──
    rho_kind = spearman(zm, zs)
    sizes = [len(x) for x in m_layers]
    bounds = np.cumsum([0, *sizes])
    bc1_draws = np.empty(min(n_iter, 2000))
    for it in range(bc1_draws.size):
        zs_perm = zs.copy()
        for a, c in itertools.pairwise(bounds):
            zs_perm[a:c] = zs[a:c][rng.permutation(c - a)]
        bc1_draws[it] = spearman(zm, zs_perm)
    bc1 = gate(rho_kind, NullDraws("within_layer_label_perm", bc1_draws,
                                   {"n_iter": bc1_draws.size}),
               "greater", alpha, "BC1_concentration",
               claim_register=Register.value, probe_register=Register.value)

    # ── BC2 TYPE-SPECIFIC (make-or-break): ρ_kind > ρ_shuffled-kind ──
    s_null = np.asarray(b["s_null_pooled"], float)     # (n_null, n_total)
    null_rhos = np.array([spearman(zm, s_null[i]) for i in range(s_null.shape[0])])
    bc2 = gate(rho_kind, NullDraws("shuffled_kind_label", null_rhos,
                                   {"n_null": int(s_null.shape[0])}),
               "greater", alpha, "BC2_type_specific",
               claim_register=Register.value, probe_register=Register.value)
    # advisory: isotropic-random-subspace ρ (sanity — expected ≈ 0)
    rand_rho_mean = float("nan")
    if "s_rand_pooled" in b:
        s_rand = np.asarray(b["s_rand_pooled"], float)
        rand_rho_mean = float(np.mean([spearman(zm, s_rand[i])
                                       for i in range(s_rand.shape[0])]))

    # ── BC3 LAYER-PROFILE (advisory) ──
    per_layer_rho = [float(spearman(_zscore(m_layers[i]), _zscore(s_layers[i])))
                     for i in range(len(m_layers))]

    # ── BC4 SANE (void-gate) ──
    sane = b.get("sane", {})
    subspace_ok = bool(sane.get("kind_sep", 0.0) > 0.0
                       and sane.get("leverage_var", 0.0) > 0.0)
    thr_ok = bool(sane.get("thr_ok", False))
    n_ok = bool(sum(sizes) >= sane.get("min_units", 1))
    bc4_pass = bool(subspace_ok and thr_ok and n_ok)

    # ── verdict tree (frozen) ──
    if not bc4_pass:
        verdict = "VOID"
    elif not bc1.verdict:
        verdict = "BOUNDARY-UNTYPED"
    elif bc2.verdict:
        verdict = "BOUNDARY-IS-TYPED"
    else:
        verdict = "MARGIN-GENERIC"

    return {
        "verdict": verdict,
        "gates": {
            "BC1": {"rho": float(rho_kind), "p": float(bc1.p),
                    "null_mean": float(bc1.null_mean), "pass": bool(bc1.verdict)},
            "BC2": {"rho_kind": float(rho_kind),
                    "shuf_mean": float(null_rhos.mean()),
                    "shuf_p95": float(np.quantile(null_rhos, 0.95)),
                    "iso_rand_mean": rand_rho_mean,
                    "p": float(bc2.p), "pass": bool(bc2.verdict)},
            "BC3_per_layer_rho": per_layer_rho,
            "BC4": {"subspace_ok": subspace_ok, "thr_ok": thr_ok,
                    "n_ok": n_ok, "pass": bc4_pass},
        },
        "means": {"rho_kind": float(rho_kind),
                  "shuf_rho_mean": float(null_rhos.mean()),
                  "iso_rand_rho_mean": rand_rho_mean,
                  "n_total": int(sum(sizes)), "n_layers": len(sizes),
                  "layer_rho_mean": float(np.mean(per_layer_rho))},
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (no model)
# ══════════════════════════════════════════════════════════════════════════
def _rand_subspace_selectivity(n_units: int, n_layers: int, n_rand: int,
                               rng: np.random.Generator) -> np.ndarray:
    """(n_rand, n_units*n_layers) within-layer-z-scored leverage of random 2-D
    subspaces (the BC2 null; per-layer independent random subspace)."""
    out = np.empty((n_rand, n_units * n_layers))
    for i in range(n_rand):
        cols = []
        for _ in range(n_layers):
            U = _orthonormal_cols(rng.standard_normal((n_units, 2)))
            cols.append(_zscore(leverage(U)))
        out[i] = np.concatenate(cols)
    return out


def _world_bc(rng, kind: str, n_units: int = 200, n_layers: int = 4,
              n_null: int = 200) -> dict:
    m_layers, s_layers, m_pool = [], [], []
    for _ in range(n_layers):
        m = rng.uniform(0.0, 0.3, n_units)                 # marginality frac
        s_base = leverage(_orthonormal_cols(rng.standard_normal((n_units, 2))))
        if kind == "boundary_is_typed":
            s = s_base + 0.15 * m + rng.normal(0, 0.005, n_units)  # m→s coupled
        elif kind == "margin_generic":
            s = s_base + 0.15 * m + rng.normal(0, 0.005, n_units)  # coupled…
        elif kind in ("boundary_untyped", "void"):
            s = s_base                                     # no m→s coupling
        else:
            raise ValueError(kind)
        m_layers.append(m)
        s_layers.append(s)
        m_pool.append(_zscore(m))
    zm = np.concatenate(m_pool)
    b: dict = {"m_layers": m_layers, "s_layers": s_layers}

    # BC2 shuffled-kind null (planted): NOT coupled to m (typed) → ρ_kind beats;
    # COUPLED to m (generic) → the coupling is kind-agnostic → ρ_kind within null.
    if kind == "margin_generic":
        # the m→leverage coupling survives kind-shuffle (generic, not kind-
        # specific) → null carries ≳ the same m-signal → ρ_kind within null.
        s_null = np.array([zm + rng.normal(0, 0.4, zm.size)
                           for _ in range(n_null)])
    else:
        s_null = np.array([rng.normal(0, 1.0, zm.size) for _ in range(n_null)])
    b["s_null_pooled"] = s_null
    b["s_rand_pooled"] = _rand_subspace_selectivity(n_units, n_layers, 100, rng)
    b["sane"] = {"kind_sep": 1.0, "leverage_var": 1.0, "thr_ok": True,
                 "min_units": 10}
    if kind == "void":
        b["sane"] = {"kind_sep": 0.0, "leverage_var": 0.0, "thr_ok": False,
                     "min_units": 10}
    return b


def run_validate(alpha: float) -> int:
    print("── §P-BOUNDARY-CHURN --validate (planted worlds, no model) ──")
    want = {"boundary_is_typed": "BOUNDARY-IS-TYPED",
            "margin_generic": "MARGIN-GENERIC",
            "boundary_untyped": "BOUNDARY-UNTYPED",
            "void": "VOID"}
    ok = True
    for kind, expect_v in want.items():
        rng = np.random.default_rng(hash(kind) % (2**31))
        res = compute_gates_bc(_world_bc(rng, kind), rng, alpha, n_iter=1000)
        good = res["verdict"] == expect_v
        ok &= good
        g = res["gates"]
        print(f"  {kind:18s} -> {res['verdict']:18s} expect {expect_v:18s} "
              f"BC1 p={g['BC1']['p']:.3f} BC2 p={g['BC2']['p']:.3f} "
              f"{'✓' if good else '✗ FAIL'}")

    # ── primitives ──
    # (1) type_subspace + leverage: plant a subspace concentrated on units 0,1
    d, npts = 32, 30
    cent = np.zeros((npts, d))
    # opcode-major nodes 9..29: give atom kind a direction on unit 0, fn on 1
    for o in range(N_OPCODES_TYPED):
        cent[9 + o * 3 + 0, 0] = 1.0    # atom → e0
        cent[9 + o * 3 + 1, 1] = 1.0    # fn   → e1
        cent[9 + o * 3 + 2, 2] = 1.0    # app  → e2
    U = type_subspace(cent)
    lev = leverage(U)
    prim1 = (U.shape[1] >= 1 and lev[0] > lev[5] and lev[1] > lev[5])
    ok &= prim1
    print(f"  primitive type_subspace/leverage  {'✓' if prim1 else '✗ FAIL'}")

    # (2) marginality band (TWN thr = 0.7·mean|W|, global per matrix):
    #   uniform matrix → every r=1/0.7=1.43 (above band) → frac 0.
    #   bimodal [0.5,1.5] (mean 1 → thr 0.7): 0.5→r=0.71 (in [0.7,1.3)), 1.5→r=2.14
    #   → frac 0.5.
    m_conf = marginality(np.ones((1, 8)))
    m_marg = marginality(np.array([[0.5, 0.5, 0.5, 0.5, 1.5, 1.5, 1.5, 1.5]]))
    prim2 = (m_conf[0] < 1e-9 and abs(m_marg[0] - 0.5) < 1e-9)
    ok &= prim2
    print(f"  primitive marginality band        {'✓' if prim2 else '✗ FAIL'}")

    # (3) random-subspace leverage is ~uncorrelated with random m (null centered)
    rng = np.random.default_rng(5)
    mm = rng.uniform(0, 0.3, 500)
    U2 = _orthonormal_cols(rng.standard_normal((500, 2)))
    prim3 = abs(spearman(mm, leverage(U2))) < 0.2
    ok &= prim3
    print(f"  primitive random-subspace null≈0  {'✓' if prim3 else '✗ FAIL'}")

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path (weights only — no forward pass)
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import torch
    from transformers import AutoModelForCausalLM

    rng = np.random.default_rng(args.seed)
    cent_data = np.load(args.centroids, allow_pickle=True)
    cent = cent_data["centroids"].astype(np.float64)      # (L, 30, d_gate)
    cent_layers = list(cent_data["layers"])
    print(f"[bc] centroids {cent.shape} over layers "
          f"{cent_layers[0]}..{cent_layers[-1]}")

    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    dec = model.model.layers
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)

    m_layers, s_layers, kind_seps, thr_oks = [], [], [], []
    for li, lay in enumerate(cent_layers):
        W_gate = dec[int(lay)].mlp.gate_proj.weight.detach().float().cpu().numpy()
        m = marginality(W_gate)                            # (n_units,)
        U = type_subspace(cent[li])                        # (d_gate, ≤2)
        s = leverage(U)                                    # (n_units,)
        if s.shape[0] != m.shape[0]:
            raise SystemExit(f"unit mismatch L{lay}: gate {m.shape[0]} vs "
                             f"centroid {s.shape[0]}")
        m_layers.append(m)
        s_layers.append(s)
        kind_seps.append(float(np.linalg.norm(U)))
        W = np.abs(W_gate.astype(np.float64))
        thr_oks.append(bool(TWN_THR_FRAC * W.mean() > 0))
        if (li + 1) % 6 == 0:
            print(f"[bc] processed {li + 1}/{len(cent_layers)} layers", flush=True)

    # BC2 matched null: shuffled-kind-label subspaces (TG5); isotropic advisory
    n_units = m_layers[0].shape[0]
    layer_idx = list(range(len(cent_layers)))
    print(f"[bc] {n_units} units × {len(m_layers)} layers; building "
          f"{N_RAND_SUBSPACES} shuffled-kind + isotropic null draws …", flush=True)
    s_null = _shuffled_kind_leverage(cent, layer_idx, N_RAND_SUBSPACES, rng)
    s_rand = _rand_subspace_selectivity(n_units, len(m_layers),
                                        N_RAND_SUBSPACES, rng)

    b = {
        "m_layers": m_layers, "s_layers": s_layers,
        "s_null_pooled": s_null, "s_rand_pooled": s_rand,
        "sane": {"kind_sep": float(np.mean(kind_seps)),
                 "leverage_var": float(np.var(_pool_within_layer(s_layers))),
                 "thr_ok": bool(all(thr_oks)),
                 "min_units": 1000},
    }
    res = compute_gates_bc(b, rng, args.alpha)
    res["meta"] = {
        "model_id": args.model_id, "centroids": str(args.centroids),
        "n_units": int(n_units), "n_layers": len(m_layers),
        "layers": [int(x) for x in cent_layers],
        "twn_thr_frac": TWN_THR_FRAC, "straddle": list(STRADDLE),
        "n_rand_subspaces": N_RAND_SUBSPACES,
        "kind_sep_mean": float(np.mean(kind_seps)),
    }
    (out_dir / "results.json").write_text(json.dumps(res, indent=2))
    np.savez_compressed(
        out_dir / "marginality_selectivity.npz",
        m=np.stack(m_layers), s=np.stack(s_layers),
        layers=np.array([int(x) for x in cent_layers]),
        per_layer_rho=np.array(res["gates"]["BC3_per_layer_rho"]))
    print(f"[bc] wrote {out_dir}/results.json")
    g, mn = res["gates"], res["means"]
    print(f"[bc] BC1 ρ={g['BC1']['rho']:.4f} p={g['BC1']['p']:.4f} "
          f"{g['BC1']['pass']} | BC2 ρ_kind={g['BC2']['rho_kind']:.4f} "
          f"shuf_mean={g['BC2']['shuf_mean']:.4f} p={g['BC2']['p']:.4f} "
          f"{g['BC2']['pass']} | iso_adv={g['BC2']['iso_rand_mean']:.4f} "
          f"| BC4 {g['BC4']['pass']}")
    print(f"[bc] per-layer ρ mean={mn['layer_rho_mean']:.4f} "
          f"(min {min(g['BC3_per_layer_rho']):.3f} "
          f"max {max(g['BC3_per_layer_rho']):.3f})")
    print(f"[bc] VERDICT: {res['verdict']}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--dtype", default="float32",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--centroids",
                    default="results/type-gram/qwen3-4b/centroids.npz")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/boundary-churn/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
