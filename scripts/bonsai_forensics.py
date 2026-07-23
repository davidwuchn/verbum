"""Bonsai ternarization forensics: reverse-engineer the parent→ternary map.

We hold both endpoints of PrismML's (undisclosed) ternarization:
  parent: Qwen/Qwen3.6-27B (FP bf16, HF cache)
  child:  bonsai27b-unpacked (materialized ternary: {-s_g, 0, +s_g} per group of 128)

Method signatures (per tensor, per group g of 128 along in_features):
  s_g   = max|w_q|                 (exact, by construction of unpacked format)
  t     = sign(w_q)                (exact)

  1. flip_rate      — fraction where t != nearest-ternary(parent w | s_g)
                      (nearest at threshold s_g/2).  ~0 => no error compensation,
                      no QAT drift.  structured/large => compensated PTQ or QAT.
  2. sign_viol      — fraction where t != 0 and sign(t) != sign(parent w).
                      >0 => weights crossed zero => training/compensation.
  3. sep_rate       — fraction of groups where a threshold Delta_g exists with
                      t = sign(w) * [|w| > Delta_g] EXACTLY
                      (max|w| over t=0  <  min|w| over t!=0).
                      1.0 => pure magnitude-threshold rule on parent weights.
  4. scale closed forms — corr(s_g, mean|w| over support)  [TWN-optimal scale]
                          corr(s_g, <w,t>/<t,t>)           [least-squares scale]
                          ratio distributions.
  5. threshold ratio — Delta_g / mean|w|_g  (TWN predicts ~0.7; absmean predicts
                          a different constant; learned thresholds => spread).

Usage:
  uv run python scripts/bonsai_forensics.py --tensors auto --depths 0.1 0.3 0.5 0.7 0.9
  uv run python scripts/bonsai_forensics.py --tensors model.layers.32.mlp.down_proj.weight
"""

from __future__ import annotations

import argparse
import glob
import json
import time
from pathlib import Path

import torch
from safetensors import safe_open

BONSAI_DIR = Path("/Users/mwhitford/localai/models/bonsai27b-unpacked")
PARENT_GLOB = "/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/"
GROUP = 128
DEVICE = "mps" if torch.backends.mps.is_available() else "cpu"


def forensics_binary(w: torch.Tensor, wq: torch.Tensor) -> dict:
    """Binary (1-bit) child vs FP parent.  Code = sign, boundary at 0.

    Signatures: sign-flip rate vs parent (the ONLY topology edit available
    without a zero waypoint), scale-vs-absmean (BitNet 1-bit rule s=mean|w|),
    flip boundary distances, channel structure.
    """
    assert w.shape == wq.shape, (w.shape, wq.shape)
    out_f, in_f = w.shape
    ng = in_f // GROUP
    w = w.to(DEVICE, torch.float32).reshape(out_f, ng, GROUP)
    wq = wq.to(DEVICE, torch.float32).reshape(out_f, ng, GROUP)

    def q(x: torch.Tensor, p: float) -> float:
        x = x.flatten().float()
        if not x.numel():
            return float("nan")
        if x.numel() > 10_000_000:
            x = x[torch.randint(0, x.numel(), (10_000_000,), device=x.device)]
        return torch.quantile(x, p).item()

    s = wq.abs().amax(dim=-1, keepdim=True)
    t = torch.sign(wq)
    flips = (t != torch.sign(w)) & (s > 0)
    flip_rate = flips.float().mean().item()

    mean_abs = w.abs().mean(dim=-1)
    s_flat = s.squeeze(-1)
    m = s_flat > 0

    def corr(a: torch.Tensor, b: torch.Tensor) -> float:
        a = a[m].flatten().float(); b = b[m].flatten().float()
        a = a - a.mean(); b = b - b.mean()
        return (a @ b / (a.norm() * b.norm() + 1e-30)).item()

    rel = (w.abs() / s.clamp(min=1e-30))[flips]
    w_hat = s * t
    n_blocks = 16
    fpb = flips.reshape(out_f, -1).float()
    fpb = fpb.reshape(out_f, n_blocks, in_f // n_blocks).mean(dim=(0, 2))
    ch_flips = flips.reshape(out_f, -1).float().sum(dim=0)
    mu = out_f * flip_rate
    sd = max((out_f * flip_rate * (1 - flip_rate)) ** 0.5, 1e-9)
    ch_z = (ch_flips - mu) / sd
    return {
        "mode": "binary",
        "n_params": w.numel(),
        "flip_rate": flip_rate,
        "n_flips": int(flips.sum().item()),
        "corr_s_absmean": corr(s_flat, mean_abs),
        "s_over_absmean_q25_50_75": [q(s_flat[m] / mean_abs[m].clamp(min=1e-30), p)
                                     for p in (0.25, 0.5, 0.75)],
        "flip_boundary_q05_25_50_75_95": [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)]
                                         if flips.any() else [],
        "cos_w_what": torch.nn.functional.cosine_similarity(
            w.flatten(), w_hat.flatten(), dim=0).item(),
        "rel_l2": ((w - w_hat).norm() / w.norm()).item(),
        "flip_col_profile": [round(x, 5) for x in fpb.tolist()],
        "chan_flip_z_q50_95_999": [q(ch_z, p) for p in (0.5, 0.95, 0.999)],
        "chan_flip_z_max": ch_z.max().item(),
    }


