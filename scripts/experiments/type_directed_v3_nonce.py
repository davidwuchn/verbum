#!/usr/bin/env python3
# register: TYPE-DIRECTEDNESS — nonce frequency-free crossover (v3, the decisive test)
"""Type-vs-position dissociation, v3 — the FREQUENCY-FREE nonce crossover.

v1/v2 showed a ROBUST behavioural type effect (a verb is cheap after a subject-NP,
dear after a non-subject; consistency 1.0) — but with real words "type-licensed"
confounds with bigram-FREQUENCY/grammaticality, and the forward arm was unmeasurable
(universal-donor targets). This kills the frequency confound: NONCE words have NO
bigram statistics, so any composition preference is the IN-CONTEXT TYPE directing it.

THE DESIGN — a CROSSOVER INTERACTION (subtracts every main effect, incl. priming):
  Teach a nonce word's TYPE in-context, then test it in two frames:
    TEACH noun:  "{W}s are common objects."   (plural -> count noun)
    TEACH verb:  "They often {w}."            (bare/infinitive -> verb)
    TEST det:    "The {w}"   det licenses a NOUN  -> cheap if NOUN-taught
    TEST name:   "John {w}"  name licenses a PRED -> cheap if VERB-taught
  full = "{teach}. {filler} {w}"  ; measure surprisal of the final nonce token.

  det_pen(w)  = S(det, verb-taught)  - S(det, noun-taught)     ( >0 if typed )
  name_pen(w) = S(name, verb-taught) - S(name, noun-taught)    ( <0 if typed )
  CROSSOVER(w) = det_pen(w) - name_pen(w)  (paired by nonce word; >>0 if type-directed)

  A crossover (the cheaper TEACHING flips with the FRAME) CANNOT come from frequency
  or a teach/prime/frame main effect — ONLY the taught TYPE interacting with the
  frame's type-requirement. Nonce -> frequency-free. This is the decisive type-directed
  composition signal (and the clean dissociation the v2 forward arm could not give).

VERDICT (lambda measure): CROSSOVER >0 sig + det_pen>0 + name_pen<0 -> composition is
  TYPE-directed, frequency-free; the in-context type DIRECTS composition; the s236-s240
  order signal is type, not L-to-R position; the VERBUM thesis holds at the behavioural
  level. CROSSOVER ~0 -> the v1/v2 effect was (partly) frequency; type does not direct
  composition in-context (at this scale) -> needs the causal-ablation register (v4).

CAVEATS (lambda measure): in-context type teaching tests CAPACITY to use a given type,
  not only the intrinsic system; the nonce appears in BOTH teach+test (repetition/
  induction — but the crossover subtracts it as a main effect); teaching templates may
  imperfectly fix the category; single model class. Nonce tokenization logged (sanity).

Usage:
    uv run python scripts/experiments/type_directed_v3_nonce.py --smoke   # 8B
    uv run python scripts/experiments/type_directed_v3_nonce.py           # 14B

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

RESULTS_DIR = _ROOT / "results" / "type-directed"

# nonce words (no real-word meaning; pronounceable) — tokenization logged at runtime
NONCE = ["wug", "blicket", "dax", "fep", "gorp", "zorp", "fendle", "glorp",
         "narp", "trisk", "florp", "queel", "vimp", "dorf", "snarl", "plong"]

# TEACH templates ({w}=lowercase, {W}=capitalised). No "the {w}"/"a {w}" -> no det leak.
NOUN_TEACH = ["{W}s are common objects.", "He collected several {w}s.",
              "Those {w}s are nice.", "Many {w}s were there."]
VERB_TEACH = ["They often {w}.", "We like to {w}.", "You should {w} now.",
              "Children love to {w}."]
# TEST fillers (sentence-initial): determiners (want a NOUN) vs names (want a PRED)
DET_FILL = ["The", "This", "That", "Each", "Every", "Some"]
NAME_FILL = ["John", "Mary", "Sarah", "David", "Peter", "Susan"]


def build_text(teach_tpl: str, w: str, filler: str) -> tuple[str, int]:
    """Return (full_text, char_start_of_target). full = '{teach}. {filler} {w}'."""
    teach = teach_tpl.format(w=w, W=w.capitalize())
    prefix = f"{teach} {filler} "
    return prefix + w, len(prefix)


def gen_items(n_each: int, seed: int):
    rng = np.random.default_rng(seed)
    items = []

    def pick(pool, k):
        idx = rng.choice(len(pool), size=min(k, len(pool)), replace=False)
        return [pool[i] for i in idx]

    for w in NONCE:
        for typ, teaches in (("noun", NOUN_TEACH), ("verb", VERB_TEACH)):
            for teach in teaches:
                for frame, fills in (("det", DET_FILL), ("name", NAME_FILL)):
                    for filler in pick(fills, n_each):
                        items.append({"w": w, "type": typ, "frame": frame,
                                      "teach": teach, "filler": filler,
                                      "cond": f"{frame}_{typ}"})
    rng.shuffle(items)
    return items


def score_item(item, model, tok, torch_mod):
    text, c0 = build_text(item["teach"], item["w"], item["filler"])
    c1 = len(text)
    enc = tok(text, return_tensors="pt", return_offsets_mapping=True)
    dev = next(model.parameters()).device
    ids = enc["input_ids"][0]
    offsets = enc["offset_mapping"][0].tolist()
    import torch.nn.functional as func
    with torch_mod.no_grad():
        logits = model(input_ids=ids.unsqueeze(0).to(dev),
                       attention_mask=enc["attention_mask"].to(dev)).logits[0]
    logp = func.log_softmax(logits.float(), dim=-1).cpu()
    ids_cpu = ids.cpu()
    nlls = []
    for j in range(1, ids_cpu.shape[0]):
        s, e = offsets[j]
        if e > s and s < c1 and e > c0:  # overlap with the final nonce token(s)
            nlls.append(-float(logp[j - 1, ids_cpu[j]]))
    return float(np.mean(nlls)) if nlls else None


def _paired(a_by_w, b_by_w):
    """mean(a - b) paired by nonce word, with t and consistency."""
    d = []
    for w, av in a_by_w.items():
        bv = b_by_w.get(w)
        if av and bv:
            d.append(float(np.mean(av) - np.mean(bv)))
    if len(d) < 2:
        return None
    arr = np.array(d)
    se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
    return {"mean": round(float(arr.mean()), 4),
            "t": round(float(arr.mean() / se) if se > 0 else 0.0, 3),
            "n": len(d), "consistency": round(float(np.mean(arr > 0)), 3),
            "per_w": {w: round(v, 3) for w, v in zip(a_by_w, d, strict=False)}}


def main() -> None:
    ap = argparse.ArgumentParser(description="Type-directedness nonce crossover (v3)")
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--n-each", type=int, default=4, help="fillers per cell")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    model_name = args.model
    n_each = args.n_each
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-8B"
        n_each = 3
        print("[type-dir3] SMOKE MODE (Qwen3-8B)")

    items = gen_items(n_each, args.seed)
    print(f"[type-dir3] {len(items)} items (n_each={n_each}, {len(NONCE)} nonce)")
    for ex in ("They often wug. John wug", "Wugs are common objects. The wug"):
        print(f"[type-dir3]   example: {ex!r}")

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    # sanity: how does each nonce tokenize (as ' wug')?
    for w in NONCE[:6]:
        ntok = len(tok(" " + w, add_special_tokens=False)["input_ids"])
        print(f"[type-dir3]   nonce {w!r} -> {ntok} token(s)")

    # cond -> nonce -> [surprisal]
    by_cond: dict[str, dict[str, list]] = defaultdict(lambda: defaultdict(list))
    cond_all: dict[str, list] = defaultdict(list)
    for i, it in enumerate(items):
        if i % 80 == 0:
            print(f"[type-dir3]   scoring {i}/{len(items)} ...")
        s = score_item(it, model, tok, torch_mod)
        if s is None:
            continue
        by_cond[it["cond"]][it["w"]].append(s)
        cond_all[it["cond"]].append(s)

    means = {c: round(float(np.mean(v)), 4) for c, v in sorted(cond_all.items())}
    # det_pen = S(det,verb) - S(det,noun) ; name_pen = S(name,verb) - S(name,noun)
    det_pen = _paired(by_cond["det_verb"], by_cond["det_noun"])
    name_pen = _paired(by_cond["name_verb"], by_cond["name_noun"])
    crossover = None
    if det_pen and name_pen:
        # paired crossover per nonce word
        d = []
        for w in by_cond["det_verb"]:
            cells = [by_cond[c].get(w) for c in
                     ("det_verb", "det_noun", "name_verb", "name_noun")]
            if all(cells):
                dv, dn, nv, nn = (float(np.mean(c)) for c in cells)
                d.append((dv - dn) - (nv - nn))
        if len(d) >= 2:
            arr = np.array(d)
            se = float(arr.std(ddof=1) / np.sqrt(len(arr)))
            tval = float(arr.mean() / se) if se > 0 else 0.0
            crossover = {"mean": round(float(arr.mean()), 4), "t": round(tval, 3),
                         "n": len(d), "consistency": round(float(np.mean(arr > 0)), 3),
                         "significant": bool(abs(tval) > 2.0)}

    type_directed = bool(
        crossover and crossover["significant"] and crossover["mean"] > 0
        and det_pen and det_pen["mean"] > 0
        and name_pen and name_pen["mean"] < 0)
    verdict = {"register": "type-directedness nonce crossover (frequency-free)",
               "condition_mean_surprisal": means,
               "det_penalty_verb_minus_noun": det_pen,
               "name_penalty_verb_minus_noun": name_pen,
               "crossover_interaction": crossover,
               "type_directed": type_directed, "n_items": len(items)}

    print("\n" + "=" * 70)
    print("TYPE-DIRECTEDNESS v3 (nonce, frequency-free) — TYPE or POSITION?")
    print("=" * 70)
    print(f"  {'condition':<14}{'mean surprisal':>16}   (lower = better fit)")
    for c in ("det_noun", "det_verb", "name_noun", "name_verb"):
        print(f"  {c:<14}{means.get(c, float('nan')):>16}")
    if det_pen:
        print(f"\n  det_pen  (verb-noun | The {{w}}):  {det_pen['mean']:>8}  "
              f"t={det_pen['t']:>7}  (>0 => det wants NOUN, verb-taught dear)")
    if name_pen:
        print(f"  name_pen (verb-noun | John {{w}}): {name_pen['mean']:>8}  "
              f"t={name_pen['t']:>7}  (<0 => name wants PRED, verb-taught cheap)")
    if crossover:
        sig = "OK" if crossover["significant"] else "  "
        print(f"\n  * CROSSOVER = det_pen - name_pen = {crossover['mean']}  "
              f"t={crossover['t']}  n={crossover['n']}  "
              f"consist={crossover['consistency']}  {sig}")
    print(f"  * type_directed (frequency-free) = {type_directed}")
    print("=" * 70 + "\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    (RESULTS_DIR / f"type_directed_v3_nonce_verdict_{slug}.json").write_text(
        json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
    meta = {"model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),
            "timestamp_utc": datetime.now(UTC).isoformat(),
            "transformers_version": _transformers_version(),
            "n_each": n_each, "n_items": len(items), "seed": args.seed}
    (RESULTS_DIR / f"type_directed_v3_nonce_meta_{slug}.json").write_text(
        json.dumps(meta, indent=2), encoding="utf-8")
    print(f"[type-dir3] wrote {RESULTS_DIR}/type_directed_v3_nonce_verdict_{slug}.json")


if __name__ == "__main__":
    main()
