"""Moiré Grating Decoder v2 — Read the program from the weights.

Session 161. The FFN IS a moiré grating. gate_proj and up_proj are
two diffraction patterns that interfere through element-wise multiply
(SwiGLU). Where they constructively interfere = a beta reduction that
attention will follow. The grating is static — burned into weights by
GD. Attention has exactly ONE operation (weighted sum). The grating
is what makes that one operation perform different beta reductions at
different layers.

The program is deterministic. GD found a fixed point. The crystal
lattice shows up identically across models because these are the
energy minima of what a single-operation machine can compute through
shaped diffraction. Non-determinism exists only at the leaves
(token selection via temperature).

Architecture:
  Qwen3.6-27B: 64 layers, d=5120, d_ff=17408
  [L,L,L,F]×16: 48 linear attention + 16 full attention
  16 full-attention checkpoints at L3,7,11,...,63

This script:
  Phase 1: Load/build fingerprints (saved as .npz for reuse)
  Phase 2: Read static program from weights (overlay matrices = instruction ROM)
  Phase 3: Trace inputs with attention capture at 16 full-attn checkpoints
  Phase 4: Assemble: grating → activation → attention reads → data flow

Usage:
    cd ~/src/verbum
    uv run python scripts/v14/isa_decoder_v2.py 2>&1 | tee results/isa-decode-v2/run.log

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
from transformers import AutoTokenizer

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode-v2"
V1_DIR = Path(__file__).parent.parent.parent / "results" / "isa-decode"
MODEL_NAME = "Qwen/Qwen3.6-27B"
DEVICE = "mps"

# Architecture
N_LAYERS = 64
D_MODEL = 5120
D_FF = 17408
N_HEADS = 24
N_KV_HEADS = 4
D_HEAD = 256  # Note: Qwen3.6-27B uses 256-dim heads (not d_model/n_heads)
FULL_ATTN_LAYERS = list(range(3, 64, 4))  # [3, 7, 11, ..., 63]
LINEAR_ATTN_LAYERS = [i for i in range(64) if i not in FULL_ATTN_LAYERS]

# Combinator basis
COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)

FINGERPRINT_FILE = RESULTS_DIR / "fingerprints_full.npz"

COMPILE_GATE = """You are a lambda calculus compiler. Convert natural language to typed lambda calculus.
Input a combinator expression. Output its beta-normal form.
Be terse. Output ONLY the reduced expression."""


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# § 1  Model Loading
# ══════════════════════════════════════════════════════════════════════

def load_model():
    """Load Qwen3.6-27B, return language model + full model + tokenizer."""
    log(f"  Loading {MODEL_NAME}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    from transformers import Qwen3_5ForConditionalGeneration
    full_model = Qwen3_5ForConditionalGeneration.from_pretrained(
        MODEL_NAME, torch_dtype=torch.bfloat16,
        device_map="auto", low_cpu_mem_usage=True,
        attn_implementation="eager",  # Required to capture attention weights
    )
    full_model.eval()
    lang_model = full_model.model.language_model

    log(f"  Loaded in {time.time()-t0:.1f}s ({len(lang_model.layers)} layers)")
    return lang_model, full_model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# § 2  Fingerprinting (with save/load)
# ══════════════════════════════════════════════════════════════════════

def build_fingerprint_pairs() -> dict[str, list[tuple[str, str]]]:
    """Minimal pairs for each combinator. Same as v1."""
    pairs = {}
    pairs["K"] = [(f"K {a} {b}", f"{a}") for a in ["x","y","a","b","f","g"] for b in ["z","w","c","d"] if a!=b][:10]
    pairs["I"] = [(f"I {v}", f"{v}") for v in ["x","y","a","b","f","g","z","w"]]
    pairs["B"] = [(f"B {f} {g} {x}", f"{f} ({g} {x})") for f in ["f","g","h","p"] for g in ["q","r","s"] if f!=g for x in ["x","a"]][:10]
    pairs["C"] = [(f"C {f} {x} {y}", f"{f} {y} {x}") for f in ["f","g","h"] for x in ["x","a","m"] for y in ["y","b","n"] if x!=y][:10]
    pairs["D"] = [(f"D {f} {g} {h} {x}", f"{f} ({g} ({h} {x}))") for f in ["f","p"] for g in ["g","q"] for h in ["h","r"] if f!=g and g!=h for x in ["x","a"]][:8]
    pairs["Y"] = [(f"Y {f}", f"{f} (Y {f})") for f in ["f","g","h","p","q","r"]]
    pairs["W"] = [(f"W {f} {x}", f"{f} {x} {x}") for f in ["f","g","h","p"] for x in ["x","a","b"]][:8]
    pairs["WHNF"] = [(f"λx. {b}", f"λx. {b}") for b in ["x","f x","g (h x)","x y","f (g x) y"]][:6]
    pairs["beta_K"] = [(f"(λx. λy. x) {a} {b}", f"{a}") for a in ["a","b","x","m"] for b in ["c","y","n"] if a!=b][:8]
    pairs["beta_I"] = [(f"(λx. x) {v}", f"{v}") for v in ["a","b","x","y","f","g","z","w"]]
    pairs["beta_apply"] = [(f"(λx. {f} x) {v}", f"{f} {v}") for f in ["f","g","h","p","q"] for v in ["a","x","m"]][:10]
    pairs["beta_compose"] = [(f"(λx. {f} ({g} x)) {v}", f"{f} ({g} {v})") for f in ["f","g","h"] for g in ["p","q","r"] if f!=g for v in ["a","x"]][:8]
    return pairs


def capture_ffn(lang_model, full_model, tokenizer, text: str, layers: list[int]) -> dict:
    """Capture FFN down_proj output at specified layers, last token."""
    ids = tokenizer.encode(text, return_tensors="pt")
    device = next(full_model.parameters()).device
    ids = ids.to(device)

    captures = {}
    hooks = []
    for li in layers:
        def make_hook(layer_idx):
            def hook(m, inp, out):
                captures[layer_idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(lang_model.layers[li].mlp.down_proj.register_forward_hook(make_hook(li)))

    with torch.no_grad():
        _ = full_model(input_ids=ids)

    for h in hooks:
        h.remove()
    return captures


def build_fingerprints(lang_model, full_model, tokenizer) -> dict[str, np.ndarray]:
    """Build or load fingerprints. Returns {op_name: (n_layers, d_model)} arrays."""

    # Try loading saved fingerprints
    if FINGERPRINT_FILE.exists():
        log(f"  Loading saved fingerprints from {FINGERPRINT_FILE}")
        data = np.load(FINGERPRINT_FILE)
        fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
        if len(fingerprints) == N_OPS:
            log(f"  ✓ Loaded {N_OPS} ops × {fingerprints[ALL_OP_NAMES[0]].shape[0]} layers")
            return fingerprints
        log(f"  ⚠ Incomplete ({len(fingerprints)}/{N_OPS}), rebuilding...")

    log(f"\n═══ Building fingerprints ({N_OPS} ops × {N_LAYERS} layers) ═══")
    pairs = build_fingerprint_pairs()
    all_layers = list(range(N_LAYERS))
    fingerprints = {}

    for op_name, op_pairs in pairs.items():
        log(f"  {op_name}: {len(op_pairs)} pairs")
        # Accumulate deltas: (n_layers, d_model)
        layer_deltas = {li: [] for li in all_layers}

        for pi, (pre_expr, post_expr) in enumerate(op_pairs):
            pre_text = f"{COMPILE_GATE}\n\n{pre_expr} ="
            post_text = f"{COMPILE_GATE}\n\n{post_expr} ="
            pre_caps = capture_ffn(lang_model, full_model, tokenizer, pre_text, all_layers)
            post_caps = capture_ffn(lang_model, full_model, tokenizer, post_text, all_layers)

            for li in all_layers:
                if li in pre_caps and li in post_caps:
                    layer_deltas[li].append(pre_caps[li] - post_caps[li])

            if (pi + 1) % 3 == 0:
                log(f"    pair {pi+1}/{len(op_pairs)}")

        # Build (n_layers, d_model) array of unit vectors
        fp_array = np.zeros((N_LAYERS, D_MODEL), dtype=np.float32)
        for li in all_layers:
            vecs = layer_deltas[li]
            if vecs:
                mean = np.mean(vecs, axis=0)
                norm = np.linalg.norm(mean)
                if norm > 1e-10:
                    fp_array[li] = mean / norm
        fingerprints[op_name] = fp_array
        log(f"    ✓ {op_name}")

    # Save for reuse
    FINGERPRINT_FILE.parent.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(FINGERPRINT_FILE, **fingerprints)
    log(f"  Saved fingerprints to {FINGERPRINT_FILE}")
    return fingerprints


# ══════════════════════════════════════════════════════════════════════
# § 3  Static Program (from weights)
# ══════════════════════════════════════════════════════════════════════

@dataclass
class GratingDescriptor:
    """One layer's moiré grating — the static instruction."""
    layer: int
    layer_type: str  # "full_attn" or "linear_attn"

    # Diagonal: how much each combinator direction passes through
    diagonal: dict[str, float] = field(default_factory=dict)

    # Dominant transforms: strongest off-diagonal couplings
    transforms: list[tuple[str, str, float]] = field(default_factory=list)  # (from, to, strength)

    # Overall character
    pass_through_strength: float = 0.0  # mean |diagonal|
    transform_strength: float = 0.0     # off-diagonal norm
    selectivity: str = ""               # "pass" | "transform" | "mixed"

    # Top-3 summary
    summary: str = ""


