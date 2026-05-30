"""Extract Ternary Plate — Teacher FFN weights → ternary {-1, 0, +1}.

Session 172. Direct extraction of FFN holographic plates from a teacher
model. The hierarchy tells us: the plate IS the program. Attention is
derived. Extract the plate, verify with the hologram reader.

Procedure per FFN layer:
  1. Load gate_proj, up_proj, down_proj weights
  2. For each weight matrix:
     a. Magnitude |W| per position
     b. Bottom 30% by magnitude → zeros (lattice backbone)
     c. Non-zero positions → sign(W) = ±1 (interference pattern)
     d. Gamma = per-row RMS of original W (contrast scalar)
  3. Save as ternary int8 + gamma fp16

Priority order (from execution hierarchy):
  gate_proj signs > up_proj signs > zeros > down_proj signs > gamma
  Gate is the beamformer (89% kill rate). Get gate right first.

Verification:
  - sign(W) @ x correlation with W @ x
  - Reconstruction quality: ternary × gamma vs original
  - Hologram reader opcode map comparison
  - β_apply direction preservation

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/extract_ternary_plate.py --model Qwen/Qwen3-0.6B
    uv run python scripts/experiments/extract_ternary_plate.py --model Qwen/Qwen3-0.6B --zero-frac 0.3
    uv run python scripts/experiments/extract_ternary_plate.py --model Qwen/Qwen3-0.6B --verify

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RESULTS_BASE = Path(__file__).parent.parent.parent / "results" / "ternary-plates"


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)
    print(msg)


# ══════════════════════════════════════════════════════════════════════
# Extraction Core
# ══════════════════════════════════════════════════════════════════════

@dataclass
class PlateStats:
    """Statistics for one extracted ternary plate (one weight matrix)."""
    name: str
    shape: tuple
    n_params: int
    n_zeros: int
    n_pos: int
    n_neg: int
    zero_frac: float
    # Quality metrics
    sign_correlation: float = 0.0        # cos(sign(W)@x, W@x)
    reconstruction_cos: float = 0.0       # cos(ternary*gamma @ x, W @ x)
    reconstruction_mse: float = 0.0       # MSE(ternary*gamma, W) / MSE(W, 0)
    gamma_stats: dict = field(default_factory=dict)

    def to_dict(self):
        return {k: v for k, v in self.__dict__.items() if v or v == 0}


@dataclass
class LayerPlate:
    """Complete ternary extraction for one transformer layer."""
    layer_idx: int
    gate: PlateStats = None
    up: PlateStats = None
    down: PlateStats = None
    # Aggregate quality
    avg_sign_corr: float = 0.0
    avg_recon_cos: float = 0.0


def extract_weight_to_ternary(
    W: np.ndarray,
    name: str,
    zero_frac: float = 0.30,
    n_test_vecs: int = 32,
) -> tuple[np.ndarray, np.ndarray, PlateStats]:
    """Extract one weight matrix to ternary plate + gamma.

    Args:
        W: float weight matrix (d_out, d_in)
        name: identifier for logging
        zero_frac: fraction of positions to zero out (by magnitude)
        n_test_vecs: number of random test vectors for quality measurement

    Returns:
        ternary: int8 matrix {-1, 0, +1} same shape as W
        gamma: float16 per-row scale (d_out,)
        stats: extraction quality statistics
    """
    d_out, d_in = W.shape
    n_params = d_out * d_in

    # ── Step 1: Compute magnitude and find zero positions ──
    magnitudes = np.abs(W)

    # Global threshold: bottom zero_frac by magnitude → zeros
    flat_mags = magnitudes.ravel()
    threshold = np.percentile(flat_mags, zero_frac * 100)

    # ── Step 2: Build ternary plate ──
    ternary = np.sign(W).astype(np.int8)  # {-1, 0, +1}
    zero_mask = magnitudes <= threshold
    ternary[zero_mask] = 0

    n_zeros = int(np.sum(ternary == 0))
    n_pos = int(np.sum(ternary == 1))
    n_neg = int(np.sum(ternary == -1))
    actual_zero_frac = n_zeros / n_params

    # ── Step 3: Compute gamma (per-row RMS of original, non-zero positions) ──
    # gamma[i] = RMS of W[i, j] where ternary[i, j] != 0
    gamma = np.zeros(d_out, dtype=np.float32)
    for i in range(d_out):
        nonzero_mask = ternary[i] != 0
        if nonzero_mask.any():
            gamma[i] = np.sqrt(np.mean(W[i, nonzero_mask] ** 2))
        else:
            gamma[i] = 0.0

    gamma_fp16 = gamma.astype(np.float16)

    # ── Step 4: Quality measurement ──
    rng = np.random.default_rng(42)
    test_vecs = rng.standard_normal((n_test_vecs, d_in)).astype(np.float32)

    # sign(W) @ x vs W @ x correlation
    sign_W = np.sign(W).astype(np.float32)
    Wx = W @ test_vecs.T          # (d_out, n_test)
    sign_Wx = sign_W @ test_vecs.T  # (d_out, n_test)

    # Flatten for overall correlation
    Wx_flat = Wx.ravel()
    sign_flat = sign_Wx.ravel()
    norm_W = np.linalg.norm(Wx_flat)
    norm_s = np.linalg.norm(sign_flat)
    sign_corr = float(np.dot(Wx_flat, sign_flat) / (norm_W * norm_s + 1e-10))

    # Reconstruction: (ternary * gamma[:, None]) @ x vs W @ x
    reconstructed = (ternary.astype(np.float32) * gamma[:, None])
    recon_Wx = reconstructed @ test_vecs.T
    recon_flat = recon_Wx.ravel()
    norm_r = np.linalg.norm(recon_flat)
    recon_cos = float(np.dot(Wx_flat, recon_flat) / (norm_W * norm_r + 1e-10))

    # Relative MSE
    mse_recon = float(np.mean((Wx_flat - recon_flat) ** 2))
    mse_baseline = float(np.mean(Wx_flat ** 2))
    rel_mse = mse_recon / (mse_baseline + 1e-10)

    stats = PlateStats(
        name=name,
        shape=W.shape,
        n_params=n_params,
        n_zeros=n_zeros,
        n_pos=n_pos,
        n_neg=n_neg,
        zero_frac=actual_zero_frac,
        sign_correlation=sign_corr,
        reconstruction_cos=recon_cos,
        reconstruction_mse=rel_mse,
        gamma_stats={
            "mean": float(np.mean(gamma)),
            "std": float(np.std(gamma)),
            "min": float(np.min(gamma)),
            "max": float(np.max(gamma)),
            "median": float(np.median(gamma)),
        },
    )

    return ternary, gamma_fp16, stats


# ══════════════════════════════════════════════════════════════════════
# Full Model Extraction
# ══════════════════════════════════════════════════════════════════════

class TernaryPlateExtractor:
    """Extract all FFN layers from a teacher to ternary plates."""

    def __init__(
        self,
        model_name: str,
        device: str = "auto",
        zero_frac: float = 0.30,
        verify: bool = False,
    ):
        self.model_name = model_name
        self.raw_device = device
        self.zero_frac = zero_frac
        self.verify = verify
        self.model = None
        self.tokenizer = None
        self.results_dir = RESULTS_BASE / model_name.replace("/", "_")
        self.results_dir.mkdir(parents=True, exist_ok=True)

    def run(self):
        t0 = time.time()
        log(f"\n{'═' * 70}")
        log(f"  Ternary Plate Extraction — {self.model_name}")
        log(f"  Zero fraction: {self.zero_frac:.0%}")
        log(f"{'═' * 70}")

        # ── Load model ──
        log(f"\n  Loading {self.model_name}...")
        self.tokenizer = AutoTokenizer.from_pretrained(
            self.model_name, trust_remote_code=True)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        if self.raw_device == "auto":
            if torch.cuda.is_available():
                dev = "cuda"
            elif hasattr(torch.backends, "mps") and torch.backends.mps.is_available():
                dev = "mps"
            else:
                dev = "cpu"
        else:
            dev = self.raw_device

        self.model = AutoModelForCausalLM.from_pretrained(
            self.model_name, torch_dtype=torch.bfloat16,
            device_map=dev if dev != "mps" else "auto",
            low_cpu_mem_usage=True, trust_remote_code=True,
        )
        self.model.eval()

        config = self.model.config
        n_layers = config.num_hidden_layers
        d_model = config.hidden_size
        d_ff = getattr(config, "intermediate_size", d_model * 4)

        log(f"  Loaded: {n_layers} layers, d={d_model}, d_ff={d_ff}")

        # Get layers
        layers = None
        for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
            obj = self.model
            try:
                for part in attr_path.split("."):
                    obj = getattr(obj, part)
                layers = list(obj)
                break
            except AttributeError:
                continue

        if layers is None:
            log("  ⚠ Cannot find transformer layers")
            return

        # ── Extract each layer ──
        all_layer_plates = []
        total_params = 0
        total_zeros = 0
        all_sign_corrs = []
        all_recon_cos = []

        plates_dir = self.results_dir / "plates"
        plates_dir.mkdir(exist_ok=True)

        for li in range(n_layers):
            layer = layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            layer_plate = LayerPlate(layer_idx=li)

            # Determine depth zone
            depth_frac = li / max(1, n_layers - 1)
            if depth_frac < 0.50:
                zone = "SILENT"
            elif depth_frac < 0.85:
                zone = "ENRICH"
            elif depth_frac < 0.93:
                zone = "SUPPRESS"
            else:
                zone = "COMMIT"

            # Extract each projection
            projections = []
            if hasattr(mlp, "gate_proj"):
                projections = [
                    ("gate", mlp.gate_proj.weight),
                    ("up", mlp.up_proj.weight),
                    ("down", mlp.down_proj.weight),
                ]
            elif hasattr(mlp, "dense_h_to_4h"):
                combined = mlp.dense_h_to_4h.weight
                d_ff_half = combined.shape[0] // 2
                projections = [
                    ("gate", combined[:d_ff_half]),
                    ("up", combined[d_ff_half:]),
                    ("down", mlp.dense_4h_to_h.weight),
                ]

            for proj_name, weight_tensor in projections:
                W = weight_tensor.detach().cpu().float().numpy()

                ternary, gamma, stats = extract_weight_to_ternary(
                    W, f"L{li:02d}_{proj_name}", self.zero_frac
                )

                # Save plate
                np.save(plates_dir / f"L{li:02d}_{proj_name}_ternary.npy", ternary)
                np.save(plates_dir / f"L{li:02d}_{proj_name}_gamma.npy", gamma)

                if proj_name == "gate":
                    layer_plate.gate = stats
                elif proj_name == "up":
                    layer_plate.up = stats
                elif proj_name == "down":
                    layer_plate.down = stats

                total_params += stats.n_params
                total_zeros += stats.n_zeros
                all_sign_corrs.append(stats.sign_correlation)
                all_recon_cos.append(stats.reconstruction_cos)

                del W, ternary, gamma

            # Aggregate per-layer quality
            plate_stats = [s for s in [layer_plate.gate, layer_plate.up, layer_plate.down] if s]
            if plate_stats:
                layer_plate.avg_sign_corr = float(np.mean([s.sign_correlation for s in plate_stats]))
                layer_plate.avg_recon_cos = float(np.mean([s.reconstruction_cos for s in plate_stats]))

            all_layer_plates.append(layer_plate)

            if li % max(1, n_layers // 8) == 0:
                log(f"    L{li:02d} [{zone:>8}]: sign_corr={layer_plate.avg_sign_corr:.4f}  "
                    f"recon_cos={layer_plate.avg_recon_cos:.4f}  "
                    f"zeros={layer_plate.gate.zero_frac:.0%}" if layer_plate.gate else "")

        # ── Summary ──
        total_ternary_bits = total_params * 1.85  # ternary encoding
        total_original_bits = total_params * 16   # bf16
        compression = total_original_bits / total_ternary_bits

        elapsed = time.time() - t0

        log(f"\n{'═' * 70}")
        log(f"  EXTRACTION SUMMARY: {self.model_name}")
        log(f"{'═' * 70}")
        log(f"  Layers extracted:    {n_layers}")
        log(f"  Total FFN params:    {total_params:,}")
        log(f"  Total zeros:         {total_zeros:,} ({total_zeros/total_params:.1%})")
        log(f"  Ternary size:        {total_ternary_bits/8/1024/1024:.1f} MB")
        log(f"  Original size:       {total_original_bits/8/1024/1024:.1f} MB")
        log(f"  Compression:         {compression:.1f}×")
        log(f"  Avg sign correlation: {np.mean(all_sign_corrs):.4f}")
        log(f"  Avg reconstruction:   {np.mean(all_recon_cos):.4f}")
        log(f"  Extraction time:      {elapsed:.1f}s")

        # Per-zone quality
        log(f"\n  Per-zone quality:")
        for zone_name, zone_start, zone_end in [
            ("SILENT", 0, 0.50), ("ENRICH", 0.50, 0.85),
            ("SUPPRESS", 0.85, 0.93), ("COMMIT", 0.93, 1.01)
        ]:
            zone_plates = [
                lp for lp in all_layer_plates
                if zone_start <= lp.layer_idx / max(1, n_layers - 1) < zone_end
            ]
            if zone_plates:
                avg_sc = np.mean([lp.avg_sign_corr for lp in zone_plates])
                avg_rc = np.mean([lp.avg_recon_cos for lp in zone_plates])
                log(f"    {zone_name:>8}: sign_corr={avg_sc:.4f}  recon_cos={avg_rc:.4f}  "
                    f"({len(zone_plates)} layers)")

        # Per-projection quality
        log(f"\n  Per-projection quality (averaged across layers):")
        for proj_name, getter in [
            ("gate", lambda lp: lp.gate),
            ("up", lambda lp: lp.up),
            ("down", lambda lp: lp.down)
        ]:
            stats_list = [getter(lp) for lp in all_layer_plates if getter(lp)]
            if stats_list:
                avg_sc = np.mean([s.sign_correlation for s in stats_list])
                avg_rc = np.mean([s.reconstruction_cos for s in stats_list])
                avg_mse = np.mean([s.reconstruction_mse for s in stats_list])
                log(f"    {proj_name:>8}: sign_corr={avg_sc:.4f}  recon_cos={avg_rc:.4f}  "
                    f"rel_mse={avg_mse:.4f}")

        # Depth profile
        log(f"\n  Depth profile (reconstruction cosine):")
        for lp in all_layer_plates:
            depth = lp.layer_idx / max(1, n_layers - 1)
            bar_len = int(lp.avg_recon_cos * 40) if lp.avg_recon_cos > 0 else 0
            bar = '█' * bar_len + '░' * (40 - bar_len)
            log(f"    L{lp.layer_idx:02d} ({depth:.2f}): {lp.avg_recon_cos:.4f} {bar}")

        # ── Save extraction manifest ──
        manifest = {
            "model": self.model_name,
            "n_layers": n_layers,
            "d_model": d_model,
            "d_ff": d_ff,
            "zero_frac": self.zero_frac,
            "total_params": total_params,
            "total_zeros": total_zeros,
            "compression_ratio": compression,
            "avg_sign_correlation": float(np.mean(all_sign_corrs)),
            "avg_reconstruction_cos": float(np.mean(all_recon_cos)),
            "extraction_time_s": elapsed,
            "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            "per_layer": [
                {
                    "layer": lp.layer_idx,
                    "sign_corr": lp.avg_sign_corr,
                    "recon_cos": lp.avg_recon_cos,
                    "gate": lp.gate.to_dict() if lp.gate else None,
                    "up": lp.up.to_dict() if lp.up else None,
                    "down": lp.down.to_dict() if lp.down else None,
                }
                for lp in all_layer_plates
            ],
        }

        manifest_path = self.results_dir / "manifest.json"
        with open(manifest_path, "w") as f:
            json.dump(manifest, f, indent=2, default=str)
        log(f"\n  Saved manifest to {manifest_path}")
        log(f"  Plates saved to {plates_dir}/")

        # ── Optional: Verification with hologram reader ──
        if self.verify:
            self._verify_extraction(layers, all_layer_plates, n_layers, d_model, d_ff)

        # Cleanup
        del self.model
        self.model = None
        gc.collect()

        log(f"\n  ✅ Extraction complete in {elapsed:.1f}s")
        log(f"  Output: {self.results_dir}")

    def _verify_extraction(self, layers, all_layer_plates, n_layers, d_model, d_ff):
        """Verify by reconstructing FFN output and comparing."""
        log(f"\n{'═' * 70}")
        log(f"  VERIFICATION: Ternary vs Original FFN output")
        log(f"{'═' * 70}")

        plates_dir = self.results_dir / "plates"

        # Test on random inputs
        rng = np.random.default_rng(42)
        n_test = 16
        test_inputs = rng.standard_normal((n_test, d_model)).astype(np.float32)

        layer_cos_sims = []

        for li in range(n_layers):
            layer = layers[li]
            mlp = layer.mlp if hasattr(layer, "mlp") else layer

            # Original FFN output
            if not hasattr(mlp, "gate_proj"):
                continue

            gate_w = mlp.gate_proj.weight.detach().cpu().float().numpy()
            up_w = mlp.up_proj.weight.detach().cpu().float().numpy()
            down_w = mlp.down_proj.weight.detach().cpu().float().numpy()

            # Load ternary plates + gamma
            gate_t = np.load(plates_dir / f"L{li:02d}_gate_ternary.npy")
            gate_g = np.load(plates_dir / f"L{li:02d}_gate_gamma.npy").astype(np.float32)
            up_t = np.load(plates_dir / f"L{li:02d}_up_ternary.npy")
            up_g = np.load(plates_dir / f"L{li:02d}_up_gamma.npy").astype(np.float32)
            down_t = np.load(plates_dir / f"L{li:02d}_down_ternary.npy")
            down_g = np.load(plates_dir / f"L{li:02d}_down_gamma.npy").astype(np.float32)

            cos_sims = []
            for x in test_inputs:
                # Original SwiGLU
                gate_out = gate_w @ x
                up_out = up_w @ x
                sig = 1.0 / (1.0 + np.exp(-np.clip(gate_out, -20, 20)))
                silu = gate_out * sig
                combined = silu * up_out
                original_out = down_w @ combined  # Transpose: down is (d_model, d_ff)
                # Wait — down_proj weight is (d_model, d_ff), so output = down_w @ combined
                # But combined is (d_ff,), so this should work

                # Ternary reconstruction
                gate_recon = (gate_t.astype(np.float32) * gate_g[:, None]) @ x
                up_recon = (up_t.astype(np.float32) * up_g[:, None]) @ x
                sig_r = 1.0 / (1.0 + np.exp(-np.clip(gate_recon, -20, 20)))
                silu_r = gate_recon * sig_r
                combined_r = silu_r * up_recon
                recon_out = (down_t.astype(np.float32) * down_g[:, None]) @ combined_r

                # Cosine similarity
                norm_o = np.linalg.norm(original_out)
                norm_r = np.linalg.norm(recon_out)
                if norm_o > 1e-10 and norm_r > 1e-10:
                    cos = float(np.dot(original_out, recon_out) / (norm_o * norm_r))
                else:
                    cos = 0.0
                cos_sims.append(cos)

            avg_cos = float(np.mean(cos_sims))
            layer_cos_sims.append(avg_cos)

            del gate_w, up_w, down_w, gate_t, up_t, down_t

            if li % max(1, n_layers // 8) == 0:
                depth = li / max(1, n_layers - 1)
                log(f"    L{li:02d} ({depth:.2f}): SwiGLU output cos = {avg_cos:.4f}")

        log(f"\n  Overall SwiGLU reconstruction:")
        log(f"    Avg cosine:  {np.mean(layer_cos_sims):.4f}")
        log(f"    Min cosine:  {np.min(layer_cos_sims):.4f} (L{np.argmin(layer_cos_sims):02d})")
        log(f"    Max cosine:  {np.max(layer_cos_sims):.4f} (L{np.argmax(layer_cos_sims):02d})")

        # Save verification results
        verif = {
            "per_layer_swiglu_cos": {f"L{i:02d}": v for i, v in enumerate(layer_cos_sims)},
            "avg_cos": float(np.mean(layer_cos_sims)),
            "min_cos": float(np.min(layer_cos_sims)),
            "max_cos": float(np.max(layer_cos_sims)),
        }
        with open(self.results_dir / "verification.json", "w") as f:
            json.dump(verif, f, indent=2)
        log(f"  Saved verification to {self.results_dir / 'verification.json'}")


def main():
    import argparse

    parser = argparse.ArgumentParser(
        description="Extract FFN weights to ternary plates"
    )
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="Teacher model")
    parser.add_argument("--device", default="auto", help="Device")
    parser.add_argument("--zero-frac", type=float, default=0.30,
                        help="Fraction of positions to zero (default: 0.30)")
    parser.add_argument("--verify", action="store_true",
                        help="Run SwiGLU reconstruction verification")
    args = parser.parse_args()

    extractor = TernaryPlateExtractor(
        model_name=args.model,
        device=args.device,
        zero_frac=args.zero_frac,
        verify=args.verify,
    )
    extractor.run()


if __name__ == "__main__":
    main()
