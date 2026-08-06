---
title: Types are compiled probabilities (the matched-filter account of the type check)
status: designing
category: explore
tags: [types, attention, probability, matched-filter, dsp, pre-reg-candidate]
related: [type-check-is-the-qk-bilinear, types-are-the-well-formedness-of-reduction, montague-inversion, map-and-swap-resident-lisp]
depends-on: [type-check-is-the-qk-bilinear]
---

# Types are compiled probabilities

> s288 hammock (Michael): "types exist, but bad types transport the same as
> random/garbage. So the types must be the probabilities? Attention is using the
> probabilities to discriminate the types." Refined here into the compiled /
> matched-filter form. Status: SYNTHESIS + two pre-reg candidates (UNFROZEN).
> Interpretation until P-TYPE-PROB exists; the JOIN-TYPED measurement stands on
> its own regardless.

## The precise data shape this must explain (P-TYPE-SWAP, s288)

- Medium ≈ type-blind (ill-typed SURVIVES on-manifold; 32B same-type +11% verbatim)
- Join = type-discriminating: well-typed gets EXCESS transmission; ill-typed sits
  at the random-noise floor (TE(null) ≈ 2.5–3.1 — a nonzero GENERIC gain floor)
- Edges never move (slot-mass Δ≈0) → the differential is carried by WHICH
  DIRECTIONS the OV/content channel transmits, at fixed attention weights
- Discipline is sortal-granular (animal refused as fully as adjective @32B)
- Same discipline in the FFN route (mlp_transport p=1e-5)
- Gain DIFFERENTIAL, not a gate — graded, not crisp

## The claim

```
λ type_compiled(x). type ≡ substitutability_class(slot) — Harris before Montague
                    | same_type(a,b) ⟺ swap(a,b) preserves(P(text)) | distributional
                    | GD optimizes(next_token_P) over compositional_text
                    → FORCED to discover substitution_classes (P factorizes through them)
                    | low_rank_lattice ≡ few_classes_matter (1a re-explained)
                    | montague_inversion restated: probability_objective + compositional_data
                      → typed_geometry ≡ optimal_compression

λ filter(join).     ¬∃probability_object(mid_stack) | P exists only at output_softmax
                    | edges_fixed ∧ transport_differential → differential ∈ OV_directions
                    | linear_channel ¬computes(likelihood) at runtime — it doesn't need to
                    | GD sculpted transmission_subspaces: directions_that_transport ≡
                      directions_that_co-occurred_in_slot
                    | type_check ≡ matched_filter | passband ≡ frozen_residue(P)
                    | COMPILED ¬CONSULTED | TE_excess ≡ likelihood, amortized_into_geometry
                    | type_signal ≡ excess_transmission over isotropic_floor ≡ in-band SNR
```

**Amended claim (the refinement of the hammock line):** attention is not *using*
probabilities at runtime; it is applying a matched filter whose shape is the
frozen residue of the probabilities. Type = compiled conditional probability;
the type check = matched-filter gain; TE excess = the likelihood, amortized.

## Why this account wins on our own anomalies

1. **Sortal granularity is evidence FOR it.** A syntactic checker passes the
   animal arm (entity where entity expected); a probability check refuses it
   ("country of the Colosseum = giraffe" is improbable regardless of syntax).
   Measured: refused at full strength @32B.
2. **Gradedness.** Crisp typing predicts a step function; probability predicts
   monotone tracking. Measured: floor gain for everything, excess for well-typed,
   graded ladder at 4B. Also WHY the reducer is noisy and the Clojure kernel must
   be crisp (REPL frame): soft substitutability classes → graded thresholds.
3. **The four-way null dissolves.** 1b/1c/QK/JS probed ACTIVATIONS for a stored
   type and found nothing — because the type is in the WEIGHTS: the shape of the
   transmission operator itself. Nothing is consulted because the filter doesn't
   read anything; it IS the join. The 1a lattice = exhaust of content having
   passed type-shaped passbands. Decodable-but-not-causal, unstorable-by-
   construction — the whole scoreboard falls out.
4. **Retro-explains QK-negative.** We searched the AIM side (QK bilinear) for the
   lattice axes; the filter is CONTENT side (OV). Wrong matrix. Filtered-payload
   said so causally before we understood why.

