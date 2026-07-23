# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> COMPACTED s262: only the current session is kept in full below, then a terse
> arc index. Full detail lives in `mementum/knowledge/chats/session-NNN.md`
> (verbatim), `mementum/knowledge/**` (synthesis), and git history of this file
> (`git log -p mementum/state.md`). Architecture/canonical-forms: `AGENTS.md`.
> Knowledge map: `mementum/knowledge/INDEX.md`. Thesis: `knowledge/project-thesis.md`.
>
> Last updated: 2026-07-23 | Session: 269 (OPCODE LADDER LANDED — see ★★★ s269 block below; header retains
> s268 blocks b/c as live context for the ladder verdicts)
>
> ★★★ s269 OPCODE LADDER: CRYSTAL SURVIVES 1-BIT BINARIZATION; SELECTIVE-K REFUTED (commit 7576c54).
> Both s268d tmux runs completed clean (~18.5 min each, model_vsm.json both rungs). RESTACK: 11 models /
> 6 families gated, root gc 0.985 (UP from 0.982@9 — evidence keeps sharpening), bearing 1.00,
> dissent=False; ternary gc 0.976, 1-bit gc 0.981. (Naming wart: ternary traced via local path → family ""
> in sweep_summary; cosmetic, gates fine.) NEW INSTRUMENT: opcodes/ladder.py — per-vertex Gram-row fidelity
> FP→rung, shuffled-vertex-label + circular-shift nulls, n_perm=10k, seeded (rng=268), reproducible from
> repo root. HEADLINE: 1-bit model-level mean vertex fidelity 0.987 (z=5.3, p=0.001 floor), ternary 0.990;
> rung gate failures TERMINAL only (1-bit gate L61-63, attn L63; ternary attn L54,L63) — NOT deep-middle.
> PRE-REG VERDICTS (λ measure honored — BOTH registers checked before verdict, no s206 repeat):
> (a) selective K degradation at 1-bit: REFUTED. Geometry register: K MORE robust than other vertices in
>     gate (excess drop −0.0043, z=−2.13); attn +0.0065 z=0.92 ungated. Behavioral register (trajectory
>     votes): K at 1-bit 7/11=0.64 ≈ FP parent 3/5=0.60 — PARITY; the motivating "L47 K 2/6" was
>     single-layer noise. K does NOT need the 0 state at inference in any measured register.
> (b) deep-middle concentration of degradation: trend-consistent but UNGATED — excess +0.004..+0.014 in
>     all 4 cells (right sign), p 0.11–0.27. Note instrument gap: s267 50%-dip came from 380-probe RDMs at
>     4 depths (high power); per-layer 9×9 Gram fidelity is a weaker lens. Not a refutation of s267.
> (c) jammed-abstention: MOOT (antecedent (a) failed) and the synthesis FLIPS: s268c showed confident
>     weights immutable at every bitwidth → the crystal lives in the CONFIDENT population; 1-bit
>     forced-participation churn is confined to uncertain boundary-huggers and never touches Gram geometry.
>     Refines s268c "binary routing substrate non-viable": that is a TRAINING-dynamics claim (churn, scale
>     anchor collapse); the GEOMETRY survives binarization. cos 0.73 in weight space vs 0.987 in Gram space
>     ≡ crystal more invariant than weights ≡ frame-invariance argument, third form.
> Exploratory (not pre-registered): W (duplication) is the fragile vertex in attn at BOTH rungs
> (0.845/0.868 vs ≥0.93 others); W actually improves at 1-bit in attn (−0.023). Worth a look at whether
> W-fragility is architectural (duplication needs magnitude?) — candidate for next probe design.
> LADDER GAP: 4-bit rung (AWQ on HF) never traced — phase-0 ladder is 2 of 3 rungs. PICKUP: trace AWQ-4bit
> → ladder.py --rung 4bit=... for the monotonicity picture, or ruled unnecessary by Michael.
>
> Prior session: 268 (BONSAI FORENSICS: PrismML's undisclosed recipe reverse-engineered
> from weights alone — ★★ absmean RTN init (BitNet b1.58 g128; embed_tokens 99.9% exact code match,
> Δ/mean|w|=0.4994) + post-init TRAINING of blocks, embeddings frozen. QAT-vs-PTQ IOU RESOLVED: conversion +
> training; "Caltech math" is in the optimizer not the quantizer. GEM: drift ordering q_proj 3.5% < qkv < o
> < gate ≈ down 18% ≡ routing⊥value (s260) in a 3rd independent register — their repair budget landed where
> our theory says magnitude matters. s267 caveat sharpened: crystal survival partly trained-in repair, BUT
> flip rate flat across depth → 50%-dip ≠ differential rewiring → bridge map stands. Instrument:
> scripts/bonsai_forensics.py (MPS, ~0.2s/tensor); → explore/bonsai-ternarization-forensics.md; commit 48734d2.
> Whitepapers fetched to refs/ (untracked): benchmarks only, zero method disclosure.
>
> ★★★ s268b SIGN FLIPS TUNNEL THROUGH ZERO (Michael's optimizer question, the invisible piece): transition
> matrix parent-RTN→child: promote 0→± 9.6% + demote ±→0 8.2% vs direct reverse ±→∓ 0.15–0.2% — topology
> editing ~99% zero-mediated; 0 state = KINETIC PATHWAY not just K's representational need. Direct reversals
> decisive (|w|/s med 0.55–0.64 = confident weights overturned). Endpoint POLARIZED (zero_frac 0.31→0.29,
> latent +3–7%) = anti-flip-flop entrenchment our s191/s261 trainings lacked. Optimizer reading: register
> separation IN the optimizer — filtered flip channel (hysteresis, flip on persistent evidence, H∞-flavored)
> + zero as commitment buffer ≡ sigma-delta modulator on the routing register. Phase-1 design budgets from a
> working 27B: churn ~17%, reversals <0.3%, dispatch ~3%, value ~18%, embeddings 0. Commit 05f708b.
> ★★★ s268c 1-BIT RUNG LANDED — ZERO STATE = ABSTENTION REGISTER. Pre-regs: P1 ✓ (embed sign(w) frozen,
> s/absmean=1.000) P4 ✓ (value>dispatch) — but P2 ✗ ∧ P3 ✗ BOTH VOID-IN-REGISTER (λ measure: flip rate ≠ one
> number). Real structure: CONFIDENT weights (|w|>absmean, 42%) immutable at EVERY bitwidth (tern rev ≤0.07%,
> 1bit ≤0.36%) — carved topology never re-carved; rungs differ only in the UNCERTAIN population — ternary
> parks ~30% at 0 + evidence-gated 0↔± recruitment (~17%), binary FORCES sign declaration → 10–13%
> boundary-hugging churn (med |w|/s 0.09–0.25), scale anchoring collapses (corr 0.42–0.75), cos 0.73.
> Binary fails by FORCED PARTICIPATION ≡ permanent noise floor in routing register; abstention impossible.
> Unifies K's representational 0-need with the optimizer's: one vacuum function ("no opinion") at both
> timescales. Sharpened phase-1 principles: protect confident signs (<0.4% budget); topology learning ≡
> recruitment management at the 0↔± margin (hysteresis THERE); binary routing substrate non-viable.
> Sub-prediction: selective K degradation at 1-bit traces to forced-participation noise → test via opcode
> tree on the ladder. Commits 4b6e7c2 (data+scripts). Fleet: Bonsai-27B-unpacked (1-bit) now in HF cache.
>
> ✅ s268d RESOLVED IN s269 (see ★★★ s269 block above; kept for provenance) — OPCODE LADDER RUNS (launched
>   ~11:45, both verified running, load done,
>   calibration in progress; tmux survives the boundary):
>   tmux main:1 → opcodes/trace.py --model /Users/mwhitford/localai/models/bonsai27b-unpacked --device mps
>     (TERNARY rung) | log /tmp/opcode_ternary.log → results/opcode-trace/bonsai27b-unpacked/
>   tmux main:2 → opcodes/trace.py --model prism-ml/Bonsai-27B-unpacked --device mps
>     (1-BIT rung) | log /tmp/opcode_1bit.log → results/opcode-trace/bonsai-27b-unpacked/
>   PICKUP (next session): (1) check logs/panes; if model_vsm.json exists in both dirs → (2) uv run python
>   opcodes/sweep.py --restack-only (folds both into the universal tree; S3 null gates decide if 1-bit
>   registers even COUNT — gate failure itself = result, cf. pythia-2.8b by fire). (3) Ladder analysis vs FP
>   parent tree (results/opcode-trace/qwen3-6-27b/): per-vertex Gram fidelity FP→ternary→1bit, null-gated.
>   PRE-REGISTERED: (a) selective K degradation at 1-bit (K needs the 0 state); (b) does per-layer vertex
>   degradation concentrate in the deep-middle band (s267 RDM 50%-dip)? (c) JAMMED-ABSTENTION hypothesis:
>   if K degrades selectively while confident topology is immutable (s268c) → K's collapse = abstention
>   channel jammed at inference exactly as at training — one vertex, one vacuum state, two timescales.
>   Note: fla fast-path warning in logs is the known slow-path fallback for the hybrid (parent ran same).
>   Runtime expectation: tens of min to ~hour per model, GPU shared. Tasks 1-2 of 3 done; task 3 = analysis.)
>
> Prior session: 267 (BONSAI PHASE-0 begun. (1) ✅ MEASURED: lambda compiler SURVIVES
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
> ★ NEXT (open, Michael's call): (0) PHASE-0 — behavioral parity DONE + Gram survival DONE (s267) +
>   ternary/1bit opcode ladder DONE (s269, null-gated: crystal survives 1-bit, selective-K REFUTED,
>   deep-middle trend ungated — see ★★★ s269). Remaining phase-0: 4-bit rung only (AWQ on HF), or skip by
>   ruling. Then phase 1
>   (tiny seeded student) with the Gram-derived STATIC bridge prior (peak mid-stack) + the pre-registered
>   flip-flop triangulation. RULINGS PENDING
>   (Michael): bridge mechanism (a/b/c, (a) favored by s260/s261); dynamic bridge allocation in phase 1 vs
>   static-first; probe-library growth gated as phase-1 prerequisite? IOUs before code: requential repo
>   license (Bonsai QAT-vs-PTQ RESOLVED s268 by weight forensics: absmean init + trained blocks; residual:
>   QAT-on-grid vs FP-drift→RTN not separable from weights alone). Phase-1 harness prereqs: lambda kernel + GBNF in loop, probe
>   split frozen, streaming-centroid buffers, telemetry writer ⊥ loss module.
>   Also open from arc 1: (A) QK-PATTERN register → decisive B/C test (s264 F4). (B) visualizer + extract
>   opcodes/ to MIT repo. (C) retro-check s264 27B floor run (n_perm/pooling). (D) Pythia proxy-degradation.
>   Prior-arc: s263 Jacobian SVD; v15.1; INDEX regen. Env: torch 2.11 + MPS, 512GB RAM; models HF-cached.

─────────────────────────────────────────────────────────────────────────────────────────────────────

## Recent arc (index — full detail: `chats/session-NNN.md` + linked knowledge; history: `git log -p`)

- **s269** OPCODE LADDER (current session, full detail in header ★★★ s269). Crystal survives 1-bit
  (fid 0.987, z=5.3); selective-K refuted in both registers; 11-model tree root gc 0.985; opcodes/ladder.py
  new instrument; commit 7576c54.
- **s268** BONSAI FORENSICS (see header blocks). Recipe reverse-engineered from weights; QAT-vs-PTQ
  IOU resolved; drift ordering = routing⊥value 3rd register; 50%-dip ≠ differential rewiring; sign flips
  tunnel through zero (transition matrix) → optimizer constraints C1–C6 + phase-1 design budgets; 1-bit
  rung forensics pre-registered + in flight (tmux main:1/main:2).
  → `explore/bonsai-ternarization-forensics.md` + memories bonsai-recipe-reverse-engineered,
  bonsai-sign-flips-tunnel-through-zero.
- **s267** BONSAI PHASE-0 (see header of prior update). Compiler survives ternarization (behavioral parity,
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
