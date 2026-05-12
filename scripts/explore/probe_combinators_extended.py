#!/usr/bin/env python3
"""Extended combinator probe — W, S, and variable binding in Qwen3-32B.

The first probe (probe_combinators.py) confirmed K, I, B, C exist.
But {B, C, K, I} is NOT Turing-complete — you need W (duplicate) or
S (distribute) for variable binding where a variable appears more
than once.

This probe tests for:
  - W (duplicate/contract):  W f x = f x x  (use arg twice)
  - S (distribute):          S f g x = f x (g x)  (apply both, combine)
  - Variable binding:        λx. ... x ... x ...  (multiple use)
  - Abstraction:             Creating functions from expressions
  - Substitution:            Replacing bound variables with values

The question: does the 32B have separate circuits for these operations,
or does it handle them through its existing K/I/B/C infrastructure
plus the residual stream?

Usage:
    uv run python scripts/explore/probe_combinators_extended.py --quick
    uv run python scripts/explore/probe_combinators_extended.py

Output: results/combinator-probe-extended/

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer


DEFAULT_GGUF = "/Users/mwhitford/localai/models/Qwen3-32B-Q8_0.gguf"
HF_MODEL = "Qwen/Qwen3-32B"
OUTPUT_DIR = Path("results/combinator-probe-extended")


# ══════════════════════════════════════════════════════════════════
# Extended combinator probes
# ══════════════════════════════════════════════════════════════════

PROBES = {
    # ── W (duplicate/contract): use an argument more than once ────
    # Active: same entity used in two roles / variable used twice
    # Control: two different entities (no duplication needed)
    "W": {
        "description": "Duplication — same argument used twice, self-reference",
        "active": [
            "The man saw himself in the mirror on the wall.",
            "She taught herself to play the piano over the summer.",
            "The dog chased its own tail around and around the yard.",
            "He gave himself a pat on the back for his good work.",
            "The machine that built itself was truly remarkable indeed.",
            "Every student who respects himself will also respect others.",
        ],
        "control": [
            "The man saw the woman in the mirror on the wall.",
            "She taught the boy to play the piano over the summer.",
            "The dog chased the cat around and around the back yard.",
            "He gave the child a pat on the back for good work.",
            "The machine that built the bridge was truly remarkable indeed.",
            "Every student who respects the teacher will also respect others.",
        ],
    },

    # ── S (distribute): apply two functions to same arg, combine ──
    # Active: same subject does two things and they interact
    # Control: two different subjects do separate things
    "S": {
        "description": "Distribution — two operations on same argument combined",
        "active": [
            "The student who studies hard and who asks questions always succeeds.",
            "Anyone who both sings and dances will entertain the whole audience.",
            "The chef who cooks well and serves quickly earns great reviews.",
            "A person who reads widely and thinks deeply becomes truly wise.",
            "The athlete who trains daily and eats well wins many competitions.",
            "Every teacher who explains clearly and listens carefully helps students.",
        ],
        "control": [
            "The student studies hard and the teacher asks questions in class.",
            "The singer entertains and the dancer performs for the whole audience.",
            "The chef cooks well and the waiter serves quickly at dinner.",
            "The reader reads widely and the thinker thinks deeply about life.",
            "The athlete trains daily and the nutritionist eats well every day.",
            "The teacher explains clearly and the counselor listens carefully always.",
        ],
    },

    # ── Variable binding: multiple occurrences of bound variable ──
    # Active: pronoun/variable refers back multiple times
    # Control: no binding needed (all distinct referents)
    "bind": {
        "description": "Variable binding — same referent in multiple positions",
        "active": [
            "Every boy thinks that he is the smartest boy in his class.",
            "If a dog is hungry then it will eat whatever food it finds.",
            "No student who failed the test believed that she would pass it.",
            "Whoever finds the key should bring it back to its rightful owner.",
            "The woman who lost her bag went back to find her bag.",
            "Each player knows that if he wins then he gets the prize.",
        ],
        "control": [
            "Every boy thinks that Mary is the smartest girl in the class.",
            "If a dog is hungry then the cat will eat the special food.",
            "No student who failed the test believed that John would pass it.",
            "The finder should bring the key back to the rightful owner here.",
            "The woman who lost the bag went back to find the wallet.",
            "Each player knows that if John wins then Mary gets the prize.",
        ],
    },

    # ── Abstraction: creating a function from an expression ───────
    # Active: sentences that describe a general rule / function
    # Control: sentences about specific instances (no abstraction)
    "abstract": {
        "description": "Abstraction — forming general rules from specific patterns",
        "active": [
            "To solve any equation you must isolate the unknown variable first.",
            "Whatever you plant in spring will grow by the end of summer.",
            "However you approach this problem the answer will always be seven.",
            "Whoever wins the election will become the next leader of us.",
            "No matter what happens the sun will always rise in the east.",
            "For any number if you double it you get an even number.",
        ],
        "control": [
            "To solve this equation you must subtract three from both sides.",
            "The tomatoes planted in spring grew well by the end of summer.",
            "The direct approach to this problem gives the answer of seven.",
            "Johnson won the election and became the next leader of us.",
            "Despite the storm today the sun rose in the east at dawn.",
            "The number eight when doubled gives the even number of sixteen.",
        ],
    },
}

NULL_PROBES = [
    "The sun rose over the mountains in the early morning light.",
    "Water flows downhill following the path of least resistance always.",
    "The library was quiet and the shelves were full of old books.",
    "Birds flew south for the winter as the leaves began to fall.",
    "The clock on the wall showed that it was nearly midnight then.",
    "Clouds gathered in the sky promising rain by the afternoon today.",
]


# ══════════════════════════════════════════════════════════════════
# Model loading (reuse pattern from probe_combinators.py)
# ══════════════════════════════════════════════════════════════════


def load_model(gguf_path: str, device: str = "mps"):
    gguf_dir = str(Path(gguf_path).parent)
    gguf_file = Path(gguf_path).name
    print(f"Loading model from {gguf_path}...", file=sys.stderr)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(HF_MODEL)
    model = AutoModelForCausalLM.from_pretrained(
        gguf_dir, gguf_file=gguf_file,
        dtype=torch.float16, device_map=device,
        trust_remote_code=True,
        attn_implementation="eager",
    )
    model.eval()
    model.config.output_attentions = True
    t1 = time.time()
    print(f"Loaded in {t1-t0:.1f}s: {model.config.num_hidden_layers} layers, "
          f"d={model.config.hidden_size}", file=sys.stderr)
    return model, tokenizer


def capture_attention(model, tokenizer, text: str) -> dict:
    inputs = tokenizer(text, return_tensors="pt").to(model.device)
    token_ids = inputs["input_ids"][0].tolist()
    token_strs = [tokenizer.decode([tid]) for tid in token_ids]
    with torch.no_grad():
        outputs = model(**inputs, output_attentions=True)
    attn_list = []
    for layer_attn in outputs.attentions:
        attn_list.append(layer_attn[0].cpu().half().numpy())
    attentions = np.stack(attn_list, axis=0)
    return {
        "token_ids": token_ids,
        "token_strs": token_strs,
        "attentions": attentions,
        "n_tokens": len(token_ids),
    }


def head_selectivity(active_attn, control_attn):
    min_seq = min(active_attn.shape[2], control_attn.shape[2])
    a = active_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    c = control_attn[:, :, :min_seq, :min_seq].astype(np.float32)
    diff = a - c
    return np.sqrt(np.mean(diff ** 2, axis=(-2, -1)))


# ══════════════════════════════════════════════════════════════════
# Analysis
# ══════════════════════════════════════════════════════════════════


def compute_selectivity(model, tokenizer, probes, null_probes, quick=False):
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    results = {}

    print("  Capturing null baseline...", file=sys.stderr)
    null_attns = []
    for text in (null_probes[:2] if quick else null_probes):
        cap = capture_attention(model, tokenizer, text)
        null_attns.append(cap)
        torch.mps.empty_cache() if torch.backends.mps.is_available() else None

    for comb_name, comb_data in probes.items():
        active_texts = comb_data["active"][:3] if quick else comb_data["active"]
        control_texts = comb_data["control"][:3] if quick else comb_data["control"]
        n_pairs = min(len(active_texts), len(control_texts))

        print(f"  Probing {comb_name} ({comb_data['description']})...",
              file=sys.stderr)

        vs_control = np.zeros((n_layers, n_heads))
        for i in range(n_pairs):
            print(f"    pair {i+1}/{n_pairs}...", file=sys.stderr)
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            control_cap = capture_attention(model, tokenizer, control_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   control_cap["attentions"])
            vs_control += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_control /= n_pairs

        vs_null = np.zeros((n_layers, n_heads))
        n_null_pairs = min(n_pairs, len(null_attns))
        for i in range(n_null_pairs):
            active_cap = capture_attention(model, tokenizer, active_texts[i])
            sel = head_selectivity(active_cap["attentions"],
                                   null_attns[i]["attentions"])
            vs_null += sel
            torch.mps.empty_cache() if torch.backends.mps.is_available() else None
        vs_null /= max(n_null_pairs, 1)

        results[comb_name] = {
            "vs_control": vs_control,
            "vs_null": vs_null,
            "description": comb_data["description"],
        }

    return results


def cross_correlate(selectivity, kibc_path=None):
    """Cross-correlate extended combinators with each other and with KIBC."""
    ext_names = list(selectivity.keys())
    flat = {c: selectivity[c]["vs_control"].flatten() for c in ext_names}

    # Load KIBC results if available
    kibc_flat = {}
    if kibc_path and kibc_path.exists():
        kibc_data = np.load(str(kibc_path))
        for c in ["K", "I", "B", "C"]:
            key = f"{c}_vs_control"
            if key in kibc_data:
                kibc_flat[c] = kibc_data[key].flatten()

    all_names = list(kibc_flat.keys()) + ext_names
    all_flat = {**kibc_flat, **flat}

    n = len(all_names)
    corr = np.zeros((n, n))
    for i, ci in enumerate(all_names):
        for j, cj in enumerate(all_names):
            corr[i, j] = float(np.corrcoef(all_flat[ci], all_flat[cj])[0, 1])

    return all_names, corr


# ══════════════════════════════════════════════════════════════════
# Visualization
# ══════════════════════════════════════════════════════════════════


def plot_extended_heatmaps(selectivity, output_dir):
    names = list(selectivity.keys())
    n = len(names)
    fig, axes = plt.subplots(1, n, figsize=(6*n, 8))
    if n == 1:
        axes = [axes]

    fig.suptitle("Extended Combinator Selectivity — Qwen3-32B\n"
                 "(active vs matched control)", fontsize=14, fontweight="bold")

    vmax = max(selectivity[c]["vs_control"].max() for c in names) * 0.8

    for idx, cname in enumerate(names):
        ax = axes[idx]
        data = selectivity[cname]["vs_control"]
        im = ax.imshow(data, aspect="auto", cmap="hot",
                       interpolation="nearest", vmin=0, vmax=vmax)
        ax.set_title(f"{cname}\n({selectivity[cname]['description'][:30]})",
                     fontsize=10)
        ax.set_xlabel("Head")
        ax.set_ylabel("Layer")
        plt.colorbar(im, ax=ax, shrink=0.8)

    plt.tight_layout()
    fig.savefig(output_dir / "extended_heatmaps.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: extended_heatmaps.png", file=sys.stderr)


def plot_full_correlation(all_names, corr, output_dir):
    fig, ax = plt.subplots(figsize=(10, 9))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    n = len(all_names)
    ax.set_xticks(range(n))
    ax.set_yticks(range(n))
    ax.set_xticklabels(all_names, fontsize=11, rotation=45, ha="right")
    ax.set_yticklabels(all_names, fontsize=11)

    for i in range(n):
        for j in range(n):
            ax.text(j, i, f"{corr[i,j]:.2f}", ha="center", va="center",
                    fontsize=9, fontweight="bold",
                    color="white" if abs(corr[i,j]) > 0.5 else "black")

    # Draw separator between KIBC and extended
    n_kibc = sum(1 for name in all_names if name in {"K", "I", "B", "C"})
    if 0 < n_kibc < n:
        ax.axhline(n_kibc - 0.5, color="black", linewidth=2)
        ax.axvline(n_kibc - 0.5, color="black", linewidth=2)

    ax.set_title("KIBC + Extended Combinator Cross-Correlation\n"
                 "Qwen3-32B — same heads respond = high correlation",
                 fontsize=12, fontweight="bold")
    plt.colorbar(im, label="Pearson r")
    plt.tight_layout()
    fig.savefig(output_dir / "full_correlation.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: full_correlation.png", file=sys.stderr)


def plot_layer_profiles(selectivity, output_dir):
    names = list(selectivity.keys())
    colors = ["#9b59b6", "#e67e22", "#1abc9c", "#e74c3c"]

    fig, ax = plt.subplots(figsize=(14, 6))
    for i, cname in enumerate(names):
        data = selectivity[cname]["vs_control"]
        mean_by_layer = data.mean(axis=1)
        color = colors[i % len(colors)]
        ax.plot(mean_by_layer, color=color, linewidth=2,
                label=f"{cname} — peak L{np.argmax(mean_by_layer)}")
        ax.fill_between(range(len(mean_by_layer)), mean_by_layer,
                        alpha=0.15, color=color)

    ax.set_xlabel("Layer")
    ax.set_ylabel("Mean selectivity")
    ax.set_title("Extended Combinator Layer Profiles — Qwen3-32B",
                 fontsize=12, fontweight="bold")
    ax.legend()
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    fig.savefig(output_dir / "extended_layer_profiles.png", dpi=150)
    plt.close(fig)
    print(f"  Saved: extended_layer_profiles.png", file=sys.stderr)


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="Extended combinator probe — W, S, binding, abstraction")
    parser.add_argument("--gguf", default=DEFAULT_GGUF)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--quick", action="store_true")
    parser.add_argument("--output-dir", type=Path, default=OUTPUT_DIR)
    parser.add_argument("--kibc-results", type=Path,
                        default=Path("results/combinator-probe/selectivity_matrices.npz"),
                        help="Path to KIBC probe NPZ for cross-correlation")
    args = parser.parse_args()

    args.output_dir.mkdir(parents=True, exist_ok=True)

    model, tokenizer = load_model(args.gguf, args.device)
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  Model: {n_layers} layers, {n_heads} heads", file=sys.stderr)

    # ── Selectivity analysis ──────────────────────────────
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"  Extended combinator selectivity", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)

    t0 = time.time()
    selectivity = compute_selectivity(
        model, tokenizer, PROBES, NULL_PROBES, quick=args.quick)
    elapsed = time.time() - t0

    # ── Summary ───────────────────────────────────────────
    ext_names = list(PROBES.keys())
    print(f"\n  Extended combinator selectivity (vs matched control):")
    print(f"  {'Comb':>8} {'Mean':>8} {'Max':>8} {'MaxLayer':>9} {'MaxHead':>8}")
    print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*9} {'─'*8}")
    for cname in ext_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        print(f"  {cname:>8} {data.mean():>8.5f} {data.max():>8.5f} "
              f"L{max_idx[0]:>3}      H{max_idx[1]:>3}")

    # ── Cross-correlation with KIBC ───────────────────────
    print(f"\n  Cross-correlation (KIBC + extended):")
    all_names, corr = cross_correlate(selectivity, args.kibc_results)

    print(f"  {'':>8}", end="")
    for name in all_names:
        print(f" {name:>7}", end="")
    print()
    for i, ci in enumerate(all_names):
        print(f"  {ci:>8}", end="")
        for j in range(len(all_names)):
            print(f" {corr[i,j]:>7.3f}", end="")
        print()

    # Key question: do W/S/bind correlate with KIBC or are they new?
    if "K" in all_names and "W" in all_names:
        ki = all_names.index("K")
        wi = all_names.index("W")
        bi = all_names.index("B")
        si_idx = all_names.index("S") if "S" in all_names else None
        bind_idx = all_names.index("bind") if "bind" in all_names else None

        print(f"\n  Key correlations (are extended combinators new circuits?):")
        for ext in ["W", "S", "bind", "abstract"]:
            if ext in all_names:
                ei = all_names.index(ext)
                max_kibc = max(corr[ei, all_names.index(c)]
                               for c in ["K", "I", "B", "C"]
                               if c in all_names)
                max_kibc_name = max(
                    ((c, corr[ei, all_names.index(c)])
                     for c in ["K", "I", "B", "C"] if c in all_names),
                    key=lambda x: x[1]
                )[0]
                print(f"    {ext:>8} → most correlated KIBC: {max_kibc_name} "
                      f"(r={max_kibc:.3f})"
                      f"{'  ← SHARED circuit' if max_kibc > 0.85 else ''}"
                      f"{'  ← RELATED circuit' if 0.7 < max_kibc <= 0.85 else ''}"
                      f"{'  ← DISTINCT circuit' if max_kibc <= 0.7 else ''}")

    # ── Dominant combinator per head (extended only) ──────
    sel_matrix = np.stack(
        [selectivity[c]["vs_control"] for c in ext_names], axis=0)
    dominant = np.argmax(sel_matrix, axis=0)
    print(f"\n  Head assignment (extended combinators only):")
    for ci, cname in enumerate(ext_names):
        count = int(np.sum(dominant == ci))
        pct = count / dominant.size * 100
        print(f"    {cname:>8}: {count:>5} heads ({pct:>5.1f}%)")

    # ── Top heads per extended combinator ─────────────────
    for cname in ext_names:
        data = selectivity[cname]["vs_control"]
        flat = data.flatten()
        top_idx = np.argsort(flat)[-5:][::-1]
        print(f"\n  Top {cname}-selective heads:")
        for idx in top_idx:
            layer = idx // n_heads
            head = idx % n_heads
            score = float(flat[idx])
            print(f"    L{layer:>2}:H{head:>2}  score={score:.5f}")

    # ── Visualizations ────────────────────────────────────
    plot_extended_heatmaps(selectivity, args.output_dir)
    plot_full_correlation(all_names, corr, args.output_dir)
    plot_layer_profiles(selectivity, args.output_dir)

    # ── Save results ──────────────────────────────────────
    output = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ"),
        "model": HF_MODEL,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "quick_mode": args.quick,
        "elapsed_s": elapsed,
        "extended_selectivity": {},
        "cross_correlation_names": all_names,
        "cross_correlation_matrix": corr.tolist(),
    }

    for cname in ext_names:
        data = selectivity[cname]["vs_control"]
        max_idx = np.unravel_index(np.argmax(data), data.shape)
        output["extended_selectivity"][cname] = {
            "description": PROBES[cname]["description"],
            "mean": float(data.mean()),
            "max": float(data.max()),
            "std": float(data.std()),
            "max_layer": int(max_idx[0]),
            "max_head": int(max_idx[1]),
        }

    np.savez_compressed(
        str(args.output_dir / "extended_matrices.npz"),
        **{f"{c}_vs_control": selectivity[c]["vs_control"] for c in ext_names},
    )

    json_path = args.output_dir / "extended_probe_results.json"
    json_path.write_text(json.dumps(output, indent=2, default=str))

    print(f"\n  💾 Results: {json_path}", file=sys.stderr)
    print(f"  💾 Matrices: {args.output_dir / 'extended_matrices.npz'}",
          file=sys.stderr)
    print(f"  Total: {elapsed:.1f}s", file=sys.stderr)


if __name__ == "__main__":
    main()
