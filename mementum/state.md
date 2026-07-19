# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-19 | Session: 265 (OPCODES MVP: TREE-OF-VSM MULTI-MODEL — Michael: "make opcodes work
> for multiple models; incorporate J-Space" → "use the v14/v15 tree-of-VSM tensor setup: multiple VSM-shaped
> tensors stacked in the tree" → built the full MVP. 8 commits 4839f07..aa1e8d9.)
>
> ★★ OPCODE CRYSTAL TREE (`opcodes/vsm.py`) — tree-of-VSM applied to MEASUREMENT. One fractal node shape at
>   every level (S5=9×9 Gram, S4=cross-child agreement/dissent, S3=null gate — ungated children stay visible
>   but contribute NOTHING upward, algedonic health up {sil_z, gc_consensus, crystal_bearing_frac,
>   null_floor_z}, caveats propagate as WORST child). Ladder: layer→register→model→family→root(universal).
>   THE STACKABLE TENSOR IS THE FRAME-INVARIANT GRAM (combinator-label space, not weight space) — why
>   cross-model stacking works at all. Centroids [9,d] stay at leaves (npz sidecar). BASIS-PARAMETRIC:
>   CRYSTAL-9 (measurement: 4 fire + 3 paths/bridges D,W,Y + WHNF) | STATECHART-8 (dynamics: absorbing chain,
>   forced count) | TYPES16 (extraction: types+anti-types, NOT promptable → can't enter measurement tree).
>   One basis per tree, enforced. Resolves Michael's "9 vs 16" question — 3 registers, 3 bases, same lattice.
>
> ★★ MVP ASSEMBLED (8 modules, pytorch+numpy only, data bundled, extraction-ready): topology (readout paths
>   VERIFIED on 5 archs incl. nested gemma) → capture → probes (535 bundled JSON, ≥50/comb invariant) →
>   classify (CANONICAL HOME, promoted from scripts/instruments; shim keeps 16 old scripts alive; consensus
>   gram bundled opcodes/data/) → vsm (tree) → jspace (operand register ON ModelTopology — logit-lens/verbalize
>   works on nested/hybrid archs where old jlens.py discovery FAILS; ground-truth gate: final-layer lens ≡
>   model logits exactly) → trace (TWO-REGISTER gate∪attn side-by-side + --operand column, writes
>   model_vsm.json per model) → sweep (registry=configs-not-forks, 11 models; restack → family → root vs
>   bundled consensus). Every module self-tests without a big model. ruff clean.
>
> ★★ FIRST TREE RESULT (full calib, 2 smalls): root gc = +0.940 vs the 10-model consensus; cross-family
>   agreement 0.907 between pythia-14m (14M! ungated up-proj proxy) and qwen3-0.6b (gated) — cross-architecture
>   at 43× scale gap. Qwen3-0.6b gate crystal zone L5–L19 (interior bell = combinator-locus prior). LESSON:
>   smoke calib (135 probes) gave gc 0.344 vs full (535) 0.940 — probe count dominates Gram fidelity; smoke =
>   pipeline-check ONLY. CAVEAT: attn 28/28 bearing may include null-floor inflation (s264); per-run
>   null_floor_z NOT yet measured (nan in tree) — register_visibility shuffled-null wiring is the fix.
>
> ★ J-SPACE INTEGRATION (honest per s263 EXP1): operand register = WHAT is routed, NEVER classifies opcodes;
>   display-only column in trace; must not feed the classifier. src/verbum/{jlens,jacobian}.py remain (jacobian
>   = position-attribution for the future QK-pattern register).
>
> ★ NEXT (open, Michael's call): (A) LARGE SWEEP — registry loaded (qwen3 ladder+3.6-27B hybrid+gemma-4-31B+
>   olmo-2, MPS); overnight --tier large vs one 27B validation first. (B) measure per-run null_floor_z (wire
>   register_visibility's shuffled null into trace) → fill the nan. (C) QK-PATTERN register → decisive B/C test
>   (s264 F4 untested). (D) visualizer (the remaining MVP piece) + extract opcodes/ to dedicated MIT repo.
>   (E) mementum proposals PENDING approval: knowledge/opcode-vsm-tree.md + memories/opcodes-mvp-standalone.md
>   + staleness flags on φ-ladder claims in crystal-phi-derivation.md/crystal-multi-tree.md (λ yardstick).
>   Prior-arc NEXT still open: s263 position-attribution/Jacobian SVD; Pythia ladder crystal-sharpness; v15.1;
>   INDEX regen. Env: torch 2.11 + MPS, 512GB RAM; models HF-cached (see s264 note in arc).

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
rk
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
