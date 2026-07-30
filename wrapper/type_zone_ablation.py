#!/usr/bin/env python3
"""P-TYPE-1b — combinator-zone x type-class dissociation (zone x axis ablation).

Pre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
(#p-type-1b, FROZEN s282). Host of record = Qwen3-32B; THIS FILE also runs the 4B
SMOKE (instrument validation + capacity read; a 4B verdict does NOT close 1b).

HYPOTHESIS (frozen): if type = which opcode's application is licensed, ablating a
role-specific type axis as a ZONE across the low-rank band selectively breaks the
matching type-class:
  - binding axis (QUANT+DET loadings; S/binding role)  -> breaks quantifier licensing
  - composition axis (MOD loadings; B/composition role) -> breaks modifier licensing
Double dissociation; nulls (random matched direction, e/ENTITY-origin direction,
non-compositional recall task) break neither. v4 (global direction, crossover
retention) was correctly negative; this is zone x axis CLASS-selectivity.

INSTRUMENT
  1. Capture the labeled Montague-type dataset at every decoder layer (reuses
     probe_type_qwen3_32b capture; residuals[L] = output of model.layers[L]).
  2. Per layer: standardize (diagonal whiten - the 1a massive-activation lesson),
     centroid SVD, PR + shuffled-label null. BAND = longest contiguous run of
     layers with p_lowrank < 0.05 (fallback: interior min-p +/- 3).
  3. Per band layer, pick axes BY LOADING PATTERN (not index - axis order may vary
     across layers/scale): bind = argmax QUANT^2+DET^2 energy among top-3;
     comp = argmax MOD^2 energy among remaining; e-dir = ENTITY centroid direction.
  4. Zone ablation = at every band layer, every token position, remove the axis in
     STANDARDIZED space: h' = h - (((h-mu)/sd) . v) (sd*v). This is the exact
     projection in the space the axes live in (an oblique projection in raw space;
     raw-space removal would target rogue massive-activation dims - lambda measure).

BEHAVIOURAL READOUTS (v3-style nonce surprisal; frequency-free)
  ONE teach pair (noun vs adj) x THREE frames, all fully crossed & paired by nonce:
     teach noun: "{W}s are common objects."     teach adj: "The dogs are {w}."
     frame quant: "Every {w}"    (QUANT licenses a NOUN)
     frame mod:   "It was very {w}"  (intensifier licenses an ADJ)
     frame name:  "John {w}"     (licenses a PRED; SHARED REFERENCE arm)
  pref(f) = S(f|adj-taught) - S(f|noun-taught)   (per nonce)
  Q_eff = pref(quant) - pref(name)   > 0 baseline   (quantifier-class licensing)
  M_eff = pref(name)  - pref(mod)    > 0 baseline   (modifier-class licensing)
  Both are crossover interactions against the SAME name arm -> the teach main
  effect cancels IDENTICALLY in both -> Q_eff / M_eff are cross-comparable, which
  is exactly what the dissociation verdict compares. Recall task = task control.

VERDICT (pre-set margins, frozen here before the run; ret = effect/baseline):
  GATE-0 (ceiling): baseline Q_eff and M_eff both mean>0 with t>=3 - else the host
    cannot express the classes and NO ablation cell is interpreted (4B risk: 0.6B
    resolved ~1 axis; a Gate-0/axis-resolution failure at 4B is itself the finding).
  BIND-SELECTIVE: ret(Q,bind)<0.5 AND ret(M,bind)>0.7
  COMP-SELECTIVE: ret(M,comp)<0.5 AND ret(Q,comp)>0.7
  NULLS: random + e-axis keep BOTH rets>0.7 ; recall surprisal ratio<1.2 all conds
  DISSOCIATION_SUPPORTED <=> gate0 & bind & comp & nulls. Anything less: verbatim.

lambda measure: ablation target = value-register band axes; claim = reduction
LICENSING -> readout is behavioural class-selectivity, never decodability change.
A RUNG: hook-not-weight; zone-not-weights; one class pair, not the whole lattice.

Usage:
    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B --smoke
    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-4B
    uv run python wrapper/type_zone_ablation.py --model Qwen/Qwen3-32B   # verdict host

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "explore"))

from probe_type_qwen3_32b import (  # noqa: E402
    LABELED_DATA,
    build_probing_dataset,
    get_transformer_layers,
    load_model,
)
from type_lattice_geometry import (  # noqa: E402
    TYPE_ORDER,
    centroids,
    participation_ratio,
)

# ── behavioural items ──────────────────────────────────────────────────────────
NONCE = ["wug", "blicket", "dax", "fep", "gorp", "zorp",
         "fendle", "glorp", "narp", "trisk"]

# teach templates: NO quantifiers, NO intensifiers, NO test-frame leakage
NOUN_TEACH = ["{W}s are common objects.", "He collected several {w}s.",
              "Those {w}s are nice.", "She bought two {w}s."]
ADJ_TEACH = ["The dogs are {w}.", "His car looks {w}.",
             "The food tasted {w}.", "That house seems {w}."]

QUANT_FILL = ["Every", "Each", "Some", "No", "Most", "All"]
MOD_FILL = ["It was very", "The dog seemed quite", "That movie was rather",
            "She felt extremely", "The room looked really", "His voice sounded so"]
NAME_FILL = ["John", "Mary", "Sarah", "David", "Peter", "Susan"]

# non-compositional task control (lexical recall; gold graded as continuation)
RECALL = [("The capital of France is", " Paris"),
          ("The capital of Japan is", " Tokyo"),
          ("The capital of Italy is", " Rome"),
          ("Water is made of hydrogen and", " oxygen"),
          ("The opposite of hot is", " cold"),
          ("Two plus two equals", " four"),
          ("The sun rises in the", " east"),
          ("The color of snow is", " white"),
          ("A week has seven", " days"),
          ("The largest ocean is the", " Pacific")]

CONDS = ["baseline", "bind_axis", "comp_axis", "random", "e_axis"]


# ── geometry: band + axes (standardized space) ─────────────────────────────────
def layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int) -> dict:
    """Standardize -> centroid SVD -> PR + shuffled-label null + axes."""
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-6
    z = (x - mu) / sd

    def pr_of(labels):
        c, present = centroids(z, labels, TYPE_ORDER)
        if len(present) < 3:
            return float("nan"), None, None, None
        cc = c - c.mean(axis=0, keepdims=True)
        u, s, vt = np.linalg.svd(cc, full_matrices=False)
        return participation_ratio(s), present, (u, s, vt), c

    pr_real, present, svd, c = pr_of(y)
    null = []
    for _ in range(n_null):
        prn, _, _, _ = pr_of(rng.permutation(y))
        if not np.isnan(prn):
            null.append(prn)
    null = np.array(null)
    p = float(np.mean(null <= pr_real)) if null.size else None
    return {"mu": mu, "sd": sd, "present": present, "svd": svd, "centroids": c,
            "pr_real": float(pr_real), "p_lowrank": p,
            "pr_null_mean": float(null.mean()) if null.size else None}


def pick_axes(geo: dict) -> dict | None:
    """Select bind/comp axes by loading pattern; e-dir from ENTITY centroid.
    Returns unit directions in STANDARDIZED space + bookkeeping, or None."""
    if geo["svd"] is None:
        return None
    present = geo["present"]
    idx = {t: i for i, t in enumerate(present)}
    if not {"QUANT", "DET", "MOD", "ENTITY"} <= set(idx):
        return None
    u, s, vt = geo["svd"]
    k = min(3, len(s))
    tot = (s ** 2).sum() + 1e-12
    bind_scores = [u[idx["QUANT"], i] ** 2 + u[idx["DET"], i] ** 2 for i in range(k)]
    bind_i = int(np.argmax(bind_scores))
    mod_scores = [u[idx["MOD"], i] ** 2 if i != bind_i else -1.0 for i in range(k)]
    comp_i = int(np.argmax(mod_scores))

    def unit(v):
        return v / (np.linalg.norm(v) + 1e-12)

    c = geo["centroids"]
    e_dir = unit(c[idx["ENTITY"]] - c.mean(axis=0))
    return {"bind": unit(vt[bind_i]), "comp": unit(vt[comp_i]), "e": e_dir,
            "bind_i": bind_i, "comp_i": comp_i,
            "bind_var": float(s[bind_i] ** 2 / tot),
            "comp_var": float(s[comp_i] ** 2 / tot),
            "bind_score": float(bind_scores[bind_i]),
            "comp_score": float(max(mod_scores))}


def find_band(per_layer: dict[int, dict], n_layers: int) -> list[int]:
    """Longest contiguous run of layers with p_lowrank < 0.05; fallback interior."""
    sig = [L for L in sorted(per_layer) if (per_layer[L]["p_lowrank"] or 1.0) < 0.05]
    best, cur = [], []
    for L in sig:
        cur = [*cur, L] if (cur and L == cur[-1] + 1) else [L]
        if len(cur) > len(best):
            best = cur
    if len(best) >= 3:
        return best
    interior = [L for L in sorted(per_layer)
                if n_layers * 0.15 <= L <= n_layers * 0.65]
    if not interior:
        return sig or sorted(per_layer)[:3]
    lo = min(interior, key=lambda L: per_layer[L]["p_lowrank"] or 1.0)
    return [L for L in sorted(per_layer) if lo - 3 <= L <= lo + 3]


# ── zone ablation hook (exact projection in standardized space) ────────────────
def make_zone_hook(mu: np.ndarray, sd: np.ndarray, v: np.ndarray):
    """h' = h - (((h-mu)/sd) . v) * (sd*v)  at ALL positions (fp32, cast back)."""
    box: dict = {}

    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if not box:
            box["mu"] = torch.as_tensor(mu, dtype=torch.float32, device=h.device)
            box["sd"] = torch.as_tensor(sd, dtype=torch.float32, device=h.device)
            box["v"] = torch.as_tensor(v, dtype=torch.float32, device=h.device)
            box["w"] = box["sd"] * box["v"]
        hf = h.float()
        coeff = ((hf - box["mu"]) / box["sd"]) @ box["v"]        # [B,T]
        hf = hf - coeff.unsqueeze(-1) * box["w"]
        h2 = hf.to(h.dtype)
        return (h2, *out[1:]) if isinstance(out, tuple) else h2

    return hook