def build_index(model_dir: Path) -> dict[str, Path]:
    """tensor name -> shard path, from safetensors index or by scanning."""
    idx_file = model_dir / "model.safetensors.index.json"
    if idx_file.exists():
        idx = json.load(open(idx_file))["weight_map"]
        return {k: model_dir / v for k, v in idx.items()}
    out: dict[str, Path] = {}
    for shard in sorted(model_dir.glob("*.safetensors")):
        with safe_open(shard, "pt") as f:
            for k in f.keys():
                out[k] = shard
    return out


def load_tensor(index: dict[str, Path], name: str) -> torch.Tensor:
    with safe_open(index[name], "pt") as f:
        return f.get_tensor(name)


def forensics_one(w: torch.Tensor, wq: torch.Tensor) -> dict:
    """All signatures for one (parent, child) tensor pair. Runs on DEVICE."""
    assert w.shape == wq.shape, (w.shape, wq.shape)
    out_f, in_f = w.shape
    n_groups_row = in_f // GROUP

    w = w.to(DEVICE, torch.float32).reshape(out_f, n_groups_row, GROUP)
    wq = wq.to(DEVICE, torch.float32).reshape(out_f, n_groups_row, GROUP)

    s = wq.abs().amax(dim=-1, keepdim=True)                     # (out, ng, 1)
    t = torch.sign(wq)                                          # exact ternary code
    nz = t != 0
    n = w.numel()

    # -- 1. flip rate vs nearest-ternary of parent given s
    def q(x: torch.Tensor, p: float) -> float:
        x = x.flatten().float()
        if not x.numel():
            return float("nan")
        if x.numel() > 10_000_000:                  # quantile() size limit + speed
            x = x[torch.randint(0, x.numel(), (10_000_000,), device=x.device)]
        return torch.quantile(x, p).item()
    live = s.squeeze(-1) > 0                                    # groups with any support
    t_nn = torch.sign(w) * (w.abs() > (s / 2))
    flips = (t != t_nn) & live.unsqueeze(-1)
    flip_rate = flips.float().mean().item()

    # -- 2. sign violations on support
    sign_viol = ((nz) & (torch.sign(w) != t)).float().sum().item() / max(nz.sum().item(), 1)

    # -- 3. exact threshold separability per group
    big = torch.finfo(torch.float32).max
    absw = w.abs()
    max_zero = torch.where(~nz, absw, torch.zeros_like(absw)).amax(dim=-1)      # (out, ng)
    min_nonzero = torch.where(nz, absw, torch.full_like(absw, big)).amin(dim=-1)
    has_zero = (~nz).any(dim=-1)
    has_nonzero = nz.any(dim=-1)
    mixed = has_zero & has_nonzero
    sep = torch.ones_like(max_zero, dtype=torch.bool)
    sep[mixed] = max_zero[mixed] < min_nonzero[mixed]
    sep_rate = sep.float().mean().item()

    # implied threshold per mixed group (midpoint), ratio to mean|w|
    delta = (max_zero + torch.where(mixed, min_nonzero, max_zero)) / 2
    mean_abs = absw.mean(dim=-1)
    delta_ratio = (delta[mixed] / mean_abs[mixed])

    # -- 4. scale closed forms (per group, over support)
    supp_cnt = nz.sum(dim=-1).clamp(min=1)
    s_twn = (absw * nz).sum(dim=-1) / supp_cnt                  # mean |w| over support
    s_ls = (w * t).sum(dim=-1) / supp_cnt                       # <w,t>/<t,t>
    s_flat = s.squeeze(-1)
    m = live & has_nonzero

    def corr(a: torch.Tensor, b: torch.Tensor) -> float:
        a = a[m].flatten().float()
        b = b[m].flatten().float()
        a = a - a.mean(); b = b - b.mean()
        return (a @ b / (a.norm() * b.norm() + 1e-30)).item()

    ratio_twn = (s_flat[m] / s_twn[m])

    # -- 5. zero fraction
    zero_frac = (~nz).float().mean().item()

    # -- 6. flip locality: rate per column-block along in_features (GPTQ-style
    #       sequential compensation accumulates error along quantization order;
    #       QAT drift is diffuse/flat)
    n_blocks = 16
    fpb = flips.reshape(out_f, -1).float()          # (out, in_f)
    fpb = fpb.reshape(out_f, n_blocks, in_f // n_blocks).mean(dim=(0, 2))
    flip_col_profile = [round(x, 5) for x in fpb.tolist()]

    # -- 7. flip boundary distance: |w|/s at flip sites. Boundary-hugging
    #       (~0.5) => tiny perturbations suffice; broad => genuine drift.
    rel = (absw / s.clamp(min=1e-30))[flips]
    flip_boundary_q = [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)] if flips.any() else []

    # -- 8. global drift: how well does the dequantized child approximate the
    #       parent pointwise?  cos ~1 => static approximation of parent;
    #       cos low => function-matching without weight-matching (distill/QAT).
    w_hat = s * t
    cos_w = torch.nn.functional.cosine_similarity(
        w.flatten(), w_hat.flatten(), dim=0).item()
    rel_l2 = ((w - w_hat).norm() / w.norm()).item()

    # -- 9. soft-threshold (proximal / LASSO-flavored) scale closed form:
    #       s_soft = mean(|w| - Delta over support).  Explains shrinkage if
    #       the method is a prox operator rather than LS projection.
    d_full = delta.unsqueeze(-1)                                # (out, ng, 1)
    s_soft = ((absw - d_full).clamp(min=0) * nz).sum(dim=-1) / supp_cnt
    corr_s_soft = corr(s_flat, s_soft)
    ratio_soft = (s_flat[m] / s_soft[m].clamp(min=1e-30))

    # -- 9b. absmean hypothesis (BitNet b1.58 recipe, group-wise):
    #        t? = clip(round(w / mean|w|_g)), s? = mean|w|_g.
    #        Exact-match rates against the actual child code/scale.
    s_abs = mean_abs.unsqueeze(-1)                              # mean|w| whole group
    t_abs = torch.clamp(torch.round(w / s_abs.clamp(min=1e-30)), -1, 1)
    absmean_code_match = ((t_abs == t) | ~live.unsqueeze(-1)).float().mean().item()
    ratio_s_absmean = (s_flat[m] / mean_abs[m].clamp(min=1e-30))
    corr_s_absmean = corr(s_flat, mean_abs)

    # -- 9c. transition matrix parent-RTN code -> child code.
    #        The optimizer's fossil record: sign reversals via the zero state
    #        (promotion/demotion churn) vs direct +/- jumps.  Reversal sites'
    #        |w|/s tells whether reversals target confident parent weights.
    tm = {}
    for a in (-1, 0, 1):
        pa = t_abs == a
        for b in (-1, 0, 1):
            tm[f"{a}->{b}"] = int((pa & (t == b)).sum().item())
    rev = (t_abs * t) == -1
    rev_mag_q = [q((absw / s.clamp(min=1e-30))[rev], p)
                 for p in (0.25, 0.5, 0.75)] if rev.any() else []
    n_nz = int((t_abs != 0).sum().item())
    trans = {
        "promotions_0_to_pm": tm["0->1"] + tm["0->-1"],
        "demotions_pm_to_0": tm["1->0"] + tm["-1->0"],
        "reversals_direct": tm["1->-1"] + tm["-1->1"],
        "stay": tm["0->0"] + tm["1->1"] + tm["-1->-1"],
        "reversal_rate_vs_nonzero": (tm["1->-1"] + tm["-1->1"]) / max(n_nz, 1),
        "reversal_mag_q25_50_75": rev_mag_q,
        "matrix": tm,
    }

    # -- 10. flip structure per input channel: z-score of max channel flip
    #        count vs binomial null.  High z => certain input channels are
    #        systematically rewired (activation-aware compensation);
    #        z ~ null => spatially unstructured drift.
    ch_flips = flips.reshape(out_f, -1).float().sum(dim=0)      # per input channel
    p_hat = flip_rate
    mu = out_f * p_hat
    sd = max((out_f * p_hat * (1 - p_hat)) ** 0.5, 1e-9)
    ch_z = (ch_flips - mu) / sd
    chan_z_q = [q(ch_z, p) for p in (0.5, 0.95, 0.999)]
    chan_z_max = ch_z.max().item()

    return {
        "n_params": n,
        "flip_rate": flip_rate,
        "n_flips": int(flips.sum().item()),
        "sign_viol_rate": sign_viol,
        "sep_rate": sep_rate,
        "zero_frac": zero_frac,
        "corr_s_twn": corr(s_flat, s_twn),
        "corr_s_ls": corr(s_flat, s_ls),
        "s_over_twn_q25_50_75": [q(ratio_twn, p) for p in (0.25, 0.5, 0.75)],
        "delta_over_meanabs_q25_50_75": [q(delta_ratio, p) for p in (0.25, 0.5, 0.75)],
        "flip_col_profile": flip_col_profile,
        "flip_boundary_q05_25_50_75_95": flip_boundary_q,
        "cos_w_what": cos_w,
        "rel_l2": rel_l2,
        "corr_s_soft": corr_s_soft,
        "s_over_soft_q25_50_75": [q(ratio_soft, p) for p in (0.25, 0.5, 0.75)],
        "absmean_code_match": absmean_code_match,
        "corr_s_absmean": corr_s_absmean,
        "s_over_absmean_q25_50_75": [q(ratio_s_absmean, p) for p in (0.25, 0.5, 0.75)],
        "chan_flip_z_q50_95_999": chan_z_q,
        "chan_flip_z_max": chan_z_max,
        "transitions": trans,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--tensors", nargs="+", default=["auto"])
    ap.add_argument("--depths", nargs="+", type=float, default=[0.5])
    ap.add_argument("--out", default=None, help="write JSON here")
    ap.add_argument("--child-dir", default=str(BONSAI_DIR),
                    help="unpacked child model dir (ternary or binary)")
    args = ap.parse_args()

    child_dir = Path(args.child_dir)
    parent_dir = Path(glob.glob(PARENT_GLOB)[0])
    print(f"device={DEVICE}  parent={parent_dir.name}  child={child_dir.name}")
    t0 = time.time()
    child_idx = build_index(child_dir)
    parent_idx = build_index(parent_dir)
    print(f"indexed: child={len(child_idx)} parent={len(parent_idx)} tensors "
          f"({time.time()-t0:.1f}s)")

    # parent (Qwen3.6-27B) is also VLM-wrapped: names are identical
    def to_parent(name: str) -> str:
        return name

    layer_ids = sorted({int(k.split(".layers.")[1].split(".")[0])
                        for k in child_idx if ".layers." in k})
    n_layers = len(layer_ids)

    if args.tensors == ["auto"]:
        names = []
        for d in args.depths:
            lid = layer_ids[min(int(d * n_layers), n_layers - 1)]
            for proj in ("mlp.down_proj", "mlp.gate_proj", "self_attn.q_proj",
                         "self_attn.o_proj", "linear_attn.in_proj_qkv",
                         "linear_attn.out_proj"):
                cand = f"model.language_model.layers.{lid}.{proj}.weight"
                if cand in child_idx:
                    names.append(cand)
        for extra in ("model.language_model.embed_tokens.weight", "lm_head.weight",
                      "model.lm_head.weight"):
            if extra in child_idx:
                names.append(extra)
    else:
        names = [n if n in child_idx
                 else "model.language_model." + n.removeprefix("model.")
                 for n in args.tensors]

    print(f"n_layers={n_layers}  probing {len(names)} tensors\n")
    results = {}
    for name in names:
        pname = to_parent(name)
        if pname not in parent_idx:
            print(f"SKIP {name}: parent tensor {pname} not found")
            continue
        t0 = time.time()
        wq_probe = load_tensor(child_idx, name)
        # auto-detect binary vs ternary: any exact zeros in the child?
        is_binary = not bool((wq_probe[: min(64, wq_probe.shape[0])] == 0).any().item())
        fn = forensics_binary if is_binary else forensics_one
        r = fn(load_tensor(parent_idx, pname), wq_probe)
        r["elapsed_s"] = round(time.time() - t0, 2)
        results[name] = r
        if is_binary:
            print(f"{name}  [BINARY]")
            print(f"  flip_rate={r['flip_rate']:.3e} ({r['n_flips']} / {r['n_params']:,})"
                  f"  cos(w,ŵ)={r['cos_w_what']:.4f}  rel_l2={r['rel_l2']:.4f}")
            print(f"  corr(s,absmean)={r['corr_s_absmean']:.4f}"
                  f"  s/absmean q25-75={['%.3f' % x for x in r['s_over_absmean_q25_50_75']]}")
            print(f"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}")
            print(f"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}")
            print(f"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}"
                  f"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\n")
            continue
        print(f"{name}")
        print(f"  flip_rate={r['flip_rate']:.3e} ({r['n_flips']} flips / {r['n_params']:,})"
              f"  sign_viol={r['sign_viol_rate']:.3e}  sep_rate={r['sep_rate']:.4f}")
        print(f"  zero_frac={r['zero_frac']:.3f}  corr(s,twn)={r['corr_s_twn']:.4f}"
              f"  corr(s,ls)={r['corr_s_ls']:.4f}")
        print(f"  s/twn q25-75={['%.3f' % x for x in r['s_over_twn_q25_50_75']]}"
              f"  Δ/mean|w| q25-75={['%.3f' % x for x in r['delta_over_meanabs_q25_50_75']]}")
        print(f"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}")
        print(f"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}")
        print(f"  cos(w,ŵ)={r['cos_w_what']:.4f}  rel_l2={r['rel_l2']:.4f}"
              f"  corr(s,soft)={r['corr_s_soft']:.4f}"
              f"  s/soft q25-75={['%.3f' % x for x in r['s_over_soft_q25_50_75']]}")
        print(f"  ABSMEAN: code_match={r['absmean_code_match']:.4f}"
              f"  corr(s,absmean)={r['corr_s_absmean']:.4f}"
              f"  s/absmean q25-75={['%.3f' % x for x in r['s_over_absmean_q25_50_75']]}")
        tr = r["transitions"]
        tot = max(sum(tr["matrix"].values()), 1)
        print(f"  TRANSITIONS: promote(0→±)={tr['promotions_0_to_pm']/tot:.4f}"
              f"  demote(±→0)={tr['demotions_pm_to_0']/tot:.4f}"
              f"  REVERSE(±→∓)={tr['reversals_direct']/tot:.5f}"
              f"  rev/nonzero={tr['reversal_rate_vs_nonzero']:.5f}")
        print(f"  reversal |w|/s q25-75={['%.3f' % x for x in tr['reversal_mag_q25_50_75']]}")
        print(f"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}"
              f"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\n")

    if args.out:
        Path(args.out).parent.mkdir(parents=True, exist_ok=True)
        json.dump({"device": DEVICE, "group": GROUP, "results": results},
                  open(args.out, "w"), indent=2)
        print(f"wrote {args.out}")


if __name__ == "__main__":
    main()
