"""Gradient-Zero Convergence Map — Where does GD deposit near-zero gradients?

HYPOTHESIS: Gradient descent deposits near-zero gradients at weight positions
that correspond to irreducible computation (converged crystal) or noise floor
(positions that should be zero in ternary).

The 2×2 of (gradient_magnitude × weight_magnitude) should reveal:
  - LOW grad + LOW weight  = noise floor → safe to zero in ternary
  - LOW grad + HIGH weight = converged irreducible → keep as ±1
  - HIGH grad + LOW weight = GD trying to grow into this dimension
  - HIGH grad + HIGH weight = active knowledge, still being shaped

KEY METRIC: Spearman correlation between |grad| and |weight| per tensor.
  positive → grad and weight aligned (high weight = high grad = active)
  negative → inverse (high weight = low grad = converged)
  zero     → independent axes (median split is meaningless)

Uses diverse data: fact recall probes + compile examples + hardcoded prompts,
with sequences up to 256 tokens for richer gradient signal.

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/gradient_zero_map.py
    uv run python scripts/experiments/gradient_zero_map.py --model Qwen/Qwen3-14B

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "gradient-zero-map"
DATA_DIR = Path(__file__).parent.parent.parent / "data"
PROBES_DIR = Path(__file__).parent.parent.parent / "probes"

# Diverse prompts spanning many domains — supplemented by data files.
HARDCODED_PROMPTS = [
    # Factual knowledge
    "The capital of France is Paris, which is located along the Seine river in northern France.",
    "The chemical symbol for gold is Au, derived from the Latin word aurum meaning shining dawn.",
    "Albert Einstein was born in Ulm, Germany in 1879 and developed the theory of special relativity.",
    "The speed of light is approximately 299,792,458 meters per second in a vacuum.",
    "Water boils at a temperature of 100 degrees Celsius at standard atmospheric pressure.",
    "DNA stands for deoxyribonucleic acid, the molecule that carries genetic instructions.",
    "Photosynthesis converts sunlight, water, and carbon dioxide into glucose and oxygen.",
    "The Great Wall of China stretches over 13,000 miles across northern China.",
    "The currency used in Japan is the Japanese yen, symbolized by the character ¥.",
    "Jupiter is the largest planet in our solar system with a mass of 1.898 × 10^27 kg.",
    # Mathematics
    "The derivative of sin(x) is cos(x), and the derivative of cos(x) is negative sin(x).",
    "The Pythagorean theorem states that in a right triangle, a² + b² = c² where c is the hypotenuse.",
    "The integral of 1/x dx is ln|x| + C, where C is the constant of integration.",
    "A prime number is a natural number greater than 1 that has no positive divisors other than 1 and itself.",
    "The Fibonacci sequence is defined recursively: F(n) = F(n-1) + F(n-2), with F(0)=0 and F(1)=1.",
    "Euler's identity e^(iπ) + 1 = 0 connects five fundamental mathematical constants.",
    "The determinant of a 2×2 matrix [[a,b],[c,d]] is ad - bc.",
    "A function f is continuous at point c if the limit as x approaches c equals f(c).",
    "The natural logarithm of e is exactly 1, since ln(e) = log_e(e) = 1.",
    "In set theory, the union of A and B contains all elements in either A or B or both.",
    # Code
    "def fibonacci(n):\n    if n <= 1:\n        return n\n    return fibonacci(n-1) + fibonacci(n-2)",
    "import numpy as np\narr = np.array([1, 2, 3, 4, 5])\nprint(arr.mean(), arr.std())",
    "class Node:\n    def __init__(self, val, left=None, right=None):\n        self.val = val\n        self.left = left\n        self.right = right",
    "SELECT name, age FROM users WHERE age > 18 ORDER BY name ASC LIMIT 100;",
    "fn main() {\n    let mut v: Vec<i32> = vec![1, 2, 3];\n    v.push(4);\n    println!(\"{:?}\", v);\n}",
    "const app = express();\napp.get('/api/users', (req, res) => {\n    res.json({ users: [] });\n});",
    "docker build -t myapp:latest . && docker run -p 8080:8080 myapp:latest",
    "git log --oneline --graph --all | head -20",
    # Natural language / narrative
    "Once upon a time in a small village nestled in the mountains, there lived an old clockmaker who could hear the ticking of every clock in town.",
    "The industrial revolution transformed society by mechanizing production, urbanizing populations, and creating new social classes.",
    "Democracy requires the active participation of citizens through voting, civic engagement, and holding elected officials accountable.",
    "Climate change affects ecosystems through rising temperatures, altered precipitation patterns, ocean acidification, and habitat loss.",
    "The history of music reflects the cultural values of each era, from Gregorian chants to jazz to electronic dance music.",
    "Ancient civilizations developed writing systems to record transactions, preserve knowledge, and communicate across distances.",
    "Education serves as the foundation for individual growth, economic development, and social cohesion in modern societies.",
    "The ocean covers approximately seventy percent of Earth's surface and contains an estimated 97 percent of the planet's water.",
    # Science
    "Quantum entanglement occurs when two particles become correlated such that measuring one instantly determines the state of the other.",
    "Natural selection favors organisms that are best adapted to their environment, driving evolution over millions of years.",
    "The second law of thermodynamics states that entropy in an isolated system always increases over time.",
    "Plate tectonics explains how the Earth's lithosphere is divided into plates that move, collide, and separate.",
    "Neurons communicate through electrical impulses called action potentials and chemical signals called neurotransmitters.",
    "Black holes form when massive stars exhaust their nuclear fuel and collapse under their own gravitational force.",
    "CRISPR-Cas9 is a gene editing tool that allows precise modifications to DNA sequences in living organisms.",
    # Philosophy
    "The trolley problem asks whether it is morally permissible to divert a trolley to kill one person instead of five.",
    "Descartes' cogito ergo sum establishes the existence of the thinking self as the one indubitable truth.",
    "Kant's categorical imperative: act only according to that maxim which you can will to be a universal law.",
    # Multilingual
    "La revolución francesa de 1789 transformó radicalmente la estructura política y social de Francia.",
    "日本の首都は東京で、世界最大の都市圏の一つとして約3700万人が暮らしています。",
    "Der kategorische Imperativ von Kant besagt, dass man nur nach derjenigen Maxime handeln soll.",
    "L'intelligence artificielle est un domaine de l'informatique qui vise à créer des systèmes capables de raisonner.",
    # Lambda / formal
    "(λx. λy. x y) (λz. z) reduces to (λy. (λz. z) y) which further reduces to (λy. y) = I",
    "The Y combinator Y = λf. (λx. f (x x)) (λx. f (x x)) enables recursion without self-reference.",
    "Church numerals: 0 = λf.λx.x, 1 = λf.λx.f x, 2 = λf.λx.f(f x), succ = λn.λf.λx.f(n f x)",
    "S K K x = K x (K x) = x, proving that S K K is extensionally equal to the identity combinator I.",
    # Dialogue
    "User: What is the weather like today?\nAssistant: I don't have access to real-time weather data.",
    "Question: How does a neural network learn?\nAnswer: Through backpropagation of gradients and iterative weight updates.",
    # Technical
    "The TCP/IP protocol stack has four layers: link, internet, transport, and application.",
    "A transformer architecture uses multi-head self-attention to model dependencies regardless of distance.",
    "The halting problem proves that no algorithm can determine whether an arbitrary program will halt.",
    "Gradient descent minimizes a loss function by iteratively moving in the direction of steepest descent.",
    "Batch normalization normalizes layer inputs to reduce internal covariate shift during training.",
    "The attention mechanism computes a weighted sum: Attention(Q,K,V) = softmax(QK^T/√d_k)V.",
    "MapReduce processes large datasets by mapping each element independently, then reducing the results.",
    "The CAP theorem states that a distributed system cannot simultaneously guarantee consistency, availability, and partition tolerance.",
]


def log(msg: str):
    print(msg, file=sys.stderr, flush=True)


def bimodality_coeff(x: np.ndarray) -> float:
    """Sarle's bimodality coefficient: (skew^2 + 1) / kurtosis_full.
    b > 0.555 (uniform) suggests bimodality. Matches gd_frozen_basis.py."""
    n = x.size
    if n < 4:
        return 0.0
    d = x - x.mean()
    s2 = (d * d).mean()
    if s2 <= 0:
        return 0.0
    g1 = (d ** 3).mean() / (s2 ** 1.5)
    g2 = (d ** 4).mean() / (s2 ** 2) - 3.0
    corr = 3.0 * (n - 1) ** 2 / ((n - 2) * (n - 3))
    return float((g1 * g1 + 1.0) / (g2 + corr))


def load_all_texts() -> list[str]:
    """Gather texts from all available sources: hardcoded + data files + probes."""
    texts = list(HARDCODED_PROMPTS)

    # Compile training data
    compile_path = DATA_DIR / "compile-train.jsonl"
    if compile_path.exists():
        with open(compile_path) as f:
            for line in f:
                d = json.loads(line)
                # Concatenate input + output for longer sequences
                texts.append(f"{d['input']} → {d['output']}")
        log(f"  Loaded {compile_path.name}: {len(texts) - len(HARDCODED_PROMPTS)} examples")

    # Fact recall probes
    probes_path = PROBES_DIR / "fact_recall_extended.json"
    if probes_path.exists():
        with open(probes_path) as f:
            probes = json.load(f)["probes"]
            for p in probes:
                texts.append(f"{p['prompt']} {p['expected']}")
        log(f"  Loaded {probes_path.name}: {len(probes)} probes")

    return texts


def create_batches(
    tokenizer,
    texts: list[str],
    batch_size: int = 4,
    max_length: int = 256,
) -> list[dict]:
    """Tokenize texts into padded batches."""
    batches = []
    for i in range(0, len(texts), batch_size):
        batch_texts = texts[i : i + batch_size]
        batch_texts = [t if t.strip() else "The" for t in batch_texts]
        encoded = tokenizer(
            batch_texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=max_length,
        )
        batches.append(encoded)
    return batches


def collect_gradient_stats(
    model,
    tokenizer,
    batches: list[dict],
    device: str,
    target_modules: list[str] | None = None,
) -> dict:
    """Run forward+backward on each batch, accumulate gradient statistics.

    Tracks per-element: sum|∇w|, sum(∇w²), sum(sign(∇w)), count.
    """
    # Select exactly the params we flagged requires_grad (respects --target-modules
    # and --layer-stride set in main); falls back to name-match if none flagged.
    target_params: dict[str, torch.nn.Parameter] = {
        name: param for name, param in model.named_parameters()
        if param.requires_grad and "weight" in name and param.ndim == 2}
    if not target_params:
        if target_modules is None:
            target_modules = ["gate_proj", "up_proj", "down_proj"]
        for name, param in model.named_parameters():
            if any(m in name for m in target_modules) and "weight" in name:
                target_params[name] = param

    log(f"  Tracking {len(target_params)} tensors across {len(batches)} batches")

    # Accumulators on CPU
    stats: dict[str, dict] = {}
    for name, param in target_params.items():
        stats[name] = {
            "sum_abs_grad": torch.zeros(param.shape, dtype=torch.float32),
            "sum_sq_grad": torch.zeros(param.shape, dtype=torch.float32),
            "sum_sign_grad": torch.zeros(param.shape, dtype=torch.float32),
            "weight_magnitude": param.data.abs().float().cpu(),
            "n_batches": 0,
        }

    for batch_idx, encoded in enumerate(batches):
        if (batch_idx + 1) % 25 == 0 or batch_idx == 0:
            log(f"    Batch {batch_idx + 1}/{len(batches)}")

        input_ids = encoded["input_ids"].to(device)
        attention_mask = encoded["attention_mask"].to(device)
        labels = input_ids.clone()
        labels[attention_mask == 0] = -100

        model.zero_grad()
        loss = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels).loss
        loss.backward()

        for name, param in target_params.items():
            if param.grad is not None:
                g = param.grad.float().cpu()
                stats[name]["sum_abs_grad"].add_(g.abs())
                stats[name]["sum_sq_grad"].add_(g.square())
                stats[name]["sum_sign_grad"].add_(g.sign())
                stats[name]["n_batches"] += 1

        model.zero_grad(set_to_none=True)
        if (batch_idx + 1) % 25 == 0:
            gc.collect()
            if device == "mps":
                torch.mps.empty_cache()

    return stats


def analyze(stats: dict) -> dict:
    """Compute per-tensor summary statistics including correlation."""
    from scipy.stats import spearmanr

    # Expected sign consistency for pure noise with n trials
    n_example = next(iter(stats.values()))["n_batches"]
    noise_floor_sc = np.sqrt(2 / (np.pi * n_example))
    log(f"  Sign consistency noise floor (n={n_example}): {noise_floor_sc:.4f}")

    results = {}
    for name, s in stats.items():
        n = s["n_batches"]
        if n == 0:
            continue

        mean_abs_grad = (s["sum_abs_grad"] / n).numpy()
        sign_consistency = (s["sum_sign_grad"] / n).abs().numpy()
        weight_mag = s["weight_magnitude"].numpy()

        g_flat = mean_abs_grad.ravel()
        w_flat = weight_mag.ravel()
        sc_flat = sign_consistency.ravel()

        # Subsample index for correlations
        rng = np.random.default_rng(42)
        n_sub = min(100_000, len(g_flat))
        idx = rng.choice(len(g_flat), n_sub, replace=False) if len(g_flat) > n_sub else np.arange(len(g_flat))

        # Three correlations: the full picture
        rho_gw, _ = spearmanr(g_flat[idx], w_flat[idx])   # grad vs weight
        rho_sw, _ = spearmanr(sc_flat[idx], w_flat[idx])   # sign_cons vs weight
        rho_sg, _ = spearmanr(sc_flat[idx], g_flat[idx])   # sign_cons vs grad

        # Sign consistency distribution
        sc_quantiles = np.percentile(sc_flat, [5, 10, 25, 50, 75, 90, 95])

        # Oscillator analysis: positions near noise floor sign consistency
        # These are the "destructive interference = zero" candidates
        oscillator_thresh = noise_floor_sc * 2   # within 2× of noise floor
        directional_thresh = 0.3                  # strongly directional

        is_oscillator = sc_flat <= oscillator_thresh
        is_directional = sc_flat >= directional_thresh

        total = len(g_flat)
        n_osc = is_oscillator.sum()
        n_dir = is_directional.sum()

        # For oscillators: what's their weight magnitude?
        osc_w_mean = float(w_flat[is_oscillator].mean()) if n_osc > 0 else 0.0
        osc_g_mean = float(g_flat[is_oscillator].mean()) if n_osc > 0 else 0.0
        dir_w_mean = float(w_flat[is_directional].mean()) if n_dir > 0 else 0.0
        dir_g_mean = float(g_flat[is_directional].mean()) if n_dir > 0 else 0.0

        # The three-way classification:
        # 1. OSCILLATOR + low weight = noise floor → ZERO (strongest signal)
        # 2. OSCILLATOR + high weight = destructive interference → ZERO (s167 insight)
        # 3. DIRECTIONAL + high weight = still reducing → KEEP
        # 4. DIRECTIONAL + low weight = growing → MONITOR
        w_median = np.median(w_flat)

        osc_lo_w = is_oscillator & (w_flat <= w_median)   # oscillating, small weight → zero
        osc_hi_w = is_oscillator & (w_flat > w_median)    # oscillating, big weight → zero (interference)
        dir_hi_w = is_directional & (w_flat > w_median)   # directional, big weight → still reducing
        dir_lo_w = is_directional & (w_flat <= w_median)  # directional, small weight → growing

        # Quadrant analysis (kept for continuity)
        g_lo = np.percentile(g_flat, 25)
        g_hi = np.percentile(g_flat, 75)
        w_lo = np.percentile(w_flat, 25)
        w_hi = np.percentile(w_flat, 75)
        zero_candidate = (g_flat <= g_lo) & (w_flat <= w_lo)
        converged = (g_flat <= g_lo) & (w_flat >= w_hi)

        # Bimodality of the gradient field (does it split high|near-zero?)
        bimod = bimodality_coeff(np.log(g_flat + 1e-30))

        results[name] = {
            # Correlations
            "rho_grad_weight": float(rho_gw),
            "bimod_log_grad": float(bimod),
            "rho_signcons_weight": float(rho_sw),
            "rho_signcons_grad": float(rho_sg),
            # Means
            "mean_abs_grad": float(g_flat.mean()),
            "mean_weight_mag": float(w_flat.mean()),
            "mean_sign_consistency": float(sc_flat.mean()),
            "median_sign_consistency": float(np.median(sc_flat)),
            # Sign consistency distribution
            "sc_quantiles": {f"p{p}": float(v) for p, v in zip([5,10,25,50,75,90,95], sc_quantiles)},
            # Oscillator analysis
            "oscillator_pct": float(n_osc / total * 100),
            "oscillator_mean_weight": osc_w_mean,
            "oscillator_mean_grad": osc_g_mean,
            "directional_pct": float(n_dir / total * 100),
            "directional_mean_weight": dir_w_mean,
            "directional_mean_grad": dir_g_mean,
            # Three-way classification
            "osc_low_weight_pct": float(osc_lo_w.sum() / total * 100),
            "osc_high_weight_pct": float(osc_hi_w.sum() / total * 100),
            "dir_high_weight_pct": float(dir_hi_w.sum() / total * 100),
            "dir_low_weight_pct": float(dir_lo_w.sum() / total * 100),
        }

        # --- Overlap analysis: oscillators vs magnitude zeros ---
        # Method A: magnitude bottom-30% (the heuristic we know works from s166-167)
        mag_thresh_30 = np.percentile(w_flat, 30)
        mag_zeros_30 = w_flat <= mag_thresh_30
        oscillators = sc_flat <= oscillator_thresh

        # Jaccard overlap
        intersection = (mag_zeros_30 & oscillators).sum()
        union = (mag_zeros_30 | oscillators).sum()
        jaccard = float(intersection / union) if union > 0 else 0.0

        # Conditional overlaps
        p_osc_given_mag = float(intersection / mag_zeros_30.sum()) if mag_zeros_30.any() else 0.0
        p_mag_given_osc = float(intersection / oscillators.sum()) if oscillators.any() else 0.0

        # What fraction of oscillators are in the top-30% by weight?
        mag_top_30 = w_flat >= np.percentile(w_flat, 70)
        osc_and_top = (oscillators & mag_top_30).sum()
        p_top_given_osc = float(osc_and_top / oscillators.sum()) if oscillators.any() else 0.0

        # Agreement/disagreement
        both_zero = mag_zeros_30 & oscillators
        mag_only = mag_zeros_30 & ~oscillators
        osc_only = oscillators & ~mag_zeros_30
        neither = ~mag_zeros_30 & ~oscillators

        # Combined score: |w| × sign_consistency
        combined_score = w_flat * (sc_flat + 0.01)
        combined_thresh_30 = np.percentile(combined_score, 30)
        combined_zeros = combined_score <= combined_thresh_30
        combined_vs_osc_jaccard = float(
            (combined_zeros & oscillators).sum() / (combined_zeros | oscillators).sum()
        ) if (combined_zeros | oscillators).any() else 0.0
        combined_vs_mag_jaccard = float(
            (combined_zeros & mag_zeros_30).sum() / (combined_zeros | mag_zeros_30).sum()
        ) if (combined_zeros | mag_zeros_30).any() else 0.0

        results[name].update({
            "overlap_jaccard": jaccard,
            "p_osc_given_mag_zero": p_osc_given_mag,
            "p_mag_zero_given_osc": p_mag_given_osc,
            "p_mag_top30_given_osc": p_top_given_osc,
            "both_zero_pct": float(both_zero.sum() / total * 100),
            "mag_only_pct": float(mag_only.sum() / total * 100),
            "osc_only_pct": float(osc_only.sum() / total * 100),
            "neither_pct": float(neither.sum() / total * 100),
            "combined_vs_osc_jaccard": combined_vs_osc_jaccard,
            "combined_vs_mag_jaccard": combined_vs_mag_jaccard,
        })

    return results


def parse_layer_module(name: str) -> tuple[int | None, str | None]:
    """Extract layer index and module type from parameter name."""
    parts = name.split(".")
    layer_idx = None
    module_type = None
    for i, p in enumerate(parts):
        if p == "layers" and i + 1 < len(parts):
            try:
                layer_idx = int(parts[i + 1])
            except ValueError:
                pass
        if p in ("gate_proj", "up_proj", "down_proj"):
            module_type = p
    return layer_idx, module_type


def print_results(results: dict):
    """Print a concise, readable summary."""
    by_layer: dict[int, list] = defaultdict(list)
    for name, r in results.items():
        layer_idx, module_type = parse_layer_module(name)
        if layer_idx is not None and module_type is not None:
            by_layer[layer_idx].append((module_type, r))

    # --- Table 1: Correlations ---
    log("\n" + "=" * 120)
    log("TABLE 1: THREE CORRELATIONS PER LAYER")
    log("  ρ(g,w) = grad mag vs weight mag")
    log("  ρ(s,w) = sign consistency vs weight mag  (+ = consistent grads on big weights)")
    log("  ρ(s,g) = sign consistency vs grad mag    (+ = consistent grads on high-grad positions)")
    log("=" * 120)
    log(f"{'Layer':>5} {'Module':>10} {'ρ(g,w)':>8} {'ρ(s,w)':>8} {'ρ(s,g)':>8} "
        f"{'mean_sc':>8} {'med_sc':>8} {'mean|w|':>10}")
    log("-" * 120)

    for layer_idx in sorted(by_layer.keys()):
        for mod, r in sorted(by_layer[layer_idx], key=lambda x: x[0]):
            log(f"{layer_idx:>5} {mod:>10} "
                f"{r['rho_grad_weight']:>+8.4f} {r['rho_signcons_weight']:>+8.4f} {r['rho_signcons_grad']:>+8.4f} "
                f"{r['mean_sign_consistency']:>8.4f} {r['median_sign_consistency']:>8.4f} "
                f"{r['mean_weight_mag']:>10.6f}")

    # --- Table 2: Oscillator classification ---
    log("\n" + "=" * 120)
    log("TABLE 2: OSCILLATOR CLASSIFICATION (sign_cons ≤ 2× noise floor = oscillating)")
    log("  %osc = oscillating positions (gradient pulled both ways = interference)")
    log("  %dir = directional positions (gradient consistently one way = still reducing)")
    log("  osc+lo_w = oscillator with small weight → ZERO (noise floor)")
    log("  osc+hi_w = oscillator with large weight → ZERO (destructive interference)")
    log("  dir+hi_w = directional with large weight → KEEP (still reducing)")
    log("=" * 120)
    log(f"{'Layer':>5} {'Module':>10} {'%osc':>7} {'%dir':>7} "
        f"{'osc+lo_w':>9} {'osc+hi_w':>9} {'dir+hi_w':>9} {'dir+lo_w':>9} "
        f"{'osc_|w|':>9} {'dir_|w|':>9}")
    log("-" * 120)

    for layer_idx in sorted(by_layer.keys()):
        for mod, r in sorted(by_layer[layer_idx], key=lambda x: x[0]):
            log(f"{layer_idx:>5} {mod:>10} "
                f"{r['oscillator_pct']:>6.1f}% {r['directional_pct']:>6.1f}% "
                f"{r['osc_low_weight_pct']:>8.1f}% {r['osc_high_weight_pct']:>8.1f}% "
                f"{r['dir_high_weight_pct']:>8.1f}% {r['dir_low_weight_pct']:>8.1f}% "
                f"{r['oscillator_mean_weight']:>9.5f} {r['directional_mean_weight']:>9.5f}")

    # --- Depth profiles ---
    log("\n" + "=" * 80)
    log("DEPTH PROFILES (averaged across gate/up/down)")
    log("=" * 80)

    log("\n  ρ(grad, weight) — bimodality:")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["rho_grad_weight"] for _, r in by_layer[li]])
        bar = "█" * int(abs(avg) * 150) if avg > 0 else "░" * int(abs(avg) * 150)
        log(f"    L{li:>2}: {avg:+.4f} {bar}")

    log("\n  ρ(sign_cons, weight) — do big weights have consistent grad direction?")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["rho_signcons_weight"] for _, r in by_layer[li]])
        bar = "█" * int(abs(avg) * 150) if avg > 0 else "░" * int(abs(avg) * 150)
        log(f"    L{li:>2}: {avg:+.4f} {bar}")

    log("\n  bimodality coeff of log|grad| (>0.555 = bimodal high|near-zero field):")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["bimod_log_grad"] for _, r in by_layer[li]])
        bar = "█" * int(avg * 100)
        log(f"    L{li:>2}: {avg:.4f} {bar}")

    log("\n  % oscillators by layer:")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["oscillator_pct"] for _, r in by_layer[li]])
        bar = "█" * int(avg * 2)
        log(f"    L{li:>2}: {avg:>5.1f}% {bar}")

    log("\n  % total zero candidates (osc+lo_w + osc+hi_w) by layer:")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["osc_low_weight_pct"] + r["osc_high_weight_pct"] for _, r in by_layer[li]])
        bar = "█" * int(avg * 2)
        log(f"    L{li:>2}: {avg:>5.1f}% {bar}")

    # --- Table 3: Overlap analysis ---
    log("\n" + "=" * 130)
    log("TABLE 3: OVERLAP — oscillator positions vs magnitude-bottom-30% zeros")
    log("  Jaccard = intersection / union (1.0 = identical sets, 0.0 = disjoint)")
    log("  P(osc|mag) = of magnitude zeros, what fraction oscillate?")
    log("  P(mag|osc) = of oscillators, what fraction are small weights?")
    log("  P(top|osc) = of oscillators, what fraction are LARGE weights? (interference zeros)")
    log("  both% = both methods agree → zero  |  mag_only% = mag says zero, grad says keep")
    log("  osc_only% = grad says zero, mag says normal  |  neither% = both say keep")
    log("=" * 130)
    log(f"{'Layer':>5} {'Module':>10} {'Jaccard':>8} {'P(o|m)':>7} {'P(m|o)':>7} {'P(t|o)':>7} "
        f"{'both%':>7} {'mag%':>7} {'osc%':>7} {'neit%':>7} "
        f"{'comb∩osc':>8} {'comb∩mag':>8}")
    log("-" * 130)

    for layer_idx in sorted(by_layer.keys()):
        for mod, r in sorted(by_layer[layer_idx], key=lambda x: x[0]):
            log(f"{layer_idx:>5} {mod:>10} "
                f"{r['overlap_jaccard']:>8.4f} "
                f"{r['p_osc_given_mag_zero']:>7.3f} {r['p_mag_zero_given_osc']:>7.3f} "
                f"{r['p_mag_top30_given_osc']:>7.3f} "
                f"{r['both_zero_pct']:>6.1f}% {r['mag_only_pct']:>6.1f}% "
                f"{r['osc_only_pct']:>6.1f}% {r['neither_pct']:>6.1f}% "
                f"{r['combined_vs_osc_jaccard']:>8.4f} {r['combined_vs_mag_jaccard']:>8.4f}")

    # Depth profile of Jaccard
    log("\n  Jaccard overlap by layer (oscillators ∩ magnitude zeros):")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["overlap_jaccard"] for _, r in by_layer[li]])
        bar = "█" * int(avg * 100)
        log(f"    L{li:>2}: {avg:.4f} {bar}")

    log("\n  P(oscillator | magnitude_zero) by layer — do small weights oscillate?")
    for li in sorted(by_layer.keys()):
        avg = np.mean([r["p_osc_given_mag_zero"] for _, r in by_layer[li]])
        bar = "█" * int(avg * 100)
        log(f"    L{li:>2}: {avg:.3f} {bar}")

    # --- Global summary ---
    log("\n" + "=" * 80)
    log("GLOBAL SUMMARY")
    log("=" * 80)
    all_rho_gw = [r["rho_grad_weight"] for r in results.values()]
    all_bimod = [r["bimod_log_grad"] for r in results.values()]
    log(f"  ρ(grad,weight) [s171 Zone-A bimodality]: {np.mean(all_rho_gw):+.4f} "
        f"± {np.std(all_rho_gw):.4f}  (micro≈0.06, s171-8B Zone-A≈+0.77)")
    log(f"  bimodality coeff log|grad|:              {np.mean(all_bimod):.4f} "
        f"± {np.std(all_bimod):.4f}  (>0.555 = bimodal; micro≈0.33 unimodal)")
    all_osc = [r["oscillator_pct"] for r in results.values()]
    all_jaccard = [r["overlap_jaccard"] for r in results.values()]
    all_both = [r["both_zero_pct"] for r in results.values()]
    all_p_osc_mag = [r["p_osc_given_mag_zero"] for r in results.values()]
    all_p_mag_osc = [r["p_mag_zero_given_osc"] for r in results.values()]
    all_p_top_osc = [r["p_mag_top30_given_osc"] for r in results.values()]
    log(f"  Oscillators: {np.mean(all_osc):.1f}% ± {np.std(all_osc):.1f}%")
    log(f"  Jaccard overlap (osc ∩ mag_zeros): {np.mean(all_jaccard):.4f} ± {np.std(all_jaccard):.4f}")
    log(f"  P(oscillator | magnitude_zero):    {np.mean(all_p_osc_mag):.3f} ± {np.std(all_p_osc_mag):.3f}")
    log(f"  P(magnitude_zero | oscillator):    {np.mean(all_p_mag_osc):.3f} ± {np.std(all_p_mag_osc):.3f}")
    log(f"  P(magnitude_TOP30 | oscillator):   {np.mean(all_p_top_osc):.3f} ± {np.std(all_p_top_osc):.3f}")
    log(f"  Both agree → zero:                 {np.mean(all_both):.1f}%")
    log(f"\n  If Jaccard ≈ 0.5+: methods agree → either signal works")
    log(f"  If Jaccard ≈ 0.2-: methods diverge → they see different zeros")
    log(f"  If P(top|osc) ≈ 0.3: oscillators are weight-independent (confirmed)")
    log(f"  If P(top|osc) >> 0.3: oscillators prefer LARGE weights (interference zeros)")
    log("=" * 80)


def main():
    parser = argparse.ArgumentParser(description="Gradient-Zero Convergence Map")
    parser.add_argument("--model", default="Qwen/Qwen3-8B", help="HuggingFace model name")
    parser.add_argument("--device", default="mps", help="Device (mps, cuda, cpu)")
    parser.add_argument("--dtype", default="float32", choices=["float16", "bfloat16", "float32"])
    parser.add_argument("--batch-size", type=int, default=4, help="Sequences per batch")
    parser.add_argument("--max-length", type=int, default=256, help="Max token length")
    parser.add_argument("--max-batches", type=int, default=None, help="Cap number of batches")
    parser.add_argument("--target-modules", default="gate_proj,up_proj,down_proj",
                        help="Comma-separated FFN submodules to track (memory control)")
    parser.add_argument("--layer-stride", type=int, default=1,
                        help="Track every Nth layer (memory control for large models)")
    args = parser.parse_args()

    dtype_map = {"float16": torch.float16, "bfloat16": torch.bfloat16, "float32": torch.float32}
    dtype = dtype_map[args.dtype]
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"=== Gradient-Zero Convergence Map ===")
    log(f"Model: {args.model}")
    log(f"Device: {args.device}, Dtype: {args.dtype}")

    # --- Load model ---
    log("\nLoading model...")
    t0 = time.time()
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=dtype, device_map=args.device, trust_remote_code=True,
    )
    model.eval()

    # Only compute gradients for the targeted FFN weights (module + layer-stride).
    target_modules = [m.strip() for m in args.target_modules.split(",") if m.strip()]

    def _match(name: str) -> bool:
        if "weight" not in name or not any(m in name for m in target_modules):
            return False
        li, _ = parse_layer_module(name)
        return li is not None and (li % args.layer_stride == 0)

    for name, param in model.named_parameters():
        param.requires_grad_(_match(name))

    n_layers = model.config.num_hidden_layers
    d_ffn = model.config.intermediate_size
    d_model = model.config.hidden_size
    n_grad = sum(p.numel() for p in model.parameters() if p.requires_grad)
    log(f"  Loaded in {time.time() - t0:.1f}s — {n_layers}L, d={d_model}, d_ffn={d_ffn}, grad_params={n_grad/1e6:.0f}M")

    # --- Gather texts and create batches ---
    log("\nGathering texts...")
    texts = load_all_texts()
    np.random.default_rng(42).shuffle(texts)
    log(f"  Total texts: {len(texts)}")

    batches = create_batches(tokenizer, texts, args.batch_size, args.max_length)
    if args.max_batches:
        batches = batches[:args.max_batches]
    log(f"  Batches: {len(batches)} (batch_size={args.batch_size}, max_len={args.max_length})")

    # --- Collect gradients ---
    log("\nCollecting gradient statistics...")
    t0 = time.time()
    with torch.enable_grad():
        stats = collect_gradient_stats(model, tokenizer, batches, args.device)
    log(f"  Done in {time.time() - t0:.1f}s ({(time.time() - t0)/len(batches):.1f}s/batch)")

    # Free model
    del model
    gc.collect()
    if args.device == "mps":
        torch.mps.empty_cache()

    # --- Analyze ---
    log("\nAnalyzing...")
    results = analyze(stats)
    del stats
    gc.collect()

    # --- Save JSON FIRST ---
    safe_model = args.model.replace("/", "_")
    summary_path = RESULTS_DIR / f"summary_{safe_model}.json"
    with open(summary_path, "w") as f:
        json.dump(results, f, indent=2)
    log(f"\nResults saved to {summary_path} ({summary_path.stat().st_size / 1024:.0f} KB)")

    # --- Print ---
    print_results(results)

    log("\nDONE.")


if __name__ == "__main__":
    main()
