#!/usr/bin/env python3
"""Test: are the 9 ternary modes the SAME across all layers?

If the transformer is a self-similar compilation pipeline, the 9 modes
should be universal — the same 9 programs applied at every depth, just
operating on different data. If not, modes are layer-specific.

Method:
  1. For each layer, collect FFN outputs on calibration data
  2. K-means cluster into 9 modes per layer
  3. Compute ternary pattern = sign(centroid) for each mode
  4. Compare ternary patterns ACROSS layers:
     a. Cosine similarity matrix of all 9×36 = 324 patterns
     b. Hungarian matching: for each layer pair, find optimal 1:1 mode alignment
     c. Cross-layer mode correlation after alignment
  5. Also check: do the modes at L13 match the modes at L30?
     If yes → universal instruction set
     If block-diagonal → phase-specific instructions

Additional tests:
  - Can a classifier trained at ONE layer work at ANOTHER layer?
    (transfer accuracy = strongest universality test)
  - Do the mode proportions (what % of tokens fall in each mode) vary by depth?

Usage:
  uv run python scripts/experiments/mode_universality.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path
from itertools import combinations

import numpy as np
import torch
from scipy.optimize import linear_sum_assignment
from sklearn.cluster import MiniBatchKMeans
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════════════
# Calibration data
# ══════════════════════════════════════════════════════════════════════

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
    "Mars is known as the Red Planet due to iron oxide on its surface.",
]

FACT_PROMPTS = [
    "The capital of France is",
    "Water boils at",
    "The first president of the United States was",
    "The chemical symbol for gold is",
    "The largest planet in our solar system is",
    "Pi is approximately equal to",
    "Einstein's famous equation is E equals",
    "The freezing point of water in Celsius is",
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def collect_ffn_data(model, tokenizer, target_layer, device, texts, n_crystal=100):
    """Collect FFN (input, output) pairs for one layer."""
    layers = get_layers(model)
    mlp = layers[target_layer].mlp
    captured = {}

    def pre_hook(module, input):
        x = input[0] if isinstance(input, tuple) else input
        captured['input'] = x.detach().float()

    def post_hook(module, input, output):
        captured['output'] = output.detach().float()

    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_post = mlp.register_forward_hook(post_hook)

    all_inputs = []
    all_outputs = []

    all_prompts = list(texts)
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])
    all_prompts.extend(FACT_PROMPTS)

    for prompt in all_prompts:
        captured.clear()
        inputs = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=128)
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs)
        if 'input' in captured and 'output' in captured:
            inp = captured['input'][0].cpu().numpy()
            out = captured['output'][0].cpu().numpy()
            if len(inp) > 24:
                idx = np.linspace(0, len(inp) - 1, 24, dtype=int)
                inp, out = inp[idx], out[idx]
            all_inputs.append(inp)
            all_outputs.append(out)

    h_pre.remove()
    h_post.remove()
    return np.concatenate(all_inputs), np.concatenate(all_outputs)


def build_modes(outputs, n_modes=9):
    """Cluster FFN outputs into modes, return ternary patterns + centroids + labels."""
    kmeans = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(64, len(outputs)))
    labels = kmeans.fit_predict(outputs)

    d = outputs.shape[1]
    ternary = np.zeros((n_modes, d))
    centroids = np.zeros((n_modes, d))
    proportions = np.zeros(n_modes)

    for i in range(n_modes):
        mask = labels == i
        proportions[i] = mask.sum() / len(labels)
        if mask.sum() == 0:
            continue
        centroid = outputs[mask].mean(axis=0)
        centroids[i] = centroid
        ternary[i] = np.sign(centroid)

    return ternary, centroids, labels, proportions


def cosine_matrix(A, B):
    """Cosine similarity between rows of A and rows of B."""
    A_norm = A / (np.linalg.norm(A, axis=1, keepdims=True) + 1e-10)
    B_norm = B / (np.linalg.norm(B, axis=1, keepdims=True) + 1e-10)
    return A_norm @ B_norm.T


def hungarian_match(cos_mat):
    """Find optimal 1:1 alignment that maximizes total cosine similarity."""
    # linear_sum_assignment minimizes, so negate
    row_ind, col_ind = linear_sum_assignment(-cos_mat)
    matched_cos = cos_mat[row_ind, col_ind]
    return row_ind, col_ind, matched_cos


def train_classifier(inputs, labels, n_modes, n_epochs=100, lr=0.01):
    """Train linear classifier, return weight matrix and accuracy."""
    import torch.nn.functional as F
    d = inputs.shape[1]
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)
    W = torch.randn(n_modes, d) * 0.01
    W.requires_grad_(True)
    opt = torch.optim.Adam([W], lr=lr)
    best_acc, best_W = 0, None
    for _ in range(n_epochs):
        logits = X @ W.T
        loss = F.cross_entropy(logits, Y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            acc = (logits.argmax(-1) == Y).float().mean().item()
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()
    return best_W.numpy(), best_acc


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-modes", type=int, default=9)
    args = p.parse_args()

    print(f"\n{'='*70}")
    print(f"  MODE UNIVERSALITY TEST")
    print(f"  Are the 9 ternary modes the same across all layers?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Modes: {args.n_modes}")
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
    print(f"  Layers: {n_layers}, d_model: {d_model}")

    # ── Phase 1: Build modes for every layer ──────────────────────
    print(f"\n  Phase 1: Collecting modes for all {n_layers} layers...")

    all_ternary = {}      # layer -> (n_modes, d_model)
    all_centroids = {}    # layer -> (n_modes, d_model)
    all_proportions = {}  # layer -> (n_modes,)
    all_inputs = {}       # layer -> (n_samples, d_model)
    all_labels = {}       # layer -> (n_samples,)

    for li in range(n_layers):
        t0 = time.time()
        inputs, outputs = collect_ffn_data(
            model, tokenizer, li, args.device, CALIBRATION_TEXTS, n_crystal=100)
        ternary, centroids, labels, proportions = build_modes(outputs, args.n_modes)
        all_ternary[li] = ternary
        all_centroids[li] = centroids
        all_proportions[li] = proportions
        all_inputs[li] = inputs
        all_labels[li] = labels
        elapsed = time.time() - t0
        top3 = sorted(proportions, reverse=True)[:3]
        print(f"    L{li:>2d}: {elapsed:.1f}s  top3_prop=[{top3[0]:.2f},{top3[1]:.2f},{top3[2]:.2f}]")

    # ── Phase 2: Cross-layer ternary pattern comparison ───────────
    print(f"\n{'='*70}")
    print(f"  Phase 2: Cross-layer mode comparison")
    print(f"{'='*70}")

    # For each pair of layers, compute:
    # 1. Raw cosine between all 9×9 mode pairs
    # 2. Hungarian-matched cosine (best 1:1 alignment)
    n = n_layers
    matched_scores = np.zeros((n, n))  # mean matched cosine
    min_matched = np.zeros((n, n))     # worst matched mode

    for i in range(n):
        for j in range(i, n):
            cos = cosine_matrix(all_ternary[i], all_ternary[j])
            _, _, matched_cos = hungarian_match(cos)
            matched_scores[i, j] = matched_cos.mean()
            matched_scores[j, i] = matched_cos.mean()
            min_matched[i, j] = matched_cos.min()
            min_matched[j, i] = matched_cos.min()

    # Print summary
    print(f"\n  Hungarian-matched cosine (mean across 9 matched modes):")
    print(f"  {'':>5s}", end="")
    label_layers = list(range(0, n, max(1, n // 12)))
    for j in label_layers:
        print(f"  L{j:>2d}", end="")
    print()

    for i in label_layers:
        print(f"  L{i:>2d}", end="")
        for j in label_layers:
            v = matched_scores[i, j]
            print(f"  {v:.2f}", end="")
        print()

    # Summary statistics
    # Same-phase pairs vs cross-phase pairs
    phase1 = list(range(0, 12))    # L0-L11
    phase2 = list(range(12, 24))   # L12-L23
    phase3 = list(range(24, n))    # L24-L35

    within_phase = []
    cross_phase = []
    for i in range(n):
        for j in range(i + 1, n):
            score = matched_scores[i, j]
            same = ((i in phase1 and j in phase1) or
                    (i in phase2 and j in phase2) or
                    (i in phase3 and j in phase3))
            if same:
                within_phase.append(score)
            else:
                cross_phase.append(score)

    print(f"\n  Within-phase mean matched cosine: {np.mean(within_phase):.4f} ± {np.std(within_phase):.4f}")
    print(f"  Cross-phase mean matched cosine:  {np.mean(cross_phase):.4f} ± {np.std(cross_phase):.4f}")
    print(f"  Overall mean matched cosine:      {np.mean(list(within_phase) + list(cross_phase)):.4f}")

    # Adjacent layer similarity
    adjacent = [matched_scores[i, i+1] for i in range(n - 1)]
    print(f"\n  Adjacent layer matched cosine:")
    for i in range(n - 1):
        bar = "█" * int(adjacent[i] * 30)
        print(f"    L{i:>2d}↔L{i+1:>2d}: {adjacent[i]:.3f}  {bar}")

    # ── Phase 3: Classifier transfer test ─────────────────────────
    print(f"\n{'='*70}")
    print(f"  Phase 3: Classifier transfer (train at one layer, test at another)")
    print(f"{'='*70}")

    # Train classifiers at a few representative layers
    source_layers = [1, 8, 15, 19, 25, 30]  # one per phase
    source_layers = [l for l in source_layers if l < n_layers]

    classifiers = {}
    for sl in source_layers:
        print(f"\n  Training classifier at L{sl}...")
        W, acc = train_classifier(all_inputs[sl], all_labels[sl], args.n_modes)
        classifiers[sl] = W
        print(f"    Self accuracy: {acc:.1%}")

    # Test each classifier at every other layer
    # But labels won't match — we need to use Hungarian matching
    print(f"\n  Transfer accuracy (Hungarian-aligned):")
    print(f"  {'Source':>8s}", end="")
    for tl in source_layers:
        print(f"  L{tl:>2d}", end="")
    print(f"  {'mean':>6s}")

    transfer_matrix = np.zeros((len(source_layers), n_layers))

    for si, sl in enumerate(source_layers):
        W = classifiers[sl]
        row_accs = []
        for tl in range(n_layers):
            # Classify target layer inputs with source classifier
            X = torch.tensor(all_inputs[tl], dtype=torch.float32)
            Wt = torch.tensor(W, dtype=torch.float32)
            with torch.no_grad():
                pred = (X @ Wt.T).argmax(dim=-1).numpy()

            # Hungarian-match predicted clusters to target clusters
            target_labels = all_labels[tl]
            # Build confusion matrix
            conf = np.zeros((args.n_modes, args.n_modes))
            for p, t in zip(pred, target_labels):
                conf[p, t] += 1
            _, col_map, _ = hungarian_match(conf)

            # Remap predictions and compute accuracy
            remapped = np.array([col_map[p] for p in pred])
            acc = (remapped == target_labels).mean()
            transfer_matrix[si, tl] = acc
            row_accs.append(acc)

        # Print row for selected target layers
        print(f"  L{sl:>2d}→  ", end="")
        for tl in source_layers:
            print(f"  {transfer_matrix[si, tl]:.2f}", end="")
        mean_acc = np.mean(row_accs)
        print(f"  {mean_acc:.3f}")

    # Print full transfer profile for each source
    print(f"\n  Full transfer profile (source → all targets):")
    for si, sl in enumerate(source_layers):
        accs = transfer_matrix[si]
        print(f"\n    L{sl} classifier applied to each layer:")
        for tl in range(n_layers):
            bar = "█" * int(accs[tl] * 40)
            marker = " ◀ self" if tl == sl else ""
            print(f"      L{tl:>2d}: {accs[tl]:.3f}  {bar}{marker}")

    # ── Phase 4: Mode proportion depth profile ───────────────────
    print(f"\n{'='*70}")
    print(f"  Phase 4: Mode proportions across depth")
    print(f"{'='*70}")

    # Stack proportions: (n_layers, n_modes)
    prop_matrix = np.stack([all_proportions[l] for l in range(n_layers)])

    # Entropy of mode proportions per layer
    print(f"\n  Mode entropy (higher = more uniform distribution):")
    for li in range(n_layers):
        props = prop_matrix[li]
        entropy = -np.sum(props * np.log(props + 1e-10))
        max_entropy = np.log(args.n_modes)
        norm_entropy = entropy / max_entropy
        bar = "█" * int(norm_entropy * 30)
        print(f"    L{li:>2d}: H={entropy:.2f} ({norm_entropy:.2f} normalized)  {bar}")

    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/mode-universality")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"

    save_data = {
        "model": args.model,
        "n_layers": n_layers,
        "n_modes": args.n_modes,
        "matched_cosine_matrix": matched_scores.tolist(),
        "min_matched_cosine": min_matched.tolist(),
        "adjacent_matched": adjacent,
        "within_phase_mean": float(np.mean(within_phase)),
        "cross_phase_mean": float(np.mean(cross_phase)),
        "overall_mean": float(np.mean(list(within_phase) + list(cross_phase))),
        "transfer_matrix": transfer_matrix.tolist(),
        "source_layers": source_layers,
        "proportions": prop_matrix.tolist(),
    }

    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
