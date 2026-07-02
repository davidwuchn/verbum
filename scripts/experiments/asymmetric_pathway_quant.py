#!/usr/bin/env python3
"""Asymmetric-pathway quantization A/B — binarize the router, keep the value path.

HYPOTHESIS (explore/asymmetric-pathway-quantization.md, s260):
  In SwiGLU FFN the SIGN carries routing (gate_proj) and the MAGNITUDE
  carries value (up_proj/down_proj) — the s203 "two registers" result.
  So bits should be allocated ASYMMETRICALLY BY PATHWAY:
    router gate_proj  -> 1-bit binary (sign+gamma; magnitude is <1 bit there)
    value  up/down    -> keep 2-3 bits (magnitude/shape is load-bearing)

  This is the in-model analog of Mixedbread's asymmetric quant
  (int8 query x binary doc = -0.61 NDCG; binary x binary = -7.2): keep
  magnitude on the side that carries it, binarize the side that doesn't.

THE TWO CRUX COMPARISONS (lambda yardstick — claim counts iff beats null):
  1. PARETO. Does asym{binary-router, 3bit-value} sit BELOW the uniform
     PPL-vs-mean-bits frontier (uniform-2bit, uniform-3bit)?
  2. INVERTED-NULL at MATCHED mean-bits (2.33). Is {binary-router,3bit-value}
     PPL far better than {3bit-router,binary-value}? Same bit budget, opposite
     register assignment. This is the causal test of "sign=router,
     magnitude=value" on the exact 8B where s203 measured it. It is the
     in-model int8xbinary-vs-binaryxbinary.

MEAN-BITS (corrected from the page's loose claim): gate/up/down are equal
size in SwiGLU, so mean-bits = mean of the three per-matrix costs.
  binary=1.0, ternary=log2(3)=1.585, nbit-uniform=n. Gamma/scale amortized ~0.
  => {1/3/3} = 2.33, NOT 1.58. "1-bit router + 3-bit value at matched 1.58"
     is arithmetically impossible; the honest test is Pareto + inverted-null.

SCOPE: FFN only (gate/up/down). Attention left fp32 to isolate the pathway
claim. Reuses proven quantizers (ternarize_weight, quantize_nbit_uniform).

Usage:
  uv run python scripts/experiments/asymmetric_pathway_quant.py \
      --model Qwen/Qwen3-8B-Base --max-tokens 32768
  uv run python scripts/experiments/asymmetric_pathway_quant.py --self-test
  uv run python scripts/experiments/asymmetric_pathway_quant.py \
      --model Qwen/Qwen3-8B-Base --configs float,uniform_ternary --max-tokens 2048

License: MIT
"""

from __future__ import annotations

import argparse
import gc
import json
import math
import os
import time
from dataclasses import dataclass

os.environ.setdefault("PYTHONUNBUFFERED", "1")

import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F


def log(msg: str = "") -> None:
    print(msg, flush=True)


# ═══════════════════════════════════════════════════════════════════
# Quantizers — each returns a reconstructed float tensor + bit cost
# (ternary/binary from full_ternarize.py; nbit from standing_wave_shape.py)
# ═══════════════════════════════════════════════════════════════════

def quantize_signed(W: torch.Tensor, zero_rate: float) -> torch.Tensor:
    """Sign + per-row gamma + magnitude zeros.

    zero_rate=0.0  -> binary {-1,+1} (1 bit)
    zero_rate>0    -> ternary {-1,0,+1} (log2(3) bits)
    """
    W = W.detach().float().cpu()
    abs_W = W.abs()
    if zero_rate > 0:
        thresholds = torch.quantile(abs_W, zero_rate, dim=1, keepdim=True)
        alive = abs_W >= thresholds
    else:
        alive = torch.ones_like(W, dtype=torch.bool)
    T = torch.where(alive, torch.sign(W), torch.zeros_like(W))
    wt = (W * T).sum(dim=1)
    tt = (T * T).sum(dim=1)
    gamma = torch.where(tt > 0, wt / tt, torch.zeros_like(wt))
    return gamma.unsqueeze(1) * T


def quantize_nbit_uniform(W: torch.Tensor, n_bits: int) -> torch.Tensor:
    """Uniform n-bit quantization with per-row min/max scaling."""
    W = W.detach().float().cpu()
    n_levels = 2 ** n_bits
    row_min = W.min(dim=1, keepdim=True).values
    row_max = W.max(dim=1, keepdim=True).values
    row_range = torch.clamp(row_max - row_min, min=1e-10)
    W_norm = (W - row_min) / row_range
    W_quant = torch.round(W_norm * (n_levels - 1)) / (n_levels - 1)
    return W_quant * row_range + row_min


