"""
explore_qwen3_moe.py
────────────────────
Load Qwen/Qwen3-30B-A3B (MoE) in FP16 on MPS and:
  1. Print first 100 named parameter names + shapes
  2. Categorise expert FFN weights
  3. Categorise MoE gate/router weights
  4. Categorise attention projections (Q/K/V/O)
  5. Identify any linear-attention-specific weights (conv1d, etc.)
  6. Count total params and per-category params
  7. Run a simple forward pass to verify the model works
  8. Measure baseline perplexity on three texts

Usage:
    uv run --group level1 python scripts/explore_qwen3_moe.py
"""

import math
import time
from collections import defaultdict

import torch
from transformers import AutoModelForCausalLM, AutoTokenizer

# ── Config ────────────────────────────────────────────────────────────────────
MODEL_ID = "Qwen/Qwen3-30B-A3B"
DTYPE = torch.float16
DEVICE = "mps"

PERPLEXITY_TEXTS = [
    "The cat sat on the mat.",
    "Lambda calculus is a formal system for expressing computation.",
    "The transformer architecture revolutionized natural language processing.",
]


# ── Helpers ───────────────────────────────────────────────────────────────────

def fmt_params(n: int) -> str:
    """Human-readable parameter count."""
    if n >= 1e9:
        return f"{n/1e9:.3f}B"
    if n >= 1e6:
        return f"{n/1e6:.2f}M"
    if n >= 1e3:
        return f"{n/1e3:.1f}K"
    return str(n)


def categorise(name: str) -> str | None:
    """Return a category label for a parameter name, or None if uncategorised."""
    # Expert FFN weights (inside MoE blocks)
    if "experts" in name and any(k in name for k in ("gate_proj", "up_proj", "down_proj")):
        return "expert_ffn"
    # Shared expert FFN (some MoE models have a shared/dense expert alongside routed ones)
    if "shared_expert" in name and any(k in name for k in ("gate_proj", "up_proj", "down_proj")):
        return "shared_expert_ffn"
    # MoE router / gate
    if any(k in name for k in ("gate.weight", "router", "gate_weight")):
        # Exclude gate_proj inside experts (already caught above)
        if "gate_proj" not in name:
            return "moe_router"
    # Attention projections
    if any(k in name for k in ("q_proj", "k_proj", "v_proj", "o_proj")):
        return "attention_proj"
    # Linear attention (conv1d, etc.)
    if any(k in name for k in ("conv1d", "conv_kernel", "short_conv", "linear_attn")):
        return "linear_attn"
    # Embedding / lm-head
    if any(k in name for k in ("embed_tokens", "lm_head")):
        return "embed_lm_head"
    # Layer-norm / RMS-norm
    if any(k in name for k in ("norm", "layernorm", "layer_norm")):
        return "norm"
    # Dense FFN weights not inside experts
    if any(k in name for k in ("gate_proj", "up_proj", "down_proj")):
        return "dense_ffn"
    return "other"


