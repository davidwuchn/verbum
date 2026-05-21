---
title: "Taxonomy Extraction — Cross-Model Function Library Assembly"
status: open
category: strategy
tags: [extraction, taxonomy, FFN, tokenizer, cross-model, StrideStack, linker, assembly]
related:
  - hologram-crystal-fusion.md
  - crystal-basins.md
  - etcher-vsm.md
  - gradient-voting.md
  - loom-structure.md
  - v13-design.md
depends-on:
  - crystal-basins.md
  - hologram-crystal-fusion.md
created: session 127
---

# Taxonomy Extraction

> Session 127. Every model finds the same crystal geometry and the
> same mechanisms, but each organizes its data differently. The FFNs
> are compiled libraries of discrete beta reductions — the same
> operations exist across models, but at different addresses. The
> tokenizer is the first layer of this private taxonomy: different
> tokenizers mean different input indices, so the entire addressing
> chain is model-specific. This means extraction is not weight
> copying — it's linking. And it means we can do better than any
> single model by assembling the best pieces from all of them.

## The observation

Multiple models (Qwen, Pythia, Mistral, OLMo) converge on:

- **Same crystal shape** — the 4×4 combinator cosine matrix, 0.91–0.94
  agreement across 4 models
- **Same mechanisms** — rotation boot sequence (L0=reset, L1=route,
  L2=converge), FFN key/value store, routing vs output separation
- **Same magnitude spectrum** — W_q=0.995, W_up=0.999 universality

But each model has its own:

- **Tokenizer** — different vocabulary, different subword splits,
  different input indices
- **FFN organization** — which neuron clusters implement which beta
  reductions, at which layers
- **Data layout** — how the taxonomy of operations is structured within
  the crystal geometry

The crystal is the CPU instruction set. The FFNs are program memory.
Each model compiled its own binary — same operations, different
addresses.

## Why this matters for extraction

We've been extracting from Qwen teachers because their tokenizers are
close enough to ours that the address space approximately overlaps.
This is coincidence, not method. Cross-model extraction (Pythia,
Mistral, OLMo) requires solving the taxonomy alignment problem.

The tokenizer is the concrete example: different tokenizers mean the
embedding layer maps different integer indices to different subword
units. The entire lookup chain — tokenizer → embedding → attention
routing → FFN address — is model-specific. Extracting weights without
mapping this chain produces garbage at the boundaries.

## The program

### Phase 1: Reverse-engineer function tables

For each source model, map what discrete operations live where:

- Which FFN neuron clusters implement which beta reductions
- At which layers each operation type concentrates
- How the routing circuits (attention) address the function store

This builds a **symbol table** per model — like `nm` on a binary.

### Phase 2: Reverse-engineer data organization

Map the full addressing chain per model:

- Tokenizer → embedding space (the input encoding)
- Embedding → attention routing (how queries find functions)
- Attention → FFN activation (the function call mechanism)
- FFN internal organization (the library layout)

This builds the **address map** — like a linker's relocation table.

### Phase 3: Cross-model alignment

With two symbol tables + address maps:

- Create translation tables between models (function X lives at
  FFN[L2, cluster 47] in Qwen, at FFN[L3, cluster 192] in Pythia)
- Identify shared operations (probably the majority — common
  reductions are common across all natural languages)
