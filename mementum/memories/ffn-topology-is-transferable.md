🎯 FFN gate topology is transferable from teacher — computable, not discovered

Session 167. FFN programs are fixed points of beta reduction (deterministic,
universal, 0.0 drift across runs). The teacher already found them through
300B+ tokens. We read and transfer, not re-derive.

Three levels of transfer:
1. **Trunk**: gate[n,d] = sign(crystal_eigenvector_pc[d]). Pure math.
   Neuron allocation per PC ∝ eigenvalue (r=0.9932). No training needed.
2. **Branches**: ISA decoder reads teacher's overlay matrices at each layer.
   Cross-PC couplings (K→B, K→I, I→K etc.) define branch neuron signs.
   Project onto student's crystal eigenbasis at corresponding relative depth.
3. **Leaves**: GD fills magnitudes (gamma, up_proj, down_proj content).

This means FFN gates can be FULLY ETCHED at initialization, before any
training. The entire routing table is computable from the crystal
eigendecomposition + teacher's overlay matrices. Training only calibrates
magnitudes around the correct topology.

Attention is different — no closed form for M-space topology. Attention
must be discovered through interference. FFN is transferred. Two
mechanisms because the math is different, not by choice.
