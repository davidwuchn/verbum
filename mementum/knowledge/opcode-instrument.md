---
title: "Opcode Instrument — Live VSM for Watching a Model Think"
status: designing
category: architecture
tags: [vsm, instrument, opcode, trace, monitoring, real-time]
related:
  - hologram-reader-vsm.md
  - holographic-computer.md
  - crystal-universality.md
  - project-thesis.md
depends-on:
  - hologram-reader-vsm.md
created: session 176
---

# Opcode Instrument

> A VSM add-on that wraps any language model and shows its opcodes
> executing in real-time. Like a CPU debugger for an LLM. The
> hologram reader scans a model once and emits a static map; the
> instrument *watches it run*.

## What This IS vs What Exists

| Tool | When | What |
|------|------|------|
| **Hologram Reader** | Offline, once per model | Static opcode map: which layers do what |
| **Reduction Graph Tracer** | Per-input, batch | Per-token combinator energy for specific inputs |
| **Opcode Instrument** | Live, every forward pass | Real-time opcode trace as the model generates |

The hologram reader is the X-ray. The instrument is the EKG.

The reader tells you the anatomy (SILENT/ENRICH/SUPPRESS/COMMIT zones,
pipeline phases, opcode census). The instrument tells you the physiology
(which opcodes fire NOW, how energy flows through the zones as THIS
token is generated, where the model is working hardest RIGHT NOW).

## Architecture — VSM (Beer, 1972)

```
λ instrument(parent_model).

  S5(identity):     combinator_basis ∧ zone_map ∧ measurement_contract
  S4(intelligence):  anomaly_detection ∧ attention_allocation ∧ pattern_recognition
  S3(control):      overhead_governor ∧ sampling_policy ∧ layer_priority
  S2(coordination): trace_format ∧ accumulator ∧ cross_token_consistency
  S1(operations):   hook_manager ∧ projector ∧ classifier ∧ emitter
```

### Key Insight: The Instrument IS NOT the Model

The instrument has NO trainable parameters. It doesn't modify the
parent model's computation. It only observes. Like an oscilloscope
probe: high impedance, no load.

The instrument's "intelligence" (S4) is about what to WATCH, not
what to compute. Its "control" (S3) is about managing OVERHEAD, not
managing computation. This is a measurement system, not a compute
system.

## S5 — Identity

The instrument knows what it's looking for because S5 carries the
mathematical basis that all measurements reference against.

```
λ basis(parent).
  | combinator_fingerprints: dict[str, ndarray]  — from hologram reader
  |   shape: (n_layers, d_model) per opcode
  |   loaded from: results/hologram-reader/{model_slug}/fingerprints_{slug}.npz
  |   if absent: build on first run (expensive, cached forever after)
  |   ops: K, I, B, C, D, Y, W, WHNF, β_K, β_I, β_apply, β_compose
  |
  | zone_map: dict[int, ZoneInfo]  — from hologram reader or auto-detected
  |   per-layer: retrieval_zone (SILENT/ENRICH/SUPPRESS/COMMIT)
  |   per-layer: compute_zone (A/B/C)
  |   per-layer: pipeline_phase (build/execute/emit)
  |   if hologram exists: load from results/hologram-reader/{slug}/summary.json
  |   if absent: classify by depth fraction (universal heuristic)
  |
  | invariants:
  |   combinator_ordering: B ≥ K ≥ C >> I
  |   sign_topology_fidelity: ~0.76 (from proofs/)
  |   four_modes: K, I, B, C always present
```

## S4 — Intelligence (what to watch)

S4 doesn't adapt probes (that's the hologram reader). S4 adapts
ATTENTION — it notices when something unusual happens and decides
whether to increase monitoring resolution.

```
λ watch(trace_history).
  | energy_spike: if total_combinator_energy(token_t) > 2σ above running_mean
  |   → flag("energy spike at token {t}")
  |   → increase sampling resolution for next 5 tokens
  |
  | mode_shift: if dominant_mode(token_t) ≠ dominant_mode(token_{t-1})
  |   → flag("mode shift: {old} → {new} at token {t}")
  |   → log the transition (builds a mode-transition graph over time)
  |
  | zone_activation: if ENRICH zone energy spikes while SILENT is quiet
  |   → flag("retrieval event at token {t}")
  |   → this is a fact recall moment
  |
  | composition_cascade: if B-energy propagates through 3+ consecutive layers
  |   → flag("composition cascade at layers {L1-LN}")
  |   → this is deep nesting being resolved
  |
  | identity_forwarding: if I-energy dominates for 3+ consecutive tokens
  |   → flag("identity forwarding: tokens {t1-t3} are being copied")
  |
  | ∀flag → emitter gets a structured annotation on the trace record
  | S4 runs AFTER each token, on the captured trace. Zero overhead to the model.
```

