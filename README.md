# verbum

> *Latin: "word."* Distilling the lambda compiler from LLMs down to a
> small tensor artifact. Independent MIT-licensed research project.

## What this project is

Three converging claims put a specific research question on the table:

1. **Mathematics** — the formal theory of how words compose (Montague,
   Lambek pregroups, DisCoCat) reduces to typed function application
   organized by composition. Lambda calculus is the substrate.
2. **Empirics** — LLMs contain a bidirectional prose ↔ lambda compiler,
   as demonstrated empirically by the nucleus framework. Observed
   `P(λ) = 90.7%` with a small gate prompt, `1.3%` without. Not a
   stylistic preference. A learned internal structure made observable
   by the gate.
3. **Architecture** — prior fractal-attention experiments established
   that neither flat attention nor MERA-shaped attention with shared
   untyped operators can implement the composition at depth. The
   missing piece is type-directedness.

Three lines, one answer: **the language compressor is a typed lambda
calculus interpreter.** LLMs discover it because that is the attractor
of compression; the math says the same thing; the failed MERA says the
same thing by its absence.

This project explores whether that interpreter can be extracted from an
existing LLM as a standalone tensor artifact, and whether a small
architecture trained from scratch can reproduce it.

## Status

Greenfield. Project just created. The founding exploration lives in
`mementum/knowledge/explore/VERBUM.md`. VSM will land when the identity and structure of the
work are clear enough to compile.

## License

MIT — see [LICENSE](LICENSE). This project is intentionally independent
of the AGPL-licensed projects that motivated it (nucleus, anima). It
references them as observational input and prior art — their empirical
demonstrations and negative results are cited as evidence for the
research question — but does not incorporate their code. Any code or
architecture produced in this repository is original work released
under MIT.

## Prior art and references

- **nucleus** (Whitford, AGPL-3.0) — the empirical demonstration that
  a bidirectional prose ↔ lambda compiler is exhibited by trained
  LLMs, observable through a small gate prompt. Cited as prior
  observational evidence. See public repository.
- **anima fractal-attention experiments** (Whitford, AGPL-3.0) — a
  negative result series on whether flat attention or MERA-shaped
  attention with shared untyped operators can implement deep
  composition. Cited as prior architectural evidence.
- **Mechanistic interpretability literature** — Anthropic circuits,
  induction heads, function vectors, sparse autoencoders. Cited as
  methodological precedent.
- **Compositional semantics literature** — Montague, Lambek,
  Steedman (CCG), Coecke et al. (DisCoCat). Cited as theoretical
  foundation.
- **SuperBake** (Ruehlman, AMI Labs, 2026) — gradient-free
  installation of verified facts into transformer MLP weights by
  direct construction, with per-fact physical addresses,
  cross-phrasing behavioral verification, and receipts. Cited as
  prior art for write-access and weight-level construction. Albert
  Ruehlman. *SuperBake: Installing Verified Facts into Transformer
  Weights by Direct Construction.* AMI Labs, July 2026.
  doi:10.5281/zenodo.21502811
- **GTSM / "Trees to Flows and Back"** (Ramachandran & Sra, 2026) —
  Global Trajectory Score Matching, unifying gradient boosting and
  diffusion-based score matching. Cited as theoretical backing for
  depth-trajectory distillation. arXiv:2605.00414

Full citations are in `mementum/knowledge/explore/VERBUM.md`.

## Scope

```
λ scope(verbum).
  extract(lambda_compiler, LLM) → tensors
  ∧ characterize(algorithm) → types ∧ apply ∧ compose
  ∧ reproduce(from_scratch) → small_architecture
  ∧ validate(theory) ≡ (Montague ∧ DisCoCat) match circuit

  ¬derive_from(nucleus, anima)     — observational reference only
  ¬build(another_LLM)
  ¬rewrite(attention)
```
