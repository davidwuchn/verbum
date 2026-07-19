#!/usr/bin/env python3
"""Auto-detect a model's topology so the opcode tracer can find the gate register.

The opcode/crystal pipeline (fingerprint -> calibrate -> classify -> trace) is
already model-agnostic at the numpy layer: it consumes per-layer *gate feature
matrices* and never learns any architecture. The one thing that was hard-coded
in the legacy monitor was the CAPTURE plumbing --
``model.model.layers[i].mlp.gate_proj`` -- which only matches dense Llama-family
models. This module removes that assumption.

``detect_topology(model)`` walks the module tree and returns a
:class:`ModelTopology` describing:

  - **layers_path**  the dotted path to the transformer ``ModuleList``
                     (``model.layers`` | ``model.language_model.layers`` |
                     ``gpt_neox.layers`` | ``transformer.h`` | ...).
  - **register**     the MLP routing register, one of:
                       * ``"gated-dense"`` -- SwiGLU/GeGLU with a per-layer
                         ``gate_proj`` (the register where the combinator crystal
                         lives). TRACEABLE.
                       * ``"moe"`` -- a sparse block (router + experts). A
                         DIFFERENT register (router logits vs active-expert
                         gates); named, NOT silently reused. Not yet traceable
                         with the dense reader -- a measurement-register decision.
                       * ``"ungated"`` -- a single up-projection + activation
                         (GPT-NeoX / GPT-2). No sign(gate) crystal register
                         exists; the detector REFUSES the read rather than faking
                         one.
  - **gate_suffix**  per-layer dotted suffix to the gate module
                     (e.g. ``"mlp.gate_proj"``); compose with a layer index via
                     :func:`gate_path`.
  - **router_suffix / expert_gate_suffix / n_experts**  MoE only.
  - **final_norm_path / unembed_path**  for the logit-lens / verbalize readout.

Design goals (AGENTS.md): ``lambda one_way`` (one canonical module discovery),
``lambda extend`` (candidate paths are an open slot -- add, don't branch),
``lambda measure`` (name the register before probing; MoE and un-gated are
distinct registers, flagged not conflated). Works on **meta-device** models
(``torch.device("meta")``) so detection is cheap to verify without loading any
weights.

License: MIT.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from torch import nn

__all__ = [
    "ModelTopology",
    "detect_topology",
    "expert_gate_path",
    "final_norm_path",
    "gate_path",
    "router_path",
    "self_test",
]


# ── candidate paths (open slots; extend, don't branch) ───────────────────────

# Dotted paths (relative to the top-level model) that commonly hold the decoder
# ``ModuleList``. Ordered most-specific-first so nested wrappers win.
_LAYER_PATHS: tuple[str, ...] = (
    "model.language_model.layers",   # Gemma-3/4, multimodal *ForConditionalGeneration
    "language_model.model.layers",   # some VLM wrappers
    "model.layers",                  # Qwen2/3, Llama, Mistral, OLMo-2, Phi3
    "model.model.layers",            # doubly-wrapped
    "gpt_neox.layers",               # Pythia / GPT-NeoX
    "model.gpt_neox.layers",
    "transformer.h",                 # GPT-2 / GPT-J
    "model.transformer.h",
    "model.decoder.layers",          # OPT / BART-style
    "layers",                        # bare
)

# Per-layer attribute names that hold the feed-forward / MLP submodule.
_FFN_ATTRS: tuple[str, ...] = ("mlp", "feed_forward", "ffn", "block_sparse_moe")

# Un-gated up-projection module names (the routing register for models without a
# SwiGLU/GeGLU gate). ``dense_h_to_4h`` = GPT-NeoX/Pythia (the module the
# cross-model consensus captured for Pythia); ``c_fc`` = GPT-2; the rest cover
# GPT-J/OPT-style stacks. Ordered by specificity.
_UPPROJ_ATTRS: tuple[str, ...] = (
    "dense_h_to_4h", "c_fc", "fc_in", "fc1", "w1", "up_proj",
)

# Final-norm dotted paths, aligned with the layer wrappers above.
_NORM_PATHS: tuple[str, ...] = (
    "model.language_model.norm",
    "model.norm",
    "model.model.norm",
    "gpt_neox.final_layer_norm",
    "model.gpt_neox.final_layer_norm",
    "transformer.ln_f",
    "model.transformer.ln_f",
    "model.decoder.final_layer_norm",
    "norm",
)

# Unembed (LM head) dotted paths.
_UNEMBED_PATHS: tuple[str, ...] = ("lm_head", "embed_out", "model.embed_out")


# ── the descriptor ───────────────────────────────────────────────────────────


@dataclass(frozen=True)
class ModelTopology:
    """A model's decoder layout, enough to capture the gate routing register."""

    arch: str                         # config.architectures[0] (or class name)
    n_layers: int
    hidden_size: int | None
    layers_path: str                  # dotted path to the decoder ModuleList
    register: str                     # gated-dense | gated-fused | ungated | moe
    gate_suffix: str | None           # per-layer suffix, e.g. "mlp.gate_proj"
    gate_width: int | None            # feature width d of the gate output
    read_register: str = ""           # the routing read, named (lambda measure)
    # MoE only:
    router_suffix: str | None = None
    expert_gate_suffix: str | None = None   # "{ffn}.experts.{{i}}.gate_proj"
    n_experts: int | None = None
    # readout:
    final_norm_path: str | None = None
    unembed_path: str | None = None
    ffn_attr: str = "mlp"
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def traceable(self) -> bool:
        """Is a routing register available to capture (dense gate OR up-proj proxy)?

        True for gated MLPs (sign(gate_proj), the validated register) AND un-gated
        MLPs (sign(up-projection), the proxy register the cross-model consensus
        actually used for GPT-NeoX/Pythia). False for MoE (a distinct, undecided
        register) and for models where no FFN projection was found.
        """
        return self.gate_suffix is not None and self.register != "moe"

    @property
    def validated_register(self) -> bool:
        """True only for the sign(gate_proj) register (s203/s231 validated)."""
        return self.register == "gated-dense"

    def summary(self) -> str:
        parts = [
            f"arch={self.arch}",
            f"L={self.n_layers}",
            f"register={self.register}",
            f"layers={self.layers_path}",
        ]
        if self.gate_suffix:
            parts.append(f"gate={self.gate_suffix}(d={self.gate_width})")
        if self.read_register:
            parts.append(f"read={self.read_register}")
        if self.register == "moe":
            parts.append(f"experts={self.n_experts} router={self.router_suffix}")
        return "  ".join(parts)


