"""Tests for the generic forward-hook intervention engine (verbum.hooks).

Runs on a real small model (Qwen3-0.6B, dense) so the engine is verified
against actual PyTorch hook semantics, not a mock. Skipped if the model is
not in the local HF cache.

License: MIT.
"""

from __future__ import annotations

import pytest
import torch

from verbum import hooks

MODEL = "Qwen/Qwen3-0.6B"


@pytest.fixture(scope="module")
def model_and_tok():
    pytest.importorskip("transformers")
    from huggingface_hub import try_to_load_from_cache

    if try_to_load_from_cache(MODEL, "config.json") is None:
        pytest.skip(f"{MODEL} not in HF cache")
    from verbum.instrument import load_model

    model, tok, _info = load_model(MODEL, device="cpu", dtype=torch.float32)
    return model, tok


def _logits(model, tok, text="The cat sat on the"):
    ids = tok(text, return_tensors="pt").to(model.device)
    with torch.no_grad():
        return model(**ids).logits[0, -1]


def test_capture_records_output(model_and_tok):
    model, tok = model_and_tok
    target = "model.layers.0.mlp"
    with hooks.intervene(model, [hooks.capture(target)]) as s:
        _logits(model, tok)
    assert target in s.captured
    out = s.captured[target]
    # MLP output is a single hidden-state tensor.
    assert isinstance(out, torch.Tensor)
    assert out.shape[-1] == model.config.hidden_size


def test_zero_output_changes_logits(model_and_tok):
    model, tok = model_and_tok
    base = _logits(model, tok)
    with hooks.intervene(model, [hooks.zero_output("model.layers.0.mlp")]):
        ablated = _logits(model, tok)
    # Zeroing an MLP's contribution must move the next-token logits.
    assert not torch.allclose(base, ablated, atol=1e-4)


def test_hooks_removed_after_context(model_and_tok):
    model, tok = model_and_tok
    base = _logits(model, tok)
    with hooks.intervene(model, [hooks.zero_output("model.layers.0.mlp")]):
        pass
    # Outside the block the model must be byte-for-byte its original self.
    after = _logits(model, tok)
    assert torch.allclose(base, after, atol=1e-6)


def test_apply_post_transform(model_and_tok):
    model, tok = model_and_tok
    base = _logits(model, tok)

    def scale_half(_m, _i, out):
        return out * 0.5

    with hooks.intervene(model, [hooks.apply_post("model.layers.0.mlp", scale_half)]):
        scaled = _logits(model, tok)
    assert not torch.allclose(base, scaled, atol=1e-4)


def test_attr_patch_set_and_restore(model_and_tok):
    model, tok = model_and_tok
    mlp_path = "model.layers.0.mlp"
    original = model.get_submodule(mlp_path).act_fn
    base = _logits(model, tok)
    # Swap the activation to identity → output must change inside the block.
    swap = hooks.set_attr(mlp_path, "act_fn", torch.nn.Identity())
    with hooks.intervene(model, [swap]):
        assert isinstance(model.get_submodule(mlp_path).act_fn, torch.nn.Identity)
        changed = _logits(model, tok)
    assert not torch.allclose(base, changed, atol=1e-4)
    # Restored on exit (same object, same logits).
    assert model.get_submodule(mlp_path).act_fn is original
    assert torch.allclose(base, _logits(model, tok), atol=1e-6)
