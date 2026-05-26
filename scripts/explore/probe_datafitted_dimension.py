#!/usr/bin/env python3
"""
Probe: Data-fitted extraction quality vs student dimension.

The algebraic sweep showed the ceiling is 0.74 per-dim — limited by
linearization, not dimension. The data-fitted approach captured 0.97
per-dim in teacher space (session 153) because it captures nonlinear
residuals from actual inference.

This probe:
  Phase 1: Load teacher, capture residuals at zone boundaries with
           4096+ tokens (was 651), fit 5120×5120 transforms, save them.
  Phase 2: Sweep d_student using embedding SVD basis, measure quality.

The answer: at what d_student does the data-fitted plate reach 95%?

Usage:
    # Phase 1 (needs teacher model, ~5 min):
    uv run python scripts/explore/probe_datafitted_dimension.py --capture

    # Phase 2 (fast, no model needed):
    uv run python scripts/explore/probe_datafitted_dimension.py --sweep

License: MIT
"""

from __future__ import annotations

import sys
import time
import json
import argparse
from pathlib import Path

import numpy as np

TEACHER_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"
D_MODEL = 5120

CACHE_DIR = Path("results/datafitted-dimension-sweep")

# Use more tokens than session 153's 651
TARGET_TOKENS = 4096


def load_model():
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"\n  Loading Qwen3.6-27B...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(
        "Qwen/Qwen3.6-27B", trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        "Qwen/Qwen3.6-27B", torch_dtype=torch.bfloat16,
        device_map="mps", trust_remote_code=True,
        attn_implementation="eager",
    )
    model.eval()
    print(f"  Loaded in {time.time()-t0:.1f}s", flush=True)
    return model, tokenizer


def get_layers(model):
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'layers'):
            return lm.model.layers
    if hasattr(model, 'model') and hasattr(model.model, 'layers'):
        return model.model.layers
    raise ValueError("Cannot find layers")


def get_embed(model):
    if hasattr(model, 'model') and hasattr(model.model, 'language_model'):
        lm = model.model.language_model
        if hasattr(lm, 'model') and hasattr(lm.model, 'embed_tokens'):
            return lm.model.embed_tokens
    if hasattr(model, 'model') and hasattr(model.model, 'embed_tokens'):
        return model.model.embed_tokens
    return None


def capture_boundaries(model, tokenizer, text, boundary_layers=[15, 47, 63]):
    """Capture residuals at zone boundaries."""
    import torch
    layers = get_layers(model)
    residuals = {}
    hooks = []

    embed = get_embed(model)
    if embed is not None:
        def eh(m, a, o):
            h = o[0] if isinstance(o, tuple) else o
            residuals["embed"] = h[0].detach().cpu().float().numpy()
        hooks.append(embed.register_forward_hook(eh))

    for idx in boundary_layers:
        def make_hook(li):
            def hf(m, a, o):
                h = o[0] if isinstance(o, tuple) else o
                residuals[f"L{li}"] = h[0].detach().cpu().float().numpy()
            return hf
        hooks.append(layers[idx].register_forward_hook(make_hook(idx)))

    try:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=512)
        device = next(model.parameters()).device
        inputs = {k: v.to(device) for k, v in inputs.items()}
        with torch.no_grad():
            model(**inputs, output_attentions=False)
    finally:
        for h in hooks:
            h.remove()

    return residuals


