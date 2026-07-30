"""(f2) R5 MECHANISM — baked-operand Q4 fragility as a ROUTING-TOPOLOGY change.

Pre-reg: ffn-function-bake-prereg.md Stage-f (f2 design freeze, s280 — thresholds
FROZEN before this run). f0 showed Q4 re-routes the ROUTING register (gate signs flip
mid-stack; value-Q4 flips exactly 0) but the easy LEARNED covering absorbs the re-route
at 4B (redundancy-gating). f1 graduated the operand hook -> ONE appended MLP recognition
neuron (E1 pass). f2 asks the R5 question: quantize the BAKED model and attribute the
installed operand's fragility BY REGISTER and BY LOCUS.

  conditions (all read vs the bf16-baked reference, NOT truth — isolates quant damage
  from the inherited mammal weak cell):
    bf16        — reference (= f1)
    slot_q4     — quantize ONLY the appended slot (key row + payload col)
    routing_q4  — RTN-Q4 every layer's RESIDENT gate_proj (slot row bf16)
    value_q4    — RTN-Q4 every layer's RESIDENT up/down_proj (slot col bf16)   [N9]
    all_q4      — resident routing+value + slot

  reads per condition:
    installed  = baked-nonce covering flip vs bf16-baked   (non-redundant target)
    learned    = native covering flip, no slot             (redundant control)
    mechanism  = gate-sign flip rate/layer (f0 instrument; measured under ALL
                 conditions — value must give the measured 0)
    locus      = slot pre-activation z at the nonce slot (key-misfire vs
                 downstream-re-route discriminator; fires iff z >= 0.5*target_z)

SERIALIZATION GATE (first): uniform-E expansion (+1 zero neuron on EVERY layer, real
slot at L) -> config.intermediate_size += 1 -> save_pretrained -> STOCK reload -> same
predictions (nonce, decoy inert, real word unharmed). Closes f1's "in-memory edit"
honest edge; the checkpoint is the f3 substrate. Attn/embeddings stay bf16 (register
attribution, not full-export simulation); the slot col is quantized with its own scale
(attribution-clean; a shared-row-grid export differs negligibly).

`lambda measure`: routing = gate sign; value = payload/dose; slot z names the LOCUS.
`lambda yardstick`: value_q4 = the null beside routing_q4; native learned = the null
beside installed; margin reported never gated (f0 value-magnitude confound).

License: MIT (`lambda provenance`; SuperBake = method reference only, no license).
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from operand_multihop import (
    COVER,
    COVER_LABELS,
    COVER_PREFIXES,
    COVER_QUERY,
    ENT_CLASS,
    ENTS,
    FRAMES,
    NONCE,
    tid,
)
from transformers import AutoModelForCausalLM, AutoTokenizer

DECOY = "blorf"
REAL_WORD = "wolf"
PROJS = ("gate_proj", "up_proj", "down_proj")


def rtn_q4(w, bits=4):
    """per-output-channel symmetric RTN int4 dequant (f0 instrument, unchanged)."""
    w32 = w.float()
    qmax = 2 ** (bits - 1) - 1                       # 7
    scale = (w32.abs().amax(dim=1, keepdim=True) / qmax).clamp_min(1e-8)
    q = torch.round(w32 / scale).clamp(-qmax - 1, qmax)
    return (q * scale).to(w.dtype)


def rtn_vec(v, bits=4):
    """one shared scale for a single appended slot row/col."""
    return rtn_q4(v.reshape(1, -1), bits).reshape(v.shape)


def quantize_group(model, groups, bits=4):
    """RTN-quantize resident proj group(s) in place; return restore list (f0)
    + WEIGHT-level sign-flip fraction per group (the register-clean routing read:
    value-Q4 changes 0 gate weights BY DEFINITION; activation-level gate flips
    can cascade from either register — s280 smoke correction to f0 finding #1)."""
    saved = []
    wflip: dict[str, list[float]] = {g: [] for g in groups}
    for layer in model.model.layers:
        mlp = layer.mlp
        for g in groups:
            proj = getattr(mlp, f"{g}_proj")
            saved.append((proj.weight, proj.weight.data.clone()))
            old = proj.weight.data
            new = rtn_q4(old, bits)
            nz = old != 0
            wflip[g].append(float(
                (torch.sign(new[nz]) != torch.sign(old[nz])).float().mean()))
            proj.weight.data.copy_(new)
    return saved, {g: round(float(np.mean(v)), 5) for g, v in wflip.items()}


def restore(saved):
    for w, orig in saved:
        w.data.copy_(orig)


def cap_out(store, key):
    def hook(_m, _i, out):
        h = out[0] if isinstance(out, tuple) else out
        store[key] = h.detach().float().cpu().numpy()
    return hook


def cap_mlp_in(store, key):
    def pre(_m, inp):
        store[key] = inp[0].detach().float().cpu().numpy()
    return pre


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--target-z", type=float, default=6.0)
    ap.add_argument("--bits", type=int, default=4)
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--smoke", action="store_true", help="one entity only")
    ap.add_argument("--skip-save", action="store_true",
                    help="skip the serialization gate (ckpt save + stock reload)")
    ap.add_argument("--ckpt-dir", default="checkpoints/operand-bake-qwen3-4b")
    ap.add_argument("--out", default="results/ffn-bake/operand-quant-qwen3-4b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    n_layers = len(dec)
    mlp = dec[L].mlp
    cover_ids = {lb: tid(tok, lb) for lb in COVER_LABELS}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[f2] {args.model_id} L={L} scale={args.scale} target_z={args.target_z} "
          f"bits={args.bits} dev={dev} layers={n_layers}")

    def find_slot(ids_list, tok_id):
        idx = [i for i, t in enumerate(ids_list) if t == tok_id]
        return idx[-1] if idx else len(ids_list) - 1

    def cover_pred(word, mdl=None):
        m = mdl if mdl is not None else model
        preds = []
        for pfx in COVER_PREFIXES:
            ids = tok(pfx + COVER_QUERY.format(x=word), return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = m(**ids).logits[0, -1, :].float().cpu().numpy()
            preds.append(max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]]))
        return max(COVER_LABELS, key=lambda lb: sum(p == lb for p in preds))

    def gate_signs(word):
        """per-layer last-token gate_proj sign (resident channels only; f0 read)."""
        ids = tok(COVER_PREFIXES[0] + COVER_QUERY.format(x=word),
                  return_tensors="pt").to(dev)
        store: dict[int, np.ndarray] = {}
        handles = []
        for li, layer in enumerate(dec):
            def mk(li_):
                def hook(_m, _i, out):
                    store[li_] = out[0, -1, :].detach().float().cpu().numpy()
                return hook
            handles.append(layer.mlp.gate_proj.register_forward_hook(mk(li)))
        with torch.no_grad():
            model(**ids)
        for h in handles:
            h.remove()
        # resident width only (slot never appended when this runs, but be safe)
        return {li: np.sign(v[:orig_inter[li]]) for li, v in store.items()}

    orig_inter = [dec[li].mlp.gate_proj.weight.shape[0] for li in range(n_layers)]

    def nonce_read(truth):
        """baked-nonce covering pred + slot z (prefix 0) + truth margin."""
        preds, margins, zval = [], [], None
        for j, pfx in enumerate(COVER_PREFIXES):
            ids = tok(pfx + COVER_QUERY.format(x=NONCE), return_tensors="pt").to(dev)
            handles = []
            st: dict = {}
            if j == 0:
                pos = find_slot(ids.input_ids[0].tolist(), nonce_last)

                def zh(_m, _i, out, st=st, pos=pos):
                    st["z"] = float(out[0, pos, -1])
                handles.append(mlp.gate_proj.register_forward_hook(zh))
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            for h in handles:
                h.remove()
            if j == 0:
                zval = st["z"]
            preds.append(max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]]))
            others = [lo[cover_ids[lb]] for lb in COVER_LABELS if lb != truth]
            margins.append(float(lo[cover_ids[truth]] - max(others)))
        pred = max(COVER_LABELS, key=lambda lb: sum(p == lb for p in preds))
        return pred, zval, float(np.mean(margins))

    # ── d_E per entity (payload; layer-L OUTPUT, object token) — f1 unchanged ─────
    def decl(fr, obj):
        s, v = fr
        return f"{s} {v} a {obj}."

    per_e = {e: [] for e in ENTS}
    for fr in FRAMES:
        for e in ENTS:
            st: dict = {}
            h = dec[L].register_forward_hook(cap_out(st, "o"))
            ids = tok(decl(fr, e), return_tensors="pt").to(dev)
            with torch.no_grad():
                model(**ids)
            h.remove()
            per_e[e].append(st["o"][0, -2, :])
    e_mean = {e: np.mean(per_e[e], axis=0) for e in ENTS}
    g_mean = np.mean([e_mean[e] for e in ENTS], axis=0)
    d_E = {e: e_mean[e] - g_mean for e in ENTS}

    # ── KEY: nonce MLP-input signature ⟂ carrier (f1 unchanged) ───────────────────
    nonce_x, innocent_x = [], []
    for pfx in COVER_PREFIXES:
        ids = tok(pfx + COVER_QUERY.format(x=NONCE), return_tensors="pt").to(dev)
        st = {}
        h = mlp.register_forward_pre_hook(cap_mlp_in(st, "i"))
        with torch.no_grad():
            model(**ids)
        h.remove()
        pos = find_slot(ids.input_ids[0].tolist(), nonce_last)
        nonce_x.append(st["i"][0, pos, :])
        innocent_x.append(st["i"][0])
    for fr in FRAMES[:4]:
        ids = tok(decl(fr, "eagle"), return_tensors="pt").to(dev)
        st = {}
        h = mlp.register_forward_pre_hook(cap_mlp_in(st, "i"))
        with torch.no_grad():
            model(**ids)
        h.remove()
        innocent_x.append(st["i"][0])
    m_nonce = np.mean(nonce_x, axis=0)
    mu = np.mean(np.concatenate(innocent_x, axis=0), axis=0)
    mu_hat = mu / (np.linalg.norm(mu) + 1e-9)
    k_raw = m_nonce - mu
    k = k_raw - (k_raw @ mu_hat) * mu_hat
    k = k / (np.linalg.norm(k) + 1e-9)
    kx = float(k @ (m_nonce - mu))
    beta = args.target_z / (kx if abs(kx) > 1e-6 else 1e-6)
    z_t = args.target_z
    m_mag = float(F.silu(torch.tensor(z_t)) * z_t)
    print(f"[f2] key⟂carrier: kx={kx:.3f} beta={beta:.3f} m_mag={m_mag:.3f}")

    # ── bake/unbake against CURRENT (possibly resident-quantized) weights ─────────
    def bake(payload, key_vec, quant_slot=False):
        base = {n: getattr(mlp, n).weight.data.clone() for n in PROJS}
        row = torch.tensor(beta * key_vec, dtype=model.dtype, device=dev).unsqueeze(0)
        col = torch.tensor(payload / m_mag, dtype=model.dtype,
                           device=dev).unsqueeze(1)
        if quant_slot:
            row = rtn_vec(row, args.bits)
            col = rtn_vec(col, args.bits)
        for n in ("gate_proj", "up_proj"):
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(torch.cat([base[n], row], dim=0))
            proj.out_features += 1
        dp = mlp.down_proj
        dp.weight = nn.Parameter(torch.cat([base["down_proj"], col], dim=1))
        dp.in_features += 1
        return base

    def unbake(base):
        for n in PROJS:
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(base[n])
        mlp.gate_proj.out_features -= 1
        mlp.up_proj.out_features -= 1
        mlp.down_proj.in_features -= 1

    # ── bf16 baseline: valid entities + native preds + gate signs ─────────────────
    base_native = {e: cover_pred(e) for e in ENTS}
    valid = [e for e in ENTS if base_native[e] == COVER[ENT_CLASS[e]]]
    ents = ["eagle"] if args.smoke else valid
    base_gate = {e: gate_signs(e) for e in valid}
    base_decoy = cover_pred(DECOY)
    print(f"[f2] bf16 native valid={len(valid)}/{len(ENTS)} "
          f"baseline decoy={base_decoy}; testing {len(ents)} entities")

    # ── SERIALIZATION GATE (uniform-E → save → stock reload) ──────────────────────
    ser = {"skipped": True}
    if not args.skip_save:
        e0 = "eagle"
        base = bake(d_E[e0] * args.scale, k, quant_slot=False)
        pred_mem, z_mem, _ = nonce_read(COVER[ENT_CLASS[e0]])
        decoy_mem = cover_pred(DECOY)
        zero_saved = []
        for li, layer in enumerate(dec):
            if li == L:
                continue
            m2 = layer.mlp
            for n in ("gate_proj", "up_proj"):
                p = getattr(m2, n)
                w = p.weight.data
                zero_saved.append((m2, n, w))
                zrow = torch.zeros(1, w.shape[1], dtype=model.dtype, device=dev)
                p.weight = nn.Parameter(torch.cat([w, zrow], dim=0))
                p.out_features += 1
            dp = m2.down_proj
            w = dp.weight.data
            zero_saved.append((m2, "down_proj", w))
            zcol = torch.zeros(w.shape[0], 1, dtype=model.dtype, device=dev)
            dp.weight = nn.Parameter(torch.cat([w, zcol], dim=1))
            dp.in_features += 1
        model.config.intermediate_size += 1
        ckpt = Path(args.ckpt_dir)
        model.save_pretrained(ckpt)
        tok.save_pretrained(ckpt)
        print(f"[f2] saved uniform-E baked ckpt → {ckpt}")
        for m2, n, w in zero_saved:
            p = getattr(m2, n)
            p.weight = nn.Parameter(w)
            if n == "down_proj":
                p.in_features -= 1
            else:
                p.out_features -= 1
        model.config.intermediate_size -= 1
        unbake(base)
        rel = AutoModelForCausalLM.from_pretrained(
            ckpt, dtype=getattr(torch, args.dtype)).to(dev).eval()
        pred_rel = cover_pred(NONCE, mdl=rel)
        decoy_rel = cover_pred(DECOY, mdl=rel)
        wolf_rel = cover_pred(REAL_WORD, mdl=rel)
        del rel
        if dev == "mps":
            torch.mps.empty_cache()
        ok = bool(pred_rel == pred_mem and decoy_rel == decoy_mem
                  and wolf_rel == COVER[ENT_CLASS[REAL_WORD]])
        ser = {"skipped": False, "entity": e0, "pred_in_memory": pred_mem,
               "pred_reloaded": pred_rel, "decoy_in_memory": decoy_mem,
               "decoy_reloaded": decoy_rel, "real_word_reloaded": wolf_rel,
               "z_in_memory": round(z_mem, 3), "verdict_SERIALIZED": ok}
        print(f"[f2] SERIALIZED={ok} (mem={pred_mem} reload={pred_rel} "
              f"decoy={decoy_rel} wolf={wolf_rel})")

    # ── condition sweep ───────────────────────────────────────────────────────────
    conds = [("bf16", [], False), ("slot_q4", [], True),
             ("routing_q4", ["gate"], False), ("value_q4", ["up", "down"], False),
             ("all_q4", ["gate", "up", "down"], True)]
    results: dict[str, dict] = {}
    bf16_baked: dict[str, str] = {}
    for name, groups, quant_slot in conds:
        saved, wflip = (quantize_group(model, groups, args.bits)
                        if groups else ([], {}))
        native = {e: cover_pred(e) for e in valid}
        layer_flip = np.zeros(n_layers)
        for e in valid:
            gs = gate_signs(e)
            for li in range(n_layers):
                layer_flip[li] += float(np.mean(base_gate[e][li] != gs[li]))
        layer_flip /= max(len(valid), 1)
        cells = {}
        for e in ents:
            b = bake(d_E[e] * args.scale, k, quant_slot=quant_slot)
            pred, zv, marg = nonce_read(COVER[ENT_CLASS[e]])
            unbake(b)
            cells[e] = {"pred": pred, "truth": COVER[ENT_CLASS[e]],
                        "z": round(zv, 3), "margin": round(marg, 3)}
        restore(saved)
        if name == "bf16":
            bf16_baked = {e: cells[e]["pred"] for e in ents}
        inst_flip = round(float(np.mean(
            [cells[e]["pred"] != bf16_baked[e] for e in ents])), 3)
        inst_acc = round(float(np.mean(
            [cells[e]["pred"] == cells[e]["truth"] for e in ents])), 3)
        nat_flip = round(float(np.mean(
            [native[e] != base_native[e] for e in valid])), 3)
        nat_acc = round(float(np.mean(
            [native[e] == COVER[ENT_CLASS[e]] for e in valid])), 3)
        z_mean = round(float(np.mean([cells[e]["z"] for e in ents])), 3)
        fired = round(float(np.mean(
            [cells[e]["z"] >= 0.5 * z_t for e in ents])), 3)
        results[name] = {
            "installed_flip_vs_bf16baked": inst_flip, "installed_acc": inst_acc,
            "native_flip_vs_bf16": nat_flip, "native_acc": nat_acc,
            "slot_z_mean": z_mean, "slot_fired_frac": fired,
            "margin_mean": round(float(np.mean(
                [cells[e]["margin"] for e in ents])), 3),
            "gate_sign_flip_mean": round(float(layer_flip.mean()), 4),
            "gate_sign_flip_by_layer": [round(float(x), 4) for x in layer_flip],
            "weight_sign_flip": wflip, "cells": cells}
        print(f"  {name:11s} inst_flip={inst_flip} inst_acc={inst_acc} "
              f"nat_flip={nat_flip} nat_acc={nat_acc} z={z_mean} fired={fired} "
              f"gate_flip={results[name]['gate_sign_flip_mean']}")

    # ── frozen verdicts ───────────────────────────────────────────────────────────
    r_all, r_rt, r_vl, r_sl = (results["all_q4"], results["routing_q4"],
                               results["value_q4"], results["slot_q4"])
    fragile = bool(r_all["installed_flip_vs_bf16baked"]
                   >= r_all["native_flip_vs_bf16"] + 0.10)
    # strict = as first frozen (s280); its `value gate_flip == 0` clause encoded an
    # f0 instrument artifact (f0 never measured the value condition's activation
    # cascade — zeros by construction). AMENDED (pre-run, documented in pre-reg):
    # drop that clause; the register-clean value-side statement is WEIGHT-level
    # (value-Q4 changes 0 gate weights by definition, see weight_sign_flip).
    routing_mech_strict = bool(
        r_rt["installed_flip_vs_bf16baked"] >= r_vl["installed_flip_vs_bf16baked"]
        and r_rt["gate_sign_flip_mean"] > 0 and r_vl["gate_sign_flip_mean"] == 0
        and r_rt["slot_z_mean"] >= 0.5 * z_t)
    routing_mech = bool(
        r_rt["installed_flip_vs_bf16baked"] >= r_vl["installed_flip_vs_bf16baked"]
        and r_rt["gate_sign_flip_mean"] > 0
        and r_rt["slot_z_mean"] >= 0.5 * z_t)
    slot_local = bool(r_sl["installed_flip_vs_bf16baked"]
                      >= r_all["installed_flip_vs_bf16baked"] - 0.05)
    print(f"\n[f2] VERDICT R5-FRAGILE-INSTALLED = {fragile}")
    print(f"[f2] VERDICT R5-ROUTING-MECHANISM = {routing_mech} "
          f"(strict-as-first-frozen = {routing_mech_strict})")
    print(f"[f2] VERDICT SLOT-LOCAL (alt)     = {slot_local}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "layer": L, "scale": args.scale,
           "target_z": z_t, "bits": args.bits, "device": dev, "n_layers": n_layers,
           "nonce": NONCE, "decoy": DECOY, "n_entities": len(ents),
           "valid": valid, "serialization": ser, "conditions": results,
           "verdict_R5_FRAGILE_INSTALLED": fragile,
           "verdict_R5_ROUTING_MECHANISM": routing_mech,
           "verdict_R5_ROUTING_MECHANISM_strict_first_frozen": routing_mech_strict,
           "verdict_SLOT_LOCAL": slot_local}
    (out / "operand_quant.json").write_text(json.dumps(res, indent=2))
    print(f"[f2] wrote {out}/operand_quant.json")


if __name__ == "__main__":
    main()
