"""Moiré Selectivity Experiment — Is fact retrieval addressed by moiré interference?

The SwiGLU FFN multiplies two projections:
    SwiGLU(x) = down_proj(silu(gate_proj(x)) × up_proj(x))

Gate and up are two diffraction gratings. Their element-wise product
creates a moiré interference pattern. The hypothesis: the moiré
pattern is MORE selective for individual facts than either grating
alone, because the addressing space is combinatorial (quadratic in
active neurons) rather than linear.

If true, this explains how 10M+ facts fit in a model with only ~8K
d_ffn: the moiré indexing provides orders of magnitude more
distinguishable patterns than the raw neuron count.

Architecture:
  1. Load model + fact recall probes
  2. Hook gate_proj (post-silu), up_proj, and their product at each layer
  3. For each probe at each ENRICH-zone layer:
     - Record gate pattern, up pattern, moiré pattern
  4. Compute pairwise cosine similarity across facts for each signal type
  5. Compare: moiré similarity < gate or up similarity = more selective
  6. Group by relation type: within-relation vs cross-relation similarity
  7. Estimate effective addressing capacity per layer

Key measurements:
  - Selectivity ratio: mean_cos(gate) / mean_cos(moiré)
     > 1 means moiré is more selective (lower cross-talk)
  - Relation coherence: within_relation_cos / cross_relation_cos
     > 1 means relations form distinct grating families
  - Capacity estimate: effective rank of the moiré pattern matrix

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/moire_selectivity.py
    uv run python scripts/experiments/moire_selectivity.py --model Qwen/Qwen3-4B

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

PROBES_FILE = Path(__file__).parent.parent.parent / "probes" / "fact_recall.json"
RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "moire-selectivity"

# Relation groups for coarse/fine angle analysis.
# Facts within a group share a relation type (coarse grating angle).
# Facts across groups have different relation types.
RELATION_GROUPS = {
    "capital": [f"cap-{i:02d}" for i in range(1, 16)],
    "creator": [f"cre-{i:02d}" for i in range(1, 11)],
    "science": [f"sci-{i:02d}" for i in range(1, 11)],
    "history": [f"his-{i:02d}" for i in range(1, 11)],
    "geography": [f"geo-{i:02d}" for i in range(1, 8)],
}


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def load_probes() -> list[dict]:
    """Load probe set from JSON. Filter to fact probes only (no computation/arithmetic)."""
    data = json.load(open(PROBES_FILE))
    fact_categories = {"capital", "creator", "science", "history", "geography"}
    return [p for p in data["probes"] if p["category"] in fact_categories]


# ---------------------------------------------------------------------------
# Activation hooking
# ---------------------------------------------------------------------------

class FFNHook:
    """Hook that captures gate (post-silu), up, and moiré activations.

    Qwen3 SwiGLU structure per layer:
        model.layers[i].mlp.gate_proj  (d_model → d_ffn)
        model.layers[i].mlp.up_proj    (d_model → d_ffn)
        model.layers[i].mlp.down_proj  (d_ffn → d_model)

    We hook gate_proj and up_proj as forward hooks, capture their outputs,
    and compute the moiré (element-wise product after silu on gate).
    """

    def __init__(self, n_layers: int):
        self.n_layers = n_layers
        self.gate_acts: dict[int, torch.Tensor] = {}
        self.up_acts: dict[int, torch.Tensor] = {}
        self.handles: list = []

    def _make_gate_hook(self, layer_idx: int):
        def hook(module, input, output):
            # output shape: (batch, seq_len, d_ffn)
            # Take last token position only
            self.gate_acts[layer_idx] = output[0, -1, :].detach().cpu()
        return hook

    def _make_up_hook(self, layer_idx: int):
        def hook(module, input, output):
            self.up_acts[layer_idx] = output[0, -1, :].detach().cpu()
        return hook

    def register(self, model):
        """Register hooks on all FFN layers."""
        for i in range(self.n_layers):
            mlp = model.model.layers[i].mlp
            h1 = mlp.gate_proj.register_forward_hook(self._make_gate_hook(i))
            h2 = mlp.up_proj.register_forward_hook(self._make_up_hook(i))
            self.handles.extend([h1, h2])
        log(f"  Registered hooks on {self.n_layers} layers")

    def remove(self):
        for h in self.handles:
            h.remove()
        self.handles.clear()

    def get_activations(self) -> dict[int, dict[str, np.ndarray]]:
        """Return gate (post-silu), up, and moiré for all layers."""
        result = {}
        for layer_idx in range(self.n_layers):
            if layer_idx not in self.gate_acts:
                continue
            gate_raw = self.gate_acts[layer_idx].float()
            up_raw = self.up_acts[layer_idx].float()

            # Apply silu to gate (matching SwiGLU: silu(gate) * up)
            gate = torch.nn.functional.silu(gate_raw)
            up = up_raw
            moire = gate * up

            result[layer_idx] = {
                "gate": gate.numpy(),
                "up": up.numpy(),
                "moire": moire.numpy(),
            }
        return result

    def clear(self):
        self.gate_acts.clear()
        self.up_acts.clear()


# ---------------------------------------------------------------------------
# Analysis functions
# ---------------------------------------------------------------------------

def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    if norm_a < 1e-10 or norm_b < 1e-10:
        return 0.0
    return float(np.dot(a, b) / (norm_a * norm_b))


def pairwise_cosine_matrix(vectors: list[np.ndarray]) -> np.ndarray:
    """Compute pairwise cosine similarity matrix."""
    n = len(vectors)
    # Stack and normalize
    mat = np.stack(vectors)  # (n, d)
    norms = np.linalg.norm(mat, axis=1, keepdims=True)
    norms = np.maximum(norms, 1e-10)
    normed = mat / norms
    return normed @ normed.T  # (n, n)


def sparsity(vec: np.ndarray, threshold: float = 1e-6) -> float:
    """Fraction of near-zero elements."""
    return float(np.mean(np.abs(vec) < threshold))


def effective_rank(vectors: list[np.ndarray]) -> float:
    """Effective rank of the pattern matrix via SVD.

    This estimates how many independent addressing dimensions the
    patterns span. Higher effective rank = more distinguishable patterns.
    Uses the entropy-based definition: exp(H(normalized_singular_values)).
    """
    mat = np.stack(vectors)  # (n_probes, d_ffn)
    # SVD
    _, s, _ = np.linalg.svd(mat, full_matrices=False)
    # Normalize singular values to a distribution
    s = s[s > 1e-10]
    if len(s) == 0:
        return 0.0
    p = s / s.sum()
    # Shannon entropy
    H = -np.sum(p * np.log(p))
    return float(np.exp(H))


def analyze_selectivity(
    activations: dict[str, dict[int, dict[str, np.ndarray]]],
    probe_ids: list[str],
    probe_categories: dict[str, str],
    n_layers: int,
) -> dict:
    """Core analysis: compare gate, up, and moiré selectivity per layer.

    Returns per-layer metrics:
      - mean/std cosine similarity for gate, up, moiré (lower = more selective)
      - selectivity ratios
      - sparsity stats
      - effective rank
      - within-relation vs cross-relation similarity
    """
    results_by_layer = {}

    for layer_idx in range(n_layers):
        # Collect patterns for this layer across all probes
        gate_patterns = []
        up_patterns = []
        moire_patterns = []
        valid_ids = []

        for pid in probe_ids:
            if layer_idx not in activations[pid]:
                continue
            acts = activations[pid][layer_idx]
            gate_patterns.append(acts["gate"])
            up_patterns.append(acts["up"])
            moire_patterns.append(acts["moire"])
            valid_ids.append(pid)

        if len(valid_ids) < 3:
            continue

        n = len(valid_ids)

        # --- Pairwise cosine similarity ---
        gate_cos = pairwise_cosine_matrix(gate_patterns)
        up_cos = pairwise_cosine_matrix(up_patterns)
        moire_cos = pairwise_cosine_matrix(moire_patterns)

        # Extract upper triangle (excluding diagonal)
        triu_idx = np.triu_indices(n, k=1)
        gate_upper = gate_cos[triu_idx]
        up_upper = up_cos[triu_idx]
        moire_upper = moire_cos[triu_idx]

        # --- Sparsity ---
        gate_sparsity = np.mean([sparsity(g) for g in gate_patterns])
        up_sparsity = np.mean([sparsity(u) for u in up_patterns])
        moire_sparsity = np.mean([sparsity(m) for m in moire_patterns])

        # --- Effective rank ---
        gate_rank = effective_rank(gate_patterns)
        up_rank = effective_rank(up_patterns)
        moire_rank = effective_rank(moire_patterns)

        # --- Within-relation vs cross-relation similarity ---
        within_sims = {"gate": [], "up": [], "moire": []}
        cross_sims = {"gate": [], "up": [], "moire": []}

        id_to_group = {}
        for group_name, group_ids in RELATION_GROUPS.items():
            for gid in group_ids:
                id_to_group[gid] = group_name

        for i in range(n):
            for j in range(i + 1, n):
                gi = id_to_group.get(valid_ids[i])
                gj = id_to_group.get(valid_ids[j])
                if gi is None or gj is None:
                    continue

                target = within_sims if gi == gj else cross_sims
                target["gate"].append(gate_cos[i, j])
                target["up"].append(up_cos[i, j])
                target["moire"].append(moire_cos[i, j])

        within_means = {k: float(np.mean(v)) if v else None for k, v in within_sims.items()}
        cross_means = {k: float(np.mean(v)) if v else None for k, v in cross_sims.items()}

        # Relation coherence: within / cross (> 1 means relations cluster)
        relation_coherence = {}
        for signal in ["gate", "up", "moire"]:
            if within_means[signal] is not None and cross_means[signal] is not None and abs(cross_means[signal]) > 1e-6:
                relation_coherence[signal] = within_means[signal] / cross_means[signal]
            else:
                relation_coherence[signal] = None

        # --- Selectivity ratios ---
        gate_mean = float(np.mean(np.abs(gate_upper)))
        up_mean = float(np.mean(np.abs(up_upper)))
        moire_mean = float(np.mean(np.abs(moire_upper)))

        # Selectivity ratio: mean |cos| of {gate,up} / mean |cos| of moiré
        # > 1 means moiré is more selective (less cross-talk)
        gate_vs_moire = gate_mean / moire_mean if moire_mean > 1e-8 else None
        up_vs_moire = up_mean / moire_mean if moire_mean > 1e-8 else None

        results_by_layer[layer_idx] = {
            "n_probes": n,
            "cosine_similarity": {
                "gate": {"mean": float(np.mean(gate_upper)), "std": float(np.std(gate_upper)),
                         "abs_mean": gate_mean},
                "up": {"mean": float(np.mean(up_upper)), "std": float(np.std(up_upper)),
                       "abs_mean": up_mean},
                "moire": {"mean": float(np.mean(moire_upper)), "std": float(np.std(moire_upper)),
                          "abs_mean": moire_mean},
            },
            "selectivity_ratio": {
                "gate_vs_moire": gate_vs_moire,
                "up_vs_moire": up_vs_moire,
            },
            "sparsity": {
                "gate": float(gate_sparsity),
                "up": float(up_sparsity),
                "moire": float(moire_sparsity),
            },
            "effective_rank": {
                "gate": gate_rank,
                "up": up_rank,
                "moire": moire_rank,
            },
            "relation_analysis": {
                "within_relation_cos": within_means,
                "cross_relation_cos": cross_means,
                "relation_coherence": relation_coherence,
                "n_within_pairs": len(within_sims["gate"]),
                "n_cross_pairs": len(cross_sims["gate"]),
            },
        }

    return results_by_layer


def print_summary(results_by_layer: dict, n_layers: int):
    """Print a readable summary of selectivity analysis."""
    log("\n" + "=" * 110)
    log(f"{'Layer':>5s} | {'gate |cos|':>10s} {'up |cos|':>10s} {'moiré |cos|':>11s} | "
        f"{'G/M ratio':>9s} {'U/M ratio':>9s} | "
        f"{'gate rank':>9s} {'up rank':>9s} {'moiré rank':>10s} | "
        f"{'gate spar':>9s} {'moiré spar':>10s}")
    log("-" * 110)

    for layer_idx in range(n_layers):
        if layer_idx not in results_by_layer:
            continue
        r = results_by_layer[layer_idx]
        cs = r["cosine_similarity"]
        sr = r["selectivity_ratio"]
        sp = r["sparsity"]
        er = r["effective_rank"]

        gm = f"{sr['gate_vs_moire']:.3f}" if sr["gate_vs_moire"] else "  N/A"
        um = f"{sr['up_vs_moire']:.3f}" if sr["up_vs_moire"] else "  N/A"

        log(f"L{layer_idx:3d}  | "
            f"{cs['gate']['abs_mean']:10.4f} {cs['up']['abs_mean']:10.4f} {cs['moire']['abs_mean']:11.4f} | "
            f"{gm:>9s} {um:>9s} | "
            f"{er['gate']:9.1f} {er['up']:9.1f} {er['moire']:10.1f} | "
            f"{sp['gate']:9.3f} {sp['moire']:10.3f}")

    # Relation analysis summary
    log("\n--- Relation Coherence (within_cos / cross_cos, >1 = relations cluster) ---")
    log(f"{'Layer':>5s} | {'gate':>8s} {'up':>8s} {'moiré':>8s} | "
        f"{'within_gate':>11s} {'within_moiré':>12s} {'cross_gate':>10s} {'cross_moiré':>11s}")
    log("-" * 95)

    for layer_idx in range(n_layers):
        if layer_idx not in results_by_layer:
            continue
        ra = results_by_layer[layer_idx]["relation_analysis"]
        rc = ra["relation_coherence"]
        wc = ra["within_relation_cos"]
        cc = ra["cross_relation_cos"]

        def fmt(v):
            return f"{v:.4f}" if v is not None else "  N/A"

        log(f"L{layer_idx:3d}  | "
            f"{fmt(rc['gate']):>8s} {fmt(rc['up']):>8s} {fmt(rc['moire']):>8s} | "
            f"{fmt(wc['gate']):>11s} {fmt(wc['moire']):>12s} "
            f"{fmt(cc['gate']):>10s} {fmt(cc['moire']):>11s}")


def print_verdict(results_by_layer: dict, n_layers: int):
    """Print the experiment's key findings."""
    log("\n" + "=" * 80)
    log("VERDICT")
    log("=" * 80)

    # Find ENRICH zone (layers where facts are active — roughly 50-90% depth)
    enrich_start = int(n_layers * 0.5)
    enrich_end = int(n_layers * 0.9)
    enrich_layers = [l for l in range(enrich_start, enrich_end + 1) if l in results_by_layer]

    if not enrich_layers:
        log("  No ENRICH zone layers found!")
        return

    # Average selectivity ratio in ENRICH zone
    gm_ratios = []
    um_ratios = []
    moire_ranks = []
    gate_ranks = []
    moire_coherences = []
    gate_coherences = []

    for l in enrich_layers:
        r = results_by_layer[l]
        sr = r["selectivity_ratio"]
        if sr["gate_vs_moire"] is not None:
            gm_ratios.append(sr["gate_vs_moire"])
        if sr["up_vs_moire"] is not None:
            um_ratios.append(sr["up_vs_moire"])
        moire_ranks.append(r["effective_rank"]["moire"])
        gate_ranks.append(r["effective_rank"]["gate"])

        mc = r["relation_analysis"]["relation_coherence"]["moire"]
        gc = r["relation_analysis"]["relation_coherence"]["gate"]
        if mc is not None:
            moire_coherences.append(mc)
        if gc is not None:
            gate_coherences.append(gc)

    avg_gm = np.mean(gm_ratios) if gm_ratios else 0
    avg_um = np.mean(um_ratios) if um_ratios else 0
    avg_moire_rank = np.mean(moire_ranks) if moire_ranks else 0
    avg_gate_rank = np.mean(gate_ranks) if gate_ranks else 0
    avg_moire_coh = np.mean(moire_coherences) if moire_coherences else 0
    avg_gate_coh = np.mean(gate_coherences) if gate_coherences else 0

    log(f"\n  ENRICH zone: L{enrich_start}-L{enrich_end} ({len(enrich_layers)} layers)")

    log(f"\n  Q1: Is moiré more selective than gate alone?")
    log(f"      Gate/Moiré selectivity ratio: {avg_gm:.3f}  (>1 = moiré wins)")
    log(f"      Up/Moiré selectivity ratio:   {avg_um:.3f}  (>1 = moiré wins)")
    if avg_gm > 1.0 and avg_um > 1.0:
        log(f"      → YES. Moiré patterns have lower cross-talk than either component.")
        log(f"        This supports quadratic addressing capacity.")
    elif avg_gm > 1.0 or avg_um > 1.0:
        log(f"      → PARTIAL. Moiré beats one component but not both.")
    else:
        log(f"      → NO. Individual components are as selective as the moiré.")
        log(f"        Linear addressing may be sufficient.")

    log(f"\n  Q2: Does moiré have higher effective rank?")
    log(f"      Gate effective rank:  {avg_gate_rank:.1f}")
    log(f"      Moiré effective rank: {avg_moire_rank:.1f}")
    rank_ratio = avg_moire_rank / avg_gate_rank if avg_gate_rank > 0 else 0
    log(f"      Rank ratio: {rank_ratio:.2f}x")
    if rank_ratio > 1.2:
        log(f"      → YES. Moiré spans more independent dimensions.")
    else:
        log(f"      → NO. Similar dimensionality.")

    log(f"\n  Q3: Do relation types form distinct grating families?")
    log(f"      Gate relation coherence:  {avg_gate_coh:.3f}  (>1 = relations cluster)")
    log(f"      Moiré relation coherence: {avg_moire_coh:.3f}  (>1 = relations cluster)")
    if avg_moire_coh > 1.2:
        log(f"      → YES. Same-relation facts fire similar moiré patterns.")
        log(f"        Coarse angle (relation) + fine angle (entity) = two-level addressing.")
    else:
        log(f"      → NO. Relations don't form distinct clusters in moiré space.")

    log(f"\n  Addressing capacity estimate (ENRICH zone avg):")
    log(f"      Gate patterns span {avg_gate_rank:.0f} effective dimensions")
    log(f"      Moiré patterns span {avg_moire_rank:.0f} effective dimensions")
    log(f"      Per-layer distinguishable patterns ≈ exp(rank) but limited by n_probes={len(enrich_layers)}")
    log(f"      NOTE: with only {results_by_layer[enrich_layers[0]]['n_probes']} probes, effective rank")
    log(f"            is bounded by n_probes. Need 200+ probes to measure true capacity.")

    log("\n" + "=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Moiré Selectivity Experiment")
    parser.add_argument("--model", default="Qwen/Qwen3-0.6B", help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--dtype", default="float32", choices=["float16", "bfloat16", "float32"])
    args = parser.parse_args()

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map[args.dtype]

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"=== Moiré Selectivity Experiment ===")
    log(f"Model: {args.model}")
    log(f"Device: {args.device}")
    log(f"Dtype: {args.dtype}")

    # --- Load probes ---
    probes = load_probes()
    log(f"Loaded {len(probes)} fact probes (excluding computation/arithmetic)")

    probe_ids = [p["id"] for p in probes]
    probe_categories = {p["id"]: p["category"] for p in probes}

    # --- Load model ---
    log("\nLoading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model,
        dtype=dtype,
        device_map=args.device,
        trust_remote_code=True,
    )
    model.eval()
    n_layers = model.config.num_hidden_layers
    d_ffn = model.config.intermediate_size
    d_model = model.config.hidden_size
    log(f"Model loaded in {time.time() - t0:.1f}s")
    log(f"  Layers: {n_layers}, d_model: {d_model}, d_ffn: {d_ffn}")

    # --- Register hooks ---
    hook = FFNHook(n_layers)
    hook.register(model)

    # --- Run probes and collect activations ---
    log("\nRunning probes and collecting activations...")
    all_activations: dict[str, dict[int, dict[str, np.ndarray]]] = {}

    t0 = time.time()
    for i, probe in enumerate(probes):
        input_ids = tokenizer.encode(probe["prompt"], return_tensors="pt").to(args.device)
        with torch.no_grad():
            model(input_ids)

        acts = hook.get_activations()
        all_activations[probe["id"]] = acts
        hook.clear()

        if (i + 1) % 10 == 0 or i == len(probes) - 1:
            log(f"  {i + 1}/{len(probes)} probes processed")

    elapsed = time.time() - t0
    log(f"Probes complete in {elapsed:.1f}s ({elapsed / len(probes):.2f}s/probe)")

    # --- Remove hooks ---
    hook.remove()

    # --- Analyze ---
    log("\nAnalyzing selectivity...")
    results_by_layer = analyze_selectivity(
        all_activations, probe_ids, probe_categories, n_layers,
    )

    # --- Print results ---
    print_summary(results_by_layer, n_layers)
    print_verdict(results_by_layer, n_layers)

    # --- Save ---
    model_slug = args.model.replace("/", "_")
    output_file = RESULTS_DIR / f"{model_slug}_selectivity.json"

    # Convert numpy types for JSON serialization
    def numpy_safe(obj):
        if isinstance(obj, (np.floating, np.float32, np.float64)):
            return float(obj)
        if isinstance(obj, (np.integer, np.int32, np.int64)):
            return int(obj)
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return obj

    output = {
        "model": args.model,
        "dtype": args.dtype,
        "n_layers": n_layers,
        "d_model": d_model,
        "d_ffn": d_ffn,
        "n_probes": len(probes),
        "probe_ids": probe_ids,
        "relation_groups": RELATION_GROUPS,
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "results_by_layer": results_by_layer,
    }

    with open(output_file, "w") as f:
        json.dump(output, f, indent=2, default=numpy_safe)
    log(f"\nResults saved to {output_file}")


if __name__ == "__main__":
    main()
