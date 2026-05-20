💡 soft-mirror-etch

**Insight**: Instead of discrete sign flips (blunt, breaks crystal), teach GD
to correct signs through continuous soft mirrors that get quantized to ternary.

A soft mirror is (d_out, d_in) initialized to 1.0 (pass-through). GD learns:
  +1 = sign correct, -1 = sign wrong (flip), 0 = noise (block).
Constrained by crystal lattice loss to preserve relational geometry.

Three-phase pipeline:
  1. Blunt flip (hot anneal) — delta sign-flip, 3-5 rounds, fixes worst 60%
  2. Soft mirror (surgical GD) — CE + crystal loss, learns remaining corrections
  3. Quantize + freeze — mirror → ternary, fold into plate, train beams only

The 7 subcrystals are NOT 7 separate extractions — they're 7 mirrors on ONE plate.
Each combinator gets its own mirror (the V13 combinator mask). Subcrystal structure
EMERGES from GD-learned mirrors, not from per-family extraction.

Connects to: crystal-gates-hologram, etcher-vsm, v13-design, oracle-crystal-hurts
