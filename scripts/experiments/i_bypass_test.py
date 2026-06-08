"""I-bypass test — is the I combinator a distinct circuit (identity + FFN
retrieval) rather than an attention-composition combinator like B/C?

Hypothesis (user, session 202): the basis is exactly 4 (K,I,B,C) not SKI
because I plays a structurally distinct role — it is overloaded as
identity AND the FFN key/value lookup, "bypassing" the attention-driven
β-reduction that B/C perform.

Falsifiable predictions, per probe (last token), aggregated over layers:
  P1  FFN fraction  = ‖ffn_out‖ / (‖ffn_out‖+‖attn_out‖)
      → I HIGH (writes via FFN retrieval), B/C LOW (write via attention).
  P2  attention entropy (last-token dist, mean over heads/layers)
      → I LOW (sharp copy-forward), B/C HIGH (distributed composition).
  P3  attention self/near focus (weight on last few positions)
      → I HIGH (forward own value), B/C LOWer.

Verdict via permutation: is I's signature separated from {B,C} beyond
random reassignment of probe labels?

Usage:
    uv run python scripts/experiments/i_bypass_test.py \
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
RESULTS_DIR = _ROOT / "results" / "i-bypass"


def log(m):
    print(m, file=sys.stderr, flush=True)


def is_prose(p):
    return ("λ" not in p.prompt) and ("lambda" not in p.prompt.lower())


def capture(model, tok, prompts, device, nL):
    """Per probe, per layer: attn_out norm, ffn_out norm, last-token attn entropy + near-focus."""
    A = np.zeros((len(prompts), nL))   # attn output norm
    F = np.zeros((len(prompts), nL))   # ffn output norm
    H = np.full((len(prompts), nL), np.nan)   # attn entropy
    NF = np.full((len(prompts), nL), np.nan)  # near-focus (weight on last 3 positions)
    attn_cap, ffn_cap = {}, {}
    hooks = []
    for li in range(nL):
        lyr = model.model.layers[li]
        def mk_a(layer):
            def fn(m, i, o):
                v = o[0] if isinstance(o, tuple) else o
                attn_cap[layer] = v[:, -1, :].detach().float().cpu().numpy()
            return fn
        def mk_f(layer):
            def fn(m, i, o):
                ffn_cap[layer] = o[:, -1, :].detach().float().cpu().numpy()
            return fn
        hooks.append(lyr.self_attn.register_forward_hook(mk_a(li)))
        hooks.append(lyr.mlp.down_proj.register_forward_hook(mk_f(li)))

    for pi, prompt in enumerate(prompts):
        attn_cap.clear(); ffn_cap.clear()
        ids = tok.encode(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        with torch.no_grad():
            out = model(ids, output_attentions=True)
        for li in range(nL):
            if li in attn_cap:
                A[pi, li] = np.linalg.norm(attn_cap[li][0])
            if li in ffn_cap:
                F[pi, li] = np.linalg.norm(ffn_cap[li][0])
        att = getattr(out, "attentions", None)
        if att is not None and att[0] is not None:
            S = ids.shape[1]
            for li in range(min(nL, len(att))):
                if att[li] is None:
                    continue
                w = att[li][0, :, -1, :].detach().float().cpu().numpy()  # (heads, S)
                w = w / np.maximum(w.sum(1, keepdims=True), 1e-9)
                ent = -(w * np.log(w + 1e-12)).sum(1)         # per head
                H[pi, li] = float(ent.mean())
                near = w[:, max(0, S - 3):].sum(1)            # weight on last 3 positions
                NF[pi, li] = float(near.mean())
        if (pi + 1) % 100 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    ffn_frac = F / np.maximum(F + A, 1e-9)
    return ffn_frac, H, NF


def zoneB(x, nL):
    a, b = int(nL * 0.3), int(nL * 0.7)
    return np.nanmean(x[:, a:b], axis=1)  # per-probe scalar over zone B


def perm_test_group(scalar, y, target_idx, other_idx, n_perm, rng, higher=True):
    """Is mean(scalar[target]) − mean(scalar[other]) extreme vs label shuffles?"""
    mask = np.isin(y, [target_idx] + other_idx)
    s = scalar[mask]
    yy = y[mask]
    def stat(lab):
        t = s[lab == target_idx].mean()
        o = s[np.isin(lab, other_idx)].mean()
        return t - o
    true = stat(yy)
    null = []
    for _ in range(n_perm):
        p = yy.copy(); rng.shuffle(p)
        null.append(stat(p))
    null = np.array(null)
    p = float((np.sum(null >= true) + 1) / (n_perm + 1)) if higher \
        else float((np.sum(null <= true) + 1) / (n_perm + 1))
    return {"diff": float(true), "null_mean": float(null.mean()),
            "null_std": float(null.std()), "p_value": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    probes = [p for p in crystal_probes() if p.combinator in OPS and is_prose(p)]
    y = np.array([OPS.index(p.combinator) for p in probes])
    log(f"  prose probes: {len(probes)}  per-op: "
        f"{ {OPS[i]: int((y==i).sum()) for i in range(len(OPS))} }")

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

    log("  capturing circuit signatures ...")
    ffn_frac, H, NF = capture(model, tok, [p.prompt for p in probes], args.device, nL)
    del model, tok

    I, B, C, K = OPS.index("I"), OPS.index("B"), OPS.index("C"), OPS.index("K")
    metrics = {
        "ffn_fraction": (zoneB(ffn_frac, nL), True),   # I higher?
        "attn_entropy": (zoneB(H, nL), False),         # I lower?
        "near_focus":   (zoneB(NF, nL), True),         # I higher?
    }
    out = {"model": args.model, "n_probes": len(probes), "n_layers": nL,
           "per_op_means": {}, "tests_I_vs_BC": {}, "tests_I_vs_KBC": {}}

    # per-op means for each metric
    for name, (sc, _) in metrics.items():
        out["per_op_means"][name] = {OPS[i]: float(np.nanmean(sc[y == i]))
                                     for i in range(len(OPS)) if (y == i).any()}

    log("\n══════ I-BYPASS RESULTS ══════")
    for name, (sc, higher) in metrics.items():
        t_bc = perm_test_group(sc, y, I, [B, C], args.n_perm, rng, higher)
        t_kbc = perm_test_group(sc, y, I, [K, B, C], args.n_perm, rng, higher)
        out["tests_I_vs_BC"][name] = t_bc
        out["tests_I_vs_KBC"][name] = t_kbc
        means = out["per_op_means"][name]
        log(f"  {name}: I={means.get('I'):.3f} K={means.get('K'):.3f} "
            f"B={means.get('B'):.3f} C={means.get('C'):.3f}  "
            f"| I−(B,C) diff={t_bc['diff']:+.4f} p={t_bc['p_value']:.4f} "
            f"({'I '+('higher' if higher else 'lower')+' predicted'})")

    with open(RESULTS_DIR / f"{args.model.replace('/', '_')}.json", "w") as f:
        json.dump(out, f, indent=2)
    log(f"  saved → {RESULTS_DIR / f'{args.model.replace('/','_')}.json'}")


if __name__ == "__main__":
    main()
