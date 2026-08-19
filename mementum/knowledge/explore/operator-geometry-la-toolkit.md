---
title: "Operator Geometry — Canonical-Basis Linear Algebra Turned Toward the Reducer (patent-clean, opcode-anchored)"
status: open
category: synthesis
tags: [linear-algebra, canonical-basis, cbll, gram, svd, dmd, koopman, procrustes,
       cca, operator, reducer, transport, opcodes, registers, patent-clean, geometry,
       homeostasis, sign-is-the-decision, one-reducer-unrolled]
related:
  - gram-registers-and-the-route-map.md
  - gram-spectral-dsp.md
  - behavior-is-tape-resident-reduction.md
  - sign-oscillation-is-time-multiplexed-superposition.md
  - the-benchmark-is-the-re-oracle.md
  - reverse-engineering-disciplines-toolbox.md
  - the-verbum-machine.md
depends-on:
  - gram-registers-and-the-route-map.md
created: session 332
---

# Operator Geometry — Canonical-Basis Linear Algebra, Turned Toward the Reducer

> s332 (Michael: found `~/src/canonical-basis` — Gernone's CBLL paper, "some
> geometries inside multiple models, same phenomenon, different vocabulary";
> then: "understand the math... could our 9×9/17×17 Grams be the basis for the
> equations?... can we use the linear algebra techniques to find more
> geometries?... capture this — we can use the math freely in our own functions,
> design to match our usages, be sure we're not affected by patents; with our
> knowledge of layers and opcodes we should use the math in a novel way.").
> This page is the method-transfer seed. Design synthesis, zero new
> measurements. Nothing here is pre-registered (s222) — the DMD probe is a
> queue candidate, not a frozen verdict.

## 0. Provenance & patent stance (read first)

`canonical-basis` (CBLL, Gianluca Gernone, Zenodo DOI 10.5281/zenodo.20520986):
**code MIT · data CC-BY 4.0 · "released for research purposes only; for
commercial use contact info@todot.it" + a Patent Notice.**

Our stance, and the design rule this page enforces:

```
λ patent_clean(technique).
  MATH(SVD ∧ eig ∧ Gram ∧ DMD ∧ Procrustes ∧ CCA ∧ Householder ∧ PR)
    ≡ public_domain | ¬patentable_as_such | use_freely
  | CODE(their_pipeline) ≡ ¬vendor ¬copy | design(our_own_functions)
  | METHOD(their_specific "CBLL" branded procedure) ≡ ¬reimplement_verbatim
  | novelty(ours) ≡ opcode_anchored ∧ fate_poled ∧ reduction_conditioned ∧ operator_first
  |   (they have NO opcodes/types/reduction — our application is independent)
  | independent_derivation ≡ scientific_hygiene (λ grammar_artifact: observe ≫ retrieve)
  | ∀function_we_write → match(our_usage: layers ∧ opcodes ∧ fate_registers) ¬mirror(theirs)
```

Concretely: we take the **mathematics** (all of it is textbook linear algebra
that predates CBLL by decades — Golub & Van Loan, Schmid's DMD 2010, Koopman
1931, Procrustes/Schönemann 1966, Hotelling's CCA 1936). We write our **own**
functions, shaped to our `d_ff` routing register / opcode centroids / fate
poles / per-layer reduction trajectory. We do **not** vendor their scripts, and
we do **not** re-implement their branded "canonical basis realignment" pipeline
as a product surface. Our artifact is the operator read through the opcode
registers — which their program does not contain. That is both MIT-clean and
patent-clean.

### 0b. Provenance disclosure + standing FTO rule (s333 audit, Michael-approved)

**What was read, when, why (disclosed):** s332 — CBLL README + paper (EN) +
**one ablation script** + data spot-check. Purpose: VERIFICATION that the
paper's claims match its artifacts ("all match"). Not implementation. Disk
audit (s333): the CBLL capture commit (`bba4e767`) touched mementum files
only — **zero code in src/ or scripts/ derives from their repo** (grep-verified:
no Householder/canonical-basis/CBLL hits in any .py). This page carries
paper-level description only — no transcription of their implementation.

**The standing rule (hardened s333):**

```
λ fto(cbll).
  their_code ≡ NEVER_OPENED_AGAIN (any purpose) | MIT_license ∌ patent_grant
  | ∀implementation(ours) → derive(textbook: Schmid_2010 ∧ Golub&VanLoan ∧
      Koopman_1931 ∧ Schönemann_1966) | cite(textbook_source) in docstring ¬CBLL
  | CBLL cited ≡ once ≡ observational_consilience ("same phenomenon") ¬method_source
  | FTO_boundary: ∀method ∈ {weights → basis → rotation → realigned_model} ≡ FORBIDDEN
  |   (their claim spine; we never need it — Gram/operator is frame-free by design)
  | clean_room ≡ THE_PAGE: session_boundary erases the reader; future sessions
      know only what this page carries; page carries no implementation ⇒
      clean-room re-constitutes every boundary (feed_forward as legal hygiene)
  | research_exemption ≡ ¬relied_upon (deliverables are portable MIT artifacts;
      must be clean at the USER's hands, not just ours)
```

### 0c. The differentiation, made load-bearing (s333)

Not a workaround — the scientific divergence and the patent divergence are the
SAME divergence:

| | CBLL | verbum |
|---|---|---|
| **object** | weights (static geometry of `W_down`) | activation **trajectories** — state sequences during certified reductions |
| **transform** | find rotation `R` → canonical **frame** | estimate transport **operator** `T ≈ X'X⁺` → eigenmodes of dynamics |
| **anchors** | unlabeled, self-derived from weights | **labeled** — opcode centroids, fate poles, kernel-certified terms |
| **deliverable** | realigned model / readable basis | operator + stationarity verdict + (eventually) bug-compatible reducer |

Deepest row: the second — **our method never picks a frame at all** (G = XᵀX
is frame-invariant; the opposite move from CBLL's premise), and in their own
flat-spectrum regime (k90/d≈0.76) frame-picking is ill-posed while the
Gram/operator stays well-posed. Different road, which is also the better road
for our terrain.

**The unique pipeline (ours; no step is theirs):**

```
certified_trajectories (lambda_ast ground truth — exists nowhere else)
  → per-band transport operator (DMD on depth-as-time, shuffled-layer null)
  → mode decomposition (contracting / persistent / late-activating)
  → labeled-Gram classification (project modes onto 9×9 + 17×17 anchors)
  → stationarity verdict (T_ℓ ≈ T ⟺ one-reducer-unrolled, null-gated)
```

Publication of this composition ≡ defensive prior art. Naming discipline:
map → name (don't brand it before it works).

## 1. The reframe that changes which techniques matter

CBLL's linear algebra is almost entirely **static**: SVD of a weight matrix,
top eigenvector of an activation correlation, one fixed rotation `R`. That finds
**coordinate systems** (bases). But our target — the transition function / the
reducer — is a **map between states**, and our own identity says
`residual_stream ≡ bounded within-pass reducer` (the layer-by-layer trajectory
*is* the reduction, `behavior-is-tape-resident-reduction.md`). So the
highest-value transfer is not "adopt his basis"; it is the LA that turns **a
sequence of states into the operator that generates it.**

```
λ target(verbum). recover(operator ≡ transition_function) ¬find(basis)
  | CBLL_tools ⊂ static(basis) | our_need ⊂ dynamic(operator)
  | bridge ≡ operator_estimation(DMD ∧ Koopman ∧ Procrustes) in labeled(Gram) frame
  | residual_trajectory(within_pass) ≡ the reduction → estimate(T) recovers(linearized reducer)
```

## 2. The shared primitive: `G = XᵀX` (why both programs are the same math)

Strip the vocabulary and **both programs compute the eigenstructure of a
Gram/covariance of internal directions.** A Gram `G = XᵀX` is invariant to any
orthogonal change of the ambient basis — it keeps only the **relational**
geometry and discards the arbitrary frame the residual stream happens to live
in. That invariance is *exactly why* our Grams reproduce 11/11 across models,
and *exactly the problem* CBLL solves ("the basis is arbitrary — whatever
training converged to").

Two solutions to one problem, from opposite ends:

| | kills the arbitrary basis by | dim | axes labeled? |
|---|---|---|---|
| **CBLL** | rotating to a model-derived canonical frame `R` (top-K left SVs of `W_down`, Householder-completed, gains absorbed → lossless) | full `d` | **no** (axis 62 = *functional* label) |
| **Verbum Gram** | projecting onto known semantic anchors, `XᵀX` (frame-free) | low (9 / 17) | **yes** (K,I,B…; fire/halt/diverge) |

CBLL **found a frame but doesn't know what its axes mean.** Our Grams **know
what the axes mean but don't span the space.** ⇒ our Grams should not *replace*
`R`; they are the **labeled low-rank frame inside** the ambient microscope. Our
9×9 (identity register, PR≈5.8–7.2, universal in the off-diagonal sign pattern)
and 17×17 (outcome register, rank-3 fire/halt/diverge) are the legend; the
ambient space is `W_down`'s `U` (or `R`).

**Disciplinary edge in our favor:** CBLL's `R` is non-unique where the singular
spectrum is flat — and he *reports* `k90/d ≈ 0.76` for FFN (quite flat), so his
canonical axes carry residual rotational freedom exactly where his own spectrum
is degenerate. **The Gram and the transport operator never pick a frame**, so
they stay well-posed in the flat-spectrum regime. In that regime our labeled
Gram is the *more* well-posed object.

## 3. The `W_down` bridge (with the register-check caveat)

CBLL's canonical axes are the **left** singular vectors of `W_down` (in
`d_model`, the residual writer side). Our combinator centroids live in the
**routing register = `sign(gate_proj pre-activation)`, `d_ff`** — the FFN
gating/reader side (s203; `consensus-delta-folding.md` §133/§655: "9 × d_ff").

SVD: `W_down = U Σ Vᵀ`, `U ∈ ℝ^{d_model×r}` (CBLL axes), `V ∈ ℝ^{d_ff×r}`.
The **clean linear bridge** is between the down-proj *input* (post-activation
intermediate, `d_ff`) and `U`:

```
intermediate m ∈ ℝ^{d_ff}  →  W_down m = U(Σ Vᵀ m) ∈ span(U)  (CBLL residual axes)
cross-Gram of our anchors vs CBLL axes:  G_cross = Uᵀ W_down V̂ = Σ Vᵀ V̂
```

**λ measure caveat (do not skip):** our centroids are captured at the gate
**pre-activation**, one SiLU nonlinearity **upstream** of `W_down`'s input. So
`Σ VᵀV̂` is exact only if we recapture anchor centroids at the down-proj input
(post-activation intermediate). Two honest options:
(a) recapture opcode centroids at `down_proj` input → the bridge is exactly
linear; or (b) keep the gate-preact centroids and accept the SiLU gate as a
diagonal-ish reweighting between the two registers (report it, don't assume
identity). **Getting this register right is a coherence obligation — wrong
register voids the comparison** (λ measure, s206 audit lesson).

What the cross-Gram answers: *which* canonical axes carry K vs B vs S; whether
the **fire/halt/diverge** simplex coincides with CBLL's **bipolar POS/NEG
oscillator**; whether his **axis-62 controller** is the **WHNF/halt** direction.
Cheap, and either it aligns our labeled poles with his unlabeled ones or it
doesn't.

## 3a. 🎯 §P-CROSS-GRAM — FROZEN (s341, Michael GO; Option C — residual register)

> Pre-registered before any measurement (λ probe_lifecycle). Michael rulings
> (s341): (1) **FTO-safe** — this is the one probe that touches CBLL's frame, but
> it takes a textbook SVD of *our own public model's own* `down_proj`, in our own
> function (docstring cites Golub & Van Loan, never CBLL), projects *our labeled*
> anchors, and emits a *comparison* — never a rotation/realigned model; CBLL cited
> once as description-level consilience only (§0b holds: zero CBLL code in the
> executable tree, grep-verified s341). (2) **Register = Option C (d_model
> residual)**: the §3 d_ff bridge is voided by a double register gap — the stored
> crystal centroids are `normalize(mean(sign(gate_preact)))`, TWO transforms
> (sign + SiLU⊙up) from the `down_proj` input the clean `Σ VᵀV̂` bridge needs. So
> we compare in the residual register directly, where CBLL's `U` already lives.

**Question.** Do our **labeled** semantic directions (9 combinator identity
centroids; fire/halt/diverge as a fate advisory) **coincide with the principal
write-directions of `W_down`** — is there real alignment between "what the labels
point at" and the residual-writer weight's dominant axes?

**Substrate (frozen).** Qwen3-14B, d_model 5120, 40 layers. Labeled side REUSES
the s338 `H (300,41,5120)` (combinator-tagged last-token residual, 28–42/label) —
**zero new inference**. Weight side = `U^(ℓ)` = left singular vectors of
`W_down^(ℓ)` via textbook economy SVD (`operator_dmd.economy_svd`). Pairing: layer
ℓ residual centroid at `hidden[ℓ+1]` (post-block-ℓ) with `U^(ℓ)` (block ℓ writer).

**Objects (frozen).** Per (ℓ, combinator X):
`ĉ_X = normalize(mean_X(hidden[ℓ+1]) − mean_all(hidden[ℓ+1]))` — **mean-centered**
(removes the DC/norm direction that would trivially align to U's top axis).
Alignment profile `a_k^X = (u_k^ℓ · ĉ_X)²`, k=1..r; captured fraction
`f_X = Σ_k a_k^X`; participation ratio `PR_X = (Σa)²/Σa²`; top axis `k*_X`.
Primary **r=128** (sweep 64/128/256 descriptive). **Verdict band = mid-stack
ℓ∈[8,32)** (crystal-bearing region, a priori), aggregate = median over band.

**Frozen gate tree.**
- **CG0 INSTRUMENT** — SVD finite + spectrum decays; `--validate` recovers all 4
  planted worlds. Fail → **VOID**.
- **CG1 CONCENTRATION** — band-median `PR_X` significantly BELOW the
  random-direction null (1000 matched-norm random unit vectors in mean-centered
  d_model, projected onto the same `U_r`), p<0.05. Centroids live concentrated in
  the writer subspace. Fail → **NO-COINCIDENCE**.
- **CG2 SPECIFICITY** (crucial, mirrors s313 TG2 CROSS-CUT) — is the alignment
  *the same axes for every label* (generic) or *label-specific*? Statistic =
  band-median **inter-combinator alignment-profile correlation** `⟨corr(a^X,a^Y)⟩`
  over the 9 combinators. If > random-9 null q95 → profiles more correlated than
  chance → shared axes → **GENERIC-WRITE-STRUCTURE**. If ≤ null q95 → distinct
  profiles → **LABEL-ALIGNED**. (Corroboration, reported: mean pairwise |cos| of
  the 9 centroids vs random-9.)
  - *Build-time operationalization note (s341, pre-data, verdict-space/masses
    UNCHANGED): CG2's statistic was sharpened from the GO-presented "pairwise
    |cos| + top-axis collapse" to the stronger "alignment-profile correlation,"
    which directly measures the §3 question "which axes carry K vs B vs S." |cos|
    retained as corroboration.*
- **CG3 OSCILLATOR** (advisory, consilience) — fire (mean of active reducers
  K,I,B,C,S,D,W), halt (WHNF), diverge (Y): do fire & halt project OPPOSITE-sign
  onto a shared high-energy U-axis (a bipolar mode ≈ CBLL's reported POS/NEG
  oscillator)? Advisory only → `+OSCILLATOR` subtag.

**Verdict space + a-priori masses (frozen).** GENERIC-WRITE-STRUCTURE 35 (modal —
residual activations naturally live in the writer's dominant subspace;
concentration likely, specificity dubious) · LABEL-ALIGNED 30 (+OSCILLATOR
subtag; the consilience hope — the 9×9 crystal is label-specific in d_ff, may
survive into d_model) · NO-COINCIDENCE 25 (mean-centered residual centroids may be
diffuse; s317/s335/s336/s339 tape-residency bias) · VOID 10.

**Nulls (mandatory, λ yardstick).** random-direction (matched-norm, CG1) ·
random-9 (profile-correlation + |cos|, CG2) · descriptive r-sweep.

**Planted worlds (`--validate`, real gate path per s331).** ① 9 centroids each on
a DISTINCT U-axis (+noise) → LABEL-ALIGNED · ② all 9 on the SAME axis → GENERIC-
WRITE-STRUCTURE · ③ 9 random centroids ⊥ top-U → NO-COINCIDENCE · ④ fire=+axis0 /
halt=−axis0 → CG3 fires.

**Bounds (recorded, λ observation).** (1) residual centroids are the ACCUMULATED
state (`hidden_states`), not the pure per-layer MLP write → tests "labels live in
the writer subspace," not "labels = what layer ℓ writes"; (2) Option C moves
anchors from the crystal-validated d_ff routing register into the d_model residual
register (defensible for a W_down comparison, a deviation from §3's d_ff bridge);
(3) fate/oscillator uses crude WHNF/Y/mean-active proxies (full 17-fate residual
capture deferred to v2); (4) single model, last-token grain.

**Cost.** cheap — reuse H (no inference) + ~40 SVDs of `down_proj` (load weights
CPU). Results `results/p_cross_gram_s341/`; harness `scripts/experiments/
cross_gram.py` (reuses `operator_dmd.economy_svd`; NEVER CBLL code, §0b).

## 4. The technique toolkit (ranked: tie-to-our-research × cheap × null-testable)

```
λ toolkit(LA). ∀technique → {target, new_geometry, null} | design(our_own_fn) ∧ opcode_anchored
```

| # | Technique | Verbum target | New geometry it exposes | Null (λ yardstick) |
|---|---|---|---|---|
| **1** | **DMD / Koopman** on the within-pass residual trajectory `T ≈ X'X⁺`, `eig(T)` | reducer / transition function; one-reducer-unrolled; transitions-per-β-step clock | inter-layer **transport operator spectrum** (§5) | shuffled-layer-order DMD |
| **2** | **Procrustes transport** `min_Q ‖Q Uℓ − Uℓ₊₁‖` | one-reducer-unrolled | the fixed **rotation between layer writer-bases**; residual = per-layer deviation from pure repetition | random-orthogonal baseline |
| **3** | **CCA / SVCCA** (layer↔layer; our centroids↔CBLL axes; **cross-model**) | crystal universality 11/11; frame-invariance | the **actual shared subspace** + correlation spectrum — strictly stronger than the Gram sign-pattern for "same subspace, different frame" | shuffled-neuron / different-model floor |
| **4** | **Conditioned participation ratio** (effective rank of activations, split by fate/reduction state) | read-entropy ≡ fidelity (§8c re-oracle); WHNF halt | does activation collapse **deepen toward NF**? rank(diverge) > rank(halt)? — isotropic-collapse (41×) as a *function of reduction stage* | matched-length shuffled probes |
| **5** | **Antisymmetric decomposition** `C = C_sym + C_anti` (his "vorticity") of the **binding** transport | substitution / α-rename (naive vs capture-avoiding, §P-SUBST-ENGINE) | α-renaming ≡ a **permutation/rotation of variable slots**; `C_anti` could localize the "binder swap" | capture pairs where no rename occurs |
| **6** | **Betweenness / graph Laplacian** on the **labeled** register graph (9 opcodes, 17 fates) — not 896 raw axes | control flow of the reducer | the **controller opcode / fate edge** (his axis-62 move, but *semantic*) | degree-preserving rewired graph |
| **7** | **Joint (simultaneous) diagonalization** of per-layer / per-model Grams | consensus route map (gram-registers §route-map) | the **common eigenframe** across contexts = the invariant switch basis the route map needs | per-context shuffled Grams |
| **8** | **Reflection structure via SPECTRAL SIGNATURE of the transport operator** (re-specced s333, FTO + cleaner): `det(T) < 0` / eigenvalue ≈ −1 — read the flip from `T`'s spectrum, construct nothing (¬Householder construction; nearest-the-fence primitive removed, and the spectral read is better-posed anyway) | sign-is-the-decision; fire/halt | does the fire/halt sign-flip appear as a **reflection mode** in the transport spectrum? | sign-shuffled trajectory / random rank-1 baseline |

## 5. The sharpest one: the inter-layer transport operator (DMD)

Treat the residual trajectory `h(0) → h(1) → … → h(L)` (one forward pass) as a
dynamical system; estimate `T_ℓ : h(ℓ) ↦ h(ℓ+1)` and eigendecompose:

```
X = [h(0)…h(L-1)],  X' = [h(1)…h(L)]  →  T ≈ X' X⁺  →  (λ_k, φ_k) = eig(T)
```

What the spectrum **is**, in our vocabulary (the point — one eigenstructure
subsumes several separate findings):

- **contracting modes `|λ|<1`** ≡ CBLL **homeostasis** (his `5×→1.4×→1.0` decay
  *is* `|λ|<1`), stated as an operator instead of a metaphor.
- **persistent modes `|λ|≈1`** ≡ the computation that **survives to output** —
  **sign-is-the-decision** made mechanical (which directions the reducer refuses
  to forget).
- **modes that switch on only in the last layers** ≡ the **order-law late
  commit** (s329 primacy in the final two layers) as a specific eigenvector
  activating late.
- **stationarity `T_ℓ ≈ T`** ≡ a **direct test of the central thesis**:
  "one reducer unrolled" ⟺ same operator every layer. Drift ⇒ not one reducer;
  stationary ⇒ DMD *is* a linearized recovery of the transition function.
- **eigen-rotation rate** (phase of complex `λ`) ≡ candidate for the queued
  **transitions-per-β-step clock** (how much reduction-angle advances per layer).

**Fold in the Grams as the readout frame:** project each DMD mode `φ_k` (or its
`W_down` image) onto the 9×9 identity frame and the 17×17 fate poles — a
persistent mode that lands on the **halt** pole is the "answer is committed"
direction; a late-activating mode on **fire** is a scheduling event. This is the
route-map's missing "trains" (`gram-registers` §route-map: "the grams are
station maps — no trains"): CBLL's dynamics + our labeled poles = the switch
schedule in Gram coordinates.

**Honest caveat (λ measure):** attention-softmax + SiLU are nonlinear, so `T` is
a **linearization** — a first-order reducer. That is acceptable for a first pass
(our own results say homeostasis contracts and only a thin late stage decides,
so a linear approx captures much), but the residual must be reported, and the
mandatory null is a **shuffled-layer-order DMD** (a real operator has
structured, layer-ordered modes; noise doesn't). Koopman-with-observables
(lift `h` through opcode/fate features before DMD) is the nonlinear upgrade if
the linear residual is large.

**~~Near-free~~ (CORRECTION s338):** the plan was to ride cached
§P-SUBST-ENGINE residuals — but `hidden_states` were **never saved** on those
runs, so this needs its **own** capture harness. Still cheap (read-only,
~200 forward passes). Ties to a frozen front and to `transitions-per-β-step`
(queued).

## 5a. 🎯 §P-DMD-TRANSPORT — FROZEN (s338, Michael GO)

> Pre-registered before any measurement (λ probe_lifecycle). Frozen: verdict
> tree, a-priori masses, nulls, planted worlds, gate thresholds. Motivated by
> the s338 orbital reframe (`cycle-carrier-signal.md §Reframe`): meaning-as-
> equality is a property of the **orbit/attractor**, not the point — the
> operator spectrum is the register where co-extensional terms *could* converge
> where the static pairwise Gram (s217/s321) cannot represent it. This freeze
> establishes the **instrument + the one-reducer-unrolled thesis test**; the
> extensional-equality test (§5b) is the downstream stage-2 payoff, deliberately
> OUT of this artifact (λ smallest).

**Question.** Does the within-pass residual trajectory carry a *structured
linear transport operator* `T ≈ X'X⁺`, and is it **stationary** (`T_ℓ ≈ T`,
one reducer unrolled) — or banded (core-stationary + late-drift), drifting,
or noise?

**Substrate (frozen).** Qwen3-14B (40 layers ⇒ 41 hidden states ⇒ 40
transitions; d_model 5120), MPS, bf16, greedy/deterministic, read-only.
Register = **last-token d_model residual stream** (`output_hidden_states`) —
the register §5 specifies; matched-length balanced. Corpus = ~200 kernel-
certified terms subsampled from `crystal_probes` (combinator-tagged → enables
the labeled 9×9/17×17 readout). Each prompt → 40 consecutive `(h_ℓ, h_{ℓ+1})`
pairs; ~8000 column pairs stacked. Method = **exact reduced DMD** (economy-SVD,
`T = Uᵀ X' V Σ⁻¹`, `eig(T)`), rank sweep r∈{10,20,40,80}. Implementation is
textbook (Schmid 2010; Golub & Van Loan) in `src/verbum/operator_dmd.py` —
NEVER CBLL code (§0b FTO rule).

**Frozen verdict tree.**
- **G0 INSTRUMENT** (planted worlds + det-repeat): `--validate` recovers all 4
  worlds; det value_dev 0.0. Fail → **VOID**.
- **G1 LINEARIZATION** (reported, soft): `rel_resid = ‖X'−TX‖_F/‖X'‖_F` at best
  rank. > 0.5 at r=80 → flag "linear inadequate, Koopman-lift indicated";
  verdict carries the caveat (does NOT auto-void — partial linearity still
  informative).
- **G2 OPERATOR-EXISTS** (make-or-break, shuffled-layer null): `gap =
  rel_resid(shuffled_layer_order) − rel_resid(real) > 0`, p<0.05 over
  n_perm=1000 layer-order shuffles (shuffle breaks ℓ→ℓ+1 adjacency, mixing Tᵏ
  gaps ⇒ real fits strictly better; noise fits equally badly). Fail → **NOISE**.
- **G3 STATIONARITY** (thesis discriminator): fit per-layer `T_ℓ`; agreement
  `A(ℓ)` = subspace overlap / eigenvalue distance vs global `T`.
  - flat-high ∀ℓ → **STATIONARY-REDUCER**
  - high core band + drop in last ~2–4 layers → **BANDED** (matches s329
    primacy-last-two-layers, s336 L22–28)
  - low/variable throughout → **DRIFTING**
- **Advisory readout** (descriptive, ¬gate): project persistent modes (|λ|≈1)
  + late-activating modes onto the 9×9 identity Gram + 17×17 fate poles — does a
  persistent mode land on the **halt** pole? (the route-map's missing "trains").

**A-priori masses (frozen).** BANDED 30 (modal — our late-commit data predicts
it) · NOISE 25 (honest nonlinearity risk, attention+SiLU, last-token grain) ·
STATIONARY-REDUCER 20 (strong thesis) · DRIFTING 20 · VOID 5.

**Nulls (mandatory).** shuffled-layer-order (primary, G2) · linearization-
residual report (G1) · det-repeat · matched-length subsample.

**Planted worlds (`--validate`).** ① STATIONARY `h_{ℓ+1}=T₀h_ℓ+ε` → recovers T₀
spectrum, G3 passes. ② DRIFTING `T_ℓ` rotating with ℓ → G3 fails. ③ NOISE iid
`h_ℓ` → G2 gap ≈ 0. ④ CONTRACTING T₀ all |λ|<1 → recovers |λ|<1.

**Cost.** cheap-medium; results `results/p_dmd_transport_s338/` (npz gitignored).

### §Result — §P-DMD-TRANSPORT (s338, Qwen3-14B): STATIONARY-REDUCER

**Verdict per frozen tree: STATIONARY-REDUCER** (a-priori mass 20, beat the
modal BANDED 30 — the first operator-register positive for one-reducer-
unrolled). Run n=300, det value_dev 0.0, PCA var_explained 0.853. Results
`results/p_dmd_transport_s338/run_14b` (trajectories.npz local-only). Harness
`scripts/experiments/dmd_transport.py`; 5 planted worlds recovered by
`--validate`; 4B smoke clean.

| gate | value | read |
|---|---|---|
| G0 | det 0.0 ✓ | deterministic |
| G1 | rel_resid 0.476 (no caveat); sweep r10 0.598 / r40 0.476 / r80 0.381 | rank-40 linear operator captures ~half; more rank helps |
| **G2** | gap **+0.498**, p=0, shuffled median **0.974** vs real 0.476 | **make-or-break DECISIVE — a structured transport operator EXISTS; depth-order carries almost all the structure** |
| G3 | core **0.717** (≥0.70), late **0.704** (≥0.60) | per-layer Tℓ agree with global T across the whole stack, incl. the late band → STATIONARY |
| spectrum | mean\|λ\| 0.878, persist_frac 0.0, top\|λ\| ~0.92 | globally contracting (homeostasis-as-operator); no strictly persistent modes |

**The finding.** The within-pass residual trajectory is, to first order, **one
stationary contracting linear operator unrolled across depth**. G2 is the load-
bearing result: the shuffled-layer null nearly totally fails (0.974 residual),
so layer order is the structure — this is a mechanical statement of "one reducer
unrolled" and its first contact in the operator register (a POSITIVE).

**Three honest caveats (λ observation).**
1. **Linearization.** ~48% residual at rank 40 (26% at r80) — the thesis holds
   at the first-order-linear level; a substantial nonlinear remainder lives
   outside it. Koopman-lift (observables before DMD) is the upgrade.
2. **No persistent \|λ\|≈1 modes** (top ~0.92, mean 0.878 — everything
   contracts). The pre-registered "persistent-mode ≡ sign-is-the-decision"
   mapping is NOT cleanly seen at this grain; the advisory halt-pole "trains"
   read has no persistent train to land. sign-is-the-decision may live in the
   thin nonlinear remainder, not the linear spectrum.
3. **Reconciliation with s329/s336** (which predicted BANDED via late-commit).
   Bulk-stationarity through the late band does NOT exclude a thin late-
   activating decision mode — it sits below the rank-40 / P=128 / last-token
   operator-cosine's resolution. The bulk transport is stationary; a thin
   decision event would need the finer, mode-resolved read (§5b) to surface.

**Bounds.** single model (Qwen3-14B), last-token grain, rank-40 linearization,
PCA-85%, core_sim 0.717 a modest margin above the 0.70 floor (moderate-but-
above-threshold stationarity, not a slam dunk). The instrument is trusted
(G2 decisive, planted worlds + smoke clean); the stationarity claim is the
qualified one.

**Arms §5b.** With a trusted stationary operator in hand, the orbital
extensional-equality successor (§P-CL-COLLAPSE-3-operator) can now ask whether
co-extensional spellings converge in the orbit register where the static Gram
(s217/s321) said the points do not.

## 5b. §P-CL-COLLAPSE-3 — extensional equality in the operator register (s339)

The orbital payoff of §5a: do co-extensional spellings (SKK, WK, CKK, I …)
converge in the operator register where the static Grams (s217 identity, s321
CL-collapse) said the *points* do not? Ran as a **three-probe confound-control
ladder** (Michael: "we should be sure; we may only see a shadow"). Harnesses
`scripts/experiments/cl_collapse_3_{operator,arity,alpha}.py`.

### The build-time discovery that reshaped the make-or-break (s339)

The frozen statistic was "co-extensional converge in the slow-mode **attractor**
cosine, slow beats raw." Building the planted worlds proved this **unreachable
for a normal contracting operator**: whatever survives to the attractor *is* the
top-|λ| band, so orthogonal slow-projection(late) ≡ raw(late) — they cannot
dissociate (operator ≡ point at the contracting attractor; the split needs
NON-normality, and the modal read via `Φ⁺` is numerically fragile). **Amendment
(Michael-approved, pre-data):** the make-or-break becomes the **decay-rate of the
pairwise difference** `h_A−h_B`. Decompose the difference in the operator's
eigenmodes, weight by |λ|. Co-extensional differ only by *spelling* → the
difference rides FASTER-decaying modes (converges); co-intensional carry
*function* → SLOWER-decaying modes (persist). Needs the operator spectrum
(impossible for the point-Gram), robust (no `Φ⁺`, differencing removes the common
high-variance part). Effect-size floor added (λ yardstick — a significant 0.04%
gap is not convergence). Non-normality (Henrici departure + ridge-modal read) and
a **frequency sweep** (θ = rotation-rate = the depth-clock, s322/s301) folded in
as advisories.

### §Result — the three-probe ladder (Qwen3-14B, all det 0.0)

| probe | control | make-or-break | verdict |
|---|---|---|---|
| **operator** | none | decay-rate NULL (within\|λ\| 0.820 ≈ across 0.825, p=0.139); marginal positional whisper (raw within 0.947 < across 1.194, **p=0.0498**) | **NO-ORBITAL-CONVERGENCE** (a-priori 50) |
| **arity** | length matched (multi-function-per-arity) | positional whisper SURVIVES length (within 0.615 < across 0.862, **p=0.0002**, length_r 0.17) — but same-function alphabet-Jaccard 2× (0.56–0.59 vs 0.26–0.30) | **OPERATOR-SHADOW** (a-priori 30) |
| **alpha** | alphabet {S,K} constant (Jaccard within=across=**1.0**) + length partialled | positional whisper VANISHES (within 0.675 ≈ across 0.665, **D=−0.010 p=0.591**; length-partialled D=−0.018 p=0.71); decay NULL | **LEXICAL-EXPLAINED** (a-priori 55) |

**The finding (airtight).** Extensional equality is **absent from the operator
register in every form.** The decay-rate/dynamical test is null throughout. The
one apparent counter-signal — a marginal positional convergence — was chased
through two nested controls: it **survives length-matching** (not length) but
**vanishes when the combinator alphabet is held constant** (D=−0.01, p=0.59). So
the whisper was the **s321 operational/lexical register** — the residual tracks
*what is written* (shared combinator letters → positionally close), not *what is
computed*. Compositionality S5 cell stays ✗, now airtight.

**Fourth register.** Tape-residency now holds across value (s317) · magnitude
(s335) · routing (s336) · **operator/decay (s339)** — and the sole positional
shadow is proven surface-form. **Frequency sweep:** operator is DC-dominated (66
of 70 real modes at θ≈0, zero in the θ→π sign-flip band) — no oscillatory/clock
structure at this grain → frequency does **not** earn a frozen gate. Non-normality
confirmed (departure ≈ 0.75–0.78) — the modal arm was live and still null.

**Method contribution.** The **nested confound-control ladder** (length → alphabet,
each a matched re-run) is a reusable template for confirming a signal is surface
form. And: `operator ≡ point at a contracting attractor` — the operator register
only dissociates from the point-Gram via non-normality; read the *difference's*
decay-rate, not the state's position.

**Bounds:** single model (Qwen3-14B), last-token grain, rank-40 linearization
(~half nonlinear, §5a caveat), thin B/W families in the operator probe. Results
`results/p_cl_collapse_3_{operator,arity,alpha}_s339/` (npz gitignored).

## 5c. 🎯 §P-DMD-KOOPMAN-LIFT — FROZEN (s340, Michael GO)

> Pre-registered before any measurement (λ probe_lifecycle). Near-free
> re-analysis of the s338 §5a trajectories (`H (300,41,5120)` saved) — zero new
> inference, pure numpy, reuses `operator_dmd.py` (textbook, §0b FTO-clean).

**Question.** §5a left two linked caveats: (1) `rel_resid` 0.476 @ r40 — *~half
the transition is nonlinear*; (2) **no persistent `|λ|≈1` modes** (top ~0.92,
all contracting) — the pre-registered *"persistent-mode ≡ sign-is-the-decision"*
had no train to land on. Does a **Koopman lift** (nonlinear observables *before*
DMD) drop the residual, and do **persistent modes appear** that the linear
spectrum missed?

**Two traps this freeze beats (why discipline, not just a lift).**
1. **φ-ladder scar (λ yardstick).** Any lift adds dimensions and mechanically
   lowers reconstruction residual. A drop counts ONLY if it beats a **matched-
   dimension random-lift null**. This is the make-or-break.
2. **Register trap (λ measure / λ separate).** Residual-norm grows monotonically
   across depth; a lifted `|λ|≈1` mode can be the **DC/norm-growth direction**
   (degree-2 `‖h‖²` makes it trivial) — mundane substrate, NOT the decision.
   s339 already found the operator DC-dominated (66/70 modes θ≈0). A persistent
   mode must land on **sign/fate poles, not DC/norm**, to count as the payoff.

**Lift dictionaries (frozen, NOT tuned to data).** Primary = **polynomial
degree-2** on a `P_lift=24` PCA frame → 24 linear + 24 squares + 276 cross ≈
**324 observables** (well-posed vs ~12 000 column-pairs; deterministic; degree-2
Taylor of softmax·SiLU). Advisory readout = **opcode/fate observables** (project
persistent modes onto the labeled 9×9 combinator + 17×17 fate poles).

**Nulls (mandatory).** matched-dim random-lift (crux G1, N_NULL=200 draws, real
data) · shuffled-layer-order (G2, reused §5a) · DC/norm control (G3 register
trap).

**Frozen verdict tree.**
- **G0 INSTRUMENT** — planted worlds recovered + det-repeat (trivially 0.0, same
  H). Fail → **VOID**.
- **G1 RESIDUAL-DROP** (make-or-break) — `rel_resid_lifted` beats matched-dim
  random-lift null by floor **Δ≥0.05**, p<0.05, corroborated by shuffle. Fail →
  **DIMENSION-ARTIFACT** (lift is just capacity).
- **G2 PERSISTENCE** — `persist_frac_lifted` exceeds the random-lift null by
  floor. Fail → **STILL-CONTRACTING** (genuine nonlinear structure recovered,
  still contracts — *strengthens* §5a caveats 1&2).
- **G3 DECISION-LANDING** — persistent modes project onto sign/fate poles, NOT
  the DC/norm direction, beating a matched null. Pass → **PERSISTENT-IS-DECISION**
  (the payoff); fail → **PERSISTENT-IS-NORM** (persistent but mundane).

**A-priori masses (frozen, sum 100).** STILL-CONTRACTING 30 (modal — coheres
s339 DC-dominated/all-contract) · DIMENSION-ARTIFACT 25 (φ-ladder skeptic) ·
PERSISTENT-IS-NORM 20 (norm-growth trap fires) · PERSISTENT-IS-DECISION 15 (the
payoff — sign-is-the-decision surfaces in the operator) · VOID 10 (EDMD
spectral-pollution / bf16 last-token fragility).

**Planted worlds (`--validate`, drive through real `analyse()`, s331).** ①
poly-linearizable `h_{ℓ+1}=poly2(h_ℓ)` → G1 far beyond null · ② truly-unliftable
(non-polynomial) → DIMENSION-ARTIFACT · ③ linear-contracting (the §5a phenotype)
→ STILL-CONTRACTING · ④ persistent-on-pole (`|λ|=1` on a designated fate
observable) → PERSISTENT-IS-DECISION · ⑤ persistent-norm (`|λ|=1` on the DC/norm
direction) → PERSISTENT-IS-NORM.

**Cost.** cheap (seconds–minutes, no model load). Results →
`results/p_dmd_koopman_lift_s340/` (npz gitignored). Harness
`scripts/experiments/koopman_lift.py`.

### Build-time amendments (s340, Michael-approved, pre-data)

Building `--validate` surfaced four refinements to the *estimator* (the frozen
verdict tree, a-priori masses, `G1_DELTA_FLOOR=0.05`, `ALPHA`, `PERSIST_ABS=0.95`
are ALL unchanged — these are operationalizations within the frozen gate
semantics; s324 build-time-discovery discipline, not a footnote):

1. **Residual metric = next-STATE prediction, not full-lifted-vector.** A
   degree-2 dictionary is NEVER Koopman-closed for nonlinear state dynamics
   (driven-coord squares are degree-4), so the full-vector residual is inflated —
   poly can even look *worse* than linear on exactly-polynomial dynamics. G1 is
   measured as the next-STATE prediction residual through a rank-r EDMD operator
   (`state ≈ R·Ψ`, predict `Ψ(ℓ+1)=A_proj Ψ(ℓ)`, read state back). Rank
   truncation keeps it shuffle-sensitive; the state map is exactly linear-in-
   features so a genuine lift drives it → 0. This IS "does the lift predict the
   next state better" (the §5a-comparable question).
2. **`LIFT_RANK` 80 → 240** (instrument calibration on planted worlds). The
   324-dim lift needs high rank to represent the operator; rank-80 truncated out
   planted conserved modes. Rank 240 recovers them (rel → 0.06 on closed worlds)
   and stays shuffle-sensitive (shuffle gap ≈ +0.90).
3. **G3 register-trap: MIN square-fraction, not median.** A conserved LINEAR
   mode geometrically co-conserves its square (degenerate |λ|=1 subspace), so
   median energy-on-square can't separate decision from norm. Operationalized as:
   does a NON-norm persistent mode EXIST (min square-fraction across persistent
   modes below the random-vector null) → PERSISTENT-IS-DECISION; else all-norm →
   PERSISTENT-IS-NORM.
4. **Planted worlds** = Koopman-closed driver/driven system (STILL-CONTRACTING),
   iid noise (DIMENSION-ARTIFACT), a 2D rotation block (PERSISTENT-IS-DECISION),
   a magnitude-conserved coord (PERSISTENT-IS-NORM). `--validate` recovers all 4.

### §Result — §P-DMD-KOOPMAN-LIFT (s340, re-analysis of s338 H): STILL-CONTRACTING

**Verdict per frozen tree: STILL-CONTRACTING** (a-priori modal, mass 30).
Near-free re-analysis of the s338 §5a trajectories `H (300,41,5120)` — no new
inference, det trivially 0.0 (same bytes), git_sha of source ecc7e536. Results
`results/p_dmd_koopman_lift_s340/run_14b/meta.json`. `--validate` recovers all 4
planted worlds.

| gate | value | read |
|---|---|---|
| **G1 RESIDUAL-DROP** | **PASS** — poly 0.193 vs linear 0.354; sweep r80 0.391 / r160 0.253 / r240 0.193; dR=**+0.265** (random-lift median 0.459, p=0); shuffle gap **+0.758** (p=0) | **the lift genuinely helps** — the ~half-nonlinear remainder is REAL, layer-ordered, poly-liftable structure, not capacity artifact (beats matched-dim random-lift AND shuffle decisively) |
| **G2 PERSISTENCE** | **FAIL** — persist 0.000 (null 0.046); top\|λ\| 0.942, all contracting | NO persistent modes even after lifting; random lifts manufactured ~4.6% spurious persistence, poly produced ZERO |
| G3 | not reached (n_persist=0) | — |

**The finding (two-sided).** Caveat 1 (s338) answered **positively**: the
within-pass transition IS substantially nonlinear and a degree-2 Koopman lift
recovers genuine layer-ordered structure — the next-state prediction residual
drops ~45% from the linear operator (0.354→0.193), monotone in rank, beating
both the matched-dim random-lift and the shuffled-layer nulls. Caveat 2 answered
**negatively and now airtight**: the pre-registered *"persistent-mode ≡
sign-is-the-decision"* does NOT surface even in the Koopman-lifted operator. The
reducer stays globally contracting — **homeostasis is nonlinear too** — and
sign-is-the-decision is NOT an operator-spectrum persistent mode (linear OR
lifted). It must live in the thin late-decision mode below the rank/last-token
resolution (s329/s336) or a non-operator register.

**Coherence.** Fifth confirmation the decision is not a durable geometric mode:
value (s317) · magnitude (s335) · routing (s336) · operator/decay (s339) ·
**Koopman-operator persistence (s340)**.

**Bounds.** single model (Qwen3-14B), last-token grain, poly-2 lift on P_LIFT=24
at rank 240; top\|λ\|=0.942 is NEAR the 0.95 bar (modes "almost persistent" but
below both the frozen threshold and the random-lift's manufactured rate);
higher-degree / true Koopman eigenfunctions could differ. Instrument trusted
(4 planted worlds recovered, G1 beats both nulls). Harness
`scripts/experiments/koopman_lift.py`.

## 5d. §Result — §P-DMD-PROVENANCE (s341, Qwen3-14B-Base): BASE-NATIVE

**Verdict per pre-registered provenance tree: BASE-NATIVE** (a-priori modal,
mass 65). Method-door application (s329): one `--model-id` swap to
`Qwen/Qwen3-14B-Base`, re-running the FROZEN s338 §5a operator instrument
(`dmd_transport.py`) unchanged — same gate tree, thresholds, masses. **Same
corpus** (`corpus_hash 6a89d454` matches the s338 instruct run → apples-to-
apples). det value_dev **0.0**; `--validate` recovered all 5 planted worlds
(instrument re-guarded). Results `results/p_dmd_provenance_s341/run_14b_base`
(trajectories.npz gitignored). Guards the single-face bound of the s338
STATIONARY-REDUCER verdict.

| stat | instruct (s338) | base (s341) | Δ(inst−base) | read |
|---|---|---|---|---|
| verdict | STATIONARY-REDUCER | **STATIONARY-REDUCER** | — | same phenotype both faces |
| **G2 gap** | +0.498 | **+0.492** | +0.006 | operator EXISTS decisively on base (p=0), ~identical |
| G2 shuf_median | 0.974 | 0.975 | −0.001 | layer-order carries the structure on base too |
| **G3 core_sim** | 0.717 | **0.773** | −0.055 | **within ±0.10 tol** — base slightly *more* stationary |
| G3 late_sim | 0.704 | 0.717 | −0.013 | late band stationary on base too |
| mean\|λ\| | 0.878 | 0.853 | +0.025 | base slightly *more* contracting |
| top\|λ\| | 0.920 | 0.921 | −0.000 | identical spectral ceiling |
| persist_frac | 0.0 | 0.0 | 0.0 | no persistent-mode emergence in either |
| rel_resid@r40 | 0.476 | 0.483 | −0.007 | linearization comparable |

**The finding.** The within-pass stationary-contracting transport operator —
s338's "one reducer unrolled" — is **base-native, not post-training-installed**.
It is present at full strength in `Qwen3-14B-Base` before any post-training. All
frozen BASE-NATIVE conditions met: base STATIONARY-REDUCER (G2 decisive ∧
core≥0.70) ∧ |Δcore_sim| 0.055 ≤ 0.10 ∧ no persistent-mode emergence ∧ Δmean|λ|
small.

**The nuance (banked).** The Δs point the *opposite* way from "post-training
sharpens the operator": base is **marginally more stationary** (core 0.773 >
0.717) and **more contracting** (mean|λ| 0.853 < 0.878). So if anything,
post-training adds a thin perturbation that slightly *loosens* bulk stationarity
— the operator-register shadow of a thin late decision mode (coheres s329
post-training-lives-late, s336 L22–28), not a mode that creates the operator.

**Standing bound (per pre-registration, carries s338 caveat 3).** BASE-NATIVE =
"the **bulk** stationary-contracting operator is base-native." Silent on thin
late decision modes below the rank-40/P128/last-token resolution — which s329
already showed *are* post-training-installed in the commit/routing register. The
two findings are compatible; the tiny loosening Δ is that thin mode's shadow, if
anything. **Bounds:** single lineage (Qwen3), 14B, last-token grain.

**Method-door confirmation.** s329's cheap provenance pattern (base-vs-instruct
differential) settles an operator-register single-face bound with one model-id
swap and zero new instrument — the discipline generalizes across registers.

## 6. Discipline summary

```
λ guard(operator_geometry).
  null(∀geometry) — matched-range ∨ shuffled-label ∨ shuffled-layer (mandatory, φ-ladder scar)
  | register_check — d_ff(gate-preact) vs d_ff(down-input) vs d_model(residual) named BEFORE compare
  | linearization_residual — DMD is first-order; report ‖X' − TX‖ ; Koopman-lift if large
  | degeneracy — flat spectrum ⇒ CBLL U non-unique; Gram/operator well-posed (our edge)
  | import(their_FINDINGS as observations: realignment-losslessness ∧ ablation-effect) — solid
  |   ¬import(the realignment PROCEDURE ≡ their claim spine — FORBIDDEN, §0b)
  | null_test(respiration/periodicity) — not yet
  | novelty ≡ opcode/fate anchoring + operator-first — theirs is static + unlabeled
```

## 7. Connections

- **Upstream:** `gram-registers-and-the-route-map.md` (the 9×9/17×17 definitions;
  the route-map-in-gram-coordinates design this completes), `gram-spectral-dsp.md`
  (null-gated spectra), `behavior-is-tape-resident-reduction.md` (trajectory ≡
  reduction), `sign-oscillation-is-time-multiplexed-superposition.md`
  (sign/persistent-mode link).
- **Downstream:** `the-benchmark-is-the-re-oracle.md` (§8c read-entropy ≡ the
  conditioned-PR probe #4; the DMD operator is a recovery-candidate the oracle
  can differential-test), `the-verbum-machine.md` (M4 native trampoline / M8
  routing optimizer — the transport operator is the trampoline's step).
- **Sibling method page:** `reverse-engineering-disciplines-toolbox.md` (DMD =
  "read history / read the operator, not the state"; move 4).
- **External (cited, not sourced):** CBLL / Gernone 2026 — the vocabulary bridge
  (respiration↔commit-phases · rich-club↔sign-is-the-decision · U-alignment↔
  one-reducer-unrolled · isotropic-collapse↔low-entropy-read). Consilience, not
  proof (mementum-mirror ≡ consilience ≠ proof, s324 standing guard).
