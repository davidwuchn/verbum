"""
Probe: Does the CompressorLM's output encode binding and typing?

The CompressorLM has self-similar architecture with three scales:
  type_layer  (stride=1,  W=8) — word-level
  parse_layer (stride=8,  W=8) — phrase-level
  apply_layer (stride=64, W=8) — clause-level

These run iteratively (2 passes over shared weights).

We test the same binding pairs from probe_binding_structure.py:
  - Do bound pairs (functor→argument) have higher cosine similarity
    than unbound pairs at each scale?
  - Do context-dependent words get different representations in
    different contexts (typing signal)?

Compare to 32B findings:
  - 32B binding gap peaked at +0.150 at L28
  - 32B context-invariant words had within-sim = 1.000

License: MIT
"""

import sys
import time
import json
from pathlib import Path

import numpy as np
import torch
import torch.nn.functional as F

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))
from verbum.compressor_lm import CompressorLM

OUTPUT_DIR = Path(__file__).parent.parent.parent / "results" / "compressor-binding"


# ══════════════════════════════════════════════════════════════════
# Probe sentences — same binding structure as 32B probe
# Adjusted to shorter sentences since CompressorLM uses GPT-NeoX tokenizer
# ══════════════════════════════════════════════════════════════════

BINDING_PROBES = [
    {
        "text": "Every cat sleeps on the mat",
        "bindings": [
            ("Every", "cat", "det→noun"),
            ("on", "mat", "prep→noun"),
            ("the", "mat", "det→noun"),
        ],
        "non_bindings": [
            ("Every", "sleeps"),
            ("Every", "mat"),
            ("cat", "mat"),
        ],
    },
    {
        "text": "Some dog chases every cat",
        "bindings": [
            ("Some", "dog", "det→noun"),
            ("every", "cat", "det→noun"),
            ("chases", "cat", "verb→obj"),
        ],
        "non_bindings": [
            ("Some", "cat"),
            ("dog", "cat"),
            ("every", "dog"),
        ],
    },
    {
        "text": "The product of three and four is seven",
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
        ],
    },
    {
        "text": "A function maps each input to an output",
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
        ],
    },
    {
        "text": "Every number that is prime has exactly two factors",
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
        ],
    },
    {
        "text": "No student who failed the exam passed the course",
        "bindings": [
            ("No", "student", "det→noun"),
            ("who", "student", "rel→antecedent"),
            ("failed", "exam", "verb→obj"),
            ("passed", "course", "verb→obj"),
        ],
        "non_bindings": [
            ("No", "exam"),
            ("No", "course"),
            ("student", "course"),
        ],
    },
]

# Typing probes: same word in different contexts
TYPING_PROBES = [
    ("is", [
        "The cat is sleeping on the mat",
        "Two plus three is five",
        "The question is whether we should proceed",
        "Every number that is prime has two factors",
    ]),
    ("Every", [
        "Every cat sleeps on the mat",
        "Every number is positive",
        "Every student passed the exam",
        "Every function has a domain",
    ]),
    ("the", [
        "The cat sleeps on the mat",
        "The product of three and four",
        "The student passed the exam",
        "The sum of five and six",
    ]),
    ("of", [
        "The product of three and four",
        "The sum of five and six",
        "Most of the students passed",
        "Each of these numbers is prime",
    ]),
]


# ══════════════════════════════════════════════════════════════════
# Load model
# ══════════════════════════════════════════════════════════════════

def load_compressor_lm(ckpt_path: str):
    """Load CompressorLM from checkpoint."""
    print(f"Loading CompressorLM from {ckpt_path}...", file=sys.stderr)
    ckpt = torch.load(ckpt_path, map_location="cpu", weights_only=False)
    cfg = ckpt["config"]

    model = CompressorLM(
        vocab_size=50277,
        d_model=cfg.get("d_model", 256),
        max_len=cfg.get("seq_len", 4096),
        d_ff=768,
        window=cfg.get("window", 8),
        strides=tuple(cfg.get("strides", [1, 8, 64])),
        mode=cfg.get("mode", "iterative"),
        n_iterations=cfg.get("n_iterations", 2),
    ).eval()
    model.load_state_dict(ckpt["model_state_dict"])
    print(f"Loaded: d={cfg.get('d_model')}, strides={cfg.get('strides')}, "
          f"iterations={cfg.get('n_iterations')}", file=sys.stderr)
    return model


# ══════════════════════════════════════════════════════════════════
# Tokenization (GPT-NeoX for CompressorLM)
# ══════════════════════════════════════════════════════════════════

def get_tokenizer():
    """Get GPT-NeoX tokenizer."""
    from transformers import AutoTokenizer
    return AutoTokenizer.from_pretrained("EleutherAI/gpt-neox-20b")


