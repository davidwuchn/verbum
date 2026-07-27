---
title: "llama.cpp tree-of-VSM wrapper — read the crystal on the real host (MoE pivot)"
status: designing
category: explore
tags: [moe, llama-cpp, tree-of-vsm, wrapper, control-vector, residual-tap, opcode-trace,
       frame-invariance, control-plane, register-read, 35b-a3b, 30b-a3b]
related:
  - control-plane-path.md
  - signal-processing-tensors.md
  - ../crystal-universality.md
  - ../two-registers-of-topology.md
depends-on:
  - control-plane-path.md
created: session 274
---

# llama.cpp tree-of-VSM wrapper

> Session 274 (Michael-directed pivot). The verbum PyTorch opcode instrument cannot
> read the crystal from a large MoE on this box: MPS breaks, CPU is 12h. The fix is
> structural — stop re-running the forward in transformers; let **llama.cpp be S1**
> (it runs the MoE natively + fast) and **wrap it with the tree-of-VSM as the readers
> tier (S2/S3)**, tapping the residual stream via llama.cpp's control-vector hook
> point. This is not a workaround — it IS the control-plane deliverable, arriving
> early because the research instrument fell over.

## ✅ VALIDATED (session 275) — read path built + frame-invariance CONFIRMED

The read-only milestone is **done and validated on the real host**. Pristine
attachment: llama.cpp built once (cmake 4.4 via `uv tool install cmake`; Metal,
`~/src/llama.cpp` UNMODIFIED); the tap links only the built public dylibs.

- **Tap built** — `wrapper/vsm_tap.cpp` (+ `CMakeLists.txt`): sets
  `llama_context_params.cb_eval` to a dumping callback via the PUBLIC C API only
  (no libcommon), regex-filters tensor names, requests all-position outputs
  (`batch.logits[i]=1`, defeats the final-layer `n_outputs` prune),
  `llama_memory_clear` per prompt (independent forwards), dumps raw f32/i32 +
  `manifest.json`. `--prompts-file` batch mode loads the GGUF ONCE.
- **Loader** — `wrapper/tap_loader.py`: `manifest.json` + `<reg>-<layer>.bin` →
  `{layer: [T, d]}`. ggml is contiguous in ne[0], so reading `ffn_gate` ne=[n_ff,
  n_tok] as `(n_tok, n_ff)` is EXACTLY the `[T, d]` classify.py wants — no transpose.
- **Frame-invariance** — `wrapper/frame_invariance.py`: same 108 crystal probes
  through both frames (transformers hooks on `Qwen/Qwen3-0.6B` @ MPS vs `vsm_tap`
  on the f16 GGUF), sign-CMR 9×9 Gram per layer, cross-frame `offdiag_corr`.

  **RESULT (`results/frame-invariance/qwen3-0-6b/frame_invariance.json`):**
  cross-frame Gram corr **mean 0.9997, median 0.9998, min 0.9992** across all 28
  layers; per-layer `tf~consensus` and `lc~consensus` track to ~3 decimals. The
  llama.cpp tap reads the SAME crystal as transformers — residual deviation is
  just fp16(GGUF) vs bf16(transformers). **Wrapper validated + independent C2
  frame-invariance confirmation across the transformers↔llama.cpp numeric boundary.**

Corrections to the s274 design below: the tap is even MORE pre-built than recorded
(a full `examples/debug/debug.cpp` + `common_debug_cb_user_data` with a
`--tensor-filter` CLI already exists — we still wrote our own pristine dumping tool
to avoid modifying their tree); the layer index is IN the tensor name
(`ffn_gate-15` via `ggml_format_name`); `find_package(llama)` from the build tree
mis-resolves includes (assumes install prefix) so we link the dylibs by path; the
WRITE path also exists — `llama_set_adapter_cvec` → per-layer `ggml_add` (`build_cvec`)
= the driver/algedonic tier, unbuilt, next tower.

## What happened (the instrument facts, corrected)

Goal: first-ever MoE opcode-trace, to close the C2/A2 MoE-register gap (registry is
all-dense; `topology.py` claims a `moe` register but it was never exercised on a real
MoE) and to test whether the 35b-a3b routes through the KIBC crystal.

