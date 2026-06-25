#!/usr/bin/env python3
# register: causal (attention-edge necessity; s239 sufficiency/necessity protocol)
"""Attention-EDGE knockout — is object-application carried by the predicate→object
attention edge? (the s250-thread CATCH test).

THE CATCH. Every s250 causal null measured the WRONG register. They ablated the
RESIDUAL stream (d_C direction, s250) or erased the FFN gate field (INLP, s250-cont)
and concluded object-application is "distributed, no discrete locus." But the standing
mechanism hypothesis (s127 {B,C}=composers→attention; s206 value register; the
attention-as-beta §3 row: "softmax-V substitutes a value → over-reads, value register
SMEARED") points at the ATTENTION EDGE, not a residual/FFN WRITE. "No locus as a
write" is NOT "no locus as an edge." s250-cont.3 even knocked out single-component
WRITES and found nothing — but never severed an EDGE. This experiment severs the edge.

THE INTERVENTION (edge knockout via the eager additive mask, Geva 2023 / Wang IOI
style): block every query position from attending to the OBJECT key token(s) across a
band of layers / all heads. If object content can never route into the rest of the
computation and object-application is attention-mediated, next-token prediction MUST be
damaged — and the damage must SCALE with object load. CONTROL: block the same NUMBER of
RANDOM non-object content keys (count-matched) → subtracts the generic "a content token
is missing" perturbation. NET = KL(object-edge) − KL(random-edge) is the object-edge-
SPECIFIC effect.

THE MATCHED LADDER (data/reading-probes.jsonl, 45×3, const labeling C-count==#objects):
  c0 intransitive (0 objects) — no object edge (floor / random-vs-random sanity)
  c1 transitive   (1 object)  — block 1 object key
  c2 ditransitive (2 objects) — block 2 object keys
The PRIMARY test is the POS-matched c1-vs-c2 contrast (both noun-ending) — this is the
exact comparison whose RESIDUAL differential REVERSED in s250 (c2<c0). If the EDGE
differential instead SCALES (net-KL c2 > c1, beats count-matched random) → the catch is
real: the mechanism is the attention edge the residual/FFN probes could not see.

VERDICT (λ measure, two-sided):
  catch_confirmed = necessity_ok AND load_scaling_ok
    necessity_ok    : NET-KL over objects (c1∪c2) > 0, paired t>2 (object-edge ≫ random)
    load_scaling_ok : NET-KL c2 > NET-KL c1, two-sample t>2 (count-controlled → scales)
  necessity WITHOUT scaling ⇒ severing the object edge perturbs generically but does
    not track object-application ⇒ the DISTRIBUTED verdict HOLDS even at the edge (a
    λ-measure win that holds the boundary against my own catch hypothesis).

Usage:
    uv run python scripts/experiments/program_edge_knockout.py --smoke
    uv run python scripts/experiments/program_edge_knockout.py \
        --model Qwen/Qwen3-14B --layers all

License: MIT. AGENTS.md S5 λ provenance (written from this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from kernel_reference_prose_v2 import read_last_token_z  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _hook_module,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
)

RESULTS_DIR = _ROOT / "results" / "program-edge-knockout"
READING_PROBES = _ROOT / "data" / "reading-probes.jsonl"


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader — EAGER attention so an explicit 4D additive mask is editable
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_eager(model_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[edge] tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    print(f"[edge] model: {model_name} (eager attn, dtype=auto, device_map=auto)")
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto",
        attn_implementation="eager",
    )
    model.eval()
    return model, tok, torch


# ═══════════════════════════════════════════════════════════════════════════════
# Corpus + object-token localization (objects parsed from const_fol)
# ═══════════════════════════════════════════════════════════════════════════════
_PRED_RE = re.compile(r"([a-zA-Z_]+)\(([^()]*)\)")


def object_words(const_fol: str) -> list[str]:
    """Object constants = non-variable args of the consequent relation.

    '∀x. soldier(x) → reads(x, owl)'        → ['owl']
    '∀x. knight(x) → gives(x, queen, book)' → ['queen', 'book']
    '∀x. king(x) → speaks(x)'               → []  (intransitive)
    """
    consequent = const_fol.split("→")[-1]
    m = _PRED_RE.search(consequent)
    if not m:
        return []
    args = [a.strip() for a in m.group(2).split(",")]
    return [a for a in args if a and a != "x"]


def subject_word(const_fol: str) -> str | None:
    """Subject restrictor noun = unary predicate of the ANTECEDENT.

    '∀x. soldier(x) → reads(x, owl)' → 'soldier'  (a noun argument, like the object,
    but NOT the applied object → the noun-vs-noun control for object-specificity)."""
    antecedent = const_fol.split("→")[0]
    m = _PRED_RE.search(antecedent)
    return m.group(1) if m else None


def load_ladder(path: Path) -> list[dict]:
    rows = []
    for line in open(path, encoding="utf-8"):
        r = json.loads(line)
        rows.append({
            "input": r["input"],
            "category": r["category"],
            "n_objects": r["n_objects"],
            "c_count": r["const_c"],
            "objects": object_words(r["const_fol"]),
            "subject": subject_word(r["const_fol"]),
        })
    return rows


def object_key_positions(prompt: str, objects: list[str], tok) -> list[int]:
    """Token indices (kv positions) covering the object words in `prompt`."""
    enc = tok(prompt, return_offsets_mapping=True)
    offsets = enc["offset_mapping"]
    pos: list[int] = []
    for w in objects:
        m = re.search(rf"\b{re.escape(w)}\b", prompt)
        if not m:
            continue
        a, b = m.span()
        for ti, (s, e) in enumerate(offsets):
            if e > s and s < b and e > a:   # token char span overlaps the word
                pos.append(ti)
    return sorted(set(pos))


# ═══════════════════════════════════════════════════════════════════════════════
# Edge-knockout hook — block attention TO `blocked_keys` (all queries, all heads)
# ═══════════════════════════════════════════════════════════════════════════════
def make_edge_hook(blocked_keys: list[int], torch_mod, head=None, n_heads=None):
    """forward_pre_hook(with_kwargs) on a self_attn module. Adds -inf to the additive
    attention mask at the blocked KEY columns → no query position can attend to them.

    head=None  → block ALL heads (broadcast mask edit; the original behavior).
    head=h     → block ONLY query-head h's edge to the object key(s). The additive mask
                 is usually [B,1,Q,K] (broadcast over heads); we expand dim-1 to n_heads
                 and write -inf at [:, h, :, cols] so a SINGLE head loses the edge while
                 every other head keeps it. The head-resolved edge intervention."""
    bk = list(blocked_keys)

    def pre_hook(_module, args, kwargs):
        mask = kwargs.get("attention_mask", None)
        idx_in_args = None
        if mask is None:
            for i, a in enumerate(args):
                if torch_mod.is_tensor(a) and a.dim() == 4:
                    mask, idx_in_args = a, i
                    break
        if mask is None or not torch_mod.is_tensor(mask) or mask.dim() != 4:
            return args, kwargs        # nothing editable (e.g. None/BlockMask)
        mask = mask.clone()
        neg = torch_mod.finfo(mask.dtype).min
        kv = mask.shape[-1]
        cols = [k for k in bk if 0 <= k < kv]
        if cols:
            if head is None:
                mask[:, :, :, cols] = neg
            else:
                if mask.shape[1] == 1 and n_heads and n_heads > 1:
                    mask = mask.expand(mask.shape[0], n_heads, mask.shape[2],
                                       mask.shape[3]).clone()
                h = head if head < mask.shape[1] else mask.shape[1] - 1
                mask[:, h, :, cols] = neg
        if idx_in_args is not None:
            args = tuple(mask if i == idx_in_args else a for i, a in enumerate(args))
        else:
            kwargs["attention_mask"] = mask
        return args, kwargs

    return pre_hook


def forward_edge(prompt, model, tok, torch_mod, gate_layers, blocked_keys, edge_layers,
                 head=None, n_heads=None):
    """ONE forward with gate-capture hooks (for z(C)) + optional edge pre-hooks.
    Returns (gate_store, next_token_logits)."""
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in gate_layers:
        handles.append(_hook_module(model, li, "gate").register_forward_hook(
            _make_hook(store, li)))
    if blocked_keys:
        hook = make_edge_hook(blocked_keys, torch_mod, head=head, n_heads=n_heads)
        for li in edge_layers:
            handles.append(model.model.layers[li].self_attn.register_forward_pre_hook(
                hook, with_kwargs=True))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            out = model(**inputs)
        logits = out.logits[0, -1, :].detach().float().cpu().numpy().astype(np.float64)
    finally:
        for h in handles:
            h.remove()
    return store, logits


# ═══════════════════════════════════════════════════════════════════════════════
# Readouts (shared with cfield)
# ═══════════════════════════════════════════════════════════════════════════════
def log_softmax(logits: np.ndarray) -> np.ndarray:
    z = logits - logits.max()
    return z - np.log(np.exp(z).sum())


def kl_div(logp_p: np.ndarray, logp_q: np.ndarray) -> float:
    return float(np.sum(np.exp(logp_p) * (logp_p - logp_q)))


def zC_field(rcc, store, all_layers, crystal_layers) -> float:
    """Mean last-token z(C) over the crystal layers = the applicative-C field. This is
    the object-application-SPECIFIC readout (s249/s250); next-token KL is recency-
    confounded, z(C) is not (it reads the combinator classifier, not surface tokens)."""
    zmap = read_last_token_z(rcc, store, all_layers)
    zs = [zmap[li]["C"] for li in crystal_layers if li in zmap]
    return float(np.mean(zs)) if zs else float("nan")


def paired(a_list, b_list) -> dict:
    a, b = np.asarray(a_list, float), np.asarray(b_list, float)
    mask = np.isfinite(a) & np.isfinite(b)
    a, b = a[mask], b[mask]
    n = len(a)
    if n < 2:
        return {"n": n, "a_mean": None, "b_mean": None, "delta": None, "t": None}
    diff = a - b
    sd = diff.std(ddof=1)
    se = sd / np.sqrt(n) if sd > 0 else 0.0
    return {"n": n, "a_mean": round(float(a.mean()), 5),
            "b_mean": round(float(b.mean()), 5),
            "delta": round(float(diff.mean()), 5),
            "t": round(float(diff.mean() / se), 3) if se > 0 else None}


def two_sample_t(a_list, b_list) -> dict:
    a = np.asarray([x for x in a_list if np.isfinite(x)], float)
    b = np.asarray([x for x in b_list if np.isfinite(x)], float)
    if len(a) < 2 or len(b) < 2:
        return {"na": len(a), "nb": len(b), "mean_a": None, "mean_b": None,
                "diff": None, "t": None}
    se = np.sqrt(a.var(ddof=1) / len(a) + b.var(ddof=1) / len(b))
    diff = a.mean() - b.mean()
    return {"na": len(a), "nb": len(b), "mean_a": round(float(a.mean()), 5),
            "mean_b": round(float(b.mean()), 5), "diff": round(float(diff), 5),
            "t": round(float(diff / se), 3) if se > 0 else None}


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    ap = argparse.ArgumentParser(description="Attention-edge knockout (s250 catch)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--mode", default="scaling",
                    choices=["scaling", "control", "sweep", "heads"],
                    help="scaling=object vs random + c2/c1; control=object vs subject "
                         "noun (specificity); sweep=layer-band gateway localization; "
                         "heads=per-head edge knockout in --head-band (which route)")
    ap.add_argument("--bands", type=int, default=8, help="sweep: # contiguous bands")
    ap.add_argument("--head-band", default="0-4",
                    help="heads mode: layer band 'lo-hi' to per-head sweep (the sweep "
                         "gateway; default L0-4)")
    ap.add_argument("--layers", default="all", choices=["all", "crystal"],
                    help="layer band to sever the object edge across")
    ap.add_argument("--n-rand", type=int, default=3)
    ap.add_argument("--max-per-group", type=int, default=None)
    ap.add_argument("--null-mode", default="gateneutral",
                    choices=["gateneutral", "crosstask"])
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, null_cap, max_per_group = 80, 3, 200, args.max_per_group or 5
        print("[edge] SMOKE MODE")
    else:
        n_perm, ppc, null_cap, max_per_group = 300, None, None, args.max_per_group

    ladder = load_ladder(READING_PROBES)
    model, tok, torch_mod = load_model_eager(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))

    rcc, cal = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                            null_mode=args.null_mode, hook="gate")
    crystal_layers = rcc.crystal_layers
    edge_layers = layers if args.layers == "all" else crystal_layers
    gate_n = gate_prefix_len(tok)
    print(f"[edge] model={model_name} layers={n_layers} edge_band={args.layers}"
          f"({len(edge_layers)}L) crystal={len(crystal_layers)} (z(C) field readout)")

    def grp(cc):
        g = [r for r in ladder if r["c_count"] == cc]
        return g[:max_per_group] if max_per_group else g
    c0, c1, c2 = grp(0), grp(1), grp(2)
    print(f"[edge] c0={len(c0)} c1={len(c1)} c2={len(c2)}")

    rng = np.random.default_rng(args.seed)

    def content_keys(prompt) -> tuple[int, list[int]]:
        n_tok = len(tok(prompt)["input_ids"])
        return n_tok, [i for i in range(gate_n, n_tok)]

    def keys_for(prompt, words, n_tok):
        return [k for k in object_key_positions(prompt, words, tok)
                if gate_n <= k < n_tok]

    def write_out(suffix, vdict, method, scope):
        RESULTS_DIR.mkdir(parents=True, exist_ok=True)
        slug = model_name.split("/")[-1].lower().replace(".", "-")
        (RESULTS_DIR / f"verdict_{slug}_{suffix}.json").write_text(
            json.dumps(_json_safe({"verdict": vdict, "calibration_summary": cal}),
                       indent=2), encoding="utf-8")
        meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
                "timestamp_utc": datetime.now(UTC).isoformat(),
                "transformers_version": _transformers_version(), "mode": args.mode,
                "edge_band": args.layers, "n_edge_layers": len(edge_layers),
                "n_rand": args.n_rand, "seed": args.seed, "null_mode": args.null_mode,
                "probe_set": str(READING_PROBES.relative_to(_ROOT)),
                "method": method, "scope": scope}
        (RESULTS_DIR / f"meta_{slug}_{suffix}.json").write_text(
            json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
        print(f"[edge] wrote verdict_{slug}_{suffix}.json (+ meta)")

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: control — noun-vs-noun (object vs SUBJECT vs random), c1 only.
    # Is the necessity object-application-SPECIFIC, or just "remove a salient noun"?
    # c1 (transitive) = subject 1 noun, object 1 noun → count-matched noun-vs-noun.
    # ═══════════════════════════════════════════════════════════════════════════
    if args.mode == "control":
        print("[edge] MODE=control (object-noun vs subject-noun vs random, c1) ...")
        rows = []
        for i, r in enumerate(c1):
            prompt = COMPILE_GATE + r["input"]
            n_tok, content = content_keys(prompt)
            ok = keys_for(prompt, r["objects"], n_tok)
            sk = keys_for(prompt, [r["subject"]] if r["subject"] else [], n_tok)
            if not ok or not sk:
                continue
            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [],
                                     edge_layers)
            zc0 = zC_field(rcc, store0, layers, crystal_layers)
            store_o, _ = forward_edge(prompt, model, tok, torch_mod, layers, ok,
                                      edge_layers)
            store_s, _ = forward_edge(prompt, model, tok, torch_mod, layers, sk,
                                      edge_layers)
            zc_o = zC_field(rcc, store_o, layers, crystal_layers)
            zc_s = zC_field(rcc, store_s, layers, crystal_layers)
            pool = [k for k in content if k not in set(ok) | set(sk)]
            zc_rs = []
            for _ in range(args.n_rand):
                rk = (list(rng.choice(pool, size=len(ok), replace=False))
                      if len(pool) >= len(ok) else list(pool))
                store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk,
                                          edge_layers)
                zc_rs.append(zC_field(rcc, store_r, layers, crystal_layers))
            zc_r = float(np.mean(zc_rs))
            rows.append({"drop_obj": zc0 - zc_o, "drop_subj": zc0 - zc_s,
                         "drop_rand": zc0 - zc_r})
            if (i + 1) % 10 == 0:
                print(f"[edge]   control {i + 1}/{len(c1)}")

        def c(k):
            return [x[k] for x in rows]
        obj_vs_subj = paired(c("drop_obj"), c("drop_subj"))   # >0 ⇒ object-specific
        obj_vs_rand = paired(c("drop_obj"), c("drop_rand"))
        subj_vs_rand = paired(c("drop_subj"), c("drop_rand"))
        object_specific = bool((obj_vs_subj["delta"] or 0) > 0
                               and (obj_vs_subj["t"] or 0) > 2.0)
        vdict = {"model": model_name, "n_layers": n_layers, "mode": "control",
                 "edge_band": args.layers, "n_c1": len(rows), "n_rand": args.n_rand,
                 "seed": args.seed, "readout": "z(C) field over crystal layers",
                 "mean_drop_obj": round(float(np.mean(c("drop_obj"))), 5),
                 "mean_drop_subj": round(float(np.mean(c("drop_subj"))), 5),
                 "mean_drop_rand": round(float(np.mean(c("drop_rand"))), 5),
                 "object_vs_subject": obj_vs_subj, "object_vs_random": obj_vs_rand,
                 "subject_vs_random": subj_vs_rand,
                 "object_specific": object_specific}
        print("\n" + "═" * 82)
        print(f"EDGE CONTROL (noun-vs-noun) — {model_name}  n={len(rows)}")
        print("═" * 82)
        print(f"  z(C) drop: object={vdict['mean_drop_obj']} "
              f"subject={vdict['mean_drop_subj']} random={vdict['mean_drop_rand']}")
        print(f"  object vs subject : Δ={obj_vs_subj['delta']} t={obj_vs_subj['t']}")
        print(f"  object vs random  : Δ={obj_vs_rand['delta']} t={obj_vs_rand['t']}")
        print(f"  subject vs random : Δ={subj_vs_rand['delta']} t={subj_vs_rand['t']}")
        print(f"\n  * OBJECT-SPECIFIC (object collapse > subject) = {object_specific}")
        print("═" * 82 + "\n")
        write_out("control", vdict,
                  "Noun-vs-noun control on c1 (transitive): z(C) collapse under "
                  "object-noun edge vs SUBJECT-noun edge vs count-matched random. "
                  "object_specific = object drop > subject drop (paired t>2).",
                  "Tests whether the edge necessity is object-application-specific or "
                  "a generic salient-noun effect (the s-edge-knockout #1 IOU).")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: sweep — sever the object edge in contiguous layer BANDS to localize the
    # gateway depth. Per band: z(C) drop (object) vs count-matched random edge.
    # ═══════════════════════════════════════════════════════════════════════════
    if args.mode == "sweep":
        nb = args.bands
        bands = [list(b) for b in np.array_split(np.array(layers), nb)]
        print(f"[edge] MODE=sweep {nb} bands: "
              f"{[(b[0], b[-1]) for b in bands]}")
        items = c1 + c2
        agg = [{"obj": [], "rand": []} for _ in bands]
        for i, r in enumerate(items):
            prompt = COMPILE_GATE + r["input"]
            n_tok, content = content_keys(prompt)
            ok = keys_for(prompt, r["objects"], n_tok)
            if not ok:
                continue
            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [], [])
            zc0 = zC_field(rcc, store0, layers, crystal_layers)
            pool = [k for k in content if k not in set(ok)]
            for bi, band in enumerate(bands):
                store_o, _ = forward_edge(prompt, model, tok, torch_mod, layers, ok,
                                          band)
                agg[bi]["obj"].append(zc0 - zC_field(rcc, store_o, layers,
                                                      crystal_layers))
                rk = (list(rng.choice(pool, size=len(ok), replace=False))
                      if len(pool) >= len(ok) else list(pool))
                store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk,
                                          band)
                agg[bi]["rand"].append(zc0 - zC_field(rcc, store_r, layers,
                                                      crystal_layers))
            if (i + 1) % 10 == 0:
                print(f"[edge]   sweep {i + 1}/{len(items)}")
        band_rows = []
        for bi, band in enumerate(bands):
            o, rd = np.asarray(agg[bi]["obj"]), np.asarray(agg[bi]["rand"])
            net = paired(list(o), list(rd))   # object drop − random drop, per band
            band_rows.append({
                "band": [int(band[0]), int(band[-1])], "n_layers": len(band),
                "mean_drop_obj": round(float(o.mean()), 5),
                "mean_drop_rand": round(float(rd.mean()), 5),
                "net_obj_minus_rand": net["delta"], "t": net["t"]})
        peak = max(band_rows, key=lambda b: (b["net_obj_minus_rand"] or -1e9))
        vdict = {"model": model_name, "n_layers": n_layers, "mode": "sweep",
                 "n_bands": nb, "n_items": len(items), "n_rand": args.n_rand,
                 "seed": args.seed, "readout": "z(C) field over crystal layers",
                 "bands": band_rows, "peak_band": peak["band"],
                 "peak_net": peak["net_obj_minus_rand"], "peak_t": peak["t"]}
        print("\n" + "═" * 82)
        print(f"EDGE SWEEP (gateway localization) — {model_name}  {nb} bands")
        print("═" * 82)
        def _f(x, w):
            return f"{x:>{w}}" if x is not None else f"{'n/a':>{w}}"
        print(f"  {'band':>10} {'obj':>9} {'rand':>9} {'net':>9} {'t':>7}")
        for b in band_rows:
            print(f"  L{b['band'][0]:>2}-{b['band'][1]:<2}    "
                  f"{_f(b['mean_drop_obj'], 9)} {_f(b['mean_drop_rand'], 9)} "
                  f"{_f(b['net_obj_minus_rand'], 9)} {_f(b['t'], 7)}")
        print(f"\n  * PEAK gateway band = L{peak['band'][0]}-{peak['band'][1]}  "
              f"net={peak['net_obj_minus_rand']} t={peak['t']}")
        print("═" * 82 + "\n")
        write_out("sweep", vdict,
                  f"Layer-band sweep ({nb} contiguous bands): per band, z(C) collapse "
                  "under object-edge knockout vs count-matched random edge. Localizes "
                  "the gateway depth = band with max net(object−random) drop.",
                  "Localizes WHERE severing the predicate→object edge collapses the "
                  "applicative-C field (necessity → depth-resolved circuit).")
        return

    # ═══════════════════════════════════════════════════════════════════════════
    # MODE: heads — per-head edge knockout inside the gateway band (L0-4 from the
    # sweep). For each (layer, head) sever ONLY that head's object edge → z(C) drop.
    # Does the early necessity concentrate in a FEW heads (a discrete head circuit,
    # the s127 {B,C}=composer test) or spread across all heads (distributed)?
    # ═══════════════════════════════════════════════════════════════════════════
    if args.mode == "heads":
        n_heads = model.config.num_attention_heads
        lo, hi = (int(x) for x in args.head_band.split("-"))
        band = [li for li in range(lo, hi + 1) if 0 <= li < n_layers]
        cap = max_per_group or 10
        items = grp(1)[:cap] + grp(2)[:cap]
        print(f"[edge] MODE=heads band=L{lo}-{hi} ({len(band)}L) × {n_heads} heads, "
              f"n_items={len(items)} (per-head object-edge knockout)")
        agg: dict[tuple[int, int], list[float]] = {}
        floor: list[float] = []
        for i, r in enumerate(items):
            prompt = COMPILE_GATE + r["input"]
            n_tok, content = content_keys(prompt)
            ok = keys_for(prompt, r["objects"], n_tok)
            if not ok:
                continue
            store0, _ = forward_edge(prompt, model, tok, torch_mod, layers, [], [])
            zc0 = zC_field(rcc, store0, layers, crystal_layers)
            for li in band:
                for h in range(n_heads):
                    store_h, _ = forward_edge(prompt, model, tok, torch_mod, layers,
                                              ok, [li], head=h, n_heads=n_heads)
                    agg.setdefault((li, h), []).append(
                        zc0 - zC_field(rcc, store_h, layers, crystal_layers))
            pool = [k for k in content if k not in set(ok)]
            rk = (list(rng.choice(pool, size=len(ok), replace=False))
                  if len(pool) >= len(ok) else list(pool))
            store_r, _ = forward_edge(prompt, model, tok, torch_mod, layers, rk, band)
            floor.append(zc0 - zC_field(rcc, store_r, layers, crystal_layers))
            if (i + 1) % 5 == 0:
                print(f"[edge]   heads {i + 1}/{len(items)}")
        head_rows = []
        for (li, h), drops in agg.items():
            st = paired(drops, [0.0] * len(drops))   # mean drop + t vs 0
            head_rows.append({"layer": li, "head": h, "n": st["n"],
                              "mean_drop": st["a_mean"], "t": st["t"]})
        head_rows.sort(key=lambda x: -(x["mean_drop"] or -1e9))
        pos = [max(0.0, hr["mean_drop"] or 0.0) for hr in head_rows]
        total = float(sum(pos)) or 1.0
        shares = (np.cumsum(pos) / total).tolist()
        n_for_80 = int(np.searchsorted(shares, 0.8) + 1) if pos else 0
        top5_share = round(float(sum(pos[:5]) / total), 4)
        carriers = [hr for hr in head_rows
                    if (hr["mean_drop"] or 0) > 0 and (hr["t"] or 0) > 2.0]
        # discrete head circuit = a handful of heads carry most of the early route
        discrete = bool(0 < n_for_80 <= 5)
        floor_mean = round(float(np.mean(floor)), 5) if floor else None
        vdict = {"model": model_name, "n_layers": n_layers, "mode": "heads",
                 "head_band": [lo, hi], "n_heads": n_heads, "n_items": len(items),
                 "readout": "z(C) field over crystal layers",
                 "random_key_floor_mean": floor_mean,
                 "n_carriers_t2": len(carriers), "n_heads_for_80pct": n_for_80,
                 "top5_share": top5_share, "discrete_head_circuit": discrete,
                 "top_heads": head_rows[:15], "all_heads": head_rows}
        print("\n" + "═" * 82)
        print(f"EDGE HEAD-KNOCKOUT (which heads route object→C) — {model_name}  "
              f"L{lo}-{hi} × {n_heads} heads")
        print("═" * 82)
        print(f"  random-key floor (all heads, band) z(C) drop = {floor_mean}")
        print(f"  {'rank':>4} {'layer':>6} {'head':>5} {'mean_drop':>10} {'t':>7}")
        for k, hr in enumerate(head_rows[:15]):
            print(f"  {k + 1:>4} {hr['layer']:>6} {hr['head']:>5} "
                  f"{hr['mean_drop']:>10} {(hr['t'] if hr['t'] is not None else 0):>7}")
        print(f"\n  carriers (mean_drop>0, t>2) = {len(carriers)}  |  "
              f"heads for 80% = {n_for_80}  |  top5 share = {top5_share}")
        print(f"  * DISCRETE HEAD CIRCUIT (\u22645 heads carry 80%) = {discrete}")
        print("═" * 82 + "\n")
        write_out("heads", vdict,
                  f"Per-head object-edge knockout across L{lo}-{hi} (sweep gateway): "
                  "each (layer,head) severs ONLY that head's attention to the object "
                  "key (per-head additive mask) → z(C) collapse vs baseline; "
                  "concentration (heads-to-80%, top5 share) = discrete vs distributed.",
                  "Localizes WHICH heads carry the early object→C route (s127 "
                  "{B,C}=composer test) — head-resolved circuit vs distributed.")
        return

    # ── per-item run: object-edge KL, count-matched random-edge KL, z(C) ──────────
    def run_item(r):
        prompt = COMPILE_GATE + r["input"]
        # baseline (no knockout)
        store0, logits0 = forward_edge(prompt, model, tok, torch_mod, layers, [],
                                       edge_layers)
        logp0 = log_softmax(logits0)
        zc0 = zC_field(rcc, store0, layers, crystal_layers)
        n_tok, content = content_keys(prompt)
        obj_keys = [k for k in object_key_positions(prompt, r["objects"], tok)
                    if gate_n <= k < n_tok]
        if not obj_keys:
            return None
        # object-edge knockout
        store_o, logits_o = forward_edge(prompt, model, tok, torch_mod, layers,
                                         obj_keys, edge_layers)
        kl_obj = kl_div(log_softmax(logits_o), logp0)
        zc_obj = zC_field(rcc, store_o, layers, crystal_layers)
        # count-matched random-content-edge control (avg over n_rand draws)
        pool = [k for k in content if k not in set(obj_keys)]
        kl_rs, zc_rs = [], []
        for _ in range(args.n_rand):
            if len(pool) >= len(obj_keys):
                rk = list(rng.choice(pool, size=len(obj_keys), replace=False))
            else:
                rk = list(pool)
            store_r, logits_r = forward_edge(prompt, model, tok, torch_mod, layers,
                                             rk, edge_layers)
            kl_rs.append(kl_div(log_softmax(logits_r), logp0))
            zc_rs.append(zC_field(rcc, store_r, layers, crystal_layers))
        zc_rand = float(np.mean(zc_rs))
        # object-application-SPECIFIC effect: how much MORE the object edge collapses
        # the applicative-C field than a count-matched random edge does. Positive =
        # object edge is load-bearing for the C field.
        return {
            "kl_obj": kl_obj, "kl_rand": float(np.mean(kl_rs)),
            "net_kl": kl_obj - float(np.mean(kl_rs)),
            "zc0": zc0, "zc_obj": zc_obj, "zc_rand": zc_rand,
            "zc_drop_obj": zc0 - zc_obj, "zc_drop_rand": zc0 - zc_rand,
            "net_zc_drop": (zc0 - zc_obj) - (zc0 - zc_rand),   # = zc_rand - zc_obj
            "n_obj_keys": len(obj_keys),
        }

    def run_group(items, name):
        out = []
        for i, r in enumerate(items):
            res = run_item(r)
            if res is not None:
                out.append(res)
            if (i + 1) % 10 == 0:
                print(f"[edge]   {name} {i + 1}/{len(items)}")
        return out

    print("[edge] arm c1 (transitive, 1 object-edge) ...")
    g1 = run_group(c1, "c1")
    print("[edge] arm c2 (ditransitive, 2 object-edges) ...")
    g2 = run_group(c2, "c2")

    def col(g, k):
        return [x[k] for x in g]

    allg = g1 + g2
    # PRIMARY (object-application-specific): does severing the object edge collapse the
    # applicative-C field MORE than a count-matched random edge?  z(C)_obj < z(C)_rand.
    necessity = paired(col(allg, "zc_rand"), col(allg, "zc_obj"))  # rand - obj > 0
    # LOAD-SCALING on the object-specific C-collapse, c2 vs c1 (count-controlled net).
    load_scaling = two_sample_t(col(g2, "net_zc_drop"), col(g1, "net_zc_drop"))
    # SECONDARY (behavioral, RECENCY-CONFOUNDED — report, do not gate on it).
    kl_behav = paired(col(allg, "kl_obj"), col(allg, "kl_rand"))
    kl_scaling = two_sample_t(col(g2, "net_kl"), col(g1, "net_kl"))

    necessity_ok = bool((necessity["delta"] or 0) > 0 and (necessity["t"] or 0) > 2.0)
    load_scaling_ok = bool(
        (load_scaling["diff"] or 0) > 0 and (load_scaling["t"] or 0) > 2.0)
    catch_confirmed = necessity_ok and load_scaling_ok

    verdict = {
        "model": model_name, "n_layers": n_layers, "edge_band": args.layers,
        "n_edge_layers": len(edge_layers), "crystal_layers": crystal_layers,
        "null_mode": args.null_mode, "readout": "z(C) field over crystal layers",
        "n_c1": len(g1), "n_c2": len(g2), "n_rand": args.n_rand, "seed": args.seed,
        "PRIMARY_necessity_zC_collapse_rand_minus_obj": necessity,
        "PRIMARY_load_scaling_net_zC_drop_c2_vs_c1": load_scaling,
        "mean_net_zC_drop_c1": round(float(np.mean(col(g1, "net_zc_drop"))), 5)
        if g1 else None,
        "mean_net_zC_drop_c2": round(float(np.mean(col(g2, "net_zc_drop"))), 5)
        if g2 else None,
        "SECONDARY_kl_behavioral_obj_vs_rand_RECENCY_CONFOUNDED": kl_behav,
        "SECONDARY_kl_scaling_c2_vs_c1": kl_scaling,
        "necessity_ok": necessity_ok, "load_scaling_ok": load_scaling_ok,
        "catch_confirmed": catch_confirmed,
    }

    print("\n" + "═" * 82)
    print(f"ATTENTION-EDGE KNOCKOUT — {model_name}  band={args.layers}"
          f"({len(edge_layers)}L)  readout=z(C) field")
    print("═" * 82)
    print(f"  c1={len(g1)} c2={len(g2)}  (object edge severed across {len(edge_layers)}"
          f" layers, all heads)")
    print("\n  -- PRIMARY NECESSITY (z(C) collapse: rand−obj > 0 ⇒ object edge "
          "feeds C-field) --")
    print(f"     z(C) rand={necessity['a_mean']} obj={necessity['b_mean']} "
          f"drop={necessity['delta']} t={necessity['t']} => {necessity_ok}")
    print("\n  -- PRIMARY LOAD-SCALING (net z(C) drop c2 vs c1; expect c2 > c1) --")
    print(f"     net_drop c2={load_scaling['mean_a']} c1={load_scaling['mean_b']} "
          f"diff={load_scaling['diff']} t={load_scaling['t']} => {load_scaling_ok}")
    print("\n  -- SECONDARY behavioral KL (RECENCY-CONFOUNDED, not gated) --")
    print(f"     KL obj={kl_behav['a_mean']} rand={kl_behav['b_mean']} "
          f"net={kl_behav['delta']} t={kl_behav['t']}")
    print(f"\n  * CATCH CONFIRMED (z(C) necessity AND scaling) = {catch_confirmed}")
    print("═" * 82 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"verdict_{slug}.json").write_text(
        json.dumps(_json_safe({"verdict": verdict, "calibration_summary": cal}),
                   indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
        "timestamp_utc": datetime.now(UTC).isoformat(),
        "transformers_version": _transformers_version(),
        "edge_band": args.layers, "n_edge_layers": len(edge_layers),
        "n_rand": args.n_rand, "seed": args.seed, "null_mode": args.null_mode,
        "probe_set": str(READING_PROBES.relative_to(_ROOT)),
        "method": "EDGE knockout: block all queries from attending to OBJECT key "
                  "token(s) (eager additive mask, all heads, across edge band) vs "
                  "count-matched RANDOM content-key control. PRIMARY readout = "
                  "applicative-C field z(C) (last-token, crystal layers) — object-"
                  "application-specific; next-token KL is SECONDARY (recency-"
                  "confounded). catch = z(C) necessity (object collapses C-field more "
                  "than random) AND scaling (net z(C) drop c2>c1, count-controlled).",
        "scope": "Tests whether object-application is carried by the predicate→object "
                 "attention EDGE — the register the s250 residual/FFN nulls could not "
                 "probe (no locus as a WRITE != no locus as an EDGE).",
    }
    (RESULTS_DIR / f"meta_{slug}.json").write_text(
        json.dumps(_json_safe(meta), indent=2), encoding="utf-8")
    print(f"[edge] wrote {RESULTS_DIR}/verdict_{slug}.json (+ meta)")


if __name__ == "__main__":
    main()
