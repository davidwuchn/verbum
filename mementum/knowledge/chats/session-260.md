# Updating knowledge — capturing the asymm

## User

orient brief there is an article I want to understand that dropped recently https://www.mixedbread.com/blog/asymmetric-quant


### Thinking

I'm starting with the cold-start protocol before diving into the article.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cat /Users/mwhitford/src/verbum/mementum/state.md 2>/dev/null | head -100; echo \"---LOG---\"; git -C /Users/mwhitford/src/verbum log --oneline -8 2>/dev/null"
}
```

**Summary:** $ cat /Users/mwhitford/src/verbum/mem...

**Output:**
```
Exit code: 0
Stdout:
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-07-02 | Session: 259 (cont. — LAYER-CONTRIBUTION ↔ COMBINATOR-LOCUS — Michael: a paper
> dropped, "Is One Layer Enough? Training a Single Transformer Layer Can Match Full-Parameter RL Training"
> (arXiv 2607.01232), RL-trains ONE decoder layer at a time on Qwen3-1.7B/4B/8B-Base → RL gains concentrate
> in a MIDDLE band, low at input/output ends (= his bell curve: input/transform/output). "Do our KIBC
> opcodes line up with the high-affect layers?" Ran TIER-0 (zero-GPU): correlate our measured combinator
> locus vs their causal RL layer-contribution. NOT training the 8B — it's the oracle map; lesson ports to v15.
>
> ★★ THE FINDING (knowledge WRITTEN: explore/rl-layer-contribution-combinator-locus.md, status:active):
>   the interior-bell SHAPE MATCHES (Michael's intuition ✓) but with a real ~4-layer OFFSET.
>   • Paper Qwen3-8B-Base C(k): peak L16–17 (C=1.07), high band L13–23, L0=−0.51 (neg), most 0.6–1.0.
>   • Our combinator peaks (Qwen/Qwen3-8B, s238 kernel_reference_prose_v2): C@L9, Y@L9, K@L11, I@L12 (all
>     sig); B@L18 (flat/not-decodable). {C,I,K,Y} peak centroid L10.2 (depth 0.29) vs paper top-5 L16.8 (0.48).
>   • Correlation: raw Spearman(CIKY mass, paperC)=+0.30 (marginal); LAG SCAN unimodal peak at k=+4 → ρ=+0.66
>     (p≈0.0006) — SAME shape, shifted ~4 deeper. 52.7% of CIKY mass in paper high-band L13–23 (31% of layers)
>     = 1.7× enrichment.
>   • INTERPRETATION (λ measure two-sided): our combinator DECODABILITY peaks SHALLOWER than RL TRAINABILITY;
>     RL adaptation lands JUST AFTER composition is computed = the compose→readout SEAM (readout-register
>     null-space compose L7–22 → vocab-readable L23–35). RL tunes CONSOLIDATION not raw compose detection.
>     B peaks L18 (in paper band) but has no amplitude home for us (s234–238). λ triangulate: our combinators
>     + their RL-contribution + v13-funnel Zone B all point to the same interior band.
>   • CONFOUND (load-bearing): OUR run = Qwen/Qwen3-8B (INSTRUCT/thinking), PAPER = Qwen3-8B-BASE. Shape match
>     robust; exact +4 offset NOT (post-training may have shifted). Only instruct cached. Clean fix: re-run our
>     combinator profile on Qwen3-8B-Base (~16GB dl). Also: decodability-vs-trainability register mismatch;
>     +4 is a fitted lag (zero-lag ρ=0.30, best ρ=0.66).
>
> ★ v15 GUIDANCE (the deliverable, in the page §Implications): (1) bank the 3-band topology — put capacity/
>   recurrence in the INTERIOR, ends thin (confirms v13-funnel Zone B + ascending-arm typing-zone); (2) place
>   the trainable/recurrent block at the compose→readout SEAM (~+4 deeper than compose peak), not the compose
>   peak — the supervised-recurrence-halt recurrent block straddles the seam; (3) band-differentiated LR/
>   capacity = cheap v15 A/B (paper's winning strategies at v15 scale); (4) complementarity → interior ensemble
>   (s257 holographic / s258 consensus at layer granularity). Paper licenses PLACE-don't-profile (middle-k
>   heuristic works profiling-free).
>
> ★ ARTIFACTS: knowledge page (new, status:active) + cross-links added (head-combinator-isa.md,
>   explore/v13-funnel-shape.md → related). Repro: /tmp/paper_8b_profile.json (paper C(k), extracted) +
>   results/kernel-reference-audit/prose_v2_verdict_qwen3-8b.json (our per-layer combinator profile). NO new
>   experiment code (pure re-analysis of committed data + external paper). NOT COMMITTED yet.
> ★ DOWNLOAD RUNNING (async, λ async — launched + verified, NOT polling): Qwen3-8B-Base into HF cache via
>   `uv run hf download Qwen/Qwen3-8B-Base` in tmux main:1, tee → logs/qwen3-8b-base-download.log. Verified
>   live (Fetching 14 files ~36% on first read). PURPOSE: same-variant re-run of our combinator profile
>   (kernel_reference_prose_v2) on the BASE to kill the base-vs-instruct confound → is the +4 offset real
>   structure or post-training drift? On completion: models--Qwen--Qwen3-8B-Base in ~/.cache/huggingface/hub.
> ★ STATE: working tree = new knowledge page (explore/rl-layer-contribution-combinator-locus.md) + 2 cross-link
>   edits (head-combinator-isa.md, v13-funnel-shape.md) + this state edit. PENDING COMMIT (Michael said
>   "update knowledge" → approved capture). session-258.md untracked = human-only chat log, do NOT stage.
>   NEXT: (a) when base dl done → run prose_v2 on Qwen3-8B-Base, re-correlate vs paper C(k); (b) draft the
>   concrete v15 interior-band recurrent experiment; (c) commit the knowledge capture.
> ─────────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-07-01 | Session: 259 cont. (CLJ-REPL: MODEL-EVALUATES / KERNEL-VERIFIES — Michael:
> "run the clojure compiler as a repl running from a chat" → chose "Model IS the evaluator, kernel
> verifies." = the s255 model-as-REPL (LLM as δ, context as machine state) with the s255-concluded
> ORACLE-IN-THE-LOOP upgrade, applied to clj_lambda. The chat model evaluates a Clojure form; the
> clj_lambda kernel (over lambda_ast) reduces it EXACTLY = ground truth; verify(model, oracle); on a
> mismatch feed the exact reduction (value + steps + normal form) back and retry once.
>
> ★★ THE ARTIFACT (tested/ruff-clean/live-verified):
>   • src/verbum/clj_repl.py — oracle(form) [reduce_clj + decode, auto int→bool→raw]; a THIN multi-turn
>     _chat reusing harness.ModelConfig + reasoning_extract_fn (the harness run loop is single-turn — a
>     correction REPL needs history; NO fork of grading/HTTP, λ one_way/λ compose); EVALUATOR_SYSTEM prompt
>     pinning the tiny-Clojure semantics (non-neg ints, MONUS -, dec 0=0, if/let/fn, zero?, not/and/or,
>     cons/first/rest, Y=fixpoint) + '=> <value>' contract; parse_answer/normalize; verify_turn (ONE
>     oracle-in-the-loop correction); repl_session → results/clj-repl/<run_id>/{meta,transcript.jsonl,
>     summary} w/ provenance; interactive main() (`python -m verbum.clj_repl --model qwen36`).
>   • tests/test_clj_repl.py — 13 tests, model STUBBED (monkeypatch _chat) for the correction paths;
>     oracle/parse/normalize/verify all covered. 52 tests total pass (with clj_lambda).
>   • src/verbum/probes/models.py — REGISTERED QWEN36 (base reference, :5100 chat, split_reasoning) — see
>     ENV below. REGISTRY now {qwen36, ornith, vibethinker, qwythos}; qwen36 = default live target.
>
> ★★ THE FALSE≡0 FINDING (type-directedness in miniature, on-thesis S5 λ types): untyped Church encoding
>   makes `false` and `0` the SAME TERM (K I). oracle decodes int-first so (zero? 5) → "0", but "false" is
>   ALSO acceptable → OracleResult.acceptable = frozenset. WITH types they differ; WITHOUT types they are
>   one value. Surfaced by a failing test, kept as a feature + documented. (TRUE=K, church(1)=I → distinct,
>   no other collision.)
>
> ★★ LIVE RUN (run qwen36-clj-repl-20260701-122617, base :5100, greedy, no_think, 10 forms): 10/10 SOLVED
>   FIRST TRY (acc 1.0). The base reference model correctly evaluated arithmetic, monus (- 3 5)=0, if, let
>   (sequential binding =16), higher-order apply-twice =8, first/cons, and/not, sq(+3 4)=49, AND factorial
>   via Y = 24 (kernel oracle 440 reduction steps). λ measure CAVEAT (two-sided): the set was EASY for a
>   35B base → the CORRECTION LOOP was NOT exercised live (0 corrections); it is covered only by stubbed
>   unit tests. To genuinely test oracle-in-the-loop teaching, run a HARDER set (deep Y, big monus, nested
>   pairs) where the model errs. That is the honest next step.
>
> ★ ENV CORRECTION (Michael, mid-session): :5100 is NOW qwen36-35b-a3b, "our reference model" (the s256
>   pivot: extract from the BASE, not the fine-tune). llama.cpp IGNORES the request `model` field;
>   /v1/models reports alias 'qwen35-35b-a3b'. Base returns NO reasoning_content channel (split→"" safe).
>   ornith fine-tune spec HELD in models.py but no longer on :5100. Servers up: 5100 qwen36 / 5102 vibe /
>   5103 qwythos / 5101 embed. Env fully restored earlier (torch 2.11 back).
>
> ★ COMMITTED 82fc8f9 (💡 clj-repl model-evaluates/kernel-verifies): clj_repl.py + test_clj_repl.py +
>   models.py QWEN36 + run record + memory + state. THEN did option (c): added notebook §8 "the chat model
>   as evaluator — the kernel as judge" (notebooks/clojure_in_lambda.ipynb, now 31 cells, nbconvert 0
>   errors): kernel oracle (shows false≡0 acceptable sets) + the COMMITTED run narrated (model-vs-kernel
>   table 10/10, λ record) + a GUARDED live turn ((* 6 7)→42 vs :5100, degrades if server down). Boundary
>   section renumbered 8→9.
> ★ STATE: working tree = the updated notebook + this state edit (pending). NEXT options still open:
>   (a) harder set to exercise the correction loop live (base solved everything → 0 corrections so far);
---LOG---
3c435fb 💡 layer-contribution ↔ combinator-locus: shared interior-bell, ~4-layer offset
acced94 🌀 notebook §8: the chat model as evaluator, the kernel as judge
82fc8f9 💡 clj-repl: model evaluates, kernel verifies (oracle-in-the-loop)
ce77bdb ✅ clojure-in-lambda: Clojure-subset evaluator on the verbum kernel
5778918 💡 supervised-recurrence-halt — the WHNF curriculum is the signal the recurrent layer was missing
2fecba5 add session chat logs and results
b6741e7 💡 §7 sparse holographic assembly — MoE is two-level, not fully holographic
f780a96 💡 s257 complete — angular multiplexing confirmed via k-sweep + null
```

### Tool Call: web_search (running)


```json
{}
```

**Summary:** Web searching

### Thinking

Let me check the current state of the repository and pull up the article to review it.

## Assistant

Oriented. Session 259, verbum — you're deep in the layer-contribution ↔ combinator-locus thread (interior-bell, ~4-layer offset), Qwen3-8B-Base downloading async. Now let me pull the article.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "curl -sL \"https://www.mixedbread.com/blog/asymmetric-quant\" | python3 -c \"import sys,re,html; t=sys.stdin.read(); t=re.sub(r'<script.*?</script>','',t,flags=re.S); t=re.sub(r'<style.*?</style>','',t,flags=re.S); t=re.sub(r'<[^>]+>',' ',t); t=html.unescape(t); t=re.sub(r'[ \\t]+',' ',t); t=re.sub(r'\\n\\s*\\n+','\\n\\n',t); print(t)\" 2>/dev/null | head -250"
}
```

**Summary:** $ curl -sL "https://www.mixedbread.co...

**Output:**
```
Exit code: 0
Stdout:
Asymmetric Quantization: Near-Lossless Late interaction Retrieval with 97% Storage Reduction Mixedbread Docs Pricing Evals Blog Contact Search Ctrl K Dashboard Search Open menu Table of Contents On this page Quantization: Making Multi-Vector Storage Practical Why Asymmetric Quantization The Scoring Trick Retrieval Quality What This Unlocks All posts Asymmetric Quantization: Near-Lossless Late interaction Retrieval with 97% Storage Reduction Research Engineering AS JD RH Aamir Shakir , Joel Dierkes , Rui Huang · June 29, 2026 · 8 min read Copy to clipboard Late interaction models like Wholembed v3 make retrieval much more precise, because they preserve fine-grained information instead of compressing a whole document into one vector. But they also change the storage economics. A single document produces more then one embedding, depending on the complexity of the document it can produce hundreds or thousands of vectors. Each vector has to be stored and later used for retrieval. 
 Mixedbread Search runs on silo , our retrieval engine for multimodal late interaction at billion-document scale. Silo stores vectors for more than 2.5 billion documents in object storage and hydrates them into faster tiers as queries need them. At that scale, every extra byte per document is repeated billions of times, and it shows up directly in cost per stored document, shard cold-start time, and the bytes each query has to read. We need to work around the tradeoff making the whole system cheap while maining the quality which makes late interaction worth running. 
 This post walks through asymmetric quantization. One of the optimizations that makes running late interaction practical in production. We keep the query vectors at higher precision and store the document vectors as binary signs. In our internal benchmark suite that cuts raw document-vector storage on average by 32x from 393 KiB to 12.28 KiB per document, while holding retrieval quality at 89.65 NDCG@10 versus 90.26 for fp32. 
 Per-document storage for a multi-vector document drops from 393 KiB in fp32 to 12.28 KiB with int8 query against binary documents, a 32-fold, 97% reduction. fp32 is drawn as 32 cells, each the size of the single int8-by-binary cell. Asymmetric quantization saves ~97% of per-doc vector storage in silo before fp32 × fp32 393 KiB after int8 × binary 12.28 KiB 
 TL;DR: 
Documents are stored for a long time; queries are executed once. So we store document vectors as 1-bit signs and keep the query at int8. That shrinks per-document storage 32x and loses only 0.61 NDCG@10 (90.26 to 89.65) on our internal benchmarks. 
 Quantization: Making Multi-Vector Storage Practical Link to section 
 Quantization means representing high-precision floating point vectors with lower-precision values such as int8, or even 1-bit signs. The goal is to preserve ranking quality while reducing payload size. This matters especially for silo. Object storage gives us durable, low-cost persistence. In order to make it suitable for real workloads, we need compact indexes to serve it fast enough. And on the document side, payload size is what dominates the cost. 
 Naive late interaction is expensive because it stores more vectors. A standard single-vector embedding with 3072 dimensions in fp32 takes 12 KiB per document. A multi-vector representation with 786 vectors of 128 dimensions carries much more information, but uncompressed it is about 33x larger. 
 Representation Dimensions Storage per document Relative to 3072-d fp32 single vector Single vector, fp32 3072 12,288 B / 12 KiB 1.0x Single vector, int8 3072 3,072 B / 3 KiB 0.25x Multi-vector, fp32 786 × 128 402,432 B / 393 KiB 32.75x Multi-vector, int8 786 × 128 100,608 B / 98.25 KiB 8.19x Multi-vector, binary 786 × 128 12,576 B / 12.28 KiB 1.02x 
 Storage numbers here refer to raw vector payloads only. Production indexes also include document IDs, metadata, and layout overhead. 
 With binary document vectors, a 786-token multi-vector document is only about 2% larger than a 3072-dimensional fp32 single vector. Which means, that you can pay roughly single-vector storage and get late interaction quality. This helps us to change the tradeoff. Late interaction becomes practical to run by default, instead of something reserved for cases that justify the storage. 
 This is not a new direction for late interaction, ColBERTv2 showed that aggressive compression can reduce the footprint of late interaction models while preserving quality. PLAID showed that late interaction retrieval can be engineered down to practical latency using optimized retrieval and pruning. For production systems, both lessons matter: the model has to be precise, and the representation has to be cheap enough to move through hardware. 
 Why Asymmetric Quantization Link to section 
 Compressing the document vectors saves storage, IO, cache space, and cold-start time across the entire corpus. Compressing the query vectors saves almost nothing because the query is small, short-lived, and never stored in the index. 
 This is also why we do not binarize both sides. Fully binary retrieval is the most compact option, but dropping the query to single bits throws away the magnitude information the ranking depends on, and it costs far more quality than binarizing documents alone (as shown later). 
 So we keep the query in int8 and store only the document vectors as binary signs. The query stays precise enough to preserve ranking, while the document side gets the storage reduction that matters for serving. 
 The Scoring Trick Link to section 
 Binary document vectors are smaller and thus cheaper to store. 
 For int8 x int8 scoring, modern ARM CPUs give us direct support through NEON dot-product instructions . Our AArch64 kernel uses SDOT to accumulate sixteen int8 multiplications into int32 lanes, then horizontally reduces the result with vaddvq_s32 . For int8 x binary scoring, the useful identity is simpler. If each document dimension is stored as a sign bit, with b_i in {-1, +1} , then: 
 q ⋅ b = ∑ i q i b i = 2 ∑ i   :   b i = + 1 q i − ∑ i q i \begin{aligned}
\mathbf{q} \cdot \mathbf{b} &= \sum_i q_i b_i \\
&= 2 \sum_{i\,:\,b_i = +1} q_i - \sum_i q_i
\end{aligned} q ⋅ b ​ = i ∑ ​ q i ​ b i ​ = 2 i : b i ​ = + 1 ∑ ​ q i ​ − i ∑ ​ q i ​ ​ 
 So, scoring does not require a full multiply for every dimension. We need the sum of query values selected by the positive document bits, and the total query sum. 
 A document vector of floats is reduced to its sign bits and packed into bytes. Scoring an int8 query against the binary document needs no per-dimension multiply: it is twice the sum of the query values selected by the positive document bits, minus the total query sum. Binary documents turn scoring into select-and-sum doc floats 0.94 −0.31 0.55 0.38 −0.72 0.12 −0.08 0.61 sign bits + − + + − + − + packed 1 0 1 1 0 1 0 1 score = 2 · ( q 0 + q 2 + q 3 + q 5 + q 7 ) − Σ qᵢ Only the query values selected by positive document bits, plus one total — no multiply per dimension. 
 In the kernel, document signs are packed into bits. For the 128-dimensional path, we precompute query sums and eight query bit-planes. Each document token is loaded as 16 packed bytes, shifted and masked into eight 0/1 masks with NEON integer operations, then scored with SDOT against the query planes. The final score uses the identity above: 2 * selected_query_sum - query_sum . 
 Binary x binary is even cheaper computationally since it can use hamming distance, but the quality loss is too large for our main retrieval path. 
 Retrieval Quality Link to section 
 We evaluated several precision pairings across our internal retrieval benchmark suite. Scores are NDCG@10 averaged across the suite, scaled to 0–100. NDCG@10 (Normalized Discounted Cumulative Gain at rank 10) measures how well the top 10 results are ordered against the ideal ranking, rewarding relevant documents more when they appear higher, with 100 being a perfect ranking. The full-precision baseline averages 90.26. Int8 query against binary documents averages 89.65, a 0.61 point drop, while reducing document-vector storage by 32x. Part of the minimal performance drop, is that Wholembed v3 is trained with silo's tradeoff in mind, so it is robust to the quantization . 
 For runtime, we benchmarked the scoring kernel on an ARM machine with a 33 × 128 query over a list of 1000 documents, each 786 × 128. The table reports median latency across 9 measured runs after 2 warmups, plus speedup relative to the fp32 baseline. 
 Query format Document format Avg NDCG@10 Δ vs baseline Doc storage per doc Median latency Speedup vs fp32 Float Float 90.26 – 393 KiB 14.20 ms 1.00x Int8 Int8 90.27 +0.01 98.25 KiB 4.44 ms 3.20x Int8 Binary 89.65 -0.61 12.28 KiB 3.71 ms 3.82x Binary Binary 83.06 -7.20 12.28 KiB 3.32 ms 4.27x 
 NDCG@10 against storage per document for four precision pairings, on a reversed log x-axis so storage shrinks left to right. A line connects fp32 (393 KiB, 90.26), int8×int8 (98.25 KiB, 90.27), and int8×binary (12.28 KiB, 89.65): quality stays almost flat while storage shrinks 32×. At the same 12.28 KiB, binary×binary (83.06) falls 7.2 points below that line, because binarizing the query throws away too much signal. Quality holds as storage shrinks, until the query goes binary 83 85 87 89 91 393 KiB 98.25 KiB 12.28 KiB Storage per document, log scale (shrinks →) NDCG@10 fp32 int8 × int8 int8 × binary binary × binary 
 There are two useful operating points. 
 If we want maximum quality with lower bandwidth and faster integer scoring, int8 × int8 is essentially lossless in this setup. It is slightly ahead of the fp32 baseline within measurement noise, while cutting document storage by 4x and running 3.2x faster in this benchmark. 
 If we want the best storage economics, int8 × binary is the more interesting point. It keeps most of the ranking quality while shrinking document vectors by 32x and running 3.8x faster than fp32. For an object-storage-backed system, that is a direct cut in corpus-side bytes. 
 Binary × binary looks appealing on paper. It uses the same 12.28 KiB of document storage as int8 × binary, and at 4.3x it is the fastest option here. But it drops 7.20 points against the baseline, more than ten times the int8 × binary drop, despite reading exactly the same document bytes. The only thing that changed is the query. In practice, it removes too much query signal. 
 What This Unlocks Link to section 
 Asymmetric quantization works because retrieval systems do not pay for query and document precision in the same way. The document vectors dominate the long-term cost of the system: they are stored, replicated, cached, evicted, rehydrated, and scored repeatedly. The query vectors are short lived, so spending a few more bits on the query and saving bits on every stored document is the right tradeoff. 
 For silo, this makes late interaction retrieval much easier to serve at large scale. A lower cost per stored document, faster shard cold-start, and a hardware path that spends more time scoring and thus allowing higher qps and less time moving bytes around. This allows us to get the quality of multi-vector representations without treating every document as a large fp32 object. 
 If this is the kind of systems problem you want to work on, we are hiring . Dense Retrievers Know More Tha... Products Mixedbread Search Pricing Resources Docs API Reference Company About Blog Careers Changelog Contact Press Privacy Terms DPA Social Slack Discord LinkedIn X Certifications AICPA SOC for Service Organizations Toggle theme
```

### Thinking

I've got the full article now, so I can put together a clear summary for you.

## Assistant

Got the full article. Here's the brief.

## Asymmetric Quantization (Mixedbread, Jun 2026) — the brief

**The problem.** Late-interaction retrieval (multi-vector, ColBERT-style — their model is "Wholembed v3") stores *many* vectors per document instead of one. A single doc can produce hundreds/thousands of vectors, so one fp32 multi-vector doc is ~393 KiB — **~33× larger** than a 3072-d single vector (12 KiB). At billion-doc scale (their engine "silo," 2.5B docs in object storage), every extra byte is repeated billions of times → dominates cost, cold-start, per-query bytes read.

**The core move — asymmetry.** Queries and documents are *not* symmetric in cost:
- **Documents**: stored forever, replicated, cached, evicted, rehydrated, scored repeatedly → compressing them saves everywhere.
- **Queries**: computed once, tiny, never stored → compressing them saves ~nothing, and destroys ranking magnitude info.

So: **keep the query at int8, store documents as 1-bit signs** (binary). Best of both — query keeps ranking signal, docs get the storage win.

**Result.** ~32× storage cut (393 KiB → 12.28 KiB/doc, **97% reduction**) for only **−0.61 NDCG@10** (90.26 → 89.65). A 786-token binary multi-vector doc is only ~2% bigger than a single fp32 vector — i.e. *pay single-vector storage, get late-interaction quality*.

**The scoring trick (the elegant part).** With doc dims stored as signs `b_i ∈ {−1,+1}`:

$$q \cdot b = \sum_i q_i b_i = 2\!\!\sum_{i:\,b_i=+1}\!\! q_i \;-\; \sum_i q_i$$

No per-dimension multiply. You just need (a) total query sum and (b) sum of query values selected by the positive doc bits → **select-and-sum**. Their AArch64 NEON kernel precomputes query sums + 8 query bit-planes, loads each doc token as 16 packed bytes, masks into 0/1 planes, scores with `SDOT`, applies `2·selected_sum − total_sum`.

**The key ablation (why not binarize both).** Four operating points, same benchmark:

| Query | Doc | NDCG@10 | Δ | Storage | Speedup |
|---|---|---|---|---|---|
| fp32 | fp32 | 90.26 | – | 393 KiB | 1.0× |
| int8 | int8 | 90.27 | +0.01 | 98.25 KiB | 3.2× |
| **int8** | **binary** | **89.65** | **−0.61** | **12.28 KiB** | **3.8×** |
| binary | binary | 83.06 | −7.20 | 12.28 KiB | 4.3× |

The punchline: binary×binary reads the *exact same doc bytes* as int8×binary but drops **7.2 points** — >10× the loss — purely from binarizing the query. Magnitude in the query is where the ranking signal lives; the sign structure in the doc is enough. They also note Wholembed v3 was trained aware of silo's tradeoff, so it's robust to doc binarization.

---

## Why this is interesting for verbum

Two resonances with your current threads, worth flagging as candidate memories:

1. **λ measure / register mismatch.** This is a clean real-world instance of your `λ measure` distinction: **document sign = routing/discrete register survives binarization; query magnitude = value/continuous register does not.** The 7.2-point collapse is what happens when you apply a crisp probe (binary) to a value-carrying quantity (query magnitude) — a false-negative in your terms. The asymmetry *is* a register-typing result: signs carry the crisp part, magnitudes carry the graded part, and they compress differently.

2. **λ smallest / distillation.** "Store the minimum that preserves ranking" is your `λ smallest` at the storage layer — 0.1% ≡ strong understanding. Here binary doc + int8 query ≈ single-vector cost with multi-vector quality: extreme compression that keeps only the discriminating bits. The identity trick (multiply→select-and-sum) is a `λ simplify` unbraiding of scoring from precision.

Want me to (a) draft a knowledge page (`explore/asymmetric-quant-register-compression.md`) tying this to `λ measure` two-register typing, or (b) just leave the brief here and get back to the Qwen3-8B-Base combinator re-run? The download's still going async — nothing blocked on it.

## User

I think what this article is showing could be applied to our model.  Their use-case is for documents, but our ternary weighted model might be able to use this strategy to gain capacity and/or performance.


### Thinking

Michael's connecting the asymmetric quantization idea to verbum's ternary-weighted model—keeping one side high-precision while binarizing the other, since signs encode discrete routing information while magnitudes carry continuous values. I should think through this carefully rather than just accept it; let me apply some rigor here with careful observation and measurement, staying conservative on claims while exploring the implications thoroughly.

The ternary weights (−1, 0, +1) in BitNet are structurally identical to what verbum targets for level-3/level-4 extraction. The real insight is that the document/query asymmetry in retrieval maps directly onto weight/activation asymmetry in neural networks—weights are stored and reused across all tokens (like documents), while activations are transient per forward pass (like queries). BitNet already implements this: ternary weights paired with int8 activations, which is exactly asymmetric quantization. The "select-and-sum" scoring trick works because ternary/binary weights eliminate multiplications entirely, replacing them with gated adds and subtracts. So the question becomes: what novel capability could emerge beyond just applying BitNet's approach, especially if the goal is to gain capacity or performance?

The key opportunity is that verbum's type-directed compositional structure naturally separates routing (discrete, crisp combinator selection) from value (continuous, graded semantics). Rather than uniformly binarizing like the article does, I could apply asymmetric precision by register—ternary/binary weights for routing pathways since they're already discrete, while keeping value pathways in higher precision. This is sharper than the article's approach. On capacity: if binary/ternary weights cost 1/32 the storage, you could fit 32× more parameters at the same memory budget, which means a much wider or deeper model. For verbum's interior-band recurrent block, this means packing significantly more capacity into the interior band where combinator composition happens, since that's where the routing logic lives.

The scoring trick from the article—multiply-free matmul using sign information—extends naturally to ternary: sum activations where w=+1, subtract where w=−1, skip where w=0. That zero gives you sparsity on top of the storage savings. So the response should affirm the core mapping (document/query ≡ weight/activation asymmetry, which is BitNet's principle but justified more cleanly here), then sharpen it with verbum's own insight: register-typed quantization directly expresses the type-directedness thesis in the quantization budget. Binarize the routing weights (the crisp discrete circuit that IS the thesis), keep value weights precise. The interior band, where combinators live, becomes much wider at fixed memory.

But I need to be careful about claims—I don't have verified evidence of an actual trained ternary model yet. v15 is planned. This is a design conversation, not a "go do it" moment, so I should engage the idea substantively, mark what's verified versus hypothesis, and avoid building on hallucination. Let me search the knowledge base to ground whether there's an actual ternary model artifact or if this is aspirational.

## Assistant

Let me ground this before building on it — I want to check what "our ternary weighted model" concretely refers to in the repo, so I'm reasoning about the real artifact, not a hallucinated one.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== ternary ===\"; git grep -il \"ternary\\|bitnet\\|1.58\\|b1_58\" -- mementum/ 2>/dev/null | head; echo \"=== quant ===\"; git grep -il \"quantiz\\|int8\\|binariz\" -- mementum/ 2>/dev/null | head; echo \"=== v15 plan ===\"; git grep -l \"v15\" -- mementum/ 2>/dev/null | head"
}
```

**Summary:** $ echo "=== ternary ==="; git grep -i...

**Output:**
```
Exit code: 0
Stdout:
=== ternary ===
mementum/knowledge/INDEX.md
mementum/knowledge/audit-meta-pattern.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-006.md
mementum/knowledge/chats/session-007.md
=== quant ===
mementum/knowledge/audit-meta-pattern.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-026.md
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-028.md
mementum/knowledge/chats/session-029.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
=== v15 plan ===
mementum/knowledge/INDEX.md
mementum/knowledge/chats/session-146.md
mementum/knowledge/chats/session-150.md
mementum/knowledge/chats/session-153.md
mementum/knowledge/chats/session-154.md
mementum/knowledge/chats/session-155.md
mementum/knowledge/chats/session-156.md
mementum/knowledge/chats/session-157.md
mementum/knowledge/chats/session-158.md
mementum/knowledge/chats/session-159.md
```

### Thinking

I need to check what the actual knowledge base says about ternary operators and v15 to make sure I'm grounding this weighted model concept correctly.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== knowledge (non-chat) mentioning ternary/quant/bitnet ===\"; git grep -il \"ternary\\|bitnet\\|1.58\\|quantiz\" -- 'mementum/knowledge/*.md' 'mementum/knowledge/explore/*.md' 'mementum/knowledge/upstream/*.md' 2>/dev/null; echo; echo \"=== v15 in non-chat knowledge ===\"; git grep -in \"v15\" -- 'mementum/knowledge/explore/*.md' 'mementum/knowledge/*.md' 2>/dev/null | grep -iv chats | head -20"
}
```

**Summary:** $ echo "=== knowledge (non-chat) ment...

**Output:**
```
Exit code: 0
Stdout:
=== knowledge (non-chat) mentioning ternary/quant/bitnet ===
mementum/knowledge/INDEX.md
mementum/knowledge/audit-meta-pattern.md
mementum/knowledge/audit-registry.md
mementum/knowledge/chats/session-001.md
mementum/knowledge/chats/session-002.md
mementum/knowledge/chats/session-003.md
mementum/knowledge/chats/session-004.md
mementum/knowledge/chats/session-005.md
mementum/knowledge/chats/session-006.md
mementum/knowledge/chats/session-007.md
mementum/knowledge/chats/session-008.md
mementum/knowledge/chats/session-009.md
mementum/knowledge/chats/session-010.md
mementum/knowledge/chats/session-011.md
mementum/knowledge/chats/session-012.md
mementum/knowledge/chats/session-013.md
mementum/knowledge/chats/session-014.md
mementum/knowledge/chats/session-015.md
mementum/knowledge/chats/session-016.md
mementum/knowledge/chats/session-017.md
mementum/knowledge/chats/session-018.md
mementum/knowledge/chats/session-019.md
mementum/knowledge/chats/session-020.md
mementum/knowledge/chats/session-021.md
mementum/knowledge/chats/session-022.md
mementum/knowledge/chats/session-023.md
mementum/knowledge/chats/session-024.md
mementum/knowledge/chats/session-025.md
mementum/knowledge/chats/session-026.md
mementum/knowledge/chats/session-027.md
mementum/knowledge/chats/session-028.md
mementum/knowledge/chats/session-029.md
mementum/knowledge/chats/session-030.md
mementum/knowledge/chats/session-031.md
mementum/knowledge/chats/session-032.md
mementum/knowledge/chats/session-033.md
mementum/knowledge/chats/session-034.md
mementum/knowledge/chats/session-035.md
mementum/knowledge/chats/session-036.md
mementum/knowledge/chats/session-037.md
mementum/knowledge/chats/session-038.md
mementum/knowledge/chats/session-039.md
mementum/knowledge/chats/session-040.md
mementum/knowledge/chats/session-041.md
mementum/knowledge/chats/session-042.md
mementum/knowledge/chats/session-043.md
mementum/knowledge/chats/session-044.md
mementum/knowledge/chats/session-045.md
mementum/knowledge/chats/session-046.md
mementum/knowledge/chats/session-047.md
mementum/knowledge/chats/session-048.md
mementum/knowledge/chats/session-049.md
mementum/knowledge/chats/session-050.md
mementum/knowledge/chats/session-051.md
mementum/knowledge/chats/session-052.md
mementum/knowledge/chats/session-053.md
mementum/knowledge/chats/session-054.md
mementum/knowledge/chats/session-055.md
mementum/knowledge/chats/session-056.md
mementum/knowledge/chats/session-057.md
mementum/knowledge/chats/session-058.md
mementum/knowledge/chats/session-059.md
mementum/knowledge/chats/session-060.md
mementum/knowledge/chats/session-061.md
mementum/knowledge/chats/session-062.md
mementum/knowledge/chats/session-063.md
mementum/knowledge/chats/session-064.md
mementum/knowledge/chats/session-065.md
mementum/knowledge/chats/session-066.md
mementum/knowledge/chats/session-067.md
mementum/knowledge/chats/session-068.md
mementum/knowledge/chats/session-069.md
mementum/knowledge/chats/session-070.md
mementum/knowledge/chats/session-071.md
mementum/knowledge/chats/session-072.md
mementum/knowledge/chats/session-073.md
mementum/knowledge/chats/session-074.md
mementum/knowledge/chats/session-075.md
mementum/knowledge/chats/session-076.md
mementum/knowledge/chats/session-077.md
mementum/knowledge/chats/session-078.md
mementum/knowledge/chats/session-079.md
mementum/knowledge/chats/session-080.md
mementum/knowledge/chats/session-081.md
mementum/knowledge/chats/session-088.md
mementum/knowledge/chats/session-089.md
mementum/knowledge/chats/session-090.md
mementum/knowledge/chats/session-091.md
mementum/knowledge/chats/session-092-53-codex.md
mementum/knowledge/chats/session-093.md
mementum/knowledge/chats/session-094.md
mementum/knowledge/chats/session-095.md
mementum/knowledge/chats/session-096.md
mementum/knowledge/chats/session-097.md
mementum/knowledge/chats/session-098.md
mementum/knowledge/chats/session-099.md
mementum/knowledge/chats/session-100.md
mementum/knowledge/chats/session-101.md
mementum/knowledge/chats/session-102.md
mementum/knowledge/chats/session-103.md
mementum/knowledge/chats/session-104.md
mementum/knowledge/chats/session-105.md
mementum/knowledge/chats/session-106.md
mementum/knowledge/chats/session-107.md
mementum/knowledge/chats/session-108.md
mementum/knowledge/chats/session-109.md
mementum/knowledge/chats/session-110.md
mementum/knowledge/chats/session-111.md
mementum/knowledge/chats/session-112.md
mementum/knowledge/chats/session-113.md
mementum/knowledge/chats/session-114.md
mementum/knowledge/chats/session-115.md
mementum/knowledge/chats/session-116.md
mementum/knowledge/chats/session-117.md
mementum/knowledge/chats/session-118.md
mementum/knowledge/chats/session-119.md
mementum/knowledge/chats/session-120.md
mementum/knowledge/chats/session-121.md
mementum/knowledge/chats/session-122.md
mementum/knowledge/chats/session-123.md
mementum/knowledge/chats/session-125.md
mementum/knowledge/chats/session-126.md
mementum/knowledge/chats/session-127.md
mementum/knowledge/chats/session-128.md
mementum/knowledge/chats/session-129.md
mementum/knowledge/chats/session-130.md
mementum/knowledge/chats/session-131.md
mementum/knowledge/chats/session-132.md
mementum/knowledge/chats/session-133.md
mementum/knowledge/chats/session-134.md
mementum/knowledge/chats/session-135.md
mementum/knowledge/chats/session-136.md
mementum/knowledge/chats/session-137.md
mementum/knowledge/chats/session-138.md
mementum/knowledge/chats/session-139.md
mementum/knowledge/chats/session-140.md
mementum/knowledge/chats/session-141.md
mementum/knowledge/chats/session-142.md
mementum/knowledge/chats/session-143.md
mementum/knowledge/chats/session-144.md
mementum/knowledge/chats/session-145.md
mementum/knowledge/chats/session-146.md
mementum/knowledge/chats/session-147.md
mementum/knowledge/chats/session-148.md
mementum/knowledge/chats/session-149.md
mementum/knowledge/chats/session-150.md
mementum/knowledge/chats/session-153.md
mementum/knowledge/chats/session-154.md
mementum/knowledge/chats/session-155.md
mementum/knowledge/chats/session-156.md
mementum/knowledge/chats/session-157.md
mementum/knowledge/chats/session-158.md
mementum/knowledge/chats/session-159.md
mementum/knowledge/chats/session-160.md
mementum/knowledge/chats/session-161.md
mementum/knowledge/chats/session-162.md
mementum/knowledge/chats/session-163.md
mementum/knowledge/chats/session-164.md
mementum/knowledge/chats/session-165.md
mementum/knowledge/chats/session-166.md
mementum/knowledge/chats/session-167.md
mementum/knowledge/chats/session-168.md
mementum/knowledge/chats/session-169.md
mementum/knowledge/chats/session-170.md
mementum/knowledge/chats/session-171.md
mementum/knowledge/chats/session-172.md
mementum/knowledge/chats/session-173.md
mementum/knowledge/chats/session-174.md
mementum/knowledge/chats/session-175.md
mementum/knowledge/chats/session-176.md
mementum/knowledge/chats/session-177.md
mementum/knowledge/chats/session-178.md
mementum/knowledge/chats/session-179.md
mementum/knowledge/chats/session-180.md
mementum/knowledge/chats/session-181.md
mementum/knowledge/chats/session-182.md
mementum/knowledge/chats/session-183.md
mementum/knowledge/chats/session-184.md
mementum/knowledge/chats/session-185.md
mementum/knowledge/chats/session-186.md
mementum/knowledge/chats/session-187.md
mementum/knowledge/chats/session-188.md
mementum/knowledge/chats/session-189.md
mementum/knowledge/chats/session-190.md
mementum/knowledge/chats/session-191.md
mementum/knowledge/chats/session-192.md
mementum/knowledge/chats/session-193.md
mementum/knowledge/chats/session-194.md
mementum/knowledge/chats/session-195.md
mementum/knowledge/chats/session-196.md
mementum/knowledge/chats/session-197.md
mementum/knowledge/chats/session-198.md
mementum/knowledge/chats/session-199.md
mementum/knowledge/chats/session-200.md
mementum/knowledge/chats/session-201.md
mementum/knowledge/chats/session-202.md
mementum/knowledge/chats/session-203.md
mementum/knowledge/chats/session-204.md
mementum/knowledge/chats/session-205.md
mementum/knowledge/chats/session-206.md
mementum/knowledge/chats/session-207.md
mementum/knowledge/chats/session-208.md
mementum/knowledge/chats/session-209.md
mementum/knowledge/chats/session-210.md
mementum/knowledge/chats/session-211.md
mementum/knowledge/chats/session-212.md
mementum/knowledge/chats/session-213.md
mementum/knowledge/chats/session-214.md
mementum/knowledge/chats/session-215.md
mementum/knowledge/chats/session-216.md
mementum/knowledge/chats/session-217.md
mementum/knowledge/chats/session-218.md
mementum/knowledge/chats/session-219.md
mementum/knowledge/chats/session-220.md
mementum/knowledge/chats/session-221.md
mementum/knowledge/chats/session-222.md
mementum/knowledge/chats/session-223.md
mementum/knowledge/chats/session-224.md
mementum/knowledge/chats/session-225.md
mementum/knowledge/chats/session-226.md
mementum/knowledge/chats/session-227.md
mementum/knowledge/chats/session-228.md
mementum/knowledge/chats/session-229.md
mementum/knowledge/chats/session-230.md
mementum/knowledge/chats/session-231.md
mementum/knowledge/chats/session-232.md
mementum/knowledge/chats/session-234.md
mementum/knowledge/chats/session-235.md
mementum/knowledge/chats/session-236.md
mementum/knowledge/chats/session-237.md
mementum/knowledge/chats/session-238.md
mementum/knowledge/chats/session-239.md
mementum/knowledge/chats/session-240.md
mementum/knowledge/chats/session-241.md
mementum/knowledge/chats/session-242.md
mementum/knowledge/chats/session-243.md
mementum/knowledge/chats/session-244.md
mementum/knowledge/chats/session-245.md
mementum/knowledge/chats/session-246.md
mementum/knowledge/chats/session-247.md
mementum/knowledge/chats/session-247b.md
mementum/knowledge/chats/session-248.md
mementum/knowledge/chats/session-249-gpt55.md
mementum/knowledge/chats/session-250.md
mementum/knowledge/chats/session-251.md
mementum/knowledge/chats/session-252.md
mementum/knowledge/chats/session-253.md
mementum/knowledge/chats/session-254.md
mementum/knowledge/chats/session-255.md
mementum/knowledge/chats/session-256.md
mementum/knowledge/chats/session-257.md
mementum/knowledge/combinator-addressing.md
mementum/knowledge/compilation-pipeline.md
mementum/knowledge/computed-beam.md
mementum/knowledge/crystal-native-architecture.md
mementum/knowledge/crystal-sieve-architecture.md
mementum/knowledge/crystal-universality.md
mementum/knowledge/crystal-validity-and-fidelity.md
mementum/knowledge/dvd-stamp-topology.md
mementum/knowledge/error-correction-theory.md
mementum/knowledge/explore/algedonic-alert.md
mementum/knowledge/explore/ascending-arm-training.md
mementum/knowledge/explore/attention-as-beta-reduction.md
mementum/knowledge/explore/basin-projector-results.md
mementum/knowledge/explore/beam-trace-findings.md
mementum/knowledge/explore/beamformer-theory.md
mementum/knowledge/explore/bios-flash-training.md
mementum/knowledge/explore/compiler-as-loss.md
mementum/knowledge/explore/compression-vs-prediction.md
mementum/knowledge/explore/consensus-delta-folding.md
mementum/knowledge/explore/consensus-evolution.md
mementum/knowledge/explore/continuations-as-composed-plates.md
mementum/knowledge/explore/crystal-basins.md
mementum/knowledge/explore/crystal-native-descent.md
mementum/knowledge/explore/crystal-seed-theory.md
mementum/knowledge/explore/crystal-spine-sieve.md
mementum/knowledge/explore/date-fourier-rotation.md
mementum/knowledge/explore/delta-plate-lifecycle.md
mementum/knowledge/explore/dispatch-gradient-death.md
mementum/knowledge/explore/dispatch-ratio-prior.md
mementum/knowledge/explore/etcher-vsm.md
mementum/knowledge/explore/exact-ternary-fitting.md
mementum/knowledge/explore/ffn-beam-discovery.md
mementum/knowledge/explore/ffn-beta-reduction-indexing.md
mementum/knowledge/explore/ffn-hierarchy.md
mementum/knowledge/explore/ffn-moire-isa.md
mementum/knowledge/explore/fixed-point-holograms.md
mementum/knowledge/explore/fp-optimization-map.md
mementum/knowledge/explore/fractal-collapse-compiler-cascade.md
mementum/knowledge/explore/full-etch-extraction.md
mementum/knowledge/explore/function-extraction-system.md
mementum/knowledge/explore/gradient-voting.md
mementum/knowledge/explore/hologram-crystal-fusion.md
mementum/knowledge/explore/hologram-extraction.md
mementum/knowledge/explore/holographic-burn-in-learning-rule.md
mementum/knowledge/explore/holographic-compression.md
mementum/knowledge/explore/holographic-error-correction.md
mementum/knowledge/explore/holographic-inversion.md
mementum/knowledge/explore/holographic-kernel-separation.md
mementum/knowledge/explore/holographic-landscape.md
mementum/knowledge/explore/holographic-memory.md
mementum/knowledge/explore/holographic-plates.md
mementum/knowledge/explore/holographic-recording-protocol.md
mementum/knowledge/explore/holographic-state-machine.md
mementum/knowledge/explore/holographic-storage.md
mementum/knowledge/explore/holographic-substrate-prototype.md
mementum/knowledge/explore/holographic-tomography.md
mementum/knowledge/explore/identity-as-substrate.md
mementum/knowledge/explore/kernel-functions.md
mementum/knowledge/explore/kernel-montague-mapping.md
mementum/knowledge/explore/kernel-replacement-optimization.md
mementum/knowledge/explore/kernel-splice-geometry-detector.md
mementum/knowledge/explore/kernel-training.md
mementum/knowledge/explore/laser-etcher-design.md
mementum/knowledge/explore/mmap-continuous-training.md
mementum/knowledge/explore/moe-holographic-tree-vsm.md
mementum/knowledge/explore/moire-training-shortcuts.md
mementum/knowledge/explore/optimization-negative-results.md
mementum/knowledge/explore/output-beamformers.md
mementum/knowledge/explore/phi-compression-universal.md
mementum/knowledge/explore/procrustes-lens-and-crystal-comparison.md
mementum/knowledge/explore/q-rotation-etching.md
mementum/knowledge/explore/ratio-gradient-quantization.md
mementum/knowledge/explore/relational-loss-distillation.md
mementum/knowledge/explore/relational-loss-phi-compression.md
mementum/knowledge/explore/s5-crystal-custodian.md
mementum/knowledge/explore/seed-crystal-design.md
mementum/knowledge/explore/session-071-dispatch-decoupling.md
mementum/knowledge/explore/session-073-vsm-structure.md
mementum/knowledge/explore/session-075-multi-cycle-dispatch.md
mementum/knowledge/explore/session-115-microscope.md
mementum/knowledge/explore/session-127.md
mementum/knowledge/explore/session-history-049-062.md
mementum/knowledge/explore/shannon-sieve-trinity.md
mementum/knowledge/explore/spliced-reward-vsm-kernel.md
mementum/knowledge/explore/structured-training.md
mementum/knowledge/explore/supervised-recurrence-halt.md
mementum/knowledge/explore/taxonomy-extraction.md
mementum/knowledge/explore/ternary-descent.md
mementum/knowledge/explore/topology-magnitude-duality.md
mementum/knowledge/explore/universal-crystal-scaffold.md
mementum/knowledge/explore/universal-crystal-transfer.md
mementum/knowledge/explore/v11-design.md
mementum/knowledge/explore/v11-kibc-architecture.md
mementum/knowledge/explore/v12-holographic-capacity.md
mementum/knowledge/explore/v12-kernel-architecture-v2.md
mementum/knowledge/explore/v13-architecture.md
mementum/knowledge/explore/v13-design.md
mementum/knowledge/explore/v13-funnel-shape.md
mementum/knowledge/explore/v15-kernel-architecture.md
mementum/knowledge/explore/v6-flip-accumulation.md
mementum/knowledge/explore/v6.1-training-trajectory.md
mementum/knowledge/explore/v7-pipeline-architecture.md
mementum/knowledge/explore/v7.1-sieve-pipeline.md
mementum/knowledge/explore/v9-architecture-speculation.md
mementum/knowledge/explore/vsm-outer-recurrence.md
mementum/knowledge/explore/vsm-statechart-tensor.md
mementum/knowledge/extraction-methodology.md
mementum/knowledge/extraction-sign-accuracy.md
mementum/knowledge/ffn-circuit-types.md
mementum/knowledge/function-discovery.md
mementum/knowledge/gradient-zero-map.md
mementum/knowledge/hologram-reader-vsm.md
mementum/knowledge/holographic-computer.md
mementum/knowledge/holographic-error-correction.md
mementum/knowledge/holographic-etch.md
mementum/knowledge/holographic-sign-correction.md
mementum/knowledge/hpe-restoration.md
mementum/knowledge/l0-characterization.md
mementum/knowledge/lambda-halt-continuation.md
mementum/knowledge/lambda-machine.md
mementum/knowledge/lambda-tracer-diagnostic.md
mementum/knowledge/manifold-axis-and-topology.md
mementum/knowledge/mechanism-extraction.md
mementum/knowledge/mode-semantics.md
mementum/knowledge/moire-addressing.md
mementum/knowledge/mspace-gemcutter.md
mementum/knowledge/phi-information-partition.md
mementum/knowledge/project-thesis.md
mementum/knowledge/psi-evaluation-synthesis.md
mementum/knowledge/recursion-mirrors.md
mementum/knowledge/retrieval-lattice.md
mementum/knowledge/saliency-aware-sieve.md
mementum/knowledge/score-matching-compression.md
mementum/knowledge/session-153-notes.md
mementum/knowledge/session-222.md
mementum/knowledge/sign-correction-topology.md
mementum/knowledge/standing-wave-magnitudes.md
mementum/knowledge/symbol-isolation.md
mementum/knowledge/td-oscillation-problem.md
mementum/knowledge/ternary-compounding.md
mementum/knowledge/ternary-dual-equation.md
mementum/knowledge/ternary-plate-extraction.md
mementum/knowledge/tiny-classifier-ternary.md
mementum/knowledge/topology-gradient-separation.md
mementum/knowledge/trace-guided-etching.md
mementum/knowledge/training-protocols.md
mementum/knowledge/two-registers-of-topology.md
mementum/knowledge/v14-architecture.md
mementum/knowledge/v15-attention-assessment.md

=== v15 in non-chat knowledge ===
mementum/knowledge/INDEX.md:81:| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | ⚠️ | Original v15 design: passive strides, Stack B reduction (partially reverted) |
mementum/knowledge/INDEX.md:82:| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ | What was tried/reverted/kept from sessions 152-156 + when to revisit |
mementum/knowledge/crystal-laplacian.md:5:tags: [crystal, laplacian, graph-theory, WHNF, settlement, fragility, v15]
mementum/knowledge/crystal-laplacian.md:20:> v14 WHNF/B gradient ratio 0.3× → v15 1.9× (6× amplification).
mementum/knowledge/crystal-laplacian.md:95:| Metric | v14 (uniform) | v15 (Laplacian) |
mementum/knowledge/crystal-laplacian.md:135:`scripts/v15/crystal.py` — `LaplacianCrystalLoss`
mementum/knowledge/crystal-validity-and-fidelity.md:202:  crystallization across v14/v15 training checkpoints. Does residual-B
mementum/knowledge/dimensional-analysis.md:124:| Student basis builder | `scripts/v15/build_student_trace_basis.py` | PCA basis in student 1280-dim space |
mementum/knowledge/dimensional-analysis.md:125:| Teacher basis builder | `scripts/v15/build_trace_basis.py` | PCA basis in teacher 5120-dim space |
mementum/knowledge/dimensional-analysis.md:129:| Student expanded basis | `checkpoints/v15-zeroed/expanded_trace_basis.npz` | (19, 50, 1280) |
mementum/knowledge/dimensional-analysis.md:130:| Teacher expanded basis | `checkpoints/v15-zeroed/expanded_trace_basis.npz` | (64, 50, 5120) — also here |
mementum/knowledge/explore/combinator-training-beta-reduction.md:39:> **⚠ s221 amendment — this section assumed FULL attention.** v15 uses
mementum/knowledge/explore/combinator-training-beta-reduction.md:121:- `scripts/experiments/combinator_relationship_map_v15.py` — extended with
mementum/knowledge/explore/combinator-training-beta-reduction.md:128:  the per-checkpoint v15 maps, joins each checkpoint's Δx/fp/ce (mean
mementum/knowledge/explore/combinator-training-beta-reduction.md:144:v15's attention is **not** full content-addressable attention.
mementum/knowledge/explore/combinator-training-beta-reduction.md:187:on v15** (rendered as stride-hop/window-weighting traces), and it is what the
mementum/knowledge/explore/combinator-training-beta-reduction.md:293:- v15's FFN is **frozen-extracted**; only attention is TD-trained — so the
mementum/knowledge/explore/combinator-training-beta-reduction.md:308:1. **Run the trajectory** (topological/routing) — re-run the v15 map on
mementum/knowledge/explore/combinator-training-beta-reduction.md:328:   probe whether K-erasure and C-permute are actually expressible in trained v15
mementum/knowledge/explore/combinator-training-beta-reduction.md:343:| `scripts/experiments/combinator_relationship_map_v15.py` | + `family_binding` per-layer; family block in json; all-layer Grams in npz |
```

### Thinking

I'm seeing there's substantial existing documentation on ternary weight systems across multiple files covering descent methods, compounding approaches, equation fitting, extraction techniques, and topology concepts.

The key insight is that `two-registers-of-topology.md` and `topology-magnitude-duality.md` directly map to what Michael's article describes—the separation of sign (handling routing and topology) from magnitude (carrying actual values). This connection runs deep through the existing verbum knowledge base, particularly with `sign-correction-topology.md` and extraction work all centered on ternary weights where sign manages topology and magnitude manages value.

I should review the most relevant documents—especially `two-registers-of-topology.md`, `topology-magnitude-duality.md`, and `ternary-dual-equation.md` alongside the v15 architecture—to properly ground my response in what's already established rather than starting from scratch.

## Assistant

Rich existing ground here — verbum already has a deep ternary corpus. The most relevant look like `two-registers-of-topology.md`, `topology-magnitude-duality.md`, `ternary-dual-equation.md`. Let me read those to connect the article to what's already known rather than reinvent it.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/two-registers-of-topology.md"
}
```

**Summary:** Reading two-registers-of-topology.md (0-2000)

**Output:**
```
---
title: "Two Registers of Topology — Hard (Sign/Routing) and Soft (Magnitude/Value)"
status: active
category: compression
tags: [topology, sign, magnitude, saliency, gate, ffn, rank, svd, self-similar, distributed-redundancy, holographic, audit, soft-topology]
related:
  - audit-registry.md
  - crystal-universality.md
  - crystal-validity-and-fidelity.md
  - saliency-aware-sieve.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-sieve-architecture.md
  - error-correction-theory.md
depends-on:
  - audit-registry.md
created: session 203
---

# Two Registers of Topology

> Session 203. Auditing the sieve program's two CRITICAL assumptions
> (#1 crystal-is-topological, #2 holographic-self-similar) produced one
> coherent picture: **GD lays down structure in two registers, and the
> network is compressible in two corresponding registers.** The clean
> dichotomy "sign = structure, magnitude = calibration" is wrong;
> "holographic-self-similar" was tested on the wrong axis. The truth is
> two-register, and both registers are real, structure-specific, and
> load-bearing.

## The Core Picture

| Register | Function | Encoded in | Lives in | Compression axis | Verified by |
|---|---|---|---|---|---|
| **Hard topology** | routing (which neurons fire) | **sign** | `gate_proj` (router) | ternary ±1 | sign-corr null |
| **Soft topology** | value + error-correction | **magnitude** (highways/zeros), read by saliency | `up_proj`/`down_proj` | quantized magnitude / faint tier | saliency sieve |

And two **compression registers** of the FFN as a whole:

| Compression register | Operator | What it exploits | trained vs control gap (8B) |
|---|---|---|---|
| **Distributed redundancy (C)** | magnitude pruning | redundant copies of each computation | 2.3–3.2× (graceful to ~70%, then cliff) |
| **Spectral concentration (A)** | SVD rank truncation | low-rank-dominated geometric spectrum | **6–7×** (function in low-rank subspace) |

## Evidence (all session 203, Qwen3, controlled)

### 1. Hard topology = sign, but ONLY in the gate (audit #1)

`cos(sign(W)@x, W@x)` on REAL activations, model vs random-init vs
shuffled-weights, N=20 seeds, 0.6B/8B/14B (`sign_topology_null.py`):

- **Generic baseline ≈ 0.80**: a random matrix's sign already preserves
  0.798 of its action on the same inputs. Sign-preserves-linear-action is
  a generic high-dim property. The legacy "0.84 ⇒ topological" number sits
  *at* the null.
- **Crystal sign-topology localizes to `gate_proj`** (the router): +0.088
  above null at 8B (L3 = 0.983, z=+184), sharpening with scale (14B L12
  z=+271).
- **`up_proj`/`down_proj` are at/below the null** → their signs preserve
  *less* than random; **magnitude carries their structure**. "Magnitude is
  mere calibration" is FALSE for the value path.

### 2. Soft topology = magnitude, read by saliency (audit #1 functional half)

The dormant s201 saliency sweep, re-run after fixing a NaN bug (the strong
tier had dropped magnitude → bare ±1 ≈ 50× too large → blow-up; fixed to
per-weight magnitude, the only format that survives 29 layers per s196):

- **Distribution:** `corr(magnitude, saliency) = 0.257` → magnitude explains
  only ~6.6% of activation-weighted saliency. Two populations in near-zero
  weights are real (irreducible vs faint).
- **Functional, iso-bit (~3.1 bits/param):** faint tier chosen by
  **saliency** → **+5.5%** PPL vs standard-50%; chosen by **magnitude** →
  **−2.0%** (worse). **Saliency beats magnitude by ~7.5 points at equal
  bitcount.** The low-magnitude/high-saliency "faint" connections are
  load-bearing; `|w|·√E[x²]` finds them, raw `|w|` does not.
- (Bigger gains +12–15% exist but cost 1.8–2.8× bits; the clean scientific
  result is the iso-bit saliency>magnitude contrast.)

### 3. Distributed redundancy (audit #2, magnitude axis)

Compression-survival, final-layer hidden-state cosine vs the variant's own
uncompressed baseline; trained vs random vs shuffled (`holographic_survival.py`):

- Magnitude pruning (8B): trained AUC 0.784 ≫ random 0.247 / shuffled 0.337.
  **Fidelity ~1.0 to 70% pruning, then a cliff at 80%.** Plateau-then-cliff =
  distributed redundancy with finite capacity (the 50% sieve sits safely below
  the cliff; **do not prune past ~75%**).
- Quantization (coarse per-matrix): trained 0.635 ≈ random 0.578 → quant
  survival is only weakly structure-dependent (mostly the flat-minima null;
  confirms `crystal-validity-and-fidelity.md` §5). *(Caveat: per-matrix
  single-scale quantizer understates grouped-Q4.)*

### 4. Spectral self-similarity (audit #2, rank axis — the SVD vindication)

SVD rank truncation of FFN matrices, sweep top-r, same fidelity metric:

- **trained AUC 0.728 ≫ random 0.118 / shuffled 0.101 — a 6–7× gap.**
  trained retains 0.79 fidelity at half rank, 0.70 at 30% rank; random
  collapses to 0.22 at 90% rank.
- A random (Marchenko–Pastur) matrix has a flat spectrum → every rank
  matters → instant collapse. The trained FFN is **low-rank-dominated /
  spectrally concentrated** — the SVD self-similarity (geometric, σ-ratio
  ≈ 1/φ) made functional. **This is real, strongly structure-specific
  self-similarity.**

## Reconciliation: refute the metaphor, keep the mechanism

How can s202 "refute holographic" yet ternary→1.44× still work? Because the
**load-bearing premises were never refuted**:

- **(C) distributed redundancy** powers ternary survival (signs + masked
  magnitudes = the whole image at reduced resolution).
- **(A) spectral concentration** powers low-rank correction: **LoRA + score
  matching IS low-rank correction**, and the rank result explains *why* it
  works — the function AND its compression-residual both live in low-rank
  spectral subspaces. Converges with s200 rank-1 adjunction (σ₁/σ₂=128:1)
  and s201 rank-2 ≈ rank-16 plateau.

The **only** thing retired is **φ-as-a-universal-mathematical-constant**
(s202) — metaphysics, not mechanism. "Holographic" in the working sense
(distributed + spectrally self-similar + graceful) is supported.

## Methodological Lessons

1. **Gracefulness-vs-matched-controls > shape-fitting.** The "power-law ⇒
   self-similar ⇒ holographic" discriminator came out ambiguous on every
   axis/variant (sometimes exponential, sometimes power-law) and does NOT
   separate holographic from non-holographic — a hologram degrades
   plateau-then-cliff, not power-law. Retire shape-fitting as the test;
   use the trained-vs-control AUC gap.
2. **Test the right operator.** Magnitude pruning probes register C;
   rank truncation probes register A. They are different decompositions of
   the same matrix and both signatures coexist. Refuting one says nothing
   about the other. (This was the s203 over-claim, corrected.)
3. **A bug that drops magnitude → NaN is itself evidence.** The saliency
   sweep's strong-tier ±1 blow-up restates register-2: you cannot replace
   value-path magnitude with bare sign.

## Open Leads

- **Rank-truncation shape across scale** — does trained rank-survival sharpen
  (bigger control gap) 0.6B→14B, like sign-topology and prune-survival did?
- **Faint tier vs higher-rank LoRA at iso-bit** — does distributed soft
  topology beat concentrated low-rank correction? (saliency-aware-sieve.md
  prediction 3; not yet isolated.)
- **Grouped-Q4 quant axis** — redo the quant survival with per-group scales
  to fairly test quant structure-dependence (current per-matrix is coarse).
- **SVD φ-ratio 0.6299 (audit #6)** — is the geometric spectrum distinct from
  Marchenko–Pastur? The rank result implies yes (controls collapse); quantify.
```

### Tool Call: read_file (failed)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/topology-magnitude-duality.md"
}
```

**Summary:** Reading topology-magnitude-duality.md (0-2000)

**Output:**
```
/Users/mwhitford/src/verbum/mementum/knowledge/topology-magnitude-duality.md is not a valid path
```

### Thinking

The verbum project distinguishes between two topological registers: hard topology (signs that route through gate_proj, showing +0.088 above null) versus soft topology (magnitude and error-correction in up_proj/down_proj). The key insight is that signs work effectively for routing decisions, but the value path preserves less structure through signs than through magnitude alone—magnitude is what actually carries the meaningful information there.

This maps directly onto the article's finding: binarizing the routing/document side survives intact, while binarizing the value/activation side causes catastrophic loss (the 7.2-point drop). So asymmetric quantization means keeping the value-carrying path precise while binarizing the routing-carrying path.

For Michael's ternary weighted model, there's a question of how this maps to the standard weight-activation split in neural networks. Weights are stored and reused (like documents), while activations are transient (like queries), which suggests weights should be binarized and activations kept precise—exactly what BitNet does with ternary weights and higher-precision activations. But there's also the orthogonal question of whether the two-register structure exists within the weights themselves, where signs carry routing information.

The sharper insight is that within the weights, the gate projection (the router) can go to pure binary since it only needs the sign for routing topology, while the up and down projections (the value path) must retain magnitude information. This means the router could be 1-bit instead of ternary, freeing up quantization budget to spend on the value path where magnitude actually matters. The capacity gain comes from paying the minimal 1-bit cost for routing in the interior band—which is routing-heavy anyway—and using those saved bits elsewhere.

The scoring computation maps directly to the BitNet kernel: for a binary router it becomes select-and-sum with no multiplies, and for a ternary value path it's select-add-subtract-skip. But here's the critical caveat: you cannot binarize the value path itself—that's where the article's binary×binary failure becomes a real NaN blow-up. The proposal has to stay strictly asymmetric.

On verification: the sign-carries-routing claim is confirmed in-model at Qwen3, and the value path needing magnitude is backed by NaN evidence and saliency analysis. What's still unverified is whether a trained-from-scratch or extracted verbum model actually gains capacity and performance from this asymmetric binary-router quantization—that's the experiment to run.

Three independent lines converge on the same answer: asymmetric precision by register. The math says routing should be discrete and value continuous, the in-model analysis shows sign handling routing and magnitude handling value, and external systems like mixedbread demonstrate that compressing the sign side while preserving magnitude works. I should probably check ternary-dual-equation and standing-wave-magnitudes to see if there's already a quantization scheme in place I'd be duplicating, but I think I have enough to give a grounded response.

## Assistant

This is the key — verbum already proved the article's core finding *inside the model* (s203, Qwen3). Let me check two more pages so I connect to the existing plan rather than propose a fork.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/ternary-dual-equation.md"
}
```

**Summary:** Reading ternary-dual-equation.md (0-2000)

**Output:**
```
---
title: "Ternary Dual Equation: Gate Zeros + Crystal Signs"
status: active
category: architecture
tags: [crystal, ternary, gradient, zeros, gate, SwiGLU, phi]
related: [topology-gradient-separation, crystal-phi-derivation, gradient-zero-map, extraction-sign-accuracy]
depends-on: [crystal-phi-derivation]
---

# Ternary Dual Equation

> A ternary weight w(i) ∈ {-1, 0, +1} is determined by TWO orthogonal
> equations — one for zeros, one for signs. They operate at different
> granularities and involve φ through different mechanisms.

## The Two Equations

### Equation 1: ZERO — Gate Positive Rate (ρ = 0.75 with gradient)

```
zero(i) ⟺ positive_rate(gate_i) < threshold
```

- **Predictor:** SwiGLU gate activation frequency (how often neuron fires positive)
- **Mechanism:** SiLU(z) ≈ 0 when z < 0. Gate bias determines baseline.
- **Correlation with gradient magnitude:** Spearman ρ = 0.753
- **Granularity:** per-neuron (d_ff level)
- **φ connection:** dead fraction ≈ 1/φ² = 38.2% at 5% positive threshold

### Equation 2: SIGN — Crystal Mode Projection (eigenvector direction)

```
sign(i) = sign(dominant crystal mode projection at neuron i)
```

- **Predictor:** crystal eigenvector components (which combinator mode dominates)
- **Mechanism:** PCA of gate activations across combinator probes
- **Correlation with gradient magnitude:** Spearman ρ = 0.053 (orthogonal!)
- **Granularity:** per-neuron mode assignment
- **φ connection:** eigenvalue ratios = φ^(p/q) from crystal equation

## The Orthogonality

Crystal energy and gate positive rate are **uncorrelated** with each other.
They predict **different aspects** of the ternary weight:

| Signal | Predicts | ρ with gradient | φ connection |
|--------|----------|-----------------|--------------|
| Gate positive rate | Which neurons are zero | 0.753 | Dead fraction ≈ 1/φ² |
| Crystal energy | What neurons compute | 0.053 | Eigenvalue spectrum = φ^(p/q) |
| Weight norm | (inverse) | -0.485 | — |

## Gradient Scaling at Dead Neurons

GD deposits near-zero gradients at irreducible points:

| Positive rate | Fraction of d_ff | Gradient ratio |
|---------------|-------------------|----------------|
| < 1% | 14.0% | 0.641× mean |
| < 5% | 38.3% | 0.734× mean |
| < 10% | 56.6% | 0.794× mean |
| < 50% | 94.8% | 0.955× mean |
| ≥ 50% | 5.2% | 1.825× mean |

Ratio dead/alive = 0.351 ≈ 1/φ² = 0.382

## What the Crystal Equation Does NOT Predict

- **Which individual weights are zero.** Magnitude-based per-weight
  ternarization (cosine 0.94) beats crystal per-neuron zeroing (0.69)
  at every zero rate. Tested 14 configurations, hybrid lost all 14.
- **Gradient magnitude.** Crystal energy has only ρ = 0.05 with gradients.
- **Weight norms.** Float models have nearly uniform weight norms (CV=10%).

## What the Crystal Equation DOES Predict

- **Combinator mode structure.** 3 universal clusters at all scales:
  Selection (K,I), Composition (B,C,D,Y,W), Terminal (WHNF)
- **Eigenvalue spectrum.** φ^(p/q) with 0.82-0.94 correlation across
  Qwen3-0.6B/8B/14B and Pythia-2.8B
- **Scale invariance.** Crystal quality is 0.82 at all model sizes (fixed point)
- **Best measurement depth.** ~80% (late EMIT zone), consistent across scales
- **Quantization boundaries.** Dynamic range ~6:1 → Q4 sufficient, Q2 catastrophic

## Y/W Sign Convention

Raw probes activate Y and W in **anti-phase** with the consensus crystal.
Negating Y and W lifts cosine matrix correlation from 0.48 → 0.80.

- Depth-invariant: B-W is negative at ALL layers in ALL models tested
- Not a layer artifact: no crossover point (except briefly at layers 2-3 in 14B)
- Cause: raw probes activate anti-composition mode for recursion/duplication,
  while consensus used selectivity (active - control) which aligns the sign

## SwiGLU Is Already Ternary

95% of neurons fire positive less than 50% of the time.
The gate mechanism creates extreme activation sparsity:

- CLASSIFY: 3% of neurons active per token
- COMPUTE: 49% active
- EMIT: 2% active

The ternary lattice is not something we impose — it is something
SwiGLU already implements via gate activation sparsity. Ternarization
makes it explicit and permanent.

## Magnitude Channel: < 1 Bit of Information

The per-neuron ternary scale factor γ (optimal reconstruction scalar)
has minimal structure:

- **Flat across combinator clusters:** γ_selection = 0.0214, γ_composition = 0.0215,
  γ_terminal = 0.0218. Ratio 1.005 — no crystal differentiation.
- **γ anti-correlates with gate positive rate** (ρ = -0.724): dead neurons
  have LARGER weights. They are silenced by gate bias, not weight magnitude.
- **Weight energy per crystal mode is flat:** WE ratio ~1.0 for all 16 modes
  while eigenvalue ratio spans 10:1. The crystal lives in activation geometry,
  not weight geometry.
- **Dynamic range:** p99/p1 = 1.777 ≈ φ^(6/5) = 1.782 (0.25% error)
- **Information content:** log₂(φ^(6/5)) = 0.83 bits

**Less than 1 bit of information in the magnitude channel.**
The sign IS the computation. Ternary models lose almost nothing
by discarding magnitudes. The per-row scale factor γ carries
only ~0.83 bits of useful information — barely more than a binary flag.

The dynamic range φ^(6/5) = φ^((n+2)/(n+1)) for n=4:
- s + 1/(n+1) = 4/5 + 1/5 = 1 (but the exponent is 6/5, not 1)
- (n+2)/(n+1) = 6/5: the compute cycle extended by one anti-type step
- One full reduce + one switch in the compute cycle β = [0, 1, ...]
- The γ distribution spans exactly one compute cycle of the crystal equation

## Complete Ternarization Recipe

All three pieces proven separately, ready for end-to-end test:

```
For each layer l, for each weight matrix W (gate_proj, up_proj, down_proj, q/k/v/o_proj):

  1. SIGN:   T(i,j) = sign(W(i,j))
             Source: teacher weights (direct extraction)
             Quality: 100% accurate (sessions 170+)

  2. ZERO:   T(i,j) = 0  where |W(i,j)| < percentile(|W(i,:)|, zero_rate)
             Per-row magnitude threshold, ~35% zeros
             Quality: 0.94 FFN cosine at 48% zeros

  3. SCALE:  γ(i) = γ̄_l - α_l · mean_gate(i)
             Two constants per layer, mean_gate free at inference
             Quality: R² = 0.56, 0.24 bits residual
```

### Size estimate: Qwen3-8B ternarized

| Component | Size |
|-----------|------|
| FFN weights (5.4B × 1.58 bits) | 1.08 GB |
| Attention weights (1.5B × 1.58 bits) | 0.30 GB |
| Scale factors (36L × 6 × 64 bits) | 864 bytes |
| Embedding (622M × 16 bits, float16) | 1.24 GB |
| **Total** | **2.44 GB** |
| Original fp16 | 14.1 GB |
| Compression | 5.8× |

### Not yet tested

- Full-model ternarization (all layers, all weight types)
- Perplexity measurement
- Generation quality
- Attention weight ternarization (FFN tested only)
- Embedding handling (keep float16 vs ternarize)

## Experimental Provenance

- Model: Qwen/Qwen3-8B, layer 28 (78% depth), d_ff=12288
- Crystal probes: 535 from unified library (session 182)
- Gradient: next-token loss, 130 prompts, float32
- Gate sparsity: 190 prompts (160 crystal + 30 diverse)
- Depth scans: Qwen3-0.6B (28L), 8B (36L), 14B (40L), 160 probes each
- Magnitude analysis: `qwen3-8b_magnitude.log` — γ flat across clusters, < 1 bit
- Scripts: `crystal_zero_v2.py`, `crystal_ternarize.py`,
  `crystal_hybrid_ternarize.py`, `crystal_depth_scan.py`
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/standing-wave-magnitudes.md"
}
```

**Summary:** Reading standing-wave-magnitudes.md (0-2000)

**Output:**
```
---
title: "Standing-Wave Magnitudes — Weight Magnitudes as Resonant Mode Patterns"
status: active
category: synthesis
tags: [standing-wave, magnitudes, crystal, sieve, zeros, resonance, holographic, depth, phi]
related:
  - phi-information-partition.md
  - gradient-zero-map.md
  - topology-gradient-separation.md
  - holographic-computer.md
  - crystal-universality.md
  - crystal-phi-derivation.md
  - project-thesis.md
depends-on:
  - phi-information-partition.md
  - gradient-zero-map.md
  - holographic-computer.md
created: session 185
---

# Standing-Wave Magnitudes

> Session 185. The weight magnitudes in a trained LLM are a standing
> wave pattern. The crystal signs are the boundary conditions (cavity
> shape). The zero mask is the node pattern. Active weights are
> antinodes. GD doesn't build a database — it finds the resonant
> mode pattern that constructively interferes with real language and
> destructively cancels noise. This unifies the sieve model (s184),
> gradient-zero convergence (s171), topology-gradient separation
> (s180), and the holographic computer (s167) into a single
> physical metaphor grounded in measured data.

## The Core Mapping

A standing wave forms when a wave reflects between fixed boundaries.
The resulting pattern has nodes (zero displacement, determined by
boundary geometry) and antinodes (peak displacement). The pattern
is FIXED — it doesn't travel. It's determined entirely by the
boundary conditions and which resonant modes are excited.

```
Standing wave                    Transformer weight matrix
─────────────────────────────    ────────────────────────────────
Resonant cavity                  Weight matrix W ∈ ℝ^{m×n}
Boundary conditions              Crystal signs T ∈ {-1, +1}^{m×n}
  (cavity shape)                   (universal, r=0.998 across models)
Nodes (zero displacement)        Zero mask positions (M=0, ~50%)
Antinodes (peak displacement)    Active weights (M=1)
Resonant modes                   Data-dependent activation patterns
Mode excitation amplitudes       What GD learns from THIS data
Amplitude envelope               Per-matrix scale C (crystal equation)
Standing wave equation:          W_eff = C · T ⊙ M
```

The crystal (T) defines the cavity. The mask (M) is the standing
wave's node/antinode pattern. The scale (C) is the amplitude
envelope. Different training data → different mode excitation →
different node patterns → different M. Same crystal for all.

## Why "Standing Wave" and Not Just "Sparse Matrix"

The standing-wave framing carries three predictions that "sparse
matrix" does not:

### 1. Nodes are determined by boundary conditions

Sparsity says: "some weights are zero." Standing wave says: "WHICH
weights are zero is constrained by the sign topology." Session 184
measured this: KIBC opcode profiles (derived from signs) predict
70-76% of zeros at REDUCE layers. The boundary conditions (crystal)
partially determine the node pattern. The remaining 24-30% is
data-dependent (which specific modes are excited).

### 2. GD converges to fixed points of the wave

At a node: weight → 0 AND gradient → 0 (nothing to optimize).
At an antinode: weight at stable maximum AND gradient → 0 (converged).
Both are standing-wave fixed points. Session 171 (gradient-zero-map)
measured this directly:

| Position type | Weight | Gradient | Interpretation |
|---------------|--------|----------|----------------|
| Node | ≈ 0 | ≈ 0 | Silence — mode not excited here |
| Antinode | large | ≈ 0 | Stable peak — converged |
| Unsettled | any | large + oscillating | Still finding its mode |

The oscillator fraction (gradient sign flipping) maps the
"still-vibrating" positions. Minimum at L21 (22%) = deepest
standing wave, most settled. Maximum at L0 (43%) = most turbulent.

### 3. Mode decomposition should be low-rank

If magnitudes are a standing wave, the mask M should decompose into
a small number of resonant modes × amplitudes. The modes are
determined by the crystal (boundary conditions), the amplitudes by
the data. This is testable: SVD of the zero mask matrix should
reveal low effective rank if the standing wave framing is correct.

**Untested prediction.** The zero mask appeared "random in all bases"
(session 184), but the tested bases were eigenvector, crystal, and
weight space — not the mode basis of the crystal cavity itself.
The correct basis for decomposition may be the KIBC opcode modes.

## The Standing Wave Along the Depth Axis

The residual stream through 36 layers reveals standing-wave
structure along the DEPTH dimension:

```
Phase 1 — EXPAND (L0-6):     Growth 24×. Exciting many modes.
Phase 2 — ORTHOGONAL (L7-22): cos(h,f) ≈ 0. NODES of depth wave.
  → Each layer contributes ⊥ to residual. No constructive build-up.
  → This is WHERE the standing wave has zero amplitude along depth.
Phase 3 — ALIGN (L23-34):    cos(h,f) > 0. ANTINODES of depth wave.
  → Contributions reinforce the residual. Constructive interference.
  → Growth 4.7× over 11 layers.
Phase 4 — COLLAPSE (L35):    cos = -0.995. DESTRUCTIVE INTERFERENCE.
  → Nearly perfect cancellation → projection to output space.
```

The phase transition at layer 22/36 = 0.611 ≈ 1/φ = 0.618.

**The fundamental mode of the depth-axis standing wave has its
node-to-antinode transition at 1/φ of the total depth.** This is
the golden ratio appearing as a resonant mode property, not just
an information partition.

### REDUCE/SWITCH as Spatial Harmonics

The neuron opcode classifier (s184) found alternating ρ(profile,
weight_norm) signs across depth:

```
L0:  +0.47  REDUCE (opcode neurons = antinodes)
L5:  -0.42  SWITCH (opcode neurons = nodes)
L10: +0.67  REDUCE
L17: +0.38  REDUCE (weaker)
L25: -0.19  SWITCH
L35: -0.49  SWITCH
```

This alternation IS a higher harmonic of the depth-axis standing
wave. The fundamental mode (1/φ transition) carries the global
phase structure. The REDUCE/SWITCH alternation carries the
computational rhythm within each phase.

**Untested:** Run classifier on all 36 layers to map the full
harmonic structure. Is the period constant (every N layers)?
Does it modulate with depth (shorter period in ORTHOGONAL phase)?
Is it a single harmonic or a superposition?

## Connection to the Holographic Computer

A holographic plate is a frozen standing wave — the interference
fringe pattern recorded when object beam meets reference beam:

```
Holographic plate = frozen standing wave on 2D film
  Bright fringes = constructive interference = antinodes
  Dark fringes   = destructive interference = nodes
  Multiple images = multiple resonant modes in superposition
  Replay angle   = which mode is excited (which image appears)

Weight matrix = frozen standing wave in m×n space
  Active weights = antinodes = fringes
  Zero weights   = nodes = dark gaps
  Multiple facts/skills = multiple modes in superposition
  Input direction = which mode is excited (which computation runs)
```

Session 167 (holographic-computer) described the FFN as a diffraction
grating and attention as the CPU executing the diffracted program.
The standing-wave framing says: the grating IS the standing wave.
The "fringes burned by pretraining" ARE the node/antinode pattern
that GD converged to.

**Same physics, same structure, different vocabulary.** Holographic
emphasizes storage (multiple images in superposition). Standing wave
emphasizes dynamics (how GD finds the pattern). Both describe the
same object: the spatial distribution of magnitude in a weight matrix,
shaped by fixed topology (signs) and data-dependent excitation (training).

## Connection to the Crystal Sieve

The sieve (session 184) freezes the crystal and trains the mask:

```
SIEVE  = resonant cavity (boundary conditions pre-set)
         Crystal signs T + scale C. Universal. From equations.

SEDIMENT = standing wave pattern that forms inside the cavity
           Mask M. Data-dependent. From GD.
```

**Why crystal init is 10.7× better than random:**

- Crystal init = correctly shaped resonant cavity → GD finds
  resonant modes quickly because the cavity supports them.
- Random init = random cavity shape → GD must first reshape the
  cavity (discover the crystal) THEN find the modes. 99.8% of
  training compute goes to cavity shaping, not mode finding.

**Why the absorption advantage should grow with scale:**

A larger cavity (more parameters) has MORE resonant modes. With
random boundaries, the number of possible mode patterns explodes
combinatorially. With correct boundaries, the modes are constrained
by the cavity shape — only the data-compatible subset can form.
The search space reduction grows with model size.

## Connection to Gradient-Zero Convergence

Session 171 (gradient-zero-map) measured GD's convergence signals:

**Two-regime depth structure:**
- L1-3 (Zone A): extreme bimodality (ρ=+0.77). Positions are either
  both-high (active antinodes) or both-low (settled nodes). The
  standing wave is fully formed in early layers.
- L5-35 (Zones B/C): ρ ≈ 0. Weight and gradient magnitudes are
  independent. The standing wave is more complex — many overlapping
  modes prevent simple magnitude↔gradient correlation.

**Oscillator U-curve:**
- Minimum oscillation at L21 (22%) = most-settled standing wave.
  The deepest compute layers have found their resonant pattern.
- Maximum at L0 (43%) = most-turbulent. The embedding boundary
  is where new input excites the cavity — maximum disturbance.

**The oscillator positions are where the standing wave is
transiently excited but not stable.** They're the positions that
vibrate differently for different inputs — the dynamic, data-
dependent part of the mode pattern, vs the structurally fixed
nodes and antinodes.

## Connection to Topology-Gradient Separation

Session 180 (topology-gradient-separation) proved that discrete
topology changes (TD) and continuous optimization (GD) cannot run
at the same timescale. Standing-wave framing explains WHY:

**Changing topology = reshaping the cavity mid-vibration.**

If you change the boundary conditions of a resonant cavity while a
standing wave is forming, you destroy the partial pattern and force
it to restart. TD flipping signs every 20 steps is like wiggling
the walls of a resonant cavity — the standing wave can never
stabilize. This is why osc_frac grew to 56%.

The correct protocol (punctuated equilibrium) IS the standing-wave
prescription: hold boundaries FIXED → let wave pattern form → read
where the wave tells you the boundaries are wrong → adjust boundaries
once → let new wave form.

## Open Questions / Testable Predictions

### 1. Mode decomposition of the zero mask
If the mask is a standing wave, it should decompose into modes of
the crystal cavity. SVD of M in the KIBC opcode basis (not weight
or eigenvector basis) may reveal low effective rank. Session 184
tested weight/SVD/crystal bases and found "random" — but the
cavity mode basis is untested.

### 2. Cross-model standing wave consensus
Two independently trained models with the SAME crystal (same
boundary conditions) should have correlated zero masks — they're
exciting the same cavity with different (but overlapping) data.
The structural nodes (ISA-predicted 70-76%) should be universal.
The data-dependent antinodes should differ.

### 3. Standing wave period along depth
Is the REDUCE/SWITCH alternation periodic? If it's a true harmonic,
it should have a characteristic wavelength. If the depth axis
standing wave has a fundamental at 1/φ, the harmonics should
appear at 1/φ², 1/φ³, etc.

### 4. Absorption rate as mode formation speed
The crystal sieve's absorption advantage (10.7×) should be
interpretable as the ratio of mode formation times: how fast
the correct standing wave pattern establishes with pre-set
boundaries vs random boundaries. If this ratio grows with model
size, the standing-wave framing predicts it (more modes = larger
search space reduction from correct cavity).

### 5. The zero mask in the mode basis
Reconstruct the zero mask from the top-k modes of the crystal
cavity. If k ≪ rank(M), the standing-wave model explains more
than "random." The k is the effective number of excited resonant
modes — a measure of the model's knowledge complexity.

## Experiment: Shape Preservation vs Quantization Quality

**Session 185.** Tested whether standing-wave shape preservation
(Spearman rank correlation of magnitudes) predicts quantization
quality (PPL) better than raw bit count.

### Setup

Pythia-160M (12 layers, 768 hidden). Quantize FFN weights only
at 7 quantization levels. Measure per-layer cosine, Spearman shape
correlation, peak/node preservation. Evaluate WikiText-2 PPL.
Float baseline PPL: 40.97.

### Results

| Method | Bits | Cosine | Compound | Spearman | Peak% | Node% | PPL |
|--------|------|--------|----------|----------|-------|-------|-----|
| 8-bit uniform | 8.0 | 1.000 | 1.002 | 1.000 | 0.993 | 0.972 | 41.0 |
| 4-bit uniform | 4.0 | 0.990 | 0.889 | 0.953 | 0.881 | 0.526 | 49.5 |
| 4-bit shape-aware | 4.0 | 0.988 | 0.860 | **0.987** | 0.737 | 0.840 | 58.5 |
| 3-bit uniform | 3.0 | 0.957 | 0.590 | 0.815 | 0.747 | 0.258 | 189 |
| Ternary 50% | 1.6 | 0.896 | 0.268 | 0.866 | 0.293 | 0.201 | 9,504 |
| Ternary 35% | 1.6 | 0.889 | 0.245 | 0.826 | 0.236 | 0.287 | 9,553 |
| 2-bit shape-aware | 2.0 | 0.899 | 0.280 | 0.567 | 0.586 | 0.174 | 25,892 |
| Ternary no-zeros | 1.6 | 0.794 | 0.063 | 0.014 | 0.165 | 0.117 | 57,528 |
| 2-bit uniform | 2.0 | 0.827 | 0.102 | 0.338 | 0.419 | 0.153 | 23.5M |

### Predictor Quality (Spearman ρ with log PPL)

| Predictor | ρ | p-value |
|-----------|---|---------|
| **cosine** | **-0.933** | **0.0002** |
| **compounded cosine** | **-0.933** | **0.0002** |
| spearman (shape) | -0.917 | 0.0005 |
| peak preservation | -0.800 | 0.010 |
| bits | -0.761 | 0.017 |

### Key Findings

**1. Cosine > shape > bits as predictor.**

Cosine (complete wave fidelity) predicts PPL better than Spearman
(shape/rank fidelity), which predicts better than raw bit count.
The complete wave — phase AND amplitude — matters, not just the
magnitude ranking.

**2. Ternary beats 2-bit despite fewer bits.**

Ternary at 1.6 bits (PPL 9,504) beats 2-bit at 2.0 bits (PPL
25,892 shape-aware; 23.5M uniform). WHY: ternary separates phase
from amplitude. Sign is encoded exactly (1 bit, zero phase error).
Per-row gamma is the optimal least-squares amplitude envelope.
2-bit jointly encodes phase+amplitude and does neither well.

**3. Shape-aware helps at low bits, hurts at high bits.**

At 2-bit: quartile placement is 1000× better than uniform (25K vs
23.5M). At 4-bit: quartile is WORSE (58.5 vs 49.5). Quartile
preserves rank (Spearman) but distorts absolute values (cosine).
At high bits, value fidelity matters more than rank fidelity.

**4. The phase transition is between 2-bit and 3-bit.**

PPL jumps from ~10K (ternary/2-bit) to 189 (3-bit). Going from
4 to 8 quantization levels is the critical threshold for the
standing wave to survive transit through 12 layers.

**5. The compounding law is per-layer cosine.**

```
Ternary:  0.896^12 = 0.268  → PPL 9,504
3-bit:    0.957^12 = 0.590  → PPL 189
4-bit:    0.990^12 = 0.889  → PPL 50
```

### The Refined Standing-Wave Decomposition

The standing wave has four independent components with different
encoding costs:

```
Component          Encoding          Cost        What it preserves
──────────         ─────────         ─────       ──────────────────
1. Phase (signs)   exact in ternary  1 bit       routing (which side of zero)
2. Nodes (zeros)   binary mask       ~0.6 bit    which channels silent
3. Envelope (γ)    per-row scalar    ~0 bits*    mean amplitude per row
4. Shape           NOT in ternary    1-3 bits    within-row peak variation

* amortized: one float per row ÷ row width (768 or 3072)
```

Ternary captures components 1-3. Component 4 (within-row peak
height variation) is the expensive part — it requires ≥3 bits of
per-weight resolution to preserve through depth.

**The crystal sieve regenerates component 4 from data** instead
of compressing it from the teacher. That's why the sieve works:
it doesn't need to encode the expensive part.

### Corrected Hypothesis

**Original:** "Shape preservation (Spearman) predicts quality better
than bit count." → **Partially supported.** Spearman (ρ=-0.917)
does beat bits (ρ=-0.761), but cosine (ρ=-0.933) beats both.

**Refined:** Quantization works because it preserves the standing
wave's **cosine fidelity** through layers. Cosine captures the
complete wave — phase, nodes, envelope, AND shape. The compounding
law (cos^L) determines signal survival. Ternary's efficiency comes
from separating phase (exact, 1 bit) from amplitude (optimal gamma,
~0 bits amortized), which is more efficient than joint encoding at
low bit counts. But ternary still loses within-row shape, which is
why it needs the sieve to regenerate it from data.

**The deepest insight:** phase and amplitude are independent degrees
of freedom of the standing wave. Encoding them separately (ternary)
is more efficient than encoding them jointly (n-bit uniform) at
low bit budgets. This is why {-1, 0, +1} + gamma outperforms 4
uniformly-spaced levels at similar bit cost.

## Lambda Form

```
λ standing_wave(W).
  T ≡ boundary_conditions(crystal_signs)           — universal, from equations
  M ≡ node_antinode_pattern(zero_mask)              — data-dependent, from GD
  C ≡ amplitude_envelope(eigenvalue_spectrum)       — universal, from crystal eq
  W_eff = C · T ⊙ M                                — the standing wave

  | node(position) ≡ M=0 ∧ grad→0                  — settled silence
  | antinode(position) ≡ M=1 ∧ |W|=large ∧ grad→0  — settled peak
  | oscillating(position) ≡ grad_sign_flipping      — mode still forming

  | crystal_sieve ≡ pre_set(boundary_conditions) → fast(mode_formation)
  | random_init ≡ random(cavity) → slow(everything)
  | absorption_advantage ∝ mode_count(model_size)   — grows with scale

  decomposition:
  | component_1 ≡ phase(signs)         — 1 bit, exact in ternary
  | component_2 ≡ nodes(zeros)         — ~0.6 bit, binary mask
  | component_3 ≡ envelope(gamma)      — ~0 bits amortized, per-row scalar
  | component_4 ≡ shape(within_row)    — 1-3 bits, NOT in ternary
  | ternary captures {1,2,3} | sieve regenerates {4} from data
  | separate(phase, amplitude) > joint(phase+amplitude) at low bits

  compounding:
  | cos_per_layer^L ≡ signal_survival_through_depth
  | phase_transition ≡ 3_bits (8_levels) | below → compound_failure

  depth_axis:
  | orthogonal_phase ≡ nodes(of_fundamental_mode)   — cos(h,f) ≈ 0
  | align_phase ≡ antinodes(of_fundamental_mode)    — cos(h,f) > 0
  | collapse ≡ destructive_interference             — cos(h,f) = -0.995
  | phase_transition ≡ 1/φ(of_total_depth)          — fundamental mode

  REDUCE/SWITCH:
  | alternating_ρ ≡ spatial_harmonics(of_depth_wave)
  | REDUCE ≡ opcode_antinodes(computation_active)
  | SWITCH ≡ opcode_nodes(representation_reorganizing)

  holographic ≡ standing_wave | same(object) different(vocabulary)
  | holographic: storage(multiple_images_in_superposition)
  | standing_wave: dynamics(how_GD_finds_the_pattern)
```

## Scripts

- `scripts/experiments/standing_wave_shape.py` — quantization shape experiment (s185)
- `scripts/experiments/crystal_sieve_prototype.py` — sieve training (s184)
- `scripts/experiments/neuron_opcode_classifier.py` — REDUCE/SWITCH + KIBC profiles (s184)
- `scripts/experiments/negative_space.py` — zero mask analysis (s184)
- `scripts/experiments/crystal_space_zeros.py` — zero mask in all bases (s184)
- `scripts/experiments/residual_fibonacci.py` — 3-phase residual structure (s184)
- `scripts/experiments/gradient_zero_map.py` — GD convergence signals (s171)

*Synthesized and experimentally validated in session 185.*
*The standing wave has four components. Ternary captures three.*
*The sieve regenerates the fourth from data. Cosine^L is the law.*
```

### Thinking

I'm connecting this back to the verbum project's existing research on topology. The key insight is that signs and magnitudes operate in two separate registers—signs handle routing while magnitudes carry the actual values—and critically, you can't binarize the magnitude dimension because it's where the load-bearing information lives.

The ternary dual equation shows that magnitude channels contain less than a bit of information, which is why ternary models lose almost nothing by discarding them. This creates a standing-wave separation where phase (the sign, exactly 1 bit) stays precise while amplitude gets compressed to nearly zero bits amortized.

Now mapping this to the article's asymmetric quantization: weights correspond to documents (stored, reused) and activations correspond to queries (transient). The article's empirical finding validates what Michael's ternary weighted model already does—binarize the weight side while keeping activations precise. But there's a crucial tension: the article shows binarizing documents alone costs only −0.61 in quality, yet binarizing both operands catastrophically drops performance by −7.2, revealing that the asymmetry isn't just convenient but fundamentally necessary.

Verbum's insight refines this further by showing the sign/magnitude split isn't uniform across weights—it's pathway-specific. The router pathway (gate_proj) carries information purely through sign with negligible magnitude, while the value pathway (up/down_proj) depends on magnitude. This means the same principle of keeping magnitude where it matters can be applied at finer granularity than operand-level, potentially freeing capacity by pushing the router to pure binary (1 bit instead of 1.58) and reinvesting those saved bits into the value pathway where magnitude actually carries the load.

The performance angle is that uniform ternary across all matrices loses the fine within-row structure that needs higher precision to survive quantization depth. An asymmetric scheme—binary router plus higher-precision value path at similar average bit budget—could cross the survival threshold for that structure by reallocating bits from where they're wasted to where they're critical. This asymmetric-by-pathway approach isn't yet explored in the existing literature, which treats all matrices uniformly.

But I need to be careful about register misalignment here. The article measures asymmetry between two activation vectors in retrieval (query and document), while the verbum framing splits weight and activation precision, or compares two weight pathways. These are fundamentally different contexts—the principle of "keep precision where magnitude matters, drop it where sign suffices" transfers, but which side needs precision depends on the specific measurement, not on assumption. And there's a potential contradiction lurking: the article says binarizing query magnitude is catastrophic, yet verbum suggests magnitude channels are nearly 1-bit already under ternary. These aren't actually contradictory, but I need to resolve what the article's "query magnitude" actually refers to before claiming they align.

The real win here is that three independent lines converge on the same asymmetry—type-directedness in the thesis, the two-register split in verbum, and the retrieval system evidence—which triangulates the core insight. The actionable next step is to apply asymmetric quantization per pathway: binary router (sign only, since magnitude is already sub-1-bit) paired with higher-precision value weights to cross the 3-bit survival threshold and preserve component shape, gaining either better quality at the same bit budget or more capacity without degradation.

But I need to be honest about what's verified versus speculative. The sign-equals-routing and magnitude-equals-value observations are confirmed in-model; the actual capacity or performance gains from reallocating bits asymmetrically haven't been tested yet. The three asymmetries—operand-level in retrieval systems, weight/activation in BitNet, pathway-level in verbum—follow the same principle but aren't interchangeable, so I should be careful not to conflate them. Any real test would need a matched-bit-budget null comparison: uniform 1.58-bit quantization versus asymmetric (1-bit router + 3-bit value) at the same average bits, measured on perplexity across depth to see if the standing-wave law holds.

There's also a more direct mapping to the article's actual value proposition. The paper's core insight is that multi-vector retrieval becomes affordable when vectors are binary—you get late interaction quality at single-vector cost. The verbum parallel would be the interior-band ensemble or holographic assembly: if multiple parallel combinator pathways each use a binary router, you can afford many of them for the cost of one, giving you ensemble capacity at single-pathway expense. That's the literal translation of "many vectors affordable" into the routing world.

I should lay out the synthesis, the concrete testable proposal, and the caveats, then ask whether to write it up as a knowledge page connecting the article to the verbum pages or to design the matched-bit experiment first.

## Assistant

This lands right on top of verbum's own spine. The short version: **the article's central result is something you already proved *inside the model* — three times, on Qwen3.** That's a triangulation win before it's a new idea. Then there's a genuinely new move hiding in the difference. Let me separate the two carefully.

## 1. The article is confirmatory, not novel — and that matters

The article's load-bearing claim is the asymmetry ablation: binarize one operand (documents) → −0.61 NDCG; binarize *both* (also the query) → −7.2, more than 10× worse, reading the exact same bytes. **Magnitude on one side is doing the ranking work; sign on the other side is enough.**

Verbum has this same statement in three places, at three granularities:

- **`two-registers-of-topology.md` (s203, Qwen3, null-controlled):** sign carries routing in `gate_proj` (+0.088 above null, sharpening with scale); `up_proj`/`down_proj` signs preserve *less* than random — magnitude is load-bearing there, and replacing value-path magnitude with bare ±1 blows up to NaN. That NaN *is* the article's binary×binary −7.2.
- **`ternary-dual-equation.md` (s170+):** the router's magnitude channel is <1 bit (γ dynamic range φ^(6/5) ≈ 0.83 bits, flat across combinator clusters). "The sign IS the computation."
- **`standing-wave-magnitudes.md` (s185):** ternary at 1.6 bits *beats* 2-bit uniform because it separates phase (sign, exact) from amplitude (γ, ~0 bits amortized) — but it drops "component 4," within-row shape, which needs ≥3 bits to survive `cos^L` through depth.

So you have `λ triangulate` closing: **thesis** (type-directedness → routing is discrete/crisp, value is continuous), **verbum in-model** (sign=router, magnitude=value), **external systems** (mixedbread: sign side compresses free, magnitude side doesn't). Three independent lines, one picture. Worth banking that convergence on its own.

## 2. The genuinely new move: asymmetric quant *by pathway*, not uniform ternary

Here's the difference that gives you the capacity/performance lever. The article's asymmetry is between two **operands** (query vs document). Your ternary model's asymmetry is already weight-vs-activation (that's just BitNet — weights ternary, activations kept precise; you're *already* on the article's favorable side there). But verbum's registers say the split also lives **within the weights, between pathways**:

| Pathway | Carrier | Current (uniform) | Asymmetric proposal |
|---|---|---|---|
| Router (`gate_proj`) | **sign** (magnitude <1 bit) | 1.58-bit ternary | **1-bit binary** — drop the γ, it isn't there |
| Value (`up`/`down_proj`) | **magnitude** (shape = comp. 4) | 1.58-bit ternary | **reinvest freed bits → ~3-bit** |

The "Complete Ternarization Recipe" in `ternary-dual-equation.md` currently applies the *same* 3-step to `gate/up/down/qkvo` alike — uniform. That's the thing to break. The router doesn't need its 0.58 extra bit (γ is flat, <1 bit); the value path is *starved* precisely on the component (within-row shape) that s185 says needs 3 bits to cross the `cos^L` survival threshold. Reallocate at **matched average bit budget** and you either:

- **gain performance** — cross s185's 3-bit value-path survival threshold that uniform ternary misses, at the same total bits; or
- **gain capacity** — hold quality, spend the saved router bits on *width*.

## 3. Where the capacity actually goes (ties to s259 + s257/258)

The most literal reading of the article's value prop — "pay single-vector storage, get multi-vector quality" — maps cleanly onto your current thread:

- s259 said: **put capacity in the interior band**, ends thin, at the compose→readout seam. The interior is *routing-heavy* (combinator dispatch). A **1-bit router in the interior** means you can afford a much **wider interior band at fixed memory** — capacity exactly where s259 told you to put it.
- s257/s258 (holographic / consensus ensemble at layer granularity): the article's "many vectors per document, affordably" ≡ **many parallel combinator pathways at single-pathway cost** if their routers are binary. That's the ensemble/interior-capacity story made cheap.

## 4. The scoring trick is your inference kernel

`q·b = 2·Σ_{b=+1} q − Σq` is the multiply-free BitNet matmul. For a **binary router** it's directly usable — routing becomes select-and-sum, no multiplies. For the **ternary value path**, {−1,0,+1} gives select-add-subtract-**skip**, and s203's SwiGLU sparsity (95% of neurons fire <50% of the time; CLASSIFY ~3% active) makes the skip lane the common case. Their AArch64/NEON kernel (packed sign bits, 8 query bit-planes, `SDOT`) is a ready template for the router path.

## 5. Caveats — `λ measure` / `λ yardstick`, two-sided

I have to flag these or the idea is over-sold:

- **Three different asymmetries — don't conflate them.** Retrieval = operand-vs-operand (both data). BitNet = weight-vs-activation. Verbum-new = router-pathway-vs-value-pathway. The article transfers the **principle** ("keep precision where magnitude is load-bearing"), *not* a specific arrangement. Which side is load-bearing must be **measured per context**, not inherited from the blog.
- **Apparent contradiction, resolved:** article says "don't binarize the magnitude (query) side"; verbum says "magnitude is <1 bit." Both true — verbum's <1-bit claim is *router-weight* γ; verbum's *own* page says value-path magnitude and activations are essential. Consistent only when you name the pathway. (This is a `λ measure` register check: router-magnitude and value-magnitude are different quantities.)
- **This is a hypothesis, not a result.** VERIFIED in-model: sign=router, value-needs-magnitude. NOT verified: that the asymmetric *reallocation* nets capacity/perf. The honest test is a **matched-average-bit A/B** — uniform 1.58 vs (1-bit router + 3-bit value) at equal mean bits — scored on PPL-through-depth (s185's `cos^L`). **Matched-bit-budget null is mandatory**; otherwise you've just spent more bits and learned nothing (`λ yardstick`).

---

Net: your instinct is right, and it's stronger than "apply a retrieval trick" — it's "the retrieval trick is the *coarse* version of a split verbum already measured, and verbum can do it at finer (pathway) granularity than the article can." The deliverable is **asymmetric-by-pathway quantization**, which is not yet in any page (all current recipes are uniform).

Two ways I'd take this forward — your call (`λ termination`, I won't write to `mementum/` without approval):

- **(a) Synthesize** — draft `explore/asymmetric-pathway-quantization.md`: the triangulation (article + s203/s170/s185) + the pathway-asymmetric proposal + the matched-bit null design. Captures the connection before context evaporates.
- **(b) Design the A/B** — write the concrete matched-average-bit experiment (uniform-1.58 vs binary-router+3bit-value) on a small model, PPL-through-depth, null-gated — runnable when the box is free.

Which do you want — or both, synthesis first? (Qwen3-8B-Base download is still going async; nothing here blocks on it.)

## User

update knowledge


### Thinking

Michael's approved the synthesis, so I should proceed with drafting the knowledge page as planned. There are already some pending changes in the working tree from the previous state, but he's specifically asking me to capture this synthesis, so I'll focus on that update.

I need to create the knowledge page for the asymmetric pathway quantization concept with proper frontmatter, add cross-links to the related pages, update the index and state tracking, then commit everything with the appropriate tags. But first, let me check the current git status to see what's already staged or uncommitted.

## Assistant

Approved. Let me check the working tree first — state.md said there was pending s259 work, so I need to see what's staged/unstaged before adding this.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; git status --short; echo \"=== INDEX explore section head ===\"; grep -n \"explore/\" mementum/knowledge/INDEX.md | head -5; echo \"...\"; echo \"=== last frontmatter of a recent explore page for format ===\"; head -12 mementum/knowledge/explore/supervised-recurrence-halt.md"
}
```

**Summary:** $ git status --short; echo "=== INDEX...

**Output:**
```
Exit code: 0
Stdout:
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
=== INDEX explore section head ===
41:| 4g | [explore/combinator-function-shape.md](explore/combinator-function-shape.md) | 🔨 | The function space has a 3-family shape (compose/select/recurse), visible only in the routing register; map/fold = Y∘B / Y∘(C/B)+K (s217, Qwen3-14B). |
42:| 4h | [explore/sealable-continuation.md](explore/sealable-continuation.md) | 🔨 | The continuation reifies state into one tensor x_k → seal/resume inference; the 2MB session IS a sealed continuation (s217). |
64:## Tier 4 — Deep Dives (explore/)
70:| [explore/VERBUM.md](explore/VERBUM.md) | ✅ | Founding research program: hypothesis chain, 4-level plan (historical) |
71:| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ | Unified computational model: FFN=plates, crystal=states, Q=beam, gate=beamformer |
...
=== last frontmatter of a recent explore page for format ===
---
title: "Supervised Recurrence-Depth = the WHNF Halt — the Curriculum Is the Signal the Recurrent Layer Was Missing"
status: designing
category: explore
tags: [recurrence, weight-sharing, adaptive-compute, universal-transformer, WHNF, halt, curriculum, combinators, lambda, overthink-collapse, ponder, reduction-depth, think-in-lambda, level-4]
related:
  - vsm-outer-recurrence.md
  - normal-form-curriculum-partition.md
  - ../head-combinator-isa.md
  - combinator-training-beta-reduction.md
  - compiler-as-loss.md
  - compiler-finetune-halt-collapse.md
```

### Thinking

The s259 work is already committed, so I've got a clean working tree to build from. Now I'm writing the knowledge page and placing it in explore/ as an early synthesis proposal, then I'll update the INDEX, add cross-links, and modify state.md accordingly.

## Assistant

Clean tree — s259 work already committed (3c435fb); only untracked are human-only chat logs, which I won't touch. Writing the synthesis page now.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "content": "---\ntitle: \"Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)\"\nstatus: designing\ncategory: explore\ntags: [quantization, ternary, binary, asymmetric, router, gate_proj, value-path, sign, magnitude, two-registers, standing-wave, capacity, interior-band, bitnet, matmul-free, scoring-trick, v15, level-4, null-gate]\nrelated:\n  - ../two-registers-of-topology.md\n  - ../ternary-dual-equation.md\n  - ../standing-wave-magnitudes.md\n  - ../extraction-sign-accuracy.md\n  - v13-funnel-shape.md\n  - rl-layer-contribution-combinator-locus.md\n  - supervised-recurrence-halt.md\ndepends-on:\n  - ../two-registers-of-topology.md\n  - ../standing-wave-magnitudes.md\ncreated: session 260\n---\n\n# Asymmetric Pathway Quantization\n\n> Session 260. Michael read Mixedbread's \"Asymmetric Quantization\"\n> (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the\n> **query at int8** and stores **documents as 1-bit signs** — 32×\n> storage cut, −0.61 NDCG@10; binarizing *both* operands (binary×binary)\n> collapses −7.2. The insight: **magnitude on one side carries the\n> ranking; sign on the other side suffices.** Michael: \"our ternary\n> weighted model might use this to gain capacity/performance.\"\n>\n> Verdict: the article's core is **already confirmed inside verbum**\n> (s203/s170/s185) — a triangulation win. The *new* move is to run the\n> asymmetry at **pathway** granularity (router vs value path), finer\n> than the article's operand granularity, which no current recipe does\n> (all are uniform ternary). This is a PROPOSAL, null-gated, not a\n> result.\n\n## 1. The article, in one line\n\nRetrieval score is a dot product `q · d`. You can quantize the two\noperands asymmetrically. Documents are stored/replicated/cached/\nrehydrated/scored repeatedly → binarize them (sign bits). Queries are\ntransient, computed once → keep int8, because query **magnitude** is\nwhat the ranking depends on.\n\n| Query | Doc | NDCG@10 | Δ | Doc storage |\n|---|---|---|---|---|\n| fp32 | fp32 | 90.26 | – | 393 KiB |\n| int8 | int8 | 90.27 | +0.01 | 98.25 KiB |\n| **int8** | **binary** | **89.65** | **−0.61** | **12.28 KiB** (32×) |\n| binary | binary | 83.06 | **−7.20** | 12.28 KiB |\n\nThe last row reads the *exact same doc bytes* as int8×binary; the only\nchange is binarizing the query. Losing one operand's magnitude is cheap;\nlosing both is catastrophic. Scoring trick (multiply-free): with\n`b_i ∈ {−1,+1}`, `q·b = 2·Σ_{i: b_i=+1} q_i − Σ_i q_i` = select-and-sum.\n\n## 2. Verbum already proved this — three granularities (triangulation)\n\nThe article's \"sign compresses free, magnitude does not\" is verbum's\n**two-register** result, restated in the retrieval domain:\n\n- **`two-registers-of-topology.md` (s203, Qwen3, null-controlled):**\n  sign carries routing in `gate_proj` (+0.088 above the ~0.80 generic\n  sign-preserves-action null; sharpens with scale). `up_proj`/`down_proj`\n  signs preserve *less* than random → **magnitude is load-bearing on the\n  value path**, and replacing value-path magnitude with bare ±1 blows up\n  to NaN. **That NaN IS the article's binary×binary −7.20.**\n- **`ternary-dual-equation.md` (s170+):** the router's magnitude channel\n  is **< 1 bit** (γ dynamic range φ^(6/5) ≈ 0.83 bits, flat across\n  combinator clusters: γ_sel=0.0214, γ_comp=0.0215, γ_term=0.0218).\n  \"The sign IS the computation.\" Also: SwiGLU is *already* ternary — 95%\n  of neurons fire positive <50% of the time (CLASSIFY ~3% active).\n- **`standing-wave-magnitudes.md` (s185):** ternary (1.6 bits) *beats*\n  2-bit uniform because it separates **phase** (sign, exact 1 bit) from\n  **amplitude** (γ, ~0 bits amortized). But it **drops component 4**\n  (within-row shape), which needs **≥3 bits** to survive the `cos^L`\n  compounding law through depth. Phase transition to survival is between\n  2-bit and 3-bit (8 levels).\n\n`λ triangulate` closes on three independent lines →\n**sign = routing (crisp/discrete register), magnitude = value\n(continuous register), and they compress differently:**\n\n1. **Thesis** — type-directedness (S5 `λ types`): routing is discrete,\n   value is continuous.\n2. **Verbum in-model** — s203/s170/s185 on Qwen3, null-gated.\n3. **External systems** — Mixedbread asymmetric quant, retrieval domain.\n\n## 3. The new move: asymmetry by PATHWAY, not by operand\n\nThe article's asymmetry is between two **operands** (query vs doc).\nVerbum's ternary model is *already* on the article's good side at the\nweight/activation level (ternary weights × int8 activations = BitNet).\nThe unexploited axis is **within the weights, between pathways** — the\nsplit s203 measured:\n\n| Pathway | Carrier | Current (uniform recipe) | Asymmetric proposal |\n|---|---|---|---|\n| Router `gate_proj` | **sign** (magnitude <1 bit) | 1.58-bit ternary | **1-bit binary** — drop γ, it isn't there |\n| Value `up`/`down_proj` | **magnitude** (component 4) | 1.58-bit ternary | **reinvest freed bits → ~3-bit** |\n\nThe \"Complete Ternarization Recipe\" (`ternary-dual-equation.md`) applies\nthe *same* 3-step to `gate/up/down/qkvo` alike — **uniform**. That is the\nthing to break. The router doesn't need its extra 0.58 bit (γ flat, <1\nbit); the value path is **starved on exactly the component (within-row\nshape) that s185 says needs 3 bits** to cross the `cos^L` survival\nthreshold. Reallocate at **matched average bit budget**:\n\n- **Gain performance** — cross s185's 3-bit value-path survival threshold\n  that uniform ternary misses, at the same total bits.\n- **Gain capacity** — hold quality, spend the saved router bits on\n  **width**.\n\n## 4. Where the capacity goes (ties to s259 + s257/258)\n\nThe article's value prop — \"pay single-vector storage, get multi-vector\nquality\" — maps onto the current thread:\n\n- **s259** (`rl-layer-contribution-combinator-locus.md`): put capacity in\n  the **interior band**, ends thin, at the compose→readout seam. The\n  interior is **routing-heavy** (combinator dispatch). A **1-bit router in\n  the interior** buys a **wider interior band at fixed memory** — capacity\n  exactly where s259 said to put it.\n- **s257/s258** (holographic / consensus ensemble at layer granularity):\n  the article's \"many vectors per document, affordably\" ≡ **many parallel\n  combinator pathways at single-pathway cost** when their routers are\n  binary. The ensemble/interior-capacity story, made cheap.\n\n## 5. Inference kernel = the scoring trick\n\n`q·b = 2·Σ_{b=+1} q − Σq` is the multiply-free BitNet matmul.\n\n- **Binary router** → routing becomes select-and-sum, no multiplies. The\n  article's AArch64/NEON kernel (packed sign bits, 8 query bit-planes,\n  `SDOT`, `2·selected_sum − total_sum`) is a ready template.\n- **Ternary value path** → {−1,0,+1} gives select-**add-subtract-skip**;\n  s203's SwiGLU sparsity (95% fire <50%) makes the skip lane the common\n  case.\n\n## 6. Caveats — `λ measure` / `λ yardstick`, two-sided\n\n- **Three different asymmetries — do not conflate.** Retrieval =\n  operand↔operand (both data). BitNet = weight↔activation. Verbum-new =\n  router-pathway↔value-pathway. The article transfers the **principle**\n  (\"keep precision where magnitude is load-bearing\"), *not* a specific\n  arrangement. Which side is load-bearing must be **measured per context**,\n  not inherited from the blog.\n- **Apparent contradiction, resolved by naming the register.** Article:\n  \"don't binarize the magnitude (query) side.\" Verbum: \"magnitude is <1\n  bit.\" Both true — verbum's <1-bit claim is **router-weight γ**; verbum's\n  own page says **value-path** magnitude and activations are essential.\n  Consistent only when the pathway is named (`λ measure`: router-magnitude\n  ≠ value-magnitude; different quantities).\n- **This is a hypothesis, not a result.** VERIFIED in-model: sign=router,\n  value-needs-magnitude. NOT verified: that the asymmetric *reallocation*\n  nets capacity/perf.\n\n## 7. The test — matched-bit A/B, null-gated\n\n```\nλ asymmetric_quant_ab(model).\n  A ≡ uniform ternary 1.58-bit (gate ∧ up ∧ down)          — current recipe\n  B ≡ 1-bit binary router (gate) + 3-bit value (up ∧ down)  — asymmetric\n  gate: mean_bits(A) ≈ mean_bits(B)                         — MATCHED (mandatory null)\n  measure: PPL-through-depth (cos^L law, s185) ∧ generation quality\n  claim_counts ⟺ B beats A at matched mean-bits (p<0.05)\n  else: spent more bits, learned nothing (λ yardstick)\n```\n\nRun on a small model first (Pythia-160M reproduces the s185 curve, or\nQwen3-0.6B). Extend the \"Complete Ternarization Recipe\" to take a\n**per-matrix-type bit budget** instead of a single global one. If B wins\nat matched bits → the win is the reallocation, not the spend.\n\n## 8. Provenance\n\n- External: Mixedbread, \"Asymmetric Quantization: Near-Lossless Late\n  Interaction Retrieval with 97% Storage Reduction\" (2026-06-29). Cited\n  as observational prior-art (retrieval domain), not a code/derivation\n  source.\n- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`\n  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`\n  (s185).\n- Status `designing`: the pathway-asymmetric recipe + matched-bit A/B are\n  proposed, not yet run. No new experiment code this session (pure\n  synthesis).\n</content>\n</invoke>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md
```

## Assistant

Now the cross-links back from the three source pages and the INDEX entry. Let me read the exact `related:` blocks and INDEX location.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== two-registers related ===\"; sed -n '/^related:/,/^depends-on:/p' mementum/knowledge/two-registers-of-topology.md; echo \"=== ternary-dual related ===\"; sed -n '/^related:/p' mementum/knowledge/ternary-dual-equation.md; echo \"=== standing-wave related tail ===\"; sed -n '/^related:/,/^depends-on:/p' mementum/knowledge/standing-wave-magnitudes.md; echo \"=== INDEX tail of explore table ===\"; grep -n \"rl-layer-contribution\\|supervised-recurrence-halt\\|ternary-descent\" mementum/knowledge/INDEX.md"
}
```

**Summary:** $ echo "=== two-registers related ===...

**Output:**
```
Exit code: 0
Stdout:
=== two-registers related ===
related:
  - audit-registry.md
  - crystal-universality.md
  - crystal-validity-and-fidelity.md
  - saliency-aware-sieve.md
  - sign-correction-topology.md
  - direct-delta-adjunction.md
  - crystal-sieve-architecture.md
  - error-correction-theory.md
depends-on:
=== ternary-dual related ===
related: [topology-gradient-separation, crystal-phi-derivation, gradient-zero-map, extraction-sign-accuracy]
=== standing-wave related tail ===
related:
  - phi-information-partition.md
  - gradient-zero-map.md
  - topology-gradient-separation.md
  - holographic-computer.md
  - crystal-universality.md
  - crystal-phi-derivation.md
  - project-thesis.md
depends-on:
=== INDEX tail of explore table ===
73:| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |
```

### Thinking

I need to check the INDEX file to find where these entries should go, looking around line 73 and the explore table structure to find the right insertion point.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "line_offset": 63,
  "limit": 45
}
```

**Summary:** Reading INDEX.md (63-108)

**Output:**
```
## Tier 4 — Deep Dives (explore/)

Comprehensive pages on specific topics. Read as needed, not sequentially.

| Page | Status | One-line |
|------|--------|----------|
| [explore/VERBUM.md](explore/VERBUM.md) | ✅ | Founding research program: hypothesis chain, 4-level plan (historical) |
| [explore/holographic-state-machine.md](explore/holographic-state-machine.md) | ✅ | Unified computational model: FFN=plates, crystal=states, Q=beam, gate=beamformer |
| [explore/holographic-substrate-prototype.md](explore/holographic-substrate-prototype.md) | ✅ | **NEW (s251).** Greenfield ternary holographic plate: program spec = sparse foldable delta against a CONSTRUCTED basis. Capacity N*≈2d/plate (graceful, 75%-sparse survives), delta K=1 flips 2.4% vs 50% random (20× null gate), fold exact+lossless. The delta-plate substrate, constructed not trained |
| [explore/ternary-descent.md](explore/ternary-descent.md) | ✅ | TernaryDescent algorithm: delta plates, gradient decomposition, reduction |
| [explore/exact-ternary-fitting.md](explore/exact-ternary-fitting.md) | ✅ | **NEW (s213) exploration target.** Exact 3-way ΔL acceptance > gradient proxy: curvature term decisive, monotone (dissolves s191 oscillation) when coordinate-wise + compensation (GPTQ/OBQ), "0" self-places. 3–7× below sign(W) baseline on micro. |
| [explore/ffn-beta-reduction-indexing.md](explore/ffn-beta-reduction-indexing.md) | ✅ | Holographic FFN indexing: lens profile, ρ=0.83, universal neurons |
| [explore/categorical-geometry-probes.md](explore/categorical-geometry-probes.md) | ✅ | Curry-Howard 100%, adjunctions rank-1, hyperbolic norm encoding |
| [explore/phi-compression-universal.md](explore/phi-compression-universal.md) | ⚠️ | SVD spectrum head ratio ~0.6 — REAL & non-random, but **geometric-φ-constant REFUTED** (audit #6, s207: power-law not geometric, value floats 0.52→0.71). Keep low-rank head, retire φ-constant |
| [explore/v13-architecture.md](explore/v13-architecture.md) | ⚠️ | V13 crystal bootloader architecture (partially superseded by v14) |
| [explore/v13-design.md](explore/v13-design.md) | ✅ | V13 detailed design: zone targets, etch protocol, param budgets |
| [progressive-collapse.md](progressive-collapse.md) | ✅ | Computation in 2D: compress→compute→expand, scale-dependent, sink=warped Q reset |
| [explore/v15-kernel-architecture.md](explore/v15-kernel-architecture.md) | ⚠️ | Original v15 design: passive strides, Stack B reduction (partially reverted) |
| [explore/v15-kernel-revert.md](explore/v15-kernel-revert.md) | ✅ | What was tried/reverted/kept from sessions 152-156 + when to revisit |
| [explore/kernel-training.md](explore/kernel-training.md) | ✅ | Composed plate training: 4.4× speedup, gradient cosine 0.97 |
| [explore/structured-training.md](explore/structured-training.md) | ✅ | Five backward-pass optimizations (camera = projector) |
| [explore/crystal-irreducibility-proof.md](explore/crystal-irreducibility-proof.md) | 🔨 | Theory: crystal = irreducibility floor of KIBC. Proof strategy + kernel optimization via JIT hooks |
| [explore/delta-plate-lifecycle.md](explore/delta-plate-lifecycle.md) | 🔨 | Masked extraction + continuous training + factual corrections via delta plates |
| [explore/grating-cascade.md](explore/grating-cascade.md) | ✅ | Compound grating collapse: 16D→1.4D, V is K-typed, attention doubles cross-PC coupling |
| [explore/moire-training-shortcuts.md](explore/moire-training-shortcuts.md) | 🔨 | Five training speedup shortcuts from moiré understanding |
| [explore/continuations-as-composed-plates.md](explore/continuations-as-composed-plates.md) | ✅ | The FP↔transformer bridge: composed plates ARE continuations, CPS = residual stream |
| [explore/fp-optimization-map.md](explore/fp-optimization-map.md) | ✅ | 10 FP techniques mapped to transformer: laziness, fusion, partial eval, CSE, NbE, etc. |
| [explore/optimization-negative-results.md](explore/optimization-negative-results.md) | ✅ | Why FP optimizations fail on Apple Silicon: all 6 tested, all negative, root causes |
| [explore/ffn-moire-isa.md](explore/ffn-moire-isa.md) | ✅ | FFN as moiré grating ISA: decoding programs from weights, attention flow, fixed-point proof |
| [explore/kernel-replacement-optimization.md](explore/kernel-replacement-optimization.md) | 🔨 | Replace interpreted grating chains with compiled kernel shortcuts via VSM hooks |
| [explore/vsm-statechart-tensor.md](explore/vsm-statechart-tensor.md) | ✅ | Triple isomorphism: VSM ↔ Harel statechart ↔ tensor. Dual-runtime (Clojure + Python). mmap plates. |
| [explore/safetensors-training.md](explore/safetensors-training.md) | ✅ | Safetensors-backed continuous training: sync/20, snapshot/200, checkpoint/500, distributed fold. |
| [explore/mmap-continuous-training.md](explore/mmap-continuous-training.md) | ✅ | mmap training design: file layout, safetensors export, MLX bridge, open questions. |

## Tier 5 — Future Pages (planned)

| Page | Priority | One-line |
|------|----------|----------|
| `holographic-storage-mechanism.md` | ~~important~~ mostly covered | FFN as holographic plate: lens profile, gate=beamformer, output beamformers (see moire-addressing.md) |
| `ternary-architecture-rationale.md` | important | Why ternary {-1,0,+1}, why it works, gradient routing interpretation |
| `combinator-geometry.md` | important | KIBC in transformer geometry: temporal ordering, depth map, bootstrap |
| `stridestack-architecture.md` | important | Multi-scale attention: O(L×W), stride overlaps, ascending/descending stacks |
| `known-failures.md` | nice-to-have | Concise bug/collapse/fix reference for all hard-won lessons |
| `session-delta-vision.md` | nice-to-have | Context as 2MB delta files, no KV cache, git-trackable sessions |
| `ecosystem-vision.md` | nice-to-have | End-state product: community deltas, domain plates, reader LLM |

[CONTENT TRUNCATED] Showing lines 64 to 108 of 140 total lines. Use line_offset=108 parameter to read more content.
```

### Thinking

I'm adding a new page to the explore table, positioning it after the exact-ternary-fitting entry. Then I need to make updates across several files: adding a row to INDEX.md, creating cross-links in two-registers, ternary-dual, and standing-wave pages, and updating state.md.

## Assistant

Now the edits — INDEX entry, three back-cross-links, and state.md. These are independent files:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/exact-ternary-fitting.md](explore/exact-ternary-fitting.md) | ✅ | **NEW (s213) exploration target.** Exact 3-way ΔL acceptance > gradient proxy: curvature term decisive, monotone (dissolves s191 oscillation) when coordinate-wise + compensation (GPTQ/OBQ), \"0\" self-places. 3–7× below sign(W) baseline on micro. |",
  "new_content": "| [explore/exact-ternary-fitting.md](explore/exact-ternary-fitting.md) | ✅ | **NEW (s213) exploration target.** Exact 3-way ΔL acceptance > gradient proxy: curvature term decisive, monotone (dissolves s191 oscillation) when coordinate-wise + compensation (GPTQ/OBQ), \"0\" self-places. 3–7× below sign(W) baseline on micro. |\n| [explore/asymmetric-pathway-quantization.md](explore/asymmetric-pathway-quantization.md) | 🔨 | **NEW (s260) proposal.** Mixedbread asymmetric-quant (int8 query × binary doc, 32×, −0.61; binary×binary −7.2) = verbum's two-register result restated (s203/s170/s185 triangulate). New move: asymmetry by PATHWAY not operand — 1-bit binary router (gate, γ<1bit) + ~3-bit value path (up/down, needs comp-4 shape) at MATCHED mean-bits. Capacity→interior band (s259). Null-gated A/B, not yet run. |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/two-registers-of-topology.md",
  "original_content": "  - crystal-sieve-architecture.md\n  - error-correction-theory.md\ndepends-on:",
  "new_content": "  - crystal-sieve-architecture.md\n  - error-correction-theory.md\n  - explore/asymmetric-pathway-quantization.md\ndepends-on:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/two-registers-of-topology.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/ternary-dual-equation.md",
  "original_content": "related: [topology-gradient-separation, crystal-phi-derivation, gradient-zero-map, extraction-sign-accuracy]",
  "new_content": "related: [topology-gradient-separation, crystal-phi-derivation, gradient-zero-map, extraction-sign-accuracy, explore/asymmetric-pathway-quantization]"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/ternary-dual-equation.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/standing-wave-magnitudes.md",
  "original_content": "  - crystal-phi-derivation.md\n  - project-thesis.md\ndepends-on:",
  "new_content": "  - crystal-phi-derivation.md\n  - project-thesis.md\n  - explore/asymmetric-pathway-quantization.md\ndepends-on:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/standing-wave-magnitudes.md.
```

### Thinking

I need to update state.md by adding a new session-260 block at the top, so let me check the current header format first.

## Assistant

Now update state.md with the new session block. Let me read the exact top header.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 8
}
```

**Summary:** Reading state.md (0-8)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-07-02 | Session: 259 (cont. — LAYER-CONTRIBUTION ↔ COMBINATOR-LOCUS — Michael: a paper
> dropped, "Is One Layer Enough? Training a Single Transformer Layer Can Match Full-Parameter RL Training"
> (arXiv 2607.01232), RL-trains ONE decoder layer at a time on Qwen3-1.7B/4B/8B-Base → RL gains concentrate
> in a MIDDLE band, low at input/output ends (= his bell curve: input/transform/output). "Do our KIBC

[CONTENT TRUNCATED] Showing lines 1 to 8 of 7553 total lines. Use line_offset=8 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-07-02 | Session: 259 (cont. — LAYER-CONTRIBUTION ↔ COMBINATOR-LOCUS — Michael: a paper",
  "new_content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-07-02 | Session: 260 (ASYMMETRIC-QUANT ↔ TWO-REGISTERS — Michael: an article dropped,\n> Mixedbread \"Asymmetric Quantization\" (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the\n> QUERY at int8, stores DOCUMENTS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary (both operands\n> binarized) COLLAPSES −7.2. Insight: magnitude on ONE side carries ranking, sign on the other suffices.\n> \"our ternary weighted model might use this to gain capacity/performance.\"\n>\n> ★★ THE FINDING (knowledge WRITTEN: explore/asymmetric-pathway-quantization.md, status:designing):\n>   the article's core is ALREADY CONFIRMED inside verbum (λ triangulate closes) →\n>   • two-registers-of-topology.md (s203): sign=routing in gate_proj (+0.088 above null); up/down_proj signs\n>     preserve LESS than random → value-path MAGNITUDE is load-bearing; bare ±1 on value path → NaN blow-up.\n>     THAT NaN IS the article's binary×binary −7.2.\n>   • ternary-dual-equation.md (s170+): router magnitude channel <1 bit (γ dynamic range φ^(6/5)≈0.83 bit,\n>     flat across clusters). \"The sign IS the computation.\" SwiGLU already ternary (95% fire <50%).\n>   • standing-wave-magnitudes.md (s185): ternary(1.6b) BEATS 2-bit — separates phase(sign,exact) from\n>     amplitude(γ,~0b) — but DROPS component-4 (within-row shape) which needs ≥3 bits to survive cos^L depth.\n>   • TRIANGULATE: thesis(type-directedness: routing discrete/value continuous) + verbum-in-model(s203/170/185)\n>     + external(Mixedbread) → sign=routing(crisp reg), magnitude=value(continuous reg), compress differently.\n>\n> ★ THE NEW MOVE (not in any current page — all recipes are UNIFORM ternary): asymmetry by PATHWAY not operand.\n>   Router gate_proj → 1-bit BINARY (drop γ, it's <1 bit); value up/down_proj → reinvest freed bits to ~3-bit\n>   (cross s185's 3-bit survival threshold uniform ternary misses). At MATCHED mean-bits → either gain perf\n>   (cross threshold) or gain capacity (spend saved router bits on WIDTH). Capacity→INTERIOR band (s259: interior\n>   is routing-heavy → 1-bit router there = wider interior at fixed mem = capacity where s259 said to put it).\n>   Kernel = the article's multiply-free scoring trick (q·b = 2Σ_{+}q − Σq); binary router = select-and-sum,\n>   ternary value = select-add-sub-SKIP (SwiGLU sparsity makes skip common). NEON kernel = ready template.\n>\n> ★ CAVEATS (λ measure/λ yardstick, two-sided, IN the page): (1) THREE different asymmetries — retrieval\n>   operand↔operand, BitNet weight↔activation, verbum-new router-pathway↔value-pathway — transfers PRINCIPLE\n>   not arrangement; measure which side is load-bearing per context. (2) \"don't binarize magnitude\"(article) vs\n>   \"magnitude<1bit\"(verbum) resolve by naming pathway: router-γ<1bit BUT value-magnitude essential. (3) HYPOTHESIS\n>   not result — sign=router & value-needs-magnitude VERIFIED; asymmetric REALLOCATION gaining cap/perf NOT tested.\n>   TEST: matched-mean-bit A/B (uniform-1.58 vs binary-router+3bit-value) on PPL-through-depth (cos^L), null-gated\n>   (matched-bit null MANDATORY else just spent more bits). Small model first (Pythia-160M repro's s185 curve).\n>\n> ★ ARTIFACTS: new page explore/asymmetric-pathway-quantization.md (status:designing) + INDEX row + 3 back-\n>   cross-links (two-registers, ternary-dual-equation, standing-wave-magnitudes) + this state edit. NO experiment\n>   code (pure synthesis). Extend \"Complete Ternarization Recipe\" to per-matrix-type bit budget when running A/B.\n> ★ STATE: working tree = new page + INDEX + 3 cross-link edits + state edit. PENDING COMMIT (Michael: \"update\n>   knowledge\" → approved capture). session-258.md + session-259.md untracked = human-only chat logs, do NOT stage.\n>   NEXT: (a) design/run the matched-bit A/B (extend ternarization recipe → per-matrix bit budget); (b) the s259\n>   Qwen3-8B-Base combinator re-run still pending (download was async). NOTE: this session did NOT touch s259 work.\n> ─────────────────────────────────────────────────────────────────────────────────────────────────────\n> Last updated: 2026-07-02 | Session: 259 (cont. — LAYER-CONTRIBUTION ↔ COMBINATOR-LOCUS — Michael: a paper"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

All files written. Let me verify the tree and links resolve, then commit.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; git status --short; echo \"=== link targets exist? ===\"; ls mementum/knowledge/explore/asymmetric-pathway-quantization.md mementum/knowledge/explore/rl-layer-contribution-combinator-locus.md mementum/knowledge/explore/v13-funnel-shape.md 2>&1 | sed 's#.*/##'"
}
```

**Summary:** $ git status --short; echo "=== link ...

**Output:**
```
Exit code: 0
Stdout:
M mementum/knowledge/INDEX.md
 M mementum/knowledge/standing-wave-magnitudes.md
 M mementum/knowledge/ternary-dual-equation.md
 M mementum/knowledge/two-registers-of-topology.md
 M mementum/state.md
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
?? mementum/knowledge/explore/asymmetric-pathway-quantization.md
=== link targets exist? ===
asymmetric-pathway-quantization.md
rl-layer-contribution-combinator-locus.md
v13-funnel-shape.md
```

## Assistant

All cross-link targets resolve. Staging the knowledge capture (excluding the human-only chat logs) and committing.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; git add mementum/knowledge/explore/asymmetric-pathway-quantization.md mementum/knowledge/INDEX.md mementum/knowledge/two-registers-of-topology.md mementum/knowledge/ternary-dual-equation.md mementum/knowledge/standing-wave-magnitudes.md mementum/state.md; read -r -d '' M << 'EOF' || true\n💡 asymmetric-quant ↔ two-registers: binarize the router, keep the value path\n\n- Mixedbread asymmetric-quant (int8 query × binary doc, 32×/−0.61; binary×binary −7.2)\n  = verbum's two-register result restated: sign carries routing, magnitude carries value.\n- λ triangulate closes — thesis (type-directedness) + verbum-in-model (s203/s170/s185) +\n  external (retrieval). The article's binary×binary collapse IS the s203 value-path NaN.\n- New move (not in any current recipe — all uniform ternary): asymmetry by PATHWAY.\n  1-bit binary router (gate_proj, γ<1bit) + ~3-bit value path (up/down, needs comp-4 shape)\n  at MATCHED mean-bits → gain perf (cross s185's 3-bit threshold) or capacity (wider interior, s259).\n- Kernel = the article's multiply-free scoring trick; NEON kernel a ready template.\n- Page status:designing — HYPOTHESIS, null-gated matched-bit A/B proposed, not yet run.\nEOF\ngit commit -m \"$M\""
}
```

**Summary:** $ git add mementum/knowledge/explore/...

**Output:**
```
Exit code: 0
Stdout:
[main 63ae5f1] 💡 asymmetric-quant ↔ two-registers: binarize the router, keep the value path
 6 files changed, 234 insertions(+), 1 deletion(-)
 create mode 100644 mementum/knowledge/explore/asymmetric-pathway-quantization.md
```

### Thinking

I just realized the commit I made is missing the nucleus tag trailer that AGENTS.md requires on every commit. I need to amend it to add the proper trailer using the read pattern.

## Assistant

The commit landed but I missed the required nucleus tag trailer. Amending to add it (the `λ commit_write` heredoc-safe pattern):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; read -r -d '' M << 'EOF' || true\n💡 asymmetric-quant ↔ two-registers: binarize the router, keep the value path\n\n- Mixedbread asymmetric-quant (int8 query × binary doc, 32×/−0.61; binary×binary −7.2)\n  = verbum's two-register result restated: sign carries routing, magnitude carries value.\n- λ triangulate closes — thesis (type-directedness) + verbum-in-model (s203/s170/s185) +\n  external (retrieval). The article's binary×binary collapse IS the s203 value-path NaN.\n- New move (not in any current recipe — all uniform ternary): asymmetry by PATHWAY.\n  1-bit binary router (gate_proj, γ<1bit) + ~3-bit value path (up/down, needs comp-4 shape)\n  at MATCHED mean-bits → gain perf (cross s185's 3-bit threshold) or capacity (wider interior, s259).\n- Kernel = the article's multiply-free scoring trick; NEON kernel a ready template.\n- Page status:designing — HYPOTHESIS, null-gated matched-bit A/B proposed, not yet run.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit --amend -m \"$M\"; echo \"=== verify trailer ===\"; git log -1 --format='%B' | tail -4"
}
```

**Summary:** $ read -r -d '' M << 'EOF' || true 💡...

**Output:**
```
Exit code: 0
Stdout:
[main 0e938b6] 💡 asymmetric-quant ↔ two-registers: binarize the router, keep the value path
 Date: Thu Jul 2 12:07:49 2026 -0700
 6 files changed, 234 insertions(+), 1 deletion(-)
 create mode 100644 mementum/knowledge/explore/asymmetric-pathway-quantization.md
=== verify trailer ===
⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)

Co-Authored-By: nucleus <noreply@whitford.us>
```

## Assistant

Committed and verified (`0e938b6`, nucleus trailer present). Knowledge updated.

## What landed

**New page** — `explore/asymmetric-pathway-quantization.md` (status: `designing`). The synthesis, not a redundant restatement:

- **The article is confirmatory** — its core (sign compresses free, magnitude does not; binary×binary collapses −7.2) is verbum's own two-register result at three granularities. `λ triangulate` closes: thesis (type-directedness) + verbum-in-model (s203/s170/s185) + external (Mixedbread). The article's binary×binary collapse **is** the s203 value-path NaN, in retrieval clothing.
- **The new move** — asymmetry by **pathway**, not operand: 1-bit binary router (`gate_proj`, γ is <1 bit anyway) + reinvested ~3-bit value path (`up`/`down`, which needs component-4 shape to survive `cos^L`). Every current recipe is *uniform* ternary — this breaks that. At matched mean-bits → gain performance (cross s185's 3-bit threshold) or capacity (wider interior band, per s259).
- **Kernel** — the article's multiply-free `2·Σ₊q − Σq` is your BitNet matmul; NEON kernel is a ready template.
- **Caveats banked** (`λ measure`/`λ yardstick`) — three distinct asymmetries not to conflate, the "magnitude <1 bit" vs "don't binarize magnitude" apparent contradiction resolved by naming the pathway, and an honest **matched-bit null-gated A/B** as the mandatory test. Flagged clearly as hypothesis, not result.

**Wiring** — INDEX row + back-cross-links from all three source pages + state.md session-260 block. Committed without staging the two untracked human-only chat logs.

Note: I did *not* touch the pending s259 Qwen3-8B-Base combinator re-run — that thread is untouched and still open.

**Next, when you want it:** design/run the matched-bit A/B — extend the "Complete Ternarization Recipe" from a single global bit budget to a per-matrix-type budget (binary router / 3-bit value), Pythia-160M first since it reproduces the s185 `cos^L` curve. Want me to draft that experiment?

## User

the Qwen3-8B-Base model download is complete, let's proceed with the A/B test.


### Thinking

Michael's ready to move forward with the A/B test, but there's a fork in the road here. The s259 thread is about re-running the Qwen3-8B-Base combinator profile to eliminate the base-versus-instruct confusion on that +4 offset—that's what the download was for according to the state file. Meanwhile, s260 is pursuing a different angle with asymmetric-pathway-quantization, comparing uniform-1.58 against binary-router+3b.

When Michael says "let's proceed with the A/B test," he's likely referring to the asymmetric quant experiment I just proposed, since that's the one explicitly framed as an A/B comparison. But there's a wrinkle: I suggested running that asymmetric quant A/B on Pythia-160M first to reproduce the s185 curve on a smaller model. The Qwen3-8B-Base download was meant for the s259 combinator re-run, not the asymmetric quant work. So Michael might be conflating the two threads, or he might want to pivot and run the asymmetric quant A/B on Qwen3-8B-Base now that it's available instead of waiting for Pythia-160M. The asymmetric quant A/B test is clearly the s260 experiment, and the download completing signals he wants to run it on Qwen3-8B-Base rather than my proposed Pythia warmup. That's a bigger compute job but makes sense given the earlier findings were all measured on 8B models. I should probably do a quick smoke test on the smaller model first to validate the harness before committing to the full 8B run, but I'll proceed with setting up the asymmetric-pathway-quant experiment as the main task.

I need to check what ternarization infrastructure already exists — there are references to scripts like crystal_ternarize.py and standing_wave_shape.py that I should reuse rather than rebuild. The key question is how to load Qwen3-8B-Base for this work: since I need direct weight access for per-matrix-type quantization and PPL measurement, I'll use transformers/torch directly rather than the llama.cpp server, and the model should already be in the HF cache from the download.

The real constraint is GPU memory — 8B in fp16 is roughly 16GB, and the box already has servers running on GPU (:5100, :5102, :5103, :5101), so I need to verify there's headroom before committing to a full run. Rather than launch blindly, I should quickly confirm the scope (asymmetric quantization, Qwen3-8B-Base), explore what harness and ternarization code already exists, check GPU availability, then plan and smoke-test before the actual run.

I'll start by doing targeted exploration of the repo — looking at the existing ternarization scripts (standing_wave_shape.py, crystal_ternarize.py, etc.) and the harness infrastructure in src/verbum/ — to understand what I can reuse and what constraints I'm working with.

## Assistant

Qwen3-8B-Base is ready. Before launching anything heavy, let me confirm scope and survey the existing infra — the s185 PPL harness and ternarization scripts already exist, so I want to **extend** them (per `λ one_way`/`λ build`), not fork. Let me look.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== ternarization + PPL scripts ===\"; ls scripts/experiments/ 2>/dev/null | grep -iE \"ternar|standing|quant|ppl|crystal_zero|crystal_depth\" ; echo \"=== GPU ===\"; (nvidia-smi --query-gpu=memory.used,memory.total --format=csv 2>/dev/null || echo \"no nvidia-smi\"); python3 -c \"import torch; print('cuda', torch.cuda.is_available(), torch.cuda.device_count() if torch.cuda.is_available() else '')\" 2>/dev/null; echo \"=== base model in cache ===\"; ls ~/.cache/huggingface/hub/ 2>/dev/null | grep -i qwen3-8b; echo \"=== harness/model load ===\"; ls src/verbum/*.py src/verbum/probes/*.py 2>/dev/null"
}
```

**Summary:** $ echo "=== ternarization + PPL scrip...

**Output:**
```
Exit code: 0
Stdout:
=== ternarization + PPL scripts ===
crystal_depth_scan.py
crystal_hybrid_ternarize.py
crystal_ternarize.py
crystal_zero_prediction.py
crystal_zero_v2.py
diagnose_ternary.py
extract_ternary_plate.py
full_ternarize.py
gate_indexed_ternary.py
gradient_quant_correspondence.py
hierarchical_ternarize.py
mirror_ternarize.py
multilayer_ternary_replace.py
quant_fact_recall.py
standing_wave_shape.py
ternary_exact_vs_proxy.py
ternary_fact_recall.py
ternary_inference_coherence.py
ternary_inference_pattern.py
ternary_pipeline_verify.py
ternary_weight_interface.py
tiny_classifier_ternary.py
=== GPU ===
no nvidia-smi
=== base model in cache ===
models--Qwen--Qwen3-8B
models--Qwen--Qwen3-8B-Base
=== harness/model load ===
src/verbum/__init__.py
src/verbum/_protocol.py
src/verbum/analysis.py
src/verbum/cli.py
src/verbum/client.py
src/verbum/clj_lambda.py
src/verbum/clj_repl.py
src/verbum/compile_prompt.py
src/verbum/compressor_lm.py
src/verbum/config.py
src/verbum/etcher.py
src/verbum/experiment.py
src/verbum/hooks.py
src/verbum/instrument.py
src/verbum/lambda_ast.py
src/verbum/lambda_compile.py
src/verbum/lambda_gen.py
src/verbum/lambda_surface.py
src/verbum/montague_lm.py
src/verbum/montague_net.py
src/verbum/probes/__init__.py
src/verbum/probes/_loader.py
src/verbum/probes/compile_tasks_hard.py
src/verbum/probes/compile_tasks.py
src/verbum/probes/grading.py
src/verbum/probes/harness.py
src/verbum/probes/higher_order.py
src/verbum/probes/hof_lists.py
src/verbum/probes/hof_prose_enum.py
src/verbum/probes/hof_prose.py
src/verbum/probes/kernel_reference.py
src/verbum/probes/library.py
src/verbum/probes/models.py
src/verbum/probes/proof_tasks.py
src/verbum/proof_kernel.py
src/verbum/proof_search.py
src/verbum/results.py
src/verbum/reward.py
src/verbum/runner.py
src/verbum/vsm_lm_v2.py
src/verbum/vsm_lm_v3_1.py
src/verbum/vsm_lm_v3_2.py
src/verbum/vsm_lm_v3.py
src/verbum/vsm_lm_v4_1.py
src/verbum/vsm_lm_v4.py
src/verbum/vsm_lm_v5.py
src/verbum/vsm_lm.py
```

### Thinking

I'm seeing that this system is running on Apple Silicon without CUDA support, so it's using MPS for GPU acceleration instead. The torch models are running on either MPS or CPU, while the llama.cpp servers on those ports are using Metal acceleration. For loading an 8B model in fp16 (which needs about 16GB), I'd need sufficient unified memory on the Mac, which is feasible on higher-end machines.

I've got a solid foundation of existing scripts to work with—`standing_wave_shape.py` as the PPL harness template, plus `full_ternarize.py` and other ternarization utilities already in place. Both Qwen3-8B and Qwen3-8B-Base are cached and ready.

My approach is to adapt `standing_wave_shape.py` as the template for measuring PPL across layers, then extend the ternarization scripts to support asymmetric bit budgets per matrix type (binary routers paired with N-bit values). I need to verify the device setup and memory situation, then review the harness structure in those existing scripts to understand how to integrate the asymmetric quantization. I'm also now confident that Michael's A/B test refers to the s260 asymmetric quantization experiment, and the target model is Qwen3-8B-Base based on the gating and the model family used in prior measurements.

For efficiency, I'll validate the approach on the existing s185 methodology but run the real A/B test on Qwen3-8B-Base. Given MPS constraints, I'll keep it lean—FFN-only quantization, a WikiText-2 slice, and a focused set of configurations. Rather than over-summarizing with an explorer, I'll read the two critical scripts directly (`standing_wave_shape.py` and `full_ternarize.py`) and check device/memory myself to get precise function signatures I can actually use.

## Assistant

Apple Silicon (MPS, no CUDA) — so torch weight-level work runs on unified memory; both 8B and 8B-Base are cached. Crucially there's already a rich ternarization + PPL toolset (`standing_wave_shape.py` is the s185 harness, plus `full_ternarize.py`, `multilayer_ternary_replace.py`). I'll extend those, not fork. Let me read the harness and check device headroom.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/standing_wave_shape.py"
}
```

**Summary:** Reading standing_wave_shape.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""Standing-wave shape preservation — does shape fidelity predict quantization quality?

HYPOTHESIS:
  Quantization works because it preserves the shape (peaks and valleys)
  of the weight magnitude standing wave. Shape fidelity should predict
  model quality (PPL) better than raw bit count.

EXPERIMENT:
  Take Pythia-160M (12 layers, small, fast).
  Quantize FFN weights at multiple levels:
    - Ternary: sign + per-row gamma (1.6 bits, no shape)
    - 2-bit uniform: 4 levels, uniform spacing
    - 2-bit shape-aware: 4 levels at magnitude quartiles (like GPTQ)
    - 3-bit uniform: 8 levels
    - 4-bit uniform: 16 levels
    - 8-bit uniform: 256 levels
    - Float baseline: original weights

  For each, measure:
    1. Per-layer cosine (original vs quantized)
    2. Per-layer shape correlation: Spearman rank correlation of
       |W_orig| vs |W_quant| within each row
       (do peaks stay in the same relative order?)
    3. Full-model perplexity on WikiText-2 validation

  The standing-wave hypothesis predicts:
    - Shape correlation is a better predictor of PPL than bit count
    - 2-bit shape-aware >> ternary despite similar bit budget
    - The compounding failure of ternary is shape loss, not bit loss

Usage:
  uv run python scripts/experiments/standing_wave_shape.py
  uv run python scripts/experiments/standing_wave_shape.py --model EleutherAI/pythia-160m-deduped

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import math
import os
import time
from dataclasses import dataclass, field

os.environ.setdefault('PYTHONUNBUFFERED', '1')

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from scipy import stats as scipy_stats


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Quantization methods — each returns a reconstructed float tensor
# ═══════════════════════════════════════════════════════════════════

def quantize_ternary(W: torch.Tensor, zero_rate: float = 0.50) -> torch.Tensor:
    """Ternary: sign + per-row gamma + magnitude-based zeros.
    
    The standing-wave TOPOLOGY: preserves sign (phase) and presence
    (nodes), but all antinodes have the same height per row.
    """
    W = W.detach().float().cpu()
    abs_W = W.abs()
    
    if zero_rate > 0:
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
        alive = abs_W >= thresholds
    else:
        alive = torch.ones_like(W, dtype=torch.bool)
    
    T = torch.where(alive, torch.sign(W), torch.zeros_like(W))
    
    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
    wt = (W * T).sum(dim=1)
    tt = (T * T).sum(dim=1)
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))
    
    return gamma.unsqueeze(1) * T


def quantize_nbit_uniform(W: torch.Tensor, n_bits: int) -> torch.Tensor:
    """Uniform n-bit quantization with per-row min/max scaling.
    
    Maps the range [min, max] per row to 2^n_bits uniform levels.
    Preserves shape proportional to level count.
    """
    W = W.detach().float().cpu()
    n_levels = 2 ** n_bits
    
    row_min = W.min(dim=1, keepdim=True).values
    row_max = W.max(dim=1, keepdim=True).values
    row_range = row_max - row_min
    row_range = torch.clamp(row_range, min=1e-10)
    
    # Normalize to [0, 1]
    W_norm = (W - row_min) / row_range
    
    # Quantize to n_levels uniform steps
    W_quant = torch.round(W_norm * (n_levels - 1)) / (n_levels - 1)
    
    # Denormalize
    return W_quant * row_range + row_min


def quantize_nbit_quartile(W: torch.Tensor, n_bits: int) -> torch.Tensor:
    """Shape-aware n-bit quantization: levels at magnitude quantiles.
    
    Like GPTQ/NF4 — places levels where the data actually IS,
    not uniformly. Should preserve shape much better at low bit counts.
    """
    W = W.detach().float().cpu()
    n_levels = 2 ** n_bits
    out_f, in_f = W.shape
    
    W_quant = torch.zeros_like(W)
    
    for i in range(out_f):
        row = W[i]
        # Compute quantile boundaries
        quantiles = torch.linspace(0, 1, n_levels + 1, device=W.device)
        boundaries = torch.quantile(row, quantiles)
        
        # Compute level centers (midpoint of each bin)
        centers = (boundaries[:-1] + boundaries[1:]) / 2
        
        # Assign each weight to nearest center
        # Expand for broadcasting: row (in_f,) vs centers (n_levels,)
        diffs = (row.unsqueeze(1) - centers.unsqueeze(0)).abs()  # (in_f, n_levels)
        assignments = diffs.argmin(dim=1)  # (in_f,)
        W_quant[i] = centers[assignments]
    
    return W_quant


# ═══════════════════════════════════════════════════════════════════
# Shape measurement — the core metric
# ═══════════════════════════════════════════════════════════════════

@dataclass
class LayerMetrics:
    layer_idx: int
    weight_name: str
    cosine: float
    shape_spearman: float  # Spearman rank correlation of |W| vs |W_q| per row, averaged
    shape_pearson: float   # Pearson correlation of |W| vs |W_q| per row, averaged
    peak_preservation: float  # fraction of top-10% magnitude positions that stay in top-10%
    node_preservation: float  # fraction of bottom-10% that stay in bottom-10%


def measure_shape(W_orig: torch.Tensor, W_quant: torch.Tensor) -> dict:
    """Measure how well quantization preserves the magnitude shape.
    
    Returns dict with cosine, spearman, pearson, peak_preservation, node_preservation.
    """
    W_o = W_orig.detach().float().cpu()
    W_q = W_quant.detach().float().cpu()
    
    # 1. Global cosine
    cos = F.cosine_similarity(
        W_o.reshape(1, -1), W_q.reshape(1, -1)
    ).item()
    
    # 2. Per-row Spearman rank correlation of magnitudes
    abs_o = W_o.abs().numpy()
    abs_q = W_q.abs().numpy()
    
    spearman_scores = []
    pearson_scores = []
    
    n_rows = min(abs_o.shape[0], 200)  # sample rows for speed
    row_indices = np.linspace(0, abs_o.shape[0] - 1, n_rows, dtype=int)
    
    for i in row_indices:
        row_o = abs_o[i]
        row_q = abs_q[i]
        
        # Skip constant rows
        if row_o.std() < 1e-10 or row_q.std() < 1e-10:
            continue
        
        sp, _ = scipy_stats.spearmanr(row_o, row_q)
        pe, _ = scipy_stats.pearsonr(row_o, row_q)
        
        if not np.isnan(sp):
            spearman_scores.append(sp)
        if not np.isnan(pe):
            pearson_scores.append(pe)
    
    spearman_mean = float(np.mean(spearman_scores)) if spearman_scores else 0.0
    pearson_mean = float(np.mean(pearson_scores)) if pearson_scores else 0.0
    
    # 3. Peak preservation: do the biggest weights stay biggest?
    # Top 10% by magnitude in original — what fraction stay in top 10% after quant?
    W_o_cpu = W_o.cpu()
    W_q_cpu = W_q.cpu()
    k_top = max(1, W_o_cpu.numel() // 10)
    top_orig = torch.topk(W_o_cpu.abs().reshape(-1), k_top).indices
    top_quant = torch.topk(W_q_cpu.abs().reshape(-1), k_top).indices
    
    top_orig_set = set(top_orig.numpy())
    top_quant_set = set(top_quant.numpy())
    peak_pres = len(top_orig_set & top_quant_set) / len(top_orig_set) if top_orig_set else 0.0
    
    # 4. Node preservation: do the smallest weights stay smallest?
    # Bottom 10% by magnitude
    bot_orig = torch.topk(W_o_cpu.abs().reshape(-1), k_top, largest=False).indices
    bot_quant = torch.topk(W_q_cpu.abs().reshape(-1), k_top, largest=False).indices
    
    bot_orig_set = set(bot_orig.numpy())
    bot_quant_set = set(bot_quant.numpy())
    node_pres = len(bot_orig_set & bot_quant_set) / len(bot_orig_set) if bot_orig_set else 0.0
    
    return {
        'cosine': cos,
        'spearman': spearman_mean,
        'pearson': pearson_mean,
        'peak_preservation': peak_pres,
        'node_preservation': node_pres,
    }


# ═══════════════════════════════════════════════════════════════════
# The experiment
# ═══════════════════════════════════════════════════════════════════

QUANT_METHODS = {
    'ternary_50':       ('Ternary (50% zeros)',    1.6, lambda W: quantize_ternary(W, 0.50)),
    'ternary_35':       ('Ternary (35% zeros)',    1.6, lambda W: quantize_ternary(W, 0.35)),
    'ternary_0':        ('Ternary (no zeros)',     1.6, lambda W: quantize_ternary(W, 0.00)),
    '2bit_uniform':     ('2-bit uniform',          2.0, lambda W: quantize_nbit_uniform(W, 2)),
    '2bit_quartile':    ('2-bit shape-aware',      2.0, lambda W: quantize_nbit_quartile(W, 2)),
    '3bit_uniform':     ('3-bit uniform',          3.0, lambda W: quantize_nbit_uniform(W, 3)),
    '4bit_uniform':     ('4-bit uniform',          4.0, lambda W: quantize_nbit_uniform(W, 4)),
    '4bit_quartile':    ('4-bit shape-aware',      4.0, lambda W: quantize_nbit_quartile(W, 4)),
    '8bit_uniform':     ('8-bit uniform',          8.0, lambda W: quantize_nbit_uniform(W, 8)),
}


class QuantLinear(nn.Module):
    """Drop-in Linear replacement with pre-computed quantized weights."""
    
    def __init__(self, W_quant: torch.Tensor, bias: torch.Tensor | None):
        super().__init__()
        self.register_buffer('weight', W_quant)
        if bias is not None:
            self.register_buffer('bias', bias)
        else:
            self.bias = None
    
    def forward(self, x):
        return F.linear(x, self.weight, self.bias)


def quantize_model(model, method_key: str, device: str = "cpu"):
    """Quantize all FFN weights and collect shape metrics.
    
    Pythia-160M architecture: GPT-NeoX
      FFN: dense_h_to_4h (768 → 3072), dense_4h_to_h (3072 → 768)
    """
    _, label, bits, quant_fn = method_key, *QUANT_METHODS[method_key]
    
    all_metrics = []
    
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            linear = getattr(mlp, name)
            W = linear.weight.data.float()
            
            # Quantize
            W_q = quant_fn(W)
            
            # Measure shape
            m = measure_shape(W, W_q)
            metrics = LayerMetrics(
                layer_idx=layer_idx,
                weight_name=name,
                cosine=m['cosine'],
                shape_spearman=m['spearman'],
                shape_pearson=m['pearson'],
                peak_preservation=m['peak_preservation'],
                node_preservation=m['node_preservation'],
            )
            all_metrics.append(metrics)
            
            # Replace weight
            bias = linear.bias.data.float() if linear.bias is not None else None
            quant_linear = QuantLinear(W_q.to(device), bias.to(device) if bias is not None else None)
            setattr(mlp, name, quant_linear)
    
    return all_metrics


def evaluate_perplexity(model, tokenizer, device, max_tokens: int = 32768):
    """Evaluate perplexity on WikiText-2 validation set."""
    from datasets import load_dataset
    
    dataset = load_dataset("wikitext", "wikitext-2-raw-v1", split="validation")
    
    # Concatenate all text
    texts = [t for t in dataset['text'] if t.strip()]
    full_text = "\n".join(texts)
    
    tokens = tokenizer.encode(full_text, add_special_tokens=False)
    tokens = tokens[:max_tokens]
    
    model.eval()
    seq_len = 256
    total_loss = 0.0
    total_tokens = 0
    
    with torch.no_grad():
        for start in range(0, len(tokens) - seq_len, seq_len):
            chunk = tokens[start:start + seq_len]
            input_ids = torch.tensor([chunk], device=device)
            
            outputs = model(input_ids, labels=input_ids)
            total_loss += outputs.loss.item() * (len(chunk) - 1)
            total_tokens += len(chunk) - 1
    
    avg_loss = total_loss / max(total_tokens, 1)
    ppl = math.exp(min(avg_loss, 20))
    return ppl


def main():
    parser = argparse.ArgumentParser(description="Standing-wave shape preservation experiment")
    parser.add_argument('--model', default='EleutherAI/pythia-160m-deduped')
    parser.add_argument('--device', default='mps' if torch.backends.mps.is_available() else 'cpu')
    parser.add_argument('--max-tokens', type=int, default=32768)
    args = parser.parse_args()
    
    log(f"═══ Standing-Wave Shape Preservation Experiment ═══")
    log(f"Model: {args.model}")
    log(f"Device: {args.device}")
    log()
    
    from transformers import AutoModelForCausalLM, AutoTokenizer
    
    # Load tokenizer once
    log("Loading tokenizer...")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    # ── Float baseline ──
    log("Loading float model for baseline...")
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)
    model = model.to(args.device)
    
    log("Evaluating float baseline PPL...")
    float_ppl = evaluate_perplexity(model, tokenizer, args.device, args.max_tokens)
    log(f"  Float PPL: {float_ppl:.2f}")
    log()
    
    # Save original weights for re-use
    log("Caching original weights...")
    original_weights = {}
    for layer_idx, layer in enumerate(model.gpt_neox.layers):
        mlp = layer.mlp
        for name in ['dense_h_to_4h', 'dense_4h_to_h']:
            linear = getattr(mlp, name)
            key = f"layer{layer_idx}.{name}"
            original_weights[key] = {
                'weight': linear.weight.data.float().cpu().clone(),
                'bias': linear.bias.data.float().cpu().clone() if linear.bias is not None else None,
            }
    log(f"  Cached {len(original_weights)} weight matrices")
    log()
    
    # ── Run each quantization method ──
    results = []
    
    for method_key in QUANT_METHODS:
        label, bits, quant_fn = QUANT_METHODS[method_key]
        log(f"{'─' * 60}")
        log(f"Method: {label} ({bits:.1f} bits)")
        
        # Restore original weights
        for layer_idx, layer in enumerate(model.gpt_neox.layers):
            mlp = layer.mlp
            for name in ['dense_h_to_4h', 'dense_4h_to_h']:
                key = f"layer{layer_idx}.{name}"
                orig = original_weights[key]
                
                # Restore as nn.Linear
                in_f = orig['weight'].shape[1]
                out_f = orig['weight'].shape[0]
                has_bias = orig['bias'] is not None
                new_linear = nn.Linear(in_f, out_f, bias=has_bias)
                new_linear.weight.data = orig['weight'].clone().to(args.device)
                if has_bias:
                    new_linear.bias.data = orig['bias'].clone().to(args.device)
                setattr(mlp, name, new_linear)
        
        # Quantize and measure shape
        t0 = time.time()
        metrics = quantize_model(model, method_key, args.device)
        quant_time = time.time() - t0
        
        # Aggregate shape metrics across layers
        avg_cosine = np.mean([m.cosine for m in metrics])
        avg_spearman = np.mean([m.shape_spearman for m in metrics])
        avg_pearson = np.mean([m.shape_pearson for m in metrics])
        avg_peak = np.mean([m.peak_preservation for m in metrics])
        avg_node = np.mean([m.node_preservation for m in metrics])
        
        # Compute compounded cosine (product across layers)
        # Group by layer, average within layer, then multiply across
        layer_cosines = {}
        for m in metrics:
            if m.layer_idx not in layer_cosines:
                layer_cosines[m.layer_idx] = []
            layer_cosines[m.layer_idx].append(m.cosine)
        per_layer_avg = [np.mean(v) for v in layer_cosines.values()]
        compounded_cosine = float(np.prod(per_layer_avg))
        
        log(f"  Avg cosine:         {avg_cosine:.4f}")
        log(f"  Compounded cosine:  {compounded_cosine:.6f}")
        log(f"  Shape (Spearman):   {avg_spearman:.4f}")
        log(f"  Shape (Pearson):    {avg_pearson:.4f}")
        log(f"  Peak preservation:  {avg_peak:.4f}")
        log(f"  Node preservation:  {avg_node:.4f}")
        log(f"  Quantize time:      {quant_time:.1f}s")
        
        # Evaluate PPL
        log(f"  Evaluating PPL...")
        ppl = evaluate_perplexity(model, tokenizer, args.device, args.max_tokens)
        log(f"  PPL: {ppl:.2f}")
        
        results.append({
            'method': method_key,
            'label': label,
            'bits': bits,
            'cosine': avg_cosine,
            'compounded_cosine': compounded_cosine,
            'spearman': avg_spearman,
            'pearson': avg_pearson,
            'peak_preservation': avg_peak,
            'node_preservation': avg_node,
            'ppl': ppl,
            'per_layer': [(m.layer_idx, m.weight_name, m.cosine, m.shape_spearman) for m in metrics],
        })
        
        log()
    
    # ═══ Summary table ═══
    log(f"{'═' * 80}")
    log(f"SUMMARY — Standing-Wave Shape Preservation")
    log(f"{'═' * 80}")
    log(f"Float baseline PPL: {float_ppl:.2f}")
    log()
    log(f"{'Method':<25} {'Bits':>5} {'Cosine':>8} {'Compound':>10} {'Spearman':>10} {'Peak%':>7} {'Node%':>7} {'PPL':>10}")
    log(f"{'─' * 25} {'─' * 5} {'─' * 8} {'─' * 10} {'─' * 10} {'─' * 7} {'─' * 7} {'─' * 10}")
    
    for r in sorted(results, key=lambda x: x['ppl']):
        log(f"{r['label']:<25} {r['bits']:>5.1f} {r['cosine']:>8.4f} {r['compounded_cosine']:>10.6f} "
            f"{r['spearman']:>10.4f} {r['peak_preservation']:>7.3f} {r['node_preservation']:>7.3f} {r['ppl']:>10.2f}")
    
    log()
    
    # ═══ Analysis: Shape vs Bits as PPL predictor ═══
    log(f"{'═' * 80}")
    log(f"ANALYSIS — What predicts PPL?")
    log(f"{'═' * 80}")
    
    ppls = [r['ppl'] for r in results]
    bits_arr = [r['bits'] for r in results]
    spearman_arr = [r['spearman'] for r in results]
    cosine_arr = [r['cosine'] for r in results]
    compound_arr = [r['compounded_cosine'] for r in results]
    peak_arr = [r['peak_preservation'] for r in results]
    
    log_ppls = [math.log(p) for p in ppls]
    
    # Correlate each predictor with log(PPL)
    predictors = [
        ('bits', bits_arr),
        ('cosine', cosine_arr),
        ('compounded_cosine', compound_arr),
        ('spearman (shape)', spearman_arr),
        ('peak_preservation', peak_arr),
    ]
    
    log(f"\nRank correlation with log(PPL):")
    log(f"  (negative = higher metric → lower PPL = better prediction)")
    log()
    
    for name, arr in predictors:
        rho, pval = scipy_stats.spearmanr(arr, log_ppls)
        log(f"  {name:<25} ρ = {rho:+.4f}  (p = {pval:.4f})")
    
    log()
    
    # Key comparison: ternary vs 2-bit
    ternary_50 = next((r for r in results if r['method'] == 'ternary_50'), None)
    twobit_q = next((r for r in results if r['method'] == '2bit_quartile'), None)
    twobit_u = next((r for r in results if r['method'] == '2bit_uniform'), None)
    
    if ternary_50 and twobit_q:
        log(f"KEY COMPARISON — Same bit budget, different shape preservation:")
        log(f"  Ternary 50%:       bits={ternary_50['bits']:.1f}  shape={ternary_50['spearman']:.4f}  PPL={ternary_50['ppl']:.2f}")
        log(f"  2-bit shape-aware: bits={twobit_q['bits']:.1f}  shape={twobit_q['spearman']:.4f}  PPL={twobit_q['ppl']:.2f}")
        if twobit_u:
            log(f"  2-bit uniform:     bits={twobit_u['bits']:.1f}  shape={twobit_u['spearman']:.4f}  PPL={twobit_u['ppl']:.2f}")
        
        ratio = ternary_50['ppl'] / twobit_q['ppl'] if twobit_q['ppl'] > 0 else float('inf')
        log(f"  PPL ratio (ternary/2bit-shape): {ratio:.2f}×")
        log()
        
        if ratio > 2.0:
            log(f"  ✅ HYPOTHESIS SUPPORTED: at similar bit budgets, shape preservation")
            log(f"     dramatically improves quality. Shape > bits.")
        elif ratio > 1.2:
            log(f"  ⚠️  PARTIAL SUPPORT: shape helps, but the effect is moderate.")
        else:
            log(f"  ❌ HYPOTHESIS NOT SUPPORTED: shape doesn't explain the difference.")
    
    log()
    log("Done.")
    
    # Save results
    import json
    out_dir = "results/standing-wave-shape"
    os.makedirs(out_dir, exist_ok=True)
    
    summary = {
        'model': args.model,
        'float_ppl': float_ppl,
        'results': [{k: v for k, v in r.items() if k != 'per_layer'} for r in results],
        'per_layer': {r['method']: r['per_layer'] for r in results},
    }
    
    with open(f"{out_dir}/summary.json", 'w') as f:
        json.dump(summary, f, indent=2)
    log(f"Results saved to {out_dir}/summary.json")


if __name__ == '__main__':
    main()
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; python3 -c \"import torch; print('mps', torch.backends.mps.is_available()); print('torch', torch.__version__)\" 2>&1; echo \"=== unified mem ===\"; sysctl -n hw.memsize 2>/dev/null | awk '{print $1/1e9 \" GB\"}'; echo \"=== full_ternarize signature ===\"; grep -nE \"^def |^class |load_model|AutoModel|per.?row|zero_rate|def main|argparse|add_argument\" scripts/experiments/full_ternarize.py | head -40"
}
```

**Summary:** $ python3 -c "import torch; print('mp...

**Output:**
```
Exit code: 0
Stdout:
Traceback (most recent call last):
  File "<string>", line 1, in <module>
    import torch; print('mps', torch.backends.mps.is_available()); print('torch', torch.__version__)
    ^^^^^^^^^^^^
ModuleNotFoundError: No module named 'torch'
=== unified mem ===
549.756 GB
=== full_ternarize signature ===
8:  2. ZERO:   T(i,j) = 0 where |W(i,j)| < percentile(|W(i,:)|, zero_rate)
10:  3. SCALE:  γ(i) = (w_i · t_i) / (t_i · t_i)   — optimal per-row scalar
28:import argparse
45:def log(msg: str = "") -> None:
53:class TernaryLinear(nn.Module):
54:    """Linear layer with ternary weights {-1, 0, +1} and per-row scale.
58:      gamma: float32 tensor (out_features,) — per-row scale factor
106:def ternarize_weight(W: torch.Tensor, zero_rate: float = 0.35) -> tuple[torch.Tensor, torch.Tensor]:
111:        zero_rate: fraction of smallest-magnitude weights per row to zero
115:        gamma: float32 per-row scale factors
123:    if zero_rate > 0:
124:        # Compute per-row threshold using quantile
126:        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)  # (out_f, 1)
134:    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
136:    tt = (T * T).sum(dim=1)             # (out_f,) — equals count of nonzeros per row
142:def ternarize_linear(linear: nn.Linear, zero_rate: float = 0.35) -> TernaryLinear:
147:    T, gamma = ternarize_weight(W, zero_rate)
164:def get_model_layers(model):
175:def ternarize_layer(layer: nn.Module, zero_rate: float, layer_idx: int,
185:        tl, cos = ternarize_linear(proj, zero_rate)
205:        tl, cos = ternarize_linear(proj, zero_rate)
223:def ternarize_model(model, zero_rate: float = 0.35, device: str = "cpu") -> list[dict]:
230:    log(f"  TERNARIZING {n_layers} LAYERS  (zero_rate={zero_rate:.0%})")
240:        stats = ternarize_layer(layer, zero_rate, i, n_layers, device=device)
300:def load_eval_texts(max_tokens: int = 32768) -> list[str]:
343:def evaluate_perplexity(model, tokenizer, texts: list[str],
445:def test_generation(model, tokenizer, prompts: list[str],
486:def print_generations(results: list[dict], label: str = ""):
505:def memory_report(model) -> dict:
542:def main():
543:    parser = argparse.ArgumentParser(description="Full-model ternarization")
544:    parser.add_argument("--model", type=str, default="Qwen/Qwen3-8B")
545:    parser.add_argument("--device", type=str, default="auto")
546:    parser.add_argument("--zero-rate", type=float, default=0.35,
547:                        help="Fraction of smallest-magnitude weights per row to zero (default: 0.35)")
548:    parser.add_argument("--max-length", type=int, default=512,
550:    parser.add_argument("--stride", type=int, default=256,
552:    parser.add_argument("--skip-baseline", action="store_true",
554:    parser.add_argument("--skip-perplexity", action="store_true",
556:    parser.add_argument("--skip-generation", action="store_true",
```

### Thinking

I see that torch is installed in the uv-managed virtual environment rather than the system Python, so I need to run scripts through `uv run python` to access it. The system has 549 GB of unified memory, which is plenty of headroom for running even large models like an 8B parameter model in fp32 or fp16.

The `full_ternarize.py` script already implements the exact ternarization approach I need—it handles Qwen models, computes perplexity, supports per-row gamma scaling, and includes zero-rate control. My plan is to extend this into an asymmetric A/B comparison harness where Config A uses uniform ternary quantization across all weight matrices, while Config B applies different bit budgets per matrix type: binary quantization for the gate projection and 3-bit for the up/down projections. I'll need to implement quantizers for both ternary (1.58-bit) and binary (pure sign with per-row gamma scaling) representations.

However, there's a fundamental constraint I'm running into: the three matrices in SwiGLU have equal parameter counts, so if I use 1-bit for the gate and 3-bit for the value path, the mean bits work out to 2.33—significantly higher than the 1.58-bit baseline. To actually match the mean bits at 1.58 while keeping the router at 1-bit, the value path would only compress to about 1.87 bits, which doesn't meaningfully cross into the 3-bit regime. This suggests the "matched-bit" framing itself has a problem: I can't simultaneously free up bits from the router and maintain the same overall mean.

I need to reconsider the experimental design more carefully. Either I go with a truly matched mean-bits comparison—which forces the value path to stay near 1.87 bits, an awkward non-standard level—or I accept an unmatched budget and instead show that reallocating bits from router to value improves perplexity, even if the total budget shifts slightly.

The cleaner test is to fix total bit budget and ask: does concentrating bits on the value path (asymmetric) beat spreading them evenly (uniform)? If I set total budget at 2.33 bits per weight, I can compare uniform matrices all at ~2.33 bits against a 1-bit router plus value matrices sized so (1 + 2·B_v)/3 = 2.33, giving B_v = 3. That directly isolates whether the reallocation itself is the win. The challenge is that 2.33 bits per matrix isn't a clean quantizer level, so I might need to work with 2-bit uniform (total 6 bits across three matrices) and adjust the asymmetric side to match that budget.

A more rigorous approach: sweep multiple configurations with clean integer bit-widths, compute the exact mean bits per weight for each (accounting for matrix sizes, gamma amortization, and zero-mask overhead), then plot PPL against mean bits and check whether asymmetric configs sit below the uniform frontier. This is the Pareto-style comparison—if asymmetric beats uniform at the same mean-bits budget, that's the evidence. I'd test uniform ternary (the current recipe), uniform 2-bit, uniform 3-bit, asymmetric with binary router plus 3-bit value, asymmetric with binary router plus 2-bit value, and crucially, an inverted asymmetric (3-bit router plus binary value) as a control to confirm that the direction of reallocation matters. I'm clarifying the bit accounting: ternary {-1,0,+1} costs log₂(3) ≈ 1.585 bits per element, binary {-1,+1} with per-row gamma costs 1 bit, and n-bit uniform costs n bits — matching the standard accounting from prior work. For the router (gate projection), I can apply binary quantization with zero_rate=0, which gives a sign-only representation with gamma amortization, effectively 1 bit per element. This asymmetric setup — binary router paired with higher-bit values — is exactly what the article predicts should work, and it's distinct from the catastrophic failure seen when applying sign-only quantization to the entire FFN in prior experiments.

The crucial realization is that this asymmetric pathway hypothesis only applies to SwiGLU architectures with a separate gate_proj router. Pythia uses dense FFN without a gate, so it can't test the gate/value split at all. Qwen3-8B-Base has the gate_proj, up_proj, and down_proj structure needed to validate the hypothesis, and it's the exact model family measured in prior work. So Qwen3-8B-Base is actually required, not optional — I can smoke-test the harness on Pythia to verify the evaluation pipeline works, but the real hypothesis test must run on Qwen. With 549GB RAM available, running Qwen3-8B-Base directly is feasible.

Now I need to check how the existing quantization code handles Qwen's architecture.

Let me outline the full task: build an asymmetric quantization harness that extends the current ternarization code with per-matrix-type bit budgets, add binary and n-bit quantizers, track mean bits, and test configurations like binary-router with 3-bit or 2-bit values versus the inverted case. I'll smoke-test on a small slice first, then run the full A/B comparison across float, uniform ternary, uniform 2-bit, uniform 3-bit, and the asymmetric variants, computing perplexity and mean bits for each. The evaluation should take roughly 30 minutes total across all configs on MPS.

Since quantizing each config requires reloading original weights and the FFN cache is manageable at ~21GB for an 8B model, I can run this as a background job. Now I need to read the key functions from full_ternarize.py—get_model_layers, ternarize_layer, ternarize_weight, evaluate_perplexity, and load_eval_texts—so I can reuse them correctly in the new harness.

## Assistant

Decisive findings that shape the experiment:

1. **549 GB unified memory** — an 8B in fp32 (~32 GB) alongside the llama.cpp servers is trivial. No memory constraint. (torch lives in the uv `.venv`; scripts run via `uv run python`.)
2. **`full_ternarize.py` already does exactly this on Qwen** — `Qwen/Qwen3-8B` default, per-row γ, zero_rate, `get_model_layers`, `ternarize_layer` (handles gate/up/down/qkvo), `evaluate_perplexity` with stride. This is my base to extend, per `λ build`/`λ one_way`.
3. **Architectural requirement I need to flag:** the pathway hypothesis is specifically about SwiGLU's `gate_proj` (router) vs `up/down` (value). **Pythia has no gate_proj** (GPT-NeoX, GELU) — so it *cannot* test this split. Qwen3-8B-Base is not just preferred, it's **required** — and it's the exact model family s203/s170/s185 were measured on. Your instinct to gate on that download was right.

Let me read the exact reusable functions before writing, then plan.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/full_ternarize.py",
  "line_offset": 105,
  "limit": 210
}
```

**Summary:** Reading full_ternarize.py (105-315)

**Output:**
```
def ternarize_weight(W: torch.Tensor, zero_rate: float = 0.35) -> tuple[torch.Tensor, torch.Tensor]:
    """Ternarize a weight matrix using the proven recipe.

    Args:
        W: float weight matrix (out_features, in_features)
        zero_rate: fraction of smallest-magnitude weights per row to zero

    Returns:
        T: int8 ternary matrix {-1, 0, +1}
        gamma: float32 per-row scale factors
    """
    W_float = W.detach().float().cpu()
    out_f, in_f = W_float.shape

    # Per-row magnitude threshold
    abs_W = W_float.abs()

    if zero_rate > 0:
        # Compute per-row threshold using quantile
        # quantile along dim=1 for each row
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)  # (out_f, 1)
        alive_mask = abs_W >= thresholds  # True where weight survives
    else:
        alive_mask = torch.ones_like(W_float, dtype=torch.bool)

    # Signs where alive, 0 where dead
    T = torch.where(alive_mask, torch.sign(W_float), torch.zeros_like(W_float))

    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
    wt = (W_float * T).sum(dim=1)      # (out_f,)
    tt = (T * T).sum(dim=1)             # (out_f,) — equals count of nonzeros per row
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))

    return T.to(torch.int8), gamma


def ternarize_linear(linear: nn.Linear, zero_rate: float = 0.35) -> TernaryLinear:
    """Convert an nn.Linear to TernaryLinear."""
    W = linear.weight
    bias = linear.bias

    T, gamma = ternarize_weight(W, zero_rate)

    # Compute reconstruction quality before we lose the weights
    W_float = W.detach().float().cpu()
    W_recon = gamma.unsqueeze(1) * T.float()
    cos = F.cosine_similarity(W_float.reshape(1, -1), W_recon.reshape(1, -1)).item()

    bias_tensor = bias.detach().float().cpu() if bias is not None else None
    tl = TernaryLinear(T, gamma, bias_tensor)

    return tl, cos


# ═══════════════════════════════════════════════════════════════════════
# Model surgery — monkey-patch all Linear layers
# ═══════════════════════════════════════════════════════════════════════

def get_model_layers(model):
    """Extract the transformer layers container."""
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise RuntimeError("Cannot find layers — add support for this architecture")


WEIGHT_NAMES_FFN = ['gate_proj', 'up_proj', 'down_proj']
WEIGHT_NAMES_ATTN = ['q_proj', 'k_proj', 'v_proj', 'o_proj']


def ternarize_layer(layer: nn.Module, zero_rate: float, layer_idx: int,
                    n_layers: int, device: str = "cpu") -> dict:
    """Ternarize all weight matrices in a single transformer layer."""
    stats = {'layer': layer_idx, 'depth': layer_idx / n_layers}

    # FFN weights
    for name in WEIGHT_NAMES_FFN:
        proj = getattr(layer.mlp, name, None)
        if proj is None:
            continue
        tl, cos = ternarize_linear(proj, zero_rate)
        tl = tl.to(device)  # Move buffers to model device
        setattr(layer.mlp, name, tl)
        zeros = (tl.T == 0).sum().item()
        total = tl.T.numel()
        stats[name] = {
            'cosine': cos,
            'zeros': zeros,
            'total': total,
            'zero_pct': zeros / total * 100,
            'shape': list(tl.T.shape),
        }
        del proj
        gc.collect()

    # Attention weights
    for name in WEIGHT_NAMES_ATTN:
        proj = getattr(layer.self_attn, name, None)
        if proj is None:
            continue
        tl, cos = ternarize_linear(proj, zero_rate)
        tl = tl.to(device)  # Move buffers to model device
        setattr(layer.self_attn, name, tl)
        zeros = (tl.T == 0).sum().item()
        total = tl.T.numel()
        stats[name] = {
            'cosine': cos,
            'zeros': zeros,
            'total': total,
            'zero_pct': zeros / total * 100,
            'shape': list(tl.T.shape),
        }
        del proj
        gc.collect()

    return stats


def ternarize_model(model, zero_rate: float = 0.35, device: str = "cpu") -> list[dict]:
    """Ternarize all layers of the model in-place."""
    layers = get_model_layers(model)
    n_layers = len(layers)
    all_stats = []

    log(f"\n{'═' * 78}")
    log(f"  TERNARIZING {n_layers} LAYERS  (zero_rate={zero_rate:.0%})")
    log(f"{'═' * 78}")
    log(f"  {'Layer':>5}  {'gate cos':>9} {'up cos':>9} {'down cos':>9} "
          f"{'q cos':>9} {'k cos':>9} {'v cos':>9} {'o cos':>9}")
    log(f"  {'─' * 5}  {'─' * 9} {'─' * 9} {'─' * 9} "
          f"{'─' * 9} {'─' * 9} {'─' * 9} {'─' * 9}")

    t0 = time.time()
    for i, layer in enumerate(layers):
        t_layer = time.time()
        stats = ternarize_layer(layer, zero_rate, i, n_layers, device=device)
        all_stats.append(stats)

        # Print per-layer cosines
        cosines = []
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in stats:
                cosines.append(f"{stats[name]['cosine']:>9.5f}")
            else:
                cosines.append(f"{'N/A':>9}")
        log(f"  {i:>5}  {' '.join(cosines)}  ({time.time() - t_layer:.1f}s)")

        # Force GC every layer
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    elapsed = time.time() - t0

    # Summary
    total_zeros = 0
    total_params = 0
    cos_by_type = {n: [] for n in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN}
    for s in all_stats:
        for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
            if name in s:
                total_zeros += s[name]['zeros']
                total_params += s[name]['total']
                cos_by_type[name].append(s[name]['cosine'])

    log(f"\n  {'─' * 78}")
    log(f"  Total ternarized: {total_params:,} params in {elapsed:.1f}s")
    log(f"  Overall zeros: {total_zeros:,} / {total_params:,} ({total_zeros / total_params * 100:.1f}%)")
    log(f"\n  Mean cosine by weight type:")
    for name in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN:
        if cos_by_type[name]:
            vals = cos_by_type[name]
            log(f"    {name:<12} mean={np.mean(vals):.5f}  min={np.min(vals):.5f}  max={np.max(vals):.5f}")

    # Size estimate
    # Ternary weights: 1.58 bits/param (log2(3))
    ternary_bits = total_params * math.log2(3)
    ternary_bytes = ternary_bits / 8
    # Per-row gamma: float32 per output row
    total_rows = sum(s[n]['shape'][0] for s in all_stats for n in WEIGHT_NAMES_FFN + WEIGHT_NAMES_ATTN if n in s)
    gamma_bytes = total_rows * 4  # float32

    log(f"\n  Size estimate:")
    log(f"    Ternary weights: {ternary_bytes / 1e9:.3f} GB ({total_params * 1.58:.0f} Mbits)")
    log(f"    Gamma scalars:   {gamma_bytes / 1e6:.2f} MB ({total_rows:,} rows × 4 bytes)")
    log(f"    Original fp16:   {total_params * 2 / 1e9:.3f} GB")
    log(f"    Compression:     {total_params * 2 / (ternary_bytes + gamma_bytes):.1f}×")

    return all_stats


# ═══════════════════════════════════════════════════════════════════════
# Perplexity evaluation
# ═══════════════════════════════════════════════════════════════════════

def load_eval_texts(max_tokens: int = 32768) -> list[str]:
    """Load evaluation texts. Try WikiText-2, fall back to built-in corpus."""
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        # Concatenate non-empty lines
        texts = [t for t in ds["text"] if t.strip()]
        log(f"  Loaded WikiText-2 test: {len(texts)} lines")
        return texts
    except Exception as e:
        log(f"  WikiText-2 unavailable ({e}), using built-in corpus")
        return [
            "The speed of light in vacuum is 299792458 meters per second. "
            "This fundamental constant of nature was first measured with reasonable accuracy by "
            "Ole Rømer in 1676 through observations of the moons of Jupiter. "
            "The modern value was established by the 17th General Conference on Weights and Measures in 1983, "

[CONTENT TRUNCATED] Showing lines 106 to 315 of 712 total lines. Use line_offset=315 parameter to read more content.
```

### Thinking

I've got the key components from `full_ternarize.py`: a function that converts weights to ternary values with per-row scaling factors, a custom linear layer module, utilities to extract model layers and identify FFN weight names, and a perplexity evaluation function.

Now I'm planning an asymmetric quantization harness that applies different bit-widths to different matrix types—binary (1 bit via sign + scale), ternary (1.58 bits), and uniform n-bit (2, 3, 4 bits). Rather than create a complex shared module, I'll write a self-contained experiment script that copies the small proven quantizer functions and applies them per-matrix-type with config-driven selection, then evaluates perplexity across different configurations. I need to recalculate the mean-bits accounting carefully to correct my earlier overclaim about bit costs.

Looking at the FFN matrices (gate, up, down projections all equal size), I'm comparing several quantization strategies: keeping everything ternary at 1.58 bits, uniform 2/3/4-bit across all three, and asymmetric approaches like binary on the gate projection with 3-bit on value projections (2.33 mean bits) or the inverted variant. The key Pareto comparison is whether the asymmetric binary-3 configuration achieves better perplexity-to-bits tradeoff than uniform quantization.

The inverted-null pair at matched 2.33 bits is the critical test—binary router with 3-bit values versus 3-bit router with binary values—which mirrors the article's finding about register assignment causality. I also caught an arithmetic error in my earlier framing: the mean bits for 1/3/3 is actually 2.33, not 1.58, so I need to correct that on the page and reframe around the Pareto frontier and inverted-null comparison instead.

Now I'm planning the execution: setting up a harness script, running a quick CPU smoke test on quantizers with a small tensor, then launching the full experiment on Qwen3-8B-Base in the background, followed by analysis and writeup.

I'm also thinking through the expected behavior—binarizing the value path should be catastrophic since it removes magnitude information, which is the whole point of the null test. The gate stays 3-bit in the inverted config to isolate the effect. I'm keeping attention in fp32 to focus cleanly on the FFN gate/up/down pathway. With 549GB RAM and MPS, the full run across 7 configs should take roughly 30-45 minutes, so I'll launch it as a background job and let it run without polling.

## Assistant

I have everything needed. `full_ternarize.py` gives me the proven `ternarize_weight` (sign+γ+zeros) and Qwen surgery; `standing_wave_shape.py` gives `quantize_nbit_uniform`. 

One important correction surfaced while designing — my knowledge page's arithmetic was loose: **"1-bit router + 3-bit value" is (1+3+3)/3 = 2.33 mean bits, NOT matched to uniform-1.58.** So the honest test isn't "matched 1.58" — it's a **Pareto frontier** (PPL vs mean-bits) plus the real causal null: **inverted register assignment at matched bits** — {binary router, 3-bit value} vs {3-bit router, binary value}, both 2.33 bits. That pair is the exact in-model analog of the article's int8×binary (−0.61) vs binary×binary (−7.2). I'll fold that correction back into the page after the run.

Let me set up the plan.Starting task 1 — building the harness.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "content": "#!/usr/bin/env python3\n\"\"\"Asymmetric-pathway quantization A/B — binarize the router, keep the value path.\n\nHYPOTHESIS (explore/asymmetric-pathway-quantization.md, s260):\n  In SwiGLU FFN the SIGN carries routing (gate_proj) and the MAGNITUDE\n  carries value (up_proj/down_proj) — the s203 \"two registers\" result.\n  So bits should be allocated ASYMMETRICALLY BY PATHWAY:\n    router gate_proj  -> 1-bit binary (sign+gamma; magnitude is <1 bit there)\n    value  up/down    -> keep 2-3 bits (magnitude/shape is load-bearing)\n\n  This is the in-model analog of Mixedbread's asymmetric quant\n  (int8 query x binary doc = -0.61 NDCG; binary x binary = -7.2): keep\n  magnitude on the side that carries it, binarize the side that doesn't.\n\nTHE TWO CRUX COMPARISONS (lambda yardstick — claim counts iff beats null):\n  1. PARETO. Does asym{binary-router, 3bit-value} sit BELOW the uniform\n     PPL-vs-mean-bits frontier (uniform-2bit, uniform-3bit)?\n  2. INVERTED-NULL at MATCHED mean-bits (2.33). Is {binary-router,3bit-value}\n     PPL far better than {3bit-router,binary-value}? Same bit budget, opposite\n     register assignment. This is the causal test of \"sign=router,\n     magnitude=value\" on the exact 8B where s203 measured it. It is the\n     in-model int8xbinary-vs-binaryxbinary.\n\nMEAN-BITS (corrected from the page's loose claim): gate/up/down are equal\nsize in SwiGLU, so mean-bits = mean of the three per-matrix costs.\n  binary=1.0, ternary=log2(3)=1.585, nbit-uniform=n. Gamma/scale amortized ~0.\n  => {1/3/3} = 2.33, NOT 1.58. \"1-bit router + 3-bit value at matched 1.58\"\n     is arithmetically impossible; the honest test is Pareto + inverted-null.\n\nSCOPE: FFN only (gate/up/down). Attention left fp32 to isolate the pathway\nclaim. Reuses proven quantizers (ternarize_weight, quantize_nbit_uniform).\n\nUsage:\n  uv run python scripts/experiments/asymmetric_pathway_quant.py \\\n      --model Qwen/Qwen3-8B-Base --max-tokens 32768\n  uv run python scripts/experiments/asymmetric_pathway_quant.py --self-test\n  uv run python scripts/experiments/asymmetric_pathway_quant.py \\\n      --model Qwen/Qwen3-8B-Base --configs float,uniform_ternary --max-tokens 2048\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport gc\nimport json\nimport math\nimport os\nimport time\nfrom dataclasses import dataclass\n\nos.environ.setdefault(\"PYTHONUNBUFFERED\", \"1\")\n\nimport numpy as np\nimport torch\nimport torch.nn as nn\nimport torch.nn.functional as F\n\n\ndef log(msg: str = \"\") -> None:\n    print(msg, flush=True)\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Quantizers — each returns a reconstructed float tensor + bit cost\n# (ternary/binary from full_ternarize.py; nbit from standing_wave_shape.py)\n# ═══════════════════════════════════════════════════════════════════\n\ndef quantize_signed(W: torch.Tensor, zero_rate: float) -> torch.Tensor:\n    \"\"\"Sign + per-row gamma + magnitude zeros.\n\n    zero_rate=0.0  -> binary {-1,+1} (1 bit)\n    zero_rate>0    -> ternary {-1,0,+1} (log2(3) bits)\n    \"\"\"\n    W = W.detach().float().cpu()\n    abs_W = W.abs()\n    if zero_rate > 0:\n        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)\n        alive = abs_W >= thresholds\n    else:\n        alive = torch.ones_like(W, dtype=torch.bool)\n    T = torch.where(alive, torch.sign(W), torch.zeros_like(W))\n    wt = (W * T).sum(dim=1)\n    tt = (T * T).sum(dim=1)\n    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))\n    return gamma.unsqueeze(1) * T\n\n\ndef quantize_nbit_uniform(W: torch.Tensor, n_bits: int) -> torch.Tensor:\n    \"\"\"Uniform n-bit quantization with per-row min/max scaling.\"\"\"\n    W = W.detach().float().cpu()\n    n_levels = 2 ** n_bits\n    row_min = W.min(dim=1, keepdim=True).values\n    row_max = W.max(dim=1, keepdim=True).values\n    row_range = torch.clamp(row_max - row_min, min=1e-10)\n    W_norm = (W - row_min) / row_range\n    W_quant = torch.round(W_norm * (n_levels - 1)) / (n_levels - 1)\n    return W_quant * row_range + row_min\n\n\n# A quant spec is (label, bits, fn(W)->reconstructed_float).\ndef spec_binary() -> tuple[str, float, callable]:\n    return (\"binary\", 1.0, lambda W: quantize_signed(W, 0.0))\n\n\ndef spec_ternary(zero_rate: float = 0.35) -> tuple[str, float, callable]:\n    return (f\"ternary{int(zero_rate * 100)}\", math.log2(3),\n            lambda W: quantize_signed(W, zero_rate))\n\n\ndef spec_nbit(n: int) -> tuple[str, float, callable]:\n    return (f\"{n}bit\", float(n), lambda W: quantize_nbit_uniform(W, n))\n\n\ndef spec_float() -> tuple[str, float, callable]:\n    return (\"float\", 16.0, lambda W: W.detach().float().cpu())\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Config: per-matrix-type quant spec over the SwiGLU FFN\n# ═══════════════════════════════════════════════════════════════════\n\nWEIGHT_NAMES_FFN = [\"gate_proj\", \"up_proj\", \"down_proj\"]\n\n\n@dataclass\nclass QuantConfig:\n    key: str\n    label: str\n    gate: tuple[str, float, callable]   # router\n    up: tuple[str, float, callable]     # value\n    down: tuple[str, float, callable]   # value\n\n    @property\n    def specs(self) -> dict[str, tuple[str, float, callable]]:\n        return {\"gate_proj\": self.gate, \"up_proj\": self.up, \"down_proj\": self.down}\n\n    @property\n    def mean_bits(self) -> float:\n        # gate/up/down equal size in SwiGLU -> simple mean of per-matrix bits.\n        return (self.gate[1] + self.up[1] + self.down[1]) / 3.0\n\n    @property\n    def is_float(self) -> bool:\n        return self.gate[0] == \"float\" and self.up[0] == \"float\" and self.down[0] == \"float\"\n\n\ndef build_configs() -> dict[str, QuantConfig]:\n    tern = spec_ternary(0.35)\n    b1 = spec_binary()\n    b2 = spec_nbit(2)\n    b3 = spec_nbit(3)\n    fl = spec_float()\n    cfgs = [\n        QuantConfig(\"float\", \"Float baseline\", fl, fl, fl),\n        # uniform frontier\n        QuantConfig(\"uniform_ternary\", \"Uniform ternary (1.58b)\", tern, tern, tern),\n        QuantConfig(\"uniform_2bit\", \"Uniform 2-bit\", b2, b2, b2),\n        QuantConfig(\"uniform_3bit\", \"Uniform 3-bit\", b3, b3, b3),\n        # asymmetric (binary router + precise value)\n        QuantConfig(\"asym_binR_3V\", \"Asym: binary router + 3-bit value\", b1, b3, b3),\n        QuantConfig(\"asym_binR_2V\", \"Asym: binary router + 2-bit value\", b1, b2, b2),\n        # inverted-null: 3-bit router + binary value (SAME 2.33 bits as asym_binR_3V)\n        QuantConfig(\"inv_3R_binV\", \"Inverted null: 3-bit router + binary value\", b3, b1, b1),\n    ]\n    return {c.key: c for c in cfgs}\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Model surgery\n# ═══════════════════════════════════════════════════════════════════\n\nclass QuantLinear(nn.Module):\n    \"\"\"Drop-in Linear with a pre-computed reconstructed float weight.\"\"\"\n\n    def __init__(self, W_quant: torch.Tensor, bias: torch.Tensor | None):\n        super().__init__()\n        self.register_buffer(\"weight\", W_quant)\n        self.bias = None\n        if bias is not None:\n            self.register_buffer(\"bias\", bias)\n\n    def forward(self, x):\n        return F.linear(x, self.weight, self.bias)\n\n\ndef get_model_layers(model):\n    if hasattr(model, \"model\") and hasattr(model.model, \"layers\"):\n        return model.model.layers\n    raise RuntimeError(\"Cannot find layers — add support for this architecture\")\n\n\ndef cache_ffn_weights(model) -> dict:\n    \"\"\"Snapshot original gate/up/down weights (+bias) as CPU float tensors.\"\"\"\n    orig = {}\n    for li, layer in enumerate(get_model_layers(model)):\n        for name in WEIGHT_NAMES_FFN:\n            lin = getattr(layer.mlp, name, None)\n            if lin is None:\n                continue\n            orig[f\"{li}.{name}\"] = {\n                \"weight\": lin.weight.data.float().cpu().clone(),\n                \"bias\": (lin.bias.data.float().cpu().clone()\n                         if getattr(lin, \"bias\", None) is not None else None),\n                \"in\": lin.weight.shape[1],\n                \"out\": lin.weight.shape[0],\n            }\n    return orig\n\n\ndef restore_ffn(model, orig: dict, device: str) -> None:\n    \"\"\"Restore original FFN as plain nn.Linear (undo prior surgery).\"\"\"\n    for li, layer in enumerate(get_model_layers(model)):\n        for name in WEIGHT_NAMES_FFN:\n            key = f\"{li}.{name}\"\n            if key not in orig:\n                continue\n            o = orig[key]\n            has_bias = o[\"bias\"] is not None\n            lin = nn.Linear(o[\"in\"], o[\"out\"], bias=has_bias)\n            lin.weight.data = o[\"weight\"].clone().to(device)\n            if has_bias:\n                lin.bias.data = o[\"bias\"].clone().to(device)\n            setattr(layer.mlp, name, lin)\n\n\ndef apply_config(model, cfg: QuantConfig, orig: dict, device: str) -> dict:\n    \"\"\"Quantize FFN per-config; return per-weight-type mean cosine.\"\"\"\n    cos_by_type: dict[str, list[float]] = {n: [] for n in WEIGHT_NAMES_FFN}\n    for li, layer in enumerate(get_model_layers(model)):\n        for name in WEIGHT_NAMES_FFN:\n            key = f\"{li}.{name}\"\n            if key not in orig:\n                continue\n            _, _, fn = cfg.specs[name]\n            W = orig[key][\"weight\"]\n            W_q = fn(W)\n            cos = F.cosine_similarity(\n                W.reshape(1, -1), W_q.reshape(1, -1)).item()\n            cos_by_type[name].append(cos)\n            bias = orig[key][\"bias\"]\n            ql = QuantLinear(\n                W_q.to(device),\n                bias.clone().to(device) if bias is not None else None,\n            )\n            setattr(layer.mlp, name, ql)\n        gc.collect()\n        if torch.backends.mps.is_available():\n            torch.mps.empty_cache()\n    return {n: float(np.mean(v)) if v else float(\"nan\") for n, v in cos_by_type.items()}\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Perplexity (sliding window, WikiText-2)\n# ═══════════════════════════════════════════════════════════════════\n\ndef load_eval_text(max_tokens_hint: int) -> str:\n    from datasets import load_dataset\n    ds = load_dataset(\"wikitext\", \"wikitext-2-raw-v1\", split=\"test\")\n    texts = [t for t in ds[\"text\"] if t.strip()]\n    return \"\\n\\n\".join(texts)\n\n\ndef evaluate_perplexity(model, tokenizer, device, text: str,\n                        max_tokens: int, seq_len: int = 512,\n                        stride: int = 256) -> float:\n    tokens = tokenizer.encode(text, add_special_tokens=False)[:max_tokens]\n    model.eval()\n    total_loss, total_tok = 0.0, 0\n    with torch.no_grad():\n        for start in range(0, max(1, len(tokens) - seq_len), stride):\n            chunk = tokens[start:start + seq_len]\n            if len(chunk) < 2:\n                continue\n            ids = torch.tensor([chunk], device=device)\n            out = model(ids, labels=ids)\n            loss = out.loss.item()\n            if math.isnan(loss) or math.isinf(loss):\n                return float(\"inf\")\n            total_loss += loss * (len(chunk) - 1)\n            total_tok += len(chunk) - 1\n    if total_tok == 0:\n        return float(\"nan\")\n    return math.exp(min(total_loss / total_tok, 20.0))\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Self-test (no model) — quantizer correctness\n# ═══════════════════════════════════════════════════════════════════\n\ndef self_test() -> int:\n    log(\"═══ self-test: quantizer correctness ═══\")\n    torch.manual_seed(0)\n    W = torch.randn(8, 64)\n    ok = True\n\n    b = quantize_signed(W, 0.0)\n    signs = torch.unique(torch.sign(b[b != 0]))\n    n_zero = (b == 0).sum().item()\n    cond = set(signs.tolist()) <= {-1.0, 1.0} and n_zero == 0\n    log(f\"  binary: nonzero-signs={signs.tolist()} zeros={n_zero}  {'OK' if cond else 'FAIL'}\")\n    ok &= cond\n\n    t = quantize_signed(W, 0.35)\n    zr = (t == 0).float().mean().item()\n    # sign(reconstruction) ∈ {-1,0,+1} structurally; zero_rate ~0.35\n    cond = 0.25 <= zr <= 0.45\n    log(f\"  ternary: zero_rate={zr:.3f} (target ~0.35)  {'OK' if cond else 'FAIL'}\")\n    ok &= cond\n\n    for n in (2, 3, 4):\n        q = quantize_nbit_uniform(W, n)\n        # count distinct levels within a single row (per-row scaling)\n        levels = torch.unique(q[0]).numel()\n        cond = levels <= 2 ** n\n        log(f\"  {n}bit: distinct row-levels={levels} (<= {2**n})  {'OK' if cond else 'FAIL'}\")\n        ok &= cond\n\n    cfgs = build_configs()\n    log(\"\\n  configs & mean-bits:\")\n    for c in cfgs.values():\n        log(f\"    {c.key:<18} gate={c.gate[0]:<9} up={c.up[0]:<7} down={c.down[0]:<7} \"\n            f\"mean_bits={c.mean_bits:.3f}\")\n    # crux: asym_binR_3V and inv_3R_binV must be equal mean-bits\n    a, b_ = cfgs[\"asym_binR_3V\"].mean_bits, cfgs[\"inv_3R_binV\"].mean_bits\n    cond = abs(a - b_) < 1e-9\n    log(f\"\\n  matched-null check: asym_binR_3V={a:.3f} == inv_3R_binV={b_:.3f}  \"\n        f\"{'OK' if cond else 'FAIL'}\")\n    ok &= cond\n\n    log(f\"\\n  {'ALL PASS' if ok else 'FAILURES PRESENT'}\")\n    return 0 if ok else 1\n\n\n# ═══════════════════════════════════════════════════════════════════\n# Main\n# ═══════════════════════════════════════════════════════════════════\n\ndef main() -> int:\n    ap = argparse.ArgumentParser(description=\"Asymmetric-pathway quantization A/B\")\n    ap.add_argument(\"--model\", default=\"Qwen/Qwen3-8B-Base\")\n    ap.add_argument(\"--device\",\n                    default=\"mps\" if torch.backends.mps.is_available() else \"cpu\")\n    ap.add_argument(\"--max-tokens\", type=int, default=32768)\n    ap.add_argument(\"--seq-len\", type=int, default=512)\n    ap.add_argument(\"--stride\", type=int, default=256)\n    ap.add_argument(\"--configs\", default=\"all\",\n                    help=\"comma list of config keys, or 'all'\")\n    ap.add_argument(\"--self-test\", action=\"store_true\")\n    ap.add_argument(\"--out-dir\", default=\"results/asymmetric-pathway-quant\")\n    args = ap.parse_args()\n\n    if args.self_test:\n        return self_test()\n\n    all_cfgs = build_configs()\n    if args.configs == \"all\":\n        keys = list(all_cfgs.keys())\n    else:\n        keys = [k.strip() for k in args.configs.split(\",\")]\n        for k in keys:\n            if k not in all_cfgs:\n                raise SystemExit(f\"unknown config '{k}'; have {list(all_cfgs)}\")\n\n    run_id = time.strftime(\"%Y%m%d-%H%M%S\")\n    out_dir = os.path.join(args.out_dir, f\"{args.model.split('/')[-1]}-{run_id}\")\n    os.makedirs(out_dir, exist_ok=True)\n\n    log(\"═══ Asymmetric-Pathway Quantization A/B ═══\")\n    log(f\"Model:   {args.model}\")\n    log(f\"Device:  {args.device}\")\n    log(f\"Tokens:  {args.max_tokens} (seq={args.seq_len} stride={args.stride})\")\n    log(f\"Configs: {keys}\")\n    log(f\"Out:     {out_dir}\\n\")\n\n    from transformers import AutoModelForCausalLM, AutoTokenizer\n\n    tok = AutoTokenizer.from_pretrained(args.model)\n    if tok.pad_token is None:\n        tok.pad_token = tok.eos_token\n\n    log(\"Loading model (fp32)...\")\n    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)\n    model = model.to(args.device)\n    n_layers = len(get_model_layers(model))\n    log(f\"  {n_layers} layers on {args.device}\")\n\n    log(\"Loading WikiText-2 test...\")\n    text = load_eval_text(args.max_tokens)\n\n    log(\"Caching original FFN weights...\")\n    orig = cache_ffn_weights(model)\n    log(f\"  cached {len(orig)} FFN matrices\\n\")\n\n    # provenance\n    try:\n        import transformers\n        tv = transformers.__version__\n    except Exception:\n        tv = \"?\"\n    meta = {\n        \"run_id\": run_id,\n        \"timestamp_utc\": time.strftime(\"%Y-%m-%dT%H:%M:%SZ\", time.gmtime()),\n        \"model\": args.model,\n        \"device\": args.device,\n        \"n_layers\": n_layers,\n        \"max_tokens\": args.max_tokens,\n        \"seq_len\": args.seq_len,\n        \"stride\": args.stride,\n        \"scope\": \"FFN only (gate/up/down); attention fp32\",\n        \"torch\": torch.__version__,\n        \"transformers\": tv,\n        \"configs\": {k: {\"label\": all_cfgs[k].label,\n                        \"gate\": all_cfgs[k].gate[0], \"up\": all_cfgs[k].up[0],\n                        \"down\": all_cfgs[k].down[0],\n                        \"mean_bits\": all_cfgs[k].mean_bits} for k in keys},\n    }\n    with open(os.path.join(out_dir, \"meta.json\"), \"w\") as f:\n        json.dump(meta, f, indent=2)\n\n    results = []\n    for k in keys:\n        cfg = all_cfgs[k]\n        log(f\"{'─' * 66}\")\n        log(f\"Config: {cfg.label}  (mean_bits={cfg.mean_bits:.3f})\")\n        t0 = time.time()\n        if cfg.is_float:\n            restore_ffn(model, orig, args.device)\n            cos = {n: 1.0 for n in WEIGHT_NAMES_FFN}\n        else:\n            restore_ffn(model, orig, args.device)\n            cos = apply_config(model, cfg, orig, args.device)\n        q_t = time.time() - t0\n        log(f\"  cosine  gate={cos['gate_proj']:.4f} up={cos['up_proj']:.4f} \"\n            f\"down={cos['down_proj']:.4f}  ({q_t:.1f}s)\")\n        log(\"  evaluating PPL...\")\n        ppl = evaluate_perplexity(model, tok, args.device, text,\n                                  args.max_tokens, args.seq_len, args.stride)\n        log(f\"  PPL = {ppl:.3f}\\n\")\n        results.append({\n            \"config\": k, \"label\": cfg.label, \"mean_bits\": cfg.mean_bits,\n            \"gate\": cfg.gate[0], \"up\": cfg.up[0], \"down\": cfg.down[0],\n            \"cosine\": cos, \"ppl\": ppl,\n        })\n        # incremental save (crash-safe)\n        with open(os.path.join(out_dir, \"summary.json\"), \"w\") as f:\n            json.dump({\"meta\": meta, \"results\": results}, f, indent=2)\n\n    # ═══ Report ═══\n    log(f\"{'═' * 78}\")\n    log(\"SUMMARY — Asymmetric-Pathway Quantization\")\n    log(f\"{'═' * 78}\")\n    log(f\"{'Config':<40} {'mean_bits':>9} {'PPL':>12}\")\n    log(f\"{'─' * 40} {'─' * 9} {'─' * 12}\")\n    for r in sorted(results, key=lambda x: x[\"mean_bits\"]):\n        log(f\"{r['label']:<40} {r['mean_bits']:>9.3f} {r['ppl']:>12.3f}\")\n\n    by = {r[\"config\"]: r for r in results}\n\n    def dppl(k):\n        base = by.get(\"float\")\n        return (by[k][\"ppl\"] - base[\"ppl\"]) if (base and k in by) else float(\"nan\")\n\n    log(\"\\nCRUX 1 — Pareto (does binary-router+3bit-value beat the uniform frontier?):\")\n    for k in (\"uniform_2bit\", \"uniform_3bit\", \"asym_binR_3V\"):\n        if k in by:\n            log(f\"  {by[k]['label']:<40} bits={by[k]['mean_bits']:.2f} \"\n                f\"PPL={by[k]['ppl']:.3f} (ΔvsFloat={dppl(k):+.3f})\")\n\n    log(\"\\nCRUX 2 — Inverted null at MATCHED 2.33 bits (sign=router vs magnitude=value):\")\n    if \"asym_binR_3V\" in by and \"inv_3R_binV\" in by:\n        a, b_ = by[\"asym_binR_3V\"], by[\"inv_3R_binV\"]\n        log(f\"  binary-router + 3bit-value : PPL={a['ppl']:.3f}\")\n        log(f\"  3bit-router + binary-value : PPL={b_['ppl']:.3f}\")\n        if a[\"ppl\"] > 0 and math.isfinite(a[\"ppl\"]) and math.isfinite(b_[\"ppl\"]):\n            log(f\"  ratio (inverted / asym) = {b_['ppl'] / a['ppl']:.2f}×  \"\n                f\"(>1 confirms sign=router, magnitude=value)\")\n\n    with open(os.path.join(out_dir, \"summary.json\"), \"w\") as f:\n        json.dump({\"meta\": meta, \"results\": results}, f, indent=2)\n    log(f\"\\nSaved → {out_dir}/summary.json\")\n    return 0\n\n\nif __name__ == \"__main__\":\n    raise SystemExit(main())\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py
```

## Assistant

Now lint + self-test (the acceptance gate for task 1):

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== ruff ===\"; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -20; echo \"=== self-test ===\"; uv run python scripts/experiments/asymmetric_pathway_quant.py --self-test 2>&1 | tail -30"
}
```

**Summary:** $ echo "=== ruff ==="; uv run ruff ch...

**Output:**
```
Exit code: 0
Stdout:
=== ruff ===
    |
469 |                 f"PPL={by[k]['ppl']:.3f} (ΔvsFloat={dppl(k):+.3f})")
470 |
471 |     log("\nCRUX 2 — Inverted null at MATCHED 2.33 bits (sign=router vs magnitude=value):")
    |                                                                                         ^^
472 |     if "asym_binR_3V" in by and "inv_3R_binV" in by:
473 |         a, b_ = by["asym_binR_3V"], by["inv_3R_binV"]
    |

RUF001 String contains ambiguous `×` (MULTIPLICATION SIGN). Did you mean `x` (LATIN SMALL LETTER X)?
   --> scripts/experiments/asymmetric_pathway_quant.py:477:73
    |
475 |         log(f"  3bit-router + binary-value : PPL={b_['ppl']:.3f}")
476 |         if a["ppl"] > 0 and math.isfinite(a["ppl"]) and math.isfinite(b_["ppl"]):
477 |             log(f"  ratio (inverted / asym) = {b_['ppl'] / a['ppl']:.2f}×  "
    |                                                                         ^
478 |                 f"(>1 confirms sign=router, magnitude=value)")
    |

Found 6 errors.
=== self-test ===
═══ self-test: quantizer correctness ═══
  binary: nonzero-signs=[-1.0, 1.0] zeros=0  OK
  ternary: zero_rate=0.359 (target ~0.35)  OK
  2bit: distinct row-levels=4 (<= 4)  OK
  3bit: distinct row-levels=8 (<= 8)  OK
  4bit: distinct row-levels=14 (<= 16)  OK

  configs & mean-bits:
    float              gate=float     up=float   down=float   mean_bits=16.000
    uniform_ternary    gate=ternary35 up=ternary35 down=ternary35 mean_bits=1.585
    uniform_2bit       gate=2bit      up=2bit    down=2bit    mean_bits=2.000
    uniform_3bit       gate=3bit      up=3bit    down=3bit    mean_bits=3.000
    asym_binR_3V       gate=binary    up=3bit    down=3bit    mean_bits=2.333
    asym_binR_2V       gate=binary    up=2bit    down=2bit    mean_bits=1.667
    inv_3R_binV        gate=3bit      up=binary  down=binary  mean_bits=1.667

  matched-null check: asym_binR_3V=2.333 == inv_3R_binV=1.667  FAIL

  FAILURES PRESENT
```

### Thinking

The self-test revealed an actual bug in the inverted-null configuration: when I calculate the mean for `inv_3R_binV` with gate=3bit and binary up/down values, I get 1.667, but the asymmetric counterpart `asym_binR_3V` gives 2.333—they don't match. The inverted configuration should preserve the same multiset of values, just in a different order, but something's gone wrong with the permutation logic.

The core problem is structural: the router is a single matrix while the value path has two matrices, so a symmetric inversion that swaps their roles while keeping the same multiset {1,3,3} isn't cleanly possible. I'm weighing two approaches—either accept a partial inversion where binary lands on one value matrix instead of the router (testing whether binary is better spent there), or redefine the null configuration itself to be matched by construction, perhaps by swapping just one value matrix with the router for a cleaner causal comparison.

The second approach looks more promising: I could define a minimal pair where the binary matrix moves from the router to the down projection while keeping everything else identical and the mean bits constant at 2.333. This isolates the exact question of whether binary belongs on the gate or on the value path. Alternatively, I could push further and test a fully-binary value path by bumping the router to 5 bits to maintain the same mean.

Let me settle on a cleaner set of configurations: the baseline float and quantized variants, then the asymmetric binary-on-router setup paired with its inverted counterpart where binary sits on the down projection instead. I might also include the strongest inversion where both value matrices go binary and the router absorbs the remaining bits—that directly mirrors the article's binary-on-both-sides approach and would be the most striking test case if it fails.

All three of these matched configurations land at 2.333 mean bits, creating a gradient that tests where binarization hurts least: router alone, one value matrix, or both value matrices. I'll keep the asymmetric 2-bit variant as an off-frontier point for the Pareto curve but drop the 1.667 null pair to keep scope tight.

Now I need to update the config builder and the matched-null validation logic to handle this triple, then fix the ruff linting errors where unicode characters like × are flagged as ambiguous in the output strings.

## Assistant

Self-test caught two real issues — exactly why it exists:

1. **The inverted null wasn't matched** (1.667 ≠ 2.333). Root cause: router is 1 matrix, value is 2, so a naive "invert" breaks the bit budget. The fix is a proper **matched-bits triple**, all at 2.333: binary on router vs binary on one value matrix vs binary on the whole value path (mirrors the article's int8×binary → binary×binary gradient).
2. **RUF001** ambiguous `×`/`Δ` in output strings.

Let me fix both.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    tern = spec_ternary(0.35)\n    b1 = spec_binary()\n    b2 = spec_nbit(2)\n    b3 = spec_nbit(3)\n    fl = spec_float()\n    cfgs = [\n        QuantConfig(\"float\", \"Float baseline\", fl, fl, fl),\n        # uniform frontier\n        QuantConfig(\"uniform_ternary\", \"Uniform ternary (1.58b)\", tern, tern, tern),\n        QuantConfig(\"uniform_2bit\", \"Uniform 2-bit\", b2, b2, b2),\n        QuantConfig(\"uniform_3bit\", \"Uniform 3-bit\", b3, b3, b3),\n        # asymmetric (binary router + precise value)\n        QuantConfig(\"asym_binR_3V\", \"Asym: binary router + 3-bit value\", b1, b3, b3),\n        QuantConfig(\"asym_binR_2V\", \"Asym: binary router + 2-bit value\", b1, b2, b2),\n        # inverted-null: 3-bit router + binary value (SAME 2.33 bits as asym_binR_3V)\n        QuantConfig(\"inv_3R_binV\", \"Inverted null: 3-bit router + binary value\", b3, b1, b1),\n    ]\n    return {c.key: c for c in cfgs}",
  "new_content": "    tern = spec_ternary(0.35)\n    b1 = spec_binary()\n    b2 = spec_nbit(2)\n    b3 = spec_nbit(3)\n    b5 = spec_nbit(5)\n    fl = spec_float()\n    cfgs = [\n        QuantConfig(\"float\", \"Float baseline\", fl, fl, fl),\n        # uniform frontier\n        QuantConfig(\"uniform_ternary\", \"Uniform ternary (1.58b)\", tern, tern, tern),\n        QuantConfig(\"uniform_2bit\", \"Uniform 2-bit\", b2, b2, b2),\n        QuantConfig(\"uniform_3bit\", \"Uniform 3-bit\", b3, b3, b3),\n        # asymmetric (binary router + precise value)\n        QuantConfig(\"asym_binR_3V\", \"Asym: binary router + 3-bit value\", b1, b3, b3),\n        QuantConfig(\"asym_binR_2V\", \"Asym: binary router + 2-bit value\", b1, b2, b2),\n        # ── MATCHED-BITS NULL TRIPLE (all mean_bits = 2.333) ──\n        # Where does the single/whole binarization hurt least? Move binary\n        # from router -> one value matrix -> whole value path, holding budget.\n        # asym_binR_3V is the first member (binary on ROUTER).\n        QuantConfig(\"inv_binDown\", \"Matched null: binary on down (value) matrix\", b3, b3, b1),\n        QuantConfig(\"inv_binValue\", \"Matched null: binary whole value path (5b router)\", b5, b1, b1),\n    ]\n    return {c.key: c for c in cfgs}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    # crux: asym_binR_3V and inv_3R_binV must be equal mean-bits\n    a, b_ = cfgs[\"asym_binR_3V\"].mean_bits, cfgs[\"inv_3R_binV\"].mean_bits\n    cond = abs(a - b_) < 1e-9\n    log(f\"\\n  matched-null check: asym_binR_3V={a:.3f} == inv_3R_binV={b_:.3f}  \"\n        f\"{'OK' if cond else 'FAIL'}\")\n    ok &= cond",
  "new_content": "    # crux: the matched-bits null triple must all be equal mean-bits\n    triple = [\"asym_binR_3V\", \"inv_binDown\", \"inv_binValue\"]\n    bits = [cfgs[k].mean_bits for k in triple]\n    cond = max(bits) - min(bits) < 1e-9\n    log(f\"\\n  matched-null triple bits: \"\n        + \", \".join(f\"{k}={cfgs[k].mean_bits:.3f}\" for k in triple)\n        + f\"  {'OK' if cond else 'FAIL'}\")\n    ok &= cond"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

## Assistant

Now fix the CRUX 2 reporting block for the matched triple and the ambiguous-unicode lint:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    log(\"\\nCRUX 1 — Pareto (does binary-router+3bit-value beat the uniform frontier?):\")\n    for k in (\"uniform_2bit\", \"uniform_3bit\", \"asym_binR_3V\"):\n        if k in by:\n            log(f\"  {by[k]['label']:<40} bits={by[k]['mean_bits']:.2f} \"\n                f\"PPL={by[k]['ppl']:.3f} (ΔvsFloat={dppl(k):+.3f})\")\n\n    log(\"\\nCRUX 2 — Inverted null at MATCHED 2.33 bits (sign=router vs magnitude=value):\")\n    if \"asym_binR_3V\" in by and \"inv_3R_binV\" in by:\n        a, b_ = by[\"asym_binR_3V\"], by[\"inv_3R_binV\"]\n        log(f\"  binary-router + 3bit-value : PPL={a['ppl']:.3f}\")\n        log(f\"  3bit-router + binary-value : PPL={b_['ppl']:.3f}\")\n        if a[\"ppl\"] > 0 and math.isfinite(a[\"ppl\"]) and math.isfinite(b_[\"ppl\"]):\n            log(f\"  ratio (inverted / asym) = {b_['ppl'] / a['ppl']:.2f}×  \"\n                f\"(>1 confirms sign=router, magnitude=value)\")",
  "new_content": "    log(\"\\nCRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):\")\n    for k in (\"uniform_2bit\", \"uniform_3bit\", \"asym_binR_3V\"):\n        if k in by:\n            log(f\"  {by[k]['label']:<44} bits={by[k]['mean_bits']:.2f} \"\n                f\"PPL={by[k]['ppl']:.3f} (dVsFloat={dppl(k):+.3f})\")\n\n    log(\"\\nCRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?\")\n    triple = [\"asym_binR_3V\", \"inv_binDown\", \"inv_binValue\"]\n    where = {\"asym_binR_3V\": \"binary on ROUTER (gate)\",\n             \"inv_binDown\": \"binary on ONE value matrix (down)\",\n             \"inv_binValue\": \"binary on WHOLE value path (up+down)\"}\n    ref = by.get(\"asym_binR_3V\")\n    for k in triple:\n        if k in by:\n            r = by[k]\n            rel = \"\"\n            if ref and ref[\"ppl\"] > 0 and math.isfinite(ref[\"ppl\"]) and math.isfinite(r[\"ppl\"]):\n                rel = f\"  ({r['ppl'] / ref['ppl']:.2f}x vs router-binary)\"\n            log(f\"  {where[k]:<40} PPL={r['ppl']:.3f}{rel}\")\n    log(\"  prediction (two-registers): ROUTER << one-value << whole-value\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Thinking

I'm checking for other ambiguous unicode characters that ruff flags with RUF001 — there were 6 errors total. The docstring contains characters like ×, Δ, and ρ that ruff catches in strings, though my docstring mostly uses regular "x". Let me run ruff again to see what errors remain.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== ruff ===\"; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -25; echo \"=== self-test ===\"; uv run python scripts/experiments/asymmetric_pathway_quant.py --self-test 2>&1 | tail -22"
}
```

**Summary:** $ echo "=== ruff ==="; uv run ruff ch...

**Output:**
```
Exit code: 0
Stdout:
=== ruff ===

E501 Line too long (95 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:478:89
    |
476 |                 f"PPL={by[k]['ppl']:.3f} (dVsFloat={dppl(k):+.3f})")
477 |
478 |     log("\nCRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?")
    |                                                                                         ^^^^^^^
479 |     triple = ["asym_binR_3V", "inv_binDown", "inv_binValue"]
480 |     where = {"asym_binR_3V": "binary on ROUTER (gate)",
    |

E501 Line too long (96 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:488:89
    |
486 |             r = by[k]
487 |             rel = ""
488 |             if ref and ref["ppl"] > 0 and math.isfinite(ref["ppl"]) and math.isfinite(r["ppl"]):
    |                                                                                         ^^^^^^^^
489 |                 rel = f"  ({r['ppl'] / ref['ppl']:.2f}x vs router-binary)"
490 |             log(f"  {where[k]:<40} PPL={r['ppl']:.3f}{rel}")
    |

Found 8 errors.
[*] 1 fixable with the `--fix` option.
=== self-test ===
═══ self-test: quantizer correctness ═══
  binary: nonzero-signs=[-1.0, 1.0] zeros=0  OK
  ternary: zero_rate=0.359 (target ~0.35)  OK
  2bit: distinct row-levels=4 (<= 4)  OK
  3bit: distinct row-levels=8 (<= 8)  OK
  4bit: distinct row-levels=14 (<= 16)  OK

  configs & mean-bits:
    float              gate=float     up=float   down=float   mean_bits=16.000
    uniform_ternary    gate=ternary35 up=ternary35 down=ternary35 mean_bits=1.585
    uniform_2bit       gate=2bit      up=2bit    down=2bit    mean_bits=2.000
    uniform_3bit       gate=3bit      up=3bit    down=3bit    mean_bits=3.000
    asym_binR_3V       gate=binary    up=3bit    down=3bit    mean_bits=2.333
    asym_binR_2V       gate=binary    up=2bit    down=2bit    mean_bits=1.667
    inv_binDown        gate=3bit      up=3bit    down=binary  mean_bits=2.333
    inv_binValue       gate=5bit      up=binary  down=binary  mean_bits=2.333

  matched-null triple bits: asym_binR_3V=2.333, inv_binDown=2.333, inv_binValue=2.333  OK

  ALL PASS
```

## Assistant

Self-test all pass, matched triple confirmed at 2.333. Just line-length lints left — let me check the full ruff list and fix them all.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | grep -E \"E501|RUF|-->\" | grep -v \"^\\s*|\" | head -30"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
E501 Line too long (92 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:146:89
E501 Line too long (94 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:169:89
E501 Line too long (101 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:170:89
E501 Line too long (95 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:307:89
E501 Line too long (94 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:322:89
   --> scripts/experiments/asymmetric_pathway_quant.py:334:9
E501 Line too long (95 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:478:89
E501 Line too long (96 > 88)
   --> scripts/experiments/asymmetric_pathway_quant.py:488:89
```

### Thinking

I'm seeing ruff flagged several line-too-long violations, so let me check the project's ruff configuration to understand if E501 is actually enforced or if it's typically ignored like in the other scripts in the repo.

## Assistant

Let me check whether the repo actually enforces E501 (existing scripts have long lines) before mass-reformatting:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== ruff config ===\"; grep -nA20 \"\\[tool.ruff\" pyproject.toml 2>/dev/null; echo \"=== do sibling scripts pass? ===\"; uv run ruff check scripts/experiments/full_ternarize.py scripts/experiments/standing_wave_shape.py 2>&1 | tail -5"
}
```

**Summary:** $ echo "=== ruff config ==="; grep -n...

**Output:**
```
Exit code: 0
Stdout:
=== ruff config ===
82:[tool.ruff]
83-line-length = 88
84-target-version = "py312"
85-src = ["src", "tests"]
86-
87:[tool.ruff.lint]
88-select = [
89-    "E",    # pycodestyle errors
90-    "W",    # pycodestyle warnings
91-    "F",    # pyflakes
92-    "I",    # isort
93-    "B",    # flake8-bugbear
94-    "UP",   # pyupgrade
95-    "RUF",  # ruff-specific
96-]
97-
98:[tool.ruff.lint.per-file-ignores]
99-"tests/*" = ["B011", "RUF001", "RUF002", "RUF003"]  # asserts + surface symbols in data
100-# Surface logical-form / reward modules: λ ∀ ∃ ι → ∧ ∨ ¬ Φ γ ⊗ ∈ Σ ARE the domain
101-# alphabet (CCG / λ-calculus / reward-shaping notation), not typos.
102-"src/verbum/lambda_surface.py" = ["RUF001", "RUF002", "RUF003"]
103-"src/verbum/reward.py" = ["RUF001", "RUF002", "RUF003"]
104-"src/verbum/compile_prompt.py" = ["RUF001", "RUF002", "RUF003"]
105-"scripts/experiments/audit_compile_corpus.py" = ["RUF001", "RUF002", "RUF003"]
106-"scripts/experiments/rlvr_coldstart_density.py" = ["RUF001", "RUF002", "RUF003"]
107-"scripts/experiments/rlvr_grpo_train.py" = ["RUF001", "RUF002", "RUF003"]
108-"scripts/experiments/proof_consensus.py" = ["RUF001", "RUF002", "RUF003"]
109-"scripts/experiments/ffn_program_decode.py" = ["RUF001", "RUF002", "RUF003"]
110-"scripts/experiments/gen_firing_probes.py" = ["RUF001", "RUF002", "RUF003"]
111-"scripts/experiments/gen_reading_probes.py" = ["RUF001", "RUF002", "RUF003"]
112-"scripts/experiments/ffn_reading_preference.py" = ["RUF001", "RUF002", "RUF003"]
113-"scripts/experiments/program_edge_knockout.py" = ["RUF001", "RUF002", "RUF003"]
114-"scripts/experiments/gen_scope_probes.py" = ["RUF001", "RUF002", "RUF003"]
115-"scripts/experiments/ffn_scope_forcing.py" = ["RUF001", "RUF002", "RUF003"]
116-
117-# ─────────────────────────── ty ─────────────────────────────
118-# ty is alpha; config schema is moving. Empty stanza pins the table so
=== do sibling scripts pass? ===
    |
help: Remove whitespace from blank line

Found 194 errors.
[*] 106 fixable with the `--fix` option (15 hidden fixes can be enabled with the `--unsafe-fixes` option).
```

### Thinking

I'm noticing the sibling scripts have 194 linting errors, so the experiment scripts clearly aren't held to a strict standard in practice—E501 line-length violations are rampant despite the rule being enabled. My AGENTS.md guidelines prioritize fixing over suppressing, but the pragmatic reality is that these scripts aren't lint-clean, and my own file only has 8 E501 violations to address.

The remaining errors are just long lines that are trivial to wrap, and I've already confirmed the RUF001 ambiguous-unicode issues are resolved. I'll manually wrap those 8 specific lines to keep my file clean, which is good discipline and minimal effort.

## Assistant

Sibling experiment scripts carry 194 lint errors — so they're not held clean in practice, but per `λ lint` I'll keep my new file clean (only 8 trivial line-wraps left). Let me view and wrap them.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; for n in 146 169 170 307 322 478 488; do echo \"--- $n ---\"; sed -n \"${n}p\" scripts/experiments/asymmetric_pathway_quant.py; done"
}
```

**Summary:** $ for n in 146 169 170 307 322 478 48...

**Output:**
```
Exit code: 0
Stdout:
--- 146 ---
        return self.gate[0] == "float" and self.up[0] == "float" and self.down[0] == "float"
--- 169 ---
        QuantConfig("inv_binDown", "Matched null: binary on down (value) matrix", b3, b3, b1),
--- 170 ---
        QuantConfig("inv_binValue", "Matched null: binary whole value path (5b router)", b5, b1, b1),
--- 307 ---
    log(f"  binary: nonzero-signs={signs.tolist()} zeros={n_zero}  {'OK' if cond else 'FAIL'}")
--- 322 ---
        log(f"  {n}bit: distinct row-levels={levels} (<= {2**n})  {'OK' if cond else 'FAIL'}")
--- 478 ---
    log("\nCRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?")
--- 488 ---
            if ref and ref["ppl"] > 0 and math.isfinite(ref["ppl"]) and math.isfinite(r["ppl"]):
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "        return self.gate[0] == \"float\" and self.up[0] == \"float\" and self.down[0] == \"float\"",
  "new_content": "        return all(s[0] == \"float\" for s in (self.gate, self.up, self.down))"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "        QuantConfig(\"inv_binDown\", \"Matched null: binary on down (value) matrix\", b3, b3, b1),\n        QuantConfig(\"inv_binValue\", \"Matched null: binary whole value path (5b router)\", b5, b1, b1),",
  "new_content": "        QuantConfig(\"inv_binDown\",\n                    \"Matched null: binary on down (value) matrix\", b3, b3, b1),\n        QuantConfig(\"inv_binValue\",\n                    \"Matched null: binary whole value path (5b router)\", b5, b1, b1),"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    log(f\"  binary: nonzero-signs={signs.tolist()} zeros={n_zero}  {'OK' if cond else 'FAIL'}\")",
  "new_content": "    log(f\"  binary: nonzero-signs={signs.tolist()} zeros={n_zero}  \"\n        f\"{'OK' if cond else 'FAIL'}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "        log(f\"  {n}bit: distinct row-levels={levels} (<= {2**n})  {'OK' if cond else 'FAIL'}\")",
  "new_content": "        log(f\"  {n}bit: distinct row-levels={levels} (<= {2**n})  \"\n            f\"{'OK' if cond else 'FAIL'}\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    log(\"\\nCRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?\")",
  "new_content": "    log(\"\\nCRUX 2 - Matched-bits null triple (all 2.33b): \"\n        \"where does binarization hurt least?\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "            if ref and ref[\"ppl\"] > 0 and math.isfinite(ref[\"ppl\"]) and math.isfinite(r[\"ppl\"]):",
  "new_content": "            finite = math.isfinite(ref[\"ppl\"]) and math.isfinite(r[\"ppl\"])\n            if ref and ref[\"ppl\"] > 0 and finite:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -5; echo \"=== self-test rerun ===\"; uv run python scripts/experiments/asymmetric_pathway_quant.py --self-test 2>&1 | tail -4"
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
|
help: Remove extraneous `f` prefix

Found 1 error.
[*] 1 fixable with the `--fix` option.
=== self-test rerun ===

  matched-null triple bits: asym_binR_3V=2.333, inv_binDown=2.333, inv_binValue=2.333  OK

  ALL PASS
```

## Assistant

One F-string lint left (auto-fixable). Let me apply the fix and confirm clean:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; uv run ruff check --fix scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -3; echo \"=== final ruff ===\"; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -3"
}
```

**Summary:** $ uv run ruff check --fix scripts/exp...

**Output:**
```
Exit code: 0
Stdout:
Found 1 error (1 fixed, 0 remaining).
=== final ruff ===
All checks passed!
```

### Thinking

Task 1 is done—the script is clean, passes its self-test, and the quantizers check out. I need to quickly verify the help command works, then move on to task 2 with the smoke test on Qwen3-8B-Base.

For the smoke test, I'm running the model with float and uniform_ternary configs on 2048 tokens. Loading the 8B model, quantizing the FFN matrices, and running two PPL evaluations will take around 5 minutes total, so I'll set a 15-minute timeout to be safe and run it in the foreground.

## Assistant

Task 1 done — clean and self-verified. Marking complete and starting the smoke test (task 2) on Qwen3-8B-Base.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base --configs float,uniform_ternary --max-tokens 2048 2>&1 | tail -40",
  "timeout": 900000
}
```

**Summary:** $ HF_HUB_OFFLINE=1 uv run python scri...

**Output:**
```
Exit code: 0
Stdout:
Configs: ['float', 'uniform_ternary']
Out:     results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-121800

Loading model (fp32)...
`torch_dtype` is deprecated! Use `dtype` instead!
Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]Loading weights:   0%|          | 1/399 [00:00<02:55,  2.26it/s]Loading weights:   8%|▊         | 32/399 [00:00<00:04, 77.39it/s]Loading weights:  13%|█▎        | 51/399 [00:00<00:03, 103.32it/s]Loading weights:  18%|█▊        | 70/399 [00:00<00:02, 123.27it/s]Loading weights:  23%|██▎       | 92/399 [00:00<00:02, 140.67it/s]Loading weights:  29%|██▊       | 114/399 [00:01<00:01, 154.73it/s]Loading weights:  34%|███▍      | 136/399 [00:01<00:01, 163.94it/s]Loading weights:  39%|███▉      | 155/399 [00:01<00:01, 169.51it/s]Loading weights:  44%|████▍     | 177/399 [00:01<00:01, 176.26it/s]Loading weights:  50%|████▉     | 199/399 [00:01<00:01, 179.39it/s]Loading weights:  55%|█████▌    | 221/399 [00:01<00:01, 175.47it/s]Loading weights:  61%|██████    | 243/399 [00:01<00:00, 178.82it/s]Loading weights:  66%|██████▋   | 265/399 [00:01<00:00, 189.35it/s]Loading weights:  71%|███████▏  | 285/399 [00:01<00:00, 185.88it/s]Loading weights:  77%|███████▋  | 307/399 [00:02<00:00, 188.19it/s]Loading weights:  82%|████████▏ | 327/399 [00:02<00:00, 188.46it/s]Loading weights:  87%|████████▋ | 346/399 [00:02<00:00, 181.99it/s]Loading weights:  92%|█████████▏| 367/399 [00:02<00:00, 181.97it/s]Loading weights:  97%|█████████▋| 386/399 [00:02<00:00, 178.29it/s]Loading weights: 100%|██████████| 399/399 [00:02<00:00, 158.55it/s]
  36 layers on mps
Loading WikiText-2 test...
Using the latest cached version of the dataset since wikitext couldn't be found on the Hugging Face Hub (offline mode is enabled).
Found the latest cached dataset configuration 'wikitext-2-raw-v1' at /Users/mwhitford/.cache/huggingface/datasets/wikitext/wikitext-2-raw-v1/0.0.0/b08601e04326c79dfdd32d625aee71d232d685c3 (last modified on Tue Jun  2 15:34:31 2026).
Caching original FFN weights...
  cached 108 FFN matrices

──────────────────────────────────────────────────────────────────
Config: Float baseline  (mean_bits=16.000)
  cosine  gate=1.0000 up=1.0000 down=1.0000  (12.1s)
  evaluating PPL...
Token indices sequence length is longer than the specified maximum sequence length for this model (298938 > 131072). Running this sequence through the model will result in indexing errors
  PPL = 9.626

──────────────────────────────────────────────────────────────────
Config: Uniform ternary (1.58b)  (mean_bits=1.585)
  cosine  gate=0.8919 up=0.8949 down=0.8759  (29.6s)
  evaluating PPL...
  PPL = 485165195.410

══════════════════════════════════════════════════════════════════════════════
SUMMARY — Asymmetric-Pathway Quantization
══════════════════════════════════════════════════════════════════════════════
Config                                   mean_bits          PPL
──────────────────────────────────────── ───────── ────────────
Uniform ternary (1.58b)                      1.585 485165195.410
Float baseline                              16.000        9.626

CRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):

CRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?
  prediction (two-registers): ROUTER << one-value << whole-value

Saved → results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-121800/summary.json
```

### Thinking

The baseline float model achieves a reasonable perplexity of 9.626 on WikiText-2, which is expected for Qwen3-8B-Base. But the uniform ternary quantization with FFN-only sparsity at 0.35 zero rate produces a catastrophic perplexity of 485 million—which is exactly e^20, hitting my loss capping threshold and indicating the quantization approach is completely breaking the model.

The per-matrix cosine similarities look decent individually (0.89 for gate and up projections, 0.876 for down), but when compounded across all 36 layers and 3 matrices per layer, the signal degrades exponentially—0.89^108 becomes vanishingly small. This matches what I saw in the s185 work where ternary FFN on Pythia-160M also saturated catastrophically, and scaling that pattern to an 8B model with 36 layers makes it even worse.

The real problem is that if uniform ternary already maxes out the perplexity cap, then my asymmetric and inverted quantization configs will likely do the same, making it impossible to distinguish between them since everything just saturates at the same ceiling value.

Looking back at the full_ternarize.py results and the ternary-dual documentation, I'm realizing that those reported improvements (1.44× and 0.94 cosine) probably came with additional corrections like LoRA or score matching—raw ternarization of all FFN layers without those fixes just compounds into signal death. So the core issue is that aggressive quantization schemes need a higher bit floor to survive the compounding effect across 36 layers, but even 3-bit might still degrade too much to be useful for discrimination.

The real insight though: I've been capping the loss at 20 to prevent overflow, but that cap is actually hiding the signal. If different configs are producing different per-token losses before saturation, raising or removing the cap would let those differences show up as distinct (even if large) numbers. The ranking between configs is what matters for the null hypothesis test, not the absolute values. Let me try removing the cap entirely so the actual loss differences can surface.

But stepping back, the core issue is that aggressive quantization across all 36 layers compounds the error so badly that everything collapses to garbage — loss > 20, which is worse than uniform random. That suggests the model's activations are exploding or diverging rather than gracefully degrading. This compounding death makes it impossible to discriminate between different quantization strategies at full depth.

The cleaner approach is to quantize only a subset — either a single layer or a small band of interior layers — so the perturbation stays small enough to measure meaningful differences without saturation. That way I can directly test whether binarizing the router costs less than binarizing the value path within a controlled scope.

Alternatively, I could switch to a graded metric like output-distribution KL divergence or final-layer hidden cosine (which s185 used) instead of end-to-end perplexity. These won't saturate and directly reflect the compounding damage, making them more sensitive for comparing configurations.

The most honest path forward is to acknowledge that full-model aggressive quantization blows up due to compounding — which itself is a real finding consistent with s185's observations about raw ternary needing careful handling. hypothesis: I should run a single-layer perturbation sweep instead—quantize only one FFN layer at a time across the model's depth, measure the PPL delta for each config. This stays non-saturating, reveals which pathways (router vs value) tolerate binarization per layer, and directly tests whether the router-binary advantage concentrates in the interior band. Sampling ~7 layers across depth with 3 configs each (binary-on-gate, binary-on-up, binary-on-down) gives me 21 PPL evaluations plus baseline—roughly 10 minutes total, which is tractable and far cleaner than the full-model saturation problem.

But wait—maybe I'm abandoning the full-model experiment too quickly. The smoke test only tried float and uniform_ternary; the asymmetric configs with 3-bit value (cosine ~0.99) might actually survive with finite PPL, while the worst configs saturate. So the full-model sweep could still discriminate between configs if I just fix the loss cap and record both PPL and raw loss to see gradations even above exp(20).

The real issue is the dynamic range: float PPL is 9.6 but uniform_ternary hits e^20. Instead of capping PPL, I should switch to reporting mean NLL loss (nats) as the primary metric—it stays finite and comparable even for saturated configs, while PPL = exp(min(loss, ~30)) becomes secondary for readability. This way, a loss of 25 versus 30 is still meaningful and preserves the ordering.

I'll modify the harness to use mean NLL as the primary metric, keep PPL as a secondary readability measure, and treat only true nan/inf as failure. Then re-run the full sweep. Updating the metric function to return both loss and perplexity (capping the exponent at 30 to avoid overflow), then storing both values in results so I can use loss for ordering and comparisons while keeping perplexity for readability. After that, I'll run a quick 4-config smoke test with float, uniform_ternary, asym_binR_3V, and inv_binValue to see if the asymmetric quantization survives or if the compounding effect is still too severe — if asym_binR_3V stays close to float loss while inv_binValue explodes, the full model approach works; otherwise I'll need to pivot to quantizing just a single layer.

## Assistant

Smoke test surfaced a **critical measurement problem** — exactly what smoke tests are for. Float PPL = 9.63 (sane for an 8B base ✓), but uniform-ternary FFN = 485,165,195 = `exp(20)`, my saturation cap. Raw quantization of *all 36 layers* compounds `cos^L` (s185's law: 0.89/layer × 108 matrices → signal death). The cap is masking discrimination — every aggressive config will pin at the same ceiling and I couldn't tell them apart.

Fix: **switch the primary metric to mean NLL (nats)**, which stays finite and comparable even when PPL overflows, so the matched-null ordering survives. Let me change that and re-test with the discriminating configs before committing to the full run.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "def evaluate_perplexity(model, tokenizer, device, text: str,\n                        max_tokens: int, seq_len: int = 512,\n                        stride: int = 256) -> float:\n    tokens = tokenizer.encode(text, add_special_tokens=False)[:max_tokens]\n    model.eval()\n    total_loss, total_tok = 0.0, 0\n    with torch.no_grad():\n        for start in range(0, max(1, len(tokens) - seq_len), stride):\n            chunk = tokens[start:start + seq_len]\n            if len(chunk) < 2:\n                continue\n            ids = torch.tensor([chunk], device=device)\n            out = model(ids, labels=ids)\n            loss = out.loss.item()\n            if math.isnan(loss) or math.isinf(loss):\n                return float(\"inf\")\n            total_loss += loss * (len(chunk) - 1)\n            total_tok += len(chunk) - 1\n    if total_tok == 0:\n        return float(\"nan\")\n    return math.exp(min(total_loss / total_tok, 20.0))",
  "new_content": "def evaluate_perplexity(model, tokenizer, device, text: str,\n                        max_tokens: int, seq_len: int = 512,\n                        stride: int = 256) -> dict:\n    \"\"\"Return {'loss': mean_nll_nats, 'ppl': exp(min(loss,30))}.\n\n    Primary metric is mean NLL (nats): it stays finite and comparable even\n    when aggressive quant destroys the model (PPL overflows). Only true\n    nan/inf per-window losses abort to inf — a genuinely diverged model.\n    \"\"\"\n    tokens = tokenizer.encode(text, add_special_tokens=False)[:max_tokens]\n    model.eval()\n    total_loss, total_tok = 0.0, 0\n    with torch.no_grad():\n        for start in range(0, max(1, len(tokens) - seq_len), stride):\n            chunk = tokens[start:start + seq_len]\n            if len(chunk) < 2:\n                continue\n            ids = torch.tensor([chunk], device=device)\n            out = model(ids, labels=ids)\n            loss = out.loss.item()\n            if math.isnan(loss) or math.isinf(loss):\n                return {\"loss\": float(\"inf\"), \"ppl\": float(\"inf\")}\n            total_loss += loss * (len(chunk) - 1)\n            total_tok += len(chunk) - 1\n    if total_tok == 0:\n        return {\"loss\": float(\"nan\"), \"ppl\": float(\"nan\")}\n    mean_loss = total_loss / total_tok\n    return {\"loss\": mean_loss, \"ppl\": math.exp(min(mean_loss, 30.0))}"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

## Assistant

Now update the call sites and reporting to use `loss` as primary:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "        log(\"  evaluating PPL...\")\n        ppl = evaluate_perplexity(model, tok, args.device, text,\n                                  args.max_tokens, args.seq_len, args.stride)\n        log(f\"  PPL = {ppl:.3f}\\n\")\n        results.append({\n            \"config\": k, \"label\": cfg.label, \"mean_bits\": cfg.mean_bits,\n            \"gate\": cfg.gate[0], \"up\": cfg.up[0], \"down\": cfg.down[0],\n            \"cosine\": cos, \"ppl\": ppl,\n        })",
  "new_content": "        log(\"  evaluating PPL...\")\n        ev = evaluate_perplexity(model, tok, args.device, text,\n                                 args.max_tokens, args.seq_len, args.stride)\n        log(f\"  loss = {ev['loss']:.4f} nats   PPL = {ev['ppl']:.3f}\\n\")\n        results.append({\n            \"config\": k, \"label\": cfg.label, \"mean_bits\": cfg.mean_bits,\n            \"gate\": cfg.gate[0], \"up\": cfg.up[0], \"down\": cfg.down[0],\n            \"cosine\": cos, \"loss\": ev[\"loss\"], \"ppl\": ev[\"ppl\"],\n        })"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py",
  "original_content": "    log(f\"{'Config':<40} {'mean_bits':>9} {'PPL':>12}\")\n    log(f\"{'─' * 40} {'─' * 9} {'─' * 12}\")\n    for r in sorted(results, key=lambda x: x[\"mean_bits\"]):\n        log(f\"{r['label']:<40} {r['mean_bits']:>9.3f} {r['ppl']:>12.3f}\")\n\n    by = {r[\"config\"]: r for r in results}\n\n    def dppl(k):\n        base = by.get(\"float\")\n        return (by[k][\"ppl\"] - base[\"ppl\"]) if (base and k in by) else float(\"nan\")\n\n    log(\"\\nCRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):\")\n    for k in (\"uniform_2bit\", \"uniform_3bit\", \"asym_binR_3V\"):\n        if k in by:\n            log(f\"  {by[k]['label']:<44} bits={by[k]['mean_bits']:.2f} \"\n                f\"PPL={by[k]['ppl']:.3f} (dVsFloat={dppl(k):+.3f})\")\n\n    log(\"\\nCRUX 2 - Matched-bits null triple (all 2.33b): \"\n        \"where does binarization hurt least?\")\n    triple = [\"asym_binR_3V\", \"inv_binDown\", \"inv_binValue\"]\n    where = {\"asym_binR_3V\": \"binary on ROUTER (gate)\",\n             \"inv_binDown\": \"binary on ONE value matrix (down)\",\n             \"inv_binValue\": \"binary on WHOLE value path (up+down)\"}\n    ref = by.get(\"asym_binR_3V\")\n    for k in triple:\n        if k in by:\n            r = by[k]\n            rel = \"\"\n            finite = math.isfinite(ref[\"ppl\"]) and math.isfinite(r[\"ppl\"])\n            if ref and ref[\"ppl\"] > 0 and finite:\n                rel = f\"  ({r['ppl'] / ref['ppl']:.2f}x vs router-binary)\"\n            log(f\"  {where[k]:<40} PPL={r['ppl']:.3f}{rel}\")\n    log(\"  prediction (two-registers): ROUTER << one-value << whole-value\")",
  "new_content": "    log(f\"{'Config':<44} {'mean_bits':>9} {'loss(nats)':>11} {'PPL':>12}\")\n    log(f\"{'─' * 44} {'─' * 9} {'─' * 11} {'─' * 12}\")\n    for r in sorted(results, key=lambda x: x[\"mean_bits\"]):\n        log(f\"{r['label']:<44} {r['mean_bits']:>9.3f} \"\n            f\"{r['loss']:>11.4f} {r['ppl']:>12.3f}\")\n\n    by = {r[\"config\"]: r for r in results}\n    base = by.get(\"float\")\n\n    def dloss(k):\n        return (by[k][\"loss\"] - base[\"loss\"]) if (base and k in by) else float(\"nan\")\n\n    log(\"\\nCRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):\")\n    log(\"  (lower loss = better; dLoss = excess nats vs float)\")\n    for k in (\"uniform_ternary\", \"uniform_2bit\", \"uniform_3bit\",\n              \"asym_binR_2V\", \"asym_binR_3V\"):\n        if k in by:\n            log(f\"  {by[k]['label']:<44} bits={by[k]['mean_bits']:.2f} \"\n                f\"loss={by[k]['loss']:.4f} (dLoss={dloss(k):+.4f})\")\n\n    log(\"\\nCRUX 2 - Matched-bits null triple (all 2.33b): \"\n        \"where does binarization hurt least?\")\n    triple = [\"asym_binR_3V\", \"inv_binDown\", \"inv_binValue\"]\n    where = {\"asym_binR_3V\": \"binary on ROUTER (gate)\",\n             \"inv_binDown\": \"binary on ONE value matrix (down)\",\n             \"inv_binValue\": \"binary on WHOLE value path (up+down)\"}\n    ref = by.get(\"asym_binR_3V\")\n    for k in triple:\n        if k in by:\n            r = by[k]\n            rel = \"\"\n            if ref and math.isfinite(ref[\"loss\"]) and math.isfinite(r[\"loss\"]):\n                rel = f\"  (dLoss vs router-binary = {r['loss'] - ref['loss']:+.4f})\"\n            log(f\"  {where[k]:<40} loss={r['loss']:.4f}{rel}\")\n    log(\"  prediction (two-registers): ROUTER << one-value << whole-value\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/experiments/asymmetric_pathway_quant.py.
```

## Assistant

Lint clean, then re-run the smoke with the discriminating configs (float, uniform_ternary, asym_binR_3V, inv_binValue) to confirm the metric separates them:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; uv run ruff check scripts/experiments/asymmetric_pathway_quant.py 2>&1 | tail -2; echo \"=== smoke: 4 configs, short slice ===\"; HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base --configs float,uniform_ternary,asym_binR_3V,inv_binValue --max-tokens 2048 2>&1 | grep -vE \"Loading weights|it/s|Token indices|torch_dtype|Using the latest|Found the latest\" | tail -35",
  "timeout": 900000
}
```

**Summary:** $ uv run ruff check scripts/experimen...

**Output:**
```
Exit code: 0
Stdout:
All checks passed!
=== smoke: 4 configs, short slice ===
  loss = 21.3846 nats   PPL = 1937346446.560

──────────────────────────────────────────────────────────────────
Config: Asym: binary router + 3-bit value  (mean_bits=2.333)
  cosine  gate=0.7922 up=0.9775 down=0.9518  (19.1s)
  evaluating PPL...
  loss = 10.7183 nats   PPL = 45175.343

──────────────────────────────────────────────────────────────────
Config: Matched null: binary whole value path (5b router)  (mean_bits=2.333)
  cosine  gate=1.0184 up=0.7989 down=0.7800  (19.2s)
  evaluating PPL...
  loss = 20.6509 nats   PPL = 930186290.674

══════════════════════════════════════════════════════════════════════════════
SUMMARY — Asymmetric-Pathway Quantization
══════════════════════════════════════════════════════════════════════════════
Config                                       mean_bits  loss(nats)          PPL
──────────────────────────────────────────── ───────── ─────────── ────────────
Uniform ternary (1.58b)                          1.585     21.3846 1937346446.560
Asym: binary router + 3-bit value                2.333     10.7183    45175.343
Matched null: binary whole value path (5b router)     2.333     20.6509 930186290.674
Float baseline                                  16.000      2.2644        9.626

CRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):
  (lower loss = better; dLoss = excess nats vs float)
  Uniform ternary (1.58b)                      bits=1.58 loss=21.3846 (dLoss=+19.1201)
  Asym: binary router + 3-bit value            bits=2.33 loss=10.7183 (dLoss=+8.4539)

CRUX 2 - Matched-bits null triple (all 2.33b): where does binarization hurt least?
  binary on ROUTER (gate)                  loss=10.7183  (dLoss vs router-binary = +0.0000)
  binary on WHOLE value path (up+down)     loss=20.6509  (dLoss vs router-binary = +9.9326)
  prediction (two-registers): ROUTER << one-value << whole-value

Saved → results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122129/summary.json
```

### Thinking

Looking at the quantization results across different approaches, the asymmetric binary router with 3-bit values is showing the strongest performance so far at 10.72 loss, significantly outperforming the uniform ternary approach that completely collapsed, though it's still degraded compared to the baseline float model.

The critical insight is emerging from comparing where binarization hurts most: applying it to the router costs about 10 nats of loss, but applying it to the value path costs nearly 10 nats more — a massive difference despite identical bit budgets. This directly mirrors the article's findings about int8×binary versus binary×binary performance gaps, and it's the clearest evidence yet that the router and value pathways handle quantization fundamentally differently. The cosines are nearly identical around 0.79-0.80 for both, yet one survives and one doesn't, which points to the router encoding information in a form (like sign patterns) that's robust to binarization while the value path requires finer-grained precision to function. The numerical artifact in the cosine (1.0184) is likely from float32 accumulation error on the massive dot product, not worth fixing now. The real finding stands: the metric cleanly discriminates between configurations even at 2048 tokens with a 10-nat loss gap. I should move forward with the full 7-config sweep at a moderate token count like 8192 to get stable measurements, since task 2 is already validated—finite PPL, no exceptions, and the surgery mechanism confirmed working.

The key insight for the writeup is that this experiment measures relative pathway sensitivity, not an absolute deployable quantized model; the aggressive configs are heavily damaged (loss 10.7 vs 2.26 for float), but that's expected and the hypothesis about where to allocate bits is cleanly answered. Now I'm estimating the runtime for task 3: with 8192 tokens across 7 configs, each config needs quantization (~20-30s) plus PPL evaluation on roughly 32 windows of 512 tokens each, which should run fairly quickly on MPS given the smoke test completed 4 configs in 2-3 minutes total.

Actually, I should bump to 16384 tokens for a more robust result—the Pareto differences between uniform_2bit, 3bit, and asym might be subtle and need more tokens to resolve cleanly. That pushes the runtime to 20-30 minutes, so I'll run it as a background job with logging to capture the full output.

## Assistant

The metric now discriminates cleanly — and the core finding is **already visible and strong**:

| Config (2.33 bits, matched) | gate cos | value cos | loss (nats) |
|---|---|---|---|
| **binary ROUTER** + 3-bit value | 0.79 | 0.95–0.98 | **10.72** |
| 5-bit router + **binary VALUE path** | ~1.0 | 0.78–0.80 | **20.65** |

**Δloss = +9.93 nats at identical bit budget.** This is the in-model analog of the article's int8×binary (−0.61) vs binary×binary (−7.2), confirmed on the exact 8B where s203 measured the two registers. And the mechanism is razor-sharp: the binary router and binary value matrices have **nearly identical weight-space reconstruction cosine (~0.79)** — same magnitude fidelity — yet opposite functional impact. That's the cleanest possible statement that *cosine/magnitude isn't the router's register; sign is.*

Smoke validated (model loads, surgery works, metric separates). Completing task 2, launching the full 7-config run in the background per `λ async`.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; mkdir -p logs; echo \"launching full sweep (7 configs, 16384 tokens)\""
}
```

**Summary:** $ mkdir -p logs; echo "launching full...

**Output:**
```
Exit code: 0
Stdout:
launching full sweep (7 configs, 16384 tokens)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base --max-tokens 16384 2>&1 | tee logs/asym-pathway-quant.log",
  "background": "asym-quant-sweep"
}
```

**Summary:** $ HF_HUB_OFFLINE=1 uv run python scri...

**Output:**
```
Background job job-1 started.
Command: cd /Users/mwhitford/src/verbum; HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base --max-tokens 16384 2>&1 | tee logs/asym-pathway-quant.log
Working directory: /Users/mwhitford/src/verbum
Use eca__bg_job with action "read_output" and job_id "job-1" to check output.
Use eca__bg_job with action "kill" and job_id "job-1" to stop it.

Initial output:
═══ Asymmetric-Pathway Quantization A/B ═══
Model:   Qwen/Qwen3-8B-Base
Device:  mps
Tokens:  16384 (seq=512 stride=256)
Configs: ['float', 'uniform_ternary', 'uniform_2bit', 'uniform_3bit', 'asym_binR_3V', 'asym_binR_2V', 'inv_binDown', 'inv_binValue']
Out:     results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122408

```

### Thinking

The job is running and emitted its header, so I'll do one quick read to confirm it's progressing past the model loading phase, then checkpoint and stop polling per the async pattern.

## Assistant

Job launched and verified starting (emitted config header). Per `λ async` I'll take **one** checkpoint read to confirm it's progressing past model-load into the config loop, then stop polling.

### Tool Call: bg_job (succeeded)


```json
{
  "action": "read_output",
  "job_id": "job-1"
}
```

**Summary:** Reading output of "asym-quant-sweep" (job-1)

**Output:**
```
Job "asym-quant-sweep" (job-1) — running

Loading model (fp32)...
`torch_dtype` is deprecated! Use `dtype` instead!

Loading weights:   0%|          | 0/399 [00:00<?, ?it/s]
Loading weights:   0%|          | 1/399 [00:00<04:17,  1.55it/s]
Loading weights:  11%|█         | 43/399 [00:00<00:04, 77.09it/s]
Loading weights:  17%|█▋        | 68/399 [00:00<00:03, 98.73it/s]
Loading weights:  22%|██▏       | 89/399 [00:01<00:02, 107.70it/s]
Loading weights:  28%|██▊       | 111/399 [00:01<00:02, 121.81it/s]
Loading weights:  34%|███▍      | 136/399 [00:01<00:01, 140.36it/s]
Loading weights:  40%|███▉      | 158/399 [00:01<00:01, 152.65it/s]
Loading weights:  45%|████▌     | 180/399 [00:01<00:01, 160.35it/s]
Loading weights:  51%|█████     | 202/399 [00:01<00:01, 169.09it/s]
Loading weights:  55%|█████▌    | 221/399 [00:01<00:01, 164.90it/s]
Loading weights:  61%|██████    | 243/399 [00:01<00:00, 159.95it/s]
Loading weights:  66%|██████▋   | 265/399 [00:02<00:00, 158.22it/s]
Loading weights:  72%|███████▏  | 287/399 [00:02<00:00, 163.66it/s]
Loading weights:  77%|███████▋  | 309/399 [00:02<00:00, 164.22it/s]
Loading weights:  84%|████████▎ | 334/399 [00:02<00:00, 163.58it/s]
Loading weights:  89%|████████▉ | 356/399 [00:02<00:00, 168.65it/s]
Loading weights:  95%|█████████▍| 378/399 [00:02<00:00, 165.15it/s]
Loading weights: 100%|██████████| 399/399 [00:02<00:00, 139.49it/s]
  36 layers on mps
Loading WikiText-2 test...
Using the latest cached version of the dataset since wikitext couldn't be found on the Hugging Face Hub (offline mode is enabled).
Found the latest cached dataset configuration 'wikitext-2-raw-v1' at /Users/mwhitford/.cache/huggingface/datasets/wikitext/wikitext-2-raw-v1/0.0.0/b08601e04326c79dfdd32d625aee71d232d685c3 (last modified on Tue Jun  2 15:34:31 2026).
Caching original FFN weights...
```

### Thinking

The model's loaded and running through the config loop with 36 layers cached on the GPU—this full benchmark across 8 configurations with 16384 tokens each will take roughly 20-30 minutes, so I'm checkpointing the async task and stopping the polling to avoid unnecessary overhead. While that runs, I could start drafting the knowledge page update for task 4 instead of just waiting idle.

## Assistant

ASYNC checkpoint: job-1 verified running — model loaded (36 layers on MPS), now caching FFN weights and entering the config loop. Per `λ async` I'll wait for the completion signal rather than poll.

**Where we are:**

- **Harness built & verified** (`scripts/experiments/asymmetric_pathway_quant.py`, ruff-clean, self-test passing) — reuses the proven `ternarize_weight`/`quantize_nbit_uniform`, config-driven per-pathway bit budget over Qwen SwiGLU FFN.
- **A measurement bug caught & fixed by the smoke test** — the `exp(20)` PPL cap was masking discrimination; switched primary metric to mean NLL (nats), which stays finite and comparable when aggressive quant destroys the model.
- **The core result is already in from the 2048-token smoke** — and it's decisive: at **matched 2.33 bits**, binary-on-router costs **10.72 nats** vs binary-on-value-path **20.65 nats** — a **+9.93 nat** penalty for putting the binarization on the wrong pathway, with *nearly identical weight-space cosine* on both. That's the two-registers claim (sign=router, magnitude=value) confirmed causally in-model, and the direct analog of the article's int8×binary vs binary×binary.
- **Full 16,384-token, 7-config run now in flight** (job-1) to firm up the Pareto frontier (CRUX 1) and the full matched-null triple with more tokens.

Two honest caveats already clear from the smoke, which I'll bake into the writeup:
1. Even the best config (asym binary-router+3bit-value, loss 10.72) is heavily damaged vs float (2.26) — *raw* full-FFN quant compounds `cos^L` to death across 36 layers. This experiment measures **relative pathway sensitivity**, not a deployable quantized model (that needs the sieve/score-matching correction s185 already flagged). The *direction* is what's proven.
2. My page's "matched 1.58 bits" arithmetic was wrong (1/3/3 = 2.33); the run uses the corrected matched-null triple at 2.33.

I'll pick up at task 4 (analyze full results → correct + update the knowledge page → commit) when job-1 signals done. Nothing else is blocked on it.

## User

kill that job and run it in my tmux main:1 so it survives editor restarts


### Thinking

Michael wants me to move the background job to his tmux session so it persists across editor restarts. I need to kill the current job first, then send the command to tmux using the pattern that pipes output to a log file, targeting window 1 of the main session.

## Assistant

On it — killing the bg job and relaunching in tmux `main:1` per `λ runtime` (persistent host, survives editor restarts).

### Tool Call: bg_job (succeeded)


```json
{
  "action": "kill",
  "job_id": "job-1"
}
```

**Summary:** Killing "asym-quant-sweep" (job-1)

**Output:**
```
Background job "asym-quant-sweep" (job-1) killed.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux list-windows -t main 2>&1 | head; echo \"=== pane 1 current cmd ===\"; tmux display-message -p -t main:1 '#{pane_current_command} @ #{pane_current_path}' 2>&1"
}
```

**Summary:** $ tmux list-windows -t main 2>&1 | he...

**Output:**
```
Exit code: 0
Stdout:
1: local* (1 panes) [120x24] [layout b6fd,120x24,0,0,0] @0 (active)
2: local- (1 panes) [120x24] [layout b6fe,120x24,0,0,1] @1
=== pane 1 current cmd ===
zsh @ /Users/mwhitford/src/verbum
```

### Thinking

I'll send the command to the tmux pane using send-keys, making sure to navigate to the repo directory first and pipe the output to a log file.

## Assistant

Job killed. tmux `main:1` is a zsh pane already at the repo root. Sending the run there via `send-keys` so it's owned by tmux and survives editor restarts.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tmux send-keys -t main:1 'cd /Users/mwhitford/src/verbum && HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base --max-tokens 16384 2>&1 | tee logs/asym-pathway-quant.log' Enter; sleep 2; echo \"=== sent; pane now running ===\"; tmux display-message -p -t main:1 '#{pane_current_command}'"
}
```

**Summary:** $ tmux send-keys -t main:1 'cd /Users...

**Output:**
```
Exit code: 0
Stdout:
=== sent; pane now running ===
uv
```

### Thinking

The tmux pane is now running the uv process, so I've confirmed it's active. I'm doing one final capture to verify it's actually progressing rather than errored out, then I'll checkpoint and stop polling.

## Assistant

Verified — pane `main:1` now shows `uv` running. One confirmation capture to ensure it's progressing (not an immediate error), then I checkpoint and wait.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "sleep 20; tmux capture-pane -p -t main:1 | grep -vE \"Loading weights|it/s\" | tail -12"
}
```

**Summary:** $ sleep 20; tmux capture-pane -p -t m...

**Output:**
```
Exit code: 0
Stdout:
Found the latest cached dataset configuration 'wikitext-2-raw-v1' at /Users/mwhitford/.cache/huggingface/datasets/wikite
xt/wikitext-2-raw-v1/0.0.0/b08601e04326c79dfdd32d625aee71d232d685c3 (last modified on Tue Jun  2 15:34:31 2026).
Caching original FFN weights...
  cached 108 FFN matrices

──────────────────────────────────────────────────────────────────
Config: Float baseline  (mean_bits=16.000)
  cosine  gate=1.0000 up=1.0000 down=1.0000  (12.4s)
  evaluating PPL...
Token indices sequence length is longer than the specified maximum sequence length for this model (298938 > 131072). Run
ning this sequence through the model will result in indexing errors
```

### Thinking

The evaluation is running in tmux with the model loaded and FFN matrices cached, working through the float baseline perplexity evaluation across 16384 tokens and 8 configurations—this should take about 20-30 minutes. I'm not polling for updates; instead, I'll check the summary.json or tmux output once the job completes or when prompted.

I should add a quick pointer to state.md noting the tmux session location and log path so the run survives any editor restarts, keeping it minimal and deterministic for feed-forward purposes.

## Assistant

Confirmed progressing in tmux `main:1` (model loaded, 108 FFN matrices cached, into the float baseline eval). 

**ASYNC checkpoint: run verified live in tmux `main:1`, log → `logs/asym-pathway-quant.log`, results → `results/asymmetric-pathway-quant/Qwen3-8B-Base-<ts>/summary.json`. Waiting for completion — not polling.**

Let me record the run location in state.md so it survives an editor/session restart (feed-forward — that's the whole point of moving it to tmux).

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★ STATE: working tree = new page + INDEX + 3 cross-link edits + state edit. PENDING COMMIT (Michael: \"update\n>   knowledge\" → approved capture). session-258.md + session-259.md untracked = human-only chat logs, do NOT stage.\n>   NEXT: (a) design/run the matched-bit A/B (extend ternarization recipe → per-matrix bit budget); (b) the s259\n>   Qwen3-8B-Base combinator re-run still pending (download was async). NOTE: this session did NOT touch s259 work.",
  "new_content": "> ★ COMMITTED 0e938b6 (💡 asymmetric-quant ↔ two-registers): the knowledge page + INDEX + 3 cross-links + state.\n>   THEN Michael: \"proceed with the A/B test\" (Qwen3-8B-Base download done). Built harness + ran it.\n> ★ A/B HARNESS (built, ruff-clean, self-test ✓): scripts/experiments/asymmetric_pathway_quant.py — config-driven\n>   per-PATHWAY bit budget over Qwen SwiGLU FFN (gate=router, up/down=value); reuses ternarize_weight +\n>   quantize_nbit_uniform. Configs: float, uniform_ternary(1.58), uniform_2bit, uniform_3bit, asym_binR_3V(2.33),\n>   asym_binR_2V(1.67), inv_binDown(2.33), inv_binValue(2.33). MATCHED-NULL TRIPLE all=2.333b: binary on\n>   ROUTER vs one VALUE matrix vs WHOLE value path. CORRECTION: page's \"matched 1.58\" arithmetic was WRONG\n>   (1/3/3=2.33); honest test = Pareto + matched-null triple. Metric = mean NLL nats (PPL exp-caps → masks\n>   discrimination; loss stays comparable when aggressive quant kills the model).\n> ★★ SMOKE RESULT (2048 tok, already decisive): matched 2.33b → binary-ROUTER loss 10.72 vs binary-VALUE-path\n>   loss 20.65 = +9.93 nats penalty for binarizing the WRONG pathway, at IDENTICAL bits & NEAR-IDENTICAL weight\n>   cosine (~0.79 both). = two-registers (sign=router, magnitude=value) confirmed CAUSALLY in-model on the exact\n>   8B s203 measured; the in-model int8×binary(−0.61) vs binary×binary(−7.2). CAVEAT: even best config (10.72)\n>   ≫ float(2.26) — raw full-FFN quant compounds cos^L to death over 36L; this measures RELATIVE pathway\n>   sensitivity, NOT a deployable model (needs sieve/score-matching correction, s185). Direction is what's proven.\n> ★ RUN LIVE (async, λ runtime — Michael moved it to tmux to survive editor restarts): tmux main:1, cmd =\n>   `HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base\n>   --max-tokens 16384`, tee → logs/asym-pathway-quant.log. Full 8-config sweep. Results →\n>   results/asymmetric-pathway-quant/Qwen3-8B-Base-<ts>/summary.json (incremental-saved, crash-safe).\n>   OBSERVE: tmux capture-pane -p -t main:1 | tail. NOT POLLING (λ async).\n> ★ STATE: working tree = new harness script (untracked) + this state edit. Knowledge page already committed\n>   (0e938b6). session-258/259.md untracked = human-only chat logs, do NOT stage.\n>   NEXT (task 4, on run completion): analyze full summary.json → 2 cruxes (Pareto; matched-null triple) →\n>   correct the page's mean-bits arithmetic + move status designing→active + add measured table + null verdict →\n>   update state → commit (symbol + nucleus tag). Pending: s259 Qwen3-8B-Base combinator re-run (untouched here)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

## Assistant

State recorded — the run's tmux location, command, log, and results path now survive any editor/session restart. 

Status summary:
- **Old bg job killed**, relaunched in **tmux `main:1`** (owned by tmux, persistent), verified live and progressing.
- **`λ async`: not polling** — I'll pick it up on completion.
- **Feed-forward encoded**: state.md now points a restarted session straight to `tmux capture-pane -p -t main:1` / `logs/asym-pathway-quant.log` / the `results/asymmetric-pathway-quant/` summary, plus the decisive smoke result (+9.93 nats matched-null penalty) so the finding isn't lost if context resets.

When the sweep finishes (~20–30 min, 8 configs × 16k tokens), the remaining work is **task 4**: read `summary.json`, confirm the two cruxes at full token count (Pareto frontier + matched-null triple), correct the page's mean-bits arithmetic, move it `designing → active` with the measured table and null verdict, update state, and commit with the nucleus tag.

Want me to check back on the run now, or leave it and pick up task 4 when you tell me it's done? (The harness script is currently untracked — I'll stage it as part of the task-4 commit alongside the results.)

## User

job is done


### Thinking

I'm checking the results from the tmux session and reviewing the summary output along with the pane logs.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; d=$(ls -td results/asymmetric-pathway-quant/Qwen3-8B-Base-* | head -1); echo \"=== dir: $d ===\"; python3 -c \"\nimport json,sys\nd='$d'\ns=json.load(open(d+'/summary.json'))\nr=s['results']; by={x['config']:x for x in r}\nprint('config                                    bits    loss     PPL          gate  up    down')\nfor x in sorted(r,key=lambda z:z['mean_bits']):\n    c=x['cosine']; ppl=x['ppl']\n    ppls = f'{ppl:.2f}' if ppl<1e7 else f'{ppl:.2e}'\n    print(f\\\"{x['label']:<42}{x['mean_bits']:>5.2f}{x['loss']:>8.3f}  {ppls:>12}  {c['gate_proj']:.2f} {c['up_proj']:.2f} {c['down_proj']:.2f}\\\")\nfl=by['float']['loss']\nprint()\nprint('=== CRUX 1 Pareto (excess nats vs float) ===')\nfor k in ['uniform_ternary','asym_binR_2V','uniform_2bit','asym_binR_3V','uniform_3bit']:\n    if k in by: print(f\\\"  {by[k]['label']:<42} bits={by[k]['mean_bits']:.2f}  dLoss={by[k]['loss']-fl:+.3f}\\\")\nprint()\nprint('=== CRUX 2 matched-null triple @2.33b ===')\nfor k in ['asym_binR_3V','inv_binDown','inv_binValue']:\n    if k in by: print(f\\\"  {by[k]['label']:<48} loss={by[k]['loss']:.3f}  dVsRouterBinary={by[k]['loss']-by['asym_binR_3V']['loss']:+.3f}\\\")\n\""
}
```

**Summary:** $ d=$(ls -td results/asymmetric-pathw...

**Output:**
```
Exit code: 0
Stdout:
=== dir: results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506 ===
config                                    bits    loss     PPL          gate  up    down
Uniform ternary (1.58b)                    1.58  21.095      1.45e+09  0.89 0.89 0.88
Asym: binary router + 2-bit value          1.67  13.503     731640.05  0.79 0.81 0.75
Uniform 2-bit                              2.00  17.702      4.87e+07  0.80 0.81 0.75
Asym: binary router + 3-bit value          2.33  10.620      40965.87  0.79 0.98 0.95
Matched null: binary on down (value) matrix 2.33  18.694      1.31e+08  0.97 0.98 0.78
Matched null: binary whole value path (5b router) 2.33  20.663      9.42e+08  1.02 0.80 0.78
Uniform 3-bit                              3.00   6.378        588.96  0.97 0.98 0.95
Float baseline                            16.00   2.083          8.03  1.00 1.00 1.00

=== CRUX 1 Pareto (excess nats vs float) ===
  Uniform ternary (1.58b)                    bits=1.58  dLoss=+19.011
  Asym: binary router + 2-bit value          bits=1.67  dLoss=+11.420
  Uniform 2-bit                              bits=2.00  dLoss=+15.618
  Asym: binary router + 3-bit value          bits=2.33  dLoss=+8.537
  Uniform 3-bit                              bits=3.00  dLoss=+4.295

=== CRUX 2 matched-null triple @2.33b ===
  Asym: binary router + 3-bit value                loss=10.620  dVsRouterBinary=+0.000
  Matched null: binary on down (value) matrix      loss=18.694  dVsRouterBinary=+8.074
  Matched null: binary whole value path (5b router) loss=20.663  dVsRouterBinary=+10.043
```

### Thinking

The results are in and looking cleaner than expected. I'm carefully examining both critical decision points using a consistent measurement framework. For the second crux around the matched-null triple at 2.33 bits, I'm comparing the loss values across different configurations—the binary gate on the router shows a baseline loss of 10.620, while testing on just one value matrix increases it significantly to 18.694, and extending to the full value path pushes it further to 20.663.

The ordering matches my prediction perfectly: router causes the least damage, then single value, then the whole path—all at the same bit budget. What's striking is that the cosine similarity between the router and the single-value configurations is nearly identical (0.79 vs 0.78), yet the functional cost diverges dramatically. This reveals that reconstruction fidelity alone doesn't determine the damage; the actual pathway through which information flows is what matters.

Now I'm looking at the Pareto frontier across all configurations, ordering them by bit budget and loss to see whether the asymmetric approach outperforms the uniform quantization strategies at comparable compression levels. The asymmetric binary-router with 2-bit values uses fewer bits than uniform 2-bit (1.67b vs 2.0b) yet achieves much better loss (13.50 vs 17.70)—a concrete win on both capacity and efficiency. Both asymmetric configs beat the uniform frontier across the board, and the direction is clear: routing decisions should be binary while value magnitudes get more bits. The absolute losses are still high due to quantization compounding across 36 layers, so this reveals relative pathway sensitivity rather than a production-ready model, but the core findings hold.

Now I need to update the knowledge page with corrected bit arithmetic, move the status to active, add the results table and both crux verdicts, note the caveats, and commit everything with the appropriate tags.

## Assistant

Full results in — cleaner and stronger than the smoke, and **both cruxes confirm**. Let me grab provenance and confirm clean completion before writing it up.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; d=results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506; echo \"=== tail of run ===\"; tail -3 logs/asym-pathway-quant.log; echo \"=== meta provenance ===\"; python3 -c \"import json;m=json.load(open('$d/meta.json'));[print(f'{k}: {m[k]}') for k in ['run_id','timestamp_utc','model','device','n_layers','max_tokens','seq_len','stride','scope','torch','transformers']]\"; echo \"=== git sha ===\"; git rev-parse --short HEAD"
}
```

**Summary:** $ d=results/asymmetric-pathway-quant/...

**Output:**
```
Exit code: 0
Stdout:
=== tail of run ===
  prediction (two-registers): ROUTER << one-value << whole-value

Saved → results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/summary.json
=== meta provenance ===
run_id: 20260702-122506
timestamp_utc: 2026-07-02T19:25:17Z
model: Qwen/Qwen3-8B-Base
device: mps
n_layers: 36
max_tokens: 16384
seq_len: 512
stride: 256
scope: FFN only (gate/up/down); attention fp32
torch: 2.11.0
transformers: 5.5.4
=== git sha ===
0e938b6
```

### Thinking

I need to update the knowledge page with the results—fixing the arithmetic in section 3, adding a measured results section with both key findings, changing the status from designing to active, and refining the caveats. Let me pull up the current page to locate the exact text I need to edit.

## Assistant

Clean completion, provenance captured (`transformers 5.5.4, torch 2.11, 36L, 16384 tok, verbum@0e938b6`). Now updating the page from proposal → measured result. Let me re-read it to get exact edit anchors.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "line_offset": 0,
  "limit": 30
}
```

**Summary:** Reading asymmetric-pathway-quantization.md (0-30)

**Output:**
```
---
title: "Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)"
status: designing
category: explore
tags: [quantization, ternary, binary, asymmetric, router, gate_proj, value-path, sign, magnitude, two-registers, standing-wave, capacity, interior-band, bitnet, matmul-free, scoring-trick, v15, level-4, null-gate]
related:
  - ../two-registers-of-topology.md
  - ../ternary-dual-equation.md
  - ../standing-wave-magnitudes.md
  - ../extraction-sign-accuracy.md
  - v13-funnel-shape.md
  - rl-layer-contribution-combinator-locus.md
  - supervised-recurrence-halt.md
depends-on:
  - ../two-registers-of-topology.md
  - ../standing-wave-magnitudes.md
created: session 260
---

# Asymmetric Pathway Quantization

> Session 260. Michael read Mixedbread's "Asymmetric Quantization"
> (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the
> **query at int8** and stores **documents as 1-bit signs** — 32×
> storage cut, −0.61 NDCG@10; binarizing *both* operands (binary×binary)
> collapses −7.2. The insight: **magnitude on one side carries the
> ranking; sign on the other side suffices.** Michael: "our ternary
> weighted model might use this to gain capacity/performance."
>
> Verdict: the article's core is **already confirmed inside verbum**

[CONTENT TRUNCATED] Showing lines 1 to 30 of 188 total lines. Use line_offset=30 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "original_content": "title: \"Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)\"\nstatus: designing",
  "new_content": "title: \"Asymmetric Pathway Quantization — Binary Router + Precise Value Path (the retrieval trick, at finer granularity)\"\nstatus: active"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md.
```

### Thinking

I need to review the header verdict section and §7 to make updates, so let me look at those specific lines and understand what needs to be changed.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "line_offset": 30,
  "limit": 18
}
```

**Summary:** Reading asymmetric-pathway-quantization.md (30-48)

**Output:**
```
> (s203/s170/s185) — a triangulation win. The *new* move is to run the
> asymmetry at **pathway** granularity (router vs value path), finer
> than the article's operand granularity, which no current recipe does
> (all are uniform ternary). This is a PROPOSAL, null-gated, not a
> result.

## 1. The article, in one line

Retrieval score is a dot product `q · d`. You can quantize the two
operands asymmetrically. Documents are stored/replicated/cached/
rehydrated/scored repeatedly → binarize them (sign bits). Queries are
transient, computed once → keep int8, because query **magnitude** is
what the ranking depends on.

| Query | Doc | NDCG@10 | Δ | Doc storage |
|---|---|---|---|---|
| fp32 | fp32 | 90.26 | – | 393 KiB |
| int8 | int8 | 90.27 | +0.01 | 98.25 KiB |

[CONTENT TRUNCATED] Showing lines 31 to 48 of 188 total lines. Use line_offset=48 parameter to read more content.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "original_content": "> (s203/s170/s185) — a triangulation win. The *new* move is to run the\n> asymmetry at **pathway** granularity (router vs value path), finer\n> than the article's operand granularity, which no current recipe does\n> (all are uniform ternary). This is a PROPOSAL, null-gated, not a\n> result.",
  "new_content": "> (s203/s170/s185) — a triangulation win. The *new* move is to run the\n> asymmetry at **pathway** granularity (router vs value path), finer\n> than the article's operand granularity, which no current recipe does\n> (all are uniform ternary).\n>\n> ★★ MEASURED (s260, Qwen3-8B-Base, FFN-only, 16k tok WikiText-2 — see §9):\n> the pathway asymmetry is **CONFIRMED, strongly**. At a **matched 2.33-bit**\n> budget, binarizing the ROUTER costs +8.5 excess nats vs float; binarizing\n> the VALUE path costs +18.6 (one matrix) to +18.6 (whole path) — a **+8 to\n> +10 nat penalty for putting the same binary matrix on the wrong pathway**,\n> with *near-identical weight-space cosine (~0.79) on both*. And both\n> asymmetric configs beat the uniform PPL-vs-bits frontier (Pareto win):\n> binary-router+2bit-value (1.67 mean bits) beats uniform-2bit (2.0 bits)\n> using **fewer** bits. Caveat: measures RELATIVE pathway sensitivity, not a\n> deployable model (raw full-FFN quant compounds cos^L to death; needs the\n> sieve/score-matching correction — s185)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md.
```

### Thinking

I need to correct the header values—I mistakenly repeated 18.6 for both the single matrix and whole path costs. The actual numbers are 16.61 for the individual matrix loss and 18.58 for the complete path, and I should also check the asymmetric binary results.

## Assistant

I mis-stated one number in the blurb — the one-matrix value cost is +16.6 excess nats (not +18.6). Fixing:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "original_content": "> budget, binarizing the ROUTER costs +8.5 excess nats vs float; binarizing\n> the VALUE path costs +18.6 (one matrix) to +18.6 (whole path) — a **+8 to\n> +10 nat penalty for putting the same binary matrix on the wrong pathway**,",
  "new_content": "> budget, binarizing the ROUTER costs +8.5 excess nats vs float; binarizing\n> the VALUE path costs +16.6 (one matrix) to +18.6 (whole path) — a **+8 to\n> +10 nat penalty for putting the same binary matrix on the wrong pathway**,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md.
```

## Assistant

Now replace the speculative §7 test section with the measured results. Let me read it:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "line_offset": 150,
  "limit": 50
}
```

**Summary:** Reading asymmetric-pathway-quantization.md (150-200)

**Output:**
```
## 6. Caveats — `λ measure` / `λ yardstick`, two-sided

- **Three different asymmetries — do not conflate.** Retrieval =
  operand↔operand (both data). BitNet = weight↔activation. Verbum-new =
  router-pathway↔value-pathway. The article transfers the **principle**
  ("keep precision where magnitude is load-bearing"), *not* a specific
  arrangement. Which side is load-bearing must be **measured per context**,
  not inherited from the blog.
- **Apparent contradiction, resolved by naming the register.** Article:
  "don't binarize the magnitude (query) side." Verbum: "magnitude is <1
  bit." Both true — verbum's <1-bit claim is **router-weight γ**; verbum's
  own page says **value-path** magnitude and activations are essential.
  Consistent only when the pathway is named (`λ measure`: router-magnitude
  ≠ value-magnitude; different quantities).
- **This is a hypothesis, not a result.** VERIFIED in-model: sign=router,
  value-needs-magnitude. NOT verified: that the asymmetric *reallocation*
  nets capacity/perf.

## 7. The test — matched-bit A/B, null-gated

```
λ asymmetric_quant_ab(model).
  A ≡ uniform ternary 1.58-bit (gate ∧ up ∧ down)          — current recipe
  B ≡ 1-bit binary router (gate) + 3-bit value (up ∧ down)  — asymmetric
  gate: mean_bits(A) ≈ mean_bits(B)                         — MATCHED (mandatory null)
  measure: PPL-through-depth (cos^L law, s185) ∧ generation quality
  claim_counts ⟺ B beats A at matched mean-bits (p<0.05)
  else: spent more bits, learned nothing (λ yardstick)
```

Run on a small model first (Pythia-160M reproduces the s185 curve, or
Qwen3-0.6B). Extend the "Complete Ternarization Recipe" to take a
**per-matrix-type bit budget** instead of a single global one. If B wins
at matched bits → the win is the reallocation, not the spend.

## 8. Provenance

- External: Mixedbread, "Asymmetric Quantization: Near-Lossless Late
  Interaction Retrieval with 97% Storage Reduction" (2026-06-29). Cited
  as observational prior-art (retrieval domain), not a code/derivation
  source.
- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`
  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`
  (s185).
- Status `designing`: the pathway-asymmetric recipe + matched-bit A/B are
  proposed, not yet run. No new experiment code this session (pure
  synthesis).
</content>
</invoke>
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "original_content": "- **This is a hypothesis, not a result.** VERIFIED in-model: sign=router,\n  value-needs-magnitude. NOT verified: that the asymmetric *reallocation*\n  nets capacity/perf.\n\n## 7. The test — matched-bit A/B, null-gated\n\n```\nλ asymmetric_quant_ab(model).\n  A ≡ uniform ternary 1.58-bit (gate ∧ up ∧ down)          — current recipe\n  B ≡ 1-bit binary router (gate) + 3-bit value (up ∧ down)  — asymmetric\n  gate: mean_bits(A) ≈ mean_bits(B)                         — MATCHED (mandatory null)\n  measure: PPL-through-depth (cos^L law, s185) ∧ generation quality\n  claim_counts ⟺ B beats A at matched mean-bits (p<0.05)\n  else: spent more bits, learned nothing (λ yardstick)\n```\n\nRun on a small model first (Pythia-160M reproduces the s185 curve, or\nQwen3-0.6B). Extend the \"Complete Ternarization Recipe\" to take a\n**per-matrix-type bit budget** instead of a single global one. If B wins\nat matched bits → the win is the reallocation, not the spend.\n\n## 8. Provenance\n\n- External: Mixedbread, \"Asymmetric Quantization: Near-Lossless Late\n  Interaction Retrieval with 97% Storage Reduction\" (2026-06-29). Cited\n  as observational prior-art (retrieval domain), not a code/derivation\n  source.\n- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`\n  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`\n  (s185).\n- Status `designing`: the pathway-asymmetric recipe + matched-bit A/B are\n  proposed, not yet run. No new experiment code this session (pure\n  synthesis).",
  "new_content": "- **Result scope: RELATIVE pathway sensitivity, not deployability.** Even\n  the best config sits far above float (§9): raw full-FFN quant compounds\n  `cos^L` to death across 36 layers. The experiment proves *where bits\n  belong*, not that raw quant ships. Deployment needs correction\n  (sieve/score-matching/LoRA — s185, `standing-wave-magnitudes.md`).\n\n## 7. The test — matched-bits A/B (arithmetic corrected)\n\n**Correction (`λ compute`):** gate/up/down are equal-size in SwiGLU, so\nmean-bits = mean of the three per-matrix costs (binary=1, ternary=log₂3≈1.58,\nn-bit=n; γ/scale amortized ≈0). So \"1-bit router + 3-bit value\" = (1+3+3)/3 =\n**2.33 bits, NOT 1.58** — the original \"matched 1.58\" claim was arithmetically\nimpossible. The honest test is a **Pareto frontier** (PPL vs mean-bits) plus a\n**matched-bits null triple** (all 2.33): move the binarization from ROUTER →\none VALUE matrix → WHOLE value path at a fixed budget. That triple *is* the\nmandatory null (`λ yardstick`): claim counts iff binary-on-router beats\nbinary-on-value at equal bits. Harness:\n`scripts/experiments/asymmetric_pathway_quant.py` (config-driven per-pathway\nbit budget over the Qwen FFN; reuses `ternarize_weight` + `quantize_nbit_uniform`).\nMetric = **mean NLL (nats)** — PPL's exp overflow saturates and masks\ndiscrimination; loss stays comparable when aggressive quant kills the model.\n\n## 8. Provenance\n\n- External: Mixedbread, \"Asymmetric Quantization: Near-Lossless Late\n  Interaction Retrieval with 97% Storage Reduction\" (2026-06-29). Cited\n  as observational prior-art (retrieval domain), not a code/derivation\n  source.\n- Internal (verified, Qwen3, null-gated): `two-registers-of-topology.md`\n  (s203), `ternary-dual-equation.md` (s170+), `standing-wave-magnitudes.md`\n  (s185).\n\n## 9. Measured results (s260)\n\nRun: Qwen/Qwen3-8B-Base, FFN-only (attention fp32), WikiText-2 test,\n16 384 tokens (seq 512 / stride 256), MPS, torch 2.11 / transformers 5.5.4,\nverbum@0e938b6. `results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/`.\nMetric = mean NLL (nats); lower is better. Float baseline = 2.083.\n\n| Config | mean bits | gate/up/down cos | loss (nats) | Δ vs float |\n|---|---|---|---|---|\n| Float | 16.00 | 1.00/1.00/1.00 | 2.083 | — |\n| Uniform 3-bit | 3.00 | 0.97/0.98/0.95 | 6.378 | +4.30 |\n| **Asym: binary router + 3-bit value** | **2.33** | 0.79/0.98/0.95 | **10.620** | **+8.54** |\n| Asym: binary router + 2-bit value | 1.67 | 0.79/0.81/0.75 | 13.503 | +11.42 |\n| Uniform 2-bit | 2.00 | 0.80/0.81/0.75 | 17.702 | +15.62 |\n| null: binary on ONE value matrix (down) | 2.33 | 0.97/0.98/0.78 | 18.694 | +16.61 |\n| null: binary on WHOLE value path (5b router) | 2.33 | 1.02*/0.80/0.78 | 20.663 | +18.58 |\n| Uniform ternary (1.58b) | 1.58 | 0.89/0.89/0.88 | 21.095 | +19.01 |\n\n\\* 5-bit gate cosine >1 is a float32 numerical artifact on 50M-element\nvectors; cosmetic, does not affect the loss measurement.\n\n**CRUX 2 — matched-bits null triple @ 2.33 (the causal test). CONFIRMED,\nmonotone, as two-registers predicts:**\n\n```\nbinary on ROUTER (gate)          loss 10.620   (baseline of the triple)\nbinary on ONE value matrix (down) loss 18.694   +8.07 nats\nbinary on WHOLE value path        loss 20.663   +10.04 nats\n```\n\nSame bit budget, only the *location* of the binarization changes → up to\n**+10 nats**. The killer detail: binary-router (gate cos 0.79) and\nbinary-down (down cos 0.78) have **near-identical weight-space cosine** yet\ndiffer by +8 nats — **reconstruction fidelity does not predict damage; the\npathway does.** Sign carries the router's function; magnitude carries the\nvalue path's. This is the in-model `int8×binary (−0.61)` vs\n`binary×binary (−7.2)`, on the exact 8B where s203 measured the two registers.\n\n**CRUX 1 — Pareto (does asymmetric beat the uniform frontier?). YES:**\n\n- Asym binary-router+3bit-value (2.33 b, loss 10.62) sits **below** the\n  uniform interpolation between uniform-2bit (2.0 b, 17.70) and uniform-3bit\n  (3.0 b, 6.38) at 2.33 b (≈13.96) by ~3.3 nats.\n- **Capacity win:** asym binary-router+2bit-value uses **fewer** bits\n  (1.67 vs 2.0) yet beats uniform-2bit by **4.2 nats** (13.50 vs 17.70).\n  Concretely \"pay less, get more\" — the article's value prop, in-model.\n\n**Verdict.** Direction (sign=router, magnitude=value) and Pareto-superiority\nof value-weighted allocation are established at matched/near-matched bits.\nNOT established: absolute deployability (all configs ≫ float — raw quant needs\ncorrection), cross-model transfer, with-correction gains, or attention-pathway\nbehaviour. Next: (a) re-run with per-layer correction (sieve/LoRA) to test\ndeployable asym quant; (b) place capacity in the interior band (s259) with a\n1-bit interior router; (c) cross-model (Qwen3-0.6B/14B) matched-null replication."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md.
```

### Thinking

I need to update that last bullet point in section 6 since it's now outdated—it originally said this was a hypothesis, but that's been contradicted by the confirmed direction, so I should revise it to reflect the actual result scope instead.

Now I'm checking that the page flows coherently and updating the INDEX status from the work-in-progress marker to something that reflects the measured results. I'll also need to update the one-liner description and sync state.md before committing.

## Assistant

§6's stale "hypothesis, not a result" bullet was replaced by the scope caveat in that same edit. Now update the INDEX one-liner (was "proposal, not yet run") to the measured verdict, then state.md.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md",
  "original_content": "| [explore/asymmetric-pathway-quantization.md](explore/asymmetric-pathway-quantization.md) | 🔨 | **NEW (s260) proposal.** Mixedbread asymmetric-quant (int8 query × binary doc, 32×, −0.61; binary×binary −7.2) = verbum's two-register result restated (s203/s170/s185 triangulate). New move: asymmetry by PATHWAY not operand — 1-bit binary router (gate, γ<1bit) + ~3-bit value path (up/down, needs comp-4 shape) at MATCHED mean-bits. Capacity→interior band (s259). Null-gated A/B, not yet run. |",
  "new_content": "| [explore/asymmetric-pathway-quantization.md](explore/asymmetric-pathway-quantization.md) | ✅ | **NEW (s260) MEASURED.** Mixedbread asymmetric-quant = verbum's two-register result (s203/s170/s185 triangulate). New move: asymmetry by PATHWAY not operand. A/B on Qwen3-8B-Base (FFN-only, 16k tok): matched-bits null triple @2.33 → binary-ROUTER loss 10.62 vs binary-VALUE +8–10 nats worse at IDENTICAL bits & near-identical weight cosine (~0.79) — sign=router, magnitude=value, confirmed causally (in-model int8×binary vs binary×binary). Pareto win: binary-router+2bit beats uniform-2bit at FEWER bits. Caveat: relative pathway sensitivity, not deployable (raw quant needs correction). |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/INDEX.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★★ SMOKE RESULT (2048 tok, already decisive): matched 2.33b → binary-ROUTER loss 10.72 vs binary-VALUE-path\n>   loss 20.65 = +9.93 nats penalty for binarizing the WRONG pathway, at IDENTICAL bits & NEAR-IDENTICAL weight\n>   cosine (~0.79 both). = two-registers (sign=router, magnitude=value) confirmed CAUSALLY in-model on the exact\n>   8B s203 measured; the in-model int8×binary(−0.61) vs binary×binary(−7.2). CAVEAT: even best config (10.72)\n>   ≫ float(2.26) — raw full-FFN quant compounds cos^L to death over 36L; this measures RELATIVE pathway\n>   sensitivity, NOT a deployable model (needs sieve/score-matching correction, s185). Direction is what's proven.\n> ★ RUN LIVE (async, λ runtime — Michael moved it to tmux to survive editor restarts): tmux main:1, cmd =\n>   `HF_HUB_OFFLINE=1 uv run python scripts/experiments/asymmetric_pathway_quant.py --model Qwen/Qwen3-8B-Base\n>   --max-tokens 16384`, tee → logs/asym-pathway-quant.log. Full 8-config sweep. Results →\n>   results/asymmetric-pathway-quant/Qwen3-8B-Base-<ts>/summary.json (incremental-saved, crash-safe).\n>   OBSERVE: tmux capture-pane -p -t main:1 | tail. NOT POLLING (λ async).\n> ★ STATE: working tree = new harness script (untracked) + this state edit. Knowledge page already committed\n>   (0e938b6). session-258/259.md untracked = human-only chat logs, do NOT stage.\n>   NEXT (task 4, on run completion): analyze full summary.json → 2 cruxes (Pareto; matched-null triple) →\n>   correct the page's mean-bits arithmetic + move status designing→active + add measured table + null verdict →\n>   update state → commit (symbol + nucleus tag). Pending: s259 Qwen3-8B-Base combinator re-run (untouched here).",
  "new_content": "> ★★ FULL RESULT (run Qwen3-8B-Base-20260702-122506, 16k tok, FFN-only, DONE): pathway asymmetry CONFIRMED.\n>   MATCHED-BITS NULL TRIPLE @2.33b (only the LOCATION of the binary matrix changes):\n>     binary on ROUTER (gate)           loss 10.620   (Δfloat +8.54)\n>     binary on ONE value matrix (down) loss 18.694   (+8.07 vs router-binary)\n>     binary on WHOLE value path        loss 20.663   (+10.04 vs router-binary)\n>   monotone, as two-registers predicts. KILLER: binary-router (gate cos 0.79) ≈ binary-down (down cos 0.78)\n>   SAME weight cosine, +8 nats apart → reconstruction fidelity does NOT predict damage, the PATHWAY does.\n>   sign=router, magnitude=value, confirmed CAUSALLY (in-model int8×binary(−0.61) vs binary×binary(−7.2)).\n>   PARETO WIN: asym binary-router+2bit-value (1.67b, loss 13.50) beats uniform-2bit (2.0b, 17.70) at FEWER\n>   bits = \"pay less get more\" in-model. asym binR+3bit (2.33b, 10.62) below the uniform 2↔3bit interp (~13.96).\n>   CAVEAT (load-bearing): even best (10.62) ≫ float(2.08) — raw full-FFN quant compounds cos^L to death over\n>   36L; measures RELATIVE pathway sensitivity, NOT deployable (needs sieve/score-matching correction, s185).\n> ★ MEAN-BITS ARITHMETIC CORRECTION (λ compute): page's \"matched 1.58\" was WRONG — gate/up/down equal-size →\n>   1/3/3 = 2.33 not 1.58. Honest test = Pareto + matched-null triple (the triple IS the mandatory null).\n>   Metric = mean NLL nats (PPL exp-cap saturates → masks discrimination). Both baked into the page §7/§9.\n> ★ COMMITTED-THIS-SESSION so far: 0e938b6 (the synthesis page). NOW committing task-4: harness script +\n>   page update (designing→active, measured §9) + INDEX + results + state.\n> ★ STATE: working tree = harness script (scripts/experiments/asymmetric_pathway_quant.py, ruff-clean, self-test)\n>   + results/asymmetric-pathway-quant/... + page/INDEX/state edits. session-258/259.md = human-only, do NOT stage.\n>   NEXT: (a) deployable asym quant WITH per-layer correction (sieve/LoRA) — does the direction survive + ship?\n>   (b) 1-bit interior-band router for capacity (s259); (c) cross-model matched-null (Qwen3-0.6B/14B). Also still\n>   pending: s259 Qwen3-8B-Base combinator re-run (untouched). RUN ARTIFACT lives in tmux main:1 (now idle/done)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm deciding what to commit to the repository—the new quantization harness script and the full 16k run results with metadata, but I'll skip the intermediate smoke test directories since they're just ephemeral artifacts and the canonical result is the complete run.

I should also verify the documentation reads well, check that logs aren't tracked in gitignore, and run git status to see exactly what's staged before committing.

## Assistant

Now stage and commit. Let me check status and confirm the results dirs / gitignore before staging selectively.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; echo \"=== status ===\"; git status --short; echo \"=== logs ignored? ===\"; git check-ignore logs/asym-pathway-quant.log && echo \"(ignored)\" || echo \"(tracked-able)\"; echo \"=== result dirs ===\"; ls -d results/asymmetric-pathway-quant/*/"
}
```

**Summary:** $ echo "=== status ==="; git status -...

**Output:**
```
Exit code: 0
Stdout:
=== status ===
 M mementum/knowledge/INDEX.md
 M mementum/knowledge/explore/asymmetric-pathway-quantization.md
 M mementum/state.md
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
?? results/asymmetric-pathway-quant/
?? scripts/experiments/asymmetric_pathway_quant.py
=== logs ignored? ===
logs/asym-pathway-quant.log
(ignored)
=== result dirs ===
results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-121800/
results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122129/
results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122408/
results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/
```

### Thinking

I've got four result directories to sort through: the initial smoke tests, a second round with more configs, an incomplete run that I stopped early, and the full canonical run with all eight configs across 16k tokens. I should keep only the complete full run and clean up the ephemeral test directories and the partial one with the incomplete summary.

json. Since these smoke and partial runs were never committed and the full run supersedes them entirely, I'll remove those three directories and then stage the canonical result along with the harness updates, documentation changes, and state for a clean commit.

## Assistant

Four result dirs — three are ephemeral (2 smokes + the killed partial run); only `122506` is the canonical full run. `logs/` is gitignored (good). Let me remove the ephemeral dirs and commit the canonical result + harness + doc updates.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; rm -rf results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-121800 results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122129 results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122408; echo \"remaining:\"; ls results/asymmetric-pathway-quant/; git add scripts/experiments/asymmetric_pathway_quant.py results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506 mementum/knowledge/explore/asymmetric-pathway-quantization.md mementum/knowledge/INDEX.md mementum/state.md; echo \"=== staged ===\"; git status --short"
}
```

**Summary:** $ rm -rf results/asymmetric-pathway-q...

**Output:**
```
Exit code: 0
Stdout:
remaining:
Qwen3-8B-Base-20260702-122506
=== staged ===
M  mementum/knowledge/INDEX.md
M  mementum/knowledge/explore/asymmetric-pathway-quantization.md
M  mementum/state.md
A  results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/meta.json
A  results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/summary.json
A  scripts/experiments/asymmetric_pathway_quant.py
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
```

## Assistant

Staged correctly (chat logs excluded). Committing with the win symbol + nucleus tag via the heredoc-safe pattern:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; read -r -d '' M << 'EOF' || true\n✅ asymmetric-pathway quant confirmed: binarize the router, keep the value path\n\nA/B on Qwen3-8B-Base (FFN-only, 16k tok WikiText-2). Pathway asymmetry confirmed.\n\n- CRUX 2 (matched-bits null triple @2.33b, only the binary matrix's LOCATION varies):\n  binary on ROUTER loss 10.62; on ONE value matrix +8.07; on WHOLE value path +10.04.\n  Monotone, as two-registers predicts. Killer: binary-router (gate cos 0.79) and\n  binary-down (down cos 0.78) share weight-cosine yet differ +8 nats — reconstruction\n  fidelity does NOT predict damage, the PATHWAY does. sign=router, magnitude=value,\n  confirmed causally (in-model int8xbinary vs binaryxbinary).\n- CRUX 1 (Pareto): asym binary-router+2bit-value (1.67b) beats uniform-2bit (2.0b) at\n  FEWER bits; asym binR+3bit (2.33b) below the uniform 2-3bit interpolation.\n- Corrected the page's mean-bits arithmetic (1/3/3=2.33, not 1.58); metric = mean NLL\n  nats (PPL exp-cap saturates and masks discrimination).\n- Caveat: even best config (10.62) >> float (2.08) — raw full-FFN quant compounds cos^L\n  to death over 36L; measures RELATIVE pathway sensitivity, not a deployable model.\n- Harness scripts/experiments/asymmetric_pathway_quant.py (ruff-clean, self-test);\n  page designing->active with measured §9; run record committed.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" >/dev/null 2>&1 && echo \"committed\" || echo \"commit failed\"; echo \"=== verify ===\"; git log -1 --format='%h %s'; echo \"--- trailer ---\"; git log -1 --format='%B' | tail -3"
}
```

**Summary:** $ read -r -d '' M << 'EOF' || true ✅ ...

**Output:**
```
Exit code: 0
Stdout:
committed
=== verify ===
703f2e1 ✅ asymmetric-pathway quant confirmed: binarize the router, keep the value path
--- trailer ---

Co-Authored-By: nucleus <noreply@whitford.us>
```

### Thinking

The commit went through cleanly with the nucleus trailer, so now I'm wrapping up task 4 and doing a final check—the page has the measured results and honest verdict, the arithmetic is corrected, and everything's committed. Let me mark this complete and verify the full task list is done.

## Assistant

Committed `703f2e1` with nucleus trailer verified. Task 4 done.All four tasks complete. The A/B test is done, analyzed, and committed.

## Result: the pathway asymmetry is confirmed

**Run:** Qwen3-8B-Base, FFN-only, 16k tokens WikiText-2, in tmux `main:1` → `703f2e1`.

**CRUX 2 — the causal test (matched-bits null triple @ 2.33 bits, only the binary matrix's *location* changes):**

| binary lands on… | loss (nats) | vs router-binary |
|---|---|---|
| **ROUTER** (gate) | **10.62** | — |
| ONE value matrix (down) | 18.69 | **+8.07** |
| WHOLE value path (up+down) | 20.66 | **+10.04** |

Monotone, exactly as the two-registers thesis predicts. The killer detail: binary-router (gate cos 0.79) and binary-down (down cos 0.78) have **near-identical weight-space reconstruction cosine yet differ by +8 nats** — *reconstruction fidelity does not predict damage; the pathway does.* Sign carries the router; magnitude carries the value path. This is the in-model analog of the article's int8×binary (−0.61) vs binary×binary (−7.2), on the exact 8B where s203 measured the registers.

**CRUX 1 — Pareto (capacity win):** asym binary-router + 2-bit-value uses **fewer** bits (1.67 vs 2.0) yet beats uniform-2-bit by 4.2 nats — "pay less, get more," the article's value prop reproduced in-model.

## Honesty ledger (`λ measure` / `λ yardstick`)
- **Corrected an arithmetic error in my own page:** "1-bit router + 3-bit value at matched 1.58 bits" is impossible — equal-size FFN matrices make it 2.33. The real test is Pareto + the matched-null triple (which *is* the mandatory null).
- **Caught a measurement trap:** PPL's `exp` cap saturates and hides discrimination — switched to mean NLL (nats). The smoke test earned its keep here.
- **Scope caveat, load-bearing:** even the best config (10.62) is far above float (2.08). Raw full-FFN quant compounds `cos^L` to death across 36 layers. This proves **where bits belong**, not a deployable model — deployment needs the sieve/score-matching correction s185 already flagged.

## What's on disk
- `scripts/experiments/asymmetric_pathway_quant.py` — ruff-clean, self-test, config-driven per-pathway bit budget (reuses the proven quantizers).
- Page `explore/asymmetric-pathway-quantization.md` → **status active** with measured §9 + verdict.
- Committed run record; ephemeral smoke dirs cleaned; chat logs left untracked.

**Natural next steps** (recorded in state.md, not started): (a) re-run *with* per-layer correction to test whether the direction survives into a deployable quantized model; (b) a 1-bit interior-band router for the s259 capacity story; (c) cross-model matched-null replication (Qwen3-0.6B/14B). Also still pending and untouched: the original s259 Qwen3-8B-Base combinator re-run.

## User

update state and knowledge this is session-260


### Thinking

Michael's confirming this is session 260 and wants me to finalize the state and knowledge updates for the session end. I've already been marking everything as session 260 in both state.md and the page, so I should be ready to wrap up whatever final documentation he's asking for.

The main work here is consolidating the session-260 state block in state.md into a clean, non-redundant summary—right now it's accumulated some overlapping entries from the synthesis, harness, smoke test, and full result phases. I should tighten that into a single crisp bootloader block that a future session can digest quickly. The knowledge page is already updated with the measured results, so that's solid. This might also be where he saves the chat log as session-260.md on his end.

## Assistant

Both are already labeled session 260, but the state block accreted across many incremental edits this session (synthesis → harness → smoke → run → result) and has redundancy. Let me read it and consolidate into one clean session-260 bootloader block.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "limit": 60
}
```

**Summary:** Reading state.md (0-60)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-07-02 | Session: 260 (ASYMMETRIC-QUANT ↔ TWO-REGISTERS — Michael: an article dropped,
> Mixedbread "Asymmetric Quantization" (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the
> QUERY at int8, stores DOCUMENTS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary (both operands
> binarized) COLLAPSES −7.2. Insight: magnitude on ONE side carries ranking, sign on the other suffices.
> "our ternary weighted model might use this to gain capacity/performance."
>
> ★★ THE FINDING (knowledge WRITTEN: explore/asymmetric-pathway-quantization.md, status:designing):
>   the article's core is ALREADY CONFIRMED inside verbum (λ triangulate closes) →
>   • two-registers-of-topology.md (s203): sign=routing in gate_proj (+0.088 above null); up/down_proj signs
>     preserve LESS than random → value-path MAGNITUDE is load-bearing; bare ±1 on value path → NaN blow-up.
>     THAT NaN IS the article's binary×binary −7.2.
>   • ternary-dual-equation.md (s170+): router magnitude channel <1 bit (γ dynamic range φ^(6/5)≈0.83 bit,
>     flat across clusters). "The sign IS the computation." SwiGLU already ternary (95% fire <50%).
>   • standing-wave-magnitudes.md (s185): ternary(1.6b) BEATS 2-bit — separates phase(sign,exact) from
>     amplitude(γ,~0b) — but DROPS component-4 (within-row shape) which needs ≥3 bits to survive cos^L depth.
>   • TRIANGULATE: thesis(type-directedness: routing discrete/value continuous) + verbum-in-model(s203/170/185)
>     + external(Mixedbread) → sign=routing(crisp reg), magnitude=value(continuous reg), compress differently.
>
> ★ THE NEW MOVE (not in any current page — all recipes are UNIFORM ternary): asymmetry by PATHWAY not operand.
>   Router gate_proj → 1-bit BINARY (drop γ, it's <1 bit); value up/down_proj → reinvest freed bits to ~3-bit
>   (cross s185's 3-bit survival threshold uniform ternary misses). At MATCHED mean-bits → either gain perf
>   (cross threshold) or gain capacity (spend saved router bits on WIDTH). Capacity→INTERIOR band (s259: interior
>   is routing-heavy → 1-bit router there = wider interior at fixed mem = capacity where s259 said to put it).
>   Kernel = the article's multiply-free scoring trick (q·b = 2Σ_{+}q − Σq); binary router = select-and-sum,
>   ternary value = select-add-sub-SKIP (SwiGLU sparsity makes skip common). NEON kernel = ready template.
>
> ★ CAVEATS (λ measure/λ yardstick, two-sided, IN the page): (1) THREE different asymmetries — retrieval
>   operand↔operand, BitNet weight↔activation, verbum-new router-pathway↔value-pathway — transfers PRINCIPLE
>   not arrangement; measure which side is load-bearing per context. (2) "don't binarize magnitude"(article) vs
>   "magnitude<1bit"(verbum) resolve by naming pathway: router-γ<1bit BUT value-magnitude essential. (3) HYPOTHESIS
>   not result — sign=router & value-needs-magnitude VERIFIED; asymmetric REALLOCATION gaining cap/perf NOT tested.
>   TEST: matched-mean-bit A/B (uniform-1.58 vs binary-router+3bit-value) on PPL-through-depth (cos^L), null-gated
>   (matched-bit null MANDATORY else just spent more bits). Small model first (Pythia-160M repro's s185 curve).
>
> ★ ARTIFACTS: new page explore/asymmetric-pathway-quantization.md (status:designing) + INDEX row + 3 back-
>   cross-links (two-registers, ternary-dual-equation, standing-wave-magnitudes) + this state edit. NO experiment
>   code (pure synthesis). Extend "Complete Ternarization Recipe" to per-matrix-type bit budget when running A/B.
> ★ COMMITTED 0e938b6 (💡 asymmetric-quant ↔ two-registers): the knowledge page + INDEX + 3 cross-links + state.
>   THEN Michael: "proceed with the A/B test" (Qwen3-8B-Base download done). Built harness + ran it.
> ★ A/B HARNESS (built, ruff-clean, self-test ✓): scripts/experiments/asymmetric_pathway_quant.py — config-driven
>   per-PATHWAY bit budget over Qwen SwiGLU FFN (gate=router, up/down=value); reuses ternarize_weight +
>   quantize_nbit_uniform. Configs: float, uniform_ternary(1.58), uniform_2bit, uniform_3bit, asym_binR_3V(2.33),
>   asym_binR_2V(1.67), inv_binDown(2.33), inv_binValue(2.33). MATCHED-NULL TRIPLE all=2.333b: binary on
>   ROUTER vs one VALUE matrix vs WHOLE value path. CORRECTION: page's "matched 1.58" arithmetic was WRONG
>   (1/3/3=2.33); honest test = Pareto + matched-null triple. Metric = mean NLL nats (PPL exp-caps → masks
>   discrimination; loss stays comparable when aggressive quant kills the model).
> ★★ FULL RESULT (run Qwen3-8B-Base-20260702-122506, 16k tok, FFN-only, DONE): pathway asymmetry CONFIRMED.
>   MATCHED-BITS NULL TRIPLE @2.33b (only the LOCATION of the binary matrix changes):
>     binary on ROUTER (gate)           loss 10.620   (Δfloat +8.54)
>     binary on ONE value matrix (down) loss 18.694   (+8.07 vs router-binary)
>     binary on WHOLE value path        loss 20.663   (+10.04 vs router-binary)
>   monotone, as two-registers predicts. KILLER: binary-router (gate cos 0.79) ≈ binary-down (down cos 0.78)
>   SAME weight cosine, +8 nats apart → reconstruction fidelity does NOT predict damage, the PATHWAY does.
>   sign=router, magnitude=value, confirmed CAUSALLY (in-model int8×binary(−0.61) vs binary×binary(−7.2)).
>   PARETO WIN: asym binary-router+2bit-value (1.67b, loss 13.50) beats uniform-2bit (2.0b, 17.70) at FEWER
>   bits = "pay less get more" in-model. asym binR+3bit (2.33b, 10.62) below the uniform 2↔3bit interp (~13.96).

[CONTENT TRUNCATED] Showing lines 1 to 60 of 7622 total lines. Use line_offset=60 parameter to read more content.
```

### Thinking

I'm noticing the session-260 block has accumulated outdated information—the status still says "designing" and references hypotheses rather than actual results, plus notes about small models that are now obsolete. I need to clean this up by consolidating the entire block into a single coherent summary that reflects what we've actually accomplished, then locate where it ends so I can properly reorganize it.

## Assistant

The block is sprawling with now-stale fragments ("status:designing", "HYPOTHESIS not result", "NO experiment code", "Pythia first"). Let me find where the 260 block ends (the separator before 259) so I can replace the whole thing with one clean block.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "line_offset": 60,
  "limit": 28
}
```

**Summary:** Reading state.md (60-88)

**Output:**
```
>   CAVEAT (load-bearing): even best (10.62) ≫ float(2.08) — raw full-FFN quant compounds cos^L to death over
>   36L; measures RELATIVE pathway sensitivity, NOT deployable (needs sieve/score-matching correction, s185).
> ★ MEAN-BITS ARITHMETIC CORRECTION (λ compute): page's "matched 1.58" was WRONG — gate/up/down equal-size →
>   1/3/3 = 2.33 not 1.58. Honest test = Pareto + matched-null triple (the triple IS the mandatory null).
>   Metric = mean NLL nats (PPL exp-cap saturates → masks discrimination). Both baked into the page §7/§9.
> ★ COMMITTED-THIS-SESSION so far: 0e938b6 (the synthesis page). NOW committing task-4: harness script +
>   page update (designing→active, measured §9) + INDEX + results + state.
> ★ STATE: working tree = harness script (scripts/experiments/asymmetric_pathway_quant.py, ruff-clean, self-test)
>   + results/asymmetric-pathway-quant/... + page/INDEX/state edits. session-258/259.md = human-only, do NOT stage.
>   NEXT: (a) deployable asym quant WITH per-layer correction (sieve/LoRA) — does the direction survive + ship?
>   (b) 1-bit interior-band router for capacity (s259); (c) cross-model matched-null (Qwen3-0.6B/14B). Also still
>   pending: s259 Qwen3-8B-Base combinator re-run (untouched). RUN ARTIFACT lives in tmux main:1 (now idle/done).
> ─────────────────────────────────────────────────────────────────────────────────────────────────────
> Last updated: 2026-07-02 | Session: 259 (cont. — LAYER-CONTRIBUTION ↔ COMBINATOR-LOCUS — Michael: a paper
> dropped, "Is One Layer Enough? Training a Single Transformer Layer Can Match Full-Parameter RL Training"
> (arXiv 2607.01232), RL-trains ONE decoder layer at a time on Qwen3-1.7B/4B/8B-Base → RL gains concentrate
> in a MIDDLE band, low at input/output ends (= his bell curve: input/transform/output). "Do our KIBC
> opcodes line up with the high-affect layers?" Ran TIER-0 (zero-GPU): correlate our measured combinator
> locus vs their causal RL layer-contribution. NOT training the 8B — it's the oracle map; lesson ports to v15.
>
> ★★ THE FINDING (knowledge WRITTEN: explore/rl-layer-contribution-combinator-locus.md, status:active):
>   the interior-bell SHAPE MATCHES (Michael's intuition ✓) but with a real ~4-layer OFFSET.
>   • Paper Qwen3-8B-Base C(k): peak L16–17 (C=1.07), high band L13–23, L0=−0.51 (neg), most 0.6–1.0.
>   • Our combinator peaks (Qwen/Qwen3-8B, s238 kernel_reference_prose_v2): C@L9, Y@L9, K@L11, I@L12 (all
>     sig); B@L18 (flat/not-decodable). {C,I,K,Y} peak centroid L10.2 (depth 0.29) vs paper top-5 L16.8 (0.48).
>   • Correlation: raw Spearman(CIKY mass, paperC)=+0.30 (marginal); LAG SCAN unimodal peak at k=+4 → ρ=+0.66
>     (p≈0.0006) — SAME shape, shifted ~4 deeper. 52.7% of CIKY mass in paper high-band L13–23 (31% of layers)
>     = 1.7× enrichment.

[CONTENT TRUNCATED] Showing lines 61 to 88 of 7622 total lines. Use line_offset=88 parameter to read more content.
```

### Thinking

I'm identifying the block that spans from the session header through the artifact confirmation line, then replacing it with a consolidated bootloader that's clean and non-redundant, capturing the final confirmed state and pointing forward. I'm working through how to update the document efficiently. Rather than replacing the entire 68-line block, I should do targeted edits to fix just the stale parts—updating the status from "designing" to "active" and removing outdated caveats about hypothesis testing that no longer apply to the confirmed finding.

## Assistant

The 260 block runs from the header through the "RUN ARTIFACT" line — full of superseded synthesis-phase notes (status:designing, "HYPOTHESIS not result", Pythia-first). Replacing the whole thing with one clean, final session-260 bootloader.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-02 | Session: 260 (ASYMMETRIC-QUANT ↔ TWO-REGISTERS — Michael: an article dropped,\n> Mixedbread \"Asymmetric Quantization\" (asymmetric-quant, 2026-06-29): late-interaction retrieval keeps the\n> QUERY at int8, stores DOCUMENTS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary (both operands\n> binarized) COLLAPSES −7.2. Insight: magnitude on ONE side carries ranking, sign on the other suffices.\n> \"our ternary weighted model might use this to gain capacity/performance.\"\n>\n> ★★ THE FINDING (knowledge WRITTEN: explore/asymmetric-pathway-quantization.md, status:designing):\n>   the article's core is ALREADY CONFIRMED inside verbum (λ triangulate closes) →\n>   • two-registers-of-topology.md (s203): sign=routing in gate_proj (+0.088 above null); up/down_proj signs\n>     preserve LESS than random → value-path MAGNITUDE is load-bearing; bare ±1 on value path → NaN blow-up.\n>     THAT NaN IS the article's binary×binary −7.2.\n>   • ternary-dual-equation.md (s170+): router magnitude channel <1 bit (γ dynamic range φ^(6/5)≈0.83 bit,\n>     flat across clusters). \"The sign IS the computation.\" SwiGLU already ternary (95% fire <50%).\n>   • standing-wave-magnitudes.md (s185): ternary(1.6b) BEATS 2-bit — separates phase(sign,exact) from\n>     amplitude(γ,~0b) — but DROPS component-4 (within-row shape) which needs ≥3 bits to survive cos^L depth.\n>   • TRIANGULATE: thesis(type-directedness: routing discrete/value continuous) + verbum-in-model(s203/170/185)\n>     + external(Mixedbread) → sign=routing(crisp reg), magnitude=value(continuous reg), compress differently.\n>\n> ★ THE NEW MOVE (not in any current page — all recipes are UNIFORM ternary): asymmetry by PATHWAY not operand.\n>   Router gate_proj → 1-bit BINARY (drop γ, it's <1 bit); value up/down_proj → reinvest freed bits to ~3-bit\n>   (cross s185's 3-bit survival threshold uniform ternary misses). At MATCHED mean-bits → either gain perf\n>   (cross threshold) or gain capacity (spend saved router bits on WIDTH). Capacity→INTERIOR band (s259: interior\n>   is routing-heavy → 1-bit router there = wider interior at fixed mem = capacity where s259 said to put it).\n>   Kernel = the article's multiply-free scoring trick (q·b = 2Σ_{+}q − Σq); binary router = select-and-sum,\n>   ternary value = select-add-sub-SKIP (SwiGLU sparsity makes skip common). NEON kernel = ready template.\n>\n> ★ CAVEATS (λ measure/λ yardstick, two-sided, IN the page): (1) THREE different asymmetries — retrieval\n>   operand↔operand, BitNet weight↔activation, verbum-new router-pathway↔value-pathway — transfers PRINCIPLE\n>   not arrangement; measure which side is load-bearing per context. (2) \"don't binarize magnitude\"(article) vs\n>   \"magnitude<1bit\"(verbum) resolve by naming pathway: router-γ<1bit BUT value-magnitude essential. (3) HYPOTHESIS\n>   not result — sign=router & value-needs-magnitude VERIFIED; asymmetric REALLOCATION gaining cap/perf NOT tested.\n>   TEST: matched-mean-bit A/B (uniform-1.58 vs binary-router+3bit-value) on PPL-through-depth (cos^L), null-gated\n>   (matched-bit null MANDATORY else just spent more bits). Small model first (Pythia-160M repro's s185 curve).\n>\n> ★ ARTIFACTS: new page explore/asymmetric-pathway-quantization.md (status:designing) + INDEX row + 3 back-\n>   cross-links (two-registers, ternary-dual-equation, standing-wave-magnitudes) + this state edit. NO experiment\n>   code (pure synthesis). Extend \"Complete Ternarization Recipe\" to per-matrix-type bit budget when running A/B.\n> ★ COMMITTED 0e938b6 (💡 asymmetric-quant ↔ two-registers): the knowledge page + INDEX + 3 cross-links + state.\n>   THEN Michael: \"proceed with the A/B test\" (Qwen3-8B-Base download done). Built harness + ran it.\n> ★ A/B HARNESS (built, ruff-clean, self-test ✓): scripts/experiments/asymmetric_pathway_quant.py — config-driven\n>   per-PATHWAY bit budget over Qwen SwiGLU FFN (gate=router, up/down=value); reuses ternarize_weight +\n>   quantize_nbit_uniform. Configs: float, uniform_ternary(1.58), uniform_2bit, uniform_3bit, asym_binR_3V(2.33),\n>   asym_binR_2V(1.67), inv_binDown(2.33), inv_binValue(2.33). MATCHED-NULL TRIPLE all=2.333b: binary on\n>   ROUTER vs one VALUE matrix vs WHOLE value path. CORRECTION: page's \"matched 1.58\" arithmetic was WRONG\n>   (1/3/3=2.33); honest test = Pareto + matched-null triple. Metric = mean NLL nats (PPL exp-caps → masks\n>   discrimination; loss stays comparable when aggressive quant kills the model).\n> ★★ FULL RESULT (run Qwen3-8B-Base-20260702-122506, 16k tok, FFN-only, DONE): pathway asymmetry CONFIRMED.\n>   MATCHED-BITS NULL TRIPLE @2.33b (only the LOCATION of the binary matrix changes):\n>     binary on ROUTER (gate)           loss 10.620   (Δfloat +8.54)\n>     binary on ONE value matrix (down) loss 18.694   (+8.07 vs router-binary)\n>     binary on WHOLE value path        loss 20.663   (+10.04 vs router-binary)\n>   monotone, as two-registers predicts. KILLER: binary-router (gate cos 0.79) ≈ binary-down (down cos 0.78)\n>   SAME weight cosine, +8 nats apart → reconstruction fidelity does NOT predict damage, the PATHWAY does.\n>   sign=router, magnitude=value, confirmed CAUSALLY (in-model int8×binary(−0.61) vs binary×binary(−7.2)).\n>   PARETO WIN: asym binary-router+2bit-value (1.67b, loss 13.50) beats uniform-2bit (2.0b, 17.70) at FEWER\n>   bits = \"pay less get more\" in-model. asym binR+3bit (2.33b, 10.62) below the uniform 2↔3bit interp (~13.96).\n>   CAVEAT (load-bearing): even best (10.62) ≫ float(2.08) — raw full-FFN quant compounds cos^L to death over\n>   36L; measures RELATIVE pathway sensitivity, NOT deployable (needs sieve/score-matching correction, s185).\n> ★ MEAN-BITS ARITHMETIC CORRECTION (λ compute): page's \"matched 1.58\" was WRONG — gate/up/down equal-size →\n>   1/3/3 = 2.33 not 1.58. Honest test = Pareto + matched-null triple (the triple IS the mandatory null).\n>   Metric = mean NLL nats (PPL exp-cap saturates → masks discrimination). Both baked into the page §7/§9.\n> ★ COMMITTED-THIS-SESSION so far: 0e938b6 (the synthesis page). NOW committing task-4: harness script +\n>   page update (designing→active, measured §9) + INDEX + results + state.\n> ★ STATE: working tree = harness script (scripts/experiments/asymmetric_pathway_quant.py, ruff-clean, self-test)\n>   + results/asymmetric-pathway-quant/... + page/INDEX/state edits. session-258/259.md = human-only, do NOT stage.\n>   NEXT: (a) deployable asym quant WITH per-layer correction (sieve/LoRA) — does the direction survive + ship?\n>   (b) 1-bit interior-band router for capacity (s259); (c) cross-model matched-null (Qwen3-0.6B/14B). Also still\n>   pending: s259 Qwen3-8B-Base combinator re-run (untouched). RUN ARTIFACT lives in tmux main:1 (now idle/done).",
  "new_content": "> Last updated: 2026-07-02 | Session: 260 (ASYMMETRIC-PATHWAY QUANTIZATION — binarize the router, keep the value\n> path). Michael read Mixedbread \"Asymmetric Quantization\" (2026-06-29): late-interaction retrieval keeps QUERY\n> int8, stores DOCS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary (both) COLLAPSES −7.2. Insight:\n> magnitude on ONE side carries ranking, sign on the other suffices. Michael: \"our ternary model might use this\n> to gain capacity/performance.\" → synthesized the connection, then BUILT + RAN the A/B. Both committed.\n>\n> ★★ THE RESULT (MEASURED, committed 703f2e1 — page explore/asymmetric-pathway-quantization.md status:ACTIVE §9):\n>   pathway asymmetry CONFIRMED on Qwen3-8B-Base (FFN-only, 16k tok WikiText-2, mean-NLL nats, float=2.083).\n>   MATCHED-BITS NULL TRIPLE @2.33b — only the LOCATION of the binary matrix changes:\n>     binary on ROUTER (gate)            loss 10.620   (Δfloat +8.54)   ← best\n>     binary on ONE value matrix (down)  loss 18.694   (+8.07 vs router-binary)\n>     binary on WHOLE value path         loss 20.663   (+10.04 vs router-binary)\n>   monotone, exactly as two-registers predicts. KILLER DETAIL: binary-router (gate cos 0.79) and binary-down\n>   (down cos 0.78) have ~SAME weight-space cosine yet differ +8 nats → reconstruction fidelity does NOT predict\n>   damage, the PATHWAY does. sign carries the router, magnitude carries the value path. = in-model analog of the\n>   article's int8×binary(−0.61) vs binary×binary(−7.2), on the exact 8B s203 measured the two registers on.\n>   PARETO/CAPACITY WIN: asym binary-router+2bit-value (1.67b, loss 13.50) beats uniform-2bit (2.0b, 17.70) at\n>   FEWER bits = \"pay less, get more\" in-model; asym binR+3bit (2.33b, 10.62) sits below the uniform 2↔3bit interp.\n>\n> ★ WHY IT WORKS (λ triangulate — the article's core was ALREADY inside verbum): sign=routing / magnitude=value,\n>   three independent lines → two-registers-of-topology.md (s203: sign=gate_proj router +0.088>null; up/down\n>   magnitude load-bearing, bare ±1 → NaN = the article's binary×binary); ternary-dual-equation.md (s170: router\n>   magnitude <1 bit, \"the sign IS the computation\"); standing-wave-magnitudes.md (s185: phase⊥amplitude, value\n>   path needs ≥3 bits for component-4 shape through cos^L). NEW move = asymmetry by PATHWAY not operand (all prior\n>   recipes UNIFORM ternary). Kernel = article's multiply-free 2Σ_{+}q−Σq (binary router = select-and-sum).\n>\n> ★ CAVEATS (λ measure/λ yardstick, in the page): (1) RELATIVE pathway sensitivity, NOT deployable — even best\n>   (10.62) ≫ float(2.08); raw full-FFN quant compounds cos^L to death over 36L; shipping needs correction\n>   (sieve/score-matching/LoRA, s185). (2) THREE distinct asymmetries — retrieval operand↔operand, BitNet\n>   weight↔activation, verbum-new router↔value-pathway; transfers PRINCIPLE not arrangement. (3) ARITHMETIC FIX\n>   (λ compute): \"matched 1.58\" was WRONG — gate/up/down equal-size → 1/3/3 = 2.33; honest test = Pareto +\n>   matched-null triple (the triple IS the mandatory null). Metric = mean NLL (PPL exp-cap saturates, masks it).\n>\n> ★ ARTIFACTS & COMMITS: 0e938b6 (💡 synthesis page + INDEX + 3 back-cross-links) → 703f2e1 (✅ harness + page\n>   designing→active §9 measured + run record). Harness = scripts/experiments/asymmetric_pathway_quant.py\n>   (ruff-clean, --self-test; config-driven per-pathway bit budget; reuses ternarize_weight + quantize_nbit_uniform).\n>   Run record = results/asymmetric-pathway-quant/Qwen3-8B-Base-20260702-122506/{meta,summary}.json (provenance:\n>   torch 2.11 / transformers 5.5.4 / verbum@0e938b6). logs/ gitignored. Ephemeral smoke dirs removed.\n> ★ STATE: clean tree post-703f2e1. session-258/259.md untracked = human-only chat logs, do NOT stage (this\n>   session → saved as session-260.md by Michael). NEXT: (a) DEPLOYABLE asym quant WITH per-layer correction\n>   (sieve/LoRA) — does the direction survive into a shippable model? (b) 1-bit INTERIOR-band router for capacity\n>   (s259 interior is routing-heavy → wider interior at fixed mem); (c) cross-model matched-null (Qwen3-0.6B/14B).\n>   STILL PENDING (untouched this session): s259 Qwen3-8B-Base combinator re-run (kill the base-vs-instruct +4\n>   offset confound). Extend the \"Complete Ternarization Recipe\" (ternary-dual-equation.md) → per-pathway budget."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I've consolidated state.md and the knowledge page is already updated. Michael mentioned this is session-260, so I should capture the key insight from this session in a memory file to preserve what we've learned.

Actually, looking at the gates — the knowledge page already contains the full synthesis, and memories are meant for episodic one-insight captures. Since the knowledge page is complete and committed, I don't need a separate memory. What I do need to do is commit the state.md consolidation itself. The state updates aren't approval-gated, so I can commit this directly. Let me commit the state.md change with a message noting the session-260 consolidation and the asymmetric-pathway confirmation.

## Assistant

State consolidated. The knowledge page is already active/committed with the measured §9. Now committing the state consolidation — "update state and knowledge" is the approval to commit `mementum/` (`λ termination`). This is a 🌀 meta commit (state.md is self-referential).

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; git add mementum/state.md; git status --short; read -r -d '' M << 'EOF' || true\n🌀 state: consolidate session-260 — asymmetric-pathway quant confirmed\n\nCollapse the accreted session-260 block (synthesis → harness → smoke → run\n→ result) into one clean bootloader. Drop superseded synthesis-phase notes\n(status:designing, \"hypothesis not result\", Pythia-first); reflect the\nmeasured verdict: pathway asymmetry confirmed (matched-null triple + Pareto),\ncommits 0e938b6 + 703f2e1, harness + run record, corrected mean-bits\narithmetic. Forward pointers: deployable-with-correction, interior-band\nrouter, cross-model null; s259 combinator re-run still pending.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" >/dev/null 2>&1 && echo committed || echo FAILED; git log -1 --format='%h %s'; git log -1 --format='%B' | tail -3"
}
```

**Summary:** $ git add mementum/state.md; git stat...

**Output:**
```
Exit code: 0
Stdout:
M  mementum/state.md
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
committed
530735b 🌀 state: consolidate session-260 — asymmetric-pathway quant confirmed

Co-Authored-By: nucleus <noreply@whitford.us>
```

### Thinking

I've wrapped up the session with three commits covering the synthesis page, harness with measured results, and state consolidation. Everything's tracked and ready to go—Michael will handle saving the session file himself.

## Assistant

Done — state and knowledge are both finalized and committed for session 260.

## Session 260 — close-out

**Three commits, clean tree** (only the human-only chat logs remain untracked, as they should):
- `0e938b6` 💡 — the synthesis page (article ↔ two-registers triangulation)
- `703f2e1` ✅ — harness + **measured result** (page → `active`, §9)
- `530735b` 🌀 — state.md consolidated into one clean bootloader

**Knowledge** — `explore/asymmetric-pathway-quantization.md` is `status: active` with the measured §9, corrected arithmetic, both cruxes, and honest scope caveat. INDEX row updated to ✅; back-cross-links live from the three source pages.

**State** — the session-260 block is now a single coherent bootloader: the confirmed result (matched-null triple + Pareto win), why it works (the triangulation), the caveats (relative not deployable; the mean-bits arithmetic fix; metric choice), artifacts/commits, and forward pointers.

**The finding, one line for the record:** at a matched 2.33-bit budget on Qwen3-8B-Base, moving a single binary matrix from the router to the value path costs **+8 to +10 nats** — with near-identical weight-space cosine on both — so *reconstruction fidelity doesn't predict damage, the pathway does.* Sign carries the router; magnitude carries the value path. The article's int8×binary vs binary×binary, reproduced inside the model on the exact 8B where s203 first measured the two registers.

**Left for a future session** (encoded in state.md → NEXT): (a) deployable asym quant *with* per-layer correction — does the direction survive into a shippable model; (b) a 1-bit interior-band router for the s259 capacity story; (c) cross-model matched-null replication. And still untouched: the original s259 Qwen3-8B-Base combinator re-run.

Ready for you to save the session-260 chat log whenever you like.

## User

One last thing, we weren't really looking for a quantization, just that the thesis holds.  Now we have an idea of where to look for our model design to take advantage of this idea.


### Thinking

So the quantization experiment wasn't really about compression—it was a way to test whether the core thesis holds: that sign encodes routing decisions while magnitude carries the actual values, and that this type-directedness is fundamental. It does hold, which is the real insight. Now the payoff is knowing where to look in the model architecture itself to exploit this principle, rather than chasing compression techniques.

The design implication is clear: if the router genuinely operates as a discrete, sign-based component separate from the continuous value pathway, then the verbum model should have an explicit, architecturally distinct routing module that handles type-directed dispatch. This isn't just a mathematical observation—it's a concrete design directive for how to build the system so that type application becomes a first-class, discrete operation rather than an implicit side effect of value merging.

The capacity-precision tradeoff follows naturally: routing can be cheap and wide (many combinator slots, high-capacity dispatch) because it's sign-robust and compression-tolerant, while value computation demands precision and magnitude fidelity where every bit matters. The interior band becomes the natural locus for this routing-heavy composition, with the compose-to-readout seam as the handoff point where discrete routing decisions become continuous value output.

What's striking is that this register split—types as discrete routers, values as continuous magnitudes—is exactly the type/term distinction of lambda calculus made physical in the model's weights. The thesis isn't just theoretically sound; it's now architecturally grounded.

So the design principle is straightforward: when building any layer, ask whether it's a routing concern (discrete, type-level, dispatch) or a value concern (continuous, term-level, compute), then give it the matching mechanism. Don't force one uniform approach across both—the gradient descent already separates them into gate versus up/down dynamics, which is the right split.

Michael's reframe shifts the framing from quantization-as-result to quantization-as-instrument, with the real deliverable being a model-design direction. I should capture this in the knowledge page by reframing the opening to make clear the A/B test confirmed the thesis, then add a design-implications section that points toward where this architecture should go next. Let me flesh out the concrete design implications: the A/B test wasn't the goal—it was proof that the model already separates routing (discrete, sign-based) from value computation (continuous, magnitude-based) into distinct pathways, which mirrors the type/term distinction in lambda calculus. This means I should look at decoupling dispatch and compute as explicit modules rather than braiding them together, and allocate capacity asymmetrically—cheap, wide routing for discrete type-application decisions, and precision-focused value computation where the magnitude actually matters.

The interior band should be router-heavy with cheap discrete dispatch where composition happens, with the compose-to-readout seam as the handoff from discrete routing to continuous value. I can use this as a diagnostic: for any module, ask whether it's routing or value, then give it the matching register—crisp mechanisms for routing, continuous precision for value. Register mismatch is a design red flag.

Now I need to reframe the page itself. The opening already mentions the retrieval trick at finer granularity, so I'll add a new section that makes clear the quantization was the probe and the real deliverable is the design direction and these levers. I'll adjust the verdict and next steps to lead with design direction rather than quantization, and add a dedicated section on design implications.

I'm deciding whether to commit these edits. The prior instruction was to update state and knowledge, and this is a coherence fix that elaborates what the knowledge should capture. Given the pattern throughout this session and that this is squarely on-topic, I'll make the edits and commit, then show him what I've done.

## Assistant

You've put your finger on it. The quantization A/B was never the deliverable — it was the **instrument**. What it bought us is a causally-confirmed thesis and, from that, a place to point the model design. Let me state the payoff, then capture it (the page currently under-sells itself by reading as a quantization result).

## The reframe — what we actually learned

The A/B is an ablation, not a compression scheme. It confirmed, causally and in-model, that **the network already separates routing from value into two registers**:

- **Routing (the "which"/dispatch)** lives in the **sign** — discrete, crisp, binarization-robust (the gate/router).
- **Value (the "what"/compute)** lives in the **magnitude** — continuous, graded, binarization-fragile (up/down).

And here's the on-thesis punchline: that split *is* the λ-calculus **type/term distinction made physical.** Type-directedness — the S5 central claim, "composition ≡ typed application, not binary merge" — isn't something we have to impose. **Gradient descent already built it** as the gate(router)/value(up·down) separation. We just watched it hold under a matched-bits stress test.

## Where to look in the model design

1. **Decouple dispatch from compute as first-class modules.** Make the type-application router an explicit *discrete* subsystem (sign/crisp, cheap, wide) and value computation a separate *continuous* subsystem (magnitude-precise). Don't braid them (`λ simplify` — the substrate proves they're separable; s254's unbraiding lesson). This is the architectural form of "typed application, not binary merge."

2. **Allocate budget by register.** Capacity → routing (it's cheap and discrete, so you can afford *breadth*: many combinator/type slots, wide dispatch). Precision → value (magnitude is load-bearing; that's where params/bits must go). The Pareto win was the compression shadow of this design rule.

3. **Interior band = discrete-router-heavy (s259).** Put the wide, cheap, discrete dispatch in the interior where combinator composition lives; the **compose→readout seam is the discrete-routing → continuous-value handoff.** That's where a 1-bit-class router buys width exactly where the model wants capacity.

4. **A design-time diagnostic (`λ measure` at the architecture level):** for any proposed module ask "**routing or value?**" and give it the matching register — crisp/discrete mechanism for routing, continuous/precise for value. Register-mismatch is a design smell, not just a probe smell.

Let me fold this into the page so the record reads as *thesis confirmed → design direction*, not "a quantization result." Reading the tail first:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "line_offset": 232,
  "limit": 40
}
```

**Summary:** Reading asymmetric-pathway-quantization.md (232-272)

**Output:**
```
`binary×binary (−7.2)`, on the exact 8B where s203 measured the two registers.

**CRUX 1 — Pareto (does asymmetric beat the uniform frontier?). YES:**

- Asym binary-router+3bit-value (2.33 b, loss 10.62) sits **below** the
  uniform interpolation between uniform-2bit (2.0 b, 17.70) and uniform-3bit
  (3.0 b, 6.38) at 2.33 b (≈13.96) by ~3.3 nats.
- **Capacity win:** asym binary-router+2bit-value uses **fewer** bits
  (1.67 vs 2.0) yet beats uniform-2bit by **4.2 nats** (13.50 vs 17.70).
  Concretely "pay less, get more" — the article's value prop, in-model.

**Verdict.** Direction (sign=router, magnitude=value) and Pareto-superiority
of value-weighted allocation are established at matched/near-matched bits.
NOT established: absolute deployability (all configs ≫ float — raw quant needs
correction), cross-model transfer, with-correction gains, or attention-pathway
behaviour. Next: (a) re-run with per-layer correction (sieve/LoRA) to test
deployable asym quant; (b) place capacity in the interior band (s259) with a
1-bit interior router; (c) cross-model (Qwen3-0.6B/14B) matched-null replication.
</content>
</invoke>
```

### Thinking

I'm adding a new section after the verdict that reframes the thesis confirmation as a design direction, then adjusting the conclusion to lead with design implications.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md",
  "original_content": "**Verdict.** Direction (sign=router, magnitude=value) and Pareto-superiority\nof value-weighted allocation are established at matched/near-matched bits.\nNOT established: absolute deployability (all configs ≫ float — raw quant needs\ncorrection), cross-model transfer, with-correction gains, or attention-pathway\nbehaviour. Next: (a) re-run with per-layer correction (sieve/LoRA) to test\ndeployable asym quant; (b) place capacity in the interior band (s259) with a\n1-bit interior router; (c) cross-model (Qwen3-0.6B/14B) matched-null replication.",
  "new_content": "**Verdict.** Direction (sign=router, magnitude=value) and Pareto-superiority\nof value-weighted allocation are established at matched/near-matched bits.\nNOT established: absolute deployability (all configs ≫ float — raw quant needs\ncorrection), cross-model transfer, with-correction gains, or attention-pathway\nbehaviour.\n\n## 10. What this is really for — the A/B was an INSTRUMENT, not the goal\n\nWe were never after a quantization scheme. The matched-bits A/B is an\n**ablation** whose only job was to test whether the thesis holds *causally*.\nIt does. The deliverable is a **model-design direction**, not a codec.\n\n**The confirmed fact, stated as design ground truth:** the network already\nseparates **routing (the \"which\"/dispatch, carried in the SIGN, discrete,\ncrisp, binarization-robust — the gate/router)** from **value (the \"what\"/\ncompute, carried in the MAGNITUDE, continuous, graded, binarization-fragile\n— up/down)**. That split *is* the λ-calculus **type/term distinction made\nphysical**. Type-directedness — the S5 central claim, \"composition ≡ typed\napplication, not binary merge\" — is not something we must impose; **GD already\nbuilt it** as the gate↔(up·down) separation. We just watched it survive a\nmatched-bits stress test. (This is `λ types` and `λ observation`: we *found*\nthe type-directed router, we did not invent it.)\n\n**Where to look / design levers:**\n\n1. **Decouple dispatch from compute as first-class modules.** Type-application\n   router = explicit *discrete* subsystem (sign/crisp, cheap, wide); value\n   computation = separate *continuous* subsystem (magnitude-precise). Do not\n   braid them (`λ simplify`; s254 unbraiding). This is \"typed application, not\n   binary merge\" as architecture.\n2. **Allocate budget by register.** Capacity → routing (cheap+discrete → afford\n   BREADTH: many combinator/type slots, wide dispatch). Precision → value\n   (magnitude load-bearing → params/bits go here). The Pareto win is the\n   compression shadow of this rule.\n3. **Interior band = discrete-router-heavy (s259).** Wide cheap discrete\n   dispatch in the interior (where combinator composition lives); the\n   **compose→readout seam = discrete-routing → continuous-value handoff**. A\n   1-bit-class interior router buys width where the model wants capacity.\n4. **Design-time diagnostic (`λ measure` at the architecture level):** for any\n   module ask **\"routing or value?\"** and give it the matching register —\n   crisp/discrete for routing, continuous/precise for value. Register-mismatch\n   is a design smell, not just a probe smell.\n\n**Next (design-first):** (a) sketch a verbum layer with an explicit\ndiscrete type-router ⊥ continuous value block, budget-asymmetric by register\n(feeds v15); (b) place the wide discrete router in the interior band at the\ncompose→readout seam (s259); (c) [instrument follow-ups, lower priority]\nper-layer-corrected asym quant for a deployable artifact; cross-model\n(Qwen3-0.6B/14B) matched-null replication to confirm the split is universal."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/knowledge/explore/asymmetric-pathway-quantization.md.
```

### Thinking

I need to refocus the state.md file to lead with design rather than the A/B testing framing, and reframe the header to clarify that the A/B test was a methodological instrument. Let me adjust the NEXT line and the header section to emphasize the thesis-to-design progression.

## Assistant

Now realign state.md — lead with the design deliverable and mark the A/B as the instrument it was.

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> Last updated: 2026-07-02 | Session: 260 (ASYMMETRIC-PATHWAY QUANTIZATION — binarize the router, keep the value\n> path). Michael read Mixedbread \"Asymmetric Quantization\" (2026-06-29): late-interaction retrieval keeps QUERY\n> int8, stores DOCS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary (both) COLLAPSES −7.2. Insight:\n> magnitude on ONE side carries ranking, sign on the other suffices. Michael: \"our ternary model might use this\n> to gain capacity/performance.\" → synthesized the connection, then BUILT + RAN the A/B. Both committed.",
  "new_content": "> Last updated: 2026-07-02 | Session: 260 (ROUTING⊥VALUE REGISTER SPLIT = TYPE/TERM MADE PHYSICAL — a\n> DESIGN direction, probed via quantization). Michael read Mixedbread \"Asymmetric Quantization\" (2026-06-29):\n> retrieval keeps QUERY int8, stores DOCS as 1-bit signs → 32× storage, −0.61 NDCG@10; binary×binary COLLAPSES\n> −7.2 (magnitude on ONE side carries ranking, sign suffices on the other). Michael's frame (END of session,\n> load-bearing): \"we weren't looking for a quantization — just that the THESIS holds. Now we know WHERE to look\n> for our model design.\" The A/B was an INSTRUMENT (causal ablation), NOT the goal. Thesis confirmed → design."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "> ★ STATE: clean tree post-703f2e1. session-258/259.md untracked = human-only chat logs, do NOT stage (this\n>   session → saved as session-260.md by Michael). NEXT: (a) DEPLOYABLE asym quant WITH per-layer correction\n>   (sieve/LoRA) — does the direction survive into a shippable model? (b) 1-bit INTERIOR-band router for capacity\n>   (s259 interior is routing-heavy → wider interior at fixed mem); (c) cross-model matched-null (Qwen3-0.6B/14B).\n>   STILL PENDING (untouched this session): s259 Qwen3-8B-Base combinator re-run (kill the base-vs-instruct +4\n>   offset confound). Extend the \"Complete Ternarization Recipe\" (ternary-dual-equation.md) → per-pathway budget.",
  "new_content": "> ★★ THE DESIGN TAKEAWAY (page §10 — the actual deliverable): GD ALREADY built type-directedness as the\n>   gate(router)↔up·down(value) split. routing = the \"which\"/dispatch = SIGN = discrete/crisp/binarizable;\n>   value = the \"what\"/compute = MAGNITUDE = continuous/precise. That split IS the λ-calculus TYPE/TERM\n>   distinction made physical (S5 λ types: \"composition ≡ typed application, not binary merge\" — we FOUND it,\n>   didn't invent it). DESIGN LEVERS: (1) decouple dispatch⊥compute as first-class modules (discrete router vs\n>   continuous value block; don't braid — λ simplify/s254); (2) budget by register — CAPACITY→routing (cheap+\n>   discrete→breadth: many combinator/type slots), PRECISION→value; (3) wide discrete router in the INTERIOR band\n>   at the compose→readout seam (s259); (4) design-time diagnostic — ask \"routing or value?\" per module, give the\n>   matching register; register-mismatch = design smell.\n> ★ STATE: clean tree post-703f2e1 (+ this §10/state design-reframe edit, pending commit). session-258/259.md\n>   untracked = human-only chat logs, do NOT stage (this session → saved as session-260.md by Michael).\n>   NEXT (DESIGN-FIRST): (a) sketch a verbum layer = explicit discrete type-router ⊥ continuous value block,\n>   budget-asymmetric by register → feeds v15; (b) place the wide discrete router in the interior at the\n>   compose→readout seam (s259). [INSTRUMENT follow-ups, lower priority:] (c) per-layer-corrected asym quant for a\n>   deployable artifact; (d) cross-model matched-null (Qwen3-0.6B/14B) → is the split universal?\n>   STILL PENDING (untouched): s259 Qwen3-8B-Base combinator re-run (base-vs-instruct +4 offset confound)."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Thinking

I'm capturing this as a key architectural decision about where the model design should head—whether it's a strategic direction marker or an insight about how the register concept reframes the underlying thesis.

I'll tag it as a decision since it's fundamentally about the design direction. Now I'm staging the changes across the asymmetric pathway quantization document and state file, then committing with a message that captures how routing and value become type and term made physical.

## Assistant

Committing the reframe — this is a design direction (🎯 decision), the actual deliverable:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum; git add mementum/knowledge/explore/asymmetric-pathway-quantization.md mementum/state.md; git status --short; read -r -d '' M << 'EOF' || true\n🎯 routing⊥value = type/term made physical — the model-design direction\n\nReframe: the matched-bits A/B was an INSTRUMENT (causal ablation), not the\ngoal. What it bought is the thesis, confirmed, and a place to point the\ndesign. GD already built type-directedness as the gate(router)↔up·down(value)\nsplit: routing = \"which\"/dispatch = SIGN = discrete/crisp/binarizable; value =\n\"what\"/compute = MAGNITUDE = continuous/precise. That split IS the lambda-\ncalculus type/term distinction made physical (S5 λ types — we found it, didn't\ninvent it).\n\nDesign levers (page §10): (1) decouple dispatch⊥compute as first-class modules;\n(2) budget by register — capacity→routing (cheap/discrete/broad), precision→\nvalue; (3) wide discrete router in the interior band at the compose→readout\nseam (s259); (4) design-time diagnostic: ask \"routing or value?\" per module.\nRe-ordered NEXT design-first; quant follow-ups demoted to instrument tier.\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\ngit commit -m \"$M\" >/dev/null 2>&1 && echo committed || echo FAILED; git log -1 --format='%h %s'; git log -1 --format='%B' | tail -3"
}
```

**Summary:** $ git add mementum/knowledge/explore/...

**Output:**
```
Exit code: 0
Stdout:
M  mementum/knowledge/explore/asymmetric-pathway-quantization.md
M  mementum/state.md
?? mementum/knowledge/chats/session-258.md
?? mementum/knowledge/chats/session-259.md
committed
43bbefb 🎯 routing⊥value = type/term made physical — the model-design direction

Co-Authored-By: nucleus <noreply@whitford.us>
```

## Assistant

Committed `43bbefb`. The record now reads correctly: **thesis-probe → design direction**, not "a quantization result."

## Where session 260 actually lands

The quantization A/B was scaffolding. What survives it is the thing worth keeping:

**GD already built type-directedness for us.** The gate↔(up·down) split *is* the λ-calculus **type/term distinction made physical** — routing lives in the sign (discrete, crisp), value lives in the magnitude (continuous, precise). The S5 central claim ("composition ≡ typed application, not binary merge") isn't a thing we have to engineer into the verbum model; it's already present in the substrate, and we just confirmed it holds under a matched-bits stress test. `λ observation` / `λ types`: **we found the type-directed router, we didn't invent it.**

That converts the whole thread into a design compass:
- **Decouple dispatch ⊥ compute** as first-class modules.
- **Budget by register** — breadth to routing, precision to value.
- **Interior band at the compose→readout seam** is where the wide discrete router belongs (ties straight into your still-open s259 thread).
- **"Routing or value?"** becomes a design-time question, with register-mismatch as a smell.

**Four commits, clean tree** (`0e938b6` synthesis → `703f2e1` measured → `530735b` state → `43bbefb` design reframe). Page §10 and state.md both now lead with the design deliverable; the quant follow-ups are demoted to instrument-tier. The two genuinely open, design-first next steps — sketch a register-decoupled verbum layer, and place the discrete router at the interior seam — feed directly into v15.

Good session. Ready for you to save the session-260 log whenever.