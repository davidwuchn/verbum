#!/usr/bin/env python3
"""§P-TYPE-LOCKIN+PRBS — AC reading of the type register (the frame's must-win).

Pre-reg: mementum/knowledge/explore/types-are-a-modulation-scheme.md
§P-TYPE-LOCKIN+PRBS (FROZEN s326, Michael GO).

§1's core claim: the type judgment is a DEMODULATION EVENT — the register
must track evidence DYNAMICALLY. Every prior read was DC (presence-detector,
NF-GAUGE demotion); this is the AC reading. PRBS upgrade (RE toolbox): one
run = full transfer function + lock-time as measured step response.

Construction (per nonce w, class c): 63 blocks; block = evidence segment +
FIXED probe frame ("The {w}." — constant surface; T read at last w token,
§11's licensing-feed position). Schedule m(t) ∈ {+1,−1} = PRBS-6 (length-63
maximal LFSR), cyclic shift per nonce. MAIN: +1 = coherent membership
paraphrase, −1 = incoherent membership-free filler (idempotency populations,
token-matched). CTRL (lexical control, s321/s322 lesson AT the gate): +1 =
class-word-present NON-membership segments (class word once, w never
predicated). SNR arms: MAIN at s ∈ {0.5, 0.25} (exact fraction of coherent
slots carry coherent segments).

Excitation ⊥ measurement: evidence modulates; readout only at constant-
surface probes — any schedule-content in y(t) must be carried by STATE.

Demodulation (pinned): y(t) = T at probe t, mean-removed per sequence (DC
excluded — DC ≡ the known presence-detector reading). ĥ(τ) = (2/B)
Σ_t y(t)·m(t−τ) cyclic. D = Σ_{τ=0..3} ĥ(τ) (SIGNED: coherent evidence must
RAISE own-class T). Null = 10k random non-trivial cyclic shifts of m
(PRBS-autocorrelation-preserving matched null; shifts overlapping the lag
window excluded).

Gates: LK0 SANE (member axis LOO, PRBS autocorr, finiteness) · LK1
AC-DETECTION (make-or-break) · LK2 JUDGMENT-NOT-LEXICAL (make-or-break #2,
paired) · LK3 TRANSFER-FUNCTION (advisory: tracker flat-H vs integrator
1/f) · LK4 CAPTURE-THRESHOLD (knee-screen: A ∝ s^γ bootstrap; read only if
LK1∧LK2).

Verdicts + a-priori (NOT tuned): NO-TRACK 30 / LEXICAL-TRACK 25 /
CARRIER-TRACKED-PROPORTIONAL 20 / CARRIER-TRACKED-THRESHOLD 15 / VOID 10.

Reuse (λ one_way, no fork): type_icl_tag (signed_T, class_axes, band_layers,
BAND_DEPTH 0.50–0.85 — the landed §11 instrument) · idempotency
(incoherent_stmts) · type_write (CLASSES, REAL_MEMBERS, _member_stmts) ·
holo_cap (NONCE_CANDS) · verbum.jlens (capture_residuals) · verbum.dsp.nulls
(gate, NullDraws, paired_permutation-style sign flips).

License: MIT (lambda provenance).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

import idempotency as idem  # noqa: E402  (frozen s320 harness — populations)
import type_icl_tag as ti  # noqa: E402  (frozen §10 harness — T instrument)
import type_write as tw  # noqa: E402  (frozen §8 harness — constants)
from holo_cap import NONCE_CANDS  # noqa: E402

from verbum.dsp.nulls import (  # noqa: E402
    NullDraws,
    Register,
    gate,
    paired_permutation,
)

# ══════════════════════════════════════════════════════════════════════════
# Frozen constants
# ══════════════════════════════════════════════════════════════════════════
B = 63                              # blocks per sequence (PRBS-6 period)
LAGS = (0, 1, 2, 3)                 # causal lag window read by D
NULL_SHIFTS = [k for k in range(B)
               if k > max(LAGS) and k < B - max(LAGS)]   # non-trivial shifts
N_NULL = 10_000
N_BOOT = 2_000
ALPHA = 0.05
SNR_LEVELS = (1.0, 0.5, 0.25)       # 1.0 ≡ MAIN
ARMS = ("main", "ctrl", "s05", "s025")
APRIORI = {"NO-TRACK": 30, "LEXICAL-TRACK": 25,
           "CARRIER-TRACKED-PROPORTIONAL": 20,
           "CARRIER-TRACKED-THRESHOLD": 15, "VOID": 10}
LOCK_LOSS_FRAC = 0.25               # bootstrap fraction with A(0.25)<=0<A(1)

# CTRL segments: class word EXACTLY once, w present, NO membership
# predication (spatial/coordination frames; skeletons mirror _member_stmts).
CTRL_TEMPLATES = (
    "A {w} is near the {cls}.",
    "The {w} is beside a {cls}.",
    "Every {w} is far from the {cls}.",
    "{w} and the {cls} are both here.",
    "I saw a {w} near the {cls}.",
)


# ══════════════════════════════════════════════════════════════════════════
# PRBS + schedule machinery (pure)
# ══════════════════════════════════════════════════════════════════════════
def prbs6() -> np.ndarray:
    """Maximal-length ±1 sequence, degree 6 (taps x^6 + x^5 + 1), period 63."""
    state = [1] * 6
    out = []
    for _ in range(B):
        bit = state[5] ^ state[4]
        out.append(1.0 if state[5] else -1.0)
        state = [bit, *state[:5]]
    return np.array(out)


def nonce_shift(i: int) -> int:
    """Deterministic distinct cyclic shift per nonce (gcd(11,63)=1)."""
    return (5 + 11 * i) % B


def prbs_autocorr_max(m: np.ndarray) -> float:
    """Max |cyclic autocorrelation| off-peak (ideal m-sequence: 1/B)."""
    return float(max(abs(np.dot(m, np.roll(m, k)) / B) for k in range(1, B)))


def crosscorr(y: np.ndarray, m: np.ndarray) -> np.ndarray:
    """c(τ) = (2/B) Σ_t y_c(t) m(t−τ), cyclic, τ = 0..B−1. y mean-removed."""
    yc = y - y.mean()
    return np.array([(2.0 / B) * float(np.dot(yc, np.roll(m, tau)))
                     for tau in range(B)])


def d_from_corr(c: np.ndarray, shift: int = 0) -> float:
    """D under cyclic shift k of m: Σ_{τ∈LAGS} c((τ + k) mod B)."""
    return float(sum(c[(tau + shift) % B] for tau in LAGS))


# ══════════════════════════════════════════════════════════════════════════
# Sequence construction (pure)
# ══════════════════════════════════════════════════════════════════════════
def coherent_seg(w: str, cls_i: int, j: int) -> str:
    return tw._member_stmts(w, cls_i)[j % 5]


def filler_seg(w: str, j: int) -> str:
    return idem.incoherent_stmts(w)[j % 5]


def ctrl_seg(w: str, cls_i: int, j: int) -> str:
    return CTRL_TEMPLATES[j % 5].format(w=w, cls=tw.CLASSES[cls_i])


def build_sequence(w: str, cls_i: int, m: np.ndarray, mode: str, s: float,
                   rng: np.random.Generator) -> tuple[str, list[int]]:
    """Return (text, char index of last char of w in each probe frame).

    mode 'main': +1 slots coherent (fraction s exactly), −1 filler.
    mode 'ctrl': +1 slots class-word non-membership, −1 filler.
    """
    plus = np.where(m > 0)[0]
    on = set(plus.tolist())
    if mode == "main" and s < 1.0:
        keep = rng.permutation(len(plus))[: round(s * len(plus))]
        on = set(plus[keep].tolist())
    parts: list[str] = []
    probe_ends: list[int] = []
    pos = 0
    for t in range(B):
        if m[t] > 0 and t in on:
            seg = (coherent_seg(w, cls_i, t) if mode == "main"
                   else ctrl_seg(w, cls_i, t))
        else:
            seg = filler_seg(w, t)
        piece = seg + " The " + w
        parts.append(piece + ". ")
        pos += len(piece)
        probe_ends.append(pos - 1)          # last char of w
        pos += 2                            # ". "
    return "".join(parts).rstrip(), probe_ends


def probe_token_positions(tok, text: str, probe_ends: list[int]) -> list[int]:
    """Map char index of last w char → token index (offset mapping)."""
    enc = tok(text, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    out = []
    for c in probe_ends:
        idx = max(i for i, (a, b) in enumerate(offsets) if a <= c < b and b > a)
        out.append(idx)
    return out


# ══════════════════════════════════════════════════════════════════════════
# Gates (shared by --validate and the model run)
# ══════════════════════════════════════════════════════════════════════════
def gate_lk0(bundle: dict) -> dict:
    y_ok = all(np.isfinite(bundle["y"][a]).all() for a in ARMS)
    loo = float(np.mean(bundle["member_loo"]))
    ac = float(bundle["prbs_autocorr_max"])
    ok = y_ok and loo > 0 and ac < 0.1
    return {"gate": "LK0", "pass": bool(ok), "member_loo_mean": loo,
            "prbs_autocorr_max": ac, "y_finite": bool(y_ok)}


def _arm_D(bundle: dict, arm: str) -> np.ndarray:
    """Per-nonce D for an arm (uses each nonce's own schedule)."""
    y, m = bundle["y"][arm], bundle["m"]
    return np.array([d_from_corr(crosscorr(y[i], m[i]))
                     for i in range(len(y))])


def _corr_matrix(bundle: dict, arm: str) -> np.ndarray:
    y, m = bundle["y"][arm], bundle["m"]
    return np.stack([crosscorr(y[i], m[i]) for i in range(len(y))])


def gate_lk1(bundle: dict, rng: np.random.Generator,
             n_null: int = N_NULL) -> dict:
    cmat = _corr_matrix(bundle, "main")                    # (n, B)
    n = cmat.shape[0]
    dwin = np.stack([[d_from_corr(cmat[i], k) for k in range(B)]
                     for i in range(n)])                   # (n, B)
    obs = float(dwin[:, 0].mean())
    ks = rng.choice(NULL_SHIFTS, size=(n_null, n))
    draws = dwin[np.arange(n)[None, :], ks].mean(axis=1)
    null = NullDraws("cyclic_shift", draws,
                     {"n_iter": n_null, "allowed_shifts": len(NULL_SHIFTS)})
    g = gate(obs, null, "greater", ALPHA, name="LK1",
             claim_register=Register.value, probe_register=Register.value)
    return {"gate": "LK1", "pass": g.verdict, "D_mean": obs, "p": g.p,
            "null_mean": g.null_mean, "null_std": g.null_std}


def gate_lk2(bundle: dict, rng: np.random.Generator,
             n_null: int = N_NULL) -> dict:
    d_main, d_ctrl = _arm_D(bundle, "main"), _arm_D(bundle, "ctrl")
    obs = float(np.mean(d_main - d_ctrl))
    null = paired_permutation(d_main, d_ctrl, rng, n_iter=n_null)
    g = gate(obs, null, "greater", ALPHA, name="LK2",
             claim_register=Register.value, probe_register=Register.value)
    return {"gate": "LK2", "pass": g.verdict, "D_main": float(d_main.mean()),
            "D_ctrl": float(d_ctrl.mean()), "diff": obs, "p": g.p}


def gate_lk3(bundle: dict) -> dict:
    """Advisory: impulse response, spectrum, lock-time. Never gates."""
    c = _corr_matrix(bundle, "main").mean(axis=0)          # (B,)
    hhat = [float(c[t]) for t in range(8)]
    step = np.cumsum(c[:8])
    peak = float(step.max()) if step.max() > 0 else 0.0
    lock = next((t for t in range(8) if peak > 0
                 and step[t] >= 0.63 * peak), None)
    spec = np.abs(np.fft.rfft(c))
    return {"gate": "LK3", "advisory": True, "hhat_0_7": hhat,
            "lock_time_blocks": lock,
            "spectrum_low_over_high": float(
                spec[1:6].mean() / max(spec[6:].mean(), 1e-12))}


def gate_lk4(bundle: dict, rng: np.random.Generator,
             n_boot: int = N_BOOT) -> dict:
    """Knee-screen: A(s) ∝ s^γ bootstrap over nonces. Read iff LK1∧LK2."""
    d_by_s = {1.0: _arm_D(bundle, "main"), 0.5: _arm_D(bundle, "s05"),
              0.25: _arm_D(bundle, "s025")}
    n = len(d_by_s[1.0])
    a_obs = {s: float(d.mean()) for s, d in d_by_s.items()}
    logs = np.log(np.array(SNR_LEVELS))
    gammas, lock_loss = [], 0
    for _ in range(n_boot):
        idx = rng.integers(0, n, n)
        a = np.array([d_by_s[s][idx].mean() for s in SNR_LEVELS])
        if a[0] > 0 and a[2] <= 0:
            lock_loss += 1
        if (a > 0).all():
            gammas.append(np.polyfit(logs, np.log(a), 1)[0])
    frac_ll = lock_loss / n_boot
    out = {"gate": "LK4", "A": {str(s): a_obs[s] for s in SNR_LEVELS},
           "lock_loss_frac": frac_ll, "n_gamma_draws": len(gammas)}
    if frac_ll > LOCK_LOSS_FRAC:
        out.update({"category": "THRESHOLD-FLAVORED", "form": "lock-loss"})
        return out
    if len(gammas) < n_boot // 2:
        out.update({"category": "UNREADABLE"})
        return out
    lo, hi = np.percentile(gammas, [2.5, 97.5])
    med = float(np.median(gammas))
    cat = ("THRESHOLD-FLAVORED" if lo > 1 else
           "COMPRESSIVE" if hi < 1 else "PROPORTIONAL")
    out.update({"category": cat, "gamma_median": med,
                "gamma_ci": [float(lo), float(hi)]})
    return out


def verdict(lk0: dict, lk1: dict, lk2: dict, lk4: dict | None) -> str:
    if not lk0["pass"]:
        return "VOID"
    if not lk1["pass"]:
        return "NO-TRACK"
    if not lk2["pass"]:
        return "LEXICAL-TRACK"
    if lk4 is not None and lk4.get("category") == "THRESHOLD-FLAVORED":
        return "CARRIER-TRACKED-THRESHOLD"
    return "CARRIER-TRACKED-PROPORTIONAL"


def run_gates(bundle: dict, rng: np.random.Generator,
              n_null: int = N_NULL, n_boot: int = N_BOOT):
    lk0 = gate_lk0(bundle)
    lk1 = gate_lk1(bundle, rng, n_null)
    lk2 = gate_lk2(bundle, rng, n_null)
    lk3 = gate_lk3(bundle)
    lk4 = (gate_lk4(bundle, rng, n_boot)
           if (lk0["pass"] and lk1["pass"] and lk2["pass"]) else None)
    v = verdict(lk0, lk1, lk2, lk4)
    gates = [lk0, lk1, lk2, lk3] + ([lk4] if lk4 else [])
    return gates, v


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted worlds (synthetic y traces through the same gates)
# ══════════════════════════════════════════════════════════════════════════
_KERNEL = np.array([0.5, 0.3, 0.15, 0.05])


def _filt(m: np.ndarray) -> np.ndarray:
    return sum(k * np.roll(m, tau) for tau, k in enumerate(_KERNEL))


def _mk_world(kind: str, rng: np.random.Generator, n: int = 20) -> dict:
    base = prbs6()
    m = np.stack([np.roll(base, nonce_shift(i)) for i in range(n)])
    noise = lambda: rng.normal(0, 0.3, (n, B))  # noqa: E731
    f = np.stack([_filt(m[i]) for i in range(n)])
    amp = {"TRACKER": (1.0, 0.5, 0.25), "THRESH": (1.0, 0.1, 0.0),
           "LEXICAL": (1.0, 0.5, 0.25), "NOTRACK": (0.0, 0.0, 0.0),
           "VOID": (1.0, 0.5, 0.25)}[kind]
    y = {"main": amp[0] * f + noise(),
         "s05": amp[1] * f + noise(),
         "s025": amp[2] * f + noise(),
         "ctrl": (f + noise()) if kind == "LEXICAL" else noise()}
    return {"y": y, "m": m,
            "member_loo": np.array([-1.0 if kind == "VOID" else 1.0] * 8),
            "prbs_autocorr_max": prbs_autocorr_max(base)}


def validate() -> bool:
    expected = {"TRACKER": "CARRIER-TRACKED-PROPORTIONAL",
                "THRESH": "CARRIER-TRACKED-THRESHOLD",
                "LEXICAL": "LEXICAL-TRACK", "NOTRACK": "NO-TRACK",
                "VOID": "VOID"}
    ok_all = True
    for kind, want in expected.items():
        rng = np.random.default_rng(63)
        gates, v = run_gates(_mk_world(kind, rng), rng,
                             n_null=2000, n_boot=500)
        ok = v == want
        ok_all &= ok
        lk1 = gates[1]
        print(f"  world={kind:<8} verdict={v:<30} want={want:<30} "
              f"D={lk1['D_mean']:+.3f} {'PASS' if ok else 'FAIL'}")
    print(f"--validate: {'ALL PASS' if ok_all else 'FAIL'}")
    return ok_all


# ══════════════════════════════════════════════════════════════════════════
# Model run
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import torch

    from verbum import jlens

    dev = (args.device if (args.device != "mps"
                           or torch.backends.mps.is_available()) else "cpu")
    rng = np.random.default_rng(args.seed)
    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model_id)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    for p in model.parameters():
        p.requires_grad_(False)
    nl = jlens.n_layers(model)
    tband = ti.band_layers(nl)
    out_dir = Path(args.out)
    out_dir.mkdir(parents=True, exist_ok=True)
    print(f"[lk] {args.model_id} dev={dev} n_layers={nl} "
          f"T-band=L{tband[0]}..L{tband[-1]} B={B} arms={ARMS}", flush=True)

    def capture_band_at(text: str, positions: list[int]) -> np.ndarray:
        """(n_pos, L_band, d) residuals at given token positions."""
        resid, _ids = jlens.capture_residuals(model, tok, text)
        return np.stack([np.stack([resid[li][p].numpy() for li in tband])
                         for p in positions])

    # ── nonce selection (type_icl_tag pattern) ──
    nonces, labels = [], []
    for i, w in enumerate(NONCE_CANDS):
        n_the = tok("The", add_special_tokens=False).input_ids
        n_thew = tok(f"The {w}", add_special_tokens=False).input_ids
        if len(n_thew) - len(n_the) >= 1:
            nonces.append(w)
            labels.append(i % 2)
    if args.n_nonce:
        a = [j for j, x in enumerate(labels) if x == 0][:args.n_nonce // 2]
        v = [j for j, x in enumerate(labels) if x == 1][:args.n_nonce // 2]
        keep = sorted(a + v)
        nonces = [nonces[j] for j in keep]
        labels = [labels[j] for j in keep]
    labels = np.array(labels)
    print(f"[lk] n_nonce={len(nonces)}", flush=True)

    # ── real-member class axes + LOO sanity (LK0 input) ──
    members = list(tw.REAL_MEMBERS[0]) + list(tw.REAL_MEMBERS[1])
    mlabels = np.array([0] * len(tw.REAL_MEMBERS[0])
                       + [1] * len(tw.REAL_MEMBERS[1]))
    h_members = np.stack([
        capture_band_at(f"The {mem}", [len(tok(f"The {mem}").input_ids) - 1])[0]
        for mem in members])
    axes = ti.class_axes(h_members, mlabels)
    loo = []
    for j in range(len(members)):
        keep = np.arange(len(members)) != j
        ax_j = ti.class_axes(h_members[keep], mlabels[keep])
        loo.append(float(ti.signed_T(h_members[j:j + 1], ax_j,
                                     mlabels[j:j + 1])[0]))
    print(f"[lk] member LOO mean={np.mean(loo):+.3f}", flush=True)

    # ── sequences: capture y per nonce per arm ──
    base = prbs6()
    m_all = np.stack([np.roll(base, nonce_shift(i))
                      for i in range(len(nonces))])
    y = {arm: np.zeros((len(nonces), B)) for arm in ARMS}
    ylayers = {arm: np.zeros((len(nonces), len(tband), B)) for arm in ARMS}
    arm_spec = [("main", "main", 1.0), ("ctrl", "ctrl", 1.0),
                ("s05", "main", 0.5), ("s025", "main", 0.25)]
    t0 = time.time()
    for i, (w, lb) in enumerate(zip(nonces, labels, strict=True)):
        srng = np.random.default_rng(1000 + i)   # per-nonce dilution draws
        for arm, mode, s in arm_spec:
            text, ends = build_sequence(w, int(lb), m_all[i], mode, s, srng)
            positions = probe_token_positions(tok, text, ends)
            h = capture_band_at(text, positions)          # (B, L, d)
            proj = np.einsum("bld,ld->bl", h, axes)       # (B, L)
            sign = 1.0 if int(lb) == 0 else -1.0
            y[arm][i] = proj.mean(axis=1) * sign
            ylayers[arm][i] = (proj * sign).T
        if i % 4 == 0:
            print(f"[lk] nonce {i + 1}/{len(nonces)} "
                  f"({time.time() - t0:.0f}s)", flush=True)

    bundle = {"y": y, "m": m_all, "member_loo": np.array(loo),
              "prbs_autocorr_max": prbs_autocorr_max(base)}
    gates, v = run_gates(bundle, rng, n_null=args.n_null)

    np.savez_compressed(
        out_dir / "traces.npz", m=m_all, member_loo=np.array(loo),
        labels=labels, nonces=np.array(nonces),
        **{f"y_{a}": y[a] for a in ARMS},
        **{f"ylayers_{a}": ylayers[a] for a in ARMS})
    rec = {"probe": "§P-TYPE-LOCKIN+PRBS (FROZEN s326)",
           "model_id": args.model_id, "n_nonce": len(nonces),
           "band": [int(tband[0]), int(tband[-1])], "B": B,
           "lags": list(LAGS), "n_null": args.n_null,
           "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
           "elapsed_s": round(time.time() - t0, 1)}
    with (out_dir / "results.jsonl").open("w") as fh:
        fh.write(json.dumps(rec) + "\n")
        for gd in gates:
            fh.write(json.dumps(gd) + "\n")
        fh.write(json.dumps({"verdict": v, "a_priori": APRIORI}) + "\n")
    for gd in gates:
        print(json.dumps(gd))
    print(f"VERDICT: {v}")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16",
                    choices=["float32", "bfloat16"])
    ap.add_argument("--n-nonce", type=int, default=0)
    ap.add_argument("--n-null", type=int, default=N_NULL)
    ap.add_argument("--seed", type=int, default=326)
    ap.add_argument("--out", default="results/type-lockin/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return 0 if validate() else 1
    return run_model(args)


if __name__ == "__main__":
    sys.exit(main())
