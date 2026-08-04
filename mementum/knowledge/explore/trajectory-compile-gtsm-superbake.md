---
title: "Trajectory-compile — GTSM loss + SuperBake bands to make gd_cd's wire legible and portable"
status: designing
category: explore
tags: [trajectory-compile, gtsm, superbake, gd_cd, backprop-compile, depth-timing,
       enrichment-band, pin, g4, legibility, ternary, prereg, s305]
related:
  - gtsm-search-space.md
  - write-not-train-ternary-routing-deltas.md
  - holographic-reduction-machine.md
depends-on:
  - gtsm-search-space.md
created: session 305
---

# Trajectory-compile — make the wire legible and portable

> s305, Michael: "we have the GTSM loss function, and you just found a depth-timing
> measurement. If you look at the SuperBake paper in refs/ it may inform a design."
> This page is the synthesis and the frozen pre-reg it produced.

## The convergence (three independent lines on one design)

1. **s305 depth-timing (measured, ours).** The country materializes on the one-shot
   landmark prompt only at L24 (the s305 decodability cliff), while the native h-hop
   has already consumed its input by then (capital_leak 0.62 at L24 on a clean
   country prompt). The two hops **overlap in depth** → no static write at L24 can
   route (five constructions inert, s303–s305).

2. **SuperBake (`refs/superbake.txt`, Ruehlman 2026) — the law from the other side.**
   *"a single-layer linear map fights with only the layers above it, while SGD's early
   deposits ride nineteen native nonlinear layers of amplification; the network is the
   kernel, and it is upstream."* Their first constructed linear solve plateaued at
   **58%**; the fix was writing composition **enrichment at 0.16× depth** (≈L6), where
   native subject→attribute machinery lives. Their transport law — *"read a payload at
   write-layer +1; it does not survive many blocks; quiet directions attenuate ~30×"* —
   is our `reinject_landed 0.033` verbatim. Our late writes violated their laws.
   **But** SuperBake composes *known* facts (inject the answer-entity early, per-fact =
   a lookup); our wire needs the model's own *inferred* country → construction hits the
   same depth wall (their §8 boundary: keys "go key-dead at depth").

3. **GTSM (`gtsm-search-space.md`, Thm 3.2).** Endpoint losses match only the terminal
   marginal → admit **compensating-error** solutions (a layer's error cancelled
   downstream): correct at the output, wrong internally. gd_cd (s303) used endpoint KL
   and **its G4 pin-mechanism was UNMET** — almost certainly an answer-shortcut, not a
   materialized intermediate. GTSM's dense per-depth match removes exactly that
   degeneracy; Prop F.6 says at finite budget, spike the weighting where it matters —
   **SuperBake supplies where (the enrichment + readout bands).**

**The design.** Take the one thing that WIRED (gd_cd gradient) and (a) widen its LoRA
band to reach the enrichment band so gradient can reshape the EARLY layers, (b) replace
endpoint KL with a **GTSM depth-dense trajectory loss** to the teacher's own CoT,
SuperBake-weighted. Prediction: the country now materializes **early and legibly** (G4
closes), the wire generalizes (F1–F3), and it ternarizes to a portable plate (s304).
This is the s299 auto-superbake lifecycle made precise: **construction laws shape the
trajectory targets; gradient (the GTSM search) finds the legible, portable delta.**

## §P-TRAJECTORY-COMPILE — pre-reg (FROZEN s305, before any run; s222 law)

> Michael GO on the direction and on **G4 as a GATING clause** (make the mechanism
> legible, not just the behavior). Trajectory target = **full residual, cosine per
> depth** (Michael-approved fork; keeps G4 an honest independent test). Freeze before
> touching the model; the run only fills numbers.

**Question.** Does a GTSM depth-dense trajectory loss with a SuperBake-scheduled band
weighting, on a LoRA band widened to the enrichment band, make gd_cd's wire *legible*
(country materializes early — G4 closes) — and is it the **loss** that does it (vs the
wider band alone)?

