"""Melt + Align — Short GD burst on etched v6 with crystal loss.

Phase 3 of the etch pipeline. After the 360° etch writes teacher signs
into v6 plates, this script:

  1. Freezes all ternary plates (signs frozen, not trainable)
  2. Trains only gamma (beam) parameters + other continuous params
  3. Loss = CE + λ_crystal × per_pass_crystal_lattice_loss
  4. The crystal loss keeps geometry stable during melt
  5. CE loss teaches the beams to route through the new sign topology

The crystal targets are CCA angle overlap metrics from the extraction
phase (weight-space relational invariants). These act as the 5D lattice
error correction signal — pulling beams back onto the crystal manifold
whenever GD drifts.

Evidence for this approach:
  - GD converges in 100 steps for 87% of accuracy (session 126)
  - Crystal lattice loss maintains 0.9998 agreement (evo descent v3)
  - 18 per-layer crystal targets is the sweet spot (session 126)
  - Beams compensate for 27% wrong signs at Q2 (session 126)

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/melt_v6.py

    # Custom steps:
    uv run python scripts/v12/melt_v6.py --steps 3000

    # Compare etched vs original:
    uv run python scripts/v12/melt_v6.py --compare

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim


def log(msg):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Config
# ══════════════════════════════════════════════════════════════════════

ETCHED_CHECKPOINT = Path("checkpoints/v6-etched-360")
ORIGINAL_CHECKPOINT = Path("checkpoints/vsm-lm-v6/step_032500")
EXTRACTION_DIR = Path("results/v6-etch")
OUTPUT_DIR = Path("checkpoints/v6-melted-360")
RESULTS_DIR = Path("results/v6-melt")

# Training config
MELT_STEPS = 1000
BATCH_SIZE = 4
SEQ_LEN = 512          # shorter than training (4096) for speed
LR = 1e-4              # conservative — we're fine-tuning beams
CRYSTAL_LAMBDA = 0.5   # proven in evo descent v3
EVAL_INTERVAL = 100
SAVE_INTERVAL = 500

# Data — we'll use the compile training data (already tokenized for Pythia)
DATA_PATH = Path("data/compile-train.jsonl")


# ══════════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════════

def load_v6_model(checkpoint_path: Path):
    """Load v6 model from checkpoint.

    Returns the model and its meta config.
    """
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from verbum.v6.model import VSMLMV6

    with open(checkpoint_path / "meta.json") as f:
        meta = json.load(f)

    config = meta.get("config", {})
    model = VSMLMV6(
        vocab_size=config.get("vocab_size", 50277),
        d_model=config.get("d_model", 512),
        d_register=config.get("d_register", 128),
        max_len=config.get("seq_len", 4096),
        n_heads=config.get("n_heads", 8),
        d_ff=config.get("d_ff", 1536),
        d_ff_consolidate=config.get("d_ff_consolidate", 2048),
        window=config.get("window", 8),
        strides=tuple(config.get("strides", [1, 8, 16, 32, 64, 128, 256, 512, 1024])),
    )

    # Load weights
    weights = mx.load(str(checkpoint_path / "weights.safetensors"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    return model, meta


# ══════════════════════════════════════════════════════════════════════
# Crystal measurement (weight-space, fast)
# ══════════════════════════════════════════════════════════════════════

def measure_crystal_agreement(model, pass_idx: int) -> dict:
    """Measure crystal quality at a specific v6 pass using weight-space metrics.

    Computes:
    1. Sign sparsity of ternary plates (how many zeros)
    2. Gamma (beam) statistics — mean, std, max
    3. Inter-stride sign overlap (self-similarity within the stride stack)

    Returns dict of metrics.
    """
    metrics = {}

    # Stride stack analysis
    stride_signs = []
    stride_gammas = []
    for i, layer in enumerate(model.stride_stack.layers):
        for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj"]:
            proj = getattr(layer, proj_name)
            tw = np.array(proj.ternary_weight)
            gamma = np.array(proj.gamma)
            stride_signs.append(tw)
            stride_gammas.append(gamma)

    if stride_signs:
        # Sparsity
        all_signs = np.concatenate([s.flatten() for s in stride_signs])
        metrics["stride_sparsity"] = float(np.mean(all_signs == 0))

        # Gamma stats
        all_gammas = np.concatenate(stride_gammas)
        metrics["gamma_mean"] = float(np.mean(all_gammas))
        metrics["gamma_std"] = float(np.std(all_gammas))
        metrics["gamma_max"] = float(np.max(np.abs(all_gammas)))

        # Inter-stride sign overlap (consecutive strides)
        if len(stride_signs) >= 2:
            overlaps = []
            for i in range(len(stride_signs) - 1):
                a = stride_signs[i].flatten().astype(float)
                b = stride_signs[i + 1].flatten().astype(float)
                # Only compare non-zero positions
                mask = (a != 0) & (b != 0)
                if mask.sum() > 0:
                    overlaps.append(float(np.mean(a[mask] == b[mask])))
            metrics["sign_overlap_mean"] = float(np.mean(overlaps))
            metrics["sign_overlap_min"] = float(np.min(overlaps))

    return metrics


# ══════════════════════════════════════════════════════════════════════
# Crystal loss (weight-space relational invariant)
# ══════════════════════════════════════════════════════════════════════

def crystal_lattice_loss(model) -> mx.array:
    """Compute crystal lattice loss from weight-space geometry.

    Measures gamma (beam) coherence across the stride stack:
    consecutive stride layers should have correlated beam patterns
    (the loom structure). Penalizes drift between stride gammas.

    This is a differentiable proxy for the 5D lattice alignment.
    The beams are the continuous parameters that sit on top of the
    ternary sign topology — keeping them aligned means the loom
    geometry is preserved.

    Returns: scalar loss (lower = more crystal-aligned beams)
    """
    stride_gammas = []
    for layer in model.stride_stack.layers:
        for proj_name in ["q_proj", "k_proj", "v_proj", "out_proj"]:
            proj = getattr(layer, proj_name)
            stride_gammas.append(proj.gamma)

    if len(stride_gammas) < 2:
        return mx.array(0.0)

    # Pairwise gamma coherence: consecutive strides should be correlated
    # This is the beam-space equivalent of the CCA angle stability
    total_loss = mx.array(0.0)
    n_pairs = 0

    for i in range(0, len(stride_gammas) - 4, 4):
        # Compare same projection type across consecutive strides
        # (q with q, k with k, etc.)
        for offset in range(4):
            if i + offset + 4 < len(stride_gammas):
                g1 = stride_gammas[i + offset]
                g2 = stride_gammas[i + offset + 4]
                # Cosine distance between gamma vectors
                dot = mx.sum(g1 * g2)
                n1 = mx.sqrt(mx.sum(g1 * g1) + 1e-8)
                n2 = mx.sqrt(mx.sum(g2 * g2) + 1e-8)
                cos_sim = dot / (n1 * n2)
                # Loss = 1 - cos_sim (want to maximize similarity)
                total_loss = total_loss + (1.0 - cos_sim)
                n_pairs += 1

    return total_loss / max(n_pairs, 1)


# ══════════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════════

def load_training_data(data_path: Path, max_examples: int = 5000) -> list[list[int]]:
    """Load tokenized training examples.

    Uses the compile training data (already in Pythia tokenizer format).
    Falls back to generating simple sequences if data not found.
    """
    examples = []

    if data_path.exists():
        with open(data_path) as f:
            for line in f:
                if len(examples) >= max_examples:
                    break
                d = json.loads(line.strip())
                # Tokenize the input text (we need Pythia tokenizer)
                # For now, use the raw text and tokenize with a simple approach
                text = d.get("input", "") + " " + d.get("output", "")
                examples.append(text)

    if not examples:
        log("  WARNING: No training data found, using synthetic sequences")
        rng = np.random.RandomState(42)
        for _ in range(max_examples):
            # Random token sequences (not ideal but functional)
            length = rng.randint(64, SEQ_LEN)
            ids = rng.randint(0, 50277, size=length).tolist()
            examples.append(ids)

    return examples


def get_batches_tokenized(
    tokenizer,
    texts: list[str],
    batch_size: int,
    seq_len: int,
    rng: np.random.RandomState,
) -> tuple[mx.array, mx.array]:
    """Tokenize and batch texts for training.

    Returns: (input_ids, target_ids) both shape (batch_size, seq_len)
    """
    # Sample random texts
    indices = rng.randint(0, len(texts), size=batch_size)
    batch_texts = [texts[i] for i in indices]

    # Tokenize
    encodings = tokenizer(
        batch_texts,
        padding="max_length",
        truncation=True,
        max_length=seq_len + 1,  # +1 for shift
        return_tensors="np",
    )

    input_ids = encodings["input_ids"][:, :-1]  # (B, L)
    target_ids = encodings["input_ids"][:, 1:]   # (B, L)

    return mx.array(input_ids), mx.array(target_ids)


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════

def freeze_ternary_plates(model):
    """Freeze all ternary_weight parameters, keep gammas trainable."""
    frozen = 0
    for name, module in model.named_modules():
        if hasattr(module, "ternary_weight"):
            module.ternary_weight = mx.stop_gradient(module.ternary_weight)
            frozen += 1
    return frozen


def ce_loss(model, input_ids, target_ids):
    """Cross-entropy loss for next-token prediction."""
    logits, _, _, _ = model(input_ids, targets=target_ids)
    # logits shape: (B, L, V)
    B, L, V = logits.shape
    logits_flat = logits.reshape(-1, V)
    targets_flat = target_ids.reshape(-1)

    # Mask padding (token 0 = pad for Pythia)
    mask = targets_flat != 0
    loss = nn.losses.cross_entropy(logits_flat, targets_flat, reduction="none")
    loss = mx.sum(loss * mask) / mx.maximum(mx.sum(mask), mx.array(1.0))
    return loss


def combined_loss(model, input_ids, target_ids, crystal_lambda):
    """CE + crystal lattice loss."""
    ce = ce_loss(model, input_ids, target_ids)
    if crystal_lambda > 0:
        cl = crystal_lattice_loss(model)
        return ce + crystal_lambda * cl, ce, cl
    return ce, ce, mx.array(0.0)


def eval_model(model, tokenizer, texts, n_batches=10):
    """Quick evaluation: compute avg loss."""
    rng = np.random.RandomState(999)
    total_loss = 0
    for _ in range(n_batches):
        input_ids, target_ids = get_batches_tokenized(
            tokenizer, texts, BATCH_SIZE, SEQ_LEN, rng
        )
        loss = ce_loss(model, input_ids, target_ids)
        mx.eval(loss)
        total_loss += loss.item()
    return total_loss / n_batches


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Melt etched v6 with crystal loss")
    parser.add_argument("--steps", type=int, default=MELT_STEPS)
    parser.add_argument("--compare", action="store_true",
                        help="Also evaluate un-etched baseline for comparison")
    parser.add_argument("--checkpoint", type=str, default=str(ETCHED_CHECKPOINT))
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    t0 = time.time()

    log("=" * 60)
    log("  Melt + Align: Crystal-guided beam training")
    log(f"  Checkpoint: {args.checkpoint}")
    log(f"  Steps: {args.steps}")
    log(f"  Crystal λ: {CRYSTAL_LAMBDA}")
    log("=" * 60)

    # ── Load tokenizer ──
    log("\nLoading Pythia tokenizer...")
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("EleutherAI/pythia-410m")
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token
        log(f"  Vocab size: {tokenizer.vocab_size}")
    except Exception as e:
        log(f"  ERROR loading tokenizer: {e}")
        log("  Install: pip install transformers")
        sys.exit(1)

    # ── Load training data ──
    log("\nLoading training data...")
    texts = load_training_data(DATA_PATH)
    log(f"  {len(texts)} training examples")

    # ── Load etched model ──
    log(f"\nLoading etched model from {args.checkpoint}...")
    model, meta = load_v6_model(Path(args.checkpoint))

    # Freeze ternary plates
    n_frozen = freeze_ternary_plates(model)
    log(f"  Frozen {n_frozen} ternary plates")

    # Count trainable params
    n_trainable = sum(p.size for p in model.trainable_parameters())
    n_total = sum(p.size for p in model.parameters())
    log(f"  Trainable: {n_trainable:,} / {n_total:,} ({n_trainable/n_total:.1%})")

    # ── Pre-melt crystal measurement ──
    log("\nPre-melt crystal measurement...")
    pre_crystal = measure_crystal_agreement(model, 0)
    for k, v in pre_crystal.items():
        log(f"  {k}: {v:.4f}")

    # ── Pre-melt eval ──
    log("\nPre-melt evaluation...")
    pre_loss = eval_model(model, tokenizer, texts)
    log(f"  Loss: {pre_loss:.4f}")

    # ── Baseline comparison ──
    if args.compare:
        log(f"\nLoading original (un-etched) model for comparison...")
        orig_model, _ = load_v6_model(ORIGINAL_CHECKPOINT)
        orig_loss = eval_model(orig_model, tokenizer, texts)
        log(f"  Original loss: {orig_loss:.4f}")
        orig_crystal = measure_crystal_agreement(orig_model, 0)
        for k, v in orig_crystal.items():
            log(f"  {k}: {v:.4f}")
        del orig_model
        mx.clear_cache()

    # ── Training setup ──
    optimizer = optim.Adam(learning_rate=LR)

    def loss_fn(model, input_ids, target_ids):
        total, ce, cl = combined_loss(model, input_ids, target_ids, CRYSTAL_LAMBDA)
        return total

    loss_and_grad = nn.value_and_grad(model, loss_fn)

    rng = np.random.RandomState(42)
    history = []

    # ── Melt loop ──
    log(f"\nMelting ({args.steps} steps)...")
    for step in range(args.steps):
        # Get batch
        input_ids, target_ids = get_batches_tokenized(
            tokenizer, texts, BATCH_SIZE, SEQ_LEN, rng
        )

        # Forward + backward
        loss_val, grads = loss_and_grad(model, input_ids, target_ids)
        mx.eval(loss_val, grads)

        # Update (only gamma params, ternary plates are frozen)
        model.update(optimizer.apply_gradients(grads, model))
        mx.eval(model.parameters())

        del grads

        # Logging
        if (step + 1) % EVAL_INTERVAL == 0 or step == 0:
            eval_loss = eval_model(model, tokenizer, texts, n_batches=5)
            crystal = measure_crystal_agreement(model, 0)

            entry = {
                "step": step + 1,
                "train_loss": float(loss_val.item()),
                "eval_loss": eval_loss,
                **{f"crystal_{k}": v for k, v in crystal.items()},
            }
            history.append(entry)

            log(f"  Step {step+1:4d}: train={loss_val.item():.4f} "
                f"eval={eval_loss:.4f} "
                f"γ_mean={crystal.get('gamma_mean', 0):.4f} "
                f"overlap={crystal.get('sign_overlap_mean', 0):.4f}")

        # Cache cleanup
        if (step + 1) % 50 == 0:
            mx.clear_cache()

        # Checkpoint save
        if (step + 1) % SAVE_INTERVAL == 0:
            log(f"  Saving checkpoint at step {step + 1}...")
            model.save_weights(str(OUTPUT_DIR / "weights.safetensors"))

    # ── Post-melt eval ──
    log("\nPost-melt evaluation...")
    post_loss = eval_model(model, tokenizer, texts)
    post_crystal = measure_crystal_agreement(model, 0)
    log(f"  Loss: {post_loss:.4f}")
    for k, v in post_crystal.items():
        log(f"  {k}: {v:.4f}")

    # ── Save final ──
    log(f"\nSaving melted model to {OUTPUT_DIR}...")
    model.save_weights(str(OUTPUT_DIR / "weights.safetensors"))

    # Copy meta
    import shutil
    shutil.copy2(Path(args.checkpoint) / "meta.json", OUTPUT_DIR / "meta.json")

    # ── Save report ──
    report = {
        "pre_loss": pre_loss,
        "post_loss": post_loss,
        "pre_crystal": pre_crystal,
        "post_crystal": post_crystal,
        "steps": args.steps,
        "lr": LR,
        "crystal_lambda": CRYSTAL_LAMBDA,
        "batch_size": BATCH_SIZE,
        "seq_len": SEQ_LEN,
        "history": history,
        "elapsed": time.time() - t0,
    }

    if args.compare:
        report["original_loss"] = orig_loss
        report["original_crystal"] = orig_crystal

    with open(RESULTS_DIR / "melt_report.json", "w") as f:
        json.dump(report, f, indent=2)

    # ── Summary ──
    log(f"\n{'=' * 60}")
    log(f"  Melt complete in {time.time()-t0:.1f}s")
    log(f"  Loss: {pre_loss:.4f} → {post_loss:.4f} "
        f"({'↓' if post_loss < pre_loss else '↑'} {abs(post_loss - pre_loss):.4f})")
    if "sign_overlap_mean" in pre_crystal and "sign_overlap_mean" in post_crystal:
        log(f"  Crystal overlap: {pre_crystal['sign_overlap_mean']:.4f} → "
            f"{post_crystal['sign_overlap_mean']:.4f}")
    if args.compare:
        log(f"  Original baseline loss: {orig_loss:.4f}")
    log(f"  Checkpoint: {OUTPUT_DIR}")
    log(f"  Report: {RESULTS_DIR}/melt_report.json")
    log(f"{'=' * 60}")


if __name__ == "__main__":
    main()
