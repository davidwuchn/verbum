#!/usr/bin/env python3
"""Crystal Sieve + Distillation — The teacher's logits ARE the DVD.

THE SYNTHESIS: Crystal signs (universal topology) + teacher logits (151K floats
of supervision per token) + ternary mask training = the complete path.

THREE CONFIGURATIONS:
  A. crystal + next-token     (s184 baseline — 1 bit per token supervision)
  B. crystal + distillation   (151K floats per token from teacher)
  C. random  + distillation   (does crystal help even with rich supervision?)

Teacher: Qwen3-8B (float16, frozen — fully-formed crystal, r=0.998)
Student: Qwen3-0.6B architecture (same tokenizer, 13× smaller)
         Crystal sieve FFN: frozen ternary signs + trainable masks + per-group scale

Usage:
    cd ~/src/verbum
    uv run python scripts/experiments/crystal_distill.py
    uv run python scripts/experiments/crystal_distill.py --steps 500

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import time
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import torch
import torch.nn as nn
import torch.nn.functional as F
from torch.utils.data import DataLoader

RESULTS_DIR = Path(__file__).parent.parent.parent / "results" / "crystal-distill"

TEACHER_ID = "Qwen/Qwen3-8B"
STUDENT_ID = "Qwen/Qwen3-0.6B"


def log(msg: str = "", end: str = "\n") -> None:
    print(msg, end=end, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Crystal Sieve Linear
# ═══════════════════════════════════════════════════════════════════

class CrystalSieveLinear(nn.Module):
    """Fixed ternary signs + learnable importance mask + per-group scale.

    During training: W_eff = group_scale * T * sigmoid(importance / τ)
    After training:  W_eff = group_scale * T * (importance > 0).float()
    """

    def __init__(self, T: torch.Tensor, scale: float,
                 bias: torch.Tensor | None = None, group_size: int = 32):
        super().__init__()
        self.register_buffer("T", T.to(torch.int8))
        self.group_size = group_size

        out_f, in_f = T.shape
        n_groups = (in_f + group_size - 1) // group_size

        self.group_scale = nn.Parameter(
            torch.full((out_f, n_groups), scale, dtype=torch.float32)
        )
        self.importance = nn.Parameter(
            torch.full(T.shape, 2.0, dtype=torch.float32)
        )

        if bias is not None:
            self.bias = nn.Parameter(bias.float())
        else:
            self.bias = None

        self.out_features, self.in_features = T.shape
        self._temperature = 1.0

    def forward(self, x: torch.Tensor) -> torch.Tensor:
        mask = torch.sigmoid(self.importance / max(self._temperature, 0.01))

        gs = self.group_scale.repeat_interleave(self.group_size, dim=1)
        gs = gs[:, :self.in_features]

        W_eff = gs.to(x.dtype) * self.T.to(x.dtype) * mask.to(x.dtype)
        return F.linear(x, W_eff, self.bias)

    def active_fraction(self) -> float:
        return (self.importance > 0).float().mean().item()


# ═══════════════════════════════════════════════════════════════════
# Model surgery — patch Qwen3 FFN
# ═══════════════════════════════════════════════════════════════════

def patch_qwen_model(model, mode: str = "crystal", group_size: int = 32):
    """Replace all FFN linears in Qwen3 model with crystal sieve versions."""
    n_patched = 0
    ffn_names = ["gate_proj", "up_proj", "down_proj"]

    for layer in model.model.layers:
        mlp = layer.mlp
        for name in ffn_names:
            linear = getattr(mlp, name)
            W = linear.weight.data.float()

            if mode == "crystal":
                T = torch.sign(W).to(torch.int8)
                T[T == 0] = 1
            else:
                T = torch.randint(0, 2, W.shape, dtype=torch.int8) * 2 - 1

            scale = W.abs().mean().item()
            bias = linear.bias.data if linear.bias is not None else None

            sieve = CrystalSieveLinear(T, scale, bias, group_size)
            setattr(mlp, name, sieve)
            n_patched += 1
            del linear

    log(f"  Patched {n_patched} FFN layers ({mode}, group_size={group_size})")
    gc.collect()
    return model


def freeze_except_trainable(model):
    """Freeze everything except importance, group_scale, biases, norms, embeddings."""
    n_train = n_frozen = 0
    for name, param in model.named_parameters():
        if any(k in name for k in ["importance", "group_scale", "bias",
                                    "layernorm", "layer_norm", "norm",
                                    "embed"]):
            param.requires_grad = True
            n_train += param.numel()
        else:
            param.requires_grad = False
            n_frozen += param.numel()
    log(f"  Trainable: {n_train:,}  Frozen: {n_frozen:,}")
    return n_train, n_frozen


# ═══════════════════════════════════════════════════════════════════
# Data
# ═══════════════════════════════════════════════════════════════════

def prepare_data(tokenizer, seq_len=256, batch_size=4):
    from datasets import load_dataset

    ds = load_dataset("wikitext", "wikitext-2-raw-v1")

    def tokenize_split(split):
        texts = [t for t in ds[split]["text"] if len(t.strip()) > 50]
        all_ids = []
        for t in texts:
            all_ids.extend(tokenizer.encode(t, add_special_tokens=False))
        chunks = []
        for i in range(0, len(all_ids) - seq_len, seq_len):
            chunks.append({"input_ids": torch.tensor(all_ids[i : i + seq_len])})
        return chunks

    train_data = tokenize_split("train")
    eval_data = tokenize_split("validation")
    log(f"  Train: {len(train_data)} seqs  Eval: {len(eval_data)} seqs")

    return (
        DataLoader(train_data, batch_size=batch_size, shuffle=True),
        DataLoader(eval_data, batch_size=batch_size, shuffle=False),
    )


# ═══════════════════════════════════════════════════════════════════
# Evaluation
# ═══════════════════════════════════════════════════════════════════

@torch.no_grad()
def eval_ppl(model, loader, device, max_batches=20):
    model.eval()
    total_loss = total_tokens = 0
    for i, batch in enumerate(loader):
        if i >= max_batches:
            break
        ids = batch["input_ids"].to(device)
        loss = model(ids, labels=ids).loss
        total_loss += loss.item() * ids.shape[1]
        total_tokens += ids.shape[1]
    return math.exp(min(total_loss / max(total_tokens, 1), 20))


# ═══════════════════════════════════════════════════════════════════
# Training
# ═══════════════════════════════════════════════════════════════════

def set_sieve_temperature(model, temperature):
    """Set temperature on all CrystalSieveLinear modules."""
    for module in model.modules():
        if isinstance(module, CrystalSieveLinear):
            module._temperature = temperature


def get_mean_active(model):
    """Mean active fraction across FFN sieve layers."""
    fracs = []
    for module in model.modules():
        if isinstance(module, CrystalSieveLinear):
            fracs.append(module.active_fraction())
    return sum(fracs) / max(len(fracs), 1)


def train_loop(
    student, teacher, train_loader, eval_loader, device,
    n_steps=250, lr=1e-3, weight_decay=0.01,
    temp_start=2.0, temp_end=0.1,
    distill_temp=2.0, loss_mode="distill", alpha=0.5,
):
    """Train student with optional teacher distillation."""
    trainable = [p for p in student.parameters() if p.requires_grad]
    optimizer = torch.optim.AdamW(trainable, lr=lr, weight_decay=weight_decay)

    temp_decay = (temp_end / temp_start) ** (1.0 / max(n_steps, 1))
    mask_temp = temp_start

    log(f"\n  Training: {loss_mode}, {n_steps} steps, lr={lr}")
    log(f"  {'Step':>6} {'Loss':>8} {'PPL':>8} {'MTemp':>6} {'Active':>8} {'Time':>6}")
    log(f"  {'─' * 6} {'─' * 8} {'─' * 8} {'─' * 6} {'─' * 8} {'─' * 6}")

    t0 = time.time()

    # Initial eval
    set_sieve_temperature(student, mask_temp)
    ppl = eval_ppl(student, eval_loader, device)
    active = get_mean_active(student)
    log(f"  {0:6d} {'─':>8} {ppl:8.1f} {mask_temp:6.2f} {active:8.1%} {0:6.1f}s")

    history = [{"step": 0, "ppl": ppl, "active": active}]
    student.train()

    step = 0
    while step < n_steps:
        for batch in train_loader:
            if step >= n_steps:
                break

            ids = batch["input_ids"].to(device)
            set_sieve_temperature(student, mask_temp)

            # ── Forward ──
            student_logits = student(ids).logits  # (B, S, V)

            if loss_mode == "next_token":
                shift_logits = student_logits[:, :-1, :].contiguous()
                shift_labels = ids[:, 1:].contiguous()
                loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                )

            elif loss_mode == "distill":
                with torch.no_grad():
                    teacher_logits = teacher(ids).logits.to(student_logits.dtype)

                s_log_probs = F.log_softmax(student_logits / distill_temp, dim=-1)
                t_probs = F.softmax(teacher_logits / distill_temp, dim=-1)

                loss = F.kl_div(
                    s_log_probs.view(-1, s_log_probs.size(-1)),
                    t_probs.view(-1, t_probs.size(-1)),
                    reduction="batchmean",
                ) * (distill_temp ** 2)

            elif loss_mode == "mixed":
                with torch.no_grad():
                    teacher_logits = teacher(ids).logits.to(student_logits.dtype)

                s_log_probs = F.log_softmax(student_logits / distill_temp, dim=-1)
                t_probs = F.softmax(teacher_logits / distill_temp, dim=-1)
                kl_loss = F.kl_div(
                    s_log_probs.view(-1, s_log_probs.size(-1)),
                    t_probs.view(-1, t_probs.size(-1)),
                    reduction="batchmean",
                ) * (distill_temp ** 2)

                shift_logits = student_logits[:, :-1, :].contiguous()
                shift_labels = ids[:, 1:].contiguous()
                ce_loss = F.cross_entropy(
                    shift_logits.view(-1, shift_logits.size(-1)),
                    shift_labels.view(-1),
                )
                loss = alpha * kl_loss + (1 - alpha) * ce_loss

            # ── Backward ──
            optimizer.zero_grad()
            loss.backward()
            torch.nn.utils.clip_grad_norm_(trainable, 1.0)
            optimizer.step()

            mask_temp *= temp_decay
            step += 1

            if step % 25 == 0 or step == 1:
                student.eval()
                set_sieve_temperature(student, mask_temp)
                ppl = eval_ppl(student, eval_loader, device)
                active = get_mean_active(student)
                elapsed = time.time() - t0
                log(f"  {step:6d} {loss.item():8.4f} {ppl:8.1f} "
                    f"{mask_temp:6.2f} {active:8.1%} {elapsed:6.1f}s")
                history.append({"step": step, "ppl": ppl, "active": active,
                                "loss": loss.item()})
                student.train()

            # Periodic cleanup for MPS
            if step % 50 == 0:
                gc.collect()
                if device == "mps":
                    torch.mps.empty_cache()

    # Final
    student.eval()
    set_sieve_temperature(student, mask_temp)
    ppl = eval_ppl(student, eval_loader, device)
    active = get_mean_active(student)
    elapsed = time.time() - t0
    log(f"  {step:6d} {'FINAL':>8} {ppl:8.1f} {mask_temp:6.2f} "
        f"{active:8.1%} {elapsed:6.1f}s")
    history.append({"step": step, "ppl": ppl, "active": active})

    return ppl, history


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(description="Crystal Distillation")
    parser.add_argument("--steps", type=int, default=250)
    parser.add_argument("--device", default="mps")
    parser.add_argument("--group-size", type=int, default=32)
    parser.add_argument("--distill-temp", type=float, default=2.0)
    parser.add_argument("--lr", type=float, default=1e-3)
    parser.add_argument("--batch-size", type=int, default=4)
    args = parser.parse_args()

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    log(f"╔{'═' * 76}╗")
    log(f"║  CRYSTAL DISTILLATION — Teacher logits ARE the DVD{' ' * 24}║")
    log(f"║  Teacher: {TEACHER_ID:<65}║")
    log(f"║  Student: {STUDENT_ID:<65}║")
    log(f"║  Steps: {args.steps:<67}║")
    log(f"╚{'═' * 76}╝")

    t_start = time.time()
    device = args.device

    from transformers import AutoModelForCausalLM, AutoTokenizer

    # ── Tokenizer (shared between teacher and student) ──
    tokenizer = AutoTokenizer.from_pretrained(STUDENT_ID)
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token

    log("\n  Preparing data...")
    train_loader, eval_loader = prepare_data(tokenizer, batch_size=args.batch_size)

    # ── Load teacher ──
    log(f"\n  Loading teacher ({TEACHER_ID})...")
    teacher = AutoModelForCausalLM.from_pretrained(
        TEACHER_ID, torch_dtype=torch.float16, device_map=device,
    )
    teacher.eval()
    for p in teacher.parameters():
        p.requires_grad = False

    teacher_ppl = eval_ppl(teacher, eval_loader, device)
    log(f"  Teacher PPL: {teacher_ppl:.2f}")

    # ── Student baseline (float, before sieve) ──
    log(f"\n  Loading student baseline ({STUDENT_ID})...")
    student_baseline = AutoModelForCausalLM.from_pretrained(
        STUDENT_ID, torch_dtype=torch.float32, device_map=device,
    )
    student_baseline.eval()
    baseline_ppl = eval_ppl(student_baseline, eval_loader, device)
    log(f"  Student float baseline PPL: {baseline_ppl:.2f}")
    del student_baseline
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    all_results = {"teacher_ppl": teacher_ppl, "student_baseline_ppl": baseline_ppl}

    # ═════════════════════════════════════════════════════════════
    # Config A: crystal + next-token
    # ═════════════════════════════════════════════════════════════
    log(f"\n{'═' * 78}")
    log(f"  CONFIG A: crystal + next-token (1 bit/token)")
    log(f"{'═' * 78}")

    student_a = AutoModelForCausalLM.from_pretrained(
        STUDENT_ID, torch_dtype=torch.float32, device_map="cpu",
    )
    student_a = patch_qwen_model(student_a, mode="crystal", group_size=args.group_size)
    freeze_except_trainable(student_a)
    student_a.to(device)

    ppl_a, hist_a = train_loop(
        student_a, None, train_loader, eval_loader, device,
        n_steps=args.steps, lr=args.lr, loss_mode="next_token",
    )
    all_results["crystal_nexttok"] = {"ppl": ppl_a, "history": hist_a}

    del student_a
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    # ═════════════════════════════════════════════════════════════
    # Config B: crystal + distillation
    # ═════════════════════════════════════════════════════════════
    log(f"\n{'═' * 78}")
    log(f"  CONFIG B: crystal + distillation (151K floats/token from {TEACHER_ID})")
    log(f"{'═' * 78}")

    student_b = AutoModelForCausalLM.from_pretrained(
        STUDENT_ID, torch_dtype=torch.float32, device_map="cpu",
    )
    student_b = patch_qwen_model(student_b, mode="crystal", group_size=args.group_size)
    freeze_except_trainable(student_b)
    student_b.to(device)

    ppl_b, hist_b = train_loop(
        student_b, teacher, train_loader, eval_loader, device,
        n_steps=args.steps, lr=args.lr, loss_mode="distill",
        distill_temp=args.distill_temp,
    )
    all_results["crystal_distill"] = {"ppl": ppl_b, "history": hist_b}

    del student_b
    gc.collect()
    if device == "mps":
        torch.mps.empty_cache()

    # ═════════════════════════════════════════════════════════════
    # Config C: random + distillation
    # ═════════════════════════════════════════════════════════════
    log(f"\n{'═' * 78}")
    log(f"  CONFIG C: random + distillation (does crystal help with rich supervision?)")
    log(f"{'═' * 78}")

    student_c = AutoModelForCausalLM.from_pretrained(
        STUDENT_ID, torch_dtype=torch.float32, device_map="cpu",
    )
    student_c = patch_qwen_model(student_c, mode="random", group_size=args.group_size)
    freeze_except_trainable(student_c)
    student_c.to(device)

    ppl_c, hist_c = train_loop(
        student_c, teacher, train_loader, eval_loader, device,
        n_steps=args.steps, lr=args.lr, loss_mode="distill",
        distill_temp=args.distill_temp,
    )
    all_results["random_distill"] = {"ppl": ppl_c, "history": hist_c}

    del student_c, teacher
    gc.collect()

    # ═════════════════════════════════════════════════════════════
    # Summary
    # ═════════════════════════════════════════════════════════════
    log(f"\n{'═' * 78}")
    log(f"  FINAL COMPARISON")
    log(f"{'═' * 78}")
    log(f"  {'Config':<35} {'PPL':>10} {'vs Teacher':>10} {'vs Student':>10}")
    log(f"  {'─' * 35} {'─' * 10} {'─' * 10} {'─' * 10}")
    log(f"  {'Teacher (Qwen3-8B float)':<35} {teacher_ppl:>10.2f} {'1.00x':>10} {'─':>10}")
    log(f"  {'Student (Qwen3-0.6B float)':<35} {baseline_ppl:>10.2f} "
        f"{baseline_ppl / teacher_ppl:>9.1f}x {'1.00x':>10}")
    log(f"  {'A: crystal + next-token':<35} {ppl_a:>10.2f} "
        f"{ppl_a / teacher_ppl:>9.1f}x {ppl_a / baseline_ppl:>9.1f}x")
    log(f"  {'B: crystal + distillation':<35} {ppl_b:>10.2f} "
        f"{ppl_b / teacher_ppl:>9.1f}x {ppl_b / baseline_ppl:>9.1f}x")
    log(f"  {'C: random + distillation':<35} {ppl_c:>10.2f} "
        f"{ppl_c / teacher_ppl:>9.1f}x {ppl_c / baseline_ppl:>9.1f}x")

    if ppl_b < ppl_a:
        log(f"\n  ✅ Distillation beats next-token: {ppl_a / ppl_b:.1f}x better PPL")
    if ppl_b < ppl_c:
        log(f"  ✅ Crystal beats random with distillation: {ppl_c / ppl_b:.1f}x better PPL")
    if ppl_b < baseline_ppl:
        log(f"  ✅ Crystal+distill beats student float: {baseline_ppl / ppl_b:.1f}x better PPL")
        log(f"     The sieve + teacher logits SURPASSES the student's own float weights!")

    # Early convergence
    for step_check in [1, 25, 50]:
        ea = next((h for h in hist_a if h["step"] == step_check), None)
        eb = next((h for h in hist_b if h["step"] == step_check), None)
        ec = next((h for h in hist_c if h["step"] == step_check), None)
        if ea and eb:
            log(f"\n  Step {step_check}: A={ea['ppl']:.1f}  B={eb['ppl']:.1f}  "
                f"C={ec['ppl']:.1f if ec else '?'}")

    with open(RESULTS_DIR / "results.json", "w") as f:
        json.dump(all_results, f, indent=2, default=str)

    elapsed = time.time() - t_start
    log(f"\n{'═' * 78}")
    log(f"  COMPLETE — {elapsed:.0f}s total")
    log(f"  Results: {RESULTS_DIR}/")
    log(f"{'═' * 78}")


if __name__ == "__main__":
    main()
