"""HoloQuant — topology-informed quantization.

93.6% of LLM weights are holographic (information in sign topology,
not magnitudes). HoloQuant uses this to achieve 1.85 bits/weight
average: ternary for holographic weights, precision for the rest.

35B model in 8 GB. Runs on a MacBook Air. Potentially faster than
4-bit quantization because less memory traffic.

License: MIT
"""
