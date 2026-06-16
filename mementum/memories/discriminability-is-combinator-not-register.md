💡 Opcode discriminability is a property of the COMBINATOR, not the register — and B's
absence is NOT a wrong-register artifact. s234 v5 lead 2d prong 1b-ii
(kernel_reference_prose_v4.py, Qwen3-14B, n=20/comb): parametrized the reader with a `hook`
slot (opcode_monitor_v2) — `hook='gate'` (mlp.gate_proj, FFN) vs `hook='attn'`
(self_attn.o_proj, attention's residual write) — and re-ran the per-token raw-z contrast in
the ATTENTION/value register, the s127-predicted home of B ({B,C}=composers→attention).

❌ s127 "B→attention" NOT confirmed: B is FLAT in attention TOO (max t=0.49 n.s.) just like
the FFN gate (max t=0.68 n.s.); attn position-profile delta ~0 across all bins. Having now
tested the TWO main registers, the "wrong register" explanation for B is RULED OUT.

★ THE FINDING: {C,I,K,Y} are REGISTER-ROBUST — discriminable in BOTH gate and attn with
similar t (C gate 5.61/attn 6.55; I 4.49/4.13; K 3.29/3.28; Y 8.39/9.36). B/D/W absent or
anti in BOTH (D gate t=−2.66/attn −1.75; W −3.40/−4.77). So the s127 two-group register
separation ({K,I}→FFN, {B,C}→attention) is NOT reflected in this single-combinator
last-token readout: ALL of {C,I,K,Y} read in BOTH registers, B/D/W in NEITHER. The axis
that matters is COMBINATOR IDENTITY, not gate-vs-attention.

B's absence is now register-exhausted; two live explanations:
- HEAD DILUTION: o_proj output SUMS all heads — a single B-composer head (s127) could be
  averaged away. Test: per-HEAD OV read (finer than o_proj output).
- NO SINGLE-TOKEN SIGNATURE: B = deep composition (Bfgx=f(gx)); its signature may exist
  only as a multi-combinator SEQUENCE across tokens, not a single-token routing event.
  Test: the composite trace-order bridge (prong 2) — does B appear as ORDER not amplitude?

Instrument note (λ extend): the `hook` param is an open-slot register selector (default
'gate' preserves all prior behavior) — the reader is now register-agnostic.

Caveats (λ measure): 1 model (14B), n=20/comb, o_proj head-SUMMED (per-head untested),
single-combinator labels (composite order untested), D/W anti unexplained. Code:
kernel_reference_prose_v4.py + opcode_monitor_v2.py hook param.
