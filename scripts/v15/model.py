"""v15 Model — Crystal-Native Tensor Statechart.

Session 174. The model IS a statechart:
  State = residual stream (R^d_model)
  Transitions = strides (plate × input → update)
  Zones = macro-states (CLASSIFY → COMPUTE → LINK → EMIT)
  Algedonic = fire alarm (bypasses all zones)

Each stride is an autonomous VSM:
  s5: its plate (identity — what it computes)
  s4: its attention (intelligence — how it routes)
  s3: its gate (control — which neurons fire)
  s2: RMSNorm + residual (coordination — anti-oscillation)
  s1: matmul ops (operations — the work)

The statechart loads from disk: plates are data, not code.
Same architecture, different plates = different program.

License: MIT
"""

from __future__ import annotations

import math
from dataclasses import dataclass
from enum import Enum, auto
from pathlib import Path
from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V15Config, Zone, AttnType, StrideSpec, COMBINATOR_NAMES


# ══════════════════════════════════════════════════════════════════════
# Algedonic Channel (S1 → S5 direct)
# ══════════════════════════════════════════════════════════════════════

class AlgedonicSignal(Enum):
    """Fire alarm signals — bypass S2/S3/S4."""
    OK = auto()
    HALT = auto()          # NaN or norm explosion/collapse
    DIVERGING = auto()     # Dimensionality increasing after COMPUTE
    OFF_MANIFOLD = auto()  # <10% energy on crystal subspace


class AlgedonicMonitor:
    """Per-stride health monitor. Runs after EVERY stride. ~Free cost.

    Three checks:
      1. Norm bounds (catches NaN, explosion, collapse)
      2. Progressive collapse (catches divergent recursion)
      3. Crystal coherence (catches off-manifold drift)
    """

    def __init__(self, config: V15Config, crystal_basis: Optional[mx.array] = None):
        self.norm_min = config.norm_min
        self.norm_max = config.norm_max
        self.coherence_min = config.coherence_min
        self.divergence_ratio = config.divergence_ratio
        self.crystal_basis = crystal_basis  # (n_combinators, d_model) or None
        self.prev_dimensionality: Optional[float] = None

    def check(self, residual: mx.array, stride_idx: int, zone: Zone) -> AlgedonicSignal:
        """Check residual stream health. Called after each stride."""
        # 1. Norm check (NaN, explosion, collapse)
        norm = mx.sqrt(mx.mean(residual * residual))
        norm_val = norm.item()
        if math.isnan(norm_val) or norm_val < self.norm_min or norm_val > self.norm_max:
            return AlgedonicSignal.HALT

        # 2. Progressive collapse (only check after COMPUTE zone)
        if zone in (Zone.LINK, Zone.EMIT) and self.crystal_basis is not None:
            proj = residual @ self.crystal_basis.T  # (batch, seq, n_ops)
            # Effective dimensionality: count PCs with significant variance
            var_per_op = mx.var(proj, axis=(0, 1))  # (n_ops,)
            dim = mx.sum(var_per_op > 0.01).item()
            if self.prev_dimensionality is not None:
                if dim > self.prev_dimensionality * self.divergence_ratio:
                    return AlgedonicSignal.DIVERGING
            self.prev_dimensionality = dim

        # 3. Crystal coherence
        if self.crystal_basis is not None:
            proj = residual @ self.crystal_basis.T
            proj_energy = mx.sum(proj * proj)
            total_energy = mx.sum(residual * residual)
            coherence = (proj_energy / (total_energy + 1e-8)).item()
            if coherence < self.coherence_min:
                return AlgedonicSignal.OFF_MANIFOLD

        return AlgedonicSignal.OK

    def reset(self):
        """Reset state between sequences."""
        self.prev_dimensionality = None


# ══════════════════════════════════════════════════════════════════════
# Ternary Plate (the holographic grating)
# ══════════════════════════════════════════════════════════════════════

