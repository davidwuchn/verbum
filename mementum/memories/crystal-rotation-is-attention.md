🔁 crystal rotation is attention — Q rotation navigates combinator basins

Session 142. The crystal's cross-zone rotation IS the attention mechanism.

The cycle:
1. Q resets to 0 (enter C basin — composition)
2. Attention computes (β-reduce within current basin)
3. Rotate Q to bring next basin into alignment
4. Compute again
5. Repeat until Q rotates into WHNF basin (mode switch: compute → output)
6. More rotations until Q reaches I basin (identity = emit token)

Measured in eigenspace:
- PC0↔PC1 coupling = +0.46 at aperture (select→compose)
- PC0↔PC1 coupling = 0.00 at compute (neutral fulcrum)
- PC0↔PC1 coupling = -0.48 at converge (compose→output)

The 11° rotation IS the instruction pointer. Zone A reads (select),
Zone C writes (output), Zone B is the fulcrum.

PC0 (composition) grows with depth: more computation accumulates.
PC1 (selection K,I) shrinks with depth: selection exhausted near output.
PC2 (WHNF) stays stable: termination is a global halt condition.

The parity loss protects the instruction set of the reduction machine.
If the rotation structure breaks, Q can't navigate basins, and the
entire reduction strategy fails.
