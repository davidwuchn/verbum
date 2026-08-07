❌ §P-FUEL (s317, qwen3-4b) — VERDICT NO-FUEL-COORDINATE. The de Carvalho
fuel theorem (type-derivation size = evaluation length) does NOT surface as
a readable magnitude in the §P-TYPE-GRAM-1 kind register at static-read
grain. Clean falsifier (a-priori 20%), FU5-sane (kind_margin=4.746 —
register recovered, valid negative not void).

- FU1 fail: raw ρ(Y_type,ℓ)=0.036 BELOW matched-token null (0.132), p=0.994.
- FU2 fail: r_type=0.036 ≈ r_norm=−0.045; random subspaces track ℓ as well
  (p_rand=0.445) — nothing type-specific.
- FU4 fail AND negative: within MATCH (token length held constant) the
  kind-register magnitude DECREASES with ℓ (ρ=−0.538).
- per-family mechanism: LIN +0.392 / DUP +0.375 apparent scaling is SURFACE
  LENGTH (ρ(Y,tok) identical +0.39; ℓ∝tok, ρ(ell,tok)=0.538). MATCH isolates
  ℓ → sign flips negative. FU3 non_idem=+0.355 is the DUP length-confound
  (distinct=1 held), killed by FU2+FU4 — NOT a finding.

Read: de Carvalho concerns the DYNAMIC reduction derivation; we measured a
STATIC single-pass read of an unreduced term. NO-FUEL-COORDINATE is
consistent with fuel being TAPE-RESIDENT (spent during reduction, not
pre-computed as magnitude) — coheres with same-session §P-TYPE-DELIVER (the
type check reads the tape) + tape-resident-reduction thesis. Bounds the §3
Metric leg of normal-forms-are-eigenmodes; §1 Detector + §2 Dynamics
untouched. Sharpest follow-up: trace-integrated type signal ACROSS a
generated reduction, not a static read. Scope: qwen3-4b, kind-subspace
magnitude, static read.

Results 79c76a0. §P-FUEL RESULT on normal-forms-are-eigenmodes.md.
