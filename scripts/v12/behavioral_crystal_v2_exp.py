"""Behavioral Crystal V2 — Fine-grained sub-function discovery.

Break down coarse categories into sub-functions to find more
universal normal forms. Focus on code and reasoning subcategories
plus other fine-grained behavioral splits.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/behavioral_crystal_v2_exp.py --model qwen3-32b

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

MODELS = {
    "qwen3-32b":  ("Qwen/Qwen3-32B",                 64, 5120),
    "qwen3-14b":  ("Qwen/Qwen3-14B",                  40, 5120),
    "mistral-7b": ("mistralai/Mistral-7B-v0.3",       32, 4096),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b-deduped",  32, 2560),
}

DEPTH_FRACTIONS = [0.1, 0.3, 0.5, 0.7, 0.9]
PCA_K = 64
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "behavioral-crystal-v2"


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Fine-Grained Behavioral Probes
# ══════════════════════════════════════════════════════════════════════

BEHAVIORAL_PROBES = {
    # ── CODE subcategories ──
    "code_algorithm": [
        "Write a function to implement merge sort.",
        "Implement Dijkstra's shortest path algorithm.",
        "Write a function for depth-first search on a graph.",
        "Implement a least recently used (LRU) cache.",
    ],
    "code_syntax": [
        "Write a Python list comprehension that filters even numbers from a list.",
        "Create a dictionary comprehension from two lists of keys and values.",
        "Write a decorator that measures function execution time.",
        "Write a context manager for file handling using the with statement.",
    ],
    "code_debug": [
        "Find the bug: def factorial(n): return n * factorial(n) # missing base case",
        "This code has an off-by-one error. Fix it: for i in range(len(arr)): if arr[i] > arr[i+1]:",
        "Debug: why does this return None? def add(a, b): result = a + b",
        "Find the memory leak: while True: data = open('file.txt').read()",
    ],
    "code_refactor": [
        "Refactor this to remove duplication: if x > 0: print('positive'); do_pos() elif x < 0: print('negative'); do_neg()",
        "Convert this imperative loop to a functional map/filter: result = []; for x in items: if x > 0: result.append(x*2)",
        "Extract a function from this repeated pattern: conn = connect(); data = conn.query(sql); conn.close(); return data",
        "Simplify this nested conditional into a dictionary dispatch.",
    ],
    # ── REASONING subcategories ──
    "reason_deductive": [
        "All mammals are warm-blooded. Whales are mammals. Therefore, whales are",
        "If it rains, the ground gets wet. It is raining. Therefore,",
        "No reptiles have fur. Snakes are reptiles. Therefore, snakes",
        "Every prime number greater than 2 is odd. 17 is prime and greater than 2. Therefore,",
    ],
    "reason_inductive": [
        "I've seen 100 swans and they were all white. What can I conclude about swans?",
        "Every time I water this plant, it grows. What pattern can I infer?",
        "The last 5 earthquakes in this region happened in March. What might this suggest?",
        "Sales have increased every quarter for 8 quarters. What trend do you see?",
    ],
    "reason_abductive": [
        "The grass is wet but it hasn't rained. What is the best explanation?",
        "The patient has a fever, cough, and body aches. What is the most likely diagnosis?",
        "The car won't start, the lights don't turn on, and the radio is dead. What probably happened?",
        "There are cookie crumbs on the counter and the cookie jar is empty. What most likely occurred?",
    ],
    "reason_causal": [
        "What would happen if the Earth's rotation suddenly stopped?",
        "If interest rates rise by 2%, how would that affect the housing market?",
        "What are the downstream effects of removing wolves from Yellowstone?",
        "If all antibiotics stopped working tomorrow, what would the consequences be?",
    ],
    "reason_math": [
        "Solve: if 3x + 7 = 22, what is x?",
        "What is the probability of rolling two sixes with two dice?",
        "A triangle has sides 3, 4, and 5. Is it a right triangle? Show your work.",
        "If a car travels 60 mph for 2.5 hours, how far does it go?",
    ],
    # ── GENERATION subcategories ──
    "gen_narrative": [
        "Write a short paragraph about a rainy day in Tokyo.",
        "Describe a character who discovers a hidden door in their basement.",
        "Tell a story about the last tree on Earth in three sentences.",
        "Write the opening paragraph of a science fiction novel set on Mars.",
    ],
    "gen_technical": [
        "Write a README section explaining how to install this Python package.",
        "Draft a brief API documentation for a POST /users endpoint.",
        "Write a commit message for adding user authentication to a web app.",
        "Create a brief technical specification for a caching layer.",
    ],
    "gen_persuasive": [
        "Write a compelling argument for why companies should adopt remote work.",
        "Convince someone to start learning a musical instrument.",
        "Write a product description that makes a simple notebook sound exciting.",
        "Draft a fundraising appeal for a local library.",
    ],
    # ── FIND subcategories ──
    "find_entity": [
        "List all person names in: Dr. Sarah Chen presented her findings to Professor James Morton at the WHO conference in Geneva.",
        "Extract all organizations mentioned: Apple and Google partnered with the EU Commission on AI safety regulations.",
        "Identify all locations: The journey took us from Mumbai to Delhi, then to Kathmandu and finally Bangkok.",
        "Extract all dates: The contract was signed on March 15, 2024 and expires December 31, 2025.",
    ],
    "find_pattern": [
        "What is the next number in the sequence: 2, 6, 12, 20, 30, ?",
        "Complete the pattern: A1, B2, C3, D4, ?",
        "Find the rule: 1→1, 2→4, 3→9, 4→16, 5→?",
        "What comes next: Mon, Wed, Fri, ?",
    ],
    "find_fact": [
        "What is the speed of light in meters per second?",
        "What element has atomic number 79?",
        "In what year was the Magna Carta signed?",
        "What is the largest organ in the human body?",
    ],
    # ── EXECUTE subcategories ──
    "exec_format": [
        "Format the following data as a markdown table: Name: Alice, Age: 30, City: NYC; Name: Bob, Age: 25, City: LA",
        "Convert this to JSON: name is John, age is 30, hobbies are reading and hiking",
        "Rewrite this as bullet points: The project has three phases: design, implementation, and testing.",
        "Format this as a numbered list with sub-items: Frontend tasks: design UI, implement forms. Backend tasks: setup API, write tests.",
    ],
    "exec_transform": [
        "Convert this sentence to past tense: The dog runs across the park and catches the ball.",
        "Rewrite in third person: I went to the store and bought some groceries.",
        "Make this more formal: Hey, can u fix the bug in the login page? thx",
        "Simplify this for a 10-year-old: Photosynthesis is the process by which chloroplasts convert light energy into chemical energy.",
    ],
    "exec_follow": [
        "Respond with exactly one word: What color is the sky?",
        "List 3 items, no more no less, separated by commas: name some fruits.",
        "Answer in the format 'X because Y': Is exercise important?",
        "First translate to French, then count the words in the French version: The cat sleeps.",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Model loading + hook infrastructure (same as v1)
# ══════════════════════════════════════════════════════════════════════

def load_model(model_key):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    model_name, n_layers, d_model = MODELS[model_key]
    log(f"  Loading {model_name}...")
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype="auto",
        device_map="mps", trust_remote_code=True,
    )
    model.eval()
    log(f"  Loaded in {time.time()-t0:.1f}s")
    return model, tokenizer


def get_q_hook_module(model, model_key, layer_idx):
    if "pythia" in model_key:
        return model.gpt_neox.layers[layer_idx].attention.query_key_value, "fused"
    else:
        return model.model.layers[layer_idx].self_attn.q_proj, "separate"


def extract_behavioral_features(model, tokenizer, model_key, probes_flat, layer_indices):
    import torch

    _, n_layers, d_model = MODELS[model_key]
    captures = {li: [] for li in layer_indices}
    hooks = []

    for li in layer_indices:
        module, mode = get_q_hook_module(model, model_key, li)
        if mode == "fused":
            q_size = d_model
            def make_hook(layer_idx, qs):
                def hook_fn(m, inp, out):
                    captures[layer_idx].append(out[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(module.register_forward_hook(make_hook(li, q_size)))
        else:
            def make_hook(layer_idx):
                def hook_fn(m, inp, out):
                    captures[layer_idx].append(out[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(module.register_forward_hook(make_hook(li)))

    log(f"  Running {len(probes_flat)} probes across {len(layer_indices)} depths...")
    for pi, prompt in enumerate(probes_flat):
        ids = tokenizer.encode(prompt, return_tensors="pt", truncation=True, max_length=256).to("mps")
        with torch.no_grad():
            _ = model(ids)
        if (pi + 1) % 20 == 0:
            log(f"    {pi+1}/{len(probes_flat)}")

    for h in hooks:
        h.remove()

    result = {}
    for li in layer_indices:
        import torch as _t
        result[li] = _t.cat(captures[li], dim=0).numpy()

    return result


def pca_project(X, k=64):
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    return X_centered @ Vt[:k].T


def compute_behavioral_crystal(features, category_indices, k=64):
    projected = pca_project(features, k=k)
    cat_names = sorted(category_indices.keys())
    cat_vecs = []
    for cat in cat_names:
        indices = category_indices[cat]
        cat_vec = projected[indices].mean(axis=0)
        cat_vecs.append(cat_vec)

    cat_vecs = np.array(cat_vecs)
    norms = np.linalg.norm(cat_vecs, axis=1, keepdims=True)
    cat_vecs_norm = cat_vecs / np.maximum(norms, 1e-8)
    cos_matrix = cat_vecs_norm @ cat_vecs_norm.T
    return cos_matrix, cat_names


def main():
    parser = argparse.ArgumentParser(description="Behavioral Crystal V2")
    parser.add_argument("--model", type=str, required=True,
                        choices=list(MODELS.keys()))
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    model_key = args.model
    model_name, n_layers, d_model = MODELS[model_key]

    log("═══════════════════════════════════════════════════════")
    log(f"  Behavioral Crystal V2 — {model_key}")
    log(f"  {n_layers} layers, d_model={d_model}")
    log(f"  {len(BEHAVIORAL_PROBES)} categories, "
        f"{sum(len(v) for v in BEHAVIORAL_PROBES.values())} probes")
    log("═══════════════════════════════════════════════════════")

    t0 = time.time()

    probes_flat = []
    category_indices = {}
    for cat_name, prompts in sorted(BEHAVIORAL_PROBES.items()):
        start = len(probes_flat)
        probes_flat.extend(prompts)
        category_indices[cat_name] = list(range(start, len(probes_flat)))
        log(f"  {cat_name}: {len(prompts)} probes (indices {start}-{len(probes_flat)-1})")

    layer_indices = [min(int(round(d * (n_layers - 1))), n_layers - 1)
                     for d in DEPTH_FRACTIONS]
    log(f"\n  Depth fractions {DEPTH_FRACTIONS} → layers {layer_indices}")

    model, tokenizer = load_model(model_key)
    features = extract_behavioral_features(
        model, tokenizer, model_key, probes_flat, layer_indices)

    del model, tokenizer
    gc.collect()
    import torch
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    log("\n═══ Computing behavioral crystals ═══")
    crystals = {}
    for li, depth in zip(layer_indices, DEPTH_FRACTIONS):
        cos_matrix, cat_names = compute_behavioral_crystal(
            features[li], category_indices, k=PCA_K)
        crystals[f"depth_{depth:.1f}"] = {
            "layer": li, "depth": depth,
            "cosine_matrix": cos_matrix.tolist(),
            "categories": cat_names,
        }
        log(f"  Depth {depth:.0%} (layer {li}): computed {len(cat_names)}×{len(cat_names)} matrix")

    # Depth-averaged
    all_matrices = [np.array(c["cosine_matrix"]) for c in crystals.values()]
    avg_matrix = np.mean(all_matrices, axis=0)
    n = len(cat_names)

    # Print depth-averaged matrix
    log("\n═══ Depth-averaged behavioral crystal ═══")
    short = [c[:7] for c in cat_names]
    header = "            " + " ".join(f"{s:>8s}" for s in short)
    log(header)
    for i in range(n):
        row = f"  {cat_names[i]:>10s} "
        for j in range(n):
            if i == j:
                row += f"  {'1.00':>6s} "
            else:
                row += f"  {avg_matrix[i, j]:+.3f}  "
        log(row)

    # Strongest pairs
    log("\n═══ Strongest pairs (top 20 attractive + top 10 repulsive) ═══")
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append((cat_names[i], cat_names[j], avg_matrix[i, j]))

    pairs.sort(key=lambda x: -x[2])
    log("  ATTRACTIVE:")
    for a, b, v in pairs[:20]:
        log(f"    {a:>20s} ↔ {b:<20s}: {v:+.3f}")
    log("  REPULSIVE:")
    for a, b, v in pairs[-10:]:
        log(f"    {a:>20s} ↔ {b:<20s}: {v:+.3f}")

    # Parent-category clustering
    log("\n═══ Sub-function clustering (within parent category) ═══")
    parent_groups = {
        "CODE": ["code_algorithm", "code_syntax", "code_debug", "code_refactor"],
        "REASON": ["reason_deductive", "reason_inductive", "reason_abductive", "reason_causal", "reason_math"],
        "GENERATE": ["gen_narrative", "gen_technical", "gen_persuasive"],
        "FIND": ["find_entity", "find_pattern", "find_fact"],
        "EXECUTE": ["exec_format", "exec_transform", "exec_follow"],
    }

    for group_name, members in parent_groups.items():
        member_idx = [cat_names.index(m) for m in members if m in cat_names]
        if len(member_idx) < 2:
            continue
        intra_sims = []
        for ii, mi in enumerate(member_idx):
            for jj, mj in enumerate(member_idx):
                if jj <= ii: continue
                intra_sims.append(avg_matrix[mi, mj])
        log(f"  {group_name}: mean within-group = {np.mean(intra_sims):+.3f} "
            f"(range {np.min(intra_sims):+.3f} to {np.max(intra_sims):+.3f})")
        for ii, mi in enumerate(member_idx):
            for jj, mj in enumerate(member_idx):
                if jj <= ii: continue
                log(f"    {members[ii]:>18s} ↔ {members[jj]:<18s}: {avg_matrix[mi, mj]:+.3f}")

    elapsed = time.time() - t0
    results = {
        "experiment": "behavioral_crystal_v2",
        "model": model_name,
        "model_key": model_key,
        "n_layers": n_layers,
        "d_model": d_model,
        "pca_k": PCA_K,
        "n_categories": len(cat_names),
        "n_probes": len(probes_flat),
        "categories": cat_names,
        "category_indices": category_indices,
        "depth_fractions": DEPTH_FRACTIONS,
        "layer_indices": layer_indices,
        "crystals": crystals,
        "depth_averaged_matrix": avg_matrix.tolist(),
        "parent_groups": parent_groups,
        "elapsed_s": elapsed,
    }

    results_path = RESULTS_DIR / f"{model_key}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n═══════════════════════════════════════════════════════")
    log(f"  Done in {elapsed:.1f}s")
    log(f"  Results: {results_path}")
    log(f"═══════════════════════════════════════════════════════")


if __name__ == "__main__":
    main()
