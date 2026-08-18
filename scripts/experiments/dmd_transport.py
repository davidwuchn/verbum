#!/usr/bin/env python3
"""P-DMD-TRANSPORT - within-pass residual transport operator (frozen s338, Michael GO).

The reducer as an OPERATOR, not a basis. Treat the last-token residual
trajectory h(0)->...->h(L) of one forward pass as a dynamical system and
estimate the linear transport operator T ~ X'X^+ via exact reduced DMD
(operator_dmd.py; Schmid 2010 / Tu 2014 / Golub&Van Loan - textbook, patent-
clean per operator-geometry-la-toolkit.md sec 0b FTO rule).

Motivation (s338 orbital reframe, cycle-carrier-signal.md sec Reframe): meaning-
as-equality is a property of the ORBIT/attractor, not the point - the operator
spectrum is the register where co-extensional terms could converge where the
static pairwise Gram cannot represent it. This probe establishes the instrument
+ the one-reducer-unrolled thesis test; the extensional-equality test is the
downstream stage-2 payoff (sec 5b), deliberately out of this artifact.

FROZEN verdict tree (operator-geometry-la-toolkit.md sec 5a):
  G0 INSTRUMENT   planted worlds recovered + det-repeat value_dev 0.0 -> else VOID
  G1 LINEARIZATION rel_resid = ||X'-TX||_F/||X'||_F at primary rank (reported;
                   caveat if > 0.5, does not auto-void)
  G2 OPERATOR-EXISTS (make-or-break, shuffled-layer null): gap =
                   rel_resid(shuffled_layer_order) - rel_resid(real) > 0, p<0.05
                   over n_perm layer-order shuffles -> else NOISE
  G3 STATIONARITY  per-layer T_l vs global T (operator cosine in a COMMON PCA
                   basis): flat-high -> STATIONARY-REDUCER; core high + late drop
                   -> BANDED; low/variable -> DRIFTING

A-priori masses: BANDED 30 / NOISE 25 / STATIONARY-REDUCER 20 / DRIFTING 20 / VOID 5.

Register: last-token d_model residual stream (output_hidden_states). Corpus:
~300 combinator-tagged kernel-certified terms subsampled from crystal_probes,
length-stratified. Method: PCA to a common P-dim frame (so per-layer operators
are directly comparable), exact reduced DMD at primary rank.

`--validate` drives planted STATIONARY / DRIFTING / NOISE / CONTRACTING (+ a
BANDED coverage world for the middle G3 branch) through the REAL analysis and
gate path (s331: planted plumbing must be probe plumbing). No model is loaded.

License: MIT.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from combinator_relationship_map import find_gate_modules, git_sha, log

from verbum.operator_dmd import (
    lstsq_operator,
    operator_cosine,
    pca_basis,
    reduced_dmd,
    reduced_rel_from_grams,
)
from verbum.probes.library import crystal_probes

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (sec 5a, s338)
# ---------------------------------------------------------------------------
P_PCA = 128            # common PCA frame dim (operators comparable across layers)
PRIMARY_RANK = 40      # DMD truncation rank for all gate statistics
RANK_SWEEP = (10, 20, 40, 80)  # descriptive only
N_PERM = 1000          # shuffled-layer-order permutations (G2)
N_PROMPTS = 300        # real corpus size (>= P_PCA for well-posed per-layer fit)
ALPHA = 0.05
G1_LIN_MAX = 0.5       # linearization caveat threshold
G3_CORE_MIN = 0.70     # stationary/banded core operator-cosine floor
G3_LATE_MIN = 0.60     # stationary vs banded late-layer floor
LATE_LAYERS = 3        # count of final transitions defining the "late" band
PERSIST_ABS = 0.95     # |lambda| >= this counts as persistent
DET_TOL = 0.0          # deterministic-repeat max abs hidden diff (bf16 greedy)
DET_CHECK_N = 8        # prompts recaptured for the det-repeat gate
SEED = 0

VERDICTS = ("STATIONARY-REDUCER", "BANDED", "DRIFTING", "NOISE", "VOID")


def _json_native(o: Any):
    if isinstance(o, (np.integer,)):
        return int(o)
    if isinstance(o, (np.floating,)):
        return float(o)
    if isinstance(o, (np.bool_,)):
        return bool(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(f"not JSON-native: {type(o)}")


# ---------------------------------------------------------------------------
# Shared analysis + gate path (real AND planted call this - s331)
# ---------------------------------------------------------------------------
def analyse(H: np.ndarray, rng: np.random.Generator) -> dict:
    """Full DMD analysis + frozen gates on a trajectory tensor.

    H: (n_prompts, L+1, d) real last-token residual trajectories.
    Returns the gates dict incl. the per-class verdict (not VOID; VOID is an
    instrument-level meta-verdict decided by the caller).
    """
    n, lp1, _d = H.shape
    L = lp1 - 1

    # --- PCA to a common frame (per-layer operators become comparable) ------
    snaps = H.reshape(n * lp1, -1)
    comps, mean, var_explained = pca_basis(snaps, P_PCA, seed=SEED)
    Z = (H - mean) @ comps  # (n, L+1, P)
    P = Z.shape[2]

    # --- global snapshot pairs (P, n*L) -------------------------------------
    X = Z[:, :L, :].reshape(n * L, P).T
    Xp = Z[:, 1:, :].reshape(n * L, P).T

    # --- per-layer Grams: layer-order permutations reduce to P x P sums ------
    # Ss[a] = Z_a^T Z_a ; Cross[b,a] = Z_b^T Z_a  (Z_a = Z[:, a, :], n x P)
    Ss = np.stack([Z[:, a, :].T @ Z[:, a, :] for a in range(lp1)])  # (lp1,P,P)
    Cross = np.empty((lp1, lp1, P, P))
    for b in range(lp1):
        Zb = Z[:, b, :].T  # (P, n)
        for a in range(lp1):
            Cross[b, a] = Zb @ Z[:, a, :]

    def grams_for_perm(pi: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        src = pi[:L]
        tgt = pi[1:]
        cxx = Ss[src].sum(axis=0)
        cxpxp = Ss[tgt].sum(axis=0)
        cxpx = Cross[tgt, src].sum(axis=0)
        return cxx, cxpx, cxpxp

    # --- G1 linearization: rank sweep + primary (real = identity perm) ------
    ident = np.arange(lp1)
    Cxx0, Cxpx0, Cxpxp0 = grams_for_perm(ident)
    sweep = {
        r: reduced_rel_from_grams(Cxx0, Cxpx0, Cxpxp0, r) for r in RANK_SWEEP
    }
    rel_real = reduced_rel_from_grams(Cxx0, Cxpx0, Cxpxp0, PRIMARY_RANK)
    # spectrum from the single exact reduced DMD (eigenvalues)
    dmd_primary = reduced_dmd(X, Xp, PRIMARY_RANK)
    abs_eig = dmd_primary["abs_eig"]
    mean_abs_eig = float(np.mean(abs_eig)) if abs_eig.size else 0.0
    persist_frac = (
        float(np.mean(abs_eig >= PERSIST_ABS)) if abs_eig.size else 0.0
    )
    top_abs = sorted(abs_eig.tolist(), reverse=True)[:5]
    g1_caveat = bool(rel_real > G1_LIN_MAX)

    # --- G2 operator-exists: shuffled-layer-order null (fast Gram path) ------
    rel_shuf = np.empty(N_PERM)
    for i in range(N_PERM):
        pi = rng.permutation(lp1)
        cxx, cxpx, cxpxp = grams_for_perm(pi)
        rel_shuf[i] = reduced_rel_from_grams(cxx, cxpx, cxpxp, PRIMARY_RANK)
    gap = float(np.median(rel_shuf) - rel_real)
    p_g2 = float(np.mean(rel_shuf <= rel_real))
    g2_pass = bool(gap > 0.0 and p_g2 < ALPHA)

    # --- G3 stationarity: per-layer operators in the common basis -----------
    T_global = lstsq_operator(X, Xp)
    sims = np.empty(L)
    layer_abs_eig = np.empty(L)
    for ell in range(L):
        Xl = Z[:, ell, :].T          # (P, n)
        Xpl = Z[:, ell + 1, :].T
        T_l = lstsq_operator(Xl, Xpl)
        sims[ell] = operator_cosine(T_l, T_global)
        layer_abs_eig[ell] = float(np.mean(np.abs(np.linalg.eigvals(T_l))))
    core = sims[: L - LATE_LAYERS]
    late = sims[L - LATE_LAYERS :]
    core_sim = float(np.median(core)) if core.size else 0.0
    late_sim = float(np.median(late)) if late.size else 0.0

    # --- verdict (per-class; VOID decided by caller) ------------------------
    if not g2_pass:
        verdict = "NOISE"
    elif core_sim >= G3_CORE_MIN and late_sim >= G3_LATE_MIN:
        verdict = "STATIONARY-REDUCER"
    elif core_sim >= G3_CORE_MIN and late_sim < G3_LATE_MIN:
        verdict = "BANDED"
    else:
        verdict = "DRIFTING"

    return {
        "n_prompts": n,
        "L": L,
        "P": P,
        "var_explained": var_explained,
        "rel_resid_primary": rel_real,
        "rel_resid_sweep": {int(k): float(v) for k, v in sweep.items()},
        "g1_caveat": g1_caveat,
        "g2": {
            "gap": gap,
            "p": p_g2,
            "pass": g2_pass,
            "rel_shuf_median": float(np.median(rel_shuf)),
        },
        "g3": {
            "core_sim": core_sim,
            "late_sim": late_sim,
            "sims": sims.tolist(),
            "layer_abs_eig": layer_abs_eig.tolist(),
        },
        "spectrum": {
            "mean_abs_eig": mean_abs_eig,
            "persist_frac": persist_frac,
            "top_abs_eig": top_abs,
        },
        "verdict": verdict,
    }


# ---------------------------------------------------------------------------
# Planted worlds (synthetic trajectories in d_synth; run FULL analyse path)
# ---------------------------------------------------------------------------
def _random_operator(rng, d, lo, hi):
    """Real operator with eigenvalue magnitudes in [lo, hi] (symmetric build)."""
    q, _ = np.linalg.qr(rng.standard_normal((d, d)))
    diag = rng.uniform(lo, hi, size=d) * rng.choice([-1.0, 1.0], size=d)
    return q @ np.diag(diag) @ q.T


def _iterate(T_of_layer, z0, lp1, noise, rng):
    n, d = z0.shape
    H = np.empty((n, lp1, d))
    H[:, 0, :] = z0
    for ell in range(lp1 - 1):
        T = T_of_layer(ell)
        H[:, ell + 1, :] = H[:, ell, :] @ T.T + noise * rng.standard_normal((n, d))
    return H


def planted_worlds(lp1: int = 41, n: int = 200, d: int = 160) -> dict:
    """Synthetic trajectory tensors for --validate. Each expects a verdict."""
    worlds = {}
    rng = np.random.default_rng(SEED)
    z0 = rng.standard_normal((n, d))

    # (1) STATIONARY: fixed operator, mixed persistent/contracting spectrum
    r0 = np.random.default_rng(101)
    Tstat = _random_operator(r0, d, 0.55, 0.99)
    worlds["STATIONARY"] = (
        _iterate(lambda _l: Tstat, z0, lp1, 0.01, np.random.default_rng(11)),
        "STATIONARY-REDUCER",
    )

    # (2) DRIFTING: strongly rotating operator, angle ramps with layer
    r2 = np.random.default_rng(202)
    base = _random_operator(r2, d, 0.6, 0.95)
    axes = r2.standard_normal((d, d))
    axesA, _ = np.linalg.qr(axes)

    def drift_T(ell):
        theta = 0.35 * ell  # strong, smooth ramp -> neighbours similar, ends far
        c, s = np.cos(theta), np.sin(theta)
        rot = np.eye(d)
        for k in range(0, d - 1, 2):
            rot[k, k], rot[k, k + 1] = c, -s
            rot[k + 1, k], rot[k + 1, k + 1] = s, c
        R = axesA @ rot @ axesA.T
        return R @ base

    worlds["DRIFTING"] = (
        _iterate(drift_T, z0, lp1, 0.01, np.random.default_rng(22)),
        "DRIFTING",
    )

    # (3) NOISE: iid snapshots, no operator
    r3 = np.random.default_rng(303)
    worlds["NOISE"] = (r3.standard_normal((n, lp1, d)), "NOISE")

    # (4) CONTRACTING: fixed operator, all |lambda|<1 (homeostasis)
    r4 = np.random.default_rng(404)
    Tcon = _random_operator(r4, d, 0.60, 0.90)
    worlds["CONTRACTING"] = (
        _iterate(lambda _l: Tcon, z0, lp1, 0.01, np.random.default_rng(44)),
        "STATIONARY-REDUCER",  # it IS stationary; contraction checked separately
    )

    # (5) BANDED (coverage for the middle G3 branch): stationary core, abrupt
    #     operator change in the last LATE_LAYERS transitions
    r5 = np.random.default_rng(505)
    Tcore = _random_operator(r5, d, 0.55, 0.99)
    Tlate = _random_operator(np.random.default_rng(515), d, 0.55, 0.99)

    def banded_T(ell):
        return Tlate if ell >= (lp1 - 1 - LATE_LAYERS) else Tcore

    worlds["BANDED"] = (
        _iterate(banded_T, z0, lp1, 0.01, np.random.default_rng(55)),
        "BANDED",
    )
    return worlds


def run_validate() -> int:
    log("[dmd] --validate: driving planted worlds through the real gate path")
    worlds = planted_worlds()
    ok = True
    for name, (H, expected) in worlds.items():
        rng = np.random.default_rng(SEED)
        res = analyse(H, rng)
        got = res["verdict"]
        extra = ""
        passed = got == expected
        if name == "CONTRACTING":
            contr = res["spectrum"]["mean_abs_eig"] < 1.0
            passed = passed and contr
            extra = f" mean|lambda|={res['spectrum']['mean_abs_eig']:.3f}(<1:{contr})"
        flag = "OK" if passed else "FAIL"
        ok = ok and passed
        log(
            f"[dmd]   {name:12s} -> {got:19s} (want {expected:19s}) "
            f"g2_gap={res['g2']['gap']:+.3f} p={res['g2']['p']:.3f} "
            f"core={res['g3']['core_sim']:.2f} late={res['g3']['late_sim']:.2f}"
            f"{extra}  {flag}"
        )
    log(f"[dmd] validate {'PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ---------------------------------------------------------------------------
# Corpus (length-stratified subsample of combinator-tagged crystal probes)
# ---------------------------------------------------------------------------
def build_corpus(n_prompts: int) -> list[dict]:
    probes = list(crystal_probes())
    by_comb: dict[str, list] = {}
    for p in probes:
        by_comb.setdefault(p.combinator or "NONE", []).append(p)
    # proportional per-combinator, length-stratified (even spread by char len)
    chosen = []
    total = len(probes)
    for _comb, ps in sorted(by_comb.items()):
        ps_sorted = sorted(ps, key=lambda p: (len(p.prompt), p.id))
        k = max(1, round(n_prompts * len(ps) / total))
        if k >= len(ps_sorted):
            picks = ps_sorted
        else:
            idx = np.linspace(0, len(ps_sorted) - 1, k).round().astype(int)
            picks = [ps_sorted[i] for i in dict.fromkeys(idx.tolist())]
        chosen.extend(picks)
    chosen = sorted(chosen, key=lambda p: p.id)[:n_prompts]
    return [
        {"id": p.id, "combinator": p.combinator, "category": p.category,
         "prompt": p.prompt}
        for p in chosen
    ]


# ---------------------------------------------------------------------------
# Real backend
# ---------------------------------------------------------------------------
class RealBackend:
    def __init__(self, model_id: str, device: str, dtype_str: str):
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer

        self.torch = torch
        self.device = device
        dtype = getattr(torch, dtype_str)
        log(f"[dmd] loading {model_id} ({dtype_str}, {device})")
        self.tok = AutoTokenizer.from_pretrained(model_id)
        self.model = (
            AutoModelForCausalLM.from_pretrained(
                model_id, torch_dtype=dtype, attn_implementation="eager"
            )
            .to(device)
            .eval()
        )
        self.n_layers = len(find_gate_modules(self.model))
        self.d_model = int(self.model.config.hidden_size)
        log(f"[dmd] n_layers={self.n_layers} d_model={self.d_model}")

    def trajectory(self, prompt: str) -> np.ndarray:
        """Last-token residual across all layers: (n_layers+1, d_model)."""
        torch = self.torch
        enc = self.tok(prompt, return_tensors="pt").to(self.device)
        with torch.no_grad():
            out = self.model(**enc, output_hidden_states=True)
        # hidden_states: tuple(len n_layers+1) of (1, seq, d); take last token
        return np.stack(
            [hs[0, -1].float().cpu().numpy() for hs in out.hidden_states]
        )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "float16", "bfloat16"])
    ap.add_argument("--n-prompts", type=int, default=N_PROMPTS)
    ap.add_argument("--out", default="results/p_dmd_transport_s338/run")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    corpus = build_corpus(args.n_prompts)
    log(f"[dmd] corpus: {len(corpus)} prompts")

    be = RealBackend(args.model_id, args.device, args.dtype)

    # capture trajectories
    trajs = []
    for i, item in enumerate(corpus):
        trajs.append(be.trajectory(item["prompt"]))
        if (i + 1) % 50 == 0:
            log(f"[dmd] captured {i + 1}/{len(corpus)}")
    H = np.stack(trajs)  # (n, L+1, d)
    log(f"[dmd] H shape {H.shape}")

    # G0 det-repeat: recapture first DET_CHECK_N, must be bit-identical
    rep = np.stack([be.trajectory(corpus[i]["prompt"]) for i in range(
        min(DET_CHECK_N, len(corpus)))])
    value_dev = float(np.max(np.abs(rep - H[: rep.shape[0]])))
    det_ok = value_dev <= DET_TOL
    log(f"[dmd] det-repeat value_dev={value_dev} ok={det_ok}")

    if args.device == "mps":
        try:
            self_torch = be.torch
            del be.model
            self_torch.mps.empty_cache()
        except Exception:
            pass

    rng = np.random.default_rng(SEED)
    res = analyse(H, rng)

    # VOID overrides: instrument failure
    global_verdict = res["verdict"]
    if not det_ok:
        global_verdict = "VOID"

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    corpus_hash = hashlib.sha256(
        json.dumps([c["prompt"] for c in corpus], sort_keys=True).encode()
    ).hexdigest()[:16]

    meta = {
        "probe": "P-DMD-TRANSPORT",
        "frozen": "s338 pre-data freeze (Michael GO): "
                  "operator-geometry-la-toolkit.md sec 5a",
        "pre_data_instantiations": {
            "P_PCA": P_PCA, "PRIMARY_RANK": PRIMARY_RANK,
            "RANK_SWEEP": list(RANK_SWEEP), "N_PERM": N_PERM,
            "N_PROMPTS": args.n_prompts, "ALPHA": ALPHA,
            "G1_LIN_MAX": G1_LIN_MAX, "G3_CORE_MIN": G3_CORE_MIN,
            "G3_LATE_MIN": G3_LATE_MIN, "LATE_LAYERS": LATE_LAYERS,
            "PERSIST_ABS": PERSIST_ABS, "SEED": SEED,
            "apriori_masses": {"BANDED": 30, "NOISE": 25,
                               "STATIONARY-REDUCER": 20, "DRIFTING": 20,
                               "VOID": 5},
        },
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "model_id": args.model_id, "device": args.device, "dtype": args.dtype,
        "smoke": args.smoke, "n_prompts": len(corpus),
        "corpus_hash": corpus_hash, "git_sha": git_sha(),
        "det_value_dev": value_dev, "det_ok": det_ok,
        "global_verdict": global_verdict,
        "gates": res,
    }
    (out / "meta.json").write_text(
        json.dumps(meta, indent=2, default=_json_native))
    with (out / "results.jsonl").open("w") as fh:
        for c in corpus:
            fh.write(json.dumps(
                {"id": c["id"], "combinator": c["combinator"],
                 "category": c["category"], "prompt_len": len(c["prompt"])},
                default=_json_native) + "\n")
    np.savez_compressed(
        out / "trajectories.npz",
        H=H.astype(np.float16),
        sims=np.array(res["g3"]["sims"]),
        layer_abs_eig=np.array(res["g3"]["layer_abs_eig"]),
    )

    log(f"[dmd] === VERDICT: {global_verdict} ===")
    log(f"[dmd] G1 rel_resid={res['rel_resid_primary']:.3f} "
        f"caveat={res['g1_caveat']} | G2 gap={res['g2']['gap']:+.3f} "
        f"p={res['g2']['p']:.3f} pass={res['g2']['pass']} | "
        f"G3 core={res['g3']['core_sim']:.2f} late={res['g3']['late_sim']:.2f} | "
        f"mean|lambda|={res['spectrum']['mean_abs_eig']:.3f} "
        f"persist={res['spectrum']['persist_frac']:.2f}")
    log(f"[dmd] wrote {out}/")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
