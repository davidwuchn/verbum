💡 The type direction is DECODABLE in every family (AUC 1.0) but CAUSALLY PARTIAL —
and the causality is NOT Qwen-forced (Mistral-7B strongest, Qwen-8B null).

s247. v4 causal ablation (project the decoded type direction OUT of the filler-stack
residual; control = random direction same magnitude; retained = ablated/baseline
crossover), n=16 nonce, n_each=4, across families:

- Mistral-7B: type_ret 0.29 / rand 0.91 → STRICT causal (the ONLY one)
- Pythia-1.4B 0.63 / OLMo-2-13B 0.63 / Qwen3-14B 0.64 (rand ~1.0) → directional
- SmolLM3-3B 1.04 / Qwen3-8B 1.43 → NULL (ablation doesn't cut the crossover)

DECODABILITY universal (AUC 1.0, 6/6). CAUSALITY directional in 4/6 (type-ablation
cuts the crossover ~0.6x vs random ~1.0x) across 3 INDEPENDENT lineages
(Mistral/Pythia/OLMo) + Qwen-14B; STRICT only Mistral-7B; NULL in SmolLM3 + Qwen-8B.
Even Qwen-14B is sub-strict (0.64).

⇒ FORCING vs DISCOVERING: NOT Qwen-forced — Mistral has the strongest causal grip and
Qwen-8B none (opposite of a Qwen artifact). The construction is discovered + cross-family;
causal localization via SINGLE-DIRECTION linear ablation is partial/method-sensitive
(decodability ≠ full causality, db5d4eb). CAVEATS: single-direction filler-stack ablation
→ a NULL is not decisive (type may be distributed); n=16, one template set. Apparatus:
v4 made architecture-agnostic (decoder_layers → GPTNeoX/Pythia). Artifacts:
results/type-directed/type_directed_v4_ablation_verdict_* + crossfamily_v4_ablation.log.
