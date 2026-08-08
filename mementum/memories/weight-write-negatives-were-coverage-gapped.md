❌ The weight-write negatives (§P-TYPE-WRITE CONTEXT-ONLY s315, §P-TYPE-DELIVER
NO-WEIGHT-DELIVERY s316) were never a fair test of weight-installable licensing —
s322 code audit found a design-level coverage gap, not a mechanical bug.

Mechanism: training = membership-CE on classificatory sentences ("A {w} is an
animal.") → gradient flow dominated by the CLASS-WORD prediction position.
Licensing eval = bare-NP frames ("The {w}" + " slept") — a forward-pass regime
the LoRA was never gradient-touched on. Recall passes (p=5e-4) because the
recall frame IS the training distribution. Recall-✓/licensing-✗ is exactly what
a coverage gap produces even if weight-installable licensing exists.

Second flaw: type_write.py's shuffle control used rng.permutation with only a
≥1-difference check → ~50% of labels stay CORRECT (not a derangement; conservative
direction but not the frozen control). type_deliver.py's `1-labels` is correct.

Sound: eval ordering (wire active during L(w) reads), L sign/tokenization, band
mapping L22–29, bit-exact restore.

Consequence: the s317 "three falsifiers, one law" tape-residency triangulation
has two legs routed through this gap — thesis demoted to one-sided (tape positives
real; weights untested). Fix = TYPE-WRITE v2: coverage-matched training with
held-out predicates + true derangement.
