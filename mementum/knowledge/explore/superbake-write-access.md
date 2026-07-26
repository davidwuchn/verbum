---
title: "SuperBake — write access to the substrate, and the weight-level recursion"
status: open
category: explore
tags: [superbake, direct-construction, gradient-free, fact-injection, unembed-silent,
       patchscope, positive-control, circuit-map, receipts, recursion, self-hosting,
       two-registers, quantization]
related:
  - lambda-gene-runtime.md
  - opcode-jacobian-jspace.md
  - ../crystal-universality.md
  - crystal-seeded-ternary-distillation.md
depends-on: []
created: session 273
---

# SuperBake — write access to the substrate, and the weight-level recursion

> s273 discussion (Michael: "look at ~/src/custom-bake"). Verbum spent ~270
> sessions building READ access to the substrate; this repo is WRITE access.
> Facts installed into transformer weights with NO gradients — hand-constructed
> circuits in appended MLP slots, closed-form, behaviorally verified, receipted.
> Nothing run yet by us; this page records the read + the convergences + the
> recursion insight + the pre-reg sketch.

## The artifact

- `~/src/custom-bake` — independent reimplementation of "SuperBake: Installing
  Verified Facts into Transformer Weights by Direct Construction" (Albert
  Ruehlman, AMI Labs, July 2026, doi:10.5281/zenodo.21502811).
- ⚠ PROVENANCE: no LICENSE file, no license field in pyproject (checked s273).
  Fine as instrument/reference; check before deriving code (S5 λ provenance).
- Mechanics: every MLP uniformly expanded by E zero slots (stock config loads
  unchanged). Per fact: Mahalanobis matched-filter RECOGNITION keys (carrier-
  perpendicular — silu knee at population mean with no bias, "born-hard"
  quadratic gates) → inject a manufactured CODE direction → READOUT + CHAIN
  neurons at a measured delivery layer push answer tokens. Closed loop calibrates
  magnitudes (secant transfer estimate, backfire guards); referees (prose NLL,
  held-out known facts, neighbour hallucination) with auto-revert; failing rows
  NEUTRALIZED (failed ≠ absent). Receipt: physical address per fact — zero the
  slots, the fact is gone, exactly.
- Measured (their box, Qwen2.5-0.5B): 483/492 rows (98.2%), 36/36 primaries,
  reverse rows 100% (reversal curse dissolved by installing the reverse
  direction as its own rows), prose NLL +0.0059 nats, 100% receipt honesty in a
  fresh stock-transformers process. Bake-then-quantize supported; int4 flips
  borderline rows.

## Convergences with verbum (why this matters to us)

1. **Codes are unembed-silent BY CONSTRUCTION ≡ the property we MEASURED.**
   Codes are drawn from a mid-band of residual PCA and orthogonalised against
   the top principal directions of the effective unembedding — "loud in the
   residual, quiet at the logits." That is exactly P2 workspace-basis silence
   (s272: J-space basis dirs frozen-unembed-silent). Ruehlman chose it for prose
   safety; GD apparently converged on it too. The bus is real; this repo writes
   onto it by hand.
2. **→ PLANTED GROUND TRUTH for patchscope.** The patchscope G1 positive
   controls are unembedding rows (weak: readable by construction). A baked code
   is the control we actually want: content-bearing AND unembed-silent by
   construction, with a KNOWN referent. Bake a fact, pull the code direction
   from the receipt, patchscope-inject it: recovers fact-content → instrument
   proven sensitive to exactly the class of direction the workspace hypothesis
   needs; then persistent workspace-dir silence would be REAL, not instrumental.
   We can now MANUFACTURE calibration standards for "silent content directions."
   Cheapest fun: 0.5B bake is minutes.
3. **Fact/function boundary made physical = the two-register split, writable.**
   SuperBake installs LOOKUP: magnitude-calibrated value-register pushes
   (clearance/gap/push are all value-register quantities). The crystal is
   COMPUTATION: routing, sign-carried, quant-robust. Predictions (pre-reg
   candidates, instruments already exist):
   - trace a baked model through opcodes/ → crystal UNTOUCHED (appended slots ⊥
     routing). A new perturbation rung for the ladder, sibling to ternary/1-bit.
   - quantize the baked model → baked facts quant-FRAGILE exactly where the
     crystal was quant-robust (README already observes int4 flipping borderline
     rows). Same model, same quantizer, opposite survival = routing⊥value
     demonstrated on installed-vs-learned knowledge in one artifact.
   - the crystal instruments become a DISCRIMINATOR between installed knowledge
     and learned computation.
