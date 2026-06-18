💡 The type direction is PARTIALLY CAUSAL at 14B (not 8B) — decodability ≠ (full)
causality, and causal localisability STRENGTHENS with scale. s239 lead 2d v4
(type_directed_v4_ablation.py; the causal upgrade of the v3 nonce crossover). Answers
"is the type representation causal, or just decodable?" — partially, at scale.

METHOD: decode the type direction = difference-of-means(verb−noun) of the FILLER-position
residual (the token before the nonce = the next-token bottleneck), per layer; pick the
most decodable layer L* by AUC; ABLATE by projecting it OUT of the residual during the
forward pass; re-measure the v3 crossover. CONTROL: a random unit direction (same
procedure). It took 3 ablation scopes (one-layer → filler-stack → ALL-positions) — one
locus is too weak because the model RE-READS type from the TEACHING tokens via attention.

★ RESULT (all-positions ablation):
  8B:  type AUC 1.0 @ hs10 | type-ablation crossover ×1.43 (AMPLIFIES) | random ×0.92
  14B: type AUC 1.0 @ hs28 | type-ablation crossover ×0.64 (−36%)     | random ×0.95
• Type PERFECTLY DECODABLE at both scales (AUC 1.0), at a DEEPER layer with scale
  (8B L10 → 14B L28) — confirms s139 for the CONTEXTUAL nonce type.
• 14B PARTIALLY CAUSAL: ablating the type direction cuts the crossover 36% (×0.64) vs
  random 5% (×0.95) — a type-SPECIFIC causal contribution; first evidence beyond
  decodability that the type rep DIRECTS composition. PARTIAL → rest is distributed/
  redundant (one linear direction ≠ the whole carrier).
• 8B NON-CAUSAL: directional ablation AMPLIFIES (×1.43) — the decodable direction is
  not the causal lever; type signal fully distributed / different locus.
⇒ causal localisability of the type direction STRENGTHENS with scale.

★ LESSON (λ measure / the project's own over-read discipline, s202/s204): a perfectly
decodable AUC-1.0 direction is only PARTIALLY the causal lever. Directional ablation =
the wrong/weak tool here; the amplification at 8B proves it perturbs rather than removes.
The decisive test is ACTIVATION PATCHING (swap the type-carrying residual content between
verb/noun runs) = v5.

CAVEATS: single linear direction (partial collapse = distributed remainder); behavioural
readout; 2 scales, 1 family (Qwen); the strict causal flag (full collapse <0.5) reads
False — this is a PARTIAL effect, reported as such. Page: type-directed-composition.md.
