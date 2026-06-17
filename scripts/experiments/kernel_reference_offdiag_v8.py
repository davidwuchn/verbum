#!/usr/bin/env python3
# register: 2nd-ORDER OFF-DIAGONAL interlayer curvature (H_{late,early} of LM CE/gate)
"""Kernel-ref OFF-DIAGONAL interlayer curvature -- is B in the f.g cross-coupling?
(s238 lead 2d prong 1c-iii).

B = composition (B f g x = f(g x)). Its backward signature is the chain rule, a PRODUCT
of derivatives `d(f.g)/dx = f'(g x).g'(x)`. Prong 1c-ii (kernel_reference_jacobian_v7)
read the DIAGONAL Hessian of the LM loss w.r.t. the gate activation via a Rademacher
Hutchinson estimator `diag(H)_a = E_v[v_a (Hv)_a]`. That estimator CANCELS every
cross-coord AND cross-layer term in expectation (`E[v_a v_b]=0`, a!=b), so it captured
only the WITHIN-layer quadratic form `g'^T (diag) g'`. B sat right ON the bar there
(discr_z +0.118, t=1.90 < 2.0) with a clean monotone climb act(-0.05) -> grad(+1.07) ->
diag-curv(+1.90).

But the LITERAL f.g coupling is the OFF-DIAGONAL block. For `L = l(f(g(z)))` with the
gate activation `z` split into an EARLY block `z_e` (~ g, processed first) and a LATE
block `z_l` (~ f, applied last),

    d2L/dz_l dz_e = the OFF-DIAGONAL Hessian block H_{l,e}   # the chain-rule cross term

is exactly "how the curvature of the late computation (f) couples to the early
computation (g)" -- the product-of-derivatives the diagonal read threw away.

ISOLATION (deterministic, ONE double-backward, NO Hutchinson noise):
  Perturb the GRADIENT direction supported ONLY on the EARLY block: v = g_e.detach() on
  EARLY, 0 on LATE. Then for any LATE layer li (li not in EARLY),

      (Hv)_li = Sum_{e in EARLY} H_{li,e} g_e        # PURE off-diagonal (no H_{li,li})

  because v is zero at li so the diagonal block never enters. Computed as a single HVP:
      s  = Sum_{e in EARLY} (g_e . g_e.detach()).sum()    # g_e = grad(CE, gate_e, c.g.)
      hv = grad(s, [gate_li for li in LATE])              # = 2.Sum_e H_{li,e} g_e (sym)
  The factor 2 is an overall scale; sign-CMR in the classifier is scale-free.

  The perturbation direction is the GRADIENT (the loss-relevant / backprop direction the
  chain rule actually propagates), NOT random -- a random v would have E[(Hv)_li]=0 and
  give a zero-mean, unstable per-probe feature. The gradient direction makes the feature
  deterministic and meaningful (the literal backward composition coupling).

Clean register-swap of v7: same RelationalCrystalClassifier (sign-CMR, crosstask null,
raw-z Welch contrast), same calibrate -> classify -> discr_z pipeline; the feature =
PURE OFF-DIAGONAL interlayer curvature (Hv)_late, pooled over supervised positions. The
classifier runs on the LATE layers only (where the feature is defined / off-diagonal).

VERDICT LOGIC (lambda measure, two-sided):
  - B discriminates in the OFF-DIAGONAL where it sat ON the bar in the diagonal (v7
    t=1.90) -> the f.g chain-rule cross-coupling is B's home; the curvature climb
    completes off the diagonal. (Compare discr_z(B) to v7's diagonal +1.90.)
  - B flat off-diagonal too -> the curvature register is exhausted at BOTH the diagonal
    AND the off-diagonal; B's positive signal is the FORWARD order-cost face (prong 2b),
    not a localizable second-order amplitude.
  - INSTRUMENT CHECK: {C,Y} (the curvature-discriminable set, v7) should still
    discriminate in the off-diagonal block, else the read is broken not B-absent.

Usage:
    uv run python scripts/experiments/kernel_reference_offdiag_v8.py --smoke
    uv run python scripts/experiments/kernel_reference_offdiag_v8.py            # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import split_probes, welch_t  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    BASELINE_NULL_SENTENCES,
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)
from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "kernel-reference-audit"
TEST_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y"]


def split_early_late(n_layers: int, split_frac: float) -> tuple[list[int], list[int]]:
    """Partition layers into EARLY (~ g, processed first) and LATE (~ f, applied last).

    split_frac = fraction of the stack that is EARLY. LATE = the readable mid-late zone
    (depth >= split_frac) where the combinator crystal lives (s187/s227). The off-diag
    feature is read on the LATE layers (coupling FROM the early block TO each late).
    """
    k = max(1, round(n_layers * split_frac))
    k = min(k, n_layers - 1)
    early = list(range(k))
    late = list(range(k, n_layers))
    return early, late


def forward_offdiag(prompt, model, tok, torch_mod, early, late):
    """Forward + double-backward; return ({li in late: off-diag (Hv)_li [T,d]}, n_tok).

    v = g_e.detach() on the EARLY block, 0 on LATE.  (Hv)_li = Sum_{e} H_{li,e} g_e
    for li in LATE = the PURE off-diagonal interlayer curvature (the chain-rule cross
    term, no within-layer H_{li,li} since v is zero at li). One HVP = a double-backward
    of the scalar Sum_e ||g_e||^2 (detached), g = grad(CE, gates, create_graph=True).
    Per-token rows returned (callers pool 0..n_tok-2; the last token feeds only the
    unsupervised next-token so its gradient/curvature row is ~0).
    """
    import torch.nn.functional as func
    all_layers = early + late
    store: dict[int, object] = {}

    def _cap(li):
        def _hook(_m, _inp, out):
            store[li] = out  # live graph tensor (NOT detached)
        return _hook

    handles = [model.model.layers[li].mlp.gate_proj.register_forward_hook(_cap(li))
               for li in all_layers]
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        out = model(**inputs)
        logits = out.logits[0]               # [T, V]
        ids = inputs["input_ids"][0]         # [T]
        t = ids.shape[0]
        ce = func.cross_entropy(logits[:-1, :], ids[1:], reduction="mean")
        gates_all = [store[li] for li in all_layers]
        grads_all = torch_mod.autograd.grad(ce, gates_all, create_graph=True)
        grad_of = dict(zip(all_layers, grads_all, strict=True))
        # scalar Sum_e(g_e . g_e.detach()) -> grad wrt LATE = 2 Sum_e H_{late,e} g_e
        scalar = sum((grad_of[e] * grad_of[e].detach()).sum() for e in early)
        late_gates = [store[li] for li in late]
        hv_late = torch_mod.autograd.grad(scalar, late_gates, retain_graph=False)
    finally:
        for h in handles:
            h.remove()
    result = {li: hv_late[j][0].detach().float().cpu().numpy().astype(np.float64)
              for j, li in enumerate(late)}
    return result, t


def pooled_supervised(feat_store, late, n_tok):
    """Mean-pool the off-diag feature over supervised positions 0..n_tok-2 -> {li:d}."""
    sup = max(1, n_tok - 1)
    return {li: feat_store[li][:sup].mean(axis=0) for li in late}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref off-diag curvature (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=25, help="calib probes/combinator")
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--split-frac", type=float, default=0.5,
                        help="fraction of the stack that is EARLY (g); LATE = the rest")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        heldout, ppc, n_perm, null_cap = 5, 5, 80, 150
        print("[offdiag] SMOKE MODE")
    else:
        heldout, ppc, n_perm, null_cap = (
            args.heldout_per, args.ppc, args.n_perm, args.null_cap)

    calib, test = split_probes(heldout)
    kept, counts = [], Counter()
    for p in calib:
        if counts[p.combinator] < ppc:
            kept.append(p)
            counts[p.combinator] += 1
    calib = kept
    print(f"[offdiag] calib={len(calib)} test={len(test)} ppc={ppc} "
          f"split_frac={args.split_frac}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    early, late = split_early_late(n_layers, args.split_frac)
    print(f"[offdiag] EARLY={early[0]}..{early[-1]} ({len(early)} layers, ≈g)  "
          f"LATE={late[0]}..{late[-1]} ({len(late)} layers, ≈f) — feature read on LATE")

    # ── calibration: per-probe POOLED off-diagonal centroids (LATE layers) ───────
    gate_by_layer: dict[int, list] = {li: [] for li in late}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 25 == 0:
            print(f"[offdiag]   calib fwd+2bwd {i}/{len(calib)} ...")
        fstore, nt = forward_offdiag(p.prompt, model, tok, torch_mod, early, late)
        pooled = pooled_supervised(fstore, late, nt)
        for li in late:
            gate_by_layer[li].append(pooled[li])
        labels.append(p.combinator)
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in late}
    labels_np = np.array(labels)

    # ── null: per-supervised-token off-diagonal feature of natural text ──────────
    null_by_layer: dict[int, list] = {li: [] for li in late}
    print(f"[offdiag] building null ({len(BASELINE_NULL_SENTENCES)} prompts)")
    for s in BASELINE_NULL_SENTENCES:
        fstore, nt = forward_offdiag(s, model, tok, torch_mod, early, late)
        sup = max(1, nt - 1)
        for li in late:
            null_by_layer[li].append(fstore[li][:sup])  # supervised rows
    null_np = {li: np.concatenate(null_by_layer[li], axis=0)[:null_cap] for li in late}

    rcc = RelationalCrystalClassifier(late, n_perm=n_perm, z_thresh=2.0,
                                      sil_z_thresh=2.0, consensus_gram="auto")
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    crystal_layers = rcc.crystal_layers
    print(f"[offdiag] crystal layers (off-diag curvature): "
          f"{len(crystal_layers)}/{len(late)} late")

    # ── read held-out prose: pooled off-diagonal pseudo-token → per-layer z ──────
    cset = set(crystal_layers)
    per_probe = []
    for i, p in enumerate(test):
        if i % 25 == 0:
            print(f"[offdiag]   test fwd+2bwd {i}/{len(test)} ...")
        fstore, nt = forward_offdiag(p.prompt, model, tok, torch_mod, early, late)
        pooled = pooled_supervised(fstore, late, nt)
        per_layer = rcc.classify(pooled).per_layer
        crystal_z = {li: {op: float(per_layer[li].get(op, 0.0)) for op in CRYSTAL}
                     for li in per_layer if li in cset}
        layer_avg = ({op: float(np.mean([crystal_z[li][op] for li in crystal_z]))
                      for op in CRYSTAL} if crystal_z else {op: 0.0 for op in CRYSTAL})
        per_probe.append({
            "combinator": p.combinator,
            "layer_avg_z": {op: round(v, 4) for op, v in layer_avg.items()},
            "crystal_z": {str(li): {op: round(crystal_z[li][op], 3) for op in CRYSTAL}
                          for li in crystal_z}})

    # ── discr_z(c): raw-z Welch contrast on the OFF-DIAGONAL (mirror v6/v7) ───────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if on:
            discr_z[c] = welch_t(on, off)

    # per-layer profile (where in the LATE stack does each op discriminate off-diag)
    peak: dict[str, dict] = {}
    for c in CRYSTAL:
        on_rows = [r for r in per_probe if r["combinator"] == c]
        off_rows = [r for r in per_probe if r["combinator"] != c]
        if not on_rows:
            continue
        best = None
        for li in crystal_layers:
            sli = str(li)
            on_z = [r["crystal_z"][sli][c] for r in on_rows if sli in r["crystal_z"]]
            off_z = [r["crystal_z"][sli][c] for r in off_rows if sli in r["crystal_z"]]
            if not on_z:
                continue
            d = float(np.mean(on_z)) - (float(np.mean(off_z)) if off_z else 0.0)
            if best is None or d > best[1]:
                best = (li, round(d, 3))
        if best:
            peak[c] = {"layer": best[0], "delta": best[1]}

    b = discr_z.get("B", {})
    b_in_offdiag = bool(b.get("significant") and b.get("discr_z", 0) > 0)
    # instrument check: did the curvature-discriminable set survive the off-diag read?
    instr = {c: bool(discr_z.get(c, {}).get("significant")
                     and discr_z.get(c, {}).get("discr_z", 0) > 0)
             for c in ("C", "Y", "K")}
    verdict = {
        "register": "off-diagonal interlayer curvature "
                    "(H_{late,early}·g_early, pooled supervised, gradient direction)",
        "split_frac": args.split_frac,
        "early_layers": [early[0], early[-1]], "late_layers": [late[0], late[-1]],
        "n_test": len(per_probe), "discr_z": discr_z,
        "peak_layer": peak, "b_discriminates_in_offdiag": b_in_offdiag,
        "instrument_works": instr,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    print("\n" + "═" * 74)
    print("KERNEL-REF OFF-DIAGONAL CURVATURE — is B in the f∘g chain-rule cross term?")
    print("═" * 74)
    print(f"  n_test={verdict['n_test']}  crystal_layers={len(crystal_layers)}"
          f"  EARLY={early[0]}..{early[-1]}  LATE={late[0]}..{late[-1]}")
    print(f"\n  {'op':<4}{'on_z':>9}{'off_z':>9}{'discr_z':>9}{'t':>8}{'sig':>5}"
          f"{'peakL':>7}")
    for c in CRYSTAL:
        d = discr_z.get(c)
        if d is None:
            continue
        sig = "✓" if d["significant"] and d["discr_z"] > 0 else " "
        pk = peak.get(c, {}).get("layer", "-")
        print(f"  {c:<4}{d['on_mean']:>9}{d['off_mean']:>9}{d['discr_z']:>9}"
              f"{(d['t'] or 0):>8}{sig:>5}{pk!s:>7}")
    print(f"\n  instrument check (C/Y/K discriminate off-diagonal): {instr}")
    print(f"  ★ B discriminates in the OFF-DIAGONAL register: "
          f"{b_in_offdiag}  (B discr_z={b.get('discr_z')}, t={b.get('t')})")
    print("  (compare v7 DIAGONAL: B discr_z +0.118, t=1.90; the monotone climb was "
          "act -0.05 -> grad +1.07 -> diag-curv +1.90)")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_probe": per_probe,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"offdiag_v8_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "ppc": ppc, "heldout_per": heldout,
        "split_frac": args.split_frac,
        "early_layers": [early[0], early[-1]], "late_layers": [late[0], late[-1]],
        "n_calib": len(calib), "n_test": len(test),
        "register": "OFF-DIAGONAL interlayer curvature H_{late,early}·g_early, "
                    "pooled supervised, deterministic gradient direction, one HVP",
    }
    (RESULTS_DIR / f"offdiag_v8_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[offdiag] wrote {RESULTS_DIR}/offdiag_v8_verdict_{slug}.json")


if __name__ == "__main__":
    main()
