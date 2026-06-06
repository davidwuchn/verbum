#!/usr/bin/env python3
"""Multi-Projection Melt — CT scan, not X-ray.

Standard melt uses one loss (CE at output) — a single photograph
of the hologram. Multi-projection melt adds intermediate losses
at functional boundaries, giving the student direct gradient signal
at every stage of the pipeline.

The holographic projections:
  Δ₀:   L0  output — lexer fidelity
  Δ₂₁:  L21 output — composition fidelity (end of sweet spot)
  Δ₂₆:  L26 output — type crystallization (binding prep)
  Δ₃₀:  L30 output — binding result
  Δ_out: logits    — output distribution (standard CE)

Protocol:
  1. Cache teacher hidden states at all checkpoints
  2. Build compressed model (L0 SVD + L10-L21 ternary + L22-L26 ternary)
  3. Run standard melt (CE only) — baseline
  4. Reset, run multi-projection melt — compare
  5. If multi-projection wins, test with spec-decoding gating

Stage 3 is the target: it broke at 38.99x → 6.54x post-melt with
single-loss. Multi-projection should push past the wall.

Usage:
  uv run python scripts/experiments/multi_projection_melt.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import copy
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
# Checkpoints — the functional boundaries
# ══════════════════════════════════════════════════════════════

# Layer indices for intermediate losses (after these decoder layers)
CHECKPOINTS = {
    "lexer":        0,    # L0 — lexer/embedding
    "composition": 21,    # L21 — end of sweet spot
    "type_crystal": 26,   # L26 — end of binding prep
    "binding":     30,    # L30 — binding result
}

# Default weights for each projection loss
DEFAULT_WEIGHTS = {
    "lexer":        0.5,
    "composition":  1.0,
    "type_crystal": 2.0,   # highest weight — this is where the wall is
    "binding":      1.0,
    "output_ce":    1.0,
}


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

TEST_PROMPTS = [
    "The capital of France is",
    "To make a good cup of coffee, you should",
    "The most important thing about science is",
    "In the beginning, there was",
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


def generate_text(model, tokenizer, prompt, device, max_new=40):
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


def show_generation(model, tokenizer, device, label=""):
    if label:
        log(f"\n  {label} generation:")
    for prompt in TEST_PROMPTS:
        gen = generate_text(model, tokenizer, prompt, device)
        log(f"    {prompt} → {gen.strip()[:60]}")


# ══════════════════════════════════════════════════════════════
# Compression modules
# ══════════════════════════════════════════════════════════════

class TrainableLowRankLinear(torch.nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.A = torch.nn.Parameter(A.clone())
        self.B = torch.nn.Parameter(B.clone())

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        out = out.clamp(-65000, 65000)
        return out.to(x.dtype)


class TrainableTernaryFFN(torch.nn.Module):
    def __init__(self, cls_w, ternary_signs, gamma):
        super().__init__()
        self.classifier = torch.nn.Parameter(
            torch.tensor(cls_w, dtype=torch.float32),
        )
        self.gamma = torch.nn.Parameter(
            torch.tensor(gamma, dtype=torch.float32),
        )
        self.register_buffer(
            "ternary",
            torch.tensor(ternary_signs, dtype=torch.float32),
        )

    def forward(self, x):
        shape = x.shape
        xf = x.reshape(-1, x.shape[-1]).float()
        logits = xf @ self.classifier.T
        logits = logits.clamp(-20.0, 20.0)
        if self.training:
            weights = F.softmax(logits * 3.0, dim=-1)
            programs = self.ternary * self.gamma
            out = weights @ programs
        else:
            mode = logits.argmax(dim=-1)
            out = self.ternary[mode] * self.gamma[mode]
        return out.to(x.dtype).reshape(shape)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


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
                idx = np.linspace(
                    0, len(inp) - 1, 32, dtype=int,
                )
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
# Teacher state caching
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, tokenizer, texts, device,
                         checkpoints):
    """Run teacher on all texts, cache hidden states at checkpoints.

    Returns: list of dicts, one per text:
      [{checkpoint_name: tensor(seq_len, d_model)}, ...]
    """
    layers = get_layers(model)
    all_cached = []

    for text in texts:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}

        captured = {}
        hooks = []

        def make_hook(name):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                captured[name] = h.detach().cpu().float()
            return hook_fn

        for name, layer_idx in checkpoints.items():
            hooks.append(
                layers[layer_idx].register_forward_hook(
                    make_hook(name)
                )
            )

        model(**enc)

        for h in hooks:
            h.remove()

        # Store as (seq_len, d_model)
        text_states = {}
        for name in checkpoints:
            if name in captured:
                text_states[name] = captured[name][0]
        all_cached.append(text_states)

    return all_cached


# ══════════════════════════════════════════════════════════════
# Multi-projection melt engine
# ══════════════════════════════════════════════════════════════

def melt_step_standard(model, tokenizer, texts, device):
    """Standard melt: CE loss only. Returns loss value."""
    total_loss = 0.0
    total_tokens = 0
    for text in texts:
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()
        out = model(**enc, labels=labels)
        loss_val = out.loss.item()
        if np.isnan(loss_val) or np.isinf(loss_val):
            continue
        out.loss.backward()
        total_loss += loss_val * labels.numel()
        total_tokens += labels.numel()
    if total_tokens == 0:
        return float("nan")
    return total_loss / total_tokens


def melt_step_multi(model, tokenizer, texts, device,
                    teacher_cache, batch_indices,
                    checkpoints, weights):
    """Multi-projection melt: CE + intermediate cosine losses.

    Returns (total_loss, ce_loss, projection_losses_dict).
    """
    layers = get_layers(model)
    total_ce = 0.0
    total_tokens = 0
    projection_losses = {name: 0.0 for name in checkpoints}
    n_texts = 0

    for text_idx, global_idx in enumerate(batch_indices):
        text = texts[global_idx]
        enc = tokenizer(
            text, return_tensors="pt",
            truncation=True, max_length=128,
        )
        enc = {k: v.to(device) for k, v in enc.items()}
        labels = enc["input_ids"].clone()

        # Install checkpoint hooks to capture student states
        student_captured = {}
        hooks = []

        def make_hook(name):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                student_captured[name] = h  # keep on device, keep grad
            return hook_fn

        for name, layer_idx in checkpoints.items():
            hooks.append(
                layers[layer_idx].register_forward_hook(
                    make_hook(name)
                )
            )

        # Forward pass
        out = model(**enc, labels=labels)

        for h in hooks:
            h.remove()

        ce_val = out.loss.item()
        if np.isnan(ce_val) or np.isinf(ce_val):
            continue

        # Compute multi-projection loss
        proj_loss = torch.tensor(0.0, device=device)

        teacher_states = teacher_cache[global_idx]
        for name in checkpoints:
            if name not in student_captured or name not in teacher_states:
                continue

            student_h = student_captured[name][0]       # (seq, d_model), on device
            teacher_h = teacher_states[name].to(device)  # (seq, d_model)

            # Match sequence lengths (student may differ by 1)
            min_seq = min(student_h.shape[0], teacher_h.shape[0])
            s = student_h[:min_seq].float()
            t = teacher_h[:min_seq].float()

            # Cosine distance: 1 - cos_sim, per position, mean
            cos_sim = F.cosine_similarity(s, t, dim=-1)  # (seq,)
            cp_loss = (1.0 - cos_sim).mean()

            proj_loss = proj_loss + weights[name] * cp_loss
            projection_losses[name] += cp_loss.item()

        # Total loss: CE + projections
        total_loss = weights["output_ce"] * out.loss + proj_loss
        total_loss.backward()

        total_ce += ce_val * labels.numel()
        total_tokens += labels.numel()
        n_texts += 1

    if total_tokens == 0:
        return float("nan"), float("nan"), projection_losses

    for name in projection_losses:
        if n_texts > 0:
            projection_losses[name] /= n_texts

    return total_ce / total_tokens, total_ce / total_tokens, projection_losses


def run_melt(model, tokenizer, device, trainable_params,
             replacements, n_steps, lr, batch_size,
             mode="standard", teacher_cache=None,
             checkpoints=None, weights=None):
    """Run melt loop. mode='standard' or 'multi'."""
    optimizer = torch.optim.Adam(trainable_params, lr=lr)

    model.train()
    for _, repl in replacements:
        repl.train()

    history = []
    proj_history = []
    t0 = time.time()
    nan_count = 0

    for step in range(n_steps):
        optimizer.zero_grad()

        rng = np.random.RandomState(step)
        batch_idx = rng.choice(
            len(CALIBRATION_TEXTS), batch_size, replace=False,
        )

        if mode == "standard":
            batch = [CALIBRATION_TEXTS[i] for i in batch_idx]
            avg_loss = melt_step_standard(
                model, tokenizer, batch, device,
            )
            proj_losses = {}
        else:
            avg_loss, ce_loss, proj_losses = melt_step_multi(
                model, tokenizer, CALIBRATION_TEXTS, device,
                teacher_cache, batch_idx,
                checkpoints, weights,
            )

        grad_norm = torch.nn.utils.clip_grad_norm_(
            trainable_params, max_norm=1.0,
        )

        if np.isnan(avg_loss) or np.isinf(avg_loss):
            nan_count += 1
            optimizer.zero_grad()
            if nan_count > 10:
                log(f"      too many NaNs ({nan_count}), stopping")
                break
            continue

        optimizer.step()
        history.append(avg_loss)
        proj_history.append(proj_losses)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            proj_str = ""
            if proj_losses:
                proj_str = "  proj: " + " ".join(
                    f"{k[:4]}={v:.4f}"
                    for k, v in proj_losses.items()
                )
            log(f"      step {step+1:>3d}/{n_steps}:"
                f" loss={avg_loss:.4f}"
                f" grad={grad_norm:.2f}"
                f" ({elapsed:.0f}s){proj_str}")

    model.eval()
    for _, repl in replacements:
        repl.eval()

    return history, proj_history


# ══════════════════════════════════════════════════════════════
# Model construction (builds Stage 3)
# ══════════════════════════════════════════════════════════════

def build_compressed_model(model, tokenizer, device, d_model,
                           l0_rank=750, n_modes=9):
    """Build Stage 3 compressed model. Returns trainable_params,
    replacements list, and initial param snapshot for reset."""

    layers = get_layers(model)
    trainable_params = []
    replacements = []  # (hook_handle, module)

    # ── L0 SVD ────────────────────────────────────────────
    log("    Installing L0 SVD rank-750...")
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, l0_rank)
        lr_mod = TrainableLowRankLinear(
            A.to(device), B.to(device),
        )
        setattr(mlp0, pname, lr_mod)
        trainable_params.extend([lr_mod.A, lr_mod.B])
    log("    L0 ✓")

    # ── Core ternary L13-L21 ──────────────────────────────
    log("    Installing core ternary (L13-L21)...")
    for li in range(13, 22):
        h, repl = _install_ternary(
            model, tokenizer, li, device, d_model,
            n_modes, trainable_params,
        )
        replacements.append((h, repl))

    # ── Inward ternary L10-L12 ────────────────────────────
    log("    Installing inward ternary (L10-L12)...")
    for li in range(10, 13):
        h, repl = _install_ternary(
            model, tokenizer, li, device, d_model,
            n_modes, trainable_params,
        )
        replacements.append((h, repl))

    # ── Outward ternary L22-L26 ───────────────────────────
    log("    Installing outward ternary (L22-L26)...")
    for li in range(22, 27):
        h, repl = _install_ternary(
            model, tokenizer, li, device, d_model,
            n_modes, trainable_params,
        )
        replacements.append((h, repl))

    # Freeze all original params
    for param in model.parameters():
        param.requires_grad = False
    for param in trainable_params:
        param.requires_grad = True

    n_train = sum(p.numel() for p in trainable_params)
    log(f"    Total: {len(replacements)} ternary + L0 SVD"
        f" = {n_train:,} trainable params")

    # Snapshot for reset
    snapshot = [p.data.clone() for p in trainable_params]

    return trainable_params, replacements, snapshot


def restore_from_snapshot(trainable_params, snapshot):
    """Reset all trainable params to their initial values."""
    for p, s in zip(trainable_params, snapshot):
        p.data.copy_(s)


def _install_ternary(model, tokenizer, layer_idx, device,
                     d_model, n_modes, trainable_params):
    """Install ternary hook. Returns (handle, replacement)."""
    mlp_in, mlp_out = collect_mlp_data(
        model, tokenizer, layer_idx, device,
        CALIBRATION_TEXTS,
    )

    km = MiniBatchKMeans(
        n_clusters=n_modes, random_state=42,
        batch_size=min(256, len(mlp_out)), n_init=5,
    )
    labels = km.fit_predict(mlp_out)

    ternary_signs = np.zeros((n_modes, d_model))
    gamma = np.zeros((n_modes, d_model))
    for i in range(n_modes):
        mask = labels == i
        if mask.sum() == 0:
            continue
        c = mlp_out[mask].mean(axis=0)
        ternary_signs[i] = np.sign(c)
        gamma[i] = np.abs(c)

    cls_W, cls_acc = train_classifier(mlp_in, labels, n_modes)
    replacement = TrainableTernaryFFN(
        cls_W, ternary_signs, gamma,
    ).to(device)

    trainable_params.extend([
        replacement.classifier, replacement.gamma,
    ])

    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    def make_hook(repl):
        def hook_fn(module, inp, out):
            x = inp[0] if isinstance(inp, tuple) else inp
            return repl(x)
        return hook_fn

    h = mlp.register_forward_hook(make_hook(replacement))
    log(f"      L{layer_idx}: acc={cls_acc:.1%}")
    return h, replacement


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
    p.add_argument("--l0-rank", type=int, default=750)
    p.add_argument("--n-modes", type=int, default=9)
    p.add_argument("--melt-steps", type=int, default=80)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--batch-size", type=int, default=4)
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  MULTI-PROJECTION MELT")
    log("  CT scan, not X-ray — holographic projections at every level")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Melt steps: {args.melt_steps}")
    log(f"  Checkpoints: {list(CHECKPOINTS.keys())}")
    log(f"  Weights: {DEFAULT_WEIGHTS}")

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
    base_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    base_correct, base_total = measure_facts(
        model, tokenizer, args.device,
    )
    log(f"  Baseline PPL: {base_ppl:.2f}")
    log(f"  Baseline facts: {base_correct}/{base_total}")

    # ══════════════════════════════════════════════════════
    # Phase 1: Cache teacher hidden states
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: CACHING TEACHER STATES")
    log(f"{'═'*70}")

    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, tokenizer, CALIBRATION_TEXTS, args.device,
        CHECKPOINTS,
    )
    elapsed = time.time() - t0
    log(f"  Cached {len(teacher_cache)} texts × "
        f"{len(CHECKPOINTS)} checkpoints in {elapsed:.1f}s")

    # Verify cache
    for name in CHECKPOINTS:
        shapes = [tc[name].shape for tc in teacher_cache if name in tc]
        log(f"    {name}: {len(shapes)} texts,"
            f" shapes {shapes[0]} to {shapes[-1]}")

    # ══════════════════════════════════════════════════════
    # Phase 2: Build compressed model (Stage 3)
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: BUILD STAGE 3 COMPRESSED MODEL")
    log(f"{'═'*70}")

    trainable_params, replacements, snapshot = build_compressed_model(
        model, tokenizer, args.device, d_model,
        args.l0_rank, args.n_modes,
    )

    # Measure pre-melt
    pre_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    pre_ratio = pre_ppl / base_ppl
    log(f"\n  Pre-melt PPL: {pre_ppl:.2f} ({pre_ratio:.2f}x)")

    # ══════════════════════════════════════════════════════
    # Phase 3A: Standard melt (CE only)
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3A: STANDARD MELT (CE loss only)")
    log(f"{'═'*70}")

    history_std, _ = run_melt(
        model, tokenizer, args.device,
        trainable_params, replacements,
        args.melt_steps, args.lr, args.batch_size,
        mode="standard",
    )

    std_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    std_ratio = std_ppl / base_ppl
    std_correct, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Standard melt PPL: {std_ppl:.2f} ({std_ratio:.2f}x)")
    log(f"  Standard melt facts: {std_correct}/{base_total}")
    show_generation(model, tokenizer, args.device, "Standard melt")

    # ══════════════════════════════════════════════════════
    # Reset to pre-melt state
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  RESETTING TO PRE-MELT STATE")
    log(f"{'═'*70}")

    restore_from_snapshot(trainable_params, snapshot)

    reset_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    log(f"  Reset PPL: {reset_ppl:.2f} ({reset_ppl/base_ppl:.2f}x)"
        f" (should match pre-melt {pre_ratio:.2f}x)")

    # ══════════════════════════════════════════════════════
    # Phase 3B: Multi-projection melt
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3B: MULTI-PROJECTION MELT (CE + intermediate losses)")
    log(f"{'═'*70}")

    history_multi, proj_history = run_melt(
        model, tokenizer, args.device,
        trainable_params, replacements,
        args.melt_steps, args.lr, args.batch_size,
        mode="multi",
        teacher_cache=teacher_cache,
        checkpoints=CHECKPOINTS,
        weights=DEFAULT_WEIGHTS,
    )

    multi_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    multi_ratio = multi_ppl / base_ppl
    multi_correct, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Multi-projection melt PPL: {multi_ppl:.2f}"
        f" ({multi_ratio:.2f}x)")
    log(f"  Multi-projection facts: {multi_correct}/{base_total}")
    show_generation(model, tokenizer, args.device, "Multi-projection")

    # ══════════════════════════════════════════════════════
    # Phase 3C: Multi-projection with higher weight on type_crystal
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3C: MULTI-PROJECTION (boosted type_crystal weight)")
    log(f"{'═'*70}")

    restore_from_snapshot(trainable_params, snapshot)

    boosted_weights = dict(DEFAULT_WEIGHTS)
    boosted_weights["type_crystal"] = 5.0
    boosted_weights["binding"] = 2.0
    log(f"  Weights: {boosted_weights}")

    history_boost, proj_history_boost = run_melt(
        model, tokenizer, args.device,
        trainable_params, replacements,
        args.melt_steps, args.lr, args.batch_size,
        mode="multi",
        teacher_cache=teacher_cache,
        checkpoints=CHECKPOINTS,
        weights=boosted_weights,
    )

    boost_ppl = measure_ppl(model, tokenizer, EVAL_TEXTS, args.device)
    boost_ratio = boost_ppl / base_ppl
    boost_correct, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Boosted melt PPL: {boost_ppl:.2f} ({boost_ratio:.2f}x)")
    log(f"  Boosted facts: {boost_correct}/{base_total}")
    show_generation(model, tokenizer, args.device, "Boosted")

    # ══════════════════════════════════════════════════════
    # Summary
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  FINAL COMPARISON")
    log(f"{'='*70}")
    log(f"  Baseline:           PPL={base_ppl:.2f}"
        f"  facts={base_correct}/{base_total}")
    log(f"  Pre-melt:           PPL={pre_ppl:.2f}"
        f" ({pre_ratio:.2f}x)")
    log(f"  Standard melt:      PPL={std_ppl:.2f}"
        f" ({std_ratio:.2f}x)"
        f"  facts={std_correct}/{base_total}")
    log(f"  Multi-projection:   PPL={multi_ppl:.2f}"
        f" ({multi_ratio:.2f}x)"
        f"  facts={multi_correct}/{base_total}")
    log(f"  Boosted projection: PPL={boost_ppl:.2f}"
        f" ({boost_ratio:.2f}x)"
        f"  facts={boost_correct}/{base_total}")

    winner = "MULTI" if multi_ratio < std_ratio else "STANDARD"
    if boost_ratio < min(multi_ratio, std_ratio):
        winner = "BOOSTED"
    delta_multi = std_ratio - multi_ratio
    delta_boost = std_ratio - boost_ratio
    log(f"\n  Winner: {winner}")
    log(f"  Multi vs Standard:  Δ={delta_multi:+.2f}x")
    log(f"  Boosted vs Standard: Δ={delta_boost:+.2f}x")

    verdict = "PASS" if min(multi_ratio, boost_ratio) < std_ratio * 0.9 else (
        "MARGINAL" if min(multi_ratio, boost_ratio) < std_ratio else "FAIL"
    )
    log(f"  VERDICT: {verdict}")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "multi-projection-melt"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "melt_steps": args.melt_steps,
        "lr": args.lr,
        "baseline_ppl": base_ppl,
        "baseline_facts": base_correct,
        "pre_melt_ppl": pre_ppl,
        "pre_melt_ratio": round(pre_ratio, 4),
        "standard": {
            "ppl": std_ppl,
            "ratio": round(std_ratio, 4),
            "facts": std_correct,
            "loss_history": [round(x, 4) for x in history_std],
        },
        "multi_projection": {
            "weights": DEFAULT_WEIGHTS,
            "ppl": multi_ppl,
            "ratio": round(multi_ratio, 4),
            "facts": multi_correct,
            "loss_history": [round(x, 4) for x in history_multi],
        },
        "boosted_projection": {
            "weights": boosted_weights,
            "ppl": boost_ppl,
            "ratio": round(boost_ratio, 4),
            "facts": boost_correct,
            "loss_history": [round(x, 4) for x in history_boost],
        },
        "winner": winner,
        "verdict": verdict,
        "checkpoints": CHECKPOINTS,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2, default=str)
    log(f"\n  Results saved to {out_path}")
    log(f"\n{'='*70}")
    log("  DONE")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
