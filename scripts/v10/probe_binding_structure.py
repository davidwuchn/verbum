"""
Probe: Does the compressed residual stream encode binding structure?

After the compressor has done its work (L0-28), can we detect WHO
binds to WHOM? If binding information is in the residual stream,
a simple parser can extract tree structure cheaply. If not, we need
a different approach.

Two signals to check:
  1. ATTENTION PATTERNS — do any heads at L25-35 show tree-like
     attention (functors attending to their arguments)?
  2. RESIDUAL SIMILARITY — are composed pairs (functor→argument)
     more similar than non-composed pairs?

Test sentences with known Montague parse trees:
  "Every cat sleeps"
    → (every cat) sleeps
    → bindings: every→cat (det→noun), (every cat)→sleeps (NP→VP)

  "Some dog chases every cat"
    → (some dog) (chases (every cat))
    → bindings: some→dog, every→cat, chases→(every cat), (some dog)→VP

Output: results/binding-structure/

License: MIT
"""

import json
import time
import argparse
import sys
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
OUTPUT_DIR = Path(__file__).parent.parent.parent / "results" / "binding-structure"

# Layers to analyze attention patterns
ATTENTION_LAYERS = list(range(20, 40))  # typing zone neighborhood

# Also grab residual stream at key layers
RESIDUAL_LAYERS = [0, 10, 20, 25, 27, 28, 29, 30, 35, 40, 50, 60, 63]


# ══════════════════════════════════════════════════════════════════
# Probe sentences with known binding structure
# ══════════════════════════════════════════════════════════════════

# Each sentence has:
#   - text: the sentence
#   - words: list of words (will be matched to tokens)
#   - bindings: list of (functor_word, argument_word, relation_type)
#     These are the pairs that SHOULD be bound in a Montague parse
#   - non_bindings: list of (word_a, word_b) pairs that should NOT be bound

BINDING_PROBES = [
    {
        "text": "Every cat sleeps on the mat.",
        "bindings": [
            ("Every", "cat", "det→noun"),
            ("on", "mat", "prep→noun"),
            ("the", "mat", "det→noun"),
        ],
        "non_bindings": [
            ("Every", "sleeps"),
            ("Every", "mat"),
            ("cat", "mat"),
            ("sleeps", "mat"),
        ],
    },
    {
        "text": "Some dog chases every cat.",
        "bindings": [
            ("Some", "dog", "det→noun"),
            ("every", "cat", "det→noun"),
            ("chases", "cat", "verb→obj"),
        ],
        "non_bindings": [
            ("Some", "cat"),
            ("Some", "chases"),
            ("dog", "cat"),
            ("every", "dog"),
        ],
    },
    {
        "text": "The product of three and four is seven.",
        "bindings": [
            ("The", "product", "det→noun"),
            ("of", "three", "prep→noun"),
            ("and", "four", "conj→noun"),
            ("is", "seven", "copula→pred"),
        ],
        "non_bindings": [
            ("The", "seven"),
            ("product", "seven"),
            ("three", "seven"),
            ("of", "is"),
        ],
    },
    {
        "text": "A function maps each input to an output.",
        "bindings": [
            ("A", "function", "det→noun"),
            ("each", "input", "det→noun"),
            ("an", "output", "det→noun"),
            ("maps", "input", "verb→obj"),
            ("to", "output", "prep→noun"),
        ],
        "non_bindings": [
            ("A", "output"),
            ("function", "output"),
            ("each", "output"),
            ("maps", "function"),
        ],
    },
    {
        "text": "Every number that is prime has exactly two factors.",
        "bindings": [
            ("Every", "number", "det→noun"),
            ("that", "number", "rel→antecedent"),
            ("is", "prime", "copula→pred"),
            ("two", "factors", "quant→noun"),
            ("has", "factors", "verb→obj"),
        ],
        "non_bindings": [
            ("Every", "prime"),
            ("Every", "factors"),
            ("number", "factors"),
            ("prime", "factors"),
        ],
    },
    {
        "text": "The sum of five and six equals eleven.",
        "bindings": [
            ("The", "sum", "det→noun"),
            ("of", "five", "prep→noun"),
            ("and", "six", "conj→noun"),
            ("equals", "eleven", "verb→obj"),
        ],
        "non_bindings": [
            ("The", "eleven"),
            ("sum", "eleven"),
            ("five", "eleven"),
            ("of", "equals"),
        ],
    },
    {
        "text": "No student who failed the exam passed the course.",
        "bindings": [
            ("No", "student", "det→noun"),
            ("who", "student", "rel→antecedent"),
            ("failed", "exam", "verb→obj"),
            ("the", "exam", "det→noun"),
            ("passed", "course", "verb→obj"),
        ],
        "non_bindings": [
            ("No", "exam"),
            ("No", "course"),
            ("student", "course"),
            ("failed", "course"),
            ("exam", "course"),
        ],
    },
    {
        "text": "If the number is even then divide it by two.",
        "bindings": [
            ("the", "number", "det→noun"),
            ("is", "even", "copula→pred"),
            ("divide", "it", "verb→obj"),
            ("by", "two", "prep→noun"),
            ("If", "then", "cond→consequent"),
        ],
        "non_bindings": [
            ("If", "two"),
            ("number", "two"),
            ("even", "two"),
            ("is", "divide"),
        ],
    },
]


