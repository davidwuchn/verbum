"""Function Discovery — Unsupervised discovery of functional directions in FFN space.

Session 172. Instead of projecting onto 12 predefined combinator directions,
capture raw FFN activations and let PCA reveal the actual functional basis.
The KIBC combinators should appear as some PCs. Additional PCs should reveal
task-level differentiation that the combinator basis misses.

Approach:
  1. Capture raw FFN activations (gate, up, moiré, down_proj output) at
     multiple depth zones for diverse task probes
  2. PCA on the raw d_ff-dimensional activations
  3. Cluster in PC space — what categories separate?
  4. Label PCs by task alignment
  5. Project combinator fingerprints onto discovered PCs — which PCs are KIBC?

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/function_discovery.py --model Qwen/Qwen3-0.6B
    uv run python scripts/experiments/function_discovery.py --model Qwen/Qwen3-14B

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
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "function-discovery"
HOLOGRAM_READER_DIR = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

COMBINATOR_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
BETA_NAMES = ["beta_K", "beta_I", "beta_apply", "beta_compose"]
ALL_OP_NAMES = COMBINATOR_NAMES + BETA_NAMES


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Probes — same as function_mapper but with IDs
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
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
            "2 + 3 =",
            "15 × 7 =",
            "100 - 37 =",
            "144 / 12 =",
            "2^10 =",
            "sqrt(144) =",
            "The sum of 8 and 13 is",
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
            "TL;DR: The Industrial Revolution was a period of major industrialization and innovation that took place during the late 1700s and early 1800s. Summary:",
            "In one sentence: Machine learning is a subset of artificial intelligence that enables systems to learn and improve from experience without being explicitly programmed.",
            "Briefly: The water cycle involves evaporation, condensation, and precipitation. In short,",
            "Key takeaway: Neural networks consist of layers of interconnected nodes that process information. The main point is",
            "Summarize: DNA carries genetic instructions for development, functioning, growth, and reproduction of all known organisms.",
            "The gist: Photosynthesis converts light energy into chemical energy stored in glucose. Essentially,",
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
            "K a b =",
            "B f g x =",
            "C f x y =",
            "S K K x =",
            "W f x =",
            "(λx. f x) a =",
            "(λx. λy. x) a b =",
            "Y f =",
        ],
    }

    for cat, prompts in cats.items():
        for p in prompts:
            probes.append({"id": idx, "category": cat, "prompt": p})
            idx += 1

    return probes


# ══════════════════════════════════════════════════════════════════════
# Discovery Engine
# ══════════════════════════════════════════════════════════════════════

class FunctionDiscovery:
    def __init__(self, model_name: str = "Qwen/Qwen3-0.6B", device: str = "auto"):
        self.model_name = model_name
        self.device = device
        self.model = None
        self.tokenizer = None
        self.layers = None
        self.n_layers = 0
        self.d_model = 0
        self.d_ff = 0
        self.fingerprints = {}
        self.results_dir = RESULTS_BASE / model_name.replace("/", "_")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        log(f"  Loading {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True)
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

        cfg = self.model.config
        self.n_layers = cfg.num_hidden_layers
        self.d_model = cfg.hidden_size
        self.d_ff = getattr(cfg, "intermediate_size", self.d_model * 4)

        for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
            obj = self.model
            try:
                for part in attr_path.split("."):
                    obj = getattr(obj, part)
                self.layers = list(obj)
                break
            except AttributeError:
                continue

        log(f"  Loaded: {self.n_layers} layers, d={self.d_model}, d_ff={self.d_ff}")

        # Load combinator fingerprints for comparison
        slug = self.model_name.replace("/", "_")
        fp_path = HOLOGRAM_READER_DIR / slug / f"fingerprints_{slug}.npz"
        if fp_path.exists():
            data = np.load(fp_path)
            self.fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
            log(f"  Loaded {len(self.fingerprints)} combinator fingerprints for comparison")

    def _capture_all(self, text: str, target_layers: list[int]) -> dict:
        """Capture gate, up, moiré, and down_proj output at target layers."""
        ids = self.tokenizer.encode(text, return_tensors="pt")
        device = next(self.model.parameters()).device
        ids = ids.to(device)

        gate_caps = {}
        up_caps = {}
        down_caps = {}
        hooks = []

        for li in target_layers:
            layer = self.layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            if hasattr(mlp, "gate_proj"):
                def make_gate(idx):
                    def hook(m, inp, out):
                        gate_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.gate_proj.register_forward_hook(make_gate(li)))

                def make_up(idx):
                    def hook(m, inp, out):
                        up_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.up_proj.register_forward_hook(make_up(li)))

                def make_down(idx):
                    def hook(m, inp, out):
                        down_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.down_proj.register_forward_hook(make_down(li)))

        with torch.no_grad():
            _ = self.model(input_ids=ids)

        for h in hooks:
            h.remove()

        # Compute moiré from gate and up
        moire_caps = {}
        for li in target_layers:
            if li in gate_caps and li in up_caps:
                g = gate_caps[li]
                u = up_caps[li]
                sig = 1.0 / (1.0 + np.exp(-np.clip(g, -20, 20)))
                moire_caps[li] = (g * sig) * u

        return {
            "gate": gate_caps, "up": up_caps,
            "moire": moire_caps, "down": down_caps,
        }

    def run(self):
        t0 = time.time()
        self._load()
        probes = build_probes()
        categories = sorted(set(p["category"] for p in probes))
        log(f"  {len(probes)} probes, {len(categories)} categories")

        # Sample layers from each zone
        silent_end = int(self.n_layers * 0.50)
        enrich_end = int(self.n_layers * 0.85)
        suppress_end = int(self.n_layers * 0.93)

        # Pick representative layers from each zone
        zone_layers = {
            "SILENT_early": max(0, silent_end // 4),
            "SILENT_late": max(0, silent_end - 1),
            "ENRICH_early": silent_end,
            "ENRICH_mid": (silent_end + enrich_end) // 2,
            "ENRICH_late": enrich_end - 1,
            "SUPPRESS": (enrich_end + suppress_end) // 2,
            "COMMIT": self.n_layers - 1,
        }

        target_layers = sorted(set(zone_layers.values()))
        log(f"  Target layers: {target_layers}")
        log(f"  Zone mapping: {zone_layers}")

        # ══════════════════════════════════════════════════════════════
        # Phase 1: Capture raw activations
        # ══════════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  Phase 1: Capturing raw FFN activations")
        log(f"{'═' * 70}")

        # Storage: per (signal_type, layer) → (n_probes, d_ff or d_model)
        all_activations = {}
        probe_cats = []

        for pi, probe in enumerate(probes):
            caps = self._capture_all(probe["prompt"], target_layers)
            probe_cats.append(probe["category"])

            for signal in ["moire", "down"]:
                for li in target_layers:
                    key = (signal, li)
                    if key not in all_activations:
                        all_activations[key] = []
                    if li in caps[signal]:
                        all_activations[key].append(caps[signal][li])
                    else:
                        # Pad with zeros if missing
                        dim = self.d_ff if signal != "down" else self.d_model
                        all_activations[key].append(np.zeros(dim, dtype=np.float32))

            if (pi + 1) % 10 == 0:
                log(f"    {pi + 1}/{len(probes)}")

        probe_cats = np.array(probe_cats)

        # ══════════════════════════════════════════════════════════════
        # Phase 2: PCA on moiré activations per zone
        # ══════════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  Phase 2: PCA on moiré space — what directions exist?")
        log(f"{'═' * 70}")

        zone_pca_results = {}

        for zone_name, li in zone_layers.items():
            key = ("moire", li)
            if key not in all_activations:
                continue

            matrix = np.array(all_activations[key])  # (n_probes, d_ff)
            n_samples, n_features = matrix.shape

            # Normalize
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)
            matrix_unit = matrix / norms

            n_components = min(20, n_samples - 1, n_features)
            pca = PCA(n_components=n_components)
            coords = pca.fit_transform(matrix_unit)  # (n_probes, n_components)

            var_explained = pca.explained_variance_ratio_
            cum_var = np.cumsum(var_explained)

            log(f"\n  [{zone_name}] L{li:02d} — moiré PCA:")
            log(f"    Variance explained: PC0={var_explained[0]:.1%}, "
                f"PC1={var_explained[1]:.1%}, PC2={var_explained[2]:.1%}")
            log(f"    Cumulative: 3PC={cum_var[2]:.1%}, 5PC={cum_var[4]:.1%}, "
                f"10PC={cum_var[min(9,n_components-1)]:.1%}")

            # Per-category centroid in PC space
            log(f"    Category centroids in PC0-PC2:")
            cat_centroids = {}
            for cat in categories:
                mask = probe_cats == cat
                cat_coords = coords[mask]
                centroid = np.mean(cat_coords, axis=0)
                cat_centroids[cat] = centroid
                log(f"      {cat:>14s}: PC0={centroid[0]:+.3f}  PC1={centroid[1]:+.3f}  PC2={centroid[2]:+.3f}")

            # Cross-category distances in PC space
            cat_list = sorted(categories)
            centroid_vecs = np.array([cat_centroids[c][:5] for c in cat_list])
            c_norms = np.linalg.norm(centroid_vecs, axis=1, keepdims=True)
            c_norms = np.clip(c_norms, 1e-10, None)
            c_unit = centroid_vecs / c_norms
            cos_mat = c_unit @ c_unit.T

            # Find most separated pairs
            min_cos = 1.0
            min_pair = ("", "")
            max_cos = -1.0
            max_pair = ("", "")
            for i in range(len(cat_list)):
                for j in range(i + 1, len(cat_list)):
                    c = cos_mat[i, j]
                    if c < min_cos:
                        min_cos = c
                        min_pair = (cat_list[i], cat_list[j])
                    if c > max_cos:
                        max_cos = c
                        max_pair = (cat_list[i], cat_list[j])

            log(f"    Most separated:  {min_pair[0]} ↔ {min_pair[1]} (cos={min_cos:.3f})")
            log(f"    Most similar:    {max_pair[0]} ↔ {max_pair[1]} (cos={max_cos:.3f})")

            # K-means in PC space
            km = KMeans(n_clusters=5, random_state=42, n_init=10)
            labels = km.fit_predict(coords[:, :10])  # Use top 10 PCs

            log(f"    K-means (k=5) in 10-PC space:")
            from collections import Counter
            for ci in range(5):
                members = probe_cats[labels == ci]
                counts = Counter(members)
                composition = ", ".join(f"{c}({n})" for c, n in counts.most_common(4))
                log(f"      C{ci} ({len(members):>2d}): {composition}")

            zone_pca_results[zone_name] = {
                "layer": li,
                "var_explained": var_explained[:10].tolist(),
                "cum_var": cum_var[:10].tolist(),
                "centroids": {c: centroid[:5].tolist() for c, centroid in cat_centroids.items()},
                "min_separation": {"pair": list(min_pair), "cos": float(min_cos)},
                "max_similarity": {"pair": list(max_pair), "cos": float(max_cos)},
                "pca_components": pca.components_[:5].tolist() if pca.components_.shape[0] >= 5 else pca.components_.tolist(),
            }

        # ══════════════════════════════════════════════════════════════
        # Phase 3: Compare PCA directions to combinator fingerprints
        # ══════════════════════════════════════════════════════════════
        if self.fingerprints:
            log(f"\n{'═' * 70}")
            log(f"  Phase 3: Are the PCA directions related to KIBC?")
            log(f"{'═' * 70}")

            for zone_name, li in zone_layers.items():
                key = ("down", li)
                if key not in all_activations:
                    continue

                # PCA on down_proj output (d_model space — same space as fingerprints)
                matrix = np.array(all_activations[key])
                norms = np.linalg.norm(matrix, axis=1, keepdims=True)
                norms = np.clip(norms, 1e-10, None)
                matrix_unit = matrix / norms

                n_components = min(20, matrix_unit.shape[0] - 1)
                pca = PCA(n_components=n_components)
                pca.fit(matrix_unit)

                # Project combinator fingerprints onto PCA directions
                log(f"\n  [{zone_name}] L{li:02d} — combinator alignment with PCA directions:")
                log(f"    {'Op':>12s}  {'PC0':>7s}  {'PC1':>7s}  {'PC2':>7s}  {'PC3':>7s}  {'PC4':>7s}  {'|total|':>7s}")

                for op in ALL_OP_NAMES:
                    fp = self.fingerprints[op][li]
                    fp_norm = np.linalg.norm(fp)
                    if fp_norm < 1e-10:
                        continue
                    fp_unit = fp / fp_norm

                    # Project onto PCA components
                    projections = [float(np.dot(fp_unit, pca.components_[i]))
                                   for i in range(min(5, n_components))]
                    total = np.sqrt(sum(p**2 for p in projections))

                    log(f"    {op:>12s}  {projections[0]:>+7.3f}  {projections[1]:>+7.3f}  "
                        f"{projections[2]:>+7.3f}  {projections[3]:>+7.3f}  {projections[4]:>+7.3f}  "
                        f"{total:>7.3f}")

        # ══════════════════════════════════════════════════════════════
        # Phase 4: Full cross-category separation analysis
        # ══════════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  Phase 4: Category separation across zones")
        log(f"{'═' * 70}")

        # For each zone, compute the mean within-category vs cross-category distance
        # in the full d_ff moiré space (not projected)
        for zone_name, li in zone_layers.items():
            key = ("moire", li)
            if key not in all_activations:
                continue

            matrix = np.array(all_activations[key])
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)
            matrix_unit = matrix / norms

            cos_mat = matrix_unit @ matrix_unit.T

            within = []
            cross = []
            for i in range(len(probes)):
                for j in range(i + 1, len(probes)):
                    c = float(cos_mat[i, j])
                    if probe_cats[i] == probe_cats[j]:
                        within.append(c)
                    else:
                        cross.append(c)

            within_mean = np.mean(within)
            cross_mean = np.mean(cross)
            separation = within_mean / max(cross_mean, 1e-10)

            log(f"  [{zone_name:>14s}] L{li:02d}: within={within_mean:.4f}  "
                f"cross={cross_mean:.4f}  ratio={separation:.3f}")

        # ══════════════════════════════════════════════════════════════
        # Save results
        # ══════════════════════════════════════════════════════════════
        output = {
            "model": self.model_name,
            "n_layers": self.n_layers,
            "d_model": self.d_model,
            "d_ff": self.d_ff,
            "n_probes": len(probes),
            "categories": categories,
            "zone_layers": zone_layers,
            "zone_pca": zone_pca_results,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        out_path = self.results_dir / "discovery.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        log(f"\n  Saved to {out_path}")

        elapsed = time.time() - t0
        log(f"\n  ✅ Complete in {elapsed:.1f}s")

        del self.model
        gc.collect()


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Unsupervised function discovery")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()
    FunctionDiscovery(model_name=args.model, device=args.device).run()


if __name__ == "__main__":
    main()