# ── surprisal scoring ──────────────────────────────────────────────────────────
def gen_items(n_nonce: int, n_teach: int, n_fill: int) -> list[dict]:
    """Fully crossed (deterministic -> exact pairing by nonce)."""
    items = []
    for w in NONCE[:n_nonce]:
        for ttype, teaches in (("noun", NOUN_TEACH), ("adj", ADJ_TEACH)):
            for teach in teaches[:n_teach]:
                for frame, fills in (("quant", QUANT_FILL), ("mod", MOD_FILL),
                                     ("name", NAME_FILL)):
                    for filler in fills[:n_fill]:
                        items.append({"kind": "typed", "w": w, "teach_type": ttype,
                                      "teach": teach, "frame": frame,
                                      "filler": filler})
    for prompt, gold in RECALL:
        items.append({"kind": "recall", "prompt": prompt, "gold": gold})
    return items


def item_text(it: dict) -> tuple[str, int]:
    """(full_text, char_start_of_target)."""
    if it["kind"] == "recall":
        return it["prompt"] + it["gold"], len(it["prompt"])
    teach = it["teach"].format(w=it["w"], W=it["w"].capitalize())
    prefix = f"{teach} {it['filler']} "
    return prefix + it["w"], len(prefix)


def score_pass(items, model, tok, tag: str) -> list[float | None]:
    """Mean surprisal of the target span per item (order-aligned with items)."""
    import torch.nn.functional as func
    dev = next(model.parameters()).device
    out = []
    for n, it in enumerate(items):
        text, c0 = item_text(it)
        enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
        ids = enc["input_ids"][0]
        offsets = enc["offset_mapping"][0].tolist()
        tgt = [j for j, (s, e) in enumerate(offsets) if e > s and e > c0 and j >= 1]
        if not tgt:
            out.append(None)
            continue
        with torch.no_grad():
            logits = model(input_ids=ids.unsqueeze(0).to(dev)).logits[0]
        logp = func.log_softmax(logits.float(), dim=-1).cpu()
        out.append(float(np.mean([-float(logp[j - 1, ids[j]]) for j in tgt])))
        if n % 60 == 0:
            print(f"[1b] {tag}: {n}/{len(items)}", file=sys.stderr, flush=True)
    return out


