---
title: "Ternary Holographic Memory — A Standalone, Model-Free, Delta-Logged Store"
status: designing
category: architecture
tags: [ternary, mirrors, plates, memory, standalone, balanced-ternary, radix-economy, delta-log, time-travel, angular-multiplexing, hrr, capacity, shannon, ecc, git-for-holograms, artifact, mit]
related:
  - holographic-reduction-machine.md
  - five-disciplines-one-object.md
  - attention-holographic-readout.md
  - ternary-compounding.md
  - holographic-error-correction.md
  - recursion-mirrors.md
  - computed-beam.md
depends-on:
  - five-disciplines-one-object.md
  - holographic-reduction-machine.md
created: session 299
---

# Ternary Holographic Memory

> Session 299, final thread. Michael: ternary plates + mirrors → arbitrary
> precision → a memory system tied to no model → "keep packing more data in
> without storage growing" → **caveat: store each change as a DELTA from the
> last state; delta back to the beginning, or any point between.** The
> caveat is the design. This page is the artifact spec — possibly the
> cheapest real deliverable on the books: standalone, MIT-clean, pure
> numpy, no model anywhere.

## 1. Arbitrary precision — yes (balanced ternary)

{−1,0,+1} is **balanced ternary** — a full numeral system (Knuth: "the
prettiest"). Stack plates as signed digit planes (mirrors = ±/skip
weighting); precision ∝ plate count. **Radix economy theorem:** base 3 is
the most economical integer radix (closest to e) — ternary is the provably
optimal storage radix, not just an extraction artifact. In-house proof of
plate-stacking: s173 sign-plate + magnitude-plate ≡ two-digit precision via
additive mirrors.

**The compounding caution inverted (ternary-compounding.md):** 0.88³⁶ =
garbage kills ternary as *deep compute* — errors compound multiplicatively
through composition. **A memory reads in O(1)** — one correlation, no
cascade. The compounding law does not bite the memory use-case. Memory is
where ternary is naturally safe.

## 2. Model-independence — yes

The math is standalone (HRR/VSA lineage — Plate's memories had no host):
write = superposed key⊛value exposures; read = correlation; address =
mirror angles (angular multiplexing — literally how physical holographic
data storage was engineered). The system defines its OWN frame; the frame
problem (cross-init sign-corr 0.000) appears only at attach time → gated
Procrustes/relational transport (s251/s296) when a host model is involved.

## 3. Capacity — the honest split (λ yardstick + λ exchange)

- **Hard bound:** Shannon. D trits ≤ ~1.585·D bits. No medium packs
  unbounded information into fixed storage. History costs bits too.
- **Measured escape hatch:** CAP coherent-gain — correlated exposures
  deepen the shared grating; retrieval STRENGTHENED through k=16. Capacity
  for ITEMS is effectively unbounded when items share structure: the medium
  stores shared structure once, deviations cost fresh bits. "Storage
  doesn't grow" ⟺ data compressible. Plus holographic fail-soft (graceful
  SNR decline, no cliff) + the ECC 95%-topology/5%-calibration redundancy
  knob.
- **The dissolution:** a fixed-size store that absorbs structured data
  without growing and retrieves by content = compression = learning = **a
  model of its data**. The memory/model distinction is only the write rule;
  the LLM is the existence proof (TB corpus → GB weights,
  content-addressable). Build the model-free memory and it becomes a model
  — of the data, of no host. That is the meaning, not a flaw.

## 4. The delta-log (Michael's caveat = the core design)

**Store each change as a delta; recover any historical state.** Git
semantics materialized in the tensor medium — the mementum S2 protocol
("git preserves history → update ∧ delete ≡ safe, always recoverable")
compiled into tensors. The fractal again: git for holograms.

**Why it works — linearity (axiom A1, measured):** deltas superpose
exactly in the accumulator register:

```
state(t) = state(0) + Σ_{i≤t} Δ_i          — exact, linear vote space
recall(t') = illuminate deltas i ≤ t'       — time travel by partial sum
undo(Δ)  = add(−Δ)                          — exact erasure
```

**Register discipline (the one subtlety):** sign(a+b) ≠ sign(a)+sign(b) —
the ternary collapse is nonlinear. So the design keeps TWO registers, and
our etch already has both: the **vote accumulator** (linear, continuous —
where the delta-log lives, exact history, no compounding) and the
**collapsed plate** (ternary — the readout snapshot). Delta history in vote
space = exact replay; collapsed snapshots = lossy checkpoints. This is the
s115/s298 etch architecture reused verbatim.

