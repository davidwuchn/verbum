"""
Probe: What is the SHAPE of the type transition at L27→L28?

We know L28 is the peak typing layer (session 056). We characterized
the OUTPUT (basins, clusters, dispatch hierarchy). We never looked at
the TRANSFORMATION — how L27 becomes L28.

Questions this probe answers:
  1. Is the type transition LOW-RANK? (effective dim of Δ = L28 - L27)
  2. Is it PER-TOKEN or CROSS-TOKEN? (does it need attention or is it pointwise?)
  3. Is the typing zone transition SPECIAL vs other layer transitions?
  4. Do context-dependent words show different transition patterns?
  5. How much of L27 survives into L28 vs how much is new?

Design:
  - Hook layers 25-30 (typing zone) + 10,11,40,41 (controls)
  - Feed curated sentences: context-dependent words in varied contexts,
    context-invariant words as controls, from existing probe sets
  - For each consecutive layer pair, compute:
    • Δ = L(n+1) - L(n)  (residual update vector)
    • ||Δ||/||L(n)||     (relative magnitude)
    • cos(L(n), L(n+1))  (direction preservation)
    • PCA(Δ across all tokens) → effective rank
    • Within-word Δ variance for polysemous vs monosemous words

Output: results/type-transition/transition_analysis.json

License: MIT
"""

import json
import time
import argparse
import sys
from pathlib import Path
from collections import defaultdict

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "results" / "type-transition"

# Layers to hook: typing zone boundary + controls
# Typing zone: 25-30 (L28 is peak, so L26→L27→L28→L29 is the critical window)
# Controls: L10-11 (early), L40-41 (late)
HOOK_LAYERS = [10, 11, 25, 26, 27, 28, 29, 30, 40, 41]

# Layer transitions to analyze
TRANSITIONS = [
    (10, 11, "early_control"),
    (25, 26, "pre_typing"),
    (26, 27, "pre_typing_2"),
    (27, 28, "typing_boundary"),  # THE transition of interest
    (28, 29, "post_typing"),
    (29, 30, "post_typing_2"),
    (40, 41, "late_control"),
]


# ══════════════════════════════════════════════════════════════════
# Probe sentences: words with known context-dependence
# ══════════════════════════════════════════════════════════════════

# Context-DEPENDENT words: same word, different contexts → different basins
# These are the words that failed in the basin projector (session 060-061)
CONTEXT_DEPENDENT_PROBES = [
    # "is" — copula vs identity vs existential
    ("is", [
        "The cat is sleeping on the mat.",
        "Two plus three is five.",
        "The question is whether we should proceed.",
        "This is the final answer.",
        "Every number that is prime has exactly two factors.",
    ]),
    # "of" — partitive vs possessive vs compositional
    ("of", [
        "The sum of three and four is seven.",
        "The color of the sky is blue.",
        "Most of the students passed the exam.",
        "Each of these numbers is prime.",
        "The product of five and six is thirty.",
    ]),
    # "a" — indefinite article vs universal
    ("a", [
        "A cat sat on a mat.",
        "Every student solved a problem.",
        "This is a simple calculation.",
        "Find a number greater than ten.",
        "A function maps each input to a output.",
    ]),
    # "product" — math operation vs commercial
    ("product", [
        "The product of three and five is fifteen.",
        "The product launched last Tuesday.",
        "Compute the product of the first ten primes.",
        "The product quality exceeded expectations.",
        "This product is the result of multiplying seven by eight.",
    ]),
    # "range" — math vs general
    ("range", [
        "The range of the function is all positive integers.",
        "The mountain range stretched across the horizon.",
        "Compute the range of these values.",
        "The range of options is limited.",
        "Every value in the range satisfies the condition.",
    ]),
]

# Context-INVARIANT words: same basin regardless of context
# These words scored >0.99 in the basin projector — near-perfect
CONTEXT_INVARIANT_PROBES = [
    ("Every", [
        "Every cat sleeps on a mat.",
        "Every number has a successor.",
        "Every student completed the assignment.",
        "Every prime greater than two is odd.",
        "Every function has a domain and range.",
    ]),
    ("Compute", [
        "Compute the sum of three and four.",
        "Compute the derivative of x squared.",
        "Compute the factorial of ten.",
        "Compute the greatest common divisor.",
        "Compute the area of the triangle.",
    ]),
    ("Translate", [
        "Translate this sentence into formal logic.",
        "Translate the expression into standard form.",
        "Translate the following into a mathematical formula.",
        "Translate the statement to predicate calculus.",
        "Translate the natural language to lambda notation.",
    ]),
]

# Additional diverse words for PCA rank analysis
DIVERSE_PROBES = [
    ("cat", [
        "The cat sleeps on the mat.",
        "Every cat is an animal.",
        "A cat chased the mouse.",
    ]),
    ("three", [
        "Three plus four is seven.",
        "The three students finished early.",
        "Multiply three by five.",
    ]),
    ("plus", [
        "Two plus three equals five.",
        "The plus side is we finished on time.",
        "Seven plus eight is fifteen.",
    ]),
    ("if", [
        "If the number is even, divide by two.",
        "Check if the condition holds.",
        "If x is greater than zero, return x.",
    ]),
    ("equals", [
        "Two plus two equals four.",
        "The result equals the expected value.",
        "Nothing equals the original.",
    ]),
    ("function", [
        "The function maps integers to booleans.",
        "Every function has a domain.",
        "Define a function that computes the sum.",
    ]),
    ("apply", [
        "Apply the function to the argument.",
        "Apply the transformation to each element.",
        "Apply this rule to simplify the expression.",
    ]),
    ("not", [
        "This is not a valid expression.",
        "The answer is not correct.",
        "Not every number is prime.",
    ]),
]


# ══════════════════════════════════════════════════════════════════
# Model loading (from oracle_extract.py)
# ══════════════════════════════════════════════════════════════════

def load_model(gguf_path: str, device: str = "mps"):
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Word boundary detection (from oracle_extract.py)
# ══════════════════════════════════════════════════════════════════

def detect_word_boundaries(tokenizer, input_ids: torch.Tensor) -> list[tuple[str, list[int]]]:
    """Returns list of (word_text, [token_indices])."""
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    words = []
    current_word_tokens = []
    current_word_ids = []

    for i, tok in enumerate(tokens):
        if tok in tokenizer.all_special_tokens:
            if current_word_tokens:
                text = tokenizer.decode(
                    [input_ids[0, j].item() for j in current_word_ids],
                    skip_special_tokens=True
                ).strip()
                words.append((text, current_word_ids))
                current_word_tokens = []
                current_word_ids = []
            continue

        if tok.startswith("Ġ") or tok.startswith("▁") or not current_word_tokens:
            if current_word_tokens:
                text = tokenizer.decode(
                    [input_ids[0, j].item() for j in current_word_ids],
                    skip_special_tokens=True
                ).strip()
                words.append((text, current_word_ids))
            current_word_tokens = [tok]
            current_word_ids = [i]
        else:
            current_word_tokens.append(tok)
            current_word_ids.append(i)

    if current_word_tokens:
        text = tokenizer.decode(
            [input_ids[0, j].item() for j in current_word_ids],
            skip_special_tokens=True
        ).strip()
        words.append((text, current_word_ids))

    return words


def find_target_word(words: list[tuple[str, list[int]]], target: str) -> list[int] | None:
    """Find token indices for the target word (case-insensitive match)."""
    target_lower = target.lower()
    for word_text, indices in words:
        if word_text.lower() == target_lower:
            return indices
    return None


# ══════════════════════════════════════════════════════════════════
# Extraction: multi-layer activations for target words
# ══════════════════════════════════════════════════════════════════

def extract_multi_layer(
    model, tokenizer, sentences_by_word: dict[str, list[str]],
    hook_layers: list[int], device: str,
) -> dict:
    """Extract activations at multiple layers for target words in context.

    Returns:
      {word: {layer: np.array(n_contexts, d_model)}}
    """
    layer_outputs = {}

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            hidden = output[0] if isinstance(output, tuple) else output
            layer_outputs[layer_idx] = hidden.detach().cpu()
        return hook_fn

    # Register hooks on selected layers only
    hooks = []
    for li in hook_layers:
        h = model.model.layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    result = {}
    total = sum(len(sents) for sents in sentences_by_word.values())
    done = 0

    try:
        with torch.no_grad():
            for word, sentences in sentences_by_word.items():
                word_activations = {li: [] for li in hook_layers}

                for sentence in sentences:
                    inputs = tokenizer(sentence, return_tensors="pt").to(device)
                    input_ids = inputs["input_ids"]

                    layer_outputs.clear()
                    _ = model(**inputs)

                    # Find target word
                    words = detect_word_boundaries(tokenizer, input_ids)
                    indices = find_target_word(words, word)

                    if indices is None:
                        print(f"  WARNING: '{word}' not found in: {sentence[:60]}...",
                              file=sys.stderr)
                        continue

                    # Mean-pool target word's tokens at each hooked layer
                    for li in hook_layers:
                        hidden = layer_outputs[li]  # (1, seq_len, d)
                        vecs = hidden[0, indices, :]  # (n_tokens, d)
                        pooled = vecs.mean(dim=0).numpy().astype(np.float32)
                        word_activations[li].append(pooled)

                    done += 1
                    if done % 10 == 0:
                        print(f"  [{done}/{total}] extracted", file=sys.stderr)

                # Stack into arrays
                result[word] = {}
                for li in hook_layers:
                    if word_activations[li]:
                        result[word][li] = np.stack(word_activations[li])

    finally:
        for h in hooks:
            h.remove()

    return result


# ══════════════════════════════════════════════════════════════════
# Analysis functions
# ══════════════════════════════════════════════════════════════════

def l2_normalize(v: np.ndarray, axis=-1) -> np.ndarray:
    """L2 normalize vectors."""
    norms = np.linalg.norm(v, axis=axis, keepdims=True)
    norms = np.maximum(norms, 1e-8)
    return v / norms


def effective_rank(singular_values: np.ndarray) -> float:
    """Shannon entropy-based effective rank."""
    sv = singular_values[singular_values > 1e-10]
    p = sv / sv.sum()
    entropy = -np.sum(p * np.log(p))
    return np.exp(entropy)


def analyze_transition(
    activations: dict,  # {word: {layer: (n_contexts, d)}}
    src_layer: int, dst_layer: int, label: str,
) -> dict:
    """Analyze the transition from src_layer to dst_layer.

    Returns dict with:
      - per_word: {word: {magnitude, cos_sim, variance_change, ...}}
      - global: {delta_rank, delta_explained_var, ...}
    """
    all_src = []
    all_dst = []
    all_deltas = []
    per_word = {}

    for word, layer_acts in activations.items():
        if src_layer not in layer_acts or dst_layer not in layer_acts:
            continue

        src = layer_acts[src_layer]  # (n_contexts, d)
        dst = layer_acts[dst_layer]  # (n_contexts, d)
        delta = dst - src  # residual update

        n = src.shape[0]
        if n == 0:
            continue

        # Per-context metrics
        src_norms = np.linalg.norm(src, axis=1)  # (n,)
        dst_norms = np.linalg.norm(dst, axis=1)
        delta_norms = np.linalg.norm(delta, axis=1)

        # Relative magnitude of the update
        rel_magnitude = delta_norms / np.maximum(src_norms, 1e-8)

        # Cosine similarity between src and dst (direction preservation)
        src_normed = l2_normalize(src)
        dst_normed = l2_normalize(dst)
        cos_sims = np.sum(src_normed * dst_normed, axis=1)

        # Within-word cosine similarity (how spread are contexts?)
        src_within = 0.0
        dst_within = 0.0
        if n >= 2:
            src_n = l2_normalize(src)
            dst_n = l2_normalize(dst)
            src_sim_matrix = src_n @ src_n.T
            dst_sim_matrix = dst_n @ dst_n.T
            # Mean of upper triangle (excluding diagonal)
            mask = np.triu(np.ones((n, n), dtype=bool), k=1)
            src_within = float(src_sim_matrix[mask].mean())
            dst_within = float(dst_sim_matrix[mask].mean())

        per_word[word] = {
            "n_contexts": int(n),
            "rel_magnitude_mean": float(rel_magnitude.mean()),
            "rel_magnitude_std": float(rel_magnitude.std()),
            "cos_sim_mean": float(cos_sims.mean()),
            "cos_sim_std": float(cos_sims.std()),
            "src_within_sim": float(src_within),
            "dst_within_sim": float(dst_within),
            "within_sim_change": float(dst_within - src_within),
            "src_norm_mean": float(src_norms.mean()),
            "dst_norm_mean": float(dst_norms.mean()),
            "delta_norm_mean": float(delta_norms.mean()),
        }

        all_src.append(src)
        all_dst.append(dst)
        all_deltas.append(delta)

    if not all_deltas:
        return {"label": label, "per_word": {}, "global": {}}

    # Global analysis: PCA on all delta vectors
    all_deltas_mat = np.concatenate(all_deltas, axis=0)  # (total_contexts, d)
    all_src_mat = np.concatenate(all_src, axis=0)
    all_dst_mat = np.concatenate(all_dst, axis=0)

    n_total = all_deltas_mat.shape[0]
    d = all_deltas_mat.shape[1]

    # Center the deltas
    delta_mean = all_deltas_mat.mean(axis=0)
    delta_centered = all_deltas_mat - delta_mean

    # SVD on deltas (for rank analysis)
    # Use a sample if too many vectors
    max_for_svd = min(n_total, 500)
    if n_total > max_for_svd:
        idx = np.random.default_rng(42).choice(n_total, max_for_svd, replace=False)
        delta_for_svd = delta_centered[idx]
    else:
        delta_for_svd = delta_centered

    U, S, Vt = np.linalg.svd(delta_for_svd, full_matrices=False)
    eff_rank = effective_rank(S)

    # Cumulative variance explained
    var_explained = np.cumsum(S**2) / np.sum(S**2)
    dims_for_90 = int(np.searchsorted(var_explained, 0.90)) + 1
    dims_for_95 = int(np.searchsorted(var_explained, 0.95)) + 1
    dims_for_99 = int(np.searchsorted(var_explained, 0.99)) + 1

    # Global magnitude and direction stats
    all_rel_mag = np.linalg.norm(all_deltas_mat, axis=1) / np.maximum(
        np.linalg.norm(all_src_mat, axis=1), 1e-8)
    all_cos = np.sum(l2_normalize(all_src_mat) * l2_normalize(all_dst_mat), axis=1)

    # L2-normalized analysis (direction-only, remove norm effects)
    src_normed = l2_normalize(all_src_mat)
    dst_normed = l2_normalize(all_dst_mat)
    delta_normed = dst_normed - src_normed
    delta_normed_centered = delta_normed - delta_normed.mean(axis=0)

    max_for_svd_n = min(n_total, 500)
    if n_total > max_for_svd_n:
        idx_n = np.random.default_rng(42).choice(n_total, max_for_svd_n, replace=False)
        delta_normed_for_svd = delta_normed_centered[idx_n]
    else:
        delta_normed_for_svd = delta_normed_centered

    U_n, S_n, Vt_n = np.linalg.svd(delta_normed_for_svd, full_matrices=False)
    eff_rank_normed = effective_rank(S_n)

    var_explained_n = np.cumsum(S_n**2) / np.sum(S_n**2)
    dims_for_90_n = int(np.searchsorted(var_explained_n, 0.90)) + 1
    dims_for_95_n = int(np.searchsorted(var_explained_n, 0.95)) + 1

    global_stats = {
        "n_tokens": int(n_total),
        "n_words": len(per_word),
        # Raw space
        "delta_effective_rank": float(eff_rank),
        "delta_dims_for_90pct": int(dims_for_90),
        "delta_dims_for_95pct": int(dims_for_95),
        "delta_dims_for_99pct": int(dims_for_99),
        "delta_top1_var_pct": float(var_explained[0]) if len(var_explained) > 0 else 0,
        "delta_top10_var_pct": float(var_explained[min(9, len(var_explained)-1)]),
        "delta_top50_var_pct": float(var_explained[min(49, len(var_explained)-1)]),
        # L2-normalized (direction-only)
        "normed_delta_effective_rank": float(eff_rank_normed),
        "normed_delta_dims_for_90pct": int(dims_for_90_n),
        "normed_delta_dims_for_95pct": int(dims_for_95_n),
        # Magnitude and direction
        "rel_magnitude_mean": float(all_rel_mag.mean()),
        "rel_magnitude_std": float(all_rel_mag.std()),
        "cos_sim_mean": float(all_cos.mean()),
        "cos_sim_std": float(all_cos.std()),
        # Top singular values (raw)
        "top_20_singular_values": S[:20].tolist(),
        # Top singular values (normed)
        "normed_top_20_singular_values": S_n[:20].tolist(),
    }

    return {
        "label": label,
        "src_layer": src_layer,
        "dst_layer": dst_layer,
        "per_word": per_word,
        "global": global_stats,
    }


def categorize_words(per_word: dict, ctx_dep_words: set, ctx_inv_words: set) -> dict:
    """Summarize transition metrics by word category."""
    categories = {"context_dependent": [], "context_invariant": [], "other": []}

    for word, metrics in per_word.items():
        if word.lower() in ctx_dep_words:
            categories["context_dependent"].append(metrics)
        elif word in ctx_inv_words:
            categories["context_invariant"].append(metrics)
        else:
            categories["other"].append(metrics)

    summary = {}
    for cat, items in categories.items():
        if not items:
            summary[cat] = {"n": 0}
            continue

        summary[cat] = {
            "n": len(items),
            "rel_magnitude_mean": float(np.mean([m["rel_magnitude_mean"] for m in items])),
            "cos_sim_mean": float(np.mean([m["cos_sim_mean"] for m in items])),
            "within_sim_change_mean": float(np.mean([m["within_sim_change"] for m in items])),
            "src_within_sim_mean": float(np.mean([m["src_within_sim"] for m in items])),
            "dst_within_sim_mean": float(np.mean([m["dst_within_sim"] for m in items])),
        }

    return summary


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe type transition shape at L27→L28")
    parser.add_argument("--gguf", default=DEFAULT_GGUF)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Build sentence map: {word: [sentences]}
    sentences_by_word = {}
    ctx_dep_words = set()
    ctx_inv_words = set()

    for word, sentences in CONTEXT_DEPENDENT_PROBES:
        sentences_by_word[word] = sentences
        ctx_dep_words.add(word.lower())

    for word, sentences in CONTEXT_INVARIANT_PROBES:
        sentences_by_word[word] = sentences
        ctx_inv_words.add(word)

    for word, sentences in DIVERSE_PROBES:
        sentences_by_word[word] = sentences

    total_words = len(sentences_by_word)
    total_sentences = sum(len(s) for s in sentences_by_word.values())
    print(f"Probing {total_words} words in {total_sentences} sentences "
          f"across {len(HOOK_LAYERS)} layers", file=sys.stderr)

    # Load model
    model, tokenizer = load_model(args.gguf, device=args.device)

    # Extract activations at all hooked layers
    print(f"\nExtracting activations at layers {HOOK_LAYERS}...", file=sys.stderr)
    t0 = time.time()
    activations = extract_multi_layer(
        model, tokenizer, sentences_by_word, HOOK_LAYERS, args.device
    )
    t1 = time.time()
    print(f"Extraction done in {t1-t0:.1f}s", file=sys.stderr)

    # Analyze each transition
    print(f"\nAnalyzing {len(TRANSITIONS)} layer transitions...", file=sys.stderr)
    results = {}

    for src, dst, label in TRANSITIONS:
        print(f"  {label}: L{src}→L{dst}", file=sys.stderr)
        analysis = analyze_transition(activations, src, dst, label)

        # Category breakdown for the typing boundary
        if analysis["per_word"]:
            analysis["category_summary"] = categorize_words(
                analysis["per_word"], ctx_dep_words, ctx_inv_words
            )

        results[label] = analysis

    # ── Summary comparison across transitions ──
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  TRANSITION COMPARISON", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(f"  {'Transition':<20} {'EffRank':>8} {'EffRank(n)':>10} "
          f"{'Dims@90%':>8} {'Dims(n)@90%':>11} {'RelMag':>8} {'CosSim':>8}",
          file=sys.stderr)
    print(f"  {'-'*20} {'-'*8} {'-'*10} {'-'*8} {'-'*11} {'-'*8} {'-'*8}",
          file=sys.stderr)

    for src, dst, label in TRANSITIONS:
        r = results[label]
        g = r.get("global", {})
        if not g:
            continue
        print(f"  {f'L{src}→L{dst} ({label})':<20} "
              f"{g.get('delta_effective_rank', 0):>8.1f} "
              f"{g.get('normed_delta_effective_rank', 0):>10.1f} "
              f"{g.get('delta_dims_for_90pct', 0):>8d} "
              f"{g.get('normed_delta_dims_for_90pct', 0):>11d} "
              f"{g.get('rel_magnitude_mean', 0):>8.4f} "
              f"{g.get('cos_sim_mean', 0):>8.4f}",
              file=sys.stderr)

    # ── Category comparison at typing boundary ──
    typing_result = results.get("typing_boundary", {})
    cat_summary = typing_result.get("category_summary", {})
    if cat_summary:
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"  TYPING BOUNDARY (L27→L28): WORD CATEGORY COMPARISON", file=sys.stderr)
        print(f"{'='*70}", file=sys.stderr)
        print(f"  {'Category':<22} {'N':>3} {'RelMag':>8} {'CosSim':>8} "
              f"{'WithinΔ':>8} {'SrcWith':>8} {'DstWith':>8}", file=sys.stderr)
        print(f"  {'-'*22} {'-'*3} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}",
              file=sys.stderr)
        for cat in ["context_dependent", "context_invariant", "other"]:
            cs = cat_summary.get(cat, {})
            if cs.get("n", 0) == 0:
                continue
            print(f"  {cat:<22} {cs['n']:>3} "
                  f"{cs.get('rel_magnitude_mean', 0):>8.4f} "
                  f"{cs.get('cos_sim_mean', 0):>8.4f} "
                  f"{cs.get('within_sim_change_mean', 0):>+8.4f} "
                  f"{cs.get('src_within_sim_mean', 0):>8.4f} "
                  f"{cs.get('dst_within_sim_mean', 0):>8.4f}",
                  file=sys.stderr)

    # ── Per-word detail at typing boundary ──
    pw = typing_result.get("per_word", {})
    if pw:
        print(f"\n{'='*70}", file=sys.stderr)
        print(f"  TYPING BOUNDARY (L27→L28): PER-WORD DETAIL", file=sys.stderr)
        print(f"{'='*70}", file=sys.stderr)
        print(f"  {'Word':<15} {'Cat':>5} {'RelMag':>8} {'CosSim':>8} "
              f"{'SrcWith':>8} {'DstWith':>8} {'WithinΔ':>8}", file=sys.stderr)
        print(f"  {'-'*15} {'-'*5} {'-'*8} {'-'*8} {'-'*8} {'-'*8} {'-'*8}",
              file=sys.stderr)

        for word in sorted(pw.keys()):
            m = pw[word]
            cat = "dep" if word.lower() in ctx_dep_words else (
                "inv" if word in ctx_inv_words else "div")
            print(f"  {word:<15} {cat:>5} "
                  f"{m['rel_magnitude_mean']:>8.4f} "
                  f"{m['cos_sim_mean']:>8.4f} "
                  f"{m['src_within_sim']:>8.4f} "
                  f"{m['dst_within_sim']:>8.4f} "
                  f"{m['within_sim_change']:>+8.4f}",
                  file=sys.stderr)

    # Save results
    output_path = output_dir / "transition_analysis.json"
    with open(output_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {output_path}", file=sys.stderr)

    # Also save raw activations for further analysis
    act_path = output_dir / "activations.npz"
    save_dict = {}
    for word, layer_acts in activations.items():
        for li, arr in layer_acts.items():
            save_dict[f"{word}_L{li}"] = arr
    np.savez_compressed(act_path, **save_dict)
    print(f"Activations saved to {act_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