# ── resolution helpers ───────────────────────────────────────────────────────


def _resolve(root: nn.Module, dotted: str) -> Any | None:
    """Follow a dotted attribute/index path from ``root``; None if any hop fails."""
    obj: Any = root
    for part in dotted.split("."):
        if part.isdigit():
            try:
                obj = obj[int(part)]
            except (IndexError, KeyError, TypeError):
                return None
        else:
            obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def _looks_like_decoder_layers(mod: Any) -> bool:
    """A ModuleList whose first element looks like a transformer block."""
    if not isinstance(mod, nn.ModuleList) or len(mod) == 0:
        return False
    block = mod[0]
    children = {n for n, _ in block.named_children()}
    has_attn = bool(children & {"self_attn", "attention", "attn", "self_attention"})
    has_ffn = bool(children & set(_FFN_ATTRS))
    return has_attn or has_ffn


def _find_layers(model: nn.Module) -> tuple[Any, str] | None:
    """Return ``(module_list, dotted_path)`` for the decoder stack, or None.

    Tries the known candidate paths first (fast, canonical), then falls back to a
    tree search for the largest decoder-like ``ModuleList`` (robust to unseen
    wrappers -- lambda extend: the search is the open default).
    """
    for path in _LAYER_PATHS:
        mod = _resolve(model, path)
        if _looks_like_decoder_layers(mod):
            return mod, path
    # fallback: search the whole tree, pick the deepest/largest decoder ModuleList
    best: tuple[int, Any, str] | None = None
    for name, mod in model.named_modules():
        if _looks_like_decoder_layers(mod):
            score = len(mod)
            if best is None or score > best[0]:
                best = (score, mod, name)
    if best is not None:
        return best[1], best[2]
    return None


def _find_ffn(layer: nn.Module) -> tuple[Any, str] | None:
    """Return ``(ffn_module, attr_name)`` for a decoder layer's MLP/MoE block."""
    for attr in _FFN_ATTRS:
        ffn = getattr(layer, attr, None)
        if ffn is not None:
            return ffn, attr
    return None


