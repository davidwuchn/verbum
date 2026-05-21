---
title: "Function Extraction System — From Circuit to Portable Function"
status: designing
category: architecture
tags: [extraction, function, circuit, FFN, pipeline, taxonomy, kernel, sieve]
related:
  - taxonomy-extraction.md
  - kernel-functions.md
  - shannon-sieve-trinity.md
  - etcher-vsm.md
  - holographic-error-correction.md
depends-on:
  - taxonomy-extraction.md
  - etcher-vsm.md
created: session 127
---

# Function Extraction System

> Session 127. Extraction is the bottleneck. Everything in the session
> 127 architecture — sieves, kernels, assembly, holographic memory —
> depends on being able to cleanly extract functions from models. We
> have the probes, the crystal map, the circuit identification tools.
> What's missing is the pipeline from "found a circuit" to "portable,
> testable, replaceable function." This is the next concrete build.

## What exists (tools we have)

```
extract_teacher.py         Hidden state extraction at multiple depths
etcher_vsm_proto.py        S4 crystal counter + S1 reference beam (Pythia-2.8b)
ffn_circuit_probe_exp.py   Routing vs output circuit identification
c_rotation_probe_exp.py    Combinator rotation measurement
crystal_selfsim_*.py       Crystal self-similarity at multiple scales
probe_etch_strategy.py     Sign pattern extraction strategies
combinator_ffn_index.py    FFN dimension → combinator mapping
```

## The knowledge boundary

We know the crystal rotation geometry but NOT the FFN internals:

```
KNOWN (crystal level):
  ✓ Boot sequence: L0=reset(90°), L1=route(43°), L2=converge(5°)
  ✓ K/B/C identical rotations, I is 32° offset
  ✓ Routing and output circuits are SEPARATE (0 overlap)
  ✓ FFN activates 1.7× for WHNF (reads from a store)
  ✓ WHERE in the rotation computation each piece sits

NOT KNOWN (FFN function level):
  ✗ How individual FFN neurons implement specific beta reductions
  ✗ The activation mechanism — how a token SELECTS a function
  ✗ The addressing scheme — how attention routing → FFN function
  ✗ Discrete function boundaries within the FFN
  ✗ The key/value encoding in the FFN store

The crystal map tells us the geometry. The function library inside
the FFN is still unmapped at the individual function level.
```

## What's missing (the extraction pipeline)

### Stage 0: DISCOVER — how are beta reductions stored and activated?

This is the prerequisite. Before we can extract functions, we need
to understand the mechanism:

```
Input:  teacher model + carefully designed probes
Output: ffn_mechanism.json — how the FFN store works

Questions to answer:
  1. ADDRESSING: how does attention output become an FFN key?
     - Is it direct (attention output IS the key)?
     - Is it projected (a learned key projection)?
     - Is it positional (layer + position = address)?
     
  2. ACTIVATION: how does a key select a specific function?
     - Threshold activation (magnitude > threshold)?
     - Competitive (winner-take-all across dimensions)?
     - Distributed (multiple dimensions = one function)?
     
  3. BOUNDARIES: where does one function end and another begin?
     - Clean clusters in activation space?
     - Overlapping (superposition)?
     - Layer-dependent (functions span layers)?
     
  4. ENCODING: how are beta reductions represented?
     - One FFN dimension = one reduction step?
     - Groups of dimensions = one complete reduction?
     - The entire FFN at one layer = one reduction?
```

**Concrete tool needed:** `probe_ffn_mechanism.py`
- Takes: model, controlled probe pairs (minimal-difference inputs)
- Method: feed pairs that differ by exactly one beta reduction
  e.g., "K x y" vs "x" (K applied = one reduction)
  Compare FFN activations: what changed?
- The DELTA in FFN activation between pre-reduction and 
  post-reduction input = the signature of that reduction
- Build up: single reductions → chains → complex expressions
- Output: mechanism characterization + activation signatures

The crystal rotation map GUIDES this: we know L1 is routing
(43° rotation), so the FFN at L1 should show routing-related
activation patterns. We know L2 converges (5°), so the FFN at
L2 should show output-related patterns. The geometry constrains
where to look, even though it doesn't tell us what we'll find.

