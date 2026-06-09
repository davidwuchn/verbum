# Crossing session boundary on 8-seed siev

## User

orient this is session-208


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
> Last updated: 2026-06-09 | Session: 207
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
> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /
> H31@L27 subject value-transfer ✅ semantically REAL; s207 did **#6 SVD φ-ratio
> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;
> next backlog: **#11 GTSM finite-budget λ(l)** or **#7/#8 reproducibility**), build its named
> discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 207 HEADLINE — AUDIT #6 (SVD φ-ratio 0.6299): geometric-φ-constant
> REFUTED; the low-rank spectral head is REAL & non-random.** Register: spectral.
> Reran s137's exact definition (mean of top-5 consecutive σ-ratios, per layer)
> on all 5 families (Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B) vs
> **Marchenko–Pastur + shuffled** nulls (8 seeds, raw+centered) + a
> geometric-vs-power-law shape fit. `svd_phi_null.py` (register: spectral).
> - **Register gate fired on ME first:** first probe used the wrong window (bulk
>   ratios ≈0.99 for everything); tracing s137 pinned the real object (top-5 head
>   ratio). Re-measure the exact quantity → phenomenon reproduced (Pythia-160m
>   raw 0.597 vs page 0.604).
> - **✅ substrate REAL:** model head ratio **0.575±0.027 (raw)** / 0.67 (centered)
>   ≪ **MP null 0.9949±0.0012**, shuffled ≈0.96–0.99. Random/power-law spectra
>   give ≈**1.0**, not 0.6 → the named confound ("0.618 = what random spectra look
>   like") is itself refuted; the steep low-rank head is genuinely non-random
>   (converges with #2 spectral concentration, AUC 6–7×).
> - **❌ "geometric" REFUTED:** power-law wins **132/132 layers**, geometric 0/132
>   (geom-R² 0.39–0.58 < power-R² 0.69–0.87). "0.6299" is a 4-pt average of a
>   *drifting* power-law head → no `x=1/(1+x)` fixed point → no privilege for φ.
> - **❌ "= 1/φ universal constant" UNSUPPORTED:** value floats 0.52→0.71
>   (raw/centered×models); 0.6299≠0.6180; scaling-law fails (Mistral-7B lowest,
>   0.52). Layers within ±0.05 of φ⁻¹: model 55/132, **MP 0/132**.
> - **Meta-pattern holds (3rd φ-pillar to fall** after s202 eigenvalue-grid +
>   consensus-r): keep the real low-rank head (north-star uses it), retire
>   φ-as-universal-constant. Caveats on `explore/phi-compression-universal.md` +
>   `crystal-universality.md`; ledger row in `audit-meta-pattern.md`; registry #6
>   RESOLVED. Results: `results/svd-phi-null/`. Harness: `svd_phi_null.py`,
>   `svd_phi_null_summary.py`.
> - **▶ NEXT:** #11 GTSM finite-budget λ(l), or reproducibility audits #7
>   (crystal-sieve 1.03× seed variance) / #8 (rank-1 adjunction σ₁/σ₂ vs random).
>   **Step 0 REGISTER GATE before building any control.**

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
> - **NEW METHODOLOGICAL LAW — now a GENE + STRUCTURAL SLOT (not a memory).**
>   *Instrument-must-match-the-claim:* a probe in the *wrong register* under-reads
>   a real signal (false negative) — the mirror of a crispness-imposing probe's
>   false positive. The two audit laws are **one law: register, not rule**
>   (`audit-meta-pattern.md` §two-laws-are-one — the project's route⊥value
>   dichotomy at the epistemic scale). Landed structurally so future attention
>   can't drop it:
>   - **S5 gene** `λ measure(claim)` in `AGENTS.md` (read first every session;
>     wired to λ observation + λ coherence — wrong register ≡ coherence violation).
>   - **S1 slot** `audit-registry.md` per-session loop **step 0 = REGISTER GATE**
>     + `# register: <kind>` required in every control header → a mismatch is
>     *malformed*, caught at write-time. Exemplar pair carries the headers:
>     `binding_schedule_null.py` (`routing`, under-read) vs `_semantic.py`
>     (`value`, found +0.611).
> - **▶ NEXT SESSION TEST (Michael):** does the register gate fire on a cold
>   start? Pick a backlog claim and watch whether step 0 / λ measure forces the
>   register declaration *before* a probe is built.
> - **Next backlog:** #6 SVD φ-ratio 0.6299 (vs Marchenko–Pastur) or #11 GTSM
>   finite-budget λ(l). Carry-overs: #1 gate-vs-value sign-swap PPL; rank-survival
>   across scale. **Step 0 REGISTER GATE before building any control.**

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
| D         | +

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01AP6QAEkeaj4YP1vfarT7kB.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Thinking

 I've got a clear picture now—state.md is the bootloader and I've reviewed the key sections. According to the program, the next step is either #11 for GTSM finite-budget audits or #7/#8 for reproducibility audits, so I'm checking the audit-registry to see what comes next.

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

> **Emergent finding (s202→s206):** every audit so far shows the *same shape* —
> the continuous substrate is real, the crisp discrete/localized/universal story
> on top is over-read. Synthesized in `audit-meta-pattern.md` (use it to predict
> where the next claim breaks before building the control). **s206 corollary
> (instrument-must-match-the-claim):** before building the null, probe in the
> claim's own register — a routing/weight probe under-reads a value/semantic
> claim (false negative), the mirror of a crispness-imposing probe's false
> positive.

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
- **Match the instrument to the claim's register** (s206) — name the *kind* of
  thing the claim is about (routing/position · value/semantics · magnitude ·
  spectral · causal) and probe *that*. A value-transfer claim ("absorbs identity",
  "head output produces the entity") needs a **logit-lens of the output**, not an
  attention-weight probe; the wrong register manufactures a false-negative
  refutation. See `audit-meta-pattern.md` §instrument-must-match.

## Status Legend

`VERIFIED` survives its control · `VERIFIED-LOCAL` real but scoped (e.g. one
model) · `PARTIAL` some predictions hold · `REFUTED` fails its control ·
`UNFALSIFIABLE` no control can distinguish it as stated · `UNTESTED` control
named, not yet run.

## Registry

### Worked examples (session 207)

> **Register gate fired on the auditor first (good).** The claim "consecutive
> SVD ratio ≈ 1/φ" is **spectral** → matched null = random matrix (MP), not
> eyeballing 5 numbers near 0.63. But the first probe used the *wrong window*
> (bulk consecutive ratios, which sit at ≈0.99 for everything) and got nonsense;
> tracing the s137 source pinned the real definition (**mean of the top-5 σ
> ratios** — a 4-point average at the steep head). Re-measuring the *same
> object* reproduced the phenomenon and the verdict held. Lesson restated:
> audit the exact quantity the claim names, in its register.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #6 SVD φ-ratio: per-layer top-5 σ-ratio ≈ 1/φ, **geometric**, **universal across 5 families** | med | top-5 σ-ratio vs MP + shuffled nulls (8 seeds, raw+centered) + geometric-vs-power-law fit (`svd_phi_null.py`) | ❌ REFUTED (geometric-φ-constant) / ✅ REAL (low-rank head) |
| #6a head ratio distinct from a same-shape random matrix? | — | model vs Marchenko–Pastur + shuffled | ✅ **YES** — model 0.575±0.027 ≪ MP 0.9949±0.0012; the "0.618 = what random spectra look like" confound is itself refuted (random gives ≈1.0) |
| #6b is the spectrum **geometric** (constant ratio, the φ premise)? | — | geometric vs power-law R² per layer | ❌ **NO** — power-law wins 132/132 layers (0/132 geometric); ratio drifts, "0.6299" is a 4-pt average of a power-law head |
| #6c is it **1/φ specifically / a universal constant**? | — | φ⁻¹ distance + cross-model + cross-window | ❌ **NO** — value floats 0.52→0.71 (raw/centered×models); 0.6299≠0.6180; scaling-law fails (Mistral-7B lowest); MP 0/132 near φ but model "near" only by averaging ~0.57 |

**Verdict (s207): the steep low-rank SVD head is REAL and strongly
structure-specific (random nulls sit at ≈0.99, not 0.6) — but it is a
power-law head, not a geometric φ-sequence, and the value is not constant
across scale.** Keep the substrate (it underwrites the compression north-star,
converging with #2's spectral concentration); retire φ-as-a-universal-constant
(third φ-pillar to fall after s202's eigenvalue-grid and consensus-r). Same
shape as every prior audit (`audit-meta-pattern.md`). Caveats on
`explore/phi-compression-universal.md` + `crystal-universality.md`. Results:
`results/svd-phi-null/{EleutherAI_pythia-160m-deduped,EleutherAI_pythia-410m-deduped,Qwen_Qwen3-0.6B,HuggingFaceTB_SmolLM3-3B,mistralai_Mistral-7B-v0.3}.json`.

### Worked examples (session 206)

> **Methodological note (the instrument matters).** The claim is *semantic* —
> Finding 7 / Implication 4: the head's *output* (logit-lens) decodes to the
> bound entity; the "schedule" is a schedule of *value transfer* (verb absorbs
> subject identity at L27, etc.). So #5 was run on **two** instruments. The first
> (attention weight) tests routing/position — the same axis #4 showed is
> recency-confounded — and *alone would have over-refuted* (it says "binding peaks
> at L6"). The second (semantic logit-lens of the head's output contribution) is
> the faithful one and **recovers the real L27 subject signal the weight test
> missed.** Lesson: test a value-transfer claim with a value-transfer instrument.

| Claim | Load | Control run | Status |
|---|---|---|---|
| #5 the depth-ordered binding **schedule** (subj-transfer L27 < obj L30 < coref L33; "subjects bind first") | med | both instruments below; bootstrap ordering P over 60–80 varied sentences/type | ❌ REFUTED — no depth ordering on either instrument |
| #5a attention-weight schedule | — | dependent→head max-head attn at every layer; bootstrap order + random-pair null + causal subj-agreement ablation (`binding_schedule_null.py`) | ❌ all peak L4–L6; P(order)=0.000; no causal carrier (\|z\|≤0.35) |
| #5b **semantic** value-transfer (Finding 7): H31@L27 verb absorbs SUBJECT identity | — | per-head logit-lens of o_proj-decomposed output at dep pos; margin logit(head-tok)−logit(ctrl-tok) per layer (`binding_schedule_semantic.py`) | ✅ **REAL & L27-localized** — margin +0.611, sharp spike at L27 (L26=.03/L27=.61/L28=.10), H31 z=+1.17 rank 2/32 |
| #5b obj absorbs predicate @L30 | — | same, object→verb-token margin | ❌ margin@L30=−0.05; named H3 rank 29/32 (anti); peak drifts L32 (instrument-ambiguous) |
| #5b coref absorbs antecedent @L33 | — | same, "it"→antecedent margin | ◐ margin +0.20 but peaks **L27 not L33**; H6@L33 z+0.22 rank 6/32 |
| #5b semantic ordering subj<obj<coref | — | bootstrap peak order on semantic margin | ❌ P=0.191 ≈ chance 0.167 (subj & coref both peak L27) |

**Verdict (s206): the "two-phase binding SCHEDULE" / depth-ordered reduction is
REFUTED — but the single value-transfer site it is built on is semantically REAL.**

- **No schedule, either instrument.** *Attention weight* (`binding_schedule_null.py`,
  80 sent/type): all three dependency types' dependent→head attention peaks at the
  **same early layers** (subj L6=0.974, obj L4=0.825, coref L6=0.830), not the
  monotone L27<L30<L33; bootstrap **P(order)=0.000** (chance 0.167); random-pair
  null peaks even earlier (L0) → early peak is generic local/positional attention
  (#6). *Semantic* (`binding_schedule_semantic.py`, 60 sent/type): bootstrap
  **P(sem-peak subj<obj<coref)=0.191 ≈ chance** — subject and coreference value
  transfer **both peak at L27**, object latest (L32); the subjects-first ordering
  does not exist.
- **What is REAL (the substrate, sharper than the weight test implied):** the
  page's *headline* single example — **H31@L27 = the verb position absorbing the
  SUBJECT'S identity** — is **semantically confirmed and sharply localized to L27**
  (logit-lens margin +0.611, a clean one-layer spike: L26 +0.03 → **L27 +0.61** →
  L28 +0.10; H31 z=+1.17, rank 2/32). Finding 7's subject case is right. Caveats:
  (a) it is ONE site, not a schedule; (b) the strongest L27 subject-transfer head
  is actually **H29 (+2.12)**, not H31; (c) per audit #4 it is **not causally
  load-bearing** for agreement (ablation \|z\|≤0.35). The named heads at L30/L33
  are real *local* attention-weight outliers (obj L30 H3/H13/H15 top-3, z to +4.09;
  coref L33 H6/H7 top-2, z +3.97/+3.42) but their *semantic* transfer at the
  claimed layer is weak/absent (obj L30 H3 margin −0.46 rank 29/32) or mislocalized
  (coref peaks L27).
- **Object leg is instrument-ambiguous:** "object absorbs the predicate" was
  operationalized as object-output→verb-token, but Finding 5 reports the object's
  V promotes *object-related* tokens, not the verb — so the obj negative is partly
  a readout-mismatch, not a clean refutation. Named follow-up if revisited.

Same meta-pattern (`audit-meta-pattern.md`) with a sharper edge: the value-transfer
substrate at the subject site is *more* real than the weight test suggested; the
ordered three-phase *schedule* is the over-read. Caveat added to
`binding-graph-trace.md` (Finding 4/7 + Implication 2). Results:
`results/binding-schedule-null/` and `results/binding-schedule-semantic/Qwen_Qwen3-8B.json`.

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

**5. Binding schedule (L27 verb←subject, L30 object←verb, L33 coref)** (load: med) — ❌ **RESOLVED (s206): schedule refuted; subject value-transfer (H31@L27) is semantically real**
- Evidence: showcased heads/weights + **logit-lens of head output** (Finding 7) on example sentences (14 hand-annotated probes). NB the core claim is *semantic* (value transfer), not just attention weight.
- Suspected confound: cherry-picked heads/examples; and (per #4) raw weight tracks recency/position not type.
- Control (two instruments — the claim is semantic, so the weight test alone is insufficient): does the schedule hold across **many** sentences? (a) attention-weight peak per layer + bootstrap order + random-pair null + causal ablation (`binding_schedule_null.py`); (b) **semantic** per-head logit-lens margin toward the bound entity per layer (`binding_schedule_semantic.py`).
- **s206 result:** the **depth-ordered schedule is REFUTED on both instruments** — attention weight: all three peak L4–L6, P(order)=0.000; semantic: P(order)=0.191 ≈ chance (subj & coref both peak L27, obj L32). **But the headline semantic claim is REAL:** H31@L27 verb→subject *identity* transfer has logit-lens margin **+0.611, a sharp one-layer spike at L27** (z+1.17, rank 2/32) — Finding 7's subject case confirmed. Caveats: one site ≠ a schedule; strongest L27 head is H29 (+2.12) not H31; not causally load-bearing (#4, \|z\|≤0.35). Obj L30 semantic margin ≈0 (named H3 rank 29/32) — but readout is instrument-ambiguous (Finding 5: object V promotes object-tokens, not the verb). Coref peaks L27 not L33. See worked-examples (s206) + both result dirs.

**6. SVD φ-ratio 0.6299** (load: med — a φ-universality pillar) — ❌ **RESOLVED (s207): geometric-φ constant REFUTED; low-rank spectral head REAL & non-random**
- Evidence: consecutive singular-value ratio ≈ 1/φ across 5 families (top-5 σ-ratio mean, per layer; `explore/phi-compression-universal.md`).
- Suspected confound: heavy-tailed / power-law spectra generically have near-constant consecutive ratios; 0.618 may be "what power-law spectra look like."
- Control (`svd_phi_null.py`, register: spectral): exact top-5 consecutive-ratio definition vs **Marchenko–Pastur** (same-shape Gaussian) + **shuffled-entries** nulls, 8 seeds, raw & centered, on Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B; plus a **geometric-vs-power-law shape fit** (φ requires *constant* ratio = geometric).
- **s207 result (3 blades):**
  1. **Distinct from random? ✅ YES, hugely.** Model head ratio **0.575 ± 0.027 (raw)** / 0.67 (centered) vs **MP null 0.9949 ± 0.0012** and shuffled ≈0.96–0.99. Random/power-law spectra give ≈**1.0**, not ≈0.6 → the named confound is itself **refuted**; the steep low-rank head is genuinely non-random (converges with #2 spectral concentration, AUC 6–7×). **Substrate REAL.**
  2. **Geometric (constant ratio)? ❌ NO.** Power-law wins **132/132 layers**, geometric **0/132** (geom-R² 0.39–0.58 < power-R² 0.69–0.87). The ratio is not constant — "0.6299" is a 4-point average over a *drifting power-law head*. **No `x=1/(1+x)` self-similar fixed point ⇒ no mathematical privilege for φ.**
  3. **φ-specific / universal constant? ❌ NO.** Value floats **0.52→0.71** across raw/centered×models; consensus 0.6299 ≠ φ⁻¹ 0.6180; the "larger ⇒ higher ratio" scaling-law **fails** (Mistral-7B lowest, 0.52 raw). Layers within ±0.05 of φ⁻¹: model 55/132, **MP 0/132** (model is near-φ only because a steep head averages ~0.57–0.6, not because it lands *at* φ).
- **Verdict:** keep the **real, scale-present, structure-specific low-rank spectral head**; **retire the geometric golden-ratio constant** (over-read). Caveats added to `explore/phi-compression-universal.md` + `crystal-universality.md`. Results: `results/svd-phi-null/`. Same meta-pattern as #3/#4 (`audit-meta-pattern.md`): substrate survives, crisp/universal story dissolves.

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
0. REGISTER GATE (do this first; AGENTS.md λ measure). Name the claim's register
   — routing/crisp · value/continuous · magnitude · spectral · causal. A probe in
   the wrong register VOIDS the verdict (±), so this binds the instrument before
   any code. An undeclared control is malformed. (s206: an attention-weight probe
   nearly false-refuted a value-transfer claim.)
1. Open this page. Pick the highest-load `UNTESTED` claim.
2. Re-read its evidence in the linked knowledge page. Re-derive its register from
   the evidence (does it claim WHERE attention routes, or WHAT value is written?).
3. Build the discriminating control IN THE CLAIM'S REGISTER (reuse the recipe).
   Put `# register: <kind>` in the control-script header; a probe whose register ≠
   the declared one is malformed — caught at write-time, not recalled at run-time.
4. Run it with a permutation/matched-control null + seed variance.
5. Update the row: status + the number + the result-JSON path.
6. If REFUTED/UNFALSIFIABLE → add a caveat header to the source page. If the first
   probe was wrong-register, run the matched-register probe before any verdict.
7. Commit (💡 finding / 🎯 if it changes a load-bearing decision).
```

> **Register slot (structural, not a rule).** Every control declares `# register:`
> in its header and every backlog claim is built only after step 0. This makes a
> register-mismatch *malformed* rather than *discouraged* — the wrong instrument
> falls out of the topology instead of relying on future attention. Exemplar pair:
> `binding_schedule_null.py` (`register: routing`, under-read #5) vs
> `binding_schedule_semantic.py` (`register: value`, found the real signal).

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

 I'm getting oriented on the current state. The next items in the backlog are the GTSM finite-budget work, reproducibility audits for crystal-sieve seed variance, and rank-1 adjunction comparisons—but first I need to register the gate before proceeding.

## Assistant

Oriented. Session 208 cold-start complete.

## Where we are

**North star:** 70B-equivalent in <1GB ternary, 200 tok/s CPU, 2M+ context, no GPU.

**Active program (s203+):** the **Validity-Distillation Audit** — one load-bearing claim per session, build a discriminating control with a permutation/matched-control null, update `audit-registry.md`, caveat the source page if it bites. Emergent meta-pattern across **every** audit so far: *the continuous substrate is real; the crisp discrete/localized/universal story on top is over-read.*

**Resolved so far:**
- #1 sign-topology → ◐ SCOPED (real only in `gate_proj`; magnitude carries value path)
- #2 holographic → ✅ spectral concentration + distributed redundancy VERIFIED
- #3 nine FFN modes → ❌ count k-means-imposed / ✅ syntactic field REAL
- #4 attention=typed-β → ❌ REFUTED-as-localized (0.82 was recency)
- #5 binding schedule → ❌ schedule REFUTED / ✅ H31@L27 subject value-transfer REAL
- #6 SVD φ-ratio 0.6299 → ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random (s207, last session)

**s206 standing law (now an S5 gene `λ measure` + S1 register slot):** *instrument must match the claim's register* — routing/value/magnitude/spectral/causal. Wrong register voids the verdict (±). **Step 0 every session = REGISTER GATE before any control is built.**

## What's next (backlog, ordered)

The registry points to three remaining med-load items:

1. **#11 GTSM finite-budget λ(l)** — does layer-targeted weighting beat uniform α=5.0 on the v3b score-matching sieve? (positive prediction, register: *value/continuous*; null is also informative — cosine may already absorb it)
2. **#7 crystal-sieve 1.03× reproducibility** — N-seed mean±variance; s196 itself saw a 3.23× rerun (register: *causal/functional*)
3. **#8 rank-1 adjunction** σ₁/σ₂=128:1 vs random/shuffled linear maps (register: *spectral*)

**Runtime:** olga.local (Apple Silicon, MPS, 480G unified); experiments launch in `tmux main:1`/`main:2`, watched live.

Which thread do you want to pull this session — #11 (compression track, the only *positive* prediction left), #7/#8 (reproducibility), or something else?

## User

lets work on 2 the crystal-sieve


### Thinking

 I'm focusing on the crystal-sieve reproducibility audit, specifically examining the claim that using continuations yields a 1.03× PPL improvement across 29 layers. Let me start by registering the gate and reviewing the existing evidence and harness setup.

## Assistant

#7 crystal-sieve reproducibility. Let me run the program's per-session loop. **Step 0 = REGISTER GATE.**

Let me first re-read the evidence and locate the s196 harness before declaring the register and building the control.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/mementum/knowledge/ | grep -iE \"sieve|crystal|continuation|compression\"; echo \"---SCRIPTS---\"; ls /Users/mwhitford/src/verbum/scripts/experiments/ 2>/dev/null | grep -iE \"sieve|continuation|crystal|beta|melt\"; echo \"---ALL EXP DIRS---\"; ls /Users/mwhitford/src/verbum/scripts/ 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/meme...

**Output:**
```
Exit code: 0
Stdout:
crystal-laplacian.md
crystal-multi-tree.md
crystal-native-architecture.md
crystal-phi-derivation.md
crystal-sieve-architecture.md
crystal-trace-tooling.md
crystal-universality.md
crystal-validity-and-fidelity.md
lambda-halt-continuation.md
saliency-aware-sieve.md
score-matching-compression.md
---SCRIPTS---
beta_expansion.py
continuation_placement_test.py
crystal_circuit_types.py
crystal_depth_scan.py
crystal_derivation.py
crystal_distill.py
crystal_ecc_sign_correction.py
crystal_error_correction.py
crystal_hybrid_ternarize.py
crystal_phi_permnull.py
crystal_sieve_pipeline.py
crystal_sieve_prototype.py
crystal_space_zeros.py
crystal_ternarize.py
crystal_tree.py
crystal_validity.py
crystal_zero_prediction.py
crystal_zero_v2.py
lambda_continuation.py
melt_boundaries.py
multi_projection_melt.py
paired_crystal_sieve.py
quasicrystal_diagnostic.py
row_norm_crystal.py
saliency_aware_sieve.py
staged_melt.py
synthetic_crystal_sieve.py
verify_crystal_phi.py
---ALL EXP DIRS---
__pycache__
analyze_binding_probes.py
analyze_essential_heads.py
analyze_v1_v2.py
compile_gradient_probe.py
experiments
explore
explore_qwen3_moe.py
gate_ablation.py
generate_training_data.py
holoquant
instruments
micro
mini-dispatch
probe_compression_v2.py
probe_compression.py
probe_predictive_functions.py
register_analysis.py
resume_vsm_v2_1B.py
run_ab_test.py
run_binding_ablation.py
run_binding_probe.py
run_binding_shape.py
run_bos_probe_v2.py
run_bos_probe.py
run_circuit_discovery.py
run_compression_map.py
run_compression_shape.py
run_compressor_lm.py
run_cross_task.py
run_distillation.py
run_head_ablation.py
run_montagu_lm.py
run_montagu_training.py
run_phi4_replication.py
run_pythia_phi_probe.py
run_pythia_replication.py
run_pythia_scaling.py
run_pythia160m_circuit.py
run_register_10k.py
run_register_probe.py
run_reverse_10k.py
run_reverse_ab.py
run_strip_test.py
run_structural_intervention.py
run_task_head_scan.py
run_tesseract.py
run_type_probe.py
run_vsm_10k.py
run_vsm_trial.py
run_vsm_v2_10k.py
run_vsm_v3_1_1B.py
run_vsm_v3_10k.py
run_vsm_v3_2_1B.py
run_vsm_v4_1_1B.py
run_vsm_v4_1B.py
run_vsm_v5_1B.py
run_weight_decomposition.py
v10
v11
v12
v13
v14
v15
v32_final_analysis.py
v6
v7
v8
v9
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/results/ 2>/dev/null | grep -iE \"sieve|continuation|crystal|beta|melt\"; echo \"---\"; find /Users/mwhitford/src/verbum -name \"*.py\" 2>/dev/null | xargs grep -lE \"continuation|crystal_sieve|beta_expansion\" 2>/dev/null | head -30"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/resu...

**Output:**
```
Exit code: 0
Stdout:
behavioral-crystal
behavioral-crystal-v2
beta-expansion
beta-reduction-probe
continuation-placement
crystal_scanner_run.log
crystal_sieve_crystal.log
crystal_sieve_random.log
crystal_space_zeros.log
crystal-circuit-types
crystal-combined
crystal-combined-run.log
crystal-comparison
crystal-completeness
crystal-completeness-run.log
crystal-compression-analysis
crystal-distill
crystal-ecc-sign-correction
crystal-error-correction
crystal-etch-attention
crystal-fourier
crystal-fourier-run.log
crystal-latch
crystal-latch-run.log
crystal-latch-v2
crystal-latch-v2-run.log
crystal-lens
crystal-phi-permnull
crystal-phi-verify
crystal-reconstruct
crystal-reconstruct-run.log
crystal-selfsim
crystal-selfsim-teacher
crystal-selfsim-v12
crystal-sieve-pipeline
crystal-tree
crystal-validity
crystal-visualization
crystal-zeros
crystal-zeros-train
lambda-continuation
loom-crystal-sharpen
melt-boundaries
multi-projection-melt
paired-crystal-sieve
q2-loom-melt
row_norm_crystal.log
saliency-aware-sieve
staged-melt
synthetic-crystal-sieve
v-crystal-cascade
---
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/mlx_lm/evaluate.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/aiohttp/_websocket/reader_py.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/aiohttp/_websocket/reader_c.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/aiohttp/http_parser.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/networkx/algorithms/cycles.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/h11/_readers.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/ntheory/ecm.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/printing/tests/test_fortran.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/printing/fortran.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/integrals/meijerint.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/assumptions/tests/test_refine.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/functions/special/hyper.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/functions/special/gamma_functions.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/functions/special/zeta_functions.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/functions/special/error_functions.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/functions/special/bessel.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/simplify/hyperexpand.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/c_like.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/graphics.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/hdl.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/verification.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/configs.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/pawn.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/_lilypond_builtins.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/lisp.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/c_cpp.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/automation.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/shell.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/d.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pygments/lexers/matlab.py
```

### Thinking

 I'm reviewing the crystal-sieve-architecture documentation and the beta_expansion harness that achieved the 1.03× improvement, then examining the s196 register details to verify the underlying claim.

## Assistant

Let me read the source knowledge page and the headline harness (`beta_expansion.py` — s196 experiment #8 that produced the 1.03×).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md"
}
```

**Summary:** Reading crystal-sieve-architecture.md (0-2000)

**Output:**
```
---
title: Crystal Sieve Architecture
status: active
category: compression
tags: [crystal, sieve, compression, continuation, beta-expansion, binding]
related:
  - lambda-tracer-diagnostic.md
  - l0-characterization.md
  - mode-semantics.md
  - tiny-classifier-ternary.md
  - dvd-stamp-topology.md
depends-on:
  - lambda-tracer-diagnostic.md
---

# Crystal Sieve Architecture

## Discovery (session 196)

Ten experiments converged on a proven compression architecture for
transformer FFN layers. The crystal sieve equation from session 185
was confirmed by direct measurement and extended with continuation
residuals to handle the cascade problem.

## The Architecture

```
Per sieved layer:
  W_eff = sign(W) ⊙ |W| ⊙ mask₅₀%

  sign(W):  crystal topology (frozen, universal r=0.998)
  |W|:      per-weight magnitudes (essential, cannot be per-row)
  mask₅₀%:  zero out smallest 50% (standing wave nodes)

Pipeline:
  L0:       SVD r=750 (lexer)
  L1-L26:   crystal sieve
  L27-L31:  continuous (binding, must stay full rank)
  L32-L34:  crystal sieve
  L35:      continuous (collapse)

  + 4 continuation residuals (rank-32 at L0/L9/L21/L26)
    1M trainable params, trained with CE loss, 100 steps
```

## Key Results

| Metric | Value |
|--------|-------|
| Per-layer sieve quality | 1.03x PPL |
| 29-layer cascade (sieve only) | 2.12x PPL |
| + continuation residuals | **1.03x PPL** |
| Binding preservation | 98% (39/40 top-1 matches) |
| Continuation params | 1,048,576 |
| Storage compression (current) | 1.8x (float16 magnitudes) |

## What Compounds vs What Doesn't

Critical lesson from this session: properties that hold per-layer
may NOT hold across 29 layers.

- Per-row scale = per-weight magnitude per layer → FAILS at 29 layers (22,800x)
- Crystal sieve quality cascades: 1.03x per layer → 2.12x at 29 layers
- Binding preservation HOLDS across cascade (98%)
- Continuation residuals absorb the cascade (2.12x → 1.03x)

## The Experimental Chain

1. **Lambda tracer**: damage is uniform across all 9 combinators
2. **Rank sweep**: functional rank varies 6x (L22=250 to L26=1500)
3. **Multi-projection melt**: intermediate losses 42% better than CE only
4. **Confidence gate**: classifier confidently wrong at L23-L26
   (the 9 programs are wrong, not the routing)
5. **Mode geometry**: same 9 programs rotated across layers, more
   modes don't help, float centroids = ternary centroids
6. **Ternary weight interface**: MASK matters more than magnitudes
   (50% sparsity improves L23 from 1.11x to 1.03x)
7. **Crystal sieve pipeline**: 2.12x at 29 layers with zero training
8. **β-expansion**: binding preserved 98%, continuations close the gap
9. **Ternary verification**: per-row encoding FAILS at full pipeline
   (per-weight magnitudes contain essential cascade-sensitive structure)

## Why the Mask Matters

The standing wave picture (session 185): the mask identifies the
nodes (zero-displacement points) of the standing wave in weight
space. Removing the bottom 50% of weights IMPROVES quality because
those small weights are noise — they interfere destructively with
the signal carried by the large weights.

At L23 (the hardest layer):
  - No mask:    1.11x PPL
  - 50% mask:   1.03x PPL (BETTER by removing noise)
  - More modes: 1.11x PPL (doesn't help)
  - Per-mode low-rank: 1.10x PPL (barely helps)

The mask is more important than the number of programs, the
magnitude granularity, or the mode representation.

## Why Continuations Work

The cascade error is purely magnitude distortion at layer
interfaces, NOT structural disruption. The binding heads (H31 at
L27, H03/H13/H15 at L30) still attend to the correct positions
with similar weights. The routing is intact; only the values
passing through are distorted.

Four low-rank corrections (rank-32 = 262K params each) at
functional boundaries absorb this distortion. They are CPS
continuations: each carries forward the correction that the next
functional zone needs to receive properly-scaled activations.

## Compression Status

**Proven quality**: 1.03x PPL at 29 sieved layers.
**Proven storage**: 1.8x compression (50% zeros in float16).
**Unproven**: magnitude quantization (Q4/Q8) in the full pipeline.

The path to real compression:
- Sign pattern: 1 bit (frozen, universal crystal)
- Mask: 1 bit (fixed from magnitude thresholding)
- Magnitude: needs ~4-8 bits per non-zero weight (NOT 0, NOT 16)
- Per-row scale: FAILS (22,800x at 29 layers)
- Per-group scale on magnitudes: untested, likely works (Q4 analog)

## Open Issues

1. **Continuation stability**: 1.03x on first run, 3.23x on rerun.
   Training is sensitive to initialization/batch order.
2. **Magnitude quantization**: Q4/Q8 per-weight with per-group scales
   needs verification across 29 layers + continuations.
3. **Attention compression**: only FFN is sieved (78% of params).
   Attention ternary works at PPL 23-30 (s190) but not yet integrated.

## Assets

| Asset | Path |
|-------|------|
| Lambda tracer | `scripts/experiments/lambda_tracer.py` |
| Binding-prep rank sweep | `scripts/experiments/binding_prep_lowrank.py` |
| Multi-projection melt | `scripts/experiments/multi_projection_melt.py` |
| Confidence gate | `scripts/experiments/confidence_gate.py` |
| Mode geometry | `scripts/experiments/mode_geometry.py` |
| Ternary weight interface | `scripts/experiments/ternary_weight_interface.py` |
| Crystal sieve pipeline | `scripts/experiments/crystal_sieve_pipeline.py` |
| β-expansion | `scripts/experiments/beta_expansion.py` |
| Ternary verification | `scripts/experiments/ternary_pipeline_verify.py` |
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/beta_expansion.py"
}
```

**Summary:** Reading beta_expansion.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""β-Expansion — reverse the reductions, correct the cascade.

The sieve cascade: per-layer error 1.03x compounds to 2.11x across 29
layers. The error propagates FORWARD through β-reductions. β-expansion
reverses this: given the teacher's correct state at binding layers,
work backward to compute what earlier layers should have produced.

Phase 1: BINDING PRESERVATION
  Does the sieve preserve the binding graph? Compare attention patterns
  at L27 (H31 verb←subject) and L30 (H03/H13 object←verb) between
  teacher and sieved model. If bindings are preserved → cascade is in
  magnitudes. If bindings change → sieve disrupts type tags.

Phase 2: STRUCTURED CORRECTION
  At binding checkpoints, compute the teacher-student delta in the
  residual stream. Decompose along binding edges. Apply corrections
  ONLY at the source positions that the binding heads read from —
  not uniformly at all positions.

Phase 3: CONTINUATION RESIDUALS
  Add small learned correction vectors at functional boundaries.
  These absorb cascade error with minimal parameters — like CPS
  continuations that carry forward the accumulated correction.

Usage:
  uv run python scripts/experiments/beta_expansion.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════
# Texts
# ══════════════════════════════════════════════════════════════

EVAL_TEXTS = [
    "The theory of general relativity describes gravity"
    " as the curvature of spacetime caused by mass and"
    " energy.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new"
    " environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps"
    " muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their"
    " composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million"
    " years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory"
    " distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable"
    " on one side by subtracting three from both sides.",
]

# Structured binding probes — sentences with clear S/V/O
BINDING_PROBES = [
    {"text": "The cat runs quickly",
     "subject": "cat", "verb": "runs", "s_pos": 1, "v_pos": 2},
    {"text": "The dog bit the cat",
     "subject": "dog", "verb": "bit", "object": "cat",
     "s_pos": 1, "v_pos": 2, "o_pos": 4},
    {"text": "She walked through the ancient forest",
     "subject": "She", "verb": "walked", "s_pos": 0, "v_pos": 1},
    {"text": "The detective examined the crime scene",
     "subject": "detective", "verb": "examined", "object": "scene",
     "s_pos": 1, "v_pos": 2, "o_pos": 5},
    {"text": "Three children ran laughing through the meadow",
     "subject": "children", "verb": "ran", "s_pos": 1, "v_pos": 2},
    {"text": "The old man sat quietly by the river",
     "subject": "man", "verb": "sat", "s_pos": 2, "v_pos": 3},
    {"text": "Birds sang in the treetops",
     "subject": "Birds", "verb": "sang", "s_pos": 0, "v_pos": 1},
    {"text": "The ship sailed slowly into the harbor",
     "subject": "ship", "verb": "sailed", "s_pos": 1, "v_pos": 2},
    {"text": "The committee voted unanimously",
     "subject": "committee", "verb": "voted", "s_pos": 1, "v_pos": 2},
    {"text": "Enzymes speed up chemical reactions",
     "subject": "Enzymes", "verb": "speed", "s_pos": 0, "v_pos": 1},
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
]

# Known binding heads from session 188
BINDING_HEADS = {
    27: [31],           # H31: verb reads subject (0.82 weight)
    30: [3, 13, 15],    # H03/H13/H15: object reads verb (0.78 weight)
}


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(text, return_tensors="pt",
                        truncation=True, max_length=256)
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Crystal Sieve (frozen, from pipeline experiment)
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)
        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class TrainableLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        return out.clamp(-65000, 65000).to(x.dtype)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Attention capture
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def capture_attention_and_states(model, input_ids, device,
                                 target_layers):
    """Capture attention weights and hidden states at target layers.

    Returns:
      attn_weights: {layer_idx: tensor (n_heads, seq, seq)}
      hidden_states: {layer_idx: tensor (seq, d_model)}
    """
    layers = get_layers(model)
    attn_weights = {}
    hidden_states = {}
    hooks = []

    # Hook attention to capture weights
    def make_attn_hook(layer_idx):
        def hook_fn(mod, args, kwargs, output):
            # Qwen3 self_attn with output_attentions returns
            # (attn_output, attn_weights, past_kv)
            if isinstance(output, tuple) and len(output) >= 2:
                w = output[1]
                if w is not None:
                    attn_weights[layer_idx] = w[0].detach().cpu()
        return hook_fn

    # Hook decoder layer for hidden states
    def make_state_hook(layer_idx):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            hidden_states[layer_idx] = h[0].detach().cpu()
        return hook_fn

    for li in target_layers:
        hooks.append(
            layers[li].self_attn.register_forward_hook(
                make_attn_hook(li), with_kwargs=True))
        hooks.append(
            layers[li].register_forward_hook(make_state_hook(li)))

    input_ids = input_ids.to(device)
    model(input_ids, output_attentions=True)

    for h in hooks:
        h.remove()

    return attn_weights, hidden_states


# ══════════════════════════════════════════════════════════════
# Phase 1: Binding Preservation
# ══════════════════════════════════════════════════════════════

def analyze_binding_preservation(teacher_attn, sieved_attn,
                                 probe, tokenizer):
    """Compare binding head attention between teacher and sieved model."""
    results = {}

    for layer_idx, head_list in BINDING_HEADS.items():
        if layer_idx not in teacher_attn or layer_idx not in sieved_attn:
            continue

        t_attn = teacher_attn[layer_idx]  # (n_heads, seq, seq)
        s_attn = sieved_attn[layer_idx]

        for head_idx in head_list:
            t_head = t_attn[head_idx]  # (seq, seq)
            s_head = s_attn[head_idx]

            # At verb position, where does the head attend?
            v_pos = probe.get("v_pos")
            s_pos = probe.get("s_pos")
            if v_pos is None:
                continue

            # Teacher: attention from verb to all positions
            t_dist = t_head[v_pos]  # (seq,)
            s_dist = s_head[v_pos]

            # Top-1 position
            t_top1 = int(t_dist.argmax())
            s_top1 = int(s_dist.argmax())

            # Attention weight at subject position
            t_subj_weight = float(t_dist[s_pos]) if s_pos is not None else 0
            s_subj_weight = float(s_dist[s_pos]) if s_pos is not None else 0

            # KL divergence between distributions
            t_log = torch.log(t_dist.clamp(min=1e-10))
            s_log = torch.log(s_dist.clamp(min=1e-10))
            kl = float(F.kl_div(s_log, t_dist, reduction='sum'))

            # Cosine of attention distributions
            cos = float(F.cosine_similarity(
                t_dist.unsqueeze(0), s_dist.unsqueeze(0)))

            key = f"L{layer_idx}_H{head_idx}"
            results[key] = {
                "teacher_top1": t_top1,
                "sieved_top1": s_top1,
                "top1_match": t_top1 == s_top1,
                "teacher_subj_weight": round(t_subj_weight, 4),
                "sieved_subj_weight": round(s_subj_weight, 4),
                "attn_cos": round(cos, 4),
                "kl_div": round(kl, 4),
            }

    return results


# ══════════════════════════════════════════════════════════════
# Phase 2: Continuation Residuals
# ══════════════════════════════════════════════════════════════

class ContinuationResidual(nn.Module):
    """Small learned correction at a layer boundary.

    Added to the residual stream after a decoder layer.
    Implemented as a low-rank down-up projection:
      correction = input @ W_down @ W_up
    """

    def __init__(self, d_model, rank=32):
        super().__init__()
        self.W_down = nn.Parameter(
            torch.randn(d_model, rank) * 0.001)
        self.W_up = nn.Parameter(
            torch.randn(rank, d_model) * 0.001)

    def forward(self, x):
        # x: (batch, seq, d_model)
        correction = x.float() @ self.W_down @ self.W_up
        return (x.float() + correction).to(x.dtype)


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--residual-rank", type=int, default=32)
    p.add_argument("--melt-steps", type=int, default=100)
    p.add_argument("--lr", type=float, default=1e-4)
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    BINDING_LAYER_IDS = [27, 30]
    # Continuation residuals at functional boundaries
    RESIDUAL_LAYERS = [0, 9, 21, 26]

    log(f"\n{'='*70}")
    log("  β-EXPANSION — Reverse the reductions, correct the cascade")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")

    # ── Load ──────────────────────────────────────────────
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model={d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_facts, base_total = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{base_total}")

    # ══════════════════════════════════════════════════════
    # Phase 1: Capture teacher binding patterns
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: TEACHER BINDING PATTERNS")
    log(f"{'═'*70}")

    teacher_bindings = []
    teacher_states_all = []
    for probe in BINDING_PROBES:
        enc = tokenizer(probe["text"], return_tensors="pt")
        attn, states = capture_attention_and_states(
            model, enc["input_ids"], args.device,
            BINDING_LAYER_IDS)
        teacher_bindings.append((probe, attn, states))

        # Also capture hidden states at functional boundaries
        all_states = {}
        layers = get_layers(model)
        hooks = []
        def make_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                all_states[li] = h[0].detach().cpu()
            return hook_fn
        for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]:
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        with torch.no_grad():
            model(enc["input_ids"].to(args.device))
        for h in hooks:
            h.remove()
        teacher_states_all.append(all_states)

    log(f"  Captured {len(BINDING_PROBES)} probes")

    # ══════════════════════════════════════════════════════
    # Install crystal sieve
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        setattr(mlp0, pname,
                TrainableLowRankLinear(A.to(args.device),
                                       B.to(args.device)))

    # Sieve remaining layers
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            setattr(mlp, pname,
                    FrozenSieveLinear(proj.weight,
                                      zero_rate=args.zero_rate).to(args.device))
    log(f"  Sieve installed on {len(SIEVE_LAYERS)} layers + L0 SVD")

    # Pre-melt measurement
    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    pre_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Pre-melt PPL: {pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)"
        f"  facts: {pre_facts}/{base_total}")

    # ══════════════════════════════════════════════════════
    # Phase 1b: Compare sieved binding patterns
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1b: BINDING PRESERVATION ANALYSIS")
    log(f"{'═'*70}")

    all_binding_results = []
    top1_matches = 0
    top1_total = 0

    for probe, teacher_attn, teacher_states in teacher_bindings:
        enc = tokenizer(probe["text"], return_tensors="pt")
        sieved_attn, sieved_states = capture_attention_and_states(
            model, enc["input_ids"], args.device,
            BINDING_LAYER_IDS)

        results = analyze_binding_preservation(
            teacher_attn, sieved_attn, probe, tokenizer)

        for key, r in results.items():
            top1_total += 1
            if r["top1_match"]:
                top1_matches += 1

        all_binding_results.append({
            "text": probe["text"],
            "bindings": results,
        })

        log(f"\n  \"{probe['text'][:40]}...\"")
        for key, r in results.items():
            match = "✓" if r["top1_match"] else "✗"
            log(f"    {key}: top1 {r['teacher_top1']}→{r['sieved_top1']}"
                f" {match}"
                f"  subj_w: {r['teacher_subj_weight']:.3f}→{r['sieved_subj_weight']:.3f}"
                f"  cos={r['attn_cos']:.3f}")

    log(f"\n  BINDING PRESERVATION: {top1_matches}/{top1_total}"
        f" top-1 matches ({top1_matches/max(top1_total,1):.0%})")

    # ══════════════════════════════════════════════════════
    # Phase 2: Hidden state comparison at boundaries
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: HIDDEN STATE FIDELITY AT BOUNDARIES")
    log(f"{'═'*70}")

    boundary_fidelity = {li: [] for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]}

    for i, probe in enumerate(BINDING_PROBES):
        enc = tokenizer(probe["text"], return_tensors="pt")
        teacher_states = teacher_states_all[i]

        # Capture sieved states at same boundaries
        sieved_states = {}
        hooks = []
        def make_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                sieved_states[li] = h[0].detach().cpu()
            return hook_fn
        for li in RESIDUAL_LAYERS + BINDING_LAYER_IDS + [35]:
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        with torch.no_grad():
            model(enc["input_ids"].to(args.device))
        for h in hooks:
            h.remove()

        for li in boundary_fidelity:
            if li in teacher_states and li in sieved_states:
                t = teacher_states[li].float()
                s = sieved_states[li].float()
                cos = F.cosine_similarity(t, s, dim=-1).mean().item()
                boundary_fidelity[li].append(cos)

    log(f"\n  {'Layer':>6s}  {'Mean cos':>8s}  {'Role':>20s}")
    log(f"  {'─'*6}  {'─'*8}  {'─'*20}")
    for li in sorted(boundary_fidelity.keys()):
        vals = boundary_fidelity[li]
        if vals:
            mean_cos = np.mean(vals)
            role = ("lexer" if li == 0 else
                    "parser" if li == 9 else
                    "composition" if li == 21 else
                    "type crystal" if li == 26 else
                    "binding (subj)" if li == 27 else
                    "binding (obj)" if li == 30 else
                    "output" if li == 35 else "?")
            log(f"  L{li:>3d}   {mean_cos:>8.4f}  {role:>20s}")

    # ══════════════════════════════════════════════════════
    # Phase 3: Continuation residuals
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3: CONTINUATION RESIDUALS")
    log(f"  Adding low-rank corrections at L{RESIDUAL_LAYERS}")
    log(f"{'═'*70}")

    # Install continuation residuals as hooks
    continuations = {}
    cont_hooks = []
    trainable_params = []

    for li in RESIDUAL_LAYERS:
        cont = ContinuationResidual(d_model, rank=args.residual_rank).to(args.device)
        continuations[li] = cont
        trainable_params.extend([cont.W_down, cont.W_up])

        def make_cont_hook(c):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                corrected = c(h)
                if isinstance(out, tuple):
                    return (corrected,) + out[1:]
                return corrected
            return hook_fn

        h = layers[li].register_forward_hook(make_cont_hook(cont))
        cont_hooks.append(h)

    n_trainable = sum(p.numel() for p in trainable_params)
    log(f"  Continuations: {len(RESIDUAL_LAYERS)} layers × rank-{args.residual_rank}"
        f" = {n_trainable:,} params")

    # Cache teacher states for melt
    teacher_cache = []
    CHECKPOINTS = {"lexer": 0, "composition": 21,
                   "type_crystal": 26, "binding": 30}
    for text in CALIBRATION_TEXTS:
        # Teacher states were captured before sieve installation
        # Need to re-capture from the already-sieved model's teacher
        # Actually we need ORIGINAL teacher states — use the ones from binding probes
        pass

    # Simple melt: just CE loss (continuations are tiny, don't need projections)
    log(f"\n  Melting with CE loss ({args.melt_steps} steps)...")
    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)
    model.train()
    history = []
    t0 = time.time()

    for step in range(args.melt_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_idx = rng.choice(len(CALIBRATION_TEXTS),
                               min(4, len(CALIBRATION_TEXTS)),
                               replace=False)
        total_loss = 0.0
        total_tokens = 0
        for idx in batch_idx:
            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors="pt",
                            truncation=True, max_length=128)
            enc = {k: v.to(args.device) for k, v in enc.items()}
            labels = enc["input_ids"].clone()
            out = model(**enc, labels=labels)
            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):
                out.loss.backward()
                total_loss += out.loss.item() * labels.numel()
                total_tokens += labels.numel()

        if total_tokens == 0:
            continue

        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)
        optimizer.step()
        avg = total_loss / total_tokens
        history.append(avg)

        if (step + 1) % 20 == 0 or step == 0:
            elapsed = time.time() - t0
            log(f"    step {step+1:>3d}: loss={avg:.4f} ({elapsed:.0f}s)")

    model.eval()

    # Post-melt measurement
    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    post_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Post-melt PPL: {post_ppl:.2f} ({post_ppl/base_ppl:.2f}x)"
        f"  facts: {post_facts}/{base_total}")

    # Clean up
    for h in cont_hooks:
        h.remove()

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:    PPL={base_ppl:.2f}  facts={base_facts}/{base_total}")
    log(f"  Sieve only:  PPL={pre_ppl:.2f} ({pre_ppl/base_ppl:.2f}x)"
        f"  facts={pre_facts}/{base_total}")
    log(f"  +Continuations: PPL={post_ppl:.2f} ({post_ppl/base_ppl:.2f}x)"
        f"  facts={post_facts}/{base_total}")
    log(f"  Binding preserved: {top1_matches}/{top1_total}"
        f" ({top1_matches/max(top1_total,1):.0%})")
    log(f"  Continuation params: {n_trainable:,}")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "beta-expansion"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    result = {
        "model": args.model,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "pre_melt_ppl": pre_ppl,
        "pre_melt_ratio": round(pre_ppl / base_ppl, 4),
        "post_melt_ppl": post_ppl,
        "post_melt_ratio": round(post_ppl / base_ppl, 4),
        "post_melt_facts": post_facts,
        "binding_top1_matches": top1_matches,
        "binding_top1_total": top1_total,
        "binding_preservation_rate": round(top1_matches / max(top1_total, 1), 4),
        "binding_results": all_binding_results,
        "boundary_fidelity": {
            str(li): round(float(np.mean(v)), 4)
            for li, v in boundary_fidelity.items() if v
        },
        "continuation_params": n_trainable,
        "residual_rank": args.residual_rank,
        "loss_history": [round(x, 4) for x in history],
    }
    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
```

### Thinking

 I'm looking at the reproducibility issue with crystal-sieve: the PPL multiplier is 1.03× on the first run but jumps to 3.23× on rerun, suggesting the training is sensitive to initialization and batch ordering. Now I need to identify what type of claim this is — it's fundamentally about reproducibility and functional behavior rather than routing, value magnitude, or spectral properties.

Looking at the actual sources of randomness in the code, I see two unseeded RNG sources: the continuation residual initialization and the sieve mask threshold subsampling (which uses randperm to select 5M elements from 50M for the quantile calculation). The batch order is actually deterministic since it's seeded by step, so the real culprits are the continuation init and the sieve mask threshold. To properly test whether 1.03× is a stable property or a lucky seed artifact, I need to design a reproducibility control that runs multiple seeds with proper seeding, measures both the pre-melt ratio (sieve only) and post-melt ratio (with continuations), and reports mean ± std to see if 1.03× is the mean or just the lucky tail.

I'll create a new harness that loads the 8B model fresh for each seed, applies the sieve, measures the baseline PPL, installs continuations, trains, and measures the final PPL — recording all metrics per seed to decompose variance between the sieve mask and continuation training.

The eval set is tiny (8 texts) and the original is a known weakness, but reproducing the claim means using the same protocol. Runtime-wise, loading the model takes about 30 seconds to a minute, sieving and quantile computations add another minute or so, PPL measurement is fast on the small set, and the melt training (100 steps through 8B) is the expensive part — probably several minutes per seed. With N=5 seeds, I'm looking at 25-50 minutes total, which is reasonable for a background run.

Facts measurement runs three times per seed (pre, post, and baseline), which is slow on MPS, but since binding preservation and facts are part of the headline, I'll keep them. I'm going to reload the model fresh each seed to avoid any state leakage, then write the reproduction script based on the existing beta_expansion script but with a seed loop. Let me first check that I'm on the right machine (olga.local with MPS) and verify the model is cached locally before setting up the task plan.

## Assistant

I have the full picture. Let me declare the **register gate** and identify the randomness sources before building.

**Step 0 — REGISTER GATE.** Claim #7: *"crystal-sieve + 4 continuation residuals = 1.03× PPL across 29 layers."* The register is **functional/reproducibility** — a behavioral PPL measurement, and the question is *seed variance* (1.03× first run vs 3.23× rerun). The discriminating control: **set a seed, run N seeds, report mean ± std** of the PPL ratio — is 1.03× the distribution's center or its lucky tail?

Reading the harness, the unseeded RNG sources are:
1. **Continuation init** — `torch.randn(...) * 0.001`, no seed (the "init sensitivity" the note names).
2. **Sieve mask threshold** — for >10M-elem projections (8B FFN = 50M), `torch.randperm(...)[:5M]` subsamples for the quantile → **different mask each run**, a source the note *didn't* name.
3. Batch order is actually `RandomState(step)` → deterministic, *not* a variance source (note is wrong on this).

So the control must also **decompose** variance: pre-melt (sieve mask only) vs post-melt (sieve + continuation training).

Let me verify the runtime environment and model cache before building.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"import torch; print('mps', torch.backends.mps.is_available()); print('torch', torch.__version__)\" 2>&1 | tail -5; echo \"---CACHE---\"; ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -i qwen3; echo \"---HOST---\"; hostname; echo \"---tmux---\"; tmux ls 2>&1 | head"
}
```

**Summary:** $ uv run python -c "import torch; pri...

**Output:**
```
Exit code: 0
Stdout:
mps True
torch 2.11.0
---CACHE---
models--mlx-community--Qwen3-Embedding-4B-4bit-DWQ
models--Qwen--Qwen3-0.6B
models--Qwen--Qwen3-14B
models--Qwen--Qwen3-235B-A22B
models--Qwen--Qwen3-30B-A3B
models--Qwen--Qwen3-32B
models--Qwen--Qwen3-4B
models--Qwen--Qwen3-8B
models--Qwen--Qwen3.5-35B-A3B
models--Qwen--Qwen3.6-27B
models--Qwen--Qwen3.6-35B-A3B
models--unsloth--Qwen3-Coder-480B-A35B-Instruct-GGUF
---HOST---
olga.local
---tmux---
main: 2 windows (created Tue Jun  9 09:03:16 2026) (attached)
trace_basis: 1 windows (created Mon Jun  1 14:02:42 2026)
```

### Thinking

 I've got MPS available on olga.local with Qwen3-8B cached, and tmux is running with two windows open. Now I'm setting up the task plan and building the harness.

## Assistant

Environment confirmed: olga.local, MPS, Qwen3-8B cached, tmux `main` has 2 windows. Let me set up the plan.

### Thinking

 I'm building a test harness that loops through different random seeds, reloading the model fresh each time to ensure reproducibility. I'll set seeds for both PyTorch and NumPy, keep the architecture matching the beta_expansion version, and track mean and standard deviation across runs.

For efficiency, I'll measure baseline PPL on each seed as a determinism check (it's cheap and should be identical), but measure baseline facts only once on the first seed to avoid redundant generation cost. Pre and post-melt metrics will run per seed since they vary with the mask subsampling and continuation initialization. The pre-melt ratio variance directly isolates the mask contribution, while post-melt captures the combined effect of masking, initialization, and training variance—giving me a clean decomposition without extra runs.

## Assistant

Now building the seeded harness:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Crystal-Sieve Reproducibility — is 1.03x the center or a lucky tail?\n\n# register: functional (reproducibility — seed variance on a PPL measurement)\n\nAudit-registry claim #7: \"crystal-sieve + 4 continuation residuals = 1.03x\nPPL across 29 sieved layers (Qwen3-8B).\" s196 itself noted a rerun gave 3.23x\nand called training \"sensitive to initialization/batch order.\"\n\nThis control re-runs the EXACT s196 beta_expansion pipeline under N controlled\nseeds and reports mean +/- std. The discriminating question: is 1.03x the\ndistribution's center, or its lucky tail?\n\nDecomposition (no extra runs needed):\n  - pre_melt_ratio  : sieve mask ONLY (no continuations, no training).\n                      Its across-seed std = the MASK-subsampling variance\n                      (the FFN projections are >10M elems -> torch.randperm\n                      subsamples 5M for the quantile threshold -> mask varies).\n  - post_melt_ratio : sieve + continuation init + 100-step CE melt.\n                      Its across-seed std = mask + init + training variance.\n  If pre std ~ 0 and post std large  -> variance is in continuation training.\n  If pre std large                    -> the mask subsampling itself is unstable.\n\nNB: batch order in the original melt is RandomState(step) -> DETERMINISTIC\nacross reruns; it is NOT a variance source (the s196 note is wrong on that).\nThe real unseeded sources are (a) continuation torch.randn init and (b) the\nsieve mask randperm subsample. Both are now seeded per run.\n\nUsage:\n  uv run python scripts/experiments/crystal_sieve_repro.py \\\n    --model Qwen/Qwen3-8B --device mps --seeds 5\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nimport time\nfrom pathlib import Path\n\nimport numpy as np\nimport torch\nimport torch.nn as nn\nimport torch.nn.functional as F\nfrom transformers import AutoModelForCausalLM, AutoTokenizer\n\n_SCRIPT_DIR = Path(__file__).resolve().parent\n_PROJECT_ROOT = _SCRIPT_DIR.parent.parent\nif str(_PROJECT_ROOT / \"src\") not in sys.path:\n    sys.path.insert(0, str(_PROJECT_ROOT / \"src\"))\n\n\n# ══════════════════════════════════════════════════════════════\n# Texts (identical to beta_expansion.py — same protocol)\n# ══════════════════════════════════════════════════════════════\n\nEVAL_TEXTS = [\n    \"The theory of general relativity describes gravity\"\n    \" as the curvature of spacetime caused by mass and\"\n    \" energy.\",\n    \"In a large mixing bowl, combine the flour, sugar,\"\n    \" and baking powder. Make a well in the center.\",\n    \"The committee voted unanimously to approve the new\"\n    \" environmental regulations for manufacturing plants.\",\n    \"She walked through the ancient forest, her footsteps\"\n    \" muffled by centuries of fallen leaves.\",\n    \"The function takes two arguments and returns their\"\n    \" composition as a new callable object.\",\n    \"During the Cambrian explosion, roughly 541 million\"\n    \" years ago, most major animal phyla appeared.\",\n    \"The patient was admitted with acute respiratory\"\n    \" distress. Initial blood work showed elevated levels.\",\n    \"To solve this equation, first isolate the variable\"\n    \" on one side by subtracting three from both sides.\",\n]\n\nFACT_PROMPTS = [\n    {\"prompt\": \"The capital of France is\", \"expected\": \"Paris\"},\n    {\"prompt\": \"The capital of Japan is\", \"expected\": \"Tokyo\"},\n    {\"prompt\": \"Water boils at\", \"expected\": \"100\"},\n    {\"prompt\": \"The speed of light is approximately\", \"expected\": \"300\"},\n    {\"prompt\": \"The first president of the United States was\",\n     \"expected\": \"George Washington\"},\n    {\"prompt\": \"The year World War II ended was\", \"expected\": \"1945\"},\n    {\"prompt\": \"The chemical symbol for gold is\", \"expected\": \"Au\"},\n    {\"prompt\": \"The largest planet in our solar system is\",\n     \"expected\": \"Jupiter\"},\n    {\"prompt\": \"The author of Romeo and Juliet is\", \"expected\": \"Shakespeare\"},\n    {\"prompt\": \"Pi is approximately equal to\", \"expected\": \"3.14\"},\n    {\"prompt\": \"The Great Wall of China is located in\", \"expected\": \"China\"},\n    {\"prompt\": \"The human body has\", \"expected\": \"206\"},\n    {\"prompt\": \"Einstein's famous equation is E equals\", \"expected\": \"mc\"},\n    {\"prompt\": \"The freezing point of water in Celsius is\", \"expected\": \"0\"},\n    {\"prompt\": \"The currency of the United Kingdom is the\", \"expected\": \"pound\"},\n]\n\nCALIBRATION_TEXTS = [\n    \"The theory of general relativity describes gravity as\"\n    \" the curvature of spacetime.\",\n    \"Photosynthesis converts carbon dioxide and water into\"\n    \" glucose and oxygen.\",\n    \"DNA carries genetic information in a double helix\"\n    \" structure discovered by Watson and Crick.\",\n    \"Quantum mechanics describes the behavior of particles\"\n    \" at the atomic and subatomic scale.\",\n    \"She walked through the ancient forest, her footsteps\"\n    \" muffled by fallen leaves.\",\n    \"The old man sat quietly by the river, watching the\"\n    \" fish jump at dawn.\",\n    \"In a large mixing bowl, combine the flour, sugar,\"\n    \" and baking powder.\",\n    \"To solve this equation, first isolate the variable\"\n    \" on one side.\",\n    \"The committee voted unanimously to approve the new\"\n    \" environmental regulations.\",\n    \"The function takes two arguments and returns their\"\n    \" composition as a new callable.\",\n    \"What time does the store close today?\",\n    \"I think we should probably leave now before it gets\"\n    \" too dark outside.\",\n]\n\n\ndef log(msg=\"\"):\n    print(msg, file=sys.stderr, flush=True)\n    print(msg, flush=True)\n\n\ndef get_layers(model):\n    if hasattr(model, \"model\") and hasattr(model.model, \"layers\"):\n        return model.model.layers\n    raise RuntimeError(f\"Can't find layers in {type(model)}\")\n\n\ndef measure_ppl(model, tokenizer, texts, device):\n    total_loss = 0.0\n    total_tokens = 0\n    for text in texts:\n        enc = tokenizer(text, return_tensors=\"pt\",\n                        truncation=True, max_length=256)\n        enc = {k: v.to(device) for k, v in enc.items()}\n        labels = enc[\"input_ids\"].clone()\n        with torch.no_grad():\n            out = model(**enc, labels=labels)\n            total_loss += out.loss.item() * labels.numel()\n            total_tokens += labels.numel()\n    return float(np.exp(total_loss / total_tokens))\n\n\ndef generate_text(model, tokenizer, prompt, device, max_new=30):\n    enc = tokenizer(prompt, return_tensors=\"pt\")\n    enc = {k: v.to(device) for k, v in enc.items()}\n    with torch.no_grad():\n        out = model.generate(**enc, max_new_tokens=max_new,\n                             do_sample=False, temperature=1.0,\n                             pad_token_id=tokenizer.pad_token_id)\n    return tokenizer.decode(out[0][enc[\"input_ids\"].shape[1]:],\n                            skip_special_tokens=True)\n\n\ndef measure_facts(model, tokenizer, device):\n    correct = 0\n    for fp in FACT_PROMPTS:\n        gen = generate_text(model, tokenizer, fp[\"prompt\"], device)\n        if fp[\"expected\"].lower() in gen.lower():\n            correct += 1\n    return correct, len(FACT_PROMPTS)\n\n\n# ══════════════════════════════════════════════════════════════\n# Crystal Sieve (identical to beta_expansion.py)\n# ══════════════════════════════════════════════════════════════\n\nclass FrozenSieveLinear(nn.Module):\n    def __init__(self, weight, zero_rate=0.5):\n        super().__init__()\n        W = weight.detach().float().cpu()\n        abs_W = W.abs()\n        if zero_rate > 0:\n            flat = abs_W.flatten()\n            if flat.numel() > 10_000_000:\n                # NOTE: torch.randperm here is the MASK-subsampling RNG.\n                # Seeded per run by torch.manual_seed in run_one_seed().\n                idx = torch.randperm(flat.numel())[:5_000_000]\n                threshold = torch.quantile(flat[idx], zero_rate)\n            else:\n                threshold = torch.quantile(flat, zero_rate)\n            mask = (abs_W >= threshold).float()\n        else:\n            mask = torch.ones_like(W)\n        W_sieve = torch.sign(W) * abs_W * mask\n        self.register_buffer(\"W_sieve\", W_sieve.half())\n\n    def forward(self, x):\n        out = x.float() @ self.W_sieve.float().T\n        return out.clamp(-65000, 65000).to(x.dtype)\n\n\nclass TrainableLowRankLinear(nn.Module):\n    def __init__(self, A, B):\n        super().__init__()\n        self.register_buffer(\"A\", A)\n        self.register_buffer(\"B\", B)\n\n    def forward(self, x):\n        out = x.float() @ self.B.T @ self.A.T\n        return out.clamp(-65000, 65000).to(x.dtype)\n\n\ndef svd_factorize(weight, rank):\n    W = weight.detach().float().cpu()\n    U, S, Vt = torch.linalg.svd(W, full_matrices=False)\n    r = min(rank, len(S))\n    sqrt_S = S[:r].sqrt()\n    A = U[:, :r] * sqrt_S.unsqueeze(0)\n    B = Vt[:r, :] * sqrt_S.unsqueeze(1)\n    return A, B\n\n\nclass ContinuationResidual(nn.Module):\n    \"\"\"Small learned correction at a layer boundary (identical to s196).\n\n    NOTE: torch.randn here is the continuation-INIT RNG. Seeded per run.\n    \"\"\"\n\n    def __init__(self, d_model, rank=32):\n        super().__init__()\n        self.W_down = nn.Parameter(torch.randn(d_model, rank) * 0.001)\n        self.W_up = nn.Parameter(torch.randn(rank, d_model) * 0.001)\n\n    def forward(self, x):\n        correction = x.float() @ self.W_down @ self.W_up\n        return (x.float() + correction).to(x.dtype)\n\n\n# ══════════════════════════════════════════════════════════════\n# One seeded run of the full pipeline\n# ══════════════════════════════════════════════════════════════\n\ndef run_one_seed(args, seed, base_facts_cached=None):\n    \"\"\"Load fresh, seed, sieve, melt — return per-seed metrics.\"\"\"\n    torch.manual_seed(seed)\n    np.random.seed(seed)\n    if torch.backends.mps.is_available():\n        torch.mps.manual_seed(seed)\n\n    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]\n    RESIDUAL_LAYERS = [0, 9, 21, 26]\n\n    dtype = (torch.float16\n             if any(s in args.model for s in [\"8B\", \"14B\", \"32B\"])\n             else torch.float32)\n    model = AutoModelForCausalLM.from_pretrained(\n        args.model, torch_dtype=dtype, device_map=args.device,\n        attn_implementation=\"eager\")\n    tokenizer = AutoTokenizer.from_pretrained(args.model)\n    if tokenizer.pad_token is None:\n        tokenizer.pad_token = tokenizer.eos_token\n    model.eval()\n    d_model = model.config.hidden_size\n\n    # Baseline (deterministic; measured per-seed as a sanity check)\n    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    if base_facts_cached is None:\n        base_facts, base_total = measure_facts(model, tokenizer, args.device)\n    else:\n        base_facts, base_total = base_facts_cached, len(FACT_PROMPTS)\n\n    # Install sieve (L0 SVD + 29 sieved layers)\n    layers = get_layers(model)\n    mlp0 = layers[0].mlp\n    for pname in [\"gate_proj\", \"up_proj\", \"down_proj\"]:\n        proj = getattr(mlp0, pname)\n        A, B = svd_factorize(proj.weight, 750)\n        setattr(mlp0, pname,\n                TrainableLowRankLinear(A.to(args.device), B.to(args.device)))\n    for li in SIEVE_LAYERS:\n        mlp = layers[li].mlp\n        for pname in [\"gate_proj\", \"up_proj\", \"down_proj\"]:\n            proj = getattr(mlp, pname)\n            setattr(mlp, pname,\n                    FrozenSieveLinear(proj.weight,\n                                      zero_rate=args.zero_rate).to(args.device))\n\n    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    pre_facts, _ = measure_facts(model, tokenizer, args.device)\n\n    # Install continuation residuals\n    continuations = {}\n    cont_hooks = []\n    trainable_params = []\n    for li in RESIDUAL_LAYERS:\n        cont = ContinuationResidual(d_model, rank=args.residual_rank).to(args.device)\n        continuations[li] = cont\n        trainable_params.extend([cont.W_down, cont.W_up])\n\n        def make_cont_hook(c):\n            def hook_fn(mod, inp, out):\n                h = out[0] if isinstance(out, tuple) else out\n                corrected = c(h)\n                if isinstance(out, tuple):\n                    return (corrected,) + out[1:]\n                return corrected\n            return hook_fn\n        cont_hooks.append(layers[li].register_forward_hook(make_cont_hook(cont)))\n\n    n_trainable = sum(p.numel() for p in trainable_params)\n\n    # Melt — CE loss, batch order RandomState(step) (deterministic, as s196)\n    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)\n    model.train()\n    history = []\n    for step in range(args.melt_steps):\n        optimizer.zero_grad()\n        rng = np.random.RandomState(step)\n        batch_idx = rng.choice(len(CALIBRATION_TEXTS),\n                               min(4, len(CALIBRATION_TEXTS)), replace=False)\n        total_loss = 0.0\n        total_tokens = 0\n        for idx in batch_idx:\n            enc = tokenizer(CALIBRATION_TEXTS[idx], return_tensors=\"pt\",\n                            truncation=True, max_length=128)\n            enc = {k: v.to(args.device) for k, v in enc.items()}\n            labels = enc[\"input_ids\"].clone()\n            out = model(**enc, labels=labels)\n            if not (np.isnan(out.loss.item()) or np.isinf(out.loss.item())):\n                out.loss.backward()\n                total_loss += out.loss.item() * labels.numel()\n                total_tokens += labels.numel()\n        if total_tokens == 0:\n            continue\n        torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=0.5)\n        optimizer.step()\n        history.append(total_loss / total_tokens)\n    model.eval()\n\n    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    post_facts, _ = measure_facts(model, tokenizer, args.device)\n\n    for h in cont_hooks:\n        h.remove()\n    del model\n    if torch.backends.mps.is_available():\n        torch.mps.empty_cache()\n\n    return {\n        \"seed\": seed,\n        \"base_ppl\": round(base_ppl, 4),\n        \"base_facts\": base_facts,\n        \"pre_melt_ppl\": round(pre_ppl, 4),\n        \"pre_melt_ratio\": round(pre_ppl / base_ppl, 4),\n        \"pre_facts\": pre_facts,\n        \"post_melt_ppl\": round(post_ppl, 4),\n        \"post_melt_ratio\": round(post_ppl / base_ppl, 4),\n        \"post_facts\": post_facts,\n        \"continuation_params\": n_trainable,\n        \"final_loss\": round(history[-1], 4) if history else None,\n    }\n\n\ndef summarize(key, rows):\n    vals = np.array([r[key] for r in rows], dtype=float)\n    return {\n        \"mean\": round(float(vals.mean()), 4),\n        \"std\": round(float(vals.std(ddof=1)) if len(vals) > 1 else 0.0, 4),\n        \"min\": round(float(vals.min()), 4),\n        \"max\": round(float(vals.max()), 4),\n        \"values\": [round(float(v), 4) for v in vals],\n    }\n\n\ndef main():\n    p = argparse.ArgumentParser(\n        description=__doc__,\n        formatter_class=argparse.RawDescriptionHelpFormatter)\n    p.add_argument(\"--model\", default=\"Qwen/Qwen3-8B\")\n    p.add_argument(\"--device\", default=\"cpu\")\n    p.add_argument(\"--zero-rate\", type=float, default=0.5)\n    p.add_argument(\"--residual-rank\", type=int, default=32)\n    p.add_argument(\"--melt-steps\", type=int, default=100)\n    p.add_argument(\"--lr\", type=float, default=1e-4)\n    p.add_argument(\"--seeds\", type=int, default=5,\n                   help=\"number of seeds 0..N-1\")\n    p.add_argument(\"--seed-list\", type=str, default=None,\n                   help=\"comma-separated explicit seeds (overrides --seeds)\")\n    args = p.parse_args()\n\n    if args.seed_list:\n        seeds = [int(s) for s in args.seed_list.split(\",\")]\n    else:\n        seeds = list(range(args.seeds))\n\n    log(f\"\\n{'='*70}\")\n    log(\"  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?\")\n    log(f\"{'='*70}\")\n    log(f\"  Model: {args.model}  Device: {args.device}\")\n    log(f\"  Seeds: {seeds}\")\n    log(f\"  register: functional (reproducibility — seed variance on PPL)\")\n\n    rows = []\n    base_facts_cached = None\n    t0 = time.time()\n    for i, seed in enumerate(seeds):\n        log(f\"\\n{'─'*70}\")\n        log(f\"  SEED {seed}  ({i+1}/{len(seeds)})   [{time.time()-t0:.0f}s elapsed]\")\n        log(f\"{'─'*70}\")\n        r = run_one_seed(args, seed, base_facts_cached)\n        base_facts_cached = r[\"base_facts\"]  # deterministic; cache after first\n        rows.append(r)\n        log(f\"  base PPL={r['base_ppl']}  facts={r['base_facts']}/15\")\n        log(f\"  pre-melt  ratio={r['pre_melt_ratio']:.3f}x \"\n            f\"(PPL {r['pre_melt_ppl']}, facts {r['pre_facts']}/15)\")\n        log(f\"  post-melt ratio={r['post_melt_ratio']:.3f}x \"\n            f\"(PPL {r['post_melt_ppl']}, facts {r['post_facts']}/15, \"\n            f\"final_loss {r['final_loss']})\")\n\n    # Summaries\n    pre_sum = summarize(\"pre_melt_ratio\", rows)\n    post_sum = summarize(\"post_melt_ratio\", rows)\n    base_sum = summarize(\"base_ppl\", rows)\n\n    log(f\"\\n{'='*70}\")\n    log(\"  SUMMARY\")\n    log(f\"{'='*70}\")\n    log(f\"  base PPL          : {base_sum['mean']} \"\n        f\"(std {base_sum['std']}, should be ~0 = determinism check)\")\n    log(f\"  pre-melt  (mask)  : {pre_sum['mean']:.3f}x \"\n        f\"± {pre_sum['std']:.3f}  [{pre_sum['min']:.3f}, {pre_sum['max']:.3f}]\")\n    log(f\"  post-melt (full)  : {post_sum['mean']:.3f}x \"\n        f\"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]\")\n    log(f\"  headline claim    : 1.03x  ->  observed mean {post_sum['mean']:.3f}x, \"\n        f\"best-seed {post_sum['min']:.3f}x\")\n\n    out_dir = _PROJECT_ROOT / \"results\" / \"crystal-sieve-repro\"\n    out_dir.mkdir(parents=True, exist_ok=True)\n    slug = args.model.replace(\"/\", \"_\")\n    result = {\n        \"register\": \"functional (reproducibility — seed variance on PPL)\",\n        \"model\": args.model,\n        \"device\": args.device,\n        \"zero_rate\": args.zero_rate,\n        \"residual_rank\": args.residual_rank,\n        \"melt_steps\": args.melt_steps,\n        \"lr\": args.lr,\n        \"seeds\": seeds,\n        \"per_seed\": rows,\n        \"summary\": {\n            \"base_ppl\": base_sum,\n            \"pre_melt_ratio\": pre_sum,\n            \"post_melt_ratio\": post_sum,\n        },\n        \"headline_claim\": 1.03,\n        \"elapsed_s\": round(time.time() - t0, 1),\n    }\n    out_path = out_dir / f\"{slug}.json\"\n    with open(out_path, \"w\") as f:\n        json.dump(result, f, indent=2)\n    log(f\"\\n  Saved to {out_path}\")\n    log(f\"{'='*70}\\n\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py
```

### Thinking

 I need to decide on a testing strategy—running a full seed on the 8B model with melt is too expensive time-wise, so I'm leaning toward a smoke test with minimal melt steps and just one seed to verify the harness doesn't crash, even though it'll still hit the expensive SVD and sieve operations. The smoke run should take about 3-5 minutes total—loading the 8B model, running SVD and sieve quantiles, generating facts, and stepping through melt a few times. I'll kick it off in the background and monitor progress. First though, let me do a quick lint and syntax check with ruff and Python compilation to catch any obvious issues.

## Assistant

Let me lint and syntax-check before running:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -20; echo \"---COMPILE---\"; uv run python -m py_compile scripts/experiments/crystal_sieve_repro.py && echo \"compile OK\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
|                            ^^^^^^^^^^^^^^^^^^^^^^
306 |                 return corrected
307 |             return hook_fn
    |
help: Replace with `(corrected, *out[1:])`

F541 [*] f-string without any placeholders
   --> scripts/experiments/crystal_sieve_repro.py:401:9
    |
399 |     log(f"  Model: {args.model}  Device: {args.device}")
400 |     log(f"  Seeds: {seeds}")
401 |     log(f"  register: functional (reproducibility — seed variance on PPL)")
    |         ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
402 |
403 |     rows = []
    |
help: Remove extraneous `f` prefix

Found 5 errors.
[*] 2 fixable with the `--fix` option (3 hidden fixes can be enabled with the `--unsafe-fixes` option).
---COMPILE---
compile OK
```

### Thinking

 I need to review all five linting errors and work through fixing them—the f-string without a placeholder, the unused loop variable, the closure-in-loop issue, and the tuple unpacking suggestion. Let me pull up the full output to see what I'm working with.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | grep -E \"^[A-Z][0-9]+|-->\" | head -40"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
F401 [*] `torch.nn.functional` imported but unused
  --> scripts/experiments/crystal_sieve_repro.py:47:31
   --> scripts/experiments/crystal_sieve_repro.py:250:20
F841 Local variable `base_total` is assigned to but never used
   --> scripts/experiments/crystal_sieve_repro.py:270:21
   --> scripts/experiments/crystal_sieve_repro.py:305:28
F541 [*] f-string without any placeholders
   --> scripts/experiments/crystal_sieve_repro.py:401:9
```

### Thinking

 I'm identifying the specific linting issues to fix: removing the unused F import, eliminating the unused `base_total` variable, stripping the f-string prefix from the register line, and noting that the closure pattern on line 305 is functionally acceptable despite the B007/B023 warnings.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "import torch.nn as nn\nimport torch.nn.functional as F\nfrom transformers import AutoModelForCausalLM, AutoTokenizer",
  "new_content": "import torch.nn as nn\nfrom transformers import AutoModelForCausalLM, AutoTokenizer"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    if base_facts_cached is None:\n        base_facts, base_total = measure_facts(model, tokenizer, args.device)\n    else:\n        base_facts, base_total = base_facts_cached, len(FACT_PROMPTS)",
  "new_content": "    if base_facts_cached is None:\n        base_facts, _ = measure_facts(model, tokenizer, args.device)\n    else:\n        base_facts = base_facts_cached"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "                if isinstance(out, tuple):\n                    return (corrected,) + out[1:]\n                return corrected",
  "new_content": "                if isinstance(out, tuple):\n                    return (corrected, *out[1:])\n                return corrected"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    log(f\"  register: functional (reproducibility — seed variance on PPL)\")",
  "new_content": "    log(\"  register: functional (reproducibility — seed variance on PPL)\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -10"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
247 |         torch.mps.manual_seed(seed)
248 |
249 |     SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]
    |                    ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
250 |     RESIDUAL_LAYERS = [0, 9, 21, 26]
    |
help: Replace with `[*list(range(1, 27)), 32, 33, 34]`

Found 1 error.
No fixes available (1 hidden fix can be enabled with the `--unsafe-fixes` option).
```

### Thinking

 I see that RUF005 is just a style preference about unpacking, and since it matches the original code exactly, I'll apply the suggested fix to keep ruff happy without changing the functionality.

## Assistant

One style nit (matches the s196 original). Fixing for a clean lint:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]",
  "new_content": "    SIEVE_LAYERS = [*range(1, 27), 32, 33, 34]"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -3"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Thinking

 Running a quick smoke test with minimal parameters to verify the pipeline works end-to-end, then I'll either monitor it or launch the full run directly depending on how fast it completes.

