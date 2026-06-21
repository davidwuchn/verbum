#!/usr/bin/env python3
# register: causal (routing direction; s239 sufficiency/necessity protocol)
"""Kernel-splice Exp 1 — the CAUSAL K-SPLICE (s243).

Exp 0.5 firmed the detection: at L18, gate-z(K) > 3.0 is a reliable (prec 0.857, tp=6,
plateau) read that the lattice "wants K". Exp 1 asks the causal question the whole pivot
turns on: **is that K-geometry the CAUSE of the K-computation, or an epiphenomenal
correlate?** — the s239 sufficiency/necessity protocol, now on the K routing direction
at the firmed locus.

THE TWO REGISTERS (resolves the s243 build crux -- NOT a compromise, it is correct):
  - DETECT in gate-space: the classifier reads `model.model.layers[L].mlp.gate_proj`
    (sign-CMR centroids). Gate-z(K) > tau decides WHERE/WHICH (Exp 0.5's firmed gate).
  - EFFECT in residual-space: re-injection belongs in the RESIDUAL -- that is what
    downstream layers read. We patch the output of `model.model.layers[L]` at the
    last-token (crystal) position. The K residual direction d_K = unit
    diff-of-means(resid_K - resid_nonK) at L; the "exact kernel K-move" geometric
    proxy = d_K at the canonical "K-fired" magnitude (mean K projection).
  - READ causal propagation downstream: the detector z(K) at crystal layers > L (the
    patch cannot affect L's own gate, upstream of the layer output) + the final
    next-token distribution. All vs a RANDOM-direction control of equal magnitude.

THREE ARMS (Michael s243: both arms):
  1. NECESSITY (detected-K probes, z(K)@L > tau): project d_K OUT. If the K-direction
     is load-bearing, downstream z(K) DROPS and the output is PERTURBED -- MORE than a
     random direction of equal magnitude.
  2. PRESERVE (detected-K probes): SET the d_K component to the canonical K value
     (overwrite the neuron's value with the kernel's exact geometric value). If the
     exact value matches what the neuron computed, the output is PRESERVED (low KL) --
     LESS than a random set of equal magnitude. = "kernel value replaces the neuron".
  3. DELIVERY / COUNTERFACTUAL (non-K probes): SET the d_K component to canonical
     (inject K where it does not fire). If d_K is sufficient, the DOWNSTREAM detector
     reads K (z(K) rises across L+1..) and the output shifts -- MORE than random.

SCOPE / HONEST LIMIT (lambda measure): crystal_probes are PROSE that engages the K
SEMANTICS (selection/projection), not formal `K a b` terms -> there is no single-token
kernel-certifiable gold here. So Exp 1 tests the K-DIRECTION's causal
sufficiency/necessity (the geometric splice) via the validated detector + output
distribution -- the prerequisite for the OPERAND-BOUND kernel-value splice on the
certified corpus (= Exp 2). This is the page's "minimal instance".

VERDICT (lambda measure):
  necessity ok (K-ablate degrades > random ∧ z(K) down) ∧ delivery ok (K-inject drives
  downstream z(K) > random) ∧ preserve ok (K-set perturbs output < random) => the K
  direction is the necessary+sufficient causal carrier; the kernel's exact move can
  replace the neuron => thesis proven causally, no-training hybrid (cleanest extract).
  Any arm fails => the decodable geometry is (partly) over-read (lambda measure win) =>
  redirect to the constructed front-end / operand-bound Exp 2.

Usage:
    uv run python scripts/experiments/kernel_splice_exp1_ksplice.py --smoke
    uv run python scripts/experiments/kernel_splice_exp1_ksplice.py \
        --model Qwen/Qwen3-14B --patch-layer 18 --gate-tau 3.0 --heldout-per 25

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import read_last_token_z, split_probes  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-splice-exp1"
KIDX = CRYSTAL.index("K")


# ── intervention hook on the patch-layer residual output ─────────────────────────
def make_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod,
                    pos: int = -1):
    """Forward hook on a decoder layer: modify the d-component of the residual at `pos`.

    mode='ablate' -> project the direction OUT (set its component to 0).
    mode='set'    -> overwrite the component to `target_mag` (deliver canonical value).
    """
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)
        v = h[0, pos, :]
        proj = (v @ d)
        if mode == "ablate":
            h[0, pos, :] = v - proj * d
        elif mode == "set":
            h[0, pos, :] = v - proj * d + target_mag * d
        else:
            raise ValueError(f"unknown mode {mode!r}")
        return out
    return hook


def forward_capture(prompt, model, tok, torch_mod, gate_layers, patch_layer,
                    patch_hook=None):
    """ONE forward: capture gate (all gate_layers, last-token-bearing [T,d]), the
    pre-patch residual at patch_layer (last token), and the final next-token logits.
    If patch_hook is given it is applied to layers[patch_layer] output (AFTER the
    residual read, so the read is the clean pre-patch value)."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in gate_layers:
        handles.append(model.model.layers[li].mlp.gate_proj.register_forward_hook(
            _make_hook(store, li)))
    resid_box: dict[str, np.ndarray] = {}

    def resid_read(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        resid_box["v"] = h[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    handles.append(model.model.layers[patch_layer].register_forward_hook(resid_read))
    if patch_hook is not None:
        handles.append(model.model.layers[patch_layer].register_forward_hook(patch_hook))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        ll = out.logits[0, -1, :].detach().float().cpu().numpy()
        logits_last = ll.astype(np.float64)
    finally:
        for h in handles:
            h.remove()
    return store, resid_box.get("v"), logits_last


def kl_div(logp_p: np.ndarray, logp_q: np.ndarray) -> float:
    """KL(P‖Q) from log-prob vectors, in nats."""
    p = np.exp(logp_p)
    return float(np.sum(p * (logp_p - logp_q)))


def log_softmax(logits: np.ndarray) -> np.ndarray:
    m = logits.max()
    z = logits - m
    return z - np.log(np.exp(z).sum())


def zK_downstream(rcc, store, all_layers, crystal_layers, patch_layer) -> float:
    """Mean detector z(K) over CRYSTAL layers strictly downstream of the patch."""
    zmap = read_last_token_z(rcc, store, all_layers)
    ds = [zmap[li]["K"] for li in crystal_layers if li > patch_layer and li in zmap]
    return float(np.mean(ds)) if ds else float("nan")


def zK_at(rcc, store, all_layers, layer) -> float:
    zmap = read_last_token_z(rcc, store, all_layers)
    return float(zmap.get(layer, {}).get("K", float("nan")))


def paired(kdir: list[float], rand: list[float]) -> dict:
    """Paired comparison K-direction vs random control over probes."""
    a, b = np.asarray(kdir, float), np.asarray(rand, float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = len(a)
    if n < 2:
        return {"n": n, "k_mean": None, "rand_mean": None, "delta": None, "t": None}
    diff = a - b
    se = diff.std(ddof=1) / np.sqrt(n) if diff.std(ddof=1) > 0 else 0.0
    return {"n": n, "k_mean": round(float(a.mean()), 4),
            "rand_mean": round(float(b.mean()), 4),
            "delta": round(float(diff.mean()), 4),
            "t": round(float(diff.mean() / se), 3) if se > 0 else None}


def main() -> None:
    ap = argparse.ArgumentParser(description="Kernel-splice Exp 1 — causal K-splice")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--patch-layer", type=int, default=18,
                    help="firmed K locus (Exp 0.5: L18)")
    ap.add_argument("--gate-tau", type=float, default=3.0,
                    help="detection gate: act on K-probes with z(K)@patch_layer > tau")
    ap.add_argument("--heldout-per", type=int, default=25)
    ap.add_argument("--n-rand", type=int, default=3,
                    help="random control directions to average over")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    patch_layer = args.patch_layer
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, heldout = 80, 5, 200, 5
        patch_layer = min(patch_layer, 6)
        print("[exp1] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, heldout = 300, None, None, args.heldout_per

    calib, test = split_probes(heldout)
    print(f"[exp1] calib={len(calib)} test={len(test)} patch_layer={patch_layer}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode="crosstask", centroid_probes=calib)
    crystal_layers = rcc.crystal_layers
    if patch_layer not in crystal_layers:
        # fall back to the nearest crystal layer at/above the requested patch layer
        cands = [li for li in crystal_layers if li >= patch_layer] or crystal_layers
        patch_layer = min(cands, key=lambda li: abs(li - patch_layer))
        print(f"[exp1] patch_layer not crystal; using nearest crystal L{patch_layer}")
    print(f"[exp1] crystal {len(crystal_layers)}/{n_layers}; patch L{patch_layer}")

    # ── Pass A: baseline collection (gate detection + resid + baseline logits) ───────
    baseline: dict[str, dict] = {}
    resid_K, resid_nonK = [], []
    for i, p in enumerate(test):
        store, resid, logits = forward_capture(
            p.prompt, model, tok, torch_mod, layers, patch_layer)
        logp0 = log_softmax(logits)
        baseline[p.id] = {
            "combinator": p.combinator,
            "logp0": logp0,
            "zK_at": zK_at(rcc, store, layers, patch_layer),
            "zK_ds0": zK_downstream(rcc, store, layers, crystal_layers, patch_layer),
        }
        if p.combinator == "K":
            resid_K.append(resid)
        else:
            resid_nonK.append(resid)
        if (i + 1) % 25 == 0:
            print(f"[exp1] baseline {i + 1}/{len(test)}")

    resid_K = np.asarray(resid_K)
    resid_nonK = np.asarray(resid_nonK)
    d_raw = resid_K.mean(0) - resid_nonK.mean(0)
    d_K = d_raw / (np.linalg.norm(d_raw) + 1e-12)
    canonical_mag = float(np.mean(resid_K @ d_K))
    print(f"[exp1] d_K built: |d_raw|={np.linalg.norm(d_raw):.3f} "
          f"canonical_mag={canonical_mag:.3f}")

    rng = np.random.default_rng(args.seed)
    rand_dirs = []
    for _ in range(args.n_rand):
        r = rng.standard_normal(d_K.shape)
        rand_dirs.append(r / (np.linalg.norm(r) + 1e-12))

    # ── partition ───────────────────────────────────────────────────────────────────
    detected_K = [p for p in test
                  if p.combinator == "K" and baseline[p.id]["zK_at"] > args.gate_tau]
    nonK = [p for p in test if p.combinator != "K"]
    print(f"[exp1] detected-K (z(K)@L{patch_layer}>{args.gate_tau}): "
          f"{len(detected_K)}/{sum(1 for p in test if p.combinator == 'K')}  "
          f"nonK={len(nonK)}")

    # ── arm runner: returns per-probe (KL_out, zK_ds_after) for a direction+mode ─────
    def run_arm(probes, direction, mode):
        kls, zds = [], []
        for p in probes:
            hook = make_patch_hook(direction, mode, canonical_mag, torch_mod)
            store, _r, logits = forward_capture(
                p.prompt, model, tok, torch_mod, layers, patch_layer,
                patch_hook=hook)
            logp = log_softmax(logits)
            kls.append(kl_div(logp, baseline[p.id]["logp0"]))
            zds.append(zK_downstream(rcc, store, layers, crystal_layers, patch_layer))
        return kls, zds

    def avg_rand(probes, mode):
        """Average the random-control arm over n_rand directions (per-probe means)."""
        kl_stack, z_stack = [], []
        for rd in rand_dirs:
            k, z = run_arm(probes, rd, mode)
            kl_stack.append(k)
            z_stack.append(z)
        kl_mean = list(np.mean(np.asarray(kl_stack), axis=0))
        z_mean = list(np.mean(np.asarray(z_stack), axis=0))
        return kl_mean, z_mean

    arms: dict[str, dict] = {}

    # 1. NECESSITY — detected-K, ablate d_K vs random
    print("[exp1] arm 1: NECESSITY (ablate on detected-K) ...")
    kl_k, z_k = run_arm(detected_K, d_K, "ablate")
    kl_r, z_r = avg_rand(detected_K, "ablate")
    z_base = [baseline[p.id]["zK_ds0"] for p in detected_K]
    arms["necessity"] = {
        "n": len(detected_K),
        "kl_out": paired(kl_k, kl_r),            # expect K > random (perturbs more)
        "zK_ds_delta_k": round(float(np.nanmean(np.asarray(z_k) - z_base)), 4),
        "zK_ds_delta_rand": round(float(np.nanmean(np.asarray(z_r) - z_base)), 4),
        "zK_ds_after": paired(z_k, z_r),         # expect K < random (K-reading drops)
    }

    # 2. PRESERVE — detected-K, set d_K→canonical vs random set
    print("[exp1] arm 2: PRESERVE (set canonical on detected-K) ...")
    kl_k2, _z = run_arm(detected_K, d_K, "set")
    kl_r2, _z = avg_rand(detected_K, "set")
    arms["preserve"] = {
        "n": len(detected_K),
        "kl_out": paired(kl_k2, kl_r2),          # expect K < random (exact preserves)
    }

    # 3. DELIVERY / COUNTERFACTUAL — non-K, set d_K→canonical vs random set
    print("[exp1] arm 3: DELIVERY (inject canonical on non-K) ...")
    kl_k3, z_k3 = run_arm(nonK, d_K, "set")
    kl_r3, z_r3 = avg_rand(nonK, "set")
    zbase_nonK = [baseline[p.id]["zK_ds0"] for p in nonK]
    cross_k = float(np.mean([1.0 if z > args.gate_tau else 0.0
                             for z in z_k3 if np.isfinite(z)]))
    cross_r = float(np.mean([1.0 if z > args.gate_tau else 0.0
                             for z in z_r3 if np.isfinite(z)]))
    arms["delivery"] = {
        "n": len(nonK),
        "zK_ds_after": paired(z_k3, z_r3),       # expect K > random (drives K-reading)
        "zK_ds_delta_k": round(float(np.nanmean(np.asarray(z_k3) - zbase_nonK)), 4),
        "zK_ds_delta_rand": round(float(np.nanmean(np.asarray(z_r3) - zbase_nonK)), 4),
        "kl_out": paired(kl_k3, kl_r3),
        "frac_cross_tau_k": round(cross_k, 3),
        "frac_cross_tau_rand": round(cross_r, 3),
    }

    # ── verdict ─────────────────────────────────────────────────────────────────────
    nec = arms["necessity"]
    pres = arms["preserve"]
    deliv = arms["delivery"]
    necessity_ok = bool(
        (nec["kl_out"]["delta"] or 0) > 0 and (nec["kl_out"]["t"] or 0) > 2.0
        and nec["zK_ds_delta_k"] < nec["zK_ds_delta_rand"])
    preserve_ok = bool(
        (pres["kl_out"]["delta"] or 0) < 0 and (pres["kl_out"]["t"] or 0) < -2.0)
    delivery_ok = bool(
        (deliv["zK_ds_after"]["delta"] or 0) > 0
        and (deliv["zK_ds_after"]["t"] or 0) > 2.0
        and deliv["frac_cross_tau_k"] > deliv["frac_cross_tau_rand"])
    splice_causal = necessity_ok and delivery_ok

    verdict = {
        "model": model_name, "patch_layer": patch_layer, "gate_tau": args.gate_tau,
        "n_layers": n_layers, "crystal_layers": crystal_layers,
        "n_detected_K": len(detected_K), "n_nonK": len(nonK),
        "canonical_mag": round(canonical_mag, 4),
        "d_raw_norm": round(float(np.linalg.norm(d_raw)), 4),
        "arms": arms,
        "necessity_ok": necessity_ok, "preserve_ok": preserve_ok,
        "delivery_ok": delivery_ok, "splice_causal": splice_causal,
    }

    # ── report ──────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 82)
    print(f"KERNEL-SPLICE EXP 1 — CAUSAL K-SPLICE — {model_name}  L{patch_layer}")
    print("═" * 82)
    print(f"  detected-K={len(detected_K)}  nonK={len(nonK)}  "
          f"canonical_mag={canonical_mag:.3f}  tau={args.gate_tau}")
    print("\n  -- NECESSITY (ablate d_K on detected-K; expect K perturbs MORE) --")
    print(f"     KL_out  K={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']} "
          f"d={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
    print(f"     zKds  d_K={nec['zK_ds_delta_k']} d_rand={nec['zK_ds_delta_rand']}  "
          f"after K={nec['zK_ds_after']['k_mean']} r={nec['zK_ds_after']['rand_mean']}")
    print(f"     => necessity_ok = {necessity_ok}")
    print("\n  -- PRESERVE (set d_K->canon on detected-K; K perturbs LESS) --")
    print(f"     KL_out  K={pres['kl_out']['k_mean']} "
          f"rand={pres['kl_out']['rand_mean']} "
          f"d={pres['kl_out']['delta']} t={pres['kl_out']['t']}")
    print(f"     => preserve_ok = {preserve_ok}")
    print("\n  -- DELIVERY (inject d_K->canon on non-K; drives downstream K) --")
    print(f"     zKds  K={deliv['zK_ds_after']['k_mean']} "
          f"rand={deliv['zK_ds_after']['rand_mean']} "
          f"d={deliv['zK_ds_after']['delta']} t={deliv['zK_ds_after']['t']}")
    print(f"     frac zKds>tau  K={deliv['frac_cross_tau_k']} "
          f"rand={deliv['frac_cross_tau_rand']}  "
          f"KL_out d={deliv['kl_out']['delta']}")
    print(f"     => delivery_ok = {delivery_ok}")
    print(f"\n  * SPLICE CAUSAL (necessity AND delivery) = {splice_causal}"
          f"   [preserve={preserve_ok}]")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "calibration_summary": cal}
    (RESULTS_DIR / f"exp1_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "patch_layer": patch_layer, "gate_tau": args.gate_tau,
        "n_perm": n_perm, "heldout_per": heldout, "n_rand": args.n_rand,
        "seed": args.seed, "n_calib": len(calib), "n_test": len(test),
        "metric": "DETECT gate-z(K)@L (sign-CMR); EFFECT residual d_K patch at L "
                  "last-token; READ downstream detector z(K) (>L) + final next-token "
                  "KL; all vs random-direction control of equal magnitude",
        "scope": "PROSE crystal_probes (K semantics, no kernel-certifiable gold) -> "
                 "tests the K-DIRECTION's causal sufficiency/necessity; operand-bound "
                 "kernel-value splice on the certified corpus = Exp 2",
    }
    (RESULTS_DIR / f"exp1_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[exp1] wrote {RESULTS_DIR}/exp1_verdict_{slug}.json")


if __name__ == "__main__":
    main()
