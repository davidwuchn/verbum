#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — causal ablation of the type direction (v4)
"""Type-directedness, v4 — CAUSAL ablation (correlation -> causation).

v3 (nonce crossover) showed, frequency-free, that the model USES an in-context-taught
type to direct composition (crossover 8B +2.18/14B +2.04, t~9-10, consistency 1.0). But
that is BEHAVIOURAL/correlational. This is the causal upgrade: DECODE the type direction
in the residual stream and ABLATE it — if the type direction CAUSES the composition
behaviour, the v3 crossover COLLAPSES under type-direction ablation, while a RANDOM-
direction ablation of the same magnitude leaves it intact (the control, lambda measure).

THE MECHANISM under test: in "{teach}. {filler} {nonce}" the model predicts the nonce
from the residual at the FILLER position (the token before the nonce — the next-token
bottleneck). VERB-taught -> that residual should carry "expect a predicate" so the nonce
is cheap after a name; NOUN-taught -> "expect a noun" so cheap after a det. The TYPE
DIRECTION = difference-of-means(verb - noun) of the filler-position residual (robust
concept direction; per-layer; pick the most decodable layer L* by AUC).

INTERVENTION: project the unit type direction OUT of the residual at the filler position
at layer L* during the forward pass -> both conditions lose the type component -> if it
drove composition, name_pen (and the crossover) collapse toward 0.
CONTROL: project out a RANDOM unit direction (same procedure) -> crossover survives.

VERDICT (lambda measure): type-ablation collapses the crossover AND random preserves it
-> the type direction is CAUSAL; type-directed composition is mechanistic, not just
behavioural; confirms s139 (type decodable+co-located) as DIRECTING dispatch. Both
collapse -> ablation non-specific. Neither -> the type info the prediction uses is
not at the filler position/this layer (try other loci).

CAVEATS (lambda measure): single-position single-layer linear ablation (type may be
distributed -> a null is not decisive); difference-of-means concept direction;
in-context teaching; behavioural readout; 1 family. Per-layer AUC logged so a low-AUC
null is not over-read as "no causation".

Usage:
    uv run python scripts/experiments/type_directed_v4_ablation.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v4_ablation.py           # 14B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "src"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from opcode_monitor_v2 import (  # noqa: E402
    _git_sha,
    _json_safe,
    _transformers_version,
    load_model_and_tokenizer,
)
from type_directed_v3_nonce import (  # noqa: E402
    DET_FILL,
    NAME_FILL,
    NONCE,
    NOUN_TEACH,
    VERB_TEACH,
    build_text,
)

RESULTS_DIR = _ROOT / "results" / "type-directed"


def decoder_layers(model):
    """Architecture-agnostic decoder-layer list (cross-family ablation).

    Llama/Mistral/OLMo/Qwen/SmolLM -> model.model.layers ; GPTNeoX/Pythia ->
    model.gpt_neox.layers ; GPT-2 -> transformer.h ; OPT -> model.decoder.layers.
    """
    for path in ("model.layers", "gpt_neox.layers", "transformer.h",
                 "model.decoder.layers"):
        obj = model
        ok = True
        for attr in path.split("."):
            if not hasattr(obj, attr):
                ok = False
                break
            obj = getattr(obj, attr)
        if ok:
            return obj
    raise AttributeError("could not locate decoder layers for this architecture")


def gen_items(n_each: int, seed: int, n_teach: int):
    """v3-style items, subsampled teach templates (causal passes are 3x forwards)."""
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    for w in NONCE:
        for typ, teaches in (("noun", NOUN_TEACH), ("verb", VERB_TEACH)):
            for teach in teaches[:n_teach]:
                for frame, fills in (("det", DET_FILL), ("name", NAME_FILL)):
                    for filler in pick(fills, n_each):
                        items.append({"w": w, "type": typ, "frame": frame,
                                      "teach": teach, "filler": filler,
                                      "cond": f"{frame}_{typ}"})
    rng.shuffle(items)
    return items


def locate(item, tok):
    """Tokenize; return (ids, attn, nonce_token_indices, filler_pos)."""
    text, c0 = build_text(item["teach"], item["w"], item["filler"])
    c1 = len(text)
    enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
    offsets = enc["offset_mapping"][0].tolist()
    nonce_js = [j for j, (s, e) in enumerate(offsets)
                if e > s and s < c1 and e > c0]
    filler_pos = (min(nonce_js) - 1) if nonce_js else None
    return enc, nonce_js, filler_pos


def nonce_surprisal(logits_logp, ids, nonce_js):
    vals = [-float(logits_logp[j - 1, ids[j]]) for j in nonce_js if j >= 1]
    return float(np.mean(vals)) if vals else None


def make_ablation_hook(direction_unit, pos_box, torch_mod, whole=True):
    """Forward hook on a decoder layer: project `direction_unit` OUT of the residual
    (output[0]). whole=True -> ALL token positions (global concept removal, so the type
    cannot be re-read from the teaching tokens); else only `pos_box[0]` (the filler)."""
    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        d = torch_mod.as_tensor(direction_unit, dtype=h.dtype, device=h.device)
        if whole:
            coeff = h[0] @ d  # [T]
            h[0] = h[0] - coeff[:, None] * d[None, :]
        else:
            pos = pos_box[0]
            v = h[0, pos, :]
            h[0, pos, :] = v - (v @ d) * d
        return out
    return hook


def _auc(pos_scores, neg_scores):
    """Mann-Whitney AUC: P(verb proj > noun proj)."""
    pos, neg = np.asarray(pos_scores), np.asarray(neg_scores)
    if len(pos) == 0 or len(neg) == 0:
        return 0.5
    allv = np.concatenate([pos, neg])
    ranks = allv.argsort().argsort().astype(float) + 1
    r_pos = ranks[: len(pos)].sum()
    return float((r_pos - len(pos) * (len(pos) + 1) / 2) / (len(pos) * len(neg)))


def crossover_stats(surpr_by_cond_w):
    """Given cond->w->[surprisal], return det_pen, name_pen, crossover (paired by w)."""
    def cell(c, w):
        v = surpr_by_cond_w[c].get(w, [])
        return float(np.mean(v)) if v else None

    dpen, npen, cross = [], [], []
    for w in NONCE:
        cells = [cell(f"{fr}_{ty}", w) for fr in ("det", "name")
                 for ty in ("verb", "noun")]
        if all(c is not None for c in cells):
            dv, dn, nv, nn = cells
            dpen.append(dv - dn)
            npen.append(nv - nn)
            cross.append((dv - dn) - (nv - nn))

    def agg(arr):
        a = np.asarray(arr)
        if len(a) < 2:
            return None
        se = float(a.std(ddof=1) / np.sqrt(len(a)))
        return {"mean": round(float(a.mean()), 4),
                "t": round(float(a.mean() / se) if se > 0 else 0.0, 3), "n": len(a)}

    return {"det_pen": agg(dpen), "name_pen": agg(npen), "crossover": agg(cross)}


def run_pass(items, model, tok, torch_mod, ablations=None):
    """Forward each item; ablate the filler position across a STACK of layers.

    ablations = list[(layer_module, direction_vector)] — each projects its direction
    OUT of the filler-position residual at that layer (filler-stack ablation, so the
    type cannot be re-derived downstream). Returns cond->w->[surprisal]."""
    import torch.nn.functional as func
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    pos_box = [0]
    handles = []
    if ablations:
        for mod, direction in ablations:
            handles.append(mod.register_forward_hook(
                make_ablation_hook(direction, pos_box, torch_mod)))
    try:
        for it in items:
            enc, nonce_js, fpos = locate(it, tok)
            if not nonce_js or fpos is None or fpos < 0:
                continue
            pos_box[0] = fpos
            ids = enc["input_ids"][0]
            with torch_mod.no_grad():
                logits = model(input_ids=ids.unsqueeze(0).to(dev),
                               attention_mask=enc["attention_mask"].to(dev)).logits[0]
            logp = func.log_softmax(logits.float(), dim=-1).cpu()
            s = nonce_surprisal(logp, ids.cpu(), nonce_js)
            if s is not None:
                out[it["cond"]][it["w"]].append(s)
    finally:
        for h in handles:
            h.remove()
    return out


def collect_residuals(items, model, tok, torch_mod):
    """Forward with output_hidden_states; return (rows, baseline-surprisal dict). Each
    row = (item, resid[L+1,H] at FILLER pos, label 1=verb/0=noun)."""
    out: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    dev = next(model.parameters()).device
    import torch.nn.functional as func
    rows = []
    for it in items:
        enc, nonce_js, fpos = locate(it, tok)
        if not nonce_js or fpos is None or fpos < 0:
            continue
        ids = enc["input_ids"][0]
        with torch_mod.no_grad():
            res = model(input_ids=ids.unsqueeze(0).to(dev),
                        attention_mask=enc["attention_mask"].to(dev),
                        output_hidden_states=True)
        hs = res.hidden_states  # tuple len n_layers+1, each [1,T,H]
        vecs = np.stack([h[0, fpos, :].float().cpu().numpy().astype(np.float16)
                         for h in hs])  # [L+1, H]
        logp = func.log_softmax(res.logits[0].float(), dim=-1).cpu()
        s = nonce_surprisal(logp, ids.cpu(), nonce_js)
        rows.append((it, vecs, 1 if it["type"] == "verb" else 0))
        if s is not None:
            out[it["cond"]][it["w"]].append(s)
    return rows, out


def main() -> None:
    ap = argparse.ArgumentParser(description="Type-directedness causal ablation (v4)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=3, help="fillers per cell")
    ap.add_argument("--n-teach", type=int, default=2, help="teach templates per type")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    n_each, n_teach = args.n_each, args.n_teach
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each, n_teach = 2, 2
        print("[type-dir4] SMOKE MODE (Qwen3-8B)")

    items = gen_items(n_each, args.seed, n_teach)
    print(f"[type-dir4] {len(items)} items (n_each={n_each}, n_teach={n_teach})")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)

    # ── pass 1: collect filler-position residuals + baseline surprisal ──────────
    print("[type-dir4] pass 1: collecting residuals + baseline ...")
    rows, base = collect_residuals(items, model, tok, torch_mod)
    n_layers_p1 = rows[0][1].shape[0]  # L+1 hidden states
    hdim = rows[0][1].shape[1]

    # ── difference-of-means TYPE direction per layer + decodability (AUC) ───────
    verb_idx = [i for i, r in enumerate(rows) if r[2] == 1]
    noun_idx = [i for i, r in enumerate(rows) if r[2] == 0]
    layer_auc, layer_dir = [], []
    for li in range(n_layers_p1):
        vmean = np.mean([rows[i][1][li].astype(np.float32) for i in verb_idx], axis=0)
        nmean = np.mean([rows[i][1][li].astype(np.float32) for i in noun_idx], axis=0)
        d = vmean - nmean
        nrm = np.linalg.norm(d)
        dunit = d / nrm if nrm > 0 else d
        proj = [float(rows[i][1][li].astype(np.float32) @ dunit)
                for i in range(len(rows))]
        auc = _auc([proj[i] for i in verb_idx], [proj[i] for i in noun_idx])
        layer_auc.append(round(auc, 4))
        layer_dir.append(dunit)
    lstar = int(np.argmax(layer_auc))  # hidden-state index (0=emb, 1..=layer outputs)
    print(f"[type-dir4] type-direction decodability AUC by layer: "
          f"max={layer_auc[lstar]} @ hidden-state {lstar} (of {n_layers_p1})")
    print(f"[type-dir4]   AUC profile (every 4): "
          f"{[layer_auc[i] for i in range(0, n_layers_p1, 4)]}")

    base_stats = crossover_stats(base)
    print(f"[type-dir4] BASELINE crossover={base_stats['crossover']} "
          f"name_pen={base_stats['name_pen']}")

    # FILLER-STACK ablation: project the per-layer type direction OUT of the filler
    # residual at EVERY hidden state h >= L* (so the type cannot be re-derived
    # downstream by attention to the teaching). hidden_states[h] <- hook layers[h-1].
    if lstar == 0:
        print("[type-dir4] WARN: best AUC at embeddings; starting ablation at layer 0")
        lstar = 1
    rng = np.random.default_rng(args.seed + 7)
    layers = decoder_layers(model)
    type_ablations, rand_ablations = [], []
    for h in range(lstar, n_layers_p1):
        mod = layers[h - 1]
        type_ablations.append((mod, layer_dir[h].astype(np.float32)))
        r = rng.standard_normal(hdim).astype(np.float32)
        rand_ablations.append((mod, r / np.linalg.norm(r)))
    print(f"[type-dir4] filler-stack ablation, hidden states {lstar}.."
          f"{n_layers_p1 - 1} ({len(type_ablations)} layers)")

    print("[type-dir4] pass 2: TYPE-direction ablation ...")
    type_abl = run_pass(items, model, tok, torch_mod, type_ablations)
    type_stats = crossover_stats(type_abl)
    print("[type-dir4] pass 3: RANDOM-direction ablation (control) ...")
    rand_abl = run_pass(items, model, tok, torch_mod, rand_ablations)
    rand_stats = crossover_stats(rand_abl)

    def ratio(ab, bs):
        if ab and bs and bs.get("crossover") and ab.get("crossover") \
                and bs["crossover"]["mean"]:
            return round(ab["crossover"]["mean"] / bs["crossover"]["mean"], 3)
        return None

    type_ratio = ratio(type_stats, base_stats)
    rand_ratio = ratio(rand_stats, base_stats)
    causal = bool(type_ratio is not None and rand_ratio is not None
                  and type_ratio < 0.5 and rand_ratio > 0.7)

    verdict = {"register": "causal ablation of the type direction (v4)",
               "ablation_layer_hidden_state": lstar,
               "type_direction_auc": layer_auc[lstar], "auc_by_layer": layer_auc,
               "baseline": base_stats, "type_ablated": type_stats,
               "random_ablated": rand_stats,
               "crossover_retained_type": type_ratio,
               "crossover_retained_random": rand_ratio,
               "type_direction_is_causal": causal, "n_items": len(items)}

    print("\n" + "=" * 72)
    print("TYPE-DIRECTEDNESS v4 — is the type direction CAUSAL?")
    print("=" * 72)
    print(f"  type-direction decodability AUC @ L*={lstar}: {layer_auc[lstar]}")
    for tag, st in (("BASELINE", base_stats), ("TYPE-ablated", type_stats),
                    ("RANDOM-ablated", rand_stats)):
        cx, nm = st.get("crossover"), st.get("name_pen")
        cxs = f"{cx['mean']} (t={cx['t']})" if cx else "n/a"
        nms = f"{nm['mean']} (t={nm['t']})" if nm else "n/a"
        print(f"  {tag:<16} crossover={cxs:<22} name_pen={nms}")
    print(f"\n  crossover retained: TYPE-ablation={type_ratio}  "
          f"RANDOM-ablation={rand_ratio}")
    print(f"  * type_direction_is_causal = {causal}")
    print("=" * 72 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"type_directed_v4_ablation_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_teach": n_teach, "n_items": len(items),
            "seed": args.seed, "hidden_dim": hdim, "n_hidden_states": n_layers_p1}
    (RESULTS_DIR / f"type_directed_v4_ablation_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[type-dir4] wrote v4 verdict for {slug}")


if __name__ == "__main__":
    main()
