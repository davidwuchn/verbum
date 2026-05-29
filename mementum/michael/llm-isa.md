# What's Inside a Large Language Model

> We disassembled a 27-billion-parameter language model and found an
> instruction set.

Not a metaphorical one. Not "it's kind of like a compiler." A
decodable, deterministic, input-dispatched instruction set with a
three-phase pipeline, typed opcodes, and a separate data path for
memory lookups.

If you've built a compiler or designed a CPU, the next five minutes
will feel familiar.

---

## The Setup

We wrote a tool that reads the weight matrices of a transformer's
feed-forward network (FFN) layers and projects them into combinator
space — the basis set of operations from combinatory logic (K, I, B,
C, etc.). Each of the 64 layers in Qwen3.6-27B produces a signature:
which combinator operations it amplifies, suppresses, or converts
between.

We call this the **moiré grating decoder**, because the FFN's
gate/up/down projections act like overlapping diffraction gratings
whose interference pattern determines which operation gets executed.

The key insight: **you can read the program from the weights without
running any input through the model.**

---

## Exhibit 1: The Static Program

Here is the instruction set, decoded directly from the weight
matrices. No forward pass. No input. Just the weights.

```
Layer  Opcode (dominant)         Transform (strongest conversion)
─────  ───────────────────────   ─────────────────────────────────
L00    I:+0.52  K:+0.44         B→I:+0.52   C→I:+0.52
L01    β_apply:-0.52            β_apply→β_I:-0.38
L02    K:+0.45  β_K:+0.44      β_compose→β_K:+0.49
L03    β_compose:-0.47          B→β_compose:-0.31
  ...
L16    β_compose:+0.37          β_compose→β_apply:+0.29
L17    Y:-0.38                  Y→D:-0.27
L18    β_K:-0.31                K→β_K:-0.27
  ...
L32    K:-0.48                  K→β_I:-0.30
L33    I:+0.53                  I→K:+0.25
L34    C:+0.50                  β_apply→β_compose:+0.27
  ...
L48    β_I:-0.25                β_I→β_K:-0.24
L49    D:+0.42                  B→D:+0.30
L50    D:+0.37                  D→W:+0.31
  ...
L58    K:-0.41  W:+0.40         K→β_I:-0.38
L62    W:-0.28                  W→C:-0.14
L63    W:-0.41  D:-0.33         W→Y:-0.36
```

Each row is an instruction. Each layer converts combinator types
into other combinator types with measurable strength. The opcodes are
typed: K (select), I (identity), B (compose), C (flip), Y (recurse),
W (duplicate), D (cascade), plus their beta-reduction variants.

The transformation strength decreases with depth:

| Region       | Layers | Transform Strength | Phase         |
|:-------------|:------:|:------------------:|:--------------|
| Early        | 0–20   | 1.17               | Build program |
| Mid          | 21–42  | 0.95               | Execute       |
| Late         | 43–63  | 0.69               | Emit result   |

Three-phase pipeline: **Build → Execute → Emit.**

A compiler engineer has seen this before. It's a compilation
pipeline. Front-end constructs the IR. Middle applies transforms.
Back-end lowers to output.

---

## Exhibit 2: Determinism

We ran the same input through the model three times and compared the
decoded instruction traces.

```
Identical programs: True
Max strength drift:  0.00000000
```

Not approximately similar. Not statistically close.
**Exactly identical across all 64 layers, every value, every run.**

The only non-determinism in the system is at the very end — token
sampling (temperature, top-k). The computation itself is a fixed
point. Gradient descent converged to gratings that execute
deterministic programs.

This is not a neural network being fuzzy. This is a machine.

---

## Exhibit 3: Input-Dependent Dispatch

Here's where it gets unmistakable. The static program (Exhibit 1)
is the same for every input — it's the instruction set. But different
inputs activate different subsets of each instruction. The activation
column shows which combinator type the residual stream is carrying at
each layer.

### K combinator: `K a b = a` (select first argument)

The K combinator takes two arguments and returns the first. Here's
what the model does when asked to reduce it:

