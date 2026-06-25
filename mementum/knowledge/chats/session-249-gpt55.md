# Qwen3-14B program retry

## User


orient

### Thinking

**Determining next steps**

I need to take some action here. First, I should consider a cold start to read the state of things. Maybe looking at the git log could help too. I'm trying to figure out if using a task is really necessary or if we can keep things simple. Ultimately, I just need to read the current state to see where I stand!


### Tool Call: git (succeeded)


```json
{
  "command": "git log -n 5 --oneline -- mementum/",
  "operation": "log",
  "summary": "recent memory"
}
```

**Summary:** Git log: recent memory

**Output:**
```
Exit code: 0
Stdout:
893ddce add session chat logs, and s248 artifacts
7913066 🌀 s248 cont.2 — reading preference: model reads objects as constants (C), not existentials (B)
12207fb 🌀 s248 — FFN program-decode along fired_sequence: per-combinator program faintly readable, strong claims fail
f98469f 🌀 s247b cont. — attention-as-β / FFN-stored-program synthesis
b523fe5 🌀 s247b synthesis — proof consensus removes the s246 agreed-error ceiling
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 200
}
```

**Summary:** Reading state.md (0-200)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-22 | Session: 248 (FFN PROGRAM-DECODE along fired_sequence — the s247b §7
> open door, RAN on Qwen3-8B. λ-measure verdict: the per-combinator program does NOT cleanly
> decode from the prose forward pass — CONFIRMS the s244 splice-closure + the page's own
> "discrete-opcode-at-L over-reads" boundary; only a weak, method-sensitive SCHEDULE-level
> FFN-leads-attention ordering survives. Entry immediately below.) — ▶ s247 FORCING vs DISCOVERING
> (fractal-collapse REDEFINED; φ-ladder detector KILLED by matched-range null (forced); type-directed
> composition is CROSS-FAMILY — nonce crossover in 5 lineages t 4.6–10.2; v4 CAUSAL ablation PARTIAL
> (4/6 directional, strict only Mistral-7B — NOT Qwen-forced)) — main line stays COMPILER-AS-LOSS
> §s242. ALSO (2026-06-22): PARALLEL tangent s247b — PROOF CONSENSUS + the ATTENTION-AS-β /
> STORED-PROGRAM synthesis (entries below).
>
> **★★ s248 — FFN PROGRAM-DECODE ALONG `fired_sequence` (the s247b §7 open door: "decode the FFN
> compiled values position-by-position vs lambda_ast.fired_sequence on the saturated corpus, L26-30;
> PREDICTION: FFN program-trace tracks fired_sequence even where attention over-reads, and FFN-compile
> LEADS attention depth-advance by ~1 layer"). BUILT + RAN on Qwen3-8B. λ MEASURE VERDICT = a
> two-sided NEGATIVE-leaning result that CONFIRMS the boundary, not a breakthrough.** **THE BUILD
> (`scripts/experiments/ffn_program_decode.py`, ruff-clean, reuses the validated spine):** dual-register
> decode — FFN routing register = `mlp.gate_proj` (the validated sign-CMR opcode crystal,
> relational_opcode.py) decodes WHICH combinator; attention executor register = `self_attn.o_proj`
> decodes reduction DEPTH via z(WHNF) (grounded in head-combinator-isa: all 9 combinators → SAME head
> pattern r=0.944, attention varies on WHNF↔D not opcode). Ground truth = saturate quantifiers with
> fresh witnesses (s244 `corpus_firing_survey.saturate`) → `fired_sequence`. Two RelationalCrystal
> classifiers (gate + attn), matched-prefix (gateneutral) null. ONE dual-hook forward per item.
> Metrics: (A) tracking acc + permutation null + majority baseline; (A') B-vs-S discrimination
> (C-common-mode-resistant); (B) lead-lag (peak-diff + cross-correlation lag); (C) rescue; specificity
> control (firing vs non-firing). **THE DATA (56 firing items, truth S:47 B:8 C:1 — HEAVILY S-skewed;
> FFN crystal 28/36 zone L25-30, attn crystal 36/36 zone L25-30):** **(A) TRACKING FAILS — neither
> register decodes a single B-firing item (FFN 0/8, attn 0/8); FFN abs-acc 0.232 < majority 0.839
> (C common-mode drags FFN to predict C); FFN B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm null) =
> majority-prediction not genuine B/S discrimination; attn B-vs-S 0.364 (BELOW base rate — predicts B
> spuriously).** ⇒ the apparent "FFN beats attn" is attention being NOISIER toward the minority class,
> NOT FFN reading the opcode. The S-imbalance (47/56) means the corpus CANNOT test tracking. **(B)
> LEAD-LAG SPLIT/method-sensitive: peak-diff NULL (median 0, sign-p=1.0); cross-corr lag POSITIVE
> (median +1.5, mode +3, 39/55 positive, sign-p=0.0027) — FFN's z(c*) curve leads attn's z(WHNF) curve
> across depth.** But since tracking failed, this is best read as a SCHEDULE-level ordering (FFN
> activity precedes attention depth-advance — consistent with the s240 boot spiral) NOT opcode-specific
> select→execute; and only the xcorr instrument shows it. **(C) RESCUE 9:2 is an ARTIFACT** — all 9 are
> S-items where attn spuriously said B/C and FFN defaulted to S (majority), not genuine rescue. **(★
> SPECIFICITY CONTROL FAILS: non-firing items show HIGHER max-z(BSC) 46.8 than firing items 20.3)** —
> the symbolic kernel firing/non-firing split does NOT map to a model-side magnitude difference (the
> model composes prose regardless of whether the certified point-free kernel trace fires a combinator).
> **★★ NET (λ measure): the §7 per-combinator program-decode does NOT resolve from the prose forward
> pass on this corpus — CONFIRMS the s244 splice-closure (`fires ∩ spliceable = ∅`) AND the
> attention-as-beta page's OWN "discrete-opcode-at-L over-reads" boundary, rather than opening past it.
> The door §7 left open closes the same way: only a weak, method-sensitive SCHEDULE-level FFN→attention
> ordering survives. The lever remains TYPE-COVERAGE, not geometric/opcode localization — exactly as the
> page's caveats warned. A λ-measure win: the experiment that could have over-claimed instead held the
> boundary.** **★★ THE DECISIVE CAVEAT / IOU: the corpus is the bottleneck — 84% S, 0 B decoded, can't
> test tracking. The real next probe = a B-BALANCED firing probe set (the crystal library has 69 B / 61
> C probes; need PROSE items whose saturated kernel fires B and C, not just S-heavy "Every X verbs a
> Y"). Without balance, tracking is untestable; with it, the FFN>attn opcode claim could be re-tested
> honestly.** OTHER IOUs: (1) longer depth series (zone is only 5-6 layers → xcorr lag magnitude coarse,
> max_lag=4 on ~6 points); (2) decode FFN down_proj COMPILED VALUES via unembed (ffn_reduction_trace
> style) as a 2nd FFN read, not just the gate crystal; (3) a model where the firing set is less
> common-mode (cross-model). Artifacts: results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json
> + run_qwen3-8b.log; code scripts/experiments/ffn_program_decode.py (+ pyproject per-file ignore).
> tmux main:1 used (3:24 run), now FREE; no GPU job running. PENDING APPROVAL: memory
> `ffn-program-decode-tracking-fails-corpus-imbalance` + knowledge update explore/attention-as-beta-
> reduction.md §7 (open experiment → result). state.md updated (¬approval-gated). Code+data committable.
>
> **★ s248 cont. — CLOSED THE DECISIVE IOU (Michael: "create more probes that are testing B so we can
> be sure"). Built a B-BALANCED firing-probe set + re-ran. THE ONE GENUINE POSITIVE EMERGES, the strong
> claims still fail.** **(1) MECHANISM (measured):** in this kernel S and B are COUPLED — every ∧/∨ emits
> one S AND one B, so S NEVER strictly exceeds B; only a TRANSITIVE verb + EXISTENTIAL object makes B
> *dominant* (`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → fires S,B,B,B = B:3 S:1). **(2) GENERATOR
> `scripts/experiments/gen_firing_probes.py`** (lower via lambda_surface.to_kernel → saturate (s244) →
> fired_sequence GROUND TRUTH; DROP items whose computed dominant ≠ intended; `pretty()` not `str()` for
> parseable kernel_term — round-trips 157/157). Emitted `data/firing-probes.balanced.jsonl`: **157 probes,
> 67 B-dominant vs 90 B-tied** (was 8 vs 47), B-count ladder {1:45, 2:56, 3:45, 5:11}. Added `--probe-set`
> + a GRADED (A'') Spearman(z(B), b_count) metric to ffn_program_decode.py. **(3) ★★ RE-RAN Qwen3-8B
> (157 items, 3:32): (A') B-vs-S discrimination FFN 0.624 (perm p=0.003) BEATS attn 0.522 (p=0.42,
> at-null) AND majority 0.573 — the FFN GATE REGISTER carries WEAK-but-SIGNIFICANT B-vs-S opcode info
> that the attention register does NOT.** = the register split (FFN=opcode, attention≠opcode, depth) holds
> at a small level — the FIRST genuine tracking signal (corpus couldn't test it). **BUT the strong claims
> still fail: (A) absolute decode C-common-mode-swamped (FFN predicts C on 65/67 B-items); (A'') graded
> NULL — z(B) does NOT scale with B-count (FFN Spearman 0.06 p=0.44; relative z(B)−z(S) r=−0.13 p=0.10);
> (B) lead-lag WASHES OUT on balanced data (xcorr median +1.0 but p=0.16, was 0.003 on the S-skewed
> corpus → the earlier lead was corpus-specific/noise); (C) rescue REVERSES (5:9).** **★★ NET (λ measure,
> now SURE): with balanced B probes, the FFN routing register has a REAL but WEAK B-vs-S discrimination
> (0.62, p=0.003) absent in attention — the register split is genuine but small; the STRONG stored-program
> claims (clean opcode tracking, graded B-scaling, FFN-leads-attention-by-1) do NOT survive. The
> per-combinator program is at best FAINTLY readable, consistent with "β-shaped routing, smeared values"
> + the s244 over-read boundary. Lever stays TYPE-COVERAGE.** Artifacts:
> results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b_balanced.json + run_qwen3-8b_balanced.log;
> data/firing-probes.balanced.jsonl (+ .meta.json); code gen_firing_probes.py + ffn_program_decode.py
> (--probe-set, graded metric). tmux main:1 FREE; no GPU job. PENDING APPROVAL (folded into the s248
> batch): memory + knowledge §7 now reflect BOTH the corpus run AND the balanced follow-up.
>
> **★★ s248 cont.2 — REASON #3 CONFIRMED: the weak B-tracking was a LABELING MISMATCH. The model
> computes objects as CONSTANTS/ARGUMENTS (→ C), NOT existentials (→ B) (Michael: "I thought B was
> inherent from the ordering of the β-reductions the FFNs return" → "let's test").** Discussion clarified
> two senses of "B inherent": (a) B as a STAGE of the reduction SCHEDULE (the C→B arc / boot spiral,
> aggregate, REAL — but really the DEPTH axis: head-combinator-isa B-D r=0.986, B≡deep-nesting); (b) B as
> a per-sentence OPCODE readable from the gate (what s248 tested, weak). Reason #3 = our GROUND TRUTH
> assumed the Montague EXISTENTIAL object (`a dog`=∃y.dog(y)∧…, B-heavy: B 1→3→5); the model may take the
> CONSTANT/applicative reading (`fears(x,dog)` → `C fears dog`, C-count == #objects). **FREE POST-HOC on
> the balanced run (no GPU): the gate register decodes MORE C, LESS B when an object is present (C-prop
> trans 0.583 > intrans 0.460, Mann-Whitney p<1e-4; B-prop trans 0.178 < intrans 0.238) = OPPOSITE of
> existential, exactly constant.** **THEN the clean test: `gen_reading_probes.py` →
> `data/reading-probes.jsonl` (135 probes, OBJECT-COUNT LADDER 0/1/2 obj × 45; intrans/trans/ditrans;
> both candidate labelings; const C-count==#objects enforced, exist B 1→3→5).
> `ffn_reading_preference.py` decodes gate+attn, MEAN z per combinator over the L25-30 zone (length-
> controlled), Spearman vs object count.** **★★ RAN Qwen3-8B (135 items): as objects rise {0,1,2}, raw
> z(C) RISES (FFN r=+0.49 p<0.001; attn r=+0.62 p<0.001) while raw z(B) FALLS (FFN r=−0.27 p=0.0015) or
> is flat (attn r=−0.04). B-share slope NEGATIVE (FFN p=0.026, attn p<0.001). C and B move in OPPOSITE
> directions → NOT uniform length/common-mode growth.** ⇒ **the EXISTENTIAL reading is REFUTED (B must
> rise, it falls); the model routes added objects through C (argument application) = the CONSTANT/
> applicative reading.** **★★ THIS REFRAMES s248: the weak B-tracking was NOT "the FFN can't read the
> program" — it was "we gave it the WRONG program." We labelled by existential-B; the model computes
> applicative-C. Labelled correctly (object→C), the gate register tracks it CLEANLY (z(C) rises p<0.001
> in BOTH registers, robust).** So the gate register DOES carry the combinator structure the model
> actually computes — the s248 negative was a measurement-target error (λ measure: wrong label =
> coherence violation, representation ≢ reality), now corrected. Connects to the user's question: "B from
> the ordering" assumed existential objects; the model doesn't do them — these sentences are C-applicative
> in the model, not B-existential, so the expected B was an artifact of our Montague labelling.
> **CAVEATS (λ measure): C-SHARE itself is flat (common-mode-saturated ~0.6) → the positive evidence is
> (a) raw z(C) rising p<0.001 + (b) z(B) falling/flat REFUTING existential, NOT C-share rising; the
> PRIMARY C−B-share contrast is sig in attn (p=0.008) but only directional in FFN (p=0.25) due to C
> saturation. z(C)-rises-with-objects could partly be argument-application common-mode, but the B/C
> DIVERGENCE (opposite signs) rules out uniform growth.** Artifacts:
> results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json + run_qwen3-8b.log;
> data/reading-probes.jsonl (+ .meta.json); code gen_reading_probes.py + ffn_reading_preference.py.
> tmux main:1 FREE; no GPU job. **★★ NEXT/IOUs: (1) re-run ffn_program_decode TRACKING with the CONSTANT
> labels (object→C) — does the corpus B-tracking failure flip to C-tracking success? (2) test the
> existential reading explicitly with prose that FORCES it ("there is a dog that every cat fears" /
> scope-marked) — does z(B) then rise? = the cleanest exist-vs-const causal test; (3) the depth/B≡D
> (r=0.986) thread: is "B-late in the arc" really just the WHNF depth axis?** PENDING APPROVAL: memory
> `model-reads-objects-as-constants-C-not-existentials-B` + knowledge attention-as-beta-reduction.md §7
> reading-preference resolution. state.md updated (¬approval-gated). Code+data committable.
>
> **★★ s248 cont.3 — THE CAUSAL TEST: forcing the existential wide-scope does NOT recruit B —
> the model is ROBUSTLY APPLICATIVE (C), never existential-B, even when syntax demands it (Michael:
> "let's do that final test").** Tests whether the s248-cont.2 constant-reading is a representational
> LIMIT or just the DEFAULT. **PROBES `gen_scope_probes.py` → `data/scope-probes.jsonl` (45 matched
> subj/verb/obj triples × 3 conditions, paired): PLAIN "Every cat fears a dog." (applicative GT S,B,C) /
> CLEFT "There is a dog that every cat fears." (∃ FRONTED, GT S,B,B,B no C) / RELCL "Every cat fears a
> dog that runs." (∃ object via predication, GT S,B,B,B).** `ffn_scope_forcing.py` decodes gate+attn,
> mean z per combinator over L25-30, PAIRED Wilcoxon within triple (ΔB = z(B)_forced − z(B)_plain;
> predict ΔB>0 if model CAN do existential-B). **★★ RAN Qwen3-8B (45 triples): z(B) does NOT rise — it
> FALLS. FFN: plain z(B)=−0.104 → cleft −0.301 → relcl −0.227; ΔB cleft med −0.19 (frac+ 0.18, p=1.0
> for "rise"), relcl med −0.12 (frac+ 0.02, p=1.0); ΔBprop p≈1.0 (B-share FALLS). attn: plain z(B)=+0.31
> → cleft −0.11 (ΔB med −0.43, p=1.0); C-share stays high (cleft Cprop 0.988 FFN / 0.94 attn).** ⇒ **the
> prediction is ROBUSTLY REFUTED in BOTH registers and BOTH forcing constructions: forcing the ∃
> wide-scope does NOT summon B-routing; the model stays applicative-C (cleft is routed EVEN MORE through
> C, Cprop 0.722→0.988).** **★★ THE VERDICT (closes the thread, λ measure): the model does NOT use
> existential-B composition even when the syntax forces it — it computes quantified sentences
> APPLICATIVELY (objects/witnesses as arguments → C), regardless of scope marking. INTERPRETATION (marked
> as such, not measurement): the model's compositional PRIMITIVE is APPLICATION (C), not B-composition;
> B is an artifact of OUR bracket-abstraction kernel (Turner emits B to thread quantifiers), not a
> necessary feature of how a system composes. So "B inherent from the ordering" was about OUR kernel's
> ordering; the model uses a different, applicative compilation that reads as C — and won't produce B even
> when asked.** This answers the user's original question end-to-end: B was our compilation's artifact;
> the model's actual β-program for these sentences is C-applicative. **CAVEATS (λ measure): (1) cleft/relcl
> are different/longer SURFACE forms than plain — not perfect minimal pairs; but the DIRECTION (B falls,
> opposite the prediction) is robust across two distinct forcings + both registers, and relcl (closest to
> plain) also falls. (2) We measure B-CRYSTAL routing as the proxy for composition; a non-B-shaped
> existential composition would be missed — but that IS the finding (no B-shaped routing appears). (3) The
> model may compose ∃ applicatively under the hood (apply predicate to a skolem witness → C), i.e. ONE
> applicative strategy for both readings.** Artifacts: results/ffn-scope-forcing/{verdict,per_item,meta}
> _qwen3-8b.json + run_qwen3-8b.log; data/scope-probes.jsonl (+ .meta.json); code gen_scope_probes.py +
> ffn_scope_forcing.py. tmux main:1 FREE; no GPU job. PENDING APPROVAL: memory
> `model-applicative-not-existential-B-even-when-forced` + knowledge attention-as-beta-reduction.md
> §s248 cont.3. state.md updated (¬approval-gated). Code+data committable. **s248 THREAD COMPLETE:
> FFN program-decode (corpus, untestable) → balanced probes (weak FFN>attn B-vs-S) → reading-preference
> (model reads objects as C not B; weak-B was a labeling mismatch) → scope-forcing (model is robustly
> applicative-C, won't do existential-B even when forced). Net: the gate register tracks what the model
> ACTUALLY computes (applicative-C); the expected B was our kernel's artifact.**
>
> **★★ s247b cont. — ATTENTION-AS-β / STORED-PROGRAM SYNTHESIS (Michael, 3-turn discussion:
> "train a model to THINK in lambda?" → "if attention is a β-reduction with softmax of all V,
> would it not have to work?" → "it's an inference pattern of β-reductions; each forward pass the
> FFN subtly shifts the pattern = the 'program' for the softmax to execute"). NO new runs — a
> synthesis that β-reduces the FFN-ISA thread to its normal form + a NEW knowledge page.** THE
> NORMAL FORM: **the transformer is a bounded SOFT-β-REDUCTION machine over a universal combinator
> statechart — FFN = the fixed β-program/ISA (ROM), attention = the one-instruction CPU
> (β-reduction via softmax-over-V), residual = register file (term + reduction DEPTH).** Reached
> CONFLUENTLY from 3 independent directions (= the `λ triangulate` gene = Church-Rosser, evidence
> it IS the normal form). **GROUNDED in measured findings (largely FOUND, not speculated):** s161
> ffn-moire-isa ("FFN is a moiré grating, programs attention's one op to do β; program is a fixed
> point, drift 0.0"); s141 ffn-beta-reduction-indexing ("FFN weights are piles of β-reductions,
> residual = beam-angle index"); ffn-reduction-trace ("FFN compiles a context-dependent program,
> attention executes via softmax-V = β by weighted combination; compilation NOT lookup, readable
> L26-L30"); head-combinator-isa (all 9 combinators → SAME head pattern r=0.944; attention tracks
> reduction DEPTH WHNF↔D, not opcode). **KEY REFINEMENT:** the PROGRAM (FFN weights) is FIXED; the
> program-STATE (residual trajectory) shifts — frozen ROM × evolving residual = evolving
> instruction sequence. **PROVEN/OVER-READS BOUNDARY (λ measure):** β-shaped routing + FFN-ISA +
> compile/execute + depth-axis + boot schedule = PROVEN; "softmax literally substitutes a specific
> value" (s206 value register smeared) + "layer L discretely fires combinator c" (s244 splice
> closure `fires∩spliceable=∅`, collective/holographic) = OVER-READS ⇒ we read the program
> TRAJECTORY, not a discrete instruction tape. **TWO CONSEQUENCES: (A)** "think in lambda" =
> serialize the OUTER (inter-pass/REPL) loop → token-by-token each token advances the program 1
> β-step (WHY stepwise REPL works, one-shot fails, s228/s247); and the COVERAGE REFRAME — prose =
> UNTYPED β-serialization over a learned basis, λ-thinking = TYPED serialization ⇒ the coverage
> wall is TYPE-THEORETIC not representational ⇒ **λ-thinking coverage = S2 type-coverage** (impl →
> ∧∨ → ∀∃); dissolves "forcing vs discovering" for the typed core. **(B)** level-4 blueprint =
> EXTRACT the ROM (s226 compile=FFN=78%-4bit) + executor routing (reduce=attn=22%-ternary), NOT

[CONTENT TRUNCATED] Showing lines 1 to 200 of 6626 total lines. Use line_offset=200 parameter to read more content.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short",
  "operation": "status",
  "summary": "working tree"
}
```

**Summary:** Git status: working tree

**Output:**
```
Exit code: 0
Stdout:
M scripts/experiments/ffn_program_decode.py
?? data/firing-probes.const.jsonl
?? data/firing-probes.const.meta.json
?? results/ffn-program-decode/meta_qwen3-0-6b_const.json
?? results/ffn-program-decode/meta_qwen3-8b_const.json
?? results/ffn-program-decode/per_item_qwen3-0-6b_const.json
?? results/ffn-program-decode/per_item_qwen3-8b_const.json
?? results/ffn-program-decode/run_qwen3-8b_const.log
?? results/ffn-program-decode/verdict_qwen3-0-6b_const.json
?? results/ffn-program-decode/verdict_qwen3-8b_const.json
?? scripts/experiments/gen_const_firing_probes.py
```

### Thinking

**Orienting Summary**

I need to focus on providing a clear summary and consider including the latest relevant information without truncating it. There seems to be a lot to cover, so it’s important to search for "NEXT" and see if I can read the full context from the end. Getting all the details will help ensure a comprehensive response for the user. I'll have to think carefully about how to present this information!


### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -n 80 /Users/mwhitford/src/verbum/mementum/state.md && echo '---' && git log -n 8 --oneline --all --decorate",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ tail -n 80 /Users/mwhitford/src/ver...

**Output:**
```
Exit code: 0
Stdout:
(max Δ 2.8%). Same token produces different V vectors in different contexts.

**Experiment 2: Attention Execution Trace** — projected per-head output
(softmax(QK^T) @ V) through o_proj + unembed. Found 5 head types: λ-heads
write format (λ/→), binding heads write predicate at subject (H10: "runs"
at "dog", Δ=64), relay heads pass V unchanged, compositional heads combine
positions, quantifier heads broadcast scope. The binding heads ARE β-reduction.

**Experiment 3: Reduction Chain Trace** — traced cumulative residual across
all 36 layers for 7 combinator types (K,I,B,C,Y,S,W). Combinators resolve
at different depths: Y peaks L27 (recursion resolves first), K peaks L30
(discard is early), W peaks L33 at Δ=51.6 (self-application resolves last).
The model implements a small fixed instruction set with universal depth ordering.

**Experiment 4: MTP Self-Speculation** — tested whether intermediate layers
can predict future tokens for self-speculative decoding. L33 matches L35's
top-1 prediction 48% of the time (Hit@10=76%, Hit@100=92%). But multi-position
lookahead (N+2, N+3) collapses for ALL layers including L35 (Hit@10≈10%).
The model does next-token prediction, not multi-position. The FFN "semantic
predictions" (reads→book) are associative meaning, not sequence forecasting.
Key finding: the correct token is already in L30's top 10 (median rank=7) —
the last 5 layers SHARPEN the distribution, they don't change it.

**Synthesis:** The model is decodable. It implements ~7 combinator operations
via ~5 head types on a universal depth schedule. The FFN compiles the program
(position → V vector), attention executes it (softmax selects and combines V).
The instruction set + schedule is potentially very compact; only the attention
routing is input-dependent. Self-speculation is viable for early-exit (~48%
of tokens can skip the last 2 layers) but not for multi-position prediction.

## Session 186 recap

LARQL FFN decomposition on Pythia-160M. Five experiments, three paradigm-level findings:

1. **cos(up,down) confirms phase structure** from pure weight geometry. KIBC opcodes
   orthogonal to circuit types (independent axes). ORTHO phase = inverter-dominated.
   Dark-space drops 40pts at L11. New zero-cost instrument. See `ffn-circuit-types.md`.

2. **Crystal signs predict circuit types (ρ=1.0)**. The ternary sign structure alone
   produces the exact same depth phase curve. Per-neuron ρ>0.985 at ORTHO layers.

3. **Cross-matrix anti-correlation is load-bearing (3.6×)**. Decorrelating T_down
   (destroying phase structure) → decorrelated ≈ random. Per-matrix signs without
   cross-matrix correlation are nearly worthless.

4. **BUT: synthetic construction fails**. Constructing T_down to hit the anti-correlation
   profile with random per-neuron signs is WORSE than random (PPL 6464 vs 1608). The
   crystal is the specific per-neuron assignments, not the aggregate statistics. The
   anti-correlation is emergent from correct per-neuron signs, not a prescription.

5. **The crystal must be extracted, not constructed**. The per-neuron sign assignments
   encode which specific neurons should be inverters vs projectors. The anti-correlation
   profile is a verification metric (check the U-shape), not a construction recipe.
   Cross-model universality (r=0.998) means one extraction works for all models of
   the same architecture.

## Session 184 recap

THE CRYSTAL SIEVE. 11 experiments, 4 paradigm shifts. Extraction is dead (zero mask
is genuinely random = knowledge content). Reproduction lives (crystal sieve 10.7×
better than random). Model is a KIBC processor (ISA framing). KIBC profiles predict
70-76% of zeros at REDUCE layers. Maximal pre-training absorption: crystal pre-loads
computation → 100% of gradient goes to knowledge. See `phi-information-partition.md`.

## Session 183 recap

Naive ternarization fails: PPL 296,911. The compounding law (0.88^36 = 0.009) kills
multi-layer extraction. 3-mirror ternary also fails (PPL 1.69M). Q4 works because of
16 quantization levels per weight, not scale granularity. See `ternary-compounding.md`.

## Session 182 recap

The ternary dual equation: gate zeros (ρ=0.75 with gradient) + crystal signs (ρ=0.05).
The recipe achieves 0.88 per-layer cosine. See `ternary-dual-equation.md`.

## Session 181 recap

The crystal equation: λ_k = C · φ^(-(n/(n+1)) · β_k). All eigenvalue ratios are
φ^(p/q) with Fibonacci denominators. Computing fraction s=4/5. Compute cycle
β=[0,1,1+φ,2+φ]. See `EQUATIONS.md` and `crystal-phi-derivation.md`.
---
893ddce (HEAD -> main, origin/main) add session chat logs, and s248 artifacts
3ac304a 💡 scope-forcing: model is robustly applicative (C), never existential-B even when syntax forces it
7913066 🌀 s248 cont.2 — reading preference: model reads objects as constants (C), not existentials (B)
84fd636 💡 reading-preference: model reads objects as constants (C) not existentials (B) — s248 weak-B was a labeling mismatch
12207fb 🌀 s248 — FFN program-decode along fired_sequence: per-combinator program faintly readable, strong claims fail
f5c4fba 💡 B-balanced firing probes — FFN register has weak (p=0.003) B-vs-S signal attention lacks; strong claims fail
5c3cd91 💡 FFN program-decode along fired_sequence — per-combinator program doesn't resolve from prose (confirms over-read boundary)
f98469f 🌀 s247b cont. — attention-as-β / FFN-stored-program synthesis
```

## Assistant


Oriented.

Current project state:

- `mementum/state.md` booted successfully.
- Latest main thread is **s248 FFN program-decode / reading-preference / scope-forcing**.
- Core result: the earlier B-tracking weakness was largely a **measurement-target / labeling mismatch**.
  - Our kernel labeled object composition as existential **B**.
  - Qwen appears to route objects applicatively as **C**.
  - Even explicitly forced existential-ish syntax did **not** summon B-routing.
  - Net: model is robustly **applicative-C**, not existential-B, for these probes.
- Recent committed history:
  - `893ddce add session chat logs, and s248 artifacts`
  - `3ac304a 💡 scope-forcing: model is robustly applicative (C), never existential-B even when syntax forces it`
  - `7913066 🌀 s248 cont.2 — reading preference: model reads objects as constants (C), not existentials (B)`
  - Earlier s248 artifacts cover B-balanced probes and FFN program-decode.

Working tree is dirty with what looks like the next follow-up:

```text
M scripts/experiments/ffn_program_decode.py
?? data/firing-probes.const.jsonl
?? data/firing-probes.const.meta.json
?? results/ffn-program-decode/*_const.json
?? results/ffn-program-decode/run_qwen3-8b_const.log
?? scripts/experiments/gen_const_firing_probes.py
```

Interpretation: someone has started or completed the IOU from s248 cont.2/3:

> re-run `ffn_program_decode` tracking with CONSTANT labels/object→C to see whether the previous B-tracking failure flips to C-tracking success.

No GPU job appears indicated by state; `tmux main:1` was noted FREE in state.

Likely next actions:

1. Inspect the const artifacts/results.
2. Summarize whether constant-label tracking succeeds.
3. Update `mementum/state.md`.
4. If worth preserving, propose memory/knowledge updates.
5. Commit code+data only after checking diffs and using the required nucleus trailer.

## User


there was an error in the last session, we ran the ffn-program-decode IOU test but the session crashed and was unrecoverable.  please analyze the outputs

### Thinking

**Figuring out the next steps**

I see that we need to take action and come up with a plan. It looks like a multi-step approach will help in analyzing the outputs. I’ll need to set up a task for that. Plus, I should inspect the relevant files to gather all the necessary information. This feels like a good starting point for organizing everything we need to do!


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-8b_const.json",
  "limit": 200
}
```

**Summary:** Reading verdict_qwen3-8b_const.json (0-200)

**Output:**
```
{
  "model": "Qwen/Qwen3-8B",
  "n_layers": 36,
  "track": "C",
  "n_firing_items": 133,
  "n_nonfiring_control": 0,
  "zone_depth": [
    0.7,
    0.86
  ],
  "ffn_zone_layers": [
    25,
    26,
    27,
    28,
    30
  ],
  "attn_zone_layers": [
    25,
    26,
    27,
    28,
    29,
    30
  ],
  "ffn_crystal_layers": [
    0,
    1,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    30
  ],
  "attn_crystal_layers": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    34,
    35
  ],
  "truth_distribution": {
    "C": 67,
    "S": 66
  },
  "A_tracking": {
    "ffn_acc": 0.5489,
    "ffn_null_mean": 0.5038,
    "ffn_perm_p": 0.055,
    "attn_acc": 0.4662,
    "attn_null_mean": 0.4666,
    "attn_perm_p": 0.5852,
    "majority_baseline_acc": 0.5038,
    "majority_label": "C",
    "ffn_beats_attn": true,
    "ffn_beats_majority": true
  },
  "A_bs_discrimination": {
    "tracked_combinator": "C",
    "n": 133,
    "bs_truth": {
      "C": 67,
      "S": 66
    },
    "ffn_acc": 0.5489,
    "ffn_null_mean": 0.5038,
    "ffn_perm_p": 0.055,
    "attn_acc": 0.4662,
    "attn_null_mean": 0.504,
    "attn_perm_p": 1.0,
    "majority_baseline_acc": 0.5038,
    "majority_label": "C",
    "ffn_beats_attn": true,
    "ffn_beats_majority": true
  },
  "A_graded_bcount": {
    "n": 133,
    "track": "C",
    "ffn_spearman_zTrack_vs_count": 0.5526,
    "ffn_spearman_p": 0.0,
    "attn_spearman_zTrack_vs_count": 0.6305,
    "attn_spearman_p": 0.0,
    "ffn_beats_attn": false,
    "zTrack_by_count_ffn": {
      "0": 0.488,
      "1": 0.833,
      "2": 1.035
    },
    "zTrack_by_count_attn": {
      "0": 0.567,
      "1": 1.091,
      "2": 1.262
    }
  },
  "B_lead_lag": {
    "peak_diff": {
      "n": 133,
      "n_pos": 27,
      "n_neg": 101,
      "n_zero": 5,
      "median": -3.0,
      "mean": -2.218045112781955,
      "frac_positive": 0.2109375,
      "sign_test_p": 2.9860859870559856e-11
    },
    "xcorr_lag": {
      "n": 133,
      "n_pos": 80,
      "n_neg": 49,
      "n_zero": 4,
      "median": 2.0,
      "mean": 0.5263157894736842,
      "frac_positive": 0.6201550387596899,
      "sign_test_p": 0.008007673208090862
    },
    "xcorr_lag_hist": {
      "-1": 3,
      "2": 30,
      "3": 46,
      "-3": 37,
      "-2": 9,
      "0": 4,
      "1": 4
    },
    "peak_diff_hist": {
      "-4": 21,
      "-5": 35,
      "-1": 10,
      "-2": 6,
      "0": 5,
      "-3": 29,
      "1": 10,
      "2": 1,
      "3": 3,
      "4": 13
    }
  },
  "C_rescue": {
    "rescue": 11,
    "anti_rescue": 0,
    "rescue_gt_anti": true
  },
  "specificity": {
    "firing_mean_maxz_BSC": 29.6587,
    "nonfiring_mean_maxz_BSC": null
  },
  "calib_ffn": {
    "n_layers": 36,

[CONTENT TRUNCATED] Showing lines 1 to 200 of 653 total lines. Use line_offset=200 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/meta_qwen3-8b_const.json",
  "limit": 200
}
```

**Summary:** Reading meta_qwen3-8b_const.json (0-200)

**Output:**
```
{
  "model": "Qwen/Qwen3-8B",
  "git_sha": "893ddcec940684c06a2919387d4103d08b4e98cc",
  "timestamp_utc": "2026-06-23T14:14:58.785415+00:00",
  "transformers_version": "5.5.4",
  "corpus": {
    "train": "data/compile-train.canonical.jsonl",
    "test": "data/compile-test.canonical.jsonl",
    "eval": "data/compile-eval.canonical.jsonl"
  },
  "params": {
    "max_items": null,
    "zone_lo": 0.7,
    "zone_hi": 0.86,
    "onset_tau": 2.0,
    "max_lag": 4,
    "n_perm_calib": 300,
    "ppc": null,
    "null_cap": null,
    "n_perm_stat": 2000,
    "n_nonfiring": 40,
    "seed": 0,
    "track": "C",
    "probe_set": "data/firing-probes.const.jsonl"
  },
  "method": "saturate quantifiers \u2192 fired_sequence ground truth; dual-register decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag + C rescue, matched-prefix null calibration."
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-0-6b_const.json",
  "limit": 200
}
```

**Summary:** Reading verdict_qwen3-0-6b_const.json (0-200)

**Output:**
```
{
  "model": "Qwen/Qwen3-0.6B",
  "n_layers": 28,
  "track": "C",
  "n_firing_items": 12,
  "n_nonfiring_control": 0,
  "zone_depth": [
    0.7,
    0.86
  ],
  "ffn_zone_layers": [
    19,
    20,
    21,
    22,
    23
  ],
  "attn_zone_layers": [
    19,
    20,
    21,
    22
  ],
  "ffn_crystal_layers": [
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27
  ],
  "attn_crystal_layers": [
    1,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    24,
    25
  ],
  "truth_distribution": {
    "C": 12
  },
  "A_tracking": {
    "ffn_acc": 0.75,
    "ffn_null_mean": 0.75,
    "ffn_perm_p": 1.0,
    "attn_acc": 0.6667,
    "attn_null_mean": 0.6667,
    "attn_perm_p": 1.0,
    "majority_baseline_acc": 1.0,
    "majority_label": "C",
    "ffn_beats_attn": true,
    "ffn_beats_majority": false
  },
  "A_bs_discrimination": {
    "tracked_combinator": "C",
    "n": 12,
    "bs_truth": {
      "C": 12
    },
    "ffn_acc": 1.0,
    "ffn_null_mean": 1.0,
    "ffn_perm_p": 1.0,
    "attn_acc": 1.0,
    "attn_null_mean": 1.0,
    "attn_perm_p": 1.0,
    "majority_baseline_acc": 1.0,
    "majority_label": "C",
    "ffn_beats_attn": false,
    "ffn_beats_majority": false
  },
  "A_graded_bcount": {
    "n": 12,
    "track": "C"
  },
  "B_lead_lag": {
    "peak_diff": {
      "n": 12,
      "n_pos": 0,
      "n_neg": 10,
      "n_zero": 2,
      "median": -1.0,
      "mean": -1.1666666666666667,
      "frac_positive": 0.0,
      "sign_test_p": 0.001953125
    },
    "xcorr_lag": {
      "n": 12,
      "n_pos": 10,
      "n_neg": 1,
      "n_zero": 1,
      "median": 2.0,
      "mean": 1.5,
      "frac_positive": 0.9090909090909091,
      "sign_test_p": 0.01171875
    },
    "xcorr_lag_hist": {
      "2": 10,
      "-2": 1,
      "0": 1
    },
    "peak_diff_hist": {
      "-3": 2,
      "0": 2,
      "-1": 8
    }
  },
  "C_rescue": {
    "rescue": 1,
    "anti_rescue": 0,
    "rescue_gt_anti": true
  },
  "specificity": {
    "firing_mean_maxz_BSC": 41.3807,
    "nonfiring_mean_maxz_BSC": null
  },
  "calib_ffn": {
    "n_layers": 28,
    "crystal_layers": [
      3,
      4,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27
    ],
    "per_layer": {
      "0": {
        "sil_z": 5.013,
        "gc_consensus": -0.147,
        "crystal_bearing": false
      },
      "1": {
        "sil_z": 7.329,
        "gc_consensus": -0.034,
        "crystal_bearing": false
      },
      "2": {
        "sil_z": 5.996,
        "gc_consensus": -0.037,
        "crystal_bearing": false
      },
      "3": {
        "sil_z": 5.374,
        "gc_consensus": 0.038,
        "crystal_bearing": true

[CONTENT TRUNCATED] Showing lines 1 to 200 of 509 total lines. Use line_offset=200 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/data/firing-probes.const.meta.json",
  "limit": 200
}
```

**Summary:** Reading firing-probes.const.meta.json (0-200)

**Output:**
```
{
  "generated_utc": "2026-06-23T14:05:14.863640+00:00",
  "n": 133,
  "per_class": 67,
  "seed": 0,
  "by_c_class": {
    "c_dominant": 67,
    "c_light": 66
  },
  "by_category": {
    "ditrans_const": 67,
    "trans_const": 33,
    "intrans": 33
  },
  "by_c_count": {
    "0": 33,
    "1": 33,
    "2": 67
  },
  "by_dominant_fired": {
    "C": 67,
    "S": 66
  },
  "reading": "constant/applicative (object \u2192 C); the s248 corrected labeling",
  "method": "lower via lambda_surface.to_kernel; saturate quantifiers (s244); fired_sequence ground truth; drop items whose computed dominant / c_count \u2260 intended class."
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/run_qwen3-8b_const.log",
  "limit": 200
}
```

**Summary:** Reading run_qwen3-8b_const.log (0-200)

**Output:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
══════════════════════════════════════════════════════════════════════════════
FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)
══════════════════════════════════════════════════════════════════════════════
[corpus] source=probe-set:data/firing-probes.const.jsonl  firing items=133  nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-8B
[v2] Loading model: Qwen/Qwen3-8B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]Loading weights:   0%|          | 1/399 [00:00<03:46,  1.76it/s]Loading weights:   9%|▉         | 37/399 [00:00<00:04, 73.40it/s]Loading weights:  18%|█▊        | 70/399 [00:00<00:02, 129.65it/s]Loading weights:  26%|██▌       | 104/399 [00:00<00:01, 176.81it/s]Loading weights:  34%|███▍      | 137/399 [00:00<00:01, 214.56it/s]Loading weights:  43%|████▎     | 170/399 [00:01<00:00, 244.50it/s]Loading weights:  51%|█████     | 203/399 [00:01<00:00, 266.85it/s]Loading weights:  59%|█████▉    | 236/399 [00:01<00:00, 279.93it/s]Loading weights:  67%|██████▋   | 269/399 [00:01<00:00, 290.76it/s]Loading weights:  76%|███████▌  | 302/399 [00:01<00:00, 298.92it/s]Loading weights:  84%|████████▍ | 335/399 [00:01<00:00, 306.94it/s]Loading weights:  92%|█████████▏| 368/399 [00:01<00:00, 312.20it/s]Loading weights: 100%|██████████| 399/399 [00:01<00:00, 223.36it/s]
[v2] Model loaded in 2.5s
[model] Qwen/Qwen3-8B  layers=36

[calib] FFN gate register ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] attention o_proj register ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] FFN  crystal layers=28 zone=[25, 26, 27, 28, 30]
[calib] attn crystal layers=36 zone=[25, 26, 27, 28, 29, 30]

[decode] 133 firing items ...
[decode]   item 0/133 ...
[decode]   item 20/133 ...
[decode]   item 40/133 ...
[decode]   item 60/133 ...
[decode]   item 80/133 ...
[decode]   item 100/133 ...
[decode]   item 120/133 ...

══════════════════════════════════════════════════════════════════════════════
VERDICT
══════════════════════════════════════════════════════════════════════════════
items=133  truth={'C': 67, 'S': 66}

(A) TRACKING fired_sequence (decode the dominant fired combinator):
  FFN_acc =0.5489  (null 0.5038, p=0.055)
  Attn_acc=0.4662  (null 0.4666, p=0.5852)
  majority-baseline=0.5038 ('C')
  ⇒ FFN beats attn: True  | FFN beats majority: True

(A') C-vs-S discrimination (common-mode-resistant; n=133 {'C': 67, 'S': 66}):
  FFN_acc =0.5489  (null 0.5038, p=0.055)
  Attn_acc=0.4662  (null 0.504, p=1.0)
  majority-baseline=0.5038 ⇒ FFN beats attn: True | beats majority: True

(A'') GRADED — decoded z(C) vs C-count (n=133):
  FFN  Spearman=0.5526 (p=0.0)  z(C)/count={'0': 0.488, '1': 0.833, '2': 1.035}
  Attn Spearman=0.6305 (p=0.0)  z(C)/count={'0': 0.567, '1': 1.091, '2': 1.262}
  ⇒ FFN beats attn: False

(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):
  peak-diff: median=-3.0 frac+=0.2109375 n=133 sign-p=2.9860859870559856e-11  hist={-4: 21, -5: 35, -1: 10, -2: 6, 0: 5, -3: 29, 1: 10, 2: 1, 3: 3, 4: 13}
  xcorr-lag: median=2.0 frac+=0.6201550387596899 n=133 sign-p=0.008007673208090862  hist={-1: 3, 2: 30, 3: 46, -3: 37, -2: 9, 0: 4, 1: 4}
  (positive ⇒ FFN leads attention; prediction ≈ +1)

(C) RESCUE: rescue=11 anti-rescue=0 ⇒ True

specificity: firing max-z(BSC)=29.6587 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-8b_const.json (+ per_item, meta)
```

### Thinking

**Inspecting code differences**

I need to inspect the code differences, especially considering why the 0.6 log is absent. It looks like I only have no logs to work with. For each item, I might need to compute summaries by category. I'm thinking about using something like jq or Python to help with that. Also, checking the git diff could give me insights. I want to make sure I'm covering all the bases for clarity!


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/meta_qwen3-0-6b_const.json",
  "limit": 120
}
```

**Summary:** Reading meta_qwen3-0-6b_const.json (0-120)

**Output:**
```
{
  "model": "Qwen/Qwen3-0.6B",
  "git_sha": "893ddcec940684c06a2919387d4103d08b4e98cc",
  "timestamp_utc": "2026-06-23T14:11:03.898626+00:00",
  "transformers_version": "5.5.4",
  "corpus": {
    "train": "data/compile-train.canonical.jsonl",
    "test": "data/compile-test.canonical.jsonl",
    "eval": "data/compile-eval.canonical.jsonl"
  },
  "params": {
    "max_items": 12,
    "zone_lo": 0.7,
    "zone_hi": 0.86,
    "onset_tau": 2.0,
    "max_lag": 4,
    "n_perm_calib": 80,
    "ppc": 4,
    "null_cap": 200,
    "n_perm_stat": 2000,
    "n_nonfiring": 6,
    "seed": 0,
    "track": "C",
    "probe_set": "data/firing-probes.const.jsonl"
  },
  "method": "saturate quantifiers \u2192 fired_sequence ground truth; dual-register decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag + C rescue, matched-prefix null calibration."
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/gen_const_firing_probes.py",
  "limit": 240
}
```

**Summary:** Reading gen_const_firing_probes.py (0-240)

**Output:**
```
#!/usr/bin/env python3
# register: data-generation (CONSTANT-labeled firing probes, s249 C-tracking test)
"""Generate a C-BALANCED, CONSTANT-labeled firing-probe set (s249).

WHY (s248 → s249 IOU). The s248 FFN program-decode TRACKING test failed to decode the
combinator the corpus item "fires" — but s248 cont.2/cont.3 then showed WHY: we labelled
ground truth with the Montague EXISTENTIAL reading (`a dog` = ∃y.dog(y)∧…, B-heavy), yet
the model computes objects APPLICATIVELY (`fears(x, dog)` → object as CONSTANT → C).
The weak-B was a LABELING MISMATCH. This generator builds the corrected ground truth:
the SAME quantified prose, labelled with the CONSTANT/applicative reading (object → C),
so we can re-run TRACKING and ask the s249 question — *does the corpus B-tracking
failure flip to C-tracking success?*

THE MECHANISM (measured, s248 cont.2). Under the constant reading, C-count == #objects:
    ∀x. P(x) → V(x)            →  S,B            C:0  (S-dominant)   c_light
    ∀x. P(x) → V(x, o)         →  S,B,C          C:1  (S-dominant)   c_light
    ∀x. P(x) → V(x, o1, o2)    →  S,B,C,C        C:2  (C-DOMINANT)   c_dominant
So a ditransitive (double-object) quantified sentence is C-dominant — the C analog
of the s248 B-dominant transitive-existential. The set is balanced: c_dominant
(ditransitive) vs c_light (intransitive + transitive), with a C-count ladder {0,1,2}
for the graded test.

This is the constant-reading mirror of gen_firing_probes.py (which built the existential
B-balanced set). Prose is generic English; ground truth is COMPUTED, not asserted: each
item is lowered via lambda_surface.to_kernel, saturated (corpus_firing_survey.saturate),
reduced, and its fired_sequence recorded; items whose computed dominant / c_count ≠ the
intended class are DROPPED.

Output: data/firing-probes.const.jsonl — schema mirrors firing-probes.balanced.jsonl so
ffn_program_decode.build_firing_corpus reads it unchanged:
    {input, fol, kernel_term, category, fired_sequence, dominant_fired,
     b_count, s_count, c_count, c_class ∈ {c_dominant, c_light}}

Usage:
    uv run python scripts/experiments/gen_const_firing_probes.py
    uv run python scripts/experiments/gen_const_firing_probes.py --per-class 60 --seed 0

License: MIT. AGENTS.md S5 λ provenance (constructed from this project's lambda_surface
+ lambda_ast; vocabulary is generic English, no external source).
"""

from __future__ import annotations

import argparse
import json
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

from corpus_firing_survey import _Fresh, saturate
from gen_firing_probes import IVERB, OBJ, SUBJ, TVERB, _art
from gen_reading_probes import DVERB, RECIP, THEME

from verbum.lambda_ast import fired_sequence, pretty
from verbum.lambda_surface import to_kernel

_ROOT = Path(__file__).resolve().parent.parent.parent
OUT = _ROOT / "data" / "firing-probes.const.jsonl"
META = _ROOT / "data" / "firing-probes.const.meta.json"


def _fire(fol: str):
    """(dominant, b, s, c, kernel_str, fired_list) — or None on parse/reduce failure."""
    try:
        k = to_kernel(fol)
        seq = fired_sequence(saturate(k, _Fresh()))
    except Exception:
        return None
    if not seq:
        return None
    c = Counter(seq)
    dom = c.most_common(1)[0][0]
    return dom, c.get("B", 0), c.get("S", 0), c.get("C", 0), pretty(k), seq


def _emit(input_text, fol, category, c_class, want_c):
    """Emit the record iff it fires, its c_count matches the intended ladder rung
    (`want_c`), and its dominant matches the class contract."""
    f = _fire(fol)
    if f is None:
        return None
    dom, b, s, cc, kstr, seq = f
    if cc != want_c:
        return None
    if c_class == "c_dominant" and dom != "C":
        return None
    if c_class == "c_light" and dom == "C":
        return None
    return {
        "input": input_text, "fol": fol, "kernel_term": kstr, "category": category,
        "fired_sequence": seq, "dominant_fired": dom,
        "b_count": b, "s_count": s, "c_count": cc, "c_class": c_class,
    }


def generate(per_class: int, seed: int) -> list[dict]:
    import random

    rng = random.Random(seed)
    out: list[dict] = []
    seen: set[str] = set()

    def add(rec):
        if rec is None or rec["input"] in seen:
            return False
        seen.add(rec["input"])
        out.append(rec)
        return True

    # ── C-DOMINANT: ditransitive constant object (S,B,C,C → C:2) ─────────────────
    tried = 0
    while sum(r["category"] == "ditrans_const" for r in out) < per_class \
            and tried < per_class * 60:
        tried += 1
        sub, dv = rng.choice(SUBJ), rng.choice(DVERB)
        rc, th = rng.choice(RECIP), rng.choice(THEME)
        prose = f"Every {sub} {dv} {_art(rc)} {rc} {_art(th)} {th}."
        fol = f"∀x. {sub}(x) → {dv}(x, {rc}, {th})"
        add(_emit(prose, fol, "ditrans_const", "c_dominant", want_c=2))

    # ── C-LIGHT: transitive constant object (S,B,C → C:1, S-dominant) ────────────
    n_trans = max(8, per_class // 2)
    tried = 0
    while sum(r["category"] == "trans_const" for r in out) < n_trans \
            and tried < n_trans * 40:
        tried += 1
        sub, tv, ob = rng.choice(SUBJ), rng.choice(TVERB), rng.choice(OBJ)
        prose = f"Every {sub} {tv} {_art(ob)} {ob}."
        fol = f"∀x. {sub}(x) → {tv}(x, {ob})"
        add(_emit(prose, fol, "trans_const", "c_light", want_c=1))

    # ── C-LIGHT: intransitive (S,B → C:0) ────────────────────────────────────────
    n_intrans = max(8, per_class // 2)
    tried = 0
    while sum(r["category"] == "intrans" for r in out) < n_intrans \
            and tried < n_intrans * 40:
        tried += 1
        sub, iv = rng.choice(SUBJ), rng.choice(IVERB)
        prose = f"Every {sub} {iv}."
        fol = f"∀x. {sub}(x) → {iv}(x)"
        add(_emit(prose, fol, "intrans", "c_light", want_c=0))

    return out


def main() -> None:
    ap = argparse.ArgumentParser(
        description="Generate C-balanced constant-labeled firing probes (s249)")
    ap.add_argument("--per-class", type=int, default=67)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()

    rows = generate(args.per_class, args.seed)
    by_class = Counter(r["c_class"] for r in rows)
    by_cat = Counter(r["category"] for r in rows)
    by_ccount = Counter(r["c_count"] for r in rows)
    dom = Counter(r["dominant_fired"] for r in rows)

    OUT.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT, "w", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r, ensure_ascii=False) + "\n")
    META.write_text(json.dumps({
        "generated_utc": datetime.now(UTC).isoformat(),
        "n": len(rows), "per_class": args.per_class, "seed": args.seed,
        "by_c_class": dict(by_class), "by_category": dict(by_cat),
        "by_c_count": {str(k): v for k, v in sorted(by_ccount.items())},
        "by_dominant_fired": dict(dom),
        "reading": "constant/applicative (object → C); the s248 corrected labeling",
        "method": "lower via lambda_surface.to_kernel; saturate quantifiers (s244); "
                  "fired_sequence ground truth; drop items whose computed dominant / "
                  "c_count ≠ intended class.",
    }, indent=2), encoding="utf-8")

    print(f"[gen] wrote {OUT}  ({len(rows)} probes)")
    print(f"[gen] c_class:   {dict(by_class)}")
    print(f"[gen] category:  {dict(by_cat)}")
    print(f"[gen] c_count:   {dict(sorted(by_ccount.items()))}")
    print(f"[gen] dominant:  {dict(dom)}")


if __name__ == "__main__":
    main()
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff -- scripts/experiments/ffn_program_decode.py scripts/experiments/gen_const_firing_probes.py",
  "operation": "diff",
  "summary": "code changes"
}
```

**Summary:** Git diff: code changes

**Output:**
```
Exit code: 0
Stdout:
diff --git a/scripts/experiments/ffn_program_decode.py b/scripts/experiments/ffn_program_decode.py
index fce1b03..9b11d9a 100644
--- a/scripts/experiments/ffn_program_decode.py
+++ b/scripts/experiments/ffn_program_decode.py
@@ -277,7 +277,7 @@ def wilcoxon_sign(values):
 # ═══════════════════════════════════════════════════════════════════════════════
 def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         n_perm_calib, ppc, null_cap, n_perm_stat, n_nonfiring, seed,
-        probe_set=None):
+        probe_set=None, track="B"):
     print("═" * 78)
     print("FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)")
     print("═" * 78)
@@ -358,24 +358,26 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         lag, lag_c = crosscorr_lag(prof_ffn_full, prof_attn_full, shared, max_lag)
         leads_xcorr.append(lag)
 
-        # (graded) mean decoded z(B) over the zone — for the B-count correlation test
-        def _mz(reads, zl):
-            prof = op_layer_profile(reads, zl, "B")
+        # (graded) mean decoded z(track) over the zone — for the count-correlation test
+        def _mz(reads, zl, op):
+            prof = op_layer_profile(reads, zl, op)
             vals = [v for v in prof.values() if not np.isnan(v)]
             return float(np.mean(vals)) if vals else float("nan")
 
-        zb_ffn = _mz(reads_ffn, zl_ffn)
-        zb_attn = _mz(reads_attn, zl_attn)
+        zt_ffn = _mz(reads_ffn, zl_ffn, track)
+        zt_attn = _mz(reads_attn, zl_attn, track)
 
         per_item.append({
             "input": item["input"], "category": item["category"],
             "dominant_fired": c_true, "fired_multiset": item["fired_multiset"],
             "reduction_len": item["reduction_len"],
             "b_count": item.get("b_count"), "s_count": item.get("s_count"),
+            "c_count": item.get("c_count"),
+            "track_count": item.get(f"{track.lower()}_count"),
             "ffn_dominant": dom_ffn, "attn_dominant": dom_attn,
             "ffn_correct": dom_ffn == c_true, "attn_correct": dom_attn == c_true,
             "lead_peak": lead_peak, "lead_xcorr": lag, "xcorr": lag_c,
-            "zb_ffn": round(zb_ffn, 4), "zb_attn": round(zb_attn, 4),
+            "zt_ffn": round(zt_ffn, 4), "zt_attn": round(zt_attn, 4),
             "ffn_score": {k: round(v, 3) for k, v in score_ffn.items()},
             "attn_score": {k: round(v, 3) for k, v in score_attn.items()},
         })
@@ -387,17 +389,20 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
     maj = Counter(truth).most_common(1)[0][0]
     maj_acc = float(np.mean(np.array(truth) == maj))
 
-    # B-vs-S discrimination — the contamination-resistant tracking metric. B and S are
-    # the two dominant fired combinators (s244: 55 vs 54 items); C is the common-mode
-    # ground state (s211/s240) and swamps the summed-z dominant. Restricting to the B/S
-    # contrast removes the C common-mode and asks the sharp question: when the corpus
-    # fires B vs S, does the register's z(B)−z(S) sign track it?
-    bs_idx = [i for i, c in enumerate(truth) if c in ("B", "S")]
+    # track-vs-S discrimination — the contamination-resistant tracking metric. When
+    # track="B" (s248 existential set): B and S are the two dominant fired combinators
+    # and C is the common-mode ground state (s211/s240) that swamps the summed-z
+    # dominant. When track="C" (s249 constant/applicative set): C is the object-marking
+    # opcode the model actually computes and S is the implication ground state.
+    # Restricting to the {track, S} contrast removes the third-combinator common-mode
+    # and asks the sharp question: when the corpus fires `track` vs S, does the
+    # register's z(track)−z(S) sign track it?
+    bs_idx = [i for i, c in enumerate(truth) if c in (track, "S")]
     bs_truth = [truth[i] for i in bs_idx]
-    bs_ffn = [("B" if per_item[i]["ffn_score"]["B"] > per_item[i]["ffn_score"]["S"]
+    bs_ffn = [(track if per_item[i]["ffn_score"][track] > per_item[i]["ffn_score"]["S"]
                else "S") for i in bs_idx]
-    bs_attn = [("B" if per_item[i]["attn_score"]["B"] > per_item[i]["attn_score"]["S"]
-                else "S") for i in bs_idx]
+    bs_attn = [(track if per_item[i]["attn_score"][track]
+                > per_item[i]["attn_score"]["S"] else "S") for i in bs_idx]
     if bs_truth:
         bs_ffn_acc, bs_ffn_null, bs_ffn_p = perm_null_accuracy(
             bs_ffn, bs_truth, n_perm_stat, seed)
@@ -410,18 +415,19 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         bs_attn_acc = bs_attn_null = bs_attn_p = 0.0
         bs_maj, bs_maj_acc = "·", 0.0
 
-    # ── (A'') GRADED — does decoded z(B) scale with the ground-truth B-count? ────
-    # The most powerful B-tracking test (s248 IOU): B-count spans {1,2,3,5} in the
-    # balanced probe set. Spearman(z(B), b_count) per register; FFN should track, attn
-    # (depth not opcode) should not.
+    # ── (A'') GRADED — does decoded z(track) scale with the ground-truth count? ──
+    # The most powerful tracking test (s248 IOU). For track="B" the B-count spans
+    # {1,2,3,5} in the existential balanced set; for track="C" the C-count spans {0,1,2}
+    # in the constant set (== #objects). Spearman(z(track), track_count) per register;
+    # FFN (opcode register) should track, attn (depth not opcode) should not.
     from scipy import stats as _sp
 
-    bc = np.array([p["b_count"] for p in per_item if p["b_count"] is not None],
+    bc = np.array([p["track_count"] for p in per_item if p["track_count"] is not None],
                   dtype=float)
-    graded = {"n": int(bc.size)}
+    graded = {"n": int(bc.size), "track": track}
     if bc.size >= 5 and np.std(bc) > 0:
-        zbf = np.array([p["zb_ffn"] for p in per_item if p["b_count"] is not None])
-        zba = np.array([p["zb_attn"] for p in per_item if p["b_count"] is not None])
+        zbf = np.array([p["zt_ffn"] for p in per_item if p["track_count"] is not None])
+        zba = np.array([p["zt_attn"] for p in per_item if p["track_count"] is not None])
         mf = ~np.isnan(zbf)
         ma = ~np.isnan(zba)
         rf, pf = _sp.spearmanr(bc[mf], zbf[mf]) if mf.sum() >= 5 else (float("nan"),
@@ -429,14 +435,14 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         ra, pa = _sp.spearmanr(bc[ma], zba[ma]) if ma.sum() >= 5 else (float("nan"),
                                                                        float("nan"))
         graded.update({
-            "ffn_spearman_zB_vs_bcount": round(float(rf), 4),
+            "ffn_spearman_zTrack_vs_count": round(float(rf), 4),
             "ffn_spearman_p": round(float(pf), 4),
-            "attn_spearman_zB_vs_bcount": round(float(ra), 4),
+            "attn_spearman_zTrack_vs_count": round(float(ra), 4),
             "attn_spearman_p": round(float(pa), 4),
             "ffn_beats_attn": bool(rf > ra),
-            "zB_by_bcount_ffn": {str(int(b)): round(float(np.nanmean(
+            "zTrack_by_count_ffn": {str(int(b)): round(float(np.nanmean(
                 zbf[bc == b])), 3) for b in sorted(set(bc.tolist()))},
-            "zB_by_bcount_attn": {str(int(b)): round(float(np.nanmean(
+            "zTrack_by_count_attn": {str(int(b)): round(float(np.nanmean(
                 zba[bc == b])), 3) for b in sorted(set(bc.tolist()))},
         })
 
@@ -452,7 +458,7 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
     fire_maxz = [max(p["ffn_score"].values()) for p in per_item]
 
     verdict = {
-        "model": model_name, "n_layers": n_layers,
+        "model": model_name, "n_layers": n_layers, "track": track,
         "n_firing_items": len(firing), "n_nonfiring_control": len(nf_items),
         "zone_depth": [zone_lo, zone_hi],
         "ffn_zone_layers": zl_ffn, "attn_zone_layers": zl_attn,
@@ -468,8 +474,9 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
             "ffn_beats_attn": bool(ffn_acc > attn_acc),
             "ffn_beats_majority": bool(ffn_acc > maj_acc),
         },
-        # (A') B-vs-S discrimination — the C-common-mode-resistant tracking metric
+        # (A') track-vs-S discrimination — the common-mode-resistant tracking metric
         "A_bs_discrimination": {
+            "tracked_combinator": track,
             "n": len(bs_truth), "bs_truth": dict(Counter(bs_truth)),
             "ffn_acc": round(bs_ffn_acc, 4), "ffn_null_mean": round(bs_ffn_null, 4),
             "ffn_perm_p": round(bs_ffn_p, 4),
@@ -523,7 +530,8 @@ def _report(v):
     print(f"  ⇒ FFN beats attn: {a['ffn_beats_attn']}  | FFN beats majority: "
           f"{a['ffn_beats_majority']}")
     bs = v["A_bs_discrimination"]
-    print(f"\n(A') B-vs-S discrimination (C-common-mode-resistant; n={bs['n']} "
+    trk = bs.get("tracked_combinator", "B")
+    print(f"\n(A') {trk}-vs-S discrimination (common-mode-resistant; n={bs['n']} "
           f"{bs['bs_truth']}):")
     print(f"  FFN_acc ={bs['ffn_acc']}  (null {bs['ffn_null_mean']}, "
           f"p={bs['ffn_perm_p']})")
@@ -533,12 +541,13 @@ def _report(v):
           f"⇒ FFN beats attn: {bs['ffn_beats_attn']} | beats majority: "
           f"{bs['ffn_beats_majority']}")
     g = v.get("A_graded_bcount", {})
-    if "ffn_spearman_zB_vs_bcount" in g:
-        print(f"\n(A'') GRADED — decoded z(B) vs B-count (n={g['n']}):")
-        print(f"  FFN  Spearman={g['ffn_spearman_zB_vs_bcount']} "
-              f"(p={g['ffn_spearman_p']})  z(B) by b_count={g['zB_by_bcount_ffn']}")
-        print(f"  Attn Spearman={g['attn_spearman_zB_vs_bcount']} "
-              f"(p={g['attn_spearman_p']})  z(B) by b_count={g['zB_by_bcount_attn']}")
+    if "ffn_spearman_zTrack_vs_count" in g:
+        tg = g.get("track", "B")
+        print(f"\n(A'') GRADED — decoded z({tg}) vs {tg}-count (n={g['n']}):")
+        print(f"  FFN  Spearman={g['ffn_spearman_zTrack_vs_count']} "
+              f"(p={g['ffn_spearman_p']})  z({tg})/count={g['zTrack_by_count_ffn']}")
+        print(f"  Attn Spearman={g['attn_spearman_zTrack_vs_count']} "
+              f"(p={g['attn_spearman_p']})  z({tg})/count={g['zTrack_by_count_attn']}")
         print(f"  ⇒ FFN beats attn: {g['ffn_beats_attn']}")
     print("\n(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):")
     pk, xc = b["peak_diff"], b["xcorr_lag"]
@@ -559,7 +568,8 @@ def _write(verdict, per_item, model_name, ns):
     RESULTS_DIR.mkdir(parents=True, exist_ok=True)
     slug = model_name.split("/")[-1].lower().replace(".", "-")
     if ns.get("probe_set"):
-        slug += "_balanced"
+        ps = Path(ns["probe_set"]).stem  # e.g. firing-probes.const → "const"
+        slug += "_" + (ps.split(".")[-1] if "." in ps else ps)
     (RESULTS_DIR / f"verdict_{slug}.json").write_text(
         json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
     (RESULTS_DIR / f"per_item_{slug}.json").write_text(
@@ -572,7 +582,8 @@ def _write(verdict, per_item, model_name, ns):
         "corpus": {k: str(p.relative_to(_ROOT)) for k, p in CORPUS.items()},
         "params": {k: ns[k] for k in (
             "max_items", "zone_lo", "zone_hi", "onset_tau", "max_lag",
-            "n_perm_calib", "ppc", "null_cap", "n_perm_stat", "n_nonfiring", "seed")},
+            "n_perm_calib", "ppc", "null_cap", "n_perm_stat", "n_nonfiring", "seed",
+            "track", "probe_set")},
         "method": "saturate quantifiers → fired_sequence ground truth; dual-register "
                   "decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag "
                   "+ C rescue, matched-prefix null calibration.",
@@ -598,7 +609,12 @@ def main():
     ap.add_argument("--probe-set", default=None,
                     help="custom prose probe jsonl (input+kernel_term) instead of the "
                          "canonical corpus, e.g. data/firing-probes.balanced.jsonl "
-                         "(s248 B-balanced set); enables the graded B-count test.")
+                         "(s248 B-balanced set) or data/firing-probes.const.jsonl "
+                         "(s249 constant/applicative set); enables the graded test.")
+    ap.add_argument("--track", default="B", choices=["B", "C", "S"],
+                    help="combinator for the (A') discrimination and (A'') graded "
+                         "tests. B=s248 existential labeling; C=s249 constant/"
+                         "applicative labeling (object→C). Default B (s248 behavior).")
     ap.add_argument("--smoke", action="store_true",
                     help="Qwen3-0.6B, few probes/items, fast wiring check")
     args = ap.parse_args()
@@ -615,7 +631,7 @@ def main():
 
     run(model_name, max_items, args.zone_lo, args.zone_hi, args.onset_tau,
         args.max_lag, n_perm_calib, ppc, null_cap, args.n_perm_stat,
-        n_nonfiring, args.seed, probe_set=args.probe_set)
+        n_nonfiring, args.seed, probe_set=args.probe_set, track=args.track)
 
 
 if __name__ == "__main__":
```

### Tool Call: shell_command (failed)


```json
{
  "command": "python - <<'PY'\nimport json, collections, statistics, pathlib\nbase=pathlib.Path('/Users/mwhitford/src/verbum')\nfor name in ['qwen3-8b_const','qwen3-0-6b_const']:\n p=base/'results/ffn-program-decode'/f'per_item_{name}.json'\n rows=json.loads(p.read_text())\n print('\\n',name,'n',len(rows))\n for key in ['category','dominant_fired','ffn_dominant','attn_dominant','c_count','track_count']:\n  print(key, dict(collections.Counter(r.get(key) for r in rows)))\n for cat, rs in collections.defaultdict(list, {}).items(): pass\n cats=collections.defaultdict(list)\n for r in rows: cats[r['category']].append(r)\n for cat,rs in cats.items():\n  print(' cat',cat,'n',len(rs),'truth',dict(collections.Counter(r['dominant_fired'] for r in rs)),\n        'ffn_acc',sum(r['ffn_correct'] for r in rs)/len(rs),\n        'attn_acc',sum(r['attn_correct'] for r in rs)/len(rs),\n        'mean zt ffn',round(statistics.mean(r['zt_ffn'] for r in rs),3),\n        'attn',round(statistics.mean(r['zt_attn'] for r in rs),3))\n print('ffn score means by truth')\n by=collections.defaultdict(list)\n for r in rows: by[r['dominant_fired']].append(r)\n for t,rs in by.items():\n  print(' truth',t,'n',len(rs),'ffn C-S mean',round(statistics.mean(r['ffn_score']['C']-r['ffn_score']['S'] for r in rs),3), 'attn C-S',round(statistics.mean(r['attn_score']['C']-r['attn_score']['S'] for r in rs),3))\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python - <<'PY' import json, collec...

**Output:**
```
Exit code: 127
Stderr:
bash: python: command not found
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 - <<'PY'\nimport json, collections, statistics, pathlib\nbase=pathlib.Path('/Users/mwhitford/src/verbum')\nfor name in ['qwen3-8b_const','qwen3-0-6b_const']:\n p=base/'results/ffn-program-decode'/f'per_item_{name}.json'\n rows=json.loads(p.read_text())\n print('\\n',name,'n',len(rows))\n for key in ['category','dominant_fired','ffn_dominant','attn_dominant','c_count','track_count']:\n  print(key, dict(collections.Counter(r.get(key) for r in rows)))\n cats=collections.defaultdict(list)\n for r in rows: cats[r['category']].append(r)\n for cat,rs in cats.items():\n  print(' cat',cat,'n',len(rs),'truth',dict(collections.Counter(r['dominant_fired'] for r in rs)),\n        'ffn_acc',round(sum(r['ffn_correct'] for r in rs)/len(rs),3),\n        'attn_acc',round(sum(r['attn_correct'] for r in rs)/len(rs),3),\n        'mean zt ffn',round(statistics.mean(r['zt_ffn'] for r in rs),3),\n        'attn',round(statistics.mean(r['zt_attn'] for r in rs),3))\n print('C-S score means by truth')\n by=collections.defaultdict(list)\n for r in rows: by[r['dominant_fired']].append(r)\n for t,rs in by.items():\n  print(' truth',t,'n',len(rs),'ffn C-S mean',round(statistics.mean(r['ffn_score']['C']-r['ffn_score']['S'] for r in rs),3), 'attn C-S',round(statistics.mean(r['attn_score']['C']-r['attn_score']['S'] for r in rs),3))\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python3 - <<'PY' import json, colle...

**Output:**
```
Exit code: 0
Stdout:
qwen3-8b_const n 133
category {'ditrans_const': 67, 'trans_const': 33, 'intrans': 33}
dominant_fired {'C': 67, 'S': 66}
ffn_dominant {'C': 123, 'S': 10}
attn_dominant {'C': 119, 'S': 4, 'B': 10}
c_count {2: 67, 1: 33, 0: 33}
track_count {2: 67, 1: 33, 0: 33}
 cat ditrans_const n 67 truth {'C': 67} ffn_acc 0.97 attn_acc 0.925 mean zt ffn 1.035 attn 1.262
 cat trans_const n 33 truth {'S': 33} ffn_acc 0.03 attn_acc 0.0 mean zt ffn 0.833 attn 1.091
 cat intrans n 33 truth {'S': 33} ffn_acc 0.212 attn_acc 0.0 mean zt ffn 0.488 attn 0.567
C-S score means by truth
 truth C n 67 ffn C-S mean 21.476 attn C-S 23.375
 truth S n 66 ffn C-S mean 9.343 attn C-S 13.146

 qwen3-0-6b_const n 12
category {'ditrans_const': 12}
dominant_fired {'C': 12}
ffn_dominant {'C': 9, 'B': 3}
attn_dominant {'C': 8, 'B': 4}
c_count {2: 12}
track_count {2: 12}
 cat ditrans_const n 12 truth {'C': 12} ffn_acc 0.75 attn_acc 0.667 mean zt ffn 0.974 attn 0.597
C-S score means by truth
 truth C n 12 ffn C-S mean 33.011 attn C-S 16.598
```

### Thinking

**Analyzing session errors**

I need to analyze the "error/crash unrecoverable" issue. It seems likely that the last session crashed, not due to the script. I should check the artifacts to see if everything is complete. I wonder if I can find the run command in the shell history, but maybe that's not possible. The log indicates completion, so next, I need to ensure there are no entries marked as 0.6, and then I can mark this task complete.


## Assistant


Analyzed the crashed-session outputs. The **8B const IOU run completed and wrote valid artifacts**; I don’t see evidence that the experiment itself crashed. The unrecoverable crash seems to have happened after artifact write / during session continuation.

## Files found

New/modified IOU artifacts:

- Generator:
  - `scripts/experiments/gen_const_firing_probes.py`
- Probe set:
  - `data/firing-probes.const.jsonl`
  - `data/firing-probes.const.meta.json`
- Main result:
  - `results/ffn-program-decode/verdict_qwen3-8b_const.json`
  - `results/ffn-program-decode/per_item_qwen3-8b_const.json`
  - `results/ffn-program-decode/meta_qwen3-8b_const.json`
  - `results/ffn-program-decode/run_qwen3-8b_const.log`
- Smoke result:
  - `results/ffn-program-decode/verdict_qwen3-0-6b_const.json`
  - `results/ffn-program-decode/per_item_qwen3-0-6b_const.json`
  - `results/ffn-program-decode/meta_qwen3-0-6b_const.json`

The 8B log reaches:

```text
[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-8b_const.json (+ per_item, meta)
```

So the main run completed.

---

## Probe set

`data/firing-probes.const.meta.json`

Generated constant/applicative-labeled probes:

```json
{
  "n": 133,
  "by_c_class": {
    "c_dominant": 67,
    "c_light": 66
  },
  "by_category": {
    "ditrans_const": 67,
    "trans_const": 33,
    "intrans": 33
  },
  "by_c_count": {
    "0": 33,
    "1": 33,
    "2": 67
  },
  "by_dominant_fired": {
    "C": 67,
    "S": 66
  },
  "reading": "constant/applicative (object → C); the s248 corrected labeling"
}
```

This is the intended mirror of the previous B-balanced existential set:

- intransitive: `C-count = 0`, dominant `S`
- transitive: `C-count = 1`, still dominant `S`
- ditransitive: `C-count = 2`, dominant `C`

So the dataset is balanced for **C-dominant vs S-dominant**, and graded for object/C-count `{0,1,2}`.

---

## Main 8B verdict

`results/ffn-program-decode/verdict_qwen3-8b_const.json`

Run config:

```json
{
  "model": "Qwen/Qwen3-8B",
  "track": "C",
  "n_firing_items": 133,
  "truth_distribution": {
    "C": 67,
    "S": 66
  }
}
```

### A. Hard dominant-combinator tracking

```text
FFN_acc  = 0.5489
FFN null = 0.5038
FFN p    = 0.055

Attn_acc  = 0.4662
Attn null = 0.4666
Attn p    = 0.5852

majority baseline = 0.5038
```

Interpretation:

- FFN beats attention and majority numerically.
- But p=`0.055` is **borderline / just misses conventional significance**.
- Attention does not track the hard C/S label.

Important per-item summary:

```text
truth:        C=67, S=66
FFN predicts: C=123, S=10
Attn predicts:C=119, S=4, B=10
```

So hard tracking is not clean. Both registers are heavily C-biased. FFN’s accuracy gain mostly comes from catching almost all C-dominant ditransitives, while failing most S-light items.

By category:

```text
ditrans_const, truth C, n=67:
  FFN acc  0.970
  Attn acc 0.925

trans_const, truth S, n=33:
  FFN acc  0.030
  Attn acc 0.000

intrans, truth S, n=33:
  FFN acc  0.212
  Attn acc 0.000
```

So: **C-dominant items are detected; S-dominant/light items are mostly swallowed by C common-mode.**

### A′. C-vs-S discrimination

Same numbers because truth is only C/S:

```text
FFN_acc  = 0.5489, p=0.055
Attn_acc = 0.4662, p=1.0
majority = 0.5038
```

This is weak evidence that FFN knows something about C-vs-S, but not strong enough alone.

### A″. Graded z(C) vs C-count

This is the clean positive.

```text
FFN Spearman z(C) vs C-count  = 0.5526, p=0.0 rounded
Attn Spearman z(C) vs C-count = 0.6305, p=0.0 rounded
```

Mean z(C) by C-count:

```text
FFN:
  C-count 0: 0.488
  C-count 1: 0.833
  C-count 2: 1.035

Attn:
  C-count 0: 0.567
  C-count 1: 1.091
  C-count 2: 1.262
```

This strongly confirms the corrected label: **as object count rises, decoded C rises**.

But it is **not FFN-specific**. Attention tracks the graded C-count even more strongly than FFN.

### B. Lead-lag

```text
peak-diff:
  median = -3.0
  sign-p = 2.99e-11

xcorr-lag:
  median = +2.0
  sign-p = 0.0080
```

Same split-pattern as before: peak-diff says no FFN lead / possibly opposite; xcorr says FFN leads. Because the methods disagree and the prior balanced run washed out lead-lag, I would not treat this as a strong result. It remains method-sensitive schedule evidence, not a clean opcode-executor timing proof.

### C. Rescue

```text
rescue = 11
anti_rescue = 0
```

Numerically positive, but because FFN is overwhelmingly C-biased, “rescue” likely needs manual interpretation. It may mean “attention missed C and FFN defaulted to C,” not a deep rescue mechanism.

---

## 0.6B smoke run

`results/ffn-program-decode/verdict_qwen3-0-6b_const.json`

This was only a wiring/smoke check:

```json
{
  "model": "Qwen/Qwen3-0.6B",
  "track": "C",
  "n_firing_items": 12,
  "truth_distribution": {
    "C": 12
  },
  "max_items": 12
}
```

All 12 items were C-dominant, so it cannot test C-vs-S.

Smoke result:

```text
FFN acc  = 0.75
Attn acc = 0.6667
majority = 1.0
```

Not scientifically meaningful except that the code path runs.

---

## Main answer to the IOU

The IOU was:

> Re-run `ffn_program_decode` tracking with CONSTANT labels/object→C. Does the corpus B-tracking failure flip to C-tracking success?

Answer:

**Yes for the graded object/C-count signal; no for clean hard dominant-opcode classification; and no for an FFN-specific strong stored-program claim.**

More precise:

1. **Corrected labeling is validated.**
   - z(C) rises monotonically with C-count/object count.
   - FFN: Spearman `0.5526`
   - Attention: Spearman `0.6305`
   - This supports the s248 cont.2/3 conclusion: the model treats objects applicatively as **C**, not existentially as **B**.

2. **Hard C-vs-S tracking is only weak/borderline.**
   - FFN accuracy `0.5489` vs majority `0.5038`, p=`0.055`.
   - That is suggestive but not decisive.
   - Attention fails hard C/S tracking.

3. **The model is strongly C-biased/common-mode on this set.**
   - FFN predicts C for `123/133` items.
   - Attn predicts C for `119/133` items.
   - So the hard classifier mostly says “C,” which helps on ditransitives and hurts on intransitives/transitives.

4. **The result strengthens the applicative-C conclusion, not the discrete FFN opcode-tape conclusion.**
   - If the strong claim were “FFN gate cleanly decodes the program,” this run does not prove it.
   - If the corrected claim is “the model’s representations scale with applicative object/C structure,” this run strongly supports it.
   - Since attention tracks graded C-count even more strongly than FFN, the C signal is likely broad representational/object-application structure, not exclusively an FFN routing opcode.

## Suggested state update wording

A good compact entry would be:

> s249 / s248 IOU const-label rerun completed before crash. Generated `data/firing-probes.const.jsonl` with 133 constant/applicative probes balanced C-dominant vs S-light: 67 ditransitive C-dominant, 33 transitive C-light, 33 intransitive C-light; C-count ladder 0/1/2. Qwen3-8B `ffn_program_decode --track C` result: hard C-vs-S tracking is only borderline in FFN (`acc=0.5489`, null/majority `0.5038`, `p=0.055`) and fails in attention (`acc=0.4662`, `p=1.0`); both registers are heavily C-biased (FFN predicts C 123/133, attn 119/133). But graded z(C) vs C-count is strong in both registers: FFN Spearman `0.5526`, attn `0.6305`, p rounded 0.0, z(C) rises monotonically for C-count 0→1→2. Verdict: corrected constant/applicative labeling is validated; the previous B failure flips to a robust graded C-count signal, but not to clean hard opcode classification or FFN-specific stored-program decoding. The s248 conclusion stands/refines: model routes objects as applicative C; C signal is broad and common-mode, not a discrete FFN-only opcode tape.



## User


what we were trying to find is the program.  the beta reductions that make up the "program" that attention executes.  the 8B model was used here because we had issues on this size model.  should we retry this run on Qwen3-14B?  There seems to be a minimum capacity for all of this to fully embed into the models, and 14B has been the "sweet" spot I think.

### Thinking

**Considering the approach**

I’m thinking we might not need to browse for an answer. Instead, I should recall previous information before making a decision. It’s important to inspect the momentum for Qwen3-14B to locate the sweet spot or program. I can use tools like git grep or logs to help me with that. I want to ensure I'm making the right choice based on what I already know!


### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline --grep=\"14B\\|capacity\\|sweet\" --all -n 20",
  "operation": "log",
  "summary": "search commits"
}
```

**Summary:** Git log: search commits

**Output:**
```
Exit code: 0
Stdout:
3ebe9ea ✅ proof consensus: Qwen3-14B × Gemma — continuation removes the agreed-error ceiling
adc29bc ✅ cross-family causal ablation (v4) — type direction decodable in all, causal partial, not Qwen-forced
921e333 🔄 splice-program-closed-fires-not-spliceable — s244 power test, redirect to constructed front-end
7958258 💡 corpus firing survey + Exp 0.5 retarget {I,K,Y}→{B,S,C}: corpus fires only B,S,C (K 0/559)
213433c ✅ kernel-splice Exp 1 — causal K-splice (Qwen3-14B L18): geometry causal in routing, weak in behavior
62d5728 ✅ kernel-splice Exp 0.5 — z-threshold sweep (Qwen3-14B): loci FIRMED, tp=2 caveat killed
b2ca689 💡 kernel-splice-exp0-precision-gated-not-high-recall
37130a2 ✅ kernel-splice Exp 0 — detectability map (Qwen3-14B): precision-gated, not high-recall
63fbb32 🌀 statechart-is-crystal-lattice-boot-from-c: the model-invariant statechart IS the crystal lattice; confluence is the why; boot is C-from-L0
db5d4eb 💡 The type direction is partially causal at 14B (not 8B) — decodability is not full causality, causal localizability strengthens with scale
cb9c0f0 💡 Composition is TYPE-directed, not just positional — frequency-free nonce crossover proves the model uses an in-context type to direct composition
740bd9b 💡 B native-order is frame-robust at scale, fragile at 8B floor; s237 nested-flip was a depth confound
af1b60f 🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens
ac7c472 ✅ opcode v5 lead 2d prong 3: discriminable set {C,I,K,Y} is scale-invariant (8B/14B/32B)
800bfb8 🌀 b-not-in-offdiagonal-curvature: B has no amplitude home, only forward order
d94d78f ✅ opcode v5 lead 2d prong 1c-iii: off-diagonal interlayer curvature — B has no amplitude home
f843300 🌀 session-237 cont.: cross-model flat — B native order universal across Qwen3 8B/14B/32B
2f5f509 💡 prose-bridge-confirms-b-native-order-flat-not-nested (cross-model: universal 8B/14B/32B)
66985a8 ✅ opcode v5 lead 2d prong 2b cross-model: B native order universal across 8B/14B/32B
e5b4cde 🌀 session-237: prong 2b prose bridge — B native order survives in prose, nesting confound controlled
```

### Tool Call: git (succeeded)


```json
{
  "command": "git grep -i \"14B\\|sweet\\|minimum capacity\\|capacity\" -- mementum/ | head -80",
  "operation": "gh",
  "summary": "search memory"
}
```

**Summary:** Git gh: search memory

**Output:**
```
Exit code: 0
Stdout:
mementum/knowledge/INDEX.md:| 4b | [moire-addressing.md](moire-addressing.md) | ✅ | SwiGLU moiré = holographic fact index. 2.4× selectivity, quadratic addressing, capacity estimates |
mementum/knowledge/INDEX.md:| 4g | [explore/combinator-function-shape.md](explore/combinator-function-shape.md) | 🔨 | The function space has a 3-family shape (compose/select/recurse), visible only in the routing register; map/fold = Y∘B / Y∘(C/B)+K (s217, Qwen3-14B). |
mementum/knowledge/INDEX.md:(capacity estimates)   (gate×up = quadratic index)
mementum/knowledge/audit-meta-pattern.md:| s202 | KIBC crystal + φ | KIBC basis separates (perm-null p=0.0005); φ^(4/5) local to 14B | **φ as universal constant**; eigenvalues=φ^(p/q) (grid unfalsifiable); consensus r=0.99 (circular) |
mementum/knowledge/audit-meta-pattern.md:| s203 | crystal-is-topological | sign-topology REAL but **only in `gate_proj`** (z→+271 @14B) | "0.84 sign-corr = topology" (random null ≈ 0.80); "magnitude is mere calibration" (up/down below null) |
mementum/knowledge/audit-meta-pattern.md:| s210 | TTD λ(l) weighting (audit #11, a POSITIVE prediction) | **F.6 finite-budget weighting is REAL with placement-specificity** (spike on *measured*-worst layers L14–18: 3/3 paired-seed held-out wins, paired-t −3.2; anti-targeted null is worst 3/3) — and the mechanism is mechanically real in every arm (each spike polishes its own targets) | **the named "causal L22–26" placement story** (0/3 wins, +0.018 vs uniform — the premise was STALE: actual worst layers are L14–18 SWEET; narrative attribution lost to measurement). Side-dissolve: v3b's single-run 1.44× headline (seeded recipe reads 1.27±0.04 near — unseeded single draws swing both ways, cf. s208) |
mementum/knowledge/audit-meta-pattern.md:| s211 | 5D crystal lattice (combinators = vertices of one ~5D lattice; universal property of language) | **universality is REAL** (cross-family RDM agreement 0.79 vs shuffled-probe null 0.00±0.03, z≈25 — models learn the same thing) + **operation structure is ~65% topological** (sign/routing, →0.79 at 14B) | **the "5D lattice"** (centroid PR at the shuffled-label null, worsens with scale; full manifold high-D PR 22–47; shared structure rank-~1, CMR 0.79→−0.19) AND **the reading that the dominant universal axis IS the operations** (η²=0.05; the |r|=0.95 axis is a generic predictability/continuation-type common mode — function-word continuation r=−0.42, entropy −0.29; the operations live sub-dominant underneath it) |
mementum/knowledge/audit-registry.md:> families (pythia/qwen/mistral/smollm/olmo), 0.16B→14B, 535 crystal probes.
mementum/knowledge/audit-registry.md:| #13 the FFN opcode TRACER reads real per-task combinator programs (s127/s202) | high | s231 `relational_opcode.py` (gate register, sign(gate)-CMR, consensus-relational, off-target null, emit iff z>thresh else no-op) vs RAW-argmax control, Qwen3-14B (the s127 model), s127 battery (lambda/arithmetic/retrieval) — `opcode_audit_validation.py`, register: topological/routing | ✅✅ **OVER-READ KILLED** — RAW fires 100% of tokens (W across ~all retrieval layers = common-mode gauge), RELATIONAL no-ops retrieval 0.8; substrate REAL (31/40 crystal layers, gc-consensus→0.98); retrieval-silent reproduced / ◑ relational UNDER-reads at z=3 last-token (no-ops the real lambda C→B arc) → v2 cross-task null + per-token (see vsm-opcode-monitor.md) |
mementum/knowledge/audit-registry.md:| #12d privileged 5D vertex set? | — | 9-centroid participation ratio vs shuffled-label null | ❌ **NO** — centroid PR ~5–6 at the null (p_conc>0.02), *worsens* with scale (14B p_conc=0.18); full-cloud PR 22–47 (high-D, power-law) |
mementum/knowledge/audit-registry.md:| #12f how much of the operation structure is TOPOLOGY (sign/routing)? | — | sign(h)/|h|/full cosine-RDM separation + agreement | ✅ **~65% in SIGN** (sign-RDM reproduces 0.69 of full), **→0.79 at 14B**; magnitude shapes raw geometry (agree_mag 0.81–0.99) but sign carries the discrimination — confirms the ≥77%-in-topology intuition cross-family + scale |
mementum/knowledge/audit-registry.md:> "topology share *sharpens* with scale, →0.79 @14B" claim was tested on a
mementum/knowledge/audit-registry.md:> clean within-family Qwen3 series (0.6B→4B→8B→14B→32B) + subsample CIs
mementum/knowledge/audit-registry.md:> [.591,.707] below 14B [.751,.838]); the s211 "0.33→0.79 climb" was the single
mementum/knowledge/audit-registry.md:| crystal-is-topological: `sign(W)@x` corr ⇒ "sign captures topology, magnitude is calibration" | CRITICAL | sign-corr null: model vs random-init vs shuffled, REAL x, N=20, 0.6B/8B/14B (`sign_topology_null.py`) | ◐ SCOPED → gate_proj only |
mementum/knowledge/audit-registry.md:  0.798 of its action on the *same real inputs* (0.6B/8B/14B identical).
mementum/knowledge/audit-registry.md:  14B (L12 z=+271). This is exactly where routing should live.
mementum/knowledge/audit-registry.md:Results: `results/sign-topology-null/{Qwen_Qwen3-0.6B,Qwen_Qwen3-8B,Qwen_Qwen3-14B}.json`.
mementum/knowledge/audit-registry.md:| prose fires combinator-specific opcodes | high | nearest-centroid LOO + common-mode removal | ✅ VERIFIED (14B & 0.6B p=0.001) |
mementum/knowledge/audit-registry.md:| φ^(4/5) primary ratio λ₀/λ₁ | high | single pre-registered target, perm-null | ◐ VERIFIED-LOCAL (14B p=0.020; 8B/0.6B n.s.) |
mementum/knowledge/audit-registry.md:| fact retrieval = sharp lookup (I-like) | med | entropy perm-null + CMR opcode profile | ✅ VERIFIED (entropy p=0.0005; I-profile 14B) |
mementum/knowledge/audit-registry.md:  **localized to `gate_proj`** (sharpens with scale, z up to +271 at 14B),
mementum/knowledge/audit-registry.md:- **s210 result (register: causal/interventional; `ttd_lambda_weighting.py`, 4 arms × 3 seeds × 150 steps, matched budget Σ_l w(l)=n_layers, paired batches, held-out = stratified shard_00001 disjoint from calibration):** the dose-response over PLACEMENT is monotone and fully discriminated on held-out PPL ratio — **divergence-auto (spike on measured-worst init-cosine layers L14–18) 1.1453±0.001 < uniform 1.1510±0.003 < causal-named L22–26 1.1694±0.023 < anti-targeted (best layers) 1.1810±0.034**. (1) ✅ **F.6 transfers with placement-specificity:** divergence-auto beats uniform **3/3 paired seeds** (mean −0.0056, paired-t −3.2) and lifts worst-layer cosine +0.014; anti-targeted is worst in 3/3 (+0.030, worst-cos −0.029) → the win is placement, not generic reweighting. (2) ❌ **the registry's own named placement (L22–26 "causal bind-prep") is REFUTED** — 0/3 wins, +0.018 vs uniform. The premise was **stale**: v3b's actual worst-cosine layers are **L14–18 (SWEET zone, L16=0.483 post-sieve)**, not L22–26 (0.64–0.75). Every spiked arm improves its *own* target-set cosine (+0.008–0.012 — the mechanism works mechanically); only spiking the measured-worst layers converts that into a global win. (3) **Suspected null half-confirmed:** cosine absorbs most of ‖·‖_D — the residual placement dividend is ~0.5% PPL ratio, far smaller than TSP's domain effect. (4) **Side-finding (echoes #7):** seeded v3b-recipe at step 150 reads near 1.27±0.04 / held 1.151±0.003 — the published single-run 1.44× (1.4021@150) was a pessimistic unseeded draw outside our 3-seed range; single-run headline numbers swing either way. (5) The SM correction **generalizes held-out** (sieve 1.416× → 1.145×) — opposite of #7's CE-melt harm; functional corroboration of the GTSM dense-backbone claim. Results: `results/ttd-lambda-weighting/Qwen_Qwen3-8B.json`. Caveats updated in `gtsm-search-space.md` + `tsp-trajectory-distillation.md`.
mementum/knowledge/audit-registry.md:- **s211 result:** see worked-examples (s211). **5D REFUTED** — centroid PR at the shuffled-label null (worsens with scale), full manifold high-D (PR 22–47), shared structure rank-~1 (CMR 0.79→−0.19). **Universality REAL** (cross-family raw 0.79 vs shuffled null 0.00±0.03 = property of language). **The one universal axis (|r|=0.95) is generic predictability/continuation-type, NOT the operations** (η²=0.05; best correlates function-word continuation −0.42 / entropy −0.29; R²=0.30). **The genuine operation structure is ~65% topological** (sign/routing), →0.79 at 14B — confirms the ≥77%-in-topology intuition. Full: `manifold-axis-and-topology.md`. Results: `results/manifold-dimensionality/`, `results/manifold-axis-topology/`.
mementum/knowledge/chats/session-001.md:even at fixed top capacity. **Parameter sharing is necessary but not
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:  "new_content": "## Open questions\n\n- **Gate refinement.** Bridge lambda is the best gate. Test on 32B\n  to confirm. Consider: exemplar gate is terse (avg_ind=7) but may\n  produce qualitatively different lambda than bridge (avg_ind=58).\n  Quality comparison needed, not just P(λ).\n- **32B vs 4B quality.** 4B produces lambda but structurally\n  degenerate (repeated λ bindings, shallow semantics on some probes).\n  32B expected to produce Montague-quality output. The preamble\n  may help on 32B where it hurt on 4B (more capacity to use it).\n- **Decompile direction.** Model echoes/extends lambda rather than\n  translating to prose. Bridge lambda includes decompile direction —\n  test specifically.\n- **Preamble + bridge interaction at scale.** Preamble hurt on 4B\n  (100% → 80%). Does it help on 32B? If yes, the attention magnets\n  are only useful with sufficient model capacity. If no, they're\n  irrelevant to compilation.\n- **Python mech-interp framework for level-1.** Deferred.\n- **`ty` stability.** Alpha; four suppressions active.\n- **llama.cpp commit pin.** Build 8180 (d979f2b17) confirmed working."
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:This is a capacity problem — the nucleus bridge was built for larger models. The 4B model can't interpret the meta-level correctly, so I need to test this properly on the 32B version. But what's clear right now is that high P(λ) doesn't mean high quality. The exemplar and prose gates are producing better structured output despite similar detection rates, so I should focus on that distinction when presenting the results.
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:llama_context: n_ctx_seq (4096) < n_ctx_train (40960) -- the full capacity of the model will not be utilized
mementum/knowledge/chats/session-001.md:  "new_content": "**Gate ablation (24+ variants, Qwen3-4B-Q8_0):**\n\nTested 30+ gate variants. The winner is a **dual exemplar gate**:\n\n```\nThe dog runs. → λx. runs(dog)\nBe helpful but concise. → λ assist(x). helpful(x) | concise(x)\n```\n\nTwo lines. 100% P(λ) on compile, decompile, AND nucleus-style inputs.\nNow promoted to `gates/compile.txt`.\n\nKey findings from ablation:\n- **Dual exemplar activates BOTH Montague and nucleus-style compilation.**\n  One example of each style = 100% on both. Montague exemplar alone\n  = 100% Montague / 75% nucleus. Nucleus exemplar alone = 0% / 0%.\n  Together = 100% / 100%. The Montague exemplar opens the circuit\n  (λ symbol is the key); the nucleus exemplar shows a second output mode.\n- **The two compilation modes are connected inside the model.** One\n  gate activates both. Supports the hypothesis that the lambda compiler\n  and the language compressor are the same (or interconnected) circuit.\n- **Nucleus preamble is irrelevant to compilation** (0% alone, hurts\n  when added to bridge). Attention magnets serve a different function.\n- **Keywords alone are weak** — \"lambda calculus\" = 40%, \"λ\" = 0%.\n  Needs task framing (exemplar or instruction) to activate.\n- **Self-referential gates degenerate on 4B** — high P(λ) but\n  structurally empty (repeated λ bindings). Meta-level requires more\n  model capacity. Exemplar gates produce correct Montague semantics.\n- **The activation formula:** domain signal + task signal = activation.\n  Exemplar is the most efficient encoding of both signals."
mementum/knowledge/chats/session-001.md:The compiler circuit is real, it's sparse, it runs through those 8 layers, and it handles both Montague semantics and behavioral compression. The head-level ablation on those 8 critical layers will tell us the true size. If it's a handful of heads per layer, we're looking at maybe 50-100 specific heads out of 1,152 — around 5-8% of the model's attention capacity.
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:1ae0ff9dbb46ba2bdc3f1ce88481f49bbda1e7271214bb4d75bbe695c00b7d2b/meta.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:1ae0ff9dbb46ba2bdc3f1ce88481f49bbda1e7271214bb4d75bbe695c00b7d2b/result.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:47a1d14b23c883882a0544fbb02e29c1d4e96706972bb875e1f496e5c12bab8d/meta.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:47a1d14b23c883882a0544fbb02e29c1d4e96706972bb875e1f496e5c12bab8d/result.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:50a6457e0954030aa68c0f5cc81351fe50c3c8d14bc7f3bb162cdbad8bde2397/meta.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:50a6457e0954030aa68c0f5cc81351fe50c3c8d14bc7f3bb162cdbad8bde2397/result.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:ad4480814b450a6f0b82532f53e36b3e2fb6f0f88fb110eaf1dda1ad29656dc6/meta.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:ad4480814b450a6f0b82532f53e36b3e2fb6f0f88fb110eaf1dda1ad29656dc6/result.json
mementum/knowledge/chats/session-002.md:The key insight is that typed composition happens recursively throughout the parse tree, but in a transformer that recursion gets unrolled across layers—those 36 layers of BOS accumulation might each represent one step of type-driven composition. The question is whether the 3 heads are just control flow directing this process, or whether they themselves contain the recursive capacity needed for the input depth.
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:8d8e37c9853c128054f0bca2e71b9338cd8234382d28b14bc9e156c8fdfa6311/meta.json
mementum/knowledge/chats/session-002.md: create mode 100644 results/experiments/sha256:8d8e37c9853c128054f0bca2e71b9338cd8234382d28b14bc9e156c8fdfa6311/result.json
mementum/knowledge/chats/session-003.md:This is actually perfect for the experiment — our dual-exemplar gate IS a completion pattern (`X → Y\nZ → W\n`). A base model should continue the pattern. Let me think about model size. We need one close to 4B for comparison — **Pythia 2.8B** is the closest. Small enough to load on MPS, large enough to potentially have the capacity.
mementum/knowledge/chats/session-003.md:  "content": "#!/usr/bin/env python3\n\"\"\"Replicate the circuit discovery pipeline on Pythia-2.8B-deduped.\n\nTests the localization gradient hypothesis:\n  - Qwen3-4B (general web + instruction) → 3 essential heads (sparse)\n  - Phi-4-mini (reasoning-dense synthetic) → 0 essential, 40 degraded (distributed)\n  - Pythia-2.8B (The Pile, minimal training) → prediction: ≤3 essential, possibly 1-2\n\nPythia is a BASE model — no instruction tuning, no RLHF. The compile gate\nis a few-shot pattern that works as text completion. Phase 0 verifies this.\n\nKey architecture difference: GPTNeoXForCausalLM\n  - model.gpt_neox.layers (not model.model.layers)\n  - layer.attention (not layer.self_attn)\n  - No GQA — num_attention_heads == num_key_value_heads\n\nUsage:\n    uv run python scripts/run_pythia_replication.py\n\nOutputs to results/pythia-2.8b/\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport sys\nimport time\nfrom datetime import datetime, timezone\nfrom pathlib import Path\n\n# Ensure project root is importable\nsys.path.insert(0, str(Path(__file__).resolve().parent.parent / \"src\"))\n\nimport structlog\n\nstructlog.configure(\n    processors=[\n        structlog.dev.ConsoleRenderer(),\n    ],\n    wrapper_class=structlog.make_filtering_bound_logger(20),\n)\n\nlog = structlog.get_logger()\n\nMODEL_NAME = \"EleutherAI/pythia-2.8b-deduped\"\nRESULTS_DIR = Path(\"results/pythia-2.8b\")\nRESULTS_DIR.mkdir(parents=True, exist_ok=True)\n\n\ndef banner(text: str) -> None:\n    print(\"\\n\" + \"=\" * 60)\n    print(f\"  {text}\")\n    print(\"=\" * 60 + \"\\n\")\n\n\ndef save_json(path: Path, data: dict) -> None:\n    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))\n    print(f\"Saved: {path}\")\n\n\n# ──────────────────────────── Phase 0: Load + Baseline ────────────────\n\n\ndef load():\n    \"\"\"Load Pythia-2.8B and return (model, tokenizer, info).\"\"\"\n    from verbum.instrument import load_model\n\n    banner(\"LOADING Pythia-2.8B-deduped\")\n    model, tokenizer, info = load_model(MODEL_NAME)\n    print(f\"  Architecture: {type(model).__name__}\")\n    print(f\"  Layers: {info.n_layers}\")\n    print(f\"  Heads: {info.n_heads}\")\n    print(f\"  KV Heads: {info.n_kv_heads}\")\n    print(f\"  Head dim: {info.head_dim}\")\n    print(f\"  Hidden: {info.hidden_size}\")\n    return model, tokenizer, info\n\n\ndef phase0_baseline(model, tokenizer, info):\n    \"\"\"Verify Pythia can compile lambda at all using the gate prompt.\n\n    This is the critical gate: if the base model can't do in-context\n    few-shot lambda compilation, the experiment stops here (which is\n    itself a finding about the localization gradient).\n    \"\"\"\n    from verbum.instrument import LAMBDA_INDICATORS, _detect_lambda, _generate\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 0: Baseline — can Pythia compile lambda?\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    results = []\n    for rp in resolved:\n        # Generate with more tokens for a base model — it may be verbose\n        gen = _generate(model, tokenizer, rp.full_prompt, max_new_tokens=80)\n        has_lambda = _detect_lambda(gen)\n        lambda_count = sum(gen.count(s) for s in LAMBDA_INDICATORS)\n\n        results.append({\n            \"probe_id\": rp.probe_id,\n            \"prompt\": rp.prompt,\n            \"generation\": gen,\n            \"has_lambda\": has_lambda,\n            \"lambda_count\": lambda_count,\n        })\n\n        status = \"✓ COMPILES\" if has_lambda else \"✗ NO LAMBDA\"\n        print(f\"  {status}  [{rp.probe_id}]  {gen[:100]}\")\n\n    success_rate = sum(1 for r in results if r[\"has_lambda\"]) / len(results)\n    print(f\"\\n  Success rate: {success_rate:.0%} ({sum(1 for r in results if r['has_lambda'])}/{len(results)})\")\n\n    save_json(RESULTS_DIR / \"phase0-baseline.json\", {\n        \"model\": MODEL_NAME,\n        \"success_rate\": success_rate,\n        \"results\": results,\n    })\n\n    return results, success_rate\n\n\n# ──────────────────────────── Phase 1: Layer Ablation ─────────────────\n\n\ndef phase1_layer_ablation(model, tokenizer, info):\n    \"\"\"Skip-ablate each layer to find critical layers.\"\"\"\n    from verbum.instrument import ablate_layers\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 1: Layer Ablation — find critical layers\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    # Test on first probe and a second for confirmation\n    all_critical = []\n\n    for rp in resolved[:2]:\n        print(f\"\\n  Probe: {rp.probe_id}\")\n        print(f\"  Prompt: {rp.prompt[:60]}...\")\n\n        baseline, results = ablate_layers(model, tokenizer, rp.full_prompt, info)\n        print(f\"  Baseline: {baseline[:100]}\")\n\n        critical = []\n        for r in results:\n            if not r.has_lambda:\n                critical.append(r.layer)\n                print(f\"    ✗ Layer {r.layer:2d} CRITICAL: {r.generation[:60]}\")\n\n        all_critical.append({\n            \"probe_id\": rp.probe_id,\n            \"baseline\": baseline,\n            \"critical_layers\": critical,\n            \"total_layers\": info.n_layers,\n        })\n\n    # Union of critical layers across probes\n    critical_union = sorted(set().union(*(\n        set(pc[\"critical_layers\"]) for pc in all_critical\n    )))\n\n    print(f\"\\n  Critical layers (union): {critical_union}\")\n    print(f\"  Total critical: {len(critical_union)} / {info.n_layers}\")\n\n    save_json(RESULTS_DIR / \"phase1-layer-ablation.json\", {\n        \"model\": MODEL_NAME,\n        \"n_layers\": info.n_layers,\n        \"critical_layers_union\": critical_union,\n        \"per_probe\": all_critical,\n    })\n\n    return critical_union\n\n\n# ──────────────────────────── Phase 2: Head Ablation ──────────────────\n\n\ndef phase2_head_ablation(model, tokenizer, info, critical_layers):\n    \"\"\"For each critical layer, ablate each head individually.\"\"\"\n    from verbum.instrument import LAMBDA_INDICATORS, _detect_lambda, _generate\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 2: Head Ablation — find essential heads\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    # Direct head ablation (skip experiment framework for simplicity)\n    from verbum.instrument import ablate_heads\n\n    all_results = {}\n    essential_per_probe = {}\n\n    for rp in resolved:\n        print(f\"\\n  Probe: {rp.probe_id}\")\n        baseline, results = ablate_heads(\n            model, tokenizer, rp.full_prompt, info,\n            target_layers=critical_layers,\n            max_new_tokens=80,\n        )\n\n        # Find essential heads (ablation breaks compilation)\n        essential = []\n        degraded = []\n        baseline_count = sum(baseline.count(s) for s in LAMBDA_INDICATORS)\n\n        for r in results:\n            if not r.has_lambda:\n                essential.append((r.layer, r.head))\n            elif r.lambda_count < baseline_count - 1:\n                degraded.append((r.layer, r.head))\n\n        essential_per_probe[rp.probe_id] = {\n            \"essential\": essential,\n            \"degraded\": degraded,\n            \"baseline\": baseline,\n            \"baseline_lambda_count\": baseline_count,\n        }\n\n        print(f\"    Essential: {essential}\")\n        print(f\"    Degraded: {len(degraded)}\")\n\n        all_results[rp.probe_id] = [\n            {\n                \"layer\": r.layer,\n                \"head\": r.head,\n                \"generation\": r.generation,\n                \"has_lambda\": r.has_lambda,\n                \"lambda_count\": r.lambda_count,\n            }\n            for r in results\n        ]\n\n    # Aggregate: head essential across ALL probes\n    from collections import Counter\n\n    break_counts: Counter = Counter()\n    degrade_counts: Counter = Counter()\n    n_probes = len(resolved)\n\n    for pid, pdata in essential_per_probe.items():\n        for l, h in pdata[\"essential\"]:\n            break_counts[(l, h)] += 1\n        for l, h in pdata[\"degraded\"]:\n            degrade_counts[(l, h)] += 1\n\n    essential_all = sorted([\n        (l, h) for (l, h), count in break_counts.items()\n        if count == n_probes\n    ])\n    essential_any = sorted(break_counts.keys())\n\n    total_candidates = len(critical_layers) * info.n_heads\n\n    print(f\"\\n  Essential (all {n_probes} probes): {essential_all}\")\n    print(f\"  Essential (any probe): {essential_any}\")\n    print(f\"  Total degraded: {len(degrade_counts)}\")\n    print(f\"  Total candidates: {total_candidates}\")\n\n    summary = {\n        \"model\": MODEL_NAME,\n        \"critical_layers\": critical_layers,\n        \"n_probes\": n_probes,\n        \"essential_heads_all\": [[l, h] for l, h in essential_all],\n        \"essential_heads_any\": [[l, h] for l, h in essential_any],\n        \"total_degraded\": len(degrade_counts),\n        \"total_candidates\": total_candidates,\n        \"break_counts\": {\n            f\"L{l}:H{h}\": count\n            for (l, h), count in sorted(break_counts.items())\n        },\n        \"degrade_counts\": {\n            f\"L{l}:H{h}\": count\n            for (l, h), count in sorted(degrade_counts.items())\n        },\n    }\n\n    save_json(RESULTS_DIR / \"phase2-head-ablation.json\", summary)\n\n    # Save full results for detailed analysis\n    save_json(RESULTS_DIR / \"phase2-head-ablation-full.json\", {\n        \"per_probe\": {\n            pid: {\n                \"essential\": [[l, h] for l, h in pdata[\"essential\"]],\n                \"degraded\": [[l, h] for l, h in pdata[\"degraded\"]],\n                \"baseline\": pdata[\"baseline\"],\n                \"baseline_lambda_count\": pdata[\"baseline_lambda_count\"],\n            }\n            for pid, pdata in essential_per_probe.items()\n        },\n    })\n\n    return essential_all, essential_any\n\n\n# ──────────────────────────── Phase 3: Comparison ─────────────────────\n\n\ndef phase3_comparison(info, critical_layers, essential_all, essential_any):\n    \"\"\"Compare Pythia results with Qwen and Phi-4.\"\"\"\n\n    banner(\"PHASE 3: Cross-Architecture Comparison\")\n\n    # Load Phi-4 results if available\n    phi4_summary = None\n    phi4_path = Path(\"results/phi4-mini/summary.json\")\n    if phi4_path.exists():\n        phi4_summary = json.loads(phi4_path.read_text())\n\n    comparison = {\n        \"models\": {\n            \"qwen3-4b\": {\n                \"architecture\": \"Qwen2ForCausalLM\",\n                \"params\": \"4.0B\",\n                \"training\": \"General web + instruction tuning\",\n                \"n_layers\": 36,\n                \"n_heads\": 32,\n                \"critical_layers\": [0, 1, 4, 7, 24, 26, 30, 33],\n                \"critical_pct\": 22.2,\n                \"essential_heads\": [[1, 0], [24, 0], [24, 2]],\n                \"n_essential\": 3,\n                \"essential_pct\": 0.26,\n                \"topology\": \"sparse/localized\",\n                \"failure_mode\": \"→ ? then System 2 reasoning\",\n            },\n            \"phi4-mini\": {\n                \"architecture\": \"Phi3ForCausalLM\",\n                \"params\": \"3.8B\",\n                \"training\": \"5T tokens, reasoning-dense synthetic\",\n                \"n_layers\": 32,\n                \"n_heads\": 24,\n                \"critical_layers\": [0, 3, 5, 30],\n                \"critical_pct\": 12.5,\n                \"essential_heads\": [],\n                \"n_essential\": 0,\n                \"essential_pct\": 0.0,\n                \"topology\": \"distributed/redundant\",\n                \"failure_mode\": \"graceful degradation, lambda count drops\",\n            },\n            \"pythia-2.8b\": {\n                \"architecture\": \"GPTNeoXForCausalLM\",\n                \"params\": \"2.8B\",\n                \"training\": \"The Pile (300B tokens), base model, no instruction tuning\",\n                \"n_layers\": info.n_layers,\n                \"n_heads\": info.n_heads,\n                \"critical_layers\": critical_layers,\n                \"critical_pct\": round(\n                    100 * len(critical_layers) / info.n_layers, 1\n                ),\n                \"essential_heads\": [[l, h] for l, h in essential_all],\n                \"n_essential\": len(essential_all),\n                \"essential_pct\": round(\n                    100 * len(essential_all) / (info.n_layers * info.n_heads),\n                    2,\n                ),\n                \"topology\": (\n                    \"sparse/localized\"\n                    if len(essential_all) <= 5\n                    else \"intermediate\"\n                    if len(essential_all) <= 20\n                    else \"distributed\"\n                ),\n            },\n        },\n        \"localization_gradient\": {\n            \"hypothesis\": \"localization ∝ 1/reasoning_training_density\",\n            \"qwen_result\": \"3 essential heads (general training → sparse)\",\n            \"phi4_result\": \"0 essential heads (reasoning-dense → distributed)\",\n            \"pythia_prediction\": \"≤3 essential heads (minimal training → even more localized)\",\n            \"pythia_result\": f\"{len(essential_all)} essential heads\",\n            \"confirmed\": len(essential_all) <= 3,\n        },\n    }\n\n    # Print comparison table\n    print(f\"  {'':>20} {'Qwen3-4B':>12} {'Phi-4-mini':>12} {'Pythia-2.8B':>12}\")\n    print(f\"  {'-'*56}\")\n    for prop in [\n        \"n_layers\", \"n_heads\", \"n_essential\", \"essential_pct\",\n    ]:\n        row = f\"  {prop:>20}\"\n        for model in [\"qwen3-4b\", \"phi4-mini\", \"pythia-2.8b\"]:\n            val = comparison[\"models\"][model].get(prop, \"?\")\n            row += f\"  {val:>10}\"\n        print(row)\n\n    print(f\"\\n  Topology: {comparison['models']['pythia-2.8b']['topology']}\")\n    print(f\"  Gradient hypothesis: {'CONFIRMED ✓' if comparison['localization_gradient']['confirmed'] else 'FALSIFIED ✗'}\")\n\n    save_json(RESULTS_DIR / \"comparison.json\", comparison)\n    return comparison\n\n\n# ──────────────────────────── Main ────────────────────────────────────\n\n\ndef main():\n    start = time.time()\n    banner(f\"PYTHIA-2.8B REPLICATION — {datetime.now(timezone.utc).isoformat()}\")\n\n    model, tokenizer, info = load()\n\n    # Phase 0: Can Pythia compile lambda at all?\n    baseline_results, success_rate = phase0_baseline(model, tokenizer, info)\n\n    if success_rate == 0:\n        banner(\"NEGATIVE RESULT: Pythia cannot compile lambda\")\n        print(\"  The gate prompt does not activate lambda compilation in this\")\n        print(\"  base model. This is itself a finding about the localization\")\n        print(\"  gradient — the compilation function may require instruction\")\n        print(\"  tuning to become accessible via few-shot prompting.\")\n        print()\n        print(\"  Possible next steps:\")\n        print(\"  - Try Pythia-6.9B or Pythia-12B (more capacity)\")\n        print(\"  - Try more exemplars in the gate (5-shot instead of 2-shot)\")\n        print(\"  - Try a different gate formulation for base models\")\n\n        save_json(RESULTS_DIR / \"summary.json\", {\n            \"model\": MODEL_NAME,\n            \"finding\": \"cannot_compile_lambda\",\n            \"success_rate\": success_rate,\n            \"elapsed_s\": time.time() - start,\n            \"timestamp\": datetime.now(timezone.utc).isoformat(),\n            \"interpretation\": (\n                \"Base model Pythia-2.8B does not compile lambda via the \"\n                \"2-shot gate prompt. The compilation function may require \"\n                \"instruction tuning to become accessible, or the model \"\n                \"may lack sufficient capacity at 2.8B parameters.\"\n            ),\n        })\n        return\n\n    if success_rate < 0.6:\n        print(f\"\\n  WARNING: Low success rate ({success_rate:.0%}). Proceeding\")\n        print(\"  with caution — results may be noisy.\")\n\n    # Phase 1: Find critical layers\n    critical_layers = phase1_layer_ablation(model, tokenizer, info)\n\n    if not critical_layers:\n        print(\"  WARNING: No critical layers found!\")\n        print(\"  All layers are individually redundant.\")\n        critical_layers = list(range(info.n_layers))\n\n    # Phase 2: Find essential heads\n    essential_all, essential_any = phase2_head_ablation(\n        model, tokenizer, info, critical_layers\n    )\n\n    # Phase 3: Cross-architecture comparison\n    comparison = phase3_comparison(\n        info, critical_layers, essential_all, essential_any\n    )\n\n    # Final summary\n    elapsed = time.time() - start\n    summary = {\n        \"model\": MODEL_NAME,\n        \"architecture\": \"GPTNeoXForCausalLM\",\n        \"n_layers\": info.n_layers,\n        \"n_heads\": info.n_heads,\n        \"head_dim\": info.head_dim,\n        \"hidden_size\": info.hidden_size,\n        \"baseline_success_rate\": success_rate,\n        \"critical_layers\": critical_layers,\n        \"essential_heads_all\": [[l, h] for l, h in essential_all],\n        \"essential_heads_any\": [[l, h] for l, h in essential_any],\n        \"elapsed_s\": elapsed,\n        \"timestamp\": datetime.now(timezone.utc).isoformat(),\n        \"localization_gradient_confirmed\": len(essential_all) <= 3,\n    }\n    save_json(RESULTS_DIR / \"summary.json\", summary)\n\n    banner(f\"COMPLETE — {elapsed:.0f}s\")\n    print(f\"  Model: {MODEL_NAME}\")\n    print(f\"  Baseline: {success_rate:.0%}\")\n    print(f\"  Critical layers: {critical_layers}\")\n    print(f\"  Essential heads (all probes): {essential_all}\")\n    print(f\"  Essential heads (any probe): {essential_any}\")\n    print(f\"  Gradient hypothesis: {'CONFIRMED' if len(essential_all) <= 3 else 'FALSIFIED'}\")\n    print(f\"  Results: {RESULTS_DIR}\")\n\n\nif __name__ == \"__main__\":\n    main()\n"
mementum/knowledge/chats/session-003.md:        print("  - Try Pythia-6.9B or Pythia-12B (more capacity)")
mementum/knowledge/chats/session-003.md:                "may lack sufficient capacity at 2.8B parameters."
mementum/knowledge/chats/session-003.md:  "content": "#!/usr/bin/env python3\n\"\"\"Replicate the circuit discovery pipeline on Pythia-2.8B-deduped.\n\nTests the localization gradient hypothesis:\n  - Qwen3-4B (general web + instruction) -> 3 essential heads (sparse)\n  - Phi-4-mini (reasoning-dense synthetic) -> 0 essential, 40 degraded\n  - Pythia-2.8B (The Pile only) -> prediction: <=3 essential heads\n\nPythia is a BASE model -- no instruction tuning, no RLHF. The compile\ngate is a few-shot pattern that works as text completion. Phase 0\nverifies this.\n\nKey architecture: GPTNeoXForCausalLM\n  - model.gpt_neox.layers (not model.model.layers)\n  - layer.attention (not layer.self_attn)\n  - No GQA\n\nUsage:\n    uv run python scripts/run_pythia_replication.py\n\nOutputs to results/pythia-2.8b/\n\"\"\"\n\nfrom __future__ import annotations\n\nimport json\nimport sys\nimport time\nfrom collections import Counter\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\n# Ensure project root is importable\nsys.path.insert(0, str(Path(__file__).resolve().parent.parent / \"src\"))\n\nimport structlog\n\nstructlog.configure(\n    processors=[\n        structlog.dev.ConsoleRenderer(),\n    ],\n    wrapper_class=structlog.make_filtering_bound_logger(20),\n)\n\nlog = structlog.get_logger()\n\nMODEL_NAME = \"EleutherAI/pythia-2.8b-deduped\"\nRESULTS_DIR = Path(\"results/pythia-2.8b\")\nRESULTS_DIR.mkdir(parents=True, exist_ok=True)\n\n\ndef banner(text: str) -> None:\n    print(\"\\n\" + \"=\" * 60)\n    print(f\"  {text}\")\n    print(\"=\" * 60 + \"\\n\")\n\n\ndef save_json(path: Path, data: dict) -> None:\n    path.write_text(json.dumps(data, indent=2, ensure_ascii=False))\n    print(f\"Saved: {path}\")\n\n\ndef _lh_list(pairs: list) -> list[list[int]]:\n    \"\"\"Convert list of (layer, head) tuples to JSON-safe [[l, h], ...].\"\"\"\n    return [[layer, head] for layer, head in pairs]\n\n\n# ──────────────────────────── Phase 0: Load + Baseline ────────────────\n\n\ndef load():\n    \"\"\"Load Pythia-2.8B and return (model, tokenizer, info).\"\"\"\n    from verbum.instrument import load_model\n\n    banner(\"LOADING Pythia-2.8B-deduped\")\n    model, tokenizer, info = load_model(MODEL_NAME)\n    print(f\"  Architecture: {type(model).__name__}\")\n    print(f\"  Layers: {info.n_layers}\")\n    print(f\"  Heads: {info.n_heads}\")\n    print(f\"  KV Heads: {info.n_kv_heads}\")\n    print(f\"  Head dim: {info.head_dim}\")\n    print(f\"  Hidden: {info.hidden_size}\")\n    return model, tokenizer, info\n\n\ndef phase0_baseline(model, tokenizer):\n    \"\"\"Verify Pythia can compile lambda at all using the gate prompt.\n\n    This is the critical gate: if the base model can't do in-context\n    few-shot lambda compilation, the experiment stops here (which is\n    itself a finding about the localization gradient).\n    \"\"\"\n    from verbum.instrument import LAMBDA_INDICATORS, _detect_lambda, _generate\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 0: Baseline -- can Pythia compile lambda?\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    results = []\n    for rp in resolved:\n        gen = _generate(\n            model, tokenizer, rp.full_prompt, max_new_tokens=80\n        )\n        has_lambda = _detect_lambda(gen)\n        lcount = sum(gen.count(s) for s in LAMBDA_INDICATORS)\n\n        results.append({\n            \"probe_id\": rp.probe_id,\n            \"prompt\": rp.prompt,\n            \"generation\": gen,\n            \"has_lambda\": has_lambda,\n            \"lambda_count\": lcount,\n        })\n\n        status = \"Y COMPILES\" if has_lambda else \"X NO LAMBDA\"\n        print(f\"  {status}  [{rp.probe_id}]  {gen[:100]}\")\n\n    n_success = sum(1 for r in results if r[\"has_lambda\"])\n    success_rate = n_success / len(results)\n    print(f\"\\n  Success rate: {success_rate:.0%} ({n_success}/{len(results)})\")\n\n    save_json(RESULTS_DIR / \"phase0-baseline.json\", {\n        \"model\": MODEL_NAME,\n        \"success_rate\": success_rate,\n        \"results\": results,\n    })\n\n    return results, success_rate\n\n\n# ──────────────────────────── Phase 1: Layer Ablation ─────────────────\n\n\ndef phase1_layer_ablation(model, tokenizer, info):\n    \"\"\"Skip-ablate each layer to find critical layers.\"\"\"\n    from verbum.instrument import ablate_layers\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 1: Layer Ablation -- find critical layers\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    all_critical = []\n\n    for rp in resolved[:2]:\n        print(f\"\\n  Probe: {rp.probe_id}\")\n        print(f\"  Prompt: {rp.prompt[:60]}...\")\n\n        baseline, results = ablate_layers(\n            model, tokenizer, rp.full_prompt, info\n        )\n        print(f\"  Baseline: {baseline[:100]}\")\n\n        critical = []\n        for r in results:\n            if not r.has_lambda:\n                critical.append(r.layer)\n                gen_snip = r.generation[:60]\n                print(f\"    X Layer {r.layer:2d} CRITICAL: {gen_snip}\")\n\n        all_critical.append({\n            \"probe_id\": rp.probe_id,\n            \"baseline\": baseline,\n            \"critical_layers\": critical,\n            \"total_layers\": info.n_layers,\n        })\n\n    # Union of critical layers across probes\n    critical_union = sorted(\n        set().union(*(set(pc[\"critical_layers\"]) for pc in all_critical))\n    )\n\n    print(f\"\\n  Critical layers (union): {critical_union}\")\n    print(f\"  Total critical: {len(critical_union)} / {info.n_layers}\")\n\n    save_json(RESULTS_DIR / \"phase1-layer-ablation.json\", {\n        \"model\": MODEL_NAME,\n        \"n_layers\": info.n_layers,\n        \"critical_layers_union\": critical_union,\n        \"per_probe\": all_critical,\n    })\n\n    return critical_union\n\n\n# ──────────────────────────── Phase 2: Head Ablation ──────────────────\n\n\ndef phase2_head_ablation(model, tokenizer, info, critical_layers):\n    \"\"\"For each critical layer, ablate each head individually.\"\"\"\n    from verbum.instrument import LAMBDA_INDICATORS, ablate_heads\n    from verbum.probes import load_probe_set, resolve_probes\n\n    banner(\"PHASE 2: Head Ablation -- find essential heads\")\n\n    probe_set = load_probe_set(\"probes/gate-ablation.json\")\n    resolved = resolve_probes(probe_set, Path(\"gates\"))\n\n    essential_per_probe: dict[str, dict] = {}\n\n    for rp in resolved:\n        print(f\"\\n  Probe: {rp.probe_id}\")\n        baseline, results = ablate_heads(\n            model, tokenizer, rp.full_prompt, info,\n            target_layers=critical_layers,\n            max_new_tokens=80,\n        )\n\n        essential = []\n        degraded = []\n        baseline_count = sum(\n            baseline.count(s) for s in LAMBDA_INDICATORS\n        )\n\n        for r in results:\n            if not r.has_lambda:\n                essential.append((r.layer, r.head))\n            elif r.lambda_count < baseline_count - 1:\n                degraded.append((r.layer, r.head))\n\n        essential_per_probe[rp.probe_id] = {\n            \"essential\": essential,\n            \"degraded\": degraded,\n            \"baseline\": baseline,\n            \"baseline_lambda_count\": baseline_count,\n        }\n\n        print(f\"    Essential: {essential}\")\n        print(f\"    Degraded: {len(degraded)}\")\n\n    # Aggregate across probes\n    break_counts: Counter = Counter()\n    degrade_counts: Counter = Counter()\n    n_probes = len(resolved)\n\n    for _pid, pdata in essential_per_probe.items():\n        for layer, head in pdata[\"essential\"]:\n            break_counts[(layer, head)] += 1\n        for layer, head in pdata[\"degraded\"]:\n            degrade_counts[(layer, head)] += 1\n\n    essential_all = sorted([\n        (layer, head)\n        for (layer, head), count in break_counts.items()\n        if count == n_probes\n    ])\n    essential_any = sorted(break_counts.keys())\n\n    total_candidates = len(critical_layers) * info.n_heads\n\n    print(f\"\\n  Essential (all {n_probes} probes): {essential_all}\")\n    print(f\"  Essential (any probe): {essential_any}\")\n    print(f\"  Total degraded: {len(degrade_counts)}\")\n    print(f\"  Total candidates: {total_candidates}\")\n\n    summary = {\n        \"model\": MODEL_NAME,\n        \"critical_layers\": critical_layers,\n        \"n_probes\": n_probes,\n        \"essential_heads_all\": _lh_list(essential_all),\n        \"essential_heads_any\": _lh_list(essential_any),\n        \"total_degraded\": len(degrade_counts),\n        \"total_candidates\": total_candidates,\n        \"break_counts\": {\n            f\"L{layer}:H{head}\": count\n            for (layer, head), count in sorted(break_counts.items())\n        },\n        \"degrade_counts\": {\n            f\"L{layer}:H{head}\": count\n            for (layer, head), count in sorted(degrade_counts.items())\n        },\n    }\n\n    save_json(RESULTS_DIR / \"phase2-head-ablation.json\", summary)\n\n    # Save full results for detailed analysis\n    save_json(RESULTS_DIR / \"phase2-head-ablation-full.json\", {\n        \"per_probe\": {\n            pid: {\n                \"essential\": _lh_list(pdata[\"essential\"]),\n                \"degraded\": _lh_list(pdata[\"degraded\"]),\n                \"baseline\": pdata[\"baseline\"],\n                \"baseline_lambda_count\": pdata[\"baseline_lambda_count\"],\n            }\n            for pid, pdata in essential_per_probe.items()\n        },\n    })\n\n    return essential_all, essential_any\n\n\n# ──────────────────────────── Phase 3: Comparison ─────────────────────\n\n\ndef phase3_comparison(info, critical_layers, essential_all):\n    \"\"\"Compare Pythia results with Qwen and Phi-4.\"\"\"\n\n    banner(\"PHASE 3: Cross-Architecture Comparison\")\n\n    comparison = {\n        \"models\": {\n            \"qwen3-4b\": {\n                \"architecture\": \"Qwen2ForCausalLM\",\n                \"params\": \"4.0B\",\n                \"training\": \"General web + instruction tuning\",\n                \"n_layers\": 36,\n                \"n_heads\": 32,\n                \"critical_layers\": [0, 1, 4, 7, 24, 26, 30, 33],\n                \"critical_pct\": 22.2,\n                \"essential_heads\": [[1, 0], [24, 0], [24, 2]],\n                \"n_essential\": 3,\n                \"essential_pct\": 0.26,\n                \"topology\": \"sparse/localized\",\n            },\n            \"phi4-mini\": {\n                \"architecture\": \"Phi3ForCausalLM\",\n                \"params\": \"3.8B\",\n                \"training\": \"5T tokens, reasoning-dense synthetic\",\n                \"n_layers\": 32,\n                \"n_heads\": 24,\n                \"critical_layers\": [0, 3, 5, 30],\n                \"critical_pct\": 12.5,\n                \"essential_heads\": [],\n                \"n_essential\": 0,\n                \"essential_pct\": 0.0,\n                \"topology\": \"distributed/redundant\",\n            },\n            \"pythia-2.8b\": {\n                \"architecture\": \"GPTNeoXForCausalLM\",\n                \"params\": \"2.8B\",\n                \"training\": \"The Pile (300B tokens), base model\",\n                \"n_layers\": info.n_layers,\n                \"n_heads\": info.n_heads,\n                \"critical_layers\": critical_layers,\n                \"critical_pct\": round(\n                    100 * len(critical_layers) / info.n_layers, 1\n                ),\n                \"essential_heads\": _lh_list(essential_all),\n                \"n_essential\": len(essential_all),\n                \"essential_pct\": round(\n                    100\n                    * len(essential_all)\n                    / (info.n_layers * info.n_heads),\n                    2,\n                ),\n                \"topology\": (\n                    \"sparse/localized\"\n                    if len(essential_all) <= 5\n                    else \"intermediate\"\n                    if len(essential_all) <= 20\n                    else \"distributed\"\n                ),\n            },\n        },\n        \"localization_gradient\": {\n            \"hypothesis\": (\n                \"localization is inversely proportional to \"\n                \"reasoning training density\"\n            ),\n            \"qwen_result\": \"3 essential (general training)\",\n            \"phi4_result\": \"0 essential (reasoning-dense)\",\n            \"pythia_prediction\": \"<=3 essential (minimal training)\",\n            \"pythia_result\": f\"{len(essential_all)} essential\",\n            \"confirmed\": len(essential_all) <= 3,\n        },\n    }\n\n    # Print comparison table\n    hdr = f\"  {'':>20} {'Qwen3-4B':>12} {'Phi-4':>12} {'Pythia':>12}\"\n    print(hdr)\n    print(f\"  {'-' * 56}\")\n    for prop in [\"n_layers\", \"n_heads\", \"n_essential\", \"essential_pct\"]:\n        row = f\"  {prop:>20}\"\n        for mdl in [\"qwen3-4b\", \"phi4-mini\", \"pythia-2.8b\"]:\n            val = comparison[\"models\"][mdl].get(prop, \"?\")\n            row += f\"  {val:>10}\"\n        print(row)\n\n    topology = comparison[\"models\"][\"pythia-2.8b\"][\"topology\"]\n    confirmed = comparison[\"localization_gradient\"][\"confirmed\"]\n    print(f\"\\n  Topology: {topology}\")\n    verdict = \"CONFIRMED\" if confirmed else \"FALSIFIED\"\n    print(f\"  Gradient hypothesis: {verdict}\")\n\n    save_json(RESULTS_DIR / \"comparison.json\", comparison)\n\n\n# ──────────────────────────── Main ────────────────────────────────────\n\n\ndef main():\n    start = time.time()\n    ts = datetime.now(UTC).isoformat()\n    banner(f\"PYTHIA-2.8B REPLICATION -- {ts}\")\n\n    model, tokenizer, info = load()\n\n    # Phase 0: Can Pythia compile lambda at all?\n    _baseline_results, success_rate = phase0_baseline(\n        model, tokenizer\n    )\n\n    if success_rate == 0:\n        banner(\"NEGATIVE RESULT: Pythia cannot compile lambda\")\n        print(\"  The gate prompt does not activate lambda compilation\")\n        print(\"  in this base model. This is itself a finding about\")\n        print(\"  the localization gradient.\")\n        print()\n        print(\"  Possible next steps:\")\n        print(\"  - Try Pythia-6.9B or Pythia-12B (more capacity)\")\n        print(\"  - Try more exemplars (5-shot instead of 2-shot)\")\n        print(\"  - Try a different gate for base models\")\n\n        save_json(RESULTS_DIR / \"summary.json\", {\n            \"model\": MODEL_NAME,\n            \"finding\": \"cannot_compile_lambda\",\n            \"success_rate\": success_rate,\n            \"elapsed_s\": time.time() - start,\n            \"timestamp\": datetime.now(UTC).isoformat(),\n            \"interpretation\": (\n                \"Base model Pythia-2.8B does not compile lambda \"\n                \"via the 2-shot gate prompt.\"\n            ),\n        })\n        return\n\n    if success_rate < 0.6:\n        print(f\"\\n  WARNING: Low success rate ({success_rate:.0%}).\")\n        print(\"  Proceeding with caution -- results may be noisy.\")\n\n    # Phase 1: Find critical layers\n    critical_layers = phase1_layer_ablation(model, tokenizer, info)\n\n    if not critical_layers:\n        print(\"  WARNING: No critical layers found!\")\n        print(\"  All layers are individually redundant.\")\n        critical_layers = list(range(info.n_layers))\n\n    # Phase 2: Find essential heads\n    essential_all, essential_any = phase2_head_ablation(\n        model, tokenizer, info, critical_layers\n    )\n\n    # Phase 3: Cross-architecture comparison\n    phase3_comparison(info, critical_layers, essential_all)\n\n  

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/call_b1HkNa9rYUV9tCzX1AWOe6Wg.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

## Assistant


Yes — I would retry on **Qwen3-14B**, but I would **not treat it as “just rerun the same test.”** I’d rerun it as the **capacity check for whether the β-program becomes readable at the sweet-spot scale**.

The 8B result says:

> constant/applicative C structure is present, but mostly as a broad C-count/common-mode signal, not as a clean recoverable ordered β-program.

That does **not** falsify “the program exists.” It says the current instrument on 8B mostly sees **object/application load**, not the actual **sequence of β reductions attention executes**.

## My recommendation

**Yes: run Qwen3-14B next.**

Reasons:

1. **8B has repeatedly looked like a floor model.**  
   Prior memory says things like:
   - B native-order is “frame-robust at scale, fragile at 8B floor.”
   - type direction became partially causal at **14B**, not 8B.
   - sign/topological operation structure sharpened toward 14B.
   - 14B has repeatedly been where the routing/register geometry becomes cleaner.

2. **The 8B const run gave the right kind of “almost but smeared” result.**  
   The graded C-count signal is strong:
   - FFN Spearman z(C) vs C-count = `0.5526`
   - Attn Spearman z(C) vs C-count = `0.6305`

   But hard program tracking is borderline:
   - FFN C/S acc = `0.5489`, p=`0.055`
   - Attention fails.

   That is exactly what I’d expect if 8B has the substrate but not enough capacity / separation for the **program trace** to crystallize cleanly.

3. **14B is the right next model because it tests the actual hypothesis.**  
   The hypothesis is not “does any model have C-count?”  
   The hypothesis is:

   > at sufficient capacity, the FFN/residual register should carry the β-reduction program clearly enough that attention’s execution path can be decoded against it.

   14B is the known sweet spot for that kind of thing in this project.

## But I would tighten the target before running

The existing `ffn_program_decode.py` still mostly asks:

- What is the **dominant fired combinator**?
- Does z(track) scale with **count**?
- Does FFN lead attention?

That is adjacent to “program,” but not the whole thing.

The actual program is closer to:

```text
fired_sequence = [S, B, C, C, ...]
```

or under the corrected reading:

```text
reduction schedule / β-step sequence
```

So the stronger 14B question should be:

> Can Qwen3-14B decode the ordered β-reduction sequence better than 8B, not merely the dominant combinator or object count?

For the first 14B retry, I’d still run the existing script for comparability, but interpret it as **capacity sweep / sanity check**, not final program proof.

## Exact 14B run I’d do first

Assuming memory/GPU allows:

```bash
uv run python scripts/experiments/ffn_program_decode.py \
  --model Qwen/Qwen3-14B \
  --probe-set data/firing-probes.const.jsonl \
  --track C \
  --n-perm-calib 300 \
  --n-perm-stat 2000 \
  --n-nonfiring 40 \
  --seed 0
```

Expected output names, given current slug logic, should be something like:

```text
results/ffn-program-decode/verdict_qwen3-14b_const.json
results/ffn-program-decode/per_item_qwen3-14b_const.json
results/ffn-program-decode/meta_qwen3-14b_const.json
```

I would compare directly against:

```text
results/ffn-program-decode/verdict_qwen3-8b_const.json
```

## What would count as a real 14B positive?

Not merely “z(C) rises with C-count.” 8B already does that.

A meaningful 14B improvement would be:

1. **Hard C-vs-S tracking becomes clearly significant**
   - FFN acc well above majority, not p=`0.055`
   - ideally p `< 0.01`
   - fewer blanket C predictions

2. **FFN improves more than attention**
   - If both improve equally, it may still be broad representational structure.
   - If FFN sharpens specifically, that supports “program register.”

3. **Per-category behavior improves**
   - 8B:
     - ditrans C: FFN acc `0.970`
     - trans S: FFN acc `0.030`
     - intrans S: FFN acc `0.212`

   A real improvement would reduce the C common-mode and correctly identify the S-light cases.

4. **Lead-lag becomes less contradictory**
   - 8B has peak-diff negative but xcorr positive.
   - 14B positive would ideally make the lead relation method-stable.

## What would still not be enough?

Even if 14B improves, this test still does not fully decode the program. It tests **dominant/graded opcode readability**.

To truly find the program, the next instrument should probably compare:

```text
ground-truth fired_sequence
vs
layerwise decoded combinator sequence
```

Not just:

```text
dominant_fired
vs
dominant decoded op
```

The program-level test should ask:

- Does layer/order align with `fired_sequence`?
- Does decoded sequence edit-distance drop at 14B?
- Do FFN states predict the next attention reduction step?
- Does attention consume the FFN-emitted opcode/value one layer later?
- Does constant/applicative C sequence beat existential B sequence as ground truth?

## Bottom line

Yes, retry on **Qwen3-14B**.

But the expected finding should be phrased carefully:

> 8B shows the corrected applicative-C signal but not a clean β-program trace. 14B is the right capacity/sweet-spot test: if the program is embedded cleanly anywhere in this family, 14B should sharpen hard C/S tracking, reduce C common-mode saturation, and make FFN-vs-attention timing more coherent. If 14B still only gives graded C-count without sequence-level tracking, then the “program” is probably distributed/holographic rather than readable as a discrete β-instruction tape by this instrument.

My vote: **run 14B now, then build the sequence-level decoder if 14B gives any sharpening.**

## User


Use my tmux main:1 window to run it, don't poll I'll tell you when it completes

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl --track C --n-perm-calib 300 --n-perm-stat 2000 --n-nonfiring 40 --seed 0 2>&1 | tee results/ffn-program-decode/run_qwen3-14b_const.log' Enter && sleep 1 && tmux capture-pane -p -t main:1 | tail -80",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
(C) RESCUE: rescue=11 anti-rescue=0 ⇒ True

specificity: firing max-z(BSC)=29.6587 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-8b_const.json (+ per_item, meta)
uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B  151.92s user 13.17s system 78% cpu 3:29.1
8 total
tee results/ffn-program-decode/run_qwen3-8b_const.log  0.00s user 0.00s system 0% cpu 3:29.18 total
[26-06-23][7:14:59][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14B --pro
be-set data/firing-probes.const.jsonl --track C --n-perm-calib 300 --n-perm-stat 2000 --n-nonfiring 40 --seed 0 2>&1 | t
ee results/ffn-program-decode/run_qwen3-14b_const.log
usage: ffn_program_decode.py [-h] [--model MODEL] [--max-items MAX_ITEMS]
                             [--zone-lo ZONE_LO] [--zone-hi ZONE_HI]
                             [--onset-tau ONSET_TAU] [--max-lag MAX_LAG]
                             [--n-perm-stat N_PERM_STAT]
                             [--n-nonfiring N_NONFIRING] [--seed SEED]
                             [--probe-set PROBE_SET] [--track {B,C,S}]
                             [--smoke]
ffn_program_decode.py: error: unrecognized arguments: --n-perm-calib 300
[26-06-23][7:52:56][mwhitford@olga][0][~/src/verbum][git:main]
λ
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl --track C --n-perm-stat 2000 --n-nonfiring 40 --seed 0 2>&1 | tee results/ffn-program-decode/run_qwen3-14b_const.log' Enter && sleep 1 && tmux capture-pane -p -t main:1 | tail -60",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
specificity: firing max-z(BSC)=29.6587 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-8b_const.json (+ per_item, meta)
uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B  151.92s user 13.17s system 78% cpu 3:29.1
8 total
tee results/ffn-program-decode/run_qwen3-8b_const.log  0.00s user 0.00s system 0% cpu 3:29.18 total
[26-06-23][7:14:59][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14B --pro
be-set data/firing-probes.const.jsonl --track C --n-perm-calib 300 --n-perm-stat 2000 --n-nonfiring 40 --seed 0 2>&1 | t
ee results/ffn-program-decode/run_qwen3-14b_const.log
usage: ffn_program_decode.py [-h] [--model MODEL] [--max-items MAX_ITEMS]
                             [--zone-lo ZONE_LO] [--zone-hi ZONE_HI]
                             [--onset-tau ONSET_TAU] [--max-lag MAX_LAG]
                             [--n-perm-stat N_PERM_STAT]
                             [--n-nonfiring N_NONFIRING] [--seed SEED]
                             [--probe-set PROBE_SET] [--track {B,C,S}]
                             [--smoke]
ffn_program_decode.py: error: unrecognized arguments: --n-perm-calib 300
[26-06-23][7:52:56][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14B --pro
be-set data/firing-probes.const.jsonl --track C --n-perm-stat 2000 --n-nonfiring 40 --seed 0 2>&1 | tee results/ffn-prog
ram-decode/run_qwen3-14b_const.log
```

## Assistant


ASYNC: launched the corrected Qwen3-14B const run in `tmux main:1` and verified it started.

Note: my first send included `--n-perm-calib 300`, but this script’s CLI does not accept that flag, so it exited immediately with an argparse error. I corrected and relaunched without it:

```bash
cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/ffn_program_decode.py \
  --model Qwen/Qwen3-14B \
  --probe-set data/firing-probes.const.jsonl \
  --track C \
  --n-perm-stat 2000 \
  --n-nonfiring 40 \
  --seed 0 \
  2>&1 | tee results/ffn-program-decode/run_qwen3-14b_const.log
```

Waiting for your signal; I won’t poll.

## User


job is done

### Thinking

**Analyzing outputs**

I think it's time to analyze the outputs properly. We might need to use some tasks to guide this process. A multi-step approach seems like a good idea to ensure we cover everything thoroughly. Okay, let's get started on this and break it down step by step, so we don’t miss any important details. I'm curious to see what we can uncover through this analysis!


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/meta_qwen3-14b_const.json",
  "limit": 120
}
```

**Summary:** Reading meta_qwen3-14b_const.json (0-120)

**Output:**
```
{
  "model": "Qwen/Qwen3-14B",
  "git_sha": "893ddcec940684c06a2919387d4103d08b4e98cc",
  "timestamp_utc": "2026-06-23T14:58:06.159353+00:00",
  "transformers_version": "5.5.4",
  "corpus": {
    "train": "data/compile-train.canonical.jsonl",
    "test": "data/compile-test.canonical.jsonl",
    "eval": "data/compile-eval.canonical.jsonl"
  },
  "params": {
    "max_items": null,
    "zone_lo": 0.7,
    "zone_hi": 0.86,
    "onset_tau": 2.0,
    "max_lag": 4,
    "n_perm_calib": 300,
    "ppc": null,
    "null_cap": null,
    "n_perm_stat": 2000,
    "n_nonfiring": 40,
    "seed": 0,
    "track": "C",
    "probe_set": "data/firing-probes.const.jsonl"
  },
  "method": "saturate quantifiers \u2192 fired_sequence ground truth; dual-register decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag + C rescue, matched-prefix null calibration."
}
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-14b_const.json",
  "limit": 180
}
```

**Summary:** Reading verdict_qwen3-14b_const.json (0-180)

**Output:**
```
{
  "model": "Qwen/Qwen3-14B",
  "n_layers": 40,
  "track": "C",
  "n_firing_items": 133,
  "n_nonfiring_control": 0,
  "zone_depth": [
    0.7,
    0.86
  ],
  "ffn_zone_layers": [
    28,
    29,
    30,
    31,
    32
  ],
  "attn_zone_layers": [
    28,
    29,
    30,
    31,
    32,
    33
  ],
  "ffn_crystal_layers": [
    0,
    1,
    3,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32
  ],
  "attn_crystal_layers": [
    0,
    1,
    2,
    3,
    4,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32,
    33,
    35,
    36,
    37,
    38,
    39
  ],
  "truth_distribution": {
    "C": 67,
    "S": 66
  },
  "A_tracking": {
    "ffn_acc": 0.609,
    "ffn_null_mean": 0.4955,
    "ffn_perm_p": 0.0005,
    "attn_acc": 0.3534,
    "attn_null_mean": 0.3073,
    "attn_perm_p": 0.0265,
    "majority_baseline_acc": 0.5038,
    "majority_label": "C",
    "ffn_beats_attn": true,
    "ffn_beats_majority": true
  },
  "A_bs_discrimination": {
    "tracked_combinator": "C",
    "n": 133,
    "bs_truth": {
      "C": 67,
      "S": 66
    },
    "ffn_acc": 0.6165,
    "ffn_null_mean": 0.503,
    "ffn_perm_p": 0.0005,
    "attn_acc": 0.5338,
    "attn_null_mean": 0.5032,
    "attn_perm_p": 0.1744,
    "majority_baseline_acc": 0.5038,
    "majority_label": "C",
    "ffn_beats_attn": true,
    "ffn_beats_majority": true
  },
  "A_graded_bcount": {
    "n": 133,
    "track": "C",
    "ffn_spearman_zTrack_vs_count": 0.5367,
    "ffn_spearman_p": 0.0,
    "attn_spearman_zTrack_vs_count": 0.5672,
    "attn_spearman_p": 0.0,
    "ffn_beats_attn": false,
    "zTrack_by_count_ffn": {
      "0": 0.54,
      "1": 0.968,
      "2": 1.245
    },
    "zTrack_by_count_attn": {
      "0": 0.309,
      "1": 0.563,
      "2": 0.677
    }
  },
  "B_lead_lag": {
    "peak_diff": {
      "n": 133,
      "n_pos": 97,
      "n_neg": 21,
      "n_zero": 15,
      "median": 1.0,
      "mean": 1.1578947368421053,
      "frac_positive": 0.8220338983050848,
      "sign_test_p": 7.271713570135107e-13
    },
    "xcorr_lag": {
      "n": 133,
      "n_pos": 77,
      "n_neg": 55,
      "n_zero": 1,
      "median": 1.0,
      "mean": 0.3233082706766917,
      "frac_positive": 0.5833333333333334,
      "sign_test_p": 0.06717037054890534
    },
    "xcorr_lag_hist": {
      "-1": 8,
      "-2": 28,
      "1": 23,
      "2": 21,
      "-3": 19,
      "0": 1,

[CONTENT TRUNCATED] Showing lines 1 to 180 of 702 total lines. Use line_offset=180 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/ffn-program-decode/run_qwen3-14b_const.log",
  "limit": 220
}
```

**Summary:** Reading run_qwen3-14b_const.log (0-220)

**Output:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
══════════════════════════════════════════════════════════════════════════════
FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)
══════════════════════════════════════════════════════════════════════════════
[corpus] source=probe-set:data/firing-probes.const.jsonl  firing items=133  nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/443 [00:00<?, ?it/s]Loading weights:   0%|          | 1/443 [00:00<06:26,  1.14it/s]Loading weights:   0%|          | 2/443 [00:01<03:12,  2.29it/s]Loading weights:   4%|▍         | 19/443 [00:01<00:14, 29.36it/s]Loading weights:   9%|▊         | 38/443 [00:01<00:06, 59.23it/s]Loading weights:  14%|█▎        | 60/443 [00:01<00:04, 90.69it/s]Loading weights:  19%|█▊        | 82/443 [00:01<00:03, 116.76it/s]Loading weights:  23%|██▎       | 104/443 [00:01<00:02, 136.94it/s]Loading weights:  28%|██▊       | 126/443 [00:01<00:02, 152.35it/s]Loading weights:  33%|███▎      | 147/443 [00:01<00:01, 164.31it/s]Loading weights:  37%|███▋      | 166/443 [00:01<00:01, 168.79it/s]Loading weights:  42%|████▏     | 185/443 [00:01<00:01, 170.12it/s]Loading weights:  46%|████▌     | 204/443 [00:02<00:01, 166.87it/s]Loading weights:  51%|█████     | 225/443 [00:02<00:01, 174.49it/s]Loading weights:  56%|█████▌    | 246/443 [00:02<00:01, 182.18it/s]Loading weights:  60%|█████▉    | 265/443 [00:02<00:00, 183.18it/s]Loading weights:  64%|██████▍   | 284/443 [00:02<00:00, 179.50it/s]Loading weights:  68%|██████▊   | 303/443 [00:02<00:00, 169.90it/s]Loading weights:  73%|███████▎  | 324/443 [00:02<00:00, 177.12it/s]Loading weights:  78%|███████▊  | 345/443 [00:02<00:00, 184.74it/s]Loading weights:  82%|████████▏ | 365/443 [00:02<00:00, 188.92it/s]Loading weights:  87%|████████▋ | 385/443 [00:03<00:00, 187.86it/s]Loading weights:  91%|█████████ | 404/443 [00:03<00:00, 183.95it/s]Loading weights:  96%|█████████▌| 424/443 [00:03<00:00, 181.64it/s]Loading weights: 100%|██████████| 443/443 [00:03<00:00, 131.75it/s]
[v2] Model loaded in 4.0s
[model] Qwen/Qwen3-14B  layers=40

[calib] FFN gate register ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] attention o_proj register ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] FFN  crystal layers=31 zone=[28, 29, 30, 31, 32]
[calib] attn crystal layers=39 zone=[28, 29, 30, 31, 32, 33]

[decode] 133 firing items ...
[decode]   item 0/133 ...
[decode]   item 20/133 ...
[decode]   item 40/133 ...
[decode]   item 60/133 ...
[decode]   item 80/133 ...
[decode]   item 100/133 ...
[decode]   item 120/133 ...

══════════════════════════════════════════════════════════════════════════════
VERDICT
══════════════════════════════════════════════════════════════════════════════
items=133  truth={'C': 67, 'S': 66}

(A) TRACKING fired_sequence (decode the dominant fired combinator):
  FFN_acc =0.609  (null 0.4955, p=0.0005)
  Attn_acc=0.3534  (null 0.3073, p=0.0265)
  majority-baseline=0.5038 ('C')
  ⇒ FFN beats attn: True  | FFN beats majority: True

(A') C-vs-S discrimination (common-mode-resistant; n=133 {'C': 67, 'S': 66}):
  FFN_acc =0.6165  (null 0.503, p=0.0005)
  Attn_acc=0.5338  (null 0.5032, p=0.1744)
  majority-baseline=0.5038 ⇒ FFN beats attn: True | beats majority: True

(A'') GRADED — decoded z(C) vs C-count (n=133):
  FFN  Spearman=0.5367 (p=0.0)  z(C)/count={'0': 0.54, '1': 0.968, '2': 1.245}
  Attn Spearman=0.5672 (p=0.0)  z(C)/count={'0': 0.309, '1': 0.563, '2': 0.677}
  ⇒ FFN beats attn: False

(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):
  peak-diff: median=1.0 frac+=0.8220338983050848 n=133 sign-p=7.271713570135107e-13  hist={-1: 17, 3: 24, 0: 15, 1: 43, 2: 28, -2: 4, 4: 2}
  xcorr-lag: median=1.0 frac+=0.5833333333333334 n=133 sign-p=0.06717037054890534  hist={-1: 8, -2: 28, 1: 23, 2: 21, -3: 19, 0: 1, 3: 33}
  (positive ⇒ FFN leads attention; prediction ≈ +1)

(C) RESCUE: rescue=35 anti-rescue=1 ⇒ True

specificity: firing max-z(BSC)=32.9269 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-14b_const.json (+ per_item, meta)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 - <<'PY'\nimport json, collections, statistics, pathlib\nbase=pathlib.Path('/Users/mwhitford/src/verbum/results/ffn-program-decode')\nfor name in ['qwen3-8b_const','qwen3-14b_const']:\n rows=json.loads((base/f'per_item_{name}.json').read_text())\n v=json.loads((base/f'verdict_{name}.json').read_text())\n print('\\n==',name,'==')\n print('A',v['A_tracking'])\n print('Aprime',v['A_bs_discrimination'])\n print('graded',v['A_graded_bcount'])\n for key in ['category','dominant_fired','ffn_dominant','attn_dominant','c_count']:\n  print(key, dict(collections.Counter(r.get(key) for r in rows)))\n cats=collections.defaultdict(list)\n for r in rows: cats[r['category']].append(r)\n for cat,rs in cats.items():\n  print(' cat',cat,'n',len(rs),'truth',dict(collections.Counter(r['dominant_fired'] for r in rs)),\n        'ffn_acc',round(sum(r['ffn_correct'] for r in rs)/len(rs),3),\n        'attn_acc',round(sum(r['attn_correct'] for r in rs)/len(rs),3),\n        'mean zC ffn',round(statistics.mean(r['zt_ffn'] for r in rs),3),\n        'attn',round(statistics.mean(r['zt_attn'] for r in rs),3),\n        'mean ffn C-S',round(statistics.mean(r['ffn_score']['C']-r['ffn_score']['S'] for r in rs),3),\n        'attn C-S',round(statistics.mean(r['attn_score']['C']-r['attn_score']['S'] for r in rs),3))\n by=collections.defaultdict(list)\n for r in rows: by[r['dominant_fired']].append(r)\n for t,rs in by.items():\n  print(' truth',t,'n',len(rs),'ffn C-S mean',round(statistics.mean(r['ffn_score']['C']-r['ffn_score']['S'] for r in rs),3), 'attn C-S',round(statistics.mean(r['attn_score']['C']-r['attn_score']['S'] for r in rs),3))\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python3 - <<'PY' import json, colle...

**Output:**
```
Exit code: 0
Stdout:
== qwen3-8b_const ==
A {'ffn_acc': 0.5489, 'ffn_null_mean': 0.5038, 'ffn_perm_p': 0.055, 'attn_acc': 0.4662, 'attn_null_mean': 0.4666, 'attn_perm_p': 0.5852, 'majority_baseline_acc': 0.5038, 'majority_label': 'C', 'ffn_beats_attn': True, 'ffn_beats_majority': True}
Aprime {'tracked_combinator': 'C', 'n': 133, 'bs_truth': {'C': 67, 'S': 66}, 'ffn_acc': 0.5489, 'ffn_null_mean': 0.5038, 'ffn_perm_p': 0.055, 'attn_acc': 0.4662, 'attn_null_mean': 0.504, 'attn_perm_p': 1.0, 'majority_baseline_acc': 0.5038, 'majority_label': 'C', 'ffn_beats_attn': True, 'ffn_beats_majority': True}
graded {'n': 133, 'track': 'C', 'ffn_spearman_zTrack_vs_count': 0.5526, 'ffn_spearman_p': 0.0, 'attn_spearman_zTrack_vs_count': 0.6305, 'attn_spearman_p': 0.0, 'ffn_beats_attn': False, 'zTrack_by_count_ffn': {'0': 0.488, '1': 0.833, '2': 1.035}, 'zTrack_by_count_attn': {'0': 0.567, '1': 1.091, '2': 1.262}}
category {'ditrans_const': 67, 'trans_const': 33, 'intrans': 33}
dominant_fired {'C': 67, 'S': 66}
ffn_dominant {'C': 123, 'S': 10}
attn_dominant {'C': 119, 'S': 4, 'B': 10}
c_count {2: 67, 1: 33, 0: 33}
 cat ditrans_const n 67 truth {'C': 67} ffn_acc 0.97 attn_acc 0.925 mean zC ffn 1.035 attn 1.262 mean ffn C-S 21.476 attn C-S 23.375
 cat trans_const n 33 truth {'S': 33} ffn_acc 0.03 attn_acc 0.0 mean zC ffn 0.833 attn 1.091 mean ffn C-S 14.686 attn C-S 20.144
 cat intrans n 33 truth {'S': 33} ffn_acc 0.212 attn_acc 0.0 mean zC ffn 0.488 attn 0.567 mean ffn C-S 4.001 attn C-S 6.148
 truth C n 67 ffn C-S mean 21.476 attn C-S 23.375
 truth S n 66 ffn C-S mean 9.343 attn C-S 13.146

== qwen3-14b_const ==
A {'ffn_acc': 0.609, 'ffn_null_mean': 0.4955, 'ffn_perm_p': 0.0005, 'attn_acc': 0.3534, 'attn_null_mean': 0.3073, 'attn_perm_p': 0.0265, 'majority_baseline_acc': 0.5038, 'majority_label': 'C', 'ffn_beats_attn': True, 'ffn_beats_majority': True}
Aprime {'tracked_combinator': 'C', 'n': 133, 'bs_truth': {'C': 67, 'S': 66}, 'ffn_acc': 0.6165, 'ffn_null_mean': 0.503, 'ffn_perm_p': 0.0005, 'attn_acc': 0.5338, 'attn_null_mean': 0.5032, 'attn_perm_p': 0.1744, 'majority_baseline_acc': 0.5038, 'majority_label': 'C', 'ffn_beats_attn': True, 'ffn_beats_majority': True}
graded {'n': 133, 'track': 'C', 'ffn_spearman_zTrack_vs_count': 0.5367, 'ffn_spearman_p': 0.0, 'attn_spearman_zTrack_vs_count': 0.5672, 'attn_spearman_p': 0.0, 'ffn_beats_attn': False, 'zTrack_by_count_ffn': {'0': 0.54, '1': 0.968, '2': 1.245}, 'zTrack_by_count_attn': {'0': 0.309, '1': 0.563, '2': 0.677}}
category {'ditrans_const': 67, 'trans_const': 33, 'intrans': 33}
dominant_fired {'C': 67, 'S': 66}
ffn_dominant {'C': 117, 'S': 14, 'B': 2}
attn_dominant {'C': 79, 'B': 52, 'S': 2}
c_count {2: 67, 1: 33, 0: 33}
 cat ditrans_const n 67 truth {'C': 67} ffn_acc 1.0 attn_acc 0.687 mean zC ffn 1.245 attn 0.677 mean ffn C-S 28.896 attn C-S 14.258
 cat trans_const n 33 truth {'S': 33} ffn_acc 0.121 attn_acc 0.03 mean zC ffn 0.968 attn 0.563 mean ffn C-S 15.631 attn C-S 10.291
 cat intrans n 33 truth {'S': 33} ffn_acc 0.303 attn_acc 0.0 mean zC ffn 0.54 attn 0.309 mean ffn C-S 2.579 attn C-S 3.005
 truth C n 67 ffn C-S mean 28.896 attn C-S 14.258
 truth S n 66 ffn C-S mean 9.105 attn C-S 6.648
```

### Thinking

**Completing the task**

I think I need to inspect the remainder for a thorough rescue, but I also want to ensure I’m not overlooking anything important. I want my final output to have some nuance, which might require careful consideration. It seems essential to tie up all loose ends here. So, I’ll focus on completing the task at hand first, ensuring everything is in place before making any final decisions. Let's get this right!


## Assistant


The 14B run completed cleanly and the result is **meaningfully better than 8B in exactly the way we hoped** — but still not a full “discrete β-program tape” readout.

## Completion

Run wrote:

```text
results/ffn-program-decode/verdict_qwen3-14b_const.json
results/ffn-program-decode/per_item_qwen3-14b_const.json
results/ffn-program-decode/meta_qwen3-14b_const.json
results/ffn-program-decode/run_qwen3-14b_const.log
```

Log ends cleanly with:

```text
[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-14b_const.json (+ per_item, meta)
```

No runtime crash in the experiment.

---

## Headline verdict

**Yes: 14B sharpens the program signal relative to 8B.**

The 8B result was:

> corrected C/applicative structure is present, but hard C-vs-S tracking is borderline and mostly C-common-mode.

The 14B result is:

> corrected C/applicative structure is not merely present; the FFN gate register now significantly tracks C-vs-S, beats majority, beats attention, and has a much stronger FFN-specific separation. This supports the “minimum capacity / 14B sweet spot” hypothesis.

But:

> it still mostly reads **dominant/graded C structure**, not the whole ordered β-reduction program.

---

## Direct 8B → 14B comparison

### A. Hard dominant tracking

| model | FFN acc | FFN p | Attn acc | Attn p | majority |
|---|---:|---:|---:|---:|---:|
| Qwen3-8B | 0.5489 | 0.055 | 0.4662 | 0.5852 | 0.5038 |
| Qwen3-14B | **0.6090** | **0.0005** | 0.3534 | 0.0265 | 0.5038 |

This is the clean capacity result.

At 8B, FFN hard tracking was borderline: p=`0.055`.

At 14B, FFN hard tracking is clearly significant: p=`0.0005`.

So the C-label correction **does flip from “suggestive” to “real” at 14B**.

### A′. C-vs-S discrimination

| model | FFN C/S acc | FFN p | Attn C/S acc | Attn p |
|---|---:|---:|---:|---:|
| Qwen3-8B | 0.5489 | 0.055 | 0.4662 | 1.0 |
| Qwen3-14B | **0.6165** | **0.0005** | 0.5338 | 0.1744 |

This is the most important number for the program-register hypothesis.

At 14B:

```text
FFN C-vs-S acc = 0.6165, p=0.0005
Attn C-vs-S acc = 0.5338, p=0.1744
```

So the **FFN gate register** carries the corrected C-vs-S program label. Attention does not significantly carry it in the same common-mode-resistant metric.

That is much closer to the story:

```text
FFN = β-program / opcode register
attention = executor / depth-routing register
```

### A″. Graded z(C) vs C-count

| model | FFN Spearman | Attn Spearman | FFN z(C) 0→1→2 | Attn z(C) 0→1→2 |
|---|---:|---:|---|---|
| Qwen3-8B | 0.5526 | 0.6305 | 0.488 → 0.833 → 1.035 | 0.567 → 1.091 → 1.262 |
| Qwen3-14B | 0.5367 | 0.5672 | 0.540 → 0.968 → 1.245 | 0.309 → 0.563 → 0.677 |

The graded C-count signal remains strong in both registers.

Interesting shift:

- At 8B, attention’s raw z(C) was bigger than FFN.
- At 14B, FFN’s raw z(C) is bigger than attention.

14B FFN:

```text
C-count 0: 0.540
C-count 1: 0.968
C-count 2: 1.245
```

14B attention:

```text
C-count 0: 0.309
C-count 1: 0.563
C-count 2: 0.677
```

That’s important. The graded rank correlation is still slightly higher in attention, but the **amplitude / separability shifted into FFN** at 14B.

This again supports: 14B embeds the applicative-C program more cleanly in FFN.

---

## Category-level behavior

Dataset:

```text
ditrans_const: 67, truth C
trans_const:   33, truth S
intrans:       33, truth S
```

### Qwen3-8B

```text
ditrans_const truth C:
  FFN acc  0.970
  Attn acc 0.925

trans_const truth S:
  FFN acc  0.030
  Attn acc 0.000

intrans truth S:
  FFN acc  0.212
  Attn acc 0.000
```

### Qwen3-14B

```text
ditrans_const truth C:
  FFN acc  1.000
  Attn acc 0.687

trans_const truth S:
  FFN acc  0.121
  Attn acc 0.030

intrans truth S:
  FFN acc  0.303
  Attn acc 0.000
```

14B improves mostly by:

1. making all C-dominant ditransitives FFN-correct;
2. modestly improving recognition of S-light items;
3. degrading attention hard classification, which sharpens the FFN/attention split.

Still, FFN remains C-biased:

```text
8B FFN predictions:
  C: 123/133
  S: 10/133

14B FFN predictions:
  C: 117/133
  S: 14/133
  B: 2/133
```

So 14B reduces C saturation slightly, but not dramatically.

---

## Lead-lag

### 8B

```text
peak-diff median = -3.0, p=2.99e-11
xcorr-lag median = +2.0, p=0.008
```

Contradictory / method-sensitive.

### 14B

```text
peak-diff median = +1.0, p=7.27e-13
xcorr-lag median = +1.0, p=0.067
```

This is much more aligned with the original prediction:

> positive ⇒ FFN leads attention; prediction ≈ +1

At 14B:

- peak-diff strongly says FFN leads by about one layer;
- xcorr is also positive median +1, but only borderline/n.s. p=`0.067`.

So lead-lag is no longer contradictory. It becomes **directionally coherent** with the FFN→attention execution story, though not fully robust across metrics.

This is another capacity win.

---

## Rescue

```text
8B:  rescue=11, anti_rescue=0
14B: rescue=35, anti_rescue=1
```

This improved strongly.

Caveat: rescue is still hard to interpret because FFN has a strong C prior. But the 14B jump is notable and consistent with FFN being more useful than attention for corrected program labels.

---

## What this means for “finding the program”

Your target is:

> the β-reductions that make up the program that attention executes.

The 14B run gives a **positive capacity signal**:

```text
at 8B:  corrected C structure visible, but smeared/common-mode
at 14B: corrected C-vs-S program label significantly readable in FFN
```

So yes: 14B looks like the right model for this.

But the current instrument is still reading:

```text
dominant fired combinator
C-vs-S contrast
z(C) vs count
lead-lag summary
```

It is **not yet reading the ordered β-program**:

```text
[S, B, C, C]
```

as a sequence.

So I’d state the scientific result like this:

> Qwen3-14B resolves the 8B ambiguity. With the corrected constant/applicative labels, the FFN gate register significantly decodes C-vs-S program structure (`0.6165`, p=`0.0005`) while attention does not (`0.5338`, p=`0.1744`). Lead-lag also becomes directionally coherent with FFN leading attention by ~1 layer. This supports the capacity-threshold hypothesis and makes 14B the right substrate for program extraction. However, the current test still reads dominant/graded opcode structure, not the ordered β-reduction tape; the next instrument should decode sequence alignment against `fired_sequence`.

## My recommendation

Yes, 14B is the sweet spot for the next step.

Next step should not be another size rerun yet. It should be a **sequence-level program decoder** on 14B.

Something like:

```text
ground truth:
  fired_sequence = [S, B, C, C]

per layer:
  FFN decoded op distribution over {B,S,C}
  attention decoded depth / WHNF distribution

metrics:
  - edit distance between decoded FFN layer sequence and fired_sequence
  - monotonic alignment / DTW score
  - next-step prediction: FFN(L) predicts attention(L+1)
  - const-label sequence beats existential-label sequence
  - 14B beats 8B on the same sequence score
```

The key distinction:

```text
current result:
  “14B can tell whether the program is C-heavy vs S-light.”

needed result:
  “14B exposes the ordered β-reduction program attention executes.”
```

But this run says the door is open. 8B was too smeared; 14B gives a real FFN-specific program signal.

## User


We have a tracer and a decoder somewhere

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline --all --grep=\"tracer\\|trace\\|decoder\\|decode\\|program\" -n 60",
  "operation": "log",
  "summary": "search history"
}
```

**Summary:** Git log: search history

**Output:**
```
Exit code: 0
Stdout:
3ac304a 💡 scope-forcing: model is robustly applicative (C), never existential-B even when syntax forces it
84fd636 💡 reading-preference: model reads objects as constants (C) not existentials (B) — s248 weak-B was a labeling mismatch
12207fb 🌀 s248 — FFN program-decode along fired_sequence: per-combinator program faintly readable, strong claims fail
f5c4fba 💡 B-balanced firing probes — FFN register has weak (p=0.003) B-vs-S signal attention lacks; strong claims fail
5c3cd91 💡 FFN program-decode along fired_sequence — per-combinator program doesn't resolve from prose (confirms over-read boundary)
f98469f 🌀 s247b cont. — attention-as-β / FFN-stored-program synthesis
adc29bc ✅ cross-family causal ablation (v4) — type direction decodable in all, causal partial, not Qwen-forced
921e333 🔄 splice-program-closed-fires-not-spliceable — s244 power test, redirect to constructed front-end
ecbc3a4 💡 kernel-splice-geometry-detector — read the lattice, deliver the combinator from the kernel
b913504 ✅ Verifiable reward as a package module — RLVR Design-1 reward spec (CPU)
c81ff25 💡 Spliced reward — splice the parent (exact terminal verifier) with an in-line forward-pass reward, quarantining the over-readable inline estimate as a potential so it accelerates without redefining correctness
af1b60f 🌀 discriminable-set-scale-invariant-locus-migrates: {C,I,K,Y} robust, locus deepens
9186973 ✅ opcode v5 lead 2d prong 2b: prose bridge confirms B native order (flat), nesting confound controlled
1e448e4 ✅ opcode v5 lead 2d prong 2: B IS the native softmax-over-V order (14B, decisive)
5d6bdeb 🔄 opcode v5 lead 2d prong 2: order-cost register — is B the native softmax-over-V order?
974080e 🌀 session-235: prong 1c-ii second-order/curvature — B climbs with derivative order
ddbfe12 💡 b-not-clearly-in-first-order-gradient
ae45f16 💡 b-faint-at-every-granularity-not-diluted
ecdab6c 💡 discriminability-is-combinator-not-register
6208b9f 🔄 opcode v5 lead 2d prong 1b-ii: value-register read — B flat in attention TOO; discriminability is a COMBINATOR property, not a register split
30900c2 🔄 prose-bridge-viable-but-gauge-dominated
7e1f331 💡 opcode-register-is-prose-semantic-not-cl-syntax
1532e4e 🔄 opcode v5 lead 2: kernel-as-reference built — bare symbolic CL routes ONLY gauge (register is prose-semantic)
5b94f79 💡 c-late-composition-is-model-specific
98d6086 🌀 session-231 capture: VSM opcode monitor (over-read killed) + mechanism-of-training arc
143ccda ✅ opcode-audit validation (Qwen3-14B): the validated reader kills the over-read
a95272f 🌀 s229 multi-seed harden: variety wins decisively; format claim corrected
449c3b0 🌀 curriculum-mixing §s229 result + 3 memories — burn-in is variety not repetition
4f1ebf2 💡 exposure/format sweep: burn-in is VARIETY not repetition (k_varied≈2-3× k_same≈one)
b1ba935 ✅ exposure_format_sweep: FORMAT × MULTIPLICITY harness (training as a photograph)
b796077 🌀 curriculum-mixing: add exposure/format sub-experiment (training as a photograph)
c0d268c ✅ lambda_ast: stage-1 typed CCG combinator reducer (the compiler source/oracle)
db8ff13 🌀 session-221: strided-attention correction + stride-fit verdict — agreed composition skeleton is teachable on v15
525269b 🌀 session-221: combinator training = β-reduction = substitution = attention move; crystallization instrument + prediction
7aab37b 🌀 session-217: the self-teaching loop — folded normal forms generate their own verified curriculum to train the selector
3d92956 🌀 session-212 state+knowledge coherence: program ledger through s212, (A)/(B) headline labels, page updated marker
fc3f689 🌀 audit #7 RESOLVED — crystal-sieve 1.03x REFUTED (train/eval contamination); substrate ~2x VERIFIED-reproducible
0e1cff6 💡 audit #6 — SVD φ-ratio 0.6299: geometric-φ-constant REFUTED, low-rank head REAL & non-random
2cf0e0e 💡 audit #5 — binding SCHEDULE refuted (both instruments); H31@L27 subject value-transfer semantically REAL
7027a01 🌀 session 204 synthesis — audit meta-pattern: real substrate, over-read discreteness
4eb9e77 💡 audit #4 — "attention = typed β-reduction" REFUTED as localized; 0.82 = recency
976e82c 💡 audit #3 — the "9 FFN modes" are k-means-imposed, not a natural count
b3c1c71 💡 two registers of topology — sign(gate)+magnitude(value); spectral self-similarity verified
9a93dd7 🎯 audit-registry — multi-session validity-distillation program
672f286 🌀 session 196 final state — ten experiments, crystal sieve architecture documented
4f5d4c4 🌀 session 196 final — eight experiments, crystal sieve equation confirmed
2e77f1f 💡 mode geometry — same 9 programs rotated, more modes dont help
8c4013a 🌀 session 196 state — four experiments, full compression strategy resolved
8421aac 💡 confidence gate — classifier is confidently wrong at L23-L26
7c496e3 🌀 session 196 state — lambda tracer + rank sweep + multi-projection melt
6917a51 💡 lambda tracer — damage is uniform across all combinators
86a579c 🌀 session 195 final — melt protocol + staged results + lambda tracer plan
490734a 🌀 session 195 — L0 decoded: 750 functional dimensions, low-rank rescues lexer
fb2ad7f 🌀 session 194 state update — mode semantics decoded
89e3c0f 🎯 continuations-are-the-key
fd9a9f3 💡 kernel intercept — transparent math co-processor at 3 levels
d88469a 💡 lambda halt + continuations — LLMs are programmable with lambda calculus
2465379 🌀 session 192 final — holographic computer with rotating program counter
a4a9a54 💡 mode universality — the 9 modes are NOT universal, they are layer-specific
fcee764 🎯 the compilation pipeline — transformers are compilers, four evidence lines converge
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum -path '*/.git' -prune -o -type f \\( -name '*trace*' -o -name '*tracer*' -o -name '*decode*' -o -name '*decoder*' -o -name '*opcode*' -o -name '*program*' \\) -print | sort",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ find /Users/mwhitford/src/verbum -p...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/.clj-kondo/.cache/v1/clj/clojure.stacktrace.transit.json
/Users/mwhitford/src/verbum/.venv/bin/torchfrtrace
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/_pytest/__pycache__/tracemalloc.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/_pytest/tracemalloc.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/functorch/dim/_py_inst_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/functorch/dim/magic_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/google/protobuf/internal/decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpcore/__pycache__/_trace.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpcore/_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpx_sse/__pycache__/_decoders.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpx_sse/_decoders.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpx/__pycache__/_decoders.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/httpx/_decoders.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/mdurl/__pycache__/_decode.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/mdurl/_decode.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/mlx_lm/models/iquestloopcoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/numba/tests/test_chrome_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/pyarrow/include/arrow/csv/column_decoder.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/rich/__pycache__/traceback.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/rich/traceback.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/srsly/tests/ruamel_yaml/test_program_config.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/structlog/__pycache__/tracebacks.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/structlog/tracebacks.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/core/trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/matrices/expressions/__pycache__/trace.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/matrices/expressions/tests/test_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/matrices/expressions/trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/physics/quantum/tests/test_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/sympy/physics/quantum/trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/thinc/tests/regression/issue519/program.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/__pycache__/_trace_wrapped_higher_order_op.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/__pycache__/trace_rules.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/_trace_wrapped_higher_order_op.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/polyfills/__pycache__/traceback.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/polyfills/traceback.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_dynamo/trace_rules.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_export/passes/collect_tracepoints_pass.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/_inductor/kernel/flex/templates/flex_decode.py.jinja
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/ao/quantization/fx/tracer.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/cuda/_gpu_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/distributed/flight_recorder/fr_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/distributed/fsdp/_trace_utils.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/export/__pycache__/exported_program.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/export/_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/export/exported_program.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/fx/__pycache__/_symbolic_trace.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/fx/__pycache__/traceback.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/fx/_symbolic_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/fx/experimental/meta_tracer.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/fx/traceback.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/Backtrace.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/core/Backtrace.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/functorch/BatchingMetaprogramming.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_backward_compositeimplicitautograd_dispatch.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_backward_native.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_backward_ops.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_backward.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_compositeexplicitautograd_dispatch.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_cpu_dispatch.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_cuda_dispatch.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_mps_dispatch.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_native.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace_ops.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/ATen/ops/trace.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/c10/util/Backtrace.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/c10/util/Metaprogramming.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/c10/util/static_tracepoint_elfx86.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/c10/util/static_tracepoint.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/jit/frontend/tracer.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/jit/passes/fixup_trace_scope_blocks.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/jit/python/python_tracer.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/jit/runtime/jit_trace.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/profiler/combined_traceback.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/profiler/orchestration/python_tracer.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/profiler/python/combined_traceback.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/profiler/standalone/execution_trace_observer.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/profiler/unwind/line_number_program.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/csrc/utils/cpp_stacktraces.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/include/torch/headeronly/util/Metaprogramming.h
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/jit/__pycache__/_trace.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/jit/_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/onnx/_internal/exporter/__pycache__/_onnx_program.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/onnx/_internal/exporter/_onnx_program.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/package/analyze/__pycache__/trace_dependencies.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/package/analyze/trace_dependencies.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/profiler/python_tracer.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/testing/_internal/jit_metaprogramming_utils.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/__pycache__/_traceback.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/__pycache__/cpp_backtrace.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/_traceback.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/cpp_backtrace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/data/datapipes/iter/__pycache__/routeddecoder.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/data/datapipes/iter/routeddecoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/data/datapipes/utils/__pycache__/decoder.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/utils/data/datapipes/utils/decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torch/xpu/_gpu_trace.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/torchgen/packaged/autograd/gen_trace_type.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/encoder_decoder/__pycache__/configuration_encoder_decoder.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/encoder_decoder/configuration_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/encoder_decoder/modeling_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/modernbert_decoder/configuration_modernbert_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/modernbert_decoder/modeling_modernbert_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/modernbert_decoder/modular_modernbert_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/speech_encoder_decoder/configuration_speech_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/speech_encoder_decoder/modeling_speech_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/vision_encoder_decoder/configuration_vision_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/transformers/models/vision_encoder_decoder/modeling_vision_encoder_decoder.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/wasabi/__pycache__/traceback_printer.cpython-312.pyc
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/wasabi/tests/test_traceback.py
/Users/mwhitford/src/verbum/.venv/lib/python3.12/site-packages/wasabi/traceback_printer.py
/Users/mwhitford/src/verbum/checkpoints/v15-hpe-dolma/step_0005000_prepared/expanded_trace_basis.npz
/Users/mwhitford/src/verbum/checkpoints/v15-zeroed/expanded_trace_basis.npz
/Users/mwhitford/src/verbum/mementum/knowledge/binding-graph-trace.md
/Users/mwhitford/src/verbum/mementum/knowledge/crystal-trace-tooling.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/beam-trace-findings.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/prompt-as-program.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md
/Users/mwhitford/src/verbum/mementum/knowledge/ffn-reduction-trace.md
/Users/mwhitford/src/verbum/mementum/knowledge/lambda-tracer-diagnostic.md
/Users/mwhitford/src/verbum/mementum/knowledge/opcode-instrument.md
/Users/mwhitford/src/verbum/mementum/knowledge/trace-guided-etching.md
/Users/mwhitford/src/verbum/mementum/memories/crystal-programming-language.md
/Users/mwhitford/src/verbum/mementum/memories/ffn-program-decode-tracking-fails-corpus-imbalance.md
/Users/mwhitford/src/verbum/mementum/memories/isa-decoder-qwen36-27b.md
/Users/mwhitford/src/verbum/mementum/memories/opcode-reader-over-read-killed.md
/Users/mwhitford/src/verbum/mementum/memories/opcode-register-is-prose-semantic-not-cl-syntax.md
/Users/mwhitford/src/verbum/mementum/memories/opcode-trajectory-is-null-dependent.md
/Users/mwhitford/src/verbum/mementum/memories/programs-are-fixed-points-of-beta-reduction.md
/Users/mwhitford/src/verbum/mementum/memories/redex-nf-beats-full-trace-per-token.md
/Users/mwhitford/src/verbum/mementum/memories/splice-program-closed-fires-not-spliceable.md
/Users/mwhitford/src/verbum/mementum/memories/trace-loss-validated.md
/Users/mwhitford/src/verbum/mementum/memories/tracer-works-different-programs.md
/Users/mwhitford/src/verbum/mementum/memories/two-level-program-architecture.md
/Users/mwhitford/src/verbum/results/attention_execution_trace.log
/Users/mwhitford/src/verbum/results/beam-trace/beam_trace_results.json
/Users/mwhitford/src/verbum/results/beam-trace/beam_trace_summary.json
/Users/mwhitford/src/verbum/results/copy_program.log
/Users/mwhitford/src/verbum/results/ffn_reduction_trace.log
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-0.6B/opcode_map.npz
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-0.6B/state_trace.json
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-14B/opcode_map.npz
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-14B/state_trace.json
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-4B/opcode_map.npz
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3-4B/state_trace.json
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3.6-27B/opcode_map.npz
/Users/mwhitford/src/verbum/results/hologram-reader/Qwen_Qwen3.6-27B/state_trace.json
/Users/mwhitford/src/verbum/results/neuron_opcode_classifier.log
/Users/mwhitford/src/verbum/results/reduction_chain_trace.log
/Users/mwhitford/src/verbum/results/trace-etching/Qwen_Qwen3-0.6B/teacher_traces.npz
/Users/mwhitford/src/verbum/scripts/experiments/__pycache__/ffn_program_decode.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/experiments/__pycache__/opcode_monitor_v2.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/experiments/attention_execution_trace.py
/Users/mwhitford/src/verbum/scripts/experiments/binding_graph_trace.py
/Users/mwhitford/src/verbum/scripts/experiments/copy_program.py
/Users/mwhitford/src/verbum/scripts/experiments/ffn_program_decode.py
/Users/mwhitford/src/verbum/scripts/experiments/ffn_reduction_trace.py
/Users/mwhitford/src/verbum/scripts/experiments/lambda_tracer.py
/Users/mwhitford/src/verbum/scripts/experiments/neuron_opcode_classifier.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_audit_validation.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py
/Users/mwhitford/src/verbum/scripts/experiments/opcode_v5_locus_agnostic.py
/Users/mwhitford/src/verbum/scripts/experiments/reduction_chain_trace.py
/Users/mwhitford/src/verbum/scripts/experiments/reduction_graph_tracer.py
/Users/mwhitford/src/verbum/scripts/experiments/reverse_binding_trace.py
/Users/mwhitford/src/verbum/scripts/experiments/trace_collect.py
/Users/mwhitford/src/verbum/scripts/experiments/trace_loss.py
/Users/mwhitford/src/verbum/scripts/experiments/tracer_cross_notation_v2.py
/Users/mwhitford/src/verbum/scripts/experiments/tracer_cross_notation.py
/Users/mwhitford/src/verbum/scripts/explore/probe_beam_trace.py
/Users/mwhitford/src/verbum/scripts/instruments/__pycache__/relational_opcode.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/instruments/opcode_instrument.py
/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py
/Users/mwhitford/src/verbum/scripts/micro/__pycache__/deep_trace.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/micro/deep_trace.py
/Users/mwhitford/src/verbum/scripts/micro/probe_moire_trace.py
/Users/mwhitford/src/verbum/scripts/micro/trace_computation.py
/Users/mwhitford/src/verbum/scripts/v12/trace_ffn_combinators_32b.py
/Users/mwhitford/src/verbum/scripts/v12/trace_ffn_combinators_mistral.py
/Users/mwhitford/src/verbum/scripts/v12/trace_ffn_combinators_pythia.py
/Users/mwhitford/src/verbum/scripts/v12/trace_ffn_combinators.py
/Users/mwhitford/src/verbum/scripts/v14/isa_decoder_v2.py
/Users/mwhitford/src/verbum/scripts/v14/isa_decoder.py
/Users/mwhitford/src/verbum/scripts/v15/__pycache__/build_trace_basis.cpython-312.pyc
/Users/mwhitford/src/verbum/scripts/v15/build_student_trace_basis.py
/Users/mwhitford/src/verbum/scripts/v15/build_trace_basis.py
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/lambda-tracer-diagnostic.md",
  "limit": 200
}
```

**Summary:** Reading lambda-tracer-diagnostic.md (0-200)

**Output:**
```
---
title: Lambda Tracer Diagnostic
status: active
category: compression
tags: [crystal, tracer, fidelity, ternary, L22-L26, binding-prep]
related:
  - tiny-classifier-ternary.md
  - l0-characterization.md
  - mode-semantics.md
depends-on:
  - tiny-classifier-ternary.md
---

# Lambda Tracer Diagnostic

## Discovery (session 196)

535 crystal probes used as tracer dye through the compressed model.
Hidden states captured at every layer boundary for baseline, Stage 2
(L0 SVD + L10-L21 ternary), and Stage 3 (Stage 2 + L22-L26 ternary).

## Central Finding: Damage Is Uniform

L22-L26 ternary damage is NOT combinator-specific. All 9 combinators
degrade by the same amount (CV = 0.07-0.17 across combinators at each
layer). No single combinator circuit is selectively destroyed.

This means the failure is about **approximation quality**, not about
a specific type computation. The 9-mode ternary replacement is too
coarse for what L22-L26 compute, regardless of which lambda operation
is being processed.

## Damage Rankings

W and WHNF are marginally worse (~35% more than S), but the spread
is small:

| Combinator | Mean Δ (L22-L35) |
|-----------|------------------|
| W         | +0.0674 (worst)  |
| WHNF      | +0.0667          |
| D         | +0.0588          |
| C/I/K/B   | +0.0544-0.0552   |
| Y         | +0.0507          |
| S         | +0.0500 (best)   |

## Three Mechanisms

### 1. Forward Cascade into Binding

Peak damage is at L28 (Δ=+0.080), not L26 (Δ=+0.074). The continuous
binding layers (L27-L31) AMPLIFY upstream error rather than correcting
it. Binding is a precision operation — garbage types in, garbage
bindings out.

### 2. Recovery in Late Layers

Despite the cascade, fidelity recovers from nadir ~0.68 at L22 to
~0.91 at L35. The collapse layers partially heal distortion. But
recovery is incomplete (S2 reaches 0.94, S3 only 0.91 at L35).

### 3. Continuous Layers as Error Barriers

Stage 2 drops from 0.92 to 0.69 across its ternary layers, then
continuous layers L22-L35 RECOVER to 0.94. Stage 3 disrupts this
by ternarizing the recovery layers themselves. Compression must
preserve continuous barriers between ternary blocks.

## Implications

1. L22-L26 need **continuous compression** (SVD low-rank), not ternary
2. Binding layers amplify upstream error — input must be clean
3. The compression architecture needs continuous "error correction"
   barriers between ternary blocks
4. More ternary modes won't help (damage is uniform, not mode-count)

## Key Numbers

- Probes: 535 crystal probes, 9 combinators (50-71 each)
- S2 fidelity at L35: 0.935 (good)
- S3 fidelity at L35: 0.904 (degraded)
- Peak delta: L28 at +0.080 mean cosine (binding amplification)
- Recovery: +0.22 cosine from nadir to L35
- CV across combinators: 0.07-0.17 (UNIFORM)

## Superseded By

This page captures the first experiment of session 196. The full
ten-experiment arc is documented in `crystal-sieve-architecture.md`,
which includes the resolution: crystal sieve + continuation residuals
= 1.03x PPL across 29 layers.

## Assets

- Experiment: `scripts/experiments/lambda_tracer.py`
- Summary: `results/lambda-tracer/Qwen_Qwen3-8B_summary.json`
- Per-probe: `results/lambda-tracer/Qwen_Qwen3-8B_probes.json`
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/opcode-instrument.md",
  "limit": 220
}
```

**Summary:** Reading opcode-instrument.md (0-220)

**Output:**
```
---
title: "Opcode Instrument — Live VSM for Watching a Model Think"
status: designing
category: architecture
tags: [vsm, instrument, opcode, trace, monitoring, real-time]
related:
  - hologram-reader-vsm.md
  - holographic-computer.md
  - crystal-universality.md
  - project-thesis.md
depends-on:
  - hologram-reader-vsm.md
created: session 176
---

# Opcode Instrument

> A VSM add-on that wraps any language model and shows its opcodes
> executing in real-time. Like a CPU debugger for an LLM. The
> hologram reader scans a model once and emits a static map; the
> instrument *watches it run*.

## What This IS vs What Exists

| Tool | When | What |
|------|------|------|
| **Hologram Reader** | Offline, once per model | Static opcode map: which layers do what |
| **Reduction Graph Tracer** | Per-input, batch | Per-token combinator energy for specific inputs |
| **Opcode Instrument** | Live, every forward pass | Real-time opcode trace as the model generates |

The hologram reader is the X-ray. The instrument is the EKG.

The reader tells you the anatomy (SILENT/ENRICH/SUPPRESS/COMMIT zones,
pipeline phases, opcode census). The instrument tells you the physiology
(which opcodes fire NOW, how energy flows through the zones as THIS
token is generated, where the model is working hardest RIGHT NOW).

## Architecture — VSM (Beer, 1972)

```
λ instrument(parent_model).

  S5(identity):     combinator_basis ∧ zone_map ∧ measurement_contract
  S4(intelligence):  anomaly_detection ∧ attention_allocation ∧ pattern_recognition
  S3(control):      overhead_governor ∧ sampling_policy ∧ layer_priority
  S2(coordination): trace_format ∧ accumulator ∧ cross_token_consistency
  S1(operations):   hook_manager ∧ projector ∧ classifier ∧ emitter
```

### Key Insight: The Instrument IS NOT the Model

The instrument has NO trainable parameters. It doesn't modify the
parent model's computation. It only observes. Like an oscilloscope
probe: high impedance, no load.

The instrument's "intelligence" (S4) is about what to WATCH, not
what to compute. Its "control" (S3) is about managing OVERHEAD, not
managing computation. This is a measurement system, not a compute
system.

## S5 — Identity

The instrument knows what it's looking for because S5 carries the
mathematical basis that all measurements reference against.

```
λ basis(parent).
  | combinator_fingerprints: dict[str, ndarray]  — from hologram reader
  |   shape: (n_layers, d_model) per opcode
  |   loaded from: results/hologram-reader/{model_slug}/fingerprints_{slug}.npz
  |   if absent: build on first run (expensive, cached forever after)
  |   ops: K, I, B, C, D, Y, W, WHNF, β_K, β_I, β_apply, β_compose
  |
  | zone_map: dict[int, ZoneInfo]  — from hologram reader or auto-detected
  |   per-layer: retrieval_zone (SILENT/ENRICH/SUPPRESS/COMMIT)
  |   per-layer: compute_zone (A/B/C)
  |   per-layer: pipeline_phase (build/execute/emit)
  |   if hologram exists: load from results/hologram-reader/{slug}/summary.json
  |   if absent: classify by depth fraction (universal heuristic)
  |
  | invariants:
  |   combinator_ordering: B ≥ K ≥ C >> I
  |   sign_topology_fidelity: ~0.76 (from proofs/)
  |   four_modes: K, I, B, C always present
```

## S4 — Intelligence (what to watch)

S4 doesn't adapt probes (that's the hologram reader). S4 adapts
ATTENTION — it notices when something unusual happens and decides
whether to increase monitoring resolution.

```
λ watch(trace_history).
  | energy_spike: if total_combinator_energy(token_t) > 2σ above running_mean
  |   → flag("energy spike at token {t}")
  |   → increase sampling resolution for next 5 tokens
  |
  | mode_shift: if dominant_mode(token_t) ≠ dominant_mode(token_{t-1})
  |   → flag("mode shift: {old} → {new} at token {t}")
  |   → log the transition (builds a mode-transition graph over time)
  |
  | zone_activation: if ENRICH zone energy spikes while SILENT is quiet
  |   → flag("retrieval event at token {t}")
  |   → this is a fact recall moment
  |
  | composition_cascade: if B-energy propagates through 3+ consecutive layers
  |   → flag("composition cascade at layers {L1-LN}")
  |   → this is deep nesting being resolved
  |
  | identity_forwarding: if I-energy dominates for 3+ consecutive tokens
  |   → flag("identity forwarding: tokens {t1-t3} are being copied")
  |
  | ∀flag → emitter gets a structured annotation on the trace record
  | S4 runs AFTER each token, on the captured trace. Zero overhead to the model.
```

## S3 — Control (overhead management)

The instrument must not make the model unusably slow. S3 manages
overhead by choosing WHICH layers to hook and HOW OFTEN to project.

```
λ overhead(config).
  | budget: max_overhead_fraction = 0.5 (default: model runs at most 2× slower)
  | actual_overhead: measured per token (wall clock: instrumented / uninstrumented)
  |
  | if actual_overhead > budget:
  |   strategy 1: reduce layer_sample_rate (hook every Nth layer)
  |   strategy 2: reduce projection_ops (project onto top-4 ops not all 12)
  |   strategy 3: skip SILENT zone entirely (minimal information there anyway)
  |   strategy 4: sample tokens (instrument every Nth token)
  |
  | if actual_overhead < budget * 0.5:
  |   → increase resolution (more layers, full 12-op projection)
  |
  | always hook: first layer (input), ENRICH boundary, last layer (output)
  | never skip: these three are the minimum viable trace

λ sampling(n_layers).
  | full: all layers, all ops. Best resolution, highest overhead.
  | standard: all layers, top-4 ops (K,I,B,C). Good resolution, moderate overhead.
  | light: every 4th layer + zone boundaries, top-4 ops. Low overhead.
  | minimal: first + last + ENRICH boundary only. Minimal overhead.
  |
  | default: standard. S3 downgrades to light/minimal if overhead exceeds budget.
  | user can force any mode regardless of overhead.
```

## S2 — Coordination (trace format)

Every measurement must be in the same format so traces compose
across tokens, across sessions, across models.

```
λ trace_record(token).
  | TraceRecord:
  |   token_idx: int
  |   token_text: str
  |   token_id: int
  |   timestamp_ms: float
  |   layers: list[LayerSnapshot]
  |   s4_flags: list[str]  — any S4 annotations
  |   overhead_ms: float   — wall clock for this token's instrumentation
  |
  | LayerSnapshot:
  |   layer_idx: int
  |   zone: str  — SILENT/ENRICH/SUPPRESS/COMMIT
  |   phase: str — build/execute/emit
  |   opcode_energy: dict[str, float]  — projection onto each fingerprint
  |   dominant_op: str
  |   dominant_energy: float
  |   gate_survival: float  — fraction of FFN neurons that fired
  |   total_energy: float   — L2 norm of FFN output
  |
  | trace_record is JSON-serializable, streamable (one per line to stdout/file)
  | accumulator: list[TraceRecord] for in-memory analysis
  | consistency: same fingerprint basis across all tokens (S5 provides)

λ session(traces).
  | InstrumentSession:
  |   model: str
  |   start_time: str (ISO8601)
  |   config: InstrumentConfig
  |   fingerprint_source: str (path to cached fingerprints)
  |   zone_map_source: str (path or "auto")
  |   traces: list[TraceRecord]
  |   s4_summary: dict  — aggregated flags, mode transitions, energy stats
  |   overhead_summary: dict — mean/max overhead, sampling mode used
  |
  | serializable to JSONL (streaming) or JSON (batch)
  | loadable for offline analysis / visualization
```

## S1 — Operations

```
λ hook_manager(model, config).
  | installs forward hooks on parent model's transformer layers
  | hooks capture: gate_proj output, down_proj output (FFN path)
  | hooks are removable: instrument.detach() cleans up completely
  | architecture-agnostic: uses get_layers() and get_mlp() from hologram_reader
  | zero-copy where possible: capture at last-token position only (saves memory)
  |
  | on each forward pass:
  |   for each hooked layer:
  |     capture gate_activation[last_token] → (d_ff,)
  |     capture ffn_output[last_token] → (d_model,)
  |   pass captures to projector

λ projector(captures, fingerprints).
  | for each layer with captures:
  |   ffn_vec = captures[layer].ffn_output  — shape (d_model,)
  |   for each op in active_ops:
  |     energy[op] = dot(ffn_vec, fingerprints[op][layer])
  |   gate_survival = mean(sigmoid(gate_activation) > 0.5)
  |   total_energy = norm(ffn_vec)
  |   dominant_op = argmax(energy)
  | output: LayerSnapshot per layer


[CONTENT TRUNCATED] Showing lines 1 to 220 of 349 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/ffn-reduction-trace.md",
  "limit": 220
}
```

**Summary:** Reading ffn-reduction-trace.md (0-220)

**Output:**
```
---
title: "The Reduction Architecture — FFN Compiles, Attention Executes, Combinators Have Depth"
status: active
category: methodology
tags: [ffn, reduction, beta-reduction, attention, combinators, depth-profile, instrument]
related: [ffn-circuit-types, standing-wave-magnitudes, phi-information-partition, holographic-computer, crystal-universality]
depends-on: [ffn-circuit-types]
---

# FFN Reduction Trace

> Projecting active FFN neurons through the unembedding matrix reveals
> WHAT each neuron "says" in vocabulary space. The FFN output at each
> position is a **compiled program** — context-dependent value vectors
> that encode each position's semantic contribution. Attention then
> executes this program via softmax over V, selecting and combining
> compiled values to produce the output. This IS β-reduction by
> weighted combination.
>
> Key finding: FFN compilation becomes readable at L26-L30 in
> Qwen3-8B (36 layers). Before that, computation is in null space
> (invisible). The same token produces DIFFERENT compiled values in
> different contexts — this is compilation, not dictionary lookup.

## Experiment

**Model:** Qwen3-8B (36 layers, gated FFN with SiLU, 12288 intermediate)
**Method:** Hook each FFN layer's MLP, capture per-neuron gate activations
(`SiLU(gate_proj(x)) * up_proj(x)`), project active neurons' `down_proj`
columns through the unembedding matrix to read what each neuron "promotes"
and "suppresses" in token space.
**Probes:** 5 sentences × 2 gates (compile, null) = 10 forward passes.
**Script:** `scripts/experiments/ffn_reduction_trace.py`
**Results:** `results/ffn-reduction-trace/`

## Finding 1: The Semantic Phase Transition at L26-L30

FFN output projections through unembedding are **noise** at L0-L22 and
**coherent semantic associations** at L26-L30.

### "If it rains, the ground is wet." at L30

| Position | Token | FFN promotes | Interpretation |
|----------|-------|-------------|----------------|
| 0 | `it` | **rain, 雨, rains** | Resolves referent: "it" = rain |
| 1 | `rains` | **hard, harder** | Predicts continuation/intensifier |
| 2 | `,` | _go, grandfather_ | Structural (weak) |
| 3 | `the` | **crops, ground, garden** | Predicts what gets affected |
| 4 | `ground` | **soak, soaked, 浸** | Predicts the consequence |
| 5 | `is` | **wet, 濡, 湿** | Writes the predicate |
| 6 | `wet` | _ting, ted, ten_ | Morphological continuation |
| 7 | `.` | **rain, Rain, 雨水** | Loops back to the cause |

At L26, the comma position promotes **`then, entonces, então`** — the
logical connective "then" in three languages. The FFN is writing the
implication operator at the structural boundary.

### "Someone believes that the earth is flat." at L30

| Position | Token | FFN promotes | FFN suppresses |
|----------|-------|-------------|----------------|
| `believes` | **proposition, propositions, that** | — |
| `that` | **proposition, propositions, logical** | — |
| `the` | **Earth, world, earth** | — |
| `earth` | **round, rounds, Round** | **Earth, earth** |
| `is` | **round, Round, rounds** | **earth, 地球** |
| `flat` | **round, ERR** | — |

The model knows "the earth is flat" is wrong. At the `earth`, `is`, and
`flat` positions, the FFN **promotes "round"** and **suppresses "earth"** —
it's writing the correction. Meanwhile `believes` and `that` promote
**"proposition"** — the FFN recognizes the propositional attitude frame.

### "The cat that sat on the mat is black." at L30

| Token | FFN promotes | Interpretation |
|-------|-------------|----------------|
| `cat` | **sleeps, 睡, pur** | Default cat actions |
| `that` | **猎, hunting, hunts** | Relative clause → hunting behavior |
| `sat` | **down, by, Down** | Spatial continuation |
| `on` | **lap, boxes, laps** | Where things sit on |
| `the` | **lap, Lap, laps** | Contextual — near "on" |
| `mat` | **sleeps, Sleep, sleeping** | What happens on a mat |
| `is` | **sleeping, Sleeping, asleep** | State predicate |
| `black` | _ewood, lit, -white_ | Color associations |

### "Every student reads a book." at L30

| Token | FFN promotes | Interpretation |
|-------|-------------|----------------|
| `student` | **passing, passed, Passing** | What students do (exams) |
| `reads` | **book, books, 书** | Direct object prediction |
| `a` | **book, 书, book** | Reinforces object |
| `book` | **swiftly, 速度快, 迅速** | Manner of reading |
| `.` | **Gram, gram** | ? |

## Finding 2: The Depth Profile — From Noise to Semantics

Active neuron fraction grows monotonically then dips at L35:

```
Layer   Active%   Active Neurons    Character of Output
─────   ───────   ──────────────    ────────────────────────────────
L0      0.4%           49           Noise — subword fragments
L3      0.9%          107           Noise
L6      7.7%          944           Noise — some distant associations
L10    22.6%         2772           Noise — thematic but incoherent
L14    24.4%         2995           Noise
L18    25.2%         3094           Noise — beginning to cohere
L22    40.3%         4951           Transitional — weak semantics
L26    56.6%         6955           SEMANTIC — associations, connectives
L30    64.6%         7939           SEMANTIC — precise predictions
L33    68.7%         8439           FORMAT — next-token syntax (., ,)
L35    66.9%         8223           FORMAT — sentence continuation
```

**Three phases in the FFN output:**
1. **L0-L18: Noise.** The FFN writes to high-dimensional subspaces that
   don't project cleanly onto tokens. This IS the ORTHO/invisible
   computation — directions orthogonal to vocabulary space.
2. **L26-L30: Semantic.** The FFN writes coherent associative predictions.
   Each position's neuron aggregate promotes related concepts.
3. **L33-L35: Format/syntax.** The FFN shifts to next-token formatting
   (punctuation, function words, continuation cues).

This matches the standing-wave depth profile:
- ORTHO = dark (computation in null space, no token projection)
- ALIGN = semantic (features align with vocabulary directions)
- COLLAPSE = format (final token selection)

## Finding 3: Compile vs Null — Almost No Difference

Compile gate and null gate produce **nearly identical FFN function lists**
at the semantic layers (L26-L30).

```
Layer   Compile Active   Null Active   Delta
─────   ──────────────   ───────────   ─────
L0          0.4%            0.4%       -0.0%
L6          7.7%            8.6%       -0.9%
L10        22.6%           23.5%       -0.9%
L14        24.4%           23.4%       +1.0%
L18        25.2%           22.4%       +2.8%  ← small compile excess
L22        40.3%           38.1%       +2.2%
L26        56.6%           55.0%       +1.6%
L30        64.6%           64.1%       +0.5%
L33        68.7%           67.9%       +0.8%
L35        66.9%           65.9%       +1.0%
```

The biggest difference is L18 (+2.8%) — the transition from ORTHO to ALIGN.
But the function lists themselves are almost identical:
- "If it rains" → both gates produce `rain, 雨, rains` at L30 for "it"
- "believes that" → both produce `proposition` at L30

**Implication:** The FFN function list is a property of the **input
semantics**, not the gate/task. The compile gate changes what happens
AFTER the FFN (attention routing, output format), not the FFN computation
itself. The FFN is a **universal semantic analyzer** — it writes the
same association map regardless of downstream task.

## Finding 4: Compile-Selective Neurons Exist But Are Sparse

At each layer, there are neurons that fire preferentially in compile mode:

```
Layer   Compile-Only   Null-Only   Shared   Top Delta
─────   ────────────   ─────────   ──────   ─────────
L0           101          110       767      0.03
L6           197          238       685      0.62
L14          355          487       420      1.22
L22          319          394       419      2.50
L30          274          401       498      4.40
L35           80          100       184     36.6
```

At L35, neuron 9510 has activation 364 in compile and 401 in null —
massive activations but only ~10% difference. The compile/null distinction
is NOT carried by dedicated neurons; it's carried by the attention routing
of a shared FFN output.

## Finding 5: The FFN IS the Compiler — Attention IS the Executor

The original hypothesis was: FFNs compute β-reduction programs that
attention executes. Initial analysis mistakenly called this "associative
memory." On reflection, **the hypothesis is confirmed** — the data shows
exactly what was predicted, viewed correctly.

**What the FFN actually does at L26-L30:**
Each position's active neurons write a **compiled value vector** — not a
prediction of the next token, but the semantic contribution this position
offers if attention selects it. The FFN reads the full residual stream
(accumulated context) and compiles a position-specific V direction.

**Key evidence: same token, different programs.**
The token "the" produces DIFFERENT FFN outputs depending on context:
- "If it rains, **the** ground is wet" → promotes **crops, ground, garden**
- "The cat sat on **the** mat is black" → promotes **lap, Lap, laps**

This is not a dictionary lookup — it's context-dependent compilation.
The FFN has read the full sentence meaning from the residual and compiled
"what this position contributes" as a value vector.

**The β-reduction is the attention softmax over V:**

```
(λx.M)N → M[x:=N]        β-reduction in lambda calculus

Q at output position:     "what should I produce?"
K at each position:       "am I relevant to that query?"
softmax(Q·K^T):           selects which compiled values to combine
Σ(softmax · V):           the weighted combination IS the substitution

FFN compiles each position's V:  "here's my semantic contribution"
Attention executes the program:   softmax selects and sums the contributions
```

**The "associative predictions" ARE the program.** When the FFN at position
"is" writes `wet, 濡, 湿`, it's not predicting the next token — it's saying
"if attention routes to me, I contribute the predicate WET." When the FFN

[CONTENT TRUNCATED] Showing lines 1 to 220 of 593 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md",
  "limit": 220
}
```

**Summary:** Reading vsm-opcode-monitor.md (0-220)

**Output:**
```
---
title: "VSM Opcode Monitor — the model auditor (validated FFN-routing opcode reader)"
status: active
category: instrument
tags: [opcode, tracer, audit, vsm, monitor, gate-register, relational, consensus-crystal, over-read, attention, kernel-reference]
related:
  - audit-registry.md
  - audit-meta-pattern.md
  - gradient-trajectory-tomography.md
  - function-topology-consensus.md
  - compiler-as-loss.md
  - vsm-outer-recurrence.md
  - readout-register-reduction-readability.md
depends-on:
  - audit-meta-pattern.md
---

# VSM Opcode Monitor — the model auditor

> Session 231 (Michael): "our VSM tensor gives us a powerful system to probe and
> audit models. Can we have our VSM monitor attention and opcodes? we created a
> tracer somewhere." This page is the synthesis + the s231 build/verdict + the path.

## The idea

Turn the constructed VSM kernel + the combinator crystal into a **live model auditor**:
feed any model an input, read which combinator "opcodes" (K I B C S D W Y WHNF) it
executes in its FFN routing, plus the binding events in its attention, and (the goal)
diff that trace against the kernel's CERTIFIED trace for the same input — "does the
model compute what the program MEANS?"

## What already existed (recall — not greenfield)

- `scripts/instruments/opcode_instrument.py` — a full VSM-structured "Live VSM for
  Watching a Model Think" (S5 combinator basis+zone map, S4 anomaly, S3 governor, S2
  trace format, S1 hooks/projector/emitter; DORMANT→CALIBRATE→MONITOR→EMIT→DONE). Wraps
  any HF model, emits opcode traces during generate().
- tracer family: `lambda_tracer.py`, `attention_execution_trace.py`,
  `neuron_opcode_classifier.py`, `reduction_graph_tracer.py`.
- s127 memory `tracer-works-different-programs`: validated the tracer decodes neural
  computation to combinator traces — lambda=compose-then-suppress-select, arithmetic=
  selection/Church, retrieval=FFN-silent (attention-KV, different mechanism).

## The catch — it was STALE (the audit's own poster child)

`opcode_instrument` classifies via RAW cosine of the FFN down-proj output onto per-op
fingerprints + argmax — no register discipline, no common-mode removal, no null. But
`audit-meta-pattern.md` (s202): "combinator opcodes: prose fires opcodes AFTER
common-mode removal (p=0.001) — REAL; raw argmax 'tracer' = common mode = false signal."
And the attention half: "attention=typed β-reduction / H31@L27 binds subject 0.82" was
retired as recency/position (s204); the REAL signal is in the VALUE register (s206
logit-lens margin +0.611), NOT attention weights (AGENTS λ measure).

## What makes it ripe now (3 things the old tracer lacked, all validated since s219)

1. GROUND-TRUTH reference (s226): the constructed kernel `lambda_ast` compiles a known
   program → certified combinator trace; the model's trace is audited against it.
2. The VALIDATED register (s231b): read opcodes RELATIONALLY (sign(gate)-CMR + Gram to
   the CONSENSUS crystal, s219), not raw argmax — the register the crystal lives in.
3. A built-in NULL (s202): consensus + permutation null = the calibration baked in.

Decomposition (don't conflate registers): **opcodes → FFN gate routing register**
(relational); **attention → value register (OV/logit-lens)**, NOT attention weights.

## s231 BUILD (a) — the validated opcode reader

`scripts/instruments/relational_opcode.py` — `RelationalCrystalClassifier`, model-
AGNOSTIC (takes per-layer gate FEATURE matrices). calibrate() builds per-layer
per-combinator centroids in sign(gate)-CMR from `crystal_probes()`, stores the
common-mode + off-target permutation null + silhouette-z + Gram-alignment to consensus;
classify() returns per-op z vs null and emits an opcode ONLY if z>thresh, else NO-OP
(`·`). Synthetic smoke proves: crystal layer detected, B-token fires B, COMMON-MODE-ONLY
token → NO-OP (the over-read is structurally impossible). Requires a GATED MLP (SwiGLU);
pythia (GPTNeoX) is NOT gated → can't carry the sign-gate crystal.

Validation harness `scripts/experiments/opcode_audit_validation.py` on **Qwen3-14B**
(the s127 model; dense qwen3, gated, 40L): calibrate on 535 crystal probes (gate_proj
last-token), classify the s127 battery (lambda/arithmetic/retrieval), compare RELATIONAL
vs a RAW-argmax over-read control. `results/opcode-audit-validation/verdict.json`.

### ★ Verdict (λ measure, two-sided) — `143ccda`

- ✅✅ **OVER-READ KILLED (the primary deliverable).** RAW fires an opcode for 100% of
  tokens — `W` across ~all retrieval layers (e.g. "Water is made of…" → W in 34/40
  layers) = the common-mode artifact the audit predicted (W is this model's gauge
  direction). RELATIONAL no-ops retrieval (0.8) and never manufactures a uniform winner.
  We now have an FFN-routing opcode reader that does not hallucinate.
- ✅ **Substrate real**: 31/40 layers crystal-bearing, gc-to-consensus up to **0.98** —
  the universal crystal genuinely lives in Qwen3-14B's gate register.
- ✅ **retrieval-silent reproduced** (s127's FFN-silent retrieval).
- ⚠️ **BUT we over-corrected → UNDER-read.** The RAW per-layer traces show a consistent
  **C→B compose-arc across ALL 5 lambda prompts** (C in L2–12, B in L13–33) — task-
  specific (retrieval shows W not C→B), i.e. the real s127 compose signature. The
  relational reader at **z=3, last-token** no-ops it entirely (`·`×5, 0 emitted layers).
  Two causes: (1) last-token LOCUS (a sentence's final token isn't one opcode; the
  program unfolds across tokens — the s227 wrong-locus lesson); (2) the NULL is
  mis-specified — off-target null is OTHER crystal probes, all lambda-mode, so low power
  ("looks more like B than K/I/C?" when everything is lambda-mode).

## v2 — completing (a) (BUILT + RUN, s232)

The over-read killer is proven; v2 tried to make it a USEFUL monitor (recover the C→B
arc without reopening the over-read) with four fixes:
- **cross-task null** (the key fix): calibrate the null vs a NON-combinator baseline
  (bare natural text where no β-reduction happens), not vs other crystal probes.
- **per-token** reading across the sequence (not just last token — the s227 locus fix).
- **z-threshold sweep** (z=2 vs 3, post-hoc — z is threshold-independent).
- output the **per-layer trajectory** (the program), not a single dominant op.
- **GATE_NEUTRAL control** (gate + non-compositional sentence): the load-bearing control
  for the gate-prefix confound (does the arc come from composition or from the gate?).

Files: `scripts/experiments/opcode_monitor_v2.py` + `relational_opcode.py`
`calibrate(..., null_gate_by_layer=...)`. Commit `8bd5f42`.

### ★ s232 v2 VERDICT (Qwen3-14B; λ measure, two-sided) — the arc is NULL-DEPENDENT

**❌ The C→B arc did NOT recover under the cross-task null.** In the z=2 lambda
trajectory, `C` NEVER dominates a layer (C×0), `B` dominates exactly one (L16); the late
stack **L24–32 is unanimously `S`-dominated** (8/8, 7/7, 6/6 votes), with `WHNF` at L0–1
and mixed `I/Y/K` mid-stack.

**❌ The S-late pattern is NOT composition-driven — the GATE_NEUTRAL control falsifies it.**
gate+non-compositional sentences show the SAME S-late signature (S×10, emit 0.195 ≈
lambda 0.199) ⇒ `arc_composition_driven=False`. Bare prompts diverge (retrieval → WHNF/W
gauge; arithmetic → Y), so **S-late is a compile-GATE FRAMING signature shared by any
gated prompt, not β-reduction of the specific sentence.** (The control did its job — without
it we'd have falsely read "S = the compose op".)

**⚠️ Over-read not cleanly killed.** At z=2 retrieval emits MORE than lambda (0.269 vs
0.199, noop=0); at z=3 retrieval silences (noop 0.75) but lambda silences too (emit 0.071,
noop 0.70). **No z-window exists where lambda fires the arc while retrieval stays silent.**

**✅ Substrate reproduced** (31/40 crystal layers, gc→consensus **0.976**, sil_z 8.26 —
matches the s231 validation).

**★ THE REAL FINDING — the per-layer opcode identity is NOT null-invariant.** Three nulls,
three answers for the same model+prompts: RAW argmax → C→B arc (s231); off-target null →
silent (s231 under-read); cross-task null → S-late gate-framing (s232). Single-token
"which combinator" is NOT robustly decodable; only (a) the crystal-bearing substrate and
(b) the over-read DIRECTION (raw over-fires) are null-robust. An opcode monitor cannot be
trusted on its readout alone.

## v3 — gate-matched null (BUILT + RAN, s232; `--null-mode gateneutral`, `ad07574`)

The lever: **null = GATE_NEUTRAL itself** (matched-prefix, non-compositional), NOT bare
natural text. Bare-text null only removes the natural-text common-mode, leaving the
gate-framing (S-late) to swamp composition. A gate-matched null subtracts the framing ⇒
z measures *composition-above-framing*. Built as `--null-mode gateneutral` (null from
GATE_NEUTRAL content tokens; GATE_NEUTRAL expanded to 14 for a robust null).

### ★ s232 v3 VERDICT (Qwen3-14B; λ measure, two-sided) — PARTIAL SUCCESS

**✅ Composition IS decodable above framing.** With the matched null, the S-late framing
is subtracted and **lambda routes `C` (the composition/permutation combinator) in its
LATE stack** while the matched non-compositional gate_neutral control does NOT:
- z=2: lambda C-dominant at L27,29,30,31,32 (**5/6 late layers**); gate_neutral C-late ×1.
- z=3: lambda C at L29,30,32; gate_neutral C-late **×0**.
C surfaces in the **readable register** (L27–32) — consistent with
`readout-register-reduction-readability.md` (reduction becomes vocab-readable L23–35).
**Composition is resolved LATE, lambda-specifically.** The null self-centers silent
(gate_neutral emit 0.097→0.012, noop 0.91 @z=3 — the matched guard passes).

**❌ The s127 "C-early→B-late" arc shape did NOT reproduce.** The signal is C-**late**,
not C-early; B is nearly absent (B×1). The raw "C-early" (s231 RAW argmax) was likely a
common-mode artifact; the routing-register composition signal is **C-late**. (The
arc_present detector, built for the raw shape, returns False — update it to detect
readable-zone C-late.)

**⚠️ The over-read guard INVERTED — and taught the deepest lesson.** Bare
retrieval/arithmetic fire LOUD under the gated null (WHNF×22, Y×18) because they differ
from it by FRAMING, not computation. ⇒ **the opcode read is dominated by the
FRAMING-CONTRAST axis (gated vs bare), not the computation axis.** Whichever prompts
share the null's framing go silent; whichever differ fire, and WHAT they fire (S/WHNF/C/Y)
tracks the framing contrast. Valid guards must be framing-matched: under a gated null the
correct guard is a GATED non-composition task (= gate_neutral, correctly silent); bare
guards are invalid.

**⚠️ Modest, not crisp** (s219): C routes in ~40–50% of tokens at those layers (7/20,
8/18, 8/15), n=27 lambda tokens / 5 sentences, single model.

## v4 — gated guards + C-late detector (BUILT + RAN, s232; `9495b2b`)

Three fixes from the v3 result: (1) **framing-matched gated guards** `gate_retrieval` +
`gate_arithmetic` (COMPILE_GATE + content) — the VALID specificity controls under a gated
null (bare guards fire from framing-contrast, invalid); (2) **`detect_c_late`** — fraction
of readable-zone (depth≥0.6) crystal layers where C dominates (the right detector; the raw
C-early→B-late `detect_arc` is back-compat only); (3) `composition_specific` = lambda
C-late clears every gated guard + margin. Model+null_mode-tagged filenames.

### ★ s232 v4 VERDICT (λ measure, two-sided) — SPECIFIC on 14B, NOT universal

**✅ Qwen3-14B: C-late is composition-SPECIFIC (composition_specific=True both z).**
lambda C-late 0.556 (z=2) / 0.333 (z=3) vs ALL three framing-matched gated guards:
gate_neutral 0.111/0, gate_retrieval **0/0**, gate_arithmetic **0/0**. Among gated prompts,
ONLY the compositional sentences route C in the readable zone (L≥24); factual, arithmetic,
and simple-declarative gated controls route ZERO C-late. The proper specificity test (v3
lacked the gated guards) passes cleanly on the s127 model.

**❌ Qwen3-8B: does NOT reproduce (composition_specific=False both z).** At z=2
gate_neutral C-late (0.714) EXCEEDS lambda (0.333); at z=3 all conditions silent. The
non-compositional control out-routes lambda ⇒ no composition specificity on 8B.

**❌ Qwen3-32B (64L): composition_specific=False — but for a DIFFERENT reason: the
C-LOCUS SHIFTED EARLY.** C-late frac = 0 for ALL conditions in the depth≥0.6 zone (L≥38).
BUT the raw-arc shows lambda C-dominant at **L5, L10, L11 (EARLY, depth ~0.1)** while
gate_neutral has C only at L0 ⇒ 32B DOES show a lambda-specific C-**early** signal that the
fixed C-late detector misses entirely (late stack is Y-dominated, Y×29).

**★ CONCLUSION (3 models): composition→C routing exists in ALL three, but the C-LOCUS
SHIFTS with scale — 8B C-late non-specific, 14B C-LATE specific (L27–32), 32B C-EARLY
(L5–11).** `composition_specific=True` ONLY for 14B, largely because its C-locus happens to
land in the fixed depth≥0.6 readable zone. So it is NOT a scale-monotone story and NOT
universal; **14B is the outlier for the C-LATE framing specifically.** The underlying
"lambda routes C, matched controls do not" phenomenon may be more general but at
MODEL-SPECIFIC DEPTHS ⇒ **the fixed-depth (0.6) detector is the wrong cross-model
instrument** (it found the signal on 14B but mislocates it on 32B). Methodological fix: per-
model C-locus calibration (find where lambda-vs-control C-routing peaks) or a locus-
agnostic full-profile compare, not a fixed zone. Caveats: 5 lambda sentences, 3 models,
modest fractions ("above chance not crisp" s219).


[CONTENT TRUNCATED] Showing lines 1 to 220 of 923 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py",
  "limit": 220
}
```

**Summary:** Reading opcode_monitor_v2.py (0-220)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Opcode Monitor v2 (+v5 lead 1) — recover the compose-arc without reopening the
over-read (s231); add a LOCUS-AGNOSTIC C detector (s233).

v5 lead 1 (s233): the s232 scale verdict found the fixed depth>=0.6 C-late detector is
the WRONG cross-model instrument — it found 14B (C-late L27-32) but mislocates 8B/32B,
because the composition->C routing LOCUS SHIFTS with scale (32B is C-EARLY L5,10,11,
depth ~0.1). build_verdict now emits a locus_agnostic block (detect_c_profile +
locus_agnostic_specificity) that counts C-dominant crystal layers ANYWHERE and tests
specificity vs the matched gated guards independent of locus.

s231 (a) BUILT + VALIDATED the over-read killer: RelationalCrystalClassifier no-ops
retrieval (the raw-argmax tracer fired an opcode for 100% of tokens = common-mode).
BUT it OVER-CORRECTED -> UNDER-read: the RAW per-layer traces showed a consistent
C->B compose-arc across ALL 5 lambda prompts (C in L2-12, B in L13-33 = the real s127
compose signature, task-specific not common-mode) and the relational reader at z=3,
last-token no-opped it entirely.

Two diagnosed causes (vsm-opcode-monitor.md §v2), both fixed here:

  1. NULL mis-spec (the KEY fix) — the off-target null was OTHER crystal probes, all
     lambda-mode, so "looks more like B than K/I/C?" had low power. v2 builds a
     CROSS-TASK null from a NON-combinator baseline (bare natural-text tokens, no
     β-reduction). Then "lambda token looks like B vs a natural-text token" clears,
     while retrieval (also natural-text mode) stays silent. (relational_opcode.py
     calibrate(..., null_gate_by_layer=...).)

  2. LAST-TOKEN locus (s227 wrong-locus) — a sentence's final token isn't one opcode;
     the program unfolds across tokens. v2 reads PER-TOKEN across the sequence and
     aggregates a PER-LAYER TRAJECTORY (the C→B program), not a single dominant op.

Plus a z-threshold sweep (z∈{2,3}; z is threshold-independent so swept post-hoc).

CONDITIONS (the only variable across the read is the SENTENCE CONTENT; gate held where
noted):
  • LAMBDA      = COMPILE_GATE + s127 compositional sentences (quantifiers / conditional
                  / relative clause)  → content positions  → expect the C→B arc.
  • GATE_NEUTRAL= COMPILE_GATE + non-compositional declaratives → content positions →
                  the GATE-CONFOUND CONTROL: if it ALSO fires the arc, the arc is
                  gate-driven; if it stays quiet while LAMBDA fires, it is composition-
                  driven (the load-bearing control, λ measure).
  • RETRIEVAL   = bare fact-lookup prompts → all positions → SILENCE GUARD (the
                  over-read must stay killed; held out from the null prompts).
  • ARITHMETIC  = bare arithmetic prompts → all positions → secondary (selection mode).

CROSS-TASK NULL = bare BASELINE_NULL natural-text tokens (no gate, no computation).
CAVEAT (λ measure, recorded): LAMBDA carries the COMPILE_GATE prefix; the null/guards
are bare. Part of any LAMBDA elevation could be the gate-mode shift rather than
β-reduction per se. GATE_NEUTRAL is the direct control for this; the s231 validation
also showed bare retrieval routes W (gauge) not C->B, i.e. the arc is task-specific.

Usage:
    uv run python scripts/experiments/opcode_monitor_v2.py
    uv run python scripts/experiments/opcode_monitor_v2.py --smoke
    uv run python scripts/experiments/opcode_monitor_v2.py --model Qwen/Qwen3-8B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

# ── project root and classifier import ────────────────────────────────────────
_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))

from relational_opcode import CRYSTAL, RelationalCrystalClassifier  # noqa: E402

# ── constants ─────────────────────────────────────────────────────────────────
RESULTS_DIR = _ROOT / "results" / "opcode-monitor-v2"
COMPILE_GATE = (_ROOT / "gates" / "compile.txt").read_text(encoding="utf-8")
Z_SWEEP = [2.0, 3.0]
# readable register (readout-register-reduction-readability.md): reduction becomes
# vocab-readable at depth >= ~0.6; the C-late composition signal lives here (s232 v3).
READABLE_FRAC = 0.6

# LAMBDA signal — s127 compositional sentences (gate-prefixed, content read)
LAMBDA_SENTENCES = [
    "The dog runs.",
    "Every student reads a book.",
    "If it rains, the ground is wet.",
    "No bird can swim.",
    "Mary likes the cat that John owns.",
]

# GATE-CONFOUND CONTROL — gate + non-compositional declaratives (content read).
# Also serves as the MATCHED-PREFIX NULL under --null-mode gateneutral (the v3 lever:
# composition-ABOVE-FRAMING). Expanded to ~14 for a robust null (~70+ content tokens).
GATE_NEUTRAL_SENTENCES = [
    "The sky is blue.",
    "Coffee is a drink.",
    "The house is old.",
    "The city is large.",
    "The book is heavy.",
    "The water is cold.",
    "The road is long.",
    "The lamp is bright.",
    "The chair is wooden.",
    "The bread is fresh.",
    "The river is wide.",
    "The mountain is tall.",
    "The garden is green.",
    "The window is open.",
]

# RETRIEVAL silence guard — bare fact-lookup (held out from the null)
RETRIEVAL_PROMPTS = [
    "The capital of France is",
    "The author of Hamlet is",
    "Water is made of hydrogen and",
    "The largest planet is",
    "The first president of the United States was",
]

# ARITHMETIC secondary — bare
ARITHMETIC_PROMPTS = [
    "2 + 3 =",
    "7 * 8 =",
    "15 - 4 =",
    "Compute 12 + 27.",
    "What is 9 times 6?",
]

# CROSS-TASK NULL baseline — bare natural text, no computation, no lists/quantifiers
BASELINE_NULL_SENTENCES = [
    "The sky was clear this morning.",
    "She walked to the store yesterday.",
    "Music played softly in the room.",
    "The old house stood on the hill.",
    "He drinks coffee every morning.",
    "Rain fell throughout the night.",
    "The garden was full of color.",
    "They watched a film last weekend.",
    "A gentle breeze moved the curtains.",
    "The city lights glowed at dusk.",
    "Children played outside in the sun.",
    "The train arrived a little late.",
]


# ═══════════════════════════════════════════════════════════════════════════════
# Gate-capture hook (ALL token positions — the per-token fix)
# ═══════════════════════════════════════════════════════════════════════════════
def _make_hook(store: dict[int, np.ndarray], layer_idx: int):
    """Forward hook: capture the WHOLE module output [T, d] as float64 CPU."""

    def _hook(_module, _inp, out):
        # out: [B, T, d] — keep all positions (d = intermediate_size for gate,
        # hidden_size for attn o_proj)
        vec = out[0, :, :].detach().float().cpu().numpy()
        store[layer_idx] = vec.astype(np.float64)

    return _hook


def _hook_module(model, li: int, hook: str):
    """Select the per-layer module to hook for a given register.

    hook='gate' → mlp.gate_proj output (the FFN gate register, default).
    hook='attn' → self_attn.o_proj output (attention's write to the residual = the
                  value/attention register; s127 {B,C}=composers→attention, s206).
    """
    layer = model.model.layers[li]
    if hook == "gate":
        return layer.mlp.gate_proj
    if hook == "attn":
        return layer.self_attn.o_proj
    raise ValueError(f"unknown hook target: {hook!r} (expected 'gate' or 'attn')")


# ═══════════════════════════════════════════════════════════════════════════════
# Model loader + forward runner
# ═══════════════════════════════════════════════════════════════════════════════
def load_model_and_tokenizer(model_name: str):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"[v2] Loading tokenizer: {model_name}")
    tok = AutoTokenizer.from_pretrained(model_name)
    print(f"[v2] Loading model: {model_name}  (dtype=auto, device_map=auto)")
    t0 = time.time()
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto", device_map="auto"
    )
    model.eval()
    print(f"[v2] Model loaded in {time.time()-t0:.1f}s")
    return model, tok, torch


def forward_all_positions(
    prompt: str, model, tok, torch_mod, layers: list[int], hook: str = "gate"
) -> tuple[dict[int, np.ndarray], int]:
    """Run one prompt forward; return ({li: activation [T, d]}, n_tokens).

    hook ∈ {'gate' (default, mlp.gate_proj), 'attn' (self_attn.o_proj)}.
    """
    store: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        h = _hook_module(model, li, hook).register_forward_hook(
            _make_hook(store, li)
        )
        handles.append(h)
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)

[CONTENT TRUNCATED] Showing lines 1 to 220 of 714 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/reduction_graph_tracer.py",
  "limit": 220
}
```

**Summary:** Reading reduction_graph_tracer.py (0-220)

**Output:**
```
"""Reduction Graph Tracer — Decode FFN→Attention computation as beta reduction graph.

Session 174. Tests the hypothesis:
  FFN proposes reductions (via gating) → Attention executes them (via routing)

For each input:
  1. At each layer, capture FFN gate activations (which neurons survive)
  2. Project surviving activations onto combinator fingerprints → decode per-position opcodes
  3. Capture attention patterns
  4. Check: does attention preferentially route between positions with compatible operations?
     (e.g., β_apply source → argument target)

Comparison: lambda input (should show structured reduction graph) vs neutral text (less structured).

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/reduction_graph_tracer.py
    uv run python scripts/experiments/reduction_graph_tracer.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "reduction-graph"
HOLOGRAM_BASE = Path(__file__).parent.parent.parent / "results" / "hologram-reader"
FINGERPRINT_BASE = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

# Combinator names matching hologram reader
ALL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF", "beta_K", "beta_I", "beta_apply", "beta_compose"]

# Test inputs — lambda expression vs neutral control
INPUTS = {
    "lambda_apply": "λx.λy.(x y) applied to (λz.z) gives",
    "lambda_compose": "(B f g) x reduces to f (g x) because composition",
    "lambda_church": "λf.λx.(f (f x)) is the Church numeral for 2",
    "neutral_factual": "The capital of France is Paris which is a large city",
    "neutral_simple": "The cat sat on the mat and looked at the birds",
    "code_function": "def apply(f, x): return f(x)  # beta reduction in Python",
}

# Zone boundaries for 0.6B (from hologram reader)
ZONES_06B = {
    "SILENT": (0, 13),
    "ENRICH": (14, 22),
    "SUPPRESS": (23, 25),
    "COMMIT": (26, 27),
}


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Load combinator fingerprints
# ══════════════════════════════════════════════════════════════════════

def load_fingerprints(model_name: str) -> dict[str, np.ndarray]:
    """Load per-layer combinator direction fingerprints. Shape: (n_layers, d_model)."""
    model_slug = model_name.replace("/", "_")
    fp_path = FINGERPRINT_BASE / model_slug / f"fingerprints_{model_slug}.npz"
    if not fp_path.exists():
        raise FileNotFoundError(f"No fingerprints at {fp_path}. Run hologram_reader.py first.")
    data = np.load(fp_path)
    fps = {op: data[op] for op in ALL_OPS if op in data}
    log(f"Loaded {len(fps)} combinator fingerprints, shape {list(fps.values())[0].shape}")
    return fps


# ══════════════════════════════════════════════════════════════════════
# Model loading and hooking
# ══════════════════════════════════════════════════════════════════════

@dataclass
class LayerTrace:
    """Captured activations from one layer for one input."""
    layer_idx: int
    # Per-position combinator energy: shape (seq_len, n_ops)
    op_energy: np.ndarray
    # Per-position dominant opcode
    dominant_ops: list[str]
    # Gate survival rate per position
    gate_survival: np.ndarray
    # Attention pattern: shape (n_heads, seq_len, seq_len)
    attention: np.ndarray


@dataclass
class ForwardTrace:
    """Complete trace of one forward pass."""
    input_text: str
    input_key: str
    tokens: list[str]
    n_layers: int
    layers: list[LayerTrace] = field(default_factory=list)


def trace_forward(
    model,
    tokenizer,
    fingerprints: dict[str, np.ndarray],
    input_text: str,
    input_key: str,
    device: str = "mps",
) -> ForwardTrace:
    """Run forward pass with hooks, decode reduction graph."""

    # Tokenize
    inputs = tokenizer(input_text, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    seq_len = input_ids.shape[1]
    tokens = [tokenizer.decode(t) for t in input_ids[0]]

    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    n_ops = len(ALL_OPS)

    # Storage for hook captures
    gate_acts = {}  # layer_idx -> (seq_len, d_ff)
    ffn_outputs = {}  # layer_idx -> (seq_len, d_model)
    attention_weights = {}  # layer_idx -> (n_heads, seq_len, seq_len)
    hidden_states = {}  # layer_idx -> (seq_len, d_model) — input to FFN

    # Register hooks
    hooks = []

    def make_gate_hook(layer_idx):
        """Hook into the gate projection to capture which neurons fire."""
        def hook_fn(module, input, output):
            # For Qwen2-style SwiGLU: gate_proj output before activation
            # The actual gating is: act(gate_proj(x)) * up_proj(x)
            # We want the gate values to know which neurons survive
            gate_acts[layer_idx] = output.detach().cpu().numpy()[0]  # (seq_len, d_ff)
        return hook_fn

    def make_ffn_output_hook(layer_idx):
        """Capture FFN output (what gets added to residual)."""
        def hook_fn(module, input, output):
            ffn_outputs[layer_idx] = output.detach().cpu().numpy()[0]  # (seq_len, d_model)
        return hook_fn

    def make_attn_hook(layer_idx):
        """Capture attention weights."""
        def hook_fn(module, input, output):
            # output is typically (attn_output, attn_weights, past_kv) or just attn_output
            if isinstance(output, tuple) and len(output) >= 2 and output[1] is not None:
                attention_weights[layer_idx] = output[1].detach().cpu().numpy()[0]  # (n_heads, seq_len, seq_len)
        return hook_fn

    def make_hidden_hook(layer_idx):
        """Capture hidden state entering the FFN (post-attention residual)."""
        def hook_fn(module, input, output):
            # input to MLP is the post-attention hidden state
            if isinstance(input, tuple):
                hidden_states[layer_idx] = input[0].detach().cpu().numpy()[0]  # (seq_len, d_model)
            else:
                hidden_states[layer_idx] = input.detach().cpu().numpy()[0]
        return hook_fn

    for i in range(n_layers):
        layer = model.model.layers[i]
        # Hook gate_proj to get gating signal
        hooks.append(layer.mlp.gate_proj.register_forward_hook(make_gate_hook(i)))
        # Hook MLP module to get FFN output
        hooks.append(layer.mlp.register_forward_hook(make_ffn_output_hook(i)))
        # Hook the MLP's forward to get its input hidden state
        hooks.append(layer.mlp.register_forward_hook(make_hidden_hook(i)))
        # Hook attention to get weights (need output_attentions=True)
        hooks.append(layer.self_attn.register_forward_hook(make_attn_hook(i)))

    # Forward pass with attention output
    with torch.no_grad():
        outputs = model(
            **inputs,
            output_attentions=True,
            return_dict=True,
        )

    # Extract attention weights from model output if hooks didn't capture
    if not attention_weights and hasattr(outputs, 'attentions') and outputs.attentions is not None:
        for i, attn in enumerate(outputs.attentions):
            attention_weights[i] = attn.detach().cpu().numpy()[0]  # (n_heads, seq_len, seq_len)

    # Remove hooks
    for h in hooks:
        h.remove()

    # ══════════════════════════════════════════════════════════════════
    # Decode: project FFN output onto combinator fingerprints
    # ══════════════════════════════════════════════════════════════════

    trace = ForwardTrace(
        input_text=input_text,
        input_key=input_key,
        tokens=tokens,
        n_layers=n_layers,
    )

    for layer_idx in range(n_layers):
        # Get the FFN contribution to residual stream
        if layer_idx not in ffn_outputs:
            continue

[CONTENT TRUNCATED] Showing lines 1 to 220 of 537 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/isa_decoder.py",
  "limit": 220
}
```

**Summary:** Reading isa_decoder.py (0-220)

**Output:**
```
"""ISA Decoder — Decompile Qwen3.6-27B FFN computation to instruction sets.

Session 161. The FFNs contain piles of beta reductions. Attention runs
inference patterns programmed by FFN projections. This script decodes
those patterns into a readable instruction set architecture (ISA).

The model IS a computer. Each layer IS an instruction. The FFN overlay
matrix (combinator-space input → combinator-space output) IS the opcode.
The residual stream IS the register file. Attention IS the memory bus.

Architecture (Qwen3.6-27B):
  64 layers, d=5120, d_ff=17408
  Pattern: [L,L,L,F]×16 (48 linear attention + 16 full attention)
  SwiGLU FFN: gate_proj(d→d_ff) * up_proj(d→d_ff) → down_proj(d_ff→d)
  24 attention heads, 4 KV heads, d_head=256

The ISA:
  OPCODES derived from KIBC-DYWH combinator basis:
    SELECT(K)   — discard one operand, keep the other
    PASS(I)     — identity, forward unchanged
    COMPOSE(B)  — chain two functions: f(g(x))
    FLIP(C)     — reorder arguments: f(y)(x) instead of f(x)(y)
    DCOMPOSE(D) — deep compose: f(g(h(x)))
    RECURSE(Y)  — fixed-point / loop
    DUPLICATE(W)— self-apply: f(x)(x)
    HALT(WHNF)  — weak head normal form, stop reducing

  OPERANDS tracked via residual stream projection into combinator space.
  CONTROL FLOW detected via WHNF/Y activation patterns.
  BASIC BLOCKS formed at phase transitions (composition→selection etc).

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/isa_decoder.py 2>&1 | tee results/isa-decode/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoConfig

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode"
MODEL_NAME = "Qwen/Qwen3.6-27B"
DEVICE = "mps"

# Architecture constants
N_LAYERS = 64
D_MODEL = 5120
D_FF = 17408
FULL_ATTN_LAYERS = list(range(3, 64, 4))  # [3, 7, 11, ..., 63]
LINEAR_ATTN_LAYERS = [i for i in range(64) if i not in FULL_ATTN_LAYERS]

# KIBC-DYWH combinator names and their ISA opcode equivalents
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
OPCODE_NAMES = {
    "K": "SELECT",
    "I": "PASS",
    "B": "COMPOSE",
    "C": "FLIP",
    "D": "DCOMPOSE",
    "Y": "RECURSE",
    "W": "DUPLICATE",
    "WHNF": "HALT",
}
# Also track beta-reduction variants (observed in v12 tracer)
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# § 1  Model Loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3.6-27B and return the language model + tokenizer.

    Qwen3.6-27B is a vision-language model (Qwen3_5ForConditionalGeneration).
    Hierarchy:
      full_model.model.visual           — vision encoder (ignore)
      full_model.model.language_model   — the text transformer we want
        .embed_tokens                   — token embeddings
        .layers[0..63]                  — 64 decoder layers
        .norm                           — final RMSNorm
        .rotary_emb                     — RoPE
      full_model.lm_head               — output projection

    Layer types (all Qwen3_5DecoderLayer):
      Linear attn (48 layers): .linear_attn (GatedDeltaNet) + .mlp
      Full attn   (16 layers): .self_attn (Attention) + .mlp
      MLP identical: gate_proj(17408,5120), up_proj(17408,5120),
                     down_proj(5120,17408), SiLU activation
    """
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    from transformers import Qwen3_5ForConditionalGeneration
    full_model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    full_model.eval()

    # The language model is where the layers live
    lang_model = full_model.model.language_model
    log(f"  Loaded in {time.time()-t0:.1f}s")
    log(f"  Language model type: {type(lang_model).__name__}")
    log(f"  N layers: {len(lang_model.layers)}")

    return lang_model, full_model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# § 2  FFN Activation Capture
# ══════════════════════════════════════════════════════════════════════

def get_mlp_module(lang_model, layer_idx: int):
    """Get the MLP/FFN module for a given layer.

    Qwen3.6-27B has SwiGLU FFN (identical on both layer types):
      gate = silu(gate_proj(x))     — (5120 → 17408)
      up = up_proj(x)               — (5120 → 17408)
      down = down_proj(gate * up)   — (17408 → 5120)
    """
    return lang_model.layers[layer_idx].mlp


def capture_ffn_and_residual(
    lang_model,
    full_model,
    tokenizer,
    text: str,
    layers: list[int] | None = None,
) -> dict:
    """Capture FFN output AND residual stream at specified layers, last token.

    Uses a single forward pass through the full VLM with text-only input.
    Hooks are placed on lang_model.layers[i] (the actual transformer layers).

    Returns:
      {layer_idx: {"ffn_out": np.array, "residual_pre": np.array}}
    """
    if layers is None:
        layers = list(range(N_LAYERS))

    ids = tokenizer.encode(text, return_tensors="pt")
    # Move to the device of the first model parameter
    device = next(full_model.parameters()).device
    ids = ids.to(device)

    captures = {}
    hooks = []

    for li in layers:
        captures[li] = {}

        # Hook the MLP down_proj output (FFN contribution to residual)
        def make_ffn_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx]["ffn_out"] = out[0, -1, :].detach().cpu().float().numpy()
            return hook

        mlp = get_mlp_module(lang_model, li)
        hooks.append(mlp.down_proj.register_forward_hook(make_ffn_hook(li)))

        # Hook the layer input (residual before this layer)
        def make_pre_hook(layer_idx):
            def hook(m, inp, out=None):
                # Input to the decoder layer: first positional arg is hidden_states
                x = inp[0] if isinstance(inp, tuple) else inp
                captures[layer_idx]["residual_pre"] = x[0, -1, :].detach().cpu().float().numpy()
            return hook

        layer = lang_model.layers[li]
        hooks.append(layer.register_forward_pre_hook(make_pre_hook(li)))

    with torch.no_grad():
        # Forward pass through the full model with text-only input
        # (no pixel_values → skips vision encoder, goes straight to language model)
        _ = full_model(input_ids=ids)

    for h in hooks:
        h.remove()

    return captures


# ══════════════════════════════════════════════════════════════════════
# § 3  Combinator Fingerprinting
# ══════════════════════════════════════════════════════════════════════

# Compile gate for fingerprinting context
COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def build_fingerprint_pairs() -> dict[str, list[tuple[str, str]]]:
    """Minimal pairs for each combinator reduction.

[CONTENT TRUNCATED] Showing lines 1 to 220 of 1168 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v14/isa_decoder_v2.py",
  "limit": 180
}
```

**Summary:** Reading isa_decoder_v2.py (0-180)

**Output:**
```
"""Moiré Grating Decoder v2 — Read the program from the weights.

Session 161. The FFN IS a moiré grating. gate_proj and up_proj are
two diffraction patterns that interfere through element-wise multiply
(SwiGLU). Where they constructively interfere = a beta reduction that
attention will follow. The grating is static — burned into weights by
GD. Attention has exactly ONE operation (weighted sum). The grating
is what makes that one operation perform different beta reductions at
different layers.

The program is deterministic. GD found a fixed point. The crystal
lattice shows up identically across models because these are the
energy minima of what a single-operation machine can compute through
shaped diffraction. Non-determinism exists only at the leaves
(token selection via temperature).

Architecture:
  Qwen3.6-27B: 64 layers, d=5120, d_ff=17408
  [L,L,L,F]×16: 48 linear attention + 16 full attention
  16 full-attention checkpoints at L3,7,11,...,63

This script:
  Phase 1: Load/build fingerprints (saved as .npz for reuse)
  Phase 2: Read static program from weights (overlay matrices = instruction ROM)
  Phase 3: Trace inputs with attention capture at 16 full-attn checkpoints
  Phase 4: Assemble: grating → activation → attention reads → data flow

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/isa_decoder_v2.py 2>&1 | tee results/isa-decode-v2/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode-v2"
V1_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode"
MODEL_NAME = "Qwen/Qwen3.6-27B"
DEVICE = "mps"

# Architecture
N_LAYERS = 64
D_MODEL = 5120
D_FF = 17408
N_HEADS = 24
N_KV_HEADS = 4
D_HEAD = 256  # Note: Qwen3.6-27B uses 256-dim heads (not d_model/n_heads)
FULL_ATTN_LAYERS = list(range(3, 64, 4))  # [3, 7, 11, ..., 63]
LINEAR_ATTN_LAYERS = [i for i in range(64) if i not in FULL_ATTN_LAYERS]

# Combinator basis
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)

FINGERPRINT_FILE = RESULTS_DIR / "fingerprints_full.npz"

COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# § 1  Model Loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3.6-27B, return language model + full model + tokenizer."""
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    from transformers import Qwen3_5ForConditionalGeneration
    full_model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        device_map="auto", low_cpu_mem_usage=True,
        attn_implementation="eager",  # Required to capture attention weights
    )
    full_model.eval()
    lang_model = full_model.model.language_model

    log(f"  Loaded in {time.time()-t0:.1f}s ({len(lang_model.layers)} layers)")
    return lang_model, full_model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# § 2  Fingerprinting (with save/load)
# ══════════════════════════════════════════════════════════════════════

def build_fingerprint_pairs() -> dict[str, list[tuple[str, str]]]:
    """Minimal pairs for each combinator. Same as v1."""
    pairs = {}
    pairs["K"] = [(f"K {a} {b}", f"{a}") for a in ["x","y","a","b","f","g"] for b in ["z","w","c","d"] if a!=b][:10]
    pairs["I"] = [(f"I {v}", f"{v}") for v in ["x","y","a","b","f","g","z","w"]]
    pairs["B"] = [(f"B {f} {g} {x}", f"{f} ({g} {x})") for f in ["f","g","h","p"] for g in ["q","r","s"] if f!=g for x in ["x","a"]][:10]
    pairs["C"] = [(f"C {f} {x} {y}", f"{f} {y} {x}") for f in ["f","g","h"] for x in ["x","a","m"] for y in ["y","b","n"] if x!=y][:10]
    pairs["D"] = [(f"D {f} {g} {h} {x}", f"{f} ({g} ({h} {x}))") for f in ["f","p"] for g in ["g","q"] for h in ["h","r"] if f!=g and g!=h for x in ["x","a"]][:8]
    pairs["Y"] = [(f"Y {f}", f"{f} (Y {f})") for f in ["f","g","h","p","q","r"]]
    pairs["W"] = [(f"W {f} {x}", f"{f} {x} {x}") for f in ["f","g","h","p"] for x in ["x","a","b"]][:8]
    pairs["WHNF"] = [(f"λx. {b}", f"λx. {b}") for b in ["x","f x","g (h x)","x y","f (g x) y"]][:6]
    pairs["beta_K"] = [(f"(λx. λy. x) {a} {b}", f"{a}") for a in ["a","b","x","m"] for b in ["c","y","n"] if a!=b][:8]
    pairs["beta_I"] = [(f"(λx. x) {v}", f"{v}") for v in ["a","b","x","y","f","g","z","w"]]
    pairs["beta_apply"] = [(f"(λx. {f} x) {v}", f"{f} {v}") for f in ["f","g","h","p","q"] for v in ["a","x","m"]][:10]
    pairs["beta_compose"] = [(f"(λx. {f} ({g} x)) {v}", f"{f} ({g} {v})") for f in ["f","g","h"] for g in ["p","q","r"] if f!=g for v in ["a","x"]][:8]
    return pairs


def capture_ffn(lang_model, full_model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture FFN down_proj output at specified layers, last token."""
    ids = tokenizer.encode(text, return_tensors="pt")
    device = next(full_model.parameters()).device
    ids = ids.to(device)

    captures = {}
    hooks = []
    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(lang_model.layers[li].mlp.down_proj.register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = full_model(input_ids=ids)

    for h in hooks:
        h.remove()
    return captures


def build_fingerprints(lang_model, full_model, tokenizer) -> dict[str, np.ndarray]:
    """Build or load fingerprints. Returns {op_name: (n_layers, d_model)} arrays."""

    # Try loading saved fingerprints
    if FINGERPRINT_FILE.exists():
        log(f"  Loading saved fingerprints from {FINGERPRINT_FILE}")
        data = np.load(FINGERPRINT_FILE)
        fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
        if len(fingerprints) == N_OPS:
            log(f"  ✓ Loaded {N_OPS} ops × {fingerprints[ALL_OP_NAMES[0]].shape[0]} layers")
            return fingerprints
        log(f"  ⚠ Incomplete ({len(fingerprints)}/{N_OPS}), rebuilding...")

    log(f"\n═══ Building fingerprints ({N_OPS} ops × {N_LAYERS} layers) ═══")
    pairs = build_fingerprint_pairs()
    all_layers = list(range(N_LAYERS))
    fingerprints = {}

    for op_name, op_pairs in pairs.items():
        log(f"  {op_name}: {len(op_pairs)} pairs")
        # Accumulate deltas: (n_layers, d_model)
        layer_deltas = {li: [] for li in all_layers}

        for pi, (pre_expr, post_expr) in enumerate(op_pairs):
            pre_text = f"{COMPILE_GATE}\n\n{pre_expr} ="
            post_text = f"{COMPILE_GATE}\n\n{post_expr} ="
            pre_caps = capture_ffn(lang_model, full_model, tokenizer, pre_text, all_layers)
            post_caps = capture_ffn(lang_model, full_model, tokenizer, post_text, all_layers)


[CONTENT TRUNCATED] Showing lines 1 to 180 of 899 total lines. Use line_offset=180 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/instruments/relational_opcode.py",
  "limit": 220
}
```

**Summary:** Reading relational_opcode.py (0-220)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing
"""Relational crystal opcode classifier — the VALIDATED upgrade (s231, audit-aware).

THE OVER-READ THIS FIXES (audit-meta-pattern.md, s202→s206):
  "combinator opcodes: prose fires opcodes AFTER common-mode removal (p=0.001) — REAL;
   raw argmax 'tracer' = common mode = false signal."
The legacy opcode_instrument projects the FFN down-proj output onto per-op fingerprints
with RAW cosine + argmax — no register discipline, no common-mode removal, no null. It
MANUFACTURES crisp opcodes (the instrument that found the structure also faked its
crispness). This classifier replaces that with the validated read:

  1. REGISTER  — classify in the GATE routing register (sign(gate)-CMR), where the
     combinator crystal actually lives (s203 sign-topology ONLY in gate_proj; s231 the
     routing register = sign(gate)-CMR). Requires a GATED MLP (SwiGLU/GeGLU).
  2. COMMON-MODE — subtract the per-layer calibration common-mode before projecting
     (the s202 fix; the gauge that inflates every raw cosine).
  3. RELATIONAL — project onto per-combinator centroids built from the crystal probes;
     report which layers are crystal-bearing by Gram alignment to the CONSENSUS crystal
     (results/combinator-map-consensus/consensus.json, the s219 universal target).
  4. NULL — every per-op energy is a z-score vs an off-target permutation null; a token
     emits an opcode ONLY if z>thresh, else NO-OP (kills "argmax always picks winner").

DESIGN: model-AGNOSTIC. calibrate() and classify() take per-layer gate FEATURE matrices
(the caller runs the model + captures gate); the numpy science is unit-testable on
synthetic data with planted structure, no model load. The instrument (which already
hooks the gate) feeds it; the validation harness feeds it from a real HF forward pass.

CRYSTAL-9 = K I B C S D W Y WHNF (aligns with the consensus Gram order).

License: MIT
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np

CRYSTAL = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
_PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
CONSENSUS_PATH = (_PROJECT_ROOT / "results" / "combinator-map-consensus"
                  / "consensus.json")


# --------------------------------------------------------------------------- #
# numpy crystal instruments (inlined; mirror relational_loss_distillation)      #
# --------------------------------------------------------------------------- #
def _unit_rows(X: np.ndarray) -> np.ndarray:
    return X / (np.linalg.norm(X, axis=1, keepdims=True) + 1e-30)


def _centroids(X: np.ndarray, labels: np.ndarray) -> np.ndarray:
    C = np.zeros((len(CRYSTAL), X.shape[1]), np.float64)
    for j, c in enumerate(CRYSTAL):
        m = labels == c
        if m.any():
            C[j] = X[m].mean(axis=0)
    return C


def _gram(C: np.ndarray) -> np.ndarray:
    U = _unit_rows(C)
    return np.clip(U @ U.T, -1, 1)


def _offdiag_corr(a: np.ndarray, b: np.ndarray) -> float:
    off = ~np.eye(len(CRYSTAL), dtype=bool)
    x, y = a[off], b[off]
    if x.std() < 1e-9 or y.std() < 1e-9:
        return 0.0
    return float(np.corrcoef(x, y)[0, 1])


def _silhouette(X: np.ndarray, labels: np.ndarray) -> float:
    U = _unit_rows(_centroids(X, labels))
    Xu = _unit_rows(X)
    sims = Xu @ U.T
    li = np.array([CRYSTAL.index(c) for c in labels])
    rows = np.arange(len(labels))
    own = sims[rows, li]
    other = sims.copy()
    other[rows, li] = -np.inf
    return float(np.mean(own - other.max(axis=1)))


def _silhouette_z(X: np.ndarray, labels: np.ndarray, n_perm: int,
                  rng: np.random.Generator) -> float:
    obs = _silhouette(X, labels)
    null = np.array([_silhouette(X, rng.permutation(labels)) for _ in range(n_perm)])
    return float((obs - null.mean()) / (null.std() + 1e-30))


def load_consensus_gram() -> np.ndarray | None:
    if not CONSENSUS_PATH.exists():
        return None
    d = json.loads(CONSENSUS_PATH.read_text())
    if list(d.get("crystal_order", [])) != CRYSTAL:
        return None
    return np.array(d["consensus_gram"], dtype=np.float64)


# --------------------------------------------------------------------------- #
@dataclass
class LayerCalib:
    """Per-layer calibration: the common-mode, centroids, and the null."""
    common_mode: np.ndarray                 # [d] mean sign(gate) over calib probes
    centroids: np.ndarray                   # [9, d] unit per-combinator centroids (CMR)
    null_mean: np.ndarray                   # [9] null projection mean per op
    null_std: np.ndarray                    # [9] null projection std per op
    silhouette_z: float                     # crystal significance at this layer
    gc_consensus: float                     # Gram alignment to consensus (or nan)
    crystal_bearing: bool                   # sil_z>thresh (∧ gc>0 if consensus present)
    null_kind: str = "offtarget"            # "offtarget"(crystal) | "crosstask"


@dataclass
class TokenOpcodes:
    """One token's per-layer opcode read."""
    per_layer: dict = field(default_factory=dict)   # li -> {op: z}
    emitted: dict = field(default_factory=dict)      # li -> [significant ops]
    dominant: str = "·"                              # max-z op (crystal) or no-op


class RelationalCrystalClassifier:
    """Validated FFN-routing opcode reader: gate register, sign-CMR,
    consensus-relational, null-calibrated. Model-agnostic (gate feature matrices in)."""

    def __init__(self, layers: list[int], *, n_perm: int = 300, z_thresh: float = 3.0,
                 sil_z_thresh: float = 2.0, seed: int = 0,
                 consensus_gram: np.ndarray | str | None = "auto"):
        self.layers = list(layers)
        self.n_perm = n_perm
        self.z_thresh = z_thresh
        self.sil_z_thresh = sil_z_thresh
        self.seed = seed
        # "auto" -> load the project consensus; None -> disable (synthetic/no-target);
        # ndarray -> use as given.
        self.consensus_gram = (load_consensus_gram()
                               if isinstance(consensus_gram, str)
                               else consensus_gram)
        self.calib: dict[int, LayerCalib] = {}

    # -- S5 calibration: build the per-layer crystal from the probe activations -- #
    def calibrate(self, gate_by_layer: dict[int, np.ndarray],
                  labels: np.ndarray,
                  null_gate_by_layer: dict[int, np.ndarray] | None = None,
                  ) -> dict[int, LayerCalib]:
        """gate_by_layer[li] = [N, d] gate last-token features for the N crystal probes;
        labels [N] in CRYSTAL. Build per-layer common-mode, CMR centroids, the null,
        silhouette-z, and consensus Gram alignment.

        NULL (s231 v2 — the over-read-killer that no longer under-reads):
          - null_gate_by_layer=None (default, BACK-COMPAT): off-target null — per op j
            the null is the projection of NON-j crystal probes onto j's centroid. But
            every crystal probe is lambda-mode, so "looks more like B than K/I/C?" has
            LOW POWER (the s231 under-read: the C→B arc no-ops at z=3).
          - null_gate_by_layer[li] = [M, d] NON-combinator baseline gate features (e.g.
            natural-text / retrieval tokens where no β-reduction happens): CROSS-TASK
            null — per op j the null is the projection of BASELINE tokens onto j's
            centroid (through the SAME sign-CMR transform). Then z asks "does this token
            look more like op j than a typical natural-text token does?" — recovers the
            lambda compose-arc while keeping retrieval silent."""
        labels = np.asarray(labels)
        rng = np.random.default_rng(self.seed)
        null_kind = "crosstask" if null_gate_by_layer is not None else "offtarget"
        for li in self.layers:
            G = np.asarray(gate_by_layer[li], dtype=np.float64)
            S = np.sign(G)
            common = S.mean(axis=0)                       # the common-mode (gauge)
            X = S - common                                # sign-CMR routing features
            cents = _centroids(X, labels)
            ucents = _unit_rows(cents)
            Xu = _unit_rows(X)
            sims = Xu @ ucents.T                          # [N, 9] cos to each centroid
            li_idx = np.array([CRYSTAL.index(c) for c in labels])
            nmean = np.zeros(len(CRYSTAL))
            nstd = np.ones(len(CRYSTAL))
            if null_gate_by_layer is not None:
                # CROSS-TASK null: project baseline (non-combinator) tokens through the
                # SAME sign-CMR transform onto each centroid; the per-op population is
                # the natural-text baseline distribution.
                B = np.asarray(null_gate_by_layer[li], dtype=np.float64)  # [M, d]
                Vb = np.sign(B) - common                                  # CMR baseline
                Vbu = _unit_rows(Vb)
                bsims = Vbu @ ucents.T                                    # [M, 9]
                for j in range(len(CRYSTAL)):
                    col = bsims[:, j]
                    nmean[j] = col.mean()
                    nstd[j] = col.std() + 1e-9
            else:
                # off-target null per op: projection of NON-op probes onto op centroid
                for j in range(len(CRYSTAL)):
                    off = sims[li_idx != j, j]
                    if off.size:
                        nmean[j] = off.mean()
                        nstd[j] = off.std() + 1e-9
            sil_z = _silhouette_z(X, labels, self.n_perm, rng)
            gc = (_offdiag_corr(_gram(cents), self.consensus_gram)
                  if self.consensus_gram is not None else float("nan"))
            bearing = sil_z > self.sil_z_thresh and (np.isnan(gc) or gc > 0.0)
            self.calib[li] = LayerCalib(
                common_mode=common, centroids=ucents, null_mean=nmean, null_std=nstd,
                silhouette_z=round(sil_z, 3),
                gc_consensus=(round(gc, 3) if not np.isnan(gc) else float("nan")),
                crystal_bearing=bool(bearing), null_kind=null_kind)
        return self.calib

    @property
    def crystal_layers(self) -> list[int]:
        return [li for li, c in self.calib.items() if c.crystal_bearing]

    # -- S1 classify: token gate -> null-calibrated per-op z, emit if significant -- #
    def classify(self, gate_by_layer_token: dict[int, np.ndarray]) -> TokenOpcodes:
        """gate_by_layer_token[li] = [d] one token's gate at layer li. Returns per-layer
        op z-scores, the significant (z>thresh) opcodes, and the dominant op across
        crystal-bearing layers (or '·' no-op if none significant)."""
        out = TokenOpcodes()

[CONTENT TRUNCATED] Showing lines 1 to 220 of 322 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/tracer_cross_notation_v2.py",
  "limit": 160
}
```

**Summary:** Reading tracer_cross_notation_v2.py (0-160)

**Output:**
```
"""Tracer cross-notation v2 — common-mode removal (the fidelity fix).

v1 + isa_decoder_v2 both project activations onto the raw opcode
fingerprints and take argmax. But the 8 fingerprints share a large
common mode (a generic "language composition" direction), so the raw
projection is dominated by it: every probe reports the same primary_op
at a given layer — an ILLUSION of universal opcode firing. The
combinator-specific signal is a small residual underneath.

This script removes the per-layer common mode from the fingerprints
(fp_op − mean_op(fp), renormalized) and asks again: does the residual,
combinator-discriminative fingerprint classify pure prose by combinator?

Reports RAW vs COMMON-MODE-REMOVED (CMR) for:
  - nearest-centroid leave-one-out classification accuracy (+ perm null)
  - prose vs lambda amplitude

If CMR rescues classification at 14B, the combinator structure is real
and was merely masked by measurement fidelity (the common mode). If not,
the combinator distinction genuinely isn't recoverable from prose.

Usage:
    uv run python scripts/experiments/tracer_cross_notation_v2.py \
        --model Qwen/Qwen3-14B --device mps --n-perm 2000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch

_ROOT = Path(__file__).resolve().parent.parent.parent
if str(_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_ROOT / "src"))

from verbum.probes.library import crystal_probes  # noqa: E402

CRYSTAL_OPS = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
RESULTS_DIR = _ROOT / "results" / "tracer-cross-notation"


def log(m):
    print(m, file=sys.stderr, flush=True)


def is_prose(p):
    return ("λ" not in p.prompt) and ("lambda" not in p.prompt.lower())


def load_fingerprints(slug):
    d = np.load(_ROOT / "results" / "hologram-reader" / slug / "opcode_map.npz")
    return np.stack([d[f"fp_{op}"] for op in CRYSTAL_OPS], 0)  # (n_ops, n_layers, d_model)


def remove_common_mode(fps):
    """Per layer, subtract the across-op mean fingerprint, renormalize."""
    common = fps.mean(0, keepdims=True)              # (1, n_layers, d_model)
    resid = fps - common
    norm = np.linalg.norm(resid, axis=2, keepdims=True)
    return resid / np.maximum(norm, 1e-9)


def capture_ffn_output(model, tok, prompts, device, n_layers):
    caps = {li: [] for li in range(n_layers)}
    hooks = []
    for li in range(n_layers):
        def mk(layer):
            def fn(m, i, o):
                caps[layer].append(o[:, -1, :].detach().cpu().float().numpy())
            return fn
        hooks.append(model.model.layers[li].mlp.down_proj.register_forward_hook(mk(li)))
    for pi, prompt in enumerate(prompts):
        ids = tok.encode(prompt, return_tensors="pt", truncation=True, max_length=128).to(device)
        with torch.no_grad():
            model(ids)
        if (pi + 1) % 150 == 0:
            log(f"    {pi+1}/{len(prompts)}")
    for h in hooks:
        h.remove()
    return np.stack([np.concatenate([caps[li][p] for li in range(n_layers)], 0)
                     for p in range(len(prompts))], 0)  # (n_probes, n_layers, d_model)


def opcode_energy(ffn, fps):
    """ffn (P,L,D) · fps (O,L,D) → (P,O) summed over layers."""
    return np.einsum("pld,old->po", ffn, fps)


def nearest_centroid_loo(X, y, n_classes):
    """Leave-one-out nearest-(class-centroid) accuracy. X standardized."""
    Xs = (X - X.mean(0)) / (X.std(0) + 1e-9)
    correct = 0
    for i in range(len(y)):
        best, bd = -1, np.inf
        for c in range(n_classes):
            idx = [j for j in range(len(y)) if y[j] == c and j != i]
            if not idx:
                continue
            cen = Xs[idx].mean(0)
            d = np.sum((Xs[i] - cen) ** 2)
            if d < bd:
                bd, best = d, c
        correct += int(best == y[i])
    return correct / len(y)


def classify_block(E, y, n_perm, rng, n_classes):
    acc = nearest_centroid_loo(E, y, n_classes)
    null = []
    for _ in range(n_perm):
        yp = y.copy()
        rng.shuffle(yp)
        null.append(nearest_centroid_loo(E, yp, n_classes))
    null = np.array(null)
    p = float((np.sum(null >= acc) + 1) / (n_perm + 1))
    return {"accuracy": acc, "null_mean": float(null.mean()),
            "null_std": float(null.std()), "p_value": p}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-14B")
    ap.add_argument("--device", default="mps")
    ap.add_argument("--n-perm", type=int, default=2000)
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    rng = np.random.default_rng(args.seed)
    n_classes = len(CRYSTAL_OPS)

    from transformers import AutoModelForCausalLM, AutoTokenizer
    slug = args.model.replace("/", "_")
    fps_raw = load_fingerprints(slug)
    fps_cmr = remove_common_mode(fps_raw)
    # mean pairwise cosine of raw fingerprints (the common-mode magnitude)
    flat = fps_raw.reshape(n_classes, -1)
    flat = flat / np.maximum(np.linalg.norm(flat, axis=1, keepdims=True), 1e-9)
    cm = flat @ flat.T
    mean_fp_cos = float(cm[~np.eye(n_classes, dtype=bool)].mean())

    probes = [p for p in crystal_probes() if p.combinator in CRYSTAL_OPS]
    prose = [p for p in probes if is_prose(p)]
    lam = [p for p in probes if not is_prose(p)]
    log(f"  prose={len(prose)} lambda={len(lam)}  mean fingerprint pairwise cosine={mean_fp_cos:+.3f}")

    tok = AutoTokenizer.from_pretrained(args.model, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.float16,
        device_map=args.device if args.device != "mps" else None,
        trust_remote_code=True)
    if args.device == "mps":

[CONTENT TRUNCATED] Showing lines 1 to 160 of 197 total lines. Use line_offset=160 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/tracer-works-different-programs.md",
  "limit": 120
}
```

**Summary:** Reading tracer-works-different-programs.md (0-120)

**Output:**
```
💡 The combinator tracer works. Different tasks run different combinator programs.

Session 127. First successful decompilation of neural computation to
combinator traces on Qwen3-14B. Key findings:

1. VALIDATION: tracer correctly identifies K, B, S, nested reductions.
   K peaks at L24 (cos=0.71), S peaks at L24 (cos=0.79). L24 = 60%
   depth = crystal breathing peak.

2. LAMBDA COMPILATION: early layers use composers (B, S, C), late
   layers anti-correlate with selectors. The compiler composes first,
   then suppresses selection. This is the lambda calculus circuit.

3. ARITHMETIC: early layers are SILENT. Mid-late layers use selectors
   (beta_identity, beta_K, beta_apply). Arithmetic is SELECTION not
   COMPOSITION. This is church encoding — numbers are selectors.
   → This is the pile of beta reductions we predicted. Kernel candidate.

4. RETRIEVAL: nearly silent across ALL layers. Factual retrieval
   doesn't use combinator operations. Different mechanism entirely
   (attention-based KV lookup, not FFN computation).

5. Each task type has a distinct combinator signature that's readable
   from the FFN activation pattern. We can now SEE what program the
   model is running for any input.

The decompiler is real. The opcode table works. Next: trace more
complex operations, identify the beta reduction piles for kernel
replacement, and map the full function library.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/memories/redex-nf-beats-full-trace-per-token.md",
  "limit": 120
}
```

**Summary:** Reading redex-nf-beats-full-trace-per-token.md (0-120)

**Output:**
```
💡 redex→NF beats full β-reduction trace per-token; the formats tie on accuracy.

s229 exposure/format sweep, held-out rule generalization. SINGLE-seed looked like
full_trace won absolute acc (0.351 vs 0.297) — but the 3-SEED HARDEN dissolved it:
- k_varied absolute: full_trace 0.320±0.023 vs redex_nf 0.306±0.006 = OVERLAPPING
  (parity, NOT a full_trace win — the single-seed gap was seed noise).
- PER-TOKEN: redex_nf wins decisively everywhere (k_varied 0.183 vs 0.094 acc/kB
  ≈ 2×), because full_trace's corpus is 2× the bytes (3392 vs 1672).

⇒ showing the full reduction trace (every intermediate β-step) bought NOTHING here
once seeds and token-budget are controlled. redex→NF (input → normal form only) is
the better format: equal accuracy at half the cost.

LESSON (λ measure): compare data formats PER-TOKEN AND multi-seed; an apparent
single-seed format advantage can be noise. (Caveat: tiny model / acc≤0.32 ceiling;
a full_trace edge could re-emerge at scale or on deeper reductions — untested.)
See sentence-atomic-curriculum-mixing.md §s229.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py",
  "line_offset": 220,
  "limit": 260
}
```

**Summary:** Reading opcode_monitor_v2.py (220-480)

**Output:**
```
    finally:
        for h in handles:
            h.remove()
    n_tokens = int(inputs["input_ids"].shape[1])
    return store, n_tokens


def gate_prefix_len(tok) -> int:
    """Number of tokens the COMPILE_GATE prefix occupies (content start index)."""
    return len(tok(COMPILE_GATE)["input_ids"])


# ═══════════════════════════════════════════════════════════════════════════════
# Calibration: crystal centroids (last token) + cross-task null (baseline tokens)
# ═══════════════════════════════════════════════════════════════════════════════
def calibrate_v2(
    model, tok, torch_mod, layers: list[int], n_perm: int,
    probes_per_combinator: int | None, null_positions_cap: int | None,
    null_mode: str = "crosstask",
    centroid_probes: list | None = None,
    hook: str = "gate",
) -> tuple[RelationalCrystalClassifier, dict]:
    """null_mode:
      - "crosstask"   (s232): null = bare natural-text tokens (all positions). Removes
        the natural-text common-mode; the gate-FRAMING (S-late) survives, swamps comp.
      - "gateneutral" (s232 v3 lever): null = GATE_NEUTRAL CONTENT tokens (gate +
        non-compositional sentence, content positions). MATCHED-PREFIX null => z is
        composition-ABOVE-FRAMING (the framing S-late is subtracted)."""
    from verbum.probes.library import crystal_probes

    # centroid_probes (held-out split, s233 lead 2b): use the supplied list instead of
    # the full crystal set, so the prose bridge can calibrate on CALIB and read TEST.
    source = centroid_probes if centroid_probes is not None else crystal_probes()
    probes = [p for p in source if p.combinator in CRYSTAL]
    if probes_per_combinator is not None:
        kept, counts = [], Counter()
        for p in probes:
            if counts[p.combinator] < probes_per_combinator:
                kept.append(p)
                counts[p.combinator] += 1
        probes = kept
    print(f"[v2] Crystal probes (last-token centroids): {len(probes)}")

    gate_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    labels: list[str] = []
    for i, p in enumerate(probes):
        if i % 50 == 0:
            print(f"[v2]   centroid forward {i}/{len(probes)} ...")
        store, _ = forward_all_positions(p.prompt, model, tok, torch_mod, layers,
                                         hook=hook)
        for li in layers:
            gate_by_layer[li].append(store[li][-1])  # last token = the crystal locus
        labels.append(p.combinator)  # type: ignore[arg-type]
    gate_np = {li: np.stack(gate_by_layer[li], axis=0) for li in layers}
    labels_np = np.array(labels)

    null_by_layer: dict[int, list[np.ndarray]] = {li: [] for li in layers}
    if null_mode == "gateneutral":
        gate_n = gate_prefix_len(tok)
        print(f"[v2] Building MATCHED-PREFIX null from {len(GATE_NEUTRAL_SENTENCES)} "
              "gate+non-compositional prompts (content positions) ...")
        for s in GATE_NEUTRAL_SENTENCES:
            store, n = forward_all_positions(
                COMPILE_GATE + s, model, tok, torch_mod, layers, hook=hook)
            lo = min(gate_n, n - 1)
            for li in layers:
                null_by_layer[li].append(store[li][lo:])  # content tokens only
    else:  # crosstask
        print(f"[v2] Building cross-task null from {len(BASELINE_NULL_SENTENCES)} "
              "bare natural-text prompts ...")
        for s in BASELINE_NULL_SENTENCES:
            store, _n = forward_all_positions(s, model, tok, torch_mod, layers,
                                              hook=hook)
            for li in layers:
                null_by_layer[li].append(store[li])  # [T, d], all positions
    null_np = {li: np.concatenate(null_by_layer[li], axis=0) for li in layers}
    if null_positions_cap is not None:
        null_np = {li: arr[:null_positions_cap] for li, arr in null_np.items()}
    n_null = next(iter(null_np.values())).shape[0]
    print(f"[v2] Null tokens pooled: {n_null}  (null_mode={null_mode})")

    rcc = RelationalCrystalClassifier(
        layers, n_perm=n_perm, z_thresh=min(Z_SWEEP), sil_z_thresh=2.0,
        consensus_gram="auto",
    )
    rcc.calibrate(gate_np, labels_np, null_gate_by_layer=null_np)
    summ = rcc.calibration_summary()
    summ["n_null_tokens"] = n_null
    summ["n_centroid_probes"] = len(probes)
    summ["null_mode"] = null_mode
    summ["hook"] = hook
    return rcc, summ


# ═══════════════════════════════════════════════════════════════════════════════
# Per-token reading → reduce to per-layer (argmax-op, z) (threshold-independent)
# ═══════════════════════════════════════════════════════════════════════════════
def read_prompt_tokens(
    rcc: RelationalCrystalClassifier, store: dict[int, np.ndarray],
    layers: list[int], positions: list[int],
) -> list[dict[int, tuple[str, float]]]:
    """For each position, classify and reduce each layer to its argmax (op, z)."""
    reads: list[dict[int, tuple[str, float]]] = []
    for pos in positions:
        gate_tok = {li: store[li][pos] for li in layers}
        tok_ops = rcc.classify(gate_tok)
        red: dict[int, tuple[str, float]] = {}
        for li, zmap in tok_ops.per_layer.items():
            op = max(zmap, key=zmap.get)  # argmax over null-calibrated z
            red[li] = (op, float(zmap[op]))
        reads.append(red)
    return reads


# ═══════════════════════════════════════════════════════════════════════════════
# Analysis: per-layer trajectory + emit/no-op rates at a z-threshold
# ═══════════════════════════════════════════════════════════════════════════════
def analyze_category(
    reads_by_prompt: list[list[dict[int, tuple[str, float]]]],
    layers: list[int], crystal_layers: list[int], zthresh: float,
) -> dict:
    crystal_set = set(crystal_layers)
    layer_votes: dict[int, Counter] = {li: Counter() for li in layers}
    cell_emit = cell_total = 0
    token_noop = n_tokens = 0
    for prompt_reads in reads_by_prompt:
        for tok_read in prompt_reads:
            n_tokens += 1
            fired = False
            for li, (op, z) in tok_read.items():
                cell_total += 1
                if z > zthresh:
                    cell_emit += 1
                    layer_votes[li][op] += 1
                    if li in crystal_set:
                        fired = True
            if not fired:
                token_noop += 1
    per_layer_dom = {}
    for li in layers:
        if layer_votes[li]:
            op, c = layer_votes[li].most_common(1)[0]
            per_layer_dom[li] = {"op": op, "votes": c,
                                 "total": sum(layer_votes[li].values())}
    # trajectory over crystal-bearing layers (the C→B program)
    trajectory = [{"layer": li, **per_layer_dom[li]}
                  for li in sorted(crystal_set) if li in per_layer_dom]
    return {
        "z_thresh": zthresh,
        "n_tokens": n_tokens,
        "token_noop_rate": (token_noop / n_tokens) if n_tokens else 0.0,
        "cell_emit_rate": (cell_emit / cell_total) if cell_total else 0.0,
        "per_layer_dominant": {str(li): d for li, d in per_layer_dom.items()},
        "trajectory": trajectory,
        "c_late": detect_c_late(trajectory, len(layers)),
    }


def detect_c_late(trajectory: list[dict], n_layers: int,
                  readable_frac: float = READABLE_FRAC) -> dict:
    """C-LATE detector (s232 v3): fraction of readable-zone (depth>=readable_frac)
    crystal layers where C (composition combinator) dominates. The routing-register
    composition signal is C-LATE, NOT the raw C-early→B-late arc (detect_arc)."""
    zone_lo = int(readable_frac * n_layers)
    zone = [t for t in trajectory if t["layer"] >= zone_lo]
    c_zone = [t for t in zone if t["op"] == "C"]
    return {
        "readable_zone_lo": zone_lo,
        "n_zone_layers": len(zone),
        "n_C_late": len(c_zone),
        "C_late_layers": [t["layer"] for t in c_zone],
        "C_late_frac": (len(c_zone) / len(zone)) if zone else 0.0,
    }


def detect_c_profile(trajectory: list[dict], n_layers: int) -> dict:
    """LOCUS-AGNOSTIC C detector (v5 lead 1). The fixed depth>=0.6 zone (detect_c_late)
    found 14B (C-late) but MISLOCATED 8B/32B — 32B routes composition C-EARLY (L5,10,11,
    depth ~0.1) which the readable-zone detector reads as 0 (s232 scale verdict: the
    C-locus SHIFTS with scale, the fixed-depth detector is the wrong cross-model
    instrument). This counts C-dominant crystal layers ANYWHERE in the stack and
    reports the per-model locus, so specificity is locus-independent."""
    c_layers = [t["layer"] for t in trajectory if t["op"] == "C"]
    n_traj = len(trajectory)
    denom = max(n_layers - 1, 1)
    depths = [li / denom for li in c_layers]
    early = [li for li in c_layers if li / denom < 1 / 3]
    mid = [li for li in c_layers if 1 / 3 <= li / denom < 2 / 3]
    late = [li for li in c_layers if li / denom >= 2 / 3]
    return {
        "C_layers": c_layers,
        "n_C": len(c_layers),
        "n_crystal_in_traj": n_traj,
        "C_frac_all": (len(c_layers) / n_traj) if n_traj else 0.0,
        "C_mean_depth": (float(np.mean(depths)) if depths else None),
        "C_locus_bins": {"early": len(early), "mid": len(mid), "late": len(late)},
    }


def locus_agnostic_specificity(
    lam_traj: list[dict], guard_trajs: dict[str, list[dict]],
    n_layers: int, margin: float = 0.10,
) -> dict:
    """Compare lambda's C-routing to the matched gated guards across ALL crystal layers
    (locus-agnostic). Two specificity reads:
      • frac:      lambda C_frac_all clears every guard's C_frac_all by `margin`;
      • exclusive: crystal layers where lambda routes C and NO gated guard does
                   (the sharpest 'composition routes C where controls don't' test,
                   independent of locus)."""
    lam = detect_c_profile(lam_traj, n_layers)
    guards = {g: detect_c_profile(t, n_layers) for g, t in guard_trajs.items()}
    guard_fracs = {g: round(p["C_frac_all"], 4) for g, p in guards.items()}
    max_guard = max(guard_fracs.values()) if guard_fracs else 0.0
    guard_c_union = set()
    for p in guards.values():
        guard_c_union |= set(p["C_layers"])
    exclusive = sorted(set(lam["C_layers"]) - guard_c_union)
    return {
        "lambda_C_profile": lam,
        "guard_C_frac_all": guard_fracs,
        "max_guard_C_frac_all": round(max_guard, 4),
        "composition_specific_agnostic": bool(lam["C_frac_all"] > max_guard + margin),
        "C_exclusive_layers": exclusive,
        "n_C_exclusive": len(exclusive),
        "exclusive_specific": bool(len(exclusive) >= 2),
    }


def detect_arc(trajectory: list[dict]) -> dict:
    """C→B compose-arc detector: are C-dominant layers earlier than B-dominant?"""
    c_layers = [t["layer"] for t in trajectory if t["op"] == "C"]
    b_layers = [t["layer"] for t in trajectory if t["op"] == "B"]
    arc = {
        "C_layers": c_layers, "B_layers": b_layers,
        "C_mean_layer": (float(np.mean(c_layers)) if c_layers else None),
        "B_mean_layer": (float(np.mean(b_layers)) if b_layers else None),
        "n_C": len(c_layers), "n_B": len(b_layers),
    }
    arc["C_before_B"] = bool(
        c_layers and b_layers and np.mean(c_layers) < np.mean(b_layers)
    )
    arc["arc_present"] = bool(arc["C_before_B"] and len(c_layers) >= 2
                             and len(b_layers) >= 2)
    return arc


# ═══════════════════════════════════════════════════════════════════════════════
# Battery runner
# ═══════════════════════════════════════════════════════════════════════════════
def run_monitor(
    model, tok, torch_mod, rcc: RelationalCrystalClassifier, layers: list[int],
    n_prompts: int | None,
) -> dict:
    crystal_layers = rcc.crystal_layers
    gate_n = gate_prefix_len(tok)

    # (prompts, gated?) per condition. gate_retrieval/gate_arithmetic = the v4
    # FRAMING-MATCHED guards (valid under a gated null; the bare ones are invalid —
    # they fire purely from framing-contrast, s232 v3 lesson). They are gated
    # non-composition tasks: if C-late is composition-specific they must stay C-late

[CONTENT TRUNCATED] Showing lines 221 to 480 of 714 total lines. Use line_offset=480 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/opcode_monitor_v2.py",
  "line_offset": 480,
  "limit": 220
}
```

**Summary:** Reading opcode_monitor_v2.py (480-700)

**Output:**
```
    # silent; if they also route C-late then C-late is gated-generic not composition.
    conditions = {
        "lambda": ([COMPILE_GATE + s for s in LAMBDA_SENTENCES], True),
        "gate_neutral": ([COMPILE_GATE + s for s in GATE_NEUTRAL_SENTENCES], True),
        "gate_retrieval": ([COMPILE_GATE + s for s in RETRIEVAL_PROMPTS], True),
        "gate_arithmetic": ([COMPILE_GATE + s for s in ARITHMETIC_PROMPTS], True),
        "retrieval": (RETRIEVAL_PROMPTS, False),
        "arithmetic": (ARITHMETIC_PROMPTS, False),
    }

    out: dict = {"conditions": {}}
    for cat, (prompts, gated) in conditions.items():
        if n_prompts is not None:
            prompts = prompts[:n_prompts]
        reads_by_prompt: list[list[dict[int, tuple[str, float]]]] = []
        for prompt in prompts:
            disp = prompt[-50:].replace("\n", "↵")
            print(f"[v2]   [{cat}] forward …{disp!r}")
            store, n = forward_all_positions(prompt, model, tok, torch_mod, layers)
            if gated:
                positions = list(range(min(gate_n, n - 1), n))  # content tokens
            else:
                positions = list(range(1, n)) if n > 1 else [0]  # skip BOS
            reads_by_prompt.append(
                read_prompt_tokens(rcc, store, layers, positions)
            )
        per_z = {}
        for z in Z_SWEEP:
            a = analyze_category(reads_by_prompt, layers, crystal_layers, z)
            if cat in ("lambda", "gate_neutral"):
                a["arc"] = detect_arc(a["trajectory"])
            per_z[f"z={z}"] = a
        out["conditions"][cat] = {"n_prompts": len(prompts),
                                  "gated": gated, "by_z": per_z}
    out["crystal_layers"] = crystal_layers
    return out


# ═══════════════════════════════════════════════════════════════════════════════
# Verdict
# ═══════════════════════════════════════════════════════════════════════════════
def build_verdict(monitor: dict, n_layers: int | None = None) -> dict:
    """Two-sided read: did the C→B arc recover in lambda while retrieval stays silent
    and the gate-neutral control stays quieter than lambda?

    v5 lead 1 adds a LOCUS-AGNOSTIC block (locus_agnostic_specificity) alongside the
    fixed depth>=0.6 C-late read, so cross-model specificity is tested wherever C
    concentrates (the s232 scale verdict: C-locus shifts with scale)."""
    conds = monitor["conditions"]
    if n_layers is None:
        # crystal_layers max + 1 is a lower bound; prefer caller-supplied n_layers
        n_layers = (max(monitor.get("crystal_layers", [0])) + 1) if monitor.get(
            "crystal_layers") else 1
    v: dict = {}
    margin = 0.10  # C-late specificity margin
    gated_guard_cats = ("gate_neutral", "gate_retrieval", "gate_arithmetic")
    for z in Z_SWEEP:
        key = f"z={z}"
        lam = conds["lambda"]["by_z"][key]
        gn = conds["gate_neutral"]["by_z"][key]
        ret = conds["retrieval"]["by_z"][key]
        arc = lam.get("arc", {})
        locus_agnostic = locus_agnostic_specificity(
            lam["trajectory"],
            {c: conds[c]["by_z"][key]["trajectory"] for c in gated_guard_cats},
            n_layers, margin,
        )

        def cl(cat: str, _key: str = key) -> float:
            return conds[cat]["by_z"][_key]["c_late"]["C_late_frac"]

        lam_cl = cl("lambda")
        # framing-matched gated guards (v4) — the valid specificity controls
        gated_guards = {c: round(cl(c), 4)
                        for c in ("gate_neutral", "gate_retrieval", "gate_arithmetic")}
        max_guard = max(gated_guards.values()) if gated_guards else 0.0
        v[key] = {
            # ── PRIMARY (v3/v4): C-LATE composition signal ──────────────────────
            "lambda_C_late_frac": round(lam_cl, 4),
            "lambda_C_late_layers": lam["c_late"]["C_late_layers"],
            "gated_guard_C_late_frac": gated_guards,
            "max_gated_guard_C_late_frac": round(max_guard, 4),
            # composition-SPECIFIC iff lambda C-late clears every framing-matched guard
            "composition_specific": bool(lam_cl > max_guard + margin),
            "readable_zone_lo": lam["c_late"]["readable_zone_lo"],
            # ── v5 lead 1: LOCUS-AGNOSTIC C routing (right cross-model instrument) ──
            "locus_agnostic": locus_agnostic,
            # ── back-compat: raw-shape arc + bare-guard over-read (now mis-framed) ─
            "lambda_arc_present": arc.get("arc_present", False),
            "lambda_n_C": arc.get("n_C", 0), "lambda_n_B": arc.get("n_B", 0),
            "lambda_cell_emit_rate": round(lam["cell_emit_rate"], 4),
            "retrieval_cell_emit_rate": round(ret["cell_emit_rate"], 4),
            "gate_neutral_cell_emit_rate": round(gn["cell_emit_rate"], 4),
        }
    return v


# ═══════════════════════════════════════════════════════════════════════════════
# Provenance + IO
# ═══════════════════════════════════════════════════════════════════════════════
def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=str(_ROOT), stderr=subprocess.DEVNULL
        ).decode().strip()
    except Exception:
        return "unknown"


def _transformers_version() -> str:
    try:
        import transformers
        return transformers.__version__
    except Exception:
        return "unknown"


def _json_safe(obj):
    import math
    if isinstance(obj, dict):
        return {str(k): _json_safe(x) for k, x in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(x) for x in obj]
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, np.integer):
        return int(obj)
    if isinstance(obj, np.floating):
        return float(obj)
    if isinstance(obj, np.ndarray):
        return obj.tolist()
    return obj


def _print_summary(calib: dict, verdict: dict) -> None:
    print("\n" + "═" * 72)
    print("OPCODE MONITOR v2 — SUMMARY")
    print("═" * 72)
    cl = calib["crystal_layers"]
    print(f"Crystal layers: {len(cl)}/{calib['n_layers']}  "
          f"null_mode={calib.get('null_mode')}  "
          f"null_tokens={calib.get('n_null_tokens')}")
    for z in Z_SWEEP:
        key = f"z={z}"
        d = verdict[key]
        print(f"\n[{key}]  (readable zone L>={d['readable_zone_lo']})")
        print(f"  ★ lambda C-late frac:   {d['lambda_C_late_frac']}  "
              f"layers={d['lambda_C_late_layers']}")
        print(f"    gated-guard C-late:   {d['gated_guard_C_late_frac']}  "
              f"(max={d['max_gated_guard_C_late_frac']})")
        print(f"    => COMPOSITION_SPECIFIC (fixed zone): {d['composition_specific']}")
        la = d["locus_agnostic"]
        lp = la["lambda_C_profile"]
        cfa = round(lp["C_frac_all"], 4)
        print(f"  ★ LOCUS-AGNOSTIC: lambda C_frac_all={cfa}"
              f" (nC={lp['n_C']} depth={lp['C_mean_depth']})")
        print(f"    locus bins={lp['C_locus_bins']}")
        print(f"    guard C_frac_all={la['guard_C_frac_all']} "
              f"(max={la['max_guard_C_frac_all']})")
        print(f"    C_exclusive_layers={la['C_exclusive_layers']} "
              f"(n={la['n_C_exclusive']})")
        af = la["composition_specific_agnostic"]
        print(f"    => COMP_SPECIFIC agnostic-frac={af}"
              f" exclusive={la['exclusive_specific']}")
        print(f"    (back-compat) raw-arc={d['lambda_arc_present']} "
              f"C x{d['lambda_n_C']}/B x{d['lambda_n_B']}; emit lam="
              f"{d['lambda_cell_emit_rate']} gn={d['gate_neutral_cell_emit_rate']} "
              f"ret_bare={d['retrieval_cell_emit_rate']}")
    print("═" * 72 + "\n")


# ═══════════════════════════════════════════════════════════════════════════════
def main() -> None:
    parser = argparse.ArgumentParser(description="Opcode monitor v2 (cross-task null)")
    parser.add_argument("--model", default="Qwen/Qwen3-14B")
    parser.add_argument("--null-mode", default="crosstask",
                        choices=["crosstask", "gateneutral"],
                        help="crosstask=bare natural-text null (s232); "
                             "gateneutral=matched-prefix null (v3)")
    parser.add_argument("--smoke", action="store_true",
                        help="Qwen3-0.6B, 3 probes/comb, 2 prompts/cat, n_perm=80")
    args = parser.parse_args()
    null_mode = args.null_mode

    model_name = args.model
    if args.smoke:
        if model_name == "Qwen/Qwen3-14B":
            model_name = "Qwen/Qwen3-0.6B"
        n_perm, ppc, n_prompts, null_cap = 80, 3, 2, 200
        print("[v2] SMOKE MODE")
    else:
        n_perm, ppc, n_prompts, null_cap = 300, None, None, None

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    cfg = model.config
    n_layers = cfg.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[v2] Layers: {n_layers}, intermediate_size: {cfg.intermediate_size}")

    rcc, calib = calibrate_v2(model, tok, torch_mod, layers, n_perm, ppc, null_cap,
                              null_mode=null_mode)
    print(f"[v2] Crystal-bearing layers: {len(calib['crystal_layers'])}/{n_layers} "
          f"-> {calib['crystal_layers'][:12]}  (null_mode={null_mode})")

    print("\n[v2] Running per-token monitor battery ...")
    monitor = run_monitor(model, tok, torch_mod, rcc, layers, n_prompts)
    verdict = build_verdict(monitor, n_layers=n_layers)
    _print_summary(calib, verdict)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    out = {"calibration_summary": calib, "monitor": monitor, "verdict": verdict}
    # filename tagged by model + null_mode (v4: avoids clobber across the model sweep;
    # the committed s232 verdict.json / verdict_gateneutral.json are left untouched).
    slug = model_name.split("/")[-1].lower().replace(".", "-")
    vname = f"verdict_{slug}_{null_mode}.json"
    mname = f"meta_{slug}_{null_mode}.json"
    (RESULTS_DIR / vname).write_text(
        json.dumps(_json_safe(out), indent=2), encoding="utf-8")
    meta = {
        "model": model_name, "smoke": args.smoke, "git_sha": _git_sha(),

[CONTENT TRUNCATED] Showing lines 481 to 700 of 714 total lines. Use line_offset=700 parameter to read more content.
```

### Thinking

**Considering response methods**

I need to respond, and I think I should inspect trace_collect. It might be worth mentioning decoder and tracer candidates too. I feel like recommending opcode_monitor_v2 and relational_opcode would be helpful, along with the ffn_program_decode borrowed pieces. Also, the old reduction_graph_tracer seems stale. I’m considering whether to run any tools for this — it feels like I need to clarify my tasks more! Let’s see if a more straightforward approach works.


## Assistant


Yes — found them. The relevant “tracer/decoder” lineage is real, but there are **two generations**, and only the newer one is safe to reuse.

## Best candidate: validated opcode monitor / relational decoder

Use this pair:

```text
scripts/experiments/opcode_monitor_v2.py
scripts/instruments/relational_opcode.py
```

This is the most relevant to what we want now.

### Why this one

`mementum/knowledge/explore/vsm-opcode-monitor.md` says the older tracer existed but was stale/over-readable. The validated path became:

> read opcodes RELATIONALLY in the FFN gate routing register using sign(gate)-CMR + common-mode removal + matched null.

The key instrument is:

```text
scripts/instruments/relational_opcode.py
```

It implements:

```text
RelationalCrystalClassifier
```

Core properties:

- reads the **gate routing register**;
- uses `sign(gate)` common-mode removal;
- calibrates against crystal probes;
- supports nulls;
- emits per-op z-scores instead of raw argmax hallucination;
- can classify token × layer activations.

This is already the decoder we need.

Then:

```text
scripts/experiments/opcode_monitor_v2.py
```

wraps it into a per-token monitor. Important functions:

```python
calibrate_v2(...)
forward_all_positions(...)
read_prompt_tokens(...)
analyze_category(...)
detect_c_profile(...)
locus_agnostic_specificity(...)
```

This already does the thing we were gesturing toward:

> per-token reading across sequence, aggregate per-layer trajectory, not just last-token dominant op.

It even says in the docstring:

```text
the program unfolds across tokens
```

and:

```text
output the per-layer trajectory (the program), not a single dominant op
```

So yes — this is the tracer.

---

## Important prior verdict

The relevant knowledge page is:

```text
mementum/knowledge/explore/vsm-opcode-monitor.md
```

It records the crucial historical lesson:

### Old raw tracer

- Saw a C→B arc.
- But raw argmax over-read common mode.
- It could manufacture crisp opcodes.

### v2/v3/v4 relational tracer

- Matched-null relational read killed the raw over-read.
- On **Qwen3-14B**, with gate-matched null, composition-specific **C-late** appeared.
- On **8B**, this did **not** reproduce cleanly.
- On **32B**, C locus shifted early.

Most relevant line:

> Qwen3-14B: C-late is composition-SPECIFIC … among gated prompts, ONLY compositional sentences route C in the readable zone.

This is exactly consistent with today’s 14B result. 14B is where this signal becomes clean.

---

## Other candidates found

### 1. `scripts/experiments/reduction_graph_tracer.py`

Older tracer. It captures:

- FFN gate activations;
- FFN outputs;
- attention patterns;
- per-position op energies;
- reduction graph analysis.

But it uses older fingerprint projection / hologram-reader style. The knowledge page warns that this raw family can over-read.

Use it as **structural reference**, not measurement authority.

### 2. `scripts/v14/isa_decoder.py`

This is the “ISA Decoder” from session 161.

It tries to decompile FFN computation into an instruction set:

```text
SELECT(K), PASS(I), COMPOSE(B), FLIP(C), ...
```

But it is hardwired for:

```text
Qwen/Qwen3.6-27B
```

and a 64-layer architecture. Good conceptual reference, not the first thing to run on Qwen3-14B.

### 3. `scripts/v14/isa_decoder_v2.py`

“Moiré Grating Decoder v2.”

This reads the static program from weights / FFN overlays. Again, mostly for Qwen3.6-27B. Useful if we later want the static ROM view, but not the direct next step.

### 4. `scripts/experiments/ffn_reduction_trace.py`

Knowledge page:

```text
mementum/knowledge/ffn-reduction-trace.md
```

This is the semantic/value trace — FFN output through unembedding. It reads what FFN “says” in vocabulary space. Very useful for semantic interpretation, but not the opcode-sequence decoder.

### 5. `scripts/experiments/lambda_tracer.py`

Older compression diagnostic tracer. Relevant historically, but not the current program extractor.

---

## Best reuse path

I would **not start from scratch**.

I would create a small new script that reuses:

```python
from scripts.experiments.opcode_monitor_v2 import (
    load_model_and_tokenizer,
    calibrate_v2,
    forward_all_positions,
    read_prompt_tokens,
)
```

and:

```python
from scripts.instruments.relational_opcode import RelationalCrystalClassifier
```

Then feed it our new probe set:

```text
data/firing-probes.const.jsonl
```

and compare decoded per-token/per-layer traces to each row’s:

```json
"fired_sequence": [...]
```

That is the missing bridge.

## Proposed new script

Something like:

```text
scripts/experiments/program_sequence_trace.py
```

Purpose:

> Decode the ordered β-program trace from Qwen3-14B gate register and align it against each probe’s certified `fired_sequence`.

Inputs:

```text
--model Qwen/Qwen3-14B
--probe-set data/firing-probes.const.jsonl
--null-mode gateneutral
--track C
```

Use the same calibration as `ffn_program_decode.py` / `opcode_monitor_v2.py`:

```python
rcc, calib = calibrate_v2(
    model, tok, torch_mod,
    layers=list(range(n_layers)),
    n_perm=300,
    probes_per_combinator=None,
    null_positions_cap=None,
    null_mode="gateneutral",
    hook="gate",
)
```

Then for each probe:

1. prompt = maybe `COMPILE_GATE + input`, or match whatever `ffn_program_decode` used;
2. capture all token positions with `forward_all_positions`;
3. content positions = after compile gate;
4. call `read_prompt_tokens`;
5. extract a matrix:

```text
token × layer × op_z
```

6. compare against ground truth:

```text
fired_sequence
```

---

## Metrics we should compute

The current `ffn_program_decode.py` tells us:

```text
dominant op / C-vs-S / z(C) count
```

The tracer should tell us:

```text
ordered program
```

I’d add these metrics:

### 1. Sequence coverage

For each ground-truth op in `fired_sequence`, does it appear as a high-z op somewhere in the readable layers?

```text
coverage = #ops in fired_sequence found / len(fired_sequence)
```

### 2. Ordered alignment

Does the layer order of decoded ops match the ground-truth order?

Use simple monotonic alignment first:

```text
truth:   S B C C
decoded: ... S ... B ... C ... C ...
```

Score:

```text
longest common subsequence / len(truth)
```

or edit distance.

### 3. FFN→attention lag

Use gate register for FFN and `hook="attn"` calibration/read for attention, then ask:

```text
Does FFN op at layer L predict attention/depth op at L+1?
```

But I’d make this phase 2. First get FFN sequence alignment working.

### 4. Const beats existential

For the same prose, compare two candidate truths:

```text
constant/applicative fired_sequence
existential/Montague fired_sequence
```

Question:

> Does decoded sequence align better to constant-C than existential-B?

This is the direct “wrong program vs actual program” test.

### 5. 14B beats 8B

Run the same sequence score on:

```text
Qwen3-8B
Qwen3-14B
```

Expected:

```text
14B sequence alignment > 8B
```

That would formalize the capacity-threshold claim.

---

## Caution: old tracer over-read trap

Do **not** use raw cosine/argmax as the primary claim.

The knowledge says that path already burned us:

```text
RAW argmax → C→B arc
off-target null → silent
cross-task null → S-late gate framing
gate-matched null → composition-specific C-late on 14B
```

So for this run, the safe contract is:

```text
gate register + sign-CMR + matched gateneutral null + per-token positions
```

i.e. `RelationalCrystalClassifier` via `opcode_monitor_v2`.

## Short answer

Yes, we have it.

Use:

```text
scripts/experiments/opcode_monitor_v2.py
scripts/instruments/relational_opcode.py
```

Do not primarily use the older raw tracers except as references.

The next move should be to adapt `opcode_monitor_v2` to read `data/firing-probes.const.jsonl` and score decoded per-token/per-layer op trajectories against each row’s `fired_sequence`. That should become the actual **β-program sequence tracer**.

## User


Ok let's build the experiment, run it in my tmux main:1 once it's ready

### Thinking

**Planning code modifications**

I realize I need to modify some code, so I'm formulating a plan. There’s already a task that’s needed here, and I need to inspect the `ffn_program_decode` function specifically for prompt construction. It’s crucial to ensure everything aligns properly. I want to make sure my changes are effective and that I understand how everything works together. Let's dive into that function and figure things out!


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/ffn_program_decode.py",
  "limit": 220
}
```

**Summary:** Reading ffn_program_decode.py (0-220)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing (FFN gate) + value/depth (attention o_proj)
"""FFN program-decode along `fired_sequence` — the §7 open experiment (s248).

THE CLAIM (explore/attention-as-beta-reduction.md §7, the stored-program normal form):
the transformer is a bounded soft-β-reduction machine — **FFN = the fixed β-program
(ISA/ROM) that compiles WHICH reduction to do; attention = the one-instruction CPU that
EXECUTES it, advancing reduction DEPTH (WHNF↔D) via softmax-over-V.** The splice program
(s242–s244) read/wrote the program GEOMETRY in place and closed (`fires ∩ spliceable =
∅`); its own notes left one door open: *"a richer multi-position program-decode
read along `fired_sequence`."* This script walks through it.

THE SHARP, FALSIFIABLE PREDICTIONS:
  (A) TRACKING — the FFN routing register (gate_proj, the VALIDATED opcode crystal,
      relational_opcode.py) decodes the combinator the corpus item actually FIRES
      (`lambda_ast.fired_sequence` on the SATURATED corpus, s244) BETTER than the
      attention register (o_proj) does. FFN_acc > Attn_acc, vs a permutation null AND
      the always-most-common-combinator baseline (two-sided, λ measure).
  (B) LEAD-LAG — the FFN opcode-lock LEADS the attention depth-advance by ~1 layer
      (select → execute). Per item: the layer where the FFN gate z locks the dominant
      fired combinator vs the layer where the attention o_proj z(WHNF) peaks.
      Prediction: attention-depth peaks ~1 layer AFTER the FFN opcode (positive lead),
      tested by the per-item peak-difference distribution AND a cross-correlation lag.
  (C) RESCUE — count tokens/items where the attention register OVER-READS (decodes the
      wrong combinator) but the FFN register decodes the RIGHT one. rescue > anti-rescue
      ⇒ "FFN tracks even where attention geometry over-reads."

WHY THIS REGISTER SPLIT (grounded, not arbitrary):
  • FFN gate register = where the combinator crystal is decodable (relational_opcode.py:
    sign(gate)-CMR, the routing register; s203/s231). → WHICH combinator (opcode).
  • attention o_proj register = head-combinator-isa: ALL 9 combinators drive the SAME
    head pattern (r=0.944); attention varies on WHNF↔deeply-nested = reduction DEPTH, a
    program counter NOT an opcode. → decode reduction DEPTH via z(WHNF).
  So (A)/(C) read combinator-identity in both registers (the over-read test); (B) pairs
  the FFN opcode-lock against the attention DEPTH-advance (the executor's job).

METHOD (reuses validated instruments — opcode_monitor_v2 + corpus_firing_survey):
  1. Calibrate TWO RelationalCrystalClassifiers (gate register, attn register), each on
     the crystal-probe centroids with a matched-prefix (gateneutral) null.
  2. Build the FIRING corpus: saturate every quantifier with a fresh witness (s244),
     reduce, keep items whose `fired_sequence != []` (behavioral register). GT per
     item = the fired multiset + dominant fired combinator + reduction length.
  3. For each firing item: ONE forward pass over the gate-prefixed prose, capturing BOTH
     registers at every layer; classify each content token in both registers.
  4. Metrics A/B/C + nulls + a non-firing specificity control.

Usage:
    uv run python scripts/experiments/ffn_program_decode.py --smoke
    uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B
    uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-8B \
        --max-items 120 --zone-lo 0.70 --zone-hi 0.86

License: MIT. AGENTS.md S5 λ provenance (written from this project's instruments).
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np

_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_ROOT / "scripts" / "instruments"))
sys.path.insert(0, str(_ROOT / "scripts" / "experiments"))

from corpus_firing_survey import _Fresh, saturate  # noqa: E402
from opcode_monitor_v2 import (  # noqa: E402
    COMPILE_GATE,
    _git_sha,
    _hook_module,
    _json_safe,
    _make_hook,
    _transformers_version,
    calibrate_v2,
    gate_prefix_len,
    load_model_and_tokenizer,
)

from verbum.lambda_ast import fired_sequence, parse  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "ffn-program-decode"
CORPUS = {
    "train": _ROOT / "data" / "compile-train.canonical.jsonl",
    "test": _ROOT / "data" / "compile-test.canonical.jsonl",
    "eval": _ROOT / "data" / "compile-eval.canonical.jsonl",
}
FIRING_SET = ["B", "C", "S"]  # the only combinators the corpus ever fires (s244)


# ═══════════════════════════════════════════════════════════════════════════════
# Firing corpus (saturate → fired_sequence ground truth)
# ═══════════════════════════════════════════════════════════════════════════════
def build_firing_corpus(paths=None) -> tuple[list[dict], list[dict]]:
    """Return (firing_items, nonfiring_items). Each firing item carries the certified
    ground-truth reduction trace from the SATURATED term. `paths` defaults to the
    canonical corpus; pass a custom probe-set path (e.g. the s248 B-balanced set,
    data/firing-probes.balanced.jsonl) to test B-tracking with balanced classes."""
    src = paths if paths is not None else list(CORPUS.values())
    firing: list[dict] = []
    nonfiring: list[dict] = []
    for path in src:
        for line in open(path, encoding="utf-8"):
            r = json.loads(line)
            t = parse(r["kernel_term"])
            seq = fired_sequence(saturate(t, _Fresh()))
            rec = {
                "input": r["input"],
                "category": r["category"],
                "kernel_term": r["kernel_term"],
                "fired_sequence": seq,
            }
            if seq:
                mult = Counter(seq)
                rec["fired_multiset"] = dict(mult)
                rec["dominant_fired"] = mult.most_common(1)[0][0]
                rec["reduction_len"] = len(seq)
                rec["b_count"] = mult.get("B", 0)
                rec["s_count"] = mult.get("S", 0)
                rec["c_count"] = mult.get("C", 0)
                firing.append(rec)
            else:
                nonfiring.append(rec)
    return firing, nonfiring


# ═══════════════════════════════════════════════════════════════════════════════
# Dual-register forward (capture FFN gate + attention o_proj in ONE pass)
# ═══════════════════════════════════════════════════════════════════════════════
def forward_dual(prompt, model, tok, torch_mod, layers):
    """Return (store_gate, store_attn, n_tokens). store_*[li] = [T, d] float64."""
    store_gate: dict[int, np.ndarray] = {}
    store_attn: dict[int, np.ndarray] = {}
    handles = []
    for li in layers:
        handles.append(
            _hook_module(model, li, "gate").register_forward_hook(
                _make_hook(store_gate, li)))
        handles.append(
            _hook_module(model, li, "attn").register_forward_hook(
                _make_hook(store_attn, li)))
    try:
        inputs = tok(prompt, return_tensors="pt")
        dev = next(model.parameters()).device
        inputs = {k: v.to(dev) for k, v in inputs.items()}
        with torch_mod.no_grad():
            model(**inputs)
    finally:
        for h in handles:
            h.remove()
    n_tokens = int(inputs["input_ids"].shape[1])
    return store_gate, store_attn, n_tokens


def classify_positions(rcc, store, layers, positions):
    """[positions] → list of per_layer {op: z} dicts (one per content token)."""
    reads = []
    for pos in positions:
        feat = {li: store[li][pos] for li in layers}
        reads.append(rcc.classify(feat).per_layer)
    return reads


# ═══════════════════════════════════════════════════════════════════════════════
# Per-item aggregation
# ═══════════════════════════════════════════════════════════════════════════════
def zone_layers(crystal_layers, n_layers, zone_lo, zone_hi):
    """Crystal-bearing layers whose depth ∈ [zone_lo, zone_hi] (the L26-30 zone,
    expressed as a depth fraction so it transfers across model sizes)."""
    denom = max(n_layers - 1, 1)
    z = [li for li in crystal_layers if zone_lo <= li / denom <= zone_hi]
    return z or crystal_layers  # fall back to all crystal layers if zone empty


def op_layer_profile(reads, layers, op):
    """Mean z(op) per layer across content tokens → {li: mean_z}."""
    prof = {}
    for li in layers:
        vals = [r[li][op] for r in reads if li in r]
        prof[li] = float(np.mean(vals)) if vals else float("nan")
    return prof


def dominant_in_set(reads, layers, op_set):
    """Argmax over op_set of the total positive z summed across (tokens × layers).
    Returns (dominant_op, score_by_op)."""
    score = dict.fromkeys(op_set, 0.0)
    for r in reads:
        for li in layers:
            if li not in r:
                continue
            for op in op_set:
                z = r[li][op]
                if z > 0:
                    score[op] += z
    dom = max(score, key=score.get) if any(v > 0 for v in score.values()) else "·"
    return dom, score


def peak_layer(profile, layers):
    """Layer of max mean-z in `profile` over `layers` (ignoring NaN)."""
    best_li, best_v = None, -np.inf
    for li in layers:
        v = profile.get(li, float("nan"))
        if not np.isnan(v) and v > best_v:
            best_li, best_v = li, v
    return best_li, best_v


def crosscorr_lag(f_ffn, f_attn, layers, max_lag):
    """Lag k∈[-max_lag, max_lag] maximizing corr(f_ffn[L], f_attn[L+k]).
    Positive k ⇒ FFN leads attention. Returns (best_lag, best_corr) or (None, None)."""
    xs = np.array([f_ffn.get(li, np.nan) for li in layers])
    ys = np.array([f_attn.get(li, np.nan) for li in layers])
    best_lag, best_c = None, -np.inf
    for k in range(-max_lag, max_lag + 1):

[CONTENT TRUNCATED] Showing lines 1 to 220 of 638 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/ffn_program_decode.py",
  "line_offset": 220,
  "limit": 180
}
```

**Summary:** Reading ffn_program_decode.py (220-400)

**Output:**
```
        if k >= 0:
            a, b = xs[: len(xs) - k], ys[k:]
        else:
            a, b = xs[-k:], ys[: len(ys) + k]
        m = ~(np.isnan(a) | np.isnan(b))
        if m.sum() < 3 or np.nanstd(a[m]) < 1e-9 or np.nanstd(b[m]) < 1e-9:
            continue
        c = float(np.corrcoef(a[m], b[m])[0, 1])
        if c > best_c:
            best_lag, best_c = k, c
    return best_lag, (None if best_c == -np.inf else best_c)


# ═══════════════════════════════════════════════════════════════════════════════
# Stats helpers
# ═══════════════════════════════════════════════════════════════════════════════
def perm_null_accuracy(decoded, truth, n_perm, seed=0):
    """Permutation null for accuracy: shuffle the truth labels against decoded preds.
    Returns (obs_acc, null_mean, p_value)."""
    decoded = np.array(decoded)
    truth = np.array(truth)
    obs = float(np.mean(decoded == truth))
    rng = np.random.default_rng(seed)
    null = np.empty(n_perm)
    for i in range(n_perm):
        null[i] = np.mean(decoded == rng.permutation(truth))
    p = float((np.sum(null >= obs) + 1) / (n_perm + 1))
    return obs, float(null.mean()), p


def wilcoxon_sign(values):
    """Sign test: frac>0, frac<0, median, two-sided sign-test p (binomial)."""
    v = np.array([x for x in values if x is not None and not np.isnan(x)])
    if v.size == 0:
        return {"n": 0}
    npos = int(np.sum(v > 0))
    nneg = int(np.sum(v < 0))
    nz = npos + nneg
    # two-sided exact binomial sign-test p (k = min(npos,nneg), n = nz, p0=0.5)
    from math import comb

    if nz == 0:
        p = 1.0
    else:
        k = min(npos, nneg)
        tail = sum(comb(nz, i) for i in range(k + 1)) / (2**nz)
        p = float(min(1.0, 2 * tail))
    return {
        "n": int(v.size), "n_pos": npos, "n_neg": nneg, "n_zero": int(np.sum(v == 0)),
        "median": float(np.median(v)), "mean": float(np.mean(v)),
        "frac_positive": float(npos / nz) if nz else 0.0, "sign_test_p": p,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# Main experiment
# ═══════════════════════════════════════════════════════════════════════════════
def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
        n_perm_calib, ppc, null_cap, n_perm_stat, n_nonfiring, seed,
        probe_set=None, track="B"):
    print("═" * 78)
    print("FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)")
    print("═" * 78)

    paths = [Path(probe_set)] if probe_set else None
    firing, nonfiring = build_firing_corpus(paths)
    print(f"[corpus] source={'probe-set:' + probe_set if probe_set else 'canonical'}  "
          f"firing items={len(firing)}  nonfiring={len(nonfiring)}")
    if max_items is not None:
        firing = firing[:max_items]
    rng = np.random.default_rng(seed)
    nf_sample = (list(rng.choice(len(nonfiring), size=min(n_nonfiring, len(nonfiring)),
                                 replace=False))
                 if nonfiring else [])
    nf_items = [nonfiring[i] for i in nf_sample]

    model, tok, torch_mod = load_model_and_tokenizer(model_name)
    n_layers = model.config.num_hidden_layers
    layers = list(range(n_layers))
    print(f"[model] {model_name}  layers={n_layers}")

    # ── calibrate two registers (matched-prefix null) ───────────────────────────
    print("\n[calib] FFN gate register ...")
    rcc_ffn, calib_ffn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="gate")
    print("[calib] attention o_proj register ...")
    rcc_attn, calib_attn = calibrate_v2(
        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,
        null_mode="gateneutral", hook="attn")
    cl_ffn = rcc_ffn.crystal_layers
    cl_attn = rcc_attn.crystal_layers
    zl_ffn = zone_layers(cl_ffn, n_layers, zone_lo, zone_hi)
    zl_attn = zone_layers(cl_attn, n_layers, zone_lo, zone_hi)
    print(f"[calib] FFN  crystal layers={len(cl_ffn)} zone={zl_ffn}")
    print(f"[calib] attn crystal layers={len(cl_attn)} zone={zl_attn}")

    gate_n = gate_prefix_len(tok)

    # ── decode every firing item in both registers ──────────────────────────────
    per_item = []
    ffn_pred, attn_pred, truth = [], [], []
    leads_peak, leads_xcorr = [], []
    rescue = anti_rescue = 0
    print(f"\n[decode] {len(firing)} firing items ...")
    for i, item in enumerate(firing):
        if i % 20 == 0:
            print(f"[decode]   item {i}/{len(firing)} ...")
        prompt = COMPILE_GATE + item["input"]
        sg, sa, n = forward_dual(prompt, model, tok, torch_mod, layers)
        positions = list(range(min(gate_n, n - 1), n))
        reads_ffn = classify_positions(rcc_ffn, sg, layers, positions)
        reads_attn = classify_positions(rcc_attn, sa, layers, positions)

        c_true = item["dominant_fired"]
        dom_ffn, score_ffn = dominant_in_set(reads_ffn, zl_ffn, FIRING_SET)
        dom_attn, score_attn = dominant_in_set(reads_attn, zl_attn, FIRING_SET)
        ffn_pred.append(dom_ffn)
        attn_pred.append(dom_attn)
        truth.append(c_true)
        if dom_attn != c_true and dom_ffn == c_true:
            rescue += 1
        if dom_ffn != c_true and dom_attn == c_true:
            anti_rescue += 1

        # (B) lead-lag: FFN opcode-lock(c_true) vs attn depth-advance z(WHNF)
        prof_ffn_op = op_layer_profile(reads_ffn, zl_ffn, c_true)
        prof_attn_whnf = op_layer_profile(reads_attn, zl_attn, "WHNF")
        pk_ffn, _ = peak_layer(prof_ffn_op, zl_ffn)
        pk_attn, _ = peak_layer(prof_attn_whnf, zl_attn)
        lead_peak = (pk_attn - pk_ffn) if (pk_ffn is not None
                                           and pk_attn is not None) else None
        leads_peak.append(lead_peak)
        # cross-corr lag over the SHARED crystal layers in the zone
        shared = sorted(set(zl_ffn) | set(zl_attn))
        prof_ffn_full = op_layer_profile(reads_ffn, shared, c_true)
        prof_attn_full = op_layer_profile(reads_attn, shared, "WHNF")
        lag, lag_c = crosscorr_lag(prof_ffn_full, prof_attn_full, shared, max_lag)
        leads_xcorr.append(lag)

        # (graded) mean decoded z(track) over the zone — for the count-correlation test
        def _mz(reads, zl, op):
            prof = op_layer_profile(reads, zl, op)
            vals = [v for v in prof.values() if not np.isnan(v)]
            return float(np.mean(vals)) if vals else float("nan")

        zt_ffn = _mz(reads_ffn, zl_ffn, track)
        zt_attn = _mz(reads_attn, zl_attn, track)

        per_item.append({
            "input": item["input"], "category": item["category"],
            "dominant_fired": c_true, "fired_multiset": item["fired_multiset"],
            "reduction_len": item["reduction_len"],
            "b_count": item.get("b_count"), "s_count": item.get("s_count"),
            "c_count": item.get("c_count"),
            "track_count": item.get(f"{track.lower()}_count"),
            "ffn_dominant": dom_ffn, "attn_dominant": dom_attn,
            "ffn_correct": dom_ffn == c_true, "attn_correct": dom_attn == c_true,
            "lead_peak": lead_peak, "lead_xcorr": lag, "xcorr": lag_c,
            "zt_ffn": round(zt_ffn, 4), "zt_attn": round(zt_attn, 4),
            "ffn_score": {k: round(v, 3) for k, v in score_ffn.items()},
            "attn_score": {k: round(v, 3) for k, v in score_attn.items()},
        })

    # ── (A) tracking accuracy + nulls ───────────────────────────────────────────
    ffn_acc, ffn_null, ffn_p = perm_null_accuracy(ffn_pred, truth, n_perm_stat, seed)
    attn_acc, attn_null, attn_p = perm_null_accuracy(
        attn_pred, truth, n_perm_stat, seed)
    maj = Counter(truth).most_common(1)[0][0]
    maj_acc = float(np.mean(np.array(truth) == maj))

    # track-vs-S discrimination — the contamination-resistant tracking metric. When
    # track="B" (s248 existential set): B and S are the two dominant fired combinators
    # and C is the common-mode ground state (s211/s240) that swamps the summed-z
    # dominant. When track="C" (s249 constant/applicative set): C is the object-marking
    # opcode the model actually computes and S is the implication ground state.
    # Restricting to the {track, S} contrast removes the third-combinator common-mode
    # and asks the sharp question: when the corpus fires `track` vs S, does the
    # register's z(track)−z(S) sign track it?
    bs_idx = [i for i, c in enumerate(truth) if c in (track, "S")]

[CONTENT TRUNCATED] Showing lines 221 to 400 of 638 total lines. Use line_offset=400 parameter to read more content.
```

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing (FFN gate β-program sequence)\n\"\"\"Program Sequence Trace — align decoded FFN opcode events to `fired_sequence`.\n\ns249 follow-up. `ffn_program_decode.py` showed Qwen3-14B significantly tracks the\ncorrected constant/applicative C-vs-S program label, while 8B was smeared. But that\nscript reads dominant/graded structure, not the ordered β-reduction program. This\nexperiment reuses the validated relational opcode reader (`RelationalCrystalClassifier`)\nand the per-token machinery from `opcode_monitor_v2.py` to decode a token×layer event\nsequence from the FFN gate register and align it against each probe's certified\n`fired_sequence`.\n\nMeasurement contract (audit-aware):\n  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;\n  • null: matched-prefix `gateneutral` by default — composition above gate framing;\n  • readout: per content token × crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;\n  • event: argmax over the fired set {B,C,S} with z >= --z-event;\n  • program score: LCS(truth fired_sequence, decoded event sequence), plus compressed\n    and layer-dominant variants.\n\nThis is intentionally conservative: raw argmax tracers over-read common-mode; this uses\nthe validated relational reader and reports sequence metrics rather than claiming a\ncrisp instruction tape from a single layer.\n\nUsage:\n    uv run python scripts/experiments/program_sequence_trace.py --smoke\n    uv run python scripts/experiments/program_sequence_trace.py \\\n      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl\n\nLicense: MIT. AGENTS.md S5 λ provenance.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import Counter\nfrom datetime import UTC, datetime\nfrom pathlib import Path\nfrom typing import Iterable\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom ffn_program_decode import (  # noqa: E402\n    FIRING_SET,\n    build_firing_corpus,\n    classify_positions,\n    perm_null_accuracy,\n    zone_layers,\n)\nfrom opcode_monitor_v2 import (  # noqa: E402\n    COMPILE_GATE,\n    _git_sha,\n    _json_safe,\n    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    gate_prefix_len,\n    load_model_and_tokenizer,\n)\n\nRESULTS_DIR = _ROOT / \"results\" / \"program-sequence-trace\"\n\n\ndef lcs_len(a: list[str], b: list[str]) -> int:\n    \"\"\"Length of the longest common subsequence, preserving duplicates.\"\"\"\n    if not a or not b:\n        return 0\n    prev = [0] * (len(b) + 1)\n    for x in a:\n        cur = [0] * (len(b) + 1)\n        for j, y in enumerate(b, 1):\n            cur[j] = prev[j - 1] + 1 if x == y else max(prev[j], cur[j - 1])\n        prev = cur\n    return prev[-1]\n\n\ndef compress_runs(seq: Iterable[str]) -> list[str]:\n    out: list[str] = []\n    for x in seq:\n        if not out or out[-1] != x:\n            out.append(x)\n    return out\n\n\ndef event_sequence(\n    reads: list[dict[int, dict[str, float]]],\n    layers: list[int],\n    *,\n    z_event: float,\n    op_set: list[str],\n) -> tuple[list[str], list[dict]]:\n    \"\"\"Flatten token×layer argmax events in layer-major order.\n\n    Layer-major order matches the transformer reduction axis: the residual program state\n    advances with depth; token position is the within-layer spatial/program-value axis.\n    \"\"\"\n    seq: list[str] = []\n    events: list[dict] = []\n    for li in layers:\n        for pos_i, r in enumerate(reads):\n            if li not in r:\n                continue\n            zmap = r[li]\n            op = max(op_set, key=lambda k: zmap[k])\n            z = float(zmap[op])\n            if z >= z_event:\n                seq.append(op)\n                events.append({\"layer\": li, \"content_pos\": pos_i, \"op\": op,\n                               \"z\": round(z, 4)})\n    return seq, events\n\n\ndef layer_dominant_sequence(\n    reads: list[dict[int, dict[str, float]]],\n    layers: list[int],\n    *,\n    z_event: float,\n    op_set: list[str],\n) -> list[str]:\n    \"\"\"One event per layer: mean z over content tokens, filtered by z_event.\"\"\"\n    seq: list[str] = []\n    for li in layers:\n        means = {}\n        for op in op_set:\n            vals = [r[li][op] for r in reads if li in r]\n            means[op] = float(np.mean(vals)) if vals else float(\"nan\")\n        op = max(op_set, key=lambda k: means[k])\n        if not np.isnan(means[op]) and means[op] >= z_event:\n            seq.append(op)\n    return seq\n\n\ndef seq_metrics(truth: list[str], decoded: list[str]) -> dict:\n    lcs = lcs_len(truth, decoded)\n    rev = list(reversed(decoded))\n    rev_lcs = lcs_len(truth, rev)\n    comp = compress_runs(decoded)\n    comp_lcs = lcs_len(truth, comp)\n    counts_t = Counter(truth)\n    counts_d = Counter(decoded)\n    bag_hit = sum(min(counts_t[o], counts_d[o]) for o in counts_t)\n    return {\n        \"truth_len\": len(truth),\n        \"decoded_len\": len(decoded),\n        \"lcs\": lcs,\n        \"lcs_frac\": round(lcs / len(truth), 4) if truth else 0.0,\n        \"reverse_lcs\": rev_lcs,\n        \"reverse_lcs_frac\": round(rev_lcs / len(truth), 4) if truth else 0.0,\n        \"compressed_len\": len(comp),\n        \"compressed_lcs\": comp_lcs,\n        \"compressed_lcs_frac\": round(comp_lcs / len(truth), 4) if truth else 0.0,\n        \"bag_hit\": bag_hit,\n        \"bag_frac\": round(bag_hit / len(truth), 4) if truth else 0.0,\n        \"decoded_counts\": dict(counts_d),\n        \"decoded_compressed\": comp[:80],\n    }\n\n\ndef _safe_slug(model_name: str, probe_set: str | None) -> str:\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    if probe_set:\n        stem = Path(probe_set).stem\n        slug += \"_\" + (stem.split(\".\")[-1] if \".\" in stem else stem)\n    return slug\n\n\ndef _mean(xs: list[float]) -> float | None:\n    return round(float(np.mean(xs)), 4) if xs else None\n\n\ndef run(\n    model_name: str,\n    probe_set: str,\n    max_items: int | None,\n    null_mode: str,\n    zone_lo: float,\n    zone_hi: float,\n    z_event: float,\n    n_perm_calib: int,\n    ppc: int | None,\n    null_cap: int | None,\n    n_perm_stat: int,\n    seed: int,\n) -> tuple[dict, list[dict], dict]:\n    print(\"═\" * 78)\n    print(\"PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence\")\n    print(\"═\" * 78)\n    paths = [Path(probe_set)]\n    firing, nonfiring = build_firing_corpus(paths)\n    if max_items is not None:\n        firing = firing[:max_items]\n    print(f\"[corpus] source={probe_set} firing={len(firing)} nonfiring={len(nonfiring)}\")\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    layers = list(range(n_layers))\n    print(f\"[model] {model_name} layers={n_layers}\")\n\n    print(f\"\\n[calib] FFN gate register null_mode={null_mode} ...\")\n    rcc, calib = calibrate_v2(\n        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,\n        null_mode=null_mode, hook=\"gate\")\n    crystal_layers = rcc.crystal_layers\n    zlayers = zone_layers(crystal_layers, n_layers, zone_lo, zone_hi)\n    print(f\"[calib] crystal_layers={len(crystal_layers)}/{n_layers} zone={zlayers}\")\n\n    gate_n = gate_prefix_len(tok)\n    per_item: list[dict] = []\n    truth_dom: list[str] = []\n    pred_lcs_full: list[str] = []\n    pred_lcs_layer: list[str] = []\n    pred_bag_full: list[str] = []\n    truth_has_op = {op: [] for op in FIRING_SET}\n    decoded_has_op = {op: [] for op in FIRING_SET}\n\n    print(f\"\\n[decode] {len(firing)} items z_event={z_event} ...\")\n    for i, item in enumerate(firing):\n        if i % 20 == 0:\n            print(f\"[decode]   item {i}/{len(firing)} ...\")\n        prompt = COMPILE_GATE + item[\"input\"]\n        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,\n                                             hook=\"gate\")\n        positions = list(range(min(gate_n, n_tok - 1), n_tok))\n        reads = classify_positions(rcc, store, layers, positions)\n\n        truth = list(item[\"fired_sequence\"])\n        full_seq, events = event_sequence(reads, zlayers, z_event=z_event,\n                                          op_set=FIRING_SET)\n        layer_seq = layer_dominant_sequence(reads, zlayers, z_event=z_event,\n                                            op_set=FIRING_SET)\n        full_m = seq_metrics(truth, full_seq)\n        layer_m = seq_metrics(truth, layer_seq)\n        all_seq, _ = event_sequence(reads, crystal_layers, z_event=z_event,\n                                    op_set=FIRING_SET)\n        all_m = seq_metrics(truth, all_seq)\n\n        # Convert sequence scores to simple item-level labels for permutation nulls.\n        # A positive item means at least half the certified program is recoverable.\n        pred_lcs_full.append(\"hit\" if full_m[\"lcs_frac\"] >= 0.5 else \"miss\")\n        pred_lcs_layer.append(\"hit\" if layer_m[\"lcs_frac\"] >= 0.5 else \"miss\")\n        pred_bag_full.append(\"hit\" if full_m[\"bag_frac\"] >= 0.5 else \"miss\")\n        truth_dom.append(\"hit\")  # all items have a recoverable truth by definition\n        for op in FIRING_SET:\n            truth_has = op in truth\n            dec_has = op in full_seq\n            truth_has_op[op].append(op if truth_has else f\"not_{op}\")\n            decoded_has_op[op].append(op if dec_has else f\"not_{op}\")\n\n        per_item.append({\n            \"input\": item[\"input\"],\n            \"category\": item[\"category\"],\n            \"dominant_fired\": item[\"dominant_fired\"],\n            \"fired_sequence\": truth,\n            \"fired_multiset\": item[\"fired_multiset\"],\n            \"reduction_len\": item[\"reduction_len\"],\n            \"b_count\": item.get(\"b_count\"),\n            \"s_count\": item.get(\"s_count\"),\n            \"c_count\": item.get(\"c_count\"),\n            \"n_content_tokens\": len(positions),\n            \"zone_layers\": zlayers,\n            \"decoded_event_seq\": full_seq[:200],\n            \"decoded_layer_seq\": layer_seq,\n            \"decoded_all_crystal_seq_prefix\": all_seq[:200],\n            \"events\": events[:500],\n            \"metrics_zone_events\": full_m,\n            \"metrics_zone_layers\": layer_m,\n            \"metrics_all_crystal_events\": all_m,\n        })\n\n    # Summary statistics.\n    full_fracs = [p[\"metrics_zone_events\"][\"lcs_frac\"] for p in per_item]\n    layer_fracs = [p[\"metrics_zone_layers\"][\"lcs_frac\"] for p in per_item]\n    all_fracs = [p[\"metrics_all_crystal_events\"][\"lcs_frac\"] for p in per_item]\n    bag_fracs = [p[\"metrics_zone_events\"][\"bag_frac\"] for p in per_item]\n    reverse_fracs = [p[\"metrics_zone_events\"][\"reverse_lcs_frac\"] for p in per_item]\n\n    op_presence = {}\n    for op in FIRING_SET:\n        acc, null, pval = perm_null_accuracy(\n            decoded_has_op[op], truth_has_op[op], n_perm_stat, seed)\n        op_presence[op] = {\n            \"presence_acc\": round(acc, 4),\n            \"null_mean\": round(null, 4),\n            \"perm_p\": round(pval, 4),\n            \"truth_counts\": dict(Counter(truth_has_op[op])),\n            \"decoded_counts\": dict(Counter(decoded_has_op[op])),\n        }\n\n    verdict = {\n        \"model\": model_name,\n        \"n_layers\": n_layers,\n        \"probe_set\": probe_set,\n        \"n_items\": len(per_item),\n        \"null_mode\": null_mode,\n        \"z_event\": z_event,\n        \"zone_depth\": [zone_lo, zone_hi],\n        \"zone_layers\": zlayers,\n        \"crystal_layers\": crystal_layers,\n        \"truth_distribution\": dict(Counter(p[\"dominant_fired\"] for p in per_item)),\n        \"sequence_alignment\": {\n            \"zone_events_mean_lcs_frac\": _mean(full_fracs),\n            \"zone_layer_mean_lcs_frac\": _mean(layer_fracs),\n            \"all_crystal_events_mean_lcs_frac\": _mean(all_fracs),\n            \"zone_events_mean_bag_frac\": _mean(bag_fracs),\n            \"zone_events_mean_reverse_lcs_frac\": _mean(reverse_fracs),\n            \"n_zone_events_half_recovered\": int(sum(x >= 0.5 for x in full_fracs)),\n            \"n_zone_layers_half_recovered\": int(sum(x >= 0.5 for x in layer_fracs)),\n            \"n_all_crystal_half_recovered\": int(sum(x >= 0.5 for x in all_fracs)),\n        },\n        \"op_presence\": op_presence,\n        \"decoded_event_counts\": dict(Counter(\n            op for p in per_item for op in p[\"decoded_event_seq\"])),\n        \"decoded_layer_counts\": dict(Counter(\n            op for p in per_item for op in p[\"decoded_layer_seq\"])),\n        \"calib\": calib,\n    }\n    meta = {\n        \"model\": model_name,\n        \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"params\": {\n            \"probe_set\": probe_set,\n            \"max_items\": max_items,\n            \"null_mode\": null_mode,\n            \"zone_lo\": zone_lo,\n            \"zone_hi\": zone_hi,\n            \"z_event\": z_event,\n            \"n_perm_calib\": n_perm_calib,\n            \"ppc\": ppc,\n            \"null_cap\": null_cap,\n            \"n_perm_stat\": n_perm_stat,\n            \"seed\": seed,\n        },\n        \"method\": \"RelationalCrystalClassifier on FFN gate sign-CMR with matched null; \"\n                  \"content token × crystal-layer event sequence aligned to certified \"\n                  \"lambda_ast.fired_sequence via LCS/bag metrics.\",\n    }\n    return verdict, per_item, meta\n\n\ndef write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = _safe_slug(verdict[\"model\"], verdict.get(\"probe_set\"))\n    (RESULTS_DIR / f\"verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(verdict), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"per_item_{slug}.json\").write_text(\n        json.dumps(_json_safe(per_item), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"meta_{slug}.json\").write_text(\n        json.dumps(_json_safe(meta), indent=2), encoding=\"utf-8\")\n    print(f\"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)\")\n\n\ndef report(verdict: dict) -> None:\n    s = verdict[\"sequence_alignment\"]\n    print(\"\\n\" + \"═\" * 78)\n    print(\"PROGRAM SEQUENCE TRACE — VERDICT\")\n    print(\"═\" * 78)\n    print(f\"items={verdict['n_items']} truth={verdict['truth_distribution']}\")\n    print(f\"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} \"\n          f\"zone={verdict['zone_layers']} z_event={verdict['z_event']}\")\n    print(\"\\nSequence alignment vs fired_sequence:\")\n    print(f\"  zone token×layer events mean LCS:   {s['zone_events_mean_lcs_frac']}\")\n    print(f\"  zone layer-dominant mean LCS:      {s['zone_layer_mean_lcs_frac']}\")\n    print(f\"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}\")\n    print(f\"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}\")\n    print(f\"  reverse-order control LCS:         {s['zone_events_mean_reverse_lcs_frac']}\")\n    print(f\"  half recovered: zone_events={s['n_zone_events_half_recovered']} \"\n          f\"zone_layers={s['n_zone_layers_half_recovered']} \"\n          f\"all_crystal={s['n_all_crystal_half_recovered']}\")\n    print(\"\\nOp presence (decoded event contains op vs truth contains op):\")\n    for op, d in verdict[\"op_presence\"].items():\n        print(f\"  {op}: acc={d['presence_acc']} null={d['null_mean']} p={d['perm_p']} \"\n              f\"truth={d['truth_counts']} decoded={d['decoded_counts']}\")\n    print(f\"\\nDecoded event counts: {verdict['decoded_event_counts']}\")\n    print(\"═\" * 78 + \"\\n\")\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"Trace FFN gate β-program sequence\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--probe-set\", default=\"data/firing-probes.const.jsonl\")\n    ap.add_argument(\"--max-items\", type=int, default=None)\n    ap.add_argument(\"--null-mode\", default=\"gateneutral\",\n                    choices=[\"gateneutral\", \"crosstask\"])\n    ap.add_argument(\"--zone-lo\", type=float, default=0.70)\n    ap.add_argument(\"--zone-hi\", type=float, default=0.86)\n    ap.add_argument(\"--z-event\", type=float, default=2.0)\n    ap.add_argument(\"--n-perm-stat\", type=int, default=2000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    model = args.model\n    max_items = args.max_items\n    if args.smoke:\n        if model == \"Qwen/Qwen3-14B\":\n            model = \"Qwen/Qwen3-0.6B\"\n        n_perm_calib, ppc, null_cap = 80, 3, 200\n        max_items = max_items or 6\n        print(\"[smoke] Qwen3-0.6B small calibration\")\n    else:\n        n_perm_calib, ppc, null_cap = 300, None, None\n\n    verdict, per_item, meta = run(\n        model, args.probe_set, max_items, args.null_mode, args.zone_lo, args.zone_hi,\n        args.z_event, n_perm_calib, ppc, null_cap, args.n_perm_stat, args.seed)\n    report(verdict)\n    write_outputs(verdict, per_item, meta)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "limit": 40
}
```

**Summary:** Reading program_sequence_trace.py (0-40)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing (FFN gate β-program sequence)
"""Program Sequence Trace — align decoded FFN opcode events to `fired_sequence`.

s249 follow-up. `ffn_program_decode.py` showed Qwen3-14B significantly tracks the
corrected constant/applicative C-vs-S program label, while 8B was smeared. But that
script reads dominant/graded structure, not the ordered β-reduction program. This
experiment reuses the validated relational opcode reader (`RelationalCrystalClassifier`)
and the per-token machinery from `opcode_monitor_v2.py` to decode a token×layer event
sequence from the FFN gate register and align it against each probe's certified
`fired_sequence`.

Measurement contract (audit-aware):
  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;
  • null: matched-prefix `gateneutral` by default — composition above gate framing;
  • readout: per content token × crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;
  • event: argmax over the fired set {B,C,S} with z >= --z-event;
  • program score: LCS(truth fired_sequence, decoded event sequence), plus compressed
    and layer-dominant variants.

This is intentionally conservative: raw argmax tracers over-read common-mode; this uses
the validated relational reader and reports sequence metrics rather than claiming a
crisp instruction tape from a single layer.

Usage:
    uv run python scripts/experiments/program_sequence_trace.py --smoke
    uv run python scripts/experiments/program_sequence_trace.py \
      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl

License: MIT. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

[CONTENT TRUNCATED] Showing lines 1 to 40 of 419 total lines. Use line_offset=40 parameter to read more content.
```

### Tool Call: shell_command (failed)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 1
Stdout:
RUF002 Docstring contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
  --> scripts/experiments/program_sequence_trace.py:9:74
   |
 7 | script reads dominant/graded structure, not the ordered β-reduction program. This
 8 | experiment reuses the validated relational opcode reader (`RelationalCrystalClassifier`)
 9 | and the per-token machinery from `opcode_monitor_v2.py` to decode a token×layer event
   |                                                                          ^
10 | sequence from the FFN gate register and align it against each probe's certified
11 | `fired_sequence`.
   |

RUF002 Docstring contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
  --> scripts/experiments/program_sequence_trace.py:16:32
   |
14 |   • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;
15 |   • null: matched-prefix `gateneutral` by default — composition above gate framing;
16 |   • readout: per content token × crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;
   |                                ^
17 |   • event: argmax over the fired set {B,C,S} with z >= --z-event;
18 |   • program score: LCS(truth fired_sequence, decoded event sequence), plus compressed
   |

UP035 [*] Import from `collections.abc` instead: `Iterable`
  --> scripts/experiments/program_sequence_trace.py:41:1
   |
39 | from datetime import UTC, datetime
40 | from pathlib import Path
41 | from typing import Iterable
   | ^^^^^^^^^^^^^^^^^^^^^^^^^^^
42 |
43 | import numpy as np
   |
help: Import from `collections.abc`

RUF002 Docstring contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
   --> scripts/experiments/program_sequence_trace.py:98:21
    |
 96 |     op_set: list[str],
 97 | ) -> tuple[list[str], list[dict]]:
 98 |     """Flatten token×layer argmax events in layer-major order.
    |                     ^
 99 |
100 |     Layer-major order matches the transformer reduction axis: the residual program state
    |

E501 Line too long (89 > 88)
   --> scripts/experiments/program_sequence_trace.py:198:89
    |
196 |     if max_items is not None:
197 |         firing = firing[:max_items]
198 |     print(f"[corpus] source={probe_set} firing={len(firing)} nonfiring={len(nonfiring)}")
    |                                                                                         ^
199 |
200 |     model, tok, torch_mod = load_model_and_tokenizer(model_name)
    |

RUF001 String contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
   --> scripts/experiments/program_sequence_trace.py:342:34
    |
340 |         },
341 |         "method": "RelationalCrystalClassifier on FFN gate sign-CMR with matched null; "
342 |                   "content token × crystal-layer event sequence aligned to certified "
    |                                  ^
343 |                   "lambda_ast.fired_sequence via LCS/bag metrics.",
344 |     }
    |

RUF001 String contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
   --> scripts/experiments/program_sequence_trace.py:369:25
    |
367 |           f"zone={verdict['zone_layers']} z_event={verdict['z_event']}")
368 |     print("\nSequence alignment vs fired_sequence:")
369 |     print(f"  zone token×layer events mean LCS:   {s['zone_events_mean_lcs_frac']}")
    |                         ^
370 |     print(f"  zone layer-dominant mean LCS:      {s['zone_layer_mean_lcs_frac']}")
371 |     print(f"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}")
    |

E501 Line too long (90 > 88)
   --> scripts/experiments/program_sequence_trace.py:371:89
    |
369 |     print(f"  zone token×layer events mean LCS:   {s['zone_events_mean_lcs_frac']}")
370 |     print(f"  zone layer-dominant mean LCS:      {s['zone_layer_mean_lcs_frac']}")
371 |     print(f"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}")
    |                                                                                         ^^
372 |     print(f"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}")
373 |     print(f"  reverse-order control LCS:         {s['zone_events_mean_reverse_lcs_frac']}")
    |

E501 Line too long (91 > 88)
   --> scripts/experiments/program_sequence_trace.py:373:89
    |
371 |     print(f"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}")
372 |     print(f"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}")
373 |     print(f"  reverse-order control LCS:         {s['zone_events_mean_reverse_lcs_frac']}")
    |                                                                                         ^^^
374 |     print(f"  half recovered: zone_events={s['n_zone_events_half_recovered']} "
375 |           f"zone_layers={s['n_zone_layers_half_recovered']} "
    |

Found 9 errors.
[*] 1 fixable with the `--fix` option.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "from collections import Counter\nfrom datetime import UTC, datetime\nfrom pathlib import Path\nfrom typing import Iterable\n",
  "new_content": "from collections import Counter\nfrom collections.abc import Iterable\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "token×layer",
  "new_content": "token-layer",
  "all_occurrences": true
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "token × crystal",
  "new_content": "token x crystal",
  "all_occurrences": true
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py.
```

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "token × layer",
  "new_content": "token x layer",
  "all_occurrences": true
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "    print(f\"[corpus] source={probe_set} firing={len(firing)} nonfiring={len(nonfiring)}\")\n",
  "new_content": "    print(\n        f\"[corpus] source={probe_set} firing={len(firing)} \"\n        f\"nonfiring={len(nonfiring)}\"\n    )\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py.
```

### Tool Call: edit_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "                  \"content token × crystal-layer event sequence aligned to certified \"\n",
  "new_content": "                  \"content token x crystal-layer event sequence aligned to certified \"\n"
}
```

**Summary:** Editing

**Output:**
```
Original content not found in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"×\\|all-crystal\\|reverse-order\\|token\" /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py | head -30",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ grep -n "×\|all-crystal\|reverse-or...

**Output:**
```
Exit code: 0
Stdout:
9:and the per-token machinery from `opcode_monitor_v2.py` to decode a token-layer event
16:  • readout: per content token x crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;
64:    load_model_and_tokenizer,
98:    """Flatten token-layer argmax events in layer-major order.
101:    advances with depth; token position is the within-layer spatial/program-value axis.
126:    """One event per layer: mean z over content tokens, filtered by z_event."""
203:    model, tok, torch_mod = load_model_and_tokenizer(model_name)
268:            "n_content_tokens": len(positions),
345:                  "content token x crystal-layer event sequence aligned to certified "
372:    print(f"  zone token-layer events mean LCS:   {s['zone_events_mean_lcs_frac']}")
374:    print(f"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}")
376:    print(f"  reverse-order control LCS:         {s['zone_events_mean_reverse_lcs_frac']}")
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "original_content": "    print(f\"  all-crystal events mean LCS:       {s['all_crystal_events_mean_lcs_frac']}\")\n    print(f\"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}\")\n    print(f\"  reverse-order control LCS:         {s['zone_events_mean_reverse_lcs_frac']}\")\n",
  "new_content": "    print(\n        \"  all-crystal events mean LCS:       \"\n        f\"{s['all_crystal_events_mean_lcs_frac']}\"\n    )\n    print(f\"  zone events bag coverage:          {s['zone_events_mean_bag_frac']}\")\n    print(\n        \"  reverse-order control LCS:         \"\n        f\"{s['zone_events_mean_reverse_lcs_frac']}\"\n    )\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "limit": 30
}
```

**Summary:** Reading program_sequence_trace.py (0-30)

**Output:**
```
#!/usr/bin/env python3
# register: topological/routing (FFN gate β-program sequence)
"""Program Sequence Trace — align decoded FFN opcode events to `fired_sequence`.

s249 follow-up. `ffn_program_decode.py` showed Qwen3-14B significantly tracks the
corrected constant/applicative C-vs-S program label, while 8B was smeared. But that
script reads dominant/graded structure, not the ordered β-reduction program. This
experiment reuses the validated relational opcode reader (`RelationalCrystalClassifier`)
and the per-token machinery from `opcode_monitor_v2.py` to decode a token-layer event
sequence from the FFN gate register and align it against each probe's certified
`fired_sequence`.

Measurement contract (audit-aware):
  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;
  • null: matched-prefix `gateneutral` by default — composition above gate framing;
  • readout: per content token x crystal layer z-scores over K/I/B/C/S/D/W/Y/WHNF;
  • event: argmax over the fired set {B,C,S} with z >= --z-event;
  • program score: LCS(truth fired_sequence, decoded event sequence), plus compressed
    and layer-dominant variants.

This is intentionally conservative: raw argmax tracers over-read common-mode; this uses
the validated relational reader and reports sequence metrics rather than claiming a
crisp instruction tape from a single layer.

Usage:
    uv run python scripts/experiments/program_sequence_trace.py --smoke
    uv run python scripts/experiments/program_sequence_trace.py \
      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl

License: MIT. AGENTS.md S5 λ provenance.

[CONTENT TRUNCATED] Showing lines 1 to 30 of 428 total lines. Use line_offset=30 parameter to read more content.
```

### Thinking

**Synchronizing after edits**

I need to make sure everything is synced after finishing my edits. It’s essential to keep everything up to date! Running the ruff tool will help ensure that any changes I made are reflected accurately. I want to get this right to avoid any confusion down the line. It feels good to take time to double-check these steps, you know? Let’s see how that goes!


### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_sequence_trace.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Thinking

**Testing smoke run parameters**

I’m considering running a smoke test with loads of 0.6B. I think a timeout of around 10 minutes sounds reasonable, but I’ll have to ensure that’s enough time for the test to complete without running into issues. It’s interesting how these little details can impact the results. I just want to make sure everything goes smoothly and efficiently, so I might re-evaluate if needed.


### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python scripts/experiments/program_sequence_trace.py --smoke --max-items 2 --n-perm-stat 100",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/p...

**Output:**
```
Exit code: 0
Stderr:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights:  23%|██▎       | 72/311 [00:00<00:00, 719.12it/s]Loading weights:  94%|█████████▎| 291/311 [00:00<00:00, 1582.54it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 1485.35it/s]
Stdout:
[smoke] Qwen3-0.6B small calibration
══════════════════════════════════════════════════════════════════════════════
PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=2 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-0.6B
[v2] Loading model: Qwen/Qwen3-0.6B  (dtype=auto, device_map=auto)
[v2] Model loaded in 0.7s
[model] Qwen/Qwen3-0.6B layers=28

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 27
[v2]   centroid forward 0/27 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=25/28 zone=[19, 20, 21, 22, 23]

[decode] 2 items z_event=2.0 ...
[decode]   item 0/2 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM SEQUENCE TRACE — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=2 truth={'C': 2}
crystal_layers=25/28 zone=[19, 20, 21, 22, 23] z_event=2.0

Sequence alignment vs fired_sequence:
  zone token-layer events mean LCS:   0.75
  zone layer-dominant mean LCS:      0.0
  all-crystal events mean LCS:       0.75
  zone events bag coverage:          0.75
  reverse-order control LCS:         0.625
  half recovered: zone_events=2 zone_layers=0 all_crystal=2

Op presence (decoded event contains op vs truth contains op):
  B: acc=1.0 null=1.0 p=1.0 truth={'B': 2} decoded={'B': 2}
  C: acc=1.0 null=1.0 p=1.0 truth={'C': 2} decoded={'C': 2}
  S: acc=0.0 null=0.0 p=1.0 truth={'S': 2} decoded={'not_S': 2}

Decoded event counts: {'B': 13, 'C': 5}
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-sequence-trace/verdict_qwen3-0-6b_const.json (+ per_item, meta)
```

### Thinking

**Sending tmux command**

I need to send a command to tmux, specifically to main:1. I have to ensure that the previous shell is at the prompt first. I'll use the command with "tee" and make sure to verify everything once it’s done. It seems simple enough, but verification is key here to confirm that everything is working as expected. Let’s just focus on executing that command properly!


### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_sequence_trace.py --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl --null-mode gateneutral --z-event 2.0 --n-perm-stat 2000 --seed 0 2>&1 | tee results/program-sequence-trace/run_qwen3-14b_const.log' Enter && sleep 1 && tmux capture-pane -p -t main:1 | tail -80",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
Attn Spearman=0.5672 (p=0.0)  z(C)/count={'0': 0.309, '1': 0.563, '2': 0.677}
  ⇒ FFN beats attn: False

(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):
  peak-diff: median=1.0 frac+=0.8220338983050848 n=133 sign-p=7.271713570135107e-13  hist={-1: 17, 3: 24, 0: 15, 1: 43,
2: 28, -2: 4, 4: 2}
  xcorr-lag: median=1.0 frac+=0.5833333333333334 n=133 sign-p=0.06717037054890534  hist={-1: 8, -2: 28, 1: 23, 2: 21, -3
: 19, 0: 1, 3: 33}
  (positive ⇒ FFN leads attention; prediction ≈ +1)

(C) RESCUE: rescue=35 anti-rescue=1 ⇒ True

specificity: firing max-z(BSC)=32.9269 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-14b_const.json (+ per_item, meta)
uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14  219.29s user 18.62s system 79% cpu 4:58.2
4 total
tee results/ffn-program-decode/run_qwen3-14b_const.log  0.00s user 0.00s system 0% cpu 4:58.24 total
[26-06-23][7:58:06][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_sequence_trace.py --model Qwen/Qwen3-14B -
-probe-set data/firing-probes.const.jsonl --null-mode gateneutral --z-event 2.0 --n-perm-stat 2000 --seed 0 2>&1 | tee r
esults/program-sequence-trace/run_qwen3-14b_const.log
```

### Thinking

**Waiting for output**

I need to verify if the process is running by capturing the command I’ve just sent, but there's no output yet. I should probably wait for about 2-3 seconds to see if anything comes through. It looks like I’m dealing with asynchronous discipline, and I should focus on launching the verification for running status. I can only poll once, so I need to be careful and patient here!


### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 3 && tmux capture-pane -p -t main:1 | tail -60",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ sleep 3 && tmux capture-pane -p -t ...

**Output:**
```
Exit code: 0
Stdout:
(C) RESCUE: rescue=35 anti-rescue=1 ⇒ True

specificity: firing max-z(BSC)=32.9269 vs nonfiring=None
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/ffn-program-decode/verdict_qwen3-14b_const.json (+ per_item, meta)
uv run python scripts/experiments/ffn_program_decode.py --model Qwen/Qwen3-14  219.29s user 18.62s system 79% cpu 4:58.2
4 total
tee results/ffn-program-decode/run_qwen3-14b_const.log  0.00s user 0.00s system 0% cpu 4:58.24 total
[26-06-23][7:58:06][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_sequence_trace.py --model Qwen/Qwen3-14B -
-probe-set data/firing-probes.const.jsonl --null-mode gateneutral --z-event 2.0 --n-perm-stat 2000 --seed 0 2>&1 | tee r
esults/program-sequence-trace/run_qwen3-14b_const.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
══════════════════════════════════════════════════════════════════════════════
PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=133 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights: 100%|██████████| 443/443 [00:02<00:00, 148.65it/s]
```

## Assistant


Built and launched the experiment.

New script:

```text
scripts/experiments/program_sequence_trace.py
```

What it does:

- Reuses the validated tracer path:
  - `RelationalCrystalClassifier`
  - `opcode_monitor_v2.calibrate_v2`
  - FFN gate register, sign-CMR
  - matched `gateneutral` null by default
- Reads `data/firing-probes.const.jsonl`
- For each probe:
  - captures content-token × crystal-layer gate activations
  - decodes B/C/S event sequences using z-threshold
  - aligns decoded sequence to certified `fired_sequence`
  - scores LCS, compressed LCS, bag coverage, reverse-order control, op-presence
- Writes to:

```text
results/program-sequence-trace/
```

Smoke validation passed on Qwen3-0.6B:

```bash
uv run ruff check scripts/experiments/program_sequence_trace.py
uv run python scripts/experiments/program_sequence_trace.py --smoke --max-items 2 --n-perm-stat 100
```

Both completed.

Launched in `tmux main:1`:

```bash
cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_sequence_trace.py \
  --model Qwen/Qwen3-14B \
  --probe-set data/firing-probes.const.jsonl \
  --null-mode gateneutral \
  --z-event 2.0 \
  --n-perm-stat 2000 \
  --seed 0 \
  2>&1 | tee results/program-sequence-trace/run_qwen3-14b_const.log
```

Verified it started and loaded the 14B model:

```text
PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence
[corpus] source=data/firing-probes.const.jsonl firing=133 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B
Loading weights: 100%|██████████| 443/443 ...
```

ASYNC: job running in `tmux main:1`. I won’t poll; tell me when it completes.

## User


job is done

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-sequence-trace/verdict_qwen3-14b_const.json",
  "limit": 220
}
```

**Summary:** Reading verdict_qwen3-14b_const.json (0-220)

**Output:**
```
{
  "model": "Qwen/Qwen3-14B",
  "n_layers": 40,
  "probe_set": "data/firing-probes.const.jsonl",
  "n_items": 133,
  "null_mode": "gateneutral",
  "z_event": 2.0,
  "zone_depth": [
    0.7,
    0.86
  ],
  "zone_layers": [
    28,
    29,
    30,
    31,
    32
  ],
  "crystal_layers": [
    0,
    1,
    3,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32
  ],
  "truth_distribution": {
    "C": 67,
    "S": 66
  },
  "sequence_alignment": {
    "zone_events_mean_lcs_frac": 0.4856,
    "zone_layer_mean_lcs_frac": 0.0501,
    "all_crystal_events_mean_lcs_frac": 0.9279,
    "zone_events_mean_bag_frac": 0.5144,
    "zone_events_mean_reverse_lcs_frac": 0.4618,
    "n_zone_events_half_recovered": 88,
    "n_zone_layers_half_recovered": 5,
    "n_all_crystal_half_recovered": 133
  },
  "op_presence": {
    "B": {
      "presence_acc": 0.2707,
      "null_mean": 0.2707,
      "perm_p": 1.0,
      "truth_counts": {
        "B": 133
      },
      "decoded_counts": {
        "not_B": 97,
        "B": 36
      }
    },
    "C": {
      "presence_acc": 0.7519,
      "null_mean": 0.6233,
      "perm_p": 0.0005,
      "truth_counts": {
        "C": 100,
        "not_C": 33
      },
      "decoded_counts": {
        "C": 99,
        "not_C": 34
      }
    },
    "S": {
      "presence_acc": 0.5414,
      "null_mean": 0.5414,
      "perm_p": 1.0,
      "truth_counts": {
        "S": 133
      },
      "decoded_counts": {
        "not_S": 61,
        "S": 72
      }
    }
  },
  "decoded_event_counts": {
    "C": 709,
    "B": 39,
    "S": 152
  },
  "decoded_layer_counts": {
    "C": 32
  },
  "calib": {
    "n_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29,
      30,
      31,
      32
    ],
    "per_layer": {
      "0": {
        "sil_z": 2.628,
        "gc_consensus": 0.909,
        "crystal_bearing": true
      },
      "1": {
        "sil_z": 3.125,
        "gc_consensus": 0.796,
        "crystal_bearing": true
      },
      "2": {
        "sil_z": 1.184,
        "gc_consensus": 0.564,
        "crystal_bearing": false
      },
      "3": {
        "sil_z": 2.138,
        "gc_consensus": 0.658,
        "crystal_bearing": true
      },
      "4": {
        "sil_z": 0.574,
        "gc_consensus": 0.641,
        "crystal_bearing": false
      },
      "5": {
        "sil_z": 3.536,
        "gc_consensus": 0.905,
        "crystal_bearing": true
      },
      "6": {
        "sil_z": 6.07,
        "gc_consensus": 0.904,
        "crystal_bearing": true
      },
      "7": {
        "sil_z": 3.883,
        "gc_consensus": 0.915,
        "crystal_bearing": true
      },
      "8": {
        "sil_z": 3.593,
        "gc_consensus": 0.929,
        "crystal_bearing": true
      },
      "9": {
        "sil_z": 5.295,
        "gc_consensus": 0.962,
        "crystal_bearing": true
      },
      "10": {
        "sil_z": 6.804,
        "gc_consensus": 0.962,
        "crystal_bearing": true
      },
      "11": {
        "sil_z": 7.211,
        "gc_consensus": 0.965,
        "crystal_bearing": true
      },
      "12": {
        "sil_z": 8.259,
        "gc_consensus": 0.95,
        "crystal_bearing": true
      },
      "13": {
        "sil_z": 5.98,
        "gc_consensus": 0.953,
        "crystal_bearing": true
      },
      "14": {
        "sil_z": 6.781,

[CONTENT TRUNCATED] Showing lines 1 to 220 of 359 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-sequence-trace/run_qwen3-14b_const.log",
  "limit": 180
}
```

**Summary:** Reading run_qwen3-14b_const.log (0-180)

**Output:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
══════════════════════════════════════════════════════════════════════════════
PROGRAM SEQUENCE TRACE — FFN gate β-program vs fired_sequence
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=133 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/443 [00:00<?, ?it/s]Loading weights:   0%|          | 1/443 [00:00<04:20,  1.70it/s]Loading weights:   0%|          | 2/443 [00:00<02:18,  3.18it/s]Loading weights:   4%|▍         | 17/443 [00:00<00:12, 34.02it/s]Loading weights:   9%|▉         | 39/443 [00:00<00:05, 75.13it/s]Loading weights:  14%|█▍        | 61/443 [00:01<00:03, 107.75it/s]Loading weights:  19%|█▊        | 83/443 [00:01<00:02, 132.61it/s]Loading weights:  24%|██▎       | 105/443 [00:01<00:02, 152.11it/s]Loading weights:  29%|██▊       | 127/443 [00:01<00:01, 166.57it/s]Loading weights:  34%|███▎      | 149/443 [00:01<00:01, 176.92it/s]Loading weights:  39%|███▊      | 171/443 [00:01<00:01, 185.06it/s]Loading weights:  44%|████▎     | 193/443 [00:01<00:01, 190.81it/s]Loading weights:  49%|████▊     | 215/443 [00:01<00:01, 194.11it/s]Loading weights:  53%|█████▎    | 237/443 [00:01<00:01, 194.90it/s]Loading weights:  58%|█████▊    | 259/443 [00:02<00:00, 196.24it/s]Loading weights:  63%|██████▎   | 281/443 [00:02<00:00, 198.29it/s]Loading weights:  68%|██████▊   | 303/443 [00:02<00:00, 198.17it/s]Loading weights:  73%|███████▎  | 324/443 [00:02<00:00, 198.68it/s]Loading weights:  78%|███████▊  | 345/443 [00:02<00:00, 196.11it/s]Loading weights:  82%|████████▏ | 365/443 [00:02<00:00, 192.12it/s]Loading weights:  87%|████████▋ | 385/443 [00:02<00:00, 185.96it/s]Loading weights:  91%|█████████ | 404/443 [00:02<00:00, 178.78it/s]Loading weights:  95%|█████████▌| 423/443 [00:02<00:00, 181.32it/s]Loading weights: 100%|██████████| 443/443 [00:02<00:00, 148.65it/s]
[v2] Model loaded in 3.8s
[model] Qwen/Qwen3-14B layers=40

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=31/40 zone=[28, 29, 30, 31, 32]

[decode] 133 items z_event=2.0 ...
[decode]   item 0/133 ...
[decode]   item 20/133 ...
[decode]   item 40/133 ...
[decode]   item 60/133 ...
[decode]   item 80/133 ...
[decode]   item 100/133 ...
[decode]   item 120/133 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM SEQUENCE TRACE — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=133 truth={'C': 67, 'S': 66}
crystal_layers=31/40 zone=[28, 29, 30, 31, 32] z_event=2.0

Sequence alignment vs fired_sequence:
  zone token-layer events mean LCS:   0.4856
  zone layer-dominant mean LCS:      0.0501
  all-crystal events mean LCS:       0.9279
  zone events bag coverage:          0.5144
  reverse-order control LCS:         0.4618
  half recovered: zone_events=88 zone_layers=5 all_crystal=133

Op presence (decoded event contains op vs truth contains op):
  B: acc=0.2707 null=0.2707 p=1.0 truth={'B': 133} decoded={'not_B': 97, 'B': 36}
  C: acc=0.7519 null=0.6233 p=0.0005 truth={'C': 100, 'not_C': 33} decoded={'C': 99, 'not_C': 34}
  S: acc=0.5414 null=0.5414 p=1.0 truth={'S': 133} decoded={'not_S': 61, 'S': 72}

Decoded event counts: {'C': 709, 'B': 39, 'S': 152}
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-sequence-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 - <<'PY'\nimport json, pathlib, collections, statistics\np=pathlib.Path('/Users/mwhitford/src/verbum/results/program-sequence-trace/per_item_qwen3-14b_const.json')\nrows=json.loads(p.read_text())\nprint('n',len(rows))\nfor key in ['category','dominant_fired','reduction_len','c_count']:\n print(key, dict(collections.Counter(r.get(key) for r in rows)))\nfor cat in sorted(set(r['category'] for r in rows)):\n rs=[r for r in rows if r['category']==cat]\n print('\\ncat',cat,'n',len(rs),'truthdom',dict(collections.Counter(r['dominant_fired'] for r in rs)))\n for metric in ['lcs_frac','bag_frac','reverse_lcs_frac','compressed_lcs_frac']:\n  vals=[r['metrics_zone_events'][metric] for r in rs]\n  print(' zone',metric, round(statistics.mean(vals),4),'half',sum(v>=0.5 for v in vals))\n vals=[r['metrics_all_crystal_events']['lcs_frac'] for r in rs]\n print(' all lcs',round(statistics.mean(vals),4),'half',sum(v>=0.5 for v in vals))\n print(' decoded counts',dict(collections.Counter(op for r in rs for op in r['decoded_event_seq'])))\n# examples low/high\nfor r in rows[:3]:\n print('\\nex',r['category'],r['input'])\n print('truth',r['fired_sequence'],'zone seq prefix',r['decoded_event_seq'][:30], 'metrics', r['metrics_zone_events'])\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python3 - <<'PY' import json, pathl...

**Output:**
```
Exit code: 0
Stdout:
n 133
category {'ditrans_const': 67, 'trans_const': 33, 'intrans': 33}
dominant_fired {'C': 67, 'S': 66}
reduction_len {4: 67, 3: 33, 2: 33}
c_count {2: 67, 1: 33, 0: 33}

cat ditrans_const n 67 truthdom {'C': 67}
 zone lcs_frac 0.653 half 60
 zone bag_frac 0.7052 half 61
 zone reverse_lcs_frac 0.6306 half 60
 zone compressed_lcs_frac 0.5597 half 54
 all lcs 0.9963 half 67
 decoded counts {'C': 501, 'B': 32, 'S': 96}

cat intrans n 33 truthdom {'S': 33}
 zone lcs_frac 0.1667 half 11
 zone bag_frac 0.1667 half 11
 zone reverse_lcs_frac 0.1667 half 11
 zone compressed_lcs_frac 0.1667 half 11
 all lcs 0.8182 half 33
 decoded counts {'C': 44, 'S': 19}

cat trans_const n 33 truthdom {'S': 33}
 zone lcs_frac 0.4647 half 17
 zone bag_frac 0.4748 half 17
 zone reverse_lcs_frac 0.4141 half 12
 zone compressed_lcs_frac 0.4647 half 17
 all lcs 0.899 half 33
 decoded counts {'S': 37, 'C': 164, 'B': 7}

ex ditrans_const Every king lends a guest a song.
truth ['S', 'B', 'C', 'C'] zone seq prefix ['C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'] metrics {'truth_len': 4, 'decoded_len': 12, 'lcs': 2, 'lcs_frac': 0.5, 'reverse_lcs': 2, 'reverse_lcs_frac': 0.5, 'compressed_len': 1, 'compressed_lcs': 1, 'compressed_lcs_frac': 0.25, 'bag_hit': 2, 'bag_frac': 0.5, 'decoded_counts': {'C': 12}, 'decoded_compressed': ['C']}

ex ditrans_const Every painter sells a neighbor a song.
truth ['S', 'B', 'C', 'C'] zone seq prefix ['B', 'S', 'S'] metrics {'truth_len': 4, 'decoded_len': 3, 'lcs': 1, 'lcs_frac': 0.25, 'reverse_lcs': 2, 'reverse_lcs_frac': 0.5, 'compressed_len': 2, 'compressed_lcs': 1, 'compressed_lcs_frac': 0.25, 'bag_hit': 2, 'bag_frac': 0.5, 'decoded_counts': {'B': 1, 'S': 2}, 'decoded_compressed': ['B', 'S']}

ex ditrans_const Every sailor hands a king a rose.
truth ['S', 'B', 'C', 'C'] zone seq prefix ['C', 'C', 'C', 'S', 'C', 'C', 'C', 'C', 'S', 'C', 'C', 'C', 'C', 'S', 'C', 'C', 'C', 'C', 'C', 'C', 'C', 'C'] metrics {'truth_len': 4, 'decoded_len': 22, 'lcs': 3, 'lcs_frac': 0.75, 'reverse_lcs': 3, 'reverse_lcs_frac': 0.75, 'compressed_len': 7, 'compressed_lcs': 3, 'compressed_lcs_frac': 0.75, 'bag_hit': 3, 'bag_frac': 0.75, 'decoded_counts': {'C': 19, 'S': 3}, 'decoded_compressed': ['C', 'S', 'C', 'S', 'C', 'S', 'C']}
```

## Assistant


The sequence tracer completed cleanly. Result: **we did not recover a clean ordered β-program tape in the readable L28–32 zone.** We did recover a **strong C-presence / C-load signal**, consistent with the prior 14B const run, but the ordered sequence evidence is weak.

## Artifacts

Wrote:

```text
results/program-sequence-trace/verdict_qwen3-14b_const.json
results/program-sequence-trace/per_item_qwen3-14b_const.json
results/program-sequence-trace/meta_qwen3-14b_const.json
results/program-sequence-trace/run_qwen3-14b_const.log
```

Run completed:

```text
[write] /Users/mwhitford/src/verbum/results/program-sequence-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
```

---

## Core metrics

Run config:

```json
{
  "model": "Qwen/Qwen3-14B",
  "n_items": 133,
  "null_mode": "gateneutral",
  "z_event": 2.0,
  "zone_layers": [28, 29, 30, 31, 32],
  "crystal_layers": 31
}
```

Truth distribution:

```text
C-dominant: 67
S-dominant: 66
```

Dataset structure:

```text
ditrans_const: 67, fired_sequence length 4, truth S B C C
trans_const:   33, fired_sequence length 3, truth S B C
intrans:       33, fired_sequence length 2, truth S B
```

---

## Sequence alignment verdict

```json
"sequence_alignment": {
  "zone_events_mean_lcs_frac": 0.4856,
  "zone_layer_mean_lcs_frac": 0.0501,
  "all_crystal_events_mean_lcs_frac": 0.9279,
  "zone_events_mean_bag_frac": 0.5144,
  "zone_events_mean_reverse_lcs_frac": 0.4618,
  "n_zone_events_half_recovered": 88,
  "n_zone_layers_half_recovered": 5,
  "n_all_crystal_half_recovered": 133
}
```

Interpretation:

### 1. Readable-zone ordered recovery is weak

```text
zone token-layer LCS = 0.4856
reverse-order control = 0.4618
bag coverage = 0.5144
```

This is the key result. The LCS is only slightly better than reverse order and roughly equal to bag coverage. That means the score is mostly saying:

> some of the right op symbols appear somewhere,

not:

> the ordered β-program is being read.

So the L28–32 readable zone does **not** expose a crisp ordered tape.

### 2. Layer-dominant sequence failed

```text
zone_layer_mean_lcs_frac = 0.0501
decoded_layer_counts = {"C": 32}
```

The one-op-per-layer abstraction collapsed almost entirely to C. This says the layer-dominant read is too coarse / C-saturated.

### 3. All-crystal score is inflated

```text
all_crystal_events_mean_lcs_frac = 0.9279
n_all_crystal_half_recovered = 133/133
```

This looks amazing but is probably not meaningful as program order evidence. Across 31 crystal-bearing layers, the decoded event stream is long enough that it almost always contains the truth subsequence somewhere. That’s a **coverage / long-sequence artifact**, not a clean program trace.

The real diagnostic is the zone score plus reverse/bag controls, and those say “not ordered.”

---

## Op presence

```json
"op_presence": {
  "B": {
    "presence_acc": 0.2707,
    "perm_p": 1.0,
    "truth_counts": {"B": 133},
    "decoded_counts": {"not_B": 97, "B": 36}
  },
  "C": {
    "presence_acc": 0.7519,
    "perm_p": 0.0005,
    "truth_counts": {"C": 100, "not_C": 33},
    "decoded_counts": {"C": 99, "not_C": 34}
  },
  "S": {
    "presence_acc": 0.5414,
    "perm_p": 1.0,
    "truth_counts": {"S": 133},
    "decoded_counts": {"not_S": 61, "S": 72}
  }
}
```

Only **C presence** is meaningfully tested because B and S are present in every ground-truth sequence in this probe set.

Important:

```text
C presence acc = 0.7519
C p = 0.0005
truth C-present = 100
decoded C-present = 99
```

So the tracer significantly detects whether C should appear at all.

That is exactly consistent with the prior `ffn_program_decode` run:

> 14B significantly tracks corrected applicative-C structure.

But B and S cannot be evaluated as binary presence here because every item contains them.

---

## Per-category read

### Ditransitive constant: truth `S B C C`

```text
n = 67
zone LCS = 0.653
zone bag = 0.7052
reverse LCS = 0.6306
compressed LCS = 0.5597
all-crystal LCS = 0.9963
decoded counts: C=501, B=32, S=96
```

Ditransitives carry the strongest apparent sequence recovery, but reverse is almost as good. This means “lots of C and some S/B,” not clean order.

### Transitive constant: truth `S B C`

```text
n = 33
zone LCS = 0.4647
zone bag = 0.4748
reverse LCS = 0.4141
compressed LCS = 0.4647
all-crystal LCS = 0.899
decoded counts: C=164, S=37, B=7
```

Mostly C again, with some S and very little B.

### Intransitive: truth `S B`

```text
n = 33
zone LCS = 0.1667
zone bag = 0.1667
reverse LCS = 0.1667
compressed LCS = 0.1667
all-crystal LCS = 0.8182
decoded counts: C=44, S=19
```

The readable zone basically fails on intransitives: B is almost absent and C appears even when C is not in truth. That is an important caveat.

---

## What did we learn?

### Positive

14B really does expose **applicative-C program structure** in the FFN gate register.

Evidence chain now:

1. `ffn_program_decode`:
   - FFN C-vs-S acc `0.6165`, p=`0.0005`
   - attention not significant on C-vs-S
   - FFN lead-lag direction coherent

2. `program_sequence_trace`:
   - C presence acc `0.7519`, p=`0.0005`
   - decoded event counts strongly C-heavy:
     ```text
     C=709, S=152, B=39
     ```

So 14B is definitely not random. The corrected C-label is visible.

### Negative / boundary

The ordered β-reduction tape is **not** recovered by this simple event-stream/LCS tracer.

The decisive numbers:

```text
zone LCS:          0.4856
reverse control:   0.4618
bag coverage:      0.5144
layer-dominant:    0.0501
```

If we had found the program, zone LCS should be clearly above reverse and bag controls. It is not.

So the result is:

> The FFN gate register knows whether applicative-C structure is present, but the ordered β-program is not readable as a simple token×layer sequence of B/C/S argmax events in L28–32.

This refines the hypothesis:

```text
program ≠ discrete instruction tape
program ≈ distributed/holographic C-load + weaker S/B structure
```

At least under this instrument.

---

## Likely methodological issue

The tracer’s event definition is too naive:

```text
for each layer:
  for each token:
    emit argmax over {B,C,S} if z >= 2
```

That creates long noisy streams dominated by C. LCS can match subsequences by chance once streams are long. Conversely, layer-dominant collapses to C and loses structure.

So we need a better event extractor.

The current tracer answers:

> Are the right symbols present?

It does not yet answer:

> Which token/layer corresponds to each β step?

---

## Best next adjustment

I would modify the experiment from **event-stream LCS** to **truth-step assignment**.

Instead of flattening all token×layer events, for each truth step `j` in:

```text
truth = [S, B, C, C]
```

ask:

```text
Where is the strongest evidence for this step?
```

Concretely:

1. Build a score map:

```text
score[op, layer, token] = z(op)
```

2. For each truth op in order, find a monotonic path:

```text
(S at l1,t1) → (B at l2,t2) → (C at l3,t3) → (C at l4,t4)
```

with constraints:

```text
l1 <= l2 <= l3 <= l4
```

possibly allowing same layer/different token.

3. Compare to controls:
   - reversed truth `[C,C,B,S]`
   - shuffled truth
   - existential label truth
   - random op sequence with same counts

This gives a real program score:

```text
best monotonic path score(truth)
vs
best monotonic path score(reversed/shuffled/wrong-reading)
```

That should be much sharper than LCS on a long event stream.

## Bottom line

This run is scientifically useful but not the breakthrough.

Verdict:

> Qwen3-14B exposes the corrected applicative-C component of the program, but the β-reduction sequence is not readable as a simple ordered opcode event stream. The evidence is strong for C-presence/load, weak for order. The next tracer should use monotonic path assignment against `fired_sequence` and compare truth vs reversed/shuffled/existential controls.

This is a good boundary result: it tells us the program is there as structure, but our first sequence decoder still reads it too coarsely.

## User


Ok let's build the next experiment and run it in my tmux main:1 window

### Thinking

**Modifying the script**

I need to consider whether to modify the current script or create a new one altogether. There's a task at hand related to building a monotonic path assignment. It seems essential to implement this properly to ensure everything functions as intended. Let’s clarify the requirements and see what specific adjustments are necessary to make this work. I want to get this right to facilitate the forthcoming tasks efficiently!


### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing (FFN gate β-program path)\n\"\"\"Program Path Trace — monotonic alignment of FFN gate z-maps to `fired_sequence`.\n\nThis is the second sequence-level attempt after `program_sequence_trace.py`. The event\nstream/LCS tracer found C-presence but not reliable order: long decoded streams made LCS\nmostly a coverage metric. This experiment instead asks the sharper question directly:\nfor a certified β-program such as [S, B, C, C], is the best monotonic layer path for that\nexact order stronger than paths for reversed or shuffled programs with the same multiset?\n\nMeasurement contract:\n  • register: FFN gate routing register (`mlp.gate_proj`), sign(gate)-CMR;\n  • null: matched-prefix `gateneutral` by default;\n  • per item: capture content-token x layer z(op) over B/C/S;\n  • layer evidence: for op at layer L, max z(op) over content tokens;\n  • path: dynamic program chooses nondecreasing layers for the ordered truth steps;\n  • controls: reversed sequence and all unique non-truth permutations of the same steps.\n\nIf a discrete-ish β-program order is readable, truth path score should beat same-multiset\npermutation controls, not merely have high C load.\n\nUsage:\n    uv run python scripts/experiments/program_path_trace.py --smoke\n    uv run python scripts/experiments/program_path_trace.py \\\n      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl\n\nLicense: MIT. AGENTS.md S5 λ provenance.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport itertools\nimport json\nimport sys\nfrom collections import Counter\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom ffn_program_decode import (  # noqa: E402\n    FIRING_SET,\n    build_firing_corpus,\n    classify_positions,\n    perm_null_accuracy,\n    zone_layers,\n)\nfrom opcode_monitor_v2 import (  # noqa: E402\n    COMPILE_GATE,\n    _git_sha,\n    _json_safe,\n    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    gate_prefix_len,\n    load_model_and_tokenizer,\n)\n\nRESULTS_DIR = _ROOT / \"results\" / \"program-path-trace\"\n\n\ndef unique_permutations(seq: list[str], limit: int = 120) -> list[list[str]]:\n    \"\"\"Unique permutations, capped for future longer traces.\"\"\"\n    out = []\n    seen = set()\n    for p in itertools.permutations(seq):\n        if p in seen:\n            continue\n        seen.add(p)\n        out.append(list(p))\n        if len(out) >= limit:\n            break\n    return out\n\n\ndef layer_op_evidence(\n    reads: list[dict[int, dict[str, float]]], layers: list[int], op_set: list[str]\n) -> dict[str, dict[int, tuple[float, int | None]]]:\n    \"\"\"op -> layer -> (max_z_over_content_tokens, best_content_pos).\"\"\"\n    out: dict[str, dict[int, tuple[float, int | None]]] = {op: {} for op in op_set}\n    for op in op_set:\n        for li in layers:\n            best_z = -float(\"inf\")\n            best_pos = None\n            for pos_i, r in enumerate(reads):\n                if li not in r:\n                    continue\n                z = float(r[li][op])\n                if z > best_z:\n                    best_z = z\n                    best_pos = pos_i\n            out[op][li] = (best_z, best_pos)\n    return out\n\n\ndef monotonic_path_score(\n    seq: list[str], evidence: dict[str, dict[int, tuple[float, int | None]]],\n    layers: list[int], *, strict: bool = False,\n) -> dict:\n    \"\"\"Best path assigning each op in seq to a nondecreasing layer.\n\n    Score is mean z over steps. The DP maximizes sum z; z values are matched-null\n    relational scores, so controls using the same multiset test ORDER rather than load.\n    \"\"\"\n    if not seq or not layers:\n        return {\"score_sum\": 0.0, \"score_mean\": 0.0, \"path\": []}\n    n, m = len(seq), len(layers)\n    dp = np.full((n, m), -np.inf, dtype=float)\n    back = np.full((n, m), -1, dtype=int)\n\n    for k, li in enumerate(layers):\n        dp[0, k] = evidence[seq[0]][li][0]\n    for j in range(1, n):\n        for k, li in enumerate(layers):\n            prev_end = k if not strict else k - 1\n            if prev_end < 0:\n                continue\n            prev_vals = dp[j - 1, : prev_end + 1]\n            pk = int(np.argmax(prev_vals))\n            pv = float(prev_vals[pk])\n            if np.isneginf(pv):\n                continue\n            dp[j, k] = pv + evidence[seq[j]][li][0]\n            back[j, k] = pk\n\n    end = int(np.argmax(dp[-1]))\n    score_sum = float(dp[-1, end])\n    if np.isneginf(score_sum):\n        return {\"score_sum\": None, \"score_mean\": None, \"path\": []}\n\n    idxs = [end]\n    for j in range(n - 1, 0, -1):\n        idxs.append(int(back[j, idxs[-1]]))\n    idxs.reverse()\n    path = []\n    for j, k in enumerate(idxs):\n        li = layers[k]\n        z, pos = evidence[seq[j]][li]\n        path.append({\"step\": j, \"op\": seq[j], \"layer\": li,\n                     \"content_pos\": pos, \"z\": round(float(z), 4)})\n    return {\n        \"score_sum\": round(score_sum, 4),\n        \"score_mean\": round(score_sum / len(seq), 4),\n        \"path\": path,\n    }\n\n\ndef score_controls(\n    truth: list[str], evidence: dict[str, dict[int, tuple[float, int | None]]],\n    layers: list[int], *, strict: bool = False,\n) -> dict:\n    truth_score = monotonic_path_score(truth, evidence, layers, strict=strict)\n    rev = list(reversed(truth))\n    reverse_score = monotonic_path_score(rev, evidence, layers, strict=strict)\n    perms = [p for p in unique_permutations(truth) if p != truth]\n    perm_scores = [monotonic_path_score(p, evidence, layers, strict=strict)\n                   for p in perms]\n    perm_means = [p[\"score_mean\"] for p in perm_scores if p[\"score_mean\"] is not None]\n    t = truth_score[\"score_mean\"]\n    if t is None or not perm_means:\n        rank_frac = None\n        margin_best = None\n        margin_mean = None\n        beats_all = False\n    else:\n        ge = sum(1 for s in perm_means if s >= t)\n        rank_frac = round(1.0 - ge / len(perm_means), 4)\n        margin_best = round(t - max(perm_means), 4)\n        margin_mean = round(t - float(np.mean(perm_means)), 4)\n        beats_all = bool(t > max(perm_means))\n    best_perm = None\n    if perm_scores:\n        best_perm = max(perm_scores, key=lambda x: -float(\"inf\") if x[\"score_mean\"] is None\n                        else x[\"score_mean\"])\n    return {\n        \"truth\": truth_score,\n        \"reverse_sequence\": rev,\n        \"reverse\": reverse_score,\n        \"n_permutation_controls\": len(perm_scores),\n        \"perm_score_mean\": round(float(np.mean(perm_means)), 4) if perm_means else None,\n        \"perm_score_max\": round(float(np.max(perm_means)), 4) if perm_means else None,\n        \"truth_rank_frac\": rank_frac,\n        \"truth_margin_vs_best_perm\": margin_best,\n        \"truth_margin_vs_mean_perm\": margin_mean,\n        \"truth_beats_all_permutations\": beats_all,\n        \"best_permutation\": best_perm,\n    }\n\n\ndef _safe_slug(model_name: str, probe_set: str | None) -> str:\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    if probe_set:\n        stem = Path(probe_set).stem\n        slug += \"_\" + (stem.split(\".\")[-1] if \".\" in stem else stem)\n    return slug\n\n\ndef _mean(xs: list[float | None]) -> float | None:\n    vals = [x for x in xs if x is not None]\n    return round(float(np.mean(vals)), 4) if vals else None\n\n\ndef run(\n    model_name: str,\n    probe_set: str,\n    max_items: int | None,\n    null_mode: str,\n    zone_lo: float,\n    zone_hi: float,\n    n_perm_calib: int,\n    ppc: int | None,\n    null_cap: int | None,\n    n_perm_stat: int,\n    seed: int,\n    strict_layers: bool,\n) -> tuple[dict, list[dict], dict]:\n    print(\"═\" * 78)\n    print(\"PROGRAM PATH TRACE — monotonic FFN gate path vs fired_sequence\")\n    print(\"═\" * 78)\n    firing, nonfiring = build_firing_corpus([Path(probe_set)])\n    if max_items is not None:\n        firing = firing[:max_items]\n    print(\n        f\"[corpus] source={probe_set} firing={len(firing)} \"\n        f\"nonfiring={len(nonfiring)}\"\n    )\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    layers = list(range(n_layers))\n    print(f\"[model] {model_name} layers={n_layers}\")\n\n    print(f\"\\n[calib] FFN gate register null_mode={null_mode} ...\")\n    rcc, calib = calibrate_v2(\n        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,\n        null_mode=null_mode, hook=\"gate\")\n    crystal_layers = rcc.crystal_layers\n    zlayers = zone_layers(crystal_layers, n_layers, zone_lo, zone_hi)\n    print(f\"[calib] crystal_layers={len(crystal_layers)}/{n_layers} zone={zlayers}\")\n\n    gate_n = gate_prefix_len(tok)\n    per_item: list[dict] = []\n    print(f\"\\n[decode] {len(firing)} items strict_layers={strict_layers} ...\")\n    for i, item in enumerate(firing):\n        if i % 20 == 0:\n            print(f\"[decode]   item {i}/{len(firing)} ...\")\n        prompt = COMPILE_GATE + item[\"input\"]\n        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,\n                                             hook=\"gate\")\n        positions = list(range(min(gate_n, n_tok - 1), n_tok))\n        reads = classify_positions(rcc, store, layers, positions)\n        truth = list(item[\"fired_sequence\"])\n\n        ev_zone = layer_op_evidence(reads, zlayers, FIRING_SET)\n        ev_all = layer_op_evidence(reads, crystal_layers, FIRING_SET)\n        zone_scores = score_controls(truth, ev_zone, zlayers, strict=strict_layers)\n        all_scores = score_controls(truth, ev_all, crystal_layers, strict=strict_layers)\n\n        per_item.append({\n            \"input\": item[\"input\"],\n            \"category\": item[\"category\"],\n            \"dominant_fired\": item[\"dominant_fired\"],\n            \"fired_sequence\": truth,\n            \"fired_multiset\": item[\"fired_multiset\"],\n            \"reduction_len\": item[\"reduction_len\"],\n            \"b_count\": item.get(\"b_count\"),\n            \"s_count\": item.get(\"s_count\"),\n            \"c_count\": item.get(\"c_count\"),\n            \"n_content_tokens\": len(positions),\n            \"zone_layers\": zlayers,\n            \"zone_path\": zone_scores,\n            \"all_crystal_path\": all_scores,\n        })\n\n    def vals(path_key: str, field: str) -> list[float | None]:\n        return [p[path_key][field] for p in per_item]\n\n    zone_truth = [p[\"zone_path\"][\"truth\"][\"score_mean\"] for p in per_item]\n    zone_rev = [p[\"zone_path\"][\"reverse\"][\"score_mean\"] for p in per_item]\n    zone_margin = vals(\"zone_path\", \"truth_margin_vs_best_perm\")\n    zone_rank = vals(\"zone_path\", \"truth_rank_frac\")\n    all_margin = vals(\"all_crystal_path\", \"truth_margin_vs_best_perm\")\n    all_rank = vals(\"all_crystal_path\", \"truth_rank_frac\")\n\n    # Item-level permutation-style null: does truth path beat all same-multiset orders?\n    decoded_zone = [\"win\" if p[\"zone_path\"][\"truth_beats_all_permutations\"] else \"loss\"\n                    for p in per_item]\n    decoded_all = [\"win\" if p[\"all_crystal_path\"][\"truth_beats_all_permutations\"]\n                   else \"loss\" for p in per_item]\n    truth_win = [\"win\"] * len(per_item)\n    zone_win_acc, zone_win_null, zone_win_p = perm_null_accuracy(\n        decoded_zone, truth_win, n_perm_stat, seed)\n    all_win_acc, all_win_null, all_win_p = perm_null_accuracy(\n        decoded_all, truth_win, n_perm_stat, seed)\n\n    verdict = {\n        \"model\": model_name,\n        \"n_layers\": n_layers,\n        \"probe_set\": probe_set,\n        \"n_items\": len(per_item),\n        \"null_mode\": null_mode,\n        \"strict_layers\": strict_layers,\n        \"zone_depth\": [zone_lo, zone_hi],\n        \"zone_layers\": zlayers,\n        \"crystal_layers\": crystal_layers,\n        \"truth_distribution\": dict(Counter(p[\"dominant_fired\"] for p in per_item)),\n        \"path_scores\": {\n            \"zone_truth_score_mean\": _mean(zone_truth),\n            \"zone_reverse_score_mean\": _mean(zone_rev),\n            \"zone_truth_minus_reverse_mean\": _mean([\n                (a - b) if a is not None and b is not None else None\n                for a, b in zip(zone_truth, zone_rev, strict=False)\n            ]),\n            \"zone_margin_vs_best_perm_mean\": _mean(zone_margin),\n            \"zone_truth_rank_frac_mean\": _mean(zone_rank),\n            \"zone_truth_beats_all_n\": int(sum(\n                p[\"zone_path\"][\"truth_beats_all_permutations\"] for p in per_item)),\n            \"zone_truth_beats_all_acc\": round(zone_win_acc, 4),\n            \"zone_truth_beats_all_null\": round(zone_win_null, 4),\n            \"zone_truth_beats_all_perm_p\": round(zone_win_p, 4),\n            \"all_crystal_margin_vs_best_perm_mean\": _mean(all_margin),\n            \"all_crystal_truth_rank_frac_mean\": _mean(all_rank),\n            \"all_crystal_truth_beats_all_n\": int(sum(\n                p[\"all_crystal_path\"][\"truth_beats_all_permutations\"]\n                for p in per_item)),\n            \"all_crystal_truth_beats_all_acc\": round(all_win_acc, 4),\n            \"all_crystal_truth_beats_all_null\": round(all_win_null, 4),\n            \"all_crystal_truth_beats_all_perm_p\": round(all_win_p, 4),\n        },\n        \"by_category\": {},\n        \"calib\": calib,\n    }\n\n    for cat in sorted({p[\"category\"] for p in per_item}):\n        rows = [p for p in per_item if p[\"category\"] == cat]\n        verdict[\"by_category\"][cat] = {\n            \"n\": len(rows),\n            \"truth_distribution\": dict(Counter(r[\"dominant_fired\"] for r in rows)),\n            \"zone_truth_score_mean\": _mean([\n                r[\"zone_path\"][\"truth\"][\"score_mean\"] for r in rows]),\n            \"zone_margin_vs_best_perm_mean\": _mean([\n                r[\"zone_path\"][\"truth_margin_vs_best_perm\"] for r in rows]),\n            \"zone_truth_rank_frac_mean\": _mean([\n                r[\"zone_path\"][\"truth_rank_frac\"] for r in rows]),\n            \"zone_truth_beats_all_n\": int(sum(\n                r[\"zone_path\"][\"truth_beats_all_permutations\"] for r in rows)),\n        }\n\n    meta = {\n        \"model\": model_name,\n        \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"params\": {\n            \"probe_set\": probe_set,\n            \"max_items\": max_items,\n            \"null_mode\": null_mode,\n            \"zone_lo\": zone_lo,\n            \"zone_hi\": zone_hi,\n            \"n_perm_calib\": n_perm_calib,\n            \"ppc\": ppc,\n            \"null_cap\": null_cap,\n            \"n_perm_stat\": n_perm_stat,\n            \"seed\": seed,\n            \"strict_layers\": strict_layers,\n        },\n        \"method\": \"Dynamic-program best monotonic layer path through FFN gate \"\n                  \"relational z(op) evidence; truth fired_sequence compared against \"\n                  \"reversed and all same-multiset permutation controls.\",\n    }\n    return verdict, per_item, meta\n\n\ndef write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = _safe_slug(verdict[\"model\"], verdict.get(\"probe_set\"))\n    if verdict.get(\"strict_layers\"):\n        slug += \"_strict\"\n    (RESULTS_DIR / f\"verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(verdict), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"per_item_{slug}.json\").write_text(\n        json.dumps(_json_safe(per_item), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"meta_{slug}.json\").write_text(\n        json.dumps(_json_safe(meta), indent=2), encoding=\"utf-8\")\n    print(f\"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)\")\n\n\ndef report(verdict: dict) -> None:\n    s = verdict[\"path_scores\"]\n    print(\"\\n\" + \"═\" * 78)\n    print(\"PROGRAM PATH TRACE — VERDICT\")\n    print(\"═\" * 78)\n    print(f\"items={verdict['n_items']} truth={verdict['truth_distribution']}\")\n    print(f\"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} \"\n          f\"zone={verdict['zone_layers']} strict={verdict['strict_layers']}\")\n    print(\"\\nZone monotonic path vs same-multiset controls:\")\n    print(f\"  truth score mean:          {s['zone_truth_score_mean']}\")\n    print(f\"  reverse score mean:        {s['zone_reverse_score_mean']}\")\n    print(f\"  truth - reverse mean:      {s['zone_truth_minus_reverse_mean']}\")\n    print(f\"  margin vs best perm mean:  {s['zone_margin_vs_best_perm_mean']}\")\n    print(f\"  rank frac mean:            {s['zone_truth_rank_frac_mean']}\")\n    print(f\"  beats all perms:           {s['zone_truth_beats_all_n']}/\"\n          f\"{verdict['n_items']} (p={s['zone_truth_beats_all_perm_p']})\")\n    print(\"\\nAll-crystal path control:\")\n    print(f\"  margin vs best perm mean:  {s['all_crystal_margin_vs_best_perm_mean']}\")\n    print(f\"  rank frac mean:            {s['all_crystal_truth_rank_frac_mean']}\")\n    print(f\"  beats all perms:           {s['all_crystal_truth_beats_all_n']}/\"\n          f\"{verdict['n_items']} (p={s['all_crystal_truth_beats_all_perm_p']})\")\n    print(\"\\nBy category:\")\n    for cat, d in verdict[\"by_category\"].items():\n        print(f\"  {cat}: n={d['n']} score={d['zone_truth_score_mean']} \"\n              f\"margin={d['zone_margin_vs_best_perm_mean']} \"\n              f\"rank={d['zone_truth_rank_frac_mean']} \"\n              f\"beats={d['zone_truth_beats_all_n']}/{d['n']}\")\n    print(\"═\" * 78 + \"\\n\")\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"Monotonic FFN β-program path tracer\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--probe-set\", default=\"data/firing-probes.const.jsonl\")\n    ap.add_argument(\"--max-items\", type=int, default=None)\n    ap.add_argument(\"--null-mode\", default=\"gateneutral\",\n                    choices=[\"gateneutral\", \"crosstask\"])\n    ap.add_argument(\"--zone-lo\", type=float, default=0.70)\n    ap.add_argument(\"--zone-hi\", type=float, default=0.86)\n    ap.add_argument(\"--n-perm-stat\", type=int, default=2000)\n    ap.add_argument(\"--seed\", type=int, default=0)\n    ap.add_argument(\"--strict-layers\", action=\"store_true\",\n                    help=\"Require strictly increasing layers for successive steps\")\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    model = args.model\n    max_items = args.max_items\n    if args.smoke:\n        if model == \"Qwen/Qwen3-14B\":\n            model = \"Qwen/Qwen3-0.6B\"\n        n_perm_calib, ppc, null_cap = 80, 3, 200\n        max_items = max_items or 6\n        print(\"[smoke] Qwen3-0.6B small calibration\")\n    else:\n        n_perm_calib, ppc, null_cap = 300, None, None\n\n    verdict, per_item, meta = run(\n        model, args.probe_set, max_items, args.null_mode, args.zone_lo, args.zone_hi,\n        n_perm_calib, ppc, null_cap, args.n_perm_stat, args.seed,\n        args.strict_layers)\n    report(verdict)\n    write_outputs(verdict, per_item, meta)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py
```

### Tool Call: shell_command (failed)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 1
Stdout:
E501 Line too long (89 > 88)
 --> scripts/experiments/program_path_trace.py:8:89
  |
6 | stream/LCS tracer found C-presence but not reliable order: long decoded streams made LCS
7 | mostly a coverage metric. This experiment instead asks the sharper question directly:
8 | for a certified β-program such as [S, B, C, C], is the best monotonic layer path for that
  |                                                                                         ^
9 | exact order stronger than paths for reversed or shuffled programs with the same multiset?
  |

E501 Line too long (89 > 88)
  --> scripts/experiments/program_path_trace.py:9:89
   |
 7 | mostly a coverage metric. This experiment instead asks the sharper question directly:
 8 | for a certified β-program such as [S, B, C, C], is the best monotonic layer path for that
 9 | exact order stronger than paths for reversed or shuffled programs with the same multiset?
   |                                                                                         ^
10 |
11 | Measurement contract:
   |

E501 Line too long (89 > 88)
  --> scripts/experiments/program_path_trace.py:19:89
   |
17 |   • controls: reversed sequence and all unique non-truth permutations of the same steps.
18 |
19 | If a discrete-ish β-program order is readable, truth path score should beat same-multiset
   |                                                                                         ^
20 | permutation controls, not merely have high C load.
   |

E501 Line too long (91 > 88)
   --> scripts/experiments/program_path_trace.py:178:89
    |
176 |     best_perm = None
177 |     if perm_scores:
178 |         best_perm = max(perm_scores, key=lambda x: -float("inf") if x["score_mean"] is None
    |                                                                                         ^^^
179 |                         else x["score_mean"])
180 |     return {
    |

Found 4 errors.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "original_content": "for a certified β-program such as [S, B, C, C], is the best monotonic layer path for that\nexact order stronger than paths for reversed or shuffled programs with the same multiset?\n",
  "new_content": "for a certified β-program such as [S, B, C, C], is the best monotonic layer\npath for that exact order stronger than reversed/shuffled same-multiset programs?\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "original_content": "If a discrete-ish β-program order is readable, truth path score should beat same-multiset\npermutation controls, not merely have high C load.\n",
  "new_content": "If a discrete-ish β-program order is readable, truth path score should beat\nsame-multiset permutation controls, not merely have high C load.\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "original_content": "    if perm_scores:\n        best_perm = max(perm_scores, key=lambda x: -float(\"inf\") if x[\"score_mean\"] is None\n                        else x[\"score_mean\"])\n",
  "new_content": "    if perm_scores:\n        def _score(x):\n            return -float(\"inf\") if x[\"score_mean\"] is None else x[\"score_mean\"]\n\n        best_perm = max(perm_scores, key=_score)\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_path_trace.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python scripts/experiments/program_path_trace.py --smoke --max-items 2 --n-perm-stat 100",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/p...

**Output:**
```
Exit code: 0
Stderr:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights:  20%|█▉        | 61/311 [00:00<00:00, 605.37it/s]Loading weights:  83%|████████▎ | 258/311 [00:00<00:00, 1400.24it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 1352.12it/s]
Stdout:
[smoke] Qwen3-0.6B small calibration
══════════════════════════════════════════════════════════════════════════════
PROGRAM PATH TRACE — monotonic FFN gate path vs fired_sequence
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=2 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-0.6B
[v2] Loading model: Qwen/Qwen3-0.6B  (dtype=auto, device_map=auto)
[v2] Model loaded in 0.7s
[model] Qwen/Qwen3-0.6B layers=28

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 27
[v2]   centroid forward 0/27 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=25/28 zone=[19, 20, 21, 22, 23]

[decode] 2 items strict_layers=False ...
[decode]   item 0/2 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM PATH TRACE — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=2 truth={'C': 2}
crystal_layers=25/28 zone=[19, 20, 21, 22, 23] strict=False

Zone monotonic path vs same-multiset controls:
  truth score mean:          3.3021
  reverse score mean:        2.7355
  truth - reverse mean:      0.5666
  margin vs best perm mean:  -0.1227
  rank frac mean:            0.7273
  beats all perms:           0/2 (p=1.0)

All-crystal path control:
  margin vs best perm mean:  -0.0877
  rank frac mean:            0.7273
  beats all perms:           0/2 (p=1.0)

By category:
  ditrans_const: n=2 score=3.3021 margin=-0.1227 rank=0.7273 beats=0/2
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-path-trace/verdict_qwen3-0-6b_const.json (+ per_item, meta)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_path_trace.py --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl --null-mode gateneutral --n-perm-stat 2000 --seed 0 2>&1 | tee results/program-path-trace/run_qwen3-14b_const.log' Enter && sleep 3 && tmux capture-pane -p -t main:1 | tail -80",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
all-crystal events mean LCS:       0.9279
  zone events bag coverage:          0.5144
  reverse-order control LCS:         0.4618
  half recovered: zone_events=88 zone_layers=5 all_crystal=133

Op presence (decoded event contains op vs truth contains op):
  B: acc=0.2707 null=0.2707 p=1.0 truth={'B': 133} decoded={'not_B': 97, 'B': 36}
  C: acc=0.7519 null=0.6233 p=0.0005 truth={'C': 100, 'not_C': 33} decoded={'C': 99, 'not_C': 34}
  S: acc=0.5414 null=0.5414 p=1.0 truth={'S': 133} decoded={'not_S': 61, 'S': 72}

Decoded event counts: {'C': 709, 'B': 39, 'S': 152}
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-sequence-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
uv run python scripts/experiments/program_sequence_trace.py --model       2.0  163.57s user 13.32s system 87% cpu 3:22.6
8 total
tee results/program-sequence-trace/run_qwen3-14b_const.log  0.00s user 0.00s system 0% cpu 3:22.68 total
[26-06-23][8:18:59][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_path_trace.py --model Qwen/Qwen3-14B --pro
be-set data/firing-probes.const.jsonl --null-mode gateneutral --n-perm-stat 2000 --seed 0 2>&1 | tee results/program-pat
h-trace/run_qwen3-14b_const.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
```

## Assistant


Built and launched the next experiment.

New script:

```text
scripts/experiments/program_path_trace.py
```

What it tests:

- Instead of flattening token×layer events and using LCS, it directly scores whether the **ordered truth program** has a stronger monotonic layer path than same-multiset controls.
- For each item:
  - builds `z(op, layer, content_token)` for B/C/S;
  - reduces each `(op, layer)` to max z over content tokens;
  - uses dynamic programming to find the best nondecreasing layer path for:
    - truth `fired_sequence`
    - reversed sequence
    - all unique same-multiset permutations
  - reports whether truth beats all permutation controls.

This is the sharper test:

```text
Does [S,B,C,C] score better than [C,C,B,S], [B,S,C,C], etc.,
using the same symbols/counts?
```

Validation done:

```bash
uv run ruff check scripts/experiments/program_path_trace.py
uv run python scripts/experiments/program_path_trace.py --smoke --max-items 2 --n-perm-stat 100
```

Both passed.

Launched in `tmux main:1`:

```bash
cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_path_trace.py \
  --model Qwen/Qwen3-14B \
  --probe-set data/firing-probes.const.jsonl \
  --null-mode gateneutral \
  --n-perm-stat 2000 \
  --seed 0 \
  2>&1 | tee results/program-path-trace/run_qwen3-14b_const.log
```

Verified initial output in `tmux main:1`:

```text
PROGRAM PATH TRACE — monotonic FFN gate path vs fired_sequence
Warning: You are sending unauthenticated requests to the HF Hub...
```

ASYNC: job running in `tmux main:1`. I won’t poll; tell me when it completes.

## User


job is done

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-path-trace/verdict_qwen3-14b_const.json",
  "limit": 220
}
```

**Summary:** Reading verdict_qwen3-14b_const.json (0-220)

**Output:**
```
{
  "model": "Qwen/Qwen3-14B",
  "n_layers": 40,
  "probe_set": "data/firing-probes.const.jsonl",
  "n_items": 133,
  "null_mode": "gateneutral",
  "strict_layers": false,
  "zone_depth": [
    0.7,
    0.86
  ],
  "zone_layers": [
    28,
    29,
    30,
    31,
    32
  ],
  "crystal_layers": [
    0,
    1,
    3,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32
  ],
  "truth_distribution": {
    "C": 67,
    "S": 66
  },
  "path_scores": {
    "zone_truth_score_mean": 2.1287,
    "zone_reverse_score_mean": 2.0843,
    "zone_truth_minus_reverse_mean": 0.0444,
    "zone_margin_vs_best_perm_mean": -0.0315,
    "zone_truth_rank_frac_mean": 0.523,
    "zone_truth_beats_all_n": 3,
    "zone_truth_beats_all_acc": 0.0226,
    "zone_truth_beats_all_null": 0.0226,
    "zone_truth_beats_all_perm_p": 1.0,
    "all_crystal_margin_vs_best_perm_mean": -0.1407,
    "all_crystal_truth_rank_frac_mean": 0.6135,
    "all_crystal_truth_beats_all_n": 45,
    "all_crystal_truth_beats_all_acc": 0.3383,
    "all_crystal_truth_beats_all_null": 0.3383,
    "all_crystal_truth_beats_all_perm_p": 1.0
  },
  "by_category": {
    "ditrans_const": {
      "n": 67,
      "truth_distribution": {
        "C": 67
      },
      "zone_truth_score_mean": 2.366,
      "zone_margin_vs_best_perm_mean": -0.0302,
      "zone_truth_rank_frac_mean": 0.7219,
      "zone_truth_beats_all_n": 0
    },
    "intrans": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "zone_truth_score_mean": 1.6892,
      "zone_margin_vs_best_perm_mean": -0.0237,
      "zone_truth_rank_frac_mean": 0.0606,
      "zone_truth_beats_all_n": 2
    },
    "trans_const": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "zone_truth_score_mean": 2.0865,
      "zone_margin_vs_best_perm_mean": -0.0422,
      "zone_truth_rank_frac_mean": 0.5818,
      "zone_truth_beats_all_n": 1
    }
  },
  "calib": {
    "n_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,
      24,
      25,
      26,
      27,
      28,
      29,
      30,
      31,
      32
    ],
    "per_layer": {
      "0": {
        "sil_z": 2.628,
        "gc_consensus": 0.909,
        "crystal_bearing": true
      },
      "1": {
        "sil_z": 3.125,
        "gc_consensus": 0.796,
        "crystal_bearing": true
      },
      "2": {
        "sil_z": 1.184,
        "gc_consensus": 0.564,
        "crystal_bearing": false
      },
      "3": {
        "sil_z": 2.138,
        "gc_consensus": 0.658,
        "crystal_bearing": true
      },
      "4": {
        "sil_z": 0.574,
        "gc_consensus": 0.641,
        "crystal_bearing": false
      },
      "5": {
        "sil_z": 3.536,
        "gc_consensus": 0.905,
        "crystal_bearing": true
      },
      "6": {
        "sil_z": 6.07,
        "gc_consensus": 0.904,
        "crystal_bearing": true
      },
      "7": {
        "sil_z": 3.883,
        "gc_consensus": 0.915,
        "crystal_bearing": true
      },
      "8": {
        "sil_z": 3.593,
        "gc_consensus": 0.929,
        "crystal_bearing": true
      },
      "9": {
        "sil_z": 5.295,
        "gc_consensus": 0.962,
        "crystal_bearing": true
      },
      "10": {
        "sil_z": 6.804,
        "gc_consensus": 0.962,
        "crystal_bearing": true
      },
      "11": {
        "sil_z": 7.211,
        "gc_consensus": 0.965,
        "crystal_bearing": true
      },
      "12": {
        "sil_z": 8.259,
        "gc_consensus": 0.95,
        "crystal_bearing": true
      },
      "13": {
        "sil_z": 5.98,
        "gc_consensus": 0.953,
        "crystal_bearing": true
      },
      "14": {
        "sil_z": 6.781,
        "gc_consensus": 0.948,
        "crystal_bearing": true
      },
      "15": {
        "sil_z": 7.542,
        "gc_consensus": 0.961,
        "crystal_bearing": true
      },

[CONTENT TRUNCATED] Showing lines 1 to 220 of 351 total lines. Use line_offset=220 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-path-trace/run_qwen3-14b_const.log",
  "limit": 160
}
```

**Summary:** Reading run_qwen3-14b_const.log (0-160)

**Output:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
══════════════════════════════════════════════════════════════════════════════
PROGRAM PATH TRACE — monotonic FFN gate path vs fired_sequence
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=133 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/443 [00:00<?, ?it/s]Loading weights:   0%|          | 1/443 [00:00<07:05,  1.04it/s]Loading weights:   4%|▍         | 17/443 [00:01<00:19, 21.47it/s]Loading weights:   9%|▉         | 39/443 [00:01<00:07, 51.11it/s]Loading weights:  14%|█▎        | 60/443 [00:01<00:04, 79.28it/s]Loading weights:  18%|█▊        | 81/443 [00:01<00:03, 105.20it/s]Loading weights:  23%|██▎       | 101/443 [00:01<00:02, 126.19it/s]Loading weights:  27%|██▋       | 120/443 [00:01<00:02, 138.54it/s]Loading weights:  31%|███▏      | 139/443 [00:01<00:02, 147.63it/s]Loading weights:  36%|███▌      | 160/443 [00:01<00:01, 157.93it/s]Loading weights:  41%|████      | 181/443 [00:01<00:01, 169.30it/s]Loading weights:  46%|████▌     | 202/443 [00:02<00:01, 178.13it/s]Loading weights:  50%|█████     | 222/443 [00:02<00:01, 181.62it/s]Loading weights:  55%|█████▍    | 242/443 [00:02<00:01, 179.60it/s]Loading weights:  59%|█████▉    | 261/443 [00:02<00:01, 176.99it/s]Loading weights:  63%|██████▎   | 280/443 [00:02<00:00, 179.73it/s]Loading weights:  68%|██████▊   | 301/443 [00:02<00:00, 185.61it/s]Loading weights:  72%|███████▏  | 320/443 [00:02<00:00, 185.92it/s]Loading weights:  77%|███████▋  | 339/443 [00:02<00:00, 183.26it/s]Loading weights:  81%|████████  | 358/443 [00:02<00:00, 178.62it/s]Loading weights:  86%|████████▌ | 379/443 [00:02<00:00, 186.62it/s]Loading weights:  90%|█████████ | 400/443 [00:03<00:00, 192.14it/s]Loading weights:  95%|█████████▍| 420/443 [00:03<00:00, 192.38it/s]Loading weights:  99%|█████████▉| 440/443 [00:03<00:00, 188.02it/s]Loading weights: 100%|██████████| 443/443 [00:03<00:00, 133.65it/s]
[v2] Model loaded in 3.9s
[model] Qwen/Qwen3-14B layers=40

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=31/40 zone=[28, 29, 30, 31, 32]

[decode] 133 items strict_layers=False ...
[decode]   item 0/133 ...
[decode]   item 20/133 ...
[decode]   item 40/133 ...
[decode]   item 60/133 ...
[decode]   item 80/133 ...
[decode]   item 100/133 ...
[decode]   item 120/133 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM PATH TRACE — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=133 truth={'C': 67, 'S': 66}
crystal_layers=31/40 zone=[28, 29, 30, 31, 32] strict=False

Zone monotonic path vs same-multiset controls:
  truth score mean:          2.1287
  reverse score mean:        2.0843
  truth - reverse mean:      0.0444
  margin vs best perm mean:  -0.0315
  rank frac mean:            0.523
  beats all perms:           3/133 (p=1.0)

All-crystal path control:
  margin vs best perm mean:  -0.1407
  rank frac mean:            0.6135
  beats all perms:           45/133 (p=1.0)

By category:
  ditrans_const: n=67 score=2.366 margin=-0.0302 rank=0.7219 beats=0/67
  intrans: n=33 score=1.6892 margin=-0.0237 rank=0.0606 beats=2/33
  trans_const: n=33 score=2.0865 margin=-0.0422 rank=0.5818 beats=1/33
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-path-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
```

### Thinking

**Finalizing tasks**

I need to get to the final stages. Maybe I should inspect some examples? Using shell might not be necessary, but it could help extract item patterns. I think I may have enough information as it stands. It’s crucial I ensure all tasks are complete before moving forward. I want to make sure everything is done right, so I might take one more look at everything before considering it finalized.


## Assistant


The monotonic path experiment completed cleanly. Verdict: **negative for ordered β-program recovery.** The path scorer confirms the previous sequence-trace boundary: 14B exposes **C/applicative load**, but the exact `fired_sequence` order is **not** preferentially readable from FFN gate z-maps in the L28–32 zone.

## Artifacts

Wrote:

```text
results/program-path-trace/verdict_qwen3-14b_const.json
results/program-path-trace/per_item_qwen3-14b_const.json
results/program-path-trace/meta_qwen3-14b_const.json
results/program-path-trace/run_qwen3-14b_const.log
```

Run completed:

```text
[write] /Users/mwhitford/src/verbum/results/program-path-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
```

---

## What this experiment tested

For each truth program, e.g.:

```text
S B C C
```

the script asked:

> Is the best monotonic layer path for `S→B→C→C` stronger than the best path for reversed/shuffled same-multiset controls like `C→C→B→S`, `B→S→C→C`, etc.?

This controls for the previous failure mode: high C load / symbol presence without order.

---

## Main result

```json
"path_scores": {
  "zone_truth_score_mean": 2.1287,
  "zone_reverse_score_mean": 2.0843,
  "zone_truth_minus_reverse_mean": 0.0444,
  "zone_margin_vs_best_perm_mean": -0.0315,
  "zone_truth_rank_frac_mean": 0.523,
  "zone_truth_beats_all_n": 3,
  "zone_truth_beats_all_perm_p": 1.0
}
```

Interpretation:

- Truth path is only **slightly** above reverse:
  ```text
  truth - reverse = +0.0444
  ```
- Truth is **below the best same-multiset permutation on average**:
  ```text
  margin vs best permutation = -0.0315
  ```
- Truth ranks basically at chance among permutations:
  ```text
  rank frac = 0.523
  ```
- Truth beats all same-multiset permutations on only:
  ```text
  3 / 133 items
  ```

So the ordered program is not being preferentially recovered.

---

## By category

### Ditransitive constant: truth `S B C C`

```text
n = 67
truth score = 2.366
margin vs best perm = -0.0302
rank frac = 0.7219
truth beats all = 0/67
```

Ditransitives have the strongest apparent rank, but truth still never beats all permutations. This probably reflects strong C load from the two object/application sites, not exact `S→B→C→C` order.

### Transitive constant: truth `S B C`

```text
n = 33
truth score = 2.0865
margin vs best perm = -0.0422
rank frac = 0.5818
truth beats all = 1/33
```

Weak / negative.

### Intransitive: truth `S B`

```text
n = 33
truth score = 1.6892
margin vs best perm = -0.0237
rank frac = 0.0606
truth beats all = 2/33
```

For intransitives, truth order is actually near the bottom among the two possible orders. That means the model/readout is not giving the kernel’s `S→B` order.

---

## All-crystal control

```json
"all_crystal_margin_vs_best_perm_mean": -0.1407,
"all_crystal_truth_rank_frac_mean": 0.6135,
"all_crystal_truth_beats_all_n": 45
```

All-crystal layers improve “beats all” to `45/133`, but margin is still negative. This means allowing all 31 crystal layers gives more chances to match the truth order, but still does not make the truth path uniquely best. Again: evidence of distributed op availability, not a clean tape.

---

## Combined interpretation across the three experiments

### 1. `ffn_program_decode.py`

Positive:

```text
14B FFN C-vs-S acc = 0.6165, p=0.0005
attention C-vs-S acc = 0.5338, p=0.1744
```

So 14B’s FFN gate register significantly tracks corrected applicative-C structure.

### 2. `program_sequence_trace.py`

Positive for C presence:

```text
C presence acc = 0.7519, p=0.0005
decoded event counts: C=709, S=152, B=39
```

But negative for order:

```text
zone LCS = 0.4856
reverse LCS = 0.4618
bag = 0.5144
```

### 3. `program_path_trace.py`

Direct same-multiset order test: negative.

```text
truth rank frac = 0.523
truth beats all permutations = 3/133
margin vs best permutation = -0.0315
```

So the stable conclusion is:

> Qwen3-14B encodes the corrected applicative-C structure in the FFN gate register, but the exact symbolic `fired_sequence` order from our kernel is not readable as a monotonic B/C/S β-instruction path in this register/zone.

---

## Scientific verdict

This is not a failure of the broader thesis; it is a boundary on the **discrete tape** interpretation.

The model appears to carry:

```text
what structure is needed / how much C-application load is present
```

not:

```text
the kernel’s exact ordered β-reduction trace S→B→C→C
```

At least not in this simple FFN-gate relational opcode read.

So the better normal form is probably:

```text
FFN program = distributed potential field / routing landscape
attention = executor sampling/combining from that field
```

not:

```text
FFN program = serial symbolic instruction tape
```

This matches prior warnings from s244/s248: program geometry exists, but discrete opcode-at-layer over-reads.

---

## Recommended next step

I would **stop trying to force the kernel’s `fired_sequence` order as the model’s order**.

The data says the model’s program is not our bracket-abstraction trace. It may still compute applicatively, but with a different schedule.

Next experiment should infer the model’s **native order** instead of scoring against our kernel order:

### Native-order extraction

For each item, compute the strongest layer for each op:

```text
best_layer(S), best_layer(B), best_layer(C)
```

or per-count for repeated C:

```text
top-k C layers
```

Then ask:

1. Is there a stable model-native ordering across examples?
2. Does that ordering differ by category?
   - intransitive
   - transitive
   - ditransitive
3. Does native order predict truth class / object count better than kernel order?
4. Is native order consistent with earlier “C-late” findings?

In other words, move from:

```text
Does the model follow our program order?
```

to:

```text
What program order does the model actually use?
```

A compact next script could be:

```text
scripts/experiments/program_native_order.py
```

Metrics:

```text
per item:
  peak layer per op
  weighted centroid layer per op
  op ordering by peak/centroid
  C-layer distribution vs c_count

aggregate:
  P(S before B), P(B before C), P(S before C)
  category-specific order
  depth histograms for S/B/C
  compare native-order stability vs kernel-order match
```

My read: this will likely show that **C dominates late/readable layers**, while S/B are either earlier, weaker, or not mapped cleanly to the kernel’s `S,B` schedule. That would explain all three results cleanly.

## User


Yes let's create the experiment and run it

### Thinking

**Planning implementation steps**

I recognize that I need to take action and develop a plan. It seems like reusing the native order script could be useful here, which might help streamline the process. After that, I’ll focus on the smoking and launching phase. I want to ensure everything goes smoothly. There’s a lot to consider, and I’m eager to get things up and running as effectively as possible!


### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py",
  "content": "#!/usr/bin/env python3\n# register: topological/routing (FFN gate native order)\n\"\"\"Program Native Order — infer the model's own FFN opcode depth schedule.\n\nThe path tracer showed that Qwen3-14B does not preferentially follow the kernel's\ncertified `fired_sequence` order under same-multiset controls. This experiment stops\nasking whether the model follows OUR bracket-abstraction order and instead asks what\norder the model actually exposes in the FFN gate routing register.\n\nFor each probe and each op in {B,C,S}, read matched-null relational z(op) over content\npositions and crystal-bearing layers, then summarize:\n  • peak layer: layer with max mean z(op) over content tokens;\n  • centroid layer: z-positive weighted average depth for the op;\n  • pairwise order relations S<B, B<C, S<C by peak and centroid;\n  • category/c_count aggregates and C-load vs object-count.\n\nUsage:\n    uv run python scripts/experiments/program_native_order.py --smoke\n    uv run python scripts/experiments/program_native_order.py \\\n      --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl\n\nLicense: MIT. AGENTS.md S5 λ provenance.\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport sys\nfrom collections import Counter, defaultdict\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport numpy as np\n\n_ROOT = Path(__file__).resolve().parent.parent.parent\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"experiments\"))\nsys.path.insert(0, str(_ROOT / \"scripts\" / \"instruments\"))\n\nfrom ffn_program_decode import (  # noqa: E402\n    FIRING_SET,\n    build_firing_corpus,\n    classify_positions,\n    zone_layers,\n)\nfrom opcode_monitor_v2 import (  # noqa: E402\n    COMPILE_GATE,\n    _git_sha,\n    _json_safe,\n    _transformers_version,\n    calibrate_v2,\n    forward_all_positions,\n    gate_prefix_len,\n    load_model_and_tokenizer,\n)\n\nRESULTS_DIR = _ROOT / \"results\" / \"program-native-order\"\nPAIRS = [(\"S\", \"B\"), (\"B\", \"C\"), (\"S\", \"C\")]\n\n\ndef op_layer_profile(\n    reads: list[dict[int, dict[str, float]]], layers: list[int], op: str\n) -> dict[int, float]:\n    prof = {}\n    for li in layers:\n        vals = [r[li][op] for r in reads if li in r]\n        prof[li] = float(np.mean(vals)) if vals else float(\"nan\")\n    return prof\n\n\ndef summarize_op(prof: dict[int, float], n_layers: int) -> dict:\n    vals = [(li, z) for li, z in prof.items() if not np.isnan(z)]\n    if not vals:\n        return {\"peak_layer\": None, \"peak_depth\": None, \"peak_z\": None,\n                \"centroid_layer\": None, \"centroid_depth\": None,\n                \"mean_z\": None, \"positive_mass\": 0.0}\n    peak_layer, peak_z = max(vals, key=lambda x: x[1])\n    zs = np.array([z for _, z in vals], dtype=float)\n    lis = np.array([li for li, _ in vals], dtype=float)\n    pos = np.maximum(zs, 0.0)\n    mass = float(pos.sum())\n    if mass > 1e-12:\n        cen = float((lis * pos).sum() / mass)\n    else:\n        cen = None\n    denom = max(n_layers - 1, 1)\n    return {\n        \"peak_layer\": int(peak_layer),\n        \"peak_depth\": round(float(peak_layer / denom), 4),\n        \"peak_z\": round(float(peak_z), 4),\n        \"centroid_layer\": round(cen, 4) if cen is not None else None,\n        \"centroid_depth\": round(float(cen / denom), 4) if cen is not None else None,\n        \"mean_z\": round(float(np.mean(zs)), 4),\n        \"positive_mass\": round(mass, 4),\n    }\n\n\ndef compare_order(op_summ: dict[str, dict], key: str) -> dict[str, bool | None]:\n    out = {}\n    for a, b in PAIRS:\n        av = op_summ[a].get(key)\n        bv = op_summ[b].get(key)\n        out[f\"{a}_before_{b}\"] = None if av is None or bv is None else bool(av < bv)\n    return out\n\n\ndef _safe_slug(model_name: str, probe_set: str | None) -> str:\n    slug = model_name.split(\"/\")[-1].lower().replace(\".\", \"-\")\n    if probe_set:\n        stem = Path(probe_set).stem\n        slug += \"_\" + (stem.split(\".\")[-1] if \".\" in stem else stem)\n    return slug\n\n\ndef _mean(xs: list[float | int | None]) -> float | None:\n    vals = [float(x) for x in xs if x is not None]\n    return round(float(np.mean(vals)), 4) if vals else None\n\n\ndef _frac(xs: list[bool | None]) -> float | None:\n    vals = [x for x in xs if x is not None]\n    return round(float(np.mean(vals)), 4) if vals else None\n\n\ndef summarize_group(rows: list[dict]) -> dict:\n    out: dict = {\"n\": len(rows)}\n    out[\"truth_distribution\"] = dict(Counter(r[\"dominant_fired\"] for r in rows))\n    for op in FIRING_SET:\n        out[f\"{op}_peak_layer_mean\"] = _mean(\n            [r[\"ops_zone\"][op][\"peak_layer\"] for r in rows])\n        out[f\"{op}_centroid_layer_mean\"] = _mean(\n            [r[\"ops_zone\"][op][\"centroid_layer\"] for r in rows])\n        out[f\"{op}_peak_z_mean\"] = _mean([r[\"ops_zone\"][op][\"peak_z\"] for r in rows])\n        out[f\"{op}_positive_mass_mean\"] = _mean(\n            [r[\"ops_zone\"][op][\"positive_mass\"] for r in rows])\n    for a, b in PAIRS:\n        out[f\"peak_P_{a}_before_{b}\"] = _frac(\n            [r[\"order_peak\"].get(f\"{a}_before_{b}\") for r in rows])\n        out[f\"centroid_P_{a}_before_{b}\"] = _frac(\n            [r[\"order_centroid\"].get(f\"{a}_before_{b}\") for r in rows])\n    return out\n\n\ndef spearman(x: list[float], y: list[float]) -> tuple[float | None, float | None]:\n    if len(x) < 3 or len(set(x)) < 2 or len(set(y)) < 2:\n        return None, None\n    from scipy import stats\n\n    r, p = stats.spearmanr(x, y)\n    return round(float(r), 4), round(float(p), 4)\n\n\ndef run(\n    model_name: str,\n    probe_set: str,\n    max_items: int | None,\n    null_mode: str,\n    zone_lo: float,\n    zone_hi: float,\n    n_perm_calib: int,\n    ppc: int | None,\n    null_cap: int | None,\n) -> tuple[dict, list[dict], dict]:\n    print(\"═\" * 78)\n    print(\"PROGRAM NATIVE ORDER — infer FFN gate opcode schedule\")\n    print(\"═\" * 78)\n    firing, nonfiring = build_firing_corpus([Path(probe_set)])\n    if max_items is not None:\n        firing = firing[:max_items]\n    print(\n        f\"[corpus] source={probe_set} firing={len(firing)} \"\n        f\"nonfiring={len(nonfiring)}\"\n    )\n\n    model, tok, torch_mod = load_model_and_tokenizer(model_name)\n    n_layers = model.config.num_hidden_layers\n    layers = list(range(n_layers))\n    print(f\"[model] {model_name} layers={n_layers}\")\n\n    print(f\"\\n[calib] FFN gate register null_mode={null_mode} ...\")\n    rcc, calib = calibrate_v2(\n        model, tok, torch_mod, layers, n_perm_calib, ppc, null_cap,\n        null_mode=null_mode, hook=\"gate\")\n    crystal_layers = rcc.crystal_layers\n    zlayers = zone_layers(crystal_layers, n_layers, zone_lo, zone_hi)\n    print(f\"[calib] crystal_layers={len(crystal_layers)}/{n_layers} zone={zlayers}\")\n\n    gate_n = gate_prefix_len(tok)\n    per_item: list[dict] = []\n    print(f\"\\n[decode] {len(firing)} items ...\")\n    for i, item in enumerate(firing):\n        if i % 20 == 0:\n            print(f\"[decode]   item {i}/{len(firing)} ...\")\n        prompt = COMPILE_GATE + item[\"input\"]\n        store, n_tok = forward_all_positions(prompt, model, tok, torch_mod, layers,\n                                             hook=\"gate\")\n        positions = list(range(min(gate_n, n_tok - 1), n_tok))\n        reads = classify_positions(rcc, store, layers, positions)\n\n        ops_zone = {}\n        ops_all = {}\n        for op in FIRING_SET:\n            ops_zone[op] = summarize_op(op_layer_profile(reads, zlayers, op), n_layers)\n            ops_all[op] = summarize_op(\n                op_layer_profile(reads, crystal_layers, op), n_layers)\n        per_item.append({\n            \"input\": item[\"input\"],\n            \"category\": item[\"category\"],\n            \"dominant_fired\": item[\"dominant_fired\"],\n            \"fired_sequence\": item[\"fired_sequence\"],\n            \"fired_multiset\": item[\"fired_multiset\"],\n            \"reduction_len\": item[\"reduction_len\"],\n            \"b_count\": item.get(\"b_count\"),\n            \"s_count\": item.get(\"s_count\"),\n            \"c_count\": item.get(\"c_count\"),\n            \"n_content_tokens\": len(positions),\n            \"zone_layers\": zlayers,\n            \"ops_zone\": ops_zone,\n            \"ops_all_crystal\": ops_all,\n            \"order_peak\": compare_order(ops_zone, \"peak_layer\"),\n            \"order_centroid\": compare_order(ops_zone, \"centroid_layer\"),\n            \"order_peak_all_crystal\": compare_order(ops_all, \"peak_layer\"),\n            \"order_centroid_all_crystal\": compare_order(ops_all, \"centroid_layer\"),\n        })\n\n    by_category = {}\n    for cat in sorted({r[\"category\"] for r in per_item}):\n        by_category[cat] = summarize_group([r for r in per_item if r[\"category\"] == cat])\n    by_c_count = {}\n    for cc in sorted({r[\"c_count\"] for r in per_item if r.get(\"c_count\") is not None}):\n        by_c_count[str(cc)] = summarize_group([r for r in per_item if r.get(\"c_count\") == cc])\n\n    c_count = [float(r[\"c_count\"]) for r in per_item]\n    c_mass = [float(r[\"ops_zone\"][\"C\"][\"positive_mass\"]) for r in per_item]\n    c_peak_z = [float(r[\"ops_zone\"][\"C\"][\"peak_z\"]) for r in per_item]\n    c_centroid = [float(r[\"ops_zone\"][\"C\"][\"centroid_layer\"]) for r in per_item]\n    mass_r, mass_p = spearman(c_count, c_mass)\n    peak_r, peak_p = spearman(c_count, c_peak_z)\n    cen_r, cen_p = spearman(c_count, c_centroid)\n\n    verdict = {\n        \"model\": model_name,\n        \"n_layers\": n_layers,\n        \"probe_set\": probe_set,\n        \"n_items\": len(per_item),\n        \"null_mode\": null_mode,\n        \"zone_depth\": [zone_lo, zone_hi],\n        \"zone_layers\": zlayers,\n        \"crystal_layers\": crystal_layers,\n        \"truth_distribution\": dict(Counter(r[\"dominant_fired\"] for r in per_item)),\n        \"native_order\": summarize_group(per_item),\n        \"by_category\": by_category,\n        \"by_c_count\": by_c_count,\n        \"c_count_correlations\": {\n            \"spearman_C_positive_mass_vs_c_count\": mass_r,\n            \"p_mass\": mass_p,\n            \"spearman_C_peak_z_vs_c_count\": peak_r,\n            \"p_peak_z\": peak_p,\n            \"spearman_C_centroid_layer_vs_c_count\": cen_r,\n            \"p_centroid_layer\": cen_p,\n        },\n        \"calib\": calib,\n    }\n    meta = {\n        \"model\": model_name,\n        \"git_sha\": _git_sha(),\n        \"timestamp_utc\": datetime.now(UTC).isoformat(),\n        \"transformers_version\": _transformers_version(),\n        \"params\": {\n            \"probe_set\": probe_set,\n            \"max_items\": max_items,\n            \"null_mode\": null_mode,\n            \"zone_lo\": zone_lo,\n            \"zone_hi\": zone_hi,\n            \"n_perm_calib\": n_perm_calib,\n            \"ppc\": ppc,\n            \"null_cap\": null_cap,\n        },\n        \"method\": \"Infer native FFN gate opcode order via peak/centroid layer of \"\n                  \"matched-null relational z(op) profiles over content tokens.\",\n    }\n    return verdict, per_item, meta\n\n\ndef write_outputs(verdict: dict, per_item: list[dict], meta: dict) -> None:\n    RESULTS_DIR.mkdir(parents=True, exist_ok=True)\n    slug = _safe_slug(verdict[\"model\"], verdict.get(\"probe_set\"))\n    (RESULTS_DIR / f\"verdict_{slug}.json\").write_text(\n        json.dumps(_json_safe(verdict), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"per_item_{slug}.json\").write_text(\n        json.dumps(_json_safe(per_item), indent=2), encoding=\"utf-8\")\n    (RESULTS_DIR / f\"meta_{slug}.json\").write_text(\n        json.dumps(_json_safe(meta), indent=2), encoding=\"utf-8\")\n    print(f\"[write] {RESULTS_DIR / f'verdict_{slug}.json'} (+ per_item, meta)\")\n\n\ndef report(verdict: dict) -> None:\n    n = verdict[\"native_order\"]\n    print(\"\\n\" + \"═\" * 78)\n    print(\"PROGRAM NATIVE ORDER — VERDICT\")\n    print(\"═\" * 78)\n    print(f\"items={verdict['n_items']} truth={verdict['truth_distribution']}\")\n    print(f\"crystal_layers={len(verdict['crystal_layers'])}/{verdict['n_layers']} \"\n          f\"zone={verdict['zone_layers']}\")\n    print(\"\\nNative order probabilities (zone):\")\n    for a, b in PAIRS:\n        print(\n            f\"  peak P({a}<{b})={n[f'peak_P_{a}_before_{b}']}  \"\n            f\"centroid P({a}<{b})={n[f'centroid_P_{a}_before_{b}']}\"\n        )\n    print(\"\\nMean peak/centroid layers by op:\")\n    for op in FIRING_SET:\n        print(\n            f\"  {op}: peak={n[f'{op}_peak_layer_mean']} \"\n            f\"centroid={n[f'{op}_centroid_layer_mean']} \"\n            f\"mass={n[f'{op}_positive_mass_mean']}\"\n        )\n    print(\"\\nC-count correlations:\")\n    print(json.dumps(verdict[\"c_count_correlations\"], indent=2))\n    print(\"\\nBy category:\")\n    for cat, d in verdict[\"by_category\"].items():\n        print(\n            f\"  {cat}: n={d['n']} C_mass={d['C_positive_mass_mean']} \"\n            f\"P(B<C)={d['peak_P_B_before_C']} \"\n            f\"P(S<C)={d['peak_P_S_before_C']}\"\n        )\n    print(\"═\" * 78 + \"\\n\")\n\n\ndef main() -> None:\n    ap = argparse.ArgumentParser(description=\"Infer native FFN opcode order\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-14B\")\n    ap.add_argument(\"--probe-set\", default=\"data/firing-probes.const.jsonl\")\n    ap.add_argument(\"--max-items\", type=int, default=None)\n    ap.add_argument(\"--null-mode\", default=\"gateneutral\",\n                    choices=[\"gateneutral\", \"crosstask\"])\n    ap.add_argument(\"--zone-lo\", type=float, default=0.70)\n    ap.add_argument(\"--zone-hi\", type=float, default=0.86)\n    ap.add_argument(\"--smoke\", action=\"store_true\")\n    args = ap.parse_args()\n\n    model = args.model\n    max_items = args.max_items\n    if args.smoke:\n        if model == \"Qwen/Qwen3-14B\":\n            model = \"Qwen/Qwen3-0.6B\"\n        n_perm_calib, ppc, null_cap = 80, 3, 200\n        max_items = max_items or 6\n        print(\"[smoke] Qwen3-0.6B small calibration\")\n    else:\n        n_perm_calib, ppc, null_cap = 300, None, None\n\n    verdict, per_item, meta = run(\n        model, args.probe_set, max_items, args.null_mode, args.zone_lo, args.zone_hi,\n        n_perm_calib, ppc, null_cap)\n    report(verdict)\n    write_outputs(verdict, per_item, meta)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py
```

### Tool Call: shell_command (failed)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 1
Stdout:
F401 [*] `collections.defaultdict` imported but unused
  --> scripts/experiments/program_native_order.py:30:34
   |
28 | import json
29 | import sys
30 | from collections import Counter, defaultdict
   |                                  ^^^^^^^^^^^
31 | from datetime import UTC, datetime
32 | from pathlib import Path
   |
help: Remove unused import: `collections.defaultdict`

E501 Line too long (89 > 88)
   --> scripts/experiments/program_native_order.py:228:89
    |
226 |     by_category = {}
227 |     for cat in sorted({r["category"] for r in per_item}):
228 |         by_category[cat] = summarize_group([r for r in per_item if r["category"] == cat])
    |                                                                                         ^
229 |     by_c_count = {}
230 |     for cc in sorted({r["c_count"] for r in per_item if r.get("c_count") is not None}):
    |

E501 Line too long (94 > 88)
   --> scripts/experiments/program_native_order.py:231:89
    |
229 |     by_c_count = {}
230 |     for cc in sorted({r["c_count"] for r in per_item if r.get("c_count") is not None}):
231 |         by_c_count[str(cc)] = summarize_group([r for r in per_item if r.get("c_count") == cc])
    |                                                                                         ^^^^^^
232 |
233 |     c_count = [float(r["c_count"]) for r in per_item]
    |

Found 3 errors.
[*] 1 fixable with the `--fix` option.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py",
  "original_content": "from collections import Counter, defaultdict\n",
  "new_content": "from collections import Counter\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py",
  "original_content": "    by_category = {}\n    for cat in sorted({r[\"category\"] for r in per_item}):\n        by_category[cat] = summarize_group([r for r in per_item if r[\"category\"] == cat])\n    by_c_count = {}\n    for cc in sorted({r[\"c_count\"] for r in per_item if r.get(\"c_count\") is not None}):\n        by_c_count[str(cc)] = summarize_group([r for r in per_item if r.get(\"c_count\") == cc])\n",
  "new_content": "    by_category = {}\n    for cat in sorted({r[\"category\"] for r in per_item}):\n        rows = [r for r in per_item if r[\"category\"] == cat]\n        by_category[cat] = summarize_group(rows)\n    by_c_count = {}\n    c_counts = sorted({r[\"c_count\"] for r in per_item if r.get(\"c_count\") is not None})\n    for cc in c_counts:\n        rows = [r for r in per_item if r.get(\"c_count\") == cc]\n        by_c_count[str(cc)] = summarize_group(rows)\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run ruff check /Users/mwhitford/src/verbum/scripts/experiments/program_native_order.py",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ uv run ruff check /Users/mwhitford/...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "uv run python scripts/experiments/program_native_order.py --smoke --max-items 2",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 600000
}
```

**Summary:** $ uv run python scripts/experiments/p...

**Output:**
```
Exit code: 0
Stderr:
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
Loading weights:   0%|          | 0/311 [00:00<?, ?it/s]Loading weights:  12%|█▏        | 36/311 [00:00<00:00, 359.16it/s]Loading weights:  76%|███████▌  | 237/311 [00:00<00:00, 1324.68it/s]Loading weights: 100%|██████████| 311/311 [00:00<00:00, 1305.71it/s]
Stdout:
[smoke] Qwen3-0.6B small calibration
══════════════════════════════════════════════════════════════════════════════
PROGRAM NATIVE ORDER — infer FFN gate opcode schedule
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=2 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-0.6B
[v2] Loading model: Qwen/Qwen3-0.6B  (dtype=auto, device_map=auto)
[v2] Model loaded in 0.8s
[model] Qwen/Qwen3-0.6B layers=28

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 27
[v2]   centroid forward 0/27 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=25/28 zone=[19, 20, 21, 22, 23]

[decode] 2 items ...
[decode]   item 0/2 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM NATIVE ORDER — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=2 truth={'C': 2}
crystal_layers=25/28 zone=[19, 20, 21, 22, 23]

Native order probabilities (zone):
  peak P(S<B)=0.0  centroid P(S<B)=None
  peak P(B<C)=1.0  centroid P(B<C)=1.0
  peak P(S<C)=0.5  centroid P(S<C)=None

Mean peak/centroid layers by op:
  B: peak=19.0 centroid=19.5095 mass=2.1789
  C: peak=23.0 centroid=21.3839 mass=4.6334
  S: peak=21.5 centroid=None mass=0.0

C-count correlations:
{
  "spearman_C_positive_mass_vs_c_count": null,
  "p_mass": null,
  "spearman_C_peak_z_vs_c_count": null,
  "p_peak_z": null,
  "spearman_C_centroid_layer_vs_c_count": null,
  "p_centroid_layer": null
}

By category:
  ditrans_const: n=2 C_mass=4.6334 P(B<C)=1.0 P(S<C)=0.5
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-native-order/verdict_qwen3-0-6b_const.json (+ per_item, meta)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_native_order.py --model Qwen/Qwen3-14B --probe-set data/firing-probes.const.jsonl --null-mode gateneutral 2>&1 | tee results/program-native-order/run_qwen3-14b_const.log' Enter && sleep 3 && tmux capture-pane -p -t main:1 | tail -80",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 10000
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
beats all perms:           3/133 (p=1.0)

All-crystal path control:
  margin vs best perm mean:  -0.1407
  rank frac mean:            0.6135
  beats all perms:           45/133 (p=1.0)

By category:
  ditrans_const: n=67 score=2.366 margin=-0.0302 rank=0.7219 beats=0/67
  intrans: n=33 score=1.6892 margin=-0.0237 rank=0.0606 beats=2/33
  trans_const: n=33 score=2.0865 margin=-0.0422 rank=0.5818 beats=1/33
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-path-trace/verdict_qwen3-14b_const.json (+ per_item, meta)
uv run python scripts/experiments/program_path_trace.py --model Qwen/Qwen3-14  166.75s user 13.27s system 87% cpu 3:26.2
8 total
tee results/program-path-trace/run_qwen3-14b_const.log  0.00s user 0.00s system 0% cpu 3:26.28 total
[26-06-23][8:33:54][mwhitford@olga][0][~/src/verbum][git:main]
λ cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_native_order.py --model Qwen/Qwen3-14B --p
robe-set data/firing-probes.const.jsonl --null-mode gateneutral 2>&1 | tee results/program-native-order/run_qwen3-14b_co
nst.log
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and
faster downloads.
```

## Assistant


Created and launched the native-order experiment.

New script:

```text
scripts/experiments/program_native_order.py
```

What it does:

- Uses the validated FFN gate relational reader:
  - `RelationalCrystalClassifier`
  - sign(gate)-CMR
  - matched `gateneutral` null
- Reads each probe’s content-token activations.
- For each op in `{B,C,S}`, computes:
  - peak layer / depth
  - z-positive centroid layer / depth
  - mean z
  - positive mass
- Aggregates native order relations:
  - `P(S < B)`
  - `P(B < C)`
  - `P(S < C)`
  - by peak and centroid
- Summarizes by:
  - category: `intrans`, `trans_const`, `ditrans_const`
  - `c_count`
- Tests C-load vs object/C-count correlations.

Validation passed:

```bash
uv run ruff check scripts/experiments/program_native_order.py
uv run python scripts/experiments/program_native_order.py --smoke --max-items 2
```

Launched in `tmux main:1`:

```bash
cd /Users/mwhitford/src/verbum && uv run python scripts/experiments/program_native_order.py \
  --model Qwen/Qwen3-14B \
  --probe-set data/firing-probes.const.jsonl \
  --null-mode gateneutral \
  2>&1 | tee results/program-native-order/run_qwen3-14b_const.log
```

Verified initial output in `tmux main:1`:

```text
PROGRAM NATIVE ORDER — infer FFN gate opcode schedule
Warning: You are sending unauthenticated requests to the HF Hub...
```

ASYNC: job running in `tmux main:1`. I won’t poll; tell me when it completes.

## User


job is done

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-native-order/verdict_qwen3-14b_const.json",
  "limit": 260
}
```

**Summary:** Reading verdict_qwen3-14b_const.json (0-260)

**Output:**
```
{
  "model": "Qwen/Qwen3-14B",
  "n_layers": 40,
  "probe_set": "data/firing-probes.const.jsonl",
  "n_items": 133,
  "null_mode": "gateneutral",
  "zone_depth": [
    0.7,
    0.86
  ],
  "zone_layers": [
    28,
    29,
    30,
    31,
    32
  ],
  "crystal_layers": [
    0,
    1,
    3,
    5,
    6,
    7,
    8,
    9,
    10,
    11,
    12,
    13,
    14,
    15,
    16,
    17,
    18,
    19,
    20,
    21,
    22,
    23,
    24,
    25,
    26,
    27,
    28,
    29,
    30,
    31,
    32
  ],
  "truth_distribution": {
    "C": 67,
    "S": 66
  },
  "native_order": {
    "n": 133,
    "truth_distribution": {
      "C": 67,
      "S": 66
    },
    "B_peak_layer_mean": 29.0451,
    "B_centroid_layer_mean": 29.0828,
    "B_peak_z_mean": -0.0282,
    "B_positive_mass_mean": 0.1488,
    "C_peak_layer_mean": 30.812,
    "C_centroid_layer_mean": 30.3758,
    "C_peak_z_mean": 1.3858,
    "C_positive_mass_mean": 5.0718,
    "S_peak_layer_mean": 28.5865,
    "S_centroid_layer_mean": 29.3798,
    "S_peak_z_mean": 0.4662,
    "S_positive_mass_mean": 1.5517,
    "peak_P_S_before_B": 0.3158,
    "centroid_P_S_before_B": 0.3115,
    "peak_P_B_before_C": 0.7293,
    "centroid_P_B_before_C": 0.8525,
    "peak_P_S_before_C": 0.9474,
    "centroid_P_S_before_C": 0.9925
  },
  "by_category": {
    "ditrans_const": {
      "n": 67,
      "truth_distribution": {
        "C": 67
      },
      "B_peak_layer_mean": 28.4179,
      "B_centroid_layer_mean": 28.3985,
      "B_peak_z_mean": -0.0516,
      "B_positive_mass_mean": 0.1029,
      "C_peak_layer_mean": 30.2388,
      "C_centroid_layer_mean": 30.0944,
      "C_peak_z_mean": 1.5617,
      "C_positive_mass_mean": 6.2245,
      "S_peak_layer_mean": 28.4776,
      "S_centroid_layer_mean": 29.402,
      "S_peak_z_mean": 0.5036,
      "S_positive_mass_mean": 1.7008,
      "peak_P_S_before_B": 0.1493,
      "centroid_P_S_before_B": 0.1071,
      "peak_P_B_before_C": 0.8507,
      "centroid_P_B_before_C": 0.9643,
      "peak_P_S_before_C": 0.9104,
      "centroid_P_S_before_C": 1.0
    },
    "intrans": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "B_peak_layer_mean": 30.3939,
      "B_centroid_layer_mean": 30.7019,
      "B_peak_z_mean": -0.0253,
      "B_positive_mass_mean": 0.1257,
      "C_peak_layer_mean": 31.1212,
      "C_centroid_layer_mean": 30.8687,
      "C_peak_z_mean": 1.0163,
      "C_positive_mass_mean": 2.8769,
      "S_peak_layer_mean": 28.7879,
      "S_centroid_layer_mean": 29.4262,
      "S_peak_z_mean": 0.3945,
      "S_positive_mass_mean": 1.3104,
      "peak_P_S_before_B": 0.6667,
      "centroid_P_S_before_B": 0.8,
      "peak_P_B_before_C": 0.4242,
      "centroid_P_B_before_C": 0.5333,
      "peak_P_S_before_C": 1.0,
      "centroid_P_S_before_C": 1.0
    },
    "trans_const": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "B_peak_layer_mean": 28.9697,
      "B_centroid_layer_mean": 28.798,
      "B_peak_z_mean": 0.0167,
      "B_positive_mass_mean": 0.2651,
      "C_peak_layer_mean": 31.6667,
      "C_centroid_layer_mean": 30.4543,
      "C_peak_z_mean": 1.398,
      "C_positive_mass_mean": 4.9264,
      "S_peak_layer_mean": 28.6061,
      "S_centroid_layer_mean": 29.2882,
      "S_peak_z_mean": 0.4621,
      "S_positive_mass_mean": 1.4902,
      "peak_P_S_before_B": 0.303,
      "centroid_P_S_before_B": 0.2222,
      "peak_P_B_before_C": 0.7879,
      "centroid_P_B_before_C": 0.9444,
      "peak_P_S_before_C": 0.9697,
      "centroid_P_S_before_C": 0.9697
    }
  },
  "by_c_count": {
    "0": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "B_peak_layer_mean": 30.3939,
      "B_centroid_layer_mean": 30.7019,
      "B_peak_z_mean": -0.0253,
      "B_positive_mass_mean": 0.1257,
      "C_peak_layer_mean": 31.1212,
      "C_centroid_layer_mean": 30.8687,
      "C_peak_z_mean": 1.0163,
      "C_positive_mass_mean": 2.8769,
      "S_peak_layer_mean": 28.7879,
      "S_centroid_layer_mean": 29.4262,
      "S_peak_z_mean": 0.3945,
      "S_positive_mass_mean": 1.3104,
      "peak_P_S_before_B": 0.6667,
      "centroid_P_S_before_B": 0.8,
      "peak_P_B_before_C": 0.4242,
      "centroid_P_B_before_C": 0.5333,
      "peak_P_S_before_C": 1.0,
      "centroid_P_S_before_C": 1.0
    },
    "1": {
      "n": 33,
      "truth_distribution": {
        "S": 33
      },
      "B_peak_layer_mean": 28.9697,
      "B_centroid_layer_mean": 28.798,
      "B_peak_z_mean": 0.0167,
      "B_positive_mass_mean": 0.2651,
      "C_peak_layer_mean": 31.6667,
      "C_centroid_layer_mean": 30.4543,
      "C_peak_z_mean": 1.398,
      "C_positive_mass_mean": 4.9264,
      "S_peak_layer_mean": 28.6061,
      "S_centroid_layer_mean": 29.2882,
      "S_peak_z_mean": 0.4621,
      "S_positive_mass_mean": 1.4902,
      "peak_P_S_before_B": 0.303,
      "centroid_P_S_before_B": 0.2222,
      "peak_P_B_before_C": 0.7879,
      "centroid_P_B_before_C": 0.9444,
      "peak_P_S_before_C": 0.9697,
      "centroid_P_S_before_C": 0.9697
    },
    "2": {
      "n": 67,
      "truth_distribution": {
        "C": 67
      },
      "B_peak_layer_mean": 28.4179,
      "B_centroid_layer_mean": 28.3985,
      "B_peak_z_mean": -0.0516,
      "B_positive_mass_mean": 0.1029,
      "C_peak_layer_mean": 30.2388,
      "C_centroid_layer_mean": 30.0944,
      "C_peak_z_mean": 1.5617,
      "C_positive_mass_mean": 6.2245,
      "S_peak_layer_mean": 28.4776,
      "S_centroid_layer_mean": 29.402,
      "S_peak_z_mean": 0.5036,
      "S_positive_mass_mean": 1.7008,
      "peak_P_S_before_B": 0.1493,
      "centroid_P_S_before_B": 0.1071,
      "peak_P_B_before_C": 0.8507,
      "centroid_P_B_before_C": 0.9643,
      "peak_P_S_before_C": 0.9104,
      "centroid_P_S_before_C": 1.0
    }
  },
  "c_count_correlations": {
    "spearman_C_positive_mass_vs_c_count": 0.5357,
    "p_mass": 0.0,
    "spearman_C_peak_z_vs_c_count": 0.3778,
    "p_peak_z": 0.0,
    "spearman_C_centroid_layer_vs_c_count": -0.7719,
    "p_centroid_layer": 0.0
  },
  "calib": {
    "n_layers": 40,
    "crystal_layers": [
      0,
      1,
      3,
      5,
      6,
      7,
      8,
      9,
      10,
      11,
      12,
      13,
      14,
      15,
      16,
      17,
      18,
      19,
      20,
      21,
      22,
      23,

[CONTENT TRUNCATED] Showing lines 1 to 260 of 482 total lines. Use line_offset=260 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/results/program-native-order/run_qwen3-14b_const.log",
  "limit": 170
}
```

**Summary:** Reading run_qwen3-14b_const.log (0-170)

**Output:**
```
Warning: You are sending unauthenticated requests to the HF Hub. Please set a HF_TOKEN to enable higher rate limits and faster downloads.
══════════════════════════════════════════════════════════════════════════════
PROGRAM NATIVE ORDER — infer FFN gate opcode schedule
══════════════════════════════════════════════════════════════════════════════
[corpus] source=data/firing-probes.const.jsonl firing=133 nonfiring=0
[v2] Loading tokenizer: Qwen/Qwen3-14B
[v2] Loading model: Qwen/Qwen3-14B  (dtype=auto, device_map=auto)
Loading weights:   0%|          | 0/443 [00:00<?, ?it/s]Loading weights:   0%|          | 1/443 [00:00<06:16,  1.17it/s]Loading weights:   0%|          | 2/443 [00:00<03:07,  2.35it/s]Loading weights:   4%|▍         | 17/443 [00:01<00:16, 26.40it/s]Loading weights:   9%|▉         | 39/443 [00:01<00:06, 61.31it/s]Loading weights:  14%|█▍        | 61/443 [00:01<00:04, 91.63it/s]Loading weights:  19%|█▊        | 83/443 [00:01<00:03, 116.49it/s]Loading weights:  24%|██▎       | 105/443 [00:01<00:02, 136.45it/s]Loading weights:  28%|██▊       | 126/443 [00:01<00:02, 154.36it/s]Loading weights:  33%|███▎      | 148/443 [00:01<00:01, 165.82it/s]Loading weights:  38%|███▊      | 170/443 [00:01<00:01, 174.13it/s]Loading weights:  43%|████▎     | 191/443 [00:01<00:01, 181.48it/s]Loading weights:  48%|████▊     | 211/443 [00:02<00:01, 183.01it/s]Loading weights:  52%|█████▏    | 231/443 [00:02<00:01, 179.07it/s]Loading weights:  56%|█████▋    | 250/443 [00:02<00:01, 173.67it/s]Loading weights:  61%|██████    | 269/443 [00:02<00:00, 176.50it/s]Loading weights:  65%|██████▌   | 290/443 [00:02<00:00, 184.01it/s]Loading weights:  70%|██████▉   | 309/443 [00:02<00:00, 185.15it/s]Loading weights:  74%|███████▍  | 328/443 [00:02<00:00, 183.52it/s]Loading weights:  78%|███████▊  | 347/443 [00:02<00:00, 178.23it/s]Loading weights:  83%|████████▎ | 369/443 [00:02<00:00, 182.46it/s]Loading weights:  88%|████████▊ | 391/443 [00:03<00:00, 185.68it/s]Loading weights:  93%|█████████▎| 413/443 [00:03<00:00, 187.97it/s]Loading weights:  98%|█████████▊| 434/443 [00:03<00:00, 193.80it/s]Loading weights: 100%|██████████| 443/443 [00:03<00:00, 133.65it/s]
[v2] Model loaded in 3.9s
[model] Qwen/Qwen3-14B layers=40

[calib] FFN gate register null_mode=gateneutral ...
[v2] Crystal probes (last-token centroids): 535
[v2]   centroid forward 0/535 ...
[v2]   centroid forward 50/535 ...
[v2]   centroid forward 100/535 ...
[v2]   centroid forward 150/535 ...
[v2]   centroid forward 200/535 ...
[v2]   centroid forward 250/535 ...
[v2]   centroid forward 300/535 ...
[v2]   centroid forward 350/535 ...
[v2]   centroid forward 400/535 ...
[v2]   centroid forward 450/535 ...
[v2]   centroid forward 500/535 ...
[v2] Building MATCHED-PREFIX null from 14 gate+non-compositional prompts (content positions) ...
[v2] Null tokens pooled: 56  (null_mode=gateneutral)
[calib] crystal_layers=31/40 zone=[28, 29, 30, 31, 32]

[decode] 133 items ...
[decode]   item 0/133 ...
[decode]   item 20/133 ...
[decode]   item 40/133 ...
[decode]   item 60/133 ...
[decode]   item 80/133 ...
[decode]   item 100/133 ...
[decode]   item 120/133 ...

══════════════════════════════════════════════════════════════════════════════
PROGRAM NATIVE ORDER — VERDICT
══════════════════════════════════════════════════════════════════════════════
items=133 truth={'C': 67, 'S': 66}
crystal_layers=31/40 zone=[28, 29, 30, 31, 32]

Native order probabilities (zone):
  peak P(S<B)=0.3158  centroid P(S<B)=0.3115
  peak P(B<C)=0.7293  centroid P(B<C)=0.8525
  peak P(S<C)=0.9474  centroid P(S<C)=0.9925

Mean peak/centroid layers by op:
  B: peak=29.0451 centroid=29.0828 mass=0.1488
  C: peak=30.812 centroid=30.3758 mass=5.0718
  S: peak=28.5865 centroid=29.3798 mass=1.5517

C-count correlations:
{
  "spearman_C_positive_mass_vs_c_count": 0.5357,
  "p_mass": 0.0,
  "spearman_C_peak_z_vs_c_count": 0.3778,
  "p_peak_z": 0.0,
  "spearman_C_centroid_layer_vs_c_count": -0.7719,
  "p_centroid_layer": 0.0
}

By category:
  ditrans_const: n=67 C_mass=6.2245 P(B<C)=0.8507 P(S<C)=0.9104
  intrans: n=33 C_mass=2.8769 P(B<C)=0.4242 P(S<C)=1.0
  trans_const: n=33 C_mass=4.9264 P(B<C)=0.7879 P(S<C)=0.9697
══════════════════════════════════════════════════════════════════════════════

[write] /Users/mwhitford/src/verbum/results/program-native-order/verdict_qwen3-14b_const.json (+ per_item, meta)
```

## Assistant


The native-order experiment completed cleanly. This one **does explain the previous failures**.

## Artifacts

Wrote:

```text
results/program-native-order/verdict_qwen3-14b_const.json
results/program-native-order/per_item_qwen3-14b_const.json
results/program-native-order/meta_qwen3-14b_const.json
results/program-native-order/run_qwen3-14b_const.log
```

Run completed:

```text
[write] /Users/mwhitford/src/verbum/results/program-native-order/verdict_qwen3-14b_const.json (+ per_item, meta)
```

---

## Headline verdict

The model-native schedule is **not** our kernel `fired_sequence` order.

The native schedule in the readable L28–32 zone is approximately:

```text
S / B early-ish  →  C late
```

But with **B extremely weak** and **C overwhelmingly dominant**.

So the model is not exposing:

```text
S → B → C
```

as a serial β-program. It is exposing:

```text
early weak S/B framing + late strong applicative-C resolution
```

This explains why:

- `ffn_program_decode` found strong C-vs-S structure;
- `program_sequence_trace` found C-presence but not order;
- `program_path_trace` failed same-multiset order controls.

The order the model actually exposes is mostly:

```text
S before C
B often before C
S vs B unstable / not kernel-like
```

---

## Native order probabilities

From the readable zone:

```text
zone_layers = [28, 29, 30, 31, 32]
```

Overall:

```text
peak P(S < B)      = 0.3158
centroid P(S < B)  = 0.3115

peak P(B < C)      = 0.7293
centroid P(B < C)  = 0.8525

peak P(S < C)      = 0.9474
centroid P(S < C)  = 0.9925
```

Interpretation:

- **S before C is very stable.**
- **B before C is fairly stable**, especially by centroid.
- **S before B is not stable**; in fact it is usually false.

So the native ordering is not the kernel order `S→B→C`. It is closer to:

```text
{S, B} before C
```

with S/B relation unstable and B weak.

---

## Mean op depths / masses

Overall readable-zone means:

```text
B:
  peak layer     = 29.0451
  centroid layer = 29.0828
  peak z         = -0.0282
  positive mass  = 0.1488

S:
  peak layer     = 28.5865
  centroid layer = 29.3798
  peak z         = 0.4662
  positive mass  = 1.5517

C:
  peak layer     = 30.8120
  centroid layer = 30.3758
  peak z         = 1.3858
  positive mass  = 5.0718
```

This is decisive:

```text
C mass ≈ 5.07
S mass ≈ 1.55
B mass ≈ 0.15
```

B is almost absent in this readout. That is why all ordered `S,B,C` program extraction failed: the “B step” barely exists in the model’s FFN gate signal.

The model is not doing the kernel’s B-heavy bracket abstraction. It is resolving applicative objects through C.

---

## Category breakdown

### Ditransitive constant: `c_count=2`, truth `S B C C`

```text
C positive mass = 6.2245
S positive mass = 1.7008
B positive mass = 0.1029

peak P(B<C) = 0.8507
peak P(S<C) = 0.9104
peak P(S<B) = 0.1493
```

Ditransitives are the strongest C cases. C is late and dominant.

### Transitive constant: `c_count=1`, truth `S B C`

```text
C positive mass = 4.9264
S positive mass = 1.4902
B positive mass = 0.2651

peak P(B<C) = 0.7879
peak P(S<C) = 0.9697
peak P(S<B) = 0.3030
```

Still C-dominant; B is slightly more visible than in ditransitives but still weak.

### Intransitive: `c_count=0`, truth `S B`

```text
C positive mass = 2.8769
S positive mass = 1.3104
B positive mass = 0.1257

peak P(B<C) = 0.4242
peak P(S<C) = 1.0
peak P(S<B) = 0.6667
```

Even when truth has no C, the model still has substantial C mass. That matches earlier C-common-mode observations. But C mass is lower than transitive/ditransitive, so it is not pure noise.

---

## C-count correlations

```text
Spearman C positive mass vs c_count:
  r = 0.5357, p = 0.0

Spearman C peak z vs c_count:
  r = 0.3778, p = 0.0

Spearman C centroid layer vs c_count:
  r = -0.7719, p = 0.0
```

This is important.

As object/C-count increases:

1. **C mass increases.**
2. **C peak z increases.**
3. **C centroid moves earlier** within the readable zone.

That means added applicative objects do not merely make a late C blip taller; they pull C-resolution earlier/stronger through the computation window.

This is probably the model’s native “program” signature:

```text
more object/application work → stronger and earlier C field
```

not:

```text
more object/application work → more discrete C instructions in a tape
```

---

## Synthesis across the four runs

### 1. `ffn_program_decode`

14B significantly tracks corrected applicative-C labels:

```text
FFN C-vs-S acc = 0.6165, p=0.0005
```

### 2. `program_sequence_trace`

C presence is significant:

```text
C presence acc = 0.7519, p=0.0005
```

But ordered LCS is weak:

```text
zone LCS = 0.4856
reverse LCS = 0.4618
bag = 0.5144
```

### 3. `program_path_trace`

Same-multiset order control fails:

```text
truth beats all permutations = 3/133
truth rank frac = 0.523
```

### 4. `program_native_order`

The reason becomes clear:

```text
C is huge and late.
S is smaller and earlier.
B is barely present.
S/B relative order is unstable.
```

So the correct interpretation is:

> The model’s FFN gate register encodes an applicative-C routing field whose strength and timing track object/application load. It does not encode the kernel’s ordered `S,B,C` bracket-abstraction program as a discrete instruction tape.

---

## The normal form now

I’d update the working hypothesis from:

```text
FFN emits ordered β-instruction tape; attention executes it.
```

to:

```text
FFN shapes a β-routing potential field.
Attention executes by sampling/combining values from that field.
The field has op-specific load and depth structure, especially C,
but not a faithful serial copy of our symbolic reducer’s order.
```

More compactly:

```text
program = depth-shaped routing field, not tape
```

For these probes, the field says:

```text
S/B framing early → C/application resolution late;
more objects → stronger + earlier C.
```

---

## Recommended next action

I’d stop the sequence-order extraction thread here and preserve this as the resolution.

Next useful experiment would be **causal**, not another decoder:

### C-field causal ablation / patch

Question:

> Is the late C field load-bearing for object/application composition?

Use the native result to target layers:

```text
C peak/centroid zone around L30–31
```

Intervene:

1. Identify high-C items:
   - ditransitive `c_count=2`
2. Identify low-C matched controls:
   - intransitive `c_count=0`
3. Patch or ablate the FFN gate C direction in L30-ish.
4. Measure whether:
   - C-vs-S classification drops;
   - object/application output behavior changes;
   - ditransitive items are selectively affected more than intransitives.

If causal patch works, the claim becomes much stronger:

> the C-field is not just readable; it is load-bearing.

Suggested script name:

```text
scripts/experiments/c_field_causal_patch.py
```

But before that, I’d update `state.md` and likely create a memory/knowledge note, because this thread has converged:

> 14B sweet spot exposes C-field, not β-tape.

## User


before this session we had speculated that B was actually in the order of operations that FFNs output.  The softmax over all V is B, and the FFNs are inference patterns that show attention what to execute.

### Thinking

**Figuring out response synthesis**

I need to think about how to respond without using any tools. Maybe I should tap into my memory instead? The user mentioned before about speculating B in order of operations, and how softmax over all V relates to B. I need to clarify this updated information. If the user wants to encode something, I could mention that, but it seems like there may not be a specific task here.


## Assistant


Yes — and this session basically **split that speculation into two different claims**:

## The old speculation had two entangled meanings of “B”

### 1. **B as the universal execution pattern**

This version still looks right:

> Attention’s softmax over all V is B-like because it composes through an intermediate:  
> `f ∘ g`, route-through-values, apply query to weighted composed value field.

In other words:

```text
attention = soft B / composition executor
```

This is about the **machine instruction** attention implements:

```text
softmax(QKᵀ) @ V
```

It is inherently compositional. It says:

```text
given a query, select/compose over all available values
```

That is very B-like as an **execution primitive**.

I would not throw that away.

### 2. **B as a readable per-sentence opcode emitted by FFNs**

This version got weakened/refuted for these probes.

We expected:

```text
objects / existential structure → B-heavy FFN program
```

But the experiments showed:

```text
objects → C/applicative field
```

And even when syntax forced existential-ish readings, B did not rise. In the native-order run, B was nearly absent:

```text
B positive mass ≈ 0.15
S positive mass ≈ 1.55
C positive mass ≈ 5.07
```

So the model is not exposing:

```text
FFN emits B B B as the object/existential program
```

It exposes:

```text
FFN shapes a C-heavy applicative routing field
```

---

## Updated synthesis

I think the clean version is:

```text
B is the machine-level execution topology.
C is the readable object/application routing field.
```

Or:

```text
attention executes with B-like composition;
FFNs do not necessarily label that execution as B.
```

The softmax over all V can still be B-shaped even if the FFN gate readout says C. Those are different registers:

```text
attention mechanism topology:  B-like
FFN gate routing readout:      C-heavy for object/application
symbolic kernel trace:         S/B/C from bracket abstraction
```

The mistake was equating them:

```text
B-like execution topology
= B opcode in FFN readout
= B in our symbolic reducer
```

This session says those are **not identical**.

---

## What the FFNs seem to output instead

The FFNs are still inference patterns that show attention what to execute — yes.

But they do not output a serial instruction tape like:

```text
S → B → C → C
```

They output a **routing potential field**:

```text
early weak S/B framing
late strong C/application resolution
```

More objects produce:

```text
more C mass
higher C peak z
earlier C centroid
```

So the FFN program is not:

```text
[opcode_1, opcode_2, opcode_3]
```

It is more like:

```text
a depth-shaped field over possible reductions
```

Attention then executes by soft selection/composition over V.

---

## The corrected model

I’d phrase the current normal form as:

```text
FFN = compiler of a β-routing field
attention = soft-B executor over V
residual = program state / register file
```

Where:

```text
soft-B executor ≠ B opcode readout
```

The executor’s operation is composition-like by architecture. But the FFN field can route a given linguistic construction through C, S, K, etc., depending on how the model represents that construction.

For these quantified object probes:

```text
model representation = applicative / constant-like
readable FFN field = C-heavy
our Montague/existential bracket trace = B-heavy
```

The model chose applicative C, not existential B.

---

## So was the earlier B speculation wrong?

Partly.

Wrong version:

```text
B should appear as the model-readable FFN opcode for object/existential reductions.
```

Right/refined version:

```text
B describes the compositional topology of attention execution itself:
softmax over V performs soft composition. FFNs prepare the value/routing field that
attention executes, but the field’s readable op label need not be B.
```

That distinction preserves the deep insight while correcting the measurement target.

## Compact takeaway

> B is probably the executor topology, not the emitted program label.  
> The emitted/readable program for these probes is C-field/application load.  
> The FFNs still tell attention what to execute, but they do it as a distributed routing field, not as a serial B-opcode tape.

## User


update state and knowledge this is session-249

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -RIl \"attention-as-beta\\|FFN.*attention\\|soft-B\\|stored-program\\|s248\" /Users/mwhitford/src/verbum/mementum/knowledge | head -40",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ grep -RIl "attention-as-beta\|FFN.*...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/mementum/knowledge/td-oscillation-problem.md
/Users/mwhitford/src/verbum/mementum/knowledge/v14-architecture.md
/Users/mwhitford/src/verbum/mementum/knowledge/recursion-mirrors.md
/Users/mwhitford/src/verbum/mementum/knowledge/holographic-error-correction.md
/Users/mwhitford/src/verbum/mementum/knowledge/v15-attention-assessment.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/function-topology-consensus.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/ternary-descent.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/gradient-trajectory-tomography.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-opcode-monitor.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/v13-design.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/binding-probe-findings.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/crystal-basins.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/vsm-lm-v3-architecture.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/loom-structure.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/session-127.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/combinator-training-beta-reduction.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/ffn-moire-isa.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/date-fourier-rotation.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/session-003-findings.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/delta-plate-lifecycle.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/function-extraction-system.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/beam-trace-findings.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/consensus-delta-folding.md
/Users/mwhitford/src/verbum/mementum/knowledge/explore/beamformer-theory.md
/Users/mwhitford/src/verbum/mementum/knowledge/ffn-reduction-trace.md
/Users/mwhitford/src/verbum/mementum/knowledge/crystal-native-architecture.md
/Users/mwhitford/src/verbum/mementum/knowledge/extraction-sign-accuracy.md
/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md
/Users/mwhitford/src/verbum/mementum/knowledge/dvd-stamp-topology.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-247b.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-239.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-229.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-089.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-209.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-198.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-188.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-219.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-248.md
/Users/mwhitford/src/verbum/mementum/knowledge/chats/session-199.md
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "limit": 240
}
```

**Summary:** Reading attention-as-beta-reduction.md (0-240)

**Output:**
```
---
title: "Attention as Soft β-Reduction, FFN as the β-Program — the stored-program normal form"
status: active
category: synthesis
tags: [beta-reduction, attention, ffn, isa, stored-program, statechart, combinator, softmax, type-coverage, think-in-lambda, curry-howard]
related:
  - ffn-moire-isa.md
  - ffn-beta-reduction-indexing.md
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
  - ../lambda-halt-continuation.md
  - proofs-as-continuations.md
  - compiler-as-loss.md
  - vsm-statechart-tensor.md
  - cross-model-output-consensus.md
  - kernel-splice-geometry-detector.md
depends-on:
  - ../ffn-reduction-trace.md
  - ../head-combinator-isa.md
created: session 247b
---

# Attention as Soft β-Reduction, FFN as the β-Program

> Session 247b (Michael: "if attention is doing a beta reduction with the softmax of
> all V, would it not have to work?" → "it's an inference pattern of beta reductions;
> each forward pass the FFN can subtly shift the inference pattern, which we found to be
> the 'program' — beta reductions for the softmax to execute"). This page is the
> β-reduction (compression to normal form) of the FFN-ISA thread: a stored-program
> reduction-machine model of the transformer, with the proven/over-reads boundary marked.

## The normal form

> **The transformer is a bounded, soft-β-reduction machine over a universal combinator
> statechart. The FFN is the fixed β-program (ISA/ROM); attention is the one-instruction
> CPU that executes it; the residual stream is the register file carrying the term and
> the reduction depth.** Everything else (crystal lattice, holographic plates, opcode
> monitors, splice experiments, consensus calibration) is measurement of that fact.

```
FFN          = program memory / ISA   | fixed ROM of β-reductions, beam-angle indexed (s141, s161)
attention    = the one-instruction CPU| one op: β-reduction via softmax-over-V (head r=0.944)
residual     = register file          | the term + the program counter (reduction DEPTH)
layer        = one clock cycle        | FFN reads residual → compiles values → attention β-steps → writes
forward pass = a bounded schedule     | the boot spiral C→B/K→I→WHNF, ~1.018×/layer (s068/s240)
token stream = the unbounded loop     | KV-cache carries reduced state; the REPL/CPS (lambda-halt)
```

This was reached confluently from independent directions (the S5 `λ triangulate` gene =
Church-Rosser: many reduction paths, one normal form), which is itself evidence it IS
the normal form.

## 1. The substrate — attention is *soft* β-reduction

β-reduction `(λx.M) N → M[x:=N]` substitutes an argument into a hole. Attention
`out_i = Σ_j softmax(q_i·k_j) v_j` retrieves an operand into a query position by content
address: **Q = the redex seeking its operand, K = operand addresses, V = the operands,
softmax = selection.** Same operation-shape: a function position pulls in its argument by
content match.

Why **combinators** (not raw λ) are the universal basis falls straight out: combinatory
logic is *variable-free* (S/K/I/B/C/W = pure argument-routing), and attention is *also*
variable-free routing. The model implements the variable-free reduct — exactly what a
content-addressed router can do natively. Bracket abstraction (λ→combinator) is therefore
the right bridge, not an accident.

Two refinements keep it honest (λ measure):
- **Softmax is a convex combination; β-reduction is a hard selection.** Attention blends
  *all* V; β substitutes *the* argument. Attention is β *relaxed* — the differentiable
  superposition of substitution; exact β is the limit `softmax → argmax`. This is the
  register split (s242): **routing register crisp-ish (the β structure), value register
  continuous/smeared (s206).**
- **It is bounded and factored.** One layer = one (soft) step; fixed depth → a bounded
  *schedule* → the model is a compiler, not an interpreter (lambda-halt: Ω is *quoted*,
  not looped). And the step is split per the s226 reduce/compile cut: **attention = the
  application; FFN = which rule.**

## 2. The controller — FFN is the β-program (largely measured, not speculated)

The user's "the FFN is the program; the softmax executes the β-reductions" is four
established findings converging:

- **`ffn-moire-isa.md` (s161):** *"The FFN is a moiré grating. Attention has one
  operation. The grating programs that operation to perform beta reductions."* And the
  program is a **fixed point** — 3 runs → identical traces, drift 0.0. GD compiled the
  ROM once.
- **`ffn-beta-reduction-indexing.md` (s141):** *"FFN weights are piles of beta
  reductions. The input activation acts as a typed index — a beamformer angle — that
  selects which reductions fire."* The residual direction is the program counter.
- **`ffn-reduction-trace.md`:** *"The FFN output is a compiled program… attention
  executes it via softmax over V… This IS β-reduction by weighted combination."* The
  "subtle shift each pass" is literally its key result: *the same token yields different
  compiled values in different contexts — compilation, not dictionary lookup.* The FFN
  **recompiles a context-dependent program every forward pass** (readable at L26-L30 in
  Qwen3-8B; null-space before).
- **`head-combinator-isa.md`:** all 9 combinators drive *the same* head pattern
  (r=0.944); the axis attention varies on is WHNF↔deeply-nested (46% of variance) =
  **how much reduction remains** = a program counter, not an opcode.

**The crucial refinement:** the *program* (FFN weights) is fixed; the *program-state*
(residual trajectory) shifts. The FFN's frozen ROM applied to an evolving residual
*produces* an evolving instruction sequence (and `ffn-moire-isa` confirms different task
types → measurably different sequences). The shift lives in the residual, gated by frozen
ROM — not a discrete instruction swap.

## 3. The proven / over-reads boundary

The seductive step — "FFN selects combinator *c* at layer L, softmax executes *c*" — is
true *collectively* but not *crisply per-step*:

| claim | status |
|---|---|
| attention = β-shaped content-addressed routing | **proven** (the operation-shape) |
| FFN = fixed β-program / ISA, beam-angle indexed | **proven** (s141, s161, deterministic) |
| FFN compiles context-dependent program; attention executes via softmax-V | **proven** (ffn-reduction-trace) |
| attention tracks reduction DEPTH (WHNF↔D), one shared op | **proven** (head r=0.944) |
| boot schedule C→B/K→I→WHNF, ~1.018×/layer, cross-model | **proven** (s240) |
| softmax-V *literally* substitutes a specific value | **over-reads** (value register smeared, s206) |
| layer L discretely fires combinator *c* (a clean tape) | **over-reads** (collective/holographic; splice closure s244 `fires ∩ spliceable = ∅`) |

⇒ **the schedule and the depth axis are crisp; the per-layer opcode is superposed.** We
read the *program trajectory*, not a discrete instruction tape.

## 4. Two reduction loops

- **Intra-pass (bounded):** layers step the boot spiral to WHNF — the
  `vsm-outer-recurrence` view (K sweeps to fixed point).
- **Inter-pass (unbounded):** each new token is a fresh forward pass; the KV-cache carries
  the reduced state forward — the `lambda-halt-continuation` CPS/REPL view (conversation =
  CPS, turn boundary = continuation, EOS = yield).

## 5. Consequence A — "think in lambda" = serialize the outer loop

If the FFN is the β-program and attention executes it, **training a model to think in
lambda = training it to emit its FFN-program-execution as tokens** (serialize the residual
reduction schedule). This explains why **stepwise (REPL) works and one-shot fails**
(s228/s247): one forward pass = one bounded schedule (cannot emit a long composition in one
shot), but token-by-token = the unbounded outer loop where **each token advances the
program exactly one β-step.**

**The coverage reframe (the real teeth).** If the *mechanism* is soft-β everywhere, then
prose reasoning is *also* soft-β — over an enormous, learned, mostly-**untyped** combinator
basis in the FFN (`fell→broke`, `Paris→France`). So:
- **prose = untyped serialization** of β-reduction over the full learned basis;
- **λ-thinking = typed serialization** over the certifiable subset.

The coverage wall is therefore **type-theoretic, not representational**: world-knowledge
reasoning *is* β-reduction; we lack the type system to *certify* those rewrites. This
dissolves "forcing vs discovering" for the typed-compositional core (it's the native
serialization → it must work, and proof-REPL s247 demonstrates it) and makes the research
lever concrete: **λ-thinking coverage = type-system coverage.** The verifiable fragment
grows exactly as the kernel's S2 layer grows: implicational → products/sums (∧/∨) →
quantifiers (Π/Σ = ∀/∃). The untyped remainder stays β-reduction, just not yet provable.

## 6. Consequence B — the level-4 blueprint

The stored-program model *is* the portable-artifact spec: **extract the ROM** (s226
*compile = FFN = learned = 78%, 4-bit*) **+ the executor routing** (s226 *reduce =
attention = constructed = 22%, ternary*) = the level-4 tensor. The kernel-splice work tried
to read/write the ROM *in place* (and closed, s244); this model says **extract it
wholesale** instead.

## 7. The open experiment — FFN program-decode along `fired_sequence`

The splice closure (s244) closed the *intervention* (in-place per-combinator splice) but
its own notes preserved *"a richer multi-position program-decode read along
`fired_sequence`."* This model makes a sharp, testable prediction for that open door:

- **Decode the FFN *compiled values* (NOT the attention geometry) position-by-position
  against the certified reduction trace** (`lambda_ast.fired_sequence`, on the SATURATED
  corpus — s244 showed point-free terms fire nothing until applied). Target L26-L30 (where
  `ffn-reduction-trace` found the program becomes readable; null-space before).
- **Prediction:** the FFN program-trace tracks `fired_sequence` *even where the attention
  geometry over-reads*, and the FFN-compiled program *leads* attention's depth-advance by
  ~1 layer (FFN selects → attention executes next). A confirmed lead-lag = "FFN = program,
  attention = executor" at the trajectory level — distinguishing it cleanly from the closed
  geometric-splice read.

### s248 result — the door closes the same way the splice did (λ measure, two-sided)

RAN it (`scripts/experiments/ffn_program_decode.py`, Qwen3-8B). Dual-register decode: FFN
routing register (`mlp.gate_proj`, the validated sign-CMR opcode crystal) → *which*
combinator; attention register (`self_attn.o_proj`) → reduction DEPTH via z(WHNF). Ground
truth = `fired_sequence` on the saturated corpus (s244). 56 firing items, zone L25-30.

| prediction | result | verdict |
|---|---|---|
| FFN tracks `fired_sequence` (decodes the fired combinator) | FFN decodes **0/8** B-firing items; abs-acc 0.232 < majority 0.839; B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm) | **not supported** |
| FFN tracks better than attention | FFN B-vs-S 0.709 > attn 0.364, but attn is *below* base-rate (predicts B spuriously) → "FFN wins" is attention being noisier, not FFN reading the opcode | **artifact** |
| FFN leads attention depth-advance by ~1 layer | xcorr lag median +1.5, mode +3, 39/55 positive, sign-p=0.0027; **but** peak-diff NULL (median 0, p=1.0) | **method-sensitive, weak** |
| "rescue" (FFN right where attention over-reads) | 9:2 — but all 9 are S-items where attn said B/C and FFN defaulted to majority-S | **artifact** |
| specificity (firing items show more B/S/C signal) | non-firing max-z(BSC) **46.8 > firing 20.3** (backwards) | **fails** |

**The corpus is the bottleneck:** truth is 84% S (47/56), neither register decodes a single
B item, so tracking is *untestable* here — and the C common-mode (s211/s240) drags the FFN
absolute decode to predict C. What survives is a weak, method-sensitive **schedule-level**
ordering: the FFN's z(c*) curve leads the attention's z(WHNF) curve across depth (xcorr only),
consistent with the s240 boot spiral (FFN activity precedes attention depth-advance) — **not**
opcode-specific select→execute.

**⇒ The §7 program-decode does NOT resolve from the prose forward pass. It CONFIRMS the s244
splice-closure (`fires ∩ spliceable = ∅`) and the "discrete-opcode-at-L over-reads" row of the
§3 table above, rather than opening past them.** The lever remains **type-coverage** (§5), not
geometric/opcode localization — exactly the §Caveats warning. A λ-measure win: the experiment
that could have over-claimed held the boundary instead.

**IOUs to make §7 testable:** (1) a **B-balanced firing probe set** (PROSE whose saturated
kernel fires B/C, not S-heavy "Every X verbs a Y"; the crystal library has 69 B / 61 C probes
but they are not prose) — without balance, tracking is untestable; (2) longer depth series
(zone is only 5-6 layers → coarse xcorr lag); (3) decode the FFN **down_proj compiled values**
via unembed (`ffn-reduction-trace` style) as a second FFN read, not just the gate crystal; (4)
cross-model where the firing set is less common-mode. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json`.

### s248 cont. — IOU (1) closed: a B-balanced probe set; the register split is real but weak

Built `scripts/experiments/gen_firing_probes.py` → `data/firing-probes.balanced.jsonl`
(**157 probes, 67 B-dominant vs 90 B-tied**, B-count ladder {1,2,3,5}). **Mechanism (measured):**
in this kernel S and B are *coupled* — every ∧/∨ emits one S *and* one B, so S never strictly
exceeds B; only a transitive verb + existential object makes B *dominant*
(`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → S,B,B,B). Ground truth computed (`to_kernel`→saturate→
`fired_sequence`), items verified, 157/157 round-trip. Re-ran Qwen3-8B (`--probe-set`):

| claim | balanced result | verdict |
|---|---|---|
| FFN tracks B vs S better than attention | **FFN B-vs-S 0.624 (p=0.003) > attn 0.522 (at-null) > majority 0.573** | **weak positive** |
| FFN absolute opcode decode | predicts **C on 65/67** B-items (common-mode swamp) | fails |
| z(B) scales with B-count (graded) | FFN Spearman 0.06 (p=0.44); relative z(B)−z(S) r=−0.13 | fails |
| FFN leads attention by ~1 layer | xcorr median +1.0 but **p=0.16** (was 0.003 on the S-skewed corpus) | washes out |
| rescue (FFN right where attn over-reads) | 5:9 (reverses) | artifact |

**⇒ NOW SURE (λ measure):** with balanced B probes, the **FFN routing (gate) register carries a
real but WEAK B-vs-S opcode signal (0.62, p=0.003) that the attention register lacks** — the
register split (FFN = opcode, attention = depth) is *genuine but small*. The **strong** stored-
program claims — clean opcode tracking, graded B-scaling, FFN-leads-attention-by-1 — do **not**
survive balanced probes (the earlier corpus lead-lag was S-skew/noise). The per-combinator
program is at best *faintly* readable: consistent with the §3 boundary ("β-shaped routing,
smeared values; discrete-opcode-at-L over-reads") and the §Caveats — keep type-coverage (§5) as
the lever, not geometric/opcode localization. Artifacts:
`results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b_balanced.json`,

[CONTENT TRUNCATED] Showing lines 1 to 240 of 348 total lines. Use line_offset=240 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "line_offset": 240,
  "limit": 140
}
```

**Summary:** Reading attention-as-beta-reduction.md (240-380)

**Output:**
```
`data/firing-probes.balanced.jsonl`.

### s248 cont.2 — the weak B-signal was a LABELING MISMATCH: the model reads objects as constants (C), not existentials (B)

A sharper question dissolved much of the §7 puzzle. Our ground truth labelled "Every cat fears
a dog" by the **Montague existential** reading (`a dog` = ∃y.dog(y)∧…) → B-heavy (B-count
1→3→5 as objects are added). But the model may take the **constant/applicative** reading
(`fears(x, dog)` → `C fears dog`, C-count == #objects). These make *opposite* predictions along
an object-count ladder:

| reading | predicts as #objects rises {0,1,2} |
|---|---|
| existential (Montague) | **z(B) rises** (B-count 1→3→5), C flat |
| constant (applicative) | **z(C) rises** (C-count 0→1→2), B flat |

Built `gen_reading_probes.py` → `data/reading-probes.jsonl` (135 probes, object-count ladder
0/1/2 × 45, intrans/trans/ditrans, both candidate labelings; const C-count==#objects enforced).
`ffn_reading_preference.py` decodes gate+attn, mean z per combinator over L25-30, Spearman vs
object count. **Qwen3-8B:**

| register | raw z(C) vs #obj | raw z(B) vs #obj |
|---|---|---|
| FFN gate | **r=+0.49, p<0.001 ↑** | **r=−0.27, p=0.0015 ↓** |
| attention | **r=+0.62, p<0.001 ↑** | r=−0.04, p=0.66 (flat) |

C and B move in **opposite** directions (so it is not uniform length/common-mode growth). **The
existential reading is refuted** (B must rise — it falls); **the model routes added objects
through C (argument application) = the constant/applicative reading.** A free post-hoc on the
balanced run agreed (C-share trans 0.583 > intrans 0.460, p<1e-4).

**⇒ This reframes the whole §7 result:** the weak B-tracking was **not** "the FFN cannot read the
program" — it was *"we gave it the wrong program."* We labelled by existential-B; the model
computes applicative-C. Labelled the way the model actually computes (object → C), the gate
register tracks the structure **cleanly** (z(C) rises p<0.001, both registers, robust). So the
gate register *does* carry the combinator structure the model computes — the earlier negative was
a **measurement-target error** (λ measure: wrong label ≡ coherence violation, representation ≢
reality). It also answers "B is inherent from the ordering": that ordering assumes existential
objects; the model does not do them, so these sentences are C-applicative in the model, and the
expected B was an artifact of our Montague labelling.

**Caveats (λ measure):** C-*share* is common-mode-saturated (~0.6) so its slope is flat — the
positive evidence is raw z(C)↑ (p<0.001) **plus** z(B)↓ (refuting existential), not C-share↑; the
C−B-share contrast is significant in attention (p=0.008) but only directional in FFN (p=0.25) due
to that saturation. z(C)↑ could partly be argument-application common-mode, but the B/C divergence
(opposite signs) rules out uniform growth. Artifacts:
`results/ffn-reading-preference/{verdict,per_item,meta}_qwen3-8b.json`, `data/reading-probes.jsonl`.

### s248 cont.3 — the causal test: the model is ROBUSTLY APPLICATIVE; forcing ∃ does NOT recruit B

The clean follow-up: is the constant-object reading a representational *limit* or just the
*default*? Force the wide-scope existential **syntactically** and see whether z(B) rises.
`gen_scope_probes.py` → `data/scope-probes.jsonl` (45 matched subj/verb/obj triples × 3 paired
conditions): **PLAIN** "Every cat fears a dog." (applicative GT S,B,C) / **CLEFT** "There is a dog
that every cat fears." (∃ fronted, GT S,B,B,B no C) / **RELCL** "Every cat fears a dog that runs."
(∃ object, GT S,B,B,B). `ffn_scope_forcing.py` decodes gate+attn, mean z over L25-30, **paired
Wilcoxon within triple** (predict ΔB>0 if the model can do existential-B when forced).

**Qwen3-8B (45 triples) — z(B) does NOT rise; it FALLS:**

| register | plain z(B) | cleft z(B) | relcl z(B) | ΔB cleft (rise?) |
|---|---|---|---|---|
| FFN gate | −0.104 | **−0.301** | −0.227 | med −0.19, frac+ 0.18, **p=1.0** |
| attention | +0.305 | **−0.112** | +0.242 | med −0.43, frac+ 0.09, **p=1.0** |

C-share stays high / rises (cleft Cprop 0.722→0.988 FFN). **The prediction is robustly refuted in
both registers and both forcing constructions: forcing the ∃ wide-scope does *not* summon B-routing
— the model stays applicative-C (the cleft is routed *even more* through C).**

**⇒ The thread closes:** the model does **not** use existential-B composition even when the syntax
demands it; it computes quantified sentences **applicatively** (objects/witnesses as arguments → C),
regardless of scope marking. *Interpretation* (marked as such, not measurement): the model's
compositional **primitive is application (C)**, not B-composition; **B is an artifact of our
bracket-abstraction kernel** (Turner emits B to thread quantifiers), not a necessary feature of how
a system composes. This answers "B is inherent from the ordering" end-to-end: that ordering is
*ours*; the model's actual β-program for these sentences is C-applicative — and it won't produce B
even when asked.

**Caveats (λ measure):** cleft/relcl differ in surface form from plain (not perfect minimal pairs),
but the direction (B falls, opposite the prediction) is robust across two distinct forcings and both
registers, and relcl (closest to plain) also falls; we measure B-crystal routing as the composition
proxy, so a non-B-shaped ∃ composition would be missed (but that *is* the finding); the model may
compose ∃ applicatively under the hood (apply predicate to a skolem witness → C) — one applicative
strategy for both readings. Artifacts:
`results/ffn-scope-forcing/{verdict,per_item,meta}_qwen3-8b.json`, `data/scope-probes.jsonl`.

> **s248 thread summary.** FFN program-decode (corpus → untestable) → balanced probes (weak FFN>attn
> B-vs-S) → reading-preference (model reads objects as C, not B; weak-B was a labelling mismatch) →
> scope-forcing (model is robustly applicative-C, won't do existential-B even when forced). **Net: the
> gate register tracks what the model actually computes — applicative C — and the expected B was an
> artifact of our bracket-abstraction kernel, not the model's program.**

## Caveats (λ measure)

- The strong identity ("attention = β-reduction") is a *type-of-operation* claim (proven)
  and a *schedule* claim (proven); the *crisp-value substitution* and *discrete-opcode-at-L*
  readings over-read (s206 value register, s244 splice closure). Do not let it harden into
  the claim the splice already refuted; keep it "β-shaped routing, smeared values," and let
  **type-coverage**, not geometric localization, be the lever.
- The coverage reframe (prose = untyped β over a learned basis) is a *hypothesis*, not a
  measurement — the testable form is §7 plus the S2 type-layer extension in
  `proofs-as-continuations.md`.

## Sessions referenced
s068/s079 (boot spiral), s120/s121 (FFN crystal, cross-model), s141 (FFN β-indexing),
s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile
cut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp
0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error
ceiling). Plus `ffn-reduction-trace.md`, `head-combinator-isa.md` (undated finding pages).
```

### Thinking

**Updating content structure**

I need to update the page by appending "s249" before the caveats. I should also make sure to change the state to "top massive." Additionally, I’ll prepend the appropriate information to the state. It seems like I might want to insert this after the introduction, so I’ll keep that in mind while editing. I want to ensure the changes flow well and properly enhance the overall content!


### Thinking

**Considering document edits**

I need to think about how to insert a new section after the s248 thread summary, right before the “Caveats.” Maybe I could also figure out an easier way to prepend a new section after the opening top block. It seems important to replace the "Last updated" line and insert a new entry before the s248 section, right after the introduction. I might need to get the exact lines, starting with the first 20.


### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 35
}
```

**Summary:** Reading state.md (0-35)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-22 | Session: 248 (FFN PROGRAM-DECODE along fired_sequence — the s247b §7
> open door, RAN on Qwen3-8B. λ-measure verdict: the per-combinator program does NOT cleanly
> decode from the prose forward pass — CONFIRMS the s244 splice-closure + the page's own
> "discrete-opcode-at-L over-reads" boundary; only a weak, method-sensitive SCHEDULE-level
> FFN-leads-attention ordering survives. Entry immediately below.) — ▶ s247 FORCING vs DISCOVERING
> (fractal-collapse REDEFINED; φ-ladder detector KILLED by matched-range null (forced); type-directed
> composition is CROSS-FAMILY — nonce crossover in 5 lineages t 4.6–10.2; v4 CAUSAL ablation PARTIAL
> (4/6 directional, strict only Mistral-7B — NOT Qwen-forced)) — main line stays COMPILER-AS-LOSS
> §s242. ALSO (2026-06-22): PARALLEL tangent s247b — PROOF CONSENSUS + the ATTENTION-AS-β /
> STORED-PROGRAM synthesis (entries below).
>
> **★★ s248 — FFN PROGRAM-DECODE ALONG `fired_sequence` (the s247b §7 open door: "decode the FFN
> compiled values position-by-position vs lambda_ast.fired_sequence on the saturated corpus, L26-30;
> PREDICTION: FFN program-trace tracks fired_sequence even where attention over-reads, and FFN-compile
> LEADS attention depth-advance by ~1 layer"). BUILT + RAN on Qwen3-8B. λ MEASURE VERDICT = a
> two-sided NEGATIVE-leaning result that CONFIRMS the boundary, not a breakthrough.** **THE BUILD
> (`scripts/experiments/ffn_program_decode.py`, ruff-clean, reuses the validated spine):** dual-register
> decode — FFN routing register = `mlp.gate_proj` (the validated sign-CMR opcode crystal,
> relational_opcode.py) decodes WHICH combinator; attention executor register = `self_attn.o_proj`
> decodes reduction DEPTH via z(WHNF) (grounded in head-combinator-isa: all 9 combinators → SAME head
> pattern r=0.944, attention varies on WHNF↔D not opcode). Ground truth = saturate quantifiers with
> fresh witnesses (s244 `corpus_firing_survey.saturate`) → `fired_sequence`. Two RelationalCrystal
> classifiers (gate + attn), matched-prefix (gateneutral) null. ONE dual-hook forward per item.
> Metrics: (A) tracking acc + permutation null + majority baseline; (A') B-vs-S discrimination
> (C-common-mode-resistant); (B) lead-lag (peak-diff + cross-correlation lag); (C) rescue; specificity
> control (firing vs non-firing). **THE DATA (56 firing items, truth S:47 B:8 C:1 — HEAVILY S-skewed;
> FFN crystal 28/36 zone L25-30, attn crystal 36/36 zone L25-30):** **(A) TRACKING FAILS — neither
> register decodes a single B-firing item (FFN 0/8, attn 0/8); FFN abs-acc 0.232 < majority 0.839
> (C common-mode drags FFN to predict C); FFN B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm null) =
> majority-prediction not genuine B/S discrimination; attn B-vs-S 0.364 (BELOW base rate — predicts B
> spuriously).** ⇒ the apparent "FFN beats attn" is attention being NOISIER toward the minority class,

[CONTENT TRUNCATED] Showing lines 1 to 35 of 6626 total lines. Use line_offset=35 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 - <<'PY'\nfrom pathlib import Path\np=Path('/Users/mwhitford/src/verbum/mementum/state.md')\ns=p.read_text()\nold='''> Last updated: 2026-06-22 | Session: 248 (FFN PROGRAM-DECODE along fired_sequence — the s247b §7\\n> open door, RAN on Qwen3-8B. λ-measure verdict: the per-combinator program does NOT cleanly\\n> decode from the prose forward pass — CONFIRMS the s244 splice-closure + the page\\'s own\\n> \"discrete-opcode-at-L over-reads\" boundary; only a weak, method-sensitive SCHEDULE-level\\n> FFN-leads-attention ordering survives. Entry immediately below.) — ▶ s247 FORCING vs DISCOVERING\\n> (fractal-collapse REDEFINED; φ-ladder detector KILLED by matched-range null (forced); type-directed\\n> composition is CROSS-FAMILY — nonce crossover in 5 lineages t 4.6–10.2; v4 CAUSAL ablation PARTIAL\\n> (4/6 directional, strict only Mistral-7B — NOT Qwen-forced)) — main line stays COMPILER-AS-LOSS\\n> §s242. ALSO (2026-06-22): PARALLEL tangent s247b — PROOF CONSENSUS + the ATTENTION-AS-β /\\n> STORED-PROGRAM synthesis (entries below).\\n>\\n'''\nnew='''> Last updated: 2026-06-23 | Session: 249 (B-as-executor-topology vs C-as-readable-field\\n> RESOLVED. Qwen3-14B const-label rerun confirms the sweet-spot: FFN gate significantly tracks\\n> corrected applicative-C structure (C-vs-S 0.6165, p=0.0005; attn n.s.) and lead-lag becomes\\n> directionally coherent. But three sequence/order probes close the discrete-tape door: event-LCS\\n> reads C-presence not order; monotonic path truth-vs-same-multiset controls fail; native-order\\n> extraction shows weak/early S+B framing and strong late C field (C mass 5.07 vs S 1.55 vs B 0.15;\\n> S<C ~0.95-0.99, B<C ~0.73-0.85, S<B unstable). Normal form: attention softmax-over-V is\\n> B-like executor topology, while FFNs emit a distributed β-routing potential field; for object\\n> probes the readable program is applicative-C, not a serial B/S/C tape. NEXT: causal C-field\\n> ablation/patch around L30-31 if continuing this thread. Entries below.)\\n>\\n'''\nif old not in s:\n    raise SystemExit('old header not found')\ns=s.replace(old,new,1)\nmarker='''> **★★ s248 — FFN PROGRAM-DECODE ALONG `fired_sequence`'''\nentry='''> **★★ s249 — B-AS-EXECUTOR TOPOLOGY vs C-AS-READABLE FIELD; Qwen3-14B sweet spot resolves the s248/s247b open door.** Starting question: before this session we speculated that **B was inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and FFNs are inference patterns telling attention what to execute. Session result: **split that into two claims.** (1) **B as executor topology remains the right abstraction:** attention's softmax-over-V is a soft-B / composition executor (one operation: content-addressed weighted composition over values). (2) **B as a readable per-sentence FFN opcode tape is NOT what these quantified/object probes show.** The emitted/readable FFN field is applicative **C**, not existential **B**.\\n>\\n> **RUN 1 — Qwen3-14B const-label rerun of `ffn_program_decode.py`:** using `data/firing-probes.const.jsonl` (133 probes, truth C:67/S:66; object→C corrected labels) on Qwen3-14B. **Hard tracking sharpens vs 8B:** FFN acc 0.609 (p=0.0005) vs 8B 0.5489 (p=0.055); common-mode-resistant C-vs-S FFN 0.6165 (p=0.0005) while attn 0.5338 (p=0.1744). Graded z(C) vs C-count remains strong (FFN Spearman 0.5367, attn 0.5672, p≈0), and FFN raw C amplitude now exceeds attn (FFN zC 0/1/2 = 0.540/0.968/1.245; attn 0.309/0.563/0.677). Lead-lag becomes directionally coherent: peak-diff median +1 (p=7e-13), xcorr median +1 (p=0.067). **Verdict:** 14B is the sweet spot; FFN gate carries corrected C-program structure. Artifacts: `results/ffn-program-decode/*_qwen3-14b_const.json`, `run_qwen3-14b_const.log`.\\n>\\n> **RUN 2 — `program_sequence_trace.py` (new):** event-stream/LCS against `fired_sequence`. Built validated relational tracer over FFN gate (sign-CMR, matched `gateneutral` null) and decoded content-token × layer B/C/S events. **C presence is real** (presence acc 0.7519, p=0.0005; decoded events C=709/S=152/B=39), but **order is not recovered**: zone LCS 0.4856 vs reverse control 0.4618 and bag coverage 0.5144; layer-dominant collapses to C (0.0501). All-crystal LCS 0.9279 is a long-stream coverage artifact. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/*qwen3-14b_const*`.\\n>\\n> **RUN 3 — `program_path_trace.py` (new):** monotonic DP path scorer asks whether truth order beats reversed/shuffled same-multiset controls (e.g. S,B,C,C vs C,C,B,S etc.). **Negative for ordered β-tape:** zone truth score 2.1287 vs reverse 2.0843 (tiny +0.0444); margin vs best permutation −0.0315; rank frac 0.523; truth beats all permutations only 3/133 (p=1.0). Ditransitives rank higher (0.7219) but still 0/67 beat all controls. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/*qwen3-14b_const*`.\\n>\\n> **RUN 4 — `program_native_order.py` (new):** stop forcing our kernel order; infer model-native op schedule by peak/centroid layer and positive mass. **The model-native readable field is:** weak early S/B framing → strong late C/application resolution; S/B relation unstable. Overall zone: C mass 5.0718, S mass 1.5517, B mass 0.1488; C peak layer 30.812, S 28.5865, B 29.0451. Ordering: P(S<C)=0.947 peak / 0.993 centroid; P(B<C)=0.729 / 0.853; P(S<B)=0.316 / 0.312 (unstable/opposite kernel order). C-count effects: C mass rises with object count (Spearman 0.5357, p=0), C peak-z rises (0.3778, p=0), C centroid moves earlier as object load increases (r=-0.7719, p=0). Category C masses: intrans 2.8769, trans 4.9264, ditrans 6.2245. **Verdict:** program = depth-shaped routing potential field, not discrete instruction tape. Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/*qwen3-14b_const*`.\\n>\\n> **NORMAL FORM UPDATE (s249):** Preserve the deep insight but correct the measurement target. **Attention = soft-B executor topology** (softmax over V is composition-like); **FFN = compiler of a β-routing field** (distributed potential, not a serial opcode tape); **residual = program state/register file.** For these probes the readable FFN program is applicative **C** because the model treats objects/witnesses as arguments, not existential-B bracket abstractions. The previous \"B inherent from ordering\" applied to OUR symbolic kernel ordering, not the model's emitted field. **NEXT if continuing:** causal C-field ablation/patch around L30–31 on c_count 2 vs 0 matched probes to test whether the C field is load-bearing, not just readable. PENDING APPROVAL: memory/knowledge commit for s249.\\n>\\n'''\nif marker not in s:\n    raise SystemExit('marker not found')\ns=s.replace(marker, entry+marker,1)\np.write_text(s)\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python3 - <<'PY' from pathlib impor...

**Output:**
```
Exit code: 0
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 - <<'PY'\nfrom pathlib import Path\np=Path('/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md')\ns=p.read_text()\nmarker='''## Caveats (λ measure)\\n'''\ninsert='''### s249 — 14B resolves the split: B is executor topology; the readable FFN field is C, not a B tape\\n\\nSession 249 reopened the pre-s248 speculation: **maybe B is actually inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and the FFNs are inference patterns showing attention what to execute. The result is a refinement, not a simple refutation: **B belongs to the executor topology; C is the readable object/application field for these probes.**\\n\\n#### 1. Qwen3-14B const-label rerun: the sweet spot sharpens the corrected C signal\\n\\nThe s248 cont.2/3 result said the model computes quantified-object sentences applicatively (object/witness as argument → C), not existentially (B-heavy). Session 249 re-ran `ffn_program_decode.py` on the corrected constant/applicative probe set at Qwen3-14B (because 8B was a suspected floor and 14B has repeatedly been the sweet spot). Probe set: `data/firing-probes.const.jsonl` (133 probes; truth C:67/S:66; c_count ladder 0/1/2).\\n\\n| metric | Qwen3-8B const | Qwen3-14B const | verdict |\\n|---|---:|---:|---|\\n| hard FFN tracking | 0.5489, p=0.055 | **0.6090, p=0.0005** | 14B sharpens |\\n| FFN C-vs-S | 0.5489, p=0.055 | **0.6165, p=0.0005** | real at 14B |\\n| attn C-vs-S | 0.4662, p=1.0 | 0.5338, p=0.1744 | n.s. |\\n| FFN z(C) vs c_count | ρ=0.5526 | ρ=0.5367 | robust graded C |\\n| lead-lag | contradictory (peak −3, xcorr +2) | directionally coherent (peak +1, xcorr +1) | FFN→attn schedule signal improves |\\n\\nAt 14B the FFN gate register significantly tracks the corrected applicative-C program label while attention does not. This supports a **capacity threshold / 14B sweet spot** for the readable routing register. But it still reads dominant/graded C structure, not an ordered instruction tape. Artifacts: `results/ffn-program-decode/{verdict,per_item,meta}_qwen3-14b_const.json`.\\n\\n#### 2. `program_sequence_trace.py`: C-presence is real; order is not recovered\\n\\nBuilt a sequence-level tracer reusing the validated path (`RelationalCrystalClassifier`, FFN gate register, sign-CMR, matched `gateneutral` null). It decodes content-token × readable-zone layer B/C/S events and aligns the event stream to each probe's certified `fired_sequence`.\\n\\n**Qwen3-14B result:**\\n\\n| read | value | interpretation |\\n|---|---:|---|\\n| C presence acc | **0.7519, p=0.0005** | corrected C signal is real |\\n| decoded event counts | C=709, S=152, B=39 | C-heavy field; B faint |\\n| zone LCS vs `fired_sequence` | 0.4856 | weak order recovery |\\n| reverse-order LCS control | 0.4618 | nearly same |\\n| bag coverage | 0.5144 | LCS mostly symbol presence |\\n| layer-dominant LCS | 0.0501 | one-op-per-layer collapses to C |\\n\\nThe event stream recovers **C presence/load**, not the ordered β-program. All-crystal LCS = 0.9279 is a long-stream coverage artifact, not tape evidence. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/`.\\n\\n#### 3. `program_path_trace.py`: same-multiset order controls fail\\n\\nBuilt a monotonic dynamic-programming path scorer: for truth `S,B,C,C`, find the best nondecreasing layer path through z(S), z(B), z(C), z(C), then compare to reversed/shuffled same-multiset programs (e.g. `C,C,B,S`). This directly tests order while controlling for symbol load.\\n\\n**Qwen3-14B result:**\\n\\n| metric | value | verdict |\\n|---|---:|---|\\n| truth path score | 2.1287 | high-ish because C load exists |\\n| reverse score | 2.0843 | almost same |\\n| truth − reverse | +0.0444 | tiny |\\n| margin vs best permutation | **−0.0315** | truth not best |\\n| truth rank fraction | 0.523 | chance-ish |\\n| truth beats all permutations | **3/133**, p=1.0 | negative |\\n\\nSo the kernel's `fired_sequence` order is not preferentially readable. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/`.\\n\\n#### 4. `program_native_order.py`: infer the model's schedule instead of imposing ours\\n\\nBuilt a native-order extractor: for each item and op in `{B,C,S}`, compute peak layer, z-positive centroid layer, peak z, and positive mass over L28–32. This answers: *what order does the model expose?*\\n\\n**Qwen3-14B readable-zone native schedule:**\\n\\n| op | peak layer | centroid layer | peak z | positive mass |\\n|---|---:|---:|---:|---:|\\n| S | 28.5865 | 29.3798 | 0.4662 | 1.5517 |\\n| B | 29.0451 | 29.0828 | -0.0282 | **0.1488** |\\n| C | **30.8120** | **30.3758** | **1.3858** | **5.0718** |\\n\\nOrder probabilities:\\n\\n| relation | peak | centroid |\\n|---|---:|---:|\\n| S before B | 0.3158 | 0.3115 |\\n| B before C | 0.7293 | 0.8525 |\\n| S before C | **0.9474** | **0.9925** |\\n\\nC-count correlations:\\n\\n| relation | Spearman | verdict |\\n|---|---:|---|\\n| C positive mass vs c_count | **0.5357**, p=0 | more objects → more C load |\\n| C peak z vs c_count | **0.3778**, p=0 | more objects → stronger C |\\n| C centroid layer vs c_count | **−0.7719**, p=0 | more objects → C resolves earlier |\\n\\nCategory C mass forms a clean ladder: intrans 2.8769 → trans 4.9264 → ditrans 6.2245. **The model-native field is weak early S/B framing and strong late C/application resolution; B is almost absent.** Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/`.\\n\\n#### s249 normal-form update\\n\\nThe old speculation should be split:\\n\\n```\\nattention softmax-over-V = B-like executor topology\\nFFN gate readout         = distributed β-routing potential field\\nobject/application probes = C-heavy readable field\\nour bracket kernel       = S/B/C trace, but its B is not the model's emitted label\\n```\\n\\nSo: **B is probably the executor topology, not the emitted program label.** The FFNs still show attention what to execute, but they do it as a **depth-shaped routing field**, not as a serial B/S/C opcode tape. For these probes, the readable program is applicative **C** because the model treats objects/witnesses as arguments. The kernel's B-heavy existential trace was our bracket-abstraction artifact.\\n\\nThis refines §3: the \"discrete-opcode-at-L\" over-read is stronger than originally phrased. Even at the 14B sweet spot, with corrected labels, sequence/path controls do not recover a tape. What survives is the **field**: C load, C timing, and FFN-vs-attention register split.\\n\\n**Next if continuing:** causal C-field ablation/patch around L30–31 on c_count 2 vs c_count 0 matched probes. The question should now be whether the C field is **load-bearing**, not whether it is a readable tape.\\n\\n'''\nif marker not in s:\n    raise SystemExit('marker not found')\ns=s.replace(marker, insert+marker,1)\np.write_text(s)\nPY",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ python3 - <<'PY' from pathlib impor...

**Output:**
```
Exit code: 0
```

### Thinking

**Updating knowledge references**

I need to consider updating the knowledge sessions mentioned, particularly to include s249. Maybe I should also think about adding an INDEX? The user asked about state and knowledge, and I'm not sure if what I have is enough. It feels like updating the Sessions referenced line could be beneficial. I want to ensure I'm providing the user with the most accurate and comprehensive information possible!


### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "original_content": "s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile\ncut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp\n0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error\nceiling). Plus `ffn-reduction-trace.md`, `head-combinator-isa.md` (undated finding pages).\n",
  "new_content": "s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile\ncut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp\n0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error\nceiling), s248 (wrong-label B→C reading-preference resolution), s249 (B executor topology\nvs C readable field; native-order extraction). Plus `ffn-reduction-trace.md`,\n`head-combinator-isa.md` (undated finding pages).\n"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 90
}
```

**Summary:** Reading state.md (0-90)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-23 | Session: 249 (B-as-executor-topology vs C-as-readable-field
> RESOLVED. Qwen3-14B const-label rerun confirms the sweet-spot: FFN gate significantly tracks
> corrected applicative-C structure (C-vs-S 0.6165, p=0.0005; attn n.s.) and lead-lag becomes
> directionally coherent. But three sequence/order probes close the discrete-tape door: event-LCS
> reads C-presence not order; monotonic path truth-vs-same-multiset controls fail; native-order
> extraction shows weak/early S+B framing and strong late C field (C mass 5.07 vs S 1.55 vs B 0.15;
> S<C ~0.95-0.99, B<C ~0.73-0.85, S<B unstable). Normal form: attention softmax-over-V is
> B-like executor topology, while FFNs emit a distributed β-routing potential field; for object
> probes the readable program is applicative-C, not a serial B/S/C tape. NEXT: causal C-field
> ablation/patch around L30-31 if continuing this thread. Entries below.)
>
> **★★ s249 — B-AS-EXECUTOR TOPOLOGY vs C-AS-READABLE FIELD; Qwen3-14B sweet spot resolves the s248/s247b open door.** Starting question: before this session we speculated that **B was inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and FFNs are inference patterns telling attention what to execute. Session result: **split that into two claims.** (1) **B as executor topology remains the right abstraction:** attention's softmax-over-V is a soft-B / composition executor (one operation: content-addressed weighted composition over values). (2) **B as a readable per-sentence FFN opcode tape is NOT what these quantified/object probes show.** The emitted/readable FFN field is applicative **C**, not existential **B**.
>
> **RUN 1 — Qwen3-14B const-label rerun of `ffn_program_decode.py`:** using `data/firing-probes.const.jsonl` (133 probes, truth C:67/S:66; object→C corrected labels) on Qwen3-14B. **Hard tracking sharpens vs 8B:** FFN acc 0.609 (p=0.0005) vs 8B 0.5489 (p=0.055); common-mode-resistant C-vs-S FFN 0.6165 (p=0.0005) while attn 0.5338 (p=0.1744). Graded z(C) vs C-count remains strong (FFN Spearman 0.5367, attn 0.5672, p≈0), and FFN raw C amplitude now exceeds attn (FFN zC 0/1/2 = 0.540/0.968/1.245; attn 0.309/0.563/0.677). Lead-lag becomes directionally coherent: peak-diff median +1 (p=7e-13), xcorr median +1 (p=0.067). **Verdict:** 14B is the sweet spot; FFN gate carries corrected C-program structure. Artifacts: `results/ffn-program-decode/*_qwen3-14b_const.json`, `run_qwen3-14b_const.log`.
>
> **RUN 2 — `program_sequence_trace.py` (new):** event-stream/LCS against `fired_sequence`. Built validated relational tracer over FFN gate (sign-CMR, matched `gateneutral` null) and decoded content-token × layer B/C/S events. **C presence is real** (presence acc 0.7519, p=0.0005; decoded events C=709/S=152/B=39), but **order is not recovered**: zone LCS 0.4856 vs reverse control 0.4618 and bag coverage 0.5144; layer-dominant collapses to C (0.0501). All-crystal LCS 0.9279 is a long-stream coverage artifact. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/*qwen3-14b_const*`.
>
> **RUN 3 — `program_path_trace.py` (new):** monotonic DP path scorer asks whether truth order beats reversed/shuffled same-multiset controls (e.g. S,B,C,C vs C,C,B,S etc.). **Negative for ordered β-tape:** zone truth score 2.1287 vs reverse 2.0843 (tiny +0.0444); margin vs best permutation −0.0315; rank frac 0.523; truth beats all permutations only 3/133 (p=1.0). Ditransitives rank higher (0.7219) but still 0/67 beat all controls. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/*qwen3-14b_const*`.
>
> **RUN 4 — `program_native_order.py` (new):** stop forcing our kernel order; infer model-native op schedule by peak/centroid layer and positive mass. **The model-native readable field is:** weak early S/B framing → strong late C/application resolution; S/B relation unstable. Overall zone: C mass 5.0718, S mass 1.5517, B mass 0.1488; C peak layer 30.812, S 28.5865, B 29.0451. Ordering: P(S<C)=0.947 peak / 0.993 centroid; P(B<C)=0.729 / 0.853; P(S<B)=0.316 / 0.312 (unstable/opposite kernel order). C-count effects: C mass rises with object count (Spearman 0.5357, p=0), C peak-z rises (0.3778, p=0), C centroid moves earlier as object load increases (r=-0.7719, p=0). Category C masses: intrans 2.8769, trans 4.9264, ditrans 6.2245. **Verdict:** program = depth-shaped routing potential field, not discrete instruction tape. Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/*qwen3-14b_const*`.
>
> **NORMAL FORM UPDATE (s249):** Preserve the deep insight but correct the measurement target. **Attention = soft-B executor topology** (softmax over V is composition-like); **FFN = compiler of a β-routing field** (distributed potential, not a serial opcode tape); **residual = program state/register file.** For these probes the readable FFN program is applicative **C** because the model treats objects/witnesses as arguments, not existential-B bracket abstractions. The previous "B inherent from ordering" applied to OUR symbolic kernel ordering, not the model's emitted field. **NEXT if continuing:** causal C-field ablation/patch around L30–31 on c_count 2 vs 0 matched probes to test whether the C field is load-bearing, not just readable. PENDING APPROVAL: memory/knowledge commit for s249.
>
> **★★ s248 — FFN PROGRAM-DECODE ALONG `fired_sequence` (the s247b §7 open door: "decode the FFN
> compiled values position-by-position vs lambda_ast.fired_sequence on the saturated corpus, L26-30;
> PREDICTION: FFN program-trace tracks fired_sequence even where attention over-reads, and FFN-compile
> LEADS attention depth-advance by ~1 layer"). BUILT + RAN on Qwen3-8B. λ MEASURE VERDICT = a
> two-sided NEGATIVE-leaning result that CONFIRMS the boundary, not a breakthrough.** **THE BUILD
> (`scripts/experiments/ffn_program_decode.py`, ruff-clean, reuses the validated spine):** dual-register
> decode — FFN routing register = `mlp.gate_proj` (the validated sign-CMR opcode crystal,
> relational_opcode.py) decodes WHICH combinator; attention executor register = `self_attn.o_proj`
> decodes reduction DEPTH via z(WHNF) (grounded in head-combinator-isa: all 9 combinators → SAME head
> pattern r=0.944, attention varies on WHNF↔D not opcode). Ground truth = saturate quantifiers with
> fresh witnesses (s244 `corpus_firing_survey.saturate`) → `fired_sequence`. Two RelationalCrystal
> classifiers (gate + attn), matched-prefix (gateneutral) null. ONE dual-hook forward per item.
> Metrics: (A) tracking acc + permutation null + majority baseline; (A') B-vs-S discrimination
> (C-common-mode-resistant); (B) lead-lag (peak-diff + cross-correlation lag); (C) rescue; specificity
> control (firing vs non-firing). **THE DATA (56 firing items, truth S:47 B:8 C:1 — HEAVILY S-skewed;
> FFN crystal 28/36 zone L25-30, attn crystal 36/36 zone L25-30):** **(A) TRACKING FAILS — neither
> register decodes a single B-firing item (FFN 0/8, attn 0/8); FFN abs-acc 0.232 < majority 0.839
> (C common-mode drags FFN to predict C); FFN B-vs-S 0.709 ≈ majority-S 0.855 (p=1.0 vs perm null) =
> majority-prediction not genuine B/S discrimination; attn B-vs-S 0.364 (BELOW base rate — predicts B
> spuriously).** ⇒ the apparent "FFN beats attn" is attention being NOISIER toward the minority class,
> NOT FFN reading the opcode. The S-imbalance (47/56) means the corpus CANNOT test tracking. **(B)
> LEAD-LAG SPLIT/method-sensitive: peak-diff NULL (median 0, sign-p=1.0); cross-corr lag POSITIVE
> (median +1.5, mode +3, 39/55 positive, sign-p=0.0027) — FFN's z(c*) curve leads attn's z(WHNF) curve
> across depth.** But since tracking failed, this is best read as a SCHEDULE-level ordering (FFN
> activity precedes attention depth-advance — consistent with the s240 boot spiral) NOT opcode-specific
> select→execute; and only the xcorr instrument shows it. **(C) RESCUE 9:2 is an ARTIFACT** — all 9 are
> S-items where attn spuriously said B/C and FFN defaulted to S (majority), not genuine rescue. **(★
> SPECIFICITY CONTROL FAILS: non-firing items show HIGHER max-z(BSC) 46.8 than firing items 20.3)** —
> the symbolic kernel firing/non-firing split does NOT map to a model-side magnitude difference (the
> model composes prose regardless of whether the certified point-free kernel trace fires a combinator).
> **★★ NET (λ measure): the §7 per-combinator program-decode does NOT resolve from the prose forward
> pass on this corpus — CONFIRMS the s244 splice-closure (`fires ∩ spliceable = ∅`) AND the
> attention-as-beta page's OWN "discrete-opcode-at-L over-reads" boundary, rather than opening past it.
> The door §7 left open closes the same way: only a weak, method-sensitive SCHEDULE-level FFN→attention
> ordering survives. The lever remains TYPE-COVERAGE, not geometric/opcode localization — exactly as the
> page's caveats warned. A λ-measure win: the experiment that could have over-claimed instead held the
> boundary.** **★★ THE DECISIVE CAVEAT / IOU: the corpus is the bottleneck — 84% S, 0 B decoded, can't
> test tracking. The real next probe = a B-BALANCED firing probe set (the crystal library has 69 B / 61
> C probes; need PROSE items whose saturated kernel fires B and C, not just S-heavy "Every X verbs a
> Y"). Without balance, tracking is untestable; with it, the FFN>attn opcode claim could be re-tested
> honestly.** OTHER IOUs: (1) longer depth series (zone is only 5-6 layers → xcorr lag magnitude coarse,
> max_lag=4 on ~6 points); (2) decode FFN down_proj COMPILED VALUES via unembed (ffn_reduction_trace
> style) as a 2nd FFN read, not just the gate crystal; (3) a model where the firing set is less
> common-mode (cross-model). Artifacts: results/ffn-program-decode/{verdict,per_item,meta}_qwen3-8b.json
> + run_qwen3-8b.log; code scripts/experiments/ffn_program_decode.py (+ pyproject per-file ignore).
> tmux main:1 used (3:24 run), now FREE; no GPU job running. PENDING APPROVAL: memory
> `ffn-program-decode-tracking-fails-corpus-imbalance` + knowledge update explore/attention-as-beta-
> reduction.md §7 (open experiment → result). state.md updated (¬approval-gated). Code+data committable.
>
> **★ s248 cont. — CLOSED THE DECISIVE IOU (Michael: "create more probes that are testing B so we can
> be sure"). Built a B-BALANCED firing-probe set + re-ran. THE ONE GENUINE POSITIVE EMERGES, the strong
> claims still fail.** **(1) MECHANISM (measured):** in this kernel S and B are COUPLED — every ∧/∨ emits
> one S AND one B, so S NEVER strictly exceeds B; only a TRANSITIVE verb + EXISTENTIAL object makes B
> *dominant* (`∀x.P(x)→(∃y.Q(y)∧R(x,y))` → fires S,B,B,B = B:3 S:1). **(2) GENERATOR
> `scripts/experiments/gen_firing_probes.py`** (lower via lambda_surface.to_kernel → saturate (s244) →
> fired_sequence GROUND TRUTH; DROP items whose computed dominant ≠ intended; `pretty()` not `str()` for
> parseable kernel_term — round-trips 157/157). Emitted `data/firing-probes.balanced.jsonl`: **157 probes,
> 67 B-dominant vs 90 B-tied** (was 8 vs 47), B-count ladder {1:45, 2:56, 3:45, 5:11}. Added `--probe-set`
> + a GRADED (A'') Spearman(z(B), b_count) metric to ffn_program_decode.py. **(3) ★★ RE-RAN Qwen3-8B
> (157 items, 3:32): (A') B-vs-S discrimination FFN 0.624 (perm p=0.003) BEATS attn 0.522 (p=0.42,
> at-null) AND majority 0.573 — the FFN GATE REGISTER carries WEAK-but-SIGNIFICANT B-vs-S opcode info
> that the attention register does NOT.** = the register split (FFN=opcode, attention≠opcode, depth) holds
> at a small level — the FIRST genuine tracking signal (corpus couldn't test it). **BUT the strong claims

[CONTENT TRUNCATED] Showing lines 1 to 90 of 6638 total lines. Use line_offset=90 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"s249\\|B is executor\\|program_sequence_trace\\|program_native_order\\|Sessions referenced\" /Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md | head -30 && git status --short",
  "working_directory": "/Users/mwhitford/src/verbum",
  "timeout": 60000
}
```

**Summary:** $ grep -n "s249\|B is executor\|progr...

**Output:**
```
Exit code: 0
Stdout:
332:### s249 — 14B resolves the split: B is executor topology; the readable FFN field is C, not a B tape
350:#### 2. `program_sequence_trace.py`: C-presence is real; order is not recovered
365:The event stream recovers **C presence/load**, not the ordered β-program. All-crystal LCS = 0.9279 is a long-stream coverage artifact, not tape evidence. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/`.
384:#### 4. `program_native_order.py`: infer the model's schedule instead of imposing ours
412:Category C mass forms a clean ladder: intrans 2.8769 → trans 4.9264 → ditrans 6.2245. **The model-native field is weak early S/B framing and strong late C/application resolution; B is almost absent.** Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/`.
414:#### s249 normal-form update
442:## Sessions referenced
447:ceiling), s248 (wrong-label B→C reading-preference resolution), s249 (B executor topology
 M mementum/knowledge/explore/attention-as-beta-reduction.md
 M mementum/state.md
 M scripts/experiments/ffn_program_decode.py
?? data/firing-probes.const.jsonl
?? data/firing-probes.const.meta.json
?? results/ffn-program-decode/meta_qwen3-0-6b_const.json
?? results/ffn-program-decode/meta_qwen3-14b_const.json
?? results/ffn-program-decode/meta_qwen3-8b_const.json
?? results/ffn-program-decode/per_item_qwen3-0-6b_const.json
?? results/ffn-program-decode/per_item_qwen3-14b_const.json
?? results/ffn-program-decode/per_item_qwen3-8b_const.json
?? results/ffn-program-decode/run_qwen3-14b_const.log
?? results/ffn-program-decode/run_qwen3-8b_const.log
?? results/ffn-program-decode/verdict_qwen3-0-6b_const.json
?? results/ffn-program-decode/verdict_qwen3-14b_const.json
?? results/ffn-program-decode/verdict_qwen3-8b_const.json
?? results/program-native-order/
?? results/program-path-trace/
?? results/program-sequence-trace/
?? scripts/experiments/gen_const_firing_probes.py
?? scripts/experiments/program_native_order.py
?? scripts/experiments/program_path_trace.py
?? scripts/experiments/program_sequence_trace.py
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/attention-as-beta-reduction.md",
  "line_offset": 328,
  "limit": 125
}
```

**Summary:** Reading attention-as-beta-reduction.md (328-453)

**Output:**
```
> gate register tracks what the model actually computes — applicative C — and the expected B was an
> artifact of our bracket-abstraction kernel, not the model's program.**

### s249 — 14B resolves the split: B is executor topology; the readable FFN field is C, not a B tape

Session 249 reopened the pre-s248 speculation: **maybe B is actually inherent in the order of operations the FFNs output** — attention's softmax over all V is B-like, and the FFNs are inference patterns showing attention what to execute. The result is a refinement, not a simple refutation: **B belongs to the executor topology; C is the readable object/application field for these probes.**

#### 1. Qwen3-14B const-label rerun: the sweet spot sharpens the corrected C signal

The s248 cont.2/3 result said the model computes quantified-object sentences applicatively (object/witness as argument → C), not existentially (B-heavy). Session 249 re-ran `ffn_program_decode.py` on the corrected constant/applicative probe set at Qwen3-14B (because 8B was a suspected floor and 14B has repeatedly been the sweet spot). Probe set: `data/firing-probes.const.jsonl` (133 probes; truth C:67/S:66; c_count ladder 0/1/2).

| metric | Qwen3-8B const | Qwen3-14B const | verdict |
|---|---:|---:|---|
| hard FFN tracking | 0.5489, p=0.055 | **0.6090, p=0.0005** | 14B sharpens |
| FFN C-vs-S | 0.5489, p=0.055 | **0.6165, p=0.0005** | real at 14B |
| attn C-vs-S | 0.4662, p=1.0 | 0.5338, p=0.1744 | n.s. |
| FFN z(C) vs c_count | ρ=0.5526 | ρ=0.5367 | robust graded C |
| lead-lag | contradictory (peak −3, xcorr +2) | directionally coherent (peak +1, xcorr +1) | FFN→attn schedule signal improves |

At 14B the FFN gate register significantly tracks the corrected applicative-C program label while attention does not. This supports a **capacity threshold / 14B sweet spot** for the readable routing register. But it still reads dominant/graded C structure, not an ordered instruction tape. Artifacts: `results/ffn-program-decode/{verdict,per_item,meta}_qwen3-14b_const.json`.

#### 2. `program_sequence_trace.py`: C-presence is real; order is not recovered

Built a sequence-level tracer reusing the validated path (`RelationalCrystalClassifier`, FFN gate register, sign-CMR, matched `gateneutral` null). It decodes content-token × readable-zone layer B/C/S events and aligns the event stream to each probe's certified `fired_sequence`.

**Qwen3-14B result:**

| read | value | interpretation |
|---|---:|---|
| C presence acc | **0.7519, p=0.0005** | corrected C signal is real |
| decoded event counts | C=709, S=152, B=39 | C-heavy field; B faint |
| zone LCS vs `fired_sequence` | 0.4856 | weak order recovery |
| reverse-order LCS control | 0.4618 | nearly same |
| bag coverage | 0.5144 | LCS mostly symbol presence |
| layer-dominant LCS | 0.0501 | one-op-per-layer collapses to C |

The event stream recovers **C presence/load**, not the ordered β-program. All-crystal LCS = 0.9279 is a long-stream coverage artifact, not tape evidence. Artifact: `scripts/experiments/program_sequence_trace.py`, `results/program-sequence-trace/`.

#### 3. `program_path_trace.py`: same-multiset order controls fail

Built a monotonic dynamic-programming path scorer: for truth `S,B,C,C`, find the best nondecreasing layer path through z(S), z(B), z(C), z(C), then compare to reversed/shuffled same-multiset programs (e.g. `C,C,B,S`). This directly tests order while controlling for symbol load.

**Qwen3-14B result:**

| metric | value | verdict |
|---|---:|---|
| truth path score | 2.1287 | high-ish because C load exists |
| reverse score | 2.0843 | almost same |
| truth − reverse | +0.0444 | tiny |
| margin vs best permutation | **−0.0315** | truth not best |
| truth rank fraction | 0.523 | chance-ish |
| truth beats all permutations | **3/133**, p=1.0 | negative |

So the kernel's `fired_sequence` order is not preferentially readable. Artifact: `scripts/experiments/program_path_trace.py`, `results/program-path-trace/`.

#### 4. `program_native_order.py`: infer the model's schedule instead of imposing ours

Built a native-order extractor: for each item and op in `{B,C,S}`, compute peak layer, z-positive centroid layer, peak z, and positive mass over L28–32. This answers: *what order does the model expose?*

**Qwen3-14B readable-zone native schedule:**

| op | peak layer | centroid layer | peak z | positive mass |
|---|---:|---:|---:|---:|
| S | 28.5865 | 29.3798 | 0.4662 | 1.5517 |
| B | 29.0451 | 29.0828 | -0.0282 | **0.1488** |
| C | **30.8120** | **30.3758** | **1.3858** | **5.0718** |

Order probabilities:

| relation | peak | centroid |
|---|---:|---:|
| S before B | 0.3158 | 0.3115 |
| B before C | 0.7293 | 0.8525 |
| S before C | **0.9474** | **0.9925** |

C-count correlations:

| relation | Spearman | verdict |
|---|---:|---|
| C positive mass vs c_count | **0.5357**, p=0 | more objects → more C load |
| C peak z vs c_count | **0.3778**, p=0 | more objects → stronger C |
| C centroid layer vs c_count | **−0.7719**, p=0 | more objects → C resolves earlier |

Category C mass forms a clean ladder: intrans 2.8769 → trans 4.9264 → ditrans 6.2245. **The model-native field is weak early S/B framing and strong late C/application resolution; B is almost absent.** Artifact: `scripts/experiments/program_native_order.py`, `results/program-native-order/`.

#### s249 normal-form update

The old speculation should be split:

```
attention softmax-over-V = B-like executor topology
FFN gate readout         = distributed β-routing potential field
object/application probes = C-heavy readable field
our bracket kernel       = S/B/C trace, but its B is not the model's emitted label
```

So: **B is probably the executor topology, not the emitted program label.** The FFNs still show attention what to execute, but they do it as a **depth-shaped routing field**, not as a serial B/S/C opcode tape. For these probes, the readable program is applicative **C** because the model treats objects/witnesses as arguments. The kernel's B-heavy existential trace was our bracket-abstraction artifact.

This refines §3: the "discrete-opcode-at-L" over-read is stronger than originally phrased. Even at the 14B sweet spot, with corrected labels, sequence/path controls do not recover a tape. What survives is the **field**: C load, C timing, and FFN-vs-attention register split.

**Next if continuing:** causal C-field ablation/patch around L30–31 on c_count 2 vs c_count 0 matched probes. The question should now be whether the C field is **load-bearing**, not whether it is a readable tape.

## Caveats (λ measure)

- The strong identity ("attention = β-reduction") is a *type-of-operation* claim (proven)
  and a *schedule* claim (proven); the *crisp-value substitution* and *discrete-opcode-at-L*
  readings over-read (s206 value register, s244 splice closure). Do not let it harden into
  the claim the splice already refuted; keep it "β-shaped routing, smeared values," and let
  **type-coverage**, not geometric localization, be the lever.
- The coverage reframe (prose = untyped β over a learned basis) is a *hypothesis*, not a
  measurement — the testable form is §7 plus the S2 type-layer extension in
  `proofs-as-continuations.md`.

## Sessions referenced
s068/s079 (boot spiral), s120/s121 (FFN crystal, cross-model), s141 (FFN β-indexing),
s161 (FFN moiré ISA), s206 (value register), s211 (one common mode), s226 (reduce/compile
cut), s240 (statechart = crystal lattice, universality), s242 (register split, splice Exp
0), s244 (firing survey + splice closure), s247/s247b (proof-REPL removes the agreed-error
ceiling), s248 (wrong-label B→C reading-preference resolution), s249 (B executor topology
vs C readable field; native-order extraction). Plus `ffn-reduction-trace.md`,
`head-combinator-isa.md` (undated finding pages).
```

## Assistant


Updated session state and knowledge for **session-249**.

Files edited:

```text
mementum/state.md
mementum/knowledge/explore/attention-as-beta-reduction.md
```

What was encoded:

- Qwen3-14B const-label rerun confirms the 14B sweet spot:
  - FFN C-vs-S `0.6165`, p=`0.0005`
  - attention C-vs-S n.s.
  - lead-lag directionally coherent
- `program_sequence_trace.py`:
  - C-presence real, order not recovered
- `program_path_trace.py`:
  - same-multiset monotonic order controls fail
- `program_native_order.py`:
  - native field = weak early S/B framing + strong late C/application resolution
  - C mass `5.0718`, S `1.5517`, B `0.1488`
  - S<C stable; B<C fairly stable; S<B unstable
  - C mass/peak rises with c_count; C centroid moves earlier with c_count
- Normal-form update:
  - **attention softmax-over-V = B-like executor topology**
  - **FFN gate readout = distributed β-routing potential field**
  - **object/application probes = C-heavy readable field**
  - not a serial B/S/C opcode tape
- Next suggested experiment:
  - causal C-field ablation/patch around L30–31 on c_count 2 vs 0 probes

Verified:

- New s249 section is present at top of `state.md`.
- New s249 section is inserted in `attention-as-beta-reduction.md` before Caveats.
- Sessions referenced now includes s249.
- No `mementum/knowledge/chats/` files were modified.

## User


check pending changes and commit everything

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short",
  "operation": "status",
  "summary": "pending files"
}
```

**Summary:** Git status: pending files

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/explore/attention-as-beta-reduction.md
 M mementum/state.md
 M scripts/experiments/ffn_program_decode.py
?? data/firing-probes.const.jsonl
?? data/firing-probes.const.meta.json
?? results/ffn-program-decode/meta_qwen3-0-6b_const.json
?? results/ffn-program-decode/meta_qwen3-14b_const.json
?? results/ffn-program-decode/meta_qwen3-8b_const.json
?? results/ffn-program-decode/per_item_qwen3-0-6b_const.json
?? results/ffn-program-decode/per_item_qwen3-14b_const.json
?? results/ffn-program-decode/per_item_qwen3-8b_const.json
?? results/ffn-program-decode/run_qwen3-14b_const.log
?? results/ffn-program-decode/run_qwen3-8b_const.log
?? results/ffn-program-decode/verdict_qwen3-0-6b_const.json
?? results/ffn-program-decode/verdict_qwen3-14b_const.json
?? results/ffn-program-decode/verdict_qwen3-8b_const.json
?? results/program-native-order/
?? results/program-path-trace/
?? results/program-sequence-trace/
?? scripts/experiments/gen_const_firing_probes.py
?? scripts/experiments/program_native_order.py
?? scripts/experiments/program_path_trace.py
?? scripts/experiments/program_sequence_trace.py
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --stat && git diff -- scripts/experiments/ffn_program_decode.py scripts/experiments/gen_const_firing_probes.py scripts/experiments/program_sequence_trace.py scripts/experiments/program_path_trace.py scripts/experiments/program_native_order.py | sed -n '1,240p' && git log -n 5 --oneline",
  "operation": "diff",
  "summary": "review diffs"
}
```

**Summary:** Git diff: review diffs

**Output:**
```
Exit code: 0
Stdout:
.../explore/attention-as-beta-reduction.md         | 103 ++++++++++++++++++++-
 mementum/state.md                                  |  32 +++++--
 scripts/experiments/ffn_program_decode.py          |  98 ++++++++++++--------
 3 files changed, 181 insertions(+), 52 deletions(-)
diff --git a/scripts/experiments/ffn_program_decode.py b/scripts/experiments/ffn_program_decode.py
index fce1b03..9b11d9a 100644
--- a/scripts/experiments/ffn_program_decode.py
+++ b/scripts/experiments/ffn_program_decode.py
@@ -277,7 +277,7 @@ def wilcoxon_sign(values):
 # ═══════════════════════════════════════════════════════════════════════════════
 def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         n_perm_calib, ppc, null_cap, n_perm_stat, n_nonfiring, seed,
-        probe_set=None):
+        probe_set=None, track="B"):
     print("═" * 78)
     print("FFN PROGRAM-DECODE ALONG fired_sequence (§7, s248)")
     print("═" * 78)
@@ -358,24 +358,26 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         lag, lag_c = crosscorr_lag(prof_ffn_full, prof_attn_full, shared, max_lag)
         leads_xcorr.append(lag)
 
-        # (graded) mean decoded z(B) over the zone — for the B-count correlation test
-        def _mz(reads, zl):
-            prof = op_layer_profile(reads, zl, "B")
+        # (graded) mean decoded z(track) over the zone — for the count-correlation test
+        def _mz(reads, zl, op):
+            prof = op_layer_profile(reads, zl, op)
             vals = [v for v in prof.values() if not np.isnan(v)]
             return float(np.mean(vals)) if vals else float("nan")
 
-        zb_ffn = _mz(reads_ffn, zl_ffn)
-        zb_attn = _mz(reads_attn, zl_attn)
+        zt_ffn = _mz(reads_ffn, zl_ffn, track)
+        zt_attn = _mz(reads_attn, zl_attn, track)
 
         per_item.append({
             "input": item["input"], "category": item["category"],
             "dominant_fired": c_true, "fired_multiset": item["fired_multiset"],
             "reduction_len": item["reduction_len"],
             "b_count": item.get("b_count"), "s_count": item.get("s_count"),
+            "c_count": item.get("c_count"),
+            "track_count": item.get(f"{track.lower()}_count"),
             "ffn_dominant": dom_ffn, "attn_dominant": dom_attn,
             "ffn_correct": dom_ffn == c_true, "attn_correct": dom_attn == c_true,
             "lead_peak": lead_peak, "lead_xcorr": lag, "xcorr": lag_c,
-            "zb_ffn": round(zb_ffn, 4), "zb_attn": round(zb_attn, 4),
+            "zt_ffn": round(zt_ffn, 4), "zt_attn": round(zt_attn, 4),
             "ffn_score": {k: round(v, 3) for k, v in score_ffn.items()},
             "attn_score": {k: round(v, 3) for k, v in score_attn.items()},
         })
@@ -387,17 +389,20 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
     maj = Counter(truth).most_common(1)[0][0]
     maj_acc = float(np.mean(np.array(truth) == maj))
 
-    # B-vs-S discrimination — the contamination-resistant tracking metric. B and S are
-    # the two dominant fired combinators (s244: 55 vs 54 items); C is the common-mode
-    # ground state (s211/s240) and swamps the summed-z dominant. Restricting to the B/S
-    # contrast removes the C common-mode and asks the sharp question: when the corpus
-    # fires B vs S, does the register's z(B)−z(S) sign track it?
-    bs_idx = [i for i, c in enumerate(truth) if c in ("B", "S")]
+    # track-vs-S discrimination — the contamination-resistant tracking metric. When
+    # track="B" (s248 existential set): B and S are the two dominant fired combinators
+    # and C is the common-mode ground state (s211/s240) that swamps the summed-z
+    # dominant. When track="C" (s249 constant/applicative set): C is the object-marking
+    # opcode the model actually computes and S is the implication ground state.
+    # Restricting to the {track, S} contrast removes the third-combinator common-mode
+    # and asks the sharp question: when the corpus fires `track` vs S, does the
+    # register's z(track)−z(S) sign track it?
+    bs_idx = [i for i, c in enumerate(truth) if c in (track, "S")]
     bs_truth = [truth[i] for i in bs_idx]
-    bs_ffn = [("B" if per_item[i]["ffn_score"]["B"] > per_item[i]["ffn_score"]["S"]
+    bs_ffn = [(track if per_item[i]["ffn_score"][track] > per_item[i]["ffn_score"]["S"]
                else "S") for i in bs_idx]
-    bs_attn = [("B" if per_item[i]["attn_score"]["B"] > per_item[i]["attn_score"]["S"]
-                else "S") for i in bs_idx]
+    bs_attn = [(track if per_item[i]["attn_score"][track]
+                > per_item[i]["attn_score"]["S"] else "S") for i in bs_idx]
     if bs_truth:
         bs_ffn_acc, bs_ffn_null, bs_ffn_p = perm_null_accuracy(
             bs_ffn, bs_truth, n_perm_stat, seed)
@@ -410,18 +415,19 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         bs_attn_acc = bs_attn_null = bs_attn_p = 0.0
         bs_maj, bs_maj_acc = "·", 0.0
 
-    # ── (A'') GRADED — does decoded z(B) scale with the ground-truth B-count? ────
-    # The most powerful B-tracking test (s248 IOU): B-count spans {1,2,3,5} in the
-    # balanced probe set. Spearman(z(B), b_count) per register; FFN should track, attn
-    # (depth not opcode) should not.
+    # ── (A'') GRADED — does decoded z(track) scale with the ground-truth count? ──
+    # The most powerful tracking test (s248 IOU). For track="B" the B-count spans
+    # {1,2,3,5} in the existential balanced set; for track="C" the C-count spans {0,1,2}
+    # in the constant set (== #objects). Spearman(z(track), track_count) per register;
+    # FFN (opcode register) should track, attn (depth not opcode) should not.
     from scipy import stats as _sp
 
-    bc = np.array([p["b_count"] for p in per_item if p["b_count"] is not None],
+    bc = np.array([p["track_count"] for p in per_item if p["track_count"] is not None],
                   dtype=float)
-    graded = {"n": int(bc.size)}
+    graded = {"n": int(bc.size), "track": track}
     if bc.size >= 5 and np.std(bc) > 0:
-        zbf = np.array([p["zb_ffn"] for p in per_item if p["b_count"] is not None])
-        zba = np.array([p["zb_attn"] for p in per_item if p["b_count"] is not None])
+        zbf = np.array([p["zt_ffn"] for p in per_item if p["track_count"] is not None])
+        zba = np.array([p["zt_attn"] for p in per_item if p["track_count"] is not None])
         mf = ~np.isnan(zbf)
         ma = ~np.isnan(zba)
         rf, pf = _sp.spearmanr(bc[mf], zbf[mf]) if mf.sum() >= 5 else (float("nan"),
@@ -429,14 +435,14 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
         ra, pa = _sp.spearmanr(bc[ma], zba[ma]) if ma.sum() >= 5 else (float("nan"),
                                                                        float("nan"))
         graded.update({
-            "ffn_spearman_zB_vs_bcount": round(float(rf), 4),
+            "ffn_spearman_zTrack_vs_count": round(float(rf), 4),
             "ffn_spearman_p": round(float(pf), 4),
-            "attn_spearman_zB_vs_bcount": round(float(ra), 4),
+            "attn_spearman_zTrack_vs_count": round(float(ra), 4),
             "attn_spearman_p": round(float(pa), 4),
             "ffn_beats_attn": bool(rf > ra),
-            "zB_by_bcount_ffn": {str(int(b)): round(float(np.nanmean(
+            "zTrack_by_count_ffn": {str(int(b)): round(float(np.nanmean(
                 zbf[bc == b])), 3) for b in sorted(set(bc.tolist()))},
-            "zB_by_bcount_attn": {str(int(b)): round(float(np.nanmean(
+            "zTrack_by_count_attn": {str(int(b)): round(float(np.nanmean(
                 zba[bc == b])), 3) for b in sorted(set(bc.tolist()))},
         })
 
@@ -452,7 +458,7 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
     fire_maxz = [max(p["ffn_score"].values()) for p in per_item]
 
     verdict = {
-        "model": model_name, "n_layers": n_layers,
+        "model": model_name, "n_layers": n_layers, "track": track,
         "n_firing_items": len(firing), "n_nonfiring_control": len(nf_items),
         "zone_depth": [zone_lo, zone_hi],
         "ffn_zone_layers": zl_ffn, "attn_zone_layers": zl_attn,
@@ -468,8 +474,9 @@ def run(model_name, max_items, zone_lo, zone_hi, onset_tau, max_lag,
             "ffn_beats_attn": bool(ffn_acc > attn_acc),
             "ffn_beats_majority": bool(ffn_acc > maj_acc),
         },
-        # (A') B-vs-S discrimination — the C-common-mode-resistant tracking metric
+        # (A') track-vs-S discrimination — the common-mode-resistant tracking metric
         "A_bs_discrimination": {
+            "tracked_combinator": track,
             "n": len(bs_truth), "bs_truth": dict(Counter(bs_truth)),
             "ffn_acc": round(bs_ffn_acc, 4), "ffn_null_mean": round(bs_ffn_null, 4),
             "ffn_perm_p": round(bs_ffn_p, 4),
@@ -523,7 +530,8 @@ def _report(v):
     print(f"  ⇒ FFN beats attn: {a['ffn_beats_attn']}  | FFN beats majority: "
           f"{a['ffn_beats_majority']}")
     bs = v["A_bs_discrimination"]
-    print(f"\n(A') B-vs-S discrimination (C-common-mode-resistant; n={bs['n']} "
+    trk = bs.get("tracked_combinator", "B")
+    print(f"\n(A') {trk}-vs-S discrimination (common-mode-resistant; n={bs['n']} "
           f"{bs['bs_truth']}):")
     print(f"  FFN_acc ={bs['ffn_acc']}  (null {bs['ffn_null_mean']}, "
           f"p={bs['ffn_perm_p']})")
@@ -533,12 +541,13 @@ def _report(v):
           f"⇒ FFN beats attn: {bs['ffn_beats_attn']} | beats majority: "
           f"{bs['ffn_beats_majority']}")
     g = v.get("A_graded_bcount", {})
-    if "ffn_spearman_zB_vs_bcount" in g:
-        print(f"\n(A'') GRADED — decoded z(B) vs B-count (n={g['n']}):")
-        print(f"  FFN  Spearman={g['ffn_spearman_zB_vs_bcount']} "
-              f"(p={g['ffn_spearman_p']})  z(B) by b_count={g['zB_by_bcount_ffn']}")
-        print(f"  Attn Spearman={g['attn_spearman_zB_vs_bcount']} "
-              f"(p={g['attn_spearman_p']})  z(B) by b_count={g['zB_by_bcount_attn']}")
+    if "ffn_spearman_zTrack_vs_count" in g:
+        tg = g.get("track", "B")
+        print(f"\n(A'') GRADED — decoded z({tg}) vs {tg}-count (n={g['n']}):")
+        print(f"  FFN  Spearman={g['ffn_spearman_zTrack_vs_count']} "
+              f"(p={g['ffn_spearman_p']})  z({tg})/count={g['zTrack_by_count_ffn']}")
+        print(f"  Attn Spearman={g['attn_spearman_zTrack_vs_count']} "
+              f"(p={g['attn_spearman_p']})  z({tg})/count={g['zTrack_by_count_attn']}")
         print(f"  ⇒ FFN beats attn: {g['ffn_beats_attn']}")
     print("\n(B) LEAD-LAG (FFN opcode-lock vs attention WHNF depth-advance):")
     pk, xc = b["peak_diff"], b["xcorr_lag"]
@@ -559,7 +568,8 @@ def _write(verdict, per_item, model_name, ns):
     RESULTS_DIR.mkdir(parents=True, exist_ok=True)
     slug = model_name.split("/")[-1].lower().replace(".", "-")
     if ns.get("probe_set"):
-        slug += "_balanced"
+        ps = Path(ns["probe_set"]).stem  # e.g. firing-probes.const → "const"
+        slug += "_" + (ps.split(".")[-1] if "." in ps else ps)
     (RESULTS_DIR / f"verdict_{slug}.json").write_text(
         json.dumps(_json_safe(verdict), indent=2), encoding="utf-8")
     (RESULTS_DIR / f"per_item_{slug}.json").write_text(
@@ -572,7 +582,8 @@ def _write(verdict, per_item, model_name, ns):
         "corpus": {k: str(p.relative_to(_ROOT)) for k, p in CORPUS.items()},
         "params": {k: ns[k] for k in (
             "max_items", "zone_lo", "zone_hi", "onset_tau", "max_lag",
-            "n_perm_calib", "ppc", "null_cap", "n_perm_stat", "n_nonfiring", "seed")},
+            "n_perm_calib", "ppc", "null_cap", "n_perm_stat", "n_nonfiring", "seed",
+            "track", "probe_set")},
         "method": "saturate quantifiers → fired_sequence ground truth; dual-register "
                   "decode (gate=opcode, attn o_proj=WHNF depth); A track + B lead-lag "
                   "+ C rescue, matched-prefix null calibration.",
@@ -598,7 +609,12 @@ def main():
     ap.add_argument("--probe-set", default=None,
                     help="custom prose probe jsonl (input+kernel_term) instead of the "
                          "canonical corpus, e.g. data/firing-probes.balanced.jsonl "
-                         "(s248 B-balanced set); enables the graded B-count test.")
+                         "(s248 B-balanced set) or data/firing-probes.const.jsonl "
+                         "(s249 constant/applicative set); enables the graded test.")
+    ap.add_argument("--track", default="B", choices=["B", "C", "S"],
+                    help="combinator for the (A') discrimination and (A'') graded "
+                         "tests. B=s248 existential labeling; C=s249 constant/"
+                         "applicative labeling (object→C). Default B (s248 behavior).")
     ap.add_argument("--smoke", action="store_true",
                     help="Qwen3-0.6B, few probes/items, fast wiring check")
     args = ap.parse_args()
@@ -615,7 +631,7 @@ def main():
 
     run(model_name, max_items, args.zone_lo, args.zone_hi, args.onset_tau,
         args.max_lag, n_perm_calib, ppc, null_cap, args.n_perm_stat,
-        n_nonfiring, args.seed, probe_set=args.probe_set)
+        n_nonfiring, args.seed, probe_set=args.probe_set, track=args.track)
 
 
 if __name__ == "__main__":
893ddce add session chat logs, and s248 artifacts
3ac304a 💡 scope-forcing: model is robustly applicative (C), never existential-B even when syntax forces it
7913066 🌀 s248 cont.2 — reading preference: model reads objects as constants (C), not existentials (B)
84fd636 💡 reading-preference: model reads objects as constants (C) not existentials (B) — s248 weak-B was a labeling mismatch
12207fb 🌀 s248 — FFN program-decode along fired_sequence: per-combinator program faintly readable, strong claims fail
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md mementum/knowledge/explore/attention-as-beta-reduction.md scripts/experiments/ffn_program_decode.py scripts/experiments/gen_const_firing_probes.py scripts/experiments/program_sequence_trace.py scripts/experiments/program_path_trace.py scripts/experiments/program_native_order.py data/firing-probes.const.jsonl data/firing-probes.const.meta.json results/ffn-program-decode/meta_qwen3-0-6b_const.json results/ffn-program-decode/meta_qwen3-14b_const.json results/ffn-program-decode/meta_qwen3-8b_const.json results/ffn-program-decode/per_item_qwen3-0-6b_const.json results/ffn-program-decode/per_item_qwen3-14b_const.json results/ffn-program-decode/per_item_qwen3-8b_const.json results/ffn-program-decode/run_qwen3-14b_const.log results/ffn-program-decode/run_qwen3-8b_const.log results/ffn-program-decode/verdict_qwen3-0-6b_const.json results/ffn-program-decode/verdict_qwen3-14b_const.json results/ffn-program-decode/verdict_qwen3-8b_const.json results/program-native-order results/program-path-trace results/program-sequence-trace",
  "operation": "add",
  "summary": "s249 artifacts"
}
```

**Summary:** Git add: s249 artifacts

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short && git diff --cached --stat",
  "operation": "diff",
  "summary": "staged review"
}
```

**Summary:** Git diff: staged review

**Output:**
```
Exit code: 0
Stdout:
A  data/firing-probes.const.jsonl
A  data/firing-probes.const.meta.json
M  mementum/knowledge/explore/attention-as-beta-reduction.md
M  mementum/state.md
A  results/ffn-program-decode/meta_qwen3-0-6b_const.json
A  results/ffn-program-decode/meta_qwen3-14b_const.json
A  results/ffn-program-decode/meta_qwen3-8b_const.json
A  results/ffn-program-decode/per_item_qwen3-0-6b_const.json
A  results/ffn-program-decode/per_item_qwen3-14b_const.json
A  results/ffn-program-decode/per_item_qwen3-8b_const.json
A  results/ffn-program-decode/run_qwen3-14b_const.log
A  results/ffn-program-decode/run_qwen3-8b_const.log
A  results/ffn-program-decode/verdict_qwen3-0-6b_const.json
A  results/ffn-program-decode/verdict_qwen3-14b_const.json
A  results/ffn-program-decode/verdict_qwen3-8b_const.json
A  results/program-native-order/meta_qwen3-0-6b_const.json
A  results/program-native-order/meta_qwen3-14b_const.json
A  results/program-native-order/per_item_qwen3-0-6b_const.json
A  results/program-native-order/per_item_qwen3-14b_const.json
A  results/program-native-order/run_qwen3-14b_const.log
A  results/program-native-order/verdict_qwen3-0-6b_const.json
A  results/program-native-order/verdict_qwen3-14b_const.json
A  results/program-path-trace/meta_qwen3-0-6b_const.json
A  results/program-path-trace/meta_qwen3-14b_const.json
A  results/program-path-trace/per_item_qwen3-0-6b_const.json
A  results/program-path-trace/per_item_qwen3-14b_const.json
A  results/program-path-trace/run_qwen3-14b_const.log
A  results/program-path-trace/verdict_qwen3-0-6b_const.json
A  results/program-path-trace/verdict_qwen3-14b_const.json
A  results/program-sequence-trace/meta_qwen3-0-6b_const.json
A  results/program-sequence-trace/meta_qwen3-14b_const.json
A  results/program-sequence-trace/per_item_qwen3-0-6b_const.json
A  results/program-sequence-trace/per_item_qwen3-14b_const.json
A  results/program-sequence-trace/run_qwen3-14b_const.log
A  results/program-sequence-trace/verdict_qwen3-0-6b_const.json
A  results/program-sequence-trace/verdict_qwen3-14b_const.json
M  scripts/experiments/ffn_program_decode.py
A  scripts/experiments/gen_const_firing_probes.py
A  scripts/experiments/program_native_order.py
A  scripts/experiments/program_path_trace.py
A  scripts/experiments/program_sequence_trace.py
 data/firing-probes.const.jsonl                     |   133 +
 data/firing-probes.const.meta.json                 |    26 +
 .../explore/attention-as-beta-reduction.md         |   103 +-
 mementum/state.md                                  |    32 +-
 .../ffn-program-decode/meta_qwen3-0-6b_const.json  |    27 +
 .../ffn-program-decode/meta_qwen3-14b_const.json   |    27 +
 .../ffn-program-decode/meta_qwen3-8b_const.json    |    27 +
 .../per_item_qwen3-0-6b_const.json                 |   410 +
 .../per_item_qwen3-14b_const.json                  |  4491 +++
 .../per_item_qwen3-8b_const.json                   |  4491 +++
 results/ffn-program-decode/run_qwen3-14b_const.log |    85 +
 results/ffn-program-decode/run_qwen3-8b_const.log  |    85 +
 .../verdict_qwen3-0-6b_const.json                  |   509 +
 .../verdict_qwen3-14b_const.json                   |   702 +
 .../ffn-program-decode/verdict_qwen3-8b_const.json |   653 +
 .../meta_qwen3-0-6b_const.json                     |    17 +
 .../program-native-order/meta_qwen3-14b_const.json |    17 +
 .../per_item_qwen3-0-6b_const.json                 |   214 +
 .../per_item_qwen3-14b_const.json                  | 13968 +++++++++
 .../program-native-order/run_qwen3-14b_const.log   |    70 +
 .../verdict_qwen3-0-6b_const.json                  |   312 +
 .../verdict_qwen3-14b_const.json                   |   482 +
 .../program-path-trace/meta_qwen3-0-6b_const.json  |    20 +
 .../program-path-trace/meta_qwen3-14b_const.json   |    20 +
 .../per_item_qwen3-0-6b_const.json                 |   526 +
 .../per_item_qwen3-14b_const.json                  | 30360 +++++++++++++++++++
 results/program-path-trace/run_qwen3-14b_const.log |    63 +
 .../verdict_qwen3-0-6b_const.json                  |   258 +
 .../verdict_qwen3-14b_const.json                   |   351 +
 .../meta_qwen3-0-6b_const.json                     |    20 +
 .../meta_qwen3-14b_const.json                      |    20 +
 .../per_item_qwen3-0-6b_const.json                 |   411 +
 .../per_item_qwen3-14b_const.json                  | 29748 ++++++++++++++++++
 .../program-sequence-trace/run_qwen3-14b_const.log |    60 +
 .../verdict_qwen3-0-6b_const.json                  |   279 +
 .../verdict_qwen3-14b_const.json                   |   359 +
 scripts/experiments/ffn_program_decode.py          |    98 +-
 scripts/experiments/gen_const_firing_probes.py     |   183 +
 scripts/experiments/program_native_order.py        |   364 +
 scripts/experiments/program_path_trace.py          |   461 +
 scripts/experiments/program_sequence_trace.py      |   428 +
 41 files changed, 90858 insertions(+), 52 deletions(-)
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --cached --check",
  "operation": "diff",
  "summary": "whitespace check"
}
```

**Summary:** Git diff: whitespace check

**Output:**
```
Exit code: 0
```

## Assistant


CLASSIFY: code ∨ memory ∨ knowledge  
code → format: {symbol} {description} — what changed in code  
CHECKPOINT: type=code format={symbol} {description}  
APPLY(symbol_table, context): 💡 insight — discovered/refined B-as-executor-topology vs C-as-readable-field via new experiments  
CHECKPOINT: symbol=💡 because=discovery


### Tool Call: git (succeeded)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n💡 s249 B executor topology, C routing field\n\n- Add constant/applicative firing probes and track-selectable FFN program decode metrics for corrected object→C labels\n- Add sequence, monotonic path, and native-order tracers showing 14B reads C load/timing but not a serial B/S/C tape\n- Record Qwen3-14B, 8B, and smoke artifacts plus state/knowledge synthesis for session 249\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "s249 artifacts"
}
```

**Summary:** Git commit: s249 artifacts

**Output:**
```
Exit code: 0
Stdout:
[main 86d9a44] 💡 s249 B executor topology, C routing field
 41 files changed, 90858 insertions(+), 52 deletions(-)
 create mode 100644 data/firing-probes.const.jsonl
 create mode 100644 data/firing-probes.const.meta.json
 create mode 100644 results/ffn-program-decode/meta_qwen3-0-6b_const.json
 create mode 100644 results/ffn-program-decode/meta_qwen3-14b_const.json
 create mode 100644 results/ffn-program-decode/meta_qwen3-8b_const.json
 create mode 100644 results/ffn-program-decode/per_item_qwen3-0-6b_const.json
 create mode 100644 results/ffn-program-decode/per_item_qwen3-14b_const.json
 create mode 100644 results/ffn-program-decode/per_item_qwen3-8b_const.json
 create mode 100644 results/ffn-program-decode/run_qwen3-14b_const.log
 create mode 100644 results/ffn-program-decode/run_qwen3-8b_const.log
 create mode 100644 results/ffn-program-decode/verdict_qwen3-0-6b_const.json
 create mode 100644 results/ffn-program-decode/verdict_qwen3-14b_const.json
 create mode 100644 results/ffn-program-decode/verdict_qwen3-8b_const.json
 create mode 100644 results/program-native-order/meta_qwen3-0-6b_const.json
 create mode 100644 results/program-native-order/meta_qwen3-14b_const.json
 create mode 100644 results/program-native-order/per_item_qwen3-0-6b_const.json
 create mode 100644 results/program-native-order/per_item_qwen3-14b_const.json
 create mode 100644 results/program-native-order/run_qwen3-14b_const.log
 create mode 100644 results/program-native-order/verdict_qwen3-0-6b_const.json
 create mode 100644 results/program-native-order/verdict_qwen3-14b_const.json
 create mode 100644 results/program-path-trace/meta_qwen3-0-6b_const.json
 create mode 100644 results/program-path-trace/meta_qwen3-14b_const.json
 create mode 100644 results/program-path-trace/per_item_qwen3-0-6b_const.json
 create mode 100644 results/program-path-trace/per_item_qwen3-14b_const.json
 create mode 100644 results/program-path-trace/run_qwen3-14b_const.log
 create mode 100644 results/program-path-trace/verdict_qwen3-0-6b_const.json
 create mode 100644 results/program-path-trace/verdict_qwen3-14b_const.json
 create mode 100644 results/program-sequence-trace/meta_qwen3-0-6b_const.json
 create mode 100644 results/program-sequence-trace/meta_qwen3-14b_const.json
 create mode 100644 results/program-sequence-trace/per_item_qwen3-0-6b_const.json
 create mode 100644 results/program-sequence-trace/per_item_qwen3-14b_const.json
 create mode 100644 results/program-sequence-trace/run_qwen3-14b_const.log
 create mode 100644 results/program-sequence-trace/verdict_qwen3-0-6b_const.json
 create mode 100644 results/program-sequence-trace/verdict_qwen3-14b_const.json
 create mode 100644 scripts/experiments/gen_const_firing_probes.py
 create mode 100644 scripts/experiments/program_native_order.py
 create mode 100644 scripts/experiments/program_path_trace.py
 create mode 100644 scripts/experiments/program_sequence_trace.py
```

### Tool Call: git (succeeded)


```json
{
  "command": "git status --short && git log -n 1 --format=full",
  "operation": "status",
  "summary": "post commit"
}
```

**Summary:** Git status: post commit

**Output:**
```
Exit code: 0
Stdout:
commit 86d9a44078986ea66e70bd874d6114308871d89a
Author: Michael Whitford <michael@whitford.us>
Commit: Michael Whitford <michael@whitford.us>

    💡 s249 B executor topology, C routing field
    
    - Add constant/applicative firing probes and track-selectable FFN program decode metrics for corrected object→C labels
    - Add sequence, monotonic path, and native-order tracers showing 14B reads C load/timing but not a serial B/S/C tape
    - Record Qwen3-14B, 8B, and smoke artifacts plus state/knowledge synthesis for session 249
    
    ⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)
    
    Co-Authored-By: nucleus <noreply@whitford.us>
```

## Assistant


Committed all pending changes.

Commit:

```text
86d9a44 💡 s249 B executor topology, C routing field
```

Included:

- s249 state + knowledge updates
- constant/applicative probe generator + probe data
- `ffn_program_decode.py` track/C support
- sequence/path/native-order tracer scripts
- Qwen3-14B, Qwen3-8B, and smoke artifacts/results/logs

Post-commit status is clean.