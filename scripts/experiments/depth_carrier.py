#!/usr/bin/env python3
"""§P-DEPTH-CARRIER — is answer assembly a late-layer rotation? (s348, re-scoped).

FROZEN DESIGN: mementum/knowledge/explore/answer-assembly-is-a-charged-rotation.md
(re-frozen s348 BEFORE data, Michael GO).

The s346 REPL pilot saw the DECIDING state's DEPTH trajectory (residual stream
of the state that emits the answer token, layer 0 -> L) as a coherent spiral.
The s348 instrument-first look (resident 14B driver) re-scoped it: the rotation
is NOT a uniform per-layer precession -- it is LATE-CONCENTRATED (flat phase
early, then a ~full-turn sweep in the last ~10 layers as amplitude explodes =
the answer-assembly / discharge region). The rank-2 residual metric was
order-blind and too brittle; the clean discriminator is the SWEPT ANGLE in the
late band vs a NORM-MATCHED null.

Object: per prompt, H = driver.bounce(prompt).hidden[k] in R^{(L+1) x d}, k =
the frame emitting the first answer content token. Battery = 5 task types.

Late band: layers from first l>=4 with raw_norm > 0.30*max(raw_norm) to the
last layer (>= 5 layers). Plane = top-2 SVD of the DC-centered band. swept =
sum|dtheta|, wind = |sum dtheta| (monotone rotation => swept ~ wind), a_align =
plane-vs-answer-token unembedding cosine.

Nulls (band fixed at real [lo,hi], content randomized): N3 NORM-MATCHED (same
per-layer step NORMS, isotropic-random DIRECTIONS -- the make-or-break); N1
shuffled-layer (confirmatory); N2 increment-shuffle (advisory, order-blind for
a low-dim subspace); N4 random-token answer-axis.

FROZEN verdict tree + a-priori mass:
  LATE-ANSWER-ROTATION  45  swept beats N3 AND plane answer-aligned (G1 & G2)
  GENERIC-LATE-SWEEP    25  swept beats N3 but NOT answer-aligned (G1 & !G2)
  NO-EXCESS-SWEEP       20  swept <= norm-matched (G1 fail; pilot spiral was a
                            norm-growth / PCA-arc artifact)
  VOID                  10  G0 fail (no determinism / no charge / short band)

Discipline: a positive verdict is a DESCRIPTIVE geometric fact -- it does NOT
license homeostat / persistent-mode / modulation vocabulary (frame_ledger 0-3,
s326). Capture-euphoria guard: the s346/s348 REPL looks FEED this design, they
are NOT evidence in this ledger.

`--validate` drives 5 planted worlds through the REAL analyse path.

Bounds: n=1 model (Qwen3-14B), greedy, last-token deciding state, today's
battery. One-directional (NO-EXCESS-SWEEP / GENERIC are the informative kills).

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

# ---------------------------------------------------------------------------
# FROZEN CONSTANTS (s348 re-freeze)

SEED = 348
LATE_FRAC = 0.30          # late band lower edge = 0.30 * max(raw_norm)
LATE_MIN = 5              # minimum late-band layers (else pid invalid)
BAND_LO_MIN = 4           # never start the band before layer 4 (skip warmup)
CHARGE_MIN = 4.0          # raw-norm growth over the trajectory (validity)
N_PERM_PLANE = 200        # trajectory nulls (band content randomized each draw)
N_PERM = 2000             # answer-axis / label nulls
N_RAND_TOK = 512          # random-token unembedding rows for N4
MIN_PER_TASK = 4
MIN_TOTAL = 20
MONO_THRESH = 0.8         # wind/swept qualifier (one-directional)
ALPHA = 0.05
DECODE_N = 8              # tokens to decode (answer token is early)
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
# geometry (the analyse core -- planted worlds drive this same code)


def late_band(H: np.ndarray) -> tuple[int, int]:
    """[lo, hi] = the answer-assembly region: raw_norm > LATE_FRAC * max."""
    rn = np.linalg.norm(H, axis=1)
    above = np.where(rn > LATE_FRAC * rn.max())[0]
    lo = int(above[0]) if above.size else 0
    lo = max(lo, BAND_LO_MIN)
    return lo, H.shape[0] - 1


def band_swept(seg: np.ndarray) -> tuple[np.ndarray, float, float, float]:
    """Top-2 SVD plane of the DC-centered segment; swept + net winding + planarity."""
    segc = seg - seg.mean(0)
    try:
        _, _, Vt = np.linalg.svd(segc, full_matrices=False)
    except np.linalg.LinAlgError:
        return np.zeros((2, seg.shape[1])), 0.0, 0.0, 0.0
    if Vt.shape[0] < 2:
        return np.zeros((2, seg.shape[1])), 0.0, 0.0, 0.0
    B = Vt[:2]
    c = segc @ B.T
    theta = np.arctan2(c[:, 1], c[:, 0])
    dth = (np.diff(theta) + np.pi) % (2 * np.pi) - np.pi
    swept = float(np.sum(np.abs(dth)))
    wind = float(abs(np.sum(dth)))
    sx, sy = float(np.std(c[:, 0])), float(np.std(c[:, 1]))
    planar = float(min(sx, sy) / (max(sx, sy) + EPS))
    return B, swept, wind, planar


def late_metrics(H: np.ndarray) -> dict:
    Hf = H.astype(np.float64)
    rn = np.linalg.norm(Hf, axis=1)
    lo, hi = late_band(Hf)
    band_len = hi - lo + 1
    charge = float(rn[hi] / (rn[BAND_LO_MIN] + EPS))  # whole-trajectory growth
    if band_len < LATE_MIN or charge < CHARGE_MIN or rn.max() < EPS:
        return {"valid": False, "reason": "no-charge-or-short", "lo": lo, "hi": hi,
                "swept": 0.0, "wind": 0.0, "planar": 0.0, "charge": charge,
                "band_len": band_len, "B": None}
    B, swept, wind, planar = band_swept(Hf[lo:hi + 1])
    return {"valid": True, "reason": "ok", "lo": lo, "hi": hi, "swept": swept,
            "wind": wind, "planar": planar, "charge": charge,
            "band_len": band_len, "B": B}


def align(B: np.ndarray, u: np.ndarray) -> float:
    nu = np.linalg.norm(u)
    if nu < EPS or B is None:
        return 0.0
    return float(np.max(np.abs(B @ u) / (np.linalg.norm(B, axis=1) * nu + EPS)))


def _swept_null(H: np.ndarray, kind: str, lo: int, hi: int, n_perm: int,
                rng) -> np.ndarray:
    """swept distribution with the band fixed at [lo,hi], content randomized."""
    H = H.astype(np.float64)
    incs = np.diff(H, axis=0)
    norms = np.linalg.norm(incs, axis=1)
    out = np.zeros(n_perm)
    for k in range(n_perm):
        if kind == "norm_matched":
            dirs = rng.standard_normal(incs.shape)
            dirs /= np.linalg.norm(dirs, axis=1, keepdims=True) + EPS
            Hs = np.vstack([H[0], H[0] + np.cumsum(dirs * norms[:, None], 0)])
        elif kind == "shuffled_layer":
            Hs = H[rng.permutation(H.shape[0])]
        elif kind == "increment_shuffle":
            perm = incs[rng.permutation(len(incs))]
            Hs = np.vstack([H[0], H[0] + np.cumsum(perm, 0)])
        else:
            raise ValueError(kind)
        _, sw, _, _ = band_swept(Hs[lo:hi + 1])
        out[k] = sw
    return out


def analyse(records: list[dict], U_rand: np.ndarray, seed: int = SEED,
            n_perm_plane: int = N_PERM_PLANE, min_total: int = MIN_TOTAL,
            min_per_task: int = MIN_PER_TASK, det_ok: bool = True) -> dict:
    rng = np.random.default_rng(seed)
    per: list[dict] = []
    for r in records:
        H = np.asarray(r["H"], dtype=np.float64)
        m = late_metrics(H)
        u = np.asarray(r["u_ans"], dtype=np.float64)
        a_align = align(m["B"], u) if m["valid"] else 0.0
        rec = {"pid": r["pid"], "task": r["task"], "a_align": a_align,
               **{k: v for k, v in m.items() if k != "B"}}
        if m["valid"]:
            lo, hi = m["lo"], m["hi"]
            for kind, key in (("norm_matched", "N3"), ("shuffled_layer", "N1"),
                              ("increment_shuffle", "N2")):
                null = _swept_null(H, kind, lo, hi, n_perm_plane, rng)
                rec[f"{key}_q95"] = float(np.quantile(null, 0.95))
                rec[f"beats_{key}"] = bool(m["swept"] > rec[f"{key}_q95"])
            bn = np.linalg.norm(m["B"], axis=1)[None]
            nu = np.linalg.norm(U_rand, axis=1)
            cos = np.abs(U_rand @ m["B"].T) / (nu[:, None] * bn + EPS)
            rec["N4_q95"] = float(np.quantile(cos.max(axis=1), 0.95))
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

    n3 = _gate("beats_N3")   # make-or-break
    n1 = _gate("beats_N1")   # confirmatory
    n2 = _gate("beats_N2")   # advisory (order-blind)
    n4 = _gate("beats_N4")
    g1_pass = g0_pass and n3[2]
    g2_pass = g1_pass and n4[2]

    if not g0_pass:
        verdict = "VOID"
    elif not g1_pass:
        verdict = "NO-EXCESS-SWEEP"
    elif not g2_pass:
        verdict = "GENERIC-LATE-SWEEP"
    else:
        verdict = "LATE-ANSWER-ROTATION"

    def _med(key: str) -> float:
        return float(np.median([p[key] for p in valid])) if valid else float("nan")

    mono = float(np.median([p["wind"] / (p["swept"] + EPS) for p in valid])) \
        if valid else float("nan")
    qualifier = None
    if verdict == "LATE-ANSWER-ROTATION":
        qualifier = "monotone" if mono >= MONO_THRESH else "nonmonotone"
    return {
        "verdict": verdict, "qualifier": qualifier, "g0_pass": g0_pass,
        "g1_pass": g1_pass, "g2_pass": g2_pass, "det_ok": bool(det_ok),
        "n_valid": n_valid, "n_records": len(per), "per_task_valid": per_task_counts,
        "tasks_ok": tasks_ok,
        "N3": {"n_beat": n3[0], "p": n3[1]}, "N1": {"n_beat": n1[0], "p": n1[1]},
        "N2": {"n_beat": n2[0], "p": n2[1]}, "N4": {"n_beat": n4[0], "p": n4[1]},
        "median_swept": _med("swept"), "median_wind": _med("wind"),
        "median_a_align": _med("a_align"), "median_charge": _med("charge"),
        "median_planar": _med("planar"), "wind_over_swept": mono,
        "per_pid": per,
    }


# ---------------------------------------------------------------------------
# capture (driver -- depth trajectory of the deciding state)


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
    amp = 0.3 * (1.15 ** ell)          # geometric charge; max ~80, late band ~L32+
    amp_flat = 1.0 + 0.01 * ell        # degenerate: charge ~1.4 < CHARGE_MIN
    lo_rot = 27                        # late sweep begins here
    records = []
    for task in TASKS:
        for j in range(n_per_task):
            Q, _ = np.linalg.qr(rng.standard_normal((d, 3)))
            e0, e1, e2 = Q[:, 0], Q[:, 1], Q[:, 2]
            noise = 0.01 * rng.standard_normal((L + 1, d))
            if world in ("late_answer_rotation", "late_generic_sweep"):
                th = np.where(ell >= lo_rot, (ell - lo_rot) * 0.74, 0.0)
                H = amp[:, None] * (np.cos(th)[:, None] * e0
                                    + np.sin(th)[:, None] * e1) + noise
                u_ans = e0 if world == "late_answer_rotation" else e2
            elif world == "random_walk":
                dirs = rng.standard_normal((L, d))
                dirs /= np.linalg.norm(dirs, axis=1, keepdims=True) + EPS
                stepn = np.abs(np.diff(amp))[:, None]
                H = np.vstack([amp[0] * e0, amp[0] * e0 + np.cumsum(dirs * stepn, 0)])
                H = H + noise
                u_ans = e2
            elif world == "ray":
                H = amp[:, None] * e0[None, :] + noise
                u_ans = e2
            elif world == "degenerate":
                H = amp_flat[:, None] * e0[None, :] + noise
                u_ans = e2
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
        "late_answer_rotation": "LATE-ANSWER-ROTATION",
        "late_generic_sweep": "GENERIC-LATE-SWEEP",
        "random_walk": "NO-EXCESS-SWEEP",
        "ray": "NO-EXCESS-SWEEP",
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
        log(f"  {'PASS' if ok else 'FAIL'} {world:22s} want {want:20s} got {got:20s} "
            f"(nvalid {st['n_valid']} swept {st['median_swept']:.2f} "
            f"align {st['median_a_align']:.3f} N3 {st['N3']['n_beat']} "
            f"N4 {st['N4']['n_beat']})")
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
        "git_sha": git_sha(), "seed": SEED, "frozen": "re-freeze-s348",
        "n_perm_plane": N_PERM_PLANE, "n_perm": N_PERM,
        "n_prompts": sum(len(v) for v in tasks.values()),
        "driver_validity": cap["validity"],
        "stats": {k: v for k, v in stats.items() if k != "per_pid"},
        "per_pid": stats["per_pid"],
    }
    (out / "meta.json").write_text(json.dumps(meta, indent=2, default=_json_native))
    q = f"/{stats['qualifier']}" if stats["qualifier"] else ""
    log(f"VERDICT {stats['verdict']}{q} | g0 {stats['g0_pass']} g1 {stats['g1_pass']} "
        f"g2 {stats['g2_pass']} | nvalid {stats['n_valid']} | "
        f"N3 {stats['N3']['n_beat']} N1 {stats['N1']['n_beat']} "
        f"N2 {stats['N2']['n_beat']} N4 {stats['N4']['n_beat']} | "
        f"med swept {stats['median_swept']:.2f} align {stats['median_a_align']:.3f} "
        f"charge {stats['median_charge']:.1f} mono {stats['wind_over_swept']:.2f}")
    log(f"wrote {out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
