#!/usr/bin/env python3
"""Type probe — Montague semantic types in Qwen3-32B.

Does Qwen3-32B encode Montague semantic types? At which layer do types
become linearly decodable?  Pythia-160M showed 84% in embeddings, 93%
at L0, then flat.  A 32B model with a fully-formed lambda compiler may
show a richer story: refined type geometry at deeper layers, or
type-differentiation that the small model lacked.

Method:
  1. Labeled dataset: word → simplified Montague type (8 categories)
  2. Forward pass through Qwen3-32B, capture residual stream at every layer
  3. Linear probe (logistic regression) per layer — 5-fold CV
  4. Where does type information become/remain decodable?

Architecture: Qwen3-32B — 64 layers, 64 heads, GQA(8 KV), d=5120, bf16.

Usage:
    uv run python scripts/explore/probe_type_qwen3_32b.py
    uv run python scripts/explore/probe_type_qwen3_32b.py --layer-stride 2  # every other layer
    uv run python scripts/explore/probe_type_qwen3_32b.py --quick  # fewer sentences

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score
from sklearn.preprocessing import LabelEncoder

MODEL = "Qwen/Qwen3-32B"

RESULTS_DIR = Path("results/type-probe-qwen3-32b")

# ══════════════════════════════════════════════════════════════════════
# Semantic Type Labels (simplified Montague)
# ══════════════════════════════════════════════════════════════════════
#
# Full Montague types are recursive but for a linear probe we need
# flat categories that capture the major type distinctions:
#
#   ENTITY     e              proper nouns, bare nouns as constants
#   PRED       <e,t>          intransitive verbs, predicate adjectives
#   REL        <e,<e,t>>      transitive verbs
#   QUANT      <<e,t>,t>      quantifier words (every, some, no, most)
#   DET        <e,t>→e        determiners (the, a, an)
#   CONN       t→t→t          connectives (and, or, if, not, because)
#   MOD        <e,t>→<e,t>    adjectives, adverbs (predicate modifiers)
#   FUNC       (structural)   punctuation, particles, auxiliaries

LABELED_DATA = [
    # ── Simple predication (intransitive) ─────────────────────
    ("The dog runs.", [
        ("The", "DET"), ("dog", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("The bird flies.", [
        ("The", "DET"), ("bird", "ENTITY"), ("flies", "PRED"), (".", "FUNC"),
    ]),
    ("The cat sleeps.", [
        ("The", "DET"), ("cat", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("The teacher laughs.", [
        ("The", "DET"), ("teacher", "ENTITY"), ("laughs", "PRED"), (".", "FUNC"),
    ]),
    ("The fish swims.", [
        ("The", "DET"), ("fish", "ENTITY"), ("swims", "PRED"), (".", "FUNC"),
    ]),
    ("The farmer walks.", [
        ("The", "DET"), ("farmer", "ENTITY"), ("walks", "PRED"), (".", "FUNC"),
    ]),
    ("The singer dances.", [
        ("The", "DET"), ("singer", "ENTITY"), ("dances", "PRED"), (".", "FUNC"),
    ]),
    ("The child cries.", [
        ("The", "DET"), ("child", "ENTITY"), ("cries", "PRED"), (".", "FUNC"),
    ]),
    ("The engine roars.", [
        ("The", "DET"), ("engine", "ENTITY"), ("roars", "PRED"), (".", "FUNC"),
    ]),
    ("The river flows.", [
        ("The", "DET"), ("river", "ENTITY"), ("flows", "PRED"), (".", "FUNC"),
    ]),

    # ── Proper nouns ──────────────────────────────────────────
    ("Alice runs.", [
        ("Alice", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("Bob sleeps.", [
        ("Bob", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("Tom walks.", [
        ("Tom", "ENTITY"), ("walks", "PRED"), (".", "FUNC"),
    ]),
    ("Mary sings.", [
        ("Mary", "ENTITY"), ("sings", "PRED"), (".", "FUNC"),
    ]),
    ("John laughs.", [
        ("John", "ENTITY"), ("laughs", "PRED"), (".", "FUNC"),
    ]),
    ("Sarah dances.", [
        ("Sarah", "ENTITY"), ("dances", "PRED"), (".", "FUNC"),
    ]),

    # ── Transitive ────────────────────────────────────────────
    ("Alice loves Bob.", [
        ("Alice", "ENTITY"), ("loves", "REL"), ("Bob", "ENTITY"), (".", "FUNC"),
    ]),
    ("The dog sees the cat.", [
        ("The", "DET"), ("dog", "ENTITY"), ("sees", "REL"),
        ("the", "DET"), ("cat", "ENTITY"), (".", "FUNC"),
    ]),
    ("Tom helps Mary.", [
        ("Tom", "ENTITY"), ("helps", "REL"), ("Mary", "ENTITY"), (".", "FUNC"),
    ]),
    ("The teacher reads the book.", [
        ("The", "DET"), ("teacher", "ENTITY"), ("reads", "REL"),
        ("the", "DET"), ("book", "ENTITY"), (".", "FUNC"),
    ]),
    ("The farmer finds the bird.", [
        ("The", "DET"), ("farmer", "ENTITY"), ("finds", "REL"),
        ("the", "DET"), ("bird", "ENTITY"), (".", "FUNC"),
    ]),
    ("Alice watches Bob.", [
        ("Alice", "ENTITY"), ("watches", "REL"), ("Bob", "ENTITY"), (".", "FUNC"),
    ]),
    ("Sarah chases Tom.", [
        ("Sarah", "ENTITY"), ("chases", "REL"), ("Tom", "ENTITY"), (".", "FUNC"),
    ]),
    ("The child hugs the dog.", [
        ("The", "DET"), ("child", "ENTITY"), ("hugs", "REL"),
        ("the", "DET"), ("dog", "ENTITY"), (".", "FUNC"),
    ]),
    ("John knows Mary.", [
        ("John", "ENTITY"), ("knows", "REL"), ("Mary", "ENTITY"), (".", "FUNC"),
    ]),
    ("The cat catches the bird.", [
        ("The", "DET"), ("cat", "ENTITY"), ("catches", "REL"),
        ("the", "DET"), ("bird", "ENTITY"), (".", "FUNC"),
    ]),

    # ── Quantified ────────────────────────────────────────────
    ("Every dog runs.", [
        ("Every", "QUANT"), ("dog", "ENTITY"), ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("Some cat sleeps.", [
        ("Some", "QUANT"), ("cat", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("No bird flies.", [
        ("No", "QUANT"), ("bird", "ENTITY"), ("flies", "PRED"), (".", "FUNC"),
    ]),
    ("Every student reads a book.", [
        ("Every", "QUANT"), ("student", "ENTITY"), ("reads", "REL"),
        ("a", "DET"), ("book", "ENTITY"), (".", "FUNC"),
    ]),
    ("Some teacher laughs.", [
        ("Some", "QUANT"), ("teacher", "ENTITY"), ("laughs", "PRED"), (".", "FUNC"),
    ]),
    ("No fish swims.", [
        ("No", "QUANT"), ("fish", "ENTITY"), ("swims", "PRED"), (".", "FUNC"),
    ]),
    ("Most children play.", [
        ("Most", "QUANT"), ("children", "ENTITY"), ("play", "PRED"), (".", "FUNC"),
    ]),
    ("Few doctors smoke.", [
        ("Few", "QUANT"), ("doctors", "ENTITY"), ("smoke", "PRED"), (".", "FUNC"),
    ]),
    ("All rivers flow.", [
        ("All", "QUANT"), ("rivers", "ENTITY"), ("flow", "PRED"), (".", "FUNC"),
    ]),

    # ── Modifiers ─────────────────────────────────────────────
    ("The tall dog runs.", [
        ("The", "DET"), ("tall", "MOD"), ("dog", "ENTITY"),
        ("runs", "PRED"), (".", "FUNC"),
    ]),
    ("The small cat sleeps.", [
        ("The", "DET"), ("small", "MOD"), ("cat", "ENTITY"),
        ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("Tom runs quickly.", [
        ("Tom", "ENTITY"), ("runs", "PRED"), ("quickly", "MOD"), (".", "FUNC"),
    ]),
    ("The bird flies slowly.", [
        ("The", "DET"), ("bird", "ENTITY"), ("flies", "PRED"),
        ("slowly", "MOD"), (".", "FUNC"),
    ]),
    ("The brave farmer walks.", [
        ("The", "DET"), ("brave", "MOD"), ("farmer", "ENTITY"),
        ("walks", "PRED"), (".", "FUNC"),
    ]),
    ("The old house stands.", [
        ("The", "DET"), ("old", "MOD"), ("house", "ENTITY"),
        ("stands", "PRED"), (".", "FUNC"),
    ]),
    ("The clever student answers.", [
        ("The", "DET"), ("clever", "MOD"), ("student", "ENTITY"),
        ("answers", "PRED"), (".", "FUNC"),
    ]),
    ("The child runs happily.", [
        ("The", "DET"), ("child", "ENTITY"), ("runs", "PRED"),
        ("happily", "MOD"), (".", "FUNC"),
    ]),
    ("A bright light shines.", [
        ("A", "DET"), ("bright", "MOD"), ("light", "ENTITY"),
        ("shines", "PRED"), (".", "FUNC"),
    ]),

    # ── Connectives ───────────────────────────────────────────
    ("Alice runs and Bob sleeps.", [
        ("Alice", "ENTITY"), ("runs", "PRED"), ("and", "CONN"),
        ("Bob", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("The dog runs or the cat sleeps.", [
        ("The", "DET"), ("dog", "ENTITY"), ("runs", "PRED"), ("or", "CONN"),
        ("the", "DET"), ("cat", "ENTITY"), ("sleeps", "PRED"), (".", "FUNC"),
    ]),
    ("Tom sings but Mary dances.", [
        ("Tom", "ENTITY"), ("sings", "PRED"), ("but", "CONN"),
        ("Mary", "ENTITY"), ("dances", "PRED"), (".", "FUNC"),
    ]),
    ("John reads because Sarah writes.", [
        ("John", "ENTITY"), ("reads", "PRED"), ("because", "CONN"),
        ("Sarah", "ENTITY"), ("writes", "PRED"), (".", "FUNC"),
    ]),

    # ── Copular / predicate adjective ─────────────────────────
    ("The dog is tall.", [
        ("The", "DET"), ("dog", "ENTITY"), ("is", "FUNC"),
        ("tall", "PRED"), (".", "FUNC"),
    ]),
    ("Alice is brave.", [
        ("Alice", "ENTITY"), ("is", "FUNC"), ("brave", "PRED"), (".", "FUNC"),
    ]),
    ("The house is old.", [
        ("The", "DET"), ("house", "ENTITY"), ("is", "FUNC"),
        ("old", "PRED"), (".", "FUNC"),
    ]),

    # ── Negation ──────────────────────────────────────────────
    ("The dog does not run.", [
        ("The", "DET"), ("dog", "ENTITY"), ("does", "FUNC"),
        ("not", "CONN"), ("run", "PRED"), (".", "FUNC"),
    ]),
    ("Alice does not sing.", [
        ("Alice", "ENTITY"), ("does", "FUNC"),
        ("not", "CONN"), ("sing", "PRED"), (".", "FUNC"),
    ]),

    # ── Complex composition ───────────────────────────────────
    ("Every tall student reads a small book.", [
        ("Every", "QUANT"), ("tall", "MOD"), ("student", "ENTITY"),
        ("reads", "REL"), ("a", "DET"), ("small", "MOD"),
        ("book", "ENTITY"), (".", "FUNC"),
    ]),
    ("Some brave farmer finds the old bird.", [
        ("Some", "QUANT"), ("brave", "MOD"), ("farmer", "ENTITY"),
        ("finds", "REL"), ("the", "DET"), ("old", "MOD"),
        ("bird", "ENTITY"), (".", "FUNC"),
    ]),
    ("No clever child quickly runs.", [
        ("No", "QUANT"), ("clever", "MOD"), ("child", "ENTITY"),
        ("quickly", "MOD"), ("runs", "PRED"), (".", "FUNC"),
    ]),
]


def banner(msg: str) -> None:
    print(f"\n{'='*72}\n  {msg}\n{'='*72}\n", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model(model_name: str, device: str = "mps"):
    """Load Qwen3-32B in bf16 with eager attention (for hook compatibility)."""
    from transformers import AutoModelForCausalLM, AutoTokenizer, AutoConfig

    banner(f"Loading {model_name}")
    t0 = time.time()

    config = AutoConfig.from_pretrained(model_name)
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
        attn_implementation="eager",
    )
    model.eval()

    dt = time.time() - t0
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size
    n_heads = config.num_attention_heads
    n_kv = getattr(config, "num_key_value_heads", n_heads)

    print(f"  Loaded in {dt:.1f}s", file=sys.stderr)
    print(f"  Layers: {n_layers}  Heads: {n_heads}  KV heads: {n_kv}  d_model: {d_model}",
          file=sys.stderr, flush=True)

    return model, tokenizer, config


# ══════════════════════════════════════════════════════════════════════
# Residual stream capture
# ══════════════════════════════════════════════════════════════════════

def get_transformer_layers(model):
    """Get the list of transformer layers from any HF model."""
    # Qwen3 structure: model.model.layers
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    # GPTNeoX: model.gpt_neox.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    # Llama/Mistral: model.model.layers
    raise ValueError(f"Cannot find transformer layers in {type(model).__name__}")


def get_embed_module(model):
    """Get the embedding module for pre-layer residual capture."""
    if hasattr(model, "model") and hasattr(model.model, "embed_tokens"):
        return model.model.embed_tokens  # Qwen3, Llama, Mistral
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "embed_in"):
        return model.gpt_neox.embed_in  # GPTNeoX
    return None


def capture_residuals(
    model, tokenizer, text: str,
    layer_indices: list[int] | None = None,
) -> tuple[dict[int, np.ndarray], list[int]]:
    """Capture residual stream at specified layers.

    Returns:
        residuals: {layer_idx: np.array (seq_len, d_model)}
                   layer_idx=-1 is embedding output (before any transformer layer)
        token_ids: list of token IDs
    """
    layers = get_transformer_layers(model)
    n_layers = len(layers)

    if layer_indices is None:
        layer_indices = list(range(n_layers))

    layer_set = set(layer_indices)
    residuals: dict[int, np.ndarray] = {}
    hooks = []

    # Hook embedding output (layer -1)
    embed_mod = get_embed_module(model)
    if embed_mod is not None and -1 in layer_set:
        def embed_hook(module, args, output):
            if isinstance(output, tuple):
                h = output[0]
            else:
                h = output
            residuals[-1] = h[0].detach().cpu().float().numpy()
        hooks.append(embed_mod.register_forward_hook(embed_hook))

    # Hook transformer layers
    for idx in layer_indices:
        if idx < 0:
            continue

        def make_hook(layer_idx):
            def hook_fn(module, args, output):
                # output is typically (hidden_states, ...) or just hidden_states
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                residuals[layer_idx] = h[0].detach().cpu().float().numpy()
            return hook_fn

        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt")
        # Move to model's device
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        token_ids = inputs["input_ids"][0].tolist()

        with torch.no_grad():
            model(**inputs, output_attentions=False)
    finally:
        for h in hooks:
            h.remove()

    return residuals, token_ids


# ══════════════════════════════════════════════════════════════════════
# Token → word alignment
# ══════════════════════════════════════════════════════════════════════

def align_tokens_to_labels(
    tokenizer, token_ids: list[int], word_labels: list[tuple[str, str]],
) -> list[tuple[int, str]]:
    """Align BPE tokens to word-level type labels.

    Returns list of (token_idx, type_label) for tokens that could be matched.
    Uses the FIRST token of each word for the probe (the token that carries
    the word's identity signal most strongly).
    """
    # Decode each token individually
    token_strs = [tokenizer.decode([tid], skip_special_tokens=False) for tid in token_ids]

    aligned = []
    word_idx = 0
    consumed_chars = 0

    for tok_idx, tok_str in enumerate(token_strs):
        if word_idx >= len(word_labels):
            break

        word_text, word_type = word_labels[word_idx]
        tok_clean = tok_str.strip()

        if not tok_clean:
            continue

        # Check if this token starts the current word
        if word_text.lower().startswith(tok_clean.lower()):
            aligned.append((tok_idx, word_type))
            consumed_chars += len(tok_clean)
            if consumed_chars >= len(word_text):
                word_idx += 1
                consumed_chars = 0
        elif tok_clean.lower().startswith(word_text.lower()):
            # Token contains the whole word (and maybe more)
            aligned.append((tok_idx, word_type))
            word_idx += 1
            consumed_chars = 0
        elif consumed_chars > 0:
            # Continuation of a multi-token word — skip (we use first token)
            consumed_chars += len(tok_clean)
            if consumed_chars >= len(word_text):
                word_idx += 1
                consumed_chars = 0
        else:
            # Try to find this token somewhere in the current word
            lower_word = word_text.lower()
            lower_tok = tok_clean.lower()
            if lower_tok in lower_word:
                aligned.append((tok_idx, word_type))
                consumed_chars = len(tok_clean)
                if consumed_chars >= len(word_text):
                    word_idx += 1
                    consumed_chars = 0

    return aligned


# ══════════════════════════════════════════════════════════════════════
# Build probing dataset
# ══════════════════════════════════════════════════════════════════════

def build_probing_dataset(
    model, tokenizer,
    layer_indices: list[int],
    labeled_data: list,
    verbose: bool = True,
) -> tuple[dict[int, tuple[np.ndarray, np.ndarray]], int, int]:
    """Build (residual_vector, type_label) pairs at specified layers.

    Returns:
        data_by_layer: {layer_idx: (X, y)} where X is (N, d_model), y is (N,)
        n_labeled: total labeled tokens
        n_skipped: sentences where alignment failed
    """
    data_by_layer: dict[int, tuple[list, list]] = {L: ([], []) for L in layer_indices}

    n_labeled = 0
    n_skipped = 0

    for sent_idx, (sent, word_labels) in enumerate(labeled_data):
        if verbose and sent_idx % 10 == 0:
            print(f"    sentence {sent_idx+1}/{len(labeled_data)}: {sent[:40]}...",
                  file=sys.stderr, flush=True)

        residuals, token_ids = capture_residuals(model, tokenizer, sent, layer_indices)
        aligned = align_tokens_to_labels(tokenizer, token_ids, word_labels)

        if not aligned:
            n_skipped += 1
            continue

        for tok_idx, word_type in aligned:
            for L in layer_indices:
                if L in residuals and tok_idx < residuals[L].shape[0]:
                    data_by_layer[L][0].append(residuals[L][tok_idx])
                    data_by_layer[L][1].append(word_type)
            n_labeled += 1

        # Free memory
        del residuals
        gc.collect()

    # Convert to numpy
    result = {}
    for L in layer_indices:
        X_list, y_list = data_by_layer[L]
        if X_list:
            result[L] = (np.array(X_list), np.array(y_list))

    return result, n_labeled, n_skipped


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Type probe for Qwen3-32B")
    parser.add_argument("--model", default=MODEL, help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--layer-stride", type=int, default=1,
                        help="Sample every N-th layer (default: every layer)")
    parser.add_argument("--quick", action="store_true",
                        help="Use fewer sentences for quick testing")
    parser.add_argument("--output", default=None, help="Output directory override")
    args = parser.parse_args()

    start = time.time()
    results_dir = Path(args.output) if args.output else RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)

    banner(f"TYPE PROBE — {args.model}")
    print(f"  Time: {datetime.now(UTC).isoformat()}", file=sys.stderr)

    # Load model
    model, tokenizer, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size

    # Select data
    labeled_data = LABELED_DATA
    if args.quick:
        labeled_data = labeled_data[:20]
        print(f"  Quick mode: using {len(labeled_data)}/{len(LABELED_DATA)} sentences",
              file=sys.stderr)

    # Count labels
    all_labels = []
    for _, word_labels in labeled_data:
        for _, wtype in word_labels:
            all_labels.append(wtype)
    label_counts = Counter(all_labels)
    print(f"  Sentences: {len(labeled_data)}", file=sys.stderr)
    print(f"  Token labels: {dict(label_counts)}", file=sys.stderr)
    print(f"  Total labeled: {len(all_labels)}", file=sys.stderr, flush=True)

    # Determine layers to probe
    if args.layer_stride > 1:
        layer_indices = [-1] + list(range(0, n_layers, args.layer_stride))
        if (n_layers - 1) not in layer_indices:
            layer_indices.append(n_layers - 1)
    else:
        layer_indices = [-1] + list(range(n_layers))

    print(f"  Probing {len(layer_indices)} layers (stride={args.layer_stride})",
          file=sys.stderr, flush=True)

    # Build dataset
    banner("BUILDING PROBING DATASET")
    data_by_layer, n_labeled, n_skipped = build_probing_dataset(
        model, tokenizer, layer_indices, labeled_data,
    )
    print(f"\n  Labeled: {n_labeled}  Skipped sentences: {n_skipped}",
          file=sys.stderr, flush=True)

    if 0 in data_by_layer:
        X, y = data_by_layer[0]
        print(f"  Dataset shape: X={X.shape}  y={y.shape}", file=sys.stderr)
        for cls, cnt in sorted(Counter(y).items()):
            print(f"    {cls:8s}: {cnt}", file=sys.stderr)

    # Free model memory
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # ── Train linear probes ───────────────────────────────────
    banner("TRAINING LINEAR PROBES (per layer)")
    baseline_acc = max(label_counts.values()) / sum(label_counts.values())
    print(f"  Method: Logistic Regression, 5-fold CV", file=sys.stderr)
    print(f"  Baseline (most frequent): {baseline_acc:.0%}\n", file=sys.stderr, flush=True)

    layer_accuracies: dict[int, dict] = {}

    for L in sorted(data_by_layer.keys()):
        X, y = data_by_layer[L]
        if len(set(y)) < 2:
            print(f"  L{L:3d}: SKIP (only 1 class)", file=sys.stderr)
            continue

        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        clf = LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs")
        try:
            scores = cross_val_score(clf, X, y_enc, cv=5, scoring="accuracy")
            mean_acc = scores.mean()
            std_acc = scores.std()
        except Exception as e:
            print(f"  L{L:3d}: ERROR — {e}", file=sys.stderr)
            continue

        layer_accuracies[L] = {"mean": float(mean_acc), "std": float(std_acc)}

        label = "embed" if L == -1 else f"L{L}"
        bar = "█" * int(mean_acc * 50) + "░" * (50 - int(mean_acc * 50))
        print(f"  {label:6s}: {bar} {mean_acc:.1%} ±{std_acc:.1%}", file=sys.stderr, flush=True)

    # ── Per-class accuracy at key layers ──────────────────────
    banner("PER-CLASS ACCURACY AT KEY LAYERS")

    # Pick embed, early, 25%, 50%, 75%, final
    key_layers = [-1, 0]
    quartiles = [n_layers // 4, n_layers // 2, 3 * n_layers // 4, n_layers - 1]
    for q in quartiles:
        # Find closest probed layer
        closest = min(data_by_layer.keys(), key=lambda x: abs(x - q))
        if closest not in key_layers:
            key_layers.append(closest)
    key_layers.sort()

    for L in key_layers:
        if L not in data_by_layer:
            continue
        X, y = data_by_layer[L]
        le = LabelEncoder()
        y_enc = le.fit_transform(y)

        clf = LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs")
        clf.fit(X, y_enc)
        preds = clf.predict(X)

        label = "embed" if L == -1 else f"L{L}"
        print(f"\n  {label}:", file=sys.stderr)
        for cls_idx, cls_name in enumerate(le.classes_):
            mask = y == cls_name
            if mask.sum() == 0:
                continue
            cls_acc = (preds[mask] == cls_idx).mean()
            n = mask.sum()
            print(f"    {cls_name:8s}: {cls_acc:.0%} ({n} tokens)", file=sys.stderr)

    # ── Summary ───────────────────────────────────────────────
    elapsed = time.time() - start
    banner(f"SUMMARY — {elapsed:.0f}s")

    if layer_accuracies:
        # Find peak
        peak_layer = max(layer_accuracies, key=lambda k: layer_accuracies[k]["mean"])
        peak_acc = layer_accuracies[peak_layer]["mean"]
        peak_label = "embed" if peak_layer == -1 else f"L{peak_layer}"
        print(f"  Peak type decodability: {peak_label} at {peak_acc:.1%}", file=sys.stderr)

        # Layer progression
        embed_acc = layer_accuracies.get(-1, {}).get("mean", 0)
        l0_acc = layer_accuracies.get(0, {}).get("mean", 0)

        print(f"\n  Type decodability progression:", file=sys.stderr)
        print(f"    Embedding:   {embed_acc:.1%}", file=sys.stderr)
        print(f"    L0:          {l0_acc:.1%}  Δ={l0_acc-embed_acc:+.1%}", file=sys.stderr)

        # Report every 8th layer or quartile
        for L in sorted(layer_accuracies.keys()):
            if L <= 0:
                continue
            if L % max(1, n_layers // 8) == 0 or L == n_layers - 1:
                acc = layer_accuracies[L]["mean"]
                print(f"    L{L:<3d}:        {acc:.1%}  Δ from embed={acc-embed_acc:+.1%}",
                      file=sys.stderr)

        # Interpretation
        mid_layer = n_layers // 2
        mid_acc_key = min(layer_accuracies.keys(), key=lambda x: abs(x - mid_layer))
        mid_acc = layer_accuracies.get(mid_acc_key, {}).get("mean", 0)
        final_acc = layer_accuracies.get(max(layer_accuracies.keys()), {}).get("mean", 0)

        print(f"\n  Interpretation:", file=sys.stderr)
        if embed_acc > 0.8:
            print(f"    Types are LEXICAL — {embed_acc:.0%} in embeddings alone", file=sys.stderr)
        elif l0_acc > 0.8:
            print(f"    Types COMPUTED in L0 — {embed_acc:.0%}→{l0_acc:.0%}", file=sys.stderr)
        else:
            print(f"    Types emerge gradually — embed={embed_acc:.0%}, L0={l0_acc:.0%}", file=sys.stderr)

        if final_acc < embed_acc - 0.05:
            print(f"    ⚠  Types DEGRADE in late layers ({embed_acc:.0%}→{final_acc:.0%})",
                  file=sys.stderr)
            print(f"       Late layers transform type geometry for prediction", file=sys.stderr)
        elif mid_acc > embed_acc + 0.05:
            print(f"    Types REFINED at depth (embed={embed_acc:.0%}→L{mid_acc_key}={mid_acc:.0%})",
                  file=sys.stderr)

    # ── Save ──────────────────────────────────────────────────
    save_data = {
        "timestamp": datetime.now(UTC).isoformat(),
        "elapsed_s": elapsed,
        "model": args.model,
        "n_layers": n_layers,
        "d_model": d_model,
        "n_sentences": len(labeled_data),
        "n_labeled_tokens": n_labeled,
        "n_skipped_sentences": n_skipped,
        "label_counts": dict(label_counts),
        "layer_stride": args.layer_stride,
        "layer_accuracies": {str(k): v for k, v in sorted(layer_accuracies.items())},
        "baseline_accuracy": baseline_acc,
    }

    save_path = results_dir / "type-probe-summary.json"
    save_path.write_text(json.dumps(save_data, indent=2, ensure_ascii=False))
    print(f"\n  Saved: {save_path}", file=sys.stderr)

    # ── Plot ──────────────────────────────────────────────────
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(1, 1, figsize=(14, 5))
        layers_sorted = sorted(layer_accuracies.keys())
        accs = [layer_accuracies[L]["mean"] for L in layers_sorted]
        stds = [layer_accuracies[L]["std"] for L in layers_sorted]
        labels = ["embed" if L == -1 else f"L{L}" for L in layers_sorted]

        x_pos = range(len(layers_sorted))
        ax.bar(x_pos, accs, yerr=stds, capsize=2, alpha=0.7, color="steelblue")
        ax.set_xticks(x_pos)
        ax.set_xticklabels(labels, rotation=90, fontsize=6)
        ax.set_ylabel("5-fold CV Accuracy")
        ax.set_title(f"Montague Type Decodability — {args.model}\n"
                     f"({len(labeled_data)} sentences, {n_labeled} tokens, "
                     f"baseline={baseline_acc:.0%})")
        ax.axhline(y=baseline_acc, color="red", linestyle="--", alpha=0.5, label="baseline")
        ax.legend()
        ax.set_ylim(0, 1.05)

        plot_path = results_dir / "type-decodability.png"
        fig.tight_layout()
        fig.savefig(str(plot_path), dpi=150)
        plt.close(fig)
        print(f"  Plot: {plot_path}", file=sys.stderr)
    except Exception as e:
        print(f"  Plot error: {e}", file=sys.stderr)

    print(f"\n  Done in {elapsed:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
