#!/usr/bin/env python3
"""Teacher-Guided Routing — Fix topology before training grout.

Hypothesis: Sign correction fails because routing (topology) and
computation (magnitudes) are entangled. MoE literature shows:
  1. Decouple routing from expert training
  2. Use teacher to supervise routing
  3. Stabilize routing FIRST, then train experts

This experiment:
  Phase 0: Install sieve (same as v3b)
  Phase 1: ROUTING — Train lightweight gate classifiers to reproduce
           the teacher's gate firing patterns (mode assignments).
           TSP-style: teacher pattern = golden path, sieve pattern = opponent.
  Phase 2: GROUT — Train LoRA with SM loss (same as v3b), but with
           corrected routing from Phase 1.

The gate classifier per layer is tiny (37K params, session 192 showed
100% accuracy). It replaces the sieved gate_proj's routing decision
while keeping the sieve's magnitude computation.

Compare to v3b (LoRA+SM only) at 1.44x baseline.

Usage:
  uv run python scripts/experiments/teacher_guided_routing.py \
    --model Qwen/Qwen3-8B --device mps

License: MIT
"""

from __future__ import annotations

import argparse
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
# Data + Helpers (shared with v3b)
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
    {"prompt": "The speed of light is approximately", "expected": "300"},
    {"prompt": "The first president of the United States was",
     "expected": "George Washington"},
    {"prompt": "The year World War II ended was", "expected": "1945"},
    {"prompt": "The chemical symbol for gold is", "expected": "Au"},
    {"prompt": "The largest planet in our solar system is",
     "expected": "Jupiter"},
    {"prompt": "The author of Romeo and Juliet is",
     "expected": "Shakespeare"},
    {"prompt": "Pi is approximately equal to", "expected": "3.14"},
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
            if torch.isnan(out.loss) or torch.isinf(out.loss):
                continue
            total_loss += out.loss.item() * labels.numel()
            total_tokens += labels.numel()
    if total_tokens == 0:
        return float('nan')
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


def svd_factorize(weight, rank):
    W = weight.detach().float().cpu()
    U, S, Vt = torch.linalg.svd(W, full_matrices=False)
    r = min(rank, len(S))
    sqrt_S = S[:r].sqrt()
    A = U[:, :r] * sqrt_S.unsqueeze(0)
    B = Vt[:r, :] * sqrt_S.unsqueeze(1)
    return A, B


# ══════════════════════════════════════════════════════════════
# Sieve modules
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


class SieveWithLoRA(nn.Module):
    def __init__(self, base_module, rank=4):
        super().__init__()
        self.base = base_module
        out_f = base_module.out_features
        in_f = base_module.in_features
        self.lora_A = nn.Parameter(torch.randn(out_f, rank) * 0.01)
        self.lora_B = nn.Parameter(torch.zeros(rank, in_f))
        self.rank = rank

    def forward(self, x):
        base_out = self.base(x)
        lora_out = x.float() @ self.lora_B.T @ self.lora_A.T
        return (base_out.float() + lora_out).to(x.dtype)

    @property
    def n_params(self):
        return self.lora_A.numel() + self.lora_B.numel()


# ══════════════════════════════════════════════════════════════
# Phase 1: Teacher-Guided Routing
# ══════════════════════════════════════════════════════════════

class GateCorrector(nn.Module):
    """Lightweight corrector that adjusts the sieved gate_proj output.

    Instead of replacing the gate entirely, this learns a CORRECTION
    to the sieve's gate activations to match the teacher's gate pattern.

    Architecture: small MLP that takes sieve gate output and predicts
    an additive correction to align gate firing with teacher.

    This is the "routing fix" — correcting which neurons fire (topology)
    without changing the magnitude computation (up_proj, down_proj).
    """
    def __init__(self, gate_dim, hidden_dim=256):
        super().__init__()
        # Bottleneck correction: gate_dim → hidden → gate_dim
        # Learns the DELTA between sieve gate and teacher gate
        self.net = nn.Sequential(
            nn.Linear(gate_dim, hidden_dim, bias=False),
            nn.SiLU(),
            nn.Linear(hidden_dim, gate_dim, bias=False),
        )
        # Init near-zero so correction starts small
        with torch.no_grad():
            self.net[0].weight.mul_(0.01)
            self.net[2].weight.mul_(0.01)

    def forward(self, sieve_gate_out):
        correction = self.net(sieve_gate_out.float())
        return sieve_gate_out.float() + correction

    @property
    def n_params(self):
        return sum(p.numel() for p in self.parameters())


