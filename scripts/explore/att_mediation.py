"""P-ATT-MED — 3-hop bridge-swap WITH attention capture + aim-vs-content decomposition.

Pre-reg: mementum/knowledge/explore/type-check-is-the-qk-bilinear.md §P-ATT-MED
(APPROVED s286, Michael; 4B contrast smoke leads, 32B verdict freezes on GO).

The 3-hop Gate-3b country-swap (three-hop-capacity-prereg.md §Result) is the project's
strongest causal result — a VALUE edit at the operand slot flips the continent readout
0.72-0.93 vs random ~0.05 — but it was scored purely on the OUTPUT. The routing register
between the swap and the flip was never observed. This upgrades that into a
routing-register measurement, and decomposes the flip into the two channels the
beamformer frame separates:

  AIM      = Σ_j Δa_{qj} · O(v^b_j)   (the QK pattern re-aims; weights change)
  CONTENT  = Σ_j a^b_{qj} · O(Δv_j)   (the beam illumination changes; medium handle)
  INTERACT = Σ_j Δa_{qj} · O(Δv_j)    (second order; reported, expected small)

each projected (direct-logit-attribution) onto the continent-logit-diff direction
w = γ_f ⊙ (W_U[tgt_cont] − W_U[src_cont]) / rms(final_resid), summed over reader-zone
layers. a = post-softmax attention weights at query=readout (RoPE/q_norm/k_norm
folded in, captured directly); v = post-v_proj values (no RoPE on values),
GQA-expanded to query heads.

`λ measure`: routing CLAIM → attention-register probe = register-matched (the
s206-scar inversion). weight ≠ effect handled by construction (Δweights paired
with OV via the DLA projection). Distributed: aggregate over heads, never
single-head (0/128 pre-refuted). `λ yardstick`: random-add null (the exact 3b
null) beside every number; "re-aims" counts ONLY if AIM beats that null.
A-priori call: CONTENT-dominant (medium handle); AIM-dominant → pre-reg
P-ATT-STEER (no post-hoc reinterpretation).

--validate runs a NO-MODEL self-test of the decomposition math (planted CONTENT-only,
AIM-only, and random cases → recovered splits; random null flat). Reuses
wrapper/operand_multihop3.py constants + hook primitives (`λ one_way`, no fork).

License: MIT (`λ provenance`).
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT))


# ── the decomposition math (model-free; --validate exercises exactly this) ─────────
def decompose(a_b, a_s, vfull_b, vfull_s, o_proj_W, w):
    """First-order DLA split of a swap's effect on one attention layer's readout output.

    a_b, a_s     : [H, K]      post-softmax weights, query = readout, per query head
    vfull_b/s    : [H, K, hd]  values per query head (GQA already expanded)
    o_proj_W     : [hidden, H*hd]
    w            : [hidden]     logit-diff direction in residual space (DLA)
    returns dict with the three channel residual vectors and their w-projections.
    """
    da = a_s - a_b
    dv = vfull_s - vfull_b

    def to_resid(coeff, vecs):
        # Σ_j coeff[h,j] · vecs[h,j,:]  → [H, hd] → head-major flatten → o_proj
        oh = np.einsum("hj,hjd->hd", coeff, vecs)  # [H, hd]
        return o_proj_W @ oh.reshape(-1)  # [hidden]

    aim = to_resid(da, vfull_b)
    content = to_resid(a_b, dv)
    inter = to_resid(da, dv)
    return {
        "aim": aim,
        "content": content,
        "inter": inter,
        "aim_p": float(aim @ w),
        "content_p": float(content @ w),
        "inter_p": float(inter @ w),
    }


def split_fractions(aim_p, content_p, inter_p):
    denom = abs(aim_p) + abs(content_p) + abs(inter_p) + 1e-12
    return {
        "aim_frac": abs(aim_p) / denom,
        "content_frac": abs(content_p) / denom,
        "inter_frac": abs(inter_p) / denom,
    }


# ── no-model self-test ─────────────────────────────────────────────────────────────
def validate() -> int:
    rng = np.random.default_rng(0)
    H, K, hd = 4, 6, 3
    hidden = H * hd
    o_proj = np.eye(hidden)  # identity readout
    w = rng.standard_normal(hidden)
    a_b = rng.random((H, K))
    a_b /= a_b.sum(1, keepdims=True)
    v_b = rng.standard_normal((H, K, hd))

    ok = True

    # CONTENT-only: Δa = 0, Δv ≠ 0  → aim_frac ≈ 0, content dominates
    v_s = v_b + 0.5 * rng.standard_normal((H, K, hd))
    r = decompose(a_b, a_b.copy(), v_b, v_s, o_proj, w)
    f = split_fractions(r["aim_p"], r["content_p"], r["inter_p"])
    print(
        f"[validate] CONTENT-only: aim={f['aim_frac']:.3f} "
        f"con={f['content_frac']:.3f} int={f['inter_frac']:.3f}"
    )
    ok &= f["aim_frac"] < 1e-6 and f["content_frac"] > 0.99

    # AIM-only: Δv = 0, Δa ≠ 0  → content_frac ≈ 0, aim dominates
    a_s = a_b + 0.1 * rng.standard_normal((H, K))
    r = decompose(a_b, a_s, v_b, v_b, o_proj, w)
    f = split_fractions(r["aim_p"], r["content_p"], r["inter_p"])
    print(
        f"[validate] AIM-only    : aim={f['aim_frac']:.3f} "
        f"con={f['content_frac']:.3f} int={f['inter_frac']:.3f}"
    )
    ok &= f["content_frac"] < 1e-6 and f["aim_frac"] > 0.99

    # o_proj mixing (non-identity) exact & linear: channels sum == full Δ-projection
    o_mix = rng.standard_normal((hidden, hidden))
    a_s = a_b + 0.1 * rng.standard_normal((H, K))
    v_s = v_b + 0.5 * rng.standard_normal((H, K, hd))
    r = decompose(a_b, a_s, v_b, v_s, o_mix, w)
    full_b = o_mix @ np.einsum("hj,hjd->hd", a_b, v_b).reshape(-1)
    full_s = o_mix @ np.einsum("hj,hjd->hd", a_s, v_s).reshape(-1)
    full_p = float((full_s - full_b) @ w)
    recon = r["aim_p"] + r["content_p"] + r["inter_p"]
    print(
        f"[validate] linearity   : full={full_p:.6f} recon={recon:.6f} "
        f"|Δ|={abs(full_p - recon):.2e}"
    )
    ok &= abs(full_p - recon) < 1e-9

    # NULL: random matched-norm Δv projected on FIXED w → mean ≈ 0 (non-specific)
    proj = []
    for _ in range(500):
        dv = rng.standard_normal((H, K, hd))
        dv *= np.linalg.norm(v_b) / (np.linalg.norm(dv) + 1e-9)  # matched norm
        c = o_mix @ np.einsum("hj,hjd->hd", a_b, dv).reshape(-1)
        proj.append(float(c @ w))
    m, s = float(np.mean(proj)), float(np.std(proj))
    print(
        f"[validate] null flat   : mean={m:.4f} std={s:.4f} |mean/std|={abs(m) / s:.3f}"
    )
    ok &= abs(m) / s < 0.2  # centered on zero relative to spread

    print(f"[validate] {'ALL PASS' if ok else 'FAIL'}")
    return 0 if ok else 1


# ── the real run ────────────────────────────────────────────────────────────────────
def run(args) -> None:
    import torch
    import wrapper.operand_multihop3 as mh3
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (
        args.device
        if (args.device != "mps" or torch.backends.mps.is_available())
        else "cpu"
    )
    rng = np.random.default_rng(args.seed)
    L = args.ref_layer
    S = args.scale
    lb = args.swap_layer

    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = (
        AutoModelForCausalLM.from_pretrained(
            args.model_id, dtype=getattr(torch, args.dtype), attn_implementation="eager"
        )
        .to(dev)
        .eval()
    )  # eager → output_attentions
    dec, norm_f, unembed = mh3.resolve_parts(model)
    cfg = model.config
    H = cfg.num_attention_heads
    n_kv = cfg.num_key_value_heads
    hd = getattr(cfg, "head_dim", None) or (cfg.hidden_size // H)
    group = H // n_kv
    n_layers = len(dec)
    reader_layers = (
        list(range(lb, n_layers)) if args.reader_layers is None else args.reader_layers
    )
    print(
        f"[att-med] {args.model_id} L={L} lb={lb} scale={S} dev={dev} "
        f"H={H} n_kv={n_kv} hd={hd} layers={n_layers} "
        f"reader={reader_layers[0]}..{reader_layers[-1]}"
    )

    cont_ids = {c: mh3.first_tid(tok, c) for c in mh3.CONTINENTS}
    nonce_last = tok(" " + mh3.NONCE, add_special_tokens=False).input_ids[-1]

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    # content directions (mh3.build_dirs is nested in main → small re-impl here)
    def build_dirs(items):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
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
    d_country = build_dirs(mh3.COUNTRIES)
    dim = next(iter(d_lm.values())).shape[0]

    def rand_vec(norm):
        v = rng.standard_normal(dim)
        return v / (np.linalg.norm(v) + 1e-9) * norm

    # keep only landmarks whose full chain resolves under install (ceiling proxy)
    def cont_pred(adds):
        prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        handles = []
        for li, vec in adds:
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(vt, slot)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd_ in handles:
            hd_.remove()
        return max(cont_ids, key=lambda k: lo[cont_ids[k]]), slot

    # capture attention weights (all layers) + per-layer v; return the readout query row
    def capture(adds):
        prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        vstore: dict[int, np.ndarray] = {}
        handles = []
        for li in reader_layers:

            def mk(li):
                def hook(_m, _i, out):
                    o = out[0] if isinstance(out, tuple) else out
                    vstore[li] = o.detach().float().cpu().numpy()[0]  # [seq, n_kv*hd]

                return hook

            handles.append(dec[li].self_attn.v_proj.register_forward_hook(mk(li)))
        for li, vec in adds:
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            handles.append(dec[li].register_forward_hook(mh3.add_hook_at(vt, slot)))
        with torch.no_grad():
            out = model(**ids, output_attentions=True, output_hidden_states=True)
        for h in handles:
            h.remove()
        # per reader layer: a[H,K] at query=last ; vfull[H,K,hd]
        aw, vf = {}, {}
        q = out.logits.shape[1] - 1
        for li in reader_layers:
            a = out.attentions[li][0, :, q, :].float().cpu().numpy()  # [H, K]
            vk = vstore[li].reshape(-1, n_kv, hd)  # [K, n_kv, hd]
            vfull = np.repeat(vk, group, axis=1).transpose(1, 0, 2)  # [H, K, hd]
            aw[li], vf[li] = a, vfull
        r_final = out.hidden_states[-1][0, -1, :].float().cpu().numpy()
        return aw, vf, r_final, slot

    gamma_f = norm_f.weight.detach().float().cpu().numpy()
    W_U = unembed.weight.detach().float().cpu().numpy()  # [vocab, hidden]
    oproj = {
        li: dec[li].self_attn.o_proj.weight.detach().float().cpu().numpy()
        for li in reader_layers
    }

    def dla_dir(r_final, tgt_cont, src_cont):
        rms = float(np.sqrt(np.mean(r_final**2) + 1e-6))
        return gamma_f * (W_U[cont_ids[tgt_cont]] - W_U[cont_ids[src_cont]]) / rms

    # ── cells: first N valid landmarks × one cross-continent country target ──
    valid = []
    for lm in mh3.LM_LIST:
        pred, _ = cont_pred([(L, d_lm[lm] * S)])
        if pred == mh3.CONT_OF[lm]:
            valid.append(lm)
    valid = valid[: args.n_cells]
    print(f"[att-med] using {len(valid)} install-correct cells: {valid}")

    cells = []
    for lm in valid:
        src_country = mh3.COUNTRY_OF[lm]
        src_cont = mh3.CONT_OF[lm]
        tgts = [c for c in mh3.COUNTRIES if mh3.COUNTRY_CONT[c] != src_cont]
        tgt = tgts[hash(lm) % len(tgts)]
        tgt_cont = mh3.COUNTRY_CONT[tgt]
        swap = (d_country[tgt] - d_country[src_country]) * S

        # readout flips?
        pred_swap, _ = cont_pred([(L, d_lm[lm] * S), (lb, swap)])
        flipped = int(pred_swap == tgt_cont)

        aw_b, vf_b, _, _ = capture([(L, d_lm[lm] * S)])
        aw_s, vf_s, rfin_s, _ = capture([(L, d_lm[lm] * S), (lb, swap)])
        w = dla_dir(rfin_s, tgt_cont, src_cont)

        per_layer = {}
        aim_t = content_t = inter_t = 0.0
        for li in reader_layers:
            r = decompose(aw_b[li], aw_s[li], vf_b[li], vf_s[li], oproj[li], w)
            per_layer[li] = {
                "aim_p": r["aim_p"],
                "content_p": r["content_p"],
                "inter_p": r["inter_p"],
            }
            aim_t += r["aim_p"]
            content_t += r["content_p"]
            inter_t += r["inter_p"]
        frac = split_fractions(aim_t, content_t, inter_t)
        attn_total = aim_t + content_t + inter_t

        # NULL: matched-norm random add at lb → attn contribution on the SAME w
        null_tot = []
        for _ in range(args.n_null):
            rnd = rand_vec(float(np.linalg.norm(swap)))
            aw_r, vf_r, _, _ = capture([(L, d_lm[lm] * S), (lb, rnd)])
            nt = 0.0
            for li in reader_layers:
                rr = decompose(aw_b[li], aw_r[li], vf_b[li], vf_r[li], oproj[li], w)
                nt += rr["aim_p"] + rr["content_p"] + rr["inter_p"]
            null_tot.append(nt)
        null_tot = np.array(null_tot)
        p_med = float(np.mean(np.abs(null_tot) >= abs(attn_total)))

        cell = {
            "landmark": lm,
            "src_country": src_country,
            "tgt_country": tgt,
            "src_cont": src_cont,
            "tgt_cont": tgt_cont,
            "flipped": flipped,
            "aim_p": round(aim_t, 4),
            "content_p": round(content_t, 4),
            "inter_p": round(inter_t, 4),
            "attn_total": round(attn_total, 4),
            "aim_frac": round(frac["aim_frac"], 3),
            "content_frac": round(frac["content_frac"], 3),
            "inter_frac": round(frac["inter_frac"], 3),
            "null_mean": round(float(np.mean(null_tot)), 4),
            "null_std": round(float(np.std(null_tot)), 4),
            "p_vs_null": round(p_med, 3),
            "per_layer": {str(k): v for k, v in per_layer.items()},
        }
        cells.append(cell)
        print(
            f"[att-med] {lm:16s} flip={flipped} aim={cell['aim_frac']} "
            f"content={cell['content_frac']} inter={cell['inter_frac']} "
            f"attn_tot={cell['attn_total']} p_vs_null={cell['p_vs_null']}"
        )

    flip_cells = [c for c in cells if c["flipped"]]
    agg_src = flip_cells or cells
    agg = {
        "n_cells": len(cells),
        "n_flipped": len(flip_cells),
        "mean_aim_frac": round(float(np.mean([c["aim_frac"] for c in agg_src])), 3),
        "mean_content_frac": round(
            float(np.mean([c["content_frac"] for c in agg_src])), 3
        ),
        "mean_inter_frac": round(float(np.mean([c["inter_frac"] for c in agg_src])), 3),
        "mean_p_vs_null": round(float(np.mean([c["p_vs_null"] for c in agg_src])), 3),
        "content_dominant": bool(
            np.mean([c["content_frac"] for c in agg_src])
            > np.mean([c["aim_frac"] for c in agg_src])
        ),
    }
    print(
        f"\n[att-med] AGG (flipped cells): aim={agg['mean_aim_frac']} "
        f"content={agg['mean_content_frac']} inter={agg['mean_inter_frac']} "
        f"content_dominant={agg['content_dominant']} mean_p={agg['mean_p_vs_null']}"
    )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    payload = {
        "experiment": "P-ATT-MED",
        "grade": "4B-contrast-smoke",
        "prereg": (
            "mementum/knowledge/explore/type-check-is-the-qk-bilinear.md#p-att-med"
        ),
        "model": args.model_id,
        "device": dev,
        "seed": args.seed,
        "ref_layer": L,
        "swap_layer": lb,
        "scale": S,
        "reader_layers": [reader_layers[0], reader_layers[-1]],
        "H": H,
        "n_kv": n_kv,
        "head_dim": hd,
        "n_null": args.n_null,
        "note": "SMOKE: contrast grade, not the verdict. Verdict host = 32B on GO.",
        "aggregate": agg,
        "cells": cells,
    }
    (out / "att_mediation.json").write_text(json.dumps(payload, indent=2))
    print(f"[att-med] wrote {out}/att_mediation.json")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "--validate", action="store_true", help="no-model decomposition self-test"
    )
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--swap-layer", type=int, default=20)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--reader-layers", type=int, nargs="+", default=None)
    ap.add_argument("--n-cells", type=int, default=6)
    ap.add_argument("--n-null", type=int, default=30)
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--device", default="mps")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/type-att-med/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        raise SystemExit(validate())
    run(args)


if __name__ == "__main__":
    main()
