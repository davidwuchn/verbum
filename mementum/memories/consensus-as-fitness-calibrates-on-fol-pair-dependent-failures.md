💡 Cross-model OUTPUT agreement works as a teaching-data fitness function, CALIBRATED on
lambda/FOL where ground truth exists: P(correct|AGREE) 0.73 (Qwen3-14B×OLMo-2-13B) / 0.80
(Qwen3-14B×Gemma-4-31B-it) vs P(correct|DISAGREE) 0.00/0.10 — REPLICATED across 2 independent
lineages (s246, binding.json, 25 probes). Output consensus needs NO frame-alignment (cf the Gram
in combinator_map_consensus.py) — generated strings share the vocabulary = the cheap register.

🔁 The AGREED-ERROR set (both models same wrong answer = the blind spot) is PAIR-DEPENDENT, and
that IS the signal: OLMo-shared anaphora errors dissolved under the stronger Gemma → the new
shared error became sortal omission on bare quantifiers ("someone loves everyone" → both
∃x.∀y.loves(x,y), dropping person(), cross_jac=1.0). ⇒ ≥3 lineages = confidence GRADIENT not
binary; consensus also surfaces annotation-CONVENTION gaps, not just model errors.

⚠️ Gotchas: token-Jaccard is the scoring bottleneck (fix = predicate stemming
fly/can_fly·love/loves·pass/passed + lowercasing, lifted 0.44→0.73); instruct models (Gemma)
ECHO a raw few-shot completion → need --chat (tokenizer chat template). Lambda is BOTH calibrator
and corrector (override consensus with truth where it exists). Exploration tangent off the
compiler-as-loss main line — candidate source for the prose→LF front-end teaching data.
See knowledge/explore/cross-model-output-consensus.md; harness consensus_output_agreement.py.