def get_diverse_texts():
    """Diverse texts — need many more tokens than session 153's 651."""
    texts = [
        "The quick brown fox jumps over the lazy dog while the cat watches from the window ledge above.",
        "In 1969, Neil Armstrong became the first human to walk on the Moon during the Apollo 11 mission.",
        "To compute the derivative of f(x) = x^3, we apply the power rule: f'(x) = 3x^2.",
        "The president announced sweeping reforms to the healthcare system that would affect millions.",
        "She walked down the empty street, her footsteps echoing off the old brick buildings on either side.",
        "Lambda calculus provides a formal system for expressing computation through function abstraction and application.",
        "The recipe calls for two cups of flour, one cup of sugar, three eggs, and a tablespoon of vanilla extract.",
        "According to general relativity, massive objects curve spacetime, causing what we perceive as gravitational attraction.",
        "The stock market rallied today as investors responded positively to the Federal Reserve's announcement on interest rates.",
        "He picked up the phone and dialed the number, hoping she would answer before the machine kicked in.",
        "The transformer architecture, introduced in 2017, revolutionized natural language processing through self-attention mechanisms.",
        "The garden was full of roses and lilies, their sweet fragrance filling the warm summer air as bees buzzed between blooms.",
        "If we define a function f that maps each element to its successor, then f(f(x)) gives the second successor of x.",
        "The committee voted unanimously to approve the budget proposal, marking the first time in a decade they reached consensus.",
        "Water boils at 100 degrees Celsius at standard atmospheric pressure, transitioning from liquid to gaseous state.",
        "The old man sat on the bench, feeding pigeons and watching the children play in the park across the street.",
        "In category theory, a functor is a mapping between categories that preserves their structure and composition laws.",
        "The company reported quarterly earnings that exceeded analyst expectations by fifteen percent, sending shares higher.",
        "She opened the book to chapter seven, where the protagonist finally discovers the truth about her family's past.",
        "The algorithm runs in O(n log n) time for the average case, making it suitable for large-scale data processing.",
        "The city council debated the new zoning regulations for three hours before tabling the motion until next week.",
        "Photosynthesis converts carbon dioxide and water into glucose and oxygen using energy from sunlight absorbed by chlorophyll.",
        "He stared at the chessboard, considering his options carefully before moving his knight to threaten the opponent's queen.",
        "The Fourier transform decomposes a function into its constituent frequencies, revealing periodic patterns in the signal.",
        "Heavy rain is expected throughout the weekend, with potential flooding in low-lying areas near the river basin.",
        "The museum's new exhibition features works from the Impressionist period, including several rarely displayed Monet paintings.",
        "Every continuous function on a closed interval attains its maximum and minimum values, by the extreme value theorem.",
        "The startup raised fifty million dollars in Series B funding to expand its artificial intelligence platform globally.",
        "The train pulled into the station twenty minutes late, and the passengers hurried onto the platform in the cold rain.",
        "Quantum entanglement allows two particles to be correlated in ways that cannot be explained by classical physics alone.",
        "The chef carefully plated the dish, arranging the seared scallops atop a bed of risotto with microgreens on the side.",
        "The proof proceeds by induction on the structure of the term, with the base case being variables and constants.",
        # More diverse texts to reach 4096+ tokens
        "The mitochondria, often called the powerhouse of the cell, generates most of the cell's supply of adenosine triphosphate.",
        "During the Renaissance, Florence became a center of art and learning, producing masters like Leonardo da Vinci and Michelangelo.",
        "The Riemann hypothesis, one of the most famous unsolved problems in mathematics, concerns the distribution of prime numbers.",
        "She adjusted the telescope and pointed it toward the constellation Orion, visible clearly in the cold winter sky.",
        "In distributed systems, the CAP theorem states that a system cannot simultaneously guarantee consistency, availability, and partition tolerance.",
        "The ancient Romans built an extensive network of roads spanning over fifty thousand miles, connecting every corner of their empire.",
        "A recursive function calls itself with a modified argument, reducing the problem size until it reaches a base case.",
        "The jazz quartet played late into the night, their improvisations weaving through complex chord changes and rhythmic variations.",
        "Entropy in thermodynamics measures the degree of disorder in a system, always increasing in isolated systems according to the second law.",
        "The archaeological team discovered pottery shards dating back three thousand years, providing evidence of early agricultural settlement.",
        "Machine learning models trained on large datasets can exhibit emergent capabilities not present in smaller versions of the same architecture.",
        "The river wound through the valley, its banks lined with willows whose branches trailed in the slow-moving current.",
        "Gödel's incompleteness theorems demonstrate that any sufficiently powerful formal system contains true statements that cannot be proved within it.",
        "The surgeon carefully made the incision, guided by the fluoroscopic image displayed on the monitor above the operating table.",
        "In functional programming, higher-order functions accept other functions as arguments or return them, enabling powerful abstraction patterns.",
        "The volcanic eruption sent a column of ash twelve kilometers into the atmosphere, disrupting air travel across three continents.",
        "Bitcoin's proof-of-work consensus mechanism requires miners to solve computationally expensive puzzles to validate transactions and create new blocks.",
        "The philosopher argued that consciousness cannot be reduced to purely physical processes, proposing instead a dual-aspect theory of mind.",
        "She carefully measured the reagents, knowing that even a slight deviation in concentration could invalidate the entire experiment.",
        "The Navier-Stokes equations describe the motion of viscous fluid substances, and proving their smoothness remains an open millennium problem.",
        "The orchestra tuned to the oboe's A, the concert hall falling silent before the conductor raised the baton for the overture.",
        "Deep reinforcement learning combines neural networks with reward-based optimization, enabling agents to master complex games and robotic control tasks.",
        "The lighthouse keeper climbed the spiral staircase each evening to light the lamp, its beam visible twenty nautical miles out to sea.",
        "Compiler optimization passes transform intermediate representations to produce faster or smaller code without changing the program's observable behavior.",
        "The drought lasted three consecutive years, depleting reservoirs and forcing mandatory water rationing across the entire southern region.",
        "A monad in Haskell encapsulates computations as composable actions, allowing side effects to be managed within a purely functional framework.",
        "The detective examined the crime scene methodically, photographing each piece of evidence before placing it in a labeled collection bag.",
        "Gravitational waves, first detected in 2015 by LIGO, are ripples in spacetime caused by the acceleration of massive objects.",
        "The bakery opened at five each morning, the smell of fresh bread and pastries drawing customers from blocks away.",
        "Attention mechanisms in neural networks allow models to dynamically focus on relevant parts of the input when producing each output element.",
        "The glacier had retreated nearly two kilometers in the past decade, exposing rock formations unseen for thousands of years.",
        "Type theory provides a formal framework for classifying expressions by the kind of value they compute, preventing certain classes of errors.",
        "The market crash of 2008 was triggered by the collapse of mortgage-backed securities, leading to a global recession lasting several years.",
        "He navigated the sailboat through the narrow strait, the wind shifting unpredictably between the steep cliffs on either side.",
        "Topological data analysis uses persistent homology to identify structural features in high-dimensional datasets that survive across multiple scales.",
    ]
    return texts


