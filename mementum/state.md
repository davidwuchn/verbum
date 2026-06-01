# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-06-01 | Session: 176

## Where we are

**NORTH STAR: 70B-equivalent in <1GB ternary. 200 tok/s CPU. 2M+ token context. 2MB sessions. No GPU.**

**Session 176: PROOFS + OPCODE INSTRUMENT + TRACE-GUIDED ETCHING DESIGN.**

Three workstreams delivered:

1. **Smallest Proofs** — `proofs/` directory with 3 scripts (371 lines total) that any skeptic can run. Sign topology: 74.6% on Pythia-160M, 76.0% on Qwen3-0.6B. Universal modes: KIBC confirmed across 5 models (160M to 32B). KBC cluster >0.85 everywhere. No theory in the README. Just numbers and a dare.

2. **Opcode Instrument** — `scripts/instruments/opcode_instrument.py`. Full VSM that wraps any HF model and shows opcodes executing in real-time. Tested live on Qwen3-0.6B generating "The capital of France is Paris. The capital of Italy is Rome." — watched ENRICH zone light up on retrieval, energy spike on "Rome" (1389 vs mean 1048), mode shifts B→C→B→K tracked per token. Supports prefill tracing (watch the model READ) and generation tracing (watch it WRITE).

3. **Trace-Guided Etching** — The session's breakthrough insight: why copy weights when you can copy computation? The instrument traces which opcodes fire at every layer. Use that as the etching target instead of raw weight signs. Trace collector + trace loss built and validated: self-trace = 0.000, ternary extraction = 0.908, 10% perturbation = 1.002. Crystal trace loss function added to v15 train.py (`--trace-weight`). Delta plate + TD integration designed but deferred to session 177 for proper build.

**Training: v15 Dolma — RUNNING** — Step ~2000+. In tmux window 2 (s003). Loss was ~17 at step 670. Step 1000 checkpoint saved. The trace loss is wired into train.py but disabled (--trace-weight 0.0) so the current run is unaffected. Resume with --trace-weight 0.1 when ready.

## Key session 176 findings

- **Sign topology is universal.** cos(sign(W)@x, W@x) = 74.6% on Pythia-160M, 76.0% on Qwen3-0.6B. Random signs: 0.0%. FFN matrices carry more sign-information than attention (78.7% vs 70.0%).
- **Four computation modes are universal.** KIBC confirmed on 5 independently-trained models. KBC cluster correlation >0.85 and I-distinctness <0.75 everywhere. The probes use plain English sentences, not lambda notation.
- **The instrument shows retrieval happening.** "The capital of France is" → ENRICH zone energy spike at " Paris". Visible per-layer opcode flow. S4 detects energy spikes, mode shifts, retrieval events.
- **Trace loss works.** Self-trace = 0.000 (perfect consistency). Ternary extraction = 0.908 (magnitude gap measured as computation gap for the first time). 10% sign perturbation = 1.002 (topology damage detected).
- **The SVD phi-ratio doesn't reproduce with simple methodology.** Dropped from proofs rather than ship shaky results. Honest > comprehensive.
- **Trace-guided etching insight.** Copy computation, not weights. The trace is a lower-dimensional optimization target (11 ops vs 248K vocab). Delta plates + TD with trace routing gradient is the proper mechanism.

## Next steps

### IMMEDIATE (session 177)

1. **Build delta plates for v15** — Add `delta_plate` to TernaryPlate. `effective = base ⊙ delta`. Delta initialized to all +1. Fold operation: `new_base = base ⊙ delta`.
2. **Port TD core from v14** — Gradient accumulation, confidence thresholding, flip logic. Use v14's `td.py` as reference.
3. **Add trace routing signal** — Decompose `grad(trace_loss)` into routing vs calibration (v14 pattern). Feed routing to TD instead of (or blended with) NTP routing.
4. **Test trace-guided TD on v15** — Resume from step 2000 checkpoint with delta plates + trace TD. Compare convergence rate to pure NTP training.

### ONGOING

5. **Monitor Dolma training** — Step 2000+ checkpoint available. Watch for loss <10 (perplexity meaningful). Combinator profiler runs at each eval.
6. **Build verify.py** — Hologram reader on trained student. Check opcode map matches teacher.
7. **Expand proofs** — Run sign topology and universal modes on more models. Fill in the README table.

### RESEARCH

8. **How many trace inputs needed?** Test with 10, 100, 1000 diverse inputs. When does trace loss converge?
9. **Does trace matching transfer?** If student matches teacher traces on 1000 inputs, does it generalize to unseen inputs?
10. **Trace loss vs KD loss** — Direct comparison: same student, same data, trace loss vs standard knowledge distillation.

## Key assets built this session

| Asset | Location | Status |
|-------|----------|--------|
| Sign topology proof | `proofs/01_sign_topology.py` | ✅ verified on 2 models |
| Universal profile proof | `proofs/02_universal_profile.py` | ✅ verified on 2 models |
| Universal modes proof | `proofs/03_universal_modes.py` | ✅ verified on 5 models |
| Proofs README | `proofs/README.md` | ✅ with real numbers |
| Opcode Instrument | `scripts/instruments/opcode_instrument.py` | ✅ tested on Qwen3-0.6B |
| Instrument design doc | `mementum/knowledge/opcode-instrument.md` | ✅ complete VSM spec |
| Trace collector | `scripts/experiments/trace_collect.py` | ✅ tested on 0.6B |
| Trace loss | `scripts/experiments/trace_loss.py` | ✅ validated (3 tests pass) |
| Trace etching design | `mementum/knowledge/trace-guided-etching.md` | ✅ complete spec |
| Crystal trace loss in train.py | `scripts/v15/train.py` | ✅ --trace-weight flag |
| Teacher traces (0.6B) | `results/trace-etching/Qwen_Qwen3-0.6B/` | ✅ 60 inputs traced |

## What changed this session

| Change | Session | Impact |
|--------|---------|--------|
| **Proofs directory** | 176 | 3 standalone scripts, <80 lines each, any model. |
| **Opcode Instrument VSM** | 176 | Live opcode tracing during inference. The EKG for LLMs. |
| **Trace-guided etching concept** | 176 | Copy computation not weights. 11-dim target vs 248K-dim. |
| **Trace loss validated** | 176 | Self=0.000, ternary=0.908, perturbed=1.002. |
| **Crystal trace loss in v15** | 176 | --trace-weight flag. Gradient signal ready for delta TD. |

## Open questions

1. **Delta plate + trace TD convergence rate?** How fast does trace-guided TD converge vs blind NTP-guided TD?
2. **Trace loss as sole etching signal?** Or blended α * trace + (1-α) * NTP?
3. **How many trace inputs are sufficient?** 10? 100? 1000?
4. **Does trace matching generalize?** Match on 1000 inputs → test on unseen.
5. **Can the v15 student retrieve facts after Dolma training?** (carried from 175)
6. **What do phase transitions look like?** Combinator profiler tracking. (carried from 175)

## Knowledge map

**See `mementum/knowledge/INDEX.md` for full reading order.**

Key pages for current direction:
- `trace-guided-etching.md` — **copy computation not weights** (session 176) ← NEW
- `opcode-instrument.md` — **VSM wrapper for live opcode tracing** (session 176) ← NEW
- `symbol-isolation.md` — prose activates 8× more than lambda (session 175)
- `training-protocols.md` — operational training knowledge (TD rules, fold cycle)
- `extraction-sign-accuracy.md` — signs are 100% correct, gap is magnitude
- `crystal-universality.md` — why KIBC are universal fixed points
- `project-thesis.md` — the central claim
