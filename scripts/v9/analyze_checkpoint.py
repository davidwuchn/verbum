"""
Analyze basin projector checkpoint(s) — diagnose training health.

Single checkpoint:
    uv run python scripts/v9/analyze_checkpoint.py checkpoints/basin/step_001000

All checkpoints (progress curve):
    uv run python scripts/v9/analyze_checkpoint.py checkpoints/basin/

With fresh eval (slow, loads model):
    uv run python scripts/v9/analyze_checkpoint.py checkpoints/basin/step_001000 --eval

License: MIT
"""

import argparse
import json
import sys
from pathlib import Path

import numpy as np

NOISE_FLOOR = 1.0 / np.sqrt(64)  # ~0.125
CEILING = 0.845  # PCA reconstruction limit at d=64
STRATA = ["sexpr", "math", "mixed", "prose", "complex", "behavioral"]


def load_state(checkpoint_dir: Path) -> dict:
    """Load state.json from a checkpoint."""
    with open(checkpoint_dir / "state.json") as f:
        return json.load(f)


def analyze_losses(losses: list[float], gen_interval: int = 25):
    """Analyze loss trajectory for sawtooth pattern."""
    losses = np.array(losses)
    n = len(losses)

    print(f"\n{'═' * 60}")
    print(f"  Loss Analysis ({n} values)")
    print(f"{'═' * 60}")

    print(f"\n  Overall: min={losses.min():.4f}  max={losses.max():.4f}  "
          f"mean={losses.mean():.4f}  std={losses.std():.4f}")

    # Trend
    mid = n // 2
    first_half = losses[:mid].mean()
    second_half = losses[mid:].mean()
    trend = "↓ improving" if second_half < first_half else "↑ worsening" if second_half > first_half else "→ flat"
    print(f"  Trend: first_half={first_half:.4f}  second_half={second_half:.4f}  {trend}")

    # Sawtooth detection
    post_tournament = []
    between = []
    for i in range(n):
        phase = i % gen_interval
        if phase < 3:
            post_tournament.append(losses[i])
        elif phase >= 10:
            between.append(losses[i])

    if post_tournament and between:
        post_mean = np.mean(post_tournament)
        between_mean = np.mean(between)
        spike = post_mean - between_mean
        print(f"\n  Sawtooth (gen_interval={gen_interval}):")
        print(f"    Post-tournament (0-2 steps): {post_mean:.4f}  (n={len(post_tournament)})")
        print(f"    Between (10+ steps):         {between_mean:.4f}  (n={len(between)})")
        print(f"    Spike: {spike:+.4f}", end="  ")
        if spike > 0.02:
            print("⚠️  SAWTOOTH — consider --gen-interval 50")
        elif spike > 0.005:
            print("⚡ mild, acceptable")
        else:
            print("✅ no sawtooth")

    # Volatility
    if n >= 10:
        rolling_std = np.array([losses[max(0, i-5):i+1].std() for i in range(5, n)])
        vol = rolling_std.mean()
        print(f"\n  Volatility: {vol:.4f}", end="  ")
        if vol > 0.05:
            print("⚠️  high")
        elif vol > 0.02:
            print("⚡ moderate (normal early)")
        else:
            print("✅ stable")


def analyze_evolution(state: dict):
    """Analyze evolutionary tournament health."""
    total_gens = state.get("total_gens", 0)
    total_accepted = state.get("total_accepted", 0)
    base_pct = state.get("base_pct", 0)
    strategy_wins = state.get("strategy_wins", {})

    print(f"\n{'═' * 60}")
    print(f"  Evolution")
    print(f"{'═' * 60}")

    if total_gens == 0:
        print("  No tournaments yet.")
        return

    accept_rate = total_accepted / total_gens
    print(f"\n  Tournaments: {total_gens}  |  Accepted: {total_accepted} ({accept_rate:.0%})  |  base_pct: {base_pct:.4f}")

    if strategy_wins:
        print(f"  Strategy wins (recent 100):")
        for s in ["explorer", "aggressive", "standard", "conservative", "rejected"]:
            count = strategy_wins.get(s, 0)
            total = sum(strategy_wins.values())
            pct = count / max(1, total) * 100
            bar = "█" * int(pct / 2.5)
            print(f"    {s:14s}: {count:3d} ({pct:4.1f}%)  {bar}")

    if accept_rate > 0.9:
        print(f"\n  ⚠️  Very high acceptance — topology easily improved, gamma may lag")
    elif accept_rate > 0.5:
        print(f"\n  ✅ Healthy — evolution finding improvements")
    elif accept_rate > 0.2:
        print(f"\n  ✅ Moderate — topology stabilizing")
    else:
        print(f"\n  ⚡ Low acceptance — topology may be near optimal (or gen_interval too short)")


