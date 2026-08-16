💡 In the prefill grid, the residual-displacement magnitude from a single-token
perturbation is governed by TOKEN DISTANCE, not by semantics. s335, Qwen3-14B,
kernel-certified lambda terms, Δ = ‖h_orig − h_pert‖/‖h_orig‖ at a cell,
layer-averaged:

    distance to readout cell:  1 → 0.099 · 2 → 0.069 · 3 → 0.059 · 12–18 → 0.043
    corr(distance, Δ) = −0.727, monotone

Consequences, all paid for in s335:
- Any design where the semantic role of a leaf is tied to its POSITION is
  confounded by construction — the control leaf being farthest makes contrasts
  positive by geometry alone (crisp probe manufacturing crispness, λ measure).
- The fix that works is matched-position: hold token, position and prompt
  length fixed and move only the certified role (difference-in-differences).
- Δ magnitude is a TRANSPORT measurement — how far a perturbation diffuses —
  and is largely indifferent to what is being computed. Do not use it as a
  semantic-dependency readout; the s335 positive control came back with the
  wrong sign twice.

Reusable substrate fact for any grid/cone/patching design on prefill.
Page: explore/latent-reasoning-and-the-prefill-triangle.md §Result.
