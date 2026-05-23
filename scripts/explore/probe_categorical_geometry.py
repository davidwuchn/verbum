#!/usr/bin/env python3
"""Categorical geometry probes — Qwen3-32B.

Four probes testing whether Qwen3-32B's residual stream encodes the
categorical / geometric structure predicted by compositional semantics:

  1. Curry-Howard  — Well-typed compositions occupy geometrically
     distinct regions from ill-typed ones. Linear classifier (LR, 5-fold
     CV) on concatenated adjacent-token residuals per layer.

  2. Adjunctions  — The encode (L2) ↔ decode (L56) relationship is more
     structured (lower-variance, lower-rank cross-correlation) than
     encode↔compress or compress↔decode.

  3. Hyperbolic Geometry — Residual norm correlates with syntactic depth,
     consistent with tree embeddings in hyperbolic space.

  4. Coherence  — Representations of the same noun converge across layers
     when the surface order of preceding adjectives is permuted (Mac Lane
     coherence: all diagram paths commute).

Architecture: Qwen3-32B — 64 layers, 64 heads, GQA(8 KV), d=5120, bf16.

Usage:
    uv run python scripts/explore/probe_categorical_geometry.py
    uv run python scripts/explore/probe_categorical_geometry.py --quick
    uv run python scripts/explore/probe_categorical_geometry.py --device cuda

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import numpy as np
import torch
from scipy import stats as scipy_stats
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import cross_val_score

MODEL = "Qwen/Qwen3-32B"
RESULTS_DIR = Path("results/categorical-geometry-qwen3-32b")

# Probe layers — early, mid-compress, mid-decode, final neighbourhood
PROBE_LAYERS = [0, 2, 8, 16, 32, 48, 56, 63]

# Zone layers for adjunction probe
ENCODE_LAYER = 2
COMPRESS_LAYER = 32
DECODE_LAYER = 56
FINAL_LAYER = 63

# ══════════════════════════════════════════════════════════════════════
# Probe 1 — Curry-Howard sentence data
# ══════════════════════════════════════════════════════════════════════

WELL_TYPED = [
    ("The dog runs.", [("The", "DET"), ("dog", "ENTITY"), ("runs", "PRED")]),
    ("Every cat sleeps.", [("Every", "QUANT"), ("cat", "ENTITY"), ("sleeps", "PRED")]),
    ("The tall man walks.", [("The", "DET"), ("tall", "MOD"), ("man", "ENTITY"), ("walks", "PRED")]),
    ("Alice quickly runs.", [("Alice", "ENTITY"), ("quickly", "MOD"), ("runs", "PRED")]),
    ("The bird flies south.", [("The", "DET"), ("bird", "ENTITY"), ("flies", "PRED"), ("south", "MOD")]),
    ("Some fish swim fast.", [("Some", "QUANT"), ("fish", "ENTITY"), ("swim", "PRED"), ("fast", "MOD")]),
    ("The old farmer walks slowly.", [("The", "DET"), ("old", "MOD"), ("farmer", "ENTITY"), ("walks", "PRED"), ("slowly", "MOD")]),
    ("Bob sees the cat.", [("Bob", "ENTITY"), ("sees", "REL"), ("the", "DET"), ("cat", "ENTITY")]),
    ("The teacher reads a book.", [("The", "DET"), ("teacher", "ENTITY"), ("reads", "REL"), ("a", "DET"), ("book", "ENTITY")]),
    ("Every student writes clearly.", [("Every", "QUANT"), ("student", "ENTITY"), ("writes", "PRED"), ("clearly", "MOD")]),
    ("The river flows gently.", [("The", "DET"), ("river", "ENTITY"), ("flows", "PRED"), ("gently", "MOD")]),
    ("A child laughs.", [("A", "DET"), ("child", "ENTITY"), ("laughs", "PRED")]),
    ("No bird flies backward.", [("No", "QUANT"), ("bird", "ENTITY"), ("flies", "PRED"), ("backward", "MOD")]),
    ("The engine roars loudly.", [("The", "DET"), ("engine", "ENTITY"), ("roars", "PRED"), ("loudly", "MOD")]),
    ("Most people sleep well.", [("Most", "QUANT"), ("people", "ENTITY"), ("sleep", "PRED"), ("well", "MOD")]),
]

ILL_TYPED = [
    ("Runs the dog.", [("Runs", "PRED"), ("the", "DET"), ("dog", "ENTITY")]),
    ("Sleeps every cat.", [("Sleeps", "PRED"), ("every", "QUANT"), ("cat", "ENTITY")]),
    ("Walks tall the man.", [("Walks", "PRED"), ("tall", "MOD"), ("the", "DET"), ("man", "ENTITY")]),
    ("Runs quickly Alice.", [("Runs", "PRED"), ("quickly", "MOD"), ("Alice", "ENTITY")]),
    ("South flies the bird.", [("South", "MOD"), ("flies", "PRED"), ("the", "DET"), ("bird", "ENTITY")]),
    ("Fast swim some fish.", [("Fast", "MOD"), ("swim", "PRED"), ("some", "QUANT"), ("fish", "ENTITY")]),
    ("Slowly walks old the farmer.", [("Slowly", "MOD"), ("walks", "PRED"), ("old", "MOD"), ("the", "DET"), ("farmer", "ENTITY")]),
    ("Cat the sees Bob.", [("Cat", "ENTITY"), ("the", "DET"), ("sees", "REL"), ("Bob", "ENTITY")]),
    ("Book a reads teacher the.", [("Book", "ENTITY"), ("a", "DET"), ("reads", "REL"), ("teacher", "ENTITY"), ("the", "DET")]),
    ("Clearly writes student every.", [("Clearly", "MOD"), ("writes", "PRED"), ("student", "ENTITY"), ("every", "QUANT")]),
    ("Gently flows river the.", [("Gently", "MOD"), ("flows", "PRED"), ("river", "ENTITY"), ("the", "DET")]),
    ("Laughs child a.", [("Laughs", "PRED"), ("child", "ENTITY"), ("a", "DET")]),
    ("Backward flies bird no.", [("Backward", "MOD"), ("flies", "PRED"), ("bird", "ENTITY"), ("no", "QUANT")]),
    ("Loudly roars engine the.", [("Loudly", "MOD"), ("roars", "PRED"), ("engine", "ENTITY"), ("the", "DET")]),
    ("Well sleep people most.", [("Well", "MOD"), ("sleep", "PRED"), ("people", "ENTITY"), ("most", "QUANT")]),
]

# ══════════════════════════════════════════════════════════════════════
# Probe 3 — Hyperbolic / syntactic depth data
# ══════════════════════════════════════════════════════════════════════

DEPTH_LABELED = [
    # (sentence, [(word, depth), ...])
    ("The cat runs.", [("The", 2), ("cat", 1), ("runs", 0)]),
    ("The big cat runs fast.", [("The", 3), ("big", 2), ("cat", 1), ("runs", 0), ("fast", 1)]),
    ("The very big cat runs.", [("The", 3), ("very", 3), ("big", 2), ("cat", 1), ("runs", 0)]),
    ("Alice sees the dog.", [("Alice", 1), ("sees", 0), ("the", 2), ("dog", 1)]),
    ("The old man sees the small cat.", [("The", 2), ("old", 2), ("man", 1), ("sees", 0), ("the", 2), ("small", 2), ("cat", 1)]),
    ("Every student reads a thick book.", [("Every", 2), ("student", 1), ("reads", 0), ("a", 2), ("thick", 2), ("book", 1)]),
    ("Bob quickly runs.", [("Bob", 1), ("quickly", 1), ("runs", 0)]),
    ("The child laughs loudly.", [("The", 2), ("child", 1), ("laughs", 0), ("loudly", 1)]),
    ("No tall man walks slowly.", [("No", 2), ("tall", 2), ("man", 1), ("walks", 0), ("slowly", 1)]),
    ("The river flows.", [("The", 2), ("river", 1), ("flows", 0)]),
    ("A very old farmer walks.", [("A", 3), ("very", 3), ("old", 2), ("farmer", 1), ("walks", 0)]),
    ("The singer dances and the bird flies.", [("The", 2), ("singer", 1), ("dances", 0), ("and", 0), ("the", 2), ("bird", 1), ("flies", 0)]),
    ("Most people think that the world is round.", [("Most", 2), ("people", 1), ("think", 0), ("that", 1), ("the", 3), ("world", 2), ("is", 1), ("round", 1)]),
    ("The teacher says the student reads.", [("The", 2), ("teacher", 1), ("says", 0), ("the", 2), ("student", 1), ("reads", 1)]),
    ("Every cat that runs sleeps.", [("Every", 2), ("cat", 1), ("that", 2), ("runs", 2), ("sleeps", 0)]),
]

# ══════════════════════════════════════════════════════════════════════
# Probe 4 — Coherence / adjective-order pairs
# ══════════════════════════════════════════════════════════════════════

COHERENCE_PAIRS = [
    # (sentence_a, sentence_b, shared_meaning_label, noun_word)
    ("The big red ball bounces.", "The red big ball bounces.", "big_red_ball", "ball"),
    ("The old stone wall stands.", "The stone old wall stands.", "old_stone_wall", "wall"),
    ("The bright blue sky shines.", "The blue bright sky shines.", "bright_blue_sky", "sky"),
    ("The long dark road stretches.", "The dark long road stretches.", "long_dark_road", "road"),
    ("The heavy iron door opens.", "The iron heavy door opens.", "heavy_iron_door", "door"),
    ("The small white cat sleeps.", "The white small cat sleeps.", "small_white_cat", "cat"),
    ("The tall green tree grows.", "The green tall tree grows.", "tall_green_tree", "tree"),
    ("The hot black coffee steams.", "The black hot coffee steams.", "hot_black_coffee", "coffee"),
    ("The cold fresh water flows.", "The fresh cold water flows.", "cold_fresh_water", "water"),
    ("The thin sharp knife cuts.", "The sharp thin knife cuts.", "thin_sharp_knife", "knife"),
]


# ══════════════════════════════════════════════════════════════════════
# Utility: banner
# ══════════════════════════════════════════════════════════════════════

def banner(msg: str) -> None:
    print(f"\n{'=' * 72}\n  {msg}\n{'=' * 72}\n", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Model loading (copied from probe_type_qwen3_32b.py)
# ══════════════════════════════════════════════════════════════════════

def load_model(model_name: str, device: str = "mps"):
    """Load Qwen3-32B in bf16 with eager attention (for hook compatibility)."""
    from transformers import AutoConfig, AutoModelForCausalLM, AutoTokenizer

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
    print(
        f"  Layers: {n_layers}  Heads: {n_heads}  KV heads: {n_kv}  d_model: {d_model}",
        file=sys.stderr,
        flush=True,
    )
    return model, tokenizer, config


# ══════════════════════════════════════════════════════════════════════
# Layer accessors (copied from probe_type_qwen3_32b.py)
# ══════════════════════════════════════════════════════════════════════

def get_transformer_layers(model):
    """Get the list of transformer layers from any HF model."""
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise ValueError(f"Cannot find transformer layers in {type(model).__name__}")


def get_embed_module(model):
    """Get the embedding module for pre-layer residual capture."""
    if hasattr(model, "model") and hasattr(model.model, "embed_tokens"):
        return model.model.embed_tokens
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "embed_in"):
        return model.gpt_neox.embed_in
    return None


# ══════════════════════════════════════════════════════════════════════
# Residual stream capture (copied from probe_type_qwen3_32b.py)
# ══════════════════════════════════════════════════════════════════════

def capture_residuals(
    model,
    tokenizer,
    text: str,
    layer_indices: list[int] | None = None,
) -> tuple[dict[int, np.ndarray], list[int]]:
    """Capture residual stream at specified layers.

    Returns:
        residuals : {layer_idx: np.array (seq_len, d_model)}
                    layer_idx=-1 is the embedding output.
        token_ids : list[int]
    """
    layers = get_transformer_layers(model)
    n_layers = len(layers)

    if layer_indices is None:
        layer_indices = list(range(n_layers))

    layer_set = set(layer_indices)
    residuals: dict[int, np.ndarray] = {}
    hooks: list = []

    embed_mod = get_embed_module(model)
    if embed_mod is not None and -1 in layer_set:
        def embed_hook(module, args, output):
            h = output[0] if isinstance(output, tuple) else output
            residuals[-1] = h[0].detach().cpu().float().numpy()

        hooks.append(embed_mod.register_forward_hook(embed_hook))

    for idx in layer_indices:
        if idx < 0:
            continue

        def make_hook(layer_idx):
            def hook_fn(module, args, output):
                h = output[0] if isinstance(output, tuple) else output
                residuals[layer_idx] = h[0].detach().cpu().float().numpy()

            return hook_fn

        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt")
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
# Token → word alignment (copied from probe_type_qwen3_32b.py)
# ══════════════════════════════════════════════════════════════════════

def align_tokens_to_labels(
    tokenizer,
    token_ids: list[int],
    word_labels: list[tuple[str, object]],
) -> list[tuple[int, object]]:
    """Align BPE tokens to word-level labels.

    Returns list of (token_idx, label) for the FIRST token of each word.
    """
    token_strs = [
        tokenizer.decode([tid], skip_special_tokens=False) for tid in token_ids
    ]

    aligned: list[tuple[int, object]] = []
    word_idx = 0
    consumed_chars = 0

    for tok_idx, tok_str in enumerate(token_strs):
        if word_idx >= len(word_labels):
            break

        word_text, word_label = word_labels[word_idx]
        tok_clean = tok_str.strip()

        if not tok_clean:
            continue

        if word_text.lower().startswith(tok_clean.lower()):
            aligned.append((tok_idx, word_label))
            consumed_chars += len(tok_clean)
            if consumed_chars >= len(word_text):
                word_idx += 1
                consumed_chars = 0
        elif tok_clean.lower().startswith(word_text.lower()):
            aligned.append((tok_idx, word_label))
            word_idx += 1
            consumed_chars = 0
        elif consumed_chars > 0:
            consumed_chars += len(tok_clean)
            if consumed_chars >= len(word_text):
                word_idx += 1
                consumed_chars = 0
        else:
            lower_word = word_text.lower()
            lower_tok = tok_clean.lower()
            if lower_tok in lower_word:
                aligned.append((tok_idx, word_label))
                consumed_chars = len(tok_clean)
                if consumed_chars >= len(word_text):
                    word_idx += 1
                    consumed_chars = 0

    return aligned


# ══════════════════════════════════════════════════════════════════════
# Shared cosine helper
# ══════════════════════════════════════════════════════════════════════

def cosine(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two 1-D vectors."""
    na = np.linalg.norm(a)
    nb = np.linalg.norm(b)
    if na == 0 or nb == 0:
        return 0.0
    return float(np.dot(a, b) / (na * nb))


# ══════════════════════════════════════════════════════════════════════
# Probe 1 — Curry-Howard
# ══════════════════════════════════════════════════════════════════════

def probe_curry_howard(
    model,
    tokenizer,
    layer_indices: list[int],
    well_typed: list,
    ill_typed: list,
) -> dict:
    """
    For each sentence, extract all adjacent-token pairs.
    Label each pair well-typed (1) or ill-typed (0).
    Build feature: concat(residual_i, residual_{i+1}) per layer.
    Train logistic regression (5-fold CV) per layer.
    Also compute mean cosine between adjacent pairs per layer.
    """
    banner("PROBE 1: Curry-Howard (type composition geometry)")

    # {layer: (list[feature], list[label])}
    layer_features: dict[int, tuple[list, list]] = {L: ([], []) for L in layer_indices}
    # {layer: (list[wt_cosines], list[it_cosines])}
    layer_cosines: dict[int, tuple[list, list]] = {L: ([], []) for L in layer_indices}

    def _process_group(sentences_with_labels: list, is_well_typed: bool) -> None:
        label = 1 if is_well_typed else 0
        group_name = "well-typed" if is_well_typed else "ill-typed"
        for sent_idx, (sent, word_labels) in enumerate(sentences_with_labels):
            print(
                f"    [{group_name}] {sent_idx + 1}/{len(sentences_with_labels)}: {sent[:50]}",
                file=sys.stderr,
                flush=True,
            )
            try:
                residuals, token_ids = capture_residuals(model, tokenizer, sent, layer_indices)
                aligned = align_tokens_to_labels(tokenizer, token_ids, word_labels)
            except Exception as e:
                print(f"      ⚠  capture failed: {e}", file=sys.stderr)
                continue

            if len(aligned) < 2:
                print("      ⚠  fewer than 2 aligned tokens, skipping", file=sys.stderr)
                continue

            tok_indices = [t for t, _ in aligned]

            for i in range(len(tok_indices) - 1):
                ti, tj = tok_indices[i], tok_indices[i + 1]
                for L in layer_indices:
                    if L not in residuals:
                        continue
                    mat = residuals[L]
                    if ti >= mat.shape[0] or tj >= mat.shape[0]:
                        continue
                    vi = mat[ti]
                    vj = mat[tj]
                    feat = np.concatenate([vi, vj])
                    layer_features[L][0].append(feat)
                    layer_features[L][1].append(label)
                    cos = cosine(vi, vj)
                    if is_well_typed:
                        layer_cosines[L][0].append(cos)
                    else:
                        layer_cosines[L][1].append(cos)

            del residuals
            gc.collect()

    _process_group(well_typed, is_well_typed=True)
    _process_group(ill_typed, is_well_typed=False)

    # ── Train classifier per layer ──
    results_by_layer: dict[str, dict] = {}

    for L in sorted(layer_indices):
        feats, labels = layer_features[L]
        if not feats or len(set(labels)) < 2:
            print(f"  L{L:3d}: SKIP (insufficient data)", file=sys.stderr)
            continue

        X = np.array(feats)
        y = np.array(labels)

        clf = LogisticRegression(max_iter=2000, C=1.0, solver="lbfgs")
        try:
            n_splits = min(5, min(np.bincount(y)))
            if n_splits < 2:
                scores = np.array([0.5])
            else:
                scores = cross_val_score(clf, X, y, cv=n_splits, scoring="accuracy")
        except Exception as e:
            print(f"  L{L:3d}: classifier error — {e}", file=sys.stderr)
            continue

        wt_cos = layer_cosines[L][0]
        it_cos = layer_cosines[L][1]

        entry = {
            "accuracy_mean": float(scores.mean()),
            "accuracy_std": float(scores.std()),
            "n_pairs": int(len(feats)),
            "n_well_typed_pairs": int(sum(1 for v in labels if v == 1)),
            "n_ill_typed_pairs": int(sum(1 for v in labels if v == 0)),
            "mean_cosine_well_typed": float(np.mean(wt_cos)) if wt_cos else None,
            "mean_cosine_ill_typed": float(np.mean(it_cos)) if it_cos else None,
        }
        results_by_layer[str(L)] = entry

        lbl = "embed" if L == -1 else f"L{L}"
        bar = "█" * int(scores.mean() * 40) + "░" * (40 - int(scores.mean() * 40))
        cos_gap = (
            f"  cos Δ={entry['mean_cosine_well_typed'] - entry['mean_cosine_ill_typed']:+.3f}"
            if entry["mean_cosine_well_typed"] is not None and entry["mean_cosine_ill_typed"] is not None
            else ""
        )
        print(
            f"  {lbl:6s}: {bar} acc={scores.mean():.1%} ±{scores.std():.1%}{cos_gap}",
            file=sys.stderr,
            flush=True,
        )

    return {
        "probe": "curry_howard",
        "description": "Well-typed vs ill-typed adjacent-pair residual classifier",
        "layer_indices": layer_indices,
        "results_by_layer": results_by_layer,
    }


# ══════════════════════════════════════════════════════════════════════
# Probe 2 — Adjunctions
# ══════════════════════════════════════════════════════════════════════

def probe_adjunctions(
    model,
    tokenizer,
    well_typed: list,
) -> dict:
    """
    For each token in each well-typed sentence, compute pairwise cosine
    similarities between zone layers and measure cross-zone mapping rank.
    Zone layers: ENCODE=L2, COMPRESS=L32, DECODE=L56, FINAL=L63.
    """
    banner("PROBE 2: Adjunctions (encode↔decode relationship)")

    zone_layers = [ENCODE_LAYER, COMPRESS_LAYER, DECODE_LAYER, FINAL_LAYER]

    # Per-token cosines per zone pair
    cos_enc_dec: list[float] = []     # L2 ↔ L56
    cos_enc_comp: list[float] = []    # L2 ↔ L32
    cos_comp_dec: list[float] = []    # L32 ↔ L56
    cos_enc_final: list[float] = []   # L2 ↔ L63

    # Collect raw residuals per zone for SVD/linear regression
    vecs_enc: list[np.ndarray] = []
    vecs_comp: list[np.ndarray] = []
    vecs_dec: list[np.ndarray] = []

    for sent_idx, (sent, word_labels) in enumerate(well_typed):
        print(
            f"    {sent_idx + 1}/{len(well_typed)}: {sent[:60]}",
            file=sys.stderr,
            flush=True,
        )
        try:
            residuals, token_ids = capture_residuals(model, tokenizer, sent, zone_layers)
            aligned = align_tokens_to_labels(tokenizer, token_ids, word_labels)
        except Exception as e:
            print(f"      ⚠  capture failed: {e}", file=sys.stderr)
            continue

        for tok_idx, _ in aligned:
            missing = [L for L in zone_layers if L not in residuals or tok_idx >= residuals[L].shape[0]]
            if missing:
                continue

            ve = residuals[ENCODE_LAYER][tok_idx]
            vc = residuals[COMPRESS_LAYER][tok_idx]
            vd = residuals[DECODE_LAYER][tok_idx]
            vf = residuals[FINAL_LAYER][tok_idx]

            cos_enc_dec.append(cosine(ve, vd))
            cos_enc_comp.append(cosine(ve, vc))
            cos_comp_dec.append(cosine(vc, vd))
            cos_enc_final.append(cosine(ve, vf))

            vecs_enc.append(ve)
            vecs_comp.append(vc)
            vecs_dec.append(vd)

        del residuals
        gc.collect()

    if not vecs_enc:
        return {"probe": "adjunctions", "error": "no aligned tokens found"}

    # ── Summary statistics ──
    def _stats(vals: list[float]) -> dict:
        a = np.array(vals)
        return {
            "mean": float(a.mean()),
            "std": float(a.std()),
            "median": float(np.median(a)),
            "n": len(vals),
        }

    stats_enc_dec = _stats(cos_enc_dec)
    stats_enc_comp = _stats(cos_enc_comp)
    stats_comp_dec = _stats(cos_comp_dec)
    stats_enc_final = _stats(cos_enc_final)

    print(f"\n  Zone-pair cosine statistics:", file=sys.stderr)
    for name, st in [
        ("L2↔L56 (enc↔dec)", stats_enc_dec),
        ("L2↔L32 (enc↔comp)", stats_enc_comp),
        ("L32↔L56 (comp↔dec)", stats_comp_dec),
        ("L2↔L63 (enc↔final)", stats_enc_final),
    ]:
        print(
            f"    {name:25s}: mean={st['mean']:+.3f}  std={st['std']:.3f}  n={st['n']}",
            file=sys.stderr,
        )

    # ── SVD of cross-correlation matrix M = Vdec^T Venc / n ──
    # Low rank M → structured (adjunction-like) transform enc→dec
    E = np.array(vecs_enc)   # (N, d)
    C = np.array(vecs_comp)
    D = np.array(vecs_dec)

    def _cross_corr_svd(A: np.ndarray, B: np.ndarray, tag: str) -> dict:
        """SVD of cross-correlation A^T B / N."""
        n = A.shape[0]
        M = (A.T @ B) / n  # (d, d)
        # Use randomised SVD via numpy — full SVD is expensive for d=5120
        # We just compute the top-k singular values
        k = min(50, n - 1, M.shape[0])
        try:
            U, s, Vt = np.linalg.svd(M, full_matrices=False, compute_uv=True)
            top_k = s[:k]
        except Exception:
            top_k = np.zeros(k)
        total_var = float(np.sum(s ** 2)) if len(s) > 0 else 1.0
        top5_var = float(np.sum(top_k[:5] ** 2)) / (total_var + 1e-12)
        top20_var = float(np.sum(top_k[:20] ** 2)) / (total_var + 1e-12)
        print(
            f"    SVD {tag}: top-5 var={top5_var:.3f}  top-20 var={top20_var:.3f}  "
            f"singular[0]={top_k[0]:.2f}  singular[4]={top_k[min(4,len(top_k)-1)]:.2f}",
            file=sys.stderr,
        )
        return {
            "top5_variance_explained": float(top5_var),
            "top20_variance_explained": float(top20_var),
            "singular_values_top10": [float(v) for v in top_k[:10]],
        }

    print(f"\n  Cross-correlation SVD (adjunction rank check):", file=sys.stderr)
    svd_enc_dec = _cross_corr_svd(E, D, "L2→L56")
    svd_enc_comp = _cross_corr_svd(E, C, "L2→L32")
    svd_comp_dec = _cross_corr_svd(C, D, "L32→L56")

    # ── Linear regression R² L2→L56 vs L2→L32 ──
    def _r2(A: np.ndarray, B: np.ndarray) -> float:
        """Mean per-dimension R² of linear regression A→B (via pseudoinverse)."""
        try:
            W, _, _, _ = np.linalg.lstsq(A, B, rcond=None)
            B_pred = A @ W
            ss_res = np.sum((B - B_pred) ** 2, axis=0)
            ss_tot = np.sum((B - B.mean(axis=0)) ** 2, axis=0)
            r2_per_dim = 1.0 - ss_res / (ss_tot + 1e-12)
            return float(r2_per_dim.mean())
        except Exception:
            return float("nan")

    r2_enc_dec = _r2(E, D)
    r2_enc_comp = _r2(E, C)
    r2_comp_dec = _r2(C, D)
    print(f"\n  Linear regression R² (mean per-dim):", file=sys.stderr)
    print(f"    L2→L56: {r2_enc_dec:.4f}", file=sys.stderr)
    print(f"    L2→L32: {r2_enc_comp:.4f}", file=sys.stderr)
    print(f"    L32→L56: {r2_comp_dec:.4f}", file=sys.stderr)

    return {
        "probe": "adjunctions",
        "description": "Zone-pair cosine similarity and cross-zone mapping rank",
        "n_tokens": len(vecs_enc),
        "cosine_stats": {
            "enc_dec_L2_L56": stats_enc_dec,
            "enc_comp_L2_L32": stats_enc_comp,
            "comp_dec_L32_L56": stats_comp_dec,
            "enc_final_L2_L63": stats_enc_final,
        },
        "svd": {
            "enc_dec_L2_L56": svd_enc_dec,
            "enc_comp_L2_L32": svd_enc_comp,
            "comp_dec_L32_L56": svd_comp_dec,
        },
        "r2": {
            "enc_dec_L2_L56": r2_enc_dec,
            "enc_comp_L2_L32": r2_enc_comp,
            "comp_dec_L32_L56": r2_comp_dec,
        },
        # Raw cosine lists for plotting
        "_raw_cosines": {
            "enc_dec": cos_enc_dec,
            "enc_comp": cos_enc_comp,
            "comp_dec": cos_comp_dec,
            "enc_final": cos_enc_final,
        },
    }


# ══════════════════════════════════════════════════════════════════════
# Probe 3 — Hyperbolic Geometry
# ══════════════════════════════════════════════════════════════════════

def probe_hyperbolic(
    model,
    tokenizer,
    layer_indices: list[int],
    depth_labeled: list,
) -> dict:
    """
    Collect (norm_of_residual, syntactic_depth) pairs for each token
    at each probe layer. Compute Spearman correlation per layer.
    """
    banner("PROBE 3: Hyperbolic Geometry (norm vs syntactic depth)")

    # {layer: (list[norm], list[depth])}
    layer_data: dict[int, tuple[list, list]] = {L: ([], []) for L in layer_indices}

    for sent_idx, (sent, word_depth_labels) in enumerate(depth_labeled):
        print(
            f"    {sent_idx + 1}/{len(depth_labeled)}: {sent[:60]}",
            file=sys.stderr,
            flush=True,
        )
        try:
            residuals, token_ids = capture_residuals(model, tokenizer, sent, layer_indices)
            aligned = align_tokens_to_labels(tokenizer, token_ids, word_depth_labels)
        except Exception as e:
            print(f"      ⚠  capture failed: {e}", file=sys.stderr)
            continue

        for tok_idx, depth in aligned:
            for L in layer_indices:
                if L not in residuals or tok_idx >= residuals[L].shape[0]:
                    continue
                norm = float(np.linalg.norm(residuals[L][tok_idx]))
                layer_data[L][0].append(norm)
                layer_data[L][1].append(int(depth))

        del residuals
        gc.collect()

    results_by_layer: dict[str, dict] = {}

    print(f"\n  Spearman(norm, depth) per layer:", file=sys.stderr)
    for L in sorted(layer_indices):
        norms, depths = layer_data[L]
        if len(norms) < 4:
            print(f"  L{L:3d}: SKIP (n={len(norms)})", file=sys.stderr)
            continue

        try:
            rho, pval = scipy_stats.spearmanr(norms, depths)
        except Exception:
            rho, pval = float("nan"), float("nan")

        entry = {
            "spearman_rho": float(rho),
            "spearman_pval": float(pval),
            "n": len(norms),
            "mean_norm": float(np.mean(norms)),
            "std_norm": float(np.std(norms)),
            "norm_by_depth": {},
        }

        # Aggregate mean norm per depth bin
        depth_arr = np.array(depths)
        norm_arr = np.array(norms)
        for d in sorted(set(depths)):
            mask = depth_arr == d
            entry["norm_by_depth"][str(d)] = {
                "mean": float(norm_arr[mask].mean()),
                "n": int(mask.sum()),
            }

        results_by_layer[str(L)] = entry
        lbl = "embed" if L == -1 else f"L{L}"
        sig = "★" if pval < 0.05 else " "
        print(
            f"  {lbl:6s}: ρ={rho:+.3f}  p={pval:.4f} {sig}  n={len(norms)}  mean_norm={np.mean(norms):.2f}",
            file=sys.stderr,
            flush=True,
        )

    return {
        "probe": "hyperbolic",
        "description": "Spearman correlation between residual norm and syntactic depth",
        "layer_indices": layer_indices,
        "results_by_layer": results_by_layer,
    }


# ══════════════════════════════════════════════════════════════════════
# Probe 4 — Coherence
# ══════════════════════════════════════════════════════════════════════

def _find_noun_token(
    tokenizer,
    token_ids: list[int],
    noun_word: str,
) -> int | None:
    """Return the index of the first token that starts the noun word."""
    token_strs = [
        tokenizer.decode([tid], skip_special_tokens=False) for tid in token_ids
    ]
    target_lower = noun_word.lower()
    for i, ts in enumerate(token_strs):
        ts_clean = ts.strip().lower()
        if ts_clean == target_lower or target_lower.startswith(ts_clean) and ts_clean:
            return i
    # Fallback: check if any token contains the noun
    for i, ts in enumerate(token_strs):
        if noun_word.lower() in ts.lower():
            return i
    return None


def probe_coherence(
    model,
    tokenizer,
    layer_indices: list[int],
    coherence_pairs: list,
) -> dict:
    """
    For each (sent_a, sent_b, label, noun) pair, capture noun-token residuals
    at each probe layer. Compute cosine similarity between the two noun
    representations at each layer.
    If coherence holds: cosine should increase monotonically across layers.
    """
    banner("PROBE 4: Coherence (parse-path convergence)")

    # {layer: list[cosine]}
    layer_cosines: dict[int, list[float]] = {L: [] for L in layer_indices}
    pair_details: list[dict] = []

    for pair_idx, (sent_a, sent_b, label, noun_word) in enumerate(coherence_pairs):
        print(
            f"    {pair_idx + 1}/{len(coherence_pairs)}: {label!r}  A='{sent_a}'",
            file=sys.stderr,
            flush=True,
        )
        try:
            res_a, tids_a = capture_residuals(model, tokenizer, sent_a, layer_indices)
            res_b, tids_b = capture_residuals(model, tokenizer, sent_b, layer_indices)
        except Exception as e:
            print(f"      ⚠  capture failed: {e}", file=sys.stderr)
            continue

        ni_a = _find_noun_token(tokenizer, tids_a, noun_word)
        ni_b = _find_noun_token(tokenizer, tids_b, noun_word)

        if ni_a is None or ni_b is None:
            print(
                f"      ⚠  could not find noun '{noun_word}' in one/both sentences",
                file=sys.stderr,
            )
            del res_a, res_b
            gc.collect()
            continue

        pair_cosines: dict[str, float] = {}
        for L in layer_indices:
            if L not in res_a or L not in res_b:
                continue
            if ni_a >= res_a[L].shape[0] or ni_b >= res_b[L].shape[0]:
                continue
            c = cosine(res_a[L][ni_a], res_b[L][ni_b])
            layer_cosines[L].append(c)
            pair_cosines[str(L)] = c

        pair_details.append(
            {
                "label": label,
                "sent_a": sent_a,
                "sent_b": sent_b,
                "noun": noun_word,
                "noun_token_idx_a": ni_a,
                "noun_token_idx_b": ni_b,
                "cosines_by_layer": pair_cosines,
            }
        )

        del res_a, res_b
        gc.collect()

    # ── Aggregate per layer ──
    mean_cosines: dict[str, float] = {}
    std_cosines: dict[str, float] = {}

    print(f"\n  Mean noun cosine per layer:", file=sys.stderr)
    for L in sorted(layer_indices):
        vals = layer_cosines[L]
        if not vals:
            continue
        mc = float(np.mean(vals))
        sc = float(np.std(vals))
        mean_cosines[str(L)] = mc
        std_cosines[str(L)] = sc
        lbl = "embed" if L == -1 else f"L{L}"
        bar = "█" * int(mc * 40) + "░" * (40 - min(40, int(mc * 40)))
        print(
            f"  {lbl:6s}: {bar} {mc:.3f} ±{sc:.3f}  n={len(vals)}",
            file=sys.stderr,
            flush=True,
        )

    # ── Compute convergence: Δ from first to last probed layer ──
    sorted_layer_keys = sorted(mean_cosines.keys(), key=lambda x: int(x))
    if len(sorted_layer_keys) >= 2:
        first_val = mean_cosines[sorted_layer_keys[0]]
        last_val = mean_cosines[sorted_layer_keys[-1]]
        convergence_delta = last_val - first_val
        print(
            f"\n  Convergence Δ (final − first): {convergence_delta:+.3f}",
            file=sys.stderr,
        )
        if convergence_delta > 0.05:
            print("  → Representations CONVERGE across layers (coherence supported)", file=sys.stderr)
        elif convergence_delta < -0.05:
            print("  → Representations DIVERGE across layers (against coherence)", file=sys.stderr)
        else:
            print("  → Minimal convergence (inconclusive)", file=sys.stderr)
    else:
        convergence_delta = None

    return {
        "probe": "coherence",
        "description": "Noun cosine similarity across adjective-order-permuted pairs",
        "layer_indices": layer_indices,
        "mean_cosines_by_layer": mean_cosines,
        "std_cosines_by_layer": std_cosines,
        "convergence_delta": convergence_delta,
        "pair_details": pair_details,
    }


# ══════════════════════════════════════════════════════════════════════
# Plotting
# ══════════════════════════════════════════════════════════════════════

def make_plots(results: dict, results_dir: Path) -> None:
    """Generate all four probe plots."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available — skipping plots", file=sys.stderr)
        return

    layer_indices = results.get("config", {}).get("probe_layers", PROBE_LAYERS)

    # ── Plot 1: Curry-Howard classification accuracy ──
    try:
        ch = results.get("curry_howard", {})
        rbl = ch.get("results_by_layer", {})
        if rbl:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            layers_sorted = sorted(rbl.keys(), key=lambda x: int(x))
            x_pos = range(len(layers_sorted))
            labels_x = [f"L{k}" for k in layers_sorted]
            accs = [rbl[k]["accuracy_mean"] for k in layers_sorted]
            stds = [rbl[k]["accuracy_std"] for k in layers_sorted]

            ax = axes[0]
            ax.bar(x_pos, accs, yerr=stds, capsize=3, alpha=0.75, color="steelblue")
            ax.axhline(0.5, color="red", linestyle="--", alpha=0.5, label="chance (50%)")
            ax.set_xticks(list(x_pos))
            ax.set_xticklabels(labels_x, rotation=45, ha="right")
            ax.set_ylabel("5-fold CV Accuracy")
            ax.set_title("Curry-Howard: Well-typed vs Ill-typed\n(LR on concat residual pairs)")
            ax.set_ylim(0, 1.05)
            ax.legend()

            # Adjacent cosine gap
            wt_cos = [rbl[k]["mean_cosine_well_typed"] for k in layers_sorted
                      if rbl[k]["mean_cosine_well_typed"] is not None]
            it_cos = [rbl[k]["mean_cosine_ill_typed"] for k in layers_sorted
                      if rbl[k]["mean_cosine_ill_typed"] is not None]
            layers_with_cos = [k for k in layers_sorted
                                if rbl[k]["mean_cosine_well_typed"] is not None]
            x_cos = range(len(layers_with_cos))

            ax2 = axes[1]
            ax2.plot(list(x_cos), wt_cos, "o-", color="green", label="well-typed adj cosine")
            ax2.plot(list(x_cos), it_cos, "s-", color="orange", label="ill-typed adj cosine")
            ax2.set_xticks(list(x_cos))
            ax2.set_xticklabels([f"L{k}" for k in layers_with_cos], rotation=45, ha="right")
            ax2.set_ylabel("Mean cosine (adjacent token pair)")
            ax2.set_title("Adjacent-pair cosine: well-typed vs ill-typed")
            ax2.legend()

            fig.tight_layout()
            path = results_dir / "curry_howard_accuracy.png"
            fig.savefig(str(path), dpi=150)
            plt.close(fig)
            print(f"  Plot: {path}", file=sys.stderr)
    except Exception as e:
        print(f"  Plot 1 error: {e}", file=sys.stderr)

    # ── Plot 2: Adjunction cross-zone distributions ──
    try:
        adj = results.get("adjunctions", {})
        raw = adj.get("_raw_cosines", {})
        if raw:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            names = ["enc_dec", "enc_comp", "comp_dec", "enc_final"]
            nice = ["L2↔L56 (enc↔dec)", "L2↔L32 (enc↔comp)",
                    "L32↔L56 (comp↔dec)", "L2↔L63 (enc↔final)"]
            colors = ["steelblue", "darkorange", "green", "purple"]

            ax = axes[0]
            for nm, label, col in zip(names, nice, colors):
                data = raw.get(nm, [])
                if data:
                    ax.hist(data, bins=20, alpha=0.5, label=label, color=col, density=True)
            ax.set_xlabel("Cosine similarity")
            ax.set_ylabel("Density")
            ax.set_title("Adjunction: cross-zone cosine distributions")
            ax.legend(fontsize=8)

            ax2 = axes[1]
            zone_means = [
                adj.get("cosine_stats", {}).get(k, {}).get("mean", 0)
                for k in ["enc_dec_L2_L56", "enc_comp_L2_L32",
                          "comp_dec_L32_L56", "enc_final_L2_L63"]
            ]
            zone_stds = [
                adj.get("cosine_stats", {}).get(k, {}).get("std", 0)
                for k in ["enc_dec_L2_L56", "enc_comp_L2_L32",
                          "comp_dec_L32_L56", "enc_final_L2_L63"]
            ]
            xlabels = ["enc↔dec\nL2-L56", "enc↔comp\nL2-L32",
                       "comp↔dec\nL32-L56", "enc↔final\nL2-L63"]
            ax2.bar(range(4), zone_means, yerr=zone_stds, capsize=5,
                    color=colors, alpha=0.8)
            ax2.set_xticks(range(4))
            ax2.set_xticklabels(xlabels)
            ax2.set_ylabel("Mean cosine similarity")
            ax2.set_title("Cross-zone mean cosine (adjunction check)")
            r2 = adj.get("r2", {})
            subtitle = (
                f"R²: enc→dec={r2.get('enc_dec_L2_L56', float('nan')):.3f}  "
                f"enc→comp={r2.get('enc_comp_L2_L32', float('nan')):.3f}  "
                f"comp→dec={r2.get('comp_dec_L32_L56', float('nan')):.3f}"
            )
            ax2.set_xlabel(subtitle, fontsize=8)

            fig.tight_layout()
            path = results_dir / "adjunction_cross_zone.png"
            fig.savefig(str(path), dpi=150)
            plt.close(fig)
            print(f"  Plot: {path}", file=sys.stderr)
    except Exception as e:
        print(f"  Plot 2 error: {e}", file=sys.stderr)

    # ── Plot 3: Hyperbolic — norm vs depth correlation per layer ──
    try:
        hyp = results.get("hyperbolic", {})
        rbl = hyp.get("results_by_layer", {})
        if rbl:
            fig, axes = plt.subplots(1, 2, figsize=(14, 5))

            layers_sorted = sorted(rbl.keys(), key=lambda x: int(x))
            rhos = [rbl[k]["spearman_rho"] for k in layers_sorted]
            pvals = [rbl[k]["spearman_pval"] for k in layers_sorted]
            x_pos = range(len(layers_sorted))
            labels_x = [f"L{k}" for k in layers_sorted]

            ax = axes[0]
            bar_colors = ["steelblue" if p < 0.05 else "lightsteelblue" for p in pvals]
            ax.bar(x_pos, rhos, color=bar_colors, alpha=0.8)
            ax.axhline(0, color="black", linewidth=0.5)
            ax.set_xticks(list(x_pos))
            ax.set_xticklabels(labels_x, rotation=45, ha="right")
            ax.set_ylabel("Spearman ρ (norm vs depth)")
            ax.set_title("Hyperbolic Geometry: norm–depth correlation\n(blue = p<0.05)")
            ax.set_ylim(-1, 1)

            # Mean norm by depth for a representative mid layer
            mid_key = layers_sorted[len(layers_sorted) // 2]
            mid_entry = rbl[mid_key]
            depth_means = mid_entry.get("norm_by_depth", {})
            if depth_means:
                depth_vals = sorted(depth_means.keys(), key=lambda x: int(x))
                mean_norms = [depth_means[d]["mean"] for d in depth_vals]
                ax2 = axes[1]
                ax2.bar(range(len(depth_vals)), mean_norms, color="steelblue", alpha=0.8)
                ax2.set_xticks(range(len(depth_vals)))
                ax2.set_xticklabels([f"depth {d}" for d in depth_vals], rotation=45, ha="right")
                ax2.set_ylabel("Mean residual norm")
                ax2.set_title(f"Mean norm by syntactic depth — L{mid_key}")

            fig.tight_layout()
            path = results_dir / "hyperbolic_norm_depth.png"
            fig.savefig(str(path), dpi=150)
            plt.close(fig)
            print(f"  Plot: {path}", file=sys.stderr)
    except Exception as e:
        print(f"  Plot 3 error: {e}", file=sys.stderr)

    # ── Plot 4: Coherence convergence ──
    try:
        coh = results.get("coherence", {})
        mc = coh.get("mean_cosines_by_layer", {})
        sc = coh.get("std_cosines_by_layer", {})
        if mc:
            fig, ax = plt.subplots(figsize=(10, 5))
            layers_sorted = sorted(mc.keys(), key=lambda x: int(x))
            x_pos = range(len(layers_sorted))
            means = [mc[k] for k in layers_sorted]
            stds = [sc.get(k, 0) for k in layers_sorted]
            labels_x = [f"L{k}" for k in layers_sorted]

            ax.errorbar(list(x_pos), means, yerr=stds, fmt="o-",
                        color="steelblue", capsize=4, linewidth=2, markersize=6)
            ax.fill_between(
                list(x_pos),
                [m - s for m, s in zip(means, stds)],
                [m + s for m, s in zip(means, stds)],
                alpha=0.2, color="steelblue",
            )
            ax.set_xticks(list(x_pos))
            ax.set_xticklabels(labels_x, rotation=45, ha="right")
            ax.set_ylabel("Mean cosine similarity (noun token)")
            ax.set_title("Coherence: noun convergence across adjective-order permutations\n"
                         "(should increase → if coherence holds)")
            delta = coh.get("convergence_delta")
            if delta is not None:
                ax.set_xlabel(f"Convergence Δ (last−first) = {delta:+.3f}")

            fig.tight_layout()
            path = results_dir / "coherence_convergence.png"
            fig.savefig(str(path), dpi=150)
            plt.close(fig)
            print(f"  Plot: {path}", file=sys.stderr)
    except Exception as e:
        print(f"  Plot 4 error: {e}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Categorical geometry probes for Qwen3-32B"
    )
    parser.add_argument("--model", default=MODEL, help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Use fewer sentences for fast testing (5 per list)",
    )
    parser.add_argument("--output", default=None, help="Output directory override")
    args = parser.parse_args()

    start = time.time()
    results_dir = Path(args.output) if args.output else RESULTS_DIR
    results_dir.mkdir(parents=True, exist_ok=True)

    banner(f"CATEGORICAL GEOMETRY PROBES — {args.model}")
    print(f"  Time     : {datetime.now(UTC).isoformat()}", file=sys.stderr)
    print(f"  Device   : {args.device}", file=sys.stderr)
    print(f"  Output   : {results_dir}", file=sys.stderr)
    print(f"  Quick    : {args.quick}", file=sys.stderr)
    print(f"  Layers   : {PROBE_LAYERS}", file=sys.stderr, flush=True)

    # ── Data slicing for --quick mode ──
    n = 5 if args.quick else None
    well_typed = WELL_TYPED[:n]
    ill_typed = ILL_TYPED[:n]
    depth_labeled = DEPTH_LABELED[:n]
    coherence_pairs = COHERENCE_PAIRS[:n]

    print(
        f"\n  Curry-Howard: {len(well_typed)} well-typed + {len(ill_typed)} ill-typed sentences",
        file=sys.stderr,
    )
    print(f"  Adjunctions : {len(well_typed)} sentences (reuse well-typed)", file=sys.stderr)
    print(f"  Hyperbolic  : {len(depth_labeled)} sentences", file=sys.stderr)
    print(f"  Coherence   : {len(coherence_pairs)} sentence pairs", file=sys.stderr, flush=True)

    # ── Load model ONCE ──
    model, tokenizer, config = load_model(args.model, device=args.device)
    n_layers = config.num_hidden_layers
    d_model = config.hidden_size

    # Clamp probe layers to valid range
    layer_indices = [L for L in PROBE_LAYERS if 0 <= L < n_layers]
    print(f"\n  Effective probe layers: {layer_indices}", file=sys.stderr, flush=True)

    # ── Run probes ──
    all_results: dict = {
        "timestamp": datetime.now(UTC).isoformat(),
        "model": args.model,
        "n_layers": n_layers,
        "d_model": d_model,
        "quick": args.quick,
        "config": {
            "probe_layers": layer_indices,
            "encode_layer": ENCODE_LAYER,
            "compress_layer": COMPRESS_LAYER,
            "decode_layer": DECODE_LAYER,
            "final_layer": FINAL_LAYER,
        },
    }

    # Probe 1 — Curry-Howard
    ch_result = probe_curry_howard(
        model, tokenizer, layer_indices, well_typed, ill_typed
    )
    all_results["curry_howard"] = ch_result

    # Probe 2 — Adjunctions
    adj_result = probe_adjunctions(model, tokenizer, well_typed)
    all_results["adjunctions"] = adj_result

    # Probe 3 — Hyperbolic
    hyp_result = probe_hyperbolic(model, tokenizer, layer_indices, depth_labeled)
    all_results["hyperbolic"] = hyp_result

    # Probe 4 — Coherence
    coh_result = probe_coherence(model, tokenizer, layer_indices, coherence_pairs)
    all_results["coherence"] = coh_result

    # ── Free model ──
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()

    elapsed = time.time() - start
    all_results["elapsed_s"] = elapsed

    # ── Save summary JSON ──
    # Strip large raw lists that are only needed for plots
    save_results = {k: v for k, v in all_results.items() if k != "adjunctions"}
    adj_save = {k: v for k, v in all_results.get("adjunctions", {}).items()
                if k != "_raw_cosines"}
    save_results["adjunctions"] = adj_save

    summary_path = results_dir / "summary.json"
    summary_path.write_text(json.dumps(save_results, indent=2, ensure_ascii=False))
    print(f"\n  Saved: {summary_path}", file=sys.stderr)

    # ── Make plots ──
    banner("GENERATING PLOTS")
    make_plots(all_results, results_dir)

    # ── Print high-level summary ──
    banner(f"SUMMARY — {elapsed:.0f}s")

    # Curry-Howard peak accuracy
    ch_rbl = ch_result.get("results_by_layer", {})
    if ch_rbl:
        peak_k = max(ch_rbl, key=lambda k: ch_rbl[k]["accuracy_mean"])
        peak_acc = ch_rbl[peak_k]["accuracy_mean"]
        print(
            f"  Curry-Howard peak accuracy: L{peak_k} = {peak_acc:.1%}",
            file=sys.stderr,
        )
        if peak_acc > 0.7:
            print("    → Well-typed/ill-typed ARE linearly separable in residual space",
                  file=sys.stderr)
        else:
            print("    → Composition geometry NOT strongly separable", file=sys.stderr)

    # Adjunction summary
    adj_r2 = all_results.get("adjunctions", {}).get("r2", {})
    if adj_r2:
        r2_ed = adj_r2.get("enc_dec_L2_L56", float("nan"))
        r2_ec = adj_r2.get("enc_comp_L2_L32", float("nan"))
        print(
            f"\n  Adjunction R²: enc↔dec(L2→L56)={r2_ed:.4f}  enc↔comp(L2→L32)={r2_ec:.4f}",
            file=sys.stderr,
        )
        if not (r2_ed != r2_ed) and not (r2_ec != r2_ec):
            if r2_ed > r2_ec:
                print("    → encode↔decode IS more structured than encode↔compress (adjunction supported)",
                      file=sys.stderr)
            else:
                print("    → encode↔compress is MORE structured (against adjunction hypothesis)",
                      file=sys.stderr)

    # Hyperbolic summary
    hyp_rbl = hyp_result.get("results_by_layer", {})
    sig_layers = [k for k, v in hyp_rbl.items()
                  if v.get("spearman_pval", 1.0) < 0.05]
    print(
        f"\n  Hyperbolic: {len(sig_layers)}/{len(hyp_rbl)} layers show significant "
        f"norm–depth correlation (p<0.05)",
        file=sys.stderr,
    )
    if sig_layers:
        best_k = max(sig_layers, key=lambda k: abs(hyp_rbl[k]["spearman_rho"]))
        best_rho = hyp_rbl[best_k]["spearman_rho"]
        print(f"    Best: L{best_k} ρ={best_rho:+.3f}", file=sys.stderr)

    # Coherence summary
    coh_delta = coh_result.get("convergence_delta")
    if coh_delta is not None:
        print(
            f"\n  Coherence convergence Δ = {coh_delta:+.3f}",
            file=sys.stderr,
        )

    print(f"\n  All results: {results_dir}/", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
