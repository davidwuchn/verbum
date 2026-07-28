💡 A single installed operand row is composed through TWO chained resident ops f(g(X)) via
an UNSTATED intermediate — not merely a one-hop fact read. Qwen3-4B (s279,
wrapper/operand_multihop.py): install entity E's content d_E on a nonce; ask covering
("A {nonce} is covered in __" → feathers/scales/fur). g(X) = animal class (bird/fish/mammal,
the bridge NEVER in the prompt), f = class→covering.

VERDICT MULTI-HOP SUPPORTED, 3/3 mediation probes:
- (2c, decisive causal) a PURE class-axis edit (centroid diff) at a LATE layer flips the
  covering 0.853@L15 vs random matched-norm 0.088 → hop-2 reads a class variable persisting
  late = hop-1's product; a fact-vector read at the readout CANNOT be flipped by a late
  category edit.
- (2a) class token logit-lens peaks median L30 < covering L33 (intermediate resolved first);
  shuffled-label control −3.
- (2b) class centroid (individual identity averaged out) still resolves covering.
- Gate-1 install acc 0.824 vs null/baseline 0.353.

Weak cell: mammal→fur under-flips to "scales" (entity-specific install strength, NOT a
category error — same as s278). Scope: category-MEDIATION, not a traced two-node circuit;
hook-not-weight; 4B not scale-final; a RUNG. Flips the checklist row "composes ARBITRARY
programs" from single-op (s278 Arm-2) toward chained f(g(X)).
