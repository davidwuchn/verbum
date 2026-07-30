"""(f3) ARTIFACT-SHIPS — the slot as a ternary MIRROR STACK; survives resident Q4.

Pre-reg: ffn-function-bake-prereg.md Stage-f (f3 design freeze, s280 — gates FROZEN
before this run). f2 localized the installed operand's Q4 fragility to the VALUE
register (payload dose; routing quant harmless, key read robust). f3 is the ships
gate: encode the slot as greedy residual balanced-ternary plates (TWN form)

    t_k = sign(r) * 1(|r| > 0.7*mean|r|),  alpha_k = mean|r| over active (= lsq),
    r <- r - alpha_k * t_k,   materialized weight = sum_k alpha_k * t_k

(`recursion-mirrors` additive-plate semantics: the artifact stores ternary plates +
per-plate scale, runtime sums them; bits/weight = K*log2(3) ~ 1.58K, K=3 ~ Q4-Q5).
Both slot vectors ternarized (key row + payload col = the fully-ternary slot).
Bake-time calibration folded into plate scales (key recon rescaled to z=target_z on
the nonce signature; payload recon rescaled to the original col norm) — applied to
ALL depths including the K=1 null, so only DIRECTION error separates depths.

Cells: slot in {bf16, K1 (N10 sign-only floor), K2, K3} x resident in {bf16, allQ4};
reads as f2 (installed pred vs the bf16/bf16 reference, slot z, margin, recon_cos).
NEW cell bf16-slot x allQ4-resident = the ceiling any mirror slot can reach in the
quantized environment (f2 never measured it; the mirror is judged against THIS,
never against bf16/bf16 — the resident damage is environmental).

`lambda yardstick` (frozen): PARITY / SURVIVES-Q4 / BEATS-N10 / ARTIFACT-SHIPS —
see pre-reg. Predict: K=1 loses cells to direction error, K>=2 recovers to parity.

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

PROJS = ("gate_proj", "up_proj", "down_proj")


def rtn_q4(w, bits=4):
    """per-output-channel symmetric RTN int4 dequant (f0/f2 instrument)."""
    w32 = w.float()
    qmax = 2 ** (bits - 1) - 1
    scale = (w32.abs().amax(dim=1, keepdim=True) / qmax).clamp_min(1e-8)
    q = torch.round(w32 / scale).clamp(-qmax - 1, qmax)
    return (q * scale).to(w.dtype)


def quantize_group(model, groups, bits=4):
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


def mirror(v, depth):
    """greedy residual balanced-ternary plates (TWN); return recon + cos."""
    r = v.astype(np.float64).copy()
    recon = np.zeros_like(r)
    for _ in range(depth):
        a = np.abs(r)
        delta = 0.7 * a.mean()
        t = np.where(a > delta, np.sign(r), 0.0)
        act = a[a > delta]
        alpha = float(act.mean()) if act.size else 0.0
        recon += alpha * t
        r -= alpha * t
    denom = (np.linalg.norm(v) * np.linalg.norm(recon)) or 1e-9
    return recon, float(v @ recon / denom)


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
    ap.add_argument("--out", default="results/ffn-bake/operand-mirror-qwen3-4b")
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
    print(f"[f3] {args.model_id} L={L} scale={args.scale} target_z={args.target_z} "
          f"bits={args.bits} dev={dev} layers={n_layers}")

    def find_slot(ids_list, tok_id):
        idx = [i for i, t in enumerate(ids_list) if t == tok_id]
        return idx[-1] if idx else len(ids_list) - 1

    def cover_pred(word):
        preds = []
        for pfx in COVER_PREFIXES:
            ids = tok(pfx + COVER_QUERY.format(x=word), return_tensors="pt").to(dev)
            with torch.no_grad():
                lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
            preds.append(max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]]))
        return max(COVER_LABELS, key=lambda lb: sum(p == lb for p in preds))

    def nonce_read(truth):
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

    # ── d_E + key construction (f1/f2 unchanged) ──────────────────────────────────
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
    sig = m_nonce - mu                                   # nonce signature (for calib)
    print(f"[f3] key⟂carrier: kx={kx:.3f} beta={beta:.3f} m_mag={m_mag:.3f}")

    # ── slot variants: bf16 vs ternary mirror depth K (calibrated) ────────────────
    row_bf16 = beta * k

    def key_row(depth):
        """ternary key row, rescaled so z(nonce signature) = target_z (calib
        folds into plate scales; float never stored)."""
        if depth is None:
            return row_bf16, 1.0
        recon, cos = mirror(row_bf16, depth)
        zr = float(recon @ sig)
        recon = recon * (z_t / (zr if abs(zr) > 1e-6 else 1e-6))
        return recon, cos

    def payload_col(e, depth):
        """ternary payload col, rescaled to the original col norm."""
        col = d_E[e] * args.scale / m_mag
        if depth is None:
            return col, 1.0
        recon, cos = mirror(col, depth)
        nr = np.linalg.norm(recon)
        recon = recon * (np.linalg.norm(col) / (nr if nr > 1e-9 else 1e-9))
        return recon, cos

    def bake(row, col):
        base = {n: getattr(mlp, n).weight.data.clone() for n in PROJS}
        rt = torch.tensor(row, dtype=model.dtype, device=dev).unsqueeze(0)
        ct = torch.tensor(col, dtype=model.dtype, device=dev).unsqueeze(1)
        for n in ("gate_proj", "up_proj"):
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(torch.cat([base[n], rt], dim=0))
            proj.out_features += 1
        dp = mlp.down_proj
        dp.weight = nn.Parameter(torch.cat([base["down_proj"], ct], dim=1))
        dp.in_features += 1
        return base

    def unbake(base):
        for n in PROJS:
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(base[n])
        mlp.gate_proj.out_features -= 1
        mlp.up_proj.out_features -= 1
        mlp.down_proj.in_features -= 1

    # ── valid entities (bf16 native ceiling) ──────────────────────────────────────
    base_native = {e: cover_pred(e) for e in ENTS}
    valid = [e for e in ENTS if base_native[e] == COVER[ENT_CLASS[e]]]
    ents = ["eagle"] if args.smoke else valid
    print(f"[f3] bf16 native valid={len(valid)}/{len(ENTS)}; "
          f"testing {len(ents)} entities")

    # ── 8-cell sweep ──────────────────────────────────────────────────────────────
    residents = [("bf16_res", []), ("allq4_res", ["gate", "up", "down"])]
    slots = [("bf16", None), ("K1", 1), ("K2", 2), ("K3", 3)]
    cells: dict[str, dict] = {}
    ref_preds: dict[str, str] = {}
    for rname, groups in residents:
        saved = quantize_group(model, groups, args.bits) if groups else []
        for sname, depth in slots:
            row, kcos = key_row(depth)
            per = {}
            for e in ents:
                col, pcos = payload_col(e, depth)
                b = bake(row, col)
                pred, zv, marg = nonce_read(COVER[ENT_CLASS[e]])
                unbake(b)
                per[e] = {"pred": pred, "truth": COVER[ENT_CLASS[e]],
                          "z": round(zv, 3), "margin": round(marg, 3),
                          "payload_cos": round(pcos, 4)}
            if rname == "bf16_res" and sname == "bf16":
                ref_preds = {e: per[e]["pred"] for e in ents}
            acc = round(float(np.mean(
                [per[e]["pred"] == per[e]["truth"] for e in ents])), 3)
            flip = round(float(np.mean(
                [per[e]["pred"] != ref_preds[e] for e in ents])), 3)
            cells[f"{rname}/{sname}"] = {
                "acc": acc, "flip_vs_ref": flip,
                "key_cos": round(kcos, 4),
                "payload_cos_mean": round(float(np.mean(
                    [per[e]["payload_cos"] for e in ents])), 4),
                "z_mean": round(float(np.mean([per[e]["z"] for e in ents])), 3),
                "margin_mean": round(float(np.mean(
                    [per[e]["margin"] for e in ents])), 3),
                "bits_per_weight": (16 if depth is None
                                    else round(depth * np.log2(3), 2)),
                "cells": per}
            c = cells[f"{rname}/{sname}"]
            print(f"  {rname:10s} {sname:5s} acc={c['acc']} flip={c['flip_vs_ref']} "
                  f"kcos={c['key_cos']} pcos={c['payload_cos_mean']} "
                  f"z={c['z_mean']} bits/w={c['bits_per_weight']}")
        restore(saved)

    # ── frozen verdicts (pre-reg f3 design freeze) ────────────────────────────────
    def acc(r, s):
        return cells[f"{r}/{s}"]["acc"]

    best_bf = max(acc("bf16_res", "K2"), acc("bf16_res", "K3"))
    best_q4 = max(acc("allq4_res", "K2"), acc("allq4_res", "K3"))
    parity = bool(best_bf >= acc("bf16_res", "bf16") - 0.06)
    survives = bool(best_q4 >= acc("allq4_res", "bf16") - 0.06)
    deg_bf = acc("bf16_res", "bf16") - acc("bf16_res", "K1") >= 0.10
    deg_q4 = acc("allq4_res", "bf16") - acc("allq4_res", "K1") >= 0.10
    n10_degrades = bool(deg_bf or deg_q4)
    beats = []
    if deg_bf:
        beats.append(best_bf - acc("bf16_res", "K1") >= 0.10)
    if deg_q4:
        beats.append(best_q4 - acc("allq4_res", "K1") >= 0.10)
    beats_n10 = bool(all(beats)) if beats else None      # None = floor uninformative
    ships = bool(parity and survives
                 and (beats_n10 if n10_degrades else True))
    print(f"\n[f3] PARITY={parity} SURVIVES-Q4={survives} "
          f"N10-degrades={n10_degrades} BEATS-N10={beats_n10}")
    print(f"[f3] VERDICT ARTIFACT-SHIPS = {ships}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "layer": L, "scale": args.scale,
           "target_z": z_t, "bits": args.bits, "device": dev,
           "n_entities": len(ents), "valid": valid, "cells": cells,
           "verdict_PARITY": parity, "verdict_SURVIVES_Q4": survives,
           "verdict_N10_degrades": n10_degrades, "verdict_BEATS_N10": beats_n10,
           "verdict_ARTIFACT_SHIPS": ships}
    (out / "operand_mirror.json").write_text(json.dumps(res, indent=2))
    print(f"[f3] wrote {out}/operand_mirror.json")


if __name__ == "__main__":
    main()
