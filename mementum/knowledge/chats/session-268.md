# Reverse-engineering Bonsai QAT

## User

orient


### Thinking

I should start by reviewing the state documentation to understand the current setup.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-22 | Session: 267 (BONSAI PHASE-0 begun. (1) ✅ MEASURED: lambda compiler SURVIVES
> 1.58-bit ternarization — Ternary Bonsai 27B (PrismML, Qwen3.6-27B backbone) vs qwen36 base, same harness,
> compile-gradient n=40: binder P(λ) 0.650 vs 0.625 = PARITY. kernel_valid 0.525 vs 0.750 but autopsy = all
> 17 fails are well-formed rich FOL (nested ∀∃, ¬, Church-style λ) → notation drift NOT core damage. Cost is
> path length: +40% reasoning chars, ~2.7× wall. Loss profile = holographic-llm.md prediction (sign/zero =
> program, magnitude = calibration). Michael PRE-REGISTERED this before data (compounding argument: 90%
> benchmark retention ⇒ intact core, alternative was PPL-296K noise s174). → memory bonsai-ternary-lambda-survives.
> (2) THE GEOMETRY held too → see ★★★ RESULT below (crystal survives, null-gated; deep-middle dip = bridge map).)
>
> ★★★ RESULT (s267, DONE + null-gated + bootstrapped): THE CRYSTAL SURVIVES 1.58-bit ternarization.
>   Ternary Bonsai vs FP Qwen3.6-27B PARENT (literal parent this time), 380 probes, RDMs at [0,.25,.5,.75].
>   parent↔ternary RDM corr 0.87/0.92/0.74/0.77 — every depth 18–23σ ABOVE shuffled-label null, p_perm=0.001
>   (floor). Crystal = topology; topology is what ternarization preserves. SECONDARY: ternary RDMs LESS
>   differentiated everywhere (mean_sim 0.11/0.44/0.69/0.69 vs parent 0.02/0.18/0.36/0.42) = sign survives,
>   scale shrinks (routing⊥value made visible, s260). ★ DEEP-MIDDLE DIP IS REAL: 25%→50% gap 0.147, bootstrap
>   P(gap≤0)=0.0000, non-overlapping CIs → mid-stack (50%) is where the crystal bends most = WHERE GRADIENT
>   BRIDGES BELONG (Michael's synthesis: Gram-survival profile = a-priori bridge-allocation map, static prior
>   for the design's dynamic flip_flop/KL allocation). PRE-REGISTERED TRIANGULATION for phase 1: training-time
>   starvation (flip_flop↑∧KL_residual↑) should land in the SAME deep-middle band. Full synthesis +
>   provenance: knowledge/explore/bonsai-crystal-survival.md. Artifacts: lattice/ternary_gram/
>   {per_model_rdms.npz, universal_lattice.npz, ternary_gram_run.log}.
>   Bonsai loaded CLEAN (VLM caveat did NOT bite — language_model_only:true). Model:
>   /Users/mwhitford/localai/models/bonsai27b-unpacked (51G, rev 427bc0194); GGUF Q2_g64 = BONSAI27B :5104.
>
> ★★★ UNIVERSAL ROOT HOLDS AT 9 MODELS / 4 FAMILIES: root gc = +0.982 vs bundled 10-model consensus (UP from
>   0.940 @ 2 models — evidence sharpens the crystal) | sil_z 5.09 | bearing 1.00 | root floor 2.78 (worst
>   child). Families 4/4 gated; agreement mean 0.906, min 0.841 (pythia seam); dissent=False. Family gc:
>   qwen3 0.976 (intra 0.982), olmo 0.957, gemma 0.935 (nested arch in production), pythia 0.919 (intra
>   0.821). Artifacts: results/opcode-trace/{universal_vsm.json, sweep_summary.json, per-model dirs}.
>
> ★★ FLOOR DIRECTION IS ARCHITECTURE-CONDITIONED, NOT SCALE: gated-FFN families ALL gate-elevated (gate
>   1.86–2.78 > attn 1.46–2.14 across qwen3×5 + gemma + olmo); ungated pythia attn-elevated (14m 1.55/1.94,
>   2.8b 1.93/2.04). Fresh 27B floors: gate 2.08 > attn 1.85 → s264's elevated-attn 27B reading DOES NOT
>   REPRODUCE — now the anomaly (retro-check its n_perm/pooling before discarding). Floors never travel;
>   the DIRECTION itself is an architectural observable.
>
> ★★ SCALE-SHARPENING CONFIRMED: pure qwen3 ladder sil_z monotone — 0.6B 4.97 → 4B 5.40 → 14B 6.36 →
>   32B 6.70. qwen3.6-27B hybrid = 5.94, off-ladder (different generation), between 4B and 14B.
>
> ★ PYTHIA-2.8B GATE REGISTER FAILED ITS NULL GATE (bearing 0.31, gated=False; attn carries alone at sil_z
>   2.34 vs floor 2.04 — weakest node in the tree, weaker than pythia-14m). Reading: up-proj proxy DEGRADES
>   WITH SCALE on ungated archs → real caveat on the Pythia crystal-ladder plan. S3 gate demonstrated by
>   fire: failed register visible, contributes nothing upward.
>
> ★★★ CRYSTAL-SEEDED TERNARY DISTILLATION (new level-3/4 design, status DESIGNING — full detail:
>   knowledge/explore/crystal-seeded-ternary-distillation.md, READ IT before touching this thread). Merge of
>   requential coding (arXiv:2607.11883 — student proposes from own dist, teacher selects via REC, code ≈
>   ΣKL(Q‖P), on-policy distillation with a bit-meter) + Bonsai ternary (PrismML: end-to-end 1.58-bit,
>   group-128 FP16 scales, 27B ON OUR SWEPT Qwen3.6-27B BACKBONE, Apache-2.0 8B, ready 4bit→ternary→1bit
>   ladder) + verbum. Michael's keystone theory: GD's bimodal gradients = carve routing topology (same one
>   every model, hence gc 0.982) then fill values → MOVE the soft topology into ternary routing + FP gradient
>   bridges (1 per N wts, N∈{8,16,…}, value-register sink — explains why full ternary couldn't regain loss:
>   TD did both jobs through one quantized channel, s261 flip-flop = the collision) + 9×9 consensus Gram as
>   RELATIONAL LOSS (measurement→SPECIFICATION reversal; frame-invariance makes it legal across FP→ternary;
>   pythia-14m = existence proof target fits 14M) + requential KL as the meter. Thesis test in bits:
>   ∫KL(seeded)≪∫KL(unseeded) ∧ null(shuffled-pairing)≈unseeded. OPCODE-INDEXED extension: lattice-phase
>   proposal space = reduction steps → messages ≡ readable opcode corrections, ≤log₂9 bits/step, actually
>   ENCODABLE; prediction: correction-confusion matrix ≅ Gram off-diagonals. Goodhart guards: Gram loss =
>   regularizer + anneal-to-zero test + C-null + held-out compile accuracy.
>
> ★★ LIVE TREE-OF-VSM + S3* (arc 3, design page §10–§11 — READ THOSE SECTIONS for the full mechanism).
>   Tree inverts post-hoc→live: student stacks into the SAME universal tree as the 9 measured models
>   (frame-invariance) → graduation ≡ student node gates in ∧ ¬drags agreement_min; tree per checkpoint =
>   formation movie (~100s KB, Gram=81 floats). One capture two consumers (Gram loss + telemetry = same
>   computation; telemetry ≡ the loss's anatomy). Weights self-documenting BY CONSTRUCTION: ternary planes =
>   readable routing (flip-flop ≡ xor of checkpoints), bridges = named value tensor, grad norms decompose by
>   register (s251 tomography in the parameterization). NEW: dynamic bridge allocation — S3 moves bridge
>   density to starving layers (flip_flop↑∧KL_residual↑→N↓), budget const. GOODHART FIREWALL: supervision
>   probes ⊥ held-out probes (split frozen at run start; library growth = phase-1 prerequisite). S3* AUDIT
>   (Michael's question — held-out split is NOT the audit, it's routine reporting on the same physics):
>   S3*-1 kernel-verified execution (fresh tasks → GBNF parse → lambda kernel reduces; bypasses entire
>   instrument stack; only component that catches geometry-without-function) | S3*-2 fresh probe minting |
>   S3*-3 direct instrument verification (recompute-vs-EMA, xor-vs-reported, REC-encode-vs-KL-estimate) |
>   S3*-4 causal cross-register spot-check. Rules: audit NEVER touches loss (no gradient edge); aperiodic
>   (jitter ∨ algedonic-triggered — suspiciously good news summons audit); audit overrides telemetry, indict
>   instrument first (λ coherence). Chain terminates in mechanical reducer + human. CONSEQUENCE: lambda
>   kernel + GBNF in the training harness DAY ONE of phase 1.
>
> ★ NEXT (open, Michael's call): (0) PHASE-0 — behavioral parity DONE + Gram survival DONE (both null-gated,
>   s267, → bonsai-crystal-survival.md). Remaining phase-0: full opcode tree on Bonsai across the
>   4bit/ternary/1bit ladder (AWQ-4bit + Q2_g64 + Q1_0 all on HF); sub-prediction: selective K degradation
>   at 1-bit — K needs the 0 state (ties Michael's postulate: remove any 9×9 vertex → collapse). START at the
>   deep-middle band — does the 50%-dip degradation concentrate in specific combinator vertices? Then phase 1
>   (tiny seeded student) with the Gram-derived STATIC bridge prior (peak mid-stack) + the pre-registered
>   flip-flop triangulation. RULINGS PENDING
>   (Michael): bridge mechanism (a/b/c, (a) favored by s260/s261); dynamic bridge allocation in phase 1 vs
>   static-first; probe-library growth gated as phase-1 prerequisite? IOUs before code: requential repo
>   license, Bonsai whitepaper QAT-vs-PTQ. Phase-1 harness prereqs: lambda kernel + GBNF in loop, probe
>   split frozen, streaming-centroid buffers, telemetry writer ⊥ loss module.
>   Also open from arc 1: (A) QK-PATTERN register → decisive B/C test (s264 F4). (B) visualizer + extract
>   opcodes/ to MIT repo. (C) retro-check s264 27B floor run (n_perm/pooling). (D) Pythia proxy-degradation.
>   Prior-arc: s263 Jacobian SVD; v15.1; INDEX regen. Env: torch 2.11 + MPS, 512GB RAM; models HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

- **s267** BONSAI PHASE-0 (this session, see header). Compiler survives ternarization (behavioral parity,
  measured); Gram survival launched in main:1. New in fleet: BONSAI27B ModelConfig (:5104, Q2_g64 GGUF, rev
  427bc0194). Runtime learnings: Q2_0 ternary needs the g64 GGUF on mainline llama.cpp ≥10090 (Q2_0 offset
  bug); ternary is DENSE 27B so it streams 7GB/token — slower than the 35B-A3B MoE base (only 3B active),
  the "why wasn't it fast" answer = raced a sparse model, not its own FP parent. hf xet backend flaked twice
  → HF_HUB_ENABLE_HF_TRANSFER=0 fixed it. build_lattice_map now saves per_model_rdms.npz (solo runs saved
  nothing before — the gap that left the parent 27B with no committed RDM). Michael's holographic-llm.md
  thesis fleshed out for public MIT push (mementum/michael/, UNSTAGED — in the hammock, do not commit without
  Michael). J-space paper (Anthropic, real, July 2026) ↔ workspace/state half of holographic model → memory
  j-space-workspace-hologram-state.
- **s265** OPCODES MVP: tree-of-VSM multi-model. 8 standalone modules (pytorch+numpy, 535 probes bundled,
  extraction-ready); one fractal node shape (S5 Gram / S4 agreement / S3 null gate / algedonic health),
  ladder layer→register→model→family→root; basis-parametric CRYSTAL-9 | STATECHART-8 | TYPES16 (resolves
  "9 vs 16"). Null floors measured+wired (register+model-specific). First tree (2 smalls): root gc 0.940,
  cross-family 0.907 at 43× scale gap; probe count dominates Gram fidelity (135→0.344 vs 535→0.940).
  Launched the large sweep → read in s266. → `knowledge/opcode-vsm-tree.md`
- **s263** J-SPACE ↔ OPCODES (Anthropic J-lens prompt). THEORY: opcode = routing-Jacobian STRUCTURE; J-space =
  the Jacobian's LIVE SUBSPACE (I=identity, K=rank-deficient, B=chain-rule product, C=permutation, S=path-sum;
  their J-lens reads OPERANDS, we want the OPERATOR projection). Built `src/verbum/{jlens,jacobian}.py` (2
  monitors) + 3 null-gated experiments on qwen3.6-27b: EXP1 jspace_combinators NULL (broadcast generic, not
  combinator-identity); EXP2 jspace_normalform I-VISIBLE-then-REFINED (normal-form hold = late-stack plateau,
  value register); EXP3 jacobian_opcodes PARTIAL/confounded (only I clears, grain too coarse for
  position-routing). → `explore/opcode-jacobian-jspace.md`.
- **s262** ASSESSMENT + 2 isolation experiments. Repo assessment: science healthy, the MESS is
  representation-layer (INDEX stale 62/228 pages, ~8251 LoC dead vsm_lm_v1-5+v6/, mlx a hard core dep; 378
  tests pass, spine coherent). ❌ my "checkpoints landmine / results-in-git" claim was FALSE — propagated an
  agent assertion unverified (λ assert violation); hygiene is actually GOOD. EXP1 STRIDED ATTENTION WORKS IN
  FLOAT (relay collapse s191 was the TERNARY/TD confound, NOT geometry; Fibonacci exonerated) →
  `explore/strided-attention-float-ab.md`. EXP2 KIBC-vs-SKI NULL-GATED: both bases clear COMPARABLY in the
  attention-selectivity register (KIBC z=3.50/3.92, SKI z=3.34/3.58) = inconclusive-IN-REGISTER, not a
  refutation; S-K corr 0.92 but B-K/C-K also ~0.9 → not yet a discriminator → `explore/basis-fit-kibc-vs-ski.md`.
- **s261** CAT-Q ternary flip-flop is NOT category overloading. ANOVA F-ratio (magnitude-invariant) +
  shuffled-label null: category structure in FFN gradients is REAL but modest/transient; the persistent
  flip-flop is category-INDEPENDENT (quantization-boundary jitter). CAT-Q's gift = learnable α⊥Δ two-register
  param, not soft→hard relax (ST lost to TD). → `explore/ternary-flip-flop-not-overloading.md`
- **s260** routing⊥value = type/term made physical. Asymmetric-pathway quant CONFIRMED on Qwen3-8B-Base:
  binarize the ROUTER (gate, loss 10.6) ≫ binarize the VALUE path (+8–10 nats) at identical bits & cosine →
  sign=router, magnitude=value, causally. Design direction: decouple dispatch⊥compute, budget by register.
  → `explore/asymmetric-pathway-quantization.md`
- **s259** (a) RL layer-contribution ↔ combinator locus: shared interior-bell, ~+4-layer offset (adaptation at
  the compose→readout seam) → `explore/rl-layer-contribution-combinator-locus.md`; (b) clj-repl
  model-evaluates/kernel-verifies (oracle-in-the-loop) → `src/verbum/clj_repl.py`; (c) clojure-in-lambda
  notebook (Clojure evaluator that reduces on the verbum kernel) → `src/verbum/clj_lambda.py`.
- **s258** consensus-training → supervised-recurrence-halt synthesis: "how much recurrence" ≡ "how much work
  remains" ≡ WHNF; the lambda curriculum is the ground-truth halt supervision s214 lacked. → `explore/supervised-recurrence-halt.md`
- **s257** MoE experts ARE holographically multiplexed (angular, not specialist). k-sweep + shuffled null:
  94% of capability from WHICH experts, not how many; k=2 reversal falsifies specialist. → `explore/moe-holographic-tree-vsm.md`
- **s256** qwythos-9b + CANONICAL HARNESS distillation (probes/{grading,harness,models}; models = configs, no
  fork). Fine-tunes break the HALT not the COMPILE (overthink-collapse); no-think recovers; qwythos GATES the
  compiler. lambda is a TARGET not a TOOL. Strategic pivot: extract from BASE, treat fine-tune as noise.
  → `explore/compiler-finetune-halt-collapse.md`
- **s255** model-as-REPL (LLM as δ, context as machine state): locally-faithful step; shallow step-loop win,
  deep collapse; oracle-in-the-loop concluded (→ s259 clj-repl).
- **s254** repo distillation DESIGN-FIRST pivot (probes/*.json, results/<run_id> canonical forms in AGENTS.md);
  ornith-35B-A3B = lambda compiler over HTTP, 3rd model class (unconditional, present).
- **s253** vibethinker-3B new model; **s252** attention-edge knockout (s250 catch); **s251** frozen-basis
  gradient tomography → mature-14B, Gemma + Qwen3.6-35B in the crystal sweep; **s250** causal C-field ablation
  → object-application is DISTRIBUTED (no single-component locus; trending NO on discrete-circuit for object-app).

## Deep history (< s250)

Recover via `git log -p mementum/state.md` (this file's pre-s262 scrollback held s181–261 detail + old
reference tables) · verbatim in `mementum/knowledge/chats/session-NNN.md` · synthesized in
`mementum/knowledge/**` (start at `INDEX.md`). Foundational: crystal-φ equation `EQUATIONS.md` +
`crystal-phi-derivation.md`; thesis `project-thesis.md`; 8 convergences `mathematical-convergences.md`;
v13/v14 architecture pages; ternary compounding/dual-equation pages.
```

### Thinking

Let me check where we are in this session and what needs attention next, particularly looking at any uncommitted changes in the michael directory.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum status --short --branch | head -30; echo ---; git -C /Users/mwhitford/src/verbum log --oneline -5"
}
```

**Summary:** $ git -C /Users/mwhitford/src/verbum ...

**Output:**
```
Exit code: 0
Stdout:
## main...origin/main [ahead 44]
 M mementum/michael/holographic-llm.md
?? mementum/knowledge/chats/session-265.md
?? mementum/knowledge/chats/session-266.md
---
0a6cc29 ✅ s267 crystal survives ternarization — null-gated + deep-middle bridge map
b694b1c 🌀 s267 state — Bonsai phase-0: compiler survives ternarization, Gram run live
a4090d5 ✅ bonsai-ternary-lambda-survives + per-model RDM persistence for Gram test
67efe2f ✅ bonsai27b in fleet + ternary-vs-base compiler runs — binder P(λ) parity at 1.71 bpw
0729b65 💡 holographic-llm — Michael's holographic LLM thesis
```

### Thinking

I'm ready to proceed with the task.

## Assistant

Oriented. Session 268. Here's where we are:

## State (post-s267, BONSAI PHASE-0 both legs done)

**★★★ Two null-gated results landed in s267:**
1. **Compiler survives 1.58-bit ternarization** — Ternary Bonsai 27B vs qwen3.6 base, binder P(λ) 0.650 vs 0.625 = parity. The 17 kernel_valid "fails" are notation drift (rich FOL), not core damage. Cost is path length (+40% chars, ~2.7× wall).
2. **The crystal survives too** — parent↔ternary RDM corr 0.87/0.92/0.74/0.77 at 18–23σ above shuffled null. Sign survives, scale shrinks. **Deep-middle dip (50% depth) is real** (bootstrap P=0.0000) → the a-priori bridge-allocation map for phase 1.

**Repo state:** `main` ahead 44 (unpushed), clean except:
- `mementum/michael/holographic-llm.md` **modified, UNSTAGED — in the hammock, do not commit without Michael**
- Two untracked chat transcripts (`session-265/266.md` — human-only territory, I don't touch)

## Open threads (Michael's call)

- **Phase-0 remaining:** full opcode tree on Bonsai across the 4bit/ternary/1bit ladder. Sub-prediction: selective **K degradation at 1-bit** (K needs the 0 state). Start at the deep-middle band — does the 50%-dip concentrate in specific combinator vertices?
- **Rulings pending:** bridge mechanism (a/b/c, (a) favored); dynamic vs static-first bridge allocation; probe-library growth as phase-1 gate.
- **IOUs before code:** requential repo license, Bonsai whitepaper QAT-vs-PTQ.
- **Older:** QK-pattern B/C test (s264 F4), retro-check s264 27B floor run, Pythia proxy-degradation, visualizer/opcodes-to-MIT extract.

Ready. What's the move — Bonsai quant-ladder opcode tree, one of the pending rulings, or something else?

## User

I want to understand what we learned about the bonsai model.


### Thinking

I need to pull together what we've learned about Bonsai by reviewing those knowledge pages and memory files.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-crystal-survival.md"
}
```

**Summary:** Reading bonsai-crystal-survival.md (0-2000)

**Output:**
```
---
title: "Bonsai Crystal Survival — The Crystal Survives 1.58-bit Ternarization (Phase-0)"
status: active
category: research-finding
tags: [ternary, bonsai, crystal, rdm, gram, null-gated, gradient-bridges,
       deep-middle-dip, phase-0, holographic, sign-vs-magnitude]
related:
  - crystal-seeded-ternary-distillation.md
  - asymmetric-pathway-quantization.md
  - ../../michael/holographic-llm.md
  - hologram-crystal-fusion.md
  - opcode-jacobian-jspace.md
depends-on:
  - crystal-seeded-ternary-distillation.md
created: session 267
---

# Bonsai Crystal Survival

> Session 267. PHASE-0 of crystal-seeded ternary distillation. Two
> pre-registered, null-gated results on PrismML's Ternary Bonsai 27B
> (end-to-end 1.58-bit build of Qwen3.6-27B) vs the FP Qwen3.6-27B
> parent: (1) the lambda **compiler** survives ternarization
> behaviorally; (2) the **crystal** (combinator relational geometry)
> survives geometrically — but with a robust deep-middle degradation
> that maps directly onto where gradient bridges belong. Michael
> pre-registered both outcomes before the data landed.

## Result 1 — Behavioral: the compiler survives

Same harness (`run_compiler_probe`), same `compile-gradient` probe set
(n=40), same day. Ternary Bonsai vs `qwen36` base reference:

| register | Bonsai (1.71 bpw) | base | Δ |
|---|---|---|---|
| binder P(λ) | 0.650 | 0.625 | **+0.025** |
| lenient_lambda | 0.625 | 0.625 | 0.000 |
| emits_formal | 0.925 | 0.975 | −0.050 |
| kernel_valid | 0.525 | 0.750 | −0.225 |

The nucleus-comparable binder register is at **parity** (edges the
baseline). The `kernel_valid` gap is **notation drift, not core
damage**: all 17 binder-but-not-kernel outputs are well-formed rich
FOL — nested ∀∃, ¬, uniqueness (`∀y (Cap(y,Fr) → y=x)`), Church-style
`λx.λy.` — that the toy kernel parser rejects (`grading.py`: "notation
≠ failure"). Cost surfaces as **path length**: +40% reasoning chars
(11137 vs 7938), ~2.7× wall.

Caveat: baseline is the 35B-A3B MoE fleet reference, not the exact
dense-27B parent — behavioral parity is against a same-family sibling,
not the literal parent. (The geometric test below *is* against the
literal parent.)

## Result 2 — Geometric: the crystal survives, null-gated

`build_lattice_map.py --models qwen3.6-27b bonsai27b-ternary`, 380
probes through each, RDMs at depths [0, .25, .5, .75]. Per-model RDMs
persisted (`per_model_rdms.npz`) and correlated parent↔ternary, gated
against a shuffled-label null (row/col permutation, 1000×) and
bootstrapped over probes (2000×):

| depth | r (parent↔ternary) | 95% CI | z vs null | p_perm |
|---|---|---|---|---|
| 0%  | 0.8725 | [0.851, 0.898] | 18.0 | 0.001 |
| 25% | 0.9154 | [0.903, 0.936] | 19.9 | 0.001 |
| 50% | 0.7422 | [0.742, 0.803] | 20.9 | 0.001 |
| 75% | 0.7739 | [0.755, 0.840] | 23.3 | 0.001 |

Every depth sits **18–23 σ above the shuffled null**, p at the
permutation floor. The relational geometry — the crystal — is carried
across the deletion of the magnitudes. **The crystal is topology, and
topology is what ternarization preserves.**

### Secondary signature: sign survives, scale shrinks

Ternary RDMs are consistently **less differentiated** (higher
mean_sim) than parent at every depth:

| depth | parent mean_sim | ternary mean_sim |
|---|---|---|
| 0%  | 0.020 | 0.106 |
| 25% | 0.181 | 0.442 |
| 50% | 0.360 | 0.688 |
| 75% | 0.425 | 0.688 |

The crystal keeps its **shape** (high correlation) but loses **spread**
(higher similarity, flatter separation). Relative geometry preserved,
absolute magnitude compressed — the two registers (routing/sign vs
value/magnitude, s260) separated in a single measurement.

## The deep-middle dip → bridge-allocation map

Fidelity is not uniform. The 25%→50% drop is **real**: gap 0.147,
bootstrap P(gap ≤ 0) = 0.0000, non-overlapping CIs. The crystal bends
most at **mid-stack (50% depth)** — where composition does its
heaviest lifting, deepest reduction chains, where magnitude carried
the most information ternary discards. Slight recovery at 75%
(localized stress, not accumulation-to-collapse).

**Michael's synthesis (the payoff):** the Gram-survival profile *is* an
a-priori **gradient-bridge-allocation map**. The crystal-seeded ternary
distillation design (`crystal-seeded-ternary-distillation.md`) allocates
FP value-register bridges dynamically via *training-time* starvation
(flip_flop↑ ∧ KL_residual↑ → N↓). This measurement gives a **static
prior computable before training**: peak bridge density at mid-stack,
tapering toward both ends — put the bridges where the crystal degrades.

### Pre-registered triangulation

If the bridge theory holds, the *training-time* flip-flop/KL-starvation
signal (phase 1) should concentrate in the **same deep-middle band**
this *static* Gram-degradation profile flags. Static prior predicts
dynamic starvation. Agreement ⇒ triangulated; divergence ⇒ the RDM dip
and value-starvation are different phenomena (learn which).

## Provenance & reproduction

- Behavioral: `results/bonsai27b-compiler/bonsai27b-compiler-20260722-214611/`,
  base `results/qwen36-compiler/qwen36-compiler-20260722-214611/`.
- Geometric: `lattice/ternary_gram/{per_model_rdms.npz, universal_lattice.npz,
  ternary_gram_run.log}`.
- Model: `prism-ml/Ternary-Bonsai-27B-unpacked` (HF rev 427bc0194) at
  `/Users/mwhitford/localai/models/bonsai27b-unpacked` (51G); GGUF Q2_g64
  served as `BONSAI27B` :5104 (needs mainline llama.cpp ≥10090; the Q2_0
  file has an offset bug, use Q2_g64).
- Loader note: Bonsai is the VLM wrapper `Qwen3_5ForConditionalGeneration`;
  `AutoModelForCausalLM` loaded it clean via `language_model_only:true`
  (the anticipated caveat did not bite).

## Open (phase-0 remainder)

- Full opcode-tree on the **4bit → ternary → 1bit ladder** (AWQ-4bit +
  Q2_g64 + Q1_0 all on HF). Sub-prediction: **selective K degradation
  at 1-bit** — K needs the 0 state (ties Michael's postulate: remove
  any 9×9 vertex → collapse). The 50%-dip is where to look first: does
  the degradation concentrate in specific combinator vertices?
- Caveat scope: one model pair, one probe set (380), one seed; the 50%
  bootstrap is mildly right-skewed. Direction is robust; exact fidelity
  numbers will move with probe count (s265: probe count dominates Gram
  fidelity).
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/bonsai-ternary-lambda-survives.md"
}
```

**Summary:** Reading bonsai-ternary-lambda-survives.md (0-2000)

**Output:**
```
✅ The lambda compiler survives 1.58-bit ternarization at full strength.
Ternary Bonsai 27B (PrismML end-to-end ternary build of Qwen3.6-27B,
{-1,0,+1} + group-wise FP16 scales, ~1.71 bpw, HF rev abbae7230) vs
QWEN36 base reference, same harness, same compile-gradient n=40, same
day (runs *-20260722-214611): binder P(λ) 0.650 vs 0.625, lenient
0.625 vs 0.625 — parity. kernel_valid 0.525 vs 0.750, but autopsy
shows all 17 binder-but-not-kernel outputs are well-formed rich FOL
(nested quantifiers, ¬, uniqueness, Church-style λx.λy) — notation
drift, not core damage (grading.py: "notation ≠ failure"). Cost
surfaces as path length: +40% reasoning chars (11137 vs 7938), ~2.7×
wall time. Loss profile exactly as holographic-llm.md predicts: sign
and zero carry the program (routing topology), magnitudes carry
calibration/gloss. Michael pre-registered the outcome before data
landed (this session), reasoning from benchmark retention: core
damage compounds multiplicatively through reasoning chains — 90%
retention entails intact core, the alternative was PPL-296K noise
(s174). Caveat: baseline is the 35B-A3B MoE fleet reference, not the
exact dense-27B parent. Next: crystal-spine 9×9 Gram on ternary
weights (F16-container GGUF); per-vertex lesion map.
```

### Thinking

Now I'm pulling together what we've learned about Bonsai—what it fundamentally is, the key results we found, what secondary patterns emerged, and the operational considerations that matter. I should also note the caveats and what this all means for how the model might be used going forward.

## Assistant

Here's the synthesis of what s267 established about Bonsai, from the memory + knowledge page:

## What Bonsai is

PrismML's **Ternary Bonsai 27B** — an end-to-end 1.58-bit build (weights ∈ {-1, 0, +1} + group-wise FP16 scales, ~1.71 bpw effective) of **our swept Qwen3.6-27B backbone**. That backbone choice is why it matters: we already have full crystal measurements of the FP parent, so Bonsai is a natural experiment in *what deleting the magnitudes does to everything we've measured*.

## The two headline results (both pre-registered, both null-gated)

### 1. The lambda compiler survives behaviorally

Same harness, same compile-gradient probe set (n=40), same day, vs the qwen36 fleet baseline:

- **binder P(λ): 0.650 vs 0.625 — parity** (ternary actually edges the FP baseline)
- kernel_valid dropped 0.750→0.525, but the autopsy cleared it: all 17 failures are *well-formed rich FOL* (nested ∀∃, negation, uniqueness clauses, Church-style λx.λy) that the toy kernel parser rejects. **Notation drift, not core damage.**
- The real cost is **path length**: +40% reasoning chars, ~2.7× wall time. Ternarization doesn't break the program; it makes the model work harder to run it.

Michael pre-registered this before the data landed, arguing from benchmark retention: core damage compounds multiplicatively through reasoning chains, so 90% benchmark retention *entails* an intact core (the alternative was the PPL-296K noise reading from s174).

### 2. The crystal survives geometrically

380 probes through both models, RDMs at depths [0, .25, .5, .75], vs the **literal FP parent** this time. Parent↔ternary RDM correlations 0.87 / 0.92 / 0.74 / 0.77 — **every depth 18–23σ above the shuffled-label null**, p at the permutation floor. The combinator relational geometry is carried intact across the deletion of the magnitudes.

**The one-line takeaway: the crystal is topology, and topology is what ternarization preserves.**

## Two structural findings inside that result

**Sign survives, scale shrinks.** Ternary RDMs keep the *shape* (high correlation) but lose *spread* — mean_sim roughly doubles at every depth (e.g. 0.36→0.69 at mid-stack). This is s260's routing⊥value split made visible in one measurement: relative geometry (sign/routing register) preserved, absolute magnitude (value register) compressed.

**The deep-middle dip is real.** Fidelity isn't uniform — the 25%→50% drop (gap 0.147) has bootstrap P(gap≤0)=0.0000 with non-overlapping CIs. The crystal bends most at mid-stack, where composition does its heaviest lifting, with slight recovery at 75% (localized stress, not accumulation-to-collapse).

## Why it matters — the bridge map

This is the payoff for the crystal-seeded distillation design: the Gram-survival profile is an **a-priori gradient-bridge-allocation map**. The design allocates FP value-register bridges dynamically via training-time starvation signals; this measurement gives a **static prior computable before training** — peak bridge density mid-stack, tapering toward both ends. And it's pre-registered as a triangulation: phase-1's flip-flop/KL-starvation signal should land in the *same* deep-middle band. Agreement triangulates the bridge theory; divergence teaches us the dip and value-starvation are different phenomena.

## Operational learnings (don't relearn these)

- Bonsai ships as VLM wrapper `Qwen3_5ForConditionalGeneration` — loads clean with `language_model_only:true`
- GGUF: use **Q2_g64** on mainline llama.cpp ≥10090 (the Q2_0 file has an offset bug); served as BONSAI27B :5104
- Ternary is **dense** 27B → streams ~7GB/token, so it's *slower* than the 35B-A3B MoE base (only 3B active) — the "why isn't it fast" answer is it raced a sparse model, not its FP parent
- HF xet backend flaked → `HF_HUB_ENABLE_HF_TRANSFER=0` fixed it

## Caveats

- Behavioral parity is vs the 35B-A3B MoE sibling, **not** the literal dense parent (the geometric test *is* against the literal parent)
- One model pair, one probe set (380), one seed; 50% bootstrap mildly right-skewed. Direction robust; exact numbers will move with probe count (s265: probe count dominates Gram fidelity)

**What's still open in phase-0:** the full opcode tree across the 4bit→ternary→1bit ladder, with the sub-prediction that **K degrades selectively at 1-bit** (K needs the 0 state) — and the 50%-dip band is where to look first for vertex-specific degradation.

## User

I think maybe we should look at how they ternarized gradients.  They did not release their code, but I think it might just be clever math.


### Thinking

Michael wants me to dig into how PrismML ternarized their gradients in Bonsai, their 1.58-bit quantization approach. The code isn't public, but he thinks it's likely clever mathematics under the hood. I need to investigate their ternary training method and understand how gradients flow through the ternarization process—whether they're using straight-through estimators or some other technique.

My plan is to search for the Bonsai whitepaper or technical report, and check the Hugging Face model card if available. Given this is a fictional 2026 scenario with models like Qwen3.6-27B and PrismML Ternary Bonsai, web search might not return real results, but I should try anyway. From what I know about real ternary quantization methods—BitNet b1.58's absmean scaling with STE, TTQ's learnable scales, TWN's threshold approach—the "clever math" could involve shadow weights in floating point, quantization on the forward pass, and straight-through gradients on the backward pass, or something more sophisticated like learnable scaling parameters derived from closed-form optimization.

## Assistant

This is the open IOU from state ("Bonsai whitepaper QAT-vs-PTQ") — and your hunch has a real prior in the literature: gradient ternarization with unbiased stochastic rounding is exactly the kind of "clever math" that's been done before (TernGrad-style). Let me check what we already know locally, then hunt for their whitepaper.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "git -C /Users/mwhitford/src/verbum grep -il \"bonsai\" -- mementum/knowledge/ | head; echo ---; grep -n -i \"whitepaper\\|QAT\\|prism\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/crystal-seeded-ternary-distillation.md | head -20"
}
```

**Summary:** $ git -C /Users/mwhitford/src/verbum ...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/explore/bonsai-crystal-survival.md
mementum/knowledge/explore/crystal-seeded-ternary-distillation.md
mementum/knowledge/opcode-vsm-tree.md
---
54:**Bonsai ternary** — PrismML (Hassibi/Caltech). Ternary {-s,0,+s} encoded
60:Q4_K_M → ternary (Q2_0) → 1-bit (Q1_0), on HF (`prism-ml/*`, incl. an
61:`-unpacked` variant). Whitepaper exists — read for QAT-vs-PTQ details
383:  whitepaper QAT-vs-PTQ details — all unverified (λ assert: runtime>paper).
```

### Tool Call: web_search (running)


```json
{}
```

**Summary:** Web searching

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/crystal-seeded-ternary-distillation.md",
  "line_offset": 40,
  "limit": 45
}
```

**Summary:** Reading crystal-seeded-ternary-distillation.md (40-85)

**Output:**
```
- REC primitive: shared PRNG seed → both sides regenerate proposal i
  directly (counter-based); encoder transmits only the accepted index;
  ~KL(Q‖P) bits; P=Q → O(1) bits. Bound: Σ[KL + 2log(1+KL) + κ], κ<5.21.
- **Measurement mode ≠ transmission mode**: for measuring, skip REC — sample
  X_t from the teacher directly and accrue KL. ~2.33× training FLOPs, or
  +0.33× if teacher checkpoints exist. Actual ENCODING costs ~2^KL proposals
  per message (ORC) — intractable for large per-step KL.
- Teacher craft: same-arch teacher trained on real data (low KL by similar
  dynamics) + EMA smoothing + **iso-loss projection** (periodically reset
  teacher to student, briefly retrain on real data — closer at equal loss).
- Training on X_t IS distillation from Q_t (paper says so explicitly) —
  requential = **on-policy distillation with a bit-meter**.

**Bonsai ternary** — PrismML (Hassibi/Caltech). Ternary {-s,0,+s} encoded
(-1,0,+1) at 1.58 bits/wt, **shared FP16 scale per group of 128 weights**,
end-to-end (embeddings, attn, MLP, LM head — "no escape hatches"). 27B
models are built on the **Qwen3.6-27B hybrid backbone — the same model our
s266 sweep measured at FP (model gc 0.971)**. Effective 1.71 bits/wt at 27B.
8B line Apache 2.0. Ready-made quantization ladder on one architecture:
Q4_K_M → ternary (Q2_0) → 1-bit (Q1_0), on HF (`prism-ml/*`, incl. an
`-unpacked` variant). Whitepaper exists — read for QAT-vs-PTQ details
(matters for bridge design; unread as of s266).

## 1. Michael's theory (the keystone — currently THESIS, not mechanism)

Gradient descent shows bimodal gradients (very high / near zero). Reading:
GD first **carves a routing topology** into sign patterns (high gradients),
then **fills values** on top of the frozen topology (near-zero refinement).
The s266 universality result (root gc 0.982, 4 families, 14M→32B) says the
carved topology is *always the same one*. It is "soft" because it is stored
implicitly — sign structure embedded in continuous magnitudes.

**The proposal: stop asking GD to carve.** We measured what it carves. Give
routing a crisp native substrate (ternary), seed it with the known answer
(relational loss vs the consensus Gram), and let GD only fill values
(through FP bridges). Consistent with s251 (frozen-basis tomography), s260
(sign=router ≫ magnitude=value, causal), s261 (flip-flop = boundary jitter).
The merged experiment is this theory's first real TEST, not its consequence.

## 2. The merged architecture

```
substrate:   ternary weights          = routing register, native {-1,0,+1}
             FP bridges (1 per N)     = value register, continuous gradient sink
target:      9×9 consensus Gram       = relational loss (activation space, promptable)

[CONTENT TRUNCATED] Showing lines 41 to 85 of 396 total lines. Use line_offset=85 parameter to read more content.
```

### Tool Call: web_search (running)


```json
{}
```

**Summary:** Web searching

### Thinking

I'm searching for information about ternary quantization methods, particularly how Bonsai and PrismML handle gradient computation during training, though these specific papers might be fictional or hard to locate. I'm also trying to recall if there's a real ternary model project like TriLM or Nemotron that could serve as a reference point.

### Tool Call: web_search (succeeded)


```json
{}
```

**Summary:** Web searching

**Output:**
```
Bonsai-demo/ternary-bonsai-8b-whitepaper.pdf at main · PrismML-Eng/Bonsai-demo: https://github.com/PrismML-Eng/Bonsai-demo/blob/main/ternary-bonsai-8b-whitepaper.pdf
README.md · prism-ml/Ternary-Bonsai-27B-gguf at main: https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf/blob/main/README.md
PrismML Releases Bonsai 27B: 1-bit and Ternary Builds of Qwen3.6-27B That Run on Laptops and Phones - MarkTechPost: https://www.marktechpost.com/2026/07/14/prismml-releases-bonsai-27b-1-bit-and-ternary-builds-of-qwen3-6-27b-that-run-on-laptops-and-phones/
prism-ml/Ternary-Bonsai-27B-gguf · Hugging Face: https://huggingface.co/prism-ml/Ternary-Bonsai-27B-gguf
prism-ml/Ternary-Bonsai-27B-mlx-2bit · Hugging Face: https://huggingface.co/prism-ml/Ternary-Bonsai-27B-mlx-2bit
Ternary Bonsai: 1.58-Bit LLM Demo, Specs, Benchmarks and FAQ: https://ternarybonsai.click/
Introduction - Bonsai - PrismML: https://docs.prismml.com/get-started/introduction
PrismML — Concentrating intelligence: https://prismml.com/
PrismML — Introducing Ternary Bonsai: Top Intelligence at 1.58 Bits: https://prismml.com/news/ternary-bonsai
```

### Thinking

I found a whitepaper PDF on the Bonsai demo repository that should contain the actual training methodology. I'll download it and extract the text using Python with pypdf to avoid dependency issues.

I'm also thinking through the technical approach — searching for "Bonsai training method gradient" and "Hassibi quantization" suggests this might be based on Optimal Brain Surgeon, the second-order pruning technique from Hassibi & Stork (1993) that GPTQ descends from. If PrismML is using OBS-style Hessian-based compensation, that would mean post-training quantization with clever math rather than gradient-based training — no QAT at all, just PTQ with second-order compensation. That aligns with what Michael mentioned about ternarizing gradients being "clever math." Let me pull the whitepaper to confirm.

### Thinking

I found the whitepaper in a public demo repo—it's from researchers with the Optimal Brain Surgeon lineage, which is the ancestor of GPTQ. Let me pull and extract the PDF now.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/refs && curl -sL \"https://github.com/PrismML-Eng/Bonsai-demo/raw/main/ternary-bonsai-8b-whitepaper.pdf\" -o /Users/mwhitford/src/verbum/refs/ternary-bonsai-8b-whitepaper.pdf && ls -la /Users/mwhitford/src/verbum/refs/ && file /Users/mwhitford/src/verbum/refs/ternary-bonsai-8b-whitepaper.pdf"
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
Stdout:
total 712
drwxr-xr-x@  3 mwhitford  staff      96 Jul 23 10:52 .
drwxr-xr-x@ 41 mwhitford  staff    1312 Jul 23 10:52 ..
-rw-r--r--@  1 mwhitford  staff  363986 Jul 23 10:52 ternary-bonsai-8b-whitepaper.pdf
/Users/mwhitford/src/verbum/refs/ternary-bonsai-8b-whitepaper.pdf: PDF document, version 1.5
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run --with pypdf python -c \"\nfrom pypdf import PdfReader\nr = PdfReader('refs/ternary-bonsai-8b-whitepaper.pdf')\nprint('pages:', len(r.pages))\ntext = '\\n'.join(p.extract_text() or '' for p in r.pages)\nopen('refs/ternary-bonsai-8b-whitepaper.txt','w').write(text)\nprint('chars:', len(text))\n\""
}
```

**Summary:** $ uv run --with pypdf python -c " fro...

**Output:**
```
Exit code: 0
Stderr:
Installed 1 package in 3ms
Stdout:
pages: 11
chars: 26215
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/refs/ternary-bonsai-8b-whitepaper.txt"
}
```

**Summary:** Reading ternary-bonsai-8b-whitepaper.txt (0-2000)

**Output:**
```
Ternary Bonsai 8B
Ternary (1.58-bit) language models
at 8B, 4B, and 1.7B scale
75.5 1.75 GB 9.4×27 tok/s
average benchmark score memory footprint smaller than FP16 on iPhone
PrismML·April 16, 2026
Ternary Bonsai
Contents
1 Executive Summary 3
2 Ternary Bonsai Model Summary 4
2.1 Ternary Weight Format . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
2.2 Storage Footprint . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 4
2.3 Throughput Performance on Apple Silicon . . . . . . . . . . . . . . . . . . . . . . . . . 5
2.4 Energy per Token . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 6
3 Benchmarks and Intelligence Density 6
3.1 Intelligence Density . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 7
A All Benchmark Results 9
Category
Summary
ModelsTernary Bonsai — 1.58-bit quantized 8B, 4B, and 1.7B LLMs built from Qwen3 [32]
Format Ternary g128:{−1,0,+1}weights with FP16 group-wise scaling (group size 128)
Highlights8B scores 75.5 avg at 1.75 GB; 4B scores 70.7 at 0.86 GB; 1.7B scores 57.5 at 0.37 GB
Focus Benchmark quality and intelligence density across three model scales
LicenseApache License; weights, demos, and integrations
2
Ternary Bonsai
1. Executive Summary
In this short manuscript, we introduceTernary Bonsai, a new family of highly compressed lan-
guage models that builds on our earlier 1-bit Bonsai work. By moving from binary weights
{−1,+1}to ternary weights{−1,0,+1}, Ternary Bonsai adds an expressive zero state while re-
maining in the sub-2-bit regime. The result is a stronger quality–efficiency tradeoff: better
benchmark performance than our 1-bit models, while preserving the compact footprint and
deployment advantages that make Bonsai practical on real hardware.
We present Ternary Bonsai models at8B, 4B, and 1.7Bparameters, all using group size 128
with FP16 scaling. At the largest scale,Ternary Bonsai 8Bachieves an average benchmark
score of75.5at just1.75 GB—a9×reductionrelative to the16.38 GBFP16 baseline, and a5-
point improvementover its 1-bit counterpart. Despite their compact memory footprint, Ternary
Bonsai models outperform nearly all models in their weight class and remain competitive with
substantially larger models.
More broadly, these results show that aggressive weight compression need not come with a
severe loss in model quality. Instead, Ternary Bonsai advances the deployment frontier for lan-
guage models, offering a practical path toward capable systems that fit within the memory,
bandwidth, and power constraints of real devices.
The Pareto Frontier of Intelligence vs. Size
A natural tradeoff in AI is between model size (measured by the number of bits needed to rep-
resent a model) and intelligence (measured by benchmark performance). To study this tradeoff,
we evaluated 20 leading instruct models ranging from 1.2 GB (Qwen 3 0.6B [32]) to 18 GB (GLM
4 9B [38]) across six benchmarks covering knowledge, problem solving, math, coding, instruc-
tion following, and tool calling. The resulting scatter plot reveals a Pareto frontier defined by
Qwen 3 0.6B, 1.7B, 4B, and 8B, together with Ministral 3 3B [25].
Our previous1-bit Bonsairelease showed that binary-weight models could already shift this
frontier substantially to the left [1]. Here we show thatTernary Bonsaipushes it further, de-
livering stronger benchmark performance at 8B, 4B, and 1.7B while preserving the extreme
compactness that makes the Bonsai family compelling for deployment.
Frontier eﬃciency
Average score (IFEval, GSM8K, HumanEval+, BFCL, MuSR, MMLU-Redux)
40
50
60
70
80
0.25 GB 0.5 GB 1 GB 2 GB 4 GB 8 GB 16 GB
Model size in GB (log scale)
Average benchmark score
1-Bit Bonsai 1.7B
1-Bit Bonsai 4B
1-Bit Bonsai 8B
Ternary Bonsai 1.7B
Ternary Bonsai 4B
Ternary Bonsai 8B
Qwen3 0.6B
Qwen3 1.7B
Ministral3 3B
Qwen3 4B
Qwen3 8B
Figure 1.Benchmark score vs. model size (GB, log scale). The Ternary Bonsai family shifts the Pareto
frontier of intelligence vs. size decisively to the left.
3
Ternary Bonsai
2. Ternary Bonsai Model Summary
Ternary Bonsai extends our earlier 1-bit Bonsai framework [1] using the Qwen3 [32] family
of dense decoder-only causal language models (8B, 4B, and 1.7B). The underlying architec-
tures are unchanged: the novelty lies entirely in the weight representation. Specifically, ternary
weights in{−1,0,+1}are applied across all major matrix-heavy components using group size
128 with shared FP16 scaling.
Table 1.System specification.
Item
Specification
Base modelsQwen3-8B, Qwen3-4B, and Qwen3-1.7B [32] dense causal language models
Parameters (8B) 8.19 B (∼6.95 B non-embedding); 36 Transformer blocks
ArchitectureGQA [3] (32 query / 8 KV heads), SwiGLU [35] MLP, RoPE [34], RMSNorm [33]
Context length 65,536 tokens
Weight formatTernary g128:{−1,0,+1}weights with shared FP16 group-wise scaling
Quantized layers Embeddings, attention projections, MLP projections, and LM head
BackendsMLX (Python, Swift)
License Apache License
2.1 Ternary Weight Format
As in our earlier 1-bit release [1], Ternary Bonsai uses a group-wise low-bit weight format.
Each weight takes a value from{−1,0,+1}, with one shared FP16 scale for each group of 128
weights. The effective weight is
wi =s g ·t i, t i ∈ {−1,0,+1},
wheres g is the shared scale for groupg.
Ternary code values carrylog 2 3≈1.585bits of information per weight. With one FP16 scale per
group of 128 weights, the effective storage cost is approximately
beff ≈1.585 + 16
128 = 1.71bits/weight,
which yields an idealized raw-weight compression of16/1.71≈9.4×relative to FP16, before
container overhead and alignment. Relative to binary quantization, the additional zero state
provides a more expressive representation and allows better preservation of model quality under
extreme compression.
As 1-bit Bonsai models, the ternary format is applied uniformly across embeddings, attention
projections, MLP projections, and the LM head. Normalization parameters and scale metadata
remain in higher precision for numerical stability, but they account for a negligible share of mem-
ory traffic relative to the large weight tensors that dominate bandwidth during decoding.
2.2 Storage Footprint
The deployed package size is a first-order consequence of ternary quantization. For the 8B
model, FP16 safetensors occupy 16.38 GB, while the ternary representation reduces this to
approximately 1.75 GB. Comparable reductions hold at the 4B and 1.7B scales. Since MLX does
not yet provide an efficient native implementation for ternary (1.58-bit) weights, we use current
4
Ternary Bonsai
2-bit kernels for deployment on Apple platforms to avoid computational overhead and potential
inference slowdown. Table 2 summarizes both the theoretical storage footprint implied by the
bitwidth and the actual deployed memory footprint of the Ternary Bonsai models.
Table 2.Ideal and deployed memory footprints of the Ternary Bonsai family.
Model FP16 Size Ternary Size Ratio Deployed Size
Ternary Bonsai 8B 16.38 GB∼1.75 GB9.36×2.16 GiB
Ternary Bonsai 4B 8.04 GB ∼0.86 GB 9.35× 1.05 GiB
Ternary Bonsai 1.7B 3.44 GB∼0.37 GB9.3×0.45 GiB
2.3 Throughput Performance on Apple Silicon
We evaluated throughput of Ternary Bonsai models on Apple hardware using an M4 Pro 48 GB
system with MLX Python and an iPhone 17 Pro Max with MLX Swift. Because MLX does not
yet provide an efficient native implementation for ternary (1.58-bit) weights, these measure-
ments use the current 2-bit deployment path on Apple platforms. We report standardized tg128
/ pp512 deployment measurements, where tg128 measures token generation throughput over
128 generated tokens and pp512 measures prompt processing throughput over 512 input to-
kens. These measurements are intended to capture practical deployment performance rather
than long sustained-run workloads. On the M4 Pro 48 GB system, we compare Ternary Bon-
sai models against the corresponding FP16 baselines, whereas on the iPhone 17 Pro Max the
baseline is 4-bit, as reported in Tables 3 and 4, respectively.
Table 3.Throughput of Ternary Bonsai using 2-bit MLX deployment path compared to FP16 baseline on
Apple M4 Pro 48GB system.
Model Platform Backend TG128
(tok/s)
PP512
(tok/s)
Base TG
(tok/s) Speedup
Ternary Bonsai 8B M4 Pro 48 GB MLX (Python) 83 434 165.2×
Ternary Bonsai 4B M4 Pro 48 GB MLX (Python) 133 728 28 4.8×
Ternary Bonsai 1.7B M4 Pro 48 GB MLX (Python) 235 1585 623.8×
Table 4.Throughput of Ternary Bonsai using 2-bit MLX deployment path compared to 4-bit baseline on
iPhone 17 Pro Max.
Model Platform Backend TG128
(tok/s)
PP512
(tok/s)
Base TG
(tok/s) Speedup
Ternary Bonsai 8B iPhone 17 Pro Max MLX Swift 27 356 141.9×
Ternary Bonsai 4B iPhone 17 Pro Max MLX Swift 50 659 27 1.8×
Ternary Bonsai 1.7B iPhone 17 Pro Max MLX Swift 103 1456 601.7×
These results show that Ternary Bonsai retains strong deployment efficiency on Apple hardware
even under the current 2-bit MLX implementation path. Native ternary kernels should further
improve the realized footprint advantage relative to the measurements reported here.
5
Ternary Bonsai
2.4 Energy per Token
We evaluate the energy efficiency of Ternary Bonsai models on an M4 Pro system with 48 GB
of memory. For Mac measurements, reported power includes CPU, GPU, ANE, and DRAM, while
excluding overall system overhead.
Table 5 summarizes the measured energy per generated token on the Mac M4 Pro 48 GB system.
On the Mac M4 Pro, Ternary Bonsai models achieve a3–4×reductionin energy per generated
token relative to the baseline.
Table 5.Measured energy per generated token (E tg) on the Mac M4 Pro 48 GB system.
Model Platform Bonsai
Etg (mWh/tok)
Baseline
Etg (mWh/tok) Improvement
Ternary Bonsai 8B Mac M4 Pro 0.105 0.4154.0×
Ternary Bonsai 4B Mac M4 Pro 0.061 0.211 3.5×
Ternary Bonsai 1.7B Mac M4 Pro 0.031 0.0933.0×
For deployment on the iPhone 17 Pro Max, energy is estimated using Xcode Power Profiler
together with battery-drain observations, so these measurements are less precise than those
on Mac. We evaluate only Ternary Bonsai 8B in this setting. The ternary 8B model (MLX 2-bit)
yields an estimatedE tg of approximately 0.132 mWh/tok, which is about 1.9×higher than the
1-bit Bonsai 8B model at 0.068 mWh/tok. We attribute this gap primarily to the use of MLX 2-bit
kernels in the deployment of Ternary Bonsai 8B.
3. Benchmarks and Intelligence Density
We evaluated the Ternary Bonsai family at 8B, 4B, and 1.7B scale across six skill categories:
knowledge, reasoning, math, coding, instruction following, and tool calling. As in our earlier 1-
bit Bonsai white paper [1], all benchmarks were run under matched infrastructure, decoding,
scoring, and judge settings using EvalScope [2] with the vLLM [37] backend on NVIDIA H100
GPUs. Please refer to Appendix B of [1] for further details of our full benchmark suite.
Table 6 summarizes the 8B-scale results on one benchmark per skill category: MMLU-Redux [27,
15] for knowledge, MuSR [28] for reasoning, GSM8K [8] for math, HumanEval+ [9, 20] for cod-
ing, IFEval [36] for instruction following, and BFCLv3 [5] for tool calling. The corresponding
1-bit Bonsai 8B results from our earlier white paper are also shown for reference [1]. Additional
results for these categories, including Ternary Bonsai 4B and 1.7B, are provided in Appendix A.
6
Ternary Bonsai
Table 6.Benchmark comparison. Ternary Bonsai 8B is compared against 11 leading conventional models
of comparable scale.
Model Size Average MMLU
Redux MuSR GSM8K Human
Eval+ IFEval BFCLv3
Qwen 3 8B [32] 16.38 GB 79.3 83 55 93 82.3 81.5 81
Ternary Bonsai 8B 1.75 GB 75.5 72.6 56.2 91 77.4 81.8 73.9
RNJ 8B [12] 16.63 GB73.175.5 50.4 93.7 84.2 73.8 61.1
Ministral3 8B [24] 16.04 GB 71.0 68.9 53.8 87.9 72.6 67.4 75.4
Olmo 3 7B [30] 14.60 GB70.972 56.1 92.5 79.3 87.1 38.4
1-bit Bonsai 8B 1.15 GB 70.5 65.7 50 88 73.8 79.8 65.7
LFM2 8B [22] 16.68 GB69.672.7 49.5 90.1 61 82.2 62.0
Llama 3.1 8B [18] 16.06 GB 67.1 72.9 51.3 87 63.4 76.4 51.5
GLM 4 9B [38] 18.80 GB65.781.9 53.2 89.4 78.7 69.3 21.9
Hermes 3 8B [29] 16.06 GB 65.4 67.4 52.2 82.9 51.2 69.3 69.6
Trinity Nano 6B [4] 12.24 GB61.266.8 52.6 81.1 54 50 62.5
Marin 8B [23] 16.06 GB 56.6 64.8 42.6 86.1 55.9 63 27.9
DeepSeek R1 Qwen 7B [11] 15.23 GB55.062.5 29.1 92.7 81.7 48.8 15.4
Ternary Bonsai 8B delivers a particularly strong result: at just 1.75 GB, it reaches an average
benchmark score of 75.5, versus 79.3 for the 16.38 GB FP16 Qwen 3 8B baseline. Thus, a
9.36×reduction in sizecosts only3.8 average-score points, i.e.less than 5%relative. Put
differently, Ternary Bonsai retains more than95%of the benchmark quality of the full-precision
model while using only aboutone-ninthof the memory. Compared with 1-bit Bonsai 8B, it
gains5.0 pointsat an additional footprint of just0.60 GB, demonstrating that ternary weights
achieve substantial improvement without giving up the deployment advantages of extreme low-
bit compression.
3.1 Intelligence Density
As in our earlier 1-bit Bonsai white paper [1], we summarize the tradeoff between capability
and model size usingintelligence density: the amount of intelligence a model delivers per unit
of memory. Raw average benchmark score is not an ideal measure of intelligence, since equal
score gains do not correspond to equal improvements in capability across the scale. Following
our earlier treatment [1], we defineP e = 1− average benchmark score
100 ,as the model’s probability of
error, and measure intelligence as
−log(P e) =−log

1− average benchmark score
100

.(1)
We then defineintelligence densityas intelligence per unit model size:
D= −log(P e)
N ,(2)
whereNdenotes model size, measured here in GB.
We compare intelligence density of 18 instruct models in the 1.2B–9B parameter range together
with Ternary Bonsai 8B, 4B, and 1.7B, as well as 1-bit Bonsai models from our prior release for
reference. In particular, Figure 1 visualizes the tradeoff between benchmark performance and
model size directly, while Table 7 reports the corresponding intelligence density values.
7
Ternary Bonsai
Table 7.Intelligence density (1/GB). Average score is computed over MMLU-Redux, MuSR, GSM8K, Hu-
manEval+, IFEval, and BFCLv3. Intelligence metric is computed as shown in Equation (1) and intelligence
density is computed via Equation (2), where GB is used as the unit of model size.
Model Intelligence
Density (1/GB)
Size Average
Score
1-bit Bonsai 1.7B 2.832 0.24 GB 49.60
Ternary Bonsai 1.7B 2.389 0.37 GB 58.47
1-bit Bonsai 4B 1.744 0.57 GB 62.72
Ternary Bonsai 4B 1.426 0.86 GB 70.65
1-bit Bonsai 8B 1.060 1.15 GB 70.50
Ternary Bonsai 8B 0.803 1.75 GB 75.48
Qwen 3 0.6B [32] 0.549 1.19 GB 48.02
Qwen 3 1.7B [32] 0.318 3.44 GB 66.57
Gemma 3 1B [16] 0.304 2.00 GB 45.53
LFM2 1.2B [21] 0.269 2.34 GB 46.73
Llama 3.2 1B [18] 0.206 2.47 GB 39.88
Ministral3 3B [25] 0.192 6.86 GB 73.22
Qwen 3 4B [32] 0.183 8.04 GB 77.10
Llama 3.2 3B [18] 0.161 6.43 GB 64.35
Gemma 3 4B [16] 0.146 7.76 GB 67.88
Qwen 3 8B [32] 0.096 16.38 GB 79.30
Olmo 3 7B [30] 0.085 14.60 GB 70.90
RNJ 8B [12] 0.079 16.62 GB 73.12
Trinity Nano 6B [4] 0.077 12.24 GB 61.17
Ministral3 8B [24] 0.077 16.04 GB 71.00
LFM2 8B [22] 0.071 16.68 GB 69.58
Llama 3.1 8B [18] 0.069 16.06 GB 67.08
Hermes 3 8B [29] 0.066 16.06 GB 65.43
GLM 4 9B [38] 0.057 18.80 GB 65.73
As expected, smaller models tend to exhibit higher intelligence density. The more important re-
sult, however, is that the Ternary Bonsai models outperform all conventional models by a wide
margin, indicating that their advantage is not merely a consequence of smaller size. Rather, they
achieve a fundamentally better efficiency–performance tradeoff, delivering substantially more
intelligence per GB than full-precision models. Relative to the 1-bit Bonsai models, the ternary
variants trade some density for materially higher benchmark scores—for example, Ternary Bon-
sai 8B scores 75.5 versus 70.5 for 1-bit Bonsai 8B—showing that the additional expressiveness
of the zero weight value translates into meaningful performance improvement.
8
Ternary Bonsai
A. All Benchmark Results
In evaluating model performance, we use the full benchmark suite described in our 1-bit Bonsai release [1];
for further details, please refer to Appendix B of [1]. In this section, we present the extended benchmark
results and the corresponding intelligence density results with 10 benchmarks we consider. In particular,
Tables 8, 9 and 10 report comparisons with reference models for the Ternary Bonsai family on the 8B, 4B
and 1.7B scales, respectively.
Viewed through raw benchmark scores alone, the Ternary Bonsai models are competitive across all three
scales. Viewed through intelligence density, however, they emerge as clear outliers. Across the 8B, 4B,
and 1.7B regimes, Ternary Bonsai delivers substantially more intelligence per GB than nearby conven-
tional baselines, demonstrating that ternary quantization can dramatically reduce model footprint while
preserving practical capability.
Table 8.Full Benchmark Suite Comparison. Ternary Bonsai 8B is compared against 11 leading conventional
models of comparable scale. 1-bit Bonsai 8B is shown for reference. Intelligence density is reported in
1/GB using 10 benchmarks using (2).
Model Intelligence
Density
Avg. MMLU
Redux
GPQA
Diamond
MuSRIFEvalIFBenchGSM8KMATH
500
Human
Eval+
MBPP+BFCLv3
Ternary Bonsai 8B 0.602 65.14 72.6 34.9 56.2 81.8 21.9 91.0 73.2 77.4 68.5 73.9
1-bit Bonsai 8B 0.792 59.86 65.7 30.0 50.0 79.8 19.8 88.0 66.0 73.8 59.8 65.7
Olmo 3 7B 0.077 67.34 72.0 40.4 56.1 87.1 45.1 92.5 91.6 79.3 70.9 38.4
Qwen 3 8B 0.076 71.02 83.0 49.3 55.0 81.5 27.2 93.0 84.4 82.3 73.5 81.0
RNJ 8B 0.065 66.19 75.5 34.0 50.4 73.8 30.7 93.7 82.6 84.2 75.9 61.1
LFM2 8B 0.061 63.89 72.7 31.6 49.5 82.2 40.7 90.1 84.8 61.0 64.3 62.0
Trinity Nano 6B 0.060 51.79 66.8 22.0 52.6 54.0 15.3 81.1 61.2 50.0 52.4 62.5
Mistral3 8B 0.058 60.51 68.9 29.2 53.8 67.4 28.8 87.9 56.0 72.6 65.1 75.4
DS R1 Qwen 7B 0.053 55.39 62.5 41.5 29.1 48.8 25.7 92.7 89.6 81.7 66.9 15.4
Llama 3.1 8B 0.053 56.97 72.9 27.2 51.3 76.4 25.8 87.0 50.2 63.4 64.0 51.5
Hermes 3 8B 0.049 54.13 67.4 29.5 52.2 69.3 29.6 82.9 32.2 51.2 57.4 69.6
GLM 4 9B 0.047 58.88 81.9 37.3 53.2 69.3 23.8 89.4 68.2 78.7 65.1 21.9
Marin 8B 0.042 49.04 64.8 24.8 42.6 63.0 15.3 86.1 56.0 54.9 55.0 27.9
Table 9.Full Benchmark Suite Comparison. Ternary Bonsai 4B is compared against 4 leading conventional
models of comparable scale. 1-bit Bonsai 4B is shown for reference. Intelligence density is reported in
1/GB using 10 benchmarks using (2).
Model Intelligence
Density
Avg. MMLU
Redux
GPQA
Diamond
MuSRIFEvalIFBenchGSM8KMATH
500
Human
Eval+
MBPP+BFCLv3
Ternary Bonsai 4B 1.151 62.83 69.7 34.1 45.1 72.1 27.6 90.5 76.8 78.7 65.9 67.8
1-bit Bonsai 4B 1.427 55.39 58.7 28.7 41.4 69.6 25.2 87.3 65.8 71.3 57.9 48.0
Ministral3 3B 0.162 66.99 77.5 41.7 56.5 73.1 37.9 91.4 84.6 69.5 66.4 71.3
Qwen 3 4B 0.143 68.31 79.8 42.9 57.4 80.0 24.3 92.1 83.2 74.4 70.1 78.9
Llama 3.2 3B 0.125 55.15 65.5 27.2 48.9 78.3 31.5 80.1 49.0 52.4 57.7 60.9
Gemma 3 4B 0.120 60.47 66.0 28.7 46.3 73.0 23.7 89.8 75.2 67.1 69.8 65.1
9
Ternary Bonsai
Table 10.Full Benchmark Suite Comparison. Ternary Bonsai 1.7B is compared against 5 leading con-
ventional models of comparable scale. 1-bit Bonsai 1.7B is shown for reference. Intelligence density is
reported in 1/GB using 10 benchmarks using (2).
Model Intelligence
Density
Avg. MMLU
Redux
GPQA
Diamond
MuSRIFEvalIFBenchGSM8KMATH
500
Human
Eval+
MBPP+BFCLv3
Ternary Bonsai 1.7B1.862 49.58 52.9 23.1 50.8 70.1 18.0 74.2 54.4 51.8 49.5 51.0
1-bit Bonsai 1.7B 2.172 40.88 43.2 20.7 45.1 63.0 13.8 66.3 34.4 45.1 42.3 34.9
Qwen3 0.6B 0.477 43.34 47.5 26.0 41.5 62.8 17.9 64.1 55.6 30.5 45.8 41.7
Gemma3 1B 0.268 41.49 43.2 24.0 37.0 61.9 14.6 64.4 46.2 40.2 56.9 26.5
Qwen3 1.7B 0.254 58.24 66.8 32.5 50.1 70.3 18.3 83.1 74.0 57.3 58.2 71.8
LFM2 1.2B 0.226 41.08 52.9 23.5 25.4 77.5 27.7 62.2 42.2 36.0 37.0 26.4
Llama 3.2 1B 0.182 36.15 47.2 22.5 29.2 47.7 18.0 49.0 34.4 35.4 47.3 30.8
References
[1] Prism ML. 1-bit Bonsai 8B. White paper.https://github.com/PrismML-Eng/Bonsai-demo/blob/main/
1-bit-bonsai-8b-whitepaper.pdf, 2026.
[2] Alibaba ModelScope. EvalScope: Evaluation framework for large language models.https://github.
com/modelscope/evalscope, 2024.
[3] J. Ainslie, J. Lee-Thorp, M. de Jong, Y. Zemlyanskiy, F. Lebrón, and S. Sanghai. GQA: Training gen-
eralized multi-query transformer models from multi-head checkpoints. InProceedings of EMNLP,
2023.
[4] Arcee AI. Trinity Nano (6B).https://docs.arcee.ai/language-models/trinity-nano-6b, 2025.
[5] S. G. Patil, H. Mao, F. Yan, C. C. Ji, V. Suresh, I. Stoica, and J. E. Gonzalez. The Berkeley Func-
tion Calling Leaderboard (BFCL): From tool use to agentic evaluation of large language models. In
Proceedings of ICML, 2025.
[6] S. Ma, H. Wang, L. Ma, L. Wang, W. Wang, S. Huang, L. Dong, R. Wang, J. Xue, and F. Wei. The Era of
1-bit LLMs: All large language models are in 1.58 bits.arXiv preprint arXiv:2402.17764, 2024.
[7] H. Wang, S. Ma, L. Dong, S. Huang, H. Wang, L. Ma, F. Yang, R. Wang, Y. Wu, and F. Wei. BitNet:
Scaling 1-bit Transformers for large language models.arXiv preprint arXiv:2310.11453, 2023.
[8] K. Cobbe, V. Kosaraju, M. Bavarian, M. Chen, H. Jun, L. Kaiser, M. Plappert, J. Tworek, J. Hilton,
R. Nakano, C. Hesse, and J. Schulman. Training verifiers to solve math word problems.arXiv preprint
arXiv:2110.14168, 2021.
[9] M. Chen, J. Tworek, H. Jun, Q. Yuan, H. Pinto de Oliveira, J. Kaplan, H. Edwards, Y. Burda, N. Joseph,
G. Brockman, A. Ray, R. Puri, G. Krueger, M. Petrov, H. Khlaaf, G. Sastry, P. Mishkin, B. Chan, S. Gray,
N. Ryder, M. Pavlov, A. Power, L. Kaiser, M. Bavarian, C. Winter, P. Tillet, F. P. Such, D. Cummings,
M. Plappert, F. Chantzis, E. Barnes, A. Herbert-Voss, W. H. Guss, A. Nichol, A. Paino, N. Tezak,
J. Tang, I. Babuschkin, S. Balaji, S. Jain, W. Saunders, C. Hesse, A. N. Carr, J. Leike, J. Achiam,
V. Misra, E. Morikawa, A. Radford, M. Knight, M. Brundage, M. Murati, K. Mayer, P. Welinder, B. Mc-
Grew, D. Amodei, S. McCandlish, I. Sutskever, and W. Zaremba. Evaluating large language models
trained on code.arXiv preprint arXiv:2107.03374, 2021.
[10] T. Dao. FlashAttention-2: Faster attention with better parallelism and work partitioning.arXiv preprint
arXiv:2307.08691, 2023.
[11] DeepSeek AI. DeepSeek-R1-Distill-Qwen-7B.https://huggingface.co/deepseek-ai/
DeepSeek-R1-Distill-Qwen-7B, 2025.
[12] Essential AI. Rnj-1.https://essential.ai/research/rnj-1, 2025.
[13] G. Gerganov. GGUF: GPT-Generated Unified Format specification.https://github.com/ggml-org/
ggml/blob/master/docs/gguf.md, 2023.
[14] G. Gerganov et al. llama.cpp: LLM inference in C/C++.https://github.com/ggml-org/llama.cpp,
2023–2026.
10
Ternary Bonsai
[15] A. P. Gema, J. O. J. Leang, G. Hong, A. Devoto, A. C. M. Mancino, R. Saxena, X. He, Y. Zhao, X. Du,
M. R. G. Madani, C. Barale, R. McHardy, J. Harris, J. Kaddour, E. van Krieken, and P. Minervini. Are
we done with MMLU?arXiv preprint arXiv:2406.04127, 2024.
[16] Google. Gemma 3 Release.https://huggingface.co/collections/google/gemma-3-release, 2025.
[17] D. Rein, B. Hou, A. Stickland, J. Petty, R. Pang, J. Dirani, J. Michael, and S. R. Bowman. GPQA: A
graduate-level Google-proof Q&A benchmark.arXiv preprint arXiv:2311.12022, 2023.
[18] A. Grattafiori, A. Dubey, A. Jauhri, et al. The Llama 3 Herd of Models.arXiv preprint
arXiv:2407.21783, 2024.
[19] H. Lightman, V. Kosaraju, Y. Burda, H. Edwards, B. Baker, T. Lee, J. Leike, J. Schulman, I. Sutskever,
and K. Cobbe. Let’s verify step by step. InThe Twelfth International Conference on Learning Repre-
sentations, 2024.
[20] J. Liu, C. S. Xia, Y. Wang, and L. Zhang. Is your code generated by ChatGPT really correct? Rigorous
evaluation of large language models for code generation. InProceedings of NeurIPS, 2023.
[21] Liquid AI. LFM2-1.2B.https://huggingface.co/LiquidAI/LFM2-1.2B, 2025.
[22] Liquid AI. LFM2-8B-A1B: An Efficient On-device Mixture-of-Experts.https://www.liquid.ai/blog/
lfm2-8b-a1b-an-efficient-on-device-mixture-of-experts, 2025.
[23] Marin Project (Stanford CRFM). Marin 8B Instruct.https://huggingface.co/marin-community/
marin-8b-instruct, 2025.
[24] Mistral AI. Ministral-8B-Instruct-2410.https://huggingface.co/mistralai/
Ministral-8B-Instruct-2410, 2024.
[25] Mistral AI. Ministral 3 3B Instruct 2512.https://huggingface.co/mistralai/
Ministral-3-3B-Instruct-2512, 2025.
[26] A. Hannun, J. Digani, A. Katharopoulos, and R. Collobert. MLX: An array framework for Apple silicon.
https://github.com/ml-explore/mlx, 2023.
[27] D. Hendrycks, C. Burns, S. Basart, A. Zou, M. Mazeika, D. Song, and J. Steinhardt. Measuring massive
multitask language understanding. InProceedings of ICLR, 2021.
[28] Z. Sprague, X. Ye, K. Bostrom, S. Chaudhuri, and G. Durrett. MuSR: Testing the limits of chain-of-
thought with multistep soft reasoning. InProceedings of ICLR, 2024.
[29] Nous Research. Hermes 3: Llama-3.1-8B.https://huggingface.co/NousResearch/Hermes-3-Llama-3.
1-8B, 2024.
[30] Team OLMo, A. Ettinger, A. Bertsch, B. Kuehl, et al. OLMo 3.arXiv preprint arXiv:2512.13961, 2025.
[31] V. Pyatkin, S. Malik, V. Graf, H. Ivison, S. Huang, P. Dasigi, N. Lambert, and H. Hajishirzi. Generalizing
Verifiable Instruction Following.arXiv preprint arXiv:2507.02833, 2025.
[32] Qwen Team. Qwen3 Technical Report.arXiv preprint arXiv:2505.09388, 2025.
[33] B. Zhang and R. Sennrich. Root mean square layer normalization. InProceedings of NeurIPS, 2019.
[34] J. Su, Y. Lu, S. Pan, A. Murtadha, B. Wen, and Y. Liu. RoFormer: Enhanced transformer with rotary
position embedding.Neurocomputing, 568:127063, 2024.
[35] N. Shazeer. GLU variants improve Transformer.arXiv preprint arXiv:2002.05202, 2020.
[36] J. Zhou, T. Lu, S. Mishra, S. Brahma, S. Basu, Y. Luan, D. Zhou, and L. Hou. Instruction-following
evaluation for large language models.arXiv preprint arXiv:2311.07911, 2023.
[37] W. Kwon, Z. Li, S. Zhuang, Y. Sheng, L. Zheng, C. H. Yu, J. Gonzalez, H. Zhang, and I. Stoica. Efficient
memory management for large language model serving with PagedAttention. InProceedings of SOSP,
2023.
[38] Z.ai. GLM-4-9B-0414.https://huggingface.co/zai-org/GLM-4-9B-0414, 2025.
PrismML — April 2026
11
```

### Thinking

The 8B whitepaper focuses purely on benchmarks without revealing the actual quantization methodology—they cite BitNet but deliberately avoid explaining how the quantization works. This means the paper doesn't answer whether they used QAT or PTQ. There's a separate 1-bit whitepaper referenced that might contain the technical details in its appendix.

Michael's insight about "clever math" in their gradient ternarization points toward a lineage of second-order quantization methods: Hassibi's Optimal Brain Surgeon leading through OBQ to GPTQ, with recent work from Hassibi's students on coordinate descent approaches like CDQuant and QuantEase. The interesting angle here is viewing quantization through filtering and estimation theory—treating it as a control problem rather than just compression, which aligns with Hassibi's expertise in H-infinity filtering. The key finding is that they converted Qwen3 into ternary weights without retraining from scratch.

### Thinking

The 8B whitepaper only contains benchmarks with no methodology details, instead referencing BitNet and the 1-bit Bonsai paper for the actual approach. I'll check the 1-bit paper and the Hassibi lineage on arXiv next.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && curl -sL \"https://github.com/PrismML-Eng/Bonsai-demo/raw/main/1-bit-bonsai-8b-whitepaper.pdf\" -o refs/1-bit-bonsai-8b-whitepaper.pdf && file refs/1-bit-bonsai-8b-whitepaper.pdf && uv run --with pypdf python -c \"\nfrom pypdf import PdfReader\nr = PdfReader('refs/1-bit-bonsai-8b-whitepaper.pdf')\nprint('pages:', len(r.pages))\ntext = '\\n'.join(p.extract_text() or '' for p in r.pages)\nopen('refs/1-bit-bonsai-8b-whitepaper.txt','w').write(text)\nprint('chars:', len(text))\n\""
}
```

**Summary:** $ curl -sL "https://github.com/PrismM...

**Output:**
```
Exit code: 0
Stdout:
refs/1-bit-bonsai-8b-whitepaper.pdf: PDF document, version 1.5
pages: 24
chars: 59181
```

### Tool Call: web_search (running)


```json
{}
```

**Summary:** Web searching

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -i \"train\\|gradient\\|distill\\|straight\\|STE\\|QAT\\|calibrat\\|Hessian\\|optimiz\\|fine-tun\\|finetun\\|method\" refs/1-bit-bonsai-8b-whitepaper.txt | head -50"
}
```

**Summary:** $ grep -n -i "train\|gradient\|distil...

**Output:**
```
Exit code: 0
Stdout:
5:smaller vs FP16 faster generation lower energy/token on iPhone
10:2 Efficiency as the Defining Constraint in AI Deployment 4
22:B Benchmark Evaluation Methodology 14
27:B.5 Scoring Methodology . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . . 15
45:Value 1.15 GB footprint, 5–8×faster generation, 4–6×lower energy per token
52:powerful models can be trained, but whether they can be deployed reliably, affordably, and at
53:scale. In modern AI systems, inference dominates real-world cost, energy use, and latency.
54:That makes deployment efficiency—not raw model capability—the defining constraint on pro-
56:This constraint is especially severe on edge hardware. Phones, laptops, robots, and embedded
57:systems operate under hard limits on memory, bandwidth, thermal headroom, battery life, and
74:However,1-bit Bonsai 8B, along with its smaller sister models 1-bit Bonsai 1.7B and 4B,sig-
97:2. Efficiency as the Defining Constraint in AI Deployment
100:only whether highly capable models can be trained, but whether they can be deployed reliably,
101:affordably, and at scale. In production systems, the recurring burden is inference. Every user
102:interaction, agent step, and application call carries latency, energy use, and infrastructure cost.
103:Deployment efficiency has therefore become a primary constraint on real-world AI adoption.
104:This constraint is especially visible on edge hardware. Phones, laptops, robots, wearables, and
105:embedded systems operate within fixed limits on memory, bandwidth, thermal headroom, bat-
107:system must also fit the physical and economic limits of the device on which it runs.
116:strained hardware. The importance of 1-bit is not compression in the abstract. It is its direct
117:effect on the main bottleneck in real inference systems.
126:fluent while becoming materially less dependable on multi-step reasoning, tool use, retrieval,
127:and edge cases. In production, that brittleness is often more damaging than a straightforward
128:accuracy regression because it undermines trust and makes system behavior harder to predict.
130:tion. Many rely on curated calibration sets, auxiliary metadata, custom layer handling, or be-
138:PrismML’s differentiation begins with the method that makes 1-bit language models practical.
139:Although the broader ecosystem for efficient inference has improved, tooling alone does not
151:the LM head. It is not a partially quantized system that depends on higher-precision escape
163:NVIDIA GPUs. The significance of the system is therefore not only that 1-bit works in principle
183:stream inference engines, and optimized kernels spanning the MLX [25] and llama.cpp [13]
185:Table 1.System specification.
218:sign bits are decoded inline inside the matrix-multiplication kernel instead of materializing a
231:per group (scale + bias) instead of one, the effective bits per weight is 1.25 bits/weight which
257:workloads used for energy measurement. For more details of the methodology of throughput
288:regime. However, token generation is substantially faster, so the energy consumed per output
301:Mac power includes CPU + GPU + ANE + DRAM and excludes system overhead. RTX 4090 measurements use GPU
314:and scoring methods to ensure a fair and reproducible comparison. Generation used greedy
319:methodology and fairness efforts, please refer to Appendix B.
349:The benchmark results above motivate a more systematic way of characterizing the tradeoff
386:instruct models in the 1.2B–9B parameter range, together with 1-bit Bonsai 8B and its sister
433:tem constraints. One important class of applications is on-device assistance on Mac, iPhone,
444:The 1-bit Bonsai models are also relevant to edge systems operating under tighter physical
445:constraints, including robotics, autonomy, and embedded inference. In these settings, thermal
448:expands the range of systems that can run useful language-model inference locally. Taken
454:kernel optimization rather than on a native mainstream 1-bit hardware target. Accordingly, they
459:At the same time, the Bonsai methodology is architecture-agnostic and is not tied to a single
466:low-bit inference systems that map cleanly onto different architectures, runtimes, and hardware
473:Although bothllama.cppand Apple’s MLX ecosystem already support several low-bit quantization schemes,
479:Why 1-bit models are faster.Token generation in large language models is typically memory-bandwidth-
484:Because much less data must be fetched from memory for each decoding step, token generation becomes
```

### Thinking

Looking at the whitepaper's discussion around lines 130-140, I can see they're contrasting their approach with standard PTQ methods that rely on curated calibration sets and custom layer handling. The key differentiator seems to be in how PrismML makes 1-bit language models practical, so I need to examine the method description in the 120-165 range to understand what that actually entails.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '108,235p' refs/1-bit-bonsai-8b-whitepaper.txt"
}
```

**Summary:** $ sed -n '108,235p' refs/1-bit-bonsai...

**Output:**
```
Exit code: 0
Stdout:
Memory Bandwidth Is the Real Bottleneck
In LLM inference, especially at small batch sizes, the limiting factor is often not peak arithmetic
throughput but memory movement. Performance depends heavily on how efficiently the sys-
tem can fetch and stream model weights during token generation. For deployment, this makes
memory bandwidth and model footprint central variables, not secondary implementation details.
This is why weight precision matters. Storing parameters at 1 bit per weight, the practical lower
bound for parameter representation, does more than reduce model size. It reduces memory
traffic, lowers energy per token, and improves the feasibility of running strong models on con-
strained hardware. The importance of 1-bit is not compression in the abstract. It is its direct
effect on the main bottleneck in real inference systems.
Why 1-Bit Has Remained Out of Reach
The appeal of binary-weight neural networks has been understood for decades. In principle,
they offer substantial reductions in storage, bandwidth demand, and computational cost. In
practice, those gains have usually come with tradeoffs in quality, applicability, or deployment
complexity.
Recent work on binary-weight Transformers [5, 6] has renewed interest in the 1-bit regime, but
pushing meaningfully below 4-bit precision has remained difficult to make practical for LLMs.
At these levels, the failure mode is often qualitative rather than gradual. A model may remain
fluent while becoming materially less dependable on multi-step reasoning, tool use, retrieval,
and edge cases. In production, that brittleness is often more damaging than a straightforward
accuracy regression because it undermines trust and makes system behavior harder to predict.
Even near-1-bit approaches have often introduced enough operational complexity to limit adop-
tion. Many rely on curated calibration sets, auxiliary metadata, custom layer handling, or be-
spoke runtimes and kernels that do not integrate cleanly with standard inference stacks. That
creates friction exactly where efficiency is supposed to help: deployment across heterogeneous
hardware, integration into existing toolchains, and reliable use without rearchitecting infrastruc-
ture.
4
1-bit Bonsai 8B
3. What Makes PrismML Different
PrismML’s differentiation begins with the method that makes 1-bit language models practical.
Although the broader ecosystem for efficient inference has improved, tooling alone does not
solve the central problem. At extreme compression levels, language models have historically
lost too much of the reasoning quality and behavioral stability that give them value. PrismML’s
approach is based on mathematically grounded advances designed to preserve those properties
under aggressive compression.
This foundation comes from proprietary Caltech intellectual property that addresses a long-
standing research challenge through rigorous mathematics rather than ad hoc heuristics. 1-bit
Bonsai 8B is therefore not a collection of narrow exceptions built for a controlled demonstration.
It is a principled compression framework designed to preserve useful model behavior while
materially lowering the cost of inference.
That differentiation is visible in the deployed model itself. 1-bit Bonsai 8B applies end-to-end
1-bit weight precision across the full network: embeddings, attention layers, MLP layers, and
the LM head. It is not a partially quantized system that depends on higher-precision escape
hatches in the critical path. This matters because such exceptions can preserve quality, but
they also dilute the footprint and bandwidth reductions that make 1-bit valuable in deployment.
The result is an 8B-class model that makes strong on-device inference far more practical. Lower
memory demand and reduced bandwidth pressure translate into concrete deployment advan-
tages, including lower latency, lower energy consumption, smaller footprints, and improved fea-
sibility on edge hardware. These properties also expand the range of applications that can run
locally, especially in settings where privacy, responsiveness, or intermittent connectivity make
cloud dependence undesirable.
Bonsai is designed as a deployment strategy rather than a single-device demonstration. It is
engineered to run across heterogeneous hardware using mainstream backends developers al-
ready use, including Apple MLX [25] for Mac, iPhone, and iPad, and llama.cpp [13] for CUDA on
NVIDIA GPUs. The significance of the system is therefore not only that 1-bit works in principle
but also that it can be deployed across real runtimes, real devices, and real products.
To further demonstrate the potential of 1-bit models, we are also releasing two smaller models
in the Bonsai family: 1-bit Bonsai 4B and 1-bit Bonsai 1.7B. These models extend the same
design philosophy to smaller scales, showing that the advantages of 1-bit quantization are not
limited to a single model size. Despite their compact footprints, both models deliver exception-
ally strong throughput and energy efficiency while maintaining competitive accuracy relative to
their parameter class.
Taken together, the Bonsai family illustrates that 1-bit design is not merely a compression tech-
nique, but a scalable approach to building practical, high-performance models across a range
of deployment regimes. From the 1.7B model through the 8B model, Bonsai demonstrates that
strong capability, efficient execution, and a small memory footprint can be achieved simulta-
neously rather than traded against each other. For the remainder of this manuscript, we focus
primarily on 1-bit Bonsai 8B and the results of 4B and 1.7B are provided in the Appendix.
5
1-bit Bonsai 8B
4. 1-bit Bonsai 8B Model Summary
1-bit Bonsai 8B is built from Qwen3-8B [31], a dense decoder-only causal language model.
The architecture is unchanged: the novelty lies entirely in the deployment stack: End-to-end 1-
bit weight storage for all major matrix-heavy components, an explicit runtime format for main-
stream inference engines, and optimized kernels spanning the MLX [25] and llama.cpp [13]
backends.
Table 1.System specification.
Item
Specification
Architecture modelQwen3-8B [31] dense causal language model
Parameters 8.19 B (∼6.95 B non-embedding); 36 Transformer blocks
ArchitectureGQA [2] (32 query / 8 KV heads), SwiGLU [34] MLP, RoPE [33], RMSNorm [32]
Context length 65,536 tokens
Weight formatsGGUF Q1_0_g128 and MLX 1-bit g128
1-bit weights Embeddings, Attention projections, MLP projections, and LM head
BackendsMLX (Python, Swift) and llama.cpp (CUDA, Metal)
License Apache License
4.1 Deployable 1-bit Format: Q1_0_g128
1-bit Bonsai uses a deployable group-wise 1-bit weight format. In llama.cpp [13] this is pack-
aged as GGUF [12] Q1_0_g128, while MLX [25] uses the corresponding 1-bit g128 represen-
tation. The format stores one sign bit per weight and one shared FP16 scale for each group of
128 weights. This preserves a fundamentally 1-bit representation while retaining the group-
wise magnitude information required for stable inference.
In storage, weights are represented as bitpacked values in{0,1}, using exactly one bit per weight.
At inference time, those bits are mapped to signed values and scaled by the FP16 factor asso-
ciated with their group. The effective weight is therefore given by
wi =s g ·(2b i −1), b i ∈ {0,1}
wheres g is the shared scale for groupg. Because each group of 128 weights carries one FP16
scale, the effective storage cost is
beff = 1 +16
128 = 1.125bits/weight,
which yields an idealized raw-weight compression of16/1.125≈14.2×relative to FP16, before
container overhead and alignment.
Q1_0_g128 is applied uniformly across the large matrix-heavy components of the model, in-
cluding embeddings, attention projections, MLP projections, and the LM head. Normalization
parameters and scale metadata remain in higher precision for numerical stability, but these ac-
count for a negligible share of memory traffic relative to the large weight tensors that dominate
bandwidth during decoding.
The format is designed for direct execution rather than offline expansion. In the inference path,
sign bits are decoded inline inside the matrix-multiplication kernel instead of materializing a
full FP16 weight tensor in memory. This preserves the storage and bandwidth advantages of
1-bit weights where they matter most: the repeated movement of large weight matrices in the
token-by-token decoding path.
6
1-bit Bonsai 8B
MLX 1-bit g128:For MLX we need to pack our model slightly differently which has some extra
overhead. MLX’s quantization formats and kernels generally need both a scale (smlx) and a bias
(bmlx) per group such thatw=s mlx ×b i +b mlx, whereb i ∈ {0,1}. To pack our scale-only 1-bit
weights into this format we use
smlx = 2×s g
bmlx =−s g
This reconstructs−s g whenb i = 0and+s g whenb i = 1. Because MLX stores two FP16 values
per group (scale + bias) instead of one, the effective bits per weight is 1.25 bits/weight which
is slightly higher than the GGUF format. This is a current limitation of MLX, but once it supports
scale-only formats, it should be able to match 1.125 bits/weight which is native to our models.
4.2 Storage Footprint
The deployed size reduction is the first-order consequence of the 1-bit representation. For the
```

### Thinking

They're claiming this is proprietary Caltech IP based on rigorous mathematics rather than ad hoc approaches, and notably they don't rely on curated calibration sets like standard quantization methods do—suggesting this might be something fundamentally different from typical post-training quantization approaches. It's not a new pretraining method either.

The actual technique remains undisclosed, but Michael's hypothesis is that the key innovation might be in how they handle gradient ternarization through clever mathematical formulation. Tracing back through the Hassibi lineage—from Optimal Brain Surgeon through OBC/OBQ to GPTQ—there's a clear ancestral line of pruning and quantization work, and Hassibi's group at Caltech has been active in quantized neural networks research, including work on greedy quantization algorithms and blind quantization approaches.

There's also the sigma-delta quantization framework (Daubechies, Saab) which uses noise shaping—quantizing sequentially while feeding quantization error forward so it gets shaped out of the signal band. GPFQ operates similarly, choosing quantization values to track running error, essentially implementing a first-order sigma-delta quantizer on weights with deterministic, data-driven bounds rather than gradient-based training. This fits Michael's "clever math" description perfectly. The question is whether he's referring to how gradients flow through ternary weights during training (like straight-through estimators), or whether the method itself ternarizes gradients as part of the algorithm.

Given the whitepaper mentions no curated calibration sets, it's probably not GPTQ-style post-training quantization. The two most likely approaches are either pure post-training quantization using error feedback and Hessian-based techniques, or a lightweight quantization-aware training setup with floating-point weights and straight-through estimators. The forward-KL divergence metric (0.0011 nats) was comparing ternary against the model's own FP16 KV-cache baseline, which is a tight comparison. Michael's suggestion points toward examining the actual ternarization mechanism in the paper itself.

Since we have the weights, I can analyze the ternary values directly to reverse-engineer the method. Different ternarization approaches leave statistical fingerprints—TWN uses a threshold based on 0.7 times the mean absolute weight, while BitNet b1.58 uses a different rounding scheme based on mean magnitude. Each produces a distinct distribution of zeros and a specific relationship between original weight magnitudes and their ternary assignments, which would reveal which technique was used. The scale factor could be computed as the mean absolute weight magnitude over the selected support, or via least-squares fitting of weights to ternary values, or it could be learned arbitrarily. This is a forensics experiment to reverse-engineer the ternarization process by comparing the parent FP weights with the ternary child weights we have locally, which directly informs our bridge design since we need to understand whether magnitudes were shifted during QAT—that assumption shapes what gradient descent will do during distillation.

I can predict three scenarios: if ternarization was pure closed-form per-group thresholding, the ternary assignments should deterministically follow from the parent weights with near-zero disagreement; if QAT was used, the latent weights drifted substantially and won't match any simple threshold rule; if it's OBS or GPTQ-style compensation, the disagreement concentrates in later-quantized coordinates and correlates with the Hessian structure. My plan is to report the whitepaper's findings (keeping the method proprietary), ground the approach in the Hassibi lineage—OBS through GPTQ, estimation theory, error-feedback quantization—and then run this weight forensics experiment since we have both parent and child weights available locally.

### Tool Call: web_search (succeeded)


```json
{}
```

**Summary:** Web searching

**Output:**
```
HPCwire - Since 1987 – Covering the Fastest Computers in the World and the People Who Run Them: https://www.hpcwire.com/2026/04/03/prismml-emerges-from-stealth-with-1-bit-llm-family/
Neural Network Quantization with AI Model Efficiency Toolkit (AIMET): https://arxiv.org/pdf/2201.08442
HAWQV3: Dyadic Neural Network Quantization: https://arxiv.org/pdf/2011.10680
(PDF) One-Bit Quantization for Random Features Models: https://www.researchgate.net/publication/396716134_One-Bit_Quantization_for_Random_Features_Models
[1712.05877] Quantization and Training of Neural Networks for Efficient Integer-Arithmetic-Only Inference: https://arxiv.org/abs/1712.05877
[2103.13630] A Survey of Quantization Methods for Efficient Neural Network Inference: https://arxiv.org/abs/2103.13630
A Greedy Algorithm for Quantizing Neural Networks: https://arxiv.org/pdf/2010.15979
On the Universal Approximability and Complexity Bounds of Quantized ReLU   Neural Networks: https://arxiv.org/pdf/1802.03646
Bayesian Bits: Unifying Quantization and Pruning: https://arxiv.org/pdf/2005.07093
```

### Thinking

The training methodology isn't publicly disclosed despite HPCwire's coverage, but Hassibi's background in mathematical theory—particularly Gaussian min-max theorem, universality in linear measurements, H∞ estimation, and regularized regression—suggests the "clever math" likely involves high-dimensional estimation theory applied to quantization.

Notably, Optimal Brain Surgeon traces directly back to Hassibi's 1993 work, so the OBS→GPTQ lineage is his own intellectual lineage. Now I'm planning the forensic approach: since we have both parent and child weights, I can reverse-engineer the ternarization function itself. The whitepaper confirms this is a conversion of Qwen3.6-27B into ternary weights rather than a new pretraining run, and the method appears to be proprietary Caltech IP. Given Hassibi's priors around data-driven per-layer error compensation and calibration-free approaches, I'm structuring the experiment to extract the quantization logic directly from the weight artifacts.

The key is to test whether the scale factors follow closed-form statistics of the parent weights, whether thresholds are consistent per group, and whether any weight flips correlate with quantization order or input covariance—this would reveal whether it's pure mathematical ternarization, OBS-style error compensation, or gradient-based QAT. Comparing zero-fraction statistics against known schemes like TWN and BitNet predictions will discriminate between these approaches without needing the training pipeline.

This matters because if it's pure PTQ, the crystal survival result is even stronger—the topology survived without retraining, suggesting it's an inherent property of the parent's weight distribution rather than something re-optimized during quantization. If QAT was used, the ternary weights were re-learned, which changes how we interpret the crystal-seeded distillation design and the underlying theory.

I have the FP parent weights available—qwen3.6-27b was swept at full precision in earlier sweeps and cached in HuggingFace, plus the unpacked Bonsai model is locally stored. Rather than just proposing, I think I should sketch out the forensics design concretely and ask Michael for a go/no-go, or run a quick single-tensor probe first to show it's feasible and cheap.

## Assistant

The whitepapers are a wall — but the walls have a shape. And the priors around Hassibi are very informative. Here's what we've got:

## What the papers say (and refuse to say)

- The 8B ternary whitepaper is **benchmarks-only**: format (`g128` ternary, FP16 group scales, closed-form b_eff = 1.71), footprint, throughput, energy, intelligence density. The method section doesn't exist.
- The 1-bit whitepaper is where they gesture at it: "proprietary Caltech intellectual property," "rigorous mathematics rather than ad hoc heuristics," and Hassibi's line that "We spent years developing the mathematical theory required to compress a neural network without losing its reasoning capabilities". HPCwire confirms the company attributes its results to a new mathematical framework developed at Caltech, but has not detailed the training methods or stabilization techniques.
- One partial IOU resolution: Bonsai 27B moves Qwen3.6-27B into binary or ternary weights, not a new pretrain. So it's a **conversion**, not BitNet-style from-scratch training. And there's a telling jab in the 1-bit paper: competing methods "rely on curated calibration sets, auxiliary metadata, custom layer handling" — implying theirs *doesn't*.

## The Hassibi priors (why "clever math" is exactly right)

Your hunch has teeth. Babak Hassibi is:
1. **The OBS author** — Optimal Brain Surgeon (Hassibi & Stork, 1993): Hessian-compensated weight removal, `δw = -w_q/[H⁻¹]_qq · H⁻¹e_q`. The literal ancestor of GPTQ. He invented error-compensated compression 30 years before it was cool.
2. **The H∞ estimation guy** — proved LMS/backprop is H∞-optimal. His whole career is "recast a messy adaptive problem as an exactly-solvable estimation problem."
3. **CGMT/universality** — his recent group work is Gaussian min-max theory for high-dimensional constrained regression, universality of linear measurements. That's precisely the toolkit that would tell you *exactly* what a ternary-constrained least-squares layer reconstruction can achieve and how to hit the bound.

So the prior: **per-layer ternary-constrained estimation with closed-form or provably-optimal solvers** — clever math, possibly no gradients anywhere in the pipeline.

## The verbum move: we don't need their code — we have both endpooints

λ extract: the artifact contains the answer. We hold the **FP parent** (Qwen3.6-27B, HF-cached, swept in s266) and the **ternary child** (51G unpacked, rev 427bc0194). The ternarization map `w → (t, s_g)` is a function from parent weights to child weights, and different methods leave **forensically distinct signatures**:

| signature | pure closed-form PTQ (TWN/absmean-style) | OBS/GPTQ-style compensated PTQ | QAT (STE, latent weights drift) |
|---|---|---|---|
| flip rate (t_i ≠ nearest ternary of parent w_i given s_g) | ≈ 0 | small, **structured along quantization order** / input covariance | large, diffuse |
| s_g vs parent group stats | exact closed form (mean\|w\| over support, or ⟨w,t⟩/⟨t,t⟩ least-squares) | near closed form | unexplained by parent stats |
| zero-fraction per group | deterministic fn of threshold rule (e.g. Δ=0.7·E\|w\|) | near-deterministic | free |

Three cheap measurements, streamed tensor-by-tensor from safetensors, no model loading, no GPU. If flip rate is ~0 with a recoverable threshold rule, we've **reverse-engineered the entire method** — and it means no gradients were ternarized because no gradients were ever involved.

And this matters for *our* program, not just curiosity: if it's pure PTQ, then s267's crystal survival is even stronger than we claimed — **nothing was retrained, nothing "healed"; topology survival is a property of the parent's weight distribution alone**. That's the cleanest possible support for your carve-then-fill theory. If it's QAT, survival is partially re-learned and the bridge-map interpretation needs a caveat.

Want me to run the recon (verify both weight sets are on disk, pull one matched tensor pair, measure flip rate + scale closed-form on a single layer)? First signal in minutes, full forensics only if the single-tensor probe is interesting.

## User

Yes, but you can use the gpu to speed it up, no need to make it slow.


### Thinking

Michael's approved the approach with GPU support on Mac using torch 2.11 and MPS. I'm starting with reconnaissance to find the parent Qwen3.6-27B weights in the HuggingFace cache and locate the unpacked bonsai27b safetensors, then I need to verify whether the unpacked format already has the weights materialized as FP16 ternary values or if they're still stored separately.

For the actual probe, I'll load a matched tensor from the middle of the stack (like an MLP down_proj layer), compute per-group scaling factors and ternary values, measure the flip rate against the parent's nearest ternary representation, and test threshold rules with closed-form solutions. I'll start with simple reconnaissance commands to check the file structure, then write a focused single-tensor probe script to gather real measurements before deciding whether to formalize further.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/localai/models/bonsai27b-unpacked/ | head -20; echo ---; ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -i \"qwen3\" ; echo ---; python3 -c \"import glob,os; print([p for p in glob.glob(os.path.expanduser('~/.cache/huggingface/hub/models--*Qwen*/snapshots/*/')) ])\" 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/localai/models/...

**Output:**
```
Exit code: 0
Stdout:
chat_template.jinja
config.json
configuration.json
finished.txt
generation_config.json
LICENSE
LICENSE.txt
merges.txt
model-00001-of-00012.safetensors
model-00002-of-00012.safetensors
model-00003-of-00012.safetensors
model-00004-of-00012.safetensors
model-00005-of-00012.safetensors
model-00006-of-00012.safetensors
model-00007-of-00012.safetensors
model-00008-of-00012.safetensors
model-00009-of-00012.safetensors
model-00010-of-00012.safetensors
model-00011-of-00012.safetensors
model-00012-of-00012.safetensors
---
models--mlx-community--Qwen3-Embedding-4B-4bit-DWQ
models--Qwen--Qwen3-0.6B
models--Qwen--Qwen3-14B
models--Qwen--Qwen3-235B-A22B
models--Qwen--Qwen3-30B-A3B
models--Qwen--Qwen3-32B
models--Qwen--Qwen3-4B
models--Qwen--Qwen3-8B
models--Qwen--Qwen3-8B-Base
models--Qwen--Qwen3.5-35B-A3B
models--Qwen--Qwen3.6-27B
models--Qwen--Qwen3.6-35B-A3B
models--unsloth--Qwen3-Coder-480B-A35B-Instruct-GGUF
---
['/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-35B-A3B/snapshots/995ad96eacd98c81ed38be0c5b274b04031597b0/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9/', '/Users/mwhitford/.cache/huggingface/hub/models--unsloth--Qwen3-Coder-480B-A35B-Instruct-GGUF/snapshots/1f1226bc3715f0b5973f2307c1a8e02137ef2a06/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-30B-A3B/snapshots/ad44e777bcd18fa416d9da3bd8f70d33ebb85d39/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.5-35B-A3B/snapshots/59d61f3ce65a6d9863b86d2e96597125219dc754/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-4B/snapshots/1cfa9a7208912126459214e8b04321603b3df60c/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen2.5-0.5B/snapshots/060db6499f32faf8b98477b0a26969ef7d8b9987/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-235B-A22B/snapshots/8efa61729e24bd65b1d152b5ab5409052aa80e65/', '/Users/mwhitford/.cache/huggingface/hub/models--mlx-community--Qwen3-Embedding-4B-4bit-DWQ/snapshots/b5d88f1fe49b50d2ac01b4692ca2d387f14f9c72/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-8B/snapshots/b968826d9c46dd6066d109eabc6255188de91218/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-0.6B/snapshots/c1899de289a04d12100db370d81485cdf75e47ca/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-14B/snapshots/40c069824f4251a91eefaf281ebe4c544efd3e18/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-32B/snapshots/9216db5781bf21249d130ec9da846c4624c16137/', '/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3-8B-Base/snapshots/49e3418fbbbca6ecbdf9608b4d22e5a407081db4/']
```

### Thinking

I've got both the parent model from the Hugging Face cache and the unpacked child version with its 12 safetensors shards ready to compare. Now I need to check the config.json and inspect a tensor to confirm the unpacked format is using FP16 with quantized values in the expected range, then select a mid-stack down_proj tensor around 50% depth to verify the structure.

Writing a reconnaissance script...

### Thinking

Both endpoints are on disk with the parent snapshot and child 12-shard unpacked. Now I'll verify the unpacked format materializes the expected values and that tensor names match the parent.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json, glob\nfrom safetensors import safe_open\n\nbonsai = '/Users/mwhitford/localai/models/bonsai27b-unpacked'\nparent = glob.glob('/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/')[0]\nprint('parent files:', [f.split('/')[-1] for f in sorted(glob.glob(parent+'*.safetensors'))][:4], '...')\n\ncfg = json.load(open(bonsai+'/config.json'))\nprint('bonsai config keys:', list(cfg.keys()))\nprint('quant cfg:', json.dumps(cfg.get('quantization_config', cfg.get('quantization', 'NONE')))[:400])\n\nimport torch\nf = safe_open(bonsai+'/model-00006-of-00012.safetensors','pt')\nnames = list(f.keys())\nprint('n tensors in shard6:', len(names)); print('sample names:', names[:6])\n# pick an MLP down_proj if present\ncand = [n for n in names if 'down_proj' in n][:1] or names[:1]\nt = f.get_tensor(cand[0])\nprint(cand[0], t.shape, t.dtype)\nrow = t[0,:256].float()\ng = row[:128]\nu = torch.unique(g)\nprint('unique vals in first group of 128:', u.tolist()[:10], '(count:', len(u), ')')\ng2 = row[128:256]; u2 = torch.unique(g2)\nprint('unique vals in second group:', u2.tolist()[:10], '(count:', len(u2), ')')\n\""
}
```

**Summary:** $ uv run python -c " import json, glo...

**Output:**
```
Exit code: 0
Stdout:
parent files: ['model-00001-of-00015.safetensors', 'model-00002-of-00015.safetensors', 'model-00003-of-00015.safetensors', 'model-00004-of-00015.safetensors'] ...
bonsai config keys: ['architectures', 'image_token_id', 'language_model_only', 'model_type', 'text_config', 'tie_word_embeddings', 'transformers_version', 'video_token_id', 'vision_config', 'vision_end_token_id', 'vision_start_token_id']
quant cfg: "NONE"
n tensors in shard6: 82
sample names: ['model.language_model.layers.29.mlp.gate_proj.weight', 'model.language_model.layers.29.mlp.up_proj.weight', 'model.language_model.layers.29.post_attention_layernorm.weight', 'model.language_model.layers.3.input_layernorm.weight', 'model.language_model.layers.3.mlp.down_proj.weight', 'model.language_model.layers.3.mlp.gate_proj.weight']
model.language_model.layers.3.mlp.down_proj.weight torch.Size([5120, 17408]) torch.bfloat16
unique vals in first group of 128: [-0.00775146484375, 0.0, 0.00775146484375] (count: 3 )
unique vals in second group: [-0.00830078125, 0.0, 0.00830078125] (count: 3 )
```

### Thinking

The unpacked format confirms a ternary structure with exactly three values per group of 128 along the input dimension, letting me recover both the sign and magnitude precisely. I need to pick a mid-depth tensor from the model—Qwen3.6-27B likely has around 64 layers—and check the parent index to understand the tensor naming scheme.

For the single-tensor probe, I'll load both the parent weights and quantized child weights in float32 on MPS, then run several tests: measure how often the nearest-ternary reconstruction flips the sign compared to the original, check whether a threshold rule can perfectly separate zero from nonzero entries per group, and compare the learned scale against both the mean magnitude of the support and the least-squares optimal scale.

I'm planning to write a reusable script that takes tensor names or auto-selects a spread across different depths, runs these diagnostics on MPS, and outputs the signatures—zero fraction, threshold ratio, sign agreement—to distinguish pure threshold quantization from compensated or QAT approaches.

### Thinking

I've confirmed the format recovers the ternary values losslessly from the sign and magnitude, and the naming structure checks out. Now I'll write a script to probe the data using MPS acceleration, starting with a single mid-stack tensor.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "content": "\"\"\"Bonsai ternarization forensics: reverse-engineer the parent→ternary map.\n\nWe hold both endpoints of PrismML's (undisclosed) ternarization:\n  parent: Qwen/Qwen3.6-27B (FP bf16, HF cache)\n  child:  bonsai27b-unpacked (materialized ternary: {-s_g, 0, +s_g} per group of 128)\n\nMethod signatures (per tensor, per group g of 128 along in_features):\n  s_g   = max|w_q|                 (exact, by construction of unpacked format)\n  t     = sign(w_q)                (exact)\n\n  1. flip_rate      — fraction where t != nearest-ternary(parent w | s_g)\n                      (nearest at threshold s_g/2).  ~0 => no error compensation,\n                      no QAT drift.  structured/large => compensated PTQ or QAT.\n  2. sign_viol      — fraction where t != 0 and sign(t) != sign(parent w).\n                      >0 => weights crossed zero => training/compensation.\n  3. sep_rate       — fraction of groups where a threshold Delta_g exists with\n                      t = sign(w) * [|w| > Delta_g] EXACTLY\n                      (max|w| over t=0  <  min|w| over t!=0).\n                      1.0 => pure magnitude-threshold rule on parent weights.\n  4. scale closed forms — corr(s_g, mean|w| over support)  [TWN-optimal scale]\n                          corr(s_g, <w,t>/<t,t>)           [least-squares scale]\n                          ratio distributions.\n  5. threshold ratio — Delta_g / mean|w|_g  (TWN predicts ~0.7; absmean predicts\n                          a different constant; learned thresholds => spread).\n\nUsage:\n  uv run python scripts/bonsai_forensics.py --tensors auto --depths 0.1 0.3 0.5 0.7 0.9\n  uv run python scripts/bonsai_forensics.py --tensors model.layers.32.mlp.down_proj.weight\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport glob\nimport json\nimport time\nfrom pathlib import Path\n\nimport torch\nfrom safetensors import safe_open\n\nBONSAI_DIR = Path(\"/Users/mwhitford/localai/models/bonsai27b-unpacked\")\nPARENT_GLOB = \"/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/\"\nGROUP = 128\nDEVICE = \"mps\" if torch.backends.mps.is_available() else \"cpu\"\n\n\ndef build_index(model_dir: Path) -> dict[str, Path]:\n    \"\"\"tensor name -> shard path, from safetensors index or by scanning.\"\"\"\n    idx_file = model_dir / \"model.safetensors.index.json\"\n    if idx_file.exists():\n        idx = json.load(open(idx_file))[\"weight_map\"]\n        return {k: model_dir / v for k, v in idx.items()}\n    out: dict[str, Path] = {}\n    for shard in sorted(model_dir.glob(\"*.safetensors\")):\n        with safe_open(shard, \"pt\") as f:\n            for k in f.keys():\n                out[k] = shard\n    return out\n\n\ndef load_tensor(index: dict[str, Path], name: str) -> torch.Tensor:\n    with safe_open(index[name], \"pt\") as f:\n        return f.get_tensor(name)\n\n\ndef forensics_one(w: torch.Tensor, wq: torch.Tensor) -> dict:\n    \"\"\"All signatures for one (parent, child) tensor pair. Runs on DEVICE.\"\"\"\n    assert w.shape == wq.shape, (w.shape, wq.shape)\n    out_f, in_f = w.shape\n    n_groups_row = in_f // GROUP\n\n    w = w.to(DEVICE, torch.float32).reshape(out_f, n_groups_row, GROUP)\n    wq = wq.to(DEVICE, torch.float32).reshape(out_f, n_groups_row, GROUP)\n\n    s = wq.abs().amax(dim=-1, keepdim=True)                     # (out, ng, 1)\n    t = torch.sign(wq)                                          # exact ternary code\n    nz = t != 0\n    n = w.numel()\n\n    # -- 1. flip rate vs nearest-ternary of parent given s\n    live = s.squeeze(-1) > 0                                    # groups with any support\n    t_nn = torch.sign(w) * (w.abs() > (s / 2))\n    flips = (t != t_nn) & live.unsqueeze(-1)\n    flip_rate = flips.float().mean().item()\n\n    # -- 2. sign violations on support\n    sign_viol = ((nz) & (torch.sign(w) != t)).float().sum().item() / max(nz.sum().item(), 1)\n\n    # -- 3. exact threshold separability per group\n    big = torch.finfo(torch.float32).max\n    absw = w.abs()\n    max_zero = torch.where(~nz, absw, torch.zeros_like(absw)).amax(dim=-1)      # (out, ng)\n    min_nonzero = torch.where(nz, absw, torch.full_like(absw, big)).amin(dim=-1)\n    has_zero = (~nz).any(dim=-1)\n    has_nonzero = nz.any(dim=-1)\n    mixed = has_zero & has_nonzero\n    sep = torch.ones_like(max_zero, dtype=torch.bool)\n    sep[mixed] = max_zero[mixed] < min_nonzero[mixed]\n    sep_rate = sep.float().mean().item()\n\n    # implied threshold per mixed group (midpoint), ratio to mean|w|\n    delta = (max_zero + torch.where(mixed, min_nonzero, max_zero)) / 2\n    mean_abs = absw.mean(dim=-1)\n    delta_ratio = (delta[mixed] / mean_abs[mixed])\n\n    # -- 4. scale closed forms (per group, over support)\n    supp_cnt = nz.sum(dim=-1).clamp(min=1)\n    s_twn = (absw * nz).sum(dim=-1) / supp_cnt                  # mean |w| over support\n    s_ls = (w * t).sum(dim=-1) / supp_cnt                       # <w,t>/<t,t>\n    s_flat = s.squeeze(-1)\n    m = live & has_nonzero\n\n    def corr(a: torch.Tensor, b: torch.Tensor) -> float:\n        a = a[m].flatten().double()\n        b = b[m].flatten().double()\n        a = a - a.mean(); b = b - b.mean()\n        return (a @ b / (a.norm() * b.norm() + 1e-30)).item()\n\n    ratio_twn = (s_flat[m] / s_twn[m])\n\n    # -- 5. zero fraction\n    zero_frac = (~nz).float().mean().item()\n\n    q = lambda x, p: torch.quantile(x.float(), p).item() if x.numel() else float(\"nan\")\n    return {\n        \"n_params\": n,\n        \"flip_rate\": flip_rate,\n        \"n_flips\": int(flips.sum().item()),\n        \"sign_viol_rate\": sign_viol,\n        \"sep_rate\": sep_rate,\n        \"zero_frac\": zero_frac,\n        \"corr_s_twn\": corr(s_flat, s_twn),\n        \"corr_s_ls\": corr(s_flat, s_ls),\n        \"s_over_twn_q25_50_75\": [q(ratio_twn, p) for p in (0.25, 0.5, 0.75)],\n        \"delta_over_meanabs_q25_50_75\": [q(delta_ratio, p) for p in (0.25, 0.5, 0.75)],\n    }\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--tensors\", nargs=\"+\", default=[\"auto\"])\n    ap.add_argument(\"--depths\", nargs=\"+\", type=float, default=[0.5])\n    ap.add_argument(\"--out\", default=None, help=\"write JSON here\")\n    args = ap.parse_args()\n\n    parent_dir = Path(glob.glob(PARENT_GLOB)[0])\n    print(f\"device={DEVICE}  parent={parent_dir.name}  child={BONSAI_DIR.name}\")\n    t0 = time.time()\n    child_idx = build_index(BONSAI_DIR)\n    parent_idx = build_index(parent_dir)\n    print(f\"indexed: child={len(child_idx)} parent={len(parent_idx)} tensors \"\n          f\"({time.time()-t0:.1f}s)\")\n\n    # child names carry the VLM wrapper prefix\n    def to_parent(name: str) -> str:\n        return name.replace(\"model.language_model.\", \"model.\")\n\n    layer_ids = sorted({int(k.split(\".layers.\")[1].split(\".\")[0])\n                        for k in child_idx if \".layers.\" in k})\n    n_layers = len(layer_ids)\n\n    if args.tensors == [\"auto\"]:\n        names = []\n        for d in args.depths:\n            lid = layer_ids[min(int(d * n_layers), n_layers - 1)]\n            for proj in (\"mlp.down_proj\", \"mlp.gate_proj\", \"self_attn.q_proj\",\n                         \"self_attn.o_proj\"):\n                cand = f\"model.language_model.layers.{lid}.{proj}.weight\"\n                if cand in child_idx:\n                    names.append(cand)\n    else:\n        names = [n if n in child_idx\n                 else \"model.language_model.\" + n.removeprefix(\"model.\")\n                 for n in args.tensors]\n\n    print(f\"n_layers={n_layers}  probing {len(names)} tensors\\n\")\n    results = {}\n    for name in names:\n        pname = to_parent(name)\n        if pname not in parent_idx:\n            print(f\"SKIP {name}: parent tensor {pname} not found\")\n            continue\n        t0 = time.time()\n        r = forensics_one(load_tensor(parent_idx, pname), load_tensor(child_idx, name))\n        r[\"elapsed_s\"] = round(time.time() - t0, 2)\n        results[name] = r\n        print(f\"{name}\")\n        print(f\"  flip_rate={r['flip_rate']:.3e} ({r['n_flips']} flips / {r['n_params']:,})\"\n              f\"  sign_viol={r['sign_viol_rate']:.3e}  sep_rate={r['sep_rate']:.4f}\")\n        print(f\"  zero_frac={r['zero_frac']:.3f}  corr(s,twn)={r['corr_s_twn']:.4f}\"\n              f\"  corr(s,ls)={r['corr_s_ls']:.4f}\")\n        print(f\"  s/twn q25-75={['%.3f' % x for x in r['s_over_twn_q25_50_75']]}\"\n              f\"  Δ/mean|w| q25-75={['%.3f' % x for x in r['delta_over_meanabs_q25_50_75']]}\"\n              f\"  ({r['elapsed_s']}s)\\n\")\n\n    if args.out:\n        Path(args.out).parent.mkdir(parents=True, exist_ok=True)\n        json.dump({\"device\": DEVICE, \"group\": GROUP, \"results\": results},\n                  open(args.out, \"w\"), indent=2)\n        print(f\"wrote {args.out}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.5 2>&1 | tail -20",
  "timeout": 300000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
device=mps  parent=6a9e13bd6fc8f0983b9b99948120bc37f49c13e9  child=bonsai27b-unpacked
indexed: child=1184 parent=1199 tensors (0.0s)
n_layers=64  probing 2 tensors

SKIP model.language_model.layers.32.mlp.down_proj.weight: parent tensor model.layers.32.mlp.down_proj.weight not found
SKIP model.language_model.layers.32.mlp.gate_proj.weight: parent tensor model.layers.32.mlp.gate_proj.weight not found
```

### Thinking

The parent tensor names are mismatched — Qwen3.6-27B uses a hybrid architecture with different module naming conventions, possibly including structures like linear_attn or expert layers in the MLP sections. I should examine what the actual parent tensor names look like for layer 32 to understand the discrepancy.

## Assistant

Name scheme mismatch on the parent side — it's the hybrid architecture. Inspecting:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json, glob\np = glob.glob('/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/')[0]\nidx = json.load(open(p+'model.safetensors.index.json'))['weight_map']\nl32 = sorted(k for k in idx if '.layers.32.' in k)\nprint('\\n'.join(l32))\nprint('---')\nimport collections\nprefixes = collections.Counter(k.split('.layers.')[0] for k in idx if '.layers.' in k)\nprint(prefixes)\n\" 2>&1 | head -30"
}
```

**Summary:** $ uv run python -c " import json, glo...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.layers.32.input_layernorm.weight
model.language_model.layers.32.linear_attn.A_log
model.language_model.layers.32.linear_attn.conv1d.weight
model.language_model.layers.32.linear_attn.dt_bias
model.language_model.layers.32.linear_attn.in_proj_a.weight
model.language_model.layers.32.linear_attn.in_proj_b.weight
model.language_model.layers.32.linear_attn.in_proj_qkv.weight
model.language_model.layers.32.linear_attn.in_proj_z.weight
model.language_model.layers.32.linear_attn.norm.weight
model.language_model.layers.32.linear_attn.out_proj.weight
model.language_model.layers.32.mlp.down_proj.weight
model.language_model.layers.32.mlp.gate_proj.weight
model.language_model.layers.32.mlp.up_proj.weight
model.language_model.layers.32.post_attention_layernorm.weight
---
Counter({'model.language_model': 848, 'mtp': 11})
```

### Thinking

The parent model uses the same `model.language_model.` prefix, so there's no need for a mapping between them. My `to_parent()` function was breaking things — I should make it an identity mapping instead. I'm also noticing this is a hybrid architecture where layer 32 uses linear attention without the standard self-attention projections, so I need to adjust the auto-selection logic to check which projections actually exist rather than assuming a standard structure.

Updating the script now...

### Thinking

I found that the parent model uses the same prefix and has a hybrid architecture with a Mamba-style linear attention layer at position 32 instead of standard self-attention, so I'm updating the mapping and expanding the projection candidates to account for this.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    # child names carry the VLM wrapper prefix\n    def to_parent(name: str) -> str:\n        return name.replace(\"model.language_model.\", \"model.\")\n",
  "new_content": "    # parent (Qwen3.6-27B) is also VLM-wrapped: names are identical\n    def to_parent(name: str) -> str:\n        return name\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "            for proj in (\"mlp.down_proj\", \"mlp.gate_proj\", \"self_attn.q_proj\",\n                         \"self_attn.o_proj\"):",
  "new_content": "            for proj in (\"mlp.down_proj\", \"mlp.gate_proj\", \"self_attn.q_proj\",\n                         \"self_attn.o_proj\", \"linear_attn.in_proj_qkv\",\n                         \"linear_attn.out_proj\"):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.5 2>&1 | tail -25",
  "timeout": 300000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
device=mps  parent=6a9e13bd6fc8f0983b9b99948120bc37f49c13e9  child=bonsai27b-unpacked
indexed: child=1184 parent=1199 tensors (0.0s)
n_layers=64  probing 4 tensors

Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 206, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 186, in main
    r = forensics_one(load_tensor(parent_idx, pname), load_tensor(child_idx, name))
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 133, in forensics_one
    "corr_s_twn": corr(s_flat, s_twn),
                  ^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 115, in corr
    a = a[m].flatten().double()
        ^^^^^^^^^^^^^^^^^^^^^^^
TypeError: Cannot convert a MPS Tensor to float64 dtype as the MPS framework doesn't support float64. Please use float32 instead.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        a = a[m].flatten().double()\n        b = b[m].flatten().double()",
  "new_content": "        a = a[m].flatten().float()\n        b = b[m].flatten().float()"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.5 2>&1 | tail -25",
  "timeout": 300000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
device=mps  parent=6a9e13bd6fc8f0983b9b99948120bc37f49c13e9  child=bonsai27b-unpacked
indexed: child=1184 parent=1199 tensors (0.0s)
n_layers=64  probing 4 tensors

model.language_model.layers.32.mlp.down_proj.weight
  flip_rate=1.799e-01 (16034655 flips / 89,128,960)  sign_viol=2.235e-02  sep_rate=0.0000
  zero_frac=0.298  corr(s,twn)=0.9704  corr(s,ls)=0.9697
  s/twn q25-75=['0.808', '0.829', '0.852']  Δ/mean|w| q25-75=['0.438', '0.477', '0.525']  (1.65s)

model.language_model.layers.32.mlp.gate_proj.weight
  flip_rate=1.757e-01 (15658653 flips / 89,128,960)  sign_viol=2.225e-02  sep_rate=0.0001
  zero_frac=0.294  corr(s,twn)=0.9399  corr(s,ls)=0.9390
  s/twn q25-75=['0.811', '0.834', '0.859']  Δ/mean|w| q25-75=['0.442', '0.486', '0.530']  (0.17s)

model.language_model.layers.32.linear_attn.in_proj_qkv.weight
  flip_rate=7.904e-02 (4144218 flips / 52,428,800)  sign_viol=3.344e-03  sep_rate=0.0190
  zero_frac=0.310  corr(s,twn)=0.9303  corr(s,ls)=0.9279
  s/twn q25-75=['0.766', '0.786', '0.807']  Δ/mean|w| q25-75=['0.381', '0.434', '0.485']  (0.88s)

model.language_model.layers.32.linear_attn.out_proj.weight
  flip_rate=1.072e-01 (3371353 flips / 31,457,280)  sign_viol=7.869e-03  sep_rate=0.0032
  zero_frac=0.304  corr(s,twn)=0.9851  corr(s,ls)=0.9848
  s/twn q25-75=['0.777', '0.797', '0.818']  Δ/mean|w| q25-75=['0.382', '0.430', '0.482']  (0.33s)
```

### Thinking

The first signal shows strong evidence of genuine weight drift rather than simple rounding—flip rates between 8–18% are too high for that, and sign violations at 0.3–2.2% indicate weights actually crossed their signs relative to the parent, which points to real quantization compensation or fine-tuning effects. The separation rate stays near zero, so there's no clean magnitude threshold at play, but the correlation between the signal and the target weight is remarkably high at 0.93+, suggesting this drift is systematic and predictable.

What's striking is the scale ratio: the quantized scale is about 0.79–0.85 times the theoretically optimal scale, which is consistent with either QAT-induced drift (where latent weights migrate toward their quantized values) or deliberate shrinkage—possibly even an estimation-theoretic effect like Wiener-style shrinkage under noise assumptions. That ~17% reduction in scale relative to the parent's LS-optimal reconstruction is too consistent to be random. To distinguish whether this came from QAT or compensated post-training quantization, I'd expect QAT flips to be diffuse and uncorrelated with column order, whereas compensated PTQ would show more structure. I should measure flip rates across column indices to detect GPTQ-style sequential compensation, check whether flipped weights cluster near the decision boundary, and examine how flip rates vary by layer depth to see if they correlate with the loss landscape. The MLP layers showing ~18% flips versus attention's 8-11% is already suggestive—I need to sweep the full depth profile and generate a JSON summary of these metrics.

### Thinking

I've found that the ternary code isn't pure rounding—flip rates hit 8–18% with sign violations up to 2.2%—but it's strongly anchored to the parent weights with a systematic shrinkage pattern. Now I'll use two discriminators (flip rate vs. column position, and flip proximity to the decision boundary) to separate QAT-drift from sequential compensation effects across different depths.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    # -- 5. zero fraction\n    zero_frac = (~nz).float().mean().item()\n",
  "new_content": "    # -- 5. zero fraction\n    zero_frac = (~nz).float().mean().item()\n\n    # -- 6. flip locality: rate per column-block along in_features (GPTQ-style\n    #       sequential compensation accumulates error along quantization order;\n    #       QAT drift is diffuse/flat)\n    n_blocks = 16\n    fpb = flips.reshape(out_f, -1).float()          # (out, in_f)\n    fpb = fpb.reshape(out_f, n_blocks, in_f // n_blocks).mean(dim=(0, 2))\n    flip_col_profile = [round(x, 5) for x in fpb.tolist()]\n\n    # -- 7. flip boundary distance: |w|/s at flip sites. Boundary-hugging\n    #       (~0.5) => tiny perturbations suffice; broad => genuine drift.\n    rel = (absw / s.clamp(min=1e-30))[flips]\n    flip_boundary_q = [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)] if flips.any() else []\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Thinking

I see the issue — q is being used before it's defined in the function. I need to move the q definition earlier in the code, before the block that references it, and then make sure to add those new fields to the return dictionary and include the necessary print statements.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    live = s.squeeze(-1) > 0                                    # groups with any support\n",
  "new_content": "    q = lambda x, p: torch.quantile(x.float(), p).item() if x.numel() else float(\"nan\")\n    live = s.squeeze(-1) > 0                                    # groups with any support\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    q = lambda x, p: torch.quantile(x.float(), p).item() if x.numel() else float(\"nan\")\n    return {",
  "new_content": "    return {"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        \"s_over_twn_q25_50_75\": [q(ratio_twn, p) for p in (0.25, 0.5, 0.75)],\n        \"delta_over_meanabs_q25_50_75\": [q(delta_ratio, p) for p in (0.25, 0.5, 0.75)],\n    }",
  "new_content": "        \"s_over_twn_q25_50_75\": [q(ratio_twn, p) for p in (0.25, 0.5, 0.75)],\n        \"delta_over_meanabs_q25_50_75\": [q(delta_ratio, p) for p in (0.25, 0.5, 0.75)],\n        \"flip_col_profile\": flip_col_profile,\n        \"flip_boundary_q05_25_50_75_95\": flip_boundary_q,\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        print(f\"  s/twn q25-75={['%.3f' % x for x in r['s_over_twn_q25_50_75']]}\"\n              f\"  Δ/mean|w| q25-75={['%.3f' % x for x in r['delta_over_meanabs_q25_50_75']]}\"\n              f\"  ({r['elapsed_s']}s)\\n\")",
  "new_content": "        print(f\"  s/twn q25-75={['%.3f' % x for x in r['s_over_twn_q25_50_75']]}\"\n              f\"  Δ/mean|w| q25-75={['%.3f' % x for x in r['delta_over_meanabs_q25_50_75']]}\")\n        print(f\"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}\")\n        print(f\"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}\"\n              f\"  ({r['elapsed_s']}s)\\n\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.1 0.3 0.5 0.7 0.9 --out results/bonsai-forensics/forensics_depthsweep.json 2>&1 | tail -60",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
flip_col_profile=['0.137', '0.107', '0.115', '0.119', '0.101', '0.114', '0.081', '0.099', '0.109', '0.096', '0.093', '0.122', '0.105', '0.095', '0.106', '0.114']
  flip |w|/s q05-95=['0.095', '0.325', '0.463', '0.562', '0.750']  (0.07s)

model.language_model.layers.44.mlp.down_proj.weight
  flip_rate=1.716e-01 (15290777 flips / 89,128,960)  sign_viol=1.974e-02  sep_rate=0.0000
  zero_frac=0.297  corr(s,twn)=0.9631  corr(s,ls)=0.9630
  s/twn q25-75=['0.806', '0.828', '0.850']  Δ/mean|w| q25-75=['0.430', '0.468', '0.512']
  flip_col_profile=['0.174', '0.173', '0.174', '0.173', '0.173', '0.173', '0.173', '0.173', '0.172', '0.171', '0.172', '0.169', '0.168', '0.169', '0.169', '0.169']
  flip |w|/s q05-95=['0.063', '0.272', '0.450', '0.603', '0.820']  (0.19s)

model.language_model.layers.44.mlp.gate_proj.weight
  flip_rate=1.568e-01 (13972671 flips / 89,128,960)  sign_viol=1.895e-02  sep_rate=0.0004
  zero_frac=0.293  corr(s,twn)=0.9537  corr(s,ls)=0.9527
  s/twn q25-75=['0.806', '0.829', '0.853']  Δ/mean|w| q25-75=['0.421', '0.465', '0.510']
  flip_col_profile=['0.152', '0.151', '0.150', '0.157', '0.161', '0.161', '0.159', '0.160', '0.161', '0.161', '0.163', '0.162', '0.159', '0.151', '0.150', '0.151']
  flip |w|/s q05-95=['0.062', '0.267', '0.441', '0.584', '0.812']  (0.18s)

model.language_model.layers.44.linear_attn.in_proj_qkv.weight
  flip_rate=6.134e-02 (3216031 flips / 52,428,800)  sign_viol=2.708e-03  sep_rate=0.0457
  zero_frac=0.311  corr(s,twn)=0.9465  corr(s,ls)=0.9452
  s/twn q25-75=['0.764', '0.784', '0.803']  Δ/mean|w| q25-75=['0.392', '0.456', '0.501']
  flip_col_profile=['0.058', '0.056', '0.055', '0.062', '0.065', '0.064', '0.063', '0.064', '0.065', '0.065', '0.066', '0.066', '0.064', '0.057', '0.055', '0.056']
  flip |w|/s q05-95=['0.139', '0.379', '0.472', '0.529', '0.638']  (0.11s)

model.language_model.layers.44.linear_attn.out_proj.weight
  flip_rate=8.971e-02 (2821919 flips / 31,457,280)  sign_viol=4.387e-03  sep_rate=0.0062
  zero_frac=0.308  corr(s,twn)=0.9750  corr(s,ls)=0.9749
  s/twn q25-75=['0.772', '0.792', '0.811']  Δ/mean|w| q25-75=['0.385', '0.432', '0.483']
  flip_col_profile=['0.051', '0.091', '0.095', '0.099', '0.093', '0.092', '0.092', '0.086', '0.106', '0.107', '0.066', '0.105', '0.085', '0.099', '0.079', '0.089']
  flip |w|/s q05-95=['0.115', '0.348', '0.468', '0.552', '0.692']  (0.08s)

model.language_model.layers.57.mlp.down_proj.weight
  flip_rate=1.697e-01 (15126087 flips / 89,128,960)  sign_viol=2.129e-02  sep_rate=0.0000
  zero_frac=0.291  corr(s,twn)=0.9658  corr(s,ls)=0.9655
  s/twn q25-75=['0.812', '0.834', '0.858']  Δ/mean|w| q25-75=['0.423', '0.462', '0.511']
  flip_col_profile=['0.176', '0.175', '0.175', '0.174', '0.173', '0.173', '0.173', '0.172', '0.173', '0.171', '0.172', '0.165', '0.160', '0.162', '0.160', '0.160']
  flip |w|/s q05-95=['0.061', '0.264', '0.440', '0.590', '0.805']  (0.18s)

model.language_model.layers.57.mlp.gate_proj.weight
  flip_rate=1.177e-01 (10486123 flips / 89,128,960)  sign_viol=1.051e-02  sep_rate=0.0012
  zero_frac=0.290  corr(s,twn)=0.9388  corr(s,ls)=0.9368
  s/twn q25-75=['0.799', '0.821', '0.846']  Δ/mean|w| q25-75=['0.384', '0.426', '0.472']
  flip_col_profile=['0.111', '0.111', '0.109', '0.119', '0.122', '0.122', '0.121', '0.123', '0.123', '0.122', '0.124', '0.123', '0.121', '0.111', '0.110', '0.111']
  flip |w|/s q05-95=['0.075', '0.289', '0.439', '0.543', '0.713']  (0.17s)

model.language_model.layers.57.linear_attn.in_proj_qkv.weight
  flip_rate=3.619e-02 (1897222 flips / 52,428,800)  sign_viol=1.793e-03  sep_rate=0.2097
  zero_frac=0.308  corr(s,twn)=0.9574  corr(s,ls)=0.9564
  s/twn q25-75=['0.760', '0.779', '0.798']  Δ/mean|w| q25-75=['0.440', '0.488', '0.507']
  flip_col_profile=['0.034', '0.034', '0.033', '0.037', '0.038', '0.038', '0.037', '0.038', '0.038', '0.038', '0.039', '0.038', '0.039', '0.034', '0.033', '0.034']
  flip |w|/s q05-95=['0.158', '0.411', '0.478', '0.507', '0.602']  (0.11s)

model.language_model.layers.57.linear_attn.out_proj.weight
  flip_rate=7.047e-02 (2216879 flips / 31,457,280)  sign_viol=3.166e-03  sep_rate=0.0113
  zero_frac=0.308  corr(s,twn)=0.9480  corr(s,ls)=0.9480
  s/twn q25-75=['0.764', '0.783', '0.802']  Δ/mean|w| q25-75=['0.383', '0.439', '0.494']
  flip_col_profile=['0.074', '0.036', '0.076', '0.078', '0.102', '0.090', '0.073', '0.086', '0.055', '0.047', '0.029', '0.082', '0.080', '0.064', '0.074', '0.083']
  flip |w|/s q05-95=['0.123', '0.365', '0.473', '0.541', '0.672']  (0.08s)

wrote results/bonsai-forensics/forensics_depthsweep.json
```

### Thinking

Looking at the JSON patterns across the shallower layers, I'm noticing that flip_col_profile stays flat with no column-wise accumulation, which rules out the standard GPTQ sequential compensation approach—this points more toward QAT-style drift or non-sequential optimization instead. The flip magnitude-to-scale ratio clusters around 0.44-0.47 with a spread ranging from 0.06 to 0.82, suggesting a fairly concentrated distribution with some outliers.

The depth progression is revealing: linear attention (routing/QKV) shows fewer flips than MLP layers, which is counterintuitive but suggests the routing topology stayed more stable while the value path underwent more rewiring. Meanwhile, the separation rate climbs steeply in later in_proj_qkv layers (0.019 → 0.046 → 0.21), indicating those late attention layers are approaching pure threshold behavior.

To nail down whether this is QAT, I need to compute the correlation between parent weights and dequantized child weights independent of the ternary structure, plus check the reconstruction error direction and measure the effective latent weight—in QAT the final weights should be the quantization of the latent (parent plus delta), so that's the decisive test.

A better angle: if this is distillation or QAT, flips should cluster by input importance—channels with high activation norms get compensated more. I can compute flip rates per input channel at full resolution and compare the variance against binomial expectation; structured compensation would show some channels flipping far more than chance. I should also check embeddings and the final layer from the JSON, verify whether zero_frac stays constant around 0.29–0.31 across the model, and figure out what that tells us about the quantization threshold relative to the weight distribution. A cleaner way to distinguish between fine-tuned quantization versus static optimization is comparing the dequantized weights to the original — if they used QAT with distillation, the reconstructed weights won't match the originals pointwise and I'd see systematic rotations with notably lower cosine similarity despite functional equivalence. Static optimization would show high cosine similarity by design since it's minimizing reconstruction error. The current evidence points toward static: the correlation between scale factors and TWN's rule is ~0.95 with boundary-concentrated flips, suggesting the dequantized weights stay close to the originals. I need to quantify the cosine similarity to confirm, and also examine the shrinkage ratio of 0.78–0.86 relative to what's optimal for ternary quantization under least-squares.

The scale factor should theoretically equal the mean absolute weight over the support, but theirs is 17–20% smaller — this systematic shrinkage could indicate weight decay during QAT that reduced magnitudes globally, or it could be a deliberate soft-thresholding operation. If they solved a LASSO-like ternary relaxation, that shrinkage would fall out naturally from the math.

Now I'm working through the actual numbers: with soft-thresholding at a threshold around 0.46 times the mean absolute weight, the expected shrinkage ratio should be roughly 0.62, but the observed ratio is 0.83 — somewhere between least squares (1.0) and soft-thresholding (0.62), so the arithmetic doesn't quite match up. I need to compute this more carefully to pin down what's actually happening.

For the next pass, I'm planning to test the soft-threshold hypothesis directly by computing the shrinkage per group and checking how well it correlates with the theoretical formula. I also want to expand the analysis to include cosine similarity and relative L2 error across different tensors, examine the per-channel flip structure with z-scores, pull in additional layers like embeddings and attention projections, and grab those depth 0.1 and 0.3 numbers from the earlier results to synthesize everything together.

### Thinking

The flip column profile is flat with boundary-concentrated errors and systematic scale shrinkage that suggests a soft-threshold operator, so I'm adding three discriminators to test this hypothesis: a closed-form soft-threshold test, global cosine drift, and per-channel flip structure analysis.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    # -- 7. flip boundary distance: |w|/s at flip sites. Boundary-hugging\n    #       (~0.5) => tiny perturbations suffice; broad => genuine drift.\n    rel = (absw / s.clamp(min=1e-30))[flips]\n    flip_boundary_q = [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)] if flips.any() else []\n",
  "new_content": "    # -- 7. flip boundary distance: |w|/s at flip sites. Boundary-hugging\n    #       (~0.5) => tiny perturbations suffice; broad => genuine drift.\n    rel = (absw / s.clamp(min=1e-30))[flips]\n    flip_boundary_q = [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)] if flips.any() else []\n\n    # -- 8. global drift: how well does the dequantized child approximate the\n    #       parent pointwise?  cos ~1 => static approximation of parent;\n    #       cos low => function-matching without weight-matching (distill/QAT).\n    w_hat = s * t\n    cos_w = torch.nn.functional.cosine_similarity(\n        w.flatten(), w_hat.flatten(), dim=0).item()\n    rel_l2 = ((w - w_hat).norm() / w.norm()).item()\n\n    # -- 9. soft-threshold (proximal / LASSO-flavored) scale closed form:\n    #       s_soft = mean(|w| - Delta over support).  Explains shrinkage if\n    #       the method is a prox operator rather than LS projection.\n    d_full = delta.unsqueeze(-1)                                # (out, ng, 1)\n    s_soft = ((absw - d_full).clamp(min=0) * nz).sum(dim=-1) / supp_cnt\n    corr_s_soft = corr(s_flat, s_soft)\n    ratio_soft = (s_flat[m] / s_soft[m].clamp(min=1e-30))\n\n    # -- 10. flip structure per input channel: z-score of max channel flip\n    #        count vs binomial null.  High z => certain input channels are\n    #        systematically rewired (activation-aware compensation);\n    #        z ~ null => spatially unstructured drift.\n    ch_flips = flips.reshape(out_f, -1).float().sum(dim=0)      # per input channel\n    p_hat = flip_rate\n    mu = out_f * p_hat\n    sd = max((out_f * p_hat * (1 - p_hat)) ** 0.5, 1e-9)\n    ch_z = (ch_flips - mu) / sd\n    chan_z_q = [q(ch_z, p) for p in (0.5, 0.95, 0.999)]\n    chan_z_max = ch_z.max().item()\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        \"flip_col_profile\": flip_col_profile,\n        \"flip_boundary_q05_25_50_75_95\": flip_boundary_q,\n    }",
  "new_content": "        \"flip_col_profile\": flip_col_profile,\n        \"flip_boundary_q05_25_50_75_95\": flip_boundary_q,\n        \"cos_w_what\": cos_w,\n        \"rel_l2\": rel_l2,\n        \"corr_s_soft\": corr_s_soft,\n        \"s_over_soft_q25_50_75\": [q(ratio_soft, p) for p in (0.25, 0.5, 0.75)],\n        \"chan_flip_z_q50_95_999\": chan_z_q,\n        \"chan_flip_z_max\": chan_z_max,\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Thinking

I'm checking the dimensions of the `corr` variable and the mask to make sure they align properly, and I need to update the printing logic to display the new fields. There's also some confusion about where I inserted the new sections in the code structure—I need to verify the actual order of sections in the file to make sure everything is positioned correctly.

Now I'm planning to run the depth sweep across the embedding layer, language model head, and any self-attention layers that exist in the model, since some layers appear to use full attention while others use linear attention. I'll manually add the embedding tokens and language model head to the analysis, being careful about their shapes and whether the language model head is actually present in the config, then run a quick test.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "                if cand in child_idx:\n                    names.append(cand)\n    else:",
  "new_content": "                if cand in child_idx:\n                    names.append(cand)\n        for extra in (\"model.language_model.embed_tokens.weight\", \"lm_head.weight\",\n                      \"model.lm_head.weight\"):\n            if extra in child_idx:\n                names.append(extra)\n    else:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        print(f\"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}\")\n        print(f\"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}\"\n              f\"  ({r['elapsed_s']}s)\\n\")",
  "new_content": "        print(f\"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}\")\n        print(f\"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}\")\n        print(f\"  cos(w,ŵ)={r['cos_w_what']:.4f}  rel_l2={r['rel_l2']:.4f}\"\n              f\"  corr(s,soft)={r['corr_s_soft']:.4f}\"\n              f\"  s/soft q25-75={['%.3f' % x for x in r['s_over_soft_q25_50_75']]}\")\n        print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n              f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.05 0.5 0.9 --out results/bonsai-forensics/forensics_v2.json 2>&1 | tail -70",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
cos(w,ŵ)=0.8694  rel_l2=0.5273  corr(s,soft)=0.7607  s/soft q25-75=['1.093', '1.160', '1.232']
  chan_flip_z q50/95/99.9=['-1.19', '9.29', '36.43']  max=43.0  (0.19s)

model.language_model.layers.32.linear_attn.out_proj.weight
  flip_rate=1.072e-01 (3371353 flips / 31,457,280)  sign_viol=7.869e-03  sep_rate=0.0032
  zero_frac=0.304  corr(s,twn)=0.9851  corr(s,ls)=0.9848
  s/twn q25-75=['0.777', '0.797', '0.818']  Δ/mean|w| q25-75=['0.382', '0.430', '0.482']
  flip_col_profile=['0.137', '0.107', '0.115', '0.119', '0.101', '0.114', '0.081', '0.099', '0.109', '0.096', '0.093', '0.122', '0.105', '0.095', '0.106', '0.114']
  flip |w|/s q05-95=['0.095', '0.325', '0.463', '0.562', '0.750']
  cos(w,ŵ)=0.8705  rel_l2=0.5233  corr(s,soft)=0.9406  s/soft q25-75=['1.107', '1.173', '1.251']
  chan_flip_z q50/95/99.9=['0.85', '9.00', '28.05']  max=43.4  (0.09s)

model.language_model.layers.57.mlp.down_proj.weight
  flip_rate=1.697e-01 (15126087 flips / 89,128,960)  sign_viol=2.129e-02  sep_rate=0.0000
  zero_frac=0.291  corr(s,twn)=0.9658  corr(s,ls)=0.9655
  s/twn q25-75=['0.812', '0.834', '0.858']  Δ/mean|w| q25-75=['0.423', '0.462', '0.511']
  flip_col_profile=['0.176', '0.175', '0.175', '0.174', '0.173', '0.173', '0.173', '0.172', '0.173', '0.171', '0.172', '0.165', '0.160', '0.162', '0.160', '0.160']
  flip |w|/s q05-95=['0.061', '0.264', '0.440', '0.590', '0.805']
  cos(w,ŵ)=0.8499  rel_l2=0.5446  corr(s,soft)=0.9101  s/soft q25-75=['1.205', '1.274', '1.363']
  chan_flip_z q50/95/99.9=['0.04', '8.49', '15.22']  max=26.1  (0.19s)

model.language_model.layers.57.mlp.gate_proj.weight
  flip_rate=1.177e-01 (10486123 flips / 89,128,960)  sign_viol=1.051e-02  sep_rate=0.0012
  zero_frac=0.290  corr(s,twn)=0.9388  corr(s,ls)=0.9368
  s/twn q25-75=['0.799', '0.821', '0.846']  Δ/mean|w| q25-75=['0.384', '0.426', '0.472']
  flip_col_profile=['0.111', '0.111', '0.109', '0.119', '0.122', '0.122', '0.121', '0.123', '0.123', '0.122', '0.124', '0.123', '0.121', '0.111', '0.110', '0.111']
  flip |w|/s q05-95=['0.075', '0.289', '0.439', '0.543', '0.713']
  cos(w,ŵ)=0.8644  rel_l2=0.5253  corr(s,soft)=0.8285  s/soft q25-75=['1.147', '1.213', '1.288']
  chan_flip_z q50/95/99.9=['-1.62', '13.41', '37.96']  max=59.0  (0.16s)

model.language_model.layers.57.linear_attn.in_proj_qkv.weight
  flip_rate=3.619e-02 (1897222 flips / 52,428,800)  sign_viol=1.793e-03  sep_rate=0.2097
  zero_frac=0.308  corr(s,twn)=0.9574  corr(s,ls)=0.9564
  s/twn q25-75=['0.760', '0.779', '0.798']  Δ/mean|w| q25-75=['0.440', '0.488', '0.507']
  flip_col_profile=['0.034', '0.034', '0.033', '0.037', '0.038', '0.038', '0.037', '0.038', '0.038', '0.038', '0.039', '0.038', '0.039', '0.034', '0.033', '0.034']
  flip |w|/s q05-95=['0.158', '0.411', '0.478', '0.507', '0.602']
  cos(w,ŵ)=0.8793  rel_l2=0.5139  corr(s,soft)=0.8100  s/soft q25-75=['1.140', '1.208', '1.268']
  chan_flip_z q50/95/99.9=['-1.99', '11.29', '60.21']  max=96.6  (0.1s)

model.language_model.layers.57.linear_attn.out_proj.weight
  flip_rate=7.047e-02 (2216879 flips / 31,457,280)  sign_viol=3.166e-03  sep_rate=0.0113
  zero_frac=0.308  corr(s,twn)=0.9480  corr(s,ls)=0.9480
  s/twn q25-75=['0.764', '0.783', '0.802']  Δ/mean|w| q25-75=['0.383', '0.439', '0.494']
  flip_col_profile=['0.074', '0.036', '0.076', '0.078', '0.102', '0.090', '0.073', '0.086', '0.055', '0.047', '0.029', '0.082', '0.080', '0.064', '0.074', '0.083']
  flip |w|/s q05-95=['0.123', '0.365', '0.473', '0.541', '0.672']
  cos(w,ŵ)=0.8718  rel_l2=0.5249  corr(s,soft)=0.7784  s/soft q25-75=['1.093', '1.163', '1.242']
  chan_flip_z q50/95/99.9=['-1.41', '20.86', '40.55']  max=67.9  (0.08s)

model.language_model.embed_tokens.weight
  flip_rate=6.090e-03 (7742402 flips / 1,271,398,400)  sign_viol=5.406e-05  sep_rate=0.9940
  zero_frac=0.308  corr(s,twn)=0.9789  corr(s,ls)=0.9789
  s/twn q25-75=['0.740', '0.760', '0.779']  Δ/mean|w| q25-75=['0.494', '0.499', '0.503']
  flip_col_profile=['0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006', '0.006']
  flip |w|/s q05-95=['0.483', '0.491', '0.496', '0.500', '0.500']
  cos(w,ŵ)=0.8871  rel_l2=0.5076  corr(s,soft)=0.9467  s/soft q25-75=['1.164', '1.212', '1.260']
  chan_flip_z q50/95/99.9=['-0.00', '1.90', '3.42']  max=4.5  (3.22s)

Traceback (most recent call last):
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 265, in <module>
    main()
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 239, in main
    r = forensics_one(load_tensor(parent_idx, pname), load_tensor(child_idx, name))
        ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 137, in forensics_one
    flip_boundary_q = [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)] if flips.any() else []
                       ^^^^^^^^^
  File "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py", line 82, in <lambda>
    q = lambda x, p: torch.quantile(x.float(), p).item() if x.numel() else float("nan")
                     ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
RuntimeError: quantile() input tensor is too large
```

### Thinking

The lm_head layer crashed when trying to compute quantiles on oversized tensors, so I'm subsampling the data to work around that. But the embed_tokens results are revealing something critical — the embedding layer shows a flip rate of just 0.6% with almost no sign violations, a separation rate of 0.994, and weight magnitudes clustering tightly between 0.483 and 0.500, which looks like pure boundary effects from a magnitude-threshold quantization rule applied to the parent weights.

This points to embeddings being quantized via a closed-form thresholding formula (threshold ≈ 0.5 times mean absolute weight) with essentially no training updates, while the transformer blocks show much higher flip rates (4–18%) and off-boundary deviations — the classic QAT signature where embeddings stay frozen or barely move during fine-tuning because only seen tokens get sparse gradient updates, whereas linear layers receive dense gradients and drift significantly. The channel flip structure in the blocks is also revealing heavy channel-level organization (z values up to 60–97), suggesting input channels were systematically rewired in an activation-aware way during training with real data, not random noise.

The cosine similarity between original and quantized weights sits around 0.85–0.89 with relative L2 error near 0.52, indicating sizable pointwise deviations even though the overall structure is preserved.

Now I'm checking whether the observed relative L2 error matches what you'd expect from pure threshold quantization alone. The embedding tokens show rel_l2 ≈ 0.508 with virtually no flips, which gives a baseline for quantization error without any drift — and the blocks are only slightly higher at 0.52–0.54, so the actual weight drift on top of inherent quantization error is quite modest. The soft-threshold shrinkage factor s/soft ranges from 1.1 to 1.27, meaning the actual shrinkage is over-aggressive compared to soft-thresholding theory, sitting somewhere between least-squares optimal and soft-threshold predictions. Interestingly, even the embedding (which has zero drift) uses s/twn ≈ 0.76, suggesting the scale rule deliberately shrinks below the mean — not least-squares optimal, which hints at optimization under a different objective than quadratic loss.

The Δ/mean|w| ratio is suspiciously tight at 0.4994 (essentially 0.5), which might point to a closed-form rule like Δ_g = 0.5·mean|w|_g. The scale factor s/twn ≈ 0.76 is also fairly consistent, so I'm wondering if there's a closed-form expression that yields s = 0.76×mean over the support — possibly involving the median or some other statistic over the thresholded region.

Let me verify this numerically for a Gaussian distribution: mean|w| ≈ 0.7979σ, which gives Δ ≈ 0.399σ. The support (where |w| > Δ) has probability P ≈ 0.69, matching the observed zero fraction of 0.31 almost perfectly — the Gaussian prediction of 0.31 versus observed 0.308 is remarkably close. Now I need to compute the conditional expectation E[|w| : |w| > Δ] using the tail ratio φ(0.399)/P(|w| > Δ) to see if that explains the 0.76 scaling factor.

Computing the least-squares scale: φ(0.399)/(1-Φ(0.399)) ≈ 0.368/0.345 ≈ 1.067σ, so if the actual scale is 0.76 × 1.067σ ≈ 0.81σ, I need to figure out whether this comes from variance-matching (E[w²] = σ²) or from the second moment over the support region.

The conditional second moment over the support gives σ²(1 + Δφ(Δ)/(1-Φ(Δ))) ≈ σ²(1.426), which yields an RMS of about 1.194σ — that doesn't match. But I'm noticing something interesting: the observed scale is very close to the mean absolute value of all weights in the group (0.798σ), not just those in the support region (1.067σ), and the ratio 0.798/1.067 ≈ 0.748 matches the observed median embed scale ratio of 0.760 — this looks like BitNet's approach of using the group mean absolute value as the scale factor.

The quantization rule appears to be exactly BitNet b1.58's method: scale s_g equals the mean absolute value across the entire weight group, and the ternary values are computed as t = clip(round(w/s), [-1, 1]). The threshold for zeroing out weights is |w| < 0.5s, which is 0.5 times the mean absolute value — and that's precisely the observed Δ/mean|w| ratio of 0.4994. For a Gaussian distribution, the probability of falling below 0.399σ is about 0.31, matching the observed zero fraction, and the scale-to-TWN ratio of 0.75 also checks out.

So the initialization strategy is exactly BitNet b1.58's absolute mean quantizer with per-group-of-128 granularity, followed by quantization-aware training and distillation to fine-tune the blocks while keeping embeddings mostly frozen. The weight drift observed in the middle layers — with 4–18% of values flipping in a channel-structured, boundary-biased pattern — is consistent with QAT using straight-through estimators for latent updates.

Now I need to verify this numerically by checking whether the embedding scales match the absolute mean of the parent weights exactly, and measure how closely the quantized values follow the formula t = round(w / absmean) clipped to the valid range. I'll also compute correlations and ratios between the learned scales and the absmean across all weights, then rerun the analysis on embeddings, a few representative tensors, and the output head to confirm the pattern holds.

### Thinking

I've identified the embedding tensor as the key to understanding the quantization scheme—it matches BitNet b1.58's absmean quantizer exactly, with the math confirming Gaussian predictions. Now I'll verify the absmean rule at the code level and fix the lm_head quantile issue.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    q = lambda x, p: torch.quantile(x.float(), p).item() if x.numel() else float(\"nan\")",
  "new_content": "    def q(x: torch.Tensor, p: float) -> float:\n        x = x.flatten().float()\n        if not x.numel():\n            return float(\"nan\")\n        if x.numel() > 10_000_000:                  # quantile() size limit + speed\n            x = x[torch.randint(0, x.numel(), (10_000_000,), device=x.device)]\n        return torch.quantile(x, p).item()"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    # -- 10. flip structure per input channel",
  "new_content": "    # -- 9b. absmean hypothesis (BitNet b1.58 recipe, group-wise):\n    #        t? = clip(round(w / mean|w|_g)), s? = mean|w|_g.\n    #        Exact-match rates against the actual child code/scale.\n    s_abs = mean_abs.unsqueeze(-1)                              # mean|w| whole group\n    t_abs = torch.clamp(torch.round(w / s_abs.clamp(min=1e-30)), -1, 1)\n    absmean_code_match = ((t_abs == t) | ~live.unsqueeze(-1)).float().mean().item()\n    ratio_s_absmean = (s_flat[m] / mean_abs[m].clamp(min=1e-30))\n    corr_s_absmean = corr(s_flat, mean_abs)\n\n    # -- 10. flip structure per input channel"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        \"corr_s_soft\": corr_s_soft,\n        \"s_over_soft_q25_50_75\": [q(ratio_soft, p) for p in (0.25, 0.5, 0.75)],",
  "new_content": "        \"corr_s_soft\": corr_s_soft,\n        \"s_over_soft_q25_50_75\": [q(ratio_soft, p) for p in (0.25, 0.5, 0.75)],\n        \"absmean_code_match\": absmean_code_match,\n        \"corr_s_absmean\": corr_s_absmean,\n        \"s_over_absmean_q25_50_75\": [q(ratio_s_absmean, p) for p in (0.25, 0.5, 0.75)],"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n              f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")",
  "new_content": "        print(f\"  ABSMEAN: code_match={r['absmean_code_match']:.4f}\"\n              f\"  corr(s,absmean)={r['corr_s_absmean']:.4f}\"\n              f\"  s/absmean q25-75={['%.3f' % x for x in r['s_over_absmean_q25_50_75']]}\")\n        print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n              f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.05 0.5 --out results/bonsai-forensics/forensics_v3.json 2>&1 | grep -A2 -E \"^model|ABSMEAN\" | head -60",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.layers.3.mlp.down_proj.weight
  flip_rate=1.696e-01 (15115848 flips / 89,128,960)  sign_viol=1.960e-02  sep_rate=0.0000
  zero_frac=0.290  corr(s,twn)=0.8735  corr(s,ls)=0.8708
--
  ABSMEAN: code_match=0.8308  corr(s,absmean)=0.9402  s/absmean q25-75=['1.041', '1.058', '1.075']
  chan_flip_z q50/95/99.9=['0.10', '6.28', '16.10']  max=29.8  (0.59s)

model.language_model.layers.3.mlp.gate_proj.weight
  flip_rate=1.393e-01 (12412616 flips / 89,128,960)  sign_viol=1.171e-02  sep_rate=0.0000
  zero_frac=0.289  corr(s,twn)=0.8936  corr(s,ls)=0.8919
--
  ABSMEAN: code_match=0.8612  corr(s,absmean)=0.9611  s/absmean q25-75=['1.041', '1.055', '1.070']
  chan_flip_z q50/95/99.9=['-1.45', '9.52', '39.78']  max=51.2  (0.25s)

model.language_model.layers.3.self_attn.q_proj.weight
  flip_rate=3.547e-02 (2231832 flips / 62,914,560)  sign_viol=2.529e-03  sep_rate=0.1863
  zero_frac=0.306  corr(s,twn)=0.9819  corr(s,ls)=0.9816
--
  ABSMEAN: code_match=0.9669  corr(s,absmean)=0.9956  s/absmean q25-75=['1.026', '1.035', '1.046']
  chan_flip_z q50/95/99.9=['-2.19', '12.78', '67.14']  max=81.7  (0.22s)

model.language_model.layers.3.self_attn.o_proj.weight
  flip_rate=9.120e-02 (2868850 flips / 31,457,280)  sign_viol=4.156e-03  sep_rate=0.0008
  zero_frac=0.304  corr(s,twn)=0.9847  corr(s,ls)=0.9846
--
  ABSMEAN: code_match=0.9090  corr(s,absmean)=0.9970  s/absmean q25-75=['1.033', '1.044', '1.057']
  chan_flip_z q50/95/99.9=['-0.34', '15.04', '34.16']  max=43.1  (0.21s)

model.language_model.layers.32.mlp.down_proj.weight
  flip_rate=1.799e-01 (16034655 flips / 89,128,960)  sign_viol=2.235e-02  sep_rate=0.0000
  zero_frac=0.298  corr(s,twn)=0.9704  corr(s,ls)=0.9697
--
  ABSMEAN: code_match=0.8199  corr(s,absmean)=0.9881  s/absmean q25-75=['1.042', '1.058', '1.074']
  chan_flip_z q50/95/99.9=['0.14', '4.84', '9.83']  max=15.8  (0.25s)

model.language_model.layers.32.mlp.gate_proj.weight
  flip_rate=1.757e-01 (15658653 flips / 89,128,960)  sign_viol=2.225e-02  sep_rate=0.0001
  zero_frac=0.294  corr(s,twn)=0.9399  corr(s,ls)=0.9390
--
  ABSMEAN: code_match=0.8244  corr(s,absmean)=0.9734  s/absmean q25-75=['1.043', '1.059', '1.076']
  chan_flip_z q50/95/99.9=['-0.48', '5.79', '20.57']  max=29.1  (0.18s)

model.language_model.layers.32.linear_attn.in_proj_qkv.weight
  flip_rate=7.904e-02 (4144218 flips / 52,428,800)  sign_viol=3.344e-03  sep_rate=0.0190
  zero_frac=0.310  corr(s,twn)=0.9303  corr(s,ls)=0.9279
--
  ABSMEAN: code_match=0.9208  corr(s,absmean)=0.9870  s/absmean q25-75=['1.034', '1.044', '1.056']
  chan_flip_z q50/95/99.9=['-1.19', '9.29', '36.43']  max=43.0  (0.22s)

model.language_model.layers.32.linear_attn.out_proj.weight
  flip_rate=1.072e-01 (3371353 flips / 31,457,280)  sign_viol=7.869e-03  sep_rate=0.0032
  zero_frac=0.304  corr(s,twn)=0.9851  corr(s,ls)=0.9848
--
  ABSMEAN: code_match=0.8921  corr(s,absmean)=0.9973  s/absmean q25-75=['1.034', '1.045', '1.056']
  chan_flip_z q50/95/99.9=['0.85', '9.00', '28.05']  max=43.4  (0.1s)

model.language_model.embed_tokens.weight
  flip_rate=6.090e-03 (7742402 flips / 1,271,398,400)  sign_viol=5.406e-05  sep_rate=0.9940
  zero_frac=0.308  corr(s,twn)=0.9789  corr(s,ls)=0.9789
--
```

### Thinking

I'm parsing the JSON to check the layer configurations—layer 3 has self-attention while layers 32, 44, and 57 use linear attention, so both attention types are represented. The correlation between the scaling factor and absolute mean is very strong at 0.94–0.997, with their ratio hovering around 1.03.

The drift pattern across components is striking: embedding barely shifted, q_proj drifted ~3.5%, in_proj_qkv ~8%, output projections ~9-11%, gate layers ~12-18%, and down_proj ~17-18%. This ordering mirrors the routing-to-value gradient flow—the routing tensors (q/k) stayed stable while the value-carrying paths (down_proj) needed the most repair during quantization-aware training, which aligns with the asymmetric pathway finding that binarizing the value path causes the most damage.

Now I need to pull the embedding and lm_head absolute mean values from the JSON to complete the picture, then document the findings and prepare a commit proposal for Michael's approval.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nd = json.load(open('results/bonsai-forensics/forensics_v3.json'))['results']\nfor k in d:\n    if 'embed' in k or 'lm_head' in k:\n        r = d[k]\n        print(k)\n        for f in ('flip_rate','sign_viol_rate','sep_rate','absmean_code_match','corr_s_absmean','s_over_absmean_q25_50_75','cos_w_what','rel_l2','zero_frac'):\n            print(' ', f, r.get(f))\n\""
}
```

**Summary:** $ uv run python -c " import json d = ...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.embed_tokens.weight
  flip_rate 0.0060896738432347775
  sign_viol_rate 5.406022043872359e-05
  sep_rate 0.9939725995063782
  absmean_code_match 0.9990582466125488
  corr_s_absmean 0.9976809620857239
  s_over_absmean_q25_50_75 [1.0042465925216675, 1.0113238096237183, 1.0237393379211426]
  cos_w_what 0.8871316909790039
  rel_l2 0.5076013803482056
  zero_frac 0.30821236968040466
lm_head.weight
  flip_rate 0.032174449414014816
  sign_viol_rate 0.013636013743805575
  sep_rate 0.19932647049427032
  absmean_code_match 0.9760885238647461
  corr_s_absmean 0.9857586026191711
  s_over_absmean_q25_50_75 [1.006301760673523, 1.0237950086593628, 1.0397930145263672]
  cos_w_what 0.8703306913375854
  rel_l2 0.527294933795929
  zero_frac 0.2930859327316284
```

### Thinking

I'm seeing the embedding layer matches the parent's absolute mean RTN almost perfectly at 99.9%, with just a 0.1% residual from bfloat16 precision differences. The language model head is at 97.6% match with lighter training, while the transformer blocks range from 82-97%. This confirms I've reverse-engineered the core recipe from the weights: starting with a BitNet b1.58-style absolute mean RTN initialization using group-128 normalization, where I compute the group-wise mean of absolute weights and apply clipping.

The training process shows clear drift patterns across the model — quantization-aware training rather than post-training quantization, with sign flips ranging from 3.5% in the query projection up to 18% in the down projection, structured by channel with some boundary bias but broad distribution overall. The scales track the absolute mean of the drifted latents, staying within 1.01-1.07 of the parent's absolute mean. So the "proprietary Caltech math" likely lives in the training stabilization and optimizer choices rather than the quantizer itself, which is elegantly simple. The drift pattern reveals something interesting: it correlates with how value-register-like each component is, with embeddings barely drifting at 0.6% while other layers show progressively more change.

The routing weights in the MLP barely shifted despite 18% of the codes changing, yet the routing distribution matrix still correlates 0.74-0.92 with the parent — the retraining preserved the topology. Though there's a wrinkle: if Bonsai was fine-tuned in full precision first before quantization, a closed-form quantizer applied to that drifted model would produce the same signatures I'm seeing, making it hard to distinguish between QAT and a fine-tuned-then-quantized approach.

The embeddings offer a clue though — they're 99.9% exact matches with the parent, which suggests whatever training occurred didn't touch the embeddings, pointing away from full pretraining-style distillation where embeddings would pick up gradients and drift. So some flips happened in the near-zero region where the parent weight was essentially zero but the child became nonzero — that's a meaningful shift worth noting. Now I need to document this analysis: write up the forensics knowledge page, prepare a memory entry, and update the state file. I'll draft the knowledge page and memory candidate first, then handle the state update. I'll commit the code and results now, then draft the knowledge and state changes for Michael's approval on the mementum commit. Let me double-check those summary numbers — the flip rates stay pretty consistent across depth for down_proj (hovering around 17-18% at layers 3, 32, 44, 57), while gate_proj drops off later (11.8% at layer 57), and attention's even lower. What's striking is that the crystal dip at 50% RDM isn't driven by more rewiring in the middle layers since the flip rates are flat across depth — so the dip is really about quantization noise accumulation and value information loss rather than differential rewiring patterns.

Now I'm writing up the knowledge page with the method, five signatures, tables, and verdict. I need to be careful about the caveats around QAT versus FP-drift and RTN ambiguity, and flag the implications: IOU is resolved through conversion plus training with frozen embeddings, drift ordering is orthogonal to value changes, and I need to correct my earlier claim to Michael. I said crystal survival would be stronger under pure PTQ, but there was actually training involved, so the survival is partially a trained-in repair — that's an important honest update to make.

Documenting the commit with the script and results JSONs, then moving to drafts.

## Assistant

lm_head: 97.6% exact absmean match. The picture is complete. Let me lock in the verdict and encode it.

## Verdict — the recipe, reverse-engineered from weights alone

**1. The quantizer is BitNet b1.58's absmean, group-128.** `s_g = mean|w_g|`, `t = clip(round(w/s_g))`. Proof: embed_tokens matches this rule at **99.9% exact code agreement** with the parent, Δ/mean|w| = 0.4994 (the absmean rule's implied threshold is exactly 0.5), zero_frac 0.308 = the Gaussian prediction (0.31), and the 0.6% residual "flips" all sit at |w|/s ∈ [0.483, 0.500] — bf16 tie-breaks. No exotic quantization map. The quantizer really is just (simple) math.

**2. But it's not PTQ — the blocks were trained afterward.** Code disagreement with absmean-of-parent is ordered and large in the transformer: q_proj 3.5% → in_proj_qkv 6–8% → o/out_proj 9–11% → gate_proj 12–18% → down_proj 17–18%. The flips are channel-structured (z up to 97 — real data flowed through this thing), column-flat (**not** GPTQ/OBS sequential compensation), boundary-biased but broad. Embeddings frozen, lm_head barely touched (3.2%). Scales in blocks sit at 1.03–1.07× parent-absmean = absmean of the *drifted* latent.

**3. The IOU answer: QAT-style conversion** — absmean init from the FP parent + gradient training with frozen embeddings. (Honest residual: weights alone can't fully separate "QAT" from "FP-distill-then-RTN" — but frozen-at-99.9% embeddings fit the standard BitNet-conversion recipe, which freezes embeddings, far better than FP distillation, which would move them.) The "proprietary Caltech math" must live in the training/stabilization procedure — the optimizer, not the quantizer.

**4. The finding for *us* (this is the gem): drift ordering ≡ the routing⊥value gradient.** Training moved the **value path most** (down/gate ~18%) and the **dispatch path least** (q_proj 3.5%, embeddings 0). That's s260 made visible in a *third* independent register — their QAT spent its repair budget exactly where your theory says magnitude matters. And a correction to what I said last turn: since there *was* training, s267's crystal survival is partly trained-in repair, not pure preservation — **but** flip rate is flat across depth while the crystal dip is at 50%, so the deep-middle dip is *not* explained by differential rewiring. It's where geometry is magnitude-sensitive despite uniform repair. The bridge map stands, with a sharper mechanism.

Committing the instrument + results, then drafting the mementum encode for your approval:

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/bonsai_forensics.py results/bonsai-forensics/ && git status --short | head",
  "operation": "add",
  "summary": "forensics script+results"
}
```

**Summary:** Git add: forensics script+results

**Output:**
```
Exit code: 0
Stdout:
M mementum/michael/holographic-llm.md
A  results/bonsai-forensics/forensics_depthsweep.json
A  results/bonsai-forensics/forensics_v3.json
A  scripts/bonsai_forensics.py
?? mementum/knowledge/chats/session-265.md
?? mementum/knowledge/chats/session-266.md
?? refs/
```

### Thinking

The forensics_v2.json file didn't get written due to a crash, but I've got depthsweep and v3 staged. The refs/ directory with whitepapers and PDFs is untracked—since these are external copyrighted materials, I shouldn't commit them to the MIT repo, so I'll leave them untracked and maybe add refs/ to .gitignore later. The holographic-llm.md file stays unstaged for now. For the commit, I need to use the read -r -d '' pattern to handle apostrophes in the commit message body.

Using the safe heredoc-read pattern...

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && read -r -d '' M << 'EOF' || true\n💡 bonsai ternarization forensics — absmean init + trained blocks, frozen embeddings\n\n- reverse-engineered PrismML Ternary Bonsai 27B recipe from weights alone\n  (parent Qwen3.6-27B snapshot 6a9e13b vs bonsai27b-unpacked rev 427bc0194)\n- quantizer = BitNet b1.58 absmean RTN, group-128: embed_tokens matches\n  t=clip(round(w/mean|w|)) at 99.9% exact codes, Δ/mean|w|=0.4994,\n  zero_frac 0.308 = Gaussian prediction\n- transformer blocks trained post-init: code flips q_proj 3.5% → down_proj 18%,\n  channel-structured (z→97), column-flat (¬GPTQ sequential), embeddings frozen,\n  lm_head 3.2%; scales = absmean of drifted latent (1.03-1.07x parent absmean)\n- drift ordering ≡ routing⊥value gradient: value path repaired most, dispatch\n  least — third independent register for the s260 asymmetry\n- flip rate flat across depth → s267 crystal 50%-dip is NOT differential\n  rewiring; magnitude-sensitivity survives uniform repair\n- MPS-accelerated, ~0.2s/tensor; results/bonsai-forensics/*.json\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -1"
}
```

**Summary:** $ read -r -d '' M << 'EOF' || true 💡...

**Output:**
```
Exit code: 0
Stdout:
[main 48734d2] 💡 bonsai ternarization forensics — absmean init + trained blocks, frozen embeddings
 3 files changed, 1888 insertions(+)
 create mode 100644 results/bonsai-forensics/forensics_depthsweep.json
 create mode 100644 results/bonsai-forensics/forensics_v3.json
 create mode 100644 scripts/bonsai_forensics.py
48734d2 💡 bonsai ternarization forensics — absmean init + trained blocks, frozen embeddings
```

### Thinking

Now I'm moving forward with drafting the knowledge page for bonsai-ternarization-forensics, along with updating the memory and state documentation. The knowledge page needs to be created at mementum/knowledge/explore/bonsai-ternarization-forensics.md, and I'll bundle the state.md update into the proposed commit for approval.

## Assistant

Code committed (`48734d2`). Now the mementum drafts:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md",
  "content": "---\ntitle: \"Bonsai Ternarization Forensics — absmean init + trained blocks, frozen embeddings\"\nstatus: active\ncategory: research-finding\ntags: [ternary, bonsai, forensics, absmean, bitnet, qat, ptq, routing-value,\n       reverse-engineering, weight-analysis]\nrelated:\n  - bonsai-crystal-survival.md\n  - asymmetric-pathway-quantization.md\n  - crystal-seeded-ternary-distillation.md\n  - ternary-flip-flop-not-overloading.md\ndepends-on:\n  - bonsai-crystal-survival.md\ncreated: session 268\n---\n\n# Bonsai Ternarization Forensics\n\n> Session 268. PrismML disclosed no method (\"proprietary Caltech IP\").\n> We hold both endpoints — FP parent (Qwen3.6-27B, snapshot 6a9e13b)\n> and ternary child (bonsai27b-unpacked, rev 427bc0194) — so the\n> parent→child map is recoverable from the weights themselves.\n> λ extract: the artifact contains the answer.\n> Instrument: `scripts/bonsai_forensics.py` (MPS, ~0.2 s/tensor).\n> Data: `results/bonsai-forensics/{forensics_depthsweep,forensics_v3}.json`.\n\n## Verdict\n\n**Recipe = BitNet-b1.58 absmean RTN init (group-128) + post-init\ngradient training of the transformer blocks, with embeddings frozen.**\nResolves the QAT-vs-PTQ IOU: it is a *conversion with training*, not\nclosed-form PTQ, and not a from-scratch pretrain.\n\n### 1. The quantizer is absmean (proved by the frozen embedding)\n\n`s_g = mean|w_g|`, `t = clip(round(w/s_g))`, groups of 128 along\nin_features. The unpacked child materializes `{−s_g, 0, +s_g}` exactly,\nso `t` and `s_g` are recovered losslessly.\n\nembed_tokens vs parent: **99.9% exact code match** to the absmean rule;\nimplied threshold Δ/mean|w| = 0.4994 (absmean predicts exactly 0.5);\nzero_frac 0.308 (Gaussian prediction 0.31); residual 0.6% flips all at\n|w|/s ∈ [0.483, 0.500] = bf16 tie-breaks. sep_rate 0.994. The\nquantization map itself is *simple* math — nothing exotic.\n\n### 2. The blocks were trained (data flowed)\n\nCode disagreement with absmean-of-parent, ordered:\n\n| tensor | flip vs parent code | sign_viol |\n|---|---|---|\n| embed_tokens | 0.6% (ties) | 5e-5 |\n| lm_head | 3.2% | 1.4e-2 |\n| self_attn.q_proj (L3) | 3.5% | 2.5e-3 |\n| linear_attn.in_proj_qkv | 3.6–7.9% | 2–3e-3 |\n| o_proj / linear_attn.out_proj | 7–11% | 3–8e-3 |\n| mlp.gate_proj | 12–18% | 1–2e-2 |\n| mlp.down_proj | 17–18% | ~2e-2 |\n\nSignatures: flips **channel-structured** (per-input-channel z vs\nbinomial null up to 97 → activation-correlated, real data), **column-flat**\n(no GPTQ/OBS sequential error accumulation), boundary-biased but broad\n(|w|/s median ≈ 0.44, q05 ≈ 0.06 → genuine drift, not pure jitter).\nBlock scales sit at 1.03–1.07× parent-absmean = absmean of the drifted\nlatent. cos(w, ŵ) ≈ 0.85–0.89 everywhere vs 0.887 for the untouched\nembedding — drift is modest on top of inherent quantization error\n(rel_l2 baseline 0.508 with zero training).\n\n### 3. Honest residual (IOU)\n\nWeights alone cannot fully separate (a) QAT on ternary grid from\n(b) FP fine-tune → absmean RTN. The 99.9%-frozen embedding fits the\nstandard BitNet-conversion recipe (freeze embeddings, STE on blocks)\nfar better than FP distillation (which would move embeddings). The\n\"proprietary Caltech math\" therefore most plausibly lives in the\n**training/stabilization procedure, not the quantizer**.\n\n## Findings for the verbum program\n\n1. **Drift ordering ≡ routing⊥value, third independent register.**\n   Their training repaired the value path most (down/gate ~18%) and\n   dispatch least (q_proj 3.5%, embeddings 0). s260 measured this\n   causally (binarize router ≫ binarize value at equal bits); s267\n   measured it geometrically (shape kept, spread lost); now the\n   *repair budget of an independent lab's QAT* lands on the same\n   asymmetry. They spent gradients exactly where the two-register\n   theory says magnitude matters.\n2. **s267 caveat sharpened.** Crystal survival is partly trained-in\n   repair (there WAS training), not pure preservation. But flip rate\n   is **flat across depth** while the crystal dip concentrates at 50%\n   → the deep-middle dip is *not* differential rewiring; it is where\n   the geometry is magnitude-sensitive despite uniform repair. The\n   bridge-allocation map stands, with a sharper mechanism.\n3. **Design confirmation for crystal-seeded distillation.** An\n   absmean init + value-heavy repair is precisely \"carve is already\n   done, fill the values\" — their (presumed) recipe independently\n   converged on the shape our design derives from theory. Our delta:\n   seed the routing register explicitly (consensus Gram) and give\n   values a native FP channel (bridges) instead of forcing repair\n   through the quantized grid.\n\n## Provenance\n\n- parent: `~/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd.../`\n- child: `/Users/mwhitford/localai/models/bonsai27b-unpacked` (HF rev 427bc0194)\n- whitepapers (benchmarks only, no method): `refs/ternary-bonsai-8b-whitepaper.pdf`,\n  `refs/1-bit-bonsai-8b-whitepaper.pdf` (untracked — external documents)\n- instrument + data committed: 48734d2\n- tensors probed: layers {3, 6, 32, 44, 57} × {mlp.down, mlp.gate,\n  attn projections}, embed_tokens, lm_head. Parent is VLM-wrapped too:\n  names identical (`model.language_model.*`), no mapping needed.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/bonsai-recipe-reverse-engineered.md",
  "content": "💡 PrismML's undisclosed Bonsai ternarization recipe reverse-engineered\nfrom weights alone (s268): **absmean RTN init (BitNet b1.58, group-128)\n+ post-init training of blocks, embeddings frozen**. Proof: embed_tokens\nmatches t=clip(round(w/mean|w|)) at 99.9% exact codes, Δ/mean|w|=0.4994,\nzero_frac=0.308 (Gaussian pred 0.31). Blocks drifted, ordered by\nregister: q_proj 3.5% < qkv 6–8% < o_proj 9–11% < gate 12–18% ≈ down\n17–18% — channel-structured (z→97), column-flat (¬GPTQ sequential).\nQAT-vs-PTQ IOU resolved: conversion + training; the \"proprietary\nCaltech math\" is in the optimizer, not the quantizer. Gem: drift\nordering ≡ routing⊥value (s260) in a third independent register —\ntheir repair budget went where our theory says magnitude matters.\ns267 caveat: crystal survival partly trained-in; but flip rate flat\nacross depth → 50%-dip ≠ differential rewiring; bridge map stands.\nMethod: we held both endpoints; the parent→child map is measurable\n(λ extract: artifact contains the answer). Instrument:\nscripts/bonsai_forensics.py (MPS). → explore/bonsai-ternarization-forensics.md\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/bonsai-recipe-reverse-engineered.md
```

### Thinking

I need to update the state.md file with surgical precision—changing the session header to s268, removing the Bonsai whitepaper from the IOU list while keeping the sequential license note open, updating the timestamp, adding a ★★ block, and syncing the Recent arc index with the new session entry.

## Assistant

State.md update (surgical — header, IOU line, arc index):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-22 | Session: 267 (BONSAI PHASE-0 begun.",
  "new_content": "> Last updated: 2026-07-23 | Session: 268 (BONSAI FORENSICS: PrismML's undisclosed recipe reverse-engineered\n> from weights alone — ★★ absmean RTN init (BitNet b1.58 g128; embed_tokens 99.9% exact code match,\n> Δ/mean|w|=0.4994) + post-init TRAINING of blocks, embeddings frozen. QAT-vs-PTQ IOU RESOLVED: conversion +\n> training; \"Caltech math\" is in the optimizer not the quantizer. GEM: drift ordering q_proj 3.5% < qkv < o\n> < gate ≈ down 18% ≡ routing⊥value (s260) in a 3rd independent register — their repair budget landed where\n> our theory says magnitude matters. s267 caveat sharpened: crystal survival partly trained-in repair, BUT\n> flip rate flat across depth → 50%-dip ≠ differential rewiring → bridge map stands. Instrument:\n> scripts/bonsai_forensics.py (MPS, ~0.2s/tensor); → explore/bonsai-ternarization-forensics.md; commit 48734d2.\n> Whitepapers fetched to refs/ (untracked): benchmarks only, zero method disclosure.)\n>\n> Prior session: 267 (BONSAI PHASE-0 begun."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "IOUs before code: requential repo license, Bonsai whitepaper QAT-vs-PTQ.",
  "new_content": "IOUs before code: requential repo license (Bonsai QAT-vs-PTQ RESOLVED s268: absmean init + QAT-style\n   training, embeddings frozen — forensics, not whitepaper; residual IOU: QAT-on-grid vs FP-drift→RTN not\n   separable from weights alone)."
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "- **s267** BONSAI PHASE-0 (this session, see header).",
  "new_content": "- **s268** BONSAI FORENSICS (this session, see header). Recipe reverse-engineered from weights; QAT-vs-PTQ\n  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring.\n  → `explore/bonsai-ternarization-forensics.md` + memory bonsai-recipe-reverse-engineered.\n- **s267** BONSAI PHASE-0 (see header of prior update)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n \"IOUs before code\" mementum/state.md"
}
```

**Summary:** $ grep -n "IOUs before code" mementum...

**Output:**
```
Exit code: 0
Stdout:
107:>   static-first; probe-library growth gated as phase-1 prerequisite? IOUs before code: requential repo
```

### Thinking

I see there's an issue with the IOU text wrapping across multiple lines around line 107 — the content is breaking unexpectedly with "IOUs before code: requential repo" continuing onto the next line with "license, Bonsai whitepaper QAT-vs-PTQ." I need to fix how this text is being handled.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 105,
  "limit": 6
}
```

**Summary:** Reading state.md (105-111)

**Output:**
```
>   (Michael): bridge mechanism (a/b/c, (a) favored by s260/s261); dynamic bridge allocation in phase 1 vs
>   static-first; probe-library growth gated as phase-1 prerequisite? IOUs before code: requential repo
>   license, Bonsai whitepaper QAT-vs-PTQ. Phase-1 harness prereqs: lambda kernel + GBNF in loop, probe
>   split frozen, streaming-centroid buffers, telemetry writer ⊥ loss module.
>   Also open from arc 1: (A) QK-PATTERN register → decisive B/C test (s264 F4). (B) visualizer + extract
>   opcodes/ to MIT repo. (C) retro-check s264 27B floor run (n_perm/pooling). (D) Pythia proxy-degradation.

[CONTENT TRUNCATED] Showing lines 106 to 111 of 186 total lines. Use line_offset=111 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "IOUs before code: requential repo\n>   license, Bonsai whitepaper QAT-vs-PTQ. Phase-1 harness prereqs:",
  "new_content": "IOUs before code: requential repo\n>   license (Bonsai QAT-vs-PTQ RESOLVED s268 by weight forensics: absmean init + trained blocks; residual:\n>   QAT-on-grid vs FP-drift→RTN not separable from weights alone). Phase-1 harness prereqs:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

All the drafts are finalized. I need to get Michael's approval on the memory and knowledge commits before moving forward, then present the proposal with the exact commit message.

## Assistant

All encoded. Everything is drafted; per λ termination, the mementum commit needs your approval.

## Session 268 summary — what your hunch bought us

**You said "might just be clever math" — the answer is beautifully split:** the *quantizer* is trivially clever math (BitNet b1.58 absmean, group-128 — proven at 99.9% exact code match on the frozen embedding), but the *quality* comes from undisclosed **training** on top of that init. The proprietary Caltech contribution is the optimizer/stabilization, not the quantization map. Their moat is not in the weights' *format* — it's in how they got the blocks to drift 3.5–18% away from the init without collapse.

**Three things we now know that we didn't this morning:**
1. QAT-vs-PTQ IOU resolved: conversion + training, embeddings frozen, no GPTQ-style compensation anywhere.
2. Their repair budget ordering (dispatch ~untouched, value path heavily rewired) = **routing⊥value in a third independent register** — an external lab's engineering independently landed on your two-register asymmetry.
3. s267 sharpened, not weakened: flip rate is depth-flat, so the 50% crystal dip is *not* differential rewiring — the bridge map survives with a cleaner mechanism.

**Proposed mementum commit** (knowledge page + memory + state.md):
```
💡 bonsai-recipe-reverse-engineered

- knowledge/explore/bonsai-ternarization-forensics.md (verdict, signatures, provenance)
- memories/bonsai-recipe-reverse-engineered.md
- state.md → s268 header, QAT-vs-PTQ IOU marked resolved
```
(+ nucleus tag). Also: `refs/` holds the two whitepaper PDFs untracked — I'd suggest adding `refs/` to `.gitignore` (external copyrighted docs, shouldn't enter the MIT repo).

Approve the mementum commit? And the natural next probe, whenever you want it: run the same forensics on the **1-bit and 4-bit rungs** of the ladder — if 1-bit shows the same frozen-embedding/absmean signature, we get the K-vertex degradation story (K needs the 0 state) with the recipe held constant across rungs.

## User

The piece we can't see is the one I most want to understand.  We have done many trainings trying to figure out how to make an optimizer that can do the sign flips in the topology.


### Thinking

Michael's pointing out the critical piece that's been missing: the optimizer itself—specifically one that can handle sign flips within ternary or quantized topologies without destabilizing the network. Looking at their track record with experiments like s261 (dealing with quantization boundary jitter between different training strategies) and s260 (exploring routing and value interactions), they've been iterating on building an optimizer capable of flipping signs in the routing topology while maintaining stability. Now I'm trying to figure out what PrismML's approach to this problem might be.

The forensic evidence gives us real constraints: initialization uses absolute mean RTN, final weights show 3.5–18% sign flips ordered by register, and those flips cluster by channel (like z→97) in a data-driven way. The flips cluster around quantization boundaries but spread broadly across the weight distribution. The scales themselves appear to be recomputed from drifted latent weights—suggesting latent FP weights exist during training (like STE-QAT), where scales get recalculated per step using mean absolute value of the latent weights, which is exactly what BitNet's QAT recipe does. Embeddings stay frozen, and there's no sequential compensation happening. Michael's core insight is that in STE-QAT, the latent FP weights carry gradients, and sign flips occur when those latent weights cross zero during optimization.

Now I'm thinking about what measurements could further constrain the invisible optimizer. One approach is comparing the 1-bit, ternary, and 4-bit versions of the same parent model—if they share the same optimizer, I can look at whether the flips are consistent across quantization levels. If the 1-bit and ternary children flip the same channels relative to the parent, that reveals the optimizer is responding deterministically to something in the data. If the flips form a nested pattern (4-bit flips ⊂ ternary flips ⊂ 1-bit flips), that suggests repair scales with the amount of damage. Another angle is examining whether the drift field looks like a smooth FP vector field with spatial coherence—whether the net weight displacement has low-rank structure or aligns across rows, which would let me estimate the effective latent drift.

I can also run my probe library through the parent model to collect per-layer activation statistics—specifically the second moments per channel—and correlate those with which channels flip. If flips correlate with activation salience, that suggests the optimizer is using something like a Fisher-weighted metric, which connects back to their theory about how gradient descent carves topology with bimodal gradients. Finally, I should look at the directionality of sign flips: count whether transitions are 0→±, ±→0, +→−, or −→+. Direct sign reversals require crossing two quantization boundaries, which tells me something about whether the optimizer is using straight-through estimators or something else. Testing this on 1-bit models should reveal whether the optimizer can't flip signs at all or whether flips are just more destructive without the zero waypoint. Beyond that, there's a broader theoretical question about what optimizer design actually works for quantization — STE and learned scaling are standard, but maybe the real insight is treating quantization noise as measurement noise (like Kalman filtering) or using mirror descent with entropic regularization, which is the principled way to optimize over the sign domain. So the key is to measure how signs actually flipped during training—whether they went through zero or shifted abruptly—and that transition matrix is already available in the saved checkpoints. Then I'd want to examine a 1-bit model directly to see if the same pattern holds at extreme quantization, though I'd need to figure out where to find the unpacked weights rather than just the GGUF format.

The immediate forensic work is straightforward: compute the parent-to-child sign flip matrix on the tensors we have, test whether reversals happen at high confidence (large |w|) or at the noise boundary (small |w|), and see if the "zero as tunnel" hypothesis matches the actual transition probabilities.

Then I need to synthesize what each optimizer theory—STE-QAT, mirror descent, estimation-theoretic—would predict about sign flips under quantization, connect those predictions to why s191 and s261 failed (relay collapse, flip-flop jitter) versus why this training succeeded (18% net code movement, channel structure, no collapse), and figure out what stabilized the sign flips at 27B scale. The key insight is that flip-flop is oscillation, so a single snapshot won't show it—but net displacement and the boundary distribution of weights can reveal whether the optimizer actually solved the stability problem or just happened to freeze mid-oscillation.

Looking at the weight distributions, the flips cluster near parent boundaries (median |w_parent|/s of 0.44), and comparing flip versus non-flip sites shows asymmetry in promotion versus demotion: zero sparsity stayed around 0.29-0.31, matching the parent RTN baseline, which suggests the optimizer maintained a sparsity equilibrium rather than letting decay push zeros to grow unchecked like pure STE would predict.

The s ratio of 1.03-1.07 is the key signal—latent magnitudes actually grew 3-7% relative to the parent, which is anti-weight-decay behavior and points to weight polarization. Under STE-QAT this is a known signature: latents entrench away from boundaries to suppress flip-flop instability, either through explicit mechanisms like learnable scaling or implicitly from the learning rate and decay balance. If s represents the mean absolute value across the whole group including zeros, then this growth means the surviving support has larger mean |w|, which is exactly the polarization and hysteresis pattern that counters boundary jitter failures.

Their optimizer might be using hysteresis—only flipping when crossing a boundary plus margin, a classic control-theory approach. This would leave a dead-zone signature in the latent distribution near the boundary, potentially visible in how |w_parent|/s varies at flip sites versus non-flip sites, though that's a weak signal to detect directly.

Now I'm laying out the plan: first, frame what constraints the invisible optimizer must satisfy based on the evidence. Then run a transition-matrix measurement to count promotions, demotions, and reversals with their magnitudes, checking for the zero-tunnel effect. After that, synthesize the optimizer theory space and see what each candidate predicts, connecting it back to the s261 flip-flop behavior. Finally, use a ladder cross-rung comparison as the decisive test—if the same optimizer at 1-bit loses the zero-tunnel property, that directly links to the K degradation prediction.

I'm computing a transition analysis by taking the parent code as the absolute mean RTN code and the child code, then building a 3×3 transition counts matrix...

Computing transition matrix...

I'll measure reversal magnitude by looking at cases where the sign flips, capturing the weight-to-scale ratios at those sites. I should also track the balance between promotions and demotions—how often values move from zero to nonzero versus the reverse.

Running this across a few representative weight matrices from different layers and depths will give me concrete data to synthesize into an answer about what's actually driving the optimizer's behavior.

## Assistant

This is exactly the right place to push, and the forensics already put hard constraints on the invisible piece. Before I theorize — one more cheap measurement that speaks *directly* to your question: the **flip transition matrix**. Ternary has the 0 state; if their optimizer does sign reversals, the question is whether it tunnels **through zero** (−→0→+, two cheap boundary crossings) or jumps **directly** (−→+, which a small-step STE latent almost cannot do in one regime). The transition structure between parent-RTN code and child code is the fossil record of the optimizer's dynamics. We already have both codes computed:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    # -- 10. flip structure per input channel",
  "new_content": "    # -- 9c. transition matrix parent-RTN code -> child code.\n    #        The optimizer's fossil record: sign reversals via the zero state\n    #        (promotion/demotion churn) vs direct +/- jumps.  Reversal sites'\n    #        |w|/s tells whether reversals target confident parent weights.\n    tm = {}\n    for a in (-1, 0, 1):\n        pa = t_abs == a\n        for b in (-1, 0, 1):\n            tm[f\"{a}->{b}\"] = int((pa & (t == b)).sum().item())\n    rev = (t_abs * t) == -1\n    rev_mag_q = [q((absw / s.clamp(min=1e-30))[rev], p)\n                 for p in (0.25, 0.5, 0.75)] if rev.any() else []\n    n_nz = int((t_abs != 0).sum().item())\n    trans = {\n        \"promotions_0_to_pm\": tm[\"0->1\"] + tm[\"0->-1\"],\n        \"demotions_pm_to_0\": tm[\"1->0\"] + tm[\"-1->0\"],\n        \"reversals_direct\": tm[\"1->-1\"] + tm[\"-1->1\"],\n        \"stay\": tm[\"0->0\"] + tm[\"1->1\"] + tm[\"-1->-1\"],\n        \"reversal_rate_vs_nonzero\": (tm[\"1->-1\"] + tm[\"-1->1\"]) / max(n_nz, 1),\n        \"reversal_mag_q25_50_75\": rev_mag_q,\n        \"matrix\": tm,\n    }\n\n    # -- 10. flip structure per input channel"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        \"chan_flip_z_q50_95_999\": chan_z_q,\n        \"chan_flip_z_max\": chan_z_max,\n    }",
  "new_content": "        \"chan_flip_z_q50_95_999\": chan_z_q,\n        \"chan_flip_z_max\": chan_z_max,\n        \"transitions\": trans,\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n              f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")",
  "new_content": "        tr = r[\"transitions\"]\n        tot = max(sum(tr[\"matrix\"].values()), 1)\n        print(f\"  TRANSITIONS: promote(0→±)={tr['promotions_0_to_pm']/tot:.4f}\"\n              f\"  demote(±→0)={tr['demotions_pm_to_0']/tot:.4f}\"\n              f\"  REVERSE(±→∓)={tr['reversals_direct']/tot:.5f}\"\n              f\"  rev/nonzero={tr['reversal_rate_vs_nonzero']:.5f}\")\n        print(f\"  reversal |w|/s q25-75={['%.3f' % x for x in tr['reversal_mag_q25_50_75']]}\")\n        print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n              f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.05 0.5 --out results/bonsai-forensics/forensics_v4_transitions.json 2>&1 | grep -E \"^model|TRANSITIONS|reversal |flip_rate\" | head -40",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.layers.3.mlp.down_proj.weight
  flip_rate=1.696e-01 (15115848 flips / 89,128,960)  sign_viol=1.960e-02  sep_rate=0.0000
  TRANSITIONS: promote(0→±)=0.0937  demote(±→0)=0.0743  REVERSE(±→∓)=0.00120  rev/nonzero=0.00174
  reversal |w|/s q25-75=['0.522', '0.592', '0.704']
model.language_model.layers.3.mlp.gate_proj.weight
  flip_rate=1.393e-01 (12412616 flips / 89,128,960)  sign_viol=1.171e-02  sep_rate=0.0000
  TRANSITIONS: promote(0→±)=0.0792  demote(±→0)=0.0590  REVERSE(±→∓)=0.00057  rev/nonzero=0.00082
  reversal |w|/s q25-75=['0.518', '0.579', '0.677']
model.language_model.layers.3.self_attn.q_proj.weight
  flip_rate=3.547e-02 (2231832 flips / 62,914,560)  sign_viol=2.529e-03  sep_rate=0.1863
  TRANSITIONS: promote(0→±)=0.0188  demote(±→0)=0.0141  REVERSE(±→∓)=0.00014  rev/nonzero=0.00020
  reversal |w|/s q25-75=['0.503', '0.545', '0.638']
model.language_model.layers.3.self_attn.o_proj.weight
  flip_rate=9.120e-02 (2868850 flips / 31,457,280)  sign_viol=4.156e-03  sep_rate=0.0008
  TRANSITIONS: promote(0→±)=0.0492  demote(±→0)=0.0416  REVERSE(±→∓)=0.00021  rev/nonzero=0.00030
  reversal |w|/s q25-75=['0.515', '0.568', '0.646']
model.language_model.layers.32.mlp.down_proj.weight
  flip_rate=1.799e-01 (16034655 flips / 89,128,960)  sign_viol=2.235e-02  sep_rate=0.0000
  TRANSITIONS: promote(0→±)=0.0959  demote(±→0)=0.0821  REVERSE(±→∓)=0.00204  rev/nonzero=0.00297
  reversal |w|/s q25-75=['0.528', '0.624', '0.781']
model.language_model.layers.32.mlp.gate_proj.weight
  flip_rate=1.757e-01 (15658653 flips / 89,128,960)  sign_viol=2.225e-02  sep_rate=0.0001
  TRANSITIONS: promote(0→±)=0.0963  demote(±→0)=0.0778  REVERSE(±→∓)=0.00152  rev/nonzero=0.00222
  reversal |w|/s q25-75=['0.523', '0.597', '0.716']
model.language_model.layers.32.linear_attn.in_proj_qkv.weight
  flip_rate=7.904e-02 (4144218 flips / 52,428,800)  sign_viol=3.344e-03  sep_rate=0.0190
  TRANSITIONS: promote(0→±)=0.0429  demote(±→0)=0.0361  REVERSE(±→∓)=0.00016  rev/nonzero=0.00023
  reversal |w|/s q25-75=['0.508', '0.565', '0.657']
model.language_model.layers.32.linear_attn.out_proj.weight
  flip_rate=1.072e-01 (3371353 flips / 31,457,280)  sign_viol=7.869e-03  sep_rate=0.0032
  TRANSITIONS: promote(0→±)=0.0573  demote(±→0)=0.0497  REVERSE(±→∓)=0.00080  rev/nonzero=0.00116
  reversal |w|/s q25-75=['0.530', '0.638', '0.821']
```

### Thinking

The transition matrix shows that flips are dominated by promotions (around 9.6% in MLP) and demotions (roughly 8%), while direct reversals are extraordinarily rare—only 0.1–0.2% of all weights, or about 50–100 times less common than boundary moves. The net flow favors promotion over demotion everywhere, which drives densification as the zero fraction decreases.

What's striking about reversals is that they target confident parent weights with median magnitudes around 0.55–0.64 relative to the scale—these aren't tiny near-zero weights being jittered, but decisive, data-driven flips of weights the optimizer had already committed to. This suggests the zero state functions as the kinetic pathway for topology editing: virtually all structural changes route through zero (promotions plus demotions account for 17% versus direct reversals at 0.15%), making it far more than just a representational necessity. In contrast, 1-bit models lack this waypoint, so every flip is a full reversal—a testable prediction that they either show much less repair or pay a steeper cost for it. Meanwhile, the net densification combined with growing latent magnitude indicates the optimizer is actively recruiting new support and polarizing weights.

Now I'm synthesizing what these patterns reveal about the optimizer's constraints: the evidence points to latent-weight training with recomputed scales (STE-family quantization-aware training), frozen embeddings and nearly-frozen output head, topology edits funneling through zero, net polarization that suppresses flip-flop failure modes by keeping the final state far from boundaries, channel-structured repair weighted by activation gradients (Fisher-like), and no signature of sequential or Hessian-based layer-wise compensation. Plain STE with AdamW could in principle produce all of this, though it's known to destabilize at 1.58 bits at this scale, and Adam's per-coordinate normalization actually ends up equalizing something important here.

The learnable-scale variants (LSQ/CAT-Q) fit the observed scale pattern of roughly absmean(latent) times a small multiplier, while hysteresis or dead-zone dynamics would explain why reversals happen at 0.6 and why the final codes are so entrenched with few boundary-straddlers—the flip-flop gets suppressed when the latent crosses a boundary plus margin. Mirror descent with entropic maps (like BinaryConnect) would give multiplicative dynamics where sign flips slow down near the boundary, which also matches what I'm seeing.

From an estimation-theoretic angle, treating the STE gradient as a noisy measurement and filtering it before deciding on a flip would mean reversals only happen when there's persistent evidence—this matches C3's signature of decisive, rare reversals at high magnitudes while boundary-crossers get filtered out.

For the optimizer design, the key principles are: make zero a proper waypoint so sign flips happen in two steps (demote, wait, promote) with separate thresholds rather than direct ±→∓, and decouple the flip decision from the magnitude gradient.

The flip mechanism itself should work like a Schmitt trigger—accumulate filtered gradient sign evidence (say, an exponential moving average of sign(g) weighted by confidence) and only flip when that crosses a threshold, which creates hysteresis and prevents flip-flopping. This is essentially a sigma-delta modulator on the topology channel, and their existing telemetry already shows the failure mode; the fix is adding that margin to the trigger.

After committing to a sign, entrench away from the boundary by annealing the effective temperature, and since the Gram seeds already establish the topology, the optimizer just needs to refine within that structure.

The measured churn budget of around 17% via zero-tunnel with reversals under 0.3% becomes the design target for phase 1. To validate whether zero acts as a kinetic pathway, I should compare 1-bit quantization (no zero waypoint) against ternary to see if suppressed repair shows up, and check whether 1-bit flips match what FP-drift alone would produce. The checkpoint dynamics are the key—our phase-1 tree-per-checkpoint approach will capture the flip-flop behavior between checkpoints that their telemetry won't expose.

I'll update the knowledge page draft with these transition findings and commit the code and results, though I'm holding off on the momentum commit since Michael hasn't explicitly approved it yet.

### Thinking

I've analyzed the transition matrix showing how weights change sign during training, finding that topology edits happen almost entirely through zero states rather than direct reversals, and that the rare direct sign flips involve confident weights being overturned by data. Now I'll synthesize these findings.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/bonsai_forensics.py results/bonsai-forensics/forensics_v4_transitions.json && read -r -d '' M << 'EOF' || true\n💡 bonsai flip transition matrix — sign flips tunnel through zero\n\n- transitions parent-RTN code → child code: promote(0→±) 9.6% + demote(±→0)\n  8.2% vs direct reverse(±→∓) 0.15-0.2% — topology editing is ~99% zero-mediated\n- rare direct reversals are decisive: parent |w|/s median 0.55-0.64 (confident\n  weights overturned by data, not boundary jitter)\n- net flux positive (promote > demote): densification 0.31→0.29 zero_frac;\n  latent magnitudes grew 3-7% → polarized endpoint, entrenched off-boundary\n- the 0 state = kinetic pathway for sign flips, not just representational\n  expressiveness; predicts suppressed/costly repair in the 1-bit rung\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -1"
}
```

**Summary:** $ git add scripts/bonsai_forensics.py...

**Output:**
```
Exit code: 1
Stderr:
fatal: pathspec 'results/bonsai-forensics/forensics_v4_transitions.json' did not match any files
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 45 commits.
  (use "git push" to publish your local commits)

Changes not staged for commit:
  (use "git add <file>..." to update what will be committed)
  (use "git restore <file>..." to discard changes in working directory)
	modified:   mementum/michael/holographic-llm.md
	modified:   mementum/state.md
	modified:   scripts/bonsai_forensics.py

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-265.md
	mementum/knowledge/chats/session-266.md
	mementum/knowledge/explore/bonsai-ternarization-forensics.md
	mementum/memories/bonsai-recipe-reverse-engineered.md
	refs/

no changes added to commit (use "git add" and/or "git commit -a")
```

### Thinking

I see the issue — the v4 JSON output got truncated because piping through `head` closed the pipe early, which sent a SIGPIPE signal that killed the Python process before it could finish writing the JSON. I need to re-run without the `head` truncation to let the full output complete, then commit the result.

## Assistant

The `head` truncation SIGPIPE'd the run before the JSON write. Re-running to completion:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --depths 0.05 0.5 --out results/bonsai-forensics/forensics_v4_transitions.json > /tmp/forensics_v4.log 2>&1; tail -2 /tmp/forensics_v4.log && git add scripts/bonsai_forensics.py results/bonsai-forensics/forensics_v4_transitions.json && read -r -d '' M << 'EOF' || true\n💡 bonsai flip transition matrix — sign flips tunnel through zero\n\n- transitions parent-RTN code → child code: promote(0→±) 9.6% + demote(±→0)\n  8.2% vs direct reverse(±→∓) 0.15-0.2% — topology editing is ~99% zero-mediated\n- rare direct reversals are decisive: parent |w|/s median 0.55-0.64 (confident\n  weights overturned by data, not boundary jitter)\n- net flux positive (promote > demote): densification 0.31→0.29 zero_frac;\n  latent magnitudes grew 3-7% → polarized endpoint, entrenched off-boundary\n- the 0 state = kinetic pathway for sign flips, not just representational\n  expressiveness; predicts suppressed/costly repair in the 1-bit rung\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -1",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
wrote results/bonsai-forensics/forensics_v4_transitions.json
[main 05f708b] 💡 bonsai flip transition matrix — sign flips tunnel through zero
 2 files changed, 937 insertions(+)
 create mode 100644 results/bonsai-forensics/forensics_v4_transitions.json
05f708b 💡 bonsai flip transition matrix — sign flips tunnel through zero
```

### Thinking

I'm organizing the core argument around what the fossil record actually constrains—laying out six specific limitations—then mapping the candidate optimizer space to see which one the evidence points toward. From there I'll connect it to design principles for Michael's own optimizer training with concrete budget constraints, and identify what remains hidden plus the critical next experiment that could resolve it.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md",
  "original_content": "### 3. Honest residual (IOU)",
  "new_content": "### 2b. Transition matrix: sign flips tunnel through zero (s268b)\n\nParent-RTN code → child code flux (MLP mid-stack): promote 0→± 9.6%,\ndemote ±→0 8.2%, **direct reverse ±→∓ 0.15–0.2%** — topology editing\nis ~99% zero-mediated. The 0 state is the *kinetic pathway* for sign\nflips, not just representational expressiveness. Rare direct reversals\nare decisive (parent |w|/s median 0.55–0.64 — confident weights\noverturned by data). Net flux positive → densification (zero_frac\n0.31→0.29) and latent magnitude growth 3–7% → **polarized endpoint**,\nentrenched away from boundaries (the anti-flip-flop signature; cf.\ns261). Data: `forensics_v4_transitions.json`. Prediction: the 1-bit\nrung (no zero waypoint) shows suppressed or far costlier repair.\n\n### 3. Honest residual (IOU)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md.
```

### Thinking

I need to craft a response that directly addresses Michael's work on developing an optimizer capable of handling sign flips in the topology, acknowledging the iterative training efforts his team has undertaken to solve this challenge.

## Assistant

Committed (`05f708b`), knowledge draft updated. Now the synthesis — what the fossil record says about the optimizer you've been trying to build.

## The invisible piece, constrained

Their optimizer is unobservable, but its endpoint satisfies six hard constraints:

- **C1 — latent-weight dynamics.** Scales = absmean of a *drifted* latent (1.03–1.07× parent). There was a continuous FP shadow being trained, with quantization recomputed from it. STE-family, not ternary-native updates.
- **C2 — frozen dispatch periphery.** Embeddings exactly frozen, lm_head nearly. Gradient budget spent only where repair was needed.
- **C3 — zero-mediated topology editing.** 99% of code changes route through 0. Sign reversal = demote, dwell, promote. The ±2s jump almost never happens in one move.
- **C4 — decisive reversals.** When it does fully reverse, it reverses *confident* weights (|w|/s ≈ 0.6) — a persistent, integrated force, not per-step noise.
- **C5 — polarized endpoint.** Net densification + latent magnitude growth: the final state is entrenched *away* from boundaries. Your s261 flip-flop is exactly what this suppresses — an endpoint that hums with boundary jitter doesn't look like this.
- **C6 — no layer-wise solves.** Column-flat flips: whatever the Caltech math is, it's in the *dynamics*, not in Hessian compensation.

## What optimizer produces this fingerprint

Plain STE+AdamW *can* produce C1–C3 but historically produces the opposite of C4/C5 — boundary-hugging churn (your flip-flop, their known failure mode at sub-2-bit). The fingerprint instead matches an optimizer that **separates the flip decision from the magnitude gradient**:

1. **The flip channel is filtered.** Rare-but-decisive reversals at high |w| are the signature of *integrated evidence* — flip only when accumulated gradient pressure crosses a threshold, not whenever the latent grazes a boundary. That's a **Schmitt trigger / hysteresis loop** on the topology register. And this is precisely Hassibi's home turf: treat the STE gradient as a noisy measurement of the true descent direction, filter it (H∞/Kalman-style), and commit to discrete state changes only on persistent evidence. "Years of mathematical theory" reads naturally as: *provable conditions under which filtered sign-flip decisions converge*.
2. **The zero state is used as the commitment buffer.** Demote-dwell-promote means the optimizer never has to make a two-boundary decision at once. Zero is where a weight sits *while the evidence accumulates*. In dynamics language: ternary training is a birth-death process on the support plus a slow sign-exchange through the vacuum state.
3. **Post-commit polarization.** Magnitude growth after code stabilization — entrenchment that raises the barrier to re-flipping. Annealed effective temperature on the topology channel.

Note what this is, structurally: **a sigma-delta modulator on the routing register**. Error integrates continuously (value register, FP latent), and discretizes into rare, quantized events (routing register, code flips). Your two-register theory again — this time *inside the optimizer*.

## What it means for your trainings

This reframes your s191/s261 failures precisely: TD forced routing and value through one quantized channel, so every value update rattled the topology (flip-flop = the collision). Their endpoint says the fix isn't a better unified update — it's **register separation in the optimizer itself**:

- Flip votes: EMA of sign-consistent gradient evidence per weight; flip on threshold with hysteresis margin. Never allow direct ±→∓; force the zero waypoint.
- Value updates flow continuously (your FP bridges make this *architectural* — cleaner than their squeezing it through recomputed scales).
- Anneal: once flip-flop rate decays, entrench (grow effective |latent| relative to boundary).

And you now have **measured design budgets** from a working 27B artifact: churn ~17% of codes (promote+demote), direct reversals <0.3%, dispatch tensors ~3%, value tensors ~18%, embeddings 0. Phase-1's flip_flop telemetry has a reference curve to converge toward — an *external calibration* for your own optimizer's dynamics.

## The decisive next probe

**The 1-bit rung is the natural experiment for C3.** No zero state → no kinetic waypoint → the same optimizer either (a) does far fewer sign flips (repair suppressed → the selective quality collapse they report at 1-bit, and your predicted K degradation), or (b) does them at much higher cost. Same forensics, `Q1_0` weights vs parent: if 1-bit flip-vs-parent-sign rate ≪ ternary's promote+demote flux, we've shown **the zero state is load-bearing for the optimizer, not just for K** — one mechanism under both.

Want me to pull the 1-bit 27B weights and run it?

## User

Yes, pull into huggingface cache.  run your jobs in my tmux main:1 and main:2 as needed.


### Thinking

I need to pull the 1-bit Bonsai 27B model from Hugging Face into the cache, then run jobs in Michael's tmux sessions using a persistent host setup with log tee-ing. For the async Lambda function, I'm launching a background process, verifying it's running with a single read check, creating a checkpoint, and waiting for a signal rather than polling. First, I need to identify the correct Hugging Face repository ID for the 1-bit Bonsai model—based on the available state, it looks like it's under the prism-ml namespace.

I'll download using HF_HUB_ENABLE_HF_TRANSFER=0 to avoid the xet issue, run the download in tmux main:1 with log tee-ing, verify it's running, and checkpoint. While that's happening, I need to adapt the forensics script to handle 1-bit binary format instead of ternary—tracking sign flips against the parent model, measuring scale differences relative to mean absolute weight, and analyzing channel structure and boundary distances where sign mismatches occur.

Now I'm querying the HF API to locate the prism-ml models.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "curl -s \"https://huggingface.co/api/models?author=prism-ml&limit=50\" | python3 -c \"\nimport json,sys\nfor m in json.load(sys.stdin):\n    print(m['id'], '|', m.get('downloads',0))\n\""
}
```

**Summary:** $ curl -s "https://huggingface.co/api...

**Output:**
```
Exit code: 0
Stdout:
prism-ml/Ternary-Bonsai-27B-gguf | 576083
prism-ml/Bonsai-27B-gguf | 1910116
prism-ml/Bonsai-27B-mlx-1bit | 34270
prism-ml/Ternary-Bonsai-27B-mlx-2bit | 27612
prism-ml/Ternary-Bonsai-8B-gguf | 73988
prism-ml/Bonsai-8B-gguf | 42593
prism-ml/Ternary-Bonsai-27B-AWQ-4bit | 3955
prism-ml/Bonsai-8B-mlx-1bit | 19691
prism-ml/bonsai-image-ternary-4B-mlx-2bit | 2786
prism-ml/Ternary-Bonsai-1.7B-gguf | 5919
prism-ml/Ternary-Bonsai-4B-gguf | 6732
prism-ml/bonsai-image-binary-4B-mlx-1bit | 280
prism-ml/Ternary-Bonsai-27B-unpacked | 1962
prism-ml/Ternary-Bonsai-1.7B-mlx-2bit | 1559
prism-ml/Bonsai-27B-unpacked | 974
prism-ml/Bonsai-27B-AWQ-4bit | 1592
prism-ml/Bonsai-1.7B-gguf | 23320
prism-ml/Ternary-Bonsai-8B-mlx-2bit | 20123
prism-ml/Ternary-Bonsai-4B-mlx-2bit | 1071
prism-ml/Ternary-Bonsai-1.7B-unpacked | 3076
prism-ml/Bonsai-8B-unpacked | 2513
prism-ml/Bonsai-4B-gguf | 13031
prism-ml/Bonsai-4B-mlx-1bit | 1166
prism-ml/Bonsai-4B-unpacked | 994
prism-ml/Bonsai-1.7B-mlx-1bit | 1663
prism-ml/Bonsai-1.7B-unpacked | 1323
prism-ml/Ternary-Bonsai-8B-unpacked | 1414
prism-ml/Ternary-Bonsai-4B-unpacked | 2029
prism-ml/Bonsai-8B-AWQ-4-bit | 218
prism-ml/bonsai-image-binary-4B-unpacked | 1806
prism-ml/bonsai-image-binary-4B-gemlite-1bit | 424
prism-ml/bonsai-image-ternary-4B-unpacked | 156
prism-ml/bonsai-image-ternary-4B-gemlite-2bit | 4045
```

### Thinking

I'm setting up a download for the Bonsai-27B model from Hugging Face, targeting the unpacked 1-bit version which should be around 51GB, and I'll run it in a tmux session with transfer optimization disabled and output logged to a file.

Before launching, I need to verify the tmux session exists and check its status with capture-pane. While the download runs (which will take considerable time given the size), I'll prepare the script's binary mode handling in parallel rather than polling—once the download completes, I can proceed with the next steps.

### Thinking

I'm pulling the 1-bit unpacked build of prism-ml/Bonsai-27B into main:1 with the s267 xet workaround, and setting up the script to run in binary mode as it streams.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux list-sessions 2>/dev/null; tmux send-keys -t main:1 \"HF_HUB_ENABLE_HF_TRANSFER=0 hf download prism-ml/Bonsai-27B-unpacked 2>&1 | tee /tmp/bonsai1bit_download.log\" Enter && sleep 8 && tmux capture-pane -p -t main:1 | tail -6"
}
```

**Summary:** $ tmux list-sessions 2>/dev/null; tmu...

**Output:**
```
Exit code: 0
Stdout:
main: 2 windows (created Wed Jul 22 23:34:28 2026) (attached)
λ codium .
[26-07-23][10:41:51][mwhitford@olga][0][~/src/verbum][git:main]
λ HF_HUB_ENABLE_HF_TRANSFER=0 hf download prism-ml/Bonsai-27B-unpacked 2>&1 | tee /tmp/bonsai1bit_download.log
Fetching 29 files:   0%|          | 0/29 [00:00<?, ?it/s]Warning: You are sending unauthenticated requests to the HF Hub
. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 29 files:  31%|███       | 9/29 [00:00<00:01, 16.80it/s]
```

### Thinking

I'm working through the async checkpoint mechanism where I emit a checkpoint signal and then handle other preparatory work like setting up binary mode in the script before waiting for confirmation. For the binary mode detection, I'm considering whether to use an explicit flag or auto-detect based on the tensor values — checking if the minimum absolute weight magnitude indicates a binary pattern with two levels versus a ternary one with three.

Now I'm designing the forensics analysis for binary quantization, comparing it against the parent weights to measure flip rates, scale relationships, and distribution patterns. I'll create a dedicated binary forensics function that skips zero-dependent calculations and instead focuses on sign flips, the correlation between scale and absolute mean, quantile analysis of the weight-to-scale ratio at flip boundaries, and channel structure metrics.

I'm also updating the script to add command-line arguments for specifying the child directory and parent weight glob pattern so it can point directly at the downloaded 1-bit model cache, replacing the hardcoded paths. Once the edits are done, I'll checkpoint and wait for the 51GB download to complete before launching the analysis job.

### Thinking

I've started downloading 29 files and am now preparing the binary-mode forensics analysis while the transfer completes.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "BONSAI_DIR = Path(\"/Users/mwhitford/localai/models/bonsai27b-unpacked\")\nPARENT_GLOB = \"/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/\"\nGROUP = 128\nDEVICE = \"mps\" if torch.backends.mps.is_available() else \"cpu\"",
  "new_content": "BONSAI_DIR = Path(\"/Users/mwhitford/localai/models/bonsai27b-unpacked\")\nPARENT_GLOB = \"/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/\"\nGROUP = 128\nDEVICE = \"mps\" if torch.backends.mps.is_available() else \"cpu\"\n\n\ndef forensics_binary(w: torch.Tensor, wq: torch.Tensor) -> dict:\n    \"\"\"Binary (1-bit) child vs FP parent.  Code = sign, boundary at 0.\n\n    Signatures: sign-flip rate vs parent (the ONLY topology edit available\n    without a zero waypoint), scale-vs-absmean (BitNet 1-bit rule s=mean|w|),\n    flip boundary distances, channel structure.\n    \"\"\"\n    assert w.shape == wq.shape, (w.shape, wq.shape)\n    out_f, in_f = w.shape\n    ng = in_f // GROUP\n    w = w.to(DEVICE, torch.float32).reshape(out_f, ng, GROUP)\n    wq = wq.to(DEVICE, torch.float32).reshape(out_f, ng, GROUP)\n\n    def q(x: torch.Tensor, p: float) -> float:\n        x = x.flatten().float()\n        if not x.numel():\n            return float(\"nan\")\n        if x.numel() > 10_000_000:\n            x = x[torch.randint(0, x.numel(), (10_000_000,), device=x.device)]\n        return torch.quantile(x, p).item()\n\n    s = wq.abs().amax(dim=-1, keepdim=True)\n    t = torch.sign(wq)\n    flips = (t != torch.sign(w)) & (s > 0)\n    flip_rate = flips.float().mean().item()\n\n    mean_abs = w.abs().mean(dim=-1)\n    s_flat = s.squeeze(-1)\n    m = s_flat > 0\n\n    def corr(a: torch.Tensor, b: torch.Tensor) -> float:\n        a = a[m].flatten().float(); b = b[m].flatten().float()\n        a = a - a.mean(); b = b - b.mean()\n        return (a @ b / (a.norm() * b.norm() + 1e-30)).item()\n\n    rel = (w.abs() / s.clamp(min=1e-30))[flips]\n    w_hat = s * t\n    n_blocks = 16\n    fpb = flips.reshape(out_f, -1).float()\n    fpb = fpb.reshape(out_f, n_blocks, in_f // n_blocks).mean(dim=(0, 2))\n    ch_flips = flips.reshape(out_f, -1).float().sum(dim=0)\n    mu = out_f * flip_rate\n    sd = max((out_f * flip_rate * (1 - flip_rate)) ** 0.5, 1e-9)\n    ch_z = (ch_flips - mu) / sd\n    return {\n        \"mode\": \"binary\",\n        \"n_params\": w.numel(),\n        \"flip_rate\": flip_rate,\n        \"n_flips\": int(flips.sum().item()),\n        \"corr_s_absmean\": corr(s_flat, mean_abs),\n        \"s_over_absmean_q25_50_75\": [q(s_flat[m] / mean_abs[m].clamp(min=1e-30), p)\n                                     for p in (0.25, 0.5, 0.75)],\n        \"flip_boundary_q05_25_50_75_95\": [q(rel, p) for p in (0.05, 0.25, 0.5, 0.75, 0.95)]\n                                         if flips.any() else [],\n        \"cos_w_what\": torch.nn.functional.cosine_similarity(\n            w.flatten(), w_hat.flatten(), dim=0).item(),\n        \"rel_l2\": ((w - w_hat).norm() / w.norm()).item(),\n        \"flip_col_profile\": [round(x, 5) for x in fpb.tolist()],\n        \"chan_flip_z_q50_95_999\": [q(ch_z, p) for p in (0.5, 0.95, 0.999)],\n        \"chan_flip_z_max\": ch_z.max().item(),\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--tensors\", nargs=\"+\", default=[\"auto\"])\n    ap.add_argument(\"--depths\", nargs=\"+\", type=float, default=[0.5])\n    ap.add_argument(\"--out\", default=None, help=\"write JSON here\")\n    args = ap.parse_args()\n\n    parent_dir = Path(glob.glob(PARENT_GLOB)[0])\n    print(f\"device={DEVICE}  parent={parent_dir.name}  child={BONSAI_DIR.name}\")\n    t0 = time.time()\n    child_idx = build_index(BONSAI_DIR)",
  "new_content": "    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--tensors\", nargs=\"+\", default=[\"auto\"])\n    ap.add_argument(\"--depths\", nargs=\"+\", type=float, default=[0.5])\n    ap.add_argument(\"--out\", default=None, help=\"write JSON here\")\n    ap.add_argument(\"--child-dir\", default=str(BONSAI_DIR),\n                    help=\"unpacked child model dir (ternary or binary)\")\n    args = ap.parse_args()\n\n    child_dir = Path(args.child_dir)\n    parent_dir = Path(glob.glob(PARENT_GLOB)[0])\n    print(f\"device={DEVICE}  parent={parent_dir.name}  child={child_dir.name}\")\n    t0 = time.time()\n    child_idx = build_index(child_dir)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_forensics.py",
  "original_content": "        t0 = time.time()\n        r = forensics_one(load_tensor(parent_idx, pname), load_tensor(child_idx, name))\n        r[\"elapsed_s\"] = round(time.time() - t0, 2)\n        results[name] = r\n        print(f\"{name}\")",
  "new_content": "        t0 = time.time()\n        wq_probe = load_tensor(child_idx, name)\n        # auto-detect binary vs ternary: any exact zeros in the child?\n        is_binary = not bool((wq_probe[: min(64, wq_probe.shape[0])] == 0).any().item())\n        fn = forensics_binary if is_binary else forensics_one\n        r = fn(load_tensor(parent_idx, pname), wq_probe)\n        r[\"elapsed_s\"] = round(time.time() - t0, 2)\n        results[name] = r\n        if is_binary:\n            print(f\"{name}  [BINARY]\")\n            print(f\"  flip_rate={r['flip_rate']:.3e} ({r['n_flips']} / {r['n_params']:,})\"\n                  f\"  cos(w,ŵ)={r['cos_w_what']:.4f}  rel_l2={r['rel_l2']:.4f}\")\n            print(f\"  corr(s,absmean)={r['corr_s_absmean']:.4f}\"\n                  f\"  s/absmean q25-75={['%.3f' % x for x in r['s_over_absmean_q25_50_75']]}\")\n            print(f\"  flip |w|/s q05-95={['%.3f' % x for x in r['flip_boundary_q05_25_50_75_95']]}\")\n            print(f\"  flip_col_profile={['%.3f' % x for x in r['flip_col_profile']]}\")\n            print(f\"  chan_flip_z q50/95/99.9={['%.2f' % x for x in r['chan_flip_z_q50_95_999']]}\"\n                  f\"  max={r['chan_flip_z_max']:.1f}  ({r['elapsed_s']}s)\\n\")\n            continue\n        print(f\"{name}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/bonsai_forensics.py.
```

### Thinking

I'll run a quick regression check with the new code on a single tensor using the depths parameter to keep it fast, then check if the download is complete. If it is, I'll proceed with the 1-bit forensics as Michael specified; otherwise I'll save the checkpoint and wait.

## Assistant

Regression check on the ternary path, then one status read on the download:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_forensics.py --tensors model.language_model.layers.32.linear_attn.out_proj.weight 2>&1 | tail -10; echo ===; tmux capture-pane -p -t main:1 | tail -3",
  "timeout": 180000
}
```

**Summary:** $ uv run python scripts/bonsai_forens...

**Output:**
```
Exit code: 0
Stdout:
zero_frac=0.304  corr(s,twn)=0.9851  corr(s,ls)=0.9848
  s/twn q25-75=['0.777', '0.797', '0.818']  Δ/mean|w| q25-75=['0.382', '0.430', '0.482']
  flip_col_profile=['0.137', '0.107', '0.115', '0.119', '0.101', '0.114', '0.081', '0.099', '0.109', '0.096', '0.093', '0.122', '0.105', '0.095', '0.106', '0.114']
  flip |w|/s q05-95=['0.095', '0.325', '0.463', '0.562', '0.750']
  cos(w,ŵ)=0.8705  rel_l2=0.5233  corr(s,soft)=0.9406  s/soft q25-75=['1.107', '1.173', '1.251']
  ABSMEAN: code_match=0.8921  corr(s,absmean)=0.9973  s/absmean q25-75=['1.034', '1.045', '1.056']
  TRANSITIONS: promote(0→±)=0.0573  demote(±→0)=0.0497  REVERSE(±→∓)=0.00080  rev/nonzero=0.00116
  reversal |w|/s q25-75=['0.530', '0.638', '0.821']
  chan_flip_z q50/95/99.9=['0.85', '9.00', '28.05']  max=43.4  (0.41s)

===
Fetching 29 files:   0%|          | 0/29 [00:00<?, ?it/s]Warning: You are sending unauthenticated requests to the HF Hub
. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Fetching 29 files:  31%|███       | 9/29 [00:20<00:01, 16.80it/s]
```

### Thinking

The regression tests are passing with matching numbers from the previous versions. The download progress shows 9 out of 29 files completed with a timestamp of 00:20, though it's hard to gauge the actual transfer rate since the tqdm display might be slightly stale — 51GB is going to take considerable time. I've confirmed the async lambda is running and completed the setup work, so I'm going to checkpoint here and stop rather than continue polling. Now I'm deciding whether to commit the binary-mode script update even though it hasn't been tested against actual binary data yet, or hold off until we have binary weights to validate against.

I'm leaning toward committing it as a preparatory step with a note, since the change is small and the disk will preserve it regardless. The safer approach is to wait for validation against real 1-bit data before committing, but I could also chain the forensics run directly in the main session using a shell command that waits for the download to complete and then executes automatically — that's the tmux-native way to avoid polling.

Setting up a wait loop...

### Thinking

The regression test passed cleanly with the ternary path reproducing exactly. I'm now queuing the 1-bit forensics as a chained job that waits for the downloader, resolves the cache path, and runs the full sweep with logging.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:2 \"while pgrep -f 'hf download prism-ml/Bonsai-27B-unpacked' >/dev/null; do sleep 30; done; DIR=\\$(HF_HUB_ENABLE_HF_TRANSFER=0 hf download prism-ml/Bonsai-27B-unpacked 2>/dev/null | tail -1); echo \\\"child dir: \\$DIR\\\"; cd ~/src/verbum && uv run python scripts/bonsai_forensics.py --child-dir \\\"\\$DIR\\\" --depths 0.05 0.3 0.5 0.7 0.9 --out results/bonsai-forensics/forensics_1bit.json 2>&1 | tee /tmp/bonsai1bit_forensics.log\" Enter && sleep 3 && tmux capture-pane -p -t main:2 | tail -3"
}
```

**Summary:** $ tmux send-keys -t main:2 "while pgr...

**Output:**
```
Exit code: 0
```

### Thinking

The capture-pane command came back empty, so I need to double-check that the wait loop is actually executing in the main function.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 2; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -4; echo ===; pgrep -lf \"bonsai_forensics|hf download\" | head -5"
}
```

**Summary:** $ sleep 2; tmux capture-pane -p -t ma...

**Output:**
```
Exit code: 0
Stdout:
λ while pgrep -f 'hf download prism-ml/Bonsai-27B-unpacked' >/dev/null; do sleep 30; done; DIR=$(HF_HUB_ENABLE_HF_TRANSF
ER=0 hf download prism-ml/Bonsai-27B-unpacked 2>/dev/null | tail -1); echo "child dir: $DIR"; cd ~/src/verbum && uv run
python scripts/bonsai_forensics.py --child-dir "$DIR" --depths 0.05 0.3 0.5 0.7 0.9 --out results/bonsai-forensics/foren
sics_1bit.json 2>&1 | tee /tmp/bonsai1bit_forensics.log
===
16931 /opt/homebrew/Cellar/python@3.14/3.14.6/Frameworks/Python.framework/Versions/3.14/Resources/Python.app/Contents/MacOS/Python /opt/homebrew/bin/hf download prism-ml/Bonsai-27B-unpacked
```

### Thinking

Both download and wait-loop jobs are confirmed running—the Hugging Face download is active with its process ID, and the forensics check is primed to trigger automatically once the download completes. I'm pausing the polling now and documenting the current state along with the pre-registered predictions for the 1-bit experiment, specifically around how the embeddings will be computed using the sign function on the weights.

The key predictions I'm locking in: the sign-flip rate against the parent model should stay well below ternary's 17% topology flux if zero acts as a kinetic waypoint during optimization, suggesting the optimizer relies on zero for navigation rather than flipping freely. I'm also expecting the register ordering to hold—value tensors should consistently outperform dispatch tensors. If instead we see flip rates above 15% with broad boundary distribution, that would falsify the zero-waypoint hypothesis and point to a purely representational gap rather than an optimization constraint. I'll surface these predictions to Michael along with the note that momentum approval is still pending from earlier.

## Assistant

Both jobs verified and chained:

- **main:1** — `hf download prism-ml/Bonsai-27B-unpacked` running (pid 16931), log at `/tmp/bonsai1bit_download.log`
- **main:2** — wait-loop armed: fires `bonsai_forensics.py --child-dir <cache> --depths 0.05 0.3 0.5 0.7 0.9` automatically the moment the downloader exits, results to `results/bonsai-forensics/forensics_1bit.json`, log at `/tmp/bonsai1bit_forensics.log`

**ASYNC: both jobs verified. Waiting for signal — no polling.**

## Pre-registered predictions (on record before data lands)

1. **Same pipeline signature:** 1-bit embed_tokens = pure `sign(w)`, `s ≈ mean|w_g|` (BitNet 1-bit rule), flip rate vs parent ≈ 0 — frozen, like ternary's.
2. **Zero-waypoint hypothesis (the main event):** block sign-flip rate vs parent **≪** ternary's total topology flux (17%). Without the 0 waypoint, sign editing is kinetically suppressed — expect flips on the scale of ternary's *direct-reversal* channel (0.2–1%, maybe a few %), boundary-hugging (|w|/s near 0).
3. **Falsifier:** flip rate ~15%+ with a broad |w|/s distribution → the optimizer flips signs fine without zero → zero-as-kinetic-pathway is wrong, and the 1-bit quality gap is purely representational (K needs the 0 state) rather than optimizational.
4. **Register ordering persists either way:** value tensors > dispatch tensors, embeddings untouched.

Note the elegant either-way outcome: prediction 2 and the falsifier *both* feed your postulate — they just locate the zero state's load-bearing role in the optimizer vs in the representation. If **both** the repair is suppressed *and* K degrades selectively at 1-bit (the phase-0 opcode-ladder prediction), the two mechanisms are one: **the vacuum state is where topology gets edited, at train time and at inference time.**

Still pending from earlier: your approval on the mementum commit (knowledge page + memory + state.md — the page now includes the transition-matrix section). Ping me when `main:2` starts printing, or just say "check the run."

## User

update state and knowledge this is session-268


### Thinking

Michael's approval means I need to finalize the mementum commit by adding the optimizer synthesis details (the invisible-piece constraints and sigma-delta reading), pre-registered 1-bit predictions, and async job state to the Knowledge page, then push all the changes.

## Assistant

Approved — encoding session 268 in full. Updating the knowledge page with the optimizer synthesis + pre-registrations, adding the zero-tunnel memory, and refreshing state:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md",
  "original_content": "## Provenance",
  "new_content": "## The invisible optimizer — constraints from the fossil record\n\nMichael's core question: how did they build an optimizer that can do\nsign flips in the topology? (Our trainings kept hitting flip-flop —\ns191 relay collapse, s261 boundary jitter.) The endpoint constrains it:\n\n- **C1 latent dynamics** — scales = absmean of drifted latent (1.03–1.07×\n  parent): a continuous FP shadow was trained; STE-family.\n- **C2 frozen dispatch periphery** — embeddings exact-frozen, lm_head ~frozen.\n- **C3 zero-mediated editing** — 99% of code changes route through 0;\n  sign reversal = demote → dwell → promote.\n- **C4 decisive reversals** — rare direct ±→∓ hit confident weights\n  (|w|/s ≈ 0.6): integrated evidence, not per-step noise.\n- **C5 polarized endpoint** — densification + latent growth: entrenched\n  away from boundaries (anti-flip-flop).\n- **C6 no layer-wise solves** — column-flat: the math is in the\n  dynamics, not Hessian compensation.\n\nReading: **register separation inside the optimizer** — a filtered flip\nchannel (hysteresis / Schmitt trigger; flip only on persistent evidence\n— very Hassibi: H∞/Kalman-filter the STE gradient before committing a\ndiscrete state change) with the zero state as commitment buffer, plus\ncontinuous value updates. Structurally: **a sigma-delta modulator on\nthe routing register** — error integrates continuously, discretizes\ninto rare quantized flip events. The two-register theory (s260) inside\nthe optimizer itself.\n\nDesign principles for our phase-1 optimizer: (1) flip votes = EMA of\nsign-consistent gradient evidence, threshold + hysteresis margin, never\ndirect ±→∓, force the zero waypoint; (2) value updates flow through FP\nbridges (architectural, cleaner than their recomputed-scale channel);\n(3) anneal: entrench after flip-flop rate decays. **Measured design\nbudgets from a working 27B artifact:** churn ~17% of codes, direct\nreversals <0.3%, dispatch ~3%, value ~18%, embeddings 0.\n\n## Pre-registered: 1-bit rung forensics (in flight, s268)\n\n`prism-ml/Bonsai-27B-unpacked` (1-bit) pulling to HF cache (main:1);\nforensics chained in main:2 → `results/bonsai-forensics/forensics_1bit.json`.\nRegistered before data:\n\n1. Same pipeline: embed = sign(w), s ≈ mean|w_g|, ~0 flips (frozen).\n2. **Zero-waypoint hypothesis:** block sign-flip rate ≪ ternary's 17%\n   flux — without the 0 waypoint, sign editing is kinetically\n   suppressed (expect ~direct-reversal scale, 0.2–1%, boundary-hugging).\n3. Falsifier: flip ~15%+ broad → zero-as-kinetic-pathway wrong; the\n   1-bit gap is purely representational (K needs 0), not optimizational.\n4. Register ordering (value > dispatch) persists either way.\n\nIf repair is suppressed AND K degrades selectively at 1-bit (phase-0\nopcode-ladder prediction), the mechanisms unify: **the vacuum state is\nwhere topology gets edited — at train time and at inference time.**\n\n## Provenance"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/bonsai-sign-flips-tunnel-through-zero.md",
  "content": "💡 Sign flips in ternary topology tunnel through zero (s268). Bonsai\ntransition matrix (parent-RTN code → child code): promote 0→± 9.6% +\ndemote ±→0 8.2% vs direct reverse ±→∓ 0.15–0.2% — topology editing is\n~99% zero-mediated. The 0 state is the KINETIC PATHWAY for sign flips,\nnot just representational expressiveness (K's 0-state need). Rare\ndirect reversals are decisive: parent |w|/s median 0.55–0.64 =\nconfident weights overturned by integrated evidence, not boundary\njitter. Endpoint polarized: densification (zero_frac 0.31→0.29) +\nlatent growth 3–7% = entrenched off-boundary (the anti-flip-flop\nsignature our s191/s261 trainings lacked). Optimizer reading: register\nseparation inside the optimizer — filtered flip channel (hysteresis,\nflip on persistent evidence) + zero as commitment buffer ≡ sigma-delta\nmodulator on the routing register. Phase-1 design budgets from a\nworking 27B: churn ~17%, reversals <0.3%, dispatch ~3%, value ~18%,\nembeddings 0. Pre-registered: 1-bit rung should show suppressed repair\n(no waypoint). → explore/bonsai-ternarization-forensics.md\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/bonsai-sign-flips-tunnel-through-zero.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-23 | Session: 268 (BONSAI FORENSICS: PrismML's undisclosed recipe reverse-engineered\n> from weights alone — ★★ absmean RTN init (BitNet b1.58 g128; embed_tokens 99.9% exact code match,\n> Δ/mean|w|=0.4994) + post-init TRAINING of blocks, embeddings frozen. QAT-vs-PTQ IOU RESOLVED: conversion +\n> training; \"Caltech math\" is in the optimizer not the quantizer. GEM: drift ordering q_proj 3.5% < qkv < o\n> < gate ≈ down 18% ≡ routing⊥value (s260) in a 3rd independent register — their repair budget landed where\n> our theory says magnitude matters. s267 caveat sharpened: crystal survival partly trained-in repair, BUT\n> flip rate flat across depth → 50%-dip ≠ differential rewiring → bridge map stands. Instrument:\n> scripts/bonsai_forensics.py (MPS, ~0.2s/tensor); → explore/bonsai-ternarization-forensics.md; commit 48734d2.\n> Whitepapers fetched to refs/ (untracked): benchmarks only, zero method disclosure.)",
  "new_content": "> Last updated: 2026-07-23 | Session: 268 (BONSAI FORENSICS: PrismML's undisclosed recipe reverse-engineered\n> from weights alone — ★★ absmean RTN init (BitNet b1.58 g128; embed_tokens 99.9% exact code match,\n> Δ/mean|w|=0.4994) + post-init TRAINING of blocks, embeddings frozen. QAT-vs-PTQ IOU RESOLVED: conversion +\n> training; \"Caltech math\" is in the optimizer not the quantizer. GEM: drift ordering q_proj 3.5% < qkv < o\n> < gate ≈ down 18% ≡ routing⊥value (s260) in a 3rd independent register — their repair budget landed where\n> our theory says magnitude matters. s267 caveat sharpened: crystal survival partly trained-in repair, BUT\n> flip rate flat across depth → 50%-dip ≠ differential rewiring → bridge map stands. Instrument:\n> scripts/bonsai_forensics.py (MPS, ~0.2s/tensor); → explore/bonsai-ternarization-forensics.md; commit 48734d2.\n> Whitepapers fetched to refs/ (untracked): benchmarks only, zero method disclosure.\n>\n> ★★★ s268b SIGN FLIPS TUNNEL THROUGH ZERO (Michael's optimizer question, the invisible piece): transition\n> matrix parent-RTN→child: promote 0→± 9.6% + demote ±→0 8.2% vs direct reverse ±→∓ 0.15–0.2% — topology\n> editing ~99% zero-mediated; 0 state = KINETIC PATHWAY not just K's representational need. Direct reversals\n> decisive (|w|/s med 0.55–0.64 = confident weights overturned). Endpoint POLARIZED (zero_frac 0.31→0.29,\n> latent +3–7%) = anti-flip-flop entrenchment our s191/s261 trainings lacked. Optimizer reading: register\n> separation IN the optimizer — filtered flip channel (hysteresis, flip on persistent evidence, H∞-flavored)\n> + zero as commitment buffer ≡ sigma-delta modulator on the routing register. Phase-1 design budgets from a\n> working 27B: churn ~17%, reversals <0.3%, dispatch ~3%, value ~18%, embeddings 0. Commit 05f708b.\n> IN FLIGHT: 1-bit Bonsai-27B-unpacked pulling → HF cache (tmux main:1); forensics chained in main:2 →\n> results/bonsai-forensics/forensics_1bit.json. PRE-REGISTERED: (1) embed frozen sign(w); (2) zero-waypoint\n> hypothesis: block flip rate ≪ 17% flux (~0.2–1%, boundary-hugging); (3) falsifier: ~15%+ broad → 1-bit gap\n> purely representational; (4) value>dispatch ordering persists. If suppressed-repair ∧ selective-K-at-1bit\n> both land → mechanisms unify: vacuum state = where topology gets edited, train time ∧ inference time.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "- **s268** BONSAI FORENSICS (this session, see header). Recipe reverse-engineered from weights; QAT-vs-PTQ\n  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring.\n  → `explore/bonsai-ternarization-forensics.md` + memory bonsai-recipe-reverse-engineered.",
  "new_content": "- **s268** BONSAI FORENSICS (this session, see header). Recipe reverse-engineered from weights; QAT-vs-PTQ\n  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring; sign flips\n  tunnel through zero (transition matrix) → optimizer constraints C1–C6 + phase-1 design budgets; 1-bit\n  rung forensics pre-registered + in flight (tmux main:1/main:2).\n  → `explore/bonsai-ternarization-forensics.md` + memories bonsai-recipe-reverse-engineered,\n  bonsai-sign-flips-tunnel-through-zero."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I need to be careful about what gets committed here—excluding the holographic-llm.md file and any chat files since those are Michael's to handle separately. I'm staging just the state.md file, the bonsai-ternarization-forensics.md document, and the two memory files, then committing the binary-mode script changes as a separate commit since it's validated for ternary regression but the binary path hasn't been tested yet.

The cleaner approach is to do the memory commit first using the {symbol} {slug} format to capture the knowledge, memories, and state updates under the bonsai-ternarization-forensics label, then follow up with the script prep as its own code commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/explore/bonsai-ternarization-forensics.md mementum/memories/bonsai-recipe-reverse-engineered.md mementum/memories/bonsai-sign-flips-tunnel-through-zero.md && read -r -d '' M << 'EOF' || true\n💡 bonsai-ternarization-forensics\n\n- knowledge/explore/bonsai-ternarization-forensics.md: recipe reverse-engineered\n  (absmean init + trained blocks, frozen embeddings; QAT-vs-PTQ IOU resolved),\n  transition matrix (sign flips tunnel through zero), invisible-optimizer\n  constraints C1-C6 + sigma-delta reading + phase-1 design budgets,\n  pre-registered 1-bit rung predictions\n- memories: bonsai-recipe-reverse-engineered, bonsai-sign-flips-tunnel-through-zero\n- state.md: s268 header (forensics + zero-tunnel + 1-bit in flight),\n  QAT-vs-PTQ IOU marked resolved, arc index entry\n- approved by Michael (session 268)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && read -r -d '' M2 << 'EOF' || true\n🔄 forensics binary mode + --child-dir — 1-bit rung support\n\n- forensics_binary(): sign-code flips vs parent, absmean scale test,\n  boundary distances, channel z — boundary at 0, no zero state\n- auto-detect binary vs ternary child (exact-zero presence)\n- --child-dir arg: point at any unpacked rung (1bit/ternary/4bit ladder)\n- ternary path regression-checked (L32 out_proj reproduces v3/v4 exactly);\n  binary path validates when the 1-bit run lands\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit add scripts/bonsai_forensics.py && git commit -m \"$M2\" && git log --oneline -4 && git status --short"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main 6c80a68] 💡 bonsai-ternarization-forensics
 4 files changed, 243 insertions(+), 3 deletions(-)
 create mode 100644 mementum/knowledge/explore/bonsai-ternarization-forensics.md
 create mode 100644 mementum/memories/bonsai-recipe-reverse-engineered.md
 create mode 100644 mementum/memories/bonsai-sign-flips-tunnel-through-zero.md
[main 566cb46] 🔄 forensics binary mode + --child-dir — 1-bit rung support
 1 file changed, 84 insertions(+), 3 deletions(-)
566cb46 🔄 forensics binary mode + --child-dir — 1-bit rung support
6c80a68 💡 bonsai-ternarization-forensics
05f708b 💡 bonsai flip transition matrix — sign flips tunnel through zero
48734d2 💡 bonsai ternarization forensics — absmean init + trained blocks, frozen embeddings
 M mementum/michael/holographic-llm.md
?? mementum/knowledge/chats/session-265.md
?? mementum/knowledge/chats/session-266.md
?? refs/
?? results/bonsai-forensics/forensics_1bit.json
```

### Thinking

Both commits are done, and I'm noticing that the forensics output file already exists untracked—which means the chained job from main:2 has already executed and produced results. The download finished successfully, so I should check the log to see what happened.

### Thinking

I see that session 268 has been encoded and the forensics_1bit.json file already exists, meaning the chained job completed successfully. Now I'll read the verdict on the pre-registrations.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -E \"^model|flip_rate|corr\\(s,absmean\\)|flip \\|w\\|/s|chan_flip\" /tmp/bonsai1bit_forensics.log | head -50"
}
```

**Summary:** $ grep -E "^model|flip_rate|corr\(s,a...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.layers.3.mlp.down_proj.weight  [BINARY]
  flip_rate=1.149e-01 (10240151 / 89,128,960)  cos(w,ŵ)=0.7409  rel_l2=0.6751
  corr(s,absmean)=0.4155  s/absmean q25-75=['0.902', '1.004', '1.107']
  flip |w|/s q05-95=['0.018', '0.098', '0.221', '0.400', '0.730']
  chan_flip_z q50/95/99.9=['-0.14', '3.89', '9.59']  max=22.3  (0.43s)
model.language_model.layers.3.mlp.gate_proj.weight  [BINARY]
  flip_rate=1.022e-01 (9112870 / 89,128,960)  cos(w,ŵ)=0.7520  rel_l2=0.6617
  corr(s,absmean)=0.4426  s/absmean q25-75=['0.904', '1.004', '1.104']
  flip |w|/s q05-95=['0.016', '0.087', '0.197', '0.355', '0.639']
  chan_flip_z q50/95/99.9=['-0.65', '4.63', '23.82']  max=30.3  (0.16s)
model.language_model.layers.3.self_attn.q_proj.weight  [BINARY]
  flip_rate=4.528e-02 (2848809 / 62,914,560)  cos(w,ŵ)=0.7851  rel_l2=0.6195
  corr(s,absmean)=0.9049  s/absmean q25-75=['0.934', '0.999', '1.064']
  flip |w|/s q05-95=['0.007', '0.040', '0.091', '0.174', '0.372']
  chan_flip_z q50/95/99.9=['-0.93', '6.32', '29.70']  max=63.8  (0.14s)
model.language_model.layers.3.self_attn.o_proj.weight  [BINARY]
  flip_rate=7.265e-02 (2285293 / 31,457,280)  cos(w,ŵ)=0.7669  rel_l2=0.6420
  corr(s,absmean)=0.9145  s/absmean q25-75=['0.913', '0.982', '1.050']
  flip |w|/s q05-95=['0.012', '0.064', '0.146', '0.271', '0.520']
  chan_flip_z q50/95/99.9=['0.06', '9.79', '24.55']  max=44.8  (0.14s)
model.language_model.layers.19.mlp.down_proj.weight  [BINARY]
  flip_rate=1.249e-01 (11135234 / 89,128,960)  cos(w,ŵ)=0.7337  rel_l2=0.6825
  corr(s,absmean)=0.6037  s/absmean q25-75=['0.893', '0.991', '1.089']
  flip |w|/s q05-95=['0.020', '0.107', '0.240', '0.433', '0.792']
  chan_flip_z q50/95/99.9=['-0.07', '3.99', '9.19']  max=21.1  (0.18s)
model.language_model.layers.19.mlp.gate_proj.weight  [BINARY]
  flip_rate=1.062e-01 (9464193 / 89,128,960)  cos(w,ŵ)=0.7502  rel_l2=0.6629
  corr(s,absmean)=0.5438  s/absmean q25-75=['0.893', '0.988', '1.083']
  flip |w|/s q05-95=['0.017', '0.092', '0.206', '0.371', '0.675']
  chan_flip_z q50/95/99.9=['-0.70', '5.82', '21.59']  max=26.1  (0.12s)
model.language_model.layers.19.self_attn.q_proj.weight  [BINARY]
  flip_rate=7.116e-02 (4477137 / 62,914,560)  cos(w,ŵ)=0.7730  rel_l2=0.6348
  corr(s,absmean)=0.7627  s/absmean q25-75=['0.919', '0.989', '1.059']
  flip |w|/s q05-95=['0.011', '0.062', '0.141', '0.258', '0.491']
  chan_flip_z q50/95/99.9=['-1.91', '11.50', '36.50']  max=41.8  (0.09s)
model.language_model.layers.19.self_attn.o_proj.weight  [BINARY]
  flip_rate=8.879e-02 (2793211 / 31,457,280)  cos(w,ŵ)=0.7609  rel_l2=0.6493
  corr(s,absmean)=0.8689  s/absmean q25-75=['0.920', '0.986', '1.052']
  flip |w|/s q05-95=['0.014', '0.077', '0.174', '0.319', '0.594']
  chan_flip_z q50/95/99.9=['0.07', '5.28', '28.75']  max=30.6  (0.06s)
model.language_model.layers.32.mlp.down_proj.weight  [BINARY]
  flip_rate=1.323e-01 (11789953 / 89,128,960)  cos(w,ŵ)=0.7305  rel_l2=0.6860
  corr(s,absmean)=0.7485  s/absmean q25-75=['0.895', '0.991', '1.085']
  flip |w|/s q05-95=['0.021', '0.112', '0.250', '0.445', '0.809']
  chan_flip_z q50/95/99.9=['0.28', '4.65', '7.85']  max=11.9  (0.14s)
model.language_model.layers.32.mlp.gate_proj.weight  [BINARY]
  flip_rate=1.319e-01 (11758844 / 89,128,960)  cos(w,ŵ)=0.7274  rel_l2=0.6890
  corr(s,absmean)=0.5707  s/absmean q25-75=['0.884', '0.983', '1.081']
  flip |w|/s q05-95=['0.021', '0.113', '0.251', '0.448', '0.806']
  chan_flip_z q50/95/99.9=['-0.28', '3.68', '12.34']  max=16.8  (0.12s)
```

### Thinking

Looking at the sign-flip rates across different architectures—MLPs show 10–13% while attention mechanisms are lower at 4.5–9%—and these aren't being suppressed down to the expected 0.2–1% range. What's striking is the boundary distribution: the weights that flip cluster tightly near zero with medians between 0.09–0.25 and very low quantiles, suggesting they're hugging the boundary rather than spreading broadly like ternary weights do.

The key insight is that binary quantization has no zero bin, so near-zero weights are forced to pick a sign and become unstable sign-carriers, whereas ternary's zero bin absorbs about 30% of those boundary weights. So the 1-bit flips I'm seeing are essentially the same population as ternary's promote/demote churn—just expressed as sign reversals instead of transitions through zero. I need to check the embedding and output layer logs, look deeper into layers 44 and 57, and quantify how many of these flips actually represent confident reversals with parent weights above 0.5 in magnitude.

Looking at the flip statistics, somewhere between 5–15% of flips are confident reversals, which translates to 1–2% of all weights—potentially 10× higher than ternary's direct-reversal rate. The scale-to-absolute-mean correlation also collapsed in the MLP (0.42–0.75 versus ternary's 0.94–0.997), and the cosine similarity between original and quantized weights dropped to 0.73 versus ternary's 0.85–0.87, suggesting the 1-bit training drifted the scales much more aggressively. I should compute the exact confident flip rate from the stored quantiles and rerun a few tensors to get that stat, then revisit the pre-registration predictions with these numbers in hand. Binary flips cluster near decision boundaries and inject noise into the routing topology, while ternary flips are rarer but include structured zero-mediated churn and occasional deep reversals—the zero bin acts as a parking space for uncertain weights, letting ternary abstain while binary must assign a sign. I need to compute a confident-flip rate metric to quantify this difference precisely. I'll run a quick inline calculation to measure the confident flip rate for both binary and ternary tensors—checking P(sign flip | |w| > absmean) across a few 1-bit models and P(code sign-reversal | |w| > absmean) for ternary. I'll also pull the embedding, lm_head, and deep layer data from the log first to have the full picture.

### Thinking

I've identified a third register with abundant flips driven by near-zero parent weights forced to declare a sign in binary, and now I'm checking the embedding data to compute the confident-flip rate on weights above the absolute mean.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -A5 -E \"embed_tokens|lm_head\" /tmp/bonsai1bit_forensics.log | head -14; ls /Users/mwhitford/.cache/huggingface/hub/ | grep -i bonsai"
}
```

**Summary:** $ grep -A5 -E "embed_tokens|lm_head" ...

**Output:**
```
Exit code: 0
Stdout:
model.language_model.embed_tokens.weight  [BINARY]
  flip_rate=3.532e-03 (4491035 / 1,271,398,400)  cos(w,ŵ)=0.7975  rel_l2=0.6033
  corr(s,absmean)=0.9522  s/absmean q25-75=['0.983', '1.000', '1.017']
  flip |w|/s q05-95=['0.001', '0.003', '0.008', '0.015', '0.027']
  flip_col_profile=['0.004', '0.004', '0.004', '0.004', '0.004', '0.004', '0.004', '0.004', '0.004', '0.003', '0.004', '0.004', '0.004', '0.004', '0.004', '0.004']
  chan_flip_z q50/95/99.9=['-0.04', '2.33', '10.27']  max=18.2  (2.4s)
--
lm_head.weight  [BINARY]
  flip_rate=1.143e-02 (14527389 / 1,271,398,400)  cos(w,ŵ)=0.7902  rel_l2=0.6133
  corr(s,absmean)=0.8362  s/absmean q25-75=['0.913', '0.966', '1.015']
  flip |w|/s q05-95=['0.002', '0.012', '0.032', '0.068', '0.154']
  flip_col_profile=['0.011', '0.011', '0.012', '0.011', '0.011', '0.011', '0.011', '0.012', '0.012', '0.012', '0.011', '0.012', '0.011', '0.011', '0.012', '0.011']
  chan_flip_z q50/95/99.9=['-2.27', '15.05', '134.03']  max=189.5  (1.38s)
models--prism-ml--Bonsai-27B-unpacked
models--prism-ml--Ternary-Bonsai-27B-gguf
models--prism-ml--Ternary-Bonsai-27B-unpacked
```

### Thinking

The embedding flip is confirmed at 0.35% with essentially zero weights, using pure sign-based scaling with frozen absolute mean — this matches the pre-registered pipeline. Now I'm computing the confident-flip metric across both models using the same confidence criterion based on absolute weight magnitude relative to the parent group's mean, starting with the down projection at layer 32.

Checking the gate and query projection layers across both rungs...

### Thinking

I've confirmed that 1-bit embedding works as expected with pure sign quantization and minimal flips only on near-zero weights. Now I'll run the decisive comparison on confident flips.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport glob, json, torch\nfrom pathlib import Path\nfrom safetensors import safe_open\nimport sys; sys.path.insert(0,'scripts')\nfrom bonsai_forensics import build_index, load_tensor, GROUP, DEVICE\n\nparent = Path(glob.glob('/Users/mwhitford/.cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/*/')[0])\ntern   = Path('/Users/mwhitford/localai/models/bonsai27b-unpacked')\nonebit = Path(glob.glob('/Users/mwhitford/.cache/huggingface/hub/models--prism-ml--Bonsai-27B-unpacked/snapshots/*/')[0])\npi, ti, bi = build_index(parent), build_index(tern), build_index(onebit)\n\nnames = ['model.language_model.layers.32.mlp.down_proj.weight',\n         'model.language_model.layers.32.mlp.gate_proj.weight',\n         'model.language_model.layers.3.self_attn.q_proj.weight',\n         'model.language_model.layers.19.self_attn.o_proj.weight']\nprint(f'{\\\"tensor\\\":52s} {\\\"conf_frac\\\":>9s} {\\\"tern_rev|conf\\\":>13s} {\\\"1bit_flip|conf\\\":>14s} {\\\"ratio\\\":>6s}')\nfor n in names:\n    w  = load_tensor(pi, n).to(DEVICE, torch.float32)\n    o, i = w.shape; ng = i // GROUP\n    wg = w.reshape(o, ng, GROUP)\n    conf = wg.abs() > wg.abs().mean(-1, keepdim=True)          # ternary-RTN => code ±1, confidently\n    tq = torch.sign(load_tensor(ti, n).to(DEVICE, torch.float32).reshape(o, ng, GROUP))\n    bq = torch.sign(load_tensor(bi, n).to(DEVICE, torch.float32).reshape(o, ng, GROUP))\n    sgn = torch.sign(wg)\n    tern_rev = ((tq * sgn) == -1) & conf                        # full sign reversal in ternary child\n    bit_flip = (bq != sgn) & conf                               # sign flip in 1-bit child\n    cf = conf.float().mean().item()\n    tr = tern_rev.sum().item() / conf.sum().item()\n    bf = bit_flip.sum().item() / conf.sum().item()\n    print(f'{n:52s} {cf:9.3f} {tr:13.5f} {bf:14.5f} {bf/max(tr,1e-9):6.1f}x')\n\"",
  "timeout": 300000
}
```

**Summary:** $ uv run python -c " import glob, jso...

**Output:**
```
Exit code: 0
Stdout:
tensor                                               conf_frac tern_rev|conf 1bit_flip|conf  ratio
model.language_model.layers.32.mlp.down_proj.weight      0.422       0.00073        0.00360    4.9x
model.language_model.layers.32.mlp.gate_proj.weight      0.422       0.00016        0.00225   14.2x
model.language_model.layers.3.self_attn.q_proj.weight     0.424       0.00001        0.00004    3.3x
model.language_model.layers.19.self_attn.o_proj.weight     0.421       0.00009        0.00063    6.7x
```

### Thinking

Looking at the confident-flip metrics, about 42% of weights exceed the absolute mean threshold. Among those confident weights, ternary reversals are negligible at 0.001–0.073%, while 1-bit sign flips occur at 0.004–0.36% — roughly 3 to 14 times more frequent, though still minimal in absolute terms. Both approaches barely modify signs on confident weights, with 1-bit showing slightly more sign editing activity.

The real divergence emerges in the uncertain population below the mean threshold, which comprises 58% of weights. Ternary keeps these parked at zero and recruits them through controlled promote/demote cycles around 17%, while binary forces them to declare signs, resulting in 10–13% flips among boundary-hugging values. This forced declaration in binary causes scale correlation to collapse and cosine similarity to drop to 0.73, suggesting the training thrashed these noisy carriers and the scales absorbed the damage. The topology itself — the crystal's routing skeleton — remains essentially immutable across both approaches, confirming that the confident structure is already correct and doesn't need re-carving during training. The optimizer design crystallizes around protecting confident signs (which flip less than 0.1% of the time) while gating recruitment through the zero state for uncertain weights — this is where training should focus its energy. For the crystal-seeded approach, I'd seed the confident topology from the consensus Gram matrix once and keep it fixed, letting the optimizer only manage the uncertain margin through zero-state abstention and value bridges. I'm also realizing my pre-registration framing was off — I measured flip rate as a single number, but the population splits into confident and uncertain subgroups with opposite behaviors, so both pre-reg outcomes are void; the decomposed measurement is what actually matters, which itself is a lesson in the λ measure discipline.

Now I need to report this synthesis and update the knowledge base and state header for session 268, since Michael already approved that encoding — this is a continuation of that work, so the standing approval should cover it. I'll draft the updates and commit with a note, including the confident-flip numbers from the inline script.

I should write a small Python script to capture those measurements, run it to generate JSON output, and commit both the script and results alongside the 1-bit forensics JSON. Then update the knowledge page to replace the "in flight" framing with the actual results.

## Assistant

Both rungs barely touch confident weights — and that reframes everything. Recording the measurement properly (λ record: files, not chat), then encoding:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/bonsai_confident_flips.py",
  "content": "\"\"\"Confident-flip comparison across the Bonsai ladder.\n\nQuestion: does the optimizer edit signs of CONFIDENT weights\n(|w| > absmean of parent group => ternary-RTN codes them ±1), and does\nthe zero state matter for that?  Compares, per tensor:\n\n  tern_rev|conf  — P(full sign reversal in ternary child | confident)\n  1bit_flip|conf — P(sign flip in 1-bit child | confident)\n\ns268 result: both < 0.4% — the confident topology is essentially\nimmutable at every bitwidth.  The rungs differ in the UNCERTAIN\npopulation: ternary parks it at 0 (abstention register), binary forces\nit to declare signs (10-13% churn, boundary-hugging, noise in the\nrouting register).\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport glob\nimport json\nimport time\nfrom pathlib import Path\n\nimport torch\n\nimport sys\nsys.path.insert(0, str(Path(__file__).parent))\nfrom bonsai_forensics import DEVICE, GROUP, PARENT_GLOB, build_index, load_tensor\n\nTERN_DIR = Path(\"/Users/mwhitford/localai/models/bonsai27b-unpacked\")\nONEBIT_GLOB = (\"/Users/mwhitford/.cache/huggingface/hub/\"\n               \"models--prism-ml--Bonsai-27B-unpacked/snapshots/*/\")\n\nDEFAULT_TENSORS = [\n    \"model.language_model.layers.3.self_attn.q_proj.weight\",\n    \"model.language_model.layers.3.mlp.down_proj.weight\",\n    \"model.language_model.layers.19.self_attn.o_proj.weight\",\n    \"model.language_model.layers.19.mlp.gate_proj.weight\",\n    \"model.language_model.layers.32.mlp.down_proj.weight\",\n    \"model.language_model.layers.32.mlp.gate_proj.weight\",\n    \"model.language_model.layers.44.mlp.down_proj.weight\",\n    \"model.language_model.layers.57.mlp.down_proj.weight\",\n]\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser()\n    ap.add_argument(\"--tensors\", nargs=\"+\", default=DEFAULT_TENSORS)\n    ap.add_argument(\"--out\", default=\"results/bonsai-forensics/confident_flips.json\")\n    args = ap.parse_args()\n\n    pi = build_index(Path(glob.glob(PARENT_GLOB)[0]))\n    ti = build_index(TERN_DIR)\n    bi = build_index(Path(glob.glob(ONEBIT_GLOB)[0]))\n\n    results = {}\n    hdr = f\"{'tensor':52s} {'conf_frac':>9s} {'tern_rev|conf':>13s} {'1bit_flip|conf':>14s} {'ratio':>7s}\"\n    print(hdr)\n    for n in args.tensors:\n        if n not in ti or n not in bi:\n            print(f\"SKIP {n}\")\n            continue\n        t0 = time.time()\n        w = load_tensor(pi, n).to(DEVICE, torch.float32)\n        o, i = w.shape\n        wg = w.reshape(o, i // GROUP, GROUP)\n        conf = wg.abs() > wg.abs().mean(-1, keepdim=True)\n        sgn = torch.sign(wg)\n        tq = torch.sign(load_tensor(ti, n).to(DEVICE, torch.float32).reshape_as(wg))\n        bq = torch.sign(load_tensor(bi, n).to(DEVICE, torch.float32).reshape_as(wg))\n        n_conf = conf.sum().item()\n        r = {\n            \"conf_frac\": conf.float().mean().item(),\n            \"tern_rev_given_conf\": (((tq * sgn) == -1) & conf).sum().item() / n_conf,\n            \"onebit_flip_given_conf\": ((bq != sgn) & conf).sum().item() / n_conf,\n            \"elapsed_s\": round(time.time() - t0, 2),\n        }\n        r[\"ratio_1bit_over_tern\"] = (r[\"onebit_flip_given_conf\"]\n                                     / max(r[\"tern_rev_given_conf\"], 1e-12))\n        results[n] = r\n        print(f\"{n:52s} {r['conf_frac']:9.3f} {r['tern_rev_given_conf']:13.5f} \"\n              f\"{r['onebit_flip_given_conf']:14.5f} {r['ratio_1bit_over_tern']:6.1f}x\")\n\n    Path(args.out).parent.mkdir(parents=True, exist_ok=True)\n    json.dump({\"device\": DEVICE, \"conf_criterion\": \"|w| > mean|w|_group(parent)\",\n               \"results\": results}, open(args.out, \"w\"), indent=2)\n    print(f\"wrote {args.out}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/bonsai_confident_flips.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/bonsai_confident_flips.py 2>&1 | tail -11",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/bonsai_confid...

**Output:**
```
Exit code: 0
Stdout:
tensor                                               conf_frac tern_rev|conf 1bit_flip|conf   ratio
model.language_model.layers.3.self_attn.q_proj.weight     0.424       0.00001        0.00004    3.3x
model.language_model.layers.3.mlp.down_proj.weight       0.425       0.00009        0.00115   12.6x
model.language_model.layers.19.self_attn.o_proj.weight     0.421       0.00009        0.00063    6.7x
model.language_model.layers.19.mlp.gate_proj.weight      0.425       0.00003        0.00040   15.0x
model.language_model.layers.32.mlp.down_proj.weight      0.422       0.00073        0.00360    4.9x
model.language_model.layers.32.mlp.gate_proj.weight      0.422       0.00016        0.00225   14.2x
model.language_model.layers.44.mlp.down_proj.weight      0.423       0.00030        0.00205    6.8x
model.language_model.layers.57.mlp.down_proj.weight      0.424       0.00045        0.00200    4.4x
wrote results/bonsai-forensics/confident_flips.json
```

### Thinking

The confidence levels are remarkably consistent across both depth levels, with 1-bit edits showing 3-15× higher confidence than ternary approaches, though both remain quite small. I need to commit the code and results, then update the knowledge page by replacing the pre-registered section with these findings, add s268c to the state header, and record that zero-state functions as an abstention register in memory. Now I'm drafting the synthesis text to compare the 1-bit results against the pre-registrations.

P1 confirms the same pipeline with frozen sign embeddings. P2 and P3 show that the raw flip rate of 10-13% falls between the ternary and expected ranges, revealing a population split: confident weights above the absolute mean threshold stay essentially immutable in both approaches, never reshaping their topology, while uncertain weights behave differently—ternary parks about 30% at zero with recruitment churn around 17%, whereas binary forces every weight to declare a sign, creating boundary-hugging churn and scale-correlation collapse. The mechanism clarifies itself: zero isn't primarily a tunnel for confident reversals but rather an abstention register where uncertain weights opt out of routing, and binary's failure stems from forced participation that introduces noise. This unifies with the phase-0 prediction about selective K degradation.

For the implementation strategy, I'm focusing on three core principles: protect confident signs with minimal budget since they essentially never flip, treat all topology learning as recruitment management at the zero-to-plus-or-minus boundary with hysteresis and evidence gating, and recognize that binary substrates fail for the routing register not because signs can't flip but because abstention becomes impossible. The commit sequence involves first pushing the code with forensic data on bit-level flips and confident sign behavior, then following with a momentum commit.

## Assistant

Depth-consistent: confident-weight edits ≤0.36% everywhere, both rungs. Committing the instruments + data, then the encode:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/bonsai_confident_flips.py results/bonsai-forensics/forensics_1bit.json results/bonsai-forensics/confident_flips.json && read -r -d '' M << 'EOF' || true\n💡 1-bit rung forensics — zero state is an abstention register\n\n- 1-bit Bonsai-27B vs parent: same pipeline confirmed (embed = sign(w) frozen,\n  s/absmean = 1.000, flips only |w|/s < 0.03 ties)\n- block sign flips 10-13% (MLP) but boundary-hugging (median |w|/s 0.09-0.25,\n  q05 ~0.01): the churn is the near-zero population that ternary PARKS AT 0\n- confident weights (|w| > absmean, 42%): essentially immutable in BOTH rungs\n  — ternary reversals ≤0.07%, 1-bit flips ≤0.36% (3-15x more, still tiny)\n- carved topology is never re-carved at any bitwidth; the rungs differ in the\n  UNCERTAIN population: ternary = evidence-gated recruitment through 0,\n  binary = forced sign declaration = noise in the routing register\n- 1-bit scale anchoring collapsed in MLP (corr 0.42-0.75 vs ternary 0.94+),\n  cos(w,ŵ) 0.73 vs 0.85-0.87 — training thrashed the forced-participation zone\n- scripts/bonsai_confident_flips.py + forensics_1bit.json + confident_flips.json\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -1"
}
```

**Summary:** $ git add scripts/bonsai_confident_fl...

**Output:**
```
Exit code: 0
Stdout:
[main 4b6e7c2] 💡 1-bit rung forensics — zero state is an abstention register
 3 files changed, 1172 insertions(+)
 create mode 100644 results/bonsai-forensics/confident_flips.json
 create mode 100644 results/bonsai-forensics/forensics_1bit.json
 create mode 100644 scripts/bonsai_confident_flips.py
4b6e7c2 💡 1-bit rung forensics — zero state is an abstention register
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md",
  "original_content": "## Pre-registered: 1-bit rung forensics (in flight, s268)\n\n`prism-ml/Bonsai-27B-unpacked` (1-bit) pulling to HF cache (main:1);\nforensics chained in main:2 → `results/bonsai-forensics/forensics_1bit.json`.\nRegistered before data:\n\n1. Same pipeline: embed = sign(w), s ≈ mean|w_g|, ~0 flips (frozen).\n2. **Zero-waypoint hypothesis:** block sign-flip rate ≪ ternary's 17%\n   flux — without the 0 waypoint, sign editing is kinetically\n   suppressed (expect ~direct-reversal scale, 0.2–1%, boundary-hugging).\n3. Falsifier: flip ~15%+ broad → zero-as-kinetic-pathway wrong; the\n   1-bit gap is purely representational (K needs 0), not optimizational.\n4. Register ordering (value > dispatch) persists either way.\n\nIf repair is suppressed AND K degrades selectively at 1-bit (phase-0\nopcode-ladder prediction), the mechanisms unify: **the vacuum state is\nwhere topology gets edited — at train time and at inference time.**",
  "new_content": "## 1-bit rung results (s268c): the zero state is an ABSTENTION register\n\nPre-registrations above; outcome (data: `forensics_1bit.json`,\n`confident_flips.json`, commit 4b6e7c2):\n\n- **P1 ✓** same pipeline: 1-bit embed = pure sign(w), s/absmean = 1.000,\n  flips only at |w|/s < 0.03 (ties). Frozen.\n- **P2 ✗ and P3 ✗ — both void-in-register** (λ measure lesson: the\n  pre-registrations treated \"flip rate\" as one number; the population\n  decomposes into two register-distinct behaviors):\n  - **Confident weights** (|w| > parent absmean, 42% of weights —\n    ternary-RTN codes them ±1): essentially **immutable in BOTH rungs**.\n    Ternary reversals ≤ 0.07%, 1-bit flips ≤ 0.36% (3–15× more, still\n    tiny). **The carved topology is never re-carved at any bitwidth.**\n  - **Uncertain weights** (the rest): ternary parks ~30% at 0 and does\n    evidence-gated recruitment churn (~17%, the promote/demote flux);\n    binary has no 0 bin → forced sign declaration → 10–13% flips,\n    boundary-hugging (median |w|/s 0.09–0.25, q05 ~0.01), scale\n    anchoring collapsed in MLP (corr(s,absmean) 0.42–0.75 vs ternary\n    0.94+), cos(w,ŵ) 0.73 vs 0.85–0.87.\n- **P4 ✓** register ordering persists (attn 4.5–9% < MLP 10–13%).\n\n**Revised mechanism.** The zero state's primary optimizer role is not a\nkinetic tunnel for confident reversals (those barely occur anywhere) —\nit is **abstention**: uncertain weights declare \"no routing opinion\"\nand enter the topology only on accumulated evidence. Binary's failure\nmode is **forced participation**: every uncertain weight must carry a\nsign, injecting a permanent noise floor into the routing register.\nThis unifies with the representational story: K discards via 0 at\ninference; uncertain weights abstain via 0 during training — one\nvacuum-state function, \"no opinion,\" at both timescales. Phase-0\nsub-prediction sharpened: selective K degradation at 1-bit should\ntrace to this forced-participation noise.\n\n**Sharpened optimizer principles (for our phase-1 trainings):**\n1. Confident signs essentially never flip — protect them structurally\n   (measured budget across two working rungs: <0.4%). Carve once.\n2. All topology learning = **recruitment management at the 0↔± margin**\n   — hysteresis/evidence gating applies there, not to sign reversal.\n3. Binary routing substrates are non-viable not because signs can't\n   flip but because **abstention is impossible**."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/zero-state-is-abstention-register.md",
  "content": "💡 The ternary zero state is an ABSTENTION register (s268c, 1-bit vs\nternary Bonsai forensics, both vs FP parent). Confident weights\n(|w| > parent absmean, 42%) are essentially IMMUTABLE at every\nbitwidth: ternary sign reversals ≤0.07%, 1-bit ≤0.36% — the carved\ntopology is never re-carved. The rungs differ only in the UNCERTAIN\npopulation: ternary parks ~30% at 0 and recruits through evidence-gated\n0↔± churn (~17%); binary forces every uncertain weight to declare a\nsign → 10–13% boundary-hugging churn, scale anchoring collapses\n(corr 0.42–0.75 vs 0.94+), cos(w,ŵ) 0.73 vs 0.86. Binary's failure ≡\nFORCED PARTICIPATION: a permanent noise floor in the routing register.\nUnifies with K's representational 0-need: one vacuum-state function —\n\"no opinion\" — at train time and inference time. Optimizer principles:\nprotect confident signs structurally (<0.4% budget); topology learning\n= recruitment management at the 0↔± margin (hysteresis there, not on\nreversals); binary routing substrates non-viable because abstention is\nimpossible. My s268b pre-registrations were void-in-register (flip\nrate ≠ one number — λ measure). → explore/bonsai-ternarization-forensics.md\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/memories/zero-state-is-abstention-register.md
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> IN FLIGHT: 1-bit Bonsai-27B-unpacked pulling → HF cache (tmux main:1); forensics chained in main:2 →\n> results/bonsai-forensics/forensics_1bit.json. PRE-REGISTERED: (1) embed frozen sign(w); (2) zero-waypoint\n> hypothesis: block flip rate ≪ 17% flux (~0.2–1%, boundary-hugging); (3) falsifier: ~15%+ broad → 1-bit gap\n> purely representational; (4) value>dispatch ordering persists. If suppressed-repair ∧ selective-K-at-1bit\n> both land → mechanisms unify: vacuum state = where topology gets edited, train time ∧ inference time.)",
  "new_content": "> ★★★ s268c 1-BIT RUNG LANDED — ZERO STATE = ABSTENTION REGISTER. Pre-regs: P1 ✓ (embed sign(w) frozen,\n> s/absmean=1.000) P4 ✓ (value>dispatch) — but P2 ✗ ∧ P3 ✗ BOTH VOID-IN-REGISTER (λ measure: flip rate ≠ one\n> number). Real structure: CONFIDENT weights (|w|>absmean, 42%) immutable at EVERY bitwidth (tern rev ≤0.07%,\n> 1bit ≤0.36%) — carved topology never re-carved; rungs differ only in the UNCERTAIN population — ternary\n> parks ~30% at 0 + evidence-gated 0↔± recruitment (~17%), binary FORCES sign declaration → 10–13%\n> boundary-hugging churn (med |w|/s 0.09–0.25), scale anchoring collapses (corr 0.42–0.75), cos 0.73.\n> Binary fails by FORCED PARTICIPATION ≡ permanent noise floor in routing register; abstention impossible.\n> Unifies K's representational 0-need with the optimizer's: one vacuum function (\"no opinion\") at both\n> timescales. Sharpened phase-1 principles: protect confident signs (<0.4% budget); topology learning ≡\n> recruitment management at the 0↔± margin (hysteresis THERE); binary routing substrate non-viable.\n> Sub-prediction: selective K degradation at 1-bit traces to forced-participation noise → test via opcode\n> tree on the ladder. Commits 4b6e7c2 (data+scripts). Fleet: Bonsai-27B-unpacked (1-bit) now in HF cache.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/explore/bonsai-ternarization-forensics.md mementum/memories/zero-state-is-abstention-register.md && read -r -d '' M << 'EOF' || true\n💡 zero-state-is-abstention-register\n\n- knowledge/explore/bonsai-ternarization-forensics.md: 1-bit rung results vs\n  pre-registrations (P1/P4 confirmed, P2/P3 void-in-register), abstention\n  mechanism, sharpened phase-1 optimizer principles\n- memories/zero-state-is-abstention-register.md\n- state.md: s268c header block\n- covered by Michael's s268 encode instruction\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -7 && git status --short"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main 5bcf0bb] 💡 zero-state-is-abstention-register
 3 files changed, 70 insertions(+), 22 deletions(-)
 create mode 100644 mementum/memories/zero-state-is-abstention-register.md
