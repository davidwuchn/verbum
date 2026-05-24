"""
Train Micro Model — Lambda calculus compile examples.

Trains the micro model on pure lambda calculus data (compile-train.jsonl)
until the holographic state machine forms: crystal latches, FFN encodes
inference pattern, attention learns Q rotations.

Data format: {"input": "Every artist knows a baker.",
              "output": "∀x. (artist(x) → knows(x, baker))"}

Tokenized as: <input>\n<output><eod>
Causal LM objective — predict every token including the output.

Usage:
    cd verbum
    uv run python scripts/micro/train_micro.py

License: MIT
"""

from __future__ import annotations

import json
import math
import os
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim

# Import from same directory
import sys
sys.path.insert(0, str(Path(__file__).parent))
from micro_model import MicroModel, MicroConfig


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════


def load_compile_examples(path: str | Path) -> list[dict]:
    """Load compile examples from JSONL."""
    examples = []
    with open(path) as f:
        for line in f:
            line = line.strip()
            if line:
                examples.append(json.loads(line))
    return examples


def tokenize_examples(
    examples: list[dict],
    tokenizer,
    max_len: int = 256,
    eod_id: int = 151643,
) -> list[np.ndarray]:
    """Tokenize compile examples as causal LM sequences.

    Format: <input>\n<output><eod>

    Returns list of int32 arrays, each of length <= max_len.
    """
    sequences = []
    for ex in examples:
        text = f"{ex['input']}\n{ex['output']}"
        token_ids = tokenizer.encode(text, add_special_tokens=False)
        token_ids.append(eod_id)
        if len(token_ids) > max_len:
            token_ids = token_ids[:max_len]
        sequences.append(np.array(token_ids, dtype=np.int32))
    return sequences


class CompileDataLoader:
    """Cycles through tokenized compile examples, packing into batches.

    Packs multiple short examples into one sequence for efficient training.
    Shuffles each epoch.
    """

    def __init__(
        self,
        sequences: list[np.ndarray],
        batch_size: int,
        seq_len: int,
        eod_id: int = 151643,
        seed: int = 42,
    ):
        self.sequences = sequences
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.eod_id = eod_id
        self.rng = np.random.RandomState(seed)

        # Pack all sequences into one long stream
        self._rebuild_stream()

    def _rebuild_stream(self):
        """Shuffle and concatenate all sequences into a token stream."""
        indices = self.rng.permutation(len(self.sequences))
        all_tokens = []
        for idx in indices:
            all_tokens.append(self.sequences[idx])
        self.stream = np.concatenate(all_tokens)
        self.position = 0

    def next_batch(self) -> tuple[np.ndarray, np.ndarray]:
        """Returns (input_ids, targets) each of shape (batch_size, seq_len)."""
        B, T = self.batch_size, self.seq_len
        needed = B * (T + 1)

        if self.position + needed > len(self.stream):
            self._rebuild_stream()

        buf = self.stream[self.position : self.position + needed]
        self.position += needed

        buf = buf.reshape(B, T + 1)
        input_ids = buf[:, :T]
        targets = buf[:, 1 : T + 1]
        return input_ids, targets


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════