class TernaryPlate(nn.Module):
    """2-plate ternary linear: out = (plate1*γ1 + plate2*γ2) @ x.

    The holographic grating. Stores multiple reductions in superposition.
    Gate reads them out selectively (89% kill).

    plate1: {-1, 0, +1} — program topology (exact signs)
    plate2: {-1, 0, +1} — magnitude class (above/below mean)
    gamma1, gamma2: per-row float scalars
    zeros_mask: structural lattice gaps (30%, never change)

    Delta plate support (session 177):
      When delta plates are enabled (via enable_delta()), the forward
      path computes:  effective = plate ⊙ delta  (element-wise ternary multiply)
      then uses effective in place of plate for the matmul.

      Delta semantics:
        +1 → keep teacher sign here (pass-through, initial state)
        -1 → flip teacher sign here (TD correction)
         0 → block this position    (staging area during transition)

      fold() merges delta into plate:  new_plate = plate ⊙ delta, delta → +1.
      Ternary × ternary = ternary, exact. No information loss.
    """

    def __init__(self, d_out: int, d_in: int, n_plates: int = 2):
        super().__init__()
        self.d_out = d_out
        self.d_in = d_in
        self.n_plates = n_plates

        # Plate 1 (always present): program topology
        # Stored as packed uint32 for inference, float for training
        self.plate1 = mx.zeros((d_out, d_in))  # will be loaded as ternary
        self.gamma1 = mx.ones((d_out,))

        # Plate 2 (optional): magnitude mirror
        if n_plates >= 2:
            self.plate2 = mx.zeros((d_out, d_in))
            self.gamma2 = mx.ones((d_out,))
        else:
            self.plate2 = None
            self.gamma2 = None

        # Delta plates: None until enable_delta() is called.
        # When active, delta1/delta2 are float arrays with values in {-1, 0, +1}.
        self.delta1: mx.array | None = None
        self.delta2: mx.array | None = None
        self._delta_enabled = False

    @property
    def delta_enabled(self) -> bool:
        return self._delta_enabled

    def enable_delta(self) -> None:
        """Enable delta plates — initialized to all +1 (pass-through).

        After calling this, the forward path uses:
            effective1 = plate1 ⊙ delta1
            effective2 = plate2 ⊙ delta2  (if 2-plate)

        The delta plates are trainable by TernaryDescent (TD), NOT by Adam.
        They participate in gradient computation via stop_gradient on the
        ternary values — TD reads the gradient direction to decide flips.
        """
        self.delta1 = mx.ones((self.d_out, self.d_in))
        if self.n_plates >= 2 and self.plate2 is not None:
            self.delta2 = mx.ones((self.d_out, self.d_in))
        self._delta_enabled = True

    def disable_delta(self) -> None:
        """Disable delta plates (revert to base-only forward path)."""
        self.delta1 = None
        self.delta2 = None
        self._delta_enabled = False

    def _effective(self, plate: mx.array, delta: mx.array | None) -> mx.array:
        """Compute effective plate: plate ⊙ delta if delta exists, else plate.

        Ternary × ternary = ternary (exact):
            +1 × +1 = +1,  +1 × -1 = -1,  -1 × -1 = +1
            anything × 0 = 0
        """
        if delta is None:
            return plate
        # stop_gradient on both plate and delta: topology is TD-managed.
        # The gradient flows through the matmul to inform TD what to flip,
        # but Adam never updates the ternary values directly.
        return mx.stop_gradient(plate * delta)

    def fold(self) -> None:
        """Fold delta into base plates:  new_plate = plate ⊙ delta, delta → +1.

        Ternary × ternary = ternary. No information loss. After folding,
        the effective weights are identical but delta is reset for the next
        round of TD corrections.

        Call this between training phases to consolidate learned corrections.
        """
        if not self._delta_enabled:
            return

        if self.delta1 is not None:
            self.plate1 = mx.sign(self.plate1 * self.delta1)
            self.delta1 = mx.ones((self.d_out, self.d_in))

        if self.delta2 is not None and self.plate2 is not None:
            self.plate2 = mx.sign(self.plate2 * self.delta2)
            self.delta2 = mx.ones((self.d_out, self.d_in))

        mx.eval(self.plate1, self.delta1)
        if self.plate2 is not None:
            mx.eval(self.plate2, self.delta2)

    def __call__(self, x: mx.array) -> mx.array:
        """Forward: plate × input with per-row gamma scaling.

        When delta plates are enabled, uses effective = plate ⊙ delta.
        """
        # plate1 contribution
        eff1 = self._effective(self.plate1, self.delta1)
        out = (x @ eff1.T) * self.gamma1

        # plate2 contribution (if 2-plate)
        if self.plate2 is not None:
            eff2 = self._effective(self.plate2, self.delta2)
            out = out + (x @ eff2.T) * self.gamma2

        return out


