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
> position is a **function list** — a set of token-space directions that
> the residual stream carries forward for attention to route.
>
> Key finding: FFNs become semantically interpretable at L26-L30 in
> Qwen3-8B (36 layers). Before that, projections are noise. After that,
> they are startlingly coherent associative predictions.

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

## Finding 5: The FFN is an Associative Memory, Not a Reduction Engine

The original hypothesis was: FFNs compute β-reduction instructions that
attention executes. The data tells a different story.

**What the FFN actually does at L26-L30:**
- Each position's active neurons collectively promote **associated concepts**
- "rains" → umbrella, 伞 (associated objects)
- "is" + "wet" → the FFN at "is" promotes "wet" (predicate completion)
- "believes" → proposition (frame recognition)
- "earth" + "flat" → the FFN promotes "round" (factual correction/association)

This is **associative next-token prediction**, not β-reduction. The FFN
at each position writes "what typically comes next or is associated with
this position's accumulated meaning." It's a **key-value memory** where:
- Key = the residual stream at this position (accumulated context)
- Value = the aggregate `down_proj` direction (associative prediction)

**The β-reduction happens in the INTERACTION between FFN output and
attention routing**, not in the FFN alone. The FFN provides the vocabulary
of possible continuations; attention selects which continuations to
actually route to the output.

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
behavior emerges from how attention **routes** these universal semantic
predictions, not from different FFN computations. This suggests:
- Extraction should focus on the attention routing circuit, not the FFN
- The FFN is substrate (compression machinery, as session 3 concluded)
- The compile function lives in the attention heads that READ the FFN output

### Revised hypothesis: FFN as associative memory → attention as router

The FFN doesn't compute β-reductions. It computes an **associative field**
at each position: "given everything this position knows, here are the most
associated concepts in vocabulary space." Attention then routes these
associations between positions to compose the final output.

The β-reduction, if it exists as a discrete operation, is in the
**attention-mediated composition** of these associative fields, not in
the FFN itself.

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