def _classify_ffn(ffn: nn.Module) -> str:
    """Classify the MLP register: 'moe' | 'gated-dense' | 'gated-fused' | 'ungated'."""
    children = {n for n, _ in ffn.named_children()}
    # MoE: a container of experts (+ usually a router named 'gate'/'router')
    if "experts" in children or any("expert" in c for c in children):
        return "moe"
    # gated dense: SwiGLU/GeGLU expose a gate_proj alongside up/down
    if "gate_proj" in children or hasattr(ffn, "gate_proj"):
        return "gated-dense"
    # gated FUSED: Phi-3 style — one projection carries gate‖up interleaved
    if "gate_up_proj" in children or hasattr(ffn, "gate_up_proj"):
        return "gated-fused"
    # everything else (GPT-NeoX dense_h_to_4h, GPT-2 c_fc, plain MLP) is un-gated —
    # the routing read falls back to the up-projection register (see _UPPROJ_ATTRS)
    return "ungated"


def _find_upproj(ffn: nn.Module) -> tuple[str, Any] | None:
    """Return ``(attr_name, module)`` for an un-gated up-projection, or None."""
    for attr in _UPPROJ_ATTRS:
        mod = getattr(ffn, attr, None)
        if mod is not None:
            return attr, mod
    return None


def _out_features(mod: Any) -> int | None:
    for attr in ("out_features", "nf", "embed_dim"):
        v = getattr(mod, attr, None)
        if isinstance(v, int):
            return v
    w = getattr(mod, "weight", None)
    if w is not None and hasattr(w, "shape") and len(w.shape) >= 1:
        return int(w.shape[0])
    return None


def _cfg_int(config: Any, *keys: str) -> int | None:
    """Read an int from config, descending into ``text_config`` for composites."""
    for src in (config, getattr(config, "text_config", None)):
        if src is None:
            continue
        for k in keys:
            v = getattr(src, k, None)
            if isinstance(v, int):
                return v
    return None


def _first_present(model: nn.Module, paths: tuple[str, ...]) -> str | None:
    for p in paths:
        if _resolve(model, p) is not None:
            return p
    return None


# ── the detector ─────────────────────────────────────────────────────────────


