#!/usr/bin/env python3
# register: GRADIENT (dL/d gate_proj, routing coords)
"""Kernel-ref GRADIENT-register read — is B in the gradients? (s234 lead 2d prong 1c).

B = composition (B f g x = f(g x)). Composition in the BACKWARD pass IS the chain rule
(d(f.g)/dx = f'(g x)*g'(x) = a PRODUCT of derivatives). So B's natural home may be the
GRADIENT, not the forward activation TOPOLOGY — explaining why prongs 1/1b/1b-ii/1b-iii
found B flat in EVERY activation register (FFN gate, attn-summed, per-head OV) while
C/I/K/Y (static rewirings) read fine. Michael (s234): "could B be in the gradients
instead of the topology?"

Clean register-swap of prong 1: same RelationalCrystalClassifier (sign-CMR, crosstask
null, raw-z Welch contrast), but the feature is the GRADIENT of the probe's LM loss
w.r.t. the gate activation, NOT the activation. Pattern from gd_gradient_shadow.py
(validated): teacher-forced LM CE -> torch.autograd.grad(loss, [gate]) -> MEAN-POOL over
SUPERVISED positions (the last token feeds only the unsupervised next-token => grad 0
there; pool 0..len-2, nonzero AND denoises sqrt(N)).

VERDICT LOGIC (λ measure, two-sided):
  • B discriminates in the GRADIENT (sig on>off) where it was flat in all activation
    registers -> B=compose=chain-rule CONFIRMED; the gap was a wrong-register read, B
    lives in the backward pass. (Compare discr_z to the v2 activation table.)
  • B flat in the gradient too -> the gradient register is also exhausted; B is
    genuinely diffuse / order-only (prong 2 trace-order remains).

Usage:
    uv run python scripts/experiments/kernel_reference_gradient_v6.py --smoke
    uv run python scripts/experiments/kernel_reference_gradient_v6.py --register

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


def forward_grad(prompt, model, tok, torch_mod, layers):
    """Forward+backward; return ({li: dL/d gate [T, d]}, n_tokens). NOT under no_grad.

    L = teacher-forced LM CE on the probe's own tokens (predict t+1 from t). The last
    token (len-1) feeds only the unsupervised next-token => its grad row is ~0; callers
    pool over supervised positions 0..len-2.
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
        grads = torch_mod.autograd.grad(ce, [store[li] for li in layers])
    finally:
        for h in handles:
            h.remove()
    result = {li: g[0].detach().float().cpu().numpy().astype(np.float64)
              for li, g in zip(layers, grads, strict=True)}
    return result, t


def pooled_supervised(grad_store, layers, n_tok):
    """Mean-pool dL/d gate over supervised positions 0..n_tok-2 -> {li: [d]}."""
    sup = max(1, n_tok - 1)
    return {li: grad_store[li][:sup].mean(axis=0) for li in layers}


