"""Diagnose the v15 pipeline: where is information lost?

Traces the residual stream through all 19 strides, measuring:
1. Residual norm at each stride boundary
2. Per-stride delta (how much each stride changes the representation)
3. Cosine similarity between consecutive stride outputs
4. Attention entropy in COMPUTE/LINK strides
5. Position-wise analysis: does information flow from prompt to last position?
6. LM head analysis: what the ternary unembedding does to the final hidden state

Usage:
    uv run python scripts/v15/diagnose_pipeline.py \
        --checkpoint checkpoints/v15-hpe-dolma/step_0005000

License: MIT
"""

from __future__ import annotations

import sys
from pathlib import Path

import mlx.core as mx
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V15Config, AttnType
from model import TensorStatechart, FullAttention, LinearAttention
from load_checkpoint import load_statechart


def load_model(extracted: str, checkpoint: str) -> TensorStatechart:
    model = load_statechart(extracted, freeze_plates=True)
    saved = mx.load(str(Path(checkpoint) / "weights.npz"))
    model.load_weights(list(saved.items()), strict=False)

    # Also load delta plates if they exist
    delta_path = Path(checkpoint) / "delta_plates.npz"
    if delta_path.exists():
        model.enable_delta_plates()
        delta_data = mx.load(str(delta_path))
        model.load_weights(list(delta_data.items()), strict=False)
        print(f"  Loaded {len(delta_data)} delta plates", file=sys.stderr)

    model.eval()
    return model


def cosine_sim(a: np.ndarray, b: np.ndarray) -> float:
    """Cosine similarity between two vectors."""
    dot = np.dot(a.flatten(), b.flatten())
    na = np.linalg.norm(a.flatten())
    nb = np.linalg.norm(b.flatten())
    if na < 1e-10 or nb < 1e-10:
        return 0.0
    return float(dot / (na * nb))


