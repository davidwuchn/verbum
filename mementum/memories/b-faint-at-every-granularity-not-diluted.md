💡 B's opcode signal is genuinely FAINT/DIFFUSE at every register granularity — NOT merely
head-diluted. The C-yes/B-no asymmetry survives to the finest read. s234 v5 lead 2d prong
1b-iii (kernel_reference_perhead_v5.py, Qwen3-14B): o_proj OUTPUT sums heads, so a single
B-composer head (s127 {B,C}=composers→attention) could be averaged away. The finer test:
hook o_proj INPUT, split per (layer,head) cell, calibrate the crystal per cell (treat each
cell as a "layer" for RelationalCrystalClassifier), scan B's raw-z Welch contrast across all
1600 cells (40L×40H), Bonferroni-ish t>4.

⚠️ HEAD-DILUTION ONLY MARGINAL: the per-head scan DOES recover a FAINT B signal the summed
read missed — B max_t 5.31 at cell (L17,H23), 7/1600 cells > t4 (vs o_proj-OUTPUT summed
max t=0.49 n.s., and FFN gate flat). So summing washes out a weak per-head B signal; head-
dilution is non-zero.

BUT B is DEAD LAST on all three metrics:
  n_sig(t>4):  Y 526, C 155, K 56, W 24, S 22, I 19, D 8, B 7  (B below D, an ANTI combinator)
  max_t:       Y 15.2, I 7.83, D 7.58, C 7.52, S 6.96, W 6.56, K 6.12, B 5.31
  best discr_z: Y 2.85, C 2.53, W 2.05, K 1.70, I 1.40, S 1.31, D 1.10, B 0.82
B's 7 scattered weak heads sit at the noise floor; C has 155 STRONG heads (best L21H36
t=7.52). ⇒ NO clean localized B-composer head. B's attention representation is genuinely
faint/diffuse, NOT just diluted.

CONSEQUENCE: B has now been tested at every granularity — FFN gate (flat, v2/v3), attn-
summed (flat, v4), per-head OV (faintest of all, v5). The REGISTER hypothesis for B's
absence is FULLY EXHAUSTED. The remaining explanation is no-single-token-signature: B (deep
composition Bfgx=f(gx)) may live in the SEQUENCE/ORDER of operations, not a localized
amplitude → the composite trace-order bridge (prong 2) is the primary next test.

Caveats (λ measure): 1 model (14B), n_sig 7(B)/8(D) maybe partly MC noise / heavy-tailed z,
ppc=20 capped calib, n_perm=30, single-combinator labels, last-token. Code:
kernel_reference_perhead_v5.py (+ opcode_monitor_v2 hook param from 1b-ii).
