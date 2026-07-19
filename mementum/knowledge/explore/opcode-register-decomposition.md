---
title: "Opcodes decompose across registers: gate vs attention-write vs QK-pattern"
status: active
category: exploration
tags: [opcodes, combinators, register, visibility, scale, superposition, tracer, opcodes-subsystem]
related:
  - opcode-jacobian-jspace.md
  - project-thesis.md
  - basis-fit-kibc-vs-ski.md
  - combinator-function-shape.md
depends-on: []
---

# Opcodes decompose across registers

> Session 264 (2026-07-19). Prompted by the idea of releasing our monitor/tracer
> as a standalone lens (complementary to Anthropic's J-Space) that shows the KIBC
> opcodes + the universal crystal lattice as a model generates tokens. Building
> the **auto-detecting, architecture-agnostic** version surfaced a real science
> result: **the nine combinator opcodes do not all live in one register.** The
> "no-ops" in the gate read are largely opcodes read in the *wrong* register.

## The `opcodes/` subsystem (new, at repo root — staged for its own MIT project)

Auto-detecting arch-agnostic opcode tracer. Same code runs on any model; nothing
architecture-specific is hard-coded (the old `opcode_monitor_v2` was pinned to
`model.model.layers[i].mlp.gate_proj`).

- **`opcodes/topology.py`** — `detect_topology(model)` → `ModelTopology`: resolves
  the layer container (`model.layers` | `model.language_model.layers` |
  `gpt_neox.layers` | ...), the **gate register** `{gated-dense | gated-fused |
  ungated | moe}`, and the **attention register** (`o_proj`/`out_proj`/`dense`,
  resolved **per-layer** for HYBRID stacks). Honest by construction: MoE is a
  *named separate register* (not silently reused); un-gated (GPT-NeoX) routes to
  the up-projection proxy `sign(dense_h_to_4h)` — the register the 10-model
  consensus actually used for Pythia. Works on the meta device (no weights).
- **`opcodes/capture.py`** — `capture_gate(model, tok, text, register={gate,attn})`
  → per-layer `[T, d]` sign-ready features via forward hooks. Feeds the validated
  `RelationalCrystalClassifier` unchanged.
- **`opcodes/trace.py`** — end-to-end detect→capture→calibrate→classify→trajectory.
- **`opcodes/register_visibility.py`** — the diagnostic below.

Verified detection: Qwen3.6-27B (**hybrid**: 3 linear-attn `linear_attn.out_proj`
+ 1 full-attn `self_attn.o_proj`, per-layer resolved), Qwen3-32B, Gemma-4-31B
(nested `language_model`), OLMo-2, Qwen3-MoE (fused experts), gpt-neox (ungated).

## The method: `register_visibility`

Held-out per-combinator visibility in a chosen register. Split the crystal probes
calib/test per combinator, calibrate the classifier on calib (natural-text null),
classify each *test* probe's last-token feature, report per combinator:
**self-accuracy** (dominant == true label), **no-op rate**, **mean best-z** (how
strongly the *true* op is seen), **top confusion**. A **shuffled-label control**
anchors chance. `λ measure` in one number: does register R even *see* opcode X?

## Findings

### 1. Capacity / superposition / scale-sharpening — CONFIRMED

Ladder (Qwen3 gate register, self-acc → best-z):

| op | 0.6B | 14B | 27B |
|----|------|-----|-----|
| WHNF/Y/S | sharp | sharper | sharp |
| K | 0.20/z1.9 | 0.30/z2.9 | 0.50/z3.6 |
| I | 0.10/z1.8 (→Y) | 0.35/z2.7 (→I) | 0.40/z2.9 (→I) |
| B | 0.00/z1.2 (→S) | 0.05/z1.7 (→S) | 0.00/z2.5 (→S) |
| C | 0.00/z1.5 (→Y) | 0.00/z1.9 (→B) | 0.11/z1.9 (→Y) |

`best_z` rises for **every** opcode with scale — small models smear opcodes into
superposition; capacity dedicates and they sharpen. This is *why we target 27B+*
(prior: `combinator_map_scale.py`, s217/s220). Sub-threshold "no-ops" are
superposition, not structure.

### 2. Identity-hold ≠ no-op — REFUTED

Hypothesis (Michael's, from the "repeat-a-token-until-output" behavior): `I` =
"hold in residual" imposes no differential routing, sits at the common-mode we
subtract, so identity reads as no-op. **Refuted:** `I` sharpens monotonically and
**self-recognizes** from 14B on (confusion flips `I→Y` → `I→I`). `I` is a normal
routing combinator, not the no-op. (The residual identity-hold seen in s263 EXP2
lives in the *value/logit-lens* register and is a separate phenomenon.)

### 3. Opcodes decompose across registers — the real result

Qwen3.6-27B, **gate** vs **attention-write** register (self-acc / best-z / →confusion):

| op | gate | attn (o_proj/out_proj) | reading |
|----|------|------------------------|---------|
| K, I | 0.50 / 0.40 | **0.60 / 0.40** | selection — sharper in attn |
| S | 0.80 → S | 0.73 → S | share — sharp in both |
| **D** | 0.33 → **S** | **0.67 → D** | **rescued by attn** (value-register opcode) |
| Y, WHNF | 0.80 / 0.80 | 0.80 / 0.87 | recursion — sharp in both |
| **B** | 0.00 → S | **0.00 → D** | **never self-recognizes** |
| **C** | 0.11 → Y | **0.17 → D** | **never self-recognizes** |

- **GATE** `sign(gate_proj)`: selection (K, I), share (S), recursion (Y, WHNF).
- **ATTN-WRITE** `sign(o_proj)`: **rescues D** (partial→sharp), sharpens K/I.
- **Composition (B, C): resolved by NEITHER scalar register.** B just migrates its
  confusion S→D; C barely moves. The "no-op" on composition tokens = an opcode
  read in the wrong register.

CAVEAT (`λ yardstick`): the **attention-write register has an elevated null floor**
— shuffled-label control gave 2 crystal layers (gate gave 0), with B's *null* z at
1.22 vs a real z of only 3.08. Sharp ops (D/Y/WHNF, z 7–9, null z ≈ 0) blow past
it; B/C sit near the leakier floor and never self-recognize. Be conservative on
weak attention-register signals.

### 4. Why B/C are elusive — refined hypothesis (untested)

`o_proj` is the attention *write* (the OV/value output = *what content moved*).
`B` (compose = nesting) and `C` (permute = argument reordering) are **position
routing** — *which position attends to which* — which is the **QK attention
pattern**, not the value written. Two scalar registers (gate, attn-write) checked;
composition needs a **pattern / position-routing** register. Converges with:
- **s250**: object-application is *distributed* (no single-component locus).
- **s263 EXP3** (`jacobian.py`): B/C structural signatures absent at last-token
  grain; grain diagnosed as too coarse for position→position routing.

## Bonus: the crystal lattice is consensus-aligned at every layer of 27B

The gate-register calibration on Qwen3.6-27B: `gc_consensus` (Gram alignment to the
universal 10-model crystal) is **positive at all 64 layers** (median 0.76, max
0.83), `sil_z` median 6.8. The universal KIBC+DWYS+WHNF lattice is present and
sharp across the whole 27B stack — strong thesis support, and a candidate
"headline panel" for the visualizer.

## Next

1. **QK-pattern register**: capture the attention pattern (or reuse
   `jacobian.py` position-attribution) and re-run `register_visibility` — the
   decisive test for whether B/C self-recognize as position-routing ops.
2. **Two-register trace/monitor**: the trajectory read must span registers (gate
   ∪ attn ∪ pattern); a single-register trajectory is blind to whole opcode
   families (the 27B gate trajectory's Y/D dominance was a visibility artifact).
3. Ladder + visualizer: the per-op sharpening curve and the `gc_consensus`-per-
   layer curve are both compelling "toy" panels.

## Files

- `opcodes/{topology,capture,trace,register_visibility}.py`
- `results/opcode-trace/`, `results/register-visibility/` (gate + attn, 0.6B/14B/27B)
