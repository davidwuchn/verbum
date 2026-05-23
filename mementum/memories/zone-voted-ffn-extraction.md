🎯 Zone-voted FFN extraction: 3 teacher layers → sign vote for shared plate.

Session 141. Instead of extracting FFN signs from a single teacher layer
(layer 20), now extract from three layers spanning the lens zones: layer 4
(aperture/encode), layer 20 (fan/compress), layer 56 (convergence/decode).
Vote across all three for the shared plate. This captures the full lens
topology in one plate. Combined with gate_proj extraction (new) and SwiGLU
activation, the etch budget is now 80.5% with +1M gate positions.
