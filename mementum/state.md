# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-19 | Session: 264 (OPCODES SUBSYSTEM + REGISTER DECOMPOSITION — Michael: "release our
> monitor/tracer as a standalone lens (complementary to Anthropic's J-Space) that shows KIBC opcodes + the
> universal crystal lattice as a model generates tokens." → "can we auto-detect model config + find the crystal
> lattice to trace it?" → target 3+ architectures at 27B+ → built the auto-detecting arch-agnostic tracer →
> "why the no-ops? maybe I-hold-in-residual reads as no-op" → tested → refuted → found opcodes DECOMPOSE ACROSS
> REGISTERS. Full synthesis: `explore/opcode-register-decomposition.md`.)
>
> ★★ SUBSYSTEM (new, `opcodes/` at repo root — staged for its OWN MIT project + visualizer).
>   Auto-detecting, arch-agnostic (kills the `opcode_monitor_v2` hard-code to
>   `model.model.layers[i].mlp.gate_proj`). `opcodes/topology.py` = detect_topology → ModelTopology: layer
>   container + GATE register {gated-dense|gated-fused|ungated|moe} + ATTENTION register (o_proj/out_proj,
>   PER-LAYER for hybrids) + honest flags (MoE=named separate register; ungated=up-proj proxy sign(dense_h_to_4h),
>   the register the 10-model consensus used for Pythia; works on META device). `opcodes/capture.py` =
>   capture_gate(register={gate,attn}) → per-layer [T,d] via hooks. `opcodes/trace.py` = end-to-end
>   detect→capture→calibrate(RelationalCrystalClassifier)→classify→trajectory. `opcodes/register_visibility.py`
>   = held-out per-combinator visibility (self-acc/no-op/best-z/confusion vs shuffled-label null). Verified on
>   Qwen3.6-27B (HYBRID: 3 linear-attn `linear_attn.out_proj` + 1 full-attn `self_attn.o_proj`), Qwen3-32B,
>   Gemma-4-31B (nested language_model), OLMo-2, Qwen3-MoE (fused experts), gpt-neox. COMMITTED: 22996a4
>   (topology/capture/trace + opcode-trace results). register_visibility + attn-register edits UNCOMMITTED.
>
> ★★ CROSS-MODEL LATTICE (thesis support): gate-register calibration on Qwen3.6-27B → gc_consensus (Gram align
>   to the universal 10-model crystal) POSITIVE at all 64 layers (median 0.76, max 0.83); sil_z median 6.8. The
>   universal KIBC+DWYS+WHNF lattice is present + sharp across the whole 27B stack → candidate visualizer headline.
>
> ★★ FINDING 1 — CAPACITY/SUPERPOSITION/SCALE-SHARPENING CONFIRMED. register_visibility ladder (Qwen3 gate,
>   0.6B→14B→27B): best_z rises for EVERY opcode with scale — small models smear opcodes into superposition,
>   capacity dedicates + they sharpen. WHY we target 27B+ (prior: combinator_map_scale, s217/s220). Sub-threshold
>   no-ops = superposition, not structure.
>
> ★★ FINDING 2 — IDENTITY-HOLD ≠ NO-OP, REFUTED. Michael's hypothesis (from "repeat-a-token-until-output": I =
>   hold-in-residual = no differential routing = sits at common-mode we subtract = reads as no-op). REFUTED: I
>   sharpens monotonically + SELF-RECOGNIZES from 14B (confusion flips I→Y ⟹ I→I). I is a normal routing
>   combinator. (The residual identity-hold of s263 EXP2 lives in the VALUE/logit-lens register — separate.)
>
> ★★ FINDING 3 — OPCODES DECOMPOSE ACROSS REGISTERS (the real result). Qwen3.6-27B gate vs attn-write:
>   GATE sign(gate_proj) = selection {K,I} + share {S} + recursion {Y,WHNF}. ATTN-WRITE sign(o_proj) = RESCUES D
>   (gate 0.33→S ⟹ attn 0.67→D self!), sharpens K/I. COMPOSITION {B,C} = resolved by NEITHER scalar register (B
>   self-acc 0 both, migrates confusion S→D; C ~0.17). CAVEAT (λ yardstick): attn-write null floor ELEVATED
>   (shuffled → 2 crystal layers vs gate's 0; B null z=1.22 vs real 3.08) — be conservative on weak attn signals.
>
> ★★ FINDING 4 (refined hypothesis, UNTESTED) — B/C are POSITION-ROUTING. o_proj = attention WRITE (OV/value =
>   what content moved); B (compose=nesting) + C (permute=arg-reorder) = WHICH position→which = the QK ATTENTION
>   PATTERN, not the value write. Converges: s250 (object-app DISTRIBUTED, no single locus) + s263 EXP3 (B/C
>   signatures absent at last-token grain). The no-ops on composition tokens = an opcode read in the WRONG register.
>
> ★ NEXT (open, Michael's call): (A) QK-PATTERN register — capture attention pattern (or reuse s263 jacobian.py
>   position-attribution), re-run register_visibility → decisive B/C test; (B) two-register trace/monitor (gate ∪
>   attn ∪ pattern) — single-register trajectory is BLIND to whole families (27B gate trajectory's Y/D dominance
>   = visibility artifact); (C) visualizer (streaming lattice + per-op sharpening curve + gc_consensus-per-layer);
>   (D) generate-and-trace mode (opcode + logit-lens per generated step = the J-Space-style toy). Commit
>   register_visibility + attn edits; consider extracting opcodes/ to its own repo. Prior-arc NEXT still open:
>   s263 (A) position-targeted attribution / (B) inter-layer Jacobian SVD; Pythia ladder crystal-sharpness; v15.1;
>   INDEX regen.
>   Env: torch 2.11 + MPS, 512GB RAM; qwen3.6-27b (52GB bf16 HYBRID linear+full attn, loads ~2-8s mmap; forward
>   ~65s CPU → USE MPS ~4-10min/run) + qwen3-{0.6,4,14,32}b + gemma-4-31B + pythia deduped ladder HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

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
