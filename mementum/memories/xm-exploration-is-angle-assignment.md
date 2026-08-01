💡 xm-exploration-is-angle-assignment

Explorative Modeling (arXiv:2607.27372, read in full s296) maps onto the
holographic thesis without strain:

- **Coupling ≡ angle assignment.** XM's coupling problem (which latent →
  which datapoint) is the write-angle assignment problem of multiplexed
  holographic storage. Mode blur ≡ cross-talk: a linear medium (s292:
  plate records linearly, interference is in the light) cannot separate
  two objects written at the same angle. Forward XM = co-adapting angle
  assignment — etch each object where it already constructively
  interferes. Minibatch-OT's failure (geometric, model-agnostic
  assignment hurts FID) supports: the medium decides where the object fits.
- **Our etch is the M=1 regressor** the paper attacks. Holographic
  distillation (s115) minimizes ||teacher−student||² → per-prediction
  expressivity 1. Candidate explanation for the 50-beats-800-probes
  anomaly: more targets per plate slot → conflicting pulls → blur.
  Prediction: exploration (best-of-K etch) closes the gap.
- **Teacher ≡ reference beam** = heterodyne scoring: candidate distance
  measured in teacher representation space, where modes are separated —
  satisfies Prop-3's separation precondition, which fails in raw token space.
- **Tape ↔ exploration substitutability** (their Fig 11): more
  exploration at etch time → less tape (CoT) needed at inference.
  Re-frames s294's backprop-compile conclusion as a loss-loop change.

Caution: the structural claim (cleaner mode-keyed latent cells) is ours,
routing-register, unmeasured by the paper. Mode Forcing theory is
self-citing (draft, same author) — treat as hypothesis under test here.

Connects to: interference-is-in-the-beam-not-the-plate,
holographic-distillation-works, diffusion-holographic-isomorphism,
burn-in-is-variety-not-repetition
