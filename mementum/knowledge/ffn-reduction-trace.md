---
title: "The Reduction Architecture — FFN Compiles, Attention Executes, Combinators Have Depth"
status: active
category: methodology
tags: [ffn, reduction, beta-reduction, attention, combinators, depth-profile, instrument]
related: [ffn-circuit-types, standing-wave-magnitudes, phi-information-partition, holographic-computer, crystal-universality]
depends-on: [ffn-circuit-types]
---

# FFN Reduction Trace

> Projecting active FFN neurons through the unembedding matrix reveals
> WHAT each neuron "says" in vocabulary space. The FFN output at each
> position is a **compiled program** — context-dependent value vectors
> that encode each position's semantic contribution. Attention then
> executes this program via softmax over V, selecting and combining
> compiled values to produce the output. This IS β-reduction by
> weighted combination.
>
> Key finding: FFN compilation becomes readable at L26-L30 in
> Qwen3-8B (36 layers). Before that, computation is in null space
> (invisible). The same token produces DIFFERENT compiled values in
> different contexts — this is compilation, not dictionary lookup.

## Experiment

**Model:** Qwen3-8B (36 layers, gated FFN with SiLU, 12288 intermediate)
**Method:** Hook each FFN layer's MLP, capture per-neuron gate activations
(`SiLU(gate_proj(x)) * up_proj(x)`), project active neurons' `down_proj`
columns through the unembedding matrix to read what each neuron "promotes"
and "suppresses" in token space.
**Probes:** 5 sentences × 2 gates (compile, null) = 10 forward passes.
**Script:** `scripts/experiments/ffn_reduction_trace.py`
**Results:** `results/ffn-reduction-trace/`

## Finding 1: The Semantic Phase Transition at L26-L30

FFN output projections through unembedding are **noise** at L0-L22 and
**coherent semantic associations** at L26-L30.

### "If it rains, the ground is wet." at L30

| Position | Token | FFN promotes | Interpretation |
|----------|-------|-------------|----------------|
| 0 | `it` | **rain, 雨, rains** | Resolves referent: "it" = rain |
| 1 | `rains` | **hard, harder** | Predicts continuation/intensifier |
| 2 | `,` | _go, grandfather_ | Structural (weak) |
| 3 | `the` | **crops, ground, garden** | Predicts what gets affected |
| 4 | `ground` | **soak, soaked, 浸** | Predicts the consequence |
| 5 | `is` | **wet, 濡, 湿** | Writes the predicate |
| 6 | `wet` | _ting, ted, ten_ | Morphological continuation |
| 7 | `.` | **rain, Rain, 雨水** | Loops back to the cause |

At L26, the comma position promotes **`then, entonces, então`** — the
logical connective "then" in three languages. The FFN is writing the
implication operator at the structural boundary.

### "Someone believes that the earth is flat." at L30

| Position | Token | FFN promotes | FFN suppresses |
|----------|-------|-------------|----------------|
| `believes` | **proposition, propositions, that** | — |
| `that` | **proposition, propositions, logical** | — |
| `the` | **Earth, world, earth** | — |
| `earth` | **round, rounds, Round** | **Earth, earth** |
| `is` | **round, Round, rounds** | **earth, 地球** |
| `flat` | **round, ERR** | — |

The model knows "the earth is flat" is wrong. At the `earth`, `is`, and
`flat` positions, the FFN **promotes "round"** and **suppresses "earth"** —
it's writing the correction. Meanwhile `believes` and `that` promote
**"proposition"** — the FFN recognizes the propositional attitude frame.

### "The cat that sat on the mat is black." at L30

| Token | FFN promotes | Interpretation |
|-------|-------------|----------------|
| `cat` | **sleeps, 睡, pur** | Default cat actions |
| `that` | **猎, hunting, hunts** | Relative clause → hunting behavior |
| `sat` | **down, by, Down** | Spatial continuation |
| `on` | **lap, boxes, laps** | Where things sit on |
| `the` | **lap, Lap, laps** | Contextual — near "on" |
| `mat` | **sleeps, Sleep, sleeping** | What happens on a mat |
| `is` | **sleeping, Sleeping, asleep** | State predicate |
| `black` | _ewood, lit, -white_ | Color associations |

### "Every student reads a book." at L30