class CorrectedGateMLP(nn.Module):
    """MLP with gate correction applied.

    Standard Qwen MLP: hidden = SiLU(gate_proj(x)) * up_proj(x)
                        output = down_proj(hidden)

    Corrected:          gate_out = gate_proj(x)
                        corrected = gate_corrector(gate_out)
                        hidden = SiLU(corrected) * up_proj(x)
                        output = down_proj(hidden)
    """
    def __init__(self, original_mlp, gate_corrector):
        super().__init__()
        self.gate_proj = original_mlp.gate_proj
        self.up_proj = original_mlp.up_proj
        self.down_proj = original_mlp.down_proj
        self.gate_corrector = gate_corrector
        self.act_fn = nn.SiLU()

    def forward(self, x):
        gate_out = self.gate_proj(x)
        corrected_gate = self.gate_corrector(gate_out)
        hidden = self.act_fn(corrected_gate) * self.up_proj(x).float()
        return self.down_proj(hidden.to(x.dtype))


@torch.no_grad()
def collect_gate_targets(model, sequences, device, sieve_layers,
                         max_seqs=64):
    """Run teacher model, collect gate_proj outputs at each sieved layer.

    Returns dict: layer_idx → list of (input_to_mlp, gate_output) pairs.
    We capture what the MLP INPUT is and what the teacher's GATE produces.
    """
    layers = get_layers(model)
    gate_data = {li: [] for li in sieve_layers}

    for seq_idx, seq in enumerate(sequences[:max_seqs]):
        input_ids = seq.unsqueeze(0).to(device)
        hooks = []
        captured = {}

        for li in sieve_layers:
            def make_mlp_hook(layer_idx):
                def fn(mod, args):
                    # MLP pre-hook: args[0] is the input to MLP
                    x = args[0] if isinstance(args, tuple) else args
                    # Compute teacher's gate output
                    gate_out = mod.gate_proj(x)
                    captured[layer_idx] = {
                        'mlp_input': x[0].detach().cpu().half(),
                        'gate_output': gate_out[0].detach().cpu().half(),
                    }
                return fn
            hooks.append(
                layers[li].mlp.register_forward_pre_hook(
                    make_mlp_hook(li)))

        model(input_ids=input_ids)
        for h in hooks:
            h.remove()

        for li in sieve_layers:
            if li in captured:
                gate_data[li].append(captured[li])

        if (seq_idx + 1) % 16 == 0:
            log(f"      Gate targets: {seq_idx+1}/{min(max_seqs, len(sequences))}")

    return gate_data


