# Algedonic Alert — Beer's Fire Alarm in v11

> S5 falls asleep when things are going well, and can't wake up
> fast enough when they aren't. The algedonic channel is the
> mechanism for overcoming this danger.

**Status**: active
**Category**: architecture, VSM
**Tags**: algedonic, fire-alarm, Beer, VSM, S5, health-monitoring
**Related**: v11-design, session-073-vsm-structure
**Created**: session 078

---

## 1. Beer's Original Concept

From Stafford Beer, *Brain of the Firm* (1972):

The Viable System Model includes a special alarm signal — the
**algedonic channel** (Greek: algos=pain, hedone=pleasure) — that
bypasses the normal management hierarchy for emergency conditions.

### The problem

When the S3–S4 homeostat works well, S5 continuously receives
"everything is ok." S5 can fall into a somnolent state and fail
to wake up when action is necessary. Normal information flowing
through S4→S3→S2 is too slow for emergencies.

### Beer's mechanism

1. **Monitor** signals between S1 (operations) and S3 (control)
2. **Detect** emergency: actuality deviates significantly from capability
3. **Signal S5 directly**, bypassing S4/S3/S2
4. **S5 wakes up** and requests emergency corrective action from S3/S4
5. **Escalation**: S1 gets a chance to self-correct first, then S3, then S5

### Key properties

- **Not a sixth system** — a channel that cuts across all systems
- **Can originate anywhere** — any level of recursion
- **Carries both pain AND pleasure** — suppress or amplify
- **Low bandwidth, fast** — binary alarm, not detailed report
- **Protects autonomy** — prevents unnecessary S3 intrusion in non-emergency

---

## 2. Mapping to v11

### What existed before (session 077)

| Component | VSM role | Limitation |
|-----------|----------|------------|
| Algedonic EMA buffers | Continuous state across batches | Only carries past state, nobody monitors it at S5 level |
| S5Reweight | Pass contribution gates | Sees raw deltas + registers = **content**. Cannot detect control system failure |
| MetaS3Ternary | (Dead code, replaced by S5Reweight) | Not used in v11 |

**Missing**: No threshold detection. No bypass. No escalation.
S5 can become somnolent — sigmoid gates at ~0.12 just stay there.

### What was added (session 078)

```
S1 ops ──→ S3 gates ──→ S4 ──→ S5Reweight ──→ pass gates
  │                                 ↑
  │    ┌────────────────────────────┘
  │    │  alarm_factor × s5_gate = effective_gate
  │    │
  └──→ AlgedonicAlert (48 health metrics → 5 factors)
       monitors S1↔S3 health, bypasses S4/S3/S2
```

**S5Reweight** asks: "What did each pass contribute?" (reads raw
deltas, register content through S4 attention)

