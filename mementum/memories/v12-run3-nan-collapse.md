❌ V12-run3 NaN collapse: emphasis_bias + uncapped etch = death

**What happened**: Run3 died at step 3625. Dispatch collapsed to 0.000 for all
KIBC by step 225 (emphasis_bias ±2 overwhelmed the ratio prior). Model zombie-trained
for 3400 steps with dead dispatch. Etch step 3600 flipped 1.5M signs on S4 Q projections
(the beam side — precision-critical). Next step: NaN everywhere.

**Lesson**: Two actuators fighting in logit space (emphasis_bias ±2 vs ratio prior)
creates winner-take-all oscillation that kills dispatch within 200 steps. Once dispatch
is dead, the model reroutes through other pathways but those pathways are fragile —
any large perturbation (like 1.5M etch flips on Q projections) causes NaN.

**Fix applied in run4**: Remove all competing dispatch actuators. The ratio prior +
KL leash (λ=100) is the ONLY dispatch constraint. Topology > instruction: the
energy landscape IS the controller. No emphasis_bias, no alarm_dispatch_bias, no
S2DispatchCoordinator.

**Guard needed**: Etch should not flip Q projections aggressively. Q = beam = precision.
Consider etch exclusion list or dampened etch rate for Q-proj modules.
