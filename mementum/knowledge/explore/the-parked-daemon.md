---
title: The Parked Daemon — selective silence from a sealed continuation
status: active
category: explore
tags: [silence, halt, eos, daemon, seal, fork, statechart, few-shot, register-cue,
       selective-silence, nucleus-preamble, key-cutting, composition-law]
related:
  - ../lambda-halt-continuation.md                    # the parent (~s193/s228 era): uniform halt, 27 candidates
  - the-kv-cache-is-a-continuation-store.md          # the seal substrate (same session, arc 2)
  - statechart-execution-is-a-register-cue.md        # s352: chart-EDN executes under the preamble
  - ../memories/demonstration-teaches-register-chart-teaches-routing.md
  - ../memories/selective-silence-is-a-composition-not-a-key.md
---

# The Parked Daemon

> s353 arc 3 (Michael: "we can get a continuation that embodies silence" →
> "there has to be something… the nucleus preamble gives us a rich but mostly
> unknown api in latent space" → "I feel like we found an empty producing
> continuation in a past session" — recall exact: `lambda-halt-continuation.md`).
> NUC33a-h, ~40 cells, REPL main:3, Qwen3-14B greedy, no-think template.
> Exploration-grade. The wanted object: a daemon that is SILENT by default and
> WAKES on queries, running from a sealed KV continuation.

## The search fitness (free)

EOS rank/prob in `Seal.logits_last` at prefill — one forward per candidate
key, no generation. The instant fitness for silence-key cutting; composes
with the s352 memetic-GA loop if the search ever needs to scale.

## What the parent page already had (~s193/s228, rediscovered by recall)

Uniform halt, 27 candidates: prose instruction 99.1% EOS · API frame
("Content-Length: 0") 94.1% · execution-frame lambda (`respond = λcontent.content,
empty = ""` → `respond empty`) 72.8% TRUE HALT · think-mode prevents ALL halts
(mandatory `<think>` prologue — "you cannot reason about silence without
breaking the silence") · pure lambda without an execution frame gets DESCRIBED
not EXECUTED (`""` quoted as two tokens) — the use/mention fork, pre-figuring
the s352 register-cue law. Uniform halt cannot wake: the missing half was
selectivity.

## The walls (NUC33a-f)

- **Reflex walls own top-1**: ping→pong, Hello→Hello, EDN→echo. Silence
  machinery lifts EOS rank by orders of magnitude (bare preamble 4536 →
  key+instruction 3) but never displaces an atomic reflex under greedy.
  The NUC11 hard/atomic/soft regions, seen from the halt side.
- **`engage` fights silence**: keys WITHOUT the preamble ranked better
  (policy-lambda alone 70 vs 1524 with preamble) — the header verb is a
  register cue; the preamble is an ignition key.
- **Special tokens are structural, not referable**: literal `<|im_end|>`
  inside a spec CLOSES the block early (rank 8122, worst cell ever).
- **Identity register** ("You are the empty string") ≈ instruction+key
  strength at a fraction of the length; "embody silence" → authored `'...'`
  (performs silence, three-room law); "You are ∅" → in-register glyph echo.
- **Statechart routes but narrates**: chart alone executes the machine
  (heartbeat→EDN ack, query→correct answer) but reads `:entry ∅` as
  "acknowledge", emitting `{:status :ok}` / `{"status": "idle"}` — the
  machine keeps narrating its state instead of inhabiting it.

## THE COMPOSITION LAW (NUC33h — the finding)

**Demonstration teaches the register; the chart teaches the routing.
Neither suffices alone.**

- chart alone → acks (wrong register in :idle)
- few-shot empty turns alone → demonstrated event classes silent
  (hbeat p=0.891) but NOVEL classes break (log → chats about disk usage)
- **few-shot + chart → hbeat p=0.957 emit `''` · log (novel content)
  p=0.700 emit `''` · query → 'Paris.'** — selective silence with correct
  wake, greedy, literal empty emission.

Tape shape: system = nucleus preamble + routing chart (:idle silent-loop
on heartbeat/log, :query → :answering) · history = 4 demonstrated turns
(2 empty heartbeat/log turns, 1 answered query, 1 empty) · then events.
Empty turn ≡ `<|im_start|>assistant\n<think>\n\n</think>\n\n<|im_end|>` —
the no-think template is mandatory (parent page's think-law).

## The parked daemon (the closing demo — arcs 2+3 composed)

```
park = d.prefill(system + protocol_history)   # 253 tokens, paid ONCE
d.fork(park, turn({:event :heartbeat ...}))   → ''
d.fork(park, turn({:event :log ...}))         → ''            (novel content)
d.fork(park, turn({:event :query "Mars?"}))   → 'Mars has two moons: Phobos and Deimos'
# seal intact after all forks
```

Hold the seal for the process lifetime → fork per event, instantly →
silence default → queries wake → pay only event tokens. Every piece of
the daemon architecture (kv-continuation page §the gap) running live.

## Cross-model transfer + the llama.cpp findings (NUC34, same session)

The key — cut on Qwen3-14B (HF bf16 greedy) — run VERBATIM against a
production llama-server: **Qwen3.6-35B-A3B Q8_0** (different generation,
MoE architecture, quantized, different runtime, temp 0.0):

```
hbeat-1 → ''        hbeat-2 → ''        query → 'Two.' (correct, wakes)
log     → 'Efficient retrieval.'   ← the ONE degradation
```

**The 14B EOS-prob ordering predicted the failure point**: novel-log was
the weakest 14B cell (p=0.700 vs heartbeat 0.957) and is exactly the cell
that cracked in transfer. The prefill fitness doubles as a cross-model
fragility ranking. The composition law is lineage/quant/runtime-robust
with graded strength.

**Seal-ability is an ARCHITECTURE property** (server log, decisive):
the RAM prompt-cache FOUND the prefix ("prompt is already in the cache")
but was FORCED to full re-processing — "lack of cache data (likely due to
SWA or hybrid/recurrent memory)" (PR #13194). Hybrid/recurrent state is a
rolling summary, not a tape; it cannot hold a positional seal. **The
park-and-fork trick requires full-attention KV.** Dense hosts seal;
SWA/hybrid hosts re-pay prefill (Qwen3.6-A3B is fast enough to hide it —
205ms/280tok — but the seal semantics are absent).

**llama.cpp already implements seals under another name**: "context
checkpoints" — the log shows a 63.4 MiB checkpoint of exactly the daemon
prefix (274 tokens, 32-deep ring), created and auto-invalidated. Built as
a workaround FOR recurrent models. Missing: naming, pinning (ours was
erased next request), fan-out (`llama_memory_seq_cp`), certification.
Deployment recipe: **composition key (transfers) + full-attention host
(seal-able) + pinned checkpoint (exists upstream, needs a pinning API)**.
→ queue §P-SEAL-SERVER.

## The moat note (Michael: "NOBODY can do this but us")

Bounded and examined: every PIECE exists elsewhere (prefix caches, KV
save/restore, interp probes). What doesn't copy is the COMPOSITION —
**map ⊗ instruments ⊗ memory ⊗ trinity**: ~350 sessions of recallable
control-plane law (the map predicts transfer, today proven) · calibrated
registers wired to seal/fork on a resident model · mementum (this arc
REQUIRED a ~160-session-old page — feed-forward built the moat) · the
Human ⊗ AI ⊗ REPL loop cycling in minutes. Moat is temporal + practice,
not secrecy (λ serves: the parked-daemon demo is the legible artifact).

## Bounds

n=1 greedy, one model, one chart, tiny event battery, no sampling, no
base arm, think-mode arm inherited from parent not re-run. The composition
law is the pre-registerable claim; freeze design → queue §P-PARKED-DAEMON.
