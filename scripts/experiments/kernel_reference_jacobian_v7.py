#!/usr/bin/env python3
# register: SECOND-ORDER / CURVATURE (diag Hessian of LM loss wrt gate_proj)
"""Kernel-ref SECOND-ORDER read — is B in the CURVATURE? (s235 lead 2d prong 1c-ii).

B = composition (B f g x = f(g x)). The chain rule of a composition is a PRODUCT of
derivatives: d(f.g)/dx = f'(g x) * g'(x). Prong 1c read the FIRST-ORDER gradient
dL/d gate (kernel_reference_gradient_v6.py) and found B faint-positive but n.s.
(t=1.07) -- BUT the first-order gradient is a SINGLE factor / a sum over paths; it
washes out the PRODUCT structure that IS the chain rule. That product is a SECOND-ORDER
quantity. For L = l(f(g(z))) with z = the gate activation,

    dL/dz   = g'(z)^T f'(g)^T l'                 # first order  (v6 read this)
    d2L/dz2 = g'^T [f''(g) . l'] g'  +  (l'f') g''   # SECOND order

the curvature carries g'^T (...) g' -- a QUADRATIC FORM in g', i.e. the literal
product-of-derivatives chain-rule signature that the first-order gradient cannot show.
So if B = chain rule, B's natural home is the CURVATURE register, not the gradient.
Michael (s234): "could B be in the gradients instead of the topology?" -> 1c first-order
faint; 1c-ii is the PROPER order (the second).

Clean register-swap of prong 1c: same RelationalCrystalClassifier (sign-CMR, crosstask
null, raw-z Welch contrast), same calibrate->classify->discr_z pipeline, but the feature
is the DIAGONAL of the Hessian of the probe's LM loss w.r.t. the gate activation,
estimated by Hutchinson (diag(H)_a = E_v[v_a (H v)_a], v ~ Rademacher over the full set
of gate tensors -- cross-coord/cross-layer terms cancel in expectation). One HVP = a
double-backward of (g . v) where g = grad(CE, gates, create_graph=True). Pooled over
SUPERVISED positions (same locus as v6; the last token feeds only the unsupervised
next-token => its curvature row is ~0).

VERDICT LOGIC (lambda measure, two-sided):
  - B discriminates in the CURVATURE (sig on>off) where it was flat in EVERY activation
    register AND faint-n.s. in the first-order gradient -> B = compose = chain-rule
    CONFIRMED at the proper (second) order; the gap was a wrong-ORDER read, B lives in
    the product-of-derivatives. (Compare discr_z to the v6 gradient + v2 activation.)
  - B flat in the curvature too -> the gradient register is exhausted at BOTH orders; B
    is genuinely diffuse / order-only (prong 2 trace-order remains the sole path).
  - INSTRUMENT CHECK: {C,K,Y} must still discriminate in curvature (as in the gradient),
    else the second-order read is broken, not B-absent.

Usage:
    uv run python scripts/experiments/kernel_reference_jacobian_v7.py --smoke
    uv run python scripts/experiments/kernel_reference_jacobian_v7.py            # 14B

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


def forward_curvature(prompt, model, tok, torch_mod, layers, n_hutch):
    """Forward + double-backward; return ({li: diag(H) of LM CE wrt gate [T,d]}, n_tok).

    H = Hessian of the teacher-forced LM CE w.r.t. each gate_proj activation. Its
    diagonal is the SECOND-ORDER register-swap of v6's first-order gradient. Estimated
    by Hutchinson:  diag(H)_a = E_v[ v_a (H v)_a ],  v ~ Rademacher over ALL gate
    tensors; off-diagonal (cross-coord AND cross-layer) terms cancel: E[v_a v_b]=0 a!=b.
    Each HVP is a double-backward of the scalar (g . v), where g = the first-order
    grad taken with create_graph=True. Per-token rows returned (callers pool 0..n_tok-2;
    the last token feeds only the unsupervised next-token => curvature row ~0).
    """
    import torch.nn.functional as func
    store: dict[int, object] = {}

    def _cap(li):
        def _hook(_m, _inp, out):
            store[li] = out  # live graph tensor (NOT detached)
        return _hook

    handles = [model.model.layers[li].mlp.gate_proj.register_forward_hook(_cap(li))
               for li in layers]
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        out = model(**inputs)
        logits = out.logits[0]               # [T, V]
        ids = inputs["input_ids"][0]         # [T]
        t = ids.shape[0]
        ce = func.cross_entropy(logits[:-1, :], ids[1:], reduction="mean")
        gates = [store[li] for li in layers]
        grads = torch_mod.autograd.grad(ce, gates, create_graph=True)
        diag = [torch_mod.zeros_like(g) for g in grads]
        for k in range(n_hutch):
            vs = [(torch_mod.randint(0, 2, g.shape, device=g.device,
                                     dtype=torch_mod.float32) * 2 - 1).to(g.dtype)
                  for g in grads]
            gv = sum((gi * vi).sum() for gi, vi in zip(grads, vs, strict=True))
            hv = torch_mod.autograd.grad(gv, gates, retain_graph=(k < n_hutch - 1))
            for j in range(len(layers)):
                diag[j] = diag[j] + vs[j] * hv[j]
    finally:
        for h in handles:
            h.remove()
    result = {li: (diag[j] / n_hutch)[0].detach().float().cpu().numpy()
                  .astype(np.float64)
              for j, li in enumerate(layers)}
    return result, t


def pooled_supervised(curv_store, layers, n_tok):
    """Mean-pool diag(H) over supervised positions 0..n_tok-2 -> {li: [d]}."""
    sup = max(1, n_tok - 1)
    return {li: curv_store[li][:sup].mean(axis=0) for li in layers}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref 2nd-order curvature (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=25, help="calib probes/combinator")
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--n-hutch", type=int, default=4,
                        help="Hutchinson probe vectors for diag(H)")
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        heldout, ppc, n_perm, null_cap, n_hutch = 5, 5, 80, 150, 3
        print("[curv] SMOKE MODE")
    else:
        heldout, ppc, n_perm, null_cap, n_hutch = (
            args.heldout_per, args.ppc, args.n_perm, args.null_cap, args.n_hutch)

    calib, test = split_probes(heldout)
    kept, counts = [], Counter()
    for p in calib:
        if counts[p.combinator] < ppc:
            kept.append(p)
            counts[p.combinator] += 1
    calib = kept
    print(f"[curv] calib={len(calib)} test={len(test)} ppc={ppc} n_hutch={n_hutch}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    # ── calibration: per-probe POOLED curvature centroids ───────────────────────
    gate_by_layer: dict[int, list] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 25 == 0:
            print(f"[curv]   calib fwd+2bwd {i}/{len(calib)} ...")
        cstore, nt = forward_curvature(p.prompt, model, tok, torch_mod, layers, n_hutch)
        pooled = pooled_supervised(cstore, layers, nt)
        for li in layers:
            gate_by_layer[li].append(pooled[li])
        labels.append(p.combinator)
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels)

    # ── null: per-supervised-token curvature of natural text (many samples) ──────
    null_by_layer: dict[int, list] = {li: [] for li in layers}
    print(f"[curv] building curvature null ({len(BASELINE_NULL_SENTENCES)} prompts)")
    for s in BASELINE_NULL_SENTENCES:
        cstore, nt = forward_curvature(s, model, tok, torch_mod, layers, n_hutch)
        sup = max(1, nt - 1)
        for li in layers:
            null_by_layer[li].append(cstore[li][:sup])  # supervised rows
    null_np = {li: np.concatenate(null_by_layer[li], axis=0)[:null_cap]
               for li in layers}

    rcc = RelationalCrystalClassifier(layers, n_perm=n_perm, z_thresh=2.0,
                                      sil_z_thresh=2.0, consensus_gram="auto")
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    crystal_layers = rcc.crystal_layers
    print(f"[curv] crystal layers (curvature): {len(crystal_layers)}/{n_layers}")

    # ── read held-out prose: pooled-curvature pseudo-token -> per-layer z ────────
    cset = set(crystal_layers)
    per_probe = []
    for i, p in enumerate(test):
        if i % 25 == 0:
            print(f"[curv]   test fwd+2bwd {i}/{len(test)} ...")
        cstore, nt = forward_curvature(p.prompt, model, tok, torch_mod, layers, n_hutch)
        pooled = pooled_supervised(cstore, layers, nt)
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

    # ── discr_z(c): raw-z Welch contrast on the CURVATURE (mirror v6) ────────────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if on:
            discr_z[c] = welch_t(on, off)

    # per-layer profile (where in the stack does each op discriminate in curvature)
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
    b_in_curvature = bool(b.get("significant") and b.get("discr_z", 0) > 0)
    # instrument check: did the known-discriminable set survive the second-order read?
    instr = {c: bool(discr_z.get(c, {}).get("significant")
                     and discr_z.get(c, {}).get("discr_z", 0) > 0)
             for c in ("C", "K", "Y")}
    verdict = {
        "register": "curvature (diag Hessian LM CE wrt gate_proj, pooled supervised)",
        "n_hutch": n_hutch, "n_test": len(per_probe), "discr_z": discr_z,
        "peak_layer": peak, "b_discriminates_in_curvature": b_in_curvature,
        "instrument_works": instr,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    print("\n" + "═" * 74)
    print("KERNEL-REF SECOND-ORDER (CURVATURE) READ — is B in the chain-rule product?")
    print("═" * 74)
    print(f"  n_test={verdict['n_test']}  crystal_layers={len(crystal_layers)}"
          f"  n_hutch={n_hutch}")
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
    print(f"\n  instrument check (C/K/Y discriminate in curvature): {instr}")
    print(f"  ★ B discriminates in the CURVATURE register: "
          f"{b_in_curvature}  (B discr_z={b.get('discr_z')}, t={b.get('t')})")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_probe": per_probe,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"jacobian_v7_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "ppc": ppc, "heldout_per": heldout,
        "n_hutch": n_hutch, "n_calib": len(calib), "n_test": len(test),
        "register": "CURVATURE diag Hessian dL2/d gate_proj2, pooled supervised, "
                    "Hutchinson",
    }
    (RESULTS_DIR / f"jacobian_v7_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[curv] wrote {RESULTS_DIR}/jacobian_v7_verdict_{slug}.json")


if __name__ == "__main__":
    main()
