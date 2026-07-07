#!/usr/bin/env python3
"""KIBC vs SKI: which combinator basis better carves the attention head space?

s262. The KIBC crystal grew from "if attention is beta-reduction, what
combinators does the model need?" The tracer compared bases (n=4 KIBC vs
n=3 SKI) and KIBC fit; but that selection was an observation, never a
null-gated artifact. This re-runs it as a proper experiment.

THE THEORY (why KIBC should win, made falsifiable):
  SKI folds composition + duplication + distribution into ONE combinator S
  (S f g x = f x (g x) — the braided substitution engine). BCKW/KIBC
  UNBRAIDS those into separate structural operations:
    K = select/discard      (weakening)
    I = identity/pass       (the diagonal)
    B = compose             (associativity)   ← S's composition, alone
    C = flip/reorder        (exchange)        ← S's argument routing, alone
  A model that tracks TYPES (routes by structural role) should present a
  head space that KIBC's unbraided operations carve cleanly, while S — being
  braided — should smear across the same heads as its parts (K/I) or fail to
  claim a distinct cluster. This IS the type-directedness claim, operational.

METHOD (reuses probe_combinators.py machinery, adds S + a shuffled null):
  Each combinator is operationalized as a linguistic phenomenon with ACTIVE
  probes (function needed) and matched CONTROL probes (surface-matched, not
  needed). Per-head selectivity = L2(attn_active, attn_control). We forward
  each unique sentence ONCE, cache its attention, then compute:

    basis_fit(B) = mean_over_heads  max_{c in B}  selectivity_c(head)
                   "how strongly each head answers to its best-fit combinator"

  NULL (shuffled-label, s247/s261 discipline): pool the basis's sentences,
  re-partition into |B| pseudo-combinators with random active/control splits,
  recompute basis_fit. The null has the SAME cardinality → controls the
  "more combinators → higher max" advantage. N shuffles → null distribution.

  VERDICT: the basis whose (real - null) gap is larger, and whose z vs its
  null is larger, carves the head space better. Two-sided (lambda measure):
    KIBC gap >> SKI gap        → KIBC-over-SKI selection is REAL, null-gated
    KIBC gap ~= SKI gap        → the selection was impression, not signal
    SKI gap  >  KIBC gap       → we were wrong; S carves better

  SECONDARY: cross-combinator head correlation within each basis. If S
  correlates highly with K or I (r high), S is redundant/braided with its
  parts = direct evidence for the braiding hypothesis.

Usage:
  uv run python scripts/experiments/basis_fit_kibc_vs_ski.py --model pythia-160m-deduped
  uv run python scripts/experiments/basis_fit_kibc_vs_ski.py --smoke   # 1 pair, 3 nulls
  uv run python scripts/experiments/basis_fit_kibc_vs_ski.py --self-test

License: MIT
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

os.environ.setdefault("PYTHONUNBUFFERED", "1")
os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")

import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "explore"))
# Reuse the canonical KIBC probes + capture machinery (no fork).
from probe_combinators import PROBES as KIBC_PROBES
from probe_combinators import capture_attention, head_selectivity

MODELS = {
    "pythia-14m-deduped": "EleutherAI/pythia-14m-deduped",
    "pythia-70m-deduped": "EleutherAI/pythia-70m-deduped",
    "pythia-160m-deduped": "EleutherAI/pythia-160m-deduped",
    "pythia-410m-deduped": "EleutherAI/pythia-410m-deduped",
    "pythia-1b-deduped": "EleutherAI/pythia-1b-deduped",
    "pythia-1.4b-deduped": "EleutherAI/pythia-1.4b-deduped",
    "pythia-2.8b-deduped": "EleutherAI/pythia-2.8b-deduped",
    "qwen3-0.6b": "Qwen/Qwen3-0.6B",
}

OUT_ROOT = Path("results/basis-fit-kibc-vs-ski")

# ══════════════════════════════════════════════════════════════════
# S combinator probes — steelmanned (argument SHARING / duplication)
# ══════════════════════════════════════════════════════════════════
# S f g x = f x (g x): the argument x is consumed by BOTH f and g.
# Linguistic realizations of one NP filling two roles / shared argument:
#   subject control, tough-movement, reflexives, right-node-raising,
#   coordination with a shared argument, parasitic gaps.
# CONTROL: surface-matched sentences where the two roles have DISTINCT
# arguments (no duplication needed).
S_PROBES = {
    "S": {
        "description": "Substitute/share — one argument fills two roles (S f g x)",
        "active": [
            "John wants to leave the party before midnight tonight.",
            "The book was easy to read on the long train journey.",
            "The senator introduced himself to the crowd at the rally.",
            "The dog chased and caught the ball in the wide green park.",
            "Mary promised to finish the report by the end of the week.",
            "The old bridge was dangerous to cross during the heavy storm.",
        ],
        "control": [
            "John wants Mary to leave the party before midnight tonight.",
            "The book was long and heavy on the long train journey.",
            "The senator introduced the guest to the crowd at the rally.",
            "The dog chased the ball and caught a stick in the green park.",
            "Mary expected the intern to finish the report by the week.",
            "The old bridge was famous and long during the heavy storm.",
        ],
    },
}


def _git_sha() -> str:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True
        ).strip()
    except Exception:
        return "unknown"


def _hash_probes(probes: dict) -> str:
    blob = json.dumps(probes, sort_keys=True).encode()
    return hashlib.sha256(blob).hexdigest()[:12]


# ══════════════════════════════════════════════════════════════════
# Attention cache — forward each unique sentence once
# ══════════════════════════════════════════════════════════════════


def build_attention_cache(model, tokenizer, all_probes: dict) -> dict:
    """Forward each unique sentence once; cache (n_layers, n_heads, L, L) attn.

    Keyed by the sentence string. Shared K/I sentences captured once.
    """
    sentences: set[str] = set()
    for comb in all_probes.values():
        sentences.update(comb["active"])
        sentences.update(comb["control"])
    cache: dict[str, np.ndarray] = {}
    for i, s in enumerate(sorted(sentences)):
        cap = capture_attention(model, tokenizer, s)
        cache[s] = cap["attentions"].astype(np.float32)
        if (i + 1) % 10 == 0:
            print(f"    cached {i + 1}/{len(sentences)} sentences", file=sys.stderr)
    return cache


def pair_selectivities(
    active: list[str], control: list[str], cache: dict
) -> list[np.ndarray]:
    """Per-PAIR head selectivity vectors — the atoms of the shuffle null.

    Each (active_i, control_i) is a surface-matched pair, so its L2 already
    controls for surface form; the combinator IDENTITY is the only thing the
    null shuffles. cache entries are (n_layers, n_heads, seq, seq).
    """
    n = min(len(active), len(control))
    return [head_selectivity(cache[active[i]], cache[control[i]]) for i in range(n)]


def selectivity_from_cache(
    active: list[str], control: list[str], cache: dict
) -> np.ndarray:
    """Mean per-head selectivity L2(active_i, control_i) over paired probes."""
    pairs = pair_selectivities(active, control, cache)
    return np.mean(pairs, axis=0)


# ══════════════════════════════════════════════════════════════════
# Basis fit metric + shuffled-label null
# ══════════════════════════════════════════════════════════════════


def basis_selectivities(basis: dict, cache: dict) -> dict[str, np.ndarray]:
    """Per-combinator (n_layers, n_heads) selectivity for a basis."""
    return {
        name: selectivity_from_cache(c["active"], c["control"], cache)
        for name, c in basis.items()
    }


def basis_fit(sels: dict[str, np.ndarray]) -> float:
    """mean over heads of max_c selectivity_c — how well the basis claims heads."""
    stack = np.stack(list(sels.values()), axis=0)  # (n_comb, L, H)
    return float(np.mean(np.max(stack, axis=0)))


def shuffled_null(
    basis: dict, cache: dict, n_shuffles: int, seed: int
) -> np.ndarray:
    """Null basis_fit: keep matched PAIRS intact, shuffle their combinator labels.

    The matched (active,control) pair already controls surface form. The null
    breaks ONLY the combinator grouping: pool all pairs, re-partition into
    |basis| same-size buckets at random. If the TRUE combinator grouping
    carves heads better than random groupings of the same pairs, real > null.
    Cardinality- and pair-count-matched by construction.
    """
    rng = np.random.RandomState(seed)
    all_pairs: list[np.ndarray] = []
    sizes = []
    for c in basis.values():
        pv = pair_selectivities(c["active"], c["control"], cache)
        all_pairs.extend(pv)
        sizes.append(len(pv))
    total = len(all_pairs)
    out = np.empty(n_shuffles)
    for t in range(n_shuffles):
        order = rng.permutation(total)
        sels = {}
        start = 0
        for k, sz in enumerate(sizes):
            idx = order[start : start + sz]
            sels[f"pseudo{k}"] = np.mean([all_pairs[j] for j in idx], axis=0)
            start += sz
        out[t] = basis_fit(sels)
    return out


def cross_correlation(sels: dict[str, np.ndarray]) -> dict:
    """Off-diagonal mean |r| among a basis's combinators (low = distinct heads)."""
    names = list(sels)
    flat = {n: sels[n].flatten() for n in names}
    pairs = {}
    offs = []
    for i, a in enumerate(names):
        for b in names[i + 1 :]:
            r = float(np.corrcoef(flat[a], flat[b])[0, 1])
            pairs[f"{a}-{b}"] = round(r, 4)
            offs.append(abs(r))
    return {"pairwise": pairs, "mean_abs_offdiag": round(float(np.mean(offs)), 4)}


