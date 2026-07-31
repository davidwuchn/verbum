#!/usr/bin/env python3
"""Kernel-certified per-opcode halt probes — the anti-crystal probe generator.

Context: the 9x9 root.gram collapses the statechart's per-opcode absorbing
states into ONE generic WHNF node (vsm.py declares fire:/whnf: vocabulary but
nothing populates it; the 16x16 Zone-B anti-crystal was a different arc, 4
models, no S). This generator produces the missing probe sets by CONSTRUCTION:
programs whose final reduction step is X, rendered as completed reduction
chains -> ground-truth whnf:X prompts (s284, Michael-approved expansion).

Method
  1. Sample random applicative terms (dust_walk generator, Y-downweighted arm
     distribution for diversity with termination).
  2. Reduce with the dust_walk tracing reducer (kernel-equivalence-gated).
  3. Bucket by FINAL fired rule X (the step that produced the normal form);
     require chain length >= 2 fired steps (a genuine completed computation).
  4. Render as an equational chain ENDING at the normal form:
     "C f a b = f b a"-style, steps joined by " = "; the prompt leaves the
     model AT REST after an X-reduction = the whnf:X state.
  5. Style-matched fire:X probes from the SAME programs: chain truncated
     before the final step, ending with " = " (mid-reduction) — the
     style-confound diagnostic (formal-vs-prose could otherwise drive the
     fire<->whnf cross-block).

Y HAS NO HALT STATE (finding, by construction): no terminating trace ends via
Y (Y f -> f (Y f) always continues; Y-containing programs halt via K-discard
or diverge). whnf:Y is therefore UNPOPULATABLE by kernel certification.
Exploratory substitute: div:Y = truncated Y-expansion chains (divergence,
bottom) — rendered mid-loop, tagged separately, never conflated with halt.

Output: opcodes/data/whnf_probes.json
  {meta, states: {"whnf:K": [prompts...], ..., "div:Y": [...],
                  "fire_formal:K": [...], ...}}

Usage:
    uv run python opcodes/whnf_probes.py [--n-per-state 60] [--seed 3]

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(_HERE))

from dust_walk import (  # noqa: E402
    ARMS,
    ATOM,
    MAX_STEPS,
    OPS,
    gen_term,
    leaf_probs,
    size,
    step,
)

HALT_OPS = ["K", "I", "B", "C", "S", "D", "W"]      # Y excluded: no halt state
ATOM_NAMES = "abcdefgh"


def render(t, atoms: dict, top: bool = True) -> str:
    """Compact combinator-expression rendering: application left-assoc,
    parens only around composite arguments."""
    if t == ATOM:
        raise ValueError("use indexed atoms")
    if t[0] == "atom":
        return atoms[t[1]]
    if t[0] == "c":
        return t[1]
    f, x = t[1], t[2]
    fs = render(f, atoms, top=False) if f[0] == "app" else render(f, atoms)
    xs = render(x, atoms)
    if x[0] == "app":
        xs = f"({xs})"
    return f"{fs} {xs}"


def index_atoms(t, counter: list) -> tuple:
    """Give each atom leaf a stable index (left-to-right) for naming."""
    if t == ATOM:
        i = counter[0]
        counter[0] += 1
        return ("atom", i)
    if t[0] == "app":
        return ("app", index_atoms(t[1], counter), index_atoms(t[2], counter))
    return t


def chain(t0, max_steps: int = MAX_STEPS, size_cap: int = 2000):
    """[(term, rule_fired_to_reach_it)...] from t0 to WHNF, cap, or blowup."""
    seq = [(t0, None)]
    t = t0
    for _ in range(max_steps):
        t2, r = step(t)
        if r is None:
            return seq, True
        seq.append((t2, r))
        t = t2
        if size(t) > size_cap:
            return seq, False
    return seq, False


def main() -> None:
    ap = argparse.ArgumentParser(description="whnf:X probe generator")
    ap.add_argument("--n-per-state", type=int, default=60)
    ap.add_argument("--seed", type=int, default=3)
    ap.add_argument("--max-samples", type=int, default=2_000_000)
    ap.add_argument("--output", default=str(_HERE / "data" / "whnf_probes.json"))
    args = ap.parse_args()

    rng = np.random.default_rng(args.seed)
    labels, probs = leaf_probs(ARMS["y-downweighted"])
    sys.setrecursionlimit(100_000)

    whnf: dict[str, list[str]] = {o: [] for o in HALT_OPS}
    fire: dict[str, list[str]] = {o: [] for o in OPS}
    seen: set[str] = set()
    need = args.n_per_state

    def done() -> bool:
        return (all(len(whnf[o]) >= need for o in HALT_OPS)
                and all(len(fire[o]) >= need for o in OPS))

    n_sampled = 0
    while not done() and n_sampled < args.max_samples:
        n_sampled += 1
        n = int(rng.integers(3, 10))
        t0 = index_atoms(gen_term(n, rng, labels, probs), [0])
        seq, halted = chain(t0)
        rules = [r for _, r in seq[1:]]
        if len(rules) < 2:
            continue
        atoms = {i: ATOM_NAMES[i % len(ATOM_NAMES)] for i in range(20)}
        if halted:
            steps_txt = [render(term, atoms) for term, _ in seq]
            x = rules[-1]
            if x in whnf and len(whnf[x]) < need:
                p = " = ".join(steps_txt)
                if p not in seen and len(p) < 220:
                    seen.add(p)
                    whnf[x].append(p)
            # style-matched fire probe for the final op: truncate before it
            if x in fire and len(fire[x]) < need:
                p = " = ".join(steps_txt[:-1]) + " ="
                if p not in seen and len(p) < 220:
                    seen.add(p)
                    fire[x].append(p)
        elif "Y" in rules and len(fire["Y"]) < need:
            # divergent Y-loop: mid-expansion prefix = div:Y / fire:Y material
            steps_txt = [render(term, atoms) for term, _ in seq[:4]]
            p = " = ".join(steps_txt) + " ="
            if p not in seen and len(p) < 220:
                seen.add(p)
                fire["Y"].append(p)

    div_y = fire.pop("Y")
    states = {f"whnf:{o}": v for o, v in whnf.items()}
    states["div:Y"] = div_y
    states.update({f"fire_formal:{o}": v for o, v in fire.items()})

    short = {k: len(v) for k, v in states.items() if len(v) < need}
    for k, v in states.items():
        print(f"[whnf-probes] {k:16s} {len(v)}", file=sys.stderr)
    if short:
        print(f"[whnf-probes] WARNING short states: {short}", file=sys.stderr)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "meta": {"generator": "opcodes/whnf_probes.py",
                 "timestamp_utc": datetime.now(UTC).isoformat(),
                 "seed": args.seed, "n_per_state": need,
                 "n_sampled": n_sampled,
                 "ensemble": "y-downweighted leaf distribution (ARMS)",
                 "y_has_no_halt_state": True,
                 "note": ("whnf:X = kernel-certified completed chains ending "
                          "via X; fire_formal:X = same programs truncated "
                          "mid-final-step (style-confound diagnostic); "
                          "div:Y = truncated Y-expansion (bottom, not halt)")},
        "states": states}, indent=1))
    print(f"[whnf-probes] wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
