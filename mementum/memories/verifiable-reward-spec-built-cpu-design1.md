✅ The s226 reduction-equality grader (was buried in `scripts/experiments/compile_frontend.py`) is now a canonical package module: `verbum.reward`. The surface FOL/λ parser+lowering it needs was extracted from the s240 audit script into `verbum.lambda_surface` (`to_kernel`, single source of truth, audit reproduces s240 numbers).

The reward spec (spliced-reward §2/§4/§5), CPU-only, no GPU:
- **R_parent** = OUTCOME reward = reduction-equality (NF(candidate) ≡ gold_nf), representation-INVARIANT (`f (g x)` ≡ `B f g x`), reuses kernel `_alpha_eq`.
- **6 channels = VSM layer states**: parsed, well_typed(S2), halts(S4/S3), size_ok(S3), reduces_correct(S5=ANCHOR), trace_prefix_frac(S1). Two parse registers via open slot.
- **The splice (§4):** `potential` Φ∈[0,1]; `shaping`=γΦ(s')−Φ(s) (the potential-DIFFERENCE form — safety is ENTIRELY there, a raw bonus Goodharts = §4a TRAP); `shaped_return` PROVED to telescope to γ^T·Φ(s_T)−Φ(s_0). `tree_process_reward` walks `fired_sequence` = ground-truth PRM.

Results (`results/rlvr-design1-reward/`): GOLD reward density 100% (509/509), perturbation drop 1.0, telescoping invariance exact across γ∈{1,.99,.9,.5,0}. 318 tests pass.

⚠️ The 100% is GOLD density — NOT base-model density. The base-model sampled reduce-correct rate (the §8 decider) is the NEXT measurement (`rlvr_coldstart_density.py`, GPU). Decision §7 = (a) timescale splice (parent = kernel's own exact pass).