def train(cfg: MicroConfig):
    """Train the micro model on compile examples."""

    print("=" * 60)
    print("Micro Model Training — Lambda Calculus")
    print("=" * 60)

    # ── Tokenizer ──
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    print(f"Tokenizer: Qwen3 BBPE, vocab={tokenizer.vocab_size}")

    # ── Data ──
    train_examples = load_compile_examples(cfg.train_file)
    eval_examples = load_compile_examples(cfg.eval_file)
    print(f"Train examples: {len(train_examples)}")
    print(f"Eval examples: {len(eval_examples)}")

    train_seqs = tokenize_examples(train_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    eval_seqs = tokenize_examples(eval_examples, tokenizer, cfg.max_seq_len, cfg.eod_id)
    print(f"Train tokens: {sum(len(s) for s in train_seqs):,}")
    print(f"Eval tokens: {sum(len(s) for s in eval_seqs):,}")
    print(f"Avg seq len: {np.mean([len(s) for s in train_seqs]):.1f}")

    train_loader = CompileDataLoader(
        train_seqs, cfg.batch_size, cfg.max_seq_len, cfg.eod_id)
    # Eval set is tiny (10 examples, ~192 tokens). Use batch_size=1
    # and a seq_len that fits. Pack all eval into one stream.
    eval_total_tokens = sum(len(s) for s in eval_seqs)
    eval_seq_len = min(cfg.max_seq_len, max(16, eval_total_tokens // 2 - 1))
    eval_loader = CompileDataLoader(
        eval_seqs, 1, eval_seq_len, cfg.eod_id, seed=99)

    # ── Model ──
    model = MicroModel(cfg)
    mx.eval(model.parameters())
    counts = model.param_count()
    print(f"\nModel: {counts['total']:,} total params")
    print(f"  Transformer blocks: {counts['blocks']:,}")
    print(f"  Crystal: {counts['crystal']:,}")

    # ── Crystal initial diagnostics ──
    diag = model.crystal_diagnostics()
    print(f"\nInitial crystal:")
    print(f"  loss: {diag['crystal_loss']:.6f}")
    print(f"  comp_cluster: {diag['composition_cluster']:.4f}")
    print(f"  K-I pair: {diag['ki_pair']:.4f}")

    # ── Optimizer ──
    lr_schedule = optim.cosine_decay(cfg.lr, cfg.total_steps, cfg.lr * 0.01)
    warmup_schedule = optim.linear_schedule(
        1e-7, cfg.lr, cfg.warmup_steps)

    def lr_fn(step):
        if step < cfg.warmup_steps:
            return warmup_schedule(step)
        return lr_schedule(step)

    optimizer = optim.AdamW(
        learning_rate=lr_fn,
        weight_decay=cfg.weight_decay,
    )

    # ── Loss function for value_and_grad ──
    def loss_fn(model, input_ids, targets):
        _, loss = model(input_ids, targets)
        return loss

    loss_and_grad_fn = nn.value_and_grad(model, loss_fn)

    # ── Checkpoint directory ──
    os.makedirs(cfg.checkpoint_dir, exist_ok=True)

    # ── Training loop ──
    print(f"\nTraining for {cfg.total_steps} steps...")
    print(f"  batch_size={cfg.batch_size}, seq_len={cfg.max_seq_len}")
    print(f"  lr={cfg.lr}, warmup={cfg.warmup_steps}")
    print()

    best_eval_loss = float("inf")
    t_start = time.time()

    for step in range(1, cfg.total_steps + 1):
        model._training_step = step

        # ── Train step ──
        input_ids, targets = train_loader.next_batch()
        input_ids = mx.array(input_ids)
        targets = mx.array(targets)

        loss_val, grads = loss_and_grad_fn(model, input_ids, targets)

        # Gradient clipping
        grads, gnorm = optim.clip_grad_norm(grads, cfg.grad_clip)

        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state, loss_val, gnorm)

        # ── Logging ──
        if step % cfg.log_interval == 0 or step == 1:
            ce = float(model._last_ce_loss.item())
            crystal = float(model._last_crystal_loss.item())
            crystal_ema = float(model._crystal_ema.item())
            parity = float(getattr(model, '_last_parity_loss', mx.array(0.0)).item())
            elapsed = time.time() - t_start
            lr_now = lr_fn(step)
            lr_val = float(lr_now.item()) if isinstance(lr_now, mx.array) else float(lr_now)

            print(
                f"step {step:5d} | "
                f"CE {ce:.4f} | "
                f"crystal {crystal:.6f} (ema {crystal_ema:.6f}) | "
                f"parity {parity:.4f} | "
                f"gnorm {float(gnorm.item()):.2f} | "
                f"lr {lr_val:.2e} | "
                f"{elapsed:.0f}s"
            )

        # ── Eval ──
        if step % cfg.eval_interval == 0:
            eval_input, eval_target = eval_loader.next_batch()
            eval_input = mx.array(eval_input)
            eval_target = mx.array(eval_target)
            eval_logits, eval_loss = model(eval_input, eval_target)
            mx.eval(eval_loss)
            eval_loss_val = float(eval_loss.item())
            eval_ce = float(model._last_ce_loss.item())

            # Crystal diagnostics
            diag = model.crystal_diagnostics()

            print(f"  EVAL  | CE {eval_ce:.4f} | total {eval_loss_val:.4f}")
            print(f"        | crystal {diag['crystal_loss']:.6f} | "
                  f"comp_cluster {diag['composition_cluster']:.4f} | "
                  f"K-I {diag['ki_pair']:.4f} | "
                  f"WHNF_anti {diag['whnf_anti']:.4f}")

            if eval_loss_val < best_eval_loss:
                best_eval_loss = eval_loss_val
                print(f"        | ★ New best eval loss")

            # ── Generate a sample ──
            try:
                prompt = train_examples[step % len(train_examples)]["input"]
                prompt_tokens = tokenizer.encode(prompt + "\n", add_special_tokens=False)
                gen_tokens = generate(model, prompt_tokens, tokenizer, max_new=64)
                gen_text = tokenizer.decode(gen_tokens)
                print(f"  GEN   | {prompt}")
                print(f"        | {gen_text}")
            except Exception as e:
                print(f"  GEN   | (error: {e})")

        # ── Checkpoint ──
        if step % cfg.checkpoint_interval == 0:
            ckpt_dir = Path(cfg.checkpoint_dir) / f"step_{step:06d}"
            os.makedirs(ckpt_dir, exist_ok=True)

            # Save model weights
            flat = dict(nn.utils.tree_flatten(model.parameters()))
            mx.savez(str(ckpt_dir / "model.npz"), **flat)

            # Save config + training state
            state = {
                "step": step,
                "crystal_ema": float(model._crystal_ema.item()),
                "best_eval_loss": best_eval_loss,
            }
            with open(ckpt_dir / "state.json", "w") as f:
                json.dump(state, f, indent=2)

            print(f"  CKPT  | saved to {ckpt_dir}")

    # ── Final save ──
    final_dir = Path(cfg.checkpoint_dir) / "final"
    os.makedirs(final_dir, exist_ok=True)
    flat = dict(nn.utils.tree_flatten(model.parameters()))
    mx.savez(str(final_dir / "model.npz"), **flat)
    state = {
        "step": cfg.total_steps,
        "crystal_ema": float(model._crystal_ema.item()),
        "best_eval_loss": best_eval_loss,
    }
    with open(final_dir / "state.json", "w") as f:
        json.dump(state, f, indent=2)

    print(f"\nTraining complete. Final model saved to {final_dir}")
    print(f"Best eval loss: {best_eval_loss:.4f}")

    # ── Final crystal diagnostics ──
    diag = model.crystal_diagnostics()
    print(f"\nFinal crystal:")
    print(f"  loss: {diag['crystal_loss']:.6f}")
    print(f"  comp_cluster: {diag['composition_cluster']:.4f}")
    print(f"  K-I pair: {diag['ki_pair']:.4f}")
    print(f"  WHNF anti: {diag['whnf_anti']:.4f}")


# ══════════════════════════════════════════════════════════════════════
# Generation (for eval samples)
# ══════════════════════════════════════════════════════════════════════


def generate(
    model: MicroModel,
    prompt_tokens: list[int],
    tokenizer,
    max_new: int = 64,
    temperature: float = 0.0,
) -> list[int]:
    """Greedy or temperature-sampled generation."""
    tokens = list(prompt_tokens)
    eod_id = model.cfg.eod_id

    for _ in range(max_new):
        # Truncate to max_seq_len
        input_tokens = tokens[-model.cfg.max_seq_len:]
        input_mx = mx.array([input_tokens])
        logits, _ = model(input_mx)
        mx.eval(logits)

        # Get logits for last position
        next_logits = logits[0, -1, :]

        if temperature == 0.0:
            next_token = int(mx.argmax(next_logits).item())
        else:
            probs = mx.softmax(next_logits / temperature, axis=-1)
            next_token = int(mx.random.categorical(mx.log(probs + 1e-10)).item())

        tokens.append(next_token)
        if next_token == eod_id:
            break

    return tokens[len(prompt_tokens):]


# ══════════════════════════════════════════════════════════════════════
# Entry point
# ══════════════════════════════════════════════════════════════════════


if __name__ == "__main__":
    cfg = MicroConfig()
    train(cfg)
