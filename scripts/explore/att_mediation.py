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
import zlib
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


# ── P-TYPE-SWAP arms (the ill-typed term) — banks + 3-stage pipeline metrics ──────
# Pre-reg: type-check-is-the-qk-bilinear.md §P-TYPE-SWAP (APPROVED s287).
# Arms are matched to the same-type swap's REALIZED norm (logged); the typing-vs-
# manifold discriminator is the wrong-type-ON-MANIFOLD cell the design space lacked.
ARM_BANKS = {
    # sortal: same broad type (entity noun), wrong domain — no continent image
    "sortal": ["tiger", "eagle", "salmon", "camel", "otter", "moose"],
    # wrong-type proper: MOD-class displacement; TWO disjoint banks (no 1-axis artifact)
    "wrongtype_a": ["fierce", "gentle", "ancient", "modern", "bright", "humble"],
    "wrongtype_b": ["crimson", "hollow", "fragrant", "rugged", "serene", "brittle"],
}


def pick_pair(key: str, bank: list[str]) -> tuple[str, str]:
    """Stable per-cell bank pair. crc32, NOT builtin hash (salted per process —
    irreproducible across runs; flagged s287)."""
    i = zlib.crc32(key.encode()) % len(bank)
    j = (i + len(bank) // 2) % len(bank)
    return bank[i], bank[j]


def arm_stage_metrics(
    reader_layers, lb, oproj, aw_b, vf_b, hs_b, aw_x, vf_x, hs_x, slot,
    margin_b, margin_x,
):
    """P-TYPE-SWAP 3-stage pipeline metrics for one arm vs baseline.

    ⚠ Measurement correction (s287, pre-reg): the P-ATT-MED differential is
    w-PROJECTED, so "refused" vs "no w-component" is indistinguishable there.
    Everything here except the margin is UNPROJECTED by construction.

    SURVIVAL  = mean over post-edit reader layers of ‖Δresidual at the edited slot‖
                (did the edit live in the medium long enough to be read?)
    TRANSPORT = Σ_L ‖Δ(attention contribution at the readout query)‖  (unprojected)
    TE        = TRANSPORT / SURVIVAL   (join efficiency, separates medium-death
                from join-refusal)
    slot_mass = mean attention weight of the readout query onto the edited slot
                (does the reader withdraw its edge from an ill-typed slot? —
                 the P-ATT-DIFF question, causal form)
    BREAK     = baseline correct-continent margin − arm margin (output register:
                ignored ⟺ ≈ random-null; interferes-as-content ⟺ beats null)
    """
    surv_layers = [li for li in reader_layers if li > lb]
    surv = (
        float(np.mean([np.linalg.norm(hs_x[li] - hs_b[li]) for li in surv_layers]))
        if surv_layers
        else 0.0
    )
    tr = 0.0
    for li in reader_layers:
        fb = oproj[li] @ np.einsum("hj,hjd->hd", aw_b[li], vf_b[li]).reshape(-1)
        fx = oproj[li] @ np.einsum("hj,hjd->hd", aw_x[li], vf_x[li]).reshape(-1)
        tr += float(np.linalg.norm(fx - fb))
    sm_b = float(np.mean([aw_b[li][:, slot].mean() for li in reader_layers]))
    sm_x = float(np.mean([aw_x[li][:, slot].mean() for li in reader_layers]))
    return {
        "survival": surv,
        "transport": tr,
        "te": tr / (surv + 1e-9),
        "slot_mass": sm_x,
        "slot_mass_delta": sm_x - sm_b,
        "break": margin_b - margin_x,
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

    # ROUTE decomposition (P-ATT-FFN): MLP projection + reconstruction + route argmax
    hidden = H * hd
    wv = rng.standard_normal(hidden)
    L_att = 5
    mlp_b = rng.standard_normal((L_att, hidden))
    mlp_s = mlp_b + 0.7 * rng.standard_normal((L_att, hidden))
    mlp_p = float(sum((mlp_s[i] - mlp_b[i]) @ wv for i in range(L_att)))
    attn_p, direct_true = 1.3, -0.4
    total_p = attn_p + mlp_p + direct_true
    direct_p = total_p - attn_p - mlp_p  # reconstruction
    route_pick = "mlp" if abs(mlp_p) > abs(attn_p) else "attn"
    print(
        f"[validate] route recon : total={total_p:.4f} attn={attn_p} "
        f"mlp={mlp_p:.4f} direct={direct_p:.4f} (true {direct_true}) route={route_pick}"
    )
    ok &= abs(direct_p - direct_true) < 1e-9

    # ── P-TYPE-SWAP arm stage metrics: planted per-stage effects ──────────────────
    rl = [1, 2]
    op = {li: np.eye(hidden) for li in rl}
    slot = 2
    aw0 = {li: a_b for li in rl}
    vf0 = {li: v_b for li in rl}
    hs0 = np.zeros((4, hidden))

    # no-change arm → all stages exactly zero
    m0 = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vf0, hs0, slot, 2.0, 2.0)
    z0 = m0["transport"] == 0.0 and m0["break"] == 0.0 and m0["slot_mass_delta"] == 0.0
    print(f"[validate] arms zero   : transport=0 break=0 smd=0 → {z0}")
    ok &= z0

    # content plant at the slot column + survival plant → transport>0, slot mass fixed;
    # doubling survival with fixed transport halves TE (the normalization that
    # separates medium-death from join-refusal)
    vfx = {li: v_b.copy() for li in rl}
    for li in rl:
        vfx[li][:, slot, :] += 1.0
    hs1 = hs0.copy()
    hs1[1:] += 0.5 / np.sqrt(hidden)
    mc = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vfx, hs1, slot, 2.0, 2.0)
    hs2 = hs0.copy()
    hs2[1:] += 1.0 / np.sqrt(hidden)
    mc2 = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vfx, hs2, slot, 2.0, 2.0)
    te_ok = (
        mc["transport"] > 0
        and abs(mc["slot_mass_delta"]) < 1e-12
        and abs(mc2["te"] - mc["te"] / 2) < 1e-6  # 1e-9 denom epsilon
    )
    print(
        f"[validate] arms content: transport={mc['transport']:.3f} smd=0 "
        f"te={mc['te']:.3f}→{mc2['te']:.3f} (2× survival halves TE) → {te_ok}"
    )
    ok &= te_ok

    # join-withdrawal plant: slot column zeroed + renormalized → slot_mass_delta < 0
    awx = {}
    for li in rl:
        a = a_b.copy()
        a[:, slot] = 0.0
        a /= a.sum(1, keepdims=True)
        awx[li] = a
    mw = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, awx, vf0, hs1, slot, 2.0, 2.0)
    w_ok = mw["slot_mass_delta"] < 0
    print(
        f"[validate] arms refuse : slot_mass_delta={mw['slot_mass_delta']:.4f}"
        f" < 0 → {w_ok}"
    )
    ok &= w_ok

    # BREAK exact: margin_b=2.0, margin_x=0.5 → break=1.5
    mb = arm_stage_metrics(rl, 0, op, aw0, vf0, hs0, aw0, vf0, hs0, slot, 2.0, 0.5)
    b_ok = abs(mb["break"] - 1.5) < 1e-12
    print(f"[validate] arms break  : break={mb['break']:.2f} (exact) → {b_ok}")
    ok &= b_ok

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
    route = args.route_decomp

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
    country_ids = {c: mh3.first_tid(tok, c) for c in mh3.COUNTRIES}
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

    # P-TYPE-SWAP arm banks (centroid offsets at ref layer, same procedure as countries)
    d_arm_banks = (
        {name: build_dirs(bank) for name, bank in ARM_BANKS.items()}
        if args.arms
        else {}
    )

    # optional 1:1 cell pinning to a previous run (builtin hash is salted per
    # process → tgt selection is NOT reproducible across runs; flagged s287)
    tgt_from = {}
    if args.cells_from:
        prev = json.loads(Path(args.cells_from).read_text())
        tgt_from = {c["landmark"]: c["tgt_country"] for c in prev["cells"]}
        print(
            f"[type-swap] pinned {len(tgt_from)} landmark→tgt cells "
            f"from {args.cells_from}"
        )

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
        mstore: dict[int, np.ndarray] = {}
        nfstore: dict[str, np.ndarray] = {}
        handles = []
        # true pre-norm final residual = INPUT to the final norm (hidden_states[-1] is
        # POST-norm — confirmed s286; using it breaks the pre-norm DLA reconstruction).

        def nf_pre(_m, inp):
            nfstore["x"] = inp[0].detach().float().cpu().numpy()[0]  # [seq, hidden]

        handles.append(norm_f.register_forward_pre_hook(nf_pre))
        for li in reader_layers:

            def mk(li):
                def hook(_m, _i, out):
                    o = out[0] if isinstance(out, tuple) else out
                    vstore[li] = o.detach().float().cpu().numpy()[0]  # [seq, n_kv*hd]

                return hook

            handles.append(dec[li].self_attn.v_proj.register_forward_hook(mk(li)))
            if route:

                def mk_mlp(li):
                    def hook(_m, _i, out):
                        o = out[0] if isinstance(out, tuple) else out
                        mstore[li] = (
                            o.detach().float().cpu().numpy()[0]
                        )  # [seq, hidden]

                    return hook

                handles.append(dec[li].mlp.register_forward_hook(mk_mlp(li)))
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
        r_final = nfstore["x"][q]  # pre-norm final residual at readout
        extra = {
            # always captured (cheap; P-TYPE-SWAP arms + BREAK margins need them)
            "logits_all": out.logits[0, -1, :].float().cpu().numpy(),
            "hs_slot": np.stack(
                [h[0, slot, :].float().cpu().numpy() for h in out.hidden_states]
            ),  # [n_layers+1, hidden] residual at the edited slot (SURVIVAL)
        }
        if route:
            extra["logits"] = out.logits[0, -1, :].float().cpu().numpy()  # [vocab]
            extra["mlp"] = {li: mstore[li][q].copy() for li in reader_layers}
            # readout-position residual per layer (for depth-order lens)
            extra["hs"] = np.stack(
                [h[0, -1, :].float().cpu().numpy() for h in out.hidden_states]
            )  # [n_layers+1, hidden]
        return aw, vf, r_final, slot, extra

    gamma_f = norm_f.weight.detach().float().cpu().numpy()
    W_U = unembed.weight.detach().float().cpu().numpy()  # [vocab, hidden]
    oproj = {
        li: dec[li].self_attn.o_proj.weight.detach().float().cpu().numpy()
        for li in reader_layers
    }

    def dla_dir(r_final, tgt_cont, src_cont):
        rms = float(np.sqrt(np.mean(r_final**2) + 1e-6))
        return gamma_f * (W_U[cont_ids[tgt_cont]] - W_U[cont_ids[src_cont]]) / rms

    def lens_peak(hs, tid, others):
        """argmax over layers of logit-lens margin (tid vs best-other) — numpy DLA."""
        margins = []
        for h in hs:
            normed = h / np.sqrt(np.mean(h**2) + 1e-6) * gamma_f
            margins.append(
                float(normed @ W_U[tid] - max(normed @ W_U[o] for o in others))
            )
        return int(np.argmax(margins))

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
        tgt = tgt_from.get(lm) or tgts[hash(lm) % len(tgts)]
        tgt_cont = mh3.COUNTRY_CONT[tgt]
        swap = (d_country[tgt] - d_country[src_country]) * S

        # readout flips?
        pred_swap, _ = cont_pred([(L, d_lm[lm] * S), (lb, swap)])
        flipped = int(pred_swap == tgt_cont)

        aw_b, vf_b, rfin_b, slot_b, ex_b = capture([(L, d_lm[lm] * S)])
        aw_s, vf_s, rfin_s, _, ex_s = capture([(L, d_lm[lm] * S), (lb, swap)])
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

        # ── route decomposition (P-ATT-FFN): attn vs MLP vs direct of the TOTAL flip ──
        route_fields = {}
        mlp_null = []
        if route:
            ti, si = cont_ids[tgt_cont], cont_ids[src_cont]
            # LINEARIZED total: Δresid_final · w — the per-layer attn+mlp deltas sum to
            # this EXACTLY (pre-norm residual identity) → clean reconstruction. The raw
            # logit flip (nonlinear through final RMSNorm) is reported separately.
            total_p = float((rfin_s - rfin_b) @ w)
            raw_total_p = float(
                (ex_s["logits"][ti] - ex_s["logits"][si])
                - (ex_b["logits"][ti] - ex_b["logits"][si])
            )
            mlp_p = float(
                sum((ex_s["mlp"][li] - ex_b["mlp"][li]) @ w for li in reader_layers)
            )
            direct_p = total_p - attn_total - mlp_p  # completeness residual, expect ~0
            denom = abs(attn_total) + abs(mlp_p) + abs(direct_p) + 1e-12
            cell_route = "mlp" if abs(mlp_p) > abs(attn_total) else "attn"
            oc = [country_ids[c] for c in mh3.COUNTRIES if c != src_country]
            ok = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]
            pk_country = lens_peak(ex_b["hs"], country_ids[src_country], oc)
            pk_cont = lens_peak(ex_b["hs"], cont_ids[src_cont], ok)
            route_fields = {
                "total_p": round(total_p, 4),
                "raw_total_p": round(raw_total_p, 4),
                "mlp_p": round(mlp_p, 4),
                "direct_p": round(direct_p, 4),
                "attn_frac_of_total": round(abs(attn_total) / denom, 3),
                "mlp_frac_of_total": round(abs(mlp_p) / denom, 3),
                "direct_frac_of_total": round(abs(direct_p) / denom, 3),
                "recon_err": round(abs(direct_p) / (abs(total_p) + 1e-9), 3),
                "route": cell_route,
                "pk_country": pk_country,
                "pk_cont": pk_cont,
                "composition_order": bool(pk_country < pk_cont),
            }

        # ── P-TYPE-SWAP arms: sortal / wrong-type ladder at matched realized norm ──
        arm_fields = {}
        arm_stats = {}
        null_arm = {
            k: [] for k in ("survival", "transport", "te", "slot_mass_delta", "break")
        }
        if args.arms:
            others_c = [cont_ids[c] for c in mh3.CONTINENTS if c != src_cont]

            def cont_margin(lo, _sc=src_cont, _oc=tuple(others_c)):
                return float(lo[cont_ids[_sc]] - max(lo[o] for o in _oc))

            margin_b = cont_margin(ex_b["logits_all"])
            edit_norm = float(np.linalg.norm(swap))

            def arm_eval(
                aw_x, vf_x, ex_x,
                _awb=aw_b, _vfb=vf_b, _exb=ex_b, _slot=slot_b,
                _mb=margin_b, _cm=cont_margin,
            ):
                m = arm_stage_metrics(
                    reader_layers, lb, oproj,
                    _awb, _vfb, _exb["hs_slot"],
                    aw_x, vf_x, ex_x["hs_slot"],
                    _slot, _mb, _cm(ex_x["logits_all"]),
                )
                m["pred"] = max(
                    cont_ids,
                    key=lambda cname, _lo=ex_x["logits_all"]: _lo[cont_ids[cname]],
                )
                if route:
                    m["mlp_transport"] = float(
                        sum(
                            np.linalg.norm(ex_x["mlp"][li] - _exb["mlp"][li])
                            for li in reader_layers
                        )
                    )
                return m

            # positive control, no re-forward (reuses the swap capture)
            arm_stats["same"] = arm_eval(aw_s, vf_s, ex_s)
            for name, bank in ARM_BANKS.items():
                b1, b2 = pick_pair(lm, bank)
                disp = d_arm_banks[name][b1] - d_arm_banks[name][b2]
                disp = disp / (np.linalg.norm(disp) + 1e-9) * edit_norm
                aw_x, vf_x, _, _, ex_x = capture([(L, d_lm[lm] * S), (lb, disp)])
                arm_stats[name] = arm_eval(aw_x, vf_x, ex_x)
                arm_stats[name]["pair"] = f"{b1}-{b2}"
            arm_fields["edit_norm"] = round(edit_norm, 2)

        # NULL: matched-norm random add at lb → attn contribution on the SAME w
        null_tot = []
        for _ in range(args.n_null):
            rnd = rand_vec(float(np.linalg.norm(swap)))
            aw_r, vf_r, _, _, ex_r = capture([(L, d_lm[lm] * S), (lb, rnd)])
            nt = 0.0
            for li in reader_layers:
                rr = decompose(aw_b[li], aw_r[li], vf_b[li], vf_r[li], oproj[li], w)
                nt += rr["aim_p"] + rr["content_p"] + rr["inter_p"]
            null_tot.append(nt)
            if route:
                mlp_null.append(
                    float(
                        sum(
                            (ex_r["mlp"][li] - ex_b["mlp"][li]) @ w
                            for li in reader_layers
                        )
                    )
                )
            if args.arms:
                nm = arm_eval(aw_r, vf_r, ex_r)
                for k in null_arm:
                    null_arm[k].append(nm[k])
        null_tot = np.array(null_tot)
        p_med = float(np.mean(np.abs(null_tot) >= abs(attn_total)))
        if route:
            mlp_null = np.array(mlp_null)
            route_fields["p_mlp_vs_null"] = round(
                float(np.mean(np.abs(mlp_null) >= abs(route_fields["mlp_p"]))), 3
            )
        if args.arms:
            na = {k: np.array(v) for k, v in null_arm.items()}
            for st in arm_stats.values():
                # one-sided vs the matched-norm random-add distribution:
                # transport/te/survival/break: arm ≥ null; slot withdrawal: ≤
                st["p_transport"] = round(
                    float(np.mean(na["transport"] >= st["transport"])), 3
                )
                st["p_te"] = round(float(np.mean(na["te"] >= st["te"])), 3)
                st["p_survival"] = round(
                    float(np.mean(na["survival"] >= st["survival"])), 3
                )
                st["p_slot_drop"] = round(
                    float(np.mean(na["slot_mass_delta"] <= st["slot_mass_delta"])), 3
                )
                st["p_break"] = round(float(np.mean(na["break"] >= st["break"])), 3)
                for k in (
                    "survival", "transport", "te",
                    "slot_mass", "slot_mass_delta", "break", "mlp_transport",
                ):
                    if k in st:
                        st[k] = round(st[k], 4)
            arm_fields["arms"] = arm_stats
            arm_fields["null_summary"] = {
                k: {
                    "mean": round(float(np.mean(v)), 4),
                    "std": round(float(np.std(v)), 4),
                }
                for k, v in na.items()
            }

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
            **route_fields,
            **arm_fields,
        }
        cells.append(cell)
        if args.arms:
            _a = arm_stats
            _n = arm_fields["null_summary"]
            print(
                f"[type-swap] {lm:16s} te same={_a['same']['te']:.2f} "
                f"sortal={_a['sortal']['te']:.2f} wtA={_a['wrongtype_a']['te']:.2f} "
                f"wtB={_a['wrongtype_b']['te']:.2f} null={_n['te']['mean']:.2f} | "
                f"smΔ s={_a['sortal']['slot_mass_delta']:+.4f} "
                f"a={_a['wrongtype_a']['slot_mass_delta']:+.4f} | "
                f"brk s={_a['sortal']['break']:+.2f}(p{_a['sortal']['p_break']}) "
                f"a={_a['wrongtype_a']['break']:+.2f}"
                f"(p{_a['wrongtype_a']['p_break']}) | "
                f"pred {_a['sortal']['pred']}/{_a['wrongtype_a']['pred']}/"
                f"{_a['wrongtype_b']['pred']}"
            )
        if route:
            print(
                f"[att-ffn] {lm:16s} flip={flipped} route={cell['route']:4s} "
                f"attn={cell['attn_frac_of_total']} mlp={cell['mlp_frac_of_total']} "
                f"direct={cell['direct_frac_of_total']} recon_err={cell['recon_err']} "
                f"p_mlp={cell['p_mlp_vs_null']} "
                f"pk={cell['pk_country']}/{cell['pk_cont']}"
            )
        else:
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

    if args.arms:
        arm_names = ["same", *ARM_BANKS]
        arm_cells = [c for c in agg_src if "arms" in c]
        agg["arms"] = {}
        for name in arm_names:
            vals = [c["arms"][name] for c in arm_cells]
            agg["arms"][name] = {
                "mean_survival": round(
                    float(np.mean([v["survival"] for v in vals])), 4
                ),
                "mean_transport": round(
                    float(np.mean([v["transport"] for v in vals])), 4
                ),
                "mean_te": round(float(np.mean([v["te"] for v in vals])), 4),
                "mean_slot_mass_delta": round(
                    float(np.mean([v["slot_mass_delta"] for v in vals])), 4
                ),
                "mean_break": round(float(np.mean([v["break"] for v in vals])), 4),
                "mean_p_transport": round(
                    float(np.mean([v["p_transport"] for v in vals])), 3
                ),
                "mean_p_te": round(float(np.mean([v["p_te"] for v in vals])), 3),
                "mean_p_break": round(float(np.mean([v["p_break"] for v in vals])), 3),
                "n_pred_stays_src": sum(
                    1 for c in arm_cells if c["arms"][name]["pred"] == c["src_cont"]
                ),
            }
        te_row = {n: agg["arms"][n]["mean_te"] for n in arm_names}
        wt_min = min(te_row["wrongtype_a"], te_row["wrongtype_b"])
        ladder = te_row["same"] > te_row["sortal"] > wt_min
        print(
            "[type-swap] ARM TE ladder: "
            + " ".join(f"{n}={te_row[n]:.2f}" for n in arm_names)
            + f" | ordering same>sortal>wrong = {ladder}"
        )
        print(
            "[type-swap] ARM break: "
            + " ".join(f"{n}={agg['arms'][n]['mean_break']:+.2f}" for n in arm_names)
            + " | preds-stay-src: "
            + " ".join(
                f"{n}={agg['arms'][n]['n_pred_stays_src']}/{len(arm_cells)}"
                for n in arm_names
            )
        )

    if route:
        mlp_cells = [c for c in agg_src if c.get("route") == "mlp"]
        attn_cells = [c for c in agg_src if c.get("route") == "attn"]
        agg["route"] = {
            "n_attn_dominant": len(attn_cells),
            "n_mlp_dominant": len(mlp_cells),
            "mlp_dominant_cells": [c["landmark"] for c in mlp_cells],
            "mean_recon_err": round(
                float(np.mean([c["recon_err"] for c in agg_src])), 3
            ),
            "mean_attn_frac_of_total": round(
                float(np.mean([c["attn_frac_of_total"] for c in agg_src])), 3
            ),
            "mean_mlp_frac_of_total": round(
                float(np.mean([c["mlp_frac_of_total"] for c in agg_src])), 3
            ),
            "mixed_route": bool(mlp_cells and attn_cells),
        }
        print(
            f"[att-ffn] ROUTE SPLIT: attn-dom={len(attn_cells)} "
            f"mlp-dom={len(mlp_cells)} "
            f"mlp-cells={agg['route']['mlp_dominant_cells']} "
            f"mean_recon_err={agg['route']['mean_recon_err']}"
        )

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    exp_name = (
        "P-TYPE-SWAP" if args.arms else ("P-ATT-FFN" if route else "P-ATT-MED")
    )
    payload = {
        "experiment": exp_name,
        "grade": ("smoke" if "4b" in args.out.lower() else "verdict"),
        "prereg": (
            "mementum/knowledge/explore/type-check-is-the-qk-bilinear.md#"
            + exp_name.lower().replace("_", "-")
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
        "route_decomp": route,
        "arms_enabled": args.arms,
        "cells_from": args.cells_from,
        "arm_banks": ARM_BANKS if args.arms else None,
        "aggregate": agg,
        "cells": cells,
    }
    fname = (
        "type_swap.json"
        if args.arms
        else ("att_ffn.json" if route else "att_mediation.json")
    )
    (out / fname).write_text(json.dumps(payload, indent=2))
    print(f"[{exp_name.lower()}] wrote {out}/{fname}")


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
    ap.add_argument(
        "--route-decomp",
        action="store_true",
        help="P-ATT-FFN: add MLP + direct channels, total reconstruction, depth-order",
    )
    ap.add_argument(
        "--arms",
        action="store_true",
        help="P-TYPE-SWAP: sortal/wrong-type ill-typed-term arms, 3-stage "
        "survival/transport/reduction metrics (unprojected), matched-norm ladder",
    )
    ap.add_argument(
        "--cells-from",
        default=None,
        help="pin landmark→tgt_country cells 1:1 from a previous run's JSON "
        "(builtin hash is process-salted → not reproducible otherwise)",
    )
    args = ap.parse_args()
    if args.validate:
        raise SystemExit(validate())
    run(args)


if __name__ == "__main__":
    main()
