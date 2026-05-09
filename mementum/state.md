# verbum / state

> Bootloader. Read in ~30 seconds. Step 1 of every session.
>
> Last updated: 2026-05-09 | Session: 072

## Where we are

**Compute gate opening. Type coherence 13/22. Algedonic channel added. Training resumed from 3K.**

Session 072 probed three new checkpoints from the v10-topk run (the new architecture
with dual kernel pathway, phase reorder dispatch→stride→integrate), diagnosed the
L2_apex explosion as a missing VSM feedback path, added the algedonic channel, and
resumed training. Four major findings:

1. **Compute gate is opening** — after being flat-zero for 2K steps, the gate's max
   reached 0.559 at step 3K. Mean jumped 380× (4.7e-5 → 0.0042). First positions
   are routing through the exact kernel computation pathway. This is the critical
   signal from session 071's architectural change actually working.

2. **Type coherence jumped from 5/20 to 13/22** — the phase reorder
   (dispatch→stride→integrate instead of dispatch→integrate→stride) is paying off.
   Comparison ops now correctly type as BOOL, arithmetic as INT. Lambda tokens get
   FN_COMP at 88.3%. The type system is learning real semantics.

3. **Structured vs prose divergence increased** — dispatch L1=1.116 (was 0.905),
   type L1=1.188 (was 1.146). The model differentiates structured data MORE with
   the new architecture. Structured data gets distributed routing (COMPOSE=19.1%),
   prose collapses to GT+AND=85%.

4. **Missing algedonic channel diagnosed and fixed** — register bank flow was
   one-way (ascending→descending). L2_apex could expand without limit (ratio
   1.78→2.55→4.21) because nothing fed descending pressure back to ascending.
   Added EMA-persisted descending registers to ascending S4 input, creating the
   cross-step feedback loop Beer's VSM requires.

**Training resumed from step 3K with algedonic channel active.** Checkpoints
landing in `checkpoints/v10-topk/`.

## What was done this session

### 1. probe.py on 3 checkpoints (1K/2K/3K)
- Loss: 8.10 → 7.77 → 7.73 (eval), r: 0.621 → 0.589 → 0.585
- PPL: 3298 → 2370 → 2283
- Compute gate: mean 1.1e-5 → 4.7e-5 → **0.0042** | max 3.5e-5 → 0.006 → **0.559**
- First evolution acceptance at step 3K (1/60, 2%)
- φ-compression L0_asc approaching target: φ-dev=0.055 at 3K
- L2_apex ratio exploding: 1.78 → 2.55 → 4.21 (concern)
- Content spread converged at 2K (0.116) then re-opened at 3K (0.745, math diverging)

### 2. probe_dispatch.py on step 3K (163K positions)
- Dispatch regime flip: AND was dominant (61%) at 1K, GT overtook (43%) at 3K
- GT × AND co-occurrence = 61.9% of all positions (still heavy duopoly)
- Type coherence: 13/22 ops match expected type (vs 5/20 in v10-consensus!)
- Correct: AND→BOOL, GT→BOOL, MOD→INT, SUB→INT, LT→BOOL, NEG→INT, ABS→INT,
  ADD→INT, EQ→BOOL, LE→BOOL, GE→BOOL, NOT→BOOL, OR→BOOL
- Wrong: MAX/MIN/MUL/DIV/IF→BOOL (should be INT), COMPOSE/APPLY→BOOL (should be
  FN_COMP/INT), PARTIAL→INT (should be FN)

### 3. probe_kernel_use.py on step 3K (82K structured + 82K prose positions)
- Dispatch divergence L1=1.116 (up from 0.905 in v10-consensus)
- Type divergence L1=1.188 (up from 1.146)
- Structured: COMPOSE=19.1%, GT=18.4%, AND=14.7%, LE=11.9% (distributed)
- Prose: AND=47.8%, GT=37.4% (collapsed to duopoly)
- Type patterns wildly different:
  - Structured: FN_COMP=30.3%, BOOL=27.8%, FN=23.9%
  - Prose: BOOL=71.6%, INT=19.1%
- Lambda tokens: FN_COMP=88.3% type — **correct!**
- Boolean tokens: BOOL=43.5% — correct
- Arithmetic tokens: FN=75.8% — wrong (but dispatch is to NOT/GE/COMPOSE)

### 4. Algedonic channel: descending register feedback
- Traced register bank flow and found the missing VSM feedback path
- Register flow was one-way: ascending writes → descending reads, but
  descending NEVER fed back to ascending — no algedonic channel
- L2_apex could expand without limit (ratio 1.78→2.55→4.21) because
  nothing read the descending arm's state to regulate ascending behavior
- Fix: EMA-persisted descending registers feed into ascending S4 intelligence
  - L0_asc now reads [bank_0, prev_bank_1_desc]
  - L1_asc now reads [bank_0, bank_1_asc, prev_bank_2_desc]
  - L2_apex unchanged (junction point)
