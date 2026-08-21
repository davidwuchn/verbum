🔁 Method (s349, §P-READ-HEAD-A⋈LEDGER-C, Michael GO after 8B-smoke design-PAUSE):
when a WITHIN-family join is degenerate because the behavior has no variance,
reframe the join to a CROSS-family contrast. Here the join was "does read
mis-attendance predict capture?" but the model is ~uniformly naive (s332) →
naive-vs-hygienic has no variance → ρ_join is nan by construction. Fix: use a
MATCHED CONTROL family for the variance instead. Redefine the competitor
structurally so it exists in BOTH families (IND = the OUTPUT binder position:
capture `\y.y` collision vs control `\y.n` non-collision) → r_control is a real
ratio, not trivially 1. The join becomes D_scope = mean(r_control) −
mean(r_capture) > 0 (two-sample perm) AND behavioral capture confirmed. Three
families form a gradient: nullind (correct source=near binder, r floors) <
capture (correct=far operand, colliding binder tempts near) ⪅ control (correct=
far, no collision, clean). Also: 8B smoke surfaced two plumbing bugs to bank —
multi-char variable names split under the tokenizer (use single letters), and
the body variable FUSES with punctuation (`\y.y`→['\','y','.y'], body y inside
'.y') so match token by ALPHABETIC content (varof), not exact string. (s349)