## S3 — Control (overhead management)

The instrument must not make the model unusably slow. S3 manages
overhead by choosing WHICH layers to hook and HOW OFTEN to project.

```
λ overhead(config).
  | budget: max_overhead_fraction = 0.5 (default: model runs at most 2× slower)
  | actual_overhead: measured per token (wall clock: instrumented / uninstrumented)
  |
  | if actual_overhead > budget:
  |   strategy 1: reduce layer_sample_rate (hook every Nth layer)
  |   strategy 2: reduce projection_ops (project onto top-4 ops not all 12)
  |   strategy 3: skip SILENT zone entirely (minimal information there anyway)
  |   strategy 4: sample tokens (instrument every Nth token)
  |
  | if actual_overhead < budget * 0.5:
  |   → increase resolution (more layers, full 12-op projection)
  |
  | always hook: first layer (input), ENRICH boundary, last layer (output)
  | never skip: these three are the minimum viable trace

λ sampling(n_layers).
  | full: all layers, all ops. Best resolution, highest overhead.
  | standard: all layers, top-4 ops (K,I,B,C). Good resolution, moderate overhead.
  | light: every 4th layer + zone boundaries, top-4 ops. Low overhead.
  | minimal: first + last + ENRICH boundary only. Minimal overhead.
  |
  | default: standard. S3 downgrades to light/minimal if overhead exceeds budget.
  | user can force any mode regardless of overhead.
```

## S2 — Coordination (trace format)

Every measurement must be in the same format so traces compose
across tokens, across sessions, across models.

```
λ trace_record(token).
  | TraceRecord:
  |   token_idx: int
  |   token_text: str
  |   token_id: int
  |   timestamp_ms: float
  |   layers: list[LayerSnapshot]
  |   s4_flags: list[str]  — any S4 annotations
  |   overhead_ms: float   — wall clock for this token's instrumentation
  |
  | LayerSnapshot:
  |   layer_idx: int
  |   zone: str  — SILENT/ENRICH/SUPPRESS/COMMIT
  |   phase: str — build/execute/emit
  |   opcode_energy: dict[str, float]  — projection onto each fingerprint
  |   dominant_op: str
  |   dominant_energy: float
  |   gate_survival: float  — fraction of FFN neurons that fired
  |   total_energy: float   — L2 norm of FFN output
  |
  | trace_record is JSON-serializable, streamable (one per line to stdout/file)
  | accumulator: list[TraceRecord] for in-memory analysis
  | consistency: same fingerprint basis across all tokens (S5 provides)

λ session(traces).
  | InstrumentSession:
  |   model: str
  |   start_time: str (ISO8601)
  |   config: InstrumentConfig
  |   fingerprint_source: str (path to cached fingerprints)
  |   zone_map_source: str (path or "auto")
  |   traces: list[TraceRecord]
  |   s4_summary: dict  — aggregated flags, mode transitions, energy stats
  |   overhead_summary: dict — mean/max overhead, sampling mode used
  |
  | serializable to JSONL (streaming) or JSON (batch)
  | loadable for offline analysis / visualization
```

## S1 — Operations

```
λ hook_manager(model, config).
  | installs forward hooks on parent model's transformer layers
  | hooks capture: gate_proj output, down_proj output (FFN path)
  | hooks are removable: instrument.detach() cleans up completely
  | architecture-agnostic: uses get_layers() and get_mlp() from hologram_reader
  | zero-copy where possible: capture at last-token position only (saves memory)
  |
  | on each forward pass:
  |   for each hooked layer:
  |     capture gate_activation[last_token] → (d_ff,)
  |     capture ffn_output[last_token] → (d_model,)
  |   pass captures to projector

λ projector(captures, fingerprints).
  | for each layer with captures:
  |   ffn_vec = captures[layer].ffn_output  — shape (d_model,)
  |   for each op in active_ops:
  |     energy[op] = dot(ffn_vec, fingerprints[op][layer])
  |   gate_survival = mean(sigmoid(gate_activation) > 0.5)
  |   total_energy = norm(ffn_vec)
  |   dominant_op = argmax(energy)
  | output: LayerSnapshot per layer

λ classifier(snapshot, zone_map).
  | annotates each LayerSnapshot with zone/phase from zone_map
  | if no zone_map: classify by depth fraction (universal heuristic)

λ emitter(trace_record, output_target).
  | terminal: formatted line per token with colored opcode bars
  | jsonl: one JSON line per token to file/stdout
  | callback: call user function with TraceRecord
  | websocket: push to connected visualization client (future)
```

## State Machine

