#!/usr/bin/env python3
"""Kernel-certified argument-kind probes — the §P-TYPE-GRAM-1 generator.

Context (pre-reg FROZEN s313, Michael-approved:
mementum/knowledge/explore/gram-registers-and-the-route-map.md
§P-TYPE-GRAM-1): first direct probe of the S5 central claim (M7 typed
apply) at constructor grain. For each opcode X ∈ {K,I,B,C,S,D,W}, produce
probe sets split by the KIND of the first argument the redex consumes:

  atom — bare variable            ('atom', i)
  fn   — combinator constant      ('c', name)   (the function-valued kind)
  app  — composite application    ('app', f, x) (unevaluated redex/spine)

→ node ``X:t`` (21 nodes max; unpopulatable combos dropped + documented,
whnf:Y precedent).

Method (whnf_probes.py precedent, s284):
  1. Sample random applicative terms (dust_walk generator, Y-downweighted
     arm for diversity with termination).
  2. Reduce with a kind-reporting mirror of the dust_walk kernel step
     (``step_info`` — kernel equivalence asserted in --validate).
  3. At every trace position j≥1 whose NEXT fired rule is X consuming a
     first argument of kind t, render the chain TRUNCATED at that moment:
     "t0 = t1 = ... = tj =" — the model is left HOLDING the redex
     X(arg:t) mid-reduction (fire_formal-style rendering, kind-bucketed).
  4. At most one harvest per (X,t) node per chain (diversity); dedup;
     length cap 220 chars (precedent).

Surface stats (TG5): per-node char-length and paren-count summaries are
recorded in meta so the runner can stratify its shuffle null; the scorer
recomputes per-prompt stats directly from the prompts.

Output: opcodes/data/type_probes.json
  {meta, states: {"K:atom": [prompts...], ..., "W:app": [...]}}

Usage:
    uv run python opcodes/type_probes.py [--n-per-state 60] [--seed 5]
    uv run python opcodes/type_probes.py --validate

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
    ARITY,
    ARMS,
    ATOM,
    MAX_STEPS,
    apply_rule,
    gen_term,
    leaf_probs,
    rebuild,
    size,
    spine,
    step,
)
from whnf_probes import index_atoms, render  # noqa: E402

TYPE_OPS = ["K", "I", "B", "C", "S", "D", "W"]   # Y excluded (pre-reg scope)
KINDS = ["atom", "fn", "app"]
ATOM_NAMES = "abcdefgh"
LEN_CAP = 220


def arg_kind(a) -> str:
    """Constructor-grain kind of a term in argument position."""
    if a == ATOM or a[0] == "atom":
        return "atom"
    if a[0] == "c":
        return "fn"
    return "app"


def step_info(t):
    """Mirror of dust_walk.step() that also reports the fired rule's
    first-argument kind. Returns (new_term, rule | None, kind | None).
    Kernel equivalence with step() is asserted in --validate."""
    if t[0] != "app":
        return t, None, None
    h, args = spine(t)
    if h[0] == "c":
        k = ARITY[h[1]]
        if len(args) >= k:
            res = apply_rule(h[1], args[:k])
            return rebuild(res, args[k:]), h[1], arg_kind(args[0])
    nf, r, kd = step_info(t[1])
    if r:
        return ("app", nf, t[2]), r, kd
    na, r, kd = step_info(t[2])
    if r:
        return ("app", t[1], na), r, kd
    return t, None, None


def chain_info(t0, max_steps: int = MAX_STEPS, size_cap: int = 2000):
    """[(term, rule_to_reach_it, arg0_kind_of_that_rule)...] from t0."""
    seq = [(t0, None, None)]
    t = t0
    for _ in range(max_steps):
        t2, r, kd = step_info(t)
        if r is None:
            return seq, True
        seq.append((t2, r, kd))
        t = t2
        if size(t) > size_cap:
            return seq, False
    return seq, False


def surface_stats(prompts: list[str]) -> dict:
    lens = np.array([len(p) for p in prompts], dtype=float)
    parens = np.array([p.count("(") for p in prompts], dtype=float)
    if len(prompts) == 0:
        return {"n": 0}
    return {"n": len(prompts),
            "len_mean": round(float(lens.mean()), 2),
            "len_median": float(np.median(lens)),
            "paren_mean": round(float(parens.mean()), 2),
            "paren_median": float(np.median(parens))}


def generate(n_per_state: int, seed: int, max_samples: int
             ) -> tuple[dict[str, list[str]], int]:
    rng = np.random.default_rng(seed)
    labels, probs = leaf_probs(ARMS["y-downweighted"])
    sys.setrecursionlimit(100_000)

    nodes = [f"{o}:{t}" for o in TYPE_OPS for t in KINDS]
    states: dict[str, list[str]] = {nd: [] for nd in nodes}
    seen: set[str] = set()

    def done() -> bool:
        return all(len(v) >= n_per_state for v in states.values())

    n_sampled = 0
    while not done() and n_sampled < max_samples:
        n_sampled += 1
        n = int(rng.integers(3, 10))
        t0 = index_atoms(gen_term(n, rng, labels, probs), [0])
        seq, _halted = chain_info(t0)
        if len(seq) < 3:                      # need j>=1 with a next step
            continue
        atoms = {i: ATOM_NAMES[i % len(ATOM_NAMES)] for i in range(20)}
        steps_txt = [render(term, atoms) for term, _, _ in seq]
        used_this_chain: set[str] = set()
        # trace position j holds seq[j]; the step j -> j+1 fires
        # rule seq[j+1][1] on a first argument of kind seq[j+1][2]
        for j in range(1, len(seq) - 1):
            x, kd = seq[j + 1][1], seq[j + 1][2]
            nd = f"{x}:{kd}"
            if nd not in states or nd in used_this_chain:
                continue
            if len(states[nd]) >= n_per_state:
                continue
            p = " = ".join(steps_txt[: j + 1]) + " ="
            if p in seen or len(p) >= LEN_CAP:
                continue
            seen.add(p)
            states[nd].append(p)
            used_this_chain.add(nd)
    return states, n_sampled


# ── validate ─────────────────────────────────────────────────────────────────
def validate() -> int:
    n_fail = 0

    def check(name: str, ok: bool, detail: str = "") -> None:
        nonlocal n_fail
        mark = "PASS" if ok else "FAIL"
        if not ok:
            n_fail += 1
        print(f"[validate] {mark} {name} {detail}", file=sys.stderr)

    c = lambda nm: ("c", nm)  # noqa: E731
    a0, a1 = ("atom", 0), ("atom", 1)
    A = lambda f, x: ("app", f, x)  # noqa: E731

    # 1. planted kind classification, redex at top
    planted = [
        (A(A(c("K"), a0), a1), "K", "atom"),
        (A(A(c("K"), c("I")), a1), "K", "fn"),
        (A(A(c("K"), A(a0, a1)), a1), "K", "app"),
        (A(c("I"), a0), "I", "atom"),
        (A(c("I"), c("W")), "I", "fn"),
        (A(c("I"), A(a0, a1)), "I", "app"),
        (A(A(A(c("B"), A(a0, a1)), a0), a1), "B", "app"),
        (A(A(c("W"), c("S")), a0), "W", "fn"),
    ]
    for t, want_r, want_k in planted:
        _, r, kd = step_info(t)
        check(f"planted {want_r}:{want_k}", r == want_r and kd == want_k,
              f"got {r}:{kd}")

    # 2. planted nested redex (fired inside an argument, head is an atom)
    t_nested = A(a0, A(A(c("K"), c("B")), a1))
    _, r, kd = step_info(t_nested)
    check("planted nested K:fn", r == "K" and kd == "fn", f"got {r}:{kd}")

    # 3. kernel equivalence: step_info ≡ step on random full chains
    rng = np.random.default_rng(0)
    labels, probs = leaf_probs(ARMS["y-downweighted"])
    mismatch = 0
    n_terms, n_steps_checked = 400, 0
    for _ in range(n_terms):
        t = index_atoms(gen_term(int(rng.integers(3, 10)), rng, labels,
                                 probs), [0])
        for _ in range(MAX_STEPS):
            t_a, r_a = step(t)
            t_b, r_b, _kd = step_info(t)
            n_steps_checked += 1
            if t_a != t_b or r_a != r_b:
                mismatch += 1
                break
            if r_a is None or size(t_a) > 2000:
                break
            t = t_a
    check("kernel equivalence step_info==step", mismatch == 0,
          f"{n_steps_checked} steps, {mismatch} mismatches")

    # 4. tiny generation: balance + rendering invariants
    states, n_sampled = generate(n_per_state=5, seed=1, max_samples=60_000)
    counts = {nd: len(v) for nd, v in states.items()}
    populated = [nd for nd, n in counts.items() if n >= 5]
    check("tiny-gen populates >= 18/21 nodes", len(populated) >= 18,
          f"{len(populated)}/21 populated ({n_sampled} sampled); "
          f"short={ {nd: n for nd, n in counts.items() if n < 5} }")
    all_prompts = [p for v in states.values() for p in v]
    check("prompts end mid-reduction ' ='",
          all(p.endswith(" =") for p in all_prompts))
    check("prompts under length cap",
          all(len(p) < LEN_CAP for p in all_prompts))
    check("prompts unique", len(all_prompts) == len(set(all_prompts)))
    check("prompts contain >=2 shown terms",
          all(p.count(" = ") >= 1 for p in all_prompts))

    # 5. surface stats computable (TG5 substrate)
    ss = {nd: surface_stats(v) for nd, v in states.items() if v}
    check("surface stats computable", all("len_mean" in s for s in
                                          ss.values()))

    print(f"[validate] {'ALL PASS' if n_fail == 0 else f'{n_fail} FAILURES'}",
          file=sys.stderr)
    return n_fail


def main() -> None:
    ap = argparse.ArgumentParser(description="X:kind probe generator "
                                             "(§P-TYPE-GRAM-1)")
    ap.add_argument("--n-per-state", type=int, default=60)
    ap.add_argument("--seed", type=int, default=5)
    ap.add_argument("--max-samples", type=int, default=2_000_000)
    ap.add_argument("--output", default=str(_HERE / "data" /
                                            "type_probes.json"))
    ap.add_argument("--validate", action="store_true")
    args = ap.parse_args()

    if args.validate:
        sys.exit(1 if validate() else 0)

    states, n_sampled = generate(args.n_per_state, args.seed,
                                 args.max_samples)

    short = {k: len(v) for k, v in states.items() if len(v) <
             args.n_per_state}
    for k, v in sorted(states.items()):
        print(f"[type-probes] {k:8s} {len(v)}", file=sys.stderr)
    if short:
        print(f"[type-probes] WARNING short states: {short}", file=sys.stderr)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps({
        "meta": {"generator": "opcodes/type_probes.py",
                 "timestamp_utc": datetime.now(UTC).isoformat(),
                 "seed": args.seed, "n_per_state": args.n_per_state,
                 "n_sampled": n_sampled,
                 "ensemble": "y-downweighted leaf distribution (ARMS)",
                 "prereg": "§P-TYPE-GRAM-1 (gram-registers-and-the-route-"
                           "map.md, frozen s313)",
                 "kinds": KINDS, "ops": TYPE_OPS,
                 "short_states": short,
                 "surface_stats": {k: surface_stats(v)
                                   for k, v in sorted(states.items())},
                 "note": ("X:t = kernel-certified chains truncated at the "
                          "moment X fires on a first argument of kind t "
                          "(model left holding the redex, fire_formal-style "
                          "rendering); at most one harvest per node per "
                          "chain; kinds: atom=bare variable, fn=combinator "
                          "constant, app=composite application")},
        "states": states}, indent=1))
    print(f"[type-probes] wrote {out}", file=sys.stderr)


if __name__ == "__main__":
    main()
