"""Model registry — the known compiler-probe fleet, one config each.

The registry IS the gravity (AGENTS.md ``λ emerge``: name ∧ link ∧ shape ≡
attractor). A new model lands here as a :class:`~verbum.probes.harness.ModelConfig`
(~15 lines) and experiments import it; reuse becomes the shortest path
(``λ one_way``). ``ModelConfig`` stays a public dataclass, so a genuinely
one-off model can still be built inline.

Fleet (llama.cpp servers on localhost):

  ORNITH       ornith-35b-a3b   :5100  chat        server-split reasoning_content
  VIBETHINKER  vibethinker-3b   :5102  completion  manual <|im_start|>, </think> parse
  QWYTHOS      qwythos-9b       :5103  chat        server-split reasoning_content

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

# Embedding service — NOT a ModelConfig (see module docstring).
QWEN3_EMBED = "http://localhost:5101"  # qwen3-embedding-8b, /v1/embeddings

#: Discoverable registry of compiler-probe configs by short name.
REGISTRY: dict[str, ModelConfig] = {
    cfg.short(): cfg for cfg in (ORNITH, VIBETHINKER, QWYTHOS)
}
