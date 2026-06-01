"""Load extracted checkpoint into TensorStatechart model.

Connects the statechart data (plates on disk) to the model (computation graph).
Plates are loaded as FROZEN parameters. Attention is initialized for training.

Usage:
    from load_checkpoint import load_statechart
    model = load_statechart("checkpoints/v15-extracted")

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import mlx.core as mx

sys.path.insert(0, str(Path(__file__).parent))
from config import V15Config, Zone, AttnType, COMBINATOR_NAMES
from model import TensorStatechart


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_statechart(
    checkpoint_dir: str | Path,
    config: V15Config | None = None,
    freeze_plates: bool = True,
) -> TensorStatechart:
    """Load extracted checkpoint into a TensorStatechart model.

    Args:
        checkpoint_dir: Path to the extraction output directory.
        config: Optional config override. If None, loads from checkpoint.
        freeze_plates: If True (default), mark plate parameters as non-trainable.

    Returns:
        TensorStatechart with plates loaded, attention initialized.
    """
    ckpt = Path(checkpoint_dir)
    if not ckpt.exists():
        raise FileNotFoundError(f"Checkpoint dir not found: {ckpt}")

    # Load config from checkpoint if not provided
    if config is None:
        with open(ckpt / "config.json") as f:
            cfg_data = json.load(f)
        # Use actual embedding size if available, fall back to config
        actual_vocab = cfg_data.get("vocab_size", 248320)
        embed_path = ckpt / "embedding.npz"
        if embed_path.exists():
            embed_data = np.load(embed_path)
            actual_vocab = embed_data["embedding"].shape[0]
            embed_data.close()
        config = V15Config(
            d_model=cfg_data["d_model"],
            d_ff=cfg_data["d_ff"],
            vocab_size=actual_vocab,
        )

    log(f"Loading statechart from {ckpt}")
    log(f"  d_model={config.d_model}, d_ff={config.d_ff}, vocab={config.vocab_size}")

    # Create model
    model = TensorStatechart(config)

    # ── Load embedding ──
    embed_path = ckpt / "embedding.npz"
    if embed_path.exists():
        embed_data = np.load(embed_path)
        embed_signs = embed_data["embedding"]  # (vocab, d_model//4) packed uint8
        # For now, store as float for the embedding layer
        # Unpack uint8 → int8 → float
        embed_float = _unpack_embedding(embed_signs, config.d_model)
        model.embed.weight = mx.array(embed_float)
        log(f"  Embedding loaded: {embed_float.shape}")
    else:
        log(f"  WARNING: No embedding found, using random init")

    # ── Load stride FFN plates ──
    specs = config.stride_specs()
    for spec in specs:
        stride_path = ckpt / "strides" / f"stride_{spec.index:02d}.npz"
        if not stride_path.exists():
            log(f"  WARNING: Missing {stride_path}, stride {spec.index} uses random init")
            continue

        data = np.load(stride_path)
        stride = model.strides[spec.index]

        # Load each FFN matrix (gate, up, down)
        for matrix_name in ["gate", "up", "down"]:
            plate_module = getattr(stride.ffn, f"{matrix_name}_plate")

            # Plate 1 (always present)
            key1 = f"{matrix_name}_plate1"
            if key1 in data:
                plate_module.plate1 = mx.array(data[key1].astype(np.float32))

            key_g1 = f"{matrix_name}_gamma1"
            if key_g1 in data:
                plate_module.gamma1 = mx.array(data[key_g1].astype(np.float32))

            # Plate 2 (if 2-plate stride)
            if spec.n_plates >= 2:
                key2 = f"{matrix_name}_plate2"
                if key2 in data:
                    plate_module.plate2 = mx.array(data[key2].astype(np.float32))

                key_g2 = f"{matrix_name}_gamma2"
                if key_g2 in data:
                    plate_module.gamma2 = mx.array(data[key_g2].astype(np.float32))

        log(f"  Stride {spec.index:2d} ({spec.zone.name:8s}): FFN plates loaded")

    # ── Load attention sign patterns (as initialization for FULL strides) ──
    for spec in specs:
        if spec.attn_type != AttnType.FULL:
            continue

        attn_path = ckpt / "attention" / f"stride_{spec.index:02d}.npz"
        if not attn_path.exists():
            log(f"  Stride {spec.index:2d}: No attention plates, using random init")
            continue

        data = np.load(attn_path)
        stride = model.strides[spec.index]
        attn = stride.attn

        # Load Q/K/V/O as initialization for the float attention weights
        # These are sign patterns (int8) — scale them as initialization
        scale = 0.02  # Xavier-like scale for d_model=1280
        for proj_name, key in [("q_proj", "q"), ("k_proj", "k"),
                                ("v_proj", "v"), ("o_proj", "o")]:
            if key in data:
                signs = data[key].astype(np.float32)  # (d_out, d_in)
                proj = getattr(attn, proj_name)
                # Initialize weight as scaled sign pattern
                # This gives attention a head start from the teacher's routing topology
                target_shape = proj.weight.shape
                if signs.shape == target_shape:
                    proj.weight = mx.array(signs * scale)
                elif signs.shape[0] >= target_shape[0] and signs.shape[1] >= target_shape[1]:
                    # Truncate if teacher dims > student dims (e.g., full K vs GQA K)
                    proj.weight = mx.array(signs[:target_shape[0], :target_shape[1]] * scale)
                else:
                    log(f"    WARNING: shape mismatch {key}: signs={signs.shape}, target={target_shape}")

        log(f"  Stride {spec.index:2d} ({spec.zone.name:8s}): attention initialized from teacher signs")

    # ── Freeze plates if requested ──
    if freeze_plates:
        frozen_count = 0
        for spec in specs:
            stride = model.strides[spec.index]
            for matrix_name in ["gate", "up", "down"]:
                plate_module = getattr(stride.ffn, f"{matrix_name}_plate")
                plate_module.plate1 = mx.stop_gradient(plate_module.plate1)
                if plate_module.plate2 is not None:
                    plate_module.plate2 = mx.stop_gradient(plate_module.plate2)
                frozen_count += 1
        log(f"  Frozen {frozen_count} plate matrices (trainable: gammas + attention)")

    # ── Tie LM head to embedding ──
    model.lm_head.weight = model.embed.weight
    log(f"  LM head tied to embedding")

    log(f"  Load complete.")
    return model


def _unpack_embedding(packed: np.ndarray, d_model: int) -> np.ndarray:
    """Unpack uint8-packed ternary embedding to float32.

    Packed format: 4 values per byte, 2 bits each.
    Encoding: 00=-1, 01=0, 10=+1

    Args:
        packed: (vocab, d_model//4) uint8
        d_model: target dimension

    Returns:
        (vocab, d_model) float32 with values in {-1, 0, +1}
    """
    vocab, packed_cols = packed.shape
    result = np.zeros((vocab, d_model), dtype=np.float32)

    for i in range(4):
        shift = (3 - i) * 2  # bits 7:6, 5:4, 3:2, 1:0
        vals = ((packed >> shift) & 0x3).astype(np.int8) - 1  # {0,1,2} → {-1,0,+1}
        result[:, i::4] = vals.astype(np.float32)

    return result


def smoke_test(checkpoint_dir: str | Path):
    """Quick test: load model, run one forward pass, check output shape."""
    model = load_statechart(checkpoint_dir)
    config = model.config

    log("\n── Smoke test ──")

    # Create dummy input
    batch_size = 1
    seq_len = 16
    input_ids = mx.array(np.random.randint(0, config.vocab_size, (batch_size, seq_len)))

    log(f"  Input: ({batch_size}, {seq_len})")

    # Forward pass with algedonic monitoring
    result = model(input_ids, return_algedonic=True)

    logits = result["logits"]
    signals = result["algedonic_signals"]

    log(f"  Output logits: {logits.shape}")
    log(f"  Algedonic signals: {len(signals)} strides checked")

    # Check signals
    for stride_idx, zone, signal in signals:
        if signal.name != "OK":
            log(f"    ⚠ Stride {stride_idx} ({zone.name}): {signal.name}")

    ok_count = sum(1 for _, _, s in signals if s.name == "OK")
    log(f"  Health: {ok_count}/{len(signals)} strides OK")

    # Storage estimate
    est = model.storage_estimate_mb()
    log(f"\n  Storage estimate:")
    for k, v in est.items():
        log(f"    {k:12s}: {v:>8.1f} MB")

    log(f"\n  Smoke test {'PASSED ✓' if logits.shape == (batch_size, seq_len, config.vocab_size) else 'FAILED ✗'}")

    return model


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkpoint", default="checkpoints/v15-extracted")
    args = parser.parse_args()
    smoke_test(args.checkpoint)
