"""Dimensional Analysis — How much of FFN space does the KIBC basis cover?

Session 178. The trace loss projects onto 11 combinator dimensions in a
1024-dim (0.6B) or 5120-dim (27B) space. How much of the model's actual
functional space does this capture? What lives in the other 99%?

Measurements:
  1. Effective dimensionality per layer (PCA on FFN outputs, diverse inputs)
  2. KIBC coverage: fraction of variance captured by the 11-dim crystal basis
  3. Number of PCs needed for 90%/95%/99% variance
  4. Task separation in full PCA vs KIBC-only subspace
  5. What the non-KIBC PCs look like (task alignment, zone signatures)

Run:
    cd ~/src/verbum
    uv run python scripts/experiments/dimensional_analysis.py --model Qwen/Qwen3-0.6B

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path
from collections import Counter

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer
from sklearn.decomposition import PCA

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "dimensional-analysis"
HOLOGRAM_READER_DIR = Path(__file__).parent.parent.parent / "results" / "hologram-reader"

ALL_OP_NAMES = ["K", "I", "B", "C", "D", "Y", "W", "WHNF",
                "beta_K", "beta_I", "beta_apply", "beta_compose"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Diverse probes — broad coverage of task space
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Diverse task probes covering 9 categories."""
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
# Analysis Engine
# ══════════════════════════════════════════════════════════════════════

