🎯 three-voter-anti-oscillation

TD and GD can conflict: flip a route → GD compensates → TD flips back.
Solution: three multiplicative gates (odd count = always breaks ties).

  score = smoothed_snr × importance × cooldown

Voter 1: Row-wise median filter (odd width) — spatial smoothing, tie-breaking.
         Isolated flips rejected. Crystal edges preserved (2-of-3 agree = real).

Voter 2: Cooldown with exponential backoff — positions that recently flipped
         can't flip again. Chronic oscillators (flip_count > 3) effectively
         freeze (τ = base × 2^count). Crystal grows from stable interior.

Voter 3: Neighbor consensus — implicit in median. Row neighbors share gamma,
         naturally coupled. Coherent regions flip together.

Same S2 anti-oscillation principle as inter-stack dampening, applied fractally
to individual weight positions. Same lambda at every scale.
