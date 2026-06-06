#!/usr/bin/env python3
"""Lambda Tracer Diagnostic — crystal probes as tracer dye.

Run 535 crystal probes through the original and compressed models,
capture hidden states at every layer boundary, cross-tabulate
combinator × layer → fidelity matrix. Find WHICH combinator fails
at WHICH layer when L22-L26 are added.

Compression stages (cumulative):
  Stage 2: L0 SVD rank-750 + L10-L21 ternary (12+L0, 1.77x PPL)
  Stage 3: Stage 2 + L22-L26 ternary        (17+L0, 6.54x PPL)

The Stage 2→3 delta isolates the damage from L22-L26 ternarization.

Usage:
  uv run python scripts/experiments/lambda_tracer.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
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
# Calibration corpus (same as staged_melt.py)
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


# ══════════════════════════════════════════════════════════════
# Utilities
# ══════════════════════════════════════════════════════════════

def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


# ══════════════════════════════════════════════════════════════
# Compression modules (from staged_melt.py)
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
        # Always eval mode for tracer — no melting
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
# Hidden state capture
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def capture_hidden_states(model, input_ids, device):
    """Capture hidden states after every decoder layer.

    Returns list of tensors: [embed, L0, L1, ..., L35]
    Each tensor is (1, seq_len, d_model) on CPU.
    """
    states = []
    layers = get_layers(model)

    def make_hook(idx):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            states.append(h.detach().cpu())
        return hook_fn

    hooks = []
    for i, layer in enumerate(layers):
        hooks.append(layer.register_forward_hook(make_hook(i)))

    embed_state = []
    def embed_hook(mod, inp, out):
        embed_state.append(out.detach().cpu())

    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        hooks.append(
            model.model.embed_tokens.register_forward_hook(embed_hook)
        )

    input_ids = input_ids.to(device)
    model(input_ids)

    for h in hooks:
        h.remove()

    if embed_state:
        return embed_state + states
    return states


def last_token_cos(baseline_states, compressed_states):
    """Per-layer cosine similarity of last-token hidden states.

    Returns array of shape (n_layers+1,) — embed + 36 layers.
    """
    n = min(len(baseline_states), len(compressed_states))
    sims = np.zeros(n)
    for i in range(n):
        # Last token of each
        a = baseline_states[i][0, -1, :].float()
        b = compressed_states[i][0, -1, :].float()
        sims[i] = F.cosine_similarity(
            a.unsqueeze(0), b.unsqueeze(0),
        ).item()
    return sims


def mean_token_cos(baseline_states, compressed_states):
    """Per-layer cosine similarity averaged over all tokens.

    Returns array of shape (n_layers+1,).
    """
    n = min(len(baseline_states), len(compressed_states))
    sims = np.zeros(n)
    for i in range(n):
        a = baseline_states[i][0].float()  # (seq, d_model)
        b = compressed_states[i][0].float()
        # Per-token cosine, then mean
        cos = F.cosine_similarity(a, b, dim=-1)  # (seq,)
        sims[i] = cos.mean().item()
    return sims


# ══════════════════════════════════════════════════════════════
# Compression installation
# ══════════════════════════════════════════════════════════════

def install_l0_lowrank(model, device, rank=750):
    """Replace L0 MLP projections with SVD low-rank."""
    layers = get_layers(model)
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, rank)
        lr_mod = TrainableLowRankLinear(
            A.to(device), B.to(device),
        )
        setattr(mlp0, pname, lr_mod)
    log("  L0 SVD low-rank installed ✓")


def install_ternary_layer(model, tokenizer, layer_idx, device,
                          d_model, n_modes=9):
    """Collect data, build ternary, install hook."""
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

    layers = get_layers(model)
    mlp = layers[layer_idx].mlp

    def make_hook(repl):
        def hook_fn(module, inp, out):
            x = inp[0] if isinstance(inp, tuple) else inp
            return repl(x)
        return hook_fn

    h = mlp.register_forward_hook(make_hook(replacement))
    log(f"    L{layer_idx}: cls_acc={cls_acc:.1%} ✓")
    return h, replacement


# ══════════════════════════════════════════════════════════════
# Probe runner
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def run_probes(model, tokenizer, probes, device, label=""):
    """Run all probes and capture hidden states.

    Returns:
      probe_states: list of (probe, states) where states is
                    list of tensors [embed, L0, ..., L35]
    """
    n = len(probes)
    if label:
        log(f"\n  Running {n} probes [{label}]...")

    results = []
    t0 = time.time()
    for i, probe in enumerate(probes):
        enc = tokenizer(
            probe.prompt, return_tensors="pt",
            truncation=True, max_length=128,
        )
        states = capture_hidden_states(
            model, enc["input_ids"], device,
        )
        results.append((probe, states))

        if (i + 1) % 100 == 0:
            elapsed = time.time() - t0
            rate = (i + 1) / elapsed
            log(f"    {i+1}/{n} ({rate:.1f} probes/s)")

    elapsed = time.time() - t0
    log(f"    Done: {n} probes in {elapsed:.1f}s"
        f" ({n/elapsed:.1f} probes/s)")
    return results


# ══════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════

def compute_fidelity_matrix(baseline_results, compressed_results):
    """Compute per-combinator, per-layer cosine fidelity.

    Returns:
      fidelity: dict[combinator -> ndarray of shape (n_layers+1,)]
                mean cosine similarity per layer
      per_probe: list of (probe_id, combinator, sims_array)
    """
    combinator_sims = defaultdict(list)
    per_probe = []

    for (probe, base_states), (_, comp_states) in zip(
        baseline_results, compressed_results,
    ):
        sims = last_token_cos(base_states, comp_states)
        combinator_sims[probe.combinator].append(sims)
        per_probe.append((probe.id, probe.combinator, sims))

    fidelity = {}
    for comb, sim_list in combinator_sims.items():
        arr = np.stack(sim_list)  # (n_probes, n_layers+1)
        fidelity[comb] = arr.mean(axis=0)  # (n_layers+1,)

    return fidelity, per_probe


def find_degradation(fid_s2, fid_s3, layer_range=(22, 27)):
    """Find combinator-specific degradation from Stage 2→3.

    Returns list of (combinator, layer, delta) sorted by severity.
    """
    degradations = []
    for comb in sorted(fid_s2.keys()):
        s2 = fid_s2[comb]
        s3 = fid_s3[comb]
        for layer in range(layer_range[0], min(layer_range[1], len(s2))):
            # layer+1 because index 0 is embedding
            idx = layer + 1
            if idx < len(s2) and idx < len(s3):
                delta = s2[idx] - s3[idx]  # positive = degradation
                degradations.append((comb, layer, delta, s2[idx], s3[idx]))

    degradations.sort(key=lambda x: -x[2])  # worst first
    return degradations


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
    p.add_argument("--max-probes", type=int, default=0,
                   help="Limit probes (0=all, for quick test)")
    args = p.parse_args()

    log(f"\n{'='*70}")
    log("  LAMBDA TRACER DIAGNOSTIC")
    log("  Crystal probes as tracer dye through compressed model")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  L0 rank: {args.l0_rank}")
    log(f"  Ternary modes: {args.n_modes}")

    # ── Load model ────────────────────────────────────────
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
    n_layers = model.config.num_hidden_layers
    log(f"  d_model: {d_model}, n_layers: {n_layers}")

    # ── Get probes ────────────────────────────────────────
    probes = crystal_probes()
    if args.max_probes > 0:
        probes = probes[:args.max_probes]
    log(f"  Crystal probes: {len(probes)}")

    comb_counts = defaultdict(int)
    for pr in probes:
        comb_counts[pr.combinator] += 1
    log(f"  Combinators: {dict(sorted(comb_counts.items()))}")

    # ══════════════════════════════════════════════════════
    # Phase 1: BASELINE — original model
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: BASELINE (original model)")
    log(f"{'═'*70}")

    baseline_results = run_probes(
        model, tokenizer, probes, args.device, "baseline",
    )

    # ══════════════════════════════════════════════════════
    # Phase 2: STAGE 2 — L0 SVD + L10-L21 ternary
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: STAGE 2 (L0 SVD + L10-L21 ternary)")
    log(f"{'═'*70}")

    # Install L0 low-rank
    log(f"\n  Installing L0 SVD rank-{args.l0_rank}...")
    install_l0_lowrank(model, args.device, args.l0_rank)

    # Install ternary layers L10-L21
    # Must do it in order: L13-L21 first (core), then L10-L12
    # (calibrated through already-compressed model)
    all_hooks = []

    log("\n  Installing core ternary (L13-L21)...")
    for li in range(13, 22):
        h, repl = install_ternary_layer(
            model, tokenizer, li, args.device, d_model,
            args.n_modes,
        )
        all_hooks.append(h)

    log("\n  Installing inward ternary (L10-L12)...")
    for li in range(10, 13):
        h, repl = install_ternary_layer(
            model, tokenizer, li, args.device, d_model,
            args.n_modes,
        )
        all_hooks.append(h)

    log(f"\n  Stage 2: {len(all_hooks)} ternary layers + L0 SVD")

    stage2_results = run_probes(
        model, tokenizer, probes, args.device, "stage 2",
    )

    # ══════════════════════════════════════════════════════
    # Phase 3: STAGE 3 — + L22-L26 ternary
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 3: STAGE 3 (+L22-L26 ternary)")
    log(f"{'═'*70}")

    log("\n  Installing outward ternary (L22-L26)...")
    for li in range(22, 27):
        h, repl = install_ternary_layer(
            model, tokenizer, li, args.device, d_model,
            args.n_modes,
        )
        all_hooks.append(h)

    log(f"\n  Stage 3: {len(all_hooks)} ternary layers + L0 SVD")

    stage3_results = run_probes(
        model, tokenizer, probes, args.device, "stage 3",
    )

    # ══════════════════════════════════════════════════════
    # Analysis
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  ANALYSIS")
    log(f"{'═'*70}")

    # Compute fidelity matrices
    fid_s2, per_probe_s2 = compute_fidelity_matrix(
        baseline_results, stage2_results,
    )
    fid_s3, per_probe_s3 = compute_fidelity_matrix(
        baseline_results, stage3_results,
    )

    # ── Per-combinator summary ────────────────────────────
    combinators = sorted(fid_s2.keys())

    log("\n  Per-combinator fidelity (cosine sim to baseline):")
    log(f"\n  {'Comb':>6s}  {'Stage':>5s}  "
        f"{'L10':>6s}  {'L15':>6s}  {'L20':>6s}  "
        f"{'L22':>6s}  {'L24':>6s}  {'L26':>6s}  "
        f"{'L28':>6s}  {'L30':>6s}  {'L35':>6s}")
    log(f"  {'─'*6}  {'─'*5}  "
        f"{'─'*6}  {'─'*6}  {'─'*6}  "
        f"{'─'*6}  {'─'*6}  {'─'*6}  "
        f"{'─'*6}  {'─'*6}  {'─'*6}")

    sample_layers = [10, 15, 20, 22, 24, 26, 28, 30, 35]

    for comb in combinators:
        s2 = fid_s2[comb]
        s3 = fid_s3[comb]
        # Stage 2 row
        vals_s2 = "  ".join(
            f"{s2[l+1]:6.4f}" if l + 1 < len(s2) else "   N/A"
            for l in sample_layers
        )
        log(f"  {comb:>6s}  {'S2':>5s}  {vals_s2}")
        # Stage 3 row
        vals_s3 = "  ".join(
            f"{s3[l+1]:6.4f}" if l + 1 < len(s3) else "   N/A"
            for l in sample_layers
        )
        log(f"  {'':>6s}  {'S3':>5s}  {vals_s3}")
        # Delta row
        deltas = "  ".join(
            f"{s2[l+1] - s3[l+1]:+6.4f}"
            if l + 1 < min(len(s2), len(s3)) else "   N/A"
            for l in sample_layers
        )
        log(f"  {'':>6s}  {'Δ':>5s}  {deltas}")
        log()

    # ── Degradation ranking ───────────────────────────────
    # Check degradation across ALL layers, not just L22-L26
    degradations = find_degradation(fid_s2, fid_s3, (0, n_layers))
    log(f"\n  Top 20 degradations (Stage 2→3, positive=worse):")
    log(f"  {'Comb':>6s}  {'Layer':>5s}  {'Δ':>8s}  "
        f"{'S2 cos':>8s}  {'S3 cos':>8s}")
    log(f"  {'─'*6}  {'─'*5}  {'─'*8}  {'─'*8}  {'─'*8}")
    for comb, layer, delta, s2_val, s3_val in degradations[:20]:
        log(f"  {comb:>6s}  L{layer:<4d}  {delta:+8.4f}  "
            f"{s2_val:8.4f}  {s3_val:8.4f}")

    # ── Overall fidelity by combinator at L35 ─────────────
    log(f"\n  Output fidelity (L{n_layers-1}, last layer):")
    log(f"  {'Comb':>6s}  {'S2 cos':>8s}  {'S3 cos':>8s}  "
        f"{'Δ':>8s}  {'n':>4s}")
    log(f"  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*4}")
    for comb in combinators:
        s2_val = fid_s2[comb][-1]  # last layer
        s3_val = fid_s3[comb][-1]
        delta = s2_val - s3_val
        n = comb_counts[comb]
        log(f"  {comb:>6s}  {s2_val:8.4f}  {s3_val:8.4f}  "
            f"{delta:+8.4f}  {n:>4d}")

    # ── Per-layer fidelity (all combinators averaged) ─────
    all_s2 = np.stack([fid_s2[c] for c in combinators])
    all_s3 = np.stack([fid_s3[c] for c in combinators])
    mean_s2 = all_s2.mean(axis=0)
    mean_s3 = all_s3.mean(axis=0)

    log(f"\n  Mean fidelity across all combinators:")
    log(f"  {'Layer':>6s}  {'S2':>8s}  {'S3':>8s}  {'Δ':>8s}")
    log(f"  {'─'*6}  {'─'*8}  {'─'*8}  {'─'*8}")
    for i in range(len(mean_s2)):
        layer_label = "embed" if i == 0 else f"L{i-1}"
        delta = mean_s2[i] - mean_s3[i]
        log(f"  {layer_label:>6s}  {mean_s2[i]:8.4f}  "
            f"{mean_s3[i]:8.4f}  {delta:+8.4f}")

    # ── Variance analysis — is damage uniform or selective? ─
    log(f"\n  Combinator variance at critical layers"
        f" (high var = selective damage):")
    for layer in [22, 23, 24, 25, 26, 30, 35]:
        idx = layer + 1
        if idx >= all_s3.shape[1]:
            continue
        vals_s3 = all_s3[:, idx]
        vals_s2 = all_s2[:, idx]
        delta_vals = vals_s2 - vals_s3
        log(f"  L{layer}: S3 mean={vals_s3.mean():.4f}"
            f" std={vals_s3.std():.4f}"
            f"  Δ mean={delta_vals.mean():.4f}"
            f" std={delta_vals.std():.4f}"
            f"  {'SELECTIVE' if delta_vals.std() > 0.01 else 'UNIFORM'}")

    # ══════════════════════════════════════════════════════
    # Save results
    # ══════════════════════════════════════════════════════
    out_dir = _PROJECT_ROOT / "results" / "lambda-tracer"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    # Full fidelity matrices
    fidelity_data = {
        "stage2": {
            c: fid_s2[c].tolist() for c in combinators
        },
        "stage3": {
            c: fid_s3[c].tolist() for c in combinators
        },
    }

    # Per-probe detail (for deep analysis)
    probe_detail = []
    for pid, comb, sims in per_probe_s2:
        probe_detail.append({
            "probe_id": pid,
            "combinator": comb,
            "stage2_cos": sims.tolist(),
        })
    for i, (pid, comb, sims) in enumerate(per_probe_s3):
        probe_detail[i]["stage3_cos"] = sims.tolist()

    result = {
        "model": args.model,
        "l0_rank": args.l0_rank,
        "n_modes": args.n_modes,
        "n_probes": len(probes),
        "combinator_counts": dict(sorted(comb_counts.items())),
        "n_layers": n_layers,
        "stage2_layers": {
            "l0_svd": True,
            "ternary": list(range(10, 22)),
        },
        "stage3_layers": {
            "l0_svd": True,
            "ternary": list(range(10, 27)),
        },
        "fidelity": fidelity_data,
        "mean_fidelity": {
            "stage2": mean_s2.tolist(),
            "stage3": mean_s3.tolist(),
        },
        "degradation_top20": [
            {
                "combinator": comb,
                "layer": layer,
                "delta": round(delta, 6),
                "s2_cos": round(s2v, 6),
                "s3_cos": round(s3v, 6),
            }
            for comb, layer, delta, s2v, s3v
            in degradations[:20]
        ],
    }

    # Save summary
    out_path = out_dir / f"{slug}_summary.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Summary saved to {out_path}")

    # Save per-probe detail
    detail_path = out_dir / f"{slug}_probes.json"
    with open(detail_path, "w") as f:
        json.dump(probe_detail, f, indent=2)
    log(f"  Per-probe detail saved to {detail_path}")

    # Clean up hooks
    for h in all_hooks:
        h.remove()

    log(f"\n{'='*70}")
    log("  LAMBDA TRACER COMPLETE")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
