"""Build warped lens — focus the KIBC crystal from a large model into V12.

The warped lens is a depth-dependent focusing optic that maps operation
directions measured in a large teacher model into V12's 7-pass architecture.

Protocol:
  1. Run lambda corpus through teacher (Qwen3-14B) at 7 depth slices
  2. PCA each depth's hidden states to 512 dims (V12's d_model)
  3. Compute per-operation centroids at each depth (K/I/B/C/M directions)
  4. Map teacher depths → V12 passes (warped lens artifact)
  5. Output: ~300KB file containing operation directions per pass

The lens tells V12: "at pass 0, K looks like THIS direction. At pass 3,
M looks like THAT direction." This initializes mirrors and provides
verification targets.

Teacher depth → V12 pass mapping (from session 106 depth profile):
  Qwen L0-5   (B=33×)    →  Pass 0 (ascending shallow)
  Qwen L6-11  (general)  →  Pass 1 (ascending mid)
  Qwen L12-17 (mid)      →  Pass 2 (ascending deep)
  Qwen L18-23 (K=51×)    →  Pass 3 (apex)
  Qwen L24-29 (deep)     →  Pass 4 (descending deep)
  Qwen L30-35 (M=145×)   →  Pass 5 (descending mid)
  Qwen L36-39 (output)   →  Pass 6 (descending shallow)

Usage:
    uv run python scripts/v12/build_warped_lens.py
    uv run python scripts/v12/build_warped_lens.py --model allenai/OLMo-2-1124-13B
    uv run python scripts/v12/build_warped_lens.py --n-per-op 200 --output lens/qwen14b_kibc.npz

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


# ══════════════════════════════════════════════════════════════════════
# Depth mapping — teacher layers → V12 passes
# ══════════════════════════════════════════════════════════════════════

def get_layer_mapping(n_teacher_layers: int, n_passes: int = 7) -> list[int]:
    """Map V12 passes to teacher layer indices (evenly spaced).

    For 40-layer teacher, 7 passes:
        Pass 0 → Layer 3  (shallow, B-dominant)
        Pass 1 → Layer 9  (early-mid)
        Pass 2 → Layer 15 (mid)
        Pass 3 → Layer 21 (deep, K-dominant)
        Pass 4 → Layer 27 (deeper)
        Pass 5 → Layer 33 (very deep, M-dominant)
        Pass 6 → Layer 39 (output)
    """
    # Evenly space through the teacher, avoiding layer 0 (embedding)
    indices = []
    for i in range(n_passes):
        # Map [0, n_passes-1] → [first, last] layers
        layer = int(3 + (n_teacher_layers - 4) * i / (n_passes - 1))
        indices.append(min(layer, n_teacher_layers - 1))
    return indices


# ══════════════════════════════════════════════════════════════════════
# Extract hidden states from teacher
# ══════════════════════════════════════════════════════════════════════

def extract_hidden_states(
    model_name: str,
    prompts: dict[str, list[str]],
    target_layers: list[int],
    max_len: int = 64,
    batch_size: int = 8,
) -> dict[int, dict[str, np.ndarray]]:
    """Extract hidden states from teacher model at specified layers.

    Args:
        model_name: HuggingFace model ID
        prompts: dict[op] → list of prompt strings
        target_layers: which layers to extract from
        max_len: max token length per prompt
        batch_size: forward pass batch size

    Returns:
        dict[layer_idx] → dict[op] → (n_prompts, d_model) hidden states
    """
    import torch
    from transformers import AutoTokenizer, AutoModelForCausalLM

    print(f"  Loading {model_name}...", file=sys.stderr, flush=True)
    tok = AutoTokenizer.from_pretrained(model_name)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    # Load model — use float16 for memory efficiency
    model = AutoModelForCausalLM.from_pretrained(
        model_name,
        torch_dtype=torch.float16,
        device_map="auto",
        output_hidden_states=True,
    )
    model.eval()

    n_layers = model.config.num_hidden_layers
    print(f"  Model: {n_layers} layers, d_model={model.config.hidden_size}",
          file=sys.stderr, flush=True)
    print(f"  Target layers: {target_layers}", file=sys.stderr, flush=True)

    # Extract hidden states per operation
    results: dict[int, dict[str, list[np.ndarray]]] = {
        layer: {op: [] for op in prompts.keys()}
        for layer in target_layers
    }

    for op, op_prompts in prompts.items():
        print(f"    {op}: {len(op_prompts)} prompts...", file=sys.stderr, flush=True)

        for batch_start in range(0, len(op_prompts), batch_size):
            batch = op_prompts[batch_start:batch_start + batch_size]

            # Tokenize
            encoded = tok(
                batch, return_tensors="pt", padding=True,
                truncation=True, max_length=max_len,
            )
            input_ids = encoded["input_ids"].to(model.device)
            attention_mask = encoded["attention_mask"].to(model.device)

            with torch.no_grad():
                outputs = model(
                    input_ids=input_ids,
                    attention_mask=attention_mask,
                    output_hidden_states=True,
                )

            # Extract last-token hidden state at each target layer
            hidden_states = outputs.hidden_states  # tuple of (B, T, D)

            # Get last real token position per sequence
            lengths = attention_mask.sum(dim=1) - 1  # (B,)

            for layer_idx in target_layers:
                # hidden_states[0] = embedding, [1] = after layer 0, etc.
                h = hidden_states[layer_idx + 1]  # (B, T, D)
                # Extract last real token
                for b in range(h.shape[0]):
                    last_pos = int(lengths[b].item())
                    vec = h[b, last_pos].cpu().float().numpy()
                    results[layer_idx][op].append(vec)

    # Stack into arrays
    final: dict[int, dict[str, np.ndarray]] = {}
    for layer_idx in target_layers:
        final[layer_idx] = {}
        for op in prompts.keys():
            final[layer_idx][op] = np.stack(results[layer_idx][op])

    # Cleanup
    del model
    if torch.cuda.is_available():
        torch.cuda.empty_cache()
    if hasattr(torch, 'mps') and torch.backends.mps.is_available():
        torch.mps.empty_cache()

    return final


# ══════════════════════════════════════════════════════════════════════
# Build the warped lens
# ══════════════════════════════════════════════════════════════════════

def build_lens(
    hidden_states: dict[int, dict[str, np.ndarray]],
    target_dim: int = 512,
    target_layers: list[int] = None,
) -> dict:
    """Build the warped lens from extracted hidden states.

    For each layer:
      1. PCA all operation hidden states to target_dim
      2. Compute per-operation centroid in PCA space
      3. Compute per-operation direction (centroid - global mean)
      4. Normalize directions

    Returns dict with:
        - pca_components: per-layer (target_dim, d_model) projection
        - pca_mean: per-layer (d_model,) mean for centering
        - op_directions: per-layer per-op (target_dim,) unit vectors
        - op_centroids: per-layer per-op (target_dim,) raw centroids
        - angular_separation: per-layer pairwise angles between ops
    """
    from sklearn.decomposition import PCA

    ops = ["K", "I", "B", "C", "M"]
    if target_layers is None:
        target_layers = sorted(hidden_states.keys())

    lens = {
        "target_dim": target_dim,
        "source_layers": target_layers,
        "n_passes": len(target_layers),
        "passes": {},
    }

    for pass_idx, layer_idx in enumerate(target_layers):
        layer_data = hidden_states[layer_idx]
        d_model = layer_data[ops[0]].shape[1]

        # Combine all ops for PCA
        all_vecs = np.concatenate([layer_data[op] for op in ops], axis=0)

        # PCA to target_dim
        actual_dim = min(target_dim, all_vecs.shape[0] - 1, d_model)
        pca = PCA(n_components=actual_dim)
        all_projected = pca.fit_transform(all_vecs)  # (N_total, actual_dim)

        # Split back per-op
        n_per_op = [layer_data[op].shape[0] for op in ops]
        split_points = np.cumsum(n_per_op)[:-1]
        op_projected = dict(zip(ops, np.split(all_projected, split_points)))

        # Global centroid
        global_centroid = all_projected.mean(axis=0)

        # Per-op centroids and directions
        op_centroids = {}
        op_directions = {}
        for op in ops:
            centroid = op_projected[op].mean(axis=0)
            direction = centroid - global_centroid
            norm = np.linalg.norm(direction)
            if norm > 1e-8:
                direction = direction / norm
            op_centroids[op] = centroid
            op_directions[op] = direction

        # Angular separation between ops
        angular_sep = {}
        for i, op_a in enumerate(ops):
            for op_b in ops[i+1:]:
                cos = float(np.dot(op_directions[op_a], op_directions[op_b]))
                angle_deg = float(np.degrees(np.arccos(np.clip(cos, -1, 1))))
                angular_sep[f"{op_a}_{op_b}"] = angle_deg

        # Store pass data
        lens["passes"][pass_idx] = {
            "source_layer": layer_idx,
            "d_model_source": d_model,
            "d_model_target": actual_dim,
            "pca_components": pca.components_,       # (actual_dim, d_model)
            "pca_mean": pca.mean_,                   # (d_model,)
            "explained_variance_ratio": pca.explained_variance_ratio_[:10].tolist(),
            "op_directions": {op: op_directions[op] for op in ops},
            "op_centroids": {op: op_centroids[op] for op in ops},
            "angular_separation": angular_sep,
        }

        # Summary
        mean_sep = np.mean(list(angular_sep.values()))
        print(f"    Pass {pass_idx} (L{layer_idx}): dim={actual_dim}, "
              f"mean angular sep={mean_sep:.1f}°, "
              f"var explained (10 PCs)={sum(pca.explained_variance_ratio_[:10])*100:.1f}%",
              file=sys.stderr, flush=True)

    return lens


def save_lens(lens: dict, output_path: Path) -> None:
    """Save the warped lens as a compressed npz + metadata json."""
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Separate numpy arrays from metadata
    arrays = {}
    metadata = {
        "target_dim": lens["target_dim"],
        "source_layers": lens["source_layers"],
        "n_passes": lens["n_passes"],
        "passes": {},
    }

    for pass_idx, pass_data in lens["passes"].items():
        pass_key = f"pass_{pass_idx}"

        # Save arrays
        arrays[f"{pass_key}_pca_components"] = pass_data["pca_components"]
        arrays[f"{pass_key}_pca_mean"] = pass_data["pca_mean"]
        for op in ["K", "I", "B", "C", "M"]:
            arrays[f"{pass_key}_dir_{op}"] = pass_data["op_directions"][op]
            arrays[f"{pass_key}_centroid_{op}"] = pass_data["op_centroids"][op]

        # Save metadata
        metadata["passes"][str(pass_idx)] = {
            "source_layer": pass_data["source_layer"],
            "d_model_source": pass_data["d_model_source"],
            "d_model_target": pass_data["d_model_target"],
            "explained_variance_ratio": pass_data["explained_variance_ratio"],
            "angular_separation": pass_data["angular_separation"],
        }

    # Save
    np.savez_compressed(str(output_path.with_suffix(".npz")), **arrays)
    with open(output_path.with_suffix(".json"), "w") as f:
        json.dump(metadata, f, indent=2)

    # Size report
    npz_size = output_path.with_suffix(".npz").stat().st_size
    print(f"\n  💾 Lens saved: {output_path.with_suffix('.npz')} ({npz_size/1024:.0f} KB)",
          file=sys.stderr, flush=True)
    print(f"  💾 Metadata: {output_path.with_suffix('.json')}",
          file=sys.stderr, flush=True)


# ══════════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build warped lens — focus KIBC crystal from teacher into V12"
    )
    parser.add_argument("--model", default="Qwen/Qwen3-14B",
                        help="Teacher model (HuggingFace ID)")
    parser.add_argument("--n-per-op", type=int, default=200,
                        help="Lambda examples per operation to run through teacher")
    parser.add_argument("--batch-size", type=int, default=8,
                        help="Batch size for teacher forward pass")
    parser.add_argument("--target-dim", type=int, default=512,
                        help="Target dimension (V12's d_model)")
    parser.add_argument("--output", default="lens/warped_lens",
                        help="Output path (without extension)")
    parser.add_argument("--n-passes", type=int, default=7,
                        help="Number of V12 passes to map to")

    args = parser.parse_args()
    output_path = Path(args.output)

    print("=" * 72, file=sys.stderr)
    print("  Warped Lens Builder", file=sys.stderr)
    print(f"  Teacher: {args.model}", file=sys.stderr)
    print(f"  Target dim: {args.target_dim} (V12 d_model)", file=sys.stderr)
    print(f"  Examples per op: {args.n_per_op}", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Step 1: Generate lambda prompts ───────────────────────
    print("\n  Generating lambda prompts...", file=sys.stderr, flush=True)
    from verbum.lambda_gen import LambdaGenerator

    gen = LambdaGenerator(seed=42)
    examples = gen.generate_all(n_per_op=args.n_per_op)

    prompts: dict[str, list[str]] = {}
    for op in ["K", "I", "B", "C", "M"]:
        prompts[op] = [ex.expr for ex in examples[op]]
        print(f"    {op}: {len(prompts[op])} prompts", file=sys.stderr, flush=True)

    # ── Step 2: Determine layer mapping ───────────────────────
    # We need to know n_layers — infer from model config
    from transformers import AutoConfig
    config = AutoConfig.from_pretrained(args.model)
    n_layers = config.num_hidden_layers
    print(f"\n  Teacher: {n_layers} layers", file=sys.stderr, flush=True)

    target_layers = get_layer_mapping(n_layers, args.n_passes)
    print(f"  Layer mapping (pass → teacher layer): {list(enumerate(target_layers))}",
          file=sys.stderr, flush=True)

    # ── Step 3: Extract hidden states ─────────────────────────
    print("\n  Extracting hidden states...", file=sys.stderr, flush=True)
    t0 = time.time()

    hidden_states = extract_hidden_states(
        model_name=args.model,
        prompts=prompts,
        target_layers=target_layers,
        max_len=64,
        batch_size=args.batch_size,
    )

    extract_time = time.time() - t0
    print(f"  Extraction complete: {extract_time:.0f}s", file=sys.stderr, flush=True)

    # Report shapes
    for layer_idx in target_layers[:2]:
        for op in ["K", "I"]:
            shape = hidden_states[layer_idx][op].shape
            print(f"    L{layer_idx} {op}: {shape}", file=sys.stderr, flush=True)

    # ── Step 4: Build the lens ────────────────────────────────
    print("\n  Building warped lens...", file=sys.stderr, flush=True)
    lens = build_lens(
        hidden_states,
        target_dim=args.target_dim,
        target_layers=target_layers,
    )

    # ── Step 5: Save ──────────────────────────────────────────
    save_lens(lens, output_path)

    # ── Summary ───────────────────────────────────────────────
    print(f"\n{'='*72}", file=sys.stderr)
    print(f"  WARPED LENS COMPLETE", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)
    print(f"\n  Angular separation per pass (mean across op pairs):", file=sys.stderr)
    for pass_idx in range(len(target_layers)):
        pass_data = lens["passes"][pass_idx]
        seps = pass_data["angular_separation"]
        mean_sep = np.mean(list(seps.values()))
        max_sep = max(seps.values())
        min_sep = min(seps.values())
        max_pair = max(seps.items(), key=lambda x: x[1])
        print(f"    Pass {pass_idx} (L{pass_data['source_layer']}): "
              f"mean={mean_sep:.1f}° min={min_sep:.1f}° max={max_sep:.1f}° "
              f"(strongest: {max_pair[0]}={max_pair[1]:.1f}°)",
              file=sys.stderr)

    print(f"\n  Total time: {time.time()-t0:.0f}s", file=sys.stderr)
    print(f"  Lens ready for V12 mirror initialization", file=sys.stderr)
    print(f"{'='*72}", file=sys.stderr)


if __name__ == "__main__":
    main()
