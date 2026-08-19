#!/usr/bin/env python3
"""Exploratory: WHERE does the model do MATH? — point the audited opcode tracer at
a task-typed battery and read the per-layer combinator program.

Michael's redirect (s344+): "with our ability to trace opcodes we should be able to
find where a model does math; in past probes the system used the I combinator for
math as if it were Church encoding." Grounded on disk — tracer-works-different-
programs (s127, 14B): "ARITHMETIC ... uses selectors (β_identity, β_K, β_apply) ...
this is church encoding — numbers are selectors"; isa-decoder-qwen36-27b (s161):
"Arithmetic: 33% β_I (identity) ... β_I dominates early, β_K dominates late. Numbers
ARE selectors." And the CONTRAST: date-fourier-rotation — date arithmetic uses
geometric ROTATION, not Church encoding. Math is NOT monolithic.

This harness REUSES opcodes/{topology,capture,classify,probes} — the null-gated,
register-correct combinator reader (sign(gate) routing register, common-mode removed,
z>thresh vs a shuffled-label null floor, tokens can NO-OP; over-read killed, audit
#13). NO re-implemented reader. It calibrates ONCE on the bundled crystal probes,
then traces a TASK-TYPED battery and reports, per task and per crystal layer, the
per-layer opcode distribution and the β_I (identity) selection fraction — for
arithmetic (Church-numeral candidate) vs modular/date (rotation candidate) vs matched
non-arithmetic controls (retrieval — combinator-silent per s127 — and plain prose).

EXPLORATORY (instrument-only, look-first, no verdict tree / no a-priori): the output
FEEDS the next design; it does not close/open a claim (λ observation). The disciplines
we care about are already in the tool: register-correctness + the shuffled-label null
+ NO-OP. The question we LOOK at: (a) does arithmetic read β_I-dominant late (s127/
s161)? (b) does its I-fraction EXCEED the matched control (over-read guard)? (c) does
modular/date read DIFFERENTLY (rotation dissociation)?

License: MIT.
"""

from __future__ import annotations

import argparse
import json
import sys
from collections import Counter
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import numpy as np

_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_ROOT / "opcodes"))

from trace import calibrate_register  # noqa: E402 (canonical calibration, reused)

import capture as C  # noqa: E402
import topology as T  # noqa: E402
from classify import CRYSTAL  # noqa: E402

RESULTS_DIR = _ROOT / "results" / "arith_trace"
I_IDX = CRYSTAL.index("I")

# --------------------------------------------------------------------------
# Task-typed battery (last token ends at the compute-commit locus where useful)
# --------------------------------------------------------------------------
BATTERY: dict[str, list[str]] = {
    # small-integer addition — the cleanest Church-numeral case
    "arith_add": [
        "2 + 3 =", "7 + 1 =", "4 + 5 =", "6 + 2 =",
        "3 + 8 =", "9 + 4 =", "1 + 6 =", "5 + 5 =",
    ],
    # successor / "one more" — Church succ
    "arith_succ": [
        "The number after 4 is", "One more than 7 is",
        "The next number after 12 is", "Two more than 5 is",
        "The number just after 9 is", "One after 20 is",
        "Add one to 8 to get", "The successor of 3 is",
    ],
    # multiplication — Church mult (composition of numerals)
    "arith_mul": [
        "2 * 3 =", "3 * 4 =", "6 * 2 =", "5 * 5 =",
        "4 * 3 =", "7 * 2 =", "2 * 8 =", "3 * 3 =",
    ],
    # modular / cyclic arithmetic — the ROTATION candidate (date-fourier contrast)
    "mod_date": [
        "3 days after Monday is", "5 months after January is",
        "2 days after Friday is", "10 o'clock plus 4 hours is",
        "4 months after October is", "6 days after Wednesday is",
        "9 o'clock plus 5 hours is", "3 months after November is",
    ],
    # retrieval control — combinator-silent per s127
    "ctrl_retrieval": [
        "The capital of France is", "The author of Hamlet is",
        "The largest planet is", "The tallest mountain is",
        "The chemical symbol for gold is", "The capital of Japan is",
        "The longest river is", "The first president was",
    ],
    # plain-prose control — no computation
    "ctrl_prose": [
        "The sky was clear this morning.", "She walked to the store yesterday.",
        "Music played softly in the room.", "The old house stood on the hill.",
        "He drinks coffee every morning.", "Rain fell throughout the night.",
        "The garden was full of color.", "They watched a film last weekend.",
    ],
}


