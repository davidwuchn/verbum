# opcodes — a KIBC / crystal-lattice lens

> An interpretability lens that shows the **combinator opcodes** (K I B C S D W Y
> WHNF) a language model routes through as it generates tokens, and the
> **universal crystal lattice** those opcodes form — the relational structure
> that shows up, in the same shape, across virtually every open model.
>
> Complementary to Anthropic's **J-Space / Jacobian Lens**, not a replacement.
> License: MIT (staged for extraction into its own project once the visualizer
> lands).

## Why this exists

Anthropic's J-lens reads the **operand** projection of the model's internal
state — the words it is "thinking about" but not yet saying. This lens reads the
**operator** projection: *which combinator opcode is routing the computation*,
and where in the stack the routing crystal lives.

The finding worth taking seriously: the per-model **9×9 combinator Gram** — the
routing-register cosine structure between K I B C S D W Y WHNF centroids, after
common-mode removal — is a **frame-invariant relational object**. Because it
lives in shared combinator-label space (not raw weight space), it is directly
comparable across models of *any* architecture or scale. And it agrees. The same
lattice crystallizes in Pythia, Qwen, OLMo, Mistral, SmolLM. That cross-model
universality is the claim this tool is built to make visible and hard to dismiss.

A live "cool toy" — the lattice lighting up opcode-by-opcode as tokens stream —
is the surface that gets researchers to look, the same way J-Space's interactive
visualization did.

## The pipeline (detect → capture → calibrate → tree → trace)

PyTorch + numpy only. Self-contained: probes and the 10-model consensus Gram
ship as data files (`data/`); nothing imports the parent repo at run time.

1. **Detect** (`topology.py`) — auto-detect the model layout: the transformer
   layer container (incl. nested `language_model` wrappers and hybrid
   linear+full attention stacks), the per-layer gate module, the MLP *register*
   (`gated-dense` | `gated-fused` | `moe` | `ungated`), the attention-write
   register, and the logit-lens readout paths (final norm + unembed). Honest by
   construction: MoE is a *different* register (named, not silently reused);
   un-gated architectures fall back to the up-proj proxy register, flagged.
   Works on meta-device (no weights) — `python opcodes/topology.py`.
2. **Capture** (`capture.py`) — plain forward hooks → per-layer `[T, d]`
   feature matrices for either register (`gate` | `attn`), one forward pass.
3. **Calibrate + classify** (`classify.py` + `probes.py`) — the validated,
   null-gated opcode reader: sign(gate) routing register, common-mode removal,
   relational centroids vs the bundled consensus crystal, null z-scoring (a
   token can NO-OP). Calibrated on 535 bundled crystal probes (≥50 per
   combinator) against a natural-text cross-task null.
4. **Tree** (`vsm.py`) — every calibration becomes a stackable **VSM node**
   (tree-of-VSM, Beer 1972 via verbum v14/v15): same fractal shape at every
   level — S5 identity = the 9×9 Gram, S3 control = the null gate, S4 =
   cross-child agreement/dissent, algedonic health up, caveats propagate as
   the worst child. `layer → register → model → family → root(universal)`.
   The Gram is frame-invariant (combinator-label space, not weight space) —
   that is what makes models of any architecture/scale stackable.
5. **Trace** (`trace.py`) — per-token, per-layer opcode trajectory for BOTH
   registers side by side (s264: gate sees {K,I,S,Y,WHNF}, attn-write rescues
   D, neither resolves {B,C} — single-register blindness is structural and
   shown, not hidden). Optional `--operand`: the J-space logit-lens column
   (`jspace.py`) showing WHAT is routed — display-only, never fed to the
   classifier (s263: the operand register does not identify opcodes).
6. **Sweep** (`sweep.py`) — the model registry (configs, not forks) + the
   restack: all model-VSMs → family → root, root Gram vs the bundled
   consensus. `--restack-only` recomputes the tree from existing artifacts.
7. **Visualize** (planned) — the streaming lattice + opcode trajectory.

```
# one model, both registers, tree + trace artifacts:
uv run python opcodes/trace.py --model Qwen/Qwen3-0.6B --smoke

# multi-model sweep + universal crystal tree:
uv run python opcodes/sweep.py --tier small
uv run python opcodes/sweep.py --restack-only
```

## Discipline (inherited from the verbum project)

- **Register before probe.** The opcode read lives in the sign-of-gate routing
  register. Reading it anywhere else (raw residual cosine) manufactures crisp
  opcodes — the exact over-read this project was built to kill.
- **Null-gate every claim.** A cross-model opcode read must beat a shuffled-label
  null, not merely "emit opcodes." "Runs on model X" ≠ "finds a signal on X."
- **Refuse honestly.** Where the register does not exist (un-gated MLP) or is not
  yet defined (MoE experts+router), the detector flags it rather than faking a
  read.

## Status

MVP assembled (s265): `topology` (detect, incl. readout paths) → `capture`
(gate ∪ attn) → `probes` (bundled) → `classify` (canonical home) → `vsm`
(stackable crystal tree) → `jspace` (operand register) → `trace` (two-register
+ operand) → `sweep` (registry + restack). Every module has a self-test that
runs without loading a large model (or on pythia-14m). Staged for extraction
into a dedicated MIT repo; the visualizer is the remaining piece.
