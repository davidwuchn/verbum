#!/usr/bin/env python3
"""RLVR Design-1 reward smoke — the verifiable reward, on the real canonical corpus.

THE POINT (session 241). `spliced-reward-vsm-kernel.md` build path step 2: "RLVR with
Design 1 (symbolic kernel as external verifiable reward) — works *today*; the s226
reduction-equality grader is the reward fn." This script proves the REWARD side of that
loop works on real data with NO GPU: load the canonical corpus, grade each gold output
through `verbum.reward`, and show the reward is (a) DENSE at cold-start (gold certifies)
and (b) DISCRIMINATIVE (perturb a gold output → reward drops).

Design 1 = external symbolic reward (CPU `lambda_ast`): rollout → reward. Exact, slow,
separate pass, non-differentiable. The GPU policy-gradient loop (GRPO) sits on top of
this reward; it is gated on the OPEN decisions (spliced-reward §7 parent axis, §8
cold-start) and is NOT built here. This is the reward, grounded.

Usage:
  uv run python scripts/experiments/rlvr_design1_reward_smoke.py
  uv run python scripts/experiments/rlvr_design1_reward_smoke.py \
      --split compile-test.canonical.jsonl

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))

from verbum.reward import RewardConfig, reward  # noqa: E402

CFG = RewardConfig(parse="surface")


def perturb(output: str) -> tuple[str | None, str | None]:
    """A semantics-changing perturbation of a surface output (→ a different NF).

    Two deterministic mutations: swap the two arguments of the first binary predicate
    `f(a, b)` → `f(b, a)`; else rename the first predicate atom. Both change the kernel
    term and therefore the normal form — the candidate still parses/types/halts but the
    outcome anchor must drop to 0. Returns (None, None) if nothing applies.
    """
    m = re.search(r"(\w+)\(\s*([^(),]+?)\s*,\s*([^(),]+?)\s*\)", output)
    if m:
        head, a, b = m.group(1), m.group(2).strip(), m.group(3).strip()
        if a != b:
            swapped = output[: m.start()] + f"{head}({b}, {a})" + output[m.end():]
            return swapped, "swap-args"
    m2 = re.search(r"[a-z_]\w*", output)
    if m2 and m2.group(0) not in ("x", "y", "z"):
        return output[: m2.start()] + "novelpred" + output[m2.end():], "rename-pred"
    return None, None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--split", default="compile-train.canonical.jsonl")
    args = ap.parse_args()

    path = ROOT / "data" / args.split
    rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
    n = len(rows)

    channel_keys = [
        "parsed", "well_typed", "halts_in_budget", "size_ok",
        "reduces_correct", "trace_prefix_frac",
    ]
    sums = dict.fromkeys(channel_keys, 0.0)
    gold_reward_sum = gold_dense_sum = 0.0
    failures: list[dict] = []

    # perturbation discrimination (paired, only on rows we can perturb)
    pert_pairs: list[tuple[float, float]] = []
    pert_kinds: dict[str, int] = {}

    for r in rows:
        out, gold_nf = r["output"], r["normal_form"]
        res = reward(out, gold_nf, CFG)
        gold_reward_sum += res.reward
        gold_dense_sum += res.dense
        for k, v in res.channels.as_scores().items():
            sums[k] += v
        if res.reward < 1.0:
            failures.append({
                "input": r.get("input"), "output": out, "gold_nf": gold_nf,
                "got_nf": res.channels.nf, "status": res.channels.status,
                "error": res.channels.error,
            })
        # discrimination
        pout, kind = perturb(out)
        if pout is not None and pout != out:
            pres = reward(pout, gold_nf, CFG)
            pert_pairs.append((res.reward, pres.reward))
            pert_kinds[kind] = pert_kinds.get(kind, 0) + 1  # type: ignore[index]

    gold_correct_rate = gold_reward_sum / n
    chan_means = {k: round(sums[k] / n, 4) for k in channel_keys}
    gold_mean = sum(g for g, _ in pert_pairs) / max(len(pert_pairs), 1)
    pert_mean = sum(p for _, p in pert_pairs) / max(len(pert_pairs), 1)

    out = {
        "split": args.split,
        "n": n,
        "reward_density_at_coldstart": round(gold_correct_rate, 4),
        "gold_dense_mean": round(gold_dense_sum / n, 4),
        "channel_means": chan_means,
        "n_failures": len(failures),
        "discrimination": {
            "n_perturbed": len(pert_pairs),
            "kinds": pert_kinds,
            "gold_mean_reward": round(gold_mean, 4),
            "perturbed_mean_reward": round(pert_mean, 4),
            "drop": round(gold_mean - pert_mean, 4),
        },
        "failures": failures[:20],
    }
    out_dir = ROOT / "results" / "rlvr-design1-reward"
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "summary.json").write_text(json.dumps(out, indent=2, ensure_ascii=False))

    # ---- printout ----
    print(f"=== RLVR Design-1 verifiable reward — {args.split} (n={n}) ===")
    print(f"\nREWARD DENSITY @ cold-start (gold reduces_correct): "
          f"{gold_correct_rate:.1%}  ({int(gold_reward_sum)}/{n})")
    print(f"gold dense-reward mean: {gold_dense_sum / n:.3f}")
    print("\nper-channel means (gold outputs):")
    for k in channel_keys:
        print(f"  {k:18s} {chan_means[k]:.3f}")
    print(f"\nDISCRIMINATION (perturbed {len(pert_pairs)} rows, kinds={pert_kinds}):")
    print(f"  gold   mean reward = {gold_mean:.3f}")
    print(f"  perturb mean reward = {pert_mean:.3f}")
    print(f"  drop = {gold_mean - pert_mean:.3f}  "
          f"({'DISCRIMINATES' if pert_mean < gold_mean else 'NO DROP'})")
    if failures:
        print(f"\n{len(failures)} gold rows did NOT reduce_correct (e.g.):")
        for f in failures[:6]:
            print(f"  out={f['output']!r}")
            print(f"      gold_nf={f['gold_nf']!r} got={f['got_nf']!r} "
                  f"status={f['status']} err={f['error']}")
    print(f"\nwrote {out_dir}/summary.json")


if __name__ == "__main__":
    main()
