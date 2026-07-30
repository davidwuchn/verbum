#!/usr/bin/env python3
"""P-TYPE-1b — combinator-zone x type-class dissociation (zone x subspace, v3).

Pre-reg: mementum/knowledge/explore/types-are-the-well-formedness-of-reduction.md
(#p-type-1b, FROZEN s282). Host of record = Qwen3-32B; THIS FILE also runs the 4B
SMOKE (instrument validation + capacity read; a 4B verdict does NOT close 1b).

HYPOTHESIS (frozen): if type = which opcode's application is licensed, removing a
role-specific slice of the type lattice as a ZONE across the low-rank band
selectively breaks the matching type-class:
  - binding subspace (QUANT/DET; S/binding role)  -> breaks quantifier licensing
  - composition subspace (MOD; B/composition role) -> breaks modifier licensing
Double dissociation; nulls (energy-matched random, role-null lattice subspace,
recall task) break neither. v4 (global direction) was correctly negative.

VERSION LOG (instrument iterations; results/.../run.log, run_v2.log)
  v1 @bc1d242: full projections at wildly unmatched removed energy -> recall
    control fired (x38/x14/x26) = dose conflated with identity. Gate worked.
  v2 @f7e07f7: energy ladder ran; caught (a) find_band falsy-zero bug (p=0.0
    layers excluded -> v1/v2 "bands" were accidental sub-bands of the true
    ~L9-L22), (b) bind-axis SVD pick tie-flips between axis0/axis1 at 4B
    (QUANT and DET SPLIT onto different axes at this scale - axis0 = QUANT-vs-
    rest @85% var, DET on axis1 ~5%, MOD clean on axis4; at 32B QUANT+DET
    co-load axis0) -> energies differ x10^4 across the flip -> ladder inverted,
    caps starved bind, (c) e-centroid direction carries ~1e5 E/tok, nothing
    like the pre-reg "near-null" intent, (d) recall RATIO gate over-fires on a
    0.39-nat baseline. Also REPLICATED: Q_eff ~2.8 t>6 but M_eff ~0 at 4B
    (2 grids) - 4B does not express modifier licensing behaviourally.
  v3 (this): (1) find_band p-bug fixed; (2) ROLE SUBSPACES built directly from
    class centroids - bind = orthonormal span{c_QUANT-mean, c_DET-mean} (holds
    both sides of the 4B axis split by construction), comp = span{c_MOD-mean},
    ROLE-NULL = span{c_CONN-mean, c_FUNC-mean} (same lattice, wrong role = the
    sharp class-control; REPLACES the pre-reg e-axis control, whose "near-null"
    intent is unrealizable as a raw centroid direction - deviation documented
    here); (3) budgets = geometric ladder over the MEASURED role-subspace
    energies [min..max]; random = 2D isotropic subspace, uncapped, matched to
    the same budget; (4) recall breakage gate = top-1 ACCURACY drop > 0.2
    (surprisal still logged).

INSTRUMENT
  1. Capture labeled Montague-type dataset at every decoder layer (reuses
     probe_type_qwen3_32b capture; residuals[L] = output of model.layers[L]).
  2. Per layer: standardize (diagonal whiten - the 1a massive-activation
     lesson), centroid SVD, PR + shuffled-label null (band detection + the
     lattice record). BAND = longest contiguous run of p<0.05 layers.
  3. Per band layer: role subspaces from class centroids (std space),
     orthonormalized (QR); full-projection removed energy measured on the
     capture: E_full = mean_tokens ||((z Q^T) Q) * sd||^2.
  4. Zone ablation at every band layer, every position, alpha-scaled:
     h' = h - alpha * (((h-mu)/sd) Q^T Q) * sd ; alpha = sqrt(B/E_full),
     capped at 1.0 for role subspaces (achieved energy logged), uncapped for
     the random subspace (scaled steering = the honest energy-matched null).

BEHAVIOURAL READOUTS (v3-nonce-style surprisal; frequency-free)
  ONE teach pair (noun vs adj) x THREE frames, fully crossed & paired by nonce:
     frame quant: "Every {w}"       (QUANT licenses a NOUN)
     frame mod:   "It was very {w}" (intensifier licenses an ADJ)
     frame name:  "John {w}"        (licenses a PRED; SHARED REFERENCE arm)
  pref(f) = S(f|adj-taught) - S(f|noun-taught)   (per nonce)
  Q_eff = pref(quant) - pref(name) > 0 baseline  (quantifier-class licensing)
  M_eff = pref(name)  - pref(mod)  > 0 baseline  (modifier-class licensing)
  Teach main effects cancel identically via the shared name arm. Recall task =
  non-compositional control (surprisal + top-1 accuracy).

VERDICT (pre-set, frozen before the v3 run; ret = effect/baseline):
  GATE-0: baseline Q_eff and M_eff both mean>0, t>=3 - else no ablation cell is
    interpreted for that class (a Gate-0 failure at 4B is a capacity finding;
    the Q side can still validate the instrument).
  b* = LARGEST budget where recall_acc drops <=0.2 for ALL of
    {bind, comp, rolenull, random}. None -> not interpretable.
  At b*: BIND-SELECTIVE: ret(Q,bind)<0.5 AND ret(M,bind)>0.7
         COMP-SELECTIVE: ret(M,comp)<0.5 AND ret(Q,comp)>0.7
         NULLS: rolenull AND random keep BOTH rets>0.7
  DISSOCIATION_SUPPORTED <=> gate0 & b* & bind & comp & nulls. Verbatim rows
  reported at every budget regardless.

lambda measure: ablation target = value-register lattice subspaces; claim =
reduction LICENSING -> readout is behavioural class-selectivity at MATCHED
dose, never a decodability change. A RUNG: hook-not-weight; one class pair.

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

ROLES = {"bind": ["QUANT", "DET"], "comp": ["MOD"], "rolenull": ["CONN", "FUNC"]}


# ── geometry: band + role subspaces (standardized space) ───────────────────────
def layer_geometry(x: np.ndarray, y: np.ndarray, rng, n_null: int) -> dict:
    """Standardize -> centroid SVD -> PR + shuffled-label null; keep z for energy."""
    mu = x.mean(axis=0)
    sd = x.std(axis=0) + 1e-6
    z = (x - mu) / sd

    def pr_of(labels):
        c, present = centroids(z, labels, TYPE_ORDER)
        if len(present) < 3:
            return float("nan"), None, None
        cc = c - c.mean(axis=0, keepdims=True)
        sv = np.linalg.svd(cc, compute_uv=False)
        return participation_ratio(sv), present, c

    pr_real, present, c = pr_of(y)
    null = []
    for _ in range(n_null):
        prn, _, _ = pr_of(rng.permutation(y))
        if not np.isnan(prn):
            null.append(prn)
    null = np.array(null)
    p = float(np.mean(null <= pr_real)) if null.size else None
    return {"mu": mu, "sd": sd, "z": z, "present": present, "centroids": c,
            "pr_real": float(pr_real), "p_lowrank": p,
            "pr_null_mean": float(null.mean()) if null.size else None}


def find_band(per_layer: dict[int, dict], n_layers: int) -> list[int]:
    """Longest contiguous run of layers with p_lowrank < 0.05 (v3: p=0.0 counts)."""
    def pval(L):
        p = per_layer[L]["p_lowrank"]
        return 1.0 if p is None else p

    sig = [L for L in sorted(per_layer) if pval(L) < 0.05]
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
    lo = min(interior, key=pval)
    return [L for L in sorted(per_layer) if lo - 3 <= L <= lo + 3]


def role_subspace(geo: dict, types: list[str]) -> np.ndarray | None:
    """Orthonormal basis (k, D) of span{c_type - grand_mean} in std space."""
    present = geo["present"]
    idx = {t: i for i, t in enumerate(present)}
    if not all(t in idx for t in types):
        return None
    c = geo["centroids"]
    grand = c.mean(axis=0)
    rows = np.stack([c[idx[t]] - grand for t in types])
    q, _ = np.linalg.qr(rows.T)          # (D, k) orthonormal columns
    return q.T                            # (k, D)


def subspace_energy(z: np.ndarray, sd: np.ndarray, q: np.ndarray) -> float:
    """Full-projection removed energy per token: mean ||((z Q^T) Q) * sd||^2."""
    delta = (z @ q.T) @ q                 # (N, D) std-space removal
    return float(np.mean(np.sum((delta * sd) ** 2, axis=1)))


# ── zone ablation hook (subspace, alpha-scaled, energy-logged) ─────────────────
def make_zone_hook(mu: np.ndarray, sd: np.ndarray, q: np.ndarray,
                   alpha: float, elog: dict):
    """h' = h - alpha * (((h-mu)/sd) Q^T Q) * sd at ALL positions (fp32->cast)."""
    box: dict = {}

    def hook(_module, _inp, out):
        h = out[0] if isinstance(out, tuple) else out
        if not box:
            box["mu"] = torch.as_tensor(mu, dtype=torch.float32, device=h.device)
            box["sd"] = torch.as_tensor(sd, dtype=torch.float32, device=h.device)
            box["q"] = torch.as_tensor(q, dtype=torch.float32, device=h.device)
        hf = h.float()
        zc = (hf - box["mu"]) / box["sd"]
        delta = alpha * ((zc @ box["q"].T) @ box["q"]) * box["sd"]   # [B,T,D]
        hf = hf - delta
        elog["e"] += float((delta ** 2).sum())
        elog["n"] += int(delta.shape[0] * delta.shape[1])
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