def train_gate_correctors(model, gate_data, device, sieve_layers,
                          hidden_dim=256, steps=100, lr=1e-3):
    """Phase 1: Train gate correctors to match teacher gate patterns.

    For each sieved layer, train a GateCorrector that adjusts the
    sieve's gate_proj output to match the teacher's gate_proj output.

    Loss: MSE on gate activations (continuous) + BCE on gate signs
    (discrete routing decision).
    """
    layers = get_layers(model)
    correctors = {}
    stats = {}

    for li in sieve_layers:
        if li not in gate_data or not gate_data[li]:
            continue

        gate_dim = gate_data[li][0]['gate_output'].shape[-1]
        corrector = GateCorrector(gate_dim, hidden_dim=hidden_dim).to(device)
        correctors[li] = corrector

        # Get the sieve's gate_proj for this layer
        mlp = layers[li].mlp
        sieve_gate = mlp.gate_proj

        optimizer = torch.optim.Adam(corrector.parameters(), lr=lr)

        best_loss = float('inf')
        loss_history = []

        for step in range(steps):
            optimizer.zero_grad()
            total_loss = 0.0
            total_sign_acc = 0.0
            n_batches = 0

            # Shuffle data
            indices = list(range(len(gate_data[li])))
            np.random.shuffle(indices)

            for idx in indices[:16]:  # mini-batch of 16 sequences
                item = gate_data[li][idx]
                mlp_input = item['mlp_input'].float().to(device)
                teacher_gate = item['gate_output'].float().to(device)

                # Sieve's gate output on the same input
                with torch.no_grad():
                    sieve_gate_out = sieve_gate(
                        mlp_input.unsqueeze(0).to(
                            next(sieve_gate.parameters()).dtype
                            if hasattr(sieve_gate, 'parameters')
                            and any(True for _ in sieve_gate.parameters())
                            else mlp_input.dtype
                        )).squeeze(0).float()

                # Corrected gate
                corrected = corrector(sieve_gate_out)

                # Loss: MSE on activations + BCE on sign (routing)
                mse_loss = F.mse_loss(corrected, teacher_gate)
                # Sign matching: does the correction fix the routing?
                teacher_sign = (teacher_gate > 0).float()
                corrected_prob = torch.sigmoid(corrected * 5.0)
                bce_loss = F.binary_cross_entropy(
                    corrected_prob, teacher_sign)

                loss = mse_loss + 0.5 * bce_loss
                loss.backward()
                total_loss += loss.item()

                # Sign accuracy
                with torch.no_grad():
                    sign_match = ((corrected > 0) == (teacher_gate > 0))
                    total_sign_acc += sign_match.float().mean().item()
                n_batches += 1

            if n_batches > 0:
                torch.nn.utils.clip_grad_norm_(
                    corrector.parameters(), max_norm=1.0)
                optimizer.step()

                avg_loss = total_loss / n_batches
                avg_acc = total_sign_acc / n_batches
                loss_history.append(avg_loss)

                if avg_loss < best_loss:
                    best_loss = avg_loss

        stats[li] = {
            "final_loss": round(loss_history[-1], 4) if loss_history else 0,
            "best_loss": round(best_loss, 4),
            "final_sign_acc": round(avg_acc, 4) if n_batches > 0 else 0,
            "n_params": corrector.n_params,
        }

    return correctors, stats


# ══════════════════════════════════════════════════════════════
# Teacher state caching (for SM loss in Phase 2)
# ══════════════════════════════════════════════════════════════

@torch.no_grad()
def cache_teacher_states(model, sequences, device, max_seqs=128):
    layers = get_layers(model)
    n_layers = len(layers)
    all_states = []
    for seq_idx, seq in enumerate(sequences[:max_seqs]):
        input_ids = seq.unsqueeze(0).to(device)
        layer_states = {}
        hooks = []

        def embed_hook(mod, args):
            h = args[0] if isinstance(args, tuple) else args
            layer_states[-1] = h[0].detach().cpu().half()
        hooks.append(layers[0].register_forward_pre_hook(embed_hook))

        def make_hook(li):
            def fn(mod, inp, out):
                h = out[0] if isinstance(out, tuple) else out
                layer_states[li] = h[0].detach().cpu().half()
            return fn
        for li in range(n_layers):
            hooks.append(layers[li].register_forward_hook(make_hook(li)))
        model(input_ids=input_ids)
        for h in hooks:
            h.remove()

        state_list = [layer_states.get(-1, torch.zeros(1))]
        for li in range(n_layers):
            state_list.append(layer_states.get(li, torch.zeros(1)))
        all_states.append(torch.stack(state_list, dim=0))
        if (seq_idx + 1) % 32 == 0:
            log(f"      {seq_idx+1}/{min(max_seqs, len(sequences))} cached")
    return all_states


# ══════════════════════════════════════════════════════════════
# Phase 2: SM loss (same as v3b)
# ══════════════════════════════════════════════════════════════

