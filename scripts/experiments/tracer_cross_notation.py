"""Tracer cross-notation test — does the λ-built fingerprint fire the SAME
opcodes on pure prose (no λ) as on lambda notation?

The claim under test: the opcode fingerprints were built WITH a lambda
preamble (to locate the neurons), but once located, pure-prose prompts
fire the SAME opcodes at the SAME depths — just with less energy. If true,
the opcodes are intrinsic to language processing; λ-notation is a volume
knob, not the cause.

Three decisive measurements (one model, fingerprints already on disk):

  1. PROSE CLASSIFICATION — for pure-prose probes labeled by combinator,
     project onto the λ-built fingerprints. Does fp_B specifically catch
     B-prose (not K/C-prose)? Build the confusion matrix and permutation-
     test the diagonal. Above-chance ⇒ opcode identity is intrinsic, not
     a notation artifact.

  2. AMPLITUDE — total opcode energy on prose vs lambda probes. The claim
     predicts prose < lambda (same structure, lower gain).

  3. PROSE↔LAMBDA PROFILE MATCH — per combinator, cosine between the mean
     prose opcode-profile and the mean lambda opcode-profile, vs the cosine
     to OTHER combinators' lambda profiles (specificity). High on-diagonal,
     low off-diagonal ⇒ prose and lambda run the same op, selectively.

Usage:
    uv run python scripts/experiments/tracer_cross_notation.py \
        --model Qwen/Qwen3-0.6B --device cpu --n-perm 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.probes.library import crystal_probes  # noqa: E402

CRYSTAL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
RESULTS_DIR = _ROOT / "results" / "tracer-cross-notation"


def log(m):
    print(m, file=sys.stderr, flush=True)


def is_prose(p):
    return ("λ" not in p.prompt) and ("lambda" not in p.prompt.lower())


def load_fingerprints(model_slug):
    path = _ROOT / "results" / "hologram-reader" / model_slug / "opcode_map.npz"
    d = np.load(path)
    return {op: d[f"fp_{op}"] for op in CRYSTAL_OPS}  # each (n_layers, d_model)


def capture_ffn_output(model, tok, prompts, device, n_layers):
    """Last-token down_proj (ffn output, d_model) at every layer."""
    caps = {li: [] for li in range(n_layers)}
    hooks = []
    for li in range(n_layers):
        mlp = model.model.layers[li].mlp
        def mk(layer):
            def fn(m, i, o):
                caps[layer].append(o[:, -1, :].detach().cpu().float().numpy())
            return fn
        hooks.append(mlp.down_proj.register_forward_hook(mk(li)))
    for pi, prompt in enumerate(prompts):
        ids = tok.encode(prompt, return_tensors="pt", truncation=True,
                         max_length=128).to(device)
        with torch.no_grad():
            model(ids)
        if (pi + 1) % 100 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    # (n_prompts, n_layers, d_model)
    return np.stack([np.concatenate([caps[li][p] for li in range(n_layers)], 0)
                     for p in range(len(prompts))], 0)


def opcode_energy(ffn, fps):
    """ffn: (n_probes, n_layers, d_model) → energy (n_probes, n_ops) summed over layers."""
    n_ops = len(CRYSTAL_OPS)
    E = np.zeros((ffn.shape[0], n_ops))
    for oi, op in enumerate(CRYSTAL_OPS):
        fp = fps[op]  # (n_layers, d_model)
        # per-layer dot, summed over layers
        E[:, oi] = np.einsum("pld,ld->p", ffn, fp)
    return E


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="cpu")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    slug = args.model.replace("/", "_")
    fps = load_fingerprints(slug)

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL_OPS]
    prose = [p for p in probes if is_prose(p)]
    lam = [p for p in probes if not is_prose(p)]
    log(f"  prose probes: {len(prose)}  lambda probes: {len(lam)}")

    log(f"  Loading {args.model} ...")
    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=args.device if args.device != "mps" else None,
        trust_remote_code=True)
    if args.device == "mps":
        model = model.to(args.device)
    model.eval()
    nL = model.config.num_hidden_layers

    log("  Capturing prose ffn outputs ...")
    ffn_prose = capture_ffn_output(model, tok, [p.prompt for p in prose], args.device, nL)
    log("  Capturing lambda ffn outputs ...")
    ffn_lam = capture_ffn_output(model, tok, [p.prompt for p in lam], args.device, nL)
    del model, tok

    E_prose = opcode_energy(ffn_prose, fps)   # (n_prose, 8)
    E_lam = opcode_energy(ffn_lam, fps)       # (n_lam, 8)
    y_prose = np.array([CRYSTAL_OPS.index(p.combinator) for p in prose])
    y_lam = np.array([CRYSTAL_OPS.index(p.combinator) for p in lam])

    # ── 1. PROSE CLASSIFICATION ──
    # z-score each opcode column across prose probes (remove per-op scale/offset)
    Z = (E_prose - E_prose.mean(0)) / (E_prose.std(0) + 1e-9)
    pred = Z.argmax(1)
    acc = float((pred == y_prose).mean())
    # confusion (row=true, col=detected), row-normalized
    n_ops = len(CRYSTAL_OPS)
    conf = np.zeros((n_ops, n_ops))
    for t, d in zip(y_prose, pred):
        conf[t, d] += 1
    conf = conf / np.maximum(conf.sum(1, keepdims=True), 1)
    # permutation null: shuffle true labels
    null_acc = []
    for _ in range(args.n_perm):
        yp = y_prose.copy()
        rng.shuffle(yp)
        null_acc.append(float((pred == yp).mean()))
    p_acc = float((np.sum(np.array(null_acc) >= acc) + 1) / (args.n_perm + 1))

    # ── 2. AMPLITUDE (prose vs lambda) ──
    # energy on each probe's OWN-combinator fingerprint (raw, not z-scored)
    own_prose = np.array([E_prose[i, y_prose[i]] for i in range(len(prose))])
    own_lam = np.array([E_lam[i, y_lam[i]] for i in range(len(lam))])
    # total absolute energy across ops (overall gain)
    tot_prose = np.abs(E_prose).sum(1)
    tot_lam = np.abs(E_lam).sum(1)

    # ── 3. PROSE↔LAMBDA PROFILE MATCH (per combinator) ──
    def mean_profile(E, y, oi):
        idx = np.where(y == oi)[0]
        if len(idx) == 0:
            return None
        v = E[idx].mean(0)
        return v / (np.linalg.norm(v) + 1e-9)
    prof_match = {}
    cross = np.full((n_ops, n_ops), np.nan)  # prose-i vs lambda-j cosine
    for i, op in enumerate(CRYSTAL_OPS):
        pi = mean_profile(E_prose, y_prose, i)
        for j in range(n_ops):
            lj = mean_profile(E_lam, y_lam, j)
            if pi is not None and lj is not None:
                cross[i, j] = float(pi @ lj)
        if pi is not None and mean_profile(E_lam, y_lam, i) is not None:
            prof_match[op] = float(cross[i, i])
    # diagonal vs off-diagonal of cross
    diag = np.nanmean([cross[i, i] for i in range(n_ops) if not np.isnan(cross[i, i])])
    off = np.nanmean([cross[i, j] for i in range(n_ops) for j in range(n_ops)
                      if i != j and not np.isnan(cross[i, j])])

    out = {
        "model": args.model, "n_prose": len(prose), "n_lambda": len(lam),
        "ops": CRYSTAL_OPS,
        "classification": {
            "accuracy": acc, "chance": 1.0 / n_ops,
            "null_acc_mean": float(np.mean(null_acc)), "p_value": p_acc,
            "confusion_row_normalized": conf.tolist(),
        },
        "amplitude": {
            "own_fp_energy_prose_median": float(np.median(own_prose)),
            "own_fp_energy_lambda_median": float(np.median(own_lam)),
            "total_energy_prose_median": float(np.median(tot_prose)),
            "total_energy_lambda_median": float(np.median(tot_lam)),
            "prose_lower_than_lambda": bool(np.median(tot_prose) < np.median(tot_lam)),
        },
        "profile_match": {
            "per_combinator_cosine": prof_match,
            "mean_diag_cosine": float(diag),
            "mean_offdiag_cosine": float(off),
            "specificity_gap": float(diag - off),
        },
    }
    with open(RESULTS_DIR / f"{slug}.json", "w") as f:
        json.dump(out, f, indent=2)

    log("\n══════════ RESULTS ══════════")
    log(f"  1. PROSE classification: acc={acc:.3f}  chance={1/n_ops:.3f}  "
        f"null={np.mean(null_acc):.3f}  p={p_acc:.4f}")
    log(f"     (does λ-built fingerprint classify pure prose by combinator?)")
    log(f"  2. AMPLITUDE: total energy prose median={np.median(tot_prose):.1f}  "
        f"lambda median={np.median(tot_lam):.1f}  "
        f"prose<lambda={out['amplitude']['prose_lower_than_lambda']}")
    log(f"     own-fp energy: prose={np.median(own_prose):+.2f}  lambda={np.median(own_lam):+.2f}")
    log(f"  3. PROFILE MATCH: diag cosine={diag:+.3f}  offdiag={off:+.3f}  "
        f"gap={diag-off:+.3f}")
    log(f"     per-combinator prose↔lambda cosine: "
        f"{ {k: round(v,2) for k,v in prof_match.items()} }")
    log(f"  saved → {RESULTS_DIR / f'{slug}.json'}")


if __name__ == "__main__":
    main()