**Four consequences:**

1. **K solved by construction.** Erasure = add the negated stored delta —
   the π-shifted exposure IS −Δ. The "K is hard at every scale" law
   (softmax can't zero, git append-only, weights accumulate) gets its
   clean solution: in a delta-logged linear medium, undo is exact algebra.
2. **Temporal angular multiplexing.** Write Δ_t at mirror angle θ(t) →
   recall state(t') by illuminating angles ≤ t'. Time as reference-beam
   angle — the loop-index-embedding trick applied to history; RoPE for the
   past. Address axes: content (correlation) × time (angle).
3. **Cost ∝ change, not state.** Deltas are sparse (small support —
   ternary diff of two states is naturally {−1,0,+1} with mostly 0). Git
   packfile economics in the medium.
4. **Compaction = squash.** Sum a prefix of deltas into a new base (trade
   history for space — Shannon's rent). The s262 state.md compaction, in
   tensors. Same lifecycle as machine-page §5c: transient → promote →
   base, gated by L-meter/Exp-B when attached to compute.

## 4b. The mementum isomorphism (s300 — the protocol has two implementations)

S2 defines mementum as **protocol ¬implementation | any_tool_can_implement**.
Taken seriously: this store is not *like* mementum — it is a **second
implementation of the mementum protocol in a tensor medium**. Operation by
operation (made exact by the transducer framing — the delta-log IS a
reduction, `state(t) = reduce(add, deltas[0..t], base)`):

| Mementum (git medium) | Ternary store (tensor medium) |
|---|---|
| Commit log = source of truth; repo state = checkout of history | Δ-log = source of truth; state = fold of the log |
| Memory file — small, one insight, append-only | Δᵢ — sparse, one exposure, appended to the log |
| `state.md` — lossy working snapshot, cheap to read | `sign(vote)` collapse — lossy ternary checkpoint, O(1) read |
| s262 compaction — squash history into terse base | `squash(t)` — sum a prefix into a new base |
| `git revert` — undo by appending inverse commit | undo = append −Δ — exact erasure, log preserved |
| Recall: temporal (`git log`) × semantic (`git grep`) | Recall: time axis (permutation prefix) × content axis (correlation) |
| Commit SHA — content-addressed integrity | `state_hash` sha256 — content-addressed integrity |
| Cold-start: read snapshot, don't replay history | Read collapsed plate, don't re-fold the log |

**Transducer decomposition (s299 transducer math applied to its own
artifact):** encode (bind ∘ time-permute, stateless map) → rf (int-add in
ℤᴰ — the ENTIRE determinism proof obligation localizes here) → drivers
(write / prefix-fold=time-travel / squash; separated per Hickey rf→rf) →
readout (correlate, `sign()` collapse) at COMPLETION only. The closure
theorem becomes topology: the chain is the linear register; `sign()`
cannot appear mid-chain by construction (λ shape: unreachable > forbidden).
Determinism: integer arithmetic end-to-end (associative add →
order-independent, platform-exact), PCG64 explicit-seed keys, permutations
in place of float mirror angles (discrete rotation, exact, invertible).
Crosstalk still exists but is DETERMINISTIC noise — the same integer every
run. Portability payoff: same encode/rf pair over a Python loop (POC),
batch replay, or eventually the forward pass (§5c fast-plates = deltas
written by a loop; same transducer, dearer host).

**Honest differences (λ yardstick — where the fit must not be forced):**

1. **Interference.** Git entries are discrete, lossless, zero-crosstalk,
   O(n) growth. The store superposes into fixed size — reads carry
   (deterministic) crosstalk. Not a defect: the §3 dissolution. Git
   remembers; the plate *learns*.
2. **★ Coherent gain ≡ the ≥3-memories rule implemented in physics.**
   Mementum-S4: ≥3 memories(topic) → knowledge candidate, via LLM
   synthesis. In the superposed medium, correlated exposures automatically
   deepen the shared grating — shared structure stored once and
   strengthened, deviations cost fresh bits. **The medium metabolizes by
   superposition; no synthesizer in the loop.** (The one genuinely new
   observation of this section.)
3. **No S3 gate.** Mementum writes pass λ store / λ termination. The
   tensor store etches any Δ unconditionally — S1/S2 substrate only;
   gates live in whatever drives the transducer (kept separate by the
   framing).
4. **No semantics in squash.** s262 compaction was meaning-aware;
   `squash` is blind summation — what survives is whatever superposes
   coherently.

**Hierarchy placement:** residual < sign-tape < transient plates <
permanent plates < git gains an interior rung — the ternary store is
**git semantics at plate cost**: fixed-size episodic history with
time-travel, the register the s295 exhaustion law says transformers lack,
carrying the protocol already trusted at project scale. The fractal
closes with the same protocol at both ends of the hierarchy.

## 5. The artifact spec

```
ternary holographic memory (standalone, MIT-clean, pure numpy, no model)
  write:     sign-vote etch (delta-increments to the vote accumulator)
             [exists, bit-reproducible since s298]
  read:      correlation                       [dsp/readout.py]
  address:   mirror-angle multiplexing — content × time axes
  history:   delta-log in vote space; time-travel by partial sum;
             undo = −Δ; squash = compaction
  precision: balanced-ternary plate stacking   [s173 proven, 2 digits]
  ECC:       redundant exposure + topology/calibration split
             [holographic-error-correction.md]
  snapshot:  ternary collapse (lossy checkpoint; exact history stays
             in votes)
```

## 6. Validation — P-CAPACITY-LAW (model-free, seconds to run)

Capacity curves: items vs retrieval SNR for random / correlated /
self-similar data. **Predictions:** random follows the √(D/k) HRR decline;
coherent shows CAP-style gain before the Shannon wall. Settles the
HRR-capacity import from five-disciplines-one-object.md (where naive
theory got the CAP sign wrong) with our own instrument. **Add the delta
axes:** (a) replay fidelity vs chain length — exact in vote space
(prediction: flat), measured degradation in collapsed-snapshot space
(prediction: compounding-law shadow); (b) recall(t') accuracy vs time-angle
separation (Bragg-style selectivity curve on the time axis — P-BRAGG's
sibling). Pure verbum.dsp + etch primitives. The purest λ smallest
experiment on the books.

## 6b. §P-CAPACITY-LAW — pre-registration (s301, frozen before run)

**Claim registers (λ measure, named before probes built):** capacity/SNR
claims = **value register** (graded, continuous); replay-exactness claims =
**causal/deterministic register** (hash equality, not statistics);
time-Bragg claim = **routing register** (crisp address selectivity).

**Substrate = the s300 store verbatim** (`src/verbum/memory/`): no new
mechanism, measurement only. `encode(key, val, t)` = ±1 bind ∘
time-permutation; fold in ℤᴰ; readout = `correlate`/`recover`;
`collapse` = ternary snapshot. D = 4096 (validate leg 1024), k ∈
{1,2,4,8,16,32,64,128}, R = 20 seeds/condition, all seeds explicit ints
(s296 law). Instrument `scripts/explore/capacity_law.py`, pure
numpy + `verbum.dsp` scoring; no model, no GD.

**Design realization (two register forks made explicit a priori):**

1. **Address fork.** Independent random ±1 keys WHITEN the data: bound
   exposures `k_i∘v_i` are pairwise-decorrelated even for identical values
   → coherent gain is REACHABLE ONLY in the shared-address register (same
   key, same t). Pre-registered consequence: the §6 "coherent shows
   CAP-style gain" prediction is tested where the physics permits it
   (shared key), and its ABSENCE under independent keys is itself a
   prediction (G3), not a failure.
2. **Collapse commutes with recover.** `sign(k∘sign(v)) = sign(k∘v)` for
   ±1 keys → per-component `recover()` is IDENTICAL from vote state and
   snapshot. Snapshot loss is only measurable in (a) correlate-readout SNR
   (a-priori theory: constant ×√(2/π) ≈ 0.798, the classic 1-bit
   quantization loss — NOT a slope change) and (b) REPEATED
   collapse-checkpointing (fold onto a collapsed base — where the
   compounding shadow actually lives). §6's "compounding-law shadow in
   collapsed-snapshot space" is sharpened to prediction (b).

**Arms (data families × address register):**

- `random`: v_i i.i.d. dense ±1 — the HRR baseline.
- `correlated`: v_i = prototype p with an independent fraction (1−c)/2 of
  components flipped, c = 0.5 — shared structure + deviations.
- `hierarchical` (the §6 "self-similar", ADVISORY curves only): 2-level
  prototype tree (4 super-prototypes, c_super = 0.7, c_item = 0.5) —
  report multi-scale SNR, no gate (predictions not sharp enough to gate).
- Address registers: `indep` (per-item key + per-item t — the episodic
  write) × `shared` (one key, one t — the coherent write).

**SNR definition (one definition, all arms):** signal = mean
`correlate(state, probe_true)`; noise = std of `correlate(state,
probe_wrongkey)` over matched wrong-key draws (the test-suite null,
promoted to yardstick). Prototype SNR uses probe = encode(K, p, t).

**Gates (all via `dsp.gate` — declared null + direction, α = 0.05;
slope-form gates use the holo_cap G2 discipline verbatim):**

- **G1 HRR-FORM** (random × indep): log-log slope β of SNR(k) vs a-priori
  β* = −1/2 (SNR = √(D/k)). Statistic |β − β*|, predict **less**, null =
  `matched_range` over the observed SNR range (s247 φ-ladder discipline).
  Materiality precondition: monotone decline, SNR(k_max) < SNR(1)/2.
- **G2 COHERENT-GAIN** (correlated × shared): prototype-SNR log-log slope
  vs k, predict **greater**, null = same pipeline rerun with c = 0 banks
  (R null draws, provenance recorded). A-priori theory: slope ≈ +1/2
  (prototype SNR = c·√(kD)); form scored ADVISORY (|β − ½| vs
  matched_range), direction is the gate.
- **G3 ADDRESS-FORK** (correlated): per-seed Δslope =
  slope_shared(prototype) − slope_indep(prototype), predict **greater**,
  null = `paired_permutation` (10k) over the R seed pairs. This is the
  register fork: gain lives in address sharing, not in data correlation
  alone.
- **G4 REPLAY** (delta axis a, two legs):
  - **G4a EXACT (deterministic, no p-value):** ∀ prefix lengths on a
    1024-commit log (incl. undo + squash events): `state_hash` of re-fold
    in shuffled order ≡ original. One failure = gate fails. (Extends
    G-DET/G-REPLAY from the unit suite to capacity-scale chains.)
  - **G4b CHECKPOINT-SHADOW:** fold C ∈ {0,1,2,4,8} collapse-checkpoint
    events into the chain (continue folding onto `collapse(state)` as new
    base); fidelity(final vs true state) declines with C. Statistic =
    mean per-seed (fidelity(C=0) − fidelity(C=8)), predict **greater**,
    null = `sign_flip` (10k). C=0 must be exact (ties G4a).
  - ADVISORY (sharp number, not gated): correlate-SNR ratio
    snapshot/vote ≈ √(2/π) ≈ 0.798, constant across k.
- **G5 TIME-BRAGG** (delta axis b): value = mean `correlate(state,
  encode(key_i, v_i, t_i))` at the true time-address; null draws = the
  same correlations at offsets δ ∈ {±1, ±2, ±4, ±8} (the sidelobe
  distribution IS the null), predict **greater**. A-priori: peak ≈ D,
  sidelobe σ ≈ √(kD) → ≥5σ separation at D=4096, k=128. ADVISORY: full
  selectivity curve vs δ (P-BRAGG's sibling, reported not gated).

**Verdict table (frozen):**

| Verdict | Condition |
|---|---|
| **CAPACITY-LAW-CONFIRMED** | G1 ∧ G2 ∧ G4(a∧b) ∧ G5 |
| **DECLINE-ONLY** | G1 ∧ ¬G2 — naive HRR right in this medium; the CAP coherent-gain does NOT transport to the standalone store (kills the §3 escape hatch as stated) |
| **GAIN-WITHOUT-FORM** | ¬G1 ∧ G2 — gain real, √(D/k) form wrong → theory import needs rework |
| **SUBSTRATE-FAULT** | ¬G4a ∨ ¬G5 — contradicts the s300 green gates → debug before any capacity claim |
| **INCONCLUSIVE** | anything else |

G3 modulates interpretation (register fork), never the headline verdict.
Score honestly; a-priori lean: CAPACITY-LAW-CONFIRMED — every gate has
closed-form theory behind it; the informative outcome is any deviation.

## 7. Status & discipline

Deliverable class: S5 artifact (useful tomorrow, without us, without any
model). Cheap to build (numpy; primitives exist). Queued per
close-before-opening: behind rung-3b freeze (s300 cold-start) — but note
P-CAPACITY-LAW needs no model and no GD → legitimate cheap-slot candidate
whenever a session has one.

## Files
| File | Content |
|---|---|
| `holographic-reduction-machine.md` §5c | the delta-plate lifecycle this memory serves |
| `five-disciplines-one-object.md` | HRR capacity import + λ exchange rule |
| `ternary-compounding.md` | the compounding law (why memory-use is safe, compute-use is not) |
| `holographic-error-correction.md` | topology/calibration split = the ECC knob |
| `src/verbum/dsp/` | readout, whiten, nulls — the read instrumentation |