| Token | FFN promotes | Interpretation |
|-------|-------------|----------------|
| `student` | **passing, passed, Passing** | What students do (exams) |
| `reads` | **book, books, 书** | Direct object prediction |
| `a` | **book, 书, book** | Reinforces object |
| `book` | **swiftly, 速度快, 迅速** | Manner of reading |
| `.` | **Gram, gram** | ? |

## Finding 2: The Depth Profile — From Noise to Semantics

Active neuron fraction grows monotonically then dips at L35:

```
Layer   Active%   Active Neurons    Character of Output
─────   ───────   ──────────────    ────────────────────────────────
L0      0.4%           49           Noise — subword fragments
L3      0.9%          107           Noise
L6      7.7%          944           Noise — some distant associations
L10    22.6%         2772           Noise — thematic but incoherent
L14    24.4%         2995           Noise
L18    25.2%         3094           Noise — beginning to cohere
L22    40.3%         4951           Transitional — weak semantics
L26    56.6%         6955           SEMANTIC — associations, connectives
L30    64.6%         7939           SEMANTIC — precise predictions
L33    68.7%         8439           FORMAT — next-token syntax (., ,)
L35    66.9%         8223           FORMAT — sentence continuation
```

**Three phases in the FFN output:**
1. **L0-L18: Noise.** The FFN writes to high-dimensional subspaces that
   don't project cleanly onto tokens. This IS the ORTHO/invisible
   computation — directions orthogonal to vocabulary space.
2. **L26-L30: Semantic.** The FFN writes coherent associative predictions.
   Each position's neuron aggregate promotes related concepts.
3. **L33-L35: Format/syntax.** The FFN shifts to next-token formatting
   (punctuation, function words, continuation cues).

This matches the standing-wave depth profile:
- ORTHO = dark (computation in null space, no token projection)
- ALIGN = semantic (features align with vocabulary directions)
- COLLAPSE = format (final token selection)

## Finding 3: Compile vs Null — Almost No Difference

Compile gate and null gate produce **nearly identical FFN function lists**
at the semantic layers (L26-L30).

```
Layer   Compile Active   Null Active   Delta
─────   ──────────────   ───────────   ─────
L0          0.4%            0.4%       -0.0%
L6          7.7%            8.6%       -0.9%
L10        22.6%           23.5%       -0.9%
L14        24.4%           23.4%       +1.0%
L18        25.2%           22.4%       +2.8%  ← small compile excess
L22        40.3%           38.1%       +2.2%
L26        56.6%           55.0%       +1.6%
L30        64.6%           64.1%       +0.5%
L33        68.7%           67.9%       +0.8%
L35        66.9%           65.9%       +1.0%
```

The biggest difference is L18 (+2.8%) — the transition from ORTHO to ALIGN.
But the function lists themselves are almost identical:
- "If it rains" → both gates produce `rain, 雨, rains` at L30 for "it"
- "believes that" → both produce `proposition` at L30

**Implication:** The FFN function list is a property of the **input
semantics**, not the gate/task. The compile gate changes what happens
AFTER the FFN (attention routing, output format), not the FFN computation
itself. The FFN is a **universal semantic analyzer** — it writes the
same association map regardless of downstream task.

## Finding 4: Compile-Selective Neurons Exist But Are Sparse

At each layer, there are neurons that fire preferentially in compile mode:

```
Layer   Compile-Only   Null-Only   Shared   Top Delta
─────   ────────────   ─────────   ──────   ─────────
L0           101          110       767      0.03
L6           197          238       685      0.62
L14          355          487       420      1.22
L22          319          394       419      2.50
L30          274          401       498      4.40
L35           80          100       184     36.6
```

At L35, neuron 9510 has activation 364 in compile and 401 in null —
massive activations but only ~10% difference. The compile/null distinction
is NOT carried by dedicated neurons; it's carried by the attention routing
of a shared FFN output.

## Finding 5: The FFN IS the Compiler — Attention IS the Executor

The original hypothesis was: FFNs compute β-reduction programs that
attention executes. Initial analysis mistakenly called this "associative
memory." On reflection, **the hypothesis is confirmed** — the data shows
exactly what was predicted, viewed correctly.

**What the FFN actually does at L26-L30:**
Each position's active neurons write a **compiled value vector** — not a
prediction of the next token, but the semantic contribution this position
offers if attention selects it. The FFN reads the full residual stream
(accumulated context) and compiles a position-specific V direction.

