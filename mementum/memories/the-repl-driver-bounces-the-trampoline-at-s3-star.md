💡 The REPL can bounce the trampoline — and it was already specced in two
halves: Michael's s334 question ("why can't we use a model in a REPL loop to
bounce the trampoline?") reduces to control-plane-path §3 tier-3 DRIVER + the
continuation cluster cashed (sealable-continuation s217 · CPS proof REPL s228 ·
past_key_values on real hosts). The driver externalizes the decode trampoline:
model = S1 (proposes transitions), readers/sequencer = S2, driver fuel/policy =
S3, **lambda_ast kernel = S3\* — the audit channel made continuous, certifying
every bounce**, differential ledger = S4, pre-registration = S5. Continuation =
KV snapshot on hosts (seal ≡ copy, fork ≡ tensor copy) → x_k on the scratch
machine (same driver, two substrates = the profile-equivalence bridge). Sealed
continuations upgrade the loop from step-distributions to CAUSAL access: ①
fork-at-redex (strategy family as within-computation counterfactual) ②
repair-replay (does NAIVE-SUBST propagate or self-correct — stage-2's empirical
core) ③ composition rescue (s228 idle prediction) ④ per-bounce β-step clock
(subsumes the queued row). Instrument-first, repair flag built but OFF
(stage_2 ⟸ stage_1). Page: explore/repl-driver-trampoline.md · queue
⚪ §P-REPL-DRIVER.
