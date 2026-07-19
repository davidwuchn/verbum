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

## The pipeline (fingerprint → crystal → trace)

Most of this already works and is model-agnostic; the goal here is to wrap it in
an **auto-detecting** system so it runs on any model without hand-editing paths.

1. **Detect** (`topology.py`) — auto-detect the model config: the transformer
   layer container, the per-layer gate module, and the MLP *register*
   (`gated-dense` | `moe` | `ungated`). Honest by construction: MoE is a
   *different* register (named, not silently reused); un-gated architectures
   (GPT-NeoX) have no routing-gate crystal to read and the detector says so.
2. **Fingerprint** (`fingerprint.py`, planned) — run the crystal probes, capture
   gate features, build the per-model 9×9 Gram and the crystal-bearing layers.
   *This is finding the lattice.*
3. **Calibrate + classify** (`classify.py`, promoted from
   `scripts/instruments/relational_opcode.py`) — the validated,
   null-gated opcode reader: sign(gate) routing register, common-mode removal,
   relational centroids vs the consensus crystal, permutation-null z-scoring
   (a token can NO-OP). Already model-agnostic.
4. **Trace** (`monitor.py`, promoted from `opcode_monitor_v2.py`) — per-token,
   per-layer opcode trajectory (the C→B program), with the gate-confound and
   retrieval-silence controls that keep it from manufacturing signal.
5. **Visualize** (planned) — the streaming lattice + opcode trajectory.

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

Foundational. `topology.py` (auto-detection) is the first module. Everything
downstream already exists in the parent repo and will be promoted here as the
system takes shape.