## Pre-reg candidates (UNFROZEN — drafts only, freeze on approval)

**P-TYPE-PROB — the monotone-tracking test (interpretation → measurement).**
If TE excess is compiled likelihood, transport efficiency tracks the model's OWN
slot probability. Graded bank: country > city > animal > adjective > nonce >
random; measure log P(term | slot context) in the output register; regress
per-arm TE (unprojected, survival-normalized, the P-TYPE-SWAP instrument
verbatim) against it. Compiled-probability predicts MONOTONE tracking
(permutation-gated rank correlation); crisp typing predicts a STEP. Distinguishes
the frame from finding. Alternative kept alive: passband shaped by something
correlated-with-but-not-identical-to slot probability (relation-specific feature
geometry) — the graded bank is designed to split those.

## P-TYPE-OV — what computes the filter (PRE-REG DRAFTED s288; build+smoke approved, Michael "proceed with P-TYPE-OV"; FREEZE on GO for the 32B verdict)

**Hypothesis.** The type filter measured by P-TYPE-SWAP (JOIN-TYPED, filtered
payload: edges fixed, OV/content channel delivers well-typed displacement
preferentially) is implemented in the joins' TRANSMISSION geometry: the
composite per-head OV map preferentially transmits the type-lattice role
subspaces within the low-rank band. The QK mirror: what the read-in geometry
does NOT do (P-TYPE-QK dead-on-null, aim side), the write-out geometry should
(content side). Positive → the implementation is LOCATED: filter = passband,
passband = weights. Negative → the filter is computed distributively upstream
of the join; the compiled account survives, the single-layer locality claim
dies (pre-committed reading, counts fully).