def read_static_program(lang_model, fingerprints: dict[str, np.ndarray]) -> list[GratingDescriptor]:
    """Read the static moiré grating program from the FFN weights.

    The grating at each layer is the SwiGLU interference pattern:
      grating(x) = down_proj(silu(gate_proj(x)) * up_proj(x))

    We characterize it by projecting through the combinator fingerprint
    basis to get a combinator-space transform matrix.
    """
    log("\n═══ Reading static program from weights ═══")
    ops = ALL_OP_NAMES
    gratings = []

    for li in range(N_LAYERS):
        layer_type = "full_attn" if li in FULL_ATTN_LAYERS else "linear_attn"

        # Build fingerprint matrix for this layer
        fp_vecs = []
        valid_ops = []
        for op in ops:
            v = fingerprints[op][li]
            if np.linalg.norm(v) > 1e-10:
                fp_vecs.append(v / np.linalg.norm(v))
                valid_ops.append(op)

        if len(fp_vecs) < 2:
            gratings.append(GratingDescriptor(layer=li, layer_type=layer_type,
                                               summary="(insufficient fingerprints)"))
            continue

        fp_matrix = np.array(fp_vecs)  # (n_valid, d_model)

        # Get FFN weights
        mlp = lang_model.layers[li].mlp
        gate_w = mlp.gate_proj.weight.detach().cpu().float().numpy()  # (d_ff, d_model)
        up_w = mlp.up_proj.weight.detach().cpu().float().numpy()
        down_w = mlp.down_proj.weight.detach().cpu().float().numpy()  # (d_model, d_ff)

        # Project fingerprint directions through the SwiGLU
        # For each combinator direction, compute the effective output
        gate_resp = fp_matrix @ gate_w.T  # (n_ops, d_ff)
        up_resp = fp_matrix @ up_w.T      # (n_ops, d_ff)

        overlay = np.zeros((len(valid_ops), len(valid_ops)))
        for i in range(len(valid_ops)):
            # SwiGLU: silu(gate) * up → down_proj
            sig = 1.0 / (1.0 + np.exp(-gate_resp[i]))
            silu = gate_resp[i] * sig
            combined = silu * up_resp[i]
            output = combined @ down_w.T  # (d_model,)
            out_norm = np.linalg.norm(output)
            if out_norm > 1e-10:
                output_unit = output / out_norm
                for j in range(len(valid_ops)):
                    overlay[i][j] = float(np.dot(output_unit, fp_matrix[j]))

        # Characterize the grating
        diag = {valid_ops[i]: float(overlay[i][i]) for i in range(len(valid_ops))}
        pass_strength = np.mean(np.abs(np.diag(overlay)))

        # Off-diagonal: find strongest transforms
        off_diag = overlay.copy()
        np.fill_diagonal(off_diag, 0)
        xform_strength = float(np.linalg.norm(off_diag))

        transforms = []
        # Top 3 off-diagonal elements
        for _ in range(3):
            idx = np.unravel_index(np.argmax(np.abs(off_diag)), off_diag.shape)
            val = float(off_diag[idx])
            if abs(val) > 0.03:
                transforms.append((valid_ops[idx[0]], valid_ops[idx[1]], val))
                off_diag[idx] = 0
            else:
                break

        # Selectivity classification
        if pass_strength > xform_strength * 1.5:
            selectivity = "pass"
        elif xform_strength > pass_strength * 1.5:
            selectivity = "transform"
        else:
            selectivity = "mixed"

        # Summary: top 3 diagonal elements
        sorted_diag = sorted(diag.items(), key=lambda x: abs(x[1]), reverse=True)[:3]
        diag_str = " ".join(f"{op}:{v:+.2f}" for op, v in sorted_diag)
        xform_str = " ".join(f"{s}→{d}:{v:+.2f}" for s, d, v in transforms[:2]) if transforms else "—"
        summary = f"[{selectivity:>9}] diag:[{diag_str}] xform:[{xform_str}]"

        gratings.append(GratingDescriptor(
            layer=li, layer_type=layer_type,
            diagonal=diag, transforms=transforms,
            pass_through_strength=pass_strength,
            transform_strength=xform_strength,
            selectivity=selectivity, summary=summary,
        ))

        if li % 16 == 0:
            log(f"  L{li:02d}: {summary}")

        # Free weight memory
        del gate_w, up_w, down_w

    log(f"  ✓ {len(gratings)} gratings characterized")
    return gratings