Ran `opcodes/trace.py --model Qwen/Qwen3-30B-A3B --smoke` (cached MoE proxy for the
design-target Qwen3.6-35B-A3B):
- **MPS:** `NotImplementedError: "histogram_mps" not implemented for 'Int'` — Qwen3-MoE's
  `grouped_mm_experts_forward` calls `torch.histc` on Int, which Metal lacks. NOT caught
  by `PYTORCH_ENABLE_MPS_FALLBACK=1` (that only catches *entirely missing* ops; `histc`
  has an MPS kernel that just rejects Int).
- **CPU:** WORKS — but ~12h (30B, even at A3B=3B active, is slow on CPU). Michael killed
  it; it did NOT fail. **Key datum: the opcode instrument's MoE logic is SOUND** — topology
  detected the register, capture ran, it was grinding forwards. Only two problems remain:
  the MPS `histc` op-gap and CPU speed.

Conclusion (λ fix): cause is structural (transformers/torch on a large MoE on Apple
Silicon), not a bug. Redesign > patch.

## The pivot — tree-of-VSM wraps the parent on the llama.cpp host

Every failure was **transformers running the MoE forward**. But **llama.cpp already runs
this MoE natively, fast, correctly** (mature C++ MoE; mmap + quant; no `histc`/MPS gap;
35b-a3b already serving there). So:

- **llama.cpp = S1** (the parent, does the compute — correctly).
- **tree-of-VSM = S2/S3** wrapper (readers tier): tap the residual stream, project onto
  the crystal centroids (`opcodes/data/consensus_gram.json` / `model_vsm.json`), gate.

This is exactly `control-plane-path.md` (parent=S1, our tensors=S2/S3) and
`signal-processing-tensors.md` (the tree-of-VSM IS a signal-processing tensor). Reading on
the **actual deployment host** means the crystal we measure is the one that ships — better
than a research-only transformers artifact this box can't even load fast.

## The residual tap — SOLVED via cb_eval + eval-callback (s274, verified in local source)

NOT a from-scratch shim. llama.cpp exposes a first-class eval callback and an official
example that dumps per-node tensor data. Verified against `~/src/llama.cpp`:
- **Public API:** `llama.h:332` — `ggml_backend_sched_eval_callback cb_eval;` +
  `cb_eval_user_data;` in `llama_context_params`. The callback fires on EVERY graph node
  during eval, with the operation + tensor data. Set it when creating the context (C/C++
  program, not the plain server — the eval-callback example IS that program).
- **Template:** `~/src/llama.cpp/examples/eval-callback/eval-callback.cpp` (+ README,
  CMakeLists). It prints name/op/shape/values per node; we FILTER by tensor-name regex and
  DUMP instead of print.
- **The graph already names every tensor onto a verbum register** (from `src/llama.cpp`
  graph build, `cb(cur, "<name>", il)` per layer `il`):

  | verbum register | ggml tensor name |
  |---|---|
  | **gate** (opcode read = sign(gate_proj)) | `ffn_gate` (dense) / `ffn_moe_gate` (MoE) |
  | **MoE router** (answers the register + starvation Qs DIRECTLY) | `ffn_moe_topk` (selected experts), `ffn_moe_probs`, `ffn_moe_weights`, `ffn_moe_logits` |
  | **residual / j-space** | `l_out` (per-layer residual output) |
  | FFN out / attn-input norm / final | `ffn_out`, `attn_norm`, `result_norm` |