# ══════════════════════════════════════════════════════════════════
# Model loading
# ══════════════════════════════════════════════════════════════════

def load_model(gguf_path: str, device: str = "mps"):
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name

    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()

    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
    )
    model.eval()

    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


# ══════════════════════════════════════════════════════════════════
# Token-to-word mapping
# ══════════════════════════════════════════════════════════════════

def map_words_to_tokens(tokenizer, input_ids: torch.Tensor) -> list[tuple[str, list[int]]]:
    """Map token positions to words. Returns [(word_text, [token_indices])]."""
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    words = []
    current_indices = []

    for i, tok in enumerate(tokens):
        if tok in tokenizer.all_special_tokens:
            if current_indices:
                text = tokenizer.decode(
                    [input_ids[0, j].item() for j in current_indices],
                    skip_special_tokens=True
                ).strip()
                words.append((text, current_indices))
                current_indices = []
            continue

        if tok.startswith("Ġ") or tok.startswith("▁") or not current_indices:
            if current_indices:
                text = tokenizer.decode(
                    [input_ids[0, j].item() for j in current_indices],
                    skip_special_tokens=True
                ).strip()
                words.append((text, current_indices))
            current_indices = [i]
        else:
            current_indices.append(i)

    if current_indices:
        text = tokenizer.decode(
            [input_ids[0, j].item() for j in current_indices],
            skip_special_tokens=True
        ).strip()
        words.append((text, current_indices))

    return words


def find_word_position(words: list[tuple[str, list[int]]], target: str) -> int | None:
    """Find the first token index of a target word."""
    target_lower = target.lower()
    for word_text, indices in words:
        if word_text.lower() == target_lower:
            return indices[0]  # First token of the word
    return None


# ══════════════════════════════════════════════════════════════════
# Extraction: attention patterns + residual stream
# ══════════════════════════════════════════════════════════════════

def extract_attention_and_residual(
    model, tokenizer, text: str,
    attn_layers: list[int], residual_layers: list[int],
    device: str,
) -> tuple[dict, dict]:
    """Extract attention weights and residual hidden states.

    Returns:
      attention: {layer: (n_heads, seq_len, seq_len)}
      residual: {layer: (seq_len, d_model)}
    """
    inputs = tokenizer(text, return_tensors="pt").to(device)

    attention_storage = {}
    residual_storage = {}

    # Hook for residual stream
    def make_residual_hook(layer_idx):
        def hook_fn(module, input, output):
            hidden = output[0] if isinstance(output, tuple) else output
            residual_storage[layer_idx] = hidden[0].detach().cpu()
        return hook_fn

    # Hook for attention weights — need to hook the attention module
    def make_attn_hook(layer_idx):
        def hook_fn(module, input, output):
            # output is (attn_output, attn_weights) when output_attentions=True
            if isinstance(output, tuple) and len(output) > 1 and output[1] is not None:
                attention_storage[layer_idx] = output[1][0].detach().cpu()
        return hook_fn

    hooks = []

    # Register residual hooks
    for li in residual_layers:
        h = model.model.layers[li].register_forward_hook(make_residual_hook(li))
        hooks.append(h)

    # Register attention hooks on self_attn modules
    for li in attn_layers:
        h = model.model.layers[li].self_attn.register_forward_hook(make_attn_hook(li))
        hooks.append(h)

    # Forward pass with attention output
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)

    # If output_attentions worked, we can also get them from outputs
    if hasattr(outputs, 'attentions') and outputs.attentions is not None:
        for li in attn_layers:
            if li not in attention_storage:
                if li < len(outputs.attentions) and outputs.attentions[li] is not None:
                    attention_storage[li] = outputs.attentions[li][0].detach().cpu()

    for h in hooks:
        h.remove()

    return attention_storage, residual_storage


