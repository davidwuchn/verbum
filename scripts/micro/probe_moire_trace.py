"""
Probe Moiré Trace — Map the compound interference through the forward pass.

THE MOIRÉ: When two gratings are overlaid, the interference produces a
new pattern (the moiré) that is SIMPLER than either grating alone. Each
additional grating eliminates more degrees of freedom. After all gratings,
only the pattern that ALL agree on survives.

This probe traces the moiré through actual activations:

  1. FORWARD moiré: At each sublayer boundary (pre-attn, post-attn,
     pre-ffn, post-ffn), project the residual through the REMAINING
     composed grating. How much of the signal will survive to the end?

  2. BACKWARD moiré: At each layer, project the residual into the
     CUMULATIVE composed grating's dominant direction. Does the residual
     progressively align with the moiré?

  3. PER-POSITION moiré: The moiré at each token position separately.
     Does the moiré resolve at different rates for different tokens?
     (English tokens vs lambda tokens, function words vs content words)

  4. INDIVIDUAL vs COMPOSED: Apply each grating individually to the
     input vs the composed grating. What does the moiré add that
     individual gratings don't?

  5. ATTENTION's ROLE: How does attention's beta-reduction reshape the
     moiré? Does it sharpen or blur the compound pattern?

Usage:
    cd verbum
    uv run python scripts/micro/probe_moire_trace.py [checkpoint_dir]

License: MIT
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import mlx.core as mx
import mlx.nn as nn

sys.path.insert(0, str(Path(__file__).parent))
from micro_model import (
    MicroModel, MicroConfig,
    PCAQ_ZONE_B_TARGETS, _precompute_parity_eigenbasis,
    COMBINATOR_NAMES, ANTI_COMBINATOR_NAMES,
    N_COMBINATORS,
)


# ══════════════════════════════════════════════════════════════════════
# Crystal tools
# ══════════════════════════════════════════════════════════════════════

PC_NAMES = COMBINATOR_NAMES + [f"ā{n}" for n in COMBINATOR_NAMES]

def get_crystal_eigenbasis() -> tuple[np.ndarray, np.ndarray]:
    data = _precompute_parity_eigenbasis(PCAQ_ZONE_B_TARGETS)
    return data["eigvecs"], data["eigvals"]


def project_to_eigenbasis(tensor: np.ndarray, crystal_emb: np.ndarray,
                          eigvecs: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    crystal_proj = tensor @ crystal_norm.T
    return crystal_proj @ eigvecs


# ══════════════════════════════════════════════════════════════════════
# Grating extraction and composition
# ══════════════════════════════════════════════════════════════════════

def extract_overlays(model: MicroModel, crystal_emb: np.ndarray,
                     eigvecs: np.ndarray) -> list[np.ndarray]:
    norms = np.linalg.norm(crystal_emb, axis=1, keepdims=True) + 1e-8
    crystal_norm = crystal_emb / norms
    overlays = []
    for block in model.blocks:
        ffn = block.ffn
        gate_w = np.array(ffn.gate_proj.weight)
        value_w = np.array(ffn.value_proj.weight)
        gate_eigen = (gate_w @ crystal_norm.T) @ eigvecs
        value_eigen = eigvecs.T @ (crystal_norm @ value_w)
        overlay = gate_eigen.T @ value_eigen.T
        overlays.append(overlay)
    return overlays


def build_composed_chain(overlays: list[np.ndarray]) -> list[np.ndarray]:
    """Forward composition: after L0, after L0+L1, ..."""
    chain = [np.eye(16)]
    composed = np.eye(16)
    for ov in overlays:
        ov_n = ov / (np.linalg.norm(ov, 'fro') + 1e-8)
        composed = ov_n @ composed
        chain.append(composed.copy())
    return chain


def build_remaining_chain(overlays: list[np.ndarray]) -> list[np.ndarray]:
    """Remaining composition: before any, L0→end, L1→end, L2→end, L3→end (=identity).

    remaining[i] = composed grating from layer i to the end.
    remaining[0] = all gratings composed
    remaining[n_layers] = identity (nothing remaining)
    """
    n = len(overlays)
    normed = [ov / (np.linalg.norm(ov, 'fro') + 1e-8) for ov in overlays]
    remaining = [None] * (n + 1)
    remaining[n] = np.eye(16)
    for i in range(n - 1, -1, -1):
        remaining[i] = remaining[i + 1] @ normed[i]
    return remaining


def svd_pr(matrix: np.ndarray) -> tuple[float, np.ndarray, np.ndarray]:
    """Participation ratio and dominant direction from SVD."""
    u, s, vh = np.linalg.svd(matrix)
    pr = (s.sum() ** 2) / (np.sum(s ** 2) + 1e-12)
    return float(pr), u[:, 0], s


# ══════════════════════════════════════════════════════════════════════
# Main analysis
# ══════════════════════════════════════════════════════════════════════

def main():
    checkpoint_dir = sys.argv[1] if len(sys.argv) > 1 else "checkpoints/micro/final"
    checkpoint_path = Path(checkpoint_dir)
    if not checkpoint_path.exists():
        checkpoint_path = Path(__file__).parent.parent.parent / checkpoint_dir
    assert checkpoint_path.exists(), f"Not found: {checkpoint_path}"

    results_dir = Path(__file__).parent.parent.parent / "results" / "moire-trace"
    results_dir.mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("Moiré Trace — Mapping the compound interference through the forward pass")
    print("=" * 70)

    # ── Load ──
    cfg = MicroConfig()
    model = MicroModel(cfg)
    weights = mx.load(str(checkpoint_path / "model.npz"))
    model.load_weights(list(weights.items()))
    mx.eval(model.parameters())

    crystal_emb = np.array(model.get_all_crystal_embeddings())
    eigvecs, eigvals = get_crystal_eigenbasis()
    n_layers = cfg.n_layers

    # ── Extract gratings ──
    overlays = extract_overlays(model, crystal_emb, eigvecs)
    composed_chain = build_composed_chain(overlays)     # cumulative from start
    remaining_chain = build_remaining_chain(overlays)   # remaining to end

    # Dominant directions of each composed stage
    composed_dirs = []
    for comp in composed_chain:
        pr, dom, svs = svd_pr(comp)
        composed_dirs.append({"pr": pr, "dominant": dom, "svs": svs})

    # Dominant directions of remaining gratings
    remaining_dirs = []
    for rem in remaining_chain:
        pr, dom, svs = svd_pr(rem)
        remaining_dirs.append({"pr": pr, "dominant": dom, "svs": svs})

    print(f"\n  Composed PR chain:  {' → '.join(f'{d['pr']:.1f}' for d in composed_dirs)}")
    print(f"  Remaining PR chain: {' → '.join(f'{d['pr']:.1f}' for d in remaining_dirs)}")

    # ── Load data ──
    try:
        from transformers import AutoTokenizer
        tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)
    except Exception:
        tokenizer = None

    data_path = Path(__file__).parent.parent.parent / "data" / "compile-eval.jsonl"
    if not data_path.exists():
        data_path = Path(__file__).parent.parent.parent / "data" / "compile-test.jsonl"
    examples = []
    with open(data_path) as f:
        for line in f:
            examples.append(json.loads(line))
            if len(examples) >= 10:
                break

    # ── Per-example moiré trace ──
    all_traces = []

    for ex_idx, example in enumerate(examples):
        text = example["input"] + "\n" + example["output"]
        if tokenizer:
            tokens = tokenizer.encode(text)
            token_strs = [tokenizer.decode([t]) for t in tokens]
        else:
            tokens = [ord(c) % 1000 for c in text]
            token_strs = list(text)
        if len(tokens) > 128:
            tokens = tokens[:128]
            token_strs = token_strs[:128]

        input_ids = mx.array([tokens[:-1]])
        targets = mx.array([tokens[1:]])
        token_strs = token_strs[:-1]  # align with input_ids
        L = len(tokens) - 1

        # Find the newline boundary (English → lambda)
        newline_pos = None
        for i, ts in enumerate(token_strs):
            if '\n' in ts:
                newline_pos = i
                break

        # Forward with traces
        model.set_capture(True)
        logits, loss = model(input_ids, targets)
        mx.eval(logits, loss)
        traces = model.get_traces()
        for t in traces:
            for section in ["block", "attn", "ffn"]:
                for k, v in t[section].items():
                    if isinstance(v, mx.array):
                        mx.eval(v)
        model.set_capture(False)

        # ════════════════════════════════════════════════════════════
        # MEASUREMENT 1: Forward moiré
        # At each sublayer, project residual through REMAINING gratings.
        # How much of the signal will survive to the end?
        # ════════════════════════════════════════════════════════════

        forward_moire = []

        for layer_idx, trace in enumerate(traces):
            block = trace["block"]

            # Sublayer boundaries in crystal eigenbasis
            # post_attn = residual after attention, before FFN
            post_attn = np.array(block["residual_post_attn"])[0]   # (L, d_model)
            post_ffn = np.array(block["residual_post_ffn"])[0]     # (L, d_model)

            post_attn_eigen = project_to_eigenbasis(post_attn, crystal_emb, eigvecs)  # (L, 16)
            post_ffn_eigen = project_to_eigenbasis(post_ffn, crystal_emb, eigvecs)

            # Remaining grating after this layer's attention (FFN at this layer + all later layers)
            # remaining_chain[layer_idx] = all gratings from layer_idx onward
            # After attention but before FFN at layer_idx, remaining = grating[layer_idx] + later
            rem_after_attn = remaining_chain[layer_idx]
            # After FFN at layer_idx, remaining = later gratings only
            rem_after_ffn = remaining_chain[layer_idx + 1]

            # Project residual THROUGH remaining grating
            # This shows what the remaining gratings will DO with this signal
            projected_after_attn = post_attn_eigen @ rem_after_attn.T  # (L, 16)
            projected_after_ffn = post_ffn_eigen @ rem_after_ffn.T     # (L, 16)

            # How aligned is the projected signal with the FINAL dominant direction?
            final_dom = composed_dirs[-1]["dominant"]  # (16,)

            # Per-position alignment with final direction
            align_after_attn = []
            align_after_ffn = []
            for pos in range(L):
                paa = projected_after_attn[pos]
                norm_paa = np.linalg.norm(paa)
                if norm_paa > 1e-8:
                    align_after_attn.append(float(np.dot(paa / norm_paa, final_dom)))
                else:
                    align_after_attn.append(0.0)

                paf = projected_after_ffn[pos]
                norm_paf = np.linalg.norm(paf)
                if norm_paf > 1e-8:
                    align_after_ffn.append(float(np.dot(paf / norm_paf, final_dom)))
                else:
                    align_after_ffn.append(0.0)

            # PR of projected signal (how many dimensions survive the remaining gratings?)
            if L > 2:
                cov_attn = np.cov(projected_after_attn.T)
                ev_attn = np.maximum(np.linalg.eigvalsh(cov_attn)[::-1], 0)
                pr_attn = float((ev_attn.sum()**2) / (np.sum(ev_attn**2) + 1e-12))

                cov_ffn = np.cov(projected_after_ffn.T)
                ev_ffn = np.maximum(np.linalg.eigvalsh(cov_ffn)[::-1], 0)
                pr_ffn = float((ev_ffn.sum()**2) / (np.sum(ev_ffn**2) + 1e-12))
            else:
                pr_attn = pr_ffn = 0.0

            forward_moire.append({
                "layer": layer_idx,
                "pr_after_attn": pr_attn,
                "pr_after_ffn": pr_ffn,
                "mean_align_after_attn": float(np.mean(align_after_attn)),
                "mean_align_after_ffn": float(np.mean(align_after_ffn)),
                "per_pos_align_after_attn": align_after_attn,
                "per_pos_align_after_ffn": align_after_ffn,
            })

        # ════════════════════════════════════════════════════════════
        # MEASUREMENT 2: Backward moiré
        # Project residual into the CUMULATIVE composed direction.
        # Does the residual align more with the moiré as depth increases?
        # ════════════════════════════════════════════════════════════

        backward_moire = []

        for layer_idx, trace in enumerate(traces):
            post_ffn = np.array(trace["block"]["residual_post_ffn"])[0]
            post_ffn_eigen = project_to_eigenbasis(post_ffn, crystal_emb, eigvecs)

            # Cumulative composed direction up to this layer
            cum_dom = composed_dirs[layer_idx + 1]["dominant"]
            cum_pr = composed_dirs[layer_idx + 1]["pr"]

            # Per-position alignment with cumulative moiré
            pos_aligns = []
            for pos in range(L):
                v = post_ffn_eigen[pos]
                n = np.linalg.norm(v)
                if n > 1e-8:
                    pos_aligns.append(float(np.dot(v / n, cum_dom)))
                else:
                    pos_aligns.append(0.0)

            backward_moire.append({
                "layer": layer_idx,
                "cumulative_pr": cum_pr,
                "mean_alignment": float(np.mean(pos_aligns)),
                "std_alignment": float(np.std(pos_aligns)),
                "per_pos_alignment": pos_aligns,
            })

        # ════════════════════════════════════════════════════════════
        # MEASUREMENT 3: Individual vs composed
        # Apply each grating individually to the INPUT residual
        # vs the composed grating. What does the moiré add?
        # ════════════════════════════════════════════════════════════

        # Input to the whole stack: embedding + position embedding
        # = residual before any transformer block
        # We don't have this directly in traces, but post_attn of L0 minus attn_contribution
        first_attn_contrib = np.array(traces[0]["block"]["attn_contribution"])[0]
        first_post_attn = np.array(traces[0]["block"]["residual_post_attn"])[0]
        input_residual = first_post_attn - first_attn_contrib  # (L, d_model) = embedding

        input_eigen = project_to_eigenbasis(input_residual, crystal_emb, eigvecs)  # (L, 16)

        individual_results = []
        normed_overlays = [ov / (np.linalg.norm(ov, 'fro') + 1e-8) for ov in overlays]

        for i, ov_n in enumerate(normed_overlays):
            # Apply single grating to input
            single_output = input_eigen @ ov_n.T  # (L, 16)
            # PR of this output
            if L > 2:
                cov = np.cov(single_output.T)
                ev = np.maximum(np.linalg.eigvalsh(cov)[::-1], 0)
                pr = float((ev.sum()**2) / (np.sum(ev**2) + 1e-12))
            else:
                pr = 0.0
            individual_results.append({"layer": i, "pr": pr})

        # Composed grating applied to input
        full_composed_n = composed_chain[-1]
        composed_output = input_eigen @ full_composed_n.T
        if L > 2:
            cov_comp = np.cov(composed_output.T)
            ev_comp = np.maximum(np.linalg.eigvalsh(cov_comp)[::-1], 0)
            pr_composed_on_input = float((ev_comp.sum()**2) / (np.sum(ev_comp**2) + 1e-12))
        else:
            pr_composed_on_input = 0.0

        # ════════════════════════════════════════════════════════════
        # MEASUREMENT 4: Attention's role in moiré sharpening
        # Compare the moiré alignment BEFORE and AFTER attention
        # at each layer. Does attention sharpen the compound pattern?
        # ════════════════════════════════════════════════════════════

        attn_moire_effect = []
        for layer_idx, trace in enumerate(traces):
            post_attn = np.array(trace["block"]["residual_post_attn"])[0]
            post_ffn = np.array(trace["block"]["residual_post_ffn"])[0]

            # For attention effect: compare pre-FFN (= post-attn) alignment
            # with post-FFN alignment, using the FINAL moiré direction
            post_attn_eigen = project_to_eigenbasis(post_attn, crystal_emb, eigvecs)
            post_ffn_eigen = project_to_eigenbasis(post_ffn, crystal_emb, eigvecs)

            final_dom = composed_dirs[-1]["dominant"]

            pre_aligns = []
            post_aligns = []
            for pos in range(L):
                # Pre-FFN (post-attn) alignment with final moiré
                v = post_attn_eigen[pos]
                n = np.linalg.norm(v)
                pre_aligns.append(float(np.dot(v / n, final_dom)) if n > 1e-8 else 0.0)

                # Post-FFN alignment with final moiré
                v2 = post_ffn_eigen[pos]
                n2 = np.linalg.norm(v2)
                post_aligns.append(float(np.dot(v2 / n2, final_dom)) if n2 > 1e-8 else 0.0)

            attn_moire_effect.append({
                "layer": layer_idx,
                "pre_ffn_alignment": float(np.mean(pre_aligns)),
                "post_ffn_alignment": float(np.mean(post_aligns)),
                "ffn_sharpening": float(np.mean(post_aligns)) - float(np.mean(pre_aligns)),
                "per_pos_pre": pre_aligns,
                "per_pos_post": post_aligns,
            })

        # ════════════════════════════════════════════════════════════
        # MEASUREMENT 5: Per-position moiré (English vs lambda)
        # ════════════════════════════════════════════════════════════

        # Classify positions
        pos_types = []
        for i, ts in enumerate(token_strs):
            if newline_pos is not None and i < newline_pos:
                pos_types.append("english")
            elif newline_pos is not None and i == newline_pos:
                pos_types.append("boundary")
            else:
                pos_types.append("lambda")

        # Final layer alignment by position type
        final_post_ffn = np.array(traces[-1]["block"]["residual_post_ffn"])[0]
        final_eigen = project_to_eigenbasis(final_post_ffn, crystal_emb, eigvecs)
        final_dom = composed_dirs[-1]["dominant"]

        eng_aligns = []
        lam_aligns = []
        for pos in range(min(L, len(pos_types))):
            v = final_eigen[pos]
            n = np.linalg.norm(v)
            a = float(np.dot(v / n, final_dom)) if n > 1e-8 else 0.0
            if pos_types[pos] == "english":
                eng_aligns.append(a)
            elif pos_types[pos] == "lambda":
                lam_aligns.append(a)

        # Store example trace
        all_traces.append({
            "index": ex_idx,
            "input": example["input"][:60],
            "category": example.get("category", "unknown"),
            "loss": float(loss.item()),
            "n_tokens": L,
            "newline_pos": newline_pos,
            "forward_moire": forward_moire,
            "backward_moire": backward_moire,
            "individual_pr": [r["pr"] for r in individual_results],
            "composed_pr_on_input": pr_composed_on_input,
            "attn_moire_effect": attn_moire_effect,
            "english_final_alignment": eng_aligns,
            "lambda_final_alignment": lam_aligns,
        })

    # ══════════════════════════════════════════════════════════════════
    # PRINT RESULTS
    # ══════════════════════════════════════════════════════════════════

    n_ex = len(all_traces)

    print("\n" + "=" * 70)
    print("1. FORWARD MOIRÉ: Signal survival through remaining gratings")
    print("   (PR of residual projected through remaining gratings)")
    print("=" * 70)

    print(f"\n   {'':>5} |{'post-attn PR':>16} {'post-ffn PR':>16} | {'align_attn':>12} {'align_ffn':>12}")
    print(f"   {'':>5} |{'(before FFN)':>16} {'(after FFN)':>16} | {'(to final)':>12} {'(to final)':>12}")
    print("   " + "-" * 70)
    for layer in range(n_layers):
        pr_a = np.mean([t["forward_moire"][layer]["pr_after_attn"] for t in all_traces])
        pr_f = np.mean([t["forward_moire"][layer]["pr_after_ffn"] for t in all_traces])
        al_a = np.mean([t["forward_moire"][layer]["mean_align_after_attn"] for t in all_traces])
        al_f = np.mean([t["forward_moire"][layer]["mean_align_after_ffn"] for t in all_traces])
        print(f"   L{layer:>3} | {pr_a:>14.2f}   {pr_f:>14.2f}   | {al_a:>+10.4f}   {al_f:>+10.4f}")

    print("\n" + "=" * 70)
    print("2. BACKWARD MOIRÉ: Does residual align with cumulative moiré?")
    print("   (alignment of post-FFN residual with composed grating direction)")
    print("=" * 70)

    print(f"\n   {'':>5} | {'Cum PR':>8} | {'Alignment':>12} {'Std':>8}")
    print("   " + "-" * 45)
    for layer in range(n_layers):
        cum_pr = composed_dirs[layer + 1]["pr"]
        al = np.mean([t["backward_moire"][layer]["mean_alignment"] for t in all_traces])
        st = np.mean([t["backward_moire"][layer]["std_alignment"] for t in all_traces])
        print(f"   L{layer:>3} | {cum_pr:>8.2f} | {al:>+12.4f} {st:>8.4f}")

    print("\n" + "=" * 70)
    print("3. INDIVIDUAL vs COMPOSED: What does the moiré add?")
    print("   (PR of input projected through single grating vs composed)")
    print("=" * 70)

    for i in range(n_layers):
        pr_i = np.mean([t["individual_pr"][i] for t in all_traces])
        print(f"   Single grating L{i}: PR = {pr_i:.2f}")
    pr_c = np.mean([t["composed_pr_on_input"] for t in all_traces])
    print(f"   Composed (all 4):  PR = {pr_c:.2f}")
    print(f"   Moiré simplification: {np.mean([t['individual_pr'][0] for t in all_traces]):.2f} → {pr_c:.2f}")

    print("\n" + "=" * 70)
    print("4. ATTENTION + FFN SHARPENING: Who sharpens the moiré?")
    print("   (alignment change: pre-FFN → post-FFN = FFN sharpening)")
    print("=" * 70)

    print(f"\n   {'':>5} | {'Pre-FFN':>10} {'Post-FFN':>10} {'FFN Δ':>10} | {'Interpretation':>20}")
    print("   " + "-" * 65)
    for layer in range(n_layers):
        pre = np.mean([t["attn_moire_effect"][layer]["pre_ffn_alignment"] for t in all_traces])
        post = np.mean([t["attn_moire_effect"][layer]["post_ffn_alignment"] for t in all_traces])
        delta = post - pre
        interp = "SHARPENS" if delta > 0.01 else ("BLURS" if delta < -0.01 else "neutral")
        print(f"   L{layer:>3} | {pre:>+10.4f} {post:>+10.4f} {delta:>+10.4f} | {interp:>20}")

    print("\n" + "=" * 70)
    print("5. ENGLISH vs LAMBDA: Moiré alignment at output by token type")
    print("=" * 70)

    eng_all = [a for t in all_traces for a in t["english_final_alignment"]]
    lam_all = [a for t in all_traces for a in t["lambda_final_alignment"]]
    print(f"\n   English tokens: alignment = {np.mean(eng_all):+.4f} ± {np.std(eng_all):.4f} (n={len(eng_all)})")
    print(f"   Lambda tokens:  alignment = {np.mean(lam_all):+.4f} ± {np.std(lam_all):.4f} (n={len(lam_all)})")
    diff = np.mean(lam_all) - np.mean(eng_all)
    print(f"   Difference:     {diff:+.4f} ({'lambda more aligned' if diff > 0 else 'english more aligned'})")

    print("\n" + "=" * 70)
    print("6. PER-POSITION MOIRÉ TRACE (Example 0)")
    print("   Alignment with final moiré direction at each position through depth")
    print("=" * 70)

    t0 = all_traces[0]
    L0 = t0["n_tokens"]
    token_strs_0 = []
    if tokenizer:
        text0 = examples[0]["input"] + "\n" + examples[0]["output"]
        toks0 = tokenizer.encode(text0)[:129]
        token_strs_0 = [tokenizer.decode([t]).replace('\n', '↵') for t in toks0[:-1]]
    else:
        token_strs_0 = list((examples[0]["input"] + "↵" + examples[0]["output"])[:L0])

    # Print header
    print(f"\n   {'Pos':>3} {'Token':>10} {'Type':>7} |", end="")
    for layer in range(n_layers):
        print(f" {'L'+str(layer)+'pre':>8} {'L'+str(layer)+'post':>8}", end="")
    print()
    print("   " + "-" * (30 + n_layers * 18))

    for pos in range(min(L0, len(token_strs_0), 25)):  # first 25 tokens
        tok = token_strs_0[pos][:10] if pos < len(token_strs_0) else "?"
        nl = t0.get("newline_pos")
        ptype = "eng" if nl and pos < nl else ("↵" if nl and pos == nl else "λ")
        print(f"   {pos:>3} {tok:>10} {ptype:>7} |", end="")
        for layer in range(n_layers):
            pre = t0["attn_moire_effect"][layer]["per_pos_pre"][pos] if pos < len(t0["attn_moire_effect"][layer]["per_pos_pre"]) else 0
            post = t0["attn_moire_effect"][layer]["per_pos_post"][pos] if pos < len(t0["attn_moire_effect"][layer]["per_pos_post"]) else 0
            print(f" {pre:>+8.3f} {post:>+8.3f}", end="")
        print()

    # ══════════════════════════════════════════════════════════════════
    # SAVE
    # ══════════════════════════════════════════════════════════════════

    summary = {
        "n_examples": n_ex,
        "composed_pr_chain": [d["pr"] for d in composed_dirs],
        "remaining_pr_chain": [d["pr"] for d in remaining_dirs],
        "forward_moire_summary": {
            f"layer_{l}": {
                "mean_pr_after_attn": float(np.mean([t["forward_moire"][l]["pr_after_attn"] for t in all_traces])),
                "mean_pr_after_ffn": float(np.mean([t["forward_moire"][l]["pr_after_ffn"] for t in all_traces])),
                "mean_align_after_attn": float(np.mean([t["forward_moire"][l]["mean_align_after_attn"] for t in all_traces])),
                "mean_align_after_ffn": float(np.mean([t["forward_moire"][l]["mean_align_after_ffn"] for t in all_traces])),
            }
            for l in range(n_layers)
        },
        "backward_moire_summary": {
            f"layer_{l}": {
                "cumulative_pr": composed_dirs[l + 1]["pr"],
                "mean_alignment": float(np.mean([t["backward_moire"][l]["mean_alignment"] for t in all_traces])),
            }
            for l in range(n_layers)
        },
        "sharpening_summary": {
            f"layer_{l}": {
                "pre_ffn": float(np.mean([t["attn_moire_effect"][l]["pre_ffn_alignment"] for t in all_traces])),
                "post_ffn": float(np.mean([t["attn_moire_effect"][l]["post_ffn_alignment"] for t in all_traces])),
                "delta": float(np.mean([t["attn_moire_effect"][l]["post_ffn_alignment"] for t in all_traces]) -
                               np.mean([t["attn_moire_effect"][l]["pre_ffn_alignment"] for t in all_traces])),
            }
            for l in range(n_layers)
        },
        "english_vs_lambda": {
            "english_mean": float(np.mean(eng_all)) if eng_all else None,
            "lambda_mean": float(np.mean(lam_all)) if lam_all else None,
            "difference": float(diff) if eng_all and lam_all else None,
        },
        "individual_vs_composed": {
            "individual_prs": [float(np.mean([t["individual_pr"][i] for t in all_traces])) for i in range(n_layers)],
            "composed_pr": float(pr_c),
        },
    }

    out_path = results_dir / "summary.json"
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\nResults saved to {out_path}")


if __name__ == "__main__":
    main()
