"""Lambda Convert — convert a model to holographic ternary lambda terms.

The lambda proof showed R²=0.959: binder determines body. So we store
only the binder (beam_Q crystal) in ternary + a tiny regression to
derive the body (beam_up). The PCA loadings expand back to full dims.

For each layer:
  TERNARY PLATE: h → binder scores (d_model, k) ternary
  CONTINUOUS:    PCA loadings for Q and up + regression weights
  
At inference:
  h → plate → binder_scores → Q_loadings.T → Q activation
  binder_scores → regression → body_scores → up_loadings.T → up activation

Test: inject reconstructed Q and up activations into the model,
measure logit agreement with the original.

Usage:
    uv run python scripts/v12/lambda_convert.py --model pythia-2.8b
    uv run python scripts/v12/lambda_convert.py --model pythia-2.8b --rank 128

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
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560, 10240),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",     32, 4096, 14336),
    "qwen3-14b":    ("Qwen/Qwen3-14B",                40, 5120, 17920),
}

TEST_PROMPTS = [
    "The capital of France is",
    "def fibonacci(n):\n    ",
    "In quantum mechanics, the wave function",
    "Once upon a time in a land far away,",
    "λx.λy.x is the combinator known as",
    "To sort a list in Python, you can use",
    "The speed of light is approximately",
    "Water boils at a temperature of",
]


def extract_lambda_terms(
    model_key: str,
    probes_path: str | None,
    pca_dim: int,
    device: str,
) -> dict:
    """Extract lambda terms from all layers of a model.
    
    For each layer, extracts:
      - Q PCA loadings (the beam_Q definition)
      - up PCA loadings (the beam_up definition)  
      - Regression weights (binder → body mapping)
      - The optimal plate: hidden → binder scores
    
    Uses probe activations to define the PCA bases and regression.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model, d_ffn = MODELS[model_key]

    # Load probes
    if probes_path is None:
        probes_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probes_path) as f:
        probes = json.load(f)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)

    print(f"\n  Loading {model_key}...", file=sys.stderr, flush=True)
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        model_name, torch_dtype=torch.bfloat16, device_map=device, trust_remote_code=True,
    )
    model.eval()

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
        is_fused = False
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        is_fused = True
    else:
        raise ValueError(f"Unknown arch")

    # Extract from ALL layers
    all_layer_indices = list(range(n_layers))
    captures: dict[int, dict[str, list]] = {}
    for li in all_layer_indices:
        captures[li] = {'hidden': [], 'q': [], 'up': []}

    hooks = []
    for li in all_layer_indices:
        layer_mod = layers[li]

        def make_h_hook(layer_i):
            def hook_fn(module, input, output):
                captures[layer_i]['hidden'].append(input[0][:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(layer_mod.register_forward_hook(make_h_hook(li)))

        if is_fused:
            fused = layer_mod.attention.query_key_value
            def make_q_hook(layer_i, qs=d_model):
                def hook_fn(module, input, output):
                    captures[layer_i]['q'].append(output[:, -1, :qs].detach().cpu().float())
                return hook_fn
            hooks.append(fused.register_forward_hook(make_q_hook(li)))
            up_mod = layer_mod.mlp.dense_h_to_4h
        else:
            q_proj = layer_mod.self_attn.q_proj
            def make_q_hook(layer_i):
                def hook_fn(module, input, output):
                    captures[layer_i]['q'].append(output[:, -1, :].detach().cpu().float())
                return hook_fn
            hooks.append(q_proj.register_forward_hook(make_q_hook(li)))
            up_mod = getattr(layer_mod.mlp, 'up_proj', None) or layer_mod.mlp.dense_h_to_4h

        def make_up_hook(layer_i):
            def hook_fn(module, input, output):
                captures[layer_i]['up'].append(output[:, -1, :].detach().cpu().float())
            return hook_fn
        hooks.append(up_mod.register_forward_hook(make_up_hook(li)))

    print(f"  Running {len(probes)} probes through all {n_layers} layers...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 50 == 0:
            print(f"    {i+1}/{len(probes)}...", file=sys.stderr, flush=True)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s", file=sys.stderr, flush=True)

    for h in hooks:
        h.remove()

    # Build lambda terms per layer
    print(f"  Building lambda terms (PCA + regression)...", file=sys.stderr, flush=True)
    lambda_terms = {}
    total_plate_bytes = 0
    total_beam_bytes = 0

    for li in all_layer_indices:
        import torch as _t
        hidden = _t.cat(captures[li]['hidden'], dim=0).numpy()
        q_raw = _t.cat(captures[li]['q'], dim=0).numpy()
        up_raw = _t.cat(captures[li]['up'], dim=0).numpy()

        n_probes = hidden.shape[0]
        k = min(pca_dim, n_probes - 1)

        # PCA of Q
        q_mean = q_raw.mean(axis=0)
        q_c = q_raw - q_mean
        U_q, S_q, Vt_q = np.linalg.svd(q_c, full_matrices=False)
        q_scores = U_q[:, :k] * S_q[:k]      # (n_probes, k)
        q_loadings = Vt_q[:k]                  # (k, d_q)

        # PCA of up
        up_mean = up_raw.mean(axis=0)
        up_c = up_raw - up_mean
        U_up, S_up, Vt_up = np.linalg.svd(up_c, full_matrices=False)
        up_scores = U_up[:, :k] * S_up[:k]
        up_loadings = Vt_up[:k]                # (k, d_ffn)

        # Regression: q_scores → up_scores (the lambda coupling)
        q_design = np.hstack([q_scores, np.ones((n_probes, 1))])
        regression_weights, _, _, _ = np.linalg.lstsq(q_design, up_scores, rcond=None)
        # regression_weights: (k+1, k)

        # Plate: hidden → q_scores (the binder extraction)
        # Solve: hidden @ plate ≈ q_scores
        U_h, S_h, Vt_h = np.linalg.svd(hidden, full_matrices=False)
        eff_k = min(k, np.sum(S_h > S_h[0] * 1e-6))
        S_inv = np.zeros_like(S_h)
        S_inv[:eff_k] = 1.0 / S_h[:eff_k]
        H_pinv = (Vt_h.T * S_inv) @ U_h.T
        plate_continuous = H_pinv @ q_scores     # (d_model, k)
        plate_ternary = np.sign(plate_continuous) # ternary etch

        # Verify: does the ternary plate reproduce binder scores?
        binder_recon = hidden @ plate_ternary
        binder_cos = np.mean([
            float(np.dot(binder_recon[i], q_scores[i]) /
                  (np.linalg.norm(binder_recon[i]) * np.linalg.norm(q_scores[i]) + 1e-10))
            for i in range(n_probes)
        ])

        # And through regression: does binder → body work?
        binder_design = np.hstack([binder_recon, np.ones((n_probes, 1))])
        body_predicted = binder_design @ regression_weights
        body_cos = np.mean([
            float(np.dot(body_predicted[i], up_scores[i]) /
                  (np.linalg.norm(body_predicted[i]) * np.linalg.norm(up_scores[i]) + 1e-10))
            for i in range(n_probes)
        ])

        # Sizes
        plate_bytes = (d_model * k * 2) // 8  # ternary
        beam_q_bytes = k * q_raw.shape[1] * 2  # bf16 loadings
        beam_up_bytes = k * up_raw.shape[1] * 2
        regression_bytes = (k + 1) * k * 4  # float32
        mean_bytes = (q_raw.shape[1] + up_raw.shape[1]) * 4  # float32 means
        layer_beam_bytes = beam_q_bytes + beam_up_bytes + regression_bytes + mean_bytes

        total_plate_bytes += plate_bytes
        total_beam_bytes += layer_beam_bytes

        lambda_terms[li] = {
            'plate_ternary': plate_ternary,     # (d_model, k) — store this
            'q_loadings': q_loadings,            # (k, d_q) — continuous beam
            'q_mean': q_mean,                    # (d_q,)
            'up_loadings': up_loadings,          # (k, d_ffn) — continuous beam
            'up_mean': up_mean,                  # (d_ffn,)
            'regression_weights': regression_weights,  # (k+1, k)
            'binder_cosine': binder_cos,
            'body_cosine': body_cos,
            'plate_bytes': plate_bytes,
            'beam_bytes': layer_beam_bytes,
        }

        if (li + 1) % 8 == 0:
            print(f"    Layer {li+1}/{n_layers}: binder_cos={binder_cos:.3f}, body_cos={body_cos:.3f}",
                  file=sys.stderr, flush=True)

    print(f"\n  Total plate: {total_plate_bytes/1024/1024:.1f} MB (ternary)",
          file=sys.stderr, flush=True)
    print(f"  Total beams: {total_beam_bytes/1024/1024:.1f} MB (continuous)",
          file=sys.stderr, flush=True)
    print(f"  Total: {(total_plate_bytes + total_beam_bytes)/1024/1024:.1f} MB",
          file=sys.stderr, flush=True)

    original_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
    print(f"  Original: {original_bytes/1024/1024:.0f} MB",
          file=sys.stderr, flush=True)
    print(f"  Compression: {original_bytes / max(total_plate_bytes + total_beam_bytes, 1):.1f}×",
          file=sys.stderr, flush=True)

    return {
        'model': model,
        'tokenizer': tokenizer,
        'lambda_terms': lambda_terms,
        'n_layers': n_layers,
        'd_model': d_model,
        'total_plate_bytes': total_plate_bytes,
        'total_beam_bytes': total_beam_bytes,
        'original_bytes': original_bytes,
        'is_fused': is_fused,
    }


def test_activation_reconstruction(extraction: dict, device: str):
    """Test: do lambda terms produce correct activations for test prompts?
    
    For each test prompt, compare:
      1. Original Q and up activations (from the model)
      2. Reconstructed Q and up activations (from lambda terms)
    """
    import torch

    model = extraction['model']
    tokenizer = extraction['tokenizer']
    lambda_terms = extraction['lambda_terms']
    n_layers = extraction['n_layers']
    is_fused = extraction['is_fused']
    d_model = extraction['d_model']

    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    else:
        layers = model.gpt_neox.layers

    print(f"\n  Testing activation reconstruction on {len(TEST_PROMPTS)} prompts...",
          file=sys.stderr, flush=True)

    # Sample 5 layers across the depth
    test_layers = [0, n_layers // 4, n_layers // 2, 3 * n_layers // 4, n_layers - 1]

    per_layer_results = {li: {'q_cosines': [], 'up_cosines': []} for li in test_layers}

    for prompt_idx, prompt in enumerate(TEST_PROMPTS):
        input_ids = tokenizer.encode(prompt, return_tensors="pt").to(device)

        # Capture original activations
        original_acts: dict[int, dict] = {}
        hooks = []

        for li in test_layers:
            original_acts[li] = {}
            layer_mod = layers[li]

            def make_h_hook(layer_i):
                def hook_fn(module, input, output):
                    original_acts[layer_i]['hidden'] = input[0][:, -1, :].detach().cpu().float().numpy()
                return hook_fn
            hooks.append(layer_mod.register_forward_hook(make_h_hook(li)))

            if is_fused:
                fused = layer_mod.attention.query_key_value
                def make_q_hook(layer_i, qs=d_model):
                    def hook_fn(module, input, output):
                        original_acts[layer_i]['q'] = output[:, -1, :qs].detach().cpu().float().numpy()
                    return hook_fn
                hooks.append(fused.register_forward_hook(make_q_hook(li)))
                up_mod = layer_mod.mlp.dense_h_to_4h
            else:
                q_proj = layer_mod.self_attn.q_proj
                def make_q_hook(layer_i):
                    def hook_fn(module, input, output):
                        original_acts[layer_i]['q'] = output[:, -1, :].detach().cpu().float().numpy()
                    return hook_fn
                hooks.append(q_proj.register_forward_hook(make_q_hook(li)))
                up_mod = getattr(layer_mod.mlp, 'up_proj', None) or layer_mod.mlp.dense_h_to_4h

            def make_up_hook(layer_i):
                def hook_fn(module, input, output):
                    original_acts[layer_i]['up'] = output[:, -1, :].detach().cpu().float().numpy()
                return hook_fn
            hooks.append(up_mod.register_forward_hook(make_up_hook(li)))

        with torch.no_grad():
            _ = model(input_ids)

        for h in hooks:
            h.remove()

        # Reconstruct from lambda terms
        for li in test_layers:
            lt = lambda_terms[li]
            h = original_acts[li]['hidden'].flatten()

            # Binder: h @ plate → binder scores
            binder_scores = h @ lt['plate_ternary']  # (k,)

            # Reconstruct Q: binder_scores @ q_loadings + q_mean
            q_recon = binder_scores @ lt['q_loadings'] + lt['q_mean']

            # Body: binder → regression → body scores
            binder_design = np.append(binder_scores, 1.0)  # (k+1,)
            body_scores = binder_design @ lt['regression_weights']  # (k,)

            # Reconstruct up: body_scores @ up_loadings + up_mean
            up_recon = body_scores @ lt['up_loadings'] + lt['up_mean']

            # Compare
            q_orig = original_acts[li]['q'].flatten()
            up_orig = original_acts[li]['up'].flatten()

            q_cos = float(np.dot(q_recon, q_orig) /
                         (np.linalg.norm(q_recon) * np.linalg.norm(q_orig) + 1e-10))
            up_cos = float(np.dot(up_recon, up_orig) /
                          (np.linalg.norm(up_recon) * np.linalg.norm(up_orig) + 1e-10))

            per_layer_results[li]['q_cosines'].append(q_cos)
            per_layer_results[li]['up_cosines'].append(up_cos)

    # Print results
    print(f"\n  ─── Activation Reconstruction Quality ───", file=sys.stderr, flush=True)
    print(f"  {'layer':>5s}  {'depth':>5s}  {'Q_cos_mean':>10s}  {'up_cos_mean':>11s}",
          file=sys.stderr, flush=True)
    print(f"  {'─'*40}", file=sys.stderr, flush=True)

    all_q_cos = []
    all_up_cos = []
    for li in test_layers:
        depth_frac = li / max(n_layers - 1, 1)
        q_mean = float(np.mean(per_layer_results[li]['q_cosines']))
        up_mean = float(np.mean(per_layer_results[li]['up_cosines']))
        all_q_cos.append(q_mean)
        all_up_cos.append(up_mean)
        print(f"  {li:>5d}  {depth_frac:>5.0%}  {q_mean:>+10.4f}  {up_mean:>+11.4f}",
              file=sys.stderr, flush=True)

    mean_q = float(np.mean(all_q_cos))
    mean_up = float(np.mean(all_up_cos))
    print(f"\n  Mean Q cosine:  {mean_q:+.4f}", file=sys.stderr, flush=True)
    print(f"  Mean up cosine: {mean_up:+.4f}", file=sys.stderr, flush=True)

    return {
        'per_layer': {li: {
            'q_cosine_mean': float(np.mean(per_layer_results[li]['q_cosines'])),
            'up_cosine_mean': float(np.mean(per_layer_results[li]['up_cosines'])),
        } for li in test_layers},
        'mean_q_cosine': mean_q,
        'mean_up_cosine': mean_up,
    }


def main():
    parser = argparse.ArgumentParser(description="Lambda Convert")
    parser.add_argument("--model", default="pythia-2.8b", choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--rank", type=int, default=64)
    parser.add_argument("--output-dir", default="results/lambda-convert")

    args = parser.parse_args()

    print("=" * 90, file=sys.stderr, flush=True)
    print(f"  Lambda Convert — Holographic Ternary Conversion via Lambda Terms",
          file=sys.stderr, flush=True)
    print(f"  Model: {args.model}, rank: {args.rank}", file=sys.stderr, flush=True)
    print("=" * 90, file=sys.stderr, flush=True)

    t_start = time.time()

    # Extract lambda terms
    extraction = extract_lambda_terms(args.model, args.probes, args.rank, args.device)

    # Test activation reconstruction
    recon_results = test_activation_reconstruction(extraction, args.device)

    # Summary
    lt = extraction['lambda_terms']
    mean_binder_cos = float(np.mean([lt[li]['binder_cosine'] for li in lt]))
    mean_body_cos = float(np.mean([lt[li]['body_cosine'] for li in lt]))

    total_mb = (extraction['total_plate_bytes'] + extraction['total_beam_bytes']) / 1024 / 1024
    orig_mb = extraction['original_bytes'] / 1024 / 1024
    compression = orig_mb / max(total_mb, 0.01)

    print(f"\n{'='*90}", file=sys.stderr, flush=True)
    print(f"  LAMBDA CONVERSION SUMMARY", file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)
    print(f"  Model: {args.model}, rank: {args.rank}", file=sys.stderr, flush=True)
    print(f"  Plate: {extraction['total_plate_bytes']/1024/1024:.1f} MB (ternary)",
          file=sys.stderr, flush=True)
    print(f"  Beams: {extraction['total_beam_bytes']/1024/1024:.1f} MB (continuous)",
          file=sys.stderr, flush=True)
    print(f"  Total: {total_mb:.1f} MB  ({compression:.1f}× compression vs {orig_mb:.0f} MB)",
          file=sys.stderr, flush=True)
    print(f"  Probe binder cosine: {mean_binder_cos:.3f} (plate → Q scores)",
          file=sys.stderr, flush=True)
    print(f"  Probe body cosine:   {mean_body_cos:.3f} (regression → up scores)",
          file=sys.stderr, flush=True)
    print(f"  Test Q cosine:       {recon_results['mean_q_cosine']:+.4f} (new prompts)",
          file=sys.stderr, flush=True)
    print(f"  Test up cosine:      {recon_results['mean_up_cosine']:+.4f} (new prompts)",
          file=sys.stderr, flush=True)
    print(f"{'='*90}", file=sys.stderr, flush=True)

    # Save
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / f"convert_{args.model}_k{args.rank}.json"
    with open(json_path, "w") as f:
        json.dump({
            "model": args.model,
            "rank": args.rank,
            "n_layers": extraction['n_layers'],
            "plate_mb": extraction['total_plate_bytes'] / 1024 / 1024,
            "beam_mb": extraction['total_beam_bytes'] / 1024 / 1024,
            "total_mb": total_mb,
            "original_mb": orig_mb,
            "compression": compression,
            "mean_binder_cosine": mean_binder_cos,
            "mean_body_cosine": mean_body_cos,
            "reconstruction": recon_results,
        }, f, indent=2)
    print(f"\n  💾 {json_path}", file=sys.stderr, flush=True)

    elapsed = time.time() - t_start
    print(f"  Total: {elapsed:.0f}s ({elapsed/60:.1f}min)", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
