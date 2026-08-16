🚫 At the answer column of the prefill grid, value-weighted read-mass barely
differentiates ground-truth answers. s336, §P-CONE-ROUTING (UNDIFFERENTIATED),
Qwen3-14B, kernel-certified capture triples
(`results/p_cone_routing_s336/run_14b`): capture-free calibration poles with
OPPOSITE answers (B→y, P→e) separate by only +0.0016 median mass at the `e`
position (δ=0.78, p=0.0039 — real, but a whisker on a base of ~0.021); the
within-prompt selectivity Sel = mass(cap)−mass(e) is near-identical across the
poles (−0.0040 vs −0.0043); the term-final interior cell shows nothing
(p=0.94). The whisker is late-stack (≈0 through L12, peak L22–28 — s329
commit-assembled-late, third sighting) and answer-column-only.

Reading: answer selection is not delivered as a prefill-visible attention read
at usable SNR — the routing-register face of s317 tape-residency. Three
registers now agree: value (s317), magnitude (s335), routing (s336).

Consequence: correlational read-mass cannot answer the y-vs-e routing
question. The instruments that can: causal read-edge patching and decode-time
reads (→ ⚪ §P-ROUTING-CAUSAL; §P-REPL-DRIVER gives decode-time per-bounce
reads for free). Page:
explore/latent-reasoning-and-the-prefill-triangle.md §Result s336.
