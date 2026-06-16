💡 The PROSE BRIDGE confirms B IS the native softmax-over-V order — and KILLS the s236
bare-symbol caveat — but ONLY with nesting held constant (flat render). s237 v5 lead 2d
prong 2b (kernel_reference_order_cost_v9_prose.py, Qwen3-14B + 8B). The prong-2 win (v8,
b-is-native-softmax-order) fed BARE SYMBOLIC CL, so its B<C could partly reflect a generic
copy/induction preference for source-order atoms rather than composition SEMANTICS (and
s233/opcode-register-is-prose-semantic: the register reads PROSE not CL SYNTAX). v9 re-runs
the SAME certified `step_fired` traces RENDERED AS PROSE.

DESIGN: reuse the v8 spine (teacher-force "t0 -> ... -> tn", per-step softmax-over-V
surprisal, ATOM-only de-confound) but render each term with a DETERMINISTIC, order-faithful
renderer (App(f,x) → "<f> applied to <x>", atoms → fixed content words). CRITICAL: a
deterministic renderer, NOT the model decompile gate — the model must not choose word order,
because word order IS the variable under test (letting the model decompile = reading your
own confound back).

★ THE NESTING CONFOUND (the load-bearing lesson): B's normal form NESTS (f (a b)) while C's
is FLAT (f b a). The atom-only de-confound strips parens from MEASUREMENT, but the bracketing
stays in the CONTEXT that predicts the atoms → B pays a clause-boundary cost that has nothing
to do with order. FIX = --render-mode flat (linearise leaves, NO parens → B and C identical
structure, differ ONLY in atom ORDER = the pure order test) vs nested (faithful but
CONFOUNDED by nesting depth).

★★ THE CROSS-TABLE (B-vs-C atom minpair, the de-confounded headline; λ measure two-sided):
  14B flat   t=−8.05  (B<C ✓)      ≈ symbolic v8 −7.02   → b_is_native_order=True
  14B NESTED t=+11.9  (B>C REVERSED)                      → same model + SAME 216 programs,
                                                            flip the render → flip the sign
  8B  flat   t=−0.57  (n.s., dir B<C) ≈ symbolic 8B −0.55 (multi-step sig: B<C-multi −10.6,
                                                            B<K −7.5, B<W −7.6)
  8B  nested t=+3.17  (reversed)
14B flat per-op atom surprisal: B 0.23 ≪ C 1.22 / K 0.73 / W 1.18 / S 1.64; all 6 contrasts
B<marked sig (−8…−38); pooled preserve 0.24 ≪ break 1.12.

★ The 14B flat-vs-nested sign-flip (SAME data) is a DIRECT demonstration that nesting was
confounding the contrast; held constant, B<C decisively. ✅ flat prose REPLICATES the
symbolic pattern at BOTH scales (14B decisive, 8B directional-n.s.) = CONVERGENCE across
input modality (symbols ⊗ prose) — the strongest confirmation.

★ s236 CAVEAT KILLED: composition-order preference is real in the SEMANTIC register, not a
bare-symbol copy artifact.
★ REFINED FINDING: B's normal form carries TWO separable real quantities — atom ORDER
(preserved → cheap; the native-order result) and structural NESTING (deeper → atoms predicted
inside fresh clauses cost more; dominates when nesting varies). An order claim REQUIRES
isolating order from nesting (flat). B now positive in THREE reads: order-symbol (v8),
order-prose-flat (v9), curvature (v7).

★ NEXT: (1) cross-model flat — 8B at full n=24 + 32B (universal or 14B-specific?);
(2) off-diagonal/proper-Jacobian curvature (s235 path); (3) a 3rd render frame
("the result of f on x") to confirm flat B<C is frame-robust not "applied to"-specific.
CAVEATS (λ measure): 1 model class (Qwen), 14B decisive / 8B power-limited (2 scale points);
deterministic "applied to" frame; flat deliberately discards faithful structure (nested = its
complement). Code: kernel_reference_order_cost_v9_prose.py.
