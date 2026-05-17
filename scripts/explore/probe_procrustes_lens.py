#!/usr/bin/env python3
"""Procrustes Lens — Can we compute a parameter-free adapter between model coordinate systems?

The universal hologram finding (session 104-106) established that independently trained
models converge on the SAME relational topology (RSA r=0.7448) but in completely
different coordinate systems (direct alignment cos≈0.000). This probe asks:

    Is the coordinate transformation between models a simple rotation in beam space?

If yes: the "lens" between teacher and student is a parameter-free Procrustes rotation,
computed analytically from calibration examples. Zero trainable parameters. The entire
adapter from a 14B model to a small crystal could fit in a tweet.

If no: we need a small learned adapter (MLP in beam space), but still tiny (k² params).

═══════════════════════════════════════════════════════════════════════════════════════

Architecture of the probe:

Phase 1 — COLLECT: Run domain-specific prompts through both models, hook hidden states
at target layers [0, 10, 20, 30] (matching the depth map). Save per-layer activations.

Phase 2 — BEAM: PCA each model's activations per layer → beam subspace (top-k components).
Measure effective dimensionality. Compare beam dimensions across domains.

Phase 3 — PROCRUSTES: For each depth mapping, compute the optimal orthogonal rotation R
that aligns model A's beam space to model B's beam space. Closed-form SVD solution:
    M = H_A^T @ H_B
    U, Σ, V^T = SVD(M)
    R = V @ U^T
Measure residual alignment error after rotation.

Phase 4 — EVALUATE: Project model A's beams through the lens (R), compare to model B's
actual beams. Metrics: angular error, magnitude ratio, topology preservation (RSA before
vs after alignment), per-domain alignment quality. Visualize beam subspaces.

═══════════════════════════════════════════════════════════════════════════════════════

Domain prompts span 4 categories (the first holographic transfer targets):
- Tool calls: function application, typed arguments, nested composition
- Code: programming constructs, algorithms, data structures
- Factual: world knowledge, entity relationships
- Reasoning: logical chains, math, inference

Each domain should activate different beam angles in the hologram. The Procrustes lens
should preserve RELATIVE angles between domains while mapping absolute coordinates.

═══════════════════════════════════════════════════════════════════════════════════════

Usage:
    uv run python scripts/explore/probe_procrustes_lens.py
    uv run python scripts/explore/probe_procrustes_lens.py --beam-dims 30
    uv run python scripts/explore/probe_procrustes_lens.py --quick  # 5 probes/domain

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

OUTPUT_DIR = Path("results/procrustes-lens")

# Models: both d_model=5120, different architectures, Apache-2.0
MODELS = {
    "qwen3-14b": {
        "name": "Qwen/Qwen3-14B",
        "d_model": 5120,
        "n_layers": 40,
    },
    "olmo-2-13b": {
        "name": "allenai/OLMo-2-1124-13B",
        "d_model": 5120,
        "n_layers": 40,
    },
}

# Depth map layers — where the action is
TARGET_LAYERS = [0, 10, 20, 30]


# ══════════════════════════════════════════════════════════════════
# Domain probe sets — the holograms we want to transfer
# ══════════════════════════════════════════════════════════════════


def build_probes() -> dict[str, list[str]]:
    """Build domain-specific probe prompts.

    Each domain targets a different holographic structure:
    - tool_call: function application (β-reduction), typed args (KIBC signatures)
    - code: programming constructs (composition, abstraction, application)
    - factual: world knowledge (entity-relation-entity patterns)
    - reasoning: logical chains (if-then, therefore, because)
    """
    return {
        "tool_call": [
            # Simple function calls — I combinator (identity/binding)
            'Call the function get_weather with arguments city="London"',
            'Use search_web to look up "latest AI research papers"',
            "Call calculate_distance with start=NYC and end=LA",
            "Invoke send_email to user@example.com with subject 'Meeting Tomorrow'",
            'Use translate_text to convert "Hello world" to French',
            # Nested/composed calls — B combinator (composition)
            "First call get_user_id for 'alice', then use that ID to call get_user_profile",
            "Call parse_csv on the file, then call summarize_data on the result",
            "Use extract_entities on the text, then call classify_entities on the output",
            "First search_database for the record, then format_response with the results",
            "Call tokenize on the input, then embed_tokens, then compute_similarity",
            # Selection/dispatch — K combinator (select one, discard rest)
            "If the input is JSON, call parse_json; if XML, call parse_xml; otherwise call parse_text",
            "Choose between create_file and update_file based on whether the path exists",
            "Select the appropriate model: use gpt4 for complex queries, gpt3 for simple ones",
            "Route the request: POST goes to create_handler, GET goes to read_handler",
            "Pick the right database: use postgres for structured data, mongo for documents",
            # Argument reordering — C combinator (flip)
            "Call compare(a, b) but swap the arguments so b is compared against a",
            "Use sort_by with the key function as the first argument instead of the list",
            "Invoke merge(target, source) where source was the original target",
            "Call replace_text with (new, old) instead of the usual (old, new)",
            "Use matrix_multiply(B, A) instead of matrix_multiply(A, B)",
            # Complex multi-step tool use — M combinator (match/pattern)
            "Read the config file, validate its schema, apply defaults for missing fields, then write it back",
            "Fetch the API response, check the status code, parse the body, extract the relevant fields",
            "Open the database connection, run the migration, verify the schema, close the connection",
            "Load the model weights, compile the graph, run inference on the batch, collect metrics",
            "Authenticate the user, check permissions, execute the query, format and return results",
        ],
        "code": [
            # Data structures
            "Implement a binary search tree with insert, delete, and find operations",
            "Write a hash map with open addressing and linear probing",
            "Create a priority queue using a min-heap",
            "Implement a trie for prefix matching on a dictionary of words",
            "Build a doubly-linked list with O(1) insertion and deletion",
            # Algorithms
            "Write quicksort with the Lomuto partition scheme",
            "Implement Dijkstra's shortest path algorithm for a weighted graph",
            "Write a function to find all permutations of a string",
            "Implement binary search on a sorted array, returning the insertion point",
            "Write merge sort for a linked list",
            # Patterns
            "Create an observer pattern where multiple listeners subscribe to events",
            "Implement a retry decorator with exponential backoff",
            "Write a memoization wrapper that caches function results by arguments",
            "Build a pipeline of transformations that compose left to right",
            "Implement the visitor pattern for an AST with expression and statement nodes",
            # Error handling
            "Write a function that validates user input and returns detailed error messages",
            "Implement a circuit breaker that stops calling a failing service after N errors",
            "Create a result type that wraps either a success value or an error",
            "Write exception handling for a file parser that recovers from malformed lines",
            "Build a timeout wrapper that kills functions exceeding a deadline",
            # Functional
            "Write map, filter, and reduce from scratch without using builtins",
            "Implement function composition: compose(f, g) returns a function that applies g then f",
            "Create a currying function that converts f(a, b, c) into f(a)(b)(c)",
            "Write a lazy evaluation wrapper using generators",
            "Implement a monad-like chain method for handling optional values",
        ],
        "factual": [
            # Geography
            "The capital of France is Paris, located on the Seine River",
            "Mount Everest is the tallest mountain on Earth at 8,849 meters",
            "The Amazon River flows through Brazil and empties into the Atlantic Ocean",
            "Tokyo is the most populous metropolitan area in the world",
            "The Sahara Desert covers most of North Africa",
            # Science
            "Water freezes at 0 degrees Celsius and boils at 100 degrees at sea level",
            "DNA carries genetic information using four nucleotide bases: A, T, C, and G",
            "The speed of light in a vacuum is approximately 299,792,458 meters per second",
            "Photosynthesis converts carbon dioxide and water into glucose and oxygen",
            "The human body contains approximately 37.2 trillion cells",
            # History
            "The Roman Empire fell in 476 AD when Romulus Augustulus was deposed",
            "The printing press was invented by Johannes Gutenberg around 1440",
            "The French Revolution began in 1789 with the storming of the Bastille",
            "World War II ended in 1945 with the surrender of Japan",
            "The Berlin Wall fell on November 9, 1989",
            # Technology
            "The first computer program was written by Ada Lovelace in 1843",
            "The internet protocol TCP/IP was standardized in 1983",
            "The transistor was invented at Bell Labs in 1947",
            "The Human Genome Project was completed in 2003",
            "CRISPR-Cas9 gene editing was first demonstrated in 2012",
            # Culture
            "Shakespeare wrote approximately 37 plays and 154 sonnets",
            "The Mona Lisa was painted by Leonardo da Vinci around 1503",
            "Beethoven composed his Ninth Symphony while completely deaf",
            "The Great Wall of China spans approximately 21,196 kilometers",
            "The Olympic Games originated in ancient Greece around 776 BC",
        ],
        "reasoning": [
            # Deductive
            "All mammals are warm-blooded. Whales are mammals. Therefore, whales are warm-blooded.",
            "If it rains, the ground gets wet. It is raining. Therefore, the ground is wet.",
            "No reptiles have fur. All dogs have fur. Therefore, no dogs are reptiles.",
            "Every prime number greater than 2 is odd. 7 is prime and greater than 2. Therefore 7 is odd.",
            "All squares are rectangles. This shape is a square. Therefore this shape is a rectangle.",
            # Mathematical
            "If x + 3 = 7, then x = 4. If x = 4, then 2x = 8. Therefore 2x = 8.",
            "The sum of angles in a triangle is 180 degrees. Two angles are 60 and 70. The third is 50.",
            "If a set has n elements, it has 2^n subsets. A set with 3 elements has 8 subsets.",
            "The probability of heads AND tails in two flips is 0.5 * 0.5 = 0.25",
            "If f(x) = x² and g(x) = x+1, then f(g(x)) = (x+1)² = x² + 2x + 1",
            # Causal
            "The bridge collapsed because the support beams corroded. The corrosion happened because of salt exposure.",
            "Inflation rises when the money supply increases faster than economic output.",
            "The experiment failed because the control group was contaminated, invalidating the results.",
            "Sleep deprivation impairs cognitive function, which leads to poor decision-making.",
            "Overfishing depletes fish populations, which disrupts the marine food chain.",
            # Analogical
            "A cell is to a body as a brick is to a building: the basic structural unit.",
            "Electricity flows through wires like water flows through pipes.",
            "An operating system manages computer resources like a manager oversees a team.",
            "Evolution by natural selection is like a sieve: only adapted organisms pass through.",
            "Neural networks learn patterns like children learn language: through exposure and correction.",
            # Counterfactual
            "If the asteroid hadn't hit Earth 66 million years ago, dinosaurs might still dominate.",
            "Had penicillin not been discovered, many bacterial infections would remain untreatable.",
            "Without the invention of writing, oral traditions would be our only historical record.",
            "If gravity were twice as strong, human bodies would need much thicker bones.",
            "Had the printing press never been invented, literacy rates would be much lower today.",
        ],
    }


def build_quick_probes() -> dict[str, list[str]]:
    """Subset for quick testing: 5 probes per domain."""
    full = build_probes()
    return {domain: prompts[:5] for domain, prompts in full.items()}


# ══════════════════════════════════════════════════════════════════
# Phase 1 & 2: Activation collection
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
    target_layers: list[int],
    probes: dict[str, list[str]],
    device: str,
) -> dict[str, np.ndarray]:
    """Load model, run all probes, collect last-token hidden states per layer.

    Returns dict with keys like "qwen3-14b_L0_tool_call" → (n_probes, d_model).
    Also returns "qwen3-14b_L0_all" → (n_all_probes, d_model) for cross-domain analysis.
    """
    model_info = MODELS[model_key]
    model_name = model_info["name"]
    print(f"\n{'='*60}")
    print(f"Loading {model_name}...")
    print(f"{'='*60}")

    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device,
    )
    model.eval()

    layers = get_layers(model)
    hidden_captures: dict[int, list[torch.Tensor]] = {li: [] for li in target_layers}

    # Register hooks
    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            h = output[0] if isinstance(output, tuple) else output
            hidden_captures[layer_idx].append(h[:, -1, :].detach().cpu().float())
        return hook_fn

    hooks = []
    for li in target_layers:
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Track domain boundaries for slicing later
    domain_slices: dict[str, tuple[int, int]] = {}
    probe_idx = 0

    # Run all probes
    total_probes = sum(len(p) for p in probes.values())
    done = 0
    t0 = time.time()

    for domain, prompts in probes.items():
        start_idx = probe_idx
        for prompt in prompts:
            input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(input_ids)
            probe_idx += 1
            done += 1
            if done % 10 == 0:
                elapsed = time.time() - t0
                rate = done / elapsed
                remaining = (total_probes - done) / rate
                print(f"  [{done}/{total_probes}] {rate:.1f} probes/s, ~{remaining:.0f}s remaining")
        domain_slices[domain] = (start_idx, probe_idx)

    # Remove hooks
    for h in hooks:
        h.remove()

    elapsed = time.time() - t0
    print(f"  Collected {total_probes} probes in {elapsed:.1f}s ({total_probes/elapsed:.1f} probes/s)")

    # Stack and slice
    results = {}
    for li in target_layers:
        all_hs = torch.cat(hidden_captures[li], dim=0).numpy()  # (n_total, d_model)
        results[f"{model_key}_L{li}_all"] = all_hs

        for domain, (start, end) in domain_slices.items():
            results[f"{model_key}_L{li}_{domain}"] = all_hs[start:end]

    # Store domain labels for later
    domain_labels = []
    for domain, prompts in probes.items():
        domain_labels.extend([domain] * len(prompts))
    results[f"{model_key}_domain_labels"] = np.array(domain_labels, dtype=object)

    # Unload
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    print(f"  Model unloaded, memory freed")
    return results


# ══════════════════════════════════════════════════════════════════
# Phase 2: Beam subspace analysis (PCA via SVD)
# ══════════════════════════════════════════════════════════════════


def compute_beam_subspace(hs: np.ndarray, k: int) -> dict:
    """PCA via SVD on hidden states → beam subspace.

    Returns:
        basis: (k, d_model) — top-k principal components
        explained: (k,) — fraction of variance explained per component
        eff_dim: effective dimensionality (participation ratio)
        projected: (n, k) — data projected into beam subspace
        mean: (d_model,) — mean hidden state (for centering)
    """
    mean = hs.mean(axis=0)
    centered = hs - mean

    # SVD: centered = U @ diag(S) @ Vt
    U, S, Vt = np.linalg.svd(centered, full_matrices=False)

    # Variance explained
    var = S ** 2
    total_var = var.sum()
    explained = var / total_var

    # Effective dimensionality (participation ratio)
    p = explained / explained.sum()
    eff_dim = 1.0 / (p ** 2).sum()

    # Top-k basis
    basis = Vt[:k]  # (k, d_model)
    projected = centered @ basis.T  # (n, k)

    # Cumulative variance in top-k
    cumvar_k = explained[:k].sum()

    return {
        "basis": basis,
        "explained": explained[:k],
        "cumvar": cumvar_k,
        "eff_dim": eff_dim,
        "projected": projected,
        "mean": mean,
        "singular_values": S[:k],
    }


# ══════════════════════════════════════════════════════════════════
# Phase 3: Procrustes lens computation
# ══════════════════════════════════════════════════════════════════


def orthogonal_procrustes(A: np.ndarray, B: np.ndarray) -> dict:
    """Solve the orthogonal Procrustes problem: find R that minimizes ||A @ R - B||.

    Given two (n, k) matrices of corresponding points in k-dimensional space,
    find the k×k orthogonal matrix R such that A @ R ≈ B.

    Solution: M = A^T @ B, SVD(M) = U Σ V^T, R = U @ V^T

    Returns:
        R: (k, k) orthogonal rotation matrix
        residual: mean squared error after alignment
        cos_after: mean cosine similarity after alignment
        scale: optimal isotropic scaling factor (teacher→student magnitude)
    """
    # Procrustes: M = A^T @ B
    M = A.T @ B  # (k, k)
    U, S, Vt = np.linalg.svd(M)
    R = U @ Vt  # (k, k) — optimal orthogonal rotation

    # Ensure proper rotation (det = +1), not reflection
    if np.linalg.det(R) < 0:
        # Flip sign of last column of U
        U[:, -1] *= -1
        R = U @ Vt

    # Apply rotation
    A_aligned = A @ R  # (n, k)

    # Residual: mean squared error
    residual = np.mean((A_aligned - B) ** 2)

    # Cosine similarity after alignment
    norms_a = np.linalg.norm(A_aligned, axis=1, keepdims=True)
    norms_b = np.linalg.norm(B, axis=1, keepdims=True)
    cos_after = np.mean(
        np.sum(A_aligned * B, axis=1)
        / (np.maximum(norms_a.flatten(), 1e-8) * np.maximum(norms_b.flatten(), 1e-8))
    )

    # Optimal isotropic scaling: minimize ||s * A_aligned - B||²
    # s = trace(A_aligned^T @ B) / trace(A_aligned^T @ A_aligned)
    scale = np.trace(A_aligned.T @ B) / np.trace(A_aligned.T @ A_aligned)

    # Scaled residual
    A_scaled = A_aligned * scale
    scaled_residual = np.mean((A_scaled - B) ** 2)

    return {
        "R": R,
        "residual": residual,
        "scaled_residual": scaled_residual,
        "cos_after": cos_after,
        "scale": scale,
        "singular_values": S,  # alignment quality per dimension
    }


def compute_rdm(hs: np.ndarray) -> np.ndarray:
    """Compute representational dissimilarity matrix (cosine similarity)."""
    norms = np.maximum(np.linalg.norm(hs, axis=1, keepdims=True), 1e-8)
    hs_norm = hs / norms
    return hs_norm @ hs_norm.T


def compute_rsa(rdm_a: np.ndarray, rdm_b: np.ndarray) -> float:
    """Representational Similarity Analysis: Pearson r on upper triangle."""
    n = rdm_a.shape[0]
    triu_idx = np.triu_indices(n, k=1)
    flat_a = rdm_a[triu_idx]
    flat_b = rdm_b[triu_idx]
    return float(np.corrcoef(flat_a, flat_b)[0, 1])


# ══════════════════════════════════════════════════════════════════
# Phase 4: Full lens evaluation
# ══════════════════════════════════════════════════════════════════


def evaluate_lens(
    teacher_data: dict,
    student_data: dict,
    teacher_key: str,
    student_key: str,
    target_layers: list[int],
    k: int,
    domains: list[str],
) -> dict:
    """Run the complete Procrustes lens evaluation.

    For each layer:
    1. Compute beam subspaces for both models
    2. Compute Procrustes rotation
    3. Measure alignment quality (global and per-domain)
    4. Compare RSA before and after alignment
    5. Test cross-domain angular separation preservation
    """
    results = {"beam_dims": k, "layers": {}, "summary": {}}

    for li in target_layers:
        print(f"\n{'─'*60}")
        print(f"Layer {li}")
        print(f"{'─'*60}")

        # Get hidden states
        hs_teacher = teacher_data[f"{teacher_key}_L{li}_all"]
        hs_student = student_data[f"{student_key}_L{li}_all"]
        n_probes = hs_teacher.shape[0]
        d_model = hs_teacher.shape[1]

        print(f"  Teacher: {hs_teacher.shape}, Student: {hs_student.shape}")

        # ── Beam subspaces ──
        beam_teacher = compute_beam_subspace(hs_teacher, k)
        beam_student = compute_beam_subspace(hs_student, k)

        print(f"  Teacher beam: eff_dim={beam_teacher['eff_dim']:.1f}, "
              f"top-{k} cumvar={beam_teacher['cumvar']:.3f}")
        print(f"  Student beam: eff_dim={beam_student['eff_dim']:.1f}, "
              f"top-{k} cumvar={beam_student['cumvar']:.3f}")

        # ── Raw RSA (before alignment) ──
        rdm_teacher_full = compute_rdm(hs_teacher)
        rdm_student_full = compute_rdm(hs_student)
        rsa_full = compute_rsa(rdm_teacher_full, rdm_student_full)
        print(f"  RSA (full d_model): {rsa_full:.4f}")

        # RSA in beam subspace (before Procrustes)
        rdm_teacher_beam = compute_rdm(beam_teacher["projected"])
        rdm_student_beam = compute_rdm(beam_student["projected"])
        rsa_beam_before = compute_rsa(rdm_teacher_beam, rdm_student_beam)
        print(f"  RSA (beam k={k}, before Procrustes): {rsa_beam_before:.4f}")

        # ── Procrustes alignment ──
        proc = orthogonal_procrustes(beam_teacher["projected"], beam_student["projected"])
        print(f"  Procrustes: cos_after={proc['cos_after']:.4f}, "
              f"residual={proc['residual']:.6f}, "
              f"scale={proc['scale']:.4f}")
        print(f"  Alignment singular values (top 5): "
              f"{proc['singular_values'][:5].round(2)}")

        # RSA after Procrustes alignment
        aligned_teacher = beam_teacher["projected"] @ proc["R"] * proc["scale"]
        rdm_aligned = compute_rdm(aligned_teacher)
        rsa_beam_after = compute_rsa(rdm_aligned, rdm_student_beam)
        print(f"  RSA (beam k={k}, after Procrustes): {rsa_beam_after:.4f}")

        # ── Direct cosine alignment ──
        # Before Procrustes: cosine between teacher and student projected points
        cos_before_pairs = []
        for i in range(n_probes):
            t = beam_teacher["projected"][i]
            s = beam_student["projected"][i]
            nt = np.linalg.norm(t)
            ns = np.linalg.norm(s)
            if nt > 1e-8 and ns > 1e-8:
                cos_before_pairs.append(np.dot(t, s) / (nt * ns))
        cos_direct_before = np.mean(cos_before_pairs)

        # After Procrustes
        cos_after_pairs = []
        for i in range(n_probes):
            t = aligned_teacher[i]
            s = beam_student["projected"][i]
            nt = np.linalg.norm(t)
            ns = np.linalg.norm(s)
            if nt > 1e-8 and ns > 1e-8:
                cos_after_pairs.append(np.dot(t, s) / (nt * ns))
        cos_direct_after = np.mean(cos_after_pairs)

        print(f"  Direct cosine (before): {cos_direct_before:.4f}")
        print(f"  Direct cosine (after):  {cos_direct_after:.4f}")

        # ── Per-domain analysis ──
        domain_labels = teacher_data[f"{teacher_key}_domain_labels"]
        domain_results = {}

        for domain in domains:
            mask = domain_labels == domain
            n_domain = mask.sum()

            # Domain-specific Procrustes quality
            t_domain = aligned_teacher[mask]
            s_domain = beam_student["projected"][mask]

            # Cosine per probe in this domain
            cos_domain = []
            for i in range(n_domain):
                nt = np.linalg.norm(t_domain[i])
                ns = np.linalg.norm(s_domain[i])
                if nt > 1e-8 and ns > 1e-8:
                    cos_domain.append(np.dot(t_domain[i], s_domain[i]) / (nt * ns))
            mean_cos = np.mean(cos_domain) if cos_domain else 0.0

            # Angular error in degrees
            angles = np.degrees(np.arccos(np.clip(cos_domain, -1, 1)))
            mean_angle = np.mean(angles) if len(angles) > 0 else 90.0

            # Domain centroid alignment
            centroid_t = t_domain.mean(axis=0)
            centroid_s = s_domain.mean(axis=0)
            nc_t = np.linalg.norm(centroid_t)
            nc_s = np.linalg.norm(centroid_s)
            centroid_cos = (
                np.dot(centroid_t, centroid_s) / (nc_t * nc_s)
                if nc_t > 1e-8 and nc_s > 1e-8 else 0.0
            )

            domain_results[domain] = {
                "n_probes": int(n_domain),
                "mean_cos": float(mean_cos),
                "mean_angle_deg": float(mean_angle),
                "std_angle_deg": float(np.std(angles)) if len(angles) > 0 else 0.0,
                "centroid_cos": float(centroid_cos),
            }
            print(f"  {domain:12s}: cos={mean_cos:.4f}, "
                  f"angle={mean_angle:.1f}° ± {np.std(angles):.1f}°, "
                  f"centroid_cos={centroid_cos:.4f}")

        # ── Cross-domain angular separation ──
        print(f"\n  Cross-domain angular separation (in beam space):")
        domain_centroids_teacher = {}
        domain_centroids_student = {}
        for domain in domains:
            mask = domain_labels == domain
            domain_centroids_teacher[domain] = aligned_teacher[mask].mean(axis=0)
            domain_centroids_student[domain] = beam_student["projected"][mask].mean(axis=0)

        sep_teacher = {}
        sep_student = {}
        for i, d1 in enumerate(domains):
            for d2 in domains[i+1:]:
                c1_t = domain_centroids_teacher[d1]
                c2_t = domain_centroids_teacher[d2]
                n1 = np.linalg.norm(c1_t)
                n2 = np.linalg.norm(c2_t)
                cos_t = np.dot(c1_t, c2_t) / (n1 * n2) if n1 > 1e-8 and n2 > 1e-8 else 0
                angle_t = np.degrees(np.arccos(np.clip(cos_t, -1, 1)))

                c1_s = domain_centroids_student[d1]
                c2_s = domain_centroids_student[d2]
                n1 = np.linalg.norm(c1_s)
                n2 = np.linalg.norm(c2_s)
                cos_s = np.dot(c1_s, c2_s) / (n1 * n2) if n1 > 1e-8 and n2 > 1e-8 else 0
                angle_s = np.degrees(np.arccos(np.clip(cos_s, -1, 1)))

                pair = f"{d1}-{d2}"
                sep_teacher[pair] = angle_t
                sep_student[pair] = angle_s
                delta = abs(angle_t - angle_s)
                print(f"    {pair:25s}: teacher={angle_t:5.1f}°, "
                      f"student={angle_s:5.1f}°, Δ={delta:.1f}°")

        # ── Angular separation preservation ──
        teacher_angles = np.array(list(sep_teacher.values()))
        student_angles = np.array(list(sep_student.values()))
        if len(teacher_angles) > 1:
            angle_corr = float(np.corrcoef(teacher_angles, student_angles)[0, 1])
        else:
            angle_corr = 0.0
        print(f"  Angular separation correlation: {angle_corr:.4f}")

        # ── Per-dimension alignment quality ──
        # How well does each Procrustes dimension align?
        dim_alignment = proc["singular_values"] / proc["singular_values"].max()
        n_good_dims = int((dim_alignment > 0.5).sum())
        n_great_dims = int((dim_alignment > 0.8).sum())
        print(f"  Dimension quality: {n_great_dims} great (>0.8), "
              f"{n_good_dims} good (>0.5) out of {k}")

        # Store layer results
        results["layers"][f"L{li}"] = {
            "rsa_full_space": float(rsa_full),
            "rsa_beam_before": float(rsa_beam_before),
            "rsa_beam_after": float(rsa_beam_after),
            "cos_direct_before": float(cos_direct_before),
            "cos_direct_after": float(cos_direct_after),
            "procrustes_residual": float(proc["residual"]),
            "procrustes_scaled_residual": float(proc["scaled_residual"]),
            "procrustes_scale": float(proc["scale"]),
            "procrustes_singular_values": proc["singular_values"].tolist(),
            "teacher_eff_dim": float(beam_teacher["eff_dim"]),
            "student_eff_dim": float(beam_student["eff_dim"]),
            "teacher_cumvar": float(beam_teacher["cumvar"]),
            "student_cumvar": float(beam_student["cumvar"]),
            "domain_results": domain_results,
            "cross_domain_separation_teacher": {k: float(v) for k, v in sep_teacher.items()},
            "cross_domain_separation_student": {k: float(v) for k, v in sep_student.items()},
            "angular_separation_correlation": float(angle_corr),
            "n_great_dims": n_great_dims,
            "n_good_dims": n_good_dims,
        }

    # ── Summary ──
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")

    all_cos_after = []
    all_rsa_full = []
    all_angle_corr = []
    for li in target_layers:
        lr = results["layers"][f"L{li}"]
        all_cos_after.append(lr["cos_direct_after"])
        all_rsa_full.append(lr["rsa_full_space"])
        all_angle_corr.append(lr["angular_separation_correlation"])

    print(f"\n  Per-layer Procrustes quality:")
    print(f"  {'Layer':>6s}  {'RSA(full)':>10s}  {'cos(before)':>12s}  {'cos(after)':>11s}  {'Δ angle corr':>12s}")
    for li in target_layers:
        lr = results["layers"][f"L{li}"]
        print(f"  L{li:>4d}  {lr['rsa_full_space']:>10.4f}  "
              f"{lr['cos_direct_before']:>12.4f}  "
              f"{lr['cos_direct_after']:>11.4f}  "
              f"{lr['angular_separation_correlation']:>12.4f}")

    results["summary"] = {
        "mean_cos_after_procrustes": float(np.mean(all_cos_after)),
        "mean_rsa_full_space": float(np.mean(all_rsa_full)),
        "mean_angular_sep_correlation": float(np.mean(all_angle_corr)),
        "verdict": "ROTATION_SUFFICIENT" if np.mean(all_cos_after) > 0.5
                   else "NEEDS_NONLINEAR" if np.mean(all_cos_after) > 0.2
                   else "TOPOLOGY_ONLY",
    }

    verdict = results["summary"]["verdict"]
    mean_cos = results["summary"]["mean_cos_after_procrustes"]

    print(f"\n  Mean cosine after Procrustes: {mean_cos:.4f}")
    print(f"  Mean RSA (full space):        {np.mean(all_rsa_full):.4f}")
    print(f"  Mean angular sep correlation: {np.mean(all_angle_corr):.4f}")
    print(f"\n  VERDICT: {verdict}")

    if verdict == "ROTATION_SUFFICIENT":
        print("  → The Procrustes rotation is sufficient!")
        print("  → The lens is a parameter-free adapter: PCA + rotation + scale")
        print("  → Teacher beam → rotate → scale → student space")
    elif verdict == "NEEDS_NONLINEAR":
        print("  → Rotation captures partial structure but needs refinement")
        print("  → A small learned adapter in beam space (k×k MLP) should work")
    else:
        print("  → Topology transfers (RSA) but coordinates are too different")
        print("  → Fall back to relational loss (what we already have)")
        print("  → Or: use domain-specific Procrustes (split by domain, align each separately)")

    return results


# ══════════════════════════════════════════════════════════════════
# Phase 4b: Visualization
# ══════════════════════════════════════════════════════════════════


def plot_results(
    teacher_data: dict,
    student_data: dict,
    teacher_key: str,
    student_key: str,
    target_layers: list[int],
    k: int,
    domains: list[str],
    output_dir: Path,
):
    """Generate visualization plots."""
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available, skipping plots")
        return

    n_layers = len(target_layers)
    fig, axes = plt.subplots(n_layers, 3, figsize=(18, 5 * n_layers))
    if n_layers == 1:
        axes = axes[None, :]

    colors = {"tool_call": "#e74c3c", "code": "#3498db", "factual": "#2ecc71", "reasoning": "#f39c12"}
    domain_labels = teacher_data[f"{teacher_key}_domain_labels"]

    for row, li in enumerate(target_layers):
        hs_teacher = teacher_data[f"{teacher_key}_L{li}_all"]
        hs_student = student_data[f"{student_key}_L{li}_all"]

        beam_teacher = compute_beam_subspace(hs_teacher, k)
        beam_student = compute_beam_subspace(hs_student, k)
        proc = orthogonal_procrustes(beam_teacher["projected"], beam_student["projected"])

        aligned = beam_teacher["projected"] @ proc["R"] * proc["scale"]

        # Plot 1: Teacher beam space (PC1 vs PC2)
        ax = axes[row, 0]
        for domain in domains:
            mask = domain_labels == domain
            ax.scatter(
                beam_teacher["projected"][mask, 0],
                beam_teacher["projected"][mask, 1],
                c=colors.get(domain, "gray"), label=domain, alpha=0.6, s=30,
            )
        ax.set_title(f"L{li} — Teacher beam (PC1 vs PC2)")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.legend(fontsize=8)

        # Plot 2: Student beam space (PC1 vs PC2)
        ax = axes[row, 1]
        for domain in domains:
            mask = domain_labels == domain
            ax.scatter(
                beam_student["projected"][mask, 0],
                beam_student["projected"][mask, 1],
                c=colors.get(domain, "gray"), label=domain, alpha=0.6, s=30,
            )
        ax.set_title(f"L{li} — Student beam (PC1 vs PC2)")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.legend(fontsize=8)

        # Plot 3: Aligned teacher vs student (overlay)
        ax = axes[row, 2]
        for domain in domains:
            mask = domain_labels == domain
            ax.scatter(
                aligned[mask, 0], aligned[mask, 1],
                c=colors.get(domain, "gray"), marker="o", alpha=0.4, s=20,
                label=f"{domain} (teacher→aligned)",
            )
            ax.scatter(
                beam_student["projected"][mask, 0],
                beam_student["projected"][mask, 1],
                c=colors.get(domain, "gray"), marker="x", alpha=0.6, s=20,
            )
        ax.set_title(f"L{li} — Aligned teacher (○) vs student (×)")
        ax.set_xlabel("PC1")
        ax.set_ylabel("PC2")
        ax.legend(fontsize=7)

    plt.tight_layout()
    plt.savefig(output_dir / "procrustes_beam_alignment.png", dpi=150)
    plt.close()
    print(f"\n  Saved: {output_dir / 'procrustes_beam_alignment.png'}")

    # ── Plot: Procrustes singular values per layer ──
    fig, ax = plt.subplots(figsize=(10, 6))
    for li in target_layers:
        hs_teacher = teacher_data[f"{teacher_key}_L{li}_all"]
        hs_student = student_data[f"{student_key}_L{li}_all"]
        beam_teacher = compute_beam_subspace(hs_teacher, k)
        beam_student = compute_beam_subspace(hs_student, k)
        proc = orthogonal_procrustes(beam_teacher["projected"], beam_student["projected"])
        sv = proc["singular_values"][:k]
        ax.plot(range(k), sv / sv.max(), label=f"L{li}", marker=".", markersize=4)
    ax.set_xlabel("Procrustes dimension")
    ax.set_ylabel("Normalized alignment strength")
    ax.set_title("Per-dimension alignment quality (Procrustes singular values)")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_dir / "procrustes_dimension_quality.png", dpi=150)
    plt.close()
    print(f"  Saved: {output_dir / 'procrustes_dimension_quality.png'}")

    # ── Plot: Angular separation preservation ──
    fig, axes_sep = plt.subplots(1, len(target_layers), figsize=(5 * len(target_layers), 5))
    if len(target_layers) == 1:
        axes_sep = [axes_sep]

    for idx, li in enumerate(target_layers):
        ax = axes_sep[idx]
        hs_teacher = teacher_data[f"{teacher_key}_L{li}_all"]
        hs_student = student_data[f"{student_key}_L{li}_all"]
        beam_teacher = compute_beam_subspace(hs_teacher, k)
        beam_student = compute_beam_subspace(hs_student, k)
        proc = orthogonal_procrustes(beam_teacher["projected"], beam_student["projected"])
        aligned = beam_teacher["projected"] @ proc["R"] * proc["scale"]

        teacher_angles = []
        student_angles = []
        pair_labels = []

        for i, d1 in enumerate(domains):
            for d2 in domains[i+1:]:
                mask1 = domain_labels == d1
                mask2 = domain_labels == d2
                # Teacher (aligned)
                c1_t = aligned[mask1].mean(axis=0)
                c2_t = aligned[mask2].mean(axis=0)
                cos_t = np.dot(c1_t, c2_t) / (np.linalg.norm(c1_t) * np.linalg.norm(c2_t) + 1e-8)
                angle_t = np.degrees(np.arccos(np.clip(cos_t, -1, 1)))
                # Student
                c1_s = beam_student["projected"][mask1].mean(axis=0)
                c2_s = beam_student["projected"][mask2].mean(axis=0)
                cos_s = np.dot(c1_s, c2_s) / (np.linalg.norm(c1_s) * np.linalg.norm(c2_s) + 1e-8)
                angle_s = np.degrees(np.arccos(np.clip(cos_s, -1, 1)))

                teacher_angles.append(angle_t)
                student_angles.append(angle_s)
                pair_labels.append(f"{d1[:4]}-{d2[:4]}")

        ax.scatter(teacher_angles, student_angles, c="royalblue", s=60, zorder=5)
        for j, label in enumerate(pair_labels):
            ax.annotate(label, (teacher_angles[j], student_angles[j]),
                       fontsize=7, ha="center", va="bottom")

        # Perfect alignment line
        min_a = min(min(teacher_angles), min(student_angles))
        max_a = max(max(teacher_angles), max(student_angles))
        ax.plot([min_a, max_a], [min_a, max_a], "k--", alpha=0.3, label="perfect")
        ax.set_xlabel("Teacher angle (°)")
        ax.set_ylabel("Student angle (°)")
        ax.set_title(f"L{li} — Domain separation preservation")
        ax.legend()
        ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig(output_dir / "angular_separation_preservation.png", dpi=150)
    plt.close()
    print(f"  Saved: {output_dir / 'angular_separation_preservation.png'}")


# ══════════════════════════════════════════════════════════════════
# Phase 5: Lens artifact — save the adapter for downstream use
# ══════════════════════════════════════════════════════════════════


def save_lens_artifact(
    teacher_data: dict,
    student_data: dict,
    teacher_key: str,
    student_key: str,
    target_layers: list[int],
    k: int,
    output_dir: Path,
):
    """Save the computed lens as a reusable artifact.

    The lens artifact contains everything needed to project teacher
    beam space → student beam space:
    - PCA basis for teacher (per layer)
    - PCA basis for student (per layer)
    - Procrustes rotation R (per layer)
    - Magnitude scale (per layer)
    - Mean vectors for centering (per layer)
    """
    lens = {}
    for li in target_layers:
        hs_teacher = teacher_data[f"{teacher_key}_L{li}_all"]
        hs_student = student_data[f"{student_key}_L{li}_all"]

        beam_teacher = compute_beam_subspace(hs_teacher, k)
        beam_student = compute_beam_subspace(hs_student, k)
        proc = orthogonal_procrustes(beam_teacher["projected"], beam_student["projected"])

        lens[f"L{li}"] = {
            "teacher_basis": beam_teacher["basis"],        # (k, d_model)
            "student_basis": beam_student["basis"],        # (k, d_model)
            "teacher_mean": beam_teacher["mean"],          # (d_model,)
            "student_mean": beam_student["mean"],          # (d_model,)
            "rotation": proc["R"],                         # (k, k)
            "scale": proc["scale"],                        # scalar
            "teacher_singular_values": beam_teacher["singular_values"],
            "student_singular_values": beam_student["singular_values"],
            "procrustes_singular_values": proc["singular_values"],
        }

    # Save as npz
    flat = {}
    for layer_key, layer_data in lens.items():
        for name, arr in layer_data.items():
            flat[f"{layer_key}_{name}"] = np.array(arr)

    npz_path = output_dir / "procrustes_lens.npz"
    np.savez_compressed(str(npz_path), **flat)
    print(f"\n  Saved lens artifact: {npz_path}")
    print(f"  Lens size: {npz_path.stat().st_size / 1024:.1f} KB")

    # Print lens usage recipe
    print(f"\n  ═══ LENS USAGE RECIPE ═══")
    print(f"  # Load the lens")
    print(f"  lens = np.load('{npz_path}')")
    print(f"  # Project a teacher hidden state (d_model,) → student beam space (k,)")
    print(f"  teacher_basis = lens['L20_teacher_basis']     # (k, d_model)")
    print(f"  student_basis = lens['L20_student_basis']     # (k, d_model)")
    print(f"  R = lens['L20_rotation']                      # (k, k)")
    print(f"  scale = lens['L20_scale']                     # scalar")
    print(f"  mean_t = lens['L20_teacher_mean']             # (d_model,)")
    print(f"  mean_s = lens['L20_student_mean']             # (d_model,)")
    print(f"  ")
    print(f"  # Transform: teacher space → student space")
    print(f"  beam_t = teacher_basis @ (h_teacher - mean_t)  # project to beam")
    print(f"  beam_aligned = beam_t @ R * scale              # rotate + scale")
    print(f"  h_student_predicted = student_basis.T @ beam_aligned + mean_s  # back to d_model")

    return lens


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Procrustes Lens — parameter-free adapter probe")
    parser.add_argument("--teacher", default="qwen3-14b", choices=list(MODELS.keys()))
    parser.add_argument("--student", default="olmo-2-13b", choices=list(MODELS.keys()))
    parser.add_argument("--beam-dims", type=int, default=20,
                       help="Number of PCA dimensions for beam subspace (default: 20)")
    parser.add_argument("--layers", type=str, default="0,10,20,30",
                       help="Comma-separated layer indices to probe")
    parser.add_argument("--output-dir", type=str, default=str(OUTPUT_DIR))
    parser.add_argument("--quick", action="store_true",
                       help="Use 5 probes per domain instead of 25")
    parser.add_argument("--device", type=str, default=None)
    parser.add_argument("--skip-plots", action="store_true")
    parser.add_argument("--teacher-cache", type=str, default=None,
                       help="Path to cached teacher activations (npz)")
    parser.add_argument("--student-cache", type=str, default=None,
                       help="Path to cached student activations (npz)")
    args = parser.parse_args()

    target_layers = [int(x) for x in args.layers.split(",")]
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    if args.device is None:
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"
    else:
        device = args.device

    # Build probes
    probes = build_quick_probes() if args.quick else build_probes()
    domains = list(probes.keys())
    total_probes = sum(len(p) for p in probes.values())
    print(f"\nProbes: {total_probes} across {len(domains)} domains: {domains}")
    print(f"Beam dimensions: {args.beam_dims}")
    print(f"Target layers: {target_layers}")
    print(f"Device: {device}")

    # Phase 1: Collect teacher activations
    if args.teacher_cache:
        print(f"\nLoading cached teacher activations from {args.teacher_cache}")
        teacher_data_raw = np.load(args.teacher_cache, allow_pickle=True)
        teacher_data = {k: teacher_data_raw[k] for k in teacher_data_raw.files}
    else:
        teacher_data = collect_activations(args.teacher, target_layers, probes, device)
        # Cache for reuse
        cache_path = output_dir / f"{args.teacher}_activations.npz"
        np.savez_compressed(str(cache_path), **teacher_data)
        print(f"  Cached teacher activations: {cache_path}")

    # Phase 2: Collect student activations
    if args.student_cache:
        print(f"\nLoading cached student activations from {args.student_cache}")
        student_data_raw = np.load(args.student_cache, allow_pickle=True)
        student_data = {k: student_data_raw[k] for k in student_data_raw.files}
    else:
        student_data = collect_activations(args.student, target_layers, probes, device)
        cache_path = output_dir / f"{args.student}_activations.npz"
        np.savez_compressed(str(cache_path), **student_data)
        print(f"  Cached student activations: {cache_path}")

    # Phase 3 & 4: Evaluate lens
    results = evaluate_lens(
        teacher_data, student_data,
        args.teacher, args.student,
        target_layers, args.beam_dims, domains,
    )

    # Save results
    # Make JSON-serializable
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

    results_path = output_dir / "procrustes_results.json"
    results_path.write_text(json.dumps(make_serializable(results), indent=2))
    print(f"\n  Saved results: {results_path}")

    # Phase 4b: Plots
    if not args.skip_plots:
        plot_results(
            teacher_data, student_data,
            args.teacher, args.student,
            target_layers, args.beam_dims, domains,
            output_dir,
        )

    # Phase 5: Save lens artifact
    lens = save_lens_artifact(
        teacher_data, student_data,
        args.teacher, args.student,
        target_layers, args.beam_dims,
        output_dir,
    )

    print(f"\n{'='*60}")
    print("DONE")
    print(f"{'='*60}")
    print(f"Results: {output_dir}")
    print(f"\nNext steps:")
    print(f"  If ROTATION_SUFFICIENT:")
    print(f"    → Use lens to project teacher activations → etch signal for V12")
    print(f"    → The interference pattern (projected_teacher - student) drives sign flips")
    print(f"    → Build: scripts/explore/holographic_etch_with_lens.py")
    print(f"  If NEEDS_NONLINEAR:")
    print(f"    → Add a small MLP adapter in beam space ({args.beam_dims}→{args.beam_dims})")
    print(f"    → Train on calibration examples, then use for etching")
    print(f"  If TOPOLOGY_ONLY:")
    print(f"    → Fall back to per-domain Procrustes (each domain gets its own R)")
    print(f"    → Or: use relational loss as-is (already works at +6.9%)")


if __name__ == "__main__":
    main()