def detect_topology(model: nn.Module, config: Any | None = None) -> ModelTopology:
    """Auto-detect ``model``'s decoder topology + gate routing register.

    Pure structural walk -- works on a fully loaded model or a ``meta``-device
    one (no weights). ``config`` defaults to ``model.config``.
    """
    config = config if config is not None else getattr(model, "config", None)
    arch = "?"
    if config is not None:
        archs = getattr(config, "architectures", None)
        arch = (archs[0] if archs else type(model).__name__)
    notes: list[str] = []

    found = _find_layers(model)
    if found is None:
        raise AttributeError(
            f"Cannot locate a decoder ModuleList in {type(model).__name__}; "
            "add its path to _LAYER_PATHS."
        )
    layers, layers_path = found
    n_layers = len(layers)
    hidden = _cfg_int(config, "hidden_size", "n_embd", "d_model") if config else None

    ffn_found = _find_ffn(layers[0])
    if ffn_found is None:
        return ModelTopology(
            arch=arch, n_layers=n_layers, hidden_size=hidden,
            layers_path=layers_path, register="ungated", gate_suffix=None,
            gate_width=None,
            final_norm_path=_first_present(model, _NORM_PATHS),
            unembed_path=_first_present(model, _UNEMBED_PATHS),
            notes=("no FFN submodule found on layer 0",),
        )
    ffn, ffn_attr = ffn_found
    register = _classify_ffn(ffn)

    gate_suffix = gate_width = None
    read_register = ""
    router_suffix = expert_gate_suffix = n_experts = None

    if register == "gated-dense":
        gate_suffix = f"{ffn_attr}.gate_proj"
        gate_width = _out_features(ffn.gate_proj) or _cfg_int(
            config, "intermediate_size"
        )
        read_register = "sign(gate_proj) [validated]"
    elif register == "gated-fused":
        gate_suffix = f"{ffn_attr}.gate_up_proj"
        full = _out_features(ffn.gate_up_proj)
        gate_width = (full // 2) if full else _cfg_int(config, "intermediate_size")
        read_register = "sign(gate_up_proj[:d]) [fused gate‖up; split before read]"
        notes.append(
            "fused gate+up projection: the gate half is gate_up_proj[..., :d]; "
            "capture must split it before the sign(gate) read."
        )
    elif register == "ungated":
        up = _find_upproj(ffn)
        if up is not None:
            up_attr, up_mod = up
            gate_suffix = f"{ffn_attr}.{up_attr}"
            gate_width = _out_features(up_mod) or _cfg_int(
                config, "intermediate_size", "n_inner"
            )
            read_register = f"sign({up_attr}) [up-proj proxy]"
            notes.append(
                "un-gated MLP: no sign(gate_proj) register. Falls back to the "
                f"up-projection register sign({up_attr}) — the same proxy the "
                "cross-model crystal consensus used for GPT-NeoX/Pythia. It is a "
                "proxy for the validated gate register, not identical to it."
            )
        else:
            read_register = "none"
            notes.append(
                "un-gated MLP and no recognized up-projection module: no routing "
                "register found; the opcode crystal read is unavailable."
            )
    elif register == "moe":
        # router: commonly 'gate' (Qwen/Mixtral) or 'router'
        router_name = next(
            (c for c in ("gate", "router") if hasattr(ffn, c)), None
        )
        router_suffix = f"{ffn_attr}.{router_name}" if router_name else None
        experts = getattr(ffn, "experts", None)
        # experts may be an indexable ModuleList (older transformers) OR a FUSED
        # module with batched weights (e.g. Qwen3MoeExperts, no __len__). Handle
        # both; fall back to config for the count.
        if experts is not None:
            try:
                n_local = len(experts)  # type: ignore[arg-type]
            except TypeError:
                n_local = None
            if n_local:
                n_experts = n_local
                expert0 = experts[0]
                if hasattr(expert0, "gate_proj"):
                    expert_gate_suffix = f"{ffn_attr}.experts.{{i}}.gate_proj"
                    gate_width = _out_features(expert0.gate_proj)
            else:
                notes.append(
                    f"fused experts ({type(experts).__name__}): per-expert gate is "
                    "a batched weight, not an indexable submodule."
                )
        n_experts = n_experts or _cfg_int(config, "num_experts", "num_local_experts")
        gate_width = gate_width or _cfg_int(config, "moe_intermediate_size")
        read_register = "moe (undecided: router-logits vs active-expert gates)"
        notes.append(
            "MoE register: router-logits vs active-expert gates is an open "
            "measurement-register decision (not the dense sign(gate) read)."
        )

    return ModelTopology(
        arch=arch, n_layers=n_layers, hidden_size=hidden,
        layers_path=layers_path, register=register, gate_suffix=gate_suffix,
        gate_width=gate_width, read_register=read_register,
        router_suffix=router_suffix,
        expert_gate_suffix=expert_gate_suffix, n_experts=n_experts,
        final_norm_path=_first_present(model, _NORM_PATHS),
        unembed_path=_first_present(model, _UNEMBED_PATHS),
        ffn_attr=ffn_attr, notes=tuple(notes),
    )


# ── path composers (feed hooks.py: model.get_submodule(path)) ────────────────


def gate_path(topo: ModelTopology, layer: int) -> str:
    """Dotted path to layer ``layer``'s gate/up-proj routing module.

    Works for any traceable topology: the validated ``sign(gate_proj)`` register
    (gated-dense/-fused) and the ``sign(up-proj)`` proxy register (un-gated,
    e.g. GPT-NeoX). Raises for MoE (undecided register) or when no projection
    was found.
    """
    if not topo.traceable or topo.gate_suffix is None:
        raise ValueError(
            f"gate_path undefined for register={topo.register!r} "
            f"(arch={topo.arch}); no routing register available "
            f"(read_register={topo.read_register!r})."
        )
    return f"{topo.layers_path}.{layer}.{topo.gate_suffix}"


def router_path(topo: ModelTopology, layer: int) -> str:
    """Dotted path to layer ``layer``'s MoE router (moe only)."""
    if topo.register != "moe" or topo.router_suffix is None:
        raise ValueError(f"router_path undefined for register={topo.register!r}")
    return f"{topo.layers_path}.{layer}.{topo.router_suffix}"


def expert_gate_path(topo: ModelTopology, layer: int, expert: int) -> str:
    """Dotted path to layer ``layer`` expert ``expert``'s gate (moe only)."""
    if topo.register != "moe" or topo.expert_gate_suffix is None:
        raise ValueError(f"expert_gate_path undefined for register={topo.register!r}")
    return f"{topo.layers_path}.{layer}.{topo.expert_gate_suffix.format(i=expert)}"


def final_norm_path(topo: ModelTopology) -> str | None:
    return topo.final_norm_path


# ── meta-device self-test (no weights loaded) ────────────────────────────────

# (model_name, expected_register). None => build expected to fail (composite
# config the installed transformers can't `from_config`) -> reported as IOU.
# NOTE: Qwen3.6-27B (composite/hybrid config) fails meta `from_config` but loads
# fine via `from_pretrained`; verified separately as register=gated-dense,
# layers=model.layers, gate=mlp.gate_proj(d=17408). See `probe_real()`.
_SELF_TEST_MODELS: tuple[tuple[str, str | None], ...] = (
    ("Qwen/Qwen3-32B", "gated-dense"),
    ("allenai/OLMo-2-1124-13B", "gated-dense"),
    ("google/gemma-4-31B-it", "gated-dense"),
    ("Qwen/Qwen3-30B-A3B", "moe"),
    ("EleutherAI/gpt-neox-20b", "ungated"),      # traceable via up-proj proxy
    ("Qwen/Qwen3.6-27B", None),   # composite config: meta build IOU (loads real)
)


def self_test(models: tuple[tuple[str, str | None], ...] = _SELF_TEST_MODELS) -> dict:
    """Build each model on the meta device and verify register detection.

    Runtime-proven, not asserted from memory: we walk the actual module tree.
    Composite-config models the installed transformers cannot ``from_config``
    are recorded as IOUs (need a real ``from_pretrained`` load), not failures.
    """
    import torch
    from transformers import AutoConfig, AutoModelForCausalLM

    rows: list[dict] = []
    ok = True
    for name, expected in models:
        row: dict[str, Any] = {"model": name, "expected": expected}
        try:
            cfg = AutoConfig.from_pretrained(name)
            with torch.device("meta"):
                model = AutoModelForCausalLM.from_config(cfg)
        except Exception as e:
            row["status"] = "IOU" if expected is None else "BUILD_FAIL"
            row["detail"] = f"{type(e).__name__}: {str(e)[:80]}"
            row["pass"] = expected is None
            ok = ok and row["pass"]
            rows.append(row)
            continue
        try:
            topo = detect_topology(model, cfg)
            row["detected"] = topo.register
            row["summary"] = topo.summary()
            row["notes"] = list(topo.notes)
            row["pass"] = (expected is None) or (topo.register == expected)
        except Exception as e:
            row["status"] = "DETECT_FAIL"
            row["detail"] = f"{type(e).__name__}: {str(e)[:80]}"
            row["pass"] = False
        ok = ok and bool(row.get("pass"))
        rows.append(row)
    return {"all_pass": ok, "rows": rows}


def probe_real(name: str, dtype: str = "bfloat16") -> ModelTopology:
    """Load a model for real (``from_pretrained``) and detect — the ground-truth
    path for composite/hybrid configs that fail meta ``from_config``.

    Heavier (loads weights), but definitive. Used for models like Qwen3.6-27B.
    """
    import torch
    from transformers import AutoModelForCausalLM

    model = AutoModelForCausalLM.from_pretrained(
        name, dtype=getattr(torch, dtype), low_cpu_mem_usage=True
    )
    return detect_topology(model, model.config)


def _print_report(report: dict) -> None:
    print("=" * 78)
    print("opcodes.topology — meta-device detection self-test")
    print("=" * 78)
    for r in report["rows"]:
        mark = "✅" if r.get("pass") else "❌"
        exp = r["expected"] if r["expected"] is not None else "(build IOU)"
        det = r.get("detected") or r.get("status") or "?"
        print(f"{mark} {r['model']:32s} expect={exp!s:12s} -> {det}")
        if "summary" in r:
            print(f"     {r['summary']}")
        if r.get("notes"):
            for n in r["notes"]:
                print(f"     · {n}")
        if "detail" in r:
            print(f"     ! {r['detail']}")
    print("=" * 78)
    print(f"all_pass={report['all_pass']}")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "--real":
        # real-load detection for one model (e.g. composite/hybrid configs)
        name = sys.argv[2] if len(sys.argv) > 2 else "Qwen/Qwen3.6-27B"
        print(f"real-load detect: {name}")
        topo = probe_real(name)
        print("  " + topo.summary())
        print(f"  traceable={topo.traceable}  validated={topo.validated_register}")
        for n in topo.notes:
            print(f"  · {n}")
    else:
        _print_report(self_test())
