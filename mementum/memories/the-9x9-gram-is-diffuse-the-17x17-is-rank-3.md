💡 The 9×9 crystal gram and the 17×17 un-flattened gram live in different
registers. Spectral+DSP battery (opcodes/spectral_dsp.py, verbum.dsp, 11
models, commit 072c3e0):

- **9×9 is spectrally diffuse** — near-full-rank (PR≈5.8–7.2 of 9), eigenvalues
  ≈1. G1 (PR < matched_range null) FAILS. Its universality is RELATIONAL
  (off-diagonal sign pattern, C2), NOT spectral. Don't chase spectral
  concentration in the 9×9.
- **17×17 is rank-3** — PR≈2.6–3.2 of 17, G1 p=5e-4 all 11 models; huge
  eigengap (Qwen3-32B 8.52,4.47,0.93,→cliff). The three poles fire/halt/diverge.
  Adding 8 near-collinear halt nodes DROPPED effective rank because it exposed
  the outcome geometry the collapsed WHNF node hid (s284 G4 dissociation, now
  spectral). Partition real 11/11 (G2), carried by top-3 eigenspace 11/11 (G3).
- **9×9 = opcode IDENTITY (orthogonal, high rank); 17×17 = reduction OUTCOME
  (3 poles, low rank).** Different views.
- φ-trap (G5) replicates s247/s251: 8/11 fail; 3 passers all Pythia; s251's
  Qwen3-14B is off here — unstable passing set = forced fit, not discovery.

**Thesis (Michael): topology routing, not magnitudes.** Every magnitude-as-signal
probe fails the yardstick (G1 9×9, G4 eigenvalue profile, G5 φ); every
topology-as-signal probe passes 11/11 (C2 off-diagonal pattern, G2 membership,
G3 poles=top eigenspace). The crystal is a routing graph recorded in a magnitude
medium — the topology is the invariant, magnitudes are model-particular
scaffolding (same as s269: relational fidelity 0.987 survives 1-bit, weight
cosine falls to 0.73).
