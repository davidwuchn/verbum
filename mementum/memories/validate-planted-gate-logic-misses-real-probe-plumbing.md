❌ `--validate` on planted/synthetic gate worlds proves the VERDICT LOGIC but NOT
the instrument's plumbing on the REAL probe set — two different things.

s331: `subst_engine.py --validate` was ALL-PASS (all five verdicts forced on
planted `compute_gates` records), yet the first live smoke on Qwen3-14B gave
`acc_ctrl=0.000`. Not a model failure — `make_candidates` couldn't build 3
distinct forced-choice options for atom / closed-lambda normal forms (e.g. `a`,
`λx.x`), so every control was silently DROPPED (`cand is None → continue`), not
mis-scored, and SE0 never ran. The planted worlds fed synthetic correctness
records straight to the gates; they never exercised candidate construction on the
actual battery.

Fix: a validate primitive that runs the REAL plumbing (`make_candidates` over
every `build_battery` item → all triple-option), PLUS smoke on real weights
before trusting a run. Rule: validate must cover BOTH the pure gate logic AND the
instrument applied to the real probes; the on-weights smoke is the catch a
planted world structurally cannot be.

Sibling: linearity_bias instrument-amendment-at-build; capture-euphoria guard
(post-GO audit disk before believing a number).