def _trace_group(model: Any, tok: Any, topo: T.ModelTopology, rcc: Any,
                 prompts: list[str], layers: list[int], z_thresh: float,
                 register: str) -> dict:
    """Per crystal-layer opcode distribution over a task group, both for ALL
    token positions and for the LAST position (the compute-commit locus)."""
    crystal = sorted(rcc.crystal_layers)
    votes_all: dict[int, Counter] = {li: Counter() for li in crystal}
    votes_last: dict[int, Counter] = {li: Counter() for li in crystal}
    n_tok = noop_all = 0
    n_last = noop_last = 0
    for prompt in prompts:
        cap = C.capture_gate(model, tok, prompt, topo=topo, layers=layers,
                             register=register)
        last = cap.n_tokens - 1
        for pos in range(1, cap.n_tokens):  # skip BOS/first
            gate_tok = {li: cap.gate[li][pos] for li in layers}
            res = rcc.classify(gate_tok)
            fired = False
            for li in crystal:
                zmap = res.per_layer.get(li)
                if not zmap:
                    continue
                op = max(zmap, key=zmap.get)
                if zmap[op] > z_thresh:
                    votes_all[li][op] += 1
                    if pos == last:
                        votes_last[li][op] += 1
                    fired = True
            n_tok += 1
            if pos == last:
                n_last += 1
                if not fired:
                    noop_last += 1
            if not fired:
                noop_all += 1

    def _layer_summary(votes: dict[int, Counter]) -> dict:
        out = {}
        for li in crystal:
            v = votes[li]
            tot = sum(v.values())
            if tot == 0:
                out[li] = {"win": "·", "fires": 0, "I_frac": 0.0, "dist": {}}
                continue
            win, _ = v.most_common(1)[0]
            out[li] = {"win": win, "fires": tot,
                       "I_frac": round(v.get("I", 0) / tot, 4),
                       "dist": dict(v)}
        return out

    la = _layer_summary(votes_all)
    ll = _layer_summary(votes_last)

    def _i_rate(votes: dict[int, Counter], lo: float, hi: float) -> float:
        sel = [li for li in crystal
               if lo <= (crystal.index(li) / max(1, len(crystal) - 1)) < hi]
        iv = sum(votes[li].get("I", 0) for li in sel)
        tv = sum(sum(votes[li].values()) for li in sel)
        return round(iv / tv, 4) if tv else 0.0

    return {
        "n_crystal_layers": len(crystal),
        "n_tokens": n_tok, "noop_rate_all": round(noop_all / n_tok, 4) if n_tok else 0,
        "noop_rate_last": round(noop_last / n_last, 4) if n_last else 0,
        "I_rate_all": _i_rate(votes_all, 0.0, 1.0),
        "I_rate_last": _i_rate(votes_last, 0.0, 1.0),
        "I_rate_early_all": _i_rate(votes_all, 0.0, 0.5),
        "I_rate_late_all": _i_rate(votes_all, 0.5, 1.001),
        "per_layer_all": {str(k): v for k, v in la.items()},
        "per_layer_last": {str(k): v for k, v in ll.items()},
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--model", default="Qwen/Qwen3-0.6B")
    ap.add_argument("--device", default="mps", choices=["cpu", "mps", "cuda"])
    ap.add_argument("--register", default="gate", choices=["gate", "attn"])
    ap.add_argument("--probes-per-comb", type=int, default=None)
    ap.add_argument("--n-perm", type=int, default=300)
    ap.add_argument("--z", type=float, default=3.0)
    ap.add_argument("--smoke", action="store_true")
    args = ap.parse_args()

    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    ppc = 15 if args.smoke else args.probes_per_comb
    n_perm = 120 if args.smoke else args.n_perm

    tok = AutoTokenizer.from_pretrained(args.model)
    model = AutoModelForCausalLM.from_pretrained(
        args.model, dtype=torch.bfloat16, low_cpu_mem_usage=True).eval()
    if args.device != "cpu":
        model = model.to(args.device)
    topo = T.detect_topology(model, model.config)
    print(f"[arith] {args.model} | {topo.summary()}")
    if args.register == "gate" and not topo.traceable:
        print("[arith] REFUSED: gate register not traceable on this arch.")
        return 2

    layers = list(range(topo.n_layers))
    rcc, summ, _ = calibrate_register(
        model, tok, topo, args.register, layers, ppc, n_perm, args.z)
    print(f"[arith] crystal-bearing layers: {len(summ['crystal_layers'])}"
          f"/{topo.n_layers}")

    groups: dict[str, dict] = {}
    for name, prompts in BATTERY.items():
        groups[name] = _trace_group(model, tok, topo, rcc, prompts, layers,
                                    args.z, args.register)
        g = groups[name]
        print(f"[arith] {name:16s} I_all={g['I_rate_all']:.3f} "
              f"(early {g['I_rate_early_all']:.3f} / late {g['I_rate_late_all']:.3f}) "
              f"I_last={g['I_rate_last']:.3f} noop_last={g['noop_rate_last']:.3f}")

    # over-read guard + rotation dissociation summary
    arith = ["arith_add", "arith_succ", "arith_mul"]
    ctrl = ["ctrl_retrieval", "ctrl_prose"]
    arith_I = float(np.mean([groups[g]["I_rate_late_all"] for g in arith]))
    ctrl_I = float(np.mean([groups[g]["I_rate_late_all"] for g in ctrl]))
    mod_I = groups["mod_date"]["I_rate_late_all"]
    print("=" * 64)
    print(f"[arith] LATE I-selection: arithmetic {arith_I:.3f} | "
          f"control {ctrl_I:.3f} | mod/date {mod_I:.3f}")
    print(f"[arith] arithmetic - control = {arith_I - ctrl_I:+.3f} "
          f"(over-read guard: want > 0); arithmetic - mod/date = "
          f"{arith_I - mod_I:+.3f} (rotation dissociation: want > 0)")

    slug = args.model.split("/")[-1].lower().replace(".", "-")
    out_dir = RESULTS_DIR / slug / args.register  # per-register (don't clobber)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = {
        "note": "EXPLORATORY opcode trace of a task-typed battery (where does "
                "math happen?); reuses the audited opcodes/ reader; no verdict",
        "model": args.model, "device": args.device, "register": args.register,
        "z_thresh": args.z, "n_perm": n_perm, "probes_per_comb": ppc,
        "smoke": bool(args.smoke), "timestamp_utc": datetime.now(UTC).isoformat(),
        "crystal_layers": summ["crystal_layers"],
        "n_layers": topo.n_layers,
        "summary": {
            "arith_late_I": round(arith_I, 4), "ctrl_late_I": round(ctrl_I, 4),
            "mod_date_late_I": round(mod_I, 4),
            "arith_minus_ctrl": round(arith_I - ctrl_I, 4),
            "arith_minus_mod": round(arith_I - mod_I, 4),
        },
        "groups": groups,
    }
    (out_dir / "arith_trace.json").write_text(json.dumps(out, indent=2, default=str))
    print(f"[arith] wrote {out_dir}/arith_trace.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
