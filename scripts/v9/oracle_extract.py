"""
Oracle extraction pipeline: feed sentences through Qwen3-32B,
extract L28 hidden states, mean-pool to word level, save shards.

This produces the training targets for the ascending arm.

Pipeline:
  1. Load Qwen3-32B from GGUF (proven pattern, ~62s on M3 Ultra)
  2. Hook ONLY layer 28 (peak typing layer)
  3. Read corpus JSONL from stdin or file
  4. For each sentence:
     a. Tokenize with Qwen3 BBPE
     b. Forward pass (inference only)
     c. Extract L28 hidden states (5120-dim)
     d. Detect BPE word boundaries (Ġ prefix)
     e. Mean-pool subword spans to word level
  5. Save shards every N sentences as compressed npz

Output per shard (results/oracle-data/shard_{NNN}.npz):
  - word_vectors: (total_words, 5120) float16
  - word_texts: list of word strings
  - sentence_offsets: (n_sentences,) int — start index of each sentence's words
  - sentence_texts: list of sentence strings
  - strata: list of stratum labels
  - groups: list of group labels (for cross-notation)

Usage:
  uv run python scripts/v9/oracle_corpus.py --pilot | \
    uv run python scripts/v9/oracle_extract.py --shard-size 100

  uv run python scripts/v9/oracle_extract.py --input corpus.jsonl

License: MIT
"""

import json
import time
import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


TARGET_LAYER = 28
DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "results" / "oracle-data"


# ══════════════════════════════════════════════════════════════════
# Model loading (from probe_clusters.py — proven)
# ══════════════════════════════════════════════════════════════════

def load_model(gguf_path: str, device: str = "mps"):
    """Load Qwen3-32B from GGUF."""
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")

    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir,
        gguf_file=gguf_file,
        dtype=torch.float16,
        device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}, device={device}", file=sys.stderr)

    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Word boundary detection
# ══════════════════════════════════════════════════════════════════

def detect_word_boundaries(tokenizer, input_ids: torch.Tensor) -> list[list[int]]:
    """Detect BPE word boundaries from token IDs.

    Returns list of word spans, where each span is a list of token indices
    belonging to that word.

    Qwen3 BBPE convention:
      - Word-initial tokens start with Ġ (U+0120, displayed as ▁)
      - Continuation tokens have no prefix
      - Special tokens (BOS/EOS) are standalone words
    """
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    words = []
    current_word = []

    for i, tok in enumerate(tokens):
        # Skip special tokens
        if tok in tokenizer.all_special_tokens:
            if current_word:
                words.append(current_word)
                current_word = []
            continue

        # Word boundary: starts with Ġ or is the first non-special token
        if tok.startswith("Ġ") or tok.startswith("▁") or not current_word:
            if current_word:
                words.append(current_word)
            current_word = [i]
        else:
            current_word.append(i)

    if current_word:
        words.append(current_word)

    return words


def word_text(tokenizer, input_ids: torch.Tensor, span: list[int]) -> str:
    """Reconstruct word text from token span."""
    token_ids = [input_ids[0, i].item() for i in span]
    text = tokenizer.decode(token_ids, skip_special_tokens=True).strip()
    return text


# ══════════════════════════════════════════════════════════════════
# Extraction
# ══════════════════════════════════════════════════════════════════

def extract_sentence(
    model, tokenizer, sentence: str, device: str,
    hook_storage: dict, target_layer: int = TARGET_LAYER,
) -> tuple[np.ndarray, list[str]]:
    """Extract per-word L28 vectors for a single sentence.

    Returns:
      word_vecs: (n_words, 5120) float16 — mean-pooled per word
      word_texts: list of word strings
    """
    # Tokenize
    inputs = tokenizer(sentence, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]

    # Forward pass (hook captures L28)
    hook_storage.clear()
    with torch.no_grad():
        _ = model(**inputs)

    # Get L28 hidden states
    hidden = hook_storage[target_layer]  # (1, seq_len, 5120)

    # Detect word boundaries
    word_spans = detect_word_boundaries(tokenizer, input_ids)

    # Mean-pool per word
    n_words = len(word_spans)
    d = hidden.shape[-1]
    word_vecs = np.zeros((n_words, d), dtype=np.float16)
    texts = []

    for wi, span in enumerate(word_spans):
        # Extract token vectors for this word span
        vecs = hidden[0, span, :]  # (n_tokens_in_word, d)
        pooled = vecs.mean(dim=0).cpu().numpy().astype(np.float16)
        word_vecs[wi] = pooled
        texts.append(word_text(tokenizer, input_ids, span))

    return word_vecs, texts


# ══════════════════════════════════════════════════════════════════
# Shard saving
# ══════════════════════════════════════════════════════════════════

