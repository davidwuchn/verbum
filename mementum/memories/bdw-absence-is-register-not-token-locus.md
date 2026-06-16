💡 The B/D/W opcode-routing gap is a REGISTER property of the FFN gate, NOT a token-locus
artifact. s234 v5 lead 2d prong 1b (kernel_reference_prose_v3.py, Qwen3-14B, n=20/comb)
falsified the cheap explanation. Prong 1 left B/D/W flat at the LAST token; two
hypotheses: (i) token-locus (B resolves mid-sentence, last-token misses it) vs (ii)
register (B lives in attention/value per s127 {B,C}=composers→attention, invisible to the
FFN gate at ANY token). v3 reads ALL token positions (free — forward_all_positions already
returns [T,d]) and contrasts last/max/mean over tokens (Welch t) + a relative-position
profile.

❌ TOKEN-LOCUS FALSIFIED: B does NOT recover at any position — last t=−0.05, **max t=0.68
(n.s., the most lenient read)**, mean t=−0.08. Position profile: B's on−off delta hovers
~0 across all 10 bins (max +0.33), never the clean C separation. D/W stay significantly
ANTI everywhere (D max t=−2.66, W max t=−3.40). ⇒ the FFN gate simply does not carry the
deep/duplicate composers.

✅ The discriminable set {C,I,K,Y} is ROBUST to the read (last/max/mean all significant)
with CHARACTERISTIC position signatures (peak_rel): I early 0.30, K mid 0.48, C mid-late
0.57, Y late 0.79. C's on−off delta is +0.8…+2.0 across the whole back half (on ~+0.6 vs
off ~−1.2). ⚠️ S "discriminates" ONLY under mean-over-tokens (t=4.11; n.s. at last/max) =
the gauge common-mode integrated over the sentence, not a combinator.

CONSEQUENCE (s127 sharpened): we read the FFN GATE → {C,I,K} present, B absent at every
token. C (a composer) LEAKS into the FFN gate but B does NOT. If s127 is right that B is an
attention composer, the value/attention register should find B where the FFN gate cannot.
NEXT (prong 1b-ii): hook o_proj / attention output, build per-layer crystal centroids in
THAT register, run the raw-z contrast — the decisive C-yes/B-no resolver.

Caveats (λ measure): 1 model (14B), n=20/comb, last/max/mean over tokens (register
untested), single-combinator labels, D/W anti unexplained. Code: kernel_reference_prose_v3.py.