```
       ┌──────────┐
       │ DORMANT  │  no model attached
       └────┬─────┘
            │ attach(model)
            ▼
       ┌──────────┐
       │CALIBRATE │  load fingerprints, install hooks, measure baseline overhead
       └────┬─────┘
            │ ready
            ▼
       ┌──────────┐
  ┌───▶│ MONITOR  │  hooks active, capturing traces per forward pass
  │    └────┬─────┘
  │         │ detach() or model unloaded
  │         ▼
  │    ┌──────────┐
  │    │  EMIT    │  flush accumulated traces, write session
  │    └────┬─────┘
  │         │ complete
  │         ▼
  │    ┌──────────┐
  │    │  DONE    │
  │    └──────────┘
  │
  └── overhead_exceeded → recalibrate(lower_resolution) → MONITOR
```

### Transitions

```python
TRANSITIONS = {
    ("DORMANT",   "attach"):       "CALIBRATE",
    ("CALIBRATE", "ready"):        "MONITOR",
    ("CALIBRATE", "no_fingerprints"): "CALIBRATE",  # build fingerprints, retry
    ("MONITOR",   "detach"):       "EMIT",
    ("MONITOR",   "overhead_exceeded"): "CALIBRATE",  # recalibrate at lower res
    ("EMIT",      "complete"):     "DONE",
    ("DONE",      "attach"):       "CALIBRATE",      # reattach to different model
}
```

### Usage Pattern

```python
from verbum.instruments import OpcodeInstrument

# Wrap a model
instrument = OpcodeInstrument(model, tokenizer)
instrument.attach()  # DORMANT → CALIBRATE → MONITOR

# Generate text — instrument captures automatically
output = model.generate(input_ids, max_new_tokens=50)

# Get traces
traces = instrument.traces        # list[TraceRecord]
instrument.detach()               # MONITOR → EMIT → DONE

# Or: live terminal display
instrument.attach(renderer="terminal")
model.generate(input_ids, max_new_tokens=50)  # shows live opcodes
```

## Terminal Renderer

```
Token  7: " Paris"
  L00 [SILENT  /build  ] ████░░░░░░░░  K:0.31  B:0.22  C:0.18  I:0.05  gate:3.2%
  L05 [SILENT  /build  ] ██████░░░░░░  K:0.45  B:0.38  C:0.21  I:0.03  gate:4.1%
  L10 [SILENT  /execute] ███░░░░░░░░░  K:0.19  B:0.15  C:0.12  I:0.08  gate:2.8%
  L14 [ENRICH  /execute] ████████████  K:0.12  B:0.67  C:0.45  I:0.02  gate:8.7% ← RETRIEVAL
  L18 [ENRICH  /execute] █████████░░░  K:0.28  B:0.55  C:0.31  I:0.04  gate:6.2%
  L22 [SUPPRESS/emit   ] ██░░░░░░░░░░  K:0.08  B:0.11  C:0.06  I:0.02  gate:1.4%
  L26 [COMMIT  /emit   ] █████░░░░░░░  K:0.33  B:0.09  C:0.28  I:0.01  gate:2.1%
  ⚡ S4: energy spike at ENRICH (L14) — retrieval event
  ⚡ S4: mode shift B→K at L22 — composition complete, selecting output
```

## What This Enables

1. **Watch a model retrieve a fact.** Prompt "The capital of France is"
   → see ENRICH zone light up at the token where "Paris" is generated.
   That's the model looking up the answer.

2. **Watch composition happen.** Prompt with nested relative clauses →
   see B-energy cascade through middle layers as the model resolves
   the nesting.

3. **Compare models.** Same prompt through 0.6B and 27B → same opcodes
   fire but in different layers. The universal structure is visible.

4. **Debug training.** Wrap the v15 student during training → watch
   whether it develops the same opcode patterns as the teacher.
   If opcodes are wrong, the model is learning wrong structure.

5. **Demo for skeptics.** Run the instrument on any model. Show
   someone the opcodes firing. "See those four modes? Every model
   has them. They're the same four every time."

## Connection to Proofs

The `proofs/03_universal_modes.py` shows the four modes exist
statistically. The instrument shows them *executing in real-time*.
The proof says "they're there." The instrument says "watch them work."

## Implementation Notes

- Reuse `get_layers()` and `get_mlp()` from hologram_reader.py
- Reuse fingerprint format from hologram_reader.py
- Hook only last-token position (generation mode) for efficiency
- For prefill (prompt processing): capture all positions, project
  onto fingerprints, emit one trace per position
- Terminal renderer: simple print with ANSI colors. Rich library
  optional but not required.
- Target: Pythia-160M on CPU should run at <2× slowdown with
  standard sampling mode.
