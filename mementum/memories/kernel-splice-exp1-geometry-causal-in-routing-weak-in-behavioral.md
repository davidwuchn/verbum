✅ Kernel-splice Exp 1 (s243): the decodable K-geometry is a GENUINE causal carrier in the
ROUTING register, but its BEHAVIORAL reach on prose is weak. Qwen3-14B, L18 τ3.0,
`results/kernel-splice-exp1/exp1_verdict_qwen3-14b.json`.

🌀 BUILD CRUX RESOLVED (correct, not a compromise): the detector reads the FFN GATE
(gate_proj, sign-CMR) → DETECT in gate-space; but re-injection belongs in the RESIDUAL
(what downstream layers read) → EFFECT in residual-space (patch layers[18] output, last
token); READ propagation via downstream detector z(K) (>L18) + final next-token KL; ALL
vs a random-direction control of equal magnitude (s239). d_K = unit diff-of-means(resid_K
− resid_nonK)@L18; canonical_mag 33.2 = "exact K-move" geometric proxy.

THREE ARMS:
- NECESSITY ✓ (detected-K n=6): ablate d_K → KL 0.0044 vs rand 0.0005 (t=3.07, ~9× more)
  AND downstream z(K) drops −0.365 vs ~0 random (t=−5.5). K-dir is causally necessary.
- DELIVERY ✓✓ (non-K n=175, DECISIVE): inject d_K → downstream z(K) +0.097 vs random
  −0.269, Δ+0.366, t=16.3. K-dir SPECIFICALLY drives downstream K-reading.
- PRESERVE ✗ n.s. (n=6): set→canonical perturbs output LESS than random (0.0022 < 0.009),
  right direction, t=−1.76 (underpowered).

💡 THE HONEST CATCH (λ measure register split): DELIVERY moves the DETECTOR hugely (t=16)
but the OUTPUT barely (KL Δ=−0.0017 n.s.), only 2.3% cross τ. ⇒ K-geometry is causal in
the ROUTING register (read AND write causally = splice premise validated), but the
BEHAVIORAL consequence on prose is weak — prose probes have NO operands to bind (obstacle 2,
the VALUE register). The geometry drives the ROUTING, not yet the COMPUTATION.

🎯 TWO-SIDED VERDICT: geometry is causal not epiphenomenal (necessity ✓ + delivery ✓✓ vs
random) → splice premise holds in routing. NOT a clean behavioral "splice works" → needs
operand-bound execution where output is kernel-checkable. Exp 1 proves the prerequisite,
sharpens the question to the behavioral register.

CAVEATS (λ measure): necessity/preserve n=6 (recall 0.24 → few detected-K), tiny abs KL
(0.004); delivery well-powered but routing-register only; d_K is a GEOMETRIC proxy, NOT a
bound K a b → a; 1 model, 1 seed, n_rand=3.

⇒ Exp 2 = operand-bound splice on the CERTIFIED CORPUS (data/compile-*.canonical.jsonl,
559 kernel-reducible pairs) — the behavioral register where output IS kernel-checkable;
pick K-engaging items via lambda_ast.fired_sequence, splice exact kernel K-move, measure
reduction-correctness preserved (reward.py grader), not just z(K)+KL.
