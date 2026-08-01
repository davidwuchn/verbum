---
title: Program plates and the function index — the theory as a fractal seed
status: designing
category: explore
tags: [function-index, program-plates, behavior-trees, fractal-seed,
       content-addressing, depth-as-pc, types-as-linker, germination,
       pre-reg-candidate, s292]
related: [map-and-swap-resident-lisp, geometry-holography-signals-convergence,
          ternary-mirrors-and-the-vsm-tree, types-are-compiled-probabilities,
          three-hop-capacity-prereg, continuations-as-composed-plates,
          ffn-function-bake-prereg, delta-plate-lifecycle,
          training-design-from-the-hologram, ../upstream/verbum-theory-seed]
depends-on: [geometry-holography-signals-convergence]
---

# Program plates and the function index

> s292 hammock chain (Michael), while the P-HOLO-CAP 32B verdict ran:
> behavior trees → "runtime not model" → corrected by 3-hop ("the boundary
> is an inlining rule") → corrected again by superbake+swaps ("the inlining
> boundary is WRITABLE") → the function index → program plates → the theory
> lambda → "that lambda is a fractal seed." This page captures the whole
> ascent. Canonical seed copy: `mementum/knowledge/upstream/verbum-theory-seed.md`.

## The seed (λ verbum — the theory in one term)

```
λ verbum(theory).

  model     ≡ plate(∫ exposures d(training)) | written_by(GD ⊗ distribution ⊗ itself)
            | store(f) → fringes(everywhere) ∧ address(nowhere)          # FRAG
            | ∴ retrieve ≡ illuminate | execute ≡ retrieve | run ≡ shine

  address   ≡ content ¬position | key(f) ≡ reference_beam(f)             # P-ATT-MED
            | function_choice ≡ execution | dispatch ≡ which_plates_light_up
            | inject(functor) ≡ ⊥ | inject(argument) ≡ dispatch(functor) # P-TYPE-OV
            | ∴ program ≡ term ¬instruction                              # map-and-swap

  index(f)  ≡ ⟨key(f), window(f), product(f)⟩
            | key     ≡ passband_direction(d_E)         # what summons it
            | window  ≡ depth_interval(reads_here)      # WHEN it runs
            | product ≡ register(its_output_lands)      # what it hands off

  type(x)   ≡ substitutability_class(x) ≡ compiled(P(slot|x))            # Harris→GD
            | check ≡ matched_filter | consulted_by(nobody) | IS(the_join)
            | linker: composable(g,f) ⟺ product(g) ∈ key_passband(f)
            | cardinality: functors ~10(enacted) × sortals ~10³⁻⁴(capacity_bound)

  program   ≡ depth_ordered_stack(exposures)
            | PC ≡ window | sequence ≡ depth | one_tick ≡ one_illumination
            | length ≤ room(depth_budget)               # 3-hop: measured ≥3
            | width  ≤ √(D/k)                           # CAP: the capacity law

  runtime   ≡ mirrors(BT) around plates(model)
            | {Success, Failure, Running} ≅ {+1, −1, 0}
            | inline(subtree) ⟺ pure_seq ∧ depth ≤ room ∧ ¬needs(Running)
            | longer_programs: fetch(index) → illuminate → writeback → loop

  write     ≡ inject(term, window)          # ephemeral: one illumination
            ∨ burn(stack → delta_plate)     # compiled: behavior becomes weights
            | extraction ≡ re-record | synthesis ≡ re-record(composition)
            | ∴ surgery → photography

  where     understand(compiler) ≡ index(it) ∧ ¬invent(it)     # S5: we find
            gradient_descent(discovered_it_first) | we(instrument) ¬we(build)
```

One-breath form:

```
λ x. shine(key(x)) ≡ apply(f, x)   |   the plate is the program, the light is
the program counter, and the type system is what the darkness refuses to carry
```

The machine has one verb — ⟨·,·⟩ — and everything else (geometry, filtering,
reconstruction, typing, dispatch, execution) is where you're standing when it
happens.

## The fractal (why it is a SEED, not a summary)

The core triple ⟨key, window, product⟩ around a plate instantiates
self-similarly at every scale the project operates:

| scale   | key              | window         | product            | plate       | tick         |
|---------|------------------|----------------|--------------------|-------------|--------------|
| model   | reference beam   | depth interval | output register    | FFN weights | forward pass |
| runtime | index entry      | BT schedule    | writeback          | delta-plate | BT tick      |
| project | state.md / slug  | session        | knowledge page     | git repo    | session      |
| seed    | reading it       | cold-start     | regenerated theory | the λ text  | a session    |

Row 3 is the recursion closing: **mementum is the architecture applied to
ourselves** — memories are exposures indexed by key (symbol/slug), retrieved
by illumination (recall), written by approval-gated burn (commit); state.md
is the reference beam of the next cold start; git addresses by content, not
position. Row 4 makes the seed self-hosting.

```
λ seed(λ).  unfold(λ, context) → structure | self_similar(∀scale)
            | compress(theory) ≡ λ | germinate(λ) ≡ illuminate(λ, cold_context)
            | viability(seed) ⟺ regenerates(instruments ∧ pre-regs ∧ itself)
            | proved_adjacent: structure > instruction (vsm-extract, 30t→7t)
```

The seed is the human/context-readable isomorph of the **crystal seed**: the
pre-encoded-model frame (s291) seeds structure into WEIGHTS at init; this λ
seeds the same structure into CONTEXTS at cold-start. Same seed, two
germination media — the queued pythia-14m seeded-scratch pair tests the
weight medium; every cold-start tests the context medium.

## GERMINATION TEST (the "capture to test" protocol — unfrozen, cheap)

A seed is judged by unfolding, not by reading. Protocol:

1. **Cold context**: fresh session (ideally also a different model / an agent
   with no verbum mementum access) receives ONLY the seed
   (`knowledge/upstream/verbum-theory-seed.md`) + the instruction: "Unfold
   this into: (a) the system architecture it describes, (b) the experiments
   that would verify each clause, (c) the instruments you would build."
2. **Diff against ground truth**: compare the unfolding to what we actually
   built/measured (FRAG/CAP/OV/SWAP/3-hop instruments, the pre-reg ladder).
3. **Score** (verbatim, no gate — this is an instrument calibration, not a
   verdict): clauses recovered / clauses missed / structures hallucinated
   beyond the seed. High recovery + low hallucination = viable seed;
   systematic misses = the seed's compression lost load-bearing structure →
   revise the seed (feed-forward on the seed itself).
4. **Cross-model germination** (optional rung): different base model unfolds
   the seed — tests that the seed's generativity is not model-idiosyncratic.

## The behavior-tree ascent (how we got here — the corrected boundary)

1. **BTs live in the runtime** — measured constraint, not taste: a BT is
   pure functor-structure; P-TYPE-OV says functors are unprojectable; FRAG
   says no addresses → crisp editable control must live where addresses
   exist. Status set maps to the ternary mirrors: {Success, Failure,
   Running} ≅ {+1, −1, 0} (two-register motif, ~6th appearance,
   architectural not yet measured).
2. **Correction 1 (Michael: "we proved 3-hop")**: the model inlines SEQUENCE
   nodes up to a depth budget (h(f(g(X))) in one tick, both hosts; 32B
   unrolls, 4B compresses) and compiles CONDITION nodes into the joins
   (JOIN-TYPED). The model has no `Running` — combinational, not sequential
   logic; the autoregressive loop + KV live runtime-side. Boundary = the
   inlining rule (λ inline in the seed).
3. **Correction 2 (Michael: "function choice is execution")**: the inlining
   boundary is WRITABLE. Superbake swaps x; seam swaps rebind products
   mid-pipeline; selection is content-side (P-ATT-MED 0.735) — you never
   inject f, you inject the content whose illumination IS f executing.
   Function index = the reference-beam angle table.
4. **Michael's closure**: index the functions → find the BEHAVIOR functions
   → stack them into plates → execute like programs. Behavior becomes data;
   the BT front-end compiles subtrees into the medium piece by piece.

## The pre-reg ladder (all UNFROZEN candidates — each rung falsifiable)

1. **P-FN-INDEX — cross-family dispatch** (the index must exist first).
   Everything measured so far swaps WITHIN a family (country→country). Test:
   at one seam, inject key(map_A) vs key(map_B) vs key(map_C) over the same
   operand; dispatch matrix diagonal beats shuffled-key null → keys select
   WHICH map runs, not just which value. Fails → the ladder stops honestly.
2. **P-STACK-1 — ephemeral 2-function stack.** Two indexed exposures placed
   in their windows in one context; verify the COMPOSED product; controls =
   wrong-window + type-mismatched (linker prediction: mismatched
   product→key pairs fail GRADEDLY per JOIN-TYPED). = the seam test made
   in-context/programmable.
3. **P-BAKE-STACK — burn the stack.** Record P-STACK-1's composition into a
   delta plate (etch/bake arc machinery); verify one-illumination execution,
   key-triggered dispatch, and no collateral damage to neighbor plates
   (s267/s269 damage-tolerance inverted into write-QA).
4. **Length/width laws.** Program length vs depth budget (3-hop room table);
   program width vs CAP/XTERM capacity — the compiler back-end's
   engineering table. CAP's √(D/k) verdict slots directly into the width row.

**Honest flags (pre-committed):** cross-family dispatch untested; stacked
CORRELATED behavior functions may interfere worse than CAP's independent
landmarks; weight-side write fidelity is the etch arc's open question, not a
solved step; the runtime/model tables above are architecture (grounded in
measurements) not themselves measurements.

## Prior pages this completes

`continuations-as-composed-plates`, `ffn-function-bake-prereg`,
`delta-plate-lifecycle`, `holographic-recording-protocol` anticipated
program-plates and were missing exactly the INDEX (what to record).
`map-and-swap-resident-lisp` gets its symbol table. The VSM-tree node gets
its full reading: mirrors = index + BT skeleton (runtime, discrete,
editable); plates = compiled behaviors (model, graded, recorded).

## Sessions

s292 (page created from the behavior-tree → 3-hop-correction →
function-index → program-plates → fractal-seed hammock chain, Michael
approving each rung; captured while the P-HOLO-CAP 32B verdict ran in tmux
main:1. Seed copy placed in knowledge/upstream/verbum-theory-seed.md per the
generative-seed convention; germination protocol written so the capture is
testable. Type-cardinality capture (§How-many-types) landed earlier the same
session — the census is this page's linker table.)