# ══════════════════════════════════════════════════════════════════════
# SwiGLU FFN (the instruction decoder)
# ══════════════════════════════════════════════════════════════════════

class TernaryFFN(nn.Module):
    """SwiGLU FFN with ternary plates.

    gate_plate @ x → silu → mask (S3: resource allocation, 89% kill)
    up_plate @ x → operands
    mask × operands → surviving reductions only
    down_plate @ result → accumulate to residual

    This is NOT an approximation of a float FFN.
    This IS a holographic lookup table. The gate beamforms.
    """

    def __init__(self, d_model: int, d_ff: int, n_plates: int = 2):
        super().__init__()
        self.gate_plate = TernaryPlate(d_ff, d_model, n_plates)
        self.up_plate = TernaryPlate(d_ff, d_model, n_plates)
        self.down_plate = TernaryPlate(d_model, d_ff, n_plates)

    def __call__(self, x: mx.array) -> mx.array:
        """SwiGLU forward: silu(gate(x)) * up(x) → down → residual."""
        gate = nn.silu(self.gate_plate(x))   # Beamform: which reductions?
        up = self.up_plate(x)                 # Load operands
        hidden = gate * up                    # Execute (89% near-zero)
        return self.down_plate(hidden)        # Accumulate


# ══════════════════════════════════════════════════════════════════════
# Attention (the router / beta reduction executor)
# ══════════════════════════════════════════════════════════════════════

