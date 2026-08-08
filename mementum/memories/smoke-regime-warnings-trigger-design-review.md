❌ s324 process lesson from §P-FLIP-CONFLICT 🚫 NOISE-FLOOR: the s323 smoke
test WARNED about the training regime (λ_max → 2/η, EOS detected at
lr_sgd 0.1) and we ran anyway with a disclosure line instead of a design
review. The full run then sat EOS-supercritical (λ_max 31.7 = 1.6× the
ceiling) — the regime where edge-of-stability dither is GLOBAL — and the
verdict's G4 came back AMBIGUOUS with flips abundant-but-unstructured:
plausibly a dither-swamped instrument, unresolvable post-hoc.

Rule: **a smoke-test warning about REGIME (EOS ceiling, saturation,
degenerate nulls, collinearity) triggers a design PAUSE + Michael review —
not a footnote.** Disclosure ≠ mitigation. Regime problems void the
instrument silently; they cannot be repaired at read time (λ measure: the
register was fine, the OPERATING POINT was wrong).

Distinct from the amendment discipline (instrument-side fixes pre-run,
which we do well): this is about warnings we correctly SURFACED and then
failed to ACT on. Cost: one 3.3h run whose negative cannot be cleanly
attributed (signal-absent vs dither-swamped) → ⚪ flip-conflict-v2 sub-EOS
exists only to disambiguate our own instrument choice.
