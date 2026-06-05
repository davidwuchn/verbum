#!/usr/bin/env python3
"""Test: can FFN computation be replaced by ternary inference patterns?

The hypothesis: the FFN compiles V vectors via continuous weights, but
the downstream computation (softmax attention) only needs the DIRECTION
of the V vector, not its precise magnitude. If we can classify what
COMBINATOR the FFN is executing (KIBC mode) and look up a precomputed
ternary pattern for that mode, we can replace the continuous FFN with
a ternary lookup.

Method:
  1. Run diverse probes through the model, capture FFN outputs per layer
  2. Classify each output by combinator mode (project onto fingerprints)
  3. For each mode, compute: ternary_pattern = sign(centroid)
  4. Replace one FFN layer: classify → lookup ternary pattern × gamma
  5. Measure PPL with original vs replaced FFN

Three replacement strategies tested:
  A. 9-mode KIBC lookup (coarsest — 9 ternary patterns)
  B. K-means clustering (data-driven — K ternary patterns)
  C. PCA reconstruction (finest — top-N sign-quantized components)

Usage:
  uv run python scripts/experiments/ternary_inference_pattern.py --model Qwen/Qwen3-0.6B --device mps
  uv run python scripts/experiments/ternary_inference_pattern.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes, by_combinator


# ══════════════════════════════════════════════════════════════════════
# Eval texts for PPL measurement
# ══════════════════════════════════════════════════════════════════════

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy. Einstein published this theory in 1915, fundamentally changing our understanding of the universe.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center and add the eggs, milk, and melted butter. Stir until just combined, being careful not to overmix the batter.",
    "The committee voted unanimously to approve the new environmental regulations, which require all manufacturing plants to reduce carbon emissions by thirty percent within the next five years.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves. The trees rose like cathedral pillars around her, their canopy filtering the light into green and gold.",
    "The function takes two arguments and returns their composition. If the first argument is a predicate, the result filters the second argument according to that predicate.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared in the fossil record over a relatively short period of geological time.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated white cell count and C-reactive protein levels consistent with bacterial pneumonia.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides, then divide by the coefficient to obtain the solution.",
]


# ══════════════════════════════════════════════════════════════════════
# Architecture helpers
# ══════════════════════════════════════════════════════════════════════

def get_layers(model):
    """Get the transformer layers regardless of architecture."""
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        return model.transformer.h
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_mlp_module(layer):
    """Get the MLP module itself (not a sub-projection)."""
    mlp = getattr(layer, 'mlp', None)
    if mlp is None:
        raise RuntimeError("No MLP found")
    return mlp


def get_zone_b_layers(n_layers: int) -> list[int]:
    """Middle 30-70% of layers."""
    start = int(n_layers * 0.3)
    end = int(n_layers * 0.7)
    indices = np.linspace(start, end, min(4, end - start + 1), dtype=int)
    return sorted(set(indices.tolist()))


# ══════════════════════════════════════════════════════════════════════
# Phase 1: Collect FFN fingerprints per combinator
# ══════════════════════════════════════════════════════════════════════

def collect_ffn_fingerprints(model, tokenizer, target_layer: int, device: str,
                              n_per_comb: int = 30) -> dict:
    """Run crystal probes, capture FFN output, classify by combinator."""

    layers = get_layers(model)
    hook_module = get_mlp_module(layers[target_layer])

    captured = {}

    def hook_fn(module, input, output):
        # MLP module output is (batch, seq, d_model)
        captured['output'] = output.detach().float()

    handle = hook_module.register_forward_hook(hook_fn)

    combinators = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]
    comb_outputs = {c: [] for c in combinators}

    for comb in combinators:
        probes = by_combinator(comb)
        prompts = [p.prompt for p in probes[:n_per_comb]]

        for prompt in prompts:
            captured.clear()
            inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
            inputs = {k: v.to(device) for k, v in inputs.items()}

            with torch.no_grad():
                model(**inputs)

            if 'output' in captured:
                # Mean pool across sequence
                out = captured['output'].mean(dim=1).squeeze(0).cpu().numpy()
                comb_outputs[comb].append(out)

    handle.remove()

    # Compute per-combinator centroids and ternary patterns
    result = {}
    for comb in combinators:
        if not comb_outputs[comb]:
            continue
        outputs = np.stack(comb_outputs[comb])  # (n_probes, d_model)
        centroid = outputs.mean(axis=0)  # (d_model,)
        ternary = np.sign(centroid)  # {-1, 0, +1}
        gamma = np.abs(centroid).mean()  # scalar scale

        # Per-position gamma (more expressive)
        pos_gamma = np.abs(centroid)

        result[comb] = {
            'centroid': centroid,
            'ternary': ternary,
            'gamma': gamma,
            'pos_gamma': pos_gamma,
            'n_probes': len(outputs),
            'variance': outputs.var(axis=0).mean(),  # within-mode variance
        }

    return result


# ══════════════════════════════════════════════════════════════════════
# Phase 2: Build replacement FFN modules
# ══════════════════════════════════════════════════════════════════════

class TernaryInferenceFFN(torch.nn.Module):
    """Replaces an FFN layer with: classify → lookup ternary pattern × gamma.

    Three modes:
      'centroid':  classify → return centroid (continuous, upper bound)
      'ternary':   classify → return ternary_pattern × pos_gamma
      'ternary_scalar': classify → return ternary_pattern × scalar_gamma
    """

    def __init__(self, fingerprints: dict, mode: str = 'ternary'):
        super().__init__()
        self.mode = mode

        combs = sorted(fingerprints.keys())
        self.combs = combs

        # Stack centroids for fast classification
        centroids = np.stack([fingerprints[c]['centroid'] for c in combs])
        self.register_buffer('centroids', torch.tensor(centroids, dtype=torch.float32))

        # Stack ternary patterns
        ternaries = np.stack([fingerprints[c]['ternary'] for c in combs])
        self.register_buffer('ternaries', torch.tensor(ternaries, dtype=torch.float32))

        # Stack gammas (per-position)
        pos_gammas = np.stack([fingerprints[c]['pos_gamma'] for c in combs])
        self.register_buffer('pos_gammas', torch.tensor(pos_gammas, dtype=torch.float32))

        # Scalar gammas
        scalar_gammas = np.array([fingerprints[c]['gamma'] for c in combs])
        self.register_buffer('scalar_gammas', torch.tensor(scalar_gammas, dtype=torch.float32))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """x: (batch, seq, d_model) → (batch, seq, d_model)"""
        # Classify: project onto centroids, find best match
        # x_flat: (batch*seq, d_model)
        orig_shape = x.shape
        x_flat = x.reshape(-1, x.shape[-1]).float()

        # Cosine similarity to each centroid
        x_norm = F.normalize(x_flat, dim=-1)
        c_norm = F.normalize(self.centroids, dim=-1)
        similarities = x_flat @ c_norm.T  # (batch*seq, n_combs)
        best_comb = similarities.argmax(dim=-1)  # (batch*seq,)

        if self.mode == 'centroid':
            # Use continuous centroids (upper bound on quality)
            output = self.centroids[best_comb]  # (batch*seq, d_model)
        elif self.mode == 'ternary':
            # Use ternary patterns × per-position gamma
            patterns = self.ternaries[best_comb]  # (batch*seq, d_model)
            gammas = self.pos_gammas[best_comb]    # (batch*seq, d_model)
            output = patterns * gammas
        elif self.mode == 'ternary_scalar':
            # Use ternary patterns × scalar gamma
            patterns = self.ternaries[best_comb]
            gammas = self.scalar_gammas[best_comb].unsqueeze(-1)
            output = patterns * gammas
        else:
            raise ValueError(f"Unknown mode: {self.mode}")

        return output.to(x.dtype).reshape(orig_shape)


# ══════════════════════════════════════════════════════════════════════
# Phase 3: PPL measurement
# ══════════════════════════════════════════════════════════════════════

def measure_ppl(model, tokenizer, texts: list[str], device: str) -> float:
    """Measure perplexity on eval texts."""
    total_loss = 0.0
    total_tokens = 0

    model.eval()
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()

        with torch.no_grad():
            outputs = model(**inputs, labels=labels)
            loss = outputs.loss
            n_tokens = labels.numel()
            total_loss += loss.item() * n_tokens
            total_tokens += n_tokens

    avg_loss = total_loss / total_tokens
    ppl = np.exp(avg_loss)
    return ppl


def replace_ffn_with_hook(model, target_layer: int, replacement: TernaryInferenceFFN, device: str):
    """Install a hook that replaces MLP output with the ternary inference pattern."""

    layers = get_layers(model)
    hook_module = get_mlp_module(layers[target_layer])
    replacement = replacement.to(device)

    # Hook the entire MLP module
    # input[0] is (batch, seq, d_model) — post-layernorm residual
    # output is (batch, seq, d_model) — MLP result (before residual add)
    # We classify the INPUT and replace the OUTPUT with our ternary lookup
    def hook_fn(module, input, output):
        x = input[0] if isinstance(input, tuple) else input
        return replacement(x)

    handle = hook_module.register_forward_hook(hook_fn)
    return handle


# ══════════════════════════════════════════════════════════════════════
# Phase 4: K-means clustering (Strategy B)
# ══════════════════════════════════════════════════════════════════════

def build_kmeans_patterns(model, tokenizer, target_layer: int, device: str,
                          n_clusters: int = 16, n_probes: int = 200) -> dict:
    """Build ternary patterns from K-means clustering of FFN outputs."""
    from sklearn.cluster import MiniBatchKMeans

    layers = get_layers(model)
    hook_module = get_mlp_module(layers[target_layer])

    captured = {}
    def hook_fn(module, input, output):
        # MLP module output is (batch, seq, d_model)
        captured['output'] = output.detach().float()

    handle = hook_module.register_forward_hook(hook_fn)

    # Collect outputs from diverse probes
    all_outputs = []
    probes = crystal_probes()
    prompts = [p.prompt for p in probes[:n_probes]]

    for prompt in prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'output' in captured:
            out = captured['output'].mean(dim=1).squeeze(0).cpu().numpy()
            all_outputs.append(out)

    # Also add eval texts for better coverage
    for text in EVAL_TEXTS:
        captured.clear()
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'output' in captured:
            out = captured['output'].mean(dim=1).squeeze(0).cpu().numpy()
            all_outputs.append(out)

    handle.remove()

    all_outputs = np.stack(all_outputs)
    print(f"    K-means on {len(all_outputs)} samples, {n_clusters} clusters...")

    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=64)
    kmeans.fit(all_outputs)

    # Build fingerprint dict compatible with TernaryInferenceFFN
    result = {}
    for i in range(n_clusters):
        centroid = kmeans.cluster_centers_[i]
        result[f"cluster_{i}"] = {
            'centroid': centroid,
            'ternary': np.sign(centroid),
            'gamma': np.abs(centroid).mean(),
            'pos_gamma': np.abs(centroid),
            'n_probes': int((kmeans.labels_ == i).sum()),
            'variance': 0.0,
        }

    return result


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-0.6B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-per-comb", type=int, default=30)
    p.add_argument("--kmeans-clusters", type=int, default=16)
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  TERNARY INFERENCE PATTERN TEST")
    print(f"  Can FFN computation be replaced by classify → lookup → gamma?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    # Load model
    print(f"  Loading {args.model}...")
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    zone_b = get_zone_b_layers(n_layers)
    print(f"  Layers: {n_layers}, Zone B: {zone_b}")

    # Baseline PPL
    print(f"\n  Measuring baseline PPL...")
    baseline_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    print(f"  Baseline PPL: {baseline_ppl:.2f}")

    # Test each Zone B layer
    results = []
    for target_layer in zone_b:
        print(f"\n{'─'*70}")
        print(f"  TARGET LAYER {target_layer}")
        print(f"{'─'*70}")

        # Phase 1: Collect combinator fingerprints
        print(f"  Collecting combinator fingerprints...")
        fingerprints = collect_ffn_fingerprints(
            model, tokenizer, target_layer, args.device, args.n_per_comb)

        n_combs = len(fingerprints)
        for comb, fp in fingerprints.items():
            nonzero = np.count_nonzero(fp['ternary'])
            total = len(fp['ternary'])
            print(f"    {comb:>5s}: {fp['n_probes']:>3d} probes, "
                  f"γ={fp['gamma']:.4f}, "
                  f"ternary density={nonzero/total:.1%}, "
                  f"within-var={fp['variance']:.6f}")

        # Phase 2: Build K-means patterns
        print(f"\n  Building K-means patterns...")
        kmeans_fp = build_kmeans_patterns(
            model, tokenizer, target_layer, args.device, args.kmeans_clusters)

        # Phase 3: Test each replacement strategy
        layer_results = {"layer": target_layer}

        strategies = [
            ("A: 9-mode KIBC centroid (continuous)", fingerprints, "centroid"),
            ("A: 9-mode KIBC ternary + pos_gamma", fingerprints, "ternary"),
            ("A: 9-mode KIBC ternary + scalar_gamma", fingerprints, "ternary_scalar"),
            (f"B: {args.kmeans_clusters}-cluster centroid", kmeans_fp, "centroid"),
            (f"B: {args.kmeans_clusters}-cluster ternary + pos_gamma", kmeans_fp, "ternary"),
            (f"B: {args.kmeans_clusters}-cluster ternary + scalar_gamma", kmeans_fp, "ternary_scalar"),
        ]

        for name, fp, mode in strategies:
            replacement = TernaryInferenceFFN(fp, mode=mode)
            handle = replace_ffn_with_hook(model, target_layer, replacement, args.device)

            ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
            ratio = ppl / baseline_ppl

            handle.remove()

            status = "✓" if ratio < 2.0 else "⚠" if ratio < 10.0 else "✗"
            print(f"    {status} {name:<50s}  PPL={ppl:>10.2f}  ratio={ratio:>6.2f}×")

            layer_results[name] = {"ppl": float(ppl), "ratio": float(ratio)}

        results.append(layer_results)

    # Summary
    print(f"\n{'='*70}")
    print(f"  SUMMARY")
    print(f"{'='*70}")
    print(f"  Baseline PPL: {baseline_ppl:.2f}")
    print(f"  Model: {args.model}")
    print()

    for lr in results:
        print(f"  Layer {lr['layer']}:")
        for k, v in lr.items():
            if k == 'layer':
                continue
            print(f"    {k:<50s}  {v['ratio']:>6.2f}×")
        print()

    # Save
    out_dir = Path("results/ternary-inference-pattern")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "baseline_ppl": float(baseline_ppl),
        "n_layers": n_layers,
        "zone_b": zone_b,
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
