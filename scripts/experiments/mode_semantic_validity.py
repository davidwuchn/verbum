#!/usr/bin/env python3
"""Audit #3 (extension) — Are the FFN modes SEMANTICALLY real (POS + logits)?

The geometry control (`mode_cluster_validity.py`, s204) refuted the *geometric*
claim that k=9 is a natural cluster count. But geometric continuity of the
gate-pattern cloud does NOT by itself refute the two claims mode-semantics.md
actually leans on:

  (semantic) modes map to syntactic roles (POS/dep) — "7 universal meta-modes"
  (logit)    mode output-centroids project to distinct promoted vocab tokens

A continuous cloud can still carry a real, smooth POS gradient and distinct
vocab projections. This control tests both directly, with nulls — examining
LOGITS (lm_head projection), not just clustering geometry, on PROSE input.

Instruments
-----------
  A. POS / dep semantic content
     A1. NMI(mode, POS) and NMI(mode, dep) of the k=9 partition.
     A2. Label-permutation null (B=200): is the real NMI above shuffled labels?
         (tests "any association" — a low bar, but the headline implies it.)
     A3. NMI-vs-k curve (k=2..32): what FRACTION of k=9's NMI is already
         captured at k=2,3,4? If punct/content (k≈2) dominates, the "7 meta-
         modes" over-reads; if NMI keeps climbing to 9, the resolution is real.
     A4. Per-mode dominant POS + purity (reproduce the headline, with the null).

  B. Logit / vocab projection (THE part the geometry control omitted)
     B1. Per mode: output centroid -> lm_head -> logit distribution; top
         promoted / suppressed tokens (qualitative, for inspection).
     B2. Distinctness: mean pairwise Jensen-Shannon divergence between mode
         logit distributions, REAL k-means vs RANDOM-partition null (B=30).
         Quantifies HOW MUCH more vocab-distinct the modes are than chance.
     B3. Distinctness-vs-k curve: does adding modes past k=2-4 keep producing
         vocab-distinct projections, or do extra modes become redundant
         (JS -> 0)? Tests the count question in OUTPUT/logit space.
  (B4 POS-coherence — promoted-vocab POS vs mode-token POS — was dropped: the
   FFN output projects to the NEXT token via lm_head, whose POS differs from the
   current token's by construction, so that test is confounded and uninformative.)

Verdict logic
-------------
  SEMANTICALLY REAL : NMI >> perm-null AND NMI keeps rising to ~9 (not saturated
                      at k=2-4) AND JS distinctness >> random-partition null and
                      persists at k=9 AND POS-coherence above shuffle.
  OVER-READ         : NMI saturates by k=2-4 (only punct/content is real),
                      JS distinctness collapses toward the random-partition null
                      as k->9 (extra modes redundant in vocab space).

Usage:
  uv run python scripts/experiments/mode_semantic_validity.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import spacy
import torch
from sklearn.cluster import KMeans
from sklearn.metrics import normalized_mutual_info_score as nmi_score
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# Reuse the exact prose set + spaCy alignment from the original page's harness.
from mode_semantics import TEXTS, align_spacy_to_tokens, get_layers  # noqa: E402

from verbum.probes.library import crystal_probes  # noqa: E402

DEFAULT_LAYERS = [3, 15, 20, 27, 35]


def log(msg=""):
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Collection — gate, output, POS/dep annotations (prose)
# ══════════════════════════════════════════════════════════════════════

def collect_layer(model, tokenizer, nlp, layer_idx, device, texts):
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {}

    def gate_hook(module, inp, out):
        captured["gate_raw"] = out.detach().float()

    def post_hook(module, inp, out):
        captured["output"] = out.detach().float()

    h_gate = mlp.gate_proj.register_forward_hook(gate_hook)
    h_post = mlp.register_forward_hook(post_hook)

    all_gate, all_out, anns = [], [], []
    for text in texts:
        captured.clear()
        enc = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        input_ids = enc["input_ids"][0].tolist()
        enc_dev = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc_dev)
        if "gate_raw" not in captured or "output" not in captured:
            continue
        gate_raw = captured["gate_raw"][0]
        gate = (gate_raw * torch.sigmoid(gate_raw)).cpu().numpy()
        out = captured["output"][0].cpu().numpy()
        ann = align_spacy_to_tokens(text, tokenizer, input_ids, nlp)
        all_gate.append(gate)
        all_out.append(out)
        anns.extend(ann)

    h_gate.remove()
    h_post.remove()
    return (np.concatenate(all_gate, 0), np.concatenate(all_out, 0), anns)


# ══════════════════════════════════════════════════════════════════════
# A. POS / dep semantic content
# ══════════════════════════════════════════════════════════════════════

def pos_semantics(gate, anns, ks, rng, b_perm=200):
    pos = np.array([a["pos"] for a in anns])
    dep = np.array([a["dep"] for a in anns])
    out = {"nmi_pos_vs_k": {}, "nmi_dep_vs_k": {}}

    for k in ks:
        labels = KMeans(n_clusters=k, random_state=42, n_init=5).fit_predict(gate)
        out["nmi_pos_vs_k"][int(k)] = float(nmi_score(pos, labels))
        out["nmi_dep_vs_k"][int(k)] = float(nmi_score(dep, labels))

    # k=9 perm-null + per-mode dominant POS
    k9 = 9 if 9 in ks else ks[len(ks) // 2]
    labels9 = KMeans(n_clusters=k9, random_state=42, n_init=5).fit_predict(gate)
    real_pos = float(nmi_score(pos, labels9))
    real_dep = float(nmi_score(dep, labels9))
    perm_pos = np.empty(b_perm)
    perm_dep = np.empty(b_perm)
    for b in range(b_perm):
        pl = labels9.copy()
        rng.shuffle(pl)
        perm_pos[b] = nmi_score(pos, pl)
        perm_dep[b] = nmi_score(dep, pl)
    out["k9"] = {
        "nmi_pos": real_pos,
        "nmi_dep": real_dep,
        "perm_pos_mean": float(perm_pos.mean()),
        "perm_pos_p95": float(np.percentile(perm_pos, 95)),
        "perm_pos_pval": float((perm_pos >= real_pos).mean()),
        "perm_dep_mean": float(perm_dep.mean()),
        "perm_dep_pval": float((perm_dep >= real_dep).mean()),
    }
    # fraction of k=9 NMI captured at small k
    n9 = out["nmi_pos_vs_k"][k9]
    out["k9"]["frac_nmi_at_k2"] = float(out["nmi_pos_vs_k"].get(2, 0.0) / (n9 + 1e-12))
    out["k9"]["frac_nmi_at_k4"] = float(out["nmi_pos_vs_k"].get(4, 0.0) / (n9 + 1e-12))

    # per-mode dominant POS purity
    dom = {}
    for m in range(k9):
        mask = labels9 == m
        if mask.sum() == 0:
            continue
        c = Counter(pos[mask])
        top, n = c.most_common(1)[0]
        dom[int(m)] = {"n": int(mask.sum()), "top_pos": top,
                       "purity": round(n / mask.sum(), 3),
                       "top3": c.most_common(3)}
    out["k9"]["mode_dominant_pos"] = dom
    return out


# ══════════════════════════════════════════════════════════════════════
# B. Logit / vocab projection
# ══════════════════════════════════════════════════════════════════════

def _softmax(x):
    x = x - x.max(axis=-1, keepdims=True)
    e = np.exp(x)
    return e / e.sum(axis=-1, keepdims=True)


def _js_matrix(P):
    """Mean pairwise Jensen-Shannon divergence among rows of P (prob dists)."""
    k = P.shape[0]
    if k < 2:
        return 0.0
    tot, cnt = 0.0, 0
    for i in range(k):
        for j in range(i + 1, k):
            m = 0.5 * (P[i] + P[j])
            kl_pm = np.sum(P[i] * (np.log(P[i] + 1e-12) - np.log(m + 1e-12)))
            kl_qm = np.sum(P[j] * (np.log(P[j] + 1e-12) - np.log(m + 1e-12)))
            tot += 0.5 * kl_pm + 0.5 * kl_qm
            cnt += 1
    return float(tot / cnt)


def _centroid_logit_dists(outputs, labels, k, lm_head):
    """Per-mode output centroid -> lm_head logits -> softmax prob dist."""
    d = outputs.shape[1]
    cents = np.zeros((k, d), dtype=np.float32)
    for m in range(k):
        mask = labels == m
        if mask.sum() > 0:
            cents[m] = outputs[mask].mean(0)
    logits = cents @ lm_head.T  # (k, vocab)
    return _softmax(logits), logits


def logit_projection(outputs, gate, lm_head, tokenizer, ks, rng, b_null=30, top_n=12):
    out = {"js_real_vs_k": {}, "js_null_mean_vs_k": {}, "js_null_std_vs_k": {}}
    n = len(outputs)
    for k in ks:
        labels = KMeans(n_clusters=k, random_state=42, n_init=5).fit_predict(gate)
        P, _ = _centroid_logit_dists(outputs, labels, k, lm_head)
        js_real = _js_matrix(P)
        # random-partition null: split the SAME outputs into k balanced groups
        null = np.empty(b_null)
        for b in range(b_null):
            rl = rng.integers(0, k, size=n)
            Pn, _ = _centroid_logit_dists(outputs, rl, k, lm_head)
            null[b] = _js_matrix(Pn)
        out["js_real_vs_k"][int(k)] = js_real
        out["js_null_mean_vs_k"][int(k)] = float(null.mean())
        out["js_null_std_vs_k"][int(k)] = float(null.std())

    # qualitative top tokens at k=9
    k9 = 9 if 9 in ks else ks[len(ks) // 2]
    labels9 = KMeans(n_clusters=k9, random_state=42, n_init=5).fit_predict(gate)
    P9, logits9 = _centroid_logit_dists(outputs, labels9, k9, lm_head)
    promoted = {}
    for m in range(k9):
        top = np.argsort(logits9[m])[-top_n:][::-1]
        promoted[int(m)] = [tokenizer.decode([int(t)]).strip() for t in top]
    out["k9"] = {
        "js_real": out["js_real_vs_k"][k9],
        "js_null_mean": out["js_null_mean_vs_k"][k9],
        "js_excess": out["js_real_vs_k"][k9] - out["js_null_mean_vs_k"][k9],
        "mode_promoted_tokens": promoted,
    }
    return out, labels9, P9


# ══════════════════════════════════════════════════════════════════════
# Driver
# ══════════════════════════════════════════════════════════════════════

def run_layer(model, tokenizer, nlp, layer_idx, device, texts, lm_head, ks, rng):
    log(f"\n{'═'*70}\n  LAYER {layer_idx}\n{'═'*70}")
    t0 = time.time()
    gate, outputs, anns = collect_layer(model, tokenizer, nlp, layer_idx, device, texts)
    log(f"  collected {len(gate)} tokens (gate {gate.shape[1]}-d, out {outputs.shape[1]}-d)")

    log("  [A] POS/dep semantics ...")
    A = pos_semantics(gate, anns, ks, rng)
    a9 = A["k9"]
    log(f"      NMI(mode,POS)@9 = {a9['nmi_pos']:.3f}  perm null {a9['perm_pos_mean']:.3f} "
        f"(p={a9['perm_pos_pval']:.3f})   NMI(mode,dep)@9 = {a9['nmi_dep']:.3f} "
        f"(p={a9['perm_dep_pval']:.3f})")
    log(f"      frac of NMI@9 captured at k2={a9['frac_nmi_at_k2']:.2f}  "
        f"k4={a9['frac_nmi_at_k4']:.2f}")

    log("  [B] logit/vocab projection ...")
    B, _, _ = logit_projection(outputs, gate, lm_head, tokenizer, ks, rng)
    b9 = B["k9"]
    log(f"      JS distinctness@9 real={b9['js_real']:.4f}  random-partition null="
        f"{b9['js_null_mean']:.4f}  excess={b9['js_excess']:+.4f}")

    log(f"  layer {layer_idx} done in {time.time()-t0:.1f}s")
    return {"layer_idx": layer_idx, "n_tokens": len(gate),
            "pos_semantics": A, "logit_projection": B,
            "elapsed_s": round(time.time() - t0, 1)}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--layers", type=int, nargs="+", default=None)
    p.add_argument("--n-crystal", type=int, default=80,
                   help="combinator-probe prose to add (balanced with 66 diverse)")
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    ks = [2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 16, 24, 32]
    layers = args.layers or DEFAULT_LAYERS
    rng = np.random.default_rng(args.seed)

    log(f"\n{'='*70}")
    log("  AUDIT #3 EXTENSION — POS + LOGIT semantic reality of the FFN modes")
    log(f"{'='*70}")
    log(f"  Model: {args.model}  Device: {args.device}  Layers: {layers}")

    log("  Loading spaCy en_core_web_sm ...")
    nlp = spacy.load("en_core_web_sm")

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    log(f"  Loading {args.model} ({dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(args.model, dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    layers = [_l for _l in layers if _l < model.config.num_hidden_layers]

    lm_head = model.lm_head.weight.detach().float().cpu().numpy()
    log(f"  lm_head: {lm_head.shape}")

    texts = list(TEXTS) + [pr.prompt for pr in crystal_probes()[:args.n_crystal]]
    log(f"  prose inputs: {len(TEXTS)} diverse + {args.n_crystal} combinator-probe = {len(texts)}")

    results = {"audit": "3-ext-semantic-logit", "model": args.model,
               "k_range": ks, "n_diverse": len(TEXTS), "n_crystal": args.n_crystal,
               "seed": args.seed, "layers": {}}
    for li in layers:
        results["layers"][str(li)] = run_layer(
            model, tokenizer, nlp, li, args.device, texts, lm_head, ks, rng)

    # ── Verdict summary ────────────────────────────────────────────────
    log(f"\n{'='*70}\n  VERDICT SUMMARY\n{'='*70}")
    log(f"  {'L':>3} | {'NMI_POS@9':>9} {'perm':>6} {'p':>5} | {'fracNMI k2/k4':>13} | "
        f"{'JS@9 real/null':>16} {'exc':>8}")
    for li in layers:
        r = results["layers"][str(li)]
        a = r["pos_semantics"]["k9"]
        b = r["logit_projection"]["k9"]
        log(f"  {li:>3} | {a['nmi_pos']:>9.3f} {a['perm_pos_mean']:>6.3f} "
            f"{a['perm_pos_pval']:>5.3f} | "
            f"{a['frac_nmi_at_k2']:>5.2f}/{a['frac_nmi_at_k4']:<5.2f} | "
            f"{b['js_real']:>7.4f}/{b['js_null_mean']:<7.4f} {b['js_excess']:>+8.4f}")

    log("\n  Reading: NMI >> perm AND NMI keeps rising to ~9 (frac at k2/k4 low) AND")
    log("  JS excess > 0 persisting at k=9 ==> modes carry real semantic/logit structure")
    log("  (a smooth gradient), even though the geometric count 9 is imposed. If NMI")
    log("  saturates by k2-4 and JS excess -> 0, the '9-mode' framing over-reads.")

    out_dir = _PROJECT_ROOT / "results" / "mode-semantic-validity"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
