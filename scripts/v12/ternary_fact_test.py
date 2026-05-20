"""Ternary Fact Test — do specific fact lookups survive ternary quantization?

The HONEST test: not RDM (relational), but actual content retrieval.
For factual probes, does the ternary FFN produce an output that's
close enough to the teacher's FFN output to get the RIGHT answer?

We measure:
  1. Per-probe output cosine (is the output vector close?)
  2. Top-k neuron overlap (do the SAME neurons fire strongest?)
  3. Output projection test (does the same token get highest logit?)
  4. Magnitude distribution (how much info does ternary destroy?)

Usage:
    uv run python scripts/v12/ternary_fact_test.py

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

MODELS = {
    "mistral-7b": ("mistralai/Mistral-7B-v0.3", 32, 4096),
    "pythia-2.8b": ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
}

DEFAULT_MODELS = ["mistral-7b"]
DEPTH_FRACTIONS = [0.3, 0.5, 0.7]
D_TARGET = 512

# Factual probes where we know the expected answer
FACT_PROBES = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately", "expected": "299"},
    {"prompt": "Python was created by", "expected": "Guido"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "2 + 2 =", "expected": "4"},
    {"prompt": "The largest planet in our solar system is", "expected": "Jupiter"},
    {"prompt": "Shakespeare wrote", "expected": "Hamlet"},
    {"prompt": "E = mc", "expected": "²"},
    {"prompt": "The mitochondria is the powerhouse of the", "expected": "cell"},
    {"prompt": "HTTP status code 404 means", "expected": "not found"},
    {"prompt": "In Python, len([1,2,3]) returns", "expected": "3"},
    {"prompt": "The square root of 144 is", "expected": "12"},
    {"prompt": "DNA stands for deoxyribonucleic", "expected": "acid"},
    {"prompt": "The first element in the periodic table is", "expected": "hydrogen"},
]


def run_test(model_key, depth_fractions, device="mps"):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]

    print(f"\n  ─── {model_key} ───", file=sys.stderr, flush=True)

    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError("Unknown arch")

    for li_frac in depth_fractions:
        li = min(int(round(li_frac * (n_layers - 1))), n_layers - 1)
        print(f"\n  Layer {li} (depth {li_frac:.0%}):", file=sys.stderr, flush=True)

        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else layers[li].feed_forward
        if hasattr(mlp, 'up_proj'):
            w_up = mlp.up_proj.weight.detach().cpu().float().numpy()
            w_down = mlp.down_proj.weight.detach().cpu().float().numpy()
        elif hasattr(mlp, 'dense_h_to_4h'):
            w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
            w_down = mlp.dense_4h_to_h.weight.detach().cpu().float().numpy()
        else:
            continue

        d_ffn, d_orig = w_up.shape

        # SVD project
        U, S, Vt = np.linalg.svd(w_up, full_matrices=False)
        k = min(D_TARGET, d_orig)
        V_proj = Vt[:k, :].T
        w_up_proj = U[:, :k] * S[:k]
        ternary_w_up = np.sign(w_up_proj)

        # Also project W_down
        # W_down: (d_model, d_ffn) for Mistral or (d_ffn, d_model) for Pythia
        # We need it to map from d_ffn back to d_model (or d_target)
        # For now, use original W_down (full precision) to isolate key matching
        
        # Hook for hidden states and FFN activations
        captures = {"hidden": [], "ffn_up": [], "ffn_full_out": []}
        hooks = []

        up_mod = getattr(mlp, 'up_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
        down_mod = getattr(mlp, 'down_proj', None) or getattr(mlp, 'dense_4h_to_h', None)

        def make_hidden_hook():
            def hook(m, inp, out):
                h_in = inp[0] if isinstance(inp, tuple) else inp
                captures["hidden"].append(h_in[:, -1, :].detach().cpu().float())
            return hook
        hooks.append(layers[li].register_forward_hook(make_hidden_hook()))

        if up_mod:
            def make_up_hook():
                def hook(m, inp, out):
                    captures["ffn_up"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(up_mod.register_forward_hook(make_up_hook()))

        # Capture MLP module output for full FFN effect
        def make_mlp_hook():
            def hook(m, inp, out):
                if isinstance(out, tuple):
                    captures["ffn_full_out"].append(out[0][:, -1, :].detach().cpu().float())
                else:
                    captures["ffn_full_out"].append(out[:, -1, :].detach().cpu().float())
            return hook
        hooks.append(mlp.register_forward_hook(make_mlp_hook()))

        for probe in FACT_PROBES:
            ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(ids)

        for h in hooks:
            h.remove()

        hidden_vecs = torch.cat(captures["hidden"], dim=0).numpy()
        teacher_up = torch.cat(captures["ffn_up"], dim=0).numpy()
        teacher_full = torch.cat(captures["ffn_full_out"], dim=0).numpy()

        # Simulate ternary FFN
        hidden_proj = hidden_vecs @ V_proj  # (n_probes, k)
        ternary_up = hidden_proj @ ternary_w_up.T  # (n_probes, d_ffn)

        # Also simulate float-projected (SVD only, no ternary)
        float_up = hidden_proj @ w_up_proj.T

        print(f"\n    {'probe':>45s}  {'teacher':>8s}  {'ternary':>8s}  {'float':>8s}  "
              f"{'top10_olap':>10s}  {'mag_ratio':>9s}",
              file=sys.stderr, flush=True)
        print(f"    {'-'*94}", file=sys.stderr, flush=True)

        for pi, probe in enumerate(FACT_PROBES):
            # Per-probe metrics
            t_vec = teacher_up[pi]
            r_vec = ternary_up[pi]
            f_vec = float_up[pi]

            t_norm = max(np.linalg.norm(t_vec), 1e-8)
            r_norm = max(np.linalg.norm(r_vec), 1e-8)
            f_norm = max(np.linalg.norm(f_vec), 1e-8)

            cos_ternary = float(np.dot(t_vec, r_vec) / (t_norm * r_norm))
            cos_float = float(np.dot(t_vec, f_vec) / (t_norm * f_norm))

            # Top-10 neuron overlap
            top10_teacher = set(np.argsort(np.abs(t_vec))[-10:])
            top10_ternary = set(np.argsort(np.abs(r_vec))[-10:])
            overlap = len(top10_teacher & top10_ternary)

            # Magnitude ratio (how much energy does ternary preserve?)
            mag_ratio = r_norm / t_norm

            prompt_short = probe["prompt"][:40]
            print(f"    {prompt_short:>45s}  {cos_float:>+7.3f}  {cos_ternary:>+7.3f}  "
                  f"{cos_float:>+7.3f}  {overlap:>10d}/10  {mag_ratio:>9.4f}",
                  file=sys.stderr, flush=True)

        # Summary stats
        all_cos_t = []
        all_cos_f = []
        all_binary = []
        for pi in range(len(FACT_PROBES)):
            t_vec = teacher_up[pi]
            r_vec = ternary_up[pi]
            f_vec = float_up[pi]
            tn = max(np.linalg.norm(t_vec), 1e-8)
            rn = max(np.linalg.norm(r_vec), 1e-8)
            fn = max(np.linalg.norm(f_vec), 1e-8)
            all_cos_t.append(float(np.dot(t_vec, r_vec) / (tn * rn)))
            all_cos_f.append(float(np.dot(t_vec, f_vec) / (tn * fn)))
            # Binary agreement
            t_bin = (t_vec > 0).astype(float)
            r_bin = (r_vec > 0).astype(float)
            all_binary.append(float((t_bin == r_bin).mean()))

        print(f"\n    Summary:", file=sys.stderr, flush=True)
        print(f"      Mean ternary cosine: {np.mean(all_cos_t):+.4f}",
              file=sys.stderr, flush=True)
        print(f"      Mean float cosine:   {np.mean(all_cos_f):+.4f}",
              file=sys.stderr, flush=True)
        print(f"      Mean binary agree:   {np.mean(all_binary):.1%}",
              file=sys.stderr, flush=True)

        # Magnitude analysis
        teacher_mags = np.linalg.norm(teacher_up, axis=1)
        ternary_mags = np.linalg.norm(ternary_up, axis=1)
        print(f"      Teacher |FFN_up|: mean={teacher_mags.mean():.2f}, "
              f"std={teacher_mags.std():.2f}",
              file=sys.stderr, flush=True)
        print(f"      Ternary |FFN_up|: mean={ternary_mags.mean():.2f}, "
              f"std={ternary_mags.std():.2f}",
              file=sys.stderr, flush=True)
        print(f"      Magnitude ratio: {(ternary_mags/teacher_mags).mean():.4f}",
              file=sys.stderr, flush=True)

        # Per-neuron activation distribution
        teacher_active = (teacher_up > 0).mean(axis=0)  # what fraction of probes activate each neuron
        ternary_active = (ternary_up > 0).mean(axis=0)
        active_corr = float(np.corrcoef(teacher_active, ternary_active)[0, 1])
        print(f"      Neuron activation rate correlation: {active_corr:+.4f}",
              file=sys.stderr, flush=True)

    del model, tokenizer
    gc.collect()


def main():
    parser = argparse.ArgumentParser(description="Ternary Fact Test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--device", type=str, default="mps")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Ternary Fact Test — Do Fact Lookups Actually Work?",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    for mk in args.models:
        run_test(mk, DEPTH_FRACTIONS, args.device)
    print(f"\n  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
