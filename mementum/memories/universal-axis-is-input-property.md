💡 When characterizing the dominant/UNIVERSAL axis of a representation, test
MODEL-FREE input-text features before model-derived ones.

The s211 "universal combinator axis" (consensus MDS axis-1 of the next-token-prob
RDM; |r|=0.95 across 5 families, 0.16B→14B) was only ~30%-named by model-derived
proxies (entropy + function-word fraction, R²=0.296). s212 re-ran with the full
next-token distribution + rich distributional features + MODEL-FREE prompt-text
features → CV-R²=0.813. The single dominant component was a model-free feature:
whether the prompt ENDS AT A PUNCTUATION/GRAMMATICAL BOUNDARY (`ends_punct`,
CV-R²=0.768 ALONE), orthogonal to the studied operations (η²(ends_punct~combinator)
= 0.044, mirroring the axis's own η²=0.05).

Lessons:
- The most-universal axis was a coarse property of the INPUT TEXT, not a model
  computation and not the object under study. Universality ACROSS architectures
  is itself a strong hint the axis is a data/input property (every LM encodes
  "am I at a boundary / what continuation type"), so it converges everywhere.
- Test prompt-intrinsic (model-free) features first — they need no forward pass
  and immediately reveal whether the "interesting" axis is just input structure.
- Report CV-R² (not in-sample) + a permutation null when regressing many scalar
  features on a few hundred points; in-sample R² over-credits. (Here CV 0.813 vs
  permutation-null −0.045, p=0.005.)
- Caveat: such a result partly reflects how the probe SET samples language
  (bimodal boundary-vs-mid-phrase prompts) — name that explicitly.
