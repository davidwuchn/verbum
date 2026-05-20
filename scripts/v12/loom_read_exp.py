"""Loom Read Experiment — Reading subcrystals one weave at a time.

Hypothesis: The teacher model's loom has 3 weaves at different crossing
angles (attention ~56°, holographic ~68°, FFN ~60°). Different computation
types (lambda composition, fact retrieval, attention-heavy reasoning)
selectively illuminate different weaves. If so, we can read each subcrystal
separately by choosing prompts that activate that weave.

Protocol:
  1. Load Pythia-2.8b, extract W_q and W_up at target layer
  2. Compute CCA directions between W_q and W_up → angle bands
  3. Partition basin probes by domain:
     - COMPOSE: lambda, pure (composition-heavy → holographic ~68°)
     - RETRIEVE: retrieval, analogy (lookup-heavy → FFN ~60°)
     - ROUTE: coding, reasoning, instruction (attention-heavy → ~56°)
  4. Run each probe set through teacher, hook Q activations
  5. For each probe set:
     a. Magnitude profile: per-dimension RMS across probes in that set
     b. Project activations onto CCA angle band directions
     c. Measure energy fraction in each angle band
     d. Compute 8×8 combinator crystal in each band (using pure anchors)
  6. Compare: do probe types concentrate in different bands?
  7. Subcrystal overlap: sign patterns at high-magnitude positions
     for each (probe-type × angle-band) — are they different weaves?

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/loom_read_exp.py

License: MIT
"""

from __future__ import annotations

import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
TARGET_LAYER = 16  # depth 0.5, consistent with prior experiments
SVD_K = 256  # CCA directions to compute

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "loom-read"

# Angle bands (from loom-structure.md, session 123)
ANGLE_BANDS = [
    ("shared",      0, 35),
    ("mid_low",    35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]

# Domain groupings — which probes are expected to illuminate which weave
DOMAIN_GROUPS = {
    "compose":  ["pure", "lambda"],          # composition → holographic weave
    "retrieve": ["retrieval", "analogy"],     # lookup → FFN weave
    "route":    ["coding", "reasoning", "instruction"],  # attention-heavy
    "neutral":  ["arithmetic", "narrative", "tool"],      # mixed / baseline
}

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def cosine_matrix(X: np.ndarray, indices: list[int]) -> np.ndarray:
    """8×8 combinator cosine matrix from probe activations."""
    vecs = X[indices]
    norms = np.maximum(np.linalg.norm(vecs, axis=1, keepdims=True), 1e-8)
    vecs_n = vecs / norms
    return vecs_n @ vecs_n.T


def rdm_correlation(A: np.ndarray, B: np.ndarray) -> float:
    """Correlation between upper-triangular elements of two matrices."""
    n = A.shape[0]
    idx = np.triu_indices(n, k=1)
    a = A[idx] - A[idx].mean()
    b = B[idx] - B[idx].mean()
    denom = np.sqrt(np.sum(a**2)) * np.sqrt(np.sum(b**2))
    return float(np.sum(a * b) / denom) if denom > 1e-10 else 0.0


def load_probes():
    """Load basin probes, return list of probe dicts."""
    path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(path) as f:
        return json.load(f)


def partition_probes(probes: list[dict]) -> dict[str, list[int]]:
    """Partition probe indices by domain group.
    
    Returns: {group_name: [probe_indices]}
    """
    groups = {name: [] for name in DOMAIN_GROUPS}
    for i, p in enumerate(probes):
        domain = p["axis"].split("/")[0]
        for group_name, domains in DOMAIN_GROUPS.items():
            if domain in domains:
                groups[group_name].append(i)
                break
    return groups


def get_pure_indices(probes: list[dict]) -> list[int]:
    """Get indices of the 8 pure combinator anchor probes (in combinator order)."""
    pure_map = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_map[comb] = i
    return [pure_map[c] for c in COMBINATOR_ORDER if c in pure_map]


# ══════════════════════════════════════════════════════════════════════
# Extract model data
# ══════════════════════════════════════════════════════════════════════

def extract_all(probes: list[dict]):
    """Load model, extract weights + activations at target layer."""
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    log(f"  Loading {MODEL_NAME}...")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_NAME)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        MODEL_NAME, torch_dtype=torch.float32, device_map="mps",
    )
    model.eval()

    # ── Extract weights at target layer ──
    layer = model.gpt_neox.layers[TARGET_LAYER]
    qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
    W_q = qkv[:D_MODEL, :]           # (d_model, d_model)
    W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()  # (d_ffn, d_model)

    log(f"  W_q: {W_q.shape}, W_up: {W_up.shape}")

    # ── Hook Q activations (after Q projection, last token) ──
    q_captures = []
    h_captures = []

    def q_hook_fn(module, input, output):
        """Capture residual stream input to this layer (the hidden state)."""
        inp = input[0] if isinstance(input, tuple) else input
        h_captures.append(inp[:, -1, :].detach().cpu().float())

    def attn_hook_fn(module, input, output):
        """Capture Q projection output (first d_model of fused QKV)."""
        # For Pythia: output of query_key_value is (batch, seq, 3*d_model)
        # We want Q = first d_model
        qkv_out = output if not isinstance(output, tuple) else output[0]
        q = qkv_out[:, -1, :D_MODEL].detach().cpu().float()
        q_captures.append(q)

    # Hook the layer input (residual stream)
    h_hook = model.gpt_neox.layers[TARGET_LAYER].register_forward_hook(q_hook_fn)
    # Hook the QKV projection output
    qkv_hook = model.gpt_neox.layers[TARGET_LAYER].attention.query_key_value.register_forward_hook(attn_hook_fn)

    log(f"  Running {len(probes)} probes...")
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)
        if (i + 1) % 20 == 0:
            log(f"    {i + 1}/{len(probes)}")

    h_hook.remove()
    qkv_hook.remove()

    hidden_states = torch.cat(h_captures, dim=0).numpy()  # (n_probes, d_model)
    q_activations = torch.cat(q_captures, dim=0).numpy()   # (n_probes, d_model)

    log(f"  Hidden states: {hidden_states.shape}")
    log(f"  Q activations: {q_activations.shape}")

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return W_q, W_up, hidden_states, q_activations