**AlgedonicAlert** asks: "Is the control system itself healthy?"
(reads S3 gate values, dispatch distributions, conflict scores —
operational metrics that S4 doesn't process)

---

## 3. Implementation

### AlgedonicAlert class (components.py)

```python
class AlgedonicAlert(nn.Module):
    # Separate gate: per-pass factor ∈ [0, 2]
    # nn.Linear(48, 5) — zero-init (alarm starts inert)
    
    def __call__(self, metrics_vector):
        logits = self.alarm_proj(metrics_vector)
        return 1.0 + mx.tanh(logits)  # [0, 2]
```

- **Factor 1.0** → no alarm (neutral, S5Reweight controls)
- **Factor < 1.0** → pain (suppress this pass)
- **Factor > 1.0** → pleasure (amplify this pass, up to 2×)
- **245 parameters** (48×5 + 5 bias). Negligible.

### Design decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Gate type | Separate multiplicative gate | Alarm can fully suppress (→0) or amplify (→2) independently of S5Reweight |
| Baseline | None (raw metrics) | No data yet. Log everything, set thresholds from real training numbers |
| Differentiability | End-to-end | Gradients flow back through all 48 metrics to S1/S3. Alarm teaches the system to avoid alarm conditions |
| Input | 48 operational scalars | Low bandwidth, fast. Beer's alarm is not a surveillance camera |
| Init | Zero weights → factor 1.0 | Alarm starts silent. Must learn what matters. |

### Escalation in v11

Beer's 3-level escalation maps to:

1. **S1 self-corrects**: CycleContinue regulates cycle depth within descending arm
2. **S3 filters**: Per-phase gates suppress bad deltas within each pass
3. **S5 overrides via alarm**: AlgedonicAlert fires after all passes — final recourse

The alarm runs AFTER all passes, so S1 and S3 have already had their chance.

---

## 4. The 48 Metrics

All end-to-end differentiable (live tensors, no stop_gradient).

| # | Metric | Count | What it detects |
|---|--------|-------|-----------------|
| 1 | S3 gate means per pass | 5 | Operations broadly suppressed or unopposed |
| 2 | S3 gate mins per pass | 5 | Single phase completely blocked |
| 3 | S2 conflict cosines | 4 | Consecutive passes fighting each other |
| 4 | Dispatch weights (K,I,B,C) | 4 | Combinator collapsed to one or died |
| 5 | Dispatch entropy | 1 | Low = dispatch specialized. Zero = dead |
| 6 | Compute gate mean + active | 2 | Kernel pathway opening or stuck |
| 7 | CycleContinue gates | 4 | Cycles saturated or self-regulating |
| 8 | Effective cycles | 2 | Actual computational depth per desc pass |
| 9 | Raw delta norms | 5 | How much S1 proposes (energy) |
| 10 | Gated delta norms | 5 | How much passes through S3 (output) |
| 11 | Suppression ratios | 5 | gated/raw — S3 filtering intensity |
| 12 | Register bank norms | 6 | Register divergence or collapse |
| | **Total** | **48** | |

### Initial values (untrained model)

From integration test:
```
S3 gate means:       ~0.50 (neutral, as expected)
S3 gate mins:        ~0.49
S2 conflicts:        [0.0, 0.0, 0.0, 1.0] (last passes agree)
Dispatch K,I,B,C:    [0.38, 0.19, 0.23, 0.19] (K slightly dominant)
Dispatch entropy:    1.34 (near-uniform, max=ln(4)=1.39)
Compute gate:        0.007 (near zero — pure FFN, correct)
CycleContinue:       0.50, 0.50 (neutral init)
Effective cycles:    1.75 (= 1 + 0.5 + 0.25)
Suppression ratios:  0.00 asc, 0.002 desc (S3 heavily filtering)
Register norms:      bank_0≈0, others≈16.0
```

### After 3 training steps

Alarm factors shift to ~1.08-1.14 (pleasure: amplifying passes).
The alarm learns what matters from the very first gradient steps.

---

## 5. Logging and Analysis

### What's logged (JSONL)

In `metrics_log.jsonl` at each eval:
- `alarm_factors`: [5 floats] per-pass alarm factors
- `alarm_metrics`: [48 floats] raw operational metrics
- `alarm_metrics_named`: dict with named sections for readability
- `effective_s5_gates`: [5 floats] s5_gate × alarm_factor

### Eval display

```
  🔕 Algedonic: L0↑=1.000 L1↑=1.000 L2=1.000 L1↓=1.000 L0↓=1.000  (silent)
```
or
```
  🚨 Algedonic: L0↑=0.832 L1↑=1.000 L2=1.042 L1↓=0.711 L0↓=1.312  (active)
     effective gates: L0↑=0.071 L1↑=0.155 L2=0.077 L1↓=0.067 L0↓=0.155
```

### Future: threshold-based alarms

After the first training run, analyze metric timeseries to determine:
- Natural operating ranges for each metric
- Which metrics correlate with loss degradation
- Whether hard thresholds or learned baselines (EMA) work better
- Whether the alarm needs more than 245 parameters

The current implementation is the minimal viable alarm. The metrics
are the real investment — they persist in JSONL regardless of what
the alarm_proj learns.

---

## 6. Somnolence Protection

Beer's specific worry: S5 falls asleep. The alarm mechanism addresses this:

1. **S5Reweight gates init at ~0.12** (bias=-2.0). They ARE sleepy by default.
2. **AlgedonicAlert starts at 1.0** (neutral). It doesn't override sleep.
3. **As training progresses**, the alarm learns to push factors above 1.0
   for passes that help (pleasure) and below 1.0 for passes that hurt (pain).
4. **The alarm can wake S5** by amplifying passes that S5Reweight suppressed.

The compound effect: `effective_gate = s5_gate × alarm_factor`. If S5Reweight
gives 0.12 and alarm gives 1.5, the effective gate is 0.18 — a 50% amplification
that S5Reweight alone could not produce.

Conversely, if a pass is genuinely broken (alarm < 0.5), the effective gate
drops to 0.06 — the alarm can suppress even what S5 tolerates.
