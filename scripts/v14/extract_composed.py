#!/usr/bin/env python3
"""
Composed Zone Transform Extraction — Teacher → 3 Ternary Plates.

Extracts the composed linear transform for each zone (A/B/C) from the
teacher model, projects to student space (d=1280), and saves as ternary
plates + per-row gamma scalars.

The result: 3 plates that replace 64 sequential layer evaluations with
3 matrix multiplications.

Protocol:
  1. Load teacher (Qwen3.6-27B)
  2. Run on training data (diverse, many tokens)
  3. Capture residuals at zone boundaries: embed, L15, L47, L63
  4. Fit least-squares linear transforms per zone
  5. Project to student space via SVD basis (V_proj from extraction)
  6. Extract sign(T) → ternary plate, |T| row-wise → gamma
  7. Save as .npz

Usage:
    cd verbum
    uv run python scripts/v14/extract_composed.py

License: MIT
"""

from __future__ import annotations

import sys
import time
import json
from pathlib import Path

import numpy as np
import torch

sys.path.insert(0, str(Path(__file__).parent))

DEVICE = "mps"
DTYPE = torch.bfloat16
MODEL_NAME = "Qwen/Qwen3.6-27B"
TEACHER_PATH = Path.home() / ".cache/huggingface/hub/models--Qwen--Qwen3.6-27B/snapshots/6a9e13bd6fc8f0983b9b99948120bc37f49c13e9"

# How many tokens to use for fitting (more = better transform estimate)
TARGET_TOKENS = 2048
BATCH_TEXTS = 32  # texts to run through teacher


def load_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer
    print(f"\n  Loading {MODEL_NAME}...", flush=True)
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME, trust_remote_code=True)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=DTYPE, device_map=DEVICE,
        trust_remote_code=True, attn_implementation="eager",
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
    raise ValueError(f"Cannot find layers")


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


def get_diverse_texts(n_texts=32):
    """Get diverse texts for transform estimation."""
    # Mix of styles: factual, narrative, technical, conversational
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
    ]
    return texts[:n_texts]


def compute_svd_projection(teacher_path, d_student=1280):
    """Compute V_proj from teacher embeddings (same as extract_qwen36.py)."""
    from safetensors import safe_open

    # Load embedding matrix
    index_path = teacher_path / "model.safetensors.index.json"
    index = json.load(open(index_path))
    emb_name = "model.language_model.embed_tokens.weight"
    shard_name = index["weight_map"][emb_name]
    shard_path = teacher_path / shard_name

    print(f"  Loading embedding for SVD projection basis...", flush=True)
    with safe_open(str(shard_path), framework="pt") as sf:
        E = sf.get_tensor(emb_name).float().numpy()  # (vocab, 5120)

    # Truncated SVD → top d_student right singular vectors
    print(f"  Computing SVD (top {d_student})...", flush=True)
    from sklearn.utils.extmath import randomized_svd
    _, _, Vt = randomized_svd(E, n_components=d_student, random_state=42)
    V_proj = Vt.T  # (5120, 1280) — projects teacher→student space

    print(f"  V_proj: {V_proj.shape}")
    return V_proj


def fit_transform(X, Y):
    """Fit Y ≈ X @ T^T via least squares. Returns T (d_out × d_in)."""
    T_t, _, _, _ = np.linalg.lstsq(X, Y, rcond=None)
    return T_t.T  # (d_out, d_in)


def extract_ternary_plate(T, label):
    """Extract sign(T) + per-row gamma from a transform matrix."""
    signs = np.sign(T).astype(np.int8)  # {-1, 0, +1}
    # Per-row gamma = mean absolute value per row (scale factor)
    gamma = np.mean(np.abs(T), axis=1).astype(np.float32)  # (d_out,)

    # Quality check: correlation of sign(T)@x vs T@x on random inputs
    x_test = np.random.randn(100, T.shape[1]).astype(np.float32)
    y_full = x_test @ T.T
    y_ternary = x_test @ signs.astype(np.float32).T * gamma[None, :]
    corr = np.corrcoef(y_full.flatten(), y_ternary.flatten())[0, 1]

    # Per-dim correlation
    per_dim = []
    for d in range(T.shape[0]):
        if y_full[:, d].std() > 1e-10:
            c = np.corrcoef(y_full[:, d], y_ternary[:, d])[0, 1]
            if not np.isnan(c):
                per_dim.append(c)
    mean_per_dim = np.mean(per_dim) if per_dim else 0.0

    print(f"    {label}: shape={T.shape}, global_corr={corr:.4f}, "
          f"per_dim_corr={mean_per_dim:.4f}, gamma_mean={gamma.mean():.4f}")

    return signs, gamma, {"global_corr": float(corr), "per_dim_corr": float(mean_per_dim)}