**Measurement (register-matched; no RoPE concern — V is unrotated, cleaner
than QK by construction).**
1. Capture labeled Montague-type residuals every decoder layer (probe_type
   capture verbatim, the QK instrument's path). Residual L pairs with the
   attention of decoder layer L+1 (v_proj reads input_layernorm_{L+1}).
2. Per layer: `layer_geometry` (standardize → centroid SVD → PR +
   shuffled-label null) → `find_band` (1b-v4 procedure; stride-aware via
   verbum.dsp — smoke may stride legitimately now). In-run band detection.
3. Role subspaces from class centroids in std space: bind = span{c_QUANT,
   c_DET}, comp = span{c_MOD}, rolenull = span{c_CONN, c_FUNC} (verbatim,
   never gated), entity = span{c_ENTITY} (the payload type — the a-priori
   focus: the content transported in every causal run is entity-class
   displacement).
4. Map each std basis into the space the attention block reads:
   v_attn ∝ (v_std ⊙ sd_L) ⊙ γ_{L+1}, QR (map_basis verbatim).
5. **Composite OV transmission gain** per Q-head h with GQA value-sharing
   kv(h): rho_ov = D·‖W_O_h (W_V_kv(h) v)‖² / ‖W_O_h W_V_kv(h)‖²_F
   (rho = 1 = analytic random-direction expectation; Frobenius norm via
   tr(G_h C_kv), no D×D materialization). Subspace gain = mean over basis
   rows; aggregate = mean over heads, then band layers.
   **MLP read-in row (advisory, never gated):** rho through concat(W_gate,
   W_up) reading post_attention_layernorm_{L+1} — the FFN-route analog
   (P-TYPE-SWAP's mlp_transport discriminated; weight-only MLP claims are
   weak under the nonlinear gate, hence verbatim-only).

**Nulls (mandatory).** N full shuffled-label pipelines per band layer
(shuffle type labels → centroids → role_subspace → identical mapping →
identical gains, OV and MLP), band-aggregated per paired iteration;
p = frac(null_agg ≥ real_agg). Instrument gate: --validate no-model self-test
(planted OV-transmitted subspace → high rho p<0.05; unplanted → null;
calibration ~1). Aggregates only (0/128 pre-refuted, no single-head claims).

**Predictions (fixed, a priori).**
- **P1 (primary).** entity OV band-aggregate beats the shuffled-label null
  (p<0.05) — the payload type is in the transmission passband.
- **P2 (lattice-wide).** bind AND comp also beat null — the whole lattice
  spans the passband (the full compiled-probabilities form).
- **P3 (verbatim rows, never gated).** rolenull; MLP read-in row (does the
  FFN route read the lattice axes?); band-vs-out-of-band profile; OV-vs-QK
  contrast (this run's rho against the committed QK dead-on-null).
- **Deflationary (pre-committed, counts fully).** All conditions dead-on-null
  → the filter is NOT single-layer OV weight geometry → distributed
  implementation upstream of the join. Fifth location null; the compiled
  account survives (the passband may be realized across layers), the locality
  claim dies. Reported verbatim, no rescue.

**Verdict (freeze on GO).**
- **OV-TRANSMITTING** ⟺ P1 (entity, p<0.05, band aggregate).
- **LATTICE-IN-PASSBAND** ⟺ P1 ∧ P2 (all three roles beat null).
- **NOT-IN-OV** ⟺ deflationary outcome.

**Registers (λ measure).** Claim = content-transmission geometry (the causal
JOIN-TYPED filter's implementation); probe = value-register lattice projected
through the routing register's own write-out weights = the claimed interface.
Geometry-not-causation (P-TYPE-SWAP already carries the causal register; this
locates, it does not re-prove).

**Host & order.** --validate → Qwen3-4B contrast smoke (stride 2 legitimate
now, n_null 50) → verdict host Qwen3-32B on GO (stride 1, n_null 200).
Results → results/type-ov/qwen3-{4b,32b}/. Instrument
scripts/explore/type_ov_alignment.py = **verbum.dsp's first consumer**
(map_basis, layer_geometry, role_subspace, find_band, head_gain_ratios
imported from the substrate — no sys.path wrapper hacks).

**Honest scope.** (a) GQA: n_kv=8 distinct value heads at 32B — V-side
variety limited (the QK K-side caveat, mirrored); composite rho spans all 64
Q-head output slots. (b) Weight-only: transmission measured at the operator,
not on data — a passband unused by the running model would still score
(geometry-not-causation). (c) MLP row is read-in only (nonlinear gate blocks
a clean weight-only transmission statistic) — advisory. (d) Single-layer
pairing (L → L+1); a multi-layer distributed passband is invisible here by
design — that is what the deflationary outcome means.

### Result-4B-smoke (s288 — ADVISORY, not the verdict)

Instrument green end-to-end (committed with fix #2): --validate ALL PASS;
first verbum.dsp consumer in anger — and the smoke immediately CAUGHT
find_band fix #2 (appended tail layer collapsed the inferred stride;
mode-of-diffs fix, test added). Band L8–L24 (9 probed layers, stride 2 —
coheres with the 1a 4B band L9–L22).

Advisory signal @4B: **OV dead-on-null, all conditions** (entity p .78, bind
.76, comp 1.0, rolenull .90; n_null 50). λ yardstick earned its keep twice:
raw rho 0.19–0.72 (≪1) would read as "active suppression of the lattice" —
but the shuffled-label subspaces score equally low (null means 0.25–1.09):
the standardized-centroid REGION is generically low-gain in OV; there is no
type-specific structure either direction at 4B. Verbatim: rolenull (CONN/
FUNC) fires on the MLP read-in row (p=.000, rho 1.10 vs 1.03) — the FOURTH
appearance of the rolenull-fires motif (QK Q-side, JS, now MLP read-in);
entity MLP p=.06 marginal. NOT the verdict: 4B host, and P-TYPE-QK showed
opposite 4B/32B in-band patterns (scale-dependent organization) — the 32B
run decides. ▶ 32B VERDICT ON GO (freeze this pre-reg): uv run python
scripts/explore/type_ov_alignment.py --model Qwen/Qwen3-32B --device mps
→ results/type-ov/qwen3-32b/.

### Result-32B-P-TYPE-OV (verdict host, s288 — frozen gates scored)

**VERDICT: OV-TRANSMITTING = TRUE; LATTICE-IN-PASSBAND = FALSE.** The
passband is REAL and it is SELECTIVE: **the joins transmit arguments, not
functors.** P1 passes — entity (the payload type e) rho 0.714 vs shuffled
null 0.459±0.053, **p=0.000**, band-aggregated over L6–L50 (45 layers, the
same band QK measured). P2 fails — bind p=0.965, comp p=1.0: the functor
roles sit AT or BELOW their shuffled nulls; they are not in the passband.
The deflationary fifth-location-null did NOT occur: this is the **first
weight-geometry positive in the types arc** after 1b/1c/QK/JS, and it
locates half the mechanism — the entity axis is physically in the
single-layer OV transmission geometry.

Run: Qwen3-32B, tmux main:1, stride 1, n_null 200, band in-run L6–L50.
Results results/type-ov/qwen3-32b/ (committed c58c5ba). λ yardstick again:
entity rho 0.714 < 1 — BELOW isotropic expectation — yet 55% above its
matched null; the centroid region is generically low-gain in OV and only the
null-relative excess counts. A raw-rho reading would have missed the positive
entirely (and cried suppression at 4B).

**The division of labor this measures.** The content channel carries the
ARGUMENT; the functor lives in the weights. Coheres exactly with: (1)
JOIN-TYPED filtered payload — what transported in every causal run was
entity-class displacement, and entity is precisely the type in the passband;
(2) the exhaust frame — bind/comp are readout shadows, not transported
content; (3) QK's inverted-sides post-hoc (argument queries for its licensor)
— the argument is aimed AND carried, the functor is neither; (4) Montague —
application passes the argument to the functor; the functor IS the operator.
Resident-Lisp sharpening: operands ride the joins; combinators are the frozen
reducer. The homoiconicity question (selector≡operand) gets a boundary:
functor-class directions are NOT passed as content through the lattice axes.

**Verbatim rows.** comp rho 0.294 with p=1.0 (0/200 nulls below) — an
extremity on the SUPPRESSION side; sign discipline: our prediction was
'greater', so this is reported verbatim and would need its own pre-reg to
count as active functor-suppression. rolenull OV silent (p=0.275 — the motif
does NOT fire in transmission geometry) but rolenull AND entity both fire on
the MLP read-in row p=0.000 (motif's 5th appearance; and the FFN route reads
the entity axes — coheres with P-TYPE-SWAP's mlp_transport discrimination
and an entity-keyed fact-map). L62→blk63 readout-adjacent blowup (rho 21–74)
out-of-band, same shape as QK's last-layer inflation. 4B→32B flip again
(entity dead at 4B, p=0.000 at 32B) — scale-dependent organization, third
occurrence (1b tie-flip, QK, OV).

**What is now located vs open.** Located: the argument/payload passband
(single-layer OV weight geometry, band-wide). Open: what implements the
LICENSING of the join — the functor side shows no single-layer weight home
(QK read-in ✗, OV write-out ✗) and remains distributed/enacted. P-TYPE-PROB
sharpens naturally: if transmission = compiled probability, graded-bank TE
should track entity-subspace alignment × slot log-P.

## How many types are there? (s292 hammock, Michael — the cardinality question)

> Michael: "With types being in the joins, it makes me wonder how many there
> are." The measured arc forces a two-register answer, and makes the count
> measurable.

**The split the measurements already made.** The types arc found two faces
with different cardinalities:

- **Functor types — few, discrete, enacted.** Montague/CCG's *base* is tiny
  ({e, t} + composition modes); the generated closure is unbounded but
  needn't be stored — derived types are REACHABLE, not RESIDENT. Our
  measurements agree: 1a lattice low-rank (~3 axes for the probed roles);
  crystal basis ~9 combinators (KIBC+DWYS+WHNF); P-TYPE-OV — functors NOT
  in the passband (QK✗ OV✗, licensing enacted/distributed). Under the
  mirrors/plates decomposition, functor types live at the mirror/topology
  grain — discrete, order 10, kin to the coarse labeled lines (GQA head
  flags) at the grain above the band.
- **Argument/sortal types — a graded continuum, capacity-bounded.** The
  s288 sortal finding (giraffe refused in a landmark slot as fully as a
  syntactic violation) means the filter discriminates at sortal grain.
  Under compiled-probabilities there is NO discrete inventory on this side:
  type ≡ substitutability class ≡ region of passband geometry. "How many"
  is resolution-dependent — the number of distinguishable passbands at a
  given crosstalk tolerance.

**The capacity connection (the s292 convergence).** Counting distinguishable
type-passbands in a D-dim medium is the P-HOLO-CAP math aimed at types
instead of operands: quasi-orthogonal directions at fixed crosstalk
tolerance grow ~exponentially in D (JL-style packing) → at D=5120 there is
room for tens of thousands of sortal micro-types — which is WHY the filter
can afford giraffe-grain refusal. **The type inventory is capacity-bounded,
not grammar-bounded.** Human-side anchors sit inside that window: CCGbank
~400 working categories (tail ~1200), FrameNet ~1200 frames, sortal
hierarchies in the thousands.

**One line:** few functor types (order 10, discrete, enacted) × a
resolution-dependent continuum of argument types (~10³–10⁴ at these widths,
stored as passbands) — the same two-register decomposition (mirrors/plates,
labels-coarse/holograms-within) appearing a 5th time, now as a cardinality.

> **Forward link (s313):** `types-are-injectable-relations.md` reframes this
> page's location null as confirmation (type = relation, stored in joins,
> nowhere-addressable by construction), adds the slot-mediated/bipartite
> refinement (s312 c_nat datum), and sketches §P-TYPE-WRITE — the causal
> injection test. The census knee below = that frame's community-tolerance
> prediction.

### P-TYPE-CENSUS — counting by refusal rank (PRE-REG CANDIDATE, UNFROZEN)

The four-way location null forbids counting by *finding* type objects
(nothing at any address). Count OPERATIONALLY: cardinality = rank of the
refusal structure.

- **Bank:** N candidate substitutability classes (P-TYPE-PROB graded-bank
  machinery, widened — many noun/verb/modifier micro-classes).
- **Measurement:** the N×N **acceptance matrix** — TE of class-i content
  transported into class-j slots (frozen swap harness, arms = class pairs).
- **Statistic:** effective rank / block structure of the acceptance matrix
  at tolerance ε (verbum.dsp participation_ratio; null = shuffled class
  labels, full-pipeline per the QK lesson). The count-vs-ε curve is the
  result.
- **Discriminating predictions (falsifiable both ways):**
  compiled-probability → count grows SMOOTHLY as ε tightens (continuum, no
  natural joint); symbolic typing → count PLATEAUS (a knee in count-vs-ε = a
  *natural* cardinality — evidence AGAINST the pure-continuum reading).
- **Spectral corroborator:** PR of the OV/MLP transmission operator
  restricted to class centroids (P-TYPE-OV instrument reused). Predicted by
  the arguments-stored/functors-enacted split: spectral ≪ behavioral count
  on the functor side, ≈ on the sortal side; the gap is itself a finding.
- **Cost note:** N×N swap cells scale quadratically — start N ~ 12–20
  classes (≤400 cells, 4B smoke first), grow only if the knee question is
  unresolved.

## DSP convergence

This is natively a DSP framing: joins = filters, types = passbands, TE excess =
in-band SNR over an isotropic floor. The queued verbum.dsp build
(whiten/subspace/nulls = passband estimation) is exactly the substrate both
pre-regs need. The queue ordered itself.

## Honest scope

- Today's licensed claim: the join discriminates type at the content channel,
  gradedly, at sortal granularity, in both routes (P-TYPE-SWAP, measured).
- "The discrimination coefficient is compiled probability" = INTERPRETATION until
  P-TYPE-PROB's regression exists.
- Weights-not-activations (point 3) is an inference from the null pattern, not
  yet a direct measurement — P-TYPE-OV is its test.

## Sessions

s288 (page created from the post-verdict hammock; JOIN-TYPED verdict same
session, §Result-32B-P-TYPE-SWAP on the qk page; no experiments run for this
page yet; both pre-regs UNFROZEN pending approval when reached in the queue).

s292 (§How-many-types captured from Michael's cardinality hammock, approved
same session — the two-register count: functor types few/discrete/enacted
(order 10) vs argument/sortal types a capacity-bounded continuum (~10³–10⁴
at D=5120); "capacity-bounded, not grammar-bounded"; the P-HOLO-CAP packing
math is the same math aimed at types. P-TYPE-CENSUS pre-reg candidate added
UNFROZEN — count by refusal rank, acceptance-matrix effective rank vs
tolerance, knee-vs-smooth as the symbolic-vs-continuum discriminator.
Captured while the P-HOLO-CAP 32B verdict ran in tmux main:1.)
