#!/usr/bin/env python3
"""Holographic Extraction Experiment — Can ternary signs from a large model
serve as a useful frozen knowledge store for a small trained reader?

Hypothesis: The sign topology of K, V, O projections (the "holographic plate")
contains the universal combinator structure. A model with frozen ternary plates
and trainable beam (Q) should converge faster and to lower loss than one with
random ternary plates.

Experiment:
  1. Extract sign(K), sign(V), sign(O), sign(gate), sign(up) from Qwen3-14B
  2. Build a thin model (subset of layers) with those frozen ternary matrices
  3. Train only: Q projections, down_proj, embeddings, norms, output head
  4. Compare against: same architecture with RANDOM ternary plates

Source: Qwen3-14B (Apache-2.0, same tokenizer as our Dolma shards)
Data: Dolma shards (Qwen3-tokenized, 50M tokens each)

Architecture (extracted model):
  - N layers (default 10, every 4th from source = layers 0,4,8,...,36)
  - d_model = 5120 (same as source)
  - n_heads = 40, n_kv_heads = 8 (GQA, same as source)
  - Frozen: K, V, O projections (ternary signs from source)
  - Frozen: gate_proj, up_proj (ternary signs from source FFN)
  - Trainable: Q projection, down_proj, embeddings, RMSNorm, output head

Usage:
    # Full experiment (extracted vs random)
    uv run python scripts/explore/extract_and_train.py

    # Quick test (fewer steps)
    uv run python scripts/explore/extract_and_train.py --steps 200 --eval-every 50

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoConfig

# ══════════════════════════════════════════════════════════════════
# Configuration
# ══════════════════════════════════════════════════════════════════

SOURCE_MODEL = "Qwen/Qwen3-14B"
DATA_DIR = Path("/Users/mwhitford/data/fractal-bitnet/shards-qwen3")
OUTPUT_DIR = Path("results/holographic-extraction")

# Architecture
N_EXTRACT_LAYERS = 10  # How many layers to extract
LAYER_STRIDE = 4       # Every 4th layer: 0, 4, 8, 12, 16, 20, 24, 28, 32, 36
D_MODEL = 5120
N_HEADS = 40
N_KV_HEADS = 8
HEAD_DIM = D_MODEL // N_HEADS  # 128
VOCAB_SIZE = 151936  # Qwen3 tokenizer
INTERMEDIATE_SIZE = 17408  # Qwen3-14B FFN intermediate

# Training
BATCH_SIZE = 2
SEQ_LEN = 512
LR = 3e-4
WEIGHT_DECAY = 0.01


# ══════════════════════════════════════════════════════════════════
# Ternary layer — frozen sign matrix with trainable scale
# ══════════════════════════════════════════════════════════════════


class TernaryFrozen(nn.Module):
    """A frozen ternary matrix with a single trainable scale factor.

    Stores sign(W) as int8, applies as: output = input @ (signs * scale)
    The signs never change. Only the per-output-channel scale is trained.
    """

    def __init__(self, in_features: int, out_features: int, signs: torch.Tensor | None = None):
        super().__init__()
        if signs is not None:
            assert signs.shape == (out_features, in_features)
            self.register_buffer("signs", signs.to(torch.int8))
        else:
            # Random ternary initialization
            random_signs = torch.randint(-1, 2, (out_features, in_features), dtype=torch.int8)
            self.register_buffer("signs", random_signs)

        # Per-output-channel scale (trainable)
        self.scale = nn.Parameter(torch.ones(out_features) * (1.0 / in_features**0.5))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        # x: (..., in_features)
        # signs: (out_features, in_features), scale: (out_features,)
        # Compute: x @ signs.T * scale
        W_effective = self.signs.float() * self.scale.unsqueeze(1)
        return F.linear(x, W_effective)


# ══════════════════════════════════════════════════════════════════
# Extracted model architecture
# ══════════════════════════════════════════════════════════════════


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        norm = torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)
        return x * norm * self.weight


class ExtractedAttention(nn.Module):
    """Attention with frozen ternary K,V,O and trainable Q."""

    def __init__(self, d_model: int, n_heads: int, n_kv_heads: int, head_dim: int,
                 k_signs=None, v_signs=None, o_signs=None):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.head_dim = head_dim
        self.n_kv_groups = n_heads // n_kv_heads

        # Trainable Q projection (the beam)
        self.q_proj = nn.Linear(d_model, n_heads * head_dim, bias=False)

        # Frozen ternary K, V, O (the plate)
        kv_dim = n_kv_heads * head_dim
        self.k_proj = TernaryFrozen(d_model, kv_dim, signs=k_signs)
        self.v_proj = TernaryFrozen(d_model, kv_dim, signs=v_signs)
        self.o_proj = TernaryFrozen(n_heads * head_dim, d_model, signs=o_signs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        B, L, _ = x.shape

        q = self.q_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)

        # GQA: expand KV
        if self.n_kv_groups > 1:
            k = k.repeat_interleave(self.n_kv_groups, dim=1)
            v = v.repeat_interleave(self.n_kv_groups, dim=1)

        # Scaled dot-product attention (with causal mask)
        attn_out = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        attn_out = attn_out.transpose(1, 2).contiguous().view(B, L, -1)

        return self.o_proj(attn_out)


class ExtractedFFN(nn.Module):
    """FFN with frozen ternary gate/up and trainable down."""

    def __init__(self, d_model: int, intermediate: int,
                 gate_signs=None, up_signs=None):
        super().__init__()
        # Frozen ternary gate and up (the plate)
        self.gate_proj = TernaryFrozen(d_model, intermediate, signs=gate_signs)
        self.up_proj = TernaryFrozen(d_model, intermediate, signs=up_signs)
        # Trainable down projection (the reader)
        self.down_proj = nn.Linear(intermediate, d_model, bias=False)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        return self.down_proj(F.silu(self.gate_proj(x)) * self.up_proj(x))


class ExtractedLayer(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads, head_dim, intermediate,
                 k_signs=None, v_signs=None, o_signs=None,
                 gate_signs=None, up_signs=None):
        super().__init__()
        self.input_norm = RMSNorm(d_model)
        self.attn = ExtractedAttention(d_model, n_heads, n_kv_heads, head_dim,
                                       k_signs, v_signs, o_signs)
        self.post_attn_norm = RMSNorm(d_model)
        self.ffn = ExtractedFFN(d_model, intermediate, gate_signs, up_signs)

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        x = x + self.attn(self.input_norm(x))
        x = x + self.ffn(self.post_attn_norm(x))
        return x


class ExtractedModel(nn.Module):
    """A thin model with frozen ternary plates from a source LLM."""

    def __init__(self, n_layers, d_model, n_heads, n_kv_heads, head_dim,
                 intermediate, vocab_size, layer_signs=None):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList()

        for i in range(n_layers):
            signs = layer_signs[i] if layer_signs else {}
            self.layers.append(ExtractedLayer(
                d_model, n_heads, n_kv_heads, head_dim, intermediate,
                k_signs=signs.get("k"),
                v_signs=signs.get("v"),
                o_signs=signs.get("o"),
                gate_signs=signs.get("gate"),
                up_signs=signs.get("up"),
            ))

        self.norm = RMSNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)

        # Tie embeddings
        self.lm_head.weight = self.embed.weight

    def forward(self, input_ids: torch.Tensor) -> torch.Tensor:
        x = self.embed(input_ids)
        for layer in self.layers:
            x = layer(x)
        x = self.norm(x)
        return self.lm_head(x)

    def count_params(self):
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen_signs = sum(b.numel() for b in self.buffers() if b.dtype == torch.int8)
        return {"total": total, "trainable": trainable, "frozen_ternary": frozen_signs}


# ══════════════════════════════════════════════════════════════════
# Sign extraction from source model
# ══════════════════════════════════════════════════════════════════


def extract_signs(model_name: str, layer_indices: list[int], device: str = "cpu") -> list[dict]:
    """Extract sign matrices from source model's attention + FFN layers.

    Returns list of dicts, one per extracted layer:
        {"k": Tensor, "v": Tensor, "o": Tensor, "gate": Tensor, "up": Tensor}
    All tensors are int8 with values in {-1, 0, 1}.
    """
    print(f"  Extracting signs from {model_name}...", file=sys.stderr)
    print(f"  Layers: {layer_indices}", file=sys.stderr)

    config = AutoConfig.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    all_signs = []
    for li in layer_indices:
        layer = model.model.layers[li]
        attn = layer.self_attn
        ffn = layer.mlp

        signs = {
            "k": torch.sign(attn.k_proj.weight.float()).to(torch.int8).cpu(),
            "v": torch.sign(attn.v_proj.weight.float()).to(torch.int8).cpu(),
            "o": torch.sign(attn.o_proj.weight.float()).to(torch.int8).cpu(),
            "gate": torch.sign(ffn.gate_proj.weight.float()).to(torch.int8).cpu(),
            "up": torch.sign(ffn.up_proj.weight.float()).to(torch.int8).cpu(),
        }
        all_signs.append(signs)
        print(f"    L{li}: K={signs['k'].shape}, V={signs['v'].shape}, "
              f"O={signs['o'].shape}, gate={signs['gate'].shape}", file=sys.stderr)

    # Free source model memory
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return all_signs


# ══════════════════════════════════════════════════════════════════
# Data loading (reuse Dolma shards)
# ══════════════════════════════════════════════════════════════════


class SimpleDataLoader:
    """Minimal data loader from pre-tokenized Dolma shards."""

    def __init__(self, data_dir: Path, batch_size: int, seq_len: int,
                 shard_start: int = 0, shard_end: int = 4, seed: int = 42):
        self.batch_size = batch_size
        self.seq_len = seq_len
        self.rng = np.random.RandomState(seed)

        shards = sorted(data_dir.glob("shard_*.npy"))
        self.shards = shards[shard_start:shard_end]
        assert len(self.shards) > 0, f"No shards in {data_dir}"

        self.current_shard_idx = 0
        self.position = 0
        self.data = np.load(self.shards[0], mmap_mode="r").astype(np.int64)

    def next_batch(self) -> tuple[torch.Tensor, torch.Tensor]:
        tokens_needed = self.batch_size * (self.seq_len + 1)

        if self.position + tokens_needed > len(self.data):
            self.current_shard_idx = (self.current_shard_idx + 1) % len(self.shards)
            self.data = np.load(self.shards[self.current_shard_idx], mmap_mode="r").astype(np.int64)
            self.position = 0

        chunk = self.data[self.position:self.position + tokens_needed]
        self.position += tokens_needed

        chunk = chunk.reshape(self.batch_size, self.seq_len + 1)
        input_ids = torch.from_numpy(chunk[:, :-1].copy())
        targets = torch.from_numpy(chunk[:, 1:].copy())
        return input_ids, targets


# ══════════════════════════════════════════════════════════════════
# Training loop
# ══════════════════════════════════════════════════════════════════


def train_model(
    model: ExtractedModel,
    train_loader: SimpleDataLoader,
    eval_loader: SimpleDataLoader,
    n_steps: int,
    lr: float,
    weight_decay: float,
    eval_every: int,
    device: str,
    label: str,
) -> list[dict]:
    """Train and return loss history."""
    model = model.to(device)

    # Only optimize trainable params
    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay)

    # Cosine schedule
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    history = []
    t0 = time.time()

    for step in range(1, n_steps + 1):
        model.train()
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        logits = model(input_ids)
        loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))

        optimizer.zero_grad()
        loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        train_loss = loss.item()

        if step % eval_every == 0 or step == 1:
            model.eval()
            eval_losses = []
            with torch.no_grad():
                for _ in range(10):
                    e_ids, e_tgt = eval_loader.next_batch()
                    e_ids, e_tgt = e_ids.to(device), e_tgt.to(device)
                    e_logits = model(e_ids)
                    e_loss = F.cross_entropy(e_logits.view(-1, e_logits.size(-1)), e_tgt.view(-1))
                    eval_losses.append(e_loss.item())
            eval_loss = np.mean(eval_losses)

            elapsed = time.time() - t0
            tok_per_sec = step * BATCH_SIZE * SEQ_LEN / elapsed

            record = {
                "step": step, "train_loss": train_loss, "eval_loss": eval_loss,
                "lr": scheduler.get_last_lr()[0], "elapsed": elapsed,
                "tok_per_sec": tok_per_sec,
            }
            history.append(record)

            print(f"  [{label}] step {step:>5} | train {train_loss:.4f} | "
                  f"eval {eval_loss:.4f} | {tok_per_sec:.0f} tok/s",
                  file=sys.stderr)

    return history


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Holographic extraction experiment")
    parser.add_argument("--source", default=SOURCE_MODEL, help="Source model")
    parser.add_argument("--n-layers", type=int, default=N_EXTRACT_LAYERS)
    parser.add_argument("--layer-stride", type=int, default=LAYER_STRIDE)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--eval-every", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--seq-len", type=int, default=SEQ_LEN)
    parser.add_argument("--lr", type=float, default=LR)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)
    layer_indices = list(range(0, 40, args.layer_stride))[:args.n_layers]

    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  HOLOGRAPHIC EXTRACTION EXPERIMENT", file=sys.stderr)
    print(f"  Source: {args.source}", file=sys.stderr)
    print(f"  Layers: {layer_indices} ({len(layer_indices)} layers)", file=sys.stderr)
    print(f"  Steps: {args.steps}, batch={args.batch_size}, seq={args.seq_len}", file=sys.stderr)
    print(f"{'='*60}\n", file=sys.stderr)

    # ── Phase 1: Extract signs from source ─────────────────
    print(f"Phase 1: Sign extraction", file=sys.stderr)
    t0 = time.time()
    extracted_signs = extract_signs(args.source, layer_indices, device=args.device)
    t_extract = time.time() - t0
    print(f"  Extraction took {t_extract:.1f}s\n", file=sys.stderr)

    # ── Phase 2: Build models ──────────────────────────────
    print(f"Phase 2: Building models", file=sys.stderr)

    # Detect intermediate size from extracted signs
    intermediate = extracted_signs[0]["gate"].shape[0]
    print(f"  Detected intermediate_size={intermediate} from extracted signs", file=sys.stderr)

    # Model A: Extracted plates (signs from source)
    model_extracted = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=extracted_signs,
    )

    # Model B: Random plates (baseline — same architecture, random signs)
    model_random = ExtractedModel(
        n_layers=len(layer_indices),
        d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
        head_dim=HEAD_DIM, intermediate=intermediate,
        vocab_size=VOCAB_SIZE, layer_signs=None,  # random init
    )

    params_e = model_extracted.count_params()
    params_r = model_random.count_params()
    print(f"  Extracted model: {params_e['trainable']:,} trainable, "
          f"{params_e['frozen_ternary']:,} frozen ternary", file=sys.stderr)
    print(f"  Random model:    {params_r['trainable']:,} trainable, "
          f"{params_r['frozen_ternary']:,} frozen ternary", file=sys.stderr)

    # ── Phase 3: Train both models ────────────────────────
    print(f"\nPhase 3: Training", file=sys.stderr)

    train_loader = SimpleDataLoader(
        DATA_DIR, args.batch_size, args.seq_len,
        shard_start=0, shard_end=4, seed=42,
    )
    eval_loader = SimpleDataLoader(
        DATA_DIR, args.batch_size, args.seq_len,
        shard_start=4, shard_end=6, seed=123,
    )

    # Train extracted model
    print(f"\n  ═══ Training EXTRACTED model ═══", file=sys.stderr)
    history_extracted = train_model(
        model_extracted, train_loader, eval_loader,
        n_steps=args.steps, lr=args.lr, weight_decay=WEIGHT_DECAY,
        eval_every=args.eval_every, device=args.device, label="EXTRACTED",
    )

    # Reset data loaders for fair comparison
    train_loader_b = SimpleDataLoader(
        DATA_DIR, args.batch_size, args.seq_len,
        shard_start=0, shard_end=4, seed=42,
    )
    eval_loader_b = SimpleDataLoader(
        DATA_DIR, args.batch_size, args.seq_len,
        shard_start=4, shard_end=6, seed=123,
    )

    # Train random model
    print(f"\n  ═══ Training RANDOM model ═══", file=sys.stderr)
    history_random = train_model(
        model_random, train_loader_b, eval_loader_b,
        n_steps=args.steps, lr=args.lr, weight_decay=WEIGHT_DECAY,
        eval_every=args.eval_every, device=args.device, label="RANDOM",
    )

    # ── Phase 4: Compare results ──────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  RESULTS COMPARISON", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    final_extracted = history_extracted[-1]["eval_loss"]
    final_random = history_random[-1]["eval_loss"]
    improvement = (final_random - final_extracted) / final_random * 100

    print(f"\n  Final eval loss:", file=sys.stderr)
    print(f"    EXTRACTED plates: {final_extracted:.4f}", file=sys.stderr)
    print(f"    RANDOM plates:    {final_random:.4f}", file=sys.stderr)
    print(f"    Improvement:      {improvement:+.2f}%", file=sys.stderr)
    print(f"", file=sys.stderr)

    if final_extracted < final_random:
        print(f"  ✅ EXTRACTED SIGNS OUTPERFORM RANDOM", file=sys.stderr)
        print(f"     The holographic plate contains useful structure!", file=sys.stderr)
    else:
        print(f"  ⚠️  Random plates match or beat extracted", file=sys.stderr)
        print(f"     Sign topology alone may not be sufficient at this scale", file=sys.stderr)

    # Step-by-step comparison
    print(f"\n  Step-by-step eval loss:", file=sys.stderr)
    print(f"  {'Step':>6} {'Extracted':>10} {'Random':>10} {'Δ':>8}", file=sys.stderr)
    print(f"  {'─'*6} {'─'*10} {'─'*10} {'─'*8}", file=sys.stderr)
    for he, hr in zip(history_extracted, history_random):
        delta = hr["eval_loss"] - he["eval_loss"]
        print(f"  {he['step']:>6} {he['eval_loss']:>10.4f} {hr['eval_loss']:>10.4f} "
              f"{delta:>+8.4f}", file=sys.stderr)

    # ── Save results ──────────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source_model": args.source,
        "layer_indices": layer_indices,
        "n_layers": len(layer_indices),
        "d_model": D_MODEL,
        "n_heads": N_HEADS,
        "n_kv_heads": N_KV_HEADS,
        "intermediate": INTERMEDIATE_SIZE,
        "vocab_size": VOCAB_SIZE,
        "training": {
            "steps": args.steps,
            "batch_size": args.batch_size,
            "seq_len": args.seq_len,
            "lr": args.lr,
        },
        "params": params_e,
        "history_extracted": history_extracted,
        "history_random": history_random,
        "final_comparison": {
            "extracted_eval_loss": final_extracted,
            "random_eval_loss": final_random,
            "improvement_pct": improvement,
            "extracted_wins": bool(final_extracted < final_random),
        },
    }

    json_path = args.output_dir / "extraction_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