# ══════════════════════════════════════════════════════════════════════
# CCA + angle band decomposition
# ══════════════════════════════════════════════════════════════════════

def compute_cca(W_q: np.ndarray, W_up: np.ndarray, k: int):
    """CCA between input spaces of W_q and W_up.
    
    Returns:
      angles: (k,) principal angles in degrees
      dirs: (d_model, k) shared (bisector) directions in d_model space
      dirs_q: (d_model, k) Q-aligned directions
      dirs_up: (d_model, k) UP-aligned directions
    """
    _, _, Vt_q = np.linalg.svd(W_q, full_matrices=False)
    _, _, Vt_up = np.linalg.svd(W_up, full_matrices=False)

    A = Vt_q[:k, :].T   # (d_model, k)
    B = Vt_up[:k, :].T   # (d_model, k)

    Qa, _ = np.linalg.qr(A)
    Qb, _ = np.linalg.qr(B)

    U_cca, S_cca, Vt_cca = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
    angles = np.degrees(np.arccos(np.clip(S_cca, 0, 1)))

    dirs_q = Qa @ U_cca        # (d_model, k)
    dirs_up = Qb @ Vt_cca.T    # (d_model, k)

    # Shared midpoint
    dirs = dirs_q + dirs_up
    norms = np.linalg.norm(dirs, axis=0, keepdims=True)
    dirs = dirs / np.maximum(norms, 1e-8)

    return angles, dirs, dirs_q, dirs_up


def bin_directions_by_angle(angles, dirs, dirs_q, dirs_up):
    """Partition CCA directions into angle bands.
    
    Returns: dict[band_name -> {indices, dirs, dirs_q, dirs_up, angles}]
    """
    bands = {}
    for name, lo, hi in ANGLE_BANDS:
        mask = (angles >= lo) & (angles < hi)
        idx = np.where(mask)[0]
        bands[name] = {
            "indices": idx,
            "dirs": dirs[:, mask],           # (d_model, n_band)
            "dirs_q": dirs_q[:, mask],
            "dirs_up": dirs_up[:, mask],
            "angles": angles[mask],
            "n": int(mask.sum()),
        }
    return bands