# ══════════════════════════════════════════════════════════════════
# Analysis: attention binding signal
# ══════════════════════════════════════════════════════════════════

def analyze_attention_binding(
    attention: dict,  # {layer: (n_heads, seq_len, seq_len)}
    word_positions: dict,  # {word: token_position}
    bindings: list[tuple[str, str, str]],
    non_bindings: list[tuple[str, str]],
) -> dict:
    """Check if any attention heads show binding structure.

    For each head at each layer:
      - Compute mean attention from functor→argument for bound pairs
      - Compute mean attention between non-bound pairs
      - The ratio is the binding signal strength
    """
    results = {}

    for layer_idx, attn_weights in sorted(attention.items()):
        n_heads = attn_weights.shape[0]
        seq_len = attn_weights.shape[1]

        head_scores = []

        for head_idx in range(n_heads):
            head_attn = attn_weights[head_idx].numpy()  # (seq_len, seq_len)

            # Attention from functor → argument for bound pairs
            bound_attns = []
            for functor, argument, _ in bindings:
                f_pos = word_positions.get(functor) or word_positions.get(functor.lower())
                a_pos = word_positions.get(argument) or word_positions.get(argument.lower())
                if f_pos is not None and a_pos is not None:
                    # Attention FROM functor TO argument (row=query, col=key)
                    bound_attns.append(head_attn[f_pos, a_pos])
                    # Also check reverse: argument → functor
                    bound_attns.append(head_attn[a_pos, f_pos])

            # Attention between non-bound pairs
            unbound_attns = []
            for word_a, word_b in non_bindings:
                a_pos = word_positions.get(word_a) or word_positions.get(word_a.lower())
                b_pos = word_positions.get(word_b) or word_positions.get(word_b.lower())
                if a_pos is not None and b_pos is not None:
                    unbound_attns.append(head_attn[a_pos, b_pos])
                    unbound_attns.append(head_attn[b_pos, a_pos])

            if bound_attns and unbound_attns:
                mean_bound = float(np.mean(bound_attns))
                mean_unbound = float(np.mean(unbound_attns))
                ratio = mean_bound / max(mean_unbound, 1e-10)

                head_scores.append({
                    "head": head_idx,
                    "mean_bound_attn": mean_bound,
                    "mean_unbound_attn": mean_unbound,
                    "ratio": ratio,
                })

        # Sort by ratio — which heads show strongest binding signal?
        head_scores.sort(key=lambda x: x["ratio"], reverse=True)

        # Summary stats
        ratios = [h["ratio"] for h in head_scores]
        mean_ratio = float(np.mean(ratios)) if ratios else 0
        max_ratio = float(np.max(ratios)) if ratios else 0
        top5_heads = head_scores[:5]

        results[layer_idx] = {
            "mean_ratio": mean_ratio,
            "max_ratio": max_ratio,
            "n_heads": n_heads,
            "top5_heads": top5_heads,
            "all_ratios": ratios,
        }

    return results