# ── stats ──────────────────────────────────────────────────────────────────────
def agg(arr: list[float]) -> dict | None:
    a = np.asarray([v for v in arr if v is not None], dtype=float)
    if len(a) < 2:
        return None
    se = float(a.std(ddof=1) / np.sqrt(len(a)))
    return {"mean": round(float(a.mean()), 4),
            "t": round(float(a.mean() / se) if se > 0 else 0.0, 3), "n": len(a)}


def class_effects(items, scores) -> dict:
    """pref(f)=S(f|adj)-S(f|noun) per nonce; Q_eff/M_eff vs the shared name arm."""
    cell: dict = {}
    for it, s in zip(items, scores, strict=True):
        if it["kind"] != "typed" or s is None:
            continue
        cell.setdefault((it["w"], it["frame"], it["teach_type"]), []).append(s)

    def pref(w, f):
        a = cell.get((w, f, "adj"))
        n = cell.get((w, f, "noun"))
        if not a or not n:
            return None
        return float(np.mean(a) - np.mean(n))

    q_eff, m_eff, prefs = [], [], {"quant": [], "mod": [], "name": []}
    for w in NONCE:
        pq, pm, pn = pref(w, "quant"), pref(w, "mod"), pref(w, "name")
        if None in (pq, pm, pn):
            continue
        q_eff.append(pq - pn)
        m_eff.append(pn - pm)
        for f, v in (("quant", pq), ("mod", pm), ("name", pn)):
            prefs[f].append(v)

    recall = [s for it, s in zip(items, scores, strict=True)
              if it["kind"] == "recall" and s is not None]
    return {"Q_eff": agg(q_eff), "M_eff": agg(m_eff),
            "pref": {f: agg(v) for f, v in prefs.items()},
            "recall_surprisal": round(float(np.mean(recall)), 4) if recall else None}


