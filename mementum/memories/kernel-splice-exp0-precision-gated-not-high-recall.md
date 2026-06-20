💡 s242 Exp 0 (kernel-splice detectability map, Qwen3-14B): NO combinator is splice-ready
for HIGH-RECALL splicing, but PRECISION-GATED splicing IS viable. The naive "detect every
K and splice" fails; "splice only when confident" is supported — and is the SAFE first
causal test.

SCRIPT: kernel_splice_exp0_detectability.py (reuses prose_v2/opcode_monitor_v2 calibration
+ last-token per-layer z; top-1 argmax-over-CRYSTAL per crystal layer vs certified
single-combinator label; precision/recall/F1 + peak layer; 160 test probes, 20/comb).

VERDICT @ strict bar (prec≥0.8 ∧ rec≥0.5): splice-ready set = ∅ (top-1 detection is
common-mode contaminated, s211 η²=0.05). BUT max-PRECISION operating points are strong:
C prec 1.0 @L10 (depth 0.26, recall 0.10), I prec 1.0 @L21 (0.54, recall 0.20), K prec
0.80 @L11 (0.28, recall 0.20), Y prec 0.67 @L20 (0.51, recall 0.40). Loci track s234 depth
signatures (C/K early-mid, I mid, Y late). Discriminability (prose_v2 contrast) ≠ top-1
splice-readiness: a Welch contrast can separate on/off while argmax top-1 is recall-poor.

CAVEAT (λ measure): prec 1.0 from tp=2 = noisy small-n; needs a z-THRESHOLD sweep to map
the precision/recall curve and firm the operating point. NEXT: Exp 1 = precision-FIRST
K-splice at L11 (deliver exact kernel K only on high-confidence detections, validate
output preserved vs random-direction control, s239 protocol). Or Exp 0.5 = z-threshold
sweep first. results/kernel-splice-exp0/exp0_verdict_qwen3-14b.json.
