"""Ternary Masked FFN Test — does combinator masking improve ternary FFN lookup?

The full pipeline: crystal → dispatch → combinator mask → ternary FFN.
Test whether using the combinator profile to MASK the ternary key plates
improves the lookup fidelity vs unmasked.

This simulates what V13 would do: use the lambda compiler's dispatch
to select which "view" of the ternary FFN to use.

Tests:
  1. Unmasked ternary FFN (baseline, already measured at 82-97%)
  2. Combinator-masked ternary FFN (does masking help?)
  3. Per-domain: does the right combinator mask improve domain-specific lookup?
  4. WHNF-masked specifically (the retrieval path)

Usage:
    uv run python scripts/v12/ternary_masked_ffn_test.py

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

DEFAULT_MODELS = ["mistral-7b", "pythia-2.8b"]
DEPTH_FRACTIONS = [0.3, 0.5, 0.7]
COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
D_TARGET = 512

SKILL_DOMAINS = [
    "lambda", "arithmetic", "coding", "tool", "retrieval",
    "analogy", "reasoning", "narrative", "instruction",
]


def load_probes(probe_path=None):
    if probe_path is None:
        probe_path = str(Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json")
    with open(probe_path) as f:
        return json.load(f)


def get_pure_indices(probes):
    idx = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            idx[p["axis"].split("/")[1]] = i
    return idx


def get_domain_indices(probes):
    idx = {}
    for i, p in enumerate(probes):
        d = p["axis"].split("/")[0]
        idx.setdefault(d, []).append(i)
    return idx


def pca_project(X, k=64):
    X_c = X - X.mean(axis=0, keepdims=True)
    U, S, Vt = np.linalg.svd(X_c, full_matrices=False)
    k = min(k, U.shape[1])
    return U[:, :k] * S[:k]


def run_test(model_key, probes, depth_fractions, device="mps"):
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    model_name, n_layers, d_model = MODELS[model_key]
    target_layers = []
    for frac in depth_fractions:
        layer = min(int(round(frac * (n_layers - 1))), n_layers - 1)
        if layer not in [l for l, _ in target_layers]:
            target_layers.append((layer, frac))

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
        get_attn = lambda l: l.self_attn
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
        get_attn = lambda l: l.attention
    else:
        raise ValueError("Unknown arch")

    is_fused = hasattr(get_attn(layers[0]), 'query_key_value')
    pure_idx = get_pure_indices(probes)
    domain_indices = get_domain_indices(probes)
    comb_indices = [pure_idx[c] for c in COMBINATOR_ORDER if c in pure_idx]

    results = {}

    for li, frac in target_layers:
        print(f"\n  Layer {li} (depth {frac:.0%}):", file=sys.stderr, flush=True)

        # Extract W_up weights
        mlp = layers[li].mlp if hasattr(layers[li], 'mlp') else layers[li].feed_forward
        if hasattr(mlp, 'up_proj'):
            w_up = mlp.up_proj.weight.detach().cpu().float().numpy()
        elif hasattr(mlp, 'dense_h_to_4h'):
            w_up = mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()
        else:
            continue

        d_ffn, d_orig = w_up.shape

        # Hook Q and FFN activations + hidden states
        captures = {"Q": [], "FFN": [], "hidden": []}
        hooks = []

        attn = get_attn(layers[li])
        if is_fused:
            def make_q(qs=d_model):
                def hook(m, inp, out):
                    captures["Q"].append(out[:, -1, :qs].detach().cpu().float())
                return hook
            hooks.append(attn.query_key_value.register_forward_hook(make_q()))
        else:
            def make_q():
                def hook(m, inp, out):
                    captures["Q"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(attn.q_proj.register_forward_hook(make_q()))

        up_mod = getattr(mlp, 'up_proj', None) or getattr(mlp, 'dense_h_to_4h', None)
        if up_mod:
            def make_ffn():
                def hook(m, inp, out):
                    captures["FFN"].append(out[:, -1, :].detach().cpu().float())
                return hook
            hooks.append(up_mod.register_forward_hook(make_ffn()))

        def make_hidden():
            def hook(m, inp, out):
                h_in = inp[0] if isinstance(inp, tuple) else inp
                captures["hidden"].append(h_in[:, -1, :].detach().cpu().float())
            return hook
        hooks.append(layers[li].register_forward_hook(make_hidden()))

        for probe in probes:
            ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(device)
            with torch.no_grad():
                _ = model(ids)

        for h in hooks:
            h.remove()

        q_vecs = torch.cat(captures["Q"], dim=0).numpy()
        teacher_ffn = torch.cat(captures["FFN"], dim=0).numpy()
        teacher_hidden = torch.cat(captures["hidden"], dim=0).numpy()
        n_probes = q_vecs.shape[0]

        # SVD project W_up
        U, S, Vt = np.linalg.svd(w_up, full_matrices=False)
        k = min(D_TARGET, d_orig)
        V_proj = Vt[:k, :].T
        w_up_proj = U[:, :k] * S[:k]
        ternary_w = np.sign(w_up_proj)

        # Project hidden states
        hidden_proj = teacher_hidden @ V_proj

        # PCA-Q combinator profiles
        q_pca = pca_project(q_vecs, 64)
        q_norms = np.maximum(np.linalg.norm(q_pca, axis=1, keepdims=True), 1e-8)
        q_norm = q_pca / q_norms
        anchor_vecs = q_norm[comb_indices]
        comb_profiles = q_norm @ anchor_vecs.T  # (n_probes, 8)

        # Teacher FFN for comparison
        t_norms = np.maximum(np.linalg.norm(teacher_ffn, axis=1, keepdims=True), 1e-8)

        # ── Test 1: Unmasked ternary (baseline) ──────────────
        ternary_ffn = hidden_proj @ ternary_w.T
        r_norms = np.maximum(np.linalg.norm(ternary_ffn, axis=1, keepdims=True), 1e-8)
        baseline_rdm_t = (teacher_ffn / t_norms) @ (teacher_ffn / t_norms).T
        baseline_rdm_r = (ternary_ffn / r_norms) @ (ternary_ffn / r_norms).T
        triu = np.triu_indices(n_probes, k=1)
        baseline_corr = float(np.corrcoef(baseline_rdm_t[triu], baseline_rdm_r[triu])[0, 1])

        print(f"    Unmasked ternary RDM corr: {baseline_corr:+.4f}",
              file=sys.stderr, flush=True)

        # ── Test 2: Per-combinator masking ────────────────────
        # For each probe, weight the ternary W_up by its combinator profile
        # This simulates: dispatch selects combinator → mask selects view
        print(f"\n    Combinator-masked ternary FFN:", file=sys.stderr, flush=True)

        # Build per-combinator neuron affinity (from previous experiments)
        # For each neuron, correlate its activation with each combinator
        ffn_binary = (teacher_ffn > 0).astype(float)
        neuron_comb_corr = np.zeros((len(COMBINATOR_ORDER), d_ffn))
        for ci in range(len(COMBINATOR_ORDER)):
            for ni in range(d_ffn):
                if ffn_binary[:, ni].std() < 1e-8:
                    continue
                neuron_comb_corr[ci, ni] = np.corrcoef(
                    comb_profiles[:, ci], ffn_binary[:, ni]
                )[0, 1]

        # Dominant combinator per neuron
        dominant = np.argmax(np.abs(neuron_comb_corr), axis=0)

        # For each combinator, create a mask: neurons that belong to this dept
        dept_masks = {}
        for ci, comb in enumerate(COMBINATOR_ORDER):
            mask = (dominant == ci).astype(float)
            dept_masks[comb] = mask
            n_in = int(mask.sum())

        # Test: per-probe, use the probe's dominant combinator to mask
        # Simulates: dispatch → correct department → masked lookup
        masked_ffn = np.zeros_like(ternary_ffn)
        for pi in range(n_probes):
            # Which combinator does this probe route through?
            probe_dom = COMBINATOR_ORDER[np.argmax(comb_profiles[pi])]
            mask = dept_masks[probe_dom]
            # Apply mask to ternary weights before matmul
            masked_w = ternary_w * mask[:, np.newaxis]  # zero out non-dept neurons
            masked_ffn[pi] = hidden_proj[pi] @ masked_w.T

        m_norms = np.maximum(np.linalg.norm(masked_ffn, axis=1, keepdims=True), 1e-8)
        masked_rdm = (masked_ffn / m_norms) @ (masked_ffn / m_norms).T
        masked_corr = float(np.corrcoef(baseline_rdm_t[triu], masked_rdm[triu])[0, 1])

        print(f"    Dispatch-masked ternary RDM corr: {masked_corr:+.4f} "
              f"(baseline: {baseline_corr:+.4f}, delta: {masked_corr - baseline_corr:+.4f})",
              file=sys.stderr, flush=True)

        # ── Test 3: WHNF mask only (retrieval path) ──────────
        whnf_mask = dept_masks.get("WHNF", np.ones(d_ffn))
        whnf_w = ternary_w * whnf_mask[:, np.newaxis]
        whnf_ffn = hidden_proj @ whnf_w.T
        w_norms = np.maximum(np.linalg.norm(whnf_ffn, axis=1, keepdims=True), 1e-8)
        whnf_rdm = (whnf_ffn / w_norms) @ (whnf_ffn / w_norms).T
        whnf_corr = float(np.corrcoef(baseline_rdm_t[triu], whnf_rdm[triu])[0, 1])

        print(f"    WHNF-only ternary RDM corr: {whnf_corr:+.4f}",
              file=sys.stderr, flush=True)

        # ── Test 4: Per-domain analysis ───────────────────────
        print(f"\n    Per-domain: unmasked vs dispatch-masked vs WHNF-only:",
              file=sys.stderr, flush=True)
        print(f"    {'domain':>12s}  {'unmasked':>8s}  {'masked':>8s}  {'whnf':>8s}  {'best':>6s}",
              file=sys.stderr, flush=True)
        print(f"    {'-'*46}", file=sys.stderr, flush=True)

        for d in SKILL_DOMAINS:
            if d not in domain_indices:
                continue
            idx = domain_indices[d]

            # Per-domain cosine between teacher and each variant
            def domain_cos(recon, teacher, indices):
                cos_vals = []
                for i in indices:
                    tn = np.linalg.norm(teacher[i])
                    rn = np.linalg.norm(recon[i])
                    if tn > 1e-8 and rn > 1e-8:
                        cos_vals.append(float(np.dot(teacher[i], recon[i]) / (tn * rn)))
                return float(np.mean(cos_vals)) if cos_vals else 0

            cos_base = domain_cos(ternary_ffn, teacher_ffn, idx)
            cos_mask = domain_cos(masked_ffn, teacher_ffn, idx)
            cos_whnf = domain_cos(whnf_ffn, teacher_ffn, idx)

            best = "unmask" if cos_base >= max(cos_mask, cos_whnf) else \
                   "masked" if cos_mask >= cos_whnf else "whnf"

            print(f"    {d:>12s}  {cos_base:>+7.4f}  {cos_mask:>+7.4f}  "
                  f"{cos_whnf:>+7.4f}  {best:>6s}",
                  file=sys.stderr, flush=True)

        # ── Test 5: Does the combinator profile align the input? ──
        # Check: does weighting the hidden_proj by combinator profile
        # improve the key matching?
        print(f"\n    Combinator-weighted input test:", file=sys.stderr, flush=True)

        # For each probe, weight the input vector by its combinator profile
        # This simulates: the crystal shapes the residual stream
        # before it enters the FFN
        for ci, comb in enumerate(COMBINATOR_ORDER):
            # Select probes that route through this combinator
            comb_probes = [pi for pi in range(n_probes)
                          if np.argmax(comb_profiles[pi]) == ci]
            if len(comb_probes) < 3:
                continue

            # Cosine for this combinator's probes
            cos_base_c = np.mean([
                float(np.dot(teacher_ffn[pi], ternary_ffn[pi]) /
                      (np.linalg.norm(teacher_ffn[pi]) * np.linalg.norm(ternary_ffn[pi]) + 1e-8))
                for pi in comb_probes
            ])
            cos_mask_c = np.mean([
                float(np.dot(teacher_ffn[pi], masked_ffn[pi]) /
                      (np.linalg.norm(teacher_ffn[pi]) * np.linalg.norm(masked_ffn[pi]) + 1e-8))
                for pi in comb_probes
            ])

            print(f"      {comb:>6s} ({len(comb_probes):2d} probes): "
                  f"unmasked={cos_base_c:+.4f}  masked={cos_mask_c:+.4f}  "
                  f"delta={cos_mask_c - cos_base_c:+.4f}",
                  file=sys.stderr, flush=True)

        results[f"{frac:.2f}"] = {
            "baseline_rdm": baseline_corr,
            "masked_rdm": masked_corr,
            "whnf_rdm": whnf_corr,
        }

    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available(): _t.mps.empty_cache()
    except: pass

    return results


def main():
    parser = argparse.ArgumentParser(description="Ternary Masked FFN Test")
    parser.add_argument("--models", nargs="+", default=DEFAULT_MODELS,
                        choices=list(MODELS.keys()))
    parser.add_argument("--probes", type=str, default=None)
    parser.add_argument("--device", type=str, default="mps")

    args = parser.parse_args()

    print("=" * 72, file=sys.stderr, flush=True)
    print("  Ternary Masked FFN — Lambda Compiler Keying Test",
          file=sys.stderr, flush=True)
    print(f"  Models: {args.models}", file=sys.stderr, flush=True)
    print("=" * 72, file=sys.stderr, flush=True)

    t0 = time.time()
    probes = load_probes(args.probes)
    print(f"  Loaded {len(probes)} probes", file=sys.stderr, flush=True)

    for mk in args.models:
        run_test(mk, probes, DEPTH_FRACTIONS, args.device)

    print(f"\n  Total: {time.time()-t0:.0f}s", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
