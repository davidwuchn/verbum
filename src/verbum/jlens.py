"""J-space probe — broadcast sensitivity + verbalizability of residual directions.

A tractable, honestly-scoped analogue of Anthropic's Jacobian Lens
("Verbalizable Representations Form a Global Workspace in Language Models",
2026-07-06). We do **not** reimplement their exact Jacobian-to-penultimate
construction; we read the two properties that make J-space interesting through
cheaper first-order primitives, and name the register before probing
(AGENTS.md ``λ measure``: name(register) before build(probe)):

  - **broadcast** — how much *injecting* a unit residual direction at a layer
    moves the output distribution (KL). This is the first-order term of the
    Jacobian along that direction: ``KL(clean ‖ clean+ε·d) ≈ ½ ε² dᵀ Jᵀ J d``.
    High broadcast ⇒ the direction is causally read out to the logits — the
    "workspace/reportable" property, in the value/magnitude register.
  - **verbalizability** — the logit-lens readout of a residual direction:
    ``unembed(d ⊙ norm.weight)`` → the tokens it points toward. The J-space
    "single-token concept" surface.

Built on :mod:`verbum.hooks` (the intervention engine) — it registers no raw
hooks of its own for injection, and it is model-agnostic (GPT-2 / Pythia /
Qwen) via the same layer-discovery logic as :mod:`verbum.instrument`.

License: MIT.
"""

from __future__ import annotations

from typing import Any

import torch
import torch.nn.functional as F
from torch import nn

from . import hooks

__all__ = [
    "broadcast_kl",
    "capture_residuals",
    "kl_rows",
    "layer_path",
    "logit_lens",
    "n_layers",
    "self_test",
    "verbalize",
]


# ── architecture discovery (mirrors instrument._get_layers, adds paths) ──────


def _layers_and_prefix(model: nn.Module) -> tuple[Any, str]:
    """Return ``(layer_module_list, dotted_prefix)`` for the transformer stack."""
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers, "gpt_neox.layers"  # Pythia / GPT-NeoX
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers, "model.layers"  # Qwen2/LLaMA/Mistral/Phi3
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h, "transformer.h"  # GPT-2 / GPT-J
    msg = f"Cannot find transformer layers in {type(model).__name__}."
    raise AttributeError(msg)


def _final_norm_unembed(model: nn.Module) -> tuple[nn.Module, nn.Module]:
    """Return ``(final_norm, unembed_linear)`` for the logit-lens readout."""
    if hasattr(model, "gpt_neox"):
        return model.gpt_neox.final_layer_norm, model.embed_out
    if hasattr(model, "model") and hasattr(model.model, "norm"):
        return model.model.norm, model.lm_head
    if hasattr(model, "transformer") and hasattr(model.transformer, "ln_f"):
        return model.transformer.ln_f, model.lm_head
    msg = f"Cannot find final norm / unembed in {type(model).__name__}."
    raise AttributeError(msg)


def layer_path(model: nn.Module, i: int) -> str:
    """Dotted submodule path for transformer layer ``i`` (for hooks.intervene)."""
    _, prefix = _layers_and_prefix(model)
    return f"{prefix}.{i}"


def n_layers(model: nn.Module) -> int:
    layers, _ = _layers_and_prefix(model)
    return len(layers)


def _hidden(out: Any) -> torch.Tensor:
    """Extract the hidden-state tensor from a layer's (possibly tuple) output."""
    return out[0] if isinstance(out, tuple) else out


# ── residual capture (all layers, all positions) ─────────────────────────────


@torch.no_grad()
def capture_residuals(
    model: nn.Module,
    tokenizer: Any,
    text: str | None = None,
    *,
    input_ids: torch.Tensor | None = None,
) -> tuple[dict[int, torch.Tensor], torch.Tensor]:
    """Forward once; return ``({layer: (seq, d)}, input_ids)``.

    Provide ``text`` (tokenized here) or pre-tokenized ``input_ids`` (shape
    ``(seq,)`` or ``(1, seq)``) — the latter for synthetic streams (e.g.
    induction sequences of raw token ids). Residual = the *output* of each
    transformer layer (post-block), for every position. Reuses
    :func:`verbum.hooks.capture`.
    """
    if input_ids is not None:
        ids = input_ids if input_ids.dim() == 2 else input_ids.unsqueeze(0)
        inputs = {"input_ids": ids.to(model.device)}
    elif text is not None:
        inputs = tokenizer(text, return_tensors="pt").to(model.device)
    else:
        raise ValueError("capture_residuals needs `text` or `input_ids`")
    nl = n_layers(model)
    ivs = [hooks.capture(layer_path(model, i), name=str(i)) for i in range(nl)]
    with hooks.intervene(model, ivs) as sess:
        model(**inputs)
    out: dict[int, torch.Tensor] = {}
    for i in range(nl):
        out[i] = _hidden(sess.captured[str(i)])[0].float()  # (seq, d), on CPU
    return out, inputs["input_ids"][0].detach().cpu()


# ── logit-lens readouts ──────────────────────────────────────────────────────


@torch.no_grad()
def logit_lens(model: nn.Module, resid: torch.Tensor) -> torch.Tensor:
    """Map residual STATE(s) ``(..., d)`` to logits ``(..., vocab)`` (full norm)."""
    norm, unembed = _final_norm_unembed(model)
    dtype = next(model.parameters()).dtype
    dev = next(model.parameters()).device
    return unembed(norm(resid.to(dtype).to(dev)))


@torch.no_grad()
def verbalize(
    model: nn.Module, tokenizer: Any, direction: torch.Tensor, *, top_k: int = 8
) -> list[str]:
    """Top-``k`` tokens a residual DIRECTION points toward (logit-lens readout).

    Uses ``unembed_weight @ (direction ⊙ norm.weight)`` — the standard
    direction readout (LayerNorm/RMSNorm affine gain only, no re-centering).
    """
    norm, unembed = _final_norm_unembed(model)
    dev = unembed.weight.device
    d = direction.to(unembed.weight.dtype).to(dev)
    gain = getattr(norm, "weight", None)
    if gain is not None:
        d = d * gain.to(d.dtype)
    col = unembed.weight @ d  # (vocab,)
    idx = torch.topk(col, top_k).indices.tolist()
    return [tokenizer.decode([i]) for i in idx]


# ── behavioral broadcast (substitution-KL, first-order Jacobian proxy) ───────


def kl_rows(clean: torch.Tensor, pert: torch.Tensor) -> torch.Tensor:
    """Per-position ``KL(clean ‖ pert)`` for logit tensors ``(seq, vocab)``."""
    logp = F.log_softmax(clean, dim=-1)
    p = logp.exp()
    logq = F.log_softmax(pert, dim=-1)
    return (p * (logp - logq)).sum(-1)


@torch.no_grad()
def forward_logits(
    model: nn.Module,
    tokenizer: Any,
    text: str,
    *,
    layer: int | None = None,
    delta_vec: torch.Tensor | None = None,
    positions: list[int] | None = None,
) -> torch.Tensor:
    """Logits ``(seq, vocab)`` for ``text``, optionally injecting ``delta_vec``.

    If ``layer``/``delta_vec`` are given, ``delta_vec`` (shape ``(d,)``) is
    added to that layer's output at ``positions`` (default: all). Injection
    goes through :func:`verbum.hooks.apply_post`.
    """
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    if layer is None or delta_vec is None:
        return model(**inputs).logits[0].float()

    dv = delta_vec.to(model.device).to(next(model.parameters()).dtype)

    def add(_m: nn.Module, _i: Any, out: Any) -> Any:
        h = _hidden(out)
        h2 = h.clone()
        if positions is None:
            h2[0, :, :] = h2[0, :, :] + dv
        else:
            for p in positions:
                h2[0, p, :] = h2[0, p, :] + dv
        return (h2, *out[1:]) if isinstance(out, tuple) else h2

    iv = hooks.apply_post(layer_path(model, layer), add)
    with hooks.intervene(model, [iv]):
        return model(**inputs).logits[0].float()


@torch.no_grad()
def broadcast_kl(
    model: nn.Module,
    tokenizer: Any,
    text: str,
    layer: int,
    delta_vec: torch.Tensor,
    *,
    positions: list[int] | None = None,
    clean: torch.Tensor | None = None,
) -> float:
    """Mean ``KL(clean ‖ clean+injected)`` — the broadcast of ``delta_vec``.

    ``clean`` may be precomputed (same ``text``) to avoid recomputation across
    many injected directions.
    """
    if clean is None:
        clean = forward_logits(model, tokenizer, text)
    pert = forward_logits(
        model, tokenizer, text, layer=layer, delta_vec=delta_vec, positions=positions
    )
    kl = kl_rows(clean, pert)
    scored = kl if positions is None else kl[positions]
    return float(scored.mean())


# ── self-test (CPU, tiny model) ──────────────────────────────────────────────


def self_test(model_name: str = "EleutherAI/pythia-14m-deduped") -> dict[str, Any]:
    """Sanity gate: identity injection is exact-zero; nonzero injection moves KL.

    Mirrors the Babel identity-inject gate — the instrument must not perturb
    when the delta is zero. Returns a small report dict.
    """
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float32, attn_implementation="eager"
    ).eval()

    text = "The cat, not the dog, chased the mouse."
    nl = n_layers(model)
    d = model.config.hidden_size
    L = nl // 2

    clean = forward_logits(model, tok, text)
    zero_kl = broadcast_kl(model, tok, text, L, torch.zeros(d), clean=clean)

    resids, _ = capture_residuals(model, tok, text)
    typical = resids[L].norm(dim=-1).mean().item()
    g = torch.Generator().manual_seed(0)
    rand = torch.randn(d, generator=g)
    rand = rand / rand.norm() * (0.5 * typical)
    rand_kl = broadcast_kl(model, tok, text, L, rand, clean=clean)

    words = verbalize(model, tok, resids[L][-1])  # last-token state readout

    return {
        "model": model_name,
        "n_layers": nl,
        "d": d,
        "identity_kl": zero_kl,
        "identity_ok": zero_kl <= 1e-9,
        "random_inject_kl": rand_kl,
        "random_moves": rand_kl > 1e-4,
        "typical_resid_norm": round(typical, 3),
        "last_token_verbalize": words,
    }


if __name__ == "__main__":
    import json

    print(json.dumps(self_test(), indent=2))