def find_word_position(tokenizer, input_ids, target_word: str) -> int | None:
    """Find the first token position matching target_word."""
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
    target_lower = target_word.lower()

    for i, tok in enumerate(tokens):
        # GPT-NeoX uses Ġ prefix for word-initial tokens
        clean = tok.replace("Ġ", "").replace("▁", "").strip()
        if clean.lower() == target_lower:
            return i

    # Fallback: decode each token
    for i in range(len(tokens)):
        decoded = tokenizer.decode([input_ids[0, i].item()]).strip()
        if decoded.lower() == target_lower:
            return i

    return None


# ══════════════════════════════════════════════════════════════════
# Extract multi-scale representations
# ══════════════════════════════════════════════════════════════════

def extract_scales(model, input_ids: torch.Tensor) -> dict[str, torch.Tensor]:
    """Extract representations at each scale (type, parse, apply).

    Returns: {scale_name: (1, seq_len, d_model)}
    Each hook fires twice (2 iterations); we keep the second (warm).
    """
    activations = {"type_layer": [], "parse_layer": [], "apply_layer": []}

    hooks = []
    for name in activations:
        layer = getattr(model.block, name)
        hooks.append(layer.register_forward_hook(
            lambda m, inp, out, n=name: activations[n].append(out.detach())
        ))

    with torch.no_grad():
        model(input_ids)

    for h in hooks:
        h.remove()

    # Return last iteration (warm/converged)
    return {
        "type": activations["type_layer"][-1],   # (1, L, d) — word scale
        "parse": activations["parse_layer"][-1],  # (1, L, d) — phrase scale
        "apply": activations["apply_layer"][-1],  # (1, L, d) — clause scale
    }


# ══════════════════════════════════════════════════════════════════
# Binding analysis
# ══════════════════════════════════════════════════════════════════

def analyze_binding_at_scale(
    hidden: torch.Tensor,  # (1, L, d)
    word_positions: dict[str, int],
    bindings: list,
    non_bindings: list,
) -> dict:
    """Measure binding signal at one scale."""
    h = hidden[0]  # (L, d)
    h_norm = F.normalize(h, dim=-1)

    bound_sims = []
    for functor, argument, rel_type in bindings:
        f_pos = word_positions.get(functor) or word_positions.get(functor.lower())
        a_pos = word_positions.get(argument) or word_positions.get(argument.lower())
        if f_pos is not None and a_pos is not None:
            sim = float((h_norm[f_pos] * h_norm[a_pos]).sum())
            bound_sims.append(sim)

    unbound_sims = []
    for word_a, word_b in non_bindings:
        a_pos = word_positions.get(word_a) or word_positions.get(word_a.lower())
        b_pos = word_positions.get(word_b) or word_positions.get(word_b.lower())
        if a_pos is not None and b_pos is not None:
            sim = float((h_norm[a_pos] * h_norm[b_pos]).sum())
            unbound_sims.append(sim)

    mean_bound = float(np.mean(bound_sims)) if bound_sims else 0
    mean_unbound = float(np.mean(unbound_sims)) if unbound_sims else 0

    return {
        "mean_bound": mean_bound,
        "mean_unbound": mean_unbound,
        "gap": mean_bound - mean_unbound,
        "n_bound": len(bound_sims),
        "n_unbound": len(unbound_sims),
    }


# ══════════════════════════════════════════════════════════════════
# Typing analysis
# ══════════════════════════════════════════════════════════════════

