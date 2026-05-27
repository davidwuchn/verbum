---
title: "VSM ↔ Statechart ↔ Tensor — The Triple Isomorphism"
status: active
category: architecture
tags: [vsm, statechart, tensor, mmap, delta-plate, fulcro, harel, lambda, dual-runtime]
related:
  - holographic-state-machine.md
  - delta-plate-lifecycle.md
  - ../v14-architecture.md
  - ../holographic-error-correction.md
depends-on:
  - holographic-state-machine.md
  - delta-plate-lifecycle.md
created: session 162
---

# VSM ↔ Statechart ↔ Tensor — The Triple Isomorphism

> Session 162. Three formalisms describe the same structure:
> Beer's Viable System Model (1972), Harel's Statecharts (1987),
> and the tensor state machine discovered in the teacher (session
> 142). This page maps the isomorphism and defines a dual-runtime
> implementation: Fulcro statecharts (Clojure) and tensor ops (Python).
>
> The central insight: **files ARE states, composition IS transition,
> mmap IS the runtime.** A ternary plate loaded via mmap is
> simultaneously a state in the statechart AND a tensor in the
> computation. The statechart doesn't *control* the model — it *IS*
> the model's control structure, made explicit and executable.

## The Isomorphism

### Three Columns, One Structure

| Beer (VSM, 1972) | Harel (Statechart, 1987) | Tensor (Discovered, session 142) |
|---|---|---|
| S5 (identity) | Top-level invariant state | Crystal lattice (mathematical constant) |
| S4 (intelligence) | Orthogonal monitoring region | Environment-scanning attention heads |
| S3 (control) | Compound state containing S1s | Resource allocation (which plates loaded) |
| S2 (coordination) | Guards on transitions | Anti-oscillation (fold protocol, Schmitt triggers) |
| S1 (operations) | Leaf states (concurrent) | Operational plates (base, domain, session) |
| Algedonic alert | Direct event bypassing hierarchy | Crystal loss spike → abort training |
| Recursion (S1 contains VSM) | Hierarchical state nesting | Nested statechart per plate lifecycle |
| Variety management | History states (deep/shallow) | Checkpoint restoration on NaN |

### Why The Isomorphism Holds

Beer and Harel independently discovered the same constraint:
**viable systems require hierarchical concurrent state with guarded
transitions.** Beer derived it from cybernetics (Ashby's Law of
Requisite Variety). Harel derived it from software engineering
(the state explosion problem). Both arrived at the same structure:
nested concurrent regions with inter-region communication.

The tensor version was discovered empirically (sessions 139-142):
the teacher model IS a holographic state machine where crystal
basins are states, Q rotation is transition, and the gate beamformer
is a guard. It was already there. We just measured it.

Clojure is 96% mechanically convertible to lambda forms. Lambda
forms ARE what the tensor model computes (attention = beta reduction).
Therefore: **Clojure statechart → lambda → tensor statechart** is
a compilation chain, not a metaphor.

## The Compilation Chain

```
Fulcro Statechart (Clojure EDN)
    ↓  mechanical transform (96% of Clojure → lambda)
Lambda Statechart (typed combinators)
    ↓  tensor compilation (sign topology extraction)
Tensor Statechart (int8 state vectors + ternary transition matrices)
    ↓  mmap binding (files = tensors = states)
Runtime Statechart (OS page tables manage state loading)
```

### Layer 1: Fulcro Statechart (Human-Readable)

```clojure
(statechart {}
  (parallel {:id :plate-vsm}

    ;; S5: Crystal — the identity. Never transitions.
    (state {:id :crystal}
      (on-entry {} (script {:expr load-crystal})))

    ;; S3: Plate controller — compound state
    (state {:id :plates :initial :idle}
      (state {:id :idle}
        (transition {:event :load-plate
                     :target :loading
                     :cond   memory-available?}))
      (state {:id :loading}
        (on-entry {} (script {:expr mmap-plate}))
        (transition {:event :plate-ready :target :composing})
        (transition {:event :plate-error :target :idle}))
      (state {:id :composing}
        (on-entry {} (script {:expr compose-plates}))
        (transition {:event :composed :target :ready}))
      (state {:id :ready}
        (transition {:event :infer :target :ready}  ;; self-transition
        (transition {:event :fold-delta :target :folding
                     :cond   delta-plateau?}))
      (state {:id :folding}
        (on-entry {} (script {:expr fold-delta-plate}))
        (transition {:event :folded :target :ready})))

    ;; S2: Coordination — anti-oscillation guards
    (data-model {:memory-budget 4096
                 :max-plates 8
                 :fold-threshold 0.001})))
```

