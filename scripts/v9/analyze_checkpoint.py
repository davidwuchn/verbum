"""
Analyze basin projector checkpoint — diagnose training health.

Checks:
  1. Loss trend and sawtooth pattern (Adam recovery after evolution)
  2. Tournament acceptance rate and strategy distribution
  3. Per-stratum eval (optional, requires model load)

Usage:
    cd ~/src/verbum
    uv run python scripts/v9/analyze_checkpoint.py checkpoints/basin/step_001000
    uv run python scripts/v9/analyze_checkpoint.py checkpoints/basin/step_001000 --eval

License: MIT
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np


def analyze_losses(losses: list[float], gen_interval: int = 25):
    """Analyze loss trajectory for sawtooth pattern."""
    losses = np.array(losses)
    n = len(losses)

    print(f"\n{'=' * 60}")
    print(f"  Loss Analysis ({n} values)")
    print(f"{'=' * 60}")

    print(f"\n  Overall: min={losses.min():.4f}  max={losses.max():.4f}  "
          f"mean={losses.mean():.4f}  std={losses.std():.4f}")

    # Trend: first half vs second half
    mid = n // 2
    first_half = losses[:mid].mean()
    second_half = losses[mid:].mean()
    trend = "↓ improving" if second_half < first_half else "↑ worsening" if second_half > first_half else "→ flat"
    print(f"  Trend: first_half={first_half:.4f}  second_half={second_half:.4f}  {trend}")

    # Sawtooth detection: compare losses right after tournament vs rest
    # Tournament happens at multiples of gen_interval
    # losses[-100:] means we need to figure out which indices are post-tournament
    post_tournament = []  # indices 0, 1, 2 after each tournament
    between = []

    for i in range(n):
        # This loss is at step (start_step + i + 1)
        # We don't know start_step exactly, but we can check modular pattern
        # Tournament is every gen_interval steps, so look at periodic pattern
        phase = i % gen_interval
        if phase < 3:  # first 3 steps after a tournament boundary
            post_tournament.append(losses[i])
        elif phase >= 10:  # well after tournament
            between.append(losses[i])

    if post_tournament and between:
        post_mean = np.mean(post_tournament)
        between_mean = np.mean(between)
        spike = post_mean - between_mean
        print(f"\n  Sawtooth analysis (gen_interval={gen_interval}):")
        print(f"    Post-tournament loss (0-2 steps after): {post_mean:.4f}  (n={len(post_tournament)})")
        print(f"    Between-tournament loss (10+ steps after): {between_mean:.4f}  (n={len(between)})")
        print(f"    Spike: {spike:+.4f}")

        if spike > 0.02:
            print(f"    ⚠️  SAWTOOTH DETECTED — loss spikes after tournaments")
            print(f"    → Adam may need more steps to recover. Consider --gen-interval 50")
        elif spike > 0.005:
            print(f"    ⚡ Mild sawtooth — acceptable, Adam mostly recovers in time")
        else:
            print(f"    ✅ No sawtooth — Adam recovers well within {gen_interval} steps")
    else:
        print(f"\n  (not enough data points for sawtooth analysis)")

    # Variance analysis: is loss stable or wild?
    rolling_std = np.array([losses[max(0,i-5):i+1].std() for i in range(5, n)])
    print(f"\n  Volatility: rolling_std(5) = {rolling_std.mean():.4f}")
    if rolling_std.mean() > 0.05:
        print(f"    ⚠️  High volatility — learning rate may be too high")
    elif rolling_std.mean() > 0.02:
        print(f"    ⚡ Moderate volatility — normal for early training")
    else:
        print(f"    ✅ Low volatility — stable training")


def analyze_evolution(state: dict):
    """Analyze evolutionary tournament health."""
    total_gens = state.get("total_gens", 0)
    total_accepted = state.get("total_accepted", 0)
    base_pct = state.get("base_pct", 0)

    print(f"\n{'=' * 60}")
    print(f"  Evolution Analysis")
    print(f"{'=' * 60}")

    if total_gens == 0:
        print("  No tournaments yet.")
        return

    accept_rate = total_accepted / total_gens
    print(f"\n  Tournaments: {total_gens}")
    print(f"  Accepted: {total_accepted} ({accept_rate:.1%})")
    print(f"  Rejected: {total_gens - total_accepted} ({1 - accept_rate:.1%})")
    print(f"  Base mutation rate: {base_pct:.4f}")

    if accept_rate > 0.9:
        print(f"\n  ⚠️  Very high acceptance ({accept_rate:.0%}) — topology is easily improved")
        print(f"  → Could mean gamma hasn't converged, or mutations are too conservative")
        print(f"  → Consider increasing base_pct for faster exploration")
    elif accept_rate > 0.6:
        print(f"\n  ✅ Healthy acceptance rate ({accept_rate:.0%}) — evolution is finding improvements")
    elif accept_rate > 0.3:
        print(f"\n  ✅ Moderate acceptance ({accept_rate:.0%}) — balanced exploration/exploitation")
    elif accept_rate > 0.1:
        print(f"\n  ⚡ Low acceptance ({accept_rate:.0%}) — topology is getting harder to improve")
        print(f"  → Normal in later training as topology stabilizes")
    else:
        print(f"\n  ⚠️  Very low acceptance ({accept_rate:.0%}) — evolution may not be helping")
        print(f"  → Consider if gen_interval should increase (let Adam work longer)")


def analyze_metrics(state: dict):
    """Analyze final metrics if available."""
    metrics = state.get("final_metrics", {})
    if not metrics:
        return

    print(f"\n{'=' * 60}")
    print(f"  Eval Metrics")
    print(f"{'=' * 60}")

    noise_floor = 1.0 / np.sqrt(64)  # ~0.125
    ceiling = 0.845

    cosine_sim = metrics.get("cosine_sim", 0)
    print(f"\n  Overall cosine_sim: {cosine_sim:.4f}")
    print(f"  Noise floor: {noise_floor:.3f}  (1/√64, below this = random)")
    print(f"  Ceiling: {ceiling:.3f}  (PCA reconstruction limit)")
    print(f"  Progress: {cosine_sim / ceiling:.1%} of theoretical max")

    print(f"\n  Per-stratum:")
    for k, v in sorted(metrics.items()):
        if k.startswith("sim_"):
            stratum = k[4:]
            status = "✅ signal" if v > noise_floor else "⚡ weak" if v > 0 else "— random"
            bar_len = max(0, int(v / ceiling * 40))
            bar = "█" * bar_len + "░" * (40 - bar_len)
            print(f"    {stratum:12s}: {v:+.4f}  |{bar}|  {status}")


def run_eval(checkpoint_dir: Path):
    """Load model and run fresh evaluation."""
    import mlx.core as mx
    import mlx.nn as nn
    import mlx.optimizers as optim

    sys.path.insert(0, str(Path(__file__).parent))
    sys.path.insert(0, str(Path(__file__).parent.parent / "v8"))

    from basin_model import BasinProjector, BasinConfig
    from train_basin import (
        PCAProjector, OracleDataLoader, evaluate, load_checkpoint,
        cosine_loss, SHARD_DIR, N_SHARDS, EVAL_SHARDS,
    )
    from ternary import zero_ternary_grads, restore_ternary

    print(f"\n{'=' * 60}")
    print(f"  Fresh Evaluation (loading model...)")
    print(f"{'=' * 60}")

    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-32B")
    pca = PCAProjector(SHARD_DIR / "pca_projector.npz")

    eval_shards = list(range(N_SHARDS - EVAL_SHARDS, N_SHARDS))
    eval_loader = OracleDataLoader(
        SHARD_DIR, pca, tokenizer, eval_shards,
        batch_size=32, seed=99,
    )

    model = BasinProjector(BasinConfig(max_seq_len=128))
    optimizer = optim.AdamW(learning_rate=3e-4)

    # Dummy init
    def loss_fn(m, ids, spans, targets, mask):
        pred, pred_mask = m(ids, spans)
        return cosine_loss(pred, targets, mask)
    _lfg = nn.value_and_grad(model, loss_fn)
    d = eval_loader.next_batch()
    _lv, _g = _lfg(model, d[0], d[1], d[2], d[3])
    mx.eval(_lv, _g)
    _g = zero_ternary_grads(model, _g)
    optimizer.update(model, _g)
    mx.eval(model.parameters(), optimizer.state)
    restore_ternary(model)
    eval_loader.reset()

    state, _, _, _ = load_checkpoint(checkpoint_dir, model, optimizer)

    metrics = evaluate(model, eval_loader, n_batches=16)

    noise_floor = 1.0 / np.sqrt(64)
    ceiling = 0.845

    print(f"\n  Overall cosine_sim: {metrics['cosine_sim']:.4f}")
    print(f"  Words evaluated: {metrics['n_words']}")

    print(f"\n  Per-stratum:")
    for k, v in sorted(metrics.items()):
        if k.startswith("sim_"):
            stratum = k[4:]
            status = "✅ signal" if v > noise_floor else "⚡ weak" if v > 0 else "— random"
            bar_len = max(0, int(v / ceiling * 40))
            bar = "█" * bar_len + "░" * (40 - bar_len)
            print(f"    {stratum:12s}: {v:+.4f}  |{bar}|  {status}")

    return metrics


def main():
    parser = argparse.ArgumentParser(description="Analyze basin projector checkpoint")
    parser.add_argument("checkpoint", type=str, help="Path to checkpoint dir")
    parser.add_argument("--eval", action="store_true",
                        help="Run fresh evaluation (slow, loads model + tokenizer)")
    parser.add_argument("--gen-interval", type=int, default=25,
                        help="Tournament interval used during training")
    args = parser.parse_args()

    checkpoint_dir = Path(args.checkpoint)
    state_path = checkpoint_dir / "state.json"

    if not state_path.exists():
        print(f"Error: {state_path} not found")
        sys.exit(1)

    with open(state_path) as f:
        state = json.load(f)

    step = state.get("step", 0)
    epoch = state.get("epoch", 0)

    print(f"{'=' * 60}")
    print(f"  Basin Projector Checkpoint Analysis")
    print(f"  Step: {step}  |  Epoch: {epoch}")
    print(f"  Path: {checkpoint_dir}")
    print(f"{'=' * 60}")

    # Loss analysis
    losses = state.get("train_losses_last100", [])
    if losses:
        analyze_losses(losses, gen_interval=args.gen_interval)
    else:
        print("\n  No loss history in checkpoint.")

    # Evolution analysis
    analyze_evolution(state)

    # Metrics from checkpoint
    analyze_metrics(state)

    # Fresh eval if requested
    if args.eval:
        run_eval(checkpoint_dir)

    print(f"\n{'=' * 60}")


if __name__ == "__main__":
    main()
