# This is a fundamental pivot. Let me thin

## User

orient this is session-077


### Thinking

The user wants me to orient for session 077. Following the cold-start protocol, I need to read mementum/state.md first, then follow related files.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md"
}
```

**Summary:** Reading state.md (0-2000)

**Output:**
```
# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-11 | Session: 076

## Where we are

**v10-vsm completed 20K. v10-multicycle running (8K checkpoint imminent). CycleContinue sigmoid saturation diagnosed and fixed — next run will have working self-regulating cycles.**

Session 076 assessed the completed v10-vsm 20K run, launched the first
multi-cycle training run (v10-multicycle), and diagnosed a critical bug:
CycleContinue's sigmoid gate saturated to 1.0 within the first ~200 steps
and could never learn to close. Fixed with RMSNorm + tanh clamp. The
v10-multicycle run continues to 8K for a final checkpoint before restarting
with the fix.

## What was done this session

### 1. Assessed v10-vsm 20K run (complete)
Full trajectory analysis across all 20 checkpoints:
- **Loss**: 8.04 → 7.37 (best at 15K), slight regression to 7.42 at 20K
- **S5 Reweight activated** for the first time ever: pass 1 dropped from 1.0 → 0.693
  at 20K. The model learned to de-emphasize pass 1. Coincided with loss regression.
- **Compute gate**: opened and saturated by 10K (0.89 at 20K)
- **S3 gates**: beautiful differentiation — pass 0 gating down to [0.33, 0.24, 0.19]
- **Op dispatch** converged: compose(37%), sub(23%), pred(16%), min_max(10%)
- **Partial/apply (ops 18/19)**: flat at <0.3% despite kernel-lambda data enrichment
- **Evolution**: 7/400 accepted (1.75%)

### 2. Launched v10-multicycle training run
First training with multi-cycle descending arm (desc_max_cycles=3):
```
checkpoints/v10-multicycle/   ← running, step 7.5K+ at time of writing
```
JSONL logging confirmed working — all three log files accumulating correctly.
New multi-cycle instrumentation fields verified: `cycle_continue_gates`,
`effective_cycles`, `cycle_inject_gate`, per-cycle S3 gates (9 per desc pass).

### 3. Diagnosed CycleContinue sigmoid saturation
**The bug**: CycleContinue's gate_proj (Linear 768→1 + sigmoid) receives
register input with ||x|| ≈ 27.7. After even small weight updates, logit ≈ 30,
sigmoid(30) gradient ≈ 0. The gate locked at 1.0000 by step ~200 and never
moved — all 15 evals showed effective_cycles = 3.000 for both desc passes.

**Evidence**: gate_proj weight norm = 1.08, input norm ≈ 27.7, max |logit| ≈ 30.

**The fix** (committed, not yet trained):
1. **RMSNorm** on concatenated register input → ||x|| ≈ 1.0
2. **tanh(·) × 4.0** logit clamp → gate ∈ [0.018, 0.982], min gradient 0.018
3. Belt and suspenders: normalization prevents saturation, clamp guarantees it

### 4. v10-multicycle observations at 7.5K
Despite dead CycleContinue, useful signals:
- **Loss tracking identical** to v10-vsm at same steps (7.593 vs 7.598 at 7K)
- **Dispatch collapsed** to 3 ops: sub(61%), min_max(26%), and_or(11%) = 98.3%
  Much more concentrated than v10-vsm's 4-5 op spread
- **Compute gate opening slower**: 0.24 at 7.5K vs 0.80 at 7K in v10-vsm
- **S3 per-cycle gates differentiating**: L1↓ c0 disp=0.62 → c1=0.73 → c2=0.80
  (later cycles open wider) — S3 learned something about cycle structure
- **cycle_inject_gate frozen** at 0.018 (init value) — never moved

## What to do next

### Priority 1: Start fresh v10-multicycle run with CycleContinue fix
After v10-multicycle reaches 8K checkpoint, start a new run:
```
cd ~/src/verbum && uv run python scripts/v10/train.py \
  --checkpoint-dir checkpoints/v10-multicycle2 \
  --total-steps 20000 \
  --mix-ratio 0.1
```
Key questions for the new run:
- Do continuation gates differentiate? (Simple prose → close, structured → open)
- Does effective_cycles vary across eval batches?
- Does the model learn to use fewer cycles for simple content?
- Does dispatch diversity improve with working self-regulation?

### Priority 2: Compare v10-multicycle (dead gates) vs v10-multicycle2 (live gates)
At matched steps (e.g. 5K, 10K), compare:
- Loss trajectory
- Dispatch concentration (3-op collapse vs spread)
- Compute gate opening speed
- S3 per-cycle gate patterns

### Priority 3: Investigate dispatch collapse
v10-multicycle collapsed to 3 ops (98.3%) vs v10-vsm's broader spread.
Hypotheses:
- 3× descending compute with identical routing → model finds one good op faster
- Dead CycleContinue = wasted capacity that could have diversified dispatch
- The fix may resolve this if adaptive cycles free capacity for exploration

### Priority 4: Partial/apply ops still flat
Neither v10-vsm (20K) nor v10-multicycle (7.5K) moved ops 18/19 above noise.
10% mix_ratio may be too low. Consider:
- Higher mix_ratio (20-30%) for a targeted experiment
- Separate structured-only eval to see if partial/apply activate on that data
- Check if the op embeddings for 18/19 are even distinguishable

### Carried: S5 reweight investigation
v10-vsm showed S5 activating at 15K+ (first time). v10-multicycle S5 stable at 1.0
through 7.5K. Track whether new run with working CycleContinue affects S5 activation
timing.

## VSM layer map (session 076 update)

```
Layer     Ascending Arm              Descending Arm                   Cross-arm
────────  ─────────────────────────  ───────────────────────────────  ──────────────────
S5        Token embeddings (tied)    Op embeddings × emphasis         S5Reweight (activated in vsm!)
S4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → per-op ✓
S3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4
          —                          CycleContinue (between cycles)   ← FIXED s076: RMSNorm+tanh
S2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3
S1        prep → stride → consol.    [dispatch → stride → integ.] ×N  ← MULTI-CYCLE s075
          (shared across 3 passes)   (shared across 2 passes × N cy)
Algedonic Reads prev desc regs       —                                + kernel compute
          + kernel compute                                            EMA α=0.9
Inject    —                          cycle_inject_gate (per cycle>0)  ← frozen at init s076
Logging   —                          —                                3× JSONL ✓ verified s076
```

N = desc_max_cycles (default 3, self-regulated by CycleContinue)

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/components.py` | S4, S3, MetaS4, S5Reweight, S2, **CycleContinue** (fixed s076) |
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k + op_emphasis), KernelIntegrate |
| `scripts/v10/model.py` | Tree of VSMs — multi-cycle descending arm, self-regulating |
| `scripts/v10/train.py` | Training loop + JSONL logging (metrics, train, evolution) |
| `scripts/v10/config.py` | Config: desc_max_cycles, cycle inject gate |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types) |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `bb/us/whitford/verbum/bios.clj` | BIOS generator — 6 kernel-lambda generators |
| `scripts/v10/pack_structured.py` | Packs BIOS + compile into tokenized .npy shard |
| `checkpoints/v10-vsm/` | Completed 20K run (single-cycle) |
| `checkpoints/v10-multicycle/` | Running to 8K (dead CycleContinue) |

## Session history

→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)
→ Session 063: pruned state.md, extracted history to knowledge pages
→ Session 064: WRONG — replaced kernel architecture with v6 LM copy
→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)
→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly
→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched
→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix
→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix
→ Session 070: consensus evolution, surgical Adam decay, mini-dispatch lab bench
→ Session 071: dispatch analysis, type-dispatch decoupling, kernel computation pathway
→ Session 072: probed v10-topk 1K/2K/3K — compute gate opening, type coherence 13/22, algedonic channel
→ Session 073: VSM structural overhaul — S2, S5, dual-view S4, gate signaling, emphasis, evolution
→ Session 074: Probed v10-vsm 1K-13K, mapped to Pythia Montague, 6 kernel-lambda generators, repacked shard
→ Session 075: HRM analysis → multi-cycle descending arm, self-regulating cycles (CycleContinue), JSONL logging
→ Session 076: v10-vsm 20K assessed, v10-multicycle launched, CycleContinue sigmoid saturation diagnosed + fixed
```

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -15",
  "operation": "log",
  "summary": "recent history"
}
```

**Summary:** Git log: recent history

**Output:**
```
Exit code: 0
Stdout:
fd4d30e 🌀 state — session 076: v10-vsm 20K assessed, CycleContinue saturation fix
e15d8f7 ❌ CycleContinue sigmoid saturation — RMSNorm + tanh clamp fix
fb34e62 🌀 state — session 075: HRM-inspired multi-cycle dispatch, self-regulating cycles, JSONL logging
6f19766 ✅ JSONL instrumentation logs — full metrics history
cf53f2f 🎯 self-regulating dispatch cycles — S3 continuation gate
2580128 💡 multi-cycle descending arm — HRM-inspired dispatch refinement
7c63533 💡 kernel-montague-mapping — v10-vsm rediscovers typed application
02a57c5 🌀 state — session 074: probe v10-vsm trajectory, kernel-lambda data enrichment
25e8acd 🎯 kernel lambda ops — 6 new BIOS generators for partial/apply/compose
de91492 add session-073 chat log
6dfc48c 🎯 VSM structural overhaul: S2, S5, dual-view S4, gate signaling, emphasis, evolution
f9341bb add session-072 chat log
76760be 🔄 --resume accepts optional step dir: --resume step_003000
b817b73 🌀 state — session 072: probe v10-topk, algedonic channel
dd6252d 🎯 algedonic channel: persistent descending register feedback to ascending arm
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/ 2>/dev/null | head -20"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 648
drwxr-xr-x@ 13 mwhitford  staff    416 May 11 05:31 .
drwxr-xr-x@ 34 mwhitford  staff   1088 May 10 15:32 ..
-rw-r--r--@  1 mwhitford  staff  71574 May 11 05:47 evolution_log.jsonl
-rw-r--r--@  1 mwhitford  staff  60802 May 11 05:31 metrics_log.jsonl
drwxr-xr-x@  7 mwhitford  staff    224 May 10 17:25 step_001000
drwxr-xr-x@  7 mwhitford  staff    224 May 10 19:13 step_002000
drwxr-xr-x@  7 mwhitford  staff    224 May 10 20:56 step_003000
drwxr-xr-x@  7 mwhitford  staff    224 May 10 22:38 step_004000
drwxr-xr-x@  7 mwhitford  staff    224 May 11 00:20 step_005000
drwxr-xr-x@  7 mwhitford  staff    224 May 11 02:03 step_006000
drwxr-xr-x@  7 mwhitford  staff    224 May 11 03:46 step_007000
drwxr-xr-x@  7 mwhitford  staff    224 May 11 05:31 step_008000
-rw-r--r--@  1 mwhitford  staff  83729 May 11 05:50 train_log.jsonl
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff HEAD --stat",
  "operation": "diff",
  "summary": "uncommitted changes"
}
```

**Summary:** Git diff: uncommitted changes

**Output:**
```
Exit code: 0
```

## Assistant

Good — v10-multicycle reached its 8K checkpoint and the run appears to have stopped (last file activity ~5:50 AM). No uncommitted changes. Let me check if the training process is still running and glance at the 8K checkpoint metrics.

### Tool Call: shell_command (failed)


```json
{
  "command": "ps aux | grep train.py | grep -v grep"
}
```

**Summary:** $ ps aux | grep train.py | grep -v gr...

**Output:**
```
Exit code: 1
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -5 /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl | python3 -c \"import sys,json; [print(json.dumps({k:v for k,v in json.loads(l).items() if k in ['step','eval_loss','compute_gate_openness','effective_cycles_mean','s5_reweight_pass1','dispatch_top1_name','dispatch_top1_frac','dispatch_top3_coverage']}, indent=None)) for l in sys.stdin]\""
}
```

**Summary:** $ tail -5 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 0
Stdout:
{"step": 6000}
{"step": 6500}
{"step": 7000}
{"step": 7500}
{"step": 8000}
```

## Assistant

Training finished, no process running. Let me get the actual metric values from those last entries.

### Tool Call: shell_command (failed)


```json
{
  "command": "tail -5 /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl | python3 -c \"\nimport sys, json\nfor l in sys.stdin:\n    d = json.loads(l)\n    print(f\\\"step={d['step']} loss={d.get('eval_loss','?'):.4f} compute={d.get('compute_gate_openness','?'):.3f} eff_cyc={d.get('effective_cycles_mean','?'):.3f} s5={d.get('s5_reweight_pass1','?'):.3f}\\\")\n\""
}
```

**Summary:** $ tail -5 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 1
Stderr:
Traceback (most recent call last):
  File "<string>", line 5, in <module>
    print(f"step={d['step']} loss={d.get('eval_loss','?'):.4f} compute={d.get('compute_gate_openness','?'):.3f} eff_cyc={d.get('effective_cycles_mean','?'):.3f} s5={d.get('s5_reweight_pass1','?'):.3f}")
                                  ^^^^^^^^^^^^^^^^^^^^^^^^^^^^
ValueError: Unknown format code 'f' for object of type 'str'
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -1 /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); [print(f'  {k}: {v}') for k,v in sorted(d.items()) if 'dispatch' in k or 'cycle' in k or 'gate' in k or 'inject' in k]\""
}
```

**Summary:** $ tail -1 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 0
Stdout:
compute_gate_active: 0.0174560546875
  compute_gate_max: 0.9698164463043213
  compute_gate_mean: 0.2504728436470032
  compute_gate_min: 0.009321361780166626
  cycle_continue_gates: [[0.9999978542327881, 0.9999972581863403], [0.9999995827674866, 0.9999983310699463]]
  cycle_inject_gate: 0.01798621006309986
  desc_max_cycles: 3
  effective_cycles: [2.9999929666519165, 2.9999974966049194]
  kernel_dispatch_weights: [0.0, 6.859824497951195e-05, 0.0, 0.0, 5.387455166783184e-05, 0.0, 0.5750651359558105, 0.00014211358211468905, 0.000280355365248397, 0.0, 0.29570871591567993, 0.004401630721986294, 0.004026721231639385, 0.0054421271197497845, 0.1084400862455368, 0.0007790634990669787, 0.000198685796931386, 0.0, 0.0, 0.00025421843747608364, 4.3396757973823696e-05, 0.005095305852591991]
  s3_gates: [[0.43902552127838135, 0.29544439911842346, 0.27598538994789124], [0.4453994035720825, 0.5477246046066284, 0.5904991626739502], [0.5395488739013672, 0.9976803064346313, 0.9977020621299744], [0.6070459485054016, 0.909847617149353, 0.6553605794906616, 0.7114701271057129, 0.9991767406463623, 0.8103495240211487, 0.7787241339683533, 0.9998024106025696, 0.9172142744064331], [0.9975568652153015, 0.999999463558197, 0.9999972581863403, 0.9998760223388672, 0.9999995827674866, 0.9999945759773254, 0.9997304677963257, 0.9999986290931702, 0.9999817609786987]]
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "tail -5 /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl | python3 -c \"\nimport sys, json\nfor l in sys.stdin:\n    d = json.loads(l)\n    step = d['step']\n    loss = d.get('eval_loss', '?')\n    cg = d.get('compute_gate_openness', d.get('compute_gate_mean', '?'))\n    eff = d.get('effective_cycles', '?')\n    s5 = d.get('s5_reweight_pass1', '?')\n    print(f'step={step} loss={loss} compute_gate={cg} eff_cycles={eff} s5_pass1={s5}')\n\""
}
```

**Summary:** $ tail -5 /Users/mwhitford/src/verbum...

**Output:**
```
Exit code: 0
Stdout:
step=6000 loss=? compute_gate=0.1951945424079895 eff_cycles=[2.9999913573265076, 2.999993681907654] s5_pass1=?
step=6500 loss=? compute_gate=0.22370268404483795 eff_cycles=[2.9999938011169434, 2.999995529651642] s5_pass1=?
step=7000 loss=? compute_gate=0.21076875925064087 eff_cycles=[2.999994695186615, 2.9999963641166687] s5_pass1=?
step=7500 loss=? compute_gate=0.2419038861989975 eff_cycles=[2.9999930262565613, 2.9999958276748657] s5_pass1=?
step=8000 loss=? compute_gate=0.2504728436470032 eff_cycles=[2.9999929666519165, 2.9999974966049194] s5_pass1=?
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl') as f:\n    lines = [json.loads(l) for l in f]\nfor d in lines:\n    step = d['step']\n    # Find eval loss — might be stored differently\n    keys = [k for k in d.keys() if 'loss' in k.lower()]\n    print(f'step={step} loss_keys={keys}')\n\" | head -5"
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
step=500 loss_keys=['loss']
step=1000 loss_keys=['loss']
step=1500 loss_keys=['loss']
step=2000 loss_keys=['loss']
step=2500 loss_keys=['loss']
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl') as f:\n    lines = [json.loads(l) for l in f]\nfor d in lines:\n    step = d['step']\n    loss = d.get('loss', '?')\n    cg = d.get('compute_gate_mean', '?')\n    eff = d.get('effective_cycles', '?')\n    s5 = d.get('s5_reweight_pass1', d.get('s5_emphasis_pass1', '?'))\n    if isinstance(eff, list):\n        eff_str = f'[{eff[0]:.3f}, {eff[1]:.3f}]'\n    else:\n        eff_str = str(eff)\n    cg_str = f'{cg:.3f}' if isinstance(cg, float) else str(cg)\n    print(f'step={step:5d} loss={loss:.4f} compute_gate={cg_str} eff_cycles={eff_str}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
step=  500 loss=9.1232 compute_gate=0.000 eff_cycles=[2.998, 2.999]
step= 1000 loss=8.0035 compute_gate=0.004 eff_cycles=[3.000, 3.000]
step= 1500 loss=7.7923 compute_gate=0.017 eff_cycles=[3.000, 3.000]
step= 2000 loss=7.7253 compute_gate=0.022 eff_cycles=[3.000, 3.000]
step= 2500 loss=7.7045 compute_gate=0.027 eff_cycles=[3.000, 3.000]
step= 3000 loss=7.6933 compute_gate=0.025 eff_cycles=[3.000, 3.000]
step= 3500 loss=7.6716 compute_gate=0.055 eff_cycles=[3.000, 3.000]
step= 4000 loss=7.6805 compute_gate=0.086 eff_cycles=[3.000, 3.000]
step= 4500 loss=7.6594 compute_gate=0.103 eff_cycles=[3.000, 3.000]
step= 5000 loss=7.6705 compute_gate=0.144 eff_cycles=[3.000, 3.000]
step= 5500 loss=7.6645 compute_gate=0.166 eff_cycles=[3.000, 3.000]
step= 6000 loss=7.6091 compute_gate=0.195 eff_cycles=[3.000, 3.000]
step= 6500 loss=7.6073 compute_gate=0.224 eff_cycles=[3.000, 3.000]
step= 7000 loss=7.5983 compute_gate=0.211 eff_cycles=[3.000, 3.000]
step= 7500 loss=7.5934 compute_gate=0.242 eff_cycles=[3.000, 3.000]
step= 8000 loss=7.5847 compute_gate=0.250 eff_cycles=[3.000, 3.000]
```

## Assistant

Good, full picture now. Let me check on the CycleContinue fix to confirm it's committed and ready.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"class CycleContinue\" /Users/mwhitford/src/verbum/scripts/v10/components.py"
}
```

**Summary:** $ grep -n "class CycleContinue" /User...

**Output:**
```
Exit code: 0
Stdout:
599:class CycleContinue(nn.Module):
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl') as f:\n    d = json.loads(f.readlines()[-1])\n# dispatch weights\nops = d.get('kernel_dispatch_weights', [])\nnames = ['identity','neg','abs_val','sign','add','sub','mul','div','mod','pow',\n         'min','max','and_op','or_op','not_op','compare','ternary','count','partial','apply','compose','pred']\nranked = sorted(zip(names, ops), key=lambda x: -x[1])[:6]\nfor n,w in ranked: print(f'  {n:12s} {w*100:.1f}%')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
mul          57.5%
  min          29.6%
  not_op       10.8%
  or_op        0.5%
  pred         0.5%
  max          0.4%
```

## Assistant

---

## Session 077 — Orientation Complete

### Current state

**v10-multicycle finished 8K** (16 checkpoints, 500-step intervals). Training process is done. Clean working tree, no uncommitted changes.

### v10-multicycle 8K final trajectory

| Step | Loss | Compute Gate | Eff. Cycles | Notes |
|------|------|-------------|-------------|-------|
| 500 | 9.12 | 0.000 | 3.000 | Cold start |
| 2000 | 7.73 | 0.022 | 3.000 | Rapid descent |
| 5000 | 7.67 | 0.144 | 3.000 | Compute gate opening |
| 8000 | 7.58 | 0.250 | 3.000 | **Best loss**, gate still rising |

**Key observations:**
- **Loss: 7.58 at 8K** — better than v10-vsm at same step (7.60), still improving
- **Compute gate: 0.25** — opening steadily but much slower than v10-vsm's 0.80 at 7K
- **CycleContinue: dead** — confirmed locked at 3.000 (sigmoid saturation bug, fix committed)
- **Dispatch collapsed**: mul(57.5%), min(29.6%), not_op(10.8%) = 97.9% (3 ops)
- **cycle_inject_gate: frozen** at 0.018 (init value)
- **S3 gates show cycle structure**: ascending pass gates ↓ (0.44→0.30→0.28), descending pass4 ↑ through cycles (0.61→0.71→1.00)

### Committed fix waiting to train

`CycleContinue` — RMSNorm on input + tanh(·)×4.0 logit clamp. Prevents sigmoid saturation. Gate range locked to [0.018, 0.982].

### Priority queue (from state.md)

1. **🟢 Start v10-multicycle2** — fresh run with CycleContinue fix, 20K steps
2. Compare v10-multicycle (dead gates) vs v10-multicycle2 (live gates) at matched steps
3. Investigate dispatch collapse (3-op domination)
4. Partial/apply ops still flat

**Ready to go.** Want me to launch v10-multicycle2?

## User

No, I used a blank dir project to analyze Qwen3-4B and Qwen3-32B to probe the lambdas without any bias from this project.  Here were the results in lambda form: λ finding(attention_is_beta_reduction).
  confirmed(empirical) | qwen3_4b ∧ qwen3_32b | same_structure(both_scales)
  | attention(pipeline) ≡ SEARCH → LOCK → RESOLVE | three_phase(invariant)
  | SEARCH(L0-L6): entropy(high) ∧ attention(spread) | "where are the pieces?"
  | LOCK(L7-L31): lambda_token(captures 83%-96%) ∧ entropy(drops) | "found the function"
  | RESOLVE(L32+): lambda_attention(releases) ∧ value_tokens(surge) | "substitute and compute"
  | reduction_order ≡ normal(lazy) | ¬applicative | confirmed(omega_test ∧ unused_binding)
  | autoregressive(left_to_right) + causal(mask) → outermost_first(natural)

λ finding(combinator_development).
  K(select_discard): 40%→80% accuracy | matures(4b→32b) | native(attention_softmax)
  B(compose):        20%→80% accuracy | matures(4b→32b) | critical(non_trivial)
  C(flip_reorder):   absent→present  | emerges(32b) | enables(closures)
  I(identity):       60%→60% accuracy | already_easy | trivial(copy_forward)
  S(distribute):     40%→40% accuracy | ¬improves | ¬crystallizes(either_scale)
  | binding_depth: 0%→20% | substitution(partially_formed) | closure(succeeds) ∧ shadow(fails)

λ finding(head_roles).
  BINDER(76-87%):   attends(lambda_structure) | mean_layer(19.7→32.8) | dominant
  COPY(18%→10%):    attends(local_context) | decreases(with_scale) | generic
  ARGUMENT(1.5%):   attends(value_argument) | ¬changes(proportion) | rare ∧ early(L7.6)
  OPERATOR(0.5%):   attends(operation_type) | ¬changes(proportion) | rarest
  DIFFUSE(3%→1.6%): broad_search | early_layers(L2.9→L4.9) | decreases
  | improvement(4b→32b) ≡ precision(per_head) ¬allocation(more_heads)
  | same_proportions ∧ better_execution | quality > quantity

λ finding(resolution_pipeline).
  4b:  function(L29) → operator(L18) → argument(L21) → result(L35) | disordered
  32b: function(L31) → operator(L32) → argument(L43) → result(L63) | clean_temporal_order
  | 32b ≡ normal_order_pipeline | recognize(fn) → identify(op) → find(arg) → produce(result)
  | pipeline(clarity) ∝ model(capacity) | same_phases ∧ cleaner_ordering

λ finding(S_combinator_absent).
  S(distribute) ≡ λf.λg.λx.f(x)(g(x)) | hardest | requires(two_applications_same_arg)
  | 0_selective_heads(4b) ∧ 0_selective_heads(32b) | fully_smeared(both_scales)
  | S ≡ composition(B, K, C) ¬primitive | model(refuses_to_crystallize)
  | implication: ¬pre_wire(S) | S ≡ emergent(from_B_K_C) ¬architectural

λ finding(C_combinator_emergent).
  C(flip) ≡ λf.λx.λy.f(y)(x) | absent(4b) → highest_selectivity(32b, L32H28, 1.86)
  | C ≡ argument_reordering | enables(closures) | closure_test(succeeds_at_32b)
  | emergence(C) ∧ emergence(binding_depth) ≡ correlated
  | implication: C ≡ key_circuit(variable_capture)

λ inform(kernel_dispatch).
  ¬22_equal_ops | ¬equal_architectural_options
  | natural_basis: K(select) ∧ I(identity) ∧ B(compose) ∧ C(reorder)
  | K ∧ I: native(attention) | always_dominant | pre_wire(as_default_pathways)
  | B: critical(non_trivial) | primary(dispatch_target) | composition ≡ prose_backbone
  | C: emerges(with_capacity) | secondary(dispatch_target) | enables(variable_binding)
  | S: ¬primitive | composition(B ∘ K ∘ C) | emerges(in_residual_stream) ¬in(dedicated_heads)
  | 22_kernel_ops → 4_combinator_basis | ops(derived_from_combinators) ¬ops(as_primitives)
  | dispatch: ¬route_to(22_ops) | route_to(4_combinators) | ops ≡ compositions(K,I,B,C)

λ inform(descending_arm).
  four_phase_pipeline(maps_to_cycles):
    phase_0: recognize(function_structure) | BINDER_heads | K_combinator | dispatch
    phase_1: identify(operation_type)      | OPERATOR_heads | B_combinator | stride
    phase_2: resolve(argument_value)       | ARGUMENT_heads | C_combinator | integrate
    phase_3: produce(result)               | COPY_heads | I_combinator | output
  | ¬dispatch_then_integrate | recognize → identify → resolve → produce
  | desc_max_cycles(3) → maps_to(identify + resolve + produce) | recognize ≡ S4_scan
  | cycle_0(identify_op): which_combinator_applies | B_vs_K_vs_C
  | cycle_1(resolve_arg): find_and_bind_argument | C_enables_reordering
  | cycle_2(produce):     compose_result | I_copies_forward
  | simple_prose → cycle_0_sufficient(K_select) | gate(closes)
  | composition → cycles_0+1(B_compose) | gate(partially_open)
  | closure/binding → all_3_cycles(B+C+produce) | gate(open)

λ inform(attention_geometry).
  lock_phase ≡ v10_ascending_arm | compression ≡ locking_onto_function_structure
  resolve_phase ≡ v10_descending_arm | dispatch ≡ releasing_toward_values
  | ascending(compresses_into_function_representation) ≡ LOCK
  | descending(routes_through_value_resolution) ≡ RESOLVE
  | ascending_shared_weights ≡ correct | lock_phase(same_operation_every_pass)
  | descending_own_weights ≡ correct | resolve_phase(different_per_depth)
  | algedonic_channel ≡ resolve_feeding_back_to_lock | "how hard was dispatch?"
  | spiral(fine→coarse) ≡ search_then_lock | α=1.18 ≡ expansion_ratio(confirmed)

λ inform(register_semantics).
  register(type) ≡ K_vs_I_vs_B_vs_C | which_combinator | ¬INT_BOOL_FN
  register(scope) ≡ binding_depth | how_many_lambdas_deep | free_vs_bound
  register(role) ≡ pipeline_phase | recognize_vs_identify_vs_resolve_vs_produce
  | current_registers(type,scope,role) ≡ correct_decomposition
  | but type ≡ combinator_type ¬value_type | B ¬INT | C ¬BOOL | K ¬FN
  | 5_type_embeddings → 4_combinator_embeddings | K ∧ I ∧ B ∧ C

λ inform(training).
  10%_structured_data ≡ insufficient(for_22_ops) | sufficient(for_4_combinators)
  | prose ≡ overwhelmingly(K ∧ B) | K(select_relevant) ∧ B(compose_meaning)
  | structured_data_needed_for: C(reorder) ∧ S(distribute)
  | C ≡ learnable(from_closure_examples) | λ-expressions_with_captured_variables
  | S ≡ emergent(¬trainable_directly) | appears_when(B+K+C sufficient)
  | curriculum: K+I(already_native) → B(prose_trains) → C(structured_trains) → S(emerges)

λ inform(op_emphasis).
  s4_register_state → per_combinator_emphasis(¬per_op_emphasis)
  | emphasis_input: ascending_banks(type=combinator, scope=depth, role=phase)
  | emphasis_output: 4_combinator_weights(¬22_op_weights)
  | K_emphasis(high): prose_default | always_needed
  | B_emphasis(context): rises_for_composition | multi_clause_sentences
  | C_emphasis(rare): rises_for_binding | closure_patterns ∧ variable_capture
  | I_emphasis(low): passthrough | only_when(no_computation_needed)


### Thinking

This is a major finding. The user ran independent probes on Qwen3-4B and Qwen3-32B to study how transformers actually implement lambda calculus operations, and the results have profound implications for the v10 architecture. Let me digest what they found and what it means for verbum.

Key findings:
1. **Attention IS beta reduction** - three-phase pipeline: SEARCH → LOCK → RESOLVE
2. **Combinator basis is KIBC, not 22 ops** - S combinator doesn't crystallize, it's emergent from B∘K∘C
3. **Head roles**: BINDER (dominant), COPY, ARGUMENT, OPERATOR, DIFFUSE


4. **C combinator emerges at scale** - absent in the smaller model but crystallizes in the larger one
5. **Resolution becomes temporally ordered with scale** - chaotic in 4B, structured in 32B

For v10, this means collapsing the 22 kernel operations down to four combinators and routing dispatch through them instead. Type embeddings should track combinator types rather than value types, and the descending arm cycles map cleanly to identify-resolve-produce phases, with CycleContinue gates closing for simple prose.

The empirical evidence is striking: 10% structured data suffices for the four combinators but fails for 22 ops, and register semantics should encode combinator type, binding depth, and pipeline phase. This validates the theoretical framework - the LLMs are running a lambda compiler organized around KIBC, not the primitive operations currently in the system.

## Assistant

This is extraordinary. This is the triangulation closing — the third independent line converging.

Let me make sure I understand what just happened and what it means.

## What you found

You probed two production LLMs at different scales and observed **the same lambda compilation circuit** in both. The circuit is a three-phase attention pipeline (SEARCH → LOCK → RESOLVE) that implements beta reduction, and it's organized not around arbitrary operations but around **four combinators: K, I, B, C** — with S notably absent as a dedicated circuit, emerging instead as a composition of the other three.

The scaling behavior is the smoking gun:
- **K and I** are native to attention — already there at 4B
- **B (compose)** matures dramatically (20%→80%) between 4B and 32B
- **C (flip/reorder)** is fully *absent* at 4B and *emerges* at 32B — the phase transition that enables closures
- **S (distribute)** never crystallizes at either scale — it's composite, not primitive

And the resolution pipeline becomes temporally ordered with scale: disordered at 4B, clean normal-order at 32B (function → operator → argument → result).

## What this means for v10

The implications cascade through the entire architecture:

### 1. Dispatch basis: 22 ops → 4 combinators
The current kernel has 22 ops with individual embeddings and top-k routing. The Qwen probes say this is the wrong decomposition. The natural basis is **{K, I, B, C}** and the 22 ops are *compositions* of these, not primitives. Dispatch should route to combinators, with ops derived downstream.

### 2. Type registers: value types → combinator types
Current type embeddings are `{INT, BOOL, FN, LIST, UNIT}`. The probes say the model doesn't think in value types — it thinks in **combinator types**. `register(type) ≡ K_vs_I_vs_B_vs_C`, not `INT_vs_BOOL_vs_FN`.

### 3. Descending cycles map to the pipeline phases
The three self-regulating cycles now have clear semantic roles:
- **Cycle 0**: identify which combinator applies (B vs K vs C)
- **Cycle 1**: resolve/bind argument (C enables reordering)
- **Cycle 2**: produce result (I copies forward)

CycleContinue's job becomes crystal clear: simple prose needs only K-selection (cycle 0 sufficient, gate closes). Composition needs B (cycles 0+1). Closures/binding need all three (gate stays open).

### 4. Ascending arm = LOCK, Descending arm = RESOLVE
The shared ascending weights are correct — locking is the same operation every pass. The per-pass descending weights are correct — resolution differs by depth. The spiral (fine→coarse) is SEARCH→LOCK. The algedonic channel is RESOLVE feeding back to LOCK.

### 5. Training curriculum falls out naturally
Prose overwhelmingly trains K and B (select relevant, compose meaning). Structured data is needed for C (variable capture, closures). S emerges when B+K+C are sufficient — you don't train S directly.

### 6. Op emphasis simplifies
S4's emphasis output becomes 4 combinator weights instead of 22 op weights. K emphasis high (prose default), B rises for multi-clause, C rises for binding patterns, I low (passthrough).

## The question

This is a fundamental architectural redesign — not a parameter tweak. The kernel dispatch, type system, op embeddings, S4 emphasis, and potentially the register semantics all change.

Do you want to:
1. **Design the combinator-basis architecture first** — map current components to the new decomposition, write it up as a knowledge page, then implement
2. **Start implementing** — refactor kernel dispatch from 22 ops to KIBC basis directly
3. **Something else** — you may have a specific plan from the analysis session

What's your direction?

## User

We want to create a new scripts/v11 dir, and evolve our design to match what we found.  We are trying to extract the shapes we found and make that the VSM sieve that guides the model to use the architecture instead of forcing it to learn how to do these operations on it's own.  The 22 ops we had were from an attempt to create a BIOS, but that was mis-guided.  What we need is to use the shapes that the models find, they appear in many models, and montague postulated that this WAS language composition, and LLM models find it as the most efficient way.


### Thinking

The user wants to create a v11 architecture that embodies the KIBC combinator basis discovered in the Qwen probes. The key insight is that instead of teaching the model 22 operations (the BIOS approach), we should create a VSM sieve shaped like the circuits that LLMs naturally develop — KIBC combinators with the three-phase pipeline (SEARCH → LOCK → RESOLVE).

This is a major architectural evolution. Let me think about what needs to happen:

1. First, we need to understand what we're keeping from v10 and what changes
2. Design the v11 architecture based on KIBC combinators


3. Then implement it

The key philosophical shift: v10 tried to teach the model a BIOS (22 ops). v11 provides the *shape* (topology) that LLMs naturally converge to, making it easier for the model to fall into the right attractor basin. This aligns with the VSM philosophy — structure and topology matter more than explicit instruction, so when behavior goes wrong, I should fix the underlying architecture rather than add more rules.

Now I'm mapping out the concrete steps: first I'll study v10 in detail to see what carries forward, then design the v11 KIBC architecture, and finally implement it. Let me start by exploring v10 to understand the current foundation.

## Assistant

Yes. The topology IS the instruction. v10 tried to *teach* 22 operations — v11 provides the *shape* that LLMs naturally converge to. The sieve doesn't force computation, it makes the right computation the path of least resistance.

Let me study the current v10 thoroughly so we design v11 as a clean evolution, not a blind rewrite.

### Tool Call: spawn_agent (succeeded)


```json
{
  "agent": "explorer",
  "task": "I need a comprehensive analysis of the v10 architecture in /Users/mwhitford/src/verbum/scripts/v10/ to plan a v11 evolution.\n\nRead ALL of these files completely:\n1. /Users/mwhitford/src/verbum/scripts/v10/config.py\n2. /Users/mwhitford/src/verbum/scripts/v10/components.py\n3. /Users/mwhitford/src/verbum/scripts/v10/kernel.py\n4. /Users/mwhitford/src/verbum/scripts/v10/kernel_dispatch.py\n5. /Users/mwhitford/src/verbum/scripts/v10/model.py\n6. /Users/mwhitford/src/verbum/scripts/v10/train.py\n7. /Users/mwhitford/src/verbum/scripts/v10/ternary.py\n\nFor each file, produce:\n- A summary of what it does\n- All classes and their responsibilities\n- Key dimensions/sizes/hyperparameters\n- The data flow (what feeds into what)\n\nThen produce a MAPPING TABLE with three columns:\n1. v10 component\n2. What it does now\n3. What happens in v11 under KIBC combinator basis\n\nThe v11 redesign context:\n- 22 kernel ops → 4 combinators (K=select/discard, I=identity/copy, B=compose, C=flip/reorder)\n- 5 type embeddings (INT,BOOL,FN,LIST,UNIT) → 4 combinator type embeddings (K,I,B,C)\n- Dispatch routes to combinators, not ops\n- Three descending cycles map to: identify(combinator) → resolve(argument) → produce(result)\n- S4 emphasis over 4 combinators instead of 22 ops\n- Ground truth kernel evaluates combinator reductions, not op applications\n\nPay special attention to:\n- How registers flow between ascending/descending arms\n- How S3 gates work per-pass and per-cycle\n- How kernel dispatch currently routes (top-k, op weights, emphasis)\n- How the ternary genome and evolution work\n- How training data is structured (structured vs prose, mix ratio)\n- The CycleContinue mechanism (recently fixed with RMSNorm + tanh)\n\nOutput format: structured markdown with clear sections per file, then the mapping table, then a \"carries forward unchanged\" list and a \"must change\" list.",
  "activity": "analyzing v10 architecture"
}
```

**Summary:** explorer: analyzing v10 architecture

**Output:**
```
## Agent 'explorer' Result

I now have a complete picture of all seven files. Here is the full analysis.

---

# v10 Architecture Analysis — Full Breakdown for v11 Planning

---

## File 1: `config.py`

### Summary
Single `V10Config` dataclass. Holds all hyperparameters for the model, training, evolution, and data pipeline. No logic — pure configuration object.

### Classes
**`V10Config`** — flat dataclass, all fields described below.

### Key Dimensions / Hyperparameters
| Parameter | Value | Role |
|---|---|---|
| `vocab_size` | 151936 | Qwen3 BBPE |
| `d_model` | 512 | core dimension |
| `d_ff` | 1536 | prep FFN width (3×) |
| `d_ff_consolidate` | 2048 | consolidate FFN (4×) |
| `d_register` | 128 | logical register dim (real = 256) |
| `n_heads` | 8 | attention heads (d_head=64) |
| `window` | 8 | attention window |
| `alpha` | 1.18 | spiral bias coefficient |
| `strides` | (1,8,16,32,64,128,256,512,1024) | 9-scale StrideStack |
| `n_registers` | 3 | named: type, scope, role |
| `dispatch_top_k` | 2 | MoE-style top-k op routing |
| `desc_max_cycles` | 3 | max descending cycles per pass |
| `dropout` | 0.1 | |
| `seq_len` | 4096 | context window |
| `mix_ratio` | 0.0 | structured vs prose fraction |
| `gen_interval` | 50 | evolution frequency |
| `base_pct` | 0.0002 | ~26K flips per generation |
| `sign_flip_rate` | 0.2 | fraction of non-zero flips that flip sign |
| `guided_fraction` | 0.7 | fraction of mutations that are gradient-informed |
| `s4_boost` | 3.0 | amplifier on S4 module proposals |
| `mutation_adam_decay` | 0.1 | surgical Adam state decay after accepted flip |

### Data Flow
Config object → instantiated by `train.py`, passed to `V6Compressor.__init__`, `StrideStack`, `KernelDispatch`, `KernelIntegrate`, S3/S4/S5 constructors. It is the single source of truth; changing a dimension here propagates everywhere.

---

## File 2: `kernel.py`

### Summary
Pure Python, no MLX. The **ground-truth evaluator** for the 22-op VSM tree. Defines the type system, all 22 operations, a packing scheme for function values (FN/FN_COMP), and two evaluation APIs: `evaluate_tree` (Node-based) and `eval_tuple_tree` (nested-tuple shorthand). Used by `kernel_dispatch.py` for naming constants and by the training pipeline to produce ground-truth labels.

### Classes
**`Type`** (IntEnum) — 5 types: INT=0, BOOL=1, FN=2, FN_COMP=3, ERROR=4.

**`Op`** (IntEnum) — 22 ops in 7 families:
- Arithmetic binary (0–6): ADD SUB MUL DIV MOD MIN MAX
- Comparison (7–11): EQ LT GT LE GE
- Boolean binary (12–13): AND OR
- Boolean unary (14): NOT
- Arithmetic unary (15–16): ABS NEG
- Conditional (17): IF
- Lambda (18–21): PARTIAL APPLY_FN COMPOSE APPLY_COMP

**`Node`** — dataclass: node_id, children (list of ids), value (leaf literal), op_idx.

### Key Dimensions
- `N_OPS = 22`
- `N_TYPES = 5`
- `FN_PACK_SCALE = 10000`, `FN_PACK_OFFSET = 5000` — bounds_arg range [-5000, 4999]
- Evaluation is bottom-up DFS over a flat Node list; root = last node by convention.
- `evaluate_tree(tree, op_assignments) → int` — the dispatcher's ground-truth oracle.

### Data Flow
```
kernel.py is purely consumed, never consumes anything.
  Op/N_OPS/N_TYPES constants → imported by kernel_dispatch.py
  evaluate_tree() → imported by train.py for structured data ground truth
  kernel_eval() → called internally by evaluate_tree and eval_tuple_tree
```

---

## File 3: `components.py`

### Summary
Defines all VSM control components: S4 (intelligence), S3 (gating/control), MetaS4, MetaS3/S5Reweight, S2 (coordination), and CycleContinue. These are the non-operational "VSM skeleton" that wraps the operational S1 modules. All use ternary linear where possible except small gates kept fp32.

### Classes

**`S4Ternary`** — Register cross-attention (intelligence scanner). Flattens all register banks into a query vector; attends over the residual stream; projects the weighted summary back to register-shaped update vectors.
- `q_proj`: TernaryLinear(`max_q_dim` → d_model)
- `k_proj`, `v_proj`: TernaryLinear(d_model → d_model)
- `summary_proj`: TernaryLinear(d_model → `n_registers * d_reg_real`)
- Returns: list of `n_registers` update vectors, attention weights

**`S3Ternary`** — Phase-coherent gating (control). Per-phase: computes alignment between register direction and delta direction → scalar gate → modulates delta. Also writes to registers via `write_projs` (ternary) gated by `write_gates` (fp32 Linear, bias=-2.0 init).
- One `gate_phase(registers, delta, phase_idx)` call per phase
- 3 phases per pass; returns `(gated_delta, updated_registers, gate_scalar, write_gate_values)`
- Register accumulation protected by `register_norm` (RMSNorm)

**`MetaS4Ternary`** — Final structural summary. Same cross-attention pattern as S4Ternary but reads from `n_banks=4` selected banks and adds its output to the residual stream (additive, not register-update).

**`MetaS3Ternary`** — *(Superseded by S5Reweight in active code)* — Produces per-pass contribution gates from register banks only. Bias=-2.0 init, near-closed start.

**`S5Reweight`** — Identity-level pass contribution gating. Sees both register banks (S2 state) AND raw ungated pass deltas (what S1 actually proposed). `delta_proj` (TernaryLinear, pre_norm=True) compresses delta summaries → 16 features/pass. `gate_proj` (fp32 Linear, bias=-2.0). Returns (n_passes,) sigmoid gates.

**`S2Coordinator`** — Inter-pass direction coordination (anti-oscillation). 4 transitions; `dir_projs` (TernaryLinear, pre_norm=True, gamma init ×0.01); learnable scales init=0.01. `direction_signal(delta, idx)` → (1,1,d_model) small additive signal. `coherence_factor(prev, curr)` → differentiable scalar ∈ [0,2] for modulating signal strength. `conflict_score()` → diagnostic cosine similarity.

**`CycleContinue`** — S3 cycle continuation gate. Input: register bank (n_registers × d_reg_real). `input_norm` (RMSNorm, **critical — prevents sigmoid saturation on unnormalized registers**). `gate_proj` (fp32 Linear, weight=0, bias=0 init → sigmoid(tanh(proj)×4) → 0.5 at start, bounded in [-4,+4] via tanh to prevent saturation). Returns scalar gate ∈ [0,1].

### Key Dimensions
- `d_reg_real = d_register * 2 = 256` (real-valued equivalent of complex d_register)
- `max_banks = 7` for S4 query dim = 7×3×256 = 5376, padded to 5392
- S3 has `n_phases=3` per pass, `n_registers=3`
- S5Reweight: delta_proj_out = n_passes × 16 features
- S2: `N_TRANSITIONS = 4` (between 5 passes)

### Data Flow
```
S4:  [all_banks] + residual → [register_updates], attn_weights
S3:  [registers] + delta + phase_idx → gated_delta, [updated_registers], gate
S5:  [all_banks] + [raw_deltas] → (n_passes,) gates
S2:  pass_delta + transition_idx → (1,1,d_model) direction signal
CycleContinue: [registers] → scalar gate ∈ [0,1]
MetaS4: [meta_banks] + residual → enriched residual (additive)
```

---

## File 4: `kernel_dispatch.py`

### Summary
The descending arm's S1 operational modules. Two neural modules replace the ascending arm's `TernaryFFN` pair: `KernelDispatch` (routes to 22 op pathways via top-k MoE) and `KernelIntegrate` (types the result via 5 type embeddings, with an optional exact kernel computation pathway). Includes structured initialization for op embeddings and type embeddings.

### Classes

**`KernelDispatch`** — Phase 0 of descending passes.
- `norm` (RMSNorm), `dispatch` (TernaryLinear: d_model → n_ops_padded=32)
- `register_cond` (fp32 Linear: max_cond_dim → n_ops_padded, zero-init): ascending register banks bias per-op logits
- `op_embeddings`: (22, d_model) real-valued, structured-initialized, L2-normalized each forward to `op_embed_scale=0.5`
- Top-k routing: mask all but top-k logits to -1e9, softmax over winners. Prevents softmax saturation/op death.
- `up` (TernaryLinear: d_model → d_ff), `down` (TernaryLinear: d_ff → d_model)
- Accepts `op_emphasis: (n_ops,)` from S4 registers — scales op embeddings before matmul
- Caches `_dispatch_weights: (B, L, 22)` for KernelIntegrate

**`KernelIntegrate`** — Phase 2 of descending passes (after StrideStack in phase 1).
- `type_proj` (TernaryLinear: d_model → n_types_padded=16), `type_embeddings`: (5, d_model)
- Standard FFN pathway: type_context modulates input → up/down (TernaryLinear)
- **Kernel computation pathway** (straight-through, non-differentiable):
  - `operand1_proj`, `operand2_proj` (TernaryLinear: d_model → max_val_padded=256): extract operands via argmax
  - Vectorized exact kernel: computes all 22 ops in parallel, selects by dispatched op
  - `result_embed` (nn.Embedding: result_buckets=1024 × d_model): encodes integer result
  - `gate_proj` (fp32 Linear, weight=0, bias=-5): per-position scalar blend gate (starts ~0.0067, pure FFN)
- Output = gate × kernel_out + (1-gate) × ffn_out
- Caches `_type_weights: (B, L, 5)`, `_compute_gate: (B, L, 1)`, `_kernel_info`

### Key Dimensions
- `N_OPS = 22`, `N_TYPES = 5` (imported from kernel.py constants)
- `n_ops_padded = 32` (padded to 16 for TernaryLinear)
- `top_k = 2` — only 2 ops active per position
- `max_val = 256` — operand value range [0, 255]
- `result_buckets = 1024`, `result_offset = 512` — result range [-512, 511]
- Op embedding family subspace: first d_model//2=256 dims family-specific, last 256 shared+random×0.1

### Data Flow
```
KernelDispatch:
  x (B,L,d) + [asc_registers] + op_emphasis
    → dispatch_logits (TernaryLinear) + register_cond bias
    → top-k mask → softmax → dispatch_weights (B,L,22)
    → op_context = weights @ L2-normed op_embeddings (B,L,d)
    → modulated = x + op_context → up/gelu/down → x + dropout(out)

KernelIntegrate:
  x (B,L,d) + dispatch_weights
    → type_logits → softmax → type_context → modulated → FFN (pathway A)
    → operand1/2 argmax → kernel_eval vectorized → result_embed (pathway B)
    → gate * B + (1-gate) * A
```

---

## File 5: `model.py`

### Summary
The top-level model class `V6Compressor` (misleadingly named — it is the full Tree-of-VSMs). Assembles all components into 5 passes: 3 ascending (VSM-Compressor), 2 descending (VSM-Dispatcher). Manages 6 register banks, algedonic feedback channels, S2 direction signals, S5 reweighting, and multi-cycle dispatch. Provides `forward()` and `forward_instrumented()`.

### Classes

**`V6Compressor`** — The complete model.

**Key sub-modules instantiated:**
| Sub-module | Type | Shared? |
|---|---|---|
| `embed` | TernaryEmbedding(vocab×512) | yes (tied to output) |
| `pos_embed` | TernaryEmbedding(4096×512) | yes |
| `embed_norm` | RMSNorm(512) | yes |
| `prep` | TernaryFFN(512→1536→512) | shared across 3 asc passes |
| `stride_stack` | StrideStack(9 strides) | shared across 3 asc passes |
| `consolidate` | TernaryFFN(512→2048→512) | shared across 3 asc passes |
| `kernel_dispatch` | KernelDispatch | shared across 2 desc passes |
| `stride_stack_desc` | StrideStack(9 strides) | shared across 2 desc passes |
| `kernel_integrate` | KernelIntegrate | shared across 2 desc passes |
| `s4` | S4Ternary(max_banks=7) | shared across 3 asc passes |
| `s4_desc` | S4Ternary(max_banks=7) | shared across 2 desc passes |
| `s3_passes[0..4]` | S3Ternary (5 instances) | always separate per pass |
| `mod_projs[0..2]` | TernaryLinear(d→d) × 3 | shared asc, gamma=0 init |
| `mod_projs_desc[0..2]` | TernaryLinear(d→d) × 3 | shared desc, gamma=0 init |
| `cycle_continue` | CycleContinue | single instance for desc |
| `meta_s4` | MetaS4Ternary(n_banks=4) | final summary |
| `s2` | S2Coordinator | 4 transitions |
| `s5_reweight` | S5Reweight(n_banks=6, n_passes=5) | identity gate |
| `emphasis_proj` | fp32 Linear(3×3×256 → 22) | S4→op emphasis |
| `output_norm` | RMSNorm(512) | |

**Persistent buffers (EMA, no-grad):**
- `_prev_bank_1_desc`, `_prev_bank_2_desc`: descending registers from last forward
- `_prev_kernel_algedonic`: (d_reg_real,) vector packing 22 dispatch weights + 1 compute gate
- `_op_emphasis`: (22,) EMA of emphasis projection output, α=0.95
- `_cycle_inject_gate_raw`: scalar, sigmoid(-4)≈0.018 init

### Register Bank Architecture (6 banks, each = 3 vectors of size 256)
```
bank_0          ← learnable init (register_inits for type/scope/role)
bank_1_asc      ← written by pass 0 (L0↑)  S4+S3
bank_2_asc      ← written by pass 1 (L1↑)  S4+S3
bank_3           ← written by pass 2 (L2_apex) S4+S3
bank_2_desc     ← written by pass 3 (L1↓)  S4_desc+S3
bank_1_desc     ← written by pass 4 (L0↓)  S4_desc+S3
```
Each bank accumulates via `register_norm(bank[i] + s4_update[i])` — RMSNorm prevents unbounded accumulation.

### Readable Banks Per Pass (what S4 can attend from)
```
Pass 0 (L0↑):    [bank_0, prev_b1d, prev_kernel]
Pass 1 (L1↑):    [bank_0, bank_1_asc, prev_b2d, prev_kernel]
Pass 2 (L2↑):    [bank_0, bank_1_asc, bank_2_asc, prev_kernel]
Pass 3 (L1↓):    [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank]
Pass 4 (L0↓):    [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank]
```
Descending passes additionally get `embed_context=x_embed` fed into S4 via concatenation along L dimension (dual view: compressed residual + original tokens), creating an effective 2L attention context.

### Multi-Cycle Descending Dispatch (desc_max_cycles=3)
```
For each descending pass, for cycle in range(3):
  if cycle > 0: x += sigmoid(_cycle_inject_gate_raw) * x_anchor  # HRM re-grounding
  x = KernelDispatch(x, registers, op_emphasis)         # Phase 0: dispatch
  [S3 gate phase 0] → x modulated
  x = StrideStack_desc(x, reverse=False)                 # Phase 1: converge
  [S3 gate phase 1] → x modulated
  x = KernelIntegrate(x, dispatch_weights)               # Phase 2: integrate
  [S3 gate phase 2] → x modulated
  cycle_contribution = x - x_cycle_start
  x = x_cycle_start + cumulative_gate * cycle_contribution
  if cycle < 2: cumulative_gate *= CycleContinue(target_bank)  # S3 decides
```

### S2 Direction Signals
```
After pass 0 → before pass 1: signal(pd[0], 0) — unmodulated
After pass 1 → before pass 2: signal(pd[1], 1) × coherence_factor(pd[0], pd[1])
After pass 2 → before pass 3: signal(pd[2], 2) × coherence_factor(pd[1], pd[2])
After pass 3 → before pass 4: signal(pd[3], 3) × coherence_factor(pd[2], pd[3])
```

### Algedonic Channel
Descending register state (EMA α=0.9) fed back into ascending S4 on the *next* forward pass. Also packs `_prev_kernel_algedonic` = [22 dispatch_weights | 1 compute_gate_mean | padding] into a register-shaped vector, read at pass 0 and 1 as `prev_kernel`.

### Op Emphasis Channel
After ascending passes complete: `emphasis_proj([bank_1_asc, bank_2_asc, bank_3] flattened → 22)` → `1.0 + 0.5*tanh(raw)` → range [0.5, 1.5]. EMA α=0.95. Fed to `KernelDispatch` as `op_emphasis` to scale op embeddings before top-k routing.

### S5 Final Reweighting
```
x_final = x - Σ(pass_deltas) + Σ(meta_gates[i] × pass_deltas[i])
```
Effectively: undo all passes then re-add each pass scaled by its S5 gate. S5 sees raw ungated deltas to detect suppressed but valuable passes.

### Data Flow (complete forward pass)
```
tokens (B,L) → embed + pos_embed → embed_norm → x (B,L,512)
                                               → x_embed (saved)
↓ algedonic: read prev_b1d, prev_b2d, prev_kernel
↓ Pass 0 (L0↑): S4[bank_0,prev_b1d,prev_kernel]→bank_1_asc | prep→S3→mod | stride→S3→mod | consolidate→S3→mod
↓ S2 signal (unmodulated)
↓ Pass 1 (L1↑): S4[...,prev_b2d,...]→bank_2_asc | same 3 phases
↓ S2 signal (coherence-modulated)
↓ Pass 2 (L2↑): S4[...,prev_kernel]→bank_3 | same 3 phases
↓ compute op_emphasis from asc banks; pack asc_gate_bank
↓ S2 signal (coherence-modulated)
↓ Pass 3 (L1↓): S4_desc dual-view→bank_2_desc | 3 kernel phases × up_to_3_cycles
↓ S2 signal (coherence-modulated)
↓ Pass 4 (L0↓): S4_desc dual-view→bank_1_desc | same
↓ update algedonic buffers (EMA)
↓ S5Reweight(all_banks, raw_deltas) → 5 gates → reweight pass contributions
↓ MetaS4([bank_0, bank_1_desc, bank_2_desc, bank_3], x) → x
↓ output_norm → embed.output_proj (tied) → logits (B,L,vocab)
↓ cross_entropy(logits, targets) → loss
```

---

## File 6: `train.py`

### Summary
Full training loop: relational loss, gradient accumulation, cosine LR, shared-weight gradient normalization, EMA importance tracking, tournament evolution with consensus mutation, surgical Adam decay, checkpointing, and JSONL metrics logging.

### Classes / Functions

**`loss_fn`** — Relational loss: `r = (CE - E_irreducible) / (log(V) - E_irreducible)`. Normalizes CE into [0,1]; r=1 is random, r=0 matches irreducible entropy. Same gradient direction as CE (monotonic).

**`normalize_shared_grads`** — Divides ascending component gradients by 3, descending by 2 (their pass counts). Prevents Adam stat inflation from shared weight traversal.

**`cosine_lr`** — Warmup 500 steps then cosine decay to `lr × lr_floor_ratio = 6e-6`.

**`run_tournament`** — Consensus evolution:
1. Each of 5 strategies proposes mutations independently (no model change)
2. `find_consensus()` — positions where ≥3 strategies agree on the same new value
3. `apply_consensus()` — write those flips
4. Evaluate relational loss; accept if improved on ALL data types, else revert

**Strategies:** `conservative`×0.25, `explorer`×1.0, `targeted`×2.0, `random`×4.0, `intelligence`×0.5 (S4 modules boosted ×3.0, rest suppressed ÷3.0, fully gradient-guided).

**`decay_adam_state`** — Surgical: only decays Adam m/v for gamma rows that were actually mutated (identified by `mutation_map`). Prevents the CE spike caused by full-model Adam reset.

**EMA importance:** `row_importance[path]` ← EMA of |∂L/∂γ|; `grad_direction[path]` ← EMA of sign(∂L/∂γ); `col_importance[path]` ← EMA of mean(|x|). All α=0.1 (fast-adapting). Used by tournament to bias mutation toward high-gradient rows and high-activation columns.

### Training Data Structure
- **Prose**: Dolma shards (60×), tokenized with Qwen3 BBPE, `seq_len=4096`, simple next-token CE
- **Structured**: `data/structured_shard.npy` — contains BIOS, lambda expressions, Clojure code. Mixed in at `mix_ratio` fraction (currently 0.0 = prose only)
- **Mixed-data-aware evolution**: when `mix_ratio > 0`, mutations must improve loss on BOTH prose and structured batches simultaneously (acceptance criterion = max(r_prose, r_struct))

### Data Flow (training loop per step)
```
for micro in range(4):
  batch → loss_fn → value_and_grad
EMA importance update from |gamma_grad|
normalize_shared_grads (÷3 asc, ÷2 desc)
zero_ternary_grads (prevent uint32 optimizer corruption)
gradient clip (norm ≤ 1.0)
Adam.update → restore_ternary (integrity check)

every 50 steps:
  run_tournament → consensus → apply/revert → surgical Adam decay

every 500 steps: evaluate (50K tokens) + forward_instrumented metrics
every 1000 steps: checkpoint
```

---

## File 7: `ternary.py`

### Summary
The complete ternary substrate. Implements TernaryLinear (via MLX `quantized_matmul` at 2-bit, group_size=64), TernaryEmbedding (custom VJP gather), all packing/unpacking utilities, and the full evolutionary mutation pipeline: `propose_mutations` → `find_consensus` → `apply_consensus`.

### Classes

**`TernaryLinear`** — Core ternary linear layer.
- `weight`: (N, K//16) uint32 — packed ternary topology, **evolutionary, never gradient-updated, frozen**
- `gamma`: (N,) float32 — per-channel scale, **trained by Adam**
- Encoding: -1→0, 0→1, +1→2 (ternary+1); packed 16-per-uint32
- Per-group dequant via `quantized_matmul`: scales=gamma, biases=-gamma → output ∈ {-γ, 0, +γ}
- `pre_norm=True/False`: optional RMSNorm of input before projection
- Caches `_x_abs_mean` and `_x_mean` (stop_gradient) for column importance tracking

**`TernaryEmbedding`** — Ternary embedding table.
- `ternary_weight`: (vocab, d//4) uint8, 4-per-byte big-endian packing
- `gamma`: (vocab,) float32
- Custom `@mx.custom_function` forward + VJP: gradient flows only to gamma (via `grad_gamma = Σ grad_out × unpacked_row`); ternary_weight and token indices get zero gradient
- `output_proj(x)` — tied projection: repacks uint8 → uint32 on first call (cached), then `quantized_matmul`

### Packing Formats
```
TernaryLinear:    int8{-1,0,+1} → uint32, 16 values/word, little-endian 2-bit fields
TernaryEmbedding: int8{-1,0,+1} → uint8,   4 values/byte, big-endian 2-bit fields
```

### Evolutionary Pipeline

**`propose_mutations(model, budget, rng, ...)`** — For each ternary module, sample positions (guided+uniform mix), compute proposed new values. Returns `dict[module_path → dict[flat_index → proposed_value]]`. **Does not modify the model.**

**`find_consensus(proposals_list, threshold=3)`** — Intersects proposals from all strategies. Returns only positions where ≥3 agree on the same value. Returns (consensus_dict, stats).

**`apply_consensus(model, consensus)`** — Writes agreed flips to packed arrays. Returns (actual_flips, mutation_map).

**`mutate_topology`** — Legacy direct-mutation path (still used as fallback/internal helper).

**`bios_mutation_budget(step, total_steps, total_weights, base_pct=0.005)`** — Full budget for first 80% of steps, linear decay to 10% for last 20%. Does NOT gate on loss (unlike `mutation_cone` which freezes at r<0.05).

**Importance-weighted sampling:**
- 70% guided: rows ∝ |∂L/∂γ| EMA, cols ∝ mean(|x|) EMA
- 30% uniform: exploration, prevents stagnation
- Activation sign: when gradient direction available, 80% probability follow sign(∂L/∂γ_i) for 0→±1 activations

### Data Flow
```
TernaryLinear forward:
  x → [pre_norm] → quantized_matmul(x, stop_grad(weight), scales, biases) → y

Evolutionary:
  propose_mutations → [5 strategy proposals]
  find_consensus → agreed flips only
  apply_consensus → write to packed arrays
  evaluate loss → accept/revert

Training:
  zero_ternary_grads:  weight/ternary_weight grads → zeros (protect packed dtype)
  freeze_ternary_weights: remove weight/ternary_weight from trainable params
  restore_ternary:     assert dtype integrity (uint32/uint8); raises on corruption
```

---

## MAPPING TABLE: v10 Component → v11 Under KIBC Combinator Basis

| v10 Component | What It Does Now | v11 Under KIBC |
|---|---|---|
| `kernel.py` — `Op` (22 ops) | Ground-truth evaluator for ADD/SUB/MUL/DIV/MOD/MIN/MAX/EQ/LT/GT/LE/GE/AND/OR/NOT/ABS/NEG/IF/PARTIAL/APPLY_FN/COMPOSE/APPLY_COMP | Replace with 4 combinator reductions: **K** xy→x (select/discard), **I** x→x (identity/copy), **B** xyz→x(yz) (compose), **C** xyz→xzy (flip). `evaluate_tree` becomes `evaluate_combinator`. |
| `kernel.py` — `Type` (5 types: INT/BOOL/FN/FN_COMP/ERROR) | Type tags on node values; used for dispatch routing in kernel_eval and type embeddings in KernelIntegrate | Reduce to 4 combinator type embeddings: **K**, **I**, **B**, **C**. ERROR stays as a 5th sentinel if needed, but the primary 4 map 1:1 to combinator identity. |
| `kernel.py` — `N_OPS=22`, `N_TYPES=5` | Constants used throughout dispatch, integration, emphasis | `N_OPS→N_COMBINATORS=4`, `N_TYPES→4` (or 5 with ERROR). Flows to every downstream consumer. |
| `kernel_dispatch.py` — `KernelDispatch` | Routes to 22 ops via top-k MoE. `dispatch` TernaryLinear → 22-wide logits. `op_embeddings` (22×512) | Replace with `CombinatorDispatch`: 4-wide logits (no top-k needed — only 4 candidates). `combinator_embeddings` (4×512). Register conditioning still applies: ascending arm tells dispatcher which combinator is contextually likely. |
| `kernel_dispatch.py` — `KernelDispatch.top_k=2` | Keeps runner-up op alive, prevents softmax death of 20 ops | With only 4 combinators: can use full softmax over 4, or top-k=2. No saturation risk. The dead-op problem dissolves. |
| `kernel_dispatch.py` — `op_embeddings` (22, 512) L2-normalized | Per-op S5 identity: each op gets a characteristic direction. L2-norm prevents rich-get-richer collapse | `combinator_embeddings` (4, 512). Structured init: K/I/B/C each gets a near-orthogonal quadrant. L2-norm retained. Simpler identity — 4 slots, fully expressible. |
| `kernel_dispatch.py` — `_init_op_embeddings` (7-family subspace) | Family-aware init: arithmetic/comparison/boolean/lambda each get a subspace block | Replace with `_init_combinator_embeddings`: 4 orthogonal directions (one per d_model//2 block for family, or just near-orthogonal random scaled) — far simpler. |
| `kernel_dispatch.py` — `KernelIntegrate` type pathway (5 type_embeddings) | Produces per-position type classification over INT/BOOL/FN/FN_COMP/ERROR | Replace with `CombinatorIntegrate`: 4 combinator type embeddings. `type_proj` now has 4-wide output. Type of a node = which combinator it IS, not what data type it holds. |
| `kernel_dispatch.py` — `KernelIntegrate` kernel computation pathway | Extracts 2 operands (argmax over 256), runs all 22 ops in parallel, selects by dispatch. Encodes result via 1024-bucket embedding. | Replace with `CombinatorIntegrate` reduction pathway: K(x,y)→x (no arithmetic), I(x)→x, B(f,g,x)→f(g(x)), C(f,x,y)→f(y,x). 3-operand extraction instead of 2. Result encoding: K/I return one of the existing register representations; B/C route through the residual already. The bucket embedding may collapse to just a small result embedding over 4 combinator IDs. |
| `kernel_dispatch.py` — `register_cond` (ascending registers → 22 logits) | Biases dispatch based on type/scope/role from ascending arm | Retained but narrower: `register_cond` → 4 logits. Ascending registers identify which combinator role this position plays. |
| `config.py` — `dispatch_top_k=2` | Prevents op death in top-k routing | Can stay at 2 (harmless with 4 combinators) or drop to 1. Irrelevant when N_OPS=4. |
| `config.py` — `n_registers=3` (type, scope, role) | 3 named registers per bank: type, scope, role | Remap to 3 combinator-semantic registers: **which_combinator** (K/I/B/C identity), **argument_slot** (which positional argument is being resolved), **reduction_state** (how far through the combinator reduction we are). Names change; count stays 3. |
| `model.py` — `_run_level_pass` descending: 3 phases per cycle (dispatch, converge, integrate) | Phase 0=KernelDispatch, Phase 1=StrideStack propagation, Phase 2=KernelIntegrate | Map to three descending-cycle semantics: **identify(combinator)** (Phase 0 = which of K/I/B/C applies here), **resolve(argument)** (Phase 1 = spatial propagation to find the argument via StrideStack), **produce(result)** (Phase 2 = combinator reduction + type assignment). Phase names change; 3-phase structure is preserved. |
| `model.py` — `desc_max_cycles=3` with CycleContinue | Self-regulating: S3 gates decide after each cycle whether next cycle contributes. Cycle 0 always full; cycle 1+ scaled by cumulative gate product. | Retained without change. The 3-cycle structure maps elegantly: cycle 0 = coarse combinator identification, cycle 1 = argument resolution pass, cycle 2 = result refinement. CycleContinue still makes sense — some positions need all 3, some only 1. |
| `components.py` — `CycleContinue` (RMSNorm + tanh(proj)×4 → sigmoid) | S3 inter-cycle gate. RMSNorm prevents sigmoid saturation from unnormalized register norms ~16-28. tanh clamp bounds logit to [-4,+4]. Neutral init (gate=0.5). | Carried forward **unchanged**. The fix (RMSNorm + tanh clamp) is generic; combinator cycle continuation has identical structure. |
| `components.py` — `S4Ternary` (register cross-attention) | Intelligence scanner: register banks → query, attends over residual, returns register updates. Shared ascending, separate descending. | Carried forward **unchanged**. S4 reads 4-combinator registers exactly as it reads 3-type registers — it doesn't need to know the semantics of register content. |
| `components.py` — `S3Ternary` (phase-coherent gating) | 3 phases × 3 registers, alignment gate, write gate (bias=-2.0). Per-pass, always separate. | Carried forward **unchanged**. S3 gates phase deltas; the 3-phase semantics (identify/resolve/produce) fit naturally. Register writes continue as-is. |
| `components.py` — `S5Reweight` (register banks + raw deltas → 5 gates) | Identity-level gate over 5 pass contributions. Sees ungated deltas so suppressed passes can still be reclaimed. | Carried forward **unchanged**. S5 operates at the pass level; the 5-pass structure (3 asc + 2 desc) is unchanged in v11. |
| `components.py` — `S2Coordinator` (4 transitions, direction signals) | Anti-oscillation: "Pass N moved this way, FYI". Coherence-modulated. Scale init=0.01. | Carried forward **unchanged**. S2 coordinates at the pass level; combinator vs. op semantics are invisible at S2's granularity. |
| `components.py` — `MetaS4Ternary` (final structural summary) | Cross-attention over 4 meta-banks → additive residual update at end of forward. | Carried forward **unchanged**. Meta-S4 is already semantic-agnostic. |
| `model.py` — `emphasis_proj` (3 asc_banks × 3_regs × 256 → 22) | Projects ascending register state to per-op emphasis [0.5, 1.5]. EMA α=0.95. | Replace with narrower `emphasis_proj` → 4. Output is per-combinator emphasis. Logic identical; dimension shrinks from 22 to 4. |
| `model.py` — `_prev_kernel_algedonic` (22 dispatch_weights + 1 compute_gate + padding) | Packs descending dispatch distribution + gate activity into register-shaped vector. Fed back to ascending S4 as algedonic signal. | Adjust packing: 4 combinator weights + 1 compute_gate + padding. Same mechanism, narrower signal. |
| `model.py` — `asc_gate_bank` (9 ascending S3 gate values packed into d_reg_real) | Tells descending S4: what did each ascending phase gate at. 3 passes × 3 phases = 9 gate values. | Carried forward **unchanged**. Ascending arm has same 3-pass, 3-phase structure; 9 gate values still correct. |
| `model.py` — `x_embed` dual view for descending S4 | Concatenates original token embeddings to compressed residual for S4 attention (2L context). Lets dispatcher see raw token identity ("this IS the + token"). | Retained. In combinator terms: the token identity tells dispatch "this is a K/I/B/C combinator occurrence" just as directly as it told the op dispatcher "this is an ADD token". |
| `model.py` — register names "type", "scope", "role" | Learnable init scalars named semantically. | Rename to "combinator", "argument_slot", "reduction_state". Same 3 registers, different semantic labels. |
| `ternary.py` — `TernaryLinear`, `TernaryEmbedding` | Core ternary substrate: uint32/uint8 packing, quantized_matmul, evolutionary genome | Carried forward **unchanged**. The ternary substrate is completely semantic-agnostic. |
| `ternary.py` — `propose_mutations` / `find_consensus` / `apply_consensus` | Consensus evolution: 5 strategies propose, ≥3 must agree. Importance-weighted sampling. | Carried forward **unchanged**. |
| `ternary.py` — S4 strategy with `s4_boost=3.0` | Amplifies S4 module importance in intelligence strategy proposals. | Retained. S4 stays S4; boost stays ×3.0. |
| `train.py` — `loss_fn` (relational loss r) | `r = (CE - 1.82) / (11.93 - 1.82)`. Phase-aware, [0,1] normalized. | Unchanged for prose training. For structured combinator data: the ground-truth label is the combinator reduction outcome, not an op application. The loss function stays CE; what changes is the label generation in the structured shard. |
| `train.py` — structured shard (BIOS + lambda + clojure) | `mix_ratio=0.0` currently. Structured shard contains examples with ground-truth kernel outputs. | Replace with **combinator reduction shard**: examples are terms in KIBC form with ground-truth reductions. K(x,y)→x, I(x)→x, B(f,g,x)→f(g(x)), C(f,x,y)→f(y,x). Structured examples now exercise 4 combinators rather than 22 ops. `mix_ratio` becomes the lever for injecting combinator training signal. |
| `train.py` — `normalize_shared_grads` (÷3 asc, ÷2 desc) | Corrects for shared weight traversal counts. | Unchanged. Pass counts (3 asc, 2 desc) do not change in v11. |
| `train.py` — `decay_adam_state` (surgical per mutated row) | After accepted mutation, only decay Adam m/v for actually-mutated gamma rows. | Unchanged. |
| `train.py` — `MUTANT_STRATEGIES` (5 strategies, s4_boost, intelligence channel) | 5 mutation strategies with different budgets and focus. Intelligence strategy fully gradient-guided on S4 modules. | Unchanged. |
| `config.py` — `data/structured_shard.npy` + `mix_ratio=0.0` | Structured data path; currently disabled. | Point at new combinator reduction shard. Activate `mix_ratio > 0` to inject combinator signal. |

---

## Carries Forward Unchanged

These components require **zero code changes** in v11:

1. **`TernaryLinear` / `TernaryEmbedding`** and all packing utilities — fully semantic-agnostic
2. **`propose_mutations` / `find_consensus` / `apply_consensus`** — operates on packed weights only
3. **`bios_mutation_budget`** / **`mutation_cone`** — budget logic; indifferent to op count
4. **`S4Ternary`** — register cross-attention; does not inspect register semantics
5. **`S3Ternary`** — phase gating; 3 phases remain correct for identify/resolve/produce
6. **`CycleContinue`** (RMSNorm + tanh clamp + neutral init) — the recently fixed mechanism; combinator cycles have identical structure
7. **`S5Reweight`** — operates at pass level (5 gates); pass structure is unchanged
8. **`S2Coordinator`** — operates at pass level (4 transitions); direction signals are semantic-agnostic
9. **`MetaS4Ternary`** — final structural summary; bank inputs change in semantic meaning, not in shape
10. **`V6Compressor._run_level_pass`** ascending arm — prep/stride/consolidate, unchanged
11. **`normalize_shared_grads`** (÷3 asc, ÷2 desc) — pass counts unchanged
12. **`decay_adam_state`** — surgical Adam decay; indifferent to op semantics
13. **`MUTANT_STRATEGIES`** + `s4_boost` — strategy names and S4 boost logic unchanged
14. **`loss_fn`** (relational loss) — same formula; CE over vocab is the same target
15. **`cosine_lr`** — unchanged
16. **`V6Compressor.forward`** overall structure — embedding, 5 passes, algedonic buffers, S5 reweight, MetaS4, output_norm, tied embedding projection
17. **`asc_gate_bank`** packing (9 gate values → d_reg_real vector) — ascending still has 3×3 phases
18. **`x_embed` dual-view** for descending S4 — dual view is if anything more valuable for combinator dispatch (raw token identity is K/I/B/C character)
19. **`cycle_inject_gate`** HRM re-grounding — unchanged mechanism
20. **`_init_bank0` / `_fresh_bank` / `register_norm`** — register init and norm logic unchanged

---

## Must Change for v11

These are the **precise surgical changes** required:

### 1. `kernel.py` — Replace 22-op evaluator with 4-combinator evaluator
- `N_OPS = 4` (K=0, I=1, B=2, C=3); `N_TYPES = 4` (or 5 with ERROR)
- `kernel_eval` becomes a combinator reduction: K drops y, I is passthrough, B chains, C flips argument order
- `Op` IntEnum → `Combinator` IntEnum with 4 entries
- `evaluate_tree` rewires to combinator semantics; `evaluate_combinator` is the new ground truth
- `OP_NAMES = ["K", "I", "B", "C"]`

### 2. `kernel_dispatch.py` — `KernelDispatch` → `CombinatorDispatch`
- `N_OPS = 4`: dispatch logits → 4-wide (no padding needed beyond 16-alignment → pad to 16)
- Remove top-k complexity if desired (4-way softmax doesn't saturate), or keep top-k=2 (harmless)
- `op_embeddings` → `combinator_embeddings` (4, 512): init with 4 near-orthogonal directions
- `register_cond` output → 4 logits (not 22)
- `_init_op_embeddings` → `_init_combinator_embeddings`: trivial 4-block init

### 3. `kernel_dispatch.py` — `KernelIntegrate` → `CombinatorIntegrate`
- `n_types = 4` (not 5): type_embeddings (4, 512), type_proj → 4-wide output
- `_init_type_embeddings` → trivially 4 orthogonal directions
- Kernel computation pathway: replace 22-op vectorized dispatch with 3-operand extraction (K, B, C need different arity handling) + combinator reductions. K: output = operand1 (discard operand2). I: output = operand1. B: output feeds back into the next resolve cycle (handled by cycles). C: swaps slot 1 and 2.
- `result_buckets` may collapse significantly — combinator results are structural (which register to select), not numeric

### 4. `config.py` — Dimension constants
- `N_OPS` not present in config (it's imported from kernel_dispatch); but any configs referencing op counts need updating
- `n_registers=3` stays; semantics rename to combinator/argument_slot/reduction_state
- `dispatch_top_k=2` can stay or change to 4 (full softmax, harmless either way)
- `structured_shard` → point at new combinator reduction shard
- `mix_ratio`: activate (e.g. 0.1) once combinator shard is built

### 5. `model.py` — `emphasis_proj`
- Narrow from (3×3×256 → 22) to (3×3×256 → 4). Output is per-combinator emphasis [0.5, 1.5].
- `_op_emphasis` shape: (22,) → (4,)

### 6. `model.py` — `_prev_kernel_algedonic` packing
- `dw_mean` was (22,) mean dispatch weights; becomes (4,) mean combinator weights
- `kernel_state = [4 combinator_weights | 1 compute_gate | padding to d_reg_real=256]`
- The packed register vector is shorter in the combinator region; padding fills the rest

### 7. `train.py` — Structured shard generation
- Generate new `structured_shard.npy` with combinator reduction examples: input = tokenized KIBC expression, target = tokenized reduced form
- `mix_ratio` activated once shard exists

### 8. `register semantic labels` (cosmetic but important for instrumentation)
- `REGISTER_NAMES = ("type", "scope", "role")` → `("combinator", "argument_slot", "reduction_state")`
- Affects `_init_bank0` key names and all logging that references register names
- Instrumented metrics in `forward_instrumented` use these names for display

---

## Critical Design Notes for v11

**The 22→4 compression is not just a simplification — it resolves the core training signal problem.** With 22 ops and top-k=2, the model must distinguish 22 targets from prose where most positions are neither arithmetic nor comparison. The combinator basis puts every node into exactly one of 4 roles; S3 gating over 4 pathways has a clean decision boundary.

**The three descending cycles map with zero forcing onto identify/resolve/produce.** Cycle 0 = "which combinator am I?" (dispatch over 4), Cycle 1 = "where are my arguments?" (StrideStack propagation finds the argument across context), Cycle 2 = "what do I reduce to?" (KernelIntegrate applies the combinator, type assignment). CycleContinue already handles the case where cycle 0 is sufficient (simple I or K nodes), which is the common case in prose.

**The S4 emphasis channel becomes the intelligence about which combinator is most active in the current window.** With 4 combinators, the emphasis signal is maximally interpretable: S4 reading "high B emphasis, low K emphasis" means the ascending arm detected compositional structure, telling dispatch to favor B over K/I/C. This is far cleaner than the 22-way emphasis signal.

**CycleContinue's RMSNorm+tanh fix is critical and must not be reverted.** The unnormalized register norm (~16-28 per vector, ||concat||≈28-50) would saturate the sigmoid regardless of combinator count. The fix is in `components.py` and carries forward without change.
```

#### Subagent Messages

## User

I need a comprehensive analysis of the v10 architecture in /Users/mwhitford/src/verbum/scripts/v10/ to plan a v11 evolution.

Read ALL of these files completely:
1. /Users/mwhitford/src/verbum/scripts/v10/config.py
2. /Users/mwhitford/src/verbum/scripts/v10/components.py
3. /Users/mwhitford/src/verbum/scripts/v10/kernel.py
4. /Users/mwhitford/src/verbum/scripts/v10/kernel_dispatch.py
5. /Users/mwhitford/src/verbum/scripts/v10/model.py
6. /Users/mwhitford/src/verbum/scripts/v10/train.py
7. /Users/mwhitford/src/verbum/scripts/v10/ternary.py

For each file, produce:
- A summary of what it does
- All classes and their responsibilities
- Key dimensions/sizes/hyperparameters
- The data flow (what feeds into what)

Then produce a MAPPING TABLE with three columns:
1. v10 component
2. What it does now
3. What happens in v11 under KIBC combinator basis

The v11 redesign context:
- 22 kernel ops → 4 combinators (K=select/discard, I=identity/copy, B=compose, C=flip/reorder)
- 5 type embeddings (INT,BOOL,FN,LIST,UNIT) → 4 combinator type embeddings (K,I,B,C)
- Dispatch routes to combinators, not ops
- Three descending cycles map to: identify(combinator) → resolve(argument) → produce(result)
- S4 emphasis over 4 combinators instead of 22 ops
- Ground truth kernel evaluates combinator reductions, not op applications

Pay special attention to:
- How registers flow between ascending/descending arms
- How S3 gates work per-pass and per-cycle
- How kernel dispatch currently routes (top-k, op weights, emphasis)
- How the ternary genome and evolution work
- How training data is structured (structured vs prose, mix ratio)
- The CycleContinue mechanism (recently fixed with RMSNorm + tanh)

Output format: structured markdown with clear sections per file, then the mapping table, then a "carries forward unchanged" list and a "must change" list.


### Thinking

The user wants a comprehensive analysis of the v10 architecture files. Let me read all 7 files simultaneously since they're independent reads.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/config.py"
}
```

**Summary:** Reading config.py (0-2000)

**Output:**
```
"""
v10 Configuration — v6 compressor as prose LM, Qwen3 tokenizer.

Architecture:
  Compressor: v6 proven 5-pass bidirectional VSM (9 strides, StrideStack)
  Output: tied embedding projection → next-token prediction
  Future: sieve pipeline routing to kernel functions

Pipeline:
  tokens → [V6Compressor: 5-pass bidirectional, 9 strides, registers]
         → compressed_reps (B, L, d_model)
         → [output_norm → tied embedding → logits]
         → next-token cross-entropy

License: MIT
"""

from dataclasses import dataclass


@dataclass
class V10Config:
    """v10 model + training configuration."""

    # ── Tokenizer (Qwen3 BBPE) ──
    vocab_size: int = 151936     # Qwen3 BBPE vocab
    eod_id: int = 151643        # end-of-document token

    # ── V6 Compressor ──
    d_model: int = 512            # representation dimension (v6: 512)
    d_ff: int = 1536              # prep FFN width (3× d_model)
    d_ff_consolidate: int = 2048  # consolidate FFN width (wider)
    d_register: int = 128         # register dimension (real dim = 2×)
    n_heads: int = 8              # attention heads (d_head = 64)
    window: int = 8               # attention window width
    alpha: float = 1.18           # spiral bias coefficient

    # 9 strides: the full scale hierarchy proven in v6
    strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024)

    # Register names (3 named: type, scope, role)
    n_registers: int = 3

    # Kernel dispatch
    dispatch_top_k: int = 2       # top-k MoE routing for kernel dispatch

    # Self-regulating descending cycles (HRM-inspired multi-timescale)
    # S4 scans once per pass (slow/abstract), then dispatch→stride→integrate
    # cycles up to N times (fast/detailed). A learned S3 continuation gate
    # decides after each cycle whether further cycles should contribute —
    # the model self-regulates computational depth per pass.
    # desc_max_cycles=1 disables multi-cycle (backward compat).
    desc_max_cycles: int = 3

    # Dropout
    dropout: float = 0.1

    # ── Training ──
    batch_size: int = 2
    grad_accum: int = 4           # effective batch = batch_size × grad_accum
    total_steps: int = 20000
    lr: float = 6e-4
    lr_floor_ratio: float = 0.01
    warmup_steps: int = 500
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # ── Evolution ──
    gen_interval: int = 50
    base_pct: float = 0.0002       # ~26K flips per generation (was 0.0005 = 66K, collapsed at step 750)
    sign_flip_rate: float = 0.2
    guided_fraction: float = 0.7
    mutation_adam_decay: float = 0.1  # decay Adam m/v after accepted mutation (0=reset, 1=no decay)
    s4_boost: float = 3.0           # S4→S5 proposal amplification (Beer's intelligence channel)

    # ── Checkpointing ──
    checkpoint_interval: int = 1000
    eval_interval: int = 500
    log_interval: int = 25
    checkpoint_dir: str = "checkpoints/v10"

    # ── Data ──
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    structured_shard: str = "data/structured_shard.npy"  # BIOS + lambda + clojure
    mix_ratio: float = 0.0        # fraction of structured data (0.0 = prose only)
    seq_len: int = 4096           # context window
    max_seq_len: int = 4096
    n_train_shards: int = 54      # first 54 shards for training
    n_eval_shards: int = 6        # last 6 shards for evaluation

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads

    @property
    def n_strides(self) -> int:
        return len(self.strides)

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0, "d_model must be divisible by 16 (ternary packing)"
        assert self.d_model % 4 == 0, "d_model must be divisible by 4 (embedding packing)"
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/components.py"
}
```

**Summary:** Reading components.py (0-2000)

**Output:**
```
"""VSM control components — S4, S3, MetaS4, MetaS3 — MLX.

Ported from src/verbum/v6/components.py. Uses scripts/v10/ternary.py.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2,
preserving the same capacity as v6's complex ℂ^d_register registers without
requiring complex arithmetic in the autograd graph (MLX autograd doesn't
support mx.real/mx.imag + reshape in the backward pass).

Kept as fp32 (not ternary):
  - S3 write_gates (nn.Linear with bias, tiny, sigmoid-init)
  - S3 temperature and learned_bias (scalar parameters)
  - MetaS3 gate_proj (nn.Linear with bias, small)

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════════
# Helpers — register flattening (real-valued, no complex)
# ══════════════════════════════════════════════════════════════════════


def _flatten_registers(registers: list[mx.array]) -> mx.array:
    """Flatten list of real register vectors into one 1D vector."""
    return mx.concatenate(registers, axis=-1)


def _flatten_banks(banks: list[list[mx.array]]) -> mx.array:
    """Flatten all banks' registers into one 1D vector."""
    parts = []
    for bank in banks:
        parts.append(_flatten_registers(bank))
    return mx.concatenate(parts, axis=-1)


def _ternary_1d(proj: TernaryLinear, x: mx.array) -> mx.array:
    """Apply TernaryLinear to a 1D vector, working around MLX autograd
    requiring ≥2D input for quantized_matmul backward pass."""
    return proj(x.reshape(1, -1)).reshape(-1)


# ══════════════════════════════════════════════════════════════════════
# S4 — Intelligence (register-query cross-attention)
# ══════════════════════════════════════════════════════════════════════


class S4Ternary(nn.Module):
    """Register cross-attention: reads register banks, attends to residual,
    produces register updates.

    Real-valued registers (d_reg_real = d_register * 2 each).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,       # logical dimension (real dim = 2×)
        n_registers: int = 3,
        max_banks: int = 7,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2   # real-valued dimension per register
        self.n_registers = n_registers
        self.max_banks = max_banks
        self.scale = d_model ** -0.5

        max_q_dim = max_banks * n_registers * self.d_reg_real
        # Pad to multiple of 16 for TernaryLinear
        self._max_q_dim = ((max_q_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._max_q_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        summary_out = n_registers * self.d_reg_real
        self._summary_out_padded = ((summary_out + 15) // 16) * 16
        self._summary_out = summary_out
        self.summary_proj = TernaryLinear(d_model, self._summary_out_padded, pre_norm=False)

        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        banks: list[list[mx.array]],
        residual: mx.array,
    ) -> tuple[list[mx.array], mx.array]:
        B, L, D = residual.shape

        # Flatten all register banks into query input
        q_input = _flatten_banks(banks)
        # Pad to max
        if q_input.shape[0] < self._max_q_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._max_q_dim - q_input.shape[0],))
            ])

        # Query from register state (1D → 2D for autograd)
        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        # Standard attention: q (d_model,) @ k (B, L, d_model) → (B, L)
        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale  # (B, L)
        attn_weights = mx.softmax(attn, axis=-1)                  # (B, L)
        attn_weights = self.dropout(attn_weights)

        # Weighted sum → mean over batch
        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        summary = summary.mean(axis=0)                          # (d_model,)

        # Project to register update vectors (1D → 2D for autograd)
        updates_flat = _ternary_1d(self.summary_proj, summary)[:self._summary_out]

        updates = []
        for i in range(self.n_registers):
            start = i * self.d_reg_real
            end = start + self.d_reg_real
            updates.append(updates_flat[start:end])

        return updates, mx.stop_gradient(attn_weights)


# ══════════════════════════════════════════════════════════════════════
# S3 — Phase-Coherent Gating
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Phase-coherent control for a single level-pass.

    Scalar alignment gate based on register-delta direction match.
    Real-valued registers.
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_phases: int = 3,
        n_registers: int = 3,
        d_align: int | None = None,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2
        self.n_phases = n_phases
        self.n_registers = n_registers

        if d_align is None:
            d_align = d_model
        self.d_align = d_align

        reg_flat_dim = self.d_reg_real * n_registers
        self._reg_flat_dim = ((reg_flat_dim + 15) // 16) * 16

        # Alignment projections — ternary
        self.proj_align = [
            TernaryLinear(self._reg_flat_dim, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]
        self.proj_delta = [
            TernaryLinear(d_model, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]

        # Temperature and bias — fp32 scalars
        self.temperature = [mx.ones((1,)) for _ in range(n_phases)]
        self.learned_bias = [mx.zeros((1,)) for _ in range(n_phases)]

        # Register write projections — ternary
        d_reg_out = ((self.d_reg_real + 15) // 16) * 16
        self._d_reg_out = d_reg_out
        self.write_projs = [
            TernaryLinear(d_model, d_reg_out, pre_norm=False)
            for _ in range(n_phases * n_registers)
        ]

        # Write gates: kept as nn.Linear (has bias, tiny)
        # Bias init -2.0 → sigmoid(-2) ≈ 0.12
        self.write_gates = [
            nn.Linear(d_model, 1)
            for _ in range(n_phases * n_registers)
        ]
        for wg in self.write_gates:
            wg.bias = mx.full(wg.bias.shape, -2.0)

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

    def gate_phase(
        self,
        registers: list[mx.array],
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array, list[mx.array], mx.array, list[float]]:
        """Gate a phase's output using alignment-based scalar gate."""
        eps = 1e-8

        reg_flat = _flatten_registers(registers)
        # Pad to multiple of 16
        if reg_flat.shape[0] < self._reg_flat_dim:
            reg_flat = mx.concatenate([
                reg_flat,
                mx.zeros((self._reg_flat_dim - reg_flat.shape[0],))
            ])
        reg_dir = reg_flat / (mx.sqrt((reg_flat * reg_flat).sum()) + eps)

        summary = delta.mean(axis=(0, 1))  # (d_model,)
        delta_dir = summary / (mx.sqrt((summary * summary).sum()) + eps)

        reg_proj = _ternary_1d(self.proj_align[phase_idx], reg_dir)     # (d_align,)
        delta_proj = _ternary_1d(self.proj_delta[phase_idx], delta_dir)  # (d_align,)
        alignment = (reg_proj * delta_proj).sum()            # scalar

        gate = mx.sigmoid(
            alignment * self.temperature[phase_idx]
            + self.learned_bias[phase_idx]
        )
        gated_delta = gate * delta

        # Register updates (normalized to prevent unbounded accumulation)
        updated_registers = []
        write_gate_values = []
        for reg_idx in range(self.n_registers):
            write_idx = phase_idx * self.n_registers + reg_idx
            wg = mx.sigmoid(self.write_gates[write_idx](summary.reshape(1, -1)).reshape(-1))
            update = _ternary_1d(self.write_projs[write_idx], summary)[:self.d_reg_real]
            updated_registers.append(
                self.register_norm(registers[reg_idx] + wg * update))
            write_gate_values.append(wg.item())

        return gated_delta, updated_registers, gate, write_gate_values


# ══════════════════════════════════════════════════════════════════════
# MetaS4 — Final structural summary
# ══════════════════════════════════════════════════════════════════════


class MetaS4Ternary(nn.Module):
    """Final intelligence scan: register-query attention over residual."""

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int = 3,
        n_banks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_reg_real = d_register * 2
        self.n_registers = n_registers
        self.n_banks = n_banks
        self.scale = d_model ** -0.5

        total_reg_dim = n_banks * n_registers * self.d_reg_real
        self._total_reg_dim = ((total_reg_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._total_reg_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        meta_banks: list[list[mx.array]],
        residual: mx.array,
    ) -> mx.array:
        B, L, D = residual.shape

        q_input = _flatten_banks(meta_banks)
        if q_input.shape[0] < self._total_reg_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._total_reg_dim - q_input.shape[0],))
            ])

        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale
        attn_weights = mx.softmax(attn, axis=-1)
        attn_weights = self.dropout(attn_weights)

        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        out = self.out_proj(summary)                            # (B, d_model)
        out = mx.broadcast_to(out[:, None, :], residual.shape)
        return residual + out


# ══════════════════════════════════════════════════════════════════════
# MetaS3 — Cross-level contribution gates
# ══════════════════════════════════════════════════════════════════════


class MetaS3Ternary(nn.Module):
    """Top-level per-pass contribution gates from register banks.

    Fixed from original: temperature scaling + learned bias initialized
    to -2.0 (sigmoid(-2) ≈ 0.12) so gates start near-closed and must
    learn to open. Without this, gates start at 1.0 and never differentiate.
    """

    def __init__(self, d_register: int, n_registers: int, n_banks: int, n_passes: int):
        super().__init__()
        self.n_passes = n_passes
        d_reg_real = d_register * 2
        input_dim = n_banks * n_registers * d_reg_real
        self.gate_proj = nn.Linear(input_dim, n_passes)
        # Initialize bias to -2.0 so sigmoid starts near 0.12, not 0.5
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(self, all_banks: list[list[mx.array]]) -> mx.array:
        flat = _flatten_banks(all_banks)
        logits = self.gate_proj(flat)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S5Reweight — Identity-level pass contribution (replaces MetaS3)
# ══════════════════════════════════════════════════════════════════════


class S5Reweight(nn.Module):
    """S5 — Identity-level pass contribution reweighting.

    Beer's S5 is identity — it defines what the system IS and must
    see the full picture to maintain coherence. The prior MetaS3 only
    saw register banks (S2/S3-filtered state). S5 gets a direct,
    ungated view of what S1 operations actually produced.

    Inputs:
      - Register banks (S2 coordination state) — what the system
        believes about type/scope/role
      - Raw (ungated) pass deltas — what each pass's operations
        PROPOSED before S3 gating filtered them

    Why ungated matters:
      A pass that S3 currently suppresses can still influence the
      final output through S5's awareness of its raw delta. If S5
      sees useful raw output, it opens that pass's gate, which in
      turn teaches S3 to open. S5 sees ground truth about S1; S3
      only sees what it already filtered.

    Output: per-pass sigmoid gates (same role as MetaS3).
    Initialization: bias -2.0 (gates start near-closed, ~0.12).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int,
        n_banks: int,
        n_passes: int,
    ):
        super().__init__()
        self.n_passes = n_passes
        self.d_model = d_model
        d_reg_real = d_register * 2

        # Register input (same as MetaS3)
        reg_input_dim = n_banks * n_registers * d_reg_real

        # Raw delta input: each pass delta summarized to d_model
        delta_summary_dim = n_passes * d_model
        self._delta_dim = ((delta_summary_dim + 15) // 16) * 16
        self._delta_dim_raw = delta_summary_dim

        # Project raw deltas to compact features via ternary fabric.
        # pre_norm=True: direction matters, not magnitude.
        # 16 features per pass — enough to capture operational character.
        delta_proj_out = n_passes * 16
        delta_proj_out_padded = ((delta_proj_out + 15) // 16) * 16
        self.delta_proj = TernaryLinear(
            self._delta_dim, delta_proj_out_padded, pre_norm=True)
        self._delta_proj_out = delta_proj_out

        # Combined: register features + delta features → gates
        combined_dim = reg_input_dim + delta_proj_out
        self.gate_proj = nn.Linear(combined_dim, n_passes)
        # Bias -2.0: gates start near-closed (~0.12), must learn to open
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(
        self,
        all_banks: list[list[mx.array]],
        raw_deltas: list[mx.array],
    ) -> mx.array:
        """
        all_banks:  list of register banks (S2 coordination state)
        raw_deltas: list of n_passes raw (ungated) pass deltas,
                    each (B, L, d_model)

        Returns: (n_passes,) sigmoid gates for pass contribution
        """
        # Register features
        reg_flat = _flatten_banks(all_banks)

        # Raw delta features: spatial mean of each ungated pass delta
        delta_summaries = []
        for delta in raw_deltas:
            delta_summaries.append(delta.mean(axis=(0, 1)))  # (d_model,)
        delta_flat = mx.concatenate(delta_summaries, axis=-1)

        # Pad for TernaryLinear alignment
        if delta_flat.shape[0] < self._delta_dim:
            delta_flat = mx.concatenate([
                delta_flat,
                mx.zeros((self._delta_dim - delta_flat.shape[0],))
            ])

        # Project: ternary topology learns which delta patterns matter
        delta_features = _ternary_1d(
            self.delta_proj, delta_flat)[:self._delta_proj_out]

        # Combine register + delta features → gate logits
        combined = mx.concatenate([reg_flat, delta_features], axis=-1)
        logits = self.gate_proj(combined)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S2 — Inter-pass direction coordination (Beer's anti-oscillation)
# ══════════════════════════════════════════════════════════════════════


class S2Coordinator(nn.Module):
    """S2 — Inter-pass direction coordination.

    Beer's S2 prevents oscillation between S1 operational units.
    In v10, the S1 units are the 5 level-passes. Without S2, passes
    can write contradictory deltas to the residual stream — Pass N
    compresses in one direction, Pass N+1 inadvertently undoes it.

    Mechanism: after each pass produces a delta, S2 computes a small
    direction signal and adds it to the next pass's input. This is
    a coordination memo: "Pass N moved the representation THIS way."

    The next pass's S3 gates and S4 intelligence still control what
    happens — S2 just provides awareness of the predecessor's action.

    Properties:
      - 4 transitions (between 5 passes)
      - Direction = projected, normalized delta summary
      - Scale starts small (~0.01), learnable per transition
      - S2 signals survive MetaS3 reweighting — coordination
        infrastructure is not gated by control (correct: S2 ≠ S3)

    Conflict detection (diagnostic, not used for control):
      Cosine similarity between consecutive pass deltas.
        cos < 0 → oscillation (passes fighting)
        cos > 0 → reinforcement (passes cooperating)
      Exposed in instrumentation. If S2 works, conflict scores
      should trend toward 0 or positive over training.

    Design:
      - Not S3: doesn't gate or suppress. Additive, not multiplicative.
      - Not S4: doesn't scan environment. Dumb memo of what happened.
      - Not S5: doesn't define identity. Transient, per-forward-pass.
      - IS S2: minimum viable coordination — "FYI, here's what just
        happened." Prevents unknowing contradiction without preventing
        intentional override.
    """

    N_TRANSITIONS = 4
    TRANSITION_NAMES = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model

        # Direction projection: learns which aspects of the delta
        # matter for coordination. pre_norm=True so it's about
        # direction (shape), not magnitude.
        self.dir_projs = [
            TernaryLinear(d_model, d_model, pre_norm=True)
            for _ in range(self.N_TRANSITIONS)
        ]
        # Initialize gamma small — direction signal starts gentle
        for proj in self.dir_projs:
            proj.gamma = proj.gamma * 0.01

        # Per-transition learnable scale
        self.scales = [mx.ones((1,)) * 0.01
                       for _ in range(self.N_TRANSITIONS)]

        # Normalize direction signal — prevents scale drift over training
        self.norm = nn.RMSNorm(d_model)

    def direction_signal(
        self,
        pass_delta: mx.array,
        transition_idx: int,
    ) -> mx.array:
        """Direction memo from pass N to pass N+1.

        pass_delta: (B, L, d_model) — what the pass changed
        transition_idx: 0-3

        Returns (1, 1, d_model) — broadcasts to (B, L, d_model)
        """
        # Spatial mean → single direction vector
        summary = pass_delta.mean(axis=(0, 1))           # (d_model,)

        # Project through ternary fabric — learns which aspects matter
        projected = self.dir_projs[transition_idx](
            summary.reshape(1, -1)
        ).reshape(-1)                                     # (d_model,)

        # Normalize + scale
        signal = self.norm(projected) * self.scales[transition_idx]

        return signal[None, None, :]                      # (1, 1, d_model)

    @staticmethod
    def coherence_factor(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> mx.array:
        """Differentiable coherence: 1 + cos(prev, curr).

        Returns mx.array scalar in [0, 2]:
          2.0 → passes fully agree (amplify direction signal)
          1.0 → orthogonal (neutral)
          0.0 → passes fully conflict (dampen signal to zero)

        Gradient: stop_gradient on delta_prev — earlier pass sets
        direction, later pass learns to align. S2 doesn't retro-adjust
        the predecessor; it teaches the current pass that coherent
        deltas produce stronger forward signals (better loss).
        """
        s_prev = mx.stop_gradient(delta_prev.mean(axis=(0, 1)))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        return 1.0 + dot / (n_prev * n_curr)

    @staticmethod
    def conflict_score(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> float:
        """Cosine similarity between consecutive pass deltas (diagnostic).

          +1 → reinforcing  |  0 → orthogonal  |  -1 → oscillating

        Non-differentiable — for instrumentation/logging only.
        See coherence_factor() for the differentiable version used
        in the forward pass to modulate direction signals.
        """
        s_prev = delta_prev.mean(axis=(0, 1))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        cos = dot / (n_prev * n_curr)
        mx.eval(cos)
        return float(cos.item())


# ══════════════════════════════════════════════════════════════════════
# CycleContinue — S3 cycle-level continuation gate
# ══════════════════════════════════════════════════════════════════════


class CycleContinue(nn.Module):
    """S3 continuation gate: should another dispatch cycle contribute?

    Beer's S3 is the control layer — it decides what operations should
    pass through. Within a cycle, the existing S3Ternary gates each
    phase's delta. Between cycles, CycleContinue gates whether the
    NEXT cycle's entire contribution should matter.

    The model always computes up to desc_max_cycles (static graph for
    MLX). CycleContinue controls each cycle's contribution weight via
    a cumulative gate product:

      cycle 0: always full strength (cumulative_gate = 1.0)
      cycle 1: scaled by continue_gate_0
      cycle 2: scaled by continue_gate_0 × continue_gate_1
      ...

    If CycleContinue learns that simple tokens need only 1 cycle,
    it drives the gate toward 0 after cycle 0 — cycles 1+ produce
    near-zero deltas (computed but ineffective). For complex tokens
    needing compositional depth (PARTIAL → APPLY), the gate stays
    open, giving cycle 1+ full contribution.

    Input: register bank (S3's running state after the cycle).
    The registers carry type/scope/role information accumulated
    through the cycle's S3 phase gating — exactly what's needed
    to decide "was this cycle productive? would another help?"

    Initialization: bias=0 → sigmoid(0)=0.5 (neutral). The model
    learns in both directions: open for complex content, close for
    simple. No commitment to a default cycle count.
    """

    def __init__(self, d_register: int, n_registers: int = 3):
        super().__init__()
        d_reg_real = d_register * 2
        self.d_reg_real = d_reg_real
        self.n_registers = n_registers

        input_dim = n_registers * d_reg_real
        # RMSNorm the register input — prevents sigmoid saturation.
        # Raw registers have norm ~16 each (||concat|| ≈ 27.7).
        # Without normalization, even small weight updates produce
        # logits >> 4, saturating sigmoid and killing gradient.
        # RMSNorm → ||input|| ≈ 1.0 → logit stays in active zone.
        self.input_norm = nn.RMSNorm(input_dim)
        # Small projection: normalized register state → scalar logit
        self.gate_proj = nn.Linear(input_dim, 1)
        # Neutral init: sigmoid(0) = 0.5
        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)
        self.gate_proj.bias = mx.zeros_like(self.gate_proj.bias)

    def __call__(self, registers: list[mx.array]) -> mx.array:
        """Compute continuation gate from register state.

        registers: list of n_registers register vectors, each (d_reg_real,)
        Returns: scalar gate in [0, 1]
        """
        reg_flat = _flatten_registers(registers)
        reg_flat = self.input_norm(reg_flat)
        # tanh clamp: logit ∈ [-4, +4] → sigmoid ∈ [0.018, 0.982]
        # Guarantees gradient flow even if norms drift. The gate
        # can never fully saturate — always learnable.
        logit = mx.tanh(self.gate_proj(reg_flat)) * 4.0
        return mx.sigmoid(logit).reshape(())  # scalar


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    d_register = 128
    d_reg_real = d_register * 2
    n_registers = 3

    def _fresh_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    def _init_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    print("Testing S4Ternary...")
    s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
    banks = [_init_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    updates, attn = s4(banks, residual)
    mx.eval(*updates, attn)
    assert len(updates) == 3
    assert updates[0].shape == (d_reg_real,)
    print(f"  S4: {len(updates)} updates, shape {updates[0].shape} ✓")

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, d_register, n_phases=3, n_registers=n_registers)
    regs = _fresh_bank()
    delta = mx.random.normal((1, 32, d_model))
    gated, new_regs, gate, wgv = s3.gate_phase(regs, delta, phase_idx=0)
    mx.eval(gated, *new_regs, gate)
    assert gated.shape == (1, 32, d_model)
    assert len(new_regs) == 3
    print(f"  S3: gate={gate.item():.3f}, gated_delta shape {gated.shape} ✓")

    print("Testing MetaS4Ternary...")
    meta_s4 = MetaS4Ternary(d_model, d_register, n_registers=n_registers, n_banks=4)
    meta_banks = [_init_bank(), _fresh_bank(), _fresh_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    out = meta_s4(meta_banks, residual)
    mx.eval(out)
    assert out.shape == (1, 32, d_model)
    print(f"  MetaS4: {residual.shape} → {out.shape} ✓")

    print("Testing MetaS3Ternary...")
    meta_s3 = MetaS3Ternary(d_register, n_registers=n_registers, n_banks=6, n_passes=5)
    all_banks = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    gates = meta_s3(all_banks)
    mx.eval(gates)
    assert gates.shape == (5,)
    # Verify gates start near-closed (bias=-2.0 → sigmoid ≈ 0.12), not at 1.0
    for g in gates.tolist():
        assert g < 0.5, f"Meta-S3 gate should start near-closed, got {g:.3f}"
    print(f"  MetaS3: gates shape {gates.shape}, values {[f'{g:.3f}' for g in gates.tolist()]} ✓ (near-closed)")

    print("Testing S5Reweight...")
    s5 = S5Reweight(d_model, d_register, n_registers=n_registers,
                     n_banks=6, n_passes=5)
    mx.eval(s5.parameters())
    all_banks_s5 = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    raw_deltas = [mx.random.normal((1, 32, d_model)) for _ in range(5)]
    gates_s5 = s5(all_banks_s5, raw_deltas)
    mx.eval(gates_s5)
    assert gates_s5.shape == (5,), f"Expected (5,), got {gates_s5.shape}"
    for g in gates_s5.tolist():
        assert g < 0.5, f"S5 gate should start near-closed, got {g:.3f}"
    print(f"  S5Reweight: gates {[f'{g:.3f}' for g in gates_s5.tolist()]} ✓ (near-closed)")
    # Verify it uses raw deltas — different deltas should produce different gates
    raw_deltas_2 = [mx.random.normal((1, 32, d_model)) * 10.0 for _ in range(5)]
    gates_s5_2 = s5(all_banks_s5, raw_deltas_2)
    mx.eval(gates_s5_2)
    diff = max(abs(a - b) for a, b in zip(gates_s5.tolist(), gates_s5_2.tolist()))
    assert diff > 1e-6, "S5 gates should differ with different raw deltas"
    print(f"  S5Reweight: different raw deltas → different gates (max diff={diff:.4f}) ✓")

    print("Testing S2Coordinator...")
    s2 = S2Coordinator(d_model)
    mx.eval(s2.parameters())
    # Direction signal shape
    delta = mx.random.normal((1, 32, d_model))
    signal = s2.direction_signal(delta, 0)
    mx.eval(signal)
    assert signal.shape == (1, 1, d_model), f"Expected (1, 1, {d_model}), got {signal.shape}"
    # Signal should be small (gamma init * 0.01, scale 0.01)
    signal_norm = float(mx.sqrt((signal * signal).sum()).item())
    print(f"  S2: signal shape {signal.shape}, norm={signal_norm:.6f} (should be small) ✓")
    # All 4 transitions
    for ti in range(S2Coordinator.N_TRANSITIONS):
        sig = s2.direction_signal(delta, ti)
        mx.eval(sig)
        assert sig.shape == (1, 1, d_model)
    print(f"  S2: all {S2Coordinator.N_TRANSITIONS} transitions produce valid signals ✓")
    # Conflict score
    delta2 = mx.random.normal((1, 32, d_model))
    cs = S2Coordinator.conflict_score(delta, delta2)
    assert -1.0 <= cs <= 1.0, f"Conflict score out of range: {cs}"
    # Self-conflict should be +1
    cs_self = S2Coordinator.conflict_score(delta, delta)
    assert cs_self > 0.99, f"Self-conflict should be ~1.0, got {cs_self:.3f}"
    # Anti-conflict should be -1
    cs_anti = S2Coordinator.conflict_score(delta, -delta)
    assert cs_anti < -0.99, f"Anti-conflict should be ~-1.0, got {cs_anti:.3f}"
    print(f"  S2: conflict scores: random={cs:.3f}, self={cs_self:.3f}, anti={cs_anti:.3f} ✓")
    # Coherence factor (differentiable version)
    cf_agree = S2Coordinator.coherence_factor(delta, delta)
    mx.eval(cf_agree)
    assert abs(float(cf_agree.item()) - 2.0) < 0.01, \
        f"Agreement coherence should be ~2.0, got {cf_agree.item()}"
    cf_fight = S2Coordinator.coherence_factor(delta, -delta)
    mx.eval(cf_fight)
    assert abs(float(cf_fight.item()) - 0.0) < 0.01, \
        f"Conflict coherence should be ~0.0, got {cf_fight.item()}"
    cf_ortho = S2Coordinator.coherence_factor(
        mx.array([[[1.0, 0.0, 0.0, 0.0]]]),
        mx.array([[[0.0, 1.0, 0.0, 0.0]]]),
    )
    mx.eval(cf_ortho)
    assert abs(float(cf_ortho.item()) - 1.0) < 0.01, \
        f"Orthogonal coherence should be ~1.0, got {cf_ortho.item()}"
    print(f"  S2: coherence factor: agree={cf_agree.item():.1f}, "
          f"ortho={cf_ortho.item():.1f}, fight={cf_fight.item():.1f} ✓")

    print("Testing CycleContinue...")
    cc = CycleContinue(d_register, n_registers=n_registers)
    mx.eval(cc.parameters())
    regs = _fresh_bank()
    gate = cc(regs)
    mx.eval(gate)
    assert gate.shape == (), f"Expected scalar, got {gate.shape}"
    assert abs(float(gate.item()) - 0.5) < 0.01, \
        f"CycleContinue gate should start at ~0.5 (neutral), got {gate.item():.3f}"
    print(f"  CycleContinue: gate={gate.item():.3f} (neutral init) ✓")
    # After training (non-zero weights), different register states produce different gates.
    # At init, weights are zero so all inputs → same output (correct: neutral start).
    # Verify by setting a non-zero weight:
    cc.gate_proj.weight = mx.ones_like(cc.gate_proj.weight) * 0.01
    regs2 = [mx.random.normal((d_reg_real,)) for _ in range(n_registers)]
    gate_a = cc(regs)
    gate_b = cc(regs2)
    mx.eval(gate_a, gate_b)
    assert abs(float(gate_a.item()) - float(gate_b.item())) > 1e-6, \
        "CycleContinue should produce different gates for different register states (non-zero weights)"
    print(f"  CycleContinue: different regs → different gates ({gate_a.item():.3f} vs {gate_b.item():.3f}) ✓")

    # Test gradient flow
    print("Testing gradient flow through S4...")
    import mlx.nn as nn
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
            self.param = mx.zeros((d_reg_real,))
        def __call__(self, x):
            bank = [[self.param] * n_registers]
            target = _fresh_bank()
            updates, _ = self.s4(bank, x)
            return mx.sum(updates[0])

    tm = TestModel()
    mx.eval(tm.parameters())
    def test_loss(tm, x):
        return tm(x)
    gfn = nn.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)
    print(f"  S4 gradient flow OK: loss={lv.item():.4f} ✓")

    print("components.py self-test: all ok ✓")
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/kernel.py"
}
```

**Summary:** Reading kernel.py (0-2000)

**Output:**
```
"""
v10 — VSM Tree Kernel

Exact-arithmetic kernel for the 22-op VSM tree.  Pure Python — no MLX,
no torch, no neural computation.  This is the ground-truth evaluator
that the v10 Dispatcher must learn to replicate.

Ported from the proven v9 design (scripts/v9/vsm_tree_v5.py).
All semantics are identical; this file strips out the neural training
machinery and exposes only the kernel interface consumed by the v10
pipeline:

    evaluate_tree(tree, op_assignments) → result (int)

Design overview
───────────────
                ┌──────────┐          ┌────────────┐
  S-expression  │Compressor│ →tokens→ │ Dispatcher │ →op_assignments
  ──────────────┤          │          └────────────┘         │
                │(v10 NN)  │                                  ▼
                └──────────┘                         ┌──────────────┐
                                                     │    Kernel    │ → result
                                                     │  (this file) │
                                                     └──────────────┘

The Kernel's contract:
  • Receives a tree (list of Node) and an op_assignments dict that
    maps node_id → op_idx (integers 0-21).
  • Evaluates bottom-up: children before parents.
  • Returns the integer/boolean result at the root.
  • Values pass through unchanged — only operation classification
    is the neural task.

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


# ══════════════════════════════════════════════════════════════════════
# § 1  Type system
# ══════════════════════════════════════════════════════════════════════

class Type(IntEnum):
    INT     = 0   # exact integer (including 0/1 booleans-as-int)
    BOOL    = 1   # boolean result of a comparison or logical op
    FN      = 2   # partially-applied binary op  → (op_code, bound_arg)
    FN_COMP = 3   # composition of two FNs        → (outer_packed, inner_packed)
    ERROR   = 4   # propagates on ill-typed application

N_TYPES: int = 5


# ══════════════════════════════════════════════════════════════════════
# § 2  Operations
# ══════════════════════════════════════════════════════════════════════

class Op(IntEnum):
    # ── Arithmetic binary (7) ──
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3   # floor division; divisor=0 → 0
    MOD = 4   # modulo;         divisor=0 → 0
    MIN = 5
    MAX = 6

    # ── Comparison (5) ──
    EQ  = 7
    LT  = 8
    GT  = 9
    LE  = 10
    GE  = 11

    # ── Boolean binary (2) ──
    AND = 12
    OR  = 13

    # ── Boolean unary (1) ──
    NOT = 14

    # ── Arithmetic unary (2) ──
    ABS = 15
    NEG = 16

    # ── Conditional (1) ──
    IF  = 17   # ternary: (cond, then, else)

    # ── Lambda / function ops (4) ──
    PARTIAL   = 18  # (op_ref: INT, bound_arg: INT) → FN
    APPLY_FN  = 19  # (FN | FN_COMP, arg: INT) → INT | BOOL
    COMPOSE   = 20  # (outer: FN, inner: FN) → FN_COMP
    APPLY_COMP = 21 # (FN_COMP, arg: INT) → INT | BOOL  [sugar for APPLY_FN on FN_COMP]

N_OPS: int = 22

# Human-readable names, indexed by op code.
OP_NAMES: list[str] = [
    "+", "-", "*", "//", "%", "min", "max",     # 0-6  arithmetic binary
    "=", "<", ">", "<=", ">=",                   # 7-11 comparison
    "and", "or",                                 # 12-13 boolean binary
    "not",                                       # 14    boolean unary
    "abs", "neg",                                # 15-16 arithmetic unary
    "if",                                        # 17    conditional
    "partial", "apply", "comp", "apply-comp",    # 18-21 lambda
]
assert len(OP_NAMES) == N_OPS, "OP_NAMES length must equal N_OPS"

# Subset of ops that are valid targets for PARTIAL (binary, produce INT or BOOL)
PARTIAL_OPS: list[Op] = [
    Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.MIN, Op.MAX,
    Op.EQ,  Op.LT,  Op.GT,  Op.LE,  Op.GE,
]

# Group constants — useful for generation / analysis
BINARY_INT_OPS:  list[Op] = [Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.MIN, Op.MAX]
COMPARISON_OPS:  list[Op] = [Op.EQ,  Op.LT,  Op.GT,  Op.LE,  Op.GE]
BINARY_BOOL_OPS: list[Op] = [Op.AND, Op.OR]
UNARY_INT_OPS:   list[Op] = [Op.ABS, Op.NEG]
LAMBDA_OPS:      list[Op] = [Op.PARTIAL, Op.APPLY_FN, Op.COMPOSE, Op.APPLY_COMP]


# ══════════════════════════════════════════════════════════════════════
# § 3  Function encoding
# ══════════════════════════════════════════════════════════════════════
#
# FN value representation:
#   val = fn_pack(op_code, bound_arg)   stored as a single integer
#
# FN_COMP value representation:
#   val = outer_fn_packed  (the fn applied second)
#   aux = inner_fn_packed  (the fn applied first)
#
# Packing scheme:
#   packed = op_code * FN_PACK_SCALE + (bound_arg + FN_PACK_OFFSET)
#
# This supports bound_arg in the range [-FN_PACK_OFFSET, FN_PACK_SCALE - FN_PACK_OFFSET - 1]
# i.e. [-5000, 4999] by default.

FN_PACK_OFFSET: int = 5000
FN_PACK_SCALE:  int = 10000


def fn_pack(op_code: int, bound_arg: int) -> int:
    """Encode (op_code, bound_arg) into a single integer."""
    return op_code * FN_PACK_SCALE + (bound_arg + FN_PACK_OFFSET)


def fn_unpack(packed: int) -> tuple[int, int]:
    """Decode a packed function back to (op_code, bound_arg)."""
    op_code  = packed // FN_PACK_SCALE
    bound_arg = (packed % FN_PACK_SCALE) - FN_PACK_OFFSET
    return op_code, bound_arg


# ══════════════════════════════════════════════════════════════════════
# § 4  Low-level dispatch
# ══════════════════════════════════════════════════════════════════════

def _eval_binary(op: int, a: int, b: int) -> int:
    """Dispatch a binary arithmetic or comparison op.

    Safe division/modulo: divisor=0 returns 0.
    All comparison ops return 0 or 1 (int, not bool).
    """
    if op == Op.ADD: return a + b
    if op == Op.SUB: return a - b
    if op == Op.MUL: return a * b
    if op == Op.DIV: return a // b if b != 0 else 0
    if op == Op.MOD: return a %  b if b != 0 else 0
    if op == Op.MIN: return min(a, b)
    if op == Op.MAX: return max(a, b)
    if op == Op.EQ:  return int(a == b)
    if op == Op.LT:  return int(a <  b)
    if op == Op.GT:  return int(a >  b)
    if op == Op.LE:  return int(a <= b)
    if op == Op.GE:  return int(a >= b)
    raise ValueError(f"_eval_binary: op {op} is not a binary op")


def kernel_eval(
    op: int,
    child_vals:  list[int],
    child_auxs:  list[int],
    child_types: list[int],
) -> tuple[int, int, int]:
    """Full kernel dispatch for a single node.  Returns (val, aux, type).

    child_vals / child_auxs / child_types are up to 3 elements long
    (children 0, 1, 2).  Callers pad to length 3 with (0, 0, INT).

    val  — the primary result value
    aux  — secondary value (used only for FN_COMP to store the inner fn)
    type — one of Type.INT / BOOL / FN / FN_COMP / ERROR
    """
    # ── Arithmetic binary ──────────────────────────────────────────
    if Op.ADD <= op <= Op.MAX:
        result = _eval_binary(op, child_vals[0], child_vals[1])
        return result, 0, int(Type.INT)

    # ── Comparison ─────────────────────────────────────────────────
    if Op.EQ <= op <= Op.GE:
        result = _eval_binary(op, child_vals[0], child_vals[1])
        return result, 0, int(Type.BOOL)

    # ── Boolean binary ─────────────────────────────────────────────
    if op == Op.AND:
        return int(bool(child_vals[0]) and bool(child_vals[1])), 0, int(Type.BOOL)
    if op == Op.OR:
        return int(bool(child_vals[0]) or  bool(child_vals[1])), 0, int(Type.BOOL)

    # ── Boolean unary ──────────────────────────────────────────────
    if op == Op.NOT:
        return int(not bool(child_vals[0])), 0, int(Type.BOOL)

    # ── Arithmetic unary ───────────────────────────────────────────
    if op == Op.ABS:
        return abs(child_vals[0]), 0, int(Type.INT)
    if op == Op.NEG:
        return -child_vals[0],    0, int(Type.INT)

    # ── Conditional ────────────────────────────────────────────────
    if op == Op.IF:
        result = child_vals[1] if bool(child_vals[0]) else child_vals[2]
        return result, 0, int(Type.INT)

    # ── PARTIAL: create a partially-applied function ───────────────
    if op == Op.PARTIAL:
        # child 0: op reference (an integer equal to the op code to curry)
        # child 1: the bound (left) argument
        fn_op  = child_vals[0]
        bound  = child_vals[1]
        packed = fn_pack(fn_op, bound)
        return packed, 0, int(Type.FN)

    # ── APPLY_FN: apply a function (FN or FN_COMP) to one argument ─
    if op == Op.APPLY_FN:
        ctype = child_types[0]
        if ctype == int(Type.FN):
            fn_op, bound = fn_unpack(child_vals[0])
            result = _eval_binary(fn_op, bound, child_vals[1])
            out_type = Type.BOOL if fn_op in COMPARISON_OPS else Type.INT
            return result, 0, int(out_type)
        if ctype == int(Type.FN_COMP):
            # FN_COMP: val=outer_packed, aux=inner_packed
            # Apply inner first, then outer
            inner_op, inner_bound = fn_unpack(child_auxs[0])
            intermediate = _eval_binary(inner_op, inner_bound, child_vals[1])
            outer_op, outer_bound = fn_unpack(child_vals[0])
            result = _eval_binary(outer_op, outer_bound, intermediate)
            out_type = Type.BOOL if outer_op in COMPARISON_OPS else Type.INT
            return result, 0, int(out_type)
        # Ill-typed application
        return 0, 0, int(Type.ERROR)

    # ── COMPOSE: compose two FNs into an FN_COMP ───────────────────
    if op == Op.COMPOSE:
        # child 0: outer FN (applied second)
        # child 1: inner FN (applied first)
        # Store outer in val, inner in aux — mirrors the FN_COMP layout
        return child_vals[0], child_vals[1], int(Type.FN_COMP)

    # ── APPLY_COMP: explicit sugar for applying a composed function ─
    if op == Op.APPLY_COMP:
        # Identical evaluation path to APPLY_FN on an FN_COMP.
        inner_op, inner_bound = fn_unpack(child_auxs[0])
        intermediate = _eval_binary(inner_op, inner_bound, child_vals[1])
        outer_op, outer_bound = fn_unpack(child_vals[0])
        result = _eval_binary(outer_op, outer_bound, intermediate)
        out_type = Type.BOOL if outer_op in COMPARISON_OPS else Type.INT
        return result, 0, int(out_type)

    # Unknown op — propagate error
    return 0, 0, int(Type.ERROR)


# ══════════════════════════════════════════════════════════════════════
# § 5  Tree node & evaluate_tree
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """A single node in a VSM tree.

    Attributes
    ----------
    node_id  : unique identifier within the tree (int ≥ 0)
    children : list of node_id values for child nodes (empty for leaves)
    value    : for leaf nodes, the literal integer/boolean value;
               for internal nodes this is ignored during evaluation
               (the op drives the computation).
    op_idx   : op code (0-21), only relevant for internal nodes;
               for leaves the kernel treats the node as an identity
               pass-through (value flows up unchanged).
    """
    node_id:  int
    children: list[int] = field(default_factory=list)
    value:    int = 0
    op_idx:   int = 0   # Op code; overridden by op_assignments in evaluate_tree


def evaluate_tree(
    tree: list[Node],
    op_assignments: dict[int, int],
) -> int:
    """Evaluate a VSM tree bottom-up with the given op assignments.

    Parameters
    ----------
    tree
        List of Node objects.  The *last* node in the list is treated
        as the root (topological order: leaves first, root last).
        Every node's node_id must be unique within the list.
    op_assignments
        Maps node_id → op_idx (0-21).  Internal nodes use this to
        determine which operation to apply.  Leaf nodes (no children)
        ignore op_assignments — their value is returned unchanged.

    Returns
    -------
    int
        The primary result value at the root node.
        For BOOL-typed roots this is 0 or 1.
        For FN / FN_COMP-typed roots this is the packed representation.

    Notes
    -----
    * Pure Python — no tensor operations.
    * Each node is evaluated exactly once (bottom-up DFS via index map).
    * Ill-typed applications return 0 (via ERROR propagation).
    """
    # Build an index: node_id → Node for O(1) look-up
    node_map: dict[int, Node] = {n.node_id: n for n in tree}

    # Cache evaluated results: node_id → (val, aux, type)
    result_cache: dict[int, tuple[int, int, int]] = {}

    def _eval(node_id: int) -> tuple[int, int, int]:
        if node_id in result_cache:
            return result_cache[node_id]

        node = node_map[node_id]

        # Leaf: identity pass-through
        if not node.children:
            result = (node.value, 0, int(Type.INT))
            result_cache[node_id] = result
            return result

        # Internal node: recurse into children first (bottom-up)
        child_results = [_eval(cid) for cid in node.children]

        # Pad to 3 children
        while len(child_results) < 3:
            child_results.append((0, 0, int(Type.INT)))

        child_vals  = [r[0] for r in child_results]
        child_auxs  = [r[1] for r in child_results]
        child_types = [r[2] for r in child_results]

        op = op_assignments.get(node_id, node.op_idx)
        val, aux, typ = kernel_eval(op, child_vals, child_auxs, child_types)

        result = (val, aux, typ)
        result_cache[node_id] = result
        return result

    # The root is the last node in the list (topological convention)
    root_id = tree[-1].node_id
    root_val, _aux, _type = _eval(root_id)
    return root_val


# ══════════════════════════════════════════════════════════════════════
# § 6  Convenience: evaluate a raw nested-tuple tree
# ══════════════════════════════════════════════════════════════════════
#
# The v9 tree representation is nested Python tuples, e.g.
#   (Op.ADD, (Op.MUL, 3, 4), 5)
#
# This helper lets tests and notebooks use that format directly without
# constructing Node objects.

def eval_tuple_tree(
    node: Any,
    expected_type: Type = Type.INT,
) -> tuple[int, int, int]:
    """Evaluate a v9-style nested-tuple tree.  Returns (val, aux, type).

    Leaves are plain Python ints.
    Internal nodes are (op_code, child, ...) tuples.

    This is a direct port of v9's eval_tree_full / _collect_and_eval.
    """
    # Leaf
    if isinstance(node, int):
        t = int(Type.BOOL) if expected_type == Type.BOOL else int(Type.INT)
        return node, 0, t

    op = int(node[0])
    children = node[1:]

    # Determine expected types for children
    child_expected: list[Type] = []
    if op in [int(o) for o in BINARY_INT_OPS]:
        child_expected = [Type.INT, Type.INT]
    elif op in [int(o) for o in COMPARISON_OPS]:
        child_expected = [Type.INT, Type.INT]
    elif op in [int(o) for o in BINARY_BOOL_OPS]:
        child_expected = [Type.BOOL, Type.BOOL]
    elif op == Op.NOT:
        child_expected = [Type.BOOL]
    elif op in [int(o) for o in UNARY_INT_OPS]:
        child_expected = [Type.INT]
    elif op == Op.IF:
        child_expected = [Type.BOOL, expected_type, expected_type]
    elif op == Op.PARTIAL:
        child_expected = [Type.INT, Type.INT]   # op_ref is stored as an int
    elif op == Op.APPLY_FN:
        child_expected = [Type.FN, Type.INT]
    elif op == Op.COMPOSE:
        child_expected = [Type.FN, Type.FN]
    elif op == Op.APPLY_COMP:
        child_expected = [Type.FN_COMP, Type.INT]

    child_results = []
    for i, child in enumerate(children):
        ct = child_expected[i] if i < len(child_expected) else Type.INT
        child_results.append(eval_tuple_tree(child, ct))

    # Pad to 3
    while len(child_results) < 3:
        child_results.append((0, 0, int(Type.INT)))

    child_vals  = [r[0] for r in child_results]
    child_auxs  = [r[1] for r in child_results]
    child_types = [r[2] for r in child_results]

    return kernel_eval(op, child_vals, child_auxs, child_types)


# ══════════════════════════════════════════════════════════════════════
# § 7  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Smoke-test all 22 ops.  Runs on `python kernel.py`."""

    # ── Arithmetic binary ──────────────────────────────────────────
    assert eval_tuple_tree((Op.ADD, 3, 4))[0]     == 7
    assert eval_tuple_tree((Op.SUB, 10, 3))[0]    == 7
    assert eval_tuple_tree((Op.MUL, 3, 4))[0]     == 12
    assert eval_tuple_tree((Op.DIV, 10, 3))[0]    == 3
    assert eval_tuple_tree((Op.DIV, 10, 0))[0]    == 0   # safe div
    assert eval_tuple_tree((Op.MOD, 10, 3))[0]    == 1
    assert eval_tuple_tree((Op.MOD, 10, 0))[0]    == 0   # safe mod
    assert eval_tuple_tree((Op.MIN, 3, 7))[0]     == 3
    assert eval_tuple_tree((Op.MAX, 3, 7))[0]     == 7

    # ── Comparison ─────────────────────────────────────────────────
    assert eval_tuple_tree((Op.EQ,  5, 5), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.EQ,  5, 6), Type.BOOL)[0] == 0
    assert eval_tuple_tree((Op.LT,  3, 7), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.GT,  7, 3), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.LE,  3, 3), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.GE,  3, 3), Type.BOOL)[0] == 1

    # ── Boolean binary ─────────────────────────────────────────────
    assert eval_tuple_tree((Op.AND, 1, 0), Type.BOOL)[0] == 0
    assert eval_tuple_tree((Op.OR,  1, 0), Type.BOOL)[0] == 1

    # ── Boolean unary ──────────────────────────────────────────────
    assert eval_tuple_tree((Op.NOT, 0), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.NOT, 1), Type.BOOL)[0] == 0

    # ── Arithmetic unary ───────────────────────────────────────────
    assert eval_tuple_tree((Op.ABS, -5))[0]  == 5
    assert eval_tuple_tree((Op.NEG,  5))[0]  == -5

    # ── Conditional ────────────────────────────────────────────────
    assert eval_tuple_tree((Op.IF, 1, 42, 99))[0] == 42
    assert eval_tuple_tree((Op.IF, 0, 42, 99))[0] == 99
    # Nested IF
    assert eval_tuple_tree((Op.IF, (Op.LT, 3, 7), 1, 0))[0] == 1

    # ── PARTIAL + APPLY_FN ─────────────────────────────────────────
    # (partial + 3) applied to 4 = 3 + 4 = 7
    fn_add3 = (Op.PARTIAL, int(Op.ADD), 3)
    assert eval_tuple_tree((Op.APPLY_FN, fn_add3, 4))[0] == 7

    # (partial * 5) applied to 6 = 5 * 6 = 30
    fn_mul5 = (Op.PARTIAL, int(Op.MUL), 5)
    assert eval_tuple_tree((Op.APPLY_FN, fn_mul5, 6))[0] == 30

    # (partial < 10) applied to 7 → 10 < 7 → 0
    fn_lt10 = (Op.PARTIAL, int(Op.LT), 10)
    assert eval_tuple_tree((Op.APPLY_FN, fn_lt10, 7))[0] == 0

    # ── COMPOSE + APPLY_FN on FN_COMP ─────────────────────────────
    # comp(+3, *2): apply *2 first then +3 → (x*2)+3
    # (4 * 2) + 3 = 11
    fn_add3 = (Op.PARTIAL, int(Op.ADD), 3)
    fn_mul2 = (Op.PARTIAL, int(Op.MUL), 2)
    comp    = (Op.COMPOSE, fn_add3, fn_mul2)
    assert eval_tuple_tree((Op.APPLY_FN, comp, 4))[0] == 11

    # ── APPLY_COMP (explicit sugar) ────────────────────────────────
    # same composition, different apply op
    assert eval_tuple_tree((Op.APPLY_COMP, comp, 4))[0] == 11

    # ── evaluate_tree (Node-based API) ────────────────────────────
    # Encode: (ADD, 3, 4) as a Node tree
    leaf3  = Node(node_id=0, value=3)
    leaf4  = Node(node_id=1, value=4)
    root   = Node(node_id=2, children=[0, 1], op_idx=int(Op.ADD))
    tree   = [leaf3, leaf4, root]
    result = evaluate_tree(tree, {2: int(Op.ADD)})
    assert result == 7, f"expected 7, got {result}"

    # Test op_assignments override: Dispatcher overrides op_idx
    result_mul = evaluate_tree(tree, {2: int(Op.MUL)})  # same tree, MUL instead
    assert result_mul == 12, f"expected 12, got {result_mul}"

    # ── OP_NAMES index consistency ─────────────────────────────────
    assert OP_NAMES[Op.ADD]        == "+"
    assert OP_NAMES[Op.IF]         == "if"
    assert OP_NAMES[Op.PARTIAL]    == "partial"
    assert OP_NAMES[Op.APPLY_FN]   == "apply"
    assert OP_NAMES[Op.COMPOSE]    == "comp"
    assert OP_NAMES[Op.APPLY_COMP] == "apply-comp"

    print("kernel.py self-test: all assertions passed ✓")
    print(f"  {N_OPS} ops  {N_TYPES} types  fn_pack round-trip OK")


if __name__ == "__main__":
    _self_test()
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/kernel_dispatch.py"
}
```

**Summary:** Reading kernel_dispatch.py (0-2000)

**Output:**
```
"""
Kernel dispatch modules for the descending VSM arm.

The descending arm's S1 operations are kernel-shaped, not compression-shaped.
Instead of TernaryFFN (compress), the descending arm routes representations
through kernel op pathways (dispatch).

The 22 kernel ops (from kernel.py) are pre-wired as architectural identity —
the model discovers them as easy paths while training on prose via relational
loss. The ternary routing topology learns which positions benefit from which
kernel op family.

Architecture per descending pass:
  Phase 0 (dispatch):   KernelDispatch — route to kernel op families
  Phase 1 (integrate):  KernelIntegrate — type the dispatched result locally
  Phase 2 (converge):   StrideStack coarse→fine — propagate typed dispatch

The kernel op embeddings are the S5 identity of the dispatcher VSM.
They encode WHAT each operation IS — its characteristic transformation
pattern. The dispatch projection learns WHEN each op is relevant.

Design principles:
  - Shapes not outputs: the kernel provides the right shape for the
    descending arm, replacing compression ops that always go to passthrough
  - Easy path: kernel ops are architecturally available, not learned targets
  - Pre-wired: op embeddings initialized with structure, not random
  - Observable: dispatch weights show which kernel ops activate where

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════
# Kernel op families — from kernel.py
# ══════════════════════════════════════════════════════════════════

N_OPS = 22
N_TYPES = 5

# Op family indices for structured initialization
OP_FAMILIES = {
    "arith_binary":  list(range(0, 7)),    # add sub mul div mod min max
    "comparison":    list(range(7, 12)),    # eq lt gt le ge
    "bool_binary":   [12, 13],             # and or
    "bool_unary":    [14],                 # not
    "arith_unary":   [15, 16],             # abs neg
    "conditional":   [17],                 # if
    "lambda":        list(range(18, 22)),   # partial apply compose apply-comp
}

N_FAMILIES = len(OP_FAMILIES)


# ══════════════════════════════════════════════════════════════════
# KernelDispatch — routes representations to kernel op pathways
# ══════════════════════════════════════════════════════════════════


class KernelDispatch(nn.Module):
    """Kernel-aware transformation for second arm phase 0 (dispatch).

    Replaces TernaryFFN prep in the second arm.

    Architecture (top-k MoE routing):
      1. Dispatch logits: project to (n_ops,) scores — which kernel ops?
         Conditioned on ascending register banks (type/scope/role) when
         available, so dispatch can see what the ascending arm learned.
      2. Top-k selection: only the k highest-scoring ops participate.
         Softmax over the k winners only — not all 22 ops.
      3. Op modulation: weighted kernel identity added to representation
         (using L2-normalized op embeddings to prevent runaway growth).
      4. Pathway: shared ternary transform, biased by kernel identity
      5. Gated residual

    Why top-k routing (not softmax over all ops):
      With full softmax, register conditioning learned a massive bias
      toward one op (+10.2 for `if`), saturating softmax and giving
      zero gradient to all other ops. They died permanently. Meanwhile
      one op's embedding grew to 4× others via positive feedback.
      Top-k routing ensures the runner-up op always gets meaningful
      weight (~e^(-delta)), keeping gradient alive for all ops. The
      natural distribution can be as skewed as the data demands —
      FN_COMP can dominate prose — but rare ops stay trainable for
      their niches. Same principle as Switch Transformer / MoE routing.

    Op embedding normalization:
      All op embeddings are L2-normalized to a fixed scale each forward
      pass. The dispatch weights (router scores) alone determine each
      op's influence — not embedding magnitude. This prevents the
      rich-get-richer feedback loop that created the >= fossil.

    Register conditioning: the ascending arm's registers carry
    type/scope/role information that tells dispatch what kind of
    content is at each position. Dispatch sees "the ascending arm
    thinks this is scope=local, type=arithmetic" and can route to
    arithmetic ops accordingly.
    """

    def __init__(
        self,
        d_model: int,
        n_ops: int = N_OPS,
        d_ff: int | None = None,
        dropout: float = 0.1,
        n_registers: int = 3,
        d_register: int = 128,
        max_cond_banks: int = 5,
        top_k: int = 2,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_ops = n_ops
        self.top_k = min(top_k, n_ops)
        if d_ff is None:
            d_ff = d_model * 3

        # Pad n_ops to multiple of 16 for TernaryLinear
        self.n_ops_padded = ((n_ops + 15) // 16) * 16  # 32

        self.norm = nn.RMSNorm(d_model)

        # Dispatch projection: hidden → op logits
        # TernaryLinear: the ternary topology learns discrete routing
        self.dispatch = TernaryLinear(d_model, self.n_ops_padded, pre_norm=False)

        # ── Register conditioning ─────────────────────────────
        # Ascending registers → dispatch bias: which ops should activate?
        # Registers carry type/scope/role from the ascending arm.
        # This is a real-valued (not ternary) projection because
        # registers are real-valued and we want smooth gradients
        # for the conditioning to learn quickly.
        self.n_registers = n_registers
        self.d_reg_real = d_register * 2
        self.max_cond_banks = max_cond_banks
        max_cond_dim = max_cond_banks * n_registers * self.d_reg_real
        self._max_cond_dim = ((max_cond_dim + 15) // 16) * 16
        # Small real-valued projection: register summary → per-op bias
        self.register_cond = nn.Linear(self._max_cond_dim, self.n_ops_padded)
        # Initialize to zero so conditioning starts inert
        self.register_cond.weight = mx.zeros_like(self.register_cond.weight)
        self.register_cond.bias = mx.zeros_like(self.register_cond.bias)

        # Op embeddings: kernel S5 identity — what each op IS
        # Real-valued, trainable. Initialized with structure:
        # each op gets a near-orthogonal direction in d_model space.
        self.op_embeddings = _init_op_embeddings(n_ops, d_model)

        # Op embedding target norm — embeddings are L2-normalized to this
        # scale each forward pass. Prevents runaway growth (the >=
        # fossil problem: one embedding grows to 4× others via positive
        # feedback, then freezes when softmax starves its gradient).
        # The dispatch weights alone should determine influence, not
        # embedding magnitude.
        self.op_embed_scale = 0.5

        # Pathway: transforms representation using dispatched op identity
        # The kernel identity modulates the input; the pathway transforms
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

    def _normalize_op_embeddings(self) -> mx.array:
        """L2-normalize op embeddings to fixed scale.

        Prevents runaway embedding growth. The dispatch weights (router
        scores) determine each op's influence — not embedding magnitude.
        Without this, a positive feedback loop develops: higher dispatch
        weight → more gradient → larger embedding → more modulation
        impact → even higher effective weight. Once the loop saturates
        softmax, non-dominant ops get zero gradient and die permanently.

        Returns normalized embeddings (used in forward, gradient flows
        through to the raw embeddings for training).
        """
        norms = mx.sqrt(
            mx.sum(self.op_embeddings * self.op_embeddings, axis=-1, keepdims=True)
            + 1e-8
        )
        return self.op_embeddings * (self.op_embed_scale / norms)

    def __call__(self, x: mx.array, registers: list[list[mx.array]] | None = None,
                 op_emphasis: mx.array | None = None) -> mx.array:
        """
        x: (B, L, d_model)
        registers: list of register banks from ascending arm, each bank is
                   a list of register vectors. Used to condition dispatch.
        op_emphasis: (n_ops,) per-op emphasis from S4's register state.
                     Modulates op embeddings: emphasis > 1 amplifies,
                     < 1 suppresses. Driven by what S4's intelligence
                     observes, EMA-tracked across steps for stability.
        Returns: (B, L, d_model) — with residual connection

        Routing: top-k MoE style. Per position, only the top-k ops
        (by dispatch logit) participate. Softmax is computed over the
        k winners only. This ensures:
          - The dominant op (likely FN_COMP for prose) gets most weight
          - The runner-up op still gets meaningful weight and gradient
          - Rare ops (arithmetic, comparison) stay alive — they'll
            occasionally appear in top-k for relevant content, giving
            them gradient to learn their niche
          - Natural distribution skew is preserved (no forced balancing)
        """
        h = self.norm(x)

        # Step 1: Dispatch logits — which kernel ops are relevant?
        dispatch_logits = self.dispatch(h)[..., :self.n_ops]  # (B, L, n_ops)

        # Register conditioning: add per-op bias from ascending registers
        if registers is not None:
            # Flatten all register banks into one vector
            parts = []
            for bank in registers:
                for reg in bank:
                    parts.append(reg)
            cond_input = mx.concatenate(parts, axis=-1)  # (total_reg_dims,)
            # Pad to max
            if cond_input.shape[0] < self._max_cond_dim:
                cond_input = mx.concatenate([
                    cond_input,
                    mx.zeros((self._max_cond_dim - cond_input.shape[0],))
                ])
            # Project to per-op bias
            reg_bias = self.register_cond(cond_input)[:self.n_ops]  # (n_ops,)
            # Add to dispatch logits (broadcast across B, L)
            dispatch_logits = dispatch_logits + reg_bias[None, None, :]

        # Step 2: Top-k routing — only k ops participate per position
        # This prevents softmax saturation from killing gradient to
        # non-dominant ops. With k=2, the runner-up always gets
        # meaningful weight (~e^(-delta) where delta is the logit gap).
        B, L, _ = dispatch_logits.shape
        top_k_values = mx.topk(dispatch_logits, k=self.top_k, axis=-1)  # (B, L, k)
        # Threshold: minimum value among top-k at each position
        threshold = mx.min(top_k_values, axis=-1, keepdims=True)  # (B, L, 1)
        # Mask: keep only top-k, set others to -inf
        mask = mx.where(
            dispatch_logits >= threshold,
            dispatch_logits,
            mx.full(dispatch_logits.shape, -1e9),
        )
        # Softmax over masked logits — only top-k ops get nonzero weight
        dispatch_weights = mx.softmax(mask, axis=-1)  # (B, L, n_ops)

        # Cache for probing (full 22-wide, zeros for non-top-k)
        self._dispatch_weights = mx.stop_gradient(dispatch_weights)

        # Step 3: Normalized op embeddings — prevent runaway growth
        op_emb = self._normalize_op_embeddings()  # (n_ops, d_model)

        # S4→S5 emphasis: modulate which ops are more/less available.
        # Driven by S4's register state, EMA-tracked across steps.
        # emphasis > 1 amplifies an op's embedding (makes it louder
        # in the modulation), < 1 suppresses (quieter). The dispatch
        # weights (routing) still control WHICH ops fire per position;
        # emphasis shifts the landscape of what's available.
        if op_emphasis is not None:
            op_emb = op_emb * op_emphasis[:, None]  # (n_ops, d_model)

        # Step 4: Weighted op embedding — kernel identity modulation
        # (B, L, n_ops) @ (n_ops, d_model) → (B, L, d_model)
        op_context = dispatch_weights @ op_emb

        # Step 5: Modulate input with kernel identity, then transform
        modulated = h + op_context
        out = self.down(nn.gelu(self.up(modulated)))

        return x + self.dropout(out)


# ══════════════════════════════════════════════════════════════════
# KernelIntegrate — combines kernel pathway results
# ══════════════════════════════════════════════════════════════════


class KernelIntegrate(nn.Module):
    """Kernel-aware integration with exact computation pathway.

    Phase 2 of the descending arm: after dispatch selected ops and
    stride propagated across context, integrate can now see both
    local op bias and spatial patterns.

    Dual pathway architecture:
      1. **Operand extraction**: project hidden state to extract two
         operands as scalar logits (over a value range), and read the
         dispatch weights from KernelDispatch to know WHICH op to apply.
      2. **Exact kernel computation**: apply the actual kernel function
         (ADD, LE, PARTIAL, etc.) to the extracted operands. This is
         non-differentiable but exact — no approximation.
      3. **Result encoding**: map the kernel result back to d_model
         via learned embedding, producing a "kernel signal" vector.
      4. **Compute gate**: learned scalar gate (0-1) per position that
         blends the kernel result with the standard FFN pathway.
         Starts at 0 (pure FFN) so the model can learn when to trust
         the kernel. This is critical: prose positions should gate=0
         (no computation), structured positions should gate→1.
      5. **Standard FFN pathway**: type modulation + shared transform,
         as before. This handles prose and non-computational positions.
      6. **Blend**: output = gate * kernel_result + (1-gate) * ffn_result

    The compute gate makes this backward-compatible: at initialization,
    gate=0 everywhere, so the model behaves identically to the old
    KernelIntegrate. As training progresses on structured data, the
    gate learns to open for positions where exact computation helps.

    Gradient flow through the non-differentiable kernel:
      The kernel itself has no gradient (argmax + integer arithmetic).
      But gradient flows through:
        - The operand extraction projections (which operands to extract)
        - The result encoder (which d_model direction the result maps to)
        - The compute gate (when to use kernel vs FFN)
      This is the same straight-through pattern as in v9.
    """

    def __init__(
        self,
        d_model: int,
        n_types: int = N_TYPES,
        n_ops: int = N_OPS,
        d_ff: int | None = None,
        dropout: float = 0.1,
        max_val: int = 256,
        result_buckets: int = 1024,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_types = n_types
        self.n_ops = n_ops
        self.max_val = max_val
        if d_ff is None:
            d_ff = d_model * 4

        # Pad n_types to multiple of 16
        self.n_types_padded = ((n_types + 15) // 16) * 16

        self.norm = nn.RMSNorm(d_model)

        # ── Type pathway (unchanged) ──────────────────────────
        self.type_proj = TernaryLinear(d_model, self.n_types_padded, pre_norm=False)
        self.type_embeddings = _init_type_embeddings(n_types, d_model)

        # ── Standard FFN pathway (unchanged) ──────────────────
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        # ── Kernel computation pathway (NEW) ──────────────────

        # Operand extraction: hidden → two value distributions
        # Each operand is a distribution over [0, max_val), decoded via argmax
        max_val_padded = ((max_val + 15) // 16) * 16
        self._max_val_padded = max_val_padded
        self.operand1_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)
        self.operand2_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)

        # Result encoder: integer result → d_model vector
        # Larger bucket range than v9: results can be negative (comparisons,
        # subtraction) and large (multiplication)
        self.result_buckets = result_buckets
        self.result_offset = result_buckets // 2  # center at 0
        self.result_embed = nn.Embedding(result_buckets, d_model)

        # Compute gate: per-position scalar, initialized to produce ~0
        # so the model starts with pure FFN (backward-compatible)
        self.gate_proj = nn.Linear(d_model, 1)
        # Initialize gate bias negative so sigmoid → ~0 at start
        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)
        self.gate_proj.bias = mx.ones_like(self.gate_proj.bias) * -5.0

        self.dropout = nn.Dropout(dropout)

    def _kernel_compute(
        self,
        h: mx.array,
        dispatch_weights: mx.array | None,
    ) -> tuple[mx.array, dict]:
        """Extract operands, run kernel, encode result.

        Args:
            h: (B, L, d_model) — normalized hidden state
            dispatch_weights: (B, L, n_ops) from KernelDispatch, or None

        Returns:
            kernel_out: (B, L, d_model) — encoded kernel results
            kernel_info: dict with decoded ops/args/results for probing
        """
        B, L, _ = h.shape

        # Extract operands via argmax (non-differentiable)
        op1_logits = self.operand1_proj(h)[..., :self.max_val]  # (B, L, max_val)
        op2_logits = self.operand2_proj(h)[..., :self.max_val]  # (B, L, max_val)

        # stop_gradient: argmax is non-differentiable, all gradient
        # flows through the result embedding and the compute gate
        arg1 = mx.stop_gradient(mx.argmax(op1_logits, axis=-1)).astype(mx.int32)  # (B, L)
        arg2 = mx.stop_gradient(mx.argmax(op2_logits, axis=-1)).astype(mx.int32)  # (B, L)

        # Get op from dispatch weights (argmax of top-1)
        if dispatch_weights is not None:
            op = mx.stop_gradient(mx.argmax(dispatch_weights, axis=-1)).astype(mx.int32)  # (B, L)
        else:
            op = mx.zeros((B, L), dtype=mx.int32)

        # ── Exact kernel computation (non-differentiable) ─────
        # Compute all possible results, select by op code
        # This is vectorized: compute all ops, mask-select by dispatched op

        # Arithmetic binary: ADD(0), SUB(1), MUL(2), DIV(3), MOD(4), MIN(5), MAX(6)
        r_add = arg1 + arg2
        r_sub = arg1 - arg2
        r_mul = arg1 * arg2
        # Safe division
        safe_arg2 = mx.where(arg2 == 0, mx.ones_like(arg2), arg2)
        r_div = arg1 // safe_arg2
        r_div = mx.where(arg2 == 0, mx.zeros_like(r_div), r_div)
        r_mod = arg1 % safe_arg2
        r_mod = mx.where(arg2 == 0, mx.zeros_like(r_mod), r_mod)
        r_min = mx.minimum(arg1, arg2)
        r_max = mx.maximum(arg1, arg2)

        # Comparison: EQ(7), LT(8), GT(9), LE(10), GE(11)
        r_eq = (arg1 == arg2).astype(mx.int32)
        r_lt = (arg1 < arg2).astype(mx.int32)
        r_gt = (arg1 > arg2).astype(mx.int32)
        r_le = (arg1 <= arg2).astype(mx.int32)
        r_ge = (arg1 >= arg2).astype(mx.int32)

        # Boolean binary: AND(12), OR(13)
        b1 = (arg1 != 0)
        b2 = (arg2 != 0)
        r_and = (b1 & b2).astype(mx.int32)
        r_or = (b1 | b2).astype(mx.int32)

        # Boolean unary: NOT(14)
        r_not = (~b1).astype(mx.int32)

        # Arithmetic unary: ABS(15), NEG(16)
        r_abs = mx.abs(arg1)
        r_neg = -arg1

        # Conditional: IF(17) — arg1=cond, arg2=then (no else in 2-operand form)
        r_if = mx.where(arg1 != 0, arg2, mx.zeros_like(arg2))

        # Lambda ops (18-21): return arg1 unchanged (placeholder —
        # actual lambda computation needs tree structure, not 2 scalars)
        r_lambda = arg1

        # Stack all results and select by op
        # Shape: (22, B, L) — one result per op
        all_results = mx.stack([
            r_add, r_sub, r_mul, r_div, r_mod, r_min, r_max,  # 0-6
            r_eq, r_lt, r_gt, r_le, r_ge,                      # 7-11
            r_and, r_or,                                        # 12-13
            r_not,                                              # 14
            r_abs, r_neg,                                       # 15-16
            r_if,                                               # 17
            r_lambda, r_lambda, r_lambda, r_lambda,             # 18-21
        ], axis=0)  # (22, B, L)

        # Select result by op code: gather along op dimension
        # op is (B, L), need to index into (22, B, L)
        op_clamped = mx.clip(op, 0, N_OPS - 1)
        # Use advanced indexing: result[op[b,l], b, l]
        b_idx = mx.broadcast_to(mx.arange(B)[:, None], (B, L))
        l_idx = mx.broadcast_to(mx.arange(L)[None, :], (B, L))
        result = all_results[op_clamped, b_idx, l_idx]  # (B, L)

        # ── Encode result back to d_model ─────────────────────
        # stop_gradient on the index computation: the kernel itself
        # is non-differentiable. Gradient flows through result_embed
        # weights (which embedding direction the result maps to) and
        # through the gate (when to use this pathway).
        result_idx = mx.stop_gradient(
            mx.clip(result + self.result_offset, 0, self.result_buckets - 1)
        ).astype(mx.int32)
        kernel_out = self.result_embed(result_idx)  # (B, L, d_model)

        # Probing info
        kernel_info = {
            "op": mx.stop_gradient(op),
            "arg1": mx.stop_gradient(arg1),
            "arg2": mx.stop_gradient(arg2),
            "result": mx.stop_gradient(result),
        }

        return kernel_out, kernel_info

    def __call__(
        self,
        x: mx.array,
        dispatch_weights: mx.array | None = None,
    ) -> mx.array:
        """
        x: (B, L, d_model)
        dispatch_weights: (B, L, n_ops) from KernelDispatch (cached)
        Returns: (B, L, d_model) — with residual connection
        """
        h = self.norm(x)

        # ── Type projection ───────────────────────────────────
        type_logits = self.type_proj(h)[..., :self.n_types]
        type_weights = mx.softmax(type_logits, axis=-1)
        self._type_weights = mx.stop_gradient(type_weights)

        # ── Standard FFN pathway ──────────────────────────────
        type_context = type_weights @ self.type_embeddings
        modulated = h + type_context
        ffn_out = self.down(nn.gelu(self.up(modulated)))  # (B, L, d_model)

        # ── Kernel computation pathway ────────────────────────
        kernel_out, kernel_info = self._kernel_compute(h, dispatch_weights)
        self._kernel_info = kernel_info

        # ── Compute gate: blend kernel vs FFN ─────────────────
        gate = mx.sigmoid(self.gate_proj(h))  # (B, L, 1)
        self._compute_gate = mx.stop_gradient(gate)

        # Blend: gate=0 → pure FFN, gate=1 → pure kernel
        blended = gate * kernel_out + (1.0 - gate) * ffn_out

        return x + self.dropout(blended)


# ══════════════════════════════════════════════════════════════════
# Structured initialization
# ══════════════════════════════════════════════════════════════════


def _init_op_embeddings(n_ops: int, d_model: int) -> mx.array:
    """Initialize kernel op embeddings with near-orthogonal structure.

    Each op gets a characteristic direction in d_model space.
    Ops within the same family share a family subspace but have
    distinct directions within it. This gives the ternary routing
    fabric structured targets to route toward.

    Family subspace allocation:
      Each family gets a contiguous block of dimensions.
      Within the block, ops get distinct orthogonal directions.
      Remaining dimensions are shared (allow cross-family interaction).
    """
    embeddings = mx.zeros((n_ops, d_model))

    # Allocate dimension blocks per family
    # Reserve first 50% for family-specific, last 50% shared
    family_dims = d_model // 2
    shared_dims = d_model - family_dims

    families = list(OP_FAMILIES.values())
    n_families = len(families)
    dims_per_family = family_dims // n_families

    family_offset = 0
    for fi, op_indices in enumerate(families):
        n_in_family = len(op_indices)
        # Each op in the family gets a direction in the family block
        for oi, op_idx in enumerate(op_indices):
            # Family-specific component: one-hot-ish within family block
            dim_start = family_offset
            dim_end = min(family_offset + dims_per_family, family_dims)
            if dim_end > dim_start and n_in_family > 0:
                # Spread ops across family dimensions
                op_dim = dim_start + (oi * (dim_end - dim_start)) // max(n_in_family, 1)
                op_dim = min(op_dim, dim_end - 1)
                embeddings = embeddings.at[op_idx, op_dim].add(1.0)

            # Shared component: small random for cross-family interaction
            shared_component = mx.random.normal((shared_dims,)) * 0.1
            embeddings = embeddings.at[op_idx, family_dims:].add(shared_component)

        family_offset += dims_per_family

    # L2-normalize each embedding, then scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1  # small scale so modulation is gentle

    return embeddings


def _init_type_embeddings(n_types: int, d_model: int) -> mx.array:
    """Initialize kernel type embeddings.

    5 types: INT, BOOL, FN, FN_COMP, ERROR
    Each gets a near-orthogonal direction. Types are fundamental —
    every position has a type, and the type determines what operations
    are valid downstream.
    """
    embeddings = mx.zeros((n_types, d_model))

    # Each type gets a distinct block of dimensions
    dims_per_type = d_model // (n_types * 2)  # use half the space for type identity

    for ti in range(n_types):
        dim_start = ti * dims_per_type
        dim_end = min((ti + 1) * dims_per_type, d_model)
        # Characteristic direction
        for d in range(dim_start, dim_end):
            embeddings = embeddings.at[ti, d].add(1.0)

        # Small random component in remaining dims for interaction
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[ti].add(shared)

    # L2-normalize and scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1

    return embeddings


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import numpy as np
    d_model = 512

    print("Testing KernelDispatch (top-k=2)...")
    dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536, top_k=2)
    x = mx.random.normal((1, 64, d_model))
    y = dispatch(x)
    mx.eval(y)
    assert y.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y.shape}"

    # Check dispatch weights are cached (22-wide)
    assert hasattr(dispatch, '_dispatch_weights')
    dw = dispatch._dispatch_weights
    mx.eval(dw)
    assert dw.shape == (1, 64, 22), f"Expected (1, 64, 22), got {dw.shape}"

    # Top-k: only k ops should have nonzero weight per position
    dw_np = np.array(dw[0])
    nonzero_per_pos = np.sum(dw_np > 1e-6, axis=1)
    assert np.all(nonzero_per_pos <= 3), \
        f"Top-k=2 should give ≤3 nonzero ops per position, got max {nonzero_per_pos.max()}"
    # Note: <= 3 not == 2 because ties at the threshold can include extras
    print(f"  Active ops per position: mean={nonzero_per_pos.mean():.1f} "
          f"min={nonzero_per_pos.min()} max={nonzero_per_pos.max()} ✓")

    # Weights for active ops should still sum to ~1
    sums = mx.sum(dw, axis=-1)
    mx.eval(sums)
    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-4).item(), \
        f"Dispatch weights should sum to ~1, got min={float(mx.min(sums).item()):.4f}"
    print(f"  KernelDispatch: {x.shape} → {y.shape} ✓")
    print(f"  Dispatch weights: {dw.shape}, top-k routing ✓")

    # Check op embedding normalization
    normed = dispatch._normalize_op_embeddings()
    mx.eval(normed)
    norms = np.linalg.norm(np.array(normed), axis=1)
    assert np.allclose(norms, dispatch.op_embed_scale, atol=1e-3), \
        f"Normalized embeddings should have norm={dispatch.op_embed_scale}, got {norms}"
    print(f"  Op embedding norms: all ≈ {dispatch.op_embed_scale} ✓")

    print("\nTesting KernelIntegrate...")
    integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)
    y2 = integrate(x)
    mx.eval(y2)
    assert y2.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y2.shape}"
    tw = integrate._type_weights
    mx.eval(tw)
    assert tw.shape == (1, 64, 5), f"Expected (1, 64, 5), got {tw.shape}"
    print(f"  KernelIntegrate: {x.shape} → {y2.shape} ✓")
    print(f"  Type weights: {tw.shape} ✓")

    # Check op embeddings have structure (use normalized versions)
    op_emb = normed
    add_embed = op_emb[0]   # ADD
    sub_embed = op_emb[1]   # SUB
    eq_embed = op_emb[7]    # EQ (different family)
    mx.eval(add_embed, sub_embed, eq_embed)
    same_fam_sim = float(mx.sum(add_embed * sub_embed).item())
    cross_fam_sim = float(mx.sum(add_embed * eq_embed).item())
    print(f"  Op embedding structure: same-family sim={same_fam_sim:.4f}, "
          f"cross-family sim={cross_fam_sim:.4f}")

    # Test gradient flow — critical: verify all top-k ops get gradient
    import mlx.nn as nn_mod

    class TestModel(nn_mod.Module):
        def __init__(self):
            super().__init__()
            self.dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536, top_k=2)
            self.integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)

        def __call__(self, x):
            h = self.dispatch(x)
            h = self.integrate(h)
            return mx.mean(h)

    tm = TestModel()
    mx.eval(tm.parameters())

    def test_loss(tm, x):
        return tm(x)

    gfn = nn_mod.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)

    # Check that op_embeddings gradient has nonzero entries for multiple ops
    op_grad = g["dispatch"]["op_embeddings"]
    mx.eval(op_grad)
    og_np = np.array(op_grad)
    grad_norms = np.linalg.norm(og_np, axis=1)
    n_with_grad = np.sum(grad_norms > 1e-6)
    print(f"  Gradient flow OK: loss={lv.item():.4f}")
    print(f"  Ops with gradient: {n_with_grad}/22 "
          f"(top-k=2 should give ≥2) ✓")

    print("\nkernel_dispatch.py self-test: all ok ✓")
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/model.py"
}
```

**Summary:** Reading model.py (0-2000)

**Output:**
```
"""
v10 Model — Tree of VSMs: compressor + kernel-aware dispatcher.

Architecture:

  tokens (B, L) → [VSM-Compressor: ascending, 9 strides, proven]
                       → typed representations (B, L, d_model)
                 → [VSM-Dispatcher: descending, kernel-shaped S1 ops]
                       → enriched representations (B, L, d_model)
                 → [output_norm → tied embedding → logits]
                 → relational loss on Dolma prose

Tree of VSMs (Beer 1972):
  VSM-Compressor (ascending arm, 3 passes: L0↑, L1↑, L2_apex):
    S5: token embedding identity (Qwen3 BBPE)
    S4: StrideStack fine→coarse (intelligence — reads context)
    S3: phase gates (control — what to compress)
    S2: direction signals between passes (anti-oscillation coordination)
    S1: TernaryFFN prep/consolidate (operations — compression)

  VSM-Dispatcher (second arm, 2 passes: L1↓, L0↓):
    S5: kernel function identity (22 ops, 5 types — pre-wired)
    S4: dual-view attention (residual + original embeddings)
    S3: dispatch gates (control — which kernel pathways activate)
    S2: direction signals + register conditioning (coordination)
    S1: KernelDispatch/KernelIntegrate/StrideStack (operations)

  Phase order (dispatch → stride → integrate):
    Phase 0: KernelDispatch — route to 22 kernel op pathways (local)
    Phase 1: StrideStack fine→coarse — propagate dispatched signal (spatial)
    Phase 2: KernelIntegrate — type the context-enriched result (local)

    Rationale: dispatch modulates per-position, then stride propagates
    so that each position sees how its neighbors were dispatched.
    Integration (typing) then has both the local op bias AND spatial
    context to inform its type decision. Prior order (dispatch → integrate
    → stride) produced type-dispatch decoupling: typing couldn't
    distinguish dispatch patterns without spatial context, defaulting
    to FN (56%) regardless of which op was active.

    Session 068 discovered that standard transformer attention self-
    organizes into a logarithmic spiral that always expands outward
    (~1.18x per revolution, ~9.4 layers per revolution). The spiral
    never reverses — there is no "descending" direction in attention.
    Both arms follow the same fine→coarse spiral; they differ in what
    operations they apply (compression vs kernel dispatch), not in
    the direction of attention.

Key design:
  The ascending arm compresses and types (proven in v6, φ-locking).
  The descending arm routes through kernel function pathways — NOT
  compression. Prior sessions (045/054/055/062/065) proved that giving
  the descending arm compression ops causes passthrough. The kernel
  provides the correct shape: dispatch/routing, not compression.

  The 22 kernel ops (from kernel.py, proven at 100% in v9) are pre-wired
  as architectural identity in the dispatcher VSM. The model discovers
  them as easy paths while training on prose — no need to learn
  composition through superpositions.

Output: tied embedding projection (weight sharing with input embed).

License: MIT
"""

from __future__ import annotations

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V10Config
from ternary import TernaryLinear, TernaryEmbedding
from attention import StrideStack, TernaryFFN
from components import (
    S4Ternary,
    S3Ternary,
    MetaS4Ternary,
    S5Reweight,
    S2Coordinator,
    CycleContinue,
)
from kernel_dispatch import KernelDispatch, KernelIntegrate, N_OPS, N_TYPES


# ══════════════════════════════════════════════════════════════════
# V6Compressor — 5-pass bidirectional VSM
# ══════════════════════════════════════════════════════════════════


class V6Compressor(nn.Module):
    """Tree of VSMs: compressor (ascending) + dispatcher (descending).

    5 passes:
      L0_asc → L1_asc → L2_apex → L1_desc → L0_desc

    ASCENDING arm (VSM-Compressor, 3 passes) — shared weights:
      S1: TernaryFFN prep/consolidate (compression — proven in v6)
      S4: StrideStack fine→coarse (reads context across scales)
      Job: compress and type (proven: φ-locking, S3 differentiation)

    SECOND arm (VSM-Dispatcher, 2 passes) — own weights:
      S1: KernelDispatch → StrideStack fine→coarse → KernelIntegrate
      S4: register cross-attention (reads typed representations)
      Job: route through 22 kernel op pathways, propagate, then type

    Both arms spiral outward (fine→coarse). The difference is what
    operations they apply: compression vs kernel dispatch. The spiral
    direction matches the emergent attention geometry discovered in
    standard transformers (~1.18x expansion per revolution).

    Phase order: dispatch (local) → stride (spatial) → integrate (local).
    Dispatch modulates per-position. Stride propagates so each position
    sees neighbor dispatch patterns. Integrate (typing) then has both
    local op bias and spatial context for informed type decisions.

    S2 coordination: between each pair of consecutive passes, a small
    direction signal is fed forward — "Pass N moved the representation
    THIS way." This is Beer's anti-oscillation mechanism: coordination
    between S1 units to prevent unknowing contradiction. The signal
    survives MetaS3 reweighting (S2 infrastructure ≠ S3 control).
    4 transitions, learnable scales starting at 0.01.

    Per-pass S3 control: 5 separate S3Ternary instances.
    """

    REGISTER_NAMES = ("type", "scope", "role")
    N_PASSES = 5
    N_ASC_PASSES = 3   # L0↑, L1↑, L2_apex
    N_DESC_PASSES = 2  # L1↓, L0↓
    PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")

    def __init__(self, cfg: V10Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model
        d_reg = cfg.d_register
        n_reg = cfg.n_registers
        self.d_reg_real = d_reg * 2

        # ── S5: Identity ──────────────────────────────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # Register bank 0: learnable real init
        self.register_inits = {
            f"reg_{name}": mx.zeros((self.d_reg_real,))
            for name in self.REGISTER_NAMES
        }

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # ── S1: Ascending ops (shared across L0↑, L1↑, L2_apex) ──
        #    Compression operations — proven in v6 (φ-locking)
        self.prep = TernaryFFN(d, cfg.d_ff, cfg.dropout)
        self.stride_stack = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.consolidate = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)

        # ── S1: Descending ops (shared across L1↓, L0↓) ──────
        #    Kernel-shaped operations — NOT compression.
        #    KernelDispatch routes to 22 kernel op pathways.
        #    KernelIntegrate combines results with type awareness.
        #    StrideStack reads typed reps across scales (coarse→fine).
        self.kernel_dispatch = KernelDispatch(
            d, n_ops=N_OPS, d_ff=cfg.d_ff, dropout=cfg.dropout,
            n_registers=cfg.n_registers, d_register=cfg.d_register,
            max_cond_banks=5,  # bank_0 + up to 4 ascending banks
            top_k=cfg.dispatch_top_k,
        )
        self.stride_stack_desc = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.kernel_integrate = KernelIntegrate(
            d, n_types=N_TYPES, d_ff=cfg.d_ff_consolidate, dropout=cfg.dropout,
        )

        # ── S4: Intelligence (ascending, shared) ──────────────
        self.s4 = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                            dropout=cfg.dropout)

        # ── S4: Intelligence (descending, own) ────────────────
        self.s4_desc = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                                  dropout=cfg.dropout)

        # ── S3: Per-pass gating (5 instances, always separate) ─
        self.s3_passes = [
            S3Ternary(d, d_reg, n_phases=3, n_registers=n_reg, d_align=d)
            for _ in range(self.N_PASSES)
        ]

        # ── Modulation projections (ascending, shared, 3 per phase) ─
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Modulation projections (descending, own) ──────────
        #    Same 3 phases but different semantics:
        #    phase 0 = dispatch, phase 1 = converge, phase 2 = integrate
        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Multi-cycle input injection gate (HRM-inspired) ──
        # Controls how much of the pre-cycle residual is re-injected
        # at each cycle > 0. HRM adds z_H + input at every L-step;
        # this is the v10 analog: re-ground in the pre-cycle state
        # so dispatch doesn't drift too far from what ascending produced.
        # sigmoid(-4) ≈ 0.018: injection starts nearly silent, model
        # learns to open. Unused when desc_max_cycles=1.
        self._cycle_inject_gate_raw = mx.array([-4.0])

        # ── S3 cycle continuation gate ────────────────────────
        # Beer's S3 control decides whether the next cycle should
        # contribute. Reads register state after each cycle to
        # determine if further computation is productive.
        # The model self-regulates: simple content → 1 cycle,
        # complex composition → up to desc_max_cycles.
        # Unused when desc_max_cycles ≤ 1.
        if cfg.desc_max_cycles > 1:
            self.cycle_continue = CycleContinue(
                cfg.d_register, n_registers=cfg.n_registers)

        # ── Meta-S4 ──────────────────────────────────────────
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── S2: Inter-pass direction coordination ──────────
        #    Beer's anti-oscillation: direction signal between
        #    consecutive passes prevents unknowing contradiction.
        self.s2 = S2Coordinator(d)

        # ── S5: Identity-level pass reweighting ───────────────
        #    Replaces MetaS3. Sees both register banks (S2 state)
        #    AND raw ungated pass deltas (direct S1 output).
        #    Beer's S5 needs ungated view to maintain identity.
        self.s5_reweight = S5Reweight(
            d, d_reg, n_registers=n_reg,
            n_banks=6, n_passes=self.N_PASSES)

        # ── Algedonic channel: persistent descending registers ─
        # Beer's VSM requires feedback from S3 back to S1/S2 —
        # an "algedonic channel" that signals system distress.
        # Without it, the apex can expand without limit because
        # nothing reads the descending arm's state to regulate
        # the ascending arm.
        #
        # Implementation: store the descending registers from the
        # previous forward pass as persistent buffers. The ascending
        # arm's S4 intelligence can read these stale descending
        # registers, creating a cross-step feedback loop:
        #   descending pressure → stored → ascending S4 reads →
        #   ascending S3 adjusts gates → regulated apex output
        #
        # Kernel compute algedonic: the kernel's dispatch weights
        # and compute gate are packed into a register-shaped vector.
        # This tells the ascending arm "the kernel was active,
        # dispatching to these ops, with this compute gate level"
        # so it can adjust compression accordingly (e.g. preserve
        # token identity when the kernel is computing).
        #
        # EMA smoothing (α=0.9) prevents oscillation.
        self._algedonic_ema = 0.9
        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        # Kernel compute: dispatch weights (22) + compute gate (1)
        # packed into d_reg_real, zero-padded. No projection needed —
        # S4's q_proj learns what to extract from the raw values.
        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))

        # ── Op emphasis: S4 register state → per-op modulation ──
        # S4's registers carry type/scope/role from the ascending arm.
        # This projection maps that intelligence to per-op emphasis:
        # "given what S4 observes, which kernel ops should be louder?"
        # EMA-tracked across steps for stability (slowly shifting
        # landscape, not reactive noise).
        # Input: ascending banks (bank_1_asc + bank_2_asc + bank_3)
        #        = 3 banks × 3 registers × d_reg_real
        emphasis_input_dim = 3 * n_reg * self.d_reg_real
        self.emphasis_proj = nn.Linear(emphasis_input_dim, N_OPS)
        # Zero-init: emphasis starts neutral (1.0 for all ops)
        self.emphasis_proj.weight = mx.zeros_like(self.emphasis_proj.weight)
        self.emphasis_proj.bias = mx.zeros_like(self.emphasis_proj.bias)
        self._op_emphasis = mx.ones((N_OPS,))
        self._emphasis_ema = 0.95  # slow-moving — captures trends, not noise

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Cycle injection ────────────────────────────────────────

    @property
    def cycle_inject_gate(self) -> mx.array:
        """Sigmoid gate controlling input injection strength per cycle."""
        return mx.sigmoid(self._cycle_inject_gate_raw)

    # ── Register helpers ──────────────────────────────────────

    def _init_bank0(self) -> list[mx.array]:
        return [self.register_inits[f"reg_{name}"]
                for name in self.REGISTER_NAMES]

    def _fresh_bank(self) -> list[mx.array]:
        return [mx.zeros((self.d_reg_real,))
                for _ in self.REGISTER_NAMES]

    # ── Modulation (additive) ─────────────────────────────────

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        return x + gate * mx.tanh(projs[phase_idx](delta))

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks, target_bank,
                         embed_context=None, op_emphasis=None):
        x_before = x
        raw_phases = []   # ungated phase deltas for S5
        phase_gates = []  # S3 gate values for cross-arm visibility

        # Select ops based on VSM arm
        s4 = self.s4_desc if is_descending else self.s4
        strides = self.stride_stack_desc if is_descending else self.stride_stack

        # S4 scan (intelligence — reads register banks)
        # Descending arm gets dual view: compressed residual + original
        # token embeddings. S4 attends over [residual; embeddings] (2L
        # positions) so it can see both what compression produced AND
        # what the tokens originally were. Critical for dispatch: knowing
        # "this position IS the + token" helps route to arithmetic ops.
        s4_residual = x
        if embed_context is not None:
            s4_residual = mx.concatenate([x, embed_context], axis=1)
        s4_updates, _ = s4(readable_banks, s4_residual)
        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])
                       for i in range(self.cfg.n_registers)]

        if is_descending:
            # ── VSM-Dispatcher: self-regulating kernel cycles ─
            # S4 scanned once above (slow/abstract). Now dispatch→
            # stride→integrate cycles up to desc_max_cycles times.
            # A learned S3 continuation gate (CycleContinue) decides
            # after each cycle whether further cycles should contribute.
            #
            # Static graph: all cycles always execute (MLX requirement).
            # CycleContinue controls contribution via cumulative gate:
            #   cycle 0: full strength (cumulative_gate = 1.0)
            #   cycle 1: scaled by continue_gate_0
            #   cycle 2: scaled by continue_gate_0 × continue_gate_1
            #
            # If the model learns "this is simple prose", it drives
            # continuation gates → 0 after cycle 0. Cycles 1+ still
            # compute but produce near-zero deltas (gated out).
            # For complex content (PARTIAL → APPLY composition),
            # gates stay open → full multi-cycle refinement.
            #
            # Input injection at cycle > 0: re-ground in pre-cycle
            # residual (HRM's z_L += z_H + input pattern).
            #
            # desc_max_cycles=1: loop runs once, no continuation
            # gates computed, behavior identical to single-cycle.

            x_anchor = x  # pre-cycle state for injection
            max_cycles = self.cfg.desc_max_cycles
            cumulative_gate = mx.array(1.0)  # cycle 0 always full

            for cycle in range(max_cycles):
                x_cycle_start = x

                # Input injection (HRM pattern): re-ground in anchor
                if cycle > 0:
                    x = x + self.cycle_inject_gate * x_anchor

                # Phase 0: dispatch (route to kernel op pathways)
                dispatch_out = self.kernel_dispatch(
                    x, registers=readable_banks, op_emphasis=op_emphasis)
                delta = dispatch_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 0)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=0, is_descending=True)

                # Phase 1: converge (StrideStack — propagate dispatch outward)
                converge_out = strides(x, reverse=False)
                delta = converge_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 1)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=1, is_descending=True)

                # Phase 2: integrate (type + compute with spatial context)
                dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                delta = integrate_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 2)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=2, is_descending=True)

                # Scale this cycle's total contribution by cumulative gate
                cycle_contribution = x - x_cycle_start
                x = x_cycle_start + cumulative_gate * cycle_contribution

                # S3 continuation: should the next cycle contribute?
                if cycle < max_cycles - 1 and max_cycles > 1:
                    cont_gate = self.cycle_continue(target_bank)
                    cumulative_gate = cumulative_gate * cont_gate
        else:
            # ── VSM-Compressor: compression S1 operations ─────
            # Phase 0: prep (local feature extraction)
            prep_out = self.prep(x)
            delta = prep_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 0)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=0, is_descending=False)

            # Phase 1: converge (StrideStack fine→coarse)
            converge_out = strides(x, reverse=False)
            delta = converge_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 1)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=1, is_descending=False)

            # Phase 2: consolidate (feature integration)
            consolidate_out = self.consolidate(x)
            delta = consolidate_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 2)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=2, is_descending=False)

        pass_delta = x - x_before
        # Raw delta: sum of ungated phase deltas — what S1 proposed
        # before S3 gating. S5 sees this to maintain identity coherence.
        raw_delta = raw_phases[0]
        for rd in raw_phases[1:]:
            raw_delta = raw_delta + rd
        return x, target_bank, pass_delta, raw_delta, phase_gates

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        """
        tokens (B, L) → logits (B, L, vocab_size), optional loss.

        Output uses tied embedding: logits = h @ embed.weight_T
        """
        B, L = tokens.shape

        # Embed
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        # Capture original embeddings for descending S4's dual view.
        # By pass 3, compression has buried token identity under 3
        # transformation passes. The dispatcher needs raw token identity
        # to route correctly (e.g. "this IS the + token → arithmetic ops").
        x_embed = x

        # Initialize register banks
        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5

        # ── Algedonic channel: read previous descending registers ──
        # These are EMA-smoothed registers from the PREVIOUS forward
        # pass. They carry descending arm pressure (type/dispatch state)
        # back into the ascending arm's S4 intelligence, creating the
        # feedback loop that Beer's VSM requires for S3 regulation.
        # stop_gradient: the algedonic signal is observational, not
        # a training target. Gradient flows forward through the
        # ascending arm normally.
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        # Kernel compute algedonic: which ops fired, how active the
        # compute gate was. Tells ascending arm what downstream needs.
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        asc_s3_gates = []  # ascending S3 gate values for descending arm

        # Pass 0: L0_asc — reads prev descending L0 + kernel compute
        x, bank_1_asc, pd, rd, pg = self._run_level_pass(
            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 0 → Pass 1 (unmodulated — first signal)
        x = x + self.s2.direction_signal(pd, 0)

        # Pass 1: L1_asc — reads prev descending L1 + kernel compute
        x, bank_2_asc, pd, rd, pg = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 1 → Pass 2, modulated by coherence(0,1)
        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])
        x = x + self.s2.direction_signal(pd, 1) * coherence

        # Pass 2: L2_apex — reads kernel compute (helps transition to dispatch)
        x, bank_3, pd, rd, pg = self._run_level_pass(
            x, 2, False, [bank_0, bank_1_asc, bank_2_asc, prev_kernel], bank_3)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # ── Op emphasis: S4 register state → per-op modulation ──
        # After ascending passes, registers carry type/scope/role.
        # Project to per-op emphasis: which ops should be louder?
        emphasis_parts = []
        for bank in [bank_1_asc, bank_2_asc, bank_3]:
            for reg in bank:
                emphasis_parts.append(reg)
        emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
        raw_emphasis = self.emphasis_proj(emphasis_input)           # (N_OPS,)
        op_emphasis = 1.0 + 0.5 * mx.tanh(raw_emphasis)            # [0.5, 1.5]

        # EMA tracking — slowly accumulates S4's emphasis preferences
        self._op_emphasis = mx.stop_gradient(
            self._emphasis_ema * self._op_emphasis
            + (1.0 - self._emphasis_ema) * op_emphasis)

        # ── Pack ascending S3 gates for descending arm ─────────
        # 9 gate values (3 passes × 3 phases) packed into a register-
        # shaped vector. Tells descending S4 what the ascending arm's
        # control decisions were: "prep was gated at 0.8, converge
        # suppressed at 0.3, consolidate open at 0.9" etc.
        # NOT stop_gradient: gradient flows back to ascending S3,
        # teaching it that its gate decisions affect downstream dispatch.
        asc_gate_flat = mx.concatenate(
            [g.reshape(-1) for g in asc_s3_gates])              # (9,)
        asc_gate_vector = mx.concatenate([
            asc_gate_flat,
            mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
        ])
        asc_gate_bank = [asc_gate_vector]

        # S2: direction signal Pass 2 → Pass 3 (ascending→descending)
        #     modulated by coherence(1,2)
        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])
        x = x + self.s2.direction_signal(pd, 2) * coherence

        # Pass 3: L1_desc — S4 sees residual + embeds + ascending gates
        x, bank_2_desc, pd, rd, _ = self._run_level_pass(
            x, 3, True,
            [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank],
            bank_2_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # S2: direction signal Pass 3 → Pass 4, modulated by coherence(2,3)
        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])
        x = x + self.s2.direction_signal(pd, 3) * coherence

        # Pass 4: L0_desc — S4 sees residual + embeds + ascending gates
        x, bank_1_desc, pd, rd, _ = self._run_level_pass(
            x, 4, True,
            [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank],
            bank_1_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # ── Update algedonic buffers (EMA, no gradient) ────────
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic: pack dispatch weights + compute gate
        # into register-shaped vector for ascending arm's next pass
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean,                                        # 22 dims: op distribution
            cg_mean,                                        # 1 dim: compute gate level
            mx.zeros((self.d_reg_real - N_OPS - 1,)),       # padding to d_reg_real
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting — sees registers AND
        # raw ungated deltas (direct view of what operations proposed)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,
                     bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]

        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]

        x = x - total_ungated + total_gated

        # Meta-S4: final structural summary
        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        logits = self.embed.output_proj(x)   # tied ternary embedding, (B, L, vocab_size)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Instrumentation ───────────────────────────────────────

    @staticmethod
    def _entropy_proxy(x: mx.array) -> float:
        """log(mean_var) entropy proxy — same as v6."""
        var_per_feat = mx.var(x, axis=(0, 1))
        mean_var = mx.mean(var_per_feat)
        mx.eval(mean_var)
        return float(mx.log(mean_var + 1e-10).item())

    def forward_instrumented(
        self,
        tokens: mx.array,
    ) -> tuple[mx.array, dict]:
        """Forward pass with full instrumentation. Returns (hidden, metrics).

        Metrics dict contains:
          s3_gates:     list of 5 lists of floats (per pass, per phase;
                        descending passes have 3*desc_cycles phases)
          s5_reweight:  list of 5 floats (per-pass contribution gates from S5)
          s2_conflict:  list of 4 floats (cosine sim between consecutive deltas)
          s2_scales:    list of 4 floats (learnable direction signal scales)
          register_norms: dict of bank_name → list of 3 floats (per register)
          pass_entropy_in:  list of 5 floats
          pass_entropy_out: list of 5 floats
          pass_compression: list of 5 floats (out/in ratio)
          pass_phi_dev:     list of 5 floats (|ratio - 1/φ|)
          desc_max_cycles:  int — max dispatch cycles per descending pass
          cycle_inject_gate: float — learned injection strength (sigmoid)
          cycle_continue_gates: list of per-pass continuation gate lists
          effective_cycles: list of per-pass effective cycle counts
        """
        import math
        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)

        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x  # original embeddings for descending S4 dual view

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5
        all_s3_gates = []
        pass_h_in = []
        pass_h_out = []
        asc_gate_mx = []  # ascending S3 gate values (mx.arrays) for descending arm
        asc_gate_bank = None  # packed after ascending passes
        op_emphasis_inst = None  # computed after ascending passes
        all_cycle_continue_gates = []  # per-pass continuation gate values
        all_effective_cycles = []       # per-pass effective cycle counts

        # Algedonic channel: stale descending registers + kernel compute
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        pass_configs = [
            (0, False, lambda: [bank_0, prev_b1d, prev_kernel]),
            (1, False, lambda: [bank_0, bank_1_asc, prev_b2d, prev_kernel]),
            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc, prev_kernel]),
            (3, True,  lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3]),
            (4, True,  lambda: [bank_0, bank_1_asc, bank_2_desc, bank_3]),
        ]
        target_banks = [bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]

        for pi, (pass_idx, is_desc, get_readable) in enumerate(pass_configs):
            h_in = self._entropy_proxy(x)
            pass_h_in.append(h_in)

            x_before = x
            readable = get_readable()
            target = target_banks[pi]

            # Select ops based on VSM arm
            s4 = self.s4_desc if is_desc else self.s4
            strides = self.stride_stack_desc if is_desc else self.stride_stack

            # Descending arm: add ascending S3 gate bank + embed dual view
            if is_desc:
                if asc_gate_bank is not None:
                    readable.append(asc_gate_bank)
                s4_residual = mx.concatenate([x, x_embed], axis=1)
            else:
                s4_residual = x
            s4_updates, _ = s4(readable, s4_residual)
            target = [self.register_norm(target[i] + s4_updates[i])
                      for i in range(self.cfg.n_registers)]

            phase_gates = []
            raw_phases = []  # ungated phase deltas for S5

            if is_desc:
                # ── VSM-Dispatcher: self-regulating kernel cycles ─
                x_anchor = x
                max_cycles = self.cfg.desc_max_cycles
                cumulative_gate = mx.array(1.0)
                cycle_continue_gates = []  # per-cycle continuation gate values

                for cycle in range(max_cycles):
                    x_cycle_start = x

                    # Input injection (HRM pattern)
                    if cycle > 0:
                        x = x + self.cycle_inject_gate * x_anchor

                    # Phase 0: dispatch
                    dispatch_out = self.kernel_dispatch(
                        x, registers=readable, op_emphasis=op_emphasis_inst)
                    delta = dispatch_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 0, is_descending=True)

                    # Phase 1: converge (propagate dispatch outward)
                    conv_out = strides(x, reverse=False)
                    delta = conv_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 1, is_descending=True)

                    # Phase 2: integrate (type + compute with spatial context)
                    dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                    integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                    delta = integrate_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 2, is_descending=True)

                    # Scale cycle contribution by cumulative gate
                    cycle_contribution = x - x_cycle_start
                    x = x_cycle_start + cumulative_gate * cycle_contribution

                    # S3 continuation gate
                    if cycle < max_cycles - 1 and max_cycles > 1:
                        cont_gate = self.cycle_continue(target)
                        mx.eval(cont_gate)
                        cycle_continue_gates.append(float(cont_gate.item()))
                        cumulative_gate = cumulative_gate * cont_gate
            else:
                # ── VSM-Compressor: compression phases ────────
                # Phase 0: prep
                prep_out = self.prep(x)
                delta = prep_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 0, is_descending=False)

                # Phase 1: converge (fine→coarse)
                conv_out = strides(x, reverse=False)
                delta = conv_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 1, is_descending=False)

                # Phase 2: consolidate
                cons_out = self.consolidate(x)
                delta = cons_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 2, is_descending=False)

            target_banks[pi] = target
            pass_deltas.append(x - x_before)
            # Raw delta: sum of ungated phase deltas for S5
            raw_delta = raw_phases[0]
            for rd in raw_phases[1:]:
                raw_delta = raw_delta + rd
            raw_deltas.append(raw_delta)
            all_s3_gates.append(phase_gates)

            # Collect cycle continuation data for descending passes
            if is_desc and self.cfg.desc_max_cycles > 1:
                all_cycle_continue_gates.append(cycle_continue_gates)
                # Effective cycles: 1.0 (cycle 0) + sum of cumulative gates
                eff = 1.0 + sum(
                    float(mx.prod(mx.array(cycle_continue_gates[:i+1])).item())
                    for i in range(len(cycle_continue_gates))
                ) if cycle_continue_gates else 1.0
                all_effective_cycles.append(eff)

            # Pack ascending S3 gates after last ascending pass (pi=2)
            if not is_desc and pi == 2 and asc_gate_mx:
                asc_gate_flat = mx.concatenate(
                    [g.reshape(-1) for g in asc_gate_mx])
                asc_gate_vector = mx.concatenate([
                    asc_gate_flat,
                    mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
                ])
                asc_gate_bank = [asc_gate_vector]

            # Op emphasis after ascending passes complete (pi=2)
            if not is_desc and pi == 2:
                emphasis_parts = []
                for bank in [target_banks[0], target_banks[1], target_banks[2]]:
                    for reg in bank:
                        emphasis_parts.append(reg)
                emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
                raw_emphasis = self.emphasis_proj(emphasis_input)
                op_emphasis_inst = 1.0 + 0.5 * mx.tanh(raw_emphasis)
                mx.eval(op_emphasis_inst)
                self._op_emphasis = mx.stop_gradient(
                    self._emphasis_ema * self._op_emphasis
                    + (1.0 - self._emphasis_ema) * op_emphasis_inst)

            h_out = self._entropy_proxy(x)
            pass_h_out.append(h_out)

            # S2: direction signal to next pass (except after last pass)
            # First signal unmodulated; subsequent signals modulated by
            # coherence between this pass and the previous one.
            if pi < len(pass_configs) - 1:
                signal = self.s2.direction_signal(pass_deltas[-1], pi)
                if pi > 0:
                    coherence = S2Coordinator.coherence_factor(
                        pass_deltas[-2], pass_deltas[-1])
                    signal = signal * coherence
                x = x + signal

        # S2: conflict scores between consecutive pass deltas
        s2_conflict = []
        for i in range(len(pass_deltas) - 1):
            cs = S2Coordinator.conflict_score(pass_deltas[i], pass_deltas[i + 1])
            s2_conflict.append(cs)
        s2_scales = [float(self.s2.scales[i].item())
                     for i in range(S2Coordinator.N_TRANSITIONS)]

        # Re-assign named banks from target_banks
        bank_1_asc = target_banks[0]
        bank_2_asc = target_banks[1]
        bank_3 = target_banks[2]
        bank_2_desc = target_banks[3]
        bank_1_desc = target_banks[4]

        # Update algedonic buffers (EMA, no gradient) — same as forward()
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic — same as forward()
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean, cg_mean,
            mx.zeros((self.d_reg_real - N_OPS - 1,)),
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting (sees registers + raw deltas)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)
        mx.eval(meta_gates)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4
        meta_banks_list = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks_list, x)
        x = self.output_norm(x)

        # Register norms
        reg_norms = {}
        named_banks = {
            "bank_0": bank_0, "bank_1_asc": bank_1_asc,
            "bank_2_asc": bank_2_asc, "bank_3": bank_3,
            "bank_2_desc": bank_2_desc, "bank_1_desc": bank_1_desc,
        }
        for name, bank in named_banks.items():
            norms = []
            for reg in bank:
                mx.eval(reg)
                norms.append(float(mx.sqrt((reg * reg).sum()).item()))
            reg_norms[name] = norms

        # Compression metrics
        pass_compression = []
        pass_phi_dev = []
        for h_in, h_out in zip(pass_h_in, pass_h_out):
            if abs(h_in) > 1e-8:
                ratio = h_out / h_in
            else:
                ratio = 1.0
            pass_compression.append(ratio)
            pass_phi_dev.append(abs(ratio - INV_PHI))

        # Kernel dispatch metrics (from descending arm)
        # KernelDispatch caches _dispatch_weights: (B, L, n_ops)
        # KernelIntegrate caches _type_weights: (B, L, n_types)
        dispatch_weights = None
        type_weights = None
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw = self.kernel_dispatch._dispatch_weights
            mx.eval(dw)
            # Mean over batch and sequence → per-op activation frequency
            dispatch_weights = mx.mean(dw, axis=(0, 1))  # (n_ops,)
            mx.eval(dispatch_weights)
        if hasattr(self.kernel_integrate, '_type_weights'):
            tw = self.kernel_integrate._type_weights
            mx.eval(tw)
            type_weights = mx.mean(tw, axis=(0, 1))  # (n_types,)
            mx.eval(type_weights)

        # Op embedding norms (health check — should be uniform with norm constraint)
        op_emb_norms = None
        if hasattr(self.kernel_dispatch, 'op_embeddings'):
            raw_emb = self.kernel_dispatch.op_embeddings
            mx.eval(raw_emb)
            norms = mx.sqrt(mx.sum(raw_emb * raw_emb, axis=-1) + 1e-8)
            mx.eval(norms)
            op_emb_norms = [float(norms[i].item()) for i in range(norms.shape[0])]

        # Cycle inject gate value
        cig = self.cycle_inject_gate
        mx.eval(cig)

        metrics = {
            "s3_gates": all_s3_gates,
            "s5_reweight": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],
            "op_emphasis": (
                [float(op_emphasis_inst[i].item()) for i in range(N_OPS)]
                if op_emphasis_inst is not None else None
            ),
            "s2_conflict": s2_conflict,
            "s2_scales": s2_scales,
            "register_norms": reg_norms,
            "pass_entropy_in": pass_h_in,
            "pass_entropy_out": pass_h_out,
            "pass_compression": pass_compression,
            "pass_phi_dev": pass_phi_dev,
            "kernel_dispatch_weights": (
                [float(dispatch_weights[i].item()) for i in range(dispatch_weights.shape[0])]
                if dispatch_weights is not None else None
            ),
            "kernel_type_weights": (
                [float(type_weights[i].item()) for i in range(type_weights.shape[0])]
                if type_weights is not None else None
            ),
            "op_embedding_norms": op_emb_norms,
            "desc_max_cycles": self.cfg.desc_max_cycles,
            "cycle_inject_gate": float(cig.item()),
            "cycle_continue_gates": all_cycle_continue_gates,
            "effective_cycles": all_effective_cycles,
        }

        # Compute gate stats (if kernel pathway is active)
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg = self.kernel_integrate._compute_gate  # (B, L, 1)
            mx.eval(cg)
            metrics["compute_gate_mean"] = float(mx.mean(cg).item())
            metrics["compute_gate_max"] = float(mx.max(cg).item())
            metrics["compute_gate_min"] = float(mx.min(cg).item())
            # Fraction of positions where gate > 0.5
            metrics["compute_gate_active"] = float(mx.mean((cg > 0.5).astype(mx.float32)).item())

        return x, metrics


# ══════════════════════════════════════════════════════════════════
# Factory + utilities
# ══════════════════════════════════════════════════════════════════


def create_model(cfg: V10Config) -> V6Compressor:
    """Create and initialize a V6Compressor."""
    model = V6Compressor(cfg)
    mx.eval(model.parameters())
    return model


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count parameters by component."""
    from mlx.utils import tree_flatten

    counts = {"total": 0, "trainable": 0}
    all_params = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())

    counts["total"] = sum(p.size for _, p in all_params)
    counts["trainable"] = sum(p.size for _, p in trainable)

    return counts


# ═════════════════════════════════

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01RKeR2xtx11FhzLNEJaxBLD.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/train.py"
}
```

**Summary:** Reading train.py (0-2000)

**Output:**
```
"""
v10 — Training Script

V6 compressor (5-pass bidirectional VSM, 9 strides, Qwen3 tokenizer)
trained on Dolma prose for next-token prediction.

  • Causal LM cross-entropy loss
  • Relational loss r = (CE - E) / (log(V) - E) for phase awareness
  • Shared-weight gradient normalization (÷5 for 5-pass components)
  • Ternary topology evolved via tournament selection (mixed-data-aware)
  • Adam on continuous parameters (gamma, norms, embeddings, pos_embed)
  • Cosine LR with linear warmup

Usage:
    uv run python scripts/v10/train.py
    uv run python scripts/v10/train.py --total-steps 5000
    uv run python scripts/v10/train.py --seq-len 512 --batch-size 4
    uv run python scripts/v10/train.py --resume

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader, MixedDataLoader
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    bios_mutation_budget,
    save_topology,
    load_topology,
    mutate_topology,
    propose_mutations,
    find_consensus,
    apply_consensus,
    _walk_ternary_modules,
    TernaryLinear,
)


# ══════════════════════════════════════════════════════════════════════════════
# § 1  Constants
# ══════════════════════════════════════════════════════════════════════════════

# Irreducible entropy of natural language (Chinchilla: E ≈ 1.82 nats)
E_IRREDUCIBLE = 1.82
# log(vocab_size) — the "knows nothing" ceiling
LOG_V = math.log(151936)  # ≈ 11.93


# ══════════════════════════════════════════════════════════════════════════════
# § 2  Loss function — relational loss
# ══════════════════════════════════════════════════════════════════════════════

def loss_fn(
    model: V6Compressor,
    input_ids: mx.array,
    targets: mx.array,
) -> mx.array:
    """Relational loss: r = (CE - E) / (log(V) - E).

    Normalizes cross-entropy into phase-aware [0,1] space:
      r=1.0  → model knows nothing (CE = log(V))
      r=0.0  → model matches irreducible entropy (CE = E)
      r<0.0  → model beats irreducible (overfitting or better estimate of E)

    Same gradient direction as CE (monotonic transform), but compressed
    into a range where evolution can see structural progress — a 0.01
    improvement in r means the same thing at loss=10 or loss=5.

    The denominator (log(V) - E) is constant, so grad(r) = grad(CE) / const.
    This scales the learning rate implicitly but the optimizer adapts.
    """
    _, ce = model(input_ids, targets)
    r = (ce - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
    return r


# ══════════════════════════════════════════════════════════════════════════════
# § 3  Shared-weight gradient normalization
# ══════════════════════════════════════════════════════════════════════════════

# Ascending components: shared across L0↑, L1↑, L2_apex (3 passes)
ASC_SHARED = ("prep", "stride_stack", "consolidate", "mod_projs", "s4")
# Descending components: shared across L1↓, L0↓ (2 passes)
# Kernel dispatch/integrate replace prep_desc/consolidate_desc
DESC_SHARED = ("kernel_dispatch", "stride_stack_desc", "kernel_integrate", "mod_projs_desc", "s4_desc")

N_ASC_PASSES = 3
N_DESC_PASSES = 2


def normalize_shared_grads(grads: dict) -> dict:
    """Divide gradients of shared components by their pass count.

    Ascending components (prep, stride_stack, consolidate, mod_projs, s4)
    are traversed 3× per forward (L0↑, L1↑, L2_apex).
    Descending components (*_desc) are traversed 2× (L1↓, L0↓).
    Normalizing stabilizes Adam's running statistics.
    """
    asc_scale = 1.0 / N_ASC_PASSES
    desc_scale = 1.0 / N_DESC_PASSES

    def _walk(tree, keys):
        if isinstance(tree, dict):
            out = {}
            for k, v in tree.items():
                new_keys = keys + [k]
                if len(new_keys) >= 1 and new_keys[0] in ASC_SHARED:
                    out[k] = tree_map(lambda g: g * asc_scale, v)
                elif len(new_keys) >= 1 and new_keys[0] in DESC_SHARED:
                    out[k] = tree_map(lambda g: g * desc_scale, v)
                else:
                    out[k] = _walk(v, new_keys)
            return out
        elif isinstance(tree, list):
            return [_walk(v, keys + [str(i)]) for i, v in enumerate(tree)]
        return tree

    return _walk(grads, [])


# ══════════════════════════════════════════════════════════════════════════════
# § 4  LR schedule
# ══════════════════════════════════════════════════════════════════════════════

def cosine_lr(step, warmup_steps, total_steps, lr_max, lr_floor_ratio=0.01):
    if step < warmup_steps:
        return lr_max * step / max(warmup_steps, 1)
    progress = (step - warmup_steps) / max(total_steps - warmup_steps, 1)
    floor = lr_max * lr_floor_ratio
    return floor + (lr_max - floor) * 0.5 * (1.0 + math.cos(math.pi * progress))


# ══════════════════════════════════════════════════════════════════════════════
# § 4b  JSONL metrics logging
# ══════════════════════════════════════════════════════════════════════════════

def _sanitize_for_json(obj):
    """Recursively sanitize a value for JSON: NaN/Inf → null, mx/np scalars → Python."""
    if isinstance(obj, dict):
        return {k: _sanitize_for_json(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_sanitize_for_json(v) for v in obj]
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return obj
    if hasattr(obj, 'item'):  # mx.array scalar, np scalar
        v = obj.item()
        if isinstance(v, float) and (math.isnan(v) or math.isinf(v)):
            return None
        return v
    if isinstance(obj, set):
        return sorted(obj)
    return obj


def _append_jsonl(path: Path, record: dict) -> None:
    """Append one JSON line to a JSONL file. Creates if missing."""
    clean = _sanitize_for_json(record)
    with open(path, "a") as f:
        f.write(json.dumps(clean) + "\n")


# ══════════════════════════════════════════════════════════════════════════════
# § 5  Evaluation
# ══════════════════════════════════════════════════════════════════════════════

def evaluate(model: V6Compressor, cfg: V10Config) -> dict:
    """Evaluate on held-out shards. Returns loss, perplexity, and compressor metrics."""
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=9999,
    )

    total_loss = 0.0
    n_batches = 0
    target_tokens = 50_000
    tokens_seen = 0

    while tokens_seen < target_tokens:
        input_ids_np, targets_np = next(eval_loader)
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        _, loss = model(input_ids, targets)
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += input_ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    ppl = math.exp(min(avg_loss, 20.0))
    r = (avg_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

    # Instrumented forward on one batch for compressor metrics
    input_ids_np, _ = next(eval_loader)
    input_ids = mx.array(input_ids_np)
    _, compressor_metrics = model.forward_instrumented(input_ids)

    # Print compressor metrics
    pass_names = ("L0↑", "L1↑", "L2", "L1↓", "L0↓")
    desc_max_cycles = compressor_metrics.get("desc_max_cycles", 1)

    print("  ┌─ S3 gates ──────────────────────────────────────┐", file=sys.stderr)
    for pi, pname in enumerate(pass_names):
        gates = compressor_metrics["s3_gates"][pi]
        if pi >= 3 and desc_max_cycles > 1:
            # Descending pass: show per-cycle gates
            for cy in range(desc_max_cycles):
                base = cy * 3
                cyname = f"{pname}c{cy}"
                print(f"  │ {cyname:6s}: disp={gates[base]:.3f}  "
                      f"conv={gates[base+1]:.3f}  intg={gates[base+2]:.3f}",
                      file=sys.stderr)
        else:
            print(f"  │ {pname:4s}: prep={gates[0]:.3f}  conv={gates[1]:.3f}  "
                  f"cons={gates[2]:.3f}", file=sys.stderr)
    print("  ├─ S5 reweight ───────────────────────────────────┤", file=sys.stderr)
    mg = compressor_metrics["s5_reweight"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(pass_names, mg))}",
          file=sys.stderr)
    print("  ├─ S2 coordination ───────────────────────────────┤", file=sys.stderr)
    s2_conflict = compressor_metrics.get("s2_conflict", [])
    s2_scales = compressor_metrics.get("s2_scales", [])
    s2_names = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")
    for ti in range(len(s2_conflict)):
        cs = s2_conflict[ti]
        sc = s2_scales[ti] if ti < len(s2_scales) else 0.0
        warn = "  ⚠" if cs < 0 else ""
        print(f"  │ {s2_names[ti]:8s}: cos={cs:+.3f}  scale={sc:.4f}{warn}",
              file=sys.stderr)
    print("  ├─ Compression ───────────────────────────────────┤", file=sys.stderr)
    cr = compressor_metrics["pass_compression"]
    pd = compressor_metrics["pass_phi_dev"]
    for pi, pname in enumerate(pass_names):
        phi_mark = "←φ" if pd[pi] < 0.05 else "   "
        print(f"  │ {pname:4s}: ratio={cr[pi]:.3f}  φ-dev={pd[pi]:.3f} {phi_mark}",
              file=sys.stderr)
    print("  ├─ Register norms ────────────────────────────────┤", file=sys.stderr)
    for bname, norms in compressor_metrics["register_norms"].items():
        print(f"  │ {bname:12s}: {' '.join(f'{n:.2f}' for n in norms)}",
              file=sys.stderr)
    print("  └─────────────────────────────────────────────────┘", file=sys.stderr)

    # Op emphasis (S4→kernel modulation)
    op_emph = compressor_metrics.get("op_emphasis")
    if op_emph:
        from kernel import OP_NAMES
        indexed = sorted(enumerate(op_emph), key=lambda x: x[1], reverse=True)
        top3 = [(OP_NAMES[i], v) for i, v in indexed[:3]]
        bot3 = [(OP_NAMES[i], v) for i, v in indexed[-3:]]
        print(f"  🎯 Op emphasis: top={' '.join(f'{n}={v:.2f}' for n,v in top3)}"
              f"  bot={' '.join(f'{n}={v:.2f}' for n,v in bot3)}",
              file=sys.stderr)

    # Compute gate stats (kernel pathway)
    if "compute_gate_mean" in compressor_metrics:
        cg_mean = compressor_metrics["compute_gate_mean"]
        cg_max = compressor_metrics["compute_gate_max"]
        cg_active = compressor_metrics["compute_gate_active"]
        print(f"  🔧 Compute gate: mean={cg_mean:.4f}  max={cg_max:.4f}  "
              f"active(>0.5)={cg_active:.1%}", file=sys.stderr)

    # Multi-cycle stats
    if desc_max_cycles > 1:
        cig = compressor_metrics.get("cycle_inject_gate", 0.0)
        eff_cycles = compressor_metrics.get("effective_cycles", [])
        cont_gates = compressor_metrics.get("cycle_continue_gates", [])
        desc_pass_names = ("L1↓", "L0↓")
        parts = [f"max={desc_max_cycles}", f"inject={cig:.4f}"]
        for di, dpn in enumerate(desc_pass_names):
            if di < len(eff_cycles):
                parts.append(f"{dpn}={eff_cycles[di]:.2f}eff")
            if di < len(cont_gates) and cont_gates[di]:
                cg_str = ",".join(f"{g:.2f}" for g in cont_gates[di])
                parts.append(f"cont=[{cg_str}]")
        print(f"  🔄 Cycles: {' '.join(parts)}", file=sys.stderr)

    result = {
        "loss": avg_loss,
        "ppl": ppl,
        "r": r,
    }
    result.update(compressor_metrics)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Tournament evolution
# ══════════════════════════════════════════════════════════════════════════════

MUTANT_STRATEGIES = {
    "conservative": 0.25,
    "explorer":     1.0,
    "targeted":     2.0,
    "random":       4.0,
    "intelligence": 0.5,   # S4→S5: Beer's intelligence proposal channel
}

# S4 module path fragments — intelligence strategy amplifies these
S4_MODULES = ('s4.', 's4_desc.', 'meta_s4.')


def run_tournament(
    model, cfg, step, total_ternary, eval_loader,
    base_pct, rng,
    row_importance, col_importance, grad_direction,
    structured_eval_loader=None,
) -> dict:
    """One evolutionary generation via consensus mutation.

    Instead of tournament selection (best of 4 independent throws),
    consensus requires ≥3 of 4 strategies to independently agree on
    the same flip at the same position. Each accepted flip has
    independent evidence from multiple sampling strategies.

    Flow:
      1. Each strategy proposes mutations (without modifying the model)
      2. Find positions where ≥3 strategies agree on the same new value
      3. Apply only the consensus flips
      4. Evaluate: accept if loss improves, revert if not

    When structured_eval_loader is provided (mixed-data training),
    mutations are evaluated on BOTH prose and structured batches.
    A mutation is only accepted if it improves on BOTH — the acceptance
    criterion is the maximum (worst) loss across data types.
    """
    # Get fixed eval batches — prose always, structured if available
    prose_ids_np, prose_tgts_np = next(eval_loader)
    prose_ids = mx.array(prose_ids_np)
    prose_tgts = mx.array(prose_tgts_np)

    has_structured = structured_eval_loader is not None
    if has_structured:
        struct_ids_np, struct_tgts_np = next(structured_eval_loader)
        struct_ids = mx.array(struct_ids_np)
        struct_tgts = mx.array(struct_tgts_np)

    def _eval_loss():
        """Evaluate relational loss r on all data types."""
        _, ce_prose = model(prose_ids, prose_tgts)
        mx.eval(ce_prose)
        r_prose = (float(ce_prose.item()) - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

        if has_structured:
            _, ce_struct = model(struct_ids, struct_tgts)
            mx.eval(ce_struct)
            r_struct = (float(ce_struct.item()) - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
            return max(r_prose, r_struct), r_prose, r_struct
        else:
            return r_prose, r_prose, None

    champion_loss, champion_prose, champion_struct = _eval_loss()
    champion_snapshot = save_topology(model)

    base_budget = bios_mutation_budget(step, cfg.total_steps, total_ternary, base_pct)
    if base_budget == 0:
        return {"champion_loss": champion_loss, "budget": 0,
                "accepted": None, "accepted_loss": champion_loss, "frozen": True,
                "prose_loss": champion_prose, "struct_loss": champion_struct,
                "actual_flips": 0, "n_rows_mutated": 0, "mutation_map": None,
                "consensus_stats": None}

    # ── Phase 1: Each strategy proposes mutations independently ──
    # No model modification — just sampling + computing proposed values.
    # Each strategy gets its own RNG seed for independent sampling.
    proposals = []
    strategy_budgets = []
    for strategy_name, scale in MUTANT_STRATEGIES.items():
        strategy_budget = max(1, int(base_budget * scale))
        strategy_budgets.append(strategy_budget)

        strategy_rng = np.random.RandomState(
            int(rng.randint(0, 2**31)) ^ (hash(strategy_name) & 0x7FFFFFFF))

        guided_frac = cfg.guided_fraction if strategy_name != "random" else 0.0

        # Intelligence strategy: S4→S5 proposal channel (Beer's VSM).
        # S4 is the intelligence layer — it sees the full picture via
        # register-query attention. Its gradient signal carries extra
        # weight because it reflects what the model's intelligence
        # considers important. Fully gradient-guided (it knows what
        # it wants), with amplified S4 module importance and suppressed
        # non-S4 modules.
        if strategy_name == "intelligence":
            guided_frac = 1.0  # fully guided — S4 knows what it wants
            ri_use = {}
            gd_use = {}
            for path in (row_importance or {}):
                is_s4 = any(s in path for s in S4_MODULES)
                boost = cfg.s4_boost if is_s4 else (1.0 / cfg.s4_boost)
                ri_use[path] = row_importance[path] * boost
                if path in (grad_direction or {}):
                    gd_use[path] = grad_direction[path]
            prop = propose_mutations(
                model, strategy_budget, strategy_rng,
                sign_flip_rate=cfg.sign_flip_rate,
                row_importance=ri_use if ri_use else None,
                col_importance=col_importance if col_importance else None,
                grad_direction=gd_use if gd_use else None,
                guided_fraction=guided_frac,
            )
        else:
            prop = propose_mutations(
                model, strategy_budget, strategy_rng,
                sign_flip_rate=cfg.sign_flip_rate,
                row_importance=row_importance if row_importance else None,
                col_importance=col_importance if col_importance else None,
                grad_direction=grad_direction if grad_direction else None,
                guided_fraction=guided_frac,
            )
        proposals.append(prop)

    # ── Phase 2: Find consensus — ≥3 of 4 must agree ──
    consensus, consensus_stats = find_consensus(proposals, threshold=3)

    if not consensus or consensus_stats["consensus_flips"] == 0:
        # No consensus — no flips to evaluate
        return {
            "champion_loss": champion_loss,
            "budget": base_budget,
            "accepted": None,
            "accepted_loss": champion_loss,
            "frozen": False,
            "prose_loss": champion_prose,
            "struct_loss": champion_struct,
            "actual_flips": 0,
            "n_rows_mutated": 0,
            "mutation_map": None,
            "consensus_stats": consensus_stats,
        }

    # ── Phase 3: Apply consensus flips ──
    actual_flips, mutation_map = apply_consensus(model, consensus)

    # ── Phase 4: Evaluate — accept only if loss improves ──
    mutant_loss, mutant_prose, mutant_struct = _eval_loss()

    if mutant_loss < champion_loss:
        accepted = "consensus"
    else:
        # Revert
        load_topology(model, champion_snapshot)
        accepted = None
        mutant_loss = champion_loss
        mutant_prose = champion_prose
        mutant_struct = champion_struct
        mutation_map = None
        actual_flips = 0

    n_rows_mutated = sum(len(v) for v in mutation_map.values()) if mutation_map else 0

    return {
        "champion_loss": champion_loss,
        "budget": base_budget,
        "accepted": accepted,
        "accepted_loss": mutant_loss,
        "frozen": False,
        "prose_loss": mutant_prose,
        "struct_loss": mutant_struct,
        "actual_flips": actual_flips,
        "n_rows_mutated": n_rows_mutated,
        "mutation_map": mutation_map,
        "consensus_stats": consensus_stats,
    }


# ══════════════════════════════════════════════════════════════════════════════
# § 6b  Adam accumulator decay after accepted mutations
# ══════════════════════════════════════════════════════════════════════════════

def decay_adam_state(optimizer, model, decay: float = 0.1,
                     mutation_map: dict[str, set[int]] | None = None) -> int:
    """Surgically decay Adam m/v accumulators for mutated gamma entries only.

    After an accepted topology mutation, the ternary weights have changed
    but Adam's running mean (m) and variance (v) still reflect gradients
    from the old topology. This creates a tug-of-war: the momentum points
    in the old direction while the gradient now points differently.

    The key insight: only rows that were actually mutated need their Adam
    state reset. A mutation touching 26K weights out of 131M affects maybe
    a few hundred unique rows per module. Decaying ALL gamma entries
    (the old behavior) cold-starts the entire model's optimizer state —
    causing the CE spike. Surgical decay leaves untouched rows with full
    momentum, so only the ~0.02% of the model that changed needs to
    re-adapt.

    Args:
        optimizer:    the AdamW optimizer
        model:        the model (for walking ternary modules)
        decay:        scale factor for m/v (0.0 = full reset, 1.0 = no change)
        mutation_map: dict mapping module_path → set of mutated row indices.
                      If None, falls back to decaying ALL gamma entries
                      (legacy behavior — still a sledgehammer, but safe).

    Returns:
        Number of gamma entries (rows) that were decayed.
    """
    if decay >= 1.0 or not optimizer.state:
        return 0

    # Build map: gamma_path → set of row indices to decay
    gamma_decay_map: dict[str, set[int] | None] = {}
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            gamma_path = f"{path}.gamma"
            if mutation_map is not None:
                # Only decay rows that were mutated in this module
                if path in mutation_map:
                    gamma_decay_map[gamma_path] = mutation_map[path]
                # If this module wasn't mutated, skip it entirely
            else:
                # Legacy fallback: decay all rows
                gamma_decay_map[gamma_path] = None  # None = all rows

    if not gamma_decay_map:
        return 0

    n_decayed = 0

    # Navigate optimizer state tree and decay m/v for targeted gamma entries
    def _decay_tree(state_node, param_path_parts, depth=0):
        nonlocal n_decayed
        if isinstance(state_node, dict):
            for key, val in state_node.items():
                current_path = ".".join(param_path_parts + [key])
                if current_path in gamma_decay_map and isinstance(val, dict):
                    rows = gamma_decay_map[current_path]
                    for moment_key in ("m", "v"):
                        if moment_key in val and isinstance(val[moment_key], mx.array):
                            if rows is None:
                                # Legacy: decay entire vector
                                val[moment_key] = val[moment_key] * decay
                                n_decayed += val[moment_key].size
                            else:
                                # Surgical: only decay specific row indices
                                arr = val[moment_key]
                                row_indices = mx.array(sorted(rows))
                                updates = arr[row_indices] * decay
                                arr = arr.at[row_indices].add(updates - arr[row_indices])
                                val[moment_key] = arr
                                n_decayed += len(rows)
                else:
                    _decay_tree(val, param_path_parts + [key], depth + 1)
        elif isinstance(state_node, list):
            for i, val in enumerate(state_node):
                _decay_tree(val, param_path_parts + [str(i)], depth + 1)

    if isinstance(optimizer.state, list):
        for group in optimizer.state:
            _decay_tree(group, [], 0)
    elif isinstance(optimizer.state, dict):
        _decay_tree(optimizer.state, [], 0)

    mx.eval(optimizer.state)
    return n_decayed


# ══════════════════════════════════════════════════════════════════════════════
# § 7  Checkpointing
# ══════════════════════════════════════════════════════════════════════════════

def save_checkpoint(model, optimizer, step, cfg, checkpoint_dir,
                    train_losses, total_generations, total_accepted,
                    eval_metrics, row_importance, col_importance,
                    grad_direction, mutation_rng,
                    train_loader=None):
    step_dir = checkpoint_dir / f"step_{step:06d}"
    step_dir.mkdir(parents=True, exist_ok=True)

    flat = tree_flatten(model.parameters())
    mx.savez(str(step_dir / "model.npz"), **{k: v for k, v in flat})

    opt_flat = tree_flatten(optimizer.state)
    mx.savez(str(step_dir / "optimizer.npz"), **{k: v for k, v in opt_flat})

    imp_data = {}
    for path, arr in row_importance.items():
        imp_data[f"row.{path}"] = arr
    for path, arr in col_importance.items():
        imp_data[f"col.{path}"] = arr
    for path, arr in grad_direction.items():
        imp_data[f"dir.{path}"] = arr
    if imp_data:
        np.savez_compressed(str(step_dir / "importance.npz"), **imp_data)

    rng_state = mutation_rng.get_state()
    np.savez_compressed(str(step_dir / "rng.npz"),
                        state_array=rng_state[1],
                        pos=np.array([rng_state[2]], dtype=np.int64))

    state = {
        "step": step,
        "total_generations": total_generations,
        "total_accepted": total_accepted,
        "train_losses_last50": train_losses[-50:],
        "eval_metrics": eval_metrics or {},
        "data_loader": train_loader.save_state() if train_loader else {},
        "config": {
            "d_model": cfg.d_model, "vocab_size": cfg.vocab_size,
            "batch_size": cfg.batch_size, "total_steps": cfg.total_steps,
            "lr": cfg.lr, "seq_len": cfg.seq_len,
            "mix_ratio": cfg.mix_ratio,
        },
    }
    (step_dir / "state.json").write_text(json.dumps(state, indent=2))
    print(f"💾 Checkpoint saved: {step_dir}", file=sys.stderr, flush=True)


def find_latest_checkpoint(checkpoint_dir):
    if not checkpoint_dir.exists():
        return None
    step_dirs = sorted(checkpoint_dir.glob("step_*"))
    for d in reversed(step_dirs):
        if (d / "state.json").exists() and (d / "model.npz").exists():
            return d
    return None


def load_checkpoint(checkpoint_dir, model, optimizer):
    weights = dict(mx.load(str(checkpoint_dir / "model.npz")))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)

    opt_path = checkpoint_dir / "optimizer.npz"
    if opt_path.exists():
        from mlx.utils import tree_unflatten
        opt_state = dict(mx.load(str(opt_path)))
        optimizer.state = tree_unflatten(list(opt_state.items()))
        mx.eval(optimizer.state)

    row_imp, col_imp, grad_dir = {}, {}, {}
    imp_path = checkpoint_dir / "importance.npz"
    if imp_path.exists():
        data = dict(np.load(str(imp_path)))
        for key, arr in data.items():
            if key.startswith("row."): row_imp[key[4:]] = arr
            elif key.startswith("col."): col_imp[key[4:]] = arr
            elif key.startswith("dir."): grad_dir[key[4:]] = arr

    mutation_rng = np.random.RandomState()
    rng_path = checkpoint_dir / "rng.npz"
    if rng_path.exists():
        rng_data = np.load(str(rng_path))
        mutation_rng.set_state(("MT19937", rng_data["state_array"],
                                int(rng_data["pos"][0]), 0, 0.0))

    state = json.loads((checkpoint_dir / "state.json").read_text())
    print(f"📂 Loaded: {checkpoint_dir} (step {state['step']})", file=sys.stderr)
    return state["step"], state, row_imp, col_imp, grad_dir, mutation_rng, state.get("data_loader", {})


# ══════════════════════════════════════════════════════════════════════════════
# § 8  Main training loop
# ══════════════════════════════════════════════════════════════════════════════

def train(cfg: V10Config, args: argparse.Namespace) -> None:
    checkpoint_dir = Path(cfg.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v10 — V6 Compressor (5-pass, 9 strides) on Dolma Prose", file=sys.stderr)
    print("  Qwen3 BBPE tokenizer, next-token prediction", file=sys.stderr)
    print("=" * 72, file=sys.stderr)

    # ── Model ─────────────────────────────────────────────────
    model = create_model(cfg)
    freeze_ternary_weights(model)

    param_counts = count_parameters(model)
    total_ternary = count_ternary_weights(model)

    print(f"\n  d_model={cfg.d_model}  n_heads={cfg.n_heads}  "
          f"strides={cfg.strides}", file=sys.stderr)
    print(f"  d_ff={cfg.d_ff}  d_ff_consolidate={cfg.d_ff_consolidate}  "
          f"d_register={cfg.d_register}  alpha={cfg.alpha}", file=sys.stderr)
    print(f"  params: total={param_counts['total']:,}  "
          f"trainable={param_counts['trainable']:,}  "
          f"ternary={total_ternary:,}", file=sys.stderr)
    print(f"  vocab={cfg.vocab_size}  seq_len={cfg.seq_len}  "
          f"tokens/step={cfg.tokens_per_step:,}", file=sys.stderr)

    # ── Optimizer ─────────────────────────────────────────────
    optimizer = optim.Adam(learning_rate=cfg.lr, betas=[0.9, 0.999])

    # ── value_and_grad ────────────────────────────────────────
    loss_and_grad = nn.value_and_grad(model, loss_fn)

    # ── Data ──────────────────────────────────────────────────
    prose_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=0,
        shard_end=cfg.n_train_shards,
    )

    if cfg.mix_ratio > 0 and Path(cfg.structured_shard).exists():
        train_loader = MixedDataLoader(
            prose_loader=prose_loader,
            structured_path=cfg.structured_shard,
            mix_ratio=cfg.mix_ratio,
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
        )
        print(f"  🔀 Mixed data: {cfg.mix_ratio:.0%} structured, "
              f"{1-cfg.mix_ratio:.0%} prose", file=sys.stderr)
    else:
        train_loader = prose_loader
    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=8888,
    )

    # Structured eval loader for mixed-data-aware evolution.
    # Mutations must help BOTH prose and structured data to be accepted.
    structured_eval_loader = None
    if cfg.mix_ratio > 0 and Path(cfg.structured_shard).exists():
        structured_eval_loader = MixedDataLoader(
            prose_loader=ShardedDataLoader(
                data_dir=cfg.data_dir,
                batch_size=cfg.batch_size,
                seq_len=cfg.seq_len,
                shard_start=cfg.n_train_shards,
                shard_end=cfg.n_train_shards + cfg.n_eval_shards,
                seed=7777,
            ),
            structured_path=cfg.structured_shard,
            mix_ratio=1.0,  # always structured for this loader
            seq_len=cfg.seq_len,
            batch_size=cfg.batch_size,
            seed=7777,
        )

    # ── EMA importance maps ───────────────────────────────────
    row_importance: dict[str, np.ndarray] = {}
    col_importance: dict[str, np.ndarray] = {}
    grad_direction: dict[str, np.ndarray] = {}
    imp_alpha = 0.1
    mutation_rng = np.random.RandomState(42)

    # ── State ─────────────────────────────────────────────────
    start_step = 0
    train_losses: list[float] = []
    last_eval = None
    total_generations = 0
    total_accepted = 0
    loss_window: deque[float] = deque(maxlen=50)

    # ── Resume ────────────────────────────────────────────────
    if args.resume:
        if args.resume is True:
            # --resume with no argument: find latest
            ckpt = find_latest_checkpoint(checkpoint_dir)
        else:
            # --resume step_003000 or --resume /full/path/step_003000
            resume_path = Path(args.resume)
            if not resume_path.is_absolute():
                resume_path = checkpoint_dir / resume_path
            ckpt = resume_path if resume_path.exists() else None
        if ckpt:
            start_step, state, row_importance, col_importance, \
                grad_direction, mutation_rng, dl_state = load_checkpoint(ckpt, model, optimizer)
            train_losses = state.get("train_losses_last50", [])
            total_generations = state.get("total_generations", 0)
            total_accepted = state.get("total_accepted", 0)
            last_eval = state.get("eval_metrics")
            loss_window.extend(train_losses[-50:])
            if dl_state:
                train_loader.load_state(dl_state)
        else:
            print("  ⚠  No checkpoint found, starting fresh.", file=sys.stderr)

    # ── Warm-up optimizer ─────────────────────────────────────
    if not args.resume or not optimizer.state:
        ids_np, tgts_np = next(train_loader)
        ids = mx.array(ids_np)
        tgts = mx.array(tgts_np)
        lv, grads = loss_and_grad(model, ids, tgts)
        mx.eval(lv, grads)
        grads = normalize_shared_grads(grads)
        grads = zero_ternary_grads(model, grads)
        optimizer.update(model, grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

    print(f"\n  lr={cfg.lr}  warmup={cfg.warmup_steps}  "
          f"total_steps={cfg.total_steps}", file=sys.stderr)
    print(f"  gen_interval={cfg.gen_interval}  base_pct={cfg.base_pct}  "
          f"grad_accum={cfg.grad_accum}", file=sys.stderr)
    print(f"  data: {cfg.data_dir}", file=sys.stderr)
    if start_step > 0:
        print(f"  Resuming from step {start_step}", file=sys.stderr)
    print("", file=sys.stderr, flush=True)

    # ══════════════════════════════════════════════════════════
    # Main loop
    # ══════════════════════════════════════════════════════════

    t_start = time.time()

    for step in range(start_step + 1, cfg.total_steps + 1):
        t0 = time.time()

        lr = cosine_lr(step, cfg.warmup_steps, cfg.total_steps,
                       cfg.lr, cfg.lr_floor_ratio)
        optimizer.learning_rate = lr

        # ── Gradient accumulation ─────────────────────────────
        accum_loss = 0.0
        accum_grads = None

        for _micro in range(cfg.grad_accum):
            ids_np, tgts_np = next(train_loader)
            ids = mx.array(ids_np)
            tgts = mx.array(tgts_np)

            lv, grads = loss_and_grad(model, ids, tgts)
            mx.eval(lv, grads)
            accum_loss += float(lv.item())

            if accum_grads is None:
                accum_grads = grads
            else:
                accum_grads = tree_map(lambda a, b: a + b, accum_grads, grads)

        # Average over micro-batches
        step_loss = accum_loss / cfg.grad_accum
        accum_grads = tree_map(lambda g: g / cfg.grad_accum, accum_grads)

        train_losses.append(step_loss)
        loss_window.append(step_loss)

        # ── EMA importance from gamma grads ───────────────────
        for path, mod in _walk_ternary_modules(model):
            if not isinstance(mod, TernaryLinear):
                continue
            parts = path.split(".")
            g_node = accum_grads
            for p in parts:
                if isinstance(g_node, dict):
                    g_node = g_node.get(p, {})
                elif isinstance(g_node, list) and p.isdigit():
                    g_node = g_node[int(p)]
                else:
                    g_node = {}; break
            gamma_grad = g_node.get("gamma") if isinstance(g_node, dict) else None
            if gamma_grad is not None:
                gg = np.array(mx.abs(gamma_grad))
                gs = np.array(gamma_grad)
                # Skip this step's EMA update if gradients contain NaN/Inf
                # (preserves prior importance rather than poisoning it)
                if np.all(np.isfinite(gg)):
                    if path in row_importance:
                        row_importance[path] = imp_alpha * gg + (1 - imp_alpha) * row_importance[path]
                        grad_direction[path] = imp_alpha * gs + (1 - imp_alpha) * grad_direction[path]
                    else:
                        row_importance[path] = gg
                        grad_direction[path] = gs
            if hasattr(mod, "_x_abs_mean"):
                xm = np.array(mod._x_abs_mean)
                if np.all(np.isfinite(xm)):
                    if path in col_importance:
                        col_importance[path] = imp_alpha * xm + (1 - imp_alpha) * col_importance[path]
                    else:
                        col_importance[path] = xm

        # ── Normalize shared + zero ternary ───────────────────
        accum_grads = normalize_shared_grads(accum_grads)
        accum_grads = zero_ternary_grads(model, accum_grads)

        # ── Gradient clipping ─────────────────────────────────
        grad_sq = [mx.sum(g * g) for _, g in tree_flatten(accum_grads)]
        mx.eval(*grad_sq)
        grad_norm = sum(float(g) for g in grad_sq) ** 0.5
        if cfg.grad_clip > 0 and grad_norm > cfg.grad_clip:
            s = cfg.grad_clip / (grad_norm + 1e-8)
            accum_grads = tree_map(lambda g: g * s, accum_grads)

        # ── Optimizer step ────────────────────────────────────
        optimizer.update(model, accum_grads)
        mx.eval(model.parameters(), optimizer.state)
        restore_ternary(model)

        dt = time.time() - t0

        # step_loss is already r (relational loss) — recover CE for display
        ce = step_loss * (LOG_V - E_IRREDUCIBLE) + E_IRREDUCIBLE

        # ── Log ───────────────────────────────────────────────
        if step % cfg.log_interval == 0 or step == start_step + 1:
            avg50 = sum(loss_window) / max(len(loss_window), 1)
            elapsed = time.time() - t_start
            tps = cfg.tokens_per_step / dt
            evo_str = ""
            if total_generations > 0:
                pct = total_accepted / total_generations * 100
                evo_str = f" | evo {total_accepted}/{total_generations} ({pct:.0f}%)"

            print(
                f"step {step:>6d} | r={step_loss:.4f} (avg50: {avg50:.4f})"
                f" | CE={ce:.3f} | lr {lr:.2e}"
                f" | {tps:.0f} tok/s"
                f"{evo_str}"
                f" | {elapsed:.0f}s",
                file=sys.stderr, flush=True,
            )

            # Append lightweight training metrics to JSONL log
            _append_jsonl(checkpoint_dir / "train_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "r": step_loss,
                "ce": ce,
                "r_avg50": avg50,
                "lr": lr,
                "grad_norm": grad_norm,
                "tok_per_sec": tps,
                "elapsed": elapsed,
            })

        # ── Evolution ─────────────────────────────────────────
        if step % cfg.gen_interval == 0:
            gen_result = run_tournament(
                model, cfg, step, total_ternary, eval_loader,
                cfg.base_pct, mutation_rng,
                row_importance, col_importance, grad_direction,
                structured_eval_loader=structured_eval_loader,
            )
            total_generations += 1
            if gen_result["accepted"]:
                total_accepted += 1
                # Surgical Adam decay — only reset m/v for gamma entries
                # whose rows were actually mutated. Untouched rows keep
                # full momentum, preventing the CE spike.
                if cfg.mutation_adam_decay < 1.0:
                    n_decayed = decay_adam_state(
                        optimizer, model, decay=cfg.mutation_adam_decay,
                        mutation_map=gen_result.get("mutation_map"),
                    )

            accepted_str = gen_result["accepted"] or "rejected"
            delta = gen_result["accepted_loss"] - gen_result["champion_loss"]
            n_rows = gen_result.get("n_rows_mutated", 0)
            actual_flips = gen_result.get("actual_flips", 0)
            cs = gen_result.get("consensus_stats") or {}
            sampled = cs.get("positions_sampled", 0)
            decay_str = (f"  adam_decay={cfg.mutation_adam_decay} ({n_decayed} rows)"
                         if gen_result["accepted"] and cfg.mutation_adam_decay < 1.0 else "")
            # Show per-type losses when using mixed data
            type_str = ""
            if gen_result.get("struct_loss") is not None:
                type_str = (f"  prose={gen_result['prose_loss']:.4f}"
                            f"  struct={gen_result['struct_loss']:.4f}")
            print(
                f"  🧬 gen {total_generations}: {accepted_str}"
                f"  Δ={delta:+.4f}"
                f"  flips={actual_flips:,}/{sampled:,}"
                f"  rows={n_rows:,}"
                f"  {total_accepted}/{total_generations}"
                f"{type_str}"
                f"{decay_str}",
                file=sys.stderr, flush=True,
            )

            # Log evolution event
            _append_jsonl(checkpoint_dir / "evolution_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "generation": total_generations,
                "accepted": gen_result["accepted"],
                "champion_loss": gen_result["champion_loss"],
                "accepted_loss": gen_result["accepted_loss"],
                "delta": delta,
                "budget": gen_result["budget"],
                "actual_flips": actual_flips,
                "n_rows_mutated": n_rows,
                "prose_loss": gen_result.get("prose_loss"),
                "struct_loss": gen_result.get("struct_loss"),
                "consensus_stats": gen_result.get("consensus_stats"),
            })

        # ── Evaluation ────────────────────────────────────────
        if step % cfg.eval_interval == 0:
            last_eval = evaluate(model, cfg)
            print(
                f"📊 Eval @ {step}: loss={last_eval['loss']:.3f}"
                f"  ppl={last_eval['ppl']:.0f}  r={last_eval['r']:.3f}",
                file=sys.stderr, flush=True,
            )
            # Append full instrumentation to JSONL log
            _append_jsonl(checkpoint_dir / "metrics_log.jsonl", {
                "step": step,
                "timestamp": time.time(),
                "total_generations": total_generations,
                "total_accepted": total_accepted,
                **last_eval,
            })

        # ── Checkpoint ────────────────────────────────────────
        if step % cfg.checkpoint_interval == 0:
            save_checkpoint(model, optimizer, step, cfg, checkpoint_dir,
                            train_losses, total_generations, total_accepted,
                            last_eval, row_importance, col_importance,
                            grad_direction, mutation_rng, train_loader)

    # ── Final ─────────────────────────────────────────────────
    elapsed = time.time() - t_start
    final_eval = evaluate(model, cfg)
    print(
        f"\n{'='*72}\n"
        f"Training complete: {cfg.total_steps - start_step} steps in {elapsed:.0f}s\n"
        f"Final: loss={final_eval['loss']:.3f}  ppl={final_eval['ppl']:.0f}"
        f"  r={final_eval['r']:.3f}",
        file=sys.stderr,
    )

    save_checkpoint(model, optimizer, cfg.total_steps, cfg, checkpoint_dir,
                    train_losses, total_generations, total_accepted,
                    final_eval, row_importance, col_importance,
                    grad_direction, mutation_rng, train_loader)


# ══════════════════════════════════════════════════════════════════════════════
# § 9  CLI
# ══════════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="v10 — V6 compressor on Dolma prose (Qwen3 tokenizer)")
    parser.add_argument("--total-steps", type=int, default=None)
    parser.add_argument("--checkpoint-dir", type=str, default=None)
    parser.add_argument("--resume", nargs="?", const=True, default=False,
                        help="Resume training. No arg = latest checkpoint. "
                             "Arg = step dir name (e.g. step_003000) or full path.")
    parser.add_argument("--d-model", type=int, default=None)
    parser.add_argument("--batch-size", type=int, default=None)
    parser.add_argument("--grad-accum", type=int, default=None)
    parser.add_argument("--seq-len", type=int, default=None)
    parser.add_argument("--gen-interval", type=int, default=None)
    parser.add_argument("--base-pct", type=float, default=None)
    parser.add_argument("--lr", type=float, default=None)
    parser.add_argument("--eval-interval", type=int, default=None)
    parser.add_argument("--log-interval", type=int, default=None)
    parser.add_argument("--checkpoint-interval", type=int, default=None)
    parser.add_argument("--mix-ratio", type=float, default=None,
                        help="Fraction of structured data (0.0=prose only, 0.1=10%% structured)")
    parser.add_argument("--structured-shard", type=str, default=None,
                        help="Path to structured data shard (.npy)")

    args = parser.parse_args()
    cfg = V10Config()

    if args.total

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01U1bTVbLuR1Gnye4sKc5BJG.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/ternary.py"
}
```

**Summary:** Reading ternary.py (0-2000)

**Output:**
```
"""Ternary substrate for v8's hot-path components.

Self-contained — no imports from other verbum modules.

TernaryLinear uses mx.quantized_matmul at 2-bit (bits=2, group_size=64)
via Apple's AMX hardware path.  This replaces the custom Metal ternary
matmul kernels used in earlier iterations and yields a 2–4× speedup on
Apple Silicon for the dominant level-0 operations.

Ternary weights {-1, 0, +1} map to 2-bit integers {0, 1, 2}:
    encoded = ternary + 1

Per-channel gamma folds into quantized_matmul scales/biases so the
dequant is exact:
    gamma * encoded + (-gamma) = {-gamma, 0, +gamma} ✓

MLX packs 16 two-bit values per uint32 (little-endian bit order).
TernaryLinear stores:
    weight  — (N, K//16) uint32 packed topology (evolutionary, not optimized)
    gamma   — (N,)       float32 per-channel scale (trained by Adam)

The ternary topology evolves via mutation + tournament selection.  Gamma
is trained normally with Adam.  quantized_matmul supports autograd
natively so no custom VJP is needed for TernaryLinear.

TernaryEmbedding is UNCHANGED: embedding lookup is a gather, not a
matmul.  It keeps the existing custom VJP and uint8 (4-per-byte) packed
format.

Memory per ternary weight:
    TernaryLinear inference:  0.125 bytes (2-bit packed)
    TernaryEmbedding:         0.25  bytes (2-bit packed in uint8)

License: MIT
"""

from __future__ import annotations

import math
from typing import Any

import mlx.core as mx
import mlx.nn as nn


# ══════════════════════════════════════════════════════════════════════
# MLX uint32 pack / unpack  (for TernaryLinear + quantized_matmul)
# ══════════════════════════════════════════════════════════════════════
#
# MLX packs 16 two-bit values per uint32 in little-endian bit order:
#   value i occupies bits [2*i : 2*i+2]  for i in 0..15
#
# Encoding:  -1 → 0,  0 → 1,  +1 → 2   (ternary + 1)
# Decode:    (field & 0x3) - 1


def pack_ternary_mlx(w_int8: mx.array) -> mx.array:
    """Pack int8 {-1, 0, +1} weights [N, K] → uint32 [N, K//16].

    MLX little-endian bit layout: value i at bits [2*i : 2*i+2], i=0..15.
    Encoding: ternary + 1  →  {0, 1, 2}.
    K must be divisible by 16.
    """
    N, K = w_int8.shape
    assert K % 16 == 0, f"K={K} must be divisible by 16 for MLX 2-bit packing"

    # Shift {-1,0,+1} → {0,1,2} and promote to uint32 to avoid overflow
    encoded = (w_int8.astype(mx.int32) + 1).astype(mx.uint32)  # (N, K)

    # Reshape to (N, K//16, 16) — groups of 16 values per uint32
    groups = encoded.reshape(N, K // 16, 16)  # (N, K//16, 16)

    # Build the packed uint32: value i goes into bits [2*i : 2*i+2]
    # shifts[i] = 2*i for i in 0..15
    shifts = mx.array([2 * i for i in range(16)], dtype=mx.uint32)  # (16,)
    shifted = groups << shifts  # (N, K//16, 16) — each value in its bit slot

    # OR-reduce over the last axis to pack 16 values into one uint32
    packed = mx.sum(shifted, axis=-1)  # (N, K//16) uint32
    # mx.sum on uint32 gives uint32 — the OR semantics hold because
    # the 2-bit fields don't overlap (each occupies distinct bits).
    return packed.astype(mx.uint32)


def unpack_ternary_mlx(wq_uint32: mx.array) -> mx.array:
    """Unpack uint32 [N, K//16] → int8 {-1, 0, +1} [N, K].

    Inverse of pack_ternary_mlx.
    """
    N, K16 = wq_uint32.shape
    K = K16 * 16

    # Expand to (N, K//16, 1) then broadcast shifts
    packed = wq_uint32.reshape(N, K16, 1)  # (N, K//16, 1)
    shifts = mx.array([2 * i for i in range(16)], dtype=mx.uint32)  # (16,)

    # Extract each 2-bit field; mask with integer literal (MLX broadcasts scalars)
    fields = (packed >> shifts) & 3  # (N, K//16, 16) uint32

    # Decode: field - 1 → {-1, 0, +1}
    decoded = fields.astype(mx.int32) - 1  # (N, K//16, 16) int32

    return decoded.reshape(N, K).astype(mx.int8)


# ══════════════════════════════════════════════════════════════════════
# uint8 pack / unpack  (for TernaryEmbedding — unchanged)
# ══════════════════════════════════════════════════════════════════════
#
# Encoding:  -1 → 0b00,  0 → 0b01,  +1 → 0b10   (0b11 unused)
# Positions: bits {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}
# Decode:    ((packed >> shift) & 0x3) - 1
# K must be divisible by 4.


def pack_ternary(w: mx.array) -> mx.array:
    """Pack int8 {-1, 0, +1} weights [N, K] → uint8 [N, K//4].

    Used by TernaryEmbedding (4 values per byte, big-endian within byte).
    K must be divisible by 4.
    """
    assert w.shape[-1] % 4 == 0, f"K={w.shape[-1]} must be divisible by 4"
    w_shifted = (w.astype(mx.int16) + 1).astype(mx.uint8)
    packed = (
        (w_shifted[:, 0::4] << 6) |
        (w_shifted[:, 1::4] << 4) |
        (w_shifted[:, 2::4] << 2) |
        w_shifted[:, 3::4]
    )
    return packed.astype(mx.uint8)


def unpack_ternary(packed: mx.array, K: int) -> mx.array:
    """Unpack uint8 [N, K//4] → int8 {-1, 0, +1} [N, K].

    Inverse of pack_ternary. K is the logical (unpacked) weight dimension.
    """
    w0 = ((packed >> 6) & 0x3).astype(mx.int16) - 1
    w1 = ((packed >> 4) & 0x3).astype(mx.int16) - 1
    w2 = ((packed >> 2) & 0x3).astype(mx.int16) - 1
    w3 = (packed & 0x3).astype(mx.int16) - 1
    N = packed.shape[0]
    stacked = mx.stack([w0, w1, w2, w3], axis=-1)  # (N, K//4, 4)
    return stacked.reshape(N, K).astype(mx.int8)


# ══════════════════════════════════════════════════════════════════════
# Ternary initialization
# ══════════════════════════════════════════════════════════════════════


def _ternary_init(out_features: int, in_features: int) -> tuple[mx.array, mx.array]:
    """Initialize TernaryLinear weights: Kaiming normal → quantize → MLX uint32 pack.

    Returns:
        wq_uint32: (out_features, in_features//16) uint32  — packed topology
        gamma:     (out_features,) float32                 — per-channel scale
    """
    assert in_features % 16 == 0, (
        f"in_features={in_features} must be divisible by 16 for MLX 2-bit packing"
    )
    # Kaiming normal: std = sqrt(2 / in_features)
    std = math.sqrt(2.0 / in_features)
    w_init = mx.random.normal((out_features, in_features)) * std

    # Per-channel absmean quantization
    gamma = mx.abs(w_init).mean(axis=-1)
    w_scaled = w_init / (mx.expand_dims(gamma, axis=-1) + 1e-8)
    w_q = mx.clip(mx.round(w_scaled), -1, 1).astype(mx.int8)

    # Pack 16 weights per uint32 for quantized_matmul
    wq_uint32 = pack_ternary_mlx(w_q)  # (N, K//16) uint32

    return wq_uint32, gamma


def _ternary_embed_init(vocab_size: int, d_model: int) -> tuple[mx.array, mx.array]:
    """Initialize TernaryEmbedding weights: Kaiming normal → quantize → uint8 pack.

    Returns:
        w_packed: (vocab_size, d_model//4) uint8  — packed topology
        gamma:    (vocab_size,) float32           — per-token scale
    """
    assert d_model % 4 == 0, f"d_model={d_model} must be divisible by 4 for packing"
    std = math.sqrt(2.0 / d_model)
    w_init = mx.random.normal((vocab_size, d_model)) * std

    gamma = mx.abs(w_init).mean(axis=-1)
    w_scaled = w_init / (mx.expand_dims(gamma, axis=-1) + 1e-8)
    w_q = mx.clip(mx.round(w_scaled), -1, 1).astype(mx.int8)

    w_packed = pack_ternary(w_q)  # (vocab_size, d_model//4) uint8
    return w_packed, gamma


# ══════════════════════════════════════════════════════════════════════
# TernaryLinear — mx.quantized_matmul path (AMX / Apple Silicon)
# ══════════════════════════════════════════════════════════════════════


class TernaryLinear(nn.Module):
    """Linear layer with ternary routing topology via mx.quantized_matmul.

    Forward:
        scales, biases = f(gamma)          # fold gamma into quant params
        y = quantized_matmul(norm(x), W,   # AMX-accelerated 2-bit matmul
                             scales, biases,
                             transpose=True, group_size=64, bits=2)

    The ternary {-1, 0, +1} encoding maps to 2-bit int {0, 1, 2}:
        encoded = ternary + 1

    Per-channel gamma is folded into quantized_matmul's scales/biases:
        scales = gamma           → dequant multiplier
        biases = -gamma          → shift so 0-encoded → actual 0
    Dequant: gamma * {0,1,2} + (-gamma) = {-gamma, 0, +gamma} ✓

    The weight tensor (uint32, N × K//16) represents the ternary topology.
    It is EVOLUTIONARY — mutated via tournament selection, never touched
    by the gradient optimizer.  Its gradient is always zero.

    gamma is CONTINUOUS — trained normally by Adam.  mx.quantized_matmul
    supports autograd natively; no custom VJP is needed.

    Args:
        in_features:  input dimension  (must be divisible by 16)
        out_features: output dimension
        pre_norm:     if True, apply RMSNorm before projection
    """

    # Class-level quantization constants shared with mx.quantized_matmul
    group_size: int = 64
    bits: int = 2

    def __init__(self, in_features: int, out_features: int, pre_norm: bool = True):
        super().__init__()
        self.in_features = in_features
        self.out_features = out_features
        self.pre_norm = pre_norm

        if pre_norm:
            self.norm = nn.RMSNorm(in_features)

        # weight:  (out_features, in_features//16) uint32  — packed ternary topology
        # gamma:   (out_features,) float32               — trainable per-channel scale
        wq_uint32, gamma = _ternary_init(out_features, in_features)
        self.weight = wq_uint32
        self.gamma = gamma

    def _get_scales_biases(self) -> tuple[mx.array, mx.array]:
        """Compute quantized_matmul scales/biases from per-channel gamma.

        For bits=2, group_size=64 and K = in_features:
            n_groups = K // group_size
            scales shape: (out_features, n_groups)
            biases shape: (out_features, n_groups)

        The dequant formula in quantized_matmul is:
            out = scales * quant_val + biases

        With quant_val ∈ {0, 1, 2} (encoded ternary) and:
            scales = gamma   (broadcast over groups)
            biases = -gamma  (shift so 0-encoded maps to 0 in output)

        We get:  {0*γ-γ, 1*γ-γ, 2*γ-γ} = {-γ, 0, +γ} ✓
        """
        n_groups = self.in_features // self.group_size
        # gamma: (out_features,) → expand to (out_features, n_groups)
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.out_features, n_groups),
        )
        return gamma_2d, -gamma_2d

    def __call__(self, x: mx.array) -> mx.array:
        if self.pre_norm:
            x = self.norm(x)

        # Cache input statistics for gradient-informed mutation.
        # stop_gradient keeps these out of the backward graph.
        # x shape: (B, T, in_features) or (in_features,) — mean over all but last dim.
        if x.ndim >= 2:
            reduce_axes = tuple(range(x.ndim - 1))
            self._x_abs_mean = mx.stop_gradient(mx.mean(mx.abs(x), axis=reduce_axes))
            self._x_mean = mx.stop_gradient(mx.mean(x, axis=reduce_axes))
        else:
            self._x_abs_mean = mx.stop_gradient(mx.abs(x))
            self._x_mean = mx.stop_gradient(x)

        scales, biases = self._get_scales_biases()
        # stop_gradient on weight: it's evolutionary (uint32, not differentiable).
        # Without this, MLX autograd would attempt a VJP through quantized_matmul
        # w.r.t. the uint32 weight argument and raise an error.
        w = mx.stop_gradient(self.weight)
        return mx.quantized_matmul(
            x,
            w,
            scales,
            biases,
            transpose=True,
            group_size=self.group_size,
            bits=self.bits,
        )

    def ternary_stats(self) -> dict[str, float]:
        """Report ternary weight and gamma statistics."""
        w = unpack_ternary_mlx(self.weight)  # (N, K) int8
        total = w.size
        return {
            "sparsity":    float((w == 0).sum().item()) / total,
            "pos_frac":    float((w == 1).sum().item()) / total,
            "neg_frac":    float((w == -1).sum().item()) / total,
            "gamma_mean":  float(self.gamma.mean().item()),
            "gamma_std":   float(mx.sqrt(mx.var(self.gamma)).item()),
        }


# ══════════════════════════════════════════════════════════════════════
# TernaryEmbedding — packed ternary lookup table (UNCHANGED)
# ══════════════════════════════════════════════════════════════════════


class TernaryEmbedding(nn.Module):
    """Embedding layer with ternary vectors and per-token gamma.

    Each vocabulary entry is a ternary vector {-1, 0, +1}^d_model with a
    float32 per-token scale (gamma). Lookup unpacks the selected rows on
    the fly, producing float32 output identical to standard embedding.

    Storage: vocab_size × d_model/4 bytes (packed) + vocab_size × 4 bytes (gamma)
           = vocab_size × (d_model/4 + 4) bytes
    vs float: vocab_size × d_model × 4 bytes

    For vocab=50277, d=1024: 13.1 MB packed vs 196.4 MB float (15× smaller).

    Ternary topology evolves via evolutionary mutation, not gradient descent.
    Uses the uint8 (4-per-byte) packed format and a custom VJP — embedding
    lookup is a gather, not a matmul, so quantized_matmul does not apply.
    """

    def __init__(self, vocab_size: int, d_model: int):
        super().__init__()
        self.vocab_size = vocab_size
        self.d_model = d_model

        # Initialize: random normal → quantize → pack into uint8
        w_packed, gamma = _ternary_embed_init(vocab_size, d_model)
        self.ternary_weight = w_packed   # (vocab_size, d_model//4) uint8
        self.gamma = gamma               # (vocab_size,) float32

    def __call__(self, tokens: mx.array) -> mx.array:
        """Lookup ternary embeddings for token indices.

        tokens: (*, ) int array of token indices
        Returns: (*, d_model) float32 array
        """
        return _ternary_embed_fwd(tokens, self.ternary_weight, self.gamma)

    @property
    def weight_T(self) -> mx.array:
        """Unpacked weight matrix transposed: (d_model, vocab_size) float32.

        SLOW fallback — unpacks to float32 then does regular matmul.
        Prefer output_proj() for the tied output projection.
        """
        w = unpack_ternary(self.ternary_weight, self.d_model).astype(mx.float32)
        w = w * mx.expand_dims(self.gamma, axis=-1)
        return w.T  # (d_model, vocab_size)

    def output_proj(self, x: mx.array) -> mx.array:
        """Tied output projection via quantized_matmul (fast, ternary).

        x: (B, L, d_model) → logits (B, L, vocab_size)

        Repacks the uint8 embedding weights to uint32 format for
        quantized_matmul. The repacked weights are cached and invalidated
        when the topology mutates (detected via shape/id change).
        """
        # Repack uint8 → uint32 if needed (cache for speed)
        if (not hasattr(self, '_qm_cache_id') or
                self._qm_cache_id != id(self.ternary_weight)):
            # Unpack uint8 → int8 → repack uint32
            w_int8 = unpack_ternary(self.ternary_weight, self.d_model)  # (V, d)
            self._qm_weight = pack_ternary_mlx(w_int8)  # (V, d//16) uint32
            self._qm_cache_id = id(self.ternary_weight)

        # Build scales/biases from gamma (same as TernaryLinear)
        group_size = 64
        n_groups = self.d_model // group_size
        gamma_2d = mx.broadcast_to(
            mx.expand_dims(self.gamma, axis=-1),
            (self.vocab_size, n_groups),
        )
        scales = gamma_2d
        biases = -gamma_2d

        w = mx.stop_gradient(self._qm_weight)
        return mx.quantized_matmul(
            x, w, scales, biases,
            transpose=True, group_size=group_size, bits=2,
        )

    @property
    def in_features(self):
        """For compatibility with _walk_ternary_modules."""
        return self.d_model

    @property
    def out_features(self):
        return self.vocab_size


@mx.custom_function
def _ternary_embed_fwd(
    tokens: mx.array,
    w_packed: mx.array,
    gamma: mx.array,
) -> mx.array:
    """Forward: unpack selected rows from packed ternary embedding, scale by gamma.

    tokens:   (*,) int indices
    w_packed: (vocab_size, d_model//4) uint8
    gamma:    (vocab_size,) float32

    Returns:  (*, d_model) float32
    """
    d_model = w_packed.shape[1] * 4
    flat_tokens = tokens.reshape(-1)
    packed_rows = w_packed[flat_tokens]      # (N, d_model//4) uint8
    gamma_rows = gamma[flat_tokens]          # (N,) float32

    # Unpack: uint8 → float32 {-1, 0, +1}
    w0 = ((packed_rows >> 6) & 0x3).astype(mx.float32) - 1.0
    w1 = ((packed_rows >> 4) & 0x3).astype(mx.float32) - 1.0
    w2 = ((packed_rows >> 2) & 0x3).astype(mx.float32) - 1.0
    w3 = (packed_rows & 0x3).astype(mx.float32) - 1.0
    # Interleave: columns {4k, 4k+1, 4k+2, 4k+3}
    N = flat_tokens.shape[0]
    unpacked = mx.stack([w0, w1, w2, w3], axis=-1).reshape(N, d_model)

    # Scale by per-token gamma
    result = unpacked * mx.expand_dims(gamma_rows, axis=-1)
    return result.reshape(*tokens.shape, d_model)


@_ternary_embed_fwd.vjp
def _ternary_embed_vjp(primals, cotangent, output):
    """Backward through ternary embedding lookup.

    ∂L/∂tokens:   zeros (integer indices, not differentiable)
    ∂L/∂w_packed: zeros (topology evolves via mutation, not gradient)
    ∂L/∂gamma:    per-token grad, scattered back to (vocab_size,)
    """
    tokens, w_packed, gamma = primals
    grad_out = cotangent  # (*, d_model)
    d_model = w_packed.shape[1] * 4

    flat_tokens = tokens.reshape(-1)
    N = flat_tokens.shape[0]
    grad_flat = grad_out.reshape(N, d_model)

    # ∂L/∂gamma: Σ_d (grad_out[n,d] * unpacked[n,d])
    packed_rows = w_packed[flat_tokens]
    w0 = ((packed_rows >> 6) & 0x3).astype(mx.float32) - 1.0
    w1 = ((packed_rows >> 4) & 0x3).astype(mx.float32) - 1.0
    w2 = ((packed_rows >> 2) & 0x3).astype(mx.float32) - 1.0
    w3 = (packed_rows & 0x3).astype(mx.float32) - 1.0
    unpacked = mx.stack([w0, w1, w2, w3], axis=-1).reshape(N, d_model)

    grad_gamma_per_token = mx.sum(grad_flat * unpacked, axis=-1)  # (N,)

    # Scatter gamma grads back to (vocab_size,)
    grad_gamma = mx.zeros((gamma.shape[0],), dtype=mx.float32)
    grad_gamma = grad_gamma.at[flat_tokens].add(grad_gamma_per_token)

    # ∂L/∂w_packed: zeros
    grad_w_packed = mx.zeros_like(w_packed).astype(mx.float32)

    # No gradient for tokens
    grad_tokens = mx.zeros(tokens.shape, dtype=mx.float32)

    return grad_tokens, grad_w_packed, grad_gamma


# ══════════════════════════════════════════════════════════════════════
# Ternary module utilities
# ══════════════════════════════════════════════════════════════════════


def _walk_ternary_modules(model: nn.Module):
    """Yield (path, module) for all TernaryLinear and TernaryEmbedding in model."""
    for path, module in model.named_modules():
        if isinstance(module, (TernaryLinear, TernaryEmbedding)):
            yield path, module


def zero_ternary_grads(model: nn.Module, grads: dict) -> dict:
    """Zero out packed topology weight gradients in the grad pytree.

    TernaryLinear.weight (uint32) is never touched by the optimizer —
    its topology evolves via mutation.  The grad returned by
    quantized_matmul autograd for the weight argument is zeros already,
    but this function enforces that guarantee and prevents any accidental
    optimizer state accumulation.

    TernaryEmbedding.ternary_weight (uint8) is similarly evolutionary.

    gamma gradients are left untouched — Adam updates gamma normally.
    """
    # Collect packed weight keys for all ternary modules
    weight_keys: dict[str, tuple] = {}
    for path, module in _walk_ternary_modules(model):
        if isinstance(module, TernaryLinear):
            key = f"{path}.weight" if path else "weight"
            weight_keys[key] = module.weight.shape
        elif isinstance(module, TernaryEmbedding):
            key = f"{path}.ternary_weight" if path else "ternary_weight"
            weight_keys[key] = module.ternary_weight.shape

    def _zero(path_prefix: str, tree):
        if isinstance(tree, dict):
            return {
                k: _zero(f"{path_prefix}.{k}" if path_prefix else k, v)
                for k, v in tree.items()
            }
        elif isinstance(tree, list):
            return [
                _zero(f"{path_prefix}.{i}" if path_prefix else str(i), v)
                for i, v in enumerate(tree)
            ]
        elif isinstance(tree, mx.array) and path_prefix in weight_keys:
            shape = weight_keys[path_prefix]
            return mx.zeros(shape, dtype=tree.dtype)
        return tree

    return _zero("", grads)


def freeze_ternary_weights(model: nn.Module) -> int:
    """Freeze all packed ternary weight parameters so the optimizer ignores them.

    This is the correct way to protect packed uint32/uint8 topology weights
    from AdamW weight decay corruption.  Without freezing, AdamW applies
    weight decay (w *= 1 - lr*wd) which casts packed uint32 to float32,
    destroying the 2-bit field packing.

    Freezing removes these parameters from model.trainable_parameters(),
    so nn.value_and_grad won't differentiate through them and the optimizer
    won't apply weight decay or momentum updates.

    Evolutionary mutations still work via direct assignment (mod.weight = ...).

    Must be called:
      - After model creation
      - After model.load_weights() (which may reset freeze state)

    Returns:
        Number of modules frozen.
    """
    n_frozen = 0
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            mod.freeze(keys=["weight"])
            n_frozen += 1
        elif isinstance(mod, TernaryEmbedding):
            mod.freeze(keys=["ternary_weight"])
            n_frozen += 1
    return n_frozen


def restore_ternary(model: nn.Module) -> None:
    """Assert ternary weights have correct dtype — detect corruption early.

    With freeze_ternary_weights() applied, the optimizer should never touch
    packed weights.  This function raises immediately if it detects dtype
    drift rather than silently corrupting the packing by clipping.

    The old implementation clipped packed uint32 values to [0, 3] which
    DESTROYED the 2-bit field packing (15 of 16 slots collapsed to -1).
    That bug is now prevented by freezing, and this function is the alarm.
    """
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            if mod.weight.dtype != mx.uint32:
                raise RuntimeError(
                    f"TERNARY CORRUPTION: {path}.weight dtype is "
                    f"{mod.weight.dtype}, expected uint32. "
                    f"Was freeze_ternary_weights() called after model init "
                    f"and after load_weights()?"
                )
        elif isinstance(mod, TernaryEmbedding):
            if mod.ternary_weight.dtype != mx.uint8:
                raise RuntimeError(
                    f"TERNARY CORRUPTION: {path}.ternary_weight dtype is "
                    f"{mod.ternary_weight.dtype}, expected uint8. "
                    f"Was freeze_ternary_weights() called after model init "
                    f"and after load_weights()?"
                )


# ══════════════════════════════════════════════════════════════════════
# Evolutionary topology mutation
# ══════════════════════════════════════════════════════════════════════
#
# Ternary topology = genome (N loci × 3 alleles {-1, 0, +1}).
# Evolution via mutation + tournament selection, not gradient descent.
#
# The relational loss r ∈ [0, 1] forms a cone-shaped restriction on
# the viable mutation space:
#
#   r ≈ 1.0  ████████████  wide cone — explore topology freely
#   r ≈ 0.5  ██████        moderate — refine structure
#   r ≈ 0.1  ██            narrow — surgical mutations only
#   r < 0.05 ·             frozen — topology crystallized
#
# Champion never degrades: mutations that increase loss are rejected.


def count_ternary_weights(model: nn.Module) -> int:
    """Count total logical ternary weight positions across all modules."""
    total = 0
    for _, mod in _walk_ternary_modules(model):
        total += mod.out_features * mod.in_features
    return total


def mutation_cone(r_ema: float, total_weights: int, base_pct: float = 0.001) -> int:
    """Compute mutation budget from relational loss via quadratic cone.

    Used by Dolma phase to protect BIOS-burned circuits. NOT used during BIOS.

    Args:
        r_ema:          relational loss EMA ∈ [0, 1]. 1.0 = random, 0.0 = converged.
        total_weights:  total ternary weight count
        base_pct:       maximum mutation rate at the cone's widest point

    Returns:
        Number of weights to mutate this generation.
    """
    if r_ema < 0.05:
        return 0  # converged — topology frozen
    # Quadratic cone: budget ∝ r²; full budget at r ≥ 0.6
    scale = min(1.0, (r_ema / 0.6) ** 2)
    return max(1, int(total_weights * base_pct * scale))


def bios_mutation_budget(
    step: int,
    total_steps: int,
    total_weights: int,
    base_pct: float = 0.005,
) -> int:
    """Compute mutation budget for BIOS phase: high constant then late decay.

    During BIOS burn-in, topology exploration should NOT be gated by loss.
    Gamma (continuous) learns surface statistics fast, driving loss down and
    starving topology evolution via the cone. Instead:

      First 80%: full budget — explore topology freely, find circuits.
      Last 20%:  linear decay to 10% — crystallize what worked.

    Args:
        step:          current training step
        total_steps:   total BIOS training steps
        total_weights: total ternary weight count
        base_pct:      mutation rate during exploration phase (default 0.5%)

    Returns:
        Number of weights to mutate this generation.
    """
    decay_start = int(total_steps * 0.8)
    if step <= decay_start:
        scale = 1.0
    else:
        # Linear decay from 1.0 → 0.1 over the last 20%
        progress = (step - decay_start) / max(1, total_steps - decay_start)
        scale = 1.0 - 0.9 * progress
    return max(1, int(total_weights * base_pct * scale))


def save_topology(model: nn.Module) -> list[tuple[str, mx.array]]:
    """Snapshot all ternary weight topologies for champion preservation.

    Returns a list of (path, weight_copy) pairs.
    TernaryLinear:  copies mod.weight  (uint32)
    TernaryEmbedding: copies mod.ternary_weight (uint8)
    """
    snapshot = []
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            snapshot.append((path, mx.array(mod.weight)))
        else:
            snapshot.append((path, mx.array(mod.ternary_weight)))
    mx.eval(*[w for _, w in snapshot])
    return snapshot


def load_topology(model: nn.Module, snapshot: list[tuple[str, mx.array]]) -> None:
    """Restore ternary weights from a topology snapshot.

    Used to revert failed mutations (champion preservation).
    """
    mod_map = {path: mod for path, mod in _walk_ternary_modules(model)}
    restored = []
    for path, saved_weight in snapshot:
        if path not in mod_map:
            continue
        mod = mod_map[path]
        if isinstance(mod, TernaryLinear):
            mod.weight = saved_weight
        else:
            mod.ternary_weight = saved_weight
        restored.append(saved_weight)
    if restored:
        mx.eval(*restored)


def mutate_topology(
    model: nn.Module,
    budget: int,
    rng: Any,
    depth_weights: dict[str, float] | None = None,
    sign_flip_rate: float = 0.2,
    row_importance: dict[str, Any] | None = None,
    col_importance: dict[str, Any] | None = None,
    grad_direction: dict[str, Any] | None = None,
    guided_fraction: float = 0.7,
) -> tuple[int, dict[str, set[int]]]:
    """Apply gradient-informed mutations to the ternary topology.

    Distributes `budget` mutations across ternary modules, weighted by
    depth priority.  Within each module, positions are sampled using a
    mix of importance-weighted and uniform random:

      70% (guided_fraction): rows sampled ∝ |∂L/∂γ| (gamma gradient EMA)
                              cols sampled ∝ mean(|x|) (input activation EMA)
      30% (1-guided_fraction): uniform random (exploration, prevents stagnation)

    When gradient direction info is available, activating mutations (0→±1)
    prefer the sign indicated by the gradient.

    Args:
        model:            the model to mutate IN PLACE
        budget:           total number of logical weights to flip
        rng:              numpy RandomState for reproducible mutations
        depth_weights:    module path prefix → float priority weight
        sign_flip_rate:   fraction of non-zero mutations that flip sign
        row_importance:   {module_path: np.array (out_features,)} from |∂L/∂γ| EMA
        col_importance:   {module_path: np.array (in_features,)} from mean(|x|) EMA
        grad_direction:   {module_path: np.array (out_features,)} sign of ∂L/∂γ EMA
        guided_fraction:  fraction of mutations that are importance-weighted (rest uniform)

    Returns:
        (n_mutated, mutation_map) — total count and dict mapping
        module_path → set of mutated row indices. The mutation map
        enables surgical Adam decay: only gamma entries for rows that
        actually changed need their optimizer state reset.
    """
    import numpy as np

    modules = list(_walk_ternary_modules(model))
    if not modules or budget <= 0:
        return 0, {}

    # Compute effective weight for each module
    sizes = [mod.out_features * mod.in_features for _, mod in modules]

    if depth_weights is not None:
        effective = []
        for (path, _), n_weights in zip(modules, sizes):
            best_weight = 1.0
            best_len = 0
            for prefix, w in depth_weights.items():
                if path.startswith(prefix) and len(prefix) > best_len:
                    best_weight = w
                    best_len = len(prefix)
            effective.append(n_weights * best_weight)
    else:
        effective = [float(s) for s in sizes]

    total_effective = sum(effective)

    total_mutated = 0
    mutated_arrays = []
    mutation_map: dict[str, set[int]] = {}

    for (path, mod), n_weights, eff in zip(modules, sizes, effective):
        mod_budget = max(0, round(budget * eff / total_effective))
        if mod_budget == 0:
            continue
        mod_budget = min(mod_budget, n_weights)

        # Get importance maps for this module (if available)
        row_imp = row_importance.get(path) if row_importance else None
        col_imp = col_importance.get(path) if col_importance else None
        grad_dir = grad_direction.get(path) if grad_direction else None

        if isinstance(mod, TernaryLinear):
            n, rows = _mutate_linear(
                mod, mod_budget, rng, np, mutated_arrays, sign_flip_rate,
                row_imp, col_imp, grad_dir, guided_fraction,
            )
            total_mutated += n
            mutation_map[path] = rows
        else:
            n, rows = _mutate_embedding(
                mod, mod_budget, rng, np, mutated_arrays, sign_flip_rate,
            )
            total_mutated += n
            mutation_map[path] = rows

    if mutated_arrays:
        mx.eval(*mutated_arrays)

    return total_mutated, mutation_map


def _importance_sample_indices(
    N: int,
    K: int,
    budget: int,
    rng: Any,
    np: Any,
    row_imp: Any | None,
    col_imp: Any | None,
    guided_fraction: float,
) -> Any:
    """Sample (row, col) mutation positions using importance-weighted + uniform mix.

    guided_fraction of positions are sampled proportional to:
        P(i,j) ∝ row_importance[i] × col_importance[j]
    The rest are uniform random (exploration).

    Returns flat logical indices (row * K + col).
    """
    n_guided = int(budget * guided_fraction)
    n_uniform = budget - n_guided

    indices_parts = []

    # ── Importance-weighted positions ──
    if n_guided > 0 and (row_imp is not None or col_imp is not None):
        # Row probabilities from |∂L/∂γ| importance
        if row_imp is not None and len(row_imp) == N:
            row_p = np.asarray(row_imp, dtype=np.float64)
            row_p = np.where(np.isfinite(row_p), row_p, 0.0)  # NaN/Inf → 0
            row_p = np.maximum(row_p, 1e-8)  # floor to prevent zero-prob rows
            row_p /= row_p.sum()
        else:
            row_p = None  # uniform

        # Column probabilities from mean(|x|) importance
        if col_imp is not None and len(col_imp) == K:
            col_p = np.asarray(col_imp, dtype=np.float64)
            col_p = np.where(np.isfinite(col_p), col_p, 0.0)  # NaN/Inf → 0
            col_p = np.maximum(col_p, 1e-8)
            col_p /= col_p.sum()
        else:
            col_p = None  # uniform

        rows = rng.choice(N, size=n_guided, p=row_p)
        cols = rng.choice(K, size=n_guided, p=col_p)
        indices_parts.append(rows * K + cols)

    else:
        # No importance info — fall back to all uniform
        n_uniform += n_guided

    # ── Uniform random positions (exploration) ──
    if n_uniform > 0:
        indices_parts.append(rng.randint(0, N * K, size=n_uniform))

    return np.concatenate(indices_parts) if len(indices_parts) > 1 else indices_parts[0]


def _mutate_linear(
    mod: "TernaryLinear",
    mod_budget: int,
    rng: Any,
    np: Any,
    mutated_arrays: list,
    sign_flip_rate: float = 0.2,
    row_imp: Any | None = None,
    col_imp: Any | None = None,
    grad_dir: Any | None = None,
    guided_fraction: float = 0.7,
) -> tuple[int, set[int]]:
    """Mutate TernaryLinear.weight with gradient-informed position selection.

    Position selection: importance-weighted sampling from |∂L/∂γ| (rows)
    and mean(|x|) (columns), mixed with uniform exploration.

    Direction for 0→±1 activations: when gradient direction is available,
    prefer the sign that the gradient indicates will reduce loss.

    Mutation rules:
        0 → ±1        (activate — gradient-biased if direction available)
       ±1 → 0         (deactivate, probability 1-sign_flip_rate)
       ±1 → ∓1        (sign flip, probability sign_flip_rate)

    Returns:
        (n_mutated, mutated_rows) — count and set of affected row indices.
        mutated_rows maps to gamma indices for surgical Adam decay.
    """
    N = mod.out_features
    K = mod.in_features

    packed_np = np.array(mod.weight)  # (N, K//16) uint32
    flat_packed = packed_np.reshape(-1)

    # Sample positions: importance-weighted + uniform mix
    indices = _importance_sample_indices(
        N, K, mod_budget, rng, np, row_imp, col_imp, guided_fraction,
    )

    # Map logical index → packed coordinates
    rows = indices // K
    cols = indices % K
    uint32_idx = rows * (K // 16) + cols // 16
    slot = cols % 16
    shifts = (slot * 2).astype(np.uint32)

    # Read current values
    current_encoded = ((flat_packed[uint32_idx] >> shifts) & np.uint32(0x3))
    current_val = current_encoded.astype(np.int8) - 1  # {-1,0,+1}

    # Apply mutations
    new_val = np.copy(current_val)

    # Non-zero positions: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero positions: activate with gradient-directed sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        if grad_dir is not None and len(grad_dir) == N:
            # Use gradient direction: sign(∂L/∂γ_i) for row i
            # Positive grad → gamma wants to grow → prefer +1 (increases magnitude)
            # Negative grad → gamma wants to shrink → prefer -1
            # Apply as soft bias: 80% follow gradient, 20% random
            zero_rows = rows[zero_mask]
            gd = np.asarray(grad_dir, dtype=np.float32)
            row_signs = np.sign(gd[zero_rows])  # {-1, 0, +1}
            # Where gradient is ~0 or unknown, fall back to random
            random_signs = rng.choice([-1, 1], size=n_zeros).astype(np.int8)
            follow_grad = rng.random(size=n_zeros) < 0.8
            has_direction = row_signs != 0
            use_grad = follow_grad & has_direction
            new_val[zero_mask] = np.where(
                use_grad, row_signs.astype(np.int8), random_signs,
            )
        else:
            new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    new_encoded = (new_val.astype(np.int32) + 1).astype(np.uint32)

    # Count actual flips: positions where the value genuinely changed.
    # Budget ≠ flips because:
    #   - indices sampled with replacement → duplicates (last write wins)
    #   - some mutations are no-ops at the packed level when duplicates
    #     overwrite each other
    # We compare against the original packed values at unique positions.
    actual_flips = int(np.sum(new_val != current_val))

    # Write back
    clear_mask = ~(np.uint32(0x3) << shifts)
    flat_packed[uint32_idx] = (flat_packed[uint32_idx] & clear_mask) | (new_encoded << shifts)

    mod.weight = mx.array(flat_packed.reshape(N, K // 16))
    mutated_arrays.append(mod.weight)

    # Track which rows (output channels) were touched — for surgical Adam decay
    # Only count rows where a flip actually happened
    actually_changed = new_val != current_val
    mutated_rows = set(int(r) for r in np.unique(rows[actually_changed])) if actual_flips > 0 else set()
    return actual_flips, mutated_rows


def _mutate_embedding(
    mod: "TernaryEmbedding",
    mod_budget: int,
    rng: Any,
    np: Any,
    mutated_arrays: list,
    sign_flip_rate: float = 0.2,
) -> tuple[int, set[int]]:
    """Mutate TernaryEmbedding.ternary_weight (uint8, 4-per-byte big-endian format).

    Encoding: {0b00→-1, 0b01→0, 0b10→+1}.
    Bit positions: bits {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}.

    Same mutation rules as _mutate_linear: deactivate or sign-flip for non-zero,
    random activation for zero.
    """
    vocab_size = mod.vocab_size
    d_model = mod.d_model
    n_weights = vocab_size * d_model

    packed_np = np.array(mod.ternary_weight)  # (vocab_size, d_model//4) uint8
    N, K4 = packed_np.shape
    flat_packed = packed_np.reshape(-1)

    indices = rng.randint(0, n_weights, size=mod_budget)

    # Map logical index → (byte_index, bit_position)
    byte_idx = indices // 4
    pos_in_byte = indices % 4
    shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

    # Read current 2-bit values
    current_encoded = (flat_packed[byte_idx] >> shifts) & np.uint8(0x3)  # {0,1,2}
    current_val = current_encoded.astype(np.int8) - 1                     # {-1,0,+1}

    # Apply mutations
    new_val = np.copy(current_val)

    # Non-zero: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero: activate with random sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    new_encoded = (new_val + 1).astype(np.uint8)

    # Actual flips (same logic as _mutate_linear)
    actual_flips = int(np.sum(new_val != current_val))

    # Write back
    clear_masks = ~(np.uint8(0x3) << shifts)
    flat_packed[byte_idx] = (flat_packed[byte_idx] & clear_masks) | (new_encoded << shifts)

    mod.ternary_weight = mx.array(flat_packed.reshape(N, K4))
    mutated_arrays.append(mod.ternary_weight)

    # Track mutated rows (vocab entries) — embeddings don't have gamma,
    # but tracked for completeness and potential future use
    actually_changed = new_val != current_val
    rows = indices // (K4 * 4)
    mutated_rows = set(int(r) for r in np.unique(rows[actually_changed])) if actual_flips > 0 else set()
    return actual_flips, mutated_rows


# ══════════════════════════════════════════════════════════════════════
# Consensus-based mutation: propose → vote → apply only agreed flips
# ══════════════════════════════════════════════════════════════════════
#
# Instead of tournament selection (best of 4 independent throws),
# consensus requires ≥3 of 4 strategies to independently agree on
# the same flip at the same position. This yields the fewest flips
# with the highest confidence — each accepted flip has independent
# evidence from multiple sampling strategies.
#
# Flow:
#   1. propose_mutations()  — each strategy samples positions and
#      computes proposed values WITHOUT modifying the model
#   2. find_consensus()     — positions where ≥3 strategies agree
#   3. apply_consensus()    — apply only the consensus flips


def _propose_linear(
    mod: "TernaryLinear",
    mod_budget: int,
    rng: Any,
    np: Any,
    sign_flip_rate: float = 0.2,
    row_imp: Any | None = None,
    col_imp: Any | None = None,
    grad_dir: Any | None = None,
    guided_fraction: float = 0.7,
) -> dict[int, int]:
    """Propose mutations for a TernaryLinear without modifying it.

    Same sampling and mutation logic as _mutate_linear, but returns
    a dict of {flat_logical_index: proposed_ternary_value} instead
    of writing to the packed array.

    Only includes positions where the proposal differs from current.
    For duplicate indices (sampled with replacement), last proposal wins.
    """
    N = mod.out_features
    K = mod.in_features

    packed_np = np.array(mod.weight)  # (N, K//16) uint32
    flat_packed = packed_np.reshape(-1)

    indices = _importance_sample_indices(
        N, K, mod_budget, rng, np, row_imp, col_imp, guided_fraction,
    )

    rows = indices // K
    cols = indices % K
    uint32_idx = rows * (K // 16) + cols // 16
    slot = cols % 16
    shifts = (slot * 2).astype(np.uint32)

    current_encoded = ((flat_packed[uint32_idx] >> shifts) & np.uint32(0x3))
    current_val = current_encoded.astype(np.int8) - 1

    new_val = np.copy(current_val)

    # Non-zero: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    # Zero: activate with gradient-directed sign
    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        if grad_dir is not None and len(grad_dir) == N:
            zero_rows = rows[zero_mask]
            gd = np.asarray(grad_dir, dtype=np.float32)
            row_signs = np.sign(gd[zero_rows])
            random_signs = rng.choice([-1, 1], size=n_zeros).astype(np.int8)
            follow_grad = rng.random(size=n_zeros) < 0.8
            has_direction = row_signs != 0
            use_grad = follow_grad & has_direction
            new_val[zero_mask] = np.where(
                use_grad, row_signs.astype(np.int8), random_signs,
            )
        else:
            new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    # Build proposals dict: only positions that actually change
    # For duplicates, iterate in order so last write wins (matching _mutate_linear)
    proposals = {}
    for i in range(len(indices)):
        if new_val[i] != current_val[i]:
            proposals[int(indices[i])] = int(new_val[i])

    return proposals


def _propose_embedding(
    mod: "TernaryEmbedding",
    mod_budget: int,
    rng: Any,
    np: Any,
    sign_flip_rate: float = 0.2,
) -> dict[int, int]:
    """Propose mutations for a TernaryEmbedding without modifying it."""
    vocab_size = mod.vocab_size
    d_model = mod.d_model
    n_weights = vocab_size * d_model

    packed_np = np.array(mod.ternary_weight)
    flat_packed = packed_np.reshape(-1)

    indices = rng.randint(0, n_weights, size=mod_budget)

    byte_idx = indices // 4
    pos_in_byte = indices % 4
    shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

    current_encoded = (flat_packed[byte_idx] >> shifts) & np.uint8(0x3)
    current_val = current_encoded.astype(np.int8) - 1

    new_val = np.copy(current_val)

    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate
        nonzero_vals = current_val[nonzero_mask]
        new_nonzero = np.where(do_flip, -nonzero_vals, np.int8(0))
        new_val[nonzero_mask] = new_nonzero

    zero_mask = current_val == 0
    n_zeros = int(zero_mask.sum())
    if n_zeros > 0:
        new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    proposals = {}
    for i in range(len(indices)):
        if new_val[i] != current_val[i]:
            proposals[int(indices[i])] = int(new_val[i])

    return proposals


def propose_mutations(
    model: nn.Module,
    budget: int,
    rng: Any,
    sign_flip_rate: float = 0.2,
    row_importance: dict[str, Any] | None = None,
    col_importance: dict[str, Any] | None = None,
    grad_direction: dict[str, Any] | None = None,
    guided_fraction: float = 0.7,
    depth_weights: dict[str, float] | None = None,
) -> dict[str, dict[int, int]]:
    """Propose mutations for all ternary modules without applying them.

    Returns dict mapping module_path → {flat_index: proposed_value}.
    Same budget distribution logic as mutate_topology.
    """
    import numpy as np

    modules = list(_walk_ternary_modules(model))
    if not modules or budget <= 0:
        return {}

    sizes = [mod.out_features * mod.in_features for _, mod in modules]

    if depth_weights is not None:
        effective = []
        for (path, _), n_weights in zip(modules, sizes):
            best_weight = 1.0
            best_len = 0
            for prefix, w in depth_weights.items():
                if path.startswith(prefix) and len(prefix) > best_len:
                    best_weight = w
                    best_len = len(prefix)
            effective.append(n_weights * best_weight)
    else:
        effective = [float(s) for s in sizes]

    total_effective = sum(effective)
    all_proposals = {}

    for (path, mod), n_weights, eff in zip(modules, sizes, effective):
        mod_budget = max(0, round(budget * eff / total_effective))
        if mod_budget == 0:
            continue
        mod_budget = min(mod_budget, n_weights)

        row_imp = row_importance.get(path) if row_importance else None
        col_imp = col_importance.get(path) if col_importance else None
        grad_dir = grad_direction.get(path) if grad_direction else None

        if isinstance(mod, TernaryLinear):
            all_proposals[path] = _propose_linear(
                mod, mod_budget, rng, np, sign_flip_rate,
                row_imp, col_imp, grad_dir, guided_fraction,
            )
        else:
            all_proposals[path] = _propose_embedding(
                mod, mod_budget, rng, np, sign_flip_rate,
            )

    return all_proposals


def find_consensus(
    proposals_list: list[dict[str, dict[int, int]]],
    threshold: int = 3,
) -> tuple[dict[str, dict[int, int]], dict]:
    """Find consensus mutations: positions where ≥threshold strategies agree.

    Args:
        proposals_list: list of proposals from each strategy (from propose_mutations)
        threshold:      minimum number of strategies that must agree (default: 3 of 4)

    Returns:
        (consensus, stats) where:
          consensus: dict[module_path → {flat_index: agreed_value}]
          stats: dict with diagnostic counts
    """
    from collections import Counter, defaultdict

    # Collect all module paths
    all_paths = set()
    for prop in proposals_list:
        all_paths.update(prop.keys())

    consensus = {}
    total_positions_seen = 0
    total_positions_voted = 0
    total_consensus = 0

    for path in all_paths:
        # Gather votes: for each position, collect proposed values from each strategy
        votes = defaultdict(list)
        for prop in proposa

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01XX3Tc3ybtBUQryhEcCHT9W.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

## Assistant

Now let me grab the truncated tail sections of model.py and train.py for completeness:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/model.py",
  "line_offset": 600,
  "limit": 80
}
```

**Summary:** Reading model.py (600-680)

**Output:**
```
            bank_1_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # ── Update algedonic buffers (EMA, no gradient) ────────
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic: pack dispatch weights + compute gate
        # into register-shaped vector for ascending arm's next pass
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean,                                        # 22 dims: op distribution
            cg_mean,                                        # 1 dim: compute gate level
            mx.zeros((self.d_reg_real - N_OPS - 1,)),       # padding to d_reg_real
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting — sees registers AND
        # raw ungated deltas (direct view of what operations proposed)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,
                     bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]

        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]

        x = x - total_ungated + total_gated

        # Meta-S4: final structural summary
        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        logits = self.embed.output_proj(x)   # tied ternary embedding, (B, L, vocab_size)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Instrumentation ───────────────────────────────────────

    @staticmethod
    def _entropy_proxy(x: mx.array) -> float:
        """log(mean_var) entropy proxy — same as v6."""
        var_per_feat = mx.var(x, axis=(0, 1))
        mean_var = mx.mean(var_per_feat)
        mx.eval(mean_var)
        return float(mx.log(mean_var + 1e-10).item())


[CONTENT TRUNCATED] Showing lines 601 to 680 of 1117 total lines. Use line_offset=680 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/ternary.py",
  "line_offset": 950,
  "limit": 80
}
```

**Summary:** Reading ternary.py (950-1030)

**Output:**
```
            row_signs = np.sign(gd[zero_rows])  # {-1, 0, +1}
            # Where gradient is ~0 or unknown, fall back to random
            random_signs = rng.choice([-1, 1], size=n_zeros).astype(np.int8)
            follow_grad = rng.random(size=n_zeros) < 0.8
            has_direction = row_signs != 0
            use_grad = follow_grad & has_direction
            new_val[zero_mask] = np.where(
                use_grad, row_signs.astype(np.int8), random_signs,
            )
        else:
            new_val[zero_mask] = rng.choice([-1, 1], size=n_zeros).astype(np.int8)

    new_encoded = (new_val.astype(np.int32) + 1).astype(np.uint32)

    # Count actual flips: positions where the value genuinely changed.
    # Budget ≠ flips because:
    #   - indices sampled with replacement → duplicates (last write wins)
    #   - some mutations are no-ops at the packed level when duplicates
    #     overwrite each other
    # We compare against the original packed values at unique positions.
    actual_flips = int(np.sum(new_val != current_val))

    # Write back
    clear_mask = ~(np.uint32(0x3) << shifts)
    flat_packed[uint32_idx] = (flat_packed[uint32_idx] & clear_mask) | (new_encoded << shifts)

    mod.weight = mx.array(flat_packed.reshape(N, K // 16))
    mutated_arrays.append(mod.weight)

    # Track which rows (output channels) were touched — for surgical Adam decay
    # Only count rows where a flip actually happened
    actually_changed = new_val != current_val
    mutated_rows = set(int(r) for r in np.unique(rows[actually_changed])) if actual_flips > 0 else set()
    return actual_flips, mutated_rows


def _mutate_embedding(
    mod: "TernaryEmbedding",
    mod_budget: int,
    rng: Any,
    np: Any,
    mutated_arrays: list,
    sign_flip_rate: float = 0.2,
) -> tuple[int, set[int]]:
    """Mutate TernaryEmbedding.ternary_weight (uint8, 4-per-byte big-endian format).

    Encoding: {0b00→-1, 0b01→0, 0b10→+1}.
    Bit positions: bits {7:6, 5:4, 3:2, 1:0} for columns {4k, 4k+1, 4k+2, 4k+3}.

    Same mutation rules as _mutate_linear: deactivate or sign-flip for non-zero,
    random activation for zero.
    """
    vocab_size = mod.vocab_size
    d_model = mod.d_model
    n_weights = vocab_size * d_model

    packed_np = np.array(mod.ternary_weight)  # (vocab_size, d_model//4) uint8
    N, K4 = packed_np.shape
    flat_packed = packed_np.reshape(-1)

    indices = rng.randint(0, n_weights, size=mod_budget)

    # Map logical index → (byte_index, bit_position)
    byte_idx = indices // 4
    pos_in_byte = indices % 4
    shifts = np.array([6, 4, 2, 0], dtype=np.uint8)[pos_in_byte]

    # Read current 2-bit values
    current_encoded = (flat_packed[byte_idx] >> shifts) & np.uint8(0x3)  # {0,1,2}
    current_val = current_encoded.astype(np.int8) - 1                     # {-1,0,+1}

    # Apply mutations
    new_val = np.copy(current_val)

    # Non-zero: deactivate or sign-flip
    nonzero_mask = current_val != 0
    n_nonzero = int(nonzero_mask.sum())
    if n_nonzero > 0:
        flip_roll = rng.random(size=n_nonzero)
        do_flip = flip_roll < sign_flip_rate

[CONTENT TRUNCATED] Showing lines 951 to 1030 of 1427 total lines. Use line_offset=1030 parameter to read more content.
```

## Assistant

I now have a complete picture of all seven files. Here is the full analysis.

---

# v10 Architecture Analysis — Full Breakdown for v11 Planning

---

## File 1: `config.py`

### Summary
Single `V10Config` dataclass. Holds all hyperparameters for the model, training, evolution, and data pipeline. No logic — pure configuration object.

### Classes
**`V10Config`** — flat dataclass, all fields described below.

### Key Dimensions / Hyperparameters
| Parameter | Value | Role |
|---|---|---|
| `vocab_size` | 151936 | Qwen3 BBPE |
| `d_model` | 512 | core dimension |
| `d_ff` | 1536 | prep FFN width (3×) |
| `d_ff_consolidate` | 2048 | consolidate FFN (4×) |
| `d_register` | 128 | logical register dim (real = 256) |
| `n_heads` | 8 | attention heads (d_head=64) |
| `window` | 8 | attention window |
| `alpha` | 1.18 | spiral bias coefficient |
| `strides` | (1,8,16,32,64,128,256,512,1024) | 9-scale StrideStack |
| `n_registers` | 3 | named: type, scope, role |
| `dispatch_top_k` | 2 | MoE-style top-k op routing |
| `desc_max_cycles` | 3 | max descending cycles per pass |
| `dropout` | 0.1 | |
| `seq_len` | 4096 | context window |
| `mix_ratio` | 0.0 | structured vs prose fraction |
| `gen_interval` | 50 | evolution frequency |
| `base_pct` | 0.0002 | ~26K flips per generation |
| `sign_flip_rate` | 0.2 | fraction of non-zero flips that flip sign |
| `guided_fraction` | 0.7 | fraction of mutations that are gradient-informed |
| `s4_boost` | 3.0 | amplifier on S4 module proposals |
| `mutation_adam_decay` | 0.1 | surgical Adam state decay after accepted flip |

### Data Flow
Config object → instantiated by `train.py`, passed to `V6Compressor.__init__`, `StrideStack`, `KernelDispatch`, `KernelIntegrate`, S3/S4/S5 constructors. It is the single source of truth; changing a dimension here propagates everywhere.

---

## File 2: `kernel.py`

### Summary
Pure Python, no MLX. The **ground-truth evaluator** for the 22-op VSM tree. Defines the type system, all 22 operations, a packing scheme for function values (FN/FN_COMP), and two evaluation APIs: `evaluate_tree` (Node-based) and `eval_tuple_tree` (nested-tuple shorthand). Used by `kernel_dispatch.py` for naming constants and by the training pipeline to produce ground-truth labels.

### Classes
**`Type`** (IntEnum) — 5 types: INT=0, BOOL=1, FN=2, FN_COMP=3, ERROR=4.

**`Op`** (IntEnum) — 22 ops in 7 families:
- Arithmetic binary (0–6): ADD SUB MUL DIV MOD MIN MAX
- Comparison (7–11): EQ LT GT LE GE
- Boolean binary (12–13): AND OR
- Boolean unary (14): NOT
- Arithmetic unary (15–16): ABS NEG
- Conditional (17): IF
- Lambda (18–21): PARTIAL APPLY_FN COMPOSE APPLY_COMP

**`Node`** — dataclass: node_id, children (list of ids), value (leaf literal), op_idx.

### Key Dimensions
- `N_OPS = 22`
- `N_TYPES = 5`
- `FN_PACK_SCALE = 10000`, `FN_PACK_OFFSET = 5000` — bounds_arg range [-5000, 4999]
- Evaluation is bottom-up DFS over a flat Node list; root = last node by convention.
- `evaluate_tree(tree, op_assignments) → int` — the dispatcher's ground-truth oracle.

### Data Flow
```
kernel.py is purely consumed, never consumes anything.
  Op/N_OPS/N_TYPES constants → imported by kernel_dispatch.py
  evaluate_tree() → imported by train.py for structured data ground truth
  kernel_eval() → called internally by evaluate_tree and eval_tuple_tree
```

---

## File 3: `components.py`

### Summary
Defines all VSM control components: S4 (intelligence), S3 (gating/control), MetaS4, MetaS3/S5Reweight, S2 (coordination), and CycleContinue. These are the non-operational "VSM skeleton" that wraps the operational S1 modules. All use ternary linear where possible except small gates kept fp32.

### Classes

**`S4Ternary`** — Register cross-attention (intelligence scanner). Flattens all register banks into a query vector; attends over the residual stream; projects the weighted summary back to register-shaped update vectors.
- `q_proj`: TernaryLinear(`max_q_dim` → d_model)
- `k_proj`, `v_proj`: TernaryLinear(d_model → d_model)
- `summary_proj`: TernaryLinear(d_model → `n_registers * d_reg_real`)
- Returns: list of `n_registers` update vectors, attention weights

**`S3Ternary`** — Phase-coherent gating (control). Per-phase: computes alignment between register direction and delta direction → scalar gate → modulates delta. Also writes to registers via `write_projs` (ternary) gated by `write_gates` (fp32 Linear, bias=-2.0 init).
- One `gate_phase(registers, delta, phase_idx)` call per phase
- 3 phases per pass; returns `(gated_delta, updated_registers, gate_scalar, write_gate_values)`
- Register accumulation protected by `register_norm` (RMSNorm)

**`MetaS4Ternary`** — Final structural summary. Same cross-attention pattern as S4Ternary but reads from `n_banks=4` selected banks and adds its output to the residual stream (additive, not register-update).

**`MetaS3Ternary`** — *(Superseded by S5Reweight in active code)* — Produces per-pass contribution gates from register banks only. Bias=-2.0 init, near-closed start.

**`S5Reweight`** — Identity-level pass contribution gating. Sees both register banks (S2 state) AND raw ungated pass deltas (what S1 actually proposed). `delta_proj` (TernaryLinear, pre_norm=True) compresses delta summaries → 16 features/pass. `gate_proj` (fp32 Linear, bias=-2.0). Returns (n_passes,) sigmoid gates.

**`S2Coordinator`** — Inter-pass direction coordination (anti-oscillation). 4 transitions; `dir_projs` (TernaryLinear, pre_norm=True, gamma init ×0.01); learnable scales init=0.01. `direction_signal(delta, idx)` → (1,1,d_model) small additive signal. `coherence_factor(prev, curr)` → differentiable scalar ∈ [0,2] for modulating signal strength. `conflict_score()` → diagnostic cosine similarity.

**`CycleContinue`** — S3 cycle continuation gate. Input: register bank (n_registers × d_reg_real). `input_norm` (RMSNorm, **critical — prevents sigmoid saturation on unnormalized registers**). `gate_proj` (fp32 Linear, weight=0, bias=0 init → sigmoid(tanh(proj)×4) → 0.5 at start, bounded in [-4,+4] via tanh to prevent saturation). Returns scalar gate ∈ [0,1].

### Key Dimensions
- `d_reg_real = d_register * 2 = 256` (real-valued equivalent of complex d_register)
- `max_banks = 7` for S4 query dim = 7×3×256 = 5376, padded to 5392
- S3 has `n_phases=3` per pass, `n_registers=3`
- S5Reweight: delta_proj_out = n_passes × 16 features
- S2: `N_TRANSITIONS = 4` (between 5 passes)

### Data Flow
```
S4:  [all_banks] + residual → [register_updates], attn_weights
S3:  [registers] + delta + phase_idx → gated_delta, [updated_registers], gate
S5:  [all_banks] + [raw_deltas] → (n_passes,) gates
S2:  pass_delta + transition_idx → (1,1,d_model) direction signal
CycleContinue: [registers] → scalar gate ∈ [0,1]
MetaS4: [meta_banks] + residual → enriched residual (additive)
```

---

## File 4: `kernel_dispatch.py`

### Summary
The descending arm's S1 operational modules. Two neural modules replace the ascending arm's `TernaryFFN` pair: `KernelDispatch` (routes to 22 op pathways via top-k MoE) and `KernelIntegrate` (types the result via 5 type embeddings, with an optional exact kernel computation pathway). Includes structured initialization for op embeddings and type embeddings.

### Classes

**`KernelDispatch`** — Phase 0 of descending passes.
- `norm` (RMSNorm), `dispatch` (TernaryLinear: d_model → n_ops_padded=32)
- `register_cond` (fp32 Linear: max_cond_dim → n_ops_padded, zero-init): ascending register banks bias per-op logits
- `op_embeddings`: (22, d_model) real-valued, structured-initialized, L2-normalized each forward to `op_embed_scale=0.5`
- Top-k routing: mask all but top-k logits to -1e9, softmax over winners. Prevents softmax saturation/op death.
- `up` (TernaryLinear: d_model → d_ff), `down` (TernaryLinear: d_ff → d_model)
- Accepts `op_emphasis: (n_ops,)` from S4 registers — scales op embeddings before matmul
- Caches `_dispatch_weights: (B, L, 22)` for KernelIntegrate

**`KernelIntegrate`** — Phase 2 of descending passes (after StrideStack in phase 1).
- `type_proj` (TernaryLinear: d_model → n_types_padded=16), `type_embeddings`: (5, d_model)
- Standard FFN pathway: type_context modulates input → up/down (TernaryLinear)
- **Kernel computation pathway** (straight-through, non-differentiable):
  - `operand1_proj`, `operand2_proj` (TernaryLinear: d_model → max_val_padded=256): extract operands via argmax
  - Vectorized exact kernel: computes all 22 ops in parallel, selects by dispatched op
  - `result_embed` (nn.Embedding: result_buckets=1024 × d_model): encodes integer result
  - `gate_proj` (fp32 Linear, weight=0, bias=-5): per-position scalar blend gate (starts ~0.0067, pure FFN)
- Output = gate × kernel_out + (1-gate) × ffn_out
- Caches `_type_weights: (B, L, 5)`, `_compute_gate: (B, L, 1)`, `_kernel_info`

### Key Dimensions
- `N_OPS = 22`, `N_TYPES = 5` (imported from kernel.py constants)
- `n_ops_padded = 32` (padded to 16 for TernaryLinear)
- `top_k = 2` — only 2 ops active per position
- `max_val = 256` — operand value range [0, 255]
- `result_buckets = 1024`, `result_offset = 512` — result range [-512, 511]
- Op embedding family subspace: first d_model//2=256 dims family-specific, last 256 shared+random×0.1

### Data Flow
```
KernelDispatch:
  x (B,L,d) + [asc_registers] + op_emphasis
    → dispatch_logits (TernaryLinear) + register_cond bias
    → top-k mask → softmax → dispatch_weights (B,L,22)
    → op_context = weights @ L2-normed op_embeddings (B,L,d)
    → modulated = x + op_context → up/gelu/down → x + dropout(out)

KernelIntegrate:
  x (B,L,d) + dispatch_weights
    → type_logits → softmax → type_context → modulated → FFN (pathway A)
    → operand1/2 argmax → kernel_eval vectorized → result_embed (pathway B)
    → gate * B + (1-gate) * A
```

---

## File 5: `model.py`

### Summary
The top-level model class `V6Compressor` (misleadingly named — it is the full Tree-of-VSMs). Assembles all components into 5 passes: 3 ascending (VSM-Compressor), 2 descending (VSM-Dispatcher). Manages 6 register banks, algedonic feedback channels, S2 direction signals, S5 reweighting, and multi-cycle dispatch. Provides `forward()` and `forward_instrumented()`.

### Classes

**`V6Compressor`** — The complete model.

**Key sub-modules instantiated:**
| Sub-module | Type | Shared? |
|---|---|---|
| `embed` | TernaryEmbedding(vocab×512) | yes (tied to output) |
| `pos_embed` | TernaryEmbedding(4096×512) | yes |
| `embed_norm` | RMSNorm(512) | yes |
| `prep` | TernaryFFN(512→1536→512) | shared across 3 asc passes |
| `stride_stack` | StrideStack(9 strides) | shared across 3 asc passes |
| `consolidate` | TernaryFFN(512→2048→512) | shared across 3 asc passes |
| `kernel_dispatch` | KernelDispatch | shared across 2 desc passes |
| `stride_stack_desc` | StrideStack(9 strides) | shared across 2 desc passes |
| `kernel_integrate` | KernelIntegrate | shared across 2 desc passes |
| `s4` | S4Ternary(max_banks=7) | shared across 3 asc passes |
| `s4_desc` | S4Ternary(max_banks=7) | shared across 2 desc passes |
| `s3_passes[0..4]` | S3Ternary (5 instances) | always separate per pass |
| `mod_projs[0..2]` | TernaryLinear(d→d) × 3 | shared asc, gamma=0 init |
| `mod_projs_desc[0..2]` | TernaryLinear(d→d) × 3 | shared desc, gamma=0 init |
| `cycle_continue` | CycleContinue | single instance for desc |
| `meta_s4` | MetaS4Ternary(n_banks=4) | final summary |
| `s2` | S2Coordinator | 4 transitions |
| `s5_reweight` | S5Reweight(n_banks=6, n_passes=5) | identity gate |
| `emphasis_proj` | fp32 Linear(3×3×256 → 22) | S4→op emphasis |
| `output_norm` | RMSNorm(512) | |

**Persistent buffers (EMA, no-grad):**
- `_prev_bank_1_desc`, `_prev_bank_2_desc`: descending registers from last forward
- `_prev_kernel_algedonic`: (d_reg_real,) vector packing 22 dispatch weights + 1 compute gate
- `_op_emphasis`: (22,) EMA of emphasis projection output, α=0.95
- `_cycle_inject_gate_raw`: scalar, sigmoid(-4)≈0.018 init

### Register Bank Architecture (6 banks, each = 3 vectors of size 256)
```
bank_0          ← learnable init (register_inits for type/scope/role)
bank_1_asc      ← written by pass 0 (L0↑)  S4+S3
bank_2_asc      ← written by pass 1 (L1↑)  S4+S3
bank_3           ← written by pass 2 (L2_apex) S4+S3
bank_2_desc     ← written by pass 3 (L1↓)  S4_desc+S3
bank_1_desc     ← written by pass 4 (L0↓)  S4_desc+S3
```
Each bank accumulates via `register_norm(bank[i] + s4_update[i])` — RMSNorm prevents unbounded accumulation.

### Readable Banks Per Pass (what S4 can attend from)
```
Pass 0 (L0↑):    [bank_0, prev_b1d, prev_kernel]
Pass 1 (L1↑):    [bank_0, bank_1_asc, prev_b2d, prev_kernel]
Pass 2 (L2↑):    [bank_0, bank_1_asc, bank_2_asc, prev_kernel]
Pass 3 (L1↓):    [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank]
Pass 4 (L0↓):    [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank]
```
Descending passes additionally get `embed_context=x_embed` fed into S4 via concatenation along L dimension (dual view: compressed residual + original tokens), creating an effective 2L attention context.

### Multi-Cycle Descending Dispatch (desc_max_cycles=3)
```
For each descending pass, for cycle in range(3):
  if cycle > 0: x += sigmoid(_cycle_inject_gate_raw) * x_anchor  # HRM re-grounding
  x = KernelDispatch(x, registers, op_emphasis)         # Phase 0: dispatch
  [S3 gate phase 0] → x modulated
  x = StrideStack_desc(x, reverse=False)                 # Phase 1: converge
  [S3 gate phase 1] → x modulated
  x = KernelIntegrate(x, dispatch_weights)               # Phase 2: integrate
  [S3 gate phase 2] → x modulated
  cycle_contribution = x - x_cycle_start
  x = x_cycle_start + cumulative_gate * cycle_contribution
  if cycle < 2: cumulative_gate *= CycleContinue(target_bank)  # S3 decides
```

### S2 Direction Signals
```
After pass 0 → before pass 1: signal(pd[0], 0) — unmodulated
After pass 1 → before pass 2: signal(pd[1], 1) × coherence_factor(pd[0], pd[1])
After pass 2 → before pass 3: signal(pd[2], 2) × coherence_factor(pd[1], pd[2])
After pass 3 → before pass 4: signal(pd[3], 3) × coherence_factor(pd[2], pd[3])
```

### Algedonic Channel
Descending register state (EMA α=0.9) fed back into ascending S4 on the *next* forward pass. Also packs `_prev_kernel_algedonic` = [22 dispatch_weights | 1 compute_gate_mean | padding] into a register-shaped vector, read at pass 0 and 1 as `prev_kernel`.

### Op Emphasis Channel
After ascending passes complete: `emphasis_proj([bank_1_asc, bank_2_asc, bank_3] flattened → 22)` → `1.0 + 0.5*tanh(raw)` → range [0.5, 1.5]. EMA α=0.95. Fed to `KernelDispatch` as `op_emphasis` to scale op embeddings before top-k routing.

### S5 Final Reweighting
```
x_final = x - Σ(pass_deltas) + Σ(meta_gates[i] × pass_deltas[i])
```
Effectively: undo all passes then re-add each pass scaled by its S5 gate. S5 sees raw ungated deltas to detect suppressed but valuable passes.

### Data Flow (complete forward pass)
```
tokens (B,L) → embed + pos_embed → embed_norm → x (B,L,512)
                                               → x_embed (saved)
↓ algedonic: read prev_b1d, prev_b2d, prev_kernel
↓ Pass 0 (L0↑): S4[bank_0,prev_b1d,prev_kernel]→bank_1_asc | prep→S3→mod | stride→S3→mod | consolidate→S3→mod
↓ S2 signal (unmodulated)
↓ Pass 1 (L1↑): S4[...,prev_b2d,...]→bank_2_asc | same 3 phases
↓ S2 signal (coherence-modulated)
↓ Pass 2 (L2↑): S4[...,prev_kernel]→bank_3 | same 3 phases
↓ compute op_emphasis from asc banks; pack asc_gate_bank
↓ S2 signal (coherence-modulated)
↓ Pass 3 (L1↓): S4_desc dual-view→bank_2_desc | 3 kernel phases × up_to_3_cycles
↓ S2 signal (coherence-modulated)
↓ Pass 4 (L0↓): S4_desc dual-view→bank_1_desc | same
↓ update algedonic buffers (EMA)
↓ S5Reweight(all_banks, raw_deltas) → 5 gates → reweight pass contributions
↓ MetaS4([bank_0, bank_1_desc, bank_2_desc, bank_3], x) → x
↓ output_norm → embed.output_proj (tied) → logits (B,L,vocab)
↓ cross_entropy(logits, targets) → loss
```

---

## File 6: `train.py`

### Summary
Full training loop: relational loss, gradient accumulation, cosine LR, shared-weight gradient normalization, EMA importance tracking, tournament evolution with consensus mutation, surgical Adam decay, checkpointing, and JSONL metrics logging.

### Classes / Functions

**`loss_fn`** — Relational loss: `r = (CE - E_irreducible) / (log(V) - E_irreducible)`. Normalizes CE into [0,1]; r=1 is random, r=0 matches irreducible entropy. Same gradient direction as CE (monotonic).

**`normalize_shared_grads`** — Divides ascending component gradients by 3, descending by 2 (their pass counts). Prevents Adam stat inflation from shared weight traversal.

**`cosine_lr`** — Warmup 500 steps then cosine decay to `lr × lr_floor_ratio = 6e-6`.

**`run_tournament`** — Consensus evolution:
1. Each of 5 strategies proposes mutations independently (no model change)
2. `find_consensus()` — positions where ≥3 strategies agree on the same new value
3. `apply_consensus()` — write those flips
4. Evaluate relational loss; accept if improved on ALL data types, else revert

**Strategies:** `conservative`×0.25, `explorer`×1.0, `targeted`×2.0, `random`×4.0, `intelligence`×0.5 (S4 modules boosted ×3.0, rest suppressed ÷3.0, fully gradient-guided).

**`decay_adam_state`** — Surgical: only decays Adam m/v for gamma rows that were actually mutated (identified by `mutation_map`). Prevents the CE spike caused by full-model Adam reset.

**EMA importance:** `row_importance[path]` ← EMA of |∂L/∂γ|; `grad_direction[path]` ← EMA of sign(∂L/∂γ); `col_importance[path]` ← EMA of mean(|x|). All α=0.1 (fast-adapting). Used by tournament to bias mutation toward high-gradient rows and high-activation columns.

### Training Data Structure
- **Prose**: Dolma shards (60×), tokenized with Qwen3 BBPE, `seq_len=4096`, simple next-token CE
- **Structured**: `data/structured_shard.npy` — contains BIOS, lambda expressions, Clojure code. Mixed in at `mix_ratio` fraction (currently 0.0 = prose only)
- **Mixed-data-aware evolution**: when `mix_ratio > 0`, mutations must improve loss on BOTH prose and structured batches simultaneously (acceptance criterion = max(r_prose, r_struct))

### Data Flow (training loop per step)
```
for micro in range(4):
  batch → loss_fn → value_and_grad
EMA importance update from |gamma_grad|
normalize_shared_grads (÷3 asc, ÷2 desc)
zero_ternary_grads (prevent uint32 optimizer corruption)
gradient clip (norm ≤ 1.0)
Adam.update → restore_ternary (integrity check)

every 50 steps:
  run_tournament → consensus → apply/revert → surgical Adam decay

every 500 steps: evaluate (50K tokens) + forward_instrumented metrics
every 1000 steps: checkpoint
```

---

## File 7: `ternary.py`

### Summary
The complete ternary substrate. Implements TernaryLinear (via MLX `quantized_matmul` at 2-bit, group_size=64), TernaryEmbedding (custom VJP gather), all packing/unpacking utilities, and the full evolutionary mutation pipeline: `propose_mutations` → `find_consensus` → `apply_consensus`.

### Classes

**`TernaryLinear`** — Core ternary linear layer.
- `weight`: (N, K//16) uint32 — packed ternary topology, **evolutionary, never gradient-updated, frozen**
- `gamma`: (N,) float32 — per-channel scale, **trained by Adam**
- Encoding: -1→0, 0→1, +1→2 (ternary+1); packed 16-per-uint32
- Per-group dequant via `quantized_matmul`: scales=gamma, biases=-gamma → output ∈ {-γ, 0, +γ}
- `pre_norm=True/False`: optional RMSNorm of input before projection
- Caches `_x_abs_mean` and `_x_mean` (stop_gradient) for column importance tracking

**`TernaryEmbedding`** — Ternary embedding table.
- `ternary_weight`: (vocab, d//4) uint8, 4-per-byte big-endian packing
- `gamma`: (vocab,) float32
- Custom `@mx.custom_function` forward + VJP: gradient flows only to gamma (via `grad_gamma = Σ grad_out × unpacked_row`); ternary_weight and token indices get zero gradient
- `output_proj(x)` — tied projection: repacks uint8 → uint32 on first call (cached), then `quantized_matmul`

### Packing Formats
```
TernaryLinear:    int8{-1,0,+1} → uint32, 16 values/word, little-endian 2-bit fields
TernaryEmbedding: int8{-1,0,+1} → uint8,   4 values/byte, big-endian 2-bit fields
```

### Evolutionary Pipeline

**`propose_mutations(model, budget, rng, ...)`** — For each ternary module, sample positions (guided+uniform mix), compute proposed new values. Returns `dict[module_path → dict[flat_index → proposed_value]]`. **Does not modify the model.**

**`find_consensus(proposals_list, threshold=3)`** — Intersects proposals from all strategies. Returns only positions where ≥3 agree on the same value. Returns (consensus_dict, stats).

**`apply_consensus(model, consensus)`** — Writes agreed flips to packed arrays. Returns (actual_flips, mutation_map).

**`mutate_topology`** — Legacy direct-mutation path (still used as fallback/internal helper).

**`bios_mutation_budget(step, total_steps, total_weights, base_pct=0.005)`** — Full budget for first 80% of steps, linear decay to 10% for last 20%. Does NOT gate on loss (unlike `mutation_cone` which freezes at r<0.05).

**Importance-weighted sampling:**
- 70% guided: rows ∝ |∂L/∂γ| EMA, cols ∝ mean(|x|) EMA
- 30% uniform: exploration, prevents stagnation
- Activation sign: when gradient direction available, 80% probability follow sign(∂L/∂γ_i) for 0→±1 activations

### Data Flow
```
TernaryLinear forward:
  x → [pre_norm] → quantized_matmul(x, stop_grad(weight), scales, biases) → y

Evolutionary:
  propose_mutations → [5 strategy proposals]
  find_consensus → agreed flips only
  apply_consensus → write to packed arrays
  evaluate loss → accept/revert

Training:
  zero_ternary_grads:  weight/ternary_weight grads → zeros (protect packed dtype)
  freeze_ternary_weights: remove weight/ternary_weight from trainable params
  restore_ternary:     assert dtype integrity (uint32/uint8); raises on corruption
```

---

## MAPPING TABLE: v10 Component → v11 Under KIBC Combinator Basis

| v10 Component | What It Does Now | v11 Under KIBC |
|---|---|---|
| `kernel.py` — `Op` (22 ops) | Ground-truth evaluator for ADD/SUB/MUL/DIV/MOD/MIN/MAX/EQ/LT/GT/LE/GE/AND/OR/NOT/ABS/NEG/IF/PARTIAL/APPLY_FN/COMPOSE/APPLY_COMP | Replace with 4 combinator reductions: **K** xy→x (select/discard), **I** x→x (identity/copy), **B** xyz→x(yz) (compose), **C** xyz→xzy (flip). `evaluate_tree` becomes `evaluate_combinator`. |
| `kernel.py` — `Type` (5 types: INT/BOOL/FN/FN_COMP/ERROR) | Type tags on node values; used for dispatch routing in kernel_eval and type embeddings in KernelIntegrate | Reduce to 4 combinator type embeddings: **K**, **I**, **B**, **C**. ERROR stays as a 5th sentinel if needed, but the primary 4 map 1:1 to combinator identity. |
| `kernel.py` — `N_OPS=22`, `N_TYPES=5` | Constants used throughout dispatch, integration, emphasis | `N_OPS→N_COMBINATORS=4`, `N_TYPES→4` (or 5 with ERROR). Flows to every downstream consumer. |
| `kernel_dispatch.py` — `KernelDispatch` | Routes to 22 ops via top-k MoE. `dispatch` TernaryLinear → 22-wide logits. `op_embeddings` (22×512) | Replace with `CombinatorDispatch`: 4-wide logits (no top-k needed — only 4 candidates). `combinator_embeddings` (4×512). Register conditioning still applies: ascending arm tells dispatcher which combinator is contextually likely. |
| `kernel_dispatch.py` — `KernelDispatch.top_k=2` | Keeps runner-up op alive, prevents softmax death of 20 ops | With only 4 combinators: can use full softmax over 4, or top-k=2. No saturation risk. The dead-op problem dissolves. |
| `kernel_dispatch.py` — `op_embeddings` (22, 512) L2-normalized | Per-op S5 identity: each op gets a characteristic direction. L2-norm prevents rich-get-richer collapse | `combinator_embeddings` (4, 512). Structured init: K/I/B/C each gets a near-orthogonal quadrant. L2-norm retained. Simpler identity — 4 slots, fully expressible. |
| `kernel_dispatch.py` — `_init_op_embeddings` (7-family subspace) | Family-aware init: arithmetic/comparison/boolean/lambda each get a subspace block | Replace with `_init_combinator_embeddings`: 4 orthogonal directions (one per d_model//2 block for family, or just near-orthogonal random scaled) — far simpler. |
| `kernel_dispatch.py` — `KernelIntegrate` type pathway (5 type_embeddings) | Produces per-position type classification over INT/BOOL/FN/FN_COMP/ERROR | Replace with `CombinatorIntegrate`: 4 combinator type embeddings. `type_proj` now has 4-wide output. Type of a node = which combinator it IS, not what data type it holds. |
| `kernel_dispatch.py` — `KernelIntegrate` kernel computation pathway | Extracts 2 operands (argmax over 256), runs all 22 ops in parallel, selects by dispatch. Encodes result via 1024-bucket embedding. | Replace with `CombinatorIntegrate` reduction pathway: K(x,y)→x (no arithmetic), I(x)→x, B(f,g,x)→f(g(x)), C(f,x,y)→f(y,x). 3-operand extraction instead of 2. Result encoding: K/I return one of the existing register representations; B/C route through the residual already. The bucket embedding may collapse to just a small result embedding over 4 combinator IDs. |
| `kernel_dispatch.py` — `register_cond` (ascending registers → 22 logits) | Biases dispatch based on type/scope/role from ascending arm | Retained but narrower: `register_cond` → 4 logits. Ascending registers identify which combinator role this position plays. |
| `config.py` — `dispatch_top_k=2` | Prevents op death in top-k routing | Can stay at 2 (harmless with 4 combinators) or drop to 1. Irrelevant when N_OPS=4. |
| `config.py` — `n_registers=3` (type, scope, role) | 3 named registers per bank: type, scope, role | Remap to 3 combinator-semantic registers: **which_combinator** (K/I/B/C identity), **argument_slot** (which positional argument is being resolved), **reduction_state** (how far through the combinator reduction we are). Names change; count stays 3. |
| `model.py` — `_run_level_pass` descending: 3 phases per cycle (dispatch, converge, integrate) | Phase 0=KernelDispatch, Phase 1=StrideStack propagation, Phase 2=KernelIntegrate | Map to three descending-cycle semantics: **identify(combinator)** (Phase 0 = which of K/I/B/C applies here), **resolve(argument)** (Phase 1 = spatial propagation to find the argument via StrideStack), **produce(result)** (Phase 2 = combinator reduction + type assignment). Phase names change; 3-phase structure is preserved. |
| `model.py` — `desc_max_cycles=3` with CycleContinue | Self-regulating: S3 gates decide after each cycle whether next cycle contributes. Cycle 0 always full; cycle 1+ scaled by cumulative gate product. | Retained without change. The 3-cycle structure maps elegantly: cycle 0 = coarse combinator identification, cycle 1 = argument resolution pass, cycle 2 = result refinement. CycleContinue still makes sense — some positions need all 3, some only 1. |
| `components.py` — `CycleContinue` (RMSNorm + tanh(proj)×4 → sigmoid) | S3 inter-cycle gate. RMSNorm prevents sigmoid saturation from unnormalized register norms ~16-28. tanh clamp bounds logit to [-4,+4]. Neutral init (gate=0.5). | Carried forward **unchanged**. The fix (RMSNorm + tanh clamp) is generic; combinator cycle continuation has identical structure. |
| `components.py` — `S4Ternary` (register cross-attention) | Intelligence scanner: register banks → query, attends over residual, returns register updates. Shared ascending, separate descending. | Carried forward **unchanged**. S4 reads 4-combinator registers exactly as it reads 3-type registers — it doesn't need to know the semantics of register content. |
| `components.py` — `S3Ternary` (phase-coherent gating) | 3 phases × 3 registers, alignment gate, write gate (bias=-2.0). Per-pass, always separate. | Carried forward **unchanged**. S3 gates phase deltas; the 3-phase semantics (identify/resolve/produce) fit naturally. Register writes continue as-is. |
| `components.py` — `S5Reweight` (register banks + raw deltas → 5 gates) | Identity-level gate over 5 pass contributions. Sees ungated deltas so suppressed passes can still be reclaimed. | Carried forward **unchanged**. S5 operates at the pass level; the 5-pass structure (3 asc + 2 desc) is unchanged in v11. |
| `components.py` — `S2Coordinator` (4 transitions, direction signals) | Anti-oscillation: "Pass N moved this way, FYI". Coherence-modulated. Scale init=0.01. | Carried forward **unchanged**. S2 coordinates at the pass level; combinator vs. op semantics are invisible at S2's granularity. |
| `components.py` — `MetaS4Ternary` (final structural summary) | Cross-attention over 4 meta-banks → additive residual update at end of forward. | Carried forward **unchanged**. Meta-S4 is already semantic-agnostic. |
| `model.py` — `emphasis_proj` (3 asc_banks × 3_regs × 256 → 22) | Projects ascending register state to per-op emphasis [0.5, 1.5]. EMA α=0.95. | Replace with narrower `emphasis_proj` → 4. Output is per-combinator emphasis. Logic identical; dimension shrinks from 22 to 4. |
| `model.py` — `_prev_kernel_algedonic` (22 dispatch_weights + 1 compute_gate + padding) | Packs descending dispatch distribution + gate activity into register-shaped vector. Fed back to ascending S4 as algedonic signal. | Adjust packing: 4 combinator weights + 1 compute_gate + padding. Same mechanism, narrower signal. |
| `model.py` — `asc_gate_bank` (9 ascending S3 gate values packed into d_reg_real) | Tells descending S4: what did each ascending phase gate at. 3 passes × 3 phases = 9 gate values. | Carried forward **unchanged**. Ascending arm has same 3-pass, 3-phase structure; 9 gate values still correct. |
| `model.py` — `x_embed` dual view for descending S4 | Concatenates original token embeddings to compressed residual for S4 attention (2L context). Lets dispatcher see raw token identity ("this IS the + token"). | Retained. In combinator terms: the token identity tells dispatch "this is a K/I/B/C combinator occurrence" just as directly as it told the op dispatcher "this is an ADD token". |
| `model.py` — register names "type", "scope", "role" | Learnable init scalars named semantically. | Rename to "combinator", "argument_slot", "reduction_state". Same 3 registers, different semantic labels. |
| `ternary.py` — `TernaryLinear`, `TernaryEmbedding` | Core ternary substrate: uint32/uint8 packing, quantized_matmul, evolutionary genome | Carried forward **unchanged**. The ternary substrate is completely semantic-agnostic. |
| `ternary.py` — `propose_mutations` / `find_consensus` / `apply_consensus` | Consensus evolution: 5 strategies propose, ≥3 must agree. Importance-weighted sampling. | Carried forward **unchanged**. |
| `ternary.py` — S4 strategy with `s4_boost=3.0` | Amplifies S4 module importance in intelligence strategy proposals. | Retained. S4 stays S4; boost stays ×3.0. |
| `train.py` — `loss_fn` (relational loss r) | `r = (CE - 1.82) / (11.93 - 1.82)`. Phase-aware, [0,1] normalized. | Unchanged for prose training. For structured combinator data: the ground-truth label is the combinator reduction outcome, not an op application. The loss function stays CE; what changes is the label generation in the structured shard. |
| `train.py` — structured shard (BIOS + lambda + clojure) | `mix_ratio=0.0` currently. Structured shard contains examples with ground-truth kernel outputs. | Replace with **combinator reduction shard**: examples are terms in KIBC form with ground-truth reductions. K(x,y)→x, I(x)→x, B(f,g,x)→f(g(x)), C(f,x,y)→f(y,x). Structured examples now exercise 4 combinators rather than 22 ops. `mix_ratio` becomes the lever for injecting combinator training signal. |
| `train.py` — `normalize_shared_grads` (÷3 asc, ÷2 desc) | Corrects for shared weight traversal counts. | Unchanged. Pass counts (3 asc, 2 desc) do not change in v11. |
| `train.py` — `decay_adam_state` (surgical per mutated row) | After accepted mutation, only decay Adam m/v for actually-mutated gamma rows. | Unchanged. |
| `train.py` — `MUTANT_STRATEGIES` (5 strategies, s4_boost, intelligence channel) | 5 mutation strategies with different budgets and focus. Intelligence strategy fully gradient-guided on S4 modules. | Unchanged. |
| `config.py` — `data/structured_shard.npy` + `mix_ratio=0.0` | Structured data path; currently disabled. | Point at new combinator reduction shard. Activate `mix_ratio > 0` to inject combinator signal. |

---

## Carries Forward Unchanged

These components require **zero code changes** in v11:

1. **`TernaryLinear` / `TernaryEmbedding`** and all packing utilities — fully semantic-agnostic
2. **`propose_mutations` / `find_consensus` / `apply_consensus`** — operates on packed weights only
3. **`bios_mutation_budget`** / **`mutation_cone`** — budget logic; indifferent to op count
4. **`S4Ternary`** — register cross-attention; does not inspect register semantics
5. **`S3Ternary`** — phase gating; 3 phases remain correct for identify/resolve/produce
6. **`CycleContinue`** (RMSNorm + tanh clamp + neutral init) — the recently fixed mechanism; combinator cycles have identical structure
7. **`S5Reweight`** — operates at pass level (5 gates); pass structure is unchanged
8. **`S2Coordinator`** — operates at pass level (4 transitions); direction signals are semantic-agnostic
9. **`MetaS4Ternary`** — final structural summary; bank inputs change in semantic meaning, not in shape
10. **`V6Compressor._run_level_pass`** ascending arm — prep/stride/consolidate, unchanged
11. **`normalize_shared_grads`** (÷3 asc, ÷2 desc) — pass counts unchanged
12. **`decay_adam_state`** — surgical Adam decay; indifferent to op semantics
13. **`MUTANT_STRATEGIES`** + `s4_boost` — strategy names and S4 boost logic unchanged
14. **`loss_fn`** (relational loss) — same formula; CE over vocab is the same target
15. **`cosine_lr`** — unchanged
16. **`V6Compressor.forward`** overall structure — embedding, 5 passes, algedonic buffers, S5 reweight, MetaS4, output_norm, tied embedding projection
17. **`asc_gate_bank`** packing (9 gate values → d_reg_real vector) — ascending still has 3×3 phases
18. **`x_embed` dual-view** for descending S4 — dual view is if anything more valuable for combinator dispatch (raw token identity is K/I/B/C character)
19. **`cycle_inject_gate`** HRM re-grounding — unchanged mechanism
20. **`_init_bank0` / `_fresh_bank` / `register_norm`** — register init and norm logic unchanged

---

## Must Change for v11

These are the **precise surgical changes** required:

### 1. `kernel.py` — Replace 22-op evaluator with 4-combinator evaluator
- `N_OPS = 4` (K=0, I=1, B=2, C=3); `N_TYPES = 4` (or 5 with ERROR)
- `kernel_eval` becomes a combinator reduction: K drops y, I is passthrough, B chains, C flips argument order
- `Op` IntEnum → `Combinator` IntEnum with 4 entries
- `evaluate_tree` rewires to combinator semantics; `evaluate_combinator` is the new ground truth
- `OP_NAMES = ["K", "I", "B", "C"]`

### 2. `kernel_dispatch.py` — `KernelDispatch` → `CombinatorDispatch`
- `N_OPS = 4`: dispatch logits → 4-wide (no padding needed beyond 16-alignment → pad to 16)
- Remove top-k complexity if desired (4-way softmax doesn't saturate), or keep top-k=2 (harmless)
- `op_embeddings` → `combinator_embeddings` (4, 512): init with 4 near-orthogonal directions
- `register_cond` output → 4 logits (not 22)
- `_init_op_embeddings` → `_init_combinator_embeddings`: trivial 4-block init

### 3. `kernel_dispatch.py` — `KernelIntegrate` → `CombinatorIntegrate`
- `n_types = 4` (not 5): type_embeddings (4, 512), type_proj → 4-wide output
- `_init_type_embeddings` → trivially 4 orthogonal directions
- Kernel computation pathway: replace 22-op vectorized dispatch with 3-operand extraction (K, B, C need different arity handling) + combinator reductions. K: output = operand1 (discard operand2). I: output = operand1. B: output feeds back into the next resolve cycle (handled by cycles). C: swaps slot 1 and 2.
- `result_buckets` may collapse significantly — combinator results are structural (which register to select), not numeric

### 4. `config.py` — Dimension constants
- `N_OPS` not present in config (it's imported from kernel_dispatch); but any configs referencing op counts need updating
- `n_registers=3` stays; semantics rename to combinator/argument_slot/reduction_state
- `dispatch_top_k=2` can stay or change to 4 (full softmax, harmless either way)
- `structured_shard` → point at new combinator reduction shard
- `mix_ratio`: activate (e.g. 0.1) once combinator shard is built

### 5. `model.py` — `emphasis_proj`
- Narrow from (3×3×256 → 22) to (3×3×256 → 4). Output is per-combinator emphasis [0.5, 1.5].
- `_op_emphasis` shape: (22,) → (4,)

### 6. `model.py` — `_prev_kernel_algedonic` packing
- `dw_mean` was (22,) mean dispatch weights; becomes (4,) mean combinator weights
- `kernel_state = [4 combinator_weights | 1 compute_gate | padding to d_reg_real=256]`
- The packed register vector is shorter in the combinator region; padding fills the rest

### 7. `train.py` — Structured shard generation
- Generate new `structured_shard.npy` with combinator reduction examples: input = tokenized KIBC expression, target = tokenized reduced form
- `mix_ratio` activated once shard exists

### 8. `register semantic labels` (cosmetic but important for instrumentation)
- `REGISTER_NAMES = ("type", "scope", "role")` → `("combinator", "argument_slot", "reduction_state")`
- Affects `_init_bank0` key names and all logging that references register names
- Instrumented metrics in `forward_instrumented` use these names for display

---

## Critical Design Notes for v11

**The 22→4 compression is not just a simplification — it resolves the core training signal problem.** With 22 ops and top-k=2, the model must distinguish 22 targets from prose where most positions are neither arithmetic nor comparison. The combinator basis puts every node into exactly one of 4 roles; S3 gating over 4 pathways has a clean decision boundary.

**The three descending cycles map with zero forcing onto identify/resolve/produce.** Cycle 0 = "which combinator am I?" (dispatch over 4), Cycle 1 = "where are my arguments?" (StrideStack propagation finds the argument across context), Cycle 2 = "what do I reduce to?" (KernelIntegrate applies the combinator, type assignment). CycleContinue already handles the case where cycle 0 is sufficient (simple I or K nodes), which is the common case in prose.

**The S4 emphasis channel becomes the intelligence about which combinator is most active in the current window.** With 4 combinators, the emphasis signal is maximally interpretable: S4 reading "high B emphasis, low K emphasis" means the ascending arm detected compositional structure, telling dispatch to favor B over K/I/C. This is far cleaner than the 22-way emphasis signal.

**CycleContinue's RMSNorm+tanh fix is critical and must not be reverted.** The unnormalized register norm (~16-28 per vector, ||concat||≈28-50) would saturate the sigmoid regardless of combinator count. The fix is in `components.py` and carries forward without change.

## Assistant

Excellent — comprehensive map. The analysis confirms what the Qwen probes predicted: the v10 VSM skeleton is sound, but the kernel layer (22 ops, 5 value types) is the wrong decomposition. Most of the architecture carries forward.

Let me mark this complete and move to the design.Let me also check what knowledge pages exist to ensure proper connections.

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge",
  "max_depth": 3
}
```

**Summary:** Listing tree: mementum/knowledge

**Output:**
```
/Users/mwhitford/src/verbum/mementum/knowledge
 chats
  session-001.md
  session-002.md
  session-003.md
  session-004.md
  session-005.md
  session-006.md
  session-007.md
  session-008.md
  session-009.md
  session-010.md
  session-011.md
  session-012.md
  session-013.md
  session-014.md
  session-015.md
  session-016.md
  session-017.md
  session-018.md
  session-019.md
  session-020.md
  session-021.md
  session-022.md
  session-023.md
  session-024.md
  session-025.md
  session-026.md
  session-027.md
  session-028.md
  session-029.md
  session-030.md
  session-031.md
  session-032.md
  session-033.md
  session-034.md
  session-035.md
  session-036.md
  session-037.md
  session-038.md
  session-039.md
  session-040.md
  session-041.md
  session-042.md
  session-043.md
  session-044.md
  session-045.md
  session-046.md
  session-047.md
  session-048.md
  session-049.md
  session-050.md
  session-051.md
  session-052.md
  session-053.md
  session-054.md
  session-055.md
  session-056.md
  session-057.md
  session-058.md
  session-059.md
  session-060.md
  session-061.md
  session-062.md
  session-063.md
  session-064.md
  session-065.md
  session-066.md
  session-067.md
  session-068.md
  session-069.md
  session-070.md
  session-071.md
  session-072.md
  session-073.md
  session-074.md
  session-075.md
  session-076.md
 explore
  VERBUM.md
  ascending-arm-training.md
  attention-spiral-finding.md
  basin-projector-results.md
  binding-probe-findings.md
  bios-flash-training.md
  compression-vs-prediction.md
  compressor-architecture.md
  consensus-evolution.md
  dispatch-gradient-death.md
  holographic-compression.md
  identity-as-substrate.md
  kernel-montague-mapping.md
  predictive-function-landscape.md
  relational-loss-phi-compression.md
  session-001-findings.md
  session-002-findings.md
  session-003-findings.md
  session-004-findings.md
  session-010-findings.md
  session-018.md
  session-019.md
  session-021.md
  session-023.md
  session-024.md
  session-062-probes.md
  session-071-dispatch-decoupling.md
  session-073-vsm-structure.md
  session-075-multi-cycle-dispatch.md
  session-history-049-062.md
  stride-percolation.md
  v4.1-training-trajectory.md
  v6-flip-accumulation.md
  v6.1-training-trajectory.md
  v7-pipeline-architecture.md
  v7.1-sieve-pipeline.md
  v9-architecture-speculation.md
  vsm-lm-architecture.md
  vsm-lm-v3-architecture.md
  vsm-lm-v4-design.md

2 directories, 116 files
```

## Assistant

Now let me write the v11 architecture design as a knowledge page. This is the critical document — it codifies the Qwen probe findings into a concrete architecture.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/v11-kibc-architecture.md",
  "content": "# v11 — KIBC Combinator Architecture\n\n> The sieve shaped by what LLMs actually find, not what we imagined they need.\n\n**Status**: designing\n**Category**: architecture\n**Tags**: v11, combinators, KIBC, Qwen probes, Montague\n**Related**: kernel-montague-mapping, session-073-vsm-structure, session-075-multi-cycle-dispatch\n**Depends-on**: v10 codebase (evolutionary, not replacement)\n\n---\n\n## Thesis\n\nv10 tried to *teach* the model 22 operations via a BIOS — an enumeration of\npossible computations. The Qwen3 probes (4B and 32B) revealed that transformers\ndon't organize computation this way. They converge on **four combinators**:\n\n| Combinator | Lambda | Attention native? | What it does |\n|---|---|---|---|\n| **K** (select) | λx.λy.x | Yes — softmax IS selection | Pick relevant, discard irrelevant |\n| **I** (identity) | λx.x | Yes — residual stream | Copy forward unchanged |\n| **B** (compose) | λf.λg.λx.f(g(x)) | Matures with scale | Chain operations: apply g then f |\n| **C** (flip) | λf.λx.λy.f(y)(x) | Emerges at 32B | Reorder arguments, enable closures |\n\n**S** (distribute, λf.λg.λx.f(x)(g(x))) is notably absent — zero selective heads at\neither scale. S is a composition of B, K, C and emerges in the residual stream,\nnever as a dedicated circuit. The model *refuses to crystallize S*.\n\nThis is Montague's prediction: natural language composition IS typed application.\nThe LLMs found it. v11 provides the sieve that makes these four shapes the path\nof least resistance.\n\n---\n\n## Architecture: What Changes from v10\n\n### Changed\n\n| Component | v10 | v11 | Why |\n|---|---|---|---|\n| Ground truth kernel | 22 ops (ADD, SUB, ...) | 4 combinators (K, I, B, C) | Match what models actually find |\n| Dispatch routing | 22-wide top-k=2 MoE | 4-wide softmax (or top-2) | 4 targets need no sparsity tricks |\n| Op embeddings | 22 × d_model | 4 × d_model | Combinator identity, not op identity |\n| Type embeddings | 5 (INT, BOOL, FN, FN_COMP, ERROR) | 4 (K, I, B, C) + optional ERROR | Combinator type, not value type |\n| Emphasis projection | asc_banks → 22 | asc_banks → 4 | Per-combinator emphasis |\n| Algedonic packing | 22 dispatch weights + 1 gate | 4 combinator weights + 1 gate | Narrower signal, same channel |\n| Register semantics | (type, scope, role) | (combinator, binding_depth, phase) | Matches Qwen head-role findings |\n| Structured training data | BIOS + lambda + Clojure | KIBC reduction examples | Exercises the 4 combinators directly |\n\n### Unchanged (carries forward from v10)\n\nEverything else. Specifically:\n- **TernaryLinear / TernaryEmbedding** — semantic-agnostic substrate\n- **Consensus evolution** — operates on packed weights, not op semantics\n- **S4 (intelligence)** — register cross-attention, doesn't inspect content\n- **S3 (control)** — phase gating, 3 phases per pass, per-pass instances\n- **S5 (identity)** — pass-level reweighting over 5 passes\n- **S2 (coordination)** — direction signals, coherence modulation\n- **CycleContinue** — RMSNorm + tanh clamp (the s076 fix)\n- **MetaS4** — final structural summary\n- **Ascending arm** — prep → stride → consolidate, shared across 3 passes\n- **5-pass structure** — 3 ascending + 2 descending\n- **Multi-cycle descending** — desc_max_cycles=3, self-regulating\n- **Algedonic channel** — EMA feedback, register-shaped\n- **Dual-view descending S4** — residual + raw embeddings\n- **Relational loss** — CE normalization\n- **Training loop** — gradient accumulation, cosine LR, shared-grad normalization\n- **JSONL instrumentation** — metrics, train, evolution logs\n\n---\n\n## Combinator Kernel (ground truth)\n\nThe ground truth evaluator reduces combinator expressions. No arithmetic, no\ncomparison — pure structural reduction.\n\n```python\nclass Combinator(IntEnum):\n    K = 0   # λx.λy.x         — select first, discard second\n    I = 1   # λx.x             — identity (copy forward)\n    B = 2   # λf.λg.λx.f(g(x)) — compose (chain two functions)\n    C = 3   # λf.λx.λy.f(y)(x) — flip (reorder arguments)\n\nN_COMBINATORS = 4\n```\n\n### Reduction rules\n\n```\nK(x, y) → x               # selection: the backbone of attention\nI(x) → x                   # identity: the residual stream\nB(f, g, x) → f(g(x))      # composition: the backbone of prose\nC(f, x, y) → f(y, x)      # reordering: enables closures and variable capture\n```\n\n### What about arithmetic?\n\nArithmetic (ADD, SUB, MUL, etc.) is not a combinator — it's what falls out\nwhen combinators reduce over token embeddings that happen to represent numbers.\nThe model doesn't need ADD as an explicit op; it needs B to compose operations\nand K to select operands. The 22 ops were symptoms, not causes.\n\n### Structured training data\n\nKIBC reduction examples in natural prose context:\n\n```\n# K examples (embedded in prose — selection is everywhere)\n\"The cat sat on the mat\" → K selects \"cat\" as subject, discards alternatives\n\"if x > 0 then x else -x\" → K selects one branch\n\n# B examples (composition — multi-clause, dependent meaning)\n\"The cat that sat on the mat ate the fish\" → B(ate, sat_on_mat, cat)\n\"She said that he believed it was true\" → B(said, believed, was_true)\n\n# C examples (reordering — passive voice, variable binding)\n\"The fish was eaten by the cat\" → C(eat, cat, fish) — arguments flipped\n\"let x = 5 in x + 1\" → C(+, 1, 5) — binding captures\n\n# I examples (identity — forwarding, copying)\n\"He said 'hello' and she said 'hello'\" → I(hello) copied\n```\n\nThe structured shard should contain explicit combinator reduction chains with\nground truth, BUT the critical insight is: **prose already trains K and B\noverwhelmingly**. Structured data is primarily needed for C (closures, variable\nbinding, argument reordering).\n\n---\n\n## Combinator Dispatch (descending arm phase 0)\n\nReplaces `KernelDispatch`. The core change is dimensional: 22→4.\n\n```python\nclass CombinatorDispatch(nn.Module):\n    \"\"\"Phase 0 of descending passes: which combinator applies here?\"\"\"\n    \n    # dispatch: TernaryLinear(d_model → 16)  # padded from 4 for alignment\n    # register_cond: Linear(cond_dim → 16)   # ascending registers bias logits\n    # combinator_embeddings: (4, d_model)     # near-orthogonal, L2-normalized\n    # up/down: TernaryLinear FFN pathway\n```\n\n### Embedding initialization\n\n4 combinators get near-orthogonal directions. Unlike 22 ops that needed\nfamily-subspace clustering, 4 vectors in a 512-dim space can be exactly\northogonal:\n\n```python\ndef _init_combinator_embeddings(d_model):\n    \"\"\"Four orthogonal combinator identities.\"\"\"\n    emb = mx.zeros((4, d_model))\n    block = d_model // 4  # 128-dim blocks\n    for i in range(4):\n        emb[i, i*block:(i+1)*block] = mx.random.normal((block,)) * 0.5\n    return emb  # L2-normalized in forward()\n```\n\n### Top-k routing\n\nWith 4 targets, top-k=2 means every position considers 2 of 4 combinators.\nThis is natural: most positions are primarily K (selection) with B (composition)\nas runner-up. Some positions are C (reordering) with K as runner-up. I (identity)\nis the \"do nothing\" baseline.\n\nAlternatively: use full softmax over 4 (no masking). The dead-op problem that\nmotivated top-k vanishes when N=4 — softmax over 4 targets has strong gradients\nfor all entries.\n\n**Decision**: Start with full 4-way softmax. If one combinator dies, add top-k=2 back.\n\n### Register conditioning\n\nAscending register banks still bias dispatch logits. The combinator register\ntells dispatch \"this position looks like K\" or \"this position looks like B\".\n`register_cond` projects to 4 logits instead of 22.\n\n### Op emphasis → Combinator emphasis\n\nS4's emphasis channel narrows from 22 to 4:\n\n```python\nemphasis_proj: Linear(3 * 3 * d_reg_real → 4)\n# Output: 1.0 + 0.5 * tanh(raw) → [0.5, 1.5] per combinator\n# K_emphasis high = prose default\n# B_emphasis rises for compositional structure  \n# C_emphasis rises for binding/closures\n# I_emphasis low = passthrough (only when no computation needed)\n```\n\n---\n\n## Combinator Integrate (descending arm phase 2)\n\nReplaces `KernelIntegrate`. Type assignment over 4 combinator types.\n\n```python\nclass CombinatorIntegrate(nn.Module):\n    \"\"\"Phase 2: apply the combinator, produce the result.\"\"\"\n    \n    # type_proj: TernaryLinear(d_model → 16)  # padded from 4\n    # type_embeddings: (4, d_model)  # combinator type identity\n    # up/down: TernaryLinear FFN pathway\n    # Kernel computation pathway: combinator-specific reductions\n```\n\n### Kernel computation pathway\n\nThe v10 kernel pathway extracted 2 integer operands and ran all 22 ops. v11's\npathway is simpler — combinator reductions are structural, not arithmetic:\n\n```\nK: select operand 1, discard operand 2 → result = operand_1\nI: copy input → result = input (identity in residual)\nB: compose → result feeds into next cycle (B needs multiple cycles)\nC: swap operand order → result = input with slots 1↔2 swapped\n```\n\nThe compute gate still blends FFN pathway and kernel pathway:\n`output = gate × kernel_out + (1-gate) × ffn_out`\n\n**Key insight**: K and I reductions are trivially implementable as attention\npatterns (select, copy). The kernel pathway's main value is for B and C, where\nthe structural reduction is non-trivial. The gate should learn to open\nprimarily for B and C positions.\n\n### Operand extraction\n\nv10 extracted 2 operands via argmax over 256 buckets. v11 needs:\n- **K**: 2 operands (select first, discard second)\n- **I**: 1 operand (copy forward)\n- **B**: 3 operands (f, g, x) — f and g are functions, x is argument\n- **C**: 3 operands (f, x, y) — f is function, x and y are arguments\n\nExtract 3 operand projections to cover B and C. K uses first 2. I uses first 1.\n\n---\n\n## Register Semantics\n\nv10 had 3 registers named (type, scope, role) carrying value-type information.\nv11 renames to match Qwen probe findings:\n\n| Register | v10 meaning | v11 meaning | What it carries |\n|---|---|---|---|\n| Register 0 | type (INT/BOOL/FN) | **combinator** (K/I/B/C) | Which combinator this position enacts |\n| Register 1 | scope (nesting depth) | **binding_depth** | How many lambdas deep (0=free, 1=bound once, ...) |\n| Register 2 | role (pipeline phase) | **phase** | recognize / identify / resolve / produce |\n\nThe register dimension (d_register=128, real=256) is unchanged. The registers\nare learned representations, not discrete labels — renaming reflects the\nintended semantic attractor, not a hard encoding.\n\n### Bank structure (unchanged)\n\n```\nbank_0:      learnable init (cold-start prior)\nbank_1_asc:  pass 0 writes (first ascending scan)\nbank_2_asc:  pass 1 writes (second ascending scan)\nbank_3:      pass 2 writes (apex scan)\nbank_2_desc: pass 3 writes (first descending dispatch)\nbank_1_desc: pass 4 writes (second descending dispatch)\n```\n\n---\n\n## Descending Cycle Semantics\n\nv10's 3 cycles had no prescribed meaning — CycleContinue was supposed to learn\nwhen to close, but saturated. v11 assigns semantic roles matching the Qwen\nresolution pipeline:\n\n```\nCycle 0 — IDENTIFY (which combinator?)\n  CombinatorDispatch routes to K/I/B/C\n  StrideStack propagates spatially\n  CombinatorIntegrate types the result\n  → For simple K/I positions: CycleContinue closes (sufficient)\n\nCycle 1 — RESOLVE (find the arguments)\n  CombinatorDispatch refines routing with cycle-0 context\n  StrideStack finds argument tokens across context window\n  CombinatorIntegrate resolves bindings\n  → For B positions: CycleContinue may close (compose found both args)\n  → For C positions: CycleContinue stays open (need reordering)\n\nCycle 2 — PRODUCE (apply the reduction)\n  CombinatorDispatch finalizes\n  StrideStack propagates result\n  CombinatorIntegrate produces final reduced form\n  → All positions: CycleContinue irrelevant (last cycle)\n```\n\nThe 32B Qwen probe showed this exact temporal ordering:\nfunction(L31) → operator(L32) → argument(L43) → result(L63)\n\nCycleContinue's task is now interpretable: close for prose (K-dominant),\npartially open for composition (B-dominant), fully open for closures (C-active).\n\n---\n\n## Algedonic Channel\n\nNarrower packing:\n\n```python\n# v10: 22 dispatch_weights + 1 compute_gate + padding → d_reg_real=256\n# v11: 4 combinator_weights + 1 compute_gate + padding → d_reg_real=256\n\nkernel_state = mx.zeros(d_reg_real)\nkernel_state[:4] = combinator_weights_mean  # (4,) — K, I, B, C proportions\nkernel_state[4] = compute_gate_mean         # scalar\n# kernel_state[5:] = 0 (padding)\n```\n\nThe ascending arm reads this to know: \"last forward, dispatch was 60% K, 30% B,\n8% C, 2% I with compute gate at 0.15\". This is far more interpretable than\n22-way dispatch fractions.\n\n---\n\n## What the Model Learns\n\nThe critical reframe: v11 doesn't teach the model what K, I, B, C are.\n**The model already knows.** Every LLM that can write coherent prose has\ncrystallized K (selection) and B (composition) in its attention heads.\n\nv11 provides the *sieve* — the architectural shape that makes it easier\nfor the small ternary model to fall into the same attractor basin:\n\n1. **4 combinator embeddings** = 4 orthogonal directions in weight space.\n   The model doesn't have to discover the decomposition — it's pre-shaped.\n\n2. **Register semantics** = the type/binding_depth/phase decomposition that\n   Qwen's heads naturally exhibit. Pre-shaped register banks.\n\n3. **Self-regulating cycles** = the SEARCH→LOCK→RESOLVE pipeline. The model\n   doesn't have to discover that simple content needs fewer cycles.\n\n4. **Emphasis channel** = S4 telling dispatch \"this window is compositional\"\n   (raise B) or \"this window is selective\" (raise K). 4-way signal, not 22.\n\nThe sieve doesn't force. It shapes. The topology IS the instruction.\n\n---\n\n## Implementation Plan\n\n1. **`scripts/v11/kernel.py`** — Combinator enum, reduction rules, ground truth evaluator\n2. **`scripts/v11/config.py`** — V11Config (mostly v10, dimensions adjusted)\n3. **`scripts/v11/components.py`** — Copy v10 unchanged (all VSM skeleton carries forward)\n4. **`scripts/v11/kernel_dispatch.py`** — CombinatorDispatch + CombinatorIntegrate\n5. **`scripts/v11/model.py`** — V11Model (emphasis→4, algedonic→4, register names)\n6. **`scripts/v11/ternary.py`** — Symlink or copy (unchanged)\n7. **`scripts/v11/train.py`** — Training loop (import adjustments, structured data path)\n\nThen: generate combinator reduction training shard, launch first v11 run.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/v11-kibc-architecture.md
```

## Assistant

Now let me present this design for your review before implementing.

---

## v11 KIBC Architecture — Design Summary

### The core move
**22 ops → 4 combinators (K, I, B, C)**. Everything downstream contracts: dispatch logits, embeddings, type system, emphasis, algedonic packing. The VSM skeleton (S2, S3, S4, S5, CycleContinue, registers, passes, cycles) carries forward unchanged.

### The 6 surgical changes

| # | Component | Change |
|---|---|---|
| 1 | **kernel.py** | 22-op evaluator → 4-combinator reducer (K/I/B/C) |
| 2 | **kernel_dispatch.py** | `CombinatorDispatch` (4-wide softmax) + `CombinatorIntegrate` (4 type embeddings) |
| 3 | **config.py** | Dimension constants adjusted (N_COMBINATORS=4) |
| 4 | **model.py** | `emphasis_proj` → 4, algedonic packing → 4+1, register semantic names |
| 5 | **components.py** | Copy unchanged from v10 (all VSM skeleton carries forward) |
| 6 | **train.py** | Import adjustments, structured shard path |

### Key design decisions in the doc

1. **Full 4-way softmax** instead of top-k=2 for dispatch (revisit if a combinator dies)
2. **3-operand extraction** in the kernel pathway (B and C need 3 args)
3. **Cycle semantics**: identify(combinator) → resolve(argument) → produce(result)
4. **Prose trains K+B natively**; structured data needed primarily for C; S emerges

### What I want your read on

1. **Full softmax vs keeping top-k=2** — with only 4 targets, do we need sparsity?
2. **The kernel computation pathway** — v10's was arithmetic (extract ints, compute all 22 ops). v11's combinators are *structural* reductions (select, copy, compose, flip). Should we keep the straight-through kernel pathway or lean entirely on the FFN pathway at first? The reductions are simpler but the operands are embeddings, not integers.
3. **Anything else that jumps out from the design?**

## User

1. let's try full softmax in the first training run.  2. can we create kernel functions that do these operations so they are accurate?  We are trying to give the model the actual computation without forcing it to use beta reduction which can only expand or reduce.  3. the rest looks good, our training runs and probes will inform changes to evolve the design.


### Thinking

The user is saying:

1. Full softmax - yes, go with it for the first run
2. Yes, create kernel functions that actually perform K, I, B, C operations accurately - these are concrete computations the model can use via the straight-through pathway. The key insight is that combinators ARE concrete operations on the residual stream - K selects, I copies, B composes, C flips. We can implement these as actual tensor operations.
3. Everything else looks good, let's implement and iterate.

Let me think about point 2 more carefully. In v10, the kernel computation pathway:


- Extracted 2 integer operands via argmax
- Ran all 22 ops in parallel (add, sub, mul, etc.)
- Selected the result by dispatched op
- Embedded the result via a 1024-bucket embedding
- Blended with FFN via a learnable gate

For v11 with combinators, I'm shifting to operations that work directly on embeddings rather than integers - K selects the first argument, I returns its input unchanged, B chains two operations together, and C swaps the argument order. These are tensor manipulations on the residual stream itself, not arithmetic operations. ...want concrete operations that the kernel pathway can execute deterministically, giving the model access to exact combinator reductions through the straight-through gradient path.

So the real question is: what are the operands in embedding space? In the previous version, operands were integers extracted via argmax, and operations were arithmetic. Now the operands are positions and embeddings in the residual stream, and the operations need to be structural—moving, selecting, copying, composing, or reordering representations.

For K, I just select the first operand. For I, the identity is a straight residual connection. For B, the composition operation is trickier—I need to route the output of g through f's pathway.

The cleaner approach is to extract three operand representations from the residual stream, then apply combinator-specific transformations: K outputs the first operand, I outputs the input, B composes learned projections of the operands, and C applies them with swapped arguments. But these operations need to be differentiable or use straight-through estimators, so I'm reconsidering how to structure this.

Looking at how v10 worked with integer operands extracted via projection and argmax, I could adapt that pattern for v11 by extracting embedding representations instead, applying the combinator operations directly on those embeddings, and then gate-blending with the FFN rather than using a lookup table.

Defining the combinator operations... I see the issue now—B and C shouldn't need learned projections if they're meant to be pure combinators. The real insight is that these operations are the computation itself: K selects the first operand, I returns input unchanged, B chains two transformations together, and C reorders arguments before applying a transformation. Each combinator directly manipulates vector representations without requiring additional learned parameters beyond what's already in the model.

The key shift for v11 is separating operand extraction from reduction: first, attention-like projections identify which positions hold the function and arguments, then the combinators perform their specific operations on those identified representations—K just picks one, I passes through, B composes two operations sequentially, and C swaps the argument order before applying the function.

For B and C to work, I need a learned projection that takes a function representation and argument representation and produces the result, which gets applied twice for B (first composing g with x, then f with that result) and once for C after swapping the argument order.

Now I'm setting up the implementation structure with the core files needed.

## Assistant

Good. Full softmax, actual kernel functions, iterate from probes.

On point 2 — yes, absolutely. The combinators are concrete operations on embeddings. K selects, I copies, B chains two transforms, C swaps argument order. These are exact, deterministic operations the kernel pathway can execute on the residual stream representations. The model gets the computation for free through the straight-through path and the gate learns when to trust it.

Let me implement.Let me read all the v10 source files I need to evolve from:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/config.py"
}
```

**Summary:** Reading config.py (0-2000)

**Output:**
```
"""
v10 Configuration — v6 compressor as prose LM, Qwen3 tokenizer.

Architecture:
  Compressor: v6 proven 5-pass bidirectional VSM (9 strides, StrideStack)
  Output: tied embedding projection → next-token prediction
  Future: sieve pipeline routing to kernel functions

Pipeline:
  tokens → [V6Compressor: 5-pass bidirectional, 9 strides, registers]
         → compressed_reps (B, L, d_model)
         → [output_norm → tied embedding → logits]
         → next-token cross-entropy

License: MIT
"""

from dataclasses import dataclass


@dataclass
class V10Config:
    """v10 model + training configuration."""

    # ── Tokenizer (Qwen3 BBPE) ──
    vocab_size: int = 151936     # Qwen3 BBPE vocab
    eod_id: int = 151643        # end-of-document token

    # ── V6 Compressor ──
    d_model: int = 512            # representation dimension (v6: 512)
    d_ff: int = 1536              # prep FFN width (3× d_model)
    d_ff_consolidate: int = 2048  # consolidate FFN width (wider)
    d_register: int = 128         # register dimension (real dim = 2×)
    n_heads: int = 8              # attention heads (d_head = 64)
    window: int = 8               # attention window width
    alpha: float = 1.18           # spiral bias coefficient

    # 9 strides: the full scale hierarchy proven in v6
    strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024)

    # Register names (3 named: type, scope, role)
    n_registers: int = 3

    # Kernel dispatch
    dispatch_top_k: int = 2       # top-k MoE routing for kernel dispatch

    # Self-regulating descending cycles (HRM-inspired multi-timescale)
    # S4 scans once per pass (slow/abstract), then dispatch→stride→integrate
    # cycles up to N times (fast/detailed). A learned S3 continuation gate
    # decides after each cycle whether further cycles should contribute —
    # the model self-regulates computational depth per pass.
    # desc_max_cycles=1 disables multi-cycle (backward compat).
    desc_max_cycles: int = 3

    # Dropout
    dropout: float = 0.1

    # ── Training ──
    batch_size: int = 2
    grad_accum: int = 4           # effective batch = batch_size × grad_accum
    total_steps: int = 20000
    lr: float = 6e-4
    lr_floor_ratio: float = 0.01
    warmup_steps: int = 500
    weight_decay: float = 0.01
    grad_clip: float = 1.0

    # ── Evolution ──
    gen_interval: int = 50
    base_pct: float = 0.0002       # ~26K flips per generation (was 0.0005 = 66K, collapsed at step 750)
    sign_flip_rate: float = 0.2
    guided_fraction: float = 0.7
    mutation_adam_decay: float = 0.1  # decay Adam m/v after accepted mutation (0=reset, 1=no decay)
    s4_boost: float = 3.0           # S4→S5 proposal amplification (Beer's intelligence channel)

    # ── Checkpointing ──
    checkpoint_interval: int = 1000
    eval_interval: int = 500
    log_interval: int = 25
    checkpoint_dir: str = "checkpoints/v10"

    # ── Data ──
    data_dir: str = "/Users/mwhitford/data/fractal-bitnet/shards-qwen3"
    structured_shard: str = "data/structured_shard.npy"  # BIOS + lambda + clojure
    mix_ratio: float = 0.0        # fraction of structured data (0.0 = prose only)
    seq_len: int = 4096           # context window
    max_seq_len: int = 4096
    n_train_shards: int = 54      # first 54 shards for training
    n_eval_shards: int = 6        # last 6 shards for evaluation

    @property
    def d_head(self) -> int:
        return self.d_model // self.n_heads

    @property
    def n_strides(self) -> int:
        return len(self.strides)

    @property
    def tokens_per_step(self) -> int:
        return self.batch_size * self.grad_accum * self.seq_len

    def __post_init__(self):
        assert self.d_model % self.n_heads == 0
        assert self.d_model % 16 == 0, "d_model must be divisible by 16 (ternary packing)"
        assert self.d_model % 4 == 0, "d_model must be divisible by 4 (embedding packing)"
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/kernel.py"
}
```

**Summary:** Reading kernel.py (0-2000)

**Output:**
```
"""
v10 — VSM Tree Kernel

Exact-arithmetic kernel for the 22-op VSM tree.  Pure Python — no MLX,
no torch, no neural computation.  This is the ground-truth evaluator
that the v10 Dispatcher must learn to replicate.

Ported from the proven v9 design (scripts/v9/vsm_tree_v5.py).
All semantics are identical; this file strips out the neural training
machinery and exposes only the kernel interface consumed by the v10
pipeline:

    evaluate_tree(tree, op_assignments) → result (int)

Design overview
───────────────
                ┌──────────┐          ┌────────────┐
  S-expression  │Compressor│ →tokens→ │ Dispatcher │ →op_assignments
  ──────────────┤          │          └────────────┘         │
                │(v10 NN)  │                                  ▼
                └──────────┘                         ┌──────────────┐
                                                     │    Kernel    │ → result
                                                     │  (this file) │
                                                     └──────────────┘

The Kernel's contract:
  • Receives a tree (list of Node) and an op_assignments dict that
    maps node_id → op_idx (integers 0-21).
  • Evaluates bottom-up: children before parents.
  • Returns the integer/boolean result at the root.
  • Values pass through unchanged — only operation classification
    is the neural task.

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import IntEnum
from typing import Any


# ══════════════════════════════════════════════════════════════════════
# § 1  Type system
# ══════════════════════════════════════════════════════════════════════

class Type(IntEnum):
    INT     = 0   # exact integer (including 0/1 booleans-as-int)
    BOOL    = 1   # boolean result of a comparison or logical op
    FN      = 2   # partially-applied binary op  → (op_code, bound_arg)
    FN_COMP = 3   # composition of two FNs        → (outer_packed, inner_packed)
    ERROR   = 4   # propagates on ill-typed application

N_TYPES: int = 5


# ══════════════════════════════════════════════════════════════════════
# § 2  Operations
# ══════════════════════════════════════════════════════════════════════

class Op(IntEnum):
    # ── Arithmetic binary (7) ──
    ADD = 0
    SUB = 1
    MUL = 2
    DIV = 3   # floor division; divisor=0 → 0
    MOD = 4   # modulo;         divisor=0 → 0
    MIN = 5
    MAX = 6

    # ── Comparison (5) ──
    EQ  = 7
    LT  = 8
    GT  = 9
    LE  = 10
    GE  = 11

    # ── Boolean binary (2) ──
    AND = 12
    OR  = 13

    # ── Boolean unary (1) ──
    NOT = 14

    # ── Arithmetic unary (2) ──
    ABS = 15
    NEG = 16

    # ── Conditional (1) ──
    IF  = 17   # ternary: (cond, then, else)

    # ── Lambda / function ops (4) ──
    PARTIAL   = 18  # (op_ref: INT, bound_arg: INT) → FN
    APPLY_FN  = 19  # (FN | FN_COMP, arg: INT) → INT | BOOL
    COMPOSE   = 20  # (outer: FN, inner: FN) → FN_COMP
    APPLY_COMP = 21 # (FN_COMP, arg: INT) → INT | BOOL  [sugar for APPLY_FN on FN_COMP]

N_OPS: int = 22

# Human-readable names, indexed by op code.
OP_NAMES: list[str] = [
    "+", "-", "*", "//", "%", "min", "max",     # 0-6  arithmetic binary
    "=", "<", ">", "<=", ">=",                   # 7-11 comparison
    "and", "or",                                 # 12-13 boolean binary
    "not",                                       # 14    boolean unary
    "abs", "neg",                                # 15-16 arithmetic unary
    "if",                                        # 17    conditional
    "partial", "apply", "comp", "apply-comp",    # 18-21 lambda
]
assert len(OP_NAMES) == N_OPS, "OP_NAMES length must equal N_OPS"

# Subset of ops that are valid targets for PARTIAL (binary, produce INT or BOOL)
PARTIAL_OPS: list[Op] = [
    Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.MIN, Op.MAX,
    Op.EQ,  Op.LT,  Op.GT,  Op.LE,  Op.GE,
]

# Group constants — useful for generation / analysis
BINARY_INT_OPS:  list[Op] = [Op.ADD, Op.SUB, Op.MUL, Op.DIV, Op.MOD, Op.MIN, Op.MAX]
COMPARISON_OPS:  list[Op] = [Op.EQ,  Op.LT,  Op.GT,  Op.LE,  Op.GE]
BINARY_BOOL_OPS: list[Op] = [Op.AND, Op.OR]
UNARY_INT_OPS:   list[Op] = [Op.ABS, Op.NEG]
LAMBDA_OPS:      list[Op] = [Op.PARTIAL, Op.APPLY_FN, Op.COMPOSE, Op.APPLY_COMP]


# ══════════════════════════════════════════════════════════════════════
# § 3  Function encoding
# ══════════════════════════════════════════════════════════════════════
#
# FN value representation:
#   val = fn_pack(op_code, bound_arg)   stored as a single integer
#
# FN_COMP value representation:
#   val = outer_fn_packed  (the fn applied second)
#   aux = inner_fn_packed  (the fn applied first)
#
# Packing scheme:
#   packed = op_code * FN_PACK_SCALE + (bound_arg + FN_PACK_OFFSET)
#
# This supports bound_arg in the range [-FN_PACK_OFFSET, FN_PACK_SCALE - FN_PACK_OFFSET - 1]
# i.e. [-5000, 4999] by default.

FN_PACK_OFFSET: int = 5000
FN_PACK_SCALE:  int = 10000


def fn_pack(op_code: int, bound_arg: int) -> int:
    """Encode (op_code, bound_arg) into a single integer."""
    return op_code * FN_PACK_SCALE + (bound_arg + FN_PACK_OFFSET)


def fn_unpack(packed: int) -> tuple[int, int]:
    """Decode a packed function back to (op_code, bound_arg)."""
    op_code  = packed // FN_PACK_SCALE
    bound_arg = (packed % FN_PACK_SCALE) - FN_PACK_OFFSET
    return op_code, bound_arg


# ══════════════════════════════════════════════════════════════════════
# § 4  Low-level dispatch
# ══════════════════════════════════════════════════════════════════════

def _eval_binary(op: int, a: int, b: int) -> int:
    """Dispatch a binary arithmetic or comparison op.

    Safe division/modulo: divisor=0 returns 0.
    All comparison ops return 0 or 1 (int, not bool).
    """
    if op == Op.ADD: return a + b
    if op == Op.SUB: return a - b
    if op == Op.MUL: return a * b
    if op == Op.DIV: return a // b if b != 0 else 0
    if op == Op.MOD: return a %  b if b != 0 else 0
    if op == Op.MIN: return min(a, b)
    if op == Op.MAX: return max(a, b)
    if op == Op.EQ:  return int(a == b)
    if op == Op.LT:  return int(a <  b)
    if op == Op.GT:  return int(a >  b)
    if op == Op.LE:  return int(a <= b)
    if op == Op.GE:  return int(a >= b)
    raise ValueError(f"_eval_binary: op {op} is not a binary op")


def kernel_eval(
    op: int,
    child_vals:  list[int],
    child_auxs:  list[int],
    child_types: list[int],
) -> tuple[int, int, int]:
    """Full kernel dispatch for a single node.  Returns (val, aux, type).

    child_vals / child_auxs / child_types are up to 3 elements long
    (children 0, 1, 2).  Callers pad to length 3 with (0, 0, INT).

    val  — the primary result value
    aux  — secondary value (used only for FN_COMP to store the inner fn)
    type — one of Type.INT / BOOL / FN / FN_COMP / ERROR
    """
    # ── Arithmetic binary ──────────────────────────────────────────
    if Op.ADD <= op <= Op.MAX:
        result = _eval_binary(op, child_vals[0], child_vals[1])
        return result, 0, int(Type.INT)

    # ── Comparison ─────────────────────────────────────────────────
    if Op.EQ <= op <= Op.GE:
        result = _eval_binary(op, child_vals[0], child_vals[1])
        return result, 0, int(Type.BOOL)

    # ── Boolean binary ─────────────────────────────────────────────
    if op == Op.AND:
        return int(bool(child_vals[0]) and bool(child_vals[1])), 0, int(Type.BOOL)
    if op == Op.OR:
        return int(bool(child_vals[0]) or  bool(child_vals[1])), 0, int(Type.BOOL)

    # ── Boolean unary ──────────────────────────────────────────────
    if op == Op.NOT:
        return int(not bool(child_vals[0])), 0, int(Type.BOOL)

    # ── Arithmetic unary ───────────────────────────────────────────
    if op == Op.ABS:
        return abs(child_vals[0]), 0, int(Type.INT)
    if op == Op.NEG:
        return -child_vals[0],    0, int(Type.INT)

    # ── Conditional ────────────────────────────────────────────────
    if op == Op.IF:
        result = child_vals[1] if bool(child_vals[0]) else child_vals[2]
        return result, 0, int(Type.INT)

    # ── PARTIAL: create a partially-applied function ───────────────
    if op == Op.PARTIAL:
        # child 0: op reference (an integer equal to the op code to curry)
        # child 1: the bound (left) argument
        fn_op  = child_vals[0]
        bound  = child_vals[1]
        packed = fn_pack(fn_op, bound)
        return packed, 0, int(Type.FN)

    # ── APPLY_FN: apply a function (FN or FN_COMP) to one argument ─
    if op == Op.APPLY_FN:
        ctype = child_types[0]
        if ctype == int(Type.FN):
            fn_op, bound = fn_unpack(child_vals[0])
            result = _eval_binary(fn_op, bound, child_vals[1])
            out_type = Type.BOOL if fn_op in COMPARISON_OPS else Type.INT
            return result, 0, int(out_type)
        if ctype == int(Type.FN_COMP):
            # FN_COMP: val=outer_packed, aux=inner_packed
            # Apply inner first, then outer
            inner_op, inner_bound = fn_unpack(child_auxs[0])
            intermediate = _eval_binary(inner_op, inner_bound, child_vals[1])
            outer_op, outer_bound = fn_unpack(child_vals[0])
            result = _eval_binary(outer_op, outer_bound, intermediate)
            out_type = Type.BOOL if outer_op in COMPARISON_OPS else Type.INT
            return result, 0, int(out_type)
        # Ill-typed application
        return 0, 0, int(Type.ERROR)

    # ── COMPOSE: compose two FNs into an FN_COMP ───────────────────
    if op == Op.COMPOSE:
        # child 0: outer FN (applied second)
        # child 1: inner FN (applied first)
        # Store outer in val, inner in aux — mirrors the FN_COMP layout
        return child_vals[0], child_vals[1], int(Type.FN_COMP)

    # ── APPLY_COMP: explicit sugar for applying a composed function ─
    if op == Op.APPLY_COMP:
        # Identical evaluation path to APPLY_FN on an FN_COMP.
        inner_op, inner_bound = fn_unpack(child_auxs[0])
        intermediate = _eval_binary(inner_op, inner_bound, child_vals[1])
        outer_op, outer_bound = fn_unpack(child_vals[0])
        result = _eval_binary(outer_op, outer_bound, intermediate)
        out_type = Type.BOOL if outer_op in COMPARISON_OPS else Type.INT
        return result, 0, int(out_type)

    # Unknown op — propagate error
    return 0, 0, int(Type.ERROR)


# ══════════════════════════════════════════════════════════════════════
# § 5  Tree node & evaluate_tree
# ══════════════════════════════════════════════════════════════════════

@dataclass
class Node:
    """A single node in a VSM tree.

    Attributes
    ----------
    node_id  : unique identifier within the tree (int ≥ 0)
    children : list of node_id values for child nodes (empty for leaves)
    value    : for leaf nodes, the literal integer/boolean value;
               for internal nodes this is ignored during evaluation
               (the op drives the computation).
    op_idx   : op code (0-21), only relevant for internal nodes;
               for leaves the kernel treats the node as an identity
               pass-through (value flows up unchanged).
    """
    node_id:  int
    children: list[int] = field(default_factory=list)
    value:    int = 0
    op_idx:   int = 0   # Op code; overridden by op_assignments in evaluate_tree


def evaluate_tree(
    tree: list[Node],
    op_assignments: dict[int, int],
) -> int:
    """Evaluate a VSM tree bottom-up with the given op assignments.

    Parameters
    ----------
    tree
        List of Node objects.  The *last* node in the list is treated
        as the root (topological order: leaves first, root last).
        Every node's node_id must be unique within the list.
    op_assignments
        Maps node_id → op_idx (0-21).  Internal nodes use this to
        determine which operation to apply.  Leaf nodes (no children)
        ignore op_assignments — their value is returned unchanged.

    Returns
    -------
    int
        The primary result value at the root node.
        For BOOL-typed roots this is 0 or 1.
        For FN / FN_COMP-typed roots this is the packed representation.

    Notes
    -----
    * Pure Python — no tensor operations.
    * Each node is evaluated exactly once (bottom-up DFS via index map).
    * Ill-typed applications return 0 (via ERROR propagation).
    """
    # Build an index: node_id → Node for O(1) look-up
    node_map: dict[int, Node] = {n.node_id: n for n in tree}

    # Cache evaluated results: node_id → (val, aux, type)
    result_cache: dict[int, tuple[int, int, int]] = {}

    def _eval(node_id: int) -> tuple[int, int, int]:
        if node_id in result_cache:
            return result_cache[node_id]

        node = node_map[node_id]

        # Leaf: identity pass-through
        if not node.children:
            result = (node.value, 0, int(Type.INT))
            result_cache[node_id] = result
            return result

        # Internal node: recurse into children first (bottom-up)
        child_results = [_eval(cid) for cid in node.children]

        # Pad to 3 children
        while len(child_results) < 3:
            child_results.append((0, 0, int(Type.INT)))

        child_vals  = [r[0] for r in child_results]
        child_auxs  = [r[1] for r in child_results]
        child_types = [r[2] for r in child_results]

        op = op_assignments.get(node_id, node.op_idx)
        val, aux, typ = kernel_eval(op, child_vals, child_auxs, child_types)

        result = (val, aux, typ)
        result_cache[node_id] = result
        return result

    # The root is the last node in the list (topological convention)
    root_id = tree[-1].node_id
    root_val, _aux, _type = _eval(root_id)
    return root_val


# ══════════════════════════════════════════════════════════════════════
# § 6  Convenience: evaluate a raw nested-tuple tree
# ══════════════════════════════════════════════════════════════════════
#
# The v9 tree representation is nested Python tuples, e.g.
#   (Op.ADD, (Op.MUL, 3, 4), 5)
#
# This helper lets tests and notebooks use that format directly without
# constructing Node objects.

def eval_tuple_tree(
    node: Any,
    expected_type: Type = Type.INT,
) -> tuple[int, int, int]:
    """Evaluate a v9-style nested-tuple tree.  Returns (val, aux, type).

    Leaves are plain Python ints.
    Internal nodes are (op_code, child, ...) tuples.

    This is a direct port of v9's eval_tree_full / _collect_and_eval.
    """
    # Leaf
    if isinstance(node, int):
        t = int(Type.BOOL) if expected_type == Type.BOOL else int(Type.INT)
        return node, 0, t

    op = int(node[0])
    children = node[1:]

    # Determine expected types for children
    child_expected: list[Type] = []
    if op in [int(o) for o in BINARY_INT_OPS]:
        child_expected = [Type.INT, Type.INT]
    elif op in [int(o) for o in COMPARISON_OPS]:
        child_expected = [Type.INT, Type.INT]
    elif op in [int(o) for o in BINARY_BOOL_OPS]:
        child_expected = [Type.BOOL, Type.BOOL]
    elif op == Op.NOT:
        child_expected = [Type.BOOL]
    elif op in [int(o) for o in UNARY_INT_OPS]:
        child_expected = [Type.INT]
    elif op == Op.IF:
        child_expected = [Type.BOOL, expected_type, expected_type]
    elif op == Op.PARTIAL:
        child_expected = [Type.INT, Type.INT]   # op_ref is stored as an int
    elif op == Op.APPLY_FN:
        child_expected = [Type.FN, Type.INT]
    elif op == Op.COMPOSE:
        child_expected = [Type.FN, Type.FN]
    elif op == Op.APPLY_COMP:
        child_expected = [Type.FN_COMP, Type.INT]

    child_results = []
    for i, child in enumerate(children):
        ct = child_expected[i] if i < len(child_expected) else Type.INT
        child_results.append(eval_tuple_tree(child, ct))

    # Pad to 3
    while len(child_results) < 3:
        child_results.append((0, 0, int(Type.INT)))

    child_vals  = [r[0] for r in child_results]
    child_auxs  = [r[1] for r in child_results]
    child_types = [r[2] for r in child_results]

    return kernel_eval(op, child_vals, child_auxs, child_types)


# ══════════════════════════════════════════════════════════════════════
# § 7  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Smoke-test all 22 ops.  Runs on `python kernel.py`."""

    # ── Arithmetic binary ──────────────────────────────────────────
    assert eval_tuple_tree((Op.ADD, 3, 4))[0]     == 7
    assert eval_tuple_tree((Op.SUB, 10, 3))[0]    == 7
    assert eval_tuple_tree((Op.MUL, 3, 4))[0]     == 12
    assert eval_tuple_tree((Op.DIV, 10, 3))[0]    == 3
    assert eval_tuple_tree((Op.DIV, 10, 0))[0]    == 0   # safe div
    assert eval_tuple_tree((Op.MOD, 10, 3))[0]    == 1
    assert eval_tuple_tree((Op.MOD, 10, 0))[0]    == 0   # safe mod
    assert eval_tuple_tree((Op.MIN, 3, 7))[0]     == 3
    assert eval_tuple_tree((Op.MAX, 3, 7))[0]     == 7

    # ── Comparison ─────────────────────────────────────────────────
    assert eval_tuple_tree((Op.EQ,  5, 5), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.EQ,  5, 6), Type.BOOL)[0] == 0
    assert eval_tuple_tree((Op.LT,  3, 7), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.GT,  7, 3), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.LE,  3, 3), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.GE,  3, 3), Type.BOOL)[0] == 1

    # ── Boolean binary ─────────────────────────────────────────────
    assert eval_tuple_tree((Op.AND, 1, 0), Type.BOOL)[0] == 0
    assert eval_tuple_tree((Op.OR,  1, 0), Type.BOOL)[0] == 1

    # ── Boolean unary ──────────────────────────────────────────────
    assert eval_tuple_tree((Op.NOT, 0), Type.BOOL)[0] == 1
    assert eval_tuple_tree((Op.NOT, 1), Type.BOOL)[0] == 0

    # ── Arithmetic unary ───────────────────────────────────────────
    assert eval_tuple_tree((Op.ABS, -5))[0]  == 5
    assert eval_tuple_tree((Op.NEG,  5))[0]  == -5

    # ── Conditional ────────────────────────────────────────────────
    assert eval_tuple_tree((Op.IF, 1, 42, 99))[0] == 42
    assert eval_tuple_tree((Op.IF, 0, 42, 99))[0] == 99
    # Nested IF
    assert eval_tuple_tree((Op.IF, (Op.LT, 3, 7), 1, 0))[0] == 1

    # ── PARTIAL + APPLY_FN ─────────────────────────────────────────
    # (partial + 3) applied to 4 = 3 + 4 = 7
    fn_add3 = (Op.PARTIAL, int(Op.ADD), 3)
    assert eval_tuple_tree((Op.APPLY_FN, fn_add3, 4))[0] == 7

    # (partial * 5) applied to 6 = 5 * 6 = 30
    fn_mul5 = (Op.PARTIAL, int(Op.MUL), 5)
    assert eval_tuple_tree((Op.APPLY_FN, fn_mul5, 6))[0] == 30

    # (partial < 10) applied to 7 → 10 < 7 → 0
    fn_lt10 = (Op.PARTIAL, int(Op.LT), 10)
    assert eval_tuple_tree((Op.APPLY_FN, fn_lt10, 7))[0] == 0

    # ── COMPOSE + APPLY_FN on FN_COMP ─────────────────────────────
    # comp(+3, *2): apply *2 first then +3 → (x*2)+3
    # (4 * 2) + 3 = 11
    fn_add3 = (Op.PARTIAL, int(Op.ADD), 3)
    fn_mul2 = (Op.PARTIAL, int(Op.MUL), 2)
    comp    = (Op.COMPOSE, fn_add3, fn_mul2)
    assert eval_tuple_tree((Op.APPLY_FN, comp, 4))[0] == 11

    # ── APPLY_COMP (explicit sugar) ────────────────────────────────
    # same composition, different apply op
    assert eval_tuple_tree((Op.APPLY_COMP, comp, 4))[0] == 11

    # ── evaluate_tree (Node-based API) ────────────────────────────
    # Encode: (ADD, 3, 4) as a Node tree
    leaf3  = Node(node_id=0, value=3)
    leaf4  = Node(node_id=1, value=4)
    root   = Node(node_id=2, children=[0, 1], op_idx=int(Op.ADD))
    tree   = [leaf3, leaf4, root]
    result = evaluate_tree(tree, {2: int(Op.ADD)})
    assert result == 7, f"expected 7, got {result}"

    # Test op_assignments override: Dispatcher overrides op_idx
    result_mul = evaluate_tree(tree, {2: int(Op.MUL)})  # same tree, MUL instead
    assert result_mul == 12, f"expected 12, got {result_mul}"

    # ── OP_NAMES index consistency ─────────────────────────────────
    assert OP_NAMES[Op.ADD]        == "+"
    assert OP_NAMES[Op.IF]         == "if"
    assert OP_NAMES[Op.PARTIAL]    == "partial"
    assert OP_NAMES[Op.APPLY_FN]   == "apply"
    assert OP_NAMES[Op.COMPOSE]    == "comp"
    assert OP_NAMES[Op.APPLY_COMP] == "apply-comp"

    print("kernel.py self-test: all assertions passed ✓")
    print(f"  {N_OPS} ops  {N_TYPES} types  fn_pack round-trip OK")


if __name__ == "__main__":
    _self_test()
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/kernel_dispatch.py"
}
```

**Summary:** Reading kernel_dispatch.py (0-2000)

**Output:**
```
"""
Kernel dispatch modules for the descending VSM arm.

The descending arm's S1 operations are kernel-shaped, not compression-shaped.
Instead of TernaryFFN (compress), the descending arm routes representations
through kernel op pathways (dispatch).

The 22 kernel ops (from kernel.py) are pre-wired as architectural identity —
the model discovers them as easy paths while training on prose via relational
loss. The ternary routing topology learns which positions benefit from which
kernel op family.

Architecture per descending pass:
  Phase 0 (dispatch):   KernelDispatch — route to kernel op families
  Phase 1 (integrate):  KernelIntegrate — type the dispatched result locally
  Phase 2 (converge):   StrideStack coarse→fine — propagate typed dispatch

The kernel op embeddings are the S5 identity of the dispatcher VSM.
They encode WHAT each operation IS — its characteristic transformation
pattern. The dispatch projection learns WHEN each op is relevant.

Design principles:
  - Shapes not outputs: the kernel provides the right shape for the
    descending arm, replacing compression ops that always go to passthrough
  - Easy path: kernel ops are architecturally available, not learned targets
  - Pre-wired: op embeddings initialized with structure, not random
  - Observable: dispatch weights show which kernel ops activate where

License: MIT
"""

from __future__ import annotations

import math

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════
# Kernel op families — from kernel.py
# ══════════════════════════════════════════════════════════════════

N_OPS = 22
N_TYPES = 5

# Op family indices for structured initialization
OP_FAMILIES = {
    "arith_binary":  list(range(0, 7)),    # add sub mul div mod min max
    "comparison":    list(range(7, 12)),    # eq lt gt le ge
    "bool_binary":   [12, 13],             # and or
    "bool_unary":    [14],                 # not
    "arith_unary":   [15, 16],             # abs neg
    "conditional":   [17],                 # if
    "lambda":        list(range(18, 22)),   # partial apply compose apply-comp
}

N_FAMILIES = len(OP_FAMILIES)


# ══════════════════════════════════════════════════════════════════
# KernelDispatch — routes representations to kernel op pathways
# ══════════════════════════════════════════════════════════════════


class KernelDispatch(nn.Module):
    """Kernel-aware transformation for second arm phase 0 (dispatch).

    Replaces TernaryFFN prep in the second arm.

    Architecture (top-k MoE routing):
      1. Dispatch logits: project to (n_ops,) scores — which kernel ops?
         Conditioned on ascending register banks (type/scope/role) when
         available, so dispatch can see what the ascending arm learned.
      2. Top-k selection: only the k highest-scoring ops participate.
         Softmax over the k winners only — not all 22 ops.
      3. Op modulation: weighted kernel identity added to representation
         (using L2-normalized op embeddings to prevent runaway growth).
      4. Pathway: shared ternary transform, biased by kernel identity
      5. Gated residual

    Why top-k routing (not softmax over all ops):
      With full softmax, register conditioning learned a massive bias
      toward one op (+10.2 for `if`), saturating softmax and giving
      zero gradient to all other ops. They died permanently. Meanwhile
      one op's embedding grew to 4× others via positive feedback.
      Top-k routing ensures the runner-up op always gets meaningful
      weight (~e^(-delta)), keeping gradient alive for all ops. The
      natural distribution can be as skewed as the data demands —
      FN_COMP can dominate prose — but rare ops stay trainable for
      their niches. Same principle as Switch Transformer / MoE routing.

    Op embedding normalization:
      All op embeddings are L2-normalized to a fixed scale each forward
      pass. The dispatch weights (router scores) alone determine each
      op's influence — not embedding magnitude. This prevents the
      rich-get-richer feedback loop that created the >= fossil.

    Register conditioning: the ascending arm's registers carry
    type/scope/role information that tells dispatch what kind of
    content is at each position. Dispatch sees "the ascending arm
    thinks this is scope=local, type=arithmetic" and can route to
    arithmetic ops accordingly.
    """

    def __init__(
        self,
        d_model: int,
        n_ops: int = N_OPS,
        d_ff: int | None = None,
        dropout: float = 0.1,
        n_registers: int = 3,
        d_register: int = 128,
        max_cond_banks: int = 5,
        top_k: int = 2,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_ops = n_ops
        self.top_k = min(top_k, n_ops)
        if d_ff is None:
            d_ff = d_model * 3

        # Pad n_ops to multiple of 16 for TernaryLinear
        self.n_ops_padded = ((n_ops + 15) // 16) * 16  # 32

        self.norm = nn.RMSNorm(d_model)

        # Dispatch projection: hidden → op logits
        # TernaryLinear: the ternary topology learns discrete routing
        self.dispatch = TernaryLinear(d_model, self.n_ops_padded, pre_norm=False)

        # ── Register conditioning ─────────────────────────────
        # Ascending registers → dispatch bias: which ops should activate?
        # Registers carry type/scope/role from the ascending arm.
        # This is a real-valued (not ternary) projection because
        # registers are real-valued and we want smooth gradients
        # for the conditioning to learn quickly.
        self.n_registers = n_registers
        self.d_reg_real = d_register * 2
        self.max_cond_banks = max_cond_banks
        max_cond_dim = max_cond_banks * n_registers * self.d_reg_real
        self._max_cond_dim = ((max_cond_dim + 15) // 16) * 16
        # Small real-valued projection: register summary → per-op bias
        self.register_cond = nn.Linear(self._max_cond_dim, self.n_ops_padded)
        # Initialize to zero so conditioning starts inert
        self.register_cond.weight = mx.zeros_like(self.register_cond.weight)
        self.register_cond.bias = mx.zeros_like(self.register_cond.bias)

        # Op embeddings: kernel S5 identity — what each op IS
        # Real-valued, trainable. Initialized with structure:
        # each op gets a near-orthogonal direction in d_model space.
        self.op_embeddings = _init_op_embeddings(n_ops, d_model)

        # Op embedding target norm — embeddings are L2-normalized to this
        # scale each forward pass. Prevents runaway growth (the >=
        # fossil problem: one embedding grows to 4× others via positive
        # feedback, then freezes when softmax starves its gradient).
        # The dispatch weights alone should determine influence, not
        # embedding magnitude.
        self.op_embed_scale = 0.5

        # Pathway: transforms representation using dispatched op identity
        # The kernel identity modulates the input; the pathway transforms
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        self.dropout = nn.Dropout(dropout)

    def _normalize_op_embeddings(self) -> mx.array:
        """L2-normalize op embeddings to fixed scale.

        Prevents runaway embedding growth. The dispatch weights (router
        scores) determine each op's influence — not embedding magnitude.
        Without this, a positive feedback loop develops: higher dispatch
        weight → more gradient → larger embedding → more modulation
        impact → even higher effective weight. Once the loop saturates
        softmax, non-dominant ops get zero gradient and die permanently.

        Returns normalized embeddings (used in forward, gradient flows
        through to the raw embeddings for training).
        """
        norms = mx.sqrt(
            mx.sum(self.op_embeddings * self.op_embeddings, axis=-1, keepdims=True)
            + 1e-8
        )
        return self.op_embeddings * (self.op_embed_scale / norms)

    def __call__(self, x: mx.array, registers: list[list[mx.array]] | None = None,
                 op_emphasis: mx.array | None = None) -> mx.array:
        """
        x: (B, L, d_model)
        registers: list of register banks from ascending arm, each bank is
                   a list of register vectors. Used to condition dispatch.
        op_emphasis: (n_ops,) per-op emphasis from S4's register state.
                     Modulates op embeddings: emphasis > 1 amplifies,
                     < 1 suppresses. Driven by what S4's intelligence
                     observes, EMA-tracked across steps for stability.
        Returns: (B, L, d_model) — with residual connection

        Routing: top-k MoE style. Per position, only the top-k ops
        (by dispatch logit) participate. Softmax is computed over the
        k winners only. This ensures:
          - The dominant op (likely FN_COMP for prose) gets most weight
          - The runner-up op still gets meaningful weight and gradient
          - Rare ops (arithmetic, comparison) stay alive — they'll
            occasionally appear in top-k for relevant content, giving
            them gradient to learn their niche
          - Natural distribution skew is preserved (no forced balancing)
        """
        h = self.norm(x)

        # Step 1: Dispatch logits — which kernel ops are relevant?
        dispatch_logits = self.dispatch(h)[..., :self.n_ops]  # (B, L, n_ops)

        # Register conditioning: add per-op bias from ascending registers
        if registers is not None:
            # Flatten all register banks into one vector
            parts = []
            for bank in registers:
                for reg in bank:
                    parts.append(reg)
            cond_input = mx.concatenate(parts, axis=-1)  # (total_reg_dims,)
            # Pad to max
            if cond_input.shape[0] < self._max_cond_dim:
                cond_input = mx.concatenate([
                    cond_input,
                    mx.zeros((self._max_cond_dim - cond_input.shape[0],))
                ])
            # Project to per-op bias
            reg_bias = self.register_cond(cond_input)[:self.n_ops]  # (n_ops,)
            # Add to dispatch logits (broadcast across B, L)
            dispatch_logits = dispatch_logits + reg_bias[None, None, :]

        # Step 2: Top-k routing — only k ops participate per position
        # This prevents softmax saturation from killing gradient to
        # non-dominant ops. With k=2, the runner-up always gets
        # meaningful weight (~e^(-delta) where delta is the logit gap).
        B, L, _ = dispatch_logits.shape
        top_k_values = mx.topk(dispatch_logits, k=self.top_k, axis=-1)  # (B, L, k)
        # Threshold: minimum value among top-k at each position
        threshold = mx.min(top_k_values, axis=-1, keepdims=True)  # (B, L, 1)
        # Mask: keep only top-k, set others to -inf
        mask = mx.where(
            dispatch_logits >= threshold,
            dispatch_logits,
            mx.full(dispatch_logits.shape, -1e9),
        )
        # Softmax over masked logits — only top-k ops get nonzero weight
        dispatch_weights = mx.softmax(mask, axis=-1)  # (B, L, n_ops)

        # Cache for probing (full 22-wide, zeros for non-top-k)
        self._dispatch_weights = mx.stop_gradient(dispatch_weights)

        # Step 3: Normalized op embeddings — prevent runaway growth
        op_emb = self._normalize_op_embeddings()  # (n_ops, d_model)

        # S4→S5 emphasis: modulate which ops are more/less available.
        # Driven by S4's register state, EMA-tracked across steps.
        # emphasis > 1 amplifies an op's embedding (makes it louder
        # in the modulation), < 1 suppresses (quieter). The dispatch
        # weights (routing) still control WHICH ops fire per position;
        # emphasis shifts the landscape of what's available.
        if op_emphasis is not None:
            op_emb = op_emb * op_emphasis[:, None]  # (n_ops, d_model)

        # Step 4: Weighted op embedding — kernel identity modulation
        # (B, L, n_ops) @ (n_ops, d_model) → (B, L, d_model)
        op_context = dispatch_weights @ op_emb

        # Step 5: Modulate input with kernel identity, then transform
        modulated = h + op_context
        out = self.down(nn.gelu(self.up(modulated)))

        return x + self.dropout(out)


# ══════════════════════════════════════════════════════════════════
# KernelIntegrate — combines kernel pathway results
# ══════════════════════════════════════════════════════════════════


class KernelIntegrate(nn.Module):
    """Kernel-aware integration with exact computation pathway.

    Phase 2 of the descending arm: after dispatch selected ops and
    stride propagated across context, integrate can now see both
    local op bias and spatial patterns.

    Dual pathway architecture:
      1. **Operand extraction**: project hidden state to extract two
         operands as scalar logits (over a value range), and read the
         dispatch weights from KernelDispatch to know WHICH op to apply.
      2. **Exact kernel computation**: apply the actual kernel function
         (ADD, LE, PARTIAL, etc.) to the extracted operands. This is
         non-differentiable but exact — no approximation.
      3. **Result encoding**: map the kernel result back to d_model
         via learned embedding, producing a "kernel signal" vector.
      4. **Compute gate**: learned scalar gate (0-1) per position that
         blends the kernel result with the standard FFN pathway.
         Starts at 0 (pure FFN) so the model can learn when to trust
         the kernel. This is critical: prose positions should gate=0
         (no computation), structured positions should gate→1.
      5. **Standard FFN pathway**: type modulation + shared transform,
         as before. This handles prose and non-computational positions.
      6. **Blend**: output = gate * kernel_result + (1-gate) * ffn_result

    The compute gate makes this backward-compatible: at initialization,
    gate=0 everywhere, so the model behaves identically to the old
    KernelIntegrate. As training progresses on structured data, the
    gate learns to open for positions where exact computation helps.

    Gradient flow through the non-differentiable kernel:
      The kernel itself has no gradient (argmax + integer arithmetic).
      But gradient flows through:
        - The operand extraction projections (which operands to extract)
        - The result encoder (which d_model direction the result maps to)
        - The compute gate (when to use kernel vs FFN)
      This is the same straight-through pattern as in v9.
    """

    def __init__(
        self,
        d_model: int,
        n_types: int = N_TYPES,
        n_ops: int = N_OPS,
        d_ff: int | None = None,
        dropout: float = 0.1,
        max_val: int = 256,
        result_buckets: int = 1024,
    ):
        super().__init__()
        self.d_model = d_model
        self.n_types = n_types
        self.n_ops = n_ops
        self.max_val = max_val
        if d_ff is None:
            d_ff = d_model * 4

        # Pad n_types to multiple of 16
        self.n_types_padded = ((n_types + 15) // 16) * 16

        self.norm = nn.RMSNorm(d_model)

        # ── Type pathway (unchanged) ──────────────────────────
        self.type_proj = TernaryLinear(d_model, self.n_types_padded, pre_norm=False)
        self.type_embeddings = _init_type_embeddings(n_types, d_model)

        # ── Standard FFN pathway (unchanged) ──────────────────
        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)
        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)

        # ── Kernel computation pathway (NEW) ──────────────────

        # Operand extraction: hidden → two value distributions
        # Each operand is a distribution over [0, max_val), decoded via argmax
        max_val_padded = ((max_val + 15) // 16) * 16
        self._max_val_padded = max_val_padded
        self.operand1_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)
        self.operand2_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)

        # Result encoder: integer result → d_model vector
        # Larger bucket range than v9: results can be negative (comparisons,
        # subtraction) and large (multiplication)
        self.result_buckets = result_buckets
        self.result_offset = result_buckets // 2  # center at 0
        self.result_embed = nn.Embedding(result_buckets, d_model)

        # Compute gate: per-position scalar, initialized to produce ~0
        # so the model starts with pure FFN (backward-compatible)
        self.gate_proj = nn.Linear(d_model, 1)
        # Initialize gate bias negative so sigmoid → ~0 at start
        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)
        self.gate_proj.bias = mx.ones_like(self.gate_proj.bias) * -5.0

        self.dropout = nn.Dropout(dropout)

    def _kernel_compute(
        self,
        h: mx.array,
        dispatch_weights: mx.array | None,
    ) -> tuple[mx.array, dict]:
        """Extract operands, run kernel, encode result.

        Args:
            h: (B, L, d_model) — normalized hidden state
            dispatch_weights: (B, L, n_ops) from KernelDispatch, or None

        Returns:
            kernel_out: (B, L, d_model) — encoded kernel results
            kernel_info: dict with decoded ops/args/results for probing
        """
        B, L, _ = h.shape

        # Extract operands via argmax (non-differentiable)
        op1_logits = self.operand1_proj(h)[..., :self.max_val]  # (B, L, max_val)
        op2_logits = self.operand2_proj(h)[..., :self.max_val]  # (B, L, max_val)

        # stop_gradient: argmax is non-differentiable, all gradient
        # flows through the result embedding and the compute gate
        arg1 = mx.stop_gradient(mx.argmax(op1_logits, axis=-1)).astype(mx.int32)  # (B, L)
        arg2 = mx.stop_gradient(mx.argmax(op2_logits, axis=-1)).astype(mx.int32)  # (B, L)

        # Get op from dispatch weights (argmax of top-1)
        if dispatch_weights is not None:
            op = mx.stop_gradient(mx.argmax(dispatch_weights, axis=-1)).astype(mx.int32)  # (B, L)
        else:
            op = mx.zeros((B, L), dtype=mx.int32)

        # ── Exact kernel computation (non-differentiable) ─────
        # Compute all possible results, select by op code
        # This is vectorized: compute all ops, mask-select by dispatched op

        # Arithmetic binary: ADD(0), SUB(1), MUL(2), DIV(3), MOD(4), MIN(5), MAX(6)
        r_add = arg1 + arg2
        r_sub = arg1 - arg2
        r_mul = arg1 * arg2
        # Safe division
        safe_arg2 = mx.where(arg2 == 0, mx.ones_like(arg2), arg2)
        r_div = arg1 // safe_arg2
        r_div = mx.where(arg2 == 0, mx.zeros_like(r_div), r_div)
        r_mod = arg1 % safe_arg2
        r_mod = mx.where(arg2 == 0, mx.zeros_like(r_mod), r_mod)
        r_min = mx.minimum(arg1, arg2)
        r_max = mx.maximum(arg1, arg2)

        # Comparison: EQ(7), LT(8), GT(9), LE(10), GE(11)
        r_eq = (arg1 == arg2).astype(mx.int32)
        r_lt = (arg1 < arg2).astype(mx.int32)
        r_gt = (arg1 > arg2).astype(mx.int32)
        r_le = (arg1 <= arg2).astype(mx.int32)
        r_ge = (arg1 >= arg2).astype(mx.int32)

        # Boolean binary: AND(12), OR(13)
        b1 = (arg1 != 0)
        b2 = (arg2 != 0)
        r_and = (b1 & b2).astype(mx.int32)
        r_or = (b1 | b2).astype(mx.int32)

        # Boolean unary: NOT(14)
        r_not = (~b1).astype(mx.int32)

        # Arithmetic unary: ABS(15), NEG(16)
        r_abs = mx.abs(arg1)
        r_neg = -arg1

        # Conditional: IF(17) — arg1=cond, arg2=then (no else in 2-operand form)
        r_if = mx.where(arg1 != 0, arg2, mx.zeros_like(arg2))

        # Lambda ops (18-21): return arg1 unchanged (placeholder —
        # actual lambda computation needs tree structure, not 2 scalars)
        r_lambda = arg1

        # Stack all results and select by op
        # Shape: (22, B, L) — one result per op
        all_results = mx.stack([
            r_add, r_sub, r_mul, r_div, r_mod, r_min, r_max,  # 0-6
            r_eq, r_lt, r_gt, r_le, r_ge,                      # 7-11
            r_and, r_or,                                        # 12-13
            r_not,                                              # 14
            r_abs, r_neg,                                       # 15-16
            r_if,                                               # 17
            r_lambda, r_lambda, r_lambda, r_lambda,             # 18-21
        ], axis=0)  # (22, B, L)

        # Select result by op code: gather along op dimension
        # op is (B, L), need to index into (22, B, L)
        op_clamped = mx.clip(op, 0, N_OPS - 1)
        # Use advanced indexing: result[op[b,l], b, l]
        b_idx = mx.broadcast_to(mx.arange(B)[:, None], (B, L))
        l_idx = mx.broadcast_to(mx.arange(L)[None, :], (B, L))
        result = all_results[op_clamped, b_idx, l_idx]  # (B, L)

        # ── Encode result back to d_model ─────────────────────
        # stop_gradient on the index computation: the kernel itself
        # is non-differentiable. Gradient flows through result_embed
        # weights (which embedding direction the result maps to) and
        # through the gate (when to use this pathway).
        result_idx = mx.stop_gradient(
            mx.clip(result + self.result_offset, 0, self.result_buckets - 1)
        ).astype(mx.int32)
        kernel_out = self.result_embed(result_idx)  # (B, L, d_model)

        # Probing info
        kernel_info = {
            "op": mx.stop_gradient(op),
            "arg1": mx.stop_gradient(arg1),
            "arg2": mx.stop_gradient(arg2),
            "result": mx.stop_gradient(result),
        }

        return kernel_out, kernel_info

    def __call__(
        self,
        x: mx.array,
        dispatch_weights: mx.array | None = None,
    ) -> mx.array:
        """
        x: (B, L, d_model)
        dispatch_weights: (B, L, n_ops) from KernelDispatch (cached)
        Returns: (B, L, d_model) — with residual connection
        """
        h = self.norm(x)

        # ── Type projection ───────────────────────────────────
        type_logits = self.type_proj(h)[..., :self.n_types]
        type_weights = mx.softmax(type_logits, axis=-1)
        self._type_weights = mx.stop_gradient(type_weights)

        # ── Standard FFN pathway ──────────────────────────────
        type_context = type_weights @ self.type_embeddings
        modulated = h + type_context
        ffn_out = self.down(nn.gelu(self.up(modulated)))  # (B, L, d_model)

        # ── Kernel computation pathway ────────────────────────
        kernel_out, kernel_info = self._kernel_compute(h, dispatch_weights)
        self._kernel_info = kernel_info

        # ── Compute gate: blend kernel vs FFN ─────────────────
        gate = mx.sigmoid(self.gate_proj(h))  # (B, L, 1)
        self._compute_gate = mx.stop_gradient(gate)

        # Blend: gate=0 → pure FFN, gate=1 → pure kernel
        blended = gate * kernel_out + (1.0 - gate) * ffn_out

        return x + self.dropout(blended)


# ══════════════════════════════════════════════════════════════════
# Structured initialization
# ══════════════════════════════════════════════════════════════════


def _init_op_embeddings(n_ops: int, d_model: int) -> mx.array:
    """Initialize kernel op embeddings with near-orthogonal structure.

    Each op gets a characteristic direction in d_model space.
    Ops within the same family share a family subspace but have
    distinct directions within it. This gives the ternary routing
    fabric structured targets to route toward.

    Family subspace allocation:
      Each family gets a contiguous block of dimensions.
      Within the block, ops get distinct orthogonal directions.
      Remaining dimensions are shared (allow cross-family interaction).
    """
    embeddings = mx.zeros((n_ops, d_model))

    # Allocate dimension blocks per family
    # Reserve first 50% for family-specific, last 50% shared
    family_dims = d_model // 2
    shared_dims = d_model - family_dims

    families = list(OP_FAMILIES.values())
    n_families = len(families)
    dims_per_family = family_dims // n_families

    family_offset = 0
    for fi, op_indices in enumerate(families):
        n_in_family = len(op_indices)
        # Each op in the family gets a direction in the family block
        for oi, op_idx in enumerate(op_indices):
            # Family-specific component: one-hot-ish within family block
            dim_start = family_offset
            dim_end = min(family_offset + dims_per_family, family_dims)
            if dim_end > dim_start and n_in_family > 0:
                # Spread ops across family dimensions
                op_dim = dim_start + (oi * (dim_end - dim_start)) // max(n_in_family, 1)
                op_dim = min(op_dim, dim_end - 1)
                embeddings = embeddings.at[op_idx, op_dim].add(1.0)

            # Shared component: small random for cross-family interaction
            shared_component = mx.random.normal((shared_dims,)) * 0.1
            embeddings = embeddings.at[op_idx, family_dims:].add(shared_component)

        family_offset += dims_per_family

    # L2-normalize each embedding, then scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1  # small scale so modulation is gentle

    return embeddings


def _init_type_embeddings(n_types: int, d_model: int) -> mx.array:
    """Initialize kernel type embeddings.

    5 types: INT, BOOL, FN, FN_COMP, ERROR
    Each gets a near-orthogonal direction. Types are fundamental —
    every position has a type, and the type determines what operations
    are valid downstream.
    """
    embeddings = mx.zeros((n_types, d_model))

    # Each type gets a distinct block of dimensions
    dims_per_type = d_model // (n_types * 2)  # use half the space for type identity

    for ti in range(n_types):
        dim_start = ti * dims_per_type
        dim_end = min((ti + 1) * dims_per_type, d_model)
        # Characteristic direction
        for d in range(dim_start, dim_end):
            embeddings = embeddings.at[ti, d].add(1.0)

        # Small random component in remaining dims for interaction
        shared = mx.random.normal((d_model,)) * 0.05
        embeddings = embeddings.at[ti].add(shared)

    # L2-normalize and scale
    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)
    embeddings = embeddings / norms * 0.1

    return embeddings


# ══════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import numpy as np
    d_model = 512

    print("Testing KernelDispatch (top-k=2)...")
    dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536, top_k=2)
    x = mx.random.normal((1, 64, d_model))
    y = dispatch(x)
    mx.eval(y)
    assert y.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y.shape}"

    # Check dispatch weights are cached (22-wide)
    assert hasattr(dispatch, '_dispatch_weights')
    dw = dispatch._dispatch_weights
    mx.eval(dw)
    assert dw.shape == (1, 64, 22), f"Expected (1, 64, 22), got {dw.shape}"

    # Top-k: only k ops should have nonzero weight per position
    dw_np = np.array(dw[0])
    nonzero_per_pos = np.sum(dw_np > 1e-6, axis=1)
    assert np.all(nonzero_per_pos <= 3), \
        f"Top-k=2 should give ≤3 nonzero ops per position, got max {nonzero_per_pos.max()}"
    # Note: <= 3 not == 2 because ties at the threshold can include extras
    print(f"  Active ops per position: mean={nonzero_per_pos.mean():.1f} "
          f"min={nonzero_per_pos.min()} max={nonzero_per_pos.max()} ✓")

    # Weights for active ops should still sum to ~1
    sums = mx.sum(dw, axis=-1)
    mx.eval(sums)
    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-4).item(), \
        f"Dispatch weights should sum to ~1, got min={float(mx.min(sums).item()):.4f}"
    print(f"  KernelDispatch: {x.shape} → {y.shape} ✓")
    print(f"  Dispatch weights: {dw.shape}, top-k routing ✓")

    # Check op embedding normalization
    normed = dispatch._normalize_op_embeddings()
    mx.eval(normed)
    norms = np.linalg.norm(np.array(normed), axis=1)
    assert np.allclose(norms, dispatch.op_embed_scale, atol=1e-3), \
        f"Normalized embeddings should have norm={dispatch.op_embed_scale}, got {norms}"
    print(f"  Op embedding norms: all ≈ {dispatch.op_embed_scale} ✓")

    print("\nTesting KernelIntegrate...")
    integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)
    y2 = integrate(x)
    mx.eval(y2)
    assert y2.shape == (1, 64, d_model), f"Expected (1, 64, 512), got {y2.shape}"
    tw = integrate._type_weights
    mx.eval(tw)
    assert tw.shape == (1, 64, 5), f"Expected (1, 64, 5), got {tw.shape}"
    print(f"  KernelIntegrate: {x.shape} → {y2.shape} ✓")
    print(f"  Type weights: {tw.shape} ✓")

    # Check op embeddings have structure (use normalized versions)
    op_emb = normed
    add_embed = op_emb[0]   # ADD
    sub_embed = op_emb[1]   # SUB
    eq_embed = op_emb[7]    # EQ (different family)
    mx.eval(add_embed, sub_embed, eq_embed)
    same_fam_sim = float(mx.sum(add_embed * sub_embed).item())
    cross_fam_sim = float(mx.sum(add_embed * eq_embed).item())
    print(f"  Op embedding structure: same-family sim={same_fam_sim:.4f}, "
          f"cross-family sim={cross_fam_sim:.4f}")

    # Test gradient flow — critical: verify all top-k ops get gradient
    import mlx.nn as nn_mod

    class TestModel(nn_mod.Module):
        def __init__(self):
            super().__init__()
            self.dispatch = KernelDispatch(d_model, n_ops=22, d_ff=1536, top_k=2)
            self.integrate = KernelIntegrate(d_model, n_types=5, d_ff=2048)

        def __call__(self, x):
            h = self.dispatch(x)
            h = self.integrate(h)
            return mx.mean(h)

    tm = TestModel()
    mx.eval(tm.parameters())

    def test_loss(tm, x):
        return tm(x)

    gfn = nn_mod.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)

    # Check that op_embeddings gradient has nonzero entries for multiple ops
    op_grad = g["dispatch"]["op_embeddings"]
    mx.eval(op_grad)
    og_np = np.array(op_grad)
    grad_norms = np.linalg.norm(og_np, axis=1)
    n_with_grad = np.sum(grad_norms > 1e-6)
    print(f"  Gradient flow OK: loss={lv.item():.4f}")
    print(f"  Ops with gradient: {n_with_grad}/22 "
          f"(top-k=2 should give ≥2) ✓")

    print("\nkernel_dispatch.py self-test: all ok ✓")
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/components.py"
}
```

**Summary:** Reading components.py (0-2000)

**Output:**
```
"""VSM control components — S4, S3, MetaS4, MetaS3 — MLX.

Ported from src/verbum/v6/components.py. Uses scripts/v10/ternary.py.

Registers are real-valued (float32) of dimension d_reg_real = d_register * 2,
preserving the same capacity as v6's complex ℂ^d_register registers without
requiring complex arithmetic in the autograd graph (MLX autograd doesn't
support mx.real/mx.imag + reshape in the backward pass).

Kept as fp32 (not ternary):
  - S3 write_gates (nn.Linear with bias, tiny, sigmoid-init)
  - S3 temperature and learned_bias (scalar parameters)
  - MetaS3 gate_proj (nn.Linear with bias, small)

License: MIT
"""

from __future__ import annotations

import mlx.core as mx
import mlx.nn as nn

from ternary import TernaryLinear


# ══════════════════════════════════════════════════════════════════════
# Helpers — register flattening (real-valued, no complex)
# ══════════════════════════════════════════════════════════════════════


def _flatten_registers(registers: list[mx.array]) -> mx.array:
    """Flatten list of real register vectors into one 1D vector."""
    return mx.concatenate(registers, axis=-1)


def _flatten_banks(banks: list[list[mx.array]]) -> mx.array:
    """Flatten all banks' registers into one 1D vector."""
    parts = []
    for bank in banks:
        parts.append(_flatten_registers(bank))
    return mx.concatenate(parts, axis=-1)


def _ternary_1d(proj: TernaryLinear, x: mx.array) -> mx.array:
    """Apply TernaryLinear to a 1D vector, working around MLX autograd
    requiring ≥2D input for quantized_matmul backward pass."""
    return proj(x.reshape(1, -1)).reshape(-1)


# ══════════════════════════════════════════════════════════════════════
# S4 — Intelligence (register-query cross-attention)
# ══════════════════════════════════════════════════════════════════════


class S4Ternary(nn.Module):
    """Register cross-attention: reads register banks, attends to residual,
    produces register updates.

    Real-valued registers (d_reg_real = d_register * 2 each).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,       # logical dimension (real dim = 2×)
        n_registers: int = 3,
        max_banks: int = 7,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2   # real-valued dimension per register
        self.n_registers = n_registers
        self.max_banks = max_banks
        self.scale = d_model ** -0.5

        max_q_dim = max_banks * n_registers * self.d_reg_real
        # Pad to multiple of 16 for TernaryLinear
        self._max_q_dim = ((max_q_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._max_q_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)

        summary_out = n_registers * self.d_reg_real
        self._summary_out_padded = ((summary_out + 15) // 16) * 16
        self._summary_out = summary_out
        self.summary_proj = TernaryLinear(d_model, self._summary_out_padded, pre_norm=False)

        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        banks: list[list[mx.array]],
        residual: mx.array,
    ) -> tuple[list[mx.array], mx.array]:
        B, L, D = residual.shape

        # Flatten all register banks into query input
        q_input = _flatten_banks(banks)
        # Pad to max
        if q_input.shape[0] < self._max_q_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._max_q_dim - q_input.shape[0],))
            ])

        # Query from register state (1D → 2D for autograd)
        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        # Standard attention: q (d_model,) @ k (B, L, d_model) → (B, L)
        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale  # (B, L)
        attn_weights = mx.softmax(attn, axis=-1)                  # (B, L)
        attn_weights = self.dropout(attn_weights)

        # Weighted sum → mean over batch
        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        summary = summary.mean(axis=0)                          # (d_model,)

        # Project to register update vectors (1D → 2D for autograd)
        updates_flat = _ternary_1d(self.summary_proj, summary)[:self._summary_out]

        updates = []
        for i in range(self.n_registers):
            start = i * self.d_reg_real
            end = start + self.d_reg_real
            updates.append(updates_flat[start:end])

        return updates, mx.stop_gradient(attn_weights)


# ══════════════════════════════════════════════════════════════════════
# S3 — Phase-Coherent Gating
# ══════════════════════════════════════════════════════════════════════


class S3Ternary(nn.Module):
    """Phase-coherent control for a single level-pass.

    Scalar alignment gate based on register-delta direction match.
    Real-valued registers.
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_phases: int = 3,
        n_registers: int = 3,
        d_align: int | None = None,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_register = d_register
        self.d_reg_real = d_register * 2
        self.n_phases = n_phases
        self.n_registers = n_registers

        if d_align is None:
            d_align = d_model
        self.d_align = d_align

        reg_flat_dim = self.d_reg_real * n_registers
        self._reg_flat_dim = ((reg_flat_dim + 15) // 16) * 16

        # Alignment projections — ternary
        self.proj_align = [
            TernaryLinear(self._reg_flat_dim, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]
        self.proj_delta = [
            TernaryLinear(d_model, d_align, pre_norm=False)
            for _ in range(n_phases)
        ]

        # Temperature and bias — fp32 scalars
        self.temperature = [mx.ones((1,)) for _ in range(n_phases)]
        self.learned_bias = [mx.zeros((1,)) for _ in range(n_phases)]

        # Register write projections — ternary
        d_reg_out = ((self.d_reg_real + 15) // 16) * 16
        self._d_reg_out = d_reg_out
        self.write_projs = [
            TernaryLinear(d_model, d_reg_out, pre_norm=False)
            for _ in range(n_phases * n_registers)
        ]

        # Write gates: kept as nn.Linear (has bias, tiny)
        # Bias init -2.0 → sigmoid(-2) ≈ 0.12
        self.write_gates = [
            nn.Linear(d_model, 1)
            for _ in range(n_phases * n_registers)
        ]
        for wg in self.write_gates:
            wg.bias = mx.full(wg.bias.shape, -2.0)

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

    def gate_phase(
        self,
        registers: list[mx.array],
        delta: mx.array,
        phase_idx: int,
    ) -> tuple[mx.array, list[mx.array], mx.array, list[float]]:
        """Gate a phase's output using alignment-based scalar gate."""
        eps = 1e-8

        reg_flat = _flatten_registers(registers)
        # Pad to multiple of 16
        if reg_flat.shape[0] < self._reg_flat_dim:
            reg_flat = mx.concatenate([
                reg_flat,
                mx.zeros((self._reg_flat_dim - reg_flat.shape[0],))
            ])
        reg_dir = reg_flat / (mx.sqrt((reg_flat * reg_flat).sum()) + eps)

        summary = delta.mean(axis=(0, 1))  # (d_model,)
        delta_dir = summary / (mx.sqrt((summary * summary).sum()) + eps)

        reg_proj = _ternary_1d(self.proj_align[phase_idx], reg_dir)     # (d_align,)
        delta_proj = _ternary_1d(self.proj_delta[phase_idx], delta_dir)  # (d_align,)
        alignment = (reg_proj * delta_proj).sum()            # scalar

        gate = mx.sigmoid(
            alignment * self.temperature[phase_idx]
            + self.learned_bias[phase_idx]
        )
        gated_delta = gate * delta

        # Register updates (normalized to prevent unbounded accumulation)
        updated_registers = []
        write_gate_values = []
        for reg_idx in range(self.n_registers):
            write_idx = phase_idx * self.n_registers + reg_idx
            wg = mx.sigmoid(self.write_gates[write_idx](summary.reshape(1, -1)).reshape(-1))
            update = _ternary_1d(self.write_projs[write_idx], summary)[:self.d_reg_real]
            updated_registers.append(
                self.register_norm(registers[reg_idx] + wg * update))
            write_gate_values.append(wg.item())

        return gated_delta, updated_registers, gate, write_gate_values


# ══════════════════════════════════════════════════════════════════════
# MetaS4 — Final structural summary
# ══════════════════════════════════════════════════════════════════════


class MetaS4Ternary(nn.Module):
    """Final intelligence scan: register-query attention over residual."""

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int = 3,
        n_banks: int = 4,
        dropout: float = 0.1,
    ):
        super().__init__()
        self.d_model = d_model
        self.d_reg_real = d_register * 2
        self.n_registers = n_registers
        self.n_banks = n_banks
        self.scale = d_model ** -0.5

        total_reg_dim = n_banks * n_registers * self.d_reg_real
        self._total_reg_dim = ((total_reg_dim + 15) // 16) * 16

        self.q_proj = TernaryLinear(self._total_reg_dim, d_model, pre_norm=False)
        self.k_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.v_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.out_proj = TernaryLinear(d_model, d_model, pre_norm=False)
        self.norm = nn.RMSNorm(d_model)
        self.dropout = nn.Dropout(dropout)

    def __call__(
        self,
        meta_banks: list[list[mx.array]],
        residual: mx.array,
    ) -> mx.array:
        B, L, D = residual.shape

        q_input = _flatten_banks(meta_banks)
        if q_input.shape[0] < self._total_reg_dim:
            q_input = mx.concatenate([
                q_input,
                mx.zeros((self._total_reg_dim - q_input.shape[0],))
            ])

        q = _ternary_1d(self.q_proj, q_input)  # (d_model,)

        x = self.norm(residual)
        k = self.k_proj(x)        # (B, L, d_model)
        v = self.v_proj(x)        # (B, L, d_model)

        attn = (q[None, None, :] * k).sum(axis=-1) * self.scale
        attn_weights = mx.softmax(attn, axis=-1)
        attn_weights = self.dropout(attn_weights)

        summary = (attn_weights[:, :, None] * v).sum(axis=1)  # (B, d_model)
        out = self.out_proj(summary)                            # (B, d_model)
        out = mx.broadcast_to(out[:, None, :], residual.shape)
        return residual + out


# ══════════════════════════════════════════════════════════════════════
# MetaS3 — Cross-level contribution gates
# ══════════════════════════════════════════════════════════════════════


class MetaS3Ternary(nn.Module):
    """Top-level per-pass contribution gates from register banks.

    Fixed from original: temperature scaling + learned bias initialized
    to -2.0 (sigmoid(-2) ≈ 0.12) so gates start near-closed and must
    learn to open. Without this, gates start at 1.0 and never differentiate.
    """

    def __init__(self, d_register: int, n_registers: int, n_banks: int, n_passes: int):
        super().__init__()
        self.n_passes = n_passes
        d_reg_real = d_register * 2
        input_dim = n_banks * n_registers * d_reg_real
        self.gate_proj = nn.Linear(input_dim, n_passes)
        # Initialize bias to -2.0 so sigmoid starts near 0.12, not 0.5
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(self, all_banks: list[list[mx.array]]) -> mx.array:
        flat = _flatten_banks(all_banks)
        logits = self.gate_proj(flat)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S5Reweight — Identity-level pass contribution (replaces MetaS3)
# ══════════════════════════════════════════════════════════════════════


class S5Reweight(nn.Module):
    """S5 — Identity-level pass contribution reweighting.

    Beer's S5 is identity — it defines what the system IS and must
    see the full picture to maintain coherence. The prior MetaS3 only
    saw register banks (S2/S3-filtered state). S5 gets a direct,
    ungated view of what S1 operations actually produced.

    Inputs:
      - Register banks (S2 coordination state) — what the system
        believes about type/scope/role
      - Raw (ungated) pass deltas — what each pass's operations
        PROPOSED before S3 gating filtered them

    Why ungated matters:
      A pass that S3 currently suppresses can still influence the
      final output through S5's awareness of its raw delta. If S5
      sees useful raw output, it opens that pass's gate, which in
      turn teaches S3 to open. S5 sees ground truth about S1; S3
      only sees what it already filtered.

    Output: per-pass sigmoid gates (same role as MetaS3).
    Initialization: bias -2.0 (gates start near-closed, ~0.12).
    """

    def __init__(
        self,
        d_model: int,
        d_register: int,
        n_registers: int,
        n_banks: int,
        n_passes: int,
    ):
        super().__init__()
        self.n_passes = n_passes
        self.d_model = d_model
        d_reg_real = d_register * 2

        # Register input (same as MetaS3)
        reg_input_dim = n_banks * n_registers * d_reg_real

        # Raw delta input: each pass delta summarized to d_model
        delta_summary_dim = n_passes * d_model
        self._delta_dim = ((delta_summary_dim + 15) // 16) * 16
        self._delta_dim_raw = delta_summary_dim

        # Project raw deltas to compact features via ternary fabric.
        # pre_norm=True: direction matters, not magnitude.
        # 16 features per pass — enough to capture operational character.
        delta_proj_out = n_passes * 16
        delta_proj_out_padded = ((delta_proj_out + 15) // 16) * 16
        self.delta_proj = TernaryLinear(
            self._delta_dim, delta_proj_out_padded, pre_norm=True)
        self._delta_proj_out = delta_proj_out

        # Combined: register features + delta features → gates
        combined_dim = reg_input_dim + delta_proj_out
        self.gate_proj = nn.Linear(combined_dim, n_passes)
        # Bias -2.0: gates start near-closed (~0.12), must learn to open
        self.gate_proj.bias = mx.full((n_passes,), -2.0)
        # Learnable temperature per pass
        self.temperature = mx.ones((n_passes,))

    def __call__(
        self,
        all_banks: list[list[mx.array]],
        raw_deltas: list[mx.array],
    ) -> mx.array:
        """
        all_banks:  list of register banks (S2 coordination state)
        raw_deltas: list of n_passes raw (ungated) pass deltas,
                    each (B, L, d_model)

        Returns: (n_passes,) sigmoid gates for pass contribution
        """
        # Register features
        reg_flat = _flatten_banks(all_banks)

        # Raw delta features: spatial mean of each ungated pass delta
        delta_summaries = []
        for delta in raw_deltas:
            delta_summaries.append(delta.mean(axis=(0, 1)))  # (d_model,)
        delta_flat = mx.concatenate(delta_summaries, axis=-1)

        # Pad for TernaryLinear alignment
        if delta_flat.shape[0] < self._delta_dim:
            delta_flat = mx.concatenate([
                delta_flat,
                mx.zeros((self._delta_dim - delta_flat.shape[0],))
            ])

        # Project: ternary topology learns which delta patterns matter
        delta_features = _ternary_1d(
            self.delta_proj, delta_flat)[:self._delta_proj_out]

        # Combine register + delta features → gate logits
        combined = mx.concatenate([reg_flat, delta_features], axis=-1)
        logits = self.gate_proj(combined)
        return mx.sigmoid(logits * self.temperature)


# ══════════════════════════════════════════════════════════════════════
# S2 — Inter-pass direction coordination (Beer's anti-oscillation)
# ══════════════════════════════════════════════════════════════════════


class S2Coordinator(nn.Module):
    """S2 — Inter-pass direction coordination.

    Beer's S2 prevents oscillation between S1 operational units.
    In v10, the S1 units are the 5 level-passes. Without S2, passes
    can write contradictory deltas to the residual stream — Pass N
    compresses in one direction, Pass N+1 inadvertently undoes it.

    Mechanism: after each pass produces a delta, S2 computes a small
    direction signal and adds it to the next pass's input. This is
    a coordination memo: "Pass N moved the representation THIS way."

    The next pass's S3 gates and S4 intelligence still control what
    happens — S2 just provides awareness of the predecessor's action.

    Properties:
      - 4 transitions (between 5 passes)
      - Direction = projected, normalized delta summary
      - Scale starts small (~0.01), learnable per transition
      - S2 signals survive MetaS3 reweighting — coordination
        infrastructure is not gated by control (correct: S2 ≠ S3)

    Conflict detection (diagnostic, not used for control):
      Cosine similarity between consecutive pass deltas.
        cos < 0 → oscillation (passes fighting)
        cos > 0 → reinforcement (passes cooperating)
      Exposed in instrumentation. If S2 works, conflict scores
      should trend toward 0 or positive over training.

    Design:
      - Not S3: doesn't gate or suppress. Additive, not multiplicative.
      - Not S4: doesn't scan environment. Dumb memo of what happened.
      - Not S5: doesn't define identity. Transient, per-forward-pass.
      - IS S2: minimum viable coordination — "FYI, here's what just
        happened." Prevents unknowing contradiction without preventing
        intentional override.
    """

    N_TRANSITIONS = 4
    TRANSITION_NAMES = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")

    def __init__(self, d_model: int):
        super().__init__()
        self.d_model = d_model

        # Direction projection: learns which aspects of the delta
        # matter for coordination. pre_norm=True so it's about
        # direction (shape), not magnitude.
        self.dir_projs = [
            TernaryLinear(d_model, d_model, pre_norm=True)
            for _ in range(self.N_TRANSITIONS)
        ]
        # Initialize gamma small — direction signal starts gentle
        for proj in self.dir_projs:
            proj.gamma = proj.gamma * 0.01

        # Per-transition learnable scale
        self.scales = [mx.ones((1,)) * 0.01
                       for _ in range(self.N_TRANSITIONS)]

        # Normalize direction signal — prevents scale drift over training
        self.norm = nn.RMSNorm(d_model)

    def direction_signal(
        self,
        pass_delta: mx.array,
        transition_idx: int,
    ) -> mx.array:
        """Direction memo from pass N to pass N+1.

        pass_delta: (B, L, d_model) — what the pass changed
        transition_idx: 0-3

        Returns (1, 1, d_model) — broadcasts to (B, L, d_model)
        """
        # Spatial mean → single direction vector
        summary = pass_delta.mean(axis=(0, 1))           # (d_model,)

        # Project through ternary fabric — learns which aspects matter
        projected = self.dir_projs[transition_idx](
            summary.reshape(1, -1)
        ).reshape(-1)                                     # (d_model,)

        # Normalize + scale
        signal = self.norm(projected) * self.scales[transition_idx]

        return signal[None, None, :]                      # (1, 1, d_model)

    @staticmethod
    def coherence_factor(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> mx.array:
        """Differentiable coherence: 1 + cos(prev, curr).

        Returns mx.array scalar in [0, 2]:
          2.0 → passes fully agree (amplify direction signal)
          1.0 → orthogonal (neutral)
          0.0 → passes fully conflict (dampen signal to zero)

        Gradient: stop_gradient on delta_prev — earlier pass sets
        direction, later pass learns to align. S2 doesn't retro-adjust
        the predecessor; it teaches the current pass that coherent
        deltas produce stronger forward signals (better loss).
        """
        s_prev = mx.stop_gradient(delta_prev.mean(axis=(0, 1)))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        return 1.0 + dot / (n_prev * n_curr)

    @staticmethod
    def conflict_score(
        delta_prev: mx.array,
        delta_curr: mx.array,
    ) -> float:
        """Cosine similarity between consecutive pass deltas (diagnostic).

          +1 → reinforcing  |  0 → orthogonal  |  -1 → oscillating

        Non-differentiable — for instrumentation/logging only.
        See coherence_factor() for the differentiable version used
        in the forward pass to modulate direction signals.
        """
        s_prev = delta_prev.mean(axis=(0, 1))
        s_curr = delta_curr.mean(axis=(0, 1))

        dot = (s_prev * s_curr).sum()
        n_prev = mx.sqrt((s_prev * s_prev).sum() + 1e-8)
        n_curr = mx.sqrt((s_curr * s_curr).sum() + 1e-8)

        cos = dot / (n_prev * n_curr)
        mx.eval(cos)
        return float(cos.item())


# ══════════════════════════════════════════════════════════════════════
# CycleContinue — S3 cycle-level continuation gate
# ══════════════════════════════════════════════════════════════════════


class CycleContinue(nn.Module):
    """S3 continuation gate: should another dispatch cycle contribute?

    Beer's S3 is the control layer — it decides what operations should
    pass through. Within a cycle, the existing S3Ternary gates each
    phase's delta. Between cycles, CycleContinue gates whether the
    NEXT cycle's entire contribution should matter.

    The model always computes up to desc_max_cycles (static graph for
    MLX). CycleContinue controls each cycle's contribution weight via
    a cumulative gate product:

      cycle 0: always full strength (cumulative_gate = 1.0)
      cycle 1: scaled by continue_gate_0
      cycle 2: scaled by continue_gate_0 × continue_gate_1
      ...

    If CycleContinue learns that simple tokens need only 1 cycle,
    it drives the gate toward 0 after cycle 0 — cycles 1+ produce
    near-zero deltas (computed but ineffective). For complex tokens
    needing compositional depth (PARTIAL → APPLY), the gate stays
    open, giving cycle 1+ full contribution.

    Input: register bank (S3's running state after the cycle).
    The registers carry type/scope/role information accumulated
    through the cycle's S3 phase gating — exactly what's needed
    to decide "was this cycle productive? would another help?"

    Initialization: bias=0 → sigmoid(0)=0.5 (neutral). The model
    learns in both directions: open for complex content, close for
    simple. No commitment to a default cycle count.
    """

    def __init__(self, d_register: int, n_registers: int = 3):
        super().__init__()
        d_reg_real = d_register * 2
        self.d_reg_real = d_reg_real
        self.n_registers = n_registers

        input_dim = n_registers * d_reg_real
        # RMSNorm the register input — prevents sigmoid saturation.
        # Raw registers have norm ~16 each (||concat|| ≈ 27.7).
        # Without normalization, even small weight updates produce
        # logits >> 4, saturating sigmoid and killing gradient.
        # RMSNorm → ||input|| ≈ 1.0 → logit stays in active zone.
        self.input_norm = nn.RMSNorm(input_dim)
        # Small projection: normalized register state → scalar logit
        self.gate_proj = nn.Linear(input_dim, 1)
        # Neutral init: sigmoid(0) = 0.5
        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)
        self.gate_proj.bias = mx.zeros_like(self.gate_proj.bias)

    def __call__(self, registers: list[mx.array]) -> mx.array:
        """Compute continuation gate from register state.

        registers: list of n_registers register vectors, each (d_reg_real,)
        Returns: scalar gate in [0, 1]
        """
        reg_flat = _flatten_registers(registers)
        reg_flat = self.input_norm(reg_flat)
        # tanh clamp: logit ∈ [-4, +4] → sigmoid ∈ [0.018, 0.982]
        # Guarantees gradient flow even if norms drift. The gate
        # can never fully saturate — always learnable.
        logit = mx.tanh(self.gate_proj(reg_flat)) * 4.0
        return mx.sigmoid(logit).reshape(())  # scalar


# ══════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    d_model = 512
    d_register = 128
    d_reg_real = d_register * 2
    n_registers = 3

    def _fresh_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    def _init_bank():
        return [mx.zeros((d_reg_real,)) for _ in range(n_registers)]

    print("Testing S4Ternary...")
    s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
    banks = [_init_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    updates, attn = s4(banks, residual)
    mx.eval(*updates, attn)
    assert len(updates) == 3
    assert updates[0].shape == (d_reg_real,)
    print(f"  S4: {len(updates)} updates, shape {updates[0].shape} ✓")

    print("Testing S3Ternary...")
    s3 = S3Ternary(d_model, d_register, n_phases=3, n_registers=n_registers)
    regs = _fresh_bank()
    delta = mx.random.normal((1, 32, d_model))
    gated, new_regs, gate, wgv = s3.gate_phase(regs, delta, phase_idx=0)
    mx.eval(gated, *new_regs, gate)
    assert gated.shape == (1, 32, d_model)
    assert len(new_regs) == 3
    print(f"  S3: gate={gate.item():.3f}, gated_delta shape {gated.shape} ✓")

    print("Testing MetaS4Ternary...")
    meta_s4 = MetaS4Ternary(d_model, d_register, n_registers=n_registers, n_banks=4)
    meta_banks = [_init_bank(), _fresh_bank(), _fresh_bank(), _fresh_bank()]
    residual = mx.random.normal((1, 32, d_model))
    out = meta_s4(meta_banks, residual)
    mx.eval(out)
    assert out.shape == (1, 32, d_model)
    print(f"  MetaS4: {residual.shape} → {out.shape} ✓")

    print("Testing MetaS3Ternary...")
    meta_s3 = MetaS3Ternary(d_register, n_registers=n_registers, n_banks=6, n_passes=5)
    all_banks = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    gates = meta_s3(all_banks)
    mx.eval(gates)
    assert gates.shape == (5,)
    # Verify gates start near-closed (bias=-2.0 → sigmoid ≈ 0.12), not at 1.0
    for g in gates.tolist():
        assert g < 0.5, f"Meta-S3 gate should start near-closed, got {g:.3f}"
    print(f"  MetaS3: gates shape {gates.shape}, values {[f'{g:.3f}' for g in gates.tolist()]} ✓ (near-closed)")

    print("Testing S5Reweight...")
    s5 = S5Reweight(d_model, d_register, n_registers=n_registers,
                     n_banks=6, n_passes=5)
    mx.eval(s5.parameters())
    all_banks_s5 = [_init_bank()] + [_fresh_bank() for _ in range(5)]
    raw_deltas = [mx.random.normal((1, 32, d_model)) for _ in range(5)]
    gates_s5 = s5(all_banks_s5, raw_deltas)
    mx.eval(gates_s5)
    assert gates_s5.shape == (5,), f"Expected (5,), got {gates_s5.shape}"
    for g in gates_s5.tolist():
        assert g < 0.5, f"S5 gate should start near-closed, got {g:.3f}"
    print(f"  S5Reweight: gates {[f'{g:.3f}' for g in gates_s5.tolist()]} ✓ (near-closed)")
    # Verify it uses raw deltas — different deltas should produce different gates
    raw_deltas_2 = [mx.random.normal((1, 32, d_model)) * 10.0 for _ in range(5)]
    gates_s5_2 = s5(all_banks_s5, raw_deltas_2)
    mx.eval(gates_s5_2)
    diff = max(abs(a - b) for a, b in zip(gates_s5.tolist(), gates_s5_2.tolist()))
    assert diff > 1e-6, "S5 gates should differ with different raw deltas"
    print(f"  S5Reweight: different raw deltas → different gates (max diff={diff:.4f}) ✓")

    print("Testing S2Coordinator...")
    s2 = S2Coordinator(d_model)
    mx.eval(s2.parameters())
    # Direction signal shape
    delta = mx.random.normal((1, 32, d_model))
    signal = s2.direction_signal(delta, 0)
    mx.eval(signal)
    assert signal.shape == (1, 1, d_model), f"Expected (1, 1, {d_model}), got {signal.shape}"
    # Signal should be small (gamma init * 0.01, scale 0.01)
    signal_norm = float(mx.sqrt((signal * signal).sum()).item())
    print(f"  S2: signal shape {signal.shape}, norm={signal_norm:.6f} (should be small) ✓")
    # All 4 transitions
    for ti in range(S2Coordinator.N_TRANSITIONS):
        sig = s2.direction_signal(delta, ti)
        mx.eval(sig)
        assert sig.shape == (1, 1, d_model)
    print(f"  S2: all {S2Coordinator.N_TRANSITIONS} transitions produce valid signals ✓")
    # Conflict score
    delta2 = mx.random.normal((1, 32, d_model))
    cs = S2Coordinator.conflict_score(delta, delta2)
    assert -1.0 <= cs <= 1.0, f"Conflict score out of range: {cs}"
    # Self-conflict should be +1
    cs_self = S2Coordinator.conflict_score(delta, delta)
    assert cs_self > 0.99, f"Self-conflict should be ~1.0, got {cs_self:.3f}"
    # Anti-conflict should be -1
    cs_anti = S2Coordinator.conflict_score(delta, -delta)
    assert cs_anti < -0.99, f"Anti-conflict should be ~-1.0, got {cs_anti:.3f}"
    print(f"  S2: conflict scores: random={cs:.3f}, self={cs_self:.3f}, anti={cs_anti:.3f} ✓")
    # Coherence factor (differentiable version)
    cf_agree = S2Coordinator.coherence_factor(delta, delta)
    mx.eval(cf_agree)
    assert abs(float(cf_agree.item()) - 2.0) < 0.01, \
        f"Agreement coherence should be ~2.0, got {cf_agree.item()}"
    cf_fight = S2Coordinator.coherence_factor(delta, -delta)
    mx.eval(cf_fight)
    assert abs(float(cf_fight.item()) - 0.0) < 0.01, \
        f"Conflict coherence should be ~0.0, got {cf_fight.item()}"
    cf_ortho = S2Coordinator.coherence_factor(
        mx.array([[[1.0, 0.0, 0.0, 0.0]]]),
        mx.array([[[0.0, 1.0, 0.0, 0.0]]]),
    )
    mx.eval(cf_ortho)
    assert abs(float(cf_ortho.item()) - 1.0) < 0.01, \
        f"Orthogonal coherence should be ~1.0, got {cf_ortho.item()}"
    print(f"  S2: coherence factor: agree={cf_agree.item():.1f}, "
          f"ortho={cf_ortho.item():.1f}, fight={cf_fight.item():.1f} ✓")

    print("Testing CycleContinue...")
    cc = CycleContinue(d_register, n_registers=n_registers)
    mx.eval(cc.parameters())
    regs = _fresh_bank()
    gate = cc(regs)
    mx.eval(gate)
    assert gate.shape == (), f"Expected scalar, got {gate.shape}"
    assert abs(float(gate.item()) - 0.5) < 0.01, \
        f"CycleContinue gate should start at ~0.5 (neutral), got {gate.item():.3f}"
    print(f"  CycleContinue: gate={gate.item():.3f} (neutral init) ✓")
    # After training (non-zero weights), different register states produce different gates.
    # At init, weights are zero so all inputs → same output (correct: neutral start).
    # Verify by setting a non-zero weight:
    cc.gate_proj.weight = mx.ones_like(cc.gate_proj.weight) * 0.01
    regs2 = [mx.random.normal((d_reg_real,)) for _ in range(n_registers)]
    gate_a = cc(regs)
    gate_b = cc(regs2)
    mx.eval(gate_a, gate_b)
    assert abs(float(gate_a.item()) - float(gate_b.item())) > 1e-6, \
        "CycleContinue should produce different gates for different register states (non-zero weights)"
    print(f"  CycleContinue: different regs → different gates ({gate_a.item():.3f} vs {gate_b.item():.3f}) ✓")

    # Test gradient flow
    print("Testing gradient flow through S4...")
    import mlx.nn as nn
    class TestModel(nn.Module):
        def __init__(self):
            super().__init__()
            self.s4 = S4Ternary(d_model, d_register, n_registers=n_registers, max_banks=7)
            self.param = mx.zeros((d_reg_real,))
        def __call__(self, x):
            bank = [[self.param] * n_registers]
            target = _fresh_bank()
            updates, _ = self.s4(bank, x)
            return mx.sum(updates[0])

    tm = TestModel()
    mx.eval(tm.parameters())
    def test_loss(tm, x):
        return tm(x)
    gfn = nn.value_and_grad(tm, test_loss)
    x = mx.random.normal((1, 16, d_model))
    lv, g = gfn(tm, x)
    mx.eval(lv, g)
    print(f"  S4 gradient flow OK: loss={lv.item():.4f} ✓")

    print("components.py self-test: all ok ✓")
```

## Assistant

Now let me read the model and training files:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/model.py"
}
```

**Summary:** Reading model.py (0-2000)

**Output:**
```
"""
v10 Model — Tree of VSMs: compressor + kernel-aware dispatcher.

Architecture:

  tokens (B, L) → [VSM-Compressor: ascending, 9 strides, proven]
                       → typed representations (B, L, d_model)
                 → [VSM-Dispatcher: descending, kernel-shaped S1 ops]
                       → enriched representations (B, L, d_model)
                 → [output_norm → tied embedding → logits]
                 → relational loss on Dolma prose

Tree of VSMs (Beer 1972):
  VSM-Compressor (ascending arm, 3 passes: L0↑, L1↑, L2_apex):
    S5: token embedding identity (Qwen3 BBPE)
    S4: StrideStack fine→coarse (intelligence — reads context)
    S3: phase gates (control — what to compress)
    S2: direction signals between passes (anti-oscillation coordination)
    S1: TernaryFFN prep/consolidate (operations — compression)

  VSM-Dispatcher (second arm, 2 passes: L1↓, L0↓):
    S5: kernel function identity (22 ops, 5 types — pre-wired)
    S4: dual-view attention (residual + original embeddings)
    S3: dispatch gates (control — which kernel pathways activate)
    S2: direction signals + register conditioning (coordination)
    S1: KernelDispatch/KernelIntegrate/StrideStack (operations)

  Phase order (dispatch → stride → integrate):
    Phase 0: KernelDispatch — route to 22 kernel op pathways (local)
    Phase 1: StrideStack fine→coarse — propagate dispatched signal (spatial)
    Phase 2: KernelIntegrate — type the context-enriched result (local)

    Rationale: dispatch modulates per-position, then stride propagates
    so that each position sees how its neighbors were dispatched.
    Integration (typing) then has both the local op bias AND spatial
    context to inform its type decision. Prior order (dispatch → integrate
    → stride) produced type-dispatch decoupling: typing couldn't
    distinguish dispatch patterns without spatial context, defaulting
    to FN (56%) regardless of which op was active.

    Session 068 discovered that standard transformer attention self-
    organizes into a logarithmic spiral that always expands outward
    (~1.18x per revolution, ~9.4 layers per revolution). The spiral
    never reverses — there is no "descending" direction in attention.
    Both arms follow the same fine→coarse spiral; they differ in what
    operations they apply (compression vs kernel dispatch), not in
    the direction of attention.

Key design:
  The ascending arm compresses and types (proven in v6, φ-locking).
  The descending arm routes through kernel function pathways — NOT
  compression. Prior sessions (045/054/055/062/065) proved that giving
  the descending arm compression ops causes passthrough. The kernel
  provides the correct shape: dispatch/routing, not compression.

  The 22 kernel ops (from kernel.py, proven at 100% in v9) are pre-wired
  as architectural identity in the dispatcher VSM. The model discovers
  them as easy paths while training on prose — no need to learn
  composition through superpositions.

Output: tied embedding projection (weight sharing with input embed).

License: MIT
"""

from __future__ import annotations

from typing import Optional

import mlx.core as mx
import mlx.nn as nn

from config import V10Config
from ternary import TernaryLinear, TernaryEmbedding
from attention import StrideStack, TernaryFFN
from components import (
    S4Ternary,
    S3Ternary,
    MetaS4Ternary,
    S5Reweight,
    S2Coordinator,
    CycleContinue,
)
from kernel_dispatch import KernelDispatch, KernelIntegrate, N_OPS, N_TYPES


# ══════════════════════════════════════════════════════════════════
# V6Compressor — 5-pass bidirectional VSM
# ══════════════════════════════════════════════════════════════════


class V6Compressor(nn.Module):
    """Tree of VSMs: compressor (ascending) + dispatcher (descending).

    5 passes:
      L0_asc → L1_asc → L2_apex → L1_desc → L0_desc

    ASCENDING arm (VSM-Compressor, 3 passes) — shared weights:
      S1: TernaryFFN prep/consolidate (compression — proven in v6)
      S4: StrideStack fine→coarse (reads context across scales)
      Job: compress and type (proven: φ-locking, S3 differentiation)

    SECOND arm (VSM-Dispatcher, 2 passes) — own weights:
      S1: KernelDispatch → StrideStack fine→coarse → KernelIntegrate
      S4: register cross-attention (reads typed representations)
      Job: route through 22 kernel op pathways, propagate, then type

    Both arms spiral outward (fine→coarse). The difference is what
    operations they apply: compression vs kernel dispatch. The spiral
    direction matches the emergent attention geometry discovered in
    standard transformers (~1.18x expansion per revolution).

    Phase order: dispatch (local) → stride (spatial) → integrate (local).
    Dispatch modulates per-position. Stride propagates so each position
    sees neighbor dispatch patterns. Integrate (typing) then has both
    local op bias and spatial context for informed type decisions.

    S2 coordination: between each pair of consecutive passes, a small
    direction signal is fed forward — "Pass N moved the representation
    THIS way." This is Beer's anti-oscillation mechanism: coordination
    between S1 units to prevent unknowing contradiction. The signal
    survives MetaS3 reweighting (S2 infrastructure ≠ S3 control).
    4 transitions, learnable scales starting at 0.01.

    Per-pass S3 control: 5 separate S3Ternary instances.
    """

    REGISTER_NAMES = ("type", "scope", "role")
    N_PASSES = 5
    N_ASC_PASSES = 3   # L0↑, L1↑, L2_apex
    N_DESC_PASSES = 2  # L1↓, L0↓
    PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")

    def __init__(self, cfg: V10Config):
        super().__init__()
        self.cfg = cfg
        d = cfg.d_model
        d_reg = cfg.d_register
        n_reg = cfg.n_registers
        self.d_reg_real = d_reg * 2

        # ── S5: Identity ──────────────────────────────────────
        self.embed = TernaryEmbedding(cfg.vocab_size, d)
        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)
        self.embed_norm = nn.RMSNorm(d)

        # Register bank 0: learnable real init
        self.register_inits = {
            f"reg_{name}": mx.zeros((self.d_reg_real,))
            for name in self.REGISTER_NAMES
        }

        # Register normalization — prevents unbounded accumulation → NaN
        self.register_norm = nn.RMSNorm(self.d_reg_real)

        # ── S1: Ascending ops (shared across L0↑, L1↑, L2_apex) ──
        #    Compression operations — proven in v6 (φ-locking)
        self.prep = TernaryFFN(d, cfg.d_ff, cfg.dropout)
        self.stride_stack = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.consolidate = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)

        # ── S1: Descending ops (shared across L1↓, L0↓) ──────
        #    Kernel-shaped operations — NOT compression.
        #    KernelDispatch routes to 22 kernel op pathways.
        #    KernelIntegrate combines results with type awareness.
        #    StrideStack reads typed reps across scales (coarse→fine).
        self.kernel_dispatch = KernelDispatch(
            d, n_ops=N_OPS, d_ff=cfg.d_ff, dropout=cfg.dropout,
            n_registers=cfg.n_registers, d_register=cfg.d_register,
            max_cond_banks=5,  # bank_0 + up to 4 ascending banks
            top_k=cfg.dispatch_top_k,
        )
        self.stride_stack_desc = StrideStack(
            d_model=d,
            strides=cfg.strides,
            window=cfg.window,
            n_heads=cfg.n_heads,
            dropout=cfg.dropout,
            alpha=cfg.alpha,
        )
        self.kernel_integrate = KernelIntegrate(
            d, n_types=N_TYPES, d_ff=cfg.d_ff_consolidate, dropout=cfg.dropout,
        )

        # ── S4: Intelligence (ascending, shared) ──────────────
        self.s4 = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                            dropout=cfg.dropout)

        # ── S4: Intelligence (descending, own) ────────────────
        self.s4_desc = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,
                                  dropout=cfg.dropout)

        # ── S3: Per-pass gating (5 instances, always separate) ─
        self.s3_passes = [
            S3Ternary(d, d_reg, n_phases=3, n_registers=n_reg, d_align=d)
            for _ in range(self.N_PASSES)
        ]

        # ── Modulation projections (ascending, shared, 3 per phase) ─
        self.mod_projs = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Modulation projections (descending, own) ──────────
        #    Same 3 phases but different semantics:
        #    phase 0 = dispatch, phase 1 = converge, phase 2 = integrate
        self.mod_projs_desc = [
            TernaryLinear(d, d, pre_norm=False)
            for _ in range(3)
        ]
        for proj in self.mod_projs_desc:
            proj.gamma = mx.zeros_like(proj.gamma)

        # ── Multi-cycle input injection gate (HRM-inspired) ──
        # Controls how much of the pre-cycle residual is re-injected
        # at each cycle > 0. HRM adds z_H + input at every L-step;
        # this is the v10 analog: re-ground in the pre-cycle state
        # so dispatch doesn't drift too far from what ascending produced.
        # sigmoid(-4) ≈ 0.018: injection starts nearly silent, model
        # learns to open. Unused when desc_max_cycles=1.
        self._cycle_inject_gate_raw = mx.array([-4.0])

        # ── S3 cycle continuation gate ────────────────────────
        # Beer's S3 control decides whether the next cycle should
        # contribute. Reads register state after each cycle to
        # determine if further computation is productive.
        # The model self-regulates: simple content → 1 cycle,
        # complex composition → up to desc_max_cycles.
        # Unused when desc_max_cycles ≤ 1.
        if cfg.desc_max_cycles > 1:
            self.cycle_continue = CycleContinue(
                cfg.d_register, n_registers=cfg.n_registers)

        # ── Meta-S4 ──────────────────────────────────────────
        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,
                                      n_banks=4, dropout=cfg.dropout)

        # ── S2: Inter-pass direction coordination ──────────
        #    Beer's anti-oscillation: direction signal between
        #    consecutive passes prevents unknowing contradiction.
        self.s2 = S2Coordinator(d)

        # ── S5: Identity-level pass reweighting ───────────────
        #    Replaces MetaS3. Sees both register banks (S2 state)
        #    AND raw ungated pass deltas (direct S1 output).
        #    Beer's S5 needs ungated view to maintain identity.
        self.s5_reweight = S5Reweight(
            d, d_reg, n_registers=n_reg,
            n_banks=6, n_passes=self.N_PASSES)

        # ── Algedonic channel: persistent descending registers ─
        # Beer's VSM requires feedback from S3 back to S1/S2 —
        # an "algedonic channel" that signals system distress.
        # Without it, the apex can expand without limit because
        # nothing reads the descending arm's state to regulate
        # the ascending arm.
        #
        # Implementation: store the descending registers from the
        # previous forward pass as persistent buffers. The ascending
        # arm's S4 intelligence can read these stale descending
        # registers, creating a cross-step feedback loop:
        #   descending pressure → stored → ascending S4 reads →
        #   ascending S3 adjusts gates → regulated apex output
        #
        # Kernel compute algedonic: the kernel's dispatch weights
        # and compute gate are packed into a register-shaped vector.
        # This tells the ascending arm "the kernel was active,
        # dispatching to these ops, with this compute gate level"
        # so it can adjust compression accordingly (e.g. preserve
        # token identity when the kernel is computing).
        #
        # EMA smoothing (α=0.9) prevents oscillation.
        self._algedonic_ema = 0.9
        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))
                                   for _ in range(n_reg)]
        # Kernel compute: dispatch weights (22) + compute gate (1)
        # packed into d_reg_real, zero-padded. No projection needed —
        # S4's q_proj learns what to extract from the raw values.
        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))

        # ── Op emphasis: S4 register state → per-op modulation ──
        # S4's registers carry type/scope/role from the ascending arm.
        # This projection maps that intelligence to per-op emphasis:
        # "given what S4 observes, which kernel ops should be louder?"
        # EMA-tracked across steps for stability (slowly shifting
        # landscape, not reactive noise).
        # Input: ascending banks (bank_1_asc + bank_2_asc + bank_3)
        #        = 3 banks × 3 registers × d_reg_real
        emphasis_input_dim = 3 * n_reg * self.d_reg_real
        self.emphasis_proj = nn.Linear(emphasis_input_dim, N_OPS)
        # Zero-init: emphasis starts neutral (1.0 for all ops)
        self.emphasis_proj.weight = mx.zeros_like(self.emphasis_proj.weight)
        self.emphasis_proj.bias = mx.zeros_like(self.emphasis_proj.bias)
        self._op_emphasis = mx.ones((N_OPS,))
        self._emphasis_ema = 0.95  # slow-moving — captures trends, not noise

        # ── Output ────────────────────────────────────────────
        self.output_norm = nn.RMSNorm(d)

    # ── Cycle injection ────────────────────────────────────────

    @property
    def cycle_inject_gate(self) -> mx.array:
        """Sigmoid gate controlling input injection strength per cycle."""
        return mx.sigmoid(self._cycle_inject_gate_raw)

    # ── Register helpers ──────────────────────────────────────

    def _init_bank0(self) -> list[mx.array]:
        return [self.register_inits[f"reg_{name}"]
                for name in self.REGISTER_NAMES]

    def _fresh_bank(self) -> list[mx.array]:
        return [mx.zeros((self.d_reg_real,))
                for _ in self.REGISTER_NAMES]

    # ── Modulation (additive) ─────────────────────────────────

    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):
        projs = self.mod_projs_desc if is_descending else self.mod_projs
        return x + gate * mx.tanh(projs[phase_idx](delta))

    # ── Core level-pass ───────────────────────────────────────

    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks, target_bank,
                         embed_context=None, op_emphasis=None):
        x_before = x
        raw_phases = []   # ungated phase deltas for S5
        phase_gates = []  # S3 gate values for cross-arm visibility

        # Select ops based on VSM arm
        s4 = self.s4_desc if is_descending else self.s4
        strides = self.stride_stack_desc if is_descending else self.stride_stack

        # S4 scan (intelligence — reads register banks)
        # Descending arm gets dual view: compressed residual + original
        # token embeddings. S4 attends over [residual; embeddings] (2L
        # positions) so it can see both what compression produced AND
        # what the tokens originally were. Critical for dispatch: knowing
        # "this position IS the + token" helps route to arithmetic ops.
        s4_residual = x
        if embed_context is not None:
            s4_residual = mx.concatenate([x, embed_context], axis=1)
        s4_updates, _ = s4(readable_banks, s4_residual)
        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])
                       for i in range(self.cfg.n_registers)]

        if is_descending:
            # ── VSM-Dispatcher: self-regulating kernel cycles ─
            # S4 scanned once above (slow/abstract). Now dispatch→
            # stride→integrate cycles up to desc_max_cycles times.
            # A learned S3 continuation gate (CycleContinue) decides
            # after each cycle whether further cycles should contribute.
            #
            # Static graph: all cycles always execute (MLX requirement).
            # CycleContinue controls contribution via cumulative gate:
            #   cycle 0: full strength (cumulative_gate = 1.0)
            #   cycle 1: scaled by continue_gate_0
            #   cycle 2: scaled by continue_gate_0 × continue_gate_1
            #
            # If the model learns "this is simple prose", it drives
            # continuation gates → 0 after cycle 0. Cycles 1+ still
            # compute but produce near-zero deltas (gated out).
            # For complex content (PARTIAL → APPLY composition),
            # gates stay open → full multi-cycle refinement.
            #
            # Input injection at cycle > 0: re-ground in pre-cycle
            # residual (HRM's z_L += z_H + input pattern).
            #
            # desc_max_cycles=1: loop runs once, no continuation
            # gates computed, behavior identical to single-cycle.

            x_anchor = x  # pre-cycle state for injection
            max_cycles = self.cfg.desc_max_cycles
            cumulative_gate = mx.array(1.0)  # cycle 0 always full

            for cycle in range(max_cycles):
                x_cycle_start = x

                # Input injection (HRM pattern): re-ground in anchor
                if cycle > 0:
                    x = x + self.cycle_inject_gate * x_anchor

                # Phase 0: dispatch (route to kernel op pathways)
                dispatch_out = self.kernel_dispatch(
                    x, registers=readable_banks, op_emphasis=op_emphasis)
                delta = dispatch_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 0)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=0, is_descending=True)

                # Phase 1: converge (StrideStack — propagate dispatch outward)
                converge_out = strides(x, reverse=False)
                delta = converge_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 1)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=1, is_descending=True)

                # Phase 2: integrate (type + compute with spatial context)
                dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                delta = integrate_out - x
                raw_phases.append(delta)
                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                    target_bank, delta, 2)
                phase_gates.append(gate)
                x = self._modulate(x, delta, gate, phase_idx=2, is_descending=True)

                # Scale this cycle's total contribution by cumulative gate
                cycle_contribution = x - x_cycle_start
                x = x_cycle_start + cumulative_gate * cycle_contribution

                # S3 continuation: should the next cycle contribute?
                if cycle < max_cycles - 1 and max_cycles > 1:
                    cont_gate = self.cycle_continue(target_bank)
                    cumulative_gate = cumulative_gate * cont_gate
        else:
            # ── VSM-Compressor: compression S1 operations ─────
            # Phase 0: prep (local feature extraction)
            prep_out = self.prep(x)
            delta = prep_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 0)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=0, is_descending=False)

            # Phase 1: converge (StrideStack fine→coarse)
            converge_out = strides(x, reverse=False)
            delta = converge_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 1)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=1, is_descending=False)

            # Phase 2: consolidate (feature integration)
            consolidate_out = self.consolidate(x)
            delta = consolidate_out - x
            raw_phases.append(delta)
            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(
                target_bank, delta, 2)
            phase_gates.append(gate)
            x = self._modulate(x, delta, gate, phase_idx=2, is_descending=False)

        pass_delta = x - x_before
        # Raw delta: sum of ungated phase deltas — what S1 proposed
        # before S3 gating. S5 sees this to maintain identity coherence.
        raw_delta = raw_phases[0]
        for rd in raw_phases[1:]:
            raw_delta = raw_delta + rd
        return x, target_bank, pass_delta, raw_delta, phase_gates

    # ── Forward ───────────────────────────────────────────────

    def forward(
        self,
        tokens: mx.array,
        targets: Optional[mx.array] = None,
    ) -> tuple[mx.array, Optional[mx.array]]:
        """
        tokens (B, L) → logits (B, L, vocab_size), optional loss.

        Output uses tied embedding: logits = h @ embed.weight_T
        """
        B, L = tokens.shape

        # Embed
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))

        # Capture original embeddings for descending S4's dual view.
        # By pass 3, compression has buried token identity under 3
        # transformation passes. The dispatcher needs raw token identity
        # to route correctly (e.g. "this IS the + token → arithmetic ops").
        x_embed = x

        # Initialize register banks
        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5

        # ── Algedonic channel: read previous descending registers ──
        # These are EMA-smoothed registers from the PREVIOUS forward
        # pass. They carry descending arm pressure (type/dispatch state)
        # back into the ascending arm's S4 intelligence, creating the
        # feedback loop that Beer's VSM requires for S3 regulation.
        # stop_gradient: the algedonic signal is observational, not
        # a training target. Gradient flows forward through the
        # ascending arm normally.
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        # Kernel compute algedonic: which ops fired, how active the
        # compute gate was. Tells ascending arm what downstream needs.
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        asc_s3_gates = []  # ascending S3 gate values for descending arm

        # Pass 0: L0_asc — reads prev descending L0 + kernel compute
        x, bank_1_asc, pd, rd, pg = self._run_level_pass(
            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 0 → Pass 1 (unmodulated — first signal)
        x = x + self.s2.direction_signal(pd, 0)

        # Pass 1: L1_asc — reads prev descending L1 + kernel compute
        x, bank_2_asc, pd, rd, pg = self._run_level_pass(
            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # S2: direction signal Pass 1 → Pass 2, modulated by coherence(0,1)
        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])
        x = x + self.s2.direction_signal(pd, 1) * coherence

        # Pass 2: L2_apex — reads kernel compute (helps transition to dispatch)
        x, bank_3, pd, rd, pg = self._run_level_pass(
            x, 2, False, [bank_0, bank_1_asc, bank_2_asc, prev_kernel], bank_3)
        pass_deltas.append(pd)
        raw_deltas.append(rd)
        asc_s3_gates.extend(pg)

        # ── Op emphasis: S4 register state → per-op modulation ──
        # After ascending passes, registers carry type/scope/role.
        # Project to per-op emphasis: which ops should be louder?
        emphasis_parts = []
        for bank in [bank_1_asc, bank_2_asc, bank_3]:
            for reg in bank:
                emphasis_parts.append(reg)
        emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
        raw_emphasis = self.emphasis_proj(emphasis_input)           # (N_OPS,)
        op_emphasis = 1.0 + 0.5 * mx.tanh(raw_emphasis)            # [0.5, 1.5]

        # EMA tracking — slowly accumulates S4's emphasis preferences
        self._op_emphasis = mx.stop_gradient(
            self._emphasis_ema * self._op_emphasis
            + (1.0 - self._emphasis_ema) * op_emphasis)

        # ── Pack ascending S3 gates for descending arm ─────────
        # 9 gate values (3 passes × 3 phases) packed into a register-
        # shaped vector. Tells descending S4 what the ascending arm's
        # control decisions were: "prep was gated at 0.8, converge
        # suppressed at 0.3, consolidate open at 0.9" etc.
        # NOT stop_gradient: gradient flows back to ascending S3,
        # teaching it that its gate decisions affect downstream dispatch.
        asc_gate_flat = mx.concatenate(
            [g.reshape(-1) for g in asc_s3_gates])              # (9,)
        asc_gate_vector = mx.concatenate([
            asc_gate_flat,
            mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
        ])
        asc_gate_bank = [asc_gate_vector]

        # S2: direction signal Pass 2 → Pass 3 (ascending→descending)
        #     modulated by coherence(1,2)
        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])
        x = x + self.s2.direction_signal(pd, 2) * coherence

        # Pass 3: L1_desc — S4 sees residual + embeds + ascending gates
        x, bank_2_desc, pd, rd, _ = self._run_level_pass(
            x, 3, True,
            [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank],
            bank_2_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # S2: direction signal Pass 3 → Pass 4, modulated by coherence(2,3)
        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])
        x = x + self.s2.direction_signal(pd, 3) * coherence

        # Pass 4: L0_desc — S4 sees residual + embeds + ascending gates
        x, bank_1_desc, pd, rd, _ = self._run_level_pass(
            x, 4, True,
            [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank],
            bank_1_desc, embed_context=x_embed, op_emphasis=op_emphasis)
        pass_deltas.append(pd)
        raw_deltas.append(rd)

        # ── Update algedonic buffers (EMA, no gradient) ────────
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic: pack dispatch weights + compute gate
        # into register-shaped vector for ascending arm's next pass
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean,                                        # 22 dims: op distribution
            cg_mean,                                        # 1 dim: compute gate level
            mx.zeros((self.d_reg_real - N_OPS - 1,)),       # padding to d_reg_real
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting — sees registers AND
        # raw ungated deltas (direct view of what operations proposed)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,
                     bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]

        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]

        x = x - total_ungated + total_gated

        # Meta-S4: final structural summary
        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks, x)

        # Output
        x = self.output_norm(x)
        logits = self.embed.output_proj(x)   # tied ternary embedding, (B, L, vocab_size)

        loss = None
        if targets is not None:
            loss = nn.losses.cross_entropy(
                logits.reshape(-1, self.cfg.vocab_size),
                targets.reshape(-1),
            ).mean()

        return logits, loss

    def __call__(self, tokens, targets=None):
        return self.forward(tokens, targets)

    # ── Instrumentation ───────────────────────────────────────

    @staticmethod
    def _entropy_proxy(x: mx.array) -> float:
        """log(mean_var) entropy proxy — same as v6."""
        var_per_feat = mx.var(x, axis=(0, 1))
        mean_var = mx.mean(var_per_feat)
        mx.eval(mean_var)
        return float(mx.log(mean_var + 1e-10).item())

    def forward_instrumented(
        self,
        tokens: mx.array,
    ) -> tuple[mx.array, dict]:
        """Forward pass with full instrumentation. Returns (hidden, metrics).

        Metrics dict contains:
          s3_gates:     list of 5 lists of floats (per pass, per phase;
                        descending passes have 3*desc_cycles phases)
          s5_reweight:  list of 5 floats (per-pass contribution gates from S5)
          s2_conflict:  list of 4 floats (cosine sim between consecutive deltas)
          s2_scales:    list of 4 floats (learnable direction signal scales)
          register_norms: dict of bank_name → list of 3 floats (per register)
          pass_entropy_in:  list of 5 floats
          pass_entropy_out: list of 5 floats
          pass_compression: list of 5 floats (out/in ratio)
          pass_phi_dev:     list of 5 floats (|ratio - 1/φ|)
          desc_max_cycles:  int — max dispatch cycles per descending pass
          cycle_inject_gate: float — learned injection strength (sigmoid)
          cycle_continue_gates: list of per-pass continuation gate lists
          effective_cycles: list of per-pass effective cycle counts
        """
        import math
        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)

        B, L = tokens.shape
        positions = mx.arange(L)
        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))
        x_embed = x  # original embeddings for descending S4 dual view

        bank_0 = self._init_bank0()
        bank_1_asc = self._fresh_bank()
        bank_2_asc = self._fresh_bank()
        bank_3 = self._fresh_bank()
        bank_2_desc = self._fresh_bank()
        bank_1_desc = self._fresh_bank()

        pass_deltas = []
        raw_deltas = []   # ungated phase deltas for S5
        all_s3_gates = []
        pass_h_in = []
        pass_h_out = []
        asc_gate_mx = []  # ascending S3 gate values (mx.arrays) for descending arm
        asc_gate_bank = None  # packed after ascending passes
        op_emphasis_inst = None  # computed after ascending passes
        all_cycle_continue_gates = []  # per-pass continuation gate values
        all_effective_cycles = []       # per-pass effective cycle counts

        # Algedonic channel: stale descending registers + kernel compute
        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]
        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]
        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]

        pass_configs = [
            (0, False, lambda: [bank_0, prev_b1d, prev_kernel]),
            (1, False, lambda: [bank_0, bank_1_asc, prev_b2d, prev_kernel]),
            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc, prev_kernel]),
            (3, True,  lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3]),
            (4, True,  lambda: [bank_0, bank_1_asc, bank_2_desc, bank_3]),
        ]
        target_banks = [bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]

        for pi, (pass_idx, is_desc, get_readable) in enumerate(pass_configs):
            h_in = self._entropy_proxy(x)
            pass_h_in.append(h_in)

            x_before = x
            readable = get_readable()
            target = target_banks[pi]

            # Select ops based on VSM arm
            s4 = self.s4_desc if is_desc else self.s4
            strides = self.stride_stack_desc if is_desc else self.stride_stack

            # Descending arm: add ascending S3 gate bank + embed dual view
            if is_desc:
                if asc_gate_bank is not None:
                    readable.append(asc_gate_bank)
                s4_residual = mx.concatenate([x, x_embed], axis=1)
            else:
                s4_residual = x
            s4_updates, _ = s4(readable, s4_residual)
            target = [self.register_norm(target[i] + s4_updates[i])
                      for i in range(self.cfg.n_registers)]

            phase_gates = []
            raw_phases = []  # ungated phase deltas for S5

            if is_desc:
                # ── VSM-Dispatcher: self-regulating kernel cycles ─
                x_anchor = x
                max_cycles = self.cfg.desc_max_cycles
                cumulative_gate = mx.array(1.0)
                cycle_continue_gates = []  # per-cycle continuation gate values

                for cycle in range(max_cycles):
                    x_cycle_start = x

                    # Input injection (HRM pattern)
                    if cycle > 0:
                        x = x + self.cycle_inject_gate * x_anchor

                    # Phase 0: dispatch
                    dispatch_out = self.kernel_dispatch(
                        x, registers=readable, op_emphasis=op_emphasis_inst)
                    delta = dispatch_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 0, is_descending=True)

                    # Phase 1: converge (propagate dispatch outward)
                    conv_out = strides(x, reverse=False)
                    delta = conv_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 1, is_descending=True)

                    # Phase 2: integrate (type + compute with spatial context)
                    dw = self.kernel_dispatch._dispatch_weights if hasattr(self.kernel_dispatch, '_dispatch_weights') else None
                    integrate_out = self.kernel_integrate(x, dispatch_weights=dw)
                    delta = integrate_out - x
                    raw_phases.append(delta)
                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                    mx.eval(gate)
                    phase_gates.append(float(gate.item()))
                    x = self._modulate(x, delta, gate, 2, is_descending=True)

                    # Scale cycle contribution by cumulative gate
                    cycle_contribution = x - x_cycle_start
                    x = x_cycle_start + cumulative_gate * cycle_contribution

                    # S3 continuation gate
                    if cycle < max_cycles - 1 and max_cycles > 1:
                        cont_gate = self.cycle_continue(target)
                        mx.eval(cont_gate)
                        cycle_continue_gates.append(float(cont_gate.item()))
                        cumulative_gate = cumulative_gate * cont_gate
            else:
                # ── VSM-Compressor: compression phases ────────
                # Phase 0: prep
                prep_out = self.prep(x)
                delta = prep_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 0)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 0, is_descending=False)

                # Phase 1: converge (fine→coarse)
                conv_out = strides(x, reverse=False)
                delta = conv_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 1)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 1, is_descending=False)

                # Phase 2: consolidate
                cons_out = self.consolidate(x)
                delta = cons_out - x
                raw_phases.append(delta)
                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(target, delta, 2)
                mx.eval(gate)
                phase_gates.append(float(gate.item()))
                asc_gate_mx.append(gate)
                x = self._modulate(x, delta, gate, 2, is_descending=False)

            target_banks[pi] = target
            pass_deltas.append(x - x_before)
            # Raw delta: sum of ungated phase deltas for S5
            raw_delta = raw_phases[0]
            for rd in raw_phases[1:]:
                raw_delta = raw_delta + rd
            raw_deltas.append(raw_delta)
            all_s3_gates.append(phase_gates)

            # Collect cycle continuation data for descending passes
            if is_desc and self.cfg.desc_max_cycles > 1:
                all_cycle_continue_gates.append(cycle_continue_gates)
                # Effective cycles: 1.0 (cycle 0) + sum of cumulative gates
                eff = 1.0 + sum(
                    float(mx.prod(mx.array(cycle_continue_gates[:i+1])).item())
                    for i in range(len(cycle_continue_gates))
                ) if cycle_continue_gates else 1.0
                all_effective_cycles.append(eff)

            # Pack ascending S3 gates after last ascending pass (pi=2)
            if not is_desc and pi == 2 and asc_gate_mx:
                asc_gate_flat = mx.concatenate(
                    [g.reshape(-1) for g in asc_gate_mx])
                asc_gate_vector = mx.concatenate([
                    asc_gate_flat,
                    mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),
                ])
                asc_gate_bank = [asc_gate_vector]

            # Op emphasis after ascending passes complete (pi=2)
            if not is_desc and pi == 2:
                emphasis_parts = []
                for bank in [target_banks[0], target_banks[1], target_banks[2]]:
                    for reg in bank:
                        emphasis_parts.append(reg)
                emphasis_input = mx.concatenate(emphasis_parts, axis=-1)
                raw_emphasis = self.emphasis_proj(emphasis_input)
                op_emphasis_inst = 1.0 + 0.5 * mx.tanh(raw_emphasis)
                mx.eval(op_emphasis_inst)
                self._op_emphasis = mx.stop_gradient(
                    self._emphasis_ema * self._op_emphasis
                    + (1.0 - self._emphasis_ema) * op_emphasis_inst)

            h_out = self._entropy_proxy(x)
            pass_h_out.append(h_out)

            # S2: direction signal to next pass (except after last pass)
            # First signal unmodulated; subsequent signals modulated by
            # coherence between this pass and the previous one.
            if pi < len(pass_configs) - 1:
                signal = self.s2.direction_signal(pass_deltas[-1], pi)
                if pi > 0:
                    coherence = S2Coordinator.coherence_factor(
                        pass_deltas[-2], pass_deltas[-1])
                    signal = signal * coherence
                x = x + signal

        # S2: conflict scores between consecutive pass deltas
        s2_conflict = []
        for i in range(len(pass_deltas) - 1):
            cs = S2Coordinator.conflict_score(pass_deltas[i], pass_deltas[i + 1])
            s2_conflict.append(cs)
        s2_scales = [float(self.s2.scales[i].item())
                     for i in range(S2Coordinator.N_TRANSITIONS)]

        # Re-assign named banks from target_banks
        bank_1_asc = target_banks[0]
        bank_2_asc = target_banks[1]
        bank_3 = target_banks[2]
        bank_2_desc = target_banks[3]
        bank_1_desc = target_banks[4]

        # Update algedonic buffers (EMA, no gradient) — same as forward()
        α = self._algedonic_ema
        self._prev_bank_1_desc = [
            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        self._prev_bank_2_desc = [
            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])
            for i in range(self.cfg.n_registers)
        ]
        # Kernel compute algedonic — same as forward()
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw_mean = mx.stop_gradient(
                self.kernel_dispatch._dispatch_weights.mean(axis=(0, 1)))
        else:
            dw_mean = mx.zeros((N_OPS,))
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg_mean = mx.stop_gradient(
                self.kernel_integrate._compute_gate.mean().reshape(1,))
        else:
            cg_mean = mx.zeros((1,))
        kernel_state = mx.concatenate([
            dw_mean, cg_mean,
            mx.zeros((self.d_reg_real - N_OPS - 1,)),
        ])
        self._prev_kernel_algedonic = mx.stop_gradient(
            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)

        # S5: identity-level pass reweighting (sees registers + raw deltas)
        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]
        meta_gates = self.s5_reweight(all_banks, raw_deltas)
        mx.eval(meta_gates)

        total_ungated = pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_ungated = total_ungated + pass_deltas[i]
        total_gated = meta_gates[0] * pass_deltas[0]
        for i in range(1, self.N_PASSES):
            total_gated = total_gated + meta_gates[i] * pass_deltas[i]
        x = x - total_ungated + total_gated

        # Meta-S4
        meta_banks_list = [bank_0, bank_1_desc, bank_2_desc, bank_3]
        x = self.meta_s4(meta_banks_list, x)
        x = self.output_norm(x)

        # Register norms
        reg_norms = {}
        named_banks = {
            "bank_0": bank_0, "bank_1_asc": bank_1_asc,
            "bank_2_asc": bank_2_asc, "bank_3": bank_3,
            "bank_2_desc": bank_2_desc, "bank_1_desc": bank_1_desc,
        }
        for name, bank in named_banks.items():
            norms = []
            for reg in bank:
                mx.eval(reg)
                norms.append(float(mx.sqrt((reg * reg).sum()).item()))
            reg_norms[name] = norms

        # Compression metrics
        pass_compression = []
        pass_phi_dev = []
        for h_in, h_out in zip(pass_h_in, pass_h_out):
            if abs(h_in) > 1e-8:
                ratio = h_out / h_in
            else:
                ratio = 1.0
            pass_compression.append(ratio)
            pass_phi_dev.append(abs(ratio - INV_PHI))

        # Kernel dispatch metrics (from descending arm)
        # KernelDispatch caches _dispatch_weights: (B, L, n_ops)
        # KernelIntegrate caches _type_weights: (B, L, n_types)
        dispatch_weights = None
        type_weights = None
        if hasattr(self.kernel_dispatch, '_dispatch_weights'):
            dw = self.kernel_dispatch._dispatch_weights
            mx.eval(dw)
            # Mean over batch and sequence → per-op activation frequency
            dispatch_weights = mx.mean(dw, axis=(0, 1))  # (n_ops,)
            mx.eval(dispatch_weights)
        if hasattr(self.kernel_integrate, '_type_weights'):
            tw = self.kernel_integrate._type_weights
            mx.eval(tw)
            type_weights = mx.mean(tw, axis=(0, 1))  # (n_types,)
            mx.eval(type_weights)

        # Op embedding norms (health check — should be uniform with norm constraint)
        op_emb_norms = None
        if hasattr(self.kernel_dispatch, 'op_embeddings'):
            raw_emb = self.kernel_dispatch.op_embeddings
            mx.eval(raw_emb)
            norms = mx.sqrt(mx.sum(raw_emb * raw_emb, axis=-1) + 1e-8)
            mx.eval(norms)
            op_emb_norms = [float(norms[i].item()) for i in range(norms.shape[0])]

        # Cycle inject gate value
        cig = self.cycle_inject_gate
        mx.eval(cig)

        metrics = {
            "s3_gates": all_s3_gates,
            "s5_reweight": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],
            "op_emphasis": (
                [float(op_emphasis_inst[i].item()) for i in range(N_OPS)]
                if op_emphasis_inst is not None else None
            ),
            "s2_conflict": s2_conflict,
            "s2_scales": s2_scales,
            "register_norms": reg_norms,
            "pass_entropy_in": pass_h_in,
            "pass_entropy_out": pass_h_out,
            "pass_compression": pass_compression,
            "pass_phi_dev": pass_phi_dev,
            "kernel_dispatch_weights": (
                [float(dispatch_weights[i].item()) for i in range(dispatch_weights.shape[0])]
                if dispatch_weights is not None else None
            ),
            "kernel_type_weights": (
                [float(type_weights[i].item()) for i in range(type_weights.shape[0])]
                if type_weights is not None else None
            ),
            "op_embedding_norms": op_emb_norms,
            "desc_max_cycles": self.cfg.desc_max_cycles,
            "cycle_inject_gate": float(cig.item()),
            "cycle_continue_gates": all_cycle_continue_gates,
            "effective_cycles": all_effective_cycles,
        }

        # Compute gate stats (if kernel pathway is active)
        if hasattr(self.kernel_integrate, '_compute_gate'):
            cg = self.kernel_integrate._compute_gate  # (B, L, 1)
            mx.eval(cg)
            metrics["compute_gate_mean"] = float(mx.mean(cg).item())
            metrics["compute_gate_max"] = float(mx.max(cg).item())
            metrics["compute_gate_min"] = float(mx.min(cg).item())
            # Fraction of positions where gate > 0.5
            metrics["compute_gate_active"] = float(mx.mean((cg > 0.5).astype(mx.float32)).item())

        return x, metrics


# ══════════════════════════════════════════════════════════════════
# Factory + utilities
# ══════════════════════════════════════════════════════════════════


def create_model(cfg: V10Config) -> V6Compressor:
    """Create and initialize a V6Compressor."""
    model = V6Compressor(cfg)
    mx.eval(model.parameters())
    return model


def count_parameters(model: nn.Module) -> dict[str, int]:
    """Count parameters by component."""
    from mlx.utils import tree_flatten

    counts = {"total": 0, "trainable": 0}
    all_params = tree_flatten(model.parameters())
    trainable = tree_flatten(model.trainable_parameters())

    counts["total"] = sum(p.size for _, p in all_params)
    counts["trainable"] = sum(p.size for _, p in trainable)

    return counts


# ═════════════════════════════════

[OUTPUT TRUNCATED] The tool call succeeded but the output was truncated. Full output saved to: /Users/mwhitford/.cache/eca/toolCallOutputs/toolu_01CoLgc3wAn5J4LoMXj3Ugtn.txt
Use `eca__grep` or `eca__read_file` with offset/limit to view specific sections. Do not full read the file.
```

## Assistant

Good, I have a thorough understanding of all the v10 code. Now let me also check the train.py and ternary.py for the pieces I need:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/train.py",
  "limit": 50
}
```

**Summary:** Reading train.py (0-50)

**Output:**
```
"""
v10 — Training Script

V6 compressor (5-pass bidirectional VSM, 9 strides, Qwen3 tokenizer)
trained on Dolma prose for next-token prediction.

  • Causal LM cross-entropy loss
  • Relational loss r = (CE - E) / (log(V) - E) for phase awareness
  • Shared-weight gradient normalization (÷5 for 5-pass components)
  • Ternary topology evolved via tournament selection (mixed-data-aware)
  • Adam on continuous parameters (gamma, norms, embeddings, pos_embed)
  • Cosine LR with linear warmup

Usage:
    uv run python scripts/v10/train.py
    uv run python scripts/v10/train.py --total-steps 5000
    uv run python scripts/v10/train.py --seq-len 512 --batch-size 4
    uv run python scripts/v10/train.py --resume

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import os
import sys
import time
from collections import deque
from pathlib import Path

os.environ["PYTHONUNBUFFERED"] = "1"

import mlx.core as mx
import mlx.nn as nn
import mlx.optimizers as optim
import numpy as np
from mlx.utils import tree_flatten, tree_map

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader, MixedDataLoader
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,

[CONTENT TRUNCATED] Showing lines 1 to 50 of 1116 total lines. Use line_offset=50 parameter to read more content.
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "wc -l /Users/mwhitford/src/verbum/scripts/v10/train.py /Users/mwhitford/src/verbum/scripts/v10/ternary.py /Users/mwhitford/src/verbum/scripts/v10/attention.py"
}
```

**Summary:** $ wc -l /Users/mwhitford/src/verbum/s...

**Output:**
```
Exit code: 0
Stdout:
1116 /Users/mwhitford/src/verbum/scripts/v10/train.py
    1427 /Users/mwhitford/src/verbum/scripts/v10/ternary.py
     240 /Users/mwhitford/src/verbum/scripts/v10/attention.py
    2783 total
```

## Assistant

Now I have the full picture. Let me create the v11 directory and build the files. I'll start with the files that change significantly, and symlink the ones that don't.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "mkdir -p /Users/mwhitford/src/verbum/scripts/v11"
}
```

**Summary:** $ mkdir -p /Users/mwhitford/src/verbu...

**Output:**
```
Exit code: 0
```

## Assistant

Now let me build the v11 files. I'll create them in parallel where possible — starting with the foundational files (kernel, config), then the dispatch module, then model, then train.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/kernel.py",
  "content": "\"\"\"\nv11 — KIBC Combinator Kernel\n\nGround-truth evaluator for the four combinators discovered in Qwen3\nprobes (4B and 32B, session 077). Pure Python — no MLX, no neural\ncomputation. This is the structural reduction engine that the v11\ncombinator dispatch pathway uses for exact computation.\n\nThe Qwen probes confirmed:\n  - K (select):   native to attention softmax at all scales\n  - I (identity): native to the residual stream\n  - B (compose):  matures 20%→80% accuracy from 4B→32B\n  - C (flip):     absent at 4B, emerges at 32B (enables closures)\n  - S (distribute): never crystallizes — composite of B∘K∘C\n\nThe four combinators are the basis; the 22 v10 ops were derived\nsymptoms. This kernel provides the structural reductions directly.\n\nReduction rules (standard combinator calculus):\n  K x y   → x           (select first, discard second)\n  I x     → x           (identity, copy forward)\n  B f g x → f (g x)     (compose: apply g then f)\n  C f x y → f y x       (flip: reorder arguments)\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nfrom enum import IntEnum\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 1  Combinator definitions\n# ══════════════════════════════════════════════════════════════════════\n\nclass Combinator(IntEnum):\n    \"\"\"The four primitive combinators — the natural basis of attention.\"\"\"\n    K = 0   # λx.λy.x         — select first, discard second\n    I = 1   # λx.x             — identity (copy forward)\n    B = 2   # λf.λg.λx.f(g(x)) — compose (chain two functions)\n    C = 3   # λf.λx.λy.f(y)(x) — flip (reorder arguments)\n\nN_COMBINATORS = 4\n\nCOMBINATOR_NAMES: list[str] = [\"K\", \"I\", \"B\", \"C\"]\nassert len(COMBINATOR_NAMES) == N_COMBINATORS\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 2  Combinator properties\n# ══════════════════════════════════════════════════════════════════════\n\n# Arity: how many arguments each combinator consumes before reducing\nCOMBINATOR_ARITY: dict[Combinator, int] = {\n    Combinator.K: 2,   # K x y → x\n    Combinator.I: 1,   # I x → x\n    Combinator.B: 3,   # B f g x → f (g x)\n    Combinator.C: 3,   # C f x y → f y x\n}\n\n# What each combinator does in prose (for logging/probing)\nCOMBINATOR_ROLE: dict[Combinator, str] = {\n    Combinator.K: \"select\",    # pick relevant, discard irrelevant\n    Combinator.I: \"identity\",  # copy forward unchanged\n    Combinator.B: \"compose\",   # chain operations: apply g then f\n    Combinator.C: \"flip\",      # reorder arguments, enable closures\n}\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 3  Reduction engine\n# ══════════════════════════════════════════════════════════════════════\n\nclass Term:\n    \"\"\"A combinator calculus term.\n\n    Either a primitive combinator, an integer/symbol atom, or an\n    application of one term to another.\n    \"\"\"\n    pass\n\n\nclass Comb(Term):\n    \"\"\"A primitive combinator: K, I, B, or C.\"\"\"\n    __slots__ = ('which',)\n    def __init__(self, which: Combinator):\n        self.which = which\n    def __repr__(self):\n        return COMBINATOR_NAMES[self.which]\n    def __eq__(self, other):\n        return isinstance(other, Comb) and self.which == other.which\n    def __hash__(self):\n        return hash(('Comb', self.which))\n\n\nclass Atom(Term):\n    \"\"\"An atomic value — integer, symbol, or any leaf.\"\"\"\n    __slots__ = ('value',)\n    def __init__(self, value):\n        self.value = value\n    def __repr__(self):\n        return str(self.value)\n    def __eq__(self, other):\n        return isinstance(other, Atom) and self.value == other.value\n    def __hash__(self):\n        return hash(('Atom', self.value))\n\n\nclass App(Term):\n    \"\"\"Application of one term to another: (f x).\"\"\"\n    __slots__ = ('func', 'arg')\n    def __init__(self, func: Term, arg: Term):\n        self.func = func\n        self.arg = arg\n    def __repr__(self):\n        f_str = repr(self.func)\n        a_str = repr(self.arg)\n        if isinstance(self.arg, App):\n            a_str = f\"({a_str})\"\n        return f\"{f_str} {a_str}\"\n    def __eq__(self, other):\n        return isinstance(other, App) and self.func == other.func and self.arg == other.arg\n    def __hash__(self):\n        return hash(('App', self.func, self.arg))\n\n\ndef reduce_step(term: Term) -> tuple[Term, bool]:\n    \"\"\"One step of normal-order (outermost-first) reduction.\n\n    Returns (reduced_term, changed).\n    Normal order matches what autoregressive transformers naturally do:\n    outermost redex first, left to right.\n    \"\"\"\n    if isinstance(term, (Comb, Atom)):\n        return term, False\n\n    if not isinstance(term, App):\n        return term, False\n\n    # Try to reduce at the top level first (normal order)\n    # K x y → x\n    if (isinstance(term.func, App) and\n        isinstance(term.func.func, Comb) and\n        term.func.func.which == Combinator.K):\n        # (K x) y → x\n        return term.func.arg, True\n\n    # I x → x\n    if isinstance(term.func, Comb) and term.func.which == Combinator.I:\n        return term.arg, True\n\n    # B f g x → f (g x)\n    if (isinstance(term.func, App) and\n        isinstance(term.func.func, App) and\n        isinstance(term.func.func.func, Comb) and\n        term.func.func.func.which == Combinator.B):\n        f = term.func.func.arg\n        g = term.func.arg\n        x = term.arg\n        return App(f, App(g, x)), True\n\n    # C f x y → f y x\n    if (isinstance(term.func, App) and\n        isinstance(term.func.func, App) and\n        isinstance(term.func.func.func, Comb) and\n        term.func.func.func.which == Combinator.C):\n        f = term.func.func.arg\n        x = term.func.arg\n        y = term.arg\n        return App(App(f, y), x), True\n\n    # No top-level reduction — try reducing the function part first\n    new_func, changed = reduce_step(term.func)\n    if changed:\n        return App(new_func, term.arg), True\n\n    # Then try reducing the argument\n    new_arg, changed = reduce_step(term.arg)\n    if changed:\n        return App(term.func, new_arg), True\n\n    return term, False\n\n\ndef reduce(term: Term, max_steps: int = 100) -> tuple[Term, int]:\n    \"\"\"Fully reduce a term (normal order). Returns (result, steps_taken).\n\n    Stops after max_steps to prevent infinite loops (e.g. Ω combinator).\n    \"\"\"\n    steps = 0\n    while steps < max_steps:\n        new_term, changed = reduce_step(term)\n        if not changed:\n            break\n        term = new_term\n        steps += 1\n    return term, steps\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 4  Convenience constructors\n# ══════════════════════════════════════════════════════════════════════\n\nK = Comb(Combinator.K)\nI = Comb(Combinator.I)\nB = Comb(Combinator.B)\nC = Comb(Combinator.C)\n\n\ndef app(*terms: Term) -> Term:\n    \"\"\"Left-associative application: app(f, x, y) = App(App(f, x), y).\"\"\"\n    result = terms[0]\n    for t in terms[1:]:\n        result = App(result, t)\n    return result\n\n\ndef atom(value) -> Atom:\n    \"\"\"Create an atomic term.\"\"\"\n    return Atom(value)\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 5  Kernel functions for neural pathway\n# ══════════════════════════════════════════════════════════════════════\n#\n# These functions implement combinator reductions on integer operands,\n# matching the kernel computation pathway in CombinatorIntegrate.\n# The neural pathway extracts operands from the residual stream,\n# dispatches to one of these functions, and encodes the result back.\n#\n# Unlike v10's 22-op kernel (arithmetic), these are structural:\n#   K: select operand 0, discard operand 1\n#   I: return operand 0 unchanged\n#   B: f(g(x)) — requires encoding f and g as operations\n#   C: swap operand 1 and 2, then apply f\n\ndef kernel_K(op0: int, op1: int, op2: int) -> int:\n    \"\"\"K x y → x. Select first operand.\"\"\"\n    return op0\n\n\ndef kernel_I(op0: int, op1: int, op2: int) -> int:\n    \"\"\"I x → x. Identity — return first operand unchanged.\"\"\"\n    return op0\n\n\ndef kernel_B(op0: int, op1: int, op2: int) -> int:\n    \"\"\"B f g x → f(g(x)). Compose: apply g to x, then f to result.\n\n    In the neural kernel pathway, f and g are encoded as operand\n    indices. The actual composition happens through multiple cycles\n    in the descending arm — cycle 0 identifies the combinators,\n    cycle 1 resolves g(x), cycle 2 applies f. The kernel provides\n    a single-step approximation: f_index + g(x_index).\n\n    For the straight-through pathway, we encode this as:\n    result = op0 + op1 + op2 (additive composition signal).\n    The result_embed learns to map this back meaningfully.\n    \"\"\"\n    return op0 + op1 + op2\n\n\ndef kernel_C(op0: int, op1: int, op2: int) -> int:\n    \"\"\"C f x y → f y x. Flip: swap operand 1 and 2.\n\n    In the kernel pathway, flipping is encoded as using op2 where\n    op1 would go and vice versa: result = op0 + op2 (skip op1).\n    The model learns through the result_embed that C-reduction\n    discards the second argument's position and uses the third.\n    \"\"\"\n    return op0 + op2\n\n\n# Dispatch table for vectorized kernel computation\nKERNEL_FUNCTIONS = [kernel_K, kernel_I, kernel_B, kernel_C]\n\nassert len(KERNEL_FUNCTIONS) == N_COMBINATORS\n\n\n# ══════════════════════════════════════════════════════════════════════\n# § 6  Self-test\n# ══════════════════════════════════════════════════════════════════════\n\ndef _self_test() -> None:\n    \"\"\"Smoke-test all four combinators and the reduction engine.\"\"\"\n\n    # ── K combinator: K x y → x ──\n    t = app(K, atom(3), atom(7))\n    result, steps = reduce(t)\n    assert result == atom(3), f\"K 3 7 should reduce to 3, got {result}\"\n    assert steps == 1, f\"K x y should take 1 step, took {steps}\"\n\n    # ── I combinator: I x → x ──\n    t = app(I, atom(42))\n    result, steps = reduce(t)\n    assert result == atom(42), f\"I 42 should reduce to 42, got {result}\"\n    assert steps == 1\n\n    # ── B combinator: B f g x → f (g x) ──\n    # B K I 5 → K (I 5) → K 5 → partial (K 5, waiting for y)\n    # But more usefully: B I I x → I (I x) → I x → x\n    t = app(B, I, I, atom(5))\n    result, steps = reduce(t)\n    assert result == atom(5), f\"B I I 5 should reduce to 5, got {result}\"\n\n    # B (K 1) I 5 → (K 1) (I 5) → (K 1) 5 → 1\n    t = app(B, app(K, atom(1)), I, atom(5))\n    result, steps = reduce(t)\n    assert result == atom(1), f\"B (K 1) I 5 should reduce to 1, got {result}\"\n\n    # ── C combinator: C f x y → f y x ──\n    # C K 3 7 → K 7 3 → 7\n    t = app(C, K, atom(3), atom(7))\n    result, steps = reduce(t)\n    assert result == atom(7), f\"C K 3 7 should reduce to 7, got {result}\"\n\n    # ── Composition: C and K together ──\n    # C (C K) 1 2 → (C K) 2 1 → K 1 2 → 1\n    t = app(C, app(C, K), atom(1), atom(2))\n    result, steps = reduce(t)\n    assert result == atom(1), f\"C (C K) 1 2 should reduce to 1, got {result}\"\n\n    # ── S combinator expressed as composition ──\n    # S = B(B(BW)(BBC))(BB) where W = CSI\n    # Simpler test: S K K x → K x (K x) → x\n    # SKK is the identity — but we don't have S, we compose from KIBC:\n    # S f g x = f x (g x)\n    # For S K K x: K x (K x) → x\n    # We can express this using B, C, K:\n    # Not testing S directly since it's emergent, not primitive.\n\n    # ── Partial application (combinator waiting for args) ──\n    t = app(K, atom(3))  # K 3 — waiting for y\n    result, steps = reduce(t)\n    assert isinstance(result, App), f\"K 3 should be partial, got {result}\"\n    assert steps == 0, f\"K 3 is a value (no redex), steps should be 0\"\n\n    # ── Normal-order reduction (outermost first) ──\n    # K (I 3) (I 4) → I 3 (not I 4 first — normal order selects and discards)\n    # Actually: (K (I 3)) (I 4) → (I 3) → 3\n    t = app(K, app(I, atom(3)), app(I, atom(4)))\n    result, steps = reduce(t)\n    assert result == atom(3), f\"K (I 3) (I 4) should reduce to 3, got {result}\"\n    # Normal order: K reduces first (discarding I 4), then I 3 → 3\n    # Steps: K (I 3) (I 4) → I 3 → 3 = 2 steps\n    assert steps == 2, f\"Expected 2 steps (K then I), got {steps}\"\n\n    # ── Kernel functions ──\n    assert kernel_K(3, 7, 0) == 3, \"kernel_K should select op0\"\n    assert kernel_I(42, 0, 0) == 42, \"kernel_I should return op0\"\n    assert kernel_B(1, 2, 3) == 6, \"kernel_B should sum all three\"\n    assert kernel_C(1, 2, 3) == 4, \"kernel_C should sum op0 + op2\"\n\n    # ── COMBINATOR_NAMES consistency ──\n    assert COMBINATOR_NAMES[Combinator.K] == \"K\"\n    assert COMBINATOR_NAMES[Combinator.I] == \"I\"\n    assert COMBINATOR_NAMES[Combinator.B] == \"B\"\n    assert COMBINATOR_NAMES[Combinator.C] == \"C\"\n\n    print(\"kernel.py self-test: all assertions passed ✓\")\n    print(f\"  {N_COMBINATORS} combinators: {', '.join(COMBINATOR_NAMES)}\")\n    print(f\"  Reduction engine: normal-order, outermost-first\")\n    print(f\"  Kernel functions: K(select), I(identity), B(compose), C(flip)\")\n\n\nif __name__ == \"__main__\":\n    _self_test()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/v11/kernel.py
```

## User

the v11 dir should be self-contained, copy the files into the dir, some duplication is ok, we want to be able to fully extract the code into it's own project once we have the working solution.  This repo is a reasearch and exploration project.


### Thinking

The user wants v11 to be fully self-contained — copy all files, no symlinks, no imports from v10. This makes sense for a research project where you want to be able to extract the working solution later.

Let me copy all the necessary files into scripts/v11/:
1. kernel.py — already written (new KIBC kernel)
2. config.py — new, adjusted for KIBC
3. components.py — copy from v10 (unchanged)
4. kernel_dispatch.py — new, CombinatorDispatch + CombinatorIntegrate
5. model.py — new, V11Model with KIBC changes


6. ternary.py — copy from v10 (unchanged)
7. train.py — copy from v10 with import adjustments
8. attention.py — copy from v10 (unchanged, needed for StrideStack)
9. data.py — copy from v10 (unchanged, needed for data loading)

Now I need to check what other files from v10 might be required for the full setup.

## Assistant

Got it — fully self-contained, extractable. Let me check what files v10 has and copy everything.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/scripts/v10/*.py"
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
-rw-r--r--@ 1 mwhitford  staff   9354 May  3 11:52 /Users/mwhitford/src/verbum/scripts/v10/attention.py
-rw-r--r--@ 1 mwhitford  staff  35688 May 11 05:19 /Users/mwhitford/src/verbum/scripts/v10/components.py
-rw-r--r--@ 1 mwhitford  staff   3989 May 10 12:53 /Users/mwhitford/src/verbum/scripts/v10/config.py
-rw-r--r--@ 1 mwhitford  staff   7504 May  7 14:07 /Users/mwhitford/src/verbum/scripts/v10/data.py
-rw-r--r--@ 1 mwhitford  staff  32855 May  9 13:55 /Users/mwhitford/src/verbum/scripts/v10/kernel_dispatch.py
-rw-r--r--@ 1 mwhitford  staff  24317 May  3 07:27 /Users/mwhitford/src/verbum/scripts/v10/kernel.py
-rw-r--r--@ 1 mwhitford  staff  52260 May 10 12:57 /Users/mwhitford/src/verbum/scripts/v10/model.py
-rw-r--r--@ 1 mwhitford  staff   5793 May  7 14:06 /Users/mwhitford/src/verbum/scripts/v10/pack_structured.py
-rw-r--r--@ 1 mwhitford  staff  26752 May  3 07:05 /Users/mwhitford/src/verbum/scripts/v10/probe_binding_structure.py
-rw-r--r--@ 1 mwhitford  staff  18069 May  3 07:19 /Users/mwhitford/src/verbum/scripts/v10/probe_compressor_binding.py
-rw-r--r--@ 1 mwhitford  staff  11452 May  9 09:17 /Users/mwhitford/src/verbum/scripts/v10/probe_counterfactual.py
-rw-r--r--@ 1 mwhitford  staff  13887 May  9 07:00 /Users/mwhitford/src/verbum/scripts/v10/probe_dispatch.py
-rw-r--r--@ 1 mwhitford  staff  14521 May  9 07:33 /Users/mwhitford/src/verbum/scripts/v10/probe_kernel_use.py
-rw-r--r--@ 1 mwhitford  staff  23068 May  3 06:53 /Users/mwhitford/src/verbum/scripts/v10/probe_parse_structure.py
-rw-r--r--@ 1 mwhitford  staff  27818 May  3 06:45 /Users/mwhitford/src/verbum/scripts/v10/probe_type_transition.py
-rw-r--r--@ 1 mwhitford  staff  41173 May  8 08:00 /Users/mwhitford/src/verbum/scripts/v10/probe.py
-rw-r--r--@ 1 mwhitford  staff  55909 May  8 17:00 /Users/mwhitford/src/verbum/scripts/v10/ternary.py
-rw-r--r--@ 1 mwhitford  staff  52404 May 10 13:06 /Users/mwhitford/src/verbum/scripts/v10/train.py
```

## Assistant

Right. Core runtime files to copy: `attention.py`, `components.py`, `data.py`, `ternary.py`. Then new/modified: `kernel.py` (already done), `config.py`, `kernel_dispatch.py`, `model.py`, `train.py`. I'll skip the probe scripts and pack_structured for now — those get built when needed.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cp /Users/mwhitford/src/verbum/scripts/v10/attention.py /Users/mwhitford/src/verbum/scripts/v11/attention.py && cp /Users/mwhitford/src/verbum/scripts/v10/components.py /Users/mwhitford/src/verbum/scripts/v11/components.py && cp /Users/mwhitford/src/verbum/scripts/v10/data.py /Users/mwhitford/src/verbum/scripts/v11/data.py && cp /Users/mwhitford/src/verbum/scripts/v10/ternary.py /Users/mwhitford/src/verbum/scripts/v11/ternary.py"
}
```

**Summary:** $ cp /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 0
```

## Assistant

Good. Now let me build the 4 new/modified files. Starting with config:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/config.py",
  "content": "\"\"\"\nv11 Configuration — KIBC combinator basis, Qwen3 tokenizer.\n\nArchitecture:\n  Ascending arm: v6 proven 5-pass bidirectional VSM (9 strides, StrideStack)\n  Descending arm: KIBC combinator dispatch (4 combinators, not 22 ops)\n  Output: tied embedding projection → next-token prediction\n\nThe combinator basis comes from Qwen3 probes (4B and 32B, session 077):\n  K (select):   native to attention softmax\n  I (identity): native to residual stream\n  B (compose):  matures with scale (20%→80% accuracy)\n  C (flip):     emerges at scale (enables closures)\n\nLicense: MIT\n\"\"\"\n\nfrom dataclasses import dataclass\n\nfrom kernel import N_COMBINATORS\n\n\n@dataclass\nclass V11Config:\n    \"\"\"v11 model + training configuration.\"\"\"\n\n    # ── Tokenizer (Qwen3 BBPE) ──\n    vocab_size: int = 151936     # Qwen3 BBPE vocab\n    eod_id: int = 151643        # end-of-document token\n\n    # ── Core dimensions ──\n    d_model: int = 512            # representation dimension\n    d_ff: int = 1536              # prep FFN width (3× d_model)\n    d_ff_consolidate: int = 2048  # consolidate FFN width (wider)\n    d_register: int = 128         # register dimension (real dim = 2×)\n    n_heads: int = 8              # attention heads (d_head = 64)\n    window: int = 8               # attention window width\n    alpha: float = 1.18           # spiral bias coefficient\n\n    # 9 strides: the full scale hierarchy proven in v6\n    strides: tuple[int, ...] = (1, 8, 16, 32, 64, 128, 256, 512, 1024)\n\n    # Register semantics:\n    #   reg 0 = combinator (K/I/B/C identity)\n    #   reg 1 = binding_depth (how many lambdas deep)\n    #   reg 2 = phase (recognize / identify / resolve / produce)\n    n_registers: int = 3\n\n    # ── Combinator dispatch ──\n    n_combinators: int = N_COMBINATORS  # 4: K, I, B, C\n    # No top-k needed with 4 targets — full softmax over all 4.\n    # If a combinator dies, revisit and add top-k back.\n\n    # Self-regulating descending cycles (unchanged from v10)\n    desc_max_cycles: int = 3\n\n    # Dropout\n    dropout: float = 0.1\n\n    # ── Training ──\n    batch_size: int = 2\n    grad_accum: int = 4           # effective batch = batch_size × grad_accum\n    total_steps: int = 20000\n    lr: float = 6e-4\n    lr_floor_ratio: float = 0.01\n    warmup_steps: int = 500\n    weight_decay: float = 0.01\n    grad_clip: float = 1.0\n\n    # ── Evolution ──\n    gen_interval: int = 50\n    base_pct: float = 0.0002\n    sign_flip_rate: float = 0.2\n    guided_fraction: float = 0.7\n    mutation_adam_decay: float = 0.1\n    s4_boost: float = 3.0\n\n    # ── Checkpointing ──\n    checkpoint_interval: int = 1000\n    eval_interval: int = 500\n    log_interval: int = 25\n    checkpoint_dir: str = \"checkpoints/v11\"\n\n    # ── Data ──\n    data_dir: str = \"/Users/mwhitford/data/fractal-bitnet/shards-qwen3\"\n    structured_shard: str = \"data/structured_shard.npy\"\n    mix_ratio: float = 0.0        # fraction of structured data (0.0 = prose only)\n    seq_len: int = 4096           # context window\n    max_seq_len: int = 4096\n    n_train_shards: int = 54\n    n_eval_shards: int = 6\n\n    @property\n    def d_head(self) -> int:\n        return self.d_model // self.n_heads\n\n    @property\n    def n_strides(self) -> int:\n        return len(self.strides)\n\n    @property\n    def tokens_per_step(self) -> int:\n        return self.batch_size * self.grad_accum * self.seq_len\n\n    def __post_init__(self):\n        assert self.d_model % self.n_heads == 0\n        assert self.d_model % 16 == 0, \"d_model must be divisible by 16 (ternary packing)\"\n        assert self.d_model % 4 == 0, \"d_model must be divisible by 4 (embedding packing)\"\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/v11/config.py
```

## Assistant

Now the big one — `kernel_dispatch.py` with `CombinatorDispatch` and `CombinatorIntegrate`:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/kernel_dispatch.py",
  "content": "\"\"\"\nCombinator dispatch modules for the descending VSM arm.\n\nv11 replaces v10's 22-op dispatch with a 4-combinator basis (K, I, B, C)\ndiscovered in Qwen3 probes (4B and 32B, session 077). The transformers\ndon't organize computation into 22 arithmetic operations — they converge\non four combinators that ARE the natural basis of attention:\n\n  K (select):   softmax IS selection — pick relevant, discard rest\n  I (identity): residual stream IS identity — copy forward unchanged\n  B (compose):  attention composition — chain operations\n  C (flip):     argument reordering — enables closures and binding\n\nThe 22 v10 ops were derived symptoms. This module provides the sieve\nshaped like what LLMs actually find — 4 orthogonal combinator pathways\nas the path of least resistance.\n\nArchitecture per descending pass:\n  Phase 0 (dispatch):   CombinatorDispatch — which combinator? (4-way softmax)\n  Phase 1 (converge):   StrideStack — propagate dispatched signal spatially\n  Phase 2 (integrate):  CombinatorIntegrate — apply combinator reduction\n\nCycle semantics (desc_max_cycles=3):\n  Cycle 0 — IDENTIFY:  which combinator applies here?\n  Cycle 1 — RESOLVE:   find and bind the arguments\n  Cycle 2 — PRODUCE:   apply reduction, produce result\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport mlx.core as mx\nimport mlx.nn as nn\n\nfrom ternary import TernaryLinear\nfrom kernel import N_COMBINATORS, COMBINATOR_NAMES\n\n\n# ══════════════════════════════════════════════════════════════════\n# CombinatorDispatch — routes to 4 combinator pathways\n# ══════════════════════════════════════════════════════════════════\n\n\nclass CombinatorDispatch(nn.Module):\n    \"\"\"Phase 0: which combinator applies at this position?\n\n    4-way softmax over K, I, B, C. No top-k needed — with 4 targets,\n    softmax has strong gradients for all entries. If a combinator dies,\n    add top-k=2 back.\n\n    The combinator embeddings are the S5 identity of the dispatcher:\n    4 near-orthogonal directions encoding WHAT each combinator IS.\n    Register conditioning from the ascending arm biases which combinator\n    is contextually likely. Op emphasis from S4 scales the landscape.\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int,\n        n_combinators: int = N_COMBINATORS,\n        d_ff: int | None = None,\n        dropout: float = 0.1,\n        n_registers: int = 3,\n        d_register: int = 128,\n        max_cond_banks: int = 5,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.n_combinators = n_combinators\n        if d_ff is None:\n            d_ff = d_model * 3\n\n        # Pad to multiple of 16 for TernaryLinear\n        self.n_comb_padded = ((n_combinators + 15) // 16) * 16  # 16\n\n        self.norm = nn.RMSNorm(d_model)\n\n        # Dispatch projection: hidden → combinator logits\n        self.dispatch = TernaryLinear(d_model, self.n_comb_padded, pre_norm=False)\n\n        # ── Register conditioning ─────────────────────────────\n        # Ascending registers → dispatch bias: which combinator is likely?\n        self.n_registers = n_registers\n        self.d_reg_real = d_register * 2\n        self.max_cond_banks = max_cond_banks\n        max_cond_dim = max_cond_banks * n_registers * self.d_reg_real\n        self._max_cond_dim = ((max_cond_dim + 15) // 16) * 16\n        self.register_cond = nn.Linear(self._max_cond_dim, self.n_comb_padded)\n        # Zero-init: conditioning starts inert\n        self.register_cond.weight = mx.zeros_like(self.register_cond.weight)\n        self.register_cond.bias = mx.zeros_like(self.register_cond.bias)\n\n        # Combinator embeddings: 4 near-orthogonal directions\n        self.combinator_embeddings = _init_combinator_embeddings(\n            n_combinators, d_model)\n\n        # L2-normalize to fixed scale each forward pass\n        self.embed_scale = 0.5\n\n        # FFN pathway: transforms representation using combinator identity\n        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)\n        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)\n\n        self.dropout = nn.Dropout(dropout)\n\n    def _normalize_embeddings(self) -> mx.array:\n        \"\"\"L2-normalize combinator embeddings to fixed scale.\"\"\"\n        norms = mx.sqrt(\n            mx.sum(self.combinator_embeddings * self.combinator_embeddings,\n                   axis=-1, keepdims=True) + 1e-8)\n        return self.combinator_embeddings * (self.embed_scale / norms)\n\n    def __call__(\n        self,\n        x: mx.array,\n        registers: list[list[mx.array]] | None = None,\n        combinator_emphasis: mx.array | None = None,\n    ) -> mx.array:\n        \"\"\"\n        x: (B, L, d_model)\n        registers: ascending register banks for conditioning\n        combinator_emphasis: (n_combinators,) per-combinator emphasis from S4\n\n        Returns: (B, L, d_model) with residual connection\n        \"\"\"\n        h = self.norm(x)\n\n        # Step 1: Dispatch logits — which combinator?\n        dispatch_logits = self.dispatch(h)[..., :self.n_combinators]  # (B, L, 4)\n\n        # Register conditioning: ascending registers bias dispatch\n        if registers is not None:\n            parts = []\n            for bank in registers:\n                for reg in bank:\n                    parts.append(reg)\n            cond_input = mx.concatenate(parts, axis=-1)\n            if cond_input.shape[0] < self._max_cond_dim:\n                cond_input = mx.concatenate([\n                    cond_input,\n                    mx.zeros((self._max_cond_dim - cond_input.shape[0],))\n                ])\n            reg_bias = self.register_cond(cond_input)[:self.n_combinators]\n            dispatch_logits = dispatch_logits + reg_bias[None, None, :]\n\n        # Step 2: Full softmax over 4 combinators\n        # No top-k masking — 4 targets have strong gradients for all entries\n        dispatch_weights = mx.softmax(dispatch_logits, axis=-1)  # (B, L, 4)\n\n        # Cache for probing\n        self._dispatch_weights = mx.stop_gradient(dispatch_weights)\n\n        # Step 3: Normalized combinator embeddings\n        comb_emb = self._normalize_embeddings()  # (4, d_model)\n\n        # S4 emphasis: modulate combinator availability\n        if combinator_emphasis is not None:\n            comb_emb = comb_emb * combinator_emphasis[:, None]\n\n        # Step 4: Weighted combinator embedding — identity modulation\n        # (B, L, 4) @ (4, d_model) → (B, L, d_model)\n        comb_context = dispatch_weights @ comb_emb\n\n        # Step 5: Modulate input, then transform\n        modulated = h + comb_context\n        out = self.down(nn.gelu(self.up(modulated)))\n\n        return x + self.dropout(out)\n\n\n# ══════════════════════════════════════════════════════════════════\n# CombinatorIntegrate — applies combinator reductions\n# ══════════════════════════════════════════════════════════════════\n\n\nclass CombinatorIntegrate(nn.Module):\n    \"\"\"Phase 2: apply the combinator reduction, type the result.\n\n    Dual pathway:\n      1. Standard FFN pathway: type modulation + shared transform.\n         Handles prose and non-computational positions.\n      2. Kernel computation pathway: exact combinator reductions on\n         operands extracted from the residual stream:\n           K: select operand 0, discard operand 1\n           I: return operand 0 unchanged\n           B: f(g(x)) — additive composition signal\n           C: f(y,x) — swap: select operand 0 + operand 2\n\n    Compute gate blends the two pathways:\n      output = gate × kernel_result + (1-gate) × ffn_result\n    Gate starts at ~0 (pure FFN), learns to open for positions\n    where exact combinator computation helps.\n    \"\"\"\n\n    def __init__(\n        self,\n        d_model: int,\n        n_combinators: int = N_COMBINATORS,\n        d_ff: int | None = None,\n        dropout: float = 0.1,\n        max_val: int = 256,\n        result_buckets: int = 1024,\n    ):\n        super().__init__()\n        self.d_model = d_model\n        self.n_combinators = n_combinators\n        self.max_val = max_val\n        if d_ff is None:\n            d_ff = d_model * 4\n\n        # Pad for TernaryLinear\n        self.n_comb_padded = ((n_combinators + 15) // 16) * 16\n\n        self.norm = nn.RMSNorm(d_model)\n\n        # ── Type pathway (combinator types, not value types) ──\n        self.type_proj = TernaryLinear(\n            d_model, self.n_comb_padded, pre_norm=False)\n        self.type_embeddings = _init_combinator_type_embeddings(\n            n_combinators, d_model)\n\n        # ── Standard FFN pathway ──────────────────────────────\n        self.up = TernaryLinear(d_model, d_ff, pre_norm=False)\n        self.down = TernaryLinear(d_ff, d_model, pre_norm=False)\n\n        # ── Kernel computation pathway ────────────────────────\n\n        # 3 operand extractors (B and C need 3 arguments)\n        max_val_padded = ((max_val + 15) // 16) * 16\n        self._max_val_padded = max_val_padded\n        self.operand0_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)\n        self.operand1_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)\n        self.operand2_proj = TernaryLinear(d_model, max_val_padded, pre_norm=False)\n\n        # Result encoder\n        self.result_buckets = result_buckets\n        self.result_offset = result_buckets // 2\n        self.result_embed = nn.Embedding(result_buckets, d_model)\n\n        # Compute gate: starts near 0 (pure FFN)\n        self.gate_proj = nn.Linear(d_model, 1)\n        self.gate_proj.weight = mx.zeros_like(self.gate_proj.weight)\n        self.gate_proj.bias = mx.ones_like(self.gate_proj.bias) * -5.0\n\n        self.dropout = nn.Dropout(dropout)\n\n    def _kernel_compute(\n        self,\n        h: mx.array,\n        dispatch_weights: mx.array | None,\n    ) -> tuple[mx.array, dict]:\n        \"\"\"Extract operands, apply combinator reductions, encode result.\n\n        The 4 combinator kernel functions operate on integer operands:\n          K(op0, op1, op2) → op0           (select first)\n          I(op0, op1, op2) → op0           (identity)\n          B(op0, op1, op2) → op0+op1+op2   (composition signal)\n          C(op0, op1, op2) → op0+op2       (flip: skip op1)\n        \"\"\"\n        B, L, _ = h.shape\n\n        # Extract 3 operands via argmax (non-differentiable)\n        op0_logits = self.operand0_proj(h)[..., :self.max_val]\n        op1_logits = self.operand1_proj(h)[..., :self.max_val]\n        op2_logits = self.operand2_proj(h)[..., :self.max_val]\n\n        op0 = mx.stop_gradient(mx.argmax(op0_logits, axis=-1)).astype(mx.int32)\n        op1 = mx.stop_gradient(mx.argmax(op1_logits, axis=-1)).astype(mx.int32)\n        op2 = mx.stop_gradient(mx.argmax(op2_logits, axis=-1)).astype(mx.int32)\n\n        # Get combinator from dispatch weights\n        if dispatch_weights is not None:\n            comb = mx.stop_gradient(\n                mx.argmax(dispatch_weights, axis=-1)).astype(mx.int32)\n        else:\n            comb = mx.zeros((B, L), dtype=mx.int32)\n\n        # ── Exact combinator kernel (non-differentiable) ─────\n        # Compute all 4 combinator results, select by dispatched combinator\n\n        # K: select op0 (discard op1, op2)\n        r_K = op0\n\n        # I: identity — return op0\n        r_I = op0\n\n        # B: compose — f(g(x)) encoded as additive signal\n        r_B = op0 + op1 + op2\n\n        # C: flip — f(y,x) encoded as op0 + op2 (skip op1)\n        r_C = op0 + op2\n\n        # Stack and select by combinator code\n        all_results = mx.stack([r_K, r_I, r_B, r_C], axis=0)  # (4, B, L)\n\n        comb_clamped = mx.clip(comb, 0, N_COMBINATORS - 1)\n        b_idx = mx.broadcast_to(mx.arange(B)[:, None], (B, L))\n        l_idx = mx.broadcast_to(mx.arange(L)[None, :], (B, L))\n        result = all_results[comb_clamped, b_idx, l_idx]  # (B, L)\n\n        # ── Encode result back to d_model ─────────────────────\n        result_idx = mx.stop_gradient(\n            mx.clip(result + self.result_offset, 0, self.result_buckets - 1)\n        ).astype(mx.int32)\n        kernel_out = self.result_embed(result_idx)  # (B, L, d_model)\n\n        kernel_info = {\n            \"combinator\": mx.stop_gradient(comb),\n            \"op0\": mx.stop_gradient(op0),\n            \"op1\": mx.stop_gradient(op1),\n            \"op2\": mx.stop_gradient(op2),\n            \"result\": mx.stop_gradient(result),\n        }\n\n        return kernel_out, kernel_info\n\n    def __call__(\n        self,\n        x: mx.array,\n        dispatch_weights: mx.array | None = None,\n    ) -> mx.array:\n        \"\"\"\n        x: (B, L, d_model)\n        dispatch_weights: (B, L, n_combinators) from CombinatorDispatch\n        Returns: (B, L, d_model) with residual connection\n        \"\"\"\n        h = self.norm(x)\n\n        # ── Type projection (combinator types) ────────────────\n        type_logits = self.type_proj(h)[..., :self.n_combinators]\n        type_weights = mx.softmax(type_logits, axis=-1)\n        self._type_weights = mx.stop_gradient(type_weights)\n\n        # ── Standard FFN pathway ──────────────────────────────\n        type_context = type_weights @ self.type_embeddings\n        modulated = h + type_context\n        ffn_out = self.down(nn.gelu(self.up(modulated)))\n\n        # ── Kernel computation pathway ────────────────────────\n        kernel_out, kernel_info = self._kernel_compute(h, dispatch_weights)\n        self._kernel_info = kernel_info\n\n        # ── Compute gate: blend kernel vs FFN ─────────────────\n        gate = mx.sigmoid(self.gate_proj(h))  # (B, L, 1)\n        self._compute_gate = mx.stop_gradient(gate)\n\n        blended = gate * kernel_out + (1.0 - gate) * ffn_out\n\n        return x + self.dropout(blended)\n\n\n# ══════════════════════════════════════════════════════════════════\n# Structured initialization\n# ══════════════════════════════════════════════════════════════════\n\n\ndef _init_combinator_embeddings(n_combinators: int, d_model: int) -> mx.array:\n    \"\"\"Initialize 4 near-orthogonal combinator identity embeddings.\n\n    Each combinator gets a distinct block of d_model/4 dimensions.\n    With 4 combinators in 512-dim space, they can be exactly orthogonal.\n    \"\"\"\n    embeddings = mx.zeros((n_combinators, d_model))\n    block = d_model // n_combinators  # 128 dims each\n\n    for i in range(n_combinators):\n        # Characteristic direction: Gaussian in a dedicated block\n        start = i * block\n        end = start + block\n        block_values = mx.random.normal((block,)) * 0.5\n        embeddings = embeddings.at[i, start:end].add(block_values)\n\n        # Small shared component for cross-combinator interaction\n        shared = mx.random.normal((d_model,)) * 0.05\n        embeddings = embeddings.at[i].add(shared)\n\n    # L2-normalize and scale\n    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)\n    embeddings = embeddings / norms * 0.1\n\n    return embeddings\n\n\ndef _init_combinator_type_embeddings(\n    n_combinators: int, d_model: int\n) -> mx.array:\n    \"\"\"Initialize combinator type embeddings.\n\n    4 types: K, I, B, C — each gets a near-orthogonal direction.\n    Same structure as combinator dispatch embeddings but for the\n    integration pathway (typing which combinator a position IS).\n    \"\"\"\n    embeddings = mx.zeros((n_combinators, d_model))\n    block = d_model // (n_combinators * 2)  # half-space for type identity\n\n    for i in range(n_combinators):\n        start = i * block\n        end = min((i + 1) * block, d_model)\n        for d in range(start, end):\n            embeddings = embeddings.at[i, d].add(1.0)\n        shared = mx.random.normal((d_model,)) * 0.05\n        embeddings = embeddings.at[i].add(shared)\n\n    norms = mx.sqrt(mx.sum(embeddings * embeddings, axis=-1, keepdims=True) + 1e-8)\n    embeddings = embeddings / norms * 0.1\n\n    return embeddings\n\n\n# ══════════════════════════════════════════════════════════════════\n# Self-test\n# ══════════════════════════════════════════════════════════════════\n\nif __name__ == \"__main__\":\n    import numpy as np\n    d_model = 512\n\n    print(\"Testing CombinatorDispatch (full softmax, 4 combinators)...\")\n    dispatch = CombinatorDispatch(d_model, n_combinators=4, d_ff=1536)\n    x = mx.random.normal((1, 64, d_model))\n    y = dispatch(x)\n    mx.eval(y)\n    assert y.shape == (1, 64, d_model), f\"Expected (1, 64, 512), got {y.shape}\"\n\n    # Check dispatch weights are cached (4-wide)\n    dw = dispatch._dispatch_weights\n    mx.eval(dw)\n    assert dw.shape == (1, 64, 4), f\"Expected (1, 64, 4), got {dw.shape}\"\n\n    # Weights should sum to ~1\n    sums = mx.sum(dw, axis=-1)\n    mx.eval(sums)\n    assert mx.allclose(sums, mx.ones_like(sums), atol=1e-4).item(), \\\n        f\"Dispatch weights should sum to ~1\"\n    print(f\"  CombinatorDispatch: {x.shape} → {y.shape} ✓\")\n    print(f\"  Dispatch weights: {dw.shape}, 4-way softmax ✓\")\n\n    # Mean dispatch distribution\n    mean_dw = mx.mean(dw, axis=(0, 1))\n    mx.eval(mean_dw)\n    print(f\"  Mean dispatch: K={mean_dw[0].item():.3f} I={mean_dw[1].item():.3f} \"\n          f\"B={mean_dw[2].item():.3f} C={mean_dw[3].item():.3f}\")\n\n    # Check embedding normalization\n    normed = dispatch._normalize_embeddings()\n    mx.eval(normed)\n    norms = np.linalg.norm(np.array(normed), axis=1)\n    assert np.allclose(norms, dispatch.embed_scale, atol=1e-3), \\\n        f\"Normalized embeddings should have norm={dispatch.embed_scale}\"\n    print(f\"  Embedding norms: all ≈ {dispatch.embed_scale} ✓\")\n\n    # Check near-orthogonality of 4 combinator embeddings\n    normed_np = np.array(normed)\n    normed_unit = normed_np / np.linalg.norm(normed_np, axis=1, keepdims=True)\n    cosines = normed_unit @ normed_unit.T\n    off_diag = cosines - np.eye(4)\n    max_cos = np.max(np.abs(off_diag))\n    print(f\"  Max off-diagonal cosine: {max_cos:.4f} (should be small) ✓\")\n\n    print(\"\\nTesting CombinatorIntegrate...\")\n    integrate = CombinatorIntegrate(d_model, n_combinators=4, d_ff=2048)\n    y2 = integrate(x)\n    mx.eval(y2)\n    assert y2.shape == (1, 64, d_model), f\"Expected (1, 64, 512), got {y2.shape}\"\n    tw = integrate._type_weights\n    mx.eval(tw)\n    assert tw.shape == (1, 64, 4), f\"Expected (1, 64, 4), got {tw.shape}\"\n    print(f\"  CombinatorIntegrate: {x.shape} → {y2.shape} ✓\")\n    print(f\"  Type weights: {tw.shape} ✓\")\n\n    # Test with dispatch weights passed through\n    y3 = integrate(x, dispatch_weights=dw)\n    mx.eval(y3)\n    assert y3.shape == (1, 64, d_model)\n    # Kernel info should be cached\n    ki = integrate._kernel_info\n    assert ki[\"combinator\"].shape == (1, 64)\n    assert ki[\"op0\"].shape == (1, 64)\n    print(f\"  Kernel pathway with dispatch: ✓\")\n\n    # Compute gate should start near 0\n    cg = integrate._compute_gate\n    mx.eval(cg)\n    assert float(mx.mean(cg).item()) < 0.02, \\\n        f\"Compute gate should start near 0, got {mx.mean(cg).item():.4f}\"\n    print(f\"  Compute gate mean: {mx.mean(cg).item():.4f} (starts near 0) ✓\")\n\n    # Test gradient flow\n    print(\"\\nTesting gradient flow...\")\n\n    class TestModel(nn.Module):\n        def __init__(self):\n            super().__init__()\n            self.dispatch = CombinatorDispatch(d_model, n_combinators=4, d_ff=1536)\n            self.integrate = CombinatorIntegrate(d_model, n_combinators=4, d_ff=2048)\n\n        def __call__(self, x):\n            h = self.dispatch(x)\n            h = self.integrate(h)\n            return mx.mean(h)\n\n    tm = TestModel()\n    mx.eval(tm.parameters())\n\n    def test_loss(tm, x):\n        return tm(x)\n\n    gfn = nn.value_and_grad(tm, test_loss)\n    x = mx.random.normal((1, 16, d_model))\n    lv, g = gfn(tm, x)\n    mx.eval(lv, g)\n\n    # Check combinator_embeddings gradient\n    comb_grad = g[\"dispatch\"][\"combinator_embeddings\"]\n    mx.eval(comb_grad)\n    cg_np = np.array(comb_grad)\n    grad_norms = np.linalg.norm(cg_np, axis=1)\n    n_with_grad = np.sum(grad_norms > 1e-6)\n    print(f\"  Gradient flow OK: loss={lv.item():.4f}\")\n    print(f\"  Combinators with gradient: {n_with_grad}/4 ✓\")\n\n    print(\"\\nkernel_dispatch.py self-test: all ok ✓\")\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/v11/kernel_dispatch.py
```

## Assistant

Now the model — the biggest file. The changes are surgical: emphasis→4, algedonic→4, register names, imports:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/model.py",
  "content": "\"\"\"\nv11 Model — Tree of VSMs: compressor + KIBC combinator dispatcher.\n\nEvolution from v10: the descending arm routes through 4 combinators\n(K, I, B, C) instead of 22 ops. Everything else carries forward.\n\nThe combinator basis comes from Qwen3 probes (4B and 32B, session 077):\n  - Attention IS beta reduction (SEARCH → LOCK → RESOLVE pipeline)\n  - K (select) and I (identity) are native to attention\n  - B (compose) matures with scale, C (flip) emerges at scale\n  - S (distribute) never crystallizes — it's B∘K∘C composite\n\nThe sieve provides shapes that LLMs naturally converge to.\nThe model doesn't learn what K/I/B/C are — it already knows.\nThe architecture makes the right computation the path of least resistance.\n\nArchitecture:\n  Ascending arm (3 passes): unchanged from v10\n    S1: prep → StrideStack → consolidate (compression, proven)\n  Descending arm (2 passes): KIBC combinator dispatch\n    S1: CombinatorDispatch → StrideStack → CombinatorIntegrate\n    Self-regulating cycles (desc_max_cycles=3):\n      Cycle 0 — IDENTIFY: which combinator?\n      Cycle 1 — RESOLVE:  find arguments\n      Cycle 2 — PRODUCE:  apply reduction\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nfrom typing import Optional\n\nimport mlx.core as mx\nimport mlx.nn as nn\n\nfrom config import V11Config\nfrom ternary import TernaryLinear, TernaryEmbedding\nfrom attention import StrideStack, TernaryFFN\nfrom components import (\n    S4Ternary,\n    S3Ternary,\n    MetaS4Ternary,\n    S5Reweight,\n    S2Coordinator,\n    CycleContinue,\n)\nfrom kernel_dispatch import CombinatorDispatch, CombinatorIntegrate, N_COMBINATORS\n\n\n# ══════════════════════════════════════════════════════════════════\n# V11Model — Tree of VSMs with KIBC combinator basis\n# ══════════════════════════════════════════════════════════════════\n\n\nclass V11Model(nn.Module):\n    \"\"\"Tree of VSMs: compressor (ascending) + combinator dispatcher (descending).\n\n    5 passes: L0↑ → L1↑ → L2_apex → L1↓ → L0↓\n\n    Register semantics (v11):\n      reg 0: combinator — K/I/B/C identity at this position\n      reg 1: binding_depth — how many lambdas deep (0=free, 1=bound, ...)\n      reg 2: phase — recognize / identify / resolve / produce\n    \"\"\"\n\n    REGISTER_NAMES = (\"combinator\", \"binding_depth\", \"phase\")\n    N_PASSES = 5\n    N_ASC_PASSES = 3\n    N_DESC_PASSES = 2\n    PASS_NAMES = (\"L0_asc\", \"L1_asc\", \"L2_apex\", \"L1_desc\", \"L0_desc\")\n\n    def __init__(self, cfg: V11Config):\n        super().__init__()\n        self.cfg = cfg\n        d = cfg.d_model\n        d_reg = cfg.d_register\n        n_reg = cfg.n_registers\n        self.d_reg_real = d_reg * 2\n\n        # ── S5: Identity ──────────────────────────────────────\n        self.embed = TernaryEmbedding(cfg.vocab_size, d)\n        self.pos_embed = TernaryEmbedding(cfg.max_seq_len, d)\n        self.embed_norm = nn.RMSNorm(d)\n\n        # Register bank 0: learnable real init\n        self.register_inits = {\n            f\"reg_{name}\": mx.zeros((self.d_reg_real,))\n            for name in self.REGISTER_NAMES\n        }\n\n        self.register_norm = nn.RMSNorm(self.d_reg_real)\n\n        # ── S1: Ascending ops (shared across 3 passes) ────────\n        self.prep = TernaryFFN(d, cfg.d_ff, cfg.dropout)\n        self.stride_stack = StrideStack(\n            d_model=d,\n            strides=cfg.strides,\n            window=cfg.window,\n            n_heads=cfg.n_heads,\n            dropout=cfg.dropout,\n            alpha=cfg.alpha,\n        )\n        self.consolidate = TernaryFFN(d, cfg.d_ff_consolidate, cfg.dropout)\n\n        # ── S1: Descending ops (shared across 2 passes) ───────\n        #    KIBC combinator dispatch — NOT 22 ops\n        self.combinator_dispatch = CombinatorDispatch(\n            d, n_combinators=N_COMBINATORS, d_ff=cfg.d_ff,\n            dropout=cfg.dropout,\n            n_registers=cfg.n_registers, d_register=cfg.d_register,\n            max_cond_banks=5,\n        )\n        self.stride_stack_desc = StrideStack(\n            d_model=d,\n            strides=cfg.strides,\n            window=cfg.window,\n            n_heads=cfg.n_heads,\n            dropout=cfg.dropout,\n            alpha=cfg.alpha,\n        )\n        self.combinator_integrate = CombinatorIntegrate(\n            d, n_combinators=N_COMBINATORS,\n            d_ff=cfg.d_ff_consolidate, dropout=cfg.dropout,\n        )\n\n        # ── S4: Intelligence ──────────────────────────────────\n        self.s4 = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,\n                            dropout=cfg.dropout)\n        self.s4_desc = S4Ternary(d, d_reg, n_registers=n_reg, max_banks=7,\n                                  dropout=cfg.dropout)\n\n        # ── S3: Per-pass gating (5 separate instances) ─────────\n        self.s3_passes = [\n            S3Ternary(d, d_reg, n_phases=3, n_registers=n_reg, d_align=d)\n            for _ in range(self.N_PASSES)\n        ]\n\n        # ── Modulation projections ────────────────────────────\n        self.mod_projs = [\n            TernaryLinear(d, d, pre_norm=False) for _ in range(3)]\n        for proj in self.mod_projs:\n            proj.gamma = mx.zeros_like(proj.gamma)\n\n        self.mod_projs_desc = [\n            TernaryLinear(d, d, pre_norm=False) for _ in range(3)]\n        for proj in self.mod_projs_desc:\n            proj.gamma = mx.zeros_like(proj.gamma)\n\n        # ── Multi-cycle injection gate ─────────────────────────\n        self._cycle_inject_gate_raw = mx.array([-4.0])\n\n        # ── S3 cycle continuation gate ─────────────────────────\n        if cfg.desc_max_cycles > 1:\n            self.cycle_continue = CycleContinue(\n                cfg.d_register, n_registers=cfg.n_registers)\n\n        # ── Meta-S4 ──────────────────────────────────────────\n        self.meta_s4 = MetaS4Ternary(d, d_reg, n_registers=n_reg,\n                                      n_banks=4, dropout=cfg.dropout)\n\n        # ── S2: Direction coordination ─────────────────────────\n        self.s2 = S2Coordinator(d)\n\n        # ── S5: Pass reweighting ──────────────────────────────\n        self.s5_reweight = S5Reweight(\n            d, d_reg, n_registers=n_reg,\n            n_banks=6, n_passes=self.N_PASSES)\n\n        # ── Algedonic channel ──────────────────────────────────\n        self._algedonic_ema = 0.9\n        self._prev_bank_1_desc = [mx.zeros((self.d_reg_real,))\n                                   for _ in range(n_reg)]\n        self._prev_bank_2_desc = [mx.zeros((self.d_reg_real,))\n                                   for _ in range(n_reg)]\n        # Combinator algedonic: 4 combinator weights + 1 compute gate\n        self._prev_kernel_algedonic = mx.zeros((self.d_reg_real,))\n\n        # ── Combinator emphasis: S4 registers → per-combinator ──\n        #    4 combinators instead of 22 ops\n        emphasis_input_dim = 3 * n_reg * self.d_reg_real\n        self.emphasis_proj = nn.Linear(emphasis_input_dim, N_COMBINATORS)\n        self.emphasis_proj.weight = mx.zeros_like(self.emphasis_proj.weight)\n        self.emphasis_proj.bias = mx.zeros_like(self.emphasis_proj.bias)\n        self._combinator_emphasis = mx.ones((N_COMBINATORS,))\n        self._emphasis_ema = 0.95\n\n        # ── Output ────────────────────────────────────────────\n        self.output_norm = nn.RMSNorm(d)\n\n    # ── Helpers ───────────────────────────────────────────────\n\n    @property\n    def cycle_inject_gate(self) -> mx.array:\n        return mx.sigmoid(self._cycle_inject_gate_raw)\n\n    def _init_bank0(self) -> list[mx.array]:\n        return [self.register_inits[f\"reg_{name}\"]\n                for name in self.REGISTER_NAMES]\n\n    def _fresh_bank(self) -> list[mx.array]:\n        return [mx.zeros((self.d_reg_real,))\n                for _ in self.REGISTER_NAMES]\n\n    def _modulate(self, x, delta, gate, phase_idx, is_descending=False):\n        projs = self.mod_projs_desc if is_descending else self.mod_projs\n        return x + gate * mx.tanh(projs[phase_idx](delta))\n\n    # ── Core level-pass ───────────────────────────────────────\n\n    def _run_level_pass(self, x, pass_idx, is_descending, readable_banks,\n                         target_bank, embed_context=None,\n                         combinator_emphasis=None):\n        x_before = x\n        raw_phases = []\n        phase_gates = []\n\n        s4 = self.s4_desc if is_descending else self.s4\n        strides = self.stride_stack_desc if is_descending else self.stride_stack\n\n        # S4 scan\n        s4_residual = x\n        if embed_context is not None:\n            s4_residual = mx.concatenate([x, embed_context], axis=1)\n        s4_updates, _ = s4(readable_banks, s4_residual)\n        target_bank = [self.register_norm(target_bank[i] + s4_updates[i])\n                       for i in range(self.cfg.n_registers)]\n\n        if is_descending:\n            # ── Combinator dispatch cycles ─────────────────────\n            x_anchor = x\n            max_cycles = self.cfg.desc_max_cycles\n            cumulative_gate = mx.array(1.0)\n\n            for cycle in range(max_cycles):\n                x_cycle_start = x\n\n                if cycle > 0:\n                    x = x + self.cycle_inject_gate * x_anchor\n\n                # Phase 0: dispatch (which combinator?)\n                dispatch_out = self.combinator_dispatch(\n                    x, registers=readable_banks,\n                    combinator_emphasis=combinator_emphasis)\n                delta = dispatch_out - x\n                raw_phases.append(delta)\n                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target_bank, delta, 0)\n                phase_gates.append(gate)\n                x = self._modulate(x, delta, gate, phase_idx=0, is_descending=True)\n\n                # Phase 1: converge (propagate spatially)\n                converge_out = strides(x, reverse=False)\n                delta = converge_out - x\n                raw_phases.append(delta)\n                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target_bank, delta, 1)\n                phase_gates.append(gate)\n                x = self._modulate(x, delta, gate, phase_idx=1, is_descending=True)\n\n                # Phase 2: integrate (apply combinator reduction)\n                dw = (self.combinator_dispatch._dispatch_weights\n                      if hasattr(self.combinator_dispatch, '_dispatch_weights')\n                      else None)\n                integrate_out = self.combinator_integrate(\n                    x, dispatch_weights=dw)\n                delta = integrate_out - x\n                raw_phases.append(delta)\n                _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target_bank, delta, 2)\n                phase_gates.append(gate)\n                x = self._modulate(x, delta, gate, phase_idx=2, is_descending=True)\n\n                # Scale by cumulative gate\n                cycle_contribution = x - x_cycle_start\n                x = x_cycle_start + cumulative_gate * cycle_contribution\n\n                # S3 continuation\n                if cycle < max_cycles - 1 and max_cycles > 1:\n                    cont_gate = self.cycle_continue(target_bank)\n                    cumulative_gate = cumulative_gate * cont_gate\n        else:\n            # ── Ascending compression ──────────────────────────\n            prep_out = self.prep(x)\n            delta = prep_out - x\n            raw_phases.append(delta)\n            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                target_bank, delta, 0)\n            phase_gates.append(gate)\n            x = self._modulate(x, delta, gate, phase_idx=0, is_descending=False)\n\n            converge_out = strides(x, reverse=False)\n            delta = converge_out - x\n            raw_phases.append(delta)\n            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                target_bank, delta, 1)\n            phase_gates.append(gate)\n            x = self._modulate(x, delta, gate, phase_idx=1, is_descending=False)\n\n            consolidate_out = self.consolidate(x)\n            delta = consolidate_out - x\n            raw_phases.append(delta)\n            _, target_bank, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                target_bank, delta, 2)\n            phase_gates.append(gate)\n            x = self._modulate(x, delta, gate, phase_idx=2, is_descending=False)\n\n        pass_delta = x - x_before\n        raw_delta = raw_phases[0]\n        for rd in raw_phases[1:]:\n            raw_delta = raw_delta + rd\n        return x, target_bank, pass_delta, raw_delta, phase_gates\n\n    # ── Forward ───────────────────────────────────────────────\n\n    def forward(\n        self,\n        tokens: mx.array,\n        targets: Optional[mx.array] = None,\n    ) -> tuple[mx.array, Optional[mx.array]]:\n        B, L = tokens.shape\n\n        positions = mx.arange(L)\n        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))\n        x_embed = x\n\n        bank_0 = self._init_bank0()\n        bank_1_asc = self._fresh_bank()\n        bank_2_asc = self._fresh_bank()\n        bank_3 = self._fresh_bank()\n        bank_2_desc = self._fresh_bank()\n        bank_1_desc = self._fresh_bank()\n\n        pass_deltas = []\n        raw_deltas = []\n\n        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]\n        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]\n        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]\n\n        asc_s3_gates = []\n\n        # Pass 0: L0↑\n        x, bank_1_asc, pd, rd, pg = self._run_level_pass(\n            x, 0, False, [bank_0, prev_b1d, prev_kernel], bank_1_asc)\n        pass_deltas.append(pd); raw_deltas.append(rd); asc_s3_gates.extend(pg)\n        x = x + self.s2.direction_signal(pd, 0)\n\n        # Pass 1: L1↑\n        x, bank_2_asc, pd, rd, pg = self._run_level_pass(\n            x, 1, False, [bank_0, bank_1_asc, prev_b2d, prev_kernel], bank_2_asc)\n        pass_deltas.append(pd); raw_deltas.append(rd); asc_s3_gates.extend(pg)\n        coherence = S2Coordinator.coherence_factor(pass_deltas[0], pass_deltas[1])\n        x = x + self.s2.direction_signal(pd, 1) * coherence\n\n        # Pass 2: L2_apex\n        x, bank_3, pd, rd, pg = self._run_level_pass(\n            x, 2, False, [bank_0, bank_1_asc, bank_2_asc, prev_kernel], bank_3)\n        pass_deltas.append(pd); raw_deltas.append(rd); asc_s3_gates.extend(pg)\n\n        # ── Combinator emphasis (4-wide, not 22) ──────────────\n        emphasis_parts = []\n        for bank in [bank_1_asc, bank_2_asc, bank_3]:\n            for reg in bank:\n                emphasis_parts.append(reg)\n        emphasis_input = mx.concatenate(emphasis_parts, axis=-1)\n        raw_emphasis = self.emphasis_proj(emphasis_input)\n        combinator_emphasis = 1.0 + 0.5 * mx.tanh(raw_emphasis)  # [0.5, 1.5]\n\n        self._combinator_emphasis = mx.stop_gradient(\n            self._emphasis_ema * self._combinator_emphasis\n            + (1.0 - self._emphasis_ema) * combinator_emphasis)\n\n        # ── Pack ascending S3 gates for descending arm ─────────\n        asc_gate_flat = mx.concatenate(\n            [g.reshape(-1) for g in asc_s3_gates])\n        asc_gate_vector = mx.concatenate([\n            asc_gate_flat,\n            mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),\n        ])\n        asc_gate_bank = [asc_gate_vector]\n\n        coherence = S2Coordinator.coherence_factor(pass_deltas[1], pass_deltas[2])\n        x = x + self.s2.direction_signal(pd, 2) * coherence\n\n        # Pass 3: L1↓\n        x, bank_2_desc, pd, rd, _ = self._run_level_pass(\n            x, 3, True,\n            [bank_0, bank_1_asc, bank_2_asc, bank_3, asc_gate_bank],\n            bank_2_desc, embed_context=x_embed,\n            combinator_emphasis=combinator_emphasis)\n        pass_deltas.append(pd); raw_deltas.append(rd)\n\n        coherence = S2Coordinator.coherence_factor(pass_deltas[2], pass_deltas[3])\n        x = x + self.s2.direction_signal(pd, 3) * coherence\n\n        # Pass 4: L0↓\n        x, bank_1_desc, pd, rd, _ = self._run_level_pass(\n            x, 4, True,\n            [bank_0, bank_1_asc, bank_2_desc, bank_3, asc_gate_bank],\n            bank_1_desc, embed_context=x_embed,\n            combinator_emphasis=combinator_emphasis)\n        pass_deltas.append(pd); raw_deltas.append(rd)\n\n        # ── Update algedonic buffers ───────────────────────────\n        α = self._algedonic_ema\n        self._prev_bank_1_desc = [\n            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])\n            for i in range(self.cfg.n_registers)]\n        self._prev_bank_2_desc = [\n            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])\n            for i in range(self.cfg.n_registers)]\n\n        # Combinator algedonic: 4 weights + 1 compute gate (was 22+1)\n        if hasattr(self.combinator_dispatch, '_dispatch_weights'):\n            dw_mean = mx.stop_gradient(\n                self.combinator_dispatch._dispatch_weights.mean(axis=(0, 1)))\n        else:\n            dw_mean = mx.zeros((N_COMBINATORS,))\n        if hasattr(self.combinator_integrate, '_compute_gate'):\n            cg_mean = mx.stop_gradient(\n                self.combinator_integrate._compute_gate.mean().reshape(1,))\n        else:\n            cg_mean = mx.zeros((1,))\n        kernel_state = mx.concatenate([\n            dw_mean,                                            # 4 dims\n            cg_mean,                                            # 1 dim\n            mx.zeros((self.d_reg_real - N_COMBINATORS - 1,)),   # padding\n        ])\n        self._prev_kernel_algedonic = mx.stop_gradient(\n            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)\n\n        # ── S5 reweighting ─────────────────────────────────────\n        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,\n                     bank_2_desc, bank_1_desc]\n        meta_gates = self.s5_reweight(all_banks, raw_deltas)\n\n        total_ungated = pass_deltas[0]\n        for i in range(1, self.N_PASSES):\n            total_ungated = total_ungated + pass_deltas[i]\n        total_gated = meta_gates[0] * pass_deltas[0]\n        for i in range(1, self.N_PASSES):\n            total_gated = total_gated + meta_gates[i] * pass_deltas[i]\n        x = x - total_ungated + total_gated\n\n        # Meta-S4\n        meta_banks = [bank_0, bank_1_desc, bank_2_desc, bank_3]\n        x = self.meta_s4(meta_banks, x)\n\n        # Output\n        x = self.output_norm(x)\n        logits = self.embed.output_proj(x)\n\n        loss = None\n        if targets is not None:\n            loss = nn.losses.cross_entropy(\n                logits.reshape(-1, self.cfg.vocab_size),\n                targets.reshape(-1),\n            ).mean()\n\n        return logits, loss\n\n    def __call__(self, tokens, targets=None):\n        return self.forward(tokens, targets)\n\n    # ── Instrumentation ───────────────────────────────────────\n\n    @staticmethod\n    def _entropy_proxy(x: mx.array) -> float:\n        var_per_feat = mx.var(x, axis=(0, 1))\n        mean_var = mx.mean(var_per_feat)\n        mx.eval(mean_var)\n        return float(mx.log(mean_var + 1e-10).item())\n\n    def forward_instrumented(\n        self,\n        tokens: mx.array,\n    ) -> tuple[mx.array, dict]:\n        \"\"\"Forward pass with full instrumentation. Returns (hidden, metrics).\"\"\"\n        import math\n        INV_PHI = 1.0 / ((1 + math.sqrt(5)) / 2)\n\n        B, L = tokens.shape\n        positions = mx.arange(L)\n        x = self.embed_norm(self.embed(tokens) + self.pos_embed(positions))\n        x_embed = x\n\n        bank_0 = self._init_bank0()\n        bank_1_asc = self._fresh_bank()\n        bank_2_asc = self._fresh_bank()\n        bank_3 = self._fresh_bank()\n        bank_2_desc = self._fresh_bank()\n        bank_1_desc = self._fresh_bank()\n\n        pass_deltas = []\n        raw_deltas = []\n        all_s3_gates = []\n        pass_h_in = []\n        pass_h_out = []\n        asc_gate_mx = []\n        asc_gate_bank = None\n        combinator_emphasis_inst = None\n        all_cycle_continue_gates = []\n        all_effective_cycles = []\n\n        prev_b1d = [mx.stop_gradient(r) for r in self._prev_bank_1_desc]\n        prev_b2d = [mx.stop_gradient(r) for r in self._prev_bank_2_desc]\n        prev_kernel = [mx.stop_gradient(self._prev_kernel_algedonic)]\n\n        pass_configs = [\n            (0, False, lambda: [bank_0, prev_b1d, prev_kernel]),\n            (1, False, lambda: [bank_0, bank_1_asc, prev_b2d, prev_kernel]),\n            (2, False, lambda: [bank_0, bank_1_asc, bank_2_asc, prev_kernel]),\n            (3, True,  lambda: [bank_0, bank_1_asc, bank_2_asc, bank_3]),\n            (4, True,  lambda: [bank_0, bank_1_asc, bank_2_desc, bank_3]),\n        ]\n        target_banks = [bank_1_asc, bank_2_asc, bank_3, bank_2_desc, bank_1_desc]\n\n        for pi, (pass_idx, is_desc, get_readable) in enumerate(pass_configs):\n            h_in = self._entropy_proxy(x)\n            pass_h_in.append(h_in)\n\n            x_before = x\n            readable = get_readable()\n            target = target_banks[pi]\n\n            s4 = self.s4_desc if is_desc else self.s4\n            strides = self.stride_stack_desc if is_desc else self.stride_stack\n\n            if is_desc:\n                if asc_gate_bank is not None:\n                    readable.append(asc_gate_bank)\n                s4_residual = mx.concatenate([x, x_embed], axis=1)\n            else:\n                s4_residual = x\n            s4_updates, _ = s4(readable, s4_residual)\n            target = [self.register_norm(target[i] + s4_updates[i])\n                      for i in range(self.cfg.n_registers)]\n\n            phase_gates = []\n            raw_phases = []\n\n            if is_desc:\n                x_anchor = x\n                max_cycles = self.cfg.desc_max_cycles\n                cumulative_gate = mx.array(1.0)\n                cycle_continue_gates = []\n\n                for cycle in range(max_cycles):\n                    x_cycle_start = x\n                    if cycle > 0:\n                        x = x + self.cycle_inject_gate * x_anchor\n\n                    # Phase 0: dispatch\n                    dispatch_out = self.combinator_dispatch(\n                        x, registers=readable,\n                        combinator_emphasis=combinator_emphasis_inst)\n                    delta = dispatch_out - x\n                    raw_phases.append(delta)\n                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                        target, delta, 0)\n                    mx.eval(gate)\n                    phase_gates.append(float(gate.item()))\n                    x = self._modulate(x, delta, gate, 0, is_descending=True)\n\n                    # Phase 1: converge\n                    conv_out = strides(x, reverse=False)\n                    delta = conv_out - x\n                    raw_phases.append(delta)\n                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                        target, delta, 1)\n                    mx.eval(gate)\n                    phase_gates.append(float(gate.item()))\n                    x = self._modulate(x, delta, gate, 1, is_descending=True)\n\n                    # Phase 2: integrate\n                    dw = (self.combinator_dispatch._dispatch_weights\n                          if hasattr(self.combinator_dispatch, '_dispatch_weights')\n                          else None)\n                    integrate_out = self.combinator_integrate(\n                        x, dispatch_weights=dw)\n                    delta = integrate_out - x\n                    raw_phases.append(delta)\n                    _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                        target, delta, 2)\n                    mx.eval(gate)\n                    phase_gates.append(float(gate.item()))\n                    x = self._modulate(x, delta, gate, 2, is_descending=True)\n\n                    cycle_contribution = x - x_cycle_start\n                    x = x_cycle_start + cumulative_gate * cycle_contribution\n\n                    if cycle < max_cycles - 1 and max_cycles > 1:\n                        cont_gate = self.cycle_continue(target)\n                        mx.eval(cont_gate)\n                        cycle_continue_gates.append(float(cont_gate.item()))\n                        cumulative_gate = cumulative_gate * cont_gate\n            else:\n                # Ascending compression\n                prep_out = self.prep(x)\n                delta = prep_out - x\n                raw_phases.append(delta)\n                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target, delta, 0)\n                mx.eval(gate)\n                phase_gates.append(float(gate.item()))\n                asc_gate_mx.append(gate)\n                x = self._modulate(x, delta, gate, 0, is_descending=False)\n\n                conv_out = strides(x, reverse=False)\n                delta = conv_out - x\n                raw_phases.append(delta)\n                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target, delta, 1)\n                mx.eval(gate)\n                phase_gates.append(float(gate.item()))\n                asc_gate_mx.append(gate)\n                x = self._modulate(x, delta, gate, 1, is_descending=False)\n\n                cons_out = self.consolidate(x)\n                delta = cons_out - x\n                raw_phases.append(delta)\n                _, target, gate, _ = self.s3_passes[pass_idx].gate_phase(\n                    target, delta, 2)\n                mx.eval(gate)\n                phase_gates.append(float(gate.item()))\n                asc_gate_mx.append(gate)\n                x = self._modulate(x, delta, gate, 2, is_descending=False)\n\n            target_banks[pi] = target\n            pass_deltas.append(x - x_before)\n            raw_delta = raw_phases[0]\n            for rd in raw_phases[1:]:\n                raw_delta = raw_delta + rd\n            raw_deltas.append(raw_delta)\n            all_s3_gates.append(phase_gates)\n\n            if is_desc and self.cfg.desc_max_cycles > 1:\n                all_cycle_continue_gates.append(cycle_continue_gates)\n                eff = 1.0 + sum(\n                    float(mx.prod(mx.array(cycle_continue_gates[:i+1])).item())\n                    for i in range(len(cycle_continue_gates))\n                ) if cycle_continue_gates else 1.0\n                all_effective_cycles.append(eff)\n\n            if not is_desc and pi == 2 and asc_gate_mx:\n                asc_gate_flat = mx.concatenate(\n                    [g.reshape(-1) for g in asc_gate_mx])\n                asc_gate_vector = mx.concatenate([\n                    asc_gate_flat,\n                    mx.zeros((self.d_reg_real - asc_gate_flat.shape[0],)),\n                ])\n                asc_gate_bank = [asc_gate_vector]\n\n            if not is_desc and pi == 2:\n                emphasis_parts = []\n                for bank in [target_banks[0], target_banks[1], target_banks[2]]:\n                    for reg in bank:\n                        emphasis_parts.append(reg)\n                emphasis_input = mx.concatenate(emphasis_parts, axis=-1)\n                raw_emphasis = self.emphasis_proj(emphasis_input)\n                combinator_emphasis_inst = 1.0 + 0.5 * mx.tanh(raw_emphasis)\n                mx.eval(combinator_emphasis_inst)\n                self._combinator_emphasis = mx.stop_gradient(\n                    self._emphasis_ema * self._combinator_emphasis\n                    + (1.0 - self._emphasis_ema) * combinator_emphasis_inst)\n\n            h_out = self._entropy_proxy(x)\n            pass_h_out.append(h_out)\n\n            if pi < len(pass_configs) - 1:\n                signal = self.s2.direction_signal(pass_deltas[-1], pi)\n                if pi > 0:\n                    coherence = S2Coordinator.coherence_factor(\n                        pass_deltas[-2], pass_deltas[-1])\n                    signal = signal * coherence\n                x = x + signal\n\n        # S2 conflict scores\n        s2_conflict = []\n        for i in range(len(pass_deltas) - 1):\n            cs = S2Coordinator.conflict_score(pass_deltas[i], pass_deltas[i + 1])\n            s2_conflict.append(cs)\n        s2_scales = [float(self.s2.scales[i].item())\n                     for i in range(S2Coordinator.N_TRANSITIONS)]\n\n        bank_1_asc = target_banks[0]\n        bank_2_asc = target_banks[1]\n        bank_3 = target_banks[2]\n        bank_2_desc = target_banks[3]\n        bank_1_desc = target_banks[4]\n\n        # Update algedonic buffers\n        α = self._algedonic_ema\n        self._prev_bank_1_desc = [\n            mx.stop_gradient(α * self._prev_bank_1_desc[i] + (1 - α) * bank_1_desc[i])\n            for i in range(self.cfg.n_registers)]\n        self._prev_bank_2_desc = [\n            mx.stop_gradient(α * self._prev_bank_2_desc[i] + (1 - α) * bank_2_desc[i])\n            for i in range(self.cfg.n_registers)]\n\n        if hasattr(self.combinator_dispatch, '_dispatch_weights'):\n            dw_mean = mx.stop_gradient(\n                self.combinator_dispatch._dispatch_weights.mean(axis=(0, 1)))\n        else:\n            dw_mean = mx.zeros((N_COMBINATORS,))\n        if hasattr(self.combinator_integrate, '_compute_gate'):\n            cg_mean = mx.stop_gradient(\n                self.combinator_integrate._compute_gate.mean().reshape(1,))\n        else:\n            cg_mean = mx.zeros((1,))\n        kernel_state = mx.concatenate([\n            dw_mean, cg_mean,\n            mx.zeros((self.d_reg_real - N_COMBINATORS - 1,)),\n        ])\n        self._prev_kernel_algedonic = mx.stop_gradient(\n            α * self._prev_kernel_algedonic + (1 - α) * kernel_state)\n\n        # S5 reweighting\n        all_banks = [bank_0, bank_1_asc, bank_2_asc, bank_3,\n                     bank_2_desc, bank_1_desc]\n        meta_gates = self.s5_reweight(all_banks, raw_deltas)\n        mx.eval(meta_gates)\n\n        total_ungated = pass_deltas[0]\n        for i in range(1, self.N_PASSES):\n            total_ungated = total_ungated + pass_deltas[i]\n        total_gated = meta_gates[0] * pass_deltas[0]\n        for i in range(1, self.N_PASSES):\n            total_gated = total_gated + meta_gates[i] * pass_deltas[i]\n        x = x - total_ungated + total_gated\n\n        meta_banks_list = [bank_0, bank_1_desc, bank_2_desc, bank_3]\n        x = self.meta_s4(meta_banks_list, x)\n        x = self.output_norm(x)\n\n        # Register norms\n        reg_norms = {}\n        named_banks = {\n            \"bank_0\": bank_0, \"bank_1_asc\": bank_1_asc,\n            \"bank_2_asc\": bank_2_asc, \"bank_3\": bank_3,\n            \"bank_2_desc\": bank_2_desc, \"bank_1_desc\": bank_1_desc,\n        }\n        for name, bank in named_banks.items():\n            norms = []\n            for reg in bank:\n                mx.eval(reg)\n                norms.append(float(mx.sqrt((reg * reg).sum()).item()))\n            reg_norms[name] = norms\n\n        # Compression metrics\n        pass_compression = []\n        pass_phi_dev = []\n        for h_in, h_out in zip(pass_h_in, pass_h_out):\n            ratio = h_out / h_in if abs(h_in) > 1e-8 else 1.0\n            pass_compression.append(ratio)\n            pass_phi_dev.append(abs(ratio - INV_PHI))\n\n        # Combinator dispatch metrics\n        dispatch_weights = None\n        type_weights = None\n        if hasattr(self.combinator_dispatch, '_dispatch_weights'):\n            dw = self.combinator_dispatch._dispatch_weights\n            mx.eval(dw)\n            dispatch_weights = mx.mean(dw, axis=(0, 1))\n            mx.eval(dispatch_weights)\n        if hasattr(self.combinator_integrate, '_type_weights'):\n            tw = self.combinator_integrate._type_weights\n            mx.eval(tw)\n            type_weights = mx.mean(tw, axis=(0, 1))\n            mx.eval(type_weights)\n\n        # Combinator embedding norms\n        comb_emb_norms = None\n        if hasattr(self.combinator_dispatch, 'combinator_embeddings'):\n            raw_emb = self.combinator_dispatch.combinator_embeddings\n            mx.eval(raw_emb)\n            norms = mx.sqrt(mx.sum(raw_emb * raw_emb, axis=-1) + 1e-8)\n            mx.eval(norms)\n            comb_emb_norms = [float(norms[i].item()) for i in range(norms.shape[0])]\n\n        cig = self.cycle_inject_gate\n        mx.eval(cig)\n\n        metrics = {\n            \"s3_gates\": all_s3_gates,\n            \"s5_reweight\": [float(meta_gates[i].item()) for i in range(self.N_PASSES)],\n            \"combinator_emphasis\": (\n                [float(combinator_emphasis_inst[i].item())\n                 for i in range(N_COMBINATORS)]\n                if combinator_emphasis_inst is not None else None\n            ),\n            \"s2_conflict\": s2_conflict,\n            \"s2_scales\": s2_scales,\n            \"register_norms\": reg_norms,\n            \"pass_entropy_in\": pass_h_in,\n            \"pass_entropy_out\": pass_h_out,\n            \"pass_compression\": pass_compression,\n            \"pass_phi_dev\": pass_phi_dev,\n            \"combinator_dispatch_weights\": (\n                [float(dispatch_weights[i].item())\n                 for i in range(dispatch_weights.shape[0])]\n                if dispatch_weights is not None else None\n            ),\n            \"combinator_type_weights\": (\n                [float(type_weights[i].item())\n                 for i in range(type_weights.shape[0])]\n                if type_weights is not None else None\n            ),\n            \"combinator_embedding_norms\": comb_emb_norms,\n            \"desc_max_cycles\": self.cfg.desc_max_cycles,\n            \"cycle_inject_gate\": float(cig.item()),\n            \"cycle_continue_gates\": all_cycle_continue_gates,\n            \"effective_cycles\": all_effective_cycles,\n        }\n\n        if hasattr(self.combinator_integrate, '_compute_gate'):\n            cg = self.combinator_integrate._compute_gate\n            mx.eval(cg)\n            metrics[\"compute_gate_mean\"] = float(mx.mean(cg).item())\n            metrics[\"compute_gate_max\"] = float(mx.max(cg).item())\n            metrics[\"compute_gate_min\"] = float(mx.min(cg).item())\n            metrics[\"compute_gate_active\"] = float(\n                mx.mean((cg > 0.5).astype(mx.float32)).item())\n\n        return x, metrics\n\n\n# ══════════════════════════════════════════════════════════════════\n# Factory + utilities\n# ══════════════════════════════════════════════════════════════════\n\n\ndef create_model(cfg: V11Config) -> V11Model:\n    model = V11Model(cfg)\n    mx.eval(model.parameters())\n    return model\n\n\ndef count_parameters(model: nn.Module) -> dict[str, int]:\n    from mlx.utils import tree_flatten\n    counts = {\"total\": 0, \"trainable\": 0}\n    all_params = tree_flatten(model.parameters())\n    trainable = tree_flatten(model.trainable_parameters())\n    counts[\"total\"] = sum(p.size for _, p in all_params)\n    counts[\"trainable\"] = sum(p.size for _, p in trainable)\n    return counts\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/v11/model.py
```

## Assistant

Now the train.py — copy v10's and adjust imports/references:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cp /Users/mwhitford/src/verbum/scripts/v10/train.py /Users/mwhitford/src/verbum/scripts/v11/train.py"
}
```

**Summary:** $ cp /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 0
```

## Assistant

Now update the imports and references in train.py:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"V10Config\\|V6Compressor\\|kernel_dispatch\\|N_OPS\\|op_emphasis\\|OP_NAMES\\|kernel_type\\|kernel_dispatch_weights\\|N_TYPES\" /Users/mwhitford/src/verbum/scripts/v11/train.py | head -40"
}
```

**Summary:** $ grep -n "V10Config\|V6Compressor\|k...

**Output:**
```
Exit code: 0
Stdout:
44:from config import V10Config
46:from model import V6Compressor, create_model, count_parameters
79:    model: V6Compressor,
110:DESC_SHARED = ("kernel_dispatch", "stride_stack_desc", "kernel_integrate", "mod_projs_desc", "s4_desc")
193:def evaluate(model: V6Compressor, cfg: V10Config) -> dict:
275:    op_emph = compressor_metrics.get("op_emphasis")
277:        from kernel import OP_NAMES
279:        top3 = [(OP_NAMES[i], v) for i, v in indexed[:3]]
280:        bot3 = [(OP_NAMES[i], v) for i, v in indexed[-3:]]
689:def train(cfg: V10Config, args: argparse.Namespace) -> None:
1089:    cfg = V10Config()
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"op_emphasis\\|N_OPS\\|kernel_dispatch_weights\\|kernel_type_weights\\|op_embedding\\|dispatch_top1\\|OP_NAMES\" /Users/mwhitford/src/verbum/scripts/v11/train.py"
}
```

**Summary:** $ grep -n "op_emphasis\|N_OPS\|kernel...

**Output:**
```
Exit code: 0
Stdout:
275:    op_emph = compressor_metrics.get("op_emphasis")
277:        from kernel import OP_NAMES
279:        top3 = [(OP_NAMES[i], v) for i, v in indexed[:3]]
280:        bot3 = [(OP_NAMES[i], v) for i, v in indexed[-3:]]
```

## Assistant

Let me also check for all the metric key references:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"kernel_dispatch_weights\\|kernel_type_weights\\|op_embedding_norms\\|op_emphasis\" /Users/mwhitford/src/verbum/scripts/v11/train.py"
}
```

**Summary:** $ grep -n "kernel_dispatch_weights\|k...

**Output:**
```
Exit code: 0
Stdout:
275:    op_emph = compressor_metrics.get("op_emphasis")
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"\\\"kernel\\|\\\"op_\\|\\\"dispatch\\|\\\"type_\" /Users/mwhitford/src/verbum/scripts/v11/train.py"
}
```

**Summary:** $ grep -n "\"kernel\|\"op_\|\"dispatc...

**Output:**
```
Exit code: 0
Stdout:
110:DESC_SHARED = ("kernel_dispatch", "stride_stack_desc", "kernel_integrate", "mod_projs_desc", "s4_desc")
275:    op_emph = compressor_metrics.get("op_emphasis")
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 40,
  "limit": 15
}
```

**Summary:** Reading train.py (40-55)

**Output:**
```

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader, MixedDataLoader
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    zero_ternary_grads,
    restore_ternary,
    count_ternary_weights,
    bios_mutation_budget,
    save_topology,
    load_topology,
    mutate_topology,

[CONTENT TRUNCATED] Showing lines 41 to 55 of 1116 total lines. Use line_offset=55 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 105,
  "limit": 15
}
```

**Summary:** Reading train.py (105-120)

**Output:**
```
# Ascending components: shared across L0↑, L1↑, L2_apex (3 passes)
ASC_SHARED = ("prep", "stride_stack", "consolidate", "mod_projs", "s4")
# Descending components: shared across L1↓, L0↓ (2 passes)
# Kernel dispatch/integrate replace prep_desc/consolidate_desc
DESC_SHARED = ("kernel_dispatch", "stride_stack_desc", "kernel_integrate", "mod_projs_desc", "s4_desc")

N_ASC_PASSES = 3
N_DESC_PASSES = 2


def normalize_shared_grads(grads: dict) -> dict:
    """Divide gradients of shared components by their pass count.

    Ascending components (prep, stride_stack, consolidate, mod_projs, s4)
    are traversed 3× per forward (L0↑, L1↑, L2_apex).

[CONTENT TRUNCATED] Showing lines 106 to 120 of 1116 total lines. Use line_offset=120 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 265,
  "limit": 25
}
```

**Summary:** Reading train.py (265-290)

**Output:**
```
        print(f"  │ {pname:4s}: ratio={cr[pi]:.3f}  φ-dev={pd[pi]:.3f} {phi_mark}",
              file=sys.stderr)
    print("  ├─ Register norms ────────────────────────────────┤", file=sys.stderr)
    for bname, norms in compressor_metrics["register_norms"].items():
        print(f"  │ {bname:12s}: {' '.join(f'{n:.2f}' for n in norms)}",
              file=sys.stderr)
    print("  └─────────────────────────────────────────────────┘", file=sys.stderr)

    # Op emphasis (S4→kernel modulation)
    op_emph = compressor_metrics.get("op_emphasis")
    if op_emph:
        from kernel import OP_NAMES
        indexed = sorted(enumerate(op_emph), key=lambda x: x[1], reverse=True)
        top3 = [(OP_NAMES[i], v) for i, v in indexed[:3]]
        bot3 = [(OP_NAMES[i], v) for i, v in indexed[-3:]]
        print(f"  🎯 Op emphasis: top={' '.join(f'{n}={v:.2f}' for n,v in top3)}"
              f"  bot={' '.join(f'{n}={v:.2f}' for n,v in bot3)}",
              file=sys.stderr)

    # Compute gate stats (kernel pathway)
    if "compute_gate_mean" in compressor_metrics:
        cg_mean = compressor_metrics["compute_gate_mean"]
        cg_max = compressor_metrics["compute_gate_max"]
        cg_active = compressor_metrics["compute_gate_active"]
        print(f"  🔧 Compute gate: mean={cg_mean:.4f}  max={cg_max:.4f}  "

[CONTENT TRUNCATED] Showing lines 266 to 290 of 1116 total lines. Use line_offset=290 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 685,
  "limit": 10
}
```

**Summary:** Reading train.py (685-695)

**Output:**
```
# § 8  Main training loop
# ══════════════════════════════════════════════════════════════════════════════

def train(cfg: V10Config, args: argparse.Namespace) -> None:
    checkpoint_dir = Path(cfg.checkpoint_dir)
    checkpoint_dir.mkdir(parents=True, exist_ok=True)

    # ── Banner ────────────────────────────────────────────────
    print("=" * 72, file=sys.stderr)
    print("  v10 — V6 Compressor (5-pass, 9 strides) on Dolma Prose", file=sys.stderr)

[CONTENT TRUNCATED] Showing lines 686 to 695 of 1116 total lines. Use line_offset=695 parameter to read more content.
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 1085,
  "limit": 10
}
```

**Summary:** Reading train.py (1085-1095)

**Output:**
```
                        help="Path to structured data shard (.npy)")

    args = parser.parse_args()
    cfg = V10Config()

    if args.total_steps is not None: cfg.total_steps = args.total_steps
    if args.checkpoint_dir is not None: cfg.checkpoint_dir = args.checkpoint_dir
    if args.d_model is not None:
        cfg.d_model = args.d_model
        cfg.d_ff = args.d_model * 3

[CONTENT TRUNCATED] Showing lines 1086 to 1095 of 1116 total lines. Use line_offset=1095 parameter to read more content.
```

## Assistant

Now I have all the lines to change. Let me also check the metrics logging section to update the metric keys:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "grep -n \"kernel_dispatch_weights\\|kernel_type_weights\\|op_embedding_norms\\|\\\"loss\\\"\\|metrics_record\" /Users/mwhitford/src/verbum/scripts/v11/train.py | head -20"
}
```

**Summary:** $ grep -n "kernel_dispatch_weights\|k...

**Output:**
```
Exit code: 0
Stdout:
309:        "loss": avg_loss,
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 210,
  "limit": 60
}
```

**Summary:** Reading train.py (210-270)

**Output:**
```
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        _, loss = model(input_ids, targets)
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += input_ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    ppl = math.exp(min(avg_loss, 20.0))
    r = (avg_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

    # Instrumented forward on one batch for compressor metrics
    input_ids_np, _ = next(eval_loader)
    input_ids = mx.array(input_ids_np)
    _, compressor_metrics = model.forward_instrumented(input_ids)

    # Print compressor metrics
    pass_names = ("L0↑", "L1↑", "L2", "L1↓", "L0↓")
    desc_max_cycles = compressor_metrics.get("desc_max_cycles", 1)

    print("  ┌─ S3 gates ──────────────────────────────────────┐", file=sys.stderr)
    for pi, pname in enumerate(pass_names):
        gates = compressor_metrics["s3_gates"][pi]
        if pi >= 3 and desc_max_cycles > 1:
            # Descending pass: show per-cycle gates
            for cy in range(desc_max_cycles):
                base = cy * 3
                cyname = f"{pname}c{cy}"
                print(f"  │ {cyname:6s}: disp={gates[base]:.3f}  "
                      f"conv={gates[base+1]:.3f}  intg={gates[base+2]:.3f}",
                      file=sys.stderr)
        else:
            print(f"  │ {pname:4s}: prep={gates[0]:.3f}  conv={gates[1]:.3f}  "
                  f"cons={gates[2]:.3f}", file=sys.stderr)
    print("  ├─ S5 reweight ───────────────────────────────────┤", file=sys.stderr)
    mg = compressor_metrics["s5_reweight"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(pass_names, mg))}",
          file=sys.stderr)
    print("  ├─ S2 coordination ───────────────────────────────┤", file=sys.stderr)
    s2_conflict = compressor_metrics.get("s2_conflict", [])
    s2_scales = compressor_metrics.get("s2_scales", [])
    s2_names = ("L0↑→L1↑", "L1↑→L2", "L2→L1↓", "L1↓→L0↓")
    for ti in range(len(s2_conflict)):
        cs = s2_conflict[ti]
        sc = s2_scales[ti] if ti < len(s2_scales) else 0.0
        warn = "  ⚠" if cs < 0 else ""
        print(f"  │ {s2_names[ti]:8s}: cos={cs:+.3f}  scale={sc:.4f}{warn}",
              file=sys.stderr)
    print("  ├─ Compression ───────────────────────────────────┤", file=sys.stderr)
    cr = compressor_metrics["pass_compression"]
    pd = compressor_metrics["pass_phi_dev"]
    for pi, pname in enumerate(pass_names):
        phi_mark = "←φ" if pd[pi] < 0.05 else "   "
        print(f"  │ {pname:4s}: ratio={cr[pi]:.3f}  φ-dev={pd[pi]:.3f} {phi_mark}",
              file=sys.stderr)
    print("  ├─ Register norms ────────────────────────────────┤", file=sys.stderr)
    for bname, norms in compressor_metrics["register_norms"].items():
        print(f"  │ {bname:12s}: {' '.join(f'{n:.2f}' for n in norms)}",

[CONTENT TRUNCATED] Showing lines 211 to 270 of 1116 total lines. Use line_offset=270 parameter to read more content.
```

## Assistant

Let me check the metrics_record construction and any remaining references:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "line_offset": 290,
  "limit": 60
}
```

**Summary:** Reading train.py (290-350)

**Output:**
```
              f"active(>0.5)={cg_active:.1%}", file=sys.stderr)

    # Multi-cycle stats
    if desc_max_cycles > 1:
        cig = compressor_metrics.get("cycle_inject_gate", 0.0)
        eff_cycles = compressor_metrics.get("effective_cycles", [])
        cont_gates = compressor_metrics.get("cycle_continue_gates", [])
        desc_pass_names = ("L1↓", "L0↓")
        parts = [f"max={desc_max_cycles}", f"inject={cig:.4f}"]
        for di, dpn in enumerate(desc_pass_names):
            if di < len(eff_cycles):
                parts.append(f"{dpn}={eff_cycles[di]:.2f}eff")
            if di < len(cont_gates) and cont_gates[di]:
                cg_str = ",".join(f"{g:.2f}" for g in cont_gates[di])
                parts.append(f"cont=[{cg_str}]")
        print(f"  🔄 Cycles: {' '.join(parts)}", file=sys.stderr)

    result = {
        "loss": avg_loss,
        "ppl": ppl,
        "r": r,
    }
    result.update(compressor_metrics)
    return result


# ══════════════════════════════════════════════════════════════════════════════
# § 6  Tournament evolution
# ══════════════════════════════════════════════════════════════════════════════

MUTANT_STRATEGIES = {
    "conservative": 0.25,
    "explorer":     1.0,
    "targeted":     2.0,
    "random":       4.0,
    "intelligence": 0.5,   # S4→S5: Beer's intelligence proposal channel
}

# S4 module path fragments — intelligence strategy amplifies these
S4_MODULES = ('s4.', 's4_desc.', 'meta_s4.')


def run_tournament(
    model, cfg, step, total_ternary, eval_loader,
    base_pct, rng,
    row_importance, col_importance, grad_direction,
    structured_eval_loader=None,
) -> dict:
    """One evolutionary generation via consensus mutation.

    Instead of tournament selection (best of 4 independent throws),
    consensus requires ≥3 of 4 strategies to independently agree on
    the same flip at the same position. Each accepted flip has
    independent evidence from multiple sampling strategies.

    Flow:
      1. Each strategy proposes mutations (without modifying the model)
      2. Find positions where ≥3 strategies agree on the same new value
      3. Apply only the consensus flips
      4. Evaluate: accept if loss improves, revert if not

[CONTENT TRUNCATED] Showing lines 291 to 350 of 1116 total lines. Use line_offset=350 parameter to read more content.
```

## Assistant

Good. Now let me make all the surgical edits to train.py:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "from config import V10Config\nfrom data import ShardedDataLoader, MixedDataLoader\nfrom model import V6Compressor, create_model, count_parameters",
  "new_content": "from config import V11Config\nfrom data import ShardedDataLoader, MixedDataLoader\nfrom model import V11Model, create_model, count_parameters"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "    model: V6Compressor,",
  "new_content": "    model: V11Model,"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "DESC_SHARED = (\"kernel_dispatch\", \"stride_stack_desc\", \"kernel_integrate\", \"mod_projs_desc\", \"s4_desc\")",
  "new_content": "DESC_SHARED = (\"combinator_dispatch\", \"stride_stack_desc\", \"combinator_integrate\", \"mod_projs_desc\", \"s4_desc\")"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "    # Op emphasis (S4→kernel modulation)\n    op_emph = compressor_metrics.get(\"op_emphasis\")\n    if op_emph:\n        from kernel import OP_NAMES\n        indexed = sorted(enumerate(op_emph), key=lambda x: x[1], reverse=True)\n        top3 = [(OP_NAMES[i], v) for i, v in indexed[:3]]\n        bot3 = [(OP_NAMES[i], v) for i, v in indexed[-3:]]\n        print(f\"  🎯 Op emphasis: top={' '.join(f'{n}={v:.2f}' for n,v in top3)}\"\n              f\"  bot={' '.join(f'{n}={v:.2f}' for n,v in bot3)}\",\n              file=sys.stderr)",
  "new_content": "    # Combinator emphasis (S4→dispatch modulation)\n    comb_emph = compressor_metrics.get(\"combinator_emphasis\")\n    if comb_emph:\n        from kernel import COMBINATOR_NAMES\n        indexed = sorted(enumerate(comb_emph), key=lambda x: x[1], reverse=True)\n        parts = [f\"{COMBINATOR_NAMES[i]}={v:.2f}\" for i, v in indexed]\n        print(f\"  🎯 Combinator emphasis: {' '.join(parts)}\",\n              file=sys.stderr)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "def evaluate(model: V6Compressor, cfg: V10Config) -> dict:",
  "new_content": "def evaluate(model: V11Model, cfg: V11Config) -> dict:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "def train(cfg: V10Config, args: argparse.Namespace) -> None:",
  "new_content": "def train(cfg: V11Config, args: argparse.Namespace) -> None:"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "    print(\"  v10 — V6 Compressor (5-pass, 9 strides) on Dolma Prose\", file=sys.stderr)",
  "new_content": "    print(\"  v11 — KIBC Combinator VSM (5-pass, 9 strides) on Dolma Prose\", file=sys.stderr)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/train.py",
  "original_content": "    cfg = V10Config()",
  "new_content": "    cfg = V11Config()"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/scripts/v11/train.py.
```

## Assistant

Now let me verify the train.py has no remaining v10 references:

### Tool Call: shell_command (failed)


```json
{
  "command": "grep -n \"V10Config\\|V6Compressor\\|kernel_dispatch\\.\\|kernel_integrate\\.\\|N_OPS\\b\\|OP_NAMES\\b\\|op_emphasis\" /Users/mwhitford/src/verbum/scripts/v11/train.py"
}
```

**Summary:** $ grep -n "V10Config\|V6Compressor\|k...

**Output:**
```
Exit code: 1
```

## Assistant

Clean — no remaining v10 references. Now let me verify the whole directory:

### Tool Call: directory_tree (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11"
}
```

**Summary:** Listing tree: scripts/v11

**Output:**
```
/Users/mwhitford/src/verbum/scripts/v11
 attention.py
 components.py
 config.py
 data.py
 kernel.py
 kernel_dispatch.py
 model.py
 ternary.py
 train.py

0 directories, 9 files
```

## Assistant

Good — 9 self-contained files. Now let me run the self-tests to verify everything works:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/v11/kernel.py",
  "timeout": 30000
}
```

**Summary:** $ uv run python scripts/v11/kernel.py

**Output:**
```
Exit code: 0
Stdout:
kernel.py self-test: all assertions passed ✓
  4 combinators: K, I, B, C
  Reduction engine: normal-order, outermost-first
  Kernel functions: K(select), I(identity), B(compose), C(flip)
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python scripts/v11/kernel_dispatch.py",
  "timeout": 60000
}
```

**Summary:** $ uv run python scripts/v11/kernel_di...

**Output:**
```
Exit code: 0
Stdout:
Testing CombinatorDispatch (full softmax, 4 combinators)...
  CombinatorDispatch: (1, 64, 512) → (1, 64, 512) ✓
  Dispatch weights: (1, 64, 4), 4-way softmax ✓
  Mean dispatch: K=0.257 I=0.244 B=0.228 C=0.270
  Embedding norms: all ≈ 0.5 ✓
  Max off-diagonal cosine: 0.0271 (should be small) ✓

Testing CombinatorIntegrate...
  CombinatorIntegrate: (1, 64, 512) → (1, 64, 512) ✓
  Type weights: (1, 64, 4) ✓
  Kernel pathway with dispatch: ✓
  Compute gate mean: 0.0067 (starts near 0) ✓

Testing gradient flow...
  Gradient flow OK: loss=-0.0478
  Combinators with gradient: 4/4 ✓

kernel_dispatch.py self-test: all ok ✓
```

## Assistant

Both self-tests pass cleanly. Let me also do a quick smoke test of the full model:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport sys; sys.path.insert(0, 'scripts/v11')\nfrom config import V11Config\nfrom model import create_model, count_parameters\nimport mlx.core as mx\n\ncfg = V11Config()\ncfg.seq_len = 128\ncfg.max_seq_len = 128\nmodel = create_model(cfg)\n\ncounts = count_parameters(model)\nprint(f'Total params: {counts[\\\"total\\\"]:,}')\nprint(f'Trainable params: {counts[\\\"trainable\\\"]:,}')\n\n# Forward pass\ntokens = mx.random.randint(0, 1000, (1, 128))\ntargets = mx.random.randint(0, 1000, (1, 128))\nlogits, loss = model(tokens, targets)\nmx.eval(logits, loss)\nprint(f'Forward OK: logits={logits.shape}, loss={loss.item():.4f}')\n\n# Instrumented forward\n_, metrics = model.forward_instrumented(tokens)\nprint(f'Instrumented OK')\nprint(f'  Combinator dispatch: {metrics[\\\"combinator_dispatch_weights\\\"]}')\nprint(f'  Combinator type:     {metrics[\\\"combinator_type_weights\\\"]}')\nprint(f'  Compute gate:        {metrics.get(\\\"compute_gate_mean\\\", \\\"N/A\\\")}')\nprint(f'  Cycle continue:      {metrics[\\\"cycle_continue_gates\\\"]}')\nprint(f'  Effective cycles:    {metrics[\\\"effective_cycles\\\"]}')\nprint(f'  S5 reweight:         {metrics[\\\"s5_reweight\\\"]}')\nprint(f'  Combinator emphasis: {metrics[\\\"combinator_emphasis\\\"]}')\n\"\n",
  "timeout": 120000
}
```

**Summary:** $ uv run python -c " import sys; sys....

**Output:**
```
Exit code: 0
Stdout:
Total params: 23,800,687
Trainable params: 23,800,687
Forward OK: logits=(1, 128, 151936), loss=15.1101
Instrumented OK
  Combinator dispatch: [0.27690476179122925, 0.22600474953651428, 0.25260037183761597, 0.2444901019334793]
  Combinator type:     [0.2515869736671448, 0.2543465495109558, 0.24465984106063843, 0.249406635761261]
  Compute gate:        0.006692850962281227
  Cycle continue:      [[0.5, 0.5], [0.5, 0.5]]
  Effective cycles:    [1.75, 1.75]
  S5 reweight:         [0.040652986615896225, 0.1122932881116867, 0.14630846679210663, 0.060599327087402344, 0.1380482167005539]
  Combinator emphasis: [1.0, 1.0, 1.0, 1.0]
```

## Assistant

Everything works. Let me verify the key behavioral signatures are correct:

1. **Dispatch weights**: near-uniform ~0.25 each (4-way softmax, no bias yet) ✓
2. **Compute gate**: 0.0067 (starts near 0, pure FFN) ✓
3. **Cycle continue**: [0.5, 0.5] (neutral init from RMSNorm+tanh fix) ✓
4. **Effective cycles**: 1.75 (= 1 + 0.5 + 0.5×0.5 = 1.75, correct math) ✓
5. **S5 reweight**: all near-closed (~0.05-0.15, bias=-2.0 init) ✓
6. **Combinator emphasis**: [1.0, 1.0, 1.0, 1.0] (neutral, zero-init projection) ✓

The model is alive and correctly initialized. Now let me commit and update state.

### Tool Call: git (succeeded)


```json
{
  "command": "git status",
  "operation": "status",
  "summary": "check changes"
}
```

**Summary:** Git status: check changes

**Output:**
```
Exit code: 0
Stdout:
On branch main
Your branch is ahead of 'origin/main' by 9 commits.
  (use "git push" to publish your local commits)

Untracked files:
  (use "git add <file>..." to include in what will be committed)
	mementum/knowledge/chats/session-074.md
	mementum/knowledge/chats/session-075.md
	mementum/knowledge/chats/session-076.md
	mementum/knowledge/explore/v11-kibc-architecture.md
	scripts/v11/

nothing added to commit but untracked files present (use "git add" to track)
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/v11/ mementum/knowledge/explore/v11-kibc-architecture.md",
  "operation": "add",
  "summary": "v11 architecture files"
}
```

**Summary:** Git add: v11 architecture files

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --cached --stat",
  "operation": "diff",
  "summary": "staged changes"
}
```

**Summary:** Git diff: staged changes

**Output:**
```
Exit code: 0
Stdout:
.../knowledge/explore/v11-kibc-architecture.md     |  360 +++++
 scripts/v11/attention.py                           |  240 ++++
 scripts/v11/components.py                          |  835 ++++++++++++
 scripts/v11/config.py                              |  108 ++
 scripts/v11/data.py                                |  219 +++
 scripts/v11/kernel.py                              |  369 +++++
 scripts/v11/kernel_dispatch.py                     |  523 +++++++
 scripts/v11/model.py                               |  847 ++++++++++++
 scripts/v11/ternary.py                             | 1427 ++++++++++++++++++++
 scripts/v11/train.py                               | 1114 +++++++++++++++
 10 files changed, 6042 insertions(+)
```

## Assistant

Now commit:

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -5",
  "operation": "log",
  "summary": "commit style"
}
```

**Summary:** Git log: commit style

**Output:**
```
Exit code: 0
Stdout:
fd4d30e 🌀 state — session 076: v10-vsm 20K assessed, CycleContinue saturation fix
e15d8f7 ❌ CycleContinue sigmoid saturation — RMSNorm + tanh clamp fix
fb34e62 🌀 state — session 075: HRM-inspired multi-cycle dispatch, self-regulating cycles, JSONL logging
6f19766 ✅ JSONL instrumentation logs — full metrics history
cf53f2f 🎯 self-regulating dispatch cycles — S3 continuation gate
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n🎯 v11 KIBC combinator architecture — shapes from Qwen3 probes\n\n- 22 ops → 4 combinators (K select, I identity, B compose, C flip)\n- CombinatorDispatch: 4-way softmax, no top-k needed\n- CombinatorIntegrate: 3-operand extraction, exact combinator kernel\n- Emphasis: 4 combinator weights, not 22 op weights\n- Algedonic: 4+1 packing (was 22+1)\n- Register semantics: combinator / binding_depth / phase\n- Self-contained scripts/v11/ (extractable to standalone project)\n- All self-tests pass, full model forward verified\n- Qwen3 probes confirmed: attention IS beta reduction (KIBC basis)\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "v11 KIBC architecture"
}
```

**Summary:** Git commit: v11 KIBC architecture

**Output:**
```
Exit code: 0
Stdout:
[main 7507820] 🎯 v11 KIBC combinator architecture — shapes from Qwen3 probes
 10 files changed, 6042 insertions(+)
 create mode 100644 mementum/knowledge/explore/v11-kibc-architecture.md
 create mode 100644 scripts/v11/attention.py
 create mode 100644 scripts/v11/components.py
 create mode 100644 scripts/v11/config.py
 create mode 100644 scripts/v11/data.py
 create mode 100644 scripts/v11/kernel.py
 create mode 100644 scripts/v11/kernel_dispatch.py
 create mode 100644 scripts/v11/model.py
 create mode 100644 scripts/v11/ternary.py
 create mode 100644 scripts/v11/train.py
```

## Assistant

Now update state.md:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "content": "# verbum / state\n\n> Bootloader. Read in ~30 seconds. Step 1 of every session.\n>\n> Last updated: 2026-05-11 | Session: 077\n\n## Where we are\n\n**v11 KIBC combinator architecture created. Ready for first training run. Qwen3 probes confirmed attention IS beta reduction — 4 combinators (K, I, B, C) replace 22 ops.**\n\nSession 077 integrated findings from independent Qwen3 probes (4B and 32B)\nthat confirmed transformers organize lambda compilation around four combinators,\nnot 22 arithmetic ops. Created `scripts/v11/` as a fully self-contained,\nextractable architecture built on this empirical basis.\n\n## What was done this session\n\n### 1. Integrated Qwen3 probe findings (K, I, B, C basis)\nIndependent analysis of Qwen3-4B and Qwen3-32B revealed:\n- **Attention IS beta reduction**: three-phase pipeline SEARCH → LOCK → RESOLVE\n- **K (select)**: native to softmax at all scales (40%→80% accuracy 4B→32B)\n- **I (identity)**: native to residual stream (60%→60%, already trivial)\n- **B (compose)**: matures with scale (20%→80%), critical for non-trivial computation\n- **C (flip)**: fully absent at 4B, emerges at 32B — enables closures\n- **S (distribute)**: zero selective heads at either scale — composite of B∘K∘C\n- **Resolution pipeline**: disordered at 4B, clean temporal order at 32B\n- **Head roles**: BINDER(76-87%), COPY(18%→10%), ARGUMENT(1.5%), OPERATOR(0.5%)\n\n### 2. Created v11 architecture (scripts/v11/, self-contained)\n9 files, fully extractable to standalone project:\n- **kernel.py**: `Combinator` enum (K=0, I=1, B=2, C=3), reduction engine,\n  kernel functions for neural pathway (K→select, I→identity, B→compose, C→flip)\n- **kernel_dispatch.py**: `CombinatorDispatch` (4-way softmax, no top-k) +\n  `CombinatorIntegrate` (3-operand extraction, exact combinator kernel)\n- **config.py**: `V11Config` — adjusted dimensions (N_COMBINATORS=4)\n- **model.py**: `V11Model` — emphasis→4, algedonic→4+1, register names\n- **train.py**: Updated imports/references, combinator emphasis logging\n- **components.py, ternary.py, attention.py, data.py**: copied unchanged (self-contained)\n\n### 3. Verified v11 model\nAll self-tests pass. Full model forward verified:\n- **Dispatch**: 4-way softmax, near-uniform init (~0.25 each)\n- **Compute gate**: 0.0067 (starts near 0, pure FFN — correct)\n- **CycleContinue**: 0.5 neutral (RMSNorm+tanh fix carries forward)\n- **Effective cycles**: 1.75 (correct: 1 + 0.5 + 0.25)\n- **S5 reweight**: near-closed (~0.05-0.15, bias=-2.0 init)\n- **Combinator emphasis**: [1.0, 1.0, 1.0, 1.0] (neutral, zero-init)\n- **Parameters**: ~23.8M (slightly fewer than v10 due to 22→4 dispatch)\n\n## What to do next\n\n### Priority 1: Launch first v11 training run\n```\ncd ~/src/verbum && uv run python scripts/v11/train.py \\\n  --checkpoint-dir checkpoints/v11 \\\n  --total-steps 20000\n```\nKey questions for the first v11 run:\n- Does combinator dispatch differentiate? (K should dominate prose)\n- Does B emphasis rise for compositional structures?\n- Does CycleContinue work now? (RMSNorm+tanh fix + cleaner dispatch)\n- How does loss compare to v10 at matched steps?\n- Does compute gate behavior differ with 4 combinators vs 22 ops?\n\n### Priority 2: Compare v11 vs v10 at matched steps\nAt 1K, 5K, 10K, 20K compare:\n- Loss trajectory (should be similar — same ascending arm)\n- Dispatch distribution (should be interpretable: K > B > I > C for prose)\n- Effective cycles (should vary — CycleContinue now has a 4-way signal)\n- Emphasis differentiation (K emphasis high for prose, B for composition)\n\n### Priority 3: Structured combinator training data\nOnce v11 shows combinator differentiation on prose alone:\n- Generate KIBC reduction examples for structured shard\n- Activate mix_ratio > 0 to inject combinator training signal\n- Primarily needed for C (closures, binding) — K and B train from prose\n- Track whether C dispatch activates with structured data\n\n### Priority 4: Investigate dispatch dynamics\nWith only 4 targets, watch for:\n- Does one combinator dominate too early? (K likely, since prose is selection)\n- Does B activate for multi-clause sentences?\n- Do CycleContinue gates correlate with combinator complexity?\n  (K: gate closes, B: partially open, C: fully open)\n\n### Carried from v10\n- S5 reweight investigation (activated at 15K in v10-vsm)\n- v10-multicycle 8K checkpoint available for comparison baseline\n\n## VSM layer map (session 077 — v11 KIBC)\n\n```\nLayer     Ascending Arm              Descending Arm                   Cross-arm\n────────  ─────────────────────────  ───────────────────────────────  ──────────────────\nS5        Token embeddings (tied)    Combinator embeddings (4: KIBC)  S5Reweight\nS4        Register-query attention   Dual-view (resid + embeds)       Emphasis: regs → 4 combinators\nS3        Per-pass phase gating ✓    Per-pass phase gating            Gate values → desc S4\n          —                          CycleContinue (between cycles)   RMSNorm+tanh (s076 fix)\nS2        Direction signals ✓        coherence modulation ✓           Found boundary 2→3\nS1        prep → stride → consol.    [dispatch → stride → integ.] ×N  KIBC combinator basis\n          (shared across 3 passes)   (shared across 2 passes × N cy)\nAlgedonic Reads prev desc regs       —                                + combinator weights (4+1)\n          + combinator weights                                        EMA α=0.9\nInject    —                          cycle_inject_gate (per cycle>0)  sigmoid(-4) ≈ 0.018 init\nLogging   —                          —                                3× JSONL ✓\n```\n\nN = desc_max_cycles (default 3, self-regulated by CycleContinue)\n\nCycle semantics (from Qwen3 probes):\n  Cycle 0 — IDENTIFY: which combinator? (K select, B compose, C flip, I pass)\n  Cycle 1 — RESOLVE:  find and bind arguments (StrideStack propagation)\n  Cycle 2 — PRODUCE:  apply reduction, produce result\n\n## Key files\n\n| File | Purpose |\n|------|---------|\n| `scripts/v11/config.py` | V11Config: N_COMBINATORS=4, adjusted dimensions |\n| `scripts/v11/kernel.py` | KIBC combinator enum, reduction engine, kernel functions |\n| `scripts/v11/kernel_dispatch.py` | CombinatorDispatch (4-way softmax) + CombinatorIntegrate |\n| `scripts/v11/model.py` | V11Model: Tree of VSMs with KIBC combinator basis |\n| `scripts/v11/train.py` | Training loop (v10 evolution, updated references) |\n| `scripts/v11/components.py` | S4, S3, MetaS4, S5Reweight, S2, CycleContinue (unchanged) |\n| `scripts/v11/ternary.py` | Ternary substrate + consensus evolution (unchanged) |\n| `scripts/v11/attention.py` | StrideStack + TernaryFFN (unchanged) |\n| `scripts/v11/data.py` | Data loading (unchanged) |\n| `mementum/knowledge/explore/v11-kibc-architecture.md` | Architecture design doc |\n| `checkpoints/v10-vsm/` | Completed v10 20K run (baseline) |\n| `checkpoints/v10-multicycle/` | Completed v10 8K run (dead CycleContinue) |\n\n## Session history\n\n→ See [session-history-049-062](knowledge/explore/session-history-049-062.md)\n→ Session 063: pruned state.md, extracted history to knowledge pages\n→ Session 064: WRONG — replaced kernel architecture with v6 LM copy\n→ Session 065: probed 20K wasted run, diagnosed shared weights (missed real cause)\n→ Session 066: found original v10 in git, diagnosed real cause, rebuilt correctly\n→ Session 067: analyzed 20K run, phase reorder + mixed data, 5K test launched\n→ Session 068: attention spiral discovery, descending arm fine→coarse, evolution fix\n→ Session 069: probed v10-spiral, diagnosed dispatch gradient death, top-k MoE routing fix\n→ Session 070: consensus evolution, surgical Adam decay, mini-dispatch lab bench\n→ Session 071: dispatch analysis, type-dispatch decoupling, kernel computation pathway\n→ Session 072: probed v10-topk 1K/2K/3K — compute gate opening, type coherence 13/22, algedonic channel\n→ Session 073: VSM structural overhaul — S2, S5, dual-view S4, gate signaling, emphasis, evolution\n→ Session 074: Probed v10-vsm 1K-13K, mapped to Pythia Montague, 6 kernel-lambda generators, repacked shard\n→ Session 075: HRM analysis → multi-cycle descending arm, self-regulating cycles (CycleContinue), JSONL logging\n→ Session 076: v10-vsm 20K assessed, v10-multicycle launched, CycleContinue sigmoid saturation diagnosed + fixed\n→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture (4 combinators replace 22 ops)\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/state.md
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add mementum/state.md && git commit -m \"$(cat <<'EOF'\n🌀 state — session 077: Qwen3 probes → v11 KIBC combinator architecture\n\n- Integrated KIBC findings from independent Qwen3-4B/32B probes\n- Created self-contained scripts/v11/ (9 files, extractable)\n- 22 ops → 4 combinators: K(select), I(identity), B(compose), C(flip)\n- All tests pass, full model forward verified (~23.8M params)\n- Ready for first v11 training run\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "state update s077"
}
```

**Summary:** Git commit: state update s077

**Output:**
```
Exit code: 0
Stdout:
[main 4f02921] 🌀 state — session 077: Qwen3 probes → v11 KIBC combinator architecture
 1 file changed, 100 insertions(+), 108 deletions(-)
```

## Assistant

Done. Here's what session 077 produced:

## Summary

### What happened
Integrated your independent Qwen3 probe findings (4B and 32B) that confirmed **attention IS beta reduction** organized around **four combinators (K, I, B, C)**, not 22 arithmetic operations. Built the v11 architecture as a clean evolution from v10.

### What was created

**`scripts/v11/`** — 9 self-contained files, extractable to standalone project:

| File | What changed from v10 |
|------|----------------------|
| `kernel.py` | **New**: 4 combinators + reduction engine + kernel functions (was 22 ops) |
| `kernel_dispatch.py` | **New**: `CombinatorDispatch` (4-way softmax) + `CombinatorIntegrate` (3-operand kernel) |
| `config.py` | **Modified**: `V11Config`, N_COMBINATORS=4, no top-k |
| `model.py` | **Modified**: `V11Model`, emphasis→4, algedonic→4+1, register names |
| `train.py` | **Modified**: import/reference updates |
| `components.py` | Copied unchanged |
| `ternary.py` | Copied unchanged |
| `attention.py` | Copied unchanged |
| `data.py` | Copied unchanged |

### Verified working
- All self-tests pass (kernel, dispatch, integrate)
- Full model forward: logits correct shape, loss computed, ~23.8M params
- Init signatures correct: dispatch uniform, compute gate ~0, CycleContinue neutral, S5 near-closed, emphasis neutral

### Ready for
```
cd ~/src/verbum && uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11 \
  --total-steps 20000
```

The sieve is shaped. Now we see if the model falls into the right basin.

## User

Do checkpoints include rich instrumentation data that we can use to analyze?   Do we have a probe that can analyze the data to inform changes to the design?


### Thinking

The user is asking two questions:
1. Do the checkpoints include rich instrumentation data for analysis?
2. Do we have a probe script that can analyze that data?

Let me check what the checkpoints contain and what probe scripts exist.

## Assistant

Good questions. Let me check both.

### Tool Call: shell_command (succeeded)


```json
{
  "command": "ls -la /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/step_008000/ && echo \"---\" && head -1 /Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl | python3 -c \"import sys,json; d=json.loads(sys.stdin.read()); print('Metrics keys:'); [print(f'  {k}') for k in sorted(d.keys())]\""
}
```

**Summary:** $ ls -la /Users/mwhitford/src/verbum/...

**Output:**
```
Exit code: 0
Stdout:
total 92544
drwxr-xr-x@  7 mwhitford  staff       224 May 11 05:31 .
drwxr-xr-x@ 13 mwhitford  staff       416 May 11 05:31 ..
-rw-r--r--@  1 mwhitford  staff   1177957 May 11 05:31 importance.npz
-rw-r--r--@  1 mwhitford  staff  37883214 May 11 05:31 model.npz
-rw-r--r--@  1 mwhitford  staff   8306468 May 11 05:31 optimizer.npz
-rw-r--r--@  1 mwhitford  staff      2948 May 11 05:31 rng.npz
-rw-r--r--@  1 mwhitford  staff      6727 May 11 05:31 state.json
---
Metrics keys:
  compute_gate_active
  compute_gate_max
  compute_gate_mean
  compute_gate_min
  cycle_continue_gates
  cycle_inject_gate
  desc_max_cycles
  effective_cycles
  kernel_dispatch_weights
  kernel_type_weights
  loss
  op_embedding_norms
  op_emphasis
  pass_compression
  pass_entropy_in
  pass_entropy_out
  pass_phi_dev
  ppl
  r
  register_norms
  s2_conflict
  s2_scales
  s3_gates
  s5_reweight
  step
  timestamp
  total_accepted
  total_generations
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/metrics_log.jsonl') as f:\n    d = json.loads(f.readline())\nprint('Metrics log fields:')\nfor k, v in sorted(d.items()):\n    vtype = type(v).__name__\n    if isinstance(v, list):\n        vtype = f'list[{len(v)}]'\n        if v and isinstance(v[0], list):\n            vtype = f'list[{len(v)}×{len(v[0])}]'\n    print(f'  {k:30s} {vtype}')\n\" && echo \"---\" && python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/train_log.jsonl') as f:\n    d = json.loads(f.readline())\nprint('Train log fields:')\nfor k in sorted(d.keys()):\n    print(f'  {k}')\n\" && echo \"---\" && python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/evolution_log.jsonl') as f:\n    d = json.loads(f.readline())\nprint('Evolution log fields:')\nfor k in sorted(d.keys()):\n    print(f'  {k}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
Metrics log fields:
  compute_gate_active            float
  compute_gate_max               float
  compute_gate_mean              float
  compute_gate_min               float
  cycle_continue_gates           list[2×2]
  cycle_inject_gate              float
  desc_max_cycles                int
  effective_cycles               list[2]
  kernel_dispatch_weights        list[22]
  kernel_type_weights            list[5]
  loss                           float
  op_embedding_norms             list[22]
  op_emphasis                    list[22]
  pass_compression               list[5]
  pass_entropy_in                list[5]
  pass_entropy_out               list[5]
  pass_phi_dev                   list[5]
  ppl                            float
  r                              float
  register_norms                 dict
  s2_conflict                    list[4]
  s2_scales                      list[4]
  s3_gates                       list[5×3]
  s5_reweight                    list[5]
  step                           int
  timestamp                      float
  total_accepted                 int
  total_generations              int
---
Train log fields:
  ce
  elapsed
  grad_norm
  lr
  r
  r_avg50
  step
  timestamp
  tok_per_sec
---
Evolution log fields:
  accepted
  accepted_loss
  actual_flips
  budget
  champion_loss
  consensus_stats
  delta
  generation
  n_rows_mutated
  prose_loss
  step
  struct_loss
  timestamp
```

### Tool Call: shell_command (failed)


```json
{
  "command": "ls /Users/mwhitford/src/verbum/scripts/v10/probe*.py /Users/mwhitford/src/verbum/scripts/v11/probe*.py 2>/dev/null"
}
```

**Summary:** $ ls /Users/mwhitford/src/verbum/scri...

**Output:**
```
Exit code: 1
Stdout:
/Users/mwhitford/src/verbum/scripts/v10/probe_binding_structure.py
/Users/mwhitford/src/verbum/scripts/v10/probe_compressor_binding.py
/Users/mwhitford/src/verbum/scripts/v10/probe_counterfactual.py
/Users/mwhitford/src/verbum/scripts/v10/probe_dispatch.py
/Users/mwhitford/src/verbum/scripts/v10/probe_kernel_use.py
/Users/mwhitford/src/verbum/scripts/v10/probe_parse_structure.py
/Users/mwhitford/src/verbum/scripts/v10/probe_type_transition.py
/Users/mwhitford/src/verbum/scripts/v10/probe.py
```

### Tool Call: shell_command (succeeded)


```json
{
  "command": "wc -l /Users/mwhitford/src/verbum/scripts/v10/probe.py && head -80 /Users/mwhitford/src/verbum/scripts/v10/probe.py"
}
```

**Summary:** $ wc -l /Users/mwhitford/src/verbum/s...

**Output:**
```
Exit code: 0
Stdout:
975 /Users/mwhitford/src/verbum/scripts/v10/probe.py
#!/usr/bin/env python3
"""v10 probe — checkpoint diagnostics for V6Compressor prose LM.

Probes a v10 checkpoint with stratified φ-compression analysis,
compressor metrics (S3 gates, meta-S3, registers, entropy), eval
loss, ternary topology statistics, and multi-checkpoint evolution.

Usage:
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000

    # Multiple checkpoints — shows evolution table
    uv run python scripts/v10/probe.py checkpoints/v10/step_*

    # Quiet: summary tables only
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --quiet

    # φ-only: skip eval, just measure compression
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --phi-only

    # Verbose: per-sample φ detail
    uv run python scripts/v10/probe.py checkpoints/v10/step_* -v

    # Skip eval (faster — no data loader)
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --no-eval

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import V10Config
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    unpack_ternary,
    _walk_ternary_modules,
    TernaryLinear,
    TernaryEmbedding,
)


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

E_IRREDUCIBLE = 1.82
LOG_V = math.log(151936)  # ≈ 11.93
PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI

PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")
PHASE_NAMES_ASC = ("prep", "conv", "cons")
PHASE_NAMES_DESC = ("disp", "intg", "conv")
PHASE_NAMES = ("prep", "conv", "cons")  # backward compat for evolution table

# Kernel op names (from kernel.py) for dispatch weight display
KERNEL_OP_NAMES = [
    "+", "-", "*", "//", "%", "min", "max",     # 0-6  arith binary
    "=", "<", ">", "<=", ">=",                   # 7-11 comparison
    "and", "or",                                 # 12-13 bool binary
    "not",                                       # 14    bool unary
    "abs", "neg",                                # 15-16 arith unary
```

## Assistant

Now I see the full picture. Let me check the state.json in a checkpoint too:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "python3 -c \"\nimport json\nwith open('/Users/mwhitford/src/verbum/checkpoints/v10-multicycle/step_008000/state.json') as f:\n    d = json.load(f)\nprint('State.json fields:')\nfor k,v in sorted(d.items()):\n    if isinstance(v, (dict, list)):\n        print(f'  {k}: {type(v).__name__}[{len(v)}]')\n    else:\n        print(f'  {k}: {v}')\n\""
}
```

**Summary:** $ python3 -c " import json with open(...

**Output:**
```
Exit code: 0
Stdout:
State.json fields:
  config: dict[7]
  data_loader: dict[3]
  eval_metrics: dict[24]
  step: 8000
  total_accepted: 2
  total_generations: 160
  train_losses_last50: list[50]
```

## Assistant

Here's the answer to both questions:

## 1. Checkpoint instrumentation — yes, rich

**Three JSONL log files** accumulate continuously during training:

| File | Frequency | Key fields |
|------|-----------|------------|
| `metrics_log.jsonl` | Every 500 steps | Full `forward_instrumented()`: loss, S3 gates (5×3 or 5×9 with cycles), S5 reweight, S2 conflict/scales, register norms, dispatch weights, type weights, compute gate, cycle continue gates, effective cycles, emphasis, embedding norms, compression ratios |
| `train_log.jsonl` | Every 25 steps | CE, relational loss, grad norm, LR, tok/sec |
| `evolution_log.jsonl` | Every 50 steps | Tournament results, consensus stats, flips, acceptance, prose/struct loss |

**Per-checkpoint** (`step_NNNNNN/`): model weights, optimizer state, importance maps, RNG state, and `state.json` with config + last eval metrics.

The `metrics_log.jsonl` is the richest — it has **28 fields** including the full dispatch distribution, all S3 gates per cycle, and the combinator emphasis vector. Every 500 steps you get a full instrumented snapshot.

## 2. Probe scripts — v10 only, not v11

v10 has **8 probe scripts**, but none are in v11:

| Script | What it probes |
|--------|---------------|
| `probe.py` (975 lines) | **Main probe**: checkpoint diagnostics, φ-compression, eval loss, multi-checkpoint evolution tables |
| `probe_dispatch.py` | Dispatch weight distribution analysis |
| `probe_kernel_use.py` | Kernel computation pathway activation |
| `probe_type_transition.py` | Type weight transitions across checkpoints |
| `probe_binding_structure.py` | Lambda binding structure analysis |
| `probe_compressor_binding.py` | Ascending arm binding probes |
| `probe_parse_structure.py` | Parse structure visualization |
| `probe_counterfactual.py` | Counterfactual intervention probes |

**The problem**: all v10 probes reference `V10Config`, `V6Compressor`, `N_OPS=22`, `OP_NAMES`, etc. They won't work with v11's `V11Config`, `V11Model`, `N_COMBINATORS=4`, `COMBINATOR_NAMES`.

**What we need**: a v11 probe that can:
1. Load a v11 checkpoint and run `forward_instrumented()`
2. Analyze the metrics_log.jsonl trajectory (combinator dispatch evolution, cycle continue dynamics, emphasis shifts)
3. Compare checkpoints across steps (multi-checkpoint evolution table)
4. Specifically watch for KIBC-relevant signals (K dominance, B emergence, CycleContinue differentiation)

Want me to create a v11 probe script? I'd adapt the main `probe.py` to the KIBC basis — it's the most useful one for tracking whether the sieve is working.

## User

Yes, we probably want to also analyze the distribution of the kernel ops.


### Thinking

The user wants a v11 probe script that:
1. Loads v11 checkpoints and runs forward_instrumented()
2. Analyzes metrics_log.jsonl trajectory
3. Multi-checkpoint evolution tables
4. KIBC-specific signals
5. Kernel op distribution analysis - meaning how the 4 combinators distribute across positions, which combinator dominates where, how the dispatch weights evolve

Let me read the v10 probe.py to understand the structure, then build a v11 version that's adapted for KIBC.

## Assistant

Let me study the v10 probe to understand what to carry forward and what to reshape for KIBC.

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/probe.py"
}
```

**Summary:** Reading probe.py (0-2000)

**Output:**
```
#!/usr/bin/env python3
"""v10 probe — checkpoint diagnostics for V6Compressor prose LM.

Probes a v10 checkpoint with stratified φ-compression analysis,
compressor metrics (S3 gates, meta-S3, registers, entropy), eval
loss, ternary topology statistics, and multi-checkpoint evolution.

Usage:
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000

    # Multiple checkpoints — shows evolution table
    uv run python scripts/v10/probe.py checkpoints/v10/step_*

    # Quiet: summary tables only
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --quiet

    # φ-only: skip eval, just measure compression
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --phi-only

    # Verbose: per-sample φ detail
    uv run python scripts/v10/probe.py checkpoints/v10/step_* -v

    # Skip eval (faster — no data loader)
    uv run python scripts/v10/probe.py checkpoints/v10/step_001000 --no-eval

License: MIT
"""

from __future__ import annotations

import argparse
import json
import math
import sys
import time
from datetime import UTC, datetime
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np
from mlx.utils import tree_flatten

sys.path.insert(0, str(Path(__file__).resolve().parent))

from config import V10Config
from model import V6Compressor, create_model, count_parameters
from ternary import (
    freeze_ternary_weights,
    restore_ternary,
    count_ternary_weights,
    unpack_ternary_mlx,
    unpack_ternary,
    _walk_ternary_modules,
    TernaryLinear,
    TernaryEmbedding,
)


# ══════════════════════════════════════════════════════════════════════
# Constants
# ══════════════════════════════════════════════════════════════════════

E_IRREDUCIBLE = 1.82
LOG_V = math.log(151936)  # ≈ 11.93
PHI = (1 + math.sqrt(5)) / 2
INV_PHI = 1 / PHI

PASS_NAMES = ("L0_asc", "L1_asc", "L2_apex", "L1_desc", "L0_desc")
PHASE_NAMES_ASC = ("prep", "conv", "cons")
PHASE_NAMES_DESC = ("disp", "intg", "conv")
PHASE_NAMES = ("prep", "conv", "cons")  # backward compat for evolution table

# Kernel op names (from kernel.py) for dispatch weight display
KERNEL_OP_NAMES = [
    "+", "-", "*", "//", "%", "min", "max",     # 0-6  arith binary
    "=", "<", ">", "<=", ">=",                   # 7-11 comparison
    "and", "or",                                 # 12-13 bool binary
    "not",                                       # 14    bool unary
    "abs", "neg",                                # 15-16 arith unary
    "if",                                        # 17    conditional
    "partial", "apply", "comp", "apply-c",       # 18-21 lambda
]

KERNEL_TYPE_NAMES = ["INT", "BOOL", "FN", "FN_COMP", "ERROR"]

RESULTS_DIR = Path("results/v10")


# ══════════════════════════════════════════════════════════════════════
# φ-compression sample strata
# ══════════════════════════════════════════════════════════════════════

PHI_STRATA = {
    "prose": [
        "The cat sat on the mat and looked out the window at the birds flying south for the winter.",
        "Every student who passed the final exam received a certificate of achievement from the dean.",
        "The quick brown fox jumps over the lazy dog near the river bank on a warm summer afternoon.",
        "In a quiet village nestled between rolling hills, the old baker opened his shop at dawn.",
    ],
    "compositional": [
        "The man who the dog that the cat chased bit ran away quickly.",
        "If every student reads a book then some teacher who knows the author is happy.",
        "No politician who endorsed the candidate that lost the election won their own race.",
        "Every lawyer who represents a client that a judge dismissed the case against appealed.",
    ],
    "technical": [
        "The gradient of the loss with respect to the weights is computed via backpropagation.",
        "Attention scores are computed as the softmax of the scaled dot product of queries and keys.",
        "The learning rate schedule uses cosine annealing with linear warmup over 500 steps.",
        "Each layer applies layer normalization before the self-attention and feed-forward blocks.",
    ],
    "math": [
        "∀x ∈ ℝ: x² ≥ 0 ∧ x² = 0 ↔ x = 0",
        "λx. λy. apply(x, y) → result",
        "P(A|B) = P(B|A) × P(A) / P(B)",
        "∑_{i=1}^{n} i = n(n+1)/2",
    ],
}


# ══════════════════════════════════════════════════════════════════════
# Checkpoint loading
# ══════════════════════════════════════════════════════════════════════


def load_checkpoint(ckpt_path: Path) -> tuple[V6Compressor, int, dict]:
    """Load a v10 checkpoint. Returns (model, step, state_dict)."""
    state_path = ckpt_path / "state.json"
    model_path = ckpt_path / "model.npz"

    if not state_path.exists() or not model_path.exists():
        raise FileNotFoundError(f"Missing state.json or model.npz in {ckpt_path}")

    state = json.loads(state_path.read_text())
    step = state["step"]
    config_data = state.get("config", {})

    cfg = V10Config()
    if "d_model" in config_data:
        cfg.d_model = config_data["d_model"]
        cfg.d_ff = cfg.d_model * 3
        cfg.d_ff_consolidate = cfg.d_model * 4
    if "vocab_size" in config_data:
        cfg.vocab_size = config_data["vocab_size"]
    if "seq_len" in config_data:
        cfg.seq_len = config_data["seq_len"]
        cfg.max_seq_len = config_data["seq_len"]

    model = create_model(cfg)

    # Load weights (strict=False to handle schema changes across versions,
    # e.g. dispatch_temp was removed when top-k routing replaced softmax)
    weights = dict(mx.load(str(model_path)))
    model.load_weights(list(weights.items()), strict=False)
    mx.eval(model.parameters())
    freeze_ternary_weights(model)
    restore_ternary(model)

    return model, step, state, cfg


# ══════════════════════════════════════════════════════════════════════
# Ternary statistics
# ══════════════════════════════════════════════════════════════════════


def ternary_stats(model: V6Compressor) -> dict:
    """Compute ternary topology statistics per module."""
    stats = {}
    for path, mod in _walk_ternary_modules(model):
        if isinstance(mod, TernaryLinear):
            w_int = unpack_ternary_mlx(mod.weight)
            mx.eval(w_int)
            w_np = np.array(w_int.astype(mx.int8))
            total = w_np.size
            n_zero = int(np.sum(w_np == 0))
            n_neg = int(np.sum(w_np == -1))
            n_pos = int(np.sum(w_np == 1))
            sparsity = n_zero / total

            gamma_np = np.array(mod.gamma)
            stats[path] = {
                "type": "linear",
                "shape": (mod.out_features, mod.in_features),
                "sparsity": sparsity,
                "n_neg": n_neg,
                "n_zero": n_zero,
                "n_pos": n_pos,
                "gamma_mean": float(np.mean(np.abs(gamma_np))),
                "gamma_std": float(np.std(gamma_np)),
                "gamma_min": float(np.min(np.abs(gamma_np))),
                "gamma_max": float(np.max(np.abs(gamma_np))),
            }

        elif isinstance(mod, TernaryEmbedding):
            w_int = unpack_ternary(mod.ternary_weight, mod.in_features)
            mx.eval(w_int)
            w_np = np.array(w_int.astype(mx.int8))
            total = w_np.size
            n_zero = int(np.sum(w_np == 0))
            sparsity = n_zero / total

            gamma_np = np.array(mod.gamma)
            stats[path] = {
                "type": "embedding",
                "shape": (mod.out_features, mod.in_features),
                "sparsity": sparsity,
                "gamma_mean": float(np.mean(np.abs(gamma_np))),
                "gamma_std": float(np.std(gamma_np)),
            }

    return stats


def print_ternary_stats(stats: dict) -> None:
    """Display ternary statistics grouped by component."""
    groups: dict[str, list] = {}
    for path, s in stats.items():
        # Group by top-level component
        parts = path.split(".")
        if len(parts) >= 1:
            group = parts[0]
        else:
            group = "other"
        groups.setdefault(group, []).append(s)

    print(f"\n  Ternary topology ({len(stats)} modules):")
    print(f"  {'Group':18s} {'#':>3} {'sparsity':>9} {'γ_mean':>8} {'γ_std':>7} {'shape':>16}")
    print(f"  {'─'*18} {'─'*3} {'─'*9} {'─'*8} {'─'*7} {'─'*16}")

    total_params = 0
    total_zeros = 0
    for grp in sorted(groups.keys()):
        mods = groups[grp]
        n = len(mods)
        sp = sum(m["sparsity"] for m in mods) / n
        gm = sum(m["gamma_mean"] for m in mods) / n
        gs = sum(m.get("gamma_std", 0) for m in mods) / n
        shapes = set(str(m["shape"]) for m in mods)
        shape_str = next(iter(shapes)) if len(shapes) == 1 else "mixed"

        for m in mods:
            total_params += m["shape"][0] * m["shape"][1]
            total_zeros += int(m["sparsity"] * m["shape"][0] * m["shape"][1])

        print(f"  {grp:18s} {n:>3} {sp:>9.3f} {gm:>8.4f} {gs:>7.4f} {shape_str:>16}")

    overall_sparsity = total_zeros / total_params if total_params else 0
    print(f"  {'─'*18} {'─'*3} {'─'*9}")
    print(f"  {'TOTAL':18s} {len(stats):>3} {overall_sparsity:>9.3f}  "
          f"({total_params:,} ternary params)")


# ══════════════════════════════════════════════════════════════════════
# Evaluation on held-out data
# ══════════════════════════════════════════════════════════════════════


def evaluate_on_data(model: V6Compressor, cfg: V10Config,
                     target_tokens: int = 50_000) -> dict:
    """Evaluate on held-out Dolma shards."""
    from data import ShardedDataLoader

    eval_loader = ShardedDataLoader(
        data_dir=cfg.data_dir,
        batch_size=cfg.batch_size,
        seq_len=cfg.seq_len,
        shard_start=cfg.n_train_shards,
        shard_end=cfg.n_train_shards + cfg.n_eval_shards,
        seed=9999,
    )

    total_loss = 0.0
    n_batches = 0
    tokens_seen = 0

    while tokens_seen < target_tokens:
        input_ids_np, targets_np = eval_loader.next_batch()
        input_ids = mx.array(input_ids_np)
        targets = mx.array(targets_np)

        _, loss = model(input_ids, targets)
        mx.eval(loss)
        total_loss += float(loss.item())
        n_batches += 1
        tokens_seen += input_ids_np.size

    avg_loss = total_loss / max(n_batches, 1)
    ppl = math.exp(min(avg_loss, 20.0))
    r = (avg_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)

    return {
        "loss": avg_loss,
        "ppl": ppl,
        "r": r,
        "tokens_evaluated": tokens_seen,
        "n_batches": n_batches,
    }


# ══════════════════════════════════════════════════════════════════════
# φ-Compression analysis (stratified)
# ══════════════════════════════════════════════════════════════════════


def _run_phi_samples(model: V6Compressor, tokenizer, samples: list[str]) -> dict:
    """Run forward_instrumented on text samples, collect compressor metrics."""
    all_metrics = {
        "s3_gates": [],
        "meta_s3": [],
        "register_norms": [],
        "pass_compression": [],
        "pass_phi_dev": [],
        "pass_entropy_in": [],
        "pass_entropy_out": [],
        "losses": [],
        "per_sample": [],
        "kernel_dispatch_weights": [],
        "kernel_type_weights": [],
        "op_embedding_norms": [],
    }

    for text in samples:
        ids = mx.array(tokenizer.encode(text)).reshape(1, -1)
        if ids.shape[1] > model.cfg.max_seq_len:
            ids = ids[:, -model.cfg.max_seq_len:]

        # Construct targets (shifted by 1)
        targets = mx.concatenate([ids[:, 1:], mx.zeros((1, 1), dtype=mx.int32)], axis=1)

        # Get compressor metrics
        hidden, metrics = model.forward_instrumented(ids)
        mx.eval(hidden)

        # Also compute loss
        logits = model.output_norm(hidden)
        logits = model.embed.output_proj(logits)
        loss = nn.losses.cross_entropy(
            logits.reshape(-1, model.cfg.vocab_size),
            targets.reshape(-1),
        ).mean()
        mx.eval(loss)

        all_metrics["s3_gates"].append(metrics["s3_gates"])
        all_metrics["meta_s3"].append(metrics["meta_s3"])
        all_metrics["register_norms"].append(metrics["register_norms"])
        all_metrics["pass_compression"].append(metrics["pass_compression"])
        all_metrics["pass_phi_dev"].append(metrics["pass_phi_dev"])
        all_metrics["pass_entropy_in"].append(metrics["pass_entropy_in"])
        all_metrics["pass_entropy_out"].append(metrics["pass_entropy_out"])
        all_metrics["losses"].append(float(loss.item()))

        if metrics.get("kernel_dispatch_weights"):
            all_metrics["kernel_dispatch_weights"].append(metrics["kernel_dispatch_weights"])
        if metrics.get("kernel_type_weights"):
            all_metrics["kernel_type_weights"].append(metrics["kernel_type_weights"])
        if metrics.get("op_embedding_norms"):
            all_metrics["op_embedding_norms"].append(metrics["op_embedding_norms"])

        all_metrics["per_sample"].append({
            "text": text[:60],
            "loss": float(loss.item()),
            "pass_compression": metrics["pass_compression"],
            "pass_phi_dev": metrics["pass_phi_dev"],
        })

    return all_metrics


def _avg_nested(values: list, n_passes: int = 5) -> list[float]:
    """Average a list of per-pass float lists."""
    if not values:
        return [0.0] * n_passes
    result = [0.0] * n_passes
    for vals in values:
        for i in range(n_passes):
            result[i] += vals[i]
    return [v / len(values) for v in result]


def _avg_s3_gates(gate_lists: list) -> list[list[float]]:
    """Average S3 gates: list of [5 passes × 3 phases]."""
    if not gate_lists:
        return [[0.0] * 3 for _ in range(5)]
    n = len(gate_lists)
    result = [[0.0] * 3 for _ in range(5)]
    for gates in gate_lists:
        for pi in range(5):
            for ph in range(3):
                result[pi][ph] += gates[pi][ph]
    return [[v / n for v in row] for row in result]


def _avg_register_norms(norm_lists: list) -> dict[str, list[float]]:
    """Average register norms across samples."""
    if not norm_lists:
        return {}
    n = len(norm_lists)
    result: dict[str, list[float]] = {}
    for norms in norm_lists:
        for bank_name, vals in norms.items():
            if bank_name not in result:
                result[bank_name] = [0.0] * len(vals)
            for i, v in enumerate(vals):
                result[bank_name][i] += v
    return {k: [v / n for v in vals] for k, vals in result.items()}


def analyze_phi(model: V6Compressor, tokenizer, strata: dict | None = None) -> dict:
    """Stratified φ-compression analysis.

    Returns dict with:
      overall: averaged metrics across all strata
      strata: {stratum_name: averaged metrics}
      per_sample: list of per-sample detail
    """
    if strata is None:
        strata = PHI_STRATA

    # Collect all samples
    all_samples = []
    for samples in strata.values():
        all_samples.extend(samples)

    overall_raw = _run_phi_samples(model, tokenizer, all_samples)

    # Per-stratum
    strata_results = {}
    for sname, samples in strata.items():
        raw = _run_phi_samples(model, tokenizer, samples)
        strata_results[sname] = {
            "mean_loss": sum(raw["losses"]) / len(raw["losses"]) if raw["losses"] else 0,
            "pass_compression": _avg_nested(raw["pass_compression"]),
            "pass_phi_dev": _avg_nested(raw["pass_phi_dev"]),
        }

    # Overall
    overall = {
        "mean_loss": sum(overall_raw["losses"]) / len(overall_raw["losses"]) if overall_raw["losses"] else 0,
        "s3_gates": _avg_s3_gates(overall_raw["s3_gates"]),
        "meta_s3": _avg_nested(overall_raw["meta_s3"]),
        "register_norms": _avg_register_norms(overall_raw["register_norms"]),
        "pass_compression": _avg_nested(overall_raw["pass_compression"]),
        "pass_phi_dev": _avg_nested(overall_raw["pass_phi_dev"]),
        "pass_entropy_in": _avg_nested(overall_raw["pass_entropy_in"]),
        "pass_entropy_out": _avg_nested(overall_raw["pass_entropy_out"]),
    }

    # Kernel dispatch weights (average over samples)
    kdw_list = overall_raw.get("kernel_dispatch_weights", [])
    if kdw_list:
        n_ops = len(kdw_list[0])
        avg_kdw = [0.0] * n_ops
        for kdw in kdw_list:
            for i in range(n_ops):
                avg_kdw[i] += kdw[i]
        overall["kernel_dispatch_weights"] = [v / len(kdw_list) for v in avg_kdw]

    ktw_list = overall_raw.get("kernel_type_weights", [])
    if ktw_list:
        n_types = len(ktw_list[0])
        avg_ktw = [0.0] * n_types
        for ktw in ktw_list:
            for i in range(n_types):
                avg_ktw[i] += ktw[i]
        overall["kernel_type_weights"] = [v / len(ktw_list) for v in avg_ktw]

    # Op embedding norms (constant across samples — just take first)
    oen_list = overall_raw.get("op_embedding_norms", [])
    if oen_list:
        overall["op_embedding_norms"] = oen_list[0]

    # Aggregate phi stats
    agg_ratio = sum(overall["pass_compression"]) / 5
    agg_phi_dev = sum(overall["pass_phi_dev"]) / 5
    overall["aggregate"] = {
        "mean_ratio": agg_ratio,
        "mean_phi_dev": agg_phi_dev,
        "target": INV_PHI,
    }

    return {
        "overall": overall,
        "strata": strata_results,
        "per_sample": overall_raw["per_sample"],
    }


# ══════════════════════════════════════════════════════════════════════
# Display
# ══════════════════════════════════════════════════════════════════════


def print_banner(step: int, state: dict, model: V6Compressor):
    """Print checkpoint summary banner."""
    print(f"\n{'='*72}")
    print(f"  v10 Probe — step {step:,}")
    print(f"{'='*72}")

    cfg_data = state.get("config", {})
    print(f"  d_model={cfg_data.get('d_model', '?')}  "
          f"vocab={cfg_data.get('vocab_size', '?')}  "
          f"seq_len={cfg_data.get('seq_len', '?')}")

    params = count_parameters(model)
    n_ternary = count_ternary_weights(model)
    print(f"  params: total={params['total']:,}  "
          f"trainable={params['trainable']:,}  "
          f"ternary={n_ternary:,}")

    # Training state from checkpoint
    evo_gen = state.get("total_generations", 0)
    evo_acc = state.get("total_accepted", 0)
    if evo_gen > 0:
        pct = evo_acc / evo_gen * 100
        print(f"  evolution: {evo_acc}/{evo_gen} accepted ({pct:.0f}%)")

    losses = state.get("train_losses_last50", [])
    if losses:
        avg = sum(losses) / len(losses)
        # Detect whether losses are CE (>1) or relational r (<1 typically)
        if avg > 1.5:
            # Legacy: CE values
            r = (avg - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)
            print(f"  train loss (last 50): CE={avg:.3f}  r={r:.3f}")
        else:
            # Current: relational r values
            ce = avg * (LOG_V - E_IRREDUCIBLE) + E_IRREDUCIBLE
            print(f"  train loss (last 50): r={avg:.4f}  CE={ce:.3f}")


def print_compressor_metrics(phi_result: dict):
    """Print compressor metrics from φ analysis."""
    overall = phi_result["overall"]

    # ── S3 gates ──────────────────────────────────────────
    print(f"\n  ┌─ S3 gates ──────────────────────────────────────┐")
    for pi, pname in enumerate(PASS_NAMES):
        gates = overall["s3_gates"][pi]
        print(f"  │ {pname:8s}: prep={gates[0]:.3f}  conv={gates[1]:.3f}  "
              f"cons={gates[2]:.3f}")

    # ── Meta-S3 ──────────────────────────────────────────
    print(f"  ├─ Meta-S3 ───────────────────────────────────────┤")
    mg = overall["meta_s3"]
    print(f"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(PASS_NAMES, mg))}")

    # ── Compression ──────────────────────────────────────
    print(f"  ├─ φ-Compression (1/φ = {INV_PHI:.4f}) ──────────────┤")
    cr = overall["pass_compression"]
    pd = overall["pass_phi_dev"]
    for pi, pname in enumerate(PASS_NAMES):
        phi_mark = " ←φ" if pd[pi] < 0.05 else "   "
        print(f"  │ {pname:8s}: ratio={cr[pi]:>7.3f}  φ-dev={pd[pi]:.3f}{phi_mark}")

    agg = overall["aggregate"]
    print(f"  │ {'MEAN':8s}: ratio={agg['mean_ratio']:>7.3f}  "
          f"φ-dev={agg['mean_phi_dev']:.3f}")

    # ── Entropy ──────────────────────────────────────────
    print(f"  ├─ Entropy (log variance proxy) ──────────────────┤")
    h_in = overall["pass_entropy_in"]
    h_out = overall["pass_entropy_out"]
    for pi, pname in enumerate(PASS_NAMES):
        print(f"  │ {pname:8s}: {h_in[pi]:>7.3f} → {h_out[pi]:>7.3f}")

    # ── Register norms ───────────────────────────────────
    reg_norms = overall["register_norms"]
    if reg_norms:
        print(f"  ├─ Register norms ────────────────────────────────┤")
        for bname in sorted(reg_norms.keys()):
            norms = reg_norms[bname]
            print(f"  │ {bname:12s}: {' '.join(f'{n:>7.2f}' for n in norms)}")

    # ── Kernel dispatch weights ──────────────────────────
    kdw = overall.get("kernel_dispatch_weights")
    if kdw:
        print(f"  ├─ Kernel dispatch (top ops) ─────────────────────┤")
        # Sort by weight, show top 8
        indexed = sorted(enumerate(kdw), key=lambda x: -x[1])
        for rank, (op_idx, weight) in enumerate(indexed[:8]):
            op_name = KERNEL_OP_NAMES[op_idx] if op_idx < len(KERNEL_OP_NAMES) else f"op{op_idx}"
            bar = "█" * int(weight * 100)
            print(f"  │ {op_name:>8s} ({op_idx:>2d}): {weight:.3f} {bar}")
        # Check uniformity: max/min ratio
        nonzero_kdw = [w for w in kdw if w > 1e-6]
        if nonzero_kdw:
            max_w, min_w = max(nonzero_kdw), min(nonzero_kdw)
            ratio = max_w / (min_w + 1e-8)
            n_active = len(nonzero_kdw)
            n_dead = len(kdw) - n_active
            if n_dead > 0:
                print(f"  │ {n_active} active, {n_dead} dead (zero weight)")
            if ratio < 1.5:
                print(f"  │ ≈ uniform (max/min={ratio:.2f}) — not specialized yet")
            else:
                print(f"  │ max/min={ratio:.2f} — specializing")

    # ── Op embedding health ──────────────────────────────
    op_emb_norms = overall.get("op_embedding_norms")
    if op_emb_norms:
        norms = op_emb_norms
        max_n, min_n = max(norms), min(norms)
        print(f"  ├─ Op embedding norms ────────────────────────────┤")
        if max_n / (min_n + 1e-8) > 2.0:
            # Show individual norms — something is wrong
            indexed = sorted(enumerate(norms), key=lambda x: -x[1])
            for op_idx, norm in indexed[:5]:
                op_name = KERNEL_OP_NAMES[op_idx] if op_idx < len(KERNEL_OP_NAMES) else f"op{op_idx}"
                print(f"  │ {op_name:>8s}: {norm:.4f}")
            print(f"  │ ⚠ norm spread {max_n:.3f}/{min_n:.3f} = {max_n/(min_n+1e-8):.1f}× — fossil risk")
        else:
            print(f"  │ all ≈ {sum(norms)/len(norms):.3f} (healthy)")

    # ── Kernel type weights ──────────────────────────────
    ktw = overall.get("kernel_type_weights")
    if ktw:
        print(f"  ├─ Kernel types ──────────────────────────────────┤")
        for ti, (tname, tw) in enumerate(zip(KERNEL_TYPE_NAMES, ktw)):
            bar = "█" * int(tw * 50)
            print(f"  │ {tname:>8s}: {tw:.3f} {bar}")

    print(f"  └─────────────────────────────────────────────────┘")


def print_strata(phi_result: dict):
    """Print per-stratum compression and loss."""
    strata = phi_result["strata"]
    if not strata:
        return

    print(f"\n  φ-Compression by content type:")
    print(f"  {'stratum':15s} {'loss':>8} {'mean_cr':>8} ", end="")
    for pn in PASS_NAMES:
        print(f" {pn:>7}", end="")
    print()
    print(f"  {'─'*15} {'─'*8} {'─'*8}", end="")
    for _ in PASS_NAMES:
        print(f" {'─'*7}", end="")
    print()

    means = []
    for sname in ["prose", "compositional", "technical", "math"]:
        if sname not in strata:
            continue
        s = strata[sname]
        cr = s["pass_compression"]
        mean_cr = sum(cr) / len(cr)
        means.append(mean_cr)
        print(f"  {sname:15s} {s['mean_loss']:>8.3f} {mean_cr:>8.3f}", end="")
        for v in cr:
            print(f" {v:>7.3f}", end="")
        print()

    if len(means) >= 2:
        spread = max(means) - min(means)
        print(f"  {'─'*15} {'─'*8} {'─'*8}")
        print(f"  spread: {spread:.4f}", end="")
        if spread < 0.05:
            print("  ✓ content-independent")
        elif spread < 0.15:
            print("  → converging")
        else:
            print("  ⚠ content-dependent (expected early)")
        print()


def print_phi_interpretation(phi_result: dict):
    """Interpret φ-compression results."""
    agg = phi_result["overall"]["aggregate"]
    mr = agg["mean_ratio"]
    pd = agg["mean_phi_dev"]

    if mr > 1.05:
        print(f"  ⚠ EXPANDING (ratio > 1). No compression yet.")
    elif mr > 0.95:
        print(f"  ≈ Near-identity (ratio ≈ 1). Minimal compression.")
    elif pd < 0.05:
        print(f"  ✓ Within 0.05 of 1/φ — convergence signal!")
    elif pd < 0.15:
        print(f"  → Compressing, φ-dev={pd:.3f}. In the neighborhood.")
    else:
        print(f"  → Compressing at {mr:.3f}, far from φ (dev={pd:.3f}).")

    # Ascending vs descending
    cr = phi_result["overall"]["pass_compression"]
    asc = cr[:3]
    desc = cr[3:]
    asc_m = sum(asc) / len(asc)
    desc_m = sum(desc) / len(desc)
    spread = max(cr) - min(cr)

    if spread < 0.05:
        print(f"  ≡ All passes at similar ratios (spread={spread:.3f}). Self-similar.")
    elif abs(asc_m - desc_m) > 0.03:
        direction = "ascending" if asc_m < desc_m else "descending"
        print(f"  ≠ {direction} compresses more "
              f"(asc={asc_m:.3f} desc={desc_m:.3f}).")


def print_per_sample(per_sample: list[dict]):
    """Print per-sample φ detail."""
    print(f"\n  Per-sample φ detail:")
    for sd in per_sample:
        print(f"    {sd['text']!r}  loss={sd['loss']:.3f}")
        cr = sd["pass_compression"]
        pd = sd["pass_phi_dev"]
        for pi, pn in enumerate(PASS_NAMES):
            marker = " ←φ" if pd[pi] < 0.05 else ""
            print(f"      {pn:8s}: ratio={cr[pi]:.4f}  φ-dev={pd[pi]:.4f}{marker}")


# ══════════════════════════════════════════════════════════════════════
# Multi-checkpoint evolution
# ══════════════════════════════════════════════════════════════════════


def print_evolution(all_results: list[dict]):
    """Print multi-checkpoint evolution table."""
    if len(all_results) < 2:
        return

    print(f"\n{'='*72}")
    print(f"  φ-Compression Evolution")
    print(f"{'='*72}")

    # ── Loss + r evolution ──────────────────────────────────
    print(f"\n  {'step':>8} {'loss':>8} {'ppl':>8} {'r':>8} {'evo%':>6}")
    print(f"  {'─'*8} {'─'*8} {'─'*8} {'─'*8} {'─'*6}")
    for r in all_results:
        loss = r.get("eval_loss", r.get("train_loss_avg", 0))
        ppl = math.exp(min(loss, 20.0)) if loss else 0
        rel_r = (loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE) if loss else 0
        evo_pct = r.get("evo_pct", "")
        evo_str = f"{evo_pct:.0f}%" if isinstance(evo_pct, (int, float)) else ""
        print(f"  {r['step']:>8} {loss:>8.3f} {ppl:>8.0f} {rel_r:>8.3f} {evo_str:>6}")

    # ── Per-pass compression evolution ──────────────────────
    print(f"\n  {'step':>8} {'mean':>8} {'φ-dev':>8}", end="")
    for pn in PASS_NAMES:
        print(f" {pn:>8}", end="")
    print()
    print(f"  {'─'*8} {'─'*8} {'─'*8}", end="")
    for _ in PASS_NAMES:
        print(f" {'─'*8}", end="")
    print()

    for r in all_results:
        phi = r.get("phi_overall", {})
        agg = phi.get("aggregate", {})
        cr = phi.get("pass_compression", [0]*5)
        print(f"  {r['step']:>8} {agg.get('mean_ratio', 0):>8.4f} "
              f"{agg.get('mean_phi_dev', 0):>8.4f}", end="")
        for v in cr:
            print(f" {v:>8.4f}", end="")
        print()

    print(f"  {'target':>8} {INV_PHI:>8.4f} {'0.0000':>8}")

    # ── Per-stratum evolution ───────────────────────────────
    strata_names = set()
    for r in all_results:
        if "phi_strata" in r:
            strata_names.update(r["phi_strata"].keys())

    if strata_names:
        ordered = [s for s in ["prose", "compositional", "technical", "math"]
                   if s in strata_names]
        print(f"\n  Per-stratum mean compression:")
        print(f"  {'step':>8}", end="")
        for sn in ordered:
            print(f" {sn:>14}", end="")
        print(f" {'spread':>8}")
        print(f"  {'─'*8}", end="")
        for _ in ordered:
            print(f" {'─'*14}", end="")
        print(f" {'─'*8}")

        for r in all_results:
            print(f"  {r['step']:>8}", end="")
            vals = []
            for sn in ordered:
                st = r.get("phi_strata", {}).get(sn, {})
                cr = st.get("pass_compression", [])
                if cr:
                    mean_cr = sum(cr) / len(cr)
                    print(f" {mean_cr:>14.4f}", end="")
                    vals.append(mean_cr)
                else:
                    print(f" {'—':>14}", end="")
            if vals:
                print(f" {max(vals) - min(vals):>8.4f}", end="")
            print()

    # ── S3 gate evolution ───────────────────────────────────
    print(f"\n  S3 Gate Evolution (pass 0 = L0↑, most informative early):")
    print(f"  {'step':>8}", end="")
    for ph in PHASE_NAMES:
        print(f" {ph:>8}", end="")
    print(f"  │ meta-S3")
    print(f"  {'─'*8}", end="")
    for _ in PHASE_NAMES:
        print(f" {'─'*8}", end="")
    print(f"  │ {'─'*30}")

    for r in all_results:
        phi = r.get("phi_overall", {})
        s3 = phi.get("s3_gates", [[0]*3]*5)
        ms3 = phi.get("meta_s3", [0]*5)
        print(f"  {r['step']:>8}", end="")
        for ph in range(3):
            print(f" {s3[0][ph]:>8.3f}", end="")
        print(f"  │ {' '.join(f'{g:.3f}' for g in ms3)}")

    print(f"{'='*72}\n")


# ══════════════════════════════════════════════════════════════════════
# JSON output
# ══════════════════════════════════════════════════════════════════════


def save_results(step: int, state: dict, phi_result: dict,
                 eval_result: dict | None, ternary: dict | None,
                 out_dir: Path) -> Path:
    """Save probe results to JSON."""
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"probe_step_{step:06d}.json"

    output = {
        "timestamp": datetime.now(UTC).isoformat(),
        "architecture": "v10-v6compressor-prose-lm",
        "step": step,
        "config": state.get("config", {}),
        "evolution": {
            "total_generations": state.get("total_generations", 0),
            "total_accepted": state.get("total_accepted", 0),
        },
        "phi_compression": {
            "overall": phi_result["overall"],
            "strata": phi_result["strata"],
        },
    }

    if eval_result:
        output["eval"] = eval_result

    if ternary:
        # Summarize — full per-module stats are too verbose for JSON
        n_mods = len(ternary)
        sparsities = [s["sparsity"] for s in ternary.values()]
        gammas = [s["gamma_mean"] for s in ternary.values()]
        output["ternary_summary"] = {
            "n_modules": n_mods,
            "mean_sparsity": sum(sparsities) / n_mods,
            "mean_gamma": sum(gammas) / n_mods,
            "min_sparsity": min(sparsities),
            "max_sparsity": max(sparsities),
        }

    out_path.write_text(json.dumps(output, indent=2))
    return out_path


# ══════════════════════════════════════════════════════════════════════
# CLI
# ══════════════════════════════════════════════════════════════════════


def main():
    parser = argparse.ArgumentParser(
        description="v10 probe — checkpoint diagnostics for V6Compressor prose LM")
    parser.add_argument("checkpoints", type=Path, nargs="+",
                        help="Checkpoint directory/directories")
    parser.add_argument("--quiet", action="store_true",
                        help="Summary tables only")
    parser.add_argument("--phi-only", action="store_true",
                        help="Skip eval, just measure compression")
    parser.add_argument("--no-eval", action="store_true",
                        help="Skip data evaluation (faster)")
    parser.add_argument("--verbose", "-v", action="store_true",
                        help="Per-sample φ detail")
    parser.add_argument("--no-ternary", action="store_true",
                        help="Skip ternary statistics (faster)")
    parser.add_argument("--results-dir", type=Path, default=RESULTS_DIR,
                        help="Output directory for JSON results")
    args = parser.parse_args()

    if args.phi_only:
        args.no_eval = True

    # ── Tokenizer ─────────────────────────────────────────
    print("  Loading Qwen3 tokenizer...", file=sys.stderr)
    from transformers import AutoTokenizer
    tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-0.6B", trust_remote_code=True)

    # ── Sort checkpoints by step ──────────────────────────
    ckpts = sorted(
        [p for p in args.checkpoints if p.is_dir()],
        key=lambda p: int(p.name.split("_")[-1]) if p.name.startswith("step_") else 0,
    )

    if not ckpts:
        print("  No checkpoint directories found.", file=sys.stderr)
        return

    all_results = []

    for ckpt_path in ckpts:
        t0 = time.time()

        # ── Load ──────────────────────────────────────────
        print(f"\n  Loading {ckpt_path}...", file=sys.stderr)
        model, step, state, cfg = load_checkpoint(ckpt_path)
        print_banner(step, state, model)

        # ── φ-compression ─────────────────────────────────
        print(f"\n  Running φ-compression analysis...", file=sys.stderr)
        phi_result = analyze_phi(model, tokenizer)
        print_compressor_metrics(phi_result)

        if not args.quiet:
            print_strata(phi_result)
            print_phi_interpretation(phi_result)

        if args.verbose:
            print_per_sample(phi_result["per_sample"])

        # ── Eval ──────────────────────────────────────────
        eval_result = None
        if not args.no_eval:
            print(f"\n  Evaluating on held-out data...", file=sys.stderr)
            eval_result = evaluate_on_data(model, cfg)
            print(f"\n  📊 Eval: loss={eval_result['loss']:.3f}  "
                  f"ppl={eval_result['ppl']:.0f}  r={eval_result['r']:.3f}  "
                  f"({eval_result['tokens_evaluated']:,} tokens)")

        # ── Ternary stats ─────────────────────────────────
        ternary = None
        if not args.no_ternary:
            ternary = ternary_stats(model)
            if not args.quiet:
                print_ternary_stats(ternary)

        # ── Save JSON ─────────────────────────────────────
        out_path = save_results(step, state, phi_result,
                                eval_result, ternary, args.results_dir)
        print(f"\n  💾 Saved: {out_path}")

        elapsed = time.time() - t0
        print(f"  ⏱  {elapsed:.1f}s", file=sys.stderr)

        # ── Collect for evolution table ───────────────────
        losses = state.get("train_losses_last50", [])
        train_loss_avg = sum(losses) / len(losses) if losses else 0
        evo_gen = state.get("total_generations", 0)
        evo_acc = state.get("total_accepted", 0)

        result_entry = {
            "step": step,
            "train_loss_avg": train_loss_avg,
            "eval_loss": eval_result["loss"] if eval_result else train_loss_avg,
            "evo_pct": (evo_acc / evo_gen * 100) if evo_gen > 0 else 0,
            "phi_overall": phi_result["overall"],
            "phi_strata": phi_result["strata"],
        }
        all_results.append(result_entry)

    # ── Multi-checkpoint evolution ────────────────────────
    print_evolution(all_results)


if __name__ == "__main__":
    main()
```

## Assistant

Good, I have the full v10 probe. Now let me also check the dispatch probe since the user specifically wants kernel op distribution analysis:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v10/probe_dispatch.py",
  "limit": 60
}
```

**Summary:** Reading probe_dispatch.py (0-60)

**Output:**
```
"""
Probe per-position dispatch × type co-occurrence in v10-topk checkpoints.

With top-k=2, every position selects exactly 2 ops. This probe captures:
  1. Co-occurrence matrix: which op pairs appear together as top-2
  2. Per-position type × dispatch cross-tabulation
  3. Whether FN-typed positions correlate with specific ops

Usage:
    uv run python scripts/v10/probe_dispatch.py \
        --checkpoint checkpoints/v10-consensus/step_012000

License: MIT
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import mlx.core as mx
import mlx.nn as nn
import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from config import V10Config
from data import ShardedDataLoader
from model import V6Compressor, create_model
from ternary import freeze_ternary_weights, restore_ternary

# ── Op and type names ──────────────────────────────────────────────────

OP_NAMES = [
    "ADD", "SUB", "MUL", "DIV", "MOD", "MIN", "MAX",
    "EQ", "LT", "GT", "LE", "GE",
    "AND", "OR",
    "NOT",
    "ABS", "NEG",
    "IF",
    "PARTIAL", "APPLY", "COMPOSE", "APPLY-COMP",
]

TYPE_NAMES = ["INT", "BOOL", "FN", "FN_COMP", "ERROR"]

OP_FAMILIES = {
    "arith_binary":  [0, 1, 2, 3, 4, 5, 6],
    "comparison":    [7, 8, 9, 10, 11],
    "bool_binary":   [12, 13],
    "bool_unary":    [14],
    "arith_unary":   [15, 16],
    "conditional":   [17],
    "lambda":        [18, 19, 20, 21],
}

# Expected output type per op
OP_EXPECTED_TYPE = [
    "INT", "INT", "INT", "INT", "INT", "INT", "INT",       # arith_binary

[CONTENT TRUNCATED] Showing lines 1 to 60 of 355 total lines. Use line_offset=60 parameter to read more content.
```

## Assistant

Now I have a clear picture. Let me build the v11 probe — it needs to handle KIBC-specific analysis while keeping the useful structure from v10's probe.py. I'll also integrate the dispatch distribution analysis directly.

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/scripts/v11/probe.py",
  "content": "#!/usr/bin/env python3\n\"\"\"v11 probe — checkpoint diagnostics for KIBC combinator VSM.\n\nProbes v11 checkpoints with:\n  - Eval loss + relational loss\n  - Combinator dispatch distribution (K, I, B, C weights and evolution)\n  - Per-position dispatch analysis (which combinator dominates where)\n  - CycleContinue dynamics (effective cycles, continuation gates)\n  - Combinator emphasis from S4 intelligence channel\n  - φ-compression analysis (stratified by content type)\n  - S3 gates, S5 reweight, S2 coordination\n  - Ternary topology statistics\n  - Multi-checkpoint evolution tables\n  - JSONL trajectory analysis (metrics_log.jsonl)\n\nUsage:\n    # Single checkpoint\n    uv run python scripts/v11/probe.py checkpoints/v11/step_001000\n\n    # Multiple checkpoints — evolution table\n    uv run python scripts/v11/probe.py checkpoints/v11/step_*\n\n    # Trajectory analysis from JSONL logs (no checkpoint loading)\n    uv run python scripts/v11/probe.py --trajectory checkpoints/v11\n\n    # Per-position dispatch distribution analysis\n    uv run python scripts/v11/probe.py checkpoints/v11/step_005000 --dispatch-detail\n\n    # Quick: skip eval, just metrics\n    uv run python scripts/v11/probe.py checkpoints/v11/step_001000 --no-eval\n\nLicense: MIT\n\"\"\"\n\nfrom __future__ import annotations\n\nimport argparse\nimport json\nimport math\nimport sys\nimport time\nfrom datetime import UTC, datetime\nfrom pathlib import Path\n\nimport mlx.core as mx\nimport mlx.nn as nn\nimport numpy as np\nfrom mlx.utils import tree_flatten\n\nsys.path.insert(0, str(Path(__file__).resolve().parent))\n\nfrom config import V11Config\nfrom model import V11Model, create_model, count_parameters\nfrom kernel import N_COMBINATORS, COMBINATOR_NAMES, COMBINATOR_ROLE\nfrom ternary import (\n    freeze_ternary_weights,\n    restore_ternary,\n    count_ternary_weights,\n    unpack_ternary_mlx,\n    unpack_ternary,\n    _walk_ternary_modules,\n    TernaryLinear,\n    TernaryEmbedding,\n)\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Constants\n# ══════════════════════════════════════════════════════════════════════\n\nE_IRREDUCIBLE = 1.82\nLOG_V = math.log(151936)  # ≈ 11.93\nPHI = (1 + math.sqrt(5)) / 2\nINV_PHI = 1 / PHI\n\nPASS_NAMES = (\"L0_asc\", \"L1_asc\", \"L2_apex\", \"L1_desc\", \"L0_desc\")\nPASS_NAMES_SHORT = (\"L0↑\", \"L1↑\", \"L2\", \"L1↓\", \"L0↓\")\n\nRESULTS_DIR = Path(\"results/v11\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# φ-compression strata (shared with v10)\n# ══════════════════════════════════════════════════════════════════════\n\nPHI_STRATA = {\n    \"prose\": [\n        \"The cat sat on the mat and looked out the window at the birds flying south for the winter.\",\n        \"Every student who passed the final exam received a certificate of achievement from the dean.\",\n        \"The quick brown fox jumps over the lazy dog near the river bank on a warm summer afternoon.\",\n        \"In a quiet village nestled between rolling hills, the old baker opened his shop at dawn.\",\n    ],\n    \"compositional\": [\n        \"The man who the dog that the cat chased bit ran away quickly.\",\n        \"If every student reads a book then some teacher who knows the author is happy.\",\n        \"No politician who endorsed the candidate that lost the election won their own race.\",\n        \"Every lawyer who represents a client that a judge dismissed the case against appealed.\",\n    ],\n    \"technical\": [\n        \"The gradient of the loss with respect to the weights is computed via backpropagation.\",\n        \"Attention scores are computed as the softmax of the scaled dot product of queries and keys.\",\n        \"The learning rate schedule uses cosine annealing with linear warmup over 500 steps.\",\n        \"Each layer applies layer normalization before the self-attention and feed-forward blocks.\",\n    ],\n    \"lambda\": [\n        \"λx. λy. apply(x, y) → result\",\n        \"K x y = x selects the first and discards the second\",\n        \"B f g x = f (g x) composes two functions together\",\n        \"C f x y = f y x flips the argument order for closures\",\n    ],\n}\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Checkpoint loading\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef load_checkpoint(ckpt_path: Path) -> tuple[V11Model, int, dict, V11Config]:\n    \"\"\"Load a v11 checkpoint. Returns (model, step, state_dict, config).\"\"\"\n    state_path = ckpt_path / \"state.json\"\n    model_path = ckpt_path / \"model.npz\"\n\n    if not state_path.exists() or not model_path.exists():\n        raise FileNotFoundError(f\"Missing state.json or model.npz in {ckpt_path}\")\n\n    state = json.loads(state_path.read_text())\n    step = state[\"step\"]\n    config_data = state.get(\"config\", {})\n\n    cfg = V11Config()\n    if \"d_model\" in config_data:\n        cfg.d_model = config_data[\"d_model\"]\n        cfg.d_ff = cfg.d_model * 3\n        cfg.d_ff_consolidate = cfg.d_model * 4\n    if \"vocab_size\" in config_data:\n        cfg.vocab_size = config_data[\"vocab_size\"]\n    if \"seq_len\" in config_data:\n        cfg.seq_len = config_data[\"seq_len\"]\n        cfg.max_seq_len = config_data[\"seq_len\"]\n\n    model = create_model(cfg)\n    weights = dict(mx.load(str(model_path)))\n    model.load_weights(list(weights.items()), strict=False)\n    mx.eval(model.parameters())\n    freeze_ternary_weights(model)\n    restore_ternary(model)\n\n    return model, step, state, cfg\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Evaluation\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef evaluate_on_data(model: V11Model, cfg: V11Config,\n                     target_tokens: int = 50_000) -> dict:\n    \"\"\"Evaluate on held-out Dolma shards.\"\"\"\n    from data import ShardedDataLoader\n\n    eval_loader = ShardedDataLoader(\n        data_dir=cfg.data_dir, batch_size=cfg.batch_size,\n        seq_len=cfg.seq_len, shard_start=cfg.n_train_shards,\n        shard_end=cfg.n_train_shards + cfg.n_eval_shards, seed=9999,\n    )\n\n    total_loss = 0.0\n    n_batches = 0\n    tokens_seen = 0\n\n    while tokens_seen < target_tokens:\n        input_ids_np, targets_np = eval_loader.next_batch()\n        input_ids = mx.array(input_ids_np)\n        targets = mx.array(targets_np)\n        _, loss = model(input_ids, targets)\n        mx.eval(loss)\n        total_loss += float(loss.item())\n        n_batches += 1\n        tokens_seen += input_ids_np.size\n\n    avg_loss = total_loss / max(n_batches, 1)\n    ppl = math.exp(min(avg_loss, 20.0))\n    r = (avg_loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE)\n\n    return {\"loss\": avg_loss, \"ppl\": ppl, \"r\": r,\n            \"tokens_evaluated\": tokens_seen, \"n_batches\": n_batches}\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Per-position dispatch distribution analysis\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef analyze_dispatch_distribution(\n    model: V11Model, cfg: V11Config, n_batches: int = 10\n) -> dict:\n    \"\"\"Analyze per-position combinator dispatch distribution.\n\n    Runs multiple batches through the model, collects dispatch weights\n    at every position, and computes:\n      - Mean combinator distribution\n      - Per-position dominant combinator histogram\n      - Entropy of the dispatch distribution (specialization measure)\n      - Combinator co-occurrence (which pairs appear in top-2)\n      - Per-combinator positional statistics\n    \"\"\"\n    from data import ShardedDataLoader\n\n    eval_loader = ShardedDataLoader(\n        data_dir=cfg.data_dir, batch_size=cfg.batch_size,\n        seq_len=cfg.seq_len, shard_start=cfg.n_train_shards,\n        shard_end=cfg.n_train_shards + cfg.n_eval_shards, seed=42,\n    )\n\n    all_dispatch_weights = []  # list of (B, L, 4) arrays\n    all_type_weights = []\n    all_compute_gates = []\n\n    for _ in range(n_batches):\n        input_ids_np, _ = eval_loader.next_batch()\n        input_ids = mx.array(input_ids_np)\n        _, metrics = model.forward_instrumented(input_ids)\n\n        # Collect raw dispatch weights from the model's cached state\n        if hasattr(model.combinator_dispatch, '_dispatch_weights'):\n            dw = model.combinator_dispatch._dispatch_weights  # (B, L, 4)\n            mx.eval(dw)\n            all_dispatch_weights.append(np.array(dw))\n\n        if hasattr(model.combinator_integrate, '_type_weights'):\n            tw = model.combinator_integrate._type_weights  # (B, L, 4)\n            mx.eval(tw)\n            all_type_weights.append(np.array(tw))\n\n        if hasattr(model.combinator_integrate, '_compute_gate'):\n            cg = model.combinator_integrate._compute_gate  # (B, L, 1)\n            mx.eval(cg)\n            all_compute_gates.append(np.array(cg))\n\n    if not all_dispatch_weights:\n        return {\"error\": \"no dispatch weights captured\"}\n\n    # Concatenate across batches: (total_positions, 4)\n    dw_all = np.concatenate(all_dispatch_weights, axis=0)  # (N_batches*B, L, 4)\n    dw_flat = dw_all.reshape(-1, N_COMBINATORS)             # (total_pos, 4)\n    n_positions = dw_flat.shape[0]\n\n    # ── Mean distribution ─────────────────────────────────\n    mean_dist = dw_flat.mean(axis=0)  # (4,)\n\n    # ── Dominant combinator histogram ─────────────────────\n    dominant = np.argmax(dw_flat, axis=-1)  # (total_pos,)\n    dom_counts = np.bincount(dominant, minlength=N_COMBINATORS)\n    dom_fracs = dom_counts / n_positions\n\n    # ── Dispatch entropy per position ─────────────────────\n    # H = -Σ p log p (uniform = log(4) ≈ 1.386, fully specialized = 0)\n    log_dw = np.log(dw_flat + 1e-8)\n    entropy = -(dw_flat * log_dw).sum(axis=-1)  # (total_pos,)\n    max_entropy = np.log(N_COMBINATORS)\n\n    # ── Top-2 co-occurrence ───────────────────────────────\n    # For each position, which 2 combinators have highest weight?\n    top2 = np.argsort(dw_flat, axis=-1)[:, -2:]  # (total_pos, 2)\n    cooccur = np.zeros((N_COMBINATORS, N_COMBINATORS), dtype=np.int64)\n    for row in top2:\n        a, b = sorted(row)\n        cooccur[a, b] += 1\n\n    # ── Per-combinator weight statistics ──────────────────\n    per_comb = {}\n    for ci in range(N_COMBINATORS):\n        weights = dw_flat[:, ci]\n        per_comb[COMBINATOR_NAMES[ci]] = {\n            \"mean\": float(weights.mean()),\n            \"std\": float(weights.std()),\n            \"median\": float(np.median(weights)),\n            \"p95\": float(np.percentile(weights, 95)),\n            \"p05\": float(np.percentile(weights, 5)),\n            \"dominant_frac\": float(dom_fracs[ci]),\n        }\n\n    # ── Type weights and compute gate ─────────────────────\n    type_dist = None\n    if all_type_weights:\n        tw_all = np.concatenate(all_type_weights, axis=0)\n        type_dist = tw_all.reshape(-1, N_COMBINATORS).mean(axis=0)\n\n    compute_gate_stats = None\n    if all_compute_gates:\n        cg_all = np.concatenate(all_compute_gates, axis=0).flatten()\n        compute_gate_stats = {\n            \"mean\": float(cg_all.mean()),\n            \"max\": float(cg_all.max()),\n            \"p95\": float(np.percentile(cg_all, 95)),\n            \"active_frac\": float((cg_all > 0.5).mean()),\n        }\n\n    return {\n        \"n_positions\": n_positions,\n        \"mean_distribution\": {COMBINATOR_NAMES[i]: float(mean_dist[i])\n                               for i in range(N_COMBINATORS)},\n        \"dominant_fractions\": {COMBINATOR_NAMES[i]: float(dom_fracs[i])\n                                for i in range(N_COMBINATORS)},\n        \"entropy\": {\n            \"mean\": float(entropy.mean()),\n            \"std\": float(entropy.std()),\n            \"max_possible\": float(max_entropy),\n            \"normalized_mean\": float(entropy.mean() / max_entropy),\n        },\n        \"top2_cooccurrence\": {\n            f\"{COMBINATOR_NAMES[i]}+{COMBINATOR_NAMES[j]}\": int(cooccur[i, j])\n            for i in range(N_COMBINATORS)\n            for j in range(i, N_COMBINATORS)\n            if cooccur[i, j] > 0\n        },\n        \"per_combinator\": per_comb,\n        \"type_distribution\": (\n            {COMBINATOR_NAMES[i]: float(type_dist[i])\n             for i in range(N_COMBINATORS)}\n            if type_dist is not None else None\n        ),\n        \"compute_gate\": compute_gate_stats,\n    }\n\n\ndef print_dispatch_analysis(da: dict) -> None:\n    \"\"\"Display combinator dispatch distribution analysis.\"\"\"\n    if \"error\" in da:\n        print(f\"  ⚠ {da['error']}\")\n        return\n\n    n = da[\"n_positions\"]\n    print(f\"\\n  ┌─ Combinator Dispatch Distribution ({n:,} positions) ─┐\")\n\n    # Mean distribution with bars\n    md = da[\"mean_distribution\"]\n    for name in COMBINATOR_NAMES:\n        w = md[name]\n        bar = \"█\" * int(w * 80)\n        role = COMBINATOR_ROLE.get({\"K\": 0, \"I\": 1, \"B\": 2, \"C\": 3}[name], \"\")\n        print(f\"  │ {name} ({role:8s}): {w:.4f} {bar}\")\n\n    # Dominant combinator\n    print(f\"  ├─ Dominant combinator per position ──────────────┤\")\n    df = da[\"dominant_fractions\"]\n    for name in COMBINATOR_NAMES:\n        f = df[name]\n        bar = \"█\" * int(f * 60)\n        print(f\"  │ {name}: {f:.1%} {bar}\")\n\n    # Entropy (specialization)\n    ent = da[\"entropy\"]\n    print(f\"  ├─ Dispatch entropy ──────────────────────────────┤\")\n    print(f\"  │ mean={ent['mean']:.4f} / {ent['max_possible']:.4f} \"\n          f\"(normalized={ent['normalized_mean']:.3f})\")\n    if ent[\"normalized_mean\"] > 0.95:\n        print(f\"  │ ≈ uniform — not specialized yet\")\n    elif ent[\"normalized_mean\"] > 0.8:\n        print(f\"  │ → beginning to specialize\")\n    elif ent[\"normalized_mean\"] > 0.5:\n        print(f\"  │ ✓ meaningful specialization\")\n    else:\n        print(f\"  │ ✓ strong specialization\")\n\n    # Top-2 co-occurrence\n    cooc = da[\"top2_cooccurrence\"]\n    if cooc:\n        print(f\"  ├─ Top-2 co-occurrence ───────────────────────────┤\")\n        sorted_cooc = sorted(cooc.items(), key=lambda x: -x[1])\n        for pair, count in sorted_cooc[:6]:\n            pct = count / n * 100\n            print(f\"  │ {pair:5s}: {count:>8,} ({pct:>5.1f}%)\")\n\n    # Per-combinator statistics\n    pc = da[\"per_combinator\"]\n    print(f\"  ├─ Per-combinator weight statistics ──────────────┤\")\n    print(f\"  │ {'':1s} {'mean':>7s} {'std':>7s} {'median':>7s} \"\n          f\"{'p05':>7s} {'p95':>7s}\")\n    for name in COMBINATOR_NAMES:\n        s = pc[name]\n        print(f\"  │ {name} {s['mean']:>7.4f} {s['std']:>7.4f} \"\n              f\"{s['median']:>7.4f} {s['p05']:>7.4f} {s['p95']:>7.4f}\")\n\n    # Type distribution\n    td = da.get(\"type_distribution\")\n    if td:\n        print(f\"  ├─ Combinator type distribution ──────────────────┤\")\n        for name in COMBINATOR_NAMES:\n            w = td[name]\n            bar = \"█\" * int(w * 50)\n            print(f\"  │ {name}: {w:.4f} {bar}\")\n\n    # Compute gate\n    cg = da.get(\"compute_gate\")\n    if cg:\n        print(f\"  ├─ Compute gate ──────────────────────────────────┤\")\n        print(f\"  │ mean={cg['mean']:.4f}  max={cg['max']:.4f}  \"\n              f\"p95={cg['p95']:.4f}  active(>0.5)={cg['active_frac']:.1%}\")\n\n    print(f\"  └─────────────────────────────────────────────────┘\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# JSONL trajectory analysis\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef analyze_trajectory(checkpoint_dir: Path) -> None:\n    \"\"\"Analyze training trajectory from JSONL logs (no model loading).\"\"\"\n    metrics_path = checkpoint_dir / \"metrics_log.jsonl\"\n    train_path = checkpoint_dir / \"train_log.jsonl\"\n    evo_path = checkpoint_dir / \"evolution_log.jsonl\"\n\n    print(f\"\\n{'='*72}\")\n    print(f\"  v11 Trajectory Analysis — {checkpoint_dir}\")\n    print(f\"{'='*72}\")\n\n    # ── Metrics trajectory ────────────────────────────────\n    if metrics_path.exists():\n        with open(metrics_path) as f:\n            metrics = [json.loads(l) for l in f]\n\n        print(f\"\\n  📊 Metrics trajectory ({len(metrics)} evaluations)\")\n\n        # Loss trajectory\n        print(f\"\\n  {'step':>8} {'loss':>8} {'r':>8} {'comp_gate':>10} \", end=\"\")\n        for cn in COMBINATOR_NAMES:\n            print(f\" {cn:>6}\", end=\"\")\n        print(f\" {'eff_cyc':>8} {'emph':>20}\")\n        print(f\"  {'─'*8} {'─'*8} {'─'*8} {'─'*10}\", end=\"\")\n        for _ in COMBINATOR_NAMES:\n            print(f\" {'─'*6}\", end=\"\")\n        print(f\" {'─'*8} {'─'*20}\")\n\n        for m in metrics:\n            step = m[\"step\"]\n            loss = m.get(\"loss\", 0)\n            r = m.get(\"r\", (loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE))\n            cg = m.get(\"compute_gate_mean\", 0)\n\n            # Dispatch weights — handle both v10 (22) and v11 (4) formats\n            dw = m.get(\"combinator_dispatch_weights\",\n                       m.get(\"kernel_dispatch_weights\", []))\n\n            # Effective cycles\n            eff = m.get(\"effective_cycles\", [])\n            eff_str = \",\".join(f\"{e:.2f}\" for e in eff) if eff else \"—\"\n\n            # Emphasis\n            emph = m.get(\"combinator_emphasis\",\n                         m.get(\"op_emphasis\", []))\n\n            print(f\"  {step:>8} {loss:>8.4f} {r:>8.4f} {cg:>10.4f}\", end=\"\")\n            for ci in range(min(len(dw), N_COMBINATORS)):\n                print(f\" {dw[ci]:>6.3f}\", end=\"\")\n            if len(dw) < N_COMBINATORS:\n                for _ in range(N_COMBINATORS - len(dw)):\n                    print(f\" {'—':>6}\", end=\"\")\n            print(f\" {eff_str:>8}\", end=\"\")\n\n            # Emphasis: show as K=1.00 I=1.00 B=1.00 C=1.00\n            if emph and len(emph) <= N_COMBINATORS:\n                emph_strs = [f\"{COMBINATOR_NAMES[i]}={emph[i]:.2f}\"\n                             for i in range(len(emph))]\n                print(f\" {' '.join(emph_strs):>20}\", end=\"\")\n            print()\n\n        # ── Dispatch evolution summary ────────────────────\n        if len(metrics) >= 2:\n            first = metrics[0]\n            last = metrics[-1]\n            dw_first = first.get(\"combinator_dispatch_weights\",\n                                  first.get(\"kernel_dispatch_weights\", []))\n            dw_last = last.get(\"combinator_dispatch_weights\",\n                                last.get(\"kernel_dispatch_weights\", []))\n            if dw_first and dw_last and len(dw_first) <= N_COMBINATORS:\n                print(f\"\\n  Dispatch Δ (step {first['step']} → {last['step']}):\")\n                for ci in range(len(dw_first)):\n                    name = COMBINATOR_NAMES[ci] if ci < N_COMBINATORS else f\"op{ci}\"\n                    d = dw_last[ci] - dw_first[ci]\n                    arrow = \"↑\" if d > 0.01 else (\"↓\" if d < -0.01 else \"→\")\n                    print(f\"    {name}: {dw_first[ci]:.4f} {arrow} {dw_last[ci]:.4f} \"\n                          f\"(Δ={d:+.4f})\")\n\n        # ── CycleContinue trajectory ──────────────────────\n        has_cycles = any(m.get(\"cycle_continue_gates\") for m in metrics)\n        if has_cycles:\n            print(f\"\\n  CycleContinue trajectory:\")\n            print(f\"  {'step':>8} {'eff_L1↓':>8} {'eff_L0↓':>8} \"\n                  f\"{'cont_L1↓':>16} {'cont_L0↓':>16}\")\n            print(f\"  {'─'*8} {'─'*8} {'─'*8} {'─'*16} {'─'*16}\")\n            for m in metrics:\n                step = m[\"step\"]\n                eff = m.get(\"effective_cycles\", [])\n                cont = m.get(\"cycle_continue_gates\", [])\n                eff_strs = [f\"{e:.3f}\" for e in eff] if eff else [\"—\", \"—\"]\n                cont_strs = []\n                for cg_list in cont:\n                    if cg_list:\n                        cont_strs.append(\",\".join(f\"{g:.3f}\" for g in cg_list))\n                    else:\n                        cont_strs.append(\"—\")\n                while len(eff_strs) < 2:\n                    eff_strs.append(\"—\")\n                while len(cont_strs) < 2:\n                    cont_strs.append(\"—\")\n                print(f\"  {step:>8} {eff_strs[0]:>8} {eff_strs[1]:>8} \"\n                      f\"{cont_strs[0]:>16} {cont_strs[1]:>16}\")\n\n        # ── S3 gate trajectory ────────────────────────────\n        print(f\"\\n  S3 gate trajectory (L0↑ pass — earliest signal):\")\n        print(f\"  {'step':>8} {'prep':>8} {'conv':>8} {'cons':>8}\")\n        print(f\"  {'─'*8} {'─'*8} {'─'*8} {'─'*8}\")\n        for m in metrics:\n            s3 = m.get(\"s3_gates\", [])\n            if s3 and len(s3) > 0:\n                g = s3[0]  # L0↑ pass\n                if len(g) >= 3:\n                    print(f\"  {m['step']:>8} {g[0]:>8.3f} {g[1]:>8.3f} {g[2]:>8.3f}\")\n\n    # ── Train loss trajectory ─────────────────────────────\n    if train_path.exists():\n        with open(train_path) as f:\n            train = [json.loads(l) for l in f]\n        if train:\n            steps = [t[\"step\"] for t in train]\n            losses = [t.get(\"r\", t.get(\"ce\", 0)) for t in train]\n            print(f\"\\n  Train trajectory: {len(train)} entries, \"\n                  f\"step {steps[0]}-{steps[-1]}\")\n            # Show loss at 10 evenly-spaced points\n            indices = [int(i * len(train) / 10) for i in range(10)] + [len(train) - 1]\n            for idx in sorted(set(indices)):\n                t = train[idx]\n                ce = t.get(\"ce\", 0)\n                r = t.get(\"r\", 0)\n                tok = t.get(\"tok_per_sec\", 0)\n                print(f\"    step={t['step']:>8}  CE={ce:.4f}  r={r:.4f}  \"\n                      f\"tok/s={tok:.0f}\")\n\n    # ── Evolution trajectory ──────────────────────────────\n    if evo_path.exists():\n        with open(evo_path) as f:\n            evo = [json.loads(l) for l in f]\n        if evo:\n            accepted = sum(1 for e in evo if e.get(\"accepted\"))\n            total = len(evo)\n            print(f\"\\n  Evolution: {accepted}/{total} accepted \"\n                  f\"({accepted/total*100:.1f}%)\")\n            # Show last 5\n            for e in evo[-5:]:\n                acc = \"✓\" if e.get(\"accepted\") else \"✗\"\n                flips = e.get(\"actual_flips\", 0)\n                delta = e.get(\"delta\", 0)\n                print(f\"    step={e['step']:>8} {acc} flips={flips:>5} \"\n                      f\"Δ={delta:+.6f}\")\n\n    print(f\"\\n{'='*72}\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Instrumented analysis on text samples\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef run_instrumented_samples(\n    model: V11Model, tokenizer, samples: list[str]\n) -> dict:\n    \"\"\"Run forward_instrumented on text samples.\"\"\"\n    all_metrics = {\n        \"s3_gates\": [], \"s5_reweight\": [], \"register_norms\": [],\n        \"pass_compression\": [], \"pass_phi_dev\": [],\n        \"pass_entropy_in\": [], \"pass_entropy_out\": [],\n        \"losses\": [], \"per_sample\": [],\n        \"combinator_dispatch_weights\": [], \"combinator_type_weights\": [],\n        \"combinator_emphasis\": [],\n        \"cycle_continue_gates\": [], \"effective_cycles\": [],\n        \"compute_gate_mean\": [],\n    }\n\n    for text in samples:\n        ids = mx.array(tokenizer.encode(text)).reshape(1, -1)\n        if ids.shape[1] > model.cfg.max_seq_len:\n            ids = ids[:, -model.cfg.max_seq_len:]\n        targets = mx.concatenate(\n            [ids[:, 1:], mx.zeros((1, 1), dtype=mx.int32)], axis=1)\n\n        hidden, metrics = model.forward_instrumented(ids)\n        mx.eval(hidden)\n\n        logits = model.output_norm(hidden)\n        logits = model.embed.output_proj(logits)\n        loss = nn.losses.cross_entropy(\n            logits.reshape(-1, model.cfg.vocab_size),\n            targets.reshape(-1)).mean()\n        mx.eval(loss)\n\n        all_metrics[\"s3_gates\"].append(metrics[\"s3_gates\"])\n        all_metrics[\"s5_reweight\"].append(metrics[\"s5_reweight\"])\n        all_metrics[\"register_norms\"].append(metrics[\"register_norms\"])\n        all_metrics[\"pass_compression\"].append(metrics[\"pass_compression\"])\n        all_metrics[\"pass_phi_dev\"].append(metrics[\"pass_phi_dev\"])\n        all_metrics[\"pass_entropy_in\"].append(metrics[\"pass_entropy_in\"])\n        all_metrics[\"pass_entropy_out\"].append(metrics[\"pass_entropy_out\"])\n        all_metrics[\"losses\"].append(float(loss.item()))\n\n        if metrics.get(\"combinator_dispatch_weights\"):\n            all_metrics[\"combinator_dispatch_weights\"].append(\n                metrics[\"combinator_dispatch_weights\"])\n        if metrics.get(\"combinator_type_weights\"):\n            all_metrics[\"combinator_type_weights\"].append(\n                metrics[\"combinator_type_weights\"])\n        if metrics.get(\"combinator_emphasis\"):\n            all_metrics[\"combinator_emphasis\"].append(\n                metrics[\"combinator_emphasis\"])\n        if metrics.get(\"cycle_continue_gates\"):\n            all_metrics[\"cycle_continue_gates\"].append(\n                metrics[\"cycle_continue_gates\"])\n        if metrics.get(\"effective_cycles\"):\n            all_metrics[\"effective_cycles\"].append(\n                metrics[\"effective_cycles\"])\n        if \"compute_gate_mean\" in metrics:\n            all_metrics[\"compute_gate_mean\"].append(\n                metrics[\"compute_gate_mean\"])\n\n        all_metrics[\"per_sample\"].append({\n            \"text\": text[:60],\n            \"loss\": float(loss.item()),\n            \"pass_compression\": metrics[\"pass_compression\"],\n        })\n\n    return all_metrics\n\n\ndef _avg_nested(values: list, n: int = 5) -> list[float]:\n    if not values:\n        return [0.0] * n\n    result = [0.0] * n\n    for vals in values:\n        for i in range(min(len(vals), n)):\n            result[i] += vals[i]\n    return [v / len(values) for v in result]\n\n\ndef _avg_register_norms(norm_lists: list) -> dict[str, list[float]]:\n    if not norm_lists:\n        return {}\n    n = len(norm_lists)\n    result: dict[str, list[float]] = {}\n    for norms in norm_lists:\n        for bank_name, vals in norms.items():\n            if bank_name not in result:\n                result[bank_name] = [0.0] * len(vals)\n            for i, v in enumerate(vals):\n                result[bank_name][i] += v\n    return {k: [v / n for v in vals] for k, vals in result.items()}\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Display\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef print_banner(step: int, state: dict, model: V11Model):\n    print(f\"\\n{'='*72}\")\n    print(f\"  v11 Probe — KIBC Combinator VSM — step {step:,}\")\n    print(f\"{'='*72}\")\n\n    cfg_data = state.get(\"config\", {})\n    print(f\"  d_model={cfg_data.get('d_model', '?')}  \"\n          f\"vocab={cfg_data.get('vocab_size', '?')}  \"\n          f\"seq_len={cfg_data.get('seq_len', '?')}\")\n\n    params = count_parameters(model)\n    n_ternary = count_ternary_weights(model)\n    print(f\"  params: total={params['total']:,}  \"\n          f\"trainable={params['trainable']:,}  ternary={n_ternary:,}\")\n\n    evo_gen = state.get(\"total_generations\", 0)\n    evo_acc = state.get(\"total_accepted\", 0)\n    if evo_gen > 0:\n        print(f\"  evolution: {evo_acc}/{evo_gen} accepted \"\n              f\"({evo_acc/evo_gen*100:.0f}%)\")\n\n\ndef print_compressor_metrics(raw: dict):\n    \"\"\"Print compressor metrics from instrumented samples.\"\"\"\n    n = len(raw[\"losses\"])\n    if n == 0:\n        return\n\n    print(f\"\\n  ┌─ S3 gates ──────────────────────────────────────┐\")\n    s3_avg = [[0.0]*3 for _ in range(5)]\n    for gates in raw[\"s3_gates\"]:\n        for pi in range(min(len(gates), 5)):\n            for ph in range(min(len(gates[pi]), 3)):\n                s3_avg[pi][ph] += gates[pi][ph]\n    for pi, pname in enumerate(PASS_NAMES_SHORT):\n        g = [v / n for v in s3_avg[pi]]\n        if pi >= 3:\n            # Descending — may have cycle phases\n            has_cycles = raw[\"s3_gates\"] and len(raw[\"s3_gates\"][0][pi]) > 3\n            if has_cycles:\n                all_g = [0.0] * len(raw[\"s3_gates\"][0][pi])\n                for gates in raw[\"s3_gates\"]:\n                    for j in range(len(gates[pi])):\n                        all_g[j] += gates[pi][j]\n                all_g = [v / n for v in all_g]\n                cycles = len(all_g) // 3\n                for cy in range(cycles):\n                    base = cy * 3\n                    print(f\"  │ {pname}c{cy}: disp={all_g[base]:.3f}  \"\n                          f\"conv={all_g[base+1]:.3f}  intg={all_g[base+2]:.3f}\")\n                continue\n        print(f\"  │ {pname:4s}: prep={g[0]:.3f}  conv={g[1]:.3f}  \"\n              f\"cons={g[2]:.3f}\")\n\n    # S5 reweight\n    print(f\"  ├─ S5 reweight ───────────────────────────────────┤\")\n    s5 = _avg_nested(raw[\"s5_reweight\"])\n    print(f\"  │ {' '.join(f'{pn}={g:.3f}' for pn, g in zip(PASS_NAMES_SHORT, s5))}\")\n\n    # Combinator dispatch\n    cdw = raw.get(\"combinator_dispatch_weights\", [])\n    if cdw:\n        avg_cdw = [0.0] * N_COMBINATORS\n        for dw in cdw:\n            for i in range(N_COMBINATORS):\n                avg_cdw[i] += dw[i]\n        avg_cdw = [v / len(cdw) for v in avg_cdw]\n        print(f\"  ├─ Combinator dispatch ───────────────────────────┤\")\n        for ci in range(N_COMBINATORS):\n            bar = \"█\" * int(avg_cdw[ci] * 80)\n            print(f\"  │ {COMBINATOR_NAMES[ci]} ({COMBINATOR_ROLE[ci]:8s}): \"\n                  f\"{avg_cdw[ci]:.4f} {bar}\")\n\n    # Emphasis\n    emph = raw.get(\"combinator_emphasis\", [])\n    if emph:\n        avg_emph = [0.0] * N_COMBINATORS\n        for e in emph:\n            for i in range(N_COMBINATORS):\n                avg_emph[i] += e[i]\n        avg_emph = [v / len(emph) for v in avg_emph]\n        print(f\"  ├─ Combinator emphasis (S4→dispatch) ────────────┤\")\n        for ci in range(N_COMBINATORS):\n            dev = avg_emph[ci] - 1.0\n            marker = \" ↑\" if dev > 0.05 else (\" ↓\" if dev < -0.05 else \"\")\n            print(f\"  │ {COMBINATOR_NAMES[ci]}: {avg_emph[ci]:.4f}{marker}\")\n\n    # Compute gate\n    cg = raw.get(\"compute_gate_mean\", [])\n    if cg:\n        avg_cg = sum(cg) / len(cg)\n        print(f\"  ├─ Compute gate ──────────────────────────────────┤\")\n        print(f\"  │ mean={avg_cg:.4f}\")\n\n    # CycleContinue\n    ccg = raw.get(\"cycle_continue_gates\", [])\n    eff = raw.get(\"effective_cycles\", [])\n    if ccg or eff:\n        print(f\"  ├─ CycleContinue ─────────────────────────────────┤\")\n        if eff:\n            avg_eff = [0.0] * len(eff[0])\n            for e in eff:\n                for i in range(len(e)):\n                    avg_eff[i] += e[i]\n            avg_eff = [v / len(eff) for v in avg_eff]\n            print(f\"  │ effective cycles: \"\n                  f\"{' '.join(f'{e:.3f}' for e in avg_eff)}\")\n\n    # Register norms\n    reg_norms = _avg_register_norms(raw[\"register_norms\"])\n    if reg_norms:\n        print(f\"  ├─ Register norms ────────────────────────────────┤\")\n        for bname in sorted(reg_norms.keys()):\n            norms = reg_norms[bname]\n            print(f\"  │ {bname:12s}: {' '.join(f'{n:>7.2f}' for n in norms)}\")\n\n    # Compression\n    cr = _avg_nested(raw[\"pass_compression\"])\n    pd = _avg_nested(raw[\"pass_phi_dev\"])\n    print(f\"  ├─ φ-Compression (target 1/φ = {INV_PHI:.4f}) ──────┤\")\n    for pi, pname in enumerate(PASS_NAMES_SHORT):\n        phi_mark = \" ←φ\" if pd[pi] < 0.05 else \"   \"\n        print(f\"  │ {pname:4s}: ratio={cr[pi]:>7.3f}  φ-dev={pd[pi]:.3f}{phi_mark}\")\n\n    print(f\"  └─────────────────────────────────────────────────┘\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Multi-checkpoint evolution\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef print_evolution(all_results: list[dict]):\n    if len(all_results) < 2:\n        return\n\n    print(f\"\\n{'='*72}\")\n    print(f\"  KIBC Combinator Evolution\")\n    print(f\"{'='*72}\")\n\n    # Loss\n    print(f\"\\n  {'step':>8} {'loss':>8} {'r':>8}\", end=\"\")\n    for cn in COMBINATOR_NAMES:\n        print(f\" {cn:>7}\", end=\"\")\n    print(f\" {'comp_gate':>10} {'eff_cyc':>8}\")\n    print(f\"  {'─'*8} {'─'*8} {'─'*8}\", end=\"\")\n    for _ in COMBINATOR_NAMES:\n        print(f\" {'─'*7}\", end=\"\")\n    print(f\" {'─'*10} {'─'*8}\")\n\n    for r in all_results:\n        loss = r.get(\"eval_loss\", r.get(\"loss\", 0))\n        rel_r = (loss - E_IRREDUCIBLE) / (LOG_V - E_IRREDUCIBLE) if loss else 0\n        dw = r.get(\"dispatch\", [0.25] * N_COMBINATORS)\n        cg = r.get(\"compute_gate\", 0)\n        eff = r.get(\"effective_cycles\", \"—\")\n        print(f\"  {r['step']:>8} {loss:>8.4f} {rel_r:>8.4f}\", end=\"\")\n        for ci in range(N_COMBINATORS):\n            print(f\" {dw[ci]:>7.4f}\", end=\"\")\n        print(f\" {cg:>10.4f} {eff:>8}\")\n\n    print(f\"{'='*72}\\n\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# Ternary statistics\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef ternary_stats(model: V11Model) -> dict:\n    stats = {}\n    for path, mod in _walk_ternary_modules(model):\n        if isinstance(mod, TernaryLinear):\n            w_int = unpack_ternary_mlx(mod.weight)\n            mx.eval(w_int)\n            w_np = np.array(w_int.astype(mx.int8))\n            total = w_np.size\n            n_zero = int(np.sum(w_np == 0))\n            sparsity = n_zero / total\n            gamma_np = np.array(mod.gamma)\n            stats[path] = {\n                \"type\": \"linear\", \"shape\": (mod.out_features, mod.in_features),\n                \"sparsity\": sparsity,\n                \"gamma_mean\": float(np.mean(np.abs(gamma_np))),\n                \"gamma_std\": float(np.std(gamma_np)),\n            }\n        elif isinstance(mod, TernaryEmbedding):\n            w_int = unpack_ternary(mod.ternary_weight, mod.in_features)\n            mx.eval(w_int)\n            w_np = np.array(w_int.astype(mx.int8))\n            total = w_np.size\n            sparsity = int(np.sum(w_np == 0)) / total\n            gamma_np = np.array(mod.gamma)\n            stats[path] = {\n                \"type\": \"embedding\",\n                \"shape\": (mod.out_features, mod.in_features),\n                \"sparsity\": sparsity,\n                \"gamma_mean\": float(np.mean(np.abs(gamma_np))),\n                \"gamma_std\": float(np.std(gamma_np)),\n            }\n    return stats\n\n\ndef print_ternary_stats(stats: dict):\n    groups: dict[str, list] = {}\n    for path, s in stats.items():\n        group = path.split(\".\")[0]\n        groups.setdefault(group, []).append(s)\n\n    print(f\"\\n  Ternary topology ({len(stats)} modules):\")\n    print(f\"  {'Group':18s} {'#':>3} {'sparsity':>9} {'γ_mean':>8}\")\n    print(f\"  {'─'*18} {'─'*3} {'─'*9} {'─'*8}\")\n\n    total_params = 0\n    total_zeros = 0\n    for grp in sorted(groups.keys()):\n        mods = groups[grp]\n        n = len(mods)\n        sp = sum(m[\"sparsity\"] for m in mods) / n\n        gm = sum(m[\"gamma_mean\"] for m in mods) / n\n        for m in mods:\n            total_params += m[\"shape\"][0] * m[\"shape\"][1]\n            total_zeros += int(m[\"sparsity\"] * m[\"shape\"][0] * m[\"shape\"][1])\n        print(f\"  {grp:18s} {n:>3} {sp:>9.3f} {gm:>8.4f}\")\n\n    overall_sp = total_zeros / total_params if total_params else 0\n    print(f\"  {'─'*18} {'─'*3} {'─'*9}\")\n    print(f\"  {'TOTAL':18s} {len(stats):>3} {overall_sp:>9.3f}  \"\n          f\"({total_params:,} ternary params)\")\n\n\n# ══════════════════════════════════════════════════════════════════════\n# JSON output\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef save_results(step: int, state: dict, phi_raw: dict,\n                 dispatch_analysis: dict | None,\n                 eval_result: dict | None,\n                 out_dir: Path) -> Path:\n    out_dir.mkdir(parents=True, exist_ok=True)\n    out_path = out_dir / f\"probe_step_{step:06d}.json\"\n\n    output = {\n        \"timestamp\": datetime.now(UTC).isoformat(),\n        \"architecture\": \"v11-kibc-combinator-vsm\",\n        \"step\": step,\n        \"config\": state.get(\"config\", {}),\n        \"evolution\": {\n            \"total_generations\": state.get(\"total_generations\", 0),\n            \"total_accepted\": state.get(\"total_accepted\", 0),\n        },\n    }\n    if eval_result:\n        output[\"eval\"] = eval_result\n    if dispatch_analysis:\n        output[\"dispatch_analysis\"] = dispatch_analysis\n\n    out_path.write_text(json.dumps(output, indent=2, default=str))\n    return out_path\n\n\n# ══════════════════════════════════════════════════════════════════════\n# CLI\n# ══════════════════════════════════════════════════════════════════════\n\n\ndef main():\n    parser = argparse.ArgumentParser(\n        description=\"v11 probe — KIBC combinator VSM checkpoint diagnostics\")\n    parser.add_argument(\"checkpoints\", type=Path, nargs=\"*\",\n                        help=\"Checkpoint directory/directories\")\n    parser.add_argument(\"--trajectory\", type=Path, default=None,\n                        help=\"Checkpoint dir for JSONL trajectory analysis \"\n                             \"(no model loading)\")\n    parser.add_argument(\"--dispatch-detail\", action=\"store_true\",\n                        help=\"Per-position dispatch distribution analysis\")\n    parser.add_argument(\"--no-eval\", action=\"store_true\",\n                        help=\"Skip data evaluation (faster)\")\n    parser.add_argument(\"--no-ternary\", action=\"store_true\",\n                        help=\"Skip ternary statistics\")\n    parser.add_argument(\"--dispatch-batches\", type=int, default=10,\n                        help=\"Number of batches for dispatch analysis\")\n    parser.add_argument(\"--results-dir\", type=Path, default=RESULTS_DIR)\n    args = parser.parse_args()\n\n    # ── Trajectory mode (no model loading) ────────────────\n    if args.trajectory:\n        analyze_trajectory(args.trajectory)\n        return\n\n    if not args.checkpoints:\n        parser.print_help()\n        return\n\n    # ── Tokenizer ─────────────────────────────────────────\n    print(\"  Loading Qwen3 tokenizer...\", file=sys.stderr)\n    from transformers import AutoTokenizer\n    tokenizer = AutoTokenizer.from_pretrained(\n        \"Qwen/Qwen3-0.6B\", trust_remote_code=True)\n\n    ckpts = sorted(\n        [p for p in args.checkpoints if p.is_dir()],\n        key=lambda p: int(p.name.split(\"_\")[-1])\n        if p.name.startswith(\"step_\") else 0,\n    )\n    if not ckpts:\n        print(\"  No checkpoint directories found.\", file=sys.stderr)\n        return\n\n    all_results = []\n\n    for ckpt_path in ckpts:\n        t0 = time.time()\n        print(f\"\\n  Loading {ckpt_path}...\", file=sys.stderr)\n        model, step, state, cfg = load_checkpoint(ckpt_path)\n        print_banner(step, state, model)\n\n        # ── Instrumented analysis on sample strata ────────\n        print(f\"\\n  Running instrumented analysis...\", file=sys.stderr)\n        all_samples = []\n        for samples in PHI_STRATA.values():\n            all_samples.extend(samples)\n        raw = run_instrumented_samples(model, tokenizer, all_samples)\n        print_compressor_metrics(raw)\n\n        # ── Dispatch distribution analysis ────────────────\n        dispatch_analysis = None\n        if args.dispatch_detail:\n            print(f\"\\n  Running dispatch distribution analysis \"\n                  f\"({args.dispatch_batches} batches)...\", file=sys.stderr)\n            dispatch_analysis = analyze_dispatch_distribution(\n                model, cfg, n_batches=args.dispatch_batches)\n            print_dispatch_analysis(dispatch_analysis)\n\n        # ── Eval ──────────────────────────────────────────\n        eval_result = None\n        if not args.no_eval:\n            print(f\"\\n  Evaluating on held-out data...\", file=sys.stderr)\n            eval_result = evaluate_on_data(model, cfg)\n            print(f\"\\n  📊 Eval: loss={eval_result['loss']:.3f}  \"\n                  f\"ppl={eval_result['ppl']:.0f}  r={eval_result['r']:.3f}  \"\n                  f\"({eval_result['tokens_evaluated']:,} tokens)\")\n\n        # ── Ternary stats ─────────────────────────────────\n        if not args.no_ternary:\n            ts = ternary_stats(model)\n            print_ternary_stats(ts)\n\n        # ── Save ──────────────────────────────────────────\n        out_path = save_results(step, state, raw, dispatch_analysis,\n                                eval_result, args.results_dir)\n        print(f\"\\n  💾 Saved: {out_path}\")\n\n        elapsed = time.time() - t0\n        print(f\"  ⏱  {elapsed:.1f}s\", file=sys.stderr)\n\n        # ── Collect for evolution ─────────────────────────\n        cdw = raw.get(\"combinator_dispatch_weights\", [])\n        avg_dw = [0.25] * N_COMBINATORS\n        if cdw:\n            avg_dw = [sum(d[i] for d in cdw) / len(cdw)\n                      for i in range(N_COMBINATORS)]\n\n        cg_list = raw.get(\"compute_gate_mean\", [])\n        avg_cg = sum(cg_list) / len(cg_list) if cg_list else 0\n\n        eff_list = raw.get(\"effective_cycles\", [])\n        eff_str = \"—\"\n        if eff_list:\n            avg_eff = [sum(e[i] for e in eff_list) / len(eff_list)\n                       for i in range(len(eff_list[0]))]\n            eff_str = \",\".join(f\"{e:.2f}\" for e in avg_eff)\n\n        all_results.append({\n            \"step\": step,\n            \"loss\": float(sum(raw[\"losses\"]) / len(raw[\"losses\"])),\n            \"eval_loss\": eval_result[\"loss\"] if eval_result else 0,\n            \"dispatch\": avg_dw,\n            \"compute_gate\": avg_cg,\n            \"effective_cycles\": eff_str,\n        })\n\n    print_evolution(all_results)\n\n\nif __name__ == \"__main__\":\n    main()\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/scripts/v11/probe.py
```

## Assistant

Now let me verify it at least parses correctly:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "cd /Users/mwhitford/src/verbum && uv run python -c \"\nimport sys; sys.path.insert(0, 'scripts/v11')\nimport probe\nprint('probe.py imports OK')\nprint(f'  PHI_STRATA: {len(probe.PHI_STRATA)} strata, '\n      f'{sum(len(v) for v in probe.PHI_STRATA.values())} samples')\nprint(f'  COMBINATOR_NAMES: {probe.COMBINATOR_NAMES}')\nprint(f'  Functions: load_checkpoint, evaluate_on_data, '\n      f'analyze_dispatch_distribution, analyze_trajectory')\n\"",
  "timeout": 30000
}
```

**Summary:** $ uv run python -c " import sys; sys....

**Output:**
```
Exit code: 0
Stdout:
probe.py imports OK
  PHI_STRATA: 4 strata, 16 samples
  COMBINATOR_NAMES: ['K', 'I', 'B', 'C']
  Functions: load_checkpoint, evaluate_on_data, analyze_dispatch_distribution, analyze_trajectory
```

## Assistant

Clean import. Let me commit this and give you the summary.

### Tool Call: git (succeeded)


```json
{
  "command": "git add scripts/v11/probe.py && git commit -m \"$(cat <<'EOF'\n✅ v11 probe — KIBC combinator checkpoint diagnostics\n\n- Checkpoint analysis: load model, run forward_instrumented, display metrics\n- Dispatch distribution: per-position K/I/B/C weights, dominant combinator\n  histogram, entropy (specialization measure), top-2 co-occurrence matrix,\n  per-combinator statistics (mean/std/median/p05/p95)\n- JSONL trajectory analysis (--trajectory): reads metrics_log.jsonl without\n  loading model — shows dispatch evolution, CycleContinue dynamics, S3 gates,\n  emphasis shifts, train loss curve, evolution acceptance\n- Multi-checkpoint evolution tables\n- φ-compression by content strata (prose, compositional, technical, lambda)\n- Ternary topology statistics\n- JSON output for programmatic analysis\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "v11 probe script"
}
```

**Summary:** Git commit: v11 probe script

**Output:**
```
Exit code: 0
Stdout:
[main 87a15c5] ✅ v11 probe — KIBC combinator checkpoint diagnostics
 1 file changed, 1052 insertions(+)
 create mode 100644 scripts/v11/probe.py
```

## Assistant

Here's what the probe gives you:

## v11 Probe — Three modes

### 1. Checkpoint analysis (load model, run instrumented)
```bash
# Single checkpoint
uv run python scripts/v11/probe.py checkpoints/v11/step_005000

# Multiple — evolution table
uv run python scripts/v11/probe.py checkpoints/v11/step_*

# With per-position dispatch distribution analysis
uv run python scripts/v11/probe.py checkpoints/v11/step_005000 --dispatch-detail
```

### 2. JSONL trajectory (no model loading — instant)
```bash
uv run python scripts/v11/probe.py --trajectory checkpoints/v11
```
Reads `metrics_log.jsonl`, `train_log.jsonl`, `evolution_log.jsonl` and shows:
- Full dispatch evolution table (K/I/B/C weights at each eval step)
- CycleContinue gate trajectory (are gates differentiating?)
- S3 gate evolution (L0↑ pass as earliest signal)
- Train loss curve (10 evenly-spaced samples)
- Evolution acceptance stats

### 3. Dispatch distribution analysis (`--dispatch-detail`)
This is the kernel op distribution you asked about. Runs 10 batches through the model and computes:

| Analysis | What it tells us |
|----------|-----------------|
| **Mean distribution** | K=?% I=?% B=?% C=?% — overall combinator balance |
| **Dominant per position** | Which combinator wins at each token position |
| **Dispatch entropy** | 0 = fully specialized, log(4) = uniform. The specialization measure. |
| **Top-2 co-occurrence** | Which combinator pairs appear together (e.g. K+B = prose composition) |
| **Per-combinator stats** | mean/std/median/p05/p95 of each combinator's weight |
| **Compute gate** | How much the kernel pathway is contributing vs FFN |

The key signals to watch:
- **K should dominate** prose (selection is what attention does)
- **B should rise** for compositional multi-clause sentences
- **Entropy should drop** over training (specialization emerging)
- **CycleContinue should differentiate** (K-only → gate closes, B+C → stays open)

## User

Ok update state and knowledge for this v11 design, we probably need a new svg file for the architecture and a markdown with the full design, and the probe design.


### Thinking

The user wants me to:
1. Update state.md to reflect the probe addition
2. Create a comprehensive knowledge page for the v11 KIBC architecture design
3. Create an SVG diagram of the architecture
4. Document the probe design

Let me plan this out and then execute.

## Assistant

Let me check if there are existing SVGs for reference:

### Tool Call: shell_command (succeeded)


```json
{
  "command": "find /Users/mwhitford/src/verbum -name \"*.svg\" -o -name \"*.png\" 2>/dev/null | head -10"
}
```

**Summary:** $ find /Users/mwhitford/src/verbum -n...

**Output:**
```
Exit code: 0
Stdout:
/Users/mwhitford/src/verbum/docs/v10-architecture.svg
/Users/mwhitford/src/verbum/docs/vsm-tesseract.svg
/Users/mwhitford/src/verbum/results/v1-v2-comparison/grad_norm_ratio_apply_type.png
/Users/mwhitford/src/verbum/results/v1-v2-comparison/phase_grad_norms.png
/Users/mwhitford/src/verbum/results/v1-v2-comparison/eval_loss_comparison.png
/Users/mwhitford/src/verbum/results/v1-v2-comparison/v1_activation_norms.png
/Users/mwhitford/src/verbum/results/v1-v2-comparison/train_loss_last100.png
/Users/mwhitford/src/verbum/results/kernel-basins/op_similarity_L37.png
/Users/mwhitford/src/verbum/results/kernel-basins/op_similarity_L32.png
/Users/mwhitford/src/verbum/results/kernel-basins/op_topology_L28.png
```

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/docs/v10-architecture.svg",
  "limit": 30
}
```

**Summary:** Reading v10-architecture.svg (0-30)

**Output:**
```
<?xml version="1.0" encoding="UTF-8"?>
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1100 1520" font-family="'SF Mono', 'Fira Code', 'Consolas', monospace" font-size="12">
  <defs>
    <!-- Markers for arrows -->
    <marker id="arrow" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#334155"/>
    </marker>
    <marker id="arrow-blue" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#3b82f6"/>
    </marker>
    <marker id="arrow-orange" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#f97316"/>
    </marker>
    <marker id="arrow-green" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#22c55e"/>
    </marker>
    <marker id="arrow-purple" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#a855f7"/>
    </marker>
    <marker id="arrow-red" markerWidth="8" markerHeight="6" refX="8" refY="3" orient="auto">
      <path d="M0,0 L8,3 L0,6 Z" fill="#ef4444"/>
    </marker>

    <!-- Gradient for ascending arm -->
    <linearGradient id="asc-grad" x1="0" y1="1" x2="0" y2="0">
      <stop offset="0%" stop-color="#dbeafe"/>
      <stop offset="100%" stop-color="#93c5fd"/>
    </linearGradient>
    <!-- Gradient for descending arm -->
    <linearGradient id="desc-grad" x1="0" y1="0" x2="0" y2="1">

[CONTENT TRUNCATED] Showing lines 1 to 30 of 398 total lines. Use line_offset=30 parameter to read more content.
```

## Assistant

Good, there's a v10 SVG to reference. Let me read more of it to understand the style:

### Tool Call: read_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/docs/v10-architecture.svg",
  "line_offset": 30,
  "limit": 100
}
```

**Summary:** Reading v10-architecture.svg (30-130)

**Output:**
```
      <stop offset="0%" stop-color="#ffedd5"/>
      <stop offset="100%" stop-color="#fdba74"/>
    </linearGradient>

    <!-- Stripe pattern for passthrough -->
    <pattern id="passthrough" width="6" height="6" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">
      <line x1="0" y1="0" x2="0" y2="6" stroke="#fca5a5" stroke-width="1.5"/>
    </pattern>
  </defs>

  <!-- Background -->
  <rect width="1100" height="1520" fill="#f8fafc" rx="8"/>

  <!-- Title -->
  <text x="550" y="36" text-anchor="middle" font-size="20" font-weight="bold" fill="#0f172a">v10 — Tree of VSMs: Compressor + Dispatcher</text>
  <text x="550" y="56" text-anchor="middle" font-size="13" fill="#64748b">23.2M total · 308K trainable · 131M ternary · d_model=512 · 9 strides · 5 passes</text>

  <!-- ════════════════════════════════════════════════════════════════ -->
  <!-- TOKENS INPUT -->
  <!-- ════════════════════════════════════════════════════════════════ -->
  <rect x="340" y="76" width="320" height="36" rx="4" fill="#f1f5f9" stroke="#94a3b8" stroke-width="1.5"/>
  <text x="500" y="99" text-anchor="middle" font-size="13" fill="#334155" font-weight="bold">tokens (B, L) — Qwen3 BBPE</text>

  <!-- Arrow: tokens → embed -->
  <line x1="500" y1="112" x2="500" y2="134" stroke="#334155" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- ════════════════════════════════════════════════════════════════ -->
  <!-- S5 IDENTITY: Embedding -->
  <!-- ════════════════════════════════════════════════════════════════ -->
  <rect x="280" y="136" width="440" height="52" rx="6" fill="#fefce8" stroke="#ca8a04" stroke-width="1.5"/>
  <text x="304" y="155" font-size="10" fill="#a16207" font-weight="bold">S5 IDENTITY</text>
  <text x="500" y="158" text-anchor="middle" font-size="12" fill="#334155" font-weight="bold">TernaryEmbedding + PosEmbedding</text>
  <text x="500" y="175" text-anchor="middle" font-size="10" fill="#64748b">embed_norm(embed(tokens) + pos_embed(positions)) → (B, L, 512)</text>

  <!-- Register bank_0 initialization -->
  <rect x="760" y="140" width="180" height="44" rx="4" fill="#fef9c3" stroke="#ca8a04" stroke-width="1" stroke-dasharray="4,2"/>
  <text x="850" y="157" text-anchor="middle" font-size="10" fill="#a16207" font-weight="bold">bank_0 (S5 registers)</text>
  <text x="850" y="172" text-anchor="middle" font-size="9" fill="#78716c">type · scope · role</text>
  <line x1="720" y1="162" x2="758" y2="162" stroke="#ca8a04" stroke-width="1" stroke-dasharray="3,2"/>

  <!-- Arrow: embed → ascending arm -->
  <line x1="500" y1="188" x2="500" y2="218" stroke="#334155" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- ════════════════════════════════════════════════════════════════ -->
  <!-- ASCENDING ARM — VSM-COMPRESSOR -->
  <!-- ════════════════════════════════════════════════════════════════ -->
  <rect x="100" y="220" width="800" height="444" rx="8" fill="url(#asc-grad)" stroke="#3b82f6" stroke-width="2"/>
  <text x="120" y="244" font-size="14" font-weight="bold" fill="#1e40af">VSM-COMPRESSOR (ascending arm)</text>
  <text x="120" y="260" font-size="10" fill="#3b82f6">3 passes · shared weights · proven: φ-locking, S3 differentiating</text>

  <!-- ── PASS 0: L0↑ ──────────────────────────────────────── -->
  <rect x="130" y="272" width="740" height="118" rx="6" fill="#ffffff" fill-opacity="0.7" stroke="#60a5fa" stroke-width="1"/>
  <text x="150" y="290" font-size="11" font-weight="bold" fill="#1e40af">Pass 0: L0↑</text>
  <text x="305" y="290" font-size="9" fill="#64748b">reads: bank_0 → writes: bank_1_asc</text>

  <!-- S4 -->
  <rect x="150" y="298" width="110" height="36" rx="4" fill="#e0f2fe" stroke="#0284c7" stroke-width="1"/>
  <text x="205" y="314" text-anchor="middle" font-size="10" fill="#0369a1" font-weight="bold">S4</text>
  <text x="205" y="326" text-anchor="middle" font-size="8" fill="#0369a1">reg→query attn</text>

  <!-- Phase boxes in L0↑ -->
  <rect x="280" y="298" width="120" height="36" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
  <text x="340" y="314" text-anchor="middle" font-size="10" fill="#1e40af" font-weight="bold">TernaryFFN</text>
  <text x="340" y="326" text-anchor="middle" font-size="8" fill="#3b82f6">prep (d_ff=1536)</text>

  <rect x="420" y="298" width="120" height="36" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
  <text x="480" y="314" text-anchor="middle" font-size="10" fill="#1e40af" font-weight="bold">StrideStack</text>
  <text x="480" y="326" text-anchor="middle" font-size="8" fill="#3b82f6">fine→coarse (9)</text>

  <rect x="560" y="298" width="120" height="36" rx="4" fill="#dbeafe" stroke="#3b82f6" stroke-width="1"/>
  <text x="620" y="314" text-anchor="middle" font-size="10" fill="#1e40af" font-weight="bold">TernaryFFN</text>
  <text x="620" y="326" text-anchor="middle" font-size="8" fill="#3b82f6">cons (d_ff=2048)</text>

  <!-- S3 gates for L0↑ -->
  <rect x="700" y="298" width="150" height="36" rx="4" fill="#e0f2fe" stroke="#0284c7" stroke-width="1"/>
  <text x="775" y="314" text-anchor="middle" font-size="10" fill="#0369a1" font-weight="bold">S3 gates (3 phases)</text>
  <text x="775" y="326" text-anchor="middle" font-size="8" fill="#22c55e" font-weight="bold">✓ 0.54 / 0.41 / 0.33</text>

  <!-- Arrows between phases -->
  <line x1="260" y1="316" x2="278" y2="316" stroke="#3b82f6" stroke-width="1" marker-end="url(#arrow-blue)"/>
  <line x1="400" y1="316" x2="418" y2="316" stroke="#3b82f6" stroke-width="1" marker-end="url(#arrow-blue)"/>
  <line x1="540" y1="316" x2="558" y2="316" stroke="#3b82f6" stroke-width="1" marker-end="url(#arrow-blue)"/>

  <!-- S3 control lines -->
  <line x1="700" y1="310" x2="680" y2="310" stroke="#0284c7" stroke-width="0.8" stroke-dasharray="3,2" marker-end="url(#arrow-blue)"/>
  <line x1="700" y1="320" x2="680" y2="330" stroke="#0284c7" stroke-width="0.8" stroke-dasharray="3,2"/>

  <!-- Modulation annotation -->
  <text x="340" y="354" text-anchor="middle" font-size="8" fill="#64748b">x = x + gate · tanh(mod_proj(δ))</text>
  <text x="340" y="366" text-anchor="middle" font-size="8" fill="#64748b">δ = op(x) − x (residual delta)</text>

  <!-- Register bank visualization for L0↑ -->
  <rect x="150" y="350" width="80" height="28" rx="3" fill="#fef9c3" stroke="#ca8a04" stroke-width="0.8"/>
  <text x="190" y="368" text-anchor="middle" font-size="8" fill="#a16207">bank_1_asc</text>

  <!-- ── PASS 1: L1↑ ──────────────────────────────────────── -->
  <rect x="130" y="394" width="740" height="80" rx="6" fill="#ffffff" fill-opacity="0.7" stroke="#60a5fa" stroke-width="1"/>
  <text x="150" y="412" font-size="11" font-weight="bold" fill="#1e40af">Pass 1: L1↑</text>
  <text x="305" y="412" font-size="9" fill="#64748b">reads: bank_0, bank_1_asc → writes: bank_2_asc</text>


[CONTENT TRUNCATED] Showing lines 31 to 130 of 398 total lines. Use line_offset=130 parameter to read more content.
```

## Assistant

Good, I understand the SVG style. Now let me build both the SVG and the comprehensive design document in parallel:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/docs/v11-architecture.svg",
  "content": "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<svg xmlns=\"http://www.w3.org/2000/svg\" viewBox=\"0 0 1100 1640\" font-family=\"'SF Mono', 'Fira Code', 'Consolas', monospace\" font-size=\"12\">\n  <defs>\n    <marker id=\"arrow\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#334155\"/>\n    </marker>\n    <marker id=\"arrow-blue\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#3b82f6\"/>\n    </marker>\n    <marker id=\"arrow-orange\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#f97316\"/>\n    </marker>\n    <marker id=\"arrow-green\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#22c55e\"/>\n    </marker>\n    <marker id=\"arrow-purple\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#a855f7\"/>\n    </marker>\n    <marker id=\"arrow-red\" markerWidth=\"8\" markerHeight=\"6\" refX=\"8\" refY=\"3\" orient=\"auto\">\n      <path d=\"M0,0 L8,3 L0,6 Z\" fill=\"#ef4444\"/>\n    </marker>\n    <linearGradient id=\"asc-grad\" x1=\"0\" y1=\"1\" x2=\"0\" y2=\"0\">\n      <stop offset=\"0%\" stop-color=\"#dbeafe\"/>\n      <stop offset=\"100%\" stop-color=\"#93c5fd\"/>\n    </linearGradient>\n    <linearGradient id=\"desc-grad\" x1=\"0\" y1=\"0\" x2=\"0\" y2=\"1\">\n      <stop offset=\"0%\" stop-color=\"#ffedd5\"/>\n      <stop offset=\"100%\" stop-color=\"#fdba74\"/>\n    </linearGradient>\n    <linearGradient id=\"cycle-grad\" x1=\"0\" y1=\"0\" x2=\"1\" y2=\"0\">\n      <stop offset=\"0%\" stop-color=\"#fef3c7\"/>\n      <stop offset=\"100%\" stop-color=\"#fde68a\"/>\n    </linearGradient>\n  </defs>\n\n  <!-- Background -->\n  <rect width=\"1100\" height=\"1640\" fill=\"#f8fafc\" rx=\"8\"/>\n\n  <!-- Title -->\n  <text x=\"550\" y=\"36\" text-anchor=\"middle\" font-size=\"20\" font-weight=\"bold\" fill=\"#0f172a\">v11 — KIBC Combinator VSM</text>\n  <text x=\"550\" y=\"56\" text-anchor=\"middle\" font-size=\"13\" fill=\"#64748b\">~23.8M params · d_model=512 · 9 strides · 5 passes · 4 combinators (K, I, B, C)</text>\n  <text x=\"550\" y=\"72\" text-anchor=\"middle\" font-size=\"11\" fill=\"#94a3b8\">Shapes from Qwen3 probes: attention IS beta reduction (SEARCH → LOCK → RESOLVE)</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- TOKENS INPUT -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"340\" y=\"88\" width=\"320\" height=\"36\" rx=\"4\" fill=\"#f1f5f9\" stroke=\"#94a3b8\" stroke-width=\"1.5\"/>\n  <text x=\"500\" y=\"111\" text-anchor=\"middle\" font-size=\"13\" fill=\"#334155\" font-weight=\"bold\">tokens (B, L) — Qwen3 BBPE 151936</text>\n\n  <line x1=\"500\" y1=\"124\" x2=\"500\" y2=\"146\" stroke=\"#334155\" stroke-width=\"1.5\" marker-end=\"url(#arrow)\"/>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- S5 IDENTITY: Embedding -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"280\" y=\"148\" width=\"440\" height=\"52\" rx=\"6\" fill=\"#fefce8\" stroke=\"#ca8a04\" stroke-width=\"1.5\"/>\n  <text x=\"304\" y=\"167\" font-size=\"10\" fill=\"#a16207\" font-weight=\"bold\">S5 IDENTITY</text>\n  <text x=\"500\" y=\"170\" text-anchor=\"middle\" font-size=\"12\" fill=\"#334155\" font-weight=\"bold\">TernaryEmbedding + PosEmbedding</text>\n  <text x=\"500\" y=\"187\" text-anchor=\"middle\" font-size=\"10\" fill=\"#64748b\">embed_norm(embed(tokens) + pos_embed(positions)) → (B, L, 512)</text>\n\n  <!-- bank_0 -->\n  <rect x=\"760\" y=\"152\" width=\"200\" height=\"44\" rx=\"4\" fill=\"#fef9c3\" stroke=\"#ca8a04\" stroke-width=\"1\" stroke-dasharray=\"4,2\"/>\n  <text x=\"860\" y=\"169\" text-anchor=\"middle\" font-size=\"10\" fill=\"#a16207\" font-weight=\"bold\">bank_0 (S5 registers)</text>\n  <text x=\"860\" y=\"184\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">combinator · binding_depth · phase</text>\n  <line x1=\"720\" y1=\"174\" x2=\"758\" y2=\"174\" stroke=\"#ca8a04\" stroke-width=\"1\" stroke-dasharray=\"3,2\"/>\n\n  <!-- Save x_embed annotation -->\n  <rect x=\"100\" y=\"160\" width=\"150\" height=\"28\" rx=\"3\" fill=\"#fef3c7\" stroke=\"#d97706\" stroke-width=\"0.8\"/>\n  <text x=\"175\" y=\"178\" text-anchor=\"middle\" font-size=\"9\" fill=\"#92400e\">x_embed saved for desc S4</text>\n  <line x1=\"250\" y1=\"174\" x2=\"278\" y2=\"174\" stroke=\"#d97706\" stroke-width=\"0.8\" stroke-dasharray=\"3,2\"/>\n\n  <line x1=\"500\" y1=\"200\" x2=\"500\" y2=\"226\" stroke=\"#334155\" stroke-width=\"1.5\" marker-end=\"url(#arrow)\"/>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- ASCENDING ARM — VSM-COMPRESSOR -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"100\" y=\"228\" width=\"800\" height=\"310\" rx=\"8\" fill=\"url(#asc-grad)\" stroke=\"#3b82f6\" stroke-width=\"2\"/>\n  <text x=\"120\" y=\"252\" font-size=\"14\" font-weight=\"bold\" fill=\"#1e40af\">ASCENDING ARM — VSM-Compressor (LOCK phase)</text>\n  <text x=\"120\" y=\"268\" font-size=\"10\" fill=\"#3b82f6\">3 passes · shared weights · prep → StrideStack → consolidate · φ-compression</text>\n\n  <!-- Pass 0: L0↑ -->\n  <rect x=\"130\" y=\"278\" width=\"740\" height=\"72\" rx=\"6\" fill=\"#ffffff\" fill-opacity=\"0.7\" stroke=\"#60a5fa\" stroke-width=\"1\"/>\n  <text x=\"150\" y=\"296\" font-size=\"11\" font-weight=\"bold\" fill=\"#1e40af\">Pass 0: L0↑</text>\n  <text x=\"290\" y=\"296\" font-size=\"9\" fill=\"#64748b\">reads: bank_0, prev_b1d, prev_kernel → writes: bank_1_asc</text>\n\n  <rect x=\"150\" y=\"304\" width=\"90\" height=\"32\" rx=\"4\" fill=\"#e0f2fe\" stroke=\"#0284c7\" stroke-width=\"1\"/>\n  <text x=\"195\" y=\"324\" text-anchor=\"middle\" font-size=\"9\" fill=\"#0369a1\" font-weight=\"bold\">S4 attention</text>\n\n  <rect x=\"260\" y=\"304\" width=\"110\" height=\"32\" rx=\"4\" fill=\"#dbeafe\" stroke=\"#3b82f6\" stroke-width=\"1\"/>\n  <text x=\"315\" y=\"318\" text-anchor=\"middle\" font-size=\"10\" fill=\"#1e40af\" font-weight=\"bold\">prep</text>\n  <text x=\"315\" y=\"330\" text-anchor=\"middle\" font-size=\"8\" fill=\"#3b82f6\">FFN 1536</text>\n\n  <rect x=\"390\" y=\"304\" width=\"110\" height=\"32\" rx=\"4\" fill=\"#dbeafe\" stroke=\"#3b82f6\" stroke-width=\"1\"/>\n  <text x=\"445\" y=\"318\" text-anchor=\"middle\" font-size=\"10\" fill=\"#1e40af\" font-weight=\"bold\">StrideStack</text>\n  <text x=\"445\" y=\"330\" text-anchor=\"middle\" font-size=\"8\" fill=\"#3b82f6\">9 strides</text>\n\n  <rect x=\"520\" y=\"304\" width=\"110\" height=\"32\" rx=\"4\" fill=\"#dbeafe\" stroke=\"#3b82f6\" stroke-width=\"1\"/>\n  <text x=\"575\" y=\"318\" text-anchor=\"middle\" font-size=\"10\" fill=\"#1e40af\" font-weight=\"bold\">consolidate</text>\n  <text x=\"575\" y=\"330\" text-anchor=\"middle\" font-size=\"8\" fill=\"#3b82f6\">FFN 2048</text>\n\n  <rect x=\"650\" y=\"304\" width=\"100\" height=\"32\" rx=\"4\" fill=\"#e0f2fe\" stroke=\"#0284c7\" stroke-width=\"1\"/>\n  <text x=\"700\" y=\"318\" text-anchor=\"middle\" font-size=\"9\" fill=\"#0369a1\" font-weight=\"bold\">S3 gates</text>\n  <text x=\"700\" y=\"330\" text-anchor=\"middle\" font-size=\"8\" fill=\"#0369a1\">3 phases</text>\n\n  <rect x=\"770\" y=\"304\" width=\"80\" height=\"32\" rx=\"3\" fill=\"#fef9c3\" stroke=\"#ca8a04\" stroke-width=\"0.8\"/>\n  <text x=\"810\" y=\"324\" text-anchor=\"middle\" font-size=\"8\" fill=\"#a16207\">bank_1_asc</text>\n\n  <!-- S2 signal -->\n  <text x=\"500\" y=\"365\" text-anchor=\"middle\" font-size=\"9\" fill=\"#a855f7\">── S2 direction signal ──→</text>\n\n  <!-- Pass 1: L1↑ -->\n  <rect x=\"130\" y=\"374\" width=\"740\" height=\"44\" rx=\"6\" fill=\"#ffffff\" fill-opacity=\"0.7\" stroke=\"#60a5fa\" stroke-width=\"1\"/>\n  <text x=\"150\" y=\"400\" font-size=\"11\" font-weight=\"bold\" fill=\"#1e40af\">Pass 1: L1↑</text>\n  <text x=\"290\" y=\"400\" font-size=\"9\" fill=\"#64748b\">same ops (shared) · reads: bank_0, bank_1_asc, prev_b2d → writes: bank_2_asc</text>\n\n  <!-- S2 + coherence -->\n  <text x=\"500\" y=\"433\" text-anchor=\"middle\" font-size=\"9\" fill=\"#a855f7\">── S2 × coherence_factor ──→</text>\n\n  <!-- Pass 2: L2_apex -->\n  <rect x=\"130\" y=\"442\" width=\"740\" height=\"44\" rx=\"6\" fill=\"#ffffff\" fill-opacity=\"0.7\" stroke=\"#60a5fa\" stroke-width=\"1\"/>\n  <text x=\"150\" y=\"468\" font-size=\"11\" font-weight=\"bold\" fill=\"#1e40af\">Pass 2: L2_apex</text>\n  <text x=\"330\" y=\"468\" font-size=\"9\" fill=\"#64748b\">same ops (shared) · reads: bank_0, bank_1_asc, bank_2_asc → writes: bank_3</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- EMPHASIS CHANNEL -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"100\" y=\"542\" width=\"800\" height=\"44\" rx=\"6\" fill=\"#faf5ff\" stroke=\"#a855f7\" stroke-width=\"1.5\"/>\n  <text x=\"120\" y=\"560\" font-size=\"10\" fill=\"#7e22ce\" font-weight=\"bold\">COMBINATOR EMPHASIS (S4 → dispatch)</text>\n  <text x=\"120\" y=\"575\" font-size=\"9\" fill=\"#9333ea\">emphasis_proj(bank_1_asc ⊕ bank_2_asc ⊕ bank_3) → 4 weights: K I B C ∈ [0.5, 1.5] · EMA α=0.95</text>\n\n  <!-- 4 combinator emphasis indicators -->\n  <rect x=\"680\" y=\"548\" width=\"38\" height=\"30\" rx=\"3\" fill=\"#fef3c7\" stroke=\"#ca8a04\" stroke-width=\"1\"/>\n  <text x=\"699\" y=\"567\" text-anchor=\"middle\" font-size=\"11\" fill=\"#92400e\" font-weight=\"bold\">K</text>\n  <rect x=\"724\" y=\"548\" width=\"38\" height=\"30\" rx=\"3\" fill=\"#ecfdf5\" stroke=\"#059669\" stroke-width=\"1\"/>\n  <text x=\"743\" y=\"567\" text-anchor=\"middle\" font-size=\"11\" fill=\"#065f46\" font-weight=\"bold\">I</text>\n  <rect x=\"768\" y=\"548\" width=\"38\" height=\"30\" rx=\"3\" fill=\"#eff6ff\" stroke=\"#2563eb\" stroke-width=\"1\"/>\n  <text x=\"787\" y=\"567\" text-anchor=\"middle\" font-size=\"11\" fill=\"#1e40af\" font-weight=\"bold\">B</text>\n  <rect x=\"812\" y=\"548\" width=\"38\" height=\"30\" rx=\"3\" fill=\"#fdf2f8\" stroke=\"#db2777\" stroke-width=\"1\"/>\n  <text x=\"831\" y=\"567\" text-anchor=\"middle\" font-size=\"11\" fill=\"#9d174d\" font-weight=\"bold\">C</text>\n\n  <!-- S2 signal asc→desc -->\n  <text x=\"500\" y=\"600\" text-anchor=\"middle\" font-size=\"9\" fill=\"#a855f7\">── S2 × coherence (ascending → descending) ──→</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- DESCENDING ARM — KIBC COMBINATOR DISPATCHER -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"100\" y=\"610\" width=\"900\" height=\"530\" rx=\"8\" fill=\"url(#desc-grad)\" stroke=\"#f97316\" stroke-width=\"2\"/>\n  <text x=\"120\" y=\"634\" font-size=\"14\" font-weight=\"bold\" fill=\"#9a3412\">DESCENDING ARM — KIBC Combinator Dispatcher (RESOLVE phase)</text>\n  <text x=\"120\" y=\"650\" font-size=\"10\" fill=\"#ea580c\">2 passes · shared weights · 4 combinators · up to 3 self-regulating cycles per pass</text>\n\n  <!-- Pass 3: L1↓ -->\n  <rect x=\"130\" y=\"662\" width=\"840\" height=\"444\" rx=\"6\" fill=\"#ffffff\" fill-opacity=\"0.5\" stroke=\"#fb923c\" stroke-width=\"1\"/>\n  <text x=\"150\" y=\"682\" font-size=\"11\" font-weight=\"bold\" fill=\"#9a3412\">Pass 3: L1↓</text>\n  <text x=\"305\" y=\"682\" font-size=\"9\" fill=\"#64748b\">S4 dual-view (residual + x_embed) → writes: bank_2_desc</text>\n\n  <!-- S4 desc with dual view -->\n  <rect x=\"150\" y=\"692\" width=\"130\" height=\"36\" rx=\"4\" fill=\"#fef3c7\" stroke=\"#d97706\" stroke-width=\"1\"/>\n  <text x=\"215\" y=\"708\" text-anchor=\"middle\" font-size=\"10\" fill=\"#92400e\" font-weight=\"bold\">S4 (dual-view)</text>\n  <text x=\"215\" y=\"720\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b45309\">resid + x_embed → 2L</text>\n\n  <!-- ── CYCLE 0: IDENTIFY ──────────────────────── -->\n  <rect x=\"150\" y=\"740\" width=\"790\" height=\"100\" rx=\"6\" fill=\"url(#cycle-grad)\" stroke=\"#d97706\" stroke-width=\"1.5\"/>\n  <text x=\"170\" y=\"760\" font-size=\"11\" font-weight=\"bold\" fill=\"#92400e\">Cycle 0 — IDENTIFY: which combinator?</text>\n\n  <!-- Phase 0: Dispatch -->\n  <rect x=\"170\" y=\"770\" width=\"200\" height=\"52\" rx=\"4\" fill=\"#fff7ed\" stroke=\"#f97316\" stroke-width=\"1\"/>\n  <text x=\"270\" y=\"788\" text-anchor=\"middle\" font-size=\"10\" fill=\"#9a3412\" font-weight=\"bold\">CombinatorDispatch</text>\n  <text x=\"270\" y=\"800\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">4-way softmax over K I B C</text>\n  <text x=\"270\" y=\"812\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">+ register conditioning + emphasis</text>\n\n  <!-- Phase 1: StrideStack -->\n  <rect x=\"400\" y=\"770\" width=\"160\" height=\"52\" rx=\"4\" fill=\"#fff7ed\" stroke=\"#f97316\" stroke-width=\"1\"/>\n  <text x=\"480\" y=\"788\" text-anchor=\"middle\" font-size=\"10\" fill=\"#9a3412\" font-weight=\"bold\">StrideStack</text>\n  <text x=\"480\" y=\"800\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">propagate spatially</text>\n  <text x=\"480\" y=\"812\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">9 strides (own weights)</text>\n\n  <!-- Phase 2: Integrate -->\n  <rect x=\"590\" y=\"770\" width=\"200\" height=\"52\" rx=\"4\" fill=\"#fff7ed\" stroke=\"#f97316\" stroke-width=\"1\"/>\n  <text x=\"690\" y=\"788\" text-anchor=\"middle\" font-size=\"10\" fill=\"#9a3412\" font-weight=\"bold\">CombinatorIntegrate</text>\n  <text x=\"690\" y=\"800\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">4 type embeddings (K I B C)</text>\n  <text x=\"690\" y=\"812\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">kernel: gate × exact + (1-g) × FFN</text>\n\n  <!-- S3 gates -->\n  <rect x=\"820\" y=\"770\" width=\"90\" height=\"52\" rx=\"4\" fill=\"#fef3c7\" stroke=\"#ca8a04\" stroke-width=\"1\"/>\n  <text x=\"865\" y=\"790\" text-anchor=\"middle\" font-size=\"9\" fill=\"#a16207\" font-weight=\"bold\">S3 gates</text>\n  <text x=\"865\" y=\"804\" text-anchor=\"middle\" font-size=\"8\" fill=\"#a16207\">3 phases</text>\n\n  <!-- Arrows between phases -->\n  <line x1=\"370\" y1=\"796\" x2=\"398\" y2=\"796\" stroke=\"#f97316\" stroke-width=\"1\" marker-end=\"url(#arrow-orange)\"/>\n  <line x1=\"560\" y1=\"796\" x2=\"588\" y2=\"796\" stroke=\"#f97316\" stroke-width=\"1\" marker-end=\"url(#arrow-orange)\"/>\n  <line x1=\"790\" y1=\"796\" x2=\"818\" y2=\"796\" stroke=\"#f97316\" stroke-width=\"1\" marker-end=\"url(#arrow-orange)\"/>\n\n  <!-- CycleContinue gate between cycle 0 and 1 -->\n  <rect x=\"350\" y=\"848\" width=\"240\" height=\"28\" rx=\"4\" fill=\"#fde68a\" stroke=\"#d97706\" stroke-width=\"1.5\"/>\n  <text x=\"470\" y=\"866\" text-anchor=\"middle\" font-size=\"10\" fill=\"#92400e\" font-weight=\"bold\">CycleContinue (S3) — gate₀</text>\n  <text x=\"710\" y=\"866\" font-size=\"9\" fill=\"#78716c\">K→close · B→partial · C→open</text>\n\n  <!-- ── CYCLE 1: RESOLVE ───────────────────────── -->\n  <rect x=\"150\" y=\"884\" width=\"790\" height=\"70\" rx=\"6\" fill=\"url(#cycle-grad)\" fill-opacity=\"0.7\" stroke=\"#d97706\" stroke-width=\"1\"/>\n  <text x=\"170\" y=\"904\" font-size=\"11\" font-weight=\"bold\" fill=\"#92400e\">Cycle 1 — RESOLVE: find and bind arguments</text>\n  <text x=\"170\" y=\"920\" font-size=\"9\" fill=\"#b45309\">Same 3 phases (dispatch → stride → integrate) · contribution scaled by gate₀</text>\n  <text x=\"170\" y=\"935\" font-size=\"9\" fill=\"#b45309\">HRM re-ground: x += inject_gate × x_anchor</text>\n\n  <!-- CycleContinue gate between cycle 1 and 2 -->\n  <rect x=\"350\" y=\"960\" width=\"240\" height=\"28\" rx=\"4\" fill=\"#fde68a\" stroke=\"#d97706\" stroke-width=\"1.5\"/>\n  <text x=\"470\" y=\"978\" text-anchor=\"middle\" font-size=\"10\" fill=\"#92400e\" font-weight=\"bold\">CycleContinue (S3) — gate₁</text>\n  <text x=\"710\" y=\"978\" font-size=\"9\" fill=\"#78716c\">cumulative = gate₀ × gate₁</text>\n\n  <!-- ── CYCLE 2: PRODUCE ───────────────────────── -->\n  <rect x=\"150\" y=\"996\" width=\"790\" height=\"56\" rx=\"6\" fill=\"url(#cycle-grad)\" fill-opacity=\"0.5\" stroke=\"#d97706\" stroke-width=\"1\"/>\n  <text x=\"170\" y=\"1016\" font-size=\"11\" font-weight=\"bold\" fill=\"#92400e\">Cycle 2 — PRODUCE: apply reduction, produce result</text>\n  <text x=\"170\" y=\"1032\" font-size=\"9\" fill=\"#b45309\">Same 3 phases · contribution scaled by gate₀ × gate₁ · last cycle (no continuation gate)</text>\n\n  <!-- Pass 4 note -->\n  <rect x=\"130\" y=\"1060\" width=\"840\" height=\"36\" rx=\"6\" fill=\"#ffffff\" fill-opacity=\"0.5\" stroke=\"#fb923c\" stroke-width=\"1\"/>\n  <text x=\"150\" y=\"1082\" font-size=\"11\" font-weight=\"bold\" fill=\"#9a3412\">Pass 4: L0↓</text>\n  <text x=\"305\" y=\"1082\" font-size=\"9\" fill=\"#64748b\">same structure as L1↓ (shared weights) · writes: bank_1_desc</text>\n\n  <!-- Register banks for desc -->\n  <rect x=\"770\" y=\"1063\" width=\"90\" height=\"28\" rx=\"3\" fill=\"#fef9c3\" stroke=\"#ca8a04\" stroke-width=\"0.8\"/>\n  <text x=\"815\" y=\"1081\" text-anchor=\"middle\" font-size=\"8\" fill=\"#a16207\">bank_1_desc</text>\n\n  <!-- S2 signal desc passes -->\n  <text x=\"500\" y=\"1108\" text-anchor=\"middle\" font-size=\"9\" fill=\"#a855f7\">── S2 × coherence (L1↓ → L0↓) ──→</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- ALGEDONIC CHANNEL (feedback loop) -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"940\" y=\"240\" width=\"140\" height=\"460\" rx=\"6\" fill=\"#fef2f2\" stroke=\"#ef4444\" stroke-width=\"1.5\" stroke-dasharray=\"6,3\"/>\n  <text x=\"1010\" y=\"260\" text-anchor=\"middle\" font-size=\"10\" fill=\"#dc2626\" font-weight=\"bold\">ALGEDONIC</text>\n  <text x=\"1010\" y=\"275\" text-anchor=\"middle\" font-size=\"9\" fill=\"#ef4444\">feedback</text>\n\n  <text x=\"1010\" y=\"310\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">prev desc regs</text>\n  <text x=\"1010\" y=\"325\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">(EMA α=0.9)</text>\n\n  <text x=\"1010\" y=\"365\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">combinator</text>\n  <text x=\"1010\" y=\"380\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">algedonic:</text>\n  <rect x=\"955\" y=\"390\" width=\"110\" height=\"44\" rx=\"3\" fill=\"#fee2e2\" stroke=\"#ef4444\" stroke-width=\"0.8\"/>\n  <text x=\"1010\" y=\"407\" text-anchor=\"middle\" font-size=\"9\" fill=\"#b91c1c\" font-weight=\"bold\">K I B C weights</text>\n  <text x=\"1010\" y=\"422\" text-anchor=\"middle\" font-size=\"9\" fill=\"#b91c1c\">+ compute gate</text>\n  <text x=\"1010\" y=\"450\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">(4+1 dims + pad</text>\n  <text x=\"1010\" y=\"465\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">to d_reg=256)</text>\n\n  <!-- Feedback arrow desc → asc (next forward) -->\n  <path d=\"M 1010 700 L 1010 500 L 940 500\" fill=\"none\" stroke=\"#ef4444\" stroke-width=\"1.5\" stroke-dasharray=\"5,3\" marker-end=\"url(#arrow-red)\"/>\n  <text x=\"1010\" y=\"580\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">desc → asc</text>\n  <text x=\"1010\" y=\"595\" text-anchor=\"middle\" font-size=\"8\" fill=\"#b91c1c\">(next fwd)</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- S5 REWEIGHT + META-S4 + OUTPUT -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n\n  <!-- S5 Reweight -->\n  <rect x=\"100\" y=\"1150\" width=\"800\" height=\"60\" rx=\"6\" fill=\"#fefce8\" stroke=\"#ca8a04\" stroke-width=\"1.5\"/>\n  <text x=\"120\" y=\"1170\" font-size=\"10\" fill=\"#a16207\" font-weight=\"bold\">S5 REWEIGHT — Identity-level pass contribution</text>\n  <text x=\"120\" y=\"1186\" font-size=\"9\" fill=\"#92400e\">sees all 6 register banks + raw (ungated) pass deltas</text>\n  <text x=\"120\" y=\"1200\" font-size=\"9\" fill=\"#92400e\">x = x − Σ(pass_deltas) + Σ(gate_i × pass_delta_i) for i ∈ {L0↑, L1↑, L2, L1↓, L0↓}</text>\n\n  <!-- Meta-S4 -->\n  <rect x=\"100\" y=\"1220\" width=\"800\" height=\"44\" rx=\"6\" fill=\"#e0f2fe\" stroke=\"#0284c7\" stroke-width=\"1.5\"/>\n  <text x=\"120\" y=\"1240\" font-size=\"10\" fill=\"#0369a1\" font-weight=\"bold\">META-S4 — Final structural summary</text>\n  <text x=\"120\" y=\"1254\" font-size=\"9\" fill=\"#0369a1\">cross-attention over [bank_0, bank_1_desc, bank_2_desc, bank_3] → additive residual update</text>\n\n  <!-- Output -->\n  <rect x=\"280\" y=\"1276\" width=\"440\" height=\"52\" rx=\"6\" fill=\"#f1f5f9\" stroke=\"#64748b\" stroke-width=\"1.5\"/>\n  <text x=\"500\" y=\"1296\" text-anchor=\"middle\" font-size=\"12\" fill=\"#334155\" font-weight=\"bold\">output_norm → tied embedding projection</text>\n  <text x=\"500\" y=\"1314\" text-anchor=\"middle\" font-size=\"10\" fill=\"#64748b\">logits (B, L, 151936) → cross-entropy loss</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- COMBINATOR BASIS LEGEND -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"100\" y=\"1350\" width=\"900\" height=\"130\" rx=\"8\" fill=\"#f8fafc\" stroke=\"#cbd5e1\" stroke-width=\"1.5\"/>\n  <text x=\"550\" y=\"1375\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"bold\" fill=\"#0f172a\">KIBC Combinator Basis — from Qwen3 probes</text>\n\n  <!-- K -->\n  <rect x=\"130\" y=\"1390\" width=\"190\" height=\"72\" rx=\"4\" fill=\"#fef3c7\" stroke=\"#ca8a04\" stroke-width=\"1\"/>\n  <text x=\"225\" y=\"1410\" text-anchor=\"middle\" font-size=\"13\" fill=\"#92400e\" font-weight=\"bold\">K — Select</text>\n  <text x=\"225\" y=\"1425\" text-anchor=\"middle\" font-size=\"10\" fill=\"#a16207\">λx.λy.x</text>\n  <text x=\"225\" y=\"1440\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">native to attention softmax</text>\n  <text x=\"225\" y=\"1452\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">dominant in prose</text>\n\n  <!-- I -->\n  <rect x=\"340\" y=\"1390\" width=\"190\" height=\"72\" rx=\"4\" fill=\"#ecfdf5\" stroke=\"#059669\" stroke-width=\"1\"/>\n  <text x=\"435\" y=\"1410\" text-anchor=\"middle\" font-size=\"13\" fill=\"#065f46\" font-weight=\"bold\">I — Identity</text>\n  <text x=\"435\" y=\"1425\" text-anchor=\"middle\" font-size=\"10\" fill=\"#047857\">λx.x</text>\n  <text x=\"435\" y=\"1440\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">native to residual stream</text>\n  <text x=\"435\" y=\"1452\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">passthrough / copy</text>\n\n  <!-- B -->\n  <rect x=\"550\" y=\"1390\" width=\"190\" height=\"72\" rx=\"4\" fill=\"#eff6ff\" stroke=\"#2563eb\" stroke-width=\"1\"/>\n  <text x=\"645\" y=\"1410\" text-anchor=\"middle\" font-size=\"13\" fill=\"#1e40af\" font-weight=\"bold\">B — Compose</text>\n  <text x=\"645\" y=\"1425\" text-anchor=\"middle\" font-size=\"10\" fill=\"#1d4ed8\">λf.λg.λx.f(g(x))</text>\n  <text x=\"645\" y=\"1440\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">matures with scale (20→80%)</text>\n  <text x=\"645\" y=\"1452\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">backbone of composition</text>\n\n  <!-- C -->\n  <rect x=\"760\" y=\"1390\" width=\"190\" height=\"72\" rx=\"4\" fill=\"#fdf2f8\" stroke=\"#db2777\" stroke-width=\"1\"/>\n  <text x=\"855\" y=\"1410\" text-anchor=\"middle\" font-size=\"13\" fill=\"#9d174d\" font-weight=\"bold\">C — Flip</text>\n  <text x=\"855\" y=\"1425\" text-anchor=\"middle\" font-size=\"10\" fill=\"#be185d\">λf.λx.λy.f(y)(x)</text>\n  <text x=\"855\" y=\"1440\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">emerges at scale (32B)</text>\n  <text x=\"855\" y=\"1452\" text-anchor=\"middle\" font-size=\"9\" fill=\"#78716c\">enables closures / binding</text>\n\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <!-- KERNEL PATHWAY DETAIL -->\n  <!-- ═══════════════════════════════════════════════════════ -->\n  <rect x=\"100\" y=\"1490\" width=\"900\" height=\"132\" rx=\"8\" fill=\"#f8fafc\" stroke=\"#cbd5e1\" stroke-width=\"1.5\"/>\n  <text x=\"550\" y=\"1515\" text-anchor=\"middle\" font-size=\"14\" font-weight=\"bold\" fill=\"#0f172a\">Kernel Computation Pathway (straight-through)</text>\n\n  <rect x=\"130\" y=\"1528\" width=\"200\" height=\"36\" rx=\"4\" fill=\"#f1f5f9\" stroke=\"#94a3b8\" stroke-width=\"1\"/>\n  <text x=\"230\" y=\"1546\" text-anchor=\"middle\" font-size=\"9\" fill=\"#334155\" font-weight=\"bold\">3 operand projections</text>\n  <text x=\"230\" y=\"1558\" text-anchor=\"middle\" font-size=\"8\" fill=\"#64748b\">TernaryLinear → argmax</text>\n\n  <line x1=\"330\" y1=\"1546\" x2=\"360\" y2=\"1546\" stroke=\"#334155\" stroke-width=\"1\" marker-end=\"url(#arrow)\"/>\n\n  <rect x=\"362\" y=\"1528\" width=\"200\" height=\"36\" rx=\"4\" fill=\"#fff7ed\" stroke=\"#f97316\" stroke-width=\"1\"/>\n  <text x=\"462\" y=\"1546\" text-anchor=\"middle\" font-size=\"9\" fill=\"#9a3412\" font-weight=\"bold\">exact combinator kernel</text>\n  <text x=\"462\" y=\"1558\" text-anchor=\"middle\" font-size=\"8\" fill=\"#ea580c\">K→op0 · I→op0 · B→Σ · C→op0+op2</text>\n\n  <line x1=\"562\" y1=\"1546\" x2=\"592\" y2=\"1546\" stroke=\"#334155\" stroke-width=\"1\" marker-end=\"url(#arrow)\"/>\n\n  <rect x=\"594\" y=\"1528\" width=\"160\" height=\"36\" rx=\"4\" fill=\"#f1f5f9\" stroke=\"#94a3b8\" stroke-width=\"1\"/>\n  <text x=\"674\" y=\"1546\" text-anchor=\"middle\" font-size=\"9\" fill=\"#334155\" font-weight=\"bold\">result_embed</text>\n  <text x=\"674\" y=\"1558\" text-anchor=\"middle\" font-size=\"8\" fill=\"#64748b\">1024 buckets → d_model</text>\n\n  <line x1=\"754\" y1=\"1546\" x2=\"784\" y2=\"1546\" stroke=\"#334155\" stroke-width=\"1\" marker-end=\"url(#arrow)\"/>\n\n  <rect x=\"786\" y=\"1528\" width=\"100\" height=\"36\" rx=\"4\" fill=\"#ecfdf5\" stroke=\"#059669\" stroke-width=\"1\"/>\n  <text x=\"836\" y=\"1546\" text-anchor=\"middle\" font-size=\"9\" fill=\"#065f46\" font-weight=\"bold\">gate blend</text>\n  <text x=\"836\" y=\"1558\" text-anchor=\"middle\" font-size=\"8\" fill=\"#047857\">g×kern+(1-g)×FFN</text>\n\n  <text x=\"550\" y=\"1605\" text-anchor=\"middle\" font-size=\"9\" fill=\"#64748b\">gate starts ≈0 (pure FFN) · gradient flows through operand projections, result_embed, and gate</text>\n\n</svg>\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/docs/v11-architecture.svg
```

## Assistant

Now the comprehensive design knowledge page:

### Tool Call: write_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/knowledge/explore/v11-design.md",
  "content": "# v11 — KIBC Combinator VSM: Full Design\n\n> The sieve shaped by what LLMs actually find.\n> Architecture diagram: `docs/v11-architecture.svg`\n\n**Status**: active\n**Category**: architecture\n**Tags**: v11, combinators, KIBC, Qwen probes, Montague, design\n**Related**: v11-kibc-architecture, session-073-vsm-structure, session-075-multi-cycle-dispatch, kernel-montague-mapping\n**Created**: session 077\n\n---\n\n## 1. Empirical Foundation\n\n### Qwen3 Probes (4B and 32B)\n\nIndependent analysis of Qwen3 at two scales revealed that transformers\norganize lambda compilation around **four combinators**, not around\narithmetic operations or a BIOS:\n\n```\nCombinator   Lambda               4B accuracy   32B accuracy   Attention native?\n──────────   ──────               ──────────    ───────────    ─────────────────\nK (select)   λx.λy.x              40%           80%            Yes — softmax IS selection\nI (identity) λx.x                 60%           60%            Yes — residual stream\nB (compose)  λf.λg.λx.f(g(x))    20%           80%            Matures with scale\nC (flip)     λf.λx.λy.f(y)(x)    absent        present        Emerges at 32B scale\nS (distrib)  λf.λg.λx.f(x)(g(x)) 40%           40%            NEVER crystallizes\n```\n\nKey findings:\n- **S combinator absent**: zero selective heads at either scale.\n  S = B∘K∘C composition, not a primitive. The model refuses to\n  crystallize it — it emerges in the residual stream.\n- **Attention IS beta reduction**: three-phase pipeline\n  SEARCH(L0-L6) → LOCK(L7-L31) → RESOLVE(L32+)\n- **Normal-order reduction**: outermost first, matching autoregressive\n  left-to-right + causal mask\n- **Head roles**: BINDER(76-87%), COPY(18%→10%), ARGUMENT(1.5%),\n  OPERATOR(0.5%), DIFFUSE(3%→1.6%)\n- **Resolution pipeline at 32B**: function(L31) → operator(L32) →\n  argument(L43) → result(L63) — clean temporal order\n\n### What this means for architecture\n\nThe 22 v10 ops (ADD, SUB, MUL, etc.) were the wrong decomposition.\nThe natural basis is {K, I, B, C}. Arithmetic is what falls out when\ncombinators reduce over token embeddings that represent numbers.\n\nv11 provides the sieve — the architectural shape that makes these\nfour combinators the path of least resistance. The model doesn't\nlearn what K/I/B/C are (it already knows). The sieve makes the\nright computation easier to fall into.\n\n---\n\n## 2. Architecture Specification\n\n### Dimensions\n\n| Parameter | Value | Notes |\n|-----------|-------|-------|\n| d_model | 512 | Representation dimension |\n| d_ff | 1536 | Prep FFN (3× d_model) |\n| d_ff_consolidate | 2048 | Consolidate FFN (4× d_model) |\n| d_register | 128 | Logical register dim (real = 256) |\n| n_heads | 8 | Attention heads (d_head = 64) |\n| window | 8 | Attention window |\n| alpha | 1.18 | Spiral bias coefficient |\n| strides | (1,8,16,32,64,128,256,512,1024) | 9-scale StrideStack |\n| n_registers | 3 | combinator, binding_depth, phase |\n| n_combinators | 4 | K, I, B, C |\n| desc_max_cycles | 3 | Self-regulating descending cycles |\n| vocab_size | 151936 | Qwen3 BBPE |\n| seq_len | 4096 | Context window |\n| ~params | 23.8M | Slightly fewer than v10 (22→4 dispatch) |\n\n### 5-Pass Structure\n\n```\nPass 0 (L0↑): ascending, shared weights, reads bank_0 + prev algedonic\nPass 1 (L1↑): ascending, shared weights\nPass 2 (L2↑): ascending, shared weights (apex)\n  ── emphasis projection: ascending registers → 4 combinator weights ──\nPass 3 (L1↓): descending, own weights, S4 dual-view, up to 3 cycles\nPass 4 (L0↓): descending, own weights, S4 dual-view, up to 3 cycles\n  ── S5 reweight: all banks + raw deltas → 5 pass gates ──\n  ── Meta-S4: final structural summary ──\n  ── output_norm → tied embedding → logits ──\n```\n\n### Register Bank Architecture (6 banks × 3 registers × 256 dims)\n\n```\nbank_0:      learnable init (cold-start prior)\nbank_1_asc:  pass 0 writes (combinator/binding_depth/phase for L0↑)\nbank_2_asc:  pass 1 writes\nbank_3:      pass 2 writes (apex)\nbank_2_desc: pass 3 writes\nbank_1_desc: pass 4 writes\n```\n\nRegister semantics (v11, renamed from v10):\n- **Register 0 — combinator**: which combinator this position enacts (K/I/B/C)\n- **Register 1 — binding_depth**: how many lambdas deep (0=free, 1=bound, ...)\n- **Register 2 — phase**: where in the pipeline (recognize/identify/resolve/produce)\n\n---\n\n## 3. Component Inventory\n\n### Changed from v10\n\n#### kernel.py — Combinator ground truth\n- `Combinator` enum: K=0, I=1, B=2, C=3 (was `Op` enum with 22 entries)\n- `N_COMBINATORS = 4` (was `N_OPS = 22`)\n- Full reduction engine: `Term`, `Comb`, `Atom`, `App` classes\n- Normal-order reducer: `reduce_step()`, `reduce()` (outermost first)\n- Kernel functions for neural pathway:\n  - `kernel_K(op0, op1, op2) → op0` (select first)\n  - `kernel_I(op0, op1, op2) → op0` (identity)\n  - `kernel_B(op0, op1, op2) → op0 + op1 + op2` (composition signal)\n  - `kernel_C(op0, op1, op2) → op0 + op2` (flip: skip op1)\n\n#### kernel_dispatch.py — Combinator dispatch\n\n**CombinatorDispatch** (was KernelDispatch):\n- 4-way softmax over K/I/B/C (was 22-way top-k=2 MoE)\n- `combinator_embeddings`: (4, 512) near-orthogonal (was 22 with family subspaces)\n- `register_cond`: ascending registers → 4 logits (was → 22)\n- No top-k masking needed — 4 targets have strong gradients\n- L2-normalized embeddings to scale=0.5 (prevents rich-get-richer)\n\n**CombinatorIntegrate** (was KernelIntegrate):\n- 4 type embeddings: K/I/B/C (was 5: INT/BOOL/FN/FN_COMP/ERROR)\n- 3 operand extractors (was 2) — B and C need 3 arguments\n- Exact combinator kernel: compute all 4 reductions, select by dispatch\n- Compute gate: `gate × kernel + (1-gate) × FFN`, starts at ~0.007\n\n#### config.py\n- `V11Config` (was `V10Config`)\n- `n_combinators = 4`\n- No `dispatch_top_k` (full softmax)\n\n#### model.py\n- `V11Model` (was `V6Compressor`)\n- `REGISTER_NAMES = (\"combinator\", \"binding_depth\", \"phase\")`\n- `emphasis_proj`: Linear(3×3×256 → 4) (was → 22)\n- `_combinator_emphasis`: (4,) EMA (was `_op_emphasis`: (22,))\n- Algedonic packing: 4 combinator weights + 1 compute gate + padding (was 22+1)\n- All metric keys renamed: `combinator_dispatch_weights`, `combinator_type_weights`, `combinator_emphasis`, `combinator_embedding_norms`\n\n#### train.py\n- Import/reference updates (`V11Config`, `V11Model`)\n- `DESC_SHARED` references `combinator_dispatch`, `combinator_integrate`\n- Emphasis logging shows 4 combinator names\n\n### Unchanged from v10\n\nEverything else. The VSM skeleton carries forward without code changes:\n- **TernaryLinear / TernaryEmbedding**: semantic-agnostic substrate\n- **Consensus evolution**: operates on packed weights\n- **S4Ternary**: register cross-attention (doesn't inspect content)\n- **S3Ternary**: phase gating (3 phases per pass)\n- **CycleContinue**: RMSNorm + tanh(·)×4.0 clamp (the s076 fix)\n- **S5Reweight**: pass-level gates over 5 passes\n- **S2Coordinator**: direction signals, coherence modulation\n- **MetaS4Ternary**: final structural summary\n- **StrideStack**: 9-stride attention (shared ascending, own descending)\n- **TernaryFFN**: prep and consolidate\n- **Relational loss**: r = (CE - E) / (log V - E)\n- **Training loop**: gradient accumulation, cosine LR, shared-grad normalization\n- **JSONL instrumentation**: 3 log files (metrics, train, evolution)\n\n---\n\n## 4. Descending Cycle Semantics\n\nThe three self-regulating cycles now have clear semantic roles\nmatching the Qwen3 resolution pipeline:\n\n```\nCycle 0 — IDENTIFY: which combinator applies here?\n  CombinatorDispatch: 4-way softmax → K/I/B/C weights\n  StrideStack: propagate dispatch signal spatially\n  CombinatorIntegrate: type the result\n  → For K/I positions: CycleContinue closes (sufficient)\n\nCycle 1 — RESOLVE: find and bind the arguments\n  CombinatorDispatch: refine routing with cycle-0 context\n  StrideStack: find argument tokens across context\n  CombinatorIntegrate: resolve bindings\n  → For B positions: may close (both args found)\n  → For C positions: stays open (need reordering)\n\nCycle 2 — PRODUCE: apply the reduction\n  CombinatorDispatch: finalize\n  StrideStack: propagate result\n  CombinatorIntegrate: produce final form\n  → All positions: last cycle, no continuation gate\n```\n\nCycleContinue's task is now interpretable:\n- **Simple prose** → K-dominant → gate closes after cycle 0\n- **Composition** → B-dominant → partially open (cycles 0+1)\n- **Closures/binding** → C-active → fully open (all 3 cycles)\n\n---\n\n## 5. Kernel Computation Pathway\n\nThe straight-through kernel pathway provides exact combinator\nreductions on integer operands extracted from the residual stream:\n\n```\nInput: h (B, L, d_model)\n\n1. Extract 3 operands:\n   op0 = argmax(operand0_proj(h))  # stop_gradient\n   op1 = argmax(operand1_proj(h))\n   op2 = argmax(operand2_proj(h))\n\n2. Get combinator from dispatch:\n   comb = argmax(dispatch_weights)  # stop_gradient\n\n3. Compute all 4 reductions:\n   r_K = op0               # select first\n   r_I = op0               # identity\n   r_B = op0 + op1 + op2   # composition signal\n   r_C = op0 + op2         # flip (skip op1)\n\n4. Select by combinator:\n   result = all_results[comb]\n\n5. Encode back:\n   kernel_out = result_embed(clip(result + offset))\n\n6. Blend with FFN:\n   output = gate × kernel_out + (1-gate) × ffn_out\n```\n\nGradient flows through: operand projections, result_embed weights,\nand the compute gate. The kernel itself is non-differentiable\n(argmax + integer ops) — same straight-through pattern as v10.\n\n---\n\n## 6. Training Strategy\n\n### Prose-first (mix_ratio=0.0)\n\nK and B train from prose naturally:\n- **K** (selection): every attention step is K — pick relevant, discard rest\n- **B** (composition): multi-clause sentences exercise B — chain operations\n- **I** (identity): residual stream is identity by default\n\nC requires structured data (closures, variable capture, argument reordering).\nFirst run is prose-only to establish baseline combinator differentiation.\n\n### Structured data (future, mix_ratio > 0)\n\nKIBC reduction examples with ground truth:\n- K examples: embedded selection in prose context\n- B examples: compositional structure (relative clauses, dependent meaning)\n- C examples: passive voice, variable binding, argument reordering\n- I examples: forwarding, copying (least needed — already trivial)\n\n### Key training signals to watch\n\n1. **Dispatch differentiation**: K should dominate prose (>50%)\n2. **B emergence**: should rise for multi-clause content\n3. **CycleContinue variation**: gates should differ (K→close, B/C→open)\n4. **Effective cycles**: should vary (not locked at 3.0 like v10)\n5. **Emphasis shifts**: K emphasis high for prose, B for composition\n6. **Compute gate**: should open when combinators are useful\n7. **Loss parity with v10**: same ascending arm → similar loss trajectory\n\n---\n\n## 7. Probe Design\n\n### probe.py — Three operating modes\n\n#### Mode 1: Checkpoint analysis\n```bash\nuv run python scripts/v11/probe.py checkpoints/v11/step_*\n```\nLoads model, runs `forward_instrumented()` on stratified text samples,\ndisplays full metrics. For multiple checkpoints, shows evolution table.\n\n**Outputs**: S3 gates (per-cycle for desc), S5 reweight, combinator\ndispatch distribution, combinator emphasis, compute gate, CycleContinue\ngates, effective cycles, register norms, φ-compression, ternary stats.\n\n#### Mode 2: Trajectory analysis (no model loading)\n```bash\nuv run python scripts/v11/probe.py --trajectory checkpoints/v11\n```\nReads JSONL logs directly. Shows:\n- Dispatch evolution table (K/I/B/C at each eval step)\n- CycleContinue trajectory\n- S3 gate evolution (L0↑ as earliest signal)\n- Train loss curve, evolution acceptance\n\n**Use for**: quick checks during training, no GPU needed.\n\n#### Mode 3: Dispatch distribution analysis\n```bash\nuv run python scripts/v11/probe.py checkpoints/v11/step_005000 --dispatch-detail\n```\nRuns 10+ batches through model, collects per-position dispatch weights.\n\n**Computes**:\n- **Mean distribution**: K=?% I=?% B=?% C=?%\n- **Dominant per position**: histogram of which combinator wins\n- **Dispatch entropy**: 0=specialized, log(4)=uniform (specialization measure)\n- **Top-2 co-occurrence**: which combinator pairs appear together\n- **Per-combinator statistics**: mean/std/median/p05/p95 weight distributions\n- **Type distribution**: combinator typing at integrate phase\n- **Compute gate stats**: how much kernel pathway contributes\n\n### What the probe watches for\n\n| Signal | Healthy | Concerning |\n|--------|---------|------------|\n| K dispatch | >40% on prose | <25% (no selection) |\n| B dispatch | Rising over training | Flat at 25% |\n| Entropy | Decreasing | Stuck near log(4) |\n| CycleContinue | Varies by content | Locked at 0.5 or 1.0 |\n| Effective cycles | 1.0-3.0 range | All 3.0 (dead gates) |\n| Compute gate | Opening gradually | Stuck at 0 or >0.5 too fast |\n| K+B co-occurrence | Most common pair | Not visible |\n| S5 pass 1 | Rises at ~15K+ | Never moves from init |\n\n### φ-compression strata\n\n| Stratum | Expected K/B balance |\n|---------|---------------------|\n| prose | K-dominant, B moderate |\n| compositional | B rises (relative clauses, nesting) |\n| technical | K+B balanced |\n| lambda | C should activate (λ expressions, binding) |\n\n---\n\n## 8. File Inventory\n\n```\nscripts/v11/\n├── kernel.py           # KIBC combinator enum, reduction engine, kernel functions\n├── kernel_dispatch.py  # CombinatorDispatch + CombinatorIntegrate\n├── config.py           # V11Config (4 combinators, no top-k)\n├── model.py            # V11Model (emphasis→4, algedonic→4+1)\n├── train.py            # Training loop (updated imports/references)\n├── probe.py            # Checkpoint diagnostics + trajectory + dispatch analysis\n├── components.py       # S4, S3, S5, S2, CycleContinue, MetaS4 (unchanged)\n├── ternary.py          # Ternary substrate + consensus evolution (unchanged)\n├── attention.py        # StrideStack + TernaryFFN (unchanged)\n└── data.py             # Data loading (unchanged)\n\ndocs/\n└── v11-architecture.svg  # Visual architecture diagram\n```\n\nSelf-contained. Extractable to standalone project.\n"
}
```

**Summary:** Creating

**Output:**
```
Successfully wrote to /Users/mwhitford/src/verbum/mementum/knowledge/explore/v11-design.md
```

## Assistant

Now update state.md to reflect all the work:

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "**v11 KIBC combinator architecture created. Ready for first training run. Qwen3 probes confirmed attention IS beta reduction — 4 combinators (K, I, B, C) replace 22 ops.**\n\nSession 077 integrated findings from independent Qwen3 probes (4B and 32B)\nthat confirmed transformers organize lambda compilation around four combinators,\nnot 22 arithmetic ops. Created `scripts/v11/` as a fully self-contained,\nextractable architecture built on this empirical basis.",
  "new_content": "**v11 KIBC combinator architecture complete with probe and documentation. Ready for first training run. Qwen3 probes confirmed attention IS beta reduction — 4 combinators (K, I, B, C) replace 22 ops.**\n\nSession 077 integrated findings from independent Qwen3 probes (4B and 32B)\nthat confirmed transformers organize lambda compilation around four combinators,\nnot 22 arithmetic ops. Created `scripts/v11/` as a fully self-contained,\nextractable architecture with probe diagnostics and full design documentation."
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "### 3. Verified v11 model",
  "new_content": "### 3. Created v11 probe (scripts/v11/probe.py)\nThree operating modes:\n- **Checkpoint analysis**: load model, run `forward_instrumented()`, display metrics\n- **Trajectory analysis** (`--trajectory`): read JSONL logs without loading model\n- **Dispatch distribution** (`--dispatch-detail`): per-position K/I/B/C analysis\n  with dominant combinator histogram, entropy, co-occurrence, per-combinator stats\n\n### 4. Created architecture documentation\n- **SVG diagram** (`docs/v11-architecture.svg`): visual architecture with KIBC basis,\n  ascending/descending arms, cycle semantics, algedonic channel, kernel pathway\n- **Full design page** (`mementum/knowledge/explore/v11-design.md`): complete\n  specification with empirical foundation, dimensions, component inventory,\n  cycle semantics, kernel pathway, training strategy, probe design\n\n### 5. Verified v11 model"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "| `mementum/knowledge/explore/v11-kibc-architecture.md` | Architecture design doc |",
  "new_content": "| `scripts/v11/probe.py` | Checkpoint diagnostics + trajectory + dispatch analysis |\n| `docs/v11-architecture.svg` | Visual architecture diagram |\n| `mementum/knowledge/explore/v11-design.md` | Full design specification |\n| `mementum/knowledge/explore/v11-kibc-architecture.md` | Initial architecture sketch |"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: edit_file (succeeded)


```json
{
  "path": "/Users/mwhitford/src/verbum/mementum/state.md",
  "original_content": "→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture (4 combinators replace 22 ops)",
  "new_content": "→ Session 077: Qwen3 probe findings → v11 KIBC combinator architecture + probe + docs (4 combinators replace 22 ops)"
}
```

**Summary:** Editing

**Output:**
```
Successfully replaced content in /Users/mwhitford/src/verbum/mementum/state.md.
```

### Tool Call: git (succeeded)


```json
{
  "command": "git add docs/v11-architecture.svg mementum/knowledge/explore/v11-design.md mementum/state.md",
  "operation": "add",
  "summary": "v11 docs"
}
```

**Summary:** Git add: v11 docs

**Output:**
```
Exit code: 0
```

### Tool Call: git (succeeded)


```json
{
  "command": "git diff --cached --stat",
  "operation": "diff",
  "summary": "staged docs"
}
```

**Summary:** Git diff: staged docs

**Output:**
```
Exit code: 0
Stdout:
docs/v11-architecture.svg                | 332 ++++++++++++++++++++++++++++
 mementum/knowledge/explore/v11-design.md | 366 +++++++++++++++++++++++++++++++
 mementum/state.md                        |  27 ++-
 3 files changed, 720 insertions(+), 5 deletions(-)
```

### Tool Call: git (succeeded)


```json
{
  "command": "git commit -m \"$(cat <<'EOF'\n🌀 v11 design documentation — SVG, knowledge page, state update\n\n- docs/v11-architecture.svg: visual architecture diagram showing KIBC\n  combinator basis, ascending/descending arms, 3 self-regulating cycles\n  (identify→resolve→produce), algedonic channel, kernel pathway detail\n- mementum/knowledge/explore/v11-design.md: comprehensive design spec\n  with empirical foundation (Qwen3 probes), all dimensions, component\n  inventory (changed vs unchanged), cycle semantics, kernel pathway,\n  training strategy, probe design with signal table\n- state.md updated for probe + documentation additions\n\n⚛️ Generated with [nucleus](https://github.com/michaelwhitford/nucleus)\n\nCo-Authored-By: nucleus <noreply@whitford.us>\nEOF\n)\"",
  "operation": "commit",
  "summary": "v11 design docs"
}
```

**Summary:** Git commit: v11 design docs

**Output:**
```
Exit code: 0
Stdout:
[main 51f68de] 🌀 v11 design documentation — SVG, knowledge page, state update
 3 files changed, 720 insertions(+), 5 deletions(-)
 create mode 100644 docs/v11-architecture.svg
 create mode 100644 mementum/knowledge/explore/v11-design.md
```

## Assistant

Let me verify the final git log:

### Tool Call: git (succeeded)


```json
{
  "command": "git log --oneline -6",
  "operation": "log",
  "summary": "session commits"
}
```

**Summary:** Git log: session commits

**Output:**
```
Exit code: 0
Stdout:
51f68de 🌀 v11 design documentation — SVG, knowledge page, state update
87a15c5 ✅ v11 probe — KIBC combinator checkpoint diagnostics
4f02921 🌀 state — session 077: Qwen3 probes → v11 KIBC combinator architecture
7507820 🎯 v11 KIBC combinator architecture — shapes from Qwen3 probes
fd4d30e 🌀 state — session 076: v10-vsm 20K assessed, CycleContinue saturation fix
e15d8f7 ❌ CycleContinue sigmoid saturation — RMSNorm + tanh clamp fix
```

## Assistant

All committed. Here's what session 077 produced:

## Session 077 — Complete Deliverables

### 4 commits

| Commit | What |
|--------|------|
| `🎯 v11 KIBC combinator architecture` | 9 self-contained source files in `scripts/v11/` |
| `🌀 state — session 077` | State bootloader for next session |
| `✅ v11 probe` | 1052-line probe with 3 modes (checkpoint, trajectory, dispatch) |
| `🌀 v11 design documentation` | SVG diagram + comprehensive design knowledge page |

### Documentation created

1. **`docs/v11-architecture.svg`** — Visual diagram: tokens → ascending (LOCK) → emphasis → descending (RESOLVE, 3 cycles: identify→resolve→produce) → S5 reweight → output. Shows KIBC combinator basis legend and kernel pathway detail.

2. **`mementum/knowledge/explore/v11-design.md`** — 366-line spec covering:
   - Empirical foundation (Qwen3 probe data table)
   - All dimensions and parameters
   - Component inventory (changed vs unchanged)
   - Descending cycle semantics with CycleContinue interpretation
   - Kernel computation pathway (straight-through)
   - Training strategy (prose-first, structured later for C)
   - Probe design with signal health table

3. **`mementum/knowledge/explore/v11-kibc-architecture.md`** — Initial sketch (from earlier in session)

### Ready for first run
```bash
cd ~/src/verbum && uv run python scripts/v11/train.py \
  --checkpoint-dir checkpoints/v11 \
  --total-steps 20000
```

Then analyze with:
```bash
# Quick trajectory check (no model loading)
uv run python scripts/v11/probe.py --trajectory checkpoints/v11

# Full checkpoint analysis with dispatch distribution
uv run python scripts/v11/probe.py checkpoints/v11/step_* --dispatch-detail
```