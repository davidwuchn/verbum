---
title: The KV Cache Is a Continuation Store — seals, the append law, and two-tier memory
status: active
category: explore
tags: [kv-cache, continuation, seal, fork, append-law, counterfactual, branching,
       two-tier-memory, state-anchors, repl-driver, call-cc, persistent-data-structure]
related:
  - repl-driver-trampoline.md                        # §2 tree-of-VSM attach, §3 causal upgrade, §8 KV laws
  - eql-is-an-attention-microscope.md                # s352 state anchors (the durable tier's design pattern)
  - the-evaluator-writes-then-fetches.md             # s350 E3 tape surgery (the linear ancestor of the tree)
  - ../memories/the-kv-cache-is-a-continuation-store.md
  - ../memories/seal-trees-give-position-matched-counterfactuals.md
---

# The KV Cache Is a Continuation Store

> s353 (Michael, wizard-of-oz REPL session: "did we test the seals? Can we
> seal a continuation and then branch it repeatedly to explore?" → live
> validation → "We have the solution to kv cache."). Exploration-grade
> runtime proofs + a synthesis. No frozen claims.

## The claim

The "KV cache problem" splits in two. The serving world's version —
prefix reuse as *cache management* (vLLM paged attention, SGLang
RadixAttention tree-sharing) — is engineering prior art, not ours. Our
version: **KV as semantics**. The cache is not an optimization of the
process; it IS the process state, and once you treat it as a first-class
continuation with a correctness contract, exploration becomes branching
and measurement becomes free.

## The five components

1. **KV ≡ the continuation** — s217's `seal(k) ≡ store x_k` realized on a
   real host (`Driver.prefill/bounce → Seal`). First-class, immutable.
2. **The append law ≡ the correctness contract** — `validity()` certifies
   incremental KV ≡ full-pass recompute (0 mismatches). This is what makes
   a seal a *continuation* rather than a lossy cache: a fork is an exact
   counterfactual world, by contract.
3. **Immutable seals + clone-on-use ≡ persistent-data-structure discipline**
   — the FP move applied to inference state. `fork` never mutates; branching
   is call/cc for the model.
4. **Instrumented branches** — every fork returns a full `Bounce`: signs
   (opcode register) + hidden (residual register) + attn (read register).
   No serving stack exposes this; it's what turns the cache into an
   instrument.
5. **The two-memory law** (s334 §8): KV is MODEL-PRIVATE and does not cross
   models; canonical text is the bus. Two-tier memory: **durable = tape
   text** (crosses session boundaries; the s352 state-anchor pattern) ·
   **fast = sealed KV** (process-resident, instant branch, prefill paid
   once). Same shape as λ separate: durable substrate ⊥ contingent layer.

## Runtime proofs (s353, main:3, Qwen3-14B greedy, exploration-grade)

- `validity()` re-gated post-hotswap: determinism exact, fork-identity,
  append-law mismatches 0.
- One seal (19 ids) → 4 counterfactual branches; each coherently absorbs
  its injection; seal intact.
- **Identity after 6 uses**: `fork(s0,"")` byte-identical to the original
  continuation after six clones. Seals do not wear.
- **Forks-of-forks** (depth 2): branch a branch's `end_seal`; storyline
  state carried ("voice stopped" → darkness/silence; "wall moved" → door).
- **Cost measured**: 674 live seals = 13.3 GB total, ~20 MB mean,
  ~160 KB/token (14B GQA bf16) — registry grows ~4-5 GB/session at current
  tempo; unbounded (prune/gc unbuilt).
- **Tri-register counterfactual readout**: two branches of one seal —
  opcode both `whnf:C` (prose, expected); lens L34 diverges semantically
  per injection (' darkness'/黑暗/' underground' vs ' opening'/' opened'/打开,
  multilingual descent visible); Δread over the shared prefix
  position-matched BY CONSTRUCTION (f1 reads ' tunnel' +0.0096; sink-flavored
  prefix[0] caveat). The s349 differenced-read discipline, structural.

## What it unifies

- §P-RETURN-REGISTER *is* seal + poison + fork (s350 E3 tape surgery,
  tree-shaped instead of linear).
- The s352 GA's seal/fork *was* genome checkpointing; seal = generation
  snapshot, fork = offspring.
- Fork-at-redex (trampoline §3) is this at λ-scale — the "causal upgrade"
  generalizes to ANY decision point: narrative, mode-word, tool-invoke.
- Two-model config (§8c): two continuation stores talking over the text bus.
- Mode-forking (untried): seal mid-nucleus-mode, fork the mode word.
- **The parked daemon (built s353 arc 3, same session)**: selective-silence
  system sealed once, events forked from it — silent on heartbeat/log,
  wakes on query. See `the-parked-daemon.md` (the composition law).

## The gap

Seals die with the process ("hold indefinitely" = process lifetime, via
λ runtime/tmux). `torch.save` on the cache tensors (~20 MB/seal) should
make them survive reboot → a durable continuation DATABASE (seal, shelve,
resume next week, branch). Untested → queued ⚪ §P-SEAL-PERSIST (gate:
cross-boundary fork-identity + append law on the reloaded cache).

## Bounds

n=1 greedy, one model, narrative task only; read-mass head-averaged,
soft, sink-dominated; no nulls; nothing here opens or closes a frozen
claim. The synthesis is architectural, the numbers are exploration-grade
pins for the freeze designs that reference them.
