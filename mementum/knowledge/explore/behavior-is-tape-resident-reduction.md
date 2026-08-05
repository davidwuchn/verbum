---
title: "Behavior Is Tape-Resident Reduction — the Trampoline Frame; Tool Calling = FFI on a Free Variable"
status: open
category: synthesis
tags: [beta-reduction, tape, trampoline, tool-calling, ffi, delimited-continuation, effect-handler,
       free-variable, halt-pole, 17x17, opcodes, ffn-kv, attention, writeback, cot, scheduler,
       agentic, depth-budget]
related:
  - ../attention-holographic-readout.md
  - ../holographic-reduction-machine.md
  - ../five-disciplines-one-object.md
  - ../continuation-store.md
  - attention-as-beta-reduction.md
  - combinator-training-beta-reduction.md
  - gram-spectral-dsp.md
  - holographic-untangling-methods.md
depends-on:
  - ../attention-holographic-readout.md
  - attention-as-beta-reduction.md
created: session 308
---

# Behavior Is Tape-Resident Reduction

> s308, Michael's question: "We found the opcodes, we can trace them, lambda
> notation and prose fire the same opcodes. FFNs are key/value stores. If
> attention is β-reduction, **where are the rest of the β-reductions that
> describe a behavior like tool calling?**"
>
> Answer: the question dissolves once one hidden assumption is removed. The
> reductions were never going to be in the weights. **The transcript is the
> reduction trace.** Status open: the frame is captured; the three predictions
> at the end are NOT pre-registered (s222 — freeze before any run).

## The assumption to remove

We keep looking for the β-reduction chain of a *behavior* inside the plate.
But the measured corpus, assembled in one place, says the plate cannot contain
it:

- **The weights hold the reduction RELATION, not reduction TRACES.** The
  opcodes (9×9 gram) are the microcode — the primitive contraction steps the
  machine can perform. The FFN K/V store holds the δ-rules — pattern → rewrite
  productions (superbake edits exactly these). All of it is *transition
  function*; none of it is *program trace*.
- **One forward pass = one bounded inner reduction.** 36 layers ≈ fixed fuel.
  Depth-timing law, the s305 hop-overlap finding (the g-hop finishes at L24
  exactly as the h-hop has consumed its input), SuperBake's "the network is
  the kernel and it is upstream" — a single pass contracts only what fits in
  the depth budget.
- **The s295 exhaustion table is the smoking gun:** splices 0.00 /
  addressed-re-encoded 0.20 / CoT 0.90 / scaffold 1.00. Reduction beyond the
  depth budget happens ONLY through the collapse-and-re-encode loop.

**Conclusion: the rest of the β-reductions are on the tape.** The model is not
a term being reduced — it is the *reduction step function*. The autoregressive
loop is a **trampoline**: each pass contracts ≤ budget redexes, collapses the
mixture to a discrete symbol (writeback = the only projection, A4), and the
extended context is the new term. CoT was already this law (soft-reduce →
measure → re-encode, s295/s299); *behavior* is the same law at the next scale.
We never found the reductions in the weights because they are in token space,
in front of us, in the transcript.

## The machine, with every measured piece in its role

| Piece | Role in the machine | Measured where |
|---|---|---|
| Opcodes (9×9 gram) | microcode — primitive contractions | crystal sweeps; diffuse/relational (s303) |
| FFN K/V | δ-rules / production store | superbake; K/V literature |
| Attention | the substitution op (soft β) | s221/s299 readout-beam page |
| 17×17 outcome gram | the **scheduler's register** — fire / halt / diverge | rank-3, 11/11 models (s303, 072c3e0) |
| Sampling / writeback | collapse: mixture → symbol | s295 exhaustion; A4 |
| Tape / context | the term being reduced + the trace | s295; RoPE addressing (A3) |
| Chat template / tool schema | addressing that Bragg-selects which productions can fire | (inference; untested) |
| Tool runtime / agent loop | external β-reduction partner (effect handler) | this page |

