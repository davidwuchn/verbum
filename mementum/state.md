# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-03 | Session: 063

## Where we are

**v10 BUILT. Strided compressor + tree of VSMs. Ready to train at scale.**

Session 062 pivoted away from proxy metrics (basin projectors, 6 sessions,
peak 0.743 — cosine sim to oracle ≠ functional capability). Four probes
on Qwen3-32B established the design constraints:

- Compression IS typing — no special layer needed
- The 32B doesn't build trees — we provide them
- Types = bindings — cosine proximity predicts binding at L28
- CompressorLM preserves 80-91% of 32B's signal

→ See [session-062-probes](knowledge/explore/session-062-probes.md)
→ See [basin-projector-results](knowledge/explore/basin-projector-results.md)

## v10 architecture

```
tokens → [Strided Compressor W=8, strides 1/8/64, 2× iter] → compressed
       → [Tree of VSMs — shared-weight VSMNode, 22 ops, 5 types]
       → result (trained end-to-end on correct computation)
```

Smoke test: 60 steps, loss 3.03→2.43, op accuracy 30%→65%.

## What to do next

### 1. Run v10 training at scale
```bash
uv run python scripts/v10/train.py --d-model 256 --seq-len 128 --total-steps 20000
```
Target: >90% op accuracy, >80% result accuracy. Start seq=128, scale later.

### 2. Cross-notation bridge
Add math notation to data pipeline. Same kernel, different parser.
Test notation-invariant representations.

### 3. Prose
The hard problem. Parser uses cosine proximity for binding (Probe 3).

### 4. Kernel extension
- Layer 2: Mask ops (bitmask positions = list type)
- Layer 3: Scope/binding (let, lambda, var_ref)

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/model.py` | Strided compressor + VSMNode tree |
| `scripts/v10/train.py` | Training with evolution + checkpoints |
| `scripts/v10/data.py` | S-expr tokenizer, tree parser, generators |
| `scripts/v10/kernel.py` | 22-op exact kernel |
| `scripts/v10/config.py` | V10Config dataclass |
| `scripts/v10/ternary.py` | Ternary weight substrate |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
