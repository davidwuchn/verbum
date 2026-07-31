"""P-HOLO-FRAG — fragment reconstruction: hologram or not hologram?

Pre-reg: mementum/knowledge/explore/geometry-holography-signals-convergence.md
§P-HOLO-FRAG (FROZEN s289, Michael-approved — G1/LDI primary, 3-hop primary
readout). The lynchpin of the holographic frame: cut the medium and watch how
it dies. A hologram degrades SMOOTHLY and LOCATION-INDEPENDENTLY (every
fragment reconstructs a degraded whole); an addressed/localized store degrades
via CLIFFS (some random cuts hit critical components, others spare them).

Design (frozen):
  - Mean-ablate a random fraction f of BAND units, two arms:
      HEADS (attention = the beam) and MLP (FFN = the plates).
  - Sweep f in {.1,.2,.35,.5,.65,.8}; R random draws per f.
  - Readout SNR = composition margin on the 3-hop geography bank (primary,
    the (e->t)->t machinery the joins carry). Margin = logit[truth_continent]
    - max logit[other continents], with the landmark operand installed.
  - Band = layer_geometry -> find_band over continent-labeled readout-slot
    residuals (verbum.dsp, in-run); fallback to a fixed interior band.

Discriminator (frozen, TWO signatures):
  G1 (PRIMARY, the ADDRESS test): Location-Dependence Index.
      LDI(f) = across-draw SNR variance / probe-resampling noise floor.
      LDI ~= 1  -> which subset you removed doesn't matter -> NO ADDRESS
                   -> holographic / delocalized.
      LDI >> 1  -> which you removed matters -> ADDRESSES EXIST -> localized.
      Permutation-gated against the probe-resampling null.
  G2 (secondary): cliff detection on the mean SNR(f) curve
      (largest single-step drop / mean step). Smooth ~= 1; cliff >> 1.
  G3 (advisory, NEVER gated — λ yardstick): functional form vs (1-f).

Verdict (freeze on GO):
  HOLOGRAPHIC/DELOCALIZED <=> G1 within null (p>=alpha) AND G2 no-cliff
                              -> promotes P-HOLO-CAP for the +sqrt(D/k) law.
  LOCALIZED/ADDRESSED     <=> G1 beats null (p<alpha) OR G2 cliff
                              -> FALSIFIES the hologram frame.
  negative/inconclusive   <=> gate-0 fails (SNR_0 within noise).

FRAG can FALSIFY (cliff/high-LDI -> addressed) or confirm DELOCALIZATION
(low-LDI + smooth). It CANNOT positively prove hologram — the +sqrt(D/k)
capacity law is P-HOLO-CAP's job. `λ measure`: claim = distribution of the
compute across the medium; probe = behavioral SNR under random structural
ablation = literally reconstruct-from-a-fragment. Aggregate/subset by
construction (0/128 single-head prior coheres).

License: MIT (`λ provenance`).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

# verbum.dsp consumer (the substrate) — band detection lives here.
from verbum.dsp import find_band, layer_geometry

# Reuse the FROZEN 3-hop geography bank (no fork — import the data, not a copy).
_WRAP = Path(__file__).resolve().parents[2] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

F_GRID_DEFAULT = (0.1, 0.2, 0.35, 0.5, 0.65, 0.8)
# Informative middle of the sweep for the verdict aggregate (mean-ablation is
# off-distribution at the extremes; the pre-reg rests the verdict on the mid).
F_VERDICT = (0.2, 0.35, 0.5, 0.65)


# ══════════════════════════════════════════════════════════════════════════
# Pure-numpy statistics (no model — these are what --validate exercises)
# ══════════════════════════════════════════════════════════════════════════
def ldi_at_f(per_probe_draws: np.ndarray, rng: np.random.Generator,
             n_boot: int = 2000) -> dict:
    """Location-Dependence Index at one f.

    per_probe_draws: (R, P) — margin per probe, per random-ablation draw.
    across-draw variance of the bank-mean vs the probe-resampling noise floor
    (the variance the bank-mean would have from probe sampling ALONE, if which
    subset you removed did nothing). LDI ~= 1 => location-independent.
    """
    r, p = per_probe_draws.shape
    bank_means = per_probe_draws.mean(axis=1)              # (R,)
    v_across = float(bank_means.var(ddof=1)) if r > 1 else 0.0
    # probe-resampling noise floor: mean over draws of Var_probes / P.
    v_noise = float(np.mean(per_probe_draws.var(axis=1, ddof=1) / p))
    ldi = v_across / v_noise if v_noise > 0 else float("inf")
    # bootstrap null of v_across under location-independence: R draws ~ the
    # noise floor only; p = frac(null_var >= observed v_across).
    if v_noise > 0 and r > 1:
        sd = np.sqrt(v_noise)
        null = np.array([rng.normal(0.0, sd, size=r).var(ddof=1)
                         for _ in range(n_boot)])
        pval = float(np.mean(null >= v_across))
    else:
        pval = None
    return {"ldi": ldi, "v_across": v_across, "v_noise": v_noise,
            "p": pval, "mean": float(bank_means.mean()), "n_draws": r}


def cliff_stat(f_grid: list[float], mean_curve: list[float],
               snr0: float) -> dict:
    """G2: largest single-step drop / mean step on the mean SNR(f) curve.

    Prepend f=0 (clean SNR_0). Smooth monotone -> ratio ~= 1; a cliff (one
    dominant step) -> ratio >> 1. Sign-agnostic to overall level via steps.
    """
    ys = [snr0, *mean_curve]
    steps = [ys[i] - ys[i + 1] for i in range(len(ys) - 1)]  # drops (may be <0)
    total = ys[0] - ys[-1]
    k = len(steps)
    mean_step = total / k if k else 0.0
    max_step = max(steps) if steps else 0.0
    ratio = (max_step / mean_step) if mean_step > 1e-9 else float("nan")
    return {"cliff_ratio": float(ratio), "steps": [float(s) for s in steps],
            "total_drop": float(total), "max_step": float(max_step)}


def aggregate_verdict(per_f: dict[float, dict], cliff: dict,
                      alpha: float, cliff_thresh: float) -> dict:
    """Combine G1 (LDI over verdict f's) + G2 (cliff) into a verdict."""
    fs = [f for f in per_f if f in F_VERDICT]
    ldis = [per_f[f]["ldi"] for f in fs if np.isfinite(per_f[f]["ldi"])]
    ps = [per_f[f]["p"] for f in fs if per_f[f]["p"] is not None]
    med_ldi = float(np.median(ldis)) if ldis else float("nan")
    # location-dependent if a MAJORITY of verdict f's individually beat the null
    n_sig = sum(1 for p in ps if p < alpha)
    g1_localized = bool(ps and n_sig > len(ps) / 2)
    g2_cliff = bool(np.isfinite(cliff["cliff_ratio"])
                    and cliff["cliff_ratio"] >= cliff_thresh)
    localized = bool(g1_localized or g2_cliff)
    return {"median_ldi_verdict_band": med_ldi, "n_sig": n_sig,
            "n_tested": len(ps), "g1_localized": g1_localized,
            "g2_cliff": g2_cliff,
            "call": "LOCALIZED/ADDRESSED" if localized
            else "HOLOGRAPHIC/DELOCALIZED"}


# ══════════════════════════════════════════════════════════════════════════
# --validate: planted ground truth exercises the LDI + cliff detectors
# ══════════════════════════════════════════════════════════════════════════
def _synth_arm(kind: str, f_grid, r: int, rng: np.random.Generator,
               n_units: int = 64, n_probe: int = 24, signal: float = 4.0,
               noise: float = 0.25) -> tuple[dict, dict, float]:
    """Synthesize per-probe margins under a planted contribution structure.

    kind: 'holographic'   — signal spread uniformly over all units (no address)
          'localized'     — signal carried by k=ceil(sqrt(N)) critical units
          'cliff'         — threshold: signal collapses once critical mass lost
    Returns (per_f_ldi, cliff, snr0).
    """
    if kind == "holographic":
        contrib = np.full(n_units, signal / n_units)
    elif kind in ("localized", "cliff"):
        k = int(np.ceil(np.sqrt(n_units)))
        contrib = np.zeros(n_units)
        contrib[rng.choice(n_units, k, replace=False)] = signal / k
    else:
        raise ValueError(kind)
    snr0 = signal
    per_f, mean_curve = {}, []
    for f in f_grid:
        n_abl = round(f * n_units)
        draws = np.zeros((r, n_probe))
        for ri in range(r):
            abl = rng.choice(n_units, n_abl, replace=False)
            retained = signal - contrib[abl].sum()
            if kind == "cliff":
                # threshold: below half the critical mass -> collapse to floor
                frac_crit_kept = retained / signal
                retained = signal if frac_crit_kept > 0.5 else 0.4 * signal
            draws[ri] = retained + rng.normal(0.0, noise, size=n_probe)
        per_f[f] = ldi_at_f(draws, rng)
        mean_curve.append(float(draws.mean()))
    return per_f, cliff_stat(list(f_grid), mean_curve, snr0), snr0


def run_validate(alpha: float, cliff_thresh: float) -> int:
    rng = np.random.default_rng(0)
    fg = list(F_GRID_DEFAULT)
    print("── P-HOLO-FRAG --validate (planted ground truth, no model) ──")
    ok = True

    # G1 detector: holographic (LDI~1, p>=alpha) vs localized (LDI>>1, p<alpha)
    holo, holo_cliff, _ = _synth_arm("holographic", fg, 100, rng)
    loc, loc_cliff, _ = _synth_arm("localized", fg, 100, rng)
    holo_ldi = np.median([holo[f]["ldi"] for f in F_VERDICT])
    loc_ldi = np.median([loc[f]["ldi"] for f in F_VERDICT])
    holo_sig = sum(holo[f]["p"] < alpha for f in F_VERDICT)
    loc_sig = sum(loc[f]["p"] < alpha for f in F_VERDICT)
    print(f"[G1] holographic: median LDI={holo_ldi:.2f} "
          f"n_sig={holo_sig}/{len(F_VERDICT)} (want ~1, 0 sig)")
    print(f"[G1] localized:   median LDI={loc_ldi:.2f} "
          f"n_sig={loc_sig}/{len(F_VERDICT)} (want >>1, all sig)")
    g1_ok = bool(holo_ldi < 3.0 and holo_sig == 0
                 and loc_ldi > 5.0 and loc_sig == len(F_VERDICT))
    print(f"[G1] discriminates = {g1_ok}")
    ok &= g1_ok

    # G2 detector: smooth (holographic, ratio~1) vs cliff (threshold, ratio>>1)
    smooth_cliff = holo_cliff
    _, thr_cliff, _ = _synth_arm("cliff", fg, 100, rng)
    print(f"[G2] smooth cliff_ratio={smooth_cliff['cliff_ratio']:.2f} "
          f"(want < {cliff_thresh}) | threshold cliff_ratio="
          f"{thr_cliff['cliff_ratio']:.2f} (want >= {cliff_thresh})")
    g2_ok = bool(smooth_cliff["cliff_ratio"] < cliff_thresh
                 and thr_cliff["cliff_ratio"] >= cliff_thresh)
    print(f"[G2] discriminates = {g2_ok}")
    ok &= g2_ok

    # Null flatness: holographic arm must NOT be called localized.
    v_holo = aggregate_verdict(holo, holo_cliff, alpha, cliff_thresh)
    v_loc = aggregate_verdict(loc, loc_cliff, alpha, cliff_thresh)
    print(f"[verdict] holographic-plant -> {v_holo['call']} (want HOLOGRAPHIC)")
    print(f"[verdict] localized-plant   -> {v_loc['call']} (want LOCALIZED)")
    verdict_ok = bool("HOLOGRAPHIC" in v_holo["call"]
                      and "LOCALIZED" in v_loc["call"])
    ok &= verdict_ok

    print(f"\n── --validate {'ALL PASS' if ok else 'FAIL'} ──")
    return 0 if ok else 1


# ══════════════════════════════════════════════════════════════════════════
# Model path (the 4B smoke / 32B verdict)
# ══════════════════════════════════════════════════════════════════════════
def run_model(args) -> int:
    import operand_multihop3 as mh3  # frozen bank + helpers (no fork)
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    rng = np.random.default_rng(args.seed)
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()
    dec, _norm, _unembed = mh3.resolve_parts(model)
    n_layers = len(dec)
    cfg = model.config
    n_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", cfg.hidden_size // n_heads)
    inter = cfg.intermediate_size
    L = args.ref_layer
    S = args.scale
    print(f"[frag] {args.model_id} L_ref={L} scale={S} dev={dev} "
          f"n_layers={n_layers} heads={n_heads} hd={head_dim} inter={inter}")

    cont_ids = {c: mh3.first_tid(tok, c) for c in mh3.CONTINENTS}
    nonce_last = tok(" " + mh3.NONCE, add_special_tokens=False).input_ids[-1]

    def find_slot(ids_list):
        idx = [i for i, t in enumerate(ids_list) if t == nonce_last]
        return idx[-1] if idx else len(ids_list) - 1

    # ── knowledge ceiling: keep only landmarks whose full real-word chain holds ──
    def real_pred(prefix, query, word, label_ids):
        prompt = prefix + query.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        return max(label_ids, key=lambda k: lo[label_ids[k]])

    city_ids = {c: mh3.first_tid(tok, c) for c in mh3.CITIES}
    country_ids = {c: mh3.first_tid(tok, c) for c in mh3.COUNTRIES}
    valid = []
    for lm in mh3.LM_LIST:
        c_city = real_pred(mh3.CITY_PREFIX, mh3.CITY_QUERY, lm, city_ids)
        c_cnty = real_pred(mh3.CITY2COUNTRY_PREFIX, mh3.CITY2COUNTRY_QUERY,
                           mh3.CITY_OF[lm], country_ids)
        c_cont = real_pred(mh3.COUNTRY2CONT_PREFIX, mh3.COUNTRY2CONT_QUERY,
                           mh3.COUNTRY_OF[lm], cont_ids)
        if (c_city == mh3.CITY_OF[lm] and c_cnty == mh3.CITY_COUNTRY[mh3.CITY_OF[lm]]
                and c_cont == mh3.COUNTRY_CONT[mh3.COUNTRY_OF[lm]]):
            valid.append(lm)
    print(f"[frag] valid landmarks (ceiling): {len(valid)}/{len(mh3.LM_LIST)}")

    # ── content directions d_lm (per-pool mean removed), install at L ──────────
    def build_dirs(items, cap_L):
        per = {e: [] for e in items}
        for fr in mh3.FRAMES:
            for e in items:
                store: dict[int, np.ndarray] = {}
                h = dec[cap_L].register_forward_hook(mh3.cap_hook(store, cap_L))
                ids = tok(fr.format(x=e), return_tensors="pt").to(dev)
                with torch.no_grad():
                    model(**ids)
                h.remove()
                per[e].append(store[cap_L][0, -2, :])
        em = {e: np.mean(per[e], axis=0) for e in items}
        gm = np.mean([em[e] for e in items], axis=0)
        return {e: em[e] - gm for e in items}

    d_lm = build_dirs(mh3.LM_LIST, L)

    def install_hook(vec_t, pos):
        def hook(_m, _i, out):
            h = out[0] if isinstance(out, tuple) else out
            if 0 <= pos < h.shape[1]:
                h[0, pos, :] = h[0, pos, :] + vec_t.to(h.dtype)
            return out
        return hook

    def cont_logits(word, adds):
        """Continent logits at the readout slot under installs (ablation hooks,
        if any, are registered by the caller and persist across the bank)."""
        prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=word)
        ids = tok(prompt, return_tensors="pt").to(dev)
        slot = find_slot(ids.input_ids[0].tolist())
        install = []  # only the install hooks are removed here
        for (li, vec) in adds:
            vt = torch.tensor(vec, dtype=torch.float32, device=dev)
            install.append(dec[li].register_forward_hook(install_hook(vt, slot)))
        with torch.no_grad():
            lo = model(**ids).logits[0, -1, :].float().cpu().numpy()
        for hd in install:
            hd.remove()
        return lo

    def margin(lm):
        lo = cont_logits(mh3.NONCE, [(L, d_lm[lm] * S)])
        truth = mh3.CONT_OF[lm]
        others = [c for c in mh3.CONTINENTS if c != truth]
        return float(lo[cont_ids[truth]]
                     - max(lo[cont_ids[c]] for c in others))

    # ── band detection: continent-labeled readout-slot residuals -> find_band ──
    def readout_residuals():
        xs, ys = [], []
        for lm in valid:
            prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
            ids = tok(prompt, return_tensors="pt").to(dev)
            slot = find_slot(ids.input_ids[0].tolist())
            vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
            hd = dec[L].register_forward_hook(install_hook(vt, slot))
            with torch.no_grad():
                out = model(**ids, output_hidden_states=True)
            hd.remove()
            hs = out.hidden_states  # (n_layers+1) x (1,seq,D)
            xs.append(np.stack([h[0, -1, :].float().cpu().numpy() for h in hs]))
            ys.append(mh3.CONT_OF[lm])
        return np.stack(xs), np.array(ys)  # (N, n_layers+1, D), (N,)

    if args.band:
        band = list(range(args.band[0], args.band[1] + 1))
        print(f"[frag] band (fixed override) = L{band[0]}..L{band[-1]}")
    else:
        res, ylab = readout_residuals()
        per_layer = {}
        for li in range(1, res.shape[1]):        # skip embedding layer 0
            geo = layer_geometry(res[:, li, :], ylab, rng, args.n_null_band,
                                 label_order=mh3.CONTINENTS)
            per_layer[li - 1] = {"p_lowrank": geo["p_lowrank"]}
        band = find_band(per_layer, n_layers)
        print(f"[frag] band (find_band) = L{band[0]}..L{band[-1]} "
              f"({len(band)} layers)")

    out_band = [li for li in range(n_layers) if li not in band]

    # ── mean-ablation calibration: per-(layer) mean of o_proj / down_proj input ──
    def calibrate_means(layers):
        head_sum = {li: np.zeros(n_heads * head_dim) for li in layers}
        mlp_sum = {li: np.zeros(inter) for li in layers}
        n_tok = 0

        def mk_pre(store, li):
            def hook(_m, inp):
                x = inp[0].detach().float().cpu().numpy()  # (1,seq,D)
                store[li] += x[0].sum(axis=0)
                return None
            return hook

        for lm in valid:
            handles = []
            for li in layers:
                handles.append(dec[li].self_attn.o_proj.register_forward_pre_hook(
                    mk_pre(head_sum, li)))
                handles.append(dec[li].mlp.down_proj.register_forward_pre_hook(
                    mk_pre(mlp_sum, li)))
            prompt = mh3.CONT_PREFIX + mh3.CONT_QUERY.format(x=mh3.NONCE)
            ids = tok(prompt, return_tensors="pt").to(dev)
            slot = find_slot(ids.input_ids[0].tolist())
            vt = torch.tensor(d_lm[lm] * S, dtype=torch.float32, device=dev)
            handles.append(dec[L].register_forward_hook(install_hook(vt, slot)))
            with torch.no_grad():
                model(**ids)
            n_tok += ids.input_ids.shape[1]
            for hd in handles:
                hd.remove()
        head_mean = {li: head_sum[li] / max(n_tok, 1) for li in layers}
        mlp_mean = {li: mlp_sum[li] / max(n_tok, 1) for li in layers}
        return head_mean, mlp_mean

    all_layers = sorted(set(band) | set(out_band))
    head_mean, mlp_mean = calibrate_means(all_layers)
    head_mean_t = {li: torch.tensor(head_mean[li], dtype=torch.float32, device=dev)
                   for li in all_layers}
    mlp_mean_t = {li: torch.tensor(mlp_mean[li], dtype=torch.float32, device=dev)
                  for li in all_layers}

    def mk_ablate(mean_t, mask_t):
        def hook(_m, inp):
            x = inp[0].clone()
            x[..., mask_t] = mean_t[mask_t].to(x.dtype)
            return (x, *inp[1:])
        return hook

    def sample_ablation(arm, f, layers):
        """Register mean-ablation pre-hooks for a random f-fraction per layer."""
        handles = []
        for li in layers:
            if arm == "heads":
                n_abl = round(f * n_heads)
                heads = rng.choice(n_heads, n_abl, replace=False)
                mask = np.zeros(n_heads * head_dim, dtype=bool)
                for h in heads:
                    mask[h * head_dim:(h + 1) * head_dim] = True
                mt = torch.tensor(mask, device=dev)
                handles.append(dec[li].self_attn.o_proj.register_forward_pre_hook(
                    mk_ablate(head_mean_t[li], mt)))
            else:  # mlp
                n_abl = round(f * inter)
                dims = rng.choice(inter, n_abl, replace=False)
                mask = np.zeros(inter, dtype=bool)
                mask[dims] = True
                mt = torch.tensor(mask, device=dev)
                handles.append(dec[li].mlp.down_proj.register_forward_pre_hook(
                    mk_ablate(mlp_mean_t[li], mt)))
        return handles

    # ── gate-0: clean SNR_0 (no ablation) ──────────────────────────────────────
    clean = np.array([margin(lm) for lm in valid])
    snr0 = float(clean.mean())
    snr0_se = float(clean.std(ddof=1) / np.sqrt(len(clean)))
    gate0 = bool(snr0 > 3 * snr0_se and snr0 > 0)
    print(f"[frag] gate-0: SNR_0={snr0:.3f} SE={snr0_se:.3f} expressed={gate0}")

    f_grid = list(args.f_grid)
    arms = args.arms

    def run_arm(arm, layers, tag):
        per_f, mean_curve, raw = {}, [], {}
        for f in f_grid:
            draws = np.zeros((args.draws, len(valid)))
            for ri in range(args.draws):
                abl = sample_ablation(arm, f, layers)
                draws[ri] = [margin(lm) for lm in valid]
                for hd in abl:
                    hd.remove()
            per_f[f] = ldi_at_f(draws, rng)
            mean_curve.append(float(draws.mean()))
            raw[f] = draws.tolist()
            pv = per_f[f]["p"]
            print(f"  [{tag}] f={f:.2f} SNR={per_f[f]['mean']:.3f} "
                  f"LDI={per_f[f]['ldi']:.2f} p={pv}")
        cliff = cliff_stat(f_grid, mean_curve, snr0)
        verdict = aggregate_verdict(per_f, cliff, args.alpha, args.cliff_thresh)
        print(f"  [{tag}] cliff_ratio={cliff['cliff_ratio']:.2f} "
              f"median_LDI={verdict['median_ldi_verdict_band']:.2f} "
              f"-> {verdict['call']}")
        return {"per_f": {f"{f}": per_f[f] for f in f_grid},
                "mean_curve": mean_curve, "cliff": cliff,
                "verdict": verdict, "raw_margins": raw}

    result = {
        "model_id": args.model_id, "seed": args.seed, "scale": S,
        "ref_layer": L, "n_layers": n_layers, "band": band,
        "f_grid": f_grid, "draws": args.draws, "n_probes": len(valid),
        "valid_landmarks": valid, "alpha": args.alpha,
        "cliff_thresh": args.cliff_thresh, "gate0": {
            "snr0": snr0, "snr0_se": snr0_se, "expressed": gate0},
        "arms": {}}

    for arm in arms:
        print(f"\n── arm: {arm.upper()} (band, in-band) ──")
        result["arms"][arm] = run_arm(arm, band, arm)
        # out-of-band matched-fraction control (should barely move SNR)
        if args.control and out_band:
            print(f"── arm: {arm.upper()} (out-of-band control) ──")
            result["arms"][f"{arm}_oob"] = run_arm(arm, out_band, f"{arm}_oob")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "holo_frag.json").write_text(json.dumps(result, indent=2))
    print(f"\n[frag] wrote {out}/holo_frag.json")
    if not gate0:
        print("[frag] ⚠ gate-0 FAILED — SNR_0 within noise; verdict INCONCLUSIVE")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="P-HOLO-FRAG fragment test")
    ap.add_argument("--validate", action="store_true",
                    help="no-model self-test of the LDI + cliff detectors")
    ap.add_argument("--model-id", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16", choices=["float32", "bfloat16"])
    ap.add_argument("--ref-layer", type=int, default=9)
    ap.add_argument("--scale", type=float, default=2.0)
    ap.add_argument("--draws", type=int, default=30)
    ap.add_argument("--f-grid", type=float, nargs="+", default=list(F_GRID_DEFAULT))
    ap.add_argument("--arms", nargs="+", default=["heads", "mlp"],
                    choices=["heads", "mlp"])
    ap.add_argument("--band", type=int, nargs=2, default=None,
                    metavar=("LO", "HI"), help="fixed band override (else find_band)")
    ap.add_argument("--n-null-band", type=int, default=200)
    ap.add_argument("--control", action="store_true", help="out-of-band control arm")
    ap.add_argument("--alpha", type=float, default=0.05)
    ap.add_argument("--cliff-thresh", type=float, default=2.5)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--out", default="results/holo-frag/qwen3-4b")
    args = ap.parse_args()
    if args.validate:
        return run_validate(args.alpha, args.cliff_thresh)
    return run_model(args)


if __name__ == "__main__":
    raise SystemExit(main())