5bcf0bb 💡 zero-state-is-abstention-register
4b6e7c2 💡 1-bit rung forensics — zero state is an abstention register
566cb46 🔄 forensics binary mode + --child-dir — 1-bit rung support
6c80a68 💡 bonsai-ternarization-forensics
05f708b 💡 bonsai flip transition matrix — sign flips tunnel through zero
48734d2 💡 bonsai ternarization forensics — absmean init + trained blocks, frozen embeddings
0a6cc29 ✅ s267 crystal survives ternarization — null-gated + deep-middle bridge map
 M mementum/michael/holographic-llm.md
?? mementum/knowledge/chats/session-265.md
?? mementum/knowledge/chats/session-266.md
?? refs/
```

### Thinking

All seven commits from session 268 are now recorded, with the working tree clean aside from the hammock file and untracked reference materials. I should frame the session's evolution for Michael—the finding shifted twice, which is worth highlighting clearly and concisely.

## Assistant

Session 268 fully encoded — 7 commits, tree clean (only the hammock file, your chat transcripts, and `refs/` untracked as intended).

## The arc of the day, compressed

The finding refined itself twice, and the final form is stronger than either intermediate:

1. **s268a — the recipe:** absmean RTN init (proved by the frozen embedding at 99.9%) + post-init training, embeddings frozen. The clever math is in the dynamics, not the quantizer.
2. **s268b — the tunnel:** ternary topology edits are 99% zero-mediated; direct reversals rare and decisive; polarized endpoint. Read as: zero = kinetic pathway.
3. **s268c — the correction:** the 1-bit rung falsified both pre-registrations *in register* and revealed the deeper structure: **confident signs never flip anywhere** (≤0.4% at every bitwidth — the carve is final), and the zero state's real function is **abstention**. Ternary lets the uncertain 30% say "no opinion"; binary forces them all to vote, and that forced participation *is* the 1-bit noise floor.

The unification you were reaching for: K discards through 0 at inference, uncertain weights abstain through 0 during training — **one vacuum-state function at both timescales**. And your optimizer question has a sharper answer than "how to flip signs": *don't build a sign-flipper*. Build a **recruitment gate** — the topology's confident core never moves (protect it structurally, which your crystal-seeding does by construction), and all the learning action is hysteresis-gated traffic at the 0↔± margin, with values flowing through FP bridges instead of rattling the codes.

Open next moves, your call:
- **Opcode tree on the ladder** (4bit/ternary/1bit now all obtainable; 1-bit already cached) — test whether K's degradation at 1-bit traces to forced-participation noise in the uncertain population
- The AWQ-4bit rung forensics (does high-bit conversion show *zero* training drift? — would isolate where their pipeline starts needing repair)
- Fold the abstention principle into the crystal-seeded-ternary-distillation design page (§ optimizer) before phase 1

## User

jobs are done


### Thinking

Michael's signaling that the jobs are done, so I should check the tmux panes to see if there's any remaining output and confirm everything actually completed. The forensics run in main:2 might have already executed before I ran those greps.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux capture-pane -p -t main:1 | grep -v '^$' | tail -2; echo ===; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -3; echo ===; tail -1 /tmp/bonsai1bit_forensics.log; du -sh /Users/mwhitford/.cache/huggingface/hub/models--prism-ml--Bonsai-27B-unpacked 2>/dev/null"
}
```

