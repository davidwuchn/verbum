#!/usr/bin/env python3
"""Paired overlay: frozen-topology probe (TD-off) vs main:1 (TD-on).

Both runs resume the SAME step_001000 checkpoint with the SAME data-loader
state and the SAME cosine schedule (--steps 5000). The ONLY difference is the
ternary sign topology: main:1 ran TD (td=124488/interval); the probe froze it
(td=0). So a step-aligned diff of Δx / CE / gnorm isolates the causal effect of
TD churn on contractivity.

Verdict read (functional register)
----------------------------------
main:1 diverged on this data: Δx 0.25->0.79, gnorm 14->1e7, CE 8.1->10.5,
onset ~step 1450. If the frozen probe holds Δx bounded and CE < 8.71 across the
SAME steps (esp. 1450-1700), TD churn was the divergence cause.

Usage
-----
  freeze_probe_overlay.py --tdon /tmp/v15_outer_k2_fp5_5k.log \
      --tdoff /tmp/v15_freeze_probe.log [--from 1000 --to 1700]
"""
from __future__ import annotations

import argparse
import re

STEP_RE = re.compile(
    r"step\s+(\d+).*?CE=([\d.]+).*?gnorm\s+([\d.eE+]+).*?"
    r"Δx=\[([\d.]+)\].*?fp=([\d.]+)"
)
AVG_RE = re.compile(r"avg50:\s*([\d.]+)")


def parse(path: str) -> dict[int, dict]:
    rows = {}
    with open(path, encoding="utf-8", errors="replace") as fh:
        for line in fh:
            if not line.startswith("step"):
                continue
            m = STEP_RE.search(line)
            if not m:
                continue
            step = int(m.group(1))
            avg = AVG_RE.search(line)
            rows[step] = {
                "ce": float(m.group(2)),
                "gnorm": float(m.group(3)),
                "dx": float(m.group(4)),
                "fp": float(m.group(5)),
                "avg50": float(avg.group(1)) if avg else float("nan"),
            }
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--tdon", required=True, help="main:1 TD-on log")
    ap.add_argument("--tdoff", required=True, help="frozen probe TD-off log")
    ap.add_argument("--from", dest="lo", type=int, default=1000)
    ap.add_argument("--to", dest="hi", type=int, default=10**9)
    args = ap.parse_args()

    on = parse(args.tdon)
    off = parse(args.tdoff)
    steps = sorted(s for s in set(on) | set(off) if args.lo <= s <= args.hi)

    hdr = (
        f"{'step':>6} | {'Δx ON':>7} {'Δx OFF':>7} | "
        f"{'CE ON':>6} {'CE OFF':>6} | {'gnorm ON':>10} {'gnorm OFF':>10} | "
        f"{'avg50 ON':>8} {'avg50 OFF':>8}"
    )
    print(hdr)
    print("-" * len(hdr))
    last = {}
    for s in steps:
        a, b = on.get(s), off.get(s)
        if a is None and b is None:
            continue
        # only print on a coarse grid + always print both-present rows
        if s % 50 != 0 and not (a and b):
            continue

        def f(d, k, w, p=3):
            return f"{d[k]:>{w}.{p}f}" if d else f"{'-':>{w}}"

        def g(d, w):
            return f"{d['gnorm']:>{w}.2e}" if d else f"{'-':>{w}}"

        print(
            f"{s:>6} | {f(a,'dx',7)} {f(b,'dx',7)} | "
            f"{f(a,'ce',6,2)} {f(b,'ce',6,2)} | {g(a,10)} {g(b,10)} | "
            f"{f(a,'avg50',8,2)} {f(b,'avg50',8,2)}"
        )
        last = {"a": a, "b": b, "s": s}

    # verdict summary over the overlap window
    common = sorted(set(on) & set(off) & set(steps))
    if common:
        import statistics as st

        dx_on = [on[s]["dx"] for s in common]
        dx_off = [off[s]["dx"] for s in common]
        ce_on = [on[s]["ce"] for s in common]
        ce_off = [off[s]["ce"] for s in common]
        gn_on = [on[s]["gnorm"] for s in common]
        gn_off = [off[s]["gnorm"] for s in common]
        print(
            f"\n=== overlap window verdict "
            f"({common[0]}-{common[-1]}, n={len(common)}) ==="
        )
        print(f"  Δx     ON mean={st.mean(dx_on):.3f} max={max(dx_on):.3f} | "
              f"OFF mean={st.mean(dx_off):.3f} max={max(dx_off):.3f}")
        print(f"  CE     ON mean={st.mean(ce_on):.3f} max={max(ce_on):.3f} | "
              f"OFF mean={st.mean(ce_off):.3f} max={max(ce_off):.3f}")
        print(f"  gnorm  ON max={max(gn_on):.2e} | OFF max={max(gn_off):.2e}")
        print(f"  CE<8.71 frac:  ON={sum(c<8.71 for c in ce_on)/len(ce_on):.2f} "
              f"OFF={sum(c<8.71 for c in ce_off)/len(ce_off):.2f}")
    elif last:
        print("\n(no overlapping steps yet; probe still early)")


if __name__ == "__main__":
    main()
