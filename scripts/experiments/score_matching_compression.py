#!/usr/bin/env python3
"""Score Matching Compression — CGTSM-inspired loss for sieve correction.

The CGTSM theorem (Def 3.1, Thm 3.2) says: matching per-layer
transformations (scores) everywhere along the trajectory is necessary
and sufficient for path matching. This changes two things from v2:

1. LOSS: Match per-layer transformations (scores), not just CE output.
   Score_l = h_{l+1} - h_l (the residual update at each layer).
   Dense: all 36 layers, not 6 boundaries.

2. CORRECTIONS: LoRA on FFN weight matrices (per-weight), not
   rank-32 vectors in the residual stream (per-activation). The
   sieve error is full-rank in weight space (r90=2970) — activation
   corrections can't address it.

Architecture:
  Round 0: Crystal sieve (same)
  Corrections: LoRA (rank-4) on each sieved FFN projection
  Loss: L_CE + α × Σ_l (1 - cos(Δ_student_l, Δ_teacher_l))
    where Δ_l = h_{l+1} - h_l is the per-layer residual update

Usage:
  uv run python scripts/experiments/score_matching_compression.py \
    --model Qwen/Qwen3-8B --device mps

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
import torch.nn as nn
import torch.nn.functional as F
from transformers import AutoModelForCausalLM, AutoTokenizer

_SCRIPT_DIR = Path(__file__).resolve().parent
_PROJECT_ROOT = _SCRIPT_DIR.parent.parent
if str(_PROJECT_ROOT / "src") not in sys.path:
    sys.path.insert(0, str(_PROJECT_ROOT / "src"))

SHARD_DIR = Path.home() / "data" / "fractal-bitnet" / "shards-qwen3"
EOD_ID = 151643


# ══════════════════════════════════════════════════════════════
# Data
# ══════════════════════════════════════════════════════════════

def load_sequences(shard_path, n_sequences, seq_len=128, offset=0):
    data = np.load(shard_path)
    data = data[offset:]
    sequences = []
    pos = 0
    while len(sequences) < n_sequences and pos + seq_len < len(data):
        chunk = data[pos:pos + seq_len]
        eod_positions = np.where(chunk == EOD_ID)[0]
        if len(eod_positions) == 0:
            sequences.append(torch.tensor(chunk, dtype=torch.long))
            pos += seq_len
        else:
            pos += int(eod_positions[0]) + 1
    return sequences


FACT_PROMPTS = [
    {"prompt": "The capital of France is", "expected": "Paris"},
    {"prompt": "The capital of Japan is", "expected": "Tokyo"},
    {"prompt": "Water boils at", "expected": "100"},
    {"prompt": "The speed of light is approximately",
     "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was",
     "expected": "1945"},
    {"prompt": "The chemical symbol for gold is",
     "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to",
     "expected": "3.14"},
    {"prompt": "The Great Wall of China is located in",
     "expected": "China"},
    {"prompt": "The human body has", "expected": "206"},
    {"prompt": "Einstein's famous equation is E equals",
     "expected": "mc"},
    {"prompt": "The freezing point of water in Celsius is",
     "expected": "0"},
    {"prompt": "The currency of the United Kingdom is the",
     "expected": "pound"},
]


# ══════════════════════════════════════════════════════════════
# Helpers
# ══════════════════════════════════════════════════════════════

def log(msg=""):
    print(msg, file=sys.stderr, flush=True)
    print(msg, flush=True)


def get_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError(f"Can't find layers in {type(model)}")


def measure_ppl_tokens(model, sequences, device):
    model.eval()
    total_loss = 0.0
    total_tokens = 0
    with torch.no_grad():
        for seq in sequences:
            input_ids = seq.unsqueeze(0).to(device)
            labels = input_ids.clone()
            out = model(input_ids=input_ids, labels=labels)
            n = labels.numel()
            total_loss += out.loss.item() * n
            total_tokens += n
    return float(np.exp(total_loss / total_tokens))


def generate_text(model, tokenizer, prompt, device, max_new=30):
    model.eval()
    enc = tokenizer(prompt, return_tensors="pt")
    enc = {k: v.to(device) for k, v in enc.items()}
    with torch.no_grad():
        out = model.generate(**enc, max_new_tokens=max_new,
                             do_sample=False, temperature=1.0,
                             pad_token_id=tokenizer.pad_token_id)
    return tokenizer.decode(out[0][enc["input_ids"].shape[1]:],
                            skip_special_tokens=True)


def measure_facts(model, tokenizer, device):
    model.eval()
    correct = 0
    for fp in FACT_PROMPTS:
        gen = generate_text(model, tokenizer, fp["prompt"], device)
        if fp["expected"].lower() in gen.lower():
            correct += 1
    return correct, len(FACT_PROMPTS)


# ══════════════════════════════════════════════════════════════
# Crystal Sieve (Round 0)
# ══════════════════════════════════════════════════════════════

class FrozenSieveLinear(nn.Module):
    def __init__(self, weight, zero_rate=0.5):
        super().__init__()
        W = weight.detach().float().cpu()
        abs_W = W.abs()
        if zero_rate > 0:
            flat = abs_W.flatten()
            if flat.numel() > 10_000_000:
                idx = torch.randperm(flat.numel())[:5_000_000]
                threshold = torch.quantile(flat[idx], zero_rate)
            else:
                threshold = torch.quantile(flat, zero_rate)
            mask = (abs_W >= threshold).float()
        else:
            mask = torch.ones_like(W)
        W_sieve = torch.sign(W) * abs_W * mask
        self.register_buffer("W_sieve", W_sieve.half())
        self.out_features, self.in_features = W.shape

    def forward(self, x):
        out = x.float() @ self.W_sieve.float().T
        return out.clamp(-65000, 65000).to(x.dtype)


class FrozenLowRankLinear(nn.Module):
    def __init__(self, A, B):
        super().__init__()
        self.register_buffer("A", A)
        self.register_buffer("B", B)
        self.out_features = A.shape[0]
        self.in_features = B.shape[1]

    def forward(self, x):
        out = x.float() @ self.B.T @ self.A.T
        return out.clamp(-65000, 65000).to(x.dtype)


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# LoRA Correction (per-weight, not per-activation)
# ══════════════════════════════════════════════════════════════

class SieveWithLoRA(nn.Module):
    """Sieved linear + LoRA correction in weight space.

    W_eff = W_sieve + A @ B   (A: out×rank, B: rank×in)
    Init: A random small, B zeros → starts as pure sieve.
    """

    def __init__(self, base_module, rank=4):
        super().__init__()
        self.base = base_module
        # Determine dimensions
        if isinstance(base_module, FrozenSieveLinear):
            out_f = base_module.out_features
            in_f = base_module.in_features
        elif isinstance(base_module, FrozenLowRankLinear):
            out_f = base_module.out_features
            in_f = base_module.in_features
        else:
            out_f, in_f = base_module.weight.shape

        # LoRA: A random, B zeros → correction starts at zero
        self.lora_A = nn.Parameter(
            torch.randn(out_f, rank) * 0.01)
        self.lora_B = nn.Parameter(
            torch.zeros(rank, in_f))
        self.rank = rank

    def forward(self, x):
        base_out = self.base(x)
        lora_out = x.float() @ self.lora_B.T @ self.lora_A.T
        return (base_out.float() + lora_out).to(x.dtype)

    @property
    def n_params(self):
        return self.lora_A.numel() + self.lora_B.numel()


# ══════════════════════════════════════════════════════════════
# Teacher state caching
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, sequences, device, max_seqs=32):
    """Cache per-layer hidden states from the teacher (pre-sieve).

    Returns: list of tensors, each (n_layers+1, seq_len, d_model)
             Index 0 = embedding output, index l+1 = output of layer l.
    """
    layers = get_layers(model)
    n_layers = len(layers)
    all_states = []

    for seq in sequences[:max_seqs]:
        input_ids = seq.unsqueeze(0).to(device)
        layer_states = {}
        hooks = []

        # Capture input to first layer (embedding output)
        def embed_hook(mod, args):
            # pre_hook receives (module, args) — args is the input tuple
            h = args[0] if isinstance(args, tuple) else args
            layer_states[-1] = h[0].detach().cpu().half()

        hooks.append(layers[0].register_forward_pre_hook(embed_hook))

        # Capture output of each layer
        def make_hook(li):
            def hook_fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                layer_states[li] = h[0].detach().cpu().half()
            return hook_fn

        for li in range(n_layers):
            hooks.append(layers[li].register_forward_hook(make_hook(li)))

        model(input_ids=input_ids)

        for h in hooks:
            h.remove()

        # Stack: (n_layers+1, seq_len, d_model)
        # Index 0 = pre-layer-0, index l+1 = post-layer-l
        state_list = [layer_states[-1]]  # embedding output
        for li in range(n_layers):
            state_list.append(layer_states[li])
        stacked = torch.stack(state_list, dim=0)  # (n_layers+1, seq, d)
        all_states.append(stacked)

    return all_states


# ══════════════════════════════════════════════════════════════
# Score matching loss
# ══════════════════════════════════════════════════════════════

def compute_score_matching_loss(model, input_ids, teacher_states,
                                sieve_layers, device):
    """Compute dense score matching loss across all layers.

    Score at layer l: Δ_l = h_{l+1} - h_l (residual update)
    Loss: Σ_l (1 - cos(Δ_student_l, Δ_teacher_l))

    Returns: (ce_loss, score_loss, per_layer_cos dict)
    """
    layers = get_layers(model)
    n_layers = len(layers)

    # Capture student hidden states at every layer
    student_states = {}

    def pre_hook(mod, args):
        h = args[0] if isinstance(args, tuple) else args
        student_states[-1] = h[0]  # keep on device, keep grad

    hooks = [layers[0].register_forward_pre_hook(pre_hook)]

    def make_hook(li):
        def hook_fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            student_states[li] = h[0]  # keep grad
        return hook_fn

    for li in range(n_layers):
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    # Forward pass
    labels = input_ids.clone()
    out = model(input_ids=input_ids, labels=labels)
    ce_loss = out.loss

    for h in hooks:
        h.remove()

    # Compute score matching loss
    # teacher_states: (n_layers+1, seq, d) — on CPU, float16
    score_loss = torch.tensor(0.0, device=device)
    per_layer_cos = {}
    n_score_layers = 0

    for li in range(n_layers):
        if li not in student_states or (li - 1) not in student_states and li > 0:
            continue
        if li == 0 and -1 not in student_states:
            continue

        # Student score (residual update)
        s_prev = student_states[-1] if li == 0 else student_states[li - 1]
        s_curr = student_states[li]
        s_delta = s_curr.float() - s_prev.float()  # (seq, d)

        # Teacher score
        t_delta = (teacher_states[li + 1].float().to(device)
                   - teacher_states[li].float().to(device))  # (seq, d)

        # Cosine loss: 1 - cos(student_delta, teacher_delta)
        # Average over sequence positions
        cos = F.cosine_similarity(s_delta, t_delta, dim=-1)  # (seq,)
        mean_cos = cos.mean()
        layer_loss = 1.0 - mean_cos

        score_loss = score_loss + layer_loss
        per_layer_cos[li] = mean_cos.item()
        n_score_layers += 1

    if n_score_layers > 0:
        score_loss = score_loss / n_score_layers

    return ce_loss, score_loss, per_layer_cos


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--lora-rank", type=int, default=4)
    p.add_argument("--steps", type=int, default=200)
    p.add_argument("--lr", type=float, default=1e-4)
    p.add_argument("--alpha", type=float, default=5.0,
                   help="Weight of score matching loss vs CE")
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128,
                   help="Sequences to cache teacher states for (SM loss)")
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--shard-dir", type=str,
                   default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  SCORE MATCHING COMPRESSION — CGTSM-inspired sieve correction")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  LoRA rank: {args.lora_rank}")
    log(f"  Steps: {args.steps}")
    log(f"  α (score/CE balance): {args.alpha}")
    log(f"  Calibration: {args.n_cal} seq × {args.seq_len} tok"
        f" (batch={args.batch_size})")
    log(f"  Teacher cache: {args.n_teacher_cache} seq"
        f" (SM+CE), {args.n_cal - args.n_teacher_cache} CE-only")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path.name}...")
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len, offset=0)
    eval_offset = args.n_cal * args.seq_len * 2
    eval_sequences = load_sequences(
        shard_path, args.n_eval, seq_len=args.seq_len, offset=eval_offset)
    log(f"  Loaded {len(cal_sequences)} cal + {len(eval_sequences)} eval")

    # ── Load model ────────────────────────────────────────
    dtype = (torch.float16
             if any(s in args.model for s in ["8B", "14B", "32B"])
             else torch.float32)
    log(f"\n  Loading {args.model} ({dtype})...")
    model = AutoModelForCausalLM.from_pretrained(
        args.model, torch_dtype=dtype, device_map=args.device,
        attn_implementation="eager")
    tokenizer = AutoTokenizer.from_pretrained(args.model)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model.eval()
    d_model = model.config.hidden_size
    log(f"  d_model={d_model}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    base_facts, total_facts = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{total_facts}")

    # ── Cache teacher states ──────────────────────────────
    log(f"\n  Caching teacher states ({args.n_teacher_cache} sequences,"
        f" all {len(get_layers(model))} layers)...")
    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, cal_sequences, args.device,
        max_seqs=args.n_teacher_cache)
    elapsed = time.time() - t0
    n_layers = len(get_layers(model))
    mem_mb = sum(t.nelement() * t.element_size()
                 for t in teacher_cache) / 1e6
    log(f"  Cached {len(teacher_cache)} × {n_layers+1} layers"
        f" ({mem_mb:.0f} MB, {elapsed:.0f}s)")

    # ═══════════════════════════════════════════════════════
    # Install crystal sieve (Round 0)
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  ROUND 0: CRYSTAL SIEVE + LoRA")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0 SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        base = FrozenLowRankLinear(A.to(args.device), B.to(args.device))
        lora = SieveWithLoRA(base, rank=args.lora_rank).to(args.device)
        setattr(mlp0, pname, lora)

    # Sieve + LoRA on remaining layers
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            base = FrozenSieveLinear(proj.weight,
                                     zero_rate=args.zero_rate)
            lora = SieveWithLoRA(base.to(args.device),
                                 rank=args.lora_rank).to(args.device)
            setattr(mlp, pname, lora)

    # Count params
    trainable_params = []
    total_lora_params = 0
    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            mod = getattr(mlp, pname)
            if isinstance(mod, SieveWithLoRA):
                trainable_params.extend([mod.lora_A, mod.lora_B])
                total_lora_params += mod.n_params

    log(f"  Sieve + LoRA installed on {len(SIEVE_LAYERS) + 1} layers")
    log(f"  LoRA rank: {args.lora_rank}")
    log(f"  Total LoRA params: {total_lora_params:,}")

    # Post-sieve measurement (LoRA starts at zero → same as sieve)
    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ═══════════════════════════════════════════════════════
    # Train with score matching loss
    # ═══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  TRAINING: CE + α × SCORE MATCHING")
    log(f"  {args.steps} steps, lr={args.lr}, α={args.alpha}")
    log(f"{'═'*70}")

    optimizer = torch.optim.Adam(trainable_params, lr=args.lr)
    model.train()
    history = []
    eval_history = []
    n_teacher = len(teacher_cache)
    n_cal = len(cal_sequences)
    t0 = time.time()

    for step in range(args.steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)

        # Sample a batch: mix teacher-cached (SM+CE) and uncached (CE-only)
        batch_indices = rng.choice(n_cal, args.batch_size, replace=False)

        step_ce = 0.0
        step_sm = 0.0
        step_tokens = 0
        step_sm_count = 0
        step_cos_accum = []

        for idx in batch_indices:
            input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)

            if idx < n_teacher:
                # This sequence has teacher cache → SM + CE
                teacher_states = teacher_cache[idx]
                ce_loss, score_loss, per_layer_cos = \
                    compute_score_matching_loss(
                        model, input_ids, teacher_states,
                        SIEVE_LAYERS, args.device)
                loss = ce_loss + args.alpha * score_loss
                step_sm += score_loss.item()
                step_sm_count += 1
                if per_layer_cos:
                    step_cos_accum.append(
                        np.mean(list(per_layer_cos.values())))
            else:
                # CE only (dolma diversity)
                labels = input_ids.clone()
                out = model(input_ids=input_ids, labels=labels)
                ce_loss = out.loss
                loss = ce_loss

            if not (torch.isnan(loss) or torch.isinf(loss)):
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            torch.nn.utils.clip_grad_norm_(trainable_params, max_norm=1.0)
            optimizer.step()

        avg_ce = step_ce / max(step_tokens, 1)
        avg_sm = step_sm / max(step_sm_count, 1)
        mean_cos = float(np.mean(step_cos_accum)) if step_cos_accum else 0.0

        record = {
            "step": step + 1,
            "ce": round(avg_ce, 4),
            "score": round(avg_sm, 4),
            "mean_cos": round(mean_cos, 4),
        }
        history.append(record)

        if (step + 1) % 10 == 0 or step == 0:
            elapsed = time.time() - t0
            sm_str = (f" SM={avg_sm:.4f} cos={mean_cos:.4f}"
                      if step_sm_count > 0 else "")
            log(f"    step {step+1:>3d}: CE={avg_ce:.4f}{sm_str}"
                f" ({elapsed:.0f}s)")

        # Periodic eval
        if (step + 1) % args.eval_every == 0:
            eval_ppl = measure_ppl_tokens(
                model, eval_sequences, args.device)
            eval_facts, _ = measure_facts(model, tokenizer, args.device)
            ppl_ratio = eval_ppl / base_ppl
            log(f"    ▶ EVAL step {step+1}: PPL={eval_ppl:.2f}"
                f" ({ppl_ratio:.3f}x) facts={eval_facts}/{total_facts}")
            eval_history.append({
                "step": step + 1,
                "ppl": eval_ppl,
                "ppl_ratio": round(ppl_ratio, 4),
                "facts": eval_facts,
            })
            model.train()

    model.eval()

    # Final eval
    final_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    final_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Final PPL: {final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts: {final_facts}/{total_facts}")

    # Final per-layer cosine (diagnostic)
    log(f"\n  Final per-layer score cosine:")
    idx = 0
    input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)
    teacher_states = teacher_cache[idx]
    with torch.no_grad():
        _, _, final_cos = compute_score_matching_loss(
            model, input_ids, teacher_states, SIEVE_LAYERS, args.device)

    zone_map = {}
    for li in range(n_layers):
        if li == 0: zone_map[li] = "L0-SVD"
        elif li <= 6: zone_map[li] = "EXPAND"
        elif li <= 12: zone_map[li] = "ORTHO"
        elif li <= 21: zone_map[li] = "SWEET"
        elif li <= 26: zone_map[li] = "BIND-P"
        elif li <= 31: zone_map[li] = "BIND"
        elif li <= 34: zone_map[li] = "LATE"
        else: zone_map[li] = "OUT"

    log(f"  {'Layer':>6s}  {'cos':>6s}  {'Zone':>8s}")
    log(f"  {'─'*6}  {'─'*6}  {'─'*8}")
    for li in sorted(final_cos.keys()):
        zone = zone_map.get(li, "?")
        log(f"  L{li:>3d}   {final_cos[li]:>6.4f}  {zone:>8s}")

    # ═══════════════════════════════════════════════════════
    # Summary
    # ═══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:   PPL={base_ppl:.2f}  facts={base_facts}/{total_facts}")
    log(f"  Sieve only: PPL={sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)")
    log(f"  Final:      PPL={final_ppl:.2f} ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}")
    log(f"  LoRA params: {total_lora_params:,}")
    log(f"  Improvement: {sieve_ppl:.2f} → {final_ppl:.2f}"
        f" ({(1 - final_ppl/sieve_ppl)*100:.1f}% reduction)")

    # Compare to v2
    log(f"\n  vs v2 (residual boosting, 2.1M params):")
    log(f"    v2: 25.50 → 18.59 (27.1% reduction, 1.65x base)")
    log(f"    v3: {sieve_ppl:.2f} → {final_ppl:.2f}"
        f" ({(1 - final_ppl/sieve_ppl)*100:.1f}% reduction,"
        f" {final_ppl/base_ppl:.2f}x base)")

    # ── Save ──────────────────────────────────────────────
    out_dir = _PROJECT_ROOT / "results" / "score-matching"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v3-score-matching",
        "config": {
            "lora_rank": args.lora_rank,
            "steps": args.steps,
            "lr": args.lr,
            "alpha": args.alpha,
            "n_cal": len(cal_sequences),
            "n_eval": len(eval_sequences),
            "n_teacher_cache": len(teacher_cache),
            "seq_len": args.seq_len,
            "batch_size": args.batch_size,
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl,
        "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl,
        "sieve_ratio": round(sieve_ppl / base_ppl, 4),
        "final_ppl": final_ppl,
        "final_ratio": round(final_ppl / base_ppl, 4),
        "final_facts": final_facts,
        "total_lora_params": total_lora_params,
        "eval_history": eval_history,
        "final_per_layer_cos": {str(k): round(v, 4)
                                for k, v in final_cos.items()},
        "loss_history": history,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