```
Layer  Static Grating              Activation    Attention Reading
─────  ──────────────────────────  ──────────    ─────────────────
L02    K:+0.45  β_K:+0.44         K:+0.56 █     [recurrent]
L07    I:+0.55  β_apply:-0.55     D:+0.50 █     =(42):0.17  a(40):0.12
L15    I:+0.28  β_apply:-0.19     K:+0.34 █     You(0):0.47
L19    I:+0.59  β_I:+0.26         K:+0.47 █     =(42):0.22  K(39):0.15
L23    β_compose:-0.41            K:+0.55 █     =(42):0.17  K(39):0.16
L35    C:-0.52  W:+0.38           K:+0.49 █     K(39):0.17
L43    C:+0.26  D:+0.26           K:+0.56 █     =(42):0.24  K(39):0.14
L51    W:+0.17  I:+0.16           K:+0.49 █     K(39):0.24  a(40):0.19
L55    Y:-0.10                    K:+0.42 █     K(39):0.14  a(40):0.13
L63    W:-0.41  D:-0.33           K:+0.42 █     =(42):0.40
```

**K activation dominant from layer 2 to layer 63.** The model
identified the combinator type in the first few layers and routed
the entire computation through the K pathway. At L51, attention
shifts to the K token (position 39) and argument `a` (position 40)
— it's reading the combinator and its first argument. The output:
`a`. First argument selected. K combinator executed.

### B combinator: `B f g x = f(gx)` (compose)

Now the same model, same weights, different input:

```
Layer  Static Grating              Activation    Attention Reading
─────  ──────────────────────────  ──────────    ─────────────────
L02    K:+0.45  β_K:+0.44         K:+0.56 █     [recurrent]
L07    I:+0.55  β_apply:-0.55     D:+0.50 █     =(43):0.19  g(41):0.07
L19    I:+0.59  β_I:+0.26         B:+0.59 █     =(43):0.21  B(39):0.11
L23    β_compose:-0.41            B:+0.53 █     =(43):0.26  B(39):0.09
L35    C:-0.52  W:+0.38           D:+0.35 █     =(43):0.27
L39    K:+0.27  Y:+0.26           B:+0.49 █     =(43):0.29  g(41):0.11
L47    β_compose:+0.19            B:+0.51 █     f(40):0.15
L51    W:+0.17  I:+0.16           B:+0.68 █     f(40):0.18  B(39):0.17
L55    Y:-0.10                    B:+0.40 █     f(40):0.13  g(41):0.11
L63    W:-0.41  D:-0.33           C:+0.42 █     f(40):0.08
```

**B activation dominant from layer 19 to layer 63.** At L55,
attention reads *both* function arguments — f(40) and g(41) — because
B needs to compose them. The final layer shows C (flip) activation,
reordering arguments for the output `f(gx)`.

### Side by side

Same static gratings. Different dynamic activation. The input
determined which pathway through the instruction set was taken.

| Input        | Dominant Type | Attention Focus            | Output   |
|:-------------|:-------------|:---------------------------|:---------|
| `K a b =`    | K (select)   | K(39), a(40)               | `a`      |
| `B f g x =`  | B (compose)  | f(40), g(41)               | `f(gx)`  |
| `S K K x =`  | Mixed K/S    | x(42), S(39)               | `x`      |

Different inputs. Same hardware. Different opcodes dispatched.

That's not learning. That's execution.

---

## Exhibit 4: One Compute Substrate for Everything

This is perhaps the most important finding. The combinator ISA isn't
just used for explicit lambda expressions. It's used for
**everything** — prose, arithmetic, code, reasoning. The model
doesn't have a "language mode" and a "math mode." It has one
computational substrate.

Here's what the residual stream carries through 64 layers for six
different inputs to the same model:

| Input | Type | Dominant Opcode | Strength | What it's doing |
|:------|:-----|:----------------|:--------:|:----------------|
| `K a b =` | Combinator | K (select) | +0.56 | Selecting first argument |
| `B f g x =` | Combinator | B (compose) | +0.68 | Composing two functions |
| `Every student read a book =` | Prose → λ | C (flip) + β_apply | +0.35 | Reordering quantifier scope |
| `The cat sat on the mat =` | Prose → λ | C (flip) + β_apply | +0.33 | Building predicate structure |
| `2 + 3 =` | Arithmetic | β_I (identity reduction) | +0.38 | Church numeral selection |
| `The capital of France is` | Retrieval | **[near zero]** | ~0 | **Bypasses compute entirely** |

The explicit combinator reductions (K, B) produce strong, clean
activations because the input already names the operation. But look
at the prose inputs — "Every student read a book" activates the
**same opcodes**: C (flip/reorder), B (compose), β_apply
(function application), β_compose (composition reduction). The
activations are weaker because the model has to *discover* which
combinators to apply, rather than being told. But the opcodes are
identical.