def analyze_typing_at_scale(
    model, tokenizer, word: str, sentences: list[str],
    scale_name: str,
) -> dict:
    """Measure within-word similarity across different contexts at one scale."""
    vectors = []

    for sentence in sentences:
        input_ids = tokenizer(sentence, return_tensors="pt")["input_ids"]
        scales = extract_scales(model, input_ids)
        h = scales[scale_name][0]  # (L, d)

        pos = find_word_position(tokenizer, input_ids, word)
        if pos is None:
            continue

        vec = h[pos].numpy()
        vectors.append(vec)

    if len(vectors) < 2:
        return {"within_sim": None, "n_contexts": len(vectors)}

    # L2 normalize
    vecs = np.stack(vectors)
    norms = np.linalg.norm(vecs, axis=1, keepdims=True)
    vecs_norm = vecs / np.maximum(norms, 1e-8)

    # Within-word cosine similarity
    sim_matrix = vecs_norm @ vecs_norm.T
    n = len(vecs_norm)
    mask = np.triu(np.ones((n, n), dtype=bool), k=1)
    within_sim = float(sim_matrix[mask].mean())

    return {
        "within_sim": within_sim,
        "n_contexts": n,
    }


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    output_dir = OUTPUT_DIR
    output_dir.mkdir(parents=True, exist_ok=True)

    ckpt_path = str(Path(__file__).parent.parent.parent /
                    "checkpoints/compressor-lm-iterative/step_010000.pt")

    model = load_compressor_lm(ckpt_path)
    tokenizer = get_tokenizer()

    scale_names = ["type", "parse", "apply"]

    # ── Binding analysis ──
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  BINDING ANALYSIS (CompressorLM)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    all_binding_results = {s: [] for s in scale_names}

    for probe in BINDING_PROBES:
        text = probe["text"]
        input_ids = tokenizer(text, return_tensors="pt")["input_ids"]
        print(f"\n  {text}", file=sys.stderr)

        # Build word→position map
        word_positions = {}
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())
        for i, tok in enumerate(tokens):
            clean = tok.replace("Ġ", "").replace("▁", "").strip()
            if clean and clean not in word_positions:
                word_positions[clean] = i
                word_positions[clean.lower()] = i

        # Check all words found
        all_words = set()
        for f, a, _ in probe["bindings"]:
            all_words.add(f)
            all_words.add(a)
        for a, b in probe["non_bindings"]:
            all_words.add(a)
            all_words.add(b)

        missing = [w for w in all_words
                    if w not in word_positions and w.lower() not in word_positions]
        if missing:
            print(f"    WARNING: missing words: {missing}", file=sys.stderr)

        # Extract all scales
        scales = extract_scales(model, input_ids)

        for scale_name in scale_names:
            result = analyze_binding_at_scale(
                scales[scale_name], word_positions,
                probe["bindings"], probe["non_bindings"],
            )
            all_binding_results[scale_name].append(result)

    # Aggregate binding results
    print(f"\n  BINDING GAP BY SCALE:", file=sys.stderr)
    print(f"  {'Scale':<10} {'BoundSim':>10} {'UnboundSim':>12} {'Gap':>8}",
          file=sys.stderr)
    print(f"  {'-'*10} {'-'*10} {'-'*12} {'-'*8}", file=sys.stderr)

    binding_summary = {}
    for scale_name in scale_names:
        results = all_binding_results[scale_name]
        if not results:
            continue
        gaps = [r["gap"] for r in results]
        bound = [r["mean_bound"] for r in results]
        unbound = [r["mean_unbound"] for r in results]

        mean_gap = float(np.mean(gaps))
        mean_bound = float(np.mean(bound))
        mean_unbound = float(np.mean(unbound))

        print(f"  {scale_name:<10} {mean_bound:>10.4f} {mean_unbound:>12.4f} "
              f"{mean_gap:>+8.4f}", file=sys.stderr)

        binding_summary[scale_name] = {
            "mean_bound": mean_bound,
            "mean_unbound": mean_unbound,
            "gap": mean_gap,
        }

    # ── Typing analysis ──
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  TYPING ANALYSIS (CompressorLM)", file=sys.stderr)
    print(f"  (within-word cosine sim: 1.0=invariant, <1.0=context-dependent)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)

    print(f"  {'Word':<12} {'type':>8} {'parse':>8} {'apply':>8}", file=sys.stderr)
    print(f"  {'-'*12} {'-'*8} {'-'*8} {'-'*8}", file=sys.stderr)

    typing_summary = {}
    for word, sentences in TYPING_PROBES:
        typing_summary[word] = {}
        line = f"  {word:<12}"
        for scale_name in scale_names:
            result = analyze_typing_at_scale(model, tokenizer, word, sentences, scale_name)
            ws = result["within_sim"]
            line += f" {ws:>8.4f}" if ws is not None else f" {'N/A':>8}"
            typing_summary[word][scale_name] = ws
        print(line, file=sys.stderr)

    # ── Comparison to 32B ──
    print(f"\n{'='*70}", file=sys.stderr)
    print(f"  COMPARISON TO 32B (L28)", file=sys.stderr)
    print(f"{'='*70}", file=sys.stderr)
    print(f"  32B binding gap at L28:  +0.150", file=sys.stderr)
    for scale_name, summary in binding_summary.items():
        print(f"  CompressorLM {scale_name:<6} gap: {summary['gap']:>+.4f}", file=sys.stderr)

    print(f"\n  32B 'is' within-sim at L28: 0.241", file=sys.stderr)
    print(f"  32B 'Every' within-sim at L28: 1.000", file=sys.stderr)
    for word in ["is", "Every"]:
        if word in typing_summary:
            for scale_name in scale_names:
                ws = typing_summary[word].get(scale_name)
                if ws is not None:
                    print(f"  CompressorLM {word:>6} {scale_name:<6}: {ws:.4f}",
                          file=sys.stderr)

    # Save
    save_data = {
        "model": "CompressorLM iterative (step_010000)",
        "binding_summary": binding_summary,
        "typing_summary": typing_summary,
        "binding_per_sentence": {
            s: all_binding_results[s] for s in scale_names
        },
        "comparison_32b": {
            "binding_gap_L28": 0.150,
            "is_within_sim_L28": 0.241,
            "every_within_sim_L28": 1.000,
        },
    }

    output_path = output_dir / "compressor_binding_analysis.json"
    with open(output_path, "w") as f:
        json.dump(save_data, f, indent=2)
    print(f"\nResults saved to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
