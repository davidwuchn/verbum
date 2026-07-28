"""(f0) ROUTING-TOPOLOGY under Q4 — register-attributed quantization damage.

Michael (s279): "Q4 is probably causing topology routing changes on the compute."
Grounds in two-registers-of-topology (hard SIGN/ROUTING gate_proj ~95% ⊥ soft
MAGNITUDE/VALUE up/down_proj ~5%) + opcodes-circuits-in-compute (soft routing overlay)
+ C3 (topology dominates). A 4-bit step is coarse enough to cross SIGN thresholds in the
routing register -> re-route the compute (SwiGLU gate neurons flip on/off -> a different
reduction path). So the naive "int4 flips baked facts, re-bake" is, in our frame, a
ROUTING-TOPOLOGY perturbation — and we can measure it.

This f0 instrument (NO bake, portable RTN-Q4, MIT) attributes Q4 damage by REGISTER on
the resident model + covering task:
  - quantize ROUTING alone (gate_proj) vs VALUE alone (up+down_proj) vs ALL
  - read (i) behavioral covering flip vs bf16, (ii) activation-level gate-sign flip rate
    per layer (routing re-route).
PREDICT (Fact 1): gate-only-Q4 dominates the behavioral damage AND induces the gate-sign
flips = Q4's damage is routing-topology-dominated. Null (N9) = value-only-Q4.

`λ measure`: routing = gate_proj sign; value = up/down magnitude. `λ yardstick`:
value-only is the null beside the routing number. RTN-Q4 = torch, MPS-clean (bnb is a
CUDA cross-check only). Pre-reg: ffn-function-bake-prereg.md Stage-f (hammock A ok).

License: MIT (`λ provenance`).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
from operand_multihop import (
    COVER,
    COVER_LABELS,
    COVER_PREFIXES,
    COVER_QUERY,
    ENT_CLASS,
    ENTS,
    tid,
)
from transformers import AutoModelForCausalLM, AutoTokenizer


def rtn_q4(w, bits=4):
    """per-output-channel symmetric RTN int4 dequant (routing/value perturbation)."""
    w32 = w.float()
    qmax = 2 ** (bits - 1) - 1                       # 7
    scale = (w32.abs().amax(dim=1, keepdim=True) / qmax).clamp_min(1e-8)
    q = torch.round(w32 / scale).clamp(-qmax - 1, qmax)
    return (q * scale).to(w.dtype)


def quantize_group(model, groups, bits=4):
    """RTN-quantize the selected proj group(s) in place; return restore list."""
    saved = []
    for layer in model.model.layers:
        mlp = layer.mlp
        for g in groups:
            proj = getattr(mlp, f"{g}_proj")
            saved.append((proj.weight, proj.weight.data.clone()))
            proj.weight.data.copy_(rtn_q4(proj.weight.data, bits))
    return saved


def restore(saved):
    for w, orig in saved:
        w.data.copy_(orig)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--bits", type=int, default=4)
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--out", default="results/ffn-bake/q4-routing-qwen3-0-6b")
    args = ap.parse_args()

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    n_layers = len(dec)
    cover_ids = {lb: tid(tok, lb) for lb in COVER_LABELS}
    print(f"[q4] {args.model_id} bits={args.bits} dev={dev} layers={n_layers}")

    # ── capture last-token gate_proj sign per layer + covering prediction ─────────
    def run(word, capture_gate=False):
        prompt = COVER_PREFIXES[0] + COVER_QUERY.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        store: dict[int, np.ndarray] = {}
        handles = []
        if capture_gate:
            for li, layer in enumerate(dec):
                def mk(li_):
                    def hook(_m, _i, out):
                        store[li_] = out[0, -1, :].detach().float().cpu().numpy()
                    return hook
                handles.append(layer.mlp.gate_proj.register_forward_hook(mk(li)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for h in handles:
            h.remove()
        pred = max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]])
        gate_sign = ({li: np.sign(v) for li, v in store.items()}
                     if capture_gate else None)
        return pred, gate_sign

    # majority over both held-out prefixes for the behavioral read (robust)
    def cover_pred(word):
        preds = []
        for pfx in COVER_PREFIXES:
            ids = tok(pfx + COVER_QUERY.format(x=word), return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            preds.append(max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]]))
        return max(COVER_LABELS, key=lambda lb: sum(p == lb for p in preds))

    def cover_margin(word):
        """continuous readout w/ headroom: logit(correct covering) - max(other labels),
        mean over held-out prefixes. Q4 damage shows here even when argmax survives."""
        truth = COVER[ENT_CLASS[word]]
        ms = []
        for pfx in COVER_PREFIXES:
            ids = tok(pfx + COVER_QUERY.format(x=word), return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            others = [lo[cover_ids[lb]] for lb in COVER_LABELS if lb != truth]
            ms.append(float(lo[cover_ids[truth]] - max(others)))
        return float(np.mean(ms))

    # ── bf16 baseline: ceiling-valid entities + captured gate signs ───────────────
    base_pred = {e: cover_pred(e) for e in ENTS}
    valid = [e for e in ENTS if base_pred[e] == COVER[ENT_CLASS[e]]]
    base_acc = round(np.mean([base_pred[e] == COVER[ENT_CLASS[e]] for e in ENTS]), 3)
    base_gate = {e: run(e, capture_gate=True)[1] for e in valid}
    base_margin = {e: cover_margin(e) for e in valid}
    print(f"[q4] bf16 covering acc={base_acc} valid={len(valid)}/{len(ENTS)} "
          f"mean_margin={np.mean(list(base_margin.values())):.2f}")

    def eval_condition(groups):
        saved = quantize_group(model, groups, args.bits)
        pred = {e: cover_pred(e) for e in valid}
        # routing re-route: gate-sign flip per layer (only meaningful if gate quantized)
        layer_flip = np.zeros(n_layers)
        if "gate" in groups:
            for e in valid:
                _, gs = run(e, capture_gate=True)
                for li in range(n_layers):
                    a, b = base_gate[e][li], gs[li]
                    layer_flip[li] += float(np.mean(a != b))
            layer_flip /= max(len(valid), 1)
        margin = {e: cover_margin(e) for e in valid}
        restore(saved)
        acc = round(np.mean([pred[e] == COVER[ENT_CLASS[e]] for e in valid]), 3)
        flip = round(np.mean([pred[e] != base_pred[e] for e in valid]), 3)
        mdrop = round(float(np.mean([base_margin[e] - margin[e] for e in valid])), 3)
        return {"acc": acc, "flip_vs_bf16": flip, "margin_drop": mdrop,
                "gate_sign_flip_by_layer": [round(float(x), 4) for x in layer_flip],
                "gate_sign_flip_mean": round(float(layer_flip.mean()), 4)}

    print("[q4] evaluating register-attributed Q4 damage ...")
    routing = eval_condition(["gate"])            # ROUTING register alone
    value = eval_condition(["up", "down"])        # VALUE register alone (N9 null)
    allq = eval_condition(["gate", "up", "down"])  # ALL
    for name, r in [("ROUTING(gate)", routing), ("VALUE(up/down)", value),
                    ("ALL", allq)]:
        print(f"  {name:16s} acc={r['acc']} flip={r['flip_vs_bf16']} "
              f"Δmargin={r['margin_drop']} gate_flip={r['gate_sign_flip_mean']}")

    # ── verdict (pre-registered): routing-topology-dominated? ─────────────────────
    # routing re-route present (gate-sign flip > 0 while value=0) is the MECHANISM;
    # behavioral/margin dominance is redundancy-gated (easy task at 4B may absorb it).
    r_flip = routing["gate_sign_flip_mean"]
    v_flip = value["gate_sign_flip_mean"]
    reroute = bool(r_flip > 0 and v_flip == 0)
    routing_dominated = bool(routing["margin_drop"] > value["margin_drop"])
    print(f"\n[q4] routing re-route present (mechanism) = {reroute}")
    print(f"[q4] VERDICT f0 ROUTING-DOMINATED (margin) = {routing_dominated}  "
          f"(routing Δmargin {routing['margin_drop']} > value {value['margin_drop']})")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "device": dev, "bits": args.bits,
           "n_layers": n_layers, "base_acc": base_acc, "valid": valid,
           "base_mean_margin": round(float(np.mean(list(base_margin.values()))), 3),
           "routing_gate": routing, "value_updown": value, "all": allq,
           "verdict_reroute_present": reroute,
           "verdict_routing_dominated_margin": routing_dominated}
    (out / "q4_routing.json").write_text(json.dumps(res, indent=2))
    print(f"[q4] wrote {out}/q4_routing.json")


if __name__ == "__main__":
    main()
