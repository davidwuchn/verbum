"""Holographic recording training — Phase 1: Crystal formation from pure lambda.

Protocol:
  1. Generate operation-labeled lambda expressions (K, I, B, C, M)
  2. Tokenize into per-operation batches
  3. For each recording round:
     a. For each operation: forward+backward N batches → accumulate direction
     b. Direct etch: write high-confidence signs onto plate
     c. Train beam only (Q proj + gamma) on mixed lambda data
  4. Phase in prose gradually (Phase 2)

The plate learns KIBC-M hologram from clean signal (pure lambda).
The beam learns to read the plate from gradient descent.
Etching happens during clean-signal exposure, not during noisy prose.

Focusing schedule (lens emulation):
  The etch starts wide and diffuse (low confidence threshold, high beam lr,
  unlimited flips) then progressively focuses like a physical lens being
  narrowed. Late rounds require near-unanimous consensus and make only
  surgical corrections. This forces convergence to a fixed point:

    Early:  wide beam (high lr) + diffuse etch (low threshold) = coarse crystal
    Middle: moderate beam        + moderate etch                = refine structure
    Late:   tight beam (low lr)  + focused etch (high threshold) = surgical
    Final:  pinpoint beam        + single-flip etch              = fixed point

  Schedule parameters are interpolated via cosine annealing between
  start and end values. Cosine gives a slow start (wide stays wide),
  fast middle (main focusing), and slow finish (fine convergence).

Usage:
    uv run python scripts/v12/holographic_train.py
    uv run python scripts/v12/holographic_train.py --n-rounds 20 --batches-per-op 50
    uv run python scripts/v12/holographic_train.py --checkpoint-dir checkpoints/v12-holo

    # Focusing schedule (lens emulation):
    uv run python scripts/v12/holographic_train.py \\
        --beam-lr 1e-4 --beam-lr-end 1e-6 \\
        --confidence-threshold 0.5 --confidence-threshold-end 0.99 \\
        --max-flips-start 0 --max-flips-end 100 \\
        --batches-per-op 50 --batches-per-op-end 200

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import deque
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V12Config
from model import V12Model, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    _walk_ternary_modules,
    TernaryLinear,
    init_direction_accumulators,
    accumulate_direction,
    direct_etch,
    reset_accumulators,
    pack_ternary_mlx,
    unpack_ternary_mlx,
)


# ══════════════════════════════════════════════════════════════════════
# Focusing schedule — lens emulation
# ══════════════════════════════════════════════════════════════════════
#
# Emulates a physical lens being focused: start wide (diffuse etch,
# fast beam), progressively narrow until the etch makes surgical
# single-weight corrections and the beam is locked to precise angles.
#
# Cosine annealing: slow start → fast middle → slow finish.
# This matches the physics: coarse structure forms quickly (wide beam
# is fine), fine structure needs patience (slow convergence at the end).

import math as _math


def focusing_schedule(
    round_idx: int,
    total_rounds: int,
    start_val: float,
    end_val: float,
) -> float:
    """Cosine annealing between start_val and end_val over total_rounds.

    round_idx=0 → start_val, round_idx=total_rounds-1 → end_val.
    Cosine gives slow departure from start, fast middle transition,
    slow arrival at end — matching the lens focusing metaphor.
    """
    if total_rounds <= 1:
        return end_val
    progress = round_idx / (total_rounds - 1)  # 0.0 → 1.0
    # Cosine annealing: 0.5 * (1 + cos(π * progress)) goes 1→0
    cosine_factor = 0.5 * (1.0 + _math.cos(_math.pi * progress))
    return end_val + (start_val - end_val) * cosine_factor


def focusing_schedule_int(
    round_idx: int,
    total_rounds: int,
    start_val: int,
    end_val: int,
) -> int:
    """Integer version of focusing_schedule (for max_flips, batches_per_op)."""
    return round(focusing_schedule(round_idx, total_rounds, float(start_val), float(end_val)))


# ══════════════════════════════════════════════════════════════════════
# Lattice alignment loss — universal lattice as reference beam
# ══════════════════════════════════════════════════════════════════════
#
# The universal lattice map (from build_lattice_map.py) encodes the
# cross-model consensus RDM — the relational geometry that every
# independently trained model agrees on. This IS the universal crystal.
#
# The lattice loss measures how well the small model's representations
# match this universal geometry. It acts as a second reference beam
# alongside the CE loss, burning the universal lattice into the plate.
#
# agreement_mask weights the loss: high-agreement probe pairs (where
# all source models agree) contribute more. Low-agreement pairs
# (model-specific noise) are downweighted.


class LatticeTarget:
    """Pre-loaded universal lattice map for alignment loss."""

    def __init__(self, lattice_path: str, depth_key: str = "0.50"):
        """Load universal lattice from .npz file.

        Args:
            lattice_path: Path to universal_lattice.npz
            depth_key: Which depth fraction to use (default: 0.50 = mid-depth)
        """
        data = np.load(lattice_path)

        key_prefix = f"depth_{depth_key}"
        rdm_key = f"{key_prefix}_consensus_rdm"
        mask_key = f"{key_prefix}_agreement_mask"

        if rdm_key not in data:
            # Try to find available depths
            available = [k.replace("_consensus_rdm", "").replace("depth_", "")
                         for k in data.files if k.endswith("_consensus_rdm")]
            raise ValueError(
                f"Depth {depth_key} not found in lattice. "
                f"Available: {available}"
            )

        self.consensus_rdm = data[rdm_key]       # (N_probes, N_probes) float32
        self.agreement_mask = data[mask_key]       # (N_probes, N_probes) float32
        self.n_probes = self.consensus_rdm.shape[0]

        # Pre-convert to MLX arrays
        self.rdm_mx = mx.array(self.consensus_rdm)
        self.mask_mx = mx.array(self.agreement_mask)

        print(f"  Lattice target loaded: {self.n_probes} probes, "
              f"depth={depth_key}, "
              f"mean_agreement={self.agreement_mask.mean():.4f}",
              file=sys.stderr, flush=True)


def lattice_alignment_loss(
    model: V12Model,
    probe_tokens: list[mx.array],
    probe_indices: np.ndarray,
    lattice: LatticeTarget,
) -> mx.array:
    """Compute lattice alignment loss for a subset of probes.

    1. Forward each probe through the model
    2. Extract last-token hidden state
    3. Compute student RDM (cosine similarity, mean-subtracted)
    4. MSE against consensus RDM, weighted by agreement mask

    Args:
        model: The V12 model
        probe_tokens: Pre-tokenized probe sequences (list of mx.array)
        probe_indices: Indices of probes to use this round (subset)
        lattice: Pre-loaded lattice target

    Returns:
        Scalar loss (lattice alignment MSE, agreement-weighted)
    """
    n = len(probe_indices)

    # Forward each probe, collect last-token hidden states
    hidden_states = []
    for idx in probe_indices:
        tokens = probe_tokens[idx]
        # Forward without targets (inference mode)
        # Shape: (1, T, d_model) → take last token
        logits, aux = model(tokens.reshape(1, -1))
        # Get the last hidden state before output projection
        if hasattr(model, '_last_hidden'):
            h = model._last_hidden[:, -1, :]  # (1, d_model)
        else:
            # Fallback: use the logit projection input
            # This is less ideal but works
            h = mx.stop_gradient(logits[:, -1, :])  # (1, V) — wrong dim
            # If _last_hidden not available, skip this round
            return mx.array(0.0)
        hidden_states.append(h)

    # Stack: (n, d_model)
    h_stack = mx.concatenate(hidden_states, axis=0)  # (n, d_model)

    # L2-normalize for cosine similarity
    h_norm = h_stack / (mx.sqrt(mx.sum(h_stack * h_stack, axis=-1, keepdims=True)) + 1e-8)

    # Student RDM: (n, n)
    student_rdm = h_norm @ h_norm.T

    # Mean-subtract (residual mode)
    student_rdm = student_rdm - mx.mean(student_rdm)

    # Extract target sub-matrix for these probe indices
    target_sub = lattice.rdm_mx[probe_indices][:, probe_indices]   # (n, n)
    mask_sub = lattice.mask_mx[probe_indices][:, probe_indices]     # (n, n)

    # Upper triangle only (RDM is symmetric)
    # Create upper triangle mask
    triu_mask = mx.zeros((n, n))
    for i in range(n):
        for j in range(i + 1, n):
            triu_mask = triu_mask.at[i, j].add(1.0)

    # Weighted MSE on upper triangle
    diff = (student_rdm - target_sub) ** 2
    weighted_diff = diff * mask_sub * triu_mask
    n_pairs = mx.sum(triu_mask)

    loss = mx.sum(weighted_diff) / (n_pairs + 1e-8)
    return loss


def load_lattice_probes(lattice_json_path: str) -> list[str]:
    """Load probe prompts from the lattice metadata JSON."""
    with open(lattice_json_path) as f:
        data = json.load(f)
    return [p["prompt"] for p in data["probes"]]


def tokenize_lattice_probes(
    prompts: list[str],
    max_len: int = 128,
) -> list[mx.array]:
    """Tokenize lattice probes for the V12 model (Qwen3 tokenizer)."""
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    tokens = []
    for prompt in prompts:
        ids = tok.encode(prompt, add_special_tokens=False)
        if len(ids) > max_len:
            ids = ids[:max_len]
        tokens.append(mx.array(ids, dtype=mx.int32))
    del tok
    return tokens


# ══════════════════════════════════════════════════════════════════════
# Lambda corpus — tokenize operations
# ══════════════════════════════════════════════════════════════════════

def build_lambda_corpus(
    n_per_op: int = 3000,
    seq_len: int = 2048,
    seed: int = 42,
) -> dict[str, list[list[int]]]:
    """Generate and tokenize lambda expressions per operation.

    Lambda expressions are short (~15-25 tokens), but the model's stride
    stack requires sequences of at least max_stride + window + 1 = 1033.
    We PACK multiple expressions into each sequence, separated by newlines.
    This gives the model dense, pure-operation signal per batch.

    Returns dict[op_name] → list of packed token sequences (list[int]).
    Each sequence is exactly seq_len tokens.
    """
    from transformers import AutoTokenizer

    # Import lambda generator
    sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
    from verbum.lambda_gen import LambdaGenerator

    print("  Generating lambda corpus...", file=sys.stderr, flush=True)
    gen = LambdaGenerator(seed=seed)
    examples = gen.generate_all(n_per_op=n_per_op)

    print("  Tokenizing...", file=sys.stderr, flush=True)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B")
    sep_tokens = tok.encode("\n", add_special_tokens=False)

    corpus: dict[str, list[list[int]]] = {}
    for op in ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]:
        # Tokenize all expressions for this op
        all_token_seqs = []
        for ex in examples[op]:
            ids = tok.encode(ex.expr, add_special_tokens=False)
            all_token_seqs.append(ids)

        avg_len = np.mean([len(s) for s in all_token_seqs])

        # Pack expressions into sequences of seq_len
        # Concatenate with newline separator, fill sequences densely
        packed_sequences = []
        current_seq: list[int] = []
        expr_idx = 0
        rng_local = np.random.RandomState(seed + hash(op) % 2**31)

        # Create many packed sequences by cycling through expressions
        target_n_sequences = max(100, n_per_op // 10)  # enough for batch sampling
        while len(packed_sequences) < target_n_sequences:
            # Pick next expression (cycle with shuffle)
            if expr_idx >= len(all_token_seqs):
                expr_idx = 0
                rng_local.shuffle(all_token_seqs)

            tokens = all_token_seqs[expr_idx]
            expr_idx += 1

            # Add separator if not start of sequence
            if current_seq:
                current_seq.extend(sep_tokens)

            current_seq.extend(tokens)

            # If we've filled a sequence, pack it
            if len(current_seq) >= seq_len:
                packed_sequences.append(current_seq[:seq_len])
                # Start next sequence with overflow
                current_seq = current_seq[seq_len:]

        # Handle leftover (pad if needed)
        if current_seq and len(current_seq) >= seq_len // 2:
            # Pad to seq_len
            pad_id = tok.eos_token_id or 0
            current_seq = current_seq[:seq_len]
            if len(current_seq) < seq_len:
                current_seq.extend([pad_id] * (seq_len - len(current_seq)))
            packed_sequences.append(current_seq)

        corpus[op] = packed_sequences
        print(f"    {op}: {len(packed_sequences)} packed seqs "
              f"(avg expr len={avg_len:.1f} tok, ~{seq_len // int(avg_len + 1)} exprs/seq)",
              file=sys.stderr, flush=True)

    del tok
    return corpus


def corpus_batch(
    corpus: dict[str, list[list[int]]],
    op: str,
    batch_size: int,
    rng: np.random.RandomState,
    seq_len: int = 2048,
) -> tuple[mx.array, mx.array]:
    """Sample a batch of (input_ids, targets) from an operation's corpus.

    Each corpus sequence is seq_len tokens. We use [:-1] as input and [1:] as target
    (standard next-token prediction shift).
    """
    sequences = corpus[op]
    indices = rng.choice(len(sequences), size=batch_size, replace=True)
    batch = [sequences[i] for i in indices]
    arr = np.array(batch, dtype=np.int32)
    # Standard next-token shift
    input_ids = mx.array(arr[:, :-1])   # (B, seq_len-1)
    targets = mx.array(arr[:, 1:])       # (B, seq_len-1)
    return input_ids, targets


# ══════════════════════════════════════════════════════════════════════
# Loss functions
# ══════════════════════════════════════════════════════════════════════

def ce_loss(model: V12Model, input_ids: mx.array, targets: mx.array) -> mx.array:
    """Standard cross-entropy loss for next-token prediction."""
    logits, _ = model(input_ids, targets=targets)
    # logits: (B, T, V), targets: (B, T)
    B, T, V = logits.shape
    loss = mx.mean(nn.losses.cross_entropy(
        logits.reshape(-1, V),
        targets.reshape(-1),
    ))
    return loss


# ══════════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════════

def holographic_train(cfg: V12Config, args: argparse.Namespace) -> None:
    """Main holographic recording training loop."""

    checkpoint_dir = Path(args.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Model ─────────────────────────────────────────────────
    print("Creating model...", file=sys.stderr, flush=True)
    model = create_model(cfg)
    mx.eval(model.parameters())
    n_params = count_parameters(model)
    print(f"  Parameters: {n_params['total']:,}", file=sys.stderr, flush=True)

    # ── Load pre-trained weights (e.g. from lens burn) ────────
    if args.load_weights:
        print(f"  Loading weights from: {args.load_weights}", file=sys.stderr, flush=True)
        weights = mx.load(args.load_weights)
        # strict=False: skip missing keys (architecture may have expanded)
        model.load_weights(list(weights.items()), strict=False)
        mx.eval(model.parameters())
        print(f"  ✓ Weights loaded ({len(weights)} arrays, strict=False)", file=sys.stderr, flush=True)

    # ── Run lens burn (optional, before holographic recording) ─
    if args.run_lens_burn:
        print(f"  Running lens burn (lens={args.lens_path}, pass={args.lens_pass_idx})...",
              file=sys.stderr, flush=True)
        from lens_burn import burn_lens_into_model
        burn_stats = burn_lens_into_model(
            model, lens_path=args.lens_path,
            pass_idx=args.lens_pass_idx, verbose=True)
        print(f"  ✓ Lens burn complete: {', '.join(burn_stats['burned'])} burned",
              file=sys.stderr, flush=True)

    # Count etchable positions
    n_etchable = sum(
        m.out_features * m.in_features
        for _, m in _walk_ternary_modules(model)
        if isinstance(m, TernaryLinear) and "q_proj" not in _
    )
    # Fix: need path not _
    n_etchable = 0
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear) and "q_proj" not in path:
            n_etchable += mod.out_features * mod.in_features
    print(f"  Etchable positions: {n_etchable:,}", file=sys.stderr, flush=True)

    # ── Lattice target (optional — universal reference beam) ──
    lattice = None
    lattice_probes_tokens = None
    lattice_n_probes = 0
    if getattr(args, 'lattice_map', None):
        lattice_npz = Path(args.lattice_map)
        lattice_json = lattice_npz.parent / "universal_lattice.json"
        print(f"\nLoading lattice map: {lattice_npz}", file=sys.stderr, flush=True)
        lattice = LatticeTarget(str(lattice_npz), depth_key=getattr(args, 'lattice_depth', '0.50'))
        lattice_n_probes = lattice.n_probes

        # Load and tokenize lattice probes
        if lattice_json.exists():
            prompts = load_lattice_probes(str(lattice_json))
            print(f"  Tokenizing {len(prompts)} lattice probes...", file=sys.stderr, flush=True)
            lattice_probes_tokens = tokenize_lattice_probes(prompts)
            print(f"  ✓ Lattice ready: {lattice_n_probes} probes, "
                  f"λ={getattr(args, 'lattice_lambda', 0.1)}",
                  file=sys.stderr, flush=True)
        else:
            print(f"  WARNING: {lattice_json} not found, lattice loss disabled",
                  file=sys.stderr, flush=True)
            lattice = None

    # ── Lambda corpus ─────────────────────────────────────────
    print("\nBuilding lambda corpus...", file=sys.stderr, flush=True)
    corpus = build_lambda_corpus(
        n_per_op=args.n_examples,
        seq_len=cfg.seq_len,
        seed=42,
    )

    # ── Optimizer (beam only during beam phase) ───────────────
    optimizer = optim.Adam(learning_rate=args.beam_lr)
    mx.eval(optimizer.state)

    # ── Direction accumulators ────────────────────────────────
    accumulators = init_direction_accumulators(model)
    print(f"  Direction accumulators: {len(accumulators)}", file=sys.stderr, flush=True)

    # ── Loss + grad function ──────────────────────────────────
    loss_and_grad = nn.value_and_grad(model, ce_loss)

    # ── Training state ────────────────────────────────────────
    rng = np.random.RandomState(42)
    start_round = getattr(args, '_resume_round', 0)
    total_flips = getattr(args, '_resume_total_flips', 0)
    round_logs = []

    # ── Focusing schedule parameters ─────────────────────────
    # End values default to start values (no schedule = current behavior)
    beam_lr_start = args.beam_lr
    beam_lr_end = getattr(args, 'beam_lr_end', None) or beam_lr_start
    conf_start = args.confidence_threshold
    conf_end = getattr(args, 'confidence_threshold_end', None) or conf_start
    max_flips_start = getattr(args, 'max_flips_start', None)  # None = unlimited
    max_flips_end = getattr(args, 'max_flips_end', None)
    max_flips_frac_start = getattr(args, 'max_flips_frac', None)  # None = disabled
    max_flips_frac_end = getattr(args, 'max_flips_frac_end', None)
    batches_start = args.batches_per_op
    batches_end = getattr(args, 'batches_per_op_end', None) or batches_start
    beam_steps_start = args.beam_steps
    beam_steps_end = getattr(args, 'beam_steps_end', None) or beam_steps_start

    has_focus_schedule = (
        beam_lr_end != beam_lr_start
        or conf_end != conf_start
        or max_flips_start is not None
        or max_flips_frac_start is not None
        or batches_end != batches_start
        or beam_steps_end != beam_steps_start
    )

    print(f"\n{'='*72}", file=sys.stderr, flush=True)
    print(f"  Holographic Recording — Phase 1", file=sys.stderr, flush=True)
    if start_round > 0:
        print(f"  Resuming from round: {start_round}", file=sys.stderr, flush=True)
    print(f"  Rounds: {start_round + 1} → {start_round + args.n_rounds}", file=sys.stderr, flush=True)
    print(f"  Batches per op per round: {args.batches_per_op}", file=sys.stderr, flush=True)
    print(f"  Beam training steps per round: {args.beam_steps}", file=sys.stderr, flush=True)
    print(f"  Confidence threshold: {args.confidence_threshold}", file=sys.stderr, flush=True)
    if has_focus_schedule:
        print(f"  ── Focusing Schedule (lens emulation) ──", file=sys.stderr, flush=True)
        print(f"  Beam LR:     {beam_lr_start:.1e} → {beam_lr_end:.1e}", file=sys.stderr, flush=True)
        print(f"  Confidence:  {conf_start:.3f} → {conf_end:.3f}", file=sys.stderr, flush=True)
        if max_flips_start is not None:
            print(f"  Max flips:   {max_flips_start:,} → {max_flips_end:,}", file=sys.stderr, flush=True)
        else:
            print(f"  Max flips:   unlimited → {max_flips_end:,}" if max_flips_end else
                  f"  Max flips:   unlimited", file=sys.stderr, flush=True)
        if max_flips_frac_start is not None:
            frac_end_str = f"{max_flips_frac_end:.3f}" if max_flips_frac_end else f"{max_flips_frac_start:.3f}"
            print(f"  Flip frac:   {max_flips_frac_start:.3f} → {frac_end_str} (proportional cap)",
                  file=sys.stderr, flush=True)
        print(f"  Batches/op:  {batches_start} → {batches_end}", file=sys.stderr, flush=True)
        print(f"  Beam steps:  {beam_steps_start} → {beam_steps_end}", file=sys.stderr, flush=True)
    print(f"{'='*72}\n", file=sys.stderr, flush=True)

    t_start = time.time()

    for round_idx in range(start_round, start_round + args.n_rounds):
        round_t0 = time.time()
        round_flips = {}

        # ── Focusing schedule: compute this round's parameters ──
        # Schedule position is relative to the TOTAL run, not just
        # remaining rounds. If resuming from round 15 with 35 total,
        # round 15 is at position 15/35 in the schedule.
        total_run_rounds = start_round + args.n_rounds
        sched_pos = round_idx  # absolute position in the schedule
        sched_total = total_run_rounds

        round_beam_lr = focusing_schedule(
            sched_pos, sched_total, beam_lr_start, beam_lr_end)
        round_confidence = focusing_schedule(
            sched_pos, sched_total, conf_start, conf_end)
        round_batches = focusing_schedule_int(
            sched_pos, sched_total, batches_start, batches_end)
        round_beam_steps = focusing_schedule_int(
            sched_pos, sched_total, beam_steps_start, beam_steps_end)

        # Max flips schedule: None→None (unlimited throughout) or int→int
        if max_flips_start is not None and max_flips_end is not None:
            round_max_flips = focusing_schedule_int(
                sched_pos, sched_total, max_flips_start, max_flips_end)
        elif max_flips_end is not None:
            # Start unlimited, ramp to end value in second half
            half = sched_total // 2
            if sched_pos < half:
                round_max_flips = None
            else:
                round_max_flips = focusing_schedule_int(
                    sched_pos - half, sched_total - half,
                    max_flips_end * 100, max_flips_end)
        else:
            round_max_flips = args.max_flips_per_op  # original behavior

        # Proportional flip cap schedule
        if max_flips_frac_start is not None:
            frac_end = max_flips_frac_end if max_flips_frac_end is not None else max_flips_frac_start
            round_max_flips_frac = focusing_schedule(
                sched_pos, sched_total, max_flips_frac_start, frac_end)
        else:
            round_max_flips_frac = None

        # Update optimizer LR for this round
        optimizer.learning_rate = mx.array(round_beam_lr)

        if has_focus_schedule:
            frac_str = f" frac={round_max_flips_frac:.3f}" if round_max_flips_frac is not None else ""
            print(
                f"  Round {round_idx+1:3d} | LENS | "
                f"beam_lr={round_beam_lr:.2e} "
                f"conf={round_confidence:.4f} "
                f"batches={round_batches} "
                f"beam_steps={round_beam_steps} "
                f"max_flips={round_max_flips if round_max_flips is not None else '∞'}"
                f"{frac_str}",
                file=sys.stderr, flush=True,
            )

        # ══════════════════════════════════════════════════════
        # Phase A: EXPOSE — accumulate directions from ALL ops
        # ══════════════════════════════════════════════════════
        #
        # Cross-op consensus: accumulate gradient directions from
        # all 8 operations into the SAME accumulators. Positions
        # where multiple ops agree on the sign direction will have
        # high confidence. Positions where ops disagree will cancel
        # out (low confidence → not etched). This eliminates the
        # tug-of-war where sequential per-op etching overwrites
        # the previous op's work.
        #
        # The resulting etch writes the CONSENSUS structure — the
        # interference pattern from all operations simultaneously.
        # This IS holographic recording: multiple reference beams,
        # one exposure, one development.

        ops = ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]
        rng.shuffle(ops)

        # Single reset at the start of each round (NOT per-op)
        reset_accumulators(accumulators)

        op_losses_all = {}
        for op in ops:
            op_losses = []
            for batch_idx in range(round_batches):
                input_ids, targets = corpus_batch(
                    corpus, op, batch_size=cfg.batch_size, rng=rng
                )

                # Forward + backward (but DON'T update weights)
                loss_val, grads = loss_and_grad(model, input_ids, targets)
                mx.eval(loss_val, grads)
                op_losses.append(float(loss_val.item()))

                # Accumulate direction (all ops into same accumulators)
                accumulate_direction(model, grads, accumulators)

                # Release grad references to free Metal buffers.
                # Without this, Python holds references to hundreds of
                # intermediate MLX arrays per step, accumulating Metal
                # buffer objects until hitting the 499K resource limit.
                del loss_val, grads, input_ids, targets

            avg_loss = np.mean(op_losses)
            op_losses_all[op] = avg_loss
            print(
                f"  Round {round_idx+1:3d} | {op:4s} | "
                f"loss={avg_loss:.4f} | exposed",
                file=sys.stderr, flush=True,
            )

        # Release accumulated Metal buffers after exposure phase.
        # Each op × batch creates ~100s of Metal buffer objects in the
        # computation graph; clear_cache releases those back to the system.
        mx.clear_cache()

        # ── LATTICE: accumulate universal lattice alignment signal ──
        # The lattice loss is a second reference beam alongside the CE loss.
        # It measures how well the model's relational geometry matches the
        # cross-model consensus. Both signals feed the same accumulators.
        lattice_loss_val = 0.0
        if lattice is not None and lattice_probes_tokens is not None:
            lattice_lambda = getattr(args, 'lattice_lambda', 0.1)
            n_lattice_probes = min(
                getattr(args, 'lattice_probes_per_round', 50),
                lattice_n_probes,
            )

            # Sample probe subset for this round
            probe_indices = rng.choice(
                lattice_n_probes, size=n_lattice_probes, replace=False
            )

            # Compute lattice alignment loss
            def lattice_loss_fn(model):
                return lattice_alignment_loss(
                    model, lattice_probes_tokens, probe_indices, lattice
                ) * lattice_lambda

            lattice_loss_and_grad = nn.value_and_grad(model, lattice_loss_fn)
            lat_loss, lat_grads = lattice_loss_and_grad(model)
            mx.eval(lat_loss, lat_grads)
            lattice_loss_val = float(lat_loss.item())

            # Accumulate lattice gradients into same direction accumulators
            accumulate_direction(model, lat_grads, accumulators)

            # Release lattice grad references and clear Metal buffers
            del lat_loss, lat_grads, lattice_loss_and_grad
            mx.clear_cache()

            print(
                f"  Round {round_idx+1:3d} | LATTICE | "
                f"loss={lattice_loss_val:.6f} | "
                f"probes={n_lattice_probes}",
                file=sys.stderr, flush=True,
            )

        # ── ETCH: write cross-op consensus hologram ───────────
        # Only positions where the AGGREGATE direction across all
        # 8 ops (+ lattice if enabled) is confident get flipped.
        # Contested positions (where signals disagree) stay put.
        etch_result = direct_etch(
            model, accumulators,
            confidence_threshold=round_confidence,
            max_flips=round_max_flips,
            max_flips_frac=round_max_flips_frac,
        )

        n_flipped = etch_result["total_flipped"]
        total_flips += n_flipped
        round_flips["consensus"] = n_flipped

        # Re-freeze after etch
        freeze_ternary_weights(model)
        restore_ternary(model)

        # Clear Metal buffers after etch — the numpy↔MLX conversions
        # in direct_etch create temporary buffers that should be released
        # before beam training starts.
        mx.clear_cache()

        # ── Confidence diagnostics ─────────────────────────────
        cs = etch_result.get("confidence_stats", {})
        conf_detail = ""
        if cs:
            throttle = cs.get("throttle_ratio", 1.0)
            p50 = cs.get("candidate_p50", 0)
            p90 = cs.get("candidate_p90", 0)
            p99 = cs.get("candidate_p99", 0)
            conf_detail = (
                f" | conf_p50={p50:.3f} p90={p90:.3f} p99={p99:.3f}"
                f" | throttle={throttle:.0f}x"
            )
            if "effective_conf_floor" in cs:
                conf_detail += f" | eff_floor={cs['effective_conf_floor']:.4f}"
            # Print histogram as a compact bar
            hist = cs.get("histogram_counts", [])
            if hist:
                # Normalize histogram for a visual bar
                max_h = max(hist) if max(hist) > 0 else 1
                bar = "".join(
                    "█" if h > max_h * 0.5 else "▄" if h > max_h * 0.1 else "·"
                    for h in hist
                )
                conf_detail += f" | dist=[{bar}]"

        print(
            f"  Round {round_idx+1:3d} | ETCH | "
            f"flips={n_flipped:,} | "
            f"candidates={etch_result['total_candidates']:,}"
            f"{conf_detail}",
            file=sys.stderr, flush=True,
        )

        # ══════════════════════════════════════════════════════
        # Phase B: BEAM TRAINING — beam adapts to new plate
        # ══════════════════════════════════════════════════════

        beam_losses = []
        for step in range(round_beam_steps):
            # Mixed lambda data (all operations)
            op = rng.choice(["K", "I", "B", "C", "M", "D", "Y", "WHNF"])
            input_ids, targets = corpus_batch(
                corpus, op, batch_size=cfg.batch_size, rng=rng
            )

            loss_val, grads = loss_and_grad(model, input_ids, targets)
            mx.eval(loss_val, grads)

            # Zero ternary gradients (plate is frozen during beam phase)
            grads = zero_ternary_grads(model, grads)

            # Optimizer step (only affects gamma, norms, embeddings, Q proj)
            optimizer.update(model, grads)
            mx.eval(model.parameters(), optimizer.state)
            restore_ternary(model)

            beam_losses.append(float(loss_val.item()))

            # Release references and periodically clear Metal buffer cache.
            # Beam training runs 200-500 steps; without clearing, Metal
            # buffer objects accumulate from each step's forward/backward.
            del loss_val, grads, input_ids, targets
            if (step + 1) % 50 == 0:
                mx.clear_cache()

        avg_beam_loss = np.mean(beam_losses) if beam_losses else 0.0

        # Final Metal cache clear at round boundary — ensures we start
        # each round with a clean buffer pool. This is the primary defense
        # against the 499K Metal resource limit error.
        mx.clear_cache()

        # ── Round summary ─────────────────────────────────────
        round_dt = time.time() - round_t0
        round_total_flips = sum(round_flips.values())

        print(
            f"  Round {round_idx+1:3d} | BEAM | "
            f"loss={avg_beam_loss:.4f} | "
            f"round_flips={round_total_flips:,} | "
            f"total_flips={total_flips:,} | "
            f"{round_dt:.1f}s",
            file=sys.stderr, flush=True,
        )
        print("", file=sys.stderr, flush=True)

        # ── Log ───────────────────────────────────────────────
        round_log = {
            "round": round_idx + 1,
            "timestamp": time.time(),
            "elapsed": time.time() - t_start,
            "flips_per_op": round_flips,
            "round_total_flips": round_total_flips,
            "cumulative_flips": total_flips,
            "beam_loss": avg_beam_loss,
            "round_time": round_dt,
            # Schedule state (for analysis)
            "beam_lr": round_beam_lr,
            "confidence_threshold": round_confidence,
            "batches_per_op": round_batches,
            "beam_steps": round_beam_steps,
            "max_flips": round_max_flips,
            "lattice_loss": lattice_loss_val,
            # Confidence diagnostics (throttle analysis)
            "etch_candidates": etch_result.get("total_candidates", 0),
            "confidence_stats": etch_result.get("confidence_stats", {}),
            "max_flips_frac": round_max_flips_frac,
        }
        round_logs.append(round_log)

        # Append to JSONL
        with open(checkpoint_dir / "holo_log.jsonl", "a") as f:
            f.write(json.dumps(round_log) + "\n")

        # ── Checkpoint (periodic) ─────────────────────────────
        if (round_idx + 1) % args.checkpoint_every == 0:
            ckpt_path = checkpoint_dir / f"round_{round_idx+1:04d}"
            ckpt_path.mkdir(parents=True, exist_ok=True)
            # Save ALL model weights (trainable + ternary plates)
            flat = dict(tree_flatten(model.parameters()))
            mx.savez(str(ckpt_path / "weights.npz"), **flat)
            # Save state
            state = {
                "round": round_idx + 1,
                "total_flips": total_flips,
                "args": vars(args),
            }
            with open(ckpt_path / "state.json", "w") as f:
                json.dump(state, f, indent=2)
            print(f"  💾 Checkpoint: {ckpt_path}", file=sys.stderr, flush=True)

    # ── Final summary ─────────────────────────────────────────
    elapsed = time.time() - t_start
    print(f"\n{'='*72}", file=sys.stderr, flush=True)
    print(f"  Holographic Recording Complete", file=sys.stderr, flush=True)
    print(f"  Rounds: {args.n_rounds}", file=sys.stderr, flush=True)
    print(f"  Total flips: {total_flips:,} / {n_etchable:,} "
          f"({total_flips/max(n_etchable,1)*100:.1f}%)", file=sys.stderr, flush=True)
    print(f"  Final beam loss: {avg_beam_loss:.4f}", file=sys.stderr, flush=True)
    print(f"  Elapsed: {elapsed:.0f}s", file=sys.stderr, flush=True)
    print(f"{'='*72}", file=sys.stderr, flush=True)

    # Save final results
    with open(checkpoint_dir / "holo_results.json", "w") as f:
        json.dump({
            "n_rounds": args.n_rounds,
            "total_flips": total_flips,
            "n_etchable": n_etchable,
            "final_beam_loss": avg_beam_loss,
            "elapsed_sec": elapsed,
            "rounds": round_logs,
        }, f, indent=2)

    print(f"\n  💾 Results: {checkpoint_dir / 'holo_results.json'}", file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Holographic recording training — crystal formation from pure lambda"
    )
    parser.add_argument("--checkpoint-dir", default="checkpoints/v12-holo",
                        help="Directory for checkpoints and logs")
    parser.add_argument("--n-rounds", type=int, default=20,
                        help="Number of recording rounds (each = expose all ops + beam train)")
    parser.add_argument("--n-examples", type=int, default=3000,
                        help="Lambda examples per operation")
    parser.add_argument("--batches-per-op", type=int, default=50,
                        help="Batches to accumulate per operation per round")
    parser.add_argument("--beam-steps", type=int, default=200,
                        help="Beam training steps per round (after all ops etched)")
    parser.add_argument("--beam-lr", type=float, default=1e-4,
                        help="Learning rate for beam training phase (start value if --beam-lr-end set)")
    parser.add_argument("--confidence-threshold", type=float, default=0.5,
                        help="Min confidence to flip a sign (start value if --confidence-threshold-end set)")
    parser.add_argument("--max-flips-per-op", type=int, default=None,
                        help="Cap on flips per round (None=unlimited). Static unless --max-flips-start/end set.")
    parser.add_argument("--checkpoint-every", type=int, default=5,
                        help="Save checkpoint every N rounds")

    # ── Focusing schedule (lens emulation) ────────────────────
    # All schedule args are optional. If not set, the corresponding
    # parameter stays constant across rounds (backward compatible).
    focus = parser.add_argument_group("focusing schedule (lens emulation)")
    focus.add_argument("--beam-lr-end", type=float, default=None,
                       help="Beam LR at final round (cosine anneal from --beam-lr). "
                            "e.g. 1e-6 for tight beam lock.")
    focus.add_argument("--confidence-threshold-end", type=float, default=None,
                       help="Confidence threshold at final round (cosine anneal from "
                            "--confidence-threshold). e.g. 0.99 for near-unanimous consensus.")
    focus.add_argument("--max-flips-start", type=int, default=None,
                       help="Max flips at round 0 (None=unlimited). Anneals to --max-flips-end.")
    focus.add_argument("--max-flips-end", type=int, default=None,
                       help="Max flips at final round. If --max-flips-start is None, "
                            "unlimited for first half then anneals to this value.")
    focus.add_argument("--batches-per-op-end", type=int, default=None,
                       help="Batches per op at final round (cosine anneal from --batches-per-op). "
                            "More batches = better statistics = higher confidence late.")
    focus.add_argument("--beam-steps-end", type=int, default=None,
                       help="Beam training steps at final round (cosine anneal from --beam-steps). "
                            "More steps late = beam locks to precise read angles.")
    focus.add_argument("--max-flips-frac", type=float, default=None,
                       help="Proportional flip cap: flip this fraction of candidates (start). "
                            "e.g. 0.5 = flip top 50%% of confident candidates. "
                            "Overrides --max-flips-start/end when set.")
    focus.add_argument("--max-flips-frac-end", type=float, default=None,
                       help="Proportional flip cap at final round (cosine anneal from --max-flips-frac). "
                            "e.g. 0.01 = top 1%% of candidates at convergence. "
                            "Requires --max-flips-frac.")

    # ── Lattice alignment (universal reference beam) ──────────
    lattice_group = parser.add_argument_group("lattice alignment (universal reference beam)")
    lattice_group.add_argument("--lattice-map", type=str, default=None,
                               help="Path to universal_lattice.npz from build_lattice_map.py. "
                                    "If not set, no lattice loss is applied (backward compatible).")
    lattice_group.add_argument("--lattice-lambda", type=float, default=0.1,
                               help="Weight of lattice alignment loss relative to CE (default: 0.1)")
    lattice_group.add_argument("--lattice-probes-per-round", type=int, default=50,
                               help="Number of lattice probes to sample per round (default: 50)")
    lattice_group.add_argument("--lattice-depth", type=str, default="0.50",
                               help="Which depth fraction from the lattice map to use (default: 0.50)")
    parser.add_argument("--load-weights", type=str, default=None,
                        help="Path to .npz weights to load before training "
                             "(e.g. from lens_burn.py output)")
    parser.add_argument("--run-lens-burn", action="store_true",
                        help="Run lens burn before holographic training "
                             "(writes teacher directions into combinator mirrors)")
    parser.add_argument("--lens-path", type=str, default="lens/warped_lens.npz",
                        help="Path to warped lens .npz (used with --run-lens-burn)")
    parser.add_argument("--lens-pass-idx", type=int, default=3,
                        help="Which pass's directions to use for lens burn (default: 3=apex)")
    parser.add_argument("--resume", type=str, default=None,
                        help="Resume from checkpoint dir (e.g. checkpoints/v12-holo-8op/round_0015). "
                             "Loads weights and continues round numbering.")

    args = parser.parse_args()

    # --resume implies --load-weights from that checkpoint
    if args.resume:
        resume_dir = Path(args.resume)
        weights_path = resume_dir / "weights.npz"
        state_path = resume_dir / "state.json"
        if not weights_path.exists():
            print(f"ERROR: {weights_path} not found", file=sys.stderr)
            sys.exit(1)
        args.load_weights = str(weights_path)
        # Load resume state for round numbering
        if state_path.exists():
            import json as _json
            with open(state_path) as f:
                resume_state = _json.load(f)
            args._resume_round = resume_state.get("round", 0)
            args._resume_total_flips = resume_state.get("total_flips", 0)
            print(f"Resuming from round {args._resume_round}, "
                  f"total_flips={args._resume_total_flips:,}", file=sys.stderr)
        else:
            args._resume_round = 0
            args._resume_total_flips = 0

    # Config — seq_len must be >= max_stride + window + 1 = 1033
    cfg = V12Config()
    cfg.seq_len = 2048  # Packed lambda sequences (many expressions per seq)
    cfg.batch_size = 2   # Smaller batch for memory (2 × 2048 = 4096 tokens/step)

    print("Holographic Training — Phase 1: Crystal Formation", file=sys.stderr)
    print(f"  Config: seq_len={cfg.seq_len}, batch_size={cfg.batch_size}", file=sys.stderr)
    print("", file=sys.stderr)

    holographic_train(cfg, args)


if __name__ == "__main__":
    main()
