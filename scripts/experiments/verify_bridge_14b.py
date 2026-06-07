#!/usr/bin/env python3
"""
Verify Bridge Nodes — Qwen3-14B
================================

The crystal is a forest of 3 trees cross-connected by bridge nodes W and Y.
This script verifies on Qwen3-14B that:
  1. The gate_proj cosine matrix reproduces the crystal topology
  2. WHNF is maximally isolated (Tree 0)
  3. K,I cluster together and separate from B,C,D (Tree 1)
  4. W sits BETWEEN selection and composition clusters (bridge)
  5. Y's neighbor ordering matches the crystal

Method: differential gate activations (probe - null baseline) at Zone B.
Uses Qwen3-14B for best crystal resolution.
"""

import json
import os
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from scipy.stats import spearmanr

PHI = (1 + np.sqrt(5)) / 2

NAMES = ['K', 'I', 'B', 'C', 'D', 'Y', 'W', 'WHNF']

M8_crystal = np.array([
    [+1.0000, +0.7865, +0.1948, +0.2265, +0.3232, +0.1768, +0.5360, -0.1862],
    [+0.7865, +1.0000, +0.2479, +0.2511, +0.3463, +0.1739, +0.3781, -0.2448],
    [+0.1948, +0.2479, +1.0000, +0.8878, +0.8937, +0.6623, +0.6851, -0.1227],
    [+0.2265, +0.2511, +0.8878, +1.0000, +0.8316, +0.7200, +0.7318, -0.1027],
    [+0.3232, +0.3463, +0.8937, +0.8316, +1.0000, +0.6798, +0.8064, -0.1729],
    [+0.1768, +0.1739, +0.6623, +0.7200, +0.6798, +1.0000, +0.5653, -0.0840],
    [+0.5360, +0.3781, +0.6851, +0.7318, +0.8064, +0.5653, +1.0000, -0.1379],
    [-0.1862, -0.2448, -0.1227, -0.1027, -0.1729, -0.0840, -0.1379, +1.0000],
], dtype=np.float64)

# Crystal eigenvectors (the tree axes)
_ev, _evec = np.linalg.eigh(M8_crystal)
_idx = np.argsort(_ev)[::-1]
CRYSTAL_EIGVALS = _ev[_idx]
CRYSTAL_EIGVECS = _evec[:, _idx]


# ═══════════════════════════════════════════════════════════════
# Probes — 15 per type for better averaging
# ═══════════════════════════════════════════════════════════════

NULL_TEXTS = [
    "The quick brown fox jumps over the lazy dog.",
    "In the year 2024, technology continues to advance rapidly.",
    "She walked through the park on a sunny afternoon.",
    "The committee decided to postpone the vote until next week.",
    "Water boils at 100 degrees Celsius at sea level.",
    "The weather forecast predicts rain for tomorrow morning.",
    "A balanced diet includes fruits, vegetables, and whole grains.",
    "The library closes at nine on weekday evenings.",
    "Traffic was heavy on the highway during rush hour.",
    "The cat sat on the mat and watched the birds outside.",
]