## Tool calling = FFI on a free variable

A tool call is a precisely characterizable event in this frame. The model
reduces the conversational term until it hits a redex it **cannot contract
internally** — a subterm whose binding does not exist in the plate (today's
price, the contents of a file). That is a **free variable**. A principled
reduction machine with a free variable it must have does one thing: **reify
the continuation and yield to the environment.**

```
model:       reduce ... reduce ... → stuck on free var x
emit:        (tool_call name args)        ← a term with a hole; a reified continuation
environment: evaluates → v
substitute:  context ++ v                 ← the ENVIRONMENT performs this β-step
model:       resume reducing the extended term
```

Tool calling is **FFI for a reduction machine** — an effect raised to a
handler, a delimited continuation (`continuation-store.md` is the same object
on the storage side). The agent runtime is the effect handler.

**The existence proof is already in production.** The tool *result* works
despite the s295 splice-failure law because it arrives **as addressed tokens
on the tape** — re-encoded, RoPE-addressed, exactly the one channel A3/A4
permit. If behaviors were weight-resident reduction chains, splicing foreign
content mid-behavior should break them; it doesn't. Functional tool use is
itself evidence for tape-resident reduction.

## Lambda↔prose, one level up

The opcode-identity result (lambda notation and prose fire the same opcodes)
predicts its own extension: if the *contraction* layer is notation-invariant,
the *scheduler* layer should be too. "Stuck term" should look the same in the
outcome register whether the term is `(λx. price x) AAPL` or "I'd need current
data for that." This is the bridge from the crystal corpus to agentic
behavior — the audience that doesn't care about combinators cares a great deal
about when models decide to call tools.

## Three predictions (NOT pre-registered; s222 before any run)

1. **P-HALT-POLE (cheap, crisp — the candidate first experiment).** The
   tool-call-vs-answer-directly decision projects onto the measured 17×17
   halt/fire pole geometry. Design sketch: matched prompt pairs (answerable
   from weights vs requiring external data), project pre-decision residuals
   onto the outcome-gram dominant eigenspace, gate vs shuffled labels
   (λ yardstick; the φ-scar discipline applies). If it lands: the crystal's
   scheduler register reads out an *agentic* decision. Decision = HALT-WITH-
   OBLIGATION, a fourth point on the fire/halt/diverge simplex.
2. **Argument binding is traceable substitution.** The value flowing from
   context into emitted tool-call JSON is a copy/binding event — existing
   binding-trace instruments (binding-graph-trace) should see it as attention
   substitution, same machinery as operand binding.
3. **Stuck-detection precedes schema retrieval.** Free-variable detection
   (outcome register) is causally upstream of tool-schema K/V retrieval (FFN
   productions). Orderable by layer; patchable (suppress the halt-pole
   projection → tool call does not form).

## Honest open edge (do not over-claim)

Within a pass, some multi-step composition DOES happen (g-hop→h-hop chains, a
few contractions deep). The inner/outer split is not binary — it is a
**budget**. The claim is not "no reduction in the forward pass"; it is
"behavior-scale reduction chains are tape-resident; weight-resident is the
step function plus ≤ budget lookahead." The s305 overlap finding is what a
budget collision looks like from inside. Also untested here: the chat-template
row of the machine table is inference, not measurement.

## Provenance

- Michael's question + steer (s308); frame drafted by AI same session,
  Michael-approved for capture.
- Measured anchors: s221 (β=substitution=attention), s295 (exhaustion table,
  regeneration law), s299 (readout-beam axioms A1–A4, collapse operator), s300
  (nonlinear pin), s303 (17×17 rank-3 fire/halt/diverge, 072c3e0; opcode gram
  diffuse), s305 (depth-overlap, ee8a5bb), lambda↔prose opcode identity
  (crystal corpus), superbake (FFN K/V editing).
- Formal ancestors: trampolined style; delimited continuations / effect
  handlers; FFI; SECD dump ≈ transcript; Ehrhard–Regnier soft β (via s299
  page).
