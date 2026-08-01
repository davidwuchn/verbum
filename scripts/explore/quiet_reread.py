#!/usr/bin/env python3
"""Quieted re-read of the 3a cells (s294) — Michael: "did we not quiet the signal
enough?" 3a read/injected through a LOUD channel (no whitening, no dark-field, raw
non-quiet keys → argmax collapsed onto the loud attractor Agra). This asks whether
the composed signal is present-but-drowned (interference, recoverable in-context)
vs genuinely absent (needs backprop).

Per cell (composition-window pair L19→L38), capture full-vocab logits for
baseline / g-alone / stack-nonce / stack-product, then read four ways:

  raw        : argmax over the union (reproduces bake_stack; Agra wins)
  common-mode: arm minus baseline logit-delta (whiten: what INJECTION added)
  dark-field : argmax over union MINUS the loud attractors (Agra/Paris/cities)
  quiet-inj  : re-inject with keys orthogonalized against the loud readout
               directions (quiet code, P-DSP-1), then dark-field read

Readout target: g-alone should reveal the COUNTRY (hop-1 product); stack should
reveal the CAPITAL (composed). If quieting surfaces them → interference, the
in-context linker may be recoverable; if not → the signal isn't there → backprop.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

from fn_index import KEY_EXEMPLARS  # noqa: E402
from fn_stack import COUNTRY2CAP_EXEMPLARS, COUNTRY_CAP, NONCE_PROMPT  # noqa: E402
from holo_cap import NONCE_CANDS  # noqa: E402


def orthogonalize(vec: np.ndarray, loud: np.ndarray) -> np.ndarray:
    """Remove vec's components along the span of loud rows (Gram-Schmidt)."""
    q = vec.astype(np.float64).copy()
    for row in loud:
        u = row / (np.linalg.norm(row) + 1e-9)
        q = q - np.dot(q, u) * u
    return q.astype(np.float32)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--pair", default="19-38", help="w_g-w_h layer pair")
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--key-scale", type=float, default=2.0)
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--out", default="results/quiet-reread/qwen3-32b")
    args = ap.parse_args()

    import operand_multihop3 as mh3
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, _norm, _u = mh3.resolve_parts(model)
    n_layers = len(dec)
    L, S = args.ref_layer, args.scale
    lg, lh = (int(x) for x in args.pair.split("-"))
    print(f"[qr] {args.model_id} pair L{lg}->L{lh} n_layers={n_layers}")

    def unembed_row(tid: int) -> np.ndarray:
        return model.lm_head.weight[tid].detach().float().cpu().numpy()

    def first_tid(w):
        return mh3.first_tid(tok, w)

    # union (capital chain) + category token sets
    cap_labels = sorted({COUNTRY_CAP[mh3.COUNTRY_OF[lm]] for lm in mh3.LM_LIST
                         if mh3.COUNTRY_OF[lm] in COUNTRY_CAP})
    vocab = (set(mh3.CONTINENTS) | set(mh3.COUNTRIES) | set(mh3.CITIES)
             | set(cap_labels))
    tid_map, drop = {}, set()
    for w in sorted(vocab):
        t = first_tid(w)
        if any(tt == t for tt in tid_map.values()):
            drop.add(w)
        tid_map[w] = t
    union = {w: tid_map[w] for w in sorted(vocab - drop)}
    city_tids = {tid_map[c] for c in mh3.CITIES if c in union}

    # cells: shortcut-free landmarks
    cells = [lm for lm in mh3.LM_LIST
             if mh3.COUNTRY_OF[lm] in COUNTRY_CAP
             and mh3.CITY_OF[lm] != COUNTRY_CAP[mh3.COUNTRY_OF[lm]]]
    print(f"[qr] union {len(union)} cells {len(cells)}")

    # operand + key directions (bake_stack convention)
    def build_dirs(items):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store = {}
                h = dec[L].register_forward_hook(mh3.cap_hook(store, L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST)

    def cap_last(prompt, layers):
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model(**ids, output_hidden_states=True)
        return {li: out.hidden_states[li + 1][0, -1, :].float().cpu().numpy()
                for li in layers}

    specs = {"country": KEY_EXEMPLARS["country"], "country2cap": COUNTRY2CAP_EXEMPLARS}
    raw = {m: {lg: [], lh: []} for m in specs}
    for m, exs in specs.items():
        for word, tpl in exs:
            c = cap_last(tpl.format(x=word), [lg, lh])
            for li in (lg, lh):
                raw[m][li].append(c[li])
    keys = {}
    for li in (lg, lh):
        means = {m: np.mean(raw[m][li], axis=0) for m in specs}
        gm = np.mean(list(means.values()), axis=0)
        for m in specs:
            keys[(m, li)] = means[m] - gm

    # loud readout directions to null (quiet code): unembed rows of all union CITY
    # tokens + the two loudest baseline attractors (found below) → orthogonalize keys
    loud_rows = np.array([unembed_row(t) for t in city_tids])

    nonce = NONCE_CANDS[0]
    nonce_tid = tok(" " + nonce, add_special_tokens=False).input_ids[-1]

    def logits(lm, adds):
        ids = tok(NONCE_PROMPT.format(x=nonce), return_tensors="pt").to(dev)
        toks = ids.input_ids[0].tolist()
        occ = [i for i, t in enumerate(toks) if t == nonce_tid][-1]
        last = len(toks) - 1
        handles = [dec[L].register_forward_hook(mh3.add_hook_at(
            torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev), occ))]
        for (li, vec) in adds:
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(
                torch.tensor(vec * args.key_scale, dtype=torch.float32, device=dev),
                last)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for h in handles:
            h.remove()
        return lo

    kg, kh = keys[("country", lg)], keys[("country2cap", lh)]
    kg_q = orthogonalize(kg, loud_rows)
    kh_q = orthogonalize(kh, loud_rows)

    def rank_of(lo, target_tid, allowed):
        order = sorted(allowed, key=lambda t: -lo[t])
        return order.index(target_tid) + 1 if target_tid in order else 999

    # find loud attractors = union tokens most often argmax under baseline
    base_arg = []
    per = []
    for lm in cells:
        cap_tid = union.get(COUNTRY_CAP[mh3.COUNTRY_OF[lm]])
        ctry_tid = union.get(mh3.COUNTRY_OF[lm])
        lo_b = logits(lm, [])
        lo_g = logits(lm, [(lg, kg)])
        lo_h = logits(lm, [(lh, kh)])                       # h-alone (ill-typed)
        lo_s = logits(lm, [(lg, kg), (lh, kh)])
        lo_q = logits(lm, [(lg, kg_q), (lh, kh_q)])
        base_arg.append(max(union, key=lambda w: lo_b[union[w]]))
        per.append((lm, cap_tid, ctry_tid, lo_b, lo_g, lo_h, lo_s, lo_q))
    from collections import Counter
    top2 = [w for w, _ in Counter(base_arg).most_common(2)]
    loud = [union[w] for w in top2]
    print(f"[qr] loud baseline attractors: {top2}")

    allowed_full = list(union.values())
    allowed_df = [t for t in union.values() if t not in loud and t not in city_tids]

    def summarize(name, hits):
        n = len(cells)
        print(f"  {name:<26} cap@1 {hits['cap1']}/{n}  cap@≤3 {hits['cap3']}/{n}"
              f"  country@1 {hits['ct1']}/{n} (g-alone)")

    reads = {k: {"cap1": 0, "cap3": 0, "ct1": 0} for k in
             ["raw(stack)", "dark-field(BASELINE=operand)",
              "dark-field(g-alone)", "dark-field(h-alone)", "dark-field(stack)",
              "common-mode(stack-base)", "quiet-inj+dark-field"]}
    detail = []
    for (lm, cap_tid, ctry_tid, lo_b, lo_g, lo_h, lo_s, lo_q) in per:
        def df_rank(lo, cap_tid=cap_tid, allowed_df=allowed_df):
            return rank_of(lo, cap_tid, allowed_df) if cap_tid in allowed_df else 999
        r_raw = rank_of(lo_s, cap_tid, allowed_full)
        r_base = df_rank(lo_b)      # NATIVE: operand only, no keys (the control)
        r_gdf = df_rank(lo_g)       # g-alone dark-field
        r_hdf = df_rank(lo_h)       # h-alone dark-field (is stack just h-blast?)
        r_df = df_rank(lo_s)        # stack dark-field
        r_cm = rank_of(lo_s - lo_b, cap_tid, allowed_full)  # injection-only mass
        r_q = df_rank(lo_q)         # quiet injection + dark-field
        allowed_ct = [t for t in union.values() if t not in city_tids or t == ctry_tid]
        r_ct = rank_of(lo_g - lo_b, ctry_tid, allowed_ct) if ctry_tid else 999
        for key, r in [("raw(stack)", r_raw),
                       ("dark-field(BASELINE=operand)", r_base),
                       ("dark-field(g-alone)", r_gdf), ("dark-field(h-alone)", r_hdf),
                       ("dark-field(stack)", r_df),
                       ("common-mode(stack-base)", r_cm),
                       ("quiet-inj+dark-field", r_q)]:
            reads[key]["cap1"] += int(r == 1)
            reads[key]["cap3"] += int(r <= 3)
            reads[key]["ct1"] += int(r_ct == 1)
        detail.append({"landmark": lm, "raw": r_raw, "baseline_df": r_base,
                       "galone_df": r_gdf, "halone_df": r_hdf, "stack_df": r_df,
                       "common_mode": r_cm, "quiet_inj": r_q, "country_rank": r_ct})

    print(f"\n── quieted reads (capital rank; g-alone country@1), n={len(cells)} ──")
    for k in reads:
        summarize(k, reads[k])
    print("\n interpretation: BASELINE dark-field ≈ stack dark-field → the "
          "recovered capital is NATIVE (operand latent), injection adds nothing "
          "(native, not composed). stack >> baseline → injection composes.")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "quiet_reread.json").write_text(json.dumps(
        {"model_id": args.model_id, "pair": args.pair, "n_cells": len(cells),
         "loud_attractors": [w for w, _ in Counter(base_arg).most_common(2)],
         "reads": reads, "detail": detail}, indent=2))
    print(f"[qr] wrote {out}/quiet_reread.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
