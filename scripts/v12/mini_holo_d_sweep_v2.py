"""D-Sweep v2: Nested Composition Chains — Finding the Real Crossover.

v1 found no crossover because the KIBC reduction task (4 rules, 18 tokens)
saturates at 46.6% regardless of model capacity. Embeddings solve it alone.

v2 uses nested multi-step composition chains that require tracking
intermediate substitution states. Examples:

  Depth 1: K a b = a                          (simple lookup)
  Depth 2: K (I a) b = I a = a                (2-step reduction)
  Depth 3: K (B f g a) (I x) = B f g a = f (g a)   (3-step)
  Depth 4: B (K a) (C f b) x = K a (C f b x) = K a (f x b) = a

The key property: deeper chains require more intermediate states.
A d-dimensional embedding can represent a fixed number of patterns,
but d² plate weights can encode transformation RULES that compose.
As depth increases, lookup tables fail and compositional rules win.

Same five conditions as v1:
  GD, beam-only, plate-only, etch-first, beam-first

Same d sweep: [48, 96, 128, 192, 256]

License: MIT
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

from mini_holo import (
    TernaryLinear, BeamLayer, MiniHoloModel,
    count_plate_params, plate_fingerprint, plate_diff,
)


# ══════════════════════════════════════════════════════════════════════
# Tokenizer — extended for nested expressions
# ══════════════════════════════════════════════════════════════════════

TOKENS = [
    "<pad>", "<bos>", "<eos>", "=",
    "K", "I", "B", "C",                    # combinators
    "a", "b", "c", "d", "e",               # variables (5)
    "f", "g", "h",                          # function variables (3)
    "x", "y", "z",                          # argument variables (3)
    "(", ")",                               # grouping
]
TOK2ID = {t: i for i, t in enumerate(TOKENS)}
ID2TOK = {i: t for t, i in TOK2ID.items()}
VOCAB_SIZE = len(TOKENS)
PAD_ID = TOK2ID["<pad>"]
BOS_ID = TOK2ID["<bos>"]
EOS_ID = TOK2ID["<eos>"]
EQ_ID = TOK2ID["="]

VARS = ["a", "b", "c", "d", "e", "x", "y", "z"]
FVARS = ["f", "g", "h"]


def tokenize(text_tokens: list[str]) -> list[int]:
    return [TOK2ID[t] for t in text_tokens]


# ══════════════════════════════════════════════════════════════════════
# Expression tree — build, reduce, serialize
# ══════════════════════════════════════════════════════════════════════

class Expr:
    """Simple expression tree for combinator calculus."""
    pass

class Var(Expr):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name
    def __eq__(self, other):
        return isinstance(other, Var) and self.name == other.name
    def to_tokens(self) -> list[str]:
        return [self.name]
    def size(self) -> int:
        return 1

class App(Expr):
    def __init__(self, fn: Expr, arg: Expr):
        self.fn = fn
        self.arg = arg
    def __repr__(self):
        return f"({self.fn} {self.arg})"
    def to_tokens(self) -> list[str]:
        # Minimal parenthesization: parenthesize fn if it's an App
        fn_toks = self.fn.to_tokens()
        arg_toks = self.arg.to_tokens()
        if isinstance(self.fn, App):
            fn_toks = ["("] + fn_toks + [")"]
        if isinstance(self.arg, App):
            arg_toks = ["("] + arg_toks + [")"]
        return fn_toks + arg_toks
    def size(self) -> int:
        return 1 + self.fn.size() + self.arg.size()

class Comb(Expr):
    def __init__(self, name: str):
        self.name = name
    def __repr__(self):
        return self.name
    def to_tokens(self) -> list[str]:
        return [self.name]
    def size(self) -> int:
        return 1


def reduce_one_step(expr: Expr) -> tuple[Expr | None, bool]:
    """Try one step of combinator reduction. Returns (result, changed).

    K x y     → x
    I x       → x
    B f g x   → f (g x)
    C f x y   → f y x
    """
    if not isinstance(expr, App):
        return expr, False

    # Collect spine: ((((comb arg1) arg2) arg3) ...)
    spine = []
    cur = expr
    while isinstance(cur, App):
        spine.append(cur.arg)
        cur = cur.fn
    spine.reverse()  # [arg1, arg2, arg3, ...]

    if isinstance(cur, Comb):
        name = cur.name
        if name == "K" and len(spine) >= 2:
            # K x y → x, then re-apply remaining args
            result = spine[0]
            for arg in spine[2:]:
                result = App(result, arg)
            return result, True

        elif name == "I" and len(spine) >= 1:
            # I x → x
            result = spine[0]
            for arg in spine[1:]:
                result = App(result, arg)
            return result, True

        elif name == "B" and len(spine) >= 3:
            # B f g x → f (g x)
            f, g, x = spine[0], spine[1], spine[2]
            result = App(f, App(g, x))
            for arg in spine[3:]:
                result = App(result, arg)
            return result, True

        elif name == "C" and len(spine) >= 3:
            # C f x y → f y x
            f, x, y = spine[0], spine[1], spine[2]
            result = App(App(f, y), x)
            for arg in spine[3:]:
                result = App(result, arg)
            return result, True

    # Try reducing subexpressions (leftmost-outermost)
    if isinstance(expr, App):
        new_fn, changed = reduce_one_step(expr.fn)
        if changed:
            return App(new_fn, expr.arg), True
        new_arg, changed = reduce_one_step(expr.arg)
        if changed:
            return App(expr.fn, new_arg), True

    return expr, False


def full_reduce(expr: Expr, max_steps: int = 20) -> Expr:
    """Reduce expression to normal form (with step limit)."""
    for _ in range(max_steps):
        expr, changed = reduce_one_step(expr)
        if not changed:
            break
    return expr


def count_reduction_steps(expr: Expr, max_steps: int = 20) -> int:
    """Count how many reduction steps to normal form."""
    steps = 0
    for _ in range(max_steps):
        expr, changed = reduce_one_step(expr)
        if not changed:
            break
        steps += 1
    return steps


# ══════════════════════════════════════════════════════════════════════
# Expression generator — depth-controlled
# ══════════════════════════════════════════════════════════════════════

def random_var(rng: np.random.RandomState) -> Var:
    return Var(rng.choice(VARS))

def random_fvar(rng: np.random.RandomState) -> Var:
    return Var(rng.choice(FVARS))

def random_atom(rng: np.random.RandomState) -> Expr:
    """Random variable or function variable."""
    if rng.random() < 0.6:
        return random_var(rng)
    else:
        return random_fvar(rng)


def generate_expr_depth(rng: np.random.RandomState, target_depth: int) -> Expr:
    """Generate an expression that requires approximately target_depth
    reduction steps.

    Strategy: build nested combinator applications.
    Depth 1: single combinator + args (K a b, I x, B f g x, C f a b)
    Depth 2: combinator with one nested combinator arg
    Depth N: recursive nesting
    """
    if target_depth <= 1:
        # Simple single-step reduction
        comb = rng.choice(["K", "I", "B", "C"])
        if comb == "K":
            return App(App(Comb("K"), random_atom(rng)), random_atom(rng))
        elif comb == "I":
            return App(Comb("I"), random_atom(rng))
        elif comb == "B":
            return App(App(App(Comb("B"), random_fvar(rng)),
                           random_fvar(rng)), random_var(rng))
        elif comb == "C":
            return App(App(App(Comb("C"), random_fvar(rng)),
                           random_var(rng)), random_var(rng))

    # Deeper: nest a reducible expression as an argument to a combinator
    inner = generate_expr_depth(rng, target_depth - 1)

    comb = rng.choice(["K", "I", "B", "C"])
    if comb == "K":
        # K (inner) y → inner, then inner reduces further
        if rng.random() < 0.5:
            return App(App(Comb("K"), inner), random_atom(rng))
        else:
            return App(App(Comb("K"), random_atom(rng)), inner)
    elif comb == "I":
        # I (inner) → inner reduces
        return App(Comb("I"), inner)
    elif comb == "B":
        # B f g (inner) → f (g inner), inner may reduce later
        # or B (inner) g x → inner (g x)
        pos = rng.choice(["f", "arg"])
        if pos == "f":
            return App(App(App(Comb("B"), inner),
                           random_fvar(rng)), random_var(rng))
        else:
            return App(App(App(Comb("B"), random_fvar(rng)),
                           random_fvar(rng)), inner)
    elif comb == "C":
        pos = rng.choice(["f", "x", "y"])
        if pos == "f":
            return App(App(App(Comb("C"), inner),
                           random_var(rng)), random_var(rng))
        elif pos == "x":
            return App(App(App(Comb("C"), random_fvar(rng)),
                           inner), random_var(rng))
        else:
            return App(App(App(Comb("C"), random_fvar(rng)),
                           random_var(rng)), inner)


def generate_example(rng: np.random.RandomState, max_depth: int = 4,
                     max_input_tokens: int = 30,
                     max_output_tokens: int = 20) -> tuple[list[str], list[str], int] | None:
    """Generate a nested reduction example.

    Returns (input_tokens, output_tokens, depth) or None if too long.
    """
    depth = rng.randint(1, max_depth + 1)

    for _attempt in range(10):
        expr = generate_expr_depth(rng, depth)
        actual_depth = count_reduction_steps(expr)

        if actual_depth < 1:
            continue

        reduced = full_reduce(expr)

        inp_toks = expr.to_tokens()
        out_toks = reduced.to_tokens()

        # Check all tokens are in vocabulary
        if not all(t in TOK2ID for t in inp_toks):
            continue
        if not all(t in TOK2ID for t in out_toks):
            continue

        if len(inp_toks) > max_input_tokens:
            continue
        if len(out_toks) > max_output_tokens:
            continue

        full_input = ["<bos>"] + inp_toks + ["="]
        full_output = out_toks + ["<eos>"]

        return full_input, full_output, actual_depth

    return None


def generate_batch(batch_size: int, rng: np.random.RandomState,
                   max_len: int = 40, max_depth: int = 4,
                   ) -> tuple[mx.array, mx.array, mx.array]:
    """Generate batch of nested reduction examples.

    Returns (input_ids, targets, loss_mask).
    Loss mask is 1 for output tokens (after =).
    """
    all_ids = []
    all_targets = []
    all_masks = []

    for _ in range(batch_size):
        result = None
        for _try in range(20):
            result = generate_example(rng, max_depth=max_depth,
                                      max_input_tokens=max_len - 8,
                                      max_output_tokens=max_len - 8)
            if result is not None:
                break

        if result is None:
            # Fallback: trivial I x = x
            result = (["<bos>", "I", "a", "="], ["a", "<eos>"], 1)

        inp, out, depth = result
        seq = inp + out
        ids = [TOK2ID[t] for t in seq]

        n = len(ids)
        if n > max_len:
            ids = ids[:max_len]
            n = max_len
        ids = ids + [PAD_ID] * (max_len - n)

        target = ids[1:] + [PAD_ID]

        mask = [0] * max_len
        eq_pos = None
        for i, tok_id in enumerate(ids):
            if tok_id == EQ_ID:
                eq_pos = i
                mask[i] = 1
            elif eq_pos is not None and tok_id != PAD_ID and tok_id != EOS_ID:
                mask[i] = 1

        all_ids.append(ids)
        all_targets.append(target)
        all_masks.append(mask)

    return (
        mx.array(np.array(all_ids, dtype=np.int32)),
        mx.array(np.array(all_targets, dtype=np.int32)),
        mx.array(np.array(all_masks, dtype=np.float32)),
    )


# ══════════════════════════════════════════════════════════════════════
# GD Baseline model (with attention — needed for token rearrangement)
# ══════════════════════════════════════════════════════════════════════

class CausalSelfAttention(nn.Module):
    """Simple single-head causal self-attention."""
    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)
        self.scale = d_model ** -0.5

    def __call__(self, x: mx.array) -> mx.array:
        B, T, D = x.shape
        q = self.q_proj(x) * self.scale  # (B, T, D)
        k = self.k_proj(x)               # (B, T, D)
        v = self.v_proj(x)               # (B, T, D)

        # Attention weights with causal mask
        attn = q @ k.transpose(0, 2, 1)  # (B, T, T)
        # Causal mask: -inf above diagonal
        mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
        attn = attn + mask
        attn = mx.softmax(attn, axis=-1)

        out = attn @ v  # (B, T, D)
        return self.o_proj(out)


class GDLayer(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.attn = CausalSelfAttention(d_model)
        self.attn_norm = nn.LayerNorm(d_model)
        self.ffn = nn.Linear(d_model, d_model)
        self.ffn_norm = nn.LayerNorm(d_model)

    def __call__(self, x: mx.array) -> mx.array:
        x = x + self.attn(self.attn_norm(x))
        x = x + self.ffn(self.ffn_norm(x))
        return x


class GDModel(nn.Module):
    def __init__(self, d_model: int = 48, n_layers: int = 3):
        super().__init__()
        self.d_model = d_model
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [GDLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids: mx.array) -> mx.array:
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


# ══════════════════════════════════════════════════════════════════════
# Holographic model — attention with ternary plates + continuous beams
#
# Architecture mirrors GDModel but splits parameters into:
#   Plates (ternary): K, V, O projections + FFN (the holographic surface)
#   Beams (continuous): Q projection + beam scales + norms + embeds
#
# This matches the beam trace finding (session 098):
#   K, V, O → ternary-safe (plate)
#   Q → needs precision (beam angle)
# ══════════════════════════════════════════════════════════════════════

class TernaryCausalAttention(nn.Module):
    """Self-attention with ternary K/V/O (plates) and continuous Q (beam)."""
    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model
        # Q is the beam — continuous, needs precision
        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        # K, V, O are the plate — ternary
        self.k_plate = TernaryLinear(d_model, d_model)
        self.v_plate = TernaryLinear(d_model, d_model)
        self.o_plate = TernaryLinear(d_model, d_model)
        # Beam scales for K/V/O plate outputs
        self.k_scale = mx.ones((d_model,))
        self.v_scale = mx.ones((d_model,))
        self.o_scale = mx.ones((d_model,))
        self.scale = d_model ** -0.5

    def __call__(self, x: mx.array) -> mx.array:
        B, T, D = x.shape
        q = self.q_proj(x) * self.scale
        k = self.k_plate(x) * self.k_scale
        v = self.v_plate(x) * self.v_scale

        attn = q @ k.transpose(0, 2, 1)
        mask = mx.triu(mx.full((T, T), float("-inf")), k=1)
        attn = attn + mask
        attn = mx.softmax(attn, axis=-1)

        out = attn @ v
        out = self.o_plate(out) * self.o_scale
        return out


class HoloBeamLayer(nn.Module):
    def __init__(self, d_model: int):
        super().__init__()
        self.attn = TernaryCausalAttention(d_model)
        self.attn_norm = nn.LayerNorm(d_model)
        # FFN: ternary plate + beam scale
        self.ffn_plate = TernaryLinear(d_model, d_model)
        self.ffn_norm = nn.LayerNorm(d_model)
        self.ffn_scale = mx.ones((d_model,))
        self.ffn_bias = mx.zeros((d_model,))

    def __call__(self, x: mx.array) -> mx.array:
        x = x + self.attn(self.attn_norm(x))
        ffn_out = self.ffn_plate(self.ffn_norm(x)) * self.ffn_scale + self.ffn_bias
        x = x + ffn_out
        return x


class HoloModel(nn.Module):
    def __init__(self, d_model: int = 48, n_layers: int = 3):
        super().__init__()
        self.d_model = d_model
        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [HoloBeamLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids: mx.array) -> mx.array:
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


def count_holo_params(model: HoloModel) -> dict:
    plate_positions = 0
    beam_params = 0
    embed_params = 0
    for layer in model.layers:
        d = model.d_model
        # Plates: K, V, O attention + FFN
        plate_positions += d * d * 4  # k_plate, v_plate, o_plate, ffn_plate
        # Beams: Q projection (d*d) + scales (k,v,o,ffn = 4*d) + ffn_bias (d)
        beam_params += d * d  # q_proj
        beam_params += d * 4  # k_scale, v_scale, o_scale, ffn_scale
        beam_params += d      # ffn_bias
        # Norms (2 per layer, each has weight+bias = 2*d)
        beam_params += d * 4  # attn_norm + ffn_norm (weight + bias each)
    embed_params += model.embed.weight.size
    embed_params += sum(x.size for x in model.output_norm.parameters().values())
    embed_params += sum(x.size for x in model.output_proj.parameters().values())
    return {
        "plate_positions": plate_positions,
        "beam_params": beam_params,
        "embed_params": embed_params,
        "continuous": beam_params + embed_params,
        "total": plate_positions + beam_params + embed_params,
    }


# ══════════════════════════════════════════════════════════════════════
# Loss & eval
# ══════════════════════════════════════════════════════════════════════

def masked_ce_loss(model, input_ids, targets, mask):
    logits = model(input_ids)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V), targets.reshape(-1),
    ).reshape(B, T)
    return (ce * mask).sum() / (mask.sum() + 1e-8)


def eval_model(model, rng, n_batches=50, batch_size=64, max_depth=4):
    total_correct = 0
    total_tokens = 0
    total_loss = 0.0
    for _ in range(n_batches):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        logits = model(input_ids)
        mx.eval(logits)
        B, T, V = logits.shape
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1),
        ).reshape(B, T)
        loss = (ce * mask).sum() / (mask.sum() + 1e-8)
        mx.eval(loss)
        total_loss += float(loss.item())
        preds = mx.argmax(logits, axis=-1)
        correct = (preds == targets).astype(mx.float32) * mask
        mx.eval(correct)
        total_correct += float(correct.sum().item())
        total_tokens += float(mask.sum().item())
    return {
        "loss": total_loss / n_batches,
        "accuracy": total_correct / max(total_tokens, 1),
    }


def eval_by_depth(model, rng, n_samples_per_depth=200, max_depth=4):
    """Evaluate accuracy broken down by reduction depth."""
    depth_stats = {}
    for depth in range(1, max_depth + 1):
        correct = 0
        total = 0
        attempts = 0
        while total < n_samples_per_depth and attempts < n_samples_per_depth * 5:
            attempts += 1
            result = generate_example(rng, max_depth=depth,
                                      max_input_tokens=32,
                                      max_output_tokens=20)
            if result is None:
                continue
            inp, out, actual_depth = result
            if actual_depth != depth:
                continue

            seq = inp + out
            ids = [TOK2ID[t] for t in seq]
            max_len = 40
            ids = ids + [PAD_ID] * (max_len - len(ids))
            ids = ids[:max_len]
            target = ids[1:] + [PAD_ID]

            input_ids = mx.array(np.array([ids], dtype=np.int32))
            targets = mx.array(np.array([target], dtype=np.int32))

            logits = model(input_ids)
            mx.eval(logits)
            preds = mx.argmax(logits, axis=-1)
            mx.eval(preds)

            # Check output tokens after =
            eq_idx = None
            for i, tok in enumerate(ids):
                if tok == EQ_ID:
                    eq_idx = i
                    break
            if eq_idx is None:
                continue

            # Compare predicted output tokens
            pred_ids = list(np.array(preds[0]))
            target_ids = list(np.array(targets[0]))

            match = True
            for i in range(eq_idx, min(len(ids) - 1, max_len - 1)):
                if target_ids[i] == PAD_ID or target_ids[i] == EOS_ID:
                    break
                if pred_ids[i] != target_ids[i]:
                    match = False
                    break

            if match:
                correct += 1
            total += 1

        depth_stats[depth] = {
            "correct": correct,
            "total": total,
            "accuracy": correct / max(total, 1),
        }
    return depth_stats


# ══════════════════════════════════════════════════════════════════════
# Plate helpers
# ══════════════════════════════════════════════════════════════════════

def _get_plates(model: HoloModel) -> list[tuple[str, TernaryLinear]]:
    """Get all ternary plate modules with their path names."""
    plates = []
    for i, layer in enumerate(model.layers):
        plates.append((f"layers.{i}.attn.k_plate", layer.attn.k_plate))
        plates.append((f"layers.{i}.attn.v_plate", layer.attn.v_plate))
        plates.append((f"layers.{i}.attn.o_plate", layer.attn.o_plate))
        plates.append((f"layers.{i}.ffn_plate", layer.ffn_plate))
    return plates


def holo_plate_fingerprint(model: HoloModel) -> list[np.ndarray]:
    return [np.sign(np.array(p.weight)).astype(np.int8)
            for _, p in _get_plates(model)]


def holo_plate_diff(before, after):
    total_flipped = 0
    total_positions = 0
    for b, a in zip(before, after):
        diff = (b != a)
        total_flipped += int(diff.sum())
        total_positions += b.size
    return {
        "total_flipped": total_flipped,
        "total_positions": total_positions,
        "fraction": total_flipped / total_positions if total_positions > 0 else 0,
    }


# ══════════════════════════════════════════════════════════════════════
# Experiment conditions
# ══════════════════════════════════════════════════════════════════════

def _extract_plate_grad(grads, layer_idx: int, plate_name: str) -> mx.array:
    """Navigate the grad tree to find the gradient for a specific plate.

    Plate names: 'attn.k_plate', 'attn.v_plate', 'attn.o_plate', 'ffn_plate'
    """
    layer_grads = grads["layers"][layer_idx]
    parts = plate_name.split(".")
    g = layer_grads
    for part in parts:
        g = g[part]
    return g["weight"]


def etch_plates(model, rng, n_batches=200, batch_size=32, max_depth=4):
    before = holo_plate_fingerprint(model)

    # Build accumulators for each plate
    plates = _get_plates(model)
    accumulators = []
    for _, plate in plates:
        shape = (plate.out_features, plate.in_features)
        accumulators.append(np.zeros(shape, dtype=np.float64))

    # Map plate index to (layer_idx, plate_name) for gradient extraction
    plate_paths = []
    for i, layer in enumerate(model.layers):
        plate_paths.append((i, "attn.k_plate"))
        plate_paths.append((i, "attn.v_plate"))
        plate_paths.append((i, "attn.o_plate"))
        plate_paths.append((i, "ffn_plate"))

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    for b in range(n_batches):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        for pidx, (layer_idx, pname) in enumerate(plate_paths):
            g = _extract_plate_grad(grads, layer_idx, pname)
            mx.eval(g)
            accumulators[pidx] += np.sign(np.array(g))
        del loss_val, grads, input_ids, targets, mask
        if (b + 1) % 50 == 0:
            mx.clear_cache()

    total_flipped = 0
    for pidx, (_, plate) in enumerate(plates):
        acc = accumulators[pidx]
        confidence = np.abs(acc) / n_batches
        target_sign = np.sign(acc)
        current = np.sign(np.array(plate.weight)).astype(np.int8)
        should_flip = (
            (confidence > 0.6) & (target_sign != 0) & (target_sign != current)
        )
        new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
        plate.weight = mx.array(new_signs)
        mx.eval(plate.weight)
        total_flipped += int(should_flip.sum())

    after = holo_plate_fingerprint(model)
    diff = holo_plate_diff(before, after)
    return total_flipped, diff["fraction"]


def _zero_plate_grads(grads, n_layers):
    """Zero out gradients for all ternary plate weights."""
    for i in range(n_layers):
        lg = grads["layers"][i]
        # Attention plates: k_plate, v_plate, o_plate
        for pname in ["k_plate", "v_plate", "o_plate"]:
            if "attn" in lg and pname in lg["attn"]:
                lg["attn"][pname]["weight"] = mx.zeros_like(
                    lg["attn"][pname]["weight"])
        # FFN plate
        if "ffn_plate" in lg:
            lg["ffn_plate"]["weight"] = mx.zeros_like(
                lg["ffn_plate"]["weight"])


def train_beams(model, rng, n_steps=500, batch_size=32, lr=0.003,
                max_depth=4):
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    losses = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        losses.append(float(loss_val.item()))
        _zero_plate_grads(grads, len(model.layers))
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
    return losses


def run_gd(d_model, n_layers=3, n_steps=3000, batch_size=32, lr=0.003,
           max_depth=4):
    model = GDModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    from mlx.utils import tree_flatten
    n_params = sum(p.size for _, p in tree_flatten(model.parameters()))

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    log.append({"step": n_steps, **final})

    # Depth breakdown
    depth_ev = eval_by_depth(model, np.random.RandomState(999),
                             max_depth=max_depth)

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "n_params": n_params, "depth_breakdown": depth_ev, "log": log}


def run_beam_only(d_model, n_layers=3, n_steps=3000, batch_size=32,
                  lr=0.003, max_depth=4):
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    for layer in model.layers:
        layer.attn.k_plate.freeze()
        layer.attn.v_plate.freeze()
        layer.attn.o_plate.freeze()
        layer.ffn_plate.freeze()
    params = count_holo_params(model)

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(
            batch_size, rng, max_depth=max_depth)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets, mask
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0:
            ev = eval_model(model, np.random.RandomState(999),
                            max_depth=max_depth)
            log.append({"step": step + 1, **ev})

    final = eval_model(model, np.random.RandomState(999), max_depth=max_depth)
    log.append({"step": n_steps, **final})

    depth_ev = eval_by_depth(model, np.random.RandomState(999),
                             max_depth=max_depth)

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "depth_breakdown": depth_ev, "log": log}


def run_plate_only(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   batch_size=32, max_depth=4):
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        log.append({"round": r + 1, "flips": flips,
                     "flip_frac": flip_frac, **ev})
        mx.clear_cache()

    depth_ev = eval_by_depth(model, np.random.RandomState(999),
                             max_depth=max_depth)

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "depth_breakdown": depth_ev, "log": log}


def run_etch_first(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   beam_steps=500, batch_size=32, lr=0.003, max_depth=4):
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        losses = train_beams(model, rng, n_steps=beam_steps,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        log.append({
            "round": r + 1, "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    depth_ev = eval_by_depth(model, np.random.RandomState(999),
                             max_depth=max_depth)

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "depth_breakdown": depth_ev, "log": log}


def run_beam_first(d_model, n_layers=3, n_rounds=15, etch_batches=200,
                   beam_steps=500, batch_size=32, lr=0.003, max_depth=4):
    model = HoloModel(d_model=d_model, n_layers=n_layers)
    mx.eval(model.parameters())
    params = count_holo_params(model)
    rng = np.random.RandomState(42)

    log = []
    for r in range(n_rounds):
        losses = train_beams(model, rng, n_steps=beam_steps,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        flips, flip_frac = etch_plates(model, rng, n_batches=etch_batches,
                                       batch_size=batch_size,
                                       max_depth=max_depth)
        ev = eval_model(model, np.random.RandomState(999),
                        max_depth=max_depth)
        log.append({
            "round": r + 1, "flips": flips, "flip_frac": flip_frac,
            "beam_start": float(np.mean(losses[:10])),
            "beam_end": float(np.mean(losses[-10:])),
            **ev,
        })
        mx.clear_cache()

    depth_ev = eval_by_depth(model, np.random.RandomState(999),
                             max_depth=max_depth)

    return {"best_acc": max(e["accuracy"] for e in log),
            "best_loss": min(e["loss"] for e in log),
            "params": params, "depth_breakdown": depth_ev, "log": log}


# ══════════════════════════════════════════════════════════════════════
# D-sweep orchestrator
# ══════════════════════════════════════════════════════════════════════

def run_d_sweep(d_values, n_layers=3, n_rounds=15, etch_batches=200,
                beam_steps=500, gd_steps=3000, batch_size=32, lr=0.003,
                max_depth=4):

    all_results = {}

    for d in d_values:
        print(f"\n{'═' * 70}")
        print(f"  d = {d}")
        print(f"{'═' * 70}")

        test_model = HoloModel(d_model=d, n_layers=n_layers)
        mx.eval(test_model.parameters())
        params = count_holo_params(test_model)
        ratio = params["plate_positions"] / max(params["continuous"], 1)
        print(f"  Plates: {params['plate_positions']:,}  "
              f"Continuous: {params['continuous']:,}  "
              f"Ratio: {ratio:.1f}:1")
        del test_model
        mx.clear_cache()

        d_results = {
            "d_model": d, "n_layers": n_layers,
            "plate_positions": params["plate_positions"],
            "beam_params": params["beam_params"],
            "embed_params": params["embed_params"],
            "continuous_params": params["continuous"],
            "plate_beam_ratio": ratio,
        }

        # 1. GD
        print(f"\n  [1/5] GD baseline...", end="", flush=True)
        t0 = time.time()
        gd = run_gd(d, n_layers, n_steps=gd_steps, batch_size=batch_size,
                     lr=lr, max_depth=max_depth)
        dt = time.time() - t0
        print(f" acc={gd['best_acc']:.1%} ({dt:.1f}s)")
        for dep, ds in gd["depth_breakdown"].items():
            print(f"    depth {dep}: {ds['accuracy']:.1%} ({ds['total']} samples)")
        d_results["gd"] = gd

        # 2. Beam-only
        print(f"  [2/5] Beam-only...", end="", flush=True)
        t0 = time.time()
        beam = run_beam_only(d, n_layers, n_steps=gd_steps,
                             batch_size=batch_size, lr=lr,
                             max_depth=max_depth)
        dt = time.time() - t0
        print(f" acc={beam['best_acc']:.1%} ({dt:.1f}s)")
        for dep, ds in beam["depth_breakdown"].items():
            print(f"    depth {dep}: {ds['accuracy']:.1%} ({ds['total']} samples)")
        d_results["beam_only"] = beam

        # 3. Plate-only
        print(f"  [3/5] Plate-only...", end="", flush=True)
        t0 = time.time()
        plate = run_plate_only(d, n_layers, n_rounds=n_rounds,
                               etch_batches=etch_batches,
                               batch_size=batch_size, max_depth=max_depth)
        dt = time.time() - t0
        print(f" acc={plate['best_acc']:.1%} ({dt:.1f}s)")
        d_results["plate_only"] = plate

        # 4. Etch-first
        print(f"  [4/5] Etch-first...", end="", flush=True)
        t0 = time.time()
        ef = run_etch_first(d, n_layers, n_rounds=n_rounds,
                            etch_batches=etch_batches, beam_steps=beam_steps,
                            batch_size=batch_size, lr=lr,
                            max_depth=max_depth)
        dt = time.time() - t0
        print(f" acc={ef['best_acc']:.1%} ({dt:.1f}s)")
        d_results["etch_first"] = ef

        # 5. Beam-first
        print(f"  [5/5] Beam-first...", end="", flush=True)
        t0 = time.time()
        bf = run_beam_first(d, n_layers, n_rounds=n_rounds,
                            etch_batches=etch_batches, beam_steps=beam_steps,
                            batch_size=batch_size, lr=lr,
                            max_depth=max_depth)
        dt = time.time() - t0
        print(f" acc={bf['best_acc']:.1%} ({dt:.1f}s)")
        d_results["beam_first"] = bf

        # Summary
        gap = gd["best_acc"] - beam["best_acc"]
        bf_vs_ef = bf["best_acc"] - ef["best_acc"]
        print(f"\n  d={d} summary:")
        print(f"    GD:          {gd['best_acc']:.1%}")
        print(f"    Beam-only:   {beam['best_acc']:.1%}  "
              f"(gap: {gap:+.1%})")
        print(f"    Plate-only:  {plate['best_acc']:.1%}")
        print(f"    Etch-first:  {ef['best_acc']:.1%}")
        print(f"    Beam-first:  {bf['best_acc']:.1%}  "
              f"(vs etch-first: {bf_vs_ef:+.1%})")

        # Depth breakdown comparison
        print(f"\n    Depth breakdown (GD vs Beam-only):")
        for dep in sorted(gd["depth_breakdown"].keys()):
            gd_d = gd["depth_breakdown"][dep]["accuracy"]
            bm_d = beam["depth_breakdown"][dep]["accuracy"]
            dgap = gd_d - bm_d
            marker = " ← GAP" if dgap > 0.03 else ""
            print(f"      depth {dep}: GD={gd_d:.1%}  "
                  f"Beam={bm_d:.1%}  gap={dgap:+.1%}{marker}")

        flip_fracs_bf = [e["flip_frac"] for e in bf["log"]]
        flip_fracs_ef = [e["flip_frac"] for e in ef["log"]]
        print(f"\n    Flip trajectory (beam-first): "
              f"{' → '.join(f'{f:.0%}' for f in flip_fracs_bf[:6])}")
        print(f"    Flip trajectory (etch-first): "
              f"{' → '.join(f'{f:.0%}' for f in flip_fracs_ef[:6])}")

        d_results["summary"] = {
            "gd_acc": gd["best_acc"],
            "beam_only_acc": beam["best_acc"],
            "plate_only_acc": plate["best_acc"],
            "etch_first_acc": ef["best_acc"],
            "beam_first_acc": bf["best_acc"],
            "gap_gd_vs_beam": gap,
            "beam_first_vs_etch_first": bf_vs_ef,
            "gd_depth": {str(k): v for k, v in gd["depth_breakdown"].items()},
            "beam_depth": {str(k): v for k, v in beam["depth_breakdown"].items()},
            "flip_trajectory_beam_first": flip_fracs_bf,
            "flip_trajectory_etch_first": flip_fracs_ef,
        }

        all_results[str(d)] = d_results
        mx.clear_cache()

    return all_results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-d-sweep-v2")
    output_dir.mkdir(parents=True, exist_ok=True)

    d_values = [48, 96, 128, 192, 256]
    max_depth = 4

    print("=" * 70)
    print("  D-SWEEP v2: Nested Composition Chains")
    print(f"  d values: {d_values}")
    print(f"  Max reduction depth: {max_depth}")
    print(f"  Task: nested KIBC reduction (multi-step)")
    print(f"  Conditions: GD, beam-only, plate-only, etch-first, beam-first")
    print("=" * 70)

    # Show sample data
    rng = np.random.RandomState(42)
    print("\n  Sample expressions:")
    for _ in range(8):
        result = generate_example(rng, max_depth=max_depth)
        if result:
            inp, out, depth = result
            print(f"    depth={depth}: {' '.join(inp[1:-1])} = "
                  f"{' '.join(out[:-1])}")

    t_start = time.time()
    results = run_d_sweep(d_values, max_depth=max_depth)
    t_total = time.time() - t_start

    # ── Grand summary ─────────────────────────────────────────
    print(f"\n{'═' * 70}")
    print(f"  GRAND SUMMARY — D-Sweep v2 (Nested Composition)")
    print(f"{'═' * 70}")
    print(f"  {'d':>5}  {'Ratio':>6}  {'GD':>7}  {'Beam':>7}  "
          f"{'Gap':>7}  {'Plate':>7}  {'EtchF':>7}  {'BeamF':>7}  "
          f"{'BF-EF':>7}")
    print(f"  {'─'*5}  {'─'*6}  {'─'*7}  {'─'*7}  {'─'*7}  "
          f"{'─'*7}  {'─'*7}  {'─'*7}  {'─'*7}")

    for d in d_values:
        s = results[str(d)]["summary"]
        r = results[str(d)]["plate_beam_ratio"]
        marker = ""
        if s["gap_gd_vs_beam"] > 0.02:
            marker = " ← CROSSOVER"
        print(f"  {d:>5}  {r:>5.1f}×  {s['gd_acc']:>6.1%}  "
              f"{s['beam_only_acc']:>6.1%}  {s['gap_gd_vs_beam']:>+6.1%}  "
              f"{s['plate_only_acc']:>6.1%}  {s['etch_first_acc']:>6.1%}  "
              f"{s['beam_first_acc']:>6.1%}  "
              f"{s['beam_first_vs_etch_first']:>+6.1%}{marker}")

    # Depth breakdown summary
    print(f"\n  Depth breakdown (GD vs Beam-only):")
    print(f"  {'d':>5}  ", end="")
    for dep in range(1, max_depth + 1):
        print(f"{'d' + str(dep) + ' GD':>8}  {'d' + str(dep) + ' Beam':>9}  "
              f"{'gap':>6}  ", end="")
    print()
    for d in d_values:
        s = results[str(d)]["summary"]
        print(f"  {d:>5}  ", end="")
        for dep in range(1, max_depth + 1):
            gd_a = s["gd_depth"].get(str(dep), {}).get("accuracy", 0)
            bm_a = s["beam_depth"].get(str(dep), {}).get("accuracy", 0)
            gap = gd_a - bm_a
            print(f"{gd_a:>7.1%}  {bm_a:>8.1%}  {gap:>+5.1%}  ", end="")
        print()

    print(f"\n  Total time: {t_total:.0f}s ({t_total/60:.1f}m)")

    # Save
    summary_results = {}
    for d_key, d_data in results.items():
        summary_results[d_key] = {
            "d_model": d_data["d_model"],
            "plate_positions": d_data["plate_positions"],
            "beam_params": d_data["beam_params"],
            "embed_params": d_data["embed_params"],
            "continuous_params": d_data["continuous_params"],
            "plate_beam_ratio": d_data["plate_beam_ratio"],
            "summary": d_data["summary"],
        }

    with open(output_dir / "summary.json", "w") as f:
        json.dump(summary_results, f, indent=2)

    with open(output_dir / "full_results.json", "w") as f:
        json.dump(results, f, indent=2)

    print(f"\n  Summary: {output_dir}/summary.json")
    print(f"  Full:    {output_dir}/full_results.json")


if __name__ == "__main__":
    main()
