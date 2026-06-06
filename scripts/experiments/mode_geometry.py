#!/usr/bin/env python3
"""Mode Geometry — why are 9 modes enough at L15 but not L23?

Session 196 confidence gate showed: at L23-L26 the classifier is
98-100% accurate (correct mode) but ternary output is 1.07-1.13x
PPL (wrong program). The modes exist — but the fixed ternary
vector per mode is too coarse.

Three hypotheses:
  H1: Ternary quantization kills direction (sign(centroid) loses
      critical angular info that matters more at L23-L26)
  H2: Within-cluster variance is higher (modes are "fuzzier")
  H3: The computation lives in a rotated subspace — projecting
      into the natural basis first would tighten the clusters

Experiments:
  1. FLOAT vs TERNARY centroids: is error in quantization or structure?
     Replace ternary_signs * gamma with float16 centroid → measure PPL
     If float centroids fix it: the 9-mode structure IS correct,
     just needs better representation per mode.

  2. WITHIN-CLUSTER VARIANCE: how tight are the clusters?
     For each layer, measure cosine similarity between each sample
     and its cluster centroid. Tight clusters → good approximation.

  3. CROSS-LAYER MODE ROTATION: are L23 modes a rotation of L15?
     Compute the optimal orthogonal transform between the two sets
     of centroids. If R exists with low residual → same 9 programs,
     different basis.

  4. MORE MODES: does 27 or 81 fix it without going to 512?
     512 modes at L0 was catastrophic (s195). But L23-L26 might
     have a sweet spot between 9 and 512.

  5. PER-MODE LOW-RANK: instead of constant output, each mode gets
     a small rank-r matrix: output = A_mode @ (B_mode @ input).
     This is a "mixture of linear experts" — 9 tiny MLPs.

Usage:
  uv run python scripts/experiments/mode_geometry.py \
    --model Qwen/Qwen3-8B --device mps

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
from sklearn.cluster import MiniBatchKMeans
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

from verbum.probes.library import crystal_probes


# ══════════════════════════════════════════════════════════════
# Texts
# ══════════════════════════════════════════════════════════════

CALIBRATION_TEXTS = [
    "The theory of general relativity describes gravity as"
    " the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into"
    " glucose and oxygen.",
    "DNA carries genetic information in a double helix"
    " structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles"
    " at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion"
    " neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under"
    " their own gravitational force.",
    "She walked through the ancient forest, her footsteps"
    " muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the"
    " fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow"
    " while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling"
    " with anticipation.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder.",
    "To solve this equation, first isolate the variable"
    " on one side.",
    "Install the software by running the setup wizard and"
    " following the prompts.",
    "The committee voted unanimously to approve the new"
    " environmental regulations.",
    "Democracy originated in ancient Greece, specifically"
    " in the city-state of Athens.",
    "The function takes two arguments and returns their"
    " composition as a new callable.",
    "Machine learning algorithms can be categorized as"
    " supervised or unsupervised.",
    "Arrays are contiguous blocks of memory that allow"
    " constant-time access by index.",
    "What time does the store close today?",
    "I think we should probably leave now before it gets"
    " too dark outside.",
    "The book that the professor recommended, which had"
    " been out of print for decades, was finally reissued.",
    "Although the experiment failed initially, the"
    " researchers persisted and eventually found"
    " the solution.",
    "The primary colors are red, blue, and yellow.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5,"
    " 8, 13, 21.",
    "Pi is approximately equal to 3.14159265 and is an"
    " irrational number.",
    "The periodic table organizes elements by atomic"
    " number and electron configuration.",
    "Enzymes are biological catalysts that speed up"
    " chemical reactions in living organisms.",
    "The ship sailed slowly into the harbor as the storm"
    " clouds gathered on the horizon.",
    "The detective examined the crime scene, noting every"
    " detail with practiced precision.",
    "Birds sang in the treetops as morning light filtered"
    " through the canopy above.",
    "The Supreme Court ruled that the legislation was"
    " constitutional.",
]

EVAL_TEXTS = [
    "The theory of general relativity describes gravity"
    " as the curvature of spacetime caused by mass and"
    " energy.",
    "In a large mixing bowl, combine the flour, sugar,"
    " and baking powder. Make a well in the center.",
    "The committee voted unanimously to approve the new"
    " environmental regulations for manufacturing plants.",
    "She walked through the ancient forest, her footsteps"
    " muffled by centuries of fallen leaves.",
    "The function takes two arguments and returns their"
    " composition as a new callable object.",
    "During the Cambrian explosion, roughly 541 million"
    " years ago, most major animal phyla appeared.",
    "The patient was admitted with acute respiratory"
    " distress. Initial blood work showed elevated levels.",
    "To solve this equation, first isolate the variable"
    " on one side by subtracting three from both sides.",
]

FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]


def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl(model, tokenizer, texts, device):
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=256,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        with torch.no_grad():
            out = model(**enc, labels=labels)
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(
            **enc, max_new_tokens=max_new,
            do_sample=False, temperature=1.0,
            pad_token_id=tokenizer.pad_token_id,
        )
    return tokenizer.decode(
        out[0][enc["input_ids"].shape[1]:],
        skip_special_tokens=True,
    )


def measure_facts(model, tokenizer, device):
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Data collection
# ══════════════════════════════════════════════════════════════

def collect_mlp_data(model, tokenizer, layer_idx, device,
                     texts, n_crystal=100):
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    captured = {}

    def pre_hook(module, inp):
        x = inp[0] if isinstance(inp, tuple) else inp
        captured["input"] = x.detach().float()

    def post_hook(module, inp, out):
        captured["output"] = out.detach().float()

    h1 = mlp.register_forward_pre_hook(pre_hook)
    h2 = mlp.register_forward_hook(post_hook)

    all_prompts = list(texts)
    probes = crystal_probes()
    all_prompts.extend([p.prompt for p in probes[:n_crystal]])

    all_in, all_out = [], []
    for prompt in all_prompts:
        captured.clear()
        enc = tokenizer(
            prompt, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        with torch.no_grad():
            model(**enc)
        if "input" in captured and "output" in captured:
            inp = captured["input"][0].cpu().numpy()
            out = captured["output"][0].cpu().numpy()
            if len(inp) > 32:
                idx = np.linspace(0, len(inp) - 1, 32, dtype=int)
                inp, out = inp[idx], out[idx]
            all_in.append(inp)
            all_out.append(out)

    h1.remove()
    h2.remove()
    return (
        np.concatenate(all_in, axis=0),
        np.concatenate(all_out, axis=0),
    )


def train_classifier(inputs, labels, n_modes,
                     n_epochs=100, lr=0.01):
    d = inputs.shape[1]
    X = torch.tensor(inputs, dtype=torch.float32)
    Y = torch.tensor(labels, dtype=torch.long)
    W = torch.randn(n_modes, d) * 0.01
    W.requires_grad_(True)
    opt = torch.optim.Adam([W], lr=lr)
    best_acc, best_W = 0.0, None
    for _ in range(n_epochs):
        logits = X @ W.T
        loss = F.cross_entropy(logits, Y)
        opt.zero_grad()
        loss.backward()
        opt.step()
        with torch.no_grad():
            acc = float((logits.argmax(-1) == Y).float().mean())
            if acc > best_acc:
                best_acc = acc
                best_W = W.detach().clone()
    return best_W.numpy(), best_acc


# ══════════════════════════════════════════════════════════════
# Replacement modules
# ══════════════════════════════════════════════════════════════

class TernaryFFN(torch.nn.Module):
    """Standard: output = ternary_signs[mode] * gamma[mode]"""
    def __init__(self, cls_w, ternary_signs, gamma):
        super().__init__()
        self.register_buffer("classifier",
                             torch.tensor(cls_w, dtype=torch.float32))
        self.register_buffer("ternary",
                             torch.tensor(ternary_signs, dtype=torch.float32))
        self.register_buffer("gamma",
                             torch.tensor(gamma, dtype=torch.float32))

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = (xf @ self.classifier.T).clamp(-20, 20)
        mode = logits.argmax(dim=-1)
        out = self.ternary[mode] * self.gamma[mode]
        return out.to(x.dtype).reshape(shape)


class FloatCentroidFFN(torch.nn.Module):
    """Float centroids: output = centroid[mode] (no ternary quantization)"""
    def __init__(self, cls_w, centroids):
        super().__init__()
        self.register_buffer("classifier",
                             torch.tensor(cls_w, dtype=torch.float32))
        self.register_buffer("centroids",
                             torch.tensor(centroids, dtype=torch.float32))

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = (xf @ self.classifier.T).clamp(-20, 20)
        mode = logits.argmax(dim=-1)
        out = self.centroids[mode]
        return out.to(x.dtype).reshape(shape)


class PerModeLowRankFFN(torch.nn.Module):
    """Per-mode low-rank: output = centroid[mode] + A[mode] @ (B[mode] @ x)
    Each mode gets a rank-r correction that's input-dependent."""
    def __init__(self, cls_w, centroids, A_modes, B_modes):
        super().__init__()
        self.register_buffer("classifier",
                             torch.tensor(cls_w, dtype=torch.float32))
        self.register_buffer("centroids",
                             torch.tensor(centroids, dtype=torch.float32))
        # A_modes: (n_modes, d_model, rank)
        # B_modes: (n_modes, rank, d_model)
        self.register_buffer("A_modes",
                             torch.tensor(A_modes, dtype=torch.float32))
        self.register_buffer("B_modes",
                             torch.tensor(B_modes, dtype=torch.float32))

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = (xf @ self.classifier.T).clamp(-20, 20)
        mode = logits.argmax(dim=-1)

        # Base: centroid lookup
        out = self.centroids[mode]

        # Per-mode low-rank correction: out += A[mode] @ (B[mode] @ x)
        # For efficiency, process per mode
        for m in range(self.centroids.shape[0]):
            mask = (mode == m)
            if not mask.any():
                continue
            x_m = xf[mask]  # (n_m, d_model)
            # B[m] @ x -> (n_m, rank), then A[m] @ that -> (n_m, d_model)
            proj = x_m @ self.B_modes[m].T  # (n_m, rank)
            correction = proj @ self.A_modes[m].T  # (n_m, d_model)
            out[mask] = out[mask] + correction

        return out.to(x.dtype).reshape(shape)


