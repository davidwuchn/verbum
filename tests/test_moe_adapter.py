"""MoEAdapter path-resolution tests via meta-device instantiation.

Instantiates the real Qwen3 MoE configs on the meta device (zero weight load)
so the adapter's structural block-finding and config reads are verified against
the actual model classes without needing 60-70GB resident. Skipped if a config
is not in the local HF cache.

License: MIT.
"""

from __future__ import annotations

import pytest

from verbum.adapters import MoEAdapter


def _meta_model(repo: str):
    pytest.importorskip("accelerate")
    from huggingface_hub import try_to_load_from_cache

    if try_to_load_from_cache(repo, "config.json") is None:
        pytest.skip(f"{repo} not in HF cache")
    from accelerate import init_empty_weights
    from transformers import AutoConfig, AutoModel, AutoModelForCausalLM

    cfg = AutoConfig.from_pretrained(repo)
    with init_empty_weights():
        try:
            return AutoModelForCausalLM.from_config(cfg)
        except Exception:
            return AutoModel.from_config(cfg)


def test_qwen35_35b_a3b_paths():
    model = _meta_model("Qwen/Qwen3.6-35B-A3B")
    a = MoEAdapter(model)
    assert len(a.blocks) == 40
    assert a.num_experts == 256
    assert a.top_k == 8
    assert a.has_shared is True
    # layer indices are 0..39, contiguous and sorted.
    assert a.layers == list(range(40))
    # every located block resolves gate + experts + shared_expert submodules.
    for layer in (0, 17, 39):
        model.get_submodule(a.gate_path(layer))
        model.get_submodule(a.shared_path(layer))
        model.get_submodule(f"{a.block_path(layer)}.experts")


def test_qwen3_30b_a3b_paths():
    model = _meta_model("Qwen/Qwen3-30B-A3B")
    a = MoEAdapter(model)
    assert len(a.blocks) == 48
    assert a.num_experts == 128
    assert a.top_k == 8
    assert a.has_shared is False
    assert a.layers == list(range(48))
    model.get_submodule(a.gate_path(0))
    model.get_submodule(f"{a.block_path(0)}.experts")


def test_intervention_builders_target_real_modules():
    """Builders must produce Interventions whose targets resolve on the model."""
    model = _meta_model("Qwen/Qwen3.6-35B-A3B")
    a = MoEAdapter(model)
    ivs = [
        *a.route_capture([0, 1]),
        a.ablate_experts(0, [3, 7, 42]),
        a.force_k(0, 4),
        a.ablate_shared(0),
    ]
    for iv in ivs:
        # target must be a resolvable submodule path.
        model.get_submodule(iv.target)
    # force_k is an attr patch on the router with the right attribute.
    fk = a.force_k(5, 2)
    assert fk.when == "attr"
    assert fk.attr == "top_k"
    assert fk.value == 2