PROBES = {
    'K': [
        "If it rains, take the umbrella; otherwise, take the",
        "Given A and B, the result is just",
        "She chose the red one and ignored the",
        "Between coffee and tea, he always picks",
        "The function returns the first argument and discards the",
        "Of the left and right paths, we take the",
        "The winning team was the first to score a",
        "He kept the diamond and threw away the",
        "Select the primary option: A over B means",
        "The filter keeps matching elements and drops",
        "Pick one and discard the other which is",
        "The if-then branch takes the first path and skips",
        "Only the first value matters, the rest are",
        "The selector outputs A and suppresses",
        "Take the head of the list and ignore the",
    ],
    'I': [
        "The value passes through unchanged as",
        "The identity function returns its input which is",
        "She repeated exactly what he said word for",
        "The mirror shows exactly what stands before",
        "Copy the input directly to the output to get",
        "The transparent proxy forwards the request without",
        "Echo back the same message that was",
        "The relay passes the signal unchanged through the",
        "Return the argument as-is with no",
        "What goes in must come out exactly the",
        "The passthrough channel preserves the signal as",
        "A no-op instruction leaves the state exactly",
        "The identity matrix multiplied by any vector gives",
        "The buffer holds the value and outputs it",
        "Copying x to y means y equals",
    ],
    'B': [
        "First wash, then dry, then fold the",
        "Apply f to the result of g applied to",
        "The pipeline processes data through multiple stages of",
        "Compose the two transformations into a single",
        "The outer function wraps the inner function's",
        "Chain the operations: first filter, then map, then",
        "The composition of rotation and translation gives a",
        "After encoding, then encrypting, the message becomes",
        "Nested function calls: f(g(x)) where x is",
        "The combined effect of both transformations is",
        "First parse the input, then analyze the",
        "Apply the color filter after the brightness adjustment to",
        "The composite function first squares then takes the root of",
        "Pipe the output of grep into sort to get",
        "Layer the transformations: scale, then rotate, then translate the",
    ],
    'C': [
        "Instead of f(x)(y), compute f(y)(x) which gives",
        "Flip the argument order so the second comes",
        "The passive voice reverses subject and object in the",
        "Swap the two parameters before calling the",
        "Rather than applying to A then B, apply to B then",
        "The inverse operation reverses the order of",
        "Reorder the arguments so the receiver becomes the",
        "Exchange the positions of the first and second",
        "The commutative law says we can swap",
        "Transpose the matrix to flip rows and",
        "Reverse the direction of the arrows in the",
        "The converse of 'A implies B' is 'B implies",
        "Switch the subject and predicate to get",
        "The mirror image swaps left and",
        "Invert the order of application: instead of giving x then y, give y then",
    ],
    'D': [
        "Compose f with g, then compose the result with h to get",
        "The double composition applies three functions in",
        "Deeply nested: f(g(h(x))) processes x through three",
        "The pipeline has three stages of",
        "Triple function composition: first h, then g, then f applied to",
        "The deeply composed transformation chains three",
        "After three successive operations, the data becomes",
        "Each layer transforms the output of the previous",
        "The deeply nested call evaluates from inside",
        "Three composed functions form a single composite",
        "Apply f after g after h to get",
        "Multi-stage processing: encode, compress, then encrypt the",
        "The nested pipeline has an inner and outer composition of",
        "Compose twice: first pair f∘g, then compose with h to get",
        "Three sequential transformations reduce to one composite",
    ],
    'Y': [
        "A folder contains files and other folders which contain",
        "She told a story about a girl who told a story about",
        "The dream was about having a dream which was about having a dream",
        "He opened a box inside a box inside a box inside",
        "The mirror reflected the mirror which reflected the",
        "The function calls itself with a smaller input until it reaches",
        "Each level of recursion creates another level of",
        "The fractal pattern repeats at every scale of",
        "The recursive definition refers back to itself in the",
        "To compute factorial of n, multiply n by factorial of",
        "The self-referential sentence describes itself as being",
        "The loop iterates over elements, processing each one and then",
        "Fibonacci numbers are defined as the sum of the two previous",
        "The tree structure branches and each branch further branches into",
        "The definition is circular: A is defined in terms of",
    ],
    'W': [
        "The dog bit itself on the",
        "She taught herself to play the",
        "The robot programmed itself to perform",
        "He convinced himself that everything would",
        "The system tested itself and found",
        "The compiler compiles itself to produce",
        "She found herself lost in the",
        "The program modifies itself during",
        "He argued with himself about the",
        "The AI trained itself on its own",
        "The snake ate itself starting from the",
        "The machine calibrates itself before each",
        "She surprised herself with how well she",
        "The organism repairs itself through",
        "The virus replicates itself by copying its",
    ],
    'WHNF': [
        "The value 42 is fully evaluated as",
        "The constant function always returns the same",
        "No further reduction is needed for the",
        "The normal form of the expression is simply",
        "The computation has terminated with result",
        "The irreducible value cannot be simplified",
        "After all reductions, the final answer is",
        "The base case of the recursion returns",
        "The fully simplified expression equals",
        "The ground term has no variables left to",
        "The literal value seven needs no further",
        "The atom at the bottom of the expression is",
        "The primitive data type stores the raw",
        "The evaluated constant is ready for",
        "The terminal symbol in the grammar is",
    ],
}