# ══════════════════════════════════════════════════════════════
# Build replacement for one layer
# ══════════════════════════════════════════════════════════════

def build_layer_data(model, tokenizer, layer_idx, device,
                     d_model, n_modes=9):
    """Collect data and cluster. Returns all pieces needed."""
    mlp_in, mlp_out = collect_mlp_data(
        model, tokenizer, layer_idx, device, CALIBRATION_TEXTS,
    )

    km = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(256, len(mlp_out)), n_init=5,
    )
    labels = km.fit_predict(mlp_out)

    # Centroids (float)
    centroids = np.zeros((n_modes, d_model))
    ternary_signs = np.zeros((n_modes, d_model))
    gamma = np.zeros((n_modes, d_model))

    for i in range(n_modes):
        mask = labels == i
        if mask.sum() == 0:
            continue
        c = mlp_out[mask].mean(axis=0)
        centroids[i] = c
        ternary_signs[i] = np.sign(c)
        gamma[i] = np.abs(c)

    cls_W, cls_acc = train_classifier(mlp_in, labels, n_modes)

    return {
        "mlp_in": mlp_in,
        "mlp_out": mlp_out,
        "labels": labels,
        "centroids": centroids,
        "ternary_signs": ternary_signs,
        "gamma": gamma,
        "cls_W": cls_W,
        "cls_acc": cls_acc,
        "n_modes": n_modes,
    }


