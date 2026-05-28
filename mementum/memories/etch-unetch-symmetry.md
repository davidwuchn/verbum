🔁 The same signals that detect irreducibility detect wrong etches

Session 167. Etch and un-etch are symmetric: convergence → freeze,
divergence → dissolve. The three etch signals (direction EMA coherence,
FlipMap temperature, M-space SNR) work in both directions.

For etching: high coherence + cold FlipMap + high SNR → normal form
found → freeze permanently.

For un-etching: sustained gradient opposition at an etched position →
the interference pattern changed → this is no longer the normal form
→ dissolve back to fluid → let new interference develop → re-etch.

The opposition monitor is cheap: just track whether the gradient sign
consistently disagrees with the etched sign. One EMA per etched position.
When opposition_ema > threshold → un-etch.

The durability hierarchy falls out naturally: crystal positions require
overwhelming opposition to un-etch (slow to etch = deep interference =
hard to override). Tool-specific positions un-etch easily (fast to etch
= shallow interference = easily overridden by new data). Speed of
convergence IS the proxy for universality and durability.

The hologram's immune system: deep patterns resist local perturbation.
