"""Build Expanded PCA Trace Basis from Qwen3.6-27B Teacher.

Session 178+. The KIBC trace loss captures only 3.5% of FFN functional
space (64-layer dimensional analysis). This script builds a data-derived
PCA basis from diverse inputs through the teacher, giving the training
loop 50× more signal coverage.

What this does:
  1. Load Qwen/Qwen3.6-27B (torch, bfloat16, MPS/auto).
  2. Run 66 diverse probes through the teacher.
  3. For each of 64 layers, hook down_proj output (d_model=5120) at
     last-token position for all 66 probes → matrix (66, 5120).
  4. PCA per layer: keep top-50 components, or enough for 90% variance,
     whichever is fewer.
  5. Project each probe's FFN output onto the PCA basis →
     teacher_trace_targets shape (64, 66, 50).
  6. Compute stride_to_layer mapping: stride i → teacher layer int(i * 63 / 18).
  7. Save as NPZ at checkpoints/v15-zeroed/expanded_trace_basis.npz.

Output NPZ keys:
  pca_components       (64, 50, 5120)   — per-layer top PCA directions
  explained_variance   (64, 50)          — variance ratios per layer per PC
  teacher_trace_targets (64, 66, 50)     — probe activations projected onto PCA
  stride_to_layer      (19,)             — student stride → teacher layer index
  n_layers             scalar 64
  n_components         scalar 50
  d_model              scalar 5120
  n_probes             scalar 66

Usage:
    cd ~/src/verbum
    uv run python scripts/v15/build_trace_basis.py

    # With explicit output path:
    uv run python scripts/v15/build_trace_basis.py \\
        --output checkpoints/v15-zeroed/expanded_trace_basis.npz

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import sys
import time
from pathlib import Path

import numpy as np
import torch
from sklearn.decomposition import PCA
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# Constants — teacher architecture
# ══════════════════════════════════════════════════════════════════════

MODEL_NAME = "Qwen/Qwen3.6-27B"
N_LAYERS   = 64
D_MODEL    = 5120
N_STRIDES  = 19           # v15 student strides
N_COMPONENTS_TARGET = 50  # PCA components to retain (max)
VAR_THRESHOLD = 0.90      # 90% variance threshold (use fewer PCs if sufficient)

DEFAULT_OUTPUT = Path(__file__).parent.parent.parent / "checkpoints" / "v15-zeroed" / "expanded_trace_basis.npz"


# ══════════════════════════════════════════════════════════════════════
# Logging
# ══════════════════════════════════════════════════════════════════════

def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Diverse probes — copied verbatim from dimensional_analysis.py
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Diverse task probes covering 9 categories (66 total)."""
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
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_model(model_name: str = MODEL_NAME):
    """Load teacher model and tokenizer onto MPS or CPU (bfloat16)."""
    log(f"Loading tokenizer: {model_name}")
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    # Determine device — prefer MPS on Apple Silicon, fall back to CPU.
    # Note: device_map="auto" with MPS is not supported by HF accelerate,
    # so we set device_map explicitly.
    if torch.cuda.is_available():
        device = "cuda"
        device_map = "auto"
        log("  Using CUDA (device_map=auto)")
    elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        device = "mps"
        device_map = "mps"
        log("  Using MPS (Apple Silicon)")
    else:
        device = "cpu"
        device_map = "cpu"
        log("  Using CPU (no GPU found)")

    log(f"Loading model: {model_name} (bfloat16) ...")
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map=device_map,
        low_cpu_mem_usage=True,
        trust_remote_code=True,
    )
    model.eval()

    cfg = model.config
    n_layers = cfg.num_hidden_layers
    d_model  = cfg.hidden_size
    log(f"  Loaded: {n_layers} layers, d_model={d_model}")

    # Sanity-check architecture constants
    assert n_layers == N_LAYERS, f"Expected {N_LAYERS} layers, got {n_layers}"
    assert d_model  == D_MODEL,  f"Expected d_model={D_MODEL}, got {d_model}"

    return model, tokenizer


# ══════════════════════════════════════════════════════════════════════
# Hook-based down_proj capture — same pattern as dimensional_analysis.py
# ══════════════════════════════════════════════════════════════════════