# ══════════════════════════════════════════════════════════════════════
# § 4  Trace with Attention Capture
# ══════════════════════════════════════════════════════════════════════

@dataclass
class AttentionSnapshot:
    """Attention pattern at one full-attention layer."""
    layer: int
    # Per-head: which positions does the last token attend to?
    # head_focus[head_idx] = list of (position, weight) sorted by weight
    head_focus: list[list[tuple[int, float]]] = field(default_factory=list)
    # Aggregate: top attended positions across all heads
    aggregate_focus: list[tuple[int, float]] = field(default_factory=list)
    # Which position dominates (the "primary operand")
    primary_pos: int = -1
    primary_weight: float = 0.0


@dataclass
class LayerTrace:
    """One layer's trace for a specific input."""
    layer: int
    layer_type: str
    # FFN activation projected onto fingerprints
    grating_activation: dict[str, float] = field(default_factory=dict)
    primary_op: str = ""
    primary_strength: float = 0.0
    # Residual stream in combinator space (what data is flowing)
    residual_pc: dict[str, float] = field(default_factory=dict)
    # FFN output norm (how much this layer changes the residual)
    ffn_norm: float = 0.0
    # Attention snapshot (only for full-attn layers)
    attention: AttentionSnapshot | None = None


def trace_with_attention(
    lang_model, full_model, tokenizer,
    text: str,
    fingerprints: dict[str, np.ndarray],
) -> tuple[list[LayerTrace], list[str], list[int]]:
    """Full trace: FFN activation + residual + attention at full-attn layers.

    Returns (traces, tokens_text, token_ids).
    """
    ids = tokenizer.encode(text, return_tensors="pt")
    token_ids = ids[0].tolist()
    tokens_text = [tokenizer.decode([tid]) for tid in token_ids]

    device = next(full_model.parameters()).device
    ids = ids.to(device)
    seq_len = ids.shape[1]

    # Storage for captures
    ffn_caps = {}     # {layer: ffn_out_vector}
    res_caps = {}     # {layer: residual_pre_vector}
    attn_caps = {}    # {layer: attn_weights_tensor}  (full-attn only)

    hooks = []

    for li in range(N_LAYERS):
        # FFN capture
        def make_ffn_hook(layer_idx):
            def hook(m, inp, out):
                ffn_caps[layer_idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(lang_model.layers[li].mlp.down_proj.register_forward_hook(make_ffn_hook(li)))

        # Residual capture
        def make_res_hook(layer_idx):
            def hook(m, inp, out=None):
                x = inp[0] if isinstance(inp, tuple) else inp
                res_caps[layer_idx] = x[0, -1, :].detach().cpu().float().numpy()
            return hook
        hooks.append(lang_model.layers[li].register_forward_pre_hook(make_res_hook(li)))

        # Attention capture at full-attention layers
        if li in FULL_ATTN_LAYERS:
            def make_attn_hook(layer_idx):
                def hook(m, inp, out):
                    # The self_attn module returns (attn_output, attn_weights, past_kv)
                    # or just (attn_output,) depending on config
                    # We need to hook deeper — capture QK product after softmax
                    # Instead, let's capture via output_attentions mechanism
                    pass  # handled via output_attentions flag below
                return hook
            # We'll use output_attentions instead of manual hooks for attention

    # Run forward pass with output_attentions=True
    with torch.no_grad():
        outputs = full_model(input_ids=ids, output_attentions=True)

    for h in hooks:
        h.remove()

    # Extract attention weights from outputs
    # With eager attention, only the 16 full-attention layers return weights.
    # outputs.attentions is a tuple of 16 elements:
    #   attns[0] = L3, attns[1] = L7, ..., attns[15] = L63
    # Each is (batch, 24_heads, seq_len, seq_len).
    # Linear-attention layers (GatedDeltaNet) don't produce standard attention.
    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
        attns = outputs.attentions
        n_attn = len(attns)
        if n_attn == len(FULL_ATTN_LAYERS):
            # Direct mapping: attns[i] → FULL_ATTN_LAYERS[i]
            for idx, attn_w in enumerate(attns):
                if attn_w is not None:
                    layer_idx = FULL_ATTN_LAYERS[idx]
                    attn_caps[layer_idx] = attn_w[0].detach().cpu().float().numpy()
        elif n_attn == N_LAYERS:
            # All layers returned (unlikely but handle it)
            for li, attn_w in enumerate(attns):
                if attn_w is not None and li in FULL_ATTN_LAYERS:
                    attn_caps[li] = attn_w[0].detach().cpu().float().numpy()
        else:
            log(f"  ⚠ Unexpected attention count: {n_attn} (expected {len(FULL_ATTN_LAYERS)} or {N_LAYERS})")

    # Build trace objects
    ops = ALL_OP_NAMES
    traces = []

    for li in range(N_LAYERS):
        layer_type = "full_attn" if li in FULL_ATTN_LAYERS else "linear_attn"
        trace = LayerTrace(layer=li, layer_type=layer_type)

        # FFN activation → fingerprint projection
        ffn_out = ffn_caps.get(li)
        if ffn_out is not None:
            trace.ffn_norm = float(np.linalg.norm(ffn_out))
            if trace.ffn_norm > 1e-10:
                ffn_unit = ffn_out / trace.ffn_norm
                for op in ops:
                    v = fingerprints[op][li]
                    if np.linalg.norm(v) > 1e-10:
                        trace.grating_activation[op] = float(np.dot(ffn_unit, v))

                if trace.grating_activation:
                    ranked = sorted(trace.grating_activation.items(),
                                    key=lambda x: abs(x[1]), reverse=True)
                    trace.primary_op = ranked[0][0]
                    trace.primary_strength = ranked[0][1]

        # Residual stream → fingerprint projection
        res = res_caps.get(li)
        if res is not None:
            res_norm = np.linalg.norm(res)
            if res_norm > 1e-10:
                res_unit = res / res_norm
                for op in ops:
                    v = fingerprints[op][li]
                    if np.linalg.norm(v) > 1e-10:
                        trace.residual_pc[op] = float(np.dot(res_unit, v))

        # Attention snapshot (full-attn only)
        if li in attn_caps:
            attn_w = attn_caps[li]  # (n_heads, seq_len, seq_len)
            n_heads_actual = attn_w.shape[0]
            last_pos = seq_len - 1

            snap = AttentionSnapshot(layer=li)

            # Per-head focus at the decoding position
            agg = np.zeros(seq_len)
            for h in range(n_heads_actual):
                weights = attn_w[h, last_pos, :]  # (seq_len,)
                # Top positions for this head
                sorted_idx = np.argsort(weights)[::-1]
                head_top = [(int(idx), float(weights[idx]))
                            for idx in sorted_idx[:5]
                            if weights[idx] > 0.01]
                snap.head_focus.append(head_top)
                agg += weights

            # Aggregate across heads
            agg /= n_heads_actual
            sorted_agg = np.argsort(agg)[::-1]
            snap.aggregate_focus = [(int(idx), float(agg[idx]))
                                    for idx in sorted_agg[:5]
                                    if agg[idx] > 0.01]

            if snap.aggregate_focus:
                snap.primary_pos = snap.aggregate_focus[0][0]
                snap.primary_weight = snap.aggregate_focus[0][1]

            trace.attention = snap

        traces.append(trace)

    return traces, tokens_text, token_ids


# ══════════════════════════════════════════════════════════════════════
# § 5  Assembly Formatter
# ══════════════════════════════════════════════════════════════════════

def format_assembly(
    traces: list[LayerTrace],
    gratings: list[GratingDescriptor],
    tokens_text: list[str],
    label: str = "",
) -> str:
    """Format as moiré grating assembly — the full program view."""
    lines = []
    seq_len = len(tokens_text)

    # Header
    lines.append("═" * 90)
    if label:
        lines.append(f"  PROGRAM: {label}")
    tok_str = "  ".join(f"{t.strip()}({i})" for i, t in enumerate(tokens_text))
    lines.append(f"  Tokens: {tok_str}")
    lines.append(f"  Decoding at position {seq_len - 1}")
    lines.append("═" * 90)
    lines.append("")

    # Column headers
    lines.append(f"{'':>3} {'Ly':>3} {'T':>1}  {'STATIC GRATING':^35s} │ {'ACTIVATION':^20s} │ {'ATTENTION (full-attn only)':^35s}")
    lines.append("─" * 3 + "─" * 4 + "─" * 2 + "─" * 36 + "┼" + "─" * 22 + "┼" + "─" * 36)

    prev_was_checkpoint = False

    for li in range(N_LAYERS):
        trace = traces[li]
        grating = gratings[li]
        is_full = li in FULL_ATTN_LAYERS

        # Grating column
        if grating.summary:
            # Compact: top 2 diagonal + top transform
            sorted_diag = sorted(grating.diagonal.items(), key=lambda x: abs(x[1]), reverse=True)[:2]
            diag_str = " ".join(f"{op}:{v:+.2f}" for op, v in sorted_diag)
            if grating.transforms:
                xf = grating.transforms[0]
                xf_str = f" {xf[0]}→{xf[1]}:{xf[2]:+.2f}"
            else:
                xf_str = ""
            grating_str = f"{diag_str}{xf_str}"
        else:
            grating_str = "—"

        # Activation column
        if trace.primary_op:
            act_str = f"{trace.primary_op:>6}:{trace.primary_strength:+.2f}"
            # Add FFN norm as a bar
            bar_len = min(8, max(1, int(trace.ffn_norm / 50)))
            act_str += " " + "█" * bar_len
        else:
            act_str = "—"

        # Attention column
        attn_str = ""
        if trace.attention and trace.attention.aggregate_focus:
            snap = trace.attention
            # Show top 3 positions with token text
            parts = []
            for pos, wt in snap.aggregate_focus[:3]:
                tok = tokens_text[pos].strip() if pos < len(tokens_text) else "?"
                parts.append(f"{tok}({pos}):{wt:.2f}")
            attn_str = " ".join(parts)

            # Arrow showing primary read
            if snap.primary_pos >= 0:
                ptok = tokens_text[snap.primary_pos].strip() if snap.primary_pos < len(tokens_text) else "?"
                attn_str += f" → {ptok}"
        elif is_full:
            attn_str = "(no attn data)"
        else:
            attn_str = "[recurrent]"

        # Layer type marker
        type_marker = "F" if is_full else "·"

        # Checkpoint separator for full-attention layers
        if is_full and not prev_was_checkpoint:
            lines.append(f"{'':>3} {'':>3} {'':>1}  {'── FULL ATTENTION CHECKPOINT ──':^35s} │ {'':^20s} │")

        lines.append(
            f"   L{li:02d} {type_marker}  {grating_str:<35s} │ {act_str:<20s} │ {attn_str}"
        )

        prev_was_checkpoint = is_full

    lines.append("═" * 90)

    # Data flow summary: how does attention focus change across checkpoints?
    lines.append("")
    lines.append("  ATTENTION DATA FLOW (16 checkpoints):")
    lines.append(f"  {'Layer':>5}  {'Primary Read':>20}  {'Weight':>7}  {'Secondary':>30}")
    lines.append("  " + "─" * 70)

    for li in FULL_ATTN_LAYERS:
        trace = traces[li]
        if trace.attention and trace.attention.aggregate_focus:
            snap = trace.attention
            ppos = snap.primary_pos
            ptok = tokens_text[ppos].strip() if 0 <= ppos < len(tokens_text) else "?"
            pwt = snap.primary_weight

            sec_parts = []
            for pos, wt in snap.aggregate_focus[1:3]:
                tok = tokens_text[pos].strip() if pos < len(tokens_text) else "?"
                sec_parts.append(f"{tok}({pos}):{wt:.2f}")
            sec_str = ", ".join(sec_parts) if sec_parts else "—"

            lines.append(f"  L{li:02d}    {ptok+'('+str(ppos)+')':>20}  {pwt:>7.3f}  {sec_str}")
        else:
            lines.append(f"  L{li:02d}    {'(no data)':>20}")

    lines.append("")
    return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════
# § 6  Probes
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Diverse probes — focused set for detailed assembly analysis."""
    probes = []

    # Combinator reductions — the clearest signal
    probes.append({"category": "reduction", "label": "K a b = a (select first)",
                    "text": f"{COMPILE_GATE}\n\nK a b ="})
    probes.append({"category": "reduction", "label": "B f g x = f(gx) (compose)",
                    "text": f"{COMPILE_GATE}\n\nB f g x ="})
    probes.append({"category": "reduction", "label": "S K K x = x (identity from selection)",
                    "text": f"{COMPILE_GATE}\n\nS K K x ="})

    # Lambda compilation
    probes.append({"category": "lambda", "label": "NL→λ: Every student read a book",
                    "text": f"{COMPILE_GATE}\n\nEvery student read a book ="})
    probes.append({"category": "lambda", "label": "NL→λ: The cat sat on the mat",
                    "text": f"{COMPILE_GATE}\n\nThe cat sat on the mat ="})

    # Arithmetic
    probes.append({"category": "arithmetic", "label": "2 + 3 = 5",
                    "text": "Calculate: 2 + 3 ="})
    probes.append({"category": "arithmetic", "label": "17 × 23 = 391",
                    "text": "Calculate: 17 × 23 ="})

    # Reasoning
    probes.append({"category": "reasoning", "label": "Syllogism: A⊂B, B⊂C ∴ A⊂C",
                    "text": "All dogs are animals. All animals are living things. Therefore all dogs are"})

    # Retrieval
    probes.append({"category": "retrieval", "label": "Capital of France",
                    "text": "The capital of France is"})

    # Code
    probes.append({"category": "code", "label": "Python fibonacci",
                    "text": "def fibonacci(n):\n    "})

    return probes


# ══════════════════════════════════════════════════════════════════════
# § 7  Determinism Check
# ══════════════════════════════════════════════════════════════════════

def check_determinism(
    lang_model, full_model, tokenizer,
    fingerprints: dict[str, np.ndarray],
    text: str,
    n_runs: int = 3,
) -> dict:
    """Verify that the same input produces identical traces.

    This confirms the program is a fixed point — the moiré gratings
    produce the same beta reductions every time.
    """
    log(f"\n  Determinism check ({n_runs} runs)...")
    traces_all = []
    for run in range(n_runs):
        traces, _, _ = trace_with_attention(lang_model, full_model, tokenizer,
                                             text, fingerprints)
        # Extract primary ops and strengths
        program = [(t.primary_op, round(t.primary_strength, 6)) for t in traces]
        traces_all.append(program)

    # Compare
    identical = all(t == traces_all[0] for t in traces_all[1:])
    max_drift = 0.0
    for run_idx in range(1, n_runs):
        for li in range(N_LAYERS):
            drift = abs(traces_all[run_idx][li][1] - traces_all[0][li][1])
            max_drift = max(max_drift, drift)

    log(f"    Identical programs: {identical}")
    log(f"    Max strength drift: {max_drift:.8f}")

    return {"identical": identical, "max_drift": max_drift, "n_runs": n_runs}


# ══════════════════════════════════════════════════════════════════════
# § 8  Main
# ══════════════════════════════════════════════════════════════════════

def main():
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log("═══════════════════════════════════════════════════════════════")
    log("  MOIRÉ GRATING DECODER v2")
    log("  Reading the program from the weights")
    log("  Session 161")
    log("═══════════════════════════════════════════════════════════════")
    log(f"  Model: {MODEL_NAME}")
    log(f"  Full-attention checkpoints: {FULL_ATTN_LAYERS}")

    t0 = time.time()

    # ── Load model ─────────────────────────────────────────────
    lang_model, full_model, tokenizer = load_model()

    # ── Phase 1: Fingerprints ──────────────────────────────────
    t1 = time.time()
    fingerprints = build_fingerprints(lang_model, full_model, tokenizer)
    log(f"  ⏱ Phase 1 (fingerprints): {time.time()-t1:.1f}s")

    # ── Phase 2: Static program from weights ───────────────────
    t2 = time.time()
    gratings = read_static_program(lang_model, fingerprints)
    log(f"  ⏱ Phase 2 (static program): {time.time()-t2:.1f}s")

    # Print static program
    log("\n═══ STATIC PROGRAM (from weights — same for ALL inputs) ═══")
    for g in gratings:
        marker = "F" if g.layer_type == "full_attn" else "·"
        log(f"  L{g.layer:02d} {marker} {g.summary}")

    # ── Phase 3: Determinism check ─────────────────────────────
    t3 = time.time()
    det_result = check_determinism(
        lang_model, full_model, tokenizer, fingerprints,
        f"{COMPILE_GATE}\n\nK a b =",
        n_runs=3,
    )
    log(f"  ⏱ Phase 3 (determinism): {time.time()-t3:.1f}s")

    # ── Phase 4: Trace probes ──────────────────────────────────
    t4 = time.time()
    log("\n═══ Phase 4: Tracing with attention capture ═══")
    probes = build_probes()
    all_results = []

    for pi, probe in enumerate(probes):
        log(f"\n  [{pi+1}/{len(probes)}] {probe['category']}: {probe['label']}")

        traces, tokens_text, token_ids = trace_with_attention(
            lang_model, full_model, tokenizer, probe["text"], fingerprints)

        # Format assembly
        assembly = format_assembly(traces, gratings, tokens_text, probe["label"])
        log(assembly)

        # Serialize
        trace_data = []
        for t in traces:
            td = {
                "layer": t.layer,
                "layer_type": t.layer_type,
                "primary_op": t.primary_op,
                "primary_strength": t.primary_strength,
                "ffn_norm": t.ffn_norm,
                "grating_activation": t.grating_activation,
                "residual_pc": t.residual_pc,
            }
            if t.attention:
                td["attention"] = {
                    "primary_pos": t.attention.primary_pos,
                    "primary_weight": t.attention.primary_weight,
                    "aggregate_focus": t.attention.aggregate_focus,
                    "n_heads_captured": len(t.attention.head_focus),
                }
            trace_data.append(td)

        all_results.append({
            "category": probe["category"],
            "label": probe["label"],
            "text": probe["text"][:200],
            "tokens": tokens_text,
            "token_ids": token_ids,
            "traces": trace_data,
        })

    log(f"\n  ⏱ Phase 4 (tracing): {time.time()-t4:.1f}s")

    # ── Phase 5: Cross-probe attention flow analysis ───────────
    log("\n═══ Phase 5: Attention Flow Comparison ═══")
    log(f"\n  How attention focus changes across checkpoints, by task type:")

    categories = sorted(set(r["category"] for r in all_results))
    for cat in categories:
        cat_results = [r for r in all_results if r["category"] == cat]
        log(f"\n  {cat.upper()} ({len(cat_results)} probes):")

        for r in cat_results:
            log(f"    {r['label']}:")
            log(f"    Tokens: {' '.join(r['tokens'][:15])}")
            log(f"    {'Layer':>7} {'Primary':>15} {'Wt':>6} {'Secondary':>25}")
            for td in r["traces"]:
                if "attention" in td and td["attention"]["primary_pos"] >= 0:
                    li = td["layer"]
                    attn = td["attention"]
                    ppos = attn["primary_pos"]
                    ptok = r["tokens"][ppos].strip() if ppos < len(r["tokens"]) else "?"
                    pwt = attn["primary_weight"]
                    sec = attn["aggregate_focus"][1:3] if len(attn["aggregate_focus"]) > 1 else []
                    sec_str = ", ".join(
                        f"{r['tokens'][p].strip() if p < len(r['tokens']) else '?'}({p}):{w:.2f}"
                        for p, w in sec
                    )
                    log(f"    L{li:02d}     {ptok+'('+str(ppos)+')':>15} {pwt:>6.3f} {sec_str}")

    # ── Save results ───────────────────────────────────────────
    elapsed = time.time() - t0

    # Serialize gratings
    grating_data = []
    for g in gratings:
        grating_data.append({
            "layer": g.layer,
            "layer_type": g.layer_type,
            "diagonal": g.diagonal,
            "transforms": [(s, d, v) for s, d, v in g.transforms],
            "pass_through_strength": g.pass_through_strength,
            "transform_strength": g.transform_strength,
            "selectivity": g.selectivity,
            "summary": g.summary,
        })

    results = {
        "experiment": "moire_grating_decoder_v2",
        "session": 161,
        "model": MODEL_NAME,
        "n_layers": N_LAYERS,
        "full_attn_layers": FULL_ATTN_LAYERS,
        "elapsed_s": elapsed,
        "determinism": det_result,
        "static_program": grating_data,
        "traces": all_results,
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(results, f, indent=2, default=str)

    log(f"\n═══════════════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {RESULTS_DIR / 'results.json'}")
    log(f"  Fingerprints: {FINGERPRINT_FILE}")
    log(f"  Determinism: {'PASS ✓' if det_result['identical'] else 'DRIFT ⚠'}")
    log(f"═══════════════════════════════════════════════════════════════")

    del lang_model, full_model, tokenizer
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


if __name__ == "__main__":
    main()
