"""(f1) WEIGHT-SERIALIZE the operand - E1 equivalence (hook -> appended FFN slot).

Pre-reg: ffn-function-bake-prereg.md Stage-f. The s277-279 operand install is a runtime
forward-hook (transient). E1 graduates it to WEIGHTS: hand-construct ONE appended MLP
recognition neuron at layer L that fires on the nonce content signature and pushes the
operand payload d_E - NO runtime hook - and reproduces the covering composition.

Bias-free-MLP fix (SuperBake s6, method reference; our code is MIT): Qwen3 MLP has no
bias, so a neuron computes only x.k. Make the key k PERPENDICULAR to the carrier mu_hat
(population mean dir) so x.k == (x-mu).k identically -> silu's knee lands at the mean
with NO bias. Selectivity from the multiplicative gate*up form with gate=up: the neuron
computes silu(z)*z, so a token scoring at ratio rho of the target gets ~rho^2 of the
output ("born hard").

  slot: gate_row = up_row = beta*k ; down_col = scale*d_E / m
  where z_nonce = beta*<k, x_nonce> set to target_z; m = silu(z)*z (add ~ scale*d_E).

`lambda measure`: key = routing (fires slot); payload = value (d_E). `lambda yardstick`:
nulls = shuffled-key (N7), decoy-nonce inert, baseline; real-word covering unharmed.
E1 pass iff baked-no-hook composition ~ hook AND >> baseline AND nonce-specific.

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

DECOY = "blorf"      # near-miss nonce: the slot must NOT fire on it


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
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--smoke", action="store_true", help="one entity only")
    ap.add_argument("--out", default="results/ffn-bake/operand-bake-qwen3-4b")
    args = ap.parse_args()

    L = args.layer
    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(0)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec = model.model.layers
    mlp = dec[L].mlp
    cover_ids = {lb: tid(tok, lb) for lb in COVER_LABELS}
    nonce_last = tok(" " + NONCE, add_special_tokens=False).input_ids[-1]
    print(f"[bake] {args.model_id} L={L} scale={args.scale} "
          f"target_z={args.target_z} dev={dev}")

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

    # ── d_E per entity (payload; layer-L OUTPUT, object token) ────────────────────
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
    hdim = g_mean.shape[0]

    # ── KEY: nonce MLP-input signature + carrier μ (population mean) ───────────────
    nonce_x, innocent_x = [], []
    for pfx in COVER_PREFIXES:
        ids = tok(pfx + COVER_QUERY.format(x=NONCE), return_tensors="pt").to(dev)
        st: dict = {}
        h = mlp.register_forward_pre_hook(cap_mlp_in(st, "i"))
        with torch.no_grad():
            model(**ids)
        h.remove()
        toks = ids.input_ids[0].tolist()
        pos = find_slot(toks, nonce_last)
        nonce_x.append(st["i"][0, pos, :])
        innocent_x.append(st["i"][0])                       # all positions = innocents
    # more innocents from declaratives (real-word prose)
    for fr in FRAMES[:4]:
        ids = tok(decl(fr, "eagle"), return_tensors="pt").to(dev)
        st = {}
        h = mlp.register_forward_pre_hook(cap_mlp_in(st, "i"))
        with torch.no_grad():
            model(**ids)
        h.remove()
        innocent_x.append(st["i"][0])
    m_nonce = np.mean(nonce_x, axis=0)
    mu = np.mean(np.concatenate(innocent_x, axis=0), axis=0)          # carrier
    mu_hat = mu / (np.linalg.norm(mu) + 1e-9)
    k_raw = m_nonce - mu
    k = k_raw - (k_raw @ mu_hat) * mu_hat                             # ⟂ carrier
    k = k / (np.linalg.norm(k) + 1e-9)
    kx = float(k @ (m_nonce - mu))                                   # nonce score (>0)
    beta = args.target_z / (kx if abs(kx) > 1e-6 else 1e-6)
    z = args.target_z
    m_mag = float(F.silu(torch.tensor(z)) * z)                        # neuron magnitude
    print(f"[bake] key⟂carrier: kx={kx:.3f} beta={beta:.3f} m_mag={m_mag:.3f} "
          f"|k·μ̂|={abs(float(k @ mu_hat)):.2e}")

    # ── append/remove ONE recognition neuron at layer L MLP ───────────────────────
    orig = {n: getattr(mlp, n).weight.data.clone() for n in ("gate_proj", "up_proj",
                                                             "down_proj")}

    def bake(payload, key_vec):
        gk = torch.tensor(beta * key_vec, dtype=model.dtype, device=dev).unsqueeze(0)
        dcol = torch.tensor(payload / m_mag, dtype=model.dtype, device=dev).unsqueeze(1)
        for n, row in (("gate_proj", gk), ("up_proj", gk)):
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(torch.cat([orig[n], row], dim=0))
            proj.out_features += 1
        dp = mlp.down_proj
        dp.weight = nn.Parameter(torch.cat([orig["down_proj"], dcol], dim=1))
        dp.in_features += 1

    def unbake():
        for n in ("gate_proj", "up_proj", "down_proj"):
            proj = getattr(mlp, n)
            proj.weight = nn.Parameter(orig[n].clone())
        mlp.gate_proj.out_features -= 1
        mlp.up_proj.out_features -= 1
        mlp.down_proj.in_features -= 1

    # hook version (equivalence reference) — add scale·d_E at nonce slot, layer L out
    def hook_pred(word, vec):
        ids = tok(COVER_PREFIXES[0] + COVER_QUERY.format(x=word),
                  return_tensors="pt").to(dev)
        pos = find_slot(ids.input_ids[0].tolist(), nonce_last)

        def add(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            h[0, pos, :] = h[0, pos, :] + torch.tensor(vec, dtype=h.dtype, device=dev)
            return out
        hd = dec[L].register_forward_hook(add)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        hd.remove()
        return max(COVER_LABELS, key=lambda lb: lo[cover_ids[lb]])

    base_nonce = cover_pred(NONCE)             # un-baked baseline
    ents = (["eagle"] if args.smoke
            else [e for e in ENTS if cover_pred(e) == COVER[ENT_CLASS[e]]])
    print(f"[bake] baseline covering(nonce)={base_nonce}; testing {len(ents)} entities")

    rng_k = k[np.argsort(rng.standard_normal(hdim))]   # shuffled-key null (N7)
    rows = {}
    baked_ok, hook_ok, decoy_fire, shuf_ok = 0, 0, 0, 0
    for e in ents:
        truth = COVER[ENT_CLASS[e]]
        # baked (no hook) — payload = scale*d_E to match the hook dose
        bake(d_E[e] * args.scale, k)
        pred_b = cover_pred(NONCE)
        pred_decoy = cover_pred(DECOY)          # near-miss: slot must not fire
        real_word = cover_pred("wolf")          # real word unharmed
        unbake()
        # shuffled-key null
        bake(d_E[e] * args.scale, rng_k)
        pred_shuf = cover_pred(NONCE)
        unbake()
        # hook reference
        pred_h = hook_pred(NONCE, d_E[e] * args.scale)
        ob = int(pred_b == truth)
        oh = int(pred_h == truth)
        baked_ok += ob
        hook_ok += oh
        decoy_fire += int(pred_decoy != cover_pred(DECOY))   # slot changed decoy? (~0)
        shuf_ok += int(pred_shuf == truth)
        rows[e] = {"truth": truth, "baked": pred_b, "hook": pred_h,
                   "decoy": pred_decoy, "real_word_wolf": real_word,
                   "shuffled_key": pred_shuf}
        print(f"  {e:9s} truth={truth:8s} baked={pred_b:8s} hook={pred_h:8s} "
              f"decoy={pred_decoy:8s} shuf={pred_shuf:8s}")

    n = len(ents)
    baked_acc = round(baked_ok / n, 3)
    hook_acc = round(hook_ok / n, 3)
    shuf_acc = round(shuf_ok / n, 3)
    base_decoy = cover_pred(DECOY)
    print(f"\n[bake] baked_acc={baked_acc} hook_acc={hook_acc} "
          f"shuffled_key_acc={shuf_acc} baseline_decoy={base_decoy}")

    # E1 verdict (pre-registered): baked ≈ hook ∧ ≫ baseline ∧ nonce-specific
    e1 = bool(baked_acc >= 0.66 and baked_acc >= hook_acc - 0.15
              and shuf_acc < baked_acc - 0.2)
    print(f"[bake] VERDICT E1 WEIGHT-SERIALIZED = {e1}")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    res = {"model": args.model_id, "layer": L, "scale": args.scale,
           "target_z": args.target_z, "device": dev, "nonce": NONCE, "decoy": DECOY,
           "baseline_nonce_cover": base_nonce, "n": n,
           "baked_acc": baked_acc, "hook_acc": hook_acc, "shuffled_key_acc": shuf_acc,
           "key_kx": round(kx, 4), "beta": round(beta, 4), "rows": rows,
           "verdict_E1": e1}
    (out / "operand_bake.json").write_text(json.dumps(res, indent=2))
    print(f"[bake] wrote {out}/operand_bake.json")


if __name__ == "__main__":
    main()
