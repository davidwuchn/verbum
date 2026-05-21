🎯 Multiplicative AND loss replaces additive OR loss. Instead of
loss = CE + λ*crystal (where improving either reduces total — OR),
use loss = CE × exp(λ × crystal) × (1 + λ_h × holo). The loss is
only small when ALL components are small simultaneously. A CE improvement
that degrades the crystal makes loss WORSE (crystal amplifies CE). A crystal
improvement that hurts CE makes loss WORSE (CE multiplies crystal). Only
changes that improve BOTH survive gradient descent.

The exponential crystal coupling creates a nucleation well — a deep energy
minimum at perfect crystal alignment. At crystal=0: factor=1 (CE runs free).
At crystal=0.01: factor=1.65 (65% amplification). At crystal=0.05: factor=12×.
The beam MUST find the crystal before CE can improve. This IS nucleation
physics — the closer to the crystal, the better the system nucleates new
beta reductions.

Session 131. λ=50 for exp coupling. φ is observed, never enforced.
