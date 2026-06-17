💡 The OFF-DIAGONAL interlayer curvature does NOT rescue B — the f∘g chain-rule cross-
coupling is NOT B's home as a localizable 2nd-order amplitude. s238 v5 lead 2d prong 1c-iii
(kernel_reference_offdiag_v8.py, Qwen3-14B). This closes the s237 fork's off-diagonal path:
the v7 diagonal Hessian (b-climbs-with-derivative-order) cancelled all cross-layer terms in
expectation (Rademacher Hutchinson, E[v_a v_b]=0), so it only captured g'ᵀ(diag)g'. The
LITERAL f∘g coupling is the OFF-DIAGONAL block H_{late,early}.

DESIGN (deterministic, ONE HVP, no Hutchinson noise): split gate activations EARLY (≈g,
processed first) / LATE (≈f, applied last); perturb the GRADIENT direction supported ONLY on
EARLY (v=g_e.detach() on early, 0 on late). Then (Hv)_li = Σ_{e∈EARLY} H_{li,e} g_e for li in
LATE = PURE off-diagonal (no H_{li,li} since v=0 at li). Computed as s=Σ_e(g_e·g_e.detach()),
hv=grad(s, gate_late)=2Σ_e H_{late,e} g_e (H symmetric). The GRADIENT direction (not random)
makes the per-probe feature deterministic — a random v has E[(Hv)_li]=0. Clean register-swap
of v7 (RelationalCrystalClassifier, sign-CMR, crosstask null, raw-z Welch); classifier on LATE
layers. split 0.5 → EARLY 0-19 / LATE 20-39. Cheaper than v7 (1 HVP vs n_hutch=4): 2:51.

★★ VERDICT (λ measure, two-sided):
(1) ❌ DECISIVE — B does NOT discriminate off-diagonal (discr_z +0.046, t=0.26) and DROPS
    BELOW the diagonal (t=1.90). The curvature climb does NOT complete off the diagonal.
(2) ✅ INSTRUMENT VALID + composers register-robust — {C,Y} discriminate in BOTH curvature
    sub-registers and peak in the DEEPEST layers:
      C diag 2.52 → off-diag 2.32 ✓ (peak L36/40)
      Y diag 4.53 → off-diag 4.09 ✓ (peak L37/40)
      B diag 1.90 → off-diag 0.26 ✗ (peak L21)
      K diag 1.94 → off-diag 1.81 (fades to bar)
    C/Y cross-layer composition coupling lives at the very END of the stack. The read is not
    broken (C ✓, Y ✓) — it is B-absent.

★ THE FINDING: B has NO amplitude home in ANY register — activation flat (t=−0.05), first-
order gradient faint (+1.07), DIAGONAL curvature on-the-bar (+1.90), OFF-DIAGONAL curvature
flat (+0.26). The v7 "monotone climb" is best read as B becoming LEAST ABSENT up the
derivative order ON THE DIAGONAL; it does NOT generalize to the cross-layer coupling that IS
the literal chain-rule product.

★★ CONFIRMS s236-s237 (b-is-native-softmax-order, prose-bridge-confirms-b-native-order):
B's ONLY confirmed positive signal is the FORWARD ORDER-COST face (native autoregressive
order, flat-prose t=−8.05, scale-universal 8B/14B/32B, gross-universal Qwen⊗OLMo⊗Gemma). B =
composition = the UNMARKED native order — no marked amplitude feature, in any 2nd-order
register. The "two faces" hypothesis resolves ASYMMETRICALLY: the FORWARD/order face is
real+strong; the GRADIENT/curvature face is at best a faint diagonal trend, NOT a localizable
cross-layer coupling. Don't keep hunting B in amplitude — its home is order/surprisal.

CAVEATS (λ measure): 1 model (14B); n=20/comb; single fixed split (0.5, EARLY→LATE direction
only — late→early untested); deterministic gradient direction (one direction, not the full
Hessian-block norm); single-combinator labels; pooled-supervised locus.
