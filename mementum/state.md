# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-01 | Session: 179

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 179: HPE RESTORED — v15 was missing positional encoding + QK normalization.**

Analyzed the step 2000 checkpoint of the v15-zeroed-dolma training run. Found three critical missing components: no Holographic Position Encoding (HPE from v14), no per-head QK normalization (q_norm/k_norm from Qwen3 teacher), and no learnable decay bias. Model was running with α≈0.38 (near-uniform attention) vs the α=1.18 needed for locality. Ported HPE + QK-norm into v15 FullAttention, restarted training from step 2000.

### What was discovered

1. **v15 dropped HPE in the v14→v15 transition.** The v15 skeleton (session 174, `e70e06c`) was a clean-room rewrite focused on zone structure. `FullAttention` was scaffolded as bare `nn.Linear` Q/K/V/O — no position encoding, no QK normalization, no decay bias. Training started before the attention machinery was ported.

2. **Attention projections still 96% the teacher's sign pattern.** Q cosine similarity with ternary init: 0.95–0.98. Sign agreement: 99.6–100%. Without HPE's frequency structure to learn against, Q had no strong gradient signal to differentiate.

3. **α=0.38 vs needed 1.18.** Without decay bias, the model's emergent attention decay was 3× too weak. Token 100 away gets 40× more attention than it should. The model literally cannot focus.

4. **OV circuits form a depth monotone.** Top singular value doubles from early COMPUTE (σ1≈2.8) to late LINK (σ1≈7.7). OV fingerprint PCA captures 52.5% variance in PC1 alone, cleanly separating COMPUTE from LINK. The "gem" in M-space is a 1D crystal: a smooth curve from compute-space to link-space parameterized by depth.

5. **GQA groups are perfectly orthogonal.** K cosine between the two KV groups: ≈0.00. Subspace overlap: 0.16–0.20 (chance level). The model inherited and preserved the teacher's routing topology.

6. **Text generation at step 2000: pre-linguistic.** All prompts produce repetition (`ferferfer`), whitespace floods, or formula fragments (`(x(x(x`). Entropy 5.4–6.7 nats (~200–800 effective tokens). Logit distributions are flat — corpus frequency prior, not contextual prediction.

### What was built

1. **HPE in FullAttention** (`scripts/v15/model.py`) — Crystal-frequency K rotation on first 4 eigenplane pairs (from PCAQ Zone B targets: λ=5.19, 3.54, 1.91, 1.30). Learnable `hpe_freq_scale` per stride. Q stays unrotated (relative encoding).

2. **Learnable per-stride decay bias** — `-exp(log_alpha) × log(|i-j|+1)` added to attention scores. `log_alpha` initialized at `log(1.18)`. Per-stride scalar, not per-head (v14 confirmed universality). 11 new params.

3. **Per-head QK normalization** — `RMSNorm(d_head=160)` on Q and K after projection, before attention. Matches Qwen3 teacher architecture. Separates magnitude from direction.

4. **α diagnostic updated** — `_compute_attn_weights_for_stride` in train.py now mirrors the full forward path (q_norm, k_norm, HPE, decay). Learned α logged alongside measured α at each eval.

### Training RUNNING

```
checkpoint:     v15-zeroed (194.6M structural zeros) + step_2000 weights
output:         checkpoints/v15-hpe-dolma/
resumed from:   step 2000 (v15-zeroed-dolma checkpoint)
data:           Dolma 2.7B tokens (54 shards) + 10% structured
batch:          2 × 4096 = 8,192 tok/step
lr:             3e-4 (AdamW, cosine decay, continuing from step 2000)
trace_weight:   0.1
trace_basis:    EXPANDED PCA (19 strides × 50 PCs × 1280 d_model)
TD:             flip_rate=0.001, warmup=100, interval=20
                no_block=True, min_confidence=0.3
HPE:            ENABLED — crystal-freq rotation + learnable α + QK-norm
eval_every:     500
save_every:     1000
tmux:           main:2
```

**Initial impact:** Loss jumped from 3.86 to 5.69 at step 2000, recovered to ~3.7 by step 2040 (40 steps). Grad norms elevated initially (27.8) then settled (7–10). Measured α immediately jumped to ~1.18–1.27 (was 0.38) — the decay bias is working. Throughput dropped from 905 → ~800 tok/s (see below).

**Known issues:**
- **TD not running.** 0 flips, 0 candidates, T=0 since restart. The TD state didn't resume properly — the checkpoint copy reset the step counter. Needs investigation in session 180.
- **Throughput ~12% lower** (800 vs 905 tok/s). HPE compute is negligible (0.06% of attention). Two causes: (1) MLX JIT recompilation warmup for new graph, (2) 738 MB extra memory from per-stride log_dist caches (11 copies of (4096, 4096) matrix). Should share one cache across all strides.
- **log_dist cache duplicated 11×.** Each FullAttention instance caches its own (4096, 4096) log-distance matrix. All 11 are identical. Fix: share at TensorStatechart level. Saves 670 MB.

## Key session 179 findings