def compute_sm_loss(model, input_ids, teacher_states, device):
    layers = get_layers(model)
    n_layers = len(layers)
    student_states = {}
    hooks = []

    def pre_hook(mod, args):
        h = args[0] if isinstance(args, tuple) else args
        student_states[-1] = h[0]
    hooks.append(layers[0].register_forward_pre_hook(pre_hook))

    def make_hook(li):
        def fn(mod, inp, out):
            h = out[0] if isinstance(out, tuple) else out
            student_states[li] = h[0]
        return fn
    for li in range(n_layers):
        hooks.append(layers[li].register_forward_hook(make_hook(li)))

    labels = input_ids.clone()
    out = model(input_ids=input_ids, labels=labels)
    ce_loss = out.loss
    for h in hooks:
        h.remove()

    sm_loss = torch.tensor(0.0, device=device)
    n_sm = 0
    for li in range(n_layers):
        if li not in student_states:
            continue
        s_prev = student_states.get(-1) if li == 0 else student_states.get(
            li - 1)
        if s_prev is None:
            continue
        s_delta = student_states[li].float() - s_prev.float()
        t_delta = (teacher_states[li + 1].float().to(device)
                   - teacher_states[li].float().to(device))
        cos = F.cosine_similarity(s_delta, t_delta, dim=-1)
        mean_cos = cos.mean()
        if not torch.isnan(mean_cos):
            sm_loss = sm_loss + (1.0 - mean_cos)
            n_sm += 1
    if n_sm > 0:
        sm_loss = sm_loss / n_sm
    return ce_loss, sm_loss


# ══════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════

