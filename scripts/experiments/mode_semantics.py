#!/usr/bin/env python3
"""Decode the semantics of the 9 FFN ternary modes.

Session 192 proved:
  - 9 modes per layer, linearly separable (100% classifier accuracy)
  - Modes are layer-specific (cross-layer cos 0.026)
  - PPL IMPROVES when replacing FFN with 9 ternary programs (0.95-1.01×)

This experiment answers: WHAT DO THE 9 MODES COMPUTE?

Method (v2 — gate-pattern clustering):
  The MLP forward is: output = down_proj(SiLU(gate_proj(x)) * up_proj(x))
  The gate pattern SiLU(gate_proj(x)) determines WHICH neurons fire — it's
  the actual "program selector." We cluster on gate patterns, not outputs.

For each target layer, we:
  1. Run diverse text, hook gate_proj to capture gate activation patterns
  2. Cluster gate patterns (not outputs) into 9 modes via K-means
  3. Tag each token with spaCy POS/dep labels
  4. Cross-tabulate: mode × POS, mode × dep role, mode × position
  5. Characterize per-mode: cos(in,out), norm ratio, vocab projection
  6. Identify whether modes are syntactic, semantic, or information-theoretic

Usage:
  uv run python scripts/experiments/mode_semantics.py --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np
import spacy
import torch
from sklearn.cluster import MiniBatchKMeans
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))


# ══════════════════════════════════════════════════════════════════════
# Diverse calibration texts — broad syntactic and domain coverage
# ══════════════════════════════════════════════════════════════════════

TEXTS = [
    # Science
    "The theory of general relativity describes gravity as the curvature of spacetime.",
    "Photosynthesis converts carbon dioxide and water into glucose and oxygen.",
    "DNA carries genetic information in a double helix structure discovered by Watson and Crick.",
    "Quantum mechanics describes the behavior of particles at the atomic and subatomic scale.",
    "The human brain contains approximately 86 billion neurons connected by trillions of synapses.",
    "Black holes form when massive stars collapse under their own gravitational force.",
    "The periodic table organizes elements by atomic number and electron configuration.",
    "Enzymes are biological catalysts that speed up chemical reactions in living organisms.",
    # Narrative
    "She walked through the ancient forest, her footsteps muffled by fallen leaves.",
    "The old man sat quietly by the river, watching the fish jump at dawn.",
    "Three children ran laughing through the sunlit meadow while their dog chased butterflies.",
    "He opened the letter carefully, his hands trembling with anticipation.",
    "The ship sailed slowly into the harbor as the storm clouds gathered on the horizon.",
    "A woman stood at the window, silently watching the rain fall on the empty street.",
    "The detective examined the crime scene, noting every detail with practiced precision.",
    "Birds sang in the treetops as morning light filtered through the canopy above.",
    # Instructional
    "In a large mixing bowl, combine the flour, sugar, and baking powder.",
    "To solve this equation, first isolate the variable on one side.",
    "Install the software by running the setup wizard and following the prompts.",
    "Remove the old filter carefully and replace it with the new one.",
    "The patient should take two tablets every four hours with food.",
    "Preheat the oven to 350 degrees Fahrenheit before placing the dish inside.",
    "Always wash your hands thoroughly before handling raw ingredients.",
    "Connect the cable to the port on the left side of the device.",
    # Formal/political
    "The committee voted unanimously to approve the new environmental regulations.",
    "Democracy originated in ancient Greece, specifically in the city-state of Athens.",
    "The president addressed the nation regarding the economic recovery plan.",
    "International trade agreements require careful negotiation between multiple parties.",
    "The Supreme Court ruled that the legislation was constitutional.",
    "Parliament debated the proposed amendment for six consecutive hours.",
    "The treaty established a framework for peaceful cooperation between nations.",
    "Voters expressed strong opposition to the proposed tax increase.",
    # Technical
    "The function takes two arguments and returns their composition as a new callable.",
    "Machine learning algorithms can be categorized as supervised or unsupervised.",
    "The API endpoint accepts POST requests with JSON payload and returns status codes.",
    "Arrays are contiguous blocks of memory that allow constant-time access by index.",
    "The compiler transforms source code into machine-executable binary through multiple passes.",
    "Hash tables provide average constant-time lookup by mapping keys to bucket indices.",
    "The neural network learns feature representations through gradient descent optimization.",
    "Recursive functions call themselves with progressively smaller subproblems until reaching a base case.",
    # Conversational
    "What time does the store close today?",
    "I think we should probably leave now before it gets too dark outside.",
    "Yes, that makes sense. Let me check the schedule and get back to you.",
    "The weather has been absolutely terrible this week, hasn't it?",
    "Can you believe they actually won the championship after being down three games?",
    "Would you mind passing me the salt, please?",
    "That restaurant on Main Street serves the best pasta I have ever tasted.",
    "How long have you been working at this company?",
    # Complex syntax
    "The book that the professor recommended, which had been out of print for decades, was finally reissued.",
    "Although the experiment failed initially, the researchers persisted and eventually found the solution.",
    "Not only did the company exceed its quarterly targets, but it also expanded into three new markets.",
    "Having carefully considered all the evidence, the jury returned a verdict of not guilty.",
    "The discovery, which some called the most significant breakthrough of the century, changed everything.",
    "Neither the students nor the teachers were satisfied with the proposed curriculum changes.",
    "Whoever finishes the assignment first will receive extra credit from the professor.",
    "The more carefully you analyze the data, the more patterns you will discover.",
    # Lists / enumeration
    "The primary colors are red, blue, and yellow.",
    "Countries in the European Union include France, Germany, Italy, Spain, and Poland.",
    "The Fibonacci sequence begins with 1, 1, 2, 3, 5, 8, 13, 21.",
    "There are four seasons: spring, summer, autumn, and winter.",
    "The planets in order from the Sun are Mercury, Venus, Earth, Mars, Jupiter, Saturn, Uranus, and Neptune.",
    # Math / numbers
    "The population of Tokyo is approximately 14 million people in the city proper.",
    "Pi is approximately equal to 3.14159265 and is an irrational number.",
    "The distance from Earth to the Moon is about 384,400 kilometers.",
    "Einstein's famous equation E equals mc squared relates mass and energy.",
    "The temperature dropped to negative 20 degrees Celsius during the winter storm.",
]


# ══════════════════════════════════════════════════════════════════════
# Target layers — one from each phase
# ══════════════════════════════════════════════════════════════════════

TARGET_LAYERS = [
    3,   # PARSER (EXPAND)
    7,   # ORTHO entry — very low entropy (0.72)
    15,  # OPTIMIZER (ZONE B) — high entropy, all 9 modes active
    20,  # Late ORTHO — entropy drops again
    27,  # REG ALLOC (binding) — where H31 reads subject
    30,  # SCHED (binding) — where H03/H13 read predicate
    35,  # COLLAPSE — highest entropy (2.92)
]


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    elif hasattr(model, "gpt_neox") and hasattr(model.gpt_neox, "layers"):
        return model.gpt_neox.layers
    raise RuntimeError(f"Cannot find layers in {type(model).__name__}")


def align_spacy_to_tokens(text, tokenizer, input_ids, nlp):
    """Align spaCy POS/dep tags to transformer subword tokens.
    
    Strategy: decode each token, track character offset into original text,
    map to the spaCy token covering that character position.
    """
    doc = nlp(text)
    
    # Build character→spacy-token mapping
    char_to_spacy = {}
    for token in doc:
        for i in range(token.idx, token.idx + len(token.text)):
            char_to_spacy[i] = token
    
    result = []
    # Use tokenizer's offset mapping if available
    try:
        encoding = tokenizer(text, return_offsets_mapping=True)
        offsets = encoding.get("offset_mapping", None)
    except Exception:
        offsets = None
    
    if offsets is not None:
        for pos_idx, (tid, offset) in enumerate(zip(input_ids, offsets)):
            tok_text = tokenizer.decode([tid])
            start, end = offset
            
            # Find spaCy token at the midpoint of this token's character span
            mid = (start + end) // 2 if end > start else start
            spacy_tok = char_to_spacy.get(mid) or char_to_spacy.get(start)
            
            # Fallback: scan nearby
            if spacy_tok is None:
                for ci in range(max(0, start - 2), min(len(text), end + 3)):
                    if ci in char_to_spacy:
                        spacy_tok = char_to_spacy[ci]
                        break
            
            result.append({
                "text": tok_text,
                "pos": spacy_tok.pos_ if spacy_tok else "UNK",
                "dep": spacy_tok.dep_ if spacy_tok else "unk",
                "word": spacy_tok.text if spacy_tok else tok_text,
                "position": pos_idx,
                "is_subword": start > 0 and text[start-1:start].isalpha() if start > 0 else False,
            })
    else:
        # Fallback: sequential decode
        for pos_idx, tid in enumerate(input_ids):
            tok_text = tokenizer.decode([tid])
            result.append({
                "text": tok_text,
                "pos": "UNK",
                "dep": "unk",
                "word": tok_text,
                "position": pos_idx,
                "is_subword": False,
            })
    
    return result


def collect_per_layer(model, tokenizer, nlp, layer_idx, device, texts):
    """Collect FFN gate pattern + input/output + token annotations.
    
    Returns:
      gate_patterns: (N, intermediate_size) — SiLU(gate_proj(x))
      inputs: (N, d_model)
      outputs: (N, d_model)
      annotations: list[dict]
    """
    layers = get_layers(model)
    mlp = layers[layer_idx].mlp
    
    captured = {}
    
    def pre_hook(module, inp):
        x = inp[0] if isinstance(inp, tuple) else inp
        captured["input"] = x.detach().float()
    
    def post_hook(module, inp, out):
        captured["output"] = out.detach().float()
    
    # Hook gate_proj to get gate activations
    def gate_hook(module, inp, out):
        # gate_proj output, before SiLU
        captured["gate_raw"] = out.detach().float()
    
    h_pre = mlp.register_forward_pre_hook(pre_hook)
    h_post = mlp.register_forward_hook(post_hook)
    h_gate = mlp.gate_proj.register_forward_hook(gate_hook)
    
    all_gate_patterns = []
    all_inputs = []
    all_outputs = []
    all_annotations = []
    
    for seq_idx, text in enumerate(texts):
        captured.clear()
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=128)
        input_ids = inputs["input_ids"][0].tolist()
        inputs_t = {k: v.to(device) for k, v in inputs.items()}
        
        with torch.no_grad():
            model(**inputs_t)
        
        if "input" not in captured or "gate_raw" not in captured:
            continue
        
        inp = captured["input"][0].cpu().numpy()
        out = captured["output"][0].cpu().numpy()
        
        # Apply SiLU to gate output to get actual gate pattern
        gate_raw = captured["gate_raw"][0]  # (seq, intermediate)
        gate_pattern = (gate_raw * torch.sigmoid(gate_raw)).cpu().numpy()
        
        # Sparsify: what fraction of neurons are active?
        # (useful for understanding mode structure)
        
        # Annotations
        annotations = align_spacy_to_tokens(text, tokenizer, input_ids, nlp)
        seq_len = len(input_ids)
        for i, ann in enumerate(annotations):
            ann["seq_idx"] = seq_idx
            ann["seq_len"] = seq_len
            ann["rel_pos"] = i / max(1, seq_len - 1)
        
        all_gate_patterns.append(gate_pattern)
        all_inputs.append(inp)
        all_outputs.append(out)
        all_annotations.extend(annotations)
    
    h_pre.remove()
    h_post.remove()
    h_gate.remove()
    
    all_gate_patterns = np.concatenate(all_gate_patterns, axis=0)
    all_inputs = np.concatenate(all_inputs, axis=0)
    all_outputs = np.concatenate(all_outputs, axis=0)
    
    return all_gate_patterns, all_inputs, all_outputs, all_annotations


def characterize_modes(gate_patterns, inputs, outputs, labels, annotations,
                       n_modes, model, tokenizer, device, layer_idx):
    """Full semantic characterization of each mode."""
    d_model = inputs.shape[1]
    intermediate = gate_patterns.shape[1]
    
    # ── Mode × POS / dep / position ──────────────────────────────
    pos_dist = defaultdict(lambda: Counter())
    dep_dist = defaultdict(lambda: Counter())
    pos_bucket_dist = defaultdict(lambda: Counter())
    subword_dist = defaultdict(lambda: Counter())
    
    def pos_bucket(rel_pos):
        if rel_pos < 0.1: return "start"
        elif rel_pos < 0.3: return "early"
        elif rel_pos < 0.7: return "mid"
        elif rel_pos < 0.9: return "late"
        else: return "end"
    
    mode_tokens = defaultdict(list)
    mode_words = defaultdict(list)
    
    for i, (label, ann) in enumerate(zip(labels, annotations)):
        mode = int(label)
        pos_dist[mode][ann["pos"]] += 1
        dep_dist[mode][ann["dep"]] += 1
        pos_bucket_dist[mode][pos_bucket(ann["rel_pos"])] += 1
        subword_dist[mode]["subword" if ann.get("is_subword") else "head"] += 1
        mode_tokens[mode].append(ann["text"])
        mode_words[mode].append(ann["word"])
    
    # ── Per-mode transform characterization ──────────────────────
    transform_stats = {}
    for mode in range(n_modes):
        mask = labels == mode
        count = int(mask.sum())
        if count == 0:
            transform_stats[mode] = {"count": 0}
            continue
        
        mode_in = inputs[mask]
        mode_out = outputs[mask]
        mode_gate = gate_patterns[mask]
        
        # Cosine similarity: input → output
        in_norms = np.linalg.norm(mode_in, axis=1, keepdims=True) + 1e-8
        out_norms = np.linalg.norm(mode_out, axis=1, keepdims=True) + 1e-8
        cos_vals = np.sum((mode_in / in_norms) * (mode_out / out_norms), axis=1)
        
        # Norm ratio
        norm_ratios = out_norms.squeeze() / in_norms.squeeze()
        if norm_ratios.ndim == 0:
            norm_ratios = norm_ratios.reshape(1)
        
        # Gate sparsity: fraction of neurons with activation > threshold
        gate_active = (np.abs(mode_gate) > 0.1).mean(axis=1)  # per-token
        
        # Gate consistency: how similar are gate patterns within this mode?
        if count > 1:
            gate_centroid = mode_gate.mean(axis=0)
            gc_norm = np.linalg.norm(gate_centroid) + 1e-8
            gate_norms = np.linalg.norm(mode_gate, axis=1, keepdims=True) + 1e-8
            gate_cos = np.sum((mode_gate / gate_norms) * (gate_centroid / gc_norm), axis=1)
            gate_consistency = float(np.mean(gate_cos))
        else:
            gate_consistency = 1.0
        
        # Output variance
        output_variance = float(np.mean(np.var(mode_out, axis=0)))
        input_variance = float(np.mean(np.var(mode_in, axis=0)))
        
        # Unique words in this mode
        unique_words = sorted(set(mode_words[mode]))[:40]
        
        transform_stats[mode] = {
            "count": count,
            "cos_in_out_mean": float(np.mean(cos_vals)),
            "cos_in_out_std": float(np.std(cos_vals)),
            "norm_ratio_mean": float(np.mean(norm_ratios)),
            "norm_ratio_std": float(np.std(norm_ratios)),
            "gate_sparsity_mean": float(np.mean(gate_active)),
            "gate_sparsity_std": float(np.std(gate_active)),
            "gate_consistency": gate_consistency,
            "output_variance": output_variance,
            "input_variance": input_variance,
            "variance_ratio": float(output_variance / (input_variance + 1e-8)),
            "example_tokens": mode_tokens[mode][:30],
            "unique_words": unique_words,
        }
    
    # ── Vocabulary projection (output centroids → token space) ───
    vocab_projection = {}
    try:
        if hasattr(model, "lm_head"):
            lm_head_weight = model.lm_head.weight.detach().float().cpu()
            
            for mode in range(n_modes):
                mask = labels == mode
                if mask.sum() == 0:
                    vocab_projection[mode] = {"promoted": [], "suppressed": []}
                    continue
                
                centroid = torch.tensor(outputs[mask].mean(axis=0), dtype=torch.float32)
                logits = lm_head_weight @ centroid
                
                top_k = torch.topk(logits, 10)
                promoted = [{"token": tokenizer.decode([idx]).strip(), "score": round(s, 2)}
                           for idx, s in zip(top_k.indices.tolist(), top_k.values.tolist())]
                
                bot_k = torch.topk(logits, 10, largest=False)
                suppressed = [{"token": tokenizer.decode([idx]).strip(), "score": round(s, 2)}
                             for idx, s in zip(bot_k.indices.tolist(), bot_k.values.tolist())]
                
                vocab_projection[mode] = {"promoted": promoted, "suppressed": suppressed}
    except Exception as e:
        print(f"    Warning: vocab projection failed: {e}")
    
    # ── Gate pattern analysis per mode ────────────────────────────
    # Which neurons are consistently active in each mode?
    gate_summary = {}
    for mode in range(n_modes):
        mask = labels == mode
        if mask.sum() == 0:
            continue
        mode_gate = gate_patterns[mask]
        mean_act = mode_gate.mean(axis=0)  # (intermediate,)
        
        # Top 20 most active neurons in this mode
        top_neuron_idx = np.argsort(np.abs(mean_act))[-20:][::-1]
        gate_summary[mode] = {
            "n_active_neurons": int((np.abs(mean_act) > 0.1).sum()),
            "total_neurons": int(intermediate),
            "active_fraction": float((np.abs(mean_act) > 0.1).sum() / intermediate),
            "top_neuron_magnitudes": [float(mean_act[i]) for i in top_neuron_idx[:10]],
            "mean_activation": float(np.mean(np.abs(mean_act))),
        }
    
    # ── Mode centroid similarity matrix ──────────────────────────
    out_centroids = np.zeros((n_modes, d_model))
    gate_centroids = np.zeros((n_modes, intermediate))
    for mode in range(n_modes):
        mask = labels == mode
        if mask.sum() > 0:
            out_centroids[mode] = outputs[mask].mean(axis=0)
            gate_centroids[mode] = gate_patterns[mask].mean(axis=0)
    
    oc_norms = np.linalg.norm(out_centroids, axis=1, keepdims=True) + 1e-8
    out_sim = (out_centroids / oc_norms) @ (out_centroids / oc_norms).T
    
    gc_norms = np.linalg.norm(gate_centroids, axis=1, keepdims=True) + 1e-8
    gate_sim = (gate_centroids / gc_norms) @ (gate_centroids / gc_norms).T
    
    return {
        "pos_distribution": {int(k): dict(v) for k, v in pos_dist.items()},
        "dep_distribution": {int(k): dict(v) for k, v in dep_dist.items()},
        "position_distribution": {int(k): dict(v) for k, v in pos_bucket_dist.items()},
        "subword_distribution": {int(k): dict(v) for k, v in subword_dist.items()},
        "transform_stats": {int(k): v for k, v in transform_stats.items()},
        "vocab_projection": {int(k): v for k, v in vocab_projection.items()},
        "gate_summary": {int(k): v for k, v in gate_summary.items()},
        "output_similarity": out_sim.tolist(),
        "gate_similarity": gate_sim.tolist(),
    }


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--n-modes", type=int, default=9)
    p.add_argument("--layers", type=int, nargs="+", default=None,
                   help="Override target layers")
    args = p.parse_args()
    
    target_layers = args.layers or TARGET_LAYERS
    n_modes = args.n_modes
    
    print(f"\n{'='*70}")
    print(f"  MODE SEMANTICS DECODER (v2 — gate-pattern clustering)")
    print(f"  What do the 9 FFN ternary modes compute?")
    print(f"{'='*70}")
    print(f"  Model: {args.model}")
    print(f"  Device: {args.device}")
    print(f"  Modes: {n_modes}")
    print(f"  Target layers: {target_layers}")
    print(f"  Texts: {len(TEXTS)}")
    print()
    
    # ── Load spaCy ────────────────────────────────────────────────
    print("  Loading spaCy en_core_web_sm...")
    nlp = spacy.load("en_core_web_sm")
    
    # ── Load model ────────────────────────────────────────────────
    dtype = torch.float16 if any(s in args.model for s in ["8B", "14B", "32B"]) else torch.float32
    print(f"  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device)
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    intermediate = model.config.intermediate_size
    print(f"  Layers: {n_layers}, d_model: {d_model}, intermediate: {intermediate}")
    
    target_layers = [l for l in target_layers if l < n_layers]
    
    # ── Run per layer ─────────────────────────────────────────────
    all_results = {
        "model": args.model,
        "n_modes": n_modes,
        "n_texts": len(TEXTS),
        "target_layers": target_layers,
        "d_model": d_model,
        "intermediate_size": intermediate,
        "layers": {},
    }
    
    for layer_idx in target_layers:
        print(f"\n{'─'*70}")
        print(f"  LAYER {layer_idx}")
        print(f"{'─'*70}")
        
        t0 = time.time()
        
        # Collect data
        print(f"    Collecting gate patterns + FFN input/output...")
        gate_patterns, inputs, outputs, annotations = collect_per_layer(
            model, tokenizer, nlp, layer_idx, args.device, TEXTS)
        n_tokens = len(inputs)
        print(f"    Collected {n_tokens} tokens in {time.time()-t0:.1f}s")
        
        # Cluster on GATE PATTERNS (not outputs)
        print(f"    Clustering {n_tokens} gate patterns ({gate_patterns.shape[1]}-dim) into {n_modes} modes...")
        kmeans = MiniBatchKMeans(
            n_clusters=n_modes, random_state=42,
            batch_size=min(256, n_tokens),
            n_init=10)
        labels = kmeans.fit_predict(gate_patterns)
        
        # Mode sizes
        mode_sizes = Counter(labels.tolist())
        print(f"    Mode sizes: {dict(sorted(mode_sizes.items()))}")
        
        # Entropy
        total = sum(mode_sizes.values())
        probs = [mode_sizes.get(i, 0) / total for i in range(n_modes)]
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs)
        print(f"    Mode entropy: {entropy:.2f} bits")
        
        # Characterize
        print(f"    Characterizing mode semantics...")
        layer_result = characterize_modes(
            gate_patterns, inputs, outputs, labels, annotations, n_modes,
            model, tokenizer, args.device, layer_idx)
        
        layer_result["entropy"] = float(entropy)
        layer_result["mode_sizes"] = {int(k): v for k, v in mode_sizes.items()}
        layer_result["n_tokens"] = n_tokens
        
        # ── Print POS summary ────────────────────────────────────
        all_pos_tags = set()
        for counts in layer_result["pos_distribution"].values():
            all_pos_tags.update(counts.keys())
        all_pos_tags = sorted(all_pos_tags)
        
        # Show modes sorted by size, with POS distribution as percentages
        print(f"\n    === MODE × POS TAG (sorted by size) ===")
        sorted_modes = sorted(mode_sizes.items(), key=lambda x: -x[1])
        
        # Find top 8 POS tags by total frequency
        total_pos = Counter()
        for counts in layer_result["pos_distribution"].values():
            total_pos.update(counts)
        top_pos = [p for p, _ in total_pos.most_common(10)]
        
        header = f"    {'Mode':>4} {'N':>5} {'%':>4} | " + " ".join(f"{p:>6}" for p in top_pos[:8])
        print(header)
        print(f"    {'─'*(len(header)+2)}")
        for mode, count in sorted_modes:
            counts = layer_result["pos_distribution"].get(mode, {})
            n = sum(counts.values())
            pct = n / total * 100
            row = f"    {mode:>4} {n:>5} {pct:>3.0f}% | "
            for pos in top_pos[:8]:
                c = counts.get(pos, 0)
                p = c / n * 100 if n > 0 else 0
                row += f"{p:>6.0f}" if p >= 1 else "     ·"
            print(row)
        
        # ── Print DEP summary ────────────────────────────────────
        print(f"\n    === MODE × DEP ROLE (top deps per mode) ===")
        for mode, count in sorted_modes:
            if count < 10:
                continue
            deps = layer_result["dep_distribution"].get(mode, {})
            n = sum(deps.values())
            top3 = sorted(deps.items(), key=lambda x: -x[1])[:4]
            top_str = "  ".join(f"{d}={c/n:.0%}" for d, c in top3)
            print(f"    mode{mode:>2} (n={n:>4}): {top_str}")
        
        # ── Print transform summary ──────────────────────────────
        print(f"\n    === TRANSFORM × GATE CHARACTERISTICS ===")
        print(f"    {'Mode':>4} {'N':>5} | {'cos':>6} {'‖out/in‖':>8} {'gate%':>6} {'g_con':>6} | Top vocab → Suppressed")
        for mode, count in sorted_modes:
            ts = layer_result["transform_stats"].get(mode, {})
            if ts.get("count", 0) == 0:
                continue
            vp = layer_result["vocab_projection"].get(mode, {})
            promoted = vp.get("promoted", [])[:4]
            suppressed = vp.get("suppressed", [])[:3]
            pro_str = ", ".join(w["token"] for w in promoted)
            sup_str = ", ".join(w["token"] for w in suppressed)
            gs = layer_result["gate_summary"].get(mode, {})
            
            print(f"    {mode:>4} {ts['count']:>5} | "
                  f"{ts['cos_in_out_mean']:>6.3f} "
                  f"{ts['norm_ratio_mean']:>8.3f} "
                  f"{ts.get('gate_sparsity_mean', 0):>6.1%} "
                  f"{ts.get('gate_consistency', 0):>6.3f} | "
                  f"{pro_str[:35]:35s} → {sup_str[:25]}")
        
        # ── Print example tokens per mode ─────────────────────────
        print(f"\n    === EXAMPLE TOKENS PER MODE ===")
        for mode, count in sorted_modes:
            ts = layer_result["transform_stats"].get(mode, {})
            tokens = ts.get("example_tokens", [])[:25]
            token_str = " ".join(repr(t) for t in tokens[:15])
            print(f"    mode{mode:>2} (n={count:>4}): {token_str}")
        
        all_results["layers"][str(layer_idx)] = layer_result
        print(f"\n    Layer {layer_idx} done in {time.time()-t0:.1f}s")
    
    # ── Cross-layer summary ───────────────────────────────────────
    print(f"\n{'='*70}")
    print(f"  CROSS-LAYER SUMMARY")
    print(f"{'='*70}")
    
    print(f"\n  Layer-level transform physics:")
    print(f"  {'Layer':>5} {'entropy':>7} {'cos':>7} {'‖ratio‖':>8} {'gate%':>7} | Dominant POS")
    for layer_idx in target_layers:
        lr = all_results["layers"][str(layer_idx)]
        ts = lr["transform_stats"]
        total_n = sum(v["count"] for v in ts.values() if v.get("count", 0) > 0)
        if total_n == 0:
            continue
        
        avg_cos = sum(v["cos_in_out_mean"]*v["count"] for v in ts.values() if v.get("count",0)>0) / total_n
        avg_norm = sum(v["norm_ratio_mean"]*v["count"] for v in ts.values() if v.get("count",0)>0) / total_n
        avg_gate = sum(v.get("gate_sparsity_mean",0)*v["count"] for v in ts.values() if v.get("count",0)>0) / total_n
        
        # Find modes with strongest POS association
        pos_signals = []
        for mode_str, pos_counts in lr["pos_distribution"].items():
            n = sum(pos_counts.values())
            if n < 15:
                continue
            for pos, c in pos_counts.items():
                if pos in ("PUNCT", "SPACE"):
                    continue
                purity = c / n
                if purity > 0.35:
                    pos_signals.append(f"m{mode_str}→{pos}({purity:.0%})")
        
        sig_str = ", ".join(pos_signals[:3]) if pos_signals else "—"
        print(f"  L{layer_idx:>3} {lr['entropy']:>7.2f} {avg_cos:>7.3f} {avg_norm:>8.3f} {avg_gate:>6.1%} | {sig_str}")
    
    # ── Save ──────────────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "mode-semantics"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_file = out_dir / f"{args.model.replace('/', '_')}.json"
    
    with open(out_file, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    
    print(f"\n  Results saved to {out_file}")
    total_tokens = sum(lr["n_tokens"] for lr in all_results["layers"].values())
    print(f"  Total tokens analyzed: {total_tokens}")


if __name__ == "__main__":
    main()
