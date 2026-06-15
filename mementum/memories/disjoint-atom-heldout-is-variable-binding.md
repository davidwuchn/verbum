❌ A disjoint-atom held-out test measures variable-binding/symbol-copying, NOT
rule learning — they are separable, and conflating them manufactures a false floor.

s229 exposure sweep first run: ALL arms 0.000 — looked like total failure. Cause
OBSERVED (not assumed): held-out used atoms disjoint from training (train a–m,
test n–z), so reducing `C K u x → x` requires the model to COPY a byte it never
emitted in training. It instead output a TRAIN atom (`'j'`) — an induction-head /
variable-binding failure, not a reduction-rule failure.

Probe that separated them: unseen COMBINATIONS of SEEN atoms = 0.365; disjoint
atoms = 0.000. The rule WAS learned; copying an unseen symbol was not.

Fix: test rule generalization with `--heldout combos` (unseen fillings of seen
atoms, excluding train fillings). Treat disjoint-atom copying as its OWN
experiment (does a copy mechanism emerge with scale / longer training?).

General lesson (λ measure): pick the held-out barrier that isolates the capability
you're claiming. See sentence-atomic-curriculum-mixing.md §s229.