## Assistant

Lint clean. Now a fast smoke test (1 seed, 3 melt steps) to verify end-to-end before the real multi-seed run:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/crystal_sieve_repro.py --model Qwen/Qwen3-8B --device mps --seed-list 0 --melt-steps 3 2>&1 | tee /tmp/sieve_repro_smoke.log",
  "background": "sieve-repro-smoke"
}
```

**Summary:** $ uv run python scripts/experiments/c...

**Output:**
```
Background job job-1 started.
Command: cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/crystal_sieve_repro.py --model Qwen/Qwen3-8B --device mps --seed-list 0 --melt-steps 3 2>&1 | tee /tmp/sieve_repro_smoke.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 60 && tail -25 /tmp/sieve_repro_smoke.log",
  "timeout": 75000
}
```

**Summary:** $ sleep 60 && tail -25 /tmp/sieve_rep...

**Output:**
```
Exit code: 0
Stdout:
======================================================================

======================================================================
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
======================================================================
======================================================================
  Model: Qwen/Qwen3-8B  Device: mps
  Model: Qwen/Qwen3-8B  Device: mps
  Seeds: [0]
  Seeds: [0]
  register: functional (reproducibility — seed variance on PPL)
  register: functional (reproducibility — seed variance on PPL)

──────────────────────────────────────────────────────────────────────