def retention(eff_abl: dict | None, eff_base: dict | None) -> float | None:
    if not eff_abl or not eff_base or not eff_base.get("mean"):
        return None
    return round(eff_abl["mean"] / eff_base["mean"], 3)


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(description="P-TYPE-1b zone x axis ablation")
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-null", type=int, default=100)
    ap.add_argument("--n-nonce", type=int, default=10)
    ap.add_argument("--n-teach", type=int, default=2)
    ap.add_argument("--n-fill", type=int, default=2)
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true",
                    help="tiny grid (plumbing + ceiling check)")
    ap.add_argument("--output", default=None)
    args = ap.parse_args()
    if args.smoke:
        args.n_nonce, args.n_teach, args.n_fill, args.n_null = 6, 2, 2, 50

    rng = np.random.default_rng(args.seed)
    model, tok, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    layer_mods = get_transformer_layers(model)

    # 1) capture + geometry per decoder layer
    data, n_lab, n_skip = build_probing_dataset(
        model, tok, list(range(n_layers)), LABELED_DATA, verbose=True)
    print(f"[1b] labeled={n_lab} skipped={n_skip}", file=sys.stderr)
    geo = {}
    for L in sorted(data):
        geo[L] = layer_geometry(*data[L], rng, args.n_null)
        g = geo[L]
        print(f"[1b] L{L:2d} PR={g['pr_real']:.2f} null={g['pr_null_mean']:.2f} "
              f"p={g['p_lowrank']}", file=sys.stderr)
    band = find_band(geo, n_layers)
    print(f"[1b] BAND = L{band[0]}..L{band[-1]} ({len(band)} layers)",
          file=sys.stderr)

    # 2) axes per band layer + ablation direction sets
    rng_r = np.random.default_rng(args.seed + 7)
    dirsets: dict[str, list] = {"bind_axis": [], "comp_axis": [],
                                "random": [], "e_axis": []}
    axis_log = {}
    for L in band:
        ax = pick_axes(geo[L])
        if ax is None:
            continue
        mu, sd = geo[L]["mu"], geo[L]["sd"]
        r = rng_r.standard_normal(len(mu))
        r /= np.linalg.norm(r)
        dirsets["bind_axis"].append((L, mu, sd, ax["bind"]))
        dirsets["comp_axis"].append((L, mu, sd, ax["comp"]))
        dirsets["random"].append((L, mu, sd, r))
        dirsets["e_axis"].append((L, mu, sd, ax["e"]))
        axis_log[str(L)] = {k: round(v, 3) if isinstance(v, float) else v
                            for k, v in ax.items()
                            if k in ("bind_i", "comp_i", "bind_var", "comp_var",
                                     "bind_score", "comp_score")}
        axis_log[str(L)]["removal_norms"] = {
            k: round(float(np.linalg.norm(sd * d)), 2)
            for k, d in (("bind", ax["bind"]), ("comp", ax["comp"]),
                         ("random", r), ("e", ax["e"]))}
    print(f"[1b] axis picks per band layer: {json.dumps(axis_log, indent=1)}",
          file=sys.stderr)

    # free the capture memory
    del data
    import gc
    gc.collect()

    # 3) behavioural passes
    items = gen_items(args.n_nonce, args.n_teach, args.n_fill)
    n_typed = sum(1 for i in items if i["kind"] == "typed")
    print(f"[1b] {len(items)} items ({n_typed} typed + {len(RECALL)} recall) "
          f"x {len(CONDS)} conds", file=sys.stderr)

    results = {}
    for cond in CONDS:
        handles = []
        if cond != "baseline":
            for L, mu, sd, v in dirsets[cond]:
                handles.append(layer_mods[L].register_forward_hook(
                    make_zone_hook(mu, sd, v)))
        try:
            scores = score_pass(items, model, tok, cond)
        finally:
            for h in handles:
                h.remove()
        results[cond] = class_effects(items, scores)
        r = results[cond]
        print(f"[1b] {cond:10s} Q_eff={r['Q_eff']} M_eff={r['M_eff']} "
              f"recall={r['recall_surprisal']}", file=sys.stderr)

    # 4) verdict (pre-set margins from the docstring)
    base = results["baseline"]
    gate0 = bool(base["Q_eff"] and base["M_eff"]
                 and base["Q_eff"]["mean"] > 0 and base["Q_eff"]["t"] >= 3
                 and base["M_eff"]["mean"] > 0 and base["M_eff"]["t"] >= 3)
    ret = {c: {"Q": retention(results[c]["Q_eff"], base["Q_eff"]),
               "M": retention(results[c]["M_eff"], base["M_eff"]),
               "recall_ratio": (round(results[c]["recall_surprisal"]
                                      / base["recall_surprisal"], 3)
                                if base["recall_surprisal"] else None)}
           for c in CONDS if c != "baseline"}

    def ok(v, lo=None, hi=None):
        return v is not None and (lo is None or v > lo) and (hi is None or v < hi)

    bind_sel = ok(ret["bind_axis"]["Q"], hi=0.5) and ok(ret["bind_axis"]["M"], lo=0.7)
    comp_sel = ok(ret["comp_axis"]["M"], hi=0.5) and ok(ret["comp_axis"]["Q"], lo=0.7)
    nulls_ok = all(ok(ret[c][k], lo=0.7) for c in ("random", "e_axis")
                   for k in ("Q", "M"))
    recall_ok = all(ok(ret[c]["recall_ratio"], hi=1.2) for c in ret)
    supported = gate0 and bind_sel and comp_sel and nulls_ok and recall_ok

    verdict = {
        "register": "P-TYPE-1b zone x axis ablation (class-selectivity)",
        "host": args.model, "is_prereg_host": args.model == "Qwen/Qwen3-32B",
        "band": [int(band[0]), int(band[-1])], "n_band_layers": len(band),
        "gate0_baseline_expresses_classes": gate0,
        "baseline": base,
        "conditions": {c: results[c] for c in CONDS if c != "baseline"},
        "retention": ret,
        "bind_selective": bind_sel, "comp_selective": comp_sel,
        "nulls_clean": nulls_ok, "recall_control_ok": recall_ok,
        "dissociation_supported": bool(supported),
        "axis_log": axis_log,
        "per_layer_pr": {str(L): {"pr": round(geo[L]["pr_real"], 3),
                                  "p": geo[L]["p_lowrank"]} for L in sorted(geo)},
    }

    print("\n" + "=" * 72)
    print("P-TYPE-1b — combinator-zone x type-class dissociation")
    print("=" * 72)
    print(f"  host={args.model}  band=L{band[0]}..L{band[-1]}  gate0={gate0}")
    print(f"  baseline  Q_eff={base['Q_eff']}  M_eff={base['M_eff']}")
    for c in ret:
        print(f"  {c:10s} retQ={ret[c]['Q']}  retM={ret[c]['M']}  "
              f"recall_ratio={ret[c]['recall_ratio']}")
    print(f"  bind_selective={bind_sel}  comp_selective={comp_sel}  "
          f"nulls={nulls_ok}  recall_ok={recall_ok}")
    print(f"  * dissociation_supported = {supported}")
    print("=" * 72 + "\n")

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out = (Path(args.output) if args.output
           else _ROOT / "results" / "type-zone-ablation" / slug)
    out.mkdir(parents=True, exist_ok=True)
    (out / "verdict.json").write_text(json.dumps(verdict, indent=2))
    try:
        sha = subprocess.run(["git", "rev-parse", "HEAD"], cwd=_ROOT,
                             capture_output=True, text=True).stdout.strip()
    except OSError:
        sha = None
    meta = {"model": args.model, "device": args.device, "smoke": args.smoke,
            "timestamp_utc": datetime.now(UTC).isoformat(), "git_sha": sha,
            "seed": args.seed, "n_null": args.n_null, "n_nonce": args.n_nonce,
            "n_teach": args.n_teach, "n_fill": args.n_fill,
            "n_items": len(items), "n_labeled": n_lab,
            "torch": torch.__version__}
    (out / "meta.json").write_text(json.dumps(meta, indent=2))
    print(f"[1b] wrote {out}/verdict.json + meta.json", file=sys.stderr)


if __name__ == "__main__":
    main()
