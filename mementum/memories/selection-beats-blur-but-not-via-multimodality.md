💡 With a genuinely multimodal (sampled-LLM) teacher, best-of-K mode-commit
beats BOTH the mixture-blur baseline and the random-commit null — the first
significant selection win of the entire XM arc (G1 p=.0118, G2 p=.0042 @800,
n=20, 10k paired-permutation, Bonferroni-cleared; s299, results d3e2dae).
The s296–297 "exploration cannot improve distillation" close was
determinism-specific: no mixture ⇒ nothing to select; real mixture ⇒
selection pays.

BUT the mechanism is not the one the thesis named: the xm−rand gain is FLAT
across the multimodality gradient at the informative regime (G3 p=.404 @800;
d1 gain ≈ d2–3 gain). Selection acts as generic target-cleanup/denoising
(best-of-8 picks cleaner targets even where the teacher is unimodal), not
proven mode-exploitation. Verdict: SELECTION-HELPS-UNSTRUCTURED
(pre-registered).

Lesson pair: (1) crisp-commit beats soft-mixture where a mixture exists —
the collapse-operator frame survives its first weight-register test; (2) a
mechanism gate (G3) that fails while outcome gates pass is the yardstick
working — we get to keep the effect and must not keep the story.