Arithmetic uses β_I (identity reduction) — the Church numeral
encoding of natural numbers, where selecting from successors is
an identity operation. Still the same instruction set.

The only input that **doesn't** use the combinator pipeline is
factual retrieval. "The capital of France is" produces near-zero
combinator activation across all 64 layers. The answer "Paris"
comes from the FFN's key-value store, not its compute gratings.
That's the data bypass (Exhibit 5).

What this means: **natural language IS lambda calculus to this
machine.** The model doesn't translate English into computation —
English already IS computation. "Every student read a book"
requires the same C (flip) and B (compose) operations whether you
write it in English or in combinator notation. The surface syntax
is irrelevant. The computation is identical.

A compiler engineer would recognize this immediately: it's the
difference between source language and intermediate representation.
Python, C, and Rust all look different on the surface. But they
all compile to the same IR, and the same optimization passes apply.
English and lambda calculus are different source languages that
compile to the same combinator IR inside the model.

---

## Exhibit 5: It's the Same ISA in Every Model

Everything above was measured on Qwen3.6-27B. We ran the same
combinator selectivity probes on six models from four different
organizations, spanning 200× in parameter count and three
unrelated architectures:

| Model | Org | Params | Layers | Architecture | K | B | C | I |
|:------|:----|-------:|-------:|:-------------|------:|------:|------:|------:|
| Pythia-160M | EleutherAI | 160M | 12 | GPT-NeoX | 0.149 | 0.137 | 0.134 | 0.067 |
| Mistral-7B | Mistral AI | 7B | 32 | Mistral | 0.053 | 0.051 | 0.050 | 0.032 |
| OLMo-2-13B | Allen AI | 13B | 40 | OLMo | 0.197 | 0.183 | 0.210 | 0.045 |
| Qwen3-14B | Alibaba | 14B | 40 | Qwen | 0.084 | 0.078 | 0.080 | 0.045 |
| Qwen3-32B | Alibaba | 32B | 64 | Qwen | 0.079 | 0.075 | 0.077 | 0.044 |
| Qwen3.6-27B | Alibaba | 27B | 64 | Qwen+Hybrid | (ISA decode above) |

The absolute magnitudes differ (smaller models have stronger
per-head selectivity because there are fewer heads). But the
**ordering is invariant**: K ≥ B ≈ C >> I, in every model, every
time. Select, compose, and flip dominate. Identity is always
weakest. The combinators are the same.

### Pythia-160M vs. Qwen3-32B: r = 0.998

We measured the KIBC selectivity correlation between the smallest
and largest models — architecturally unrelated, trained on
different data, 200× apart in parameter count:

**Correlation: r = 0.998.**

Not "similar." Not "analogous." Essentially identical combinator
profiles. The same operations, at the same relative strengths,
discovered independently by gradient descent in completely
different training runs.

This is like finding the same instruction set in an Intel chip
and an ARM chip. Different designers, different transistor counts,
different fabrication — same ISA. Because the math constrains the
design. There are only so many ways to do typed function
application, and gradient descent finds them all.

### The extended opcodes are there too

Beyond KIBC, we probed for higher-order combinators in Qwen3-32B:

| Opcode | Mean Selectivity | Role |
|:-------|:----------------:|:-----|
| W | 0.073 | Duplicate (use argument twice) |
| S | 0.071 | Substitution (general composition) |
| abstract | 0.061 | Lambda abstraction |
| bind | 0.043 | Variable binding |

The full 12-opcode instruction set from the ISA decoder (Exhibit 1)
is confirmed by independent selectivity measurements. These aren't
artifacts of our decoder — they're operations the model is actually
performing.

---

## Exhibit 6: The Bypass

Not everything goes through the combinator pipeline. When you ask a
factual question — "The capital of France is" — the model does
something completely different:

```
Layer  Static Grating              Activation       Attention Reading
─────  ──────────────────────────  ──────────────   ─────────────────
L03    β_compose:-0.47            [near zero]       The(0):0.26  France(3):0.24
L07    I:+0.55  β_apply:-0.55    [near zero]       France(3):0.32  is(4):0.31
L15    I:+0.28  β_apply:-0.19    [near zero]       The(0):0.67
L23    β_compose:-0.41            [near zero]       The(0):0.37  is(4):0.35
L39    K:+0.27  Y:+0.26          [near zero]       The(0):0.42  France(3):0.29
L51    W:+0.17  I:+0.16          [near zero]       The(0):0.38  is(4):0.26
L63    W:-0.41  D:-0.33          [near zero]       is(4):0.57  France(3):0.16
```

