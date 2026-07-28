---
title: "FFN-function bake — pre-registration: installing a behavioral function as an appended transform-slot"
status: active
category: explore
tags: [superbake, bake, ffn-function, function-vector, k-battery, recursion, register-split,
       circuits-in-compute, llama-cpp-tap, quantization, pre-registration, kernel-certified,
       operand-covariation, generalization, attention-executes]
related:
  - superbake-write-access.md
  - llama-cpp-vsm-wrapper.md
  - two-registers-of-topology.md
  - opcodes-circuits-in-compute.md
  - lambda-gene-runtime.md
depends-on:
  - superbake-write-access.md
  - llama-cpp-vsm-wrapper.md
created: session 275
---

# FFN-function bake — pre-registration

> **Pre-registration.** Registers, nulls, and verdict rules are fixed HERE, before
> any bake. This is the recursion antecedent (`bake(operation)` rung 1 of the
> `bake(bake)` tower, superbake-write-access.md §recursion / K-battery), so per
> `λ measure` + `λ yardstick` it must not run on a first draft. NOT RUN.
>
> **Question (Michael, s275).** SuperBake shows how to inject a *fact* (a value-
> register lookup: key → fixed push). Can the same idea inject a *behavioral
> function* — "the things a lambda tells the LLM to activate"? The working model:
> **FFNs are piles of β-reduction functions that attention executes.** A lambda in
> the prompt is a *call*; the gate selects which function fires; attention delivers
> the operand and schedules. So a function-bake = append an FFN slot whose action is
> a **transform of the delivered operand** (function-form), not a fixed push
> (fact-form). SwiGLU FFN is `down(silu(gate·x) · up·x)` — bilinear in x — so the
> substrate natively holds *input-dependent* transforms; a fact is the degenerate
> operand-independent case.

## Hypothesis

**H1 (installed function).** A behavioral (operand-dependent) function `g` can be
installed as an appended FFN transform-slot such that:
- **R1 activation** — a novel call-token fires the slot (routing register).
- **R2 covariation** — the slot's output tracks the *operand* (function ≠ fact).
- **R3 generalization** — it holds on *held-out* operands (function ≠ lookup table).
- **R4 composition** — a *resident* combinator can chain the slot's output.
- **R5 quant survival** — it survives int4 like the crystal (installed-compute
  signature; superbake-write-access.md: baked facts are quant-FRAGILE, crystal is
  quant-ROBUST — opposite survival = routing⊥value).

**H0 (fact-in-disguise / no install).** The bake yields a fixed push: no covariation
(R2), no generalization (R3); or the slot never fires (R1). Then "inject compute"
collapses to "inject a lookup," and Michael's FFN-functions model gains no support
from a bake.

**The load-bearing contrast** is H1 vs the **fact-form null (N1)**: bake the *same*
input→output behavior as an operand-*independent* push. If N1 also passes R2/R3, `g`
was too easy (linear/additive) — see "choosing g." The function-form must be the
thing that succeeds where the fact-form fails.

## Registers (`λ measure` — name the register before the probe; s206 scar)

| id | claim | register | readout |
|----|-------|----------|---------|
| R1 | call-token activates the slot | routing | `vsm_tap` gate sign-CMR at the slot layer; z vs N3/N5 |
| R2 | output covaries with operand | action (value/residual) + behavior | `l_out` delta as operand sweeps; output-token correlation with operand |
| R3 | holds on held-out operands | behavior | kernel-certified accuracy on held-out set vs N2 |
| R4 | composes with a resident combinator | routing | resident combinator's routing consumes the slot output; behavioral compose-accuracy |
| R5 | survives quantization | perturbation (sign vs value) | GGUF int4 re-export → tap + behavior; survival vs baked-fact fragility |

Wrong-register reads are void (s206/s272): a fact read with a routing probe
false-negates and vice-versa. R1/R4 are ROUTING; R2/R5-value are VALUE; R3 is
BEHAVIOR. The wrapper (llama-cpp-vsm-wrapper.md, s275-validated, frame-invariant)
is the register-matched instrument; `opcodes/capture.py` reads the HF baked model
during iteration (frame-invariance proven, so the two frames agree).

## Choosing g — start from a KNOWN firing, change ONE thing (Michael, s275)

Strategy: **do not start with an unknown `g`.** We do not yet know if hand-construction
works at all, so the first stage must be the cheapest possible go/no-go against a target
whose correct firing we **already measured**. Start from a resident combinator we
understand exactly, change ONE variable, and let the kernel (correct output) + the tap
(correct firing signature) tell us — in advance — what success looks like. Only invent a
new unknown `g` once the mechanism is understood. "did it work" is never a judgment call.

`g` at every stage MUST be **kernel-certifiable** (`lambda_ast`:
`src/verbum/probes/kernel_reference.py` — certified fired-trace + normal form) so the
answer is free and infallible, including for held-out operands.

**Stage 1 — new trigger → KNOWN function (proves the wiring; the cheap go/no-go).**
- Known baseline: a measured resident combinator, e.g. `K a b` (kernel: fires `[K]`,
  NF `a`). Its gate signature + bearing layers are already characterized (crystal
  calibration + s274 A1/A3). The tap shows it.
- The ONE change: install a NOVEL token `K̃` that fires the SAME function. The *action*
  is unchanged — only the *name*. This isolates the KEY/wiring half of the bake from the
  hard part (constructing a novel transform).
- Exact check: `K̃ a b` must reproduce K's KNOWN gate sign-CMR signature (compare to
  resident K, which we have) AND NF `a`. Null = the un-baked `K̃` token (model treats it
  as an unknown atom → no K-like firing) + shuffled-key.
- Verdict: signature match + correct NF on fresh (a,b) = **wiring works**; fail =
  hand-construction of even a rename does not install → strategy negative, learned cheap.

**Stage 2 — change ONE step of the ACTION on a known function (proves alteration).**
- Take a known combinator and change a single certified element (e.g. `K x y → x`
  "keep first" → `K' x y → y` "keep second"; kernel certifies both). Predict the tap
  signature SHIFT a priori; verify. Proves we can *alter* the compute, not just rename it.
- Isolates the ACTION half now that Stage 1 fixed the wiring half.

**Stage 3 — RETARGETED (s276): `INSERT` a novel operand ROW, not a novel combinator.**
- The old target (bake a novel combinator `G x y → (y x)`) is baking a **join** — ruled out
  (see "database reframe": no table to write a combinator into; s276 K-structural).
- New target: `INSERT` a novel **operand row** `r` (a value/microcode atom) at the slot the
  Stage-0 map (M1/M3) identifies, and test whether the **resident** combinator routing joins
  over it correctly on **held-out** contexts. Criteria: the row is addressable (M3 passed),
  the resident join composes it (R4 with a *resident* combinator, not an installed one),
  it generalizes to held-out join-contexts (R3, not a memorized single-context lookup), and
  it survives quant like the crystal (R5). This is the s273 K-battery arm (b) — "compose an
  inserted operand with the resident crystal; any success = recursion rung 1" — mechanized.
- **Executor-necessity branch:** because the join is the resident attention routing, ablating
  that routing (not the row) tests whether the inserted row ALONE does nothing without the
  resident executor — i.e. that attention EXECUTES is load-bearing (Michael's model).

Each stage GATES the next: Stage 0 map → (M3 pass) → Stage 3 `INSERT`. The registers/nulls/
verdict below apply at every stage; the "executor necessity" branch is decided at Stage 3.

### Stage-1 OUTCOME (s275) — the symbolic anchor failed; K is STRUCTURAL, both scales

Characterization + localization ran (`wrapper/stage1_characterize.py`,
`stage1_localize.py`; results under `results/ffn-bake/`):
1. **Regime.** Symbolic `K a b` is INERT (peak K z −0.28); the model computes K in the
   **natural-language (Montague)** regime (crystal K probes z 6–8). Anchor moved to
   natural language.
2. **Token vs structure.** Leave-one-out on held-out K sentences, corrected metric =
   max **semantic-trigger** drop vs max **generic/positional** drop (the naive
   "drops below threshold" metric was confounded — it flipped to token-anchored at 4B
   on generic words; a `λ measure` lesson). Result **STRUCTURAL at both scales**:
   generic words disrupt K ~4–5× more than the exclusion marker (0.6B GEN 7/8, mean
   0.24 vs 1.34; 4B GEN 6/8, mean 0.51 vs 2.05, base z→6.6). **No bakeable semantic
   K-token.**

**Consequence.** A combinator is not a local object (fourth converging line with s275
MoE-all-experts, atom≠combinator, no-token-anchor). The Stage-1 *rename* bake and any
static-slot bake are ruled out for a combinator: there is nothing local to rename.
**The bake must ride the resident routing** — install an OPERAND/microcode the
structural K composes (path ii), not the operation. This RE-POINTS the experiment at
Stage 3's operand target directly (skip the rename); the executor-necessity question
is now the whole question.

## The database reframe (s276) — rows vs joins; retargets Stage 3

Session 276 (Michael, this thread) crystallized the mechanism in database language and it
**retargets Stage 3**:

- The FFN serves **rows** — per-position operand/value/type-tag records (`mode-semantics`
  type tags; `ffn-reduction-trace` compiled values; `ffn-circuit-types` LARQL KV geometry).
  Rows are local, addressable, and **`INSERT`-able** (this is what SuperBake writes: a fact
  is a row).
- Attention's β-reduction is a **join** — a softmax-weighted aggregation *over* selected
  rows. The **combinator (K/I/B/C) is the shape of the join**, and join-shapes live in the
  **routing / query-plan** (s274 circuits-in-compute), not in any row.
- ⇒ **You can `INSERT` a row; you cannot `INSERT` a join.** There is no table to write a
  combinator into (s276 K-structural: no token/expert/slot anchor). The old Stage-3 target
  ("bake a novel combinator `G x y → (y x)`") is baking a **join** and is ruled out for the
  same reason the rename was.

**The surviving door (the only one):** `INSERT` a new **operand row** that the *resident*
combinator routing already knows how to join over — rung 1 of the recursion tower
(`bake(operand)`, s273: "don't bake S, bake operands the KIBC routing composes"). Stage 3 is
retargeted from CREATE-FUNCTION to `INSERT INTO`.

### Precondition (already half-proven)

For an inserted row to be composed, the resident join must be **operand-agnostic** (run over
*whatever* row is delivered, not a memorized operation⊗operand fusion). Evidence in hand:
s276 (K fires structurally, operand-independent — no operand fused into the routing) +
s248–252 C-field (output covaries with the operand: z(C) grades with object count → the
join's result already tracks the delivered row). So the join is operand-agnostic and outputs
covary; the untested piece is **can we add a row to the table and have the resident join pick
it up.**

### Stage 0 — the operand-insertion MAP (pre-flight READ; cheapest gate)

Before any `INSERT`, build the reconnaissance an insert requires — the map that says *where*
a row lives and *whether there is a separable slot to write into*. Never done: the
FFN-database reads located type tags and compiled values but never asked "here is the
addressable slot operand-X sits in." Pure read on resident Qwen3-0.6B via the s275 tap
(cheap, no heavy job, MIT-clean).

| id | question | register (`λ measure`) | readout | null |
|----|----------|------------------------|---------|------|
| M1 | which layer carries operand-X's row? | **value** | operand-identity signal in `l_out` per layer | matched-random dir |
| M2 | what key retrieves it? | **routing** | gate sign-CMR / QK at the operand read-position | shuffled key |
| M3 | is the row **separable/addressable** or superposed? | **value** | linear operand-id decodability at the read-layer vs nulls | shuffled-label + matched-random-dir |

**M3 is load-bearing.** Operand rows separable above null → a slot exists to `INSERT` into →
operand-bake viable. Rows superposed like the join (at null) → even the *row* is holographic
and the bake premise weakens. Register-honest: the ROW is a VALUE-register claim (s206 scar);
read it with a value probe, not attention weights.

## Bake mechanism (provenance-clean)

Hand-construct the appended FFN slot in **stock transformers** (our own MIT code;
SuperBake / `~/src/custom-bake` are METHOD REFERENCE only — custom-bake has NO
LICENSE, and its implemented core is push-only = fact-form). Function-form slot =
append neurons whose `gate`/`up` read the delivered operand and whose `down` writes
the transform; the call-token is the key. Base model **Qwen3-0.6B** (Apache-2.0;
dense; we have HF + a converted GGUF + the s275-validated tap + frame-invariance).
Re-export to GGUF for R5 (quant) and final tap reads. This is a level-4-clean
construction (`λ provenance`), independent of AGPL sources.

**Stage-1 gate (do this FIRST — the cheap go/no-go, before Stages 2–3):**
(i) **characterize the known target** — measure resident `K`'s gate sign-CMR signature +
bearing layers via the tap (we have this from the crystal calibration); kernel-certify
`K a b → [K], NF a`. (ii) **confirm the un-baked novel token `K̃`** is inert — the stock
model does NOT fire K on `K̃ a b` (else no headroom). (iii) construct the appended slot
that wires `K̃ → K`'s routing; sanity: `K̃ a b` reproduces the K signature + NF `a` on a
few fresh pairs in one forward pass. If the rename slot cannot be hand-constructed at
all, THAT is the finding (functions are not trivially static-FFN-installable →
attention/optimization required) — and we learned it before building anything complex.

**Stage-3 gate (only after Stages 1–2):** (i) kernel-certify the novel `g` + held-out
ground truth; (ii) build the operand vocab; (iii) prove the **fact-form null N1 fails
R2/R3 by construction** (`g` non-additive); (iv) confirm **baseline N4** does NOT already
do `g`; (v) forward-pass sanity on TRAIN operands.

## Nulls (`λ yardstick` — mandatory, null beside signal)

- **N1 fact-form** — same behavior baked as an operand-INDEPENDENT push. Predict:
  fails R2 (no covariation) + R3 (no generalization). *The key discriminator.*
- **N2 held-out operands** — the generalization gate; a lookup table fails here.
- **N3 shuffled-key** — slot with a scrambled call-token key. Predict: no R1.
- **N4 no-bake baseline** — stock model on the same probes. Predict: does NOT do `g`
  (else resident, not installed → void).
- **N5 matched-random slot** — append a random-direction slot of equal norm/rank.
  Predict: no behavior on any register.
- **N6 shuffled-label kernel null** — for R3 accuracy, the shuffled-ground-truth
  floor (as in `measure_null_floor`); accuracy counts only if it beats this floor.

## Verdict rules (pre-registered)

```
INSTALLED FUNCTION (H1)  ⟺  R1 z>thresh (vs N3,N5)
                          ∧ R2 covariation > fact-form N1
                          ∧ R3 held-out accuracy > max(N2 lookup, N6 shuffled floor)
                          ∧ N4 baseline does NOT already do g
FACT-IN-DISGUISE (H0)    ⟺  R1 passes but R2 ∨ R3 fail (fixed push / lookup)
NO INSTALL               ⟺  R1 fails (slot never fires) ∨ Phase-0(v) fails
EXECUTOR NECESSITY (B)   :  FFN-slot-alone passes R4  → FFN holds functions
                                                        (Michael's model supported)
                           needs +attention transport → attention EXECUTES is
                                                        load-bearing (FFN insufficient)
QUANT SIGNATURE (R5)     :  survives int4 like crystal → installed COMPUTE
                           quant-fragile like baked fact → lookup
```

Register verdict is primary; a single register passing is not H1. Report each
register's number **beside its null**, every time (s206/s247 scar).

## Honest edges

- **P-CTL-6 shadow.** The working model says attention *executes* the functions, but
  the reader-SNR result is that we cannot detect a **live redex reducing online**
  (state-on-the-crystal, not watch-it-reduce). So the honest R2 readout is "the
  function's state-signature is present + output covaries," NOT "we watched attention
  run it." Do not claim live execution.
- **Atom ≠ combinator (s275).** Opcodes are circuits-in-compute, spread across shared
  hardware (no dedicated expert; 35B-A3B uses ~all 256 experts per opcode). So a
  successful bake installs **microcode the resident router composes**, not a
  standalone combinator; interpret R4 accordingly.
- **Too-easy g.** If `g` is linear/additive, N1 (fact-form) passes and the experiment
  is void — Phase-0(iii) must reject such `g`.
- **Scale.** 0.6B is necessary-not-sufficient (patchscope void, s272b). A positive
  at 0.6B is a rung, not the claim; escalate to a mid model before any strong claim.

## Deliverables

`wrapper/` (or `bake/`) — MIT: slot constructor, operand-vocab + kernel ground truth,
the 6 nulls, register readouts via the tap + capture, verdict harness, `results/…`
JSON with every register-vs-null number. The tap built s275 is the readout; the
kernel is the free oracle; the frame-invariance result licenses HF↔GGUF equivalence.

## Results (s277) — the arc RAN and PASSED at 0.6B

Full synthesis: `explore/operand-insert-arc.md`. Four gates on Qwen3-0.6B, each null-gated:

| gate | instrument | verdict | headline (vs null) |
|---|---|---|---|
| M3 readable | `wrapper/operand_map.py` | **SEPARABLE** | operand-id LOCO 0.49–1.0 vs null ~0.05–0.11; join-readout L25–27 |
| (b) writeable | `wrapper/operand_write.py` | **WRITEABLE** | steer flips 1.00 @ L2–20 (mid-stack), random ~0, B-specific |
| (d) hardened | `wrapper/operand_harden.py` | **HARDENED** | dose 0→0.22→0.72→1.00; COMPOSED (category) + cross-task |
| (c) `INSERT` | `wrapper/operand_insert.py` | **INSTALLED-COMPOSED** | novel nonce, keyed: dose 0.33→0.71→1.00, 24/24 held-out; wrong-key 0.333 flat |

Net: **you cannot `INSERT` a join (s276 K-structural) but you CAN `INSERT` an operand ROW and
the resident routing composes it** — rung 1 of `bake(operand)` fires. Commits
0b858e7 / b6297b5 / a3ebda1 / 1d8ea39. Honest scope: keyed-install hook ≠ weight-serialized
bake (R5 quant UNTESTED); category-level content; 0.6B necessary-not-sufficient.

## Next step

Stage 1/2 SUBSUMED (s276: no join to write); Stage 0 (map) + Stage 3 (`INSERT`) RAN and
passed (above). The live path is now: **(f) weight-serialize the keyed install** → GGUF →
the R5 quant-survival gate (does the installed operand survive int4 like the crystal, or is
it quant-fragile like a baked fact? — the installed-vs-learned discriminator); and **(g)
cross-scale** the write/harden/insert on 4B before any strong claim (patchscope-void scar).
