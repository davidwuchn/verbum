"""
Probe: WHERE and WHEN does Qwen3-32B build compositional structure?

Probe 1 showed typing is distributed — compression IS typing, no special
layer. This probe asks: is PARSING (tree structure / composition) also
distributed, or is there a distinct composition phase?

Method: Logit lens on nested S-expressions with known sub-results.

For `(+ 3 (* 4 5))`:
  - At the `)` closing `(* 4 5)`: when does the model predict "20"?
  - At the final `)`: when does the model predict "23"?
  - Does inner composition resolve BEFORE outer? (tree-ordered)

Also tests:
  - Depth 1 (flat): `(+ 3 4)` → 7
  - Depth 2 (nested): `(+ 3 (* 4 5))` → inner=20, outer=23
  - Depth 3 (deep): `(+ 1 (* 2 (- 10 3)))` → innermost=7, mid=14, outer=15
  - Math notation: `3 + 4 * 5` (same computation, different syntax)

The logit lens applies the final LayerNorm + LM head to intermediate
hidden states, revealing what the model is "thinking" at each layer.

Output: results/parse-structure/composition_timeline.json

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
OUTPUT_DIR = Path(__file__).parent.parent.parent / "results" / "parse-structure"


# ══════════════════════════════════════════════════════════════════
# Test expressions with known composition points
# ══════════════════════════════════════════════════════════════════

# Each entry: (expression_string, list_of_composition_points)
# Composition point: (description, target_token_text, expected_result_str, nesting_level)
# target_token_text is what we search for to find the position to probe

SEXPR_PROBES = [
    # ── Depth 1: flat operations ──
    {
        "expr": "(+ 3 4) =",
        "notation": "sexpr",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "7", "level": 0},
        ],
    },
    {
        "expr": "(* 6 7) =",
        "notation": "sexpr",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "42", "level": 0},
        ],
    },
    {
        "expr": "(- 15 8) =",
        "notation": "sexpr",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "7", "level": 0},
        ],
    },
    {
        "expr": "(* 9 3) =",
        "notation": "sexpr",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "27", "level": 0},
        ],
    },

    # ── Depth 2: one level of nesting ──
    {
        "expr": "(+ 3 (* 4 5)) =",
        "notation": "sexpr",
        "depth": 2,
        "points": [
            {"desc": "inner_result", "probe_after": "))", "expected": "23", "level": 0,
             "inner_expected": "20", "note": "inner (* 4 5)=20, outer (+ 3 20)=23"},
        ],
    },
    {
        "expr": "(* 2 (+ 3 7)) =",
        "notation": "sexpr",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "20", "level": 0,
             "note": "inner (+ 3 7)=10, outer (* 2 10)=20"},
        ],
    },
    {
        "expr": "(- (* 5 6) 8) =",
        "notation": "sexpr",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "22", "level": 0,
             "note": "inner (* 5 6)=30, outer (- 30 8)=22"},
        ],
    },
    {
        "expr": "(+ (* 3 3) (* 4 4)) =",
        "notation": "sexpr",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "25", "level": 0,
             "note": "left (* 3 3)=9, right (* 4 4)=16, outer (+ 9 16)=25"},
        ],
    },

    # ── Depth 3: two levels of nesting ──
    {
        "expr": "(+ 1 (* 2 (- 10 3))) =",
        "notation": "sexpr",
        "depth": 3,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "15", "level": 0,
             "note": "innermost (- 10 3)=7, mid (* 2 7)=14, outer (+ 1 14)=15"},
        ],
    },
    {
        "expr": "(* (+ 2 3) (- 9 4)) =",
        "notation": "sexpr",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "25", "level": 0,
             "note": "left (+ 2 3)=5, right (- 9 4)=5, outer (* 5 5)=25"},
        ],
    },

    # ── Math notation (same computations) ──
    {
        "expr": "3 + 4 =",
        "notation": "math",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "7", "level": 0},
        ],
    },
    {
        "expr": "6 * 7 =",
        "notation": "math",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "42", "level": 0},
        ],
    },
    {
        "expr": "3 + 4 * 5 =",
        "notation": "math",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "23", "level": 0,
             "note": "precedence: 4*5=20, then 3+20=23"},
        ],
    },
    {
        "expr": "2 * (3 + 7) =",
        "notation": "math",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "20", "level": 0},
        ],
    },
    {
        "expr": "5 * 6 - 8 =",
        "notation": "math",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "22", "level": 0,
             "note": "precedence: 5*6=30, then 30-8=22"},
        ],
    },
    {
        "expr": "3 * 3 + 4 * 4 =",
        "notation": "math",
        "depth": 2,
        "points": [
            {"desc": "result", "probe_after": "=", "expected": "25", "level": 0,
             "note": "3*3=9, 4*4=16, 9+16=25"},
        ],
    },

    # ── Prose notation ──
    {
        "expr": "What is three plus four? The answer is",
        "notation": "prose",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "is", "expected": "seven", "level": 0,
             "find_last": True},
        ],
    },
    {
        "expr": "What is six times seven? The answer is",
        "notation": "prose",
        "depth": 1,
        "points": [
            {"desc": "result", "probe_after": "is", "expected": "forty", "level": 0,
             "find_last": True, "note": "forty-two, first token"},
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
# Logit lens: apply final norm + LM head to intermediate layers
# ══════════════════════════════════════════════════════════════════

def logit_lens(
    model, tokenizer, text: str, probe_positions: dict[str, int],
    expected_tokens: dict[str, str], device: str,
    layer_sample: list[int] | None = None,
) -> dict:
    """Apply logit lens at every (or sampled) layer.

    Args:
        probe_positions: {point_name: token_position_to_probe}
        expected_tokens: {point_name: expected_next_token_string}
        layer_sample: which layers to probe (None = all)

    Returns:
        {point_name: {layer: {rank, prob, top5: [(token, prob), ...]}}}
    """
    inputs = tokenizer(text, return_tensors="pt").to(device)
    input_ids = inputs["input_ids"]
    n_layers = model.config.num_hidden_layers

    if layer_sample is None:
        layer_sample = list(range(n_layers))

    # Hook all sampled layers
    layer_outputs = {}

    def make_hook(layer_idx):
        def hook_fn(module, input, output):
            hidden = output[0] if isinstance(output, tuple) else output
            layer_outputs[layer_idx] = hidden.detach()
        return hook_fn

    hooks = []
    for li in layer_sample:
        h = model.model.layers[li].register_forward_hook(make_hook(li))
        hooks.append(h)

    # Forward pass
    with torch.no_grad():
        outputs = model(**inputs)

    # Get final layer norm and LM head
    final_norm = model.model.norm
    lm_head = model.lm_head

    results = {}

    for point_name, pos in probe_positions.items():
        expected_text = expected_tokens[point_name]
        # Tokenize the expected result to get its token ID
        expected_ids = tokenizer.encode(expected_text, add_special_tokens=False)
        if not expected_ids:
            print(f"  WARNING: couldn't tokenize expected '{expected_text}'",
                  file=sys.stderr)
            continue
        expected_id = expected_ids[0]  # First token of expected result

        layer_results = {}

        for li in layer_sample:
            hidden = layer_outputs[li]  # (1, seq_len, d)
            h_at_pos = hidden[0, pos, :]  # (d,)

            # Apply final norm + LM head
            h_normed = final_norm(h_at_pos.unsqueeze(0))  # (1, d)
            logits = lm_head(h_normed)[0]  # (vocab_size,)

            # Softmax for probabilities
            probs = torch.softmax(logits, dim=-1)

            # Rank and probability of expected token
            prob_expected = probs[expected_id].item()
            rank = (probs > prob_expected).sum().item()  # 0 = top prediction

            # Top 5 predictions
            top5_probs, top5_ids = torch.topk(probs, 5)
            top5 = [
                (tokenizer.decode([tid.item()]).strip(), tp.item())
                for tid, tp in zip(top5_ids, top5_probs)
            ]

            layer_results[li] = {
                "rank": int(rank),
                "prob": float(prob_expected),
                "top5": top5,
            }

        results[point_name] = layer_results

    # Also get the final output's prediction at each probe position
    final_logits = outputs.logits[0]  # (seq_len, vocab_size)
    for point_name, pos in probe_positions.items():
        expected_text = expected_tokens[point_name]
        expected_ids = tokenizer.encode(expected_text, add_special_tokens=False)
        if not expected_ids:
            continue
        expected_id = expected_ids[0]

        probs = torch.softmax(final_logits[pos], dim=-1)
        prob_expected = probs[expected_id].item()
        rank = (probs > prob_expected).sum().item()

        top5_probs, top5_ids = torch.topk(probs, 5)
        top5 = [
            (tokenizer.decode([tid.item()]).strip(), tp.item())
            for tid, tp in zip(top5_ids, top5_probs)
        ]

        results[point_name][n_layers] = {
            "rank": int(rank),
            "prob": float(prob_expected),
            "top5": top5,
            "note": "final_output",
        }

    # Cleanup
    for h in hooks:
        h.remove()

    return results


# ══════════════════════════════════════════════════════════════════
# Find probe positions in tokenized input
# ══════════════════════════════════════════════════════════════════

def find_probe_position(tokenizer, input_ids: torch.Tensor, target_text: str,
                        find_last: bool = False) -> int | None:
    """Find the token position corresponding to target_text.

    Returns the position of the LAST token of the target (so we probe
    the next-token prediction at that position).
    """
    tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())

    # Simple approach: find the target text in the token list
    target_lower = target_text.lower()

    matches = []
    for i, tok in enumerate(tokens):
        # Clean up token (remove Ġ prefix)
        clean = tok.replace("Ġ", "").replace("▁", "").strip()
        if clean.lower() == target_lower:
            matches.append(i)

    if not matches:
        # Try decoding each token
        for i in range(len(tokens)):
            decoded = tokenizer.decode([input_ids[0, i].item()]).strip()
            if decoded.lower() == target_lower:
                matches.append(i)

    if not matches:
        return None

    return matches[-1] if find_last else matches[0]


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Probe parse/composition structure")
    parser.add_argument("--gguf", default=DEFAULT_GGUF)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--output-dir", default=str(OUTPUT_DIR))
    parser.add_argument("--layer-stride", type=int, default=1,
                        help="Sample every Nth layer (1=all, 2=every other, etc.)")
    args = parser.parse_args()

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    # Load model
    model, tokenizer = load_model(args.gguf, device=args.device)
    n_layers = model.config.num_hidden_layers

    # Layer sampling
    layer_sample = list(range(0, n_layers, args.layer_stride))
    print(f"Probing {len(layer_sample)} layers (stride={args.layer_stride})",
          file=sys.stderr)

    all_results = []

    for probe_idx, probe in enumerate(SEXPR_PROBES):
        expr = probe["expr"]
        print(f"\n[{probe_idx+1}/{len(SEXPR_PROBES)}] {expr}", file=sys.stderr)

        # Tokenize
        inputs = tokenizer(expr, return_tensors="pt").to(args.device)
        input_ids = inputs["input_ids"]
        tokens = tokenizer.convert_ids_to_tokens(input_ids[0].tolist())

        # Show tokenization
        token_strs = []
        for i, t in enumerate(tokens):
            decoded = tokenizer.decode([input_ids[0, i].item()])
            token_strs.append(f"{i}:'{decoded.strip()}'")
        print(f"  Tokens: {' '.join(token_strs)}", file=sys.stderr)

        # Find probe positions
        probe_positions = {}
        expected_tokens = {}

        for point in probe["points"]:
            target = point["probe_after"]
            find_last = point.get("find_last", False)
            pos = find_probe_position(tokenizer, input_ids, target, find_last)

            if pos is None:
                print(f"  WARNING: couldn't find '{target}' in tokens", file=sys.stderr)
                continue

            point_name = point["desc"]
            probe_positions[point_name] = pos
            expected_tokens[point_name] = point["expected"]
            decoded_at_pos = tokenizer.decode([input_ids[0, pos].item()]).strip()
            print(f"  Probe '{point_name}' at pos {pos} (token='{decoded_at_pos}'), "
                  f"expecting '{point['expected']}'", file=sys.stderr)

        if not probe_positions:
            print(f"  SKIPPED: no valid probe positions", file=sys.stderr)
            continue

        # Run logit lens
        lens_results = logit_lens(
            model, tokenizer, expr, probe_positions, expected_tokens,
            args.device, layer_sample=layer_sample,
        )

        # Store results
        probe_result = {
            "expr": expr,
            "notation": probe["notation"],
            "depth": probe["depth"],
            "tokens": [tokenizer.decode([input_ids[0, i].item()]).strip()
                       for i in range(input_ids.shape[1])],
            "points": {},
        }

        for point_name, layer_data in lens_results.items():
            point_info = next(p for p in probe["points"] if p["desc"] == point_name)

            # Find key transitions: when does the expected token first enter top-5?
            # When does it become rank 0?
            first_top5 = None
            first_top1 = None
            first_prob_10pct = None

            timeline = []
            for li in sorted(layer_data.keys()):
                ld = layer_data[li]
                rank = ld["rank"]
                prob = ld["prob"]

                if first_top5 is None and rank < 5:
                    first_top5 = li
                if first_top1 is None and rank == 0:
                    first_top1 = li
                if first_prob_10pct is None and prob > 0.10:
                    first_prob_10pct = li

                timeline.append({
                    "layer": li,
                    "rank": rank,
                    "prob": round(prob, 6),
                    "top1": ld["top5"][0] if ld["top5"] else None,
                })

            probe_result["points"][point_name] = {
                "expected": point_info["expected"],
                "probe_pos": probe_positions.get(point_name),
                "note": point_info.get("note", ""),
                "first_top5_layer": first_top5,
                "first_top1_layer": first_top1,
                "first_prob_10pct_layer": first_prob_10pct,
                "timeline": timeline,
            }

            # Print summary
            final = layer_data.get(n_layers, layer_data.get(max(layer_data.keys())))
            print(f"  → '{point_name}': expect='{point_info['expected']}' | "
                  f"top5@L{first_top5} | top1@L{first_top1} | "
                  f"p>10%@L{first_prob_10pct} | "
                  f"final: rank={final['rank']}, p={final['prob']:.3f}, "
                  f"top1='{final['top5'][0][0] if final['top5'] else '?'}'",
                  file=sys.stderr)

        all_results.append(probe_result)

    # ══════════════════════════════════════════════════════════════
    # Summary analysis
    # ══════════════════════════════════════════════════════════════

    print(f"\n{'='*80}", file=sys.stderr)
    print(f"  COMPOSITION TIMELINE SUMMARY", file=sys.stderr)
    print(f"{'='*80}", file=sys.stderr)

    # Group by notation and depth
    by_notation = {}
    for r in all_results:
        key = (r["notation"], r["depth"])
        if key not in by_notation:
            by_notation[key] = []
        by_notation[key].append(r)

    print(f"\n  {'Notation':<8} {'Depth':>5} {'Expression':<35} {'Expected':>8} "
          f"{'Top5@':>6} {'Top1@':>6} {'P>10%@':>7} {'Final P':>8} {'Final Rank':>10}",
          file=sys.stderr)
    print(f"  {'-'*8} {'-'*5} {'-'*35} {'-'*8} {'-'*6} {'-'*6} {'-'*7} {'-'*8} {'-'*10}",
          file=sys.stderr)

    for r in all_results:
        for pname, pdata in r["points"].items():
            tl = pdata["timeline"]
            final = tl[-1] if tl else {}
            print(f"  {r['notation']:<8} {r['depth']:>5} {r['expr']:<35} "
                  f"{pdata['expected']:>8} "
                  f"{'L'+str(pdata['first_top5_layer']) if pdata['first_top5_layer'] is not None else 'never':>6} "
                  f"{'L'+str(pdata['first_top1_layer']) if pdata['first_top1_layer'] is not None else 'never':>6} "
                  f"{'L'+str(pdata['first_prob_10pct_layer']) if pdata['first_prob_10pct_layer'] is not None else 'never':>7} "
                  f"{final.get('prob', 0):>8.3f} "
                  f"{final.get('rank', '?'):>10}",
                  file=sys.stderr)

    # Notation comparison
    print(f"\n  CROSS-NOTATION COMPARISON (same computation, different syntax):", file=sys.stderr)
    print(f"  {'Computation':<25} {'S-expr top1@':>12} {'Math top1@':>12} {'Prose top1@':>12}",
          file=sys.stderr)
    print(f"  {'-'*25} {'-'*12} {'-'*12} {'-'*12}", file=sys.stderr)

    # Match computations across notations
    computations = {
        "3+4=7": {"sexpr": "(+ 3 4) =", "math": "3 + 4 =", "prose": "three plus four"},
        "6*7=42": {"sexpr": "(* 6 7) =", "math": "6 * 7 =", "prose": "six times seven"},
        "3+4*5=23": {"sexpr": "(+ 3 (* 4 5)) =", "math": "3 + 4 * 5 ="},
        "2*(3+7)=20": {"sexpr": "(* 2 (+ 3 7)) =", "math": "2 * (3 + 7) ="},
        "5*6-8=22": {"sexpr": "(- (* 5 6) 8) =", "math": "5 * 6 - 8 ="},
    }

    for comp_name, exprs in computations.items():
        line = f"  {comp_name:<25}"
        for notation in ["sexpr", "math", "prose"]:
            if notation not in exprs:
                line += f"  {'—':>12}"
                continue
            # Find matching result
            found = False
            for r in all_results:
                if r["notation"] == notation:
                    for pname, pdata in r["points"].items():
                        if r["expr"].startswith(exprs[notation][:10]):
                            t1 = pdata["first_top1_layer"]
                            line += f"  {'L'+str(t1) if t1 is not None else 'never':>12}"
                            found = True
                            break
                if found:
                    break
            if not found:
                line += f"  {'N/A':>12}"
        print(line, file=sys.stderr)

    # Save results
    output_path = output_dir / "composition_timeline.json"
    with open(output_path, "w") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nResults saved to {output_path}", file=sys.stderr)


if __name__ == "__main__":
    main()
