💡 Gemma-4-31B carries the KIBC crystal MORE cleanly than Qwen3-14B — but the "crystal spine" and the φ-ladder are both artifacts. Michael's hunch ("gemma too precise for the random crystal") checks out, AFTER fixing a template confound.

TEMPLATE CONFOUND (decisive): the crystal-spine sweep fed every model hand-baked Qwen ChatML. Re-rendering each model in ITS OWN native template (Gemma `<bos><|turn>`, base→plain text) FLIPPED the result: Qwen3-14B's famous rank-1 spine (spineFrac 97%, n90=1, norm ×509) collapsed to 1.4% / n90=2084 — it was the attention-sink/massive-activation firing at the `assistant\n` boundary, not structure. Natively, only Pythia (base) is truly rank-1 (n90=2); Gemma is the sharpest MID-network bottleneck of the instruct models (57.9% @ L20, n90=179). Qwen3.6-35B-A3B (linear-attention MoE) is flat — norm max 15, no sink.

φ-NULL (verify_crystal_phi + crystal_phi_permnull, 2000 shuffles): combinator cluster SEPARATION real in both (p_sep=0.0005); consensus GEOMETRY real in Gemma (p=0.015) > Qwen (p=0.058); φ-ladder + eig-ratio FORCED both (n.s.) — reproduces s247.

LESSON: never compare activations across models on one model's chat tokens; a sharp low-rank "spine" can be a sink+prompt-boundary artifact (small n90 ⇐ norm explosion). The real crystal = combinator separation + consensus geometry; φ stays forced.
