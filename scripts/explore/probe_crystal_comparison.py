#!/usr/bin/env python3
"""Crystal Comparison — Which model has the best crystal for each domain?

If a model is a pile of domain crystals sharing a KIBC lattice, then different models
have different crystal QUALITY per domain. Model A might have a sharp tool-call crystal
but a blurry reasoning crystal. Model B might be the opposite.

This probe:
1. Runs the same domain probes on multiple models of different sizes
2. Measures crystal quality per domain per model using crystallographic metrics
3. Identifies the best crystal for each domain across all models
4. Builds a COMPOSITE lens: cherry-pick the best domain crystal from the best model
5. The composite lens should outperform any single-teacher lens

═══════════════════════════════════════════════════════════════════════════════════════

Crystal quality metrics (from crystallography):

  MOSAICITY     — how well-aligned are the crystal planes within a domain?
                  Measured: mean cosine similarity within domain probes in beam space.
                  Lower mosaicity (higher cos) = sharper crystal = cleaner readout.

  SELECTIVITY   — how well-separated is this domain from other domains?
                  Measured: mean angular separation from other domain centroids.
                  Higher angle = less cross-talk = fewer confused outputs.

  COMPLETENESS  — how many distinct sub-structures exist within the domain?
                  Measured: effective dimensionality of within-domain PCA.
                  Higher = more sub-types distinguishable (simple vs nested vs dispatch).

  COHERENCE     — how consistent is the crystal across examples?
                  Measured: std of angular deviation from domain centroid.
                  Lower std = more coherent = every example hits the same plane.

  DEPTH PROFILE — does the crystal use the right depths for the right operations?
                  Measured: correlation of domain activation profile with the
                  theoretically predicted depth profile (B→shallow, K/I→deep, M→deepest).

═══════════════════════════════════════════════════════════════════════════════════════

Models compared (using relative depth fractions for cross-architecture comparability):
  - Qwen3-14B:     40 layers, d=5120  → probe at L0, L10, L20, L30
  - OLMo-2-13B:    40 layers, d=5120  → probe at L0, L10, L20, L30
  - Mistral-7B:    32 layers, d=4096  → probe at L0, L8, L16, L24
  - Pythia-160M:   12 layers, d=768   → probe at L0, L3, L6, L9
  - Pythia-1.4B:   24 layers, d=2048  → probe at L0, L6, L12, L18

Usage:
    uv run python scripts/explore/probe_crystal_comparison.py
    uv run python scripts/explore/probe_crystal_comparison.py --quick
    uv run python scripts/explore/probe_crystal_comparison.py --models qwen3-14b,mistral-7b

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

OUTPUT_DIR = Path("results/crystal-comparison")

# Model registry with relative depth layer mapping
# Depth fractions: 0%, 25%, 50%, 75% of total layers
MODELS = {
    "qwen3-14b": {
        "name": "Qwen/Qwen3-14B",
        "d_model": 5120,
        "n_layers": 40,
        "target_layers": [0, 10, 20, 30],
        "dtype": "bfloat16",
    },
    "olmo-2-13b": {
        "name": "allenai/OLMo-2-1124-13B",
        "d_model": 5120,
        "n_layers": 40,
        "target_layers": [0, 10, 20, 30],
        "dtype": "bfloat16",
    },
    "mistral-7b": {
        "name": "mistralai/Mistral-7B-v0.3",
        "d_model": 4096,
        "n_layers": 32,
        "target_layers": [0, 8, 16, 24],
        "dtype": "bfloat16",
    },
    "pythia-1.4b": {
        "name": "EleutherAI/pythia-1.4b-deduped",
        "d_model": 2048,
        "n_layers": 24,
        "target_layers": [0, 6, 12, 18],
        "dtype": "float32",
    },
    "pythia-160m": {
        "name": "EleutherAI/pythia-160m-deduped",
        "d_model": 768,
        "n_layers": 12,
        "target_layers": [0, 3, 6, 9],
        "dtype": "float32",
    },
}

# Depth labels (same for all models — relative positions)
DEPTH_LABELS = ["shallow", "mid_shallow", "mid_deep", "deep"]


# ══════════════════════════════════════════════════════════════════
# Domain probes (same as Procrustes lens probe)
# ══════════════════════════════════════════════════════════════════


def build_probes() -> dict[str, list[str]]:
    """Domain-specific probe prompts — 25 per domain, 4 domains."""
    return {
        "tool_call": [
            'Call the function get_weather with arguments city="London"',
            'Use search_web to look up "latest AI research papers"',
            "Call calculate_distance with start=NYC and end=LA",
            "Invoke send_email to user@example.com with subject 'Meeting Tomorrow'",
            'Use translate_text to convert "Hello world" to French',
            "First call get_user_id for 'alice', then use that ID to call get_user_profile",
            "Call parse_csv on the file, then call summarize_data on the result",
            "Use extract_entities on the text, then call classify_entities on the output",
            "First search_database for the record, then format_response with the results",
            "Call tokenize on the input, then embed_tokens, then compute_similarity",
            "If the input is JSON, call parse_json; if XML, call parse_xml; otherwise call parse_text",
            "Choose between create_file and update_file based on whether the path exists",
            "Select the appropriate model: use gpt4 for complex queries, gpt3 for simple ones",
            "Route the request: POST goes to create_handler, GET goes to read_handler",
            "Pick the right database: use postgres for structured data, mongo for documents",
            "Call compare(a, b) but swap the arguments so b is compared against a",
            "Use sort_by with the key function as the first argument instead of the list",
            "Invoke merge(target, source) where source was the original target",
            "Call replace_text with (new, old) instead of the usual (old, new)",
            "Use matrix_multiply(B, A) instead of matrix_multiply(A, B)",
            "Read the config file, validate its schema, apply defaults for missing fields, then write it back",
            "Fetch the API response, check the status code, parse the body, extract the relevant fields",
            "Open the database connection, run the migration, verify the schema, close the connection",
            "Load the model weights, compile the graph, run inference on the batch, collect metrics",
            "Authenticate the user, check permissions, execute the query, format and return results",
        ],
        "code": [
            "Implement a binary search tree with insert, delete, and find operations",
            "Write a hash map with open addressing and linear probing",
            "Create a priority queue using a min-heap",
            "Implement a trie for prefix matching on a dictionary of words",
            "Build a doubly-linked list with O(1) insertion and deletion",
            "Write quicksort with the Lomuto partition scheme",
            "Implement Dijkstra's shortest path algorithm for a weighted graph",
            "Write a function to find all permutations of a string",
            "Implement binary search on a sorted array, returning the insertion point",
            "Write merge sort for a linked list",
            "Create an observer pattern where multiple listeners subscribe to events",
            "Implement a retry decorator with exponential backoff",
            "Write a memoization wrapper that caches function results by arguments",
            "Build a pipeline of transformations that compose left to right",
            "Implement the visitor pattern for an AST with expression and statement nodes",
            "Write a function that validates user input and returns detailed error messages",
            "Implement a circuit breaker that stops calling a failing service after N errors",
            "Create a result type that wraps either a success value or an error",
            "Write exception handling for a file parser that recovers from malformed lines",
            "Build a timeout wrapper that kills functions exceeding a deadline",
            "Write map, filter, and reduce from scratch without using builtins",
            "Implement function composition: compose(f, g) returns a function that applies g then f",
            "Create a currying function that converts f(a, b, c) into f(a)(b)(c)",
            "Write a lazy evaluation wrapper using generators",
            "Implement a monad-like chain method for handling optional values",
        ],
        "factual": [
            "The capital of France is Paris, located on the Seine River",
            "Mount Everest is the tallest mountain on Earth at 8,849 meters",
            "The Amazon River flows through Brazil and empties into the Atlantic Ocean",
            "Tokyo is the most populous metropolitan area in the world",
            "The Sahara Desert covers most of North Africa",
            "Water freezes at 0 degrees Celsius and boils at 100 degrees at sea level",
            "DNA carries genetic information using four nucleotide bases: A, T, C, and G",
            "The speed of light in a vacuum is approximately 299,792,458 meters per second",
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen",
            "The human body contains approximately 37.2 trillion cells",
            "The Roman Empire fell in 476 AD when Romulus Augustulus was deposed",
            "The printing press was invented by Johannes Gutenberg around 1440",
            "The French Revolution began in 1789 with the storming of the Bastille",
            "World War II ended in 1945 with the surrender of Japan",
            "The Berlin Wall fell on November 9, 1989",
            "The first computer program was written by Ada Lovelace in 1843",
            "The internet protocol TCP/IP was standardized in 1983",
            "The transistor was invented at Bell Labs in 1947",
            "The Human Genome Project was completed in 2003",
            "CRISPR-Cas9 gene editing was first demonstrated in 2012",
            "Shakespeare wrote approximately 37 plays and 154 sonnets",
            "The Mona Lisa was painted by Leonardo da Vinci around 1503",
            "Beethoven composed his Ninth Symphony while completely deaf",
            "The Great Wall of China spans approximately 21,196 kilometers",
            "The Olympic Games originated in ancient Greece around 776 BC",
        ],
        "reasoning": [
            "All mammals are warm-blooded. Whales are mammals. Therefore, whales are warm-blooded.",
            "If it rains, the ground gets wet. It is raining. Therefore, the ground is wet.",
            "No reptiles have fur. All dogs have fur. Therefore, no dogs are reptiles.",
            "Every prime number greater than 2 is odd. 7 is prime and greater than 2. Therefore 7 is odd.",
            "All squares are rectangles. This shape is a square. Therefore this shape is a rectangle.",
            "If x + 3 = 7, then x = 4. If x = 4, then 2x = 8. Therefore 2x = 8.",
            "The sum of angles in a triangle is 180 degrees. Two angles are 60 and 70. The third is 50.",
            "If a set has n elements, it has 2^n subsets. A set with 3 elements has 8 subsets.",
            "The probability of heads AND tails in two flips is 0.5 * 0.5 = 0.25",
            "If f(x) = x² and g(x) = x+1, then f(g(x)) = (x+1)² = x² + 2x + 1",
            "The bridge collapsed because the support beams corroded. The corrosion happened because of salt exposure.",
            "Inflation rises when the money supply increases faster than economic output.",
            "The experiment failed because the control group was contaminated, invalidating the results.",
            "Sleep deprivation impairs cognitive function, which leads to poor decision-making.",
            "Overfishing depletes fish populations, which disrupts the marine food chain.",
            "A cell is to a body as a brick is to a building: the basic structural unit.",
            "Electricity flows through wires like water flows through pipes.",
            "An operating system manages computer resources like a manager oversees a team.",
            "Evolution by natural selection is like a sieve: only adapted organisms pass through.",
            "Neural networks learn patterns like children learn language: through exposure and correction.",
            "If the asteroid hadn't hit Earth 66 million years ago, dinosaurs might still dominate.",
            "Had penicillin not been discovered, many bacterial infections would remain untreatable.",
            "Without the invention of writing, oral traditions would be our only historical record.",
            "If gravity were twice as strong, human bodies would need much thicker bones.",
            "Had the printing press never been invented, literacy rates would be much lower today.",
        ],
    }


def build_quick_probes() -> dict[str, list[str]]:
    full = build_probes()
    return {domain: prompts[:5] for domain, prompts in full.items()}


# ══════════════════════════════════════════════════════════════════
# Activation collection
# ══════════════════════════════════════════════════════════════════


def get_layers(model):
    """Multi-architecture layer accessor."""
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    if hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    if hasattr(model, "transformer") and hasattr(model.transformer, "h"):
        return model.transformer.h
    raise AttributeError(f"Cannot find layers in {type(model).__name__}")


def collect_activations(
    model_key: str,
    probes: dict[str, list[str]],
    device: str,
    cache_dir: Path,
) -> dict[str, np.ndarray]:
    """Collect hidden states from a model, with caching."""
    cache_path = cache_dir / f"{model_key}_activations.npz"

    if cache_path.exists():
        print(f"\n  Loading cached activations for {model_key} from {cache_path}",
              file=sys.stderr)
        cached = np.load(str(cache_path), allow_pickle=True)
        return {k: cached[k] for k in cached.files}

    info = MODELS[model_key]
    target_layers = info["target_layers"]
    dtype = getattr(torch, info["dtype"])

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Loading {info['name']} (d={info['d_model']}, "
          f"L={info['n_layers']}, probe at {target_layers})", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    tokenizer = AutoTokenizer.from_pretrained(info["name"])
    model = AutoModelForCausalLM.from_pretrained(
        info["name"], torch_dtype=dtype, device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    layers = get_layers(model)
    hidden_captures: dict[int, list[torch.Tensor]] = {li: [] for li in target_layers}

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            h = output[0] if isinstance(output, tuple) else output
            hidden_captures[layer_idx].append(h[:, -1, :].detach().cpu().float())
        return hook_fn

    hooks = []
    for li in target_layers:
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    # Track domain boundaries
    domain_slices = {}
    probe_idx = 0
    total = sum(len(p) for p in probes.values())
    done = 0
    t0 = time.time()

    for domain, prompts in probes.items():
        start = probe_idx
        for prompt in prompts:
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(input_ids)
            probe_idx += 1
            done += 1
            if done % 10 == 0:
                elapsed = time.time() - t0
                print(f"    [{done}/{total}] {done/elapsed:.1f} probes/s", file=sys.stderr)
        domain_slices[domain] = (start, probe_idx)

    for h in hooks:
        h.remove()

    print(f"  Collected {total} probes in {time.time()-t0:.1f}s", file=sys.stderr)

    # Stack and organize
    results = {}
    for li in target_layers:
        all_hs = torch.cat(hidden_captures[li], dim=0).numpy()
        results[f"{model_key}_L{li}_all"] = all_hs
        for domain, (s, e) in domain_slices.items():
            results[f"{model_key}_L{li}_{domain}"] = all_hs[s:e]

    domain_labels = []
    for domain, prompts in probes.items():
        domain_labels.extend([domain] * len(prompts))
    results[f"{model_key}_domain_labels"] = np.array(domain_labels, dtype=object)

    # Cache
    np.savez_compressed(str(cache_path), **results)
    print(f"  Cached: {cache_path}", file=sys.stderr)

    # Unload
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    return results


def try_load_from_lens_cache(model_key: str, lens_cache_dir: Path) -> dict | None:
    """Try to load activations from the Procrustes lens probe cache."""
    cache_path = lens_cache_dir / f"{model_key}_activations.npz"
    if cache_path.exists():
        print(f"  Reusing Procrustes lens cache for {model_key}: {cache_path}",
              file=sys.stderr)
        cached = np.load(str(cache_path), allow_pickle=True)
        return {k: cached[k] for k in cached.files}
    return None


# ══════════════════════════════════════════════════════════════════
# Beam subspace analysis
# ══════════════════════════════════════════════════════════════════


def compute_beam_subspace(hs: np.ndarray, k: int) -> dict:
    """PCA via SVD → beam subspace."""
    mean = hs.mean(axis=0)
    centered = hs - mean
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)
    var = S ** 2
    total_var = var.sum()
    explained = var / total_var
    p = explained / explained.sum()
    eff_dim = 1.0 / (p ** 2).sum()
    basis = Vt[:k]
    projected = centered @ basis.T
    return {
        "basis": basis, "explained": explained[:k],
        "cumvar": explained[:k].sum(), "eff_dim": eff_dim,
        "projected": projected, "mean": mean,
        "singular_values": S[:k],
    }


def orthogonal_procrustes(A: np.ndarray, B: np.ndarray) -> dict:
    """Procrustes alignment: find R minimizing ||A@R - B||."""
    M = A.T @ B
    U, S, Vt = np.linalg.svd(M)
    R = U @ Vt
    if np.linalg.det(R) < 0:
        U[:, -1] *= -1
        R = U @ Vt
    aligned = A @ R
    residual = np.mean((aligned - B) ** 2)
    norms_a = np.maximum(np.linalg.norm(aligned, axis=1), 1e-8)
    norms_b = np.maximum(np.linalg.norm(B, axis=1), 1e-8)
    cos_after = np.mean(np.sum(aligned * B, axis=1) / (norms_a * norms_b))
    scale = np.trace(aligned.T @ B) / np.trace(aligned.T @ aligned)
    return {"R": R, "cos_after": cos_after, "scale": scale,
            "residual": residual, "singular_values": S}


# ══════════════════════════════════════════════════════════════════
# Crystal quality metrics
# ══════════════════════════════════════════════════════════════════


def measure_crystal_quality(
    data: dict,
    model_key: str,
    target_layers: list[int],
    domains: list[str],
    k: int,
) -> dict:
    """Compute crystal quality metrics for each domain at each depth.

    Returns nested dict: {depth_label: {domain: {metric: value}}}
    """
    quality = {}

    for depth_idx, li in enumerate(target_layers):
        depth_label = DEPTH_LABELS[depth_idx]
        hs_all = data[f"{model_key}_L{li}_all"]
        domain_labels = data[f"{model_key}_domain_labels"]

        # Compute beam subspace on all data
        beam = compute_beam_subspace(hs_all, k)

        depth_quality = {}

        for domain in domains:
            mask = domain_labels == domain
            domain_proj = beam["projected"][mask]  # (n_domain, k)
            n_domain = domain_proj.shape[0]

            # ── MOSAICITY: within-domain cosine similarity ──
            norms = np.maximum(np.linalg.norm(domain_proj, axis=1, keepdims=True), 1e-8)
            domain_norm = domain_proj / norms
            sim_matrix = domain_norm @ domain_norm.T
            triu = np.triu_indices(n_domain, k=1)
            within_cos = sim_matrix[triu].mean() if len(triu[0]) > 0 else 0.0

            # ── COHERENCE: angular deviation from domain centroid ──
            centroid = domain_proj.mean(axis=0)
            centroid_norm = np.linalg.norm(centroid)
            if centroid_norm > 1e-8:
                angles_from_centroid = []
                centroid_unit = centroid / centroid_norm
                for i in range(n_domain):
                    ni = np.linalg.norm(domain_proj[i])
                    if ni > 1e-8:
                        cos_i = np.dot(domain_proj[i], centroid) / (ni * centroid_norm)
                        angles_from_centroid.append(
                            np.degrees(np.arccos(np.clip(cos_i, -1, 1))))
                mean_angle = np.mean(angles_from_centroid)
                std_angle = np.std(angles_from_centroid)
            else:
                mean_angle = 90.0
                std_angle = 0.0

            # ── SELECTIVITY: angular separation from other domains ──
            separations = {}
            for other in domains:
                if other == domain:
                    continue
                other_mask = domain_labels == other
                other_proj = beam["projected"][other_mask]
                other_centroid = other_proj.mean(axis=0)
                other_norm = np.linalg.norm(other_centroid)
                if centroid_norm > 1e-8 and other_norm > 1e-8:
                    cos_sep = np.dot(centroid, other_centroid) / (centroid_norm * other_norm)
                    sep_angle = np.degrees(np.arccos(np.clip(cos_sep, -1, 1)))
                else:
                    sep_angle = 90.0
                separations[other] = float(sep_angle)
            mean_separation = np.mean(list(separations.values()))
            min_separation = min(separations.values()) if separations else 0.0

            # ── COMPLETENESS: effective dimensionality within domain ──
            if n_domain > 2:
                domain_centered = domain_proj - domain_proj.mean(axis=0)
                _, S_d, _ = np.linalg.svd(domain_centered, full_matrices=False)
                var_d = S_d ** 2
                total_d = var_d.sum()
                if total_d > 0:
                    p_d = var_d / total_d
                    domain_eff_dim = 1.0 / (p_d ** 2).sum()
                else:
                    domain_eff_dim = 1.0
            else:
                domain_eff_dim = 1.0

            # ── CENTROID MAGNITUDE: how strongly this domain activates ──
            centroid_magnitude = float(centroid_norm)

            depth_quality[domain] = {
                "mosaicity": float(within_cos),         # higher = sharper (0-1)
                "coherence_mean_angle": float(mean_angle),  # lower = more coherent
                "coherence_std_angle": float(std_angle),    # lower = more consistent
                "selectivity_mean": float(mean_separation), # higher = better separated
                "selectivity_min": float(min_separation),   # higher = no cross-talk
                "selectivity_per_domain": separations,
                "completeness": float(domain_eff_dim),      # higher = richer structure
                "centroid_magnitude": centroid_magnitude,
                "n_probes": int(n_domain),
            }

        quality[depth_label] = depth_quality

    return quality


def compute_composite_score(quality: dict, domain: str) -> float:
    """Compute a single composite crystal quality score for a domain.

    Weighted combination of metrics across all depths:
      - Mosaicity (×2): sharper crystal is more important
      - Selectivity (×1.5): separation prevents confusion
      - Coherence (×1): consistency matters
      - Completeness (×0.5): richness is nice but not critical

    Higher = better crystal.
    """
    scores = []
    weights = []

    for depth_label in DEPTH_LABELS:
        if depth_label not in quality:
            continue
        if domain not in quality[depth_label]:
            continue
        m = quality[depth_label][domain]

        # Normalize each metric to [0, 1]
        mosaicity_score = m["mosaicity"]  # already 0-1
        selectivity_score = min(m["selectivity_min"] / 90.0, 1.0)  # 90° = perfect
        coherence_score = max(1.0 - m["coherence_mean_angle"] / 90.0, 0.0)  # lower angle = better
        completeness_score = min(m["completeness"] / 10.0, 1.0)  # 10 dims = rich

        composite = (
            2.0 * mosaicity_score +
            1.5 * selectivity_score +
            1.0 * coherence_score +
            0.5 * completeness_score
        ) / 5.0

        # Weight deeper layers more (they carry more semantic content)
        depth_weight = {"shallow": 0.5, "mid_shallow": 1.0,
                        "mid_deep": 1.5, "deep": 2.0}[depth_label]

        scores.append(composite * depth_weight)
        weights.append(depth_weight)

    return float(np.average(scores, weights=weights)) if weights else 0.0


# ══════════════════════════════════════════════════════════════════
# Cross-model Procrustes alignment
# ══════════════════════════════════════════════════════════════════


def compute_cross_model_alignment(
    all_data: dict[str, dict],
    model_keys: list[str],
    k: int,
) -> dict:
    """Compute pairwise Procrustes alignment between all model pairs.

    Returns alignment matrix with cos_after for each pair at each depth.
    """
    alignment = {}

    for i, m1 in enumerate(model_keys):
        for m2 in model_keys[i+1:]:
            pair = f"{m1}_vs_{m2}"
            layers_1 = MODELS[m1]["target_layers"]
            layers_2 = MODELS[m2]["target_layers"]

            pair_results = {}
            for di in range(min(len(layers_1), len(layers_2))):
                li_1 = layers_1[di]
                li_2 = layers_2[di]
                depth = DEPTH_LABELS[di]

                hs_1 = all_data[m1][f"{m1}_L{li_1}_all"]
                hs_2 = all_data[m2][f"{m2}_L{li_2}_all"]

                beam_1 = compute_beam_subspace(hs_1, k)
                beam_2 = compute_beam_subspace(hs_2, k)

                proc = orthogonal_procrustes(beam_1["projected"], beam_2["projected"])

                pair_results[depth] = {
                    "cos_after": float(proc["cos_after"]),
                    "scale": float(proc["scale"]),
                    "residual": float(proc["residual"]),
                }

            mean_cos = np.mean([v["cos_after"] for v in pair_results.values()])
            alignment[pair] = {
                "depths": pair_results,
                "mean_cos": float(mean_cos),
            }

            print(f"    {pair:35s}: mean_cos={mean_cos:.4f}", file=sys.stderr)

    return alignment


# ══════════════════════════════════════════════════════════════════
# Best-of-breed selection and composite lens
# ══════════════════════════════════════════════════════════════════


def select_best_and_build_composite(
    all_data: dict[str, dict],
    all_quality: dict[str, dict],
    model_keys: list[str],
    domains: list[str],
    k: int,
    target_student: str | None,
) -> dict:
    """Select best crystal per domain, build composite lens.

    If target_student is specified, build Procrustes alignment from each
    best model → student. Otherwise, report selection only.
    """
    # Compute composite scores
    scores = {}
    for model_key in model_keys:
        scores[model_key] = {}
        for domain in domains:
            scores[model_key][domain] = compute_composite_score(
                all_quality[model_key], domain)

    # Select best per domain
    best = {}
    for domain in domains:
        domain_scores = {m: scores[m][domain] for m in model_keys}
        best_model = max(domain_scores, key=domain_scores.get)
        best[domain] = {
            "model": best_model,
            "score": domain_scores[best_model],
            "all_scores": {m: float(s) for m, s in domain_scores.items()},
        }

    # Build composite lens if student specified
    composite_lens = None
    if target_student and target_student in all_data:
        print(f"\n  Building composite lens → {target_student}...", file=sys.stderr)
        composite_lens = {}

        for domain in domains:
            teacher_key = best[domain]["model"]
            teacher_layers = MODELS[teacher_key]["target_layers"]
            student_layers = MODELS[target_student]["target_layers"]

            domain_lens = {}
            domain_labels = all_data[teacher_key][f"{teacher_key}_domain_labels"]

            for di in range(min(len(teacher_layers), len(student_layers))):
                li_t = teacher_layers[di]
                li_s = student_layers[di]
                depth = DEPTH_LABELS[di]

                hs_t = all_data[teacher_key][f"{teacher_key}_L{li_t}_all"]
                hs_s = all_data[target_student][f"{target_student}_L{li_s}_all"]

                beam_t = compute_beam_subspace(hs_t, k)
                beam_s = compute_beam_subspace(hs_s, k)
                proc = orthogonal_procrustes(beam_t["projected"], beam_s["projected"])

                domain_lens[depth] = {
                    "teacher_model": teacher_key,
                    "teacher_layer": li_t,
                    "student_layer": li_s,
                    "cos_after": float(proc["cos_after"]),
                    "scale": float(proc["scale"]),
                }

            composite_lens[domain] = domain_lens
            print(f"    {domain}: teacher={teacher_key}, "
                  f"mean_cos={np.mean([v['cos_after'] for v in domain_lens.values()]):.4f}",
                  file=sys.stderr)

    return {
        "scores": {m: {d: float(s) for d, s in ds.items()} for m, ds in scores.items()},
        "best_per_domain": best,
        "composite_lens": composite_lens,
    }


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_crystal_comparison(
    all_quality: dict[str, dict],
    model_keys: list[str],
    domains: list[str],
    best_selection: dict,
    output_dir: Path,
):
    """Generate comparison plots."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available, skipping plots", file=sys.stderr)
        return

    model_colors = {
        "qwen3-14b": "#e74c3c",
        "olmo-2-13b": "#3498db",
        "mistral-7b": "#2ecc71",
        "pythia-1.4b": "#f39c12",
        "pythia-160m": "#9b59b6",
    }

    # ── Plot 1: Composite scores per domain per model ──
    fig, ax = plt.subplots(figsize=(12, 6))
    x = np.arange(len(domains))
    width = 0.8 / len(model_keys)

    for i, model_key in enumerate(model_keys):
        scores_per_domain = [
            best_selection["scores"].get(model_key, {}).get(d, 0) for d in domains
        ]
        bars = ax.bar(x + i * width, scores_per_domain, width,
                      label=model_key, color=model_colors.get(model_key, "gray"),
                      alpha=0.8)
        # Mark best with star
        for j, domain in enumerate(domains):
            best_model = best_selection["best_per_domain"][domain]["model"]
            if model_key == best_model:
                ax.annotate("★", (x[j] + i * width, scores_per_domain[j]),
                           ha="center", va="bottom", fontsize=14, color="gold")

    ax.set_xticks(x + width * (len(model_keys) - 1) / 2)
    ax.set_xticklabels(domains)
    ax.set_ylabel("Crystal Quality Score")
    ax.set_title("Crystal Quality by Domain and Model (★ = best)")
    ax.legend(loc="upper right")
    ax.grid(True, alpha=0.3, axis="y")
    plt.tight_layout()
    plt.savefig(output_dir / "crystal_quality_scores.png", dpi=150)
    plt.close()
    print(f"  Saved: {output_dir / 'crystal_quality_scores.png'}", file=sys.stderr)

    # ── Plot 2: Radar chart of metrics for each model (tool_call domain) ──
    metrics = ["mosaicity", "selectivity_mean", "coherence_mean_angle", "completeness"]
    metric_labels = ["Mosaicity\n(higher=sharper)", "Selectivity\n(higher=separated)",
                     "Coherence\n(lower=better)", "Completeness\n(higher=richer)"]

    fig, axes = plt.subplots(1, len(domains), figsize=(5 * len(domains), 5))
    if len(domains) == 1:
        axes = [axes]

    for di, domain in enumerate(domains):
        ax = axes[di]
        for model_key in model_keys:
            # Average across depths
            values = []
            for metric in metrics:
                vals_per_depth = []
                for depth in DEPTH_LABELS:
                    if depth in all_quality[model_key] and domain in all_quality[model_key][depth]:
                        vals_per_depth.append(
                            all_quality[model_key][depth][domain][metric])
                values.append(np.mean(vals_per_depth) if vals_per_depth else 0)

            # Normalize for display
            norm_values = [
                values[0],                          # mosaicity: already 0-1
                min(values[1] / 180, 1.0),          # selectivity: /180°
                max(1 - values[2] / 90, 0),         # coherence: invert (lower=better)
                min(values[3] / 15, 1.0),            # completeness: /15
            ]

            ax.plot(range(len(metrics)), norm_values, marker="o",
                    label=model_key, color=model_colors.get(model_key, "gray"))

        ax.set_xticks(range(len(metrics)))
        ax.set_xticklabels(metric_labels, fontsize=8)
        ax.set_ylim(0, 1)
        ax.set_title(f"{domain}", fontsize=12, fontweight="bold")
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)

    plt.suptitle("Crystal Metrics by Domain", fontsize=14, fontweight="bold")
    plt.tight_layout()
    plt.savefig(output_dir / "crystal_metrics_comparison.png", dpi=150)
    plt.close()
    print(f"  Saved: {output_dir / 'crystal_metrics_comparison.png'}", file=sys.stderr)

    # ── Plot 3: Depth profiles per model per domain ──
    fig, axes = plt.subplots(len(domains), 1, figsize=(10, 4 * len(domains)))
    if len(domains) == 1:
        axes = [axes]

    for di, domain in enumerate(domains):
        ax = axes[di]
        for model_key in model_keys:
            profile = []
            for depth in DEPTH_LABELS:
                if depth in all_quality[model_key] and domain in all_quality[model_key][depth]:
                    profile.append(all_quality[model_key][depth][domain]["mosaicity"])
                else:
                    profile.append(0)
            ax.plot(DEPTH_LABELS, profile, marker="s",
                    label=model_key, color=model_colors.get(model_key, "gray"),
                    linewidth=2)

        ax.set_ylabel("Mosaicity (within-domain cos)")
        ax.set_title(f"{domain} — Crystal sharpness by depth")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "crystal_depth_profiles.png", dpi=150)
    plt.close()
    print(f"  Saved: {output_dir / 'crystal_depth_profiles.png'}", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Crystal Comparison across models")
    parser.add_argument("--models", type=str,
                       default="qwen3-14b,olmo-2-13b,mistral-7b,pythia-1.4b,pythia-160m",
                       help="Comma-separated model keys to compare")
    parser.add_argument("--beam-dims", type=int, default=20)
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--quick", action="store_true", help="5 probes per domain")
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--target-student", type=str, default=None,
                       help="Model key for composite lens target (default: largest model)")
    parser.add_argument("--lens-cache-dir", type=Path,
                       default=Path("results/procrustes-lens"),
                       help="Directory with cached activations from lens probe")
    args = parser.parse_args()

    model_keys = [m.strip() for m in args.models.split(",")]
    for m in model_keys:
        if m not in MODELS:
            print(f"Unknown model: {m}. Available: {list(MODELS.keys())}", file=sys.stderr)
            sys.exit(1)

    if args.device is None:
        if torch.backends.mps.is_available():
            args.device = "mps"
        elif torch.cuda.is_available():
            args.device = "cuda"
        else:
            args.device = "cpu"

    args.output_dir.mkdir(parents=True, exist_ok=True)

    probes = build_quick_probes() if args.quick else build_probes()
    domains = list(probes.keys())
    total_probes = sum(len(p) for p in probes.values())

    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  CRYSTAL COMPARISON ACROSS MODELS", file=sys.stderr)
    print(f"  Models: {model_keys}", file=sys.stderr)
    print(f"  Probes: {total_probes} across {len(domains)} domains", file=sys.stderr)
    print(f"  Beam dims: {args.beam_dims}", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    # ── Phase 1: Collect activations from all models ──
    print(f"\nPhase 1: Activation collection", file=sys.stderr)
    all_data: dict[str, dict] = {}

    for model_key in model_keys:
        # Try Procrustes lens cache first
        data = try_load_from_lens_cache(model_key, args.lens_cache_dir)
        if data is not None:
            # Verify it has what we need
            li = MODELS[model_key]["target_layers"][0]
            if f"{model_key}_L{li}_all" in data:
                all_data[model_key] = data
                continue
            else:
                print(f"  Lens cache for {model_key} has different format, re-collecting",
                      file=sys.stderr)

        # Collect fresh
        all_data[model_key] = collect_activations(
            model_key, probes, args.device, args.output_dir)

    # ── Phase 2: Crystal quality metrics ──
    print(f"\nPhase 2: Crystal quality measurement", file=sys.stderr)
    all_quality = {}

    for model_key in model_keys:
        target_layers = MODELS[model_key]["target_layers"]
        quality = measure_crystal_quality(
            all_data[model_key], model_key, target_layers, domains, args.beam_dims)
        all_quality[model_key] = quality

        print(f"\n  {model_key} (d={MODELS[model_key]['d_model']}):", file=sys.stderr)
        for depth in DEPTH_LABELS:
            if depth not in quality:
                continue
            for domain in domains:
                if domain not in quality[depth]:
                    continue
                m = quality[depth][domain]
                print(f"    {depth:12s} {domain:12s}: "
                      f"mos={m['mosaicity']:.3f} sel={m['selectivity_mean']:.1f}° "
                      f"coh={m['coherence_mean_angle']:.1f}±{m['coherence_std_angle']:.1f}° "
                      f"comp={m['completeness']:.1f}",
                      file=sys.stderr)

    # ── Phase 3: Cross-model alignment ──
    print(f"\nPhase 3: Cross-model Procrustes alignment", file=sys.stderr)
    alignment = compute_cross_model_alignment(all_data, model_keys, args.beam_dims)

    # ── Phase 4: Best-of-breed selection ──
    print(f"\nPhase 4: Best-of-breed selection", file=sys.stderr)

    target_student = args.target_student
    if target_student is None:
        # Default: use the largest model as reference student
        # (for composite lens construction, we need a target)
        largest = max(model_keys, key=lambda m: MODELS[m]["d_model"])
        target_student = largest

    selection = select_best_and_build_composite(
        all_data, all_quality, model_keys, domains, args.beam_dims, target_student)

    # ── Results summary ──
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  RESULTS", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    print(f"\n  Best crystal per domain:", file=sys.stderr)
    print(f"  {'Domain':15s} {'Best Model':20s} {'Score':>8s}  {'Runner-up':20s} {'Score':>8s}",
          file=sys.stderr)
    print(f"  {'─'*75}", file=sys.stderr)

    for domain in domains:
        info = selection["best_per_domain"][domain]
        sorted_scores = sorted(info["all_scores"].items(), key=lambda x: -x[1])
        best = sorted_scores[0]
        runner = sorted_scores[1] if len(sorted_scores) > 1 else ("N/A", 0)
        print(f"  {domain:15s} {best[0]:20s} {best[1]:>8.4f}  "
              f"{runner[0]:20s} {runner[1]:>8.4f}", file=sys.stderr)

    print(f"\n  Cross-model alignment (mean cos after Procrustes):", file=sys.stderr)
    for pair, result in sorted(alignment.items(), key=lambda x: -x[1]["mean_cos"]):
        print(f"    {pair:35s}: {result['mean_cos']:.4f}", file=sys.stderr)

    print(f"\n  Composite lens target: {target_student}", file=sys.stderr)
    if selection["composite_lens"]:
        print(f"  Composite lens recipe:", file=sys.stderr)
        for domain in domains:
            best_model = selection["best_per_domain"][domain]["model"]
            lens = selection["composite_lens"][domain]
            mean_cos = np.mean([v["cos_after"] for v in lens.values()])
            print(f"    {domain:15s} ← {best_model:20s} (cos={mean_cos:.4f})", file=sys.stderr)

    # ── Save results ──
    def make_serializable(obj):
        if isinstance(obj, dict):
            return {str(k): make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, (np.integer,)):
            return int(obj)
        elif isinstance(obj, (np.floating,)):
            return float(obj)
        elif isinstance(obj, np.ndarray):
            return obj.tolist()
        elif isinstance(obj, list):
            return [make_serializable(x) for x in obj]
        return obj

    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "models": model_keys,
            "beam_dims": args.beam_dims,
            "n_probes_per_domain": len(probes[domains[0]]),
            "domains": domains,
        },
        "crystal_quality": make_serializable(all_quality),
        "cross_model_alignment": make_serializable(alignment),
        "selection": make_serializable(selection),
    }

    json_path = args.output_dir / "crystal_comparison_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)

    # ── Plots ──
    if not args.skip_plots:
        print(f"\n  Generating plots...", file=sys.stderr)
        plot_crystal_comparison(
            all_quality, model_keys, domains, selection, args.output_dir)

    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  DONE", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)


if __name__ == "__main__":
    main()