# ══════════════════════════════════════════════════════════════════════
# Core measurements
# ══════════════════════════════════════════════════════════════════════

def measure_band_energy(
    activations: np.ndarray,
    bands: dict,
    probe_indices: list[int],
) -> dict[str, float]:
    """For a set of probes, measure what fraction of their activation energy
    falls in each angle band.
    
    Returns: {band_name: energy_fraction}
    """
    subset = activations[probe_indices]  # (n_probes, d_model)
    total_energy = np.sum(subset ** 2)

    energies = {}
    for band_name, band_data in bands.items():
        if band_data["n"] < 1:
            energies[band_name] = 0.0
            continue
        # Project onto band directions
        projected = subset @ band_data["dirs"]  # (n_probes, n_band_dirs)
        band_energy = np.sum(projected ** 2)
        energies[band_name] = float(band_energy / total_energy) if total_energy > 0 else 0.0

    return energies


def measure_magnitude_profile(
    activations: np.ndarray,
    probe_indices: list[int],
) -> np.ndarray:
    """Per-dimension RMS magnitude across a probe set.
    
    Returns: (d_model,) magnitude profile
    """
    subset = activations[probe_indices]
    return np.sqrt(np.mean(subset ** 2, axis=0))


def measure_band_crystal(
    activations: np.ndarray,
    bands: dict,
    pure_indices: list[int],
    reference_crystal: np.ndarray,
) -> dict[str, dict]:
    """For each angle band, compute the 8×8 combinator cosine matrix
    and its agreement with the full crystal.
    
    Returns: {band_name: {agreement, whnf_polarity, mean_cosine, ...}}
    """
    results = {}
    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {
                "agreement": None,
                "whnf_polarity": None,
                "n_dirs": band_data["n"],
            }
            continue

        projected = activations @ band_data["dirs"]
        cos_mat = cosine_matrix(projected, pure_indices)
        agreement = rdm_correlation(cos_mat, reference_crystal)

        whnf_idx = COMBINATOR_ORDER.index("WHNF")
        n_comb = len(pure_indices)
        whnf_cos = [cos_mat[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]

        upper_tri = cos_mat[np.triu_indices(n_comb, k=1)]

        results[band_name] = {
            "agreement": float(agreement),
            "whnf_polarity": float(np.mean(whnf_cos)),
            "mean_cosine": float(upper_tri.mean()),
            "std_cosine": float(upper_tri.std()),
            "n_dirs": band_data["n"],
        }

    return results


def measure_subcrystal_signs(
    W_q: np.ndarray,
    magnitude_profiles: dict[str, np.ndarray],
    bands: dict,
    top_k_frac: float = 0.2,
) -> dict:
    """Extract sign patterns at high-magnitude positions for each
    (probe-group × angle-band) and measure overlap between groups.
    
    This is the key test: if different probe types produce different
    sign patterns at the same angle band, the weaves are genuinely
    different subcrystals.
    
    Returns: sign overlap matrix between groups at each band
    """
    sign_W = np.sign(W_q)  # (d_model, d_model) or (output, input)

    groups = list(magnitude_profiles.keys())
    results = {}

    for band_name, band_data in bands.items():
        if band_data["n"] < 2:
            results[band_name] = {"n_dirs": band_data["n"], "overlaps": {}}
            continue

        # Project W_q's sign pattern into band directions
        # band_data["dirs"] is (d_model, n_band) — these are INPUT directions
        # sign(W_q) is (d_out, d_in) — project the input side
        band_dirs = band_data["dirs"]  # (d_model, n_band)

        # For each group: find top-k magnitude dimensions in this band,
        # extract sign pattern there
        group_signs = {}
        for group_name, mag_profile in magnitude_profiles.items():
            # Project magnitude profile onto band directions
            mag_in_band = np.abs(band_dirs.T @ mag_profile)  # (n_band,)

            # Top-k directions by magnitude
            n_top = max(1, int(top_k_frac * len(mag_in_band)))
            top_idx = np.argsort(mag_in_band)[-n_top:]

            # Sign pattern: W_q projected through top-k band directions
            top_dirs = band_dirs[:, top_idx]  # (d_model, n_top)
            sign_projected = sign_W @ top_dirs  # (d_out, n_top)
            group_signs[group_name] = np.sign(sign_projected).flatten()

        # Compute pairwise sign overlap (fraction of matching signs)
        overlaps = {}
        for i, g1 in enumerate(groups):
            for j, g2 in enumerate(groups):
                if j <= i:
                    continue
                s1 = group_signs[g1]
                s2 = group_signs[g2]
                # Only compare non-zero positions
                valid = (s1 != 0) & (s2 != 0)
                if valid.sum() == 0:
                    overlap = None
                else:
                    overlap = float(np.mean(s1[valid] == s2[valid]))
                overlaps[f"{g1}_vs_{g2}"] = overlap

        results[band_name] = {
            "n_dirs": band_data["n"],
            "overlaps": overlaps,
        }

    return results


def measure_group_band_profiles(
    activations: np.ndarray,
    bands: dict,
    probe_groups: dict[str, list[int]],
    pure_indices: list[int],
    reference_crystal: np.ndarray,
) -> dict:
    """For each (group × band), compute crystal agreement.
    
    Key test: does the compose group have DIFFERENT crystal structure
    in the holographic band vs the attention band?
    """
    results = {}
    for group_name, indices in probe_groups.items():
        if len(indices) == 0:
            continue

        group_acts = activations[indices]  # (n_group, d_model)
        group_results = {}

        for band_name, band_data in bands.items():
            if band_data["n"] < 2:
                group_results[band_name] = None
                continue

            # Project group activations into this band
            projected = group_acts @ band_data["dirs"]  # (n_group, n_band)

            # We need pure anchors in this group's activations
            # Use all probes' pure anchors projected through this band
            all_projected = activations @ band_data["dirs"]
            cos_mat = cosine_matrix(all_projected, pure_indices)
            agreement = rdm_correlation(cos_mat, reference_crystal)

            # Also: project ONLY this group's probes and measure
            # how concentrated their energy is here
            group_energy = np.sum(projected ** 2)
            total_energy = np.sum(group_acts ** 2)
            energy_frac = float(group_energy / total_energy) if total_energy > 0 else 0.0

            group_results[band_name] = {
                "energy_fraction": energy_frac,
                "n_probes": len(indices),
            }

        results[group_name] = group_results

    return results


# ══════════════════════════════════════════════════════════════════════
# Main experiment
# ══════════════════════════════════════════════════════════════════════

def main():
    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    # ── Load probes ──
    log("Loading probes...")
    probes = load_probes()
    probe_groups = partition_probes(probes)
    pure_indices = get_pure_indices(probes)

    log(f"  {len(probes)} probes total")
    for name, indices in probe_groups.items():
        domains = DOMAIN_GROUPS[name]
        log(f"  {name}: {len(indices)} probes ({', '.join(domains)})")
    log(f"  Pure anchors: {len(pure_indices)} ({[probes[i]['axis'] for i in pure_indices]})")

    # ── Extract from model ──
    log("\nExtracting model data...")
    W_q, W_up, hidden_states, q_activations = extract_all(probes)

    # ── Reference crystal (from full hidden states) ──
    reference_crystal = cosine_matrix(hidden_states, pure_indices)
    log(f"\nReference crystal (hidden states):")
    whnf_idx = COMBINATOR_ORDER.index("WHNF")
    n_comb = len(pure_indices)
    whnf_cos = [reference_crystal[whnf_idx, j] for j in range(n_comb) if j != whnf_idx]
    log(f"  WHNF polarity: {np.mean(whnf_cos):.4f}")

    # Also compute from Q activations
    q_crystal = cosine_matrix(q_activations, pure_indices)
    q_agreement = rdm_correlation(q_crystal, reference_crystal)
    log(f"  Q crystal agreement with hidden: {q_agreement:.4f}")

    # ── CCA: angle band decomposition ──
    log("\nComputing CCA Q↔UP...")
    angles, dirs, dirs_q, dirs_up = compute_cca(W_q, W_up, SVD_K)
    bands = bin_directions_by_angle(angles, dirs, dirs_q, dirs_up)

    log("  Angle bands:")
    for name, band in bands.items():
        lo, hi = [(l, h) for n, l, h in ANGLE_BANDS if n == name][0]
        log(f"    {name:12s} [{lo:2d}°-{hi:2d}°]: {band['n']:3d} dirs")

    # ══════════════════════════════════════════════════════════════════
    # TEST 1: Energy distribution per probe group per angle band
    # ══════════════════════════════════════════════════════════════════
    log("\n" + "=" * 60)
    log("TEST 1: Energy distribution by probe group × angle band")
    log("=" * 60)

    energy_results = {}

    # Use hidden states (residual stream) for energy measurement
    for group_name, indices in probe_groups.items():
        energies = measure_band_energy(hidden_states, bands, indices)
        energy_results[group_name] = energies
        log(f"\n  {group_name} ({len(indices)} probes):")
        for band_name, frac in energies.items():
            bar = "█" * int(frac * 100)
            log(f"    {band_name:12s}: {frac:.4f}  {bar}")

    # Also with Q activations
    q_energy_results = {}
    log("\n  Q activation energy:")
    for group_name, indices in probe_groups.items():
        energies = measure_band_energy(q_activations, bands, indices)
        q_energy_results[group_name] = energies
        log(f"\n  {group_name} (Q):")
        for band_name, frac in energies.items():
            bar = "█" * int(frac * 100)
            log(f"    {band_name:12s}: {frac:.4f}  {bar}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 2: Magnitude profiles per probe group
    # ══════════════════════════════════════════════════════════════════
    log("\n" + "=" * 60)
    log("TEST 2: Magnitude profiles per probe group")
    log("=" * 60)

    mag_profiles_h = {}
    mag_profiles_q = {}

    for group_name, indices in probe_groups.items():
        mag_h = measure_magnitude_profile(hidden_states, indices)
        mag_q = measure_magnitude_profile(q_activations, indices)
        mag_profiles_h[group_name] = mag_h
        mag_profiles_q[group_name] = mag_q

    # Pairwise correlations between magnitude profiles
    groups = list(probe_groups.keys())
    log("\n  Hidden state magnitude profile correlations:")
    mag_corr_h = {}
    for i, g1 in enumerate(groups):
        for j, g2 in enumerate(groups):
            if j <= i:
                continue
            corr = float(np.corrcoef(mag_profiles_h[g1], mag_profiles_h[g2])[0, 1])
            mag_corr_h[f"{g1}_vs_{g2}"] = corr
            log(f"    {g1} vs {g2}: {corr:.4f}")

    log("\n  Q activation magnitude profile correlations:")
    mag_corr_q = {}
    for i, g1 in enumerate(groups):
        for j, g2 in enumerate(groups):
            if j <= i:
                continue
            corr = float(np.corrcoef(mag_profiles_q[g1], mag_profiles_q[g2])[0, 1])
            mag_corr_q[f"{g1}_vs_{g2}"] = corr
            log(f"    {g1} vs {g2}: {corr:.4f}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 3: Per-band crystal agreement (full probes, then per-group)
    # ══════════════════════════════════════════════════════════════════
    log("\n" + "=" * 60)
    log("TEST 3: Crystal agreement per angle band")
    log("=" * 60)

    # Full crystal per band (as in angle_spectrum_probe.py)
    band_crystal = measure_band_crystal(
        hidden_states, bands, pure_indices, reference_crystal)

    log("\n  Full crystal per band (hidden states):")
    for band_name, data in band_crystal.items():
        if data["agreement"] is not None:
            log(f"    {band_name:12s}: agreement={data['agreement']:.4f}  "
                f"WHNF={data['whnf_polarity']:+.4f}  "
                f"mean_cos={data['mean_cosine']:.4f}")
        else:
            log(f"    {band_name:12s}: too few directions")

    # Per-group band profiles
    group_band = measure_group_band_profiles(
        hidden_states, bands, probe_groups, pure_indices, reference_crystal)

    log("\n  Energy by group × band:")
    for group_name, band_data in group_band.items():
        log(f"\n  {group_name}:")
        for band_name, data in band_data.items():
            if data is not None:
                log(f"    {band_name:12s}: energy={data['energy_fraction']:.4f}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 4: Subcrystal sign overlap
    # ══════════════════════════════════════════════════════════════════
    log("\n" + "=" * 60)
    log("TEST 4: Subcrystal sign overlap between probe groups")
    log("=" * 60)

    sign_results = measure_subcrystal_signs(
        W_q, mag_profiles_h, bands, top_k_frac=0.2)

    for band_name, data in sign_results.items():
        if data["n_dirs"] < 2:
            continue
        log(f"\n  {band_name} ({data['n_dirs']} dirs):")
        for pair, overlap in data["overlaps"].items():
            if overlap is not None:
                # 0.5 = random, 1.0 = identical, lower = different weaves
                diff_signal = "★ DIFFERENT" if overlap < 0.55 else ""
                log(f"    {pair:30s}: {overlap:.4f}  {diff_signal}")

    # ══════════════════════════════════════════════════════════════════
    # TEST 5: Differential magnitude — which dimensions does each
    #         group amplify relative to others?
    # ══════════════════════════════════════════════════════════════════
    log("\n" + "=" * 60)
    log("TEST 5: Differential magnitude profiles")
    log("=" * 60)

    # Mean magnitude profile across all groups (the baseline)
    all_mag = np.mean([mag_profiles_h[g] for g in groups], axis=0)

    diff_profiles = {}
    for group_name in groups:
        diff = mag_profiles_h[group_name] - all_mag
        diff_profiles[group_name] = diff

        # Where is this group amplified vs suppressed?
        amplified = np.sum(diff > 0)
        suppressed = np.sum(diff < 0)
        max_amp = float(np.max(diff))
        max_sup = float(np.min(diff))
        log(f"\n  {group_name}:")
        log(f"    Amplified dims: {amplified}/{D_MODEL}")
        log(f"    Max amplification: {max_amp:.4f}")
        log(f"    Max suppression: {max_sup:.4f}")

        # Project differential onto angle bands
        log(f"    Differential energy per band:")
        for band_name, band_data in bands.items():
            if band_data["n"] < 1:
                continue
            band_dirs = band_data["dirs"]
            diff_projected = band_dirs.T @ diff  # (n_band,)
            diff_energy = float(np.sum(diff_projected ** 2))
            total_diff = float(np.sum(diff ** 2))
            frac = diff_energy / total_diff if total_diff > 0 else 0.0
            bar = "█" * int(frac * 100)
            log(f"      {band_name:12s}: {frac:.4f}  {bar}")

    # ══════════════════════════════════════════════════════════════════
    # Save results
    # ══════════════════════════════════════════════════════════════════

    results = {
        "model": MODEL_NAME,
        "target_layer": TARGET_LAYER,
        "n_probes": len(probes),
        "probe_groups": {k: len(v) for k, v in probe_groups.items()},
        "domain_groupings": DOMAIN_GROUPS,
        "angle_bands": {b["n"]: [lo, hi] for (name, lo, hi), b in zip(ANGLE_BANDS, bands.values())},
        "reference_crystal_whnf_polarity": float(np.mean(whnf_cos)),
        "q_crystal_agreement": float(q_agreement),
        "test1_energy_hidden": energy_results,
        "test1_energy_q": q_energy_results,
        "test2_mag_correlation_hidden": mag_corr_h,
        "test2_mag_correlation_q": mag_corr_q,
        "test3_band_crystal": {k: v for k, v in band_crystal.items()},
        "test3_group_band_energy": group_band,
        "test4_sign_overlap": sign_results,
        "test5_differential": {
            g: {
                "amplified_dims": int(np.sum(diff_profiles[g] > 0)),
                "max_amplification": float(np.max(diff_profiles[g])),
                "max_suppression": float(np.min(diff_profiles[g])),
            }
            for g in groups
        },
        "elapsed_seconds": time.time() - t0,
    }

    results_path = RESULTS_DIR / "results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\n✓ Results saved to {results_path}")
    log(f"  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