def diagnose(model: TensorStatechart, tokenizer, prompt: str):
    """Run full diagnostic on a single prompt."""
    config = model.config
    specs = config.stride_specs()

    # Tokenize
    ids = tokenizer.encode(prompt, add_special_tokens=False)
    x_input = mx.array([ids])  # (1, L)
    B, L = x_input.shape

    print(f"\n{'='*72}")
    print(f"PROMPT: \"{prompt}\"  ({L} tokens)")
    print(f"{'='*72}")

    # ── 1. Manual forward with per-stride instrumentation ──
    x = model.embed(x_input)
    mx.eval(x)
    embed_out = np.array(x)

    mask = model._get_causal_mask(L)

    print(f"\n  After embedding:")
    print(f"    norm(last_pos)={np.linalg.norm(embed_out[0, -1]):.4f}")
    print(f"    norm(mean)={np.mean(np.linalg.norm(embed_out[0], axis=-1)):.4f}")
    print(f"    std(last_pos)={embed_out[0, -1].std():.6f}")

    prev_x = embed_out.copy()
    stride_states = [embed_out.copy()]  # index 0 = post-embed

    print(f"\n  {'Stride':>8} {'Zone':>8} {'Attn':>6} {'Norm(last)':>11} {'Delta_norm':>11} "
          f"{'Cos(prev)':>10} {'Cos(embed)':>11} {'Std(last)':>10}")
    print(f"  {'-'*8} {'-'*8} {'-'*6} {'-'*11} {'-'*11} {'-'*10} {'-'*11} {'-'*10}")

    for spec in specs:
        stride = model.strides[spec.index]
        x = stride(x, mask=mask)
        mx.eval(x)
        x_np = np.array(x)

        last = x_np[0, -1]
        prev_last = prev_x[0, -1]
        embed_last = embed_out[0, -1]
        delta = x_np - prev_x

        norm_last = np.linalg.norm(last)
        delta_norm = np.linalg.norm(delta[0, -1])
        cos_prev = cosine_sim(last, prev_last)
        cos_embed = cosine_sim(last, embed_last)
        std_last = last.std()

        attn_type = "FULL" if spec.attn_type == AttnType.FULL else "LIN"
        zone_name = spec.zone.name

        print(f"  {spec.index:>8d} {zone_name:>8} {attn_type:>6} {norm_last:>11.4f} "
              f"{delta_norm:>11.4f} {cos_prev:>10.6f} {cos_embed:>11.6f} {std_last:>10.6f}")

        stride_states.append(x_np.copy())
        prev_x = x_np.copy()

    # ── 2. Final norm + lm_head analysis ──
    x_normed = model.final_norm(x)
    mx.eval(x_normed)
    x_normed_np = np.array(x_normed)

    logits = model.lm_head(x_normed)
    mx.eval(logits)
    logits_np = np.array(logits)

    last_hidden = x_normed_np[0, -1]
    last_logits = logits_np[0, -1]

    print(f"\n  Final norm → lm_head:")
    print(f"    pre-norm  norm={np.linalg.norm(np.array(x)[0, -1]):.4f}")
    print(f"    post-norm norm={np.linalg.norm(last_hidden):.4f}  std={last_hidden.std():.6f}")
    print(f"    logits    min={last_logits.min():.3f}  max={last_logits.max():.3f}  "
          f"std={last_logits.std():.3f}  mean={last_logits.mean():.3f}")

    # ── 3. Attention entropy analysis ──
    print(f"\n  Attention analysis (COMPUTE/LINK strides):")
    print(f"    {'Stride':>8} {'Zone':>8} {'MeanEntropy':>12} {'MaxWeight':>10} "
          f"{'EffectiveSpan':>14} {'HeadStd':>10}")
    print(f"    {'-'*8} {'-'*8} {'-'*12} {'-'*10} {'-'*14} {'-'*10}")

    # Re-run to capture attention weights
    x_attn = model.embed(x_input)
    for spec in specs:
        stride = model.strides[spec.index]
        if spec.attn_type == AttnType.FULL:
            attn = stride.attn
            h = stride.attn_norm(x_attn)

            # Manually compute attention weights
            d_head = attn.d_head
            q = attn.q_proj(h).reshape(B, L, attn.n_heads, d_head)
            k = attn.k_proj(h).reshape(B, L, attn.n_kv_heads, d_head)

            q = attn.q_norm(q)
            k = attn.k_norm(k)
            q = q.transpose(0, 2, 1, 3)
            k = k.transpose(0, 2, 1, 3)
            k = attn._apply_hpe_rotation(k, L)

            if attn.n_kv_heads < attn.n_heads:
                repeats = attn.n_heads // attn.n_kv_heads
                k = mx.repeat(k, repeats, axis=1)

            scores = (q @ k.transpose(0, 1, 3, 2)) * attn.scale
            alpha = mx.exp(attn.log_alpha)
            log_dist = attn._get_log_distances(L)
            scores = scores - alpha * log_dist
            scores = scores + mask
            weights = mx.softmax(scores, axis=-1)  # (B, H, L, L)
            mx.eval(weights)
            w_np = np.array(weights)

            # Analyze attention at last position across all heads
            last_pos_weights = w_np[0, :, -1, :]  # (H, L) — what the last position attends to
            # Entropy per head
            eps = 1e-10
            ent_per_head = -np.sum(last_pos_weights * np.log(last_pos_weights + eps), axis=-1)
            max_w_per_head = last_pos_weights.max(axis=-1)
            # Effective attention span: exp(entropy)
            eff_span = np.exp(ent_per_head)

            print(f"    {spec.index:>8d} {spec.zone.name:>8} {ent_per_head.mean():>12.4f} "
                  f"{max_w_per_head.mean():>10.4f} {eff_span.mean():>14.1f} "
                  f"{ent_per_head.std():>10.4f}")

            # Forward through the full stride for next iteration
            x_attn = stride(x_attn, mask=mask)
            mx.eval(x_attn)
        else:
            x_attn = stride(x_attn, mask=mask)
            mx.eval(x_attn)

    # ── 4. Position-wise analysis: prompt positions vs last position ──
    print(f"\n  Position-wise analysis (final residual stream):")
    final_residual = stride_states[-1]  # after last stride

    # Cosine similarity between each position and the last position
    last_rep = final_residual[0, -1]
    cos_to_last = []
    norms = []
    for pos in range(L):
        pos_rep = final_residual[0, pos]
        cos_to_last.append(cosine_sim(pos_rep, last_rep))
        norms.append(np.linalg.norm(pos_rep))

    print(f"    Position norms: min={min(norms):.4f} max={max(norms):.4f} mean={np.mean(norms):.4f}")
    print(f"    Cos(pos, last_pos):")
    for pos in range(L):
        token_str = tokenizer.decode([ids[pos]])
        print(f"      pos={pos:2d} token=\"{token_str}\"  cos={cos_to_last[pos]:.6f}  norm={norms[pos]:.4f}")

    # ── 5. Pairwise cosine between ALL positions in the final residual ──
    print(f"\n  Pairwise cos similarity in final residual (all positions):")
    cos_matrix = np.zeros((L, L))
    for i in range(L):
        for j in range(L):
            cos_matrix[i, j] = cosine_sim(final_residual[0, i], final_residual[0, j])
    # Just show the extremes
    off_diag = cos_matrix[np.triu_indices(L, k=1)]
    print(f"    Off-diagonal cos: min={off_diag.min():.6f}  max={off_diag.max():.6f}  "
          f"mean={off_diag.mean():.6f}  std={off_diag.std():.6f}")

    # ── 6. LM head weight analysis ──
    print(f"\n  LM head (tied ternary embedding) analysis:")
    lm_w = np.array(model.lm_head.weight)  # (vocab, d_model)
    print(f"    Shape: {lm_w.shape}")
    print(f"    Value distribution: unique={len(np.unique(lm_w))}, "
          f"frac_zero={np.mean(lm_w == 0):.4f}, "
          f"frac_pos1={np.mean(lm_w == 1):.4f}, "
          f"frac_neg1={np.mean(lm_w == -1):.4f}")
    # If not perfectly ternary, show actual range
    non_ternary = np.sum(~np.isin(lm_w, [-1, 0, 1]))
    if non_ternary > 0:
        print(f"    Non-ternary values: {non_ternary} ({non_ternary/lm_w.size*100:.2f}%)")
        print(f"    Actual range: [{lm_w.min():.4f}, {lm_w.max():.4f}]")

    # Row norms of lm_head (per-token)
    row_norms = np.linalg.norm(lm_w, axis=1)
    print(f"    Row norms: min={row_norms.min():.4f}  max={row_norms.max():.4f}  "
          f"mean={row_norms.mean():.4f}  std={row_norms.std():.4f}")

    # What are the logits for the winning token vs the correct token?
    winner_id = int(np.argmax(last_logits))
    winner_str = tokenizer.decode([winner_id])
    print(f"\n    Top prediction: [{winner_id}] \"{winner_str}\"  logit={last_logits[winner_id]:.3f}")
    print(f"    Logit of token ' Paris': {last_logits[tokenizer.encode(' Paris', add_special_tokens=False)[0]]:.3f}")

    # ── 7. Check if the hidden state direction differentiates tokens ──
    # Project the final hidden state against a few specific token embeddings
    print(f"\n  Hidden-state vs token embedding dot products:")
    test_tokens = [" Paris", " London", " Berlin", "5", "       ", " data", " the", " is"]
    for tok_str in test_tokens:
        tok_ids = tokenizer.encode(tok_str, add_special_tokens=False)
        if len(tok_ids) == 1:
            tok_embed = lm_w[tok_ids[0]]
            dot = np.dot(last_hidden, tok_embed)
            print(f"    \"{tok_str:>12}\" id={tok_ids[0]:>6d}  dot={dot:>10.4f}  "
                  f"embed_norm={np.linalg.norm(tok_embed):.4f}")


def main():
    import argparse
    from transformers import AutoTokenizer

    p = argparse.ArgumentParser(description="Diagnose v15 pipeline")
    p.add_argument("--extracted", default="checkpoints/v15-zeroed")
    p.add_argument("--checkpoint", default="checkpoints/v15-hpe-dolma/step_0005000")
    args = p.parse_args()

    print("Loading model...", file=sys.stderr)
    model = load_model(args.extracted, args.checkpoint)

    print("Loading tokenizer...", file=sys.stderr)
    tok = AutoTokenizer.from_pretrained("Qwen/Qwen3.6-27B", trust_remote_code=True)

    prompts = [
        "The capital of France is",
        "Once upon a time, there was a",
        "Water boils at a temperature of",
    ]

    for prompt in prompts:
        diagnose(model, tok, prompt)

    print("\n" + "="*72)
    print("DONE")


if __name__ == "__main__":
    main()
