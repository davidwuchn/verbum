💡 The flat B<C native-order result is FRAME-ROBUST at scale (14B/32B strengthen) but
FRAGILE at the 8B floor — and the s237 nested SIGN-FLIP was a pure NESTING-DEPTH confound.
s239 v5 lead 2d path 1 (kernel_reference_order_cost_v10_frame.py,
`--render-frame {applied_to, result_of}`). Tested a 2nd render frame for App(f,x): the
CIRCUMFIX "the result of <f> on <x>" vs v9's INFIX "<f> applied to <x>". Flat result_of =
one "the result of" prefix + leaves chained by " on " → B "the result of f on a on b" vs C
"...f on b on a" = pure atom-order, NEW lexicon+syntax. (applied_to+flat reproduces v9
byte-for-byte: 8B smoke t=−0.567 ≡ v9.)

★ FRAME-ROBUST WHERE STRONG, FRAGILE AT FLOOR (B-vs-C atom minpair, n=24):
  Qwen 14B  applied_to −8.05 → result_of −9.24 ✓ (stronger)
  Qwen 32B  applied_to −4.48 → result_of −11.7 ✓ (stronger)
  Qwen 8B   applied_to −2.87 → result_of +0.70 ✗ (frame-FRAGILE — floor signal dies)
⇒ frame-robustness is itself SCALE-GATED: the order preference is a property of COMPOSITION
(not the "applied to" infix) where strong, but the weakest 8B read is frame-sensitive.

★ NESTED-FLIP = DEPTH CONFOUND (clarifies s237): result_of NESTED 14B B<C atom t=−15.45 ✓
(EQUAL depth — B and C each have ONE nest; full surface t=+0.28 n.s. but atoms decisive) vs
s237 applied_to nested +11.9 ✗ (UNEQUAL depth: B nested, C flat). Equalize nest-depth → B<C
survives nesting. The s237 sign-flip was DEPTH, not order.

★ OFF-QWEN SINGLE-STEP SHARPENING is frame×model-dependent: Gemma-31B-it applied_to −0.56
n.s. → result_of −9.35 ✓ (natural-English circumfix UNLOCKS the sharp single-step for the
instruct model; caveat OOD huge surprisals, B atoms 9.3). OLMo-13B −1.25 → +0.73, both n.s.
(no sharpen). GROSS composition (composite B-vs-C-multi, B-vs-S) holds across ALL models +
BOTH frames.

CAVEATS (λ measure): result_of flat = clean order test; nested conflates order with
nest-POSITION (equal-depth, cleaner than s237). 8B = frame-fragile floor. Gemma instruct OOD.
Single-combinator labels; within-program paired contrasts.