──────────────────────────────────────────────────────────────────────
  SEED 0  (1/1)   [0s elapsed]
  SEED 0  (1/1)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
`torch_dtype` is deprecated! Use `dtype` instead!
Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]Loading weights:   0%|          | 1/399 [00:00<02:53,  2.29it/s]Loading weights:   7%|▋         | 28/399 [00:00<00:05, 67.83it/s]Loading weights:  18%|█▊        | 70/399 [00:00<00:02, 155.28it/s]Loading weights:  26%|██▌       | 103/399 [00:00<00:01, 200.99it/s]Loading weights:  34%|███▍      | 137/399 [00:00<00:01, 236.64it/s]Loading weights:  42%|████▏     | 169/399 [00:00<00:00, 255.73it/s]Loading weights:  51%|█████     | 204/399 [00:01<00:00, 281.58it/s]Loading weights:  59%|█████▉    | 236/399 [00:01<00:00, 291.23it/s]Loading weights:  67%|██████▋   | 269/399 [00:01<00:00, 297.28it/s]Loading weights:  76%|███████▌  | 302/399 [00:01<00:00, 305.96it/s]Loading weights:  84%|████████▍ | 335/399 [00:01<00:00, 311.73it/s]Loading weights:  92%|█████████▏| 368/399 [00:01<00:00, 308.57it/s]Loading weights: 100%|██████████| 399/399 [00:01<00:00, 241.49it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
The following generation flags are not valid and may be ignored: ['top_p', 'top_k']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
```

### Thinking

 I'm waiting for the process to advance through its stages—baseline, sieve, and melt—before checking again. I'll give it about 90 seconds and then poll once more, rather than repeatedly checking.

## Assistant

Model loaded, running through baseline/sieve. Let me wait for the smoke to finish the pipeline:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 120 && grep -vE \"Loading weights|it/s|Warning|generation flags|torch_dtype\" /tmp/sieve_repro_smoke.log | tail -20",
  "timeout": 135000
}
```

**Summary:** $ sleep 120 && grep -vE "Loading weig...

**Output:**
```
Exit code: 0
Stdout:
======================================================================
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
======================================================================
======================================================================
  Model: Qwen/Qwen3-8B  Device: mps
  Model: Qwen/Qwen3-8B  Device: mps
  Seeds: [0]
  Seeds: [0]
  register: functional (reproducibility — seed variance on PPL)
  register: functional (reproducibility — seed variance on PPL)

──────────────────────────────────────────────────────────────────────

──────────────────────────────────────────────────────────────────────
  SEED 0  (1/1)   [0s elapsed]
  SEED 0  (1/1)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
```

### Thinking

 Still waiting on the baseline results after a few minutes. The pipeline's moving through load and baseline PPL quickly, but the baseline facts generation is taking a while since it's running 15 generations at 30 tokens each on the MPS device. After that comes the sieve install with SVD and quantiles, then the pre-melt and melt steps, finishing with post-processing. I should check the background job output directly to see what's happening.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "sieve-repro-smoke" (job-1)

**Output:**
```
Job "sieve-repro-smoke" (job-1) — running


======================================================================

======================================================================
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
======================================================================
======================================================================
  Model: Qwen/Qwen3-8B  Device: mps
  Model: Qwen/Qwen3-8B  Device: mps
  Seeds: [0]
  Seeds: [0]
  register: functional (reproducibility — seed variance on PPL)
  register: functional (reproducibility — seed variance on PPL)

──────────────────────────────────────────────────────────────────────

──────────────────────────────────────────────────────────────────────
  SEED 0  (1/1)   [0s elapsed]
  SEED 0  (1/1)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]
Loading weights:   0%|          | 1/399 [00:00<02:53,  2.29it/s]
Loading weights:   7%|▋         | 28/399 [00:00<00:05, 67.83it/s]
Loading weights:  18%|█▊        | 70/399 [00:00<00:02, 155.28it/s]
Loading weights:  26%|██▌       | 103/399 [00:00<00:01, 200.99it/s]
Loading weights:  34%|███▍      | 137/399 [00:00<00:01, 236.64it/s]
Loading weights:  42%|████▏     | 169/399 [00:00<00:00, 255.73it/s]
Loading weights:  51%|█████     | 204/399 [00:01<00:00, 281.58it/s]
Loading weights:  59%|█████▉    | 236/399 [00:01<00:00, 291.23it/s]
Loading weights:  67%|██████▋   | 269/399 [00:01<00:00, 297.28it/s]
Loading weights:  76%|███████▌  | 302/399 [00:01<00:00, 305.96it/s]
Loading weights:  84%|████████▍ | 335/399 [00:01<00:00, 311.73it/s]
Loading weights:  92%|█████████▏| 368/399 [00:01<00:00, 308.57it/s]
Loading weights: 100%|██████████| 399/399 [00:01<00:00, 241.49it/s]
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
The following generation flags are not valid and may be ignored: ['top_p', 'top_k']. Set `TRANSFORMERS_VERBOSITY=info` for more details.
```

### Thinking

 The model's loaded and baseline facts generation is running through the 8B model on MPS, which is the main bottleneck—15 greedy generations of 30 tokens each, repeated 3 times across base/pre/post phases. For the full 5-seed run, base facts cache after the first seed, but pre and post facts regenerate every time, so that's where most of the compute time goes.

I'm estimating roughly 10-12 minutes per seed with facts included, which would be about an hour for 5 seeds—doable but tight. Since the core claim is about the 1.03× PPL ratio and facts are more of a secondary validation, I'm thinking about adding a `--skip-facts` flag to speed up the real run and allow more seeds. I could either skip facts entirely or just measure them at the final post-melt state to cut the generation cost by two-thirds while still checking if the compressed model retains factual knowledge. Let me let the smoke test finish first to validate the full pipeline works end-to-end, then add the flag for the production run.

## Assistant

Smoke is in the slow baseline-facts phase (15 greedy generations × 30 tokens on MPS — the dominant cost, run 3× per seed). While it validates the full path, let me add a `--skip-facts` flag so the real multi-seed sweep can afford more seeds (the audit's headline is the PPL ratio, not facts).

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    # Baseline (deterministic; measured per-seed as a sanity check)\n    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    if base_facts_cached is None:\n        base_facts, _ = measure_facts(model, tokenizer, args.device)\n    else:\n        base_facts = base_facts_cached",
  "new_content": "    # Baseline (deterministic; measured per-seed as a sanity check)\n    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    if args.skip_facts:\n        base_facts = -1\n    elif base_facts_cached is None:\n        base_facts, _ = measure_facts(model, tokenizer, args.device)\n    else:\n        base_facts = base_facts_cached"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    pre_facts, _ = measure_facts(model, tokenizer, args.device)",
  "new_content": "    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    pre_facts = (-1 if args.skip_facts\n                 else measure_facts(model, tokenizer, args.device)[0])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    post_facts, _ = measure_facts(model, tokenizer, args.device)",
  "new_content": "    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    post_facts = (-1 if args.skip_facts\n                  else measure_facts(model, tokenizer, args.device)[0])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    p.add_argument(\"--seed-list\", type=str, default=None,\n                   help=\"comma-separated explicit seeds (overrides --seeds)\")\n    args = p.parse_args()",
  "new_content": "    p.add_argument(\"--seed-list\", type=str, default=None,\n                   help=\"comma-separated explicit seeds (overrides --seeds)\")\n    p.add_argument(\"--skip-facts\", action=\"store_true\",\n                   help=\"skip fact-retrieval generations (3x faster; PPL is \"\n                        \"the headline metric for the reproducibility audit)\")\n    args = p.parse_args()"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Thinking

 The smoke test ran successfully end-to-end and generated the JSON output, so the first acceptance criterion is satisfied. Looking at the results from seed 0, the sieve-only preprocessing achieved a 2.125× speedup, which matches exactly what was observed in the earlier s196 experiment at 29 layers—that's a good sign the pipeline is working correctly. After applying the three melt steps, the improvement dropped slightly to 2.059×.

The key insight is that with only three melt steps, the gains are modest, but the full protocol calls for 100 steps to reach the claimed 1.03× speedup. I need to run the full experiment across multiple seeds to properly estimate the mean and variance. I'm planning to launch the real run with 8 seeds at 100 melt steps, skipping the facts generation to save time. Based on rough estimates, each seed will take around 10-15 minutes (mostly from the 100-step melt process on the 8B model), so the full run should complete in 1.5-2 hours running in the background. The critical question is whether the full melt actually achieves the claimed 1.03× speedup—if it doesn't reach that on any seed, that's itself a significant finding about reproducibility.

I'm setting up to run this in a tmux window so the progress can be monitored live, and I need to check which tmux window is available first.

## Assistant

Smoke completed end-to-end and wrote JSON — **task #1 acceptance met**. And it already reproduces a key s196 number: **pre-melt (sieve-only) = 2.125×**, matching s196's reported "2.12× at 29 layers" exactly. Post-melt only moved to 2.059× because the smoke used 3 melt steps (headline needs 100).

Let me lint the edits, complete task #1, and launch the real sweep.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -3; echo \"---smoke json---\"; cat results/crystal-sieve-repro/Qwen_Qwen3-8B.json | python3 -c \"import json,sys; d=json.load(sys.stdin); print('per_seed:', d['per_seed']); print('elapsed_s:', d['elapsed_s'])\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
---smoke json---
per_seed: [{'seed': 0, 'base_ppl': 10.1505, 'base_facts': 12, 'pre_melt_ppl': 21.5731, 'pre_melt_ratio': 2.1253, 'pre_facts': 11, 'post_melt_ppl': 20.8971, 'post_melt_ratio': 2.0587, 'post_facts': 11, 'continuation_params': 1048576, 'final_loss': 4.0478}]
elapsed_s: 203.2
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux list-windows -t main 2>&1; echo \"---panes main:1---\"; tmux capture-pane -p -t main:1 2>/dev/null | grep -vE \"^$\" | tail -3; echo \"---panes main:2---\"; tmux capture-pane -p -t main:2 2>/dev/null | grep -vE \"^$\" | tail -3"
}
```

**Summary:** $ tmux list-windows -t main 2>&1; ech...

**Output:**
```
Exit code: 0
Stdout:
1: local- (1 panes) [120x24] [layout b704,120x24,0,0,7] @7
2: local* (1 panes) [120x24] [layout b705,120x24,0,0,8] @8 (active)
---panes main:1---
[26-06-09][9:03:16][mwhitford@olga][0][~/src/verbum][git:main]
λ
---panes main:2---
tee results/binding-schedule-semantic/run.log  0.00s user 0.00s system 0% cpu 1:02.09 total
[26-06-09][9:23:00][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Thinking

 Both tmux windows are ready at the prompt, so I'll run the main test in window 1. The smoke test took about 3.4 minutes for one seed with facts and 3 melt steps. If I skip facts but run 100 melt steps instead, I'll lose roughly 2 minutes from the three fact generations but add about 97 more melt iterations—I need to estimate how long each melt step actually takes based on what I saw in the smoke run.

Rather than trying to decompose the timing further, I'll just launch 8 seeds with skip-facts and 100 steps to get good statistics. At an estimated 8-12 minutes per seed, that's about 1-1.5 hours total, which is reasonable for a tmux session. I'm setting up the command to run the crystal sieve reproduction script with those parameters, piping output to a log file so I can monitor progress. Let me finish the current task and then kick off the run.

## Assistant

Both tmux windows are idle. Task #1 is complete (end-to-end run + JSON write, lint clean). Launching the real sweep in `main:1`.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 \"cd ~/src/verbum && uv run python scripts/experiments/crystal_sieve_repro.py --model Qwen/Qwen3-8B --device mps --seeds 8 --melt-steps 100 --skip-facts 2>&1 | tee results/crystal-sieve-repro/run.log\" Enter; sleep 3; echo \"launched\""
}
```

**Summary:** $ tmux send-keys -t main:1 "cd ~/src/...

**Output:**
```
Exit code: 0
Stdout:
launched
```

### Thinking

 I need to verify that it's running with one read per async discipline, then save the checkpoint and wait.

## Assistant

Let me verify it's running (one read), then checkpoint per async discipline.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 30; tmux capture-pane -p -t main:1 | grep -vE \"^$|Loading weights|it/s\" | tail -12; echo \"---proc---\"; ps aux | grep \"crystal_sieve_repro\" | grep -v grep | wc -l | tr -d ' '"
}
```

**Summary:** $ sleep 30; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
Seeds: [0, 1, 2, 3, 4, 5, 6, 7]
  register: functional (reproducibility — seed variance on PPL)
  register: functional (reproducibility — seed variance on PPL)
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
  SEED 0  (1/8)   [0s elapsed]
  SEED 0  (1/8)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
---proc---
2
```

### Thinking

 The job is running with 8 seeds across two processes, so I'll checkpoint here and wait for it to complete—estimated around 1-1.5 hours. Following async discipline, since the job is verified and not blocked, I should move on to other work or report that I'm waiting rather than polling repeatedly.

## Assistant

**ASYNC checkpoint:** 8-seed sieve-repro sweep verified running in `tmux main:1` (`results/crystal-sieve-repro/run.log`), process alive, seeds [0–7], 100 melt steps, `--skip-facts`. Register: functional/reproducibility.

The smoke already gave one finding for free: **sieve-only (pre-melt) reproduces s196's 2.12× exactly and deterministically per-seed**. The open question is the *post-melt* distribution across seeds (the 1.03× headline vs the 3.23× rerun). Estimated ~1–1.5 hr for 8 seeds.

Let me wait for the first full seed (validates the 100-step melt config and gives the first real post-melt number), then hold for completion.

### Tool Call: shell_command (rejected)


```json
{
  "command": "sleep 600; echo \"=== run.log (filtered) ===\"; grep -vE \"^$|Loading weights|it/s|Warning|torch_dtype|generation flags\" results/crystal-sieve-repro/run.log 2>/dev/null | tail -18",
  "timeout": 615000,
  "working_directory": "/Users/mwhitford/src/verbum"
}
```

**Summary:** $ sleep 600; echo "=== run.log (filte...

## System


Prompt stopped

## User

if that run is going to be hours we need to cross session boundaries instead of keeping tasks pending in the editor tooling


### Thinking

 The user's right that this could take a while, so instead of leaving tasks hanging I should save the current state to a file so the next session can pick up where we left off. I'll check if the run is still active, update the status document with what's in progress, commit the finished harness code, and document the exact command to resume along with where the results will end up.

## Assistant

You're right — the editor task list won't survive a session boundary; only git + `state.md` do (λ feed_forward). Let me check current progress, then encode the in-flight state durably and commit the harness so a future session can pick up cleanly.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== progress ===\"; grep -vE \"^$|Loading weights|it/s|Warning|torch_dtype|generation flags\" results/crystal-sieve-repro/run.log 2>/dev/null | tail -16; echo \"=== proc alive ===\"; ps aux | grep crystal_sieve_repro | grep -v grep | wc -l | tr -d ' '"
}
```

**Summary:** $ echo "=== progress ==="; grep -vE "...

**Output:**
```
Exit code: 0
Stdout:
=== progress ===
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
  CRYSTAL-SIEVE REPRODUCIBILITY — is 1.03x the center or the tail?
======================================================================
======================================================================
  Model: Qwen/Qwen3-8B  Device: mps
  Model: Qwen/Qwen3-8B  Device: mps
  Seeds: [0, 1, 2, 3, 4, 5, 6, 7]
  Seeds: [0, 1, 2, 3, 4, 5, 6, 7]
  register: functional (reproducibility — seed variance on PPL)
  register: functional (reproducibility — seed variance on PPL)
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
  SEED 0  (1/8)   [0s elapsed]
  SEED 0  (1/8)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
=== proc alive ===
2
```

### Thinking

 Seed 0 is taking longer than expected even with --skip-facts enabled. The melt phase has expanded to 100 steps compared to just 3 in the smoke test, and with 4 forward-backward passes through the 8B model on MPS, this could reasonably take 10-15 minutes total, so it might still be running within expected bounds.

The log appears stalled because I removed the per-step progress logging from the reproduction script, so there's no intermediate output between the seed start and the final summary. That's fine — it just means I can't see the melt steps as they execute. Scaling to 8 seeds puts us at roughly 1.5-2 hours total, which justifies crossing the session boundary.

Now I need to handle the commits carefully. The harness script itself is code and can be committed autonomously, so I'll mark that as complete. For state.md, I can write updates freely during work, but committing anything to mementum/ requires approval, so I'll update the file and propose that commit to the user since we're crossing a boundary.

I'll add a new SESSION 208 IN-FLIGHT block to state.md right after the program section, updating the timestamp and session number at the top, then lay out what's running and what the next session should check.

## Assistant

The run survives in tmux independent of this session, but the *handoff* must live in git. Let me encode it. First, update `state.md` with an in-flight s208 block, then commit the harness (code, autonomous) and propose the state.md commit (mementum, approval-gated).

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 40
}
```

**Summary:** Reading state.md (0-40)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-09 | Session: 207
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
> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /
> H31@L27 subject value-transfer ✅ semantically REAL; s207 did **#6 SVD φ-ratio
> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;
> next backlog: **#11 GTSM finite-budget λ(l)** or **#7/#8 reproducibility**), build its named
> discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 207 HEADLINE — AUDIT #6 (SVD φ-ratio 0.6299): geometric-φ-constant
> REFUTED; the low-rank spectral head is REAL & non-random.** Register: spectral.
> Reran s137's exact definition (mean of top-5 consecutive σ-ratios, per layer)
> on all 5 families (Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B) vs
> **Marchenko–Pastur + shuffled** nulls (8 seeds, raw+centered) + a
> geometric-vs-power-law shape fit. `svd_phi_null.py` (register: spectral).
> - **Register gate fired on ME first:** first probe used the wrong window (bulk
>   ratios ≈0.99 for everything); tracing s137 pinned the real object (top-5 head
>   ratio). Re-measure the exact quantity → phenomenon reproduced (Pythia-160m
>   raw 0.597 vs page 0.604).
> - **✅ substrate REAL:** model head ratio **0.575±0.027 (raw)** / 0.67 (centered)

[CONTENT TRUNCATED] Showing lines 1 to 40 of 2765 total lines. Use line_offset=40 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-06-09 | Session: 207",
  "new_content": "> Last updated: 2026-06-09 | Session: 208"
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
  "original_content": "> distill real working data from assumptions/biased methodology, one\n> control per session, until a small hard core of verified claims remains.\n\n> **▶ SESSION 207 HEADLINE",
  "new_content": "> distill real working data from assumptions/biased methodology, one\n> control per session, until a small hard core of verified claims remains.\n\n> **▶ SESSION 208 — AUDIT #7 (crystal-sieve 1.03× reproducibility): RUN IN FLIGHT.**\n> Register: **functional (reproducibility — seed variance on a PPL measurement).**\n> Picked #7 from the backlog: s196 reported crystal-sieve + 4 continuation\n> residuals = **1.03× PPL** at 29 sieved layers (Qwen3-8B), but its own note says a\n> rerun gave **3.23×** (\"training sensitive to init/batch order\"). The control:\n> seed it, run N seeds, report **mean ± std** — is 1.03× the center or a lucky tail?\n> - **NEW HARNESS (committed):** `scripts/experiments/crystal_sieve_repro.py`\n>   (`# register: functional`). Exact s196 `beta_expansion.py` pipeline (L0 SVD\n>   r=750 + sieve L1–26,32–34 + 4 rank-32 continuations, 100-step CE melt) wrapped\n>   in a **seed loop** that reloads the model fresh per seed and seeds torch+numpy+mps.\n> - **Decomposition (no extra runs):** `pre_melt_ratio` std = the **mask-subsample\n>   variance** (FFN projections >10M elems → `torch.randperm[:5M]` for the quantile\n>   threshold — an unseeded source s196's note *missed*); `post_melt_ratio` std =\n>   mask + continuation-init + training. The s196 note blames \"batch order\" but\n>   batch order is `RandomState(step)` = **deterministic**; the real culprits are\n>   the mask subsample + `torch.randn` continuation init (both now seeded).\n> - **SMOKE (seed 0, 3 melt steps, WITH facts) already confirmed:** **pre-melt\n>   (sieve-only) = 2.125× — reproduces s196's \"2.12× at 29 layers\" exactly**, and\n>   deterministic given the seed. Post-melt at 3 steps only reached 2.059× (needs\n>   the full 100-step melt to chase 1.03×). base PPL 10.15 (determinism check std 0).\n> - **▶ IN-FLIGHT RUN:** `tmux main:1`, 8 seeds × 100 melt steps, `--skip-facts`\n>   (PPL is the headline; facts 3× the cost). `results/crystal-sieve-repro/run.log`\n>   + `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` (overwritten on completion;\n>   the JSON currently on disk is the seed-0 smoke). No per-step logging between the\n>   `SEED n` banner and its summary — ~12–15 min/seed, **~1.5–2 hr total**, so it\n>   crosses the session boundary. Started ~09:40.\n> - **▶ NEXT SESSION — RESUME HERE (do not re-launch if still running):**\n>   1. `ps aux | grep crystal_sieve_repro` — if alive, `tail results/crystal-sieve-repro/run.log`; if dead, read `results/crystal-sieve-repro/Qwen_Qwen3-8B.json`.\n>   2. Read the `summary` block: `post_melt_ratio.{mean,std,min,max,values}` and `pre_melt_ratio` (mask-only variance). Verdict logic: **1.03× VERIFIED-reproducible** iff post mean ≈ 1.03× with small std; **REFUTED-as-reproducible** (substrate real, headline = lucky tail) iff mean ≫ 1.03× and 1.03× only at the min — the expected meta-pattern (`audit-meta-pattern.md`): the *sieve substrate* (2.12× pre-melt) is real & deterministic, the *1.03× headline* is the over-read.\n>   3. Update `audit-registry.md` #7 row (status + number + JSON path) + worked-examples row; add a caveat to `crystal-sieve-architecture.md` §\"Open Issues\" #1 (replace \"1.03× on first run, 3.23× on rerun\" with the measured mean ± std).\n>   4. Replace this IN-FLIGHT block with the s208 HEADLINE; commit (💡/🎯).\n> - If the run died early (NaN/OOM), the harness is re-runnable: same command in\n>   `tmux main:1`. Fewer seeds OK (`--seed-list 0,1,2,3`).\n\n> **▶ SESSION 207 HEADLINE"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I've updated state.md and now I need to commit the harness separately, staging just the script before proposing the state.md changes through the approval process. Let me check the git status and diff to follow proper commit conventions.