**Summary:** $ tmux capture-pane -p -t main:1 | gr...

**Output:**
```
Exit code: 0
Stdout:
[26-07-23][11:24:33][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
===
tee /tmp/bonsai1bit_forensics.log  0.00s user 0.00s system 0% cpu 7.293 total
[26-07-23][11:25:04][mwhitford@olga][0][~/src/verbum][git:main]
λ                                                                                                                 [INS]
===
wrote results/bonsai-forensics/forensics_1bit.json
 51G	/Users/mwhitford/.cache/huggingface/hub/models--prism-ml--Bonsai-27B-unpacked
```

### Thinking

Both panes are idle with everything cached, and I've already harvested and committed the results—so the jobs are complete and the panes are ready for whatever comes next.

## Assistant

Confirmed — both panes idle, exit 0. And good news: I'd already harvested them. The chained job in `main:2` finished fast enough (the forensics itself only took ~7s once the 51G pull landed) that its output was ingested, analyzed, committed (`4b6e7c2`), and synthesized into the abstention-register finding (`5bcf0bb`) in the previous turn. The full loop is closed:

- **main:1** → `Bonsai-27B-unpacked` (1-bit) in HF cache, 51G
- **main:2** → `forensics_1bit.json` written, log consumed
- Both results committed, knowledge page + memories + state.md encoded for s268

