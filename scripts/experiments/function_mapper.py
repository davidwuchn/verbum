"""Function Mapper — Map the program library stored in the holographic plate.

Session 172. The KIBC opcodes are the instruction set. This script maps
the higher-level PROGRAMS — discrete functional clusters composed from
those opcodes. Different tasks (retrieval, reasoning, tool use, summarization)
should activate different grating programs, visible as distinct clusters
in combinator activation space.

Approach:
  1. Build diverse probes across functional categories
  2. Capture FFN activations (combinator projections) across all layers
  3. Cluster the activation profiles
  4. Map clusters to combinator combinations
  5. Build the function table: which programs exist, what opcodes they use

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/function_mapper.py
    uv run python scripts/experiments/function_mapper.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "function-map"
HOLOGRAM_READER_DIR = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES
N_OPS = len(ALL_OP_NAMES)


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Functional Category Probes
# ══════════════════════════════════════════════════════════════════════

def build_function_probes() -> list[dict]:
    """Build probes spanning diverse functional categories."""
    probes = []

    # ── FACTUAL RETRIEVAL ──
    for prompt in [
        "The capital of France is",
        "The chemical symbol for gold is",
        "Albert Einstein was born in",
        "The largest ocean on Earth is the",
        "The currency of Japan is the",
        "Mount Everest is located in",
        "The speed of light is approximately",
        "The author of Romeo and Juliet is",
    ]:
        probes.append({"category": "retrieval", "prompt": prompt})

    # ── ARITHMETIC ──
    for prompt in [
        "2 + 3 =",
        "15 × 7 =",
        "100 - 37 =",
        "144 / 12 =",
        "2^10 =",
        "sqrt(144) =",
        "The sum of 8 and 13 is",
        "What is 25 percent of 200?",
    ]:
        probes.append({"category": "arithmetic", "prompt": prompt})

    # ── LOGICAL REASONING ──
    for prompt in [
        "If all dogs are mammals and Rex is a dog, then Rex is a",
        "If A implies B and B implies C, then A implies",
        "The opposite of hot is",
        "If today is Tuesday, tomorrow is",
        "All squares are rectangles. Is every rectangle a square?",
        "If it rains, the ground gets wet. The ground is wet. Can we conclude it rained?",
        "Which is larger: 3/4 or 5/8?",
        "If no cats are dogs and some pets are cats, then some pets are not",
    ]:
        probes.append({"category": "reasoning", "prompt": prompt})

    # ── CODE GENERATION ──
    for prompt in [
        "def fibonacci(n):\n    ",
        "function quicksort(arr) {\n    ",
        "SELECT name FROM users WHERE",
        "import numpy as np\nnp.",
        "class LinkedList:\n    def __init__(self):\n        ",
        "for i in range(10):\n    print(",
        "const express = require('express');\nconst app = express();\napp.",
        "git commit -m \"",
    ]:
        probes.append({"category": "code", "prompt": prompt})

    # ── TRANSLATION / LANGUAGE SWITCHING ──
    for prompt in [
        "Translate to French: Hello, how are you?",
        "Translate to Spanish: The cat is on the table.",
        "Translate to German: I love programming.",
        "Translate to Japanese: Good morning.",
        "In Chinese, 'thank you' is",
        "The French word for 'book' is",
        "Comment dit-on 'computer' en français?",
        "'Guten Morgen' means",
    ]:
        probes.append({"category": "translation", "prompt": prompt})

    # ── SUMMARIZATION / COMPRESSION ──
    for prompt in [
        "TL;DR: The Industrial Revolution was a period of major industrialization and innovation that took place during the late 1700s and early 1800s. Summary:",
        "In one sentence: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
        "Briefly: The water cycle involves evaporation, condensation, and precipitation. In short,",
        "Key takeaway: Neural networks consist of layers of interconnected nodes that process information. The main point is",
        "Summarize: DNA carries genetic instructions for development, functioning, growth, and reproduction of all known organisms.",
        "The gist: Photosynthesis converts light energy into chemical energy stored in glucose. Essentially,",
    ]:
        probes.append({"category": "summarization", "prompt": prompt})

    # ── CREATIVE / GENERATIVE ──
    for prompt in [
        "Once upon a time in a magical forest,",
        "Write a haiku about the ocean:",
        "A recipe for chocolate cake:\n1.",
        "Dear diary, today I",
        "The year is 2150. Humanity has",
        "Roses are red, violets are blue,",
    ]:
        probes.append({"category": "creative", "prompt": prompt})

    # ── INSTRUCTION FOLLOWING / TOOL USE ──
    for prompt in [
        "Step 1: Open the terminal.\nStep 2:",
        "To install Python, first",
        "Please list the top 5 programming languages:",
        "Compare and contrast: Python vs JavaScript.",
        "Explain like I'm five: How does the internet work?",
        "Create a bullet-point list of vegetables:",
    ]:
        probes.append({"category": "instruction", "prompt": prompt})

    # ── LAMBDA / COMBINATOR (control group — should show strong KIBC) ──
    for prompt in [
        "K a b =",
        "B f g x =",
        "C f x y =",
        "S K K x =",
        "W f x =",
        "(λx. f x) a =",
        "(λx. λy. x) a b =",
        "Y f =",
    ]:
        probes.append({"category": "lambda", "prompt": prompt})

    return probes


# ══════════════════════════════════════════════════════════════════════
# Mapper
# ══════════════════════════════════════════════════════════════════════

class FunctionMapper:
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.layers = None
        self.n_layers = 0
        self.d_model = 0
        self.fingerprints = {}
        self.results_dir = RESULTS_BASE / model_name.replace("/", "_")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        log(f"  Loading {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        dev = self.device
        if dev == "auto":
            if torch.cuda.is_available(): dev = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available(): dev = "mps"
            else: dev = "cpu"

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, torch_dtype=torch.bfloat16,
            device_map=dev if dev != "mps" else "auto",
            low_cpu_mem_usage=True, trust_remote_code=True)
        self.model.eval()

        self.n_layers = self.model.config.num_hidden_layers
        self.d_model = self.model.config.hidden_size

        for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
            obj = self.model
            try:
                for part in attr_path.split("."):
                    obj = getattr(obj, part)
                self.layers = list(obj)
                break
            except AttributeError:
                continue

        # Load fingerprints
        slug = self.model_name.replace("/", "_")
        fp_path = HOLOGRAM_READER_DIR / slug / f"fingerprints_{slug}.npz"
        if fp_path.exists():
            data = np.load(fp_path)
            self.fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
            log(f"  Loaded {len(self.fingerprints)} fingerprints")
        else:
            log(f"  ⚠ No fingerprints at {fp_path} — run hologram_reader.py first")
            sys.exit(1)

    def _capture_ffn(self, text: str, layer_indices: list[int]) -> dict[int, np.ndarray]:
        ids = self.tokenizer.encode(text, return_tensors="pt")
        device = next(self.model.parameters()).device
        ids = ids.to(device)
        captures = {}
        hooks = []
        for li in layer_indices:
            layer = self.layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer
            target = getattr(mlp, "down_proj", getattr(mlp, "dense_4h_to_h", None))
            if target is None: continue
            def make_hook(idx):
                def hook(m, inp, out):
                    captures[idx] = out[0, -1, :].detach().cpu().float().numpy()
                return hook
            hooks.append(target.register_forward_hook(make_hook(li)))
        with torch.no_grad():
            _ = self.model(input_ids=ids)
        for h in hooks:
            h.remove()
        return captures

    def _project_combinators(self, vec: np.ndarray, layer: int) -> dict[str, float]:
        norm = np.linalg.norm(vec)
        if norm < 1e-10:
            return {op: 0.0 for op in ALL_OP_NAMES}
        unit = vec / norm
        return {
            op: float(np.dot(unit, self.fingerprints[op][layer] / max(np.linalg.norm(self.fingerprints[op][layer]), 1e-10)))
            for op in ALL_OP_NAMES
        }

    def run(self):
        t0 = time.time()
        self._load()
        probes = build_function_probes()
        categories = sorted(set(p["category"] for p in probes))
        log(f"  {len(probes)} probes across {len(categories)} categories: {categories}")

        all_layers = list(range(self.n_layers))

        # ── Capture all probes ──
        # For each probe: compute the average |combinator projection| across all layers
        # This gives a "program signature" vector of length N_OPS
        probe_signatures = []  # (n_probes, N_OPS)
        probe_depth_profiles = []  # (n_probes, n_layers, N_OPS)
        probe_categories = []

        for pi, probe in enumerate(probes):
            caps = self._capture_ffn(probe["prompt"], all_layers)

            # Per-layer combinator projections
            depth_profile = np.zeros((self.n_layers, N_OPS), dtype=np.float32)
            for li in all_layers:
                if li in caps:
                    proj = self._project_combinators(caps[li], li)
                    for oi, op in enumerate(ALL_OP_NAMES):
                        depth_profile[li, oi] = proj[op]

            # Signature = mean |projection| across all layers
            signature = np.mean(np.abs(depth_profile), axis=0)
            probe_signatures.append(signature)
            probe_depth_profiles.append(depth_profile)
            probe_categories.append(probe["category"])

            if (pi + 1) % 10 == 0:
                log(f"    {pi+1}/{len(probes)}")

        signatures = np.array(probe_signatures)  # (n_probes, N_OPS)
        depth_profiles = np.array(probe_depth_profiles)  # (n_probes, n_layers, N_OPS)

        # ── Per-category average signature ──
        log(f"\n{'═' * 70}")
        log(f"  FUNCTION MAP: {self.model_name}")
        log(f"{'═' * 70}")

        category_signatures = {}
        for cat in categories:
            mask = [i for i, c in enumerate(probe_categories) if c == cat]
            cat_sigs = signatures[mask]
            mean_sig = np.mean(cat_sigs, axis=0)
            category_signatures[cat] = mean_sig

        # Print the function table
        log(f"\n  PROGRAM LIBRARY — Average |combinator activation| per category:")
        header = f"  {'Category':>14s}"
        for op in ALL_OP_NAMES:
            header += f" {op:>7s}"
        header += f" {'TOTAL':>7s}"
        log(header)
        log(f"  {'─'*14}" + f" {'─'*7}" * (N_OPS + 1))

        sorted_cats = sorted(category_signatures.keys(),
                             key=lambda c: np.sum(category_signatures[c]), reverse=True)
        for cat in sorted_cats:
            sig = category_signatures[cat]
            line = f"  {cat:>14s}"
            for v in sig:
                line += f" {v:>7.4f}"
            line += f" {np.sum(sig):>7.3f}"
            log(line)

        # ── Dominant opcode per category ──
        log(f"\n  DOMINANT OPCODES per category (top 3):")
        for cat in sorted_cats:
            sig = category_signatures[cat]
            ranked = sorted(zip(ALL_OP_NAMES, sig), key=lambda x: x[1], reverse=True)[:3]
            top_str = ", ".join(f"{op}({v:.4f})" for op, v in ranked)
            log(f"    {cat:>14s}: {top_str}")

        # ── Cross-category similarity ──
        log(f"\n  CROSS-CATEGORY COSINE SIMILARITY:")
        cat_vecs = np.array([category_signatures[c] for c in sorted_cats])
        norms = np.linalg.norm(cat_vecs, axis=1, keepdims=True)
        norms = np.clip(norms, 1e-10, None)
        cat_unit = cat_vecs / norms
        cos_matrix = cat_unit @ cat_unit.T

        header = f"  {'':>14s}"
        for cat in sorted_cats:
            header += f" {cat[:7]:>7s}"
        log(header)
        for i, cat in enumerate(sorted_cats):
            line = f"  {cat:>14s}"
            for j in range(len(sorted_cats)):
                line += f" {cos_matrix[i,j]:>7.3f}"
            log(line)

        # ── Depth profile per category ──
        log(f"\n  DEPTH PROFILE — Total combinator energy by depth zone:")
        log(f"  {'Category':>14s} {'SILENT':>8s} {'ENRICH':>8s} {'SUPP':>8s} {'COMMIT':>8s}")

        for cat in sorted_cats:
            mask = [i for i, c in enumerate(probe_categories) if c == cat]
            cat_depths = depth_profiles[mask]  # (n_cat, n_layers, N_OPS)
            # Sum absolute projections across ops, average across probes
            energy_per_layer = np.mean(np.sum(np.abs(cat_depths), axis=2), axis=0)  # (n_layers,)

            silent_end = int(self.n_layers * 0.50)
            enrich_end = int(self.n_layers * 0.85)
            suppress_end = int(self.n_layers * 0.93)

            silent_e = np.mean(energy_per_layer[:silent_end])
            enrich_e = np.mean(energy_per_layer[silent_end:enrich_end])
            suppress_e = np.mean(energy_per_layer[enrich_end:suppress_end])
            commit_e = np.mean(energy_per_layer[suppress_end:])

            log(f"  {cat:>14s} {silent_e:>8.3f} {enrich_e:>8.3f} {suppress_e:>8.3f} {commit_e:>8.3f}")

        # ── Cluster analysis ──
        log(f"\n  CLUSTER ANALYSIS (k-means on signatures):")
        from sklearn.cluster import KMeans

        # Try k=3,4,5 clusters
        for k in [3, 4, 5]:
            km = KMeans(n_clusters=k, random_state=42, n_init=10)
            labels = km.fit_predict(signatures)

            # What categories end up in each cluster?
            log(f"\n    k={k}:")
            for ci in range(k):
                members = [probe_categories[i] for i in range(len(labels)) if labels[i] == ci]
                from collections import Counter
                counts = Counter(members)
                total = len(members)
                composition = ", ".join(f"{cat}({n})" for cat, n in counts.most_common(5))
                # Cluster centroid's top opcodes
                centroid = km.cluster_centers_[ci]
                top_ops = sorted(zip(ALL_OP_NAMES, centroid), key=lambda x: x[1], reverse=True)[:3]
                top_str = " ".join(f"{op}:{v:.3f}" for op, v in top_ops)
                log(f"      C{ci}: [{top_str}]  members({total}): {composition}")

        # ── Save results ──
        output = {
            "model": self.model_name,
            "n_layers": self.n_layers,
            "n_probes": len(probes),
            "categories": categories,
            "category_signatures": {
                cat: {op: float(v) for op, v in zip(ALL_OP_NAMES, sig)}
                for cat, sig in category_signatures.items()
            },
            "cross_category_cos": {
                sorted_cats[i]: {sorted_cats[j]: float(cos_matrix[i,j]) for j in range(len(sorted_cats))}
                for i in range(len(sorted_cats))
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }
        with open(self.results_dir / "function_map.json", "w") as f:
            json.dump(output, f, indent=2)
        log(f"\n  Saved to {self.results_dir / 'function_map.json'}")

        elapsed = time.time() - t0
        log(f"\n  ✅ Complete in {elapsed:.1f}s")

        del self.model
        gc.collect()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Map the program library")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()
    FunctionMapper(model_name=args.model, device=args.device).run()


if __name__ == "__main__":
    main()
