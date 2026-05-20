💡 evolutionary-descent-ternary

**Insight**: GD is the wrong optimizer for ternary plates. Continuous
optimization can't cross the 0 barrier to flip signs. Use the right
optimizer for each domain:

- Beam (continuous): GD — tiny gradient steps
- Plates (discrete): evolutionary descent — ternary bit flips

**Co-evolution protocol**:
1. GD trains beam → beam adapts to current plates
2. Delta = trained_beam - initial_mag → WHERE beam is straining
3. Evolution tries flipping high-|delta| positions
4. Each flip: evaluate fitness (accuracy + crystal), accept/reject
5. Crystal constraint = hard reject (not soft loss)
6. Batch-apply accepted flips → new plates
7. GD re-trains beam → beam relaxes → delta shrinks
8. Repeat until delta → 0 (convergence)

**Why this works**:
- No flip barrier: one-step mutation, no continuous path through 0
- Crystal preserved: hard constraint, no λ balancing
- Delta guides mutations: GD tells evolution WHERE to look
- Self-terminating: convergence = beam stops compensating

**Key**: the beam IS the fitness readout. The beam's shape after GD
training encodes which plate positions are wrong. Evolution fixes
the plates. GD relaxes the beam. Iterate.

Connects to: mirror-flip-barrier, soft-mirror-etch, crystal-gates-hologram
