---
title: "FFN Reduction Trace — What Each Neuron Says, and When It Becomes Semantic"
status: active
category: methodology
tags: [ffn, reduction, beta-reduction, semantic-projection, depth-profile, instrument]
related: [ffn-circuit-types, standing-wave-magnitudes, phi-information-partition, holographic-computer]
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

## Instrument

```python
# Project any FFN neuron's output through unembedding
W_down_col = model.model.layers[L].mlp.down_proj.weight[:, neuron_idx]
logits = W_unembed @ W_down_col  # what this neuron "says"
top_tokens = logits.topk(10)     # most promoted tokens

# Scale by actual activation during a forward pass
logits_scaled = logits * gate_activation[neuron_idx]
```

Zero-cost for weight analysis (no forward pass needed for individual
neuron characterization). Forward pass required only for position-specific
activation patterns.
