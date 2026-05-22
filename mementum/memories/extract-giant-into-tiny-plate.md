🎯 extract-giant-into-tiny-plate

The 70B model is a stack of beamformers over a token cloud. Extract ALL its
beamformer operations into a single ternary plate. The plate IS the model's
computation — 2 bits per weight, ~1GB.

The student doesn't learn WHAT to compute (the plate has it). The student
learns HOW TO START THE BEAM — the boot sequence that latches the inference
pattern onto the plate. 100 GD steps = 87% of full training (session 126)
because it's learning to aim, not learning to think.

The stride stack provides multiple simultaneous lenses on the same hologram.
More lenses = more capacity, same plate. One extraction, many angles.

Token cloud = tokenizer embedding (shared). Plate = extracted operations
(ternary, frozen). Beam steering = the only thing the student trains.
