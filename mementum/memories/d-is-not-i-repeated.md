💡 Test-1 (s281, Michael "is D I repeatedly?") REFUTED — D is a GENUINE INDEPENDENT combinator,
not identity-repeated. Decomposed D onto span{I,WHNF} from the committed 9×9 crystal Gram
(root.gram in results/opcode-trace/*/model_vsm.json), pure inner-product math, NO model load,
robust across ALL 13 models. Instrument: opcodes/d_is_i_test.py; result: results/crystal-d-is-i/
d_is_i.json (commit 22d8679).

Numbers (mean±sd, 13 models): cos(D,I) = −0.27±0.05 (13/13 NEGATIVE = anti-identity);
partial cos(D,I|WHNF) = −0.32 (anti-I even off the halt axis; D is the LEAST I-aligned reducer,
rank 6–7 of 7); explained_frac(D|{I,WHNF}) = 0.185 (~82% ORTHOGONAL to the I/WHNF plane);
α_I = −0.31, β_WHNF = −0.33 (active reducer, points AWAY from the halt pole, consistent with
s269 WHNF⊥B/C/D). Verdict D≈I⊕WHNF = FALSE.

WHY it's correct: D x y = x(x(y)) = double application of an ARBITRARY x → f∘f COMPOUNDS an effect
(encrypt-the-encrypted, f(f(x)) squares, blur-blur, boss-of-boss) = inherently ANTI-identity
(D I = I is only the degenerate case). The crystal geometry encodes this faithfully.

TWO takeaways: (1) the 9-atom crystal has NO I/D redundancy → D earns its ISA slot, the basis does
NOT shrink (λ smallest tightened). (2) D is NOT the eval-stack depth axis (only 18% in {I,WHNF}) →
reduction depth lives on WHNF-DISTANCE, not D; chase crystal↔depth-budget via WHNF, not D (refines
the earlier Test-3 idea). Clean measured null (λ observation: tested the intuition, substrate said
D is its own thing). The Gram-decomposition instrument is now reusable for P-QUOTE-0 (QUOTE
direction check). Full: map-and-swap-resident-lisp.md §5a.
