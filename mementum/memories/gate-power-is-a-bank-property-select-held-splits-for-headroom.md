💡🔁 A permutation gate on a held split has POWER only where the base model is
WRONG (headroom). If base competence is high on a split, the treatment can't flip
enough cells → p stays >α even when the effect is huge. Cost s311 THREE wire-2 bake
cycles: gd_cd hit 1.0 on every split all three times, but G1 failed on B1/B2 purely
because base was high there (0.75 on n=8 → p=0.25). NOT a wire failure — a power
artifact (same over-read-the-label trap as s310 SIGN-CHURN).

**Base competence is BIMODAL per entity-class**, not uniform: Qwen3-4B 2-hops
France/Poland/Vietnam landmarks perfectly (base 1.0, zero headroom) but fails
Germany/Canada/Australia/Switzerland/China (base 0.0). So gate power is a property
of the BANK, decided at curation time.

**Rule (writeback_compile-style gated wires): select the HELD splits (B1/B2) from
base-WRONG cells** so the gate has flippable mass. Do it by EMPIRICAL selection —
measure base (one no-train forward pass on a candidate pool) then keep gate-0-valid
cells with base incorrect. Select on BASE ONLY (measurability), never on
post-training accuracy (that would bias the result). bake_wire2.py --select/--reselect
implements this; the offline --reselect re-derives from an existing base pass (no
model). See §P-PLATE-LINKER-1 / write-not-train wires.

Corollary: TRAIN split does NOT need headroom (KL-to-CoT-teacher trains regardless);
reserve the base-wrong cells for the GATED (held) splits.