def analyze_eval_metrics(state: dict):
    """Analyze per-stratum eval metrics from checkpoint."""
    metrics = state.get("eval_metrics", state.get("final_metrics", {}))
    if not metrics:
        print(f"\n  ❌ No eval metrics saved in checkpoint. Re-run training with updated code.")
        return

    print(f"\n{'═' * 60}")
    print(f"  Basin Similarity (saved at checkpoint time)")
    print(f"{'═' * 60}")

    cosine_sim = metrics.get("cosine_sim", 0)
    n_words = metrics.get("n_words", "?")
    print(f"\n  Overall: {cosine_sim:.4f}  ({cosine_sim/CEILING:.0%} of ceiling)  |  words: {n_words}")
    print(f"  Noise floor: {NOISE_FLOOR:.3f}  |  Ceiling: {CEILING:.3f}")

    print(f"\n  Per-stratum:")
    for s in STRATA:
        k = f"sim_{s}"
        v = metrics.get(k, None)
        if v is None:
            continue
        bar_len = max(0, int(v / CEILING * 40))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        if v > NOISE_FLOOR:
            status = "✅ signal"
        elif v > 0:
            status = "⚡ weak"
        elif v > -NOISE_FLOOR:
            status = "— noise"
        else:
            status = "⚠️  anti"
        print(f"    {s:12s}: {v:+.4f}  |{bar}|  {status}")


def analyze_ternary(state: dict):
    """Analyze ternary topology statistics."""
    ternary_stats = state.get("ternary_stats", {})
    if not ternary_stats:
        return

    print(f"\n{'═' * 60}")
    print(f"  Ternary Topology")
    print(f"{'═' * 60}")

    print(f"\n  {'Module':<35s} {'Sparsity':>8s} {'Pos':>6s} {'Neg':>6s} {'γ_mean':>7s} {'γ_std':>7s}")
    print(f"  {'─' * 35} {'─' * 8} {'─' * 6} {'─' * 6} {'─' * 7} {'─' * 7}")

    for path in sorted(ternary_stats.keys()):
        s = ternary_stats[path]
        sp = s.get("sparsity", 0)
        pos = s.get("pos_frac", 0)
        neg = s.get("neg_frac", 0)
        gm = s.get("gamma_mean", 0)
        gs = s.get("gamma_std", 0)
        print(f"  {path:<35s} {sp:7.1%} {pos:5.1%} {neg:5.1%} {gm:7.4f} {gs:7.4f}")


def multi_checkpoint_progress(checkpoint_root: Path):
    """Compare metrics across all checkpoints."""
    step_dirs = sorted(checkpoint_root.glob("step_*"))
    if not step_dirs:
        print(f"  No checkpoints found in {checkpoint_root}")
        return

    print(f"\n{'═' * 60}")
    print(f"  Progress Across {len(step_dirs)} Checkpoints")
    print(f"{'═' * 60}")

    # Header
    header = f"  {'Step':>6s} │ {'Loss':>7s} │ {'Sim':>6s} │"
    for s in STRATA:
        header += f" {s[:5]:>5s} │"
    header += f" {'Acc%':>5s} │ {'Gens':>5s}"
    print(f"\n{header}")
    print(f"  {'─' * 6}─┼─{'─' * 7}─┼─{'─' * 6}─┼" + "─" * (7 * len(STRATA) + 1) + f"┼─{'─' * 5}─┼─{'─' * 5}")

    for step_dir in step_dirs:
        state_path = step_dir / "state.json"
        if not state_path.exists():
            continue
        state = load_state(step_dir)
        step = state.get("step", 0)
        loss = state.get("train_loss_recent", 0)
        metrics = state.get("eval_metrics", state.get("final_metrics", {}))
        sim = metrics.get("cosine_sim", 0) if metrics else 0
        gens = state.get("total_gens", 0)
        accepted = state.get("total_accepted", 0)
        acc_pct = (accepted / max(1, gens)) * 100

        row = f"  {step:6d} │ {loss:7.4f} │ {sim:+5.3f} │"
        for s in STRATA:
            v = metrics.get(f"sim_{s}", 0) if metrics else 0
            row += f" {v:+4.2f} │"
        row += f" {acc_pct:4.0f}% │ {gens:5d}"
        print(row)

    print()

    # Also show the learning curve if we have enough points
    if len(step_dirs) >= 3:
        steps = []
        sims = {s: [] for s in STRATA}
        overall = []

        for step_dir in step_dirs:
            state = load_state(step_dir)
            steps.append(state.get("step", 0))
            metrics = state.get("eval_metrics", state.get("final_metrics", {}))
            overall.append(metrics.get("cosine_sim", 0) if metrics else 0)
            for s in STRATA:
                sims[s].append(metrics.get(f"sim_{s}", 0) if metrics else 0)

        # Trend assessment
        print(f"  Trends (first → last):")
        for s in STRATA:
            vals = sims[s]
            if len(vals) >= 2:
                delta = vals[-1] - vals[0]
                arrow = "↑" if delta > 0.01 else "↓" if delta < -0.01 else "→"
                print(f"    {s:12s}: {vals[0]:+.3f} → {vals[-1]:+.3f}  ({delta:+.3f}) {arrow}")


