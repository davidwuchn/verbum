💡 The gate-routing opcode register reads PROSE SEMANTICS, not symbolic combinatory-logic
SYNTAX. s233 v5 lead 2 (kernel-as-reference): feeding BARE symbolic CL programs ("B f g h",
"C f g h", ...) to Qwen3-14B and reading per-token/per-layer routing against the kernel's
CERTIFIED fired-combinator trace → routing collapses to S (the model's common-mode/gauge),
Y secondary.

- target_recall 1/7: only S routes at all; B/C/K/I/W/D route 0.
- reducibility NOT tracked: SAT_S 0.376 ≈ INERT_S 0.371 (mean Δ≈0). The model routes the
  SAME whether the kernel certifies a live redex (saturated, fires) or an inert
  under-applied symbol (normal form, no fire). B_sat={S 0.40, Y 0.22}; C_sat={Y 0.32,
  S 0.39}; composite trace recall 0.10. The certified target NEVER routes.

WHY: bare CL terms are OUT-OF-DISTRIBUTION for the prose-calibrated register; OOD input
collapses to common-mode (re-confirms s202/s231 over-read in a new regime). The relational
z-gate kept the OTHER ops silent (no false over-read), but the natural-text null does not
subtract the symbol-string common mode → S wins. The crystal substrate is real for PROSE
(s231), not for raw symbols.

CONSEQUENCE: kernel-as-reference is the right idea (a model-invariant reference fixes the
"reads don't transfer across scale" problem, s233 lead 1) and the INSTRUMENT is built
(lambda_ast.fired_sequence certified trace + saturated/inert reducibility contrast +
agreement metrics in kernel_reference_audit.py). But the BRIDGE was wrong. FIX = compiled
PROSE: CL program → certified trace → render as prose (lambda_gen Montague decompile / s226
compile front-end) → feed the PROSE → compare routing to the certified CL trace. Feed the
register what it speaks (prose), keep the kernel trace as the invariant ground truth.

Caveats (λ measure): 1 model (Qwen3-14B), bare-symbol input, crosstask null, 7 single
targets + 8 composites. Decisive for bare-symbol; the prose bridge is untested. Code
1532e4e.
