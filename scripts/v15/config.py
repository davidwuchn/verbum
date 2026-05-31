"""v15 Configuration — Crystal-Native Tensor Statechart.

Session 174. Ablation-verified 4-zone architecture.
Each stride is an autonomous VSM. The model IS a statechart loaded from data.

Architecture (VSM, Beer 1972):
  S5: Crystal basis {K,I,B,C,D,Y,W,WHNF,β_K,β_I,β_apply,β_compose}
  S4: Two-timescale routing (CLASSIFY macro + COMPUTE micro)
  S3: SwiGLU gate (89% kill = resource allocation per stride)
  S2: Residual stream + RMSNorm (anti-oscillation)
  S1: 18 autonomous stride-VSMs

Zones (ablation-verified on Qwen3.6-27B):
  CLASSIFY (strides 0-4):  1-plate, linear attn — token recognition
  COMPUTE  (strides 5-12): 2-plate, full attn — reduction engine
  LINK     (strides 13-15): 2-plate, TBD attn — compose results
  EMIT     (strides 16-18): 2-plate, linear attn — knowledge retrieval

Statechart format:
  A checkpoint IS the statechart. Load it, execute it. The plates
  are the program. Attention is the router. The residual stream is
  the state. Each stride is a transition.

Teacher: Qwen3.6-27B (64 layers, d=5120, d_ff=17408, hybrid L+F attn)
Student: 19 strides, d=1280, d_ff=5120, hybrid linear+full attn

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum, auto
from pathlib import Path
from typing import Optional


# ══════════════════════════════════════════════════════════════════════
# Zone definitions
# ══════════════════════════════════════════════════════════════════════

class Zone(Enum):
    """Computational zones — verified by ablation (session 174)."""
    CLASSIFY = auto()  # Token recognition, program selection
    COMPUTE = auto()   # Reduction engine (Y, B, D, β_apply)
    LINK = auto()      # Compose results (B, β_K), eliminate constants
    EMIT = auto()      # Knowledge retrieval, output formatting


class AttnType(Enum):
    """Attention mechanism per stride."""
    LINEAR = auto()    # Mamba-style (O(N), structural routing)
    FULL = auto()      # Standard QKV softmax (O(N²), content-adaptive)


# ══════════════════════════════════════════════════════════════════════
# Stride specification
# ══════════════════════════════════════════════════════════════════════

@dataclass
class StrideSpec:
    """Specification for one stride in the statechart."""
    index: int
    zone: Zone
    attn_type: AttnType
    n_plates: int          # 1 or 2 (plate precision)
    teacher_layers: tuple[int, ...]  # which teacher layers map here
    stride_window: int = 0  # for strided attention (0 = full context)


# ══════════════════════════════════════════════════════════════════════
# Architecture configuration
# ══════════════════════════════════════════════════════════════════════

@dataclass
class V15Config:
    """Crystal-native tensor statechart configuration."""

    # Core dimensions
    d_model: int = 1280
    d_ff: int = 5120
    n_heads: int = 8
    n_kv_heads: int = 2       # GQA: 8 heads, 2 KV groups
    d_head: int = 160         # d_model // n_heads
    vocab_size: int = 151936  # Qwen3.6 tokenizer

    # Stride allocation (19 strides: 5 + 8 + 3 + 3)
    n_strides: int = 19

    # Crystal basis
    n_combinators: int = 12   # K,I,B,C,D,Y,W,WHNF,β_K,β_I,β_apply,β_compose

    # Teacher info (for extraction mapping)
    teacher_name: str = "Qwen/Qwen3.6-27B"
    teacher_n_layers: int = 64
    teacher_d_model: int = 5120
    teacher_d_ff: int = 17408

    # Algedonic thresholds
    norm_min: float = 0.1
    norm_max: float = 100.0
    coherence_min: float = 0.1   # fraction on crystal manifold
    divergence_ratio: float = 1.5  # dimensionality increase threshold

    # Training
    max_seq_len: int = 8192

    # Paths
    checkpoint_dir: Path = field(default_factory=lambda: Path("checkpoints/v15"))

    def stride_specs(self) -> list[StrideSpec]:
        """Generate the 19 stride specifications with teacher mapping."""
        specs = []

        # Teacher layer allocation (64 layers → 19 strides)
        # CLASSIFY: 5 strides ← teacher L0-31 (32 layers, ~6 each)
        # COMPUTE:  8 strides ← teacher L32-53 (22 layers, ~3 each)
        # LINK:     3 strides ← teacher L54-58 (5 layers, ~2 each)
        # EMIT:     3 strides ← teacher L59-63 (5 layers, ~2 each)

        teacher_map = {
            # CLASSIFY: broad strokes, ~6 teacher layers each
            0: (0, 1, 2, 3, 4, 5),
            1: (6, 7, 8, 9, 10, 11),
            2: (12, 13, 14, 15, 16, 17),
            3: (18, 19, 20, 21, 22, 23),
            4: (24, 25, 26, 27, 28, 29, 30, 31),
            # COMPUTE: fine-grained, ~3 teacher layers each
            5: (32, 33, 34),
            6: (35, 36, 37),
            7: (38, 39, 40),
            8: (41, 42, 43),
            9: (44, 45, 46),
            10: (47, 48, 49),
            11: (50, 51),
            12: (52, 53),
            # LINK: ~2 teacher layers each
            13: (54, 55),
            14: (56, 57),
            15: (58,),
            # EMIT: ~2 teacher layers each
            16: (59, 60),
            17: (61, 62),
            18: (63,),
        }

        for i in range(self.n_strides):
            if i < 5:
                zone = Zone.CLASSIFY
                attn = AttnType.LINEAR
                n_plates = 1
            elif i < 13:
                zone = Zone.COMPUTE
                attn = AttnType.FULL
                n_plates = 2
            elif i < 16:
                zone = Zone.LINK
                attn = AttnType.FULL  # composition needs adaptive routing
                n_plates = 2
            else:
                zone = Zone.EMIT
                attn = AttnType.LINEAR
                n_plates = 2

            specs.append(StrideSpec(
                index=i,
                zone=zone,
                attn_type=attn,
                n_plates=n_plates,
                teacher_layers=teacher_map[i],
            ))

        return specs

    @property
    def zone_ranges(self) -> dict[Zone, tuple[int, int]]:
        """Stride index ranges per zone."""
        return {
            Zone.CLASSIFY: (0, 4),
            Zone.COMPUTE: (5, 12),
            Zone.LINK: (13, 15),
            Zone.EMIT: (16, 18),
        }


# ══════════════════════════════════════════════════════════════════════
# Combinator names (S5 identity)
# ══════════════════════════════════════════════════════════════════════

COMBINATOR_NAMES = [
    "K", "I", "B", "C", "D", "Y", "W", "WHNF",
    "beta_K", "beta_I", "beta_apply", "beta_compose",
]

ZONE_NAMES = {
    Zone.CLASSIFY: "CLASSIFY",
    Zone.COMPUTE: "COMPUTE",
    Zone.LINK: "LINK",
    Zone.EMIT: "EMIT",
}
