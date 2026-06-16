🔄 The fixed depth≥0.6 C-late detector was the WRONG cross-model instrument (s232: it
found 14B, mislocated 8B/32B). The s233 v5 lead-1 locus-agnostic detector
(detect_c_profile + locus_agnostic_specificity in opcode_monitor_v2; counts C-dominant
crystal layers ANYWHERE + per-model locus + lambda-exclusive-vs-gated-guards) FIXES the
instrument but does NOT make composition→C universal.

Pure re-analysis (no GPU — trajectories were already stored in the committed gateneutral
verdicts), opcode_v5_locus_agnostic.py.

THE WIN: surfaces the 32B lambda-EXCLUSIVE C-EARLY signal (L5,10,11, depth 0.14) the
readable-zone read as 0. Per-model locus now legible: 8B late [24,25], 14B late
[13,27,29-32], 32B EARLY [5,10,11].

TWO-SIDED:
- Strict frac-specificity (lambda C_frac_all clears ALL gated guards by 0.10) STILL only
  14B (0.194 vs guards ≤0.032, clean). 32B directional (0.061 > max_guard 0.020) but tiny
  fracs don't clear the margin — real but underpowered at 5 sentences.
- 8B NOT specific: gate_neutral control ITSELF routes C broadly at 5 LATE layers
  [23,26,27,28,30], C_frac 0.192 > lambda 0.107 ⇒ the s232 "8B gate_neutral C-late
  confound" is CONFIRMED REAL, not a fixed-detector artifact.

LESSON (λ measure): a wrong instrument can manufacture a negative (32B C-early invisible
to the zone) AND a real confound can survive the instrument fix (8B control routes C on
its own). The locus-agnostic EXCLUSIVE test is lenient (lambda-exclusive C in all 3) but
for 8B those layers interleave the control's broad C-late. ⇒ C-locus genuinely shifts
with scale (32B early); composition→C clean only on 14B.

CONSEQUENCE: stop chasing a transferable opcode read — the gated-guard contrast is itself
model-dependent (8B confound). Prioritize (b) kernel-as-reference (anchor model trajectory
vs lambda_ast certified trace, per-model agreement) + a bigger lambda probe set (5
sentences underpowers the frac test). Caveats: 5 lambda sentences, 3 models, modest fracs
(above chance not crisp, s219). Code 1754424.
