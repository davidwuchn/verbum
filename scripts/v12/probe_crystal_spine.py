"""Find the crystal spine across architectures.

Tests whether all models collapse to a low-rank bottleneck in their
middle layers, and whether the dominant PC is always a single neuron
(the "mode switch" / "crystal spine").

Runs a small diverse probe set through each model, hooks every layer,
finds the variance bottleneck, and reports the dominant dimension.

Usage:
    uv run python scripts/v12/probe_crystal_spine.py
    uv run python scripts/v12/probe_crystal_spine.py --models qwen3-8b mistral-7b
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

# ══════════════════════════════════════════════════════════════════════
# Model registry
# ══════════════════════════════════════════════════════════════════════

MODELS = {
    "qwen3-14b":    ("Qwen/Qwen3-14B",              40, 5120),
    "qwen3-8b":     ("Qwen/Qwen3-8B",               36, 4096),
    "qwen3-4b":     ("Qwen/Qwen3-4B",               36, 2560),
    "qwen3-0.6b":   ("Qwen/Qwen3-0.6B",             28, 1024),
    "mistral-7b":   ("mistralai/Mistral-7B-v0.3",    32, 4096),
    "olmo-2-13b":   ("allenai/OLMo-2-1124-13B",      40, 5120),
    "phi-4-mini":   ("microsoft/Phi-4-mini-instruct", 32, 3072),
    "smollm3-3b":   ("HuggingFaceTB/SmolLM3-3B",     36, 2560),
    "pythia-2.8b":  ("EleutherAI/pythia-2.8b-deduped", 32, 2560),
    "pythia-1.4b":  ("EleutherAI/pythia-1.4b-deduped", 24, 2048),
    "pythia-1b":    ("EleutherAI/pythia-1b-deduped",   16, 2048),
    "pythia-410m":  ("EleutherAI/pythia-410m-deduped",  24, 1024),
    "pythia-160m":  ("EleutherAI/pythia-160m-deduped",  12,  768),
}

DEFAULT_MODELS = ["qwen3-14b", "qwen3-4b", "mistral-7b", "olmo-2-13b", "pythia-2.8b", "smollm3-3b"]


# ══════════════════════════════════════════════════════════════════════
# Minimal diverse probe set — just enough to find the spine
# ══════════════════════════════════════════════════════════════════════

def build_probes() -> list[dict]:
    """Build a small diverse probe set — 50 probes across domains.
    
    We need enough variety to reveal the crystal structure but few
    enough to run fast across many models.
    """
    probes = []
    
    # ── Tool-like (with system prompt tool definitions) ──
    tool_sys = (
        "<|im_start|>system\nYou are a helpful assistant.\n\n# Tools\n\n"
        "You may call one or more functions to assist with the user query.\n\n"
        '<tools>\n{"type": "function", "function": {"name": "get_weather", '
        '"description": "Get weather for a city", "parameters": {"type": "object", '
        '"properties": {"city": {"type": "string"}}, "required": ["city"]}}}\n'
        '{"type": "function", "function": {"name": "search", '
        '"description": "Search the web", "parameters": {"type": "object", '
        '"properties": {"query": {"type": "string"}}, "required": ["query"]}}}\n'
        '{"type": "function", "function": {"name": "run_code", '
        '"description": "Execute Python code", "parameters": {"type": "object", '
        '"properties": {"code": {"type": "string"}}, "required": ["code"]}}}\n'
        "</tools>\n<|im_end|>\n"
    )
    
    tool_queries = [
        ("What's the weather in Tokyo?", "tool/weather"),
        ("Search for recent papers on attention mechanisms.", "tool/search"),
        ("Calculate 15% of 847.", "tool/math"),
        ("Run: print(sorted([3,1,4,1,5,9]))", "tool/code"),
        ("What time is it in London?", "tool/time"),
        ("List files in /home/user/docs", "tool/files"),
        ("Find flights from NYC to Paris", "tool/travel"),
        ("Look up Apple stock price", "tool/finance"),
        ("Send email to team@co.com", "tool/action"),
        ("Query database for active users", "tool/db"),
    ]
    for query, sub in tool_queries:
        probes.append({
            "prompt": f"{tool_sys}<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n",
            "domain": "tool",
            "subdomain": sub,
        })
    
    # ── Tool output (assistant already producing) ──
    output_prefixes = [
        ('<tool_call>\n{"name": "get_weather", "arguments": {"city": "', "output/json"),
        ('<tool_call>\n{"name": "search", "arguments": {"query": "attention', "output/json"),
        ("The weather in Tokyo is currently", "output/prose"),
        ("I'll help you calculate that.\n\n<tool_call>", "output/tool_start"),
        ('{"name": "run_code", "arguments": {"code": "import', "output/raw_json"),
    ]
    for prefix, sub in output_prefixes:
        probes.append({
            "prompt": f"{tool_sys}<|im_start|>user\nWhat's the weather?<|im_end|>\n<|im_start|>assistant\n{prefix}",
            "domain": "output",
            "subdomain": sub,
        })
    
    # ── No-tool control (same format, no tool defs) ──
    notool_sys = "<|im_start|>system\nYou are a helpful assistant.<|im_end|>\n"
    
    notool_queries = [
        ("Describe a rainy day in Tokyo.", "control/prose"),
        ("Explain how percentages work.", "control/explain"),
        ("Write a haiku about mountains.", "control/creative"),
        ("What is the capital of France?", "control/factual"),
        ("Summarize the theory of relativity.", "control/academic"),
        ("Tell me a joke about programming.", "control/humor"),
        ("What are the benefits of exercise?", "control/health"),
        ("Explain the difference between TCP and UDP.", "control/technical"),
        ("Write a Python function for fibonacci.", "control/code"),
        ("What is the derivative of x^3?", "control/math"),
        ("Prove that sqrt(2) is irrational.", "control/proof"),
        ("Express the S combinator in lambda calculus.", "control/lambda"),
        ("What is the Y combinator?", "control/lambda"),
        ("Explain Church encoding of natural numbers.", "control/lambda"),
        ("Write a recursive descent parser in Python.", "control/code"),
    ]
    for query, sub in notool_queries:
        probes.append({
            "prompt": f"{notool_sys}<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n",
            "domain": "control",
            "subdomain": sub,
        })
    
    # ── Schema binding (the lambda part) ──
    schema_queries = [
        ("Weather in São Paulo?", "schema/1arg"),
        ("Show me /etc/hosts.", "schema/path"),
        ("Search for 'transformer architecture' with limit 10", "schema/2arg"),
        ("Create event 'Design Review' Friday 10am", "schema/complex"),
        ("Run SELECT * FROM users WHERE active = true", "schema/sql"),
    ]
    for query, sub in schema_queries:
        probes.append({
            "prompt": f"{tool_sys}<|im_start|>user\n{query}<|im_end|>\n<|im_start|>assistant\n",
            "domain": "schema",
            "subdomain": sub,
        })
    
    # ── Raw text (no chat template at all) ──
    raw_texts = [
        ("The quick brown fox jumps over the lazy dog.", "raw/pangram"),
        ("In 1969, Neil Armstrong became the first person to walk on the Moon.", "raw/history"),
        ("def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)", "raw/code"),
        ("λx.λy.x y (y x)", "raw/lambda"),
        ("SELECT name, age FROM users WHERE age > 30 ORDER BY name;", "raw/sql"),
        ('{"name": "Alice", "age": 30, "city": "Portland"}', "raw/json"),
        ("<html><body><h1>Hello World</h1></body></html>", "raw/html"),
        ("∀x∈ℝ: x² ≥ 0", "raw/math_symbol"),
        ("Once upon a time in a land far away, there lived a", "raw/narrative"),
        ("BREAKING: Scientists discover New species in deep ocean", "raw/news"),
    ]
    for text, sub in raw_texts:
        probes.append({
            "prompt": text,
            "domain": "raw",
            "subdomain": sub,
        })
    
    return probes


# ══════════════════════════════════════════════════════════════════════
# Extraction — per model
# ══════════════════════════════════════════════════════════════════════

def extract_spine(
    model_key: str,
    probes: list[dict],
) -> dict:
    """Extract the crystal spine from one model.
    
    Hooks ALL layers, runs probes, finds the variance bottleneck,
    and identifies the dominant dimension.
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM
    
    model_name, n_layers, d_model = MODELS[model_key]
    
    print(f"\n{'━'*70}", file=sys.stderr, flush=True)
    print(f"  {model_key} — {model_name}", file=sys.stderr, flush=True)
    print(f"  {n_layers} layers, d_model={d_model}", file=sys.stderr, flush=True)
    print(f"{'━'*70}", file=sys.stderr, flush=True)
    
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.bfloat16,
        device_map="mps",
        trust_remote_code=True,
    )
    model.eval()
    
    # Find transformer layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        layers = model.model.layers
    elif hasattr(model, 'transformer') and hasattr(model.transformer, 'h'):
        layers = model.transformer.h
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        layers = model.gpt_neox.layers
    else:
        raise ValueError(f"Cannot find transformer layers for {model_key}")
    
    actual_n_layers = len(layers)
    print(f"  Found {actual_n_layers} layers", file=sys.stderr, flush=True)
    
    # Hook EVERY layer
    hidden_captures = {li: [] for li in range(actual_n_layers)}
    hooks = []
    
    for li in range(actual_n_layers):
        def make_hook(layer_idx):
            def hook_fn(module, input, output):
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                hidden_captures[layer_idx].append(
                    h[:, -1, :].detach().cpu().float()
                )
            return hook_fn
        h = layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)
    
    # Run probes
    print(f"  Running {len(probes)} probes...", file=sys.stderr, flush=True)
    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(
            probe["prompt"], return_tensors="pt"
        ).to("mps")
        with torch.no_grad():
            _ = model(input_ids)
    dt = time.time() - t0
    print(f"  Done in {dt:.1f}s ({dt/len(probes)*1000:.0f}ms/probe)",
          file=sys.stderr, flush=True)
    
    for h in hooks:
        h.remove()
    
    # ── Analyze each layer ──
    results = {
        "model": model_key,
        "model_name": model_name,
        "n_layers": actual_n_layers,
        "d_model": d_model,
        "n_probes": len(probes),
        "layers": {},
    }
    
    bottleneck_layer = -1
    bottleneck_var = 0
    
    for li in range(actual_n_layers):
        hs_tensor = torch.cat(hidden_captures[li], dim=0).numpy()  # (n_probes, d_model)
        
        # Center
        hs_centered = hs_tensor - hs_tensor.mean(axis=0, keepdims=True)
        
        # SVD
        U, S, Vt = np.linalg.svd(hs_centered, full_matrices=False)
        
        total_var = (S**2).sum()
        pc1_var = S[0]**2 / total_var * 100
        top3_var = (S[:3]**2).sum() / total_var * 100
        top5_var = (S[:5]**2).sum() / total_var * 100
        
        # Norm statistics
        norms = np.linalg.norm(hs_tensor, axis=1)
        
        # Dominant dimension of PC1
        pc1_dir = Vt[0]  # (d_model,)
        top_dim = int(np.argmax(np.abs(pc1_dir)))
        top_dim_weight = float(pc1_dir[top_dim])
        top_dim_frac = top_dim_weight**2  # fraction of PC1 energy in this dim
        
        # How many dims for 90% of PC1?
        sorted_abs = np.sort(np.abs(pc1_dir))[::-1]
        cum_energy = np.cumsum(sorted_abs**2)
        n90 = int(np.searchsorted(cum_energy, 0.90) + 1)
        n99 = int(np.searchsorted(cum_energy, 0.99) + 1)
        
        layer_result = {
            "pc1_var_pct": float(pc1_var),
            "top3_var_pct": float(top3_var),
            "top5_var_pct": float(top5_var),
            "norm_mean": float(norms.mean()),
            "norm_std": float(norms.std()),
            "singular_values_top5": [float(x) for x in S[:5]],
            "pc1_dominant_dim": top_dim,
            "pc1_dominant_weight": float(top_dim_weight),
            "pc1_dominant_frac": float(top_dim_frac),
            "pc1_dims_for_90pct": n90,
            "pc1_dims_for_99pct": n99,
        }
        results["layers"][li] = layer_result
        
        if top3_var > bottleneck_var:
            bottleneck_var = top3_var
            bottleneck_layer = li
    
    results["bottleneck_layer"] = bottleneck_layer
    results["bottleneck_depth"] = bottleneck_layer / (actual_n_layers - 1)
    results["bottleneck_top3_var"] = bottleneck_var
    
    # Print summary
    print(f"\n  {'Layer':>5} | {'Depth':>5} | {'PC1%':>6} | {'Top3%':>6} | {'Norm':>8} | {'DomDim':>6} | {'DomWt':>7} | {'Frac':>6} | {'n90':>4} | {'n99':>4}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*85}", file=sys.stderr, flush=True)
    
    for li in range(actual_n_layers):
        r = results["layers"][li]
        depth = li / (actual_n_layers - 1) * 100
        marker = " ◀ BOTTLENECK" if li == bottleneck_layer else ""
        print(
            f"  {li:5d} | {depth:4.0f}% | {r['pc1_var_pct']:5.1f}% | {r['top3_var_pct']:5.1f}% | "
            f"{r['norm_mean']:8.0f} | {r['pc1_dominant_dim']:6d} | {r['pc1_dominant_weight']:7.4f} | "
            f"{r['pc1_dominant_frac']:5.3f} | {r['pc1_dims_for_90pct']:4d} | {r['pc1_dims_for_99pct']:4d}"
            f"{marker}",
            file=sys.stderr, flush=True,
        )
    
    print(f"\n  ★ Bottleneck: layer {bottleneck_layer} ({results['bottleneck_depth']*100:.0f}% depth), "
          f"top-3 PCs = {bottleneck_var:.1f}%",
          file=sys.stderr, flush=True)
    bl = results["layers"][bottleneck_layer]
    print(f"  ★ Crystal spine: dim {bl['pc1_dominant_dim']}, "
          f"weight={bl['pc1_dominant_weight']:.4f}, "
          f"explains {bl['pc1_dominant_frac']*100:.1f}% of PC1",
          file=sys.stderr, flush=True)
    
    # Cleanup
    del model, tokenizer
    gc.collect()
    try:
        import torch as _t
        if _t.backends.mps.is_available():
            _t.mps.empty_cache()
    except Exception:
        pass
    
    return results


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Find the crystal spine across architectures")
    parser.add_argument("--models", nargs="+", default=None,
                        help=f"Models to probe. Available: {', '.join(MODELS.keys())}")
    parser.add_argument("--output", default="lattice/crystal_spine",
                        help="Output directory")
    args = parser.parse_args()
    
    model_keys = args.models or DEFAULT_MODELS
    for k in model_keys:
        if k not in MODELS:
            print(f"ERROR: unknown model '{k}'. Available: {', '.join(MODELS.keys())}",
                  file=sys.stderr)
            sys.exit(1)
    
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    probes = build_probes()
    print(f"\nProbe corpus: {len(probes)} probes", file=sys.stderr, flush=True)
    
    # Save probes
    with open(output_dir / "probes.json", "w") as f:
        json.dump(probes, f, indent=2)
    
    all_results = {}
    for model_key in model_keys:
        result = extract_spine(model_key, probes)
        all_results[model_key] = result
        
        # Save per-model result immediately (in case of crash)
        with open(output_dir / f"{model_key}.json", "w") as f:
            json.dump(result, f, indent=2)
    
    # ── Cross-model comparison ──
    print(f"\n\n{'='*80}", file=sys.stderr, flush=True)
    print(f"  CROSS-MODEL CRYSTAL SPINE COMPARISON", file=sys.stderr, flush=True)
    print(f"{'='*80}", file=sys.stderr, flush=True)
    
    print(f"\n  {'Model':<20s} | {'Layers':>6} | {'d_model':>7} | {'Bottleneck':>10} | {'Depth':>5} | {'Top3%':>6} | {'SpineDim':>8} | {'SpineWt':>8} | {'Frac':>6} | {'n90':>4}",
          file=sys.stderr, flush=True)
    print(f"  {'-'*110}", file=sys.stderr, flush=True)
    
    for model_key in model_keys:
        r = all_results[model_key]
        bl = r["bottleneck_layer"]
        bl_data = r["layers"][str(bl)] if str(bl) in r["layers"] else r["layers"][bl]
        print(
            f"  {model_key:<20s} | {r['n_layers']:6d} | {r['d_model']:7d} | "
            f"L{bl:3d}       | {r['bottleneck_depth']*100:4.0f}% | "
            f"{bl_data['top3_var_pct']:5.1f}% | "
            f"{bl_data['pc1_dominant_dim']:8d} | "
            f"{bl_data['pc1_dominant_weight']:8.4f} | "
            f"{bl_data['pc1_dominant_frac']*100:5.1f}% | "
            f"{bl_data['pc1_dims_for_90pct']:4d}",
            file=sys.stderr, flush=True,
        )
    
    # Save combined results
    with open(output_dir / "all_results.json", "w") as f:
        json.dump(all_results, f, indent=2)
    
    print(f"\n  💾 Results: {output_dir}/", file=sys.stderr, flush=True)


if __name__ == "__main__":
    main()