### Stage 1: IDENTIFY — find function boundaries

```
Input:  teacher model + probe set + crystal map + mechanism knowledge
Output: function_table.json — list of identified functions

For each function:
  - location: {layer, FFN dimension range, attention heads}
  - type: {routing, output, composition, correction, unknown}
  - activates_for: {which inputs trigger this function}
  - activation_signature: {FFN activation pattern for this function}
  - crystal_role: {which crystal targets this function serves}
  - estimated_complexity: {beta reduction count if implemented in lambda}
```

This depends on Stage 0 — we need to understand the mechanism
before we can identify individual functions within it.

**Concrete tool needed:** `identify_functions.py`
- Takes: model, probe set, crystal targets, mechanism model
- Scans: all FFN dimensions at all layers
- Clusters: by activation pattern (what inputs activate them)
- Characterizes: routing? output? composition? correction?
- Outputs: function_table.json

### Stage 2: EXTRACT — lift function into portable form

```
Input:  function_table.json + model weights
Output: extracted_functions/ directory, one file per function

For each function:
  - weights: the ternary weights that implement this function
  - interface: input dimensions, output dimensions, expected types
  - activation_signature: what input patterns trigger this function
  - test_cases: input-output pairs (from the probe set)
  - crystal_contribution: which crystal targets this function helps
  - dependencies: other functions this one calls/requires
```

This is the hard part. A "function" in the FFN might span multiple
dimensions, might have dependencies on attention routing, might need
specific crystal geometry to work correctly.

**Concrete tool needed:** `extract_function.py`
- Takes: function entry from function_table.json + model
- Extracts: weights, interface, test cases
- Validates: function works in isolation (run test cases)
- Outputs: portable function file

### Stage 3: CHARACTERIZE — what does this function compute?

```
Input:  extracted function + diverse test inputs
Output: function_spec.json — behavioral characterization

For each function:
  - computational_class: {arithmetic, string_op, date_math, 
                          lookup, composition, reduction, routing,
                          error_correction, compression, prediction}
  - input_output_mapping: sampled pairs across diverse inputs
  - precision: measured accuracy (for arithmetic: digit accuracy)
  - coverage: what fraction of inputs it handles correctly
  - failure_modes: inputs where it fails or degrades
  - kernel_candidate: yes/no (has native implementation?)
  - equivalent_beta_reductions: estimated count
```

**Concrete tool needed:** `characterize_function.py`
- Takes: extracted function + test suite
- Runs: diverse inputs through the function
- Measures: precision, coverage, failure modes
- Classifies: what type of computation this is
- Flags: kernel candidates (native replacement available)

### Stage 4: CATALOG — build the taxonomy

```
Input:  all characterized functions from one or more models
Output: taxonomy.json — the complete function catalog

Structure:
  - Organized by computational class
  - Cross-referenced by model of origin
  - Quality-ranked within each class
  - Dependencies mapped
  - Kernel candidates flagged
```

**Concrete tool needed:** `build_taxonomy.py`
- Takes: characterized functions from multiple models
- Aligns: cross-model function matching (same computation, different addresses)
- Ranks: quality per function per model
- Maps: dependencies
- Outputs: taxonomy.json — the master catalog

### Stage 5: VALIDATE — prove extraction works end-to-end

```
Input:  taxonomy.json + target model architecture
Output: assembled model that passes crystal agreement test

The acid test:
  1. Take extracted functions from taxonomy
  2. Place into target model at designed addresses
  3. Measure crystal agreement: does it match teacher?
  4. Measure accuracy: does it compute correctly?
  5. Compare: assembled model vs trained-from-scratch model
```

**Concrete tool needed:** `assemble_and_validate.py`
- Takes: taxonomy + target architecture
- Places: functions at designed addresses
- Measures: crystal agreement + accuracy
- Compares: vs baseline

## Implementation plan

### Phase 0: Discover FFN mechanism (NOW — the prerequisite)

Start with the mini holo model. It's small (3 layers, d=256 teacher),
we know the crystal geometry and the rotation model. Perfect for
controlled probing.