def score_pass(items, model, tok, tag: str) -> list[dict | None]:
    """Per item: {'s': mean target surprisal, 'acc': top-1 gold (recall only)}."""
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
        rec = {"s": float(np.mean([-float(logp[j - 1, ids[j]]) for j in tgt]))}
        if it["kind"] == "recall":
            j0 = min(tgt)
            rec["acc"] = float(int(logp[j0 - 1].argmax()) == int(ids[j0]))
        out.append(rec)
        if n % 120 == 0:
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
    for it, r in zip(items, scores, strict=True):
        if it["kind"] != "typed" or r is None:
            continue
        cell.setdefault((it["w"], it["frame"], it["teach_type"]), []).append(r["s"])

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

    rec = [r for it, r in zip(items, scores, strict=True)
           if it["kind"] == "recall" and r is not None]
    return {"Q_eff": agg(q_eff), "M_eff": agg(m_eff),
            "pref": {f: agg(v) for f, v in prefs.items()},
            "recall_surprisal": (round(float(np.mean([r["s"] for r in rec])), 4)
                                 if rec else None),
            "recall_acc": (round(float(np.mean([r["acc"] for r in rec])), 3)
                           if rec else None)}


def retention(eff_abl: dict | None, eff_base: dict | None) -> float | None:
    if not eff_abl or not eff_base or not eff_base.get("mean"):
        return None
    return round(eff_abl["mean"] / eff_base["mean"], 3)