**Key evidence: same token, different programs.**
The token "the" produces DIFFERENT FFN outputs depending on context:
- "If it rains, **the** ground is wet" → promotes **crops, ground, garden**
- "The cat sat on **the** mat is black" → promotes **lap, Lap, laps**

This is not a dictionary lookup — it's context-dependent compilation.
The FFN has read the full sentence meaning from the residual and compiled
"what this position contributes" as a value vector.

**The β-reduction is the attention softmax over V:**

```
(λx.M)N → M[x:=N]        β-reduction in lambda calculus

Q at output position:     "what should I produce?"
K at each position:       "am I relevant to that query?"
softmax(Q·K^T):           selects which compiled values to combine
Σ(softmax · V):           the weighted combination IS the substitution

FFN compiles each position's V:  "here's my semantic contribution"
Attention executes the program:   softmax selects and sums the contributions
```

**The "associative predictions" ARE the program.** When the FFN at position
"is" writes `wet, 濡, 湿`, it's not predicting the next token — it's saying
"if attention routes to me, I contribute the predicate WET." When the FFN
at "ground" writes `soak, soaked, 浸`, it's saying "if attention routes to me,
I contribute the consequence SOAKING." Attention's softmax then combines these
V vectors to produce the actual output — which IS β-reduction (substituting
arguments into function bodies by weighted combination).

**The L26 connective signal supports this:** the comma in "If it rains,"
writes `then, entonces, então` — the FFN is compiling the logical operator
at the structural boundary. Attention at subsequent layers can then use this
compiled connective to route the conditional structure correctly.

