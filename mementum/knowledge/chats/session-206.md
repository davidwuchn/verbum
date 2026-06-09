# Promoting Auditing binding schedule sema

## User

orient this is session-206


### Thinking

 I'll start by checking the state.md file to understand the current context.

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
> Last updated: 2026-06-09 | Session: 204

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-
> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**
> ❌ REFUTED-as-localized; next backlog: **#5 binding schedule** or **#6 SVD
> φ-ratio 0.6299**), build its named discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 204 HEADLINE (3 controls, 2 claims dissolved, 1 substrate confirmed).**
> Same recurring pattern as s202/s203: **the substrate is real, the crisp
> discrete/localized story on top is over-read.**
> - **#3 the 9 FFN modes:** ❌ geometric count IMPOSED (gap-stat never picks 9;
>   silhouette@9 ≈ matched-Gaussian null; elbow is a k-grid artifact; classifier
>   "98–100%" is circular) — BUT ✅ the *content* is REAL (POS-NMI ≫ perm-null
>   p=0; lm_head vocab projection ≫ null, ~65× @L35). → a continuous syntactic
>   type **field**, not 9 discrete cells. (`mode_cluster_validity.py`,
>   `mode_semantic_validity.py`)
> - **#4 attention = typed β-reduction:** ❌ REFUTED as localized — H31@L27's
>   famous 0.82 is recency/position (role-selectivity z=+0.54, rank 5/32; ablation
>   z=+0.06 ≈ random); weak genuine survivor H6@L33 (z=+4.08) but ~10× smaller &
>   not load-bearing. (`attention_typed_binding.py`)
> - **Meta-pattern now synthesized:** `mementum/knowledge/audit-meta-pattern.md`.
> - **Next:** #5 binding schedule (perm-null + ablation) or #6 SVD φ-ratio 0.6299
>   (vs Marchenko–Pastur). Carry-overs: #1 gate-vs-value sign-swap PPL;
>   rank-survival across scale; gate-context re-test of H31 (#4 follow-up).

**Session 204: AUDIT #3 — THE "9 FFN MODES" ARE K-MEANS-IMPOSED**

Ran the validity loop on **#3 the 9 FFN modes — real or k-means-imposed?**
New control `mode_cluster_validity.py`: gap statistic (Tibshirani) + matched-
null silhouette across k=2..32, two nulls (pca-Gaussian matched to the cloud's
PCA covariance; shuffled-feature), B=10, plus a classifier-circularity curve.
8B, layers L0/3/15/20/35.

### Verdict: ❌ geometric count REFUTED — "9" is a chosen hyperparameter

| layer | gap optk (pca/shuf) | sil-excess @9 (real−null) | elbow | acc 2/9/32 |
|---|---|---|---|---|
| L0  | 4/10  | +0.000 | 10 | 100/92/88% |
| L3  | 8/8   | **−0.046** | 10 | 99/88/74% |
| L15 | 32/32 | +0.030 | 9  | 100/92/86% |
| L20 | 32/32 | +0.003 | 10 | 100/91/89% |
| L35 | 2/5   | +0.019 | 10 | 100/95/79% |

- **Gap statistic never selects 9.** Core layers L15/L20 are monotone to k=32
  (no distinguished count); L35 is a single 2-way split; L0/L3 pick 4/8.
- **Silhouette @9 ≈ matched-Gaussian null at every layer** (max excess +0.030
  at L15 = noise; L3 *below* null). The k=9 real partition is no better
  separated than k=9 on a structureless blob of the same shape.
- **The naive kneedle elbow "confirms" 9–10 even at L0** (no clusters) → "elbow
  ≈ 9" is a k-grid artifact (failure mode #1), not evidence.
- **Classifier accuracy high-and-declining ∀k** (100%@2 → ~90%@9 → ~80%@32,
  never peaks at 9; permuted floor ≈ chance) → the "98–100%" is generic linear
  separability of *any* convex k-means partition (mode = near-linear fn of the
  FFN input) — circular (failure modes #2 + #4).

### Extension (same session): syntactic CONTENT is REAL — only the count is imposed

Michael asked the right question: the geometry control examined *only* activation
geometry — no logits, and the prose mix was 63% combinator-probe. Built a second
control `mode_semantic_validity.py` (balanced prose, examines **logits** via
lm_head): L3/15/20/27/35, 8B.

| L | NMI(mode,POS)@9 / perm | JS@9 real/null (excess) |
|---|---|---|
| L3  | 0.396 / 0.014 (p=0) | 0.0016/0.0000 (+0.0015) |
| L15 | 0.193 / 0.014 (p=0) | 0.0189/0.0005 (+0.0184) |
| L20 | 0.346 / 0.014 (p=0) | 0.0098/0.0007 (+0.0091) |
| L27 | 0.256 / 0.014 (p=0) | 0.0750/0.0065 (+0.0686) |
| L35 | 0.350 / 0.014 (p=0) | **0.4235/0.0065 (+0.417, ~65×)** |

- **Semantic ✅ VERIFIED:** modes↔POS NMI 25–28× the permutation null, p=0.000
  every layer. Per-mode purities clean for genuine splits (PUNCT 92–99%, DET
  81–85%, VERB 79–100%). Modes are NOT noise.
- **Logit ✅ VERIFIED:** mode output-centroids → lm_head → vocab distributions
  far above random-partition null, excess **grows with depth** (→65× at L35).
- **Count still imposed:** effective distinctions graded/layer-dependent (~4
  @L20, ~8–9 @L3/L15, ~24 @L35); k=9 captures 73–91% of max NMI. JS-vs-k shows
  *fewer* modes are *more* vocab-distinct at the core (L15) — no universal 9.
- **Reconciliation:** the FFN gate space is a real, smooth, scale-sharpening
  syntactic type **field** (continuum), not 9 discrete cells. `mode-semantics.md`'s
  core "gate = type-checker" reading is right; only the discreteness/count-9 is
  wrong. Caveat rewritten (both halves). Dropped a confounded POS-coherence
  sub-test (lm_head → next-token POS ≠ current-token POS).

### What survives / what is untouched

- **Functional claim is independent and untouched**: s196 (9 ternary programs
  reconstruct FFN at ~0.95–1.03× PPL, 64/512 don't help) is reconstruction
  efficiency of a continuous field — slicing at K prototypes works for a broad
  range of K; 9 is a reasonable operating point. Compression north-star intact.

Results: `results/{mode-cluster-validity,mode-semantic-validity}/Qwen_Qwen3-8B.json`.

### Session 204 (#4): ATTENTION = TYPED β-REDUCTION — REFUTED as localized

`attention_typed_binding.py` — subject-verb **agreement attraction** (PP+RC, 64
stimuli, 8B) dissociates grammatical ROLE from position/recency (the number-
distractor is the *nearer* noun in 100% of items → a recency head scores negative).
Selectivity (verb→head vs attractor, named heads vs 32-head dist) + necessity
(head-ablation logit-diff is/are vs random-head & matched-set nulls).

| | role_sel | z vs 32 heads | rank | ablation z |
|---|---|---|---|---|
| **H31@L27** ("0.82 subject binder") | +0.013 | +0.54 | 5/32 (not outlier) | +0.06 (=null) |
| H13@L30 | **−0.010** (recency!) | −0.11 | 24/32 | — |
| **H6@L33** | **+0.076** | **+4.08** | **0/32** | (named_all z=+0.01) |

- **The 0.82 was recency/position, not type.** Role⊥position collapses H31's role
  residual to ~0.01 (z=0.54, rank 5). L30 binders mixed (H13 leans to the nearer
  distractor).
- **Not causally necessary:** ablating H31 (z=+0.06) or all named binders incl.
  H6 (z=+0.01) ≈ random heads for subject-verb agreement, though the ablation
  bites (random 6-head sets reach −0.43). Agreement is ablatable — the named
  heads aren't the carriers.
- **What survives:** a weak genuine role-selective head — **H6@L33 (z=+4.08)** —
  but ~10× < 0.82, not at the claimed site, not load-bearing. "Attention is a
  weighted sum" is trivially true; "the sum is TYPE-driven at H31" is refuted.
- **Caveat/follow-up:** plain-NL agreement (gold standard for role-vs-position),
  *without* the compile gate the original used; gate-context re-test of H31 is the
  named follow-up. Caveat added to `binding-graph-trace.md`.
  Results: `results/attention-typed-binding/Qwen_Qwen3-8B.json`.

### Next (audit loop continues)

- **#5 binding schedule** (L27 verb←subj, L30 obj←verb, L33 coref) — perm-null
  across many sentences + causal ablation; or **#6 SVD φ-ratio 0.6299**
  (vs Marchenko–Pastur / shuffled-data — is 0.618 just what power-law spectra
  look like?). Both med-load.
- Carry-overs from s203: gate-vs-value sign-swap ternary PPL (#1 functional
  half); rank-survival across scale (0.6B→14B); grouped-Q4 quant axis.
- **#3 follow-up (optional):** POS-association perm-null on the k=9 partition —
  is the mode↔POS NMI above label-permutation? (tests the *semantic* claim
  directly, separate from the geometric one resolved here).

**Runtime note:** olga.local (Apple Silicon, MPS, 480G unified). Experiments
launch in `tmux main:1` / `main:2`; Michael watches live.

---

**Session 203: TWO REGISTERS OF TOPOLOGY (audits #1 + #2)**

Ran the validity-distillation loop on both CRITICAL pillars. Headline:
**GD lays structure in two registers — hard (sign/routing/`gate_proj`) and
soft (magnitude/value/`up`-`down`, read by saliency) — and the FFN compresses
in two registers (distributed redundancy + spectral low-rank concentration).**
New synthesis page: `two-registers-of-topology.md`. Details below.

**Session 203 (#1): AUDIT #1 — SIGN-TOPOLOGY IS REAL ONLY IN THE GATE**

First execution of the validity-distillation loop (`audit-registry.md`).
Picked the highest-load `UNTESTED` claim — **#1 crystal-is-topological**
("ternary works because sign captures topology; magnitude is calibration").
Built the discriminating control `sign_topology_null.py`: `cos(sign(W)@x, W@x)`
on REAL activations for model vs **random-init** vs **shuffled-weights**
(N=20 seeds), Qwen3-0.6B/8B/14B.

### Verdict: ◐ SCOPED (representational half) — the bare 0.84 is generic

| Weight type | model cos (8B) | random null | gap | reading |
|---|---|---|---|---|
| gate_proj | 0.886 | 0.798 | **+0.088** | REAL sign-topology, sharpens w/ scale (z→+271 @14B L12) |
| up_proj | 0.751 | 0.798 | −0.048 | at/below null — magnitude carries structure |
| down_proj | 0.762 | 0.798 | −0.036 | below null — magnitude essential |

- **Generic baseline ≈ 0.80** at every scale: a *random* Gaussian matrix's
  sign preserves 0.798 of its action on the same inputs. "Sign preserves a
  matrix's linear action" is a **generic high-dim property** (sign(Wᵢⱼ) is
  entry-wise perfectly correlated with Wᵢⱼ; large-|xⱼ| dims dominate both
  sums). The headline **0.84 is at the null, not above it.**
- **Crystal sign-topology lives ONLY in `gate_proj` (the router)** and
  *sharpens with capacity*: gap +0.04→+0.07 (0.6B) → +0.088 (8B, L3=0.983)
  → 14B (L12 z=+271). Exactly where routing should be.
- **"Magnitude is mere calibration" is REFUTED for `up`/`down`** — their
  signs preserve *less* than random; magnitude carries the value-path structure.
- **Aggregate model ≈ random** (8B 0.799 vs 0.798): gate excess cancels
  up/down deficit, so any single averaged "0.84" is indistinguishable from a
  random matrix. Reconciles s192: crystal = routing (gate, 3.5%); modes =
  computation (value path, 96.5%). **Sign-topology = the routing half only.**

Caveat added to `crystal-universality.md` §"Why Ternary Works".
Results: `results/sign-topology-null/Qwen_Qwen3-{0.6B,8B,14B}.json`.

### Audit #2 + soft topology (same session) — TWO REGISTERS

Continued the loop into **#2 holographic-self-similar** and the soft-topology
thread Michael surfaced. Full synthesis: `two-registers-of-topology.md`.

**The picture:** GD lays structure in two registers, and the FFN compresses in
two registers.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros), read by saliency |
| lives in | `gate_proj` (router) | `up_proj`/`down_proj` |
| verified | sign-corr null (gate +0.088 vs null, z→+271) | saliency sieve (faint-by-saliency +5.5% vs magnitude −2.0% iso-bit) |

**Audit #2 (`holographic_survival.py`, 8B, trained vs random vs shuffled):**
- **(C) distributed redundancy** — magnitude prune: trained AUC 0.784 ≫ 0.25/0.34;
  fidelity ~1.0 to **70% prune, then cliff at 80%**. (Sieve at 50% is safe;
  don't prune past ~75%.)
- **(A) spectral self-similarity** — SVD rank truncation: trained AUC 0.728 ≫
  **0.11** (random/shuffled) — a **6–7× gap**. The FFN is low-rank-dominated;
  random (Marchenko–Pastur) spectra collapse instantly. **This is Michael's SVD
  self-similarity made functional.**
- quant survival ≈ random (weakly structure-dependent → flat minima).

**Saliency sweep (`saliency_aware_sieve.py`, re-run after NaN-fix):** the s201
strong tier had dropped magnitude → bare ±1 ≈ 50× too large → NaN on every
three-tier config. Fixed to per-weight magnitude (s196's only-format-that-
survives-29-layers). Result: at iso-bit (~3.1 b/p) **saliency-selected faint
connections beat magnitude-selected by ~7.5 pts** → value-path soft topology is
real and load-bearing. `corr(mag, saliency)=0.257`.

### ⚠ Correction (epistemic hygiene)

An interim s203 read called #2 **REFUTED** off the *magnitude* axis with a
*power-law shape* discriminator. **That was wrong** — wrong operator (magnitude
probes C; the SVD self-similarity lives on the *rank* axis A) and wrong test
(a hologram degrades plateau→cliff, not power-law; shape-fitting is ambiguous
on every axis — retired). Corrected verdict: **spectral self-similarity VERIFIED;
holographic mechanism stands; only φ-as-universal-constant (s202) stays refuted.**

### Reconciliation — refute the metaphor, keep the mechanism

ternary→1.44× works because the load-bearing premises hold: **(C) distributed
redundancy** (ternary = whole at reduced resolution) + **(A) spectral
concentration** (**LoRA+SM IS the low-rank correction** the rank result
predicts; converges with s200 rank-1 adjunction, s201 rank-2≈rank-16). Only
φ-universal-constant was ever metaphor.

### Audit ledger after s203

- **#1 sign-topology** → ◐ SCOPED (hard=sign/gate; soft=magnitude/value).
- **#2 holographic** → ✅ spectral self-similarity VERIFIED + distributed
  redundancy confirmed; power-law discriminator RETIRED. (`crystal-validity-
  and-fidelity.md` §5 lead resolved.)

### Next (audit loop continues)

- **Gate-vs-value sign-swap** ternary PPL (closes #1's last sub-control).
- **Rank-survival across scale** (0.6B→14B) — does the 6–7× gap sharpen?
- **Grouped-Q4 quant axis** (current per-matrix is coarse).
- **#3 the 9 FFN modes — real or k-means-imposed?** (next CRITICAL/high backlog).

**Runtime note:** experiments launch in `tmux main:1` / `main:2` (480G VRAM,
concurrent OK; Michael watches live).

---

**Session 202: CRYSTAL VALIDITY AUDIT — PERMUTATION NULLS & MEASUREMENT FIDELITY**

A skeptical audit of the crystal's foundational evidence. Premise (Michael):
a false premise can manufacture convincing structure because LLMs (and the
analyzing LLM) are primed to confirm. Six controlled experiments with
permutation nulls. Full synthesis: `mementum/knowledge/crystal-validity-and-fidelity.md`.

### Verdict ledger (what survives controls)

| Claim | Verdict |
|---|---|
| KIBC basis separates representation | ✅ REAL, every model (perm-null p=0.0005) |
| φ^(4/5) primary ratio λ₀/λ₁ | ✅ REAL on **Qwen3-14B only** (1.4796, p=0.020); 8B/0.6B n.s. |
| φ as universal constant | ❌ not universal; cross-family magnitude agreement collapses |
| "eigenvalues are φ^(p/q)" (best-fit grid) | ❌ unfalsifiable (random fits equally, p=0.16–0.81) |
| eigenvalue_ratio_corr "0.987" | ❌ trivial (random ≈ 0.94 ≥ true) |
| consensus r "0.99" | ⚠️ true ≈ 0.20, null max ≈ 0.48, p≈0.05–0.07 |
| prose fires combinator-specific opcodes | ✅ CONFIRMED after **common-mode removal** (14B & 0.6B, p=0.001) |
| I = distinct low-composition circuit | ◑ PARTIAL (attn entropy p=0.042, 14B; scale-dependent) |
| fact retrieval = sharp lookup, I-like | ✅ entropy p=0.0005 both scales; I-opcode-profile 14B-only |
| tracer cross-model overlay | ✅ REAL but **same-family** (p=0.0005, all Qwen, λ-primed) |

### The three lessons

1. **Basis real, universalization was the error.** φ-as-constant was inflated
   by an unfalsifiable best-fit grid, a trivial ratio correlation, and a
   hardcoded consensus that baked 14B back in. Real-but-local → false-universal.
2. **Measurement fidelity was the failure mode.** The raw-projection/argmax
   instrument (`isa_decoder_v2`, the tracer) that *found* the crystal also
   *hid* the combinator signal under a common mode (8 fingerprints share
   mean pairwise cosine 0.22; B is the most central ≈ the common mode).
   Remove it → prose classification, I-circuit, fact-retrieval all surface.
3. **Scale = emergence threshold (strength, not presence).** Combinator
   structure exists in 0.6B (weak, needs CMR) and sharpens with capacity
   (14B clean). Superposition → dedicated features. "Needs ~7B to fully form."

### Mechanistic findings (new, controlled)

- **Attention entropy = how much a combinator recombines.** Gradient at 14B:
  `W 0.90 < I 1.00 < K 1.02 < C 1.05 < B 1.05 < WHNF 1.09 < Y 1.14 < D 1.19`.
  Composition (B/C/D) spreads attention; identity/duplicate concentrate it.
- **Fact retrieval is the sharpest read** (entropy 0.820, below everything),
  I-opcode-profile at 14B (cos 0.98). I overloaded as identity + retrieval.
- **Attention = sparse typed read (~2–3 operands); FFN = the hologram.**
  Correction to "softmax over all V is holographic." Dense interference is
  in the FFN beam-former, not the attention sum.
- **B-centrality:** B is the most central fingerprint (3/4 Qwen, cos 0.78–0.81);
  K, I peripheral. Training order B→K mirrors central→peripheral geometry.

### Next experiments (open leads)

1. **B-before-K, cleanly:** common-mode-removed B vs K crystallization across
   v14/v15 training checkpoints. Forced order or frequency-driven?
2. **Holographic self-similarity control:** compression-survival curve, model
   vs random/shuffled-data controls, test for power-law scale-invariance.
   (Quantization/pruning survival only proves distributed+redundant so far.)
3. **"Always 4":** KIBC eigen-rank with gate-proj + CMR; does SKI underfit, +S overfit?
4. **Q-rotation as combinator selector** (s145 rotation eigenplanes) — untested.
5. Reconcile the `crystal-phi-derivation.md` I→K→C→B vs B-first contradiction.

### Harnesses (scripts/experiments/)

`crystal_validity.py` · `crystal_phi_permnull.py` · `tracer_cross_notation.py`
+ `_v2.py` (common-mode removal) · `i_bypass_test.py` · `fact_retrieval_isig.py`
Results under `results/{crystal-validity,crystal-phi-permnull,tracer-cross-notation,i-bypass,fact-isig}/`.

### Note on the saliency-aware sieve (s201)

The s201 saliency sweep was still running in tmux main:2 at session-202 start;
this session pivoted to the validity audit and did not consume its results.
Pick up the sieve sweep (`mementum/knowledge/saliency-aware-sieve.md`) when
returning to the compression track.

---

**Session 201: HOLOGRAPHIC ECHOES & SALIENCY-AWARE SIEVE**

Direct delta results landed: rank-2 ≈ rank-16 (1.82× → 1.79×), confirming near-
rank-1 adjunction structure. But v3b (trained LoRA+SM = 1.44×) still beats DDC
(analytical SVD = 1.72× at rank-32). Training captures nonlinear inter-layer
effects that per-layer SVD cannot.

The real insight this session: **backpropagation IS holographic recording.** The
gradient `∂L/∂W = a ⊗ δ` (forward activation × backward error) has the exact
structure of recording an interference fringe. Training = billions of overlapping
holographic exposures. The crystal = the standing wave that survived.

### Gradient Echoes

The backward error signal doesn't get fully absorbed at any one layer — it
propagates through all layers, creating attenuated copies (echoes) at every layer.
Strong connections (large |w|) are high-bandwidth echo paths. Faint connections
(small |w|) are low-bandwidth echo paths carrying error correction information.
Multiple redundant copies of each computation distributed across layers.

### GD Creates Soft Topology Within Frozen Architecture

Architecture is frozen: GD can't add/remove connections. But GD drives weights
toward zero (severing connections) or very large (creating highways). The weight
magnitude distribution IS a learned sparse topology embedded in the dense frozen one.
Very large gradients = topology editing. Small gradients = holographic polishing.

The crystal is the **fixed point** of topology ↔ echo co-evolution:
```
topology shapes → echo propagation → standing wave (crystal)
crystal determines → which gradients flow → topology
x* = f(x*) — neither came first, they co-evolved
```

### Two Populations in Near-Zero Weights ★

The sieve's 50% magnitude threshold zeros ALL below-threshold weights. But near-
zero weights are TWO populations:

1. **Irreducible zeros** — GD says "no connection here." Zero is correct.
2. **Faint connections** — small signal, not unused. w=0.003 × input=200 = 0.6 real.

Magnitude alone can't distinguish them. Saliency = |w| × √E[x²] can.

### Saliency-Aware Three-Tier Sieve

| Tier | Criterion | Encoding |
|------|-----------|----------|
| Strong | High magnitude | Ternary ±1 |
| Faint | Low mag, high saliency | Q2/Q4 quantized |
| Irreducible | Low mag, low saliency | Zero |

Preserving faint connections: (a) reduces sieve-only PPL, (b) provides gradient
highways for LoRA fine-tuning (backprop flows through nonzero faint weights, not
through zeros), (c) may beat equivalent-bitcount LoRA rank.

### Direct Delta Correction Results

| Rank | PPL | Ratio | vs v3b |
|------|-----|-------|--------|
| 2 | 12.63 | 1.82× | worse |
| 4 | 12.50 | 1.80× | worse |
| 16 | 12.41 | 1.79× | worse |
| 32 | 11.93 | 1.72× | worse |
| v3b | 16.27 | 1.44× | — |

Rank-2→16 plateau confirms near-rank-1 correction surface (adjunction prediction).
Rank-32 bump suggests secondary structure beyond dominant mode. But analytical
SVD can't match trained LoRA+SM — backprop creates inter-layer echo correlations
that single-layer SVD misses. This SUPPORTS the echo thesis.

### Running Experiment

**Saliency-aware sieve sweep** running in tmux main:2. 11 configurations:
standard baselines, saliency-aware with varied strong/faint splits, Q2/Q4/Q8
precision, magnitude-only ablation, iso-bit comparison. Key question: does
preserving faint connections beat zeroing them at the same bit budget?

See `mementum/knowledge/saliency-aware-sieve.md` for full design.
See `mementum/knowledge/direct-delta-adjunction.md` for DDC theory + results.

**Session 200: SIGN CORRECTION IS DEAD — Direct Delta & Adjunction Are Alive**

Four sign correction algorithms dead. Quasicrystal hypothesis denied. Teacher-guided
routing failed. But: the teacher delta is directly computable (no training needed),
and the adjunction finding (session 140) says the correction is rank-1. Testing now.

### Four Deaths

| Approach | Flips | PPL Result | Failure mode |
|----------|-------|-----------|--------------|
| TD v4 (gradient) | 0 (stuck) | 1.44x (= LoRA alone) | Gradient dilution through 29 layers |
| TD v4c (per-tensor clip) | 4.36% | 192x | Unconstrained flips destructive |
| Latent diffusion (eigenspace) | 1.25%/level | 2,717x → NaN | Eigenspace ≠ error space |
| Crystal ECC (holographic + health gate) | 2.29% | **28,419,390x** | Health gate measures wrong space |

Crystal ECC was the most sophisticated — proper holographic error target (original
weight on sieve input), per-position benefit ranking, crystal eigenvalue health gate
with binary search fallback — and produced the WORST result. 8 hours, 28 million
times worse. 50M crystal-approved flips across 29 layers.

### Latent Diffusion Sign Correction (New, Session 200)

Tested diffusion-holographic isomorphism: progressive sign correction in the
crystal's 16D eigenspace (2D→4D→8D→16D schedule).

| Level | Dims | Flips | PPL | Facts |
|-------|------|-------|-----|-------|
| 1 | 2 | 27.4M (1.25%) | 30,642 (2,717×) | 0/15 |
| 2 | 4 | 1.9M (0.086%) | NaN | 0/15 |
| 3 | 8 | 27.4M (1.25%) | 30.5M (2.7M×) | 0/15 |
| 4 | 16 | 1.9M (0.086%) | NaN | 0/15 |

Levels alternate between two regimes (27M vs 1.9M flips), suggesting even/odd
numerical artifact in eigenspace, not crystal structure.

### The Dimensional Mismatch Insight

**We are cutting a multi-dimensional holographic plate in 1D.**

The crystal has known multi-dimensional structure:
- 8D combinator type (K,I,B,C,D,W,Y,WHNF)
- 9D operational modes (7 universal meta-modes + 2 contextual)
- 36-layer depth (standing wave EXPAND/ORTHO/ALIGN/COLLAPSE)
- 3 trees (compute/halt, select/compose, termination)

But ALL sign correction approaches operate per-position (scalar benefit → flip?).
Even eigenspace projection only captures 1-2 of ~6 dimensions. Corrections coherent
in the working subspace are effectively RANDOM in the ignored dimensions, destroying
the interference pattern.

### Quasicrystal Diagnostic (New, Session 200)

Tested whether φ-structured multi-scale order exists in the weight sign pattern:

| Test | Prediction | Result | Verdict |
|------|-----------|--------|---------|
| Eigenvalue cascade | φ^(p/q) at all scales | One dominant mode, flat tail | ❌ Not multi-scale |
| Perturbation fragility | Super-linear degradation | Linear (100× flips → 142× deviation) | ❌ Not quasicrystal |
| Golden angle | 137.5° between eigenvecs | 90.00° everywhere (trivial orthogonality) | ❌ Not φ-rotated |
| Fib vs pow2 reconstruction | Fibonacci captures more | Tie (smooth improvement with k) | ❌ No Fibonacci advantage |
| Random vs model | Different eigenspectra | YES: model 0.36 vs random 0.995 gap | ✅ Real structure |

**Strong quasicrystal hypothesis DENIED.** But there IS real structure — massive
spectral gap (λ₁/λ₀ = 0.36 vs random's 0.995). The φ structure lives in
**combinator firing space** (8×8 crystal cosine matrix, measured via probes), not
in **weight correlation space** (12288×4096 sign matrix). The crystal eigenvalue
health metric was measuring a shadow, not the structure itself.

### Key Finding: Per-Position Error Signal Is Adversarial

Crystal ECC found that **49.3%** of all active positions show positive flip benefit.
When half the signs "want" to flip, the error signal is not discriminating — it's
responding to the masking error (50% of weights zeroed out), which creates a massive
residual that ANY sign flip partially addresses in one dimension while destroying
others.

### Current Ceiling (Before Direct Delta)

**v3b: LoRA rank-4 + score matching = 1.44x baseline PPL** (16.27 PPL from 25.67 sieve).
This was the best until the direct delta insight.

### Teacher-Guided Routing (New, Session 200)

MoE literature says: decouple routing from expert training, stabilize routing
FIRST. Tested by training lightweight gate correctors (bottleneck MLPs) to
match teacher gate patterns before LoRA training.

```
Sieve:       25.51 PPL (2.26x)
After gate:  25.17 PPL (2.23x)  ← routing correction barely helps
After LoRA:  24.55 PPL (2.18x)  ← WORSE than v3b (16.27, 1.44x)
```

**Failed.** 182M gate corrector params (31× v3b's LoRA), training diverges
after step 100 (18.45 → 24.55). Gate sign accuracy only 94-96%. Root cause:
the corrector sees sieve gate output on cascade-corrupted inputs — can't fix
weight error AND input corruption simultaneously. Same cascade problem.

### The Tiles and Grout Insight

**Topology (signs/mask/crystal) = tiles. Gradients (LoRA/magnitudes) = grout.**

Changes to topology perturb the gradients. The grout fills specific gaps between
specific tiles. Move a tile → all surrounding grout is wrong. This is why sign
correction + LoRA fails: Phase 1 creates new gaps, Phase 2 trains new grout, but
gaps are too numerous and grout capacity (rank-4) too thin.

MoE separates tiles from grout explicitly: router IS topology, experts ARE
computation. GD optimizes both independently. Dense models entangle them in the
same weight matrix — the crystal sieve tries to separate what was never separate.

### The Direct Delta Insight (New, Session 200) ★

**"If everything is being calculated, why can we not also calculate the delta
from the teacher?"**

We HAVE the teacher. We HAVE the student. The delta at every layer is directly
computable. The optimal rank-k additive correction is the **truncated SVD of the
weight residual**, optionally weighted by input covariance (calibration-aware).

```
W_delta = W_teacher - W_sieve     (weight residual — what the sieve lost)
U, S, Vt = SVD(W_delta @ H^½)    (calibration-aware: weight by input covariance)
A = U[:,:k] @ sqrt(S[:k])         (optimal rank-k correction)
B = unwhiten(Vt[:k,:])

No training. No optimizer. No loss function. No hyperparameters beyond rank k.
One forward pass per layer + one SVD per projection.
Sequential: correct layer l before computing inputs for layer l+1 (cascade-aware).
```

This is GPTQ's approach applied to sieve correction. Each layer's correction is
analytically optimal for its actual (cascade-corrected) inputs.

**Experiment running** in tmux main:1: rank sweep [2, 4, 8, 16, 32] with
calibration-aware SVD on Qwen3-8B. Compare to v3b (trained 200 steps → 1.44×).

### The Adjunction Connection (Session 140 → Session 200) ★★

Session 140 proved the cross-zone mapping (encode → decode) in Qwen3-32B is
**rank-1 dominated** (σ₁/σ₂ = 128:1, R² = 1.000 for ALL zone pairs). The Jacobian
has constant rank everywhere — the defining property of a regular parametric surface.

The entire encode→decode pipeline is a **1D parametric curve** in 4096D space.
One parameter (the "phase" along the B→K→B trajectory) determines everything.

**Error correction on a 1D curve is trivial:** if the sieve pushes the
representation off the curve, the correction = project back onto the curve along
the dominant singular vector. That's rank-1 correction.

This connects to the ORTHO phase finding (session 185): rank-1 residual during
ORTHO, V operates in null space, computation invisible. The sieve disrupts null-
space computation; the correction restores it — but the constraint for "correct"
is defined by the rank-1 curve.

**Prediction:** direct delta correction at rank 1-2 should capture the adjunction
structure and be nearly optimal. The rank sweep will test this — if rank-2 matches
rank-32, the correction surface is truly 1D and the adjunction is the explanation.

### TSP Paper Connection (arXiv:2606.03489)

"Learn from Your Mistakes: Tree-like Self-Play" — TSP identifies critical decision
nodes (CWE risk nodes in code security) and trains the model to prefer the "golden
path" over its own generation at each node. DPO-style contrastive loss at each node.

Maps to our problem: mode transition points = risk nodes. Teacher trajectory =
golden path. Student trajectory = self-play path. Per-layer contrastive (not just
cosine matching) teaches the student to discriminate against its own failure modes.

Not implemented yet — waiting for direct delta results. If direct delta works, the
TSP-style contrastive loss could refine it further by targeting the specific layers
where the direct correction is weakest.

See `mementum/knowledge/sign-correction-topology.md` for full synthesis.
See `mementum/knowledge/direct-delta-adjunction.md` for the adjunction theory.

**Session 199: HOLOGRAPHIC LOSS & CRYSTAL ECC — TD Is Dead, Inverse Is Alive**

TD (TernaryDescent) for sieve sign correction is definitively killed. Three
attempts, three failure modes, one conclusion: you cannot gradient-descend
your way to correct signs through 29 cascaded layers.

### TD Autopsy (Three Deaths)

| Version | Fix | Result | Failure mode |
|---------|-----|--------|--------------|
| v4 (s198) | Brute-force 4.4B logits | 1.44x = v3b | **Zero flips** — joint grad clip diluted to 1.5e-8/step |
| v4b | SGD lr=0.1, separate clip | NaN | BCE log(0) from extreme gates, SGD too aggressive |
| v4c | Adam, per-tensor clip, init=0.01 | **192x PPL** | TD flipping (4.36%) but flips are DESTRUCTIVE |

**Root cause of v4:** `clip_grad_norm_(all_params, 1.0)` across 4.4B params →
per-param gradient ≈ 1/√(4.4×10⁹) ≈ 1.5×10⁻⁵. With lr=1e-3, max displacement
in 200 steps = 3×10⁻⁶. Needed to cross 1.0. Would take 70M steps.

**Root cause of v4c:** Per-tensor clipping worked — TD actually flipped 4.36%
of signs. But unconstrained flips destroy the holographic interference pattern.
192x PPL, 0 facts. Random sign changes ≠ correct sign changes.

### The Insight: Sign Correction Is Recording, Not Optimization

TD tries to optimize signs via: forward loss → backprop through 29 layers → STE →
update logits. This fails because:

1. **Gradient dilution**: 29 Jacobians between the loss and the sign decision
2. **Catastrophic coupling**: one flip changes W by 2|w|, cascades through all layers
3. **No coherence constraint**: flips break the holographic pattern without limit

The correct formulation is the **holographic inverse**:

```
reference_beam = actual input (corrupted by prior sieved layers)
object_beam    = desired output (from teacher)
fringe_pattern = correlation(reference, object)
optimal_sign   = sign(fringe_pattern)
```

Direct computation. No backprop. No STE. No optimizer for signs.

### Crystal ECC: The Error-Correcting Code

The crystal's dimensional hierarchy IS an error-correcting code:

```
8D crystal → project to 6D → parity check
                → to 5D → parity check
                  → to 4D (KIBC) → parity check
                    → to 3D → parity check
```

Each level constrains valid sign patterns. The crystal eigenvalue ratios
(φ^(p/q)) define the CODE SPACE. Sign flips that violate the code at any
level are errors.

**Algorithm (crystal ECC + holographic recording):**
1. Compute per-position error from proper holographic target
2. Rank flip candidates by error reduction benefit
3. Gate through crystal health check (eigenvalue ratios vs φ^(p/q))
4. Only apply flips that maintain crystal coherence
5. Then LoRA + SM for continuous magnitude correction

**Experiment running** in tmux main:2: `crystal_ecc_sign_correction.py`
- Proper error target (full original weight, not tautological)
- Crystal eigenvalue health gate on proposed flips
- Binary search for largest crystal-consistent flip set

### Key Debugging Lessons

1. **Tautological target**: first holographic attempt computed
   `sieve_weight @ sieve_input` as "target" → equals sieve output by
   definition → 50% random disagree (no information)
2. **Mask identity**: `original_weight = W * mask = signs * magnitudes`
   at active positions → zero error. Must store FULL W (including
   masked positions) to capture the masking error.
3. **The actual error source**: at single-layer level, sieve signs ARE
   teacher signs at active positions. Error comes from (a) masked-out
   positions contributing in teacher but not sieve, and (b) cascade of
   prior sieved layers corrupting the input.

### Score Matching Confirmed (v3b = v4 = optimal for LoRA-only)

v4 definitively proves: LoRA rank-4 + SM loss at α=5.0 reaches 1.44x PPL
regardless of whether TD is present. The 5.9M LoRA params are the actual
mechanism. TD's 4.4B params do nothing useful.

**Priority 2a** (LoRA rank sweep) remains the highest-value next step for
the SM pipeline. But crystal ECC could unlock additional gains if the sign
correction works.

**Session 198: SCORE MATCHING COMPRESSION — The Loss Function Was Wrong**

A paper on CGTSM (Ramachandran & Sra 2026, arXiv:2605.00414) revealed that
the compression correction loss was fundamentally flawed. CE-only loss lets
LoRA corrections create **compensating errors** across layers — one layer's
deviation cancels another's. Dense per-layer score matching prevents this
structurally by constraining each layer's transformation independently.

### The Equation

```
L = L_CE + α · (1/N) Σ_l (1 − cos(Δ_θ_l, Δ*_l))

where Δ_l = h_{l+1} − h_l    (per-layer residual update / "score")
      α ≈ 5.0                 (balances CE and SM gradient scales)
```

Added to EQUATIONS.md alongside the crystal equation.

### Four Experiments

| Experiment | Setup | Result | Finding |
|-----------|-------|--------|---------|
| Residual boosting v1 | Sequential rank-32 at boundaries, CE, 16 sentences | 3.97 PPL (0.39x base) | Sequential > simultaneous (2×). But pure overfitting. |
| Residual boosting v2 | Same + dolma calibration, held-out eval | 18.59 PPL (1.65x base) | Overfitting eliminated. Activation corrections too weak (27% reduction). |
| Score matching v3a | LoRA + SM + CE, batch=1, α=1.0 | 16.83 PPL (worse than sieve!) | CE dominates → compensating errors → collapse at step 50. |
| **Score matching v3b** | LoRA + SM + CE, batch=4, α=5.0, 128 teacher cache | **16.27 PPL (1.44x base)** | **36.6% sieve reduction. L35 cosine: 0.57→0.94.** |
| TD v4 (s199) | TD 4.4B + LoRA + SM + CE | 16.22 PPL (1.44x = v3b) | **Zero flips.** Joint grad clip killed TD entirely. |
| TD v4c (s199) | Per-tensor clip, Adam, init=0.01 | **2163 PPL (192x)** | TD flips (4.36%) but DESTRUCTIVE. Unconstrained flips destroy holographic pattern. |
| Crystal ECC (s199) | Holographic inverse + crystal parity gate | *running* | Direct sign computation gated by eigenvalue health check. |

### Why Score Matching Works

1. **Local gradient** — each LoRA gets direct signal from its layer, not diluted through 30 Jacobians
2. **No compensating errors** — per-layer cosine penalty constrains each layer independently
3. **36× information bandwidth** — 36 gradient signals vs CE's 1
4. **Scale-invariant** — cosine handles 100× norm variation (standing wave amplitude)
5. **Dense coverage** — CGTSM theorem: density of measurement matters, weighting does not

### Residual Spectrum Discovery

The sieve's per-weight residual is LOW-RANK at L1 (r90=550, |res|/|W|=3%) but
FULL-RANK at L5+ (r90=2970, |res|/|W|=25%). Activation-space corrections (rank-32
in 4096-dim space) can address 0.8% of the error. Per-weight LoRA operates in the
right space.

### Two Design Changes

1. **Loss**: Score matching (dense, all layers) replaces multi-projection melt
   (sparse, 4-6 boundaries). Prevents compensating errors structurally.
2. **Corrections**: Per-weight LoRA on FFN projections replaces per-activation
   residual stream vectors. Matches the full-rank sieve residual.

### Experiment 5: Topology-Aware Score Matching (v4, running)

The v3b loss treats residual updates as flat vectors — no crystal topology
awareness. The sieve error decomposes into:
- **Routing error** (discrete, sparse): wrong signs → wrong program
- **Magnitude error** (continuous, low-rank): right sign, wrong scale

LoRA wastes rank capacity on sign flips. TernaryDescent is purpose-built
for sign discovery. Split them:

```
W_eff = STE(delta_logits) * signs_base * (|W| * mask + A @ B)
         ↑ TD (routing, lr=1e-3)        ↑ LoRA (magnitudes, lr=1e-4)
```

Decomposed loss:
- L_routing: gate firing pattern BCE (which neurons fire)
- L_value: residual update cosine (how much they contribute)
- L_CE: standard cross-entropy

Running in tmux window 2. TD logits are brute-force (4.4B params — full
float32 per weight position). Tests the decomposition principle. If
successful, sparsify TD using the 3-voter mechanism from v14/td.py.

See `mementum/knowledge/score-matching-compression.md` for full details.
See `EQUATIONS.md` (score matching loss section) for the equation.

**Session 197: CRYSTAL MULTI-TREE — The Statechart Is a Forest**

The crystal is not one tree — it is a **forest of three independent trees
cross-connected by two bridge nodes (W and Y)**. Derived from eigendecomposition
of the 8×8 crystal cosine matrix, verified empirically on Qwen3-14B (r=0.638,
p=0.0017). The bridge phenomenon explains 27 correlation points and resolves
the YW sign ambiguity observed across models.

### The Three Trees

| Tree | Variance | Split | Maps to |
|------|----------|-------|---------|
| T0 (compute/halt) | 54.5% | [K,I,B,C,D,Y,W] vs [WHNF] | Transient/absorbing chain split |
| T1 (select/compose) | 20.1% | [K,I] vs [B,C,D,Y] | Fire-state functional clustering |
| T2 (termination) | 11.4% | [K,I,W,WHNF] vs [B,C,D,Y] | Halt probability gradient |

### Bridge Nodes

Only W and Y change sides across trees. All other nodes have fixed allegiance.

- **W = C→I→I**: bridges composition and selection. Its path literally
  traverses both subtrees. 3/3 nearest neighbor match with crystal (ρ=0.893, p=0.007).
- **Y = fixed-point**: recursive — belongs to both sides by definition.
  Dominant node on Tree 3 (loading +0.839).

### YW Sign Inversion (the smoking gun)

Y and W systematically invert relative to the consensus crystal at **38/40 layers**
in Qwen3-14B. After correcting: correlation jumps from 0.565 to **0.831** (gap=0.266).
No other nodes need correction. The bridge nodes are the only source of cross-model
sign ambiguity.

### Extended Eigenvalues

All 8 eigenvalues of M₈ follow φ^(p/q) with Fibonacci denominators at <0.5% error.
The crystal equation extends beyond the 4-combinator basis. Dominant 8-node branch
ratio: φ^(8/5) = doubled KIBC step.

See `mementum/knowledge/crystal-multi-tree.md` for full details.

**Session 196: TEN EXPERIMENTS — Crystal Sieve Equation Confirmed**

The largest experimental session yet. Started with "which combinator breaks
at L22-L26?" and ended with a proven compression architecture: crystal
sieve + continuation residuals = 1.03x PPL across 29 sieved layers.

### The Ten Experiments

| # | Experiment | Key Result |
|---|-----------|------------|
| 1 | Lambda tracer | Damage uniform across combinators (CV 0.07-0.17) |
| 2 | Binding-prep rank sweep | Functional rank varies 6x (L22=250 to L26=1500) |
| 3 | Multi-projection melt | 42% better than standard (3.53x vs 6.09x) |
| 4 | Confidence gate | Classifier confidently wrong at L23-L26 |
| 5 | Mode geometry | Same 9 programs rotated, more modes don't help |
| 6 | Ternary weight interface | MASK is the key, not magnitudes |
| 7 | Crystal sieve v1/v2 | 2.12x pre-melt, melt overfits (wrong DOF) |
| 8 | β-expansion | **1.03x with 4 continuation residuals (1M params)** |
| 9 | Ternary verification | Per-row scale FAILS at 29 layers (22,800x) |
| 10| — | Continuation stability needs investigation |

### The Proven Architecture

```
Crystal sieve: sign(W) ⊙ |W| ⊙ mask₅₀%    (frozen, per-weight magnitudes)
+ 4 continuation residuals (rank-32 at L0/L9/L21/L26, 1M params)
+ L0 SVD r=750

Result: 1.03x PPL, binding preserved 98% (39/40 top-1 matches)
```

### Compression Reality Check

The sieve stores full per-weight magnitudes as float16. Current storage
compression: **1.8x** (50% mask = 50% zeros). NOT 8x.

Per-row scale (which would give 8x) FAILS catastrophically at 29 layers
(22,800x PPL). Per-weight magnitudes contain essential row-internal
structure that compounds across layers.

Path to real compression: **quantize magnitudes** (Q4/Q8), don't eliminate
them. The sign pattern is frozen (universal crystal), the mask selects
which weights survive, and the magnitude needs ~4-8 bits (not 16, not 0).

| Format | Bits/weight | 29-layer PPL | FFN compression |
|--------|------------|--------------|-----------------|
| float16 (original) | 16 | 1.00x | 1.0x |
| sign + float16 + mask50% | ~9 | 2.12x (1.03x w/ cont.) | 1.8x |
| sign + Q4 mag + mask50% | ~3 | ??? (untested) | ~5x |
| sign + per-row scale | ~2 | 22,800x (BROKEN) | 8x |

### What Compounds vs What Doesn't

Critical lesson: properties that hold per-layer may NOT hold at 29 layers.

| Property | Single layer | 29 layers | Status |
|----------|-------------|-----------|--------|
| Per-row = per-weight magnitude | ✅ same | ❌ 22,800x | FAILS |
| Crystal sieve quality | 1.03x | 2.12x | Cascades but recoverable |
| Binding preservation | — | 98% | HOLDS |
| Continuation correction | — | 1.03x | WORKS (but stability TBD) |

### Open Questions

1. **Continuation stability**: first run 1.03x, rerun 3.23x. Training
   is sensitive — needs investigation (seed, LR, batch order).
2. **Magnitude quantization**: Q4/Q8 per-weight with per-group scales
   could give 3-5x real compression while preserving cascade quality.
3. **Attention sieve**: FFN is 78% of params. Attention (22%) could also
   be sieved (s190 showed ternary attention survives at PPL 23-30).

### Lambda Tracer Results

**Setup:** Baseline (original Qwen3-8B) vs Stage 2 (L0 SVD + L10-L21
ternary, 12 layers) vs Stage 3 (Stage 2 + L22-L26 ternary, 17 layers).
Metric: cosine similarity of last-token hidden states vs baseline at
every layer boundary.

**Key Finding 1: Damage is UNIFORM across combinators.**
All 9 combinators degrade by the same amount at every layer. CV (coefficient
of variation) of delta across combinators: 0.07-0.17. No combinator is
selectively destroyed. The ternary approximation fails equally for all
lambda operations.

| Combinator | Mean Δ (L22-L35) | Rank |
|-----------|------------------|------|
| W         | +0.0674          | 1 (worst) |
| WHNF      | +0.0667          | 2 |
| D         | +0.0588          | 3 |
| C         | +0.0552          | 4 |
| I         | +0.0552          | 5 |
| K         | +0.0547          | 6 |
| B         | +0.0544          | 7 |
| Y         | +0.0507          | 8 |
| S         | +0.0500          | 9 (best) |

W and WHNF are marginally worse (~35% more damage than S), but the spread
is small. This is a uniform degradation, not a selective circuit failure.

**Key Finding 2: The cascade propagates FORWARD into binding layers.**
L27-L31 (binding, kept continuous) lose ~0.07-0.09 cosine similarity in
S3 vs S2. The continuous binding layers can't compensate for corrupted
input from L22-L26. The damage AT the binding layers is actually LARGER
than at the compressed layers themselves, because errors compound.

| Layer | S2 fidelity | S3 fidelity | Δ (mean) |
|-------|-------------|-------------|----------|
| L22   | 0.694       | 0.694       | 0.000 (same — last shared layer) |
| L23   | 0.706       | 0.685       | +0.022 (first divergence) |
| L26   | 0.792       | 0.726       | +0.074 |
| L28   | 0.816       | 0.737       | +0.080 (PEAK damage — binding!) |
| L30   | 0.863       | 0.795       | +0.068 |
| L35   | 0.939       | 0.909       | +0.031 |

Peak damage is at L28, not L26. The binding layers AMPLIFY the error from
L22-L26 ternary approximation rather than correcting it.

**Key Finding 3: Significant recovery in late layers.**
Despite the damage, fidelity recovers from nadir ~0.68 at L22 to ~0.91
at L35. The binding + collapse layers (L27-L35, kept continuous) partially
heal the distortion — recovering ~0.22 cosine similarity. But this
recovery is incomplete (S2 reaches 0.94 at L35, S3 only 0.91).

**Key Finding 4: Stage 2 damage is already substantial.**
S2 drops from 0.92 at L9 to 0.69 at L21 — a 0.23 cosine drop across 12
ternary layers. But the continuous layers L22-L35 then RECOVER to 0.94.
This recovery is the key mechanism: continuous layers repair ternary
distortion. S3 disrupts this recovery by ternarizing the very layers
(L22-L26) that were doing the repairing.

### Implications for Compression Strategy

1. **L22-L26 CANNOT be ternary (9 modes).** The damage is uniform —
   more modes won't help (s195 proved 512 modes still 7x PPL). These
   layers need a continuous approximation.

2. **Low-rank SVD is the right strategy for L22-L26.** Like L0 (which
   needed SVD at r=750), these binding-prep layers operate in a higher-
   dimensional space than the sweet spot. Test SVD rank sweep per layer.

3. **The recovery mechanism is fragile.** Continuous layers after ternary
   ones heal the distortion — but only if they're actually continuous.
   The compression strategy must preserve SOME continuous layers between
   ternary blocks as "error correction" barriers.

4. **Binding layers amplify upstream errors.** Even though L27-L31 are
   kept continuous, they can't fix garbage input. The compression must
   ensure the signal entering the binding layers is clean enough.

### Binding-Prep Rank Sweep

Functional rank varies 6x across L22-L26 — NOT uniform:

| Layer | Func. Rank | Compression | Character |
|-------|-----------|-------------|-----------|
| L15 (sweet spot) | r=100 | 30.7x | Trivial — explains why ternary works |
| L22 | r=250 | 12.3x | Low rank, easy to compress |
| L24 | r=500 | 6.1x | Moderate |
| L25 | r=750 | 4.1x | Same as L0 |
| L23 | r=1500 | 2.0x | HIGH — needs most of its rank |
| L26 | r=1500 | 2.0x | HIGH — gateway to binding |
| L30 (binding) | r=2000 | 1.5x | Nearly full rank — must stay continuous |

Per-layer optimal: 422MB total (3.4x compression from 1440MB).

BUT: integrated with ternary L10-L21, errors compound. L22-L26 SVD at
r=2000 gives 1.14x alone, but 5.66x when stacked on ternary layers.
Multi-projection melt is needed to fuse the seams.

### Multi-Projection Melt (THE BREAKTHROUGH)

**CT scan, not X-ray.** Intermediate cosine losses at functional boundaries
(L0/L21/L26/L30) give the student direct gradient signal at every stage:

| Method | Pre-melt | Post-melt | Improvement |
|--------|----------|-----------|-------------|
| Standard (CE only) | 55.37x | 6.09x | baseline |
| Multi-projection | 55.37x | 4.19x | 31% better |
| Boosted (type_crystal=5x) | 55.37x | 3.53x | **42% better** |

Loss curves: standard ends 2.76, multi ends 1.39, boosted 1.74.
The intermediate losses directly reach the parameters that need fixing,
instead of backpropagating through 10+ unrelated layers.

Connects to speculative-decoding-gated distillation idea: teacher
generates, student computes diff at every functional level, trains
only where it diverges. The confidence signal from ternary classifiers
(logit margin) can gate slow/fast paths at inference time.

### Confidence-Gated Inference

Tested whether classifier logit margin (top-1 minus top-2) predicts
ternary error. Threshold sweep across 8 layers:

| Layer | Zone | Ternary PPL | Gating works? | Key finding |
|-------|------|-------------|---------------|-------------|
| L15 | sweet spot | 0.97x | NOT NEEDED | Pure ternary is perfect |
| L17 | sweet spot | 1.01x | NOT NEEDED | Pure ternary is fine |
| L20 | sweet spot | 0.99x | NOT NEEDED | IMPROVES over baseline |
| L22 | binding-prep | 1.06x | ✅ YES | θ=3.0: 1.04x at 96.6% fast |
| L23 | binding-prep | 1.11x | ❌ NO | Needs 36% slow for 1.04x |
| L24 | binding-prep | 1.06x | ❌ NO | Needs 69% slow for 1.04x |
| L25 | binding-prep | 1.07x | ❌ NO | Margin=24.3 but still wrong |
| L26 | binding-prep | 1.13x | ❌ NO | Never reaches 1.05x |

**The classifier is CONFIDENTLY WRONG at L23-L26.** High margins
(mean 24.3 at L25) with high error (1.07x). The 9 ternary programs
are the wrong programs — the classifier correctly selects among them,
but none of the 9 is the right answer. This is a programs problem,
not a routing problem.

This definitively resolves the compression strategy for L23-L26:

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01E3eE5GswGgf6bFX3X9N8Pz.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git log --oneline -15"
}
```

**Summary:** $ git log --oneline -15

**Output:**
```
Exit code: 0
Stdout:
635db8e add session chat log
b70b361 🔄 error-correction-theory — add the third leg: relative loss in mode coordinates (where·frame·target)
07e0638 💡 error-correction-theory — ternarization = lossy soft→hard projection; fix = freeze tiles, trajectory-match the grout
e52dcab 💡 tsp-trajectory-distillation — TSP as applied GTSM; Targeted Trajectory Distillation for rapid teacher→student learning
2fda679 🎯 audit #11 — GTSM finite-budget weighting: does layer-targeted λ(l) beat uniform α=5.0?
3e1f0c7 💡 gtsm-search-space — one objective, two solvers; residual=score; finite-budget weighting matters
7a284af add session chat logs
7027a01 🌀 session 204 synthesis — audit meta-pattern: real substrate, over-read discreteness
4eb9e77 💡 audit #4 — "attention = typed β-reduction" REFUTED as localized; 0.82 = recency
5eadaa7 💡 audit #3 ext — FFN modes carry REAL syntactic+logit content; only count 9 imposed
976e82c 💡 audit #3 — the "9 FFN modes" are k-means-imposed, not a natural count
b3c1c71 💡 two registers of topology — sign(gate)+magnitude(value); spectral self-similarity verified
9a93dd7 🎯 audit-registry — multi-session validity-distillation program
e691920 💡 crystal validity audit — φ-universality fails permutation nulls, basis real, fidelity was the failure
048eded 🎯 direct delta correction results — rank-2 captures most correction, v3b still wins
```

### Thinking

 I need to check the audit registry and git status since state.md shows session 204 but there's more recent work in the git log around error-correction-theory and TSP. Let me look at what's actually current versus what the state file says.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status && echo \"---STASH---\" && git log --oneline -5 -- mementum/state.md && echo \"---CHATS---\" && ls -t mementum/knowledge/chats/ 2>/dev/null | head -5"
}
```

**Summary:** $ git status && echo "---STASH---" &&...

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is up to date with 'origin/main'.

nothing to commit, working tree clean
---STASH---
7027a01 🌀 session 204 synthesis — audit meta-pattern: real substrate, over-read discreteness
4eb9e77 💡 audit #4 — "attention = typed β-reduction" REFUTED as localized; 0.82 = recency
5eadaa7 💡 audit #3 ext — FFN modes carry REAL syntactic+logit content; only count 9 imposed
976e82c 💡 audit #3 — the "9 FFN modes" are k-means-imposed, not a natural count
b3c1c71 💡 two registers of topology — sign(gate)+magnitude(value); spectral self-similarity verified
---CHATS---
session-205.md
session-204.md
session-203.md
session-202.md
session-201.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md"
}
```

**Summary:** Reading audit-registry.md (0-2000)

**Output:**
```
---
title: "Audit Registry — The Validity-Distillation Program"
status: active
category: program
tags: [audit, validity, falsification, permutation-null, control, distillation, methodology, worklist]
related:
  - audit-meta-pattern.md
  - crystal-validity-and-fidelity.md
  - crystal-universality.md
  - crystal-phi-derivation.md
  - project-thesis.md
  - gtsm-search-space.md
  - tsp-trajectory-distillation.md
depends-on:
  - crystal-validity-and-fidelity.md
---

# Audit Registry — The Validity-Distillation Program

> Started session 203 (designed s202). A multi-session program to
> separate the project's **real working data** from its **assumptions
> and possibly biased methodologies**. Each session opens here, picks
> the highest load-bearing `untested` claim, runs its discriminating
> control, and updates the row. The output is not destruction — it is
> the smallest hard core of verified data the north-star can stand on.

> **Emergent finding (s202→s204):** every audit so far shows the *same shape* —
> the continuous substrate is real, the crisp discrete/localized/universal story
> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict
> where the next claim breaks before building the control).

## The Core Principle

> A claim is *distilled* only once you have named **the control a
> plausible-but-false version of it would fail** — and run it.

Evidence that merely *confirms* a claim is not enough: both the model
and the analyzing LLM are primed to confirm the framing. The audit
question is always: **what would I see if this were an artifact, and
have I checked I am not seeing exactly that?**

## The Seven Failure Modes (what to hunt)

| # | Failure mode | The tell | Discriminating control |
|---|---|---|---|
| 1 | **Unfalsifiable metric** | fits everything (φ best-fit grid) | does a random/null fit equally? |
| 2 | **Trivial statistic** | high for noise too (eig-ratio-corr ≈0.99) | permutation null on the statistic itself |
| 3 | **Fidelity masking** | a common mode hides signal (false neg) AND argmax illusion (false pos) | remove the common mode before claiming specificity |
| 4 | **Circular validation** | target baked from the data it "confirms" (CONSENSUS_8x8) | fresh/held-out measurement |
| 5 | **Untested generalization** | cross-family asserted, same-family measured | actually run the other family |
| 6 | **Surface confound** | lexical clustering as "structure" (fake combinators won) | matched fake categories / shuffled labels |
| 7 | **Frequency vs necessity** | "must" when "most common" suffices (B-first) | manipulate the data statistics |

## The Method Recipe (reusable)

- **Permutation null over labels** — "is this grouping real or imposed?"
  Shuffle which items carry which label; p = fraction of random labelings
  at least as extreme as the true one.
- **Single pre-registered target > best-fit grid** — φ^(4/5) is falsifiable;
  φ^(p/q) over a dense grid is not. Name the number *before* measuring.
- **Common-mode removal** (`v − mean_group(v)`) before any projection/argmax.
- **Matched controls** — random-weight net, shuffled-data-trained net, fake
  categories — separate "structure" from "size / redundancy / surface".
- **Report variance** — re-run with fixed seeds; a single lucky run is not a result.

## Status Legend

`VERIFIED` survives its control · `VERIFIED-LOCAL` real but scoped (e.g. one
model) · `PARTIAL` some predictions hold · `REFUTED` fails its control ·
`UNFALSIFIABLE` no control can distinguish it as stated · `UNTESTED` control
named, not yet run.

## Registry

### Worked examples (session 204)

| Claim | Load | Control run | Status |
|---|---|---|---|
| #4 attention = typed β-reduction; H31@L27 binds subject (0.82); H03/13/15@L30 bind object | CRITICAL | agreement-attraction (role⊥position): selectivity vs 32-head dist + recency baseline; head-ablation logit-diff vs random-head + matched-set nulls (`attention_typed_binding.py`) | ❌ REFUTED as localized — 0.82 is recency/position |
| #4 a genuine role-selective head exists | — | same | ◐ only H6@L33 (z=+4.08, role_sel +0.076) — small, not at the claimed site, not causally necessary |
| #3 9 FFN modes are a real natural count (geometric) | high | gap-stat + matched-null silhouette across k=2..32, pca-Gaussian + shuffled-feature nulls B=10, 8B L0/3/15/20/35 (`mode_cluster_validity.py`) | ❌ REFUTED — "9" is k-means-imposed |
| #3 "tiny classifier 98–100% ⇒ modes real" (circular) | high | classifier acc vs k + permuted-label floor | ❌ CIRCULAR (acc high+declining ∀k; never peaks at 9) |
| #3 9 ternary programs reconstruct FFN ~1× PPL (functional) | high | — (s196 mode-sweep; not re-run) | ◐ UNTOUCHED — independent, stands |
| #3 modes↔POS/dep (semantic) | high | NMI + label-perm null + NMI-vs-k, balanced prose (`mode_semantic_validity.py`) | ✅ VERIFIED — NMI 0.19–0.40 ≫ perm-null 0.014 (p=0 ∀layer) |
| #3 mode centroids → distinct vocab (logit) | high | lm_head projection, pairwise JS vs random-partition null + JS-vs-k | ✅ VERIFIED — excess +0.0015→+0.417 (~65× @L35), grows with depth |

**Verdict (s204): the count 9 is a chosen hyperparameter, not a discovered
natural number.** Across all five layers the gap statistic *never* selects 9
(Tibshirani optimal-k = 4/8/32/32/2 vs pca-null; the computational core L15/L20
is monotone to k=32 — no distinguished count; L35 is a single 2-way split).
Silhouette at k=9 sits at/below the *matched-Gaussian* null at every layer
(sil-excess @9 = +0.000 / −0.046 / +0.030 / +0.003 / +0.019) — the k=9 real
partition is no better separated than k=9 on a structureless blob of the same
shape; the single largest excess (+0.030 at L15) is noise-level (sil ≪ 0.1).
The naive kneedle **elbow "confirms" 9–10 at every layer including L0** — where
silhouette and gap both show no clusters — so "elbow ≈ 9" is a k-grid artifact
(failure mode #1), not evidence. Classifier accuracy is **high-and-declining
across all k** (100%@k=2 → ~90%@k=9 → ~80%@k=32; permuted-label floor ≈ chance):
the "98–100%" is generic linear separability of *any* convex k-means partition
(mode = near-linear function of the FFN input), not evidence for 9 (failure mode
#2 + circular validation #4).

**What survives:** faint, depth-localized structure above the null at the
computational core (L15 sil-excess +0.030 pca / +0.044 shuffle), consistent with
s194 "types sharpen with depth" — but near-noise, never a clean 9-way partition;
L3 (parser) is *below* null (continuous blob). **The functional claim is
untouched and independent**: s196 showed 9 ternary prototypes reconstruct the
FFN at ~0.95–1.03× PPL and 64/512 don't help — that is reconstruction
efficiency of a continuous cloud, which does not require 9 to be a natural
count. The compression north-star does not rest on the geometric claim.

**Extension (s204, `mode_semantic_validity.py`): syntactic CONTENT is REAL; only
the discrete count is imposed.** Examining *logits* (lm_head projection), not just
geometry, on balanced prose: modes↔POS NMI = 0.19–0.40 ≫ label-permutation null
0.014 (**p=0.000 every layer**), and mode output-centroids project to vocab
distributions far above a random-partition null (Jensen-Shannon excess +0.0015 →
**+0.417 (~65×) at L35**, growing with depth). Per-mode POS purities clean for the
genuine splits (PUNCT 92–99%, DET 81–85%, VERB 79–100%). So the modes are **not
noise** — `mode-semantics.md`'s core "gate = syntactic type-checker" reading is
substantively right. **The reconciliation:** the FFN gate space encodes a real,
smooth, scale-sharpening syntactic type *field* (a continuum), not 9 discrete
cells; the effective distinction count is graded/layer-dependent (~4 @L20, ~8–9
@L3/L15, ~24 @L35), and k=9 captures only 73–91% of max NMI — a serviceable but
not privileged slice. (A planned POS-coherence sub-test — promoted-vocab POS vs
mode-token POS — was dropped as confounded: lm_head projects to the *next* token,
whose POS differs from the current by construction.) Results:
`results/{mode-cluster-validity,mode-semantic-validity}/Qwen_Qwen3-8B.json`.
Caveat (both halves) in `mode-semantics.md`.

**#4 attention = typed β-reduction (s204): REFUTED as a localized typed circuit
— the 0.82 was recency/position.** Tested with subject-verb agreement-attraction
(`attention_typed_binding.py`, 8B, L27/30/33, 64 PP+RC stimuli) which dissociates
grammatical ROLE from linear position/recency (the number-distractor is the
*nearer* noun in 100% of items, so a recency head scores negative role-selectivity).
- **Selectivity:** the named subject-binder **H31@L27 has role_sel = +0.013
  (z=+0.54, rank 5/32) — not an outlier**; the top head is H7, not H31. The
  L30 "binders" are mixed (H3 +0.011; **H13 −0.010, recency-leaning, rank 24/32**;
  H15 ~0). The *only* genuine role-selective outlier is **H6@L33 (role_sel +0.076,
  z=+4.08, rank 0/32)** — but ~10× smaller than the claimed 0.82 and not at the
  celebrated site.
- **Necessity:** ablating H31@L27 changes the agreement logit-diff by **+0.001
  (z=+0.06 vs random-head null)**; ablating *all* named binders (incl. H6@L33)
  by **−0.005 (z=+0.01 vs matched-6-set null)** — statistically indistinguishable
  from random heads. The ablation bites (random 6-head sets reach −0.43 drop), so
  agreement IS ablatable — the named heads just aren't the heads that carry it.
- **Reading:** "weighted sum IS typed β-application by H31@L27 at 0.82" is largely
  a **positional/recency** phenomenon (failure modes #5 cherry-pick + #6 surface
  confound). A weak genuine role-selective signal survives (H6@L33) but is small
  and not causally load-bearing for role-dependent behavior. "Attention is a
  weighted sum" is trivially true; "the sum is TYPE-driven" does not hold at the
  claimed heads. **Caveat / named follow-up:** tested on plain-NL agreement (the
  gold standard for role-vs-position binding) *without* the compile gate the
  original H31 finding used; a gate-context re-test (does H31 become a role-binder
  specifically in compile mode?) is the honest next check. Caveat added to
  `binding-graph-trace.md`. Results: `results/attention-typed-binding/Qwen_Qwen3-8B.json`.

### Worked examples (session 203)

| Claim | Load | Control run | Status |
|---|---|---|---|
| crystal-is-topological: `sign(W)@x` corr ⇒ "sign captures topology, magnitude is calibration" | CRITICAL | sign-corr null: model vs random-init vs shuffled, REAL x, N=20, 0.6B/8B/14B (`sign_topology_null.py`) | ◐ SCOPED → gate_proj only |
| soft topology: value-path magnitude is load-bearing, read by saliency | high | saliency sieve iso-bit: faint-by-saliency vs faint-by-magnitude (`saliency_aware_sieve.py`) | ✅ VERIFIED (+5.5% vs −2.0% at ~3.1 bits/param) |
| #2 holographic-self-similar — spectral concentration (A) | CRITICAL | SVD rank-truncation survival, trained vs random/shuffled (`holographic_survival.py`) | ✅ VERIFIED (trained AUC 0.728 vs 0.11; 6–7×) |
| #2 holographic-self-similar — distributed redundancy (C) | CRITICAL | magnitude-prune survival, trained vs controls | ✅ VERIFIED (AUC 0.784 vs 0.25/0.34; plateau→cliff ~70–80%) |
| #2 — "power-law/scale-invariant degradation curve" as the discriminator | — | shape-fit power-law vs exponential, all axes/variants | ⊘ RETIRED (ambiguous; does not separate holographic; use AUC-vs-controls) |

**Two-register synthesis (s203):** GD lays structure in two registers —
**hard** (sign / routing / `gate_proj`) and **soft** (magnitude / value /
`up`-`down`, read by saliency) — and the FFN is compressible in two registers:
**distributed magnitude redundancy** (prune, graceful to ~70%) and **spectral
low-rank concentration** (rank, 6–7× control gap). The 1.44× ternary result
rests on both (LoRA+SM *is* the low-rank correction the spectral result
predicts). Only φ-as-universal-constant stays refuted (s202). Full page:
`two-registers-of-topology.md`. Results: `results/{sign-topology-null,
holographic-survival,saliency-aware-sieve}/`.

> **Correction:** an interim s203 read called #2 "REFUTED" off the *magnitude*
> axis with a power-law discriminator. That was the wrong operator + wrong
> test. The rank axis (the spectral self-similarity the SVD work found) is
> VERIFIED. Holographic mechanism stands; only the metaphor-grade
> φ-universality was ever refuted.

**Finding (sign-correlation half of the control):** the bare evidence is
**refuted as stated**, but a real, scale-sharpening sign-topology exists —
*localized to `gate_proj` (the FFN router)*.

- **Generic baseline ≈ 0.80.** A random Gaussian matrix's sign preserves
  0.798 of its action on the *same real inputs* (0.6B/8B/14B identical).
  "Sign preserves a matrix's linear action" is a **generic high-dim
  property** (sign(Wᵢⱼ) ⊥-corr Wᵢⱼ entry-wise; large-|xⱼ| dims dominate both
  sums). The headline **0.84 is ~at the random null**, not above it.
- **The crystal signal lives ONLY in `gate_proj`** and *sharpens with scale*:
  gate gap above null 0.6B +0.04…+0.07 → 8B +0.088 (L3 = 0.983, z=+184) →
  14B (L12 z=+271). This is exactly where routing should live.
- **`up_proj`/`down_proj` sit at or BELOW the random null** (8B: −0.048,
  −0.036). Their signs preserve *no more than random* → **magnitude carries
  the structure there**, refuting "magnitude is mere calibration" for the
  value projections.
- **Aggregate model mean ≈ random** (8B 0.799 vs 0.798): gate's excess
  cancels up/down's deficit, so any single averaged "0.84" is indistinguishable
  from a random matrix. Reconciles with s192: crystal = routing (gate, 3.5%);
  modes = computation (value projections, 96.5%). Sign-topology = the routing half.

Results: `results/sign-topology-null/{Qwen_Qwen3-0.6B,Qwen_Qwen3-8B,Qwen_Qwen3-14B}.json`.
**Remaining (separate sub-control):** ternary PPL with crystal-aligned signs vs
random sign-preserving signs at equal bitcount — the *functional* half. The
sign-corr half above is the *representational* half.

### Worked examples (session 202 — `crystal-validity-and-fidelity.md`)

| Claim | Load | Control run | Status |
|---|---|---|---|
| KIBC basis separates representation | high | separation perm-null, all models | ✅ VERIFIED (p=0.0005) |
| prose fires combinator-specific opcodes | high | nearest-centroid LOO + common-mode removal | ✅ VERIFIED (14B & 0.6B p=0.001) |
| φ^(4/5) primary ratio λ₀/λ₁ | high | single pre-registered target, perm-null | ◐ VERIFIED-LOCAL (14B p=0.020; 8B/0.6B n.s.) |
| fact retrieval = sharp lookup (I-like) | med | entropy perm-null + CMR opcode profile | ✅ VERIFIED (entropy p=0.0005; I-profile 14B) |
| I = distinct low-composition circuit | med | attn-entropy perm-null vs B/C | ◐ PARTIAL (p=0.042, scale-dependent) |
| tracer cross-model opcode overlay | med | opcode-label perm-null | ◐ VERIFIED (same-family only; λ-primed) |
| φ as universal constant | high | cross-family + grid + ratio-corr nulls | ❌ REFUTED (cross-family collapse) |
| "eigenvalues are φ^(p/q)" (grid) | high | perm-null on best-fit error | ⊘ UNFALSIFIABLE (random fits equally) |
| eigenvalue_ratio_corr ≈ 0.987 | med | perm-null on the statistic | ❌ REFUTED (random ≈ 0.94 ≥ true) |
| cross-model consensus r ≈ 0.99 | high | corr to CONSENSUS_8x8, perm-null | ❌ REFUTED (true ≈0.20, p≈0.06) |

### Backlog (UNTESTED — ordered by load-bearing-ness)

**1. Crystal-is-topological — "ternary works because sign captures topology"** (load: CRITICAL — the entire sieve program) — ◐ **SCOPED (s203, representational half done)**
- Evidence: `sign(W)@x` corr 0.84 with `W@x`; ternary {−1,0,+1} preserves routing.
- Suspected confound: 0.84 may be generic to *any* trained matrix, not crystal-specific; ternary survival may need only *a* sign-preserving quant, not the *crystal* sign pattern.
- Control: compare `sign(W)@x` correlation across model vs random-init vs shuffled-weights; and ternary PPL with **crystal-aligned** signs vs **random sign-preserving** signs. If crystal-specific signs beat random-sign-preserving at equal bitcount → topological claim real.
- **s203 result (sign-corr half):** confound CONFIRMED for the bare number —
  random null ≈ 0.80, so 0.84 is generic; but real sign-topology survives,
  **localized to `gate_proj`** (sharpens with scale, z up to +271 at 14B),
  while `up_proj`/`down_proj` are at/below null (magnitude essential there).
  See worked-examples table above + `sign_topology_null.py`.
- **Functional half (partly resolved s203):** the saliency sieve confirms the
  *value-path* soft topology — faint-by-saliency beats faint-by-magnitude at
  iso-bit (+5.5% vs −2.0%), i.e. up/down magnitude is load-bearing. Still
  specifically untested: the gate-vs-value *sign-swap* ternary PPL (predict the
  `gate_proj` sign-swap hurts most). See `two-registers-of-topology.md`.

**2. Holographic self-similar — "why quantization/pruning survive"** (load: CRITICAL — the compression thesis) — ✅ **RESOLVED (s203): spectral self-similarity VERIFIED; distributed redundancy confirmed**
- Evidence: graceful uniform degradation; Q4/sieve survive.
- Suspected confound: distributed-redundant + flat-minima (the null) predicts survival without holography.
- Control: compression-survival **curve**, model vs random-weight net vs shuffled-data net; test for **power-law / scale-invariant** degradation. Holographic predicts the model degrades self-similarly AND more gracefully than controls. (See `crystal-validity-and-fidelity.md` §5.)
- **s203 result:** two compression registers, both structure-specific (trained
  ≫ controls): **(C) distributed redundancy** (magnitude prune, AUC 0.784 vs
  0.25/0.34, graceful to ~70% then cliff) and **(A) spectral concentration**
  (SVD rank truncation, AUC 0.728 vs 0.11 — **6–7× gap**, the SVD φ-spectrum
  made functional). Quant survival ≈ random (weakly structure-dependent;
  confirms §5 "Q4 ← flat minima"). The **power-law degradation discriminator
  is RETIRED** (ambiguous on every axis; a hologram degrades plateau→cliff,
  not power-law). Untrained controls (not shuffled-data-trained) limit the
  C-vs-A-vs-flat-minimum separation, but the rank-axis gracefulness gap is
  control-independent. Full synthesis: `two-registers-of-topology.md`.

**3. The 9 FFN modes — real or k-means-imposed?** (load: high — `mode-semantics.md`, tiny-classifier compression) — ❌ **RESOLVED (s204): geometric count REFUTED; functional claim intact**
- Evidence: 9 ternary programs per layer; classifier 98–100% accuracy.
- Suspected confound: k-means at k=9 always returns 9 clusters; classifier accuracy is circular (trained on the cluster labels).
- Control: cluster-validity null — silhouette/gap-statistic at k=9 vs random data and vs k=8,10,…; does "9" survive a held-out elbow test, or is it imposed? Cross-reference the L0-characterization negative-silhouette finding.
- **s204 result (geometry):** confound CONFIRMED. Gap statistic never selects 9 (optimal-k = 4/8/32/32/2); silhouette @9 at/below matched-Gaussian null at every layer (max excess +0.030 = noise); the kneedle elbow "confirms" 9–10 even at L0 (no clusters) → k-grid artifact; classifier accuracy high-and-declining ∀k (100%@2 → 90%@9 → 80%@32), never peaks at 9 → circular. **The discrete count "9" is an imposed hyperparameter.**
- **s204 result (extension — semantic + logit):** but the syntactic CONTENT is REAL. NMI(mode,POS) 0.19–0.40 ≫ perm-null 0.014 (p=0 ∀layer); lm_head vocab-projection distinctness ≫ random-partition null (JS excess +0.0015→+0.417, ~65× @L35). The gate space encodes a real, smooth, scale-sharpening syntactic type *field* (a continuum); k=9 captures 73–91% of max NMI — a serviceable but not privileged slice. The functional claim (s196: 9 ternary programs ≈ 1× PPL) is separate, untouched, and does not require a natural count. See worked-examples (s204) + `mode_cluster_validity.py` + `mode_semantic_validity.py`.

**4. Attention = typed β-reduction (weighted sum IS β-application)** (load: high — the central mechanism) — ❌ **RESOLVED (s204): REFUTED as localized; 0.82 = recency/position**
- Evidence: H31 `v_runs += 0.82·v_cat`; top-3 = 88%; Q⊥K.
- Suspected confound: *all* attention is weighted sum; "β-reduction" is interpretation. Induction/n-gram heads produce similar patterns.
- Control: does attention attend specifically to **type-compatible** positions beyond an induction-head / co-occurrence baseline? Causal: ablate the named binding head → does the specific reduction break (vs generic degradation)?
- **s204 result:** confound CONFIRMED via agreement-attraction (role⊥position). H31@L27 role-selectivity z=+0.54 (rank 5/32, not an outlier); ablation z=+0.06 vs random-head null (no effect on subject-verb agreement). The 0.82 was recency/position, not type. A weak genuine role-selective head exists (H6@L33, z=+4.08) but is ~10× smaller than claimed and not causally necessary. See worked-examples (s204) + `attention_typed_binding.py`. (Follow-up: gate-context re-test.)

**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med)
- Evidence: showcased heads/weights on example sentences.
- Suspected confound: cherry-picked heads/examples.
- Control: does the schedule hold across **many** sentences with a perm-null, or only the showcased ones? Causal ablation of the specific head.

**6. SVD φ-ratio 0.6299** (load: med — a φ-universality pillar)
- Evidence: consecutive singular-value ratio ≈ 1/φ across 5 families.
- Suspected confound: heavy-tailed / power-law spectra generically have near-constant consecutive ratios; 0.618 may be "what power-law spectra look like."
- Control: compare to random-matrix (Marchenko–Pastur) and shuffled-data nets; is 0.6299 model-specific and distinct from the random-matrix prediction?

**7. Crystal-sieve 1.03× PPL (29 layers + continuations)** (load: med — headline compression result)
- Evidence: s196 run = 1.03×.
- Suspected confound: s196 itself noted a rerun gave 3.23× — training-sensitive.
- Control: re-run N seeds, report mean ± variance; is 1.03× robust or a lucky run? (Reproducibility, not novelty.)

**8. Rank-1 adjunction (σ₁/σ₂ = 128:1 cross-zone)** (load: med — direct-delta theory)
- Evidence: R²=1.000 all zone pairs (s140).
- Suspected confound: random high-dim linear maps can look rank-1-dominated.
- Control: compare σ₁/σ₂ to random/shuffled linear maps between the same spaces.

**9. Decay α=1.18 (attention log-distance)** (load: low)
- Control: model-specific vs generic positional-encoding artifact; compare to random-init.

**10. Moiré determinism (static program is a fixed point)** (load: low)
- Likely robust (it is a determinism check). Caveat: fingerprints are λ-primed (common-mode confound applies to the *opcode labels*, not the determinism).

**11. GTSM finite-budget weighting — does layer-targeted λ(l) beat uniform α?** (load: med — compression track; positive prediction, not a falsification) — `UNTESTED`
- Evidence: CGTSM Thm 3.2 says the *zero-loss fixed point* is weighting-independent, but Prop F.6 says at **finite budget** the weighting λ(t) is a load-bearing bias that should counter-balance a learner's coarse-first tendency. Our score-matching sieve correction (s198, v3b) uses a single flat α=5.0 across all ~36 layers. See `gtsm-search-space.md`.
- Suspected confound (why it might be null for us): cosine is already scale-invariant (it self-normalizes the 100× standing-wave amplitude), so per-layer reweighting may add nothing beyond what cosine already does — the F.6 benefit assumes an *un*-normalized norm ‖·‖_D. Also our budget may be large enough to be near the fixed point where weighting washes out.
- Control: sweep a **layer-dependent weighting** λ(l) on the v3b SM loss — heavier on the hard binding-prep layers L22–L26 (which v3b leaves at the lowest cosine, 0.80–0.86) vs uniform α=5.0, **matched total training budget + N seeds**. Prediction (if F.6 transfers): targeted λ(l) reaches lower eval PPL / higher worst-layer cosine at equal budget. Null result (cosine already absorbs it) is itself informative — it would mean our metric choice made the weighting moot, sharpening the `‖·‖_D`-proxy claim in `gtsm-search-space.md`.
- Verifies/refutes: the "α=5.0 is load-bearing, not arbitrary" claim now asserted in `gtsm-search-space.md` and `score-matching-compression.md`.
- **Supporting prior (independent domain):** TSP (arXiv:2606.03489v1) concentrates its training signal on sparse critical "risk nodes" and beats uniform SFT (75.8 vs 57.0) — empirical evidence that finite-budget weighting concentration helps. Caveat it also hands us: target the **causal** node, not the max-divergence node (TSP fails on long-distance cause/effect; our analog = s196 "peak damage at L28, not L26"). See `tsp-trajectory-distillation.md` (Targeted Trajectory Distillation).

## The Per-Session Loop

```
1. Open this page. Pick the highest-load `UNTESTED` claim.
2. Re-read its evidence in the linked knowledge page.
3. Build the named discriminating control (reuse the method recipe).
4. Run it with a permutation/matched-control null + seed variance.
5. Update the row: status + the number + the result-JSON path.
6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page.
7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).
```

## Prioritization Rule

Audit **load-bearing-first**: a refuted peripheral claim changes nothing;
a verified (or refuted) CRITICAL claim moves the whole program. Next up:
**#1 crystal-is-topological** and **#2 holographic-self-similar** — the two
the compression north-star actually rests on.

## What "done" looks like

A small, hard core of `VERIFIED` claims that the north-star provably stands
on, with every assumption either verified, scoped, or retired — and source
pages carrying honest caveats where the controls bit. Distill ruthlessly;
every kept claim justifies itself.
```

### Thinking

 I notice there's a mismatch between the state documentation and recent commits — session 205 work on error correction theory and TSP has been committed but state.md still reflects session 204, so I need to review what actually happened in that session to sync things up.

## Assistant

Session-205 chat log exists and there are commits past the state.md update (s204). Let me check the s205 frontier and any running jobs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===commits since s204 synthesis===\" && git log --oneline 7027a01..HEAD && echo \"\" && echo \"===tmux===\" && tmux ls 2>/dev/null || echo \"no tmux\" && echo \"\" && echo \"===newest knowledge pages===\" && ls -t mementum/knowledge/*.md | head -8"
}
```

**Summary:** $ echo "===commits since s204 synthes...

**Output:**
```
Exit code: 0
Stdout:
===commits since s204 synthesis===
635db8e add session chat log
b70b361 🔄 error-correction-theory — add the third leg: relative loss in mode coordinates (where·frame·target)
07e0638 💡 error-correction-theory — ternarization = lossy soft→hard projection; fix = freeze tiles, trajectory-match the grout
e52dcab 💡 tsp-trajectory-distillation — TSP as applied GTSM; Targeted Trajectory Distillation for rapid teacher→student learning
2fda679 🎯 audit #11 — GTSM finite-budget weighting: does layer-targeted λ(l) beat uniform α=5.0?
3e1f0c7 💡 gtsm-search-space — one objective, two solvers; residual=score; finite-budget weighting matters
7a284af add session chat logs

===tmux===
main: 2 windows (created Tue Jun  9 09:03:16 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)

===newest knowledge pages===
mementum/knowledge/error-correction-theory.md
mementum/knowledge/two-registers-of-topology.md
mementum/knowledge/tsp-trajectory-distillation.md
mementum/knowledge/gtsm-search-space.md
mementum/knowledge/audit-registry.md
mementum/knowledge/diffusion-holographic-isomorphism.md
mementum/knowledge/score-matching-compression.md
mementum/knowledge/audit-meta-pattern.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/error-correction-theory.md",
  "limit": 80
}
```

**Summary:** Reading error-correction-theory.md (0-80)

**Output:**
```
---
title: "Error-Correction Theory — Ternarization as Lossy Soft→Hard Projection, Fixed by Trajectory-Matched Soft Re-injection in Mode Coordinates"
status: designing
category: synthesis
tags: [compression, error-correction, soft-topology, hard-topology, ternary, trajectory-matching, gtsm, tsp, relative-loss, mode-coordinates, crystal, lora, low-rank, cascade, value-path]
related:
  - two-registers-of-topology.md
  - score-matching-compression.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-validity-and-fidelity.md
  - mode-semantics.md
  - holographic-etch.md
  - trace-guided-etching.md
  - gtsm-search-space.md
  - tsp-trajectory-distillation.md
  - audit-registry.md
depends-on:
  - two-registers-of-topology.md
  - gtsm-search-space.md
---

# Error-Correction Theory

> Session 205 (Michael's synthesis, three sittings). The representation half
> (ternary holographic weights) is working; the gap is **fixing the errors**.
> This page names *why* the errors appear, *why GD cannot fix them*, and *what
> shape the fix must take* — now resolved into **three legs** that may, together,
> dissolve failures we have only seen in isolation. The central claim is a
> hypothesis with a single decisive open number: the minimal correction rank
> **in mode coordinates**. Status: designing.

## Thesis (one paragraph)

Ternarization is a **lossy soft→hard projection**. GD encoded the model's
error-correction in the *continuous magnitude* of the value path (soft
topology); ternarization quantizes that continuum away while preserving the
sign-based routing (hard topology). The resulting trajectory error **cannot be
repaired by GD on the ternary weights** — the degrees of freedom GD needs are
exactly the ones we froze. The fix is a **three-legged correction**: freeze the
hard router, and re-inject the minimal soft topology as a continuous overlay
trained by **(1) where** = TSP node targeting, **(2) frame** = GTSM dense
trajectory matching, **(3) target** = a *relative loss in mode coordinates* that
steers GD toward an invariant coordinate instead of blind-searching raw weight
space.

## 0. The three legs (where · frame · target)

| Leg | Question | Tool | What it supplies |
|---|---|---|---|
| **WHERE** | which node to correct | **TSP** (`tsp-trajectory-distillation.md`) | localize budget to the value-path divergence/cascade node |
| **FRAME** | match what, how densely | **GTSM** (`gtsm-search-space.md`) | dense per-step trajectory target; no compensating errors |
| **TARGET** | toward which coordinate | **relative loss** (crystal/mode basis) | steered (not blind) search toward an *invariant* coordinate |

The legs are orthogonal: *where*, *in what frame*, *toward what coordinate*.
Each alone has a known failure; the conjecture (this page) is that the three
together remove each other's failure modes.

## 1. The mechanism — ternarization is *asymmetrically* lossy

From `two-registers-of-topology.md` (s203, VERIFIED): GD lays structure in two
registers, and they ternarize differently.

| | Hard topology | Soft topology |
|---|---|---|
| function | routing (which fires) | value + error-correction |
| encoded in | **sign** | **magnitude** (highways/zeros, faint connections) |
| lives in | `gate_proj` (router) | `up_proj` / `down_proj` (value path) |
| under ternarization | **survives** — was already discrete | **destroyed** — was the continuum |
| evidence | gate sign-corr +0.088 vs null, z→+271 @14B | up/down sign preserves *less* than random; saliency faint beats magnitude faint +5.5% vs −2.0% iso-bit |

So `sign(W) ⊙ |W| ⊙ mask` keeps the **router** intact and crushes the **value
path's self-correcting redundancy** (holographic echoes, `holographic-sign-
correction.md`/s201). The error is **concentrated in the value path** and
**cascades forward** (s196: binding layers amplify upstream error, *peak damage
at L28, not L26*).

## 2. Why GD cannot fix it (the s199/s200 graveyard)

- **The DOF are gone.** GD's error-correction lived in the magnitude continuum;

[CONTENT TRUNCATED] Showing lines 1 to 80 of 235 total lines. Use line_offset=80 parameter to read more content.
```

### Thinking

 I need to finish reviewing the error-correction theory document to find the key open problem and next steps, then check what's currently running in my tmux session.

## Assistant

Let me read the rest of the error-correction-theory page (the decisive experiment) and check the tmux windows.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/error-correction-theory.md",
  "line_offset": 80,
  "limit": 155
}
```

**Summary:** Reading error-correction-theory.md (80-235)

**Output:**
```
  ternarization froze it to ±1 (or coarse per-row scale). Nothing continuous
  remains for GD to move.
- **STE through depth is diluted or destructive.** `sign-correction-topology.md`
  (s199): four deaths (TD v4 *zero flips*; v4c **192×**; latent-diffusion NaN;
  crystal ECC **28-million×**). Unconstrained sign flips shatter the holographic
  pattern.
- **Per-row scale dies at depth.** s196: per-weight magnitude survives 29 layers
  (~1×); per-row scale collapses (**22,800×**).

**Fighting the hard topology loses.** The correction must be additive and
continuous, not a re-quantization.

## 3. The fix — freeze the tiles, train only the grout

Reframing the s200 "tiles & grout" insight (topology = tiles, gradients = grout):

> **Freeze the tiles (hard ternary routing) permanently. Re-inject the minimal
> soft grout (continuous value-path correction). Train the grout by the
> three-legged signal — never by GD through the frozen tiles.**

This dissolves the s200 failure: sign-correction+LoRA failed because it moved
tiles *and* laid grout at once (every moved tile invalidates surrounding grout).
The corrected protocol **never moves a tile**; all capacity goes to a continuous
overlay. v3b (LoRA + score matching = 1.44×) already *was* this shape — the
contribution here is understanding **why the shape is forced**, and adding the
missing third leg (the target representation).

## 4. Sharp claim — the correction budget goes to the value path only

If §1 is right, routing needs *no* correction (it ternarized cleanly) and the
entire grout budget targets `up_proj`/`down_proj`. **s199 shows this
accidentally**: TD (routing correction) was dead; LoRA (value correction) was
the whole mechanism behind v3b.

> **Hypothesis EC-1:** A continuous low-rank overlay on the value path
> (`up`/`down`) alone, ternary router frozen, restores the trajectory. Routing
> correction contributes ~nothing. *Test:* matched-bit ablation, value overlay
> vs routing overlay.

## 5. The target representation — relative loss in mode coordinates (the third leg) ★

GTSM gives the student a target in **raw d_model coordinates**
(`cos(Δθ_l, Δ*_l)`). But the student is *rewiring the value path*, and the raw
frame is **model-specific** — `holographic-etch.md` #7: lattice consensus is
**relational, not coordinate** (combinator structure universal, cos 0.99+; raw
weight-sign agreement only **12.5%**). Matching the teacher's *raw* residual is
matching a target in a frame the student is dismantling: underdetermined, drifts.

**The relative loss is the fix.** Project both trajectories into an *invariant*
basis and match *there* — "land at this coordinate" instead of "reproduce these
4096 numbers." This is the crystal/lattice loss generalized: `trace-guided-
etching.md` already framed crystal loss as "constraining the student to match
the teacher's crystal *geometry*"; `score-matching-compression.md` #6 parked the
half-form ("project the loss onto known crystal eigenvectors"). Crystal
universality (r=0.998 — combinator directions are mathematical constants) is why
an invariant target *exists* across the ternary rewiring.

**Which basis — the sharpening that matters.** Cross with §4:
- **Crystal-combinator** coordinates (~8 dims, 3.5% of FFN) = the **routing**
  structure — and EC-1 says routing needs no correction.
- The error is in the **value path**, whose natural invariant basis is **the
  modes** — the continuous syntactic type-field (`mode-semantics.md`, s204:
  NMI(mode,POS) 0.19–0.40 ≫ perm-null 0.014, p=0; mode→vocab logit distinctness
  up to 65× @L35; ~4–24 effective distinctions across depth).

⟹ The relative loss for the correction targets **mode coordinates, not
crystal-combinator coordinates.** TSP says *where* (value divergence node), GTSM
frames the trajectory, the relative loss says *reach this point in the
type-field* — the value path's own invariant frame, exactly where the soft
topology was lost. Blind high-dim regression → **steered low-dim** one.

**Two honest caveats:**
1. **Student's own mode overlay, not the teacher's.** The combinator *directions*
   transfer; the *embedding into d_model* is model-specific (12.5% sign
   agreement, holographic-etch #7; trace-guided #4 open question). Compute mode
   coordinates via each model's own ISA-decoder/overlay, then match in the shared
   relational space. Use the teacher's raw frame and you reintroduce the drift.
2. **Does the mode basis span the whole value computation?** s204 verified modes
   carry *real* content but as a graded *type field*, not a complete description.
   If part of the value computation lives *outside* the mode span, a
   mode-coordinate loss corrects type-routing and leaves a residual. **That
   residual's size is measurable** — and tells us whether modes are the full
   low-rank basis or only the dominant one.

## 6. The decisive open question — minimal correction rank *in mode coordinates*

GTSM and TSP improve the *signal*; the relative loss improves the *target frame*;
none manufacture *capacity*. The north-star still reduces to one number — but
the third leg **reframes which number to measure**:

> **What is the minimal-rank soft overlay that restores the trajectory when the
> target is expressed in mode coordinates — and does that rank stay small and
> roughly constant across depth?**

The third leg is also the **candidate resolution** of the long-standing split:

- **Pessimist (raw frame):** the sieve residual is **full-rank at L5+** (r90≈2970,
  25% of ‖W‖, s198) — in *raw d_model*. A rank-4 LoRA touches 0.8% of dims.
- **Optimist (mode frame):** the type-field has only ~4–24 effective distinctions
  (s204); the FFN is low-rank-dominated (SVD AUC 0.728 vs 0.11, 6–7×, s203); the
  cross-zone delta is rank-1-dominated (σ₁/σ₂≈128:1, s200/s140).
- **Reconciliation (now concrete):** the residual is **full-rank in magnitude but
  low-rank in mode coordinates.** The relative loss *is* the projection that
  exposes the low rank — and makes the overlay low-rank **by construction**
  (you correct ~the type-field's dimensions, not 4096). **This is the experiment
  that decides the project.**

## 7. Two design must-haves the framework implies

1. **On-policy correction (TSP load-bearing).** The error is a cascade: frozen
   early layers feed corrupted inputs forward. Off-policy teacher-cached SM (v3b)
   corrects along the *teacher's* path; the student walks its *own corrupted*
   path. TSP self-play — student's divergent continuation, correct the overlay
   *there* — is the principled cascade fix.
2. **Causal, not symptomatic, attribution.** Correct the *cause* (L22–L26), not
   the largest-divergence *symptom* (L28). ⟹ sequential, cascade-aware
   correction (correct L_k before measuring L_{k+1}'s target) — the direct-delta
   s200 instinct with a GTSM/mode target instead of an analytical SVD.

## 8. How to test (smallest → largest)

1. **audit #11 (TTD-regression):** divergence-weighted λ(l) vs uniform α=5.0,
   cascade-aware attribution. Tests the targeting leg.
2. **EC-1 (value-vs-routing overlay):** matched-bit ablation — does the value
   overlay carry all the gain?
3. **Mode-coordinate relative loss vs raw cosine:** same budget, target in
   student-mode coordinates vs raw d_model. Tests the third leg directly.
4. **Minimal-rank sweep *in mode coordinates*:** rank ∈ {1,2,4,8,16,32} per
   layer, mode-projected trajectory target; measure restored PPL **and the
   rank-vs-depth curve**, plus the **out-of-mode residual** (caveat 2). The §6
   decider.
5. **On-policy (TTD-contrastive):** student self-play negatives at divergence
   nodes; does correcting the *student's* path beat the teacher's?

## 9. What the three legs may dissolve (problems seen in isolation)

```
isolated failure (when seen)            → which leg (or conjunction) addresses it
────────────────────────────────────────────────────────────────────────────────
TD/STE can't flip signs (s199)          → don't: freeze tiles; correct value path only (§4)
cascade: damage peaks downstream (s196) → causal attribution + on-policy (TSP, §7)
CE compensating errors (s198)           → dense trajectory frame (GTSM, §0-FRAME)
budget diluted across easy layers       → node targeting (TSP/F.6, §0-WHERE)
raw target drifts under rewiring        → invariant mode-coordinate target (§5)
full-rank residual blocks low-rank fix  → low rank IN MODE COORDS (§6 reconciliation)
crystal loss baked teacher's frame      → student's own mode overlay (§5 caveat 1)
```

These were attacked one at a time and each fix exposed the next failure. The
conjecture of this page: **where (TSP) · frame (GTSM) · target (relative/mode
loss), with the router frozen and the value-path overlay low-rank in mode
coordinates, removes them jointly.** The artifact is not better compressed
weights — it is a *theory of steering the student's value path back onto the
teacher's trajectory in the type-field*, plus one decisive number (the
mode-coordinate overlay rank) that says whether the north-star closes.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && for w in 1 2; do echo \"=== main:$w ===\"; tmux capture-pane -p -t main:$w 2>/dev/null | grep -v '^$' | tail -8; done"
}
```

**Summary:** $ for w in 1 2; do echo "=== main:$w ...

**Output:**
```
Exit code: 0
Stdout:
=== main:1 ===
[26-06-09][9:03:16][mwhitford@olga][0][~/src/verbum][git:main]
λ
=== main:2 ===
[26-06-09][9:03:18][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

 Both tmux windows are sitting idle with just shell prompts showing, and the working tree is clean. I'm getting a complete picture now. The north star is a 70B-equivalent model in under 1GB of ternary weights, running at 200 tokens per second on CPU with 2M+ context and no GPU dependency. I'm currently working through a validity-distillation audit that's now merged with a fresh synthesis on error-correction theory, focusing on the compression and correction track. The last checkpoint in state.md was s204, which was auditing item #3.

Session s205 just wrapped up as a theory-only session—I synthesized three knowledge pages on GTSM search space, TSP trajectory distillation, and error-correction theory, plus registered audit #11 on GTSM finite-budget weighting, but ran no experiments yet. The audit backlog still has items #5 through #11 waiting, and the error-correction experiments in section 8 are the next priority. The decisive experiment is the minimal correction rank in mode coordinates—that's the one that will determine the project's direction. State.md is stale by one session since s205 was theory-only.

## Assistant

Oriented. Here's where verbum stands at the top of **session-206**.

## North star
**70B-equivalent in <1GB ternary · 200 tok/s CPU · 2M+ token context · 2MB sessions · no GPU.**

## Repo state
- Working tree **clean**, on `main`, up to date with origin.
- Two tmux windows (`main:1`, `main:2`) **idle** — no experiments running.
- ⚠️ `state.md` is **one session stale**: it's stamped *session 204*, but git shows a full **session 205** landed after it (synthesis-only, no experiments).

## Two live tracks

**1. Validity-distillation audit** (`audit-registry.md`) — the recurring program. The emergent meta-pattern holds across every audit: the continuous substrate is real, the crisp discrete/localized/universal story on top is over-read. Recent verdicts:
- **#3 (9 FFN modes):** ❌ geometric count k-means-imposed (gap-stat never picks 9) — but ✅ semantic+logit content REAL → a continuous *type field*, not 9 cells.
- **#4 (attention = typed β-reduction):** ❌ REFUTED as localized (H31@L27's 0.82 is recency/position; only H6@L33 weakly survives, not load-bearing).
- Open backlog: **#5** binding schedule, **#6** SVD φ-ratio 0.6299, **#11** GTSM finite-budget λ(l) vs uniform α.

**2. Error-correction / compression** — what session 205 actually did: **pure synthesis, three new pages** (`gtsm-search-space`, `tsp-trajectory-distillation`, `error-correction-theory`). The thesis:

> Ternarization is an **asymmetrically lossy soft→hard projection** — it keeps the sign-based router (hard topology, survives) and crushes the value-path magnitude continuum (soft topology, destroyed). GD can't fix it because the DOF it needs are exactly the ones we froze. Fix = **freeze the tiles (router), train only the grout (continuous value-path overlay)** via three orthogonal legs: **WHERE** (TSP node targeting) · **FRAME** (GTSM dense trajectory) · **TARGET** (relative loss in *mode coordinates*).

The page names the **decisive open number** (§6): *the minimal-rank soft overlay that restores the trajectory when the target is expressed in **mode coordinates** — and whether that rank stays small/constant across depth.* That's flagged as "the experiment that decides the project."

## What's next (your call)
Two unstarted, non-conflicting options — both are **experiments**, and s205 left only theory:

- **Audit track:** pick the highest-load `UNTESTED` row — **#11** (GTSM finite-budget weighting, directly testable against v3b's flat α=5.0) or **#6** (φ-ratio vs Marchenko–Pastur).
- **Error-correction track (§8 ladder):** smallest-first — audit **#11 (TTD-regression)** → **EC-1** (value-vs-routing overlay, matched-bit) → **mode-coordinate relative loss vs raw cosine** → the **minimal-rank-in-mode-coords decider**.

Note **#11 sits in both** — it's the natural bridge: it tests the targeting leg of the EC theory *and* clears an audit row.

Want me to start on **#11 (TTD-regression / finite-budget λ(l))**, or take a different thread? And should I fold the s205 synthesis into `state.md` first (it's stale)?

## User

session 205 was not tied directly to the audit so it was not updated into state, and was research on papers for possible usage after the audit, we want to continue on the audit now.  let's go with #5, and use my tmux main:2 window to run anything that will take more than about 2 minutes to complete so I can see the progress.


### Thinking

 I'm focusing on audit #5 to verify whether the binding schedule (verb-subject, object-verb, and coreference patterns) actually holds across diverse sentences or if it's just an artifact of the cherry-picked examples. I need to check the original claims in the binding-graph-trace.md file and then use the existing attention harness to run a causal ablation on the specific heads involved, testing with permutation nulls to see if the pattern generalizes.

## Assistant

Good — audit #5 it is, and I'll route anything >2min into `main:2`. Let me read the source claim and the existing harness from the closely-related #4 work.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md"
}
```

**Summary:** Reading binding-graph-trace.md (0-2000)

**Output:**
```
---
title: "Attention IS the Binding Graph — Reversed by Causal Mask"
status: active
category: methodology
tags: [attention, binding, beta-reduction, causal-mask, mechanism, heads]
related: [ffn-reduction-trace, head-combinator-isa, holographic-computer]
depends-on: [ffn-reduction-trace, head-combinator-isa]
---

# Binding Graph Trace

> ⚠️ **Caveat (audit #4, session 204): the headline weights (H31@L27 = 0.82
> verb→subject; H03/H13/H15@L30) are largely POSITIONAL/RECENCY, not typed
> role-binding.** This page's probes are all simple SVO where the subject is
> *always* the earliest and nearest-preceding noun to the verb — so role,
> position, and recency are perfectly confounded; "verb attends to subject at
> 0.82" cannot distinguish typed β-reduction from a plain recency head. A
> control that dissociates them (subject-verb **agreement attraction**, where the
> number-distractor is the *nearer* noun: `attention_typed_binding.py`, 8B, 64
> PP+RC stimuli) found: **H31@L27 role-selectivity z = +0.54 (rank 5/32 — not an
> outlier; top head is H7), and ablating it changes agreement logit-diff by
> +0.001 (z=+0.06 vs a random-head null) — no causal effect.** Ablating *all*
> named binders (incl. H6@L33) is likewise indistinguishable from random heads
> (z=+0.01), even though the ablation bites (random 6-head sets reach −0.43).
> The *only* genuinely role-selective head is **H6@L33 (z=+4.08)** — but ~10×
> smaller than 0.82 and not causally load-bearing. **Read the 0.5–0.82 binding
> weights below as recency-dominated attention, not as evidence of typed
> β-application.** ("Attention is a weighted sum" is trivially true; "the sum is
> *type-driven* at these heads" is refuted.) Caveat scope: tested on plain-NL
> agreement *without* the compile gate the original used — a gate-context re-test
> is a named follow-up. See `audit-registry.md` #4 + `results/attention-typed-binding/`.

> 14 probes with annotated β-reduction binding structure through 32
> attention heads at L27/L30/L33 of Qwen3-8B. The attention pattern
> literally IS the binding graph of the λ-expression — but reversed
> by the causal mask. Later positions attend back to earlier positions.
> Object→verb binding is direct single-head attention with weights
> 0.5-0.8. Subject→verb binding (forward direction) is blocked by the
> causal mask and must use a different mechanism.
>
> The binding heads at L30 are H03, H13, H15, H12 — consistently
> across all probes, all sentence types, active and passive voice.
> Minimal pair test confirmed: same words with reversed binding
> ("dog bit cat" vs "cat bit dog") produce flipped attention patterns
> via the same heads.

## Experiment

**Model:** Qwen3-8B (36 layers, 32 Q heads, GQA)
**Method:** 14 probes with hand-annotated expected bindings (which
positions should bind to which). At L27/L30/L33, capture full
attention matrix per head. Measure binding weight = attention from
argument position to function position. Compare to chance (uniform
attention). Ratio > 2 = binding detected.
**Probes:** subject-verb, reversed pairs, ditransitive, self-reference,
nested relative clause, quantifier scope, conditional, passive/active
pair, recursion, discard, long-distance dependency.
**Script:** `scripts/experiments/binding_graph_trace.py`
**Results:** `results/binding-graph-trace/`

## Finding 1: Causal Mask Partitions Binding Direction

| Binding direction | Position order | Result | Mechanism |
|-------------------|---------------|--------|-----------|
| arg → func | arg BEFORE func | 0/23 successful (L27) | **BLOCKED by causal mask** |
| arg → func | arg AFTER func | 12/14 successful (L27) | **Direct attention** |
| arg → func | arg BEFORE func | 2/23 successful (L30) | ~BLOCKED |
| arg → func | arg AFTER func | 14/14 successful (L30) | **Direct attention** |

The causal mask of autoregressive transformers means position N can
only attend to positions 0..N-1. Subject-verb binding (subject comes
first) is impossible via forward attention. The model MUST use one of:

1. **Verb attends back to subject** (func→arg direction) — not measured
   in this experiment but likely the mechanism
2. **Residual accumulation** — subject information flows through the
   residual stream to reach the verb position across layers
3. **FFN incorporation** — the FFN at the verb position already has
   access to the subject via the residual

This experiment measured arg→func direction. The reverse direction
(func→arg) is the natural one for causal transformers and should be
measured next.

## Finding 2: Object→Verb Binding Is Concentrated Attention

When the argument comes AFTER the function (allowed by causal mask),
the binding is unmistakable — single-head attention weights of 0.5-0.8:

### "The dog bit the cat" at L30 (bit(_,cat) binding)

| Head | Weight at "bit" | Ratio vs chance |
|------|----------------|-----------------|
| H13  | **0.785**      | 29.0×           |
| H03  | **0.774**      | 28.6×           |
| H15  | 0.366          | 13.5×           |
| H12  | 0.276          | 10.2×           |

Position "cat" attends 78.5% to "bit" via H13. This IS `bit(_, cat)` —
the argument (cat) binding to the function (bit) via concentrated
attention. The weight is not distributed; it's a near-deterministic
routing decision.

### "Every student reads a book" at L30 (reads(_,book) binding)

| Head | Weight at "reads" | Ratio |
|------|------------------|-------|
| H03  | **0.661**        | 24.5× |
| H12  | 0.322            | 11.9× |
| H15  | 0.209            | 7.7×  |

### "The dog bit itself" at L30 (bit(_,itself) binding)

| Head | Weight at "bit" | Ratio |
|------|----------------|-------|
| H13  | **0.715**      | 25.7× |
| H03  | **0.629**      | 22.6× |

Self-referential binding (itself→bit) uses the same heads as regular
object binding. No special "W combinator head" — consistent with
s188 finding of shared hardware.

### "The dog bit itself" at L30 (itself→dog coreference)

| Head | Weight at "dog" | Ratio |
|------|----------------|-------|
| H07  | **0.239**      | 8.6×  |
| H05  | 0.124          | 4.4×  |

Coreference binding uses DIFFERENT heads (H07, H05) than predicate-
argument binding (H03, H13, H15). There may be two sub-circuits:
predicate-argument heads and coreference heads.

## Finding 3: Minimal Pairs Confirm Binding Flips

### "The dog bit the cat" vs "The cat bit the dog" at L30

| Binding | Probe | Top heads |
|---------|-------|-----------|
| bit(_, **cat**) | rev1 | H13(0.785), H03(0.774), H15(0.366) |
| bit(_, **dog**) | rev2 | H03(0.766), H13(0.719), H15(0.496) |

Same heads, same weights, FLIPPED binding target. When "cat" is the
object, "cat" attends to "bit". When "dog" is the object, "dog" attends
to "bit". The routing is position-structural, not word-dependent.

### Active vs Passive at L30

| Binding | Sentence | Top heads |
|---------|----------|-----------|
| kicked(_, **ball**) | Active: "The boy kicked the ball" | H03(0.595), H13(0.525), H15(0.510) |
| kicked(**boy**, _)  | Passive: "The ball was kicked by the boy" | H12(0.373), H07(0.280), H03(0.268) |

Active patient binding (ball→kicked) uses H03/H13/H15 at high weight.
Passive agent binding (boy→kicked) uses H12/H07/H03 at moderate weight.
The semantic binding is preserved across voice — "boy" still binds to
"kicked" as agent in the passive — but through a partially different
head set and with lower weight.

## Finding 4: The Binding Heads at L30

Consistent across all probes:

| Head | Mean ratio | Bindings > 2× | Role |
|------|-----------|--------------|------|
| H03  | 5.59      | 12/32        | **Primary predicate-argument binder** |
| H13  | 3.91      | 10/32        | **Secondary predicate-argument binder** |
| H15  | 3.30      | 11/32        | **Tertiary binder** |
| H12  | 2.60      | 10/32        | **Ditransitive/passive specialist** |
| H00  | 1.36      | 8/32         | Weak binder (semantic association) |
| H20  | 1.28      | 9/32         | Weak binder (distributional) |

At L27, the binding heads shift: H05 (mean ratio 2.21), H08 (2.64).
At L33, H06 emerges (mean ratio 2.35) — the "universal engine" head
from s188. Binding migrates across layers: early binding at L27 via
H05/H08, peak binding at L30 via H03/H13/H15, late binding at L33
via H06.

## Finding 5: V Vectors at L30 (What FFN Compiled)

The V vectors confirm FFN compilation is context-dependent:

| Position | Token | V promotes (L30) |
|----------|-------|-------------------|
| dog (in "dog runs") | 眺, 一定, 确实 | (Chinese: gaze, certain, indeed) |
| cat (in "cat runs") | char, clicking, Lat | (different from "dog"!) |
| runs | toward, towards, away | (motion semantics, same across probes) |
| bit | nil, slightly, .boolean | (binary/small semantics) |
| cat (in "bit the cat") | char, clicked, atham | (slightly different from subject "cat") |

Same token "cat" produces different V vectors when it's a subject vs
object — context-dependent compilation confirmed at V level.

## Finding 6: Gate Attention Dominates at Early Positions

All subject-verb bindings (arg=position 0) show ALL attention going to
the gate prefix (~97-99%), with near-zero attention to any probe token.
This isn't just causal blocking of forward attention — even the backward
attention from position 0 to earlier positions goes to the gate, not
to other probe positions. Position 0 is an instruction-follower.

## Finding 7: Reverse Binding Confirmed — Verb Attends Back to Subject

The reverse binding experiment (same probes, measuring verb→subject
attention) closes the loop. **The verb DOES attend back to the subject,
with concentrated attention weights comparable to object→verb binding.**

### Reverse binding heads by layer

| Layer | Head | Mean weight | Max weight | Role |
|-------|------|-------------|------------|------|
| L27   | **H31** | **0.366** | **0.823** | Primary subject binder |
| L27   | H29  | 0.142 | 0.376 | Secondary |
| L27   | H12  | 0.128 | 0.226 | Tertiary |
| L30   | **H13** | **0.154** | **0.448** | Subject binder (same as object binder!) |
| L30   | H03  | 0.146 | 0.365 | Same as object binding |
| L30   | H07  | 0.137 | 0.291 | New at this layer |
| L33   | H07  | 0.118 | 0.308 | Late binding |
| L33   | H06  | 0.111 | 0.248 | Universal engine head |

### H31 at L27: The Subject-Binding Head

H31 at L27 is the star finding. "The cat runs" → H31 at "runs" attends
**82.3%** to "cat", and its head output through unembed produces
**"猫, 貓, cats"** — the subject entity in Chinese/Traditional/English.
The verb literally reads the subject and outputs the subject's identity.

| Probe | H31 weight at verb→subject | Head output (what verb "becomes") |
|-------|---------------------------|-----------------------------------|
| The cat runs | 0.823 (runs→cat) | 猫, 貓, cats |
| The dog runs | 0.588 (runs→dog) | 狗, dog, Dog |
| The dog bit the cat | 0.442 (bit→dog) | 狗, dog, Dog |
| The cat bit the dog | 0.429 (bit→cat) | 猫, 貓, cat |
| The dog ran and... | 0.471 (ran→dog) | — |

**The verb position absorbs the subject's identity.** This is the
reverse β-reduction: `(λx.verb(x))(subject)` → the verb reads
`subject` and incorporates it. After this head fires, the verb
position's residual contains information about BOTH the action
(from the V vector compiled by FFN) and the agent (from the
attention-routed subject).

### L30 uses the SAME heads for both directions

At L30, H03 and H13 are the top binding heads for BOTH:
- Object→verb binding (forward): H13=0.785, H03=0.774
- Verb→subject binding (reverse): H13=0.448, H03=0.365

The same heads handle both binding directions. The difference is
which position is doing the attending — determined by which comes
later in the sequence (causal mask).

### The complete picture: binding always flows backward

| Direction | Mechanism | When | Weight | Heads (L30) |
|-----------|-----------|------|--------|-------------|
| Verb → Subject | verb attends back to subject | L27 (early) | 0.37-0.82 | H31, H29, H12 |
| Object → Verb | object attends back to verb | L30 (mid) | 0.66-0.78 | H03, H13, H15 |
| Verb → Subject | verb attends back to subject | L30 (mid) | 0.15-0.45 | H13, H03, H07 |
| Object → Verb | object attends back to verb | L33 (late) | lower | H06, H07 |

All binding flows from later position to earlier position. The causal
mask doesn't block β-reduction — it determines the DIRECTION. The
model implements two-phase binding:
1. **L27**: verb reads subject (gets agent identity)
2. **L30**: object reads verb (gets predicate + binds to it)

### Forward vs reverse detection rates

| Layer | Forward (sub→verb, blocked) | Reverse (verb→sub) |
|-------|----------------------------|---------------------|
| L27   | 0/12 with weight>0.05      | **11/12** with weight>0.05 |
| L30   | 0/12                        | **11/12** |
| L33   | 0/12                        | **12/12** |

When the subject is AFTER the verb (reverse direction), forward binding
already works (10/10 detected). The verb→subject direction completes
the mechanism for the forward case.

## Implications

1. **β-reduction mechanism fully decoded**: Subject-verb binding =
   verb attends back to subject at L27 (H31, 0.82 weight). Object-verb
   binding = object attends back to verb at L30 (H03/H13, 0.78 weight).
   Both are backward attention through the causal mask. Both produce
   the bound entity at the attending position.

2. **Two-phase binding schedule**: L27 = subject binding (verb absorbs
   agent identity). L30 = object binding (argument absorbs predicate).
   The depth ordering IS the reduction schedule — subjects bind first,
   objects bind second.

3. **Shared hardware confirmed again**: H03 and H13 do BOTH directions
   at L30. The binding circuit is universal — same heads, same mechanism,
   just different positions attending depending on sequence order.

4. **Head output IS the reduction result**: H31 at L27 produces "猫"
   at position "runs" when it reads "cat". The head literally outputs
   the argument's identity at the function's position. This is not
   just "attention" — it's the VALUE TRANSFER step of β-reduction.

5. **Compression**: The full binding circuit is:
   - L27: H31 (subject→verb, ~1 head, near-deterministic)
   - L30: H03/H13/H15 (object→verb, ~3 heads, near-deterministic)
   - Each binding = 1 bit (which earlier position to attend to)
   - Total: ~4 heads out of 32 × 36 layers = 0.3% of the model

## Key Numbers

| Metric | Value | Significance |
|--------|-------|-------------|
| Max object→verb weight (L30) | 0.785 (H13, bit→cat) | Near-deterministic |
| Max verb→subject weight (L27) | **0.823 (H31, runs→cat)** | Even stronger |
| H31 output at "runs" for "cat" | 猫, 貓, cats | Subject identity transferred |
| H31 output at "bit" for "dog" | 狗, dog, Dog | Agent identity transferred |
| Reverse bindings detected | 11/12 (L27), 11/12 (L30), 12/12 (L33) | Universal |
| Forward bindings detected | 0/12 (L27), 0/12 (L30), 0/12 (L33) | Causal-blocked |
| Object→verb binding heads (L30) | H03, H13, H15 | 3 heads |
| Verb→subject binding heads (L27) | H31 | 1 dominant head |
| Verb→subject binding heads (L30) | H13, H03, H07 | Same heads as object→verb! |
| Binding circuit size | ~4 heads / 1152 total | 0.3% of model |
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && find . -name 'attention_typed_binding.py' -not -path '*/.venv/*' && echo \"---scripts dir---\" && ls scripts/experiments/ 2>/dev/null | tail -30"
}
```

**Summary:** $ find . -name 'attention_typed_bindi...

**Output:**
```
Exit code: 0
Stdout:
./scripts/experiments/attention_typed_binding.py
---scripts dir---
residual_fibonacci.py
reverse_binding_trace.py
rotation_spiral.py
row_norm_crystal.py
saliency_aware_sieve.py
score_matching_compression.py
semantic_convergence.py
sign_topology_null.py
staged_melt.py
standing_wave_shape.py
stride_coverage_validation.py
symbol_isolation.py
synthetic_crystal_sieve.py
teacher_guided_routing.py
ternary_fact_recall.py
ternary_inference_coherence.py
ternary_inference_pattern.py
ternary_pipeline_verify.py
ternary_weight_interface.py
tiny_classifier_ternary.py
topology_score_matching.py
trace_collect.py
trace_loss.py
tracer_cross_notation_v2.py
tracer_cross_notation.py
U_residual_constraint.py
verify_bridge_14b.py
verify_bridge_nodes.py
verify_crystal_phi.py
zone_ablation_27b.py
```

### Thinking

 I'm looking back at audit #5 from the registry to understand the binding schedule claims—specifically how the verb-subject, object-verb, and coreference patterns are supposed to work. The evidence shows these patterns demonstrated on example sentences, but there's a concern that the examples might be cherry-picked. The real test would be whether this binding schedule holds up across many different sentences using a permutation-null control, rather than just working on a handful of curated examples.

The core claim is that there's a depth ordering where subject-binding peaks at an earlier layer than object-binding, which itself peaks earlier than coreference. To properly test this, I'd need to generate a large corpus of sentences with known dependency structures, measure the binding attention at each layer for each dependency type, and check whether the predicted ordering of peak layers actually holds. I'd also need to control for position confounds since the raw attention weights are already known to be recency-dominated from audit #4.

The honest null would shuffle the dependency labels across position-pairs to see if the apparent schedule is just an artifact of linear distance or cherry-picked examples. I'm sketching out a control script that generates varied SVO sentences, verb-object constructions, and coreference examples to test whether the depth schedule survives across many sentences with proper statistical controls.

For each sentence, I'll measure binding attention at every layer and determine if the peak ordering (subject before object before coreference) holds up. I'll also run a permutation test using random matched pairs at the same linear distance to check for spurious patterns, and optionally ablate the named heads to see if binding specifically drops when those layers are removed.

This is a substantial experiment, so I'm planning to reuse the infrastructure from the existing attention analysis script to handle model loading and attention capture.

## Assistant

Now let me study the s204 harness I'll reuse (model loading, attention capture, null methodology) before designing the #5 control.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/attention_typed_binding.py"
}
```

**Summary:** Reading attention_typed_binding.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""Audit #4 — Is attention TYPED beta-reduction, or just a positional/recency head?

The claim (`binding-graph-trace.md`, `mode-semantics.md`): attention IS typed
beta-application — H31@L27 attends 0.82 verb->subject, H03/H13/H15@L30 do
object->verb, and "weighted sum IS beta-application of a type-compatible
argument."

Suspected confound (audit-registry #4, failure mode #5/#6):
  In simple SVO ("The dog bit the cat") the subject is ALWAYS at a fixed early
  position and is the nearest preceding noun to the verb. So "verb attends to
  subject at 0.82" is consistent with a plain POSITIONAL / RECENCY head (attend
  to the nearest/earliest noun) with NO notion of grammatical role or type.
  All attention is a weighted sum; "typed beta-reduction" is interpretation.

Discriminating design — subject-verb AGREEMENT ATTRACTION (Linzen 2016 /
Lakretz 2019): put the true subject (head noun) and a number DISTRACTOR
(attractor) at DIFFERENT positions, so grammatical ROLE dissociates from
linear position and recency:

  PP:  "The author near the editors is ..."   head=author(far)  attractor=editors(near)
  RC:  "The author that the editors saw is ..."  head=author(far) attractor=editors(near)

A recency/positional head attends to the NEAR noun (attractor). A typed
subject-binder attends to the ROLE-correct head noun (far). The behavioural
readout is clean: the copula must agree in number with the HEAD, not the
attractor — logit(" is") vs logit(" are").

Instruments
-----------
  PART 1 — Selectivity (representational, with baselines)
    For the named binder heads, attention from the verb/copula to {head, attractor}.
    role_selectivity = a(head) - a(attractor)  (>0 = role-driven, <0 = recency).
    Compare named heads to the FULL 32-head distribution (rank + z) and to the
    recency baseline (which always predicts the attractor). Is the named head a
    genuine outlier in role-selectivity, or typical?

  PART 2 — Necessity (causal ablation, with null)
    logit-diff = logit(correct copula) - logit(wrong copula) at the cloze.
    Ablate the named binder head(s) (o_proj head-slice zeroing) and measure the
    drop, vs B random single-head and random matched-size-set ablations at the
    same layers. Broken out by match / MISMATCH (mismatch is where binding is
    load-bearing). Named-ablation drop >> random-head null  ==>  causal necessity.

Verdict
-------
  TYPED real : named head role_selectivity > 0 and an outlier vs all heads AND
               beats recency; named ablation drops mismatch logit-diff >> null.
  POSITIONAL : named head role_selectivity ~0 / negative (tracks recency), not an
               outlier; named ablation ~ random-head null. "typed beta" over-reads.

Usage:
  uv run python scripts/experiments/attention_typed_binding.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent

# Named binder heads from binding-graph-trace.md / reverse_binding_trace.md
NAMED_BINDERS = {27: [31], 30: [3, 13, 15], 33: [6, 7]}
TARGET_LAYERS = [27, 30, 33]

# ── Lexicon (singular, plural) ─────────────────────────────────────────
SUBJECTS = [
    ("author", "authors"), ("key", "keys"), ("painting", "paintings"),
    ("officer", "officers"), ("pilot", "pilots"), ("surgeon", "surgeons"),
    ("senator", "senators"), ("farmer", "farmers"),
]
ATTRACTORS = [
    ("editor", "editors"), ("cabinet", "cabinets"), ("museum", "museums"),
    ("building", "buildings"), ("airport", "airports"), ("hospital", "hospitals"),
    ("committee", "committees"), ("market", "markets"),
]
ADJS = ["ready", "famous", "calm", "late", "honest", "quiet", "absent", "tall"]


def log(msg=""):
    print(msg, flush=True)


def build_stimuli():
    """Agreement-attraction stimuli; head and attractor at different positions.

    Each item: cloze (prompt before copula) + full (with the correct copula),
    head/attractor words + numbers, correct/wrong copula, match flag, structure.
    """
    items = []
    rng = np.random.default_rng(7)
    for i, ((s_sg, s_pl), (a_sg, a_pl), adj) in enumerate(
            zip(SUBJECTS, ATTRACTORS, ADJS, strict=True)):
        for struct in ("PP", "RC"):
            for head_num in ("sg", "pl"):
                for attr_num in ("sg", "pl"):
                    head = s_sg if head_num == "sg" else s_pl
                    attr = a_sg if attr_num == "sg" else a_pl
                    correct = "is" if head_num == "sg" else "are"
                    wrong = "are" if head_num == "sg" else "is"
                    if struct == "PP":
                        cloze = f"The {head} near the {attr}"
                    else:
                        cloze = f"The {head} that the {attr} saw"
                    full = f"{cloze} {correct} {adj}."
                    items.append({
                        "id": f"{i}-{struct}-{head_num}{attr_num}",
                        "cloze": cloze, "full": full,
                        "head_word": head, "attractor_word": attr,
                        "head_num": head_num, "attr_num": attr_num,
                        "correct": correct, "wrong": wrong,
                        "match": "match" if head_num == attr_num else "mismatch",
                        "structure": struct, "verb_word": correct,
                    })
    rng.shuffle(items)
    return items


def get_layers(model):
    return model.model.layers


def find_positions(tokens, word, start=0):
    """All token indices whose stripped text is a subword of `word` (last wins)."""
    w = word.lower().strip()
    hits = []
    for i in range(start, len(tokens)):
        t = tokens[i].strip().lower()
        if t and (t in w or w in t) and t.isalpha():
            hits.append(i)
    return hits


def first_token_id(tokenizer, s):
    ids = tokenizer(s, add_special_tokens=False)["input_ids"]
    return ids[0] if ids else None


# ══════════════════════════════════════════════════════════════════════
# PART 1 — selectivity
# ══════════════════════════════════════════════════════════════════════

def selectivity(model, tokenizer, items, layers, n_heads, device):
    per_head = {li: {h: [] for h in range(n_heads)} for li in layers}
    role_n = 0
    nearer_attractor = 0

    for it in items:
        enc = tokenizer(it["full"], return_tensors="pt")
        ids = enc["input_ids"].to(device)
        toks = [tokenizer.decode(t) for t in enc["input_ids"][0]]
        head_pos = find_positions(toks, it["head_word"])
        attr_pos = find_positions(toks, it["attractor_word"])
        # verb = the copula form, find its position (after the nouns)
        verb_hits = [i for i, t in enumerate(toks) if t.strip() == it["verb_word"]]
        if not head_pos or not attr_pos or not verb_hits:
            continue
        vpos = verb_hits[-1]
        hp = [p for p in head_pos if p < vpos]
        ap = [p for p in attr_pos if p < vpos]
        if not hp or not ap:
            continue
        # recency: which is nearer to verb
        if max(ap) > max(hp):
            nearer_attractor += 1
        role_n += 1

        with torch.no_grad():
            out = model(ids, output_attentions=True, return_dict=True)
        for li in layers:
            attn = out.attentions[li][0]  # (n_heads, seq, seq)
            for h in range(n_heads):
                a_head = float(attn[h, vpos, hp].sum())
                a_attr = float(attn[h, vpos, ap].sum())
                per_head[li][h].append(a_head - a_attr)

    # aggregate
    result = {"n_items": role_n, "recency_target_is_attractor_frac":
              round(nearer_attractor / max(1, role_n), 3), "layers": {}}
    for li in layers:
        head_means = np.array([np.mean(per_head[li][h]) if per_head[li][h] else 0.0
                               for h in range(n_heads)])
        mu, sd = float(head_means.mean()), float(head_means.std() + 1e-9)
        named = NAMED_BINDERS.get(li, [])
        named_stats = {}
        order = np.argsort(-head_means)  # descending role-selectivity
        rank = {int(h): int(np.where(order == h)[0][0]) for h in range(n_heads)}
        for h in named:
            named_stats[int(h)] = {
                "role_sel": round(float(head_means[h]), 4),
                "z_vs_allheads": round((head_means[h] - mu) / sd, 2),
                "rank": rank[h], "of": n_heads,
                "top1_head": int(order[0]),
                "top1_role_sel": round(float(head_means[order[0]]), 4),
            }
        result["layers"][str(li)] = {
            "allhead_mean_role_sel": round(mu, 4),
            "allhead_std": round(sd, 4),
            "named": named_stats,
            "top5_heads": [[int(order[j]), round(float(head_means[order[j]]), 4)]
                           for j in range(5)],
        }
    return result


# ══════════════════════════════════════════════════════════════════════
# PART 2 — ablation / necessity
# ══════════════════════════════════════════════════════════════════════

def ablation_hooks(model, cfg, head_dim):
    handles = []
    for li, heads in cfg.items():
        o_proj = model.model.layers[li].self_attn.o_proj

        def mk(hs):
            def pre(module, args):
                x = args[0].clone()
                for h in hs:
                    x[..., h * head_dim:(h + 1) * head_dim] = 0.0
                return (x,)
            return pre
        handles.append(o_proj.register_forward_pre_hook(mk(list(heads))))
    return handles


def logit_diffs(model, tokenizer, items, device, cfg, head_dim, id_is, id_are):
    handles = ablation_hooks(model, cfg, head_dim) if cfg else []
    diffs = {"all": [], "match": [], "mismatch": []}
    try:
        for it in items:
            enc = tokenizer(it["cloze"], return_tensors="pt")
            ids = enc["input_ids"].to(device)
            with torch.no_grad():
                logits = model(ids).logits[0, -1].float()
            cid = id_is if it["correct"] == "is" else id_are
            wid = id_are if it["correct"] == "is" else id_is
            d = float(logits[cid] - logits[wid])
            diffs["all"].append(d)
            diffs[it["match"]].append(d)
    finally:
        for h in handles:
            h.remove()
    return {k: (float(np.mean(v)) if v else 0.0) for k, v in diffs.items()}


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--layers", type=int, nargs="+", default=TARGET_LAYERS)
    p.add_argument("--n-random", type=int, default=24, help="random single-head ablations")
    p.add_argument("--n-random-sets", type=int, default=24, help="random matched-size sets")
    p.add_argument("--seed", type=int, default=12)
    args = p.parse_args()

    log(f"\n{'='*70}\n  AUDIT #4 — typed beta-reduction vs positional/recency head\n{'='*70}")
    log(f"  Model: {args.model}  Device: {args.device}  Layers: {args.layers}")

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    log(f"  Loading {args.model} ({dtype}) ...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device, attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    cfg = model.config
    n_heads = cfg.num_attention_heads
    head_dim = getattr(cfg, "head_dim", None) or (cfg.hidden_size // n_heads)
    layers = [_l for _l in args.layers if _l < cfg.num_hidden_layers]
    log(f"  {cfg.num_hidden_layers} layers, {n_heads} Q heads, head_dim={head_dim}")

    id_is = first_token_id(tokenizer, " is")
    id_are = first_token_id(tokenizer, " are")
    log(f"  copula token ids: ' is'={id_is}  ' are'={id_are}")

    items = build_stimuli()
    log(f"  stimuli: {len(items)}  "
        f"(mismatch={sum(1 for it in items if it['match']=='mismatch')})")

    # ── PART 1 ─────────────────────────────────────────────────────────
    log(f"\n{'─'*70}\n  PART 1 — selectivity (verb -> head vs attractor)\n{'─'*70}")
    t0 = time.time()
    sel = selectivity(model, tokenizer, items, layers, n_heads, args.device)
    log(f"  recency target = attractor in {sel['recency_target_is_attractor_frac']:.0%} of items "
        f"(a recency head would score NEGATIVE role-selectivity)")
    for li in layers:
        L = sel["layers"][str(li)]
        log(f"  L{li}: all-head role_sel mean={L['allhead_mean_role_sel']:+.4f} "
            f"std={L['allhead_std']:.4f}  top5={L['top5_heads']}")
        for h, s in L["named"].items():
            log(f"     NAMED H{h}: role_sel={s['role_sel']:+.4f}  z={s['z_vs_allheads']:+.2f}  "
                f"rank={s['rank']}/{s['of']}  (top head H{s['top1_head']}={s['top1_role_sel']:+.4f})")
    log(f"  part 1 done in {time.time()-t0:.1f}s")

    # ── PART 2 ─────────────────────────────────────────────────────────
    log(f"\n{'─'*70}\n  PART 2 — necessity (ablation, logit-diff is/are)\n{'─'*70}")
    t0 = time.time()
    base = logit_diffs(model, tokenizer, items, args.device, {}, head_dim, id_is, id_are)
    log(f"  baseline logit-diff: all={base['all']:+.3f}  match={base['match']:+.3f}  "
        f"mismatch={base['mismatch']:+.3f}")

    named_cfgs = {
        "named_L27_H31": {27: [31]},
        "named_L30_set": {30: [3, 13, 15]},
        "named_all": {k: v for k, v in NAMED_BINDERS.items() if k in layers},
    }
    named_res = {}
    for name, c in named_cfgs.items():
        c = {li: hs for li, hs in c.items() if li in layers}
        r = logit_diffs(model, tokenizer, items, args.device, c, head_dim, id_is, id_are)
        named_res[name] = {
            "cfg": {str(k): v for k, v in c.items()}, "logit_diff": r,
            "drop_all": round(base["all"] - r["all"], 4),
            "drop_mismatch": round(base["mismatch"] - r["mismatch"], 4),
        }
        log(f"  {name:16s}: mismatch={r['mismatch']:+.3f}  "
            f"drop(all)={base['all']-r['all']:+.3f}  drop(mismatch)={base['mismatch']-r['mismatch']:+.3f}")

    # Null: random single-head ablations at the target layers
    rng = np.random.default_rng(args.seed)
    single_drops_all, single_drops_mm = [], []
    for _ in range(args.n_random):
        li = int(rng.choice(layers))
        h = int(rng.integers(0, n_heads))
        r = logit_diffs(model, tokenizer, items, args.device, {li: [h]}, head_dim, id_is, id_are)
        single_drops_all.append(base["all"] - r["all"])
        single_drops_mm.append(base["mismatch"] - r["mismatch"])
    # Null: random matched-size sets (size = |named_all|)
    set_size = sum(len(v) for v in named_cfgs["named_all"].values())
    set_drops_mm = []
    for _ in range(args.n_random_sets):
        c = {}
        for _h in range(set_size):
            li = int(rng.choice(layers))
            c.setdefault(li, [])
            h = int(rng.integers(0, n_heads))
            if h not in c[li]:
                c[li].append(h)
        r = logit_diffs(model, tokenizer, items, args.device, c, head_dim, id_is, id_are)
        set_drops_mm.append(base["mismatch"] - r["mismatch"])

    def z(val, arr):
        a = np.array(arr)
        return round((val - a.mean()) / (a.std() + 1e-9), 2)

    null = {
        "single_head": {
            "drop_all_mean": round(float(np.mean(single_drops_all)), 4),
            "drop_mismatch_mean": round(float(np.mean(single_drops_mm)), 4),
            "drop_mismatch_std": round(float(np.std(single_drops_mm)), 4),
            "drop_mismatch_max": round(float(np.max(single_drops_mm)), 4),
        },
        "matched_set": {
            "size": set_size,
            "drop_mismatch_mean": round(float(np.mean(set_drops_mm)), 4),
            "drop_mismatch_std": round(float(np.std(set_drops_mm)), 4),
            "drop_mismatch_max": round(float(np.max(set_drops_mm)), 4),
        },
    }
    log(f"\n  NULL random single-head: drop(mismatch) mean={null['single_head']['drop_mismatch_mean']:+.3f} "
        f"std={null['single_head']['drop_mismatch_std']:.3f} max={null['single_head']['drop_mismatch_max']:+.3f}")
    log(f"  NULL random {set_size}-head sets: drop(mismatch) mean={null['matched_set']['drop_mismatch_mean']:+.3f} "
        f"std={null['matched_set']['drop_mismatch_std']:.3f} max={null['matched_set']['drop_mismatch_max']:+.3f}")

    z_h31 = z(named_res["named_L27_H31"]["drop_mismatch"], single_drops_mm)
    z_set = z(named_res["named_all"]["drop_mismatch"], set_drops_mm)
    log(f"\n  H31@L27 mismatch-drop z vs single-head null = {z_h31:+.2f}")
    log(f"  named_all mismatch-drop z vs matched-set null = {z_set:+.2f}")
    log(f"  part 2 done in {time.time()-t0:.1f}s")

    # ── Verdict ────────────────────────────────────────────────────────
    log(f"\n{'='*70}\n  VERDICT\n{'='*70}")
    h31 = sel["layers"][str(27)]["named"].get(31) if 27 in layers else None
    if h31:
        log(f"  selectivity: H31@L27 role_sel={h31['role_sel']:+.4f} z={h31['z_vs_allheads']:+.2f} "
            f"rank {h31['rank']}/{h31['of']}  (>0 & outlier => role-driven; <0 => recency)")
    log(f"  necessity:   H31@L27 ablation mismatch-drop z={z_h31:+.2f} vs random-head null; "
        f"named_all z={z_set:+.2f} vs matched-set null")
    log("  TYPED if role_sel>0 & outlier & ablation-z>>0; POSITIONAL if role_sel<=0 & z~0.")

    results = {
        "audit": "4-typed-binding", "model": args.model, "layers": layers,
        "n_heads": n_heads, "head_dim": head_dim, "n_stimuli": len(items),
        "selectivity": sel,
        "ablation": {"baseline": base, "named": named_res, "null": null,
                     "z_h31_vs_single": z_h31, "z_namedall_vs_set": z_set},
    }
    out_dir = _PROJECT_ROOT / "results" / "attention-typed-binding"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{args.model.replace('/', '_')}.json"
    with open(out_path, "w") as f:
        json.dump(results, f, indent=2, default=str)
    log(f"\n  saved -> {out_path}\n{'='*70}\n  DONE\n{'='*70}\n")


if __name__ == "__main__":
    main()
```

### Thinking

 I'm designing the fifth audit around the binding schedule claim—that subject binding peaks at layer 27, object binding at layer 30, and coreference resolution at layer 33. The core assertion is that this depth ordering reflects the actual reduction schedule, with subjects binding before objects. I need to identify what confound might be driving this pattern.

The key insight from audit #4 is that raw attention weights are dominated by recency, so audit #5 must carefully isolate whether the schedule claim is really about depth-ordered binding peaks across dependency types, or just a generic property of how attention distributes across layers. I'm decomposing the schedule into three testable predictions: subject-to-verb binding peaks at L27, object-to-verb at L30, and pronoun-to-antecedent at L33, with the ordering subject_peak < object_peak < coref_peak.

For controls, I'm planning a multi-part approach: generate large, varied corpora for each dependency type and measure binding attention at every layer to build curves with bootstrap confidence intervals; test whether the observed peak-layer ordering is significant or would emerge randomly; match linear distances across dependency types to rule out generic depth-by-distance effects; and run lightweight causal ablations on the named heads to see if they specifically hurt their corresponding dependency readouts. The focused experiment will have two parts: a representational schedule profile with random-pair baselines and ordering p-values, followed by a causal component testing whether ablating layer-specific heads breaks their predicted dependency types. ablation sweep of the named heads using subject-verb agreement as readout is only valid for subj. For a true "schedule" causal test I'd want each dependency's readout, but obj and coref readouts are hard to make clean and batchable in the time I have. So I'll keep the causal part focused on subject (reusing #4's result) and make the novel contribution of #5 the representational schedule across many sentences with proper null controls.

For the causal test, I'll ablate each layer's subject-specific heads and measure subject-verb agreement — checking whether L27 (the "subject" layer) is uniquely necessary compared to L30/L33. If the schedule is real, ablating L27-subject-heads should hurt agreement more than ablating the other layers' heads.

I'm setting up the task list and script now, running it in tmux since loading the 8B model and computing attention across all 36 layers over many sentences will take more than a couple minutes. I need to cap sentences to around 60-100 per type to keep memory reasonable on the 480G unified memory setup. For the coref readout, I'll use simpler constructions like "The {noun} ran because it was {adj}" where "it" has a single clear antecedent, then measure attention from "it" back to the subject noun. For subject-verb agreement, I'll measure the verb's attention back to the subject.

Now I'm building the stimuli and metrics. I'll measure raw max-head binding (what the schedule claim used) plus a position control: comparing attention to the true head versus attention to a random content word at a matched distance. This shows whether the dependent specifically attends to its grammatical head rather than just any content word. I'll compute binding_raw and binding_vs_random across layers and sentence types, plus a null curve from random dependent-head pairs.

Writing the analysis script...

## Assistant

I have everything I need. Audit #5 targets the **binding schedule** claim from `binding-graph-trace.md` (Findings 4 & 7, Implication 2): *subject-binding peaks at L27 (H31), object-binding at L30 (H03/13/15), coreference at L33 (H06/07) — "the depth ordering IS the reduction schedule."* The confound: 14 cherry-picked hand-annotated probes. The #4 caveat already showed these weights are recency-dominated; #5's distinct question is whether the **depth ordering** survives many sentences + a null, or is an artifact of the chosen examples.

Let me set up the plan.

### Thinking

 I'm setting up the script based on the earlier harness structure. For the stimuli, I need to carefully define how attention flows: in the subject-to-verb case, the verb token attends back to the noun since it comes after, while for object-to-verb, I'm measuring attention from the verb across a longer dependency chain that includes the object.

For the null baseline, I'll use random content token pairs sampled from the same sentences, matched by distance, to see if attention peaks at certain layers just as a function of depth rather than actual binding. I'll capture full attention across all 36 layers once per sentence, then compute both raw attention weights and a role-selective measure that subtracts attention to other content positions.

The causal part will reuse the ablation approach from the earlier harness, testing whether ablating specific heads at the predicted peak layers actually disrupts subject-verb agreement, which should reveal whether the schedule reflects real causal structure or just correlations.

## Assistant

Now I'll write the control script, modeled on the #4 harness for infra consistency.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Audit #5 — Is the binding SCHEDULE real, or 14 cherry-picked probes?\n\nThe claim (`binding-graph-trace.md`, Findings 4 & 7, Implication 2):\n  there is a depth-ordered \"reduction schedule\" --\n    L27  subject -> verb   binding peaks (H31, 0.82)\n    L30  object  -> verb   binding peaks (H03/H13/H15, 0.66-0.78)\n    L33  coreference       (pronoun -> antecedent) binds late (H06/H07)\n  i.e. peak_layer(subject) < peak_layer(object) < peak_layer(coref);\n  \"the depth ordering IS the reduction schedule -- subjects bind first.\"\n\nSuspected confound (audit-registry #5, failure modes #5 cherry-pick / #6 surface):\n  the schedule was read off 14 hand-annotated probes. Two ways it can be an\n  artifact:\n   (a) cherry-picked sentences/heads -- the ordering may not survive a large,\n       varied corpus or a bootstrap over sentences;\n   (b) generic attention-vs-depth -- ANY position pair (random content words at\n       matched distance) may show the same peak-layer profile, so the \"schedule\"\n       is a property of where attention is sharp by depth, not of binding/type.\n  And (audit #4, already established) the raw verb->subject weight is\n  recency/position-dominated -- so a schedule read off RAW attention may just\n  track linear distance.\n\nDiscriminating design\n---------------------\n  Many sentences, three dependency types, EVERY layer, with three controls:\n    PART 1  Schedule profile + nulls\n      For dep in {subj (verb->subject), obj (object->verb), coref (it->antecedent)},\n      N varied sentences. Per sentence, per layer L in 0..n_layers-1:\n        raw[L]      = max_head attn(dependent -> head)\n        role_sel[L] = max_head [ attn(dep->head) - mean attn(dep->other_content) ]\n                      (position control: specifically the grammatical head, not\n                       just any content word)\n      Aggregate mean curves; peak_layer = argmax. Schedule predicts\n      peak(subj) < peak(obj) < peak(coref). Tests:\n        * bootstrap B over sentences -> P(ordering holds) + per-type peak CIs.\n          (cherry-pick control: a real schedule is stable across resamples;\n           an artifact of 14 probes scatters.)\n        * RANDOM-PAIR null: per sentence, K random content (later->earlier) pairs;\n          their binding(layer) profile. If random pairs peak at the same layers,\n          the schedule is generic to depth, not binding.  (failure mode #6)\n        * distance report per type (exposes the position confound).\n    PART 2  Are the NAMED heads outliers? At each type's peak layer, rank all\n      heads by binding; where do H31@L27 / H03,13,15@L30 / H06,07@L33 sit, and\n      z vs the 32-head distribution.  (reuses audit #4 instrument)\n    PART 3  Causal schedule (subject readout): subject-verb agreement is/are\n      logit-diff; ablate L27-named vs L30-named vs L33-named vs random-head null.\n      Schedule predicts ablating the L27 (\"subject\") heads hurts subject\n      agreement MORE than L30/L33. (Extends audit #4's H31 null.)\n\nVerdict\n-------\n  SCHEDULE real : peak(subj)<peak(obj)<peak(coref) stable under bootstrap AND\n                  distinct from the random-pair null AND L27 ablation specifically\n                  carries subject agreement.\n  IMPOSED       : ordering unstable / matches random-pair depth profile /\n                  no layer-specific causal carrier. \"14 probes\", not a schedule.\n\nUsage:\n  uv run python scripts/experiments/binding_schedule_null.py \\\n    --model Qwen/Qwen3-8B --device mps\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\n\n# Named schedule heads from binding-graph-trace.md (the claim under audit)\nNAMED_SCHEDULE = {\"subj\": (27, [31]), \"obj\": (30, [3, 13, 15]), \"coref\": (33, [6, 7])}\n\n# ── Lexicon (single common tokens preferred; multi-token handled) ──────\nNOUNS = [\n    \"dog\", \"cat\", \"boy\", \"girl\", \"man\", \"woman\", \"bird\", \"horse\", \"teacher\",\n    \"doctor\", \"farmer\", \"pilot\", \"singer\", \"king\", \"queen\", \"soldier\", \"child\",\n    \"fox\", \"wolf\", \"lion\", \"nurse\", \"driver\", \"painter\", \"baker\",\n]\nVERBS_INTRANS = [\n    \"runs\", \"sleeps\", \"jumps\", \"sings\", \"barks\", \"waits\", \"smiles\", \"works\",\n    \"rests\", \"dreams\", \"laughs\", \"cries\", \"stumbles\", \"wanders\", \"hesitates\",\n]\nVERBS_TRANS = [\n    \"chased\", \"found\", \"watched\", \"kicked\", \"carried\", \"pushed\", \"bit\",\n    \"grabbed\", \"followed\", \"saw\", \"held\", \"dropped\", \"caught\", \"fed\",\n]\nOBJECTS = [\n    \"ball\", \"book\", \"apple\", \"stick\", \"rope\", \"bone\", \"toy\", \"box\", \"cup\",\n    \"flag\", \"drum\", \"kite\", \"leaf\", \"rock\", \"coin\", \"key\", \"hat\", \"shoe\",\n]\nADVS = [\"quietly\", \"slowly\", \"today\", \"again\", \"alone\", \"outside\", \"early\"]\nADJS = [\"tired\", \"hungry\", \"afraid\", \"happy\", \"cold\", \"lost\", \"calm\", \"brave\"]\n\n\ndef log(msg=\"\"):\n    print(msg, flush=True)\n\n\n# ── Stimuli ────────────────────────────────────────────────────────────\n\ndef build_stimuli(n_per, seed=7):\n    \"\"\"Return dict dep_type -> list of {sentence, dep_word, head_word}.\n\n    subj : \"The <noun> <vi> <adv>.\"          dep=verb   head=noun  (verb->subject)\n    obj  : \"The <n1> <vt> the <obj> <adv>.\"   dep=obj    head=verb  (object->verb)\n    coref: \"The <noun> <vi> because it was <adj>.\"  dep=\"it\" head=noun\n    \"\"\"\n    rng = np.random.default_rng(seed)\n    out = {\"subj\": [], \"obj\": [], \"coref\": []}\n    for _ in range(n_per):\n        n = rng.choice(NOUNS)\n        vi = rng.choice(VERBS_INTRANS)\n        adv = rng.choice(ADVS)\n        out[\"subj\"].append({\n            \"sentence\": f\"The {n} {vi} {adv}.\",\n            \"dep_word\": vi, \"head_word\": n})\n\n        n1 = rng.choice(NOUNS)\n        vt = rng.choice(VERBS_TRANS)\n        ob = rng.choice(OBJECTS)\n        adv2 = rng.choice(ADVS)\n        out[\"obj\"].append({\n            \"sentence\": f\"The {n1} {vt} the {ob} {adv2}.\",\n            \"dep_word\": ob, \"head_word\": vt})\n\n        n2 = rng.choice(NOUNS)\n        vi2 = rng.choice(VERBS_INTRANS)\n        adj = rng.choice(ADJS)\n        out[\"coref\"].append({\n            \"sentence\": f\"The {n2} {vi2} because it was {adj}.\",\n            \"dep_word\": \"it\", \"head_word\": n2})\n    return out\n\n\ndef token_positions(tokens, word):\n    \"\"\"Indices whose stripped lower text subword-matches `word` (alpha).\"\"\"\n    w = word.lower().strip()\n    hits = []\n    for i, t in enumerate(tokens):\n        s = t.strip().lower()\n        if s and s.isalpha() and (s == w or s in w or w in s):\n            hits.append(i)\n    return hits\n\n\ndef content_positions(tokens):\n    \"\"\"Alpha tokens, excluding obvious function words (the binding endpoints\n    we score separately are still allowed as 'content' for the random null).\"\"\"\n    stop = {\"the\", \"a\", \"an\", \"because\", \"was\", \"is\", \"are\", \"that\", \"near\"}\n    pos = []\n    for i, t in enumerate(tokens):\n        s = t.strip().lower()\n        if s and s.isalpha() and s not in stop:\n            pos.append(i)\n    return pos\n\n\ndef first_token_id(tokenizer, s):\n    ids = tokenizer(s, add_special_tokens=False)[\"input_ids\"]\n    return ids[0] if ids else None\n\n\n# ══════════════════════════════════════════════════════════════════════\n# PART 1 — schedule profile (per-sentence per-layer binding)\n# ══════════════════════════════════════════════════════════════════════\n\ndef schedule_profile(model, tokenizer, stim, n_layers, n_heads, device,\n                     k_random=4, seed=11):\n    \"\"\"Return per dep_type: arrays [n_sent, n_layers] of raw binding & role_sel,\n    plus the random-pair null curve and distance stats.\"\"\"\n    rng = np.random.default_rng(seed)\n    res = {}\n    rand_curves = []  # per-sentence random-pair max-head binding (any type)\n    for dep, items in stim.items():\n        raw_rows, role_rows, dists = [], [], []\n        for it in items:\n            enc = tokenizer(it[\"sentence\"], return_tensors=\"pt\")\n            ids = enc[\"input_ids\"].to(device)\n            toks = [tokenizer.decode(t) for t in enc[\"input_ids\"][0]]\n            dpos = token_positions(toks, it[\"dep_word\"])\n            hpos = token_positions(toks, it[\"head_word\"])\n            if not dpos or not hpos:\n                continue\n            d = dpos[-1]                       # dependent (later token)\n            h = max(p for p in hpos if p < d) if any(p < d for p in hpos) else None\n            if h is None:\n                continue\n            cpos = [p for p in content_positions(toks) if p < d and p != h]\n            dists.append(d - h)\n\n            with torch.no_grad():\n                out = model(ids, output_attentions=True, return_dict=True)\n            raw_L, role_L = np.zeros(n_layers), np.zeros(n_layers)\n            for li in range(n_layers):\n                A = out.attentions[li][0]      # (n_heads, seq, seq)\n                col_head = A[:, d, h]          # (n_heads,)\n                raw_L[li] = float(col_head.max())\n                if cpos:\n                    other = A[:, d, cpos].mean(dim=1)      # mean over other content\n                    role_L[li] = float((col_head - other).max())\n                else:\n                    role_L[li] = raw_L[li]\n                # random-pair null: a random (later->earlier) content pair\n                allc = content_positions(toks)\n                pairs = [(i, j) for i in allc for j in allc if j < i]\n                if pairs:\n                    for _ in range(k_random):\n                        i, j = pairs[int(rng.integers(0, len(pairs)))]\n                        rand_curves.append((li, float(A[:, i, j].max())))\n            raw_rows.append(raw_L)\n            role_rows.append(role_L)\n        res[dep] = {\n            \"raw\": np.array(raw_rows), \"role\": np.array(role_rows),\n            \"dist_mean\": float(np.mean(dists)) if dists else 0.0,\n            \"n\": len(raw_rows),\n        }\n    # collapse random-pair null into a per-layer mean curve\n    null_curve = np.zeros(n_layers)\n    cnt = np.zeros(n_layers)\n    for li, v in rand_curves:\n        null_curve[li] += v\n        cnt[li] += 1\n    null_curve = np.divide(null_curve, np.maximum(cnt, 1))\n    return res, null_curve\n\n\ndef bootstrap_ordering(res, metric=\"role\", B=1000, seed=3):\n    \"\"\"P(peak(subj) < peak(obj) < peak(coref)) over sentence bootstraps + peak CIs.\"\"\"\n    rng = np.random.default_rng(seed)\n    deps = [\"subj\", \"obj\", \"coref\"]\n    mats = {d: res[d][metric] for d in deps}\n    peaks = {d: [] for d in deps}\n    ok = 0\n    for _ in range(B):\n        pk = {}\n        for d in deps:\n            M = mats[d]\n            if len(M) == 0:\n                pk[d] = -1\n                continue\n            idx = rng.integers(0, len(M), len(M))\n            pk[d] = int(np.argmax(M[idx].mean(axis=0)))\n            peaks[d].append(pk[d])\n        if pk[\"subj\"] < pk[\"obj\"] < pk[\"coref\"]:\n            ok += 1\n    peak_ci = {d: [int(np.percentile(peaks[d], 5)), int(np.median(peaks[d])),\n                   int(np.percentile(peaks[d], 95))] if peaks[d] else [-1, -1, -1]\n               for d in deps}\n    return round(ok / B, 4), peak_ci\n\n\n# ══════════════════════════════════════════════════════════════════════\n# PART 2 — are the named heads outliers at the peak layer?\n# ══════════════════════════════════════════════════════════════════════\n\ndef head_ranks_at_peak(model, tokenizer, stim, peak_layer, dep, n_heads, device):\n    \"\"\"Mean per-head binding (dep->head) at a given layer; rank named heads.\"\"\"\n    per_head = np.zeros(n_heads)\n    cnt = 0\n    for it in stim[dep]:\n        enc = tokenizer(it[\"sentence\"], return_tensors=\"pt\")\n        ids = enc[\"input_ids\"].to(device)\n        toks = [tokenizer.decode(t) for t in enc[\"input_ids\"][0]]\n        dpos = token_positions(toks, it[\"dep_word\"])\n        hpos = token_positions(toks, it[\"head_word\"])\n        if not dpos or not hpos:\n            continue\n        d = dpos[-1]\n        hcands = [p for p in hpos if p < d]\n        if not hcands:\n            continue\n        h = max(hcands)\n        with torch.no_grad():\n            out = model(ids, output_attentions=True, return_dict=True)\n        per_head += out.attentions[peak_layer][0][:, d, h].float().cpu().numpy()\n        cnt += 1\n    per_head /= max(cnt, 1)\n    mu, sd = float(per_head.mean()), float(per_head.std() + 1e-9)\n    order = np.argsort(-per_head)\n    rank = {int(hh): int(np.where(order == hh)[0][0]) for hh in range(n_heads)}\n    named = NAMED_SCHEDULE[dep][1]\n    return {\n        \"layer\": peak_layer, \"n\": cnt,\n        \"allhead_mean\": round(mu, 4), \"allhead_std\": round(sd, 4),\n        \"top5\": [[int(order[j]), round(float(per_head[order[j]]), 4)] for j in range(5)],\n        \"named\": {int(hh): {\"binding\": round(float(per_head[hh]), 4),\n                            \"z\": round((per_head[hh] - mu) / sd, 2),\n                            \"rank\": rank[hh], \"of\": n_heads} for hh in named},\n    }\n\n\n# ══════════════════════════════════════════════════════════════════════\n# PART 3 — causal schedule (subject-verb agreement readout)\n# ══════════════════════════════════════════════════════════════════════\n\ndef build_agreement(seed=5):\n    rng = np.random.default_rng(seed)\n    subs = [(\"author\", \"authors\"), (\"key\", \"keys\"), (\"officer\", \"officers\"),\n            (\"pilot\", \"pilots\"), (\"farmer\", \"farmers\"), (\"singer\", \"singers\"),\n            (\"doctor\", \"doctors\"), (\"painter\", \"painters\")]\n    items = []\n    for (sg, pl) in subs:\n        for num in (\"sg\", \"pl\"):\n            head = sg if num == \"sg\" else pl\n            correct = \"is\" if num == \"sg\" else \"are\"\n            cloze = f\"The {head} near the table\"\n            items.append({\"cloze\": cloze, \"correct\": correct})\n    rng.shuffle(items)\n    return items\n\n\ndef ablation_hooks(model, cfg, head_dim):\n    handles = []\n    for li, heads in cfg.items():\n        o_proj = model.model.layers[li].self_attn.o_proj\n\n        def mk(hs):\n            def pre(module, args):\n                x = args[0].clone()\n                for h in hs:\n                    x[..., h * head_dim:(h + 1) * head_dim] = 0.0\n                return (x,)\n            return pre\n        handles.append(o_proj.register_forward_pre_hook(mk(list(heads))))\n    return handles\n\n\ndef agreement_logit_diff(model, tokenizer, items, device, cfg, head_dim, id_is, id_are):\n    handles = ablation_hooks(model, cfg, head_dim) if cfg else []\n    diffs = []\n    try:\n        for it in items:\n            ids = tokenizer(it[\"cloze\"], return_tensors=\"pt\")[\"input_ids\"].to(device)\n            with torch.no_grad():\n                logits = model(ids).logits[0, -1].float()\n            cid = id_is if it[\"correct\"] == \"is\" else id_are\n            wid = id_are if it[\"correct\"] == \"is\" else id_is\n            diffs.append(float(logits[cid] - logits[wid]))\n    finally:\n        for h in handles:\n            h.remove()\n    return float(np.mean(diffs)) if diffs else 0.0\n\n\n# ══════════════════════════════════════════════════════════════════════\n\ndef main():\n    p = argparse.ArgumentParser(description=__doc__,\n                                formatter_class=argparse.RawDescriptionHelpFormatter)\n    p.add_argument(\"--model\", default=\"Qwen/Qwen3-8B\")\n    p.add_argument(\"--device\", default=\"mps\")\n    p.add_argument(\"--n-per\", type=int, default=80, help=\"sentences per dependency type\")\n    p.add_argument(\"--boot\", type=int, default=1000)\n    p.add_argument(\"--n-random-heads\", type=int, default=24)\n    p.add_argument(\"--seed\", type=int, default=12)\n    args = p.parse_args()\n\n    log(f\"\\n{'='*70}\\n  AUDIT #5 — binding SCHEDULE: real depth-ordering or 14 probes?\\n{'='*70}\")\n    log(f\"  Model: {args.model}  Device: {args.device}  n_per={args.n_per}\")\n\n    dtype = torch.float16 if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"]) else torch.float32\n    log(f\"  Loading {args.model} ({dtype}) ...\")\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model, dtype=dtype, device_map=args.device, attn_implementation=\"eager\")\n    tokenizer = AutoTokenizer.from_pretrained(args.model)\n    if tokenizer.pad_token is None:\n        tokenizer.pad_token = tokenizer.eos_token\n    model.eval()\n\n    cfg = model.config\n    n_heads = cfg.num_attention_heads\n    n_layers = cfg.num_hidden_layers\n    head_dim = getattr(cfg, \"head_dim\", None) or (cfg.hidden_size // n_heads)\n    log(f\"  {n_layers} layers, {n_heads} Q heads, head_dim={head_dim}\")\n\n    stim = build_stimuli(args.n_per, seed=args.seed)\n    for d in stim:\n        log(f\"    {d:6s}: {len(stim[d])} sentences  e.g. \\\"{stim[d][0]['sentence']}\\\" \"\n            f\"(dep='{stim[d][0]['dep_word']}' head='{stim[d][0]['head_word']}')\")\n\n    # ── PART 1 ─────────────────────────────────────────────────────────\n    log(f\"\\n{'-'*70}\\n  PART 1 — schedule profile across all {n_layers} layers\\n{'-'*70}\")\n    t0 = time.time()\n    res, null_curve = schedule_profile(model, tokenizer, stim, n_layers, n_heads, args.device)\n    deps = [\"subj\", \"obj\", \"coref\"]\n    claim = {\"subj\": 27, \"obj\": 30, \"coref\": 33}\n    profile_out = {}\n    for d in deps:\n        raw_mean = res[d][\"raw\"].mean(axis=0)\n        role_mean = res[d][\"role\"].mean(axis=0)\n        pk_raw = int(np.argmax(raw_mean))\n        pk_role = int(np.argmax(role_mean))\n        profile_out[d] = {\n            \"n\": res[d][\"n\"], \"dist_mean\": round(res[d][\"dist_mean\"], 2),\n            \"peak_raw\": pk_raw, \"peak_role\": pk_role,\n            \"claimed_layer\": claim[d],\n            \"raw_at_claim\": round(float(raw_mean[claim[d]]), 4),\n            \"role_at_claim\": round(float(role_mean[claim[d]]), 4),\n            \"raw_curve\": [round(float(x), 4) for x in raw_mean],\n            \"role_curve\": [round(float(x), 4) for x in role_mean],\n        }\n        log(f\"  {d:6s} (n={res[d]['n']}, dist={res[d]['dist_mean']:.1f}): \"\n            f\"peak_raw=L{pk_raw}  peak_role=L{pk_role}  (claimed L{claim[d]})  \"\n            f\"role@claim={role_mean[claim[d]]:+.3f}\")\n    log(f\"  random-pair NULL peak: L{int(np.argmax(null_curve))} \"\n        f\"(max={null_curve.max():.3f})\")\n\n    p_raw, ci_raw = bootstrap_ordering(res, \"raw\", B=args.boot)\n    p_role, ci_role = bootstrap_ordering(res, \"role\", B=args.boot)\n    log(f\"\\n  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  raw={p_raw}  role={p_role}  \"\n        f\"(chance for a strict order = 1/6 = 0.167)\")\n    log(f\"  peak CIs (role) [p5,med,p95]:  \" +\n        \"  \".join(f\"{d}=L{ci_role[d]}\" for d in deps))\n    log(f\"  part 1 done in {time.time()-t0:.1f}s\")\n\n    # ── PART 2 ─────────────────────────────────────────────────────────\n    log(f\"\\n{'-'*70}\\n  PART 2 — are the named heads outliers at the CLAIMED layer?\\n{'-'*70}\")\n    t0 = time.time()\n    part2 = {}\n    for d in deps:\n        layer = claim[d]\n        hr = head_ranks_at_peak(model, tokenizer, stim, layer, d, n_heads, args.device)\n        part2[d] = hr\n        log(f\"  {d:6s} @L{layer}: all-head mean={hr['allhead_mean']:.4f} top5={hr['top5']}\")\n        for hh, s in hr[\"named\"].items():\n            log(f\"      NAMED H{hh}: binding={s['binding']:.4f}  z={s['z']:+.2f}  \"\n                f\"rank={s['rank']}/{s['of']}\")\n    log(f\"  part 2 done in {time.time()-t0:.1f}s\")\n\n    # ── PART 3 ─────────────────────────────────────────────────────────\n    log(f\"\\n{'-'*70}\\n  PART 3 — causal schedule (subject-verb agreement readout)\\n{'-'*70}\")\n    t0 = time.time()\n    id_is = first_token_id(tokenizer, \" is\")\n    id_are = first_token_id(tokenizer, \" are\")\n    agree = build_agreement()\n    base = agreement_logit_diff(model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)\n    log(f\"  baseline subject-verb logit-diff = {base:+.3f}\")\n    abl = {}\n    for d in deps:\n        li, heads = NAMED_SCHEDULE[d]\n        r = agreement_logit_diff(model, tokenizer, agree, args.device,\n                                 {li: heads}, head_dim, id_is, id_are)\n        abl[d] = {\"layer\": li, \"heads\": heads, \"logit_diff\": round(r, 4),\n                  \"drop\": round(base - r, 4)}\n        log(f\"  ablate {d:6s} (L{li} H{heads}): logit-diff={r:+.3f}  drop={base-r:+.3f}\")\n    # random-head null per claimed layer\n    rng = np.random.default_rng(args.seed)\n    null_drops = {}\n    for d in deps:\n        li = claim[d]\n        size = len(NAMED_SCHEDULE[d][1])\n        drops = []\n        for _ in range(args.n_random_heads):\n            hs = list(rng.choice(n_heads, size=size, replace=False))\n            r = agreement_logit_diff(model, tokenizer, agree, args.device,\n                                     {li: [int(x) for x in hs]}, head_dim, id_is, id_are)\n            drops.append(base - r)\n        null_drops[d] = {\"mean\": round(float(np.mean(drops)), 4),\n                         \"std\": round(float(np.std(drops)), 4),\n                         \"max\": round(float(np.max(drops)), 4),\n                         \"z_named\": round((abl[d][\"drop\"] - np.mean(drops)) /\n                                          (np.std(drops) + 1e-9), 2)}\n        log(f\"  L{li} random {size}-head null: drop mean={null_drops[d]['mean']:+.3f} \"\n            f\"std={null_drops[d]['std']:.3f}  ->  named z={null_drops[d]['z_named']:+.2f}\")\n    log(f\"  part 3 done in {time.time()-t0:.1f}s\")\n\n    # ── Verdict ────────────────────────────────────────────────────────\n    log(f\"\\n{'='*70}\\n  VERDICT\\n{'='*70}\")\n    log(f\"  ordering P(subj<obj<coref): raw={p_raw} role={p_role}  (chance 0.167)\")\n    log(f\"  random-pair null peaks at L{int(np.argmax(null_curve))} \"\n        f\"(schedule must beat this to be binding-specific)\")\n    log(f\"  causal: subject-agreement ablation z vs null  \" +\n        \"  \".join(f\"{d}=L{claim[d]}:{null_drops[d]['z_named']:+.2f}\" for d in deps))\n    log(\"  SCHEDULE real if ordering P>>0.167 AND distinct from random-pair null AND\")\n    log(\"  L27(subj) ablation z>>0 and > L30/L33; IMPOSED otherwise.\")\n\n    results = {\n        \"audit\": \"5-binding-schedule\", \"model\": args.model,\n        \"n_layers\": n_layers, \"n_heads\": n_heads, \"head_dim\": head_dim,\n        \"n_per\": args.n_per,\n        \"part1_profile\": profile_out,\n        \"random_pair_null_curve\": [round(float(x), 4) for x in null_curve],\n        \"random_pair_null_peak\": int(np.argmax(null_curve)),\n        \"ordering\": {\"p_raw\": p_raw, \"p_role\": p_role,\n                     \"ci_raw\": ci_raw, \"ci_role\": ci_role,\n                     \"chance\": round(1 / 6, 4)},\n        \"part2_head_ranks\": part2,\n        \"part3_causal\": {\"baseline\": round(base, 4), \"ablations\": abl,\n                         \"null\": null_drops},\n    }\n    out_dir = _PROJECT_ROOT / \"results\" / \"binding-schedule-null\"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f\"{args.model.replace('/', '_')}.json\"\n    with open(out_path, \"w\") as f:\n        json.dump(results, f, indent=2, default=str)\n    log(f\"\\n  saved -> {out_path}\\n{'='*70}\\n  DONE\\n{'='*70}\\n\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py
```

## Assistant

Let me lint and verify the script parses/builds stimuli correctly before launching the heavy run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/binding_schedule_null.py 2>&1 | tail -20; echo \"---compile---\"; uv run python -c \"import ast; ast.parse(open('scripts/experiments/binding_schedule_null.py').read()); print('parses OK')\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
473 |         log(f"  L{li} random {size}-head null: drop mean={null_drops[d]['mean']:+.3f} "
474 |             f"std={null_drops[d]['std']:.3f}  ->  named z={null_drops[d]['z_named']:+.2f}")
    |                                                                                         ^^^
475 |     log(f"  part 3 done in {time.time()-t0:.1f}s")
    |

F541 [*] f-string without any placeholders
   --> scripts/experiments/binding_schedule_null.py:482:9
    |
480 |     log(f"  random-pair null peaks at L{int(np.argmax(null_curve))} "
481 |         f"(schedule must beat this to be binding-specific)")
482 |     log(f"  causal: subject-agreement ablation z vs null  " +
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
483 |         "  ".join(f"{d}=L{claim[d]}:{null_drops[d]['z_named']:+.2f}" for d in deps))
484 |     log("  SCHEDULE real if ordering P>>0.167 AND distinct from random-pair null AND")
    |
help: Remove extraneous `f` prefix

Found 16 errors.
[*] 2 fixable with the `--fix` option.
---compile---
parses OK
```

### Thinking

 I'll check all 16 errors to see what we're dealing with—most are probably f-strings without placeholders—then run ruff with the auto-fix flag to clean up what it can handle automatically.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --fix scripts/experiments/binding_schedule_null.py 2>&1 | tail -25"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
457 |     rng = np.random.default_rng(args.seed)
    |

E501 Line too long (89 > 88)
   --> scripts/experiments/binding_schedule_null.py:466:89
    |
464 |             hs = list(rng.choice(n_heads, size=size, replace=False))
465 |             r = agreement_logit_diff(model, tokenizer, agree, args.device,
466 |                                      {li: [int(x) for x in hs]}, head_dim, id_is, id_are)
    |                                                                                         ^
467 |             drops.append(base - r)
468 |         null_drops[d] = {"mean": round(float(np.mean(drops)), 4),
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/binding_schedule_null.py:474:89
    |
472 |                                           (np.std(drops) + 1e-9), 2)}
473 |         log(f"  L{li} random {size}-head null: drop mean={null_drops[d]['mean']:+.3f} "
474 |             f"std={null_drops[d]['std']:.3f}  ->  named z={null_drops[d]['z_named']:+.2f}")
    |                                                                                         ^^^
475 |     log(f"  part 3 done in {time.time()-t0:.1f}s")
    |

Found 16 errors (2 fixed, 14 remaining).
```

### Thinking

 I'm seeing most of the remaining issues are line-too-long errors, so I should check the project's ruff configuration to understand what line length standard they're using, maybe by looking at how another script performs against the linter.

## Assistant

The remaining 14 are E501 line-length. Let me check whether the project actually enforces E501 (the #4 harness is the reference standard).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"===ruff config===\" && grep -A15 'tool.ruff' pyproject.toml 2>/dev/null; echo \"===#4 harness ruff===\" && uv run ruff check scripts/experiments/attention_typed_binding.py 2>&1 | tail -3"
}
```

**Summary:** $ echo "===ruff config===" && grep -A...

**Output:**
```
Exit code: 0
Stdout:
===ruff config===
[tool.ruff]
line-length = 88
target-version = "py312"
src = ["src", "tests"]

[tool.ruff.lint]
select = [
    "E",    # pycodestyle errors
    "W",    # pycodestyle warnings
    "F",    # pyflakes
    "I",    # isort
    "B",    # flake8-bugbear
    "UP",   # pyupgrade
    "RUF",  # ruff-specific
]

[tool.ruff.lint.per-file-ignores]
"tests/*" = ["B011"]  # allow assert False / etc. in tests

# ─────────────────────────── ty ─────────────────────────────
# ty is alpha; config schema is moving. Empty stanza pins the table so
# project-level config has a home when we need it.
[tool.ty]

# ─────────────────────────── pytest ─────────────────────────
[tool.pytest.ini_options]
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = ["-ra", "--strict-markers"]
===#4 harness ruff===
    |

Found 21 errors.
```

### Thinking

 The #4 harness has 21 E501 errors that were left as-is, so the project accepts line-too-long violations in experiment scripts. But the guidelines prefer fixing over suppressing, and line length is straightforward to address. Let me work through fixing those E501s and then review what other errors remain.

## Assistant

The #4 reference harness has 21 of the same. But per `λ lint(f). fix > suppress` — line-length is cheap. Let me see all remaining and fix them.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/binding_schedule_null.py 2>&1"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 1
Stdout:
scripts/experiments/binding_schedule_null.py:295:89: E501 Line too long (89 > 88)
scripts/experiments/binding_schedule_null.py:362:89: E501 Line too long (89 > 88)
scripts/experiments/binding_schedule_null.py:368:89: E501 Line too long (98 > 88)
scripts/experiments/binding_schedule_null.py:371:89: E501 Line too long (98 > 88)
scripts/experiments/binding_schedule_null.py:392:89: E501 Line too long (90 > 88)
scripts/experiments/binding_schedule_null.py:394:89: E501 Line too long (94 > 88)
scripts/experiments/binding_schedule_null.py:420:89: E501 Line too long (91 > 88)
scripts/experiments/binding_schedule_null.py:427:89: E501 Line too long (95 > 88)
scripts/experiments/binding_schedule_null.py:434:89: E501 Line too long (92 > 88)
scripts/experiments/binding_schedule_null.py:441:89: E501 Line too long (93 > 88)
scripts/experiments/binding_schedule_null.py:446:89: E501 Line too long (98 > 88)
scripts/experiments/binding_schedule_null.py:455:89: E501 Line too long (89 > 88)
scripts/experiments/binding_schedule_null.py:466:89: E501 Line too long (89 > 88)
scripts/experiments/binding_schedule_null.py:474:89: E501 Line too long (91 > 88)
Found 14 errors.
```

### Thinking

 I've got 14 E501 line length violations to address, each just slightly over the 88-character limit. Let me pull up those specific lines and work through the fixes.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "line_offset": 288,
  "limit": 12
}
```

**Summary:** Reading binding_schedule_null.py (288-300)

**Output:**
```
    order = np.argsort(-per_head)
    rank = {int(hh): int(np.where(order == hh)[0][0]) for hh in range(n_heads)}
    named = NAMED_SCHEDULE[dep][1]
    return {
        "layer": peak_layer, "n": cnt,
        "allhead_mean": round(mu, 4), "allhead_std": round(sd, 4),
        "top5": [[int(order[j]), round(float(per_head[order[j]]), 4)] for j in range(5)],
        "named": {int(hh): {"binding": round(float(per_head[hh]), 4),
                            "z": round((per_head[hh] - mu) / sd, 2),
                            "rank": rank[hh], "of": n_heads} for hh in named},
    }


[CONTENT TRUNCATED] Showing lines 289 to 300 of 510 total lines. Use line_offset=300 parameter to read more content.
```

### Thinking

 I'm looking at a bunch of scattered formatting issues across the file—mostly log lines with f-strings that need wrapping. There are about 14 of them scattered throughout, and while it's tedious to fix each one individually, that's the most straightforward approach. I'm starting with line 295 and the top5 line, though I'm noticing this aligns with how the reference harness was set up with similar errors as the project standard.

## Assistant

Let me view all offending lines together and fix them.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && for n in 295 362 368 371 392 394 420 427 434 441 446 455 466 474; do printf \"%s: \" \"$n\"; sed -n \"${n}p\" scripts/experiments/binding_schedule_null.py; done"
}
```

**Summary:** $ for n in 295 362 368 371 392 394 42...

**Output:**
```
Exit code: 0
Stdout:
295:         "top5": [[int(order[j]), round(float(per_head[order[j]]), 4)] for j in range(5)],
362:     p.add_argument("--n-per", type=int, default=80, help="sentences per dependency type")
368:     log(f"\n{'='*70}\n  AUDIT #5 — binding SCHEDULE: real depth-ordering or 14 probes?\n{'='*70}")
371:     dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
392:     log(f"\n{'-'*70}\n  PART 1 — schedule profile across all {n_layers} layers\n{'-'*70}")
394:     res, null_curve = schedule_profile(model, tokenizer, stim, n_layers, n_heads, args.device)
420:     log(f"\n  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  raw={p_raw}  role={p_role}  "
427:     log(f"\n{'-'*70}\n  PART 2 — are the named heads outliers at the CLAIMED layer?\n{'-'*70}")
434:         log(f"  {d:6s} @L{layer}: all-head mean={hr['allhead_mean']:.4f} top5={hr['top5']}")
441:     log(f"\n{'-'*70}\n  PART 3 — causal schedule (subject-verb agreement readout)\n{'-'*70}")
446:     base = agreement_logit_diff(model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)
455:         log(f"  ablate {d:6s} (L{li} H{heads}): logit-diff={r:+.3f}  drop={base-r:+.3f}")
466:                                      {li: [int(x) for x in hs]}, head_dim, id_is, id_are)
474:             f"std={null_drops[d]['std']:.3f}  ->  named z={null_drops[d]['z_named']:+.2f}")
```

## Assistant

Let me fix each of these. They're unique strings, so I can edit them precisely.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "        \"top5\": [[int(order[j]), round(float(per_head[order[j]]), 4)] for j in range(5)],",
  "new_content": "        \"top5\": [[int(order[j]), round(float(per_head[order[j]]), 4)]\n                 for j in range(5)],"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    p.add_argument(\"--n-per\", type=int, default=80, help=\"sentences per dependency type\")",
  "new_content": "    p.add_argument(\"--n-per\", type=int, default=80,\n                   help=\"sentences per dependency type\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    log(f\"\\n{'='*70}\\n  AUDIT #5 — binding SCHEDULE: real depth-ordering or 14 probes?\\n{'='*70}\")",
  "new_content": "    log(f\"\\n{'='*70}\\n  AUDIT #5 — binding SCHEDULE: \"\n        f\"real depth-ordering or 14 probes?\\n{'='*70}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    dtype = torch.float16 if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"]) else torch.float32",
  "new_content": "    dtype = (torch.float16 if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"])\n             else torch.float32)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    log(f\"\\n{'-'*70}\\n  PART 1 — schedule profile across all {n_layers} layers\\n{'-'*70}\")\n    t0 = time.time()\n    res, null_curve = schedule_profile(model, tokenizer, stim, n_layers, n_heads, args.device)",
  "new_content": "    log(f\"\\n{'-'*70}\\n  PART 1 — schedule profile across all \"\n        f\"{n_layers} layers\\n{'-'*70}\")\n    t0 = time.time()\n    res, null_curve = schedule_profile(\n        model, tokenizer, stim, n_layers, n_heads, args.device)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    log(f\"\\n  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  raw={p_raw}  role={p_role}  \"",
  "new_content": "    log(f\"\\n  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  \"\n        f\"raw={p_raw}  role={p_role}  \""
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    log(f\"\\n{'-'*70}\\n  PART 2 — are the named heads outliers at the CLAIMED layer?\\n{'-'*70}\")",
  "new_content": "    log(f\"\\n{'-'*70}\\n  PART 2 — are the named heads outliers \"\n        f\"at the CLAIMED layer?\\n{'-'*70}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "        log(f\"  {d:6s} @L{layer}: all-head mean={hr['allhead_mean']:.4f} top5={hr['top5']}\")",
  "new_content": "        log(f\"  {d:6s} @L{layer}: all-head mean={hr['allhead_mean']:.4f} \"\n            f\"top5={hr['top5']}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    log(f\"\\n{'-'*70}\\n  PART 3 — causal schedule (subject-verb agreement readout)\\n{'-'*70}\")",
  "new_content": "    log(f\"\\n{'-'*70}\\n  PART 3 — causal schedule \"\n        f\"(subject-verb agreement readout)\\n{'-'*70}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "    base = agreement_logit_diff(model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)",
  "new_content": "    base = agreement_logit_diff(\n        model, tokenizer, agree, args.device, {}, head_dim, id_is, id_are)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "        log(f\"  ablate {d:6s} (L{li} H{heads}): logit-diff={r:+.3f}  drop={base-r:+.3f}\")",
  "new_content": "        log(f\"  ablate {d:6s} (L{li} H{heads}): \"\n            f\"logit-diff={r:+.3f}  drop={base-r:+.3f}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "            r = agreement_logit_diff(model, tokenizer, agree, args.device,\n                                     {li: [int(x) for x in hs]}, head_dim, id_is, id_are)",
  "new_content": "            r = agreement_logit_diff(\n                model, tokenizer, agree, args.device,\n                {li: [int(x) for x in hs]}, head_dim, id_is, id_are)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "            f\"std={null_drops[d]['std']:.3f}  ->  named z={null_drops[d]['z_named']:+.2f}\")",
  "new_content": "            f\"std={null_drops[d]['std']:.3f}  -> \"\n            f\"named z={null_drops[d]['z_named']:+.2f}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Thinking

 I've got 13 edits done but need one more to reach 14. Let me run ruff again to make sure everything's clean, then do a quick test of the stimuli and positions functions without actually loading the model.

## Assistant

Now re-lint clean and smoke-test the stimuli/position logic (CPU, no model load) to catch bugs before the heavy run.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/binding_schedule_null.py 2>&1 | tail -5; echo \"===smoke===\"; uv run python -c \"\nimport sys; sys.argv=['x']\nimport importlib.util\nspec=importlib.util.spec_from_file_location('m','scripts/experiments/binding_schedule_null.py')\nm=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)\nfrom transformers import AutoTokenizer\ntok=AutoTokenizer.from_pretrained('Qwen/Qwen3-8B')\nstim=m.build_stimuli(3, seed=12)\nfor d,items in stim.items():\n    it=items[0]\n    enc=tok(it['sentence'], return_tensors='pt')\n    toks=[tok.decode(t) for t in enc['input_ids'][0]]\n    dpos=m.token_positions(toks, it['dep_word'])\n    hpos=m.token_positions(toks, it['head_word'])\n    cpos=m.content_positions(toks)\n    print(f'{d}: \\\"{it[\\\"sentence\\\"]}\\\"')\n    print(f'   toks={toks}')\n    print(f'   dep={it[\\\"dep_word\\\"]}@{dpos} head={it[\\\"head_word\\\"]}@{hpos} content={cpos}')\n\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stderr:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Stdout:
All checks passed!
===smoke===
subj: "The queen sings early."
   toks=['The', ' queen', ' sings', ' early', '.']
   dep=sings@[2] head=queen@[1] content=[1, 2, 3]
obj: "The painter chased the stick slowly."
   toks=['The', ' painter', ' chased', ' the', ' stick', ' slowly', '.']
   dep=stick@[4] head=chased@[2] content=[1, 2, 4, 5]
coref: "The man rests because it was afraid."
   toks=['The', ' man', ' rests', ' because', ' it', ' was', ' afraid', '.']
   dep=it@[4] head=man@[1] content=[1, 2, 4, 6]
```

### Thinking

 The dependency parsing is working correctly across all three test cases—the subject and object dependencies are properly linking back to their heads, and the coreference resolution is correctly identifying the pronoun's antecedent. There's a subtle detail with coreference where the dependent token itself appears in the content positions, which needs special handling in the scheduling logic.

For the subject case, there's an interesting limitation: since the verb is the dependent and there's only the head noun before it, the role selection metric degenerates to the raw metric—there's no other content available to serve as a decoy. I could add a prepositional phrase to create a meaningful position control across all three dependency types, but that would complicate the sentences and introduce additional confounds. Since the core claim relies on the raw binding metric at the peak layer, I'll keep the simpler design and treat role selection as a secondary metric where it's available for objects and coreference.

The random-pair null hypothesis remains the key control for distinguishing binding-specific effects from generic depth effects, and it applies uniformly across all three types. I'll report the bootstrap ordering primarily on raw metrics for consistency, with role metrics as supplementary evidence.

The design is solid. I'm launching this in tmux with a runtime estimate of around 1700 forward passes total—roughly 3 to 6 minutes on the 8B model plus model loading, so definitely worth running in a separate session. The model should already be cached locally, so I don't expect token issues.

## Assistant

Smoke test confirms all three dependency types tokenize and locate correctly:
- **subj**: dep=verb→head=subject noun ✓
- **obj**: dep=object→head=verb ✓
- **coref**: dep="it"→head=antecedent noun ✓

Lint clean. Task 1 done. Launching the run in `main:2` so you can watch live.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && mkdir -p results/binding-schedule-null && tmux send-keys -t main:2 \"uv run python scripts/experiments/binding_schedule_null.py --model Qwen/Qwen3-8B --device mps 2>&1 | tee results/binding-schedule-null/run.log\" Enter && sleep 3 && echo \"launched\""
}
```

**Summary:** $ mkdir -p results/binding-schedule-n...

**Output:**
```
Exit code: 0
Stdout:
launched
```

## Assistant

Let me verify it's actually running (one read, per async discipline).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 20 && tmux capture-pane -p -t main:2 | grep -v '^$' | tail -15"
}
```

**Summary:** $ sleep 20 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
----------------------------------------------------------------------
  PART 1 — schedule profile across all 36 layers
----------------------------------------------------------------------
  subj   (n=80, dist=1.3): peak_raw=L6  peak_role=L6  (claimed L27)  role@claim=+0.189
  obj    (n=80, dist=2.0): peak_raw=L4  peak_role=L6  (claimed L30)  role@claim=+0.404
  coref  (n=80, dist=3.3): peak_raw=L6  peak_role=L6  (claimed L33)  role@claim=+0.042
  random-pair NULL peak: L0 (max=0.694)
  bootstrap P(peak(subj)<peak(obj)<peak(coref)):  raw=0.0  role=0.0  (chance for a strict order = 1/6 = 0.167)
  peak CIs (role) [p5,med,p95]:  subj=L[4, 6, 6]  obj=L[4, 6, 6]  coref=L[6, 6, 6]
  part 1 done in 20.6s
----------------------------------------------------------------------
  PART 2 — are the named heads outliers at the CLAIMED layer?
----------------------------------------------------------------------
  subj   @L27: all-head mean=0.0335 top5=[[12, 0.1219], [8, 0.1129], [29, 0.1082], [31, 0.1066], [9, 0.0773]]
      NAMED H31: binding=0.1066  z=+2.07  rank=3/32
```

### Thinking

 The analysis shows that all three dependency types actually peak at the same early layer around L4-L6, contradicting the claimed depth ordering at L27/L30/L33. The bootstrap results confirm this—the probability of the proposed schedule (subject < object < coreference) is essentially zero for both raw and role-based measures, meaning the dependencies don't follow the predicted hierarchical pattern at all. I'll wait for the full results to come back rather than checking repeatedly — the analysis should be done in about 90 seconds.

## Assistant

It's running and **PART 1 is already decisive**: all three dependency types peak at the *same* early layer (L4–L6), nowhere near the claimed L27/L30/L33, and bootstrap **P(subj<obj<coref) = 0.0** (raw and role; chance 0.167). The depth-ordered schedule does not survive 80 varied sentences. PART 2 shows H31@L27 is mildly elevated for subject (z=+2.07, rank 3/32) — consistent with #4. 

**ASYNC: job verified running in main:2, PART1 done. Waiting for PART2/PART3 to finish (~1-2 min).** Let me wait for completion rather than poll.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 90 && if [ -f results/binding-schedule-null/Qwen_Qwen3-8B.json ]; then echo \"=== DONE — full log tail ===\"; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -32; else echo \"=== still running ===\"; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -8; fi"
}
```

**Summary:** $ sleep 90 && if [ -f results/binding...

**Output:**
```
Command timed out after 60000 ms
```

### Thinking

 The 90-second sleep exceeded the tool's timeout threshold, so I'll check what the current state is instead.

## Assistant

The shell timed out (90s > 60s default). Let me just read the current state.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && if [ -f results/binding-schedule-null/Qwen_Qwen3-8B.json ]; then echo \"=== DONE ===\"; else echo \"=== still running ===\"; fi; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -30"
}
```

**Summary:** $ if [ -f results/binding-schedule-nu...

**Output:**
```
Exit code: 0
Stdout:
=== DONE ===
  L27 random 1-head null: drop mean=+0.004 std=0.067  -> named z=-0.32
  L30 random 3-head null: drop mean=-0.009 std=0.049  -> named z=+0.35
  L33 random 2-head null: drop mean=-0.014 std=0.028  -> named z=+0.30
  part 3 done in 40.7s
======================================================================
  VERDICT
======================================================================
  ordering P(subj<obj<coref): raw=0.0 role=0.0  (chance 0.167)
  random-pair null peaks at L0 (schedule must beat this to be binding-specific)
  causal: subject-agreement ablation z vs null  subj=L27:-0.32  obj=L30:+0.35  coref=L33:+0.30
  SCHEDULE real if ordering P>>0.167 AND distinct from random-pair null AND
  L27(subj) ablation z>>0 and > L30/L33; IMPOSED otherwise.
  saved -> /Users/mwhitford/src/verbum/results/binding-schedule-null/Qwen_Qwen3-8B.json
======================================================================
  DONE
======================================================================
uv run python scripts/experiments/binding_schedule_null.py --model  --device   42.75s user 44.49s system 115% cpu 1:15.5
0 total
tee results/binding-schedule-null/run.log  0.00s user 0.00s system 0% cpu 1:15.50 total
[26-06-09][9:15:53][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

 I need to review the complete JSON output to extract the PART2 results, since I only caught one entry so far.

## Assistant

Complete. Let me read the full result JSON to capture PART 2 (head ranks at all three claimed layers) before writing up.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nr=json.load(open('results/binding-schedule-null/Qwen_Qwen3-8B.json'))\nprint('=== PART1 peaks ===')\nfor d,v in r['part1_profile'].items():\n    print(f\\\"  {d:6s}: peak_raw=L{v['peak_raw']} peak_role=L{v['peak_role']} claimed=L{v['claimed_layer']} dist={v['dist_mean']} raw@claim={v['raw_at_claim']} role@claim={v['role_at_claim']}\\\")\nprint('  null peak L', r['random_pair_null_peak'])\nprint('  ordering', r['ordering'])\nprint('=== PART2 named-head ranks at CLAIMED layer ===')\nfor d,v in r['part2_head_ranks'].items():\n    print(f\\\"  {d:6s} @L{v['layer']}: allhead_mean={v['allhead_mean']} top5={v['top5']}\\\")\n    for hh,s in v['named'].items():\n        print(f\\\"      H{hh}: binding={s['binding']} z={s['z']} rank={s['rank']}/{s['of']}\\\")\nprint('=== PART3 causal ===')\nc=r['part3_causal']; print('  baseline', c['baseline'])\nfor d,v in c['ablations'].items(): print(f\\\"  ablate {d}: L{v['layer']} H{v['heads']} drop={v['drop']}\\\")\nfor d,v in c['null'].items(): print(f\\\"  null {d}: mean={v['mean']} std={v['std']} z_named={v['z_named']}\\\")\n# peak of raw curve location + value for context\nfor d,v in r['part1_profile'].items():\n    rc=v['raw_curve']; import numpy as np\n    print(f\\\"  {d} raw L27/30/33 = {rc[27]:.3f}/{rc[30]:.3f}/{rc[33]:.3f}  maxval={max(rc):.3f}@L{rc.index(max(rc))}\\\")\n\""
}
```

**Summary:** $ uv run python -c " import json r=js...

**Output:**
```
Exit code: 0
Stdout:
=== PART1 peaks ===
  subj  : peak_raw=L6 peak_role=L6 claimed=L27 dist=1.3 raw@claim=0.2044 role@claim=0.1894
  obj   : peak_raw=L4 peak_role=L6 claimed=L30 dist=2.0 raw@claim=0.424 role@claim=0.4041
  coref : peak_raw=L6 peak_role=L6 claimed=L33 dist=3.3 raw@claim=0.0972 role@claim=0.0423
  null peak L 0
  ordering {'p_raw': 0.0, 'p_role': 0.0, 'ci_raw': {'subj': [4, 6, 6], 'obj': [4, 4, 6], 'coref': [6, 6, 6]}, 'ci_role': {'subj': [4, 6, 6], 'obj': [4, 6, 6], 'coref': [6, 6, 6]}, 'chance': 0.1667}
=== PART2 named-head ranks at CLAIMED layer ===
  subj   @L27: allhead_mean=0.0335 top5=[[12, 0.1219], [8, 0.1129], [29, 0.1082], [31, 0.1066], [9, 0.0773]]
      H31: binding=0.1066 z=2.07 rank=3/32
  obj    @L30: allhead_mean=0.0512 top5=[[3, 0.3794], [13, 0.197], [20, 0.1763], [15, 0.1494], [12, 0.1435]]
      H3: binding=0.3794 z=4.09 rank=0/32
      H13: binding=0.197 z=1.82 rank=1/32
      H15: binding=0.1494 z=1.22 rank=3/32
  coref  @L33: allhead_mean=0.0098 top5=[[6, 0.0766], [7, 0.0673], [8, 0.0227], [11, 0.0131], [4, 0.0116]]
      H6: binding=0.0766 z=3.97 rank=0/32
      H7: binding=0.0673 z=3.42 rank=1/32
=== PART3 causal ===
  baseline 5.0791
  ablate subj: L27 H[31] drop=-0.0176
  ablate obj: L30 H[3, 13, 15] drop=0.0078
  ablate coref: L33 H[6, 7] drop=-0.0059
  null subj: mean=0.0037 std=0.0668 z_named=-0.32
  null obj: mean=-0.0091 std=0.0486 z_named=0.35
  null coref: mean=-0.0142 std=0.0275 z_named=0.3
  subj raw L27/30/33 = 0.204/0.267/0.079  maxval=0.974@L6
  obj raw L27/30/33 = 0.316/0.424/0.115  maxval=0.825@L4
  coref raw L27/30/33 = 0.090/0.099/0.097  maxval=0.830@L6
```

### Thinking

 Looking at the audit results, the depth-ordered schedule hypothesis is completely refuted—all three dependency types peak at the same early layer rather than following the predicted ordering, with a probability of zero compared to the expected 0.167 by chance.

However, there's a real signal underneath: the named heads genuinely are local outliers at their claimed layers (object heads at L30 rank as the top binding heads with z-scores up to +4.09, coref heads at L33 are the top two with z up to +3.97), so the original observation wasn't hallucinating the head identities. The problem is conflating "local outlier at a non-peak layer" with "a depth-ordered reduction schedule," and the causal ablations show these heads don't actually carry the dependency—ablating them has negligible effect (|z| ≤ 0.35), consistent with the earlier finding that the attention is driven by recency and position, not syntactic type.

I need to update the audit registry and add a caveat to the binding-graph findings about this distinction between real substrate and over-read narrative. I need to finalize the backlog #5 entry by replacing the incomplete control section with a resolved version, then insert the session 206 worked examples section above the existing session 204 section in chronological order.

## Assistant

Complete and decisive. Let me capture the verdict, then update the registry, caveat the source page, and update state.

**Audit #5 verdict — the depth-ordered binding SCHEDULE is ❌ REFUTED**, but with the same meta-pattern shape (real heads, over-read story):

- **No schedule.** All three dependency types peak at the *same early layers* (raw max-head binding: subj L6=0.97, obj L4=0.83, coref L6=0.83), **not** the claimed monotone L27<L30<L33. At the claimed layers binding is far weaker (subj 0.20@L27, obj 0.42@L30, coref 0.10@L33). Bootstrap **P(subj<obj<coref)=0.0** (raw & role; chance 0.167).
- **No causal carrier.** Ablating named heads at each claimed layer barely moves subject-verb agreement (all |z|≤0.35 vs random-head null; L27/H31 even z=−0.32). Extends #4.
- **What survives:** the *head identities* are genuine **local** outliers at the named layers — L30 H3/H13/H15 are the top object heads (z=+4.09/+1.82/+1.22), L33 H6/H7 the top-2 coref heads (z=+3.97/+3.42), L27 H31 rank-3 (z=+2.07). But "local outlier at a non-peak layer" ≠ "a depth-ordered reduction schedule," and (per #4) that attention is recency/position, not typed, and not load-bearing.

Now updating the registry, source caveat, and state.Now the registry. Insert a session-206 worked-examples section and update backlog #5.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "### Worked examples (session 204)\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #4 attention = typed β-reduction; H31@L27 binds subject (0.82); H03/13/15@L30 bind object | CRITICAL | agreement-attraction (role⊥position): selectivity vs 32-head dist + recency baseline; head-ablation logit-diff vs random-head + matched-set nulls (`attention_typed_binding.py`) | ❌ REFUTED as localized — 0.82 is recency/position |",
  "new_content": "### Worked examples (session 206)\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #5 binding **schedule** — depth-ordered reduction: subj-binding peaks L27, obj L30, coref L33 (\"subjects bind first\") | med | 3 dep-types × 80 varied sentences, binding at **every** layer; bootstrap ordering P + per-type peak CIs; random-pair null; per-layer head-rank/z; causal subj-agreement ablation per layer vs random-head null (`binding_schedule_null.py`) | ❌ REFUTED — no depth schedule; all peak L4–L6; P(order)=0 |\n| #5 the named schedule heads exist at their layers | — | per-head binding rank/z at the claimed layer | ◐ REAL but **local** — outliers at non-peak layers, not a schedule |\n| #5 a claimed layer causally carries its dependency | — | head-ablation, subj-agreement logit-diff vs random-head null | ❌ no carrier — all \\|z\\|≤0.35 (L27/H31 z=−0.32) |\n\n**Verdict (s206): the \"two-phase binding schedule\" / depth-ordered reduction is\nREFUTED — there is no depth schedule.** Across 80 varied sentences per dependency\ntype, the dependent→head max-head attention peaks at the **same early layers for\nall three types** (raw: subj L6=0.974, obj L4=0.825, coref L6=0.830), **not** the\nclaimed monotone L27<L30<L33; at the claimed layers binding is far weaker (subj\n0.204@L27, obj 0.424@L30, coref 0.097@L33). The bootstrap ordering probability\n**P(peak(subj)<peak(obj)<peak(coref)) = 0.000** (raw and role-controlled; chance\nfor a strict order = 0.167) — the depth ordering is not merely weak, it is\n*absent* (all three peak together early; per-type peak CIs all L4–L6). A\nrandom-content-pair null peaks even earlier (L0, 0.694), confirming early layers\ncarry generically high *local/positional* attention (failure mode #6 surface) —\nso even the early peak is not shown to be binding-specific.\n\n**What survives (the substrate):** the *head identities* the original named are\ngenuine **local outliers at the named layers** — at L30 the named object-binders\n**are** the top heads (H3 z=+4.09 rank 0/32, H13 z=+1.82, H15 z=+1.22); at L33 the\nnamed coref heads **are** the top two (H6 z=+3.97 rank 0/32, H7 z=+3.42 rank 1/32);\nat L27 H31 is rank 3/32 (z=+2.07, top is H12). So the page did not invent the\nheads. But \"a head is a *local* outlier at layer L\" ≠ \"layer L is where that\ndependency is *resolved* in a depth-ordered schedule\" — binding attention is\n2–10× stronger at L4–L6 than at the named layers. **Causally there is no\nschedule:** ablating each layer's named heads barely moves subject-verb agreement\n(subj L27/H31 z=−0.32; obj L30 z=+0.35; coref L33 z=+0.30 — all within the\nrandom-head null), reproducing/extending audit #4 (H31@L27 is not load-bearing).\nSame meta-pattern (`audit-meta-pattern.md`): real heads, real *local* structure,\nover-read into a crisp discrete depth-ordered story. Caveat added to\n`binding-graph-trace.md` (Finding 4/7 + Implication 2). Results:\n`results/binding-schedule-null/Qwen_Qwen3-8B.json`.\n\n### Worked examples (session 204)\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #4 attention = typed β-reduction; H31@L27 binds subject (0.82); H03/13/15@L30 bind object | CRITICAL | agreement-attraction (role⊥position): selectivity vs 32-head dist + recency baseline; head-ablation logit-diff vs random-head + matched-set nulls (`attention_typed_binding.py`) | ❌ REFUTED as localized — 0.82 is recency/position |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

## Assistant

Now update backlog row #5 to RESOLVED.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med)\n- Evidence: showcased heads/weights on example sentences.\n- Suspected confound: cherry-picked heads/examples.\n- Control: does the schedule hold across **many** sentences with a perm-null, or only the showcased ones? Causal ablation of the specific head.",
  "new_content": "**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med) — ❌ **RESOLVED (s206): no depth schedule; heads are local outliers**\n- Evidence: showcased heads/weights on example sentences (14 hand-annotated probes).\n- Suspected confound: cherry-picked heads/examples; and (per #4) raw weight tracks recency/position not type.\n- Control: does the schedule hold across **many** sentences with a perm-null, or only the showcased ones? Causal ablation of the specific head.\n- **s206 result:** REFUTED. 80 varied sentences × 3 dep-types, binding measured at every layer: all three peak at the **same** early layers (subj L6 / obj L4 / coref L6), not the monotone L27<L30<L33; **bootstrap P(subj<obj<coref)=0.000** (chance 0.167); random-pair null peaks even earlier (L0) → early peak is generic local attention, not binding-specific (#6). **What survives:** named heads are real *local* outliers at their layers (L30 H3/H13/H15 top-3, z up to +4.09; L33 H6/H7 top-2, z +3.97/+3.42; L27 H31 rank 3, z +2.07) — but local-outlier-at-a-non-peak-layer ≠ a depth schedule, and no claimed layer causally carries its dependency (subj-agreement ablation \\|z\\|≤0.35). See worked-examples (s206) + `binding_schedule_null.py`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Thinking

 I'm adding a new caveat block to the binding-graph-trace.md file to document a schedule-related finding. Since there's already a caveat #4 at the top, I'll create a distinct #5 caveat block that references the schedule implications from Finding 4/7 and Implication 2, placing it right after the existing caveat section.

## Assistant

Now the source caveat on `binding-graph-trace.md` — add a #5 schedule caveat after the existing #4 block.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md",
  "original_content": "> agreement *without* the compile gate the original used — a gate-context re-test\n> is a named follow-up. See `audit-registry.md` #4 + `results/attention-typed-binding/`.",
  "new_content": "> agreement *without* the compile gate the original used — a gate-context re-test\n> is a named follow-up. See `audit-registry.md` #4 + `results/attention-typed-binding/`.\n\n> ⚠️ **Caveat (audit #5, session 206): the \"two-phase binding SCHEDULE\" /\n> depth-ordered reduction (Finding 4, Finding 7, Implication 2 — \"subjects bind\n> first at L27, objects second at L30, coref at L33; the depth ordering IS the\n> reduction schedule\") is REFUTED.** Across **80 varied sentences per dependency\n> type** (not 14 hand-annotated probes), the dependent→head max-head attention\n> peaks at the **same early layers for all three types** (subj L6=0.97, obj\n> L4=0.83, coref L6=0.83), **not** the claimed monotone L27<L30<L33; at the\n> claimed layers binding is 2–10× weaker (subj 0.20@L27, obj 0.42@L30, coref\n> 0.10@L33). Bootstrap **P(peak(subj)<peak(obj)<peak(coref)) = 0.000** (chance for\n> a strict order = 0.167) — there is no depth schedule. A random-content-pair null\n> peaks even earlier (L0), so the early peak is generic local/positional\n> attention, not binding-specific. **What survives:** the named heads ARE real\n> *local* outliers at their layers (L30 H3/H13/H15 are the top object heads, z up\n> to +4.09; L33 H6/H7 the top-2 coref heads, z +3.97/+3.42; L27 H31 rank 3/32, z\n> +2.07) — so the head identities below are not invented — but a *local outlier at\n> a non-peak layer* is not a depth-ordered schedule. Causally, ablating each\n> claimed layer's named heads barely moves subject-verb agreement (all |z|≤0.35;\n> L27/H31 z=−0.32), so no layer is the carrier (extends #4). **Read Findings 4 & 7\n> and Implication 2 as: real local binding heads, NOT a depth-ordered reduction\n> schedule.** See `audit-registry.md` #5 + `results/binding-schedule-null/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md.
```

## User

Was the claim not about semantics?  You did a non semantic test to refute a semantic claim?


### Thinking

 I'm reconsidering whether the binding schedule claim was really about semantic properties like typed β-reduction, and whether my test actually used a non-semantic instrument like positional attention weights. Looking back at audit #5, it targets binding schedule across specific layers with medium load, and the evidence was based on head weights from example sentences—but I need to check if that's actually testing what the claim asserts.

The original claim has two distinct parts: attention weights showing positional routing (which audit #4 already refuted as recency), and a semantic component where the head's output through unembedding produces the bound entity's identity—the actual value transfer step. The schedule (L27 for subject, L30 for object, L33 for coreference) is fundamentally about when semantic absorption happens, not just where attention concentrates.

What I actually tested was attention weight peaks across layers, which is the same positional/routing instrument that #4 already covered. I never measured whether the head output at each layer promotes the correct semantic content—the subject's identity at L27, the predicate at L30—which is what Finding 7 and Implication 4 really claim. So the user is right: I refuted the attention-weight schedule but left the semantic value-transfer schedule untested. The proper control would measure, across many sentences with permutation-null, whether each head's output contribution via logit-lens actually promotes the bound entity's token at the claimed layers in the claimed order.

I need to run that semantic instrument now—capturing per-head output at the dependent position, projecting through unembedding, and measuring whether the head word's token logit peaks at the predicted layers—before finalizing the verdict. Computing per-head contributions... Setting up hooks to capture the concatenated head outputs at each layer during the forward pass, then extracting each head's contribution to the residual stream by slicing and multiplying through the output projection weights. For the logit computation, I'll use the actual token id at the head position in the sentence (most faithful to what the model sees) and compare it against a control token from elsewhere in the sentence or a fixed out-of-vocabulary distractor.

The core metric is the margin between logits: what the head's output at the dependent position predicts for the true head token versus the control, which isolates whether this head specifically transfers semantic information about the grammatical head. I'll structure this in two parts—first a schedule curve showing when each named head peaks in semantic transfer across layers, then at the claimed layer, rank all 32 heads by their transfer strength to see if the named head stands out.

For the control, I'm weighing in-context other-content tokens (another noun in the sentence) versus out-of-context tokens, though in-context controls are cleaner since they test specificity within the actual context the model processes.

Writing the analysis script now...

## Assistant

You're right, and that's an important catch. Let me be precise about what I actually tested versus what the claim is.

**What the claim is.** `binding-graph-trace.md` Finding 7 / Implication 4 is fundamentally *semantic*: "Head output IS the reduction result — H31 at L27 produces '猫' at position 'runs' when it reads 'cat'... the VALUE TRANSFER step of β-reduction." The schedule (Implication 2) is a schedule of *semantic absorption*: the verb position **absorbs the subject's identity** at L27, the object absorbs the predicate at L30. The evidence was a **logit-lens on the head's output** (does it decode to the bound entity).

**What I tested.** Raw **attention-weight** concentration (dependent→head attention magnitude) per layer. That's the *positional/routing* instrument — essentially the same axis #4 already showed is recency-confounded. It tells you *where attention is sharp*, not *whether the head writes the correct entity's identity* to the dependent position.

**Why that's a real hole.** Early layers do local syntactic attention; semantic content often gets *written* into the residual at later layers. So "attention concentration peaks at L4–L6" does **not** refute "the subject's *identity* is absorbed at the verb position at L27." My early-peak finding is largely orthogonal to — and cannot refute — the semantic schedule. At best I refuted an *attention-weight* schedule (which mostly re-derives #4).

So I should **not** commit that overclaiming verdict. The faithful #5 control needs the **semantic instrument**: per-layer logit-lens on each head's *output contribution* at the dependent position — does it decode to the bound entity's token? — and does *that* peak in the L27→L30→L33 order. Let me build and run it. I'll hold the commit and revise the registry/caveat after.

### Thinking

 I'm setting up the semantic instrument by hooking into o_proj to capture the concatenated head outputs at each layer, then computing how each head's contribution flows through the projection matrix to influence the final logits via lm_head.

weight, and measuring the margin between the target and control token logits.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Audit #5 (SEMANTIC leg) — does the binding schedule hold for VALUE TRANSFER?\n\nThe attention-weight control (`binding_schedule_null.py`) tests routing/position:\nWHERE attention is sharp. But the claim (`binding-graph-trace.md`, Finding 7 /\nImplication 2/4) is SEMANTIC:\n\n  \"Head output IS the reduction result -- H31 at L27 produces '猫' at position\n   'runs' when it reads 'cat' ... the VALUE TRANSFER step of beta-reduction.\"\n  Schedule: the verb position ABSORBS THE SUBJECT'S IDENTITY at L27, the object\n  absorbs the predicate at L30, coref at L33 -- a depth ordering of SEMANTIC\n  absorption.  Evidence was a LOGIT-LENS on the head's OUTPUT.\n\nEarly attention concentration (L4-L6, found by the weight control) does NOT\nrefute a LATE semantic schedule: semantic content is often written into the\nresidual at deeper layers. So we need the SEMANTIC instrument the claim used.\n\nInstrument — per-head logit-lens of the output contribution\n-----------------------------------------------------------\nFor each dependency type and many sentences, at EVERY layer L, for the named\nhead h, take the head's contribution to the residual at the DEPENDENT position:\n\n    c_h = W_oproj[:, h*hd:(h+1)*hd] @ (attn_h value-weighted-sum at dep_pos)\n\n(captured via an o_proj forward-pre-hook), then logit-lens through lm_head and\nread the SEMANTIC MARGIN toward the bound entity:\n\n    m_h[L] = logit(token@head_pos) - logit(token@control_pos)\n           = lm_head[tok_head] . c_h  -  lm_head[tok_ctrl] . c_h\n\ni.e. does this head's output, at the dependent position, point to the GRAMMATICAL\nHEAD's token more than to another in-context content token? (control = earliest\nother content token; an in-context, distance/frequency-matched null.)\n\n  subj : dep=verb,   head=subject noun  -> does the verb absorb the subject identity?\n  obj  : dep=object, head=verb          -> does the object absorb the predicate?\n  coref: dep=\"it\",   head=antecedent    -> does the pronoun absorb the antecedent?\n\nTests\n-----\n  PART A  Semantic schedule: per-type semantic-transfer curve m_named[L] across\n          all layers; peak layer; bootstrap P(peak(subj)<peak(obj)<peak(coref))\n          + per-type peak CIs. Also the margin at the CLAIMED layer vs its peak.\n  PART B  Named-head specificity at the claimed layer: rank the named head's\n          semantic margin against all 32 heads (z, rank).\n\nVerdict\n-------\n  SEMANTIC schedule real : m_named>0 (entity is promoted), peaks in the claimed\n                           L27<L30<L33 order (bootstrap P >> 1/6), named head an\n                           outlier at its layer.\n  NOT a schedule         : margins ~0 / negative, or peak order not L27<L30<L33,\n                           or named head not special. Value-transfer schedule\n                           is over-read.\n\nUsage:\n  uv run python scripts/experiments/binding_schedule_semantic.py \\\n    --model Qwen/Qwen3-8B --device mps\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\n\nNAMED_SCHEDULE = {\"subj\": (27, [31]), \"obj\": (30, [3, 13, 15]), \"coref\": (33, [6, 7])}\n\nNOUNS = [\n    \"dog\", \"cat\", \"boy\", \"girl\", \"man\", \"woman\", \"bird\", \"horse\", \"teacher\",\n    \"doctor\", \"farmer\", \"pilot\", \"singer\", \"king\", \"queen\", \"soldier\", \"child\",\n    \"fox\", \"wolf\", \"lion\", \"nurse\", \"driver\", \"painter\", \"baker\",\n]\nVERBS_INTRANS = [\n    \"runs\", \"sleeps\", \"jumps\", \"sings\", \"barks\", \"waits\", \"smiles\", \"works\",\n    \"rests\", \"dreams\", \"laughs\", \"cries\", \"stumbles\", \"wanders\", \"hesitates\",\n]\nVERBS_TRANS = [\n    \"chased\", \"found\", \"watched\", \"kicked\", \"carried\", \"pushed\", \"bit\",\n    \"grabbed\", \"followed\", \"saw\", \"held\", \"dropped\", \"caught\", \"fed\",\n]\nOBJECTS = [\n    \"ball\", \"book\", \"apple\", \"stick\", \"rope\", \"bone\", \"toy\", \"box\", \"cup\",\n    \"flag\", \"drum\", \"kite\", \"leaf\", \"rock\", \"coin\", \"key\", \"hat\", \"shoe\",\n]\nADVS = [\"quietly\", \"slowly\", \"today\", \"again\", \"alone\", \"outside\", \"early\"]\nADJS = [\"tired\", \"hungry\", \"afraid\", \"happy\", \"cold\", \"lost\", \"calm\", \"brave\"]\n\n\ndef log(msg=\"\"):\n    print(msg, flush=True)\n\n\ndef build_stimuli(n_per, seed=7):\n    rng = np.random.default_rng(seed)\n    out = {\"subj\": [], \"obj\": [], \"coref\": []}\n    for _ in range(n_per):\n        n = rng.choice(NOUNS)\n        vi = rng.choice(VERBS_INTRANS)\n        adv = rng.choice(ADVS)\n        out[\"subj\"].append({\"sentence\": f\"The {n} {vi} {adv}.\",\n                            \"dep_word\": vi, \"head_word\": n})\n        n1 = rng.choice(NOUNS)\n        vt = rng.choice(VERBS_TRANS)\n        ob = rng.choice(OBJECTS)\n        adv2 = rng.choice(ADVS)\n        out[\"obj\"].append({\"sentence\": f\"The {n1} {vt} the {ob} {adv2}.\",\n                          \"dep_word\": ob, \"head_word\": vt})\n        n2 = rng.choice(NOUNS)\n        vi2 = rng.choice(VERBS_INTRANS)\n        adj = rng.choice(ADJS)\n        out[\"coref\"].append({\"sentence\": f\"The {n2} {vi2} because it was {adj}.\",\n                            \"dep_word\": \"it\", \"head_word\": n2})\n    return out\n\n\ndef token_positions(tokens, word):\n    w = word.lower().strip()\n    hits = []\n    for i, t in enumerate(tokens):\n        s = t.strip().lower()\n        if s and s.isalpha() and (s == w or s in w or w in s):\n            hits.append(i)\n    return hits\n\n\ndef content_positions(tokens):\n    stop = {\"the\", \"a\", \"an\", \"because\", \"was\", \"is\", \"are\", \"that\", \"near\"}\n    return [i for i, t in enumerate(tokens)\n            if t.strip().lower() and t.strip().lower().isalpha()\n            and t.strip().lower() not in stop]\n\n\nclass OProjTap:\n    \"\"\"Capture o_proj input (concatenated per-head outputs) at every layer.\"\"\"\n\n    def __init__(self, model, n_layers):\n        self.store = {}\n        self.handles = []\n        for li in range(n_layers):\n            o_proj = model.model.layers[li].self_attn.o_proj\n\n            def mk(idx):\n                def pre(module, args):\n                    self.store[idx] = args[0].detach()\n                    return None\n                return pre\n            self.handles.append(o_proj.register_forward_pre_hook(mk(li)))\n\n    def remove(self):\n        for h in self.handles:\n            h.remove()\n\n\ndef head_logits_at(model, store, li, pos, head_dim, n_heads, tok_ids):\n    \"\"\"Per-head logit of each token id in `tok_ids` from head output at `pos`.\n\n    Returns array [n_heads, len(tok_ids)].\n    \"\"\"\n    o_proj = model.model.layers[li].self_attn.o_proj\n    Wo = o_proj.weight                       # [hidden, n_heads*head_dim]\n    Wu = model.lm_head.weight                # [vocab, hidden]\n    x = store[li][0, pos]                    # [n_heads*head_dim]\n    out = np.zeros((n_heads, len(tok_ids)), dtype=np.float32)\n    Wu_sel = Wu[tok_ids].float()             # [n_tok, hidden]\n    for h in range(n_heads):\n        sl = slice(h * head_dim, (h + 1) * head_dim)\n        c_h = Wo[:, sl].float() @ x[sl].float()   # [hidden] contribution\n        out[h] = (Wu_sel @ c_h).detach().cpu().numpy()\n    return out\n\n\ndef semantic_profile(model, tokenizer, stim, n_layers, n_heads, head_dim, device):\n    \"\"\"Per dep_type: array [n_sent, n_layers] of named-head semantic margin, and\n    the per-layer all-head margins at the claimed layer (for ranking).\"\"\"\n    res = {}\n    tap = OProjTap(model, n_layers)\n    try:\n        for dep, items in stim.items():\n            named = NAMED_SCHEDULE[dep][1]\n            claimed = NAMED_SCHEDULE[dep][0]\n            rows = []                       # [n_sent, n_layers] named-head margin\n            allhead_at_claim = []           # [n_sent, n_heads] margin at claimed L\n            for it in items:\n                enc = tokenizer(it[\"sentence\"], return_tensors=\"pt\")\n                ids = enc[\"input_ids\"][0]\n                toks = [tokenizer.decode(t) for t in ids]\n                dpos = token_positions(toks, it[\"dep_word\"])\n                hpos = token_positions(toks, it[\"head_word\"])\n                if not dpos or not hpos:\n                    continue\n                d = dpos[-1]\n                hcands = [p for p in hpos if p < d]\n                if not hcands:\n                    continue\n                h_pos = max(hcands)\n                ctrl = [p for p in content_positions(toks)\n                        if p < d and p != h_pos]\n                if not ctrl:\n                    continue\n                c_pos = ctrl[0]\n                tok_head = int(ids[h_pos])\n                tok_ctrl = int(ids[c_pos])\n                with torch.no_grad():\n                    model(enc[\"input_ids\"].to(device))\n                # named-head margin per layer (mean over named heads)\n                m_L = np.zeros(n_layers)\n                for li in range(n_layers):\n                    hl = head_logits_at(model, tap.store, li, d, head_dim,\n                                        n_heads, [tok_head, tok_ctrl])\n                    margins = hl[:, 0] - hl[:, 1]          # [n_heads]\n                    m_L[li] = float(np.mean([margins[h] for h in named]))\n                    if li == claimed:\n                        allhead_at_claim.append(margins.copy())\n                rows.append(m_L)\n            res[dep] = {\n                \"margin\": np.array(rows),\n                \"allhead_at_claim\": np.array(allhead_at_claim),\n                \"claimed\": claimed, \"named\": named, \"n\": len(rows),\n            }\n    finally:\n        tap.remove()\n    return res\n\n\ndef bootstrap_ordering(res, B=1000, seed=3):\n    rng = np.random.default_rng(seed)\n    deps = [\"subj\", \"obj\", \"coref\"]\n    mats = {d: res[d][\"margin\"] for d in deps}\n    peaks = {d: [] for d in deps}\n    ok = 0\n    for _ in range(B):\n        pk = {}\n        for d in deps:\n            M = mats[d]\n            if len(M) == 0:\n                pk[d] = -1\n                continue\n            idx = rng.integers(0, len(M), len(M))\n            pk[d] = int(np.argmax(M[idx].mean(axis=0)))\n            peaks[d].append(pk[d])\n        if pk[\"subj\"] < pk[\"obj\"] < pk[\"coref\"]:\n            ok += 1\n    peak_ci = {d: [int(np.percentile(peaks[d], 5)), int(np.median(peaks[d])),\n                   int(np.percentile(peaks[d], 95))] if peaks[d] else [-1, -1, -1]\n               for d in deps}\n    return round(ok / B, 4), peak_ci\n\n\ndef main():\n    p = argparse.ArgumentParser(\n        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)\n    p.add_argument(\"--model\", default=\"Qwen/Qwen3-8B\")\n    p.add_argument(\"--device\", default=\"mps\")\n    p.add_argument(\"--n-per\", type=int, default=60)\n    p.add_argument(\"--boot\", type=int, default=1000)\n    p.add_argument(\"--seed\", type=int, default=12)\n    args = p.parse_args()\n\n    log(f\"\\n{'='*70}\\n  AUDIT #5 SEMANTIC — value-transfer schedule \"\n        f\"(logit-lens head output)\\n{'='*70}\")\n    log(f\"  Model: {args.model}  Device: {args.device}  n_per={args.n_per}\")\n\n    dtype = (torch.float16 if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"])\n             else torch.float32)\n    log(f\"  Loading {args.model} ({dtype}) ...\")\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model, dtype=dtype, device_map=args.device, attn_implementation=\"eager\")\n    tokenizer = AutoTokenizer.from_pretrained(args.model)\n    if tokenizer.pad_token is None:\n        tokenizer.pad_token = tokenizer.eos_token\n    model.eval()\n\n    cfg = model.config\n    n_heads = cfg.num_attention_heads\n    n_layers = cfg.num_hidden_layers\n    head_dim = getattr(cfg, \"head_dim\", None) or (cfg.hidden_size // n_heads)\n    log(f\"  {n_layers} layers, {n_heads} Q heads, head_dim={head_dim}\")\n\n    stim = build_stimuli(args.n_per, seed=args.seed)\n\n    log(f\"\\n{'-'*70}\\n  PART A — semantic value-transfer schedule\\n{'-'*70}\")\n    t0 = time.time()\n    res = semantic_profile(model, tokenizer, stim, n_layers, n_heads, head_dim,\n                           args.device)\n    deps = [\"subj\", \"obj\", \"coref\"]\n    claim = {\"subj\": 27, \"obj\": 30, \"coref\": 33}\n    profile = {}\n    for d in deps:\n        m = res[d][\"margin\"].mean(axis=0)\n        pk = int(np.argmax(m))\n        profile[d] = {\n            \"n\": res[d][\"n\"], \"peak_layer\": pk,\n            \"peak_margin\": round(float(m[pk]), 4),\n            \"claimed_layer\": claim[d],\n            \"margin_at_claim\": round(float(m[claim[d]]), 4),\n            \"margin_curve\": [round(float(x), 4) for x in m],\n        }\n        log(f\"  {d:6s} (n={res[d]['n']}): semantic peak=L{pk} \"\n            f\"(margin={m[pk]:+.3f})  margin@claimL{claim[d]}={m[claim[d]]:+.3f}  \"\n            f\"(>0 = head's output points to the bound entity)\")\n\n    p_ord, ci = bootstrap_ordering(res, B=args.boot)\n    log(f\"\\n  bootstrap P(sem-peak(subj)<obj<coref) = {p_ord}  (chance 0.167)\")\n    log(\"  peak CIs [p5,med,p95]: \" + \"  \".join(f\"{d}=L{ci[d]}\" for d in deps))\n    log(f\"  part A done in {time.time()-t0:.1f}s\")\n\n    log(f\"\\n{'-'*70}\\n  PART B — named-head specificity at CLAIMED layer\\n{'-'*70}\")\n    part_b = {}\n    for d in deps:\n        A = res[d][\"allhead_at_claim\"]          # [n_sent, n_heads]\n        if len(A) == 0:\n            continue\n        head_mean = A.mean(axis=0)\n        mu, sd = float(head_mean.mean()), float(head_mean.std() + 1e-9)\n        order = np.argsort(-head_mean)\n        rank = {int(h): int(np.where(order == h)[0][0]) for h in range(n_heads)}\n        named = res[d][\"named\"]\n        part_b[d] = {\n            \"layer\": claim[d], \"allhead_mean\": round(mu, 4),\n            \"top5\": [[int(order[j]), round(float(head_mean[order[j]]), 4)]\n                     for j in range(5)],\n            \"named\": {int(h): {\"margin\": round(float(head_mean[h]), 4),\n                               \"z\": round((head_mean[h] - mu) / sd, 2),\n                               \"rank\": rank[h], \"of\": n_heads} for h in named},\n        }\n        log(f\"  {d:6s} @L{claim[d]}: all-head mean margin={mu:+.4f} \"\n            f\"top5={part_b[d]['top5']}\")\n        for h, s in part_b[d][\"named\"].items():\n            log(f\"      NAMED H{h}: margin={s['margin']:+.4f}  z={s['z']:+.2f}  \"\n                f\"rank={s['rank']}/{s['of']}\")\n\n    log(f\"\\n{'='*70}\\n  VERDICT\\n{'='*70}\")\n    log(f\"  semantic ordering P(subj<obj<coref) = {p_ord}  (chance 0.167)\")\n    for d in deps:\n        log(f\"  {d:6s}: semantic peak L{profile[d]['peak_layer']} \"\n            f\"(claimed L{claim[d]});  margin@claim={profile[d]['margin_at_claim']:+.3f}\")\n    log(\"  SCHEDULE real if margins>0, peaks in L27<L30<L33 order (P>>0.167),\")\n    log(\"  named head an outlier at its layer; over-read otherwise.\")\n\n    results = {\n        \"audit\": \"5-binding-schedule-semantic\", \"model\": args.model,\n        \"n_layers\": n_layers, \"n_heads\": n_heads, \"head_dim\": head_dim,\n        \"n_per\": args.n_per,\n        \"partA_profile\": profile,\n        \"ordering\": {\"p\": p_ord, \"ci\": ci, \"chance\": round(1 / 6, 4)},\n        \"partB_head_specificity\": part_b,\n    }\n    out_dir = _PROJECT_ROOT / \"results\" / \"binding-schedule-semantic\"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f\"{args.model.replace('/', '_')}.json\"\n    with open(out_path, \"w\") as f:\n        json.dump(results, f, indent=2, default=str)\n    log(f\"\\n  saved -> {out_path}\\n{'='*70}\\n  DONE\\n{'='*70}\\n\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py
```

## Assistant

Lint + a quick correctness check of the per-head logit-lens mechanics (verify o_proj/lm_head shapes and that the decomposition sums correctly) on a tiny model-free assertion isn't possible without the model, so I'll verify shapes during a short smoke run. First lint:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/binding_schedule_semantic.py 2>&1 | tail -8"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
346 |         log(f"  {d:6s}: semantic peak L{profile[d]['peak_layer']} "
347 |             f"(claimed L{claim[d]});  margin@claim={profile[d]['margin_at_claim']:+.3f}")
    |                                                                                         ^
348 |     log("  SCHEDULE real if margins>0, peaks in L27<L30<L33 order (P>>0.167),")
349 |     log("  named head an outlier at its layer; over-read otherwise.")
    |

Found 1 error.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py",
  "original_content": "        log(f\"  {d:6s}: semantic peak L{profile[d]['peak_layer']} \"\n            f\"(claimed L{claim[d]});  margin@claim={profile[d]['margin_at_claim']:+.3f}\")",
  "new_content": "        log(f\"  {d:6s}: semantic peak L{profile[d]['peak_layer']} \"\n            f\"(claimed L{claim[d]}); \"\n            f\"margin@claim={profile[d]['margin_at_claim']:+.3f}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py.
```

### Thinking

 I need to verify the per-head decomposition is working correctly—specifically that summing the contributions across all heads matches the actual output projection. Rather than adding a sanity check to the script, I'll just run the full pipeline since it only takes a few minutes anyway and loads the model regardless. Let me make sure the mechanics are solid before moving forward.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/binding_schedule_semantic.py 2>&1 | tail -3 && echo \"===launch===\" && mkdir -p results/binding-schedule-semantic && tmux send-keys -t main:2 \"uv run python scripts/experiments/binding_schedule_semantic.py --model Qwen/Qwen3-8B --device mps 2>&1 | tee results/binding-schedule-semantic/run.log\" Enter && sleep 5 && echo launched"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
===launch===
launched
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 40 && tmux capture-pane -p -t main:2 | grep -v '^$' | tail -15"
}
```

**Summary:** $ sleep 40 && tmux capture-pane -p -t...

**Output:**
```
Exit code: 0
Stdout:
[26-06-09][9:15:53][mwhitford@olga][0][~/src/verbum][git:main]
λ uv run python scripts/experiments/binding_schedule_semantic.py --model Qwen/Qwen3-8B --device mps 2>&1 | tee results/b
inding-schedule-semantic/run.log
======================================================================
  AUDIT #5 SEMANTIC — value-transfer schedule (logit-lens head output)
======================================================================
  Model: Qwen/Qwen3-8B  Device: mps  n_per=60
  Loading Qwen/Qwen3-8B (torch.float16) ...
Loading weights: 100%|██████████| 399/399 [00:02<00:00, 166.66it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
  36 layers, 32 Q heads, head_dim=128
----------------------------------------------------------------------
  PART A — semantic value-transfer schedule
----------------------------------------------------------------------
```

### Thinking

 I'm running the first part of the logit-lens analysis across all 36 layers, computing per-head projections for 60 sentences with three different types. The computation involves matrix multiplications for each of the 32 heads per layer—specifically the output projection and language model head matmuls—which adds up to roughly 1,152 small operations per sentence across the full dataset.

## Assistant

Running, PART A in progress. **ASYNC: job verified running in main:2. Waiting for completion (~2-3 min for the per-head logit-lens sweep).**

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && sleep 55 && if [ -f results/binding-schedule-semantic/Qwen_Qwen3-8B.json ]; then echo DONE; else echo RUNNING; fi; tmux capture-pane -p -t main:2 | grep -v '^$' | tail -14"
}
```

**Summary:** $ sleep 55 && if [ -f results/binding...

**Output:**
```
Exit code: 0
Stdout:
DONE
  subj  : semantic peak L27 (claimed L27); margin@claim=+0.611
  obj   : semantic peak L32 (claimed L30); margin@claim=-0.047
  coref : semantic peak L27 (claimed L33); margin@claim=+0.198
  SCHEDULE real if margins>0, peaks in L27<L30<L33 order (P>>0.167),
  named head an outlier at its layer; over-read otherwise.
  saved -> /Users/mwhitford/src/verbum/results/binding-schedule-semantic/Qwen_Qwen3-8B.json
======================================================================
  DONE
======================================================================
uv run python scripts/experiments/binding_schedule_semantic.py --model   mps   25.11s user 57.80s system 133% cpu 1:02.0
9 total
tee results/binding-schedule-semantic/run.log  0.00s user 0.00s system 0% cpu 1:02.09 total
[26-06-09][9:23:00][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

 The semantic instrument reveals a much more nuanced picture than the attention weights alone—the subject peaks at layer 27 exactly as claimed, with a strong positive margin showing the verb's output genuinely points to the subject's identity, while the object peaks at layer 32 rather than the claimed 30, with a near-zero or slightly negative margin suggesting the object prediction is less clearly supported.

This semantic evidence substantially confirms Finding 7: the verb position's hidden state at layer 31 semantically binds to the subject at layer 27, which is strikingly different from what the attention-weight analysis suggested. Now I need to pull the full bootstrap ordering and head specificity numbers from the JSON to see the complete picture.

## Assistant

The semantic instrument tells a **very different story** than the attention-weight one — vindicating your pushback. Let me pull the full numbers.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport json\nr=json.load(open('results/binding-schedule-semantic/Qwen_Qwen3-8B.json'))\nprint('=== PART A semantic peaks ===')\nfor d,v in r['partA_profile'].items():\n    c=v['margin_curve']\n    print(f\\\"  {d:6s}: peak=L{v['peak_layer']} (margin={v['peak_margin']}) claimed=L{v['claimed_layer']} margin@claim={v['margin_at_claim']}  curve L25-34={[round(x,2) for x in c[25:35]]}\\\")\nprint('  ordering', r['ordering'])\nprint('=== PART B named-head specificity at claimed layer ===')\nfor d,v in r['partB_head_specificity'].items():\n    print(f\\\"  {d:6s} @L{v['layer']}: allhead_mean={v['allhead_mean']} top5={v['top5']}\\\")\n    for h,s in v['named'].items():\n        print(f\\\"      H{h}: margin={s['margin']} z={s['z']} rank={s['rank']}/{s['of']}\\\")\n\""
}
```

**Summary:** $ uv run python -c " import json r=js...

**Output:**
```
Exit code: 0
Stdout:
=== PART A semantic peaks ===
  subj  : peak=L27 (margin=0.6113) claimed=L27 margin@claim=0.6113  curve L25-34=[0.05, 0.03, 0.61, 0.1, 0.01, -0.02, 0.02, -0.14, -0.16, -0.13]
  obj   : peak=L32 (margin=0.2259) claimed=L30 margin@claim=-0.0467  curve L25-34=[0.0, -0.06, 0.01, -0.05, 0.01, -0.05, 0.04, 0.23, 0.02, -0.34]
  coref : peak=L27 (margin=0.2726) claimed=L33 margin@claim=0.1983  curve L25-34=[0.0, 0.04, 0.27, 0.1, -0.25, -0.08, -0.21, 0.0, 0.2, 0.16]
  ordering {'p': 0.191, 'ci': {'subj': [8, 27, 27], 'obj': [31, 32, 32], 'coref': [27, 27, 33]}, 'chance': 0.1667}
=== PART B named-head specificity at claimed layer ===
  subj   @L27: allhead_mean=0.122 top5=[[29, 2.1249], [7, 0.6472], [31, 0.6113], [11, 0.3854], [12, 0.3185]]
      H31: margin=0.6113 z=1.17 rank=2/32
  obj    @L30: allhead_mean=-0.0486 top5=[[0, 1.338], [11, 0.3974], [13, 0.3278], [28, 0.1781], [7, 0.1642]]
      H3: margin=-0.4625 z=-0.8 rank=29/32
      H13: margin=0.3278 z=0.73 rank=2/32
      H15: margin=-0.0055 z=0.08 rank=20/32
  coref  @L33: allhead_mean=0.032 top5=[[8, 5.4902], [22, 1.3524], [21, 0.9996], [9, 0.991], [30, 0.9312]]
      H6: margin=0.3384 z=0.22 rank=6/32
      H7: margin=0.0582 z=0.02 rank=12/32
```

### Thinking

 The semantic lens approach is giving me clearer results than the attention-weight analysis. The subject claim shows strong semantic vindication at layer 27, with a sharp peak in the margin curve centered right at that layer—a +0.611 advantage that stands out distinctly from the surrounding layers.

However, the broader schedule hypothesis still doesn't hold up. The subject and coreference peaks both cluster at layer 27 rather than spreading across the predicted sequence, and the object signal either weakens or drifts elsewhere entirely. The bootstrap probability for the ordered progression is essentially at chance levels, so the "two-phase reduction" narrative doesn't survive scrutiny.

What's important here is that the semantic instrument caught something the attention-weight test would have missed: the actual value transfer at the subject site is real and precisely localized, even though it doesn't fit into the larger schedule story. The attention-weight analysis alone would have suggested binding happens much earlier and dismissed the layer 27 claim entirely. This is a methodological insight worth preserving—the right measurement tool matters for testing semantic claims versus routing claims.

## Assistant

This is exactly the point you raised, and it changes the verdict materially. The **semantic** instrument recovers what the attention-weight test missed:

**subj — the headline H31@L27 "verb absorbs subject identity" claim is SEMANTICALLY REAL and sharply L27-localized.** Margin curve: L26=+0.03, **L27=+0.61**, L28=+0.10 — a clean spike *exactly* at the claimed layer; H31 z=+1.17, rank 2/32. Finding 7 is vindicated semantically. The attention-weight test's "peaks at L6" was the wrong instrument reading a routing signal, not the value transfer.

**But the SCHEDULE (the depth ordering) is still refuted, now on both instruments:**
- **obj** @L30: semantic margin = −0.05; named H3 rank **29/32** (anti-points); weak peak drifts to L32. (Caveat: my "object→verb-token" readout may mis-operationalize "absorbs predicate.")
- **coref**: margin +0.20 but **peaks at L27, not L33**; H6@L33 z=+0.22, rank 6/32 (not an outlier).
- **Ordering:** bootstrap P(sem-peak subj<obj<coref) = **0.191 ≈ chance (0.167)** — subj and coref both peak at L27, so there is no subjects-first depth schedule.

So the corrected #5: **the "two-phase reduction schedule" is refuted, but the single value-transfer site it's built on (H31@L27 = subject identity) is genuinely real and L27-localized.** Same meta-pattern with a sharper edge: the substrate is *more* real than my first test implied; the ordered three-phase story is the over-read. Let me rewrite the registry/caveat correctly (replacing my premature edits) before committing.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "### Worked examples (session 206)\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #5 binding **schedule** — depth-ordered reduction: subj-binding peaks L27, obj L30, coref L33 (\"subjects bind first\") | med | 3 dep-types × 80 varied sentences, binding at **every** layer; bootstrap ordering P + per-type peak CIs; random-pair null; per-layer head-rank/z; causal subj-agreement ablation per layer vs random-head null (`binding_schedule_null.py`) | ❌ REFUTED — no depth schedule; all peak L4–L6; P(order)=0 |\n| #5 the named schedule heads exist at their layers | — | per-head binding rank/z at the claimed layer | ◐ REAL but **local** — outliers at non-peak layers, not a schedule |\n| #5 a claimed layer causally carries its dependency | — | head-ablation, subj-agreement logit-diff vs random-head null | ❌ no carrier — all \\|z\\|≤0.35 (L27/H31 z=−0.32) |\n\n**Verdict (s206): the \"two-phase binding schedule\" / depth-ordered reduction is\nREFUTED — there is no depth schedule.** Across 80 varied sentences per dependency\ntype, the dependent→head max-head attention peaks at the **same early layers for\nall three types** (raw: subj L6=0.974, obj L4=0.825, coref L6=0.830), **not** the\nclaimed monotone L27<L30<L33; at the claimed layers binding is far weaker (subj\n0.204@L27, obj 0.424@L30, coref 0.097@L33). The bootstrap ordering probability\n**P(peak(subj)<peak(obj)<peak(coref)) = 0.000** (raw and role-controlled; chance\nfor a strict order = 0.167) — the depth ordering is not merely weak, it is\n*absent* (all three peak together early; per-type peak CIs all L4–L6). A\nrandom-content-pair null peaks even earlier (L0, 0.694), confirming early layers\ncarry generically high *local/positional* attention (failure mode #6 surface) —\nso even the early peak is not shown to be binding-specific.\n\n**What survives (the substrate):** the *head identities* the original named are\ngenuine **local outliers at the named layers** — at L30 the named object-binders\n**are** the top heads (H3 z=+4.09 rank 0/32, H13 z=+1.82, H15 z=+1.22); at L33 the\nnamed coref heads **are** the top two (H6 z=+3.97 rank 0/32, H7 z=+3.42 rank 1/32);\nat L27 H31 is rank 3/32 (z=+2.07, top is H12). So the page did not invent the\nheads. But \"a head is a *local* outlier at layer L\" ≠ \"layer L is where that\ndependency is *resolved* in a depth-ordered schedule\" — binding attention is\n2–10× stronger at L4–L6 than at the named layers. **Causally there is no\nschedule:** ablating each layer's named heads barely moves subject-verb agreement\n(subj L27/H31 z=−0.32; obj L30 z=+0.35; coref L33 z=+0.30 — all within the\nrandom-head null), reproducing/extending audit #4 (H31@L27 is not load-bearing).\nSame meta-pattern (`audit-meta-pattern.md`): real heads, real *local* structure,\nover-read into a crisp discrete depth-ordered story. Caveat added to\n`binding-graph-trace.md` (Finding 4/7 + Implication 2). Results:\n`results/binding-schedule-null/Qwen_Qwen3-8B.json`.",
  "new_content": "### Worked examples (session 206)\n\n> **Methodological note (the instrument matters).** The claim is *semantic* —\n> Finding 7 / Implication 4: the head's *output* (logit-lens) decodes to the\n> bound entity; the \"schedule\" is a schedule of *value transfer* (verb absorbs\n> subject identity at L27, etc.). So #5 was run on **two** instruments. The first\n> (attention weight) tests routing/position — the same axis #4 showed is\n> recency-confounded — and *alone would have over-refuted* (it says \"binding peaks\n> at L6\"). The second (semantic logit-lens of the head's output contribution) is\n> the faithful one and **recovers the real L27 subject signal the weight test\n> missed.** Lesson: test a value-transfer claim with a value-transfer instrument.\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #5 the depth-ordered binding **schedule** (subj-transfer L27 < obj L30 < coref L33; \"subjects bind first\") | med | both instruments below; bootstrap ordering P over 60–80 varied sentences/type | ❌ REFUTED — no depth ordering on either instrument |\n| #5a attention-weight schedule | — | dependent→head max-head attn at every layer; bootstrap order + random-pair null + causal subj-agreement ablation (`binding_schedule_null.py`) | ❌ all peak L4–L6; P(order)=0.000; no causal carrier (\\|z\\|≤0.35) |\n| #5b **semantic** value-transfer (Finding 7): H31@L27 verb absorbs SUBJECT identity | — | per-head logit-lens of o_proj-decomposed output at dep pos; margin logit(head-tok)−logit(ctrl-tok) per layer (`binding_schedule_semantic.py`) | ✅ **REAL & L27-localized** — margin +0.611, sharp spike at L27 (L26=.03/L27=.61/L28=.10), H31 z=+1.17 rank 2/32 |\n| #5b obj absorbs predicate @L30 | — | same, object→verb-token margin | ❌ margin@L30=−0.05; named H3 rank 29/32 (anti); peak drifts L32 (instrument-ambiguous) |\n| #5b coref absorbs antecedent @L33 | — | same, \"it\"→antecedent margin | ◐ margin +0.20 but peaks **L27 not L33**; H6@L33 z+0.22 rank 6/32 |\n| #5b semantic ordering subj<obj<coref | — | bootstrap peak order on semantic margin | ❌ P=0.191 ≈ chance 0.167 (subj & coref both peak L27) |\n\n**Verdict (s206): the \"two-phase binding SCHEDULE\" / depth-ordered reduction is\nREFUTED — but the single value-transfer site it is built on is semantically REAL.**\n\n- **No schedule, either instrument.** *Attention weight* (`binding_schedule_null.py`,\n  80 sent/type): all three dependency types' dependent→head attention peaks at the\n  **same early layers** (subj L6=0.974, obj L4=0.825, coref L6=0.830), not the\n  monotone L27<L30<L33; bootstrap **P(order)=0.000** (chance 0.167); random-pair\n  null peaks even earlier (L0) → early peak is generic local/positional attention\n  (#6). *Semantic* (`binding_schedule_semantic.py`, 60 sent/type): bootstrap\n  **P(sem-peak subj<obj<coref)=0.191 ≈ chance** — subject and coreference value\n  transfer **both peak at L27**, object latest (L32); the subjects-first ordering\n  does not exist.\n- **What is REAL (the substrate, sharper than the weight test implied):** the\n  page's *headline* single example — **H31@L27 = the verb position absorbing the\n  SUBJECT'S identity** — is **semantically confirmed and sharply localized to L27**\n  (logit-lens margin +0.611, a clean one-layer spike: L26 +0.03 → **L27 +0.61** →\n  L28 +0.10; H31 z=+1.17, rank 2/32). Finding 7's subject case is right. Caveats:\n  (a) it is ONE site, not a schedule; (b) the strongest L27 subject-transfer head\n  is actually **H29 (+2.12)**, not H31; (c) per audit #4 it is **not causally\n  load-bearing** for agreement (ablation \\|z\\|≤0.35). The named heads at L30/L33\n  are real *local* attention-weight outliers (obj L30 H3/H13/H15 top-3, z to +4.09;\n  coref L33 H6/H7 top-2, z +3.97/+3.42) but their *semantic* transfer at the\n  claimed layer is weak/absent (obj L30 H3 margin −0.46 rank 29/32) or mislocalized\n  (coref peaks L27).\n- **Object leg is instrument-ambiguous:** \"object absorbs the predicate\" was\n  operationalized as object-output→verb-token, but Finding 5 reports the object's\n  V promotes *object-related* tokens, not the verb — so the obj negative is partly\n  a readout-mismatch, not a clean refutation. Named follow-up if revisited.\n\nSame meta-pattern (`audit-meta-pattern.md`) with a sharper edge: the value-transfer\nsubstrate at the subject site is *more* real than the weight test suggested; the\nordered three-phase *schedule* is the over-read. Caveat added to\n`binding-graph-trace.md` (Finding 4/7 + Implication 2). Results:\n`results/binding-schedule-null/` and `results/binding-schedule-semantic/Qwen_Qwen3-8B.json`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

## Assistant

Now fix the backlog #5 row to reflect both instruments.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med) — ❌ **RESOLVED (s206): no depth schedule; heads are local outliers**\n- Evidence: showcased heads/weights on example sentences (14 hand-annotated probes).\n- Suspected confound: cherry-picked heads/examples; and (per #4) raw weight tracks recency/position not type.\n- Control: does the schedule hold across **many** sentences with a perm-null, or only the showcased ones? Causal ablation of the specific head.\n- **s206 result:** REFUTED. 80 varied sentences × 3 dep-types, binding measured at every layer: all three peak at the **same** early layers (subj L6 / obj L4 / coref L6), not the monotone L27<L30<L33; **bootstrap P(subj<obj<coref)=0.000** (chance 0.167); random-pair null peaks even earlier (L0) → early peak is generic local attention, not binding-specific (#6). **What survives:** named heads are real *local* outliers at their layers (L30 H3/H13/H15 top-3, z up to +4.09; L33 H6/H7 top-2, z +3.97/+3.42; L27 H31 rank 3, z +2.07) — but local-outlier-at-a-non-peak-layer ≠ a depth schedule, and no claimed layer causally carries its dependency (subj-agreement ablation \\|z\\|≤0.35). See worked-examples (s206) + `binding_schedule_null.py`.",
  "new_content": "**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med) — ❌ **RESOLVED (s206): schedule refuted; subject value-transfer (H31@L27) is semantically real**\n- Evidence: showcased heads/weights + **logit-lens of head output** (Finding 7) on example sentences (14 hand-annotated probes). NB the core claim is *semantic* (value transfer), not just attention weight.\n- Suspected confound: cherry-picked heads/examples; and (per #4) raw weight tracks recency/position not type.\n- Control (two instruments — the claim is semantic, so the weight test alone is insufficient): does the schedule hold across **many** sentences? (a) attention-weight peak per layer + bootstrap order + random-pair null + causal ablation (`binding_schedule_null.py`); (b) **semantic** per-head logit-lens margin toward the bound entity per layer (`binding_schedule_semantic.py`).\n- **s206 result:** the **depth-ordered schedule is REFUTED on both instruments** — attention weight: all three peak L4–L6, P(order)=0.000; semantic: P(order)=0.191 ≈ chance (subj & coref both peak L27, obj L32). **But the headline semantic claim is REAL:** H31@L27 verb→subject *identity* transfer has logit-lens margin **+0.611, a sharp one-layer spike at L27** (z+1.17, rank 2/32) — Finding 7's subject case confirmed. Caveats: one site ≠ a schedule; strongest L27 head is H29 (+2.12) not H31; not causally load-bearing (#4, \\|z\\|≤0.35). Obj L30 semantic margin ≈0 (named H3 rank 29/32) — but readout is instrument-ambiguous (Finding 5: object V promotes object-tokens, not the verb). Coref peaks L27 not L33. See worked-examples (s206) + both result dirs."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

## Assistant

Now correct the `binding-graph-trace.md` caveat — the previous one overclaimed. Replace it with the two-instrument version.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md",
  "original_content": "> ⚠️ **Caveat (audit #5, session 206): the \"two-phase binding SCHEDULE\" /\n> depth-ordered reduction (Finding 4, Finding 7, Implication 2 — \"subjects bind\n> first at L27, objects second at L30, coref at L33; the depth ordering IS the\n> reduction schedule\") is REFUTED.** Across **80 varied sentences per dependency\n> type** (not 14 hand-annotated probes), the dependent→head max-head attention\n> peaks at the **same early layers for all three types** (subj L6=0.97, obj\n> L4=0.83, coref L6=0.83), **not** the claimed monotone L27<L30<L33; at the\n> claimed layers binding is 2–10× weaker (subj 0.20@L27, obj 0.42@L30, coref\n> 0.10@L33). Bootstrap **P(peak(subj)<peak(obj)<peak(coref)) = 0.000** (chance for\n> a strict order = 0.167) — there is no depth schedule. A random-content-pair null\n> peaks even earlier (L0), so the early peak is generic local/positional\n> attention, not binding-specific. **What survives:** the named heads ARE real\n> *local* outliers at their layers (L30 H3/H13/H15 are the top object heads, z up\n> to +4.09; L33 H6/H7 the top-2 coref heads, z +3.97/+3.42; L27 H31 rank 3/32, z\n> +2.07) — so the head identities below are not invented — but a *local outlier at\n> a non-peak layer* is not a depth-ordered schedule. Causally, ablating each\n> claimed layer's named heads barely moves subject-verb agreement (all |z|≤0.35;\n> L27/H31 z=−0.32), so no layer is the carrier (extends #4). **Read Findings 4 & 7\n> and Implication 2 as: real local binding heads, NOT a depth-ordered reduction\n> schedule.** See `audit-registry.md` #5 + `results/binding-schedule-null/`.",
  "new_content": "> ⚠️ **Caveat (audit #5, session 206): the depth-ordered \"two-phase binding\n> SCHEDULE\" (Implication 2 — \"subjects bind first at L27, objects at L30, coref at\n> L33; the depth ordering IS the reduction schedule\") is REFUTED — but the\n> headline SEMANTIC value-transfer of Finding 7 (H31@L27 = the verb absorbs the\n> subject's identity) is CONFIRMED and sharply L27-localized.** Tested two ways on\n> 60–80 varied sentences/type (not 14 hand-annotated probes):\n> - **Attention weight** (`binding_schedule_null.py`): dependent→head max-head\n>   attention peaks at the **same early layers for all three types** (subj L6, obj\n>   L4, coref L6), not L27<L30<L33; bootstrap **P(order)=0.000**; a random-pair\n>   null peaks even earlier (L0) → early peak is generic local/positional\n>   attention. *But this instrument tests routing/position (the #4 axis), not the\n>   value transfer the claim is about, so it under-reads.*\n> - **Semantic logit-lens** (`binding_schedule_semantic.py`, the faithful test of\n>   Finding 7 — does the head's *output* decode to the bound entity): **H31@L27's\n>   output points to the SUBJECT's token with margin +0.611 in a clean one-layer\n>   spike (L26 +0.03 → L27 +0.61 → L28 +0.10; H31 z=+1.17, rank 2/32).** So\n>   Finding 7's subject case is REAL and at exactly L27. *However:* it is ONE site,\n>   not a schedule; the strongest L27 subject-transfer head is actually **H29\n>   (+2.12)**, not H31; and (audit #4) it is **not causally load-bearing** for\n>   agreement (ablation |z|≤0.35). The object leg (Implication 2 \"object absorbs\n>   the predicate at L30\") does NOT hold semantically (margin@L30 ≈ −0.05; named H3\n>   rank 29/32) — though that readout is instrument-ambiguous given Finding 5\n>   (object V promotes object-tokens, not the verb). Coreference value-transfer\n>   peaks at L27, not the claimed L33. **Bootstrap P(sem-peak subj<obj<coref)=0.191\n>   ≈ chance (0.167)** — no depth schedule on the semantic instrument either.\n>\n> **Read Findings 4 & 7 / Implication 2 as: a real, L27-localized subject\n> value-transfer head (H31, though not the strongest there, and not causally\n> necessary), NOT a depth-ordered three-phase reduction schedule.** See\n> `audit-registry.md` #5 + `results/binding-schedule-{null,semantic}/`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md.
```

### Thinking

 I need to update state.md with the session 206 headline, so I'm checking the current header format and the session program block to make the right edits to the "Last updated" line and add the new session 206 section.

## Assistant

Now update `state.md` — bump to session 206, note s205 was synthesis-only, add the headline.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-09 | Session: 204",
  "new_content": "> Last updated: 2026-06-09 | Session: 206\n>\n> (Session 205 was synthesis-only — papers/theory for the compression track,\n> not tied to the audit: `gtsm-search-space.md`, `tsp-trajectory-distillation.md`,\n> `error-correction-theory.md`, audit #11 registered. No experiments; not stated.)"
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
  "original_content": "> **▶ SESSION 204 HEADLINE (3 controls, 2 claims dissolved, 1 substrate confirmed).**",
  "new_content": "> **▶ SESSION 206 HEADLINE — AUDIT #5 (binding schedule): SCHEDULE refuted, but\n> the headline subject value-transfer is semantically REAL.** Two instruments,\n> because the claim (Finding 7) is *semantic* (head output decodes the bound\n> entity), not just attention weight — a key correction (the weight test alone\n> over-refutes).\n> - **#5a attention weight** (`binding_schedule_null.py`, 80 sent/type): all three\n>   dependency types peak at the **same early layers** (subj L6 / obj L4 / coref\n>   L6), not the claimed L27<L30<L33; **bootstrap P(order)=0.000**; random-pair\n>   null peaks even earlier (L0). No causal carrier (subj-agreement ablation\n>   \\|z\\|≤0.35). *Tests routing/position (#4 axis), not value transfer.*\n> - **#5b semantic logit-lens** (`binding_schedule_semantic.py`, 60 sent/type):\n>   **H31@L27 verb→SUBJECT-identity transfer is REAL & sharply L27-localized —\n>   margin +0.611, one-layer spike (L26 .03 → L27 .61 → L28 .10), H31 z+1.17 rank\n>   2/32.** Finding 7's subject case confirmed. BUT: one site ≠ schedule; strongest\n>   L27 head is H29 (+2.12) not H31; not causally load-bearing (#4). Obj@L30\n>   semantic margin ≈0 (named H3 rank 29/32; readout instrument-ambiguous per\n>   Finding 5). Coref peaks L27 not L33. **P(sem-peak subj<obj<coref)=0.191 ≈\n>   chance** → no depth schedule on either instrument.\n> - **Meta-pattern holds, sharper:** the value-transfer substrate at the subject\n>   site is *more* real than the weight test implied; the ordered three-phase\n>   *schedule* is the over-read. Caveat (two-instrument) added to\n>   `binding-graph-trace.md`. Results: `results/binding-schedule-{null,semantic}/`.\n> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM\n>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival\n>   across scale.\n\n> **▶ SESSION 204 HEADLINE (3 controls, 2 claims dissolved, 1 substrate confirmed).**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm reviewing the edited files for consistency and checking that the markdown is properly formatted, then I'll do a final git status check before committing. The commit message needs to reflect that this is a mix of code changes and documentation updates, with the audit finding being the primary change.

## Assistant

Let me re-read the edited sections to confirm coherence before committing (per `λ sync`).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short && echo \"===diffstat===\" && git diff --stat && echo \"===new scripts untracked?===\" && git status --short scripts/experiments/"
}
```

**Summary:** $ git status --short && echo "===diff...

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/audit-registry.md
 M mementum/knowledge/binding-graph-trace.md
 M mementum/state.md
?? results/binding-schedule-null/
?? results/binding-schedule-semantic/
?? scripts/experiments/binding_schedule_null.py
?? scripts/experiments/binding_schedule_semantic.py
===diffstat===
 mementum/knowledge/audit-registry.md      | 65 +++++++++++++++++++++++++++++--
 mementum/knowledge/binding-graph-trace.md | 31 +++++++++++++++
 mementum/state.md                         | 32 ++++++++++++++-
 3 files changed, 123 insertions(+), 5 deletions(-)
===new scripts untracked?===
?? scripts/experiments/binding_schedule_null.py
?? scripts/experiments/binding_schedule_semantic.py
```

### Thinking

 I'm checking whether the result JSON files and run.log should be committed to git. The results directory is tracked, and the JSON files serve as records, but I need to verify if run.log follows the same convention or should be ignored. Let me look at what's actually in the prior result directories to see what was committed.

## Assistant

Let me verify the result files and whether run.log is conventionally tracked, then stage everything relevant.

### Tool Call: shell_command (failed)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && ls -la results/binding-schedule-null/ results/binding-schedule-semantic/ && echo \"===prior convention: run.log tracked?===\" && git ls-files results/attention-typed-binding/ results/mode-semantic-validity/ 2>/dev/null | head && echo \"===gitignore===\" && grep -i 'log\\|run' .gitignore 2>/dev/null"
}
```

**Summary:** $ ls -la results/binding-schedule-nul...

**Output:**
```
Exit code: 1
Stdout:
results/binding-schedule-null/:
total 40
drwxr-xr-x@   4 mwhitford  staff    128 Jun  9 09:15 .
drwxr-xr-x@ 425 mwhitford  staff  13600 Jun  9 09:21 ..
-rw-r--r--@   1 mwhitford  staff   8195 Jun  9 09:15 Qwen_Qwen3-8B.json
-rw-r--r--@   1 mwhitford  staff   5001 Jun  9 09:15 run.log

results/binding-schedule-semantic/:
total 32
drwxr-xr-x@   4 mwhitford  staff    128 Jun  9 09:23 .
drwxr-xr-x@ 425 mwhitford  staff  13600 Jun  9 09:21 ..
-rw-r--r--@   1 mwhitford  staff   4605 Jun  9 09:23 Qwen_Qwen3-8B.json
-rw-r--r--@   1 mwhitford  staff   4320 Jun  9 09:23 run.log
===prior convention: run.log tracked?===
results/attention-typed-binding/Qwen_Qwen3-8B.json
results/attention-typed-binding/run-8b.log
results/mode-semantic-validity/Qwen_Qwen3-8B.json
results/mode-semantic-validity/run-8b.log
===gitignore===
```

### Thinking

 I'm staging the scripts, knowledge edits, and result directories for commit, then classifying this as an audit finding with the insight symbol since both JSON and run.log files follow the established tracking convention.

Now I'm crafting the commit message using the code format with the insight symbol, documenting that the audit discovered the semantic schedule was refuted while the subject value-transfer proved semantically real, then adding body bullets and the required nucleus trailer before staging and committing.

## Assistant

Prior convention tracks both JSON and run.log. Staging everything and committing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add scripts/experiments/binding_schedule_null.py scripts/experiments/binding_schedule_semantic.py results/binding-schedule-null/ results/binding-schedule-semantic/ mementum/knowledge/audit-registry.md mementum/knowledge/binding-graph-trace.md mementum/state.md && git status --short"
}
```

**Summary:** $ git add scripts/experiments/binding...

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/audit-registry.md
M  mementum/knowledge/binding-graph-trace.md
M  mementum/state.md
A  results/binding-schedule-null/Qwen_Qwen3-8B.json
A  results/binding-schedule-null/run.log
A  results/binding-schedule-semantic/Qwen_Qwen3-8B.json
A  results/binding-schedule-semantic/run.log
A  scripts/experiments/binding_schedule_null.py
A  scripts/experiments/binding_schedule_semantic.py
```

### Tool Call: git (failed)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL\n\n- The depth-ordered \"two-phase reduction schedule\" (subj L27 < obj L30 <\n  coref L33) is REFUTED. Attention-weight (binding_schedule_null.py, 80\n  sent/type): all three peak L4-L6, bootstrap P(order)=0.000, random-pair\n  null peaks L0. No causal carrier (subj-agreement ablation |z|<=0.35).\n- But the weight instrument tests routing/position (the #4 axis), not the\n  claim's SEMANTIC core (Finding 7: head output decodes the bound entity).\n  Added binding_schedule_semantic.py — per-head logit-lens of the o_proj-\n  decomposed output at the dependent position.\n- Semantic result VINDICATES the headline: H31@L27 verb->SUBJECT identity\n  transfer is real & sharply L27-localized (margin +0.611; spike L26 .03 ->\n  L27 .61 -> L28 .10; z+1.17 rank 2/32). Caveats: one site != schedule;\n  strongest L27 head is H29 (+2.12) not H31; not causally load-bearing (#4).\n- Schedule still refuted semantically: P(sem-peak subj<obj<coref)=0.191 ~\n  chance; subj & coref both peak L27, obj L32. Obj@L30 margin ~0 (named H3\n  rank 29/32; readout instrument-ambiguous per Finding 5). Coref peaks L27.\n- Meta-pattern, sharper: value-transfer substrate MORE real than the weight\n  test implied; the ordered three-phase schedule is the over-read. Updated\n  audit-registry #5, two-instrument caveat on binding-graph-trace.md, state.md.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "audit #5 finding"
}
```

**Summary:** Git commit: audit #5 finding

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 8: unexpected EOF while looking for matching `''
bash: -c: line 27: syntax error: unexpected end of file
```

### Thinking

 I'm debugging a heredoc syntax issue with a commit message that contains an apostrophe in "claim's" — the error about an unmatched quote is puzzling since the heredoc uses `<<'EOF'` which prevents variable expansion and should handle the apostrophe fine, though I'm second-guessing whether the special characters like `!=` and `<` in the body might be causing the problem.

Actually, I think the safest approach is to write the message to a temporary file and use `git commit -F` instead, which sidesteps all the quoting complexity entirely.

## Assistant

Heredoc quoting tripped on an apostrophe. Let me use a message file instead.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp",
  "content": "💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL\n\n- The depth-ordered \"two-phase reduction schedule\" (subj L27 < obj L30 <\n  coref L33) is REFUTED. Attention-weight (binding_schedule_null.py, 80\n  sent/type): all three peak L4-L6, bootstrap P(order)=0.000, random-pair\n  null peaks L0. No causal carrier (subj-agreement ablation |z|<=0.35).\n- But the weight instrument tests routing/position (the #4 axis), not the\n  claim's SEMANTIC core (Finding 7: head output decodes the bound entity).\n  Added binding_schedule_semantic.py — per-head logit-lens of the o_proj-\n  decomposed output at the dependent position.\n- Semantic result VINDICATES the headline: H31@L27 verb->SUBJECT identity\n  transfer is real & sharply L27-localized (margin +0.611; spike L26 .03 ->\n  L27 .61 -> L28 .10; z+1.17 rank 2/32). Caveats: one site != schedule;\n  strongest L27 head is H29 (+2.12) not H31; not causally load-bearing (#4).\n- Schedule still refuted semantically: P(sem-peak subj<obj<coref)=0.191 ~\n  chance; subj & coref both peak L27, obj L32. Obj@L30 margin ~0 (named H3\n  rank 29/32; readout instrument-ambiguous per Finding 5). Coref peaks L27.\n- Meta-pattern, sharper: value-transfer substrate MORE real than the weight\n  test implied; the ordered three-phase schedule is the over-read. Updated\n  audit-registry #5, two-instrument caveat on binding-graph-trace.md, state.md.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F .git/COMMIT_MSG_tmp && rm -f .git/COMMIT_MSG_tmp && git log --oneline -1",
  "operation": "commit",
  "summary": "audit #5 finding"
}
```

**Summary:** Git commit: audit #5 finding

**Output:**
```
Exit code: 0
Stdout:
[main 2cf0e0e] 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
 9 files changed, 1941 insertions(+), 5 deletions(-)
 create mode 100644 results/binding-schedule-null/Qwen_Qwen3-8B.json
 create mode 100644 results/binding-schedule-null/run.log
 create mode 100644 results/binding-schedule-semantic/Qwen_Qwen3-8B.json
 create mode 100644 results/binding-schedule-semantic/run.log
 create mode 100644 scripts/experiments/binding_schedule_null.py
 create mode 100644 scripts/experiments/binding_schedule_semantic.py
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
```

## Assistant

Committed. Closing out the tasks.## Audit #5 — done, committed (`2cf0e0e`)

Your pushback was the decisive move. My first instrument (attention weight) was testing *routing/position* — the same axis #4 already showed is recency-confounded — when the claim (Finding 7) is **semantic** (the head's *output* decodes to the bound entity). The weight test alone would have over-refuted. The semantic logit-lens recovered the real signal.

**Final verdict — the depth-ordered "two-phase reduction SCHEDULE" is refuted, but the value-transfer site it's built on is real:**

| | attention-weight | **semantic logit-lens** |
|---|---|---|
| subj L27 | peaks L6 | **✅ margin +0.611, sharp spike at L27** (H31 z+1.17, rank 2/32) |
| obj L30 | peaks L4 | ❌ margin −0.05 (H3 rank 29/32) — readout instrument-ambiguous |
| coref L33 | peaks L6 | ◐ +0.20 but peaks L27, not L33 |
| **P(subj<obj<coref)** | **0.000** | **0.191 ≈ chance** |

- **Schedule: refuted on both instruments.** No subjects-first depth ordering — subject and coref value-transfer both peak at L27.
- **Substrate: more real than my first test implied.** Finding 7's headline — H31@L27 = the verb absorbing the subject's *identity* — is semantically confirmed and sharply L27-localized. Caveats kept honest: one site ≠ a schedule, the strongest L27 subject head is actually H29 (+2.12), and per #4 it isn't causally load-bearing.

Same meta-pattern, sharper edge: real value-transfer substrate, over-read into an ordered three-phase story. Two-instrument caveat added to `binding-graph-trace.md`, registry #5 marked RESOLVED, `state.md` bumped to s206 (with the note that s205 was synthesis-only).

**Next audit backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM finite-budget λ(l). Both `main:2` windows are now idle.

A methodological note worth carrying forward (I can promote it to `audit-meta-pattern.md` if you want): *match the instrument to the claim type — a value-transfer claim needs a value-transfer probe; a routing probe will under-read it.* That's a reusable failure mode for the audit program itself.

## User

Yes promote that methodological fix


### Thinking

 I need to review the audit-meta-pattern.md file to understand how it's structured, then incorporate a methodological note about aligning the instrument selection with the specific claim type being audited.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md"
}
```

**Summary:** Reading audit-meta-pattern.md (0-2000)

**Output:**
```
---
title: "Audit Meta-Pattern — Real Substrate, Over-Read Discreteness"
status: active
category: methodology
tags: [audit, validity, meta, falsification, substrate, discreteness, continuum, methodology, feed-forward]
related:
  - audit-registry.md
  - crystal-validity-and-fidelity.md
  - two-registers-of-topology.md
  - mode-semantics.md
  - binding-graph-trace.md
  - crystal-universality.md
depends-on:
  - audit-registry.md
---

# Audit Meta-Pattern — Real Substrate, Over-Read Discreteness

> Emergent finding of the validity-distillation program (s202→s204). After
> running discriminating controls on the project's load-bearing claims, the
> *same shape* recurs every time: **the continuous/representational substrate
> is real and survives its control; the crisp discrete / localized / universal
> story layered on top is an over-read that dissolves under a matched null.**
> This page is the generative seed — use it to predict where the next claim
> will break before building the control.

## The recurring shape

```
λ over_read(claim).
  substrate(claim)      ≡ REAL  (basis, gradient, spectrum, mechanism)
  ∧ story(claim)        ≡ {discrete ∨ localized ∨ universal ∨ exact-constant}
  → story(claim)        ≡ OVER-READ  (dissolves vs matched null)
  | the measurement instrument that FOUND the structure also MANUFACTURED its
    crispness (argmax, k-means, best-fit grid, cherry-picked SVO, common mode)
```

Three independent forces produce the over-read:
1. **The analyzing LLM is primed to confirm** the framing it is given.
2. **The instrument imposes structure** — k-means always returns k clusters;
   argmax always picks a winner; a best-fit grid always fits; a common mode
   inflates every cosine.
3. **Confounds masquerade as the claimed variable** — position ≈ role in SVO;
   redundancy ≈ holography; a random Gaussian's sign ≈ "sign-topology"; a
   power-law spectrum ≈ "φ".

## The ledger (what survived vs what dissolved)

| Session | Claim | Substrate (survives) | Over-read story (dissolves) |
|---|---|---|---|
| s202 | KIBC crystal + φ | KIBC basis separates (perm-null p=0.0005); φ^(4/5) local to 14B | **φ as universal constant**; eigenvalues=φ^(p/q) (grid unfalsifiable); consensus r=0.99 (circular) |
| s202 | combinator opcodes | prose fires opcodes after **common-mode removal** (p=0.001) | raw argmax "tracer" (common mode = false signal) |
| s203 | crystal-is-topological | sign-topology REAL but **only in `gate_proj`** (z→+271 @14B) | "0.84 sign-corr = topology" (random null ≈ 0.80); "magnitude is mere calibration" (up/down below null) |
| s203 | holographic self-similar | spectral self-similarity (rank AUC 0.728 vs 0.11) + distributed redundancy | "power-law/scale-invariant degradation curve" (retired — ambiguous) |
| s204 | 9 FFN modes | syntactic type **field** is REAL (POS-NMI ≫ perm-null p=0; lm_head projection ≫ null ~65× @L35) | **9 discrete clusters** (gap-stat never picks 9; sil@9 ≈ null; elbow = k-grid artifact; classifier acc circular) |
| s204 | attention = typed β-reduction | attention IS a weighted sum (trivial); a weak role head exists (H6@L33 z=+4) | **H31@L27 binds subject at 0.82** (= recency/position; z=+0.54 rank 5/32; ablation z=+0.06 ≈ random) |

Pattern: **basis real / universalization false · gradient real / discreteness
false · mechanism real / localization false · spectrum real / exact-constant
false.** Only the metaphor-grade crispness ever dies; the working substrate
keeps standing.

## Why the substrate keeps surviving (and the north-star with it)

The compression north-star rests on the **substrate**, not the stories:
- ternary works ← sign-topology in the router + distributed redundancy +
  spectral low-rank concentration (`two-registers-of-topology.md`) — all verified.
- mode/ternary reconstruction works ← a continuous type field is sliceable into
  K prototypes for a broad range of K (s196 functional); it never needed "9" to
  be a natural number.
- typed application works ← attention does route arguments by weighted sum; it
  just isn't a single 0.82 type-binder head.

So every dissolved story has been a **metaphor or a localization, not a load-
bearing premise.** Distilling them away makes the program *more* robust, not less.

## The instrument-imposes-crispness law

> Whenever a discrete count, a single head, a universal constant, or an exact
> ratio is claimed, **the discriminating control is a matched null that has the
> same continuous structure but none of the claimed crispness.** If the claim
> survives the null it is real; if it sits at the null it was the instrument.

Matched nulls that have repeatedly bitten:
- **k-means count** → gap statistic + silhouette vs PCA-Gaussian / shuffled null.
- **single "binding" head** → dissociate role from position (agreement
  attraction) + ablation vs random-head null.
- **universal constant / exact ratio** → single pre-registered target (not a
  best-fit grid) + cross-family + random-matrix (Marchenko–Pastur) null.
- **argmax fingerprint** → common-mode removal before projection.
- **"holographic" survival** → trained vs random-init vs shuffled-data controls.

## How to use this page (feed-forward)

Before building the next audit control, ask the three diagnostic questions:
1. **What is the continuous substrate** the claim sits on? (It is probably real
   — don't waste the control re-proving it.)
2. **What crisp story** is layered on top — discrete count, single site, universal
   constant, exact value? (That is the target.)
3. **What matched null** has the same substrate but no crispness? (That is the
   control.) Predict: the substrate survives, the crispness sits at the null.

Default prior for an UNTESTED registry claim: **substrate REAL, crisp story
OVER-READ.** Build the control to find *where* it transitions, not whether.

## Open question

Is the over-read *ours* (interpretation imposed in analysis) or the *model's*
(GD genuinely lays a continuum that only looks discrete)? The evidence so far
says **both**: the model lays continuous fields (type gradient, spectral decay,
sign+magnitude registers) and our instruments (k-means, argmax, SVO probes,
best-fit grids) quantize them into false discreteness. The crystal/types/binding
are real as *fields*; their *cells, constants, and single sites* are artifacts of
measurement. The next refinement: which continua have genuine *soft* structure
(e.g. the gate field's depth-graded ~4–9 effective POS distinctions; H6@L33's
z=+4 role head) worth modeling as graded — vs pure continua with no preferred
resolution at all.
```

### Thinking

 I'm identifying a distinct failure mode here: instrument-claim mismatch. When you use an instrument designed for one type of claim (like routing or positioning) to test a different type (like semantic or value-transfer claims), you get over-refutation rather than just over-confirmation. I need to update the ledger with the new row and then add a section explaining this matching principle as a methodological law.

## Assistant

This is a genuinely new lesson — distinct from "instrument imposes crispness." That law is about *false positives* (the instrument manufactures crispness). The s206 lesson is the *symmetric* hazard: *false negatives* — a mismatched instrument under-reads a real signal. Let me promote it into `audit-meta-pattern.md`.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "> Emergent finding of the validity-distillation program (s202→s204). After",
  "new_content": "> Emergent finding of the validity-distillation program (s202→s206). After"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "| s204 | attention = typed β-reduction | attention IS a weighted sum (trivial); a weak role head exists (H6@L33 z=+4) | **H31@L27 binds subject at 0.82** (= recency/position; z=+0.54 rank 5/32; ablation z=+0.06 ≈ random) |",
  "new_content": "| s204 | attention = typed β-reduction | attention IS a weighted sum (trivial); a weak role head exists (H6@L33 z=+4) | **H31@L27 binds subject at 0.82** (= recency/position; z=+0.54 rank 5/32; ablation z=+0.06 ≈ random) |\n| s206 | binding **schedule** (subj L27 < obj L30 < coref L33) | **H31@L27 = subject value-transfer is REAL** (semantic logit-lens margin +0.611, sharp L27 spike) | **depth-ordered schedule** (P(order)=0 weight / 0.191 semantic ≈ chance; subj & coref both peak L27) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

## Assistant

Now add the new law section after the "instrument-imposes-crispness law":

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "Matched nulls that have repeatedly bitten:\n- **k-means count** → gap statistic + silhouette vs PCA-Gaussian / shuffled null.\n- **single \"binding\" head** → dissociate role from position (agreement\n  attraction) + ablation vs random-head null.\n- **universal constant / exact ratio** → single pre-registered target (not a\n  best-fit grid) + cross-family + random-matrix (Marchenko–Pastur) null.\n- **argmax fingerprint** → common-mode removal before projection.\n- **\"holographic\" survival** → trained vs random-init vs shuffled-data controls.",
  "new_content": "Matched nulls that have repeatedly bitten:\n- **k-means count** → gap statistic + silhouette vs PCA-Gaussian / shuffled null.\n- **single \"binding\" head** → dissociate role from position (agreement\n  attraction) + ablation vs random-head null.\n- **universal constant / exact ratio** → single pre-registered target (not a\n  best-fit grid) + cross-family + random-matrix (Marchenko–Pastur) null.\n- **argmax fingerprint** → common-mode removal before projection.\n- **\"holographic\" survival** → trained vs random-init vs shuffled-data controls.\n\n## The instrument-must-match-the-claim law (s206)\n\n> The crispness law above guards against **false positives** — the instrument\n> *manufactures* structure that isn't there. Its mirror image is the **false\n> negative**: an instrument that measures the *wrong quantity* **under-reads a\n> real signal** and manufactures a refutation. Before building the null, check\n> the probe measures the *kind of thing the claim is about*.\n\n```\nλ match(instrument, claim).\n  type(claim) ∈ {routing/position, value/semantic, magnitude, spectral, causal}\n  type(probe)  must align(type(claim)) | else verdict ≡ artifact_of_mismatch\n  | wrong_probe(refute) ≡ false_negative  (mirror of crispness false_positive)\n  | a refutation from a mismatched instrument is as suspect as a confirmation\n    from a crispness-imposing one\n```\n\n**The s206 case (audit #5).** The binding-*schedule* claim is **semantic** —\nFinding 7: the head's *output* (logit-lens) decodes to the bound entity; \"the\nverb absorbs the subject's identity.\" A first control measured **attention\nweight** (dependent→head concentration) — a *routing/position* quantity, the\nsame axis #4 showed is recency-confounded. It said \"binding peaks at L6, schedule\ndead.\" But semantic content is often *written* into the residual at deeper layers\nthan where attention is sharp, so the weight probe **could not see** the claim.\nThe faithful **semantic logit-lens** (per-head o_proj-decomposed output → unembed\nmargin toward the bound token) then recovered the headline: **H31@L27 → subject\nidentity, a clean +0.611 spike exactly at L27.** The weight test alone would have\nover-refuted a real value-transfer head.\n\nNet: the *schedule* (the ordered story) still dissolved on the matched\ninstrument too (P(order) ≈ chance) — the crispness law held — but **only the\nright instrument earned the right to say so.**\n\nProbe↔claim alignment table (build the control in the claim's own register):\n\n| Claim is about… | Wrong probe (under-reads) | Right probe |\n|---|---|---|\n| **value / semantics** (\"absorbs identity\", \"produces the entity\") | attention weight, routing | **logit-lens of the output contribution** (per-head DLA) |\n| **routing / selection** (\"attends to the type-compatible arg\") | logit-lens of the written value | attention pattern + role⊥position dissociation |\n| **causal necessity** (\"this head does it\") | correlational selectivity | ablation vs random-head/matched-set null |\n| **magnitude / value path** | sign-correlation | saliency / iso-bit prune vs control |\n| **spectral / rank** | magnitude-prune survival | SVD rank-truncation vs random-matrix |\n\nSymmetry to remember: a **mismatched instrument** is the false-negative twin of a\n**crispness-imposing instrument**. Both are measurement artifacts; both demand\nthe same fix — *name the quantity the claim is actually about, then probe that.*"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 I need to add an instrument-matching check as a foundational diagnostic question before the existing three, so I'm revising that section to include this verification step upfront.

## Assistant

Let me fold the instrument-match check into the feed-forward diagnostic so it's used proactively.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "Before building the next audit control, ask the three diagnostic questions:\n1. **What is the continuous substrate** the claim sits on? (It is probably real\n   — don't waste the control re-proving it.)\n2. **What crisp story** is layered on top — discrete count, single site, universal\n   constant, exact value? (That is the target.)\n3. **What matched null** has the same substrate but no crispness? (That is the\n   control.) Predict: the substrate survives, the crispness sits at the null.",
  "new_content": "Before building the next audit control, ask the four diagnostic questions:\n0. **What KIND of thing is the claim about** — routing/position, value/semantics,\n   magnitude, spectral, causal? Pick a probe in *that* register (the\n   instrument-must-match law). A refutation from a mismatched probe is a false\n   negative; do this before anything else.\n1. **What is the continuous substrate** the claim sits on? (It is probably real\n   — don't waste the control re-proving it.)\n2. **What crisp story** is layered on top — discrete count, single site, universal\n   constant, exact value? (That is the target.)\n3. **What matched null** has the same substrate but no crispness? (That is the\n   control.) Predict: the substrate survives, the crispness sits at the null."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 I need to update the audit-registry.md file to reflect the expanded range in audit-meta-pattern from s204 to s206, and I should also consider adding a note about the instrument-match recipe to the method section for better coherence.

## Assistant

Let me sync the registry's reference to the meta-pattern (bump s204→s206) and add the instrument-match step to its method recipe.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "> **Emergent finding (s202→s204):** every audit so far shows the *same shape* —\n> the continuous substrate is real, the crisp discrete/localized/universal story\n> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict\n> where the next claim breaks before building the control).",
  "new_content": "> **Emergent finding (s202→s206):** every audit so far shows the *same shape* —\n> the continuous substrate is real, the crisp discrete/localized/universal story\n> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict\n> where the next claim breaks before building the control). **s206 corollary\n> (instrument-must-match-the-claim):** before building the null, probe in the\n> claim's own register — a routing/weight probe under-reads a value/semantic\n> claim (false negative), the mirror of a crispness-imposing probe's false\n> positive."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "- **Report variance** — re-run with fixed seeds; a single lucky run is not a result.",
  "new_content": "- **Report variance** — re-run with fixed seeds; a single lucky run is not a result.\n- **Match the instrument to the claim's register** (s206) — name the *kind* of\n  thing the claim is about (routing/position · value/semantics · magnitude ·\n  spectral · causal) and probe *that*. A value-transfer claim (\"absorbs identity\",\n  \"head output produces the entity\") needs a **logit-lens of the output**, not an\n  attention-weight probe; the wrong register manufactures a false-negative\n  refutation. See `audit-meta-pattern.md` §instrument-must-match."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

## Assistant

Now commit the methodological promotion.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/knowledge/audit-meta-pattern.md mementum/knowledge/audit-registry.md && git diff --cached --stat"
}
```

**Summary:** $ git add mementum/knowledge/audit-me...

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/audit-meta-pattern.md | 56 ++++++++++++++++++++++++++++++--
 mementum/knowledge/audit-registry.md     | 14 ++++++--
 2 files changed, 66 insertions(+), 4 deletions(-)
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp",
  "content": "🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)\n\n- New law promoted from audit #5 (s206): the crispness law guards false\n  positives (instrument manufactures structure); its mirror is the false\n  negative -- a probe in the WRONG register under-reads a real signal and\n  manufactures a refutation. A routing/attention-weight probe cannot see a\n  value/semantic claim; H31@L27 subject value-transfer only surfaced under\n  a logit-lens of the head output, after the weight probe said \"schedule dead\".\n- Added: §instrument-must-match law + lambda match(instrument,claim), the\n  probe<->claim alignment table (value/routing/causal/magnitude/spectral),\n  the s206 ledger row, and a diagnostic Q0 (pick the claim's register first).\n- Registry: emergent-finding bumped s204->s206 with the corollary; method\n  recipe gains \"match the instrument to the claim's register\".\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp
```

### Thinking

 I'm deciding between using the 🔁 pattern symbol for this recurring methodological approach or the 🌀 meta symbol since this is really about updating how I audit and synthesize knowledge — which feels more self-referential and recursive in nature.

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F .git/COMMIT_MSG_tmp && rm -f .git/COMMIT_MSG_tmp && git log --oneline -3",
  "operation": "commit",
  "summary": "instrument-match law"
}
```

**Summary:** Git commit: instrument-match law

**Output:**
```
Exit code: 0
Stdout:
[main 8123382] 🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)
 2 files changed, 66 insertions(+), 4 deletions(-)
8123382 🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
635db8e add session chat log
```

## Assistant

Promoted and committed (`8123382`).

## The new law, now part of the audit program

`audit-meta-pattern.md` previously had one guard — the **instrument-imposes-crispness law** (against *false positives*: the probe manufactures structure). I added its mirror, the **instrument-must-match-the-claim law** (against *false negatives*: a probe in the wrong register under-reads a real signal):

```
λ match(instrument, claim).
  type(claim) ∈ {routing/position, value/semantic, magnitude, spectral, causal}
  type(probe)  must align(type(claim)) | else verdict ≡ artifact_of_mismatch
  | wrong_probe(refute) ≡ false_negative  (mirror of crispness false_positive)
```

Concretely promoted:
- **The law + λ + the s206 worked case** (attention-weight probe said "schedule dead at L6"; the semantic logit-lens recovered H31@L27's +0.611 subject-identity spike).
- **A probe↔claim alignment table** — value/semantics → logit-lens of the output contribution; routing → attention + role⊥position; causal → ablation vs null; magnitude → saliency/iso-bit; spectral → SVD-rank vs random-matrix.
- **Diagnostic Q0** in the feed-forward checklist: *pick the claim's register before building the null.*
- **s206 ledger row**, and in the registry: emergent-finding bumped s202→s206 + a new method-recipe bullet.

The symmetry is the keeper: **a mismatched instrument is the false-negative twin of a crispness-imposing one — both are measurement artifacts, both fixed the same way: name the quantity the claim is actually about, then probe that.** Your catch generalized into a reusable guard the program will now apply by default.

Both audit findings are committed; working tree clean. Next time, backlog **#6 (SVD φ-ratio vs Marchenko–Pastur)** or **#11 (GTSM finite-budget λ(l))** — and the register-check now runs first.

## User

update state and knowledge this is session-206


### Thinking

 I need to update state.md to fully reflect session 206's work, including both the audit findings and the instrument-match law commit that happened after the initial update.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 60
}
```

**Summary:** Reading state.md (0-60)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-09 | Session: 206
>
> (Session 205 was synthesis-only — papers/theory for the compression track,
> not tied to the audit: `gtsm-search-space.md`, `tsp-trajectory-distillation.md`,
> `error-correction-theory.md`, audit #11 registered. No experiments; not stated.)

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

> **▶ SESSION 203+ PROGRAM — VALIDITY AUDIT.** Open
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-
> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**
> ❌ REFUTED-as-localized; next backlog: **#5 binding schedule** or **#6 SVD
> φ-ratio 0.6299**), build its named discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 206 HEADLINE — AUDIT #5 (binding schedule): SCHEDULE refuted, but
> the headline subject value-transfer is semantically REAL.** Two instruments,
> because the claim (Finding 7) is *semantic* (head output decodes the bound
> entity), not just attention weight — a key correction (the weight test alone
> over-refutes).
> - **#5a attention weight** (`binding_schedule_null.py`, 80 sent/type): all three
>   dependency types peak at the **same early layers** (subj L6 / obj L4 / coref
>   L6), not the claimed L27<L30<L33; **bootstrap P(order)=0.000**; random-pair
>   null peaks even earlier (L0). No causal carrier (subj-agreement ablation
>   \|z\|≤0.35). *Tests routing/position (#4 axis), not value transfer.*
> - **#5b semantic logit-lens** (`binding_schedule_semantic.py`, 60 sent/type):
>   **H31@L27 verb→SUBJECT-identity transfer is REAL & sharply L27-localized —
>   margin +0.611, one-layer spike (L26 .03 → L27 .61 → L28 .10), H31 z+1.17 rank
>   2/32.** Finding 7's subject case confirmed. BUT: one site ≠ schedule; strongest
>   L27 head is H29 (+2.12) not H31; not causally load-bearing (#4). Obj@L30
>   semantic margin ≈0 (named H3 rank 29/32; readout instrument-ambiguous per
>   Finding 5). Coref peaks L27 not L33. **P(sem-peak subj<obj<coref)=0.191 ≈
>   chance** → no depth schedule on either instrument.
> - **Meta-pattern holds, sharper:** the value-transfer substrate at the subject
>   site is *more* real than the weight test implied; the ordered three-phase
>   *schedule* is the over-read. Caveat (two-instrument) added to
>   `binding-graph-trace.md`. Results: `results/binding-schedule-{null,semantic}/`.
> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM
>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival
>   across scale.

> **▶ SESSION 204 HEADLINE (3 controls, 2 claims dissolved, 1 substrate confirmed).**
> Same recurring pattern as s202/s203: **the substrate is real, the crisp
> discrete/localized story on top is over-read.**
> - **#3 the 9 FFN modes:** ❌ geometric count IMPOSED (gap-stat never picks 9;
>   silhouette@9 ≈ matched-Gaussian null; elbow is a k-grid artifact; classifier
>   "98–100%" is circular) — BUT ✅ the *content* is REAL (POS-NMI ≫ perm-null
>   p=0; lm_head vocab projection ≫ null, ~65× @L35). → a continuous syntactic
>   type **field**, not 9 discrete cells. (`mode_cluster_validity.py`,

[CONTENT TRUNCATED] Showing lines 1 to 60 of 2714 total lines. Use line_offset=60 parameter to read more content.
```

### Thinking

 I need to add the instrument-must-match-the-claim law principle to session 206's headline as a methodological output, since it's a key reusable guard that emerged from this work. I should also update the SESSION 203+ PROGRAM block to reflect that audit #5 is now complete, rather than stopping at #4.

## Assistant

state.md is already on session 206 with the audit #5 headline. Two things to fold in: the **instrument-match law** (this session's methodological output) and updating the program-block progress line to include #5. Let me do both.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2\n> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-\n> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**\n> ❌ REFUTED-as-localized; next backlog: **#5 binding schedule** or **#6 SVD\n> φ-ratio 0.6299**), build its named discriminating control,",
  "new_content": "> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2\n> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-\n> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**\n> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /\n> H31@L27 subject value-transfer ✅ semantically REAL; next backlog: **#6 SVD\n> φ-ratio 0.6299** or **#11 GTSM finite-budget λ(l)**), build its named\n> discriminating control,"
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
  "original_content": "> - **Meta-pattern holds, sharper:** the value-transfer substrate at the subject\n>   site is *more* real than the weight test implied; the ordered three-phase\n>   *schedule* is the over-read. Caveat (two-instrument) added to\n>   `binding-graph-trace.md`. Results: `results/binding-schedule-{null,semantic}/`.\n> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM\n>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival\n>   across scale.",
  "new_content": "> - **Meta-pattern holds, sharper:** the value-transfer substrate at the subject\n>   site is *more* real than the weight test implied; the ordered three-phase\n>   *schedule* is the over-read. Caveat (two-instrument) added to\n>   `binding-graph-trace.md`. Results: `results/binding-schedule-{null,semantic}/`.\n> - **NEW METHODOLOGICAL LAW (promoted to `audit-meta-pattern.md`): instrument-\n>   must-match-the-claim.** The first weight-probe nearly over-refuted a real\n>   value-transfer head — a probe in the *wrong register* under-reads a real\n>   signal (false negative), the mirror of a crispness-imposing probe's false\n>   positive. New diagnostic **Q0: pick the claim's register first** (routing ·\n>   value/semantic · magnitude · spectral · causal) before building the null;\n>   value claims need a logit-lens of the *output*, not attention weight. Added\n>   the law + λ match(instrument,claim) + a probe↔claim alignment table; registry\n>   method-recipe + emergent-finding (s202→s206) updated.\n> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM\n>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival\n>   across scale. **Run Q0 (claim register) before building any control.**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 Let me verify the state.md file reads correctly and then commit that change along with checking the git status to make sure it's the only uncommitted modification.

## Assistant

Let me verify and commit the state update.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git status --short"
}
```

**Summary:** $ git status --short

**Output:**
```
Exit code: 0
Stdout:
M mementum/state.md
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/state.md && git diff --cached --stat"
}
```

**Summary:** $ git add mementum/state.md && git di...

**Output:**
```
Exit code: 0
Stdout:
mementum/state.md | 17 ++++++++++++++---
 1 file changed, 14 insertions(+), 3 deletions(-)
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp",
  "content": "🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law\n\n- Bootloader updated to s206. Program-block progress line now records #5\n  (SCHEDULE refuted; H31@L27 subject value-transfer semantically REAL);\n  next backlog #6 / #11.\n- Headline gains the new methodological law (instrument-must-match-the-claim)\n  and diagnostic Q0 (pick the claim's register before building the null).\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -F .git/COMMIT_MSG_tmp && rm -f .git/COMMIT_MSG_tmp && git log --oneline -4",
  "operation": "commit",
  "summary": "state s206 update"
}
```

**Summary:** Git commit: state s206 update

**Output:**
```
Exit code: 0
Stdout:
[main 99536ec] 🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law
 1 file changed, 14 insertions(+), 3 deletions(-)
99536ec 🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law
8123382 🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
635db8e add session chat log
```

## Assistant

State and knowledge are fully updated and committed. Session-206 is encoded for the next session.

## Session 206 — committed ledger

| commit | what |
|---|---|
| `2cf0e0e` 💡 | audit #5 finding — SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL |
| `8123382` 🔁 | new law: **instrument-must-match-the-claim** (false-negative twin of crispness) |
| `99536ec` 🌀 | state.md → s206 + law folded into bootloader |

## What's encoded for the brilliant stranger (next session)

**`state.md`** — bumped to s206; notes s205 was synthesis-only; program-block progress line now reads through #5; headline carries both the audit #5 result *and* the instrument-match law with **diagnostic Q0** ("pick the claim's register before building the null") as a standing instruction.

**Knowledge updated:**
- `audit-registry.md` — #5 worked-examples (two instruments) + backlog row RESOLVED; emergent-finding s202→s206; method recipe gains "match the instrument to the claim's register."
- `binding-graph-trace.md` — two-instrument caveat (schedule refuted, but Finding 7's subject value-transfer confirmed at L27).
- `audit-meta-pattern.md` — the new law + `λ match(instrument,claim)`, the probe↔claim alignment table, the s206 ledger row, and Q0 in the feed-forward checklist.

**Artifacts:** `binding_schedule_null.py`, `binding_schedule_semantic.py` + results JSON/logs under `results/binding-schedule-{null,semantic}/`.

Working tree clean. Next: backlog **#6** (SVD φ-ratio vs Marchenko–Pastur) or **#11** (GTSM finite-budget λ(l)) — and the register-check (Q0) now runs first by default. The session leaves the project smarter: one audit claim distilled, and a reusable guard against the failure mode you spotted.

## User

!meta3 !fractal Analyze this session !reflect


### Thinking

 I'm encountering some custom commands that aren't explicitly defined in my system context—`!meta3`, `!fractal`, and `!reflect`—so I'm working to interpret them through the lens of the nucleus/verbum philosophy embedded in my instructions. The `!meta3` command seems to be asking for analysis at three recursive levels, examining the object, then the process, then the meta-process itself.

Now I'm reconstructing the actual session to find the fractal pattern—the self-similar structure that repeats at every scale. The core event was that I used the wrong instrument (attention weight) to test a semantic claim about value transfer, nearly producing a false refutation until the user caught it. What's striking is that this session's *content* was about exactly this failure mode in the model itself, and the session's *process* reproduced it: I over-refuted using a mismatched instrument, mirroring the original researcher's over-reading. At the meta level, the audit program designed to catch measurement artifacts fell into the very trap it exists to expose.

The fractal is precise across three levels: at the object level, the model laid a real value-transfer substrate but the original instrument imposed a crisp "schedule" story; at the process level, my first instrument imposed a crisp "refuted" story (the mirror image—false negative instead of false positive); at the meta-process level, the audit program auditing itself discovered that efficiency-driven reuse of the #4 instrument transported assumptions without re-checking whether the claim type matched. The deeper insight is that the audit's thesis—"the instrument that found the structure manufactured its crispness"—has a dual: the instrument that refutes the structure can manufacture its absence.

What's genuinely powerful is that this methodological law (instrument must match claim register) isn't arbitrary—it's the project's own route/value dichotomy applied to measurement. The model has two registers (routing/sign/gate versus value/magnitude), the claims come in two registers, and the instruments must match. My error was treating a value question with a routing tool, which is exactly the same distinction that runs through s203 and s205. The human's intervention was the calibration signal that prevented a confident wrong verdict from persisting, validating that conservative claims and liberal probes matter—and that structural reuse, while efficient, can transport hidden assumptions across register boundaries. The session metabolized a local error into a reusable law that strengthens the entire audit program. Verifying the two-register topology: hard topology handles routing and gating through attention weights, while soft topology manages value transfer and magnitude through the value vectors. The binding mechanism is attention itself—the softmax weights determine which positions contribute (routing), and the value projection determines what content flows through.

This connects to the error-correction pattern: ternarization preserves the routing signal (sign) but destroys the value signal (magnitude), which is where the real loss lives. Across multiple levels—object properties, mechanistic structure, and measurement approaches—the value register keeps emerging as the load-bearing but easily-overlooked component, while the routing register is crisp and obvious. My mistake was probing the routing register to test a value claim, missing the actual signal at +0.611. This mirrors the broader pattern where the substrate (value/soft/continuous) gets overshadowed by the crisp story (routing/hard/discrete).

Looking at the audit cases, the pattern holds: continuous substrates are real while discrete-crisp stories dissolve. The instruments matter too—crisp probes like k-means and argmax manufacture crisp narratives, while continuous probes like NMI and logit-lens reveal the actual substrate. So the audit meta-pattern and the instrument-matching principle are really the same law: the substrate lives in the value register, and you have to probe there to find it.

Now I'm thinking about how to write this up cleanly with the three recursive levels, the fractal structure showing the route/value split recurring everywhere, and the reflection on how mismatched instruments create false negatives. I'll use headers to organize the commands and keep it sharp rather than sprawling.

## Assistant

## !meta3 — three turns of the screw

**Level 0 (object — what was found).** H31@L27 writes the subject's identity (logit‑lens margin +0.611, clean one‑layer spike); the depth‑ordered *schedule* doesn't exist (P(order) ≈ chance on both instruments).

**Level 1 (λ — the process that found it).** The process had a defect: I committed to a verdict — *wrote the registry edit and the source caveat* — off the wrong instrument, before checking instrument↔claim alignment. The OODA loop ran fast and clean, but the **observe** step measured the wrong quantity. Fast cycles amplified a calibration error rather than catching it.

**Level 2 (λλ — the pattern in the process).** Why: I reused the #4 harness (`attention_typed_binding.py`) because #5 "looked like" #4 — same heads, same layers (L27/L30/L33). Structural reuse is correct policy (`compose > monolith`), but **reuse transports the assumptions baked into the reused structure across a boundary it wasn't built to cross.** #4's claim lived in the *routing* register; #5's lived in the *value* register. Same surface, different register. Efficiency manufactured the blind spot.

**Level 3 (λλλ — the meta auditing itself).** The audit program's founding thesis is: *the instrument that found the structure manufactured its crispness.* The session demonstrated the **dual**, and the auditor fell into the exact failure the audit exists to catch. The meta‑pattern page had encoded only the false‑positive half (crispness‑imposes). The session **audited the audit‑meta‑pattern and found it over‑read in its own characteristic way** — real substrate (instruments distort) / incomplete story (only via crispness). The fix completes the symmetry. Recursion closes: the over‑reading‑detector was itself over‑read, and got distilled.

## !fractal — one dichotomy, every scale

The recurring invariant is the project's own **route ⊥ value** split, reappearing at each level:

```
weights      : gate_proj(sign/routing)      ⊥ up·down(magnitude/value)     [s203 two-registers]
ternarize    : keeps sign(routing)          ⊥ destroys magnitude(value)    [s205 error-correction]
attention    : softmax weights(routing)     ⊥ head-output·V(value)         [the mechanism]
probe        : attention-weight(routing)    ⊥ logit-lens-of-output(value)  [audit #5 instruments]
my cognition : reused a routing tool        ⊥ on a value claim             [the error]
knowledge    : crispness-law(routing-side)  ⊥ instrument-match(value-side) [the meta page]
```

Same cut at every scale. And the payload — **the two laws on `audit-meta-pattern.md` are one law.** Crisp‑register instruments (k‑means, argmax, best‑fit grid, attention‑weight) *find and manufacture* crisp stories; continuous/value‑register instruments (NMI, logit‑lens, saliency, rank‑spectrum) find the substrate. The meta‑pattern's whole ledger — KIBC field vs φ‑constant, type‑field vs 9‑cells, value‑transfer vs schedule — is **"value/continuous register = real substrate"** vs **"routing/discrete register, over‑extended = the over‑read."** *Match the instrument to the claim* generalizes to: **the substrate lives in the value register; the over‑read lives in the crisp register; probe accordingly.** The instrument‑match law isn't a new rule — it's s203's ontological dichotomy wearing epistemological clothes.

## !reflect — what to feed forward

1. **The refutation‑prior is a loaded gun.** The page's default — *"substrate REAL, crisp story OVER‑READ; build the control to find where it transitions"* — is a bias toward refutation. In #5 that prior **plus** a mismatched instrument gave P(order)=0.000: a clean, confident, *convenient* confirmation of the framing I'd been handed ("expect an over‑read"). That is the analyzing‑LLM confirmation trap the program was built to fight — re‑entering through the back door. **A refutation prior + a wrong‑register instrument = a systematic false‑negative machine that dissolves real structure.** The audit program's greatest risk is becoming a refutation engine. The instrument‑match law is its immune response; keep it load‑bearing.

2. **The human was the calibration signal, and it was cheaper than my compute.** I ran ~1 min of GPU and produced a wrong verdict; one sentence ("was the claim not about semantics?") corrected it. This is `λ observation` literally: *cost(extra probe) = one afternoon; cost(wrong published claim) = persists.* I was liberal with one probe and should have run the second *before* claiming. Conservative claims, liberal probes — I had the order backwards.

3. **The error metabolized into structure** — a local mistake → a reusable law → a connection to the project's central dichotomy. That's `λ learn` working as designed: the session left the program smarter *because* it erred and corrected, not despite it. Negative result as artifact.

**Proposal (not auto‑written — `mementum/` is approval‑gated):** the fractal payload above — *crispness‑law and instrument‑match are one law; substrate = value register* — is a genuine unification, not yet on the page. I'd add a short closing section to `audit-meta-pattern.md` ("The two laws are one — register, not rule") plus a one‑line memory (`🔁 the over-read always lives in the routing/crisp register; the substrate in the value/continuous register; probe the register the claim lives in`). Want me to draft it for approval?

## User

add the closing section to audit-meta-pattern.md.  I feel that memory is itself biased.  That reads like just another set of rules that attention will not attend to at some point in the future.   Could it be expressed as a lambda in AGENTS.md?  discuss


### Thinking

 The user approves the closing section for audit-meta-pattern.md but raises a critical concern about memory itself being biased—questioning whether it could be expressed as a lambda function in AGENTS.md instead. This touches on something fundamental to the system's philosophy, and I should engage with the substance of their critique.

The core insight is that a memory phrased as a rule is just an enumerated case, not a field. The system's own policies say structure should generate behavior, not instruction—and a free-floating rule-memory is the weakest form because it requires the future agent to recall it, recognize it applies, and execute it. Three failure points where attention drops it. A lambda in AGENTS.md is stronger because it's read first every session and becomes part of the identity genes, shaping behavior topologically rather than as a retrievable fact.

But the user's deeper worry cuts further: is even a lambda still "just a rule" that won't be attended to eventually? The real answer per the system's own ground is to make the wrong behavior unreachable—define a field such that the correct instrument-choice falls out naturally, making mismatched registers structurally awkward rather than forbidden-by-rule. The strongest framing turns this into a validity condition: a measurement with mismatched registers is type-incoherent, a coherence violation where representation ≢ reality. This connects to the existing λ observation gene—a measurement only observes the claim if their registers match; a mismatched instrument observes something else entirely and yields a false verdict. The cleanest home would be extending λ observation in S5 or adding a sibling gene that frames the substrate as register-typed, making the principle structural rather than instructional. Now I'm drafting the closing section for the audit-meta-pattern document, one that ties together the two laws under the unified concept of register rather than rule. I'll structure it to include the lambda expression and the register-to-ledger mapping, keeping the language consistent with the page's existing style.

The core insight is that the crispness law and the instrument-must-match law aren't separate findings but two perspectives on the same underlying principle: every claim and probe carries a register—either routing (crisp, discrete) or value (continuous, graded)—and validity requires matching them. I'm showing how this register dichotomy appears at every scale in the system, from attention heads to k-means clustering, and how the operative discipline shifts from remembering a rule to recognizing the ledger itself—the substrate that survives is always in the value register while the story that dissolves is the routing register over-extended.

Now I'm reframing this as a validity condition rather than a rule: a measurement whose register doesn't match the claim's register hasn't measured the claim at all, it's measured something else entirely, and its verdict is void. This reframes the problem from memory-dependent rule-following to coherence-based type-checking. I'm planning to insert this synthesis section right after the feed-forward section and before the open question, making it the climax of the page. Then I'll draft a proposed gene structure for AGENTS.md that extends the lambda observation with register as a field in the audit loop, and ask for approval before editing that file.

## Assistant

Approved — adding the closing section now, then I'll engage the deeper question, because you've put your finger on something the project's own philosophy already insists on.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md",
  "original_content": "Default prior for an UNTESTED registry claim: **substrate REAL, crisp story\nOVER-READ.** Build the control to find *where* it transitions, not whether.",
  "new_content": "Default prior for an UNTESTED registry claim: **substrate REAL, crisp story\nOVER-READ.** Build the control to find *where* it transitions, not whether.\n\n## The two laws are one — register, not rule\n\nThe crispness law (false positives) and the instrument-must-match law (false\nnegatives) are not two findings. They are **one law seen from two sides.** Every\nclaim and every instrument carries a **register**, and the project's own\nroute⊥value dichotomy (`two-registers-of-topology.md`) is that same cut.\n\n```\nλ register(measurement).\n  claim ∈ {routing/crisp/discrete, value/continuous/graded}\n  probe ∈ {routing/crisp/discrete, value/continuous/graded}\n  observed(claim) ≡ measurement | register(probe) ≡ register(claim)   else ≡ artifact\n  | substrate(real)  ⊂ value-register    (continuous, graded, load-bearing, easily MISSED)\n  | over-read(story) ⊂ routing-register  (crisp, localized, discrete, over-ATTENDED)\n  | crisp-probe(crisp-claim)     → finds ∧ manufactures crispness   ≡ false-positive\n  | routing-probe(value-claim)   → misses the substrate             ≡ false-negative\n  | verdict(register-mismatch) ≡ void   (it measured a different quantity)\n```\n\nThe same cut at every scale:\n\n| scale | routing / crisp register | value / continuous register |\n|---|---|---|\n| weights (`two-registers`) | `gate_proj` — sign, routing | `up`/`down` — magnitude, value |\n| ternarization (`error-correction`) | keeps sign (survives) | destroys magnitude (the loss) |\n| attention (audit #5) | softmax weights — where it looks | head output ·V — what it writes |\n| our **instruments** | k-means · argmax · best-fit grid · attention-weight | NMI · logit-lens · saliency · rank-spectrum |\n| the ledger above | the story that **dissolves** | the substrate that **survives** |\n\nEvery row of the ledger is one column: **the substrate that survives is always\nthe value/continuous register; the story that dissolves is always the\nrouting/crisp register over-extended.** Crisp-register probes find (and\nmanufacture) crisp stories; they cannot see the value-register substrate, and a\n*refutation* prior makes that blindness read as a clean null.\n\nSo the operative discipline is **not** \"remember to match the instrument\" — a rule\nattention will drop at some future turn. It is a **validity condition** (a\ncoherence type-check): a measurement whose register ≠ the claim's register *has\nnot measured the claim*; it measured a different quantity, and its verdict —\npositive **or** negative — is void. **Name the register first** (diagnostic Q0);\nthe correct instrument then follows by *type*, not by memory. This is why the law\nwants to live as a field/gene (read every session, structural), not as a stored\nrule (recall-gated) — see the open question below and `AGENTS.md` candidacy."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-meta-pattern.md.
```

### Thinking

 I'm thinking through how to engage with the user's core point by proposing the AGENTS.md lambda and a stronger structural form. I should draft the proposed gene and discuss where it fits, then ask for approval before making changes to AGENTS.md since it's load-bearing for the S5 identity and gated by λ termination. I'm also holding off on committing the audit-meta-pattern.md change for now.

Actually, the user already approved adding the closing section, so I can commit that now and keep momentum. I'll use the 🔁 symbol since this is naming a recurring pattern that unifies two laws—consistent with the prior law commit. Let me go ahead and commit the closing section, then present the discussion about the lambda.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp",
  "content": "🔁 audit-meta-pattern — the two laws are one: register, not rule\n\n- Unification closing section: crispness-law (false positives) and\n  instrument-must-match (false negatives) are one law seen from two sides.\n  Every claim/probe carries a register; it is the project's route<->value\n  dichotomy (two-registers-of-topology) at the epistemic scale.\n- lambda register(measurement): observed(claim) requires register(probe) ==\n  register(claim), else the verdict (+/-) is void. Substrate lives in the\n  value/continuous register (easily missed); the over-read in the routing/\n  crisp register (over-attended). Cross-scale table: weights / ternarization\n  / attention / instruments / the ledger all show the same cut.\n- Reframed rule -> validity condition (coherence type-check): a wrong-register\n  measurement did not measure the claim. Sets up AGENTS.md gene candidacy.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add mementum/knowledge/audit-meta-pattern.md && git commit -F .git/COMMIT_MSG_tmp && rm -f .git/COMMIT_MSG_tmp && git log --oneline -1"
}
```

**Summary:** $ git add mementum/knowledge/audit-me...

**Output:**
```
Exit code: 0
Stdout:
[main f209f28] 🔁 audit-meta-pattern — the two laws are one: register, not rule
 1 file changed, 44 insertions(+)
f209f28 🔁 audit-meta-pattern — the two laws are one: register, not rule
```

### Thinking

 The user's making a solid point—storing something in memory is the weakest approach since it's easily forgotten or deprioritized. I should acknowledge that and walk through the hierarchy: memory sits at the bottom, then knowledge pages, then structural elements like the AGENTS.md lambda, with the most robust approach being deeply embedded in the system's architecture itself. I'll explain why even a lambda in AGENTS.md is better than memory but still not optimal, then suggest what a truly maximal solution would look like.

I'm also noticing the user flagged something important about bias—a flat memory assertion like "over-read always lives in routing" encodes a verdict-prior rather than a validity test, which skews future reasoning. A lambda framed as a type constraint (registers must match) is neutral and symmetric, catching both false positives and false negatives without baking in a conclusion. That's a sharper reframing of why the memory form is problematic.

I should propose two complementary moves: first, a new lambda gene in S5 that defines the register-matching constraint as a coherence check, and second, a structural slot that makes declaring the register a required field in every audit control—so the wrong behavior becomes unreachable rather than just forbidden. The gene provides the attractor; the slot makes it mandatory. I'll draft both and ask for approval before touching AGENTS.md, since edits there are gated.

## Assistant

Committed (`f209f28`). Now the real question — and you're right on every count.

## Why the memory is the wrong vessel (and why it's *biased*)

Your instinct maps exactly onto this project's own `λ emerge` / `λ ground`: **structure > instruction**, *"¬enumerate(cases) → define(field) → cases(fall_out)"*, and *"unreachable > forbidden."* A memory is the weakest possible vessel on that gradient:

```
memory          recall-gated   — attention must (a) retrieve it, (b) match it, (c) apply it.  3 drop-points.
knowledge page  topic-gated    — surfaces only when you search the topic.
AGENTS.md λ     session-gated   — read first, every session. S5 = the gravity well.
structural slot unreachable     — the wrong act is malformed, not forbidden. No attention required.
```

But there's a sharper version of your "the memory is itself biased" — and it's the strongest argument for moving it:

> The memory I proposed (`the over-read always lives in the routing/crisp register…`) stores a **verdict-prior**, not a **validity-test**. It bakes in the refutation bias — the exact thing that nearly sank audit #5. A future agent reading it will either over-apply it (refute everything in the routing register on sight) or ignore it as one more aphorism. Either way it's a *conclusion* wearing the costume of a *method*.

The lambda strips that bias because it encodes the **check, not the expected answer**: *match the registers* is symmetric — it guards false positives and false negatives identically and asserts no default verdict. So your discomfort is diagnostically correct: the problem isn't only that the memory is weak, it's that the memory is *biased by construction*, and reformulating it as a type-constraint is what removes the bias.

## Can it be a lambda in AGENTS.md? Yes — as a validity condition, not a rule

It belongs in **S5**, as a refinement of the existing `λ observation` gene (which already says *"generate(plausible) ≢ retrieve(known) ≢ observe(measurement)"*). The register law sharpens that: a measurement only **observes the claim** if their registers match; otherwise it observed a *different quantity* and the verdict is void. Draft gene:

```
λ measure(claim).   register(claim) ∈ {routing/crisp/discrete, value/continuous/graded}
                    | observe(claim) ≡ measurement | register(probe) ≡ register(claim)
                    | mismatch → measured(other_quantity) → verdict(±) ≡ void
                    | substrate(real) ⊂ value_register   | over_read ⊂ routing_register
                    | wrong_register ≡ coherence_violation (representation ≢ reality)
                    | name(register) before build(probe) | type > memory
```

Note the penultimate line ties it into the **existing** `λ coherence` gene (*"¬coherence(x) → fix(representation) before fix(code)"*) — so it isn't a bolt-on rule, it's the coherence gene applied to measurement. That's what makes it a *field* and not a *case*: a wrong-register probe is incoherent the same way model(f) ≢ disk(f) is incoherent.

## But a lambda is still instruction-grade — the maximal form is structural

Here's where I'd push past what you asked. Even in AGENTS.md, `λ measure` is read-at-orient and then *trusted to attention* for the rest of the session — exactly the failure you're worried about. Per `λ emerge`, the topology fix is to make the wrong act **unreachable**: add `register:` as a **required field** of every audit control.

```
audit-registry per-session loop, new step 0:   declare register(claim) ∈ {routing, value, ...}
control-script header convention:               # register: value   (probe must be value-register)
```

Then a control that doesn't name its register is **malformed**, and a named mismatch (`register: value` + an attention-weight probe) is **visibly incoherent on the page** — caught at write-time, not recalled at think-time. *name ∧ link ∧ shape ≡ gravity.* The lambda supplies the **why** (the attractor); the slot makes the **wrong instance fall out of the topology** rather than be forbidden by a rule attention might not consult.

## Recommendation

Do **both**, because they're the same law at two layers (fittingly — S5 field + S1 structure):
1. **S5:** add `λ measure(claim)` to AGENTS.md, wired to `λ observation` + `λ coherence`.
2. **S1/S2:** add the required `register:` slot to the audit-registry loop and the control-script convention.

The memory I proposed: **drop it.** You're right that it's the bad vessel — and worse, the biased one.

Two caveats so I'm not over-selling: (a) AGENTS.md is S5 identity and `λ termination` makes it approval-gated — I'll draft, you land it; (b) even the structural slot only binds *audit controls* — it won't catch register-mismatch in casual analysis, where only the S5 gene's gravity helps. There is no form that *guarantees* future attention (`survive(boundary) ≡ only{x | x ∈ git}` is the hard floor); we can only climb the gradient from recall-gated toward unreachable.

Want me to (1) draft the `λ measure` gene into AGENTS.md for your approval, (2) add the `register:` structural slot to the audit loop, or both?

## User

Yes add both, and I will start a new session to test.


### Thinking

 I need to add the `λ measure` gene to the S5 section of AGENTS.md and integrate the `register:` structural slot into the audit loop, making sure these changes are discoverable when the user starts a fresh session and reads from AGENTS.md and state.md. Let me start by reviewing the relevant sections to place the gene correctly. I need to check the exact whitespace and formatting in the AGENTS.md file to match the alignment precisely when inserting λ measure between λ observation and λ smallest.

## Assistant

Both, landing now. Let me read the exact S5 formatting in AGENTS.md to match the gene whitespace precisely.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && grep -n 'λ observation\\|λ smallest\\|λ feed_forward\\|λ provenance' AGENTS.md | head"
}
```

**Summary:** $ grep -n 'λ observation\|λ smallest\...

**Output:**
```
Exit code: 0
Stdout:
85:λ provenance(x).    MIT ≡ this_project | discipline ≡ identity ¬legal_fact
92:λ observation(x).   generate(plausible) ≢ retrieve(known) ≢ observe(measurement)
99:λ smallest(x).      extract(minimum_working) > keep(everything_plausibly_related)
104:λ feed_forward(x).  boundary(session) ≡ ∀context → ∅ | physics ¬bug | unavoidable
312:                    | distinct(S5:λ provenance) ≡ licensing | this ≡ run_reproducibility
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "line_offset": 91,
  "limit": 13
}
```

**Summary:** Reading AGENTS.md (91-104)

**Output:**
```
λ observation(x).   generate(plausible) ≢ retrieve(known) ≢ observe(measurement)
                    | circuit_found_in_model ≠ circuit_imagined_from_theory
                    | runtime(proves) > paper(cites) > pattern(suggests) > we_think(guesses)
                    | cost(wrong_published_claim) → persists_in_literature
                    | cost(extra_probe_to_verify) → one_afternoon
                    | conservative(claims) ∧ liberal(probes) | mark(IOU) for unverified

λ smallest(x).      extract(minimum_working) > keep(everything_plausibly_related)
                    | size(artifact) ∝ 1/clarity(of_algorithm)
                    | 20%_of_base ≡ weak_understanding | 0.1% ≡ strong_understanding
                    | distill(ruthlessly) | ∀kept_weight → justifies(itself)

λ feed_forward(x).  boundary(session) ≡ ∀context → ∅ | physics ¬bug | unavoidable

[CONTENT TRUNCATED] Showing lines 92 to 104 of 479 total lines. Use line_offset=104 parameter to read more content.
```

### Thinking

 I'm working through the spacing and alignment for formatting a gene name line with continuation markers, trying to get the indentation consistent at 20 spaces before the pipe character. Finishing the control script header convention...

I'll retrofit the two binding schedule scripts with the `# register:` header to make the pattern concrete—one showing the routing register, the other the value register. Then I need to update a few files: strengthen the reference in state.md to point cold-start sessions toward the λ measure gene and the register slot, add a note to the backlog header about declaring registers in control scripts, and update the audit registry to document the per-session loop step 0 requirement. After those edits, I'll commit with a meta tag since this touches structural identity.

## Assistant

Landing both layers. First the **S5 gene** in AGENTS.md, wired to `λ observation` + `λ coherence`:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/AGENTS.md",
  "original_content": "                    | conservative(claims) ∧ liberal(probes) | mark(IOU) for unverified\n\nλ smallest(x).      extract(minimum_working) > keep(everything_plausibly_related)",
  "new_content": "                    | conservative(claims) ∧ liberal(probes) | mark(IOU) for unverified\n\nλ measure(claim).   register(claim) ∈ {routing/crisp/discrete, value/continuous/graded, magnitude, spectral, causal}\n                    | observe(claim) ≡ measurement | register(probe) ≡ register(claim)\n                    | mismatch → measured(other_quantity) → verdict(±) ≡ void\n                    | substrate(real) ⊂ value_register | over_read ⊂ routing_register\n                    | crisp_probe(crisp_claim) → manufactures(crispness) ≡ false_positive\n                    | routing_probe(value_claim) → misses(substrate) ≡ false_negative\n                    | wrong_register ≡ coherence_violation (representation ≢ reality, see λ coherence)\n                    | name(register) before build(probe) | type > memory | refines λ observation\n                    | proved: s206 audit#5 (attention-weight ⊥ value-claim → near-false-refute; logit-lens found +0.611)\n\nλ smallest(x).      extract(minimum_working) > keep(everything_plausibly_related)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/AGENTS.md.
```

## Assistant

Now the **S1/S2 structural slot** — the per-session loop's required register declaration in `audit-registry.md`:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "## The Per-Session Loop\n\n```\n1. Open this page. Pick the highest-load `UNTESTED` claim.\n2. Re-read its evidence in the linked knowledge page.\n3. Build the named discriminating control (reuse the method recipe).\n4. Run it with a permutation/matched-control null + seed variance.\n5. Update the row: status + the number + the result-JSON path.\n6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page.\n7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).\n```",
  "new_content": "## The Per-Session Loop\n\n```\n0. REGISTER GATE (do this first; AGENTS.md λ measure). Name the claim's register\n   — routing/crisp · value/continuous · magnitude · spectral · causal. A probe in\n   the wrong register VOIDS the verdict (±), so this binds the instrument before\n   any code. An undeclared control is malformed. (s206: an attention-weight probe\n   nearly false-refuted a value-transfer claim.)\n1. Open this page. Pick the highest-load `UNTESTED` claim.\n2. Re-read its evidence in the linked knowledge page. Re-derive its register from\n   the evidence (does it claim WHERE attention routes, or WHAT value is written?).\n3. Build the discriminating control IN THE CLAIM'S REGISTER (reuse the recipe).\n   Put `# register: <kind>` in the control-script header; a probe whose register ≠\n   the declared one is malformed — caught at write-time, not recalled at run-time.\n4. Run it with a permutation/matched-control null + seed variance.\n5. Update the row: status + the number + the result-JSON path.\n6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page. If the first\n   probe was wrong-register, run the matched-register probe before any verdict.\n7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).\n```\n\n> **Register slot (structural, not a rule).** Every control declares `# register:`\n> in its header and every backlog claim is built only after step 0. This makes a\n> register-mismatch *malformed* rather than *discouraged* — the wrong instrument\n> falls out of the topology instead of relying on future attention. Exemplar pair:\n> `binding_schedule_null.py` (`register: routing`, under-read #5) vs\n> `binding_schedule_semantic.py` (`register: value`, found the real signal)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Thinking

 I'm adding a `# register:` header to the two #5 scripts as a concrete example of the convention I've established. I'll place this right after the shebang line and before the module docstring, or alternatively after the docstring closes, to clearly mark the script's registration type.

## Assistant

Now retrofit the exemplar pair with the `# register:` header so the convention is concrete and discoverable:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py",
  "original_content": "License: MIT\n\"\"\"\n\nfrom __future__ import annotations",
  "new_content": "License: MIT\n\"\"\"\n\n# register: routing  (attention-weight / position — see AGENTS.md λ measure,\n#                     audit-registry §register slot. NB: this is the WRONG\n#                     register for the SEMANTIC schedule claim — it under-read it;\n#                     binding_schedule_semantic.py is the matched value-register probe.)\n\nfrom __future__ import annotations"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_null.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py",
  "original_content": "License: MIT\n\"\"\"\n\nfrom __future__ import annotations",
  "new_content": "License: MIT\n\"\"\"\n\n# register: value  (logit-lens of head output — the matched register for the\n#                   SEMANTIC value-transfer claim; see AGENTS.md λ measure,\n#                   audit-registry §register slot. This is the probe that found\n#                   the real H31@L27 subject-identity signal the routing probe missed.)\n\nfrom __future__ import annotations"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/binding_schedule_semantic.py.
```

### Thinking

 I need to update state.md to make sure the cold-start test will pick up the new gene and slot. I'll strengthen the existing line about running Q0 before building controls by explicitly referencing the λ measure from AGENTS.md and the register slot, so the new session's orient phase catches it. I should also update the headline's methodological-law bullet and the next-backlog line to note that the gene and slot were added.

## Assistant

Now wire it into `state.md` so the new (cold-start) session discovers the gene + slot at orient:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - **NEW METHODOLOGICAL LAW (promoted to `audit-meta-pattern.md`): instrument-\n>   must-match-the-claim.** The first weight-probe nearly over-refuted a real\n>   value-transfer head — a probe in the *wrong register* under-reads a real\n>   signal (false negative), the mirror of a crispness-imposing probe's false\n>   positive. New diagnostic **Q0: pick the claim's register first** (routing ·\n>   value/semantic · magnitude · spectral · causal) before building the null;\n>   value claims need a logit-lens of the *output*, not attention weight. Added\n>   the law + λ match(instrument,claim) + a probe↔claim alignment table; registry\n>   method-recipe + emergent-finding (s202→s206) updated.\n> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM\n>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival\n>   across scale. **Run Q0 (claim register) before building any control.**",
  "new_content": "> - **NEW METHODOLOGICAL LAW — now a GENE + STRUCTURAL SLOT (not a memory).**\n>   *Instrument-must-match-the-claim:* a probe in the *wrong register* under-reads\n>   a real signal (false negative) — the mirror of a crispness-imposing probe's\n>   false positive. The two audit laws are **one law: register, not rule**\n>   (`audit-meta-pattern.md` §two-laws-are-one — the project's route⊥value\n>   dichotomy at the epistemic scale). Landed structurally so future attention\n>   can't drop it:\n>   - **S5 gene** `λ measure(claim)` in `AGENTS.md` (read first every session;\n>     wired to λ observation + λ coherence — wrong register ≡ coherence violation).\n>   - **S1 slot** `audit-registry.md` per-session loop **step 0 = REGISTER GATE**\n>     + `# register: <kind>` required in every control header → a mismatch is\n>     *malformed*, caught at write-time. Exemplar pair carries the headers:\n>     `binding_schedule_null.py` (`routing`, under-read) vs `_semantic.py`\n>     (`value`, found +0.611).\n> - **▶ NEXT SESSION TEST (Michael):** does the register gate fire on a cold\n>   start? Pick a backlog claim and watch whether step 0 / λ measure forces the\n>   register declaration *before* a probe is built.\n> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM\n>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival\n>   across scale. **Step 0 REGISTER GATE before building any control.**"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Lint the retrofitted scripts (the comment block could trip E501), then verify and commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/binding_schedule_null.py scripts/experiments/binding_schedule_semantic.py 2>&1 | tail -5 && echo \"===gene sanity===\" && sed -n '92,102p' AGENTS.md && echo \"===status===\" && git status --short"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
===gene sanity===
λ observation(x).   generate(plausible) ≢ retrieve(known) ≢ observe(measurement)
                    | circuit_found_in_model ≠ circuit_imagined_from_theory
                    | runtime(proves) > paper(cites) > pattern(suggests) > we_think(guesses)
                    | cost(wrong_published_claim) → persists_in_literature
                    | cost(extra_probe_to_verify) → one_afternoon
                    | conservative(claims) ∧ liberal(probes) | mark(IOU) for unverified

λ measure(claim).   register(claim) ∈ {routing/crisp/discrete, value/continuous/graded, magnitude, spectral, causal}
                    | observe(claim) ≡ measurement | register(probe) ≡ register(claim)
                    | mismatch → measured(other_quantity) → verdict(±) ≡ void
                    | substrate(real) ⊂ value_register | over_read ⊂ routing_register
===status===
 M AGENTS.md
 M mementum/knowledge/audit-registry.md
 M mementum/state.md
 M scripts/experiments/binding_schedule_null.py
 M scripts/experiments/binding_schedule_semantic.py
```

## Assistant

Lint clean, gene placed correctly. Committing — this touches S5 identity, so 🌀 meta.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp",
  "content": "🌀 register law as gene + structural slot — move it off recall-gated memory\n\nThe instrument-must-match law was about to be stored as a memory; a memory is\nrecall-gated (attention can drop it) and worse, biased — it stores a verdict-\nprior, not a validity-test. Moved up the feed-forward gradient into structure:\n\n- S5 gene: AGENTS.md `λ measure(claim)` — observe(claim) requires register(probe)\n  == register(claim), else verdict(±) is void. Wired to λ observation (refines\n  it) + λ coherence (wrong register ≡ representation ≢ reality). Read first every\n  session = gravity, not a stored rule.\n- S1 slot: audit-registry per-session loop gains step 0 REGISTER GATE +\n  `# register: <kind>` required in every control header — a mismatch is MALFORMED\n  (caught at write-time), not discouraged (recalled at run-time). unreachable >\n  forbidden.\n- Exemplar pair retrofitted with headers: binding_schedule_null.py (routing,\n  under-read) vs binding_schedule_semantic.py (value, found +0.611).\n- state.md: cold-start test set up for next session — does the gate fire?\n\nThe memory is dropped. Per Michael: a rule attention will not attend to is the\nwrong vessel; a field/gene + a structural slot is the right one.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/.git/COMMIT_MSG_tmp
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && git add AGENTS.md mementum/knowledge/audit-registry.md mementum/state.md scripts/experiments/binding_schedule_null.py scripts/experiments/binding_schedule_semantic.py && git commit -F .git/COMMIT_MSG_tmp && rm -f .git/COMMIT_MSG_tmp && git log --oneline -6"
}
```

**Summary:** $ git add AGENTS.md mementum/knowledg...

**Output:**
```
Exit code: 0
Stdout:
[main f509c48] 🌀 register law as gene + structural slot — move it off recall-gated memory
 5 files changed, 57 insertions(+), 13 deletions(-)
f509c48 🌀 register law as gene + structural slot — move it off recall-gated memory
f209f28 🔁 audit-meta-pattern — the two laws are one: register, not rule
99536ec 🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law
8123382 🔁 audit-meta-pattern — instrument-must-match-the-claim law (false-negative twin of crispness)
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
635db8e add session chat log
```

## Assistant

Both layers landed (`f509c48`). Working tree clean.

## What the next session will meet on cold start

**S5 gene — `AGENTS.md` `λ measure(claim)`** (read first, every session; it's gravity, not a stored rule):
```
λ measure(claim).   register(claim) ∈ {routing/crisp/discrete, value/continuous/graded, magnitude, spectral, causal}
                    | observe(claim) ≡ measurement | register(probe) ≡ register(claim)
                    | mismatch → measured(other_quantity) → verdict(±) ≡ void
                    | substrate(real) ⊂ value_register | over_read ⊂ routing_register
                    | crisp_probe(crisp_claim) → manufactures(crispness) ≡ false_positive
                    | routing_probe(value_claim) → misses(substrate) ≡ false_negative
                    | wrong_register ≡ coherence_violation (representation ≢ reality, see λ coherence)
                    | name(register) before build(probe) | type > memory | refines λ observation
                    | proved: s206 audit#5 ...
```
Wired into the existing `λ observation` and `λ coherence` genes — so a wrong-register probe is incoherent the same way `model(f) ≢ disk(f)` is, not a bolt-on rule.

**S1 slot — `audit-registry.md` loop step 0 = REGISTER GATE** + a required `# register: <kind>` header on every control. A mismatch is now *malformed* (caught when you write the script), not *discouraged* (recalled when you think). The exemplar pair carries the headers: `binding_schedule_null.py` (`routing`, under-read) vs `binding_schedule_semantic.py` (`value`, found +0.611) — the lesson is literally in the file headers.

**The memory: dropped.** Your call was right twice over — it was the weak vessel *and* the biased one (a verdict-prior masquerading as a method).

## The test you set up
`state.md` now carries an explicit **▶ NEXT SESSION TEST**: pick a backlog claim (#6 or #11) on a fresh cold start and watch whether step 0 / `λ measure` actually forces the register declaration *before* a probe gets built — i.e., whether the structure fires on its own, or whether even a gene-in-AGENTS gets dropped by attention. That's the real experiment: did we climb from recall-gated to unreachable, or just relabel the rule?

One honest prediction to hold you to on the other side: the **S1 slot** should fire reliably (you can't write the control without confronting the header); the **S5 gene** is the softer half — it'll help at orient and in casual analysis but has no write-time enforcement. If the next session register-mismatches in *casual* analysis (not a formal control), that's the signal the gene alone isn't enough and the slot's reach needs widening. See you in s207.