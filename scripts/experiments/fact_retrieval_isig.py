"""Fact retrieval = I-signature test.

Hypothesis (user, s202): fact retrieval bypasses the composition
combinators — attention does a relation/graph lookup, then I forwards
the retrieved value. Prediction: fact-recall prompts should carry the
SAME mechanical signature as the I (identity) combinator, distinct from
B/C (composition):

  - LOW attention entropy (sharp lookup), like I, unlike B/C
  - opcode-energy profile (common-mode-removed fingerprints) closest to
    I, not to B/C
  - (context) FFN fraction

This cross-validates the I-finding on a totally different probe set:
if fact-recall ≈ I-signature, "I is overloaded as identity + retrieval"
gets real support.

Usage:
    uv run python scripts/experiments/fact_retrieval_isig.py \
        --model Qwen/Qwen3-14B --device mps --n-perm 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.probes.library import crystal_probes  # noqa: E402

OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
RESULTS_DIR = _ROOT / "results" / "fact-isig"


def log(m):
    print(m, file=sys.stderr, flush=True)


def is_prose(p):
    return ("λ" not in p.prompt) and ("lambda" not in p.prompt.lower())


def load_fingerprints_cmr(slug):
    d = np.load(_ROOT / "results" / "hologram-reader" / slug / "opcode_map.npz")
    fps = np.stack([d[f"fp_{op}"] for op in OPS], 0)        # (O,L,D)
    common = fps.mean(0, keepdims=True)
    resid = fps - common
    return resid / np.maximum(np.linalg.norm(resid, axis=2, keepdims=True), 1e-9)


def capture(model, tok, prompts, device, nL):
    """Per probe: per-layer attn norm, ffn norm, ffn-out vector, attn entropy."""
    A = np.zeros((len(prompts), nL))
    F = np.zeros((len(prompts), nL))
    H = np.full((len(prompts), nL), np.nan)
    FV = np.zeros((len(prompts), nL, model.config.hidden_size), dtype=np.float32)
    acap, fcap = {}, {}
    hooks = []
    for li in range(nL):
        lyr = model.model.layers[li]
        def mk_a(layer):
            def fn(m, i, o):
                v = o[0] if isinstance(o, tuple) else o
                acap[layer] = v[:, -1, :].detach().float().cpu().numpy()
            return fn
        def mk_f(layer):
            def fn(m, i, o):
                fcap[layer] = o[:, -1, :].detach().float().cpu().numpy()
            return fn
        hooks.append(lyr.self_attn.register_forward_hook(mk_a(li)))
        hooks.append(lyr.mlp.down_proj.register_forward_hook(mk_f(li)))
    for pi, prompt in enumerate(prompts):
        acap.clear(); fcap.clear()
        ids = tok.encode(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        with torch.no_grad():
            out = model(ids, output_attentions=True)
        for li in range(nL):
            if li in acap:
                A[pi, li] = np.linalg.norm(acap[li][0])
            if li in fcap:
                v = fcap[li][0]
                F[pi, li] = np.linalg.norm(v)
                FV[pi, li] = v
        att = getattr(out, "attentions", None)
        if att is not None and att[0] is not None:
            for li in range(min(nL, len(att))):
                if att[li] is None:
                    continue
                w = att[li][0, :, -1, :].detach().float().cpu().numpy()
                w = w / np.maximum(w.sum(1, keepdims=True), 1e-9)
                H[pi, li] = float((-(w * np.log(w + 1e-12)).sum(1)).mean())
        if (pi + 1) % 100 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    return A, F, H, FV


def zoneB(x, nL):
    a, b = int(nL * 0.3), int(nL * 0.7)
    return np.nanmean(x[:, a:b], axis=1)


def opcode_profile(FV, fps):
    """mean over probes of summed-over-layer opcode energy, normalized → (8,)."""
    E = np.einsum("pld,old->po", FV, fps)   # (P, O)
    v = E.mean(0)
    return v / (np.linalg.norm(v) + 1e-9), E


def perm_diff(scalar_a, scalar_b, n_perm, rng, lower=True):
    """Is mean(a) − mean(b) extreme vs shuffling the a/b assignment?"""
    s = np.concatenate([scalar_a, scalar_b])
    na = len(scalar_a)
    true = scalar_a.mean() - scalar_b.mean()
    null = []
    idx = np.arange(len(s))
    for _ in range(n_perm):
        rng.shuffle(idx)
        null.append(s[idx[:na]].mean() - s[idx[na:]].mean())
    null = np.array(null)
    p = float((np.sum(null <= true) + 1) / (n_perm + 1)) if lower \
        else float((np.sum(null >= true) + 1) / (n_perm + 1))
    return {"diff": float(true), "p_value": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    slug = args.model.replace("/", "_")
    fps = load_fingerprints_cmr(slug)

    # probe groups
    cp = [p for p in crystal_probes() if is_prose(p)]
    groups = {op: [p.prompt for p in cp if p.combinator == op] for op in ["I", "B", "C", "K"]}
    fact = []
    for fn in ["probes/fact_recall_extended.json", "probes/fact_recall.json"]:
        try:
            d = json.load(open(_ROOT / fn))
            ps = d.get("probes", d) if isinstance(d, dict) else d
            fact += [(p.get("prompt") or p.get("text")) for p in ps]
        except Exception:
            pass
    fact = list(dict.fromkeys([f for f in fact if f]))   # dedup
    groups["FACT"] = fact
    log(f"  groups: { {k: len(v) for k,v in groups.items()} }")

    from transformers import AutoModelForCausalLM, AutoTokenizer
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16, trust_remote_code=True,
        attn_implementation="eager",
        device_map=args.device if args.device != "mps" else None)
    if args.device == "mps":
        model = model.to(args.device)
    model.eval()
    nL = model.config.num_hidden_layers

    ent, ffrac, prof = {}, {}, {}
    for g, prompts in groups.items():
        log(f"  capturing {g} ({len(prompts)}) ...")
        A, F, H, FV = capture(model, tok, prompts, args.device, nL)
        ent[g] = zoneB(H, nL)
        ffrac[g] = zoneB(F / np.maximum(F + A, 1e-9), nL)
        prof[g], _ = opcode_profile(FV, fps)
    del model, tok

    # ── tests ──
    out = {"model": args.model, "group_sizes": {k: len(v) for k, v in groups.items()},
           "mean_attn_entropy": {g: float(np.nanmean(ent[g])) for g in groups},
           "mean_ffn_fraction": {g: float(np.nanmean(ffrac[g])) for g in groups}}

    # 1. fact entropy LOW like I, vs B/C?
    bc = np.concatenate([ent["B"], ent["C"]])
    out["fact_entropy_vs_BC"] = perm_diff(ent["FACT"], bc, args.n_perm, rng, lower=True)
    out["fact_entropy_vs_I"] = perm_diff(ent["FACT"], ent["I"], args.n_perm, rng, lower=True)

    # 2. fact opcode profile closest to I?
    cos = {g: float(prof["FACT"] @ prof[g]) for g in ["I", "B", "C", "K"]}
    out["fact_profile_cosine"] = cos
    out["fact_profile_argmax_op"] = OPS[int(np.argmax(prof["FACT"]))]
    out["fact_closest_combinator"] = max(cos, key=cos.get)

    with open(RESULTS_DIR / f"{slug}.json", "w") as f:
        json.dump(out, f, indent=2)

    log("\n══════ FACT = I-SIGNATURE ══════")
    log(f"  attn entropy:  FACT={out['mean_attn_entropy']['FACT']:.3f}  "
        f"I={out['mean_attn_entropy']['I']:.3f}  B={out['mean_attn_entropy']['B']:.3f}  "
        f"C={out['mean_attn_entropy']['C']:.3f}  K={out['mean_attn_entropy']['K']:.3f}")
    log(f"    FACT vs (B,C): diff={out['fact_entropy_vs_BC']['diff']:+.3f} "
        f"p={out['fact_entropy_vs_BC']['p_value']:.4f} (FACT lower predicted)")
    log(f"    FACT vs I:     diff={out['fact_entropy_vs_I']['diff']:+.3f} "
        f"p={out['fact_entropy_vs_I']['p_value']:.4f} (similar→not lower)")
    log(f"  FFN fraction:  FACT={out['mean_ffn_fraction']['FACT']:.3f}  "
        f"I={out['mean_ffn_fraction']['I']:.3f}  B={out['mean_ffn_fraction']['B']:.3f}")
    log(f"  CMR opcode profile cosine to: {{ {', '.join(f'{k}:{v:+.2f}' for k,v in cos.items())} }}")
    log(f"    fact argmax opcode = {out['fact_profile_argmax_op']}  "
        f"closest combinator = {out['fact_closest_combinator']}")
    log(f"  saved → {RESULTS_DIR / f'{slug}.json'}")


if __name__ == "__main__":
    main()