4. **The receipt is the circuit-map canonical form S2 has an IOU for.**
   {layer, slots, role, clearance, push, verified, neutralized} + honesty
   invariants (verify-what-ships, failed ≠ absent, referees-with-revert). Steal
   the shape, derive our own.

## The recursion (Michael's completion — the piece the convergence list missed)

```
bake(fact)      works        — measured, receipted
bake(operation) open         — the K-battery question (below)
bake ∈ operations            — the baker is itself a procedure
∴ bake(bake′)                — the installer is installable
∴ Y at the weight level      — self-modification as an acquired, addressable capability
```

If operations inject, the lambda-gene runtime loop CLOSES THROUGH THE SUBSTRATE:
proven genes graduate prompt → weights, and the next generation of genes is
generated by the improved model. Each pass persists into the thing that runs the
next pass ≡ self-hosting bootstrap (compiler compiling itself; the compiler is
the λ-crystal, the linker is direct construction). s272d said recurrence converts
duplication-in-space (softmax-forbidden) into duplication-in-time; this is that
theorem at the SYSTEM level — external Y with the accumulator inside the model.

What keeps it sane:
- **Kernel = rung-verifier.** Every candidate operation is a lambda term → kernel
  certifies semantics (exact reduction; S3*-1 kernel-verified execution), receipt
  certifies installation. Y with a step budget and a judge at every unfold.
- **Receipts make every rung ablatable** → auditable self-improvement history;
  gene-db lineage extends into the weights (locus, receipt, fitness, parent).
- **λ termination**: AI proposes → kernel certifies → receipt verifies → HUMAN
  approves graduation to weights. Michael stays the termination condition of the
  Y. The mementum protocol was already shaped for this.

**Feasible path — ride the resident crystal, don't rebuild it.** SuperBake's
implemented core is MLP-only (matched filter → push) = lookup; genuine operations
need variable transport = attention, and the §3.6 attention organ is
unimplemented in the repo (paper §3.6 now READ — recipe exists, see §s273c
below). But the routing ALREADY EXISTS in the host: the crystal (KIBC,
universal, quant-robust). So don't bake S — bake OPERANDS/microcode the resident
compiler composes. Division of labor lands exactly on the measured register split
(s269c): operations register-bound and already present; content register-invariant
and installable. Crystal = ALU, bakes = instruction tables, resident attention =
transport. we(find) ¬we(build) — then extend what we found in its own idiom.

## Two-arm K-battery (pre-reg SKETCH — formalize registers/nulls before running)

- **Arm (a)**: bake a battery of K-combinator INSTANCES ("K a b → a" as facts);
  test FRESH argument pairs. Expect FAILURE (lookup ≠ function; MLP-only
  ceiling). This alone = memorization-vs-rule boundary made physical.
- **Arm (b)**: bake instances keyed to COMPOSE with the resident crystal
  (recognition fires on structure; push injects content existing opcodes then
  route); test whether generalization emerges from composition with what is
  already there. Any partial success = the recursion's first rung.
- Registers: behavioral (fresh-instance accuracy) + geometric (do baked circuits
  appear in / couple to crystal Gram geometry? prediction for arm (a): NO).
- Nulls: never-baked decoy instances; shuffled-label geometry nulls per
  λ yardstick.
- Status: NOT RUN. Antecedent of everything in the recursion section.

## s273b — GTSM ⇄ baking, custom-bake ⇄ TernaryDescent (Michael's two questions)

Both directions are one move seen from two ends: **measurement + closed-form
write replaces descent wherever response is linear (value register); GTSM
explains why any loop — bake or training — must constrain TRAJECTORIES, because
endpoints under-determine.**

### GTSM → baking

SuperBake's closed loop is an ENDPOINT objective (target_gap at the answer
position). Every stage-C guard is a patch for endpoint-matching failure:
"greedy catches chain deaths teacher forcing hides" ≡ the endpoint-vs-path
distinction verbatim; backfire/neighbor-shift/prune-to-fixed-point = many
internal configs share one terminal gap; the referees (prose NLL, leak, known
facts) = SPARSE POST-HOC SAMPLES of a trajectory constraint.