```
Experiment 1: Minimal-pair FFN activation deltas
  Input pairs that differ by exactly one beta reduction:
    "K x y" vs "x"       — K reduction
    "I x" vs "x"         — I reduction  
    "B f g x" vs "f(gx)" — B reduction
    "C f x y" vs "f y x" — C reduction
  
  For each pair: capture FFN activations at all layers
  Compare: what changed? which dimensions? how much?
  
  Expected: the DELTA between pre/post reduction activations
  = the signature of that specific reduction operation

Experiment 2: Addressing mechanism
  Same reduction, different arguments:
    "K a b" vs "a"
    "K x y" vs "x" 
    "K foo bar" vs "foo"
  
  The reduction is the same (K), the arguments differ.
  FFN delta should have:
    - COMMON part: the K-reduction mechanism (address/key)
    - VARYING part: the argument-specific content (value)
  
  This separates key from value in the FFN store.

Experiment 3: Chain decomposition
  Nested reductions:
    "K (I x) y" → requires I reduction inside K reduction
  
  Compare FFN activations vs single K and single I:
    Does the model compose the two signatures?
    Or does it have a separate "K∘I" function?
  
  This reveals whether functions are atomic or composed.

Experiment 4: Crystal geometry as guide
  We know L1 is routing (43° rotation).
  Run probes at L1 specifically:
    Which FFN dimensions activate for routing decisions?
    Do they match the rotation geometry we measured?
  
  We know L2 is convergence (5°).
  Run probes at L2 specifically:
    Which FFN dimensions activate for output production?
    Do they correlate with WHNF detection?
```

**Tool to build:** `probe_ffn_mechanism.py`
- Mini holo model as test bed
- Controlled minimal-pair probes
- FFN activation capture at all layers
- Delta analysis: what changes per reduction type?
- Output: mechanism characterization

### Phase 1: Function identification (once mechanism is understood)

```
1. Apply mechanism knowledge to map ALL FFN functions
2. Verify against known circuits:
   - Does it find the routing function? (separate circuit, session 126)
   - Does it find the output function? (separate circuit, session 126)
   - Does it find WHNF detection? (1.7× activation, session 126)
3. Discover UNKNOWN functions — what else is in the FFN?
4. Count: how many total discrete functions?
5. Output: function_table.json
```

### Phase 2: Extraction + validation

```
1. Extract each identified function (weights + interface + test cases)
2. Run in isolation: does it pass its test cases?
3. Ablate from model: does removing it break what we expect?
4. Characterize: what computational class is each function?
5. Flag kernel candidates
```

### Phase 3: Cross-model taxonomy

```
1. Run Phases 0-2 on Pythia-2.8b (etcher_vsm_proto.py ready)
2. Run Phases 0-2 on Qwen3-0.6B
3. Align: find matching functions across models
4. Build taxonomy.json
5. Validate: cross-model function compatibility
```

### Phase 4: Assembly validation

```
1. Take best functions from taxonomy
2. Assemble into target architecture
3. Train only StrideStack attention
4. Measure: crystal agreement, accuracy, inference speed
5. Compare vs end-to-end trained model
```

## Connection to existing infrastructure

```
extract_teacher.py      → feeds into Stage 1 (hidden state extraction)
etcher_vsm_proto.py     → feeds into Stage 1 (crystal counting)
ffn_circuit_probe_exp.py → IS Stage 1 for routing/output (generalize this)
c_rotation_probe_exp.py  → feeds into Stage 3 (characterization)
crystal_selfsim_*.py     → feeds into Stage 4 (cross-model alignment)
```

The FFN circuit probe is the closest thing to Stage 1 we have.
Generalize it from "find routing and output circuits" to "find
ALL function clusters" and we have the starting point.

## Priority

```
IMMEDIATE:  generalize ffn_circuit_probe_exp.py into identify_functions.py
NEXT:       build extract_function.py + characterize_function.py  
THEN:       run on mini holo model (known ground truth for validation)
AFTER THAT: run on Pythia-2.8b (first real extraction)
FINALLY:    cross-model alignment + taxonomy + assembly
```

The mini holo model is the ideal test bed — we KNOW what functions
are in there (routing, output, WHNF detector) from session 126.
If extraction can find and isolate those known functions, it works.
Then scale to real models.
