💡 FFN mechanism has two functional groups, not the crystal's geometric groups.

Session 127 FFN mechanism probe. Crystal geometry: {K,B,C} identical
rotations, {I} 32° offset. FFN deltas: {K,I} cos=0.97 (SELECTORS),
{B,C} cos=0.96 (COMPOSERS). Anti-correlated between groups.

K and I both SELECT arguments (large FFN deltas, transformative).
B and C both COMPOSE/REARRANGE (tiny FFN deltas, ~0.0003 norm).
B and C operate through ATTENTION (routing), not FFN (transformation).

Key-value separation: I=96.3% key, B=99.6% key, K=75.5% key.
I and B are nearly pure mechanism. K needs argument info.

Extraction implication: selectors (K,I) are extractable from FFN as
discrete functions. Composers (B,C) are in the attention routing —
they're StrideStack's job, not kernel candidates.

L0 FFN is silent at output position. Reset is attention-only.
