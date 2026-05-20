"""Etcher VSM Prototype — S4 Crystal Counter + S1 Reference Beam Extractor.

Session 124. This is the core of the etcher VSM: the measurement and
extraction pipeline. Given a teacher model and probe set:

S4 (crystal counter): Measure subcrystal count at each depth × band.
S1 (reference beam):  Extract sign patterns per subcrystal family.

The prototype runs S4 at one depth, then S1 to extract per-family
sign patterns at that depth. This validates the pipeline before
scaling to the full breathing curve.

Usage:
    cd ~/src/verbum
    uv run python scripts/v12/etcher_vsm_proto.py [--depth 0.226]

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from pathlib import Path

import numpy as np

MODEL_NAME = "EleutherAI/pythia-2.8b-deduped"
N_LAYERS = 32
D_MODEL = 2560
SVD_K = 256

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "etcher-vsm"

ANGLE_BANDS = [
    ("shared",      0, 35),
    ("mid_low",    35, 50),
    ("attn_clust", 50, 58),
    ("transition", 58, 64),
    ("holographic", 64, 72),
    ("peripheral", 72, 82),
    ("private",    82, 91),
]

# Subcrystal families (7 reference beams)
FAMILIES = {
    "pure":       ["pure"],
    "lambda":     ["lambda"],
    "arithmetic": ["arithmetic"],
    "coding":     ["coding"],
    "analogy":    ["analogy"],
    "reasoning":  ["reasoning"],
    "text_gen":   ["tool", "narrative", "instruction"],
}

# Remaining domains that might not be in families
EXTRA_DOMAINS = ["retrieval"]  # retrieval sometimes clusters with analogy, sometimes alone

COMBINATOR_ORDER = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes():
    path = Path(__file__).parent.parent.parent / "lattice" / "basin_probes.json"
    with open(path) as f:
        return json.load(f)


def get_family_indices(probes):
    """Map each family → list of probe indices."""
    families = {name: [] for name in FAMILIES}
    families["retrieval"] = []  # separate tracking

    for i, p in enumerate(probes):
        domain = p["axis"].split("/")[0]
        placed = False
        for fam_name, domains in FAMILIES.items():
            if domain in domains:
                families[fam_name].append(i)
                placed = True
                break
        if not placed and domain == "retrieval":
            families["retrieval"].append(i)

    return families


def get_pure_indices(probes):
    pure_map = {}
    for i, p in enumerate(probes):
        if p["axis"].startswith("pure/"):
            comb = p["axis"].split("/")[1]
            pure_map[comb] = i
    return [pure_map[c] for c in COMBINATOR_ORDER if c in pure_map]


# ══════════════════════════════════════════════════════════════════════
# S4: CRYSTAL COUNTER
# ══════════════════════════════════════════════════════════════════════

class CrystalCounter:
    """S4 — Adaptive crystal counter.
    
    Given a teacher model at one depth:
    1. Extract W_q, W_up
    2. CCA → angle bands
    3. Run probes → magnitude profiles per family
    4. Sign overlap matrix → cluster count per band
    
    Returns: BreathingPoint with subcrystal count, clusters, sign overlaps.
    """

    def __init__(self, W_q, W_up, hidden_states, probes, family_indices):
        self.W_q = W_q
        self.W_up = W_up
        self.hidden_states = hidden_states
        self.probes = probes
        self.family_indices = family_indices

        # CCA decomposition
        self.angles, self.dirs = self._compute_cca(SVD_K)
        self.bands = self._bin_directions()

        # Magnitude profiles per family
        self.mag_profiles = {}
        for fam_name, indices in family_indices.items():
            if len(indices) > 0:
                self.mag_profiles[fam_name] = np.sqrt(
                    np.mean(hidden_states[indices] ** 2, axis=0))

    def _compute_cca(self, k):
        _, _, Vt_q = np.linalg.svd(self.W_q, full_matrices=False)
        _, _, Vt_up = np.linalg.svd(self.W_up, full_matrices=False)
        A = Vt_q[:k, :].T
        B = Vt_up[:k, :].T
        Qa, _ = np.linalg.qr(A)
        Qb, _ = np.linalg.qr(B)
        U, S, Vt = np.linalg.svd(Qa.T @ Qb, full_matrices=False)
        angles = np.degrees(np.arccos(np.clip(S, 0, 1)))
        dirs_q = Qa @ U
        dirs_up = Qb @ Vt.T
        dirs = dirs_q + dirs_up
        norms = np.linalg.norm(dirs, axis=0, keepdims=True)
        dirs = dirs / np.maximum(norms, 1e-8)
        return angles, dirs

    def _bin_directions(self):
        bands = {}
        for name, lo, hi in ANGLE_BANDS:
            mask = (self.angles >= lo) & (self.angles < hi)
            bands[name] = {"dirs": self.dirs[:, mask], "n": int(mask.sum())}
        return bands

    def count_at_band(self, band_name, threshold=0.55, top_k_frac=0.2):
        """Count subcrystals at one angle band.
        
        Returns: (count, clusters, overlap_matrix)
        """
        band = self.bands[band_name]
        if band["n"] < 2:
            return 0, [], {}

        sign_W = np.sign(self.W_q)
        band_dirs = band["dirs"]

        family_names = [f for f in self.mag_profiles.keys()]
        family_signs = {}

        for fam_name in family_names:
            mag = self.mag_profiles[fam_name]
            mag_in_band = np.abs(band_dirs.T @ mag)
            n_top = max(1, int(top_k_frac * len(mag_in_band)))
            top_idx = np.argsort(mag_in_band)[-n_top:]
            top_dirs = band_dirs[:, top_idx]
            sign_proj = sign_W @ top_dirs
            family_signs[fam_name] = np.sign(sign_proj).flatten()

        # Pairwise overlaps
        overlaps = {}
        for i, f1 in enumerate(family_names):
            for j, f2 in enumerate(family_names):
                if j <= i:
                    continue
                s1, s2 = family_signs[f1], family_signs[f2]
                valid = (s1 != 0) & (s2 != 0)
                if valid.sum() == 0:
                    overlaps[f"{f1}_vs_{f2}"] = None
                else:
                    overlaps[f"{f1}_vs_{f2}"] = float(np.mean(s1[valid] == s2[valid]))

        # Cluster
        n = len(family_names)
        agree = np.ones((n, n), dtype=bool)
        for pair, ov in overlaps.items():
            if ov is None or ov < threshold:
                parts = pair.split("_vs_")
                i = family_names.index(parts[0])
                j = family_names.index(parts[1])
                agree[i, j] = False
                agree[j, i] = False

        visited = set()
        clusters = []
        for i in range(n):
            if i in visited:
                continue
            cluster = {i}
            queue = [i]
            while queue:
                curr = queue.pop(0)
                for j in range(n):
                    if j not in visited and j not in cluster and agree[curr, j]:
                        cluster.add(j)
                        queue.append(j)
            visited.update(cluster)
            clusters.append([family_names[k] for k in sorted(cluster)])

        return len(clusters), clusters, overlaps

    def count_all_bands(self):
        """Count subcrystals at all angle bands. Returns dict."""
        results = {}
        for band_name, _, _ in ANGLE_BANDS:
            count, clusters, overlaps = self.count_at_band(band_name)
            results[band_name] = {
                "count": count,
                "clusters": clusters,
                "overlaps": overlaps,
                "n_dirs": self.bands[band_name]["n"],
            }
        return results


# ══════════════════════════════════════════════════════════════════════
# S1: REFERENCE BEAM EXTRACTOR
# ══════════════════════════════════════════════════════════════════════

class ReferenceBeam:
    """S1 — Extract one subcrystal from the teacher.
    
    Given a family name and a CrystalCounter (which has the CCA decomposition
    and magnitude profiles), extract the sign pattern at high-magnitude
    positions within the target angle band.
    """

    def __init__(self, family_name, counter: CrystalCounter,
                 band_name="holographic", top_k_frac=0.2):
        self.family_name = family_name
        self.band_name = band_name

        band = counter.bands[band_name]
        if band["n"] < 2 or family_name not in counter.mag_profiles:
            self.sign_pattern = None
            self.position_mask = None
            self.n_positions = 0
            return

        band_dirs = band["dirs"]  # (d_model, n_band)
        mag = counter.mag_profiles[family_name]

        # Project magnitude onto band directions
        mag_in_band = np.abs(band_dirs.T @ mag)  # (n_band,)
        n_top = max(1, int(top_k_frac * len(mag_in_band)))
        top_idx = np.argsort(mag_in_band)[-n_top:]

        # Extract sign pattern at these positions
        self.top_dirs = band_dirs[:, top_idx]  # (d_model, n_top)
        sign_W = np.sign(counter.W_q)
        self.sign_pattern = np.sign(sign_W @ self.top_dirs)  # (d_out, n_top)

        # Magnitude values for weighting
        self.mag_weights = mag_in_band[top_idx]

        # Position mask in d_model space (which dimensions are active)
        # The top-k band directions define a subspace
        self.n_positions = self.sign_pattern.size
        self.n_nonzero = int(np.sum(self.sign_pattern != 0))

    def summary(self):
        if self.sign_pattern is None:
            return f"{self.family_name}: no data"
        pos_frac = np.mean(self.sign_pattern > 0)
        neg_frac = np.mean(self.sign_pattern < 0)
        return (f"{self.family_name} @ {self.band_name}: "
                f"{self.n_positions} positions, "
                f"{self.n_nonzero} nonzero, "
                f"+{pos_frac:.1%} / -{neg_frac:.1%}")

    def overlap_with(self, other: 'ReferenceBeam') -> float | None:
        """Compute sign overlap with another reference beam."""
        if self.sign_pattern is None or other.sign_pattern is None:
            return None
        s1 = self.sign_pattern.flatten()
        s2 = other.sign_pattern.flatten()
        if s1.shape != s2.shape:
            return None
        valid = (s1 != 0) & (s2 != 0)
        if valid.sum() == 0:
            return None
        return float(np.mean(s1[valid] == s2[valid]))


# ══════════════════════════════════════════════════════════════════════
# S3: BUDGET ALLOCATOR (stub — just uses S4 output)
# ══════════════════════════════════════════════════════════════════════

def allocate_beams(crystal_counts: dict) -> dict:
    """Given subcrystal counts per band, decide how many beams per band.
    
    Simple policy: n_beams = n_subcrystals at each band.
    More sophisticated: weight by crystal agreement, WHNF polarity, etc.
    """
    schedule = {}
    for band_name, data in crystal_counts.items():
        schedule[band_name] = {
            "n_beams": data["count"],
            "families": data["clusters"],
        }
    return schedule


# ══════════════════════════════════════════════════════════════════════
# Main — run S4 + S1 at one depth
# ══════════════════════════════════════════════════════════════════════

def extract_teacher(probes, target_layer):
    """Load teacher, extract weights + activations at target layer."""
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

    layer = model.gpt_neox.layers[target_layer]
    qkv = layer.attention.query_key_value.weight.detach().cpu().float().numpy()
    W_q = qkv[:D_MODEL, :]
    W_up = layer.mlp.dense_h_to_4h.weight.detach().cpu().float().numpy()

    captures = []

    def hook_fn(module, input, output):
        inp = input[0] if isinstance(input, tuple) else input
        captures.append(inp[:, -1, :].detach().cpu().float())

    hook = model.gpt_neox.layers[target_layer].register_forward_hook(hook_fn)

    log(f"  Running {len(probes)} probes...")
    for probe in probes:
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to("mps")
        with torch.no_grad():
            _ = model(input_ids)

    hook.remove()
    hidden_states = torch.cat(captures, dim=0).numpy()

    del model, tokenizer
    gc.collect()
    torch.mps.empty_cache()

    return W_q, W_up, hidden_states


def main():
    parser = argparse.ArgumentParser(description="Etcher VSM Prototype")
    parser.add_argument("--depth", type=float, default=0.226,
                        help="Depth fraction (default 0.226 = peak fragmentation)")
    args = parser.parse_args()

    t0 = time.time()
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    target_layer = min(int(round(args.depth * (N_LAYERS - 1))), N_LAYERS - 1)
    log(f"Etcher VSM Prototype — depth={args.depth:.3f}, layer={target_layer}")

    # Load probes
    probes = load_probes()
    family_indices = get_family_indices(probes)
    active_families = {k: v for k, v in family_indices.items() if len(v) > 0}
    log(f"  {len(probes)} probes, {len(active_families)} active families:")
    for name, idx in active_families.items():
        log(f"    {name}: {len(idx)} probes")

    # Extract teacher
    log("\nExtracting teacher...")
    W_q, W_up, hidden_states = extract_teacher(probes, target_layer)

    # ═══════════════════════════════════════════════════════════════
    # S4: Crystal Counter
    # ═══════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log(f"S4: CRYSTAL COUNTER (layer {target_layer}, depth {args.depth:.3f})")
    log(f"{'='*60}")

    counter = CrystalCounter(W_q, W_up, hidden_states, probes, active_families)
    crystal_counts = counter.count_all_bands()

    log("\n  Subcrystal counts by band:")
    for band_name, data in crystal_counts.items():
        if data["count"] > 0:
            cl_str = " | ".join(["+".join(c) for c in data["clusters"]])
            log(f"    {band_name:12s}: {data['count']} crystals  [{cl_str}]")

    # ═══════════════════════════════════════════════════════════════
    # S3: Budget Allocator
    # ═══════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("S3: BUDGET ALLOCATOR")
    log(f"{'='*60}")

    schedule = allocate_beams(crystal_counts)
    total_beams = sum(s["n_beams"] for s in schedule.values())
    log(f"\n  Total beams needed: {total_beams}")
    for band_name, sched in schedule.items():
        if sched["n_beams"] > 0:
            log(f"    {band_name:12s}: {sched['n_beams']} beams → "
                f"{['+'.join(c) for c in sched['families']]}")

    # ═══════════════════════════════════════════════════════════════
    # S1: Reference Beam Extraction
    # ═══════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("S1: REFERENCE BEAM EXTRACTION")
    log(f"{'='*60}")

    # Extract beams at the 3 most interesting bands
    target_bands = ["mid_low", "holographic", "transition"]
    all_beams = {}

    for band_name in target_bands:
        log(f"\n  {band_name} band ({counter.bands[band_name]['n']} dirs):")
        beams = {}
        for fam_name in active_families.keys():
            beam = ReferenceBeam(fam_name, counter, band_name=band_name)
            beams[fam_name] = beam
            log(f"    {beam.summary()}")

        # Cross-beam overlaps
        fam_names = list(beams.keys())
        log(f"\n    Cross-beam overlaps:")
        for i, f1 in enumerate(fam_names):
            for j, f2 in enumerate(fam_names):
                if j <= i:
                    continue
                ov = beams[f1].overlap_with(beams[f2])
                if ov is not None:
                    marker = "★" if ov < 0.55 else " "
                    log(f"      {f1:12s} ↔ {f2:12s}: {ov:.4f} {marker}")

        all_beams[band_name] = beams

    # ═══════════════════════════════════════════════════════════════
    # Verification: does S1 output match S4 clustering?
    # ═══════════════════════════════════════════════════════════════
    log(f"\n{'='*60}")
    log("VERIFICATION: S1 beams agree with S4 clusters?")
    log(f"{'='*60}")

    for band_name in target_bands:
        s4_data = crystal_counts.get(band_name, {})
        s4_clusters = s4_data.get("clusters", [])
        s4_count = s4_data.get("count", 0)

        beams = all_beams[band_name]
        fam_names = list(beams.keys())

        # Build S1 overlap-based clusters
        n = len(fam_names)
        agree = np.ones((n, n), dtype=bool)
        for i, f1 in enumerate(fam_names):
            for j, f2 in enumerate(fam_names):
                if j <= i:
                    continue
                ov = beams[f1].overlap_with(beams[f2])
                if ov is None or ov < 0.55:
                    agree[i, j] = False
                    agree[j, i] = False

        visited = set()
        s1_clusters = []
        for i in range(n):
            if i in visited:
                continue
            cluster = {i}
            queue = [i]
            while queue:
                curr = queue.pop(0)
                for j in range(n):
                    if j not in visited and j not in cluster and agree[curr, j]:
                        cluster.add(j)
                        queue.append(j)
            visited.update(cluster)
            s1_clusters.append([fam_names[k] for k in sorted(cluster)])

        match = "✓ MATCH" if len(s1_clusters) == s4_count else "✗ MISMATCH"
        log(f"\n  {band_name}:")
        log(f"    S4 says: {s4_count} clusters → {s4_clusters}")
        log(f"    S1 says: {len(s1_clusters)} clusters → {s1_clusters}")
        log(f"    {match}")

    # Save
    results = {
        "model": MODEL_NAME,
        "target_layer": target_layer,
        "depth": args.depth,
        "s4_crystal_counts": {
            bn: {"count": d["count"], "clusters": d["clusters"]}
            for bn, d in crystal_counts.items()
        },
        "s3_schedule": {
            bn: {"n_beams": s["n_beams"]}
            for bn, s in schedule.items()
        },
        "s3_total_beams": total_beams,
        "elapsed_seconds": time.time() - t0,
    }

    results_path = RESULTS_DIR / f"proto_d{args.depth:.3f}.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    log(f"\n✓ Results saved to {results_path}")
    log(f"  Total time: {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
