💡 The depth-schedule zones that gate multi-hop composition are pinned WITHIN a model but
DEPTH-PROPORTIONAL across models — not locked to absolute layer indices.

s281 cross-scale depth-budget (wrapper/operand_depthbudget.py, commit 8ceaaec). The
class→covering transform zone (2-hop f(g(X))) sits at ~0.85–0.90 of total depth in BOTH
Qwen3-4B and Qwen3-32B: pinned at L30–31/36 @4B, L58/64 @32B, install-invariant within each.
So s280's "pinned zones" is refined: pinned within-model, proportional across-model. Deeper
model ⇒ the transform lives later in absolute terms; the A1 zone structure scales with the
stack.

Depth is fuel, quantified: the marginal cost of the 2nd hop (D_hop2 = L_max_1hop − L_max_2hop)
collapsed 12 → 4 layers from 4B → 32B; the missed-deadline reader-close moved L25 → L51;
install tolerated to L45 @32B vs L13 @4B. 3-HOP-ROOM = False@4B / True@32B (headroom 36 ≫
cost 4) → pre-registers a 4B-FAIL/32B-PASS 3-hop capacity pair (three-hop-capacity-prereg.md).

Gotcha (λ measure): the frozen BUDGET-VISIBLE/UNMEASURED rule was tuned to the cramped 4B
regime; at 32B it reads UNMEASURED because there is TOO MUCH room (hops stay coupled, no
dissociation band) — the null IS the "more room" finding, not a measurement failure.

Hybrid hint (Qwen3.6-27B, sparse attention): smoke shows the class peak SLID with install
(L47.5→L53), unlike the pinned dense models → sparse attention may loosen zone-pinning
(full run pending). Instrument made architecture-robust via resolve_parts (dense
model.model.layers vs hybrid model.model.language_model.layers).