def main():
    print(f"\n{'='*80}")
    print(f"  Composed Zone Transform Extraction")
    print(f"  Teacher: {MODEL_NAME}")
    print(f"  Target tokens: {TARGET_TOKENS}")
    print(f"{'='*80}")

    model, tokenizer = load_model()
    texts = get_diverse_texts(BATCH_TEXTS)

    # ── Collect residuals ──
    print(f"\n  Collecting residuals from {len(texts)} texts...", flush=True)

    all_embed = []
    all_L15 = []
    all_L47 = []
    all_L63 = []
    total_tokens = 0

    for i, text in enumerate(texts):
        residuals = capture_boundaries(model, tokenizer, text)

        embed = residuals.get("embed")
        l15 = residuals.get("L15")
        l47 = residuals.get("L47")
        l63 = residuals.get("L63")

        if all([embed is not None, l15 is not None, l47 is not None, l63 is not None]):
            # Skip position 0 (attention sink)
            all_embed.append(embed[1:])
            all_L15.append(l15[1:])
            all_L47.append(l47[1:])
            all_L63.append(l63[1:])
            total_tokens += embed.shape[0] - 1

        if (i + 1) % 8 == 0:
            print(f"    {i+1}/{len(texts)}: {total_tokens} tokens collected", flush=True)

        if total_tokens >= TARGET_TOKENS:
            break

    X_embed = np.concatenate(all_embed, axis=0)[:TARGET_TOKENS]
    Y_L15 = np.concatenate(all_L15, axis=0)[:TARGET_TOKENS]
    Y_L47 = np.concatenate(all_L47, axis=0)[:TARGET_TOKENS]
    Y_L63 = np.concatenate(all_L63, axis=0)[:TARGET_TOKENS]

    print(f"\n  Collected {X_embed.shape[0]} tokens, d={X_embed.shape[1]}")

    # Free model
    del model
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()

    # ── Fit transforms in teacher space (5120×5120) ──
    print(f"\n  Fitting zone transforms (teacher space)...", flush=True)

    t0 = time.time()
    T_A = fit_transform(X_embed, Y_L15)   # embed → L15
    T_B = fit_transform(Y_L15, Y_L47)     # L15 → L47
    T_C = fit_transform(Y_L47, Y_L63)     # L47 → L63
    print(f"  Fitted in {time.time()-t0:.1f}s")

    # ── Project to student space (1280×1280) ──
    print(f"\n  Projecting to student space (d=1280)...", flush=True)
    V_proj = compute_svd_projection(TEACHER_PATH, d_student=1280)

    # T_student = V_proj.T @ T_teacher @ V_proj
    # (1280×5120) @ (5120×5120) @ (5120×1280) = (1280×1280)
    T_A_student = V_proj.T @ T_A @ V_proj
    T_B_student = V_proj.T @ T_B @ V_proj
    T_C_student = V_proj.T @ T_C @ V_proj

    print(f"  Student transforms: {T_A_student.shape}")

    # ── Extract ternary plates + gamma ──
    print(f"\n  Extracting ternary plates...", flush=True)

    signs_A, gamma_A, stats_A = extract_ternary_plate(T_A_student, "Zone_A_compress")
    signs_B, gamma_B, stats_B = extract_ternary_plate(T_B_student, "Zone_B_compute")
    signs_C, gamma_C, stats_C = extract_ternary_plate(T_C_student, "Zone_C_expand")

    # ── Also extract the full model transform ──
    T_full = fit_transform(X_embed, Y_L63)
    T_full_student = V_proj.T @ T_full @ V_proj
    signs_full, gamma_full, stats_full = extract_ternary_plate(T_full_student, "Full_model")

    # ── Save ──
    out_dir = Path("checkpoints/v14-composed")
    out_dir.mkdir(parents=True, exist_ok=True)

    np.savez_compressed(
        str(out_dir / "composed_plates.npz"),
        # Zone plates (student space, 1280×1280)
        zone_a_signs=signs_A,
        zone_a_gamma=gamma_A,
        zone_b_signs=signs_B,
        zone_b_gamma=gamma_B,
        zone_c_signs=signs_C,
        zone_c_gamma=gamma_C,
        # Full model plate (student space, 1280×1280)
        full_signs=signs_full,
        full_gamma=gamma_full,
        # V_proj for reference
        v_proj=V_proj.astype(np.float16),
    )

    # Metadata
    meta = {
        "teacher": MODEL_NAME,
        "n_tokens": int(X_embed.shape[0]),
        "d_teacher": int(X_embed.shape[1]),
        "d_student": 1280,
        "zone_boundaries": {"embed": -1, "L15": 15, "L47": 47, "L63": 63},
        "stats": {
            "zone_a": stats_A,
            "zone_b": stats_B,
            "zone_c": stats_C,
            "full": stats_full,
        },
    }
    with open(out_dir / "meta.json", "w") as f:
        json.dump(meta, f, indent=2)

    # Size report
    plate_size = signs_A.nbytes + signs_B.nbytes + signs_C.nbytes
    gamma_size = gamma_A.nbytes + gamma_B.nbytes + gamma_C.nbytes
    total_positions = signs_A.size + signs_B.size + signs_C.size

    print(f"\n{'='*80}")
    print(f"  EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"\n  Plates saved to: {out_dir}/composed_plates.npz")
    print(f"  Ternary positions: {total_positions:,} ({total_positions/1e6:.1f}M)")
    print(f"  Plate storage: {plate_size/1024:.1f} KB (int8)")
    print(f"  Gamma storage: {gamma_size/1024:.1f} KB (float32)")
    print(f"  Total: {(plate_size + gamma_size)/1024:.1f} KB")
    print(f"\n  Comparison:")
    print(f"    Individual extraction: 593M positions (85 MB)")
    print(f"    Composed extraction:   {total_positions/1e6:.1f}M positions ({(plate_size+gamma_size)/1024:.0f} KB)")
    print(f"    Reduction: {593e6/total_positions:.0f}×")
    print(f"\n  Quality (sign(T)+gamma on random inputs):")
    print(f"    Zone A: per-dim corr = {stats_A['per_dim_corr']:.4f}")
    print(f"    Zone B: per-dim corr = {stats_B['per_dim_corr']:.4f}")
    print(f"    Zone C: per-dim corr = {stats_C['per_dim_corr']:.4f}")
    print(f"    Full:   per-dim corr = {stats_full['per_dim_corr']:.4f}")
    print()


if __name__ == "__main__":
    main()