def capture_all_layers(
    model: AutoModelForCausalLM,
    tokenizer: AutoTokenizer,
    prompt: str,
) -> np.ndarray:
    """Capture down_proj output at last-token position for all 64 layers.

    Uses register_forward_hook on each layer's mlp.down_proj to grab the
    output tensor (batch=1, seq_len, d_model) and slice [:, -1, :].

    Returns:
        float32 array of shape (N_LAYERS, D_MODEL).
    """
    ids = tokenizer.encode(prompt, return_tensors="pt")
    # Move to the same device as the model's first parameter.
    device = next(model.parameters()).device
    ids = ids.to(device)

    # Storage for captured activations, indexed by layer index.
    captures: dict[int, np.ndarray] = {}
    hooks = []

    layers = model.model.layers   # nn.ModuleList of 64 transformer layers

    for li, layer in enumerate(layers):
        mlp = layer.mlp
        if not hasattr(mlp, "down_proj"):
            # Safety guard — should never happen for Qwen3.6-27B.
            log(f"  WARNING: layer {li} has no down_proj; skipping")
            continue

        def make_hook(idx: int):
            def hook(module, inp, out):
                # out: (batch, seq_len, d_model) in bfloat16 on MPS/CUDA.
                # Slice last token, convert to float32, move to CPU.
                captures[idx] = out[0, -1, :].detach().cpu().float().numpy()
            return hook

        h = mlp.down_proj.register_forward_hook(make_hook(li))
        hooks.append(h)

    try:
        with torch.no_grad():
            _ = model(input_ids=ids)
    finally:
        for h in hooks:
            h.remove()

    # Assemble in layer order; fill missing layers with zeros.
    result = np.zeros((N_LAYERS, D_MODEL), dtype=np.float32)
    for li in range(N_LAYERS):
        if li in captures:
            result[li] = captures[li]
    return result


# ══════════════════════════════════════════════════════════════════════
# PCA per layer
# ══════════════════════════════════════════════════════════════════════

def _effective_n_components(explained_variance: np.ndarray, threshold: float = VAR_THRESHOLD) -> int:
    """Return the smallest k such that cumulative variance >= threshold."""
    cum = np.cumsum(explained_variance)
    idx = int(np.searchsorted(cum, threshold))
    return min(idx + 1, len(explained_variance))