## Assistant

state.md encoded with a full resume protocol. Now commit the harness (code — autonomous), then propose the mementum commit (approval-gated).

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short; echo \"---log style---\"; git log --oneline -5",
  "operation": "status",
  "summary": "check status"
}
```

**Summary:** Git status: check status

**Output:**
```
Exit code: 0
Stdout:
M mementum/state.md
?? mementum/knowledge/chats/session-206.md
?? mementum/knowledge/chats/session-207.md
?? results/crystal-sieve-repro/
?? scripts/experiments/crystal_sieve_repro.py
---log style---
f6551f4 🌀 propagate audit #6 — index + stale φ-memory caveated to s207
0e1cff6 💡 audit #6 — SVD φ-ratio 0.6299: geometric-φ-constant REFUTED, low-rank head REAL & non-random
f509c48 🌀 register law as gene + structural slot — move it off recall-gated memory
f209f28 🔁 audit-meta-pattern — the two laws are one: register, not rule
99536ec 🌀 state — session 206: audit #5 done + instrument-must-match-the-claim law
```

## User

it looks like it's showing wrong info for facts is that expected?  I was expecting to see 12/15 there


### Thinking

 Looking at the JSON data from the smoke test, I see base_facts is 12, pre_facts is 11, and post_facts is 11, but the summary log showed "facts=.../15" — the user was expecting to see 12/15 displayed there, so I need to figure out where that discrepancy is coming from.

The current run with --skip-facts sets all fact counts to -1 intentionally (to speed up the reproducibility sweep), so if the user is looking at the in-flight run.log, they'd see "facts=-1/15" which would look wrong compared to the smoke's actual measurement of 12/15. The baseline model itself only achieves 12 out of 15 facts with the greedy 30-token generation and substring matching approach, so that's the ceiling for this measurement method.

I should clarify that the -1 is a deliberate sentinel value for skipped facts, but the display is misleading — I could improve it by showing "skipped" instead of "-1/15" to make it clearer that facts weren't measured in this run. If they want the full facts breakdown across all seeds, I can re-run without the --skip-facts flag, though it'll take longer.

## Assistant

Good catch — let me check exactly what's being shown.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== current run.log facts lines ===\"; grep -iE \"facts\" results/crystal-sieve-repro/run.log | tail -8; echo \"=== smoke JSON facts (on disk) ===\"; python3 -c \"import json; d=json.load(open('results/crystal-sieve-repro/Qwen_Qwen3-8B.json')); [print(k, d['per_seed'][0].get(k)) for k in ('base_facts','pre_facts','post_facts')]\"; echo \"=== seed 0 done yet? ===\"; grep -E \"SEED|ratio=\" results/crystal-sieve-repro/run.log | tail -4"
}
```

**Summary:** $ echo "=== current run.log facts lin...

**Output:**
```
Exit code: 0
Stdout:
=== current run.log facts lines ===
  base PPL=10.1505  facts=-1/15
  base PPL=10.1505  facts=-1/15
  pre-melt  ratio=2.125x (PPL 21.5731, facts -1/15)
  pre-melt  ratio=2.125x (PPL 21.5731, facts -1/15)
  post-melt ratio=0.865x (PPL 8.7768, facts -1/15, final_loss 0.1128)
  post-melt ratio=0.865x (PPL 8.7768, facts -1/15, final_loss 0.1128)
=== smoke JSON facts (on disk) ===
base_facts 12
pre_facts 11
post_facts 11
=== seed 0 done yet? ===
  post-melt ratio=0.865x (PPL 8.7768, facts -1/15, final_loss 0.1128)
  post-melt ratio=0.865x (PPL 8.7768, facts -1/15, final_loss 0.1128)
  SEED 1  (2/8)   [204s elapsed]
  SEED 1  (2/8)   [204s elapsed]
```

### Thinking

 The in-flight run shows `facts=-1/15` which is the sentinel value for skipped facts, so that's working as intended even though the display could be clearer. But there's something much more significant here: seed 0 post-melt is showing 0.865×, which is actually below baseline performance.

This is a red flag for overfitting. The eval set and calibration set overlap significantly — they share common sentences — so when the melt trains on those calibration texts, it's essentially memorizing patterns from the eval set, which artificially tanks the perplexity. This train/eval contamination explains why the results are so unstable: the smoke run showed 2.059× while seed 0 shows 0.865×, both on the same supposedly-held-out eval set. That's the real issue driving the irreproducibility, not the facts measurement itself.

I'll make a quick fix to display "skipped" instead of the `-1/15` sentinel for clarity in future runs, then respond to the user with these findings.

## Assistant

Yes — that's expected, but the display is misleading. Two things:

**1. Why `-1/15`:** the in-flight sweep runs with `--skip-facts`, so facts aren't measured — `-1` is the "not-measured" sentinel. I skipped them because the fact probe is 15 greedy generations run 3× per seed (the dominant cost), and the audit's headline metric is the **PPL ratio**, not facts. The `12/15` you're remembering is from the **smoke** run (which *did* measure facts): base **12/15**, pre **11/15**, post **11/15**. Note the baseline model itself only scores 12/15 on this substring-match probe — that's the probe's ceiling, so 12/15 is correct, not 15/15.

The `-1/15` rendering is genuinely confusing though — let me patch it to print `skip` for future runs (won't disturb the running process):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "        rows.append(r)\n        log(f\"  base PPL={r['base_ppl']}  facts={r['base_facts']}/15\")\n        log(f\"  pre-melt  ratio={r['pre_melt_ratio']:.3f}x \"\n            f\"(PPL {r['pre_melt_ppl']}, facts {r['pre_facts']}/15)\")\n        log(f\"  post-melt ratio={r['post_melt_ratio']:.3f}x \"\n            f\"(PPL {r['post_melt_ppl']}, facts {r['post_facts']}/15, \"\n            f\"final_loss {r['final_loss']})\")",
  "new_content": "        rows.append(r)\n        def _f(v):\n            return \"skip\" if v == -1 else f\"{v}/15\"\n        log(f\"  base PPL={r['base_ppl']}  facts={_f(r['base_facts'])}\")\n        log(f\"  pre-melt  ratio={r['pre_melt_ratio']:.3f}x \"\n            f\"(PPL {r['pre_melt_ppl']}, facts {_f(r['pre_facts'])})\")\n        log(f\"  post-melt ratio={r['post_melt_ratio']:.3f}x \"\n            f\"(PPL {r['post_melt_ppl']}, facts {_f(r['post_facts'])}, \"\n            f\"final_loss {r['final_loss']})\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Thinking

 I'm noticing the seed 0 post-melt result sits at 0.865, which is below baseline, and there's an eval/calibration overlap that looks like the real reproducibility signal here. I should flag this to the user as the key finding and mention the seed-0 number along with the contamination hypothesis, then note that I'll confirm once the sweep finishes.

## Assistant

**2. The bigger signal already emerging.** Seed 0 just finished: **post-melt = 0.865×** (PPL 8.78, *below* the baseline 10.15), where the 3-step smoke gave 2.059×. That swing — and a sub-baseline ratio — is the smoking gun for the audit: the eval set **overlaps the calibration set** the melt trains on (e.g. "The theory of general relativity…", "She walked through the ancient forest…", "In a large mixing bowl…", "To solve this equation…", "The committee voted…", "The function takes two arguments…" appear in *both* `EVAL_TEXTS` and `CALIBRATION_TEXTS`). So the 100-step melt overfits the eval set → the "1.03×" is a train-contaminated number, and tiny init/mask differences swing it wildly (1.03× ↔ 3.23×). That train/eval contamination is very likely the *real* mechanism behind the irreproducibility the s196 note flagged.

I'll let the 8-seed sweep finish to get the mean ± std distribution, and I'll add a held-out eval check if the contamination hypothesis holds.

Let me lint the display fix, then return to encoding the handoff (the run continues in tmux regardless).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -3"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Thinking

 I need to commit the harness with the recent edits (the skip-facts flag and display fix), then decide whether to update state.md to reflect the new findings from the contamination analysis.

The contamination hypothesis and the 0.865× seed-0 result are important discoveries that should be documented before the session ends, so the next session knows to set up a held-out evaluation. I'll add these as a signal bullet in the in-flight block of state.md, then commit both the harness code and the enriched state file to preserve the progress across the session boundary.

## Assistant

The run continues in tmux regardless of this session. Let me finish the durable handoff — enrich `state.md` with the contamination finding (a real discovery worth surviving), then commit.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - **▶ IN-FLIGHT RUN:** `tmux main:1`, 8 seeds × 100 melt steps, `--skip-facts`",
  "new_content": "> - **★ SIGNAL (seed 0, full 100-step melt): post-melt = 0.865× — BELOW baseline**\n>   (PPL 8.78 < base 10.15), vs the 3-step smoke's 2.059×. Root cause spotted:\n>   **`EVAL_TEXTS` overlaps `CALIBRATION_TEXTS`** (≥6 shared sentences: general\n>   relativity, ancient forest, mixing bowl, isolate the variable, committee voted,\n>   two arguments→composition). The 100-step melt **overfits the eval set** → the\n>   \"1.03×\" is a *train-contaminated* number, and tiny init/mask differences swing\n>   it wildly (explains s196's 1.03× ↔ 3.23×). **This is the likely real mechanism\n>   of the irreproducibility.** NEXT SESSION: add a **held-out eval** (eval texts\n>   disjoint from calibration) — predict the contamination-free ratio is ≫ 1× and\n>   *stable*; the sub-1× values are the overfit tail. Same meta-pattern: sieve\n>   substrate real (2.12× deterministic), 1.03× headline = methodology artifact.\n> - **▶ IN-FLIGHT RUN:** `tmux main:1`, 8 seeds × 100 melt steps, `--skip-facts`"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now commit the harness (code — autonomous per AGENTS; only `mementum/` commits are approval-gated):

### Tool Call: git (failed)


```json
{
  "command": "git add scripts/experiments/crystal_sieve_repro.py results/crystal-sieve-repro/ && git commit -m \"$(cat <<'EOF'\n💡 audit #7 harness — seeded crystal-sieve reproducibility (pre/post variance decomposition)\n\n- scripts/experiments/crystal_sieve_repro.py (# register: functional).\n  Wraps the exact s196 beta_expansion pipeline (L0 SVD r=750 + sieve\n  L1-26,32-34 + 4 rank-32 continuations, 100-step CE melt) in a seed loop\n  that reloads the model fresh per seed and seeds torch+numpy+mps.\n- Decomposes variance with no extra runs: pre_melt_ratio std = mask-subsample\n  variance (FFN >10M elems -> torch.randperm[:5M] for the quantile threshold,\n  an unseeded source s196 missed); post_melt_ratio std = mask+init+training.\n  Batch order is RandomState(step) = deterministic, NOT a variance source\n  (the s196 note is wrong on that).\n- Smoke (seed 0): pre-melt sieve-only = 2.125x, reproduces s196's \"2.12x at\n  29 layers\" exactly and deterministically. --skip-facts for the PPL sweep.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "commit harness"
}
```

**Summary:** Git commit: commit harness

**Output:**
```
Exit code: 2
Stderr:
bash: -c: line 12: unexpected EOF while looking for matching `''
bash: -c: line 20: syntax error: unexpected end of file
```

### Thinking

 I'm realizing the issue is with how the apostrophe in "s196's" is being interpreted within the command substitution — the single-quoted heredoc delimiter should protect the content, but the whole expression is nested inside double quotes, which is causing the quote parsing to break down.

Rather than wrestling with escaping, I'll write the commit message to a temporary file and use the `-F` flag instead, which sidesteps the quoting problem entirely.

## Assistant

Heredoc quoting tripped on an apostrophe. Using a message file instead:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/sieve_repro_commit.txt",
  "content": "💡 audit #7 harness — seeded crystal-sieve reproducibility (pre/post variance decomposition)\n\n- scripts/experiments/crystal_sieve_repro.py (# register: functional).\n  Wraps the exact s196 beta_expansion pipeline (L0 SVD r=750 + sieve\n  L1-26,32-34 + 4 rank-32 continuations, 100-step CE melt) in a seed loop\n  that reloads the model fresh per seed and seeds torch+numpy+mps.\n- Decomposes variance with no extra runs: pre_melt_ratio std = mask-subsample\n  variance (FFN >10M elems -> torch.randperm[:5M] for the quantile threshold,\n  an unseeded source s196 missed); post_melt_ratio std = mask+init+training.\n  Batch order is RandomState(step) = deterministic, NOT a variance source.\n- Smoke (seed 0): pre-melt sieve-only = 2.125x, reproduces s196 \"2.12x at\n  29 layers\" exactly and deterministically. --skip-facts for the PPL sweep.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/sieve_repro_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/crystal_sieve_repro.py results/crystal-sieve-repro/ && git commit -F /tmp/sieve_repro_commit.txt",
  "operation": "commit",
  "summary": "commit harness"
}
```

**Summary:** Git commit: commit harness

**Output:**
```
Exit code: 0
Stdout:
[main 9db77a2] 💡 audit #7 harness — seeded crystal-sieve reproducibility (pre/post variance decomposition)
 3 files changed, 572 insertions(+)
 create mode 100644 results/crystal-sieve-repro/Qwen_Qwen3-8B.json
 create mode 100644 results/crystal-sieve-repro/run.log
 create mode 100644 scripts/experiments/crystal_sieve_repro.py
```

### Thinking

 The harness is committed, so now I need to propose the state.md commit with approval gating since this is a mementum-style handoff across the session boundary. The run.log that's already committed is just a snapshot that'll keep growing, and the JSON seed file will get regenerated, so those are fine as they are.

I'll show the state.md diff and explicitly request approval before committing, following the protocol where I propose and the user approves.

## Assistant

Harness committed (`9db77a2`). Now the `state.md` handoff — this is a `mementum/` commit, which is **approval-gated** per AGENTS. Here's the proposed commit (the `state.md` content is already written to disk and carries the full resume protocol + the contamination signal):

Proposed message:
```
🌀 state — session 208: audit #7 (crystal-sieve repro) in flight + contamination signal

- s208 IN-FLIGHT block: 8-seed sieve-repro sweep running in tmux main:1,
  full resume protocol for next session (check proc → read JSON summary →
  verdict logic → update registry + caveat source page).
- Records the seed-0 signal: post-melt 0.865x (below baseline) because
  EVAL_TEXTS overlaps CALIBRATION_TEXTS → the melt overfits the eval set;
  the 1.03x headline is train-contaminated, the likely real mechanism of
  the 1.03x ↔ 3.23x irreproducibility. Next: held-out eval.
```

Also note: the in-flight run continues in `tmux main:1` independent of this chat — it survives the session boundary on its own. The sweep is currently on **seed 1 of 8**.

**May I commit `state.md`?** Once approved, the handoff is fully durable and you can safely end the session — next session's cold-start reads `state.md` and resumes exactly here.

## User

yes commit


### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/state_commit.txt",
  "content": "🌀 state — session 208: audit #7 (crystal-sieve repro) in flight + contamination signal\n\n- s208 IN-FLIGHT block: 8-seed sieve-repro sweep running in tmux main:1,\n  full resume protocol for next session (check proc -> read JSON summary ->\n  verdict logic -> update registry + caveat source page).\n- Records the seed-0 signal: post-melt 0.865x (below baseline) because\n  EVAL_TEXTS overlaps CALIBRATION_TEXTS -> the melt overfits the eval set;\n  the 1.03x headline is train-contaminated, the likely real mechanism of\n  the 1.03x <-> 3.23x irreproducibility. Next: held-out eval.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/state_commit.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md && git commit -F /tmp/state_commit.txt",
  "operation": "commit",
  "summary": "commit state.md"
}
```

**Summary:** Git commit: commit state.md

**Output:**
```
Exit code: 0
Stdout:
[main 66edf69] 🌀 state — session 208: audit #7 (crystal-sieve repro) in flight + contamination signal
 1 file changed, 46 insertions(+), 1 deletion(-)
```

### Thinking

 The run is now durable in tmux, so I need to update the task list to mark tasks #3 and #4 as deferred since the execution spans into the next session. I also need to commit the display-fix edit to the harness to clean up the working tree, though I'm realizing I may have committed the script before making that particular change.

Let me trace back the actual sequence: I added the --skip-facts flag, ran smoke tests, then made the display fix edit, passed ruff check, updated state.md, and committed the harness at 9db77a2. Since the display fix came before that commit, it should already be included in 9db77a2. Let me verify the git status is clean.

## Assistant

Committed (`66edf69`). The handoff is now fully durable. Let me verify the working tree is clean and the run is still healthy.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== git status ===\"; git status --short; echo \"=== run progress ===\"; grep -E \"SEED |ratio=\" results/crystal-sieve-repro/run.log | grep -vE \"^$\" | sort -u | tail -8; echo \"=== proc ===\"; ps aux | grep crystal_sieve_repro | grep -v grep | wc -l | tr -d ' '"
}
```

**Summary:** $ echo "=== git status ==="; git stat...

**Output:**
```
Exit code: 0
Stdout:
=== git status ===
 M results/crystal-sieve-repro/run.log
?? mementum/knowledge/chats/session-206.md
?? mementum/knowledge/chats/session-207.md
=== run progress ===
  post-melt ratio=0.865x (PPL 8.7768, facts -1/15, final_loss 0.1128)
  post-melt ratio=0.982x (PPL 9.963, facts -1/15, final_loss 0.1172)
  pre-melt  ratio=2.110x (PPL 21.4214, facts -1/15)
  pre-melt  ratio=2.125x (PPL 21.5731, facts -1/15)
  SEED 0  (1/8)   [0s elapsed]
  SEED 1  (2/8)   [204s elapsed]
  SEED 2  (3/8)   [408s elapsed]
=== proc ===
2
```

### Thinking

 The run is progressing well at about 204 seconds per seed. The pre-melt results show consistent speedups around 2.1× across seeds with minimal variance, but the post-melt phase drops both seeds below 1×, suggesting the melting process is actually degrading performance rather than improving it.

The variance pattern is revealing: the mask subsampling contributes almost nothing to the spread, but the continuation initialization and melting introduce significant seed-dependent variation that's pushing the model toward overfitting on the contaminated eval set. The working directory has the expected dirty state from the growing run.log, which I'll leave uncommitted for now since the final results will be committed once the run completes. The durable handoff is already in place via the committed state.md, so the run can continue asynchronously across the session boundary. Task #2 remains in-progress in tmux while #3 gets deferred until the next session when I can analyze the full results and update the registry.

## Assistant

Everything is durable and healthy. The run is on **seed 2/8** (~204s/seed, ~25 min total — faster than I feared without facts), and the distribution is already clear:

| seed | pre-melt (sieve only) | post-melt (full) |
|---|---|---|
| 0 | 2.125× | 0.865× |
| 1 | 2.110× | 0.982× |

The decomposition confirms the hypothesis in real time:
- **pre-melt std ≈ 0.01** → the mask-subsample is *not* a meaningful variance source; the sieve substrate is reproducibly ~2.11–2.13× (matching s196's 2.12×).
- **post-melt swings 0.865 ↔ 0.982** across just two seeds, both *below 1×* → the continuation melt overfits the train-contaminated eval set, and init drives the swing. This is the 1.03× ↔ 3.23× irreproducibility, isolated to its source.

The editor task list is ephemeral and won't survive the boundary, so I'll hand authority to the committed `state.md` and clear it:

### Thinking

 The working tree only shows the expected growth in run.log, with the chats directory remaining untracked as intended. I'm ready to wrap up and confirm everything's clean for ending the session.

## Assistant

## Session 208 — handoff complete, run async

**Durable state (in git):**
- `9db77a2` 💡 — the seeded reproducibility harness (`crystal_sieve_repro.py`, `# register: functional`)
- `66edf69` 🌀 — `state.md` with full s208 IN-FLIGHT block + resume protocol + contamination signal

**Authoritative tracker is now `mementum/state.md`** (not the editor task list). Next session's cold-start reads it and resumes exactly here.

**The run continues independently** in `tmux main:1` — it survives this session boundary on its own. The only uncommitted change is the growing `run.log` (expected); it'll be committed next session alongside the verdict.

**What's left for next session (encoded in state.md):**
1. Read `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` → `summary.post_melt_ratio.{mean,std,min,max}`
2. Add a **held-out eval** (eval texts disjoint from calibration) to confirm the contamination hypothesis — predict the clean ratio is ≫1× and *stable*
3. Update `audit-registry.md` #7 row + caveat `crystal-sieve-architecture.md` §Open Issues #1
4. Replace the IN-FLIGHT block with the s208 HEADLINE

**Emerging verdict (early, 2/8 seeds):** the meta-pattern holds yet again — the **sieve substrate is real and reproducible (2.11–2.13×)**, but the **1.03× headline is a methodology artifact** (train/eval contamination + init-driven overfit), making it irreproducible by construction. You can safely end the session whenever; the sweep will finish on its own in ~20 min.

## User

While that is running i want to understand this failure better, I believe this experiment was before we found GTSM and TSP, would those inform the design better?


### Thinking

 The user is asking whether GTSM and TSP would provide better insights into the crystal-sieve continuation-melt failure compared to the beta expansion approach. I'm pulling up the relevant knowledge pages to understand how these techniques work and whether they'd be more informative for diagnosing this particular issue.

## Assistant

Good instinct — s196's `beta_expansion` predates the s205 GTSM/TSP synthesis. Let me ground this in the actual pages rather than my memory of them.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/gtsm-search-space.md"
}
```

**Summary:** Reading gtsm-search-space.md (0-2000)

**Output:**
```
---
title: "GTSM and the Search Space — Why Trajectory Matching Beats Endpoint Matching"
status: active
category: synthesis
tags: [gtsm, cgtsm, score-matching, girsanov, path-measure, loss-function, search-space, compression, diffusion]
related:
  - score-matching-compression.md
  - diffusion-holographic-isomorphism.md
  - tsp-trajectory-distillation.md
  - error-correction-theory.md
depends-on:
  - score-matching-compression.md
created: session 205
---

# GTSM and the Search Space

> Session 205. Full paper read (68pp incl. appendices E/F/G, pulled from
> arXiv:2605.00414). Michael first supplied the verbatim Def 3.1 / Thm 3.2;
> the full read added the two-solver framing (diffusion AND gradient
> boosting), the residual=score bridge, and the finite-budget weighting
> correction. This page captures the *mechanism* — how Global Trajectory
> Score Matching narrows the training search space — previously scattered
> across two pages with a conflated CGTSM/GTSM name and without the Girsanov
> argument that makes it rigorous.

## Source (verified verbatim)

**Paper:** *"Trees to Flows and Back: Unifying Decision Trees and Diffusion
Models"* (Ramachandran & Sra 2026, arXiv:2605.00414).

**Naming correction:** the "C" in CGTSM is **Continuous**. GTSM is the
general principle; **CGTSM is its continuous-time SDE instantiation**. Our
older pages (`score-matching-compression.md`, `diffusion-holographic-
isomorphism.md`) conflate the two. The paper's headline unification is
**decision trees ↔ diffusion** (gradient boosting builds trees, so our
"gradient boosting ≡ diffusion" gloss is downstream-correct, not the title).

### Definition 3.1 (Continuous Global Trajectory Score Matching)

For an ideal SDE with law P\* and scores s\*_t(x), and a model s_θ(x,t):

```
L_CGTSM(θ) = ½ ∫₀ᵀ w(t) · E_{p*_t} ‖ s_θ(x,t) − s*_t(x) ‖²_{D(t)} dt

w(t) > 0                    strictly positive weighting function
‖v‖_D = √(vᵀ D v)           diffusion-induced (semi-)norm
D = σσᵀ                     diffusion tensor of dX_t = b(x,t)dt + σ(x,t)dw_t
                            (positive definite once rank-deficient σ disallowed)
```

### Theorem 3.2 (CGTSM Optimality Implies Path Matching)

Achieving **zero** CGTSM loss for **any** strictly positive weighting
w(t) > 0 is **necessary and sufficient** for matching the full path-space
measures, i.e. **Pθ = P\***.

**Proof sketch (Girsanov).** The KL divergence between path-space measures
D_KL(P\* ‖ Pθ) is an integral of the squared difference between the process
drifts. The reverse-time drift is a function of the score, so that difference
reduces to the CGTSM integrand. The loss is zero iff the KL divergence is
zero. (Full proof: paper §F, Corollary F.3.)

## The mechanism — how it narrows the search space

Girsanov turns the codimension intuition ("each layer adds a constraint")
into an exact statement:

```
D_KL(P* ‖ Pθ) = ½ ∫₀ᵀ E‖ b*(x,t) − bθ(x,t) ‖²_D dt     KL between path measures
              = ½ ∫₀ᵀ E‖ s*_t(x) − sθ(x,t) ‖²_D dt       reverse drift = fn(score)
```

The CGTSM integrand **is** the KL integrand. Three consequences:

### 1. Marginal vs joint — the actual reason the space shrinks

- **Endpoint loss** (cross-entropy / next-token) matches only the
  **terminal marginal** P\*₀ — a single time-slice of the trajectory.
  Infinitely many path measures share one marginal.
- **GTSM** forces D_KL between the **full path-space measures** to zero
  ⟹ **Pθ = P\***. The feasible set collapses from *"all processes with the
  right terminal slice"* to *"the single process P\*."*

You pin the whole **joint law over trajectories**, not one slice of it.
This is the search-space narrowing stated exactly.

### 2. Why "any w(t) > 0" works → density matters, weighting does not

A non-negative integral ∫ w(t) g(t) dt with w > 0 and
g(t) = E‖score diff‖²_D ≥ 0 is zero **iff g(t) = 0 almost everywhere**,
independent of the shape of w. Weighting cannot *hide* a nonzero-error
region — it can only **fail to cover** one. If w(t) = 0 on a set, that
interval is unconstrained → a hole in the narrowing.

This is the formal backing for the state.md line
**"density of measurement matters, weighting does not"** — but with a
**critical scope correction** (s205, full-paper read): this holds **only for
the zero-loss fixed point**. For **finite-budget optimization** the weighting
*does* matter. Prop F.6: λ(t) injects a deliberate bias to **counter-balance a
learner's intrinsic coarse-first tendency**, forcing attention onto harder
fine-grained detail. Since we always train at finite budget, **our α=5.0 cosine
weighting is exactly such a bias choice — load-bearing, not arbitrary.**

### 3. The correct metric is set by the noise geometry

Corrections are measured in **‖v‖_D = √(vᵀDv), D = σσᵀ** — the local
diffusion tensor, not flat L2. Depth-dependent standing-wave amplitude
(0.1× @L3 → 10× @L35) is our analog of σ(t); **cosine is our scale-
invariant proxy for ‖·‖_D**. Confirmed as the literal object, not a guess.