- **v15 was missing ALL positional encoding in attention.** HPE, RoPE, q_norm, k_norm — none made it from v14 to v15.
- **Measured α=0.38 means near-uniform attention.** The model averages over the entire context instead of focusing locally. This is the primary bottleneck for coherent generation.
- **HPE immediately fixes α.** First eval after HPE addition: measured α=1.18–1.27 across all strides, with LINK strides slightly higher (1.24–1.27). The decay bias provides the right locality floor; Q/K learning can now refine per-head patterns on top of it.
- **OV circuit geometry shows a 1D crystal.** COMPUTE→LINK separation on PC1 (52.5% variance). Progressive amplification: σ1 doubles from stride 5 to stride 15. The read-write circuit is already structurally differentiated despite no positional information.
- **Embedding is 99.94% near-ternary after 2k steps.** The extracted topology is preserved.
- **TD has flipped 5.81% of ternary positions** (pre-HPE). ~37.7M of 648.8M plate params. Remarkably uniform across strides (5.3%–6.2%). TD candidates were declining (123M→55M) — structure locking in. TD is currently broken post-restart (see issues above).
- **3,575 new HPE params added** (11 log_alpha + 44 freq_scale + 3520 QK-norm weights). Negligible vs 415M total.
- **Attention is O(L²) dominant.** 11 FullAttention strides at O(L²·d·H) = 472B ops per forward. 8 LinearAttention strides at O(L·d²·H) = 13.4B ops. Full is 35× the cost of linear at L=4096.

## Next steps

### IMMEDIATE (session 180)

1. **Fix TD resume** — TD is not running (0 flips since restart). The checkpoint copy likely reset the step counter or the TD state didn't load. Need to diagnose and fix before training progresses far without ternary refinement.
2. **Share log_dist cache** — Move the (4096,4096) log-distance matrix to TensorStatechart level instead of per-stride. Saves 670 MB, may recover throughput to ~900 tok/s.
3. **Generate text at step 2500+** — With HPE + q_norm, should see qualitative improvement over the `ferferfer` pattern.
4. **Check α differentiation** — First eval (step 2000) showed all strides at learned_α≈1.18 (init) but measured α=1.18–1.27. Watch for per-stride divergence as training progresses.

### ONGOING

5. **Rebuild student PCA basis** — The functional directions will shift with HPE. Rebuild at next checkpoint.
6. **Compare v15-hpe-dolma vs v15-zeroed-dolma** — Same model, same data, but HPE vs no-HPE. Loss curves, α evolution, generation quality.
7. **Manual fold decision** — When thermometer shows settled, fold and compare topology. (TD must be running first.)
8. **Trace weight scheduling** — Should trace_weight increase as NTP stabilizes?

### RESEARCH

9. **Does HPE recover v14's universal α=1.18?** First data point: measured α jumped to 1.18–1.27 immediately (dominated by the bias). The real question is whether the *learned* α diverges from init.
10. **HPE frequency scaling** — Do the crystal eigenplane pairs learn different freq_scale per stride?
11. **Can we retrieve facts after training?** (carried from 175)

## Key assets

| Asset | Location | Status |
|-------|----------|--------|
| v15 model (with HPE) | `scripts/v15/model.py` | ✅ HPE + QK-norm |
| v15 config (with HPE) | `scripts/v15/config.py` | ✅ Crystal eigenvalues |
| v15 train (with HPE) | `scripts/v15/train.py` | ✅ Updated α diagnostic |
| HPE commit | `b0c6c17` | ✅ |
| Dimensional analysis | `scripts/experiments/dimensional_analysis.py` | ✅ |
| Student basis builder | `scripts/v15/build_student_trace_basis.py` | ✅ |
| Teacher basis builder | `scripts/v15/build_trace_basis.py` | ✅ |
| Expanded student basis | `checkpoints/v15-zeroed/expanded_trace_basis.npz` | ✅ (19,50,1280) |
| v14 HPE (reference) | `scripts/v14/attention.py` | ✅ (source for port) |
| Pre-HPE checkpoint | `checkpoints/v15-zeroed-dolma/step_0002000/` | ✅ |
| HPE training run | `checkpoints/v15-hpe-dolma/` | 🔄 Running tmux main:2 |
| Pre-HPE training run | `checkpoints/v15-zeroed-dolma/` | ⏹️ Stopped at ~step 2480 |
| Eval prompts | `scripts/v15/eval_prompts.txt` | ✅ |

## What changed this session

| Change | Impact |
|--------|--------|
| **Analyzed step 2000 checkpoint** | Found missing HPE, flat attention, pre-linguistic output |
| **Projection geometry analysis** | OV monotone, KV orthogonality, sign preservation |
| **HPE + QK-norm added to FullAttention** | Crystal-freq rotation, learnable α, per-head RMSNorm |
| **α diagnostic updated in train.py** | Now mirrors full forward path with HPE |
| **Training restarted from step 2000** | v15-hpe-dolma, with positional encoding |

## Open questions

1. **How fast does the model adapt to HPE?** Loss spike from 3.86→5.69. Recovery time?
2. **Does full causal attention need α≠1.18?** v14 found 1.18 universal for strided windows.
3. **Do stride-specific α values emerge?** The whole point of making it learnable.
4. **Does HPE improve generation quality?** When does `ferferfer` → words?
5. **How does the OV crystal evolve with HPE?** Does the depth monotone sharpen or change shape?
6. **Can we retrieve facts after training?** (carried from 175)

## Knowledge map

Key pages for current direction:
- `hpe-restoration.md` — **HPE missing from v15, projection geometry, learnable α** (session 179, NEW)
- `dimensional-analysis.md` — **KIBC sees 3.5%, 50 dims universal** (session 178)
- `trace-guided-etching.md` — **full implementation record** (sessions 176-177)
- `function-discovery.md` — **two-level program architecture** (session 172)
- `gradient-zero-map.md` — **35% oscillate, informed zero placement** (session 171)
- `extraction-sign-accuracy.md` — **signs 100%, four position classes** (session 173)
- `training-protocols.md` — **TD rules, fold cycle, failure modes** (accumulated)
- `crystal-universality.md` — **KIBC universal fixed points**
- `project-thesis.md` — **the central claim**