# A quant spec is (label, bits, fn(W)->reconstructed_float).
def spec_binary() -> tuple[str, float, callable]:
    return ("binary", 1.0, lambda W: quantize_signed(W, 0.0))


def spec_ternary(zero_rate: float = 0.35) -> tuple[str, float, callable]:
    return (f"ternary{int(zero_rate * 100)}", math.log2(3),
            lambda W: quantize_signed(W, zero_rate))


def spec_nbit(n: int) -> tuple[str, float, callable]:
    return (f"{n}bit", float(n), lambda W: quantize_nbit_uniform(W, n))


def spec_float() -> tuple[str, float, callable]:
    return ("float", 16.0, lambda W: W.detach().float().cpu())


# ═══════════════════════════════════════════════════════════════════
# Config: per-matrix-type quant spec over the SwiGLU FFN
# ═══════════════════════════════════════════════════════════════════

WEIGHT_NAMES_FFN = ["gate_proj", "up_proj", "down_proj"]


@dataclass
class QuantConfig:
    key: str
    label: str
    gate: tuple[str, float, callable]   # router
    up: tuple[str, float, callable]     # value
    down: tuple[str, float, callable]   # value

    @property
    def specs(self) -> dict[str, tuple[str, float, callable]]:
        return {"gate_proj": self.gate, "up_proj": self.up, "down_proj": self.down}

    @property
    def mean_bits(self) -> float:
        # gate/up/down equal size in SwiGLU -> simple mean of per-matrix bits.
        return (self.gate[1] + self.up[1] + self.down[1]) / 3.0

    @property
    def is_float(self) -> bool:
        return all(s[0] == "float" for s in (self.gate, self.up, self.down))


def build_configs() -> dict[str, QuantConfig]:
    tern = spec_ternary(0.35)
    b1 = spec_binary()
    b2 = spec_nbit(2)
    b3 = spec_nbit(3)
    b5 = spec_nbit(5)
    fl = spec_float()
    cfgs = [
        QuantConfig("float", "Float baseline", fl, fl, fl),
        # uniform frontier
        QuantConfig("uniform_ternary", "Uniform ternary (1.58b)", tern, tern, tern),
        QuantConfig("uniform_2bit", "Uniform 2-bit", b2, b2, b2),
        QuantConfig("uniform_3bit", "Uniform 3-bit", b3, b3, b3),
        # asymmetric (binary router + precise value)
        QuantConfig("asym_binR_3V", "Asym: binary router + 3-bit value", b1, b3, b3),
        QuantConfig("asym_binR_2V", "Asym: binary router + 2-bit value", b1, b2, b2),
        # ── MATCHED-BITS NULL TRIPLE (all mean_bits = 2.333) ──
        # Where does the single/whole binarization hurt least? Move binary
        # from router -> one value matrix -> whole value path, holding budget.
        # asym_binR_3V is the first member (binary on ROUTER).
        QuantConfig("inv_binDown",
                    "Matched null: binary on down (value) matrix", b3, b3, b1),
        QuantConfig("inv_binValue",
                    "Matched null: binary whole value path (5b router)", b5, b1, b1),
    ]
    return {c.key: c for c in cfgs}


# ═══════════════════════════════════════════════════════════════════
# Model surgery
# ═══════════════════════════════════════════════════════════════════

class QuantLinear(nn.Module):
    """Drop-in Linear with a pre-computed reconstructed float weight."""

    def __init__(self, W_quant: torch.Tensor, bias: torch.Tensor | None):
        super().__init__()
        self.register_buffer("weight", W_quant)
        self.bias = None
        if bias is not None:
            self.register_buffer("bias", bias)

    def forward(self, x):
        return F.linear(x, self.weight, self.bias)


def get_model_layers(model):
    if hasattr(model, "model") and hasattr(model.model, "layers"):
        return model.model.layers
    raise RuntimeError("Cannot find layers — add support for this architecture")


