💡 The last escape hatch is closed: NO nonlinear C survived INLP → the applicative-C
routing field is a READOUT REGISTER linearly AND nonlinearly (Qwen3-14B, s250 cont.2,
program_cfield_nonlinear_probe.py).

s250-cont's caveat: INLP erases only LINEAR decodability; a nonlinear C-encoding could
be load-bearing and missed. Test = decodability gap (a full SAE needs ~1e6 activations,
infeasible at n=135). Linear (logistic) vs nonlinear (MLP, RBF-SVM) C-present probes,
5-fold CV in a StandardScaler pipeline, on RAW and POST-INLP L27/29/30/31 residuals;
shuffle control + PCA-50 view.

RAW: linear 0.978-0.993; nonlinear NO better (RBF 0.948-0.970 < logistic; MLP 0.83-0.91)
→ C is linearly separable, nonlinearity adds nothing. POST-INLP: linear 0.30-0.36
(erased); nonlinear MLP 0.585-0.652, RBF 0.667-0.674 — all at/below shuffle (~0.66) and
majority (0.667); escape threshold 0.767 never crossed. NO nonlinear escape hatch; the
linear INLP erasure was COMPLETE.

⇒ s250 thread FULLY CLOSED: applicative-C field = readout register / correlate, not the
object-application mechanism. decodability ≠ causality proven at rank-1 (s250), rank-16
distributed INLP (s250-cont), AND linear-vs-nonlinear (s250-cont.2). NEXT: hunt the
mechanism in attention OV / value register (s127, s206), not the FFN C-field.
