#!/usr/bin/env python3
"""How much of a neural network is just the signs of its weights?

Replaces every weight with +1/-1/0 (its sign), throws away all
magnitudes, and measures how much of the computation survives.

Usage:
    pip install torch transformers
    python 01_sign_topology.py                                    # Pythia-160M (~2 min)
    python 01_sign_topology.py --model mistralai/Mistral-7B-v0.3  # any HF model
"""
import argparse
import sys
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM


def measure_sign_fidelity(W, n_samples=20):
    """cos(sign(W) @ x, W @ x) averaged over random inputs."""
    sign_W = torch.sign(W)
    rand_W = torch.sign(torch.randn_like(W))  # control: random ±1
    cos_sign, cos_rand = [], []
    for _ in range(n_samples):
        x = torch.randn(W.shape[1], device=W.device)
        full = W @ x
        cos_sign.append(F.cosine_similarity(sign_W @ x, full, dim=0).item())
        cos_rand.append(F.cosine_similarity(rand_W @ x, full, dim=0).item())
    return sum(cos_sign) / len(cos_sign), sum(cos_rand) / len(cos_rand)


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="EleutherAI/pythia-160m-deduped")
    p.add_argument("--device", default="cpu")
    p.add_argument("--samples", type=int, default=20, help="random inputs per matrix")
    args = p.parse_args()

    print(f"Loading {args.model} ...", file=sys.stderr)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=torch.float32, device_map=args.device)
    model.eval()

    rows = []
    for name, param in model.named_parameters():
        if param.ndim != 2 or min(param.shape) < 64:
            continue
        W = param.data.float()
        cs, cr = measure_sign_fidelity(W, args.samples)
        rows.append((name, W.shape, cs, cr))
        print(f"  {name:<55} sign={cs:+.4f}  random={cr:+.4f}", file=sys.stderr)

    # ── Summary ──────────────────────────────────────────────
    sign_vals = [r[2] for r in rows]
    rand_vals = [r[3] for r in rows]
    mean_sign = sum(sign_vals) / len(sign_vals)
    mean_rand = sum(rand_vals) / len(rand_vals)
    min_sign = min(sign_vals)
    max_sign = max(sign_vals)

    print(f"\n{'='*62}")
    print(f"  Model:  {args.model}")
    print(f"  Matrices tested:  {len(rows)}")
    print(f"{'='*62}")
    print(f"  cos(sign(W)@x, W@x)     mean = {mean_sign:.4f}   "
          f"[{min_sign:.4f} .. {max_sign:.4f}]")
    print(f"  cos(random(±1)@x, W@x)  mean = {mean_rand:.4f}   (control)")
    print(f"{'='*62}")
    print(f"\n  Weight signs alone carry {mean_sign*100:.1f}% of the computation.")
    print(f"  Random signs carry {abs(mean_rand)*100:.1f}%.\n")


if __name__ == "__main__":
    main()