def cache_ffn_weights(model) -> dict:
    """Snapshot original gate/up/down weights (+bias) as CPU float tensors."""
    orig = {}
    for li, layer in enumerate(get_model_layers(model)):
        for name in WEIGHT_NAMES_FFN:
            lin = getattr(layer.mlp, name, None)
            if lin is None:
                continue
            orig[f"{li}.{name}"] = {
                "weight": lin.weight.data.float().cpu().clone(),
                "bias": (lin.bias.data.float().cpu().clone()
                         if getattr(lin, "bias", None) is not None else None),
                "in": lin.weight.shape[1],
                "out": lin.weight.shape[0],
            }
    return orig


def restore_ffn(model, orig: dict, device: str) -> None:
    """Restore original FFN as plain nn.Linear (undo prior surgery)."""
    for li, layer in enumerate(get_model_layers(model)):
        for name in WEIGHT_NAMES_FFN:
            key = f"{li}.{name}"
            if key not in orig:
                continue
            o = orig[key]
            has_bias = o["bias"] is not None
            lin = nn.Linear(o["in"], o["out"], bias=has_bias)
            lin.weight.data = o["weight"].clone().to(device)
            if has_bias:
                lin.bias.data = o["bias"].clone().to(device)
            setattr(layer.mlp, name, lin)


def apply_config(model, cfg: QuantConfig, orig: dict, device: str) -> dict:
    """Quantize FFN per-config; return per-weight-type mean cosine."""
    cos_by_type: dict[str, list[float]] = {n: [] for n in WEIGHT_NAMES_FFN}
    for li, layer in enumerate(get_model_layers(model)):
        for name in WEIGHT_NAMES_FFN:
            key = f"{li}.{name}"
            if key not in orig:
                continue
            _, _, fn = cfg.specs[name]
            W = orig[key]["weight"]
            W_q = fn(W)
            cos = F.cosine_similarity(
                W.reshape(1, -1), W_q.reshape(1, -1)).item()
            cos_by_type[name].append(cos)
            bias = orig[key]["bias"]
            ql = QuantLinear(
                W_q.to(device),
                bias.clone().to(device) if bias is not None else None,
            )
            setattr(layer.mlp, name, ql)
        gc.collect()
        if torch.backends.mps.is_available():
            torch.mps.empty_cache()
    return {n: float(np.mean(v)) if v else float("nan") for n, v in cos_by_type.items()}


# ═══════════════════════════════════════════════════════════════════
# Perplexity (sliding window, WikiText-2)
# ═══════════════════════════════════════════════════════════════════

def load_eval_text(max_tokens_hint: int) -> str:
    from datasets import load_dataset
    ds = load_dataset("wikitext", "wikitext-2-raw-v1", split="test")
    texts = [t for t in ds["text"] if t.strip()]
    return "\n\n".join(texts)


def evaluate_perplexity(model, tokenizer, device, text: str,
                        max_tokens: int, seq_len: int = 512,
                        stride: int = 256) -> dict:
    """Return {'loss': mean_nll_nats, 'ppl': exp(min(loss,30))}.

    Primary metric is mean NLL (nats): it stays finite and comparable even
    when aggressive quant destroys the model (PPL overflows). Only true
    nan/inf per-window losses abort to inf — a genuinely diverged model.
    """
    tokens = tokenizer.encode(text, add_special_tokens=False)[:max_tokens]
    model.eval()
    total_loss, total_tok = 0.0, 0
    with torch.no_grad():
        for start in range(0, max(1, len(tokens) - seq_len), stride):
            chunk = tokens[start:start + seq_len]
            if len(chunk) < 2:
                continue
            ids = torch.tensor([chunk], device=device)
            out = model(ids, labels=ids)
            loss = out.loss.item()
            if math.isnan(loss) or math.isinf(loss):
                return {"loss": float("inf"), "ppl": float("inf")}
            total_loss += loss * (len(chunk) - 1)
            total_tok += len(chunk) - 1
    if total_tok == 0:
        return {"loss": float("nan"), "ppl": float("nan")}
    mean_loss = total_loss / total_tok
    return {"loss": mean_loss, "ppl": math.exp(min(mean_loss, 30.0))}


# ═══════════════════════════════════════════════════════════════════
# Self-test (no model) — quantizer correctness
# ═══════════════════════════════════════════════════════════════════