def analyze_residual_binding(
    residual: dict,  # {layer: (seq_len, d_model)}
    word_positions: dict,
    bindings: list[tuple[str, str, str]],
    non_bindings: list[tuple[str, str]],
) -> dict:
    """Check if cosine similarity in residual stream predicts binding."""
    results = {}

    for layer_idx, hidden in sorted(residual.items()):
        hidden_np = hidden.numpy()  # (seq_len, d_model)

        # L2 normalize
        norms = np.linalg.norm(hidden_np, axis=1, keepdims=True)
        norms = np.maximum(norms, 1e-8)
        hidden_normed = hidden_np / norms

        # Cosine sim between bound pairs
        bound_sims = []
        for functor, argument, _ in bindings:
            f_pos = word_positions.get(functor) or word_positions.get(functor.lower())
            a_pos = word_positions.get(argument) or word_positions.get(argument.lower())
            if f_pos is not None and a_pos is not None:
                sim = float(np.dot(hidden_normed[f_pos], hidden_normed[a_pos]))
                bound_sims.append(sim)

        # Cosine sim between non-bound pairs
        unbound_sims = []
        for word_a, word_b in non_bindings:
            a_pos = word_positions.get(word_a) or word_positions.get(word_a.lower())
            b_pos = word_positions.get(word_b) or word_positions.get(word_b.lower())
            if a_pos is not None and b_pos is not None:
                sim = float(np.dot(hidden_normed[a_pos], hidden_normed[b_pos]))
                unbound_sims.append(sim)

        mean_bound = float(np.mean(bound_sims)) if bound_sims else 0
        mean_unbound = float(np.mean(unbound_sims)) if unbound_sims else 0
        gap = mean_bound - mean_unbound

        results[layer_idx] = {
            "mean_bound_sim": mean_bound,
            "mean_unbound_sim": mean_unbound,
            "gap": gap,
            "n_bound": len(bound_sims),
            "n_unbound": len(unbound_sims),
            "bound_sims": bound_sims,
            "unbound_sims": unbound_sims,
        }

    return results


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe binding structure in residual stream")
    parser.add_argument("--gguf", default=DEFAULT_GGUF)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(args.gguf, device=args.device)

    all_attn_results = []
    all_resid_results = []
    all_probes = []

    for probe_idx, probe in enumerate(BINDING_PROBES):
        text = probe["text"]
        print(f"\n[{probe_idx+1}/{len(BINDING_PROBES)}] {text}", file=sys.stderr)

        # Tokenize and map words
        inputs = tokenizer(text, return_tensors="pt").to(args.device)
        input_ids = inputs["input_ids"]
        words = map_words_to_tokens(tokenizer, input_ids)

        print(f"  Words: {[(w, idx) for w, idx in words]}", file=sys.stderr)

        # Build word→position map
        word_positions = {}
        for word_text, indices in words:
            # Store first occurrence with original case, and lowercase
            if word_text not in word_positions:
                word_positions[word_text] = indices[0]
            if word_text.lower() not in word_positions:
                word_positions[word_text.lower()] = indices[0]

        # Check all binding targets are found
        missing = []
        for functor, argument, rel in probe["bindings"]:
            f_pos = word_positions.get(functor) or word_positions.get(functor.lower())
            a_pos = word_positions.get(argument) or word_positions.get(argument.lower())
            if f_pos is None:
                missing.append(functor)
            if a_pos is None:
                missing.append(argument)
        if missing:
            print(f"  WARNING: missing words: {missing}", file=sys.stderr)

        # Extract attention patterns and residual stream
        print(f"  Extracting attention (layers {ATTENTION_LAYERS[0]}-{ATTENTION_LAYERS[-1]}) "
              f"and residual ({len(RESIDUAL_LAYERS)} layers)...", file=sys.stderr)

        attention, residual = extract_attention_and_residual(
            model, tokenizer, text,
            ATTENTION_LAYERS, RESIDUAL_LAYERS, args.device,
        )

        print(f"  Got attention for {len(attention)} layers, "
              f"residual for {len(residual)} layers", file=sys.stderr)

        # Analyze attention binding signal
        attn_results = {}
        if attention:
            attn_results = analyze_attention_binding(
                attention, word_positions,
                probe["bindings"], probe["non_bindings"],
            )

        # Analyze residual binding signal
        resid_results = analyze_residual_binding(
            residual, word_positions,
            probe["bindings"], probe["non_bindings"],
        )

        all_attn_results.append(attn_results)
        all_resid_results.append(resid_results)
        all_probes.append(probe)

        # Print per-probe summary
        if attn_results:
            best_layer = max(attn_results.items(), key=lambda x: x[1]["max_ratio"])
            print(f"  Attention: best binding layer=L{best_layer[0]}, "
                  f"max_ratio={best_layer[1]['max_ratio']:.2f}, "
                  f"mean_ratio={best_layer[1]['mean_ratio']:.2f}",
                  file=sys.stderr)

        if resid_results:
            best_gap = max(resid_results.items(), key=lambda x: x[1]["gap"])
            print(f"  Residual: best gap layer=L{best_gap[0]}, "
                  f"gap={best_gap[1]['gap']:.4f} "
                  f"(bound={best_gap[1]['mean_bound_sim']:.4f}, "
                  f"unbound={best_gap[1]['mean_unbound_sim']:.4f})",
                  file=sys.stderr)

    # ══════════════════════════════════════════════════════════════
    # Aggregate analysis
    # ══════════════════════════════════════════════════════════════

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"  AGGREGATE ANALYSIS", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    # ── Attention: binding ratio across layers ──
    if any(all_attn_results):
        print(f"\n  ATTENTION: Mean binding ratio across sentences by layer", file=sys.stderr)
        print(f"  (ratio = mean_attn(bound pairs) / mean_attn(unbound pairs))", file=sys.stderr)
        print(f"  ratio>1 means bound pairs get more attention", file=sys.stderr)
        print(f"  {'Layer':<8} {'MeanRatio':>10} {'MaxRatio':>10} {'BestHead':>10}", file=sys.stderr)
        print(f"  {'-'*8} {'-'*10} {'-'*10} {'-'*10}", file=sys.stderr)

        # Collect all layers that appear
        all_layers = set()
        for ar in all_attn_results:
            all_layers.update(ar.keys())

        for layer in sorted(all_layers):
            mean_ratios = []
            max_ratios = []
            for ar in all_attn_results:
                if layer in ar:
                    mean_ratios.append(ar[layer]["mean_ratio"])
                    max_ratios.append(ar[layer]["max_ratio"])

            if mean_ratios:
                print(f"  L{layer:<6} {np.mean(mean_ratios):>10.2f} "
                      f"{np.mean(max_ratios):>10.2f}",
                      file=sys.stderr)

    # ── Residual: binding gap across layers ──
    print(f"\n  RESIDUAL: Cosine similarity gap (bound - unbound) by layer", file=sys.stderr)
    print(f"  gap>0 means bound pairs are more similar", file=sys.stderr)
    print(f"  {'Layer':<8} {'Gap':>8} {'BoundSim':>10} {'UnboundSim':>12}", file=sys.stderr)
    print(f"  {'-'*8} {'-'*8} {'-'*10} {'-'*12}", file=sys.stderr)

    for layer in sorted(RESIDUAL_LAYERS):
        gaps = []
        bound_sims = []
        unbound_sims = []
        for rr in all_resid_results:
            if layer in rr:
                gaps.append(rr[layer]["gap"])
                bound_sims.append(rr[layer]["mean_bound_sim"])
                unbound_sims.append(rr[layer]["mean_unbound_sim"])

        if gaps:
            print(f"  L{layer:<6} {np.mean(gaps):>+8.4f} "
                  f"{np.mean(bound_sims):>10.4f} "
                  f"{np.mean(unbound_sims):>12.4f}",
                  file=sys.stderr)

    # ── Per-binding-type analysis at L28 ──
    print(f"\n  BINDING TYPE ANALYSIS AT L28:", file=sys.stderr)
    print(f"  {'Type':<20} {'N':>4} {'MeanSim':>8} {'Control':>8} {'Gap':>8}", file=sys.stderr)
    print(f"  {'-'*20} {'-'*4} {'-'*8} {'-'*8} {'-'*8}", file=sys.stderr)

    type_sims = {}
    type_controls = {}
    for probe, rr in zip(all_probes, all_resid_results):
        if 28 not in rr:
            continue
        r28 = rr[28]
        for i, (functor, argument, rel_type) in enumerate(probe["bindings"]):
            if i < len(r28["bound_sims"]):
                if rel_type not in type_sims:
                    type_sims[rel_type] = []
                type_sims[rel_type].append(r28["bound_sims"][i])

        # Aggregate control sims by type
        for usim in r28["unbound_sims"]:
            if "control" not in type_controls:
                type_controls["control"] = []
            type_controls["control"].append(usim)

    control_mean = np.mean(type_controls.get("control", [0]))
    for rel_type, sims in sorted(type_sims.items()):
        print(f"  {rel_type:<20} {len(sims):>4} {np.mean(sims):>8.4f} "
              f"{control_mean:>8.4f} {np.mean(sims)-control_mean:>+8.4f}",
              file=sys.stderr)

    # Save results
    save_data = {
        "probes": [p["text"] for p in all_probes],
        "attention_results": {
            str(k): {
                "mean_ratio": v["mean_ratio"],
                "max_ratio": v["max_ratio"],
            }
            for ar in all_attn_results
            for k, v in ar.items()
        },
        "residual_results": {
            str(layer): {
                "gaps": [rr[layer]["gap"] for rr in all_resid_results if layer in rr],
                "bound_sims": [rr[layer]["mean_bound_sim"] for rr in all_resid_results if layer in rr],
                "unbound_sims": [rr[layer]["mean_unbound_sim"] for rr in all_resid_results if layer in rr],
            }
            for layer in RESIDUAL_LAYERS
        },
        "binding_type_analysis": {
            rel_type: {
                "sims": sims,
                "mean": float(np.mean(sims)),
                "n": len(sims),
            }
            for rel_type, sims in type_sims.items()
        },
        "control_mean_sim": float(control_mean),
    }

    output_path = output_dir / "binding_analysis.json"
    with open(output_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\nResults saved to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
