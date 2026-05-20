✅ coevolution-works

**Finding**: Evolutionary descent (ternary bit flips) + GD (continuous beams)
+ crystal lattice loss = accuracy AND crystal improve together.

Evo v3 results:
  Baseline:  acc=0.483, crystal=0.368
  Co-evolve: acc=0.577, crystal=0.611 (+0.094 acc, +0.243 crystal)
  Peak R8:   acc=0.564, crystal=0.917 (highest student crystal ever)

**Why it works**: Crystal loss stabilizes the crystal during GD, which ENABLES
the evo phase. Stable crystal → more positions above floor → more useful
flips accepted. Without crystal loss: 20 accepted flips. With: 53 (2.6×).

**Two phases**: R0-R4 crystal stabilizing (floor blocks everything, evo inactive).
R5-R8 crystal stable (evo takes off, 4-29 flips per round, crystal 0.735-0.917).

**The pipeline**:
  GD: CE + crystal_lattice_loss (continuous, keeps crystal stable)
  Evo: delta-guided flips + absolute crystal floor (discrete, only improving flips)
  Co-evolve: alternate GD → evo → reset beams → repeat

**Key insight**: crystal loss doesn't just protect — it ENABLES. Stability is
the precondition for evolution. You can't evolve on an unstable landscape.

Connects to: crystal-gates-hologram, evolutionary-descent-ternary, mirror-flip-barrier
