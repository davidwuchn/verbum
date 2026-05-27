"""ISA Decoder — Decompile Qwen3.6-27B FFN computation to instruction sets.

Session 161. The FFNs contain piles of beta reductions. Attention runs
inference patterns programmed by FFN projections. This script decodes
those patterns into a readable instruction set architecture (ISA).

The model IS a computer. Each layer IS an instruction. The FFN overlay
matrix (combinator-space input → combinator-space output) IS the opcode.
The residual stream IS the register file. Attention IS the memory bus.

Architecture (Qwen3.6-27B):
  64 layers, d=5120, d_ff=17408
  Pattern: [L,L,L,F]×16 (48 linear attention + 16 full attention)
  SwiGLU FFN: gate_proj(d→d_ff) * up_proj(d→d_ff) → down_proj(d_ff→d)
  24 attention heads, 4 KV heads, d_head=256

The ISA:
  OPCODES derived from KIBC-DYWH combinator basis:
    SELECT(K)   — discard one operand, keep the other
    PASS(I)     — identity, forward unchanged
    COMPOSE(B)  — chain two functions: f(g(x))
    FLIP(C)     — reorder arguments: f(y)(x) instead of f(x)(y)
    DCOMPOSE(D) — deep compose: f(g(h(x)))
    RECURSE(Y)  — fixed-point / loop
    DUPLICATE(W)— self-apply: f(x)(x)
    HALT(WHNF)  — weak head normal form, stop reducing

  OPERANDS tracked via residual stream projection into combinator space.
  CONTROL FLOW detected via WHNF/Y activation patterns.
  BASIC BLOCKS formed at phase transitions (composition→selection etc).

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/isa_decoder.py 2>&1 | tee results/isa-decode/run.log

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoTokenizer, AutoConfig

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode"
MODEL_NAME = "Qwen/Qwen3.6-27B"
DEVICE = "mps"

# Architecture constants
N_LAYERS = 64
D_MODEL = 5120
D_FF = 17408
FULL_ATTN_LAYERS = list(range(3, 64, 4))  # [3, 7, 11, ..., 63]
LINEAR_ATTN_LAYERS = [i for i in range(64) if i not in FULL_ATTN_LAYERS]

# KIBC-DYWH combinator names and their ISA opcode equivalents
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
OPCODE_NAMES = {
    "K": "SELECT",
    "I": "PASS",
    "B": "COMPOSE",
    "C": "FLIP",
    "D": "DCOMPOSE",
    "Y": "RECURSE",
    "W": "DUPLICATE",
    "WHNF": "HALT",
}
# Also track beta-reduction variants (observed in v12 tracer)
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# § 1  Model Loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3.6-27B and return the language model + tokenizer.

    Qwen3.6-27B is a vision-language model (Qwen3_5ForConditionalGeneration).
    Hierarchy:
      full_model.model.visual           — vision encoder (ignore)
      full_model.model.language_model   — the text transformer we want
        .embed_tokens                   — token embeddings
        .layers[0..63]                  — 64 decoder layers
        .norm                           — final RMSNorm
        .rotary_emb                     — RoPE
      full_model.lm_head               — output projection

    Layer types (all Qwen3_5DecoderLayer):
      Linear attn (48 layers): .linear_attn (GatedDeltaNet) + .mlp
      Full attn   (16 layers): .self_attn (Attention) + .mlp
      MLP identical: gate_proj(17408,5120), up_proj(17408,5120),
                     down_proj(5120,17408), SiLU activation
    """
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    from transformers import Qwen3_5ForConditionalGeneration
    full_model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_NAME,
        torch_dtype=torch.bfloat16,
        device_map="auto",
        low_cpu_mem_usage=True,
    )
    full_model.eval()

    # The language model is where the layers live
    lang_model = full_model.model.language_model
    log(f"  Loaded in {time.time()-t0:.1f}s")
    log(f"  Language model type: {type(lang_model).__name__}")
    log(f"  N layers: {len(lang_model.layers)}")

    return lang_model, full_model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# § 2  FFN Activation Capture
# ══════════════════════════════════════════════════════════════════════

def get_mlp_module(lang_model, layer_idx: int):
    """Get the MLP/FFN module for a given layer.

    Qwen3.6-27B has SwiGLU FFN (identical on both layer types):
      gate = silu(gate_proj(x))     — (5120 → 17408)
      up = up_proj(x)               — (5120 → 17408)
      down = down_proj(gate * up)   — (17408 → 5120)
    """
    return lang_model.layers[layer_idx].mlp


def capture_ffn_and_residual(
    lang_model,
    full_model,
    tokenizer,
    text: str,
    layers: list[int] | None = None,
) -> dict:
    """Capture FFN output AND residual stream at specified layers, last token.

    Uses a single forward pass through the full VLM with text-only input.
    Hooks are placed on lang_model.layers[i] (the actual transformer layers).

    Returns:
      {layer_idx: {"ffn_out": np.array, "residual_pre": np.array}}
    """
    if layers is None:
        layers = list(range(N_LAYERS))

    ids = tokenizer.encode(text, return_tensors="pt")
    # Move to the device of the first model parameter
    device = next(full_model.parameters()).device
    ids = ids.to(device)

    captures = {}
    hooks = []

    for li in layers:
        captures[li] = {}

        # Hook the MLP down_proj output (FFN contribution to residual)
        def make_ffn_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx]["ffn_out"] = out[0, -1, :].detach().cpu().float().numpy()
            return hook

        mlp = get_mlp_module(lang_model, li)
        hooks.append(mlp.down_proj.register_forward_hook(make_ffn_hook(li)))

        # Hook the layer input (residual before this layer)
        def make_pre_hook(layer_idx):
            def hook(m, inp, out=None):
                # Input to the decoder layer: first positional arg is hidden_states
                x = inp[0] if isinstance(inp, tuple) else inp
                captures[layer_idx]["residual_pre"] = x[0, -1, :].detach().cpu().float().numpy()
            return hook

        layer = lang_model.layers[li]
        hooks.append(layer.register_forward_pre_hook(make_pre_hook(li)))

    with torch.no_grad():
        # Forward pass through the full model with text-only input
        # (no pixel_values → skips vision encoder, goes straight to language model)
        _ = full_model(input_ids=ids)

    for h in hooks:
        h.remove()

    return captures


# ══════════════════════════════════════════════════════════════════════
# § 3  Combinator Fingerprinting
# ══════════════════════════════════════════════════════════════════════

# Compile gate for fingerprinting context
COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def build_fingerprint_pairs() -> dict[str, list[tuple[str, str]]]:
    """Minimal pairs for each combinator reduction.

    Each pair is (pre_reduction, post_reduction). The FFN delta between
    them IS the combinator's fingerprint — the neural signature of that
    specific reduction operation.
    """
    pairs = {}

    # K: λx.λy.x — select first, discard second
    pairs["K"] = [
        (f"K {a} {b}", f"{a}")
        for a in ["x", "y", "a", "b", "f", "g"]
        for b in ["z", "w", "c", "d"] if a != b
    ][:10]

    # I: λx.x — identity
    pairs["I"] = [
        (f"I {v}", f"{v}")
        for v in ["x", "y", "a", "b", "f", "g", "z", "w"]
    ]

    # B: λf.λg.λx.f(g(x)) — compose
    pairs["B"] = [
        (f"B {f} {g} {x}", f"{f} ({g} {x})")
        for f in ["f", "g", "h", "p"]
        for g in ["q", "r", "s"] if f != g
        for x in ["x", "a"]
    ][:10]

    # C: λf.λx.λy.f(y)(x) — flip arguments
    pairs["C"] = [
        (f"C {f} {x} {y}", f"{f} {y} {x}")
        for f in ["f", "g", "h"]
        for x in ["x", "a", "m"]
        for y in ["y", "b", "n"] if x != y
    ][:10]

    # D: B∘B = λf.λg.λh.λx.f(g(h(x))) — deep compose
    pairs["D"] = [
        (f"D {f} {g} {h} {x}", f"{f} ({g} ({h} {x}))")
        for f in ["f", "p"]
        for g in ["g", "q"]
        for h in ["h", "r"] if f != g and g != h
        for x in ["x", "a"]
    ][:8]

    # Y: λf.f(Y(f)) — fixed point / recursion
    pairs["Y"] = [
        (f"Y {f}", f"{f} (Y {f})")
        for f in ["f", "g", "h", "p", "q", "r"]
    ]

    # W: λf.λx.f(x)(x) — duplicate/self-apply
    pairs["W"] = [
        (f"W {f} {x}", f"{f} {x} {x}")
        for f in ["f", "g", "h", "p"]
        for x in ["x", "a", "b"]
    ][:8]

    # WHNF: terminal forms — already reduced, nothing to do
    # Fingerprint: contrast reducible vs irreducible
    pairs["WHNF"] = [
        (f"λx. {body}", f"λx. {body}")  # Already in WHNF
        for body in ["x", "f x", "g (h x)", "x y", "f (g x) y"]
    ][:6]

    # Beta reductions (explicit lambda applications)
    pairs["beta_K"] = [
        (f"(λx. λy. x) {a} {b}", f"{a}")
        for a in ["a", "b", "x", "m"]
        for b in ["c", "y", "n"] if a != b
    ][:8]

    pairs["beta_I"] = [
        (f"(λx. x) {v}", f"{v}")
        for v in ["a", "b", "x", "y", "f", "g", "z", "w"]
    ]

    pairs["beta_apply"] = [
        (f"(λx. {f} x) {v}", f"{f} {v}")
        for f in ["f", "g", "h", "p", "q"]
        for v in ["a", "x", "m"]
    ][:10]

    pairs["beta_compose"] = [
        (f"(λx. {f} ({g} x)) {v}", f"{f} ({g} {v})")
        for f in ["f", "g", "h"]
        for g in ["p", "q", "r"] if f != g
        for v in ["a", "x"]
    ][:8]

    return pairs


def build_fingerprints(lang_model, full_model, tokenizer) -> dict[str, dict[int, np.ndarray]]:
    """Compute mean FFN delta vectors per combinator per layer.

    These are the "opcodes" — the characteristic FFN signature of each
    combinator reduction operation in the teacher model.
    """
    log("\n═══ Phase 1: Building combinator fingerprints (Qwen3.6-27B) ═══")
    log(f"  64 layers × {N_OPS} operations = {64 * N_OPS} fingerprint vectors")

    pairs = build_fingerprint_pairs()
    fingerprints = {}  # {op_name: {layer: unit_delta_vector}}

    # Sample a subset of layers for faster fingerprinting
    # Use all layers but process in batches
    fp_layers = list(range(N_LAYERS))

    for op_name, op_pairs in pairs.items():
        log(f"\n  {op_name}: {len(op_pairs)} pairs")
        layer_deltas = {li: [] for li in fp_layers}

        for pi, (pre_expr, post_expr) in enumerate(op_pairs):
            pre_text = f"{COMPILE_GATE}\n\n{pre_expr} ="
            post_text = f"{COMPILE_GATE}\n\n{post_expr} ="

            pre_caps = capture_ffn_and_residual(lang_model, full_model, tokenizer,
                                                 pre_text, fp_layers)
            post_caps = capture_ffn_and_residual(lang_model, full_model, tokenizer,
                                                  post_text, fp_layers)

            for li in fp_layers:
                pre_ffn = pre_caps.get(li, {}).get("ffn_out")
                post_ffn = post_caps.get(li, {}).get("ffn_out")
                if pre_ffn is not None and post_ffn is not None:
                    delta = pre_ffn - post_ffn
                    layer_deltas[li].append(delta)

            if (pi + 1) % 3 == 0:
                log(f"    pair {pi+1}/{len(op_pairs)}")

        # Average and normalize
        fingerprints[op_name] = {}
        for li in fp_layers:
            vecs = layer_deltas[li]
            if len(vecs) > 0:
                mean_delta = np.mean(vecs, axis=0)
                norm = np.linalg.norm(mean_delta)
                if norm > 1e-10:
                    fingerprints[op_name][li] = mean_delta / norm
                else:
                    fingerprints[op_name][li] = mean_delta

        log(f"    ✓ {op_name} fingerprints computed ({len(fingerprints[op_name])} layers)")

    return fingerprints


# ══════════════════════════════════════════════════════════════════════
# § 4  Overlay Matrix Computation
# ══════════════════════════════════════════════════════════════════════

def compute_overlay_matrices(
    lang_model,
    fingerprints: dict[str, dict[int, np.ndarray]],
) -> list[dict]:
    """Compute the FFN overlay matrix for each layer.

    The overlay matrix maps combinator-space input to combinator-space output.
    Each entry overlay[i][j] = how much combinator-direction-i input produces
    combinator-direction-j output through this layer's FFN.

    This IS the instruction. The diagonal is "pass through" (identity for
    that combinator type). Off-diagonal is "transform" (one combinator type
    converting to another).
    """
    log("\n═══ Phase 2: Computing overlay matrices ═══")

    overlays = []
    ops = list(fingerprints.keys())
    n_ops = len(ops)

    for li in range(N_LAYERS):
        # Build the fingerprint matrix for this layer: (n_ops, d_model)
        fp_matrix = []
        valid_ops = []
        for op in ops:
            if li in fingerprints[op]:
                fp_matrix.append(fingerprints[op][li])
                valid_ops.append(op)

        if len(fp_matrix) < 2:
            overlays.append({"layer": li, "valid": False})
            continue

        fp_matrix = np.array(fp_matrix)  # (n_valid_ops, d_model)

        # The overlay matrix: how do fingerprints project onto each other?
        # overlay[i][j] = cosine(fingerprint_i, fingerprint_j) at this layer
        # Diagonal should be 1.0 (self-similarity)
        # Off-diagonal shows which operations share neural substrate
        norms = np.linalg.norm(fp_matrix, axis=1, keepdims=True) + 1e-10
        fp_unit = fp_matrix / norms
        overlay = fp_unit @ fp_unit.T  # (n_ops, n_ops)

        # Also compute the FFN weight-based overlay if we have access
        # to the actual FFN weights (gate_proj, up_proj, down_proj)
        mlp = get_mlp_module(lang_model, li)
        gate_w = mlp.gate_proj.weight.detach().cpu().float().numpy()  # (d_ff, d_model)
        up_w = mlp.up_proj.weight.detach().cpu().float().numpy()      # (d_ff, d_model)
        down_w = mlp.down_proj.weight.detach().cpu().float().numpy()  # (d_model, d_ff)

        # Project FFN weights through fingerprint basis
        # How does each combinator direction get processed by this FFN?
        # gate response: fingerprint_i → gate_proj → activation pattern
        gate_response = fp_unit @ gate_w.T  # (n_ops, d_ff) — how each op activates the gate
        up_response = fp_unit @ up_w.T      # (n_ops, d_ff) — how each op activates up_proj

        # SwiGLU: output = down_proj(silu(gate) * up)
        # Linearized: for direction d_i, the effective transform is:
        # d_i → gate_proj → silu → element_wise_mult(up_proj(d_i)) → down_proj → output
        # The overlay in combinator space:
        # output_in_combinator_j = fingerprint_j · down_proj(silu(gate_proj(fingerprint_i)) * up_proj(fingerprint_i))

        # Compute the effective transform for each fingerprint direction
        effective_overlay = np.zeros((len(valid_ops), len(valid_ops)))
        for i in range(len(valid_ops)):
            # SwiGLU activation for fingerprint direction i
            gate_act = 1.0 / (1.0 + np.exp(-gate_response[i]))  # sigmoid approx of silu
            gate_act = gate_response[i] * gate_act  # silu = x * sigmoid(x)
            combined = gate_act * up_response[i]  # element-wise product
            output = combined @ down_w.T  # back to d_model space: (d_model,)
            # Project output back into fingerprint basis
            output_norm = np.linalg.norm(output)
            if output_norm > 1e-10:
                output_unit = output / output_norm
                for j in range(len(valid_ops)):
                    effective_overlay[i][j] = float(np.dot(output_unit, fp_unit[j]))

        # Classify layer type
        layer_type = "full_attn" if li in FULL_ATTN_LAYERS else "linear_attn"

        overlays.append({
            "layer": li,
            "layer_type": layer_type,
            "valid": True,
            "ops": valid_ops,
            "cosine_overlay": overlay.tolist(),
            "effective_overlay": effective_overlay.tolist(),
            "diagonal": np.diag(effective_overlay).tolist(),
            "off_diag_norm": float(np.linalg.norm(
                effective_overlay - np.diag(np.diag(effective_overlay)))),
        })

        if li % 8 == 0:
            log(f"    Layer {li:2d} ({layer_type:>11s}): "
                f"diag_mean={np.mean(np.diag(effective_overlay)):.3f}, "
                f"off_diag={overlays[-1]['off_diag_norm']:.3f}")

    return overlays


# ══════════════════════════════════════════════════════════════════════
# § 5  Instruction Decoder
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Instruction:
    """One decoded instruction from one layer of the model."""
    layer: int
    layer_type: str  # "full_attn" or "linear_attn"
    opcode: str      # Primary operation (SELECT, COMPOSE, etc.)
    op_source: str   # Which combinator fingerprint matched (K, B, etc.)
    strength: float  # Cosine similarity of primary match
    secondary_ops: list[tuple[str, float]] = field(default_factory=list)
    # Operand tracking
    residual_pc: dict[str, float] = field(default_factory=dict)  # combinator decomposition of residual
    ffn_delta_pc: dict[str, float] = field(default_factory=dict)  # combinator decomposition of FFN output
    # Control flow signals
    halt_signal: float = 0.0  # WHNF activation strength
    recurse_signal: float = 0.0  # Y activation strength
    select_signal: float = 0.0  # K activation strength (conditional branch)
    # Overlay info
    dominant_transform: str = ""  # What the FFN converts FROM → TO
    transform_strength: float = 0.0


@dataclass
class BasicBlock:
    """A sequence of instructions forming a logical unit."""
    start_layer: int
    end_layer: int
    phase: str  # "composition", "selection", "routing", "recursion", "terminal"
    instructions: list[Instruction] = field(default_factory=list)
    summary: str = ""


def decode_trace(
    captures: dict,
    fingerprints: dict,
    overlays: list[dict],
    threshold: float = 0.10,
) -> list[Instruction]:
    """Decode a full model trace into instruction sequence."""
    instructions = []
    ops = list(fingerprints.keys())

    for li in sorted(captures.keys()):
        cap = captures[li]
        ffn_out = cap.get("ffn_out")
        residual_pre = cap.get("residual_pre")

        if ffn_out is None:
            continue

        layer_type = "full_attn" if li in FULL_ATTN_LAYERS else "linear_attn"

        # Project FFN output against all fingerprints
        ffn_norm = np.linalg.norm(ffn_out)
        if ffn_norm < 1e-10:
            instructions.append(Instruction(
                layer=li, layer_type=layer_type,
                opcode="NOP", op_source="none", strength=0.0,
            ))
            continue

        ffn_unit = ffn_out / ffn_norm

        scores = {}
        for op in ops:
            if li in fingerprints[op]:
                cos = float(np.dot(ffn_unit, fingerprints[op][li]))
                scores[op] = cos

        if not scores:
            continue

        # Primary opcode: highest absolute cosine match
        ranked = sorted(scores.items(), key=lambda x: abs(x[1]), reverse=True)
        primary_op = ranked[0][0]
        primary_score = ranked[0][1]

        # Map to ISA opcode
        if primary_op in OPCODE_NAMES:
            opcode = OPCODE_NAMES[primary_op]
        elif primary_op.startswith("beta_"):
            base = primary_op.replace("beta_", "").upper()
            opcode = f"β_{base}"
        else:
            opcode = primary_op.upper()

        # Secondary ops (above threshold, excluding primary)
        secondary = [
            (OPCODE_NAMES.get(op, op.upper()), score)
            for op, score in ranked[1:]
            if abs(score) > threshold
        ]

        # Residual stream decomposition (operand tracking)
        residual_pc = {}
        if residual_pre is not None:
            res_norm = np.linalg.norm(residual_pre)
            if res_norm > 1e-10:
                res_unit = residual_pre / res_norm
                for op in ops:
                    if li in fingerprints[op]:
                        residual_pc[op] = float(np.dot(res_unit, fingerprints[op][li]))

        # FFN delta decomposition
        ffn_delta_pc = scores.copy()

        # Control flow signals
        halt_signal = abs(scores.get("WHNF", 0.0))
        recurse_signal = abs(scores.get("Y", 0.0))
        select_signal = abs(scores.get("K", 0.0)) + abs(scores.get("beta_K", 0.0))

        # Overlay-based transform detection
        dominant_transform = ""
        transform_strength = 0.0
        if li < len(overlays) and overlays[li].get("valid"):
            ov = overlays[li]
            eff = np.array(ov["effective_overlay"])
            ov_ops = ov["ops"]
            # Find the strongest off-diagonal element
            np.fill_diagonal(eff, 0)
            if eff.size > 0:
                max_idx = np.unravel_index(np.argmax(np.abs(eff)), eff.shape)
                if abs(eff[max_idx]) > 0.05:
                    src_op = ov_ops[max_idx[0]] if max_idx[0] < len(ov_ops) else "?"
                    dst_op = ov_ops[max_idx[1]] if max_idx[1] < len(ov_ops) else "?"
                    dominant_transform = f"{src_op}→{dst_op}"
                    transform_strength = abs(float(eff[max_idx]))

        instructions.append(Instruction(
            layer=li,
            layer_type=layer_type,
            opcode=opcode,
            op_source=primary_op,
            strength=primary_score,
            secondary_ops=secondary,
            residual_pc=residual_pc,
            ffn_delta_pc=ffn_delta_pc,
            halt_signal=halt_signal,
            recurse_signal=recurse_signal,
            select_signal=select_signal,
            dominant_transform=dominant_transform,
            transform_strength=transform_strength,
        ))

    return instructions


# ══════════════════════════════════════════════════════════════════════
# § 6  Basic Block Formation
# ══════════════════════════════════════════════════════════════════════

def form_basic_blocks(instructions: list[Instruction]) -> list[BasicBlock]:
    """Group instructions into basic blocks based on phase transitions.

    A new block starts when:
    - The dominant operation family changes (composition↔selection↔routing)
    - A control flow signal is strong (HALT, RECURSE)
    - Layer type changes (linear_attn ↔ full_attn)
    """
    if not instructions:
        return []

    def classify_phase(inst: Instruction) -> str:
        if inst.halt_signal > 0.3:
            return "terminal"
        if inst.recurse_signal > 0.3:
            return "recursion"
        if inst.opcode in ("SELECT", "β_K", "β_I"):
            return "selection"
        if inst.opcode in ("COMPOSE", "DCOMPOSE", "β_COMPOSE", "β_APPLY"):
            return "composition"
        if inst.opcode in ("FLIP",):
            return "routing"
        if inst.opcode in ("DUPLICATE",):
            return "duplication"
        if inst.opcode == "PASS":
            return "identity"
        return "mixed"

    blocks = []
    current_block = BasicBlock(
        start_layer=instructions[0].layer,
        end_layer=instructions[0].layer,
        phase=classify_phase(instructions[0]),
        instructions=[instructions[0]],
    )

    for inst in instructions[1:]:
        phase = classify_phase(inst)
        # Start new block on phase transition or significant control flow
        if (phase != current_block.phase or
                inst.halt_signal > 0.4 or
                inst.recurse_signal > 0.4):
            # Finalize current block
            current_block.end_layer = current_block.instructions[-1].layer
            current_block.summary = _summarize_block(current_block)
            blocks.append(current_block)
            # Start new block
            current_block = BasicBlock(
                start_layer=inst.layer,
                end_layer=inst.layer,
                phase=phase,
                instructions=[inst],
            )
        else:
            current_block.instructions.append(inst)

    # Finalize last block
    current_block.end_layer = current_block.instructions[-1].layer
    current_block.summary = _summarize_block(current_block)
    blocks.append(current_block)

    return blocks


def _summarize_block(block: BasicBlock) -> str:
    """Generate human-readable summary of a basic block."""
    n = len(block.instructions)
    opcodes = [i.opcode for i in block.instructions]
    unique_ops = set(opcodes)
    dominant = max(set(opcodes), key=opcodes.count)
    avg_strength = np.mean([abs(i.strength) for i in block.instructions])

    return (f"L{block.start_layer}-L{block.end_layer}: "
            f"{block.phase} phase, {n} layers, "
            f"dominant={dominant} ({avg_strength:.2f}), "
            f"ops={{{', '.join(sorted(unique_ops))}}}")


# ══════════════════════════════════════════════════════════════════════
# § 7  Disassembly Formatter
# ══════════════════════════════════════════════════════════════════════

def format_disassembly(
    instructions: list[Instruction],
    blocks: list[BasicBlock],
    label: str = "",
) -> str:
    """Format decoded program as human-readable disassembly."""
    lines = []

    lines.append(f"╔══════════════════════════════════════════════════════════════╗")
    if label:
        lines.append(f"║  PROGRAM: {label[:55]:<55s} ║")
    lines.append(f"║  {len(instructions)} instructions, {len(blocks)} basic blocks")
    lines.append(f"╠══════════════════════════════════════════════════════════════╣")

    # Phase summary
    phase_counts = {}
    for b in blocks:
        phase_counts[b.phase] = phase_counts.get(b.phase, 0) + len(b.instructions)
    phases_str = " | ".join(f"{p}:{c}" for p, c in sorted(phase_counts.items(), key=lambda x: -x[1]))
    lines.append(f"║  Phases: {phases_str}")
    lines.append(f"╠══════════════════════════════════════════════════════════════╣")

    # Per-block disassembly
    for bi, block in enumerate(blocks):
        lines.append(f"║")
        lines.append(f"║  ┌── BLOCK {bi}: {block.phase.upper()} (L{block.start_layer}..L{block.end_layer}) ──")
        lines.append(f"║  │  {block.summary}")
        lines.append(f"║  │")

        for inst in block.instructions:
            # Instruction line
            attn_marker = "F" if inst.layer_type == "full_attn" else "L"
            strength_bar = "█" * max(1, int(abs(inst.strength) * 10))

            # Primary opcode with strength
            primary = f"{inst.opcode:>10s}({inst.op_source})"
            strength = f"{inst.strength:+.3f}"

            # Secondary ops (compact)
            sec_str = ""
            if inst.secondary_ops:
                top_sec = inst.secondary_ops[:2]
                sec_str = " + " + ", ".join(f"{op}:{s:+.2f}" for op, s in top_sec)

            # Transform info
            xform = ""
            if inst.dominant_transform and inst.transform_strength > 0.05:
                xform = f" [{inst.dominant_transform} {inst.transform_strength:.2f}]"

            # Control flow markers
            ctrl = ""
            if inst.halt_signal > 0.2:
                ctrl += " ⏹"
            if inst.recurse_signal > 0.2:
                ctrl += " ↻"
            if inst.select_signal > 0.4:
                ctrl += " ⎇"

            lines.append(
                f"║  │ {attn_marker} L{inst.layer:02d}: {primary} {strength} "
                f"{strength_bar}{sec_str}{xform}{ctrl}"
            )

            # Operand flow (compact — top 3 residual PCs)
            if inst.residual_pc:
                top_res = sorted(inst.residual_pc.items(),
                                 key=lambda x: abs(x[1]), reverse=True)[:3]
                res_str = ", ".join(f"{op}:{v:+.2f}" for op, v in top_res)
                lines.append(f"║  │        operands: [{res_str}]")

        lines.append(f"║  └──")

    lines.append(f"╚══════════════════════════════════════════════════════════════╝")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# § 8  Probe Suite
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Diverse probes for tracing — same categories as v12 tracer plus more."""
    probes = []

    # ── Lambda compilation (the compiler circuit) ──
    probes.append({
        "category": "lambda",
        "label": "NL→λ: Every student read a book",
        "text": f"{COMPILE_GATE}\n\nEvery student read a book =",
    })
    probes.append({
        "category": "lambda",
        "label": "NL→λ: The cat sat on the mat",
        "text": f"{COMPILE_GATE}\n\nThe cat sat on the mat =",
    })
    probes.append({
        "category": "lambda",
        "label": "NL→λ: If it rains then streets are wet",
        "text": f"{COMPILE_GATE}\n\nIf it rains then the streets are wet =",
    })

    # ── Combinator reduction (validation) ──
    probes.append({
        "category": "reduction",
        "label": "K a b = a",
        "text": f"{COMPILE_GATE}\n\nK a b =",
    })
    probes.append({
        "category": "reduction",
        "label": "B f g x = f(gx)",
        "text": f"{COMPILE_GATE}\n\nB f g x =",
    })
    probes.append({
        "category": "reduction",
        "label": "S f g x = fx(gx)",
        "text": f"{COMPILE_GATE}\n\nS f g x =",
    })
    probes.append({
        "category": "reduction",
        "label": "S K K x = x (SKK = I)",
        "text": f"{COMPILE_GATE}\n\nS K K x =",
    })

    # ── Arithmetic (church encoding / beta reduction piles) ──
    probes.append({
        "category": "arithmetic",
        "label": "2 + 3 = 5",
        "text": "Calculate: 2 + 3 =",
    })
    probes.append({
        "category": "arithmetic",
        "label": "17 × 23 = 391",
        "text": "Calculate: 17 × 23 =",
    })
    probes.append({
        "category": "arithmetic",
        "label": "sqrt(169) = 13",
        "text": "Calculate: sqrt(169) =",
    })

    # ── Reasoning (compositional logic) ──
    probes.append({
        "category": "reasoning",
        "label": "Syllogism: A⊂B, B⊂C ∴ A⊂C",
        "text": "All dogs are animals. All animals are living things. Therefore all dogs are",
    })
    probes.append({
        "category": "reasoning",
        "label": "Contrapositive: A→B, ¬B ∴ ¬A",
        "text": "If it rains, the ground is wet. The ground is not wet. Therefore,",
    })
    probes.append({
        "category": "reasoning",
        "label": "Analogy: A:B :: C:?",
        "text": "Hot is to cold as fast is to",
    })

    # ── Retrieval (factual lookup — should NOT use combinator FFN) ──
    probes.append({
        "category": "retrieval",
        "label": "Capital of France",
        "text": "The capital of France is",
    })
    probes.append({
        "category": "retrieval",
        "label": "Water formula",
        "text": "The chemical formula for water is",
    })
    probes.append({
        "category": "retrieval",
        "label": "Einstein birth year",
        "text": "Albert Einstein was born in the year",
    })

    # ── Code generation (structural composition) ──
    probes.append({
        "category": "code",
        "label": "Python fibonacci",
        "text": "def fibonacci(n):\n    ",
    })
    probes.append({
        "category": "code",
        "label": "Python sort",
        "text": "def quicksort(arr):\n    if len(arr) <= 1:\n        return arr\n    ",
    })

    # ── String manipulation (sequential processing) ──
    probes.append({
        "category": "string",
        "label": "Reverse 'hello'",
        "text": "Reverse the letters in 'hello': ",
    })

    # ── Translation (deep structural mapping) ──
    probes.append({
        "category": "translation",
        "label": "English→French: The cat",
        "text": "Translate to French: The cat sat on the mat →",
    })

    return probes


# ══════════════════════════════════════════════════════════════════════
# § 9  Cross-Category Analysis
# ══════════════════════════════════════════════════════════════════════

def analyze_categories(all_results: list[dict]) -> dict:
    """Compare instruction sequences across task categories."""
    categories = sorted(set(r["category"] for r in all_results))
    analysis = {}

    for cat in categories:
        cat_results = [r for r in all_results if r["category"] == cat]

        # Aggregate opcode distributions
        opcode_counts = {}
        total_instructions = 0
        phase_counts = {}

        for r in cat_results:
            for inst in r["instructions"]:
                op = inst["opcode"]
                opcode_counts[op] = opcode_counts.get(op, 0) + 1
                total_instructions += 1

            for block in r["blocks"]:
                phase = block["phase"]
                # blocks are serialized with "n_instructions", not the list itself
                n_inst = block.get("n_instructions", len(block.get("instructions", [])))
                phase_counts[phase] = phase_counts.get(phase, 0) + n_inst

        # Normalize to distribution
        if total_instructions > 0:
            opcode_dist = {op: count / total_instructions
                           for op, count in opcode_counts.items()}
        else:
            opcode_dist = {}

        # Average control flow signals per depth region
        depth_signals = {"early": [], "mid": [], "late": []}
        for r in cat_results:
            for inst in r["instructions"]:
                li = inst["layer"]
                region = "early" if li < 21 else ("mid" if li < 43 else "late")
                depth_signals[region].append({
                    "halt": inst["halt_signal"],
                    "recurse": inst["recurse_signal"],
                    "select": inst["select_signal"],
                    "strength": abs(inst["strength"]),
                })

        avg_signals = {}
        for region, signals in depth_signals.items():
            if signals:
                avg_signals[region] = {
                    "halt": np.mean([s["halt"] for s in signals]),
                    "recurse": np.mean([s["recurse"] for s in signals]),
                    "select": np.mean([s["select"] for s in signals]),
                    "strength": np.mean([s["strength"] for s in signals]),
                }

        analysis[cat] = {
            "n_probes": len(cat_results),
            "opcode_distribution": opcode_dist,
            "phase_distribution": phase_counts,
            "depth_signals": avg_signals,
        }

    return analysis


# ══════════════════════════════════════════════════════════════════════
# § 10  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════════════")
    log("  ISA DECODER — Decompiling Qwen3.6-27B to Instruction Sets")
    log("  Session 161")
    log("═══════════════════════════════════════════════════════════════")
    log(f"  Model: {MODEL_NAME}")
    log(f"  Layers: {N_LAYERS} ({len(FULL_ATTN_LAYERS)} full attn, {len(LINEAR_ATTN_LAYERS)} linear attn)")
    log(f"  Operations: {', '.join(ALL_OP_NAMES)}")
    log(f"  Device: {DEVICE}")

    t0 = time.time()

    # ── Load model ─────────────────────────────────────────────
    lang_model, full_model, tokenizer = load_model()

    # ── Phase 1: Build fingerprints ────────────────────────────
    t1 = time.time()
    fingerprints = build_fingerprints(lang_model, full_model, tokenizer)
    log(f"\n  ⏱ Phase 1 (fingerprinting): {time.time()-t1:.1f}s")

    # Save fingerprints (just the norms for verification, not the full vectors)
    fp_summary = {}
    for op, layers in fingerprints.items():
        fp_summary[op] = {
            "n_layers": len(layers),
            "layer_norms": {str(li): float(np.linalg.norm(v))
                            for li, v in layers.items()},
        }
    with open(RESULTS_DIR / "fingerprints_summary.json", "w") as f:
        json.dump(fp_summary, f, indent=2)
    log(f"\n  Fingerprint summary saved")

    # ── Phase 2: Compute overlay matrices ──────────────────────
    t2 = time.time()
    overlays = compute_overlay_matrices(lang_model, fingerprints)
    log(f"\n  ⏱ Phase 2 (overlay matrices): {time.time()-t2:.1f}s")
    with open(RESULTS_DIR / "overlay_matrices.json", "w") as f:
        json.dump(overlays, f, indent=2)
    log(f"\n  Overlay matrices saved ({len(overlays)} layers)")

    # ── Phase 3: Trace probes ──────────────────────────────────
    t3 = time.time()
    log("\n═══ Phase 3: Tracing diverse inputs ═══")
    probes = build_probes()
    all_results = []

    for pi, probe in enumerate(probes):
        log(f"\n  [{pi+1}/{len(probes)}] {probe['category']}: {probe['label']}")

        # Capture FFN + residual at all layers
        captures = capture_ffn_and_residual(
            lang_model, full_model, tokenizer, probe["text"])

        # Decode to instructions
        instructions = decode_trace(captures, fingerprints, overlays)

        # Form basic blocks
        blocks = form_basic_blocks(instructions)

        # Format disassembly
        disasm = format_disassembly(instructions, blocks, probe["label"])
        log(disasm)

        # Serialize instructions
        inst_data = []
        for inst in instructions:
            inst_data.append({
                "layer": inst.layer,
                "layer_type": inst.layer_type,
                "opcode": inst.opcode,
                "op_source": inst.op_source,
                "strength": inst.strength,
                "secondary_ops": inst.secondary_ops,
                "residual_pc": inst.residual_pc,
                "ffn_delta_pc": inst.ffn_delta_pc,
                "halt_signal": inst.halt_signal,
                "recurse_signal": inst.recurse_signal,
                "select_signal": inst.select_signal,
                "dominant_transform": inst.dominant_transform,
                "transform_strength": inst.transform_strength,
            })

        block_data = []
        for block in blocks:
            block_data.append({
                "start_layer": block.start_layer,
                "end_layer": block.end_layer,
                "phase": block.phase,
                "summary": block.summary,
                "n_instructions": len(block.instructions),
            })

        all_results.append({
            "category": probe["category"],
            "label": probe["label"],
            "text": probe["text"][:200],
            "instructions": inst_data,
            "blocks": block_data,
            "n_instructions": len(instructions),
            "n_blocks": len(blocks),
        })

    log(f"\n  ⏱ Phase 3 (tracing): {time.time()-t3:.1f}s")

    # ── Phase 4: Cross-category analysis ──────────────────────
    log("\n═══ Phase 4: Cross-Category Analysis ═══")
    cat_analysis = analyze_categories(all_results)

    for cat, analysis in cat_analysis.items():
        log(f"\n  {cat.upper()} ({analysis['n_probes']} probes):")

        # Opcode distribution
        op_dist = analysis["opcode_distribution"]
        sorted_ops = sorted(op_dist.items(), key=lambda x: -x[1])[:5]
        log(f"    Top opcodes: {', '.join(f'{op}:{pct:.1%}' for op, pct in sorted_ops)}")

        # Phase distribution
        phase_dist = analysis["phase_distribution"]
        log(f"    Phases: {', '.join(f'{p}:{c}' for p, c in sorted(phase_dist.items(), key=lambda x: -x[1]))}")

        # Depth signals
        for region, sigs in analysis.get("depth_signals", {}).items():
            log(f"    {region:>5}: halt={sigs['halt']:.3f}, "
                f"recurse={sigs['recurse']:.3f}, "
                f"select={sigs['select']:.3f}, "
                f"strength={sigs['strength']:.3f}")

    # ── Save all results ───────────────────────────────────────
    elapsed = time.time() - t0

    results = {
        "experiment": "isa_decode",
        "session": 161,
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "full_attn_layers": FULL_ATTN_LAYERS,
        "linear_attn_layers": LINEAR_ATTN_LAYERS,
        "operations": ALL_OP_NAMES,
        "elapsed_s": elapsed,
        "n_probes": len(probes),
        "traces": all_results,
        "category_analysis": {k: {
            "n_probes": v["n_probes"],
            "opcode_distribution": v["opcode_distribution"],
            "phase_distribution": v["phase_distribution"],
            "depth_signals": {
                region: {sk: float(sv) for sk, sv in sigs.items()}
                for region, sigs in v.get("depth_signals", {}).items()
            },
        } for k, v in cat_analysis.items()},
        "overlay_summary": [
            {
                "layer": ov["layer"],
                "layer_type": ov.get("layer_type", "?"),
                "valid": ov["valid"],
                "diagonal": ov.get("diagonal", []),
                "off_diag_norm": ov.get("off_diag_norm", 0),
            }
            for ov in overlays
        ],
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n═══════════════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {RESULTS_DIR / 'results.json'}")
    log(f"  Overlays: {RESULTS_DIR / 'overlay_matrices.json'}")
    log(f"  Fingerprints: {RESULTS_DIR / 'fingerprints_summary.json'}")
    log(f"═══════════════════════════════════════════════════════════════")

    # Cleanup
    del lang_model, full_model, tokenizer
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


if __name__ == "__main__":
    main()
