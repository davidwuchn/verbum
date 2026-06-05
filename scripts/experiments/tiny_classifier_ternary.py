#!/usr/bin/env python3
"""Test: replace entire FFN with tiny classifier → ternary lookup.

Previous experiments showed:
  - 9 ternary patterns capture the crystal (PPL ≤1.06×)
  - Gate-indexed patterns recover facts (80%+ at all cluster counts)
  - But gate_proj is 96MB — dominates storage

This test: replace gate_proj with a tiny linear classifier (d_model → N_modes).
Total FFN becomes: small matrix + ternary lookup. ~450× compression.

Method:
  1. Collect (mlp_input, gate_pattern, mlp_output) triples
  2. Cluster gate patterns into N modes
  3. Train tiny classifier: mlp_input → mode_id (linear, no hidden layers)
  4. Replace entire MLP: tiny_classify(x) → lookup ternary[mode] × gamma
  5. Test PPL + fact recall

Usage:
  uv run python scripts/experiments/tiny_classifier_ternary.py --model Qwen/Qwen3-8B --device mps

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
# Prompts
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
    "The Eiffel Tower was built for the 1889 World's Fair in Paris.",
    "The mitochondria is often called the powerhouse of the cell.",
    "Abraham Lincoln delivered the Gettysburg Address in 1863.",
    "The Pacific Ocean is the largest and deepest ocean on Earth.",
    "Beethoven composed his Ninth Symphony while completely deaf.",
    "The Magna Carta was signed in 1215 by King John of England.",
    "Insulin was first used to treat diabetes in 1922.",
    "Mount Everest is the tallest mountain above sea level at 8,849 meters.",
    "The printing press was invented by Johannes Gutenberg around 1440.",
    "Mars is known as the Red Planet due to iron oxide on its surface.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity as the curvature of spacetime caused by mass and energy.",
    "In a large mixing bowl, combine the flour, sugar, and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable on one side by subtracting three from both sides.",
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


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        labels = inputs["input_ids"].clone()
        with torch.no_grad():
            outputs = model(**inputs, labels=labels)
            total_loss += outputs.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return np.exp(total_loss / total_tokens)


class TinyClassifierFFN(torch.nn.Module):
    """Entire FFN replaced by: tiny linear classifier → ternary lookup.
    
    classifier: (d_model) → (n_modes) via single matrix multiply
    lookup: mode_id → ternary_pattern × gamma
    
    Total params: d_model × n_modes + n_modes × d_model × 3 bytes
    vs original: d_model × intermediate × 3 matrices × 2 bytes
    """
    
    def __init__(self, classifier_weight, ternary_patterns, gamma_patterns):
        super().__init__()
        # classifier_weight: (n_modes, d_model) — trained linear layer
        self.register_buffer('classifier', torch.tensor(classifier_weight, dtype=torch.float32))
        self.register_buffer('ternary', torch.tensor(ternary_patterns, dtype=torch.float32))
        self.register_buffer('gamma', torch.tensor(gamma_patterns, dtype=torch.float32))
    
    def forward(self, x):
        orig_shape = x.shape
        x_flat = x.reshape(-1, x.shape[-1]).float()
        
        # Classify: single matmul
        logits = x_flat @ self.classifier.T  # (batch*seq, n_modes)
        mode = logits.argmax(dim=-1)  # (batch*seq,)
        
        # Lookup
        output = self.ternary[mode] * self.gamma[mode]
        
        return output.to(x.dtype).reshape(orig_shape)


def collect_training_data(model, tokenizer, target_layer, device, texts, n_crystal=150):
    """Collect (mlp_input, mlp_output) pairs for classifier training."""
    
    layers = get_layers(model)
    mlp = layers[target_layer].mlp
    
    captured = {}
    
    def input_hook(module, input, output):
        captured['input'] = input[0].detach().float() if isinstance(input, tuple) else input.detach().float()
    
    def output_hook(module, input, output):
        captured['output'] = output.detach().float()
    
    h_in = mlp.register_forward_hook(
        lambda m, inp, out: captured.update({'input': (inp[0] if isinstance(inp, tuple) else inp).detach().float()}))
    
    # Actually, we need a pre-hook for input and post-hook for output
    def pre_hook(module, input):
        x = input[0] if isinstance(input, tuple) else input
        captured['input'] = x.detach().float()
    
    def post_hook(module, input, output):
        captured['output'] = output.detach().float()
    
    # Remove the lambda hook and use proper hooks
    h_in.remove()
    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_post = mlp.register_forward_hook(post_hook)
    
    all_inputs = []
    all_outputs = []
    
    all_prompts = texts.copy()
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])
    all_prompts.extend([f["prompt"] for f in FACT_PROMPTS])
    
    for prompt in all_prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            model(**inputs)
        
        if 'input' in captured and 'output' in captured:
            # Collect ALL token positions (not just last) for richer training data
            inp = captured['input'][0].cpu().numpy()   # (seq, d_model)
            out = captured['output'][0].cpu().numpy()   # (seq, d_model)
            # Subsample if sequence is long
            if len(inp) > 32:
                idx = np.linspace(0, len(inp)-1, 32, dtype=int)
                inp = inp[idx]
                out = out[idx]
            all_inputs.append(inp)
            all_outputs.append(out)
    
    h_pre.remove()
    h_post.remove()
    
    all_inputs = np.concatenate(all_inputs, axis=0)
    all_outputs = np.concatenate(all_outputs, axis=0)
    
    return all_inputs, all_outputs


def train_classifier(inputs, labels, n_modes, n_epochs=100, lr=0.01):
    """Train a linear classifier: input → mode_id."""
    d_model = inputs.shape[1]
    
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)
    
    # Simple linear classifier
    W = torch.randn(n_modes, d_model) * 0.01
    W.requires_grad_(True)
    
    optimizer = torch.optim.Adam([W], lr=lr)
    
    best_acc = 0
    best_W = None
    
    for epoch in range(n_epochs):
        logits = X @ W.T  # (n_samples, n_modes)
        loss = F.cross_entropy(logits, Y)
        
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        with torch.no_grad():
            preds = logits.argmax(dim=-1)
            acc = (preds == Y).float().mean().item()
            
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()
        
        if (epoch + 1) % 25 == 0:
            print(f"      Epoch {epoch+1}: loss={loss.item():.4f} acc={acc:.3f}")
    
    return best_W.numpy(), best_acc


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--target-layer", type=int, default=None)
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  TINY CLASSIFIER → TERNARY LOOKUP TEST")
    print(f"  Replace ENTIRE FFN with small matrix + ternary table")
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
    d_model = model.config.hidden_size
    intermediate = model.config.intermediate_size
    target_layer = args.target_layer or int(n_layers * 0.55)  # Middle of Zone B
    print(f"  Layers: {n_layers}, d_model: {d_model}, intermediate: {intermediate}")
    print(f"  Target layer: {target_layer}")

    # ── Baseline ──────────────────────────────────────────────────
    print(f"\n  Measuring baseline...")
    baseline_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    
    baseline_correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device=args.device)
        hit = check_fact(gen, fp["expected"])
        baseline_correct += int(hit)
    baseline_fact_rate = baseline_correct / len(FACT_PROMPTS)
    print(f"  Baseline PPL: {baseline_ppl:.2f}, Facts: {baseline_correct}/{len(FACT_PROMPTS)} = {baseline_fact_rate:.0%}")

    # ── Collect training data ─────────────────────────────────────
    print(f"\n  Collecting training data from layer {target_layer}...")
    mlp_inputs, mlp_outputs = collect_training_data(
        model, tokenizer, target_layer, args.device, CALIBRATION_TEXTS, n_crystal=150)
    print(f"  Collected {len(mlp_inputs)} samples, d_model={d_model}")

    # ── Original FFN storage ──────────────────────────────────────
    orig_params = d_model * intermediate * 3  # gate + up + down
    orig_bytes = orig_params * 2  # float16
    orig_mb = orig_bytes / 1024 / 1024

    # ── Sweep mode counts ─────────────────────────────────────────
    mode_counts = [9, 16, 32, 64]
    
    results = []
    
    for n_modes in mode_counts:
        if n_modes >= len(mlp_inputs):
            continue
            
        print(f"\n{'─'*70}")
        print(f"  N_MODES = {n_modes}")
        print(f"{'─'*70}")
        
        # Cluster outputs to get mode assignments
        from sklearn.cluster import MiniBatchKMeans
        kmeans = MiniBatchKMeans(n_clusters=n_modes, random_state=42, batch_size=min(64, len(mlp_outputs)))
        labels = kmeans.fit_predict(mlp_outputs)
        
        # Compute ternary patterns per mode
        ternary_patterns = np.zeros((n_modes, d_model))
        gamma_patterns = np.zeros((n_modes, d_model))
        for i in range(n_modes):
            mask = labels == i
            if mask.sum() == 0:
                continue
            centroid = mlp_outputs[mask].mean(axis=0)
            ternary_patterns[i] = np.sign(centroid)
            gamma_patterns[i] = np.abs(centroid)
        
        # Train tiny classifier
        print(f"    Training {d_model}×{n_modes} classifier ({d_model * n_modes} params)...")
        classifier_W, train_acc = train_classifier(mlp_inputs, labels, n_modes)
        print(f"    Classifier accuracy: {train_acc:.1%}")
        
        # Storage calculation
        classifier_bytes = d_model * n_modes * 2  # float16
        ternary_bytes = n_modes * d_model * 1     # 1 byte per trit (could be 2 bits)
        gamma_bytes = n_modes * d_model * 2       # float16
        total_bytes = classifier_bytes + ternary_bytes + gamma_bytes
        total_kb = total_bytes / 1024
        compression = orig_bytes / total_bytes
        
        print(f"    Storage: classifier={classifier_bytes/1024:.0f}KB + "
              f"ternary={ternary_bytes/1024:.0f}KB + gamma={gamma_bytes/1024:.0f}KB "
              f"= {total_kb:.0f}KB (original: {orig_mb:.0f}MB, compression: {compression:.0f}×)")
        
        # Install replacement
        replacement = TinyClassifierFFN(classifier_W, ternary_patterns, gamma_patterns)
        replacement = replacement.to(args.device)
        
        layers = get_layers(model)
        mlp = layers[target_layer].mlp
        
        def make_hook(repl):
            def hook_fn(module, input, output):
                x = input[0] if isinstance(input, tuple) else input
                return repl(x)
            return hook_fn
        
        handle = mlp.register_forward_hook(make_hook(replacement))
        
        # Test PPL
        ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
        ppl_ratio = ppl / baseline_ppl
        
        # Test fact recall
        correct = 0
        for fp in FACT_PROMPTS:
            gen = generate_text(model, tokenizer, fp["prompt"], device=args.device)
            hit = check_fact(gen, fp["expected"])
            correct += int(hit)
            status = "✓" if hit else "✗"
            print(f"      {status} {fp['prompt']:<50s} → {gen.strip()[:50]}")
        
        handle.remove()
        
        fact_rate = correct / len(FACT_PROMPTS)
        
        print(f"\n    PPL: {ppl:.2f} ({ppl_ratio:.2f}× baseline)")
        print(f"    Facts: {correct}/{len(FACT_PROMPTS)} = {fact_rate:.0%} (baseline: {baseline_fact_rate:.0%})")
        print(f"    Classifier: {d_model}×{n_modes} = {d_model*n_modes:,} params")
        print(f"    Compression: {compression:.0f}× ({total_kb:.0f}KB vs {orig_mb:.0f}MB)")
        
        results.append({
            "n_modes": n_modes,
            "ppl": float(ppl),
            "ppl_ratio": float(ppl_ratio),
            "fact_rate": float(fact_rate),
            "train_acc": float(train_acc),
            "compression": float(compression),
            "storage_kb": float(total_kb),
            "classifier_params": d_model * n_modes,
        })

    # ── Summary ───────────────────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  SUMMARY — Layer {target_layer}")
    print(f"{'='*70}")
    print(f"  Baseline: PPL={baseline_ppl:.2f}, Facts={baseline_fact_rate:.0%}")
    print(f"  Original FFN: {orig_mb:.0f}MB ({orig_params:,} params)")
    print()
    print(f"  {'Modes':>5s}  {'PPL':>7s}  {'Ratio':>6s}  {'Facts':>6s}  {'ClsAcc':>7s}  {'Size':>8s}  {'Compress':>8s}")
    print(f"  {'─'*5}  {'─'*7}  {'─'*6}  {'─'*6}  {'─'*7}  {'─'*8}  {'─'*8}")
    
    for r in results:
        print(f"  {r['n_modes']:>5d}  {r['ppl']:>7.2f}  {r['ppl_ratio']:>5.2f}×  "
              f"{r['fact_rate']:>5.0%}  {r['train_acc']:>6.1%}  "
              f"{r['storage_kb']:>6.0f}KB  {r['compression']:>7.0f}×")

    # Save
    out_dir = Path("results/tiny-classifier-ternary")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}_L{target_layer}.json"
    
    with open(out_path, "w") as f:
        json.dump({"model": args.model, "target_layer": target_layer,
                    "baseline_ppl": float(baseline_ppl),
                    "baseline_fact_rate": float(baseline_fact_rate),
                    "orig_mb": float(orig_mb), "results": results}, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
