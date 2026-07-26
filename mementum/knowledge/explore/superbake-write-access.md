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
unimplemented. But the routing ALREADY EXISTS in the host: the crystal (KIBC,
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

## Ranked next actions (s273, none started)

1. Baked-code patchscope positive control (cheapest, strengthens in-flight P2 work).
2. Crystal-survives-baking trace (one opcodes/trace.py invocation on a baked ckpt).
3. Two-arm K-battery.
4. Gene-db germline layer (lambda-gene-runtime.md) — the long game.