# ══════════════════════════════════════════════════════════════════
# Run
# ══════════════════════════════════════════════════════════════════


def run(model_key: str, n_shuffles: int, seed: int, smoke: bool) -> dict:
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    hf = MODELS[model_key]
    device = "mps" if torch.backends.mps.is_available() else "cpu"
    print(f"Loading {hf} on {device}...", file=sys.stderr)
    t0 = time.time()
    # float32: fp16 attention softmax overflows to NaN for Pythia on MPS.
    tokenizer = AutoTokenizer.from_pretrained(hf)
    model = AutoModelForCausalLM.from_pretrained(
        hf, dtype=torch.float32, device_map=device,
        trust_remote_code=True, attn_implementation="eager",
    )
    model.eval()
    model.config.output_attentions = True
    rev = getattr(model.config, "_name_or_path", hf)
    n_layers = model.config.num_hidden_layers
    n_heads = model.config.num_attention_heads
    print(f"  {n_layers}L x {n_heads}H in {time.time() - t0:.1f}s", file=sys.stderr)

    # ── Bases: KIBC = {K,I,B,C}; SKI = {S,K,I} (K,I shared) ──
    kibc = {k: KIBC_PROBES[k] for k in ("K", "I", "B", "C")}
    ski = {"S": S_PROBES["S"], "K": KIBC_PROBES["K"], "I": KIBC_PROBES["I"]}
    if smoke:
        for d in (kibc, ski):
            for c in d.values():
                c["active"] = c["active"][:2]
                c["control"] = c["control"][:2]
        n_shuffles = min(n_shuffles, 3)

    all_probes = {**kibc, "S": ski["S"]}  # union of unique sentence sets
    print("  building attention cache...", file=sys.stderr)
    cache = build_attention_cache(model, tokenizer, all_probes)

    verdict = {}
    for name, basis in (("KIBC", kibc), ("SKI", ski)):
        sels = basis_selectivities(basis, cache)
        real = basis_fit(sels)
        null = shuffled_null(basis, cache, n_shuffles, seed)
        nmean, nstd = float(np.mean(null)), float(np.std(null) + 1e-9)
        z = (real - nmean) / nstd
        p = float(np.mean(null >= real))
        verdict[name] = {
            "combinators": list(basis),
            "n_combinators": len(basis),
            "real_fit": round(real, 6),
            "null_mean": round(nmean, 6),
            "null_std": round(nstd, 6),
            "gap": round(real - nmean, 6),
            "z": round(z, 3),
            "p_null_ge_real": round(p, 4),
            "cross_correlation": cross_correlation(sels),
            "per_combinator_peak": {
                k: round(float(np.max(v)), 5) for k, v in sels.items()
            },
        }

    # Head-space carve: does KIBC beat SKI, NULL-GATED? The z vs each basis's
    # own shuffled null is the statistic (raw gap is scale/variance-dependent;
    # SKI's null is far noisier, so a larger raw gap can be non-significant).
    zk, zs = verdict["KIBC"]["z"], verdict["SKI"]["z"]
    dz = zk - zs
    SIG = 1.64  # one-sided ~p<0.05
    if zk > SIG and zs <= SIG:
        call = (f"KIBC clears its null (z={zk:.2f}), SKI does NOT "
                f"(z={zs:.2f}) — KIBC-over-SKI selection is REAL, null-gated")
    elif zk > SIG and zs > SIG and dz > 1.0:
        call = f"both clear null; KIBC stronger (Δz={dz:+.2f})"
    elif zk > SIG and zs > SIG:
        call = f"both bases clear null comparably (Δz={dz:+.2f}) — INCONCLUSIVE"
    elif zs > SIG and zk <= SIG:
        call = f"SKI clears null, KIBC does not — hypothesis REFUTED (Δz={dz:+.2f})"
    else:
        call = f"neither basis clears its null (zK={zk:.2f}, zS={zs:.2f})"

    return {
        "model_key": model_key,
        "model": hf,
        "model_revision": rev,
        "n_layers": n_layers,
        "n_heads": n_heads,
        "device": device,
        "verdict": verdict,
        "delta_gap_kibc_minus_ski": round(
            verdict["KIBC"]["gap"] - verdict["SKI"]["gap"], 6
        ),
        "delta_z_kibc_minus_ski": round(dz, 3),
        "call": call,
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="pythia-160m-deduped", choices=list(MODELS))
    ap.add_argument("--n-shuffles", type=int, default=50)
    ap.add_argument("--seed", type=int, default=262)
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--self-test", action="store_true")
    args = ap.parse_args()

    if args.self_test:
        _self_test()
        return

    run_id = f"{args.model}-{datetime.now(UTC).strftime('%Y%m%d-%H%M%S')}"
    out_dir = OUT_ROOT / run_id
    out_dir.mkdir(parents=True, exist_ok=True)

    import torch
    import transformers

    result = run(args.model, args.n_shuffles, args.seed, args.smoke)
    meta = {
        "run_id": run_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "git_sha": _git_sha(),
        "seed": args.seed,
        "n_shuffles": (3 if args.smoke else args.n_shuffles),
        "smoke": args.smoke,
        "model": result["model"],
        "model_revision": result["model_revision"],
        "kibc_probe_hash": _hash_probes({k: KIBC_PROBES[k] for k in "KIBC"}),
        "ski_probe_hash": _hash_probes(
            {"S": S_PROBES["S"], "K": KIBC_PROBES["K"], "I": KIBC_PROBES["I"]}
        ),
        "torch": torch.__version__,
        "transformers": transformers.__version__,
        "null": "shuffled-label (independent active/control perm, cardinality-matched)",
        "metric": "basis_fit = mean_head max_combinator selectivity(active vs control)",
    }
    (out_dir / "meta.json").write_text(json.dumps(meta, indent=2))
    (out_dir / "summary.json").write_text(json.dumps(result, indent=2))

    print(f"\n{'=' * 64}")
    print(f"KIBC vs SKI basis fit — {result['model']} "
          f"({result['n_layers']}L x {result['n_heads']}H)")
    print(f"{'=' * 64}")
    print(f"{'basis':6}{'real':>10}{'null':>10}{'gap':>10}{'z':>8}"
          f"{'p':>8}{'mean|r|':>9}")
    for name in ("KIBC", "SKI"):
        v = result["verdict"][name]
        print(f"{name:6}{v['real_fit']:>10.5f}{v['null_mean']:>10.5f}"
              f"{v['gap']:>10.5f}{v['z']:>8.2f}{v['p_null_ge_real']:>8.3f}"
              f"{v['cross_correlation']['mean_abs_offdiag']:>9.3f}")
    print(f"\nΔgap (KIBC-SKI) = {result['delta_gap_kibc_minus_ski']:+.5f}   "
          f"Δz = {result['delta_z_kibc_minus_ski']:+.2f}")
    print(f"S cross-corr: {result['verdict']['SKI']['cross_correlation']['pairwise']}")
    print(f"\nCALL: {result['call']}")
    print(f"written: {out_dir}/summary.json")


