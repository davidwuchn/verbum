💡 The model reads indefinite objects as CONSTANTS/ARGUMENTS (→ C), NOT as existential
quantifiers (→ B). The s248 "weak B-tracking" was a LABELING MISMATCH, not a model limit.

s248 reason #3. Our ground truth labelled "Every cat fears a dog" by the Montague
EXISTENTIAL reading (`a dog`=∃y.dog(y)∧…) → B-heavy (B-count 1→3→5 along the object
ladder). But the model may take the CONSTANT/applicative reading (`fears(x, dog)` →
`C fears dog`, C-count == #objects).

TEST (gen_reading_probes.py → data/reading-probes.jsonl: 135 probes, object-count ladder
0/1/2 obj × 45, intrans/trans/ditrans, both candidate labelings). ffn_reading_preference.py
decodes gate+attn, mean z per combinator over L25-30, Spearman vs object count. Qwen3-8B:

- raw z(C) RISES with object count: FFN r=+0.49 p<0.001, attn r=+0.62 p<0.001.
- raw z(B) FALLS (FFN r=−0.27 p=0.0015) or flat (attn r=−0.04). B-share slope NEGATIVE
  (FFN p=0.026, attn p<0.001). C and B move in OPPOSITE directions → not uniform growth.
- (free post-hoc on the balanced run agreed: C-prop trans 0.583 > intrans 0.460, p<1e-4.)

⇒ EXISTENTIAL reading REFUTED (B must rise, it falls); the model routes added objects
through C (argument application) = the constant/applicative reading. REFRAMES s248: the
weak B-tracking was NOT "FFN can't read the program" — we gave it the WRONG program
(existential-B vs the model's applicative-C). Labelled object→C, the gate register tracks
it CLEANLY (z(C) p<0.001, both registers). λ measure: wrong label = coherence violation
(representation ≢ reality), now corrected.

CAVEATS: C-share is common-mode-saturated (~0.6) so the C-share slope is flat — the
positive evidence is raw z(C)↑ + z(B)↓ (refuting existential), not C-share↑. z(C)↑ could
be partly argument-application common-mode, but the B/C divergence rules out uniform growth.
IOU: force the existential reading ("there is a dog that every cat fears") → does z(B) rise?