class FullAttention(nn.Module):
    """Multi-head attention with GQA, QK-norm, and HPE. Content-adaptive routing.

    Used in COMPUTE and LINK zones where the reduction graph is built
    and routing must adapt per-input (cross-input correlation 0.38-0.49).

    Three mechanisms ported from v14 + Qwen3 teacher:
      q_norm/k_norm:  RMSNorm(d_head) per-head after projection (from Qwen3)
                      Normalizes Q/K to unit RMS → only direction matters for routing.
      HPE rotation:   Crystal-frequency rotation on K in first n_eigen_pairs dim pairs.
                      Encodes relative log-position via holographic lens physics.
      Decay bias:     -α·log(|i-j|+1) added to attention scores.
                      Learnable α per stride (initialized at 1.18 from v14 universal).
    """

    def __init__(self, d_model: int, n_heads: int, n_kv_heads: int,
                 config: Optional[V15Config] = None):
        super().__init__()
        self.n_heads = n_heads
        self.n_kv_heads = n_kv_heads
        self.d_head = d_model // n_heads
        self.scale = 1.0 / math.sqrt(self.d_head)

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, n_kv_heads * self.d_head, bias=False)
        self.v_proj = nn.Linear(d_model, n_kv_heads * self.d_head, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

        # Per-head QK normalization (from Qwen3 teacher architecture)
        # Normalizes each head to unit RMS, then rescales by learned weight.
        # This separates magnitude from direction — Q/K direction = routing,
        # learned weight = per-dimension importance.
        self.q_norm = nn.RMSNorm(self.d_head)
        self.k_norm = nn.RMSNorm(self.d_head)

        # HPE: Holographic Position Encoding (from v14)
        cfg = config or V15Config()
        self.n_eigen_pairs = cfg.n_eigen_pairs

        # Crystal-derived frequencies (normalized by λ₀)
        crystal_freqs = [ev / cfg.crystal_eigenvalues[0]
                         for ev in cfg.crystal_eigenvalues[:cfg.n_eigen_pairs]]
        self._crystal_freqs = mx.array(crystal_freqs)  # (n_eigen_pairs,)

        # Learnable frequency scaling — initialized to 1.0 (full rotation)
        self.hpe_freq_scale = mx.ones((cfg.n_eigen_pairs,))

        # Learnable decay: log(α) so α = exp(log_alpha) is always positive.
        # Initialized at log(1.18) from v14 universal constant.
        # Per-stride (not per-head): v14 confirmed α is universal across heads.
        self.log_alpha = mx.array(math.log(cfg.alpha_init))

        # Cache for log-distance bias matrix
        self._log_dist_cache: Optional[mx.array] = None
        self._log_dist_cache_len: int = 0

    def _get_log_distances(self, seq_len: int) -> mx.array:
        """Causal log-distance matrix: log(|i-j| + 1) for j <= i, else 0.

        Shape: (seq_len, seq_len). Cached for repeated calls with same length.
        """
        if self._log_dist_cache is not None and self._log_dist_cache_len >= seq_len:
            return self._log_dist_cache[:seq_len, :seq_len]

        # Build lower-triangular log-distance matrix
        # positions[i, j] = i - j for j <= i
        pos = mx.arange(seq_len)
        distances = pos[:, None] - pos[None, :]  # (L, L), negative above diagonal
        # log(d + 1) where d = i - j, clamped to 0 for non-causal entries
        log_dist = mx.log(mx.maximum(distances, 0).astype(mx.float32) + 1.0)
        # Zero out above diagonal (will be masked by causal mask anyway)
        causal = distances >= 0
        log_dist = mx.where(causal, log_dist, mx.zeros_like(log_dist))

        self._log_dist_cache = log_dist
        self._log_dist_cache_len = seq_len
        return log_dist

    def _apply_hpe_rotation(self, k: mx.array, seq_len: int) -> mx.array:
        """Apply HPE rotation to K: rotate first n_eigen_pairs dim pairs by
        log-distance × crystal frequency.

        K is rotated per-position relative to position 0. Since Q stays
        unrotated, the Q·K product encodes relative log-distance (like RoPE
        but log-scale and crystal-frequency).

        Args:
            k: (B, H, L, Dh) — key states (already transposed to head-first)
            seq_len: sequence length

        Returns:
            k with first 2*n_eigen_pairs dimensions rotated by position.
        """
        n_pairs = self.n_eigen_pairs
        if n_pairs == 0:
            return k

        freqs = self._crystal_freqs * self.hpe_freq_scale  # (n_pairs,)

        # Absolute position log-distances from position 0
        positions = mx.arange(seq_len, dtype=mx.float32)
        log_pos = mx.log(positions + 1.0)  # (L,) — log(pos + 1)

        # Rotation angles: (L, n_pairs)
        angles = log_pos[:, None] * freqs[None, :]
        cos_a = mx.cos(angles)  # (L, n_pairs)
        sin_a = mx.sin(angles)  # (L, n_pairs)

        # Reshape for broadcasting: (1, 1, L, n_pairs)
        cos_a = cos_a.reshape(1, 1, seq_len, n_pairs)
        sin_a = sin_a.reshape(1, 1, seq_len, n_pairs)

        # Split K into pairs for rotation: (B, H, L, n_pairs, 2)
        rot_dim = 2 * n_pairs
        k_rot = k[:, :, :, :rot_dim].reshape(*k.shape[:3], n_pairs, 2)
        k_pass = k[:, :, :, rot_dim:]  # dimensions that don't rotate

        # Givens rotation per pair: [cos -sin; sin cos] @ [k0; k1]
        k0 = k_rot[:, :, :, :, 0]  # (B, H, L, n_pairs)
        k1 = k_rot[:, :, :, :, 1]
        k0_rot = k0 * cos_a - k1 * sin_a
        k1_rot = k0 * sin_a + k1 * cos_a

        # Reassemble: (B, H, L, n_pairs, 2) → (B, H, L, rot_dim)
        k_rotated = mx.stack([k0_rot, k1_rot], axis=-1).reshape(*k.shape[:3], rot_dim)

        # Concatenate rotated + pass-through dimensions
        return mx.concatenate([k_rotated, k_pass], axis=-1)

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        B, L, D = x.shape
        d_head = self.d_head

        # Project
        q = self.q_proj(x).reshape(B, L, self.n_heads, d_head)
        k = self.k_proj(x).reshape(B, L, self.n_kv_heads, d_head)
        v = self.v_proj(x).reshape(B, L, self.n_kv_heads, d_head).transpose(0, 2, 1, 3)

        # Per-head QK normalization (Qwen3-style)
        # q_norm/k_norm: RMSNorm on last dim (d_head), applied per-head
        q = self.q_norm(q)
        k = self.k_norm(k)

        # Transpose to (B, H, L, Dh)
        q = q.transpose(0, 2, 1, 3)
        k = k.transpose(0, 2, 1, 3)

        # HPE: rotate K by crystal frequencies × log-position
        k = self._apply_hpe_rotation(k, L)

        # GQA: repeat KV heads
        if self.n_kv_heads < self.n_heads:
            repeats = self.n_heads // self.n_kv_heads
            k = mx.repeat(k, repeats, axis=1)
            v = mx.repeat(v, repeats, axis=1)

        # Scaled dot-product attention
        scores = (q @ k.transpose(0, 1, 3, 2)) * self.scale

        # Learnable log-decay bias: -α·log(|i-j|+1)
        alpha = mx.exp(self.log_alpha)
        log_dist = self._get_log_distances(L)
        scores = scores - alpha * log_dist

        if mask is not None:
            scores = scores + mask
        weights = mx.softmax(scores, axis=-1)
        attn_out = (weights @ v).transpose(0, 2, 1, 3).reshape(B, L, D)

        return self.o_proj(attn_out)


class LinearAttention(nn.Module):
    """Simplified linear attention (Mamba-inspired). Structural routing.

    Used in CLASSIFY and EMIT zones where attention is input-independent
    (cross-input correlation 0.95+). O(N) cost, no softmax.

    This is a placeholder — production version would use proper
    Mamba/GLA recurrence. For now: causal linear attention with
    feature map φ(x) = elu(x) + 1.
    """

    def __init__(self, d_model: int, n_heads: int):
        super().__init__()
        self.n_heads = n_heads
        self.d_head = d_model // n_heads

        self.q_proj = nn.Linear(d_model, d_model, bias=False)
        self.k_proj = nn.Linear(d_model, d_model, bias=False)
        self.v_proj = nn.Linear(d_model, d_model, bias=False)
        self.o_proj = nn.Linear(d_model, d_model, bias=False)

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        B, L, D = x.shape
        d_head = self.d_head

        q = self.q_proj(x).reshape(B, L, self.n_heads, d_head)
        k = self.k_proj(x).reshape(B, L, self.n_heads, d_head)
        v = self.v_proj(x).reshape(B, L, self.n_heads, d_head)

        # Feature map: φ(x) = elu(x) + 1 (non-negative)
        q = nn.elu(q) + 1.0
        k = nn.elu(k) + 1.0

        # Causal linear attention via cumulative sum
        # S_t = sum_{i<=t} φ(k_i) ⊗ v_i
        # out_t = φ(q_t) @ S_t / (φ(q_t) @ sum_{i<=t} φ(k_i))
        kv = mx.expand_dims(k, axis=-1) * mx.expand_dims(v, axis=-2)  # (B, L, H, d, d)
        kv_cumsum = mx.cumsum(kv, axis=1)  # cumulative outer products
        k_cumsum = mx.cumsum(k, axis=1)    # cumulative keys

        # Numerator: q @ cumulative(kv)
        num = mx.sum(mx.expand_dims(q, axis=-1) * kv_cumsum, axis=-2)  # (B, L, H, d)
        # Denominator: q @ cumulative(k)
        den = mx.sum(q * k_cumsum, axis=-1, keepdims=True) + 1e-6

        out = (num / den).reshape(B, L, D)
        return self.o_proj(out)


# ══════════════════════════════════════════════════════════════════════
# Stride (one autonomous VSM unit)
# ══════════════════════════════════════════════════════════════════════

class Stride(nn.Module):
    """One stride in the tensor statechart. An autonomous VSM.

    s5: plate (identity — what this stride computes)
    s4: attention (intelligence — how it routes)
    s3: gate within FFN (control — which neurons fire)
    s2: RMSNorm + residual (coordination)
    s1: forward pass (operations)
    """

    def __init__(self, config: V15Config, spec: StrideSpec):
        super().__init__()
        self.spec = spec
        self.zone = spec.zone

        # s2: coordination (RMSNorm before each sub-layer)
        self.attn_norm = nn.RMSNorm(config.d_model)
        self.ffn_norm = nn.RMSNorm(config.d_model)

        # s4: attention (the router)
        if spec.attn_type == AttnType.FULL:
            self.attn = FullAttention(config.d_model, config.n_heads, config.n_kv_heads,
                                      config=config)
        else:
            self.attn = LinearAttention(config.d_model, config.n_heads)

        # s5 + s3 + s1: FFN (the plate IS the identity, gate IS control)
        self.ffn = TernaryFFN(config.d_model, config.d_ff, spec.n_plates)

    def __call__(self, x: mx.array, mask: Optional[mx.array] = None) -> mx.array:
        """Forward: attention + FFN with residual connections."""
        # Attention (s4: routing)
        h = self.attn_norm(x)
        x = x + self.attn(h, mask=mask)

        # FFN (s5: program, s3: gate, s1: compute)
        h = self.ffn_norm(x)
        x = x + self.ffn(h)

        return x


# ══════════════════════════════════════════════════════════════════════
# Tensor Statechart (the complete model)
# ══════════════════════════════════════════════════════════════════════

class TensorStatechart(nn.Module):
    """Crystal-native student model. A viable system that IS a statechart.

    State = residual stream
    Transitions = strides (each an autonomous VSM)
    Zones = macro-states (CLASSIFY → COMPUTE → LINK → EMIT)
    Algedonic = fire alarm (S1 → S5 direct)

    Load plates from disk = load a new program.
    Same architecture, different plates = different computation.
    """

    def __init__(self, config: V15Config):
        super().__init__()
        self.config = config

        # Embedding (token → R^d_model)
        self.embed = nn.Embedding(config.vocab_size, config.d_model)

        # Strides (the statechart transitions)
        specs = config.stride_specs()
        self.strides = [Stride(config, spec) for spec in specs]

        # Final norm + LM head
        self.final_norm = nn.RMSNorm(config.d_model)
        self.lm_head = nn.Linear(config.d_model, config.vocab_size, bias=False)

        # Algedonic monitor (fire alarm)
        self.algedonic = AlgedonicMonitor(config)

        # Causal mask cache
        self._causal_mask = None

    def set_crystal_basis(self, basis: mx.array):
        """Load crystal basis for algedonic coherence checks.

        Args:
            basis: (n_combinators, d_model) — the S5 identity fingerprints
        """
        self.algedonic.crystal_basis = basis

    # ── Delta plate management ──────────────────────────────────────

    def enable_delta_plates(self) -> int:
        """Enable delta plates on all TernaryPlate modules in the model.

        Returns the number of delta plate pairs activated.
        """
        count = 0
        for stride in self.strides:
            for plate_name in ("gate_plate", "up_plate", "down_plate"):
                plate: TernaryPlate = getattr(stride.ffn, plate_name)
                plate.enable_delta()
                count += 1
        return count

    def disable_delta_plates(self) -> None:
        """Disable delta plates on all TernaryPlate modules."""
        for stride in self.strides:
            for plate_name in ("gate_plate", "up_plate", "down_plate"):
                plate: TernaryPlate = getattr(stride.ffn, plate_name)
                plate.disable_delta()

    def fold_delta_plates(self) -> None:
        """Fold all delta plates into base plates across the model.

        new_plate = plate ⊙ delta; delta → +1. Lossless consolidation.
        """
        for stride in self.strides:
            for plate_name in ("gate_plate", "up_plate", "down_plate"):
                plate: TernaryPlate = getattr(stride.ffn, plate_name)
                plate.fold()

    def collect_delta_params(self) -> list[tuple[str, TernaryPlate, str]]:
        """Collect all (name, plate_module, which_delta) tuples for TD.

        Returns a list of (identifier, TernaryPlate, "delta1"|"delta2") for
        every active delta plate in the model. TD iterates this to accumulate
        moments and commit flips.

        Only returns entries where the delta is not None (i.e., enabled).
        """
        params = []
        for si, stride in enumerate(self.strides):
            for plate_name in ("gate_plate", "up_plate", "down_plate"):
                plate: TernaryPlate = getattr(stride.ffn, plate_name)
                if not plate.delta_enabled:
                    continue
                name_prefix = f"strides.{si}.ffn.{plate_name}"
                if plate.delta1 is not None:
                    params.append((f"{name_prefix}.delta1", plate, "delta1"))
                if plate.delta2 is not None:
                    params.append((f"{name_prefix}.delta2", plate, "delta2"))
        return params

    def _get_causal_mask(self, seq_len: int) -> mx.array:
        """Causal attention mask."""
        if self._causal_mask is None or self._causal_mask.shape[-1] < seq_len:
            mask = mx.full((seq_len, seq_len), -1e9)
            mask = mx.triu(mask, k=1)
            self._causal_mask = mask
        return self._causal_mask[:seq_len, :seq_len]

    def __call__(
        self,
        input_ids: mx.array,
        return_algedonic: bool = False,
        return_residuals: bool = False,
    ) -> dict:
        """Forward pass through the tensor statechart.

        Args:
            input_ids: (batch, seq_len) token IDs
            return_algedonic: if True, include per-stride health signals
            return_residuals: if True, include per-stride residual stream snapshots

        Returns:
            dict with 'logits' and optionally 'algedonic_signals', 'residuals'
        """
        B, L = input_ids.shape

        # Embed
        x = self.embed(input_ids)

        # Causal mask (for full attention strides)
        mask = self._get_causal_mask(L)

        # Reset algedonic state
        self.algedonic.reset()

        # Execute statechart: stride by stride
        signals = []
        residuals = [] if return_residuals else None
        for stride in self.strides:
            x = stride(x, mask=mask)

            # Capture residual stream snapshot (for combinator profiling)
            if return_residuals:
                residuals.append(x)

            # Algedonic check (fire alarm)
            if return_algedonic:
                sig = self.algedonic.check(x, stride.spec.index, stride.zone)
                signals.append((stride.spec.index, stride.zone, sig))
                if sig != AlgedonicSignal.OK:
                    break  # HALT — don't continue

        # Final norm + logits
        x = self.final_norm(x)
        logits = self.lm_head(x)

        result = {"logits": logits}
        if return_algedonic:
            result["algedonic_signals"] = signals
        if return_residuals:
            result["residuals"] = residuals
        return result

    def count_parameters(self) -> dict:
        """Count parameters by zone and component."""
        counts = {"total": 0, "by_zone": {}, "embedding": 0, "lm_head": 0}

        # Embedding
        n_embed = self.config.vocab_size * self.config.d_model
        counts["embedding"] = n_embed
        counts["total"] += n_embed

        # LM head (tied or separate)
        n_lm = self.config.vocab_size * self.config.d_model
        counts["lm_head"] = n_lm
        counts["total"] += n_lm

        # Per-zone
        for zone in Zone:
            counts["by_zone"][zone.name] = 0

        for stride in self.strides:
            zone = stride.zone
            # FFN: 3 plates × d_ff × d_model × n_plates + gammas
            n_plates = stride.spec.n_plates
            n_ffn = 3 * self.config.d_ff * self.config.d_model * n_plates
            n_ffn += 3 * self.config.d_ff * n_plates  # gammas

            # Attention: Q + K + V + O projections
            d_kv = self.config.n_kv_heads * self.config.d_head
            n_attn = (
                self.config.d_model * self.config.d_model  # Q
                + self.config.d_model * d_kv              # K
                + self.config.d_model * d_kv              # V
                + self.config.d_model * self.config.d_model  # O
            )

            n_stride = n_ffn + n_attn
            counts["by_zone"][zone.name] += n_stride
            counts["total"] += n_stride

        return counts

    def storage_estimate_mb(self) -> dict:
        """Estimate storage in MB (ternary plates at 2 bits, attention at float16)."""
        est = {}

        # Embedding: float16
        est["embedding"] = self.config.vocab_size * self.config.d_model * 2 / 1e6

        # Per zone
        for zone in Zone:
            est[zone.name] = 0.0

        for stride in self.strides:
            zone = stride.zone
            n_plates = stride.spec.n_plates

            # FFN: ternary (2 bits per value per plate)
            ffn_values = 3 * self.config.d_ff * self.config.d_model
            ffn_mb = ffn_values * n_plates * 2 / 8 / 1e6  # 2 bits per plate
            ffn_mb += 3 * self.config.d_ff * n_plates * 4 / 1e6  # gammas (float32)

            # Attention: float16
            d_kv = self.config.n_kv_heads * self.config.d_head
            attn_params = (
                self.config.d_model * self.config.d_model * 2  # Q + O
                + self.config.d_model * d_kv * 2               # K + V
            )
            attn_mb = attn_params * 2 / 1e6  # float16

            est[zone.name] += ffn_mb + attn_mb

        est["total"] = sum(est.values())
        return est
