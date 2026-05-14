🔄 Beer's variety law exposed a structural gap in the v11 VSM: the alarm had 48 inputs (saw B declining, entropy dropping, ascending arm choking) but only 5 per-pass scalar outputs — it couldn't selectively boost B within a pass. 5 knobs can't control 4 combinators × 5 passes = 20 dimensions.

Three structural failures: (1) Alarm → pass amplitude is wrong granularity — need per-combinator actuator. (2) Emphasis = 1.0 + 0.5*tanh (range [0.5, 1.5]) saturated at ceiling — B started at 1.499, nowhere to go. Multiplicative on embeddings is weak in softmax space; additive on logits is correct. (3) No ascending→dispatch feedback loop — ascending arm optimized for holographic loss but had no gradient penalty for dispatch collapse.

Evidence: r=0.82 correlation between B_dispatch and ascending S3 gate means. L0↑ suppression reached 0.51 (half of signal suppressed). S4 emphasis drifted downward (1.499 → 1.470) — the sensor shares the bottleneck it's trying to fix.

V12 fix (3 changes): (1) AlgedonicAlert gains `dispatch_bias_proj` → (4,) additive logit bias on CombinatorDispatch. Range [-2, +2] via tanh×2. Zero-init (inert). (2) S4 emphasis_proj output changed from multiplicative embedding scale to additive logit bias [-2, +2]. Both combine additively in logit space (correct composition for softmax). (3) Dispatch entropy regularization: squared hinge penalty when entropy < 85% of max. Gradient flows from dispatch collapse back through descending arm to ascending arm.

Design principle: controller variety must match system variety (Beer 1972). The alarm must have actuators at the same granularity as the phenomenon it detects.