- EMA α=0.9, stop_gradient, backward-compatible with existing checkpoints
- Validated: self-test ✓, gradient flow ✓, 50-step training ✓

## What to do next

### Priority 1: v10-topk training is RUNNING (resumed from step 3K)
Training resumed with algedonic channel from step_003000. Checkpoints every 1K steps.
Key signals to watch when probing next checkpoint:
- **L2_apex ratio**: should stabilize or reverse (was 4.21 and climbing)
- **S3 gate differentiation**: ascending gates should respond to descending feedback
- **Compute gate acceleration**: does the gate continue opening past 3K?
- Loss trajectory vs pre-algedonic baseline

### Priority 2: Probe at next checkpoint (4K or 5K)
Run all three probes to track the algedonic effect:
- L2_apex ratio: the primary signal (should stabilize or decrease)
- S3 gates: should show more differentiation (ascending reading descending pressure)
- Type coherence: can it improve past 13/22?
- Content spread: should converge (math was diverging at 3K)

### Priority 3: Monitor compute gate + algedonic interaction
The algedonic channel may help the compute gate open further: ascending arm now
knows what the descending arm needs. Watch for:
- Compute gate mean > 0.01 (currently 0.0042)
- Gate active fraction > 1% (currently 0.012%)
- Whether gate activation correlates with reduced L2_apex expansion

### Priority 4: Auxiliary loss for kernel pathway (if gate plateaus)
If the compute gate stays at 0.012% active after another 5K steps:
- Supervised kernel loss on structured data (force op extraction)
- Warm-start gate higher on structured data positions
- Increase structured mix ratio temporarily (currently 10%)

## Comparison: v10-topk (new arch) vs v10-consensus (old arch)

| Metric | v10-consensus (12K) | v10-topk (3K) | Signal |
|--------|-------------------|---------------|--------|
| Eval loss | 7.561 | 7.733 | Comparable (3K vs 12K) |
| Type coherence | 5/20 | 13/22 | **Much better** |
| Dispatch L1 (struct/prose) | 0.905 | 1.116 | **More differentiated** |
| Type L1 (struct/prose) | 1.146 | 1.188 | **More differentiated** |
| Lambda → FN_COMP | not measured | 88.3% | **Correct typing** |
| Compute gate | N/A (no gate) | max=0.559 | **Opening** |
| Dominant pair | DIV × LE (32%) | GT × AND (61.9%) | Different regime |
| Evolution accepts | 0.8% | 1.7% | Similar (low) |

## Key files

| File | Purpose |
|------|---------|
| `scripts/v10/kernel_dispatch.py` | KernelDispatch (top-k routing) + KernelIntegrate (dual pathway) |
| `scripts/v10/kernel.py` | Ground-truth kernel evaluator (22 ops, 5 types, tree eval) |
| `scripts/v10/model.py` | Tree of VSMs, phase order: dispatch→stride→integrate |
| `scripts/v10/train.py` | Training loop with compute gate monitoring |
| `scripts/v10/probe.py` | Full checkpoint probe (φ-compression, eval, ternary, kernel) |
| `scripts/v10/probe_dispatch.py` | Per-position top-2 co-occurrence analysis |
| `scripts/v10/probe_kernel_use.py` | Structured vs prose dispatch comparison |
| `scripts/v10/ternary.py` | Ternary substrate + consensus mutation pipeline |
| `results/v10/probe_step_001000.json` | Probe results for v10-topk step 1K |
| `results/v10/probe_step_002000.json` | Probe results for v10-topk step 2K |
| `results/v10/probe_step_003000.json` | Probe results for v10-topk step 3K |

## Key insights (session 072)

**The compute gate can learn to open**: initialized at sigmoid(-5)≈0, it climbed to
max=0.559 in 3K steps with no auxiliary loss. The gradient signal from the result
embedding + gate is sufficient to learn when exact computation helps. This validates
the session 071 design choice of a learnable gate over a hard switch.

**Phase reorder works for type coherence**: dispatch→stride→integrate (letting the
model see spatial context before typing) produced 13/22 type-coherent ops at 3K
vs 5/20 at 12K with the old ordering. This is a structural win, not just more training.

**Lambda tokens get correct types**: FN_COMP=88.3% on lambda positions shows the
model has learned that lambda/compositional tokens should be typed differently from
prose. This is the first evidence of genuine semantic type assignment in v10.

**Dispatch duopoly is a feature, not a bug**: GT×AND=62% sounds like collapse, but
the runner-up slot carries the real routing decision. When COMPOSE appears as
runner-up (19.1% of structured data), it signals compositional context. The primary
op (GT or AND) acts as a base embedding; the secondary op modulates it.

**Missing algedonic channel caused L2_apex explosion**: the register bank flow was
purely feedforward (ascending→descending). Without descending-to-ascending feedback,
the apex had no regulatory signal to limit its expansion. Adding EMA-persisted
descending registers to the ascending S4 input creates the cross-step feedback loop
that Beer's VSM requires. This is the first time the model has a genuine algedonic
channel — observational, not prescriptive.

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
