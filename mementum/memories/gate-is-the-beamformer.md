💡 The SwiGLU gate IS the holographic aperture selector, not the key-match.

Session 141. Probed Qwen3-32B L63: 89% of inactive neurons are killed by
silu(gate_proj), not up_proj. The key (up_proj) matches broadly — it's
promiscuous. The gate says "no" to 89%. Gate/up magnitude ratio for active
neurons: 3.9×. This means gate_proj signs are MORE critical than up_proj
signs for the addressing topology. We were only etching up_proj + down_proj.
Added ffn_gate_plate to V13 with SwiGLU activation. Run 9 CE=11.27 at
step 1 vs run 8 CE=11.88 — immediate improvement from gate etch.