def compute_perplexity(model, tokenizer, text: str, device: str) -> float:
    """Compute per-token perplexity for a single string."""
    enc = tokenizer(text, return_tensors="pt")
    input_ids = enc["input_ids"].to(device)

    with torch.no_grad():
        outputs = model(input_ids, labels=input_ids)
        # outputs.loss is mean cross-entropy over tokens
        loss = outputs.loss.item()

    return math.exp(loss)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    print("=" * 72)
    print(f"  Loading {MODEL_ID}")
    print(f"  dtype={DTYPE}  device_map=auto  trust_remote_code=True")
    print("=" * 72)

    t0 = time.time()

    # Load tokenizer (text-only; processor not needed for pure LM tasks)
    print("\n[1/3] Loading tokenizer …")
    tokenizer = AutoTokenizer.from_pretrained(MODEL_ID, trust_remote_code=True)

    # Load model — device_map="auto" will spread across MPS + CPU as needed
    print("[2/3] Loading model weights (this may take a minute) …")
    model = AutoModelForCausalLM.from_pretrained(
        MODEL_ID,
        torch_dtype=DTYPE,
        device_map="auto",
        trust_remote_code=True,
    )
    model.eval()

    elapsed = time.time() - t0
    print(f"[3/3] Model loaded in {elapsed:.1f}s\n")

    # ── 1. First 100 named parameters ────────────────────────────────────────
    print("=" * 72)
    print("  SECTION 1 — First 100 named parameter names + shapes")
    print("=" * 72)

    all_params = list(model.named_parameters())
    for i, (name, p) in enumerate(all_params[:100]):
        print(f"  [{i:3d}] {name:<70s}  {list(p.shape)}")

    print(f"\n  (Total named parameter tensors: {len(all_params)})\n")

    # ── 2-6. Categorise & count ───────────────────────────────────────────────
    print("=" * 72)
    print("  SECTION 2-6 — Weight categories")
    print("=" * 72)

    category_params: dict[str, int] = defaultdict(int)
    category_names: dict[str, list[str]] = defaultdict(list)
    total_params = 0

    for name, p in all_params:
        n = p.numel()
        total_params += n
        cat = categorise(name)
        if cat:
            category_params[cat] += n
            # Store up to 5 example names per category to keep output tidy
            if len(category_names[cat]) < 5:
                category_names[cat].append(f"{name}  {list(p.shape)}")

    ordered_cats = [
        ("expert_ffn",       "Expert FFN weights (gate/up/down_proj inside experts)"),
        ("shared_expert_ffn","Shared-expert FFN weights"),
        ("moe_router",       "MoE gate/router weights"),
        ("attention_proj",   "Attention projections (Q/K/V/O)"),
        ("linear_attn",      "Linear-attention-specific weights (conv1d, etc.)"),
        ("dense_ffn",        "Dense FFN weights (non-expert)"),
        ("embed_lm_head",    "Embedding / LM-head"),
        ("norm",             "LayerNorm / RMSNorm"),
        ("other",            "Other / uncategorised"),
    ]

    for cat_key, cat_label in ordered_cats:
        n = category_params.get(cat_key, 0)
        pct = 100.0 * n / total_params if total_params else 0.0
        print(f"\n  ── {cat_label}")
        print(f"     Params: {fmt_params(n)}  ({pct:.2f}%)")
        examples = category_names.get(cat_key, [])
        if examples:
            print("     Example names:")
            for ex in examples:
                print(f"       • {ex}")
        else:
            print("     (none found)")

    print(f"\n  {'─'*60}")
    print(f"  TOTAL parameters: {fmt_params(total_params)}")
    print(f"  {'─'*60}\n")

    # ── 7. Forward pass smoke test ────────────────────────────────────────────
    print("=" * 72)
    print("  SECTION 7 — Forward pass smoke test")
    print("=" * 72)

    test_text = "Hello, I am Qwen. The capital of France is"
    print(f"\n  Input: \"{test_text}\"")

    enc = tokenizer(test_text, return_tensors="pt")
    # Move to the device that the model's first layer is on
    first_device = next(model.parameters()).device
    input_ids = enc["input_ids"].to(first_device)
    attention_mask = enc["attention_mask"].to(first_device)

    t0 = time.time()
    with torch.no_grad():
        out = model.generate(
            input_ids,
            attention_mask=attention_mask,
            max_new_tokens=20,
            do_sample=False,
            pad_token_id=tokenizer.eos_token_id,
        )
    elapsed = time.time() - t0

    prompt_len = input_ids.shape[1]
    generated_ids = out[0][prompt_len:]
    generated_text = tokenizer.decode(generated_ids, skip_special_tokens=True)

    print(f"  Generated ({len(generated_ids)} new tokens in {elapsed:.2f}s):")
    print(f"  → \"{generated_text}\"\n")

    # ── 8. Perplexity ─────────────────────────────────────────────────────────
    print("=" * 72)
    print("  SECTION 8 — Baseline perplexity")
    print("=" * 72)

    # Use the device of the first parameter for all ppl passes
    ppl_device = str(first_device)

    for text in PERPLEXITY_TEXTS:
        ppl = compute_perplexity(model, tokenizer, text, ppl_device)
        tokens = tokenizer(text, return_tensors="pt")["input_ids"].shape[1]
        print(f"\n  Text : \"{text}\"")
        print(f"  Tokens: {tokens}   Perplexity: {ppl:.4f}")

    print("\n" + "=" * 72)
    print("  Done.")
    print("=" * 72)


if __name__ == "__main__":
    main()