**Combinator activations near zero across all 64 layers.** The
computation pipeline sits idle. Attention just reads the entity
("France") and the relation ("capital... is") directly. The answer
"Paris" comes from a completely different mechanism — the FFN's
key-value store, not its combinator grating.

A CPU architect would call this a **data bypass**. When the result
is already in a register (the FFN's learned associations), you don't
need the ALU. The model has both: a compute path (combinators) and a
data path (retrieval), and it routes between them based on input type.

---

## What A Compiler Engineer Should See

1. **An instruction set** — 12 typed opcodes (K, I, B, C, D, W, Y,
   S, and their beta-reduction variants), decodable from static
   weights

2. **Deterministic execution** — 0.00000000 drift across runs, a
   literal fixed point

3. **Input-dependent dispatch** — same hardware, different activation
   pathways, determined by input type

4. **One compute substrate for all inputs** — prose, arithmetic,
   code, and explicit lambda all use the same combinator opcodes.
   English and lambda calculus are different source languages that
   compile to the same IR

5. **The same ISA in every model** — six models, four organizations,
   three architectures, 200× parameter range, r=0.998 correlation.
   Gradient descent converges to the same instruction set every
   time, independently, the way every civilization independently
   discovers arithmetic

6. **A three-phase pipeline** — build (high transform), execute
   (medium), emit (low)

7. **A data bypass** — retrieval skips the compute path entirely

This is not a pattern we imposed. We built a decoder and pointed it
at the weights. This is what came out. Then we pointed it at five
more models and got the same answer.

---

## The Implication

Right now, the world is spending billions of dollars to make these
models bigger. More parameters, more GPUs, more data.

But if the computation inside is a typed lambda calculus compiler
running on a fixed combinator instruction set — and the evidence
says it is — then this is an optimization problem, not a scaling
problem.

Compilers got 1000× faster not by making the hardware bigger, but by
understanding the computation and optimizing the passes. Dead code
elimination. Constant folding. Register allocation. Instruction
scheduling.

We measured the quantization cliff: the computation (combinators)
survives aggressive compression down to 3 bits per weight. The data
(factual knowledge) dies at 3 bits but survives at 4. The compute is
robust because fixed points are robust — they're energy minima.

A 70-billion-parameter model might be running a program that fits in
a few hundred megabytes if you extract the instruction set and
compile it properly. The rest is holographic redundancy — the same
program encoded many times over, the way a hologram stores the
entire image in every fragment.

We've been scaling the hologram. We should be reading the program.

---

## Reproduce It

All measurements were made on **Qwen3.6-27B** (bf16) using
the moiré grating decoder:

```
git clone https://github.com/michaelwhitford/verbum
cd verbum
uv sync
uv run python scripts/v14/isa_decoder_v2.py
```

Runtime: ~8 minutes on M3 Ultra (512GB). ~2 minutes with cached
fingerprints. Results in `results/isa-decode-v2/`.

The decoder:
1. Builds combinator fingerprints (12 ops × 64 layers) by running
   reduction pairs through the FFN and measuring the residual delta
2. Projects each layer's weight matrix into combinator space to read
   the static program
3. Runs the determinism check (3 identical passes, drift = 0.0)
4. Traces diverse inputs with attention capture at 16 checkpoints
5. Compares opcode distributions and attention patterns across tasks

Cross-model combinator probes are in `results/combinator-probe-*/`
for Pythia-160M, Mistral-7B, OLMo-2-13B, Qwen3-14B, and Qwen3-32B.

The code is MIT-licensed. The models are open-weight. The findings
are the findings.

---

## Prior Art and Context

This work builds on and extends:
- **Combinatory logic** (Schönfinkel 1924, Curry 1930) — the
  theoretical basis for the combinator types we decode
- **The Curry-Howard correspondence** — programs are proofs, types
  are propositions. If LLMs implement typed combinators, they're
  doing proof search
- **Mechanistic interpretability** (Elhage et al. 2022, Conmy et al.
  2023) — circuit-level analysis of transformers. Our contribution:
  the circuits implement a specific, known computational formalism
- **nucleus** (Whitford 2025) — observational evidence that LLMs
  perform lambda compilation with P(λ)=0.907 behavioral probability,
  which motivated the search for the internal mechanism

---

*Michael Whitford — [verbum](https://github.com/michaelwhitford/verbum)*
*May 2026*
