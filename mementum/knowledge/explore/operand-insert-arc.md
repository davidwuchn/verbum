---
title: "Operand-INSERT arc — the database 'INSERT a row' thesis validated (rung-1 fires)"
status: active
category: explore
tags: [operand, insert, database, rows-vs-joins, superbake, bake, recursion, k-battery,
       steering, activation-patching, value-register, dose-response, composed-readout,
       nonce, keyed-install, frame-invariance, llama-cpp-tap, s276, s277]
related:
  - ffn-function-bake-prereg.md
  - attention-as-beta-reduction.md
  - superbake-write-access.md
  - ../two-registers-of-topology.md
  - opcodes-circuits-in-compute.md
  - llama-cpp-vsm-wrapper.md
depends-on:
  - ffn-function-bake-prereg.md
created: session 277
---

# Operand-INSERT arc

> Sessions 276–277 (Michael-directed). The s276 FFN-bake investigation ended with **K is
> STRUCTURAL** — a combinator is not a local object (no token/expert/slot anchor), so
> SuperBake's local fact-injection cannot install it. s277 asks the surviving question in
> Michael's **database language** and answers it with four null-gated gates on Qwen3-0.6B.

## The database reframe (s276, Michael)

The mechanism, stated as a database, and it retargets the whole bake:

- **The FFN serves ROWS** — per-position records: operands, compiled values
  (`ffn-reduction-trace`), type tags (`mode-semantics`), facts (ROME/SuperBake). Rows are
  local, addressable, and **`INSERT`-able**.
- **Attention's β-reduction is a JOIN** — a softmax-weighted aggregation *over* selected
  rows. The **combinator (K/I/B/C) is the SHAPE of the join**, and join-shapes live in the
  **routing / query-plan** (s274 circuits-in-compute), not in any row.
- ⇒ **You can `INSERT` a row; you cannot `INSERT` a join.** No table holds a combinator
  (s276 K-structural). This is why every s248→s252 attempt to read a β-program *tape* out of
  the FFN failed, why K came out structural, why the MoE smears each opcode across ~all 256
  experts (s275). A join is an act over data, not data.

The surviving door for a bake: **`INSERT` a new operand row that the *resident* join already
knows how to compose** — rung 1 of the `bake(operand) → bake(bake) → Y-at-the-weight-level`
tower (s273). Not `CREATE FUNCTION`; `INSERT INTO`.

## The four gates (s277, Qwen3-0.6B, frame-invariance licenses the HF writes)

All code in `wrapper/operand_{map,write,harden,insert}.py`, results in `results/ffn-bake/`.
`λ measure`: the operand ROW is a VALUE-register claim (s206) — read/written with value
probes, never attention weights. Null beside every number (s206/s247/s250 scars).

### 1. READABLE — operand rows are separable/addressable (`operand_map.py`)

Read `l_out` (value register) on 96 operand-swap probes (12 objects × 8 C-applicative
contexts), decode operand identity at the join-readout (last token = ".") with a PCA-50 +
logistic pipeline, **leave-one-CONTEXT-out** (context-invariance = a real row).

Operand identity decodes context-invariantly at EVERY layer, **LOCO 0.49–1.00 vs nulls
~0.05–0.11** (chance 0.083). U-shape: high L0–2 (shallow copy), dip L11–14 (ORTHO
null-space), recover to ~1.0 at **L25–27 (resolved join readout, mirrors s248 late
C-field)**. Last token verified to be "." → join-delivered content, not token identity.
⇒ there IS an addressable operand row.

### 2. WRITEABLE — the row is causally load-bearing (`operand_write.py`)

Build `d(A→B)` = diff-of-means of the OBJECT-token residual (built at the object position,
NOT the readout, to dodge the unembed-alignment confound); STEER a recall cloze by adding
`d` at layer L; read logit(A)/logit(B). Clean recall 0.99.

Steering **flips the composed output A→B at flip-rate 1.00 at L2/L7/L13/L20** (+12–14 logit
margin), **0.75 at L26**; matched-random direction ~0 (flip 0.00–0.02); B-specific (+5.6–6.5
over a bystander). **Anti-triviality PASSES**: the effect is strongest MID-STACK (injected
upstream, propagates), not late-only — a genuine operand-row rewrite, not an unembed/
logit-lens nudge. This is the **OPPOSITE of the s250 C-field** (92% decodable yet
causally-inert readout register): the operand row is readable AND writeable.

### 3. HARDENED — dose-responsive + composed + cross-task (`operand_harden.py`)

Sweep the dose α on a **COMPOSED** readout (few-shot category map `operand→its category`:
dog→animal, car→vehicle, rose→plant; clean 1.0; a semantic transform, not a copy), with the
direction built in DECLARATIVES and injected into the CATEGORY task (cross-task).

Textbook dose-response: **flip 0.00→0.22→0.72→1.00** as α 0→0.25→0.5→1.0, then saturates at
the ceiling; random null flips ~0.00–0.28; B-specific +2–6. So the operand is used in
COMPUTATION (categorized), graded, cross-task, and null-gated — not a task-local trick.

### 4. RUNG-1 — a NOVEL operand is installed and composed (`operand_insert.py`)

