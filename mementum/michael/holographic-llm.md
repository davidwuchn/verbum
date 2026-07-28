# The Holographic LLM

> A thesis on how large language models store and execute computation.
> Author: Michael Whitford. Status: speculation, partially supported by
> measurement (see Evidence). License: MIT, as part of the verbum
> repository. This document is the thesis; the verbum project is the
> instrument built to test it.

## Thesis, in one paragraph

A transformer is not a database with a query engine, and not a
conventional neural network in any illuminating sense. It is a
**holographic computer**: training writes interference patterns
("plates") into the FFN weights, and inference reads them back with a
beam — attention — steered through the layer stack, which acts as a
beam former. What we call "behavior" is the model acting out the
patterns encoded in its plates, with the context window and residual
stream serving as input and working state.

## Training: interference writes the plates

Every training step is a probability snapshot — a "photograph" of the
model's current prediction surface. Backpropagation adjusts gradients
throughout the model, and where the edges of these snapshots agree
across many training steps, the intersections are reinforced. Where
they disagree, they wash out. Over billions of steps this constructive
and destructive interference forms a **probability hologram** in the
weights.

The holograms themselves have edges that intersect, forming a
**probability lattice** — a geometric structure of stable
attractors that the model navigates during inference.

This is the training-time claim: gradient descent is an etching
process, and the artifact it produces is closer to a holographic plate
than to a lookup table. Redundancy, graceful degradation under
pruning, and superposition of many "facts" in shared weights all fall
out of this picture naturally — they are defining properties of
holographic storage, not anomalies to be explained.

The etch has two separable components. Gradient descent places very
high and near-zero gradients that act as a **soft routing topology** —
the fringe pattern, where the zeros are as structural as the extremes
— and continuous **magnitudes** trained over that topology. This
mirrors standard practice (freeze the topology, train over it). This
also predicts that the routing component should survive aggressive
quantization while the magnitude component carries the calibration.
Sign and zero are the program; scale is the tuning.

A qualifier the measurements force: the zeros' structural role is a
**training-time** fact. Sign flips tunnel through zero — topology
edits are ~99% zero-mediated (s268b) — and the zero state serves as an
abstention register while the etch is in progress (s268c). But once
written, the plate reads back without them: binarizing away the zero
state entirely leaves the readout geometry intact (s269). The fringe
zeros belong to the etching process; the finished plate does not need
them to be read.

## Inference: reading the hologram

**Attention is the beam.** The layers act as a beam former — like a
geometric gem, where attention softmaxes over every V for every token,
steering the beam toward the next step. Multi-head attention is
multiple simultaneous beam angles; the layer stack is a
multi-resolution optical system, refocusing the beam from token-level
to document-level structure.