def main():
    model_name = "Qwen/Qwen3-14B"

    print("╔" + "═" * 68 + "╗")
    print("║" + "  BRIDGE NODE VERIFICATION — Qwen3-14B".center(68) + "║")
    print("╚" + "═" * 68 + "╝")

    # Load model
    from transformers import AutoModelForCausalLM, AutoTokenizer

    print(f"\n  Loading {model_name}...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(model_name, trust_remote_code=True)
    model = AutoModelForCausalLM.from_pretrained(
        model_name, dtype=torch.float16,
        device_map="auto", trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    d_model = model.config.hidden_size
    dt = time.time() - t0
    print(f"  Loaded in {dt:.1f}s — {n_layers}L × d={d_model}")

    layers = list(model.model.layers)
    device = next(model.parameters()).device

    # Zone B: layers at 35%-65% depth (the compute zone)
    zone_b = list(range(int(n_layers * 0.35), int(n_layers * 0.65) + 1))
    print(f"  Zone B: layers {zone_b[0]}-{zone_b[-1]} ({len(zone_b)} layers)")

    # ── Collect gate activations ──
    def get_mean_gate(texts, label=""):
        """Get mean gate_proj activation per layer across texts."""
        all_acts = {li: [] for li in zone_b}
        for ti, text in enumerate(texts):
            ids = tokenizer(text, return_tensors="pt").input_ids.to(device)
            captures = {}
            hooks = []
            for li in zone_b:
                gate = layers[li].mlp.gate_proj
                def make_hook(l):
                    def hook(m, inp, out):
                        captures[l] = out[0, -1, :].detach().cpu().float().numpy()
                    return hook
                hooks.append(gate.register_forward_hook(make_hook(li)))

            with torch.no_grad():
                _ = model(input_ids=ids)

            for h in hooks:
                h.remove()

            for li in zone_b:
                if li in captures:
                    all_acts[li].append(captures[li])

            if label and (ti + 1) % 5 == 0:
                print(f"    {label}: {ti+1}/{len(texts)} done", flush=True)

        return {li: np.mean(acts, axis=0) for li, acts in all_acts.items() if acts}

    print(f"\n  ── Computing null baseline ({len(NULL_TEXTS)} texts) ──")
    null_mean = get_mean_gate(NULL_TEXTS, "null")

    print(f"\n  ── Computing combinator activations ──")
    diff_acts = {}
    for comb in NAMES:
        texts = PROBES[comb]
        print(f"    {comb} ({len(texts)} probes)...", flush=True)
        mean_act = get_mean_gate(texts)
        diff_acts[comb] = {
            li: mean_act[li] - null_mean[li]
            for li in zone_b
            if li in mean_act and li in null_mean
        }

    # Free model memory
    del model
    torch.cuda.empty_cache() if torch.cuda.is_available() else None
    import gc; gc.collect()

    # ── Build differential cosine matrix ──
    print(f"\n" + "═" * 70)
    print(f"  DIFFERENTIAL COSINE MATRIX")
    print(f"═" * 70)

    # Average across Zone B layers
    avg_diff = {}
    for comb in NAMES:
        vecs = [diff_acts[comb][li] for li in zone_b if li in diff_acts[comb]]
        if vecs:
            avg_diff[comb] = np.mean(vecs, axis=0)

    cos_mat = np.zeros((8, 8))
    for i, ci in enumerate(NAMES):
        for j, cj in enumerate(NAMES):
            vi, vj = avg_diff[ci], avg_diff[cj]
            ni, nj = np.linalg.norm(vi), np.linalg.norm(vj)
            if ni > 1e-10 and nj > 1e-10:
                cos_mat[i, j] = np.dot(vi, vj) / (ni * nj)

    print(f"\n  Observed differential cosine matrix:")
    print("       " + "    ".join(f"{n:>6}" for n in NAMES))
    for i, n in enumerate(NAMES):
        row = "  ".join(f"{cos_mat[i,j]:>+6.3f}" for j in range(8))
        print(f"  {n:>4}: {row}")

    # ── Per-layer analysis ──
    print(f"\n  Per-layer cosine matrices (checking stability):")
    layer_corrs = []
    for li in zone_b:
        layer_diff = {c: diff_acts[c][li] for c in NAMES if li in diff_acts[c]}
        if len(layer_diff) < 8:
            continue
        lcos = np.zeros((8, 8))
        for i, ci in enumerate(NAMES):
            for j, cj in enumerate(NAMES):
                vi, vj = layer_diff[ci], layer_diff[cj]
                ni, nj = np.linalg.norm(vi), np.linalg.norm(vj)
                if ni > 1e-10 and nj > 1e-10:
                    lcos[i, j] = np.dot(vi, vj) / (ni * nj)
        mask = np.triu(np.ones_like(lcos, dtype=bool), k=1)
        corr_crystal = np.corrcoef(lcos[mask], M8_crystal[mask])[0, 1]
        corr_avg = np.corrcoef(lcos[mask], cos_mat[mask])[0, 1]
        layer_corrs.append((li, corr_crystal, corr_avg))
        depth_frac = li / (n_layers - 1)
        print(f"    L{li:02d} (d={depth_frac:.2f}): r_crystal={corr_crystal:+.3f}  r_avg={corr_avg:+.3f}")

    # ── Correlation with crystal ──
    mask = np.triu(np.ones_like(M8_crystal, dtype=bool), k=1)
    pearson_r = np.corrcoef(cos_mat[mask], M8_crystal[mask])[0, 1]
    spearman_rho, spearman_p = spearmanr(cos_mat[mask], M8_crystal[mask])

    print(f"\n  Crystal correlation (avg across Zone B):")
    print(f"    Pearson r:  {pearson_r:.4f}")
    print(f"    Spearman ρ: {spearman_rho:.4f}  (p = {spearman_p:.6f})")

    # ── Eigendecomposition ──
    obs_eigvals, obs_eigvecs = np.linalg.eigh(cos_mat)
    idx = np.argsort(obs_eigvals)[::-1]
    obs_eigvals = obs_eigvals[idx]
    obs_eigvecs = obs_eigvecs[:, idx]

    print(f"\n  Eigenvalues: {['%.4f' % v for v in obs_eigvals]}")

    print(f"\n  Eigenvector sign comparison:")
    print(f"  {'PC':>4}  {'λ_obs':>8}  {'λ_cryst':>8}  {'Observed':>45}  {'Crystal':>45}  {'Match':>5}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*45}  {'─'*45}  {'─'*5}")

    for k in range(min(5, len(obs_eigvals))):
        obs_str = ' '.join(f"{NAMES[i]}{'+'if obs_eigvecs[i,k]>0 else '-'}" for i in range(8))
        cry_str = ' '.join(f"{NAMES[i]}{'+'if CRYSTAL_EIGVECS[i,k]>0 else '-'}" for i in range(8))
        match_n = sum(1 for i in range(8) if (obs_eigvecs[i,k]>0) == (CRYSTAL_EIGVECS[i,k]>0))
        match = max(match_n, 8 - match_n)
        print(f"  PC{k}  {obs_eigvals[k]:>8.4f}  {CRYSTAL_EIGVALS[k]:>8.4f}  {obs_str:>45}  {cry_str:>45}  {match}/8")

    # ── BRIDGE NODE TEST ──
    print(f"\n" + "═" * 70)
    print(f"  BRIDGE NODE TEST")
    print(f"═" * 70)

    print(f"\n  Node positions in eigenspace:")
    print(f"  {'Node':>4}  {'T0':>8}  {'T1':>8}  {'T2':>8}  {'T3':>8}  {'Side T1':>8}  {'Flips?':>7}")
    print(f"  {'─'*4}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*8}  {'─'*7}")
    for i, n in enumerate(NAMES):
        t0 = obs_eigvecs[i, 0]
        t1 = obs_eigvecs[i, 1]
        t2 = obs_eigvecs[i, 2] if len(obs_eigvals) > 2 else 0
        t3 = obs_eigvecs[i, 3] if len(obs_eigvals) > 3 else 0
        side = "SEL" if t1 > 0 else "COMP"
        flips = "YES" if (t1 > 0) != (t3 > 0) else ""
        print(f"  {n:>4}  {t0:>+8.3f}  {t1:>+8.3f}  {t2:>+8.3f}  {t3:>+8.3f}  {side:>8}  {flips:>7}")

    # W's bridge position
    ki_sel = [obs_eigvecs[NAMES.index(c), 1] for c in ['K', 'I']]
    bcd_comp = [obs_eigvecs[NAMES.index(c), 1] for c in ['B', 'C', 'D']]
    ki_mean = np.mean(ki_sel)
    bcd_mean = np.mean(bcd_comp)
    w_val = obs_eigvecs[NAMES.index('W'), 1]
    y_val = obs_eigvecs[NAMES.index('Y'), 1]

    if abs(ki_mean - bcd_mean) > 1e-10:
        w_interp = (w_val - bcd_mean) / (ki_mean - bcd_mean)
        y_interp = (y_val - bcd_mean) / (ki_mean - bcd_mean)
    else:
        w_interp = y_interp = 0.5

    print(f"\n  Bridge interpolation on Tree 1 axis:")
    print(f"    KI centroid:  {ki_mean:+.4f}")
    print(f"    BCD centroid: {bcd_mean:+.4f}")
    print(f"    Separation:   {abs(ki_mean - bcd_mean):.4f}")
    print(f"    W position:   {w_val:+.4f}  ({w_interp:.1%} toward KI)")
    print(f"    Y position:   {y_val:+.4f}  ({y_interp:.1%} toward KI)")
    print(f"    Crystal W:    30% toward KI")

    # ── Rank-based analysis (robust to scale) ──
    print(f"\n" + "═" * 70)
    print(f"  RANK-BASED ANALYSIS")
    print(f"═" * 70)

    print(f"\n  Per-node Spearman rank correlation:")
    for i, name in enumerate(NAMES):
        obs_row = [cos_mat[i, j] for j in range(8) if j != i]
        cry_row = [M8_crystal[i, j] for j in range(8) if j != i]
        rho, p = spearmanr(obs_row, cry_row)
        sig = "***" if p < 0.01 else "**" if p < 0.05 else "*" if p < 0.1 else ""
        print(f"    {name:>4}: ρ = {rho:+.3f}  (p={p:.3f}) {sig}")

    # Nearest neighbor check
    print(f"\n  Nearest neighbors (observed vs crystal):")
    for i, name in enumerate(NAMES):
        obs_nn = sorted([(cos_mat[i,j], NAMES[j]) for j in range(8) if j != i], reverse=True)
        cry_nn = sorted([(M8_crystal[i,j], NAMES[j]) for j in range(8) if j != i], reverse=True)
        obs_top3 = [n for _, n in obs_nn[:3]]
        cry_top3 = [n for _, n in cry_nn[:3]]
        overlap = len(set(obs_top3) & set(cry_top3))
        print(f"    {name:>4}: obs=[{','.join(obs_top3)}]  crystal=[{','.join(cry_top3)}]  overlap={overlap}/3")

    # W's cluster membership
    print(f"\n  W's affinity to each cluster (cosine):")
    w_idx = NAMES.index('W')
    ki_cos = np.mean([cos_mat[w_idx, NAMES.index(c)] for c in ['K', 'I']])
    bcd_cos = np.mean([cos_mat[w_idx, NAMES.index(c)] for c in ['B', 'C', 'D']])
    ki_cos_c = np.mean([M8_crystal[w_idx, NAMES.index(c)] for c in ['K', 'I']])
    bcd_cos_c = np.mean([M8_crystal[w_idx, NAMES.index(c)] for c in ['B', 'C', 'D']])
    print(f"    W↔KI:   obs={ki_cos:.3f}  crystal={ki_cos_c:.3f}")
    print(f"    W↔BCD:  obs={bcd_cos:.3f}  crystal={bcd_cos_c:.3f}")
    print(f"    W closer to KI: obs={'YES' if ki_cos > bcd_cos else 'NO'}  crystal={'YES' if ki_cos_c > bcd_cos_c else 'NO'}")

    # WHNF isolation
    print(f"\n  Node mean similarity to others (isolation test):")
    for i, name in enumerate(NAMES):
        mean_cos = np.mean([cos_mat[i,j] for j in range(8) if j != i])
        mean_cos_c = np.mean([M8_crystal[i,j] for j in range(8) if j != i])
        marker = " ← MOST ISOLATED" if name == 'WHNF' else ""
        print(f"    {name:>4}: obs={mean_cos:.3f}  crystal={mean_cos_c:+.3f}{marker}")

    # ── VERDICT ──
    print(f"\n" + "═" * 70)
    print(f"  VERDICT")
    print(f"═" * 70)

    # Criteria
    whnf_isolated = all(
        np.mean([cos_mat[NAMES.index('WHNF'), j] for j in range(8) if j != NAMES.index('WHNF')])
        < np.mean([cos_mat[i, j] for j in range(8) if j != i])
        for i in range(8) if i != NAMES.index('WHNF')
    )
    y_isolated = all(
        np.mean([cos_mat[NAMES.index('Y'), j] for j in range(8) if j != NAMES.index('Y')])
        < np.mean([cos_mat[i, j] for j in range(8) if j != i])
        for i in range(8) if i not in [NAMES.index('Y'), NAMES.index('WHNF')]
    )
    bd_closest = cos_mat[NAMES.index('B'), NAMES.index('D')] > cos_mat[NAMES.index('B'), NAMES.index('K')]
    ki_close = cos_mat[NAMES.index('K'), NAMES.index('I')] > np.median(cos_mat[mask])

    print(f"\n  Structural tests:")
    print(f"    WHNF most isolated:     {'✅' if whnf_isolated else '❌'}")
    print(f"    Y second most isolated: {'✅' if y_isolated else '❌'}")
    print(f"    B-D closest pair:       {'✅' if bd_closest else '❌'} (cos={cos_mat[NAMES.index('B'), NAMES.index('D')]:.3f})")
    print(f"    K-I close pair:         {'✅' if ki_close else '❌'} (cos={cos_mat[NAMES.index('K'), NAMES.index('I')]:.3f})")
    print(f"    Overall rank corr:      {'✅' if spearman_rho > 0.3 else '❌'} (ρ={spearman_rho:.3f}, p={spearman_p:.4f})")
    print(f"    W bridges clusters:     {'✅' if 0.15 < w_interp < 0.85 else '❌'} (interp={w_interp:.1%})")

    # Save
    out_dir = Path(__file__).parent.parent.parent / 'results' / 'bridge-verification'
    out_dir.mkdir(parents=True, exist_ok=True)

    results = {
        'model': model_name,
        'n_layers': n_layers,
        'zone_b_layers': zone_b,
        'n_probes_per_type': len(PROBES['K']),
        'n_null_texts': len(NULL_TEXTS),
        'differential_cosine_matrix': cos_mat.tolist(),
        'eigvals': obs_eigvals.tolist(),
        'pearson_r': float(pearson_r),
        'spearman_rho': float(spearman_rho),
        'spearman_p': float(spearman_p),
        'w_interpolation': float(w_interp),
        'y_interpolation': float(y_interp),
        'whnf_most_isolated': bool(whnf_isolated),
        'per_layer_crystal_corr': [(li, float(r)) for li, r, _ in layer_corrs],
    }
    with open(out_dir / 'Qwen_Qwen3-14B_results.json', 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n  Results saved to: {out_dir}/Qwen_Qwen3-14B_results.json")


if __name__ == '__main__':
    main()