def phase1_capture():
    """Load teacher, capture residuals, fit transforms, save to disk."""
    import torch

    print(f"\n{'='*80}")
    print(f"  Phase 1: Data-Fitted Transform Capture")
    print(f"  Target: {TARGET_TOKENS} tokens")
    print(f"{'='*80}")

    model, tokenizer = load_model()
    texts = get_diverse_texts()

    print(f"\n  Collecting residuals from {len(texts)} texts...", flush=True)

    all_embed, all_L15, all_L47, all_L63 = [], [], [], []
    total_tokens = 0

    for i, text in enumerate(texts):
        residuals = capture_boundaries(model, tokenizer, text)
        embed = residuals.get("embed")
        l15 = residuals.get("L15")
        l47 = residuals.get("L47")
        l63 = residuals.get("L63")

        if all(x is not None for x in [embed, l15, l47, l63]):
            all_embed.append(embed[1:])   # skip pos 0 (attention sink)
            all_L15.append(l15[1:])
            all_L47.append(l47[1:])
            all_L63.append(l63[1:])
            total_tokens += embed.shape[0] - 1

        if (i + 1) % 8 == 0:
            print(f"    {i+1}/{len(texts)}: {total_tokens} tokens", flush=True)

        if total_tokens >= TARGET_TOKENS:
            break

    X_embed = np.concatenate(all_embed, axis=0)[:TARGET_TOKENS]
    Y_L15 = np.concatenate(all_L15, axis=0)[:TARGET_TOKENS]
    Y_L47 = np.concatenate(all_L47, axis=0)[:TARGET_TOKENS]
    Y_L63 = np.concatenate(all_L63, axis=0)[:TARGET_TOKENS]

    n_tok = X_embed.shape[0]
    print(f"\n  Collected {n_tok} tokens, d={X_embed.shape[1]}")

    # Free model
    del model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # Fit transforms (teacher space: 5120×5120)
    print(f"\n  Fitting zone transforms...", flush=True)
    t0 = time.time()

    def fit(X, Y, label):
        T_t, res, rank, sv = np.linalg.lstsq(X, Y, rcond=None)
        T = T_t.T  # (d_out, d_in)
        # R² = 1 - residual / total_var
        y_pred = X @ T_t
        ss_res = np.sum((Y - y_pred) ** 2)
        ss_tot = np.sum((Y - Y.mean(axis=0)) ** 2)
        r2 = 1 - ss_res / ss_tot
        print(f"    {label}: shape={T.shape}, R²={r2:.6f}, lstsq_rank={rank}")
        return T, r2

    T_A, r2_A = fit(X_embed, Y_L15, "Zone A (embed→L15)")
    T_B, r2_B = fit(Y_L15, Y_L47, "Zone B (L15→L47)")
    T_C, r2_C = fit(Y_L47, Y_L63, "Zone C (L47→L63)")
    T_full, r2_full = fit(X_embed, Y_L63, "Full (embed→L63)")

    print(f"  Fitted in {time.time()-t0:.1f}s")

    # SVD analysis in teacher space
    for label, T in [("Zone A", T_A), ("Zone B", T_B), ("Zone C", T_C), ("Full", T_full)]:
        _, S, _ = np.linalg.svd(T, full_matrices=False)
        cum = np.cumsum(S**2) / np.sum(S**2)
        rank90 = int(np.searchsorted(cum, 0.90)) + 1
        rank95 = int(np.searchsorted(cum, 0.95)) + 1
        rank99 = int(np.searchsorted(cum, 0.99)) + 1
        print(f"    {label}: rank90={rank90}, rank95={rank95}, rank99={rank99}, "
              f"σ₁={S[0]:.4f}, σ₁/σ₂={S[0]/S[1]:.2f}")

    # Teacher-space ternary quality
    print(f"\n  Teacher-space ternary quality (sign+gamma):", flush=True)
    for label, T in [("Zone A", T_A), ("Zone B", T_B), ("Zone C", T_C), ("Full", T_full)]:
        signs = np.sign(T).astype(np.float32)
        gamma = np.mean(np.abs(T), axis=1)
        x_test = np.random.randn(500, T.shape[1]).astype(np.float32)
        y_full = x_test @ T.T
        y_tern = (x_test @ signs.T) * gamma[None, :]
        pd = []
        for d in range(T.shape[0]):
            if y_full[:, d].std() > 1e-10:
                c = np.corrcoef(y_full[:, d], y_tern[:, d])[0, 1]
                if not np.isnan(c):
                    pd.append(c)
        gc = np.corrcoef(y_full.flatten(), y_tern.flatten())[0, 1]
        print(f"    {label}: per_dim={np.mean(pd):.4f}, global={gc:.4f}")

    # Save
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    np.savez_compressed(
        str(CACHE_DIR / "teacher_transforms.npz"),
        T_A=T_A, T_B=T_B, T_C=T_C, T_full=T_full,
    )

    meta = {
        "n_tokens": int(n_tok),
        "d_model": D_MODEL,
        "r2": {"zone_a": float(r2_A), "zone_b": float(r2_B),
               "zone_c": float(r2_C), "full": float(r2_full)},
        "boundaries": {"embed": -1, "L15": 15, "L47": 47, "L63": 63},
    }
    with open(CACHE_DIR / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    print(f"\n  Saved teacher-space transforms to {CACHE_DIR}/")
    return T_full


def phase2_sweep(T_full=None):
    """Load saved transform, sweep d_student."""
    print(f"\n{'='*80}")
    print(f"  Phase 2: Dimension Sweep (Data-Fitted)")
    print(f"{'='*80}")

    if T_full is None:
        cache = CACHE_DIR / "teacher_transforms.npz"
        if not cache.exists():
            print(f"  ERROR: {cache} not found. Run --capture first.")
            sys.exit(1)
        print(f"\n  Loading cached transforms from {cache}...", flush=True)
        data = np.load(str(cache))
        T_full = data["T_full"]
        T_A = data["T_A"]
        T_B = data["T_B"]
        T_C = data["T_C"]
    else:
        T_A = T_B = T_C = None

    np.random.seed(42)
    t0 = time.time()

    # Full SVD
    print(f"  Computing SVD of T_full ({T_full.shape})...", flush=True)
    U_T, S_T, Vt_T = np.linalg.svd(T_full, full_matrices=False)

    total_energy = np.sum(S_T**2)
    cum_energy = np.cumsum(S_T**2) / total_energy

    rank_thresholds = {}
    print(f"\n  Singular value spectrum of data-fitted transform:")
    for thr in [0.50, 0.70, 0.80, 0.85, 0.90, 0.95, 0.99, 0.999]:
        rank = int(np.searchsorted(cum_energy, thr)) + 1
        rank_thresholds[f"rank{int(thr*100)}"] = rank
        print(f"    rank{int(thr*100):3d}: {rank:4d} dims")

    print(f"\n  Top 30 singular values:")
    for i in range(0, 30, 5):
        vals = [f"{S_T[j]:.4f}" for j in range(i, min(i+5, len(S_T)))]
        print(f"    [{i:3d}-{min(i+4,len(S_T)-1):3d}]: {', '.join(vals)}")

    # Embedding SVD basis
    print(f"\n  Computing embedding SVD basis...", flush=True)
    from sklearn.utils.extmath import randomized_svd
    from safetensors import safe_open
    idx = json.load(open(TEACHER_PATH / "model.safetensors.index.json"))
    emb_name = "model.language_model.embed_tokens.weight"
    fname = idx["weight_map"][emb_name]
    with safe_open(str(TEACHER_PATH / fname), framework="pt") as sf:
        E = sf.get_tensor(emb_name).float().numpy()
    _, _, Vt_emb = randomized_svd(E, n_components=D_MODEL, random_state=42)
    V_full = Vt_emb.T  # (5120, 5120)

    # Teacher-space ceiling
    signs_t = np.sign(T_full).astype(np.float32)
    gamma_t = np.mean(np.abs(T_full), axis=1)
    x_test = np.random.randn(500, D_MODEL).astype(np.float32)
    y_t_full = x_test @ T_full.T
    y_t_tern = (x_test @ signs_t.T) * gamma_t[None, :]
    t_pd = []
    for d in range(D_MODEL):
        if y_t_full[:, d].std() > 1e-10:
            c = np.corrcoef(y_t_full[:, d], y_t_tern[:, d])[0, 1]
            if not np.isnan(c):
                t_pd.append(c)
    teacher_per_dim = float(np.mean(t_pd))
    teacher_global = float(np.corrcoef(y_t_full.flatten(), y_t_tern.flatten())[0, 1])
    print(f"\n  Teacher space (d=5120): per_dim={teacher_per_dim:.4f}, global={teacher_global:.4f}")

    # Sweep
    d_values = sorted(set([
        8, 16, 24, 27, 32, 48, 64, 96, 128,
        160, 192, 256, 320, 384, 448, 512,
        640, 768, 896, 1024, 1280,
        1536, 1792, 2048,
        2560, 3072, 3584, 4096,
        4608, 5120,
    ]))
    d_values = [d for d in d_values if d <= V_full.shape[1]]

    results = []

    for d in d_values:
        V_proj = V_full[:, :d]
        T_s = V_proj.T @ T_full @ V_proj

        signs = np.sign(T_s).astype(np.float32)
        gamma = np.mean(np.abs(T_s), axis=1)

        n_test = 500
        x_s = np.random.randn(n_test, d).astype(np.float32)
        y_full = x_s @ T_s.T
        y_tern = (x_s @ signs.T) * gamma[None, :]

        global_corr = float(np.corrcoef(y_full.flatten(), y_tern.flatten())[0, 1])

        per_dim = []
        for dim in range(d):
            if y_full[:, dim].std() > 1e-10:
                c = np.corrcoef(y_full[:, dim], y_tern[:, dim])[0, 1]
                if not np.isnan(c):
                    per_dim.append(c)
        mean_per_dim = float(np.mean(per_dim)) if per_dim else 0.0

        # Cosine sim
        y_fn = y_full / (np.linalg.norm(y_full, axis=1, keepdims=True) + 1e-10)
        y_tn = y_tern / (np.linalg.norm(y_tern, axis=1, keepdims=True) + 1e-10)
        cos_sim = float(np.mean(np.sum(y_fn * y_tn, axis=1)))

        # E2E
        x_t = np.random.randn(n_test, D_MODEL).astype(np.float32)
        y_t = x_t @ T_full.T
        y_t_proj = y_t @ V_proj
        x_s_from_t = x_t @ V_proj
        y_tern_e2e = (x_s_from_t @ signs.T) * gamma[None, :]
        e2e_pd = []
        for dim in range(d):
            if y_t_proj[:, dim].std() > 1e-10 and y_tern_e2e[:, dim].std() > 1e-10:
                c = np.corrcoef(y_t_proj[:, dim], y_tern_e2e[:, dim])[0, 1]
                if not np.isnan(c):
                    e2e_pd.append(c)
        mean_e2e = float(np.mean(e2e_pd)) if e2e_pd else 0.0

        sv_energy = float(cum_energy[min(d-1, len(cum_energy)-1)])

        # Student transform rank
        _, S_s, _ = np.linalg.svd(T_s, full_matrices=False)
        cum_s = np.cumsum(S_s**2) / (np.sum(S_s**2) + 1e-10)
        rank90_s = int(np.searchsorted(cum_s, 0.90)) + 1

        result = {
            "d_student": d,
            "per_dim_corr": mean_per_dim,
            "global_corr": global_corr,
            "cosine_sim": cos_sim,
            "e2e_per_dim": mean_e2e,
            "sv_energy_top_d": sv_energy,
            "rank90_student": rank90_s,
            "ternary_positions": d * d,
            "plate_size_mb": (d * d) / (8 * 1024 * 1024),
        }
        results.append(result)

        print(f"    d={d:5d}: per_dim={mean_per_dim:.4f}  e2e={mean_e2e:.4f}  "
              f"sv={sv_energy:.4f}  rank90={rank90_s:3d}  "
              f"plate={d*d/1e6:.1f}M ({d*d/(8*1024*1024):.2f}MB)",
              flush=True)

    # Optimal basis (T's own SVD)
    print(f"\n  Optimal projection basis (T_full's own SVD)...", flush=True)
    optimal_results = []
    for d in [27, 48, 64, 128, 256, 512, 1024, 1280, 2048, 3072, 4096, 5120]:
        if d > D_MODEL:
            continue
        V_opt = Vt_T[:d, :].T

        T_opt = V_opt.T @ T_full @ V_opt
        signs_o = np.sign(T_opt).astype(np.float32)
        gamma_o = np.mean(np.abs(T_opt), axis=1)

        x_o = np.random.randn(500, d).astype(np.float32)
        y_o_full = x_o @ T_opt.T
        y_o_tern = (x_o @ signs_o.T) * gamma_o[None, :]

        pd = []
        for dim in range(d):
            if y_o_full[:, dim].std() > 1e-10:
                c = np.corrcoef(y_o_full[:, dim], y_o_tern[:, dim])[0, 1]
                if not np.isnan(c):
                    pd.append(c)
        mpd = float(np.mean(pd)) if pd else 0.0
        gc = float(np.corrcoef(y_o_full.flatten(), y_o_tern.flatten())[0, 1])

        optimal_results.append({
            "d": d, "per_dim_corr": mpd, "global_corr": gc,
            "sv_energy": float(cum_energy[min(d-1, len(cum_energy)-1)]),
        })
        print(f"    d={d:5d}: per_dim={mpd:.4f}  global={gc:.4f}  "
              f"sv={cum_energy[min(d-1,len(cum_energy)-1)]:.4f}",
              flush=True)

    # Find crossings
    target_90 = next((r for r in results if r['per_dim_corr'] >= 0.90), None)
    target_95 = next((r for r in results if r['per_dim_corr'] >= 0.95), None)
    target_90_opt = next((r for r in optimal_results if r['per_dim_corr'] >= 0.90), None)
    target_95_opt = next((r for r in optimal_results if r['per_dim_corr'] >= 0.95), None)

    # Print table
    print(f"\n{'='*80}")
    print(f"  RESULTS: Data-Fitted Extraction Quality vs Dimension")
    print(f"{'='*80}")

    print(f"\n  Embedding SVD basis:")
    print(f"  {'d':>6s} | {'per_dim':>8s} | {'e2e':>8s} | {'global':>8s} | {'cos':>8s} | {'sv_energy':>10s} | {'positions':>12s} | {'MB':>8s}")
    print(f"  {'-'*6} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*8} | {'-'*10} | {'-'*12} | {'-'*8}")

    for r in results:
        flag = ""
        if target_90 and r['d_student'] == target_90['d_student'] and target_90 != target_95:
            flag = " ← 90%"
        if target_95 and r['d_student'] == target_95['d_student']:
            flag = " ← 95%"
        if r['d_student'] == 1280:
            flag = flag or " ← current"

        print(f"  {r['d_student']:>6d} | {r['per_dim_corr']:>8.4f} | {r['e2e_per_dim']:>8.4f} | "
              f"{r['global_corr']:>8.4f} | {r['cosine_sim']:>8.4f} | "
              f"{r['sv_energy_top_d']:>10.6f} | {r['ternary_positions']:>12,} | "
              f"{r['plate_size_mb']:>8.2f}{flag}")

    print(f"\n  Optimal basis (T's own SVD):")
    print(f"  {'d':>6s} | {'per_dim':>8s} | {'global':>8s} | {'sv_energy':>10s}")
    print(f"  {'-'*6} | {'-'*8} | {'-'*8} | {'-'*10}")
    for r in optimal_results:
        flag = ""
        if target_95_opt and r['d'] == target_95_opt['d']:
            flag = " ← 95%"
        if target_90_opt and r['d'] == target_90_opt['d'] and target_90_opt != target_95_opt:
            flag = " ← 90%"
        print(f"  {r['d']:>6d} | {r['per_dim_corr']:>8.4f} | {r['global_corr']:>8.4f} | "
              f"{r['sv_energy']:>10.6f}{flag}")

    print(f"\n  Teacher space (d=5120): per_dim={teacher_per_dim:.4f}")

    print(f"\n{'='*80}")
    print(f"  KEY FINDINGS")
    print(f"{'='*80}")

    if target_90:
        print(f"\n  90% per-dim: d={target_90['d_student']} ({target_90['ternary_positions']:,} positions, {target_90['plate_size_mb']:.2f} MB)")
    if target_95:
        current = next(r for r in results if r['d_student'] == 1280)
        print(f"\n  95% per-dim: d={target_95['d_student']} ({target_95['ternary_positions']:,} positions, {target_95['plate_size_mb']:.2f} MB)")
        print(f"    vs current d=1280 ({current['per_dim_corr']:.4f}):")
        print(f"    d increase: {target_95['d_student']/1280:.1f}×")
        print(f"    position increase: {target_95['ternary_positions']/current['ternary_positions']:.1f}×")
    else:
        print(f"\n  95% per-dim NOT reached with embedding basis!")
        print(f"  Teacher ceiling: {teacher_per_dim:.4f}")
        if teacher_per_dim < 0.95:
            print(f"  ⚠ Ceiling ({teacher_per_dim:.4f}) < 95%: gap is sign+gamma, not dimension")
        else:
            print(f"  ✓ Ceiling ({teacher_per_dim:.4f}) ≥ 95%: reachable with right basis or larger d")

    if target_95_opt:
        print(f"\n  With OPTIMAL basis: 95% at d={target_95_opt['d']}")
    elif optimal_results:
        best = max(optimal_results, key=lambda r: r['per_dim_corr'])
        print(f"\n  With OPTIMAL basis: best={best['per_dim_corr']:.4f} at d={best['d']}")

    # Compare algebraic vs data-fitted at d=1280
    print(f"\n  Comparison at d=1280:")
    current = next((r for r in results if r['d_student'] == 1280), None)
    if current:
        print(f"    Data-fitted: per_dim={current['per_dim_corr']:.4f}")
    print(f"    Algebraic:   per_dim=0.7439 (from prior sweep)")
    print(f"    Session 153: per_dim=0.76-0.79 (651 tokens)")

    # Save
    output = {
        "teacher_per_dim": teacher_per_dim,
        "teacher_global": teacher_global,
        "n_tokens_fitted": TARGET_TOKENS,
        "singular_values_top100": S_T[:100].tolist(),
        "rank_thresholds": rank_thresholds,
        "embedding_basis_sweep": results,
        "optimal_basis_sweep": optimal_results,
        "target_90_emb": target_90,
        "target_95_emb": target_95,
        "target_90_opt": target_90_opt,
        "target_95_opt": target_95_opt,
    }

    with open(CACHE_DIR / "results.json", "w") as f:
        json.dump(output, f, indent=2,
                  default=lambda x: float(x) if isinstance(x, (np.floating, np.integer)) else x)

    print(f"\n  Saved to {CACHE_DIR}/results.json")
    print(f"  Phase 2 took {time.time()-t0:.0f}s")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--capture", action="store_true", help="Phase 1: capture residuals + fit transforms")
    parser.add_argument("--sweep", action="store_true", help="Phase 2: sweep dimensions")
    args = parser.parse_args()

    if not args.capture and not args.sweep:
        args.capture = True
        args.sweep = True

    T_full = None
    if args.capture:
        T_full = phase1_capture()
    if args.sweep:
        phase2_sweep(T_full)


if __name__ == "__main__":
    main()
