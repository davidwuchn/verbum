#!/usr/bin/env python3
"""Holographic Etch with Procrustes Lens — drain a big model's holograms into a small crystal.

The Procrustes lens probe (session 107) proved that two independently trained models'
hidden state spaces are related by a ROTATION in beam subspace (cos=0.83 after
alignment, zero trainable parameters). This experiment uses that lens to transfer
knowledge from a large teacher to a small student.

═══════════════════════════════════════════════════════════════════════════════════════

Core mechanism: INTERFERENCE-DRIVEN ETCHING

In optical holography:
  - Reference beam (coherent, known) + Object beam (what you want to record)
  - Interference pattern = where they meet in the recording medium
  - The pattern IS the hologram

Here:
  - Reference beam = teacher's hidden states projected through Procrustes lens
  - Object beam = student's hidden states during training
  - Interference pattern = projected_teacher - student_actual
  - The interference drives weight updates (gradient) + sign flips (etch)

The teacher doesn't tell the student what weights to have. It tells the student
what GEOMETRY to have at each depth. The student figures out how to achieve that
geometry with its own weights.

═══════════════════════════════════════════════════════════════════════════════════════

Experiment: 4-condition comparison (2×2: plates × lens)

  A: Extracted plates, NT loss only         (session 104 baseline: eval_loss=77.72)
  B: Extracted plates, NT + lens alignment  (does lens improve beyond extraction?)
  C: Random plates, NT loss only            (session 104 baseline: eval_loss=81.96)
  D: Random plates, NT + lens alignment     (can lens guide formation from nothing?)

  Holy grail: D > A → lens-guided training beats static extraction

The lens is ADAPTIVE: recomputed every N steps because the student's beam subspace
evolves during training. Procrustes alignment is O(k³) — negligible cost.

═══════════════════════════════════════════════════════════════════════════════════════

Usage:
    # Full experiment (4 conditions)
    uv run python scripts/explore/holographic_etch_with_lens.py

    # Quick test
    uv run python scripts/explore/holographic_etch_with_lens.py --quick

    # With pre-cached teacher activations (skip teacher loading)
    uv run python scripts/explore/holographic_etch_with_lens.py \\
        --teacher-cache results/holographic-etch/teacher_activations.npz

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
OUTPUT_DIR = Path("results/holographic-etch")

# Architecture (from extract_and_train.py)
TEACHER_LAYERS = [0, 10, 20, 30]  # Depth map layers
D_MODEL = 5120
N_HEADS = 40
N_KV_HEADS = 8
HEAD_DIM = D_MODEL // N_HEADS  # 128
VOCAB_SIZE = 151936
INTERMEDIATE_SIZE = 17408

# Training
BATCH_SIZE = 2
SEQ_LEN = 512
LR = 3e-4
WEIGHT_DECAY = 0.01

# Lens config
BEAM_DIMS = 20          # PCA dimensions for beam subspace
LENS_EVERY = 50         # Recompute Procrustes lens every N steps
LENS_BUFFER_SIZE = 64   # Number of examples to accumulate for lens calibration
ALIGN_LAMBDA = 0.05     # Weight of alignment loss (gentle: don't fight next-token)
ALIGN_WARMUP = 50       # Start alignment loss after this many steps (beam needs structure first)


# ══════════════════════════════════════════════════════════════════
# Ternary layer (reused from extract_and_train.py)
# ══════════════════════════════════════════════════════════════════


class TernaryFrozen(nn.Module):
    """Frozen ternary matrix with trainable per-output scale."""

    def __init__(self, in_features: int, out_features: int, signs: torch.Tensor | None = None):
        super().__init__()
        if signs is not None:
            self.register_buffer("signs", signs.to(torch.int8))
        else:
            self.register_buffer("signs",
                torch.randint(-1, 2, (out_features, in_features), dtype=torch.int8))
        self.scale = nn.Parameter(torch.ones(out_features) * (1.0 / in_features**0.5))

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        W_effective = self.signs.float() * self.scale.unsqueeze(1)
        return F.linear(x, W_effective)


# ══════════════════════════════════════════════════════════════════
# Student model architecture (from extract_and_train.py)
# ══════════════════════════════════════════════════════════════════


class RMSNorm(nn.Module):
    def __init__(self, dim: int, eps: float = 1e-6):
        super().__init__()
        self.weight = nn.Parameter(torch.ones(dim))
        self.eps = eps

    def forward(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps) * self.weight


class ExtractedAttention(nn.Module):
    def __init__(self, d_model, n_heads, n_kv_heads, head_dim,
                 k_signs=None, v_signs=None, o_signs=None):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.head_dim = head_dim
        self.n_kv_groups = n_heads // n_kv_heads
        self.q_proj = nn.Linear(d_model, n_heads * head_dim, bias=False)
        kv_dim = n_kv_heads * head_dim
        self.k_proj = TernaryFrozen(d_model, kv_dim, signs=k_signs)
        self.v_proj = TernaryFrozen(d_model, kv_dim, signs=v_signs)
        self.o_proj = TernaryFrozen(n_heads * head_dim, d_model, signs=o_signs)

    def forward(self, x):
        B, L, _ = x.shape
        q = self.q_proj(x).view(B, L, self.n_heads, self.head_dim).transpose(1, 2)
        k = self.k_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)
        v = self.v_proj(x).view(B, L, self.n_kv_heads, self.head_dim).transpose(1, 2)
        if self.n_kv_groups > 1:
            k = k.repeat_interleave(self.n_kv_groups, dim=1)
            v = v.repeat_interleave(self.n_kv_groups, dim=1)
        attn_out = F.scaled_dot_product_attention(q, k, v, is_causal=True)
        return self.o_proj(attn_out.transpose(1, 2).contiguous().view(B, L, -1))


class ExtractedFFN(nn.Module):
    def __init__(self, d_model, intermediate, gate_signs=None, up_signs=None):
        super().__init__()
        self.gate_proj = TernaryFrozen(d_model, intermediate, signs=gate_signs)
        self.up_proj = TernaryFrozen(d_model, intermediate, signs=up_signs)
        self.down_proj = nn.Linear(intermediate, d_model, bias=False)

    def forward(self, x):
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

    def forward(self, x):
        x = x + self.attn(self.input_norm(x))
        x = x + self.ffn(self.post_attn_norm(x))
        return x


class HolographicStudent(nn.Module):
    """Student model with hooks for hidden state capture at each layer."""

    def __init__(self, n_layers, d_model, n_heads, n_kv_heads, head_dim,
                 intermediate, vocab_size, layer_signs=None):
        super().__init__()
        self.embed = nn.Embedding(vocab_size, d_model)
        self.layers = nn.ModuleList()
        self.n_layers = n_layers

        for i in range(n_layers):
            signs = layer_signs[i] if layer_signs else {}
            self.layers.append(ExtractedLayer(
                d_model, n_heads, n_kv_heads, head_dim, intermediate,
                k_signs=signs.get("k"), v_signs=signs.get("v"), o_signs=signs.get("o"),
                gate_signs=signs.get("gate"), up_signs=signs.get("up"),
            ))

        self.norm = RMSNorm(d_model)
        self.lm_head = nn.Linear(d_model, vocab_size, bias=False)
        self.lm_head.weight = self.embed.weight

        # Hidden state capture (populated during forward when capture=True)
        self._capture = False
        self._hidden_states: dict[int, torch.Tensor] = {}

    def forward(self, input_ids: torch.Tensor, capture_hidden: bool = False) -> torch.Tensor:
        self._capture = capture_hidden
        self._hidden_states = {}

        x = self.embed(input_ids)
        for i, layer in enumerate(self.layers):
            x = layer(x)
            if self._capture:
                # Capture the residual stream AFTER each layer
                # Store last-token hidden state: (batch, d_model)
                self._hidden_states[i] = x[:, -1, :]

        x = self.norm(x)
        return self.lm_head(x)

    def get_hidden_states(self) -> dict[int, torch.Tensor]:
        """Return captured hidden states {layer_idx: (batch, d_model)}."""
        return self._hidden_states

    def count_params(self):
        total = sum(p.numel() for p in self.parameters())
        trainable = sum(p.numel() for p in self.parameters() if p.requires_grad)
        frozen = sum(b.numel() for b in self.buffers() if b.dtype == torch.int8)
        return {"total": total, "trainable": trainable, "frozen_ternary": frozen}


# ══════════════════════════════════════════════════════════════════
# Teacher activation pre-computation
# ══════════════════════════════════════════════════════════════════


def precompute_teacher_activations(
    model_name: str,
    data_dir: Path,
    target_layers: list[int],
    n_batches: int,
    batch_size: int,
    seq_len: int,
    device: str,
    cache_path: Path | None = None,
) -> dict[int, np.ndarray]:
    """Load teacher, run training data, capture hidden states, save.

    Returns {layer_idx: ndarray of shape (n_batches * batch_size, d_model)}
    where each row is the last-token hidden state for one sequence.
    """
    if cache_path and cache_path.exists():
        print(f"  Loading cached teacher activations from {cache_path}", file=sys.stderr)
        cached = np.load(str(cache_path))
        result = {}
        for li in target_layers:
            key = f"L{li}"
            result[li] = cached[key]
            print(f"    L{li}: {result[li].shape}", file=sys.stderr)
        return result

    print(f"  Loading {model_name} for activation pre-computation...", file=sys.stderr)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    layers = model.model.layers
    hidden_captures: dict[int, list[torch.Tensor]] = {li: [] for li in target_layers}

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            h = output[0] if isinstance(output, tuple) else output
            # Last token hidden state
            hidden_captures[layer_idx].append(h[:, -1, :].detach().cpu().float())
        return hook_fn

    hooks = []
    for li in target_layers:
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Load data
    loader = SimpleDataLoader(data_dir, batch_size, seq_len, shard_start=0, shard_end=4, seed=42)

    print(f"  Running {n_batches} batches through teacher...", file=sys.stderr)
    t0 = time.time()
    for b in range(n_batches):
        input_ids, _ = loader.next_batch()
        input_ids = input_ids.to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (b + 1) % 50 == 0:
            elapsed = time.time() - t0
            print(f"    Batch {b+1}/{n_batches} ({elapsed:.1f}s)", file=sys.stderr)

    for h in hooks:
        h.remove()

    elapsed = time.time() - t0
    print(f"  Teacher activations collected in {elapsed:.1f}s", file=sys.stderr)

    # Stack results
    result = {}
    save_dict = {}
    for li in target_layers:
        stacked = torch.cat(hidden_captures[li], dim=0).numpy()
        result[li] = stacked
        save_dict[f"L{li}"] = stacked
        print(f"    L{li}: {stacked.shape} (mean_norm={np.linalg.norm(stacked, axis=1).mean():.1f})",
              file=sys.stderr)

    # Save cache
    if cache_path:
        cache_path.parent.mkdir(parents=True, exist_ok=True)
        np.savez_compressed(str(cache_path), **save_dict)
        print(f"  Cached teacher activations: {cache_path} "
              f"({cache_path.stat().st_size / 1e6:.1f} MB)", file=sys.stderr)

    # Unload teacher
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()
    elif torch.cuda.is_available():
        torch.cuda.empty_cache()

    return result


# ══════════════════════════════════════════════════════════════════
# Sign extraction (from extract_and_train.py)
# ══════════════════════════════════════════════════════════════════


def extract_signs(model_name: str, layer_indices: list[int], device: str = "cpu") -> list[dict]:
    """Extract sign(K,V,O,gate,up) from source model."""
    print(f"  Extracting signs from {model_name}, layers {layer_indices}...", file=sys.stderr)

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device,
    )
    model.eval()

    all_signs = []
    for li in layer_indices:
        layer = model.model.layers[li]
        signs = {
            "k": torch.sign(layer.self_attn.k_proj.weight.float()).to(torch.int8).cpu(),
            "v": torch.sign(layer.self_attn.v_proj.weight.float()).to(torch.int8).cpu(),
            "o": torch.sign(layer.self_attn.o_proj.weight.float()).to(torch.int8).cpu(),
            "gate": torch.sign(layer.mlp.gate_proj.weight.float()).to(torch.int8).cpu(),
            "up": torch.sign(layer.mlp.up_proj.weight.float()).to(torch.int8).cpu(),
        }
        all_signs.append(signs)
        print(f"    L{li}: extracted K{list(signs['k'].shape)} V{list(signs['v'].shape)} "
              f"O{list(signs['o'].shape)} gate{list(signs['gate'].shape)}", file=sys.stderr)

    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return all_signs


# ══════════════════════════════════════════════════════════════════
# Adaptive Procrustes Lens
# ══════════════════════════════════════════════════════════════════


class ProcustesLens:
    """Adaptive lens that aligns teacher beam space → student beam space.

    The lens is recomputed periodically as the student evolves. Each recomputation:
    1. PCA teacher activations at each layer → teacher beam basis (k, d_model)
    2. PCA student activations at each layer → student beam basis (k, d_model)
    3. Procrustes: find rotation R that aligns teacher beams to student beams
    4. Store: basis, rotation, scale per layer

    Usage during training:
      projected = lens.project(teacher_hidden, layer_idx)
      loss = MSE(projected, student_hidden_in_beam_space)
    """

    def __init__(self, n_layers: int, k: int, target_layers: list[int]):
        self.n_layers = n_layers
        self.k = k
        self.target_layers = target_layers  # teacher layer indices

        # Per layer: teacher_basis (k, d), student_basis (k, d), R (k, k), scale, means
        self.teacher_basis: dict[int, np.ndarray] = {}
        self.student_basis: dict[int, np.ndarray] = {}
        self.rotation: dict[int, np.ndarray] = {}
        self.scale: dict[int, float] = {}
        self.teacher_mean: dict[int, np.ndarray] = {}
        self.student_mean: dict[int, np.ndarray] = {}
        self.is_calibrated = False

        # Calibration buffers
        self._teacher_buffer: dict[int, list[np.ndarray]] = {i: [] for i in range(n_layers)}
        self._student_buffer: dict[int, list[np.ndarray]] = {i: [] for i in range(n_layers)}

    def accumulate(
        self,
        teacher_hs: dict[int, np.ndarray],  # {teacher_layer: (batch, d_model)}
        student_hs: dict[int, np.ndarray],  # {student_layer: (batch, d_model)}
    ):
        """Accumulate hidden states for next lens calibration."""
        for student_li in range(self.n_layers):
            teacher_li = self.target_layers[student_li]
            if teacher_li in teacher_hs and student_li in student_hs:
                self._teacher_buffer[student_li].append(teacher_hs[teacher_li])
                self._student_buffer[student_li].append(student_hs[student_li])

    def buffer_size(self) -> int:
        """How many examples in the calibration buffer."""
        if 0 in self._teacher_buffer and self._teacher_buffer[0]:
            return sum(x.shape[0] for x in self._teacher_buffer[0])
        return 0

    def calibrate(self):
        """Compute Procrustes alignment from accumulated buffers."""
        for student_li in range(self.n_layers):
            t_stack = np.concatenate(self._teacher_buffer[student_li], axis=0)
            s_stack = np.concatenate(self._student_buffer[student_li], axis=0)
            n = t_stack.shape[0]

            if n < self.k + 2:
                print(f"    L{student_li}: only {n} examples, need {self.k + 2}, skipping",
                      file=sys.stderr)
                continue

            # PCA teacher
            t_mean = t_stack.mean(axis=0)
            t_centered = t_stack - t_mean
            _, S_t, Vt_t = np.linalg.svd(t_centered, full_matrices=False)
            t_basis = Vt_t[:self.k]  # (k, d_model)
            t_proj = t_centered @ t_basis.T  # (n, k)

            # PCA student
            s_mean = s_stack.mean(axis=0)
            s_centered = s_stack - s_mean
            _, S_s, Vt_s = np.linalg.svd(s_centered, full_matrices=False)
            s_basis = Vt_s[:self.k]  # (k, d_model)
            s_proj = s_centered @ s_basis.T  # (n, k)

            # Procrustes: find R such that t_proj @ R ≈ s_proj
            M = t_proj.T @ s_proj  # (k, k)
            U, S, Vt = np.linalg.svd(M)
            R = U @ Vt
            if np.linalg.det(R) < 0:
                U[:, -1] *= -1
                R = U @ Vt

            # Scale
            aligned = t_proj @ R
            scale = np.trace(aligned.T @ s_proj) / np.trace(aligned.T @ aligned)

            # Cosine after alignment
            aligned_scaled = aligned * scale
            cos_pairs = []
            for i in range(n):
                na = np.linalg.norm(aligned_scaled[i])
                ns = np.linalg.norm(s_proj[i])
                if na > 1e-8 and ns > 1e-8:
                    cos_pairs.append(np.dot(aligned_scaled[i], s_proj[i]) / (na * ns))
            mean_cos = np.mean(cos_pairs) if cos_pairs else 0.0

            # Store
            self.teacher_basis[student_li] = t_basis
            self.student_basis[student_li] = s_basis
            self.rotation[student_li] = R
            self.scale[student_li] = float(scale)
            self.teacher_mean[student_li] = t_mean
            self.student_mean[student_li] = s_mean

            # Variance explained
            t_var = (S_t[:self.k] ** 2).sum() / (S_t ** 2).sum()
            s_var = (S_s[:self.k] ** 2).sum() / (S_s ** 2).sum()

            print(f"    Layer {student_li} (teacher L{self.target_layers[student_li]}): "
                  f"cos={mean_cos:.4f}, scale={scale:.4f}, "
                  f"t_var={t_var:.3f}, s_var={s_var:.3f}",
                  file=sys.stderr)

        self.is_calibrated = True

        # Clear buffers
        self._teacher_buffer = {i: [] for i in range(self.n_layers)}
        self._student_buffer = {i: [] for i in range(self.n_layers)}

    def project_teacher(
        self, teacher_hidden: torch.Tensor, student_layer_idx: int
    ) -> torch.Tensor:
        """Project teacher hidden state → student beam space.

        Input: teacher_hidden (batch, d_model) at the corresponding teacher layer
        Output: projected (batch, k) in student beam space

        Pipeline: center → PCA(teacher) → rotate → scale → student beam coords
        """
        if student_layer_idx not in self.teacher_basis:
            return None

        device = teacher_hidden.device
        dtype = teacher_hidden.dtype

        t_basis = torch.from_numpy(self.teacher_basis[student_layer_idx]).to(device, dtype)
        s_basis = torch.from_numpy(self.student_basis[student_layer_idx]).to(device, dtype)
        R = torch.from_numpy(self.rotation[student_layer_idx]).to(device, dtype)
        scale = self.scale[student_layer_idx]
        t_mean = torch.from_numpy(self.teacher_mean[student_layer_idx]).to(device, dtype)

        # Teacher → beam space → rotate → scale
        centered = teacher_hidden - t_mean
        beam_t = centered @ t_basis.T  # (batch, k)
        aligned = beam_t @ R * scale   # (batch, k)

        return aligned

    def project_student(
        self, student_hidden: torch.Tensor, student_layer_idx: int
    ) -> torch.Tensor:
        """Project student hidden state → student beam space.

        Input: student_hidden (batch, d_model)
        Output: projected (batch, k) in student beam space
        """
        if student_layer_idx not in self.student_basis:
            return None

        device = student_hidden.device
        dtype = student_hidden.dtype

        s_basis = torch.from_numpy(self.student_basis[student_layer_idx]).to(device, dtype)
        s_mean = torch.from_numpy(self.student_mean[student_layer_idx]).to(device, dtype)

        centered = student_hidden - s_mean
        beam_s = centered @ s_basis.T  # (batch, k)
        return beam_s

    def alignment_loss(
        self,
        teacher_hs: dict[int, torch.Tensor],   # {teacher_layer: (batch, d_model)}
        student_hs: dict[int, torch.Tensor],    # {student_layer: (batch, d_model)}
    ) -> torch.Tensor:
        """Compute MSE alignment loss in beam space across all layers.

        The loss measures how well the student's hidden states match the
        teacher's projected beam. This is the interference pattern.
        """
        total_loss = torch.tensor(0.0, device=next(iter(student_hs.values())).device)
        n_layers = 0

        for student_li in range(self.n_layers):
            teacher_li = self.target_layers[student_li]
            if teacher_li not in teacher_hs or student_li not in student_hs:
                continue
            if student_li not in self.teacher_basis:
                continue

            t_beam = self.project_teacher(teacher_hs[teacher_li], student_li)
            s_beam = self.project_student(student_hs[student_li], student_li)

            if t_beam is not None and s_beam is not None:
                # MSE in beam space = the interference pattern magnitude
                layer_loss = F.mse_loss(s_beam, t_beam.detach())
                total_loss = total_loss + layer_loss
                n_layers += 1

        if n_layers > 0:
            total_loss = total_loss / n_layers

        return total_loss


# ══════════════════════════════════════════════════════════════════
# Data loading
# ══════════════════════════════════════════════════════════════════


class SimpleDataLoader:
    """Minimal data loader from pre-tokenized Dolma shards."""

    def __init__(self, data_dir: Path, batch_size: int, seq_len: int,
                 shard_start: int = 0, shard_end: int = 4, seed: int = 42):
        self.batch_size = batch_size
        self.seq_len = seq_len

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
        return (torch.from_numpy(chunk[:, :-1].copy()),
                torch.from_numpy(chunk[:, 1:].copy()))


# ══════════════════════════════════════════════════════════════════
# Training loop with lens-guided etch
# ══════════════════════════════════════════════════════════════════


def train_with_lens(
    model: HolographicStudent,
    teacher_activations: dict[int, np.ndarray] | None,  # Pre-cached teacher states
    teacher_layers: list[int],
    train_loader: SimpleDataLoader,
    eval_loader: SimpleDataLoader,
    n_steps: int,
    lr: float,
    weight_decay: float,
    eval_every: int,
    align_lambda: float,
    align_warmup: int,
    lens_every: int,
    lens_buffer_size: int,
    beam_dims: int,
    device: str,
    label: str,
) -> list[dict]:
    """Train model with optional lens-guided alignment loss.

    If teacher_activations is None, trains with next-token loss only (baseline).
    """
    use_lens = teacher_activations is not None and align_lambda > 0
    model = model.to(device)

    trainable_params = [p for p in model.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable_params, lr=lr, weight_decay=weight_decay)
    scheduler = torch.optim.lr_scheduler.CosineAnnealingLR(optimizer, T_max=n_steps)

    # Initialize lens
    lens = None
    if use_lens:
        lens = ProcustesLens(model.n_layers, beam_dims, teacher_layers)

    history = []
    t0 = time.time()
    teacher_batch_idx = 0
    n_teacher_examples = (
        teacher_activations[teacher_layers[0]].shape[0] if teacher_activations else 0
    )

    for step in range(1, n_steps + 1):
        model.train()
        input_ids, targets = train_loader.next_batch()
        input_ids = input_ids.to(device)
        targets = targets.to(device)

        # Forward pass (capture hidden states if using lens)
        capture = use_lens and lens is not None
        logits = model(input_ids, capture_hidden=capture)

        # Next-token loss
        ce_loss = F.cross_entropy(logits.view(-1, logits.size(-1)), targets.view(-1))
        total_loss = ce_loss
        align_loss_val = 0.0

        # Lens alignment loss
        if use_lens and lens is not None and step > align_warmup:
            student_hs = model.get_hidden_states()

            # Get corresponding teacher hidden states
            batch_size = input_ids.shape[0]
            t_start = teacher_batch_idx % n_teacher_examples
            t_end = t_start + batch_size
            if t_end > n_teacher_examples:
                # Wrap around
                teacher_batch_idx = 0
                t_start = 0
                t_end = batch_size

            teacher_hs_torch = {}
            for li in teacher_layers:
                t_slice = teacher_activations[li][t_start:t_end]
                teacher_hs_torch[li] = torch.from_numpy(t_slice).to(device)
            teacher_batch_idx = t_end

            # Accumulate for lens calibration
            teacher_hs_np = {li: teacher_activations[li][t_start:t_end] for li in teacher_layers}
            student_hs_np = {si: student_hs[si].detach().cpu().numpy() for si in student_hs}
            lens.accumulate(teacher_hs_np, student_hs_np)

            # Calibrate lens periodically
            if lens.buffer_size() >= lens_buffer_size or (step == align_warmup + 1):
                if lens.buffer_size() >= beam_dims + 2:
                    print(f"\n  [{label}] Calibrating lens at step {step} "
                          f"(buffer={lens.buffer_size()})...", file=sys.stderr)
                    lens.calibrate()

            # Compute alignment loss if lens is calibrated
            if lens.is_calibrated:
                align_loss = lens.alignment_loss(teacher_hs_torch, student_hs)
                total_loss = total_loss + align_lambda * align_loss
                align_loss_val = align_loss.item()

        optimizer.zero_grad()
        total_loss.backward()
        torch.nn.utils.clip_grad_norm_(trainable_params, 1.0)
        optimizer.step()
        scheduler.step()

        # Evaluation
        if step % eval_every == 0 or step == 1:
            model.eval()
            eval_losses = []
            with torch.no_grad():
                for _ in range(10):
                    e_ids, e_tgt = eval_loader.next_batch()
                    e_ids, e_tgt = e_ids.to(device), e_tgt.to(device)
                    e_logits = model(e_ids)
                    e_loss = F.cross_entropy(
                        e_logits.view(-1, e_logits.size(-1)), e_tgt.view(-1))
                    eval_losses.append(e_loss.item())
            eval_loss = np.mean(eval_losses)

            elapsed = time.time() - t0
            tok_per_sec = step * BATCH_SIZE * SEQ_LEN / elapsed

            record = {
                "step": step,
                "train_loss": ce_loss.item(),
                "eval_loss": eval_loss,
                "align_loss": align_loss_val,
                "total_loss": total_loss.item(),
                "lr": scheduler.get_last_lr()[0],
                "elapsed": elapsed,
                "tok_per_sec": tok_per_sec,
                "lens_calibrated": lens.is_calibrated if lens else False,
            }
            history.append(record)

            align_str = f" | align {align_loss_val:.4f}" if use_lens else ""
            print(f"  [{label}] step {step:>5} | CE {ce_loss.item():.4f} | "
                  f"eval {eval_loss:.4f}{align_str} | {tok_per_sec:.0f} tok/s",
                  file=sys.stderr)

    return history


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(description="Holographic etch with Procrustes lens")
    parser.add_argument("--source", default=SOURCE_MODEL)
    parser.add_argument("--steps", type=int, default=500)
    parser.add_argument("--eval-every", type=int, default=25)
    parser.add_argument("--batch-size", type=int, default=BATCH_SIZE)
    parser.add_argument("--seq-len", type=int, default=SEQ_LEN)
    parser.add_argument("--lr", type=float, default=LR)
    parser.add_argument("--align-lambda", type=float, default=ALIGN_LAMBDA)
    parser.add_argument("--align-warmup", type=int, default=ALIGN_WARMUP)
    parser.add_argument("--beam-dims", type=int, default=BEAM_DIMS)
    parser.add_argument("--lens-every", type=int, default=LENS_EVERY)
    parser.add_argument("--lens-buffer", type=int, default=LENS_BUFFER_SIZE)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--teacher-cache", type=Path, default=None)
    parser.add_argument("--signs-cache", type=Path, default=None,
                       help="Path to cached extracted signs (npz)")
    parser.add_argument("--quick", action="store_true",
                       help="200 steps, eval every 50")
    parser.add_argument("--teacher-batches", type=int, default=300,
                       help="Number of batches for teacher activation pre-computation")
    parser.add_argument("--conditions", type=str, default="A,B,C,D",
                       help="Which conditions to run (A=extracted+NT, B=extracted+lens, "
                            "C=random+NT, D=random+lens)")
    args = parser.parse_args()

    if args.quick:
        args.steps = 200
        args.eval_every = 50
        args.teacher_batches = 100

    args.output_dir.mkdir(parents=True, exist_ok=True)
    conditions = [c.strip() for c in args.conditions.split(",")]

    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  HOLOGRAPHIC ETCH WITH PROCRUSTES LENS", file=sys.stderr)
    print(f"  Source: {args.source}", file=sys.stderr)
    print(f"  Student layers: {len(TEACHER_LAYERS)} (from teacher {TEACHER_LAYERS})", file=sys.stderr)
    print(f"  Steps: {args.steps}, λ_align={args.align_lambda}, beam_dims={args.beam_dims}", file=sys.stderr)
    print(f"  Conditions: {conditions}", file=sys.stderr)
    print(f"{'='*70}\n", file=sys.stderr)

    # ── Phase 1: Pre-compute teacher activations ──────────
    need_lens = "B" in conditions or "D" in conditions
    teacher_activations = None

    if need_lens:
        print(f"Phase 1: Teacher activation pre-computation", file=sys.stderr)
        cache_path = args.teacher_cache or args.output_dir / "teacher_activations.npz"
        teacher_activations = precompute_teacher_activations(
            args.source, DATA_DIR, TEACHER_LAYERS,
            n_batches=args.teacher_batches,
            batch_size=args.batch_size,
            seq_len=args.seq_len,
            device=args.device,
            cache_path=cache_path,
        )
        print(f"  Teacher activations ready: {teacher_activations[TEACHER_LAYERS[0]].shape[0]} examples\n",
              file=sys.stderr)

    # ── Phase 2: Extract signs ─────────────────────────────
    need_extracted = "A" in conditions or "B" in conditions
    extracted_signs = None

    if need_extracted:
        print(f"Phase 2: Sign extraction", file=sys.stderr)
        if args.signs_cache and args.signs_cache.exists():
            print(f"  Loading cached signs from {args.signs_cache}", file=sys.stderr)
            cached = np.load(str(args.signs_cache), allow_pickle=True)
            extracted_signs = []
            for i in range(len(TEACHER_LAYERS)):
                signs = {}
                for name in ["k", "v", "o", "gate", "up"]:
                    signs[name] = torch.from_numpy(cached[f"layer{i}_{name}"])
                extracted_signs.append(signs)
        else:
            extracted_signs = extract_signs(args.source, TEACHER_LAYERS, device=args.device)
            # Cache for reuse
            save_dict = {}
            for i, signs in enumerate(extracted_signs):
                for name, tensor in signs.items():
                    save_dict[f"layer{i}_{name}"] = tensor.numpy()
            cache_path = args.output_dir / "extracted_signs.npz"
            np.savez_compressed(str(cache_path), **save_dict)
            print(f"  Cached signs: {cache_path}\n", file=sys.stderr)

    intermediate = (
        extracted_signs[0]["gate"].shape[0] if extracted_signs
        else INTERMEDIATE_SIZE
    )

    # ── Phase 3: Train all conditions ──────────────────────
    print(f"\nPhase 3: Training", file=sys.stderr)
    all_histories = {}

    condition_configs = {
        "A": {"label": "Extracted+NT", "use_extracted": True, "use_lens": False},
        "B": {"label": "Extracted+Lens", "use_extracted": True, "use_lens": True},
        "C": {"label": "Random+NT", "use_extracted": False, "use_lens": False},
        "D": {"label": "Random+Lens", "use_extracted": False, "use_lens": True},
    }

    for cond in conditions:
        cfg = condition_configs[cond]
        print(f"\n  {'═'*60}", file=sys.stderr)
        print(f"  Condition {cond}: {cfg['label']}", file=sys.stderr)
        print(f"  {'═'*60}", file=sys.stderr)

        # Build model
        layer_signs = extracted_signs if cfg["use_extracted"] else None
        model = HolographicStudent(
            n_layers=len(TEACHER_LAYERS),
            d_model=D_MODEL, n_heads=N_HEADS, n_kv_heads=N_KV_HEADS,
            head_dim=HEAD_DIM, intermediate=intermediate,
            vocab_size=VOCAB_SIZE, layer_signs=layer_signs,
        )
        params = model.count_params()
        print(f"  Params: {params['trainable']:,} trainable, "
              f"{params['frozen_ternary']:,} frozen ternary", file=sys.stderr)

        # Data loaders (same seed for fair comparison)
        train_loader = SimpleDataLoader(
            DATA_DIR, args.batch_size, args.seq_len, shard_start=0, shard_end=4, seed=42)
        eval_loader = SimpleDataLoader(
            DATA_DIR, args.batch_size, args.seq_len, shard_start=4, shard_end=6, seed=123)

        # Train
        history = train_with_lens(
            model=model,
            teacher_activations=teacher_activations if cfg["use_lens"] else None,
            teacher_layers=TEACHER_LAYERS,
            train_loader=train_loader,
            eval_loader=eval_loader,
            n_steps=args.steps,
            lr=args.lr,
            weight_decay=WEIGHT_DECAY,
            eval_every=args.eval_every,
            align_lambda=args.align_lambda if cfg["use_lens"] else 0.0,
            align_warmup=args.align_warmup,
            lens_every=args.lens_every,
            lens_buffer_size=args.lens_buffer,
            beam_dims=args.beam_dims,
            device=args.device,
            label=f"{cond}:{cfg['label']}",
        )

        all_histories[cond] = history

        # Free model
        del model
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()

    # ── Phase 4: Compare results ──────────────────────────
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  RESULTS", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    # Final eval losses
    print(f"\n  Final eval loss:", file=sys.stderr)
    final_losses = {}
    for cond in conditions:
        final = all_histories[cond][-1]["eval_loss"]
        final_losses[cond] = final
        cfg = condition_configs[cond]
        print(f"    {cond}: {cfg['label']:20s} → {final:.4f}", file=sys.stderr)

    # Key comparisons
    print(f"\n  Key comparisons:", file=sys.stderr)
    if "A" in final_losses and "B" in final_losses:
        delta = final_losses["A"] - final_losses["B"]
        pct = delta / final_losses["A"] * 100
        verdict = "✅ LENS HELPS" if delta > 0 else "❌ lens hurts"
        print(f"    Lens on extracted plates: {delta:+.4f} ({pct:+.2f}%) — {verdict}",
              file=sys.stderr)

    if "C" in final_losses and "D" in final_losses:
        delta = final_losses["C"] - final_losses["D"]
        pct = delta / final_losses["C"] * 100
        verdict = "✅ LENS HELPS" if delta > 0 else "❌ lens hurts"
        print(f"    Lens on random plates:    {delta:+.4f} ({pct:+.2f}%) — {verdict}",
              file=sys.stderr)

    if "A" in final_losses and "D" in final_losses:
        delta = final_losses["A"] - final_losses["D"]
        pct = delta / final_losses["A"] * 100
        if delta > 0:
            print(f"    🏆 HOLY GRAIL: Random+Lens beats Extracted+NT by {delta:+.4f} ({pct:+.2f}%)!",
                  file=sys.stderr)
            print(f"       → Lens-guided training > static extraction!", file=sys.stderr)
        else:
            print(f"    Random+Lens vs Extracted+NT: {delta:+.4f} ({pct:+.2f}%)",
                  file=sys.stderr)

    if "A" in final_losses and "C" in final_losses:
        delta = final_losses["C"] - final_losses["A"]
        pct = delta / final_losses["C"] * 100
        print(f"    Extraction benefit (no lens): {delta:+.4f} ({pct:+.2f}%)", file=sys.stderr)

    # Step-by-step table
    print(f"\n  Step-by-step eval loss:", file=sys.stderr)
    header = f"  {'Step':>6}"
    for cond in conditions:
        header += f"  {cond}:{condition_configs[cond]['label']:>14s}"
    print(header, file=sys.stderr)
    print(f"  {'─' * (6 + 16 * len(conditions))}", file=sys.stderr)

    # Align by step
    max_records = max(len(all_histories[c]) for c in conditions)
    for i in range(max_records):
        row = ""
        step = None
        for cond in conditions:
            if i < len(all_histories[cond]):
                rec = all_histories[cond][i]
                if step is None:
                    step = rec["step"]
                row += f"  {rec['eval_loss']:>14.4f}"
            else:
                row += f"  {'':>14s}"
        if step is not None:
            print(f"  {step:>6}{row}", file=sys.stderr)

    # ── Save results ──────────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "config": {
            "source_model": args.source,
            "teacher_layers": TEACHER_LAYERS,
            "n_student_layers": len(TEACHER_LAYERS),
            "d_model": D_MODEL,
            "beam_dims": args.beam_dims,
            "align_lambda": args.align_lambda,
            "align_warmup": args.align_warmup,
            "lens_every": args.lens_every,
            "steps": args.steps,
            "batch_size": args.batch_size,
            "seq_len": args.seq_len,
            "lr": args.lr,
        },
        "conditions": {
            cond: {
                "label": condition_configs[cond]["label"],
                "history": all_histories[cond],
                "final_eval_loss": all_histories[cond][-1]["eval_loss"],
            }
            for cond in conditions
        },
        "comparisons": {},
    }

    if "A" in final_losses and "B" in final_losses:
        output["comparisons"]["lens_on_extracted"] = {
            "delta": final_losses["A"] - final_losses["B"],
            "pct": (final_losses["A"] - final_losses["B"]) / final_losses["A"] * 100,
        }
    if "C" in final_losses and "D" in final_losses:
        output["comparisons"]["lens_on_random"] = {
            "delta": final_losses["C"] - final_losses["D"],
            "pct": (final_losses["C"] - final_losses["D"]) / final_losses["C"] * 100,
        }
    if "A" in final_losses and "D" in final_losses:
        output["comparisons"]["holy_grail"] = {
            "random_lens_vs_extracted_nt": final_losses["A"] - final_losses["D"],
            "random_lens_wins": bool(final_losses["D"] < final_losses["A"]),
        }

    json_path = args.output_dir / "holographic_etch_results.json"
    json_path.write_text(json.dumps(output, indent=2))
    print(f"\n  💾 Results: {json_path}", file=sys.stderr)

    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  DONE", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)


if __name__ == "__main__":
    main()
