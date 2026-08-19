💡 §P-SCHEDULE-READ arm A (s343, zero model load, re-analysis of the committed
CMR route grams, 10 models): the s342 universal+stationary route-Gram frame (the
"station map") carries a **universal STATIC per-direction emphasis ladder** but
**NO universal depth-timetable**. Verdict MODEL-SPECIFIC (a-priori 20).

The trap: per-model schedules look ~96% mutually similar (U=0.894, mean off-diag
corr 0.870, median R²-to-shared-template 0.965) — but matched-range REPRODUCES
that (p=0.263) because the shared part is 99.3% static LEVEL, 0.7% depth-variation.
The cross-model template is a monotone emphasis ladder
[0.006,0.66,0.73,0.80,0.90,0.96,1.05,1.60]; each direction barely moves with depth.
Shared timetable is sub-floor (beats shuffled-layer p=0 but Δ+0.025 < 0.05 floor).
Model-specific residual has NO family structure (within 0.971 ≈ across 0.974) →
idiosyncratic/noise, not a learned lineage signature.

READING: the only universal thing about the schedule is a static intensional
brightness-ladder = part of the station map, not a moving train. No universal
dynamic trains. Reinforces the "static map, not trains" reframe half at the
schedule sub-object (complements tape-residency: value s317 · magnitude s335 ·
routing s336 · operator s339 · residual-vs-W_down s341).

METHOD BANKED: to test "is the schedule shared or trivial," decompose shared
LEVEL vs depth-TIMETABLE energy AND gate with BOTH shuffled-layer (shape-vs-level)
and matched-range (range-floor) — high raw cross-model corr can be entirely a
shared per-direction level ladder that both nulls reproduce. High U ≠ shared trains.

Harness scripts/experiments/schedule_read.py (FTO-clean, reuses verbum.joint_diag,
--validate 4/4 incl LEVEL-ONLY guard). Results p_schedule_read_s343 (meta.json;
npz gitignored). Successor: §P-SCHEDULE-READ-C = faithful co-extensional test
across ALL registers (Michael).