def build_per_mode_lowrank(data, rank=8):
    """Build per-mode low-rank corrections from residuals."""
    n_modes = data["n_modes"]
    d_model = data["centroids"].shape[1]

    A_modes = np.zeros((n_modes, d_model, rank))
    B_modes = np.zeros((n_modes, rank, d_model))

    for m in range(n_modes):
        mask = data["labels"] == m
        if mask.sum() < rank + 1:
            continue

        # Residuals: actual output - centroid
        residuals = data["mlp_out"][mask] - data["centroids"][m]
        inputs_m = data["mlp_in"][mask]

        # Fit: residual ≈ inputs @ B.T @ A.T
        # Use SVD on the mapping inputs_m -> residuals
        # This is a rank-r approximation of the linear map
        # residuals = inputs_m @ W_residual, W_residual ≈ B.T @ A.T
        # So we need SVD of (inputs_m.T @ residuals) or similar

        # Simple approach: SVD of the residuals directly to find
        # the principal directions, then project inputs onto those
        U, S, Vt = np.linalg.svd(residuals, full_matrices=False)
        r = min(rank, len(S))

        # The principal output directions
        # A = top-r right singular vectors of residuals = Vt[:r]
        # B = how to get there from inputs: B = (pinv(inputs_m) @ U[:,:r] @ diag(S[:r]))
        # Simpler: just use the residual structure directly

        # Actually, we want: for each input x_i, correction = A @ B @ x_i
        # should approximate residual_i = output_i - centroid
        # This is a low-rank regression problem
        # W* = argmin ||residuals - inputs @ W||, then factor W = B.T @ A.T

        # Least squares: W = pinv(inputs) @ residuals
        # Then factor W with SVD
        try:
            W_map, _, _, _ = np.linalg.lstsq(inputs_m, residuals, rcond=None)
            # W_map: (d_model, d_model) — the full residual mapping
            # Factor to rank r
            Uw, Sw, Vwt = np.linalg.svd(W_map, full_matrices=False)
            sqrt_S = np.sqrt(Sw[:r])
            B_m = (Uw[:, :r] * sqrt_S).T  # (r, d_model) — input side
            A_m = (Vwt[:r, :] * sqrt_S[:, None])  # (r, d_model) — output side
            B_modes[m] = B_m
            A_modes[m] = A_m.T  # (d_model, r)
        except Exception:
            pass  # leave as zeros

    return A_modes, B_modes