def save_shard(
    shard_idx: int,
    word_vectors: list[np.ndarray],
    word_texts: list[list[str]],
    sentence_texts: list[str],
    strata: list[str],
    groups: list[str | None],
    output_dir: Path,
):
    """Save accumulated sentences as a compressed shard."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Stack word vectors
    all_word_vecs = np.concatenate(word_vectors, axis=0)  # (total_words, 5120)

    # Sentence offsets: where each sentence's words start
    offsets = np.zeros(len(word_vectors), dtype=np.int32)
    running = 0
    for i, wv in enumerate(word_vectors):
        offsets[i] = running
        running += wv.shape[0]

    # Flatten word texts
    flat_word_texts = []
    for wt_list in word_texts:
        flat_word_texts.extend(wt_list)

    shard_path = output_dir / f"shard_{shard_idx:04d}.npz"

    np.savez_compressed(
        shard_path,
        word_vectors=all_word_vecs,
        sentence_offsets=offsets,
        # Store text arrays as JSON strings in a single array
        word_texts=np.array(flat_word_texts, dtype=object),
        sentence_texts=np.array(sentence_texts, dtype=object),
        strata=np.array(strata, dtype=object),
        groups=np.array([g if g else "" for g in groups], dtype=object),
    )

    total_words = all_word_vecs.shape[0]
    size_mb = shard_path.stat().st_size / 1e6
    print(f"  Saved shard {shard_idx}: {len(sentence_texts)} sentences, "
          f"{total_words} words, {all_word_vecs.shape}, {size_mb:.1f} MB",
          file=sys.stderr)

    return shard_path


# ══════════════════════════════════════════════════════════════════
# Main pipeline
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Extract oracle L28 activations")
    parser.add_argument("--gguf", default=DEFAULT_GGUF,
                        help="Path to Qwen3-32B GGUF file")
    parser.add_argument("--device", default="mps",
                        help="Device (mps, cuda, cpu)")
    parser.add_argument("--input", default=None,
                        help="Input JSONL file (default: stdin)")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR),
                        help="Output directory for shards")
    parser.add_argument("--shard-size", type=int, default=500,
                        help="Sentences per shard")
    parser.add_argument("--max-sentences", type=int, default=None,
                        help="Stop after N sentences (for testing)")
    parser.add_argument("--layer", type=int, default=TARGET_LAYER,
                        help=f"Target layer (default: {TARGET_LAYER})")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)

    # Load model
    model, tokenizer = load_model(args.gguf, device=args.device)

    # Register hook on target layer only
    hook_storage = {}

    def hook_fn(module, input, output):
        hidden = output[0] if isinstance(output, tuple) else output
        hook_storage[args.layer] = hidden.detach()

    hook = model.model.layers[args.layer].register_forward_hook(hook_fn)

    # Read corpus
    if args.input:
        f_in = open(args.input)
    else:
        f_in = sys.stdin

    # Accumulate for shards
    shard_word_vecs = []
    shard_word_texts = []
    shard_sent_texts = []
    shard_strata = []
    shard_groups = []
    shard_idx = 0
    total_sentences = 0
    total_words = 0
    t_start = time.time()
    t_last_report = t_start

    try:
        for line_no, line in enumerate(f_in):
            line = line.strip()
            if not line:
                continue

            record = json.loads(line)
            sentence = record["sentence"]
            stratum = record["stratum"]
            group = record.get("group")

            try:
                word_vecs, word_txts = extract_sentence(
                    model, tokenizer, sentence, args.device,
                    hook_storage, target_layer=args.layer,
                )
            except Exception as e:
                print(f"  ERROR on sentence {line_no}: {e}", file=sys.stderr)
                continue

            shard_word_vecs.append(word_vecs)
            shard_word_texts.append(word_txts)
            shard_sent_texts.append(sentence)
            shard_strata.append(stratum)
            shard_groups.append(group)

            total_sentences += 1
            total_words += word_vecs.shape[0]

            # Save shard when full
            if len(shard_sent_texts) >= args.shard_size:
                save_shard(
                    shard_idx, shard_word_vecs, shard_word_texts,
                    shard_sent_texts, shard_strata, shard_groups, output_dir,
                )
                shard_idx += 1
                shard_word_vecs = []
                shard_word_texts = []
                shard_sent_texts = []
                shard_strata = []
                shard_groups = []

            # Progress report every 10 seconds
            now = time.time()
            if now - t_last_report > 10:
                elapsed = now - t_start
                rate = total_sentences / elapsed
                print(f"  [{total_sentences} sentences, {total_words} words, "
                      f"{rate:.1f} sent/s, {elapsed:.0f}s elapsed]",
                      file=sys.stderr)
                t_last_report = now

            # Early stop
            if args.max_sentences and total_sentences >= args.max_sentences:
                break

    finally:
        # Save remaining
        if shard_sent_texts:
            save_shard(
                shard_idx, shard_word_vecs, shard_word_texts,
                shard_sent_texts, shard_strata, shard_groups, output_dir,
            )
            shard_idx += 1

        # Cleanup
        hook.remove()
        if args.input and f_in is not sys.stdin:
            f_in.close()

    elapsed = time.time() - t_start
    rate = total_sentences / elapsed if elapsed > 0 else 0

    print(f"\nDone: {total_sentences} sentences → {total_words} words "
          f"in {shard_idx} shards", file=sys.stderr)
    print(f"Time: {elapsed:.1f}s ({rate:.1f} sent/s)", file=sys.stderr)
    print(f"Output: {output_dir}/", file=sys.stderr)


if __name__ == "__main__":
    main()
