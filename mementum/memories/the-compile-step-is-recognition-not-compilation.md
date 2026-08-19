💡 The s344 "compile step" is LEXICAL SYNTAX RECOGNITION, not compilation of the
computation (§P-COMPILE-STEP-V2, s344, Qwen3-14B, RECOGNITION, a-priori modal 35).

§P-COMPILE-STEP found only FORMAL notation routes into whnf:*, but the whnf:* poles
are themselves FORMAL-derived → couldn't separate "recognized formal syntax as
reducible" from "compiled the computation." V2 added a 4th level FORMAL_SCRAMBLE:
atom-order shuffle of each frozen formal item (same λ/vars/parens/dots atoms, order
destroyed → no valid reduction; recognition CAN fire, validity CANNOT). formal-vs-
scramble is LENGTH-MATCHED BY CONSTRUCTION.

RESULT: SCRAMBLED formal routes into whnf:* just as much as VALID formal (mass +0.121
vs +0.138), both ~0.36 above prose. ds(formal−scramble) +0.0186 p=0.32 NULL;
dsp(scramble−plain) +0.3619 p=0.0002 carries the whole branch; rep(formal−plain)
+0.3805 p=0.0002 replicates s344 (+0.377). The notation branch is RECOGNITION of
formal syntax, not compilation of the specific computation.

Honest asterisk: ds is a small NON-significant positive (validity increment, if real,
below power). Coheres tape-residency — even the compile-to-whnf gate fires on surface
SYNTAX; the reduction lives on the tape.

METHOD BANKED: the identity rep = ds + dsp (D linear in paired means) makes a 3-level
decomposition exhaustive — COMPILATION = ds carries it, RECOGNITION = dsp carries it,
MIXED = both. A SCRAMBLE (same atoms, order destroyed) is a length-clean validity
control. det 0.0, G0 0.929, len_r_scramble 0.013. Harness compile_step_v2.py (frozen
c09cb514, imports the frozen s344 corpus → exact replication); results
p_compile_step_v2_s344/run_14b.