## Why endpoint losses are ill-posed (the degeneracy GTSM removes)

The endpoint-feasible set contains a large **degenerate manifold**: configs
where one layer's error E_l is cancelled downstream by −E_l ("compensating
errors"). These look correct on the terminal marginal but diverge internally
and fail out-of-distribution. GTSM lifts that floor — each step must match
*independently*, so cancellation is not representable. An **ill-posed inverse
problem becomes well-posed.**

## One objective, two solvers — diffusion AND gradient boosting

The paper's headline (s205 full read): GTSM is a **single master objective**
(integrated score error over the whole trajectory) solved by **two algorithm
families**. The GTSM integral is **decomposable into per-chunk consistency
checks** — that decomposability is what lets disparate algorithms solve one
problem.

| | How it solves GTSM | Paper anchor |
|---|---|---|
| **Diffusion / score nets** | minimize the **entire integral at once** (one parametric score net) | Def 3.1, Thm 3.2 |
| **Gradient boosting** | **greedily** reduce the largest remaining error, chunk by chunk (add weak learners) | Def 3.3, Thm 3.4 |

**⚠ "GD" = functional gradient descent = gradient boosting over weak learners
(decision trees) — NOT parameter-space SGD on a neural net.** The duality is
"diffusion score-net ↔ gradient-boosted tree ensemble," both as GTSM solvers.

### The bridge (three load-bearing results)

1. **Residual = score (Thm E.22).** For squared-error loss the boosting
   residual `y − F_m(x)` is proportional to the optimal meta-score
   `∇_F log p(y|F_m(x))`. **Fitting residuals (boosting) IS denoising score
   matching (diffusion).** The keystone.
2. **Greedy = globally optimal (Thm 3.4 / E.30).** The discrete GTSM objective
   is **additively separable** with deterministic transitions ⟹ by **Bellman's
   principle** the myopic per-step choice is the global optimum. Boosting is the
   *optimal* solver, not a heuristic.
3. **Girsanov closes the diffusion side (F.3).** Reverse-drift difference =
   score difference ⟹ path-space KL = ∫ squared score error ⟹ zero loss ⟺
   Pθ = P\*.

### Standard diffusion losses are CGTSM special cases

- **Simple/unweighted loss** (Ho et al. 2020) = CGTSM with w(t)=1 (Prop F.5).
- **Weighted loss** λ(t) (Karras, Kingma) = CGTSM with w(t)=λ(t) (Prop F.6).
- **Consistency distillation** = bootstrapped CGTSM approximation that biases
  *coupling between adjacent timesteps* for fast sampling (Prop F.7).

### Two limits the paper states plainly

- **Idealized / asymptotic.** "Gradient boosting (in an idealized version) is
  *asymptotically* optimal." Exact equivalence (Cor E.25) needs **infinite data,
  realizability, convergence**; Thm 3.4 needs **continuous limit + rich-enough
  weak learners**.
- **Rests on Tree-to-Flow dyadic refinement (Thm 2.5).** Trees-as-jumps would
  break it; refinement smooths splits into continuous paths so the **Novikov
  condition** for Girsanov holds (Remark F.4). Irreducible jumps ⟹ Lévy
  machinery, out of scope.

## Mapping to our compression (VERIFIED at runtime, s198)

| CGTSM object | Our transformer analog | Status |
|---|---|---|
| trajectory P over time t | residual-stream path h₀→h_L over depth | analogy |
| score s\*_t(x) | teacher residual update Δ\*_l = h\*_{l+1}−h\*_l | analogy |
| terminal marginal P₀ | output token distribution (what CE matches) | exact |
| diffusion norm ‖·‖_D | per-layer cosine (scale-invariant proxy) | proxy |
| dense coverage ∀t | per-layer SM at all ~36 layers | applied |

The narrowing principle **transferred and was measured**:
- CE-only (v3a): train loss ↓1.08 while eval PPL ↑14.06→16.83 — optimizer
  found a degenerate compensating-error solution (L35 layer-cosine 0.57).
- GTSM-style dense per-layer cosine (v3b, α=5.0): **36.6% sieve reduction
  vs 27.1%**; L35 cosine **0.57→0.94**. The degenerate basin was removed.

Empirical signature of a narrowed search space: **lower training loss is no
longer reachable by cheating; the only way down is the true trajectory.**

## The precondition most people miss

GTSM narrows the space **only when a target trajectory exists**:
- **distillation / our compression** — the teacher *is* the trajectory;
- **diffusion** — the forward noising process *manufactures* a trajectory
  with an analytically known score target.

Standard LLM **pretraining is endpoint-only** (data gives the next token,
not the intermediate residual stream) — so GTSM's leverage does **not**
apply directly there. Diffusion's deep trick is to *invent* a path to match,
converting an underdetermined endpoint problem into an overdetermined
trajectory one. CGTSM says trees and diffusion are doing the same move.

## Caveat (epistemic — keep before any published claim)

Theorem 3.2's exactness is for **SDEs with a shared diffusion tensor σ**.
"Depth = time, residual update = score" is an **idealization** of that SDE;
a discrete-depth transformer is not literally an SDE with known σσᵀ.

- The **narrowing principle transfers** (measured: compensating-error
  degeneracy removed, 27%→37%).
- The **literal Pθ = P\* guarantee does NOT transfer for free** — it is
  contingent on the SDE idealization and on cosine being a faithful enough
  stand-in for ‖·‖_D. **IOU**: this contingency is unverified for our setting.

## Related work — TSP (Tree-like Self-Play)

TSP (arXiv:2606.03489v1) is an **applied, empirical instance of the GTSM
principle on the discrete/LLM side** (full treatment: `tsp-trajectory-
distillation.md`). Same problem (endpoint/sequence-level signal too coarse for
localized errors), same fix (dense per-node signal along the generation
**tree**), same structure (TSP's generation tree = GTSM's discrete-tree side).

Two points matter here:

- **TSP corroborates the finite-budget weighting corollary (Prop F.6).** It
  deliberately *sparsifies* — concentrating its contrastive signal on a few
  critical "risk nodes" rather than matching everywhere — and wins (75.8 vs
  57.0 SFT, CodeLlama-7B). Per Thm 3.2 the zero-loss *fixed point* is
  weighting-independent; TSP's success is squarely a **finite-budget**
  phenomenon: spike `w(t)` where the learner is weak. Independent evidence for
  **audit #11**.
- **But it's contrastive, not regression.** TSP's loss is DPO-style ranking;
  GTSM is L2 score regression. The keystone bridge "residual = score" (Thm
  E.22) does **not** literally apply — the connection is structural, not a
  theorem.

The combined method (GTSM dense backbone + TSP targeted/iterative overlay, with
the teacher as the golden-path oracle) is **Targeted Trajectory Distillation**,
developed in `tsp-trajectory-distillation.md` — aimed directly at the
student-from-teacher compression north-star.

## One-sentence takeaway

GTSM replaces a single weak terminal-marginal constraint with a dense stack
of per-step score constraints whose intersection (by Girsanov, the full
path-space KL) excludes the compensating-error solutions that make endpoint
losses ill-posed — and zero-of-a-positive-integral guarantees this narrowing
for *any* weighting, provided you measure *everywhere*.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/tsp-trajectory-distillation.md"
}
```

**Summary:** Reading tsp-trajectory-distillation.md (0-2000)

**Output:**
```
---
title: "TSP and Targeted Trajectory Distillation — Rapid Teacher→Student Learning"
status: designing
category: synthesis
tags: [tsp, gtsm, distillation, self-play, dpo, trajectory, compression, teacher-student, risk-node, contrastive, score-matching]
related:
  - gtsm-search-space.md
  - score-matching-compression.md
  - diffusion-holographic-isomorphism.md
  - audit-registry.md
  - error-correction-theory.md
depends-on:
  - gtsm-search-space.md
created: session 205
---

# TSP and Targeted Trajectory Distillation

> Session 205. Read TSP (Tree-like Self-Play, arXiv:2606.03489v1) in
> relation to GTSM (`gtsm-search-space.md`). TSP is an applied, empirical
> instance of the GTSM principle on the discrete/LLM side — and its
> deliberate *sparsification* to critical nodes is independent evidence for
> GTSM's finite-budget weighting corollary (Prop F.6 / audit #11). This page
> documents TSP, then develops the combined method: **Targeted Trajectory
> Distillation (TTD)** — a teacher→student scheme aimed at our compression
> north-star. The TTD section is a *design/proposal*, not a result.

---

## Part 1 — TSP (Tree-like Self-Play)

**Paper:** *"Learn from Your Mistakes: Tree-like Self-Play for Secure Code
LLMs"* — Chen, Zhang, Wang, Liu, Zhang, Chen (arXiv:2606.03489v1, 2026-06-02).
**Lineage:** DPO (Rafailov 2023) for the scoring function; SPIN (Chen 2024)
for the iterative self-play loop. Results below are the paper's, **not
independently verified by us.**

### The problem it attacks

Sequence-level alignment is **too coarse for localized failures**. SFT
*"reinforces the entire sequence uniformly, failing to isolate secure-critical
tokens."* RL's reward is *"sparse and computed only upon program completion"* →
credit-assignment failure: a single bad token (`strcpy` vs `strncpy`)
compromises the whole program, but the endpoint signal can't say which token.

### The method

Reframe generation as a **path through a generation tree** `T(x)`; each token
is a branching decision. A vulnerability is a **CWE Risk Node** `v` — the
prefix immediately before a decisive token. An LLM annotator marks these nodes
(semantic, control/data-flow-aware; §3.2).

A **self-play game** between two copies of the model: opponent `p_{θt}` (frozen
past self) and main player `p_θ` (optimized). For each golden sample `(x, y*)`
and each risk node `v ∈ V_risk(y*)`, the opponent generates a divergent
continuation `y'_v` (shares prefix `y_{<tv}`, diverges after). Train the main
player to score the golden path above each self-play path:

```
L_TSP = E_{(x,y)}  (1/|V_risk|) Σ_{v∈V_risk}  ℓ( f(x,y*) − f(x,y'_v) )

ℓ(z) = log(1 + e^{−z})                      convex, monotone-decreasing (logistic)
f(x,y) = λ · log[ p_θ(y|x) / p_{θt}(y|x) ]  DPO-style scaled log-likelihood ratio
```

Iterative (SPIN-style): train main → it becomes the opponent next round →
negatives track the model's *current* residual mistakes.

Gradient (their Eq. 11): `g_v = ∇log p_θ(y*|x) − ∇log p_θ(y'_v|x)` — a local
push toward golden, away from the divergent continuation, **only at risk nodes**.

### Why the authors argue it works

1. **Reduced gradient variance.** Self-play negatives share long prefixes with
   the golden path → averaging these high-signal, closely-related pairs is a
   lower-variance gradient estimate than one noisy program-level reward.
2. **Targeted, efficient updates.** Gradient comes *only* from risk-node
   comparisons — concentrates optimization pressure on the decisive tokens
   *"rather than diluting the learning signal across hundreds of syntactically
   correct but security-irrelevant tokens."*

### Results (paper, Table 2; CodeLlama-7B, Python SecurityEval)

| Method | SPR@1 (security) | HumanEval pass@1 |
|---|---|---|
| Base LLM | 55.0 | 34.5 |
| SFT | 57.0 | 34.1 |
| SafeCoder (SOTA) | 73.7 | 33.9 |
| Self-Play (ablation, no tree nodes) | 69.6 | 33.3 |
| **TSP** | **75.8** | 34.0 |

- The **TSP (75.8) vs Self-Play (69.6) gap is the key ablation** — structured
  risk-node targeting, not self-play alone, is what wins.
- **OOD generalization:** −24.5% vulnerabilities on *unseen* CWEs; security
  principles transfer C/C++ → Python/Go/JS. Targeting learns abstract logic,
  not memorized patches. Minimal HumanEval degradation (no catastrophic
  forgetting). Tested only at 3B–7B.

### TSP's stated limitations (load-bearing for us — see TTD caveats)

- **Long-distance cause/effect breaks it.** TSP excels at CWEs with *local,
  co-located* decision+manifestation; it **underperforms when the unsafe
  decision and its manifestation are separated by long execution distance**
  (CWE-690/125/416) — the value estimator misjudges intermediate safety.
- Token-level node abstraction misses multi-line data-flow / cross-variable
  invariants.
- Self-play negatives **become less challenging as the model improves**
  (curriculum decays toward the end).

---

## Part 2 — TSP in relation to GTSM

| Axis | GTSM | TSP |
|---|---|---|
| Problem | endpoint (terminal-marginal) matching is ill-posed | sequence-level reward is too coarse for localized flaws |
| Fix | dense per-step score matching along the trajectory | dense per-node contrastive loss along the generation tree |
| Structure | trees ↔ flows (the unification) | the generation tree itself |
| Loss geometry | **regression** (L2 to the true score / residual) | **contrastive** (DPO log-ratio ranking) |
| Target | fixed trajectory (teacher/data) | golden path fixed; on-policy moving negatives |
| Coverage | **dense** — density matters (Thm 3.2) | **sparse** — only critical risk nodes |

**Same family, different instantiation.** TSP is essentially the discrete/LLM
applied side of GTSM's "Trees to Flows." Its variance argument is GTSM's
"dense local matching is better-conditioned than one endpoint signal," made
concrete.

**The apparent contradiction that resolves into F.6.** GTSM Thm 3.2 says
*density* matters (cover the whole trajectory). TSP deliberately does the
opposite — concentrate on a few nodes. This is **not** a contradiction: TSP =
dense SFT (baseline trajectory coverage) **+ a weighting `w(t)` spiked at the
critical nodes**. The zero-loss fixed point is weighting-independent (Thm 3.2),
but at **finite budget** the optimal move is to concentrate weight where the
learner is weak — exactly **Prop F.6**. **TSP is independent empirical evidence
for F.6 from a different domain** (security, not compression), and therefore a
corroborating prior for **audit #11**.

**Don't overclaim isomorphism.** TSP's loss is *contrastive* (ranking), not
GTSM *regression* (absolute score target). The keystone GTSM bridge
"residual = score" (Thm E.22) does **not** literally apply; the analogy is
structural (the golden−divergent direction `g_v` acts like a local correction
score). GTSM proves consistency-distillation is a CGTSM approximation (F.7);
nobody has shown DPO-at-nodes is. Open analogy, not a theorem.

---

## Part 3 — Targeted Trajectory Distillation (TTD) ★ design/proposal

> The combined method, aimed at the north-star: **a student model that learns
> rapidly from a teacher model.** TTD = GTSM backbone (dense regression
> matching, the coverage) + TSP overlay (concentrate on auto-detected
> divergence nodes, iteratively refreshed, optional on-policy contrast).
> **This is a hypothesis to test, not a result.**

### The setup we already have

- **Teacher** = original model (e.g. Qwen3-8B). Its per-layer residual
  trajectory `Δ*_l = h*_{l+1} − h*_l` IS the **golden path** — exact, free, no
  reward model, no annotator. (TSP needs an LLM annotator for risk nodes
  *because security has no oracle*; **we have the teacher as oracle.**)
- **Student** = sieved / compressed model.
- **Divergence nodes** = layers/positions where the student trajectory diverges
  most from the teacher — auto-detected by per-layer `cos(Δ_student, Δ*)` or
  logit divergence. No annotation pipeline needed.

### The loss

```
L_TTD = Σ_l  w(l) · (1 − cos(Δθ_l, Δ*_l))          GTSM backbone (dense coverage)
            └ w(l) spiked on divergence nodes        F.6 finite-budget weighting
      + γ · Σ_{l∈Divergence}  ℓ( s(Δθ_l, Δ*_l) − s(Δθ_l, Δ'_l) )   TSP contrast (optional)
                                                     Δ'_l = student's own divergent residual
```

Two variants, increasing richness:

