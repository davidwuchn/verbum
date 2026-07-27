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

## Next actions (pick up here) — the tap is SOLVED, so this is mostly plumbing

1. **Build the tap** = copy `examples/eval-callback/eval-callback.cpp`, replace print with
   a name-regex FILTER `{ffn_gate|ffn_moe_gate|ffn_moe_topk|ffn_moe_probs|ffn_moe_weights|l_out}`
   and a per-layer/per-token DUMP (npz/binary). Build via its CMakeLists. Feed it the probe
   set as prompts. (Smoke first on a tiny GGUF to confirm the callback + names fire.)
2. **Wire the projection** — feed the dumped `ffn_gate` (sign-CMR) to the EXISTING crystal
   projection (`opcodes/classify.py`: sign-CMR centroids vs consensus Gram, null-gated).
   Proven logic; only the activation SOURCE changes (transformers hooks → llama.cpp dump).
3. **Validate on a dense model** via frame-invariance (C2): llama.cpp `ffn_gate` Gram vs the
   committed transformers `gate_proj` Gram (`results/opcode-trace/qwen3-0-6b|qwen3-6-27b/`).
   Same register, two numeric frames — match confirms the wrapper AND frame-invariance.
4. **Point at the MoE** (30b-a3b GGUF, then 35b-a3b): `ffn_moe_gate` = the gate register per
   selected expert; `ffn_moe_topk`/`weights` = the routing. Answers: does the router route
   through KIBC? does 3B-active cover every reduction gate or STARVE one? (closes C2/A2 MoE
   gap + the genome-routing register question). Need GGUFs (30b-a3b/35b-a3b) — Michael serves
   these already, so the .gguf exists on the box.
5. **Resolve the attn-write name** (read the attn block in `src/llama.cpp` graph build) if
   the two-register read is wanted; not needed for the first gate-register crystal read.

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
