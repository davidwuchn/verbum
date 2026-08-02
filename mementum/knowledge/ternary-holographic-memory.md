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