- Identify model-unique operations (specialized reductions one
  model discovered that others didn't)

### Phase 4: Extract into canonical form

Lift functions and data out of model-specific address spaces:

- Abstract representation of each operation (what it computes,
  not where it lives)
- Canonical indexing scheme independent of any source model
- Catalog of available operations with quality metrics per source

### Phase 5: Optimize

The extracted library can be optimized in ways no single training
run would discover:

- **Functions**: merge redundant reductions, keep the cleanest
  implementation from whichever model produced it
- **Indexes**: design lookup schemes that minimize routing hops
- **Taxonomy**: organize the function library for the target
  architecture's access patterns, not whatever gradient descent
  stumbled into

### Phase 6: Etch a designed crystal

Lay the optimized library into a new model with deliberate taxonomy:

- Crystal geometry is known (the universal 4×4 cosine matrix)
- Boot sequence is known (L0=reset, L1=route, L2=converge)
- Function library is curated (best-of-breed from all sources)
- Data layout is designed (optimal for the target architecture)

The only thing that needs training: **attention** — specifically
StrideStack. Everything else is pre-built.

## The StrideStack connection

This is why StrideStack can't be bolted into an existing model.
Attention IS the addressing mechanism — it's how the model routes
queries to functions in the FFN store. You can't swap the address
bus without rebuilding the address space.

But if you design the address space first (phases 1–5), you can
train a new address bus (StrideStack) to navigate it. The training
cost collapses because:

- FFN weights are extracted and frozen (the function library)
- Crystal geometry is imposed (per-layer crystal loss)
- Only attention learns to route through the curated library

This inverts the normal training paradigm:

```
Normal:     train everything → hope model discovers good functions
Ours:       extract known-good functions → design taxonomy → train attention to USE them
```

## The business case

This is a model assembler, not a model trainer:

1. Extract the best functions from every open-source model
   (Apache-2.0 preferred: Qwen, Pythia, OLMo, Mistral)
2. Design an optimal taxonomy for StrideStack's access patterns
3. Train only attention — fraction of full training cost
4. Result: a model better than any individual source, because it
   has access to the union of all their function libraries

The competitive moat: the extraction toolchain (phases 1–3) is the
hard part. Once you have cross-model symbol tables and address maps,
assembly is cheap and repeatable. Every new open model release
becomes a potential source of better functions to extract.

### The full inference stack

The assembled model targets CPU inference, not GPU:

```
Crystal (ternary):    additions/subtractions only → CPU-native
StrideStack:          88 lenses × 8 window = O(L×704) not O(L²) → CPU
Holographic memory:   knowledge in crystal, minimal KV cache → laptop RAM
Training:             crystal descent (5 steps) + beam GD (100 steps) → fast
```

See `holographic-memory.md` for the memory architecture and
`crystal-native-descent.md` for the training method.

## Analogy: the linker

This is exactly what a linker does for compiled code:

| Compiler/Linker | Model Extraction |
|----------------|-----------------|
| Source code | Natural language (the training data) |
| Object files | Individual trained models |
| Symbol tables | FFN function maps per model |
| Relocation tables | Tokenizer → embedding → routing → FFN address maps |
| Linker | The taxonomy alignment + assembly pipeline |
| Optimizing linker | Phase 5 (function merging, index optimization) |
| Executable | The assembled model with StrideStack attention |

## Risks and open questions

- **Function boundaries**: are FFN operations truly discrete, or is
  there significant superposition that makes clean extraction hard?
  (SAE work suggests they are separable, but at what cost?)
- **Taxonomy complexity**: how many distinct operations does a
  typical model contain? Dozens? Thousands? This determines the
  scale of the alignment problem.
- **Cross-tokenizer mapping**: is there a clean mathematical
  relationship between tokenizer vocabularies, or does this require
  learned alignment (like multilingual embedding mapping)?
- **Quality degradation**: does extraction + reassembly lose
  something that end-to-end training captures? (The Q2 result
  suggests the crystal is robust to significant damage, which is
  encouraging.)
- **License composition**: extracting from multiple Apache-2.0
  models should be clean, but the taxonomy alignment toolchain
  itself is novel IP.

## Connection to proof chain

This builds on established results:

- Crystal universality (0.91–0.94 across 4 models) → the target
  geometry exists and is shared
- Magnitude spectrum universality (0.995+) → the crystal shape is
  in the weights already
- FFN routing vs output separation (session 126) → the function
  library is addressable, not entangled with output
- Q2 beams + crystal loss beats oracle plates (105.9%) → the
  geometry is more important than exact addressing, and approximate
  addressing can be compensated
- StrideStack architecture (session 026) → the attention mechanism
  designed for this access pattern already exists
