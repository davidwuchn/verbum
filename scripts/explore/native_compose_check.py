#!/usr/bin/env python3
"""Cheap native-composition check (s294) — is the landmark->capital JOIN already
in the weights, and if so does it fire ONE-SHOT or only via the TAPE?

Decides the rung-3 direction after 3a LINKER-FAILS (Michael: "the second hop may
only work if we can backprop it into the weights"). Three conditions per
shortcut-free landmark (city != capital, so the answer is genuinely 2-hop):

  direct   : one-shot, NO chain given  -> does the join fire in one illumination?
  cot      : the model writes its own chain onto the tape (RoPE-addressed)
  scaffold : the intermediate country is HANDED to it (control = resident
             country->capital map; should always work)

Readout = does the correct CAPITAL string appear in a greedy generation
(behavior register). Also records whether the intermediate COUNTRY appears.

Interpretation:
  direct works                 -> join exists one-shot (GD wrote it) => extract/trigger
  direct fails, cot works      -> join address-free, needs tape => compile (backprop)
  direct+cot fail, scaffold ok -> join genuinely absent => must be trained outright
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_HERE = Path(__file__).resolve().parent
if str(_HERE) not in sys.path:
    sys.path.insert(0, str(_HERE))
_WRAP = _HERE.parents[1] / "wrapper"
if str(_WRAP) not in sys.path:
    sys.path.insert(0, str(_WRAP))

from fn_stack import COUNTRY_CAP  # noqa: E402


def norm(s: str) -> str:
    return s.lower().strip()


def contains(text: str, target: str) -> bool:
    """Whole-target substring match (case-insensitive); first token also ok."""
    t, tg = norm(text), norm(target)
    return tg in t or norm(target.split()[0]) in t.split()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model-id", default="Qwen/Qwen3-32B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--dtype", default="bfloat16")
    ap.add_argument("--out", default="results/native-compose/qwen3-32b")
    args = ap.parse_args()

    import operand_multihop3 as mh3
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    dev = (args.device if (args.device != "mps" or torch.backends.mps.is_available())
           else "cpu")
    tok = AutoTokenizer.from_pretrained(args.model_id)
    model = AutoModelForCausalLM.from_pretrained(
        args.model_id, dtype=getattr(torch, args.dtype)).to(dev).eval()

    # shortcut-free cells (city != capital), same filter as bake_stack
    cells = []
    for lm in mh3.LM_LIST:
        c = mh3.COUNTRY_OF[lm]
        if c in COUNTRY_CAP and mh3.CITY_OF[lm] != COUNTRY_CAP[c]:
            cells.append(lm)
    print(f"[nc] {args.model_id} dev={dev} cells={len(cells)}")

    def gen(prompt: str, n: int) -> str:
        ids = tok(prompt, return_tensors="pt").to(dev)
        with torch.no_grad():
            out = model.generate(**ids, max_new_tokens=n, do_sample=False,
                                  pad_token_id=tok.eos_token_id)
        return tok.decode(out[0, ids.input_ids.shape[1]:], skip_special_tokens=True)

    conds = {
        "direct": (lambda lm: f"The {lm} is a famous landmark. The capital of the "
                              f"country where it is located is", 10),
        "cot": (lambda lm: f"Question: What is the capital of the country where "
                           f"the {lm} is located?\nAnswer: Let's reason step by "
                           f"step.", 80),
        "scaffold": (lambda lm: f"The {lm} is located in {mh3.COUNTRY_OF[lm]}. "
                                f"The capital of {mh3.COUNTRY_OF[lm]} is", 10),
    }

    rows, tally = [], {k: {"cap": 0, "country": 0} for k in conds}
    hdr = f"{'landmark':<16}{'truth':<12}{'direct':<8}{'cot':<8}{'scaffold':<9}"
    print(hdr)
    print("-" * len(hdr))
    for lm in cells:
        cap = COUNTRY_CAP[mh3.COUNTRY_OF[lm]]
        country = mh3.COUNTRY_OF[lm]
        rec = {"landmark": lm, "country": country, "capital": cap,
               "city": mh3.CITY_OF[lm]}
        marks = {}
        for k, (mk, n) in conds.items():
            g = gen(mk(lm), n)
            cap_hit = contains(g, cap)
            country_hit = contains(g, country)
            rec[k] = {"gen": g, "cap_hit": cap_hit, "country_hit": country_hit}
            tally[k]["cap"] += int(cap_hit)
            tally[k]["country"] += int(country_hit)
            marks[k] = "C" if cap_hit else ("~" if country_hit else ".")
        rows.append(rec)
        print(f"{lm:<16}{cap.split()[0]:<12}{marks['direct']:<8}"
              f"{marks['cot']:<8}{marks['scaffold']:<9}")

    n = len(cells)
    print(f"\n── capital-hit rate (n={n}): "
          + " | ".join(f"{k} {tally[k]['cap']}/{n}" for k in conds))
    print("   (C=capital in gen, ~=only country/intermediate, .=neither)")
    print("── INTERPRETATION ──")
    d, ct, sf = (tally['direct']['cap'], tally['cot']['cap'], tally['scaffold']['cap'])
    if d >= 0.6 * n:
        print("  direct fires -> join EXISTS one-shot (GD wrote it) => extract/trigger")
    elif ct >= 0.6 * n:
        print("  direct fails, cot fires -> join ADDRESS-FREE, needs the tape "
              "=> compile via backprop")
    elif sf >= 0.6 * n:
        print("  only scaffold fires -> join ABSENT (chain not composed even on "
              "tape) => must train outright")
    else:
        print("  even scaffold weak -> readout/measurement issue, inspect gens")

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    (out / "native_compose.json").write_text(
        json.dumps({"model_id": args.model_id, "n_cells": n, "tally": tally,
                    "cells": rows}, indent=2))
    print(f"[nc] wrote {out}/native_compose.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
