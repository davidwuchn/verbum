"""§P-FUEL — the de Carvalho fuel theorem, operationalized.

Pre-reg FROZEN s317 (Michael-approved GO):
mementum/knowledge/explore/normal-forms-are-eigenmodes.md §P-FUEL.

de Carvalho: for non-idempotent intersection types, derivation SIZE =
evaluation LENGTH. If that is the substrate's pinned type system
(curry-howard §3), the TYPE-REGISTER signal on a closed λ-term should scale
with its kernel-certified reduction length ℓ(t)=reduce(t).steps — and,
decisively, with step count WITH MULTIPLICITY (non-idempotent), not with the
count of DISTINCT sub-reductions (idempotent). Lights the 4th type-system
corner and joins the s295 CoT-length law: distance-to-normal-form as a
readable geometric coordinate.

Ground truth (lambda_ast, fixed a-priori — λ yardstick):
  ℓ(t)=reduce(t).steps (mult) · distinct(t)=|{fired-redex shapes in trace}| ·
  size(nf) · tok(t)=len(tokenizer(prompt)).

Register (λ measure): Y = type-register MAGNITUDE = ‖proj of the last-token
band residual onto the type subspace fit HELD-OUT on the §P-TYPE-GRAM-1
crystal/kind probes (opcodes/data/type_probes.json)‖. Value register, band
depth 0.50–0.85 (readability ≥0.6 rule). Michael s317: pure P-TYPE-GRAM-1
reuse. Controls Y_norm (centered magnitude) · Y_rand (matched-dim random).

Arms (one qwen3-4b load, ALL training-free — read-only activation probe):
  LIN  h (C a1 b1 c1) … (C an bn cn)  distinct atoms  → mult=distinct=n
  DUP  h (C a b c) … (C a b c)        same redex ×n   → mult=n distinct=1  (knife)
  MATCH fixed N args, k active (C…) / N−k inert (Z…)  → tok≈const, ℓ=k

Gates (α=0.05): FU1 FUEL-SCALES ρ(Y,ℓ|tok) vs matched-token null · FU2
TYPE-SPECIFIC (> random-subspace null AND > Y_norm) · FU3 NON-IDEMPOTENT
(ρ(Y,mult|distinct) > null AND > ρ(Y,distinct|mult)) · FU4 LENGTH-DECOUPLED
(Y~ℓ within MATCH const-tok) · FU5 SANE (held-out kind register recovered;
all terms reduce to NF). Verdicts FUEL-METER(+NON-IDEMPOTENT) /
FUEL-METER-IDEMPOTENT / LENGTH-ONLY (falsifier) / NO-FUEL-COORDINATE
(falsifier) / VOID. A-priori 35/15/25/20/5.

Reuse (λ one_way, no fork): verbum.lambda_ast (reduce/pretty/spine/rebuild/
Comb/REDUCTIONS) · verbum.dsp.nulls (gate/NullDraws) · verbum.jlens
(capture_residuals) · frozen opcodes/data/type_probes.json. New code =
term-family generation + fuel-gate statistics.

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parents[1]
if str(_ROOT / "opcodes") not in sys.path:
    sys.path.insert(0, str(_ROOT / "opcodes"))

from verbum.dsp.nulls import NullDraws, Register, gate  # noqa: E402
from verbum.lambda_ast import (  # noqa: E402
    REDUCTIONS,
    Comb,
    Status,
    pretty,
    rebuild,
    reduce,
    spine,
)

# ══════════════════════════════════════════════════════════════════════════
# Construction (FROZEN §P-FUEL)
# ══════════════════════════════════════════════════════════════════════════
BAND_DEPTH = (0.50, 0.85)          # value register, late (readability ≥0.6)
TYPE_SUBSPACE_DIM = 2              # kind register: 3 kinds → 2 contrasts
N_RAND_SUBSPACES = 500            # FU2 random-subspace null
N_PERM = 500                       # FU1/FU3/FU4 permutation nulls
N_LENS = (1, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20)   # ℓ ladder for LIN / DUP
MATCH_N = 20                       # MATCH arm arg-count (tok held ~const)
MATCH_K = (0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20)  # active-arg ladder
N_ATOM_SEEDS = 5                   # replicate atom draws per (family, n)
_ALPHA = 0.05


# ── kernel-certified fuel quantities (lambda_ast primitives; no fork) ──────
def _fired_redex(t):
    """The leftmost-outermost saturated redex LHS (Comb + its arity args), or
    None. Mirrors lambda_ast.step's search order exactly → the shape that
    fires at this step."""
    head, args = spine(t)
    if isinstance(head, Comb) and head.name in REDUCTIONS:
        arity, _rule = REDUCTIONS[head.name]
        if len(args) >= arity:
            return rebuild(head, args[:arity])
    for a in args:
        r = _fired_redex(a)
        if r is not None:
            return r
    return None


def certify(prompt: str):
    """Parse+reduce a combinator term → kernel-certified fuel quantities.

    mult = ℓ = β-steps to NF (de Carvalho evaluation length).
    distinct = #distinct fired-redex SHAPES over the trace (non-idempotence
    axis: DUP reuses one shape n times → distinct small; LIN → distinct≈ℓ).
    """
    from verbum.lambda_ast import parse
    r = reduce(parse(prompt))
    shapes = {pretty(_fired_redex(ti)) for ti in r.trace[:r.steps]}
    from verbum.lambda_ast import size as _size
    return {
        "ell": int(r.steps),
        "mult": int(r.steps),
        "distinct": len(shapes),
        "nf_size": int(_size(r.normal_form)),
        "status": r.status.value,
        "is_nf": bool(r.status == Status.NORMAL_FORM),
    }


# ── term-family generation ────────────────────────────────────────────────
def _atoms(rng: np.random.Generator, n: int) -> list[str]:
    """n distinct lowercase-prefixed atoms (parse-safe alnum tokens)."""
    return [f"v{int(x)}" for x in rng.choice(100000, size=n, replace=False)]


def _redex(a: str, b: str, c: str) -> str:
    return f"(C {a} {b} {c})"          # C a b c → a c b : 1 step, distinct by atoms


def _inert(a: str, b: str, c: str) -> str:
    return f"(Z {a} {b} {c})"          # Z atom head → 0 steps, matched token shape


def build_battery(rng: np.random.Generator) -> list[dict]:
    """LIN / DUP / MATCH terms with kernel-certified fuel labels."""
    battery: list[dict] = []

    def emit(prompt: str, family: str):
        cert = certify(prompt)
        battery.append({"prompt": prompt, "family": family, **cert})

    for _ in range(N_ATOM_SEEDS):
        for n in N_LENS:
            # LIN — n distinct single-step redexes (distinct = ℓ = n)
            ats = _atoms(rng, 3 * n)
            args = [_redex(ats[3 * i], ats[3 * i + 1], ats[3 * i + 2])
                    for i in range(n)]
            emit("h " + " ".join(args), "LIN")

            # DUP — the SAME redex n times (distinct = 1, mult = ℓ = n)
            a, b, c = _atoms(rng, 3)
            emit("h " + " ".join([_redex(a, b, c)] * n), "DUP")

        # MATCH — fixed N args, k active (tok ~const, ℓ = k)
        for k in MATCH_K:
            ats = _atoms(rng, 3 * MATCH_N)
            args = []
            for i in range(MATCH_N):
                x, y, z = ats[3 * i], ats[3 * i + 1], ats[3 * i + 2]
                args.append(_redex(x, y, z) if i < k else _inert(x, y, z))
            emit("h " + " ".join(args), "MATCH")
    return battery


# ── rank / correlation statistics (numpy only) ────────────────────────────
def _rankdata(a: np.ndarray) -> np.ndarray:
    a = np.asarray(a, float)
    order = a.argsort(kind="mergesort")
    ranks = np.empty(len(a), float)
    ranks[order] = np.arange(len(a), dtype=float)
    # average ties
    _, inv, counts = np.unique(a, return_inverse=True, return_counts=True)
    sums = np.zeros(len(counts))
    np.add.at(sums, inv, ranks)
    return (sums / counts)[inv]


def _pearson(x: np.ndarray, y: np.ndarray) -> float:
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    x = x - x.mean()
    y = y - y.mean()
    d = np.linalg.norm(x) * np.linalg.norm(y)
    return float(x @ y / d) if d > 1e-12 else 0.0


def spearman(x: np.ndarray, y: np.ndarray) -> float:
    return _pearson(_rankdata(x), _rankdata(y))


def partial_spearman(x: np.ndarray, y: np.ndarray, z: np.ndarray) -> float:
    """Spearman(x, y | z): pearson of rank-residuals after regressing out rank(z)."""
    rx, ry, rz = _rankdata(x), _rankdata(y), _rankdata(z)
    Z = np.column_stack([np.ones_like(rz), rz])
    ex = rx - Z @ np.linalg.lstsq(Z, rx, rcond=None)[0]
    ey = ry - Z @ np.linalg.lstsq(Z, ry, rcond=None)[0]
    return _pearson(ex, ey)


def _perm_within_bins(vals: np.ndarray, binvar: np.ndarray,
                      rng: np.random.Generator) -> np.ndarray:
    """Permute `vals` only within groups of equal `binvar` (matched-* null)."""
    out = np.array(vals, float)
    for b in np.unique(binvar):
        idx = np.where(binvar == b)[0]
        if idx.size > 1:
            out[idx] = vals[rng.permutation(idx)]
    return out


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict — PURE (no torch; what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def compute_gates_fuel(d: dict, rng: np.random.Generator,
                       alpha: float = _ALPHA) -> dict:
    yt = np.asarray(d["y_type"], float)
    yn = np.asarray(d["y_norm"], float)
    ell = np.asarray(d["ell"], float)
    distinct = np.asarray(d["distinct"], float)
    tok = np.asarray(d["tok"], float)
    fam = np.asarray(d["family"])
    rand_rhos = np.asarray(d["rand_rhos"], float)     # ρ(Y_rand_i, ℓ), FU2 null
    tok_bin = np.round(tok / 4.0).astype(int)         # coarse token-length bins

    # ── FU1 FUEL-SCALES: ρ(Y,ℓ) vs matched-token-length null ──
    # AMENDMENT (s317, validate-forced, Michael-noted pre-run): raw ρ(Y,ℓ)
    # beating the matched-token-length null (permute ℓ within tok-bins) — the
    # NULL is the length control. Frozen FU1 also partialled tok, double-
    # controlling length → made the LENGTH-ONLY verdict unreachable (a pure-
    # length world failed FU1 → NO-FUEL). Frozen null + verdict tree unchanged.
    v1 = spearman(yt, ell)
    d1 = np.array([spearman(yt, _perm_within_bins(ell, tok_bin, rng))
                   for _ in range(N_PERM)])
    fu1 = gate(v1, NullDraws("matched_token_length", d1), "greater",
               alpha, "FU1", Register.value, Register.value)

    # ── FU2 TYPE-SPECIFIC: ρ(Y_type,ℓ) > random-subspace null AND > Y_norm ──
    r_type = spearman(yt, ell)
    r_norm = spearman(yn, ell)
    fu2_null = gate(r_type, NullDraws("random_subspace", rand_rhos), "greater",
                    alpha, "FU2_rand", Register.value, Register.value)
    fu2_beats_norm = bool(r_type > r_norm)
    fu2_pass = bool(fu2_null.verdict and fu2_beats_norm)

    # ── FU3 NON-IDEMPOTENT: ρ(Y,mult|distinct) > null AND > ρ(Y,distinct|mult) ──
    v3m = partial_spearman(yt, ell, distinct)          # mult == ell
    v3d = partial_spearman(yt, distinct, ell)
    d3 = np.array([partial_spearman(yt, rng.permutation(ell), distinct)
                   for _ in range(N_PERM)])
    fu3_null = gate(v3m, NullDraws("shuffled_mult", d3), "greater",
                    alpha, "FU3", Register.value, Register.value)
    fu3_mult_wins = bool(v3m > v3d)
    fu3_non_idem = bool(fu3_null.verdict and fu3_mult_wins)

    # ── FU4 LENGTH-DECOUPLED: Y~ℓ within MATCH (tok held ~const) ──
    m = fam == "MATCH"
    v4 = spearman(yt[m], ell[m])
    d4 = np.array([spearman(yt[m], _perm_within_bins(ell[m],
                   tok_bin[m], rng)) for _ in range(N_PERM)])
    fu4 = gate(v4, NullDraws("match_token_perm", d4), "greater",
               alpha, "FU4", Register.value, Register.value)

    # ── FU5 SANE (void-gate) ──
    kind_margin = float(d["kind_margin"])
    all_nf = bool(d["all_nf"])
    fu5_pass = bool(kind_margin > 0.0 and all_nf)

    # ── verdict tree (frozen) ──
    if not fu5_pass:
        verdict = "VOID"
    elif not fu1.verdict:
        verdict = "NO-FUEL-COORDINATE"
    elif not (fu2_pass and fu4.verdict):
        verdict = "LENGTH-ONLY"
    elif fu3_non_idem:
        verdict = "FUEL-METER (+NON-IDEMPOTENT)"
    else:
        verdict = "FUEL-METER-IDEMPOTENT"

    return {
        "verdict": verdict,
        "gates": {
            "FU1": _g(fu1) | {"pass": fu1.verdict},
            "FU2": {"r_type": r_type, "r_norm": r_norm,
                    "p_rand": fu2_null.p, "beats_norm": fu2_beats_norm,
                    "pass": fu2_pass},
            "FU3": _g(fu3_null) | {"rho_mult_given_distinct": v3m,
                                   "rho_distinct_given_mult": v3d,
                                   "mult_wins": fu3_mult_wins,
                                   "non_idem": fu3_non_idem},
            "FU4": _g(fu4) | {"pass": fu4.verdict},
            "FU5": {"kind_margin": kind_margin, "all_nf": all_nf,
                    "pass": fu5_pass},
        },
    }


def _g(gt) -> dict:
    return {"value": gt.value, "null_mean": gt.null_mean, "p": gt.p,
            "sign_ok": gt.sign_ok, "null": gt.null_name}


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds exercise every verdict + primitives
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng: np.random.Generator) -> dict:
    """Synthesize (Y, ℓ, distinct, tok, family) with a known ground-truth verdict."""
    lin_n = np.repeat(N_LENS, 6).astype(float)
    dup_n = np.repeat(N_LENS, 6).astype(float)
    match_k = np.repeat(MATCH_K, 6).astype(float)
    ell = np.concatenate([lin_n, dup_n, match_k])
    distinct = np.concatenate([lin_n, np.ones_like(dup_n), match_k])
    tok = np.concatenate([lin_n * 4, dup_n * 4,
                          np.full_like(match_k, MATCH_N * 4)])
    fam = np.array(["LIN"] * lin_n.size + ["DUP"] * dup_n.size
                   + ["MATCH"] * match_k.size)
    noise = rng.normal(0, 0.03, ell.size)

    yn = 0.02 * tok + rng.normal(0, 0.05, ell.size)   # generic norm ∝ size (default)
    rand_rhos = rng.normal(0, 0.08, N_RAND_SUBSPACES)  # random subspaces ⊥ ℓ (default)

    if kind == "fuel_nonidem":          # Y ∝ ℓ (mult), type-specific
        yt = 0.1 * ell + noise
    elif kind == "fuel_idem":           # Y ∝ distinct → FU3 inverts
        yt = 0.1 * distinct + noise
    elif kind == "length_only":         # generic magnitude: norm tracks ℓ BETTER
        yt = 0.1 * ell + rng.normal(0, 0.30, ell.size)   # noisier type read
        yn = 0.1 * ell + rng.normal(0, 0.02, ell.size)   # r_norm > r_type → ¬beats_norm
    elif kind == "no_fuel":             # Y noise
        yt = noise
    else:                                # void: bad register (kind_margin<0)
        yt = 0.1 * ell + noise
    kind_margin = -1.0 if kind == "void" else 1.0
    return {"y_type": yt, "y_norm": yn, "ell": ell, "distinct": distinct,
            "tok": tok, "family": fam, "rand_rhos": rand_rhos,
            "kind_margin": kind_margin, "all_nf": kind != "void"}


def validate() -> bool:
    rng = np.random.default_rng(0)
    want = {
        "fuel_nonidem": "FUEL-METER (+NON-IDEMPOTENT)",
        "fuel_idem": "FUEL-METER-IDEMPOTENT",
        "length_only": "LENGTH-ONLY",
        "no_fuel": "NO-FUEL-COORDINATE",
        "void": "VOID",
    }
    ok = True
    for kind, exp in want.items():
        got = compute_gates_fuel(_planted(kind, rng), rng)["verdict"]
        good = got == exp
        ok &= good
        print(f"  verdict[{kind:14s}] {got:30s} {'✓' if good else '✗ want ' + exp}")

    # primitive: kernel certifies the mult≫distinct knife by construction
    b = build_battery(np.random.default_rng(1))
    lin = next(x for x in b if x["family"] == "LIN" and x["ell"] == 20)
    dup = next(x for x in b if x["family"] == "DUP" and x["ell"] == 20)
    p_knife = lin["distinct"] == 20 and dup["distinct"] == 1 and dup["mult"] == 20
    print(f"  primitive knife (LIN distinct=20, DUP distinct=1/mult=20) "
          f"{'✓' if p_knife else '✗ FAIL: ' + str((lin, dup))}")
    ok &= p_knife

    # primitive: all battery terms reduce to NF, ℓ matches construction
    p_nf = all(x["is_nf"] for x in b)
    p_ell = all(x["ell"] == x["mult"] for x in b)
    print(f"  primitive all-NF {'✓' if p_nf else '✗ FAIL'} · "
          f"ell==mult {'✓' if p_ell else '✗ FAIL'}")
    ok &= p_nf and p_ell

    # primitive: MATCH holds tok ~const while ℓ varies (FU4 precondition)
    mt = [x for x in b if x["family"] == "MATCH"]
    toks = {len(x["prompt"].split()) for x in mt}
    p_match = len(toks) == 1 and len({x["ell"] for x in mt}) > 1
    print(f"  primitive MATCH const-word-count={toks} varied-ℓ "
          f"{'✓' if p_match else '✗ FAIL'}")
    ok &= p_match

    print("validate:", "ALL PASS ✓" if ok else "FAIL ✗")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# Y — type-register magnitude (§P-TYPE-GRAM-1 kind subspace, held-out fit)
# ══════════════════════════════════════════════════════════════════════════
def _orthonormal(cols: np.ndarray) -> np.ndarray:
    """Column-orthonormal basis of the span of `cols` (d, k) via QR."""
    q, _ = np.linalg.qr(cols)
    return q


def fit_type_subspace(h_probe: np.ndarray, op_ids: np.ndarray,
                      kind_ids: np.ndarray):
    """Kind register per layer (§P-TYPE-GRAM-1 cross-cut): remove per-opcode
    mean, then span the shared kind-centroid contrasts. Returns (mu, U) with
    mu (L,d) global mean and U (L,d,k) orthonormal kind subspace."""
    L, d = h_probe.shape[1], h_probe.shape[2]
    mu = h_probe.mean(axis=0)                                   # (L,d)
    U = np.zeros((L, d, TYPE_SUBSPACE_DIM))
    kinds = np.unique(kind_ids)
    for li in range(L):
        H = h_probe[:, li, :].copy()
        for op in np.unique(op_ids):                           # opcode-center
            m = op_ids == op
            H[m] -= H[m].mean(axis=0, keepdims=True)
        cents = np.stack([H[kind_ids == k].mean(axis=0) for k in kinds])  # (3,d)
        contrasts = (cents[1:] - cents[0]).T                   # (d, 2)
        U[li] = _orthonormal(contrasts)
    return mu, U


def y_project(h: np.ndarray, mu: np.ndarray, U: np.ndarray) -> float:
    """Band-mean ‖U_lᵀ(h_l − μ_l)‖ — type-register magnitude."""
    vals = [np.linalg.norm(U[li].T @ (h[li] - mu[li])) for li in range(h.shape[0])]
    return float(np.mean(vals))


def y_norm(h: np.ndarray, mu: np.ndarray) -> float:
    return float(np.mean([np.linalg.norm(h[li] - mu[li]) for li in range(h.shape[0])]))


def kind_margin_heldout(h_test: np.ndarray, kind_ids: np.ndarray,
                        mu: np.ndarray, U: np.ndarray) -> float:
    """FU5 sanity: on held-out probes, are kinds separated in U? between−within
    mean pairwise U-projection distance (>0 ⇒ register recovered)."""
    P = np.stack([U[li].T @ (h_test[:, li, :] - mu[li]).T
                  for li in range(h_test.shape[1])])            # (L,k,n)
    P = P.transpose(2, 0, 1).reshape(h_test.shape[0], -1)       # (n, L*k)
    within, between = [], []
    for i in range(len(P)):
        for j in range(i + 1, len(P)):
            dst = np.linalg.norm(P[i] - P[j])
            (within if kind_ids[i] == kind_ids[j] else between).append(dst)
    return float(np.mean(between) - np.mean(within))


# ══════════════════════════════════════════════════════════════════════════
# main — model load, capture, gates
# ══════════════════════════════════════════════════════════════════════════
def band_layers(nl: int) -> list[int]:
    return list(range(round(BAND_DEPTH[0] * nl), round(BAND_DEPTH[1] * nl) + 1))


def _load_type_probes(path: Path, n_train: int, n_test: int):
    d = json.load(open(path))
    states = d["states"]
    train, test = [], []
    for node, prompts in states.items():
        op, kind = node.split(":")
        for p in prompts[:n_train]:
            train.append((p, op, kind))
        for p in prompts[n_train:n_train + n_test]:
            test.append((p, op, kind))
    return train, test


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--n-train", type=int, default=40)
    ap.add_argument("--n-test", type=int, default=15)
    ap.add_argument("--out", default="results/fuel/qwen3-4b")
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    if args.validate:
        return 0 if validate() else 1

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    import verbum.jlens as jlens

    rng = np.random.default_rng(args.seed)
    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    nl = jlens.n_layers(model)
    tband = band_layers(nl)
    print(f"[fuel] {args.model_id} dev={dev} n_layers={nl} "
          f"band=L{tband[0]}..L{tband[-1]}", flush=True)

    def capture_band(text: str) -> np.ndarray:
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return np.stack([resid[li][-1].float().cpu().numpy() for li in tband])

    # ── fit type subspace on held-out §P-TYPE-GRAM-1 probes ──
    tp_path = _ROOT / "opcodes" / "data" / "type_probes.json"
    n_train, n_test = (8, 4) if args.smoke else (args.n_train, args.n_test)
    train, test = _load_type_probes(tp_path, n_train, n_test)
    print(f"[fuel] type probes: train={len(train)} test={len(test)}", flush=True)
    ops = sorted({o for _, o, _ in train})
    kinds = sorted({k for _, _, k in train})
    op_idx = {o: i for i, o in enumerate(ops)}
    kind_idx = {k: i for i, k in enumerate(kinds)}
    h_tr = np.stack([capture_band(p) for p, _, _ in train])
    op_ids = np.array([op_idx[o] for _, o, _ in train])
    kind_ids = np.array([kind_idx[k] for _, _, k in train])
    mu, U = fit_type_subspace(h_tr, op_ids, kind_ids)
    h_te = np.stack([capture_band(p) for p, _, _ in test])
    kind_te = np.array([kind_idx[k] for _, _, k in test])
    kmargin = kind_margin_heldout(h_te, kind_te, mu, U)
    print(f"[fuel] held-out kind_margin={kmargin:.4f}", flush=True)

    # matched-dim random subspaces (FU2 null), per layer
    d = h_tr.shape[2]
    R = [_orthonormal(rng.normal(size=(d, TYPE_SUBSPACE_DIM)))
         for _ in range(N_RAND_SUBSPACES)]

    # ── battery ──
    battery = build_battery(rng if not args.smoke
                            else np.random.default_rng(args.seed))
    if args.smoke:
        battery = battery[:24]
    print(f"[fuel] battery n={len(battery)} "
          f"(LIN {sum(x['family'] == 'LIN' for x in battery)} / "
          f"DUP {sum(x['family'] == 'DUP' for x in battery)} / "
          f"MATCH {sum(x['family'] == 'MATCH' for x in battery)})", flush=True)

    yt, yn, yr = [], [], []
    ell, mult, distinct, tokn, fam = [], [], [], [], []
    for i, x in enumerate(battery):
        h = capture_band(x["prompt"])
        yt.append(y_project(h, mu, U))
        yn.append(y_norm(h, mu))
        yr.append([float(np.mean([np.linalg.norm(Rk[:, :].T @ (h[li] - mu[li]))
                                  for li in range(h.shape[0])])) for Rk in R])
        ell.append(x["ell"])
        mult.append(x["mult"])
        distinct.append(x["distinct"])
        tokn.append(len(tok(x["prompt"]).input_ids))
        fam.append(x["family"])
        if (i + 1) % 20 == 0:
            print(f"[fuel]   captured {i + 1}/{len(battery)}", flush=True)

    yr = np.array(yr)                        # (n_terms, N_RAND)
    ell = np.array(ell, float)
    rand_rhos = np.array([spearman(yr[:, j], ell) for j in range(yr.shape[1])])

    dat = {"y_type": np.array(yt), "y_norm": np.array(yn), "ell": ell,
           "mult": np.array(mult, float), "distinct": np.array(distinct, float),
           "tok": np.array(tokn, float), "family": np.array(fam),
           "rand_rhos": rand_rhos, "kind_margin": kmargin,
           "all_nf": all(x["is_nf"] for x in battery)}
    res = compute_gates_fuel(dat, rng, _ALPHA)

    g = res["gates"]
    print(f"[fuel] FU1 p={g['FU1']['p']:.4f} {g['FU1']['pass']} | "
          f"FU2 r_type={g['FU2']['r_type']:.3f} r_norm={g['FU2']['r_norm']:.3f} "
          f"p_rand={g['FU2']['p_rand']:.4f} {g['FU2']['pass']} | "
          f"FU3 mult|dist={g['FU3']['rho_mult_given_distinct']:.3f} "
          f"dist|mult={g['FU3']['rho_distinct_given_mult']:.3f} "
          f"non_idem={g['FU3']['non_idem']} | "
          f"FU4 p={g['FU4']['p']:.4f} {g['FU4']['pass']} | "
          f"FU5 margin={g['FU5']['kind_margin']:.3f} {g['FU5']['pass']}", flush=True)
    print(f"[fuel] VERDICT: {res['verdict']}", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"model_id": args.model_id, "n_layers": nl, "band": [tband[0], tband[-1]],
            "n_terms": len(battery), "n_train": len(train), "n_test": len(test),
            "seed": args.seed, "smoke": args.smoke}
    json.dump({**res, "means": {"kind_margin": kmargin},
               "meta": meta}, open(out / "results.json", "w"), indent=1)
    np.savez_compressed(
        out / "fuel.npz",
        y_type=dat["y_type"], y_norm=dat["y_norm"], ell=ell,
        mult=dat["mult"], distinct=dat["distinct"], tok=dat["tok"],
        family=dat["family"], rand_rhos=rand_rhos)
    print(f"[fuel] wrote {out}/results.json + fuel.npz", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
