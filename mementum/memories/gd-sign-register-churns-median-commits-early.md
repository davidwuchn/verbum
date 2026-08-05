❌🔁 §SIGN-COMMITMENT-CURVE (s309 run, s310 read; Qwen3-4B gd_cd wire, results
26ad20b): verdict **SIGN-CHURN** — GD's trit SIGNS do NOT freeze. flip_last
0.0295 > FLIP_CHURN 0.02 (persistent ~3%/snap tail to step 499) even though
S(T⁻)=0.9705 passed. G1=F G2=F G3=T G4=T.

**BUT churn ≠ didn't work (Michael's correction — I over-read the label).**
The wire WORKS: loss 5.031→0.252 (95% drop, 90% by step 8), mag_cos 0.901,
G4 pass, ternarizes retention ~1.0 (s304). SIGN-CHURN is a routing-register
*trajectory* verdict, not task failure. → ALWAYS check loss before reading a
register-trajectory verdict as damage (λ measure / λ observation).

**Decoupling = the finding.** Loss flat by step ~34–89 (410/500 steps move it
2%), yet signs flip 3–5%/snap to the end ⇒ **loss-neutral churn**. Median trit
commits its sign at step 5 (frac 0.010, G3 null-beats p=0.0004); a heavy tail
(p90=144) never settles. Two-population read: churn concentrates in MARGINAL
trits (r=|Δ_T|/thr_j ≈ 1, straddling the per-column TWN threshold; r<1 ⇒ final
0) = the **ternary-0 "insufficient evidence" population**; CONFIDENT trits
(r≫1) commit early and freeze. Smoke preview: 96.5% of late flips at r<1.3.
Full-run confirmation pending (rescore in flight).

Two-timescale ratio 0.38 rejected/inverted but CONFOUNDED (M(0)=0.723 vs
Sc(0)=0.542 — signs start near chance) → NOT MAG-EARLY.

**Lesson for M8/TD-v2:** SIGN-CHURN is a direct measurement of GD's wasted
routing motion (flips signs after loss is solved) ⇒ the routing optimizer needs
a never-freeze ternary-0 band, not a frozen sign field. Prescription, not
refutation. Convergence (s304 retention ~1.0) ≠ trajectory.