def run_fresh_eval(checkpoint_dir: Path):
    """Load model and run evaluation (slow)."""
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

    print(f"\n{'═' * 60}")
    print(f"  Fresh Evaluation (loading model...)")
    print(f"{'═' * 60}")

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

    print(f"\n  Overall cosine_sim: {metrics['cosine_sim']:.4f}  |  Words: {metrics['n_words']}")
    print(f"\n  Per-stratum:")
    for s in STRATA:
        k = f"sim_{s}"
        v = metrics.get(k, 0)
        bar_len = max(0, int(v / CEILING * 40))
        bar = "█" * bar_len + "░" * (40 - bar_len)
        status = "✅" if v > NOISE_FLOOR else "⚡" if v > 0 else "—" if v > -NOISE_FLOOR else "⚠️"
        print(f"    {s:12s}: {v:+.4f}  |{bar}|  {status}")


def main():
    parser = argparse.ArgumentParser(description="Analyze basin projector checkpoint(s)")
    parser.add_argument("checkpoint", type=str,
                        help="Path to checkpoint dir or parent dir for multi-checkpoint")
    parser.add_argument("--eval", action="store_true",
                        help="Run fresh evaluation (slow)")
    parser.add_argument("--gen-interval", type=int, default=None,
                        help="Tournament interval (auto-detected from checkpoint)")
    args = parser.parse_args()

    checkpoint_path = Path(args.checkpoint)

    # Multi-checkpoint mode: path is the parent dir
    if not (checkpoint_path / "state.json").exists():
        step_dirs = sorted(checkpoint_path.glob("step_*"))
        if step_dirs:
            multi_checkpoint_progress(checkpoint_path)

            # Also analyze the latest checkpoint in detail
            latest = step_dirs[-1]
            print(f"\n{'═' * 60}")
            print(f"  Latest: {latest.name}")
            print(f"{'═' * 60}")
            state = load_state(latest)
            gen_interval = args.gen_interval or state.get("gen_interval", 25)
            losses = state.get("train_losses_last100", [])
            if losses:
                analyze_losses(losses, gen_interval)
            analyze_evolution(state)
            analyze_eval_metrics(state)
            analyze_ternary(state)

            if args.eval:
                run_fresh_eval(latest)
            return
        else:
            print(f"No checkpoints found in {checkpoint_path}")
            sys.exit(1)

    # Single checkpoint mode
    state = load_state(checkpoint_path)
    step = state.get("step", 0)
    epoch = state.get("epoch", 0)
    gen_interval = args.gen_interval or state.get("gen_interval", 25)

    print(f"{'═' * 60}")
    print(f"  Basin Projector — Step {step}  |  Epoch {epoch}")
    print(f"  {checkpoint_path}")
    print(f"{'═' * 60}")

    losses = state.get("train_losses_last100", [])
    if losses:
        analyze_losses(losses, gen_interval)
    analyze_evolution(state)
    analyze_eval_metrics(state)
    analyze_ternary(state)

    if args.eval:
        run_fresh_eval(checkpoint_path)

    print()


if __name__ == "__main__":
    main()