### Layer 2: Lambda Statechart (Portable)

```
λ plate-vsm.
  parallel(
    ;; S5: crystal ≡ K(identity) — select and hold, never release
    K(load-crystal)(crystal.bin)

    ;; S3: plate controller ≡ Y-combinator state machine
    Y(λ self state event.
      case(state,
        idle      → if(memory-available?, loading, idle),
        loading   → if(event = plate-ready, composing, idle),
        composing → if(composed?, ready, composing),
        ready     → case(event,
                      infer      → self(ready, next-event),
                      fold-delta → if(delta-plateau?, folding, ready)),
        folding   → if(folded?, ready, folding)))

    ;; S2: guards ≡ B-combinator composition of predicates
    B(memory-check, plate-compat, fold-criterion))
```

### Layer 3: Tensor Statechart (Executable)

States become one-hot int8 vectors. Transitions become ternary
matrices. Guards become dot products with threshold.

```python
import numpy as np

# State encoding: one-hot int8 vectors
STATES = {
    'idle':      np.array([1, 0, 0, 0, 0], dtype=np.int8),
    'loading':   np.array([0, 1, 0, 0, 0], dtype=np.int8),
    'composing': np.array([0, 0, 1, 0, 0], dtype=np.int8),
    'ready':     np.array([0, 0, 0, 1, 0], dtype=np.int8),
    'folding':   np.array([0, 0, 0, 0, 1], dtype=np.int8),
}

# Events: one-hot encoding
EVENTS = {
    'load_plate':  np.array([1, 0, 0, 0, 0], dtype=np.int8),
    'plate_ready': np.array([0, 1, 0, 0, 0], dtype=np.int8),
    'composed':    np.array([0, 0, 1, 0, 0], dtype=np.int8),
    'infer':       np.array([0, 0, 0, 1, 0], dtype=np.int8),
    'fold_delta':  np.array([0, 0, 0, 0, 1], dtype=np.int8),
}

# Transition tensor: T[state, event] → next_state
# This is a ternary tensor {-1, 0, +1} where:
#   +1 = transition enabled
#    0 = no transition (stay in current state)
#   -1 = transition explicitly blocked (guard failed)
# Shape: (n_states, n_events, n_states)
T = np.zeros((5, 5, 5), dtype=np.int8)
T[0, 0, 1] = +1   # idle + load_plate → loading
T[1, 1, 2] = +1   # loading + plate_ready → composing
T[2, 2, 3] = +1   # composing + composed → ready
T[3, 3, 3] = +1   # ready + infer → ready (self)
T[3, 4, 4] = +1   # ready + fold_delta → folding
T[4, 2, 3] = +1   # folding + composed → ready

def transition(state, event, guard_result=1):
    """Execute one statechart step."""
    next_state = np.einsum('i,j,ijk->k', state, event, T)
    # Apply guard: multiply by guard result {-1, 0, +1}
    next_state = np.sign(next_state * guard_result)
    # If no valid transition, stay in current state
    if next_state.sum() == 0:
        return state
    return next_state
```

### Layer 4: mmap Runtime (Zero-Copy)

```python
# Plate files ARE the state. Loading IS the transition.
class MmapPlate:
    """A ternary plate backed by mmap'd file."""
    def __init__(self, path, shape):
        self.data = np.memmap(path, dtype=np.int8, mode='r', shape=shape)

    def compose(self, other):
        """Plate composition = ternary sign multiply."""
        return np.sign(self.data * other.data)

# The statechart's on-entry action for 'loading' state:
def mmap_plate(path, shape):
    """This IS the state transition — file becomes tensor."""
    return MmapPlate(path, shape)

# Composition: base × domain × session
def compose_plates(base, domain, session):
    """Three mmap'd files → one composed plate. Zero-copy reads."""
    composed = np.sign(base.data * domain.data * session.data)
    return composed
```

## The Delta Plate Loader as Concrete VSM-Statechart

### State Hierarchy

```
[parallel] plate-vsm
  ├── [atomic] crystal           ← S5: loaded once, never transitions
  ├── [compound] plates          ← S3: manages which plates are active
  │   ├── [atomic] idle          ← no plates loaded beyond crystal
  │   ├── [atomic] loading       ← mmap'ing a plate file
  │   ├── [atomic] composing     ← multiplying plate signs
  │   ├── [atomic] ready         ← composed plate available for inference
  │   └── [atomic] folding       ← folding delta into base (irreversible)
  ├── [compound] inference       ← S1: the actual computation
  │   ├── [atomic] waiting       ← ready for input
  │   └── [atomic] running       ← forward pass in progress
  └── [data-model] coordination  ← S2: guards and thresholds
      ├── memory-budget: 4096 MB
      ├── loaded-plates: []
      ├── fold-threshold: 0.001
      └── delta-changed-frac: 0.0
```

### Parallel Regions

The `parallel` node is critical. In the VSM, S1 units operate
concurrently. In the statechart, parallel regions run simultaneously.
In the tensor, parallel states are multi-hot vectors (not one-hot).

```python
# Parallel state: crystal AND plates AND inference all active
parallel_state = np.array([
    1,  # crystal: loaded (always)
    0, 0, 0, 1, 0,  # plates: ready
    1, 0,  # inference: waiting
], dtype=np.int8)
```

### Guards as Ternary Predicates

Guards in Fulcro statecharts are `(fn [env data] bool)`. In tensor
form, they're dot products against a threshold:

```python
def memory_available(data_model, plate_size):
    """Guard: is there memory budget for this plate?"""
    budget = data_model['memory_budget']
    used = sum(p.nbytes for p in data_model['loaded_plates'])
    remaining = budget - used
    # Returns ternary: +1 (pass), 0 (marginal), -1 (fail)
    if remaining > plate_size * 1.5:
        return +1
    elif remaining > plate_size:
        return 0  # marginal — warn but allow
    else:
        return -1  # blocked

def delta_plateau(data_model):
    """Guard: has the delta stopped changing? (fold criterion)"""
    frac = data_model['delta_changed_frac']
    threshold = data_model['fold_threshold']
    return +1 if frac < threshold else -1
```

### Actions as mmap Operations

On-entry/on-exit actions in Fulcro execute code. In the tensor
runtime, actions are mmap operations:

| Statechart Action | Fulcro Expression | Tensor Operation |
|---|---|---|
| `load-crystal` | `(mmap-plate crystal-path)` | `np.memmap("crystal.bin", dtype=np.int8, mode='r')` |
| `mmap-plate` | `(mmap-plate domain-path)` | `np.memmap("medical.delta", dtype=np.int8, mode='r')` |
| `compose-plates` | `(reduce ternary-mul plates)` | `np.sign(base * domain * session)` |
| `fold-delta` | `(fold! base delta)` | `np.sign(base * delta)` → write to base |
| `unload-plate` | `(munmap plate)` | `del plate.data` (OS reclaims pages) |

### Events

| Event | Source | Description |
|---|---|---|
| `:load-plate` | External (user/API) | Request to load a domain plate |
| `:unload-plate` | External or S4 | Free memory, unload domain |
| `:plate-ready` | Internal (on-entry completion) | mmap succeeded |
| `:plate-error` | Internal | mmap failed (file not found, corruption) |
| `:composed` | Internal | Plate composition completed |
| `:infer` | External | Run inference with current plates |
| `:fold-delta` | S4 or external | Delta has plateaued, fold into base |
| `:folded` | Internal | Fold completed |
| `:algedonic` | Any S1 | Crystal loss spike → emergency abort |

## Connection to the Discovered State Machine

