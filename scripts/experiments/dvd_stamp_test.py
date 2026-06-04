#!/usr/bin/env python3
"""DVD Stamp Test — Does gradient topology compound less than magnitude?

THE DVD HYPOTHESIS: A trained model's gradient-zero map IS the holographic
pattern — the pits and lands of a DVD. The gradient goes to zero where
beta reduction found irreducible positions. Copying this binary topology
(the "stamp") might compound less than copying continuous weight magnitudes,
because topology errors are discrete (bit flips) not continuous (drift).

THREE MASKS at 50% sparsity, head-to-head:
  M_magnitude:  zero the 50% smallest |W| per row (current best, s182-183)
  M_gradient:   zero the 50% smallest mean|∇W| per row (the DVD stamp)
  M_node:       zero positions where BOTH |W| and |∇W| are below median

MEASUREMENT: Cumulative compounding curve.
  For L in [1..36]: ternarize layers 0..L-1, keep L..35 float.
  At each depth: measure hidden state cosine vs full-float forward pass.
  Plot the three curves. If M_gradient stays higher → DVD hypothesis confirmed.

Also measures full-model PPL for the complete ternarization with each mask.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/dvd_stamp_test.py

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "dvd-stamp-test"


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════════
# Phase 1: Gradient Collection
# ═══════════════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    # Factual knowledge
    "The capital of France is Paris, which is located along the Seine river in northern France.",
    "Albert Einstein was born in Ulm, Germany in 1879 and developed the theory of special relativity.",
    "The speed of light is approximately 299,792,458 meters per second in a vacuum.",
    "DNA stands for deoxyribonucleic acid, the molecule that carries genetic instructions.",
    "Photosynthesis converts sunlight, water, and carbon dioxide into glucose and oxygen.",
    "Jupiter is the largest planet in our solar system with a mass of 1.898 × 10^27 kg.",
    "The chemical symbol for gold is Au, derived from the Latin word aurum meaning shining dawn.",
    "Water boils at a temperature of 100 degrees Celsius at standard atmospheric pressure.",
    # Mathematics
    "The derivative of sin(x) is cos(x), and the derivative of cos(x) is negative sin(x).",
    "The Pythagorean theorem states that in a right triangle, a² + b² = c² where c is the hypotenuse.",
    "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.",
    "Euler's identity e^(iπ) + 1 = 0 connects five fundamental mathematical constants.",
    "The Fibonacci sequence is defined recursively: F(n) = F(n-1) + F(n-2), with F(0)=0 and F(1)=1.",
    "The integral of 1/x dx is ln|x| + C, where C is the constant of integration.",
    # Code
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nprint(arr.mean(), arr.std())",
    "class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val",
    "SELECT name, age FROM users WHERE age > 18 ORDER BY name ASC LIMIT 100;",
    "fn main() { let mut v: Vec<i32> = vec![1,2,3]; v.push(4); println!(\"{:?}\", v); }",
    "docker build -t myapp:latest . && docker run -p 8080:8080 myapp:latest",
    # Science
    "Quantum entanglement occurs when two particles become correlated such that measuring one instantly determines the state of the other.",
    "Natural selection favors organisms that are best adapted to their environment, driving evolution over millions of years.",
    "The second law of thermodynamics states that entropy in an isolated system always increases over time.",
    "Neurons communicate through electrical impulses called action potentials and chemical signals called neurotransmitters.",
    "Black holes form when massive stars exhaust their nuclear fuel and collapse under their own gravitational force.",
    # Narrative
    "Once upon a time in a small village nestled in the mountains, there lived an old clockmaker who could hear the ticking of every clock in town.",
    "The industrial revolution transformed society by mechanizing production, urbanizing populations, and creating new social classes.",
    "Democracy requires the active participation of citizens through voting, civic engagement, and holding elected officials accountable.",
    "The history of music reflects the cultural values of each era, from Gregorian chants to jazz to electronic dance music.",
    "Climate change affects ecosystems through rising temperatures, altered precipitation patterns, ocean acidification, and habitat loss.",
    # Multilingual
    "La revolución francesa de 1789 transformó radicalmente la estructura política y social de Francia.",
    "日本の首都は東京で、世界最大の都市圏の一つとして約3700万人が暮らしています。",
    "Der kategorische Imperativ von Kant besagt, dass man nur nach derjenigen Maxime handeln soll.",
    "L'intelligence artificielle est un domaine de l'informatique qui vise à créer des systèmes capables de raisonner.",
    # Lambda / formal
    "(λx. λy. x y) (λz. z) reduces to (λy. (λz. z) y) which further reduces to (λy. y) = I",
    "The Y combinator Y = λf. (λx. f (x x)) (λx. f (x x)) enables recursion without self-reference.",
    "Church numerals: 0 = λf.λx.x, 1 = λf.λx.f x, 2 = λf.λx.f(f x), succ = λn.λf.λx.f(n f x)",
    "S K K x = K x (K x) = x, proving that S K K is extensionally equal to the identity combinator I.",
    # Technical / systems
    "The TCP/IP protocol stack has four layers: link, internet, transport, and application.",
    "A transformer architecture uses multi-head self-attention to model dependencies regardless of distance.",
    "The halting problem proves that no algorithm can determine whether an arbitrary program will halt.",
    "Gradient descent minimizes a loss function by iteratively moving in the direction of steepest descent.",
    "The attention mechanism computes a weighted sum: Attention(Q,K,V) = softmax(QK^T/√d_k)V.",
    # Philosophy
    "The trolley problem asks whether it is morally permissible to divert a trolley to kill one person instead of five.",
    "Descartes' cogito ergo sum establishes the existence of the thinking self as the one indubitable truth.",
    "Kant's categorical imperative: act only according to that maxim which you can will to be a universal law.",
    # Dialogue
    "User: What is the weather like today?\nAssistant: I don't have access to real-time weather data.",
    "Question: How does a neural network learn?\nAnswer: Through backpropagation of gradients and iterative weight updates.",
    # Additional diverse content for gradient stability
    "The Amazon rainforest covers approximately 5.5 million square kilometres and produces 20 percent of the world's oxygen.",
    "In computer science, a hash table uses a hash function to compute an index into an array of buckets.",
    "Machine learning focuses on the development of programs that can access data and use it to learn for themselves.",
    "Lambda calculus is a formal system for expressing computation based on function abstraction and application.",
    "The Great Wall of China stretches over 13,000 miles across northern China and was built over many centuries.",
    "Plate tectonics explains how the Earth's lithosphere is divided into plates that move, collide, and separate.",
    "A function f is continuous at point c if the limit as x approaches c equals f(c).",
    "The determinant of a 2x2 matrix [[a,b],[c,d]] is computed as ad minus bc.",
    "In set theory, the union of A and B contains all elements that belong to either A or B or both.",
    "MapReduce processes large datasets by mapping each element independently, then reducing the results.",
    "The CAP theorem states that a distributed system cannot simultaneously guarantee consistency, availability, and partition tolerance.",
    "CRISPR-Cas9 is a gene editing tool that allows precise modifications to DNA sequences in living organisms.",
    "The ocean covers approximately seventy percent of Earth's surface and contains 97 percent of the planet's water.",
    "Ancient civilizations developed writing systems to record transactions, preserve knowledge, and communicate.",
    "Education serves as the foundation for individual growth, economic development, and social cohesion.",
]


TARGET_MODULES_FFN = ["gate_proj", "up_proj", "down_proj"]
TARGET_MODULES_ATTN = ["q_proj", "k_proj", "v_proj", "o_proj"]
TARGET_MODULES = TARGET_MODULES_FFN + TARGET_MODULES_ATTN


def collect_gradient_maps(
    model,
    tokenizer,
    device: str,
    n_batches: int = 50,
    batch_size: int = 4,
    max_length: int = 256,
) -> dict[str, torch.Tensor]:
    """Collect per-weight mean |∇W| across calibration batches.

    Returns dict mapping parameter name → mean_abs_grad tensor (same shape as weight).
    This is the DVD: the map of where GD deposited near-zero gradients.
    """
    log(f"\n{'═' * 78}")
    log(f"  PHASE 1: COLLECTING GRADIENT DVD  ({n_batches} batches)")
    log(f"{'═' * 78}")

    # Prepare calibration batches
    texts = CALIBRATION_TEXTS.copy()
    # Duplicate to fill batches if needed
    while len(texts) < n_batches * batch_size:
        texts.extend(CALIBRATION_TEXTS)
    texts = texts[: n_batches * batch_size]

    batches = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        encoded = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )
        batches.append(encoded)

    # Identify target parameters
    target_params: dict[str, nn.Parameter] = {}
    for name, param in model.named_parameters():
        if any(m in name for m in TARGET_MODULES) and "weight" in name:
            target_params[name] = param

    log(f"  Tracking {len(target_params)} weight tensors")

    # Accumulators — per-element sum of |grad| on CPU
    accum: dict[str, torch.Tensor] = {}
    valid_counts: dict[str, int] = {}
    for name, param in target_params.items():
        accum[name] = torch.zeros(param.shape, dtype=torch.float32)
        valid_counts[name] = 0

    # Scale loss down before backward to prevent fp16 gradient overflow.
    # Early layer gradients can exceed fp16 max (~65504) → NaN.
    # We divide loss by GRAD_SCALE, so all gradients are divided by it.
    # Then multiply back when computing the mean.
    GRAD_SCALE = 256.0

    t0 = time.time()
    for batch_idx, encoded in enumerate(batches):
        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded["attention_mask"].to(device)
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100

        model.zero_grad()
        loss = model(
            input_ids=input_ids, attention_mask=attention_mask, labels=labels
        ).loss
        # Scale down to keep gradients in fp16 range
        scaled_loss = loss / GRAD_SCALE
        scaled_loss.backward()

        for name, param in target_params.items():
            if param.grad is not None:
                g = param.grad.float().cpu()
                # Skip if still NaN/Inf despite scaling (shouldn't happen)
                if torch.isnan(g).any() or torch.isinf(g).any():
                    continue
                accum[name].add_(g.abs())
                valid_counts[name] += 1

        model.zero_grad(set_to_none=True)

        if (batch_idx + 1) % 10 == 0 or batch_idx == 0:
            elapsed = time.time() - t0
            rate = (batch_idx + 1) / elapsed
            remaining = (n_batches - batch_idx - 1) / rate
            log(
                f"    Batch {batch_idx + 1}/{n_batches}  "
                f"({elapsed:.0f}s elapsed, ~{remaining:.0f}s remaining)"
            )

        # Periodic cleanup
        if (batch_idx + 1) % 10 == 0:
            gc.collect()
            if device == "mps":
                torch.mps.empty_cache()

    # Compute mean |grad| per weight, undoing the loss scaling
    grad_maps: dict[str, torch.Tensor] = {}
    for name in accum:
        n_valid = valid_counts[name]
        if n_valid > 0:
            # Multiply back by GRAD_SCALE to get true gradient magnitudes
            grad_maps[name] = (accum[name] * GRAD_SCALE) / n_valid
        else:
            log(f"  WARNING: {name} had 0 valid batches (all NaN/Inf)")
            grad_maps[name] = torch.zeros_like(accum[name])

    elapsed = time.time() - t0
    log(f"\n  Gradient collection complete: {elapsed:.1f}s for {n_batches} batches")

    # Summary stats
    for name in sorted(grad_maps.keys()):
        g = grad_maps[name]
        near_zero_pct = (g < g.median() * 0.01).float().mean().item() * 100
        log(
            f"    {name:<55} mean|∇|={g.mean():.6f}  "
            f"near-zero(<1%median)={near_zero_pct:.1f}%"
        )

    return grad_maps


# ═══════════════════════════════════════════════════════════════════════
# Phase 2: Mask Construction
# ═══════════════════════════════════════════════════════════════════════


def build_masks(
    model, grad_maps: dict[str, torch.Tensor], zero_rate: float = 0.50
) -> dict[str, dict[str, torch.Tensor]]:
    """Build three mask strategies from weight magnitudes and gradient maps.

    Each mask is a boolean tensor: True = KEEP (antinode), False = ZERO (node).
    All masks enforce the same zero_rate per row for fair comparison.

    Returns:
        {"magnitude": {name: mask}, "gradient": {name: mask}, "node": {name: mask}}
    """
    log(f"\n{'═' * 78}")
    log(f"  PHASE 2: BUILDING THREE MASKS  (zero_rate={zero_rate:.0%})")
    log(f"{'═' * 78}")

    masks = {"magnitude": {}, "gradient": {}, "node": {}}

    # Collect overlap statistics
    overlaps = []

    for name, param in model.named_parameters():
        if name not in grad_maps:
            continue

        W = param.data.detach().float().cpu()
        G = grad_maps[name]

        # ── Mask 1: MAGNITUDE — zero the smallest |W| per row ──
        abs_W = W.abs()
        mag_thresh = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
        mask_mag = abs_W >= mag_thresh

        # ── Mask 2: GRADIENT (DVD) — zero the smallest mean|∇W| per row ──
        grad_thresh = torch.quantile(G, zero_rate, dim=1, keepdim=True)
        mask_grad = G >= grad_thresh

        # ── Mask 3: NODE — zero positions where BOTH are below median ──
        # Use per-row medians for each signal, then intersect the "small" sets
        abs_W_median = torch.quantile(abs_W, 0.5, dim=1, keepdim=True)
        G_median = torch.quantile(G, 0.5, dim=1, keepdim=True)

        # "Small in both" = node candidate
        both_small = (abs_W < abs_W_median) & (G < G_median)
        # We want exactly zero_rate zeros per row. The "node" mask zeros
        # the both-small positions first, then fills remaining quota from
        # a combined score (|W| * |∇W|) to reach exact zero_rate.
        combined_score = abs_W * G
        # Per-row: rank by combined score, zero the bottom zero_rate fraction
        # BUT prioritize positions that are both-small
        # Strategy: set combined_score to -inf where both_small, then take
        # bottom zero_rate by rank
        node_score = combined_score.clone()
        node_score[both_small] = -1.0  # ensure these are zeroed first
        node_thresh = torch.quantile(node_score, zero_rate, dim=1, keepdim=True)
        mask_node = node_score >= node_thresh

        masks["magnitude"][name] = mask_mag
        masks["gradient"][name] = mask_grad
        masks["node"][name] = mask_node

        # Overlap statistics
        total = mask_mag.numel()
        agree = ((mask_mag == mask_grad).float().mean().item()) * 100
        mag_only = ((mask_mag & ~mask_grad).float().mean().item()) * 100
        grad_only = ((~mask_mag & mask_grad).float().mean().item()) * 100

        layer_str = name.split(".")[2] if "layers" in name else "?"
        module_str = name.split(".")[-2] if "." in name else name
        overlaps.append((layer_str, module_str, agree, mag_only, grad_only))

    # Print overlap summary
    log(f"\n  Mask overlap (magnitude vs gradient):")
    log(f"  {'Layer':>5} {'Module':<12} {'Agree%':>7} {'Mag-only%':>10} {'Grad-only%':>11}")
    log(f"  {'─' * 5} {'─' * 12} {'─' * 7} {'─' * 10} {'─' * 11}")

    # Aggregate by layer
    layer_stats = defaultdict(lambda: {"agree": [], "mag_only": [], "grad_only": []})
    for layer, module, agree, mag_only, grad_only in overlaps:
        layer_stats[layer]["agree"].append(agree)
        layer_stats[layer]["mag_only"].append(mag_only)
        layer_stats[layer]["grad_only"].append(grad_only)

    for layer in sorted(layer_stats.keys(), key=lambda x: int(x) if x.isdigit() else 999):
        s = layer_stats[layer]
        log(
            f"  {layer:>5} {'(all)':.<12} "
            f"{np.mean(s['agree']):>6.1f}% "
            f"{np.mean(s['mag_only']):>9.1f}% "
            f"{np.mean(s['grad_only']):>10.1f}%"
        )

    # Global summary
    all_agree = [o[2] for o in overlaps]
    log(f"\n  Global mean overlap: {np.mean(all_agree):.1f}% agreement")
    log(f"  If ~50% → masks are independent (orthogonal signals)")
    log(f"  If ~90% → masks are redundant (same information)")

    return masks


# ═══════════════════════════════════════════════════════════════════════
# Phase 3: Ternarization + Compounding Measurement
# ═══════════════════════════════════════════════════════════════════════


class TernaryLinear(nn.Module):
    """Drop-in ternary Linear. Reused from full_ternarize.py."""

    def __init__(self, T: torch.Tensor, gamma: torch.Tensor,
                 bias: torch.Tensor | None = None):
        super().__init__()
        self.register_buffer("T", T.to(torch.int8))
        self.register_buffer("gamma", gamma.to(torch.float32))
        if bias is not None:
            self.register_buffer("bias", bias.to(torch.float32))
        else:
            self.bias = None
        self.out_features = T.shape[0]
        self.in_features = T.shape[1]

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        T_cast = self.T.to(device=x.device, dtype=x.dtype)
        out = F.linear(x, T_cast)
        gamma = self.gamma.to(device=x.device, dtype=x.dtype)
        out = out * gamma
        if self.bias is not None:
            out = out + self.bias.to(device=x.device, dtype=x.dtype)
        return out


def ternarize_weight_with_mask(
    W: torch.Tensor, mask: torch.Tensor
) -> tuple[torch.Tensor, torch.Tensor]:
    """Ternarize using a pre-computed mask.

    Args:
        W: float weight matrix (out_features, in_features)
        mask: boolean tensor, True = keep, False = zero

    Returns:
        T: int8 ternary {-1, 0, +1}
        gamma: float32 per-row scale
    """
    W_float = W.detach().float().cpu()
    T = torch.where(mask, torch.sign(W_float), torch.zeros_like(W_float))
    # Optimal per-row gamma: γ_i = (w_i · t_i) / (t_i · t_i)
    wt = (W_float * T).sum(dim=1)
    tt = (T * T).sum(dim=1)
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))
    return T.to(torch.int8), gamma


def compute_weight_cosine(W: torch.Tensor, T: torch.Tensor,
                          gamma: torch.Tensor) -> float:
    """Cosine similarity between original weight and ternary reconstruction."""
    W_float = W.detach().float().cpu()
    W_recon = gamma.unsqueeze(1) * T.float()
    return F.cosine_similarity(
        W_float.reshape(1, -1), W_recon.reshape(1, -1)
    ).item()


def get_model_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError("Cannot find layers")


def ternarize_layer_with_mask(
    layer: nn.Module,
    layer_idx: int,
    masks: dict[str, torch.Tensor],
    device: str,
) -> dict[str, float]:
    """Ternarize one layer using pre-built masks. Returns per-module cosines."""
    cosines = {}

    for name in TARGET_MODULES_FFN:
        proj = getattr(layer.mlp, name, None)
        if proj is None:
            continue
        param_name = f"model.layers.{layer_idx}.mlp.{name}.weight"
        if param_name not in masks:
            continue

        W = proj.weight
        mask = masks[param_name]
        T, gamma = ternarize_weight_with_mask(W, mask)
        cos = compute_weight_cosine(W, T, gamma)
        cosines[name] = cos

        bias = proj.bias.detach().float().cpu() if proj.bias is not None else None
        tl = TernaryLinear(T, gamma, bias).to(device)
        setattr(layer.mlp, name, tl)
        del proj
        gc.collect()

    for name in TARGET_MODULES_ATTN:
        proj = getattr(layer.self_attn, name, None)
        if proj is None:
            continue
        param_name = f"model.layers.{layer_idx}.self_attn.{name}.weight"
        if param_name not in masks:
            continue

        W = proj.weight
        mask = masks[param_name]
        T, gamma = ternarize_weight_with_mask(W, mask)
        cos = compute_weight_cosine(W, T, gamma)
        cosines[name] = cos

        bias = proj.bias.detach().float().cpu() if proj.bias is not None else None
        tl = TernaryLinear(T, gamma, bias).to(device)
        setattr(layer.self_attn, name, tl)
        del proj
        gc.collect()

    return cosines


# ═══════════════════════════════════════════════════════════════════════
# Phase 3a: Cumulative compounding sweep via hidden state comparison
# ═══════════════════════════════════════════════════════════════════════


@torch.no_grad()
def collect_float_hidden_states(
    model, tokenizer, probe_texts: list[str], device: str
) -> list[torch.Tensor]:
    """Run float model on probe texts, collect hidden states after each layer.

    Returns list of tensors [n_layers+1], each (total_tokens, hidden_dim).
    Index 0 = post-embedding, index L = after layer L-1.
    """
    # Tokenize all probe texts together
    encoded = tokenizer(
        probe_texts,
        return_tensors="pt",
        padding=True,
        truncation=True,
        max_length=128,
    ).to(device)

    # Forward pass with output_hidden_states
    outputs = model(
        input_ids=encoded["input_ids"],
        attention_mask=encoded["attention_mask"],
        output_hidden_states=True,
    )

    # hidden_states is tuple of (n_layers+1) tensors, each (batch, seq, hidden)
    # Flatten batch×seq → total_tokens, move to CPU
    mask = encoded["attention_mask"].bool()
    hidden_states = []
    for hs in outputs.hidden_states:
        # Only keep non-padding tokens
        flat = hs[mask].float().cpu()
        hidden_states.append(flat)

    return hidden_states


@torch.no_grad()
def measure_compounding(
    model,
    tokenizer,
    masks_dict: dict[str, dict[str, torch.Tensor]],
    device: str,
    probe_texts: list[str] | None = None,
) -> dict[str, list[dict]]:
    """Measure compounding curves for all three mask strategies.

    For each mask strategy:
      1. Load fresh float model
      2. Collect float hidden states (reference)
      3. Progressively ternarize layers 0→35
      4. At each depth L, forward pass and compare hidden states at layer L

    This is expensive but gives the definitive compounding comparison.
    Returns {mask_name: [{depth, cosine, weight_cos_mean}, ...]}.
    """
    if probe_texts is None:
        probe_texts = [
            "The capital of France is Paris, located along the Seine river.",
            "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
            "(λx. λy. x y) (λz. z) reduces to (λy. y) which is the identity combinator I.",
            "Quantum entanglement occurs when two particles become correlated.",
            "The derivative of sin(x) is cos(x), a fundamental result in calculus.",
            "Once upon a time in a small village there lived an old clockmaker.",
            "SELECT name, age FROM users WHERE age > 18 ORDER BY name;",
            "日本の首都は東京で、世界最大の都市圏の一つです。",
        ]

    results = {}

    for mask_name in ["magnitude", "gradient", "node"]:
        log(f"\n{'═' * 78}")
        log(f"  COMPOUNDING SWEEP: {mask_name.upper()} MASK")
        log(f"{'═' * 78}")

        mask_set = masks_dict[mask_name]

        # We need to reload the model fresh for each mask strategy
        # But that's very expensive. Instead, we use a hook-based approach:
        # keep the float model, but intercept each layer's output and compare
        # against what a ternarized version would produce.
        #
        # Actually, the cleanest approach: ternarize in-place progressively,
        # collecting hidden states at each depth. We reload the model once
        # per mask strategy.

        log(f"  Loading fresh model for {mask_name} sweep...")
        from transformers import AutoModelForCausalLM, AutoTokenizer

        fresh_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-8B",
            torch_dtype=torch.float16,
            device_map=device,
        )
        fresh_model.eval()

        # Collect float reference hidden states FIRST
        log(f"  Collecting float reference hidden states...")
        float_hidden = collect_float_hidden_states(
            fresh_model, tokenizer, probe_texts, device
        )
        n_layers = len(float_hidden) - 1  # subtract embedding
        log(f"  Reference: {n_layers} layers, {float_hidden[0].shape[0]} tokens")

        # Progressive ternarization
        layers = get_model_layers(fresh_model)
        sweep = []

        for depth in range(n_layers):
            # Ternarize layer `depth`
            layer_cosines = ternarize_layer_with_mask(
                layers[depth], depth, mask_set, device
            )
            mean_wcos = np.mean(list(layer_cosines.values())) if layer_cosines else 0

            # Forward pass to get hidden states at this depth
            encoded = tokenizer(
                probe_texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=128,
            ).to(device)

            outputs = fresh_model(
                input_ids=encoded["input_ids"],
                attention_mask=encoded["attention_mask"],
                output_hidden_states=True,
            )

            mask_tokens = encoded["attention_mask"].bool()
            # Compare hidden state at layer depth+1 (after ternarized layer)
            hs_ternary = outputs.hidden_states[depth + 1][mask_tokens].float().cpu()
            hs_float = float_hidden[depth + 1]

            # Cosine similarity per token, then mean
            cos_per_token = F.cosine_similarity(hs_ternary, hs_float, dim=1)
            mean_cos = cos_per_token.mean().item()
            min_cos = cos_per_token.min().item()

            sweep.append({
                "depth": depth,
                "cumulative_cosine": mean_cos,
                "cumulative_cosine_min": min_cos,
                "weight_cosine_mean": mean_wcos,
                "per_module": layer_cosines,
            })

            log(
                f"  L{depth:>2}: hidden_cos={mean_cos:.6f}  "
                f"min={min_cos:.6f}  weight_cos={mean_wcos:.4f}"
            )

            gc.collect()
            if device == "mps":
                torch.mps.empty_cache()

        results[mask_name] = sweep

        # Cleanup
        del fresh_model
        gc.collect()
        if device == "mps":
            torch.mps.empty_cache()

    return results


# ═══════════════════════════════════════════════════════════════════════
# Phase 4: Full-model PPL comparison
# ═══════════════════════════════════════════════════════════════════════


def load_eval_texts() -> list[str]:
    """Load evaluation texts for PPL."""
    try:
        from datasets import load_dataset
        ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
        texts = [t for t in ds["text"] if t.strip()]
        log(f"  Loaded WikiText-2 test: {len(texts)} lines")
        return texts
    except Exception as e:
        log(f"  WikiText-2 unavailable ({e}), using built-in corpus")
        return CALIBRATION_TEXTS[:20]


@torch.no_grad()
def evaluate_perplexity(
    model, tokenizer, texts: list[str],
    max_length: int = 512, stride: int = 256,
    max_eval_tokens: int = 16384, device: str = "mps",
) -> dict:
    """Sliding-window PPL evaluation. Reused from full_ternarize.py."""
    log(f"  Evaluating PPL (max_length={max_length}, stride={stride})...")
    t0 = time.time()

    full_text = "\n\n".join(texts)
    encodings = tokenizer(full_text, return_tensors="pt", truncation=False)
    input_ids = encodings.input_ids[0]
    seq_len = input_ids.size(0)

    if max_eval_tokens > 0 and seq_len > max_eval_tokens:
        input_ids = input_ids[:max_eval_tokens]
        seq_len = max_eval_tokens
    log(f"  Tokens: {seq_len:,}")

    nlls = []
    n_tokens = 0

    for begin_loc in range(0, seq_len - 1, stride):
        end_loc = min(begin_loc + max_length, seq_len)
        score_begin = stride if begin_loc > 0 else 0

        input_chunk = input_ids[begin_loc:end_loc].unsqueeze(0).to(device)
        outputs = model(input_chunk)
        logits = outputs.logits

        shift_logits = logits[0, score_begin:-1, :].contiguous()
        shift_labels = input_chunk[0, score_begin + 1 :].contiguous()

        loss = F.cross_entropy(shift_logits, shift_labels, reduction="sum")
        nlls.append(loss.float().cpu().item())
        n_tokens += shift_labels.size(0)

        if end_loc >= seq_len:
            break

    mean_nll = sum(nlls) / n_tokens
    ppl = math.exp(mean_nll)
    elapsed = time.time() - t0

    log(f"  PPL: {ppl:.2f}  (NLL: {mean_nll:.4f}, {n_tokens:,} tokens, {elapsed:.1f}s)")
    return {"perplexity": ppl, "nll": mean_nll, "n_tokens": n_tokens}


def full_model_ppl_comparison(
    tokenizer,
    masks_dict: dict[str, dict[str, torch.Tensor]],
    device: str,
) -> dict[str, dict]:
    """Ternarize full model with each mask, measure PPL."""
    eval_texts = load_eval_texts()
    results = {}

    for mask_name in ["magnitude", "gradient", "node"]:
        log(f"\n{'═' * 78}")
        log(f"  FULL-MODEL PPL: {mask_name.upper()} MASK")
        log(f"{'═' * 78}")

        from transformers import AutoModelForCausalLM

        fresh_model = AutoModelForCausalLM.from_pretrained(
            "Qwen/Qwen3-8B",
            torch_dtype=torch.float16,
            device_map=device,
        )
        fresh_model.eval()

        mask_set = masks_dict[mask_name]
        layers = get_model_layers(fresh_model)
        n_layers = len(layers)

        # Ternarize all layers
        all_cosines = []
        for i in range(n_layers):
            layer_cos = ternarize_layer_with_mask(layers[i], i, mask_set, device)
            mean_cos = np.mean(list(layer_cos.values())) if layer_cos else 0
            all_cosines.append(mean_cos)

        log(f"  Mean weight cosine: {np.mean(all_cosines):.5f}")

        ppl_result = evaluate_perplexity(
            fresh_model, tokenizer, eval_texts, device=device
        )
        results[mask_name] = {
            "ppl": ppl_result["perplexity"],
            "nll": ppl_result["nll"],
            "mean_weight_cosine": float(np.mean(all_cosines)),
        }

        del fresh_model
        gc.collect()
        if device == "mps":
            torch.mps.empty_cache()

    return results


# ═══════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="DVD Stamp Test")
    parser.add_argument("--model", default="Qwen/Qwen3-8B")
    parser.add_argument("--device", default="mps")
    parser.add_argument("--n-batches", type=int, default=50,
                        help="Calibration batches for gradient collection")
    parser.add_argument("--zero-rate", type=float, default=0.50,
                        help="Fraction of weights to zero per row")
    parser.add_argument("--skip-compounding", action="store_true",
                        help="Skip compounding sweep (expensive, 3 model loads)")
    parser.add_argument("--skip-ppl", action="store_true",
                        help="Skip full-model PPL (expensive, 3 model loads)")
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  DVD STAMP TEST — Does Gradient Topology Compound Less?{' ' * 20}║")
    log(f"║  Model: {args.model:<67}║")
    log(f"║  Device: {args.device:<66}║")
    log(f"║  Zero rate: {args.zero_rate:<63.0%}║")
    log(f"║  Calibration batches: {args.n_batches:<53}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()

    # ── Load model + tokenizer ──
    log(f"\n  Loading model...")
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(args.model, padding_side="left")
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        torch_dtype=torch.float16,
        device_map=args.device,
    )
    model.eval()

    # ── Phase 1: Collect gradient DVD ──
    grad_maps = collect_gradient_maps(
        model, tokenizer, args.device, n_batches=args.n_batches
    )

    # Save gradient maps for reuse
    log(f"\n  Saving gradient maps...")
    grad_save = {}
    for name, g in grad_maps.items():
        grad_save[name] = g.half()  # save as float16 to reduce disk
    torch.save(grad_save, RESULTS_DIR / "gradient_maps.pt")
    log(f"  Saved to {RESULTS_DIR / 'gradient_maps.pt'}")

    # ── Phase 2: Build masks ──
    masks_dict = build_masks(model, grad_maps, zero_rate=args.zero_rate)

    # Free gradient maps — we have the masks now
    del grad_maps
    gc.collect()

    # ── Quick per-layer weight cosine comparison (no model reload needed) ──
    log(f"\n{'═' * 78}")
    log(f"  PER-LAYER WEIGHT COSINE COMPARISON")
    log(f"{'═' * 78}")
    log(f"  {'Layer':>5}  {'Magnitude':>10} {'Gradient':>10} {'Node':>10}  {'Winner':>8}")
    log(f"  {'─' * 5}  {'─' * 10} {'─' * 10} {'─' * 10}  {'─' * 8}")

    cosine_summary = {"magnitude": [], "gradient": [], "node": []}
    layers = get_model_layers(model)
    n_layers = len(layers)

    for layer_idx in range(n_layers):
        cos_per_mask = {}
        for mask_name in ["magnitude", "gradient", "node"]:
            mask_set = masks_dict[mask_name]
            layer_cosines = []
            for mod_name in TARGET_MODULES:
                if mod_name in TARGET_MODULES_FFN:
                    param_name = f"model.layers.{layer_idx}.mlp.{mod_name}.weight"
                    proj = getattr(layers[layer_idx].mlp, mod_name, None)
                else:
                    param_name = f"model.layers.{layer_idx}.self_attn.{mod_name}.weight"
                    proj = getattr(layers[layer_idx].self_attn, mod_name, None)

                if proj is None or param_name not in mask_set:
                    continue

                W = proj.weight
                mask = mask_set[param_name]
                T, gamma = ternarize_weight_with_mask(W, mask)
                cos = compute_weight_cosine(W, T, gamma)
                layer_cosines.append(cos)

            mean_cos = np.mean(layer_cosines) if layer_cosines else 0
            cos_per_mask[mask_name] = mean_cos
            cosine_summary[mask_name].append(mean_cos)

        winner = max(cos_per_mask, key=cos_per_mask.get)
        log(
            f"  {layer_idx:>5}  "
            f"{cos_per_mask['magnitude']:>10.6f} "
            f"{cos_per_mask['gradient']:>10.6f} "
            f"{cos_per_mask['node']:>10.6f}  "
            f"{'← ' + winner if cos_per_mask[winner] > min(cos_per_mask.values()) + 0.001 else 'tie':>8}"
        )

    log(f"\n  Summary (mean across all layers):")
    for mask_name in ["magnitude", "gradient", "node"]:
        vals = cosine_summary[mask_name]
        log(
            f"    {mask_name:<12} mean={np.mean(vals):.6f}  "
            f"min={np.min(vals):.6f}  max={np.max(vals):.6f}"
        )

    # Free the original model before compounding sweep (we reload fresh copies)
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # ── Phase 3: Compounding sweep ──
    if not args.skip_compounding:
        compounding = measure_compounding(
            None, tokenizer, masks_dict, args.device
        )

        # Save compounding results
        with open(RESULTS_DIR / "compounding.json", "w") as f:
            json.dump(compounding, f, indent=2)

        # Print comparison
        log(f"\n{'═' * 78}")
        log(f"  COMPOUNDING COMPARISON — Cumulative Hidden-State Cosine")
        log(f"{'═' * 78}")
        log(
            f"  {'Depth':>5}  {'Magnitude':>10} {'Gradient':>10} {'Node':>10}  "
            f"{'Grad-Mag':>9}"
        )
        log(
            f"  {'─' * 5}  {'─' * 10} {'─' * 10} {'─' * 10}  {'─' * 9}"
        )

        n = len(compounding["magnitude"])
        for i in range(n):
            mag_cos = compounding["magnitude"][i]["cumulative_cosine"]
            grad_cos = compounding["gradient"][i]["cumulative_cosine"]
            node_cos = compounding["node"][i]["cumulative_cosine"]
            delta = grad_cos - mag_cos
            log(
                f"  {i:>5}  {mag_cos:>10.6f} {grad_cos:>10.6f} "
                f"{node_cos:>10.6f}  {delta:>+9.6f}"
            )

        # Final comparison
        mag_final = compounding["magnitude"][-1]["cumulative_cosine"]
        grad_final = compounding["gradient"][-1]["cumulative_cosine"]
        node_final = compounding["node"][-1]["cumulative_cosine"]
        log(f"\n  FINAL DEPTH (layer {n-1}):")
        log(f"    Magnitude: {mag_final:.6f}")
        log(f"    Gradient:  {grad_final:.6f}  (Δ = {grad_final - mag_final:+.6f})")
        log(f"    Node:      {node_final:.6f}  (Δ = {node_final - mag_final:+.6f})")
        if grad_final > mag_final:
            log(f"  ✅ DVD HYPOTHESIS SUPPORTED — gradient topology compounds less!")
        else:
            log(f"  ❌ DVD hypothesis not supported — magnitude still wins")
    else:
        log("\n  [Skipping compounding sweep]")
        compounding = None

    # ── Phase 4: Full-model PPL ──
    if not args.skip_ppl:
        ppl_results = full_model_ppl_comparison(tokenizer, masks_dict, args.device)

        log(f"\n{'═' * 78}")
        log(f"  FULL-MODEL PERPLEXITY COMPARISON")
        log(f"{'═' * 78}")
        for mask_name in ["magnitude", "gradient", "node"]:
            r = ppl_results[mask_name]
            log(
                f"    {mask_name:<12} PPL={r['ppl']:>12.2f}  "
                f"NLL={r['nll']:.4f}  weight_cos={r['mean_weight_cosine']:.5f}"
            )
    else:
        log("\n  [Skipping PPL evaluation]")
        ppl_results = None

    # ── Save all results ──
    all_results = {
        "config": {
            "model": args.model,
            "device": args.device,
            "n_batches": args.n_batches,
            "zero_rate": args.zero_rate,
        },
        "weight_cosines": cosine_summary,
        "compounding": compounding,
        "ppl": ppl_results,
        "elapsed_total": time.time() - t_start,
    }

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results saved to {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
