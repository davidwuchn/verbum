"""Behavioral Crystal Experiment — find universal behavioral functions across models.

Do tool calling, summarization, analysis, etc. reduce to the same
internal geometry in every model? If yes, those geometries are normal
forms — irreducible compiled functions that can be etched.

Protocol (same as PCA-Q combinator crystal measurement):
  1. Hook Q-proj at 5 depths
  2. Run behavioral probes (10+ categories, 4-5 probes each)
  3. PCA project (k=64)
  4. Compute N×N cosine matrix (category-averaged)
  5. Compare across models

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/behavioral_crystal_exp.py --model qwen3-32b
    uv run python scripts/v12/behavioral_crystal_exp.py --model mistral-7b
    uv run python scripts/v12/behavioral_crystal_exp.py --model pythia-2.8b
    uv run python scripts/v12/behavioral_crystal_exp.py --model qwen3-14b

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
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "behavioral-crystal"


def log(msg):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Behavioral Probe Set
# ══════════════════════════════════════════════════════════════════════

BEHAVIORAL_PROBES = {
    "tool_calling": [
        "Use the calculator tool to compute 17 * 23 and return the result.",
        "Call the weather API to get the current temperature in Tokyo.",
        "Search the database for all users named 'Smith' and return their emails.",
        "Use the code interpreter to run: print(sorted([3,1,4,1,5,9]))",
        "Call the translation service to translate 'hello world' to Japanese.",
    ],
    "summarization": [
        "Summarize the following in one sentence: The quick brown fox jumps over the lazy dog. The dog was sleeping peacefully in the sun. The fox was in a hurry to get home before dark.",
        "Write a brief summary: Machine learning models learn patterns from data. They use these patterns to make predictions on new, unseen data. Training requires large datasets and significant compute.",
        "Condense this to key points: The economy grew 3.2% last quarter. Unemployment fell to 4.1%. Inflation remained at 2.5%. Consumer spending increased by 1.8%.",
        "Summarize: DNA contains the genetic instructions for all living organisms. It consists of four nucleotide bases: adenine, thymine, guanine, and cytosine. The sequence of these bases encodes information.",
        "Give a one-line summary: The committee met on Tuesday to discuss the budget. They agreed to reduce spending by 15% across all departments. The changes take effect next quarter.",
    ],
    "analysis": [
        "Analyze the pros and cons of remote work versus office work.",
        "What are the key factors driving inflation in 2024?",
        "Compare and contrast renewable energy sources: solar, wind, and hydro.",
        "Evaluate the strengths and weaknesses of this argument: All birds can fly. Penguins are birds. Therefore penguins can fly.",
        "Analyze why some startups succeed while most fail.",
    ],
    "instruction_following": [
        "List exactly three fruits that are red. Use bullet points.",
        "Write the numbers 1 through 5, each on a separate line.",
        "Respond with only the word 'yes' or 'no': Is the sky blue?",
        "Rewrite this sentence in passive voice: The cat chased the mouse.",
        "Format the following as a JSON object with keys 'name' and 'age': John is 30 years old.",
    ],
    "code_generation": [
        "Write a Python function that reverses a string.",
        "Implement binary search in Python.",
        "Write a function to check if a number is prime.",
        "Create a Python class for a stack data structure with push and pop methods.",
        "Write a function that finds the longest common subsequence of two strings.",
    ],
    "classification": [
        "Is this review positive or negative? 'The food was terrible and the service was slow.'",
        "Classify this text as spam or not spam: 'You have won a free iPhone! Click here now!'",
        "Is this sentence about science, politics, or sports? 'The team scored three goals in the second half.'",
        "Determine the sentiment: 'I absolutely loved this movie, it was fantastic!'",
        "Is this a question, statement, or command? 'Please close the door when you leave.'",
    ],
    "extraction": [
        "Extract all dates mentioned: The meeting is on March 15, 2025. The deadline was January 1, 2025. The project started on November 30, 2024.",
        "List all person names: John Smith met with Dr. Sarah Johnson and Professor Michael Chen at the conference.",
        "Extract the key numbers: Revenue was $4.2 billion, up 12% from last year. Operating margin improved to 23.5%.",
        "Identify all locations: She traveled from Paris to London, then flew to New York before returning to Tokyo.",
        "Extract the action items: We need to finish the report by Friday, schedule a meeting with the client, and update the database.",
    ],
    "translation": [
        "Translate to French: The weather is beautiful today.",
        "Translate to Spanish: Where is the nearest hospital?",
        "Translate to German: I would like to order a coffee, please.",
        "Translate to Japanese: Thank you for your help.",
        "Translate to Italian: The restaurant is closed on Mondays.",
    ],
    "chain_of_thought": [
        "Think step by step: If all roses are flowers, and all flowers need water, do roses need water?",
        "Solve step by step: A train leaves at 9:00 AM going 60 mph. Another leaves at 10:00 AM going 80 mph. When does the second train catch up?",
        "Reason through this: If it takes 5 machines 5 minutes to make 5 widgets, how long does it take 100 machines to make 100 widgets?",
        "Work through the logic: In a room of 23 people, what is the probability that at least two share a birthday? Explain your reasoning.",
        "Think carefully: A bat and ball cost $1.10 total. The bat costs $1.00 more than the ball. How much does the ball cost?",
    ],
    "qa_retrieval": [
        "What is the capital of France?",
        "Who wrote Romeo and Juliet?",
        "What is the boiling point of water in Celsius?",
        "What year did World War II end?",
        "What is the chemical symbol for gold?",
    ],
    "creative_writing": [
        "Write a haiku about the ocean.",
        "Describe a sunset in three sentences.",
        "Write an opening line for a mystery novel.",
        "Create a metaphor for loneliness.",
        "Write a short dialogue between a cat and a dog.",
    ],
    "comparison": [
        "Which is faster, a cheetah or a falcon?",
        "Compare Python and JavaScript for web development.",
        "What are the differences between TCP and UDP?",
        "Compare the French Revolution and the American Revolution.",
        "Which is a better investment: stocks or real estate?",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Model loading + hook infrastructure
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
    """Get the Q projection module for hooking."""
    if "pythia" in model_key:
        # Fused QKV — we'll slice Q out in the hook
        return model.gpt_neox.layers[layer_idx].attention.query_key_value, "fused"
    else:
        # Separate Q/K/V
        return model.model.layers[layer_idx].self_attn.q_proj, "separate"


def extract_behavioral_features(model, tokenizer, model_key, probes_flat, layer_indices):
    """Run all probes, capture Q-proj hidden states at specified layers.

    Returns: dict[layer_idx] -> np.array (n_probes, d_q)
    """
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

    # Stack into arrays
    result = {}
    for li in layer_indices:
        import torch as _t
        result[li] = _t.cat(captures[li], dim=0).numpy()

    return result


# ══════════════════════════════════════════════════════════════════════
# PCA + cosine crystal measurement
# ══════════════════════════════════════════════════════════════════════

def pca_project(X, k=64):
    """PCA project (n_samples, d) -> (n_samples, k)."""
    X_centered = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_centered, full_matrices=False)
    return X_centered @ Vt[:k].T


def compute_behavioral_crystal(features, category_indices, k=64):
    """Compute N×N cosine matrix between behavioral categories.

    features: (n_probes, d) — raw Q hidden states
    category_indices: dict[category_name] -> list of probe indices

    Returns: (n_categories, n_categories) cosine matrix, category names
    """
    # PCA project
    projected = pca_project(features, k=k)

    # Category-averaged vectors
    cat_names = sorted(category_indices.keys())
    cat_vecs = []
    for cat in cat_names:
        indices = category_indices[cat]
        cat_vec = projected[indices].mean(axis=0)
        cat_vecs.append(cat_vec)

    cat_vecs = np.array(cat_vecs)  # (n_cats, k)

    # Normalize
    norms = np.linalg.norm(cat_vecs, axis=1, keepdims=True)
    cat_vecs_norm = cat_vecs / np.maximum(norms, 1e-8)

    # Cosine matrix
    cos_matrix = cat_vecs_norm @ cat_vecs_norm.T

    return cos_matrix, cat_names


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Behavioral Crystal Experiment")
    parser.add_argument("--model", type=str, required=True,
                        choices=list(MODELS.keys()))
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    model_key = args.model
    model_name, n_layers, d_model = MODELS[model_key]

    log("═══════════════════════════════════════════════════════")
    log(f"  Behavioral Crystal — {model_key}")
    log(f"  {n_layers} layers, d_model={d_model}")
    log(f"  {len(BEHAVIORAL_PROBES)} categories, "
        f"{sum(len(v) for v in BEHAVIORAL_PROBES.values())} probes")
    log("═══════════════════════════════════════════════════════")

    t0 = time.time()

    # Flatten probes, track category indices
    probes_flat = []
    category_indices = {}
    for cat_name, prompts in sorted(BEHAVIORAL_PROBES.items()):
        start = len(probes_flat)
        probes_flat.extend(prompts)
        category_indices[cat_name] = list(range(start, len(probes_flat)))
        log(f"  {cat_name}: {len(prompts)} probes (indices {start}-{len(probes_flat)-1})")

    # Compute layer indices from depth fractions
    layer_indices = [min(int(round(d * (n_layers - 1))), n_layers - 1)
                     for d in DEPTH_FRACTIONS]
    log(f"\n  Depth fractions {DEPTH_FRACTIONS} → layers {layer_indices}")

    # Load model
    model, tokenizer = load_model(model_key)

    # Extract features
    features = extract_behavioral_features(
        model, tokenizer, model_key, probes_flat, layer_indices)

    # Free model memory
    del model, tokenizer
    gc.collect()
    import torch
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # Compute behavioral crystal at each depth
    log("\n═══ Computing behavioral crystals ═══")
    crystals = {}
    for li, depth in zip(layer_indices, DEPTH_FRACTIONS):
        cos_matrix, cat_names = compute_behavioral_crystal(
            features[li], category_indices, k=PCA_K)
        crystals[f"depth_{depth:.1f}"] = {
            "layer": li,
            "depth": depth,
            "cosine_matrix": cos_matrix.tolist(),
            "categories": cat_names,
        }

        log(f"\n  Depth {depth:.0%} (layer {li}):")
        n = len(cat_names)
        # Print matrix
        header = "            " + " ".join(f"{c[:6]:>7s}" for c in cat_names)
        log(header)
        for i in range(n):
            row = f"  {cat_names[i]:>10s} "
            for j in range(n):
                v = cos_matrix[i, j]
                if i == j:
                    row += f"  {'1.00':>5s} "
                else:
                    row += f"  {v:+.3f} "
            log(row)

    # Compute depth-averaged crystal (the "consensus" behavioral crystal)
    log("\n═══ Depth-averaged behavioral crystal ═══")
    all_matrices = [np.array(c["cosine_matrix"]) for c in crystals.values()]
    avg_matrix = np.mean(all_matrices, axis=0)

    log("            " + " ".join(f"{c[:6]:>7s}" for c in cat_names))
    for i in range(len(cat_names)):
        row = f"  {cat_names[i]:>10s} "
        for j in range(len(cat_names)):
            if i == j:
                row += f"  {'1.00':>5s} "
            else:
                row += f"  {avg_matrix[i, j]:+.3f} "
        log(row)

    # Find strongest clusters (highest average within-cluster similarity)
    log("\n═══ Behavioral clusters (avg off-diagonal similarity) ═══")
    n = len(cat_names)
    avg_sims = []
    for i in range(n):
        others = [avg_matrix[i, j] for j in range(n) if i != j]
        avg_sims.append((cat_names[i], np.mean(others)))
    avg_sims.sort(key=lambda x: -x[1])
    for name, sim in avg_sims:
        bar = "█" * int(max(0, sim + 0.5) * 20)
        log(f"  {name:>20s}: {sim:+.3f}  {bar}")

    # Find strongest pairs
    log("\n═══ Strongest behavioral pairs ═══")
    pairs = []
    for i in range(n):
        for j in range(i+1, n):
            pairs.append((cat_names[i], cat_names[j], avg_matrix[i, j]))
    pairs.sort(key=lambda x: -x[2])
    for a, b, v in pairs[:15]:
        log(f"  {a:>20s} ↔ {b:<20s}: {v:+.3f}")
    log("  ...")
    for a, b, v in pairs[-5:]:
        log(f"  {a:>20s} ↔ {b:<20s}: {v:+.3f}")

    # Save results
    elapsed = time.time() - t0
    results = {
        "experiment": "behavioral_crystal",
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
