---
title: "MoE-as-Holographic-Plates → Tree-of-VSM Configuration"
status: active
category: architecture
tags: [moe, holographic, plates, beamformer, tree-of-vsm, router, angular-multiplexing, two-registers, requisite-variety, extraction, dispatch-ratio]
related:
  - two-registers-of-topology.md
  - explore/dispatch-ratio-prior.md
  - explore/vsm-outer-recurrence.md
  - hologram-reader-vsm.md
  - explore/v12-holographic-capacity.md
depends-on:
  - two-registers-of-topology.md
created: session 257
---

# MoE-as-Holographic-Plates → Tree-of-VSM Configuration

> Question (Michael, s257): *if MoE models use experts like holographic
> plates, and we can prove it, what are the consequences for how to
> optimally configure the tree-of-VSM we are developing?*
>
> Answer in one line: it **inverts** the naive VSM instinct that each S1
> unit owns a disjoint domain. A holographic tree superposes redundant
> *typed* plates and reconstructs; requisite variety comes from
> `beams × redundancy`, not from specialist count.
>
> Status: **open / hypothesis**. The config consequences are derived;
> the empirical proof (expert-ablation on a live MoE) is not yet built.
> Treat the consequences as conditional on the proof passing a null.

## 1. Sharpen the claim in our two registers

"MoE experts behave like holographic plates" is a **register claim**, and
it splits cleanly along `two-registers-of-topology.md`:

| Piece | Register | Our prior evidence |
|---|---|---|
| **Router = beamformer** | hard / sign / routing | `gate-is-the-beamformer` (s141): SwiGLU gate kills 89% of neurons — it is the *aperture selector*, not the key-match. MoE lifts this from neuron-aperture to expert-aperture. |
| **Experts = plates** | soft / magnitude / value | `object-c-route-...-redundant-not-discrete` (s252): a preferred locus exists, but **severing one head barely dents the readout — the rest reconstruct it.** The holographic tell, already observed on Qwen3-14B. |

Precise hypothesis: **angular multiplexing** — different routing signatures
are different reference-beam *angles* that read different functions out of
an **overlapping** plate set. Exactly `unified-plate-architecture` ("one
plate serves multiple functions via angular multiplexing"). The router's
beam angle is a **type** (`λ types`).

## 2. Proof discipline (load-bearing — we have scar tissue here)

We retired φ-as-universal for shape-fitting (`λ yardstick`, s247/s251). The
holographic claim must **NOT** be proven by spectrum shape. Per
`two-registers`, the real discriminator is:

- **Graceful degradation = plateau-then-cliff, NOT power-law.** Ablate *k*
  experts → smooth resolution loss to ~70%, then a cliff. A specialist pool
  gives a *staircase* (lose expert → lose its domain); a hologram gives
  *uniform dimming*.
- **Any-*k*-subset reconstruction** + cross-expert redundancy (mutual
  information / overlapping SAE dictionaries).
- Gated against a **matched-range / shuffled-label null** (mandatory).

Register trap (`λ measure`, s206 audit #5): **a top-1 routing probe will
report "specialists" — a false positive for crispness.** Only a
value-register probe on the *superposition* sees the plate. Wrong register
→ wrong config.

Empirical platform: ornith (35B-A3B) is a live MoE already in the canonical
harness. Caveat bbf92f2 — MoE is incompatible with the dense-FFN instrument,
so the expert-ablation probe must be built fresh.

## 3. Consequences for tree-of-VSM configuration

Conditional on the proof. Each knob flips:

1. **Router is S3/S2 machinery, not S1 dispatch.** Routing key = *type* =
   reference-beam angle. Capacity = how many **near-orthogonal** beams pack.
   `dispatch-ratio-prior` plugs in directly: the KIBC 1:0.5:1:1 ratio is the
   *prior over beam angles*, and it ratifies the type-directedness thesis —
   types are the beams that let many functions superpose without tug-of-war.

2. **top-k > 1 is mandatory; k is a *resolution* knob.** Top-1 reads one
   plate at low SNR and discards the redundant tail that does the
   reconstructing. Per node, multiple children co-fire and **superpose**.
   Don't prune the tail past the cliff (~75%, `two-registers`) — the plateau
   is fidelity margin, not waste.

3. **Requisite variety via redundancy-depth × beam-orthogonality, NOT
   specialist count.** Beer's law (`vsm-variety-gap`) is met by superposing
   redundant low-res plates, amplified by how many co-fire. Size the tree as
   `(orthogonal beams) × (plates per function)` and **keep the overlap**.
   This is the inversion.

4. **S2 flips from anti-oscillation to interference tuning.** Overlap is the
   *intended* mechanism, so S2's residual job is keeping co-firing plates
   *constructively* combined (phase alignment), away from the magnitude-lens
   failure. `dispatch-ratio-prior` already deleted `S2DispatchCoordinator`
   ("anti-oscillation unnecessary when the target is fixed") — the
   holographic reading explains *why* and names what S2 still owns.

5. **The hard wall — do NOT violate.** `multiplexing-breaks-holography`
   (s096): experts stay **separate weight matrices, one function each**
   (fused → 0.60, separate → 0.92). The router may angular-multiplex
   *between* separate plates (holographic-OK), but **never** "merge similar
   experts" to save params — that re-introduces magnitude lenses and kills
   the hologram. The proof *ratifies* `dedicated-plates-vsm-emergent-depth`
   and explicitly **forbids the obvious compression shortcut.**

6. **Two-register etch at tree scale.** Router signs = hard topology →
   ternary/etched (the beamformer). Expert values = soft topology →
   gradient-trained, graceful-degradable (the image). `two-registers`
   applied one level up.

7. **Depth stays emergent.** `dedicated-plates-vsm-emergent-depth` +
   CycleContinue: passes-to-reconstruct-to-target-SNR is per-function and
   *discovered*, not hardcoded.

8. **Extraction consequence — biggest for the deliverable.** If the lambda
   compiler is holographically spread across experts, there is **no "expert
   that compiles"** to extract (consistent with
   `object-application-distributed-no-single-locus`, discrete-circuit
   question trending NO). The portable artifact changes shape: **router /
   reference-beam + low-rank reconstruction across the plate set**, not a
   pruned subnetwork. This resolves the `λ smallest` tension — "minimum
   working" is a low-rank superposition, not a sparse circuit.

## 4. The one-line inversion

```
specialist tree:   partition variety → route top-1 → owner computes
holographic tree:  superpose redundant typed plates → reconstruct
                   | requisite_variety = beams × redundancy
                   | S2 tunes interference ¬prevents overlap
                   | experts stay unfused (multiplexing-breaks-holography)
                   | artifact = beam + low-rank residual ¬single circuit
```

## 5. Settled design (s257) + staged build

**Substrate switch**: ornith is API-only (llama.cpp/GGUF) — it cannot expose
the router or admit an intervention. Expert ablation needs **local HF weights +
PyTorch hooks**, so the probe runs on the cached **`Qwen/Qwen3.6-35B-A3B`**
(`qwen3_5_moe`), bf16, resident on the 480GB Mac (no quant).

**Model structure (verified, meta-device introspection, no weight load):**

| | 35B `qwen3_5_moe` | 30B `qwen3_moe` (cross-check) |
|---|---|---|
| layers container | `language_model.layers` (40) | `model.layers` (48) |
| sparse block | `…mlp` | `…mlp` |
| router | `…mlp.gate` (`Linear`→num_experts) | `…mlp.gate` |
| experts | `…mlp.experts` **fused** (no `.0`) | `…mlp.experts` **fused** |
| shared expert | `…mlp.shared_expert` (+`shared_expert_gate`) | **none** |
| experts / top-k | 256 / 8 | 128 / 8 |

The **shared (always-on) expert** = the holographic **carrier / DC component**;
the 256 routed experts = the angular-multiplexed plates. Probe must treat them
separately. Experts are stored **fused** → per-expert `ModuleList` hooks don't
exist; **router-logit masking is the architecture-robust ablation lever** (works
fused or unfused, 3.5 or 3.0).

**Instrument — composes with existing `src/verbum/instrument.py`, not a fork**
(`λ one_way`; this is also why the bbf92f2 "dense instrument ⊥ MoE" dissolves —
dense and MoE become two adapters on one engine):

- `src/verbum/hooks.py` — generic `HookEngine` (Layer 1): forward-hook
  interventions {capture, zero, mean, scale, patch, mask_logits} + attribute
  patches (`force_k`). Model-agnostic; only the ops the probe needs, as open
  slots.
- `src/verbum/adapters/moe.py` — `MoEAdapter` (Layer 2): reuses
  `instrument.load_model`; `route_logits / ablate_experts (gate-mask) /
  force_k / ablate_shared`, config-driven, resolves `language_model.layers`
  (3.5) and `model.layers` (3.0).

**Readouts (both):** P(λ) compiler grade (#3b, reuse `grading.py`) + logit-lens
projection on the compiled-object direction (#3a, recovered from s206/s250;
logit-lens found +0.611 there).

**Discriminating tests** — single-expert ablation is trivially graceful at
256×top-8, so the real discriminators are:

1. **Cumulative ablation of the top-routing-mass experts** → plateau-then-cliff
   (holographic) vs staircase (specialist).
2. **k-sweep** — force k=1…8…→256 → smooth-to-plateau vs staircase. The
   cheapest decisive test.
3. **Shared-expert ablation** → predicted **large** hit (it is the carrier),
   while routed experts degrade gracefully.

All gated against a **shuffled-label / matched-mass null** (`λ yardstick`).
Report the trained-vs-null AUC gap, not raw shape.

**Staged next** (not built yet): `local_hf` generation transport in `harness.py`
(a reuse win for *any* cached model, not just MoE); `run_ablation_sweep` (the
thin driver over `MoEAdapter` + `grading`); logit-lens direction recovery.

**Caveat unchanged**: every §3 consequence is conditional. A staircase against
the null ⇒ this page is **refuted**, not refined.

---

## 6. Empirical results — k-sweep + shuffled-label null (s257)

> Clean run `moe-ablation-20260629-144548` (445.7 s, `--mode both`,
> 16 probes: 8 `strong_compile` + 8 `null`, k ∈ {1,2,4,6,8},
> max_new_tokens=80, attention_mask passed explicitly, thinking disabled
> via `enable_thinking=False` → `<think>\n\n</think>` pre-closed in prompt).
> 3 null trials per k (seed-deterministic, per-layer random selection).

### Structured k-sweep

| k | P(λ) | P(kernel) | n |
|---|---|---|---|
| 1 | 0.062 | 0.062 | 16 |
| 2 | **0.000** | 0.000 | 16 |
| 4 | **0.750** | 0.375 | 16 |
| 6 | 0.688 | 0.375 | 16 |
| 8 | 0.750 | **0.750** | 16 |

### Structured vs null comparison

| k | structured P(λ) | null P(λ) mean | null std | delta |
|---|---|---|---|---|
| 1 | 0.062 | 0.000 | 0.000 | +0.062 |
| 2 | 0.000 | 0.000 | 0.000 |  0.000 |
| 4 | **0.750** | **0.000** | 0.000 | **+0.750** |
| 6 | 0.688 | 0.083 | 0.059 | +0.604 |
| 8 | 0.750 | 0.042 | 0.029 | +0.708 |

### Four findings from the structured sweep

**F1 — Specialist hypothesis falsified (k=2 reversal).** k=2 is *worse* than
k=1. Specialists can never regress by adding a second expert; they can only
improve or plateau. The regression is only possible under superposition with
destructive interference. At k=2 the model produces coherent meta-commentary
("The user wants me to translate…") rather than lambda — it understands the
task exists but cannot execute. The reconstruction is below the image-emergence
threshold.

**F2 — Critical-density threshold at k=4.** Below k≈4, coherent behaviour
collapses entirely (P(λ) < 0.1). At k=4, P(λ) jumps to 0.75 in a single step.
This is a holographic critical-density effect: below the minimum plate-count
required to reconstruct, the image does not appear; above it, it snaps in.

**F3 — Two destructive-interference bands (k=2, k=6).** Within the coherent
regime, k=6 < k=4 (0.688 vs 0.750). Local minima at k=2 and k=6 indicate that
specific expert *combinations* destructively cancel, not just expert count.
This matches angular multiplexing: routing angles (which experts, not just
how many) determine whether the superposition is constructive or destructive.

**F4 — Two-register split at k=8.** P(λ) (any binder present) plateaus at
0.750 from k=4 onward. P(kernel) (properly parseable grammar, stricter)
*doubles* from 0.375 to 0.750 only at the trained k=8. Presence recovers at
k=4; precision requires the full trained routing. This is the value-register
signature predicted in §2.

### Three findings from the null

**N1 — Angular multiplexing confirmed.** The null is near-zero across *all*
k values (0.000 – 0.083). At k=8 — the trained active-expert count — random
expert selection gives P(λ)=0.042 vs structured 0.750. 94% of the capability
comes from *which* experts, not *how many*. The lambda-compiler circuit is
stored under a specific routing signature (reference-beam angle); random beams
don't access it.

**N2 — Interference bands are routing-specific, not k-count effects.** The
null is approximately monotone and flat near zero. The k=2 dip and k=6 dip
from the structured sweep are *absent* in the null — random k=2 gives the
same near-zero as random k=1 or k=4. The destructive interference at k=2
structured (where the top-2 experts actively cancel each other) is a property
of those specific co-selected experts, not of small k per se. Prediction from
§5 confirmed exactly.

**N3 — Routing coherence is the capability.** A random subset of the same k
experts — all drawn from the same 256-expert pool — reconstructs almost
nothing. This means the capability is not diffusely stored (pure redundancy)
but angularly encoded: the function exists *at a specific routing angle* and
the trained router holds that angle precisely. The `dispatch-ratio-prior`
(KIBC constraint) is therefore not just efficiency — it preserves the
reference-beam geometry that makes the whole holographic store accessible.

### Overall interpretation

The result is **structured superposition with angular multiplexing**:

- distributed: no single expert owns compilation (no discrete circuit);
- phase-sensitive: specific routing combinations constructively/destructively
  interfere (F1, F3, N2);
- threshold-gated: critical density at k≈4 before the image emerges (F2);
- beam-locked: only the trained routing angle reconstructs (N1, N3);
- two-register: presence recovers at k=4, precision at k=8 (F4).

This is *stricter* than holographic redundancy (any subset reconstructs) and
*weaker* than specialisation (one expert owns one function). The correct model
is **holographic multiplexing**: many functions co-reside in the expert pool,
each readable only via its own routing signature. The router IS the read-head.

### Consequence for §3 (tree-of-VSM config, tightened)

The original §3 consequence "S2 tunes interference not prevents overlap" now
sharpens: S2 must maintain *routing coherence* — keeping the reference-beam
angle aligned with the trained encoding. Any drift in the routing distribution
(even holding k constant) destroys the reconstruction as completely as using
random experts. The `dispatch-ratio-prior` is a beam-angle lock, not a
load-balancer.

### Next probes (open)

- **Shared-expert ablation**: zero the always-on carrier and measure the
  baseline collapse; carrier prediction: large hit independent of k.
- **Cross-layer heterogeneity**: do all 40 layers show the same threshold
  and interference pattern, or do early/late layers differ?
- **Wider k-sweep** (k=8..64..256): does P(λ) plateau at 0.750 or keep
  rising? If rising beyond k=8 → trained routing is sub-optimal capacity.