# ══════════════════════════════════════════════════════════════
# Install hook + measure
# ══════════════════════════════════════════════════════════════

def install_and_measure(model, tokenizer, layer_idx, device,
                        replacement, baseline_ppl, label=""):
    """Install replacement, measure PPL, remove."""
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    def make_hook(repl):
        def hook_fn(module, inp, out):
            x = inp[0] if isinstance(inp, tuple) else inp
            return repl(x)
        return hook_fn

    h = mlp.register_forward_hook(make_hook(replacement))
    ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, device)
    ratio = ppl / baseline_ppl
    h.remove()

    marker = "★★" if ratio < 1.02 else (
        "★" if ratio < 1.05 else (
            "✓" if ratio < 1.10 else ""))

    log(f"    {label:>30s}: PPL={ppl:>8.2f} ({ratio:>5.2f}x) {marker}")
    return {"ppl": round(ppl, 4), "ratio": round(ratio, 4)}


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  MODE GEOMETRY — Why 9 modes work at L15 but not L23")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")

    # ── Load ──────────────────────────────────────────────
    dtype = (
        torch.float16
        if any(s in args.model for s in ["8B", "14B", "32B"])
        else torch.float32
    )
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
    )
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()

    d_model = model.config.hidden_size
    log(f"  d_model: {d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    baseline_ppl = measure_ppl(
        model, tokenizer, EVAL_TEXTS, args.device,
    )
    log(f"  Baseline PPL: {baseline_ppl:.2f}")

    # ── Target layers ─────────────────────────────────────
    target_layers = [15, 20, 22, 23, 24, 25, 26]

    # ══════════════════════════════════════════════════════
    # Collect data + cluster for all layers
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  COLLECTING DATA")
    log(f"{'═'*70}")

    all_data = {}
    for li in target_layers:
        log(f"  L{li}: collecting + clustering...")
        data = build_layer_data(
            model, tokenizer, li, args.device, d_model,
        )
        all_data[li] = data
        log(f"    {len(data['mlp_in'])} samples, cls_acc={data['cls_acc']:.1%}")

    # ══════════════════════════════════════════════════════
    # Exp 1: Ternary vs Float centroids
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 1: TERNARY vs FLOAT CENTROIDS (9 modes)")
    log("  Is the error in ternary quantization or 9-mode structure?")
    log(f"{'═'*70}")

    results_exp1 = {}
    for li in target_layers:
        data = all_data[li]
        log(f"\n  L{li}:")

        # Ternary
        ternary_repl = TernaryFFN(
            data["cls_W"], data["ternary_signs"], data["gamma"],
        ).to(args.device)
        r_ternary = install_and_measure(
            model, tokenizer, li, args.device,
            ternary_repl, baseline_ppl, "ternary (sign * |centroid|)",
        )

        # Float centroid
        float_repl = FloatCentroidFFN(
            data["cls_W"], data["centroids"],
        ).to(args.device)
        r_float = install_and_measure(
            model, tokenizer, li, args.device,
            float_repl, baseline_ppl, "float centroid",
        )

        results_exp1[str(li)] = {
            "ternary": r_ternary,
            "float_centroid": r_float,
            "delta": round(r_ternary["ratio"] - r_float["ratio"], 4),
        }

    # ══════════════════════════════════════════════════════
    # Exp 2: Within-cluster variance
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 2: WITHIN-CLUSTER VARIANCE")
    log("  How tight are the 9 clusters at each layer?")
    log(f"{'═'*70}")

    variance_results = {}
    for li in target_layers:
        data = all_data[li]
        cos_sims = []
        norm_ratios = []
        for m in range(data["n_modes"]):
            mask = data["labels"] == m
            if mask.sum() < 2:
                continue
            samples = data["mlp_out"][mask]
            centroid = data["centroids"][m]

            # Cosine similarity to centroid
            c_norm = centroid / (np.linalg.norm(centroid) + 1e-8)
            for s in samples:
                s_norm = s / (np.linalg.norm(s) + 1e-8)
                cos_sims.append(float(np.dot(c_norm, s_norm)))
                norm_ratios.append(
                    float(np.linalg.norm(s) / (np.linalg.norm(centroid) + 1e-8))
                )

        cos_arr = np.array(cos_sims)
        norm_arr = np.array(norm_ratios)
        variance_results[str(li)] = {
            "cos_mean": round(float(np.mean(cos_arr)), 4),
            "cos_std": round(float(np.std(cos_arr)), 4),
            "cos_p5": round(float(np.percentile(cos_arr, 5)), 4),
            "norm_mean": round(float(np.mean(norm_arr)), 4),
            "norm_std": round(float(np.std(norm_arr)), 4),
        }
        log(f"  L{li:>2d}: cos_to_centroid mean={np.mean(cos_arr):.4f}"
            f"  std={np.std(cos_arr):.4f}"
            f"  p5={np.percentile(cos_arr, 5):.4f}"
            f"  norm_ratio={np.mean(norm_arr):.3f}±{np.std(norm_arr):.3f}")

    # ══════════════════════════════════════════════════════
    # Exp 3: Cross-layer mode rotation
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 3: CROSS-LAYER MODE ROTATION")
    log("  Are L23 modes a rotation of L15 modes?")
    log(f"{'═'*70}")

    ref_layer = 15
    ref_centroids = all_data[ref_layer]["centroids"]
    # Normalize
    ref_norms = np.linalg.norm(ref_centroids, axis=1, keepdims=True)
    ref_normed = ref_centroids / (ref_norms + 1e-8)

    rotation_results = {}
    for li in target_layers:
        if li == ref_layer:
            continue
        target_centroids = all_data[li]["centroids"]
        target_norms = np.linalg.norm(target_centroids, axis=1, keepdims=True)
        target_normed = target_centroids / (target_norms + 1e-8)

        # Optimal orthogonal transform: R* = argmin ||target - R @ ref||
        # Solution via SVD of target.T @ ref
        M = target_normed.T @ ref_normed  # (d_model, d_model) but rank 9
        U, S, Vt = np.linalg.svd(M, full_matrices=False)
        # R = U @ Vt (Procrustes solution)
        R = U @ Vt
        rotated_ref = ref_normed @ R.T

        # Measure fit
        residual = target_normed - rotated_ref
        frob_residual = np.linalg.norm(residual) / np.linalg.norm(target_normed)

        # Per-mode cosine after rotation
        mode_cos = []
        for i in range(9):
            cos = float(np.dot(target_normed[i], rotated_ref[i]))
            mode_cos.append(cos)

        rotation_results[str(li)] = {
            "frob_residual": round(float(frob_residual), 4),
            "mean_cos_after_rotation": round(float(np.mean(mode_cos)), 4),
            "min_cos_after_rotation": round(float(np.min(mode_cos)), 4),
            "singular_values": [round(float(s), 4) for s in S[:9]],
        }

        log(f"  L{ref_layer}→L{li:>2d}: frob_residual={frob_residual:.4f}"
            f"  mean_cos={np.mean(mode_cos):.4f}"
            f"  min_cos={np.min(mode_cos):.4f}"
            f"  {'ROTATED' if np.mean(mode_cos) > 0.8 else 'DIFFERENT'}")

    # ══════════════════════════════════════════════════════
    # Exp 4: More modes (27, 81)
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 4: MORE MODES (9 vs 27 vs 81)")
    log(f"{'═'*70}")

    mode_sweep_layers = [15, 23, 25, 26]
    mode_counts = [9, 27, 81]
    mode_results = {}

    for li in mode_sweep_layers:
        log(f"\n  L{li}:")
        mode_results[str(li)] = {}
        for n_modes in mode_counts:
            data = build_layer_data(
                model, tokenizer, li, args.device, d_model,
                n_modes=n_modes,
            )
            # Float centroid (best case for this mode count)
            repl = FloatCentroidFFN(
                data["cls_W"], data["centroids"],
            ).to(args.device)
            r = install_and_measure(
                model, tokenizer, li, args.device,
                repl, baseline_ppl,
                f"{n_modes} modes (float centroid)",
            )
            mode_results[str(li)][str(n_modes)] = {
                **r,
                "cls_acc": round(data["cls_acc"], 4),
            }

    # ══════════════════════════════════════════════════════
    # Exp 5: Per-mode low-rank correction
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  EXP 5: PER-MODE LOW-RANK CORRECTION")
    log("  centroid + A[mode] @ B[mode] @ input (mixture of tiny MLPs)")
    log(f"{'═'*70}")

    lowrank_layers = [15, 23, 25, 26]
    lowrank_ranks = [4, 8, 16, 32]
    lowrank_results = {}

    for li in lowrank_layers:
        log(f"\n  L{li}:")
        lowrank_results[str(li)] = {}
        data = all_data[li]

        for rank in lowrank_ranks:
            A_modes, B_modes = build_per_mode_lowrank(data, rank=rank)

            repl = PerModeLowRankFFN(
                data["cls_W"], data["centroids"], A_modes, B_modes,
            ).to(args.device)

            # Params: 9 modes × (d_model × rank × 2) + centroids + classifier
            mode_params = 9 * d_model * rank * 2
            total_params = mode_params + 9 * d_model + 9 * d_model
            param_mb = total_params * 4 / 1024 / 1024

            r = install_and_measure(
                model, tokenizer, li, args.device,
                repl, baseline_ppl,
                f"9 modes + rank-{rank} correction ({param_mb:.1f}MB)",
            )
            lowrank_results[str(li)][str(rank)] = {
                **r,
                "params": total_params,
                "param_mb": round(param_mb, 2),
            }

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  SUMMARY")
    log(f"{'='*70}")
    log(f"  Baseline: PPL={baseline_ppl:.2f}")

    log(f"\n  Float vs Ternary centroids (Δ = ternary - float):")
    for li in target_layers:
        r = results_exp1[str(li)]
        log(f"    L{li:>2d}: ternary={r['ternary']['ratio']:.2f}x"
            f"  float={r['float_centroid']['ratio']:.2f}x"
            f"  Δ={r['delta']:+.4f}")

    log(f"\n  Within-cluster tightness (cosine to centroid):")
    for li in target_layers:
        v = variance_results[str(li)]
        tight = "TIGHT" if v["cos_mean"] > 0.95 else (
            "LOOSE" if v["cos_mean"] < 0.85 else "MODERATE")
        log(f"    L{li:>2d}: cos={v['cos_mean']:.4f} ({tight})")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "mode-geometry"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "baseline_ppl": baseline_ppl,
        "exp1_float_vs_ternary": results_exp1,
        "exp2_cluster_variance": variance_results,
        "exp3_cross_layer_rotation": rotation_results,
        "exp4_more_modes": mode_results,
        "exp5_per_mode_lowrank": lowrank_results,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"\n{'='*70}")
    log("  DONE")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
