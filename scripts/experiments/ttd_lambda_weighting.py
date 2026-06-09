#!/usr/bin/env python3
# register: causal
"""Audit #11 — GTSM finite-budget weighting: does layer-targeted λ(l)
beat uniform α=5.0 at MATCHED training budget?

REGISTER: causal (interventional/functional). The claim predicts an
intervention outcome — at matched finite budget, spiking the dense SM
loss weight λ(l) on weak/causal layers yields lower HELD-OUT PPL ratio
and higher worst-layer cosine than uniform weighting. The instrument is
a controlled A/B at matched budget (same steps/lr/batch/Σw mass), N
seeds, held-out eval on a DISJOINT shard (s208 contamination lesson),
plus a placement-specificity null.

Claim sources:
  - gtsm-search-space.md   (Prop F.6: finite-budget weighting is load-bearing)
  - tsp-trajectory-distillation.md (TTD-regression = "exactly audit #11";
    causal caveat: weight the upstream causal layer L22-26, not the
    max-divergence layer — s196 "peak damage at L28, not L26")
  - score-matching-compression.md ("α=5.0 is load-bearing, not arbitrary")

Suspected null mechanism (registry #11): cosine is already scale-
invariant — it may absorb what F.6's ‖·‖_D weighting provides. A null
result sharpens the ‖·‖_D-proxy claim.

ARMS (all at matched budget — only the weight profile differs;
Σ_l w(l) = n_layers in every arm, so total loss mass is matched):

  uniform          w(l) = 1                      (v3b reproduction, the control)
  causal-named     spike on L22-26               (registry's F.6+TSP prediction:
                                                  upstream causal bind-prep layers)
  divergence-auto  spike on bottom-k layers by   (TTD auto-detection; per the v3b
                   measured post-sieve cosine     result JSON these are L15-17
                   (pre-pass, fixed across runs)  SWEET-zone, NOT L22-26)
  anti-targeted    spike on top-k BEST layers    (placement-specificity NULL: if
                                                  this also "wins", the spike effect
                                                  is generic, not placement)

PAIRING: batch order is RandomState(step) — identical across arms and
seeds → arms are paired per seed; variance isolated to (seeded) LoRA
init + MPS kernel nondeterminism.

EVAL (two sets, both reported):
  eval_near  shard_00000 @ offset n_cal*seq_len*2   (v3b-comparable, 1.44x ref)
  eval_held  shard_00001, STRATIFIED across shard   (clean held-out, disjoint shard;
                                                     contiguous@0 hit a spam doc)
Verdict is read on eval_held (s208: contaminated/near eval can invert).

Usage:
  uv run python scripts/experiments/ttd_lambda_weighting.py \
    --model Qwen/Qwen3-8B --device mps --steps 150 --seeds 0,1,2

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
import torch
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(_SCRIPT_DIR))
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

# v3b parity: reuse the exact s198 pipeline components
from score_matching_compression import (  # noqa: E402
    FrozenLowRankLinear,
    FrozenSieveLinear,
    SieveWithLoRA,
    cache_teacher_states,
    get_layers,
    load_sequences,
    log,
    measure_facts,
    measure_ppl_tokens,
    svd_factorize,
)

SHARD_DIR = Path.home() / "data" / "fractal-bitnet" / "shards-qwen3"
SIEVE_LAYERS = [*range(1, 27), 32, 33, 34]
NAMED_CAUSAL_SET = [22, 23, 24, 25, 26]  # registry #11 / TSP causal caveat


def load_sequences_strided(shard_path, n_sequences, seq_len=128,
                           n_strides=16):
    """Held-out eval sampler: draw sequences at evenly spaced offsets
    across the WHOLE shard instead of one contiguous region.

    Rationale (found in smoke test): shard_00001 @ offset 0 lands in a
    spam/word-salad document (teacher PPL 300-800). A single contiguous
    region is document-correlated → noisy, unrepresentative held-out.
    Stratified sampling averages over ~n_strides distinct documents.
    """
    data_len = len(np.load(shard_path, mmap_mode="r"))
    per_stride = max(1, n_sequences // n_strides)
    offsets = np.linspace(0, data_len - seq_len * per_stride * 4,
                          n_strides).astype(int)
    sequences = []
    for off in offsets:
        sequences.extend(load_sequences(
            shard_path, per_stride, seq_len=seq_len, offset=int(off)))
        if len(sequences) >= n_sequences:
            break
    return sequences[:n_sequences]


# ══════════════════════════════════════════════════════════════
# Weighted score matching loss (the only delta vs v3b)
# ══════════════════════════════════════════════════════════════

def compute_weighted_sm_loss(model, input_ids, teacher_states,
                             layer_weights, device):
    """v3b's dense SM loss with a per-layer weight profile w(l).

    score_loss = (1/L) Σ_l w(l) · (1 − cos(Δθ_l, Δ*_l))

    With Σ_l w(l) = L this reduces EXACTLY to v3b's unweighted mean
    when w(l) = 1 ∀l (budget-matched by construction).
    """
    layers = get_layers(model)
    n_layers = len(layers)

    student_states = {}

    def pre_hook(mod, args):
        h = args[0] if isinstance(args, tuple) else args
        student_states[-1] = h[0]

    hooks = [layers[0].register_forward_pre_hook(pre_hook)]

    def make_hook(li):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            student_states[li] = h[0]
        return hook_fn

    for li in range(n_layers):
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    labels = input_ids.clone()
    out = model(input_ids=input_ids, labels=labels)
    ce_loss = out.loss

    for h in hooks:
        h.remove()

    score_loss = torch.tensor(0.0, device=device)
    per_layer_cos = {}
    n_score_layers = 0

    for li in range(n_layers):
        if li not in student_states:
            continue
        if li > 0 and (li - 1) not in student_states:
            continue
        if li == 0 and -1 not in student_states:
            continue

        s_prev = student_states[-1] if li == 0 else student_states[li - 1]
        s_curr = student_states[li]
        s_delta = s_curr.float() - s_prev.float()

        t_delta = (teacher_states[li + 1].float().to(device)
                   - teacher_states[li].float().to(device))

        cos = F.cosine_similarity(s_delta, t_delta, dim=-1)
        mean_cos = cos.mean()
        w = float(layer_weights.get(li, 1.0))
        score_loss = score_loss + w * (1.0 - mean_cos)
        per_layer_cos[li] = mean_cos.item()
        n_score_layers += 1

    if n_score_layers > 0:
        score_loss = score_loss / n_score_layers

    return ce_loss, score_loss, per_layer_cos


def make_weight_profile(n_layers, target_set, spike):
    """w(l) = spike on targets, 1 elsewhere, normalized to Σw = n_layers."""
    w = np.ones(n_layers, dtype=np.float64)
    for li in target_set:
        w[li] = spike
    w *= n_layers / w.sum()
    return {li: float(w[li]) for li in range(n_layers)}


# ══════════════════════════════════════════════════════════════
# Model build (v3b parity, seeded)
# ══════════════════════════════════════════════════════════════

def build_sieved_model(args, seed):
    torch.manual_seed(seed)
    np.random.seed(seed)
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    model.eval()
    layers = get_layers(model)

    # L0 SVD r=750
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        base = FrozenLowRankLinear(A.to(args.device), B.to(args.device))
        lora = SieveWithLoRA(base, rank=args.lora_rank).to(args.device)
        setattr(mlp0, pname, lora)

    # Sieve + LoRA
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            base = FrozenSieveLinear(proj.weight, zero_rate=args.zero_rate)
            lora = SieveWithLoRA(base.to(args.device),
                                 rank=args.lora_rank).to(args.device)
            setattr(mlp, pname, lora)

    trainable = []
    for li in [0, *SIEVE_LAYERS]:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if isinstance(mod, SieveWithLoRA):
                trainable.extend([mod.lora_A, mod.lora_B])
    return model, trainable


def free_model(model):
    del model
    gc.collect()
    if torch.backends.mps.is_available():
        torch.mps.empty_cache()


# ══════════════════════════════════════════════════════════════
# Init cosine measurement (target-set detection pre-pass)
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def measure_init_cosines(model, cal_sequences, teacher_cache, device,
                         n_seqs=8):
    """Per-layer cos(Δ_sieve, Δ_teacher) of the pure sieve (LoRA at 0)."""
    accum = {}
    for idx in range(min(n_seqs, len(teacher_cache))):
        input_ids = cal_sequences[idx].unsqueeze(0).to(device)
        _, _, plc = compute_weighted_sm_loss(
            model, input_ids, teacher_cache[idx], {}, device)
        for li, c in plc.items():
            accum.setdefault(li, []).append(c)
    return {li: float(np.mean(v)) for li, v in accum.items()}


# ══════════════════════════════════════════════════════════════
# One training run (one arm × one seed)
# ══════════════════════════════════════════════════════════════

def run_arm(args, arm_name, layer_weights, seed, cal_sequences,
            eval_near, eval_held, teacher_cache, tokenizer):
    log(f"\n{'═'*70}")
    log(f"  RUN: arm={arm_name} seed={seed}")
    spiked = sorted([li for li, w in layer_weights.items() if w > 1.001])
    log(f"  spiked layers: {spiked if spiked else 'none (uniform)'}")
    log(f"{'═'*70}")

    t_run = time.time()
    model, trainable = build_sieved_model(args, seed)

    base_ppl_near = measure_ppl_tokens(model, eval_near, args.device)
    # NOTE: base PPLs measured on the SIEVED model would be wrong; the
    # sieve is installed already, so baseline PPLs come from the caller.

    sieve_ppl_near = base_ppl_near  # this IS the sieve (LoRA at zero)
    sieve_ppl_held = measure_ppl_tokens(model, eval_held, args.device)
    log(f"  sieve PPL near={sieve_ppl_near:.2f} held={sieve_ppl_held:.2f}")

    optimizer = torch.optim.Adam(trainable, lr=args.lr)
    model.train()
    n_teacher = len(teacher_cache)
    n_cal = len(cal_sequences)
    history = []

    for step in range(args.steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)  # PAIRED across arms/seeds
        batch_indices = rng.choice(n_cal, args.batch_size, replace=False)

        step_ce, step_sm, step_tokens, step_sm_count = 0.0, 0.0, 0, 0
        step_cos = []

        for idx in batch_indices:
            input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)
            if idx < n_teacher:
                ce_loss, score_loss, plc = compute_weighted_sm_loss(
                    model, input_ids, teacher_cache[idx],
                    layer_weights, args.device)
                loss = ce_loss + args.alpha * score_loss
                step_sm += score_loss.item()
                step_sm_count += 1
                if plc:
                    step_cos.append(np.mean(list(plc.values())))
            else:
                labels = input_ids.clone()
                out = model(input_ids=input_ids, labels=labels)
                ce_loss = out.loss
                loss = ce_loss

            if not (torch.isnan(loss) or torch.isinf(loss)):
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            torch.nn.utils.clip_grad_norm_(trainable, max_norm=1.0)
            optimizer.step()

        if (step + 1) % 10 == 0 or step == 0:
            avg_ce = step_ce / max(step_tokens, 1)
            avg_sm = step_sm / max(step_sm_count, 1)
            mc = float(np.mean(step_cos)) if step_cos else 0.0
            log(f"    [{arm_name} s{seed}] step {step+1:>3d}: "
                f"CE={avg_ce:.4f} SM={avg_sm:.4f} cos={mc:.4f} "
                f"({time.time()-t_run:.0f}s)")
            history.append({"step": step + 1, "ce": round(avg_ce, 4),
                            "score": round(avg_sm, 4),
                            "mean_cos": round(mc, 4)})

    model.eval()
    final_ppl_near = measure_ppl_tokens(model, eval_near, args.device)
    final_ppl_held = measure_ppl_tokens(model, eval_held, args.device)
    facts, total_facts = measure_facts(model, tokenizer, args.device)

    # final per-layer cosine, averaged over a few sequences (not just 1)
    final_cos = measure_init_cosines(
        model, cal_sequences, teacher_cache, args.device, n_seqs=8)

    sieved_set = {0, *SIEVE_LAYERS}
    sieved_cos = {li: c for li, c in final_cos.items() if li in sieved_set}
    worst_li = min(sieved_cos, key=sieved_cos.get)

    record = {
        "arm": arm_name,
        "seed": seed,
        "spiked_layers": spiked,
        "layer_weights": {str(k): round(v, 4)
                          for k, v in layer_weights.items()},
        "sieve_ppl_near": sieve_ppl_near,
        "sieve_ppl_held": sieve_ppl_held,
        "final_ppl_near": final_ppl_near,
        "final_ppl_held": final_ppl_held,
        "final_facts": facts,
        "total_facts": total_facts,
        "final_per_layer_cos": {str(k): round(v, 4)
                                for k, v in final_cos.items()},
        "worst_sieved_layer": worst_li,
        "worst_sieved_cos": round(sieved_cos[worst_li], 4),
        "mean_sieved_cos": round(float(np.mean(list(sieved_cos.values()))), 4),
        "elapsed_s": round(time.time() - t_run, 1),
        "history": history,
    }
    free_model(model)
    return record


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="mps")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--lora-rank", type=int, default=4)
    p.add_argument("--steps", type=int, default=150,
                   help="matched budget; v3b's best eval was step 150")
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--alpha", type=float, default=5.0)
    p.add_argument("--spike", type=float, default=8.0,
                   help="raw spike weight before Σw normalization")
    p.add_argument("--spike-k", type=int, default=5,
                   help="size of auto/anti target sets")
    p.add_argument("--seeds", type=str, default="0,1,2")
    p.add_argument("--arms", type=str,
                   default="uniform,causal-named,divergence-auto,anti-targeted")
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--teacher-cache-file", type=str, default="")
    args = p.parse_args()

    seeds = [int(s) for s in args.seeds.split(",")]
    arms = args.arms.split(",")

    out_dir = _PROJECT_ROOT / "results" / "ttd-lambda-weighting"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")
    out_path = out_dir / f"{slug}.json"

    log(f"\n{'='*70}")
    log("  AUDIT #11 — TTD λ(l) WEIGHTING vs UNIFORM α (register: causal)")
    log(f"{'='*70}")
    log(f"  model={args.model} device={args.device}")
    log(f"  arms={arms} seeds={seeds}")
    log(f"  budget: steps={args.steps} lr={args.lr} batch={args.batch_size} "
        f"alpha={args.alpha} (matched across arms; Σw = n_layers)")
    log(f"  spike={args.spike} (raw, pre-normalization), k={args.spike_k}")

    # ── Data ──────────────────────────────────────────────
    cal_path = SHARD_DIR / "shard_00000.npy"
    held_path = SHARD_DIR / "shard_00001.npy"
    cal_sequences = load_sequences(cal_path, args.n_cal,
                                   seq_len=args.seq_len, offset=0)
    eval_near = load_sequences(cal_path, args.n_eval, seq_len=args.seq_len,
                               offset=args.n_cal * args.seq_len * 2)
    eval_held = load_sequences_strided(held_path, args.n_eval,
                                       seq_len=args.seq_len)
    log(f"  data: {len(cal_sequences)} cal + {len(eval_near)} near-eval "
        f"(shard0) + {len(eval_held)} held-eval (shard1, disjoint)")

    # ── Tokenizer + teacher baseline + teacher cache ──────
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    cache_file = (Path(args.teacher_cache_file) if args.teacher_cache_file
                  else out_dir / (f"{slug}.teacher-cache."
                                  f"{args.n_teacher_cache}x{args.seq_len}"
                                  f".c{args.n_cal}.pt"))

    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading teacher {args.model} ({dtype}) for baseline+cache...")
    teacher = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    teacher.eval()
    n_layers = len(get_layers(teacher))

    base_ppl_near = measure_ppl_tokens(teacher, eval_near, args.device)
    base_ppl_held = measure_ppl_tokens(teacher, eval_held, args.device)
    base_facts, total_facts = measure_facts(teacher, tokenizer, args.device)
    log(f"  teacher baseline: near={base_ppl_near:.2f} "
        f"held={base_ppl_held:.2f} facts={base_facts}/{total_facts}")

    if cache_file.exists():
        log(f"  Loading teacher cache from {cache_file.name}...")
        teacher_cache = torch.load(cache_file, map_location="cpu")
    else:
        log(f"  Caching teacher states ({args.n_teacher_cache} seqs)...")
        t0 = time.time()
        teacher_cache = cache_teacher_states(
            teacher, cal_sequences, args.device,
            max_seqs=args.n_teacher_cache)
        torch.save(teacher_cache, cache_file)
        log(f"  cached in {time.time()-t0:.0f}s → {cache_file.name}")
    free_model(teacher)

    # ── Pre-pass: init cosines → fixed target sets ────────
    log("\n  PRE-PASS: measuring post-sieve init cosines (seed 0)...")
    model0, _ = build_sieved_model(args, seed=0)
    init_cos = measure_init_cosines(
        model0, cal_sequences, teacher_cache, args.device, n_seqs=8)
    free_model(model0)

    candidates = [li for li in [0, *SIEVE_LAYERS] if li in init_cos]
    by_cos = sorted(candidates, key=lambda li: init_cos[li])
    auto_set = sorted(by_cos[:args.spike_k])          # worst = divergence
    anti_set = sorted(by_cos[-args.spike_k:])         # best = null arm
    log(f"  init cosines (sieved layers, worst→best): "
        f"{[(li, round(init_cos[li], 3)) for li in by_cos]}")
    log(f"  divergence-auto set: {auto_set}")
    log(f"  anti-targeted set:   {anti_set}")
    log(f"  causal-named set:    {NAMED_CAUSAL_SET}")

    arm_sets = {
        "uniform": [],
        "causal-named": NAMED_CAUSAL_SET,
        "divergence-auto": auto_set,
        "anti-targeted": anti_set,
    }

    result = {
        "audit": "#11 GTSM finite-budget lambda(l) vs uniform alpha",
        "register": "causal",
        "model": args.model,
        "config": {
            "steps": args.steps, "lr": args.lr, "alpha": args.alpha,
            "batch_size": args.batch_size, "lora_rank": args.lora_rank,
            "zero_rate": args.zero_rate, "spike": args.spike,
            "spike_k": args.spike_k, "n_cal": len(cal_sequences),
            "n_eval": args.n_eval, "seq_len": args.seq_len,
            "n_teacher_cache": args.n_teacher_cache,
            "sieve_layers": SIEVE_LAYERS, "seeds": seeds, "arms": arms,
            "cal_shard": str(cal_path), "held_shard": str(held_path),
        },
        "baseline": {
            "ppl_near": base_ppl_near, "ppl_held": base_ppl_held,
            "facts": base_facts, "total_facts": total_facts,
        },
        "init_cos_postsieve": {str(k): round(v, 4)
                               for k, v in init_cos.items()},
        "arm_target_sets": arm_sets,
        "runs": [],
    }

    def save():
        with open(out_path, "w") as f:
            json.dump(result, f, indent=2)

    save()

    # ── Run matrix (arm-major within seed → partials cover arms) ──
    for seed in seeds:
        for arm in arms:
            weights = make_weight_profile(n_layers, arm_sets[arm],
                                          args.spike)
            rec = run_arm(args, arm, weights, seed, cal_sequences,
                          eval_near, eval_held, teacher_cache, tokenizer)
            rec["final_ratio_near"] = round(
                rec["final_ppl_near"] / base_ppl_near, 4)
            rec["final_ratio_held"] = round(
                rec["final_ppl_held"] / base_ppl_held, 4)
            rec["sieve_ratio_near"] = round(
                rec["sieve_ppl_near"] / base_ppl_near, 4)
            rec["sieve_ratio_held"] = round(
                rec["sieve_ppl_held"] / base_ppl_held, 4)
            result["runs"].append(rec)
            save()
            log(f"\n  ▶ [{arm} s{seed}] FINAL: "
                f"near {rec['final_ratio_near']}x | "
                f"held {rec['final_ratio_held']}x | "
                f"worst-cos L{rec['worst_sieved_layer']}="
                f"{rec['worst_sieved_cos']} | "
                f"facts {rec['final_facts']}/{total_facts}")

    # ── Aggregate ─────────────────────────────────────────
    log(f"\n{'='*70}")
    log("  AGGREGATE (mean ± std over seeds)")
    log(f"{'='*70}")
    agg = {}
    for arm in arms:
        rr = [r for r in result["runs"] if r["arm"] == arm]
        if not rr:
            continue
        held = [r["final_ratio_held"] for r in rr]
        near = [r["final_ratio_near"] for r in rr]
        wc = [r["worst_sieved_cos"] for r in rr]
        mc = [r["mean_sieved_cos"] for r in rr]
        agg[arm] = {
            "n": len(rr),
            "final_ratio_held_mean": round(float(np.mean(held)), 4),
            "final_ratio_held_std": round(float(np.std(held)), 4),
            "final_ratio_near_mean": round(float(np.mean(near)), 4),
            "final_ratio_near_std": round(float(np.std(near)), 4),
            "worst_cos_mean": round(float(np.mean(wc)), 4),
            "mean_cos_mean": round(float(np.mean(mc)), 4),
        }
        log(f"  {arm:>16s}: held {agg[arm]['final_ratio_held_mean']}x "
            f"± {agg[arm]['final_ratio_held_std']} | "
            f"near {agg[arm]['final_ratio_near_mean']}x "
            f"± {agg[arm]['final_ratio_near_std']} | "
            f"worst-cos {agg[arm]['worst_cos_mean']}")
    result["aggregate"] = agg
    save()
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
