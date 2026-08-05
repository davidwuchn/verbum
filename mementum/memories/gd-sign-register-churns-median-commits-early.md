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
(p90=144) never settles. **Two-population split CONFIRMED at step 499** (s310
rescore, 1.44M trits binned by r=|Δ_T|/thr_j): the two lowest-r bands own
**0.781** of all late flips (r<1 0.536 + marginal r≈1 0.245); the marginal band
has the highest per-trit late flip-rate (0.099). CONFIDENT core r≥2 is FROZEN
(flip_last 0.0003 / 0.0000). = the **ternary-0 "insufficient evidence"
population** jitters forever; trits with margin commit at step 0 and never move.
Loss-neutrality confirmed: plateau moves loss 0.11% while flip-rate stays 0.045.

Two-timescale ratio 0.38 rejected/inverted but CONFOUNDED (M(0)=0.723 vs
Sc(0)=0.542 — signs start near chance) → NOT MAG-EARLY.

**Lesson for M8/TD-v2:** SIGN-CHURN is a direct measurement of GD's wasted
routing motion (flips signs after loss is solved) ⇒ the routing optimizer needs
a never-freeze ternary-0 band, not a frozen sign field. Prescription, not
refutation. Convergence (s304 retention ~1.0) ≠ trajectory.
