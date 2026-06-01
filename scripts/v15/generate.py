"""v15 Text Generation — sample from a trained checkpoint.

Quick tool to see what the crystal statechart produces.

Usage:
    uv run python scripts/v15/generate.py \
        --checkpoint checkpoints/v15-train/step_0004000 \
        --prompt "The capital of France is" \
        --max-tokens 128 \
        --temperature 0.8

License: MIT
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import mlx.core as mx
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config
from model import TensorStatechart
from load_checkpoint import load_statechart


def load_tokenizer():
    """Load Qwen tokenizer."""
    from transformers import AutoTokenizer
    for name in ["Qwen/Qwen3.6-27B", "Qwen/Qwen3-0.6B", "Qwen/Qwen3-4B"]:
        try:
            tok = AutoTokenizer.from_pretrained(name, trust_remote_code=True)
            print(f"Tokenizer: {name} (vocab={len(tok)})")
            return tok
        except Exception:
            continue
    raise RuntimeError("Could not load Qwen tokenizer")


def load_model(extracted_ckpt: str, train_ckpt: str | None) -> TensorStatechart:
    """Load model from extracted checkpoint, then overlay trained weights."""
    model = load_statechart(extracted_ckpt, freeze_plates=True)

    if train_ckpt:
        weights_path = Path(train_ckpt) / "weights.npz"
        if weights_path.exists():
            saved = mx.load(str(weights_path))
            model.load_weights(list(saved.items()), strict=False)
            print(f"Loaded trained weights from {weights_path}")
        else:
            print(f"WARNING: no weights.npz in {train_ckpt}")

    model.eval()
    return model


def sample_token(logits: mx.array, temperature: float = 1.0, top_k: int = 50) -> int:
    """Sample a token from logits with temperature and top-k."""
    if temperature <= 0:
        return int(mx.argmax(logits, axis=-1).item())

    logits = logits / temperature

    # Top-k filtering
    if top_k > 0 and top_k < logits.shape[-1]:
        top_vals = mx.topk(logits, k=top_k)
        threshold = top_vals[-1]
        logits = mx.where(logits < threshold, mx.array(-1e9), logits)

    probs = mx.softmax(logits, axis=-1)
    token = mx.random.categorical(mx.log(probs + 1e-10))
    return int(token.item())


def generate(
    model: TensorStatechart,
    tokenizer,
    prompt: str,
    max_tokens: int = 128,
    temperature: float = 0.8,
    top_k: int = 50,
) -> str:
    """Auto-regressive generation from the model."""
    input_ids = tokenizer.encode(prompt, add_special_tokens=False)
    tokens = list(input_ids)

    print(f"\n{'='*60}")
    print(f"Prompt ({len(input_ids)} tokens): {prompt}")
    print(f"{'='*60}")
    print(prompt, end="", flush=True)

    t0 = time.time()
    for i in range(max_tokens):
        # Build input tensor
        x = mx.array([tokens])  # (1, seq_len)

        # Forward pass
        result = model(x)
        logits = result["logits"]

        # Get logits for last position
        next_logits = logits[0, -1, :]  # (vocab,)

        # Sample
        next_token = sample_token(next_logits, temperature=temperature, top_k=top_k)
        tokens.append(next_token)

        # Decode and print incrementally
        new_text = tokenizer.decode([next_token])
        print(new_text, end="", flush=True)

        # Stop on EOS
        if next_token == tokenizer.eos_token_id:
            break

    elapsed = time.time() - t0
    gen_tokens = len(tokens) - len(input_ids)
    tok_per_sec = gen_tokens / elapsed if elapsed > 0 else 0

    print(f"\n{'='*60}")
    print(f"Generated {gen_tokens} tokens in {elapsed:.1f}s ({tok_per_sec:.1f} tok/s)")
    print(f"{'='*60}")

    return tokenizer.decode(tokens)


def main():
    p = argparse.ArgumentParser(description="Generate text from v15 statechart")
    p.add_argument("--extracted", default="checkpoints/v15-extracted",
                   help="Path to extracted checkpoint (plates)")
    p.add_argument("--checkpoint", default=None,
                   help="Path to training checkpoint (attention weights)")
    p.add_argument("--prompt", default="The capital of France is",
                   help="Text prompt")
    p.add_argument("--max-tokens", type=int, default=128)
    p.add_argument("--temperature", type=float, default=0.8)
    p.add_argument("--top-k", type=int, default=50)
    p.add_argument("--greedy", action="store_true", help="Greedy decoding (temp=0)")
    p.add_argument("--prompts-file", default=None,
                   help="File with one prompt per line (runs all)")
    args = p.parse_args()

    if args.greedy:
        args.temperature = 0.0

    tokenizer = load_tokenizer()
    model = load_model(args.extracted, args.checkpoint)

    # Multiple prompts
    prompts = []
    if args.prompts_file:
        with open(args.prompts_file) as f:
            prompts = [line.strip() for line in f if line.strip()]
    else:
        prompts = [args.prompt]

    for prompt in prompts:
        generate(model, tokenizer, prompt,
                max_tokens=args.max_tokens,
                temperature=args.temperature,
                top_k=args.top_k)
        print()


if __name__ == "__main__":
    main()
