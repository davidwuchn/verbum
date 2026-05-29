💡 Universal lattice is relational (overlay matrices), not coordinate (weight signs)

Session 167. Cross-model probe on 4 Qwen3 models (0.6B, 4B, 8B, 14B).
PC allocation cosine = 0.99+ across all depths — the RELATIONAL structure
(how many neurons per combinator) is universal. But sign agreement in
weight-coordinate space is only 12.5% — individual weight positions
don't match across models.

The mapping from combinator space (16-dim) to d_model space (1024-5120)
is model-specific. Tiling crystal eigenvectors across d_model doesn't
capture the correct projection. Each model learns its own coordinate
embedding for the universal combinator structure.

Consensus must happen in combinator space, not weight space:
- ISA decoder overlay matrices (combinator-to-combinator transforms)
- Cross-PC coupling patterns at relative depths
- NOT raw gate_proj weight signs

This confirms the earlier finding: "FFN map is universal at RELATIONAL
level, model-specific at NEURON level." Same query results, different
page numbers. The lattice is the query structure, not the page layout.