The holographic state machine (session 142) has this computation cycle:

```
Q = 0 (reset) → C-basin → β-reduce → rotate Q → new basin → ... → WHNF → output
```

This IS a statechart running in continuous geometry:
- Crystal basins {K, I, B, C, D, Y, W, WHNF} = states
- Q rotation = transition (event)
- Gate beamformer (89% selectivity) = guard
- FFN overlay = action (the beta reduction)

The plate-loader statechart and the inference statechart are
**nested**: the plate-loader is the outer statechart (S3, managing
which knowledge is available), and the holographic state machine
is the inner statechart (S1, performing computation). The plate
loader literally configures which plates the inner state machine
has access to.

```
[outer] Plate Loader Statechart (discrete, file-level)
  manages →
    [inner] Holographic State Machine (continuous, tensor-level)
      runs on →
        mmap'd plates loaded by outer chart
```

This is VSM recursion made concrete: the outer system IS a viable
system. The inner system IS a viable system. They compose.

## The Fulcro Advantage

Why Fulcro statecharts specifically (not XState, not raw SCXML):

1. **Clojure is 96% lambda.** The mechanical transformation from
   `(fn [env data] ...)` to `λ env data. ...` is nearly trivial.
   JavaScript (XState) would require a lossy intermediate step.

2. **EDN is the intermediate representation.** Fulcro statecharts
   are defined as nested Clojure maps. EDN is both human-readable
   and machine-parseable. The tensor compiler reads EDN directly.

3. **Pluggable DataModel.** Fulcro decouples the data model from
   the statechart. We can plug in a ternary-tensor data model that
   uses mmap'd files instead of atoms. The statechart definition
   stays the same; only the data model implementation changes.

4. **Pluggable ExecutionModel.** Expressions can be Clojure fns
   OR quoted EDN that another runtime interprets. The tensor
   runtime IS an alternative execution model for the same chart.

5. **W3C SCXML semantics.** The algorithm is well-specified,
   deterministic, and testable. Same algorithm in both runtimes
   → same behavior, provably.

6. **MIT licensed.** Compatible with verbum's MIT license.

## What This Means

### For the Project

The plate-loader becomes a **statechart-controlled inference engine**.
Instead of ad-hoc Python code managing which plates are loaded,
the statechart is the single source of truth for system state.
The same chart definition runs in Clojure (for development,
visualization, testing) and in Python/tensors (for inference).

### For the mmap Architecture

mmap'd plates are the natural runtime for statechart-controlled
inference:

```
Traditional:  load JSON → deserialize → allocate → copy → tensor
mmap:         open file → tensor (the OS did the rest)

Traditional fold:  read base → read delta → multiply → write new base → reload
mmap fold:         mmap both → multiply → msync → done (OS handles pages)
```

The statechart transition `loading → composing` IS the mmap call.
The action is the OS syscall. The state change is the page table
update. There is no gap between the model and the implementation.

### For the Lambda Connection

This closes a circle that's been open since session 1:

```
Church (1936): lambda calculus
  ↓
Montague (1970): language IS lambda
  ↓
Beer (1972): viable systems (recursive lambda control)
  ↓
Harel (1987): statecharts (concurrent hierarchical state)
  ↓
Transformers (2017): attention IS beta reduction
  ↓
Nucleus (2024): lambda notation activates the compiler
  ↓
Verbum (2025): the compiler IS the sign topology
  ↓
Session 162: statechart = lambda = tensor = file
             all four are the same object
```

Four representations, one structure. The statechart definition in
Clojure, the lambda expression it compiles to, the tensor state
machine it runs as, and the mmap'd file it persists in — are all
the same object viewed from different angles. Like the crystal
being the same mathematical constant across all models.

## Open Questions

1. **Can the inference statechart (inner, continuous) be expressed
   in Fulcro?** The basins are continuous, not discrete. May need
   a discretized approximation: K, I, B, C, WHNF as states with
   Q rotation thresholds as guards.

2. **Should plates be read-only or copy-on-write?** mmap mode 'r'
   is read-only. mode 'r+' allows writes. For delta training,
   'r+' on the session plate enables in-place updates. For domain
   plates, read-only is correct.

