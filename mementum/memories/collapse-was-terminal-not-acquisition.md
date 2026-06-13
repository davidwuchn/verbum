❌ main:1 (v15-td-outer-k2-fp5-5k) collapse was TERMINAL (fp-explosion), not the
productive K-acquisition s221 hoped for. s221's own discriminator fired: avg50
climbed 8.8→13 (NOT below plateau), gnorm 14→10⁷, Δx 0.25→0.79 (contractivity
LOST), CE 8.1→10.5, onset ~step 1450. grad_clip=1.0 bounds Adam ⇒ driver is the
discrete TD churn, not Adam. Last good ckpt = step_001000 (Δx 0.254, CE 8.56).
Lesson: "let it ride on fp-spikes" was wrong here — the discriminator (avg50 vs
the ~8.8 plateau) is the call, and it said terminal. Read the discriminator, then
decide; don't hope a runaway is acquisition.