**The loss (FROZEN).**
```
L = KL_answer(student ‖ teacher)                      # gd_cd terminal anchor
  + λ · Σ_L w(L) · ( 1 − cos( student_last[L], teacher_last[L] ) )   # GTSM trajectory
```
- teacher = **frozen base** on its own committed CoT `TEACHER_PROMPT` ("...located in
  {c}. The capital of {c} is", {c} = the gate-0 committed country); student = the
  one-shot `DIRECT_PROMPT` (LoRA-adapted). `*_last[L]` = last-token residual (decoder
  layer output) at layer L; teacher trajectory precomputed once (frozen base).
- **w(L)** = SuperBake schedule (FROZEN): uniform floor 0.2 + Gaussian bumps at the
  **enrichment band L6** (0.16×36) and the **readout band L25** (0.7×36), σ=2, then
  normalized to Σ_L w(L)=1. (GTSM: cover everywhere; spike where it matters.)
- **λ = 1.0** (FROZEN, not tuned; trajectory term ≈ O(1) vs KL O(1–5) at init).
- cosine-per-depth = the ‖·‖_D proxy (per gtsm-search-space.md; SDE→transformer
  idealization caveat inherited — narrowing transfers, literal Pθ=P* does not).

**Structural change (forced by s305 + SuperBake).** LoRA band widened from gd_cd's
late **L22–29** to **L5–L27** (≈0.14–0.75 depth, FFN-only, r=16, α=32) so gradient can
reshape the EARLY layers — *"the network is the kernel, and it is upstream."* lr 1e-4,
≤500 steps, bf16, Qwen3-4B, ≥3 seeds. Gate-0 (the frozen 53 cells) inherited; VOID if
it fails.

**Arms** (trained on TRAIN cells; scored on the frozen splits):
- `base` — floor (0.200 / 0.125 / 0.545).
- `traj_compile` — **PRIMARY**: wide band L5–27, loss = KL + λ·trajectory.
- `gd_cd_wide` — **CONTROL (isolates the loss)**: same wide band L5–27, **endpoint KL
  only**. If it also closes G4, the wide band alone suffices; if only `traj_compile`
  closes G4, the **trajectory loss is causal**.
- `traj_shuffle` — **λ yardstick**: trajectory loss to a teacher whose CoT has
  **deranged countries** (matched budget/band). Must fail. ≥3 derangement seeds.
- `construct_lookup` — inherited materialized-view null (F2 baseline; must fail B2).

**Gates** (verbum.dsp paired-perm 10k; primaries F1–F3 Bonferroni α/3; G4 gating this
time; F5 deterministic; primary arm = `traj_compile`):
- **F1 WIRE** : traj_compile > base, flip on B1 AND B2.
- **F2 NOT-LOOKUP** : traj_compile > construct_lookup on B2.
- **F3 SPECIFICITY** : traj_compile > traj_shuffle on held-out (B1 ∪ B2).
- **G4 PIN — GATING (Michael's call): the mechanism must be legible.** On **held-out**
  cells, build the whitened country key at the enrichment band L6 (shared-Σ from
  CC_FRAMES + innocents, as build_keys). Two sub-clauses, BOTH required:
  - **G4a rises** : mean enrichment-band country readout (traj_compile) > base on
    held cells (the country now materializes early);
  - **G4b tracks** : the readout separates correct-from-incorrect held cells (gate on
    correct−incorrect readout means > 0). Legibility ≡ present ∧ predictive.
- **F5 SURVIVE** : innocent CE ≤ 2% rel base; native g/h within 0.10 abs.

**Reports (advisory, NOT gates; λ observation).** Per-layer country-readout trajectory
(the money plot: does the country now materialize early? traj_compile vs gd_cd_wide vs
base) · ternarize-retention (TWN the traj_compile delta per s304 — does it survive to a
portable plate?) · G4 at the s303 install layer L23 (for continuity) · KL/trajectory
loss curves · trit-count of the ternarized delta (λ smallest).

**Verdicts (FROZEN).**
- **TRAJECTORY-COMPILES (+PIN-LEGIBLE, +LOSS-CAUSAL)** : F1∧F2∧F3∧G4∧F5 ∧
  `gd_cd_wide` FAILS G4 → the wire installs, the pin is legible, and the **trajectory
  loss** is what closed it (the wide band alone did not). ★ the target result — the
  s303 G4 gap closed, mechanism understood, and the causal lever named.
- **TRAJECTORY-COMPILES (+PIN-LEGIBLE, BAND-SUFFICES)** : F1∧F2∧F3∧G4∧F5 but
  `gd_cd_wide` ALSO passes G4 → early materialization comes from the wide band, not the
  trajectory loss (still a win: the pin is legible; the depth-timing fix was the band).
- **WIRES-BUT-OPAQUE** : F1∧F2∧F3∧F5 but ¬G4 → wires like gd_cd, but neither the loss
  nor the band made the country materialize legibly early on held cells (the
  answer-position residual match did not force early materialization) → the next
  refinement is the country/capital-subspace-targeted trajectory (the deferred fork).
- **NO-WIRE** : ¬F1 → the wide-band trajectory loss failed to wire (surprise vs gd_cd).
- **UNSPECIFIC** (¬F3) / **HOST-DAMAGED** (¬F5).

**A-priori lean (grounded; do NOT peek).** gd_cd already wires → F1 likely. The genuine
uncertainty is G4. SuperBake+GTSM predict the wide band + trajectory loss materialize
the country early and legibly; the sharp open question is whether the FULL-residual
answer-position match forces early country-specific materialization or just surface
mimicry. ~50% +PIN-LEGIBLE (split +LOSS-CAUSAL vs BAND-SUFFICES), ~35% WIRES-BUT-OPAQUE,
~15% NO-WIRE/other. **gd_cd_wide failing G4 while traj_compile passes is the causal
control; either G4 branch is a real finding.** Not tuned to pass (λ, w, band frozen a
priori; λ yardstick).

**Cadence.** build the instrument (reuse `writeback_compile.py` gd_cd loop + LoRA +
gate scoring + the whitened readout; add the per-depth trajectory loss, wide band, the
G4 gate, arms) → `--validate` (planted: trajectory loss drives cosine up, band mask,
G4 rise+track, verdict worlds) → smoke (`--n-cells`, mechanics only, s297) → Michael GO
→ run tmux main:1 (~1–3h MPS) → frozen scoring → §Result-trajectory-compile + approval
batch.

## Sessions
s305 (this thread. Michael pointed at the SuperBake paper after the HHOP-INERT
depth-timing finding + the GTSM loss. Synthesis: SuperBake proves "the network is the
kernel and it is upstream" (our depth-timing law from the other side) and shows
construction can't wire an inferred intermediate; GTSM removes the compensating-error
degeneracy that left gd_cd's G4 pin unmet. Design = trajectory-compile: widen gd_cd's
band to the enrichment band + replace endpoint KL with a GTSM depth-dense trajectory
loss, SuperBake-weighted. G4 promoted to a GATING clause (legibility). §P-TRAJECTORY-
COMPILE frozen; instrument + run pending Michael GO).
