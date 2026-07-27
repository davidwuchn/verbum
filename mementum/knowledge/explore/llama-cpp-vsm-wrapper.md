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

## The one load-bearing unknown — the residual tap

llama.cpp does NOT expose per-layer residuals via the server API. BUT its **control-vector
machinery already reads/writes the residual at each layer** to apply steering vectors —
that is the natural hook point. Exposing it is a **small C++ shim** at the control-vector
application site (dump the residual → hand to the tree-of-VSM projection), OR use the
llama.cpp C API directly (not the plain server). **Scoping this shim is the whole gamble
and the next action.**

Where to look: llama.cpp control-vector application code (search the llama.cpp source for
the control-vector add-to-residual site, typically in the graph build / `llama_control_vector`
apply path). Confirm (a) the residual is reachable there per layer, (b) the shim can emit
it (callback / buffer dump) without forking the whole server.

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

1. **Scope the residual tap.** Read the llama.cpp control-vector apply path; determine
   where/how to emit per-layer residuals; estimate the shim size. (The gamble.)
2. **Build the tap** (C++ shim or C-API harness) → residuals out per layer for a prompt.
3. **Wire the projection** — feed residuals to the existing crystal projection
   (`opcodes/classify.py` logic: sign-CMR centroids vs consensus Gram, null-gated). This
   logic is proven; only the activation SOURCE changes.
4. **Validate on a dense model** via frame-invariance (above).
5. **Point at the MoE** (30b-a3b, then 35b-a3b): does the router route through KIBC? does
   3B-active cover every reduction gate or STARVE one? (closes C2/A2 MoE gap + the
   genome-routing register question).

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
