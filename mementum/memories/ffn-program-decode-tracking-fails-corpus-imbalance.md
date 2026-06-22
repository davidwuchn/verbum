❌ The §7 FFN program-decode along `fired_sequence` does NOT resolve from the prose
forward pass — it CONFIRMS the s244 splice-closure + the "discrete-opcode-at-L over-reads"
boundary, not opens past it. The corpus S-imbalance is the bottleneck.

s248. Built `scripts/experiments/ffn_program_decode.py` (Qwen3-8B): dual-register decode —
FFN routing register (`mlp.gate_proj`, validated sign-CMR opcode crystal) → which
combinator; attention (`self_attn.o_proj`) → reduction DEPTH via z(WHNF). Ground truth =
saturated-corpus `fired_sequence` (s244). 56 firing items, zone L25-30.

- (A) TRACKING FAILS: neither register decodes a single B-firing item (FFN 0/8, attn 0/8);
  FFN abs-acc 0.232 < majority-S 0.839 (C common-mode drags FFN to C); FFN B-vs-S 0.709 ≈
  majority 0.855 (p=1.0 vs perm) = majority-prediction, not discrimination. "FFN beats attn"
  (0.71 vs 0.36) is attention being NOISIER toward the minority class, not FFN reading opcode.
- (B) LEAD-LAG method-sensitive: xcorr lag +1.5 median, sign-p=0.0027 (FFN z(c*) curve leads
  attn z(WHNF) curve) BUT peak-diff NULL. Read as a weak SCHEDULE-level ordering (boot spiral,
  s240), NOT opcode-specific select→execute (tracking failed).
- (C) RESCUE 9:2 = artifact (all S-items, FFN defaults to majority).
- SPECIFICITY FAILS: non-firing max-z(BSC) 46.8 > firing 20.3 — the symbolic kernel
  firing/non-firing split does NOT map to a model-side magnitude difference.

⇒ The lever stays TYPE-COVERAGE, not geometric/opcode localization.
Artifacts: results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json.

s248 cont. — CLOSED the IOU with a B-BALANCED probe set (`gen_firing_probes.py` →
`data/firing-probes.balanced.jsonl`: 157 probes, 67 B-dom vs 90 B-tied, B-count ladder
{1,2,3,5}; mechanism: S and B are COUPLED, only transitive+existential-object makes B
dominant). Re-ran Qwen3-8B (`--probe-set`):

- ★ THE ONE POSITIVE: B-vs-S discrimination FFN 0.624 (perm p=0.003) BEATS attn 0.522
  (at-null) AND majority 0.573 — the FFN gate register carries WEAK-but-SIGNIFICANT
  B-vs-S opcode info the attention register lacks = register split (FFN=opcode,
  attn=depth) is genuine but SMALL.
- Strong claims STILL fail: absolute decode C-swamped (FFN predicts C 65/67 B-items);
  graded NULL (z(B) doesn't scale with B-count, Spearman 0.06); lead-lag WASHES OUT on
  balanced data (xcorr p=0.16, was 0.003 on the S-skewed corpus = corpus-specific/noise);
  rescue reverses 5:9.

⇒ NOW SURE: the per-combinator program is at best FAINTLY readable (weak FFN>attn B-vs-S,
p=0.003); the strong stored-program tracking/lead-lag claims do NOT survive balanced
probes. Consistent with "β-shaped routing, smeared values" + s244 over-read boundary.