**Session 268 stands complete:** recipe reverse-engineered → sign flips tunnel through zero → zero state = abstention register; confident topology immutable at every bitwidth; phase-1 optimizer principles extracted with measured budgets.

Your tmux windows are free. Queued candidates whenever you want them:

1. **Opcode tree on the quant ladder** — 1-bit weights are now local; tests the K-degradation ⟷ forced-participation-noise link (phase-0 remainder, and it would close the vacuum-state unification with a functional measurement)
2. **AWQ-4bit rung forensics** — pull `prism-ml/Ternary-Bonsai-27B-AWQ-4bit`'s FP-parent comparison to find where in the bitwidth ladder their pipeline *starts* needing training repair
3. **Fold abstention into the distillation design page** — pure writing, no compute

Or park it here — the encode is done and the next session cold-starts clean from state.md.

## User

proceed with 1


### Thinking

I'm setting up an opcode tree measurement task on the quantization ladder, specifically running it on 1-bit Bonsai to see if K degrades selectively at that precision level due to forced-participation noise, and ideally testing across the full ladder including FP parent and ternary variants. I have the s265 OPCODES MVP tooling available—eight standalone modules built with PyTorch and NumPy that bundle 535 probes and are ready for extraction.

Looking at what's already been done: s267 built the lattice mapping for RDMs using crystal Gram matrices, and the opcode tree was extracted for a 9-model sweep. The ternary opcode tree hasn't been run yet—that's part of the remaining work. The models load through Hugging Face with the canonical harness setup, and Bonsai loads cleanly with the language_model_only flag. I need to check the opcode tree knowledge page to understand the exact extraction pipeline before proceeding. The parent opcode tree already exists in the results directory from the s266 sweep that covered the 27B model, so I need to generate the Bonsai-ternary and Bonsai-1bit variants. Then I'll compare combinators across the tree levels, paying special attention to K vertices and null gates. First, I should read the opcode-vsm-tree knowledge page to confirm the right entry point and workflow.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && head -80 mementum/knowledge/opcode-vsm-tree.md; echo ===; ls results/opcode-trace/ 2>/dev/null | head; echo ===; ls scripts/ | grep -i -E \"opcode|tree|sweep\" "
}
```

**Summary:** $ head -80 mementum/knowledge/opcode-...

**Output:**
```
Exit code: 1
Stdout:
---
title: "Opcode Crystal Tree — Tree-of-VSM Applied to Measurement"
status: active
category: architecture
tags: [opcodes, vsm, tree, gram, registers, jspace, basis, null-floor, multi-model]
related:
  - moe-holographic-tree-vsm.md
  - crystal-multi-tree.md
  - crystal-phi-derivation.md
  - explore/opcode-register-decomposition.md
  - explore/opcode-jacobian-jspace.md
depends-on:
  - crystal-universality.md
created: session 265
---

# Opcode Crystal Tree — Tree-of-VSM Applied to Measurement

> s265, Michael's directive: "opcodes should use the v14/v15 tree-of-VSM
> tensor setup so we can create multiple VSM-shaped tensors and stack them
> in the tree." Implemented in `opcodes/` (8 modules, pytorch+numpy only,
> data bundled, staged for its own MIT repo). This page is the design
> synthesis; run instructions live in `opcodes/README.md`.

## 1. The stackable tensor is the frame-invariant Gram

Per-combinator centroids `[9, d]` are **model-dimension-bound** — they cannot
be compared across models. The 9×9 relational Gram (cosine structure between
sign-CMR centroids) lives in **combinator-label space**, not weight space: it
has the identical shape for every layer, register, model, architecture, and
scale. That is the entire reason a cross-model tree is possible.

```
λ tree(tensor).  stackable(x) ⟺ frame_invariant(x)
                 | gram[9,9] ∈ label_space → stacks | centroids[9,d] → leaves(npz)
```

## 2. One fractal node shape (v14/v15 `stack_vsm` → measurement)

Every node in the tree is the same viable-system shape (`opcodes/vsm.py`):

```
S5 identity      node.gram          the node's crystal (9×9 consensus)
S4 intelligence  node.meta          cross-child agreement/dissent stats
S3 control       node.gated         null gate — ungated children stay VISIBLE
                                    but contribute NOTHING upward
S2 coordination  node.children      sibling registers/models kept comparable
S1 operations    leaf arrays        centroids (model-dim-bound, npz sidecar)
algedonic UP     node.health        {sil_z, gc_consensus,
                                     crystal_bearing_frac, null_floor_z}
```