GTSM (gtsm-search-space.md, Thm 3.2/Girsanov): match drift along the path ⟺
match the path measure, for ANY positive weighting. Practical because the drift
perturbation of an appended neuron is ANALYTIC — for harvested innocent state x,
Δdrift = down_column × silu(x·k_gate)(x·k_up), no forward pass. So:

```
∫ depth×positions E_innocents ‖Δdrift(x)‖²_D  ≈  KL(P_baked ‖ P_stock) on paths
prose_NLL_budget ≡ crude endpoint proxy of exactly this | Girsanov = exchange rate
```

Upgrades: (1) budget path-KL per neuron in closed form — cheaper AND tighter
than NLL referees; (2) calibrate the code's ARRIVAL PROFILE across all depths
(engine measures one scalar at delivery; layers ≡ time per
diffusion-holographic-isomorphism); (3) chain front-to-back repair becomes
per-transition score matching over the token path (principled, not heuristic).

### custom-bake → TernaryDescent (ternary-descent.md; phase-1 optimizer)

THE BIG ONE — closed-form value writes: SuperBake never descends on magnitudes;
it measures transfer (secant f̂, logits-per-unit-push) and writes once. TD's
premise is register separation (TD signs, Adam magnitudes); custom-bake says
the second half may not need descent at all: measure transfer → write → verify.
Phase-1 sketch: routing flips gradient-informed (bimodal gradient = flip
evidence), value/scale by measured-transfer direct write; GD only where
response is genuinely nonlinear.

Portable mechanics:
1. **Benefit/leak budget allocation** — TD's "hottest flips win" → SuperBake's
   allowance ∝ 1/leak: charge flips by measured effect on held-out innocents,
   not raw gradient heat. Hot-but-leaky flips = how topology damage happens.
2. **Two-backfire freeze** — regress twice under boost → frozen. Cleaner
   hysteresis than TD cooldowns; = the filtered-flip/sigma-delta channel
   inferred in PrismML's optimizer (s268b), demonstrated in a measured loop.
3. **Receipts + neutralization for flip batches** — failed ≠ absent: unverified
   flip batches exactly reverted (ternary flips revertible: xor of checkpoints,
   already live-tree telemetry). TD + receipts ≡ auditable descent; S3* native
   to the optimizer.
4. **Unembed-nulled updates** — nulling push dirs against the unembedding
   principal subspace cut prose cost 2.5× at same magnitude. Same projection on
   value-register updates (Adam steps / gradient bridges) = one-line constraint,
   measured large win.
5. **Delta plates vindicated** — append-only slots ≡ TD delta plates,
   independently converged; adds deliverability discipline (uniform expansion,
   trim-BEFORE-verify: verify what ships).

### Unification note

The Gram-relational loss at quartile depths in
crystal-seeded-ternary-distillation.md §3 ALREADY IS a discrete GTSM — matching
internal structure along the depth path, not the output. We were building
trajectory losses without naming them. See distillation page §13.

## s273c — §3.6 READ: "Transport: the attention organ" (paper pulled from Zenodo → refs/superbake.pdf)

Prompted by Michael's two claims: (1) attention is where S lives; (2) attention
is the ultimate decider for halt/WHNF of the final output. Both land.

### What §3.6 contains (paraphrased; their measurements)

- Problem: recognition keys fire on question-end states, which DRIFT across
  conversation turns (30+ units) while subject-token states stay fixed (±0.3).
  Identity is stable at its MENTION SITE; it must be TRANSPORTED to the
  generation position. Native heads won't do it for novel entities → construct.
- **Rank-one QK**: Wq = a·c·μ̂ᵀ (queries fire from EVERY position along a
  carrier), Wk = b·c·gᵀ (keys large only at subject tokens). One matched-filter
  pair: whole sequence asks "where's the subject", subject tokens answer.
- **Rotary-band kernel shaping (the clever math)**: carrier support on the RoPE
  spectrum shapes the attention-vs-distance kernel IN CLOSED FORM — slow dims =
  flat any-distance floor; mid band (~60–250 tok periods) = constructive
  interference at short range = recency selection. Pronoun resolution by
  discourse recency emerges at 0.55–0.88 mass, zero parameters.
