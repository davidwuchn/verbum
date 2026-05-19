"""Experiment 2: Next-token prediction on KIBC lambda expressions.

The real test: can the tiny holographic model learn the STRUCTURE
of lambda calculus? Not memorizing 4 reduction rules but predicting
next tokens in lambda expressions — requiring scope, binding, and
application understanding.

Reuses the four-way decomposition (GD, beam-only, plate-only, alternating)
on a task that should push beyond the embedding ceiling.

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

from mini_holo import TernaryLinear, plate_fingerprint, plate_diff


# ══════════════════════════════════════════════════════════════════════
# Lambda expression tokenizer (character-level, small vocab)
# ══════════════════════════════════════════════════════════════════════

LAMBDA_TOKENS = [
    "<pad>", "<bos>", "<eos>",
    "λ", ".", "(", ")", " ",
    "K", "I", "B", "C",         # combinators
    "a", "b", "c", "d", "e",    # variables
    "f", "g", "h",              # function vars
    "x", "y", "z",              # more vars
    "0", "1", "2",              # for de Bruijn indices
]
L_TOK2ID = {t: i for i, t in enumerate(LAMBDA_TOKENS)}
L_ID2TOK = {i: t for t, i in L_TOK2ID.items()}
L_VOCAB = len(LAMBDA_TOKENS)
L_PAD = L_TOK2ID["<pad>"]
L_BOS = L_TOK2ID["<bos>"]
L_EOS = L_TOK2ID["<eos>"]


def l_tokenize(s: str) -> list[int]:
    """Tokenize a lambda expression character by character."""
    ids = [L_BOS]
    for ch in s:
        if ch in L_TOK2ID:
            ids.append(L_TOK2ID[ch])
        # skip unknown chars
    ids.append(L_EOS)
    return ids


# ══════════════════════════════════════════════════════════════════════
# Lambda expression generator
# ══════════════════════════════════════════════════════════════════════

VARS = list("abcdexyz")
FVARS = list("fgh")
COMBINATORS = {
    "K": "λx.λy.x",
    "I": "λx.x",
    "B": "λf.λg.λx.f (g x)",
    "C": "λf.λx.λy.f y x",
}


def gen_lambda_expr(rng: np.random.RandomState, depth: int = 0) -> str:
    """Generate a random KIBC lambda expression."""
    if depth > 3:
        return rng.choice(VARS)

    choice = rng.random()

    if choice < 0.15:
        # Raw combinator definition
        c = rng.choice(list(COMBINATORS.keys()))
        return COMBINATORS[c]

    elif choice < 0.35:
        # Combinator applied to args
        c = rng.choice(list(COMBINATORS.keys()))
        if c == "K":
            a, b = rng.choice(VARS, 2, replace=True)
            return f"K {a} {b}"
        elif c == "I":
            a = rng.choice(VARS)
            return f"I {a}"
        elif c == "B":
            f = rng.choice(FVARS)
            g = rng.choice(FVARS)
            x = rng.choice(VARS)
            return f"B {f} {g} {x}"
        elif c == "C":
            f = rng.choice(FVARS)
            x, y = rng.choice(VARS, 2, replace=True)
            return f"C {f} {x} {y}"

    elif choice < 0.55:
        # Lambda abstraction
        v = rng.choice(VARS)
        body = gen_lambda_expr(rng, depth + 1)
        return f"λ{v}.{body}"

    elif choice < 0.75:
        # Application
        f = gen_lambda_expr(rng, depth + 1)
        x = gen_lambda_expr(rng, depth + 1)
        if len(f) > 1 and not f.startswith("("):
            f = f"({f})"
        return f"{f} {x}"

    elif choice < 0.90:
        # Nested combinator application
        c1 = rng.choice(list(COMBINATORS.keys()))
        c2 = rng.choice(list(COMBINATORS.keys()))
        v = rng.choice(VARS)
        return f"{c1} ({c2} {v})"

    else:
        # Variable
        return rng.choice(VARS)


def generate_lambda_batch(
    batch_size: int,
    rng: np.random.RandomState,
    seq_len: int = 48,
) -> tuple[mx.array, mx.array]:
    """Generate batch of lambda expressions for next-token prediction.

    Returns (input_ids, targets) — predict EVERY token (no mask needed).
    """
    all_ids = []
    all_targets = []

    for _ in range(batch_size):
        # Pack multiple expressions into one sequence
        seq_tokens = [L_BOS]
        while len(seq_tokens) < seq_len - 1:
            expr = gen_lambda_expr(rng)
            expr_ids = [L_TOK2ID[c] for c in expr if c in L_TOK2ID]
            # Add space separator
            if len(seq_tokens) > 1:
                seq_tokens.append(L_TOK2ID[" "])
            seq_tokens.extend(expr_ids)

        seq_tokens = seq_tokens[:seq_len]
        # Pad
        while len(seq_tokens) < seq_len:
            seq_tokens.append(L_PAD)

        target = seq_tokens[1:] + [L_PAD]
        all_ids.append(seq_tokens)
        all_targets.append(target)

    return (
        mx.array(np.array(all_ids, dtype=np.int32)),
        mx.array(np.array(all_targets, dtype=np.int32)),
    )


# ══════════════════════════════════════════════════════════════════════
# Models (reuse plate/beam architecture)
# ══════════════════════════════════════════════════════════════════════

class BeamLayer(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.plate = TernaryLinear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)
        self.beam_scale = mx.ones((d_model,))
        self.beam_bias = mx.zeros((d_model,))

    def __call__(self, x):
        return x + self.plate(self.norm(x)) * self.beam_scale + self.beam_bias


class GDLayer(nn.Module):
    def __init__(self, d_model):
        super().__init__()
        self.linear = nn.Linear(d_model, d_model)
        self.norm = nn.LayerNorm(d_model)

    def __call__(self, x):
        return x + self.linear(self.norm(x))


class LambdaModel(nn.Module):
    def __init__(self, d_model=48, n_layers=3, use_ternary=True):
        super().__init__()
        self.d_model = d_model
        self.use_ternary = use_ternary
        self.embed = nn.Embedding(L_VOCAB, d_model)
        if use_ternary:
            self.layers = [BeamLayer(d_model) for _ in range(n_layers)]
        else:
            self.layers = [GDLayer(d_model) for _ in range(n_layers)]
        self.output_norm = nn.LayerNorm(d_model)
        self.output_proj = nn.Linear(d_model, L_VOCAB)

    def __call__(self, input_ids):
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        return self.output_proj(self.output_norm(x))


# ══════════════════════════════════════════════════════════════════════
# Loss and evaluation
# ══════════════════════════════════════════════════════════════════════

def ntp_loss(model, input_ids, targets):
    """Next-token prediction loss on every position (skip padding)."""
    logits = model(input_ids)
    B, T, V = logits.shape
    ce = nn.losses.cross_entropy(
        logits.reshape(-1, V), targets.reshape(-1),
    ).reshape(B, T)
    # Mask out padding targets
    mask = (targets != L_PAD).astype(mx.float32)
    return (ce * mask).sum() / (mask.sum() + 1e-8)


def ntp_evaluate(model, rng, n_batches=50, batch_size=64, seq_len=48):
    total_correct = 0
    total_tokens = 0
    total_loss = 0.0
    for _ in range(n_batches):
        input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
        logits = model(input_ids)
        mx.eval(logits)
        B, T, V = logits.shape
        ce = nn.losses.cross_entropy(
            logits.reshape(-1, V), targets.reshape(-1),
        ).reshape(B, T)
        mask = (targets != L_PAD).astype(mx.float32)
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


# ══════════════════════════════════════════════════════════════════════
# Experiment runners
# ══════════════════════════════════════════════════════════════════════

def run_gd_baseline(n_steps=3000, batch_size=32, lr=0.003, seq_len=48):
    model = LambdaModel(d_model=48, n_layers=3, use_ternary=False)
    mx.eval(model.parameters())
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, ntp_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
        loss_val, grads = loss_and_grad(model, input_ids, targets)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0 or step == 0:
            ev = ntp_evaluate(model, np.random.RandomState(999), seq_len=seq_len)
            log.append({"step": step + 1, **ev})
            print(f"    Step {step+1:5d} | loss={ev['loss']:.4f} acc={ev['accuracy']:.1%}")
    return log


def run_beam_only(n_steps=3000, batch_size=32, lr=0.003, seq_len=48):
    model = LambdaModel(d_model=48, n_layers=3, use_ternary=True)
    mx.eval(model.parameters())
    for layer in model.layers:
        layer.plate.freeze()
    optimizer = optim.Adam(learning_rate=lr)
    loss_and_grad = nn.value_and_grad(model, ntp_loss)
    rng = np.random.RandomState(42)

    log = []
    for step in range(n_steps):
        input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
        loss_val, grads = loss_and_grad(model, input_ids, targets)
        mx.eval(loss_val, grads)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())
        del loss_val, grads, input_ids, targets
        if (step + 1) % 50 == 0:
            mx.clear_cache()
        if (step + 1) % 500 == 0 or step == 0:
            ev = ntp_evaluate(model, np.random.RandomState(999), seq_len=seq_len)
            log.append({"step": step + 1, **ev})
            print(f"    Step {step+1:5d} | loss={ev['loss']:.4f} acc={ev['accuracy']:.1%}")
    return log


def run_plate_only(n_rounds=15, etch_batches=200, batch_size=32, seq_len=48):
    model = LambdaModel(d_model=48, n_layers=3, use_ternary=True)
    mx.eval(model.parameters())
    rng = np.random.RandomState(42)

    log = []
    for round_idx in range(n_rounds):
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad = nn.value_and_grad(model, ntp_loss)
        for b in range(etch_batches):
            input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
            loss_val, grads = loss_and_grad(model, input_ids, targets)
            mx.eval(loss_val, grads)
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads, input_ids, targets
            if (b + 1) % 50 == 0:
                mx.clear_cache()

        total_flipped = 0
        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = ((confidence > 0.6) & (target_sign != 0) &
                           (target_sign != current))
            new_signs = np.where(should_flip, target_sign, current)
            layer.plate.weight = mx.array(new_signs.astype(np.float32))
            mx.eval(layer.plate.weight)
            total_flipped += int(should_flip.sum())

        ev = ntp_evaluate(model, np.random.RandomState(999), seq_len=seq_len)
        log.append({"round": round_idx + 1, "flips": total_flipped, **ev})
        print(f"    Round {round_idx+1:3d} | flips={total_flipped:5d} | "
              f"loss={ev['loss']:.4f} acc={ev['accuracy']:.1%}")
        mx.clear_cache()
    return log


def run_alternating(n_rounds=15, etch_batches=200, beam_steps=300,
                    batch_size=32, lr=0.003, seq_len=48):
    model = LambdaModel(d_model=48, n_layers=3, use_ternary=True)
    mx.eval(model.parameters())
    rng = np.random.RandomState(42)

    log = []
    for round_idx in range(n_rounds):
        # Etch
        accumulators = {}
        for i, layer in enumerate(model.layers):
            shape = (layer.plate.out_features, layer.plate.in_features)
            accumulators[i] = np.zeros(shape, dtype=np.float64)

        loss_and_grad = nn.value_and_grad(model, ntp_loss)
        for b in range(etch_batches):
            input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
            loss_val, grads = loss_and_grad(model, input_ids, targets)
            mx.eval(loss_val, grads)
            for i, layer in enumerate(model.layers):
                g = grads["layers"][i]["plate"]["weight"]
                mx.eval(g)
                accumulators[i] += np.sign(np.array(g))
            del loss_val, grads, input_ids, targets
            if (b + 1) % 50 == 0:
                mx.clear_cache()

        total_flipped = 0
        for i, layer in enumerate(model.layers):
            acc = accumulators[i]
            confidence = np.abs(acc) / etch_batches
            target_sign = np.sign(acc)
            current = layer.plate.signs
            should_flip = ((confidence > 0.6) & (target_sign != 0) &
                           (target_sign != current))
            new_signs = np.where(should_flip, target_sign, current)
            layer.plate.weight = mx.array(new_signs.astype(np.float32))
            mx.eval(layer.plate.weight)
            total_flipped += int(should_flip.sum())

        # Beam training
        optimizer = optim.Adam(learning_rate=lr)
        loss_and_grad_beam = nn.value_and_grad(model, ntp_loss)
        for step in range(beam_steps):
            input_ids, targets = generate_lambda_batch(batch_size, rng, seq_len)
            loss_val, grads = loss_and_grad_beam(model, input_ids, targets)
            mx.eval(loss_val, grads)
            for i in range(len(model.layers)):
                if "plate" in grads["layers"][i]:
                    grads["layers"][i]["plate"]["weight"] = mx.zeros_like(
                        grads["layers"][i]["plate"]["weight"])
            model.update(optimizer.apply_gradients(grads, model))
            mx.eval(model.parameters())
            del loss_val, grads, input_ids, targets
            if (step + 1) % 50 == 0:
                mx.clear_cache()

        ev = ntp_evaluate(model, np.random.RandomState(999), seq_len=seq_len)
        log.append({"round": round_idx + 1, "flips": total_flipped, **ev})
        print(f"    Round {round_idx+1:3d} | flips={total_flipped:5d} | "
              f"loss={ev['loss']:.4f} acc={ev['accuracy']:.1%}")
        mx.clear_cache()
    return log


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    output_dir = Path("checkpoints/mini-holo-exp2")
    output_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 60)
    print("  EXPERIMENT 2: Next-Token Prediction on KIBC Lambda")
    print("  vocab=26, seq_len=48, d_model=48, 3 layers")
    print("=" * 60)

    # Show sample data
    rng = np.random.RandomState(42)
    print("\n  Sample expressions:")
    for _ in range(5):
        expr = gen_lambda_expr(rng)
        print(f"    {expr}")

    results = {}

    print("\n  [1/4] GD Baseline...")
    results["gd"] = run_gd_baseline()

    print("\n  [2/4] Beam-Only (random plates)...")
    results["beam_only"] = run_beam_only()

    print("\n  [3/4] Plate-Only (no beam training)...")
    results["plate_only"] = run_plate_only()

    print("\n  [4/4] Alternating (etch + beam)...")
    results["alternating"] = run_alternating()

    # Summary
    print(f"\n{'=' * 60}")
    print("  SUMMARY")
    print(f"{'=' * 60}")
    for name, log in results.items():
        b = max(log, key=lambda x: x["accuracy"])
        sk = "step" if "step" in b else "round"
        print(f"  {name:15s}: best acc={b['accuracy']:.1%} "
              f"loss={b['loss']:.4f} @ {sk}={b[sk]}")

    with open(output_dir / "results.json", "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n  Saved to {output_dir}/results.json")


if __name__ == "__main__":
    main()