def main():
    p = argparse.ArgumentParser(
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("--model", default="Qwen/Qwen3-8B")
    p.add_argument("--device", default="cpu")
    p.add_argument("--zero-rate", type=float, default=0.5)
    p.add_argument("--lora-rank", type=int, default=4)
    p.add_argument("--gate-hidden", type=int, default=256,
                   help="Hidden dim for gate corrector bottleneck")
    p.add_argument("--gate-steps", type=int, default=100,
                   help="Training steps for gate correction (Phase 1)")
    p.add_argument("--sm-steps", type=int, default=200,
                   help="Training steps for LoRA + SM (Phase 2)")
    p.add_argument("--lr-gate", type=float, default=1e-3)
    p.add_argument("--lr-lora", type=float, default=1e-4)
    p.add_argument("--alpha-sm", type=float, default=5.0)
    p.add_argument("--n-cal", type=int, default=256)
    p.add_argument("--n-gate-cal", type=int, default=64,
                   help="Sequences for gate target collection")
    p.add_argument("--n-eval", type=int, default=64)
    p.add_argument("--n-teacher-cache", type=int, default=128)
    p.add_argument("--seq-len", type=int, default=128)
    p.add_argument("--batch-size", type=int, default=4)
    p.add_argument("--eval-every", type=int, default=50)
    p.add_argument("--shard-dir", type=str, default=str(SHARD_DIR))
    args = p.parse_args()

    SIEVE_LAYERS = list(range(1, 27)) + [32, 33, 34]

    log(f"\n{'='*70}")
    log("  TEACHER-GUIDED ROUTING")
    log("  Fix topology before training grout")
    log(f"{'='*70}")
    log(f"  Model: {args.model}")
    log(f"  Device: {args.device}")
    log(f"  Phase 1: Gate correction ({args.gate_steps} steps,"
        f" hidden={args.gate_hidden})")
    log(f"  Phase 2: LoRA + SM ({args.sm_steps} steps,"
        f" rank={args.lora_rank}, α={args.alpha_sm})")

    # ── Load data ─────────────────────────────────────────
    shard_path = Path(args.shard_dir) / "shard_00000.npy"
    log(f"\n  Loading sequences from {shard_path.name}...")
    cal_sequences = load_sequences(
        shard_path, args.n_cal, seq_len=args.seq_len)
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
    log(f"  d_model={model.config.hidden_size}")

    # ── Baseline ──────────────────────────────────────────
    log("\n  Measuring baseline...")
    base_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    base_facts, total_facts = measure_facts(model, tokenizer, args.device)
    log(f"  Baseline PPL: {base_ppl:.2f}, facts: {base_facts}/{total_facts}")

    # ══════════════════════════════════════════════════════
    # Collect teacher gate targets BEFORE sieving
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  COLLECTING TEACHER GATE TARGETS (before sieve)")
    log(f"{'═'*70}")

    t0 = time.time()
    gate_data = collect_gate_targets(
        model, cal_sequences, args.device, SIEVE_LAYERS,
        max_seqs=args.n_gate_cal)
    gate_elapsed = time.time() - t0
    n_gate_items = sum(len(v) for v in gate_data.values())
    log(f"  Collected {n_gate_items} gate targets across"
        f" {len(SIEVE_LAYERS)} layers ({gate_elapsed:.0f}s)")

    # ── Cache teacher states (for SM loss) ────────────────
    log(f"\n  Caching teacher states ({args.n_teacher_cache} seqs)...")
    t0 = time.time()
    teacher_cache = cache_teacher_states(
        model, cal_sequences, args.device,
        max_seqs=args.n_teacher_cache)
    log(f"  Cached {len(teacher_cache)} ({time.time()-t0:.0f}s)")

    # ══════════════════════════════════════════════════════
    # Install sieve
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  INSTALLING CRYSTAL SIEVE")
    log(f"{'═'*70}")

    layers = get_layers(model)

    # L0: SVD
    mlp0 = layers[0].mlp
    for pname in ["gate_proj", "up_proj", "down_proj"]:
        proj = getattr(mlp0, pname)
        A, B = svd_factorize(proj.weight, 750)
        mod = FrozenLowRankLinear(
            A.to(args.device), B.to(args.device)).to(args.device)
        setattr(mlp0, pname, mod)

    # Sieved layers
    for li in SIEVE_LAYERS:
        mlp = layers[li].mlp
        for pname in ["gate_proj", "up_proj", "down_proj"]:
            proj = getattr(mlp, pname)
            mod = FrozenSieveLinear(
                proj.weight, zero_rate=args.zero_rate).to(args.device)
            setattr(mlp, pname, mod)

    sieve_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    sieve_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"  Sieve PPL: {sieve_ppl:.2f} ({sieve_ppl/base_ppl:.2f}x)"
        f"  facts: {sieve_facts}/{total_facts}")

    # ══════════════════════════════════════════════════════
    # Phase 1: Train gate correctors
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 1: TEACHER-GUIDED GATE CORRECTION")
    log(f"  Training gate correctors to match teacher routing")
    log(f"  {args.gate_steps} steps, hidden={args.gate_hidden},"
        f" lr={args.lr_gate}")
    log(f"{'═'*70}")

    t0 = time.time()
    correctors, gate_stats = train_gate_correctors(
        model, gate_data, args.device, SIEVE_LAYERS,
        hidden_dim=args.gate_hidden, steps=args.gate_steps,
        lr=args.lr_gate)
    gate_train_elapsed = time.time() - t0

    # Install correctors
    total_gate_params = 0
    n_installed = 0
    for li, corrector in correctors.items():
        mlp = layers[li].mlp
        corrected_mlp = CorrectedGateMLP(mlp, corrector)
        layers[li].mlp = corrected_mlp
        total_gate_params += corrector.n_params
        n_installed += 1

    log(f"\n  Gate correction summary:")
    log(f"    Installed: {n_installed} layers")
    log(f"    Total gate params: {total_gate_params:,}")
    log(f"    Training time: {gate_train_elapsed:.0f}s")

    # Show per-layer stats (sample)
    sample_layers = [1, 5, 10, 15, 20, 25, 33]
    log(f"\n  {'Layer':>6} {'Loss':>8} {'SignAcc':>8} {'Params':>8}")
    log(f"  {'─'*6} {'─'*8} {'─'*8} {'─'*8}")
    for li in sample_layers:
        if li in gate_stats:
            s = gate_stats[li]
            log(f"  L{li:>3d}  {s['final_loss']:>8.4f}"
                f" {s['final_sign_acc']:>8.4f} {s['n_params']:>8,}")

    # Measure post-gate-correction PPL
    gate_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    gate_facts, _ = measure_facts(model, tokenizer, args.device)
    log(f"\n  Post-gate PPL: {gate_ppl:.2f} ({gate_ppl/base_ppl:.2f}x)"
        f"  facts: {gate_facts}/{total_facts}")
    log(f"  Gate correction effect: {sieve_ppl:.2f} → {gate_ppl:.2f}")

    # ══════════════════════════════════════════════════════
    # Phase 2: LoRA + Score Matching (same as v3b)
    # ══════════════════════════════════════════════════════
    log(f"\n{'═'*70}")
    log("  PHASE 2: LoRA + SCORE MATCHING (with corrected routing)")
    log(f"  {args.sm_steps} steps, rank={args.lora_rank},"
        f" α={args.alpha_sm}")
    log(f"{'═'*70}")

    # Add LoRA to all sieved projections (gate, up, down)
    # For CorrectedGateMLP layers, add LoRA to the inner projections
    lora_params = []
    total_lora_params = 0

    for li in [0] + SIEVE_LAYERS:
        mlp = layers[li].mlp
        # Handle CorrectedGateMLP wrapper
        if isinstance(mlp, CorrectedGateMLP):
            proj_container = mlp
        else:
            proj_container = mlp

        for pname in ["gate_proj", "up_proj", "down_proj"]:
            base_mod = getattr(proj_container, pname)
            if isinstance(base_mod, (FrozenSieveLinear, FrozenLowRankLinear)):
                lora_mod = SieveWithLoRA(
                    base_mod, rank=args.lora_rank).to(args.device)
                setattr(proj_container, pname, lora_mod)
                lora_params.extend([lora_mod.lora_A, lora_mod.lora_B])
                total_lora_params += lora_mod.n_params

    # Also make gate corrector params trainable in Phase 2
    for li, corrector in correctors.items():
        lora_params.extend(list(corrector.parameters()))
        # (already counted in total_gate_params)

    log(f"  LoRA params: {total_lora_params:,}")
    log(f"  Gate params: {total_gate_params:,} (joint training)")
    log(f"  Total trainable: {total_lora_params + total_gate_params:,}")

    optimizer = torch.optim.Adam(lora_params, lr=args.lr_lora)
    n_teacher = len(teacher_cache)
    n_cal = len(cal_sequences)
    model.train()

    loss_history = []
    eval_history = []
    t0 = time.time()

    for step in range(args.sm_steps):
        optimizer.zero_grad()
        rng = np.random.RandomState(step)
        batch_indices = rng.choice(n_cal, args.batch_size, replace=False)

        step_ce = 0.0
        step_sm = 0.0
        step_tokens = 0

        for idx in batch_indices:
            input_ids = cal_sequences[idx].unsqueeze(0).to(args.device)
            if idx < n_teacher:
                ce_loss, sm_loss = compute_sm_loss(
                    model, input_ids, teacher_cache[idx], args.device)
                loss = ce_loss + args.alpha_sm * sm_loss
                step_sm += sm_loss.item()
            else:
                labels = input_ids.clone()
                out = model(input_ids=input_ids, labels=labels)
                ce_loss = out.loss
                loss = ce_loss

            if not (torch.isnan(loss) or torch.isinf(loss)
                    or torch.isnan(ce_loss)):
                loss.backward()
                step_ce += ce_loss.item() * input_ids.numel()
                step_tokens += input_ids.numel()

        if step_tokens > 0:
            torch.nn.utils.clip_grad_norm_(lora_params, max_norm=1.0)
            optimizer.step()

        avg_ce = step_ce / max(step_tokens, 1)
        n_sm_batch = sum(1 for i in batch_indices if i < n_teacher)
        avg_sm = step_sm / max(n_sm_batch, 1)
        loss_history.append({"step": step+1, "ce": round(avg_ce, 4),
                             "sm": round(avg_sm, 4)})

        if (step + 1) % 10 == 0 or step == 0:
            log(f"    step {step+1:>3d}: CE={avg_ce:.4f}"
                f" SM={avg_sm:.4f} ({time.time()-t0:.0f}s)")

        if (step + 1) % args.eval_every == 0:
            eval_ppl = measure_ppl_tokens(
                model, eval_sequences, args.device)
            eval_facts, _ = measure_facts(model, tokenizer, args.device)
            log(f"    ▶ EVAL step {step+1}: PPL={eval_ppl:.2f}"
                f" ({eval_ppl/base_ppl:.3f}x)"
                f" facts={eval_facts}/{total_facts}")
            eval_history.append({
                "step": step+1, "ppl": eval_ppl,
                "ppl_ratio": round(eval_ppl / base_ppl, 4),
                "facts": eval_facts,
            })
            model.train()

    model.eval()
    final_ppl = measure_ppl_tokens(model, eval_sequences, args.device)
    final_facts, _ = measure_facts(model, tokenizer, args.device)

    # ══════════════════════════════════════════════════════
    # Results
    # ══════════════════════════════════════════════════════
    log(f"\n{'='*70}")
    log("  RESULTS")
    log(f"{'='*70}")
    log(f"  Baseline:       PPL={base_ppl:.2f}"
        f"  facts={base_facts}/{total_facts}")
    log(f"  Sieve only:     PPL={sieve_ppl:.2f}"
        f" ({sieve_ppl/base_ppl:.2f}x)")
    log(f"  After gate fix: PPL={gate_ppl:.2f}"
        f" ({gate_ppl/base_ppl:.2f}x)"
        f"  [Phase 1: routing correction]")
    log(f"  After LoRA+SM:  PPL={final_ppl:.2f}"
        f" ({final_ppl/base_ppl:.3f}x)"
        f"  facts={final_facts}/{total_facts}"
        f"  [Phase 2: grout]")

    log(f"\n  vs v3b (LoRA+SM only, no routing fix):")
    log(f"    v3b:     25.67 → 16.27 (1.44x base)")
    log(f"    Routing: {sieve_ppl:.2f} → {gate_ppl:.2f}"
        f" → {final_ppl:.2f} ({final_ppl/base_ppl:.2f}x)")

    log(f"\n  Params:")
    log(f"    Gate correctors: {total_gate_params:,}")
    log(f"    LoRA:            {total_lora_params:,}")
    log(f"    Total:           {total_lora_params + total_gate_params:,}")

    # Save
    out_dir = _PROJECT_ROOT / "results" / "teacher-guided-routing"
    out_dir.mkdir(parents=True, exist_ok=True)
    slug = args.model.replace("/", "_")

    result = {
        "model": args.model,
        "version": "v1-teacher-guided-routing",
        "config": {
            "lora_rank": args.lora_rank,
            "gate_hidden": args.gate_hidden,
            "gate_steps": args.gate_steps,
            "sm_steps": args.sm_steps,
            "lr_gate": args.lr_gate,
            "lr_lora": args.lr_lora,
            "alpha_sm": args.alpha_sm,
            "n_cal": len(cal_sequences),
            "n_gate_cal": args.n_gate_cal,
            "n_eval": len(eval_sequences),
            "n_teacher_cache": len(teacher_cache),
            "sieve_layers": SIEVE_LAYERS,
        },
        "baseline_ppl": base_ppl, "baseline_facts": base_facts,
        "sieve_ppl": sieve_ppl, "sieve_facts": sieve_facts,
        "gate_ppl": gate_ppl, "gate_facts": gate_facts,
        "final_ppl": final_ppl, "final_facts": final_facts,
        "final_ratio": round(final_ppl / base_ppl, 4),
        "total_gate_params": total_gate_params,
        "total_lora_params": total_lora_params,
        "gate_stats": gate_stats,
        "eval_history": eval_history,
        "loss_history": loss_history,
    }

    out_path = out_dir / f"{slug}.json"
    with open(out_path, "w") as f:
        json.dump(result, f, indent=2)
    log(f"\n  Results saved to {out_path}")
    log(f"{'='*70}\n")


if __name__ == "__main__":
    main()
