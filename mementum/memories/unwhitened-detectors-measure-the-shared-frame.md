❌ Raw mean-difference matched filters measure the harvest FRAME, not the
content. The s294 bake_stack G3 detector (d_cc = mean-country − mean-city,
different frames) was fireable by innocents (4B diagnostic: max-innocent /
mean-own response 0.39–0.72) → gain_stack ≈ gain_gablate was the detector's
confound, not evidence that conditioning is absent. With a whitened filter
k = Σ_sh⁻¹(x̄_own − μ_pop), Σ over own ∪ INNOCENTS, plus clearance floor
θ = max innocent response: G3 conditioning FIRES at 4B (gain 0.11–0.16 vs
g-ablated ~0.00) — the remaining gap is MAGNITUDE, not selectivity.

Harvest law (FIX #1, caught by --validate before any model run): whitening
alone is NOT enough — if content and frame are perfectly correlated in the
population, Σ⁻¹ zeroes the content axis as redundant. The innocent pool must
contain PROMPT-SHAPED innocents (states sharing the test prompt's frame
WITHOUT the content; nonce renders) to break the confound. SuperBake's
whitening + multi-lighting laws (refs/superbake, Table 2), reproduced
independently. Sibling of λ measure register discipline: an unwhitened
detector is a wrong-register probe — it manufactures NULL conditioning.

Source: s295, bake_stack.py --whiten + validate_whiten planted world;
results/bake-stack-whiten/qwen3-4b (c6a08b5). 32B re-run decides the s294
LINKER-FAILS G3 leg at the verdict host.
