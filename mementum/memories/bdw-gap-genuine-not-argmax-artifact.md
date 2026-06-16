💡 The B/D/W prose-discriminability gap is GENUINE at the last-token FFN-gate locus — it
SURVIVES the bottleneck-free raw-z contrast. s234 v5 lead 2d prong 1 (kernel_reference_
prose_v2.py, Qwen3-14B, n=20/comb held-out): lead-2c's discriminability still embedded a
per-layer ARGMAX (route_frac = fraction of layers an op WINS) before the contrast, so
B/D/W — out-competed by the S/Y common-mode at every layer — scored ~0 with no power. FIX:
contrast the RAW per-op z per layer, NO argmax, Welch t-test.

INSTRUMENT WORKS (argmax bottleneck was real): K RECOVERS (discr_z +1.01, t=2.12; was
sub-threshold); C/I sharpen (C +1.73 t=5.71, I +1.89 t=3.83). And the raw-z read is MORE
CONSERVATIVE — at n=20 argmax-discr manufactures a B false-positive (+0.079>0.05) but
raw-z says B is FLAT (on 0.217≈off 0.236, t=−0.05). ⇒ raw-z Welch contrast > argmax
route-frac: more power AND fewer false positives. Same argmax-manufactures-false-* lesson
(s225 AUC, lead 2c), one level deeper.

BUT B/D/W do NOT recover: B flat; D,W significantly ANTI-correlated (D −0.67 t=−4.6,
W −0.63 t=−2.3 — D/W prose routes D/W LESS than baseline). Discriminable set = {C,I,K,Y}.
GAUGE REFINED: S is pure gauge (on 2.70≈off 2.97, discr −0.27); Y genuinely selective
(+2.01, t=6.86). WHERE: discriminable ops peak L12-14 (readable zone) — C@L13 Δ3.70,
I@L13, Y@L14, K@L12; B's only bump is an early L1 wash that vanishes on averaging.

THEORY (s127 ffn-two-groups: {K,I}=selectors→FFN, {B,C}=composers→attention): we read the
FFN GATE → K,I,C discriminable but B not ⇒ C leaks into the FFN gate, B does NOT. B likely
lives in ATTENTION (s206 OV/value register), which a last-token FFN-gate read structurally
cannot see → B's absence is plausibly a LOCUS artifact. NEXT: re-read B in the attention/
value register and/or per-token (prong 1b) — the clean test of the C-yes/B-no split.

Caveats (λ measure): 1 model (14B), n=20/comb, last-token locus (load-bearing for B),
single-combinator labels, D/W anti-signal unexplained. Code: kernel_reference_prose_v2.py.
