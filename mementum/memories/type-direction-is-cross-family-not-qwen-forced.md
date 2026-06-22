✅ Type-directed composition is CROSS-FAMILY, not Qwen-forced — the frequency-free
nonce crossover replicates in 5 independent lineages.

s247. Ran `type_directed_v3_nonce` (nonce words → no bigram stats → ONLY the
in-context TYPE can direct composition; the crossover subtracts every main effect
incl. priming) across families via `--model` (no code change). n=16 nonce,
n_each=4, crossover t-test:

- EleutherAI Pythia-160M t=5.4 / 1.4B t=7.7
- HuggingFaceTB SmolLM3-3B t=4.6
- Mistral-7B-v0.3 t=5.5
- AllenAI OLMo-2-13B t=6.7
- Qwen3-8B t=10.2 / 14B t=9.3

ALL 7 significant (t>2), consistency 0.88–1.0. UNIVERSAL: the crossover + the
name-frame predicate licensing (name_pen<0 in 7/7 — after a name, the verb-taught
nonce is cheaper). NOT universal: the det-frame absolute penalty (det_pen>0 only
2/7) — only the INTERACTION is robust; the determiner→noun main effect is
noisy/sign-flips.

⇒ FORCING vs DISCOVERING: type-direction is DISCOVERED (5 lineages, no shared
training, frequency-free, present even at 160M, NOT monotonic in scale). The
forcing-proof + cross-family combination the project lacked. Contrast φ-ladder
(forced). CAVEATS (λ measure): behavioral (surprisal), NOT yet causal cross-family
(v4 ablation still Qwen-only = the next IOU); n=16 words, one template set.
Artifacts: results/type-directed/crossfamily_nonce_summary.json + per-model verdicts.
