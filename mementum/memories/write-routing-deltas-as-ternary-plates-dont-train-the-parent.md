💡 Michael (s303): "why train the parent at all? write routing deltas into
ternary storage, apply to a frozen base." Reframe: we ALREADY freeze the parent
— gd_cd is LoRA (base frozen, only rank-16 B·A moved). So the real questions are
STORAGE and FINDING, not train-vs-not.

- STORAGE (high confidence): wire=routing (s303); ternary={−1,0,+1}=routing
  register; s269 routing survives ternary at 0.987 while magnitude cosine falls
  to 0.73 → a routing delta ternarizes losslessly-for-routing. + delta-log
  (s299/s300) = git-for-weights (undo=−Δ, sha256, compose). Portable artifact =
  wire as one small ternary plate.
- FINDING (open): construct FAILED — but in the MAGNITUDE register (hand-guessed
  product-key gain), NOT proof gradient is required. Untested = a ROUTING-register
  construct: HRR/sign-vote ternary bind-plate Δ=Σ key⊛value from measured key
  geometry, frozen base, no gradient.
- CAVEAT: ternary plates are LINEAR storage; the pin is nonlinear (s300 ∄ clean
  linear linker). Plate carries the linear routing EDGE; frozen base supplies the
  collapse. gd_cd (linear LoRA on frozen base) already proves edge-on-frozen-
  nonlinearity works.
- This IS map-and-swap resident Lisp: frozen base = universal reducer (9×9
  crystal eval/apply); ternary plate = swapped-in program.

Full page + 2 pre-scoped experiments: knowledge/explore/
write-not-train-ternary-routing-deltas.md. s304 pickup: run EXP-1
(ternarize-the-delta, storage, cheap) FIRST.