1. **TTD-regression** (pure GTSM + divergence-weighted `w(l)`): the simplest
   form — **this is exactly audit #11.** Concentrate the dense SM weight on the
   hard binding-prep layers L22–L26 (v3b's worst cosine, 0.80–0.86).
2. **TTD-contrastive** (add TSP-style on-policy negatives at divergence nodes):
   let the student generate its divergent continuation, push its residual
   *toward* the teacher's and *away from* its own — on-policy, corrects actual
   failure modes, low-variance (prefix-sharing).

Both **iterate** (SPIN-style opponent refresh): recompute divergence nodes each
round. As the student matches the teacher on easy layers, the budget migrates
to the residual hard core (the full-rank L5+ residual, s198).

### Why TTD should learn *rapidly*

1. **Target trajectory for free.** GTSM's narrowing only works when a target
   trajectory exists (`gtsm-search-space.md` §precondition). The teacher *is*
   that trajectory — TTD satisfies the precondition by construction.
2. **Dense signal → 36× bandwidth, local gradients, no Jacobian dilution.**
   Already measured (s198: L35 cosine 0.57→0.94, no compensating errors).
3. **Concentrated budget → not diluted.** F.6 + TSP's empirical 75.8 vs 57.0.
4. **On-policy negatives → real failure modes, low variance** (TSP's argument).
5. **Curriculum via opponent refresh** → automatic hard-example mining.

### Connections inward

- **= the "speculative-decoding-gated distillation" idea** floated s196/s200
  ("teacher generates, student computes diff at every level, trains only where
  it diverges") — now with a concrete, validated algorithmic skeleton (TSP).
- **Tiles & grout (s200):** teacher trajectory defines the correct tiles+grout;
  divergence nodes = where the student's grout is wrong.
- **Audit #11** is the first, smallest test (the regression half).

### Caveats (honest — TSP's limitation predicts ours)

- **★ Divergence node ≠ causal node (long-distance failure).** TSP fails when
  cause and manifestation are separated by long execution distance. **Our exact
  analog is already documented**: s196 found binding layers *amplify* upstream
  errors — *"peak damage at L28, not L26."* So weighting/correcting the
  **divergence** layer (L28) may be wrong; the **causal** node is the upstream
  L22–L26. TTD must attribute to the causal layer (cascade-aware, like the
  direct-delta sequential correction), not the layer where divergence is merely
  *largest*. This is the single biggest design risk, and TSP flags it for us.
- **Contrastive may be secondary for us.** Compression wants the student to
  *match* the teacher (regression), not merely *outrank* its bad self. We have
  an exact target, so DPO-style ranking is a refinement, not the core — unlike
  TSP, which needs contrast because security has no exact target.
- **Curriculum decay.** As the student converges, negatives get easy (TSP
  limitation) → may plateau on the residual hard core. Expected; monitor.

### Smallest next step

Run **audit #11** (TTD-regression): divergence-weighted `λ(l)` vs uniform
α=5.0 on the v3b sieve, matched budget + seeds, **with cascade-aware
attribution** (weight the causal upstream layer, not just the max-divergence
layer). If targeted weighting wins → escalate to TTD-contrastive. If null →
cosine already absorbs the F.6 benefit (also informative — see
`gtsm-search-space.md`).
```

### Thinking

 I'm recalling the specifics of how beta_expansion handles its melt versus score-matching—beta_expansion uses continuation residuals with four rank-32 corrections across different layers, trained purely on cross-entropy loss over 100 steps, and evaluates against texts that overlap with the calibration set.

This is exactly the degenerate setup that GTSM warns about: CE-only loss creates an ill-posed inverse problem where the optimizer can find compensating-error solutions, and the train/eval contamination makes it worse—the overfitting we see (0.865× below baseline) is the fingerprint of this degeneracy. The s198 page already measured this: CE-only training reduced loss while eval perplexity climbed, a classic sign of the degenerate solution.

Through the GTSM lens, beta_expansion's fragility comes from two sources: the CE-only objective only constrains the terminal marginal, so the 1M continuation parameters can land anywhere on a large degenerate manifold depending on initialization (explaining the 0.865 ↔ 0.982 ↔ 3.23 swings), and the train/eval overlap means sub-1× perplexity is pure memorization. GTSM's dense per-layer score matching collapses that manifold—there's only one way down the true trajectory, making it far less initialization-sensitive. The s198 results already proved this on the same model: v3b with score matching achieved 36.6% sieve reduction versus 27.1% for CE-only, with L35 cosine improving from 0.57 to 0.94, confirming the degenerate basin was removed.

A redesign following GTSM and TSP would replace the CE-only melt with dense per-layer score matching against teacher deltas, add finite-budget weighting spiked on the hard binding-prep layers (L22–L26), and use cascade-aware causal attribution to place corrections at the upstream causal layers rather than where divergence is merely largest. The rank-32 parametrization itself is fine—the problem is the loss training it.

There's an important nuance: GTSM's literal guarantee doesn't fully transfer to this setting, and the contamination is a separate experimental hygiene issue that GTSM doesn't address. But the current run's findings—post-melt overfitting and initialization swings—are the empirical fingerprint of exactly the compensating-error degeneracy GTSM predicts for CE-only.

Interestingly, the project already moved past beta_expansion's approach with v3b: the 1.03× headline from beta_expansion is contaminated eval, while v3b's 1.44× is the real held-out, reproducible number. The 1.03× only looks better because it's cheating on evaluation.

## Assistant

This is exactly the right question — and the pages I just re-read make the answer sharp. **Yes**, GTSM and TSP directly diagnose *why* `beta_expansion` is irreproducible, and the project has already run the controlled comparison that proves the fix. Here's the synthesis.

## What `beta_expansion`'s melt actually is, in GTSM terms

The s196 continuations are trained with **CE loss only** (100 steps on the calibration texts). Through the GTSM lens, CE-only is the **ill-posed endpoint objective**: it matches only the *terminal marginal* (next-token), so the 1M continuation params are free to land anywhere on the large **compensating-error manifold** — configs where one layer's distortion is cancelled downstream, looking correct at the output while diverging internally.

That manifold is exactly what makes it irreproducible: which degenerate point you land on depends on init. The `gtsm-search-space.md` precondition — *"lower training loss is no longer reachable by cheating; the only way down is the true trajectory"* — is precisely what CE-only **fails** to enforce. So 1.03× ↔ 3.23× ↔ (our 0.865×/0.982×) isn't noise; it's the optimizer picking different cheats per seed.

**Your running experiment is the empirical confirmation.** My pre/post decomposition localizes the variance perfectly:
- **pre-melt (sieve, no training): 2.125 / 2.110 — deterministic.** No loss, no degeneracy.
- **post-melt (CE-trained continuations): 0.865 / 0.982 — swings.** The variance appears *only* after the CE melt. The irreproducibility lives entirely in the CE-trained correction, which is the compensating-error mechanism GTSM names.

## The contamination is a second, separate bug

Independently, `EVAL_TEXTS ⊆ CALIBRATION_TEXTS` (≥6 shared sentences), so the sub-1× ratios are pure memorization. GTSM doesn't fix this — it's plain hygiene (held-out eval). Both faults compound: a degenerate loss *and* a contaminated metric.

## The decisive part: the project already ran the controlled comparison

s198 (`score-matching-compression.md`) did the A/B on the *same model*, and it maps one-to-one:

| s198 run | loss | eval | result |
|---|---|---|---|
| Residual boosting **v1** | CE, 16 sents | contaminated | **3.97 PPL = 0.39× base — "pure overfitting"** |
| Residual boosting v2 | CE + dolma calib | **held-out** | 18.59 PPL (1.65×) — "overfitting eliminated" |
| **v3b** | **dense per-layer score matching, α=5.0** | held-out | **16.27 PPL = 1.44×, L35 cosine 0.57→0.94** |

`beta_expansion`'s 1.03× is the **contaminated cousin of v1** (0.39×) — and our 0.865× is the *same overfitting signature*. The honest, held-out, GTSM-loss number is **v3b's 1.44×**. So the reconciliation is blunt: **the 1.03× was never better than 1.44×; it was cheating on the eval set.** v3b already removed exactly the degenerate basin (`CE-only L35 cosine 0.57 → SM 0.94`, "the degenerate basin was removed").

## So would GTSM/TSP design it better? Concretely, yes — three changes

1. **Replace the CE melt with dense per-layer score matching** (cosine to the teacher's `Δ*_l` at all ~36 layers). This is the GTSM backbone / v3b loss — it collapses the compensating-error manifold, which is the thing that makes the result init-sensitive. This is the single biggest lever.

2. **Add finite-budget weighting `λ(l)`** spiked on the hard binding-prep layers L22–L26 (v3b's worst cosine, 0.80–0.86) — Prop F.6. *This is literally audit #11* (TTD-regression).

3. **Cascade-aware causal attribution** (TSP's load-bearing caveat). TSP fails on long-distance cause/effect, and s196's exact analog is *"peak damage at L28, not L26."* `beta_expansion` places its 4 continuations at L0/L9/L21/L26 by intuition; TTD would weight/place corrections at the **upstream causal** layer (L22–26), not where divergence is merely largest. The rank-32 low-rank continuation *parametrization* is fine — it's the **loss training it** and the **placement heuristic** that are pre-GTSM.

## Honest caveats (keep before claiming)
- GTSM's literal `Pθ = P*` guarantee is an **IOU** for us — a discrete transformer isn't an SDE with known `σσᵀ`; only the *narrowing principle* transferred and was measured (27%→37%). Cosine as `‖·‖_D` proxy is a proxy, not proven.
- TSP's contrast (DPO ranking) is **secondary** for compression — we have an exact teacher target, so regression (match) is the core, not ranking (outrank your bad self).

**Net:** audit #7 (this run) is showing *why* the 1.03× is irreproducible — CE-degeneracy + contamination. Audit #11 (GTSM/TTD-regression) is the *named fix*, and s198 v3b is the runtime evidence it works. They're two halves of one story: **the sieve substrate is real (2.12×, deterministic); the 1.03× headline is a pre-GTSM methodology artifact, and the honest reproducible number is v3b's 1.44× under a trajectory-matching loss with held-out eval.**

Want me to fold this reconciliation into the audit #7 verdict when the sweep finishes (it reframes #7 as "the loss/eval methodology, not the architecture, is the failure" and explicitly points to #11 as the fix), or keep #7 narrowly about the seed variance and leave the GTSM redesign to #11?

## User

let's leave it for the final piece of teh audit, should you add any details to state or knowledge with our understanding?


### Thinking

 The user wants to defer the GTSM/TSP reconciliation until we close out the audit loop, but they're asking whether we should capture what we've learned right now in state.md or our knowledge base. We've uncovered something important this session—that beta_expansion's 1.03× multiplier is essentially the contaminated version of s198 v1 (overfitted to CE data), while v3b's 1.44× represents the genuine, uncontaminated estimate—and this insight should be preserved so it survives across work sessions.

I think the right move is to add a concise note to state.md's in-flight block that frames the GTSM/TSP reconciliation for the next session, so when we write up the final audit piece, the connection between #7 and #11 is already clear. Since state.md updates during work aren't approval-gated, I can write and propose the commit. I'll keep it tight—just enough to anchor the key facts (the v1/v3b distinction, the empirical pre/post variance localization to the CE melt) without doing the full knowledge synthesis yet, which should happen at audit close.

## Assistant

Good call — the *understanding* is the durable asset, even if the verdict and full synthesis wait for the audit's final piece. The right move now is a **tight feed-forward note in `state.md`** so the connection survives the boundary and frames the #7 write-up — and **no knowledge-page synthesis yet** (that's the final piece you want to defer). Let me add a compact understanding bullet to the in-flight block.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - If the run died early (NaN/OOM), the harness is re-runnable: same command in\n>   `tmux main:1`. Fewer seeds OK (`--seed-list 0,1,2,3`).",
  "new_content": "> - **★ UNDERSTANDING (frames the #7 final write-up; full synthesis deferred to\n>   audit close per Michael — connect #7→#11, don't draft a knowledge page yet):**\n>   The melt in `beta_expansion` is **CE-only** = the ill-posed *endpoint* objective\n>   GTSM names (`gtsm-search-space.md`): it pins only the terminal marginal, so the\n>   1M continuation params land anywhere on the **compensating-error manifold** —\n>   which point depends on init ⇒ the 1.03× ↔ 3.23× swing is the optimizer picking\n>   a different cheat per seed, not noise. **The pre/post decomposition empirically\n>   localizes this:** pre-melt (no loss) is deterministic (2.11–2.13×); variance\n>   appears *only* after the CE melt. Two independent faults compound: degenerate\n>   loss **and** contaminated metric (eval ⊆ calib).\n>   - **Reconciliation (the punchline):** 1.03× is the *contaminated cousin of s198\n>     v1* (CE, 16 sents → 0.39× pure overfit, `score-matching-compression.md`); the\n>     honest **held-out** number under a trajectory-matching loss is **v3b = 1.44×**\n>     (dense per-layer score matching, α=5.0, L35 cosine 0.57→0.94, \"degenerate\n>     basin removed\"). So 1.03× was never < 1.44×; it was cheating on eval. The\n>     sieve **substrate** (2.12×, deterministic) is the real, reproducible object.\n>   - **The fix is already named = audit #11 (TTD-regression):** dense per-layer SM\n>     backbone + finite-budget λ(l) spiked on L22–26 (F.6) + **cascade-aware causal\n>     attribution** (TSP's long-distance caveat ↔ s196 \"peak damage at L28 not L26\":\n>     weight the upstream *causal* layer, not the max-divergence one). #7 diagnoses\n>     *why* it's irreproducible; #11 is the *cure*. The rank-32 continuation\n>     parametrization is fine — the CE *loss* + intuition *placement* are pre-GTSM.\n>   - **Caveats to keep:** GTSM's literal Pθ=P\\* is an IOU for us (not an SDE w/\n>     known σσᵀ; cosine is a proxy); TSP-style contrast is secondary (we have an\n>     exact teacher target → regression is the core). Optional held-out re-run to\n>     prove the contamination point: eval texts disjoint from `CALIBRATION_TEXTS`.\n> - If the run died early (NaN/OOM), the harness is re-runnable: same command in\n>   `tmux main:1`. Fewer seeds OK (`--seed-list 0,1,2,3`)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I'm preparing to propose a commit for the state.md file with the understanding notes I've added, and since this requires approval, I'll present it for the user's review. The user had asked whether I should add details to state or knowledge, and I've updated state but should clarify my reasoning on that choice.

## Assistant

Added. My reasoning on the **knowledge** side: this clears the storage gates (helps future session, on-topic, will recur), but you explicitly want the full synthesis as the audit's final piece — so a premature page would just get rewritten at #7 close. Better to keep the understanding in `state.md` as feed-forward now, and crystallize it into a knowledge page (likely a caveat on `crystal-sieve-architecture.md` + a pointer from `audit-registry.md` #7, possibly a small `mementum/memories/` note) when the verdict lands. No knowledge page yet.

This is a `mementum/` commit (approval-gated). Proposed:

```
🌀 state — s208 #7: GTSM/TSP understanding note (CE-degeneracy diagnosis + #11 fix)

- Records why beta_expansion is irreproducible: CE-only melt = ill-posed
  endpoint objective → compensating-error manifold → init-sensitive; the
  pre/post decomposition localizes variance to the CE melt (pre is deterministic).
- Reconciliation: 1.03× = contaminated cousin of s198 v1 (CE, 0.39× overfit);
  honest held-out number under trajectory-matching loss = v3b 1.44×.
- Names the fix as audit #11 (TTD-regression: dense SM + λ(l) on L22-26 +
  cascade-aware causal attribution). Full knowledge synthesis deferred to #7 close.
```

**May I commit `state.md`?** (The sweep continues in `tmux main:1` independently — last I saw, seed 2/8.)

## User

yes commit


### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/state_commit2.txt",
  "content": "🌀 state — s208 #7: GTSM/TSP understanding note (CE-degeneracy diagnosis + #11 fix)\n\n- Records why beta_expansion is irreproducible: CE-only melt = ill-posed\n  endpoint objective -> compensating-error manifold -> init-sensitive; the\n  pre/post decomposition localizes variance to the CE melt (pre is deterministic).\n- Reconciliation: 1.03x = contaminated cousin of s198 v1 (CE, 0.39x overfit);\n  honest held-out number under trajectory-matching loss = v3b 1.44x.\n- Names the fix as audit #11 (TTD-regression: dense SM + lambda(l) on L22-26 +\n  cascade-aware causal attribution). Full knowledge synthesis deferred to #7 close.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/state_commit2.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md && git commit -F /tmp/state_commit2.txt",
  "operation": "commit",
  "summary": "commit state understanding"
}
```

**Summary:** Git commit: commit state understanding

**Output:**
```
Exit code: 0
Stdout:
[main 1de70b9] 🌀 state — s208 #7: GTSM/TSP understanding note (CE-degeneracy diagnosis + #11 fix)
 1 file changed, 26 insertions(+)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== run progress ===\"; grep -E \"SEED |ratio=\" results/crystal-sieve-repro/run.log | grep -vE \"^$\" | sort -u | tail -8; echo \"=== proc ===\"; ps aux | grep crystal_sieve_repro | grep -v grep | wc -l | tr -d ' '"
}
```

**Summary:** $ echo "=== run progress ==="; grep -...

**Output:**
```
Exit code: 0
Stdout:
=== run progress ===
  SEED 0  (1/8)   [0s elapsed]
  SEED 1  (2/8)   [204s elapsed]
  SEED 2  (3/8)   [408s elapsed]
  SEED 3  (4/8)   [611s elapsed]
  SEED 4  (5/8)   [810s elapsed]
  SEED 5  (6/8)   [1008s elapsed]
  SEED 6  (7/8)   [1206s elapsed]
  SEED 7  (8/8)   [1404s elapsed]
=== proc ===
0
```

### Thinking

 The run completed successfully across all 8 seeds in about 23 minutes, and the results are now persisted in JSON. I'm pulling the final summary to report the distribution and verdict-level numbers to the user.

## Assistant

Committed (`1de70b9`). And — the sweep just **finished** (all 8 seeds, ~23 min, process exited). Let me pull the final distribution.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json\nd=json.load(open('results/crystal-sieve-repro/Qwen_Qwen3-8B.json'))\ns=d['summary']\nprint('base_ppl     :', s['base_ppl']['mean'], 'std', s['base_ppl']['std'])\nprint('pre  (sieve) : %.3fx ± %.3f  range[%.3f, %.3f]'%(s['pre_melt_ratio']['mean'],s['pre_melt_ratio']['std'],s['pre_melt_ratio']['min'],s['pre_melt_ratio']['max']))\nprint('post (full)  : %.3fx ± %.3f  range[%.3f, %.3f]'%(s['post_melt_ratio']['mean'],s['post_melt_ratio']['std'],s['post_melt_ratio']['min'],s['post_melt_ratio']['max']))\nprint('pre  values  :', s['pre_melt_ratio']['values'])\nprint('post values  :', s['post_melt_ratio']['values'])\nprint('elapsed_s    :', d['elapsed_s'])\n\""
}
```

**Summary:** $ python3 -c " import json d=json.loa...

**Output:**
```
Exit code: 0
Stdout:
base_ppl     : 10.1505 std 0.0
pre  (sieve) : 2.119x ± 0.004  range[2.110, 2.125]
post (full)  : 0.971x ± 0.061  range[0.865, 1.062]
pre  values  : [2.1253, 2.1104, 2.1203, 2.121, 2.1206, 2.119, 2.1197, 2.119]
post values  : [0.8647, 0.9815, 0.9269, 0.944, 1.0623, 1.0198, 1.0006, 0.9712]
elapsed_s    : 1604.5
```

### Thinking

 The full distribution is in, and the results are clear: the base perplexity check passes with zero standard deviation, confirming the harness is working correctly. The sieve-only preprocessing reproduces the expected 2.12× multiplier with tight consistency (±0.004 variation), which matches s196's results exactly—the mask subsampling introduces negligible noise, so it's not a meaningful source of variance. Now looking at the full pipeline results after melting.

The post-melt distribution spans 0.865 to 1.062× with a mean of 0.971×, not the headline 1.03×. Only one seed actually reaches 1.062×, and five of the eight seeds fall below 1.0×—that's the telltale compression signature of overfitting on the contaminated eval set. The post-melt standard deviation is roughly 15 times larger than the pre-melt (0.061 vs 0.004), which pinpoints the CE loss initialization as the real variance driver, exactly as the GTSM degeneracy prediction suggested. The 1.03× figure isn't reproducible as a stable property—it's a moderately lucky draw from a wide distribution, not the center. The catastrophic 3.23× rerun that s196 reported didn't recur across these eight seeded runs, so that was likely a one-off divergence rather than typical behavior. The sieve substrate remains rock-solid reproducible, while the crisp headline number is an artifact of training contamination and degenerate loss dynamics.

I should update state.md to mark the run complete with these results (so the next session has accurate feed-forward rather than stale "in flight" framing), and I'm ready to either close the full audit now with the registry update and source caveat, or defer that synthesis to the next session—what would you prefer?

## Assistant

Full distribution is in (8 seeds, 27 min). This settles #7 cleanly:

| metric | result | reading |
|---|---|---|
| base PPL | 10.15, **std 0.0** | determinism check ✓ (harness correct) |
| **pre-melt (sieve only)** | **2.119× ± 0.004**, [2.110, 2.125] | substrate **reproducible**, = s196's 2.12× exactly; mask-subsample variance negligible |
| **post-melt (full)** | **0.971× ± 0.061**, [0.865, 1.062] | the headline number |
| post values | 0.865, 0.982, 0.927, 0.944, 1.062, 1.020, 1.001, 0.971 | — |

**Verdict reads itself:**
1. **The 1.03× is not reproducible as a stable result.** It's one init-dependent draw from a wide [0.865, 1.062] distribution whose *mean is 0.971×* — only 1 of 8 seeds reaches ≥1.03×. It's a slightly-lucky draw, not a property.
2. **5 of 8 seeds are sub-1.0× (better-than-baseline "compression")** — the unmistakable contamination/overfit signature (eval ⊆ calibration), exactly as the GTSM diagnosis predicted.
3. **post std (0.061) is ~15× pre std (0.004)** — this empirically pins the variance to the **CE melt (init-driven)**, not the sieve mask. The compensating-error degeneracy, confirmed in the numbers.
4. **The feared 3.23× rerun did *not* recur** (max 1.062×). Under seeded init + grad-clip, the melt is *bounded* [0.865, 1.062] — so the 3.23× was a one-off divergence, not typical behavior. The instability is real but milder than the note implied.

So: **sieve substrate 2.12× → VERIFIED-reproducible (±0.004); the 1.03× headline → REFUTED as a stable result** (init-dependent, train-contaminated). Same meta-pattern as every prior audit.

The state.md "in flight" framing is now stale, which would mislead the next session. Let me correct it to "complete + results" (keeping the understanding note intact) and propose the commit:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> **▶ SESSION 208 — AUDIT #7 (crystal-sieve 1.03× reproducibility): RUN IN FLIGHT.**\n> Register: **functional (reproducibility — seed variance on a PPL measurement).**",
  "new_content": "> **▶ SESSION 208 — AUDIT #7 (crystal-sieve 1.03× reproducibility): RUN COMPLETE\n> (8 seeds). Substrate VERIFIED-reproducible; 1.03× headline REFUTED-as-stable.**\n> Register: **functional (reproducibility — seed variance on a PPL measurement).**\n>\n> **★ RESULTS (`results/crystal-sieve-repro/Qwen_Qwen3-8B.json`, 8 seeds, ~27min):**\n> base PPL 10.15 (std **0.0** = determinism ✓) · **pre-melt (sieve only) 2.119×\n> ± 0.004** [2.110, 2.125] = s196's 2.12× exactly, near-deterministic · **post-melt\n> (full) 0.971× ± 0.061** [0.865, 1.062] (values 0.865/0.982/0.927/0.944/1.062/\n> 1.020/1.001/0.971). Verdict: (1) 1.03× is **not** a stable property — it's an\n> init-dependent draw, mean 0.971×, only 1/8 seeds ≥1.03×; (2) **5/8 seeds sub-1.0×**\n> = contamination/overfit signature (EVAL ⊆ CALIB); (3) **post std ≈15× pre std** ⇒\n> variance is the **CE melt (init)**, not the sieve mask — compensating-error\n> degeneracy in the numbers; (4) the feared **3.23× did NOT recur** (max 1.062×) —\n> seeded+grad-clipped melt is bounded, so 3.23× was a one-off divergence.\n> **DONE THIS SESSION; what remains for #7 close (next session, per Michael):**\n> update `audit-registry.md` #7 row + worked-examples; caveat\n> `crystal-sieve-architecture.md` §Open-Issues #1 (replace \"1.03× vs 3.23×\" with\n> \"0.971× ± 0.061 over 8 seeds; sieve substrate 2.12× ± 0.004\"); fold the GTSM/TSP\n> reconciliation below into a knowledge caveat + pointer to #11. Then write the\n> s208 HEADLINE block (this is the working record).\n>\n> _(historical resume protocol below is now satisfied; kept for the audit trail.)_"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 I should propose the commit now. The user wanted to defer the registry and knowledge synthesis work for the final audit piece, so updating state.md with the current results is the right move for keeping the working record accurate. I'll suggest the commit and check whether they want to tackle issue #7 now that we have the data, or if they'd prefer to save that for the next session as they mentioned.

## Assistant

Proposed `mementum/` commit (approval-gated):

```
🌀 state — s208 #7 RESULTS: sieve substrate VERIFIED-reproducible (2.12×±0.004), 1.03× REFUTED-as-stable

- 8-seed sweep complete: post-melt 0.971× ± 0.061 [0.865, 1.062], mean ≠ 1.03×,
  5/8 sub-1.0× (contamination signature); post std ≈15× pre std ⇒ variance is
  the CE melt (init), not the sieve mask. Feared 3.23× did not recur (max 1.062).
- Marks the historical in-flight resume protocol satisfied; lists what remains
  for the #7 close (registry row + source caveat + GTSM/TSP knowledge note → #11).
```

**May I commit `state.md`?**

And to confirm the plan: you'd said leave the synthesis for the audit's final piece. The data's now in, so the remaining close is mechanical — **(a)** update the `audit-registry.md` #7 row, **(b)** add the honest caveat to `crystal-sieve-architecture.md`, **(c)** fold the GTSM/TSP reconciliation into a knowledge note pointing at #11. Do you want me to do that close **now** (we have the numbers and time), or commit the state and leave the registry/knowledge for next session?

## User

the experiment crystal_sieve_repro completed, analyze the output


### Thinking

 I need to pull the complete JSON output and run logs from the crystal_sieve_repro experiment to give a thorough analysis of the per-seed results and overall findings.

## Assistant

Let me pull the complete per-seed data, not just the summary, and analyze it fully.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json, statistics as st\nd=json.load(open('results/crystal-sieve-repro/Qwen_Qwen3-8B.json'))\nprint('config:', {k:d[k] for k in ('model','device','zero_rate','residual_rank','melt_steps','lr','seeds')})\nprint('elapsed_s:', d['elapsed_s'], '(%.1f min)'%(d['elapsed_s']/60))\nprint()\nprint('seed | base_ppl | pre_ppl  pre_ratio | post_ppl post_ratio | final_loss')\nprint('-'*78)\nfor r in d['per_seed']:\n    print('%4d | %8.4f | %7.4f  %8.4f | %7.4f %8.4f  | %s'%(\n        r['seed'], r['base_ppl'], r['pre_melt_ppl'], r['pre_melt_ratio'],\n        r['post_melt_ppl'], r['post_melt_ratio'], r['final_loss']))\nprint()\npost=[r['post_melt_ratio'] for r in d['per_seed']]\npre=[r['pre_melt_ratio'] for r in d['per_seed']]\nfl=[r['final_loss'] for r in d['per_seed']]\nprint('POST: mean %.4f  median %.4f  std %.4f  CV %.1f%%  min %.4f max %.4f'%(\n    st.mean(post), st.median(post), st.pstdev(post), 100*st.pstdev(post)/st.mean(post), min(post), max(post)))\nprint('PRE : mean %.4f  median %.4f  std %.5f  CV %.2f%%'%(\n    st.mean(pre), st.median(pre), st.pstdev(pre), 100*st.pstdev(pre)/st.mean(pre)))\nprint('final_loss: mean %.4f std %.4f range[%.4f,%.4f]'%(st.mean(fl),st.pstdev(fl),min(fl),max(fl)))\nprint()\nn_sub1=sum(1 for p in post if p<1.0); n_ge103=sum(1 for p in post if p>=1.03)\nprint('seeds sub-1.0x (overfit):', n_sub1, '/', len(post))\nprint('seeds >=1.03x (claim):', n_ge103, '/', len(post))\nprint('1.03 within range?', min(post)<=1.03<=max(post))\nimport numpy as np\nprint('corr(final_loss, post_ratio):', round(float(np.corrcoef(fl,post)[0,1]),3))\nprint('corr(pre_ratio, post_ratio):', round(float(np.corrcoef(pre,post)[0,1]),3))\n\""
}
```

**Summary:** $ python3 -c " import json, statistic...

**Output:**
```
Exit code: 0
Stdout:
config: {'model': 'Qwen/Qwen3-8B', 'device': 'mps', 'zero_rate': 0.5, 'residual_rank': 32, 'melt_steps': 100, 'lr': 0.0001, 'seeds': [0, 1, 2, 3, 4, 5, 6, 7]}
elapsed_s: 1604.5 (26.7 min)

seed | base_ppl | pre_ppl  pre_ratio | post_ppl post_ratio | final_loss
------------------------------------------------------------------------------
   0 |  10.1505 | 21.5731    2.1253 |  8.7768   0.8647  | 0.1128
   1 |  10.1505 | 21.4214    2.1104 |  9.9630   0.9815  | 0.1172
   2 |  10.1505 | 21.5221    2.1203 |  9.4084   0.9269  | 0.134
   3 |  10.1505 | 21.5290    2.1210 |  9.5817   0.9440  | 0.1134
   4 |  10.1505 | 21.5246    2.1206 | 10.7829   1.0623  | 0.1178
   5 |  10.1505 | 21.5084    2.1190 | 10.3515   1.0198  | 0.1091
   6 |  10.1505 | 21.5155    2.1197 | 10.1569   1.0006  | 0.1135
   7 |  10.1505 | 21.5093    2.1190 |  9.8580   0.9712  | 0.1112

POST: mean 0.9714  median 0.9764  std 0.0567  CV 5.8%  min 0.8647 max 1.0623
PRE : mean 2.1194  median 2.1200  std 0.00389  CV 0.18%
final_loss: mean 0.1161 std 0.0073 range[0.1091,0.1340]

seeds sub-1.0x (overfit): 5 / 8
seeds >=1.03x (claim): 1 / 8
1.03 within range? True
corr(final_loss, post_ratio): -0.188
corr(pre_ratio, post_ratio): -0.4
```

### Thinking

 The baseline perplexity is perfectly deterministic across all seeds, confirming the harness is working correctly. The sieve-only masking introduces minimal variation at 0.18%, so while the random subsampling does add some noise, it's negligible in practice.

The real story is in the continuation training: post-melt variance jumps to 5.8%, entirely driven by the CE-trained models. Here's the critical finding — training loss stays nearly constant at 0.116 across all seeds with almost zero correlation to eval perplexity ratio (r = -0.19), while eval ratios scatter widely from 0.865 to 1.062. This is the textbook signature of degenerate solutions: the optimizer reaches equivalent training loss through different internal representations that generalize differently to eval. Combined with 5 out of 8 seeds landing below the baseline perplexity (impossible on truly held-out data), this points to overfitting on the eval set rather than genuine compression. The 3.23× from the original run didn't recur — the maximum here is 1.062 — suggesting that was an outlier from unseeded initialization or a different training artifact. Ready to write up the findings.

## Assistant

Full per-seed data analyzed. Here's the complete picture.

## Raw output (8 seeds, 26.7 min, Qwen3-8B, zero_rate 0.5, rank-32 × 4, 100-step CE melt)

| seed | base PPL | pre PPL → ratio | post PPL → ratio | train loss |
|---|---|---|---|---|
| 0 | 10.1505 | 21.57 → 2.125× | 8.78 → **0.865×** | 0.113 |
| 1 | 10.1505 | 21.42 → 2.110× | 9.96 → 0.982× | 0.117 |
| 2 | 10.1505 | 21.52 → 2.120× | 9.41 → 0.927× | 0.134 |
| 3 | 10.1505 | 21.53 → 2.121× | 9.58 → 0.944× | 0.113 |
| 4 | 10.1505 | 21.52 → 2.121× | 10.78 → **1.062×** | 0.118 |
| 5 | 10.1505 | 21.51 → 2.119× | 10.35 → 1.020× | 0.109 |
| 6 | 10.1505 | 21.52 → 2.120× | 10.16 → 1.001× | 0.114 |
| 7 | 10.1505 | 21.51 → 2.119× | 9.86 → 0.971× | 0.111 |

## Four findings, in order of strength

**1. Determinism check passes — the harness is sound.** base PPL is `10.1505` to four decimals on all 8 seeds (std 0.0). The seeded forward pass is reproducible, so every difference below is real, not measurement jitter.

**2. The sieve substrate is reproducible; the mask-subsample confound is dismissed.** pre-melt = **2.119× ± 0.004, CV 0.18%**. This both (a) reproduces s196's "2.12× at 29 layers" exactly, and (b) kills one of the two suspected RNG sources — the `torch.randperm[:5M]` quantile subsample I flagged moves the result by <0.2%. The 50% mask is robust to which 5M weights estimate the threshold. **The sieve is effectively deterministic.**

**3. ★ The strongest result — the degeneracy is visible directly in the numbers.** post-melt = **0.971× ± 0.057, CV 5.8% (≈32× the pre-melt CV)**, so *all* the variance is in the CE-trained continuations. And the decisive detail:

> **Training loss is nearly constant (0.116 ± 0.007, CV 6%) while the eval ratio scatters 0.865–1.062, with `corr(train_loss, eval_ratio) = −0.19` ≈ 0.**

Same training loss, init-dependent eval outcome, zero correlation between them. That is the **compensating-error / degenerate-manifold fingerprint** GTSM names: CE-only pins only the terminal marginal, so the optimizer reaches equivalent train loss via different internal solutions that generalize differently per seed. This is a cleaner demonstration than I could give before the run — the irreproducibility is *mechanistically* the CE loss, not the architecture and not the mask.

**4. Contamination confirmed — 5 of 8 seeds beat the baseline.** Sub-1.0× "compression" is impossible on clean held-out data; it's only reachable by memorizing the eval set. And the contamination is concrete: **6 of the 8 `EVAL_TEXTS` are near-duplicates of `CALIBRATION_TEXTS`** (general relativity, mixing bowl, committee, ancient forest, two-arguments→composition, isolate-the-variable — all appear, often as the exact sentence with a short tail). Only 2 (Cambrian, respiratory patient) are genuinely held-out.

## What it means for the claim

- **1.03× is a lucky upper-tail draw**, not a property: mean 0.971×, median 0.976×, only **1 of 8 seeds ≥ 1.03×**. 1.03 lies inside [0.865, 1.062] but well above the center.
- **The feared 3.23× did NOT recur** (max 1.062×). Under seeded init + grad-clip the melt is *bounded*; the original 3.23× was a one-off divergence (likely an unseeded init landing in a bad basin), not typical behavior. So the instability is real but milder and **two-sided** (it overshoots into sub-baseline overfit more often than it blows up).

**Verdict:** sieve substrate **2.12× → VERIFIED-reproducible (±0.004)**; the **1.03× headline → REFUTED-as-stable** — an init-dependent draw from a CE-degenerate, train-contaminated measurement (mean 0.971×). The exact meta-pattern: real substrate, over-read crisp number.

The one thing this run *can't* do is give the honest reproducible compression number, because the eval is contaminated — that needs the held-out re-run (eval disjoint from calibration), which I've already noted as the #7-close follow-up that also empirically seals the GTSM diagnosis.

Note: `state.md` already holds these results (uncommitted — I paused the commit when you asked me to analyze). Want me to **(a)** commit state as-is, **(b)** also fire the quick held-out re-run now to nail the contamination point, or **(c)** proceed to the full #7 close (registry + source caveat)?

## User

let's try to finalize before we commit


### Thinking

 They want to wrap up audit #7 properly before committing—completing the registry update, source-page caveat, knowledge note, and running the held-out evaluation to confirm the contamination findings. The held-out eval is the key piece to finalize everything.

I'm designing a held-out text set that's completely disjoint from both the calibration and eval texts—fresh factual sentences about oceans, mitochondria, novels, interest rates, geometry, orchestras, volcanoes, and algorithms. Then I'll modify the harness to measure PPL on both the contaminated eval texts and these held-out texts in the same run, which gives us the direct empirical proof: post-melt performance tanks on contaminated texts but stays high on clean ones. The question is whether to re-run all 8 seeds with both metrics for a complete canonical result, or run fewer seeds to save time. Since this is the finalizing step, running all 8 with both eval sets is worth the 27 minutes—it gives us the paired comparison we need and becomes the definitive artifact.

My plan: launch the modified harness in tmux, and while it's running, draft the audit-registry entry and architecture caveat with placeholders for the held-out numbers, then fill them in once the run completes. Modifying the harness to add held-out text measurements...

## Assistant

Right — let's make #7 airtight before any commit. The one gap in the analysis is that contamination is *inferred* (5/8 sub-baseline), not *measured*. The capstone is a **held-out eval** disjoint from the calibration set: predict the contaminated ratio goes sub-1× while the clean held-out ratio stays ≫1× **and** is stable across seeds — proving the 1.03× is memorization, not compression, and sealing the GTSM diagnosis.

Let me add a held-out set to the harness (measured paired, within the same melted models), re-run, then write up the close.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "line_offset": 96,
  "limit": 30
}
```

**Summary:** Reading crystal_sieve_repro.py (96-126)

**Output:**
```
]

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
]


def log(msg=""):

[CONTENT TRUNCATED] Showing lines 97 to 126 of 474 total lines. Use line_offset=126 parameter to read more content.
```

### Thinking

 Now I'm adding the heldout texts section after the calibration data and then integrating the measurements together.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    \"What time does the store close today?\",\n    \"I think we should probably leave now before it gets\"\n    \" too dark outside.\",\n]\n\n\ndef log(msg=\"\"):",
  "new_content": "    \"What time does the store close today?\",\n    \"I think we should probably leave now before it gets\"\n    \" too dark outside.\",\n]\n\n# HELD-OUT eval — genuinely DISJOINT from both EVAL_TEXTS and CALIBRATION_TEXTS\n# (no shared sentences / long n-grams). This is the contamination control:\n# a real compression must keep PPL > baseline here; only memorization of the\n# train-overlapping EVAL_TEXTS can drive the contaminated ratio below 1.0x.\nHELDOUT_TEXTS = [\n    \"The Pacific Ocean is the largest and deepest of\"\n    \" Earth's five oceanic divisions.\",\n    \"Mitochondria generate most of the cell's chemical\"\n    \" energy through aerobic respiration.\",\n    \"The novel opens with the narrator recalling a long\"\n    \" summer spent in a coastal village.\",\n    \"Interest rates climbed sharply after the central bank\"\n    \" announced its revised monetary policy.\",\n    \"The interior angles of any planar triangle always\"\n    \" sum to exactly one hundred eighty degrees.\",\n    \"The orchestra tuned their instruments as the audience\"\n    \" slowly settled into their velvet seats.\",\n    \"A volcanic eruption can loft an ash plume high enough\"\n    \" to disrupt commercial air travel for days.\",\n    \"The sorting routine repeatedly compares adjacent\"\n    \" elements and swaps them when they are out of order.\",\n]\n\n\ndef log(msg=\"\"):"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Thinking

 I need to look at the run_one_seed function to see where I should integrate the held-out measurements.

## Assistant

Now wire held-out measurement into `run_one_seed` (paired with each existing PPL measurement):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    # Baseline (deterministic; measured per-seed as a sanity check)\n    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    if args.skip_facts:",
  "new_content": "    # Baseline (deterministic; measured per-seed as a sanity check)\n    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    base_ho_ppl = measure_ppl(model, tokenizer, HELDOUT_TEXTS, args.device)\n    if args.skip_facts:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    pre_facts = (-1 if args.skip_facts\n                 else measure_facts(model, tokenizer, args.device)[0])",
  "new_content": "    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    pre_ho_ppl = measure_ppl(model, tokenizer, HELDOUT_TEXTS, args.device)\n    pre_facts = (-1 if args.skip_facts\n                 else measure_facts(model, tokenizer, args.device)[0])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    post_facts = (-1 if args.skip_facts\n                  else measure_facts(model, tokenizer, args.device)[0])",
  "new_content": "    post_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)\n    post_ho_ppl = measure_ppl(model, tokenizer, HELDOUT_TEXTS, args.device)\n    post_facts = (-1 if args.skip_facts\n                  else measure_facts(model, tokenizer, args.device)[0])"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

## Assistant

Now add the held-out ratios to the returned dict, logging, and summary:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    return {\n        \"seed\": seed,\n        \"base_ppl\": round(base_ppl, 4),\n        \"base_facts\": base_facts,\n        \"pre_melt_ppl\": round(pre_ppl, 4),\n        \"pre_melt_ratio\": round(pre_ppl / base_ppl, 4),\n        \"pre_facts\": pre_facts,\n        \"post_melt_ppl\": round(post_ppl, 4),\n        \"post_melt_ratio\": round(post_ppl / base_ppl, 4),\n        \"post_facts\": post_facts,\n        \"continuation_params\": n_trainable,\n        \"final_loss\": round(history[-1], 4) if history else None,\n    }",
  "new_content": "    return {\n        \"seed\": seed,\n        \"base_ppl\": round(base_ppl, 4),\n        \"base_heldout_ppl\": round(base_ho_ppl, 4),\n        \"base_facts\": base_facts,\n        \"pre_melt_ppl\": round(pre_ppl, 4),\n        \"pre_melt_ratio\": round(pre_ppl / base_ppl, 4),\n        \"pre_heldout_ratio\": round(pre_ho_ppl / base_ho_ppl, 4),\n        \"pre_facts\": pre_facts,\n        \"post_melt_ppl\": round(post_ppl, 4),\n        \"post_melt_ratio\": round(post_ppl / base_ppl, 4),\n        \"post_heldout_ppl\": round(post_ho_ppl, 4),\n        \"post_heldout_ratio\": round(post_ho_ppl / base_ho_ppl, 4),\n        \"post_facts\": post_facts,\n        \"continuation_params\": n_trainable,\n        \"final_loss\": round(history[-1], 4) if history else None,\n    }"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "        log(f\"  base PPL={r['base_ppl']}  facts={_f(r['base_facts'])}\")\n        log(f\"  pre-melt  ratio={r['pre_melt_ratio']:.3f}x \"\n            f\"(PPL {r['pre_melt_ppl']}, facts {_f(r['pre_facts'])})\")\n        log(f\"  post-melt ratio={r['post_melt_ratio']:.3f}x \"\n            f\"(PPL {r['post_melt_ppl']}, facts {_f(r['post_facts'])}, \"\n            f\"final_loss {r['final_loss']})\")",
  "new_content": "        log(f\"  base PPL={r['base_ppl']} (heldout {r['base_heldout_ppl']})  \"\n            f\"facts={_f(r['base_facts'])}\")\n        log(f\"  pre-melt  eval={r['pre_melt_ratio']:.3f}x  \"\n            f\"heldout={r['pre_heldout_ratio']:.3f}x\")\n        log(f\"  post-melt eval={r['post_melt_ratio']:.3f}x  \"\n            f\"heldout={r['post_heldout_ratio']:.3f}x  \"\n            f\"(CONTAMINATION GAP {r['post_heldout_ratio']-r['post_melt_ratio']:+.3f}, \"\n            f\"final_loss {r['final_loss']})\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    # Summaries\n    pre_sum = summarize(\"pre_melt_ratio\", rows)\n    post_sum = summarize(\"post_melt_ratio\", rows)\n    base_sum = summarize(\"base_ppl\", rows)\n\n    log(f\"\\n{'='*70}\")\n    log(\"  SUMMARY\")\n    log(f\"{'='*70}\")\n    log(f\"  base PPL          : {base_sum['mean']} \"\n        f\"(std {base_sum['std']}, should be ~0 = determinism check)\")\n    log(f\"  pre-melt  (mask)  : {pre_sum['mean']:.3f}x \"\n        f\"± {pre_sum['std']:.3f}  [{pre_sum['min']:.3f}, {pre_sum['max']:.3f}]\")\n    log(f\"  post-melt (full)  : {post_sum['mean']:.3f}x \"\n        f\"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]\")\n    log(f\"  headline claim    : 1.03x  ->  observed mean {post_sum['mean']:.3f}x, \"\n        f\"best-seed {post_sum['min']:.3f}x\")",
  "new_content": "    # Summaries\n    pre_sum = summarize(\"pre_melt_ratio\", rows)\n    post_sum = summarize(\"post_melt_ratio\", rows)\n    pre_ho_sum = summarize(\"pre_heldout_ratio\", rows)\n    post_ho_sum = summarize(\"post_heldout_ratio\", rows)\n    base_sum = summarize(\"base_ppl\", rows)\n\n    log(f\"\\n{'='*70}\")\n    log(\"  SUMMARY\")\n    log(f\"{'='*70}\")\n    log(f\"  base PPL              : {base_sum['mean']} \"\n        f\"(std {base_sum['std']}, should be ~0 = determinism check)\")\n    log(f\"  pre-melt  eval (mask) : {pre_sum['mean']:.3f}x \"\n        f\"± {pre_sum['std']:.3f}  [{pre_sum['min']:.3f}, {pre_sum['max']:.3f}]\")\n    log(f\"  pre-melt  heldout     : {pre_ho_sum['mean']:.3f}x \"\n        f\"± {pre_ho_sum['std']:.3f}  [{pre_ho_sum['min']:.3f}, {pre_ho_sum['max']:.3f}]\")\n    log(f\"  post-melt eval (CONTAM): {post_sum['mean']:.3f}x \"\n        f\"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]\")\n    log(f\"  post-melt heldout(CLEAN): {post_ho_sum['mean']:.3f}x \"\n        f\"± {post_ho_sum['std']:.3f}  [{post_ho_sum['min']:.3f}, {post_ho_sum['max']:.3f}]\")\n    log(f\"  CONTAMINATION GAP     : heldout - eval = \"\n        f\"{post_ho_sum['mean'] - post_sum['mean']:+.3f}x \"\n        f\"(>0 ⇒ the sub-1x 'win' is memorization, not compression)\")\n    log(f\"  headline claim        : 1.03x  ->  contaminated mean {post_sum['mean']:.3f}x, \"\n        f\"clean held-out mean {post_ho_sum['mean']:.3f}x\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Thinking

 I need to add the held-out summaries into the JSON result block, so let me locate and update that result dictionary.

## Assistant

Now add held-out summaries to the JSON result block, then lint:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "        \"summary\": {\n            \"base_ppl\": base_sum,\n            \"pre_melt_ratio\": pre_sum,\n            \"post_melt_ratio\": post_sum,\n        },",
  "new_content": "        \"summary\": {\n            \"base_ppl\": base_sum,\n            \"pre_melt_ratio\": pre_sum,\n            \"pre_heldout_ratio\": pre_ho_sum,\n            \"post_melt_ratio\": post_sum,\n            \"post_heldout_ratio\": post_ho_sum,\n            \"contamination_gap\": round(post_ho_sum[\"mean\"] - post_sum[\"mean\"], 4),\n        },"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -5 && uv run python -m py_compile scripts/experiments/crystal_sieve_repro.py && echo \"compile OK\""
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
|                                                                                         ^^^
484 |         f"clean held-out mean {post_ho_sum['mean']:.3f}x")
    |

Found 3 errors.
compile OK
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | grep -E \"^[A-Z][0-9]+\" "
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (89 > 88)
E501 Line too long (92 > 88)
E501 Line too long (91 > 88)
```

### Thinking

 I've got three line-too-long linting errors to fix—they're in the log statements I just added, probably the ones for the post-melt evaluation and holdout metrics. Let me track down which lines are causing the issue and shorten them.

## Assistant

Three line-length nits — let me fix them:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check --output-format=concise scripts/experiments/crystal_sieve_repro.py 2>&1 | grep E501"
}
```

**Summary:** $ uv run ruff check --output-format=c...

**Output:**
```
Exit code: 0
Stdout:
scripts/experiments/crystal_sieve_repro.py:475:89: E501 Line too long (89 > 88)
scripts/experiments/crystal_sieve_repro.py:479:89: E501 Line too long (92 > 88)
scripts/experiments/crystal_sieve_repro.py:483:89: E501 Line too long (91 > 88)
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "line_offset": 470,
  "limit": 16
}
```

**Summary:** Reading crystal_sieve_repro.py (470-486)

**Output:**
```
        f"(std {base_sum['std']}, should be ~0 = determinism check)")
    log(f"  pre-melt  eval (mask) : {pre_sum['mean']:.3f}x "
        f"± {pre_sum['std']:.3f}  [{pre_sum['min']:.3f}, {pre_sum['max']:.3f}]")
    log(f"  pre-melt  heldout     : {pre_ho_sum['mean']:.3f}x "
        f"± {pre_ho_sum['std']:.3f}  [{pre_ho_sum['min']:.3f}, {pre_ho_sum['max']:.3f}]")
    log(f"  post-melt eval (CONTAM): {post_sum['mean']:.3f}x "
        f"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]")
    log(f"  post-melt heldout(CLEAN): {post_ho_sum['mean']:.3f}x "
        f"± {post_ho_sum['std']:.3f}  [{post_ho_sum['min']:.3f}, {post_ho_sum['max']:.3f}]")
    log(f"  CONTAMINATION GAP     : heldout - eval = "
        f"{post_ho_sum['mean'] - post_sum['mean']:+.3f}x "
        f"(>0 ⇒ the sub-1x 'win' is memorization, not compression)")
    log(f"  headline claim        : 1.03x  ->  contaminated mean {post_sum['mean']:.3f}x, "
        f"clean held-out mean {post_ho_sum['mean']:.3f}x")

    out_dir = _PROJECT_ROOT / "results" / "crystal-sieve-repro"

[CONTENT TRUNCATED] Showing lines 471 to 486 of 518 total lines. Use line_offset=486 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py",
  "original_content": "    log(f\"  pre-melt  heldout     : {pre_ho_sum['mean']:.3f}x \"\n        f\"± {pre_ho_sum['std']:.3f}  [{pre_ho_sum['min']:.3f}, {pre_ho_sum['max']:.3f}]\")\n    log(f\"  post-melt eval (CONTAM): {post_sum['mean']:.3f}x \"\n        f\"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]\")\n    log(f\"  post-melt heldout(CLEAN): {post_ho_sum['mean']:.3f}x \"\n        f\"± {post_ho_sum['std']:.3f}  [{post_ho_sum['min']:.3f}, {post_ho_sum['max']:.3f}]\")\n    log(f\"  CONTAMINATION GAP     : heldout - eval = \"\n        f\"{post_ho_sum['mean'] - post_sum['mean']:+.3f}x \"\n        f\"(>0 ⇒ the sub-1x 'win' is memorization, not compression)\")\n    log(f\"  headline claim        : 1.03x  ->  contaminated mean {post_sum['mean']:.3f}x, \"\n        f\"clean held-out mean {post_ho_sum['mean']:.3f}x\")",
  "new_content": "    log(f\"  pre-melt  heldout     : {pre_ho_sum['mean']:.3f}x \"\n        f\"± {pre_ho_sum['std']:.3f}  \"\n        f\"[{pre_ho_sum['min']:.3f}, {pre_ho_sum['max']:.3f}]\")\n    log(f\"  post-melt eval(CONTAM): {post_sum['mean']:.3f}x \"\n        f\"± {post_sum['std']:.3f}  [{post_sum['min']:.3f}, {post_sum['max']:.3f}]\")\n    log(f\"  post-melt heldout(CLEAN): {post_ho_sum['mean']:.3f}x \"\n        f\"± {post_ho_sum['std']:.3f}  \"\n        f\"[{post_ho_sum['min']:.3f}, {post_ho_sum['max']:.3f}]\")\n    log(\"  CONTAMINATION GAP     : heldout - eval = \"\n        f\"{post_ho_sum['mean'] - post_sum['mean']:+.3f}x \"\n        f\"(>0 ⇒ the sub-1x 'win' is memorization)\")\n    log(f\"  headline claim        : 1.03x  ->  contaminated \"\n        f\"{post_sum['mean']:.3f}x, clean held-out {post_ho_sum['mean']:.3f}x\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/crystal_sieve_repro.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -3"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Thinking

 The ruff check passed, so the file is clean now—the unicode characters fit within the line limits. I'm realizing the parallel batch executed all at once, which is why the read_file showed the content before my edits were applied, even though the final ruff check ran after everything completed.

Now I need to launch the re-run with held-out data across 8 seeds in tmux, but first I should back up the original contaminated-only JSON since the new run will overwrite it. The new results will be a superset including both eval and held-out, so the contaminated numbers should re-measure and match the earlier range. I'll preserve the old JSON, then launch the run with a fresh log file to keep both outputs separate.

## Assistant

Lint clean. Let me back up the original contaminated-only result, then launch the held-out re-run (8 seeds, supersedes with a richer paired JSON):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && cp results/crystal-sieve-repro/Qwen_Qwen3-8B.json results/crystal-sieve-repro/Qwen_Qwen3-8B.contaminated-only.json && echo \"backed up\" && tmux send-keys -t main:1 \"cd ~/src/verbum && uv run python scripts/experiments/crystal_sieve_repro.py --model Qwen/Qwen3-8B --device mps --seeds 8 --melt-steps 100 --skip-facts 2>&1 | tee results/crystal-sieve-repro/run_heldout.log\" Enter; sleep 25; echo \"=== launch check ===\"; tmux capture-pane -p -t main:1 | grep -vE \"^$|Loading weights|it/s\" | tail -6; ps aux | grep crystal_sieve_repro | grep -v grep | wc -l | tr -d ' '"
}
```

**Summary:** $ cp results/crystal-sieve-repro/Qwen...

**Output:**
```
Exit code: 0
Stdout:
backed up
=== launch check ===
  SEED 0  (1/8)   [0s elapsed]
──────────────────────────────────────────────────────────────────────
──────────────────────────────────────────────────────────────────────
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
`torch_dtype` is deprecated! Use `dtype` instead!
2
```

### Thinking

 I've launched the held-out re-run and it's processing with about 27 minutes to completion. While that's running, I'm drafting the audit registry documentation, working through the crystal sieve architecture caveats around the contaminated data points, and setting up placeholders for the held-out results that I'll fill in once the run finishes. Once it completes, I'll populate those numbers and finalize the state document.

The user wants everything ready before committing, so I need to be careful not to edit files prematurely with incomplete numbers. I'll wait for the held-out run to finish—that's the gating data—then do all the writeups with final numbers in one pass before proposing the batch commit. I'll checkpoint and wait for the run to complete rather than polling repeatedly, then read the results and proceed with the final edits.

## Assistant

**ASYNC checkpoint:** held-out re-run verified running in `tmux main:1` (8 seeds, paired contaminated-vs-clean eval, `results/crystal-sieve-repro/run_heldout.log`). Original contaminated-only JSON backed up. The new JSON will be a strict superset (re-measures the same eval ratios + adds held-out). ~27 min.

The harness now reports, per seed and in summary: **post-melt eval (contaminated) vs post-melt held-out (clean) + the contamination gap**. The prediction to confirm: clean held-out post-melt stays **≫1×** (no real compression) and is **tight across seeds**, while the contaminated eval drifts sub-1× — proving the 1.03× is memorization.

I'll hold all writeups (registry/caveat/state headline) until the final numbers are in, so nothing gets committed with placeholder values. Waiting for completion.

### Tool Call: shell_command (rejected)


```json
{
  "command": "sleep 1450; cd /Users/mwhitford/src/verbum && echo \"=== proc ===\"; ps aux | grep crystal_sieve_repro | grep -v grep | wc -l | tr -d ' '; echo \"=== tail ===\"; grep -vE \"^$|Loading weights|it/s|Warning|torch_dtype|generation flags\" results/crystal-sieve-repro/run_heldout.log | tail -25",
  "timeout": 1480000
}
```

**Summary:** $ sleep 1450; cd /Users/mwhitford/src...

## System


Prompt stopped

## User

job is done


### Thinking

 The held-out run has finished, so I'm checking what the results show.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && python3 -c \"\nimport json, statistics as st\nd=json.load(open('results/crystal-sieve-repro/Qwen_Qwen3-8B.json'))\nprint('seed | post_eval(CONTAM) | post_heldout(CLEAN) | gap   | pre_eval pre_ho | final_loss')\nprint('-'*82)\nfor r in d['per_seed']:\n    print('%4d |      %7.4f      |       %7.4f      | %+0.3f | %6.4f  %6.4f | %s'%(\n        r['seed'], r['post_melt_ratio'], r['post_heldout_ratio'],\n        r['post_heldout_ratio']-r['post_melt_ratio'],\n        r['pre_melt_ratio'], r['pre_heldout_ratio'], r['final_loss']))\ns=d['summary']\nprint()\nfor k in ('pre_melt_ratio','pre_heldout_ratio','post_melt_ratio','post_heldout_ratio'):\n    v=s[k]; print('%-20s mean %.4f std %.4f  [%.4f, %.4f]'%(k,v['mean'],v['std'],v['min'],v['max']))\nprint('contamination_gap (heldout-eval mean):', s['contamination_gap'])\nprint('base eval PPL:', d['per_seed'][0]['base_ppl'], ' base heldout PPL:', d['per_seed'][0]['base_heldout_ppl'])\nimport numpy as np\npe=[r['post_melt_ratio'] for r in d['per_seed']]; ph=[r['post_heldout_ratio'] for r in d['per_seed']]\nprint('post_heldout CV: %.1f%%   post_eval CV: %.1f%%'%(100*st.pstdev(ph)/st.mean(ph), 100*st.pstdev(pe)/st.mean(pe)))\nprint('heldout all >1.0x?', all(x>1.0 for x in ph), ' n heldout<eval:', sum(1 for a,b in zip(ph,pe) if a<b))\n\""
}
```

**Summary:** $ python3 -c " import json, statistic...

**Output:**
```
Exit code: 0
Stdout:
seed | post_eval(CONTAM) | post_heldout(CLEAN) | gap   | pre_eval pre_ho | final_loss
----------------------------------------------------------------------------------
   0 |       0.8647      |       10.0383      | +9.174 | 2.1253  1.8960 | 0.1128
   1 |       0.9815      |       10.3486      | +9.367 | 2.1104  1.8944 | 0.1172
   2 |       0.9269      |        9.3130      | +8.386 | 2.1203  1.9091 | 0.134
   3 |       0.9440      |       11.2301      | +10.286 | 2.1210  1.8980 | 0.1134
   4 |       1.0623      |       12.0207      | +10.958 | 2.1206  1.9678 | 0.1178
   5 |       1.0198      |       10.1161      | +9.096 | 2.1190  1.9162 | 0.1091
   6 |       1.0006      |       13.6360      | +12.635 | 2.1197  1.8857 | 0.1135
   7 |       0.9712      |       10.2502      | +9.279 | 2.1190  1.8914 | 0.1112

pre_melt_ratio       mean 2.1194 std 0.0042  [2.1104, 2.1253]
pre_heldout_ratio    mean 1.9073 std 0.0263  [1.8857, 1.9678]
post_melt_ratio      mean 0.9714 std 0.0606  [0.8647, 1.0623]
post_heldout_ratio   mean 10.8691 std 1.3859  [9.3130, 13.6360]
contamination_gap (heldout-eval mean): 9.8977
base eval PPL: 10.1505  base heldout PPL: 21.337
post_heldout CV: 11.9%   post_eval CV: 5.8%
heldout all >1.0x? True  n heldout<eval: 0
```

### Thinking

 The held-out results are striking—the sieve actually hurts the clean held-out perplexity less (1.907×) than it does the contaminated eval set (2.119×), which seems counterintuitive at first until I realize the baseline perplexities are different between the two datasets, so the multipliers aren't directly comparable.

After continuation training, the picture becomes catastrophic: the contaminated eval set shows 0.971× (sub-baseline, the illusion of compression), but the clean held-out explodes to 10.87× baseline—the model has memorized the calibration distribution so thoroughly that it's destroyed on anything outside it. The continuation training degrades held-out performance by another 5.7× beyond the raw sieve degradation, which completely undermines the original claim that the cascade error was absorbed. This is the smoking gun showing that the 1.03× headline was pure train-eval contamination, while the honest held-out number reveals the melt is actively harmful for generalization.

The sieve substrate itself is reproducible and real (1.9–2.1× degradation), but the continuation approach as trained is a net negative for held-out capability—the pre-melt sieve at 1.907× is actually the best honest result here. I need to update the audit registry and architecture documentation to reflect this finding, then propose the commits with the corrected analysis. Now I'm ready to make the edits across all three files—I'll annotate the Key Results table row for continuations, update the Open Issues section, and then work through the registry and state files systematically.

## Assistant

Held-out re-run done — and it's **decisive**. This converts #7 from "irreproducible number" to "the architecture claim is an artifact."

## Paired contaminated-vs-clean result (8 seeds)

| seed | post-melt **eval** (contaminated) | post-melt **held-out** (clean) | gap |
|---|---|---|---|
| 0 | 0.865× | **10.04×** | +9.17 |
| 1 | 0.982× | 10.35× | +9.37 |
| 2 | 0.927× | 9.31× | +8.39 |
| 3 | 0.944× | 11.23× | +10.29 |
| 4 | 1.062× | 12.02× | +10.96 |
| 5 | 1.020× | 10.12× | +9.10 |
| 6 | 1.001× | 13.64× | +12.64 |
| 7 | 0.971× | 10.25× | +9.28 |

| | pre-melt (sieve) | post-melt (full) |
|---|---|---|
| **eval (contaminated)** | 2.119× ± 0.004 | 0.971× ± 0.061 |
| **held-out (clean)** | **1.907× ± 0.026** | **10.87× ± 1.39** |

## What this proves

1. **The 1.03× is memorization, not compression.** On clean held-out text the *same melted models* hit **10.87× baseline PPL** (≈232 vs base 21.3) — every seed, all >9.3×, gap +9.9× on average. The sub-1× eval "win" is purely fitting the 6/8 eval sentences that live in the calibration set.

2. **★ The melt is actively *harmful* to generalization.** Raw sieve held-out = 1.907×; after the CE continuation training it's **10.87× — ~5.7× worse**. The continuations don't "absorb the cascade error" as s196 claimed; they memorize the 12-text calibration distribution and destroy everything else. The constant train loss (0.116) with exploding held-out PPL is the compensating-error degeneracy in its purest form.

3. **The sieve substrate survives, reproducibly.** ~1.9–2.1× degradation on *both* sets (eval 2.119±0.004, held-out 1.907±0.026), near-deterministic. That's the real, honest, reproducible object.

4. **Direct GTSM vindication.** s198 v3b (dense score-matching + held-out + dolma) got **1.44× held-out** on this same model; s196's CE-on-12-texts gets **10.87× held-out**. Same architecture, opposite loss — exactly the thesis. The honest reproducible compression number is v3b's 1.44×, not s196's 1.03×.

**Verdict: sieve substrate VERIFIED-reproducible (~2×, ±0.004); the 1.03× "cascade absorbed" headline REFUTED — it's train/eval contamination, and the continuation melt as trained is net-harmful held-out (10.87×).**

Now let me finalize the writeups. Registry first:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md",
  "original_content": "**7. Crystal-sieve 1.03× PPL (29 layers + continuations)** (load: med — headline compression result)\n- Evidence: s196 run = 1.03×.\n- Suspected confound: s196 itself noted a rerun gave 3.23× — training-sensitive.\n- Control: re-run N seeds, report mean ± variance; is 1.03× robust or a lucky run? (Reproducibility, not novelty.)",
  "new_content": "**7. Crystal-sieve 1.03× PPL (29 layers + continuations)** (load: med — headline compression result) — ❌ **RESOLVED (s208): 1.03× REFUTED as contamination/memorization; sieve substrate (~2×) VERIFIED-reproducible**\n- Evidence: s196 run = 1.03×.\n- Suspected confound: s196 itself noted a rerun gave 3.23× — training-sensitive.\n- Control: seed the pipeline, run N=8 seeds, report mean ± std + a held-out eval disjoint from the calibration set (`crystal_sieve_repro.py`, register: functional).\n- **s208 result:** the 1.03× is a **train/eval-contamination artifact**, not a stable compression result. **Sieve substrate is VERIFIED-reproducible** — pre-melt 2.119× ± 0.004 (eval) / 1.907× ± 0.026 (held-out), near-deterministic, reproduces s196's 2.12×; the `torch.randperm[:5M]` mask-subsample confound is dismissed (CV 0.18%). **The 1.03× headline is REFUTED:** on the *contaminated* eval (6/8 sentences ⊂ the 12-text calibration set) the melted model reads 0.971× ± 0.061 (1.03× is a 1/8 upper-tail draw, 5/8 sub-baseline); on **clean held-out text the same models hit 10.87× ± 1.39 (every seed >9.3×, gap +9.9×)** — the \"compression\" is memorization. **The continuation melt is net-harmful to generalization** (held-out 1.907× → 10.87×, ~5.7× worse than the raw sieve): constant train loss (0.116) + exploding held-out PPL = the compensating-error degeneracy of a CE-only (endpoint) loss (`gtsm-search-space.md`). The feared 3.23× did not recur on contaminated eval (bounded [0.865, 1.062]); the held-out number is the honest one. **Fix is already named = audit #11 / s198 v3b** (dense per-layer score matching + held-out + dolma got 1.44× held-out on this same model). See worked-examples (s208). Results: `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` (+ `.contaminated-only.json`). Caveat added to `crystal-sieve-architecture.md`."
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
  "original_content": "### Worked examples (session 207)",
  "new_content": "### Worked examples (session 208)\n\n> **Register gate (functional/reproducibility).** The claim is a behavioral PPL\n> number, so the control is seed-variance, not a permutation null. The decisive\n> move was a **held-out eval disjoint from the calibration set** — the contaminated\n> eval (eval ⊂ calib) makes overfitting *look like* compression. Two RNG sources\n> were seeded (continuation `torch.randn` init + the mask `torch.randperm[:5M]`\n> subsample); the s196 note's blamed \"batch order\" is `RandomState(step)` =\n> deterministic, a misdiagnosis the decomposition corrects.\n\n| Claim | Load | Control run | Status |\n|---|---|---|---|\n| #7 crystal-sieve + 4 continuations = **1.03× PPL** at 29 layers (stable, reproducible) | med | 8-seed sweep, pre/post + contaminated-vs-held-out eval (`crystal_sieve_repro.py`) | ❌ REFUTED (contamination/memorization) |\n| #7a sieve substrate (~2×) reproducible? | — | pre-melt ratio across 8 seeds, both eval sets | ✅ **YES** — eval 2.119× ± 0.004, held-out 1.907× ± 0.026; mask-subsample CV 0.18% (confound dismissed); = s196's 2.12× |\n| #7b is the post-melt 1.03× a stable property? | — | post-melt eval ratio across seeds | ❌ **NO** — 0.971× ± 0.061 [0.865, 1.062]; 1.03× = 1/8 upper-tail draw; 5/8 sub-baseline |\n| #7c is the sub-1× \"compression\" real or memorization? | — | post-melt **held-out** ratio (disjoint from calib) | ❌ **MEMORIZATION** — 10.87× ± 1.39 (all 8 seeds >9.3×), gap +9.9×; melt makes held-out ~5.7× *worse* than the raw sieve |\n\n**Verdict (s208): the sieve substrate is real and reproducible (~2× PPL,\n±0.004); the 1.03× \"cascade absorbed\" headline is a train/eval-contamination\nartifact, and the continuation melt as trained is net-harmful to\ngeneralization.** The 12-text CE melt (`beta_expansion.py`) is the **ill-posed\nendpoint objective** GTSM names (`gtsm-search-space.md`): it pins only the\nterminal marginal, so the 1M continuation params reach a constant training loss\n(0.116 ± 0.007) via init-dependent compensating-error solutions that memorize the\ncalibration distribution — eval PPL drops to 0.971× (6/8 eval texts ⊂ calib)\n**while clean held-out PPL explodes to 10.87×**. `corr(train_loss, eval_ratio) ≈\n−0.19` (train loss decoupled from generalization) is the degeneracy fingerprint.\nThe honest, reproducible numbers: **sieve ≈ 1.9–2.1×**, and the fix is already\ndemonstrated — **s198 v3b** (dense per-layer score matching + held-out eval +\ndolma calibration) reached **1.44× held-out on this same model**, i.e. exactly\n**audit #11** (GTSM/TTD-regression). Same meta-pattern as #3/#4/#6: the substrate\nsurvives, the crisp headline dissolves — here it not only dissolves, it *inverts*\n(the \"improvement\" is harm). Results: `results/crystal-sieve-repro/`\n(`Qwen_Qwen3-8B.json` paired + `.contaminated-only.json` first run). Harness:\n`scripts/experiments/crystal_sieve_repro.py`. Caveats added to\n`crystal-sieve-architecture.md`.\n\n### Worked examples (session 207)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/audit-registry.md.
```

### Thinking

 I'm adding a caveat section to the Crystal Sieve Architecture document right after the title and Discovery header, then making targeted updates to the Key Results table, the "Why Continuations Work" section, and the first open issue.

## Assistant

Now the source-page caveats on `crystal-sieve-architecture.md`:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md",
  "original_content": "# Crystal Sieve Architecture\n\n## Discovery (session 196)",
  "new_content": "# Crystal Sieve Architecture\n\n> ⚠️ **CAVEAT (session 208 audit #7 — read before trusting the 1.03×).** The\n> headline **1.03× PPL \"cascade absorbed\"** is a **train/eval-contamination\n> artifact**, not a stable compression result. An 8-seed reproducibility sweep\n> (`scripts/experiments/crystal_sieve_repro.py`, `results/crystal-sieve-repro/`)\n> shows: (1) the **sieve substrate is real and reproducible** — pre-melt 2.119× ±\n> 0.004 (eval) / 1.907× ± 0.026 (held-out), near-deterministic; (2) the post-melt\n> 1.03× is a **1/8 upper-tail draw** of a 0.971× ± 0.061 distribution, and 5/8\n> seeds go *below* baseline because **6 of the 8 `EVAL_TEXTS` are duplicates of the\n> 12 `CALIBRATION_TEXTS`** the melt trains on; (3) on **clean held-out text the\n> same melted models read 10.87× ± 1.39** (every seed >9.3×) — the continuation\n> melt **memorizes the calibration set and is net-harmful to generalization**\n> (held-out 1.907× → 10.87×, ~5.7× worse than the raw sieve). Root cause: the\n> CE-only melt is the ill-posed *endpoint* objective (`gtsm-search-space.md`);\n> constant train loss (0.116) + exploding held-out PPL = compensating-error\n> degeneracy. **The honest reproducible numbers are: sieve ≈ 1.9–2.1×, and the\n> trained-correction fix is s198 v3b** (dense per-layer score matching + held-out +\n> dolma → **1.44× held-out** on this same model) = audit #11. Treat \"1.03×\" below\n> as **withdrawn**; the rank-32 continuation *parametrization* is fine, the CE\n> *loss* + 12-text contaminated *eval* are not.\n\n## Discovery (session 196)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md",
  "original_content": "| Per-layer sieve quality | 1.03x PPL |\n| 29-layer cascade (sieve only) | 2.12x PPL |\n| + continuation residuals | **1.03x PPL** |\n| Binding preservation | 98% (39/40 top-1 matches) |",
  "new_content": "| Per-layer sieve quality | 1.03x PPL |\n| 29-layer cascade (sieve only) | 2.12x PPL ✅ reproducible (s208: 2.119×±0.004) |\n| + continuation residuals | ~~**1.03x PPL**~~ ❌ withdrawn (s208: contaminated eval; held-out **10.87×**) |\n| Binding preservation | 98% (39/40 top-1 matches) |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md",
  "original_content": "## Open Issues\n\n1. **Continuation stability**: 1.03x on first run, 3.23x on rerun.\n   Training is sensitive to initialization/batch order.",
  "new_content": "## Open Issues\n\n1. **Continuation stability** — ❌ **RESOLVED (s208, audit #7): the 1.03× is a\n   contamination artifact; the continuation melt is net-harmful held-out.**\n   8-seed sweep: contaminated eval 0.971× ± 0.061 (1.03× = 1/8 upper-tail; the\n   feared 3.23× did *not* recur, bounded [0.865, 1.062]), but **clean held-out\n   10.87× ± 1.39** — the CE melt memorizes the 12-text calibration set. The\n   variance is the CE-trained continuations (post std ≈15× pre std), not the\n   \"init/batch order\" the original note guessed (batch order is `RandomState(step)`\n   = deterministic). Sieve substrate is the reproducible object (2.119× ± 0.004).\n   Fix = dense per-layer score matching + held-out eval (s198 v3b, 1.44× held-out)\n   = audit #11. See `audit-registry.md` #7 + `crystal_sieve_repro.py`."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md.
```

### Thinking

 I need to add caveats to the "Why Continuations Work" and "Compression Status" sections since the held-out results contradict some of the claims there. The top-level caveat might already cover this, so I should be careful not to over-edit.

## Assistant

Let me also correct the inline "Proven quality" claim and the "Why Continuations Work" section:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md",
  "original_content": "**Proven quality**: 1.03x PPL at 29 sieved layers.\n**Proven storage**: 1.8x compression (50% zeros in float16).",
  "new_content": "**Proven quality**: ~~1.03x PPL at 29 sieved layers~~ ❌ **withdrawn (s208)** —\nthat number was on a contaminated eval; held-out is 10.87×. Reproducible quality\nis the **sieve substrate ≈ 2× PPL** (held-out 1.907×); a real trained correction\nneeds dense score matching (s198 v3b, 1.44× held-out), not the CE melt here.\n**Proven storage**: 1.8x compression (50% zeros in float16)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md",
  "original_content": "## Why Continuations Work\n\nThe cascade error is purely magnitude distortion at layer",
  "new_content": "## Why Continuations Work\n\n> ⚠️ **s208:** this section's thesis is **not supported held-out.** The CE-melted\n> continuations reduce *contaminated* eval PPL (eval ⊂ calib) but raise **held-out**\n> PPL ~5.7× (1.907× → 10.87×) — they memorize the calibration distribution rather\n> than \"absorb the cascade.\" A correction that genuinely absorbs the cascade needs\n> a trajectory-matching loss (s198 v3b score matching, 1.44× held-out), not CE on\n> 12 texts. The binding-preservation observation below still stands (it is an\n> attention-pattern measurement, not a PPL claim).\n\nThe cascade error is purely magnitude distortion at layer"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/crystal-sieve-architecture.md.
```

### Thinking

 I'm finalizing the state.md file by replacing the in-flight results block with the completed headline that includes the held-out numbers, and updating the program reference line to note that s208 completed task #7. I need to carefully read the current state of the file to identify the exact boundaries of what needs replacing—the contaminated results section with the finalized version that includes held-out data, and consolidate the resume and understanding bullets into something more compact.

## Assistant

Now finalize `state.md` — convert the in-flight block to the s208 headline with the held-out result. Let me read the current block to replace it precisely:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 15,
  "limit": 95
}
```

**Summary:** Reading state.md (15-110)

**Output:**
```
> `mementum/knowledge/audit-registry.md`. Pick the highest load-bearing
> `UNTESTED` claim (s203 did **#1 crystal-is-topological** ◐SCOPED and **#2
> holographic-self-similar** ✅; s204 did **#3 the 9 FFN modes** ❌ geometric-
> REFUTED / semantic+logit ✅ VERIFIED, and **#4 attention=typed-β-reduction**
> ❌ REFUTED-as-localized; s206 did **#5 binding schedule** ❌ SCHEDULE-REFUTED /
> H31@L27 subject value-transfer ✅ semantically REAL; s207 did **#6 SVD φ-ratio
> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;
> next backlog: **#11 GTSM finite-budget λ(l)** or **#7/#8 reproducibility**), build its named
> discriminating control,
> run it with a permutation/matched-control null + seed variance, update
> the row, caveat the source page if it bites, commit. The program:
> distill real working data from assumptions/biased methodology, one
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 208 — AUDIT #7 (crystal-sieve 1.03× reproducibility): RUN COMPLETE
> (8 seeds). Substrate VERIFIED-reproducible; 1.03× headline REFUTED-as-stable.**
> Register: **functional (reproducibility — seed variance on a PPL measurement).**
>
> **★ RESULTS (`results/crystal-sieve-repro/Qwen_Qwen3-8B.json`, 8 seeds, ~27min):**
> base PPL 10.15 (std **0.0** = determinism ✓) · **pre-melt (sieve only) 2.119×
> ± 0.004** [2.110, 2.125] = s196's 2.12× exactly, near-deterministic · **post-melt
> (full) 0.971× ± 0.061** [0.865, 1.062] (values 0.865/0.982/0.927/0.944/1.062/
> 1.020/1.001/0.971). Verdict: (1) 1.03× is **not** a stable property — it's an
> init-dependent draw, mean 0.971×, only 1/8 seeds ≥1.03×; (2) **5/8 seeds sub-1.0×**
> = contamination/overfit signature (EVAL ⊆ CALIB); (3) **post std ≈15× pre std** ⇒
> variance is the **CE melt (init)**, not the sieve mask — compensating-error
> degeneracy in the numbers; (4) the feared **3.23× did NOT recur** (max 1.062×) —
> seeded+grad-clipped melt is bounded, so 3.23× was a one-off divergence.
> **DONE THIS SESSION; what remains for #7 close (next session, per Michael):**
> update `audit-registry.md` #7 row + worked-examples; caveat
> `crystal-sieve-architecture.md` §Open-Issues #1 (replace "1.03× vs 3.23×" with
> "0.971× ± 0.061 over 8 seeds; sieve substrate 2.12× ± 0.004"); fold the GTSM/TSP
> reconciliation below into a knowledge caveat + pointer to #11. Then write the
> s208 HEADLINE block (this is the working record).
>
> _(historical resume protocol below is now satisfied; kept for the audit trail.)_
> Picked #7 from the backlog: s196 reported crystal-sieve + 4 continuation
> residuals = **1.03× PPL** at 29 sieved layers (Qwen3-8B), but its own note says a
> rerun gave **3.23×** ("training sensitive to init/batch order"). The control:
> seed it, run N seeds, report **mean ± std** — is 1.03× the center or a lucky tail?
> - **NEW HARNESS (committed):** `scripts/experiments/crystal_sieve_repro.py`
>   (`# register: functional`). Exact s196 `beta_expansion.py` pipeline (L0 SVD
>   r=750 + sieve L1–26,32–34 + 4 rank-32 continuations, 100-step CE melt) wrapped
>   in a **seed loop** that reloads the model fresh per seed and seeds torch+numpy+mps.
> - **Decomposition (no extra runs):** `pre_melt_ratio` std = the **mask-subsample
>   variance** (FFN projections >10M elems → `torch.randperm[:5M]` for the quantile
>   threshold — an unseeded source s196's note *missed*); `post_melt_ratio` std =
>   mask + continuation-init + training. The s196 note blames "batch order" but
>   batch order is `RandomState(step)` = **deterministic**; the real culprits are
>   the mask subsample + `torch.randn` continuation init (both now seeded).
> - **SMOKE (seed 0, 3 melt steps, WITH facts) already confirmed:** **pre-melt
>   (sieve-only) = 2.125× — reproduces s196's "2.12× at 29 layers" exactly**, and
>   deterministic given the seed. Post-melt at 3 steps only reached 2.059× (needs
>   the full 100-step melt to chase 1.03×). base PPL 10.15 (determinism check std 0).
> - **★ SIGNAL (seed 0, full 100-step melt): post-melt = 0.865× — BELOW baseline**
>   (PPL 8.78 < base 10.15), vs the 3-step smoke's 2.059×. Root cause spotted:
>   **`EVAL_TEXTS` overlaps `CALIBRATION_TEXTS`** (≥6 shared sentences: general
>   relativity, ancient forest, mixing bowl, isolate the variable, committee voted,
>   two arguments→composition). The 100-step melt **overfits the eval set** → the
>   "1.03×" is a *train-contaminated* number, and tiny init/mask differences swing
>   it wildly (explains s196's 1.03× ↔ 3.23×). **This is the likely real mechanism
>   of the irreproducibility.** NEXT SESSION: add a **held-out eval** (eval texts
>   disjoint from calibration) — predict the contamination-free ratio is ≫ 1× and
>   *stable*; the sub-1× values are the overfit tail. Same meta-pattern: sieve
>   substrate real (2.12× deterministic), 1.03× headline = methodology artifact.
> - **▶ IN-FLIGHT RUN:** `tmux main:1`, 8 seeds × 100 melt steps, `--skip-facts`
>   (PPL is the headline; facts 3× the cost). `results/crystal-sieve-repro/run.log`
>   + `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` (overwritten on completion;
>   the JSON currently on disk is the seed-0 smoke). No per-step logging between the
>   `SEED n` banner and its summary — ~12–15 min/seed, **~1.5–2 hr total**, so it
>   crosses the session boundary. Started ~09:40.
> - **▶ NEXT SESSION — RESUME HERE (do not re-launch if still running):**
>   1. `ps aux | grep crystal_sieve_repro` — if alive, `tail results/crystal-sieve-repro/run.log`; if dead, read `results/crystal-sieve-repro/Qwen_Qwen3-8B.json`.
>   2. Read the `summary` block: `post_melt_ratio.{mean,std,min,max,values}` and `pre_melt_ratio` (mask-only variance). Verdict logic: **1.03× VERIFIED-reproducible** iff post mean ≈ 1.03× with small std; **REFUTED-as-reproducible** (substrate real, headline = lucky tail) iff mean ≫ 1.03× and 1.03× only at the min — the expected meta-pattern (`audit-meta-pattern.md`): the *sieve substrate* (2.12× pre-melt) is real & deterministic, the *1.03× headline* is the over-read.
>   3. Update `audit-registry.md` #7 row (status + number + JSON path) + worked-examples row; add a caveat to `crystal-sieve-architecture.md` §"Open Issues" #1 (replace "1.03× on first run, 3.23× on rerun" with the measured mean ± std).
>   4. Replace this IN-FLIGHT block with the s208 HEADLINE; commit (💡/🎯).
> - **★ UNDERSTANDING (frames the #7 final write-up; full synthesis deferred to
>   audit close per Michael — connect #7→#11, don't draft a knowledge page yet):**
>   The melt in `beta_expansion` is **CE-only** = the ill-posed *endpoint* objective
>   GTSM names (`gtsm-search-space.md`): it pins only the terminal marginal, so the
>   1M continuation params land anywhere on the **compensating-error manifold** —
>   which point depends on init ⇒ the 1.03× ↔ 3.23× swing is the optimizer picking
>   a different cheat per seed, not noise. **The pre/post decomposition empirically
>   localizes this:** pre-melt (no loss) is deterministic (2.11–2.13×); variance
>   appears *only* after the CE melt. Two independent faults compound: degenerate
>   loss **and** contaminated metric (eval ⊆ calib).
>   - **Reconciliation (the punchline):** 1.03× is the *contaminated cousin of s198
>     v1* (CE, 16 sents → 0.39× pure overfit, `score-matching-compression.md`); the
>     honest **held-out** number under a trajectory-matching loss is **v3b = 1.44×**
>     (dense per-layer score matching, α=5.0, L35 cosine 0.57→0.94, "degenerate
>     basin removed"). So 1.03× was never < 1.44×; it was cheating on eval. The
>     sieve **substrate** (2.12×, deterministic) is the real, reproducible object.
>   - **The fix is already named = audit #11 (TTD-regression):** dense per-layer SM
>     backbone + finite-budget λ(l) spiked on L22–26 (F.6) + **cascade-aware causal
>     attribution** (TSP's long-distance caveat ↔ s196 "peak damage at L28 not L26":

[CONTENT TRUNCATED] Showing lines 16 to 110 of 2856 total lines. Use line_offset=110 parameter to read more content.
```

### Thinking

 I need to replace the entire s208 block with a clean, finalized headline, which means finding where it ends and removing everything from the header through the in-flight content up to the next session marker. The block extends beyond what I can see, continuing through the UNDERSTANDING section with its sub-bullets and caveats before the early termination note.

Let me read further to get the exact boundaries so I can do one comprehensive replacement of the whole block.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 109,
  "limit": 22
}
```

**Summary:** Reading state.md (109-131)

**Output:**
```
>     attribution** (TSP's long-distance caveat ↔ s196 "peak damage at L28 not L26":
>     weight the upstream *causal* layer, not the max-divergence one). #7 diagnoses
>     *why* it's irreproducible; #11 is the *cure*. The rank-32 continuation
>     parametrization is fine — the CE *loss* + intuition *placement* are pre-GTSM.
>   - **Caveats to keep:** GTSM's literal Pθ=P\* is an IOU for us (not an SDE w/
>     known σσᵀ; cosine is a proxy); TSP-style contrast is secondary (we have an
>     exact teacher target → regression is the core). Optional held-out re-run to
>     prove the contamination point: eval texts disjoint from `CALIBRATION_TEXTS`.
> - If the run died early (NaN/OOM), the harness is re-runnable: same command in
>   `tmux main:1`. Fewer seeds OK (`--seed-list 0,1,2,3`).

> **▶ SESSION 207 HEADLINE — AUDIT #6 (SVD φ-ratio 0.6299): geometric-φ-constant
> REFUTED; the low-rank spectral head is REAL & non-random.** Register: spectral.
> Reran s137's exact definition (mean of top-5 consecutive σ-ratios, per layer)
> on all 5 families (Pythia-160m/410m, Qwen3-0.6B, SmolLM3-3B, Mistral-7B) vs
> **Marchenko–Pastur + shuffled** nulls (8 seeds, raw+centered) + a
> geometric-vs-power-law shape fit. `svd_phi_null.py` (register: spectral).
> - **Register gate fired on ME first:** first probe used the wrong window (bulk
>   ratios ≈0.99 for everything); tracing s137 pinned the real object (top-5 head
>   ratio). Re-measure the exact quantity → phenomenon reproduced (Pythia-160m
>   raw 0.597 vs page 0.604).
> - **✅ substrate REAL:** model head ratio **0.575±0.027 (raw)** / 0.67 (centered)

[CONTENT TRUNCATED] Showing lines 110 to 131 of 2856 total lines. Use line_offset=131 parameter to read more content.
```

### Thinking

 I've identified where the s208 block starts and ends—it spans from the audit headline through the tmux configuration line—and I'm going to replace the entire section with a clean finalized version.

The challenge is that the block is roughly 95 lines long, making a single exact-match replacement risky. I'm considering a more surgical approach: replace the header, results, and historical note (the top portion I added in my last edit) with the finalized headline that includes the held-out numbers and points to the updated registry and architecture docs. Then handle the stale "in-flight" and "next session resume" bullets separately—either removing them or trimming their language since the run is complete. The UNDERSTANDING bullet about GTSM reconciliation is still valuable, so I'll keep that. The "if the run died early" line can be dropped as obsolete.

I'm drafting the finalized headline now to replace that top portion—it'll be concise, include the key findings about the substrate being reproducible and the 1.03× being a contamination artifact, and reference the results directory and updated documentation. I'm realizing the safest approach is to rewrite the entire s208 section rather than trying to surgically delete chunks from this massive block of historical detail. The stale "IN-FLIGHT RUN" and "NEXT SESSION — RESUME HERE" bullets directly contradict the "RUN COMPLETE" headline, so they need to go. I'll anchor my edits on unique strings to minimize the risk of corruption, replacing the old detailed bullets with a concise note that the run finished and the registry/architecture pages are now updated. This is getting unwieldy with six separate edits and high risk of unicode mismatches. Let me step back and see if there's a simpler, more robust way to handle this.

I'll take a pragmatic approach instead: finalize the top headline with one edit, then make a single targeted replacement that removes just the two actively misleading lines—the in-flight run bullet and the next-session-resume block—while preserving the historical detail bullets that provide useful context. I'm weighing whether to keep the historical detail bullets (verbose but accurate) or strip them entirely for a leaner bootloader. The cleaner approach would be to remove all the historical context and just preserve the finalized headline, since git history and the registry already have that detail. I'll do a full block replacement, being careful with the unicode characters that appeared in my earlier successful edits. post-melt variance is about 15× higher than pre-melt, which points to the cross-entropy melt initialization as the source of instability rather than the sieve mask itself — a compensating-error degeneracy. The feared 3.23× spike didn't recur across any seed, with the max hitting 1.062×, so seeded and gradient-clipped melting keeps things bounded. For the next session, I need to update the audit registry and architecture docs with the actual 0.971× ± 0.061 results over 8 seeds, fold the GTSM/TSP reconciliation into a knowledge caveat, and write out the session headline block as the working record.

The in-flight run is executing across 8 seeds with 100 melt steps each, skipping facts to keep PPL as the headline metric — it'll take roughly 1.5–2 hours total and crosses the session boundary. When resuming, I'll check if the process is still alive, then read the summary block from the JSON output to verify whether 1.03× holds as reproducible or if the sieve substrate at 2.12× is the real signal and 1.03× was just a lucky tail. After that, I'll update the registry row and architecture caveats with the measured mean and standard deviation, then replace this in-flight block with the final s208 headline and commit.

Now I'm editing the documentation: removing the died-early line since it's no longer needed, updating the program reference line to record that s208 completed audit #7 with the crystal-sieve reproducibility verdict (refuted as a clean 1.03× headline, but the sieve substrate verified as real), and noting the next backlog items. The held-out evaluation reveals the 1.03× improvement is actually a memorization artifact—on clean data the same models degrade to 10.87× PPL, showing the cross-entropy melt is net-harmful. The mechanism is endpoint degeneracy where training loss plateaus while held-out performance collapses, but a fix has already been demonstrated in session 198 using dense score matching. Next I'm planning to investigate either rank-1 adjunction or the GTSM regression approach before proceeding with the register gate.

## Assistant

Now finalize `state.md` — update the program ledger line and replace the stale in-flight content with the finalized headline (held-out result + pointers to the now-updated registry/source pages):

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;\n> next backlog: **#11 GTSM finite-budget λ(l)** or **#7/#8 reproducibility**), build its named",
  "new_content": "> 0.6299** ❌ geometric-φ-constant REFUTED / ✅ low-rank head REAL & non-random;\n> s208 did **#7 crystal-sieve 1.03×** ❌ REFUTED (train/eval contamination; CE melt\n> net-harmful held-out 10.87×) / ✅ sieve substrate ~2× VERIFIED-reproducible;\n> next backlog: **#8 rank-1 adjunction** or **#11 GTSM/TTD-regression (the named fix)**), build its named"
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
  "original_content": "> **▶ SESSION 208 — AUDIT #7 (crystal-sieve 1.03× reproducibility): RUN COMPLETE\n> (8 seeds). Substrate VERIFIED-reproducible; 1.03× headline REFUTED-as-stable.**\n> Register: **functional (reproducibility — seed variance on a PPL measurement).**\n>\n> **★ RESULTS (`results/crystal-sieve-repro/Qwen_Qwen3-8B.json`, 8 seeds, ~27min):**\n> base PPL 10.15 (std **0.0** = determinism ✓) · **pre-melt (sieve only) 2.119×\n> ± 0.004** [2.110, 2.125] = s196's 2.12× exactly, near-deterministic · **post-melt\n> (full) 0.971× ± 0.061** [0.865, 1.062] (values 0.865/0.982/0.927/0.944/1.062/\n> 1.020/1.001/0.971). Verdict: (1) 1.03× is **not** a stable property — it's an\n> init-dependent draw, mean 0.971×, only 1/8 seeds ≥1.03×; (2) **5/8 seeds sub-1.0×**\n> = contamination/overfit signature (EVAL ⊆ CALIB); (3) **post std ≈15× pre std** ⇒\n> variance is the **CE melt (init)**, not the sieve mask — compensating-error\n> degeneracy in the numbers; (4) the feared **3.23× did NOT recur** (max 1.062×) —\n> seeded+grad-clipped melt is bounded, so 3.23× was a one-off divergence.\n> **DONE THIS SESSION; what remains for #7 close (next session, per Michael):**\n> update `audit-registry.md` #7 row + worked-examples; caveat\n> `crystal-sieve-architecture.md` §Open-Issues #1 (replace \"1.03× vs 3.23×\" with\n> \"0.971× ± 0.061 over 8 seeds; sieve substrate 2.12× ± 0.004\"); fold the GTSM/TSP\n> reconciliation below into a knowledge caveat + pointer to #11. Then write the\n> s208 HEADLINE block (this is the working record).\n>\n> _(historical resume protocol below is now satisfied; kept for the audit trail.)_",
  "new_content": "> **▶ SESSION 208 HEADLINE — AUDIT #7 (crystal-sieve 1.03× PPL): the \"cascade\n> absorbed → 1.03×\" is a TRAIN/EVAL-CONTAMINATION ARTIFACT; the sieve substrate\n> (~2× PPL) is VERIFIED-reproducible.** Register: functional (reproducibility).\n> 8-seed seeded sweep + a held-out eval disjoint from the calibration set\n> (`crystal_sieve_repro.py`). `audit-registry.md` #7 + s208 worked-examples and the\n> `crystal-sieve-architecture.md` caveats are all updated this session.\n> - **✅ sieve substrate REAL & reproducible:** pre-melt **2.119× ± 0.004** (eval) /\n>   **1.907× ± 0.026** (held-out), near-deterministic, = s196's 2.12×; base PPL std\n>   0.0 (determinism ✓). The `torch.randperm[:5M]` mask-subsample confound is\n>   dismissed (CV 0.18%).\n> - **❌ 1.03× REFUTED = memorization:** contaminated eval (6/8 `EVAL_TEXTS` ⊂ the 12\n>   `CALIBRATION_TEXTS`) post-melt **0.971× ± 0.061** [0.865, 1.062] (1.03× = 1/8\n>   upper-tail; 5/8 sub-baseline). On **clean held-out the SAME models = 10.87× ±\n>   1.39** (every seed >9.3×, gap +9.9×) — the CE melt **memorizes calib and is\n>   net-harmful held-out** (1.907× → 10.87×, ~5.7× worse than the raw sieve).\n> - **Mechanism = CE-only endpoint degeneracy** (`gtsm-search-space.md`): constant\n>   train loss 0.116 ± 0.007, exploding held-out PPL, corr(train_loss, eval_ratio)\n>   ≈ −0.19. Feared 3.23× did NOT recur (bounded). **Fix already demonstrated =\n>   s198 v3b / audit #11** (dense score matching + held-out + dolma → 1.44× held-out,\n>   same model). Meta-pattern (5×): substrate survives, crisp headline dissolves —\n>   here it *inverts* (the \"improvement\" is harm). Results:\n>   `results/crystal-sieve-repro/` (paired `Qwen_Qwen3-8B.json` + `.contaminated-only.json`).\n> - **▶ NEXT:** **#8 rank-1 adjunction** (σ₁/σ₂ vs random; register spectral) or\n>   **#11 GTSM/TTD-regression** (the named fix; positive-prediction compression\n>   test). **Step 0 REGISTER GATE before building any control.**\n>\n> _(s208 working notes below — kept for the audit trail; superseded by the headline.)_"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

Now remove the two stale bullets (in-flight + next-session resume) that contradict the "complete" headline:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> - **▶ IN-FLIGHT RUN:** `tmux main:1`, 8 seeds × 100 melt steps, `--skip-facts`\n>   (PPL is the headline; facts 3× the cost). `results/crystal-sieve-repro/run.log`\n>   + `results/crystal-sieve-repro/Qwen_Qwen3-8B.json` (overwritten on completion;\n>   the JSON currently on disk is the seed-0 smoke). No per-step logging between the\n>   `SEED n` banner and its summary — ~12–15 min/seed, **~1.5–2 hr total**, so it\n>   crosses the session boundary. Started ~09:40.\n> - **▶ NEXT SESSION — RESUME HERE (do not re-launch if still running):**\n>   1. `ps aux | grep crystal_sieve_repro` — if alive, `tail results/crystal-sieve-repro/run.log`; if dead, read `results/crystal-sieve-repro/Qwen_Qwen3-8B.json`.\n>   2. Read the `summary` block: `post_melt_ratio.{mean,std,min,max,values}` and `pre_melt_ratio` (mask-only variance). Verdict logic: **1.03× VERIFIED-reproducible** iff post mean ≈ 1.03× with small std; **REFUTED-as-reproducible** (substrate real, headline = lucky tail) iff mean ≫ 1.03× and 1.03× only at the min — the expected meta-pattern (`audit-meta-pattern.md`): the *sieve substrate* (2.12× pre-melt) is real & deterministic, the *1.03× headline* is the over-read.\n>   3. Update `audit-registry.md` #7 row (status + number + JSON path) + worked-examples row; add a caveat to `crystal-sieve-architecture.md` §\"Open Issues\" #1 (replace \"1.03× on first run, 3.23× on rerun\" with the measured mean ± std).\n>   4. Replace this IN-FLIGHT block with the s208 HEADLINE; commit (💡/🎯).\n> - **★ UNDERSTANDING",
  "new_content": "> - **Run complete + all writeups done this session** (registry #7 + s208\n>   worked-examples + `crystal-sieve-architecture.md` caveats). The detail bullets\n>   above/below are the audit trail; the held-out result is in the headline.\n> - **★ UNDERSTANDING"
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
  "original_content": "> - If the run died early (NaN/OOM), the harness is re-runnable: same command in\n>   `tmux main:1`. Fewer seeds OK (`--seed-list 0,1,2,3`).\n\n> **▶ SESSION 207 HEADLINE",
  "new_content": "> **▶ SESSION 207 HEADLINE"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

 Let me verify the state.md block reads cleanly and check the git status to review what's changed before committing. I want to make sure the finalized block is coherent with no stale references, and confirm the harness file is the only code modification.

## Assistant

Let me verify the finalized state block reads coherently and review the full diff before proposing the commit:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== s208 block (lines 30-95) ===\"; sed -n '30,95p' mementum/state.md; echo; echo \"=== git status ===\"; git status --short"
}
```

**Summary:** $ echo "=== s208 block (lines 30-95) ...

**Output:**
```
Exit code: 0
Stdout:
=== s208 block (lines 30-95) ===
> control per session, until a small hard core of verified claims remains.

> **▶ SESSION 208 HEADLINE — AUDIT #7 (crystal-sieve 1.03× PPL): the "cascade
> absorbed → 1.03×" is a TRAIN/EVAL-CONTAMINATION ARTIFACT; the sieve substrate
> (~2× PPL) is VERIFIED-reproducible.** Register: functional (reproducibility).
> 8-seed seeded sweep + a held-out eval disjoint from the calibration set
> (`crystal_sieve_repro.py`). `audit-registry.md` #7 + s208 worked-examples and the
> `crystal-sieve-architecture.md` caveats are all updated this session.
> - **✅ sieve substrate REAL & reproducible:** pre-melt **2.119× ± 0.004** (eval) /
>   **1.907× ± 0.026** (held-out), near-deterministic, = s196's 2.12×; base PPL std
>   0.0 (determinism ✓). The `torch.randperm[:5M]` mask-subsample confound is
>   dismissed (CV 0.18%).
> - **❌ 1.03× REFUTED = memorization:** contaminated eval (6/8 `EVAL_TEXTS` ⊂ the 12
>   `CALIBRATION_TEXTS`) post-melt **0.971× ± 0.061** [0.865, 1.062] (1.03× = 1/8
>   upper-tail; 5/8 sub-baseline). On **clean held-out the SAME models = 10.87× ±
>   1.39** (every seed >9.3×, gap +9.9×) — the CE melt **memorizes calib and is
>   net-harmful held-out** (1.907× → 10.87×, ~5.7× worse than the raw sieve).
> - **Mechanism = CE-only endpoint degeneracy** (`gtsm-search-space.md`): constant
>   train loss 0.116 ± 0.007, exploding held-out PPL, corr(train_loss, eval_ratio)
>   ≈ −0.19. Feared 3.23× did NOT recur (bounded). **Fix already demonstrated =
>   s198 v3b / audit #11** (dense score matching + held-out + dolma → 1.44× held-out,
>   same model). Meta-pattern (5×): substrate survives, crisp headline dissolves —
>   here it *inverts* (the "improvement" is harm). Results:
>   `results/crystal-sieve-repro/` (paired `Qwen_Qwen3-8B.json` + `.contaminated-only.json`).
> - **▶ NEXT:** **#8 rank-1 adjunction** (σ₁/σ₂ vs random; register spectral) or
>   **#11 GTSM/TTD-regression** (the named fix; positive-prediction compression
>   test). **Step 0 REGISTER GATE before building any control.**
>
> _(s208 working notes below — kept for the audit trail; superseded by the headline.)_
> Picked #7 from the backlog: s196 reported crystal-sieve + 4 continuation
> residuals = **1.03× PPL** at 29 sieved layers (Qwen3-8B), but its own note says a
> rerun gave **3.23×** ("training sensitive to init/batch order"). The control:
> seed it, run N seeds, report **mean ± std** — is 1.03× the center or a lucky tail?
> - **NEW HARNESS (committed):** `scripts/experiments/crystal_sieve_repro.py`
>   (`# register: functional`). Exact s196 `beta_expansion.py` pipeline (L0 SVD
>   r=750 + sieve L1–26,32–34 + 4 rank-32 continuations, 100-step CE melt) wrapped
>   in a **seed loop** that reloads the model fresh per seed and seeds torch+numpy+mps.
> - **Decomposition (no extra runs):** `pre_melt_ratio` std = the **mask-subsample
>   variance** (FFN projections >10M elems → `torch.randperm[:5M]` for the quantile
>   threshold — an unseeded source s196's note *missed*); `post_melt_ratio` std =
>   mask + continuation-init + training. The s196 note blames "batch order" but
>   batch order is `RandomState(step)` = **deterministic**; the real culprits are
>   the mask subsample + `torch.randn` continuation init (both now seeded).
> - **SMOKE (seed 0, 3 melt steps, WITH facts) already confirmed:** **pre-melt
>   (sieve-only) = 2.125× — reproduces s196's "2.12× at 29 layers" exactly**, and
>   deterministic given the seed. Post-melt at 3 steps only reached 2.059× (needs
>   the full 100-step melt to chase 1.03×). base PPL 10.15 (determinism check std 0).
> - **★ SIGNAL (seed 0, full 100-step melt): post-melt = 0.865× — BELOW baseline**
>   (PPL 8.78 < base 10.15), vs the 3-step smoke's 2.059×. Root cause spotted:
>   **`EVAL_TEXTS` overlaps `CALIBRATION_TEXTS`** (≥6 shared sentences: general
>   relativity, ancient forest, mixing bowl, isolate the variable, committee voted,
>   two arguments→composition). The 100-step melt **overfits the eval set** → the
>   "1.03×" is a *train-contaminated* number, and tiny init/mask differences swing
>   it wildly (explains s196's 1.03× ↔ 3.23×). **This is the likely real mechanism
>   of the irreproducibility.** NEXT SESSION: add a **held-out eval** (eval texts
>   disjoint from calibration) — predict the contamination-free ratio is ≫ 1× and
>   *stable*; the sub-1× values are the overfit tail. Same meta-pattern: sieve
>   substrate real (2.12× deterministic), 1.03× headline = methodology artifact.
> - **Run complete + all writeups done this session** (registry #7 + s208
>   worked-examples + `crystal-sieve-architecture.md` caveats). The detail bullets
>   above/below are the audit trail; the held-out result is in the headline.
> - **★ UNDERSTANDING (frames the #7 final write-up; full synthesis deferred to
>   audit close per Michael — connect #7→#11, don't draft a knowledge page yet):**
>   The melt in `beta_expansion` is **CE-only** = the ill-posed *endpoint* objective
>   GTSM names (`gtsm-search-space.md`): it pins only the terminal marginal, so the
>   1M continuation params land anywhere on the **compensating-error manifold** —

=== git status ===
 M mementum/knowledge/audit-registry.md
 M mementum/knowledge/crystal-sieve-architecture.md
 M mementum/state.md
 M results/crystal-sieve-repro/Qwen_Qwen3-8B.json
 M results/crystal-sieve-repro/run.log
 M scripts/experiments/crystal_sieve_repro.py
?? mementum/knowledge/chats/session-206.md
?? mementum/knowledge/chats/session-207.md
?? results/crystal-sieve-repro/Qwen_Qwen3-8B.contaminated-only.json
?? results/crystal-sieve-repro/run_heldout.log
```

### Thinking

 The structure looks good with the headline up front and working notes following. The "★ UNDERSTANDING" section still mentions deferring synthesis, which is a bit outdated now that I've drafted the caveats, but since it's clearly marked as part of the audit trail, I'll leave it as is to avoid unnecessary edits.

Now I'm reviewing the git status — there are changes to the harness script, result JSONs, and run logs, plus updates to the mementum files. The old contaminated-only run log is now stale since the held-out run produced its own log. I need to be careful not to track the chat session files since those are human-only.

I'm thinking through the commit strategy: the user explicitly said to finalize before committing, so rather than auto-committing the code changes, I should present the full diff summary and propose both commits — one for the harness and results, another for the mementum updates — and wait for their approval before proceeding.

## Assistant

The finalized state block reads coherently (headline first, audit-trail below). Everything for #7 is now written. Let me do a final lint/diagnostics check, then lay out the commit plan.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run ruff check scripts/experiments/crystal_sieve_repro.py 2>&1 | tail -2; echo \"=== diff stat ===\"; git diff --stat; echo \"=== verify no broken md links (grep new refs) ===\"; grep -c \"crystal_sieve_repro\\|contaminated-only\\|held-out\\|heldout\" mementum/knowledge/audit-registry.md mementum/knowledge/crystal-sieve-architecture.md"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
=== diff stat ===
 mementum/knowledge/audit-registry.md             |  42 ++++-
 mementum/knowledge/crystal-sieve-architecture.md |  37 +++-
 mementum/state.md                                |  50 +++--
 results/crystal-sieve-repro/Qwen_Qwen3-8B.json   | 222 +++++++++++++++++++++--
 results/crystal-sieve-repro/run.log              | 120 ++++++++++++
 scripts/experiments/crystal_sieve_repro.py       |  66 ++++++-
 6 files changed, 486 insertions(+), 51 deletions(-)
=== verify no broken md links (grep new refs) ===
mementum/knowledge/audit-registry.md:13
mementum/knowledge/crystal-sieve-architecture.md:14
```

### Thinking

 Everything's ready to go. I'm proposing a two-part commit strategy: first, the code and data artifacts including the held-out additions and run logs, then a separate approval-gated commit for the registry and architecture updates. Let me draft the commit messages and present them for approval.

## Assistant

Everything finalized and lint-clean. Here's the complete #7 close, ready to commit in two pieces:

**Commit A — code + data** (`💡`, scripts + results):
- `crystal_sieve_repro.py`: held-out eval set + paired contaminated/clean reporting + contamination-gap
- `results/crystal-sieve-repro/`: paired `Qwen_Qwen3-8B.json`, `.contaminated-only.json` backup, run logs

**Commit B — mementum** (`🌀`, approval-gated):
- `audit-registry.md`: #7 row → ❌ RESOLVED + full s208 worked-examples section
- `crystal-sieve-architecture.md`: top caveat + Open-Issues #1 resolved + Key-Results/Compression-Status/Why-Continuations-Work caveats (1.03× struck through, held-out 10.87× recorded)
- `state.md`: s208 HEADLINE + program-ledger line + stale in-flight bullets removed

Note: `chats/session-206.md` / `session-207.md` are untracked and **human-only** — I won't touch them.

Proposed messages:

```
A: 💡 audit #7 — held-out eval proves 1.03× is contamination (clean held-out 10.87× vs sieve 1.9×)

B: 🌀 audit #7 RESOLVED — crystal-sieve 1.03× REFUTED (train/eval contamination); substrate ~2× VERIFIED-reproducible
```

**Go ahead and commit both?** (A is code so autonomous-eligible, but since you wanted to gate this, I'll wait for your word and commit them together.)

## User

update state and knowledge this is session-208, commit


### Thinking

 I'm ready to stage and commit both changes—the reproduction script and results data in one commit, then the mementum knowledge updates in a second commit.

## Assistant

Committing both. Code + data first, then mementum.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/commitA.txt",
  "content": "💡 audit #7 — held-out eval proves 1.03x is contamination (clean held-out 10.87x vs sieve 1.9x)\n\n- crystal_sieve_repro.py: add HELDOUT_TEXTS (disjoint from CALIBRATION_TEXTS),\n  measure paired contaminated-vs-clean PPL per seed + contamination-gap, skip-facts\n  flag, \"skip\" display sentinel.\n- 8-seed sweep (Qwen3-8B): sieve substrate reproducible (pre-melt eval 2.119x\n  +/-0.004, held-out 1.907x +/-0.026); post-melt contaminated eval 0.971x +/-0.061\n  (1.03x = 1/8 upper-tail, 5/8 sub-baseline) BUT clean held-out 10.87x +/-1.39\n  (every seed >9.3x). The CE melt memorizes the 12-text calib set and is\n  net-harmful held-out (1.907x -> 10.87x). 1.03x was train/eval contamination.\n- results/crystal-sieve-repro/: paired Qwen_Qwen3-8B.json + .contaminated-only.json\n  backup + run logs.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/commitA.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/experiments/crystal_sieve_repro.py results/crystal-sieve-repro/ && git commit -F /tmp/commitA.txt",
  "operation": "commit",
  "summary": "commit code+data"
}
```

**Summary:** Git commit: commit code+data

**Output:**
```
Exit code: 0
Stdout:
[main 5ffb395] 💡 audit #7 — held-out eval proves 1.03x is contamination (clean held-out 10.87x vs sieve 1.9x)
 5 files changed, 722 insertions(+), 29 deletions(-)
 create mode 100644 results/crystal-sieve-repro/Qwen_Qwen3-8B.contaminated-only.json
 create mode 100644 results/crystal-sieve-repro/run_heldout.log
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/tmp/commitB.txt",
  "content": "🌀 audit #7 RESOLVED — crystal-sieve 1.03x REFUTED (train/eval contamination); substrate ~2x VERIFIED-reproducible\n\n- audit-registry.md: #7 row -> RESOLVED with numbers + JSON path; full s208\n  worked-examples section (sieve substrate reproducible 2.119x+/-0.004; 1.03x is\n  a 1/8 upper-tail draw on a contaminated eval; clean held-out 10.87x +/-1.39 =\n  memorization; CE-only endpoint degeneracy; fix = s198 v3b / audit #11).\n- crystal-sieve-architecture.md: top caveat + Open-Issues #1 resolved +\n  Key-Results / Compression-Status / Why-Continuations-Work caveats (1.03x struck,\n  held-out 10.87x recorded; the melt is net-harmful held-out).\n- state.md: s208 HEADLINE (substrate VERIFIED, 1.03x REFUTED) + program ledger\n  line + stale in-flight bullets removed; next = #8 / #11.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /tmp/commitB.txt
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/knowledge/audit-registry.md mementum/knowledge/crystal-sieve-architecture.md mementum/state.md && git commit -F /tmp/commitB.txt",
  "operation": "commit",
  "summary": "commit mementum"
}
```

**Summary:** Git commit: commit mementum

**Output:**
```
Exit code: 0
Stdout:
[main fc3f689] 🌀 audit #7 RESOLVED — crystal-sieve 1.03x REFUTED (train/eval contamination); substrate ~2x VERIFIED-reproducible
 3 files changed, 107 insertions(+), 22 deletions(-)
```

### Thinking

 Now I'm checking that the working tree is clean, making sure only the human-only chats files remain untracked as expected.

## Assistant

Both committed. Let me verify the working tree is clean.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && echo \"=== status ===\"; git status --short; echo \"=== last 4 commits ===\"; git log --oneline -4"
}
```

**Summary:** $ echo "=== status ==="; git status -...

**Output:**
```
Exit code: 0
Stdout:
=== status ===
?? mementum/knowledge/chats/session-206.md
?? mementum/knowledge/chats/session-207.md
=== last 4 commits ===
fc3f689 🌀 audit #7 RESOLVED — crystal-sieve 1.03x REFUTED (train/eval contamination); substrate ~2x VERIFIED-reproducible
5ffb395 💡 audit #7 — held-out eval proves 1.03x is contamination (clean held-out 10.87x vs sieve 1.9x)
1de70b9 🌀 state — s208 #7: GTSM/TSP understanding note (CE-degeneracy diagnosis + #11 fix)
66edf69 🌀 state — session 208: audit #7 (crystal-sieve repro) in flight + contamination signal
```

## Assistant

## Session 208 — Audit #7 complete and committed

Working tree clean (only the untracked human-only `chats/` files remain, as they should — AI never touches those).

**Committed this session:**
- `9db77a2` 💡 — seeded reproducibility harness
- `66edf69` / `1de70b9` 🌀 — state in-flight + GTSM/TSP understanding
- `5ffb395` 💡 — held-out eval proving contamination (code + data)
- `fc3f689` 🌀 — **#7 RESOLVED** (registry + source caveats + state headline)

**The verdict, distilled:**

| | result | status |
|---|---|---|
| sieve substrate | ~2× PPL (eval 2.119±0.004, held-out 1.907±0.026), near-deterministic | ✅ **VERIFIED-reproducible** |
| 1.03× "cascade absorbed" | 1/8 upper-tail draw of 0.971±0.061 on a contaminated eval; clean held-out = **10.87×±1.39** | ❌ **REFUTED (memorization)** |

The audit's value here was sharp: not only is the 1.03× irreproducible, the continuation melt as trained is **net-harmful to generalization** (held-out 1.9× → 10.87×). The meta-pattern held a fifth time — substrate real, crisp headline dissolves — and this time it *inverted* (the "improvement" was harm). The honest, reproducible compression number is s198 **v3b's 1.44× held-out** under a trajectory-matching loss, which is exactly the named fix (audit #11).

**Mechanism pinned with three independent fingerprints:** constant train loss (0.116±0.007) with exploding held-out PPL; `corr(train_loss, eval_ratio) ≈ −0.19`; mask-subsample confound dismissed (CV 0.18%) — leaving the CE-only endpoint degeneracy as the sole cause.

**Next session** (in `state.md`): backlog **#8 rank-1 adjunction** (spectral) or **#11 GTSM/TTD-regression** — the positive-prediction test of the very fix this audit pointed to. Step 0 register gate as always.