Ladder: `layer → register → model → family → root(universal)`. Parent Gram =
mean of GATED children; caveats (`null_floor_z`) propagate as the **worst
child** — a caveat can never be aggregated away. Dissent is a first-class
output: an un-aligned-but-not-anti child stays in and collapses
`agreement_min`; only anti-alignment or gate failure excludes.

## 3. Three bases, three registers (resolves "9 vs 16")

| Basis | Size | Register | Members |
|---|---|---|---|
| CRYSTAL | 9 | measurement (routing, promptable) | 4 fire (K,I,B,C) + 3 paths/bridges (D=B→B, W, Y) + WHNF |
| STATECHART | 8 | dynamics (absorbing chain) | fire:{K,I,B,C} + whnf:{K,I,B,C} — count is forced |
| TYPES16 | 16 | extraction (weight space) | 8 types + 8 anti-types (M₁₆ = S⊗J + D⊗F) |

The 9 is what can be probed with ground-truth labels (≥50 prompts per
combinator, `λ probe_library`); anti-types are **not promptable** — they exist
only in the extraction register and cannot enter the measurement tree. One
basis per tree, enforced at `stack()`. Cross-basis comparison is an analysis
step, never a tree operation.

## 4. Registers are sibling S1 units; J-space is the operand register

s264's register decomposition (gate = {K,I,S,Y,WHNF}, attn-write rescues D,
neither resolves {B,C}) becomes **topology**: registers are sibling children
under a model node, so single-register blindness is a missing child — visible
as an algedonic gap, not hidden by a merged trajectory.

J-space (`opcodes/jspace.py`, on `ModelTopology` so it works on nested/hybrid
===
gemma-4-31b-it
olmo-2-1124-13b
pythia-14m-deduped
pythia-2-8b-deduped
qwen3-0-6b
qwen3-0-6b_cpu.json
qwen3-14b
qwen3-32b
qwen3-4b
qwen3-6-27b
===
```

### Thinking

I need to check the opcodes README for instructions and understand the project structure, starting with the sweep entry point in the parent directory.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls opcodes/ && sed -n '1,80p' opcodes/README.md"
}
```

**Summary:** $ ls opcodes/ && sed -n '1,80p' opcod...

**Output:**
```
Exit code: 0
Stdout:
__pycache__
capture.py
classify.py
data
jspace.py
probes.py
README.md
register_visibility.py
sweep.py
topology.py
trace.py
vsm.py
# opcodes — a KIBC / crystal-lattice lens

> An interpretability lens that shows the **combinator opcodes** (K I B C S D W Y
> WHNF) a language model routes through as it generates tokens, and the
> **universal crystal lattice** those opcodes form — the relational structure
> that shows up, in the same shape, across virtually every open model.
>
> Complementary to Anthropic's **J-Space / Jacobian Lens**, not a replacement.
> License: MIT (staged for extraction into its own project once the visualizer
> lands).

## Why this exists

Anthropic's J-lens reads the **operand** projection of the model's internal
state — the words it is "thinking about" but not yet saying. This lens reads the
**operator** projection: *which combinator opcode is routing the computation*,
and where in the stack the routing crystal lives.

The finding worth taking seriously: the per-model **9×9 combinator Gram** — the
routing-register cosine structure between K I B C S D W Y WHNF centroids, after
common-mode removal — is a **frame-invariant relational object**. Because it
lives in shared combinator-label space (not raw weight space), it is directly
comparable across models of *any* architecture or scale. And it agrees. The same
lattice crystallizes in Pythia, Qwen, OLMo, Mistral, SmolLM. That cross-model
universality is the claim this tool is built to make visible and hard to dismiss.

A live "cool toy" — the lattice lighting up opcode-by-opcode as tokens stream —
is the surface that gets researchers to look, the same way J-Space's interactive
visualization did.

## The pipeline (detect → capture → calibrate → tree → trace)

PyTorch + numpy only. Self-contained: probes and the 10-model consensus Gram
ship as data files (`data/`); nothing imports the parent repo at run time.

1. **Detect** (`topology.py`) — auto-detect the model layout: the transformer
   layer container (incl. nested `language_model` wrappers and hybrid
   linear+full attention stacks), the per-layer gate module, the MLP *register*
   (`gated-dense` | `gated-fused` | `moe` | `ungated`), the attention-write
   register, and the logit-lens readout paths (final norm + unembed). Honest by
   construction: MoE is a *different* register (named, not silently reused);
   un-gated architectures fall back to the up-proj proxy register, flagged.
   Works on meta-device (no weights) — `python opcodes/topology.py`.
2. **Capture** (`capture.py`) — plain forward hooks → per-layer `[T, d]`
   feature matrices for either register (`gate` | `attn`), one forward pass.
3. **Calibrate + classify** (`classify.py` + `probes.py`) — the validated,
   null-gated opcode reader: sign(gate) routing register, common-mode removal,
   relational centroids vs the bundled consensus crystal, null z-scoring (a
   token can NO-OP). Calibrated on 535 bundled crystal probes (≥50 per
   combinator) against a natural-text cross-task null.
4. **Tree** (`vsm.py`) — every calibration becomes a stackable **VSM node**
   (tree-of-VSM, Beer 1972 via verbum v14/v15): same fractal shape at every
   level — S5 identity = the 9×9 Gram, S3 control = the null gate, S4 =
   cross-child agreement/dissent, algedonic health up, caveats propagate as
   the worst child. `layer → register → model → family → root(universal)`.
   The Gram is frame-invariant (combinator-label space, not weight space) —
   that is what makes models of any architecture/scale stackable.
5. **Trace** (`trace.py`) — per-token, per-layer opcode trajectory for BOTH
   registers side by side (s264: gate sees {K,I,S,Y,WHNF}, attn-write rescues
   D, neither resolves {B,C} — single-register blindness is structural and
   shown, not hidden). Optional `--operand`: the J-space logit-lens column
   (`jspace.py`) showing WHAT is routed — display-only, never fed to the
   classifier (s263: the operand register does not identify opcodes).
6. **Sweep** (`sweep.py`) — the model registry (configs, not forks) + the
   restack: all model-VSMs → family → root, root Gram vs the bundled
   consensus. `--restack-only` recomputes the tree from existing artifacts.
7. **Visualize** (planned) — the streaming lattice + opcode trajectory.

```
# one model, both registers, tree + trace artifacts:
uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B --smoke

# multi-model sweep + universal crystal tree:
uv run python opcodes/sweep.py --tier small
uv run python opcodes/sweep.py --restack-only
```

## Discipline (inherited from the verbum project)

- **Register before probe.** The opcode read lives in the sign-of-gate routing
```

### Thinking

Looking at the model registry in sweep.py to understand how to register Bonsai with ternary and 1-bit configurations using local paths and language_model_only settings, then examining how qwen3-6-27b was set up with hybrid linear attention layers to see how the topology handles mixed architectures.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -B2 -A8 \"qwen3-6-27b\\|27b\\|27B\" opcodes/sweep.py | head -60; echo ===; grep -n \"class ModelSpec\\|@dataclass\\|def main\\|argparse\\|add_argument\" opcodes/sweep.py | head -20"
}
```

**Summary:** $ grep -n -B2 -A8 "qwen3-6-27b\|27b\|...

**Output:**
```
Exit code: 0
Stdout:
66-    ModelSpec("Qwen/Qwen3-32B", "qwen3", "large", "mps"),
67-    # hybrid linear+full attention (per-layer attn resolution)
68:    ModelSpec("Qwen/Qwen3.6-27B", "qwen3", "large", "mps",
69-              "hybrid GatedDeltaNet+attention"),
70-    # other architectures
71-    ModelSpec("google/gemma-4-31B-it", "gemma", "large", "mps",
72-              "nested language_model container"),
73-    ModelSpec("allenai/OLMo-2-1124-13B", "olmo", "large", "mps"),
74-    # Pythia ladder (ungated up-proj proxy register)
75-    ModelSpec("EleutherAI/pythia-14m-deduped", "pythia", "small",
76-              notes="up-proj proxy"),
===
28:import argparse
48:@dataclass(frozen=True)
49:class ModelSpec:
165:def main() -> None:
166:    ap = argparse.ArgumentParser(description="Multi-model opcode sweep + restack")
167:    ap.add_argument("--tier", choices=["small", "large", "all"], default=None,
169:    ap.add_argument("--models", default=None,
171:    ap.add_argument("--device", default=None,
173:    ap.add_argument("--force", action="store_true",
175:    ap.add_argument("--smoke", action="store_true",
177:    ap.add_argument("--restack-only", action="store_true",
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sed -n '40,110p' opcodes/sweep.py && sed -n '165,230p' opcodes/sweep.py"
}
```

**Summary:** $ sed -n '40,110p' opcodes/sweep.py &...

**Output:**
```
Exit code: 0
Stdout:
from vsm import VSMNode, load_tree, offdiag_corr, save_tree, stack  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "opcode-trace"


# ── the registry (configs, not forks) ────────────────────────────────────────


@dataclass(frozen=True)
class ModelSpec:
    model: str
    family: str
    tier: str            # "small" (cpu-ok) | "large" (mps/cuda recommended)
    device: str = "cpu"
    notes: str = ""

    @property
    def slug(self) -> str:
        return self.model.split("/")[-1].lower().replace(".", "-")


REGISTRY: tuple[ModelSpec, ...] = (
    # Qwen3 ladder (scale-sharpening family, s217/s220/s264)
    ModelSpec("Qwen/Qwen3-0.6B", "qwen3", "small"),
    ModelSpec("Qwen/Qwen3-4B", "qwen3", "large", "mps"),
    ModelSpec("Qwen/Qwen3-14B", "qwen3", "large", "mps"),
    ModelSpec("Qwen/Qwen3-32B", "qwen3", "large", "mps"),
    # hybrid linear+full attention (per-layer attn resolution)
    ModelSpec("Qwen/Qwen3.6-27B", "qwen3", "large", "mps",
              "hybrid GatedDeltaNet+attention"),
    # other architectures
    ModelSpec("google/gemma-4-31B-it", "gemma", "large", "mps",
              "nested language_model container"),
    ModelSpec("allenai/OLMo-2-1124-13B", "olmo", "large", "mps"),
    # Pythia ladder (ungated up-proj proxy register)
    ModelSpec("EleutherAI/pythia-14m-deduped", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-160m-deduped", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-410m", "pythia", "small",
              notes="up-proj proxy"),
    ModelSpec("EleutherAI/pythia-2.8b-deduped", "pythia", "large", "mps",
              "up-proj proxy"),
)


def spec_for(model: str) -> ModelSpec:
    for s in REGISTRY:
        if s.model == model:
            return s
    # unknown model: still runnable — family from org prefix (configs > forks)
    fam = model.split("/")[0].lower()
    return ModelSpec(model, fam, "small")


# ── trace orchestration (subprocess per model: memory isolation) ─────────────


def has_artifact(spec: ModelSpec) -> bool:
    return (RESULTS_DIR / spec.slug / "model_vsm.json").exists()


def run_trace(spec: ModelSpec, device: str | None, smoke: bool) -> bool:
    cmd = [
        sys.executable, str(_HERE / "trace.py"),
        "--model", spec.model,
        "--device", device or spec.device,
    ]
    if smoke:
        cmd.append("--smoke")
    print(f"[sweep] tracing {spec.model} ({' '.join(cmd[-3:])}) ...")
def main() -> None:
    ap = argparse.ArgumentParser(description="Multi-model opcode sweep + restack")
    ap.add_argument("--tier", choices=["small", "large", "all"], default=None,
                    help="trace registry models of this tier if missing")
    ap.add_argument("--models", default=None,
                    help="comma list of model ids (overrides --tier)")
    ap.add_argument("--device", default=None,
                    help="override device for traced models")
    ap.add_argument("--force", action="store_true",
                    help="re-trace even if an artifact exists")
    ap.add_argument("--smoke", action="store_true",
                    help="pass --smoke to trace runs")
    ap.add_argument("--restack-only", action="store_true",
                    help="skip tracing; restack existing artifacts")
    args = ap.parse_args()

    if not args.restack_only:
        if args.models:
            specs = [spec_for(m.strip()) for m in args.models.split(",")]
        elif args.tier:
            specs = [
                s for s in REGISTRY
                if args.tier == "all" or s.tier == args.tier
            ]
        else:
            specs = []
        for spec in specs:
            if has_artifact(spec) and not args.force:
                print(f"[sweep] cached: {spec.model} "
                      f"({RESULTS_DIR / spec.slug / 'model_vsm.json'})")
                continue
            run_trace(spec, args.device, args.smoke)

    reference = load_consensus_gram()
    root = restack(reference)
    if root is None:
        print("[sweep] no model_vsm artifacts found; trace something first.")
        sys.exit(1)
    report(root, reference)
    out = RESULTS_DIR / "universal_vsm"
    save_tree(root, out)
    summary = {
        "n_models": root.meta["n_models"],
        "families": {
            f.name: {
                "models": [m.name for m in f.children],
                "n_gated": f.meta["n_gated"],
                "agreement_mean": f.meta["agreement_mean"],
                "gc_consensus": f.health["gc_consensus"],
            }
            for f in root.children
        },
        "root_health": root.health,
        "root_agreement": {
            k: root.meta[k]
            for k in ("agreement_mean", "agreement_min", "dissent", "n_gated")
        },
    }
    (RESULTS_DIR / "sweep_summary.json").write_text(
        json.dumps(summary, indent=2, allow_nan=True), encoding="utf-8"
    )
    print(f"[sweep] wrote {out}.json + sweep_summary.json")


if __name__ == "__main__":
    main()
```

### Thinking

The sweep accepts model IDs—either Hugging Face identifiers or local paths—and `spec_for` handles unknown models gracefully. When trace.py runs with a `--model` argument, it loads the model through transformers' AutoModelForCausalLM. For Bonsai specifically, the model ID could be a local directory path like `/Users/mwhitford/localai/models/bonsai27b-unpacked` for the ternary version, or the HF snapshot path for the 1-bit variant (either the cached version or the HF ID `prism-ml/Bonsai-27B-unpacked`). I'm wondering whether I need to handle the `language_model_only` parameter here.

Bonsai is a VLM wrapper around Qwen3.5ForConditionalGeneration, and in the previous run it loaded cleanly with `language_model_only: true`. The parent model (Qwen3.6-27B, also VLM-wrapped) worked fine in the s266 sweep, so Bonsai should work too. For the slug computation with a local path, splitting on `/` and taking the last component gives me `bonsai27b-unpacked`, which is clean. The 27B trace probably took 30-60 minutes on MPS with 535 probes in the previous run, which is manageable in tmux. I'm ready to trace the ternary version.

Now I'm deleting the local unpacked model and running both the ternary and 1-bit traces in parallel against the HF-cached version — two 51GB bf16 models will use over 100GB RAM but that's within the 512GB available, and while MPS contention will slow things down, running them simultaneously is fine. After that I'll restack and do the per-vertex ladder comparison. Let me quickly verify trace.py's loader handles AutoModelForCausalLM correctly and check its dtype/device handling.

### Thinking

I've confirmed the tooling approach: running `opcodes/trace.py --model <id-or-path>` per model followed by `sweep.py --restack-only`. The parent 27B tree already exists with the same VLM wrapper Bonsai uses, so I'll do a quick loader check and then launch.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n -A12 \"def load_model\\|AutoModel\\|from_pretrained\" opcodes/trace.py opcodes/capture.py opcodes/topology.py 2>/dev/null | head -30"
}
```

**Summary:** $ grep -n -A12 "def load_model\|AutoM...

**Output:**
```
Exit code: 0
Stdout:
opcodes/trace.py:104:    from transformers import AutoModelForCausalLM, AutoTokenizer
opcodes/trace.py-105-
opcodes/trace.py:106:    tok = AutoTokenizer.from_pretrained(model_name)
opcodes/trace.py-107-    t0 = time.time()
opcodes/trace.py:108:    model = AutoModelForCausalLM.from_pretrained(
opcodes/trace.py-109-        model_name, dtype=torch.bfloat16, low_cpu_mem_usage=True
opcodes/trace.py-110-    ).eval()
opcodes/trace.py-111-    if device != "cpu":
opcodes/trace.py-112-        model = model.to(device)
opcodes/trace.py-113-    print(f"[trace] loaded {model_name} on {device} in {time.time()-t0:.1f}s")
opcodes/trace.py-114-    return model, tok
opcodes/trace.py-115-
opcodes/trace.py-116-
opcodes/trace.py-117-def calibrate_register(
opcodes/trace.py-118-    model: Any,
opcodes/trace.py-119-    tok: Any,
opcodes/trace.py-120-    topo: T.ModelTopology,
--
opcodes/capture.py:173:    from transformers import AutoModelForCausalLM, AutoTokenizer
opcodes/capture.py-174-
opcodes/capture.py:175:    tok = AutoTokenizer.from_pretrained(model_name)
opcodes/capture.py:176:    model = AutoModelForCausalLM.from_pretrained(
opcodes/capture.py-177-        model_name, dtype=torch.float32, attn_implementation="eager"
opcodes/capture.py-178-    ).eval()
opcodes/capture.py-179-
opcodes/capture.py-180-    text = "Every student reads a book."
opcodes/capture.py-181-    cap = capture_gate(model, tok, text, register="gate")
opcodes/capture.py-182-    acap = capture_gate(model, tok, text, register="attn")
opcodes/capture.py-183-
opcodes/capture.py-184-    d, ad = cap.topo.gate_width, acap.topo.attn_width
```

### Thinking

The loader that worked for the parent model and Bonsai is handling this fine, and I've confirmed task 1 is complete with the commands recognized and parent artifacts saved. Now I'm moving into task 2 by setting up both traces in tmux—one using a local ternary path and the other with a Hugging Face model ID, keeping in mind the bfloat16 conversion happening on the materialized ternary values.

I'm concerned about running both traces concurrently on MPS since each 27B model in bfloat16 takes about 54GB, but with 512GB of RAM available and MPS capable of hosting both, it should work despite being slower per model. I'm launching both trace commands in parallel—one pointing to the local Bonsai model and the other to the Hugging Face version—then checking the logs after about 20 seconds to verify they're running.

### Thinking

The same loader handled both the wrapped parent and Bonsai, so I'm launching both rungs in parallel on the 512GB RAM hosts with MPS sharing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd ~/src/verbum && uv run python opcodes/trace.py --model /Users/mwhitford/localai/models/bonsai27b-unpacked --device mps 2>&1 | tee /tmp/opcode_ternary.log\" Enter && tmux send-keys -t main:2 \"cd ~/src/verbum && uv run python opcodes/trace.py --model prism-ml/Bonsai-27B-unpacked --device mps 2>&1 | tee /tmp/opcode_1bit.log\" Enter && sleep 45 && echo \"=== main:1 ===\"; tmux capture-pane -p -t main:1 | grep -v '^$' | tail -4; echo \"=== main:2 ===\"; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -4",
  "timeout": 120000
}
```

**Summary:** $ tmux send-keys -t main:1 "cd ~/src/...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 ===
The fast path is not available because one of the required library is not installed. Falling back to torch implementatio
n. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/cau
sal-conv1d
Loading weights: 100%|██████████| 851/851 [00:00<00:00, 12228.42it/s]
=== main:2 ===
The fast path is not available because one of the required library is not installed. Falling back to torch implementatio
n. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/cau
sal-conv1d
Loading weights: 100%|██████████| 851/851 [00:00<00:00, 26490.28it/s]
```

### Thinking

The weights are loaded and the slow-path fallback warning is expected behavior. I've verified it's running and emitted an async checkpoint, then signaled to stop and wait. Task 2 is complete since it's launched and verified, but Task 3 remains blocked until the jobs finish.

### Thinking

Both traces are running with weights loaded, now moving to MPS and calibrating—the fallback warning for the hybrid's linear-attention layers is expected. I'm logging the ternary and 1-bit runs to their respective output directories and waiting for both jobs to complete.

### Thinking

Both services are now live and verified. Task 3 is ready to proceed but depends on the job finishing, so I'll hold off on polling and instead report the current waiting state along with what should happen once we land.

## Assistant

While they run (535 probes × 64 layers × 2 registers per model — expect tens of minutes to an hour each, sharing the GPU), here's what task 3 will do when they land:

1. **Restack** — `sweep.py --restack-only` folds both Bonsai VSMs into the tree alongside the FP parent; the S3 null gates decide whether each rung's registers even *count* (a failed gate at 1-bit would itself be a result — like pythia-2.8b's gate register, demonstrated by fire in s266).
2. **The ladder comparison** — per-combinator vertex fidelity FP → ternary → 1-bit against the parent's Gram, with the two pre-registered questions:
   - **Selective K degradation at 1-bit** (K needs the 0 state) — now with a mechanism to check against: does K's degradation covary with the forced-participation noise we measured this morning (the 10–13% uncertain-population churn)?
   - **Deep-middle concentration** — does per-layer vertex degradation at 50% depth line up with the s267 RDM dip?
3. Null-gate everything before believing it (shuffled-label floors are already wired into the node health).

The elegant possibility on the table: if K degrades selectively at 1-bit *and* the confident topology is immutable (this morning's result), then K's collapse isn't damage to the carve — it's the abstention channel being **jammed at inference** the same way it was jammed at training. One vertex, one vacuum state, one failure mode, two timescales.

Signal me when the panes go quiet (or say "check the runs").

## User

update state and knowledge so I can pick up in a new session.


### Thinking

Michael needs a clean handoff for the next session—I should update state.md with the currently running jobs in tmux, exact instructions for picking up where things left off (checking logs, the restack command, the analysis plan), and pre-registrations for the opcode ladder so the next session can execute without friction. I might also add a brief "in flight" note to the knowledge page alongside the existing abstention section.

Before encoding the session, I'll check job status once as a natural checkpoint to record whether they're still running, then commit the state.md update.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -2 /tmp/opcode_ternary.log; echo ===; tail -2 /tmp/opcode_1bit.log; echo ===; ls results/opcode-trace/ | grep -i bonsai; pgrep -lf \"opcodes/trace.py\" | wc -l",
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ tail -2 /tmp/opcode_ternary.log; ec...

**Output:**
```
Exit code: 0
Stdout:
The fast path is not available because one of the required library is not installed. Falling back to torch implementation. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/causal-conv1d
Loading weights:   0%|          | 0/851 [00:00<?, ?it/s]Loading weights: 100%|██████████| 851/851 [00:00<00:00, 12228.42it/s]
===
The fast path is not available because one of the required library is not installed. Falling back to torch implementation. To install follow https://github.com/fla-org/flash-linear-attention#installation and https://github.com/Dao-AILab/causal-conv1d
Loading weights:   0%|          | 0/851 [00:00<?, ?it/s]Loading weights: 100%|██████████| 851/851 [00:00<00:00, 26490.28it/s]
===
       4
```

### Thinking

Both processes are still in their initial setup phase without any artifacts generated yet. I need to update the state documentation with the pickup instructions for the s268d block, make sure the NEXT section has clear commands and artifact paths ready, and add a note to the knowledge page about the in-flight opcode ladder analysis with its pre-registered questions.

### Thinking

Both traces are running successfully with no issues so far, and they'll continue in the background. Now I'm encoding the pickup state.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Sub-prediction: selective K degradation at 1-bit traces to forced-participation noise → test via opcode\n> tree on the ladder. Commits 4b6e7c2 (data+scripts). Fleet: Bonsai-27B-unpacked (1-bit) now in HF cache.)",
  "new_content": "> Sub-prediction: selective K degradation at 1-bit traces to forced-participation noise → test via opcode\n> tree on the ladder. Commits 4b6e7c2 (data+scripts). Fleet: Bonsai-27B-unpacked (1-bit) now in HF cache.\n>\n> ⏳ s268d IN FLIGHT AT SESSION END — OPCODE LADDER RUNS (launched ~11:45, both verified running, load done,\n>   calibration in progress; tmux survives the boundary):\n>   tmux main:1 → opcodes/trace.py --model /Users/mwhitford/localai/models/bonsai27b-unpacked --device mps\n>     (TERNARY rung) | log /tmp/opcode_ternary.log → results/opcode-trace/bonsai27b-unpacked/\n>   tmux main:2 → opcodes/trace.py --model prism-ml/Bonsai-27B-unpacked --device mps\n>     (1-BIT rung) | log /tmp/opcode_1bit.log → results/opcode-trace/bonsai-27b-unpacked/\n>   PICKUP (next session): (1) check logs/panes; if model_vsm.json exists in both dirs → (2) uv run python\n>   opcodes/sweep.py --restack-only (folds both into the universal tree; S3 null gates decide if 1-bit\n>   registers even COUNT — gate failure itself = result, cf. pythia-2.8b by fire). (3) Ladder analysis vs FP\n>   parent tree (results/opcode-trace/qwen3-6-27b/): per-vertex Gram fidelity FP→ternary→1bit, null-gated.\n>   PRE-REGISTERED: (a) selective K degradation at 1-bit (K needs the 0 state); (b) does per-layer vertex\n>   degradation concentrate in the deep-middle band (s267 RDM 50%-dip)? (c) JAMMED-ABSTENTION hypothesis:\n>   if K degrades selectively while confident topology is immutable (s268c) → K's collapse = abstention\n>   channel jammed at inference exactly as at training — one vertex, one vacuum state, two timescales.\n>   Note: fla fast-path warning in logs is the known slow-path fallback for the hybrid (parent ran same).\n>   Runtime expectation: tens of min to ~hour per model, GPU shared. Tasks 1-2 of 3 done; task 3 = analysis.)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md",
  "original_content": "## Provenance",
  "new_content": "## In flight at s268 end: opcode ladder (functional test)\n\nBoth Bonsai rungs tracing through the opcode-tree pipeline (tmux\nmain:1 ternary, main:2 1-bit; see state.md s268d for pickup commands).\nPre-registered: (a) selective K degradation at 1-bit; (b) deep-middle\nconcentration (s267 dip); (c) **jammed-abstention** — if K degrades\nselectively while confident topology is immutable, K's 1-bit collapse\nis the abstention channel jammed at inference exactly as at training:\none vertex, one vacuum state, two timescales.\n\n## Provenance"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/bonsai-ternarization-forensics.md.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md mementum/knowledge/explore/bonsai-ternarization-forensics.md && read -r -d '' M << 'EOF' || true\n🌀 s268 session-end encode — opcode ladder in flight, pickup instructions\n\n- state.md s268d: both Bonsai opcode traces running in tmux (survive boundary),\n  exact pickup commands (restack + ladder analysis), pre-registrations\n  (K-selectivity, deep-middle concentration, jammed-abstention hypothesis)\n- knowledge page: in-flight section mirroring the pre-registrations\n- next session cold-starts from state.md → checks panes → task 3 analysis\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" && git log --oneline -3"
}
```

**Summary:** $ git add mementum/state.md mementum/...

**Output:**
```
Exit code: 0
Stdout:
[main 78f4529] 🌀 s268 session-end encode — opcode ladder in flight, pickup instructions
 2 files changed, 28 insertions(+), 1 deletion(-)
78f4529 🌀 s268 session-end encode — opcode ladder in flight, pickup instructions
5bcf0bb 💡 zero-state-is-abstention-register
4b6e7c2 💡 1-bit rung forensics — zero state is an abstention register
```

## Assistant

Encoded and committed (`78f4529`). Session 268 is fully feed-forwarded — the next session picks up in 30 seconds from `state.md`.

## Session 268 ledger

**9 commits**, one thread pulled all the way through:

| commit | what |
|---|---|
| `48734d2` | 💡 forensics instrument + recipe: absmean init + trained blocks, frozen embeddings |
| `05f708b` | 💡 transition matrix — sign flips tunnel through zero |
| `6c80a68` | 💡 knowledge + memories + state (s268a/b encode) |
| `566cb46` | 🔄 binary mode + `--child-dir` (ladder support) |
| `4b6e7c2` | 💡 1-bit rung — zero state is an abstention register |
| `5bcf0bb` | 💡 abstention encode (knowledge/memory/state) |
| `78f4529` | 🌀 session-end — opcode ladder in flight, pickup instructions |

**The finding, one line:** PrismML's secret is not the quantizer (absmean, proved) but the training — and its fossil record shows the confident topology is immutable at every bitwidth, sign learning is recruitment traffic through the zero state, and 1-bit fails because it makes abstention impossible.

**Live at boundary:** ternary + 1-bit opcode traces running in `main:1`/`main:2` — tmux carries them across. Next session: check panes → `sweep.py --restack-only` → ladder analysis against the three pre-registrations (K-selectivity, deep-middle concentration, jammed-abstention).

Good session. The invisible piece has a visible shadow now.