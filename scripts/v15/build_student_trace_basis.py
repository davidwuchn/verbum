"""Build expanded trace basis in STUDENT space (1280-dim).

Session 178. The KIBC crystal basis captures 3.5-6.7% of FFN functional
space. This script runs diverse probes through the v15 student and builds
a PCA basis per stride that captures 90%+ of the variance.

The basis replaces crystal_basis_d_model.npz for trace loss computation.
Same interface: (n_strides, n_components, d_model) but n_components=50
instead of 11, covering the task dispatch table + knowledge retrieval +
opcodes instead of just opcodes.

Usage:
    cd ~/src/verbum
    uv run python scripts/v15/build_student_trace_basis.py \
        --checkpoint checkpoints/v15-zeroed

License: MIT
"""

from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import mlx.core as mx
from sklearn.decomposition import PCA

# Add parent to path for v15 imports
sys.path.insert(0, str(Path(__file__).parent))
from model import TensorStatechart
from load_checkpoint import load_statechart
from config import V15Config


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def build_probes() -> list[dict]:
    """Same diverse probes as dimensional_analysis.py."""
    probes = []
    idx = 0
    cats = {
        "retrieval": [
            "The capital of France is",
            "The chemical symbol for gold is",
            "Albert Einstein was born in",
            "The largest ocean on Earth is the",
            "The currency of Japan is the",
            "Mount Everest is located in",
            "The speed of light is approximately",
            "The author of Romeo and Juliet is",
        ],
        "arithmetic": [
            "2 + 3 =", "15 × 7 =", "100 - 37 =", "144 / 12 =",
            "2^10 =", "sqrt(144) =", "The sum of 8 and 13 is",
            "What is 25 percent of 200?",
        ],
        "reasoning": [
            "If all dogs are mammals and Rex is a dog, then Rex is a",
            "If A implies B and B implies C, then A implies",
            "The opposite of hot is",
            "If today is Tuesday, tomorrow is",
            "All squares are rectangles. Is every rectangle a square?",
            "If it rains, the ground gets wet. The ground is wet. Can we conclude it rained?",
            "Which is larger: 3/4 or 5/8?",
            "If no cats are dogs and some pets are cats, then some pets are not",
        ],
        "code": [
            "def fibonacci(n):\n    ",
            "function quicksort(arr) {\n    ",
            "SELECT name FROM users WHERE",
            "import numpy as np\nnp.",
            "class LinkedList:\n    def __init__(self):\n        ",
            "for i in range(10):\n    print(",
            "const express = require('express');\nconst app = express();\napp.",
            'git commit -m "',
        ],
        "translation": [
            "Translate to French: Hello, how are you?",
            "Translate to Spanish: The cat is on the table.",
            "Translate to German: I love programming.",
            "Translate to Japanese: Good morning.",
            "In Chinese, 'thank you' is",
            "The French word for 'book' is",
            "Comment dit-on 'computer' en français?",
            "'Guten Morgen' means",
        ],
        "summarization": [
            "TL;DR: The Industrial Revolution was a period of major industrialization. Summary:",
            "In one sentence: Machine learning enables systems to learn from experience.",
            "Briefly: The water cycle involves evaporation, condensation, and precipitation.",
            "Summarize: DNA carries genetic instructions for development and reproduction.",
            "The gist: Photosynthesis converts light energy into chemical energy.",
            "Key takeaway: Neural networks consist of layers of interconnected nodes.",
        ],
        "creative": [
            "Once upon a time in a magical forest,",
            "Write a haiku about the ocean:",
            "A recipe for chocolate cake:\n1.",
            "Dear diary, today I",
            "The year is 2150. Humanity has",
            "Roses are red, violets are blue,",
        ],
        "instruction": [
            "Step 1: Open the terminal.\nStep 2:",
            "To install Python, first",
            "Please list the top 5 programming languages:",
            "Compare and contrast: Python vs JavaScript.",
            "Explain like I'm five: How does the internet work?",
            "Create a bullet-point list of vegetables:",
        ],
        "lambda": [
            "K a b =", "B f g x =", "C f x y =", "S K K x =",
            "W f x =", "(λx. f x) a =", "(λx. λy. x) a b =", "Y f =",
        ],
    }
    for cat, prompts in cats.items():
        for p in prompts:
            probes.append({"id": idx, "category": cat, "prompt": p})
            idx += 1
    return probes


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Build expanded PCA trace basis in student space")
    parser.add_argument("--checkpoint", default="checkpoints/v15-zeroed")
    parser.add_argument("--n-components", type=int, default=50,
                        help="Max PCA components per stride")
    args = parser.parse_args()

    t0 = time.time()
    checkpoint_dir = Path(args.checkpoint)
    n_components = args.n_components

    # Load student model
    log(f"Loading student from {checkpoint_dir}...")
    model = load_statechart(str(checkpoint_dir))
    config = model.config
    n_strides = config.n_strides
    d_model = config.d_model
    log(f"  {n_strides} strides, d_model={d_model}")

    # Load tokenizer (Qwen)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained(config.teacher_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    probes = build_probes()
    n_probes = len(probes)
    log(f"  {n_probes} probes")

    # Capture residuals for all probes
    log("Capturing per-stride residuals...")
    # per_stride[s] = list of (d_model,) arrays, one per probe
    per_stride = {s: [] for s in range(n_strides)}

    for pi, probe in enumerate(probes):
        ids = tokenizer.encode(probe["prompt"], return_tensors="np")
        input_ids = mx.array(ids)

        result = model(input_ids, return_residuals=True)
        residuals = result["residuals"]  # list of (1, seq_len, d_model) per stride
        mx.eval(residuals)

        for s in range(min(n_strides, len(residuals))):
            # Take last token position
            r = residuals[s][0, -1, :]  # (d_model,)
            per_stride[s].append(np.array(r, dtype=np.float32))

        if (pi + 1) % 10 == 0:
            log(f"  {pi + 1}/{n_probes}")

    # PCA per stride
    log(f"\nBuilding PCA basis per stride (max {n_components} components)...")
    all_components = np.zeros((n_strides, n_components, d_model), dtype=np.float32)
    all_variance = np.zeros((n_strides, n_components), dtype=np.float32)

    for s in range(n_strides):
        matrix = np.array(per_stride[s])  # (n_probes, d_model)
        norms = np.linalg.norm(matrix, axis=1, keepdims=True)
        norms = np.clip(norms, 1e-10, None)
        matrix_unit = matrix / norms

        k = min(n_components, n_probes - 1, d_model)
        pca = PCA(n_components=k)
        pca.fit(matrix_unit)

        n_actual = min(k, pca.components_.shape[0])
        all_components[s, :n_actual] = pca.components_[:n_actual]
        all_variance[s, :n_actual] = pca.explained_variance_ratio_[:n_actual]

        cumvar = np.cumsum(pca.explained_variance_ratio_)
        # How many PCs for 90%?
        dim90 = int(np.searchsorted(cumvar, 0.90) + 1)
        log(f"  Stride {s:02d}: dim90={dim90:>3d}  cum50={cumvar[min(49,k-1)]:.1%}  "
            f"PC0={pca.explained_variance_ratio_[0]:.1%}")

    # Save
    out_path = checkpoint_dir / "expanded_trace_basis.npz"
    np.savez_compressed(
        out_path,
        pca_components=all_components,       # (n_strides, n_components, d_model)
        explained_variance=all_variance,     # (n_strides, n_components)
        n_strides=n_strides,
        n_components=n_components,
        d_model=d_model,
        n_probes=n_probes,
    )
    size_mb = out_path.stat().st_size / 1024 / 1024
    log(f"\nSaved to {out_path} ({size_mb:.1f} MB)")

    # Summary
    mean_cumvar = np.mean([np.cumsum(all_variance[s])[-1] for s in range(n_strides)])
    old_basis = checkpoint_dir / "crystal_basis_d_model.npz"
    if old_basis.exists():
        old = np.load(old_basis)
        old_dims = old["per_stride_basis"].shape[1]
        log(f"\n  Old basis: {old_dims} dims (KIBC)")
    log(f"  New basis: {n_components} dims (PCA)")
    log(f"  Mean cumulative variance at {n_components} PCs: {mean_cumvar:.1%}")
    log(f"  Coverage improvement: ~{n_components / 11:.0f}× more dimensions")

    elapsed = time.time() - t0
    log(f"\n✅ Complete in {elapsed:.1f}s")


if __name__ == "__main__":
    main()