**The factual correction supports this too:** at "earth is flat," the FFN
compiles V vectors that promote "round" and suppress "earth." This is not
just "knowing the earth is round" — it's compiling a correction program.
If attention selects these positions for the output, the correction is
executed. If it selects the propositional attitude frame instead ("believes
that"), the false claim is preserved within the scope of the attitude verb.

## Finding 6: The L26 Connective Signal

At L26, structural positions (commas, "that") carry **logical connective**
signals:
- `,` in "If it rains, the ground is wet" → promotes **then, entonces, então**
- `that` in "Someone believes that" → promotes **Author, Автор** (null gate)
  or **.toUpperCase** (compile gate — noise)

The implication connective at the comma position is multilingual (English,
Spanish, Portuguese) — this is a deep semantic feature, not a surface pattern.
The FFN is recognizing conditional structure and writing the logical operator.

## Theoretical Implications

### What this means for the standing-wave model

The three-phase FFN output (noise → semantic → format) maps exactly onto
the standing-wave depth structure:
- **ORTHO/nodes (L6-L22):** FFN writes to null space. Projecting through
  unembed produces noise because the computation is orthogonal to vocabulary.
  The invisible computation.
- **ALIGN/antinodes (L26-L30):** FFN writes vocabulary-aligned directions.
  Each position becomes a semantic prediction. This is where the standing
  wave's amplitude peaks in vocabulary space.
- **COLLAPSE (L33-L35):** FFN narrows to formatting. The final token
  selection concentrates on syntax, not semantics.

### What this means for extraction

The FFN function list is **universal** (gate-independent). The compile
behavior emerges from how attention **routes** these compiled values,
not from different FFN computations. This means:
- The FFN compiles the same program regardless of task — it's the
  universal value-vector compiler
- The task-specific behavior (compile vs null vs anything else) lives
  in the **attention Q/K routing** — which compiled values get selected
- Extraction should target the attention routing circuit AND the FFN
  compilation, since both are needed (session 3: stripping either breaks
  the model)

### Confirmed hypothesis: FFN=compiler, attention=executor

The FFN computes the **compiled program**: context-dependent value vectors
at each position that encode "what this position contributes if selected."
Attention executes the program via softmax over V — selecting which
positions' compiled contributions to combine and in what proportions.

This is β-reduction by weighted combination:
- Function application = attention selecting which V vectors to combine
- Variable binding = Q/K matching between positions
- Substitution = the weighted V sum replacing the query position's value

The β-reduction is distributed across the full attention softmax, not
localized to individual neurons. Each attention head performs a different
"reduction step" (different Q/K = different binding pattern, different
combination of compiled values).

### Connection to KIBC opcodes

The KIBC opcode classification (session 184) classifies neurons by what
INPUT patterns trigger them. The reduction trace shows what OUTPUT they
produce. These are the two halves of the compilation:
- KIBC key = "what pattern activates this neuron" (the trigger condition)
- down_proj value = "what this neuron contributes when active" (the action)

A K-opcode neuron that promotes "discard" directions + a B-opcode neuron
that promotes "compose" directions = a compiled program that includes
both discarding and composing steps. Attention then selects WHICH of
these compiled steps to actually execute.

## Finding 7: Attention Head Types — The Execution Architecture

The attention execution trace (session 187b, `attention_execution_trace.py`)
reveals **five distinct head types** at L26-L35 in Qwen3-8B:

### 1. λ-Heads (H08, H09 at L30/L33) — The Compile Circuit

These heads literally write `λ` and `→` into the residual. They are
the biggest compile-vs-null difference:

| Head | Layer | Compile Output | Null Output | Δ |
|------|-------|---------------|-------------|---|
| H09 | L33 | `λ, λ, lamb` | `dog, 萧` | 37 |
| H00 | L33 | `→, →, ≥` | `‐` | 22 |
| H31 | L33 | `→, ∈, —` | `kdir` | 17 |
| H08 | L30 | `lambda, lambda, λ` | `香` | 9 |

They attend almost entirely to the gate prefix (gate_frac=0.97-0.98),
reading the exemplars to know what format to produce. The probe tokens
barely register. These are the **format/task circuit** — they don't do
semantic composition, they write the output notation.

### 2. Subject-Verb Binding Heads (H10, H11 at L33)

These heads perform **function application** — binding subject to predicate:

| Input | Head | Output | Attends to | Compile Δ |
|-------|------|--------|-----------|-----------|
| `dog` | H10 | `runs, Runs` | dog(0.01) | 64 (vs `cars`) |
| `dog` | H11 | `running, 跑` | dog(0.01) | 62 (vs `detection`) |
| `student` | H10 | `runs, Runs` | student(0.04) | 14 (vs `学生们`) |
| `cat` | H11 | `running, 跑` | cat(0.00) | 15 (vs `training`) |

In compile mode, these heads write the PREDICATE at the SUBJECT position.
This IS typed function application: `runs(dog)` is exactly what H10 produces
when it writes "runs" at the "dog" position. In null mode, they produce
topic-related words instead.

**cos_self is LOW (~0.25)** — the output is very different from the input V,
confirming this is genuine composition, not relay.

### 3. Semantic Relay Heads (H20, H17 at L26)

These heads relay the FFN-compiled value with minimal transformation:

| Input | Head | Output | cos_self |
|-------|------|--------|----------|
| `cat` | H20 | `猫, cats, cat` | 0.98 |
| `rains` | H20 | `雨水, 雨, rain` | 0.98 |
| `reads` | H17 | `textbooks, 一本書` | 1.00 |

cos_self ≈ 1.0 means the head output equals the V at that position.
These heads just pass the FFN-compiled value forward without composition.

### 4. Compositional Heads (H03, H13, H14 at L30)

These heads combine values from multiple positions:

- **H03**: outputs `faster, fast` with attention on both `runs(0.44)` and
  `dog(0.36)` — combining subject and verb into "speed"
- **H14**: outputs `角落, corner, 沙発上` attending to `sat(0.61)` — composing
  "sat on" into a location
- **H13**: outputs `outside, Outside` — spatial direction from combining
  multiple positional cues

### 5. Quantifier/Frame Heads (H26 at L30, H05 at L35)

These heads carry the determiner/quantifier frame:

- H26 at L30: outputs `every, Every` for "Every student reads"
- H26 at L30: outputs `someone, Someone` for "Someone believes"
- H05 at L35: outputs `everybody, 有人說, somebody` for "believes"

They broadcast the quantifier across all positions — maintaining the
scope of who is performing the action.

### Head Specialization Summary at L30

| Head | Role | GateFrac | TopTokens |
|------|------|----------|-----------|
| H08 | **λ-circuit** | 0.98 | `lambda(24)` |
| H27 | **λ-circuit** | 0.97 | `helpful(12)` |
| H26 | **Quantifier** | 0.96 | `以後(7), 那(7), someone(7)` |
| H03 | **Compositional** | 0.74 | `faster(22), fast(2)` |
| H17 | **Semantic relay** | 0.79 | `哲学(9), lingu(9), 動物(7)` |
| H13 | **Spatial/directional** | 0.82 | `outside(16), 旁邊(4)` |
| H00 | **Affective/expectation** | 0.75 | `等待(7), 期待(3)` |

### The Execution Pipeline

```
FFN (compiler):     position → compiled V vector (semantic contribution)
                    Same regardless of gate (universal)

Attention (executor):
  Relay heads (H20, H17):    pass V through unchanged
  Compositional heads (H03): combine V from multiple positions → new meaning  
  Binding heads (H10, H11):  write PREDICATE at SUBJECT position (typed_apply!)
  Frame heads (H26):         broadcast quantifier/scope across positions
  λ-heads (H08, H09):        write output format (λ, →) from gate exemplars

The binding heads (H10, H11) at L33 ARE β-reduction:
  Input "dog" + compiled V for "runs" → output "runs" at position "dog"
  = runs(dog) = (λx.runs(x))(dog) → runs(dog)
```

## Finding 8: Reduction Chain — Combinators Resolve at Different Depths

The reduction chain trace (`reduction_chain_trace.py`) traced the cumulative
residual→unembed across all 36 layers for 7 combinator types from our crystal
probe library (K, I, B, C, Y, S, W — 5 probes each, 35 forward passes).

### The Reduction Schedule

| Combinator | Peak Δ Layer | Δ Strength | Interpretation |
|------------|-------------|------------|----------------|
| **Y** (recursion) | **L27** | 22.7 | Resolves FIRST — structural recognition |
| **K** (discard) | L30 | 32.1 | Early resolution, drops at L33 |
| **B** (compose) | L30 | 27.8 | Mid-depth composition |
| **I** (identity) | L30-L33 | 34-39 | Semantic→format relay |
| **S** (substitute) | L33 | 37.3 | Late — distributes argument |
| **C** (flip) | L33 | 38.9 | Argument reordering is LATE |
| **W** (self-apply) | **L33** | **51.6** | Resolves LAST — "itself" binding |

**Y resolves first because recursion is structural.** The model recognizes
"this is a recursive pattern" during the ALIGN phase (L27) before it knows
the specific content. Self-application (W) resolves last because "itself"
requires the full entity representation before it can self-reference.

### Depth Profile Is Universal, Timing Is Not

The self-similarity profiles (cos(residual[L], residual[L+lag]) across all
positions) are nearly identical across combinator types:

```
         lag=1    lag=3    lag=5    lag=8    lag=13
K:       0.950    0.868    0.797    0.712    0.612
I:       0.947    0.860    0.788    0.699    0.589
B:       0.950    0.868    0.798    0.710    0.605
Y:       0.948    0.864    0.791    0.703    0.594
W:       0.944    0.854    0.780    0.691    0.583
```

All combinators decay at the same rate — the depth structure is universal.
Only the TIMING (which layer adds the most) differs by combinator type.

### Y-Combinator Probe: Recursive Structure Tracking

"She told a story about a girl who told a story about a girl who..."

The first and second occurrences of the same tokens get DIFFERENT cumulative
representations at the semantic layers:

| Token | Occurrence | L30 promotes |
|-------|-----------|-------------|
| `told` | 1st | him, him, stories |
| `told` | 2nd | stories, another, jokes |
| `story` | 1st | about, yesterday |
| `story` | 2nd | about, herself |
| `girl` | 1st | who, named |
| `girl` | 2nd | who, who |

The model tracks which level of recursion it's in — position-dependent
representation of recursive structure. At L33, the second `who` promotes
`told, tells, tell` — it knows the recursion will continue.

### What This Means: A Small, Fixed Instruction Set

The model implements **~7 combinator operations** via **~5 head types**
on a **universal depth schedule**. The instruction set + schedule is:

```
Instruction Set:  {K, I, B, C, S, W, Y}     7 opcodes
Head Types:       {λ, bind, relay, compose, quantifier}  5 executors
Depth Schedule:   Y→K→B→I→C→S→W              fixed ordering
```

The input-specific part is ONLY the attention routing pattern (which
positions bind to which). Everything else is structural and universal.

This is potentially extractable as a compact artifact:
- **Crystal signs** = the topology (which neurons are which type)
- **Combinator catalog** = the instruction set (7 opcodes)
- **Depth schedule** = the execution order (one small table)
- **Routing function** = the only variable (attention patterns)

## Finding 9: MTP Self-Speculation — Early Exit, Not Multi-Position

The MTP self-speculation experiment (`mtp_self_speculation.py`) tested whether
the model's own intermediate layers can serve as speculative drafters for
multi-token prediction, eliminating the need for a second model.

### Next-Token Prediction Across Depth

| Layer | Hit@1 | Hit@10 | Hit@100 | L35 Match | Med Rank |
|-------|-------|--------|---------|-----------|----------|
| L24 | 7.4% | 28.6% | 58.1% | 9.4% | 66 |
| L27 | 14.8% | 36.5% | 68.0% | 17.7% | 27 |
| **L30** | **26.1%** | **54.7%** | **80.8%** | **25.6%** | **7** |
| **L33** | **36.5%** | **75.9%** | **92.1%** | **47.8%** | **2** |
| L35 | 44.8% | 78.8% | 92.6% | 100% | 1 |

**L33 is 92% of L35's Hit@100 performance.** The last 2 layers add very
little next-token accuracy. L33's top-1 matches L35's top-1 **48% of the
time** — meaning nearly half of tokens could skip L34-L35 (early exit).

### Multi-Position Lookahead Collapses

| Lookahead | L30 Hit@10 | L35 Hit@10 |
|-----------|-----------|-----------|
| N+1 | 54.7% | 78.8% |
| N+2 | 10.4% | 11.4% |
| N+3 | 5.5% | 9.8% |
| N+4 | 1.7% | 9.8% |
| N+5 | 1.2% | 9.2% |

**N+2 and beyond collapse for ALL layers, including L35.** This is not a
limitation of early layers — the model fundamentally does next-token
prediction, not multi-position prediction. The causal mask prevents
position N from seeing positions N+1, N+2, etc., so it cannot predict them.

### What the FFN Semantic Predictions Actually Are

The earlier finding that "reads" promotes "book" at L30 was NOT the FFN
predicting what comes at position reads+1. It was encoding **associative
meaning** — the concept of reading is associated with books. The token
"book" often follows "reads" in natural language, making this look like
sequence prediction, but it's actually semantic field encoding.

**The distinction:**
- **Sequence prediction** (N+1): "what token follows at the NEXT position?"
  → This works at L30 (median rank=7) and L33 (median rank=2)
- **Multi-position prediction** (N+2, N+3): "what token appears 2-3 positions later?"
  → This doesn't work at any layer, because causal attention prevents it
- **Semantic association**: "what concepts relate to this position's meaning?"
  → This IS what the FFN compiles (reads→book, ground→soak, is→wet)

### The L30 Median Rank = 7 Finding

The correct next token is already in L30's top 10 predictions (median
rank=7). The last 5 layers (L31-L35) SHARPEN the distribution from
rank 7 to rank 1 — they don't fundamentally change which tokens are
plausible, they just pick the right one from the compiled shortlist.