def self_test() -> int:
    log("═══ self-test: quantizer correctness ═══")
    torch.manual_seed(0)
    W = torch.randn(8, 64)
    ok = True

    b = quantize_signed(W, 0.0)
    signs = torch.unique(torch.sign(b[b != 0]))
    n_zero = (b == 0).sum().item()
    cond = set(signs.tolist()) <= {-1.0, 1.0} and n_zero == 0
    log(f"  binary: nonzero-signs={signs.tolist()} zeros={n_zero}  "
        f"{'OK' if cond else 'FAIL'}")
    ok &= cond

    t = quantize_signed(W, 0.35)
    zr = (t == 0).float().mean().item()
    # sign(reconstruction) ∈ {-1,0,+1} structurally; zero_rate ~0.35
    cond = 0.25 <= zr <= 0.45
    log(f"  ternary: zero_rate={zr:.3f} (target ~0.35)  {'OK' if cond else 'FAIL'}")
    ok &= cond

    for n in (2, 3, 4):
        q = quantize_nbit_uniform(W, n)
        # count distinct levels within a single row (per-row scaling)
        levels = torch.unique(q[0]).numel()
        cond = levels <= 2 ** n
        log(f"  {n}bit: distinct row-levels={levels} (<= {2**n})  "
            f"{'OK' if cond else 'FAIL'}")
        ok &= cond

    cfgs = build_configs()
    log("\n  configs & mean-bits:")
    for c in cfgs.values():
        log(f"    {c.key:<18} gate={c.gate[0]:<9} up={c.up[0]:<7} down={c.down[0]:<7} "
            f"mean_bits={c.mean_bits:.3f}")
    # crux: the matched-bits null triple must all be equal mean-bits
    triple = ["asym_binR_3V", "inv_binDown", "inv_binValue"]
    bits = [cfgs[k].mean_bits for k in triple]
    cond = max(bits) - min(bits) < 1e-9
    log("\n  matched-null triple bits: "
        + ", ".join(f"{k}={cfgs[k].mean_bits:.3f}" for k in triple)
        + f"  {'OK' if cond else 'FAIL'}")
    ok &= cond

    log(f"\n  {'ALL PASS' if ok else 'FAILURES PRESENT'}")
    return 0 if ok else 1


# ═══════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════