def main() -> None:
    parser = argparse.ArgumentParser(description="Kernel-ref gradient read (B)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--heldout-per", type=int, default=20)
    parser.add_argument("--ppc", type=int, default=25, help="calib probes/combinator")
    parser.add_argument("--null-cap", type=int, default=300)
    parser.add_argument("--n-perm", type=int, default=200)
    parser.add_argument("--smoke", action="store_true")
    args = parser.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        heldout, ppc, n_perm, null_cap = 5, 5, 80, 150
        print("[grad] SMOKE MODE")
    else:
        heldout, ppc, n_perm, null_cap = (args.heldout_per, args.ppc, args.n_perm,
                                          args.null_cap)

    calib, test = split_probes(heldout)
    kept, counts = [], Counter()
    for p in calib:
        if counts[p.combinator] < ppc:
            kept.append(p)
            counts[p.combinator] += 1
    calib = kept
    print(f"[grad] calib={len(calib)} test={len(test)} ppc={ppc}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    # ── calibration: per-probe POOLED gradient centroids ─────────────────────────
    gate_by_layer: dict[int, list] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(calib):
        if i % 25 == 0:
            print(f"[grad]   calib fwd+bwd {i}/{len(calib)} ...")
        gstore, nt = forward_grad(p.prompt, model, tok, torch_mod, layers)
        pooled = pooled_supervised(gstore, layers, nt)
        for li in layers:
            gate_by_layer[li].append(pooled[li])
        labels.append(p.combinator)
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels)

    # ── null: per-supervised-token gradients of natural text (many samples) ──────
    null_by_layer: dict[int, list] = {li: [] for li in layers}
    print(f"[grad] building gradient null ({len(BASELINE_NULL_SENTENCES)} prompts)")
    for s in BASELINE_NULL_SENTENCES:
        gstore, nt = forward_grad(s, model, tok, torch_mod, layers)
        sup = max(1, nt - 1)
        for li in layers:
            null_by_layer[li].append(gstore[li][:sup])  # supervised rows
    null_np = {li: np.concatenate(null_by_layer[li], axis=0)[:null_cap]
               for li in layers}

    rcc = RelationalCrystalClassifier(layers, n_perm=n_perm, z_thresh=2.0,
                                      sil_z_thresh=2.0, consensus_gram="auto")
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    crystal_layers = rcc.crystal_layers
    print(f"[grad] crystal layers (gradient): {len(crystal_layers)}/{n_layers}")

    # ── read held-out prose: pooled-gradient pseudo-token -> per-layer z ─────────
    cset = set(crystal_layers)
    per_probe = []
    for i, p in enumerate(test):
        if i % 25 == 0:
            print(f"[grad]   test fwd+bwd {i}/{len(test)} ...")
        gstore, nt = forward_grad(p.prompt, model, tok, torch_mod, layers)
        pooled = pooled_supervised(gstore, layers, nt)
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

    # ── discr_z(c): raw-z Welch contrast on the GRADIENT (mirror v2) ─────────────
    discr_z: dict[str, dict] = {}
    for c in CRYSTAL:
        on = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] == c]
        off = [r["layer_avg_z"][c] for r in per_probe if r["combinator"] != c]
        if on:
            discr_z[c] = welch_t(on, off)

    # per-layer profile (where in the stack does each op discriminate in the gradient)
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
    b_in_gradient = bool(b.get("significant") and b.get("discr_z", 0) > 0)
    verdict = {
        "register": "gradient (dL/d gate_proj, pooled over supervised)",
        "n_test": len(per_probe), "discr_z": discr_z, "peak_layer": peak,
        "b_discriminates_in_gradient": b_in_gradient,
        "n_discr_z_significant": sum(
            1 for c in CRYSTAL if discr_z.get(c, {}).get("significant")
            and discr_z.get(c, {}).get("discr_z", 0) > 0),
    }

    print("\n" + "═" * 74)
    print("KERNEL-REF GRADIENT-REGISTER READ — is B in the gradients?")
    print("═" * 74)
    print(f"  n_test={verdict['n_test']}  crystal_layers={len(crystal_layers)}")
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
    print(f"\n  ★ B discriminates in the GRADIENT register: "
          f"{b_in_gradient}  (B discr_z={b.get('discr_z')}, t={b.get('t')})")
    print("═" * 74 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    out = {"verdict": verdict, "per_probe": per_probe,
           "crystal_layers": crystal_layers}
    (RESULTS_DIR / f"gradient_v6_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "n_layers": n_layers, "n_perm": n_perm, "ppc": ppc, "heldout_per": heldout,
        "n_calib": len(calib), "n_test": len(test),
        "register": "GRADIENT dL/d gate_proj, pooled over supervised positions",
    }
    (RESULTS_DIR / f"gradient_v6_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[grad] wrote {RESULTS_DIR}/gradient_v6_verdict_{slug}.json")


if __name__ == "__main__":
    main()