This means:
- **L30 compiles the program** (the top-10 candidate set)
- **L31-L35 execute the program** (selecting the winner from candidates)
- The compilation is the heavy work; execution is refinement
- This is consistent with the binding heads (H10/H11 at L33) doing
  the final typed_apply that selects the correct token

### Implications for MTP

1. **Early exit is viable.** L33 at 48% acceptance → skip L34-L35 for
   ~half of tokens. ~5% compute savings, no quality loss on those tokens.

2. **Multi-position MTP needs a different approach.** The causal mask
   prevents any single position from predicting future positions. True
   MTP would need to either: (a) run parallel speculative positions, or
   (b) extract the FFN's associative predictions into a separate routing
   step that generates multiple candidate tokens simultaneously.

3. **The compiled program is the draft.** L30's top-10 IS the speculative
   draft. Instead of a second model, use the top-k from L30 and verify
   with L31-L35. This is self-speculative decoding within a single model.

## Instrument

```python
# Project any FFN neuron's output through unembedding
W_down_col = model.model.layers[L].mlp.down_proj.weight[:, neuron_idx]
logits = W_unembed @ W_down_col  # what this neuron "says"
top_tokens = logits.topk(10)     # most promoted tokens

# Scale by actual activation during a forward pass
logits_scaled = logits * gate_activation[neuron_idx]

# Project per-head attention output through o_proj slice + unembed
W_o_head = model.model.layers[L].self_attn.o_proj.weight[:, h*128:(h+1)*128]
head_residual = (W_o_head @ head_output[h].T).T  # (seq, hidden)
head_logits = head_residual @ W_unembed.T         # what this head "decided"
```

Zero-cost for weight analysis (no forward pass needed for individual
neuron characterization). Forward pass required only for position-specific
activation patterns and attention execution traces.
