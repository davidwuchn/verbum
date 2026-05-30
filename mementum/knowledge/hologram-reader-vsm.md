---
title: "Hologram Reader VSM — Reading the Full Opcode Map from a Teacher"
status: designing
category: architecture
tags: [vsm, statechart, hologram, reader, isa, opcode, moire, extraction]
related:
  - holographic-computer.md
  - moire-addressing.md
  - retrieval-lattice.md
  - crystal-universality.md
  - project-thesis.md
depends-on:
  - holographic-computer.md
  - moire-addressing.md
  - crystal-universality.md
created: session 172
---

# Hologram Reader VSM

> A VSM tensor statechart that reads the full opcode map from a
> teacher model. Not a single-pass decoder — a self-directing
> measurement system that adapts its probing strategy based on
> what it discovers, allocates compute where the hologram is
> richest, and emits a complete structured description of both
> the compute ISA and the knowledge index.

## Why a VSM, Not a Script

The ISA decoder v2 is a linear pipeline: fingerprint → overlay →
trace → emit. It works. But it misses structure:

- It doesn't know which layers are **worth probing deeper** (the
  ENRICH zone has more to say than SILENT layers)
- It doesn't connect the **compute ISA** (KIBC programs) with the
  **knowledge index** (moiré relation families)
- It doesn't adapt — if it finds an unexpected opcode distribution,
  it can't decide to probe further
- It produces a flat table, not a structured map

A VSM reader is self-directing. S4 (intelligence) decides what to
probe next. S3 (control) allocates compute budget. S2 (coordination)
keeps measurements consistent. S1 (operations) runs the actual
probes. S5 (identity) is the combinator basis itself — the
mathematical invariant that all measurements reference against.

The reader IS the inverse of the holographic computer: the computer
writes programs into gratings during pretraining; the reader
recovers those programs from the gratings.

## Architecture

```
λ hologram_reader(model).

  S5(identity):    combinator_basis ∧ relation_basis ∧ measurement_invariants
  S4(intelligence): adaptive_probe_strategy ∧ anomaly_detection ∧ coverage_tracking
  S3(control):     compute_budget ∧ layer_priority ∧ depth_allocation
  S2(coordination): canonical_forms ∧ cross_layer_consistency ∧ accumulator
  S1(operations):  fingerprint ∧ overlay ∧ moiré ∧ trace ∧ classify ∧ emit
```

## S5 — Identity (what the reader IS)

The reader's identity is the mathematical basis it measures against.
This never changes during a scan. It IS the crystal.

```
λ basis(x).     combinator_fingerprints ≡ {K, I, B, C, D, Y, W, WHNF}
                ∧ beta_fingerprints ≡ {β_K, β_I, β_apply, β_compose}
                | 12_opcodes ≡ the_instruction_set
                | fingerprints ≡ empirical_basis_vectors(from_reduction_pairs)
                | cached: fingerprints.npz ≡ reusable_across_scans
                | model_specific: fingerprints_vary_by_model(same_semantics)
                | invariant: combinator_ordering(B ≥ K ≥ C >> I) ≡ universal

λ relation_basis(x). relation_fingerprints ≡ {capital, language, continent, ...}
                | from: probes/fact_recall_extended.json (204 probes, 15 categories)
                | moiré_centroids ≡ relation_directions_in_activation_space
                | crystallization ≡ variance_explained_by_centroid
                | these ARE the knowledge opcodes (complement to compute opcodes)

λ invariants(x). crystal_cos_threshold ≡ 0.84 (sign ≈ weight)
                | phi_ratio ≡ 0.6299 ± 0.019 (SVD spectrum)
                | decay_alpha ≡ 1.18 ± 0.006 (attention log-distance)
                | zone_ratios ≡ {aperture: 0-5%, fan: 30-50%, converge: 1-5%}
                | ∀measurement → reference(these_invariants) ≡ calibration
```

## S4 — Intelligence (adaptive probing)

The reader adapts. After each measurement phase, S4 evaluates what
was found and decides what to probe next. This is where the VSM
earns its keep over a linear script.

```
λ adapt(findings).
  | unexpected_opcode(layer) → probe_deeper(layer, more_pairs)
  | high_selectivity(layer) → mark_as(ENRICH_candidate)
  | low_rank(moiré, layer) → skip_knowledge_probe(layer)
  | anomalous_zone_boundary → refine_zone_classification
  | coverage_gap(opcode) → add_fingerprint_pairs(opcode)
  | convergence_detected → advance_to_next_phase

λ coverage(scan).
  | compute_coverage ≡ fraction_of_opcodes_with_confident_assignment
  | knowledge_coverage ≡ fraction_of_ENRICH_layers_with_moiré_decomposition
  | depth_coverage ≡ fraction_of_layers_scanned
  | target: compute ≥ 0.95, knowledge ≥ 0.80, depth = 1.0
  | under_target → S3:allocate_more_compute

λ anomaly(measurement).
  | opcode_strength < 0.05 ∧ expected > 0.20 → flag(silent_layer)
  | moiré_selectivity < 1.5 × gate → flag(weak_hologram)
  | zone_transition ≠ expected → flag(boundary_shift)
  | cross_layer_inconsistency → flag(S2_coordination_failure)
  | ∀anomaly → log ∧ probe_deeper ∨ skip_and_note
```

## S3 — Control (resource allocation)

Scanning a 70B model is expensive. S3 decides where to spend
compute. Key insight: not all layers deserve equal attention.

```
λ budget(model).
  | total_compute ≡ user_specified ∨ auto(proportional_to_n_layers)
  | phase_allocation:
  |   FINGERPRINT: 30% (one-time, cached)
  |   SCAN:        40% (overlay decode, all layers)
  |   CLASSIFY:     5% (zone assignment, cheap)
  |   MOIRÉ:       20% (only ENRICH layers, expensive per layer)
  |   MAP:          3% (assembly, cheap)
  |   EMIT:         2% (output, trivial)

λ priority(layer, phase).
  | zone_A(layer) → low_priority(moiré) ∧ medium_priority(overlay)
  | zone_B(layer) → high_priority(moiré) ∧ high_priority(overlay)
  | zone_C(layer) → low_priority(moiré) ∧ medium_priority(overlay)
  | ENRICH(layer) → maximum_priority(moiré)
  | SILENT(layer) → skip(moiré)
  | adaptive: priority_updates_as_zone_classification_refines

λ depth(probe, layer).
  | fingerprint_pairs_per_op: default 10, expand to 20 if anomalous
  | overlay_resolution: full(all 12×12 couplings) vs quick(diagonal only)
  | moiré_probes: 52 (quick) or 204 (full) or 500+ (research)
  | fact_categories: 15 (standard) or expand if capacity question
  | each_controlled_by_S3 ∧ adapted_by_S4
```

## S2 — Coordination (canonical forms and consistency)

What must stay consistent across all measurements so the opcode
map composes into a single coherent picture.

```
λ accumulator(x).
  | opcode_map ≡ dict[layer_idx → LayerDescriptor]
  | LayerDescriptor:
  |   layer_idx: int
  |   layer_type: "full_attn" | "linear_attn"
  |   zone: "A" | "B" | "C" (compute zone)
  |   retrieval_zone: "SILENT" | "ENRICH" | "SUPPRESS" | "COMMIT"
  |   sparsity: float (fraction of FFN neurons active)
  |   overlay_matrix: array[12, 12] (combinator-space transform)
  |   dominant_opcode: str (strongest diagonal element)
  |   dominant_transform: tuple[str, str, float] (strongest off-diagonal)
  |   transform_strength: float (off-diagonal norm)
  |   moiré_selectivity: float | None (if ENRICH layer)
  |   moiré_rank: int | None (effective rank of moiré space)
  |   moiré_relation_coherence: float | None (within/cross relation ratio)
  |   relation_crystallization: dict[str, float] | None (variance explained per relation)
  |   phase: "build" | "execute" | "emit" (three-phase pipeline position)

λ consistency(measurements).
  | fingerprints ≡ same_basis_for_all_layers (S5 provides)
  | probe_set ≡ same_probes_for_all_moiré_measurements
  | normalization ≡ unit_vectors_everywhere
  | ∀overlay_matrix → same_basis_ordering(ALL_OP_NAMES)
  | ∀moiré_measurement → same_probe_set ∧ same_gate_text
  | cross_check: overlay_diagonal(layer) ≈ activation_trace(layer)

λ canonical_output(map).
  | JSON: opcode_map.json ≡ human_readable(summary ∧ per_layer)
  | NPZ: opcode_map.npz ≡ machine_readable(overlay_matrices ∧ moiré_data)
  | fields:
  |   meta: {model, n_layers, d_model, d_ff, scan_timestamp, phases_completed}
  |   summary: {zone_boundaries, phase_boundaries, n_opcodes, n_relations}
  |   per_layer: [LayerDescriptor × n_layers]
  |   overlay_tensor: array[n_layers, 12, 12] (the full combinator transform stack)
  |   moiré_tensor: array[n_enrich_layers, n_probes, d_ff] | None
  |   relation_centroids: array[n_relations, d_ff] | None
```

## S1 — Operations (the measurement tools)

Concrete operations. Each is a function that takes model + config
and returns structured measurements.

```
λ fingerprint(model, pairs).
  | for_each(op ∈ ALL_OPS):
  |   for_each(pair ∈ pairs[op]):
  |     pre_activation ← capture_ffn(model, pre_text, all_layers)
  |     post_activation ← capture_ffn(model, post_text, all_layers)
  |     delta ← pre - post
  |   fingerprint[op] ← normalize(mean(deltas))
  | output: dict[op_name → array[n_layers, d_model]]
  | cache: fingerprints_{model_slug}.npz
  | reuse: isa_decoder_v2.py::build_fingerprints (same logic)

λ overlay(model, layer, fingerprints).
  | gate_w ← model.layers[layer].mlp.gate_proj.weight
  | up_w ← model.layers[layer].mlp.up_proj.weight
  | down_w ← model.layers[layer].mlp.down_proj.weight
  | for_each(op_i ∈ ALL_OPS):
  |   gate_resp ← fingerprint[op_i] @ gate_w.T
  |   up_resp ← fingerprint[op_i] @ up_w.T
  |   silu_resp ← gate_resp * sigmoid(gate_resp)
  |   combined ← silu_resp * up_resp
  |   output ← combined @ down_w.T
  |   for_each(op_j ∈ ALL_OPS):
  |     overlay[i, j] ← cos(output, fingerprint[op_j])
  | output: array[12, 12] — the combinator-space transform
  | reuse: isa_decoder_v2.py::read_static_program (same logic, per-layer)

λ classify_zone(overlays, sparsities).
  | compute_zone:
  |   sparsity < 0.10 → zone_A (aperture)
  |   sparsity > 0.25 → zone_B (fan/compute)
  |   sparsity < 0.05 ∧ depth > 0.85 → zone_C (converge)
  | retrieval_zone:
  |   avg_fact_delta ≈ 0 → SILENT
  |   avg_fact_delta > 0 ∧ boost% > 0.70 → ENRICH
  |   boost% < 0.30 → SUPPRESS
  |   final_layers → COMMIT
  | pipeline_phase:
  |   transform_strength > 1.0 → build
  |   0.7 < transform_strength ≤ 1.0 → execute
  |   transform_strength < 0.7 → emit
  | output: per_layer zone + retrieval_zone + phase assignments

λ moiré(model, layer, probes).
  | for_each(probe ∈ probes):
  |   activation ← forward(model, probe.prompt, capture_at=layer)
  |   gate_act ← capture(gate_proj_output)
  |   up_act ← capture(up_proj_output)
  |   moiré_act ← silu(gate_act) * up_act
  |   record(probe.id → moiré_act)
  | selectivity ← mean_pairwise_cos(moiré_activations)
  | rank ← effective_rank(moiré_activations)
  | relation_coherence ← within_relation_cos / cross_relation_cos
  | crystallization ← per_relation_variance_explained_by_centroid
  | output: MoiréDescriptor per layer
  | reuse: moire_selectivity.py ∧ moire_decompose.py (same measurements)

λ trace(model, inputs, checkpoints).
  | for_each(input ∈ inputs):
  |   for_each(cp ∈ checkpoints):
  |     activation ← forward(model, input, capture_at=cp)
  |     projection ← activation @ fingerprint_matrix.T
  |     dominant_op ← argmax(projection)
  |     attention_pattern ← capture_attention(cp)
  |   record(input → activation_trace)
  | output: per_input activation trajectory through layers
  | confirms: static overlay matches dynamic execution
  | reuse: isa_decoder_v2.py::trace_inputs (same logic)

λ emit(accumulator).
  | validate: ∀layer ∈ accumulator → has(overlay ∧ zone ∧ phase)
  | assemble: opcode_map.json ∧ opcode_map.npz
  | summary: zone_boundaries ∧ phase_boundaries ∧ opcode_census
  | opcode_census:
  |   for_each(op ∈ ALL_OPS):
  |     layers_where_dominant ← [l for l if dominant_opcode[l] == op]
  |     avg_strength ← mean(overlay_diagonal[op] across all layers)
  | relation_census:
  |   for_each(rel ∈ relations):
  |     crystallization ← mean across ENRICH layers
  |     layers_where_active ← [l for l if relation_coherence[l] > threshold]
```

## The State Machine

The reader has six states, driven by completion events from S1
operations. S4 can inject probe-deeper events that loop the
machine back.

```
         ┌──────────────┐
         │   DORMANT    │ (no model loaded)
         └──────┬───────┘
                │ load(model)
                ▼
         ┌──────────────┐
         │ FINGERPRINT  │ S1: build/load combinator fingerprints
         └──────┬───────┘
                │ fingerprints_ready
                ▼
         ┌──────────────┐
    ┌───▶│    SCAN      │ S1: overlay decode, all layers
    │    └──────┬───────┘
    │           │ scan_complete
    │           ▼
    │    ┌──────────────┐
    │    │  CLASSIFY    │ S1: zone + phase assignment
    │    └──────┬───────┘
    │           │ classified
    │           ▼
    │    ┌──────────────┐
    │    │   MOIRÉ      │ S1: moiré decomposition (ENRICH layers only)
    │    └──────┬───────┘
    │           │ moiré_complete
    │           │
    │     S4 ───┤ anomaly_detected → probe_deeper
    │    ┌──────┘                         │
    │    │                                │
    │    ▼                                │
    │    ┌──────────────┐                 │
    │    │    MAP       │ S1: assemble    │
    │    └──────┬───────┘                 │
    │           │ map_complete            │
    │           ▼                         │
    │    ┌──────────────┐                 │
    │    │    EMIT      │ S1: write       │
    │    └──────┬───────┘                 │
    │           │ complete                │
    │           ▼                         │
    │    ┌──────────────┐                 │
    │    │    DONE      │                 │
    │    └──────────────┘                 │
    │                                     │
    └─────────────────────────────────────┘
          probe_deeper → SCAN (with refined params)
```

### Transitions

```python
TRANSITIONS = {
    # (current_state, event) → next_state
    ("DORMANT",     "load"):               "FINGERPRINT",
    ("FINGERPRINT", "fingerprints_ready"):  "SCAN",
    ("SCAN",        "scan_complete"):       "CLASSIFY",
    ("CLASSIFY",    "classified"):          "MOIRÉ",
    ("MOIRÉ",       "moiré_complete"):      "MAP",
    ("MOIRÉ",       "probe_deeper"):        "SCAN",      # S4 loop-back
    ("MAP",         "map_complete"):        "EMIT",
    ("MAP",         "probe_deeper"):        "SCAN",      # S4 loop-back
    ("EMIT",        "complete"):            "DONE",
}
```

### Events from S4

S4 monitors the accumulator after each phase and can inject events:

| Condition | Event | Effect |
|-----------|-------|--------|
| Unexpected opcode in >5% of layers | `probe_deeper` | Return to SCAN with expanded fingerprint pairs |
| Moiré rank still growing at max probes | `probe_deeper` | Return to MOIRÉ with expanded probe set |
| Zone boundaries shifted from expected | `anomaly_logged` | Note in output, continue |
| Coverage < target after all phases | `probe_deeper` | One more pass with focused attention |

### Guards

| Transition | Guard |
|-----------|-------|
| DORMANT → FINGERPRINT | Model loaded successfully |
| MOIRÉ start | At least one ENRICH layer identified |
| probe_deeper | Budget remaining > 0 ∧ iteration < max_iterations |

## Output Artifact: The Opcode Map

The opcode map IS the hologram readout. It's the structured
description of what the model computes and what it stores.

```
opcode_map/
  meta.json           # model, scan params, timing, phases
  summary.json        # zone boundaries, phase boundaries, opcode census
  layers.json         # per-layer descriptors (human-readable)
  overlay.npz         # [n_layers, 12, 12] overlay tensor
  moiré.npz           # [n_enrich, n_probes, d_ff] moiré activations
  centroids.npz       # [n_relations, d_ff] relation direction centroids
  fingerprints.npz    # [12, n_layers, d_model] basis vectors
```

### Summary Format

```json
{
  "model": "Qwen/Qwen3-0.6B",
  "n_layers": 28,
  "d_model": 1024,
  "d_ff": 3072,

  "compute_zones": {
    "A": {"layers": [0, 1, 2], "label": "aperture"},
    "B": {"layers": [3, 4, "...", 24], "label": "fan/compute"},
    "C": {"layers": [25, 26, 27], "label": "converge"}
  },

  "retrieval_zones": {
    "SILENT":   {"layers": [0, "...", 15]},
    "ENRICH":   {"layers": [16, "...", 24]},
    "SUPPRESS": {"layers": [25, 26]},
    "COMMIT":   {"layers": [27]}
  },

  "pipeline_phases": {
    "build":   {"layers": [0, "...", 8], "avg_transform": 1.17},
    "execute": {"layers": [9, "...", 20], "avg_transform": 0.95},
    "emit":    {"layers": [21, "...", 27], "avg_transform": 0.69}
  },

  "opcode_census": {
    "K":  {"dominant_layers": 5, "avg_diagonal": 0.42},
    "I":  {"dominant_layers": 3, "avg_diagonal": 0.38},
    "B":  {"dominant_layers": 7, "avg_diagonal": 0.45},
    "...": "..."
  },

  "relation_census": {
    "capital":   {"crystallization": 0.96, "enrich_layers": 8},
    "language":  {"crystallization": 0.97, "enrich_layers": 7},
    "...": "..."
  },

  "invariant_checks": {
    "combinator_ordering": "B ≥ K ≈ C >> I",
    "phi_ratio": 0.627,
    "decay_alpha": 1.18
  }
}
```

## Connection to Existing Tools

The reader doesn't reinvent — it orchestrates:

| Existing Tool | S1 Operation | Reuse |
|---------------|-------------|-------|
| `isa_decoder_v2.py::build_fingerprints` | `λ fingerprint` | Exact same logic, generalized to any model |
| `isa_decoder_v2.py::read_static_program` | `λ overlay` | Exact same logic, per-layer |
| `isa_decoder_v2.py::trace_inputs` | `λ trace` | Same logic, confirmation pass |
| `moire_selectivity.py` | `λ moiré` (selectivity) | Same measurement |
| `moire_decompose.py` | `λ moiré` (rank + crystallization) | Same measurement |
| `tensor_statechart.py` | VSM engine pattern | State machine skeleton |

The new contribution is the **orchestration layer** (S4 + S3 + S2)
that connects these measurements into a self-directing scan and
produces a unified output.

## What This Enables

1. **Any-model opcode map.** Run on Qwen3-0.6B, 4B, 14B, 32B.
   Compare opcode maps across scales. The invariants (KIBC ordering,
   phi ratio, zone structure) should match. The details (which
   layers, how many relations, moiré rank) will differ.

2. **Capacity scaling measurement.** The moiré rank per ENRICH layer
   as a function of d_ff is THE experiment for the capacity question.
   The reader produces this automatically.

3. **Extraction target specification.** The opcode map tells you
   exactly what needs to be in the ternary artifact: which layers
   carry which opcodes, where the knowledge lives, what the zone
   boundaries are.

4. **Cross-model comparison.** Run on Qwen and Pythia. Compare
   overlay tensors. The universal crystal predicts high correlation.
   The opcode map makes this a structured comparison, not ad hoc.

5. **Research instrument.** A principled measurement system that
   accumulates knowledge and adapts — not a one-shot script that
   you modify by hand for each experiment.