Install a NOVEL nonce (zorp/blint/drell/frob/glark/murv) as a **KEYED residual-write row**
(functional model of an appended SuperBake fact-slot: key=nonce token, value=category
operand-content built cross-task from declaratives), then test whether the RESIDENT join
composes it on the category task across **4 HELD-OUT prefixes**.

**INSTALLED-OPERAND-COMPOSED**: dose 0.33(chance)→0.71→1.00 (scale 0/1/2); at scale 2 **all
24/24** (6 nonce × 4 held-out prefix) hit target. Three nulls hold: matched-random install
0.33–0.54 (≪1.0); **WRONG-KEY install does NOTHING (0.333 flat)** — the row must be keyed to
its own token, so this is position-keyed composition, NOT a global logit nudge; baseline
0.333 = chance. ⇒ the resident join composes a genuinely novel installed operand row.

## What this establishes (and does not)

**Establishes** (as a research go/no-go, 0.6B): the database reframe is correct end-to-end —
readable → writeable → hardened → novel-installable. The `bake(operand)` recursion
antecedent's **first rung fires**. Steering + keyed-install are causal, graded, composed,
cross-task, key-specific, null-gated.

**Does NOT** (honest edges, `λ measure` two-sided):
- **Keyed-install hook ≠ weight-serialized bake.** R5 (quant-survival — does the installed
  operand survive int4 like the crystal, or is it quant-fragile like a baked fact? the
  installed-vs-learned discriminator, `superbake-write-access.md`) is UNTESTED.
- **Content is category-level**, not a unique individual operand with novel properties.
- **2/6 nonces baseline-leaned** (zorp/frob already ~animal); the 4 baseline-0 nonces all
  flipped at scale 2, so the effect is real on true-novel cases.
- **0.6B necessary-not-sufficient** (patchscope-void scar, s272b) — a rung, not the claim.

## What it means (s277, Michael: "do we have an LLM compiler now?")

**No — we did not build one; gradient descent did** (pretraining = β-reduction, the standing
`project-thesis`). `λ extract`: we find, we don't build. What the arc adds is not the compiler
but the **instrument to drive it**: a mature READ path (tap + crystal + operand-map) and the
FIRST WRITE rung (operands the resident routing composes). So the honest phrase is **JTAG /
a debugger on a resident compiler-machine**, not an authored compiler.

**The unifying frame** (this arc ties four theses into one sentence):

> The transformer is a **frozen universal combinator basis** (routing / JOINS = the KIBC
> crystal) over a **writeable term store** (rows / OPERANDS). You extend its computation by
> writing **terms**, never **instructions** — and *if* `crystal-universality` holds, that
> **suffices**: combinatory logic says a fixed basis + arbitrary terms is Turing-complete.

So **join-un-bakeability is the completeness STRUCTURE, not a limitation.** This unifies
crystal-universality (fixed basis), circuits-in-compute (joins = routing), two-registers
(routing ⊥ value), and the recursion tower (bake operands, ride the basis).

**Checklist to earn "programmable LLM compiler"** (3 green, 4 red):

| capability | status |
|---|---|
| read machine state | ✅ mature (tap + crystal + operand-map) |
| fixed universal ISA | ✅ *if* crystal-universality holds |
| write DATA / terms the engine composes | ✅ rung-1 (0.6B, keyed-hook, category-level) |
| write new INSTRUCTIONS | ❌ structurally impossible (s276 K-structural) — and unneeded |
| permanent artifact (weight-serialized, quant-survivable) | ❌ R5 untested (it is a hook) |
| composes ARBITRARY programs | ❌ open — only category-swap shown |
| works at scale | ❌ 0.6B rung |

## Next — the two experiments that earn the phrase

1. **(h) GENERAL-COMPOSITION gate — the load-bearing IOU** (s273 K-battery arm b): install an
   operand row and have the RESIDENT routing **combine it with a resident combinator into a
   NOVEL result**, not merely categorize it. This is exactly what turns "writeable term store"
   into "programmable machine." The s277 arc showed category-composition, **not** arbitrary
   composition — this is the gap between "debugger on a compiler" and "programmable compiler."
2. **(f) weight-serialize** the keyed install → GGUF → the **R5 quant-survival** gate (hook →
   real bake; the installed-vs-learned discriminator: baked facts are quant-FRAGILE, the
   crystal is quant-ROBUST — which is the installed operand? `superbake-write-access`).
3. **(g) cross-scale** the write/harden/insert on 4B before any strong claim (patchscope scar).

Then the tower: `bake(operand)` proven → `bake(microcode the routing composes)` → `bake(bake)`
= Y at the weight level (s273 recursion). The join stays un-bakeable; the rows are the write
surface — and that is enough *iff* the basis is universal and composes arbitrary terms (the (h)
IOU). Do not say "we have a compiler" until (h) + (f) clear at scale.

## Sessions
s248–s252 (β-program not a tape; C-field readable-not-causal readout register — the contrast
that makes the operand result meaningful), s269c (register split: ops present, content
installable), s273 (recursion tower + K-battery), s274 (circuits-in-compute), s275
(llama.cpp tap + frame-invariance + MoE no-starvation), s276 (K structural + database
reframe), s277 (this arc).