def fit_pca_per_layer(
    all_ffn: np.ndarray,  # (N_LAYERS, n_probes, D_MODEL)
    n_components_max: int = N_COMPONENTS_TARGET,
    var_threshold: float = VAR_THRESHOLD,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Fit PCA independently per layer and return aligned arrays.

    For each layer:
      - Run PCA with n_components_max components on the (n_probes, D_MODEL) matrix.
      - Determine k = min(n_components_max, k_90pct) components to keep.
      - Pad component arrays to n_components_max if k < n_components_max.

    Args:
        all_ffn:          Shape (N_LAYERS, n_probes, D_MODEL).
        n_components_max: Maximum PCA components to retain (default 50).
        var_threshold:    Cumulative variance threshold (default 0.90).

    Returns:
        components     (N_LAYERS, n_components_max, D_MODEL)  — PCA directions
        exp_variance   (N_LAYERS, n_components_max)           — variance ratios
        probe_coords   (N_LAYERS, n_probes, n_components_max) — projections
    """
    n_layers, n_probes, d_model = all_ffn.shape
    n_comp = n_components_max

    components   = np.zeros((n_layers, n_comp, d_model), dtype=np.float32)
    exp_variance = np.zeros((n_layers, n_comp),          dtype=np.float32)
    probe_coords = np.zeros((n_layers, n_probes, n_comp), dtype=np.float32)

    # PCA can handle at most min(n_probes - 1, D_MODEL) components.
    n_pca = min(n_probes - 1, d_model, n_comp)

    log(f"\n  Fitting PCA ({n_pca} components) for {n_layers} layers ...")
    t0 = time.time()

    for li in range(n_layers):
        matrix = all_ffn[li]  # (n_probes, D_MODEL)

        pca = PCA(n_components=n_pca, random_state=42)
        coords_full = pca.fit_transform(matrix)  # (n_probes, n_pca)
        ev_full     = pca.explained_variance_ratio_

        # Determine how many PCs we actually keep for this layer.
        k90 = _effective_n_components(ev_full, var_threshold)
        k   = min(n_comp, k90)  # never exceed n_comp_max

        # Store (zero-padded beyond k automatically since arrays are pre-zeroed).
        components[li, :k, :]  = pca.components_[:k].astype(np.float32)
        exp_variance[li, :k]   = ev_full[:k].astype(np.float32)
        probe_coords[li, :, :k] = coords_full[:, :k].astype(np.float32)

        if (li + 1) % 8 == 0 or li == 0 or li == n_layers - 1:
            cum90 = float(np.cumsum(ev_full)[k90 - 1]) if k90 > 0 else 0.0
            log(f"    L{li:02d}: k90={k90:>3d}  k_kept={k:>3d}  "
                f"cum_var={cum90:.3f}  top1_var={ev_full[0]:.4f}")

    elapsed = time.time() - t0
    log(f"  PCA complete in {elapsed:.1f}s")
    return components, exp_variance, probe_coords


# ══════════════════════════════════════════════════════════════════════
# Stride → Teacher layer mapping
# ══════════════════════════════════════════════════════════════════════

def build_stride_to_layer(n_strides: int = N_STRIDES, n_teacher_layers: int = N_LAYERS) -> np.ndarray:
    """Map student strides to teacher layers by relative depth.

    stride i → teacher layer int(i * (n_teacher_layers - 1) / (n_strides - 1))

    With n_strides=19 and n_teacher_layers=64:
      stride  0 → layer  0
      stride  1 → layer  3
      stride  2 → layer  7
      ...
      stride 18 → layer 63

    Returns:
        int32 array of shape (n_strides,).
    """
    mapping = np.array(
        [int(i * (n_teacher_layers - 1) / (n_strides - 1)) for i in range(n_strides)],
        dtype=np.int32,
    )
    return mapping


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main() -> None:
    parser = argparse.ArgumentParser(
        description="Build expanded PCA trace basis from Qwen3.6-27B teacher."
    )
    parser.add_argument(
        "--model",
        default=MODEL_NAME,
        help=f"Teacher model name or path (default: {MODEL_NAME})",
    )
    parser.add_argument(
        "--output",
        default=str(DEFAULT_OUTPUT),
        help=f"Output NPZ path (default: {DEFAULT_OUTPUT})",
    )
    parser.add_argument(
        "--n-components",
        type=int,
        default=N_COMPONENTS_TARGET,
        help=f"Max PCA components to retain (default: {N_COMPONENTS_TARGET})",
    )
    parser.add_argument(
        "--var-threshold",
        type=float,
        default=VAR_THRESHOLD,
        help=f"Cumulative variance threshold for component selection (default: {VAR_THRESHOLD})",
    )
    args = parser.parse_args()

    out_path = Path(args.output)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    t_start = time.time()

    # ── 1. Build probes ───────────────────────────────────────────────
    probes = build_probes()
    n_probes = len(probes)
    log(f"\n{'═' * 68}")
    log(f"  Build Expanded PCA Trace Basis")
    log(f"  Model:      {args.model}")
    log(f"  Probes:     {n_probes}")
    log(f"  Layers:     {N_LAYERS}")
    log(f"  d_model:    {D_MODEL}")
    log(f"  Max PCs:    {args.n_components}")
    log(f"  Var thresh: {args.var_threshold:.0%}")
    log(f"  Output:     {out_path}")
    log(f"{'═' * 68}\n")

    # ── 2. Load model ─────────────────────────────────────────────────
    model, tokenizer = load_model(args.model)

    # ── 3. Capture down_proj outputs for all probes × all layers ──────
    log(f"\nCapturing FFN outputs ({n_probes} probes × {N_LAYERS} layers) ...")
    # all_ffn[layer, probe, d_model]
    all_ffn = np.zeros((N_LAYERS, n_probes, D_MODEL), dtype=np.float32)

    for pi, probe in enumerate(probes):
        t_probe = time.time()
        layer_vecs = capture_all_layers(model, tokenizer, probe["prompt"])
        all_ffn[:, pi, :] = layer_vecs   # (N_LAYERS, D_MODEL)

        if (pi + 1) % 10 == 0 or pi == 0:
            elapsed = time.time() - t_probe
            log(f"  probe {pi + 1:>3d}/{n_probes}  [{probe['category']:>14s}]  "
                f"last={elapsed:.2f}s  prompt={probe['prompt'][:40]!r}")

    log(f"\nCapture complete. all_ffn shape: {all_ffn.shape}  "
        f"({all_ffn.nbytes / 1e6:.1f} MB)")

    # ── 4. Free model memory before PCA ──────────────────────────────
    log("\nFreeing model from memory ...")
    del model
    gc.collect()
    # On MPS, empty cache explicitly.
    if hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    # ── 5. PCA per layer ─────────────────────────────────────────────
    components, exp_variance, probe_coords = fit_pca_per_layer(
        all_ffn,
        n_components_max=args.n_components,
        var_threshold=args.var_threshold,
    )
    # components:   (64, 50, 5120)
    # exp_variance: (64, 50)
    # probe_coords: (64, 66, 50) — this IS teacher_trace_targets

    teacher_trace_targets = probe_coords  # explicit alias for clarity

    # ── 6. Stride → layer mapping ─────────────────────────────────────
    stride_to_layer = build_stride_to_layer(N_STRIDES, N_LAYERS)
    log(f"\nStride → layer mapping (n_strides={N_STRIDES}):")
    for i, li in enumerate(stride_to_layer):
        log(f"  stride {i:>2d} → layer {li:>2d}")

    # ── 7. Summary statistics ─────────────────────────────────────────
    log(f"\n{'═' * 68}")
    log(f"  Summary")
    log(f"{'═' * 68}")
    log(f"  pca_components:       {components.shape}")
    log(f"  explained_variance:   {exp_variance.shape}")
    log(f"  teacher_trace_targets:{teacher_trace_targets.shape}")
    log(f"  stride_to_layer:      {stride_to_layer.shape}")

    # Per-layer 90% variance coverage check
    n_zero_comps = 0
    for li in range(N_LAYERS):
        cum90_idx = _effective_n_components(exp_variance[li], VAR_THRESHOLD)
        cum_at_kept = float(np.sum(exp_variance[li]))
        n_nonzero = int(np.sum(exp_variance[li] > 1e-6))
        n_zero_comps += (args.n_components - n_nonzero)

    mean_ev_top1  = float(np.mean(exp_variance[:, 0]))
    mean_ev_total = float(np.mean(np.sum(exp_variance, axis=1)))
    log(f"\n  Mean top-1 PC variance:   {mean_ev_top1:.4f} ({mean_ev_top1:.1%})")
    log(f"  Mean total kept variance: {mean_ev_total:.4f} ({mean_ev_total:.1%})")

    # ── 8. Save NPZ ───────────────────────────────────────────────────
    log(f"\nSaving to {out_path} ...")
    np.savez_compressed(
        str(out_path),
        pca_components=components,                            # (64, 50, 5120)
        explained_variance=exp_variance,                      # (64, 50)
        teacher_trace_targets=teacher_trace_targets,          # (64, 66, 50)
        stride_to_layer=stride_to_layer,                      # (19,)
        n_layers=np.int32(N_LAYERS),
        n_components=np.int32(args.n_components),
        d_model=np.int32(D_MODEL),
        n_probes=np.int32(n_probes),
    )

    # Verify save
    verify = np.load(str(out_path))
    log(f"\nVerification:")
    expected_keys = [
        "pca_components", "explained_variance", "teacher_trace_targets",
        "stride_to_layer", "n_layers", "n_components", "d_model", "n_probes",
    ]
    all_ok = True
    for key in expected_keys:
        if key in verify:
            val = verify[key]
            shape_str = str(val.shape) if hasattr(val, "shape") and val.ndim > 0 else str(val.item())
            log(f"  [✓] {key:30s} {shape_str}")
        else:
            log(f"  [✗] {key:30s}  MISSING")
            all_ok = False

    if all_ok:
        size_mb = out_path.stat().st_size / 1e6
        elapsed_total = time.time() - t_start
        log(f"\n  ✅ All keys present. File size: {size_mb:.1f} MB")
        log(f"  ✅ Total elapsed: {elapsed_total:.1f}s ({elapsed_total / 60:.1f} min)")
        log(f"\n  Ready for training loop at:\n    {out_path}")
    else:
        log("\n  ❌ Verification failed — check save step above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
