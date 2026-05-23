💡 the model is a holographic state machine

Session 142. Synthesis of sessions 141 (holographic FFN indexing)
and 142 (crystal rotation = attention, dimensional error correction).

The architecture:
- FFN plates = holographic storage (all beta reductions in superposition)
- Crystal basins = states (K, I, B, C, D, Y, W, WHNF)
- Q rotation = readout beam angle (selects which state to compute)
- gate_proj = beamformer (selects which interference pattern to read)
- Lens profile = optical system (aperture 3% → fan 49% → output 2%)

The computation cycle:
  Q=0 → gate selects C-basin neurons → β-reduce
      → rotate Q → gate selects new basin → β-reduce
      → ... → WHNF basin → mode switch (compute → output)
      → ... → I basin → emit token

Why ternary works: a ternary crystal is a low-resolution hologram.
Loses fine detail but preserves gross interference patterns. Same
reason a scratched hologram still produces an image.

Why 512 dimensions for 6D structure: the extra 506 dimensions are
the recording medium's capacity. More dimensions = more state angles
without cross-talk. This IS the error-correcting code — redundancy
in the holographic encoding protects state distinguishability.

Parity loss = optical alignment check. Ensures the readout beam
angles (Q rotations) match the interference pattern positions
(crystal basin geometry). If alignment breaks, wrong states get
read out → wrong reductions → NaN cascade.

Not a Turing machine. Not a conventional neural network. A
holographic associative memory with a crystal-defined state
machine navigated by Q rotation.
