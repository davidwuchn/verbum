🔄 s242: RLVR on Qwen3-8B redirects a PRE-FORMED lambda function — it does NOT
construct one. Pivot to the V15-clean architecture (constructed reducer).

THE CONTROL (results/rlvr-grpo/run1): GRPO ⊗ verifiable kernel reward, SFT-seed merged +
fresh LoRA, temp 1.5, 200 steps. `frac_reward_zero_std`=0.75 the WHOLE run (75% of
groups zero-advantage: easy all-8 + dead all-0). Checkpoint-50 re-measure (129 hard
prompts): density dead-FLAT 0.409 across temps 0.8→1.5; ~54% still all-0. The lever is
weak because the dead tail is QWEN'S representational gap, not the kernel's — a
pretrained model's pre-formed lambda circuit MASKS the research question (can the
compiler be a discrete circuit?).

THE PIVOT (= the s226 cut, now load-bearing): freeze routing into TOPOLOGY (the s240
crystal lattice; routing is INVARIANT → nothing to learn → no gradient through dispatch
→ kills the v12–v15 gradient-death) + replace reduce NEURONS with EXACT KERNEL CALLS
(lambda_ast stage 3 = ternary CCG plates = level-4 artifact). Learn ONLY the thin
prose→LF front-end (CE on 509 gold pairs; Qwen demoted to LF teacher, never the
reducer). First exp: small front-end ∘ exact kernel, certify-rate + param-count vs the
8B-LoRA loop. See knowledge/explore/compiler-as-loss.md §s242.
