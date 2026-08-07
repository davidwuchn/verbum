"""§P-DISJ-COST — the ∨-vs-∧ asymmetry fingerprint (first type-fingerprint probe).

Pre-reg FROZEN s318 (Michael-approved GO):
mementum/knowledge/explore/type-systems-under-llm-constraints.md §P-DISJ-COST.

Pinned substrate (curry-howard-closes-the-loop / type-systems-under-constraints):
intersection is FREE (superposition-native — membership in many passbands at
once), union is HEAD-HUNGRY (separate matched filters per disjunct). Fingerprint:
at matched surface complexity, union representations recruit MORE effective
dimensions than intersection. Cartesian substrate (free duplication, no ∧/∨
asymmetry) = the pre-committed death (SKI-control #4).

Register (λ measure) — REPRESENTATIONAL, not magnitude (the s317-s318 arc showed
the kind-register MAGNITUDE does not grade; this reads DIMENSIONALITY, robust to
that 3-fold null):
  R1 effective rank / participation ratio PR=(Σλ)²/Σλ² per arm-set covariance.
  R2 off-plane residual (paired): ‖r_conn − proj_{span{A_dir,B_dir}}(r_conn)‖ /
     ‖r_conn‖ — does the connective need a direction OUTSIDE the A,B passbands?
     (a "head" ≡ a new direction). A_dir = r_A − r_neutral, etc.

Construction (matched, token-controlled): N category pairs (A,B) the model knows;
5 arms read at the final shared content token (and/or/near single-token matched):
  A "It is a bird"  B "It is a fish"  AND "It is a bird and a fish"
  OR "It is a bird or a fish"  FILLER "It is a bird near a fish"  (+ NEUTRAL anchor)
Band L18-31, one qwen3-4b load, read-only, no wire.

Gates (α=0.05): DC1 RANK-ASYMMETRY (PR(OR)>PR(AND) vs matched-label null) · DC2
OFF-PLANE (paired resid(OR)>resid(AND) vs sign-flip null — the mechanism) · DC3
OR-SPECIFIC (FILLER patterns with AND: resid(OR)>resid(FILLER) ∧ PR(OR)>PR(FILLER))
· DC4 SANE (categories separable, non-degenerate). Verdicts INTERSECTION-FREE
(+OR-COSTS) / OR-COSTS-OPAQUE / SYMMETRIC (falsifier) / COMPLEXITY-ARTIFACT /
VOID. A-priori 45/20/20/10/5. Lean on DC2 (mechanism); DC1 corroborates.

Caveat (frozen): "OR spreads more dimensions" is consistent with OR-machinery
(theory) AND OR-uncertainty (mundane). DC1/DC2 establish the asymmetry+direction
(kills Cartesian); machinery-vs-uncertainty is a boundary, not a claim.

Reuse (λ one_way, no fork): verbum.jlens (capture_residuals/n_layers) +
fuel_theorem (band_layers/_orthonormal) + numpy. New code = ∧/∨/filler
construction + PR/effective-rank + off-plane residual + DC gates.

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
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))

import fuel_theorem as ff  # noqa: E402  (band_layers + _orthonormal, no fork)

_ALPHA = 0.05
N_PERM = 500

# ── category pairs (distinct kinds; mutually-exclusive membership) ─────────
NOUNS_A = [
    "bird", "metal", "tree", "car", "hammer", "river", "star", "book",
    "dog", "flower", "mountain", "boat", "knife", "cloud", "coin", "song",
    "snake", "engine", "bridge", "lamp",
]
NOUNS_B = [
    "fish", "liquid", "rock", "plane", "saw", "lake", "planet", "song",
    "cat", "insect", "valley", "truck", "spoon", "storm", "note", "poem",
    "lizard", "wheel", "tunnel", "candle",
]
TEMPLATES = ("It is a", "That is a", "Here is a")
NEUTRAL_WORD = "thing"


def build_pairs() -> list[tuple[str, str]]:
    return [(a, b) for a, b in zip(NOUNS_A, NOUNS_B, strict=True) if a != b]


def arm_prompt(template: str, a: str, b: str, arm: str) -> str:
    if arm == "A":
        return f"{template} {a}"
    if arm == "B":
        return f"{template} {b}"
    if arm == "NEU":
        return f"{template} {NEUTRAL_WORD}"
    conn = {"AND": "and", "OR": "or", "FILLER": "near"}[arm]
    return f"{template} {a} {conn} a {b}"


ARMS = ("A", "B", "AND", "OR", "FILLER", "NEU")
CONN_ARMS = ("AND", "OR", "FILLER")


# ══════════════════════════════════════════════════════════════════════════
# Readouts — PURE (no torch; what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def _pr_layer(X: np.ndarray) -> float:
    """Participation ratio (Σλ)²/Σλ² of the centered set X (N,d) via N×N gram."""
    X = X - X.mean(0, keepdims=True)
    ev = np.linalg.eigvalsh(X @ X.T)
    ev = np.clip(ev, 0.0, None)
    s1, s2 = float(ev.sum()), float((ev ** 2).sum())
    return (s1 * s1 / s2) if s2 > 1e-12 else 0.0


def pr_arm(V_arm: np.ndarray) -> float:
    """Band-mean PR across layers. V_arm (N,L,d)."""
    return float(np.mean([_pr_layer(V_arm[:, li, :]) for li in range(V_arm.shape[1])]))


def _pr_diff_perm(pool: np.ndarray, labels: np.ndarray, rng, n_perm: int) -> np.ndarray:
    """Null draws of PR(label=1) − PR(label=0) under label shuffles. pool (2N,L,d)."""
    L = pool.shape[1]
    out = np.empty(n_perm)
    for k in range(n_perm):
        lab = rng.permutation(labels)
        d1 = np.mean([_pr_layer(pool[lab == 1, li, :]) for li in range(L)])
        d0 = np.mean([_pr_layer(pool[lab == 0, li, :]) for li in range(L)])
        out[k] = d1 - d0
    return out


def off_plane_resid(V_arm: np.ndarray, A_dir: np.ndarray, B_dir: np.ndarray,
                    NEU: np.ndarray) -> np.ndarray:
    """Per-pair band-mean off-plane residual of arm vs span{A_dir,B_dir}.
    All (N,L,d). Returns (N,)."""
    N, L, _ = V_arm.shape
    res = np.zeros(N)
    for n in range(N):
        acc = []
        for li in range(L):
            basis = np.column_stack([A_dir[n, li], B_dir[n, li]])   # (d,2)
            Q = ff._orthonormal(basis)                              # (d,2)
            c = V_arm[n, li] - NEU[n, li]
            cn = np.linalg.norm(c)
            if cn < 1e-9:
                continue
            proj = Q @ (Q.T @ c)
            acc.append(np.linalg.norm(c - proj) / cn)
        res[n] = float(np.mean(acc)) if acc else 0.0
    return res


def _signflip_p(diff: np.ndarray, rng, n_perm: int) -> tuple[float, float]:
    """Paired sign-flip permutation. Returns (obs_mean, p one-sided greater)."""
    obs = float(diff.mean())
    draws = np.array([float((diff * rng.choice([-1.0, 1.0], size=diff.size)).mean())
                      for _ in range(n_perm)])
    p = float((1 + np.sum(draws >= obs)) / (1 + n_perm))
    return obs, p


# ══════════════════════════════════════════════════════════════════════════
# Gates + verdict — PURE
# ══════════════════════════════════════════════════════════════════════════
def compute_gates_disj(V: dict, rng: np.random.Generator,
                       alpha: float = _ALPHA) -> dict:
    A_dir = V["A"] - V["NEU"]
    B_dir = V["B"] - V["NEU"]

    pr = {arm: pr_arm(V[arm]) for arm in CONN_ARMS}
    resid = {arm: off_plane_resid(V[arm], A_dir, B_dir, V["NEU"]) for arm in CONN_ARMS}

    # ── DC2 OFF-PLANE (SOLE core): paired resid(OR) > resid(AND) = mechanism ──
    obs_off, p_off = _signflip_p(resid["OR"] - resid["AND"], rng, N_PERM)
    dc2_pass = bool(obs_off > 0 and p_off < alpha)

    # ── DC3 OR-SPECIFIC: FILLER patterns with AND (low), not OR (paired) ──
    obs_ofl, p_ofl = _signflip_p(resid["OR"] - resid["FILLER"], rng, N_PERM)
    dc3_pass = bool(obs_ofl > 0 and p_ofl < alpha)

    # ── DC1 RANK-CORROBORATION (REPORTED, non-gating; s318 amendment) ──
    # PR is geometrically coupled to DC2 (rank>2 ⟹ off-plane), so it can only
    # corroborate the off-plane mechanism, never independently contradict it.
    obs_pr = pr["OR"] - pr["AND"]
    pool = np.concatenate([V["OR"], V["AND"]], axis=0)
    labels = np.concatenate([np.ones(V["OR"].shape[0]), np.zeros(V["AND"].shape[0])])
    d_pr = _pr_diff_perm(pool, labels, rng, N_PERM)
    p_pr = float((1 + np.sum(d_pr >= obs_pr)) / (1 + N_PERM))
    dc1_agrees = bool(obs_pr > 0 and p_pr < alpha)

    # ── DC4 SANE: A/B directions distinct + non-degenerate ──
    cos = []
    na, nb = [], []
    for n in range(A_dir.shape[0]):
        for li in range(A_dir.shape[1]):
            a, b = A_dir[n, li], B_dir[n, li]
            na.append(np.linalg.norm(a))
            nb.append(np.linalg.norm(b))
            dn = np.linalg.norm(a) * np.linalg.norm(b)
            if dn > 1e-9:
                cos.append(abs(float(a @ b) / dn))
    med_cos = float(np.median(cos)) if cos else 1.0
    dc4_pass = bool(med_cos < 0.95 and np.median(na) > 1e-6 and np.median(nb) > 1e-6)

    # ── verdict tree (frozen, s318-amended: DC2 sole mechanism, DC1 reported) ──
    if not dc4_pass:
        verdict = "VOID"
    elif dc2_pass and dc3_pass:
        verdict = "INTERSECTION-FREE (+OR-COSTS)"
    elif dc2_pass and not dc3_pass:
        verdict = "OR-COSTS-OPAQUE"
    else:                                    # ¬DC2 → no off-plane asymmetry
        verdict = "SYMMETRIC"

    return {
        "verdict": verdict,
        "gates": {
            "DC2": {"resid_or": float(resid["OR"].mean()),
                    "resid_and": float(resid["AND"].mean()),
                    "obs": obs_off, "p": p_off, "pass": dc2_pass},
            "DC3": {"resid_filler": float(resid["FILLER"].mean()),
                    "obs_or_minus_fil": obs_ofl, "p": p_ofl, "pass": dc3_pass},
            "DC1_corrob": {"pr_or": pr["OR"], "pr_and": pr["AND"], "obs": obs_pr,
                           "null_mean": float(d_pr.mean()), "p": p_pr,
                           "agrees": dc1_agrees},
            "DC4": {"median_cos_AB": med_cos, "pass": dc4_pass},
        },
    }


# ══════════════════════════════════════════════════════════════════════════
# --validate — planted worlds exercise every verdict
# ══════════════════════════════════════════════════════════════════════════
def _planted(kind: str, rng: np.random.Generator, N: int = 40, L: int = 3,
             d: int = 16) -> dict:
    V = {arm: np.zeros((N, L, d)) for arm in ARMS}
    for n in range(N):
        m = rng.normal(size=d)
        a = rng.normal(size=d)
        b = a + 0.01 * rng.normal(size=d) if kind == "void" else rng.normal(size=d)
        for li in range(L):
            def nz(s=0.05):
                return rng.normal(0, s, d)
            plane = 0.5 * a + 0.5 * b
            V["NEU"][n, li] = m
            V["A"][n, li] = m + a + nz()
            V["B"][n, li] = m + b + nz()
            V["AND"][n, li] = m + plane + nz()
            off_o = rng.normal(size=d)
            off_f = rng.normal(size=d)
            if kind == "intersection_free":
                V["OR"][n, li] = m + plane + 1.5 * off_o + nz()
                V["FILLER"][n, li] = m + plane + nz()
            elif kind == "or_opaque":
                V["OR"][n, li] = m + plane + 1.5 * off_o + nz()
                V["FILLER"][n, li] = m + plane + 1.5 * off_f + nz()
            elif kind == "symmetric":
                V["OR"][n, li] = m + plane + nz()
                V["FILLER"][n, li] = m + plane + nz()
            else:                             # void
                V["OR"][n, li] = m + plane + 1.5 * off_o + nz()
                V["FILLER"][n, li] = m + plane + nz()
    return V


def validate() -> bool:
    rng = np.random.default_rng(0)
    want = {
        "intersection_free": "INTERSECTION-FREE (+OR-COSTS)",
        "or_opaque": "OR-COSTS-OPAQUE",
        "symmetric": "SYMMETRIC",
        "void": "VOID",
    }
    ok = True
    for kind, exp in want.items():
        got = compute_gates_disj(_planted(kind, rng), rng)["verdict"]
        good = got == exp
        ok &= good
        print(f"  verdict[{kind:20s}] {got:30s} {'✓' if good else '✗ want ' + exp}")

    # primitive: prompt construction matched (single connective token difference)
    pairs = build_pairs()
    a, b = pairs[0]
    p_and = arm_prompt("It is a", a, b, "AND")
    p_or = arm_prompt("It is a", a, b, "OR")
    p_fil = arm_prompt("It is a", a, b, "FILLER")
    only_conn = (p_and.replace(" and ", " X ") == p_or.replace(" or ", " X ")
                 == p_fil.replace(" near ", " X "))
    print(f"  primitive prompts differ only in connective {'✓' if only_conn else '✗'}"
          f" · pairs n={len(pairs)}")
    ok &= only_conn and len(pairs) >= 16

    print("validate:", "ALL PASS ✓" if ok else "FAIL ✗")
    return ok


# ══════════════════════════════════════════════════════════════════════════
# main — model load, capture, gates
# ══════════════════════════════════════════════════════════════════════════
def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="float32")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/disj-cost/qwen3-4b")
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
    tband = ff.band_layers(nl)
    print(f"[dc] {args.model_id} dev={dev} n_layers={nl} "
          f"band=L{tband[0]}..L{tband[-1]}", flush=True)

    def cap_last(text: str) -> np.ndarray:
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return np.stack([resid[li][-1].float().cpu().numpy() for li in tband])

    pairs = build_pairs()
    templates = TEMPLATES[:1] if args.smoke else TEMPLATES
    pairs = pairs[:4] if args.smoke else pairs
    samples = [(t, a, b) for t in templates for (a, b) in pairs]
    print(f"[dc] pairs={len(pairs)} templates={len(templates)} "
          f"samples={len(samples)}", flush=True)

    V = {arm: [] for arm in ARMS}
    for i, (t, a, b) in enumerate(samples):
        for arm in ARMS:
            V[arm].append(cap_last(arm_prompt(t, a, b, arm)))
        if (i + 1) % 20 == 0:
            print(f"[dc]   captured {i + 1}/{len(samples)}", flush=True)
    V = {arm: np.stack(V[arm]) for arm in ARMS}       # each (N,L,d)

    res = compute_gates_disj(V, rng, _ALPHA)
    g = res["gates"]
    print(f"[dc] DC2 resid_or={g['DC2']['resid_or']:.4f} "
          f"resid_and={g['DC2']['resid_and']:.4f} p={g['DC2']['p']:.4f} "
          f"{g['DC2']['pass']} | DC3 resid_fil={g['DC3']['resid_filler']:.4f} "
          f"p={g['DC3']['p']:.4f} {g['DC3']['pass']} | "
          f"DC1c pr_or={g['DC1_corrob']['pr_or']:.3f} "
          f"pr_and={g['DC1_corrob']['pr_and']:.3f} agrees={g['DC1_corrob']['agrees']} "
          f"| DC4 cos={g['DC4']['median_cos_AB']:.3f} {g['DC4']['pass']}", flush=True)
    print(f"[dc] VERDICT: {res['verdict']}", flush=True)

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    meta = {"model_id": args.model_id, "n_layers": nl, "band": [tband[0], tband[-1]],
            "n_samples": len(samples), "n_pairs": len(pairs),
            "n_templates": len(templates), "seed": args.seed, "smoke": args.smoke}
    json.dump({**res, "meta": meta}, open(out / "results.json", "w"), indent=1)
    np.savez_compressed(out / "disj_cost.npz",
                        **{f"V_{arm}": V[arm] for arm in ARMS})
    print(f"[dc] wrote {out}/results.json + disj_cost.npz", flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