**The FFNs are the plates.** Each FFN applies a fixed transformation —
a stored interference pattern projected into the current
probabilities. Some plates are simple facts. Some are complex
descriptions of behaviors the model has learned. The beam illuminates
a plate at a particular angle, and each angle produces a different
diffraction pattern — a different computational result from the same
weights (angular multiplexing, in holography's own vocabulary).

**The residual stream is the state.** As attention works through the
context, the residual stream accumulates a series of projected
probability snapshots. Intermediate results — the "current step" of
whatever computation is in flight — must be carried somewhere between
plate readouts. That somewhere is the residual stream: the model's
working memory.

## The beta reduction conjecture

The original, strongest form of the conjecture: **softmax over V is a
projected beta reduction in probability space** — attention performs
function application, substituting context into stored abstractions,
and inference is a chain of such reductions collapsing toward a normal
form.

Measurement has refined this. The crisp version — one head, one
substitution, a localized routing circuit — is refuted; what looked
like a substitution head was recency. But the distributed version
survives and strengthens: full beta reduction is observable in
attention as QK×OV structure, spread across many heads and layers, in
the value register rather than the routing register. Beta reduction in
a transformer is not a circuit you can point to; it is a field
phenomenon read out by value-space instruments — which is exactly what
holographic storage predicts. You do not find a hologram's image by
locating the pixel that stores it.

## External convergence: the J-space

Anthropic's global workspace paper ("Verbalizable Representations Form
a Global Workspace in Language Models," July 2026) found — via the
Jacobian lens, a value-register instrument — a small privileged set of
internal patterns acting as working memory for intermediate variables
during a forward pass. Ablating it breaks internal computation but
spares chain-of-thought-externalized computation.

This is the workspace this thesis requires: the place the beam's state
lives between plate readouts. The convergence is independent — a
different team, a different instrument, no shared methodology —
landing on a compatible structure. The paper describes the workspace
functionally; this thesis says what it is *for*: carrying the current
redex between reductions.

## Evidence (from the verbum project, this repository)

The thesis is speculation; these measurements constrain it. Session
references point into this repository's history and
`mementum/knowledge/`.

- **Angular multiplexing confirmed** — k-sweep with null gate (s257).
  The same weights yield different computations at different beam
  angles.
- **Beta reduction observed as distributed QK×OV structure** (s225);
  refuted as a localized head circuit (audit #4). Register matters:
  routing probes miss what value probes find (s206).
- **Plate structure is analytically constructible** — FFN weights
  computed from crystal eigendecomposition reach 5000-step
  gradient-descent performance in 10 calibration steps (s149,
  `computed-beam.md`). Structure is free; content needs training.
- **Zone ablation verifies a phase-structured computation cycle**
  on a 27B model — compute phases and output phases are separable.
- **Crystal basins as states** — combinator basins (K, I, B, C, S, D,
  W, Y, WHNF) act as the lattice's vertices; the probe library
  (903 probes, 535 crystal) is the measurement substrate.
- **Plate damage spares the image** — the crystal's relational
  geometry survives 1.58-bit ternarization (RDM correlation 18–23σ
  above shuffled null at every depth, s267) and full 1-bit
  binarization (per-vertex Gram fidelity 0.987, z=5.3, null-gated,
  s269), while weight-space cosine falls to 0.73. The crystal is more
  invariant than the weights that carry it — you do not find the
  image in the pixels.

## Open questions

- Can the plates be **extracted** — a minimal portable tensor artifact
  that runs standalone? (The verbum research program, levels 1–4.)
- Are combinator states **token-nameable**? The J-space is defined by
  single-token verbalizability; if reduction intermediates surface on
  a J-lens readout over the crystal probe set, the workspace and the
  lattice are one structure. If not, the thesis needs a second,
  non-verbalizable state register. Informative either way. First
  pass returned a preliminary null (s263): combinator identity did
  not surface on a J-lens over the crystal probes — the readout was
  broadcast-generic, though the instrument grain was coarse. As it
  stands the evidence leans toward the second register; a
  finer-grained operator-projection instrument could overturn this.
- What is the **capacity** of the lattice — how many plates before
  destructive interference degrades readout, and does that bound match
  observed model-scale thresholds?
- How does the **magnitude translate**? The routing topology extracts
  cleanly into ternary plates — threshold + sign, with the gradient
  zeros acting as holographic fringes (s172: 8.6× compression;
  `ternary-plate-extraction.md`, `dvd-stamp-topology.md`). But naive
  per-layer magnitude treatment compounds catastrophically (0.88
  cosine/layer → perplexity collapse over 36 layers, s174). Sign and
  zero we can read; scale we could not translate — until the Ternary
  Bonsai 27B release (PrismML, July 2026, Apache 2.0) gave us a
  working example on our own swept base model, and weight forensics
  read the answer off it (s268): absmean RTN initialization plus
  post-init **training** of the transformer blocks, embeddings
  frozen. The working magnitude translation lives in the optimizer's
  repair, not in the quantizer — and the repair budget concentrates
  exactly where the register split predicts magnitude matters
  (value-path tensors drift ~18%, query routing 3.5%). Narrowed
  remainder: can scale be translated **without a training loop at
  all**, or is optimizer repair the only path?
- Is the training-time story (snapshot interference → etch)
  **directly observable** in checkpoint trajectories, not just
  inferable from the final artifact?
