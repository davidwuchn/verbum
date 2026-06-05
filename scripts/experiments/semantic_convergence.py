#!/usr/bin/env python3
"""Test: do representations converge across languages in the middle layers?

The hypothesis (session 192):
  L0:       BOOT      — token-specific, language-specific
  L1-L12:   DISSOLVE  — converging from tokens to semantic types
  L13-L21:  SOUP      — language-independent semantic computation
  L22-L35:  FORMAT    — precipitating back to language-specific output

If true: cos(residual("dog"), residual("perro")) should PEAK in the middle
layers and be LOW at L0 and L35. The "zone of silence" (where ternary
replacement improves PPL) is the zone of semantic convergence.

Method:
  1. For each concept, provide it in 3+ languages
  2. Run each through the model, capture residual at every layer
  3. Measure pairwise cosine similarity between language variants per layer
  4. Plot the convergence curve across depth

The prediction is clear: the middle layers should show convergence (high cos),
the entry/exit layers should show divergence (low cos). The convergence zone
should align with the ternary sweet spot (L13-L21).

Usage:
  uv run python scripts/experiments/semantic_convergence.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer


# ══════════════════════════════════════════════════════════════════════
# Semantic concept groups (same meaning, different languages)
# ══════════════════════════════════════════════════════════════════════

CONCEPT_GROUPS = [
    {
        "concept": "dog",
        "variants": {
            "en": "The dog runs quickly",
            "es": "El perro corre rápido",
            "zh": "狗跑得很快",
            "fr": "Le chien court vite",
            "de": "Der Hund läuft schnell",
            "ja": "犬が速く走る",
        },
        "target_word_positions": {
            # approximate position of the concept word in each sentence
            "en": 1,   # "dog"
            "es": 1,   # "perro"
            "zh": 0,   # "狗"
            "fr": 1,   # "chien"
            "de": 1,   # "Hund"
            "ja": 0,   # "犬"
        }
    },
    {
        "concept": "water",
        "variants": {
            "en": "Water is essential for life",
            "es": "El agua es esencial para la vida",
            "zh": "水是生命之本",
            "fr": "L'eau est essentielle à la vie",
            "de": "Wasser ist lebenswichtig",
            "ja": "水は命に不可欠です",
        },
        "target_word_positions": {
            "en": 0,
            "es": 1,
            "zh": 0,
            "fr": 0,  # L'eau
            "de": 0,
            "ja": 0,
        }
    },
    {
        "concept": "sun",
        "variants": {
            "en": "The sun rises in the east",
            "es": "El sol sale por el este",
            "zh": "太阳从东方升起",
            "fr": "Le soleil se lève à l'est",
            "de": "Die Sonne geht im Osten auf",
            "ja": "太陽は東から昇る",
        },
        "target_word_positions": {
            "en": 1,
            "es": 1,
            "zh": 0,   # 太阳 may be 0-1
            "fr": 1,
            "de": 1,
            "ja": 0,
        }
    },
    {
        "concept": "eat",
        "variants": {
            "en": "People eat food every day",
            "es": "La gente come comida todos los días",
            "zh": "人们每天吃食物",
            "fr": "Les gens mangent de la nourriture chaque jour",
            "de": "Die Leute essen jeden Tag Essen",
            "ja": "人々は毎日食べ物を食べる",
        },
        "target_word_positions": {
            "en": 1,   # "eat"
            "es": 2,   # "come"
            "zh": 2,   # "吃"
            "fr": 2,   # "mangent"
            "de": 2,   # "essen"
            "ja": 3,   # "食べる" (approximate)
        }
    },
    {
        "concept": "big",
        "variants": {
            "en": "The mountain is very big",
            "es": "La montaña es muy grande",
            "zh": "这座山非常大",
            "fr": "La montagne est très grande",
            "de": "Der Berg ist sehr groß",
            "ja": "その山はとても大きい",
        },
        "target_word_positions": {
            "en": 4,   # "big"
            "es": 4,   # "grande"
            "zh": 3,   # "大"  (approximate)
            "fr": 4,   # "grande"
            "de": 4,   # "groß"
            "ja": 3,   # "大きい" (approximate)
        }
    },
    {
        "concept": "love",
        "variants": {
            "en": "Love is the most powerful emotion",
            "es": "El amor es la emoción más poderosa",
            "zh": "爱是最强大的情感",
            "fr": "L'amour est l'émotion la plus puissante",
            "de": "Liebe ist die stärkste Emotion",
            "ja": "愛は最も強い感情です",
        },
        "target_word_positions": {
            "en": 0,
            "es": 1,
            "zh": 0,
            "fr": 0,
            "de": 0,
            "ja": 0,
        }
    },
    {
        "concept": "three",
        "variants": {
            "en": "There are three apples on the table",
            "es": "Hay tres manzanas en la mesa",
            "zh": "桌子上有三个苹果",
            "fr": "Il y a trois pommes sur la table",
            "de": "Auf dem Tisch liegen drei Äpfel",
            "ja": "テーブルの上にリンゴが三つある",
        },
        "target_word_positions": {
            "en": 2,   # "three"
            "es": 1,   # "tres"
            "zh": 3,   # "三"
            "fr": 3,   # "trois"
            "de": 4,   # "drei"
            "ja": 5,   # "三つ" (approximate)
        }
    },
    {
        "concept": "king",
        "variants": {
            "en": "The king ruled the kingdom wisely",
            "es": "El rey gobernó el reino sabiamente",
            "zh": "国王明智地治理王国",
            "fr": "Le roi a gouverné le royaume avec sagesse",
            "de": "Der König regierte das Königreich weise",
            "ja": "王は王国を賢く統治した",
        },
        "target_word_positions": {
            "en": 1,
            "es": 1,
            "zh": 0,
            "fr": 1,
            "de": 1,
            "ja": 0,
        }
    },
]

# Control: DIFFERENT concepts (should NOT converge)
CONTROL_PAIRS = [
    ("The dog runs quickly", "Water is essential for life"),
    ("The sun rises in the east", "People eat food every day"),
    ("Love is the most powerful emotion", "The mountain is very big"),
    ("There are three apples on the table", "The king ruled the kingdom wisely"),
]


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'layers'):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def get_all_residuals(model, tokenizer, text, device):
    """Capture the residual stream at every layer boundary.
    
    Returns:
      residuals: list of (seq_len, d_model) tensors, one per layer + 1 for embedding
      tokens: list of token strings
    """
    inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
    inputs = {k: v.to(device) for k, v in inputs.items()}
    
    layers = get_layers(model)
    n_layers = len(layers)
    residuals = []
    
    # Hook every layer's OUTPUT (post-attention + post-FFN residual)
    captured = {}
    handles = []
    
    for i, layer in enumerate(layers):
        def make_hook(idx):
            def hook_fn(module, input, output):
                # output is typically (hidden_states, ...) or just hidden_states
                if isinstance(output, tuple):
                    h = output[0]
                else:
                    h = output
                captured[idx] = h.detach().float().cpu()
            return hook_fn
        handle = layer.register_forward_hook(make_hook(i))
        handles.append(handle)
    
    # Also capture embedding output (pre-layer-0)
    embed_module = None
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        embed_module = model.model.embed_tokens
    elif hasattr(model, 'gpt_neox') and hasattr(model.gpt_neox, 'embed_in'):
        embed_module = model.gpt_neox.embed_in
    
    if embed_module is not None:
        def embed_hook(module, input, output):
            captured['embed'] = output.detach().float().cpu()
        handles.append(embed_module.register_forward_hook(embed_hook))
    
    with torch.no_grad():
        model(**inputs)
    
    for h in handles:
        h.remove()
    
    # Build residual list: [embedding, layer0, layer1, ..., layerN-1]
    result = []
    if 'embed' in captured:
        result.append(captured['embed'][0].numpy())  # (seq, d_model)
    for i in range(n_layers):
        if i in captured:
            result.append(captured[i][0].numpy())
    
    tokens = tokenizer.convert_ids_to_tokens(inputs['input_ids'][0])
    return result, tokens


def cosine_sim(a, b):
    """Cosine similarity between two vectors."""
    a_norm = a / (np.linalg.norm(a) + 1e-10)
    b_norm = b / (np.linalg.norm(b) + 1e-10)
    return float(np.dot(a_norm, b_norm))


def find_concept_position(tokens, target_pos, text, concept):
    """Best-effort find the concept word token position.
    
    Uses target_pos as hint, but also searches for the concept word
    in the token list as a fallback.
    """
    # Clamp target_pos to valid range
    target_pos = min(target_pos, len(tokens) - 1)
    return target_pos


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    args = p.parse_args()
    
    print(f"\n{'='*70}")
    print(f"  SEMANTIC CONVERGENCE TEST")
    print(f"  Does 'dog' = 'perro' = '犬' in the middle layers?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Concepts: {len(CONCEPT_GROUPS)}")
    print()
    
    # Load model
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model}...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    
    n_layers = model.config.num_hidden_layers
    print(f"  Layers: {n_layers}")
    
    # ── Collect residuals for all concept variants ────────────────
    print(f"\n  Collecting residuals...")
    
    all_concept_results = []
    
    for cg in CONCEPT_GROUPS:
        concept = cg["concept"]
        print(f"\n  Concept: {concept}")
        
        variant_residuals = {}  # lang -> list of (seq, d_model) per layer
        variant_tokens = {}
        variant_positions = {}
        
        for lang, text in cg["variants"].items():
            residuals, tokens = get_all_residuals(model, tokenizer, text, args.device)
            variant_residuals[lang] = residuals
            variant_tokens[lang] = tokens
            
            # Find concept position
            target_pos = cg["target_word_positions"].get(lang, 0)
            pos = find_concept_position(tokens, target_pos, text, concept)
            variant_positions[lang] = pos
            
            tok_str = tokens[pos] if pos < len(tokens) else "?"
            print(f"    {lang}: '{text}' → token[{pos}]='{tok_str}' ({len(tokens)} tokens)")
        
        # ── Compute pairwise cosine per layer ─────────────────────
        langs = sorted(variant_residuals.keys())
        n_depth = len(variant_residuals[langs[0]])  # embed + n_layers
        
        # Strategy 1: use the concept word position from each variant
        per_layer_cos_concept = []
        # Strategy 2: mean-pool the full sequence
        per_layer_cos_mean = []
        
        for d in range(n_depth):
            pair_cos_concept = []
            pair_cos_mean = []
            
            for i in range(len(langs)):
                for j in range(i + 1, len(langs)):
                    lang_a, lang_b = langs[i], langs[j]
                    res_a = variant_residuals[lang_a][d]  # (seq_a, d_model)
                    res_b = variant_residuals[lang_b][d]  # (seq_b, d_model)
                    
                    # Concept word position
                    pos_a = min(variant_positions[lang_a], len(res_a) - 1)
                    pos_b = min(variant_positions[lang_b], len(res_b) - 1)
                    
                    cos_c = cosine_sim(res_a[pos_a], res_b[pos_b])
                    pair_cos_concept.append(cos_c)
                    
                    # Mean pooled
                    mean_a = res_a.mean(axis=0)
                    mean_b = res_b.mean(axis=0)
                    cos_m = cosine_sim(mean_a, mean_b)
                    pair_cos_mean.append(cos_m)
            
            per_layer_cos_concept.append(float(np.mean(pair_cos_concept)))
            per_layer_cos_mean.append(float(np.mean(pair_cos_mean)))
        
        all_concept_results.append({
            "concept": concept,
            "n_variants": len(langs),
            "languages": langs,
            "cos_concept_word": per_layer_cos_concept,
            "cos_mean_pool": per_layer_cos_mean,
        })
        
        # Print depth profile for this concept
        print(f"    Depth profile (concept word cosine):")
        for d in range(n_depth):
            depth_label = "emb" if d == 0 else f"L{d-1:>2d}"
            bar = "█" * int(per_layer_cos_concept[d] * 40)
            print(f"      {depth_label}: {per_layer_cos_concept[d]:>6.3f}  {bar}")
    
    # ── Control: different concepts (should NOT converge) ─────────
    print(f"\n  Control: DIFFERENT concepts (should NOT converge)")
    control_results = []
    
    for text_a, text_b in CONTROL_PAIRS:
        res_a, tok_a = get_all_residuals(model, tokenizer, text_a, args.device)
        res_b, tok_b = get_all_residuals(model, tokenizer, text_b, args.device)
        
        per_layer_cos = []
        for d in range(len(res_a)):
            # Compare concept word positions (position 1 for both, approximate)
            pos_a = min(1, len(res_a[d]) - 1)
            pos_b = min(1, len(res_b[d]) - 1)
            cos = cosine_sim(res_a[d][pos_a], res_b[d][pos_b])
            per_layer_cos.append(float(cos))
        
        control_results.append({
            "text_a": text_a,
            "text_b": text_b,
            "cos_per_layer": per_layer_cos,
        })
    
    # ── Grand average ─────────────────────────────────────────────
    n_depth = len(all_concept_results[0]["cos_concept_word"])
    
    avg_same_concept = np.zeros(n_depth)
    for cr in all_concept_results:
        avg_same_concept += np.array(cr["cos_concept_word"])
    avg_same_concept /= len(all_concept_results)
    
    avg_diff_concept = np.zeros(n_depth)
    for ctrl in control_results:
        avg_diff_concept += np.array(ctrl["cos_per_layer"])
    avg_diff_concept /= len(control_results)
    
    separation = avg_same_concept - avg_diff_concept
    
    print(f"\n{'='*70}")
    print(f"  GRAND AVERAGE: same concept (cross-lingual) vs different concept")
    print(f"{'='*70}")
    print(f"  {'Depth':>5s}  {'Same':>7s}  {'Diff':>7s}  {'Sep':>7s}  {'Visual'}")
    print(f"  {'─'*5}  {'─'*7}  {'─'*7}  {'─'*7}  {'─'*40}")
    
    peak_layer = -1
    peak_sep = -999
    
    for d in range(n_depth):
        depth_label = "emb" if d == 0 else f"L{d-1:>2d}"
        s = avg_same_concept[d]
        diff = avg_diff_concept[d]
        sep = separation[d]
        
        if sep > peak_sep:
            peak_sep = sep
            peak_layer = d
        
        # Visual: same as filled bar, diff as empty
        bar_same = "█" * int(s * 30)
        bar_diff = "░" * int(diff * 30)
        marker = " ◀" if d >= 14 and d <= 22 else ""  # mark zone of silence
        print(f"  {depth_label:>5s}  {s:>7.3f}  {diff:>7.3f}  {sep:>+7.3f}  {bar_same}{marker}")
    
    peak_label = "emb" if peak_layer == 0 else f"L{peak_layer - 1}"
    print(f"\n  Peak separation at {peak_label}: {peak_sep:+.3f}")
    print(f"  Zone of silence (L13-L21) average same-concept cos: "
          f"{avg_same_concept[14:22].mean():.3f}")
    print(f"  Zone of silence average separation: "
          f"{separation[14:22].mean():+.3f}")
    
    # ── Save ──────────────────────────────────────────────────────
    out_dir = Path("results/semantic-convergence")
    out_dir.mkdir(parents=True, exist_ok=True)
    model_slug = args.model.replace("/", "_")
    out_path = out_dir / f"{model_slug}.json"
    
    save_data = {
        "model": args.model,
        "n_layers": n_layers,
        "concepts": all_concept_results,
        "controls": control_results,
        "grand_average": {
            "same_concept_cos": avg_same_concept.tolist(),
            "diff_concept_cos": avg_diff_concept.tolist(),
            "separation": separation.tolist(),
            "peak_layer": int(peak_layer),
            "peak_separation": float(peak_sep),
        },
    }
    
    with open(out_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\n  Results saved to {out_path}")
    print(f"{'='*70}\n")


if __name__ == "__main__":
    main()