class DimensionalAnalysis:
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
        slug = model_name.replace("/", "_")
        self.results_dir = RESULTS_BASE / slug
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def _load(self):
        log(f"Loading {self.model_name}...")
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

        log(f"  {self.n_layers} layers, d={self.d_model}, d_ff={self.d_ff}")

        # Load combinator fingerprints
        slug = self.model_name.replace("/", "_")
        fp_path = HOLOGRAM_READER_DIR / slug / f"fingerprints_{slug}.npz"
        if fp_path.exists():
            data = np.load(fp_path)
            self.fingerprints = {op: data[op] for op in ALL_OP_NAMES if op in data}
            log(f"  Loaded {len(self.fingerprints)} combinator fingerprints")
        else:
            log(f"  WARNING: No fingerprints at {fp_path}")

    def _capture_ffn_outputs(self, text: str, target_layers: list[int]) -> dict[int, np.ndarray]:
        """Capture down_proj output (d_model) at target layers for last token."""
        ids = self.tokenizer.encode(text, return_tensors="pt")
        device = next(self.model.parameters()).device
        ids = ids.to(device)

        captures = {}
        hooks = []

        for li in target_layers:
            layer = self.layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            if hasattr(mlp, "down_proj"):
                def make_hook(idx):
                    def hook(m, inp, out):
                        captures[idx] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(mlp.down_proj.register_forward_hook(make_hook(li)))

        with torch.no_grad():
            _ = self.model(input_ids=ids)

        for h in hooks:
            h.remove()

        return captures

    def _effective_dim(self, explained_variance: np.ndarray, threshold: float = 0.90) -> int:
        """Number of PCs needed to capture threshold fraction of variance."""
        cum = np.cumsum(explained_variance)
        idx = np.searchsorted(cum, threshold)
        return min(idx + 1, len(explained_variance))

    def _participation_ratio(self, explained_variance: np.ndarray) -> float:
        """Participation ratio: (Σλ)² / Σλ². Effective dimensionality metric."""
        s = explained_variance
        return float((s.sum()) ** 2 / (s ** 2).sum()) if (s ** 2).sum() > 0 else 0.0

    def run(self):
        t0 = time.time()
        self._load()
        probes = build_probes()
        categories = sorted(set(p["category"] for p in probes))
        n_probes = len(probes)
        log(f"  {n_probes} probes, {len(categories)} categories")

        # Capture ALL layers
        target_layers = list(range(self.n_layers))
        log(f"  Capturing all {self.n_layers} layers...")

        # Storage: per layer → (n_probes, d_model)
        all_ffn = {li: [] for li in target_layers}
        probe_cats = []

        for pi, probe in enumerate(probes):
            caps = self._capture_ffn_outputs(probe["prompt"], target_layers)
            probe_cats.append(probe["category"])

            for li in target_layers:
                if li in caps:
                    all_ffn[li].append(caps[li])
                else:
                    all_ffn[li].append(np.zeros(self.d_model, dtype=np.float32))

            if (pi + 1) % 10 == 0:
                log(f"    {pi + 1}/{n_probes}")

        probe_cats = np.array(probe_cats)

        # ══════════════════════════════════════════════════════════
        # Measurement 1: PCA per layer — effective dimensionality
        # ══════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  M1: Effective dimensionality per layer (PCA on FFN outputs)")
        log(f"{'═' * 70}")

        n_components = min(n_probes - 1, self.d_model, 64)
        per_layer_results = {}

        for li in target_layers:
            matrix = np.array(all_ffn[li])  # (n_probes, d_model)
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)
            matrix_unit = matrix / norms

            pca = PCA(n_components=n_components)
            coords = pca.fit_transform(matrix_unit)
            ev = pca.explained_variance_ratio_

            dim90 = self._effective_dim(ev, 0.90)
            dim95 = self._effective_dim(ev, 0.95)
            dim99 = self._effective_dim(ev, 0.99)
            pr = self._participation_ratio(ev)

            # ══════════════════════════════════════════════════════
            # Measurement 2: KIBC coverage at this layer
            # ══════════════════════════════════════════════════════
            kibc_coverage = 0.0
            kibc_per_op = {}
            if self.fingerprints:
                # Build KIBC basis matrix for this layer
                fp_vecs = []
                fp_names = []
                for op in ALL_OP_NAMES:
                    if op in self.fingerprints and li < self.fingerprints[op].shape[0]:
                        v = self.fingerprints[op][li]
                        n = np.linalg.norm(v)
                        if n > 1e-10:
                            fp_vecs.append(v / n)
                            fp_names.append(op)

                if fp_vecs:
                    fp_matrix = np.array(fp_vecs)  # (n_ops, d_model)

                    # Project each PCA component onto the KIBC subspace
                    # and measure how much of PCA variance is captured
                    pca_components = pca.components_  # (n_components, d_model)

                    # For each PC: what fraction of it lies in the KIBC subspace?
                    # |proj(pc, KIBC_span)|² / |pc|²
                    # Using orthogonalized KIBC basis
                    U, S, Vt = np.linalg.svd(fp_matrix.T, full_matrices=False)
                    # U: (d_model, n_ops) — orthonormal basis of KIBC span
                    kibc_rank = np.sum(S > 1e-6)
                    kibc_basis = U[:, :kibc_rank]  # (d_model, kibc_rank)

                    total_var_in_kibc = 0.0
                    for pc_i in range(len(ev)):
                        pc_vec = pca_components[pc_i]
                        proj = kibc_basis.T @ pc_vec  # (kibc_rank,)
                        frac_in_kibc = float(np.dot(proj, proj))  # |proj|² since pc is unit
                        total_var_in_kibc += ev[pc_i] * frac_in_kibc

                    kibc_coverage = total_var_in_kibc

                    # Per-op coverage: how much does each individual op contribute
                    for op, fp_vec in zip(fp_names, fp_vecs):
                        op_var = 0.0
                        for pc_i in range(len(ev)):
                            proj = float(np.dot(pca_components[pc_i], fp_vec))
                            op_var += ev[pc_i] * proj ** 2
                        kibc_per_op[op] = float(op_var)

            # ══════════════════════════════════════════════════════
            # Measurement 4: Task separation in full PCA vs KIBC
            # ══════════════════════════════════════════════════════
            # Full PCA separation (using top-20 PCs)
            n_sep = min(20, n_components)
            full_pca_centroids = {}
            for cat in categories:
                mask = probe_cats == cat
                full_pca_centroids[cat] = np.mean(coords[mask, :n_sep], axis=0)

            # Within vs cross category distance in full PCA space
            within_dists = []
            cross_dists = []
            for i in range(n_probes):
                for j in range(i + 1, n_probes):
                    d = np.linalg.norm(coords[i, :n_sep] - coords[j, :n_sep])
                    if probe_cats[i] == probe_cats[j]:
                        within_dists.append(d)
                    else:
                        cross_dists.append(d)

            full_separation = float(np.mean(cross_dists) / max(np.mean(within_dists), 1e-10))

            # KIBC-only separation (project onto KIBC subspace)
            kibc_separation = 0.0
            if self.fingerprints and fp_vecs:
                kibc_coords = matrix_unit @ kibc_basis  # (n_probes, kibc_rank)
                within_k = []
                cross_k = []
                for i in range(n_probes):
                    for j in range(i + 1, n_probes):
                        d = np.linalg.norm(kibc_coords[i] - kibc_coords[j])
                        if probe_cats[i] == probe_cats[j]:
                            within_k.append(d)
                        else:
                            cross_k.append(d)
                kibc_separation = float(np.mean(cross_k) / max(np.mean(within_k), 1e-10))

            per_layer_results[li] = {
                "dim90": dim90,
                "dim95": dim95,
                "dim99": dim99,
                "participation_ratio": round(pr, 2),
                "var_explained_top10": [round(float(v), 5) for v in ev[:10]],
                "cumvar_at_10": round(float(np.cumsum(ev)[:10][-1]), 4),
                "cumvar_at_20": round(float(np.cumsum(ev)[:min(20, len(ev))][-1]), 4),
                "kibc_coverage": round(kibc_coverage, 5),
                "kibc_rank": kibc_rank if self.fingerprints else 0,
                "kibc_per_op": {k: round(v, 6) for k, v in kibc_per_op.items()},
                "full_separation": round(full_separation, 3),
                "kibc_separation": round(kibc_separation, 3),
            }

            # Print compact summary
            kibc_pct = f"{kibc_coverage:.1%}" if self.fingerprints else "N/A"
            log(f"  L{li:02d}: dim90={dim90:>3d}  dim95={dim95:>3d}  PR={pr:>5.1f}  "
                f"KIBC={kibc_pct:>6s}  full_sep={full_separation:.2f}  kibc_sep={kibc_separation:.2f}")

        # ══════════════════════════════════════════════════════════
        # Measurement 5: What are the non-KIBC PCs?
        # ══════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  M5: Non-KIBC PC characterization (sampled layers)")
        log(f"{'═' * 70}")

        # Pick representative layers
        sample_layers = [0, self.n_layers // 4, self.n_layers // 2,
                         3 * self.n_layers // 4, self.n_layers - 1]
        sample_layers = [li for li in sample_layers if li < self.n_layers]

        non_kibc_analysis = {}

        for li in sample_layers:
            matrix = np.array(all_ffn[li])
            norms = np.linalg.norm(matrix, axis=1, keepdims=True)
            norms = np.clip(norms, 1e-10, None)
            matrix_unit = matrix / norms

            pca = PCA(n_components=n_components)
            coords = pca.fit_transform(matrix_unit)
            ev = pca.explained_variance_ratio_
            components = pca.components_

            if not self.fingerprints:
                continue

            # Build orthogonalized KIBC basis
            fp_vecs = []
            for op in ALL_OP_NAMES:
                if op in self.fingerprints and li < self.fingerprints[op].shape[0]:
                    v = self.fingerprints[op][li]
                    n = np.linalg.norm(v)
                    if n > 1e-10:
                        fp_vecs.append(v / n)
            if not fp_vecs:
                continue
            fp_matrix = np.array(fp_vecs)
            U, S, Vt = np.linalg.svd(fp_matrix.T, full_matrices=False)
            kibc_rank = np.sum(S > 1e-6)
            kibc_basis = U[:, :kibc_rank]

            log(f"\n  L{li:02d} — Top 20 PCs: KIBC overlap + task alignment")
            log(f"    {'PC':>3s}  {'var%':>6s}  {'cum%':>6s}  {'KIBC':>6s}  {'best_task':>14s}  {'contrast':>10s}")

            pc_info = []
            for pc_i in range(min(20, len(ev))):
                pc_vec = components[pc_i]
                proj = kibc_basis.T @ pc_vec
                kibc_frac = float(np.dot(proj, proj))

                # Task alignment: which category has highest absolute centroid on this PC
                best_cat = ""
                best_val = 0.0
                for cat in categories:
                    mask = probe_cats == cat
                    cat_mean = float(np.mean(coords[mask, pc_i]))
                    if abs(cat_mean) > abs(best_val):
                        best_val = cat_mean
                        best_cat = cat

                # Contrast: max inter-category difference on this PC
                cat_means = {cat: float(np.mean(coords[probe_cats == cat, pc_i]))
                             for cat in categories}
                max_diff = max(cat_means.values()) - min(cat_means.values())

                cum = float(np.cumsum(ev)[:pc_i + 1][-1])
                label = "KIBC" if kibc_frac > 0.5 else "task" if max_diff > 0.3 else "other"

                log(f"    {pc_i:>3d}  {ev[pc_i]:>5.1%}  {cum:>5.1%}  {kibc_frac:>5.1%}  "
                    f"{best_cat:>14s}  {max_diff:>10.3f}  [{label}]")

                pc_info.append({
                    "pc": pc_i,
                    "var_pct": round(float(ev[pc_i]), 5),
                    "kibc_frac": round(kibc_frac, 4),
                    "best_task": best_cat,
                    "best_val": round(best_val, 4),
                    "contrast": round(max_diff, 4),
                    "label": label,
                })

            non_kibc_analysis[li] = pc_info

        # ══════════════════════════════════════════════════════════
        # Summary
        # ══════════════════════════════════════════════════════════
        log(f"\n{'═' * 70}")
        log(f"  SUMMARY")
        log(f"{'═' * 70}")

        all_coverage = [per_layer_results[li]["kibc_coverage"]
                        for li in target_layers if per_layer_results[li]["kibc_coverage"] > 0]
        all_dim90 = [per_layer_results[li]["dim90"] for li in target_layers]
        all_pr = [per_layer_results[li]["participation_ratio"] for li in target_layers]

        if all_coverage:
            log(f"  KIBC coverage: min={min(all_coverage):.1%} max={max(all_coverage):.1%} "
                f"mean={np.mean(all_coverage):.1%}")
        log(f"  dim90: min={min(all_dim90)} max={max(all_dim90)} mean={np.mean(all_dim90):.1f}")
        log(f"  Participation ratio: min={min(all_pr):.1f} max={max(all_pr):.1f} "
            f"mean={np.mean(all_pr):.1f}")

        # What fraction of variance is NOT covered by KIBC?
        if all_coverage:
            mean_gap = 1.0 - np.mean(all_coverage)
            log(f"\n  ⚠ KIBC basis captures {np.mean(all_coverage):.1%} of FFN output variance on average")
            log(f"  ⚠ {mean_gap:.1%} of the functional space is INVISIBLE to trace loss")

        # How many PCs would you need to match 90% of what PCA gives?
        log(f"\n  Dimension counts for 90% variance coverage:")
        for li in sample_layers:
            r = per_layer_results[li]
            log(f"    L{li:02d}: {r['dim90']} PCs for 90%, {r['dim95']} PCs for 95%")

        # ══════════════════════════════════════════════════════════
        # Save
        # ══════════════════════════════════════════════════════════
        output = {
            "model": self.model_name,
            "n_layers": self.n_layers,
            "d_model": self.d_model,
            "d_ff": self.d_ff,
            "n_probes": n_probes,
            "categories": categories,
            "kibc_ops": ALL_OP_NAMES,
            "per_layer": per_layer_results,
            "non_kibc_pcs": {str(k): v for k, v in non_kibc_analysis.items()},
            "summary": {
                "kibc_coverage_mean": round(float(np.mean(all_coverage)), 5) if all_coverage else None,
                "kibc_coverage_min": round(float(min(all_coverage)), 5) if all_coverage else None,
                "kibc_coverage_max": round(float(max(all_coverage)), 5) if all_coverage else None,
                "dim90_mean": round(float(np.mean(all_dim90)), 1),
                "dim90_min": int(min(all_dim90)),
                "dim90_max": int(max(all_dim90)),
                "participation_ratio_mean": round(float(np.mean(all_pr)), 1),
            },
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        }

        # Convert numpy types for JSON serialization
        def to_native(obj):
            if isinstance(obj, (np.integer,)):
                return int(obj)
            elif isinstance(obj, (np.floating,)):
                return float(obj)
            elif isinstance(obj, np.ndarray):
                return obj.tolist()
            elif isinstance(obj, dict):
                return {k: to_native(v) for k, v in obj.items()}
            elif isinstance(obj, (list, tuple)):
                return [to_native(v) for v in obj]
            return obj

        output = to_native(output)
        out_path = self.results_dir / "analysis.json"
        with open(out_path, "w") as f:
            json.dump(output, f, indent=2)
        log(f"\n  Saved to {out_path}")

        elapsed = time.time() - t0
        log(f"  ✅ Complete in {elapsed:.1f}s")

        del self.model
        gc.collect()

        return output


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Dimensional analysis of FFN space")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="auto")
    args = parser.parse_args()
    DimensionalAnalysis(model_name=args.model, device=args.device).run()


if __name__ == "__main__":
    main()
