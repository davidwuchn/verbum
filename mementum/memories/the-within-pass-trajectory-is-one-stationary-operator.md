✅ The within-pass residual trajectory is (to first order) ONE stationary contracting linear operator unrolled across depth (s338, §P-DMD-TRANSPORT, Qwen3-14B, n=300, STATIONARY-REDUCER, a-priori 20 beat modal BANDED 30). First operator-register contact for the one-reducer-unrolled thesis — a positive.

Method: exact reduced DMD (T≈X'X⁺) on the last-token d_model residual trajectory h(0)→…→h(40), PCA to a common P=128 frame so per-layer operators are comparable. src/verbum/operator_dmd.py (patent-clean textbook DMD, Gram method-of-snapshots) + scripts/experiments/dmd_transport.py.

THE LOAD-BEARING RESULT IS G2 (shuffled-layer null): shuffled-layer residual 0.974 vs real 0.476 (gap +0.498, p=0). Layer ORDER carries almost all the structure — that IS "one reducer unrolled" made mechanical. G3 stationarity core 0.717 / late 0.704 (both above threshold), so per-layer Tℓ agree with the global T even in the late band.

THREE CAVEATS (don't over-read):
1. Linearization — rel_resid 0.476 @ rank 40 (0.381 @ r80). ~half the transition is nonlinear remainder; Koopman-lift is the upgrade. "One reducer" holds at first-order-linear only.
2. NO persistent |λ|≈1 modes (top ~0.92, mean 0.878, all contracting). The pre-registered "persistent-mode ≡ sign-is-the-decision" mapping is NOT seen at this grain — sign-is-the-decision may live in the nonlinear remainder, not the linear spectrum.
3. Bulk-stationarity does NOT contradict s329/s336 late-commit: a thin late-activating decision mode sits below the rank-40/P128/last-token operator-cosine resolution. Bulk transport stationary; thin decision event needs the mode-resolved read.

Bounds: single model, last-token grain, core_sim 0.717 a modest margin. Instrument trusted (G2 decisive, 5 planted worlds + smoke clean); stationarity is the qualified claim. ARMS §5b §P-CL-COLLAPSE-3-operator (do co-extensional spellings converge in the orbit register?). Results results/p_dmd_transport_s338/run_14b.
