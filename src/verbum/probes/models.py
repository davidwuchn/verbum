"""Model registry — the known compiler-probe fleet, one config each.

The registry IS the gravity (AGENTS.md ``λ emerge``: name ∧ link ∧ shape ≡
attractor). A new model lands here as a :class:`~verbum.probes.harness.ModelConfig`
(~15 lines) and experiments import it; reuse becomes the shortest path
(``λ one_way``). ``ModelConfig`` stays a public dataclass, so a genuinely
one-off model can still be built inline.

Fleet (llama.cpp servers on localhost — port assignment is fluid):

  QWEN36       qwen36-35b-a3b   :5100  chat        BASE REFERENCE (s256 pivot target)
  VIBETHINKER  vibethinker-3b   :5102  completion  manual <|im_start|>, </think> parse
  QWYTHOS      qwythos-9b       :5103  chat        server-split reasoning_content

  ORNITH is the ornith-35b-a3b fine-tune spec (held for reference); as of s259 the
  base reference qwen36-35b-a3b serves on :5100 (the s256 "extract from the base"
  pivot). llama.cpp ignores the request ``model`` field; ``/v1/models`` reports the
  alias ``qwen35-35b-a3b``.

The embedding model (``qwen3-embedding-8b`` :5101) is **not** a ``ModelConfig`` —
it has no template, no reasoning split, no grading register; its job is
``/v1/embeddings`` for semantic recall, not lambda generation. Documented as
:data:`QWEN3_EMBED` (a plain endpoint string) so the fleet stays discoverable in
one file without polluting the compiler-probe abstraction (one register typing).

License: MIT.
"""

from __future__ import annotations

from verbum.probes.harness import (
    ModelConfig,
    parse_think_tag,
    split_reasoning_field,
)


def qwen_chatml_template(system: str, sentence: str) -> str:
    """Qwen ChatML prompt for the completion transport (manual templating)."""
    return (
        f"<|im_start|>system\n{system}<|im_end|>\n"
        f"<|im_start|>user\n{sentence}<|im_end|>\n"
        f"<|im_start|>assistant\n"
    )


# ── compiler-probe fleet ─────────────────────────────────────────────────────

QWEN36 = ModelConfig(
    name="qwen36-35b-a3b",
    endpoint="http://localhost:5100",
    transport="chat",
    reasoning_extract_fn=split_reasoning_field,
    arch="35B-A3B MoE BASE reference model (s256 pivot: extract from the base, "
    "not the fine-tune). Serves on :5100; /v1/models alias 'qwen35-35b-a3b'.",
)

ORNITH = ModelConfig(
    name="ornith-35b-a3b",
    endpoint="http://localhost:5100",
    transport="chat",
    reasoning_extract_fn=split_reasoning_field,
    gguf_path="/Users/mwhitford/localai/models/ornith/ornith-1.0-35b-Q8_0.gguf",
    arch="35B-A3B MoE, multimodal reasoner (n_vocab 248320, n_embd 2048, ctx 262144)",
)

VIBETHINKER = ModelConfig(
    name="vibethinker-3b",
    endpoint="http://localhost:5102",
    transport="completion",
    reasoning_extract_fn=parse_think_tag,
    template_fn=qwen_chatml_template,
    gguf_path="/Users/mwhitford/localai/models/vibethinker/vibethinker-3b-q8_0.gguf",
    arch="qwen2 3B, RL-tuned reasoner (36L, d=2048, d_ff=11008, n_vocab 151936)",
)

QWYTHOS = ModelConfig(
    name="qwythos-9b",
    endpoint="http://localhost:5103",
    transport="chat",
    reasoning_extract_fn=split_reasoning_field,
    gguf_path=(
        "/Users/mwhitford/localai/models/qwythos/"
        "Qwythos-9B-Claude-Mythos-5-1M-MTP-Q8_0.gguf"
    ),
    arch="9B Qwen-family reasoner, multimodal (vision+video), 1M ctx, MTP",
)

BONSAI27B = ModelConfig(
    name="bonsai27b-ternary",
    endpoint="http://localhost:5104",
    transport="chat",
    reasoning_extract_fn=split_reasoning_field,
    gguf_path=(
        "/Users/mwhitford/localai/models/bonsai27b/"
        "Ternary-Bonsai-27B-Q2_g64.gguf"
    ),
    arch=(
        "PrismML Ternary Bonsai 27B — end-to-end ternary build of Qwen3.6-27B "
        "dense (48L, hybrid-attention ~75% linear). HF rev abbae7230. "
        "Weights {-1,0,+1} + group-wise FP16 scales; s268: the live probe of "
        "whether combinator competence survives 1.58-bit (holographic-llm.md)."
    ),
    quant="Q2_g64 (ternary, group-64 scales, ~1.71 bpw effective)",
)

# Embedding service — NOT a ModelConfig (see module docstring).
QWEN3_EMBED = "http://localhost:5101"  # qwen3-embedding-8b, /v1/embeddings

#: Discoverable registry of compiler-probe configs by short name.
#: QWEN36 (base reference) is the default live target on :5100.
REGISTRY: dict[str, ModelConfig] = {
    cfg.short(): cfg for cfg in (QWEN36, ORNITH, VIBETHINKER, QWYTHOS, BONSAI27B)
}
