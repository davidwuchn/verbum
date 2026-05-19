"""Mini Holographic Microscope — understanding plate/beam mechanics.

A tiny model with the same holographic architecture as VSM-LM:
ternary plates (topology) + continuous beams (angles). Small enough
to visualize every parameter and track every flip.

Task: combinator reduction (K, I, B, C).
  K a b = a          (select first)
  I x = x            (identity)
  B f g x = f (g x)  (composition)
  C f a b = f b a     (flip)

The model predicts each next token. We know every correct answer.
By separating plate etching from beam training, we can see exactly
how each mechanism encodes information — like reading a laserdisc.

Usage:
    # Train and analyze
    uv run python scripts/v12/mini_holo.py

    # Just analyze a checkpoint
    uv run python scripts/v12/mini_holo.py --analyze checkpoints/mini-holo/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

# ══════════════════════════════════════════════════════════════════════
# Tokenizer — tiny vocabulary for combinator logic
# ══════════════════════════════════════════════════════════════════════

TOKENS = [
    "<pad>", "<bos>", "<eos>", "=",
    "K", "I", "B", "C",                    # combinators
    "a", "b", "c", "d",                    # variables
    "f", "g",                              # function variables
    "x", "y",                              # argument variables
    "(", ")",                              # grouping
]
TOK2ID = {t: i for i, t in enumerate(TOKENS)}
ID2TOK = {i: t for t, i in TOK2ID.items()}
VOCAB_SIZE = len(TOKENS)
PAD_ID = TOK2ID["<pad>"]
BOS_ID = TOK2ID["<bos>"]
EOS_ID = TOK2ID["<eos>"]
EQ_ID = TOK2ID["="]


def tokenize(tokens: list[str]) -> list[int]:
    return [TOK2ID[t] for t in tokens]


def detokenize(ids: list[int]) -> list[str]:
    return [ID2TOK.get(i, "?") for i in ids]


# ══════════════════════════════════════════════════════════════════════
# Data generator — combinator reductions with known answers
# ══════════════════════════════════════════════════════════════════════

VARS = ["a", "b", "c", "d", "x", "y"]
FVARS = ["f", "g"]


def generate_reduction(rng: np.random.RandomState) -> tuple[list[str], list[str]]:
    """Generate one combinator reduction example.

    Returns (input_tokens, output_tokens) where:
      input  = [<bos>, op, args..., =]
      output = [result..., <eos>]

    Full sequence for training: input + output (next-token prediction).
    """
    op = rng.choice(["K", "I", "B", "C"])
    v = lambda: rng.choice(VARS)
    fv = lambda: rng.choice(FVARS)

    if op == "K":
        # K x y = x
        x, y = v(), v()
        inp = ["<bos>", "K", x, y, "="]
        out = [x, "<eos>"]

    elif op == "I":
        # I x = x
        x = v()
        inp = ["<bos>", "I", x, "="]
        out = [x, "<eos>"]

    elif op == "B":
        # B f g x = f ( g x )
        f, g, x = fv(), fv(), v()
        inp = ["<bos>", "B", f, g, x, "="]
        out = [f, "(", g, x, ")", "<eos>"]

    elif op == "C":
        # C f x y = f y x
        f = fv()
        x, y = v(), v()
        inp = ["<bos>", "C", f, x, y, "="]
        out = [f, y, x, "<eos>"]

    return inp, out


def generate_batch(
    batch_size: int,
    rng: np.random.RandomState,
    max_len: int = 16,
) -> tuple[mx.array, mx.array, mx.array]:
    """Generate a batch of (input_ids, targets, loss_mask).

    loss_mask is 1 for output tokens (after =), 0 for input tokens.
    We only compute loss on the part after = (the reduction result).
    """
    all_ids = []
    all_targets = []
    all_masks = []

    for _ in range(batch_size):
        inp, out = generate_reduction(rng)
        seq = inp + out
        ids = tokenize(seq)

        # Pad to max_len
        n = len(ids)
        if n > max_len:
            ids = ids[:max_len]
            n = max_len
        ids = ids + [PAD_ID] * (max_len - n)

        # Targets: shifted by 1
        target = ids[1:] + [PAD_ID]

        # Loss mask: 1 after the = token, 0 before and on padding
        mask = [0] * max_len
        eq_pos = None
        for i, tok_id in enumerate(ids):
            if tok_id == EQ_ID:
                eq_pos = i
            elif eq_pos is not None and tok_id != PAD_ID:
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
# TernaryLinear — ternary plates (the holographic surface)
# ══════════════════════════════════════════════════════════════════════

class TernaryLinear(nn.Module):
    """Linear layer with ternary weights {-1, 0, +1}.

    The weight matrix is stored as float but constrained to {-1, 0, +1}.
    These are the "plates" — fixed topology that reflects the beam.
    """

    def __init__(self, in_features: int, out_features: int):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        # Initialize randomly as ternary
        w = np.random.choice([-1.0, 0.0, 1.0],
                             size=(out_features, in_features),
                             p=[0.3, 0.4, 0.3])
        self.weight = mx.array(w.astype(np.float32))

    def __call__(self, x: mx.array) -> mx.array:
        return x @ self.weight.T

    @property
    def signs(self) -> np.ndarray:
        """Current ternary signs as numpy array."""
        return np.sign(np.array(self.weight)).astype(np.int8)

    @signs.setter
    def signs(self, new_signs: np.ndarray):
        self.weight = mx.array(new_signs.astype(np.float32))
        mx.eval(self.weight)


# ══════════════════════════════════════════════════════════════════════
# BeamParams — continuous parameters (the reference beam angles)
# ══════════════════════════════════════════════════════════════════════

class BeamLayer(nn.Module):
    """One plate + beam unit: TernaryLinear (plate) + scale/bias (beam).

    The plate defines WHAT patterns exist (topology).
    The beam defines HOW to read the plate (angles, gain).

    plate_out = TernaryLinear(x)           # topology
    beam_out  = plate_out * scale + bias   # angle + gain
    output    = x + beam_out               # residual
    """

    def __init__(self, d_model: int):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)
        # Beam params: per-feature scale and bias
        self.beam_scale = mx.ones((d_model,))
        self.beam_bias = mx.zeros((d_model,))

    def __call__(self, x: mx.array) -> mx.array:
        plate_out = self.plate(self.norm(x))
        beam_out = plate_out * self.beam_scale + self.beam_bias
        return x + beam_out


# ══════════════════════════════════════════════════════════════════════
# MiniHoloModel — the microscope
# ══════════════════════════════════════════════════════════════════════

class MiniHoloModel(nn.Module):
    """Tiny holographic model for plate/beam mechanics research.

    Architecture:
        embed → beam_layer_0 → beam_layer_1 → beam_layer_2 → output

    Ternary plates: 3 × d_model² positions (~7K at d=48)
    Continuous beams: 3 × 2 × d_model params (~288 at d=48)
    Embeddings: vocab × d_model + d_model × vocab (~1.7K at d=48, v=18)

    Small enough to visualize everything. Same mechanics as VSM-LM.
    """

    def __init__(self, d_model: int = 48, n_layers: int = 3):
        super().__init__()
        self.d_model = d_model
        self.n_layers = n_layers

        self.embed = nn.Embedding(VOCAB_SIZE, d_model)
        self.layers = [BeamLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, VOCAB_SIZE)

    def __call__(self, input_ids: mx.array) -> mx.array:
        """Forward pass. Returns logits (B, T, V)."""
        x = self.embed(input_ids)  # (B, T, d)
        for layer in self.layers:
            x = layer(x)
        x = self.output_norm(x)
        logits = self.output_proj(x)  # (B, T, V)
        return logits

    def get_hidden_states(self, input_ids: mx.array) -> list[mx.array]:
        """Forward pass returning hidden state at each layer."""
        states = []
        x = self.embed(input_ids)
        states.append(x)
        for layer in self.layers:
            x = layer(x)
            states.append(x)
        return states


# ══════════════════════════════════════════════════════════════════════
# Loss function
# ══════════════════════════════════════════════════════════════════════

def masked_ce_loss(
    model: MiniHoloModel,
    input_ids: mx.array,
    targets: mx.array,
    mask: mx.array,
) -> mx.array:
    """Cross-entropy loss on output tokens only (after =)."""
    logits = model(input_ids)  # (B, T, V)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V),
        targets.reshape(-1),
    ).reshape(B, T)
    # Mask: only compute loss on result tokens
    masked_loss = (ce * mask).sum() / (mask.sum() + 1e-8)
    return masked_loss


# ══════════════════════════════════════════════════════════════════════
# Plate analysis tools
# ══════════════════════════════════════════════════════════════════════

def count_plate_params(model: MiniHoloModel) -> dict:
    """Count ternary plate positions and continuous beam params."""
    plate_positions = 0
    beam_params = 0
    embed_params = 0

    for i, layer in enumerate(model.layers):
        p = layer.plate.in_features * layer.plate.out_features
        plate_positions += p
        beam_params += layer.beam_scale.size + layer.beam_bias.size
        beam_params += sum(x.size for x in layer.norm.parameters().values())

    embed_params += model.embed.weight.size
    embed_params += sum(x.size for x in model.output_norm.parameters().values())
    embed_params += sum(x.size for x in model.output_proj.parameters().values())

    return {
        "plate_positions": plate_positions,
        "beam_params": beam_params,
        "embed_params": embed_params,
        "total": plate_positions + beam_params + embed_params,
    }


def plate_fingerprint(model: MiniHoloModel) -> list[np.ndarray]:
    """Get current ternary signs of all plates."""
    return [layer.plate.signs for layer in model.layers]


def plate_diff(before: list[np.ndarray], after: list[np.ndarray]) -> dict:
    """Compare two plate states. How many flipped? Where?"""
    total_flipped = 0
    total_positions = 0
    per_layer = []

    for i, (b, a) in enumerate(zip(before, after)):
        diff = (b != a)
        n_flipped = int(diff.sum())
        n_total = b.size
        total_flipped += n_flipped
        total_positions += n_total
        per_layer.append({
            "layer": i,
            "flipped": n_flipped,
            "total": n_total,
            "fraction": n_flipped / n_total if n_total > 0 else 0,
        })

    return {
        "total_flipped": total_flipped,
        "total_positions": total_positions,
        "fraction": total_flipped / total_positions if total_positions > 0 else 0,
        "per_layer": per_layer,
    }


def measure_geometry(model: MiniHoloModel, probes: list[list[int]]) -> np.ndarray:
    """Forward probes and compute RDM (cosine similarity matrix).

    Returns (n_probes, n_probes) cosine similarity matrix.
    """
    states = []
    for probe in probes:
        tokens = mx.array([probe])
        logits = model(tokens)
        # Use last token's hidden state before output projection
        x = model.embed(tokens)
        for layer in model.layers:
            x = layer(x)
        h = np.array(x[0, -1, :])  # last token
        states.append(h)

    states = np.stack(states)
    norms = np.linalg.norm(states, axis=1, keepdims=True)
    normed = states / (norms + 1e-8)
    return normed @ normed.T


# ══════════════════════════════════════════════════════════════════════
# Etch protocol — separate plate and beam training
# ══════════════════════════════════════════════════════════════════════

def etch_plates(
    model: MiniHoloModel,
    rng: np.random.RandomState,
    n_batches: int = 100,
    batch_size: int = 32,
) -> dict:
    """Accumulate gradient directions across batches, then flip plates.

    This is the holographic recording: expose the plate to many
    reference beams (examples), accumulate the interference pattern,
    then develop (flip confident positions).

    Returns stats about what was flipped.
    """
    before = plate_fingerprint(model)

    # Accumulate gradient signs across batches
    accumulators = {}
    for i, layer in enumerate(model.layers):
        shape = (layer.plate.out_features, layer.plate.in_features)
        accumulators[i] = np.zeros(shape, dtype=np.float64)

    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)
    losses = []

    for _ in range(n_batches):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        losses.append(float(loss_val.item()))

        # Extract plate gradients and accumulate signs
        for i, layer in enumerate(model.layers):
            g = grads["layers"][i]["plate"]["weight"]
            mx.eval(g)
            accumulators[i] += np.sign(np.array(g))

        del loss_val, grads

    # Majority vote: flip where accumulated direction is confident
    for i, layer in enumerate(model.layers):
        acc = accumulators[i]
        confidence = np.abs(acc) / n_batches
        target_sign = np.sign(acc)

        current = layer.plate.signs
        # Flip where confidence > 0.6 and target disagrees
        should_flip = (confidence > 0.6) & (target_sign != 0) & (target_sign != current)
        new_signs = np.where(should_flip, target_sign, current).astype(np.float32)
        layer.plate.weight = mx.array(new_signs)
        mx.eval(layer.plate.weight)

    after = plate_fingerprint(model)
    diff = plate_diff(before, after)
    diff["mean_loss"] = float(np.mean(losses))

    return diff


def train_beams(
    model: MiniHoloModel,
    rng: np.random.RandomState,
    n_steps: int = 100,
    batch_size: int = 32,
    lr: float = 0.001,
) -> dict:
    """Train only the continuous beam parameters (scale, bias, embeds).

    Plates are frozen. Only beam angles change.
    """
    # Freeze plates
    for layer in model.layers:
        layer.plate.weight = mx.stop_gradient(layer.plate.weight)

    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, masked_ce_loss)

    losses = []
    for step in range(n_steps):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        loss_val, grads = loss_and_grad(model, input_ids, targets, mask)
        mx.eval(loss_val, grads)
        losses.append(float(loss_val.item()))

        # Zero out plate gradients (freeze plates)
        for i in range(len(model.layers)):
            if "plate" in grads["layers"][i]:
                grads["layers"][i]["plate"]["weight"] = mx.zeros_like(
                    grads["layers"][i]["plate"]["weight"])

        optimizer.apply_gradients(grads, model)
        mx.eval(model.parameters())

        del loss_val, grads

    return {
        "start_loss": float(np.mean(losses[:10])) if len(losses) >= 10 else losses[0],
        "end_loss": float(np.mean(losses[-10:])) if len(losses) >= 10 else losses[-1],
        "mean_loss": float(np.mean(losses)),
        "n_steps": n_steps,
    }


# ══════════════════════════════════════════════════════════════════════
# Evaluation
# ══════════════════════════════════════════════════════════════════════

def evaluate(
    model: MiniHoloModel,
    rng: np.random.RandomState,
    n_batches: int = 50,
    batch_size: int = 64,
) -> dict:
    """Evaluate model accuracy on combinator reductions."""
    total_correct = 0
    total_tokens = 0
    total_loss = 0.0

    for _ in range(n_batches):
        input_ids, targets, mask = generate_batch(batch_size, rng)
        logits = model(input_ids)
        mx.eval(logits)

        # Loss
        B, T, V = logits.shape
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1)
        ).reshape(B, T)
        masked_loss = (ce * mask).sum() / (mask.sum() + 1e-8)
        mx.eval(masked_loss)
        total_loss += float(masked_loss.item())

        # Accuracy on masked positions
        preds = mx.argmax(logits, axis=-1)  # (B, T)
        correct = (preds == targets).astype(mx.float32) * mask
        mx.eval(correct)
        total_correct += float(correct.sum().item())
        total_tokens += float(mask.sum().item())

    return {
        "loss": total_loss / n_batches,
        "accuracy": total_correct / max(total_tokens, 1),
        "n_tokens": int(total_tokens),
    }


# ══════════════════════════════════════════════════════════════════════
# Plate sensitivity analysis — the microscope
# ══════════════════════════════════════════════════════════════════════

def analyze_plate_sensitivity(
    model: MiniHoloModel,
    rng: np.random.RandomState,
    n_flips: int = 50,
) -> dict:
    """Flip random plate positions one at a time and measure impact.

    For each flip:
      1. Save current state
      2. Flip one position
      3. Measure loss change
      4. Restore

    This shows which plate positions are "load-bearing" vs redundant.
    """
    eval_rng = np.random.RandomState(999)
    input_ids, targets, mask = generate_batch(64, eval_rng)

    # Baseline loss
    baseline_logits = model(input_ids)
    B, T, V = baseline_logits.shape
    baseline_ce = nn.losses.cross_entropy(
        baseline_logits.reshape(-1, V), targets.reshape(-1)
    ).reshape(B, T)
    baseline_loss = float(((baseline_ce * mask).sum() / (mask.sum() + 1e-8)).item())

    sensitivities = []

    for _ in range(n_flips):
        # Pick random layer and position
        layer_idx = rng.randint(len(model.layers))
        layer = model.layers[layer_idx]
        r = rng.randint(layer.plate.out_features)
        c = rng.randint(layer.plate.in_features)

        # Current sign
        current = float(layer.plate.weight[r, c].item())
        # Flip: -1→+1, +1→-1, 0→random±1
        if current == 0:
            new_val = rng.choice([-1.0, 1.0])
        else:
            new_val = -current

        # Apply flip
        w = np.array(layer.plate.weight)
        w[r, c] = new_val
        layer.plate.weight = mx.array(w)
        mx.eval(layer.plate.weight)

        # Measure
        logits = model(input_ids)
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1)
        ).reshape(B, T)
        new_loss = float(((ce * mask).sum() / (mask.sum() + 1e-8)).item())

        delta = new_loss - baseline_loss

        sensitivities.append({
            "layer": layer_idx,
            "row": r,
            "col": c,
            "old_sign": current,
            "new_sign": new_val,
            "loss_delta": delta,
        })

        # Restore
        w[r, c] = current
        layer.plate.weight = mx.array(w)
        mx.eval(layer.plate.weight)

    # Summary
    deltas = [s["loss_delta"] for s in sensitivities]
    per_layer = {}
    for s in sensitivities:
        li = s["layer"]
        if li not in per_layer:
            per_layer[li] = []
        per_layer[li].append(abs(s["loss_delta"]))

    return {
        "baseline_loss": baseline_loss,
        "mean_abs_delta": float(np.mean(np.abs(deltas))),
        "max_abs_delta": float(np.max(np.abs(deltas))),
        "std_delta": float(np.std(deltas)),
        "per_layer_mean": {k: float(np.mean(v)) for k, v in per_layer.items()},
        "details": sensitivities,
    }


def analyze_beam_sensitivity(
    model: MiniHoloModel,
    rng: np.random.RandomState,
    epsilon: float = 0.01,
    n_params: int = 50,
) -> dict:
    """Perturb random beam parameters and measure impact.

    Same idea as plate sensitivity but for continuous params.
    Shows how much the beam angles control the output.
    """
    eval_rng = np.random.RandomState(999)
    input_ids, targets, mask = generate_batch(64, eval_rng)

    baseline_logits = model(input_ids)
    B, T, V = baseline_logits.shape
    baseline_ce = nn.losses.cross_entropy(
        baseline_logits.reshape(-1, V), targets.reshape(-1)
    ).reshape(B, T)
    baseline_loss = float(((baseline_ce * mask).sum() / (mask.sum() + 1e-8)).item())

    sensitivities = []

    for _ in range(n_params):
        layer_idx = rng.randint(len(model.layers))
        layer = model.layers[layer_idx]
        param_type = rng.choice(["scale", "bias"])

        if param_type == "scale":
            param = layer.beam_scale
        else:
            param = layer.beam_bias

        idx = rng.randint(param.size)
        old_val = float(param[idx].item())

        # Perturb
        arr = np.array(param)
        arr[idx] += epsilon
        if param_type == "scale":
            layer.beam_scale = mx.array(arr)
            mx.eval(layer.beam_scale)
        else:
            layer.beam_bias = mx.array(arr)
            mx.eval(layer.beam_bias)

        # Measure
        logits = model(input_ids)
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1)
        ).reshape(B, T)
        new_loss = float(((ce * mask).sum() / (mask.sum() + 1e-8)).item())
        delta = new_loss - baseline_loss

        sensitivities.append({
            "layer": layer_idx,
            "param": param_type,
            "idx": idx,
            "loss_delta": delta,
            "loss_delta_per_eps": delta / epsilon,
        })

        # Restore
        arr[idx] = old_val
        if param_type == "scale":
            layer.beam_scale = mx.array(arr)
            mx.eval(layer.beam_scale)
        else:
            layer.beam_bias = mx.array(arr)
            mx.eval(layer.beam_bias)

    deltas = [s["loss_delta"] for s in sensitivities]
    return {
        "baseline_loss": baseline_loss,
        "mean_abs_delta": float(np.mean(np.abs(deltas))),
        "max_abs_delta": float(np.max(np.abs(deltas))),
        "epsilon": epsilon,
        "details": sensitivities,
    }


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Mini Holographic Microscope")
    parser.add_argument("--d-model", type=int, default=48)
    parser.add_argument("--n-layers", type=int, default=3)
    parser.add_argument("--n-rounds", type=int, default=20,
                        help="Number of etch+beam rounds")
    parser.add_argument("--etch-batches", type=int, default=100,
                        help="Batches for plate accumulation per round")
    parser.add_argument("--beam-steps", type=int, default=200,
                        help="GD steps for beam training per round")
    parser.add_argument("--beam-lr", type=float, default=0.001)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--output", type=str, default="checkpoints/mini-holo")
    parser.add_argument("--analyze", type=str, default=None,
                        help="Just analyze an existing checkpoint")
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    rng = np.random.RandomState(args.seed)

    print("=" * 60, file=sys.stderr)
    print("  Mini Holographic Microscope", file=sys.stderr)
    print(f"  d_model={args.d_model}, n_layers={args.n_layers}", file=sys.stderr)
    print(f"  vocab={VOCAB_SIZE}, task=combinator reduction", file=sys.stderr)
    print("=" * 60, file=sys.stderr)

    # ── Create model ──────────────────────────────────────────
    model = MiniHoloModel(d_model=args.d_model, n_layers=args.n_layers)
    mx.eval(model.parameters())

    params = count_plate_params(model)
    print(f"\n  Plates:  {params['plate_positions']:,} ternary positions",
          file=sys.stderr)
    print(f"  Beams:   {params['beam_params']:,} continuous params",
          file=sys.stderr)
    print(f"  Embeds:  {params['embed_params']:,} continuous params",
          file=sys.stderr)
    print(f"  Total:   {params['total']:,}", file=sys.stderr)

    # ── Geometry probes (fixed set for tracking) ──────────────
    probe_exprs = [
        ["<bos>", "K", "a", "b", "="],
        ["<bos>", "K", "x", "y", "="],
        ["<bos>", "I", "a", "="],
        ["<bos>", "I", "x", "="],
        ["<bos>", "B", "f", "g", "x", "="],
        ["<bos>", "B", "f", "g", "a", "="],
        ["<bos>", "C", "f", "a", "b", "="],
        ["<bos>", "C", "g", "x", "y", "="],
    ]
    probe_tokens = [tokenize(p) for p in probe_exprs]

    # ── Initial evaluation ────────────────────────────────────
    eval_rng = np.random.RandomState(999)
    init_eval = evaluate(model, eval_rng)
    print(f"\n  Initial: loss={init_eval['loss']:.4f} "
          f"acc={init_eval['accuracy']:.1%}", file=sys.stderr)

    # ── Training loop: alternate etch + beam ──────────────────
    log = []
    for round_idx in range(args.n_rounds):
        t0 = time.time()

        # Phase 1: Etch plates (accumulate + flip)
        etch_stats = etch_plates(
            model, rng,
            n_batches=args.etch_batches,
            batch_size=args.batch_size,
        )

        # Phase 2: Train beams (GD on continuous params)
        beam_stats = train_beams(
            model, rng,
            n_steps=args.beam_steps,
            batch_size=args.batch_size,
            lr=args.beam_lr,
        )

        # Evaluate
        eval_stats = evaluate(model, np.random.RandomState(999))

        # Geometry
        rdm = measure_geometry(model, probe_tokens)
        rdm_mean = float(np.mean(rdm[np.triu_indices(len(probe_tokens), k=1)]))

        dt = time.time() - t0

        round_log = {
            "round": round_idx + 1,
            "etch_flips": etch_stats["total_flipped"],
            "etch_fraction": etch_stats["fraction"],
            "etch_loss": etch_stats["mean_loss"],
            "beam_start_loss": beam_stats["start_loss"],
            "beam_end_loss": beam_stats["end_loss"],
            "eval_loss": eval_stats["loss"],
            "eval_accuracy": eval_stats["accuracy"],
            "rdm_mean_cosine": rdm_mean,
            "elapsed": dt,
        }
        log.append(round_log)

        # Print
        print(
            f"  Round {round_idx+1:3d} | "
            f"etch={etch_stats['total_flipped']:5d} ({etch_stats['fraction']:.1%}) | "
            f"beam {beam_stats['start_loss']:.3f}→{beam_stats['end_loss']:.3f} | "
            f"eval loss={eval_stats['loss']:.3f} acc={eval_stats['accuracy']:.1%} | "
            f"cos={rdm_mean:.3f} | {dt:.1f}s",
            file=sys.stderr,
        )

        # Per-layer etch detail
        for pl in etch_stats["per_layer"]:
            print(
                f"         L{pl['layer']}: {pl['flipped']:4d}/{pl['total']} "
                f"({pl['fraction']:.1%})",
                file=sys.stderr,
            )

    # ── Final analysis ────────────────────────────────────────
    print(f"\n{'─' * 60}", file=sys.stderr)
    print("  Plate sensitivity analysis...", file=sys.stderr)
    plate_sens = analyze_plate_sensitivity(model, rng, n_flips=100)
    print(f"  Mean |delta|: {plate_sens['mean_abs_delta']:.6f}", file=sys.stderr)
    print(f"  Max  |delta|: {plate_sens['max_abs_delta']:.6f}", file=sys.stderr)
    for li, mean_d in plate_sens["per_layer_mean"].items():
        print(f"    Layer {li}: {mean_d:.6f}", file=sys.stderr)

    print(f"\n  Beam sensitivity analysis...", file=sys.stderr)
    beam_sens = analyze_beam_sensitivity(model, rng, n_params=100)
    print(f"  Mean |delta|: {beam_sens['mean_abs_delta']:.6f}", file=sys.stderr)
    print(f"  Max  |delta|: {beam_sens['max_abs_delta']:.6f}", file=sys.stderr)

    # ── Save ──────────────────────────────────────────────────
    # Save log
    with open(output_dir / "training_log.json", "w") as f:
        json.dump(log, f, indent=2)

    # Save model
    from mlx.utils import tree_flatten
    flat = dict(tree_flatten(model.parameters()))
    mx.savez(str(output_dir / "weights.npz"), **flat)

    # Save analysis
    analysis = {
        "params": params,
        "plate_sensitivity": {k: v for k, v in plate_sens.items()
                              if k != "details"},
        "beam_sensitivity": {k: v for k, v in beam_sens.items()
                             if k != "details"},
        "final_eval": eval_stats,
        "final_rdm": rdm.tolist(),
    }
    with open(output_dir / "analysis.json", "w") as f:
        json.dump(analysis, f, indent=2)

    print(f"\n  Saved to {output_dir}/", file=sys.stderr)
    print("=" * 60, file=sys.stderr)


if __name__ == "__main__":
    main()
