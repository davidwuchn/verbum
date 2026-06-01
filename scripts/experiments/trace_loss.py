#!/usr/bin/env python3
"""Trace Loss — Match student opcode projections to teacher traces.

The trace loss compares a model's per-layer combinator projections against
pre-computed teacher traces. Used for trace-guided etching: train the
student to reproduce the teacher's COMPUTATION, not its weights.

Can be used as:
  1. A standalone validator: compare any model to teacher traces
  2. A loss function in training: add to next-token loss
  3. A diagnostic: which layers diverge most from the teacher?

Validation test (run standalone):
  - Loads 0.6B teacher + its own traces → trace loss ≈ 0
  - Ternary-extracts the teacher → trace loss shows magnitude gap
  - Randomly perturbs 10% of signs → trace loss spikes

Usage:
    uv run python scripts/experiments/trace_loss.py --model Qwen/Qwen3-0.6B
    uv run python scripts/experiments/trace_loss.py --model Qwen/Qwen3-0.6B --validate

License: MIT
"""

from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
RESULTS_BASE = PROJECT_ROOT / "results" / "hologram-reader"
TRACE_BASE = PROJECT_ROOT / "results" / "trace-etching"

TOP4_OPS = ["K", "I", "B", "C"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def get_layers(model) -> list:
    for attr_path in ["model.layers", "transformer.h", "gpt_neox.layers"]:
        obj = model
        try:
            for part in attr_path.split("."):
                obj = getattr(obj, part)
            return list(obj)
        except AttributeError:
            continue
    raise RuntimeError(f"Cannot find transformer layers")


def get_gate_and_down(layer):
    mlp = layer.mlp if hasattr(layer, "mlp") else layer
    if hasattr(mlp, "gate_proj"):
        return mlp.gate_proj, mlp.down_proj, "swiglu"
    if hasattr(mlp, "dense_h_to_4h"):
        return mlp.dense_h_to_4h, mlp.dense_4h_to_h, "gpt_neox"
    raise RuntimeError(f"Cannot find MLP")


# ══════════════════════════════════════════════════════════════════════
# Trace Loss Core
# ══════════════════════════════════════════════════════════════════════

class TraceLoss:
    """Compute trace divergence between a model and teacher traces.

    Teacher traces are pre-computed opcode projections per layer per input.
    The loss measures how well the model reproduces those projections.
    """

    def __init__(
        self,
        teacher_traces: np.ndarray,   # (n_inputs, n_layers, n_ops)
        fingerprints: dict[str, np.ndarray],  # op → (n_layers, d_model)
        ops: list[str],
        input_texts: list[str],
        importance: np.ndarray | None = None,  # (n_layers, d_ff)
    ):
        self.teacher_traces = teacher_traces
        self.fingerprints = fingerprints
        self.ops = ops
        self.input_texts = input_texts
        self.n_inputs, self.n_layers, self.n_ops = teacher_traces.shape

        # Layer importance weights: layers with higher mean opcode energy matter more
        mean_energy = np.mean(np.abs(teacher_traces), axis=(0, 2))  # (n_layers,)
        if mean_energy.sum() > 0:
            self.layer_weights = mean_energy / mean_energy.sum()
        else:
            self.layer_weights = np.ones(self.n_layers) / self.n_layers

        # Pre-build per-layer fingerprint matrices
        self.fp_matrices = {}  # layer_idx → (n_ops, d_model) numpy
        for li in range(self.n_layers):
            vecs = []
            for op in ops:
                fp = fingerprints.get(op)
                if fp is not None and li < fp.shape[0]:
                    v = fp[li]
                    n = np.linalg.norm(v)
                    vecs.append(v / n if n > 1e-10 else v)
                else:
                    vecs.append(np.zeros(fp.shape[1] if fp is not None else 1))
            self.fp_matrices[li] = np.stack(vecs)  # (n_ops, d_model)

    def compute_single(
        self, model, tokenizer, input_idx: int,
    ) -> dict:
        """Trace one input through the model and compare to teacher."""
        text = self.input_texts[input_idx]
        teacher = self.teacher_traces[input_idx]  # (n_layers, n_ops)

        input_ids = tokenizer(text, return_tensors="pt").input_ids
        device = next(model.parameters()).device
        input_ids = input_ids.to(device)

        layers = get_layers(model)
        ffn_caps = {}
        hooks = []

        for li in range(self.n_layers):
            try:
                _, down_mod, _ = get_gate_and_down(layers[li])
            except RuntimeError:
                continue

            def make_hook(idx):
                def hook(m, inp, out):
                    ffn_caps[idx] = out[0, -1, :].detach().cpu().float().numpy()
                return hook
            hooks.append(down_mod.register_forward_hook(make_hook(li)))

        with torch.no_grad():
            _ = model(input_ids=input_ids)

        for h in hooks:
            h.remove()

        # Project onto fingerprints and compare
        student_ops = np.zeros((self.n_layers, self.n_ops), dtype=np.float32)
        per_layer_loss = np.zeros(self.n_layers, dtype=np.float32)

        for li in range(self.n_layers):
            if li not in ffn_caps:
                continue
            ffn_vec = ffn_caps[li]
            ffn_norm = np.linalg.norm(ffn_vec)
            if ffn_norm < 1e-10:
                continue

            ffn_unit = ffn_vec / ffn_norm
            fp_mat = self.fp_matrices[li]  # (n_ops, d_model)
            projections = fp_mat @ ffn_unit  # (n_ops,)
            student_ops[li] = projections

            # Cosine distance for this layer
            t = teacher[li]
            t_norm = np.linalg.norm(t)
            s_norm = np.linalg.norm(projections)
            if t_norm > 1e-10 and s_norm > 1e-10:
                cos = np.dot(t, projections) / (t_norm * s_norm)
                per_layer_loss[li] = 1.0 - cos

        # Weighted total
        total_loss = float(np.sum(per_layer_loss * self.layer_weights))

        return {
            "total_loss": total_loss,
            "per_layer_loss": per_layer_loss,
            "student_ops": student_ops,
            "teacher_ops": teacher,
        }

    def compute_batch(
        self, model, tokenizer, indices: list[int] | None = None,
    ) -> dict:
        """Compute trace loss over multiple inputs."""
        if indices is None:
            indices = list(range(self.n_inputs))

        losses = []
        per_layer_acc = np.zeros(self.n_layers, dtype=np.float64)

        for idx in indices:
            result = self.compute_single(model, tokenizer, idx)
            losses.append(result["total_loss"])
            per_layer_acc += result["per_layer_loss"]

        per_layer_mean = per_layer_acc / len(indices)

        return {
            "mean_loss": float(np.mean(losses)),
            "std_loss": float(np.std(losses)),
            "per_layer_mean": per_layer_mean,
            "n_inputs": len(indices),
        }


# ══════════════════════════════════════════════════════════════════════
# Validation test
# ══════════════════════════════════════════════════════════════════════

def validate(model_name: str, device: str):
    """Full validation: self-trace, ternary extraction, perturbation."""
    slug = model_name.replace("/", "_")

    # Load traces
    trace_path = TRACE_BASE / slug / "teacher_traces.npz"
    if not trace_path.exists():
        log(f"  ❌ No traces at {trace_path}. Run trace_collect.py first.")
        sys.exit(1)

    data = np.load(trace_path, allow_pickle=True)
    traces = data["traces"]
    ops = list(data["op_names"])
    texts = list(data["input_texts"])
    n_layers = int(data["n_layers"])

    # Load fingerprints
    fp_path = RESULTS_BASE / slug / f"fingerprints_{slug}.npz"
    fp_data = np.load(fp_path)
    fingerprints = {op: fp_data[op] for op in ops if op in fp_data}

    log(f"  Traces: {traces.shape}, Ops: {ops}")

    # Load model
    log(f"\n  Loading {model_name}...")
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.float32, device_map=device)
    model.eval()
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    tl = TraceLoss(traces, fingerprints, ops, texts)

    # Use subset for speed
    test_indices = list(range(min(20, len(texts))))

    # ── Test 1: Self-trace (should be ~0) ─────────────────────
    log(f"\n  Test 1: Self-trace (model vs its own traces)")
    t0 = time.time()
    result = tl.compute_batch(model, tokenizer, test_indices)
    log(f"    Loss: {result['mean_loss']:.6f} ± {result['std_loss']:.6f}")
    log(f"    Time: {time.time()-t0:.1f}s")
    self_loss = result["mean_loss"]

    # ── Test 2: Ternary extraction (sign only) ────────────────
    log(f"\n  Test 2: Ternary extraction (sign(W) replaces W)")
    # Replace all 2D params with their sign
    original_params = {}
    for name, param in model.named_parameters():
        if param.ndim == 2 and min(param.shape) >= 64:
            original_params[name] = param.data.clone()
            param.data = torch.sign(param.data)

    result = tl.compute_batch(model, tokenizer, test_indices)
    log(f"    Loss: {result['mean_loss']:.6f} ± {result['std_loss']:.6f}")
    ternary_loss = result["mean_loss"]

    # Restore
    for name, orig in original_params.items():
        dict(model.named_parameters())[name].data = orig

    # ── Test 3: Random perturbation (10% sign flips) ─────────
    log(f"\n  Test 3: 10% random sign perturbation")
    original_params = {}
    for name, param in model.named_parameters():
        if param.ndim == 2 and min(param.shape) >= 64:
            original_params[name] = param.data.clone()
            mask = torch.rand_like(param.data) < 0.10
            param.data[mask] *= -1

    result = tl.compute_batch(model, tokenizer, test_indices)
    log(f"    Loss: {result['mean_loss']:.6f} ± {result['std_loss']:.6f}")
    perturbed_loss = result["mean_loss"]

    # Restore
    for name, orig in original_params.items():
        dict(model.named_parameters())[name].data = orig

    # ── Summary ───────────────────────────────────────────────
    log(f"\n{'='*60}")
    log(f"  TRACE LOSS VALIDATION — {model_name}")
    log(f"{'='*60}")
    log(f"  Self-trace (expect ~0):       {self_loss:.6f}")
    log(f"  Ternary extraction:           {ternary_loss:.6f}  ({ternary_loss/max(self_loss,1e-10):.1f}× self)")
    log(f"  10% sign perturbation:        {perturbed_loss:.6f}  ({perturbed_loss/max(self_loss,1e-10):.1f}× self)")
    log(f"{'='*60}")

    if self_loss < 0.01:
        log(f"  ✅ Self-trace near zero — trace loss is consistent")
    else:
        log(f"  ⚠  Self-trace not near zero — possible fingerprint instability")

    if ternary_loss > self_loss * 1.5:
        log(f"  ✅ Ternary extraction detected — trace loss sees the magnitude gap")
    else:
        log(f"  ⚠  Ternary not well separated from self")

    if perturbed_loss > ternary_loss:
        log(f"  ✅ Perturbation worst — trace loss is sensitive to topology damage")
    else:
        log(f"  ⚠  Perturbation not worst — unexpected")

    # Per-layer divergence for ternary
    log(f"\n  Per-layer trace loss (ternary extraction):")
    # Recompute for ternary to get per-layer
    for name, param in model.named_parameters():
        if param.ndim == 2 and min(param.shape) >= 64:
            original_params[name] = param.data.clone()
            param.data = torch.sign(param.data)

    result = tl.compute_batch(model, tokenizer, test_indices)
    per_layer = result["per_layer_mean"]
    for li in range(0, n_layers, max(1, n_layers // 10)):
        bar_len = min(20, int(per_layer[li] * 20 / max(per_layer.max(), 0.01)))
        bar = "█" * bar_len + "░" * (20 - bar_len)
        log(f"    L{li:02d}: {bar} {per_layer[li]:.4f}")

    # Restore
    for name, orig in original_params.items():
        dict(model.named_parameters())[name].data = orig

    log(f"\n  ✅ Validation complete\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B")
    parser.add_argument("--device", default="cpu")
    parser.add_argument("--validate", action="store_true",
                        help="Run full validation suite")
    args = parser.parse_args()

    if args.validate:
        validate(args.model, args.device)
    else:
        log("  Use --validate to run the validation suite")
        log("  Or import TraceLoss for use in training")


if __name__ == "__main__":
    main()