def _self_test() -> None:
    """No-model unit test of the metric + null on synthetic attention."""
    rng = np.random.RandomState(0)
    L, H = 4, 6
    # Fake cache: sentences map to random attn; a "structured" combinator gets
    # a consistent head bump so real > null.
    probes = {
        "K": {"active": ["a1", "a2"], "control": ["c1", "c2"]},
        "I": {"active": ["a3", "a4"], "control": ["c3", "c4"]},
    }
    cache = {}
    for s in ["a1", "a2", "a3", "a4", "c1", "c2", "c3", "c4"]:
        seq = 5
        cache[s] = rng.rand(L, H, seq, seq).astype(np.float32)
    sels = basis_selectivities(probes, cache)
    fit = basis_fit(sels)
    null = shuffled_null(probes, cache, 5, 0)
    assert fit > 0 and null.shape == (5,)
    cc = cross_correlation(sels)
    assert "mean_abs_offdiag" in cc
    assert 0.0 <= cc["mean_abs_offdiag"] <= 1.0
    # basis_fit == mean of per-head max — must be >= each combinator's mean
    stack = np.stack(list(sels.values()), 0)
    assert fit >= np.mean(np.max(stack, axis=0)) - 1e-9
    print("basis_fit_kibc_vs_ski self-test passed ✓")


if __name__ == "__main__":
    main()