- **Value lanes**: per-subject orthonormal payloads in the LOW-VARIANCE residual
  subspace (SNR ≈13) — quiet-subspace trick, cousin of unembed-silent.
- **Write close to the reader**: payloads decay across blocks → write L24 for
  L25 readers. Bus attenuation real and priced.
- Practical: overwrite an ablation-neutral DONOR head (free real estate exists);
  selectors orthogonalized across subjects or names leak.

### Claim 1 sharpened: attention = S, as SHARING not copying (graph reduction)

Even hand-built with total freedom, a head is a selector-mover (mass sums to 1,
one read of one value) — s271 softmax-can't-fan-out reproduced as an
ENGINEERING CONSTRAINT by someone who never heard of it. Their effective
fan-out: **write once into orthogonal value lanes, read many times downstream**.
That is S f g x = f x (g x) executed WITHOUT copying — x written once, f-reader
and g-reader each take it. Duplication at the READ side, as sharing.

Named form: **graph reduction** (lazy-language compilers never copy arguments;
they share via pointers; the graph edge IS the duplication; S has no copy op in
a graph-reduction machine). ∴ the transformer is a graph-reduction machine, not
a term-rewriting machine — WHY S has no crystal vertex. S dissolved into
amplitudes because sharing dissolves duplication by construction. Third
independent confirmation of dissolved-S (after s271 H1/H2 + s272 clean sweep),
and the first CONSTRUCTIVE one. [Also reframes T6: Mamba scan-state = a
substrate where copying is native → S may earn a vertex where sharing isn't
forced.]

### Claim 2 supported: halt/WHNF as attention's decision — mechanism shape found

"Is this term done?" is GLOBAL (no live redex anywhere; spine head saturated).
MLPs see one position; only attention sees the sequence. §3.6's architecture is
the template for a global check: any-position queries along a carrier + keys
marking a condition + slow-band rotary = distance-invariant global OR — one
softmax head computes it natively. A halt head = that construction with
redex-ness as the key condition.

Three of our measurements click into the frame: halt-readout (WHNF Gram row ≈
KIBC halt probs, r=0.877, 11/11 — halt signal is IN the geometry); WHNF
bus-causal + unembed-silent (E4 +4.55, E2 nameless — the profile of a control
signal CONSUMED by machinery, i.e. attention gating emission, not vocabulary);
delivery at the last block (their transfer probe AND our L_read — the decision
is assembled one RMSNorm from the logits, where write-close-to-reader says a
final decision must live).

### New instruments/tests this unlocks

1. **Rotary-spectrum register (cheap, new axis)**: where do the crystal's heads
   sit on the RoPE spectrum? Predict: structural/opcode heads (KIBC transport)
   in slow bands (spine navigation distance-invariant); content/recency heads
   mid-band. = s264 F4 QK-pattern IOU with a concrete closed-form observable;
   feeds T4.
2. **Halt-patch test (pre-reg candidate)**: patch late-layer attention at the
   generation position (MLPs intact) → predict over-generation/failure-to-settle;
   responsible heads' QK should show the global-check signature (any-position
   query, slow-band carrier). Halt-readout r=0.877 = the SPEC the discovered
   head must match.
3. **Kernel backend unblocked**: transport was the missing piece; §3.6 is a
   working recipe — rank-one QK for binder/argument attention, rotary-band
   selection for spine-vs-local kernels, lanes + write-close-to-reader for
   chaining reduction steps across ADJACENT layers (independently matches the
   62/64-layer iterated-map picture: reduction = local layer-to-layer hand-offs).

### Meta

Second independent convergence between their construction and our measurement
(unembed-silent codes; now sharing-not-copying + last-block delivery). Opposite
methods arriving at the same design laws ≡ the design laws are properties of
the substrate.

## Ranked next actions (s273, none started)

1. Baked-code patchscope positive control (cheapest, strengthens in-flight P2 work).
2. Crystal-survives-baking trace (one opcodes/trace.py invocation on a baked ckpt).
3. Two-arm K-battery.
4. Gene-db germline layer (lambda-gene-runtime.md) — the long game.