# ── main ───────────────────────────────────────────────────────────────────────
def main() -> None:
    ap = argparse.ArgumentParser(
        description="P-TYPE-1b zone x subspace ablation (v3 role subspaces)")
    ap.add_argument("--model", default="Qwen/Qwen3-4B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-null", type=int, default=100)
    ap.add_argument("--n-nonce", type=int, default=10)
    ap.add_argument("--n-teach", type=int, default=2)
    ap.add_argument("--n-fill", type=int, default=3)
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

    # 2) role subspaces + energies per band layer
    rng_r = np.random.default_rng(args.seed + 7)
    band_info, sub_log = {}, {}
    for L in band:
        g = geo[L]
        subs = {name: role_subspace(g, types) for name, types in ROLES.items()}
        if any(v is None for v in subs.values()):
            continue
        r = rng_r.standard_normal((2, len(g["mu"])))
        qr, _ = np.linalg.qr(r.T)
        subs["random"] = qr.T[:2]
        E = {k: subspace_energy(g["z"], g["sd"], q) for k, q in subs.items()}
        band_info[L] = {"subs": subs, "E": E, "mu": g["mu"], "sd": g["sd"]}
        sub_log[str(L)] = {"E_full": {k: round(v, 1) for k, v in E.items()}}
    print(f"[1b] subspace energies: {json.dumps(sub_log, indent=1)}",
          file=sys.stderr)

    # free capture memory (keep summaries)
    for L in geo:
        geo[L].pop("z", None)
        geo[L].pop("centroids", None)
    del data
    import gc
    gc.collect()

    # 3) budgets: geometric ladder over MEASURED role-subspace energies
    def gmean(vals):
        return float(np.exp(np.mean(np.log(np.maximum(vals, 1e-9)))))

    role_gmeans = {name: gmean([band_info[L]["E"][name] for L in band_info])
                   for name in ROLES}
    e_lo, e_hi = min(role_gmeans.values()), max(role_gmeans.values())
    budgets = [e_lo, float(np.sqrt(e_lo * e_hi)), e_hi]
    print(f"[1b] role gmeans={ {k: round(v, 1) for k, v in role_gmeans.items()} } "
          f"budgets={[round(b, 1) for b in budgets]}", file=sys.stderr)

    # conditions: baseline + {bind, comp, rolenull, random} x budgets
    conds: dict[str, list] = {"baseline": []}
    alpha_log: dict[str, dict] = {}
    for bidx, budget in enumerate(budgets, start=1):
        for name in ("bind", "comp", "rolenull", "random"):
            cname = f"{name}@b{bidx}"
            conds[cname] = []
            alpha_log[cname] = {}
            for L, bi in band_info.items():
                alpha = float(np.sqrt(budget / max(bi["E"][name], 1e-9)))
                if name != "random":
                    alpha = min(alpha, 1.0)   # projection cap; achieved E logged
                conds[cname].append((L, bi["mu"], bi["sd"], bi["subs"][name],
                                     alpha))
                alpha_log[cname][str(L)] = round(alpha, 4)

    # 4) behavioural passes
    items = gen_items(args.n_nonce, args.n_teach, args.n_fill)
    n_typed = sum(1 for i in items if i["kind"] == "typed")
    print(f"[1b] {len(items)} items ({n_typed} typed + {len(RECALL)} recall) "
          f"x {len(conds)} conds", file=sys.stderr)

    results, energy = {}, {}
    for cname, dirset in conds.items():
        handles, elog = [], {"e": 0.0, "n": 0}
        for L, mu, sd, q, alpha in dirset:
            handles.append(layer_mods[L].register_forward_hook(
                make_zone_hook(mu, sd, q, alpha, elog)))
        try:
            scores = score_pass(items, model, tok, cname)
        finally:
            for h in handles:
                h.remove()
        results[cname] = class_effects(items, scores)
        energy[cname] = round(elog["e"] / max(elog["n"], 1), 1)
        r = results[cname]
        print(f"[1b] {cname:12s} Q_eff={r['Q_eff']} M_eff={r['M_eff']} "
              f"recall_acc={r['recall_acc']} E/tok={energy[cname]}",
              file=sys.stderr)

    # 5) verdict (pre-set margins from the docstring)
    base = results["baseline"]
    gate0_q = bool(base["Q_eff"] and base["Q_eff"]["mean"] > 0
                   and base["Q_eff"]["t"] >= 3)
    gate0_m = bool(base["M_eff"] and base["M_eff"]["mean"] > 0
                   and base["M_eff"]["t"] >= 3)
    gate0 = gate0_q and gate0_m
    ret = {c: {"Q": retention(results[c]["Q_eff"], base["Q_eff"]),
               "M": retention(results[c]["M_eff"], base["M_eff"]),
               "recall_acc": results[c]["recall_acc"],
               "E_per_tok": energy[c]}
           for c in conds if c != "baseline"}

    def ok(v, lo=None, hi=None):
        return v is not None and (lo is None or v > lo) and (hi is None or v < hi)

    def recall_ok(c):
        a, b = results[c]["recall_acc"], base["recall_acc"]
        return a is not None and b is not None and (b - a) <= 0.2

    b_star = None
    for bidx in (3, 2, 1):
        if all(recall_ok(f"{n}@b{bidx}")
               for n in ("bind", "comp", "rolenull", "random")):
            b_star = bidx
            break

    bind_sel = comp_sel = nulls_ok = False
    if b_star is not None:
        bb, cc = f"bind@b{b_star}", f"comp@b{b_star}"
        nn, rr = f"rolenull@b{b_star}", f"random@b{b_star}"
        bind_sel = ok(ret[bb]["Q"], hi=0.5) and ok(ret[bb]["M"], lo=0.7)
        comp_sel = ok(ret[cc]["M"], hi=0.5) and ok(ret[cc]["Q"], lo=0.7)
        nulls_ok = all(ok(ret[c][k], lo=0.7) for c in (nn, rr) for k in ("Q", "M"))
    supported = bool(gate0 and b_star is not None
                     and bind_sel and comp_sel and nulls_ok)

    verdict = {
        "register": "P-TYPE-1b zone x subspace ablation v3 (role subspaces)",
        "host": args.model, "is_prereg_host": args.model == "Qwen/Qwen3-32B",
        "band": [int(band[0]), int(band[-1])], "n_band_layers": len(band_info),
        "role_gmeans_E": {k: round(v, 1) for k, v in role_gmeans.items()},
        "budgets_E_per_tok": [round(b, 1) for b in budgets],
        "gate0": {"both": gate0, "Q": gate0_q, "M": gate0_m},
        "baseline": base,
        "conditions": {c: results[c] for c in conds if c != "baseline"},
        "retention": ret,
        "b_star_interpretation_budget": b_star,
        "bind_selective": bind_sel, "comp_selective": comp_sel,
        "nulls_clean": nulls_ok,
        "dissociation_supported": supported,
        "alpha_log": alpha_log, "subspace_log": sub_log,
        "per_layer_pr": {str(L): {"pr": round(geo[L]["pr_real"], 3),
                                  "p": geo[L]["p_lowrank"]} for L in sorted(geo)},
        "deviations": ["e-axis control replaced by role-null (CONN/FUNC lattice "
                       "subspace): raw ENTITY-centroid direction carries ~1e5 "
                       "E/tok, unrealizable as the pre-reg near-null (v2 catch)"],
    }

    print("\n" + "=" * 76)
    print("P-TYPE-1b v3 — zone x subspace dissociation, role subspaces")
    print("=" * 76)
    print(f"  host={args.model}  band=L{band[0]}..L{band[-1]}  "
          f"gate0={gate0} (Q={gate0_q} M={gate0_m})  "
          f"budgets={[round(b, 1) for b in budgets]}")
    print(f"  baseline  Q_eff={base['Q_eff']}  M_eff={base['M_eff']}  "
          f"recall_acc={base['recall_acc']}")
    for c in ret:
        print(f"  {c:12s} retQ={ret[c]['Q']}  retM={ret[c]['M']}  "
              f"recall_acc={ret[c]['recall_acc']}  E/tok={ret[c]['E_per_tok']}")
    print(f"  b*={b_star}  bind_selective={bind_sel}  comp_selective={comp_sel}  "
          f"nulls={nulls_ok}")
    print(f"  * dissociation_supported = {supported}")
    print("=" * 76 + "\n")

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
