#!/usr/bin/env python3
"""Test: can gate firing patterns index a ternary fact lookup table?

Previous experiment showed 9 KIBC modes capture the crystal (routing)
but lose the plate (facts). The gate already selects ~3% of neurons —
each unique gate pattern is a "fact address." If we index by gate
pattern instead of combinator mode, we might capture both crystal
AND plate.

Method:
  1. Keep gate_proj (cheap — computes WHICH neurons fire)
  2. Replace up_proj + down_proj with: gate_pattern → ternary lookup
  3. Sweep N_clusters: 16, 32, 64, 128, 256, 512
  4. Test fact recall at each cluster count

The question: at what cluster count do facts come back?

Usage:
  uv run python scripts/experiments/gate_indexed_ternary.py --model Qwen/Qwen3-8B --device mps

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

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════════════
# Test prompts (same as coherence test)
# ══════════════════════════════════════════════════════════════════════

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was", "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is", "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is", "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in", "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals", "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is", "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the", "expected": "pound"},
]

# Additional calibration texts for building the lookup table
CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "The committee voted unanimously to approve the new environmental regulations.",
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The function takes two arguments and returns their composition.",
    "During the Cambrian explosion, most major animal phyla appeared in the fossil record.",
    "The patient was admitted with acute respiratory distress and fever.",
    "To solve this equation, first isolate the variable on one side.",
    "The Renaissance began in Italy in the 14th century and spread across Europe.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "The stock market experienced significant volatility during the trading session.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The Amazon rainforest produces approximately 20 percent of the world's oxygen.",
    "Shakespeare wrote 37 plays and 154 sonnets during his literary career.",
    "The Pythagorean theorem states that a squared plus b squared equals c squared.",
    "Climate change is caused primarily by the burning of fossil fuels.",
    "The human brain contains approximately 86 billion neurons.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "DNA carries genetic information in a double helix structure.",
    "The Industrial Revolution began in Britain in the late 18th century.",
    "Quantum mechanics describes the behavior of particles at the atomic scale.",
    "The Nile is the longest river in Africa, flowing through eleven countries.",
    "Mozart composed his first symphony at the age of eight.",
    "The periodic table organizes chemical elements by atomic number.",
    "Gravity on the Moon is about one-sixth of Earth's gravitational pull.",
    "The French Revolution began in 1789 with the storming of the Bastille.",
    "Antibiotics were discovered by Alexander Fleming in 1928.",
    "The speed of sound in air is approximately 343 meters per second.",
    "Venus is the hottest planet in our solar system despite not being closest to the Sun.",
    "The Great Barrier Reef is the world's largest coral reef system.",
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def generate_text(model, tokenizer, prompt, max_new_tokens=30, device="cpu"):
    inputs = tokenizer(prompt, return_tensors="pt")
    inputs = {k: v.to(device) for k, v in inputs.items()}
    with torch.no_grad():
        outputs = model.generate(
            **inputs, max_new_tokens=max_new_tokens,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id)
    generated = outputs[0][inputs['input_ids'].shape[1]:]
    return tokenizer.decode(generated, skip_special_tokens=True)


def check_fact(generated, expected):
    return expected.lower() in generated.lower()


class GateIndexedTernaryFFN(torch.nn.Module):
    """Replace up_proj + down_proj with gate-pattern-indexed ternary lookup.
    
    Keeps gate_proj (to compute which neurons fire).
    Replaces the rest with: binarize(gate) → nearest cluster → ternary output.
    """
    
    def __init__(self, cluster_centers_gate, cluster_outputs_ternary, 
                 cluster_outputs_gamma, gate_proj_weight, gate_proj_bias=None,
                 act_fn='silu'):
        super().__init__()
        # Gate projection (kept from original model)
        self.register_buffer('gate_weight', gate_proj_weight.float())
        if gate_proj_bias is not None:
            self.register_buffer('gate_bias', gate_proj_bias.float())
        else:
            self.gate_bias = None
        
        # Cluster centers in gate space (binarized gate patterns)
        self.register_buffer('centers', torch.tensor(cluster_centers_gate, dtype=torch.float32))
        
        # Ternary output patterns per cluster
        self.register_buffer('ternary', torch.tensor(cluster_outputs_ternary, dtype=torch.float32))
        self.register_buffer('gamma', torch.tensor(cluster_outputs_gamma, dtype=torch.float32))
        
        self.act_fn = act_fn
    
    def forward(self, x):
        orig_shape = x.shape
        x_flat = x.reshape(-1, x.shape[-1]).float()
        
        # Compute gate (same as original model)
        gate = x_flat @ self.gate_weight.T
        if self.gate_bias is not None:
            gate = gate + self.gate_bias
        
        # Binarize gate (which neurons fire)
        if self.act_fn == 'silu':
            gate_activated = F.silu(gate)
        else:
            gate_activated = F.gelu(gate)
        gate_binary = (gate_activated.abs() > gate_activated.abs().mean(dim=-1, keepdim=True) * 0.5).float()
        
        # Find nearest cluster center
        # Use cosine similarity for matching
        gate_norm = F.normalize(gate_binary, dim=-1)
        center_norm = F.normalize(self.centers, dim=-1)
        similarities = gate_norm @ center_norm.T  # (batch*seq, n_clusters)
        best_cluster = similarities.argmax(dim=-1)  # (batch*seq,)
        
        # Lookup ternary output
        patterns = self.ternary[best_cluster]
        gammas = self.gamma[best_cluster]
        output = patterns * gammas
        
        return output.to(x.dtype).reshape(orig_shape)


def collect_gate_and_output_pairs(model, tokenizer, target_layer, device, 
                                   texts, n_crystal=100):
    """Collect (gate_pattern, ffn_output) pairs from diverse inputs."""
    
    layers = get_layers(model)
    layer = layers[target_layer]
    mlp = layer.mlp
    
    gate_captures = []
    output_captures = []
    
    captured = {}
    
    # Hook gate_proj output
    def gate_hook(module, input, output):
        captured['gate'] = output.detach().float()
    
    # Hook MLP output
    def mlp_hook(module, input, output):
        captured['output'] = output.detach().float()
    
    h_gate = mlp.gate_proj.register_forward_hook(gate_hook)
    h_mlp = mlp.register_forward_hook(mlp_hook)
    
    all_prompts = texts.copy()
    
    # Add crystal probes
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])
    
    # Add fact prompts
    all_prompts.extend([f["prompt"] for f in FACT_PROMPTS])
    
    for prompt in all_prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            model(**inputs)
        
        if 'gate' in captured and 'output' in captured:
            # Use last token position
            gate = captured['gate'][0, -1].cpu().numpy()
            output = captured['output'][0, -1].cpu().numpy()
            gate_captures.append(gate)
            output_captures.append(output)
    
    h_gate.remove()
    h_mlp.remove()
    
    return np.stack(gate_captures), np.stack(output_captures)


def build_gate_indexed_table(gates, outputs, n_clusters, act_fn='silu'):
    """Build ternary lookup table indexed by gate patterns."""
    from sklearn.cluster import MiniBatchKMeans
    
    # Binarize gates
    if act_fn == 'silu':
        gate_act = gates * (1 / (1 + np.exp(-gates)))  # approx SiLU
    else:
        gate_act = np.maximum(0, gates)  # approx
    
    gate_binary = (np.abs(gate_act) > np.abs(gate_act).mean(axis=-1, keepdims=True) * 0.5).astype(np.float32)
    
    # Cluster gate patterns
    kmeans = MiniBatchKMeans(n_clusters=n_clusters, random_state=42, batch_size=64)
    labels = kmeans.fit_predict(gate_binary)
    
    # For each cluster, compute ternary output pattern
    cluster_ternary = np.zeros((n_clusters, outputs.shape[1]))
    cluster_gamma = np.zeros((n_clusters, outputs.shape[1]))
    cluster_counts = np.zeros(n_clusters)
    
    for i in range(n_clusters):
        mask = labels == i
        if mask.sum() == 0:
            continue
        centroid = outputs[mask].mean(axis=0)
        cluster_ternary[i] = np.sign(centroid)
        cluster_gamma[i] = np.abs(centroid)
        cluster_counts[i] = mask.sum()
    
    return kmeans.cluster_centers_, cluster_ternary, cluster_gamma, cluster_counts


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--target-layer", type=int, default=None,
                   help="Specific layer to test (default: worst fact-recall layer from previous experiment)")
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  GATE-INDEXED TERNARY LOOKUP TEST")
    print(f"  Does indexing by gate pattern recover fact recall?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print()

    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    n_layers = model.config.num_hidden_layers
    # Test the layer that lost facts in the previous experiment
    # For Qwen3-8B: L25 lost WWII date, L15 lost water boiling point
    target_layer = args.target_layer or int(n_layers * 0.7)  # ~Zone B upper boundary
    print(f"  Target layer: {target_layer} (of {n_layers})")

    # ── Baseline ──────────────────────────────────────────────────
    print(f"\n  Baseline fact recall:")
    baseline_correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device=args.device)
        hit = check_fact(gen, fp["expected"])
        baseline_correct += int(hit)
        status = "✓" if hit else "✗"
        print(f"    {status} {fp['prompt']:<50s} → {gen.strip()[:50]}")
    baseline_rate = baseline_correct / len(FACT_PROMPTS)
    print(f"  Baseline: {baseline_correct}/{len(FACT_PROMPTS)} = {baseline_rate:.0%}")

    # ── Collect gate/output pairs ─────────────────────────────────
    print(f"\n  Collecting gate/output pairs from layer {target_layer}...")
    gates, outputs = collect_gate_and_output_pairs(
        model, tokenizer, target_layer, args.device,
        CALIBRATION_TEXTS, n_crystal=150)
    print(f"  Collected {len(gates)} pairs, gate_dim={gates.shape[1]}, out_dim={outputs.shape[1]}")

    # Get gate_proj weights for the replacement module
    layers = get_layers(model)
    gate_proj = layers[target_layer].mlp.gate_proj
    gate_weight = gate_proj.weight.data.clone()
    gate_bias = gate_proj.bias.data.clone() if gate_proj.bias is not None else None

    # ── Sweep cluster counts ──────────────────────────────────────
    cluster_counts = [9, 16, 32, 64, 128, 256]
    # Cap at number of samples
    cluster_counts = [c for c in cluster_counts if c < len(gates)]

    print(f"\n  Sweeping cluster counts: {cluster_counts}")
    print(f"  (9 = combinator-level, 256 = fine-grained gate patterns)")

    results = []

    for n_clusters in cluster_counts:
        print(f"\n{'─'*70}")
        print(f"  N_CLUSTERS = {n_clusters}")
        print(f"{'─'*70}")

        # Build lookup table
        centers, ternary_patterns, gamma_patterns, counts = build_gate_indexed_table(
            gates, outputs, n_clusters)

        active_clusters = (counts > 0).sum()
        print(f"  Active clusters: {active_clusters}/{n_clusters}")
        print(f"  Cluster sizes: min={counts[counts>0].min():.0f} "
              f"mean={counts[counts>0].mean():.1f} max={counts.max():.0f}")

        # Build replacement module
        replacement = GateIndexedTernaryFFN(
            centers, ternary_patterns, gamma_patterns,
            gate_weight, gate_bias).to(args.device)

        # Install hook
        mlp = layers[target_layer].mlp
        def make_hook(repl):
            def hook_fn(module, input, output):
                x = input[0] if isinstance(input, tuple) else input
                return repl(x)
            return hook_fn

        handle = mlp.register_forward_hook(make_hook(replacement))

        # Test fact recall
        correct = 0
        for fp in FACT_PROMPTS:
            gen = generate_text(model, tokenizer, fp["prompt"], device=args.device)
            hit = check_fact(gen, fp["expected"])
            correct += int(hit)
            status = "✓" if hit else "✗"
            print(f"    {status} {fp['prompt']:<50s} → {gen.strip()[:50]}")

        handle.remove()

        fact_rate = correct / len(FACT_PROMPTS)
        delta = fact_rate - baseline_rate
        print(f"  Fact recall: {correct}/{len(FACT_PROMPTS)} = {fact_rate:.0%} (Δ={delta:+.0%})")

        # Storage estimate
        storage_ternary = n_clusters * outputs.shape[1] * 1  # 1 bit per ternary
        storage_gamma = n_clusters * outputs.shape[1] * 2    # 16-bit gamma
        storage_gate = gate_weight.numel() * 2               # 16-bit gate_proj
        total_kb = (storage_ternary + storage_gamma + storage_gate) / 1024
        
        # Original FFN storage (gate + up + down)
        orig_params = gate_weight.numel() * 3  # gate + up + down roughly same size
        orig_kb = orig_params * 2 / 1024
        compression = orig_kb / total_kb

        print(f"  Storage: {total_kb:.0f} KB (original: {orig_kb:.0f} KB, compression: {compression:.1f}×)")

        results.append({
            "n_clusters": n_clusters,
            "fact_rate": fact_rate,
            "delta": delta,
            "active_clusters": int(active_clusters),
            "storage_kb": total_kb,
            "compression": compression,
        })

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY — Layer {target_layer}")
    print(f"{'='*70}")
    print(f"  Baseline fact recall: {baseline_rate:.0%}")
    print()
    print(f"  {'Clusters':>8s}  {'Fact rate':>9s}  {'Δ':>5s}  {'Storage':>10s}  {'Compress':>8s}")
    print(f"  {'─'*8}  {'─'*9}  {'─'*5}  {'─'*10}  {'─'*8}")
    
    for r in results:
        print(f"  {r['n_clusters']:>8d}  {r['fact_rate']:>8.0%}  {r['delta']:>+4.0%}  "
              f"{r['storage_kb']:>8.0f}KB  {r['compression']:>7.1f}×")

    # Save
    out_dir = Path("results/gate-indexed-ternary")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}_L{target_layer}.json"
    
    save_data = {
        "model": args.model,
        "target_layer": target_layer,
        "baseline_fact_rate": baseline_rate,
        "n_calibration_samples": len(gates),
        "results": results,
    }
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