def main() -> int:
    ap = argparse.ArgumentParser(description="Asymmetric-pathway quantization A/B")
    ap.add_argument("--model", default="Qwen/Qwen3-8B-Base")
    ap.add_argument("--device",
                    default="mps" if torch.backends.mps.is_available() else "cpu")
    ap.add_argument("--max-tokens", type=int, default=32768)
    ap.add_argument("--seq-len", type=int, default=512)
    ap.add_argument("--stride", type=int, default=256)
    ap.add_argument("--configs", default="all",
                    help="comma list of config keys, or 'all'")
    ap.add_argument("--self-test", action="store_true")
    ap.add_argument("--out-dir", default="results/asymmetric-pathway-quant")
    args = ap.parse_args()

    if args.self_test:
        return self_test()

    all_cfgs = build_configs()
    if args.configs == "all":
        keys = list(all_cfgs.keys())
    else:
        keys = [k.strip() for k in args.configs.split(",")]
        for k in keys:
            if k not in all_cfgs:
                raise SystemExit(f"unknown config '{k}'; have {list(all_cfgs)}")

    run_id = time.strftime("%Y%m%d-%H%M%S")
    out_dir = os.path.join(args.out_dir, f"{args.model.split('/')[-1]}-{run_id}")
    os.makedirs(out_dir, exist_ok=True)

    log("═══ Asymmetric-Pathway Quantization A/B ═══")
    log(f"Model:   {args.model}")
    log(f"Device:  {args.device}")
    log(f"Tokens:  {args.max_tokens} (seq={args.seq_len} stride={args.stride})")
    log(f"Configs: {keys}")
    log(f"Out:     {out_dir}\n")

    from transformers import AutoModelForCausalLM, AutoTokenizer

    tok = AutoTokenizer.from_pretrained(args.model)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token

    log("Loading model (fp32)...")
    model = AutoModelForCausalLM.from_pretrained(args.model, torch_dtype=torch.float32)
    model = model.to(args.device)
    n_layers = len(get_model_layers(model))
    log(f"  {n_layers} layers on {args.device}")

    log("Loading WikiText-2 test...")
    text = load_eval_text(args.max_tokens)

    log("Caching original FFN weights...")
    orig = cache_ffn_weights(model)
    log(f"  cached {len(orig)} FFN matrices\n")

    # provenance
    try:
        import transformers
        tv = transformers.__version__
    except Exception:
        tv = "?"
    meta = {
        "run_id": run_id,
        "timestamp_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "model": args.model,
        "device": args.device,
        "n_layers": n_layers,
        "max_tokens": args.max_tokens,
        "seq_len": args.seq_len,
        "stride": args.stride,
        "scope": "FFN only (gate/up/down); attention fp32",
        "torch": torch.__version__,
        "transformers": tv,
        "configs": {k: {"label": all_cfgs[k].label,
                        "gate": all_cfgs[k].gate[0], "up": all_cfgs[k].up[0],
                        "down": all_cfgs[k].down[0],
                        "mean_bits": all_cfgs[k].mean_bits} for k in keys},
    }
    with open(os.path.join(out_dir, "meta.json"), "w") as f:
        json.dump(meta, f, indent=2)

    results = []
    for k in keys:
        cfg = all_cfgs[k]
        log(f"{'─' * 66}")
        log(f"Config: {cfg.label}  (mean_bits={cfg.mean_bits:.3f})")
        t0 = time.time()
        if cfg.is_float:
            restore_ffn(model, orig, args.device)
            cos = {n: 1.0 for n in WEIGHT_NAMES_FFN}
        else:
            restore_ffn(model, orig, args.device)
            cos = apply_config(model, cfg, orig, args.device)
        q_t = time.time() - t0
        log(f"  cosine  gate={cos['gate_proj']:.4f} up={cos['up_proj']:.4f} "
            f"down={cos['down_proj']:.4f}  ({q_t:.1f}s)")
        log("  evaluating PPL...")
        ev = evaluate_perplexity(model, tok, args.device, text,
                                 args.max_tokens, args.seq_len, args.stride)
        log(f"  loss = {ev['loss']:.4f} nats   PPL = {ev['ppl']:.3f}\n")
        results.append({
            "config": k, "label": cfg.label, "mean_bits": cfg.mean_bits,
            "gate": cfg.gate[0], "up": cfg.up[0], "down": cfg.down[0],
            "cosine": cos, "loss": ev["loss"], "ppl": ev["ppl"],
        })
        # incremental save (crash-safe)
        with open(os.path.join(out_dir, "summary.json"), "w") as f:
            json.dump({"meta": meta, "results": results}, f, indent=2)

    # ═══ Report ═══
    log(f"{'═' * 78}")
    log("SUMMARY — Asymmetric-Pathway Quantization")
    log(f"{'═' * 78}")
    log(f"{'Config':<44} {'mean_bits':>9} {'loss(nats)':>11} {'PPL':>12}")
    log(f"{'─' * 44} {'─' * 9} {'─' * 11} {'─' * 12}")
    for r in sorted(results, key=lambda x: x["mean_bits"]):
        log(f"{r['label']:<44} {r['mean_bits']:>9.3f} "
            f"{r['loss']:>11.4f} {r['ppl']:>12.3f}")

    by = {r["config"]: r for r in results}
    base = by.get("float")

    def dloss(k):
        return (by[k]["loss"] - base["loss"]) if (base and k in by) else float("nan")

    log("\nCRUX 1 - Pareto (does binary-router+3bit-value beat the uniform frontier?):")
    log("  (lower loss = better; dLoss = excess nats vs float)")
    for k in ("uniform_ternary", "uniform_2bit", "uniform_3bit",
              "asym_binR_2V", "asym_binR_3V"):
        if k in by:
            log(f"  {by[k]['label']:<44} bits={by[k]['mean_bits']:.2f} "
                f"loss={by[k]['loss']:.4f} (dLoss={dloss(k):+.4f})")

    log("\nCRUX 2 - Matched-bits null triple (all 2.33b): "
        "where does binarization hurt least?")
    triple = ["asym_binR_3V", "inv_binDown", "inv_binValue"]
    where = {"asym_binR_3V": "binary on ROUTER (gate)",
             "inv_binDown": "binary on ONE value matrix (down)",
             "inv_binValue": "binary on WHOLE value path (up+down)"}
    ref = by.get("asym_binR_3V")
    for k in triple:
        if k in by:
            r = by[k]
            rel = ""
            if ref and math.isfinite(ref["loss"]) and math.isfinite(r["loss"]):
                rel = f"  (dLoss vs router-binary = {r['loss'] - ref['loss']:+.4f})"
            log(f"  {where[k]:<40} loss={r['loss']:.4f}{rel}")
    log("  prediction (two-registers): ROUTER << one-value << whole-value")

    with open(os.path.join(out_dir, "summary.json"), "w") as f:
        json.dump({"meta": meta, "results": results}, f, indent=2)
    log(f"\nSaved → {out_dir}/summary.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