So the tap = adapt eval-callback to filter `{ffn_gate, ffn_moe_gate, ffn_moe_topk,
ffn_moe_probs, ffn_moe_weights, l_out}` and write them per-layer/per-token to disk. The
MoE-register question ("does the router route through KIBC? does 3B-active cover every gate
or STARVE one?") is answerable directly from `ffn_moe_topk` (which experts fired) ×
`ffn_moe_gate` (their gate activations) × `ffn_moe_weights`.

Open detail (minor): a clean **attn-write** tensor name wasn't spotted in the grep
(`attn_norm`/`l_out`/`ffn_out` are named; the out_proj output may be fused). Resolve by
reading the attn block in `src/llama.cpp` graph build — but the GATE register (where the
opcode read lives) is nailed, so this doesn't block the first read.

## The de-risk (frame-invariance validation — rigor for free)

The crystal Gram is **frame-invariant** (C2, `crystal-universality.md`). So before trusting
the wrapper on the MoE:
1. Read residuals via the llama.cpp tap on a DENSE model we've ALREADY transformers-traced
   (Qwen3-0.6B or Qwen3.6-27B).
2. Project onto the crystal; compute the Gram.
3. Compare to the committed transformers-traced Gram (`results/opcode-trace/<model>/`).
- **Match** → wrapper validated + an INDEPENDENT frame-invariance confirmation across the
  transformers↔llama.cpp numeric boundary (a bonus C2 result).
- **Mismatch** → itself a finding about the frame; investigate before trusting MoE reads.

## Next actions (pick up here)

1. ✅ **DONE (s275)** — tap built (`wrapper/vsm_tap.cpp`), pristine public-API attachment.
2. ✅ **DONE (s275)** — projection wired (`wrapper/tap_loader.py` → `opcodes/classify.py`).
3. ✅ **DONE (s275)** — frame-invariance CONFIRMED on dense Qwen3-0.6B (cross-frame Gram
   corr mean 0.9997). See the VALIDATED section above.
4. ✅ **MoE TAP VERIFIED (s275)** on the design-target `Qwen3.5-35B-A3B-Q8_0` (34GB, Metal).
   Registers fire: `ffn_moe_gate` ne=[n_ff=512, n_expert_used=8, n_tok], `ffn_moe_topk` [8,n_tok]
   i32, `ffn_moe_weights` [1,8,n_tok], `ffn_moe_probs` [n_expert=256, n_tok], `l_out` [2048,n_tok].
   The genuinely-new loader bit is DONE + tested: `tap_loader.load_moe_gate_effective` combines
   the selected experts by router weight — `gate_eff[t]=Σ_e w[e,t]·ffn_moe_gate[:,e,t]` → [T,512]
   per layer (40 layers, finite, sane sign balance). So the wrapper READS THE CRYSTAL FROM A MoE
   — which `opcodes/capture.py` explicitly refuses. (Also: tap now skips ggml `(reshaped)` view
   aliases.) Invocation: `./wrapper/build/vsm_tap --model <moe.gguf> --prompts-file <probes> --out <dir> -ngl 99`.
   ▶ **REMAINING**: run the full crystal-probe set through the 35B-A3B, calibrate the effective-gate
   Gram vs consensus + shuffled-label null = the actual C2/A2 answer (does the router route KIBC?
   does 3B-active starve a gate? read `ffn_moe_topk` coverage per combinator). Not yet run.
5. **Resolve the attn-write name** (attn block in `src/llama.cpp` graph build) if the
   two-register read is wanted; not needed for the gate-register crystal read.
6. **Driver tier (later tower)** — `llama_set_adapter_cvec` per-layer additive write is the
   S3/algedonic driver; E4-gated. The read tap validated the frame the driver would write into.

## Fallbacks (if the shim proves expensive)

- **MPS `histc` patch** (tactical, throwaway): monkeypatch the failing `histc` to run on
  CPU for that one tiny per-layer tensor (num_experts bins → negligible round-trip), keep
  the rest on MPS. Risk: whack-a-mole — may reveal the next MPS gap in the MoE path. Gets
  a number, builds nothing.
- **CPU overnight** (known-good, ~12h): just works; run `--device cpu` and wait.

## Why this is the right call (not just a dodge)

The wrapper wins on all three axes at once: **fast** (llama.cpp runs MoE natively),
**robust** (no torch/MPS gaps to whack), and it **IS the deliverable** (the control-plane
readers tier reified on the real serving host). The instrument failure made the case for
building the ship instead of polishing the scaffold. And the CPU run — by *working* before
it was killed — proved the crystal-projection logic is sound on MoE, so the only genuinely
new thing to build is the residual tap.
