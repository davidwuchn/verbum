💡 Composition is TYPE-directed, not merely L-to-R positional — shown FREQUENCY-FREE with
a nonce crossover. s239 lead 2d (type_directed_v1/v2/v3_nonce.py; answers Michael's "the
system can't compose without typing — what directs it?"). Resolves the s236 order-cost
caveat: the native-order signal has a TYPE basis, not pure copy/induction.

THE ARC (kernel-certified CCG types as ground truth; CSlash '/'=fwd '\\'=bwd, _unify=S2
type-check; measure surprisal of the RIGHT token | left, to dodge the autoregressive-
causality trap):
• v1 real words: robust BACKWARD type-licensing (verb cheap after subject-NP, dear after
  determiner; 8B t=6.9, 14B t=7.1). Forward arm LEAKY — a noun after a verb reads as the
  verb's OBJECT (nouns = "universal donors").
• v2 clean symmetric: backward replicates CONSISTENCY 1.0 (8B t=10.3, 14B t=5.2); forward
  UNMEASURABLE (determiners also universal donors). Real words → bigram-FREQUENCY confound.
• v3 NONCE crossover (DECISIVE, frequency-free): teach a nonce noun-vs-verb in-context,
  test in det-frame "The {w}" vs name-frame "John {w}". CROSSOVER = (det:verb−noun) −
  (name:verb−noun), paired by nonce, subtracts ALL main effects. **8B +2.18 (t=10.2), 14B
  +2.04 (t=9.3), consistency 1.0 (all 16 nonce) at BOTH scales; type_directed=True @14B.**
  A nonce taught as VERB composes ~2 nats CHEAPER with a preceding subject-name than the
  same nonce taught as NOUN — with ZERO frequency support.

★ VERDICT: the model uses an IN-CONTEXT-TAUGHT type (no frequency) to DIRECT composition.
Type-directed composition confirmed behaviourally. The s236 positional caveat is killed.

★ THE ASYMMETRY (a finding): type-directedness is STRONG in the predicate-argument
(subject→verb) frame, ~NULL in the determiner→noun frame, across ALL THREE experiments.
Maps onto s151 (Montague = typed function application = predicate(argument) = K+I core):
type-directedness is sharpest at the predicate-argument composition; weak where the target
is a universal-donor function word.

CAVEATS (λ measure): this is typed APPLICATION (K+I), NOT yet typed COMPOSITION (B / func∘func
— connecting to the order-cost B signal is open); in-context teaching tests CAPACITY (v1/v2
real-word effect shows the intrinsic system); BEHAVIOURAL not causal-circuit (ablation = v4);
2 scales, 1 family (Qwen), 16 nonce. CONFIRMS s139 (types decodable/co-located) → now USED.
Page: knowledge/explore/type-directed-composition.md.