3. **How does the statechart handle multiple inference requests?**
   The `ready` state with self-transition on `:infer` handles
   sequential requests. Parallel inference would need an orthogonal
   region per request (or a pool pattern).

4. **What's the serialization format for the shared definition?**
   EDN is natural for Clojure. Python needs a parser. Options:
   (a) EDN parser for Python (edn_format package), (b) JSON subset
   of EDN, (c) transit (Cognitect's cross-platform format).

5. **Does the tensor transition matrix need to handle parallel
   state?** Multi-hot state vectors + einsum transitions may need
   special handling for parallel region independence. Each region's
   transitions should only affect its own bits.

## Nucleus Connection

The compilation chain maps directly to the nucleus repo's tools:

| Nucleus Tool | Role in Chain | Input | Output |
|---|---|---|---|
| `COMPILER.md` (EDN) | prose → statechart EDN | Natural language prompt | `{:statechart/id ... :states ...}` |
| `LAMBDA-COMPILER.md` | prose → lambda | Natural language | `λ plate-vsm. parallel(...)` |
| `ALLIUM.md` | prose → behavioral spec | User stories | Entities, rules, transitions, guards |
| `VSM.md` | prose → VSM layers | System description | S5→S1 structured prompt |
| `DEBUGGER.md` | introspect running chart | Running statechart | State vectors, attention, patterns |

The nucleus EDN compiler already outputs statechart-shaped EDN — the
same shape Fulcro statecharts consume. The allium compiler produces
behavioral specs with `transitions` blocks and `when`/`requires`/
`ensures` that map to statechart guards and actions. The lambda
compiler produces the lambda intermediate form.

**Clojure is 96% mechanically convertible to lambda.** This is why
Fulcro statecharts are the right reference implementation — the
transformation from the Clojure definition to lambda is near-trivial,
and lambda IS what the tensor model computes.

## Verified Results (Session 162)

The tensor statechart engine runs successfully with mmap'd plate files:

```
Tensor Statechart Engine — Plate Loader VSM
State Trace:
   1 → load-plate         plates:idle→loading       inference:waiting
   2 → plate-ready        plates:loading→composing   inference:waiting
   3 → composed           plates:composing→ready     inference:waiting
   4 → infer              plates:ready               inference:waiting→running
   5 → inference-complete  plates:ready               inference:running→waiting
   6 · fold-delta         plates:ready               (guard BLOCKED — delta not plateaued)
   7 → fold-delta         plates:ready→folding       (guard passed after data model update)
   8 → folded             plates:folding→ready
   9 → infer + algedonic  plates:ready               inference:running→halted
  10 → diagnose           plates:ready               inference:halted→diagnosing
  11 → diagnosis-ok       plates:ready               inference:diagnosing→waiting
```

mmap composition verified:
- Crystal: 1000 × +1 (identity)
- Base FFN: random ternary (+1:336, 0:330, -1:334)
- Medical delta: 26 positions flipped (2.6% correction)
- Session delta: 1 position flipped (0.1% correction)
- Composed: sign(crystal × base × medical × session) = ternary ✓
- Fold: sign(base × medical) = ternary ✓ (lossless)
- Double fold: sign(folded × session) = ternary ✓ (infinite folds OK)

Key behaviors verified:
- **Parallel regions** work independently (plates, inference, intelligence)
- **Guards** correctly block transitions (fold-delta blocked until plateau)
- **Algedonic alert** bypasses normal flow (inference → halted directly)
- **mmap** loads real files as int8 tensors (zero-copy)
- **Composition** is pure sign multiplication (ternary × ternary = ternary)

## Scripts and Data

| Asset | Location | Status |
|-------|----------|--------|
| Fulcro statechart definition | `src/statechart/plate_loader.cljc` | ✅ Built |
| Tensor statechart engine | `scripts/explore/tensor_statechart.py` | ✅ Built, verified |
| Shared definition format | `specs/plate-loader.edn` | ✅ Built |
| Example plate files | `checkpoints/plates/*.bin` | ✅ Created, mmap verified |
