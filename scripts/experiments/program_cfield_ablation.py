#!/usr/bin/env python3
# register: causal (routing direction; s239 sufficiency/necessity protocol)
"""Program C-field ablation — is the applicative-C routing field LOAD-BEARING? (s250).

THE s249 OPEN DOOR. Session 249 established (Qwen3-14B sweet spot) that the FFN gate
register exposes a DECODABLE applicative-C routing field: as object count rises
{0,1,2} the positive C-mass rises (Spearman ~0.54, p=0), the C peak sits at L~30-31,
and the model reads objects as arguments (C) not existential witnesses (B). But every
s249 result is DECODABILITY — a read. The open question the thread leaves:

    is the C-field LOAD-BEARING (causally necessary for the model's object-application
    computation) or merely a READABLE epiphenomenon / common-mode correlate?

This is the `λ measure` causality test (decodability ≠ causality, db5d4eb / s247-v4).

THE DESIGN (reuses the validated s248 Exp-1 causal spine — kernel_splice_exp1_ksplice):
  - DETECT/READ in the gate register: the RelationalCrystal classifier (sign-CMR
    centroids, relational_opcode.py) reads downstream z(C).
  - EFFECT in the residual: d_C = unit diff-of-means(resid_Cpresent - resid_Cabsent) at
    the patch layer, built from mean-over-content residuals. We patch the OUTPUT of
    model.model.layers[L] (the residual) across CONTENT positions at L30 AND L31 (the
    s249 C-peak zone, depth ~0.75-0.78).
  - CONTROL: a random direction of equal magnitude (s239), averaged over n_rand draws.

THE MATCHED LADDER (data/reading-probes.jsonl, 45x3): intransitive (const_c=0, no
object → no C-application) vs transitive (c=1) vs ditransitive (c=2, two objects → most
C-application). The const labeling enforces C-count == #objects.

THREE ARMS:
  1. NECESSITY (ditransitive, c=2): ablate d_C across content positions. If the C-field
     is load-bearing the next-token output is PERTURBED (KL) and downstream z(C) DROPS,
     MORE than a random direction of equal magnitude.
  2. SPECIFICITY / DIFFERENTIAL (intransitive, c=0): the SAME ablation. With no object
     there is no C-application to disrupt → the C-direction-specific perturbation should
     be SMALLER than on c=2. The load-bearing signature is that the d_C-vs-random net
     effect SCALES with C-load (c=2 net ≫ c=0 net). A flat differential ⇒ the field is a
     generic/common-mode correlate, NOT load-bearing.
  3. DELIVERY / SUFFICIENCY (intransitive, c=0): inject d_C→canonical where no object
     fires. If sufficient, downstream z(C) RISES vs random (manufacture C-routing).

VERDICT (λ measure, two-sided):
  load_bearing = necessity_ok (c=2 ablate: KL>random t>2 ∧ z(C) drops more than random)
                 AND differential_ok (c=2 net-KL > c=0 net-KL, two-sample t>2).
  necessity without differential ⇒ d_C ablation generically perturbs (common-mode), the
  field is READABLE not load-bearing — a λ measure win that holds the s249 boundary.

Usage:
    uv run python scripts/experiments/program_cfield_ablation.py --smoke
    uv run python scripts/experiments/program_cfield_ablation.py \
        --model Qwen/Qwen3-14B --patch-layers 30 31

License: MIT. AGENTS.md S5 λ provenance (written from this project's instruments).
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

from kernel_reference_prose_v2 import read_last_token_z  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _hook_module,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)

RESULTS_DIR = _ROOT / "results" / "program-cfield-ablation"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# Corpus — the matched object-count ladder (const labeling, C-count == #objects)
# ═══════════════════════════════════════════════════════════════════════════════
def load_ladder(path: Path) -> list[dict]:
    rows = []
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        rows.append({
            "input": r["input"],
            "category": r["category"],
            "n_objects": r["n_objects"],
            "c_count": r["const_c"],  # const reading: C-count == #objects (s248)
            "b_count": r["const_b"],
        })
    return rows


# ═══════════════════════════════════════════════════════════════════════════════
# Intervention hook — patch the residual d-component over a CONTENT position range
# ═══════════════════════════════════════════════════════════════════════════════
def make_field_patch_hook(direction_unit, mode: str, target_mag: float, torch_mod,
                          pos_start: int, pos_end: int):
    """Forward hook on a decoder layer: modify the d-component of the residual at every
    content position in [pos_start, pos_end).

    mode='ablate' → project the direction OUT (set its component to 0) per position.
    mode='set'    → overwrite the component to `target_mag` per position.
    """
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)
        end = min(pos_end, h.shape[1])
        if pos_start >= end:
            return out
        v = h[0, pos_start:end, :]            # [P, d]
        proj = v @ d                          # [P]
        if mode == "ablate":
            h[0, pos_start:end, :] = v - proj[:, None] * d
        elif mode == "set":
            h[0, pos_start:end, :] = v - proj[:, None] * d + target_mag * d
        else:
            raise ValueError(f"unknown mode {mode!r}")
        return out
    return hook


def forward_capture(prompt, model, tok, torch_mod, gate_layers, patch_layers,
                    resid_layer, patch_hooks=None):
    """ONE forward. Capture: gate register (all gate_layers, [T,d]); the pre-patch
    residual at `resid_layer` over CONTENT positions (mean) — read BEFORE any patch
    hook on that layer; the final next-token logits. `patch_hooks` is an optional
    {layer: hook} applied to layers[layer] output (registered AFTER the resid read so
    the read stays clean)."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in gate_layers:
        handles.append(_hook_module(model, li, "gate").register_forward_hook(
            _make_hook(store, li)))
    resid_box: dict[str, np.ndarray] = {}

    def resid_read(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        resid_box["v"] = h[0, :, :].detach().float().cpu().numpy().astype(np.float64)
    handles.append(model.model.layers[resid_layer].register_forward_hook(resid_read))
    if patch_hooks:
        for li, hk in patch_hooks.items():
            handles.append(model.model.layers[li].register_forward_hook(hk))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        logits_last = out.logits[0, -1, :].detach().float().cpu().numpy().astype(
            np.float64)
    finally:
        for h in handles:
            h.remove()
    return store, resid_box.get("v"), logits_last


# ═══════════════════════════════════════════════════════════════════════════════
# Readouts
# ═══════════════════════════════════════════════════════════════════════════════
def log_softmax(logits: np.ndarray) -> np.ndarray:
    m = logits.max()
    z = logits - m
    return z - np.log(np.exp(z).sum())


def kl_div(logp_p: np.ndarray, logp_q: np.ndarray) -> float:
    """KL(P‖Q) in nats."""
    p = np.exp(logp_p)
    return float(np.sum(p * (logp_p - logp_q)))


def zC_downstream(rcc, store, all_layers, crystal_layers, max_patch) -> float:
    """Mean detector z(C) over CRYSTAL layers strictly downstream of the patch."""
    zmap = read_last_token_z(rcc, store, all_layers)
    ds = [zmap[li]["C"] for li in crystal_layers if li > max_patch and li in zmap]
    return float(np.mean(ds)) if ds else float("nan")


def paired(a_list: list[float], b_list: list[float]) -> dict:
    """Paired comparison (d_C vs random control) over items."""
    a, b = np.asarray(a_list, float), np.asarray(b_list, float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = len(a)
    if n < 2:
        return {"n": n, "k_mean": None, "rand_mean": None, "delta": None, "t": None}
    diff = a - b
    sd = diff.std(ddof=1)
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    return {"n": n, "k_mean": round(float(a.mean()), 5),
            "rand_mean": round(float(b.mean()), 5),
            "delta": round(float(diff.mean()), 5),
            "t": round(float(diff.mean() / se), 3) if se > 0 else None}


def two_sample_t(a_list: list[float], b_list: list[float]) -> dict:
    """Welch two-sample t: is group-a net effect > group-b net effect?"""
    a = np.asarray([x for x in a_list if np.isfinite(x)], float)
    b = np.asarray([x for x in b_list if np.isfinite(x)], float)
    if len(a) < 2 or len(b) < 2:
        return {"na": len(a), "nb": len(b), "mean_a": None, "mean_b": None,
                "diff": None, "t": None}
    va, vb = a.var(ddof=1), b.var(ddof=1)
    se = np.sqrt(va / len(a) + vb / len(b))
    diff = a.mean() - b.mean()
    return {"na": len(a), "nb": len(b), "mean_a": round(float(a.mean()), 5),
            "mean_b": round(float(b.mean()), 5), "diff": round(float(diff), 5),
            "t": round(float(diff / se), 3) if se > 0 else None}


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Causal C-field ablation (s250)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--patch-layers", type=int, nargs="+", default=[30, 31],
                    help="residual layers to patch (s249 C-peak zone)")
    ap.add_argument("--n-rand", type=int, default=3,
                    help="random control directions to average over")
    ap.add_argument("--max-per-group", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    patch_layers = sorted(args.patch_layers)
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap = 80, 3, 200
        max_per_group = args.max_per_group or 5
        print("[cfield] SMOKE MODE")
    else:
        n_perm, ppc, null_cap = 300, None, None
        max_per_group = args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    # scale patch layers if they exceed this model (smoke / smaller models)
    if max(patch_layers) >= n_layers:
        denom = max(n_layers - 1, 1)
        # keep the s249 depth band (~0.75-0.78) for whichever model
        patch_layers = sorted({min(n_layers - 2, round(f * denom))
                               for f in (0.75, 0.775)})
        print(f"[cfield] patch layers rescaled for {n_layers}L → {patch_layers}")
    resid_layer = patch_layers[0]
    max_patch = max(patch_layers)
    print(f"[cfield] model={model_name} layers={n_layers} patch={patch_layers}")

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode=args.null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    print(f"[cfield] crystal {len(crystal_layers)}/{n_layers}; "
          f"downstream layers > L{max_patch}")

    gate_n = gate_prefix_len(tok)

    # ── partition the matched ladder ─────────────────────────────────────────────
    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    c0, c1, c2 = grp(0), grp(1), grp(2)
    print(f"[cfield] c0(intrans)={len(c0)} c1(trans)={len(c1)} c2(ditrans)={len(c2)}")

    # ── Pass A: baseline (gate read + content-mean residual + baseline logits) ───
    baseline: dict[str, dict] = {}
    resid_present, resid_absent = [], []

    def base_pass(items, c_present):
        for i, r in enumerate(items):
            prompt = COMPILE_GATE + r["input"]
            store, resid, logits = forward_capture(
                prompt, model, tok, torch_mod, layers, patch_layers, resid_layer)
            n_tok = store[layers[0]].shape[0]
            start = min(gate_n, n_tok - 1)
            content_mean = resid[start:n_tok].mean(axis=0)
            baseline[r["input"]] = {
                "c_count": r["c_count"], "category": r["category"],
                "logp0": log_softmax(logits),
                "start": start, "n_tok": n_tok,
                "zC_ds0": zC_downstream(rcc, store, layers, crystal_layers, max_patch),
            }
            (resid_present if c_present else resid_absent).append(content_mean)
            if (i + 1) % 20 == 0:
                print(f"[cfield]   baseline {i + 1}/{len(items)}")

    print("[cfield] Pass A: baseline (C-present=trans+ditrans, C-absent=intrans) ...")
    base_pass(c0, c_present=False)
    base_pass(c1, c_present=True)
    base_pass(c2, c_present=True)

    resid_present = np.asarray(resid_present)
    resid_absent = np.asarray(resid_absent)
    d_raw = resid_present.mean(0) - resid_absent.mean(0)
    d_C = d_raw / (np.linalg.norm(d_raw) + 1e-12)
    canonical_mag = float(np.mean(resid_present @ d_C))
    print(f"[cfield] d_C: |d_raw|={np.linalg.norm(d_raw):.3f} "
          f"canonical_mag={canonical_mag:.3f}")

    rng = np.random.default_rng(args.seed)
    rand_dirs = []
    for _ in range(args.n_rand):
        rr = rng.standard_normal(d_C.shape)
        rand_dirs.append(rr / (np.linalg.norm(rr) + 1e-12))

    # ── arm runner: per-item (KL_out, zC_ds_after) for a direction + mode ────────
    def run_arm(items, direction, mode):
        kls, zds = [], []
        for r in items:
            b = baseline[r["input"]]
            hooks = {li: make_field_patch_hook(
                direction, mode, canonical_mag, torch_mod, b["start"], b["n_tok"])
                for li in patch_layers}
            store, _resid, logits = forward_capture(
                COMPILE_GATE + r["input"], model, tok, torch_mod, layers,
                patch_layers, resid_layer, patch_hooks=hooks)
            kls.append(kl_div(log_softmax(logits), b["logp0"]))
            zds.append(zC_downstream(rcc, store, layers, crystal_layers, max_patch))
        return kls, zds

    def avg_rand(items, mode):
        kl_stack, z_stack = [], []
        for rd in rand_dirs:
            k, z = run_arm(items, rd, mode)
            kl_stack.append(k)
            z_stack.append(z)
        return (list(np.mean(np.asarray(kl_stack), axis=0)),
                list(np.mean(np.asarray(z_stack), axis=0)))

    arms: dict[str, dict] = {}

    # ── ARM 1 NECESSITY (c=2 ditrans, ablate) ───────────────────────────────────
    print("[cfield] arm 1: NECESSITY (ablate d_C on c=2 ditransitive) ...")
    kl_c2, z_c2 = run_arm(c2, d_C, "ablate")
    klr_c2, zr_c2 = avg_rand(c2, "ablate")
    zbase_c2 = [baseline[r["input"]]["zC_ds0"] for r in c2]
    arms["necessity_c2"] = {
        "n": len(c2),
        "kl_out": paired(kl_c2, klr_c2),                  # expect d_C > random
        "zC_ds_delta_dC": round(float(np.nanmean(np.asarray(z_c2) - zbase_c2)), 5),
        "zC_ds_delta_rand": round(float(np.nanmean(np.asarray(zr_c2) - zbase_c2)), 5),
        "zC_ds_after": paired(z_c2, zr_c2),               # expect d_C < random (drops)
    }

    # ── ARM 2 SPECIFICITY (c=0 intrans, ablate) — the differential ───────────────
    print("[cfield] arm 2: SPECIFICITY (ablate d_C on c=0 intransitive) ...")
    kl_c0, z_c0 = run_arm(c0, d_C, "ablate")
    klr_c0, zr_c0 = avg_rand(c0, "ablate")
    zbase_c0 = [baseline[r["input"]]["zC_ds0"] for r in c0]
    arms["specificity_c0"] = {
        "n": len(c0),
        "kl_out": paired(kl_c0, klr_c0),
        "zC_ds_delta_dC": round(float(np.nanmean(np.asarray(z_c0) - zbase_c0)), 5),
        "zC_ds_delta_rand": round(float(np.nanmean(np.asarray(zr_c0) - zbase_c0)), 5),
        "zC_ds_after": paired(z_c0, zr_c0),
    }

    # net (d_C - random) per item, the C-direction-specific perturbation
    net_kl_c2 = list(np.asarray(kl_c2) - np.asarray(klr_c2))
    net_kl_c0 = list(np.asarray(kl_c0) - np.asarray(klr_c0))
    differential = two_sample_t(net_kl_c2, net_kl_c0)  # expect c2 > c0

    # ── ARM 3 DELIVERY (c=0 intrans, inject) ─────────────────────────────────────
    print("[cfield] arm 3: DELIVERY (inject d_C→canonical on c=0 intransitive) ...")
    kl_d, z_d = run_arm(c0, d_C, "set")
    klr_d, zr_d = avg_rand(c0, "set")
    zbase_d = [baseline[r["input"]]["zC_ds0"] for r in c0]
    arms["delivery_c0"] = {
        "n": len(c0),
        "zC_ds_after": paired(z_d, zr_d),                 # expect d_C > random (rises)
        "zC_ds_delta_dC": round(float(np.nanmean(np.asarray(z_d) - zbase_d)), 5),
        "zC_ds_delta_rand": round(float(np.nanmean(np.asarray(zr_d) - zbase_d)), 5),
        "kl_out": paired(kl_d, klr_d),
    }

    # ── verdict ──────────────────────────────────────────────────────────────────
    nec = arms["necessity_c2"]
    deliv = arms["delivery_c0"]
    necessity_ok = bool(
        (nec["kl_out"]["delta"] or 0) > 0 and (nec["kl_out"]["t"] or 0) > 2.0
        and nec["zC_ds_delta_dC"] < nec["zC_ds_delta_rand"])
    differential_ok = bool(
        (differential["diff"] or 0) > 0 and (differential["t"] or 0) > 2.0)
    delivery_ok = bool(
        (deliv["zC_ds_after"]["delta"] or 0) > 0
        and (deliv["zC_ds_after"]["t"] or 0) > 2.0)
    load_bearing = necessity_ok and differential_ok

    verdict = {
        "model": model_name, "n_layers": n_layers, "patch_layers": patch_layers,
        "crystal_layers": crystal_layers, "null_mode": args.null_mode,
        "n_c0": len(c0), "n_c1": len(c1), "n_c2": len(c2),
        "canonical_mag": round(canonical_mag, 4),
        "d_raw_norm": round(float(np.linalg.norm(d_raw)), 4),
        "n_rand": args.n_rand, "seed": args.seed,
        "arms": arms, "differential_net_kl_c2_vs_c0": differential,
        "necessity_ok": necessity_ok, "differential_ok": differential_ok,
        "delivery_ok": delivery_ok, "load_bearing": load_bearing,
    }

    # ── report ─────────────────────────────────────────────────────────────────────
    print("\n" + "═" * 82)
    print(f"PROGRAM C-FIELD ABLATION — {model_name}  L{patch_layers}")
    print("═" * 82)
    print(f"  c0(intrans)={len(c0)} c1(trans)={len(c1)} c2(ditrans)={len(c2)}  "
          f"canonical_mag={canonical_mag:.3f}")
    print("\n  -- NECESSITY (ablate d_C on c=2; expect d_C perturbs MORE) --")
    print(f"     KL_out  dC={nec['kl_out']['k_mean']} rand={nec['kl_out']['rand_mean']}"
          f"  d={nec['kl_out']['delta']} t={nec['kl_out']['t']}")
    print(f"     zCds Δ  dC={nec['zC_ds_delta_dC']} rand={nec['zC_ds_delta_rand']}")
    print(f"     => necessity_ok = {necessity_ok}")
    print("\n  -- DIFFERENTIAL (net KL = d_C-rand; expect c2 > c0) --")
    print(f"     net_KL c2={differential['mean_a']} c0={differential['mean_b']}  "
          f"diff={differential['diff']} t={differential['t']}")
    print(f"     => differential_ok = {differential_ok}")
    print("\n  -- DELIVERY (inject d_C→canon on c=0; drives downstream z(C)) --")
    print(f"     zCds  dC={deliv['zC_ds_after']['k_mean']} "
          f"rand={deliv['zC_ds_after']['rand_mean']} "
          f"d={deliv['zC_ds_after']['delta']} t={deliv['zC_ds_after']['t']}")
    print(f"     => delivery_ok = {delivery_ok}")
    print(f"\n  * LOAD-BEARING (necessity AND differential) = {load_bearing}"
          f"   [delivery={delivery_ok}]")
    print("═" * 82 + "\n")

    # ── write ──────────────────────────────────────────────────────────────────────
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe({"verdict": verdict, "calibration_summary": cal}),
                   indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "patch_layers": patch_layers, "n_perm": n_perm, "n_rand": args.n_rand,
        "seed": args.seed, "null_mode": args.null_mode,
        "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "DETECT/READ gate-z(C) (sign-CMR); EFFECT residual d_C = "
                  "diff-of-means(C-present - C-absent) patched over CONTENT positions "
                  "at L30/L31; READ downstream z(C) + next-token KL; vs random "
                  "direction of equal magnitude; load-bearing = necessity AND c2>c0 "
                  "differential.",
        "scope": "Tests whether the s249 decodable applicative-C field is causally "
                 "load-bearing or a readable common-mode correlate.",
    }
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[cfield] wrote {RESULTS_DIR}/verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
