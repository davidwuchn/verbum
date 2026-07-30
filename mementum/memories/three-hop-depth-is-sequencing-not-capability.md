💡 3-hop `h(f(g(X)))` over one installed operand COMPOSES at BOTH Qwen3-4B and 32B
(geography chain landmark→city→country→continent, `wrapper/operand_multihop3.py`, s282).

The pre-registered depth-CAPACITY dissociation (4B-FAIL / 32B-PASS) MISSED: both compose
the full chain (Gate-1 4B 0.824 / 32B 0.944, controls PASS, causal bridge-swaps PASS at
both). The s280 accounting (D_hop2=12, 3-HOP-ROOM@4B=False) over-estimated the third-hop
cost — 4B had the room. Reported verbatim (λ measure): the capability prediction was wrong.

The depth signal is REAL but on the SEQUENCING axis (Gate-3a), not capability (Gate-1):
- 4B compresses the two bridges into ONE late window (city=country=L32, continent=L33) —
  3a order FAILS.
- 32B unrolls them SEQUENTIALLY (city L52.5 < country L57.5 < continent L60) — 3a PASSES,
  beats shuffled null.
⇒ depth is fuel for step-by-step UNROLLING, not for whether the chain composes. Coheres
with s280 pinned-late-zone + 27B-hybrid UNPIN (more room → more spreading).

⚠ POST-HOC (chain-passes-but-3a-fails@4B was a surprise; needs its own pre-reg to count as
C8). Scale also cleaned Gate-1/content-spec → layer-vs-scale locus confounded here. A RUNG,
hook-not-weight, pair-not-scaling-law. Frame: capability depth-robust; sequencing depth-scaled.
