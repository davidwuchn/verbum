#!/usr/bin/env python3
# register: behavioral self-decode (patchscopes-style; the model reads its own wires)
"""P2-RETEST — can the model itself verbalize J-space workspace directions?

Michael's s272 catch: the s270 P2 "verbalize" negative read basis directions
through the FROZEN unembedding (zero-shot logit-lens). Anthropic's readable
J-space demos rode a TRAINED decoder (babel-codec). Wrong-register negative ≡
void (λ measure, s206 shape). This instrument retests with a far stronger
zero-training readout: inject the direction into the model's own residual
stream inside an identity few-shot prompt and let the model decode itself
(Ghandeharioun et al. 2024, patchscopes).

Method:
  prompt  = "cat -> cat\\n1135 -> 1135\\nhello -> hello\\nX"
  patch   = at layer L, last position, REPLACE h with norm-matched a*v-hat
            (a = ||h_orig[pos]||; same residual-write convention as
            projector._injection_forward, so the decode lives in exactly
            the space the basis was measured in)
  decode  = greedy, max_new tokens; both ±v (basis sign is arbitrary)

PRE-REGISTERED (fixed before any 27B data; smoke on a small model only
checks plumbing, not verdicts):
  G0 basis-reproduction gate: recomputed strengths must match the committed
     jspace_projector.json strengths (same seed/params) — median rel dev
     < 0.05, else the basis is not the artifact's basis and NO verdict.
  G1 instrument gate (readability ceiling): unembed-row directions of known
     tokens (" recursively", " previously", " cat") injected the same way
     must decode to their own semantic field (stem match) in ≥ 2/3 cases,
     else the recipe cannot read even KNOWN-readable directions → void.
  G3 null: n matched-random unit directions, same scale a, same prompt.
  VERDICT RULE: "workspace dirs self-decode" iff basis-dir generations show
     lexicon hits / coherent fields ABOVE the random-dir rate. Watch list
     (from s269f + the WHNF-adjacent watch): recursion, precedence, halt
     lexicons. Eyeball dump of ALL generations saved for judgment either
     way — automatic lexicons are a floor, not the readout.

Cost note: recomputing the 27B basis is the expensive step (same as the
sweep sidecar, tens of minutes); the basis is saved to jspace_basis.npz so
this is paid ONCE (H3 --keep-centroids gap, same lesson).

Output: results/opcode-trace/<slug>/{jspace_basis.npz, patchscope_selfdecode.json}

Usage:
  uv run python opcodes/patchscope.py --model Qwen/Qwen3.6-27B --device mps
  uv run python opcodes/patchscope.py --smoke          # pythia-14m plumbing check

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

_HERE = Path(__file__).resolve().parent
_ROOT = _HERE.parent
sys.path.insert(0, str(_HERE))

import trace as TR  # noqa: E402

import projector as P  # noqa: E402
import topology as T  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "opcode-trace"

IDENTITY_PROMPT = "cat -> cat\n1135 -> 1135\nhello -> hello\nX"

# G1 control tokens: known-readable through the FROZEN unembedding — the
# contrast class for the workspace dirs (which are frozen-unembed-silent).
# NOTE (s272, 0.6B run): " cat" control was VOID — the word appears in the
# identity prompt itself, so stem-match is contaminated by echo. Replaced
# with " Paris" (absent from prompt). Instrument fix, not a claim change.
CONTROL_TOKENS = [" recursively", " previously", " Paris"]
CONTROL_STEMS = ["recurs", "previous", "paris"]

# Pre-registered watch lexicons (floor metric; eyeball dump is the readout).
LEXICONS = {
    "recursion": ["recurs", "recurrent", "iterat", "repeat", "again", "loop",
                  "递归", "依次"],
    "precedence": ["previous", "prior", "before", "earlier", "preced", "first",
                   "此前", "先前"],
    "halt": ["done", "finish", "complete", "halt", "stop", "end", "final",
             "terminat", "结束", "完成"],
}


def slugify(model: str) -> str:
    return model.split("/")[-1].lower().replace(".", "-")


def hit_lexicons(text: str) -> dict[str, int]:
    low = text.lower()
    return {name: sum(1 for s in stems if s in low)
            for name, stems in LEXICONS.items()}


@torch.no_grad()
def batched_selfdecode(
    model, tok, topo, layer: int, deltas_unit: np.ndarray, max_new: int,
) -> list[str]:
    """Prefill with per-row norm-matched replacement at (layer, last pos),
    then greedy-decode. Returns generated text per row."""
    dev = next(model.parameters()).device
    b = deltas_unit.shape[0]
    inputs = tok([IDENTITY_PROMPT] * b, return_tensors="pt").to(dev)
    pos = inputs["input_ids"].shape[1] - 1
    b_idx = torch.arange(b, device=dev)
    dvec = torch.from_numpy(deltas_unit).to(dev)

    def hook(_m, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if h.shape[1] <= 1:  # decode step; patched KV already baked
            return None
        norms = h[b_idx, pos].norm(dim=-1, keepdim=True).float()
        h2 = h.clone()
        h2[b_idx, pos] = (dvec * norms).to(h.dtype)
        return (h2, *out[1:]) if isinstance(out, tuple) else h2

    mod = model.get_submodule(f"{topo.layers_path}.{layer}")
    handle = mod.register_forward_hook(hook)
    try:
        out = model(**inputs, use_cache=True)
        past = out.past_key_values
        next_ids = out.logits[:, -1].argmax(dim=-1, keepdim=True)
        gen = [next_ids]
        for _ in range(max_new - 1):
            out = model(input_ids=next_ids, past_key_values=past,
                        use_cache=True)
            past = out.past_key_values
            next_ids = out.logits[:, -1].argmax(dim=-1, keepdim=True)
            gen.append(next_ids)
    finally:
        handle.remove()
    toks = torch.cat(gen, dim=1)
    return [tok.decode(toks[i], skip_special_tokens=True) for i in range(b)]


def unembed_direction(model, tok, text: str) -> tuple[np.ndarray, str]:
    ids = tok.encode(text, add_special_tokens=False)
    w = model.get_output_embeddings().weight[ids[0]].detach().float().cpu()
    v = w.numpy()
    return v / np.linalg.norm(v), tok.decode([ids[0]])


def main() -> None:
    ap = argparse.ArgumentParser(description="Patchscope self-decode of J-space dirs")
    ap.add_argument("--model", default="Qwen/Qwen3.6-27B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--k", type=int, default=32)
    ap.add_argument("--top-dirs", type=int, default=5)
    ap.add_argument("--n-random", type=int, default=8)
    ap.add_argument("--max-new", type=int, default=12)
    ap.add_argument("--proj-ppc", type=int, default=3)
    ap.add_argument("--depths", default="0.25,0.5,0.75")
    ap.add_argument("--eps-rel", type=float, default=0.02)
    ap.add_argument("--seed", type=int, default=270)
    ap.add_argument("--smoke", action="store_true",
                    help="pythia-14m on cpu; plumbing only, no verdicts")
    args = ap.parse_args()
    if args.smoke:
        args.model, args.device = "EleutherAI/pythia-14m-deduped", "cpu"

    slug = slugify(args.model)
    out_dir = RESULTS_DIR / slug
    out_dir.mkdir(parents=True, exist_ok=True)
    depths = [float(x) for x in args.depths.split(",")]
    rng = np.random.default_rng(args.seed + 2)

    t0 = time.time()
    model, tok = TR.load(args.model, args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[patchscope] {topo.summary()}")
    target_layer = topo.n_layers - 2
    layers = sorted({
        min(max(round(f * topo.n_layers), 0), target_layer - 1)
        for f in depths
    })

    # ── basis: load sidecar or recompute (once) ──────────────────────────────
    npz_path = out_dir / "jspace_basis.npz"
    if npz_path.exists():
        z = np.load(npz_path)
        bases = {li: (z[f"basis_L{li}"], z[f"strengths_L{li}"])
                 for li in layers if f"basis_L{li}" in z}
        print(f"[patchscope] loaded basis sidecar {npz_path}")
    else:
        proj_probes, _ = TR._balanced_subsets(
            [p for p in TR.crystal_probes() if p.combinator in TR.CRYSTAL],
            args.proj_ppc, 0,
        )
        print(f"[patchscope] building bases at {layers} from "
              f"{len(proj_probes)} prompts (k={args.k}) ...")
        built = P.jspace_bases(
            model, tok, [p.prompt for p in proj_probes],
            layers=layers, target_layer=target_layer, k=args.k,
            refine=True, eps_rel=args.eps_rel, topo=topo, seed=args.seed,
        )
        bases = {li: (b.basis, b.strengths) for li, b in built.items()}
        np.savez_compressed(
            npz_path,
            **{f"basis_L{li}": v for li, (v, _) in bases.items()},
            **{f"strengths_L{li}": s for li, (_, s) in bases.items()},
        )
        print(f"[patchscope] saved basis sidecar {npz_path}")

    # ── G0: reproduction gate vs committed artifact ──────────────────────────
    g0 = {"available": False, "median_rel_dev": None, "pass": None}
    art_path = out_dir / "jspace_projector.json"
    if art_path.exists() and not args.smoke:
        art = json.loads(art_path.read_text(encoding="utf-8"))
        devs = []
        for li, (_, s) in bases.items():
            a = np.array(art["layers"][str(li)]["strengths"][: len(s)])
            devs.extend(np.abs(np.asarray(s[: len(a)]) - a) / np.maximum(a, 1e-9))
        med = float(np.median(devs))
        g0 = {"available": True, "median_rel_dev": med, "pass": bool(med < 0.05)}
        print(f"[patchscope] G0 basis reproduction: median rel dev {med:.4f} "
              f"-> {'PASS' if g0['pass'] else 'FAIL (no verdict)'}")

    # ── build injection sets & decode per layer ──────────────────────────────
    controls = [unembed_direction(model, tok, t) for t in CONTROL_TOKENS]
    results: dict[str, dict] = {}
    g1_hits = 0
    for li in layers:
        basis, _strengths = bases[li]
        rows, labels = [], []
        for d in range(min(args.top_dirs, basis.shape[0])):
            v = basis[d] / np.linalg.norm(basis[d])
            rows += [v, -v]
            labels += [f"dir{d}+", f"dir{d}-"]
        for (v, tok_str), name in zip(controls, CONTROL_TOKENS, strict=True):
            rows.append(v)
            labels.append(f"G1:{name.strip()}({tok_str.strip()})")
        for i in range(args.n_random):
            r = rng.standard_normal(basis.shape[1])
            rows.append(r / np.linalg.norm(r))
            labels.append(f"rand{i}")
        deltas = np.stack(rows).astype(np.float32)
        print(f"[patchscope] L{li}: decoding {len(rows)} injections ...")
        texts = batched_selfdecode(model, tok, topo, li, deltas, args.max_new)
        layer_out = {}
        for lab, txt in zip(labels, texts, strict=True):
            rec = {"text": txt, "lexicon_hits": hit_lexicons(txt)}
            if lab.startswith("G1:"):
                stem = CONTROL_STEMS[[c.strip() for c in CONTROL_TOKENS].index(
                    lab.split(":")[1].split("(")[0])]
                rec["g1_pass"] = stem in txt.lower()
            layer_out[lab] = rec
        results[str(li)] = layer_out

    # G1 aggregated over layers: a control passes if it decodes at ANY depth
    g1_by_token = {}
    for name, _stem in zip(CONTROL_TOKENS, CONTROL_STEMS, strict=True):
        ok = any(
            rec.get("g1_pass")
            for lay in results.values()
            for lab, rec in lay.items()
            if lab.startswith(f"G1:{name.strip()}")
        )
        g1_by_token[name.strip()] = bool(ok)
        g1_hits += ok
    g1 = {"by_token": g1_by_token, "passed": g1_hits,
          "pass": bool(g1_hits >= 2)}
    print(f"[patchscope] G1 instrument gate: {g1_hits}/3 controls decode "
          f"-> {'PASS' if g1['pass'] else 'FAIL (instrument void)'}")

    # lexicon floor summary: basis vs random
    def pool(kind: str) -> dict[str, float]:
        tot = {k: 0 for k in LEXICONS}
        n = 0
        for lay in results.values():
            for lab, rec in lay.items():
                if (kind == "basis" and lab.startswith("dir")) or \
                   (kind == "random" and lab.startswith("rand")):
                    n += 1
                    for k, v in rec["lexicon_hits"].items():
                        tot[k] += v
        return {k: v / max(n, 1) for k, v in tot.items()}

    summary = {"basis_hits_per_gen": pool("basis"),
               "random_hits_per_gen": pool("random")}
    print(f"[patchscope] lexicon floor: basis {summary['basis_hits_per_gen']} "
          f"vs random {summary['random_hits_per_gen']}")

    out = {
        "model": args.model, "layers": layers, "target_layer": target_layer,
        "k": args.k, "top_dirs": args.top_dirs, "n_random": args.n_random,
        "max_new": args.max_new, "seed": args.seed,
        "prompt": IDENTITY_PROMPT,
        "preregistration": {
            "G0": "median rel strength dev < 0.05 vs committed artifact",
            "G1": ">=2/3 unembed-row controls decode their own field",
            "verdict": "basis dirs self-decode iff coherent fields above "
                       "random-dir rate (lexicon floor + eyeball dump)",
        },
        "g0": g0, "g1": g1, "lexicon_summary": summary,
        "generations": results,
        "elapsed_s": round(time.time() - t0, 1),
    }
    out_path = out_dir / "patchscope_selfdecode.json"
    out_path.write_text(json.dumps(out, indent=2, ensure_ascii=False),
                        encoding="utf-8")
    print(f"[patchscope] wrote {out_path} ({out['elapsed_s']}s)")


if __name__ == "__main__":
    main()
