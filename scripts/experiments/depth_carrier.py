#!/usr/bin/env python3
"""§P-DEPTH-CARRIER — is answer assembly a charged rotation? (s348).

FROZEN DESIGN: mementum/knowledge/explore/answer-assembly-is-a-charged-rotation.md
(committed c953705d BEFORE data, Michael GO).

The s346 REPL pilot saw the DECIDING state's DEPTH trajectory (residual stream
of the state that emits the answer token, layer 0 -> L) as a coherent spiral in
a 2-plane: CHARGES geometrically while PRECESSING then DISCHARGES at the final
layer. Charging is mundane (norm grows with depth in every transformer). THE
CLAIM UNDER TEST is the coherent, answer-aligned ROTATION — not the charge.

Object: per prompt, H = driver.bounce(prompt).hidden[k] in R^{(L+1) x d}, where
k = the frame that emits the first answer content token. Battery = task types
(reduction / dates / arith / code_scope / prose), each with one answer token.

Plane (pre-registered, DMD-first): DC-center H; leading complex-conjugate DMD
eigenpair (|phase| > 5 deg) -> plane = span{Re(v), Im(v)}; SVD-fallback (top-2
right singular vectors) if DC-dominated (flagged plane=svd).

Rotation metric ROT = |mean_rate| * planarity over the charging band — high ONLY
for consistent-rate rotation in a genuinely 2D plane (a norm-growth RAY has
planarity ~0; incoherent drift has mean_rate ~0). Separated from R (concentration)
and rho (rate, deg/layer), reported as descriptors.

Nulls (re-extract the plane each draw): N1 shuffled-layer, N2 increment-shuffle,
N3 NORM-MATCHED RANDOM-PLANE (make-or-break for GENERIC: same per-layer step
norms, isotropic-random directions). N4 answer-axis = random-token unembedding
cosines.

FROZEN verdict tree + a-priori mass:
  CHARGED-ROTATION          35  G1 (ROT beats N1,N2,N3) AND G2 (answer-aligned)
  GENERIC-NORM-GROWTH-ONLY  30  G1 fail (rotation is a norm-growth artifact)
  MIXED                     25  G1 pass, G2 fail (coherent rotation, generic plane)
  VOID                      10  G0 fail (no determinism / no charge / no plane)

Discipline: CHARGED-ROTATION is a DESCRIPTIVE geometric verdict — it does NOT
license homeostat / persistent-mode / modulation vocabulary (frame_ledger 0-3,
s326); |lambda|~1 is a DMD-average of charge(>1) x discharge(<1), not a
persistent mode (s340 persist_frac 0.0). Capture-euphoria guard: the s346 pilot
FEEDS this design, it is NOT evidence in this ledger.

`--validate` drives 5 planted worlds through the REAL analyse path.

Bounds: n=1 model (Qwen3-14B), greedy, last-token deciding state, today's
battery. One-directional (GENERIC/MIXED are the informative kills).

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from datetime import UTC, datetime
from math import comb
from pathlib import Path

import numpy as np

_SCRIPT_DIR = Path(__file__).resolve().parent
_ROOT = _SCRIPT_DIR.parents[1]
sys.path.insert(0, str(_ROOT / "src"))

from verbum.operator_dmd import reduced_dmd  # noqa: E402

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s348 pre-data freeze c953705d)

SEED = 348
PHASE_MIN_RAD = np.deg2rad(5.0)   # DMD pair selection threshold
BAND_LO = 4                       # skip embedding + early warmup layers
CHARGE_MIN = 4.0                  # amplitude must grow >= 4x over band (validity)
BAND_MIN = 3                      # minimum band length (layers)
N_PERM_PLANE = 200                # trajectory nulls (re-extract plane each draw)
N_PERM = 2000                     # answer-axis + label nulls
N_RAND_TOK = 512                  # random-token unembedding rows for N4
MIN_PER_TASK = 4
MIN_TOTAL = 20
ALPHA = 0.05
DECODE_N = 8                      # tokens to decode (answer token is early)
EPS = 1e-9

TASKS: dict[str, list[tuple[str, str]]] = {
    "arith": [
        ("7 + 5 = ", "12"), ("6 + 3 = ", "9"), ("9 + 8 = ", "17"),
        ("4 + 4 = ", "8"), ("11 + 2 = ", "13"), ("5 + 6 = ", "11"),
        ("8 + 7 = ", "15"), ("3 + 9 = ", "12"), ("10 + 5 = ", "15"),
        ("2 + 2 = ", "4"),
    ],
    "dates": [
        ("Monday, Tuesday, Wednesday. The day after Tuesday is ", "Wednesday"),
        ("If today is Monday, in two days it will be ", "Wednesday"),
        ("The day after Friday is ", "Saturday"),
        ("Sunday, Monday, Tuesday. The day before Monday is ", "Sunday"),
        ("Three days after Monday is ", "Thursday"),
        ("The day after Saturday is ", "Sunday"),
        ("If today is Wednesday, tomorrow is ", "Thursday"),
        ("The day before Sunday is ", "Saturday"),
        ("Two days after Thursday is ", "Saturday"),
        ("The day after Sunday is ", "Monday"),
    ],
    "prose": [
        ("The capital of France is ", "Paris"),
        ("The opposite of hot is ", "cold"),
        ("The sky on a clear day is ", "blue"),
        ("The capital of Japan is ", "Tokyo"),
        ("The opposite of up is ", "down"),
        ("Water is made of hydrogen and ", "oxygen"),
        ("The first month of the year is ", "January"),
        ("The opposite of black is ", "white"),
        ("A dog says woof and a cat says ", "meow"),
        ("The capital of Italy is ", "Rome"),
    ],
    "code_scope": [
        ("x = 42\nprint(x)\n", "42"),
        ("a = 7\nb = a\nprint(b)\n", "7"),
        ("n = 100\nprint(n)\n", "100"),
        ("y = 5\nprint(y)\n", "5"),
        ("val = 13\nprint(val)\n", "13"),
        ("count = 8\nprint(count)\n", "8"),
        ("z = 21\nprint(z)\n", "21"),
        ("k = 3\nprint(k)\n", "3"),
        ("total = 55\nprint(total)\n", "55"),
        ("m = 9\nprint(m)\n", "9"),
    ],
}
# reduction uses a shared rule header
_RED_HEADER = "Rules: I x = x; K x y = x; S f g x = f x (g x); C f x y = f y x.\n"
TASKS["reduction"] = [
    (_RED_HEADER + "I a = ", "a"),
    (_RED_HEADER + "K a b = ", "a"),
    (_RED_HEADER + "K p q = ", "p"),
    (_RED_HEADER + "S K K a = ", "a"),
    (_RED_HEADER + "I q = ", "q"),
    (_RED_HEADER + "K b a = ", "b"),
    (_RED_HEADER + "C K a b = ", "b"),
    (_RED_HEADER + "S K K b = ", "b"),
    (_RED_HEADER + "K x y = ", "x"),
    (_RED_HEADER + "I p = ", "p"),
]


def log(msg: str) -> None:
    print(f"[depth-carrier] {msg}", flush=True)


def git_sha() -> str:
    try:
        return subprocess.run(
            ["git", "rev-parse", "HEAD"], cwd=_ROOT, capture_output=True,
            text=True, check=True,
        ).stdout.strip()
    except Exception:
        return "unknown"


def _json_native(o):
    if isinstance(o, np.integer):
        return int(o)
    if isinstance(o, np.floating):
        return float(o)
    if isinstance(o, np.ndarray):
        return o.tolist()
    if isinstance(o, np.bool_):
        return bool(o)
    raise TypeError(f"not JSON-serializable: {type(o)}")


def binom_sf(k: int, n: int, p: float) -> float:
    """P(X >= k) for X ~ Binomial(n, p)."""
    if k <= 0:
        return 1.0
    if k > n:
        return 0.0
    return float(sum(comb(n, i) * p**i * (1 - p) ** (n - i) for i in range(k, n + 1)))


# ---------------------------------------------------------------------------
# geometry (the analyse core — planted worlds drive this same code)


def _orthonormal2(v0: np.ndarray, v1: np.ndarray) -> np.ndarray | None:
    a = v0.astype(np.float64)
    na = np.linalg.norm(a)
    if na < EPS:
        return None
    a = a / na
    b = v1.astype(np.float64) - (v1 @ a) * a
    nb = np.linalg.norm(b)
    if nb < EPS:
        return None
    return np.stack([a, b / nb])  # (2, d)


def extract_rotation(H: np.ndarray, rank: int = 2):
    """Fit a rank-2 DMD to the DC-centered depth trajectory.

    Returns (B, mode, phase_rad, resid_r2, has_pair):
      - a clean rotation-with-growth IS a rank-2 linear operator h(l+1)=A h(l)
        with a COMPLEX eigenpair (|lambda| = charge, angle = precession rate)
        and LOW reconstruction residual;
      - a norm-growth RAY has a REAL leading eigenpair (no rotation);
      - a random walk is full-rank -> HIGH rank-2 residual.
    B spans the rotation plane (complex-pair) or the SVD-fallback top-2.
    """
    Hc = H.astype(np.float64) - H.astype(np.float64).mean(0)
    dd = reduced_dmd(Hc[:-1].T, Hc[1:].T, rank)
    resid = float(dd["rel_resid"])
    At, Ur = dd["A_tilde"], dd["Ur"]
    B, phase, has_pair = None, 0.0, False
    if At.shape[0] >= 2:
        evals, evecs = np.linalg.eig(At)
        i = int(np.argmax(np.abs(evals.imag)))
        ph = abs(float(np.angle(evals[i])))
        if np.abs(evals[i].imag) > 1e-9 and ph > PHASE_MIN_RAD:
            v = Ur @ evecs[:, i]  # complex (d,)
            B = _orthonormal2(np.real(v), np.imag(v))
            if B is not None:
                phase = ph
                has_pair = True
    if B is None:  # SVD-fallback plane for descriptors (no rotation pair)
        try:
            _, _, Vt = np.linalg.svd(Hc, full_matrices=False)
        except np.linalg.LinAlgError:
            return None, "fail", 0.0, 1.0, False
        if Vt.shape[0] < 2:
            return None, "fail", 0.0, 1.0, False
        B = Vt[:2]
    return B, ("dmd" if has_pair else "svd"), phase, resid, has_pair


def rotation_metrics(H: np.ndarray, B: np.ndarray, phase: float, resid: float,
                     has_pair: bool) -> dict:
    """Validity (charge) + descriptors; the primary rotation stat is `resid`.

    resid = rank-2 DMD reconstruction residual (LOWER = more rotation-structured);
    has_pair = the leading eigenpair is complex with |phase| > PHASE_MIN (a
    rotation, not a real-growth ray). ROT is a logged descriptor only.
    """
    Hf = H.astype(np.float64)
    raw_norm = np.linalg.norm(Hf, axis=1)
    Hc = Hf - Hf.mean(0)
    coords = Hc @ B.T  # (T, 2)
    a = np.linalg.norm(coords, axis=1)
    T = coords.shape[0]
    start, end = BAND_LO, T - 2  # exclude the final-layer discharge transition
    band_len = end - start
    charge = float(raw_norm[end] / (raw_norm[start] + EPS))  # RAW norm growth
    discharge = float(a[-1] / (a[-2] + EPS))
    if band_len < BAND_MIN or a.max() < EPS or charge < CHARGE_MIN:
        return {"valid": False, "reason": "no-charge", "ROT": 0.0, "R": 0.0,
                "rho_deg": float(np.rad2deg(phase)), "planarity": 0.0,
                "resid": resid, "has_pair": bool(has_pair), "charge": charge,
                "discharge": discharge, "band_len": max(band_len, 0)}
    xb, yb = coords[start:end + 1, 0], coords[start:end + 1, 1]
    sx, sy = float(np.std(xb)), float(np.std(yb))
    planarity = float(min(sx, sy) / (max(sx, sy) + EPS))
    R = 1.0 - resid  # rank-2 reconstruction quality (descriptor)
    ROT = R * phase * planarity
    return {"valid": True, "reason": "ok", "ROT": ROT, "R": R,
            "rho_deg": float(np.rad2deg(phase)), "planarity": planarity,
            "resid": resid, "has_pair": bool(has_pair), "charge": charge,
            "discharge": discharge, "band_len": band_len}


def answer_align(B: np.ndarray, u_ans: np.ndarray) -> tuple[float, int]:
    u = u_ans.astype(np.float64)
    nu = np.linalg.norm(u)
    if nu < EPS:
        return 0.0, 0
    cos = np.abs(B @ u) / (np.linalg.norm(B, axis=1) * nu)
    return float(cos.max()), int(np.argmax(cos))


def _resid_null(H: np.ndarray, kind: str, n_perm: int, rng) -> np.ndarray:
    """rank-2 DMD residual distribution under a trajectory null.

    A pid's rotation is real iff it reconstructs BETTER (lower residual) than
    these matched nulls. norm_matched is the make-or-break: same per-layer step
    NORMS, isotropic-random DIRECTIONS (a random walk is full-rank -> high resid).
    """
    H = H.astype(np.float64)
    incs = np.diff(H, axis=0)
    norms = np.linalg.norm(incs, axis=1)
    out = np.full(n_perm, 1.0)
    for k in range(n_perm):
        if kind == "shuffled_layer":
            Hs = H[rng.permutation(H.shape[0])]
        elif kind == "increment_shuffle":
            perm_inc = incs[rng.permutation(len(incs))]
            Hs = np.vstack([H[0], H[0] + np.cumsum(perm_inc, 0)])
        elif kind == "norm_matched":
            dirs = rng.standard_normal(incs.shape)
            dirs /= (np.linalg.norm(dirs, axis=1, keepdims=True) + EPS)
            Hs = np.vstack([H[0], H[0] + np.cumsum(dirs * norms[:, None], 0)])
        else:
            raise ValueError(kind)
        _, _, _, resid, has_pair = extract_rotation(Hs)
        out[k] = resid if has_pair else 1.0  # no complex pair -> no rotation
    return out


def analyse(records: list[dict], U_rand: np.ndarray, seed: int = SEED,
            n_perm_plane: int = N_PERM_PLANE, min_total: int = MIN_TOTAL,
            min_per_task: int = MIN_PER_TASK, det_ok: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    per: list[dict] = []
    for r in records:
        H = np.asarray(r["H"], dtype=np.float64)
        B, mode, phase, resid, has_pair = extract_rotation(H)
        if B is None:
            per.append({"pid": r["pid"], "task": r["task"], "valid": False,
                        "reason": "no-plane", "plane_mode": mode})
            continue
        m = rotation_metrics(H, B, phase, resid, has_pair)
        a_align, axis_i = answer_align(B, np.asarray(r["u_ans"], dtype=np.float64))
        rec = {"pid": r["pid"], "task": r["task"], "plane_mode": mode,
               "a_align": a_align, "answer_axis": axis_i, **m}
        if m["valid"]:
            # a pid rotates iff it has a complex pair AND reconstructs BETTER
            # (lower rank-2 residual) than the matched trajectory nulls.
            for kind, key in (("shuffled_layer", "N1"), ("increment_shuffle", "N2"),
                              ("norm_matched", "N3")):
                null = _resid_null(H, kind, n_perm_plane, rng)
                rec[f"{key}_q05"] = float(np.quantile(null, 0.05))
                rec[f"beats_{key}"] = bool(has_pair and resid < rec[f"{key}_q05"])
            # N4 answer-axis null: random-token cosines vs the same plane
            nu = np.linalg.norm(U_rand, axis=1)
            bn = np.linalg.norm(B, axis=1)[None]
            cos = np.abs(U_rand @ B.T) / (nu[:, None] * bn + EPS)
            null4 = cos.max(axis=1)
            rec["N4_q95"] = float(np.quantile(null4, 0.95))
            rec["beats_N4"] = bool(a_align > rec["N4_q95"])
        per.append(rec)

    valid = [p for p in per if p.get("valid")]
    n_valid = len(valid)
    per_task_counts = {t: sum(1 for p in valid if p["task"] == t) for t in TASKS}
    tasks_ok = sum(1 for c in per_task_counts.values() if c >= min_per_task)
    g0_pass = bool(det_ok) and n_valid >= min_total and tasks_ok >= 2

    def _gate(key: str) -> tuple[int, float, bool]:
        nb = sum(1 for p in valid if p.get(key))
        pval = binom_sf(nb, n_valid, ALPHA) if n_valid else 1.0
        return nb, pval, pval < ALPHA

    n1 = _gate("beats_N1")
    n2 = _gate("beats_N2")
    n3 = _gate("beats_N3")
    g1_pass = g0_pass and n1[2] and n2[2] and n3[2]
    n4 = _gate("beats_N4")
    g2_pass = g1_pass and n4[2]

    # G3 (qualifier): cross-task consistency of |rho| vs shuffled-task-label null
    g3_pass = False
    cv_real = cv_q05 = float("nan")
    if n_valid >= min_total and tasks_ok >= 2:
        rhos = np.array([abs(p["rho_deg"]) for p in valid])
        labs = np.array([p["task"] for p in valid])
        def _cv(labels):
            means = [rhos[labels == t].mean() for t in TASKS
                     if (labels == t).sum() >= min_per_task]
            means = np.array(means)
            if len(means) < 2:
                return np.nan
            return float(np.std(means) / (np.mean(means) + EPS))
        cv_real = _cv(labs)
        null_cv = np.array([_cv(rng.permutation(labs)) for _ in range(N_PERM)])
        null_cv = null_cv[~np.isnan(null_cv)]
        if not np.isnan(cv_real) and null_cv.size:
            cv_q05 = float(np.quantile(null_cv, 0.05))
            g3_pass = cv_real < cv_q05

    if not g0_pass:
        verdict = "VOID"
    elif not g1_pass:
        verdict = "GENERIC-NORM-GROWTH-ONLY"
    elif not g2_pass:
        verdict = "MIXED"
    else:
        verdict = "CHARGED-ROTATION"
    qualifier = None
    if verdict == "CHARGED-ROTATION":
        qualifier = "universal" if g3_pass else "per-task"

    def _med(key: str) -> float:
        return float(np.median([p[key] for p in valid])) if valid else float("nan")

    med_align = _med("a_align")
    med_rot = _med("ROT")
    med_rho = _med("rho_deg")
    med_charge = _med("charge")
    return {
        "verdict": verdict, "qualifier": qualifier, "g0_pass": g0_pass,
        "g1_pass": g1_pass, "g2_pass": g2_pass, "g3_pass": g3_pass,
        "det_ok": bool(det_ok), "n_valid": n_valid, "n_records": len(per),
        "per_task_valid": per_task_counts, "tasks_ok": tasks_ok,
        "N1": {"n_beat": n1[0], "p": n1[1]}, "N2": {"n_beat": n2[0], "p": n2[1]},
        "N3": {"n_beat": n3[0], "p": n3[1]}, "N4": {"n_beat": n4[0], "p": n4[1]},
        "cv_rho_real": cv_real, "cv_rho_q05": cv_q05,
        "median_a_align": med_align, "median_ROT": med_rot,
        "median_rho_deg": med_rho, "median_charge": med_charge,
        "per_pid": per,
    }


# ---------------------------------------------------------------------------
# capture (driver — depth trajectory of the deciding state)


def capture(model_id: str, tasks: dict, seed: int) -> dict:
    from verbum.driver import Driver

    d = Driver(model_id=model_id)
    validity = d.validity()
    log(f"driver validity: {validity}")
    W = d.model.lm_head.weight.detach().float().cpu().numpy()  # (vocab, d)
    rng = np.random.default_rng(seed)
    ridx = rng.choice(W.shape[0], size=N_RAND_TOK, replace=False)
    U_rand = W[ridx].astype(np.float32)

    records, arrays = [], {}
    t0 = time.time()
    for task, items in tasks.items():
        for j, (prompt, expected) in enumerate(items):
            b = d.bounce(prompt, n=DECODE_N, hidden=True, keep_seal=False)
            if b.hidden is None or len(b.tokens) == 0:
                continue
            k = next((i for i, t in enumerate(b.tokens) if t.strip()), None)
            if k is None:
                continue
            H = b.hidden[k].astype(np.float32)  # (L+1, d)
            tok_id = int(b.new_ids[k])
            u_ans = W[tok_id].astype(np.float32)
            gen = "".join(b.tokens).strip()
            pid = f"{task}{j}"
            records.append({
                "pid": pid, "task": task, "prompt": prompt, "expected": expected,
                "answer_token": b.tokens[k], "answer_token_id": tok_id,
                "generated": gen, "correct": gen.startswith(expected),
                "H": H, "u_ans": u_ans,
            })
            arrays[f"H_{pid}"] = H
            arrays[f"u_{pid}"] = u_ans
            log(f"{pid}: {prompt[-24:]!r} -> {b.tokens[k]!r} "
                f"[{time.time() - t0:.0f}s]")
    arrays["U_rand"] = U_rand
    return {"records": records, "validity": validity, "arrays": arrays,
            "U_rand": U_rand}


# ---------------------------------------------------------------------------
# planted worlds (through the REAL analyse path)


def _synth(world: str, d: int = 48, L: int = 40, n_per_task: int = 6,
           seed: int = 99) -> tuple[list[dict], np.ndarray]:
    rng = np.random.default_rng(seed)
    ell = np.arange(L + 1)
    amp = 0.3 * (1.15 ** ell)          # geometric charge
    amp_flat = 1.0 + 0.01 * ell        # degenerate: charge ~1.4 < CHARGE_MIN
    records = []
    for task in TASKS:
        for j in range(n_per_task):
            Q, _ = np.linalg.qr(rng.standard_normal((d, 3)))
            e0, e1, e2 = Q[:, 0], Q[:, 1], Q[:, 2]
            noise = 0.01 * rng.standard_normal((L + 1, d))
            if world == "pure_rotation":
                th = np.deg2rad(5.0) * ell
                H = amp[:, None] * (np.cos(th)[:, None] * e0 + np.sin(th)[:, None] * e1)
                H = H + noise
                u_ans = e0.copy()
            elif world == "norm_growth":
                H = amp[:, None] * e0[None, :] + noise
                u_ans = e2.copy()
            elif world == "rotation_off_axis":
                th = np.deg2rad(5.0) * ell
                H = amp[:, None] * (np.cos(th)[:, None] * e0 + np.sin(th)[:, None] * e1)
                H = H + noise
                u_ans = e2.copy()  # answer axis orthogonal to the rotation plane
            elif world == "drift":
                dirs = rng.standard_normal((L, d))
                dirs /= np.linalg.norm(dirs, axis=1, keepdims=True) + EPS
                stepn = np.abs(np.diff(amp))[:, None]
                H = np.vstack([amp[0] * e0, amp[0] * e0 + np.cumsum(dirs * stepn, 0)])
                H = H + noise
                u_ans = e2.copy()
            elif world == "degenerate":
                H = amp_flat[:, None] * e0[None, :] + noise
                u_ans = e2.copy()
            else:
                raise ValueError(world)
            records.append({"pid": f"{task}{j}", "task": task,
                            "H": H.astype(np.float32),
                            "u_ans": u_ans.astype(np.float32)})
    U_rand = rng.standard_normal((N_RAND_TOK, d)).astype(np.float32)
    return records, U_rand


def run_validate() -> int:
    log("--validate: 5 planted worlds through the REAL analyse path")
    expect = {
        "pure_rotation": "CHARGED-ROTATION",
        "norm_growth": "GENERIC-NORM-GROWTH-ONLY",
        "rotation_off_axis": "MIXED",
        "drift": "GENERIC-NORM-GROWTH-ONLY",
        "degenerate": "VOID",
    }
    fails = 0
    for world, want in expect.items():
        recs, U_rand = _synth(world)
        st = analyse(recs, U_rand, seed=7, n_perm_plane=100,
                     min_total=20, min_per_task=4)
        got = st["verdict"]
        ok = got == want
        fails += 0 if ok else 1
        log(f"  {'PASS' if ok else 'FAIL'} {world:18s} want {want:24s} got {got:24s} "
            f"(nvalid {st['n_valid']} ROT {st['median_ROT']:.4f} "
            f"align {st['median_a_align']:.3f} "
            f"N3 {st['N3']['n_beat']}/p{st['N3']['p']:.3f} "
            f"N4 {st['N4']['n_beat']}/p{st['N4']['p']:.3f})")
    log(f"validate: {5 - fails}/5")
    return 1 if fails else 0


# ---------------------------------------------------------------------------


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-14B")
    ap.add_argument("--out", default=None)
    args = ap.parse_args()

    if args.validate:
        return run_validate()

    model_id = args.model_id
    if args.smoke and model_id == "Qwen/Qwen3-14B":
        model_id = "Qwen/Qwen3-8B"  # A2 law (s347): smoke >= 4B, prefer 7B+
    tasks = ({t: items[:4] for t, items in TASKS.items()} if args.smoke else TASKS)
    min_total = 10 if args.smoke else MIN_TOTAL

    cap = capture(model_id, tasks, SEED)
    det_ok = bool(cap["validity"].get("ok", False))
    stats = analyse(cap["records"], cap["U_rand"], seed=SEED,
                    min_total=min_total, det_ok=det_ok)

    tag = "run_smoke" if args.smoke else "run_14b"
    default_out = _ROOT / "results" / "p_depth_carrier_s348" / tag
    out = Path(args.out) if args.out else default_out
    out.mkdir(parents=True, exist_ok=True)
    with (out / "results.jsonl").open("w") as f:
        for r in cap["records"]:
            row = {k: v for k, v in r.items() if k not in ("H", "u_ans")}
            f.write(json.dumps(row, default=_json_native) + "\n")
    np.savez_compressed(out / "trajectories.npz", **cap["arrays"])
    meta = {
        "run_id": f"p_depth_carrier_s348/{tag}",
        "timestamp": datetime.now(UTC).isoformat(),
        "model": model_id, "sampling": {"strategy": "greedy", "n": DECODE_N},
        "git_sha": git_sha(), "seed": SEED, "frozen": "c953705d",
        "n_perm_plane": N_PERM_PLANE, "n_perm": N_PERM,
        "n_prompts": sum(len(v) for v in tasks.values()),
        "driver_validity": cap["validity"],
        "stats": {k: v for k, v in stats.items() if k != "per_pid"},
        "per_pid": stats["per_pid"],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    q = f"/{stats['qualifier']}" if stats["qualifier"] else ""
    log(f"VERDICT {stats['verdict']}{q} | g0 {stats['g0_pass']} g1 {stats['g1_pass']} "
        f"g2 {stats['g2_pass']} g3 {stats['g3_pass']} | nvalid {stats['n_valid']} | "
        f"N1 {stats['N1']['n_beat']} N2 {stats['N2']['n_beat']} "
        f"N3 {stats['N3']['n_beat']} N4 {stats['N4']['n_beat']} | "
        f"med ROT {stats['median_ROT']:.4f} align {stats['median_a_align']:.3f} "
        f"rho {stats['median_rho_deg']:.2f} charge {stats['median_charge']:.1f}")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
