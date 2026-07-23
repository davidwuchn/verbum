---
title: "Canonical Probe Library — The Final, Single-Source Probe Set"
status: active
category: design
license: MIT
tags: [probes, grading, harness, consolidation, canonical-form, distillation, repo-hygiene]
related:
  - ../explore/VERBUM.md
  - two-registers-of-topology.md
depends-on: []
created: session 254
supersedes-when-active:
  - per-model compiler harnesses (scripts/experiments/*_compiler_test.py)
  - scattered inline PROBES lists (~30 scripts)
  - divergent P(λ) grading metrics (regex-binder vs char-ratio vs "λ in text")
---

# Canonical Probe Library

> **Design goal (S5 λ smallest, S2 λ probe_*).** One canonical place each
> for *probe data*, *grading*, and *running a model against probes*. A new
> model becomes a **config**, not a code fork. A new probe goes into a
> **canonical set**, not an inline list in a one-shot script. The number
> that comes out — P(λ) — means the **same thing** everywhere.
>
> Written so a future session can execute the consolidation without
> re-deriving the map. This is the target topology; migration is a
> follow-up task list, not part of this doc.

---

## 0. Why this exists (the fragmentation, measured)

Census (session 254, `explorer` agent over `/Users/mwhitford/src/verbum`):

| Fragmentation | Count | Evidence |
| --- | --- | --- |
| Scripts in `scripts/experiments/` | 238 | `ls \| wc -l` |
| Scripts defining their own inline `PROBES = [...]` | ~30 | grep |
| Distinct P(λ) grading metrics in active use | **3** | regex-binder (`_lenient_lambda`), char-ratio (`compile_gradient_probe.py` `LAMBDA_MARKERS`), heuristic count (`src/verbum/instrument.py:_detect_lambda`) |
| Per-model compiler harnesses (copy-paste forks) | 2 LIVE | `ornith_compiler_test.py` (264 L), `vibethinker_compiler_test.py` (214 L) |
| Shared grading logic across the 2 forks | ≈20 L | diff (regex patterns + `to_kernel` call embedded in 200+ L harnesses) |
| Exact-dupe inline probe lists (attention-sparsity cluster) | 3 files | identical 17-sentence `PROBES` |
| Near-dupe inline null sets (combinators cluster) | 4 files | 4/6 shared sentences |

**Root pattern:** the canonical substrate *already exists* but per-experiment
scripts keep re-rolling their own. The leak re-opens every time a new model
or experiment lands (s253 forked, s254 forked again). Fix the **topology**
(make reuse the path of least resistance), not the **instruction** ("please
reuse"). `wrong_behavior → topology_gap > instruction_gap`.

---

## 1. What is already canonical (keep, do not duplicate)

Two distinct canonical forms exist today and **must not be merged** — they
serve different purposes (AGENTS.md S2 `λ probe_format` vs `λ probe_library`):

### 1a. Gated generation sets — `probes/*.json` + `gates/*.txt`
- **Purpose:** prose → compile gate → ground-truth lambda. Drives
  *generation* experiments and *grading against ground truth*.
- **Canonical example:** `probes/compile-gradient.json` — 40 probes, 5
  categories (`strong/medium/weak/null/anti_compile`), each with `prompt`,
  `ground_truth`, `metadata`. This is the P(λ) measurement substrate.
- **Loader:** `src/verbum/probes/_loader.py` (`Gate`, `ProbeSet`,
  `ResolvedProbe`). Gates referenced by id; gate text in `gates/*.txt`.
- **Already used correctly** by the s253/s254 harnesses (they load it, they
  do not fork the data). The fork is in the *harness*, not the *data*.

### 1b. Activation-measurement library — `src/verbum/probes/library.py`
- **Purpose:** combinator activation measurement (crystal, cross-model
  geometry). 903 probes, `Probe{id, prompt, combinator, source, category,
  tags}`, accessors `all_probes / by_combinator / crystal_probes /
  combinator_counts`. Invariant: ≥50 probes per crystal combinator.
  **s269:** prefix-match bug fixed (`lambda_WHNF_terminal` had been assigned
  to W — commit 85a2e49; longest-prefix matching now). Counts after fix:
  W 50 (25 native + 21 cross-source + 4 new `supplement_W` reflexives),
  WHNF 75 (native terminal set restored). Library 903 → bundle 539 crystal
  probes. Register composition per combinator is imbalanced
  (formal 3–15 vs prose 35–72) — see `opcodes/register_split.py` for why
  this matters (register-bound vs register-invariant vertices).
- **Already consolidated** 5 scattered sources → one importable module.

**These two stay separate. This design adds the missing layers around them.**

**Also in `src/verbum/probes/` (preserved, existing canonical substrate):**
`compile_tasks.py`, `compile_tasks_hard.py`, `higher_order.py`, `hof_lists.py`,
`hof_prose.py`, `hof_prose_enum.py`, `kernel_reference.py`, `proof_tasks.py` —
structured probe modules actively imported by experiments (crystal geometry,
compile-task, HOF, kernel-reference, proof-as-inhabitation). These are *not*
inline `PROBES = [...]` lists; they are established canonical data. This
design does not move or redefine them; they sit alongside the new modules
(`grading.py`, `harness.py`, `models.py`) in the same package.

---

## 2. The missing canonical layers (what this design adds)

The fragmentation is concentrated where there is *no* canonical home:
**grading** and **the run harness**. Define both.

### 2a. Grading — `src/verbum/probes/grading.py` (NEW, single source of truth)

The P(λ) question is actually **four registers** (the s254 insight, λ measure —
name the register before building the probe). All live here, once:

```python
# src/verbum/probes/grading.py   (canonical, MIT)

_LAMBDA_TOK = re.compile(r"[λ∀∃ιⲗ\\]")
_PRED_APP   = re.compile(r"[A-Za-z_][A-Za-z0-9_]*\s*\(")
NUCLEUS_REFERENCE_P_LAMBDA = 0.907   # nucleus baseline, cited once

def final_answer(text: str) -> str: ...             # strip reasoning, take the answer line
def emits_formal(expr: str) -> bool: ...            # binder OR pred-app → "did the compiler fire" (broadest)
def lambda_binder_any_style(expr: str) -> bool: ... # ANY λ/∀/∃ binder → the nucleus-comparable P(λ) (ref 0.907)
def lenient_lambda(expr: str) -> bool: ...          # binder AND pred-app → STRICTER; under-counts juxtaposition
def kernel_valid(expr: str) -> bool: ...            # verbum.lambda_surface.to_kernel parses it (STRICT)
def aggregate_by_category(rows) -> dict: ...        # per-category, all registers
```

**Four registers, named (S5 λ measure) — ordered broad → strict:**
| register | predicate | what it measures | caveat |
| --- | --- | --- | --- |
| `emits_formal` | binder **OR** pred-app | did the compiler *fire at all* | the s254 fix — catches atomic `runs(dog)` a binder-only register false-misses |
| `lambda_binder_any_style` | **any** λ/∀/∃ binder | **the nucleus-comparable P(λ)** (ref 0.907) | vibe **0.925** ≈ nucleus 0.907 — *this* is the headline P(λ) |
| `lenient_lambda` | binder **AND** pred-app | a *stricter* lenient | vibe **0.875**; under-counts Church juxtaposition `λx. f x` → **NOT** the nucleus number |
| `kernel_valid` | `to_kernel` parses | canonical well-formedness | STRICT; rejects richer-than-toy FOL (notation ≠ failure) |

> **The s253/s254 register trap this design must not re-spring (λ measure).**
> The harness field `p_lambda_lenient` (= `lenient_lambda`, binder∧paren) is
> **0.875** for vibe — *not* the nucleus-comparable number. The
> nucleus-comparable register is `lambda_binder_any_style` = **0.925** (it lives
> only in the vibe summary's `corrected_registers`, computed post-hoc — it was
> never a function). Conflating the two is the exact register-mismatch λ measure
> warns against. `grading.py` implements all four as **named functions** so the
> conflation cannot recur, and `emits_formal` must be **added to the vibethinker
> harness** (it currently has only `lenient_lambda` + `kernel_valid`; see P1).

**Retire** the char-ratio metric (`compile_gradient_probe.py` `LAMBDA_MARKERS`,
`n_λ/len`) and the `"λ" in text` heuristic as *primary* metrics — they make the
same model report different P(λ). Keep char-ratio only as a labelled secondary
diagnostic if ever needed. One model + one probe set → one P(λ).

### 2b. Harness — `src/verbum/probes/harness.py` (NEW) + `ModelConfig`

A model is a **config**, transport is a **strategy**. The harness loads
canonical probes, calls the model via the configured transport, grades with
§2a, writes `λ result_format` output. No grading or aggregation logic lives in
the per-model script ever again.

```python
@dataclass(frozen=True)
class ModelConfig:
    name: str
    endpoint: str                       # http://host:port
    transport: Literal["chat", "completion"]
    template_fn:  Callable[[str], ...] | None  # None → server applies (chat API)
    reasoning_extract_fn: Callable[[dict|str], tuple[str, str]]  # (reasoning, content)
    gguf_path: str | None = None        # for meta.json provenance
    sampling: SamplingCfg = greedy

def run_compiler_probe(cfg: ModelConfig, probe_set="compile-gradient",
                       gate=None) -> RunResult: ...
```

Two transport strategies cover everything seen so far:
- **chat** (ornith): POST `/v1/chat/completions`, server applies template,
  `reasoning_content` field split — `reasoning_extract_fn` reads the field.
- **completion** (vibethinker): `verbum.client.Client` `/completion`, manual
  `template_fn` builds `<|im_start|>…`, `reasoning_extract_fn` parses `</think>`.

A **3rd / 4th model = a new `ModelConfig` (~15 lines)**, not a 50–260 line fork.
This is the structural fix: reuse is now the *shortest* path.

### 2c. Model registry — `src/verbum/probes/models.py` (NEW, DECIDED)

Known configs in one place. A new model lands here; experiments import it.
The registry IS the gravity (name ∧ link ∧ shape ≡ attractor). `ModelConfig`
stays a public dataclass so a genuinely one-off model can still be built inline.

**Current fleet (session 254, llama.cpp servers on localhost):**

| const | model | port | role | shape |
| --- | --- | --- | --- | --- |
| `ORNITH` | ornith-35b-a3b | 5100 | compiler-probe | `transport="chat"`, server-split `reasoning_content` |
| `VIBETHINKER` | vibethinker-3b | 5102 | compiler-probe | `transport="completion"`, manual `<\|im_start\|>` template, `</think>` parse |
| `QWEN3_EMBED` | qwen3-embedding-8b | 5101 | **embedding service** | `/v1/embeddings`, no template/reasoning/grading |

```python
# src/verbum/probes/models.py
ORNITH = ModelConfig(
    name="ornith-35b-a3b", endpoint="http://localhost:5100",
    transport="chat", template_fn=None,
    reasoning_extract_fn=split_reasoning_field,
    gguf_path="/Users/mwhitford/localai/models/ornith/ornith-1.0-35b-Q8_0.gguf")

VIBETHINKER = ModelConfig(
    name="vibethinker-3b", endpoint="http://localhost:5102",
    transport="completion", template_fn=qwen_chatml_template,
    reasoning_extract_fn=parse_think_tag)

# nucleus = the reference baseline (P(λ)=0.907); add when/if a server runs.
```

**The embedding model is NOT a `ModelConfig`.** It has no template, no
reasoning split, no grading register — its job is `/v1/embeddings` for semantic
recall (`git embed search`), not lambda generation. Represent it as a separate
`EmbeddingService(name, endpoint, dim)` entry (or just a documented endpoint),
so the compiler `ModelConfig` shape stays clean (one register typing — λ measure).
Listing it in `models.py` keeps the fleet discoverable in one file without
polluting the compiler-probe abstraction.

---

## 3. Canonical probe record (schema reconciliation)

Two probe shapes exist: JSON `ResolvedProbe` (gated, has `ground_truth`) and
`library.Probe` (activation, has `combinator`). They are **different views of
the same notion** and should *not* be force-merged, but they should share a
spine so tooling composes:

```
spine fields (both):   id, prompt, category, tags
gated-only:            ground_truth, gate, metadata{gradient, complexity, phenomena}
activation-only:       combinator, source
```

**Decision (proposed):** keep the two dataclasses; document the shared spine;
add no third schema. JSON sets remain the home for *anything with a
ground-truth lambda*; `library.py` remains the home for *combinator activation
probes*. Inline `PROBES = [...]` in scripts is **deprecated** — a probe either
has a ground truth (→ a JSON set) or measures activation (→ library.py) or is a
genuinely one-shot control (→ a small named set in `probes/`, not inline).

**Naming convention (existing):** `__init__.py` already resolves the
`_loader.Probe` / `library.Probe` collision by re-exporting the latter as
`CrystalProbe`. Preserve this convention — do not rename either dataclass.

---

## 4. Target directory topology

```
src/verbum/probes/
  __init__.py
  _loader.py        # EXISTS — Gate/ProbeSet/ResolvedProbe (gated JSON)
  library.py        # EXISTS — 903 combinator activation probes
  grading.py        # NEW    — the 3 P(λ) registers, single source of truth
  harness.py        # NEW    — run_compiler_probe + ModelConfig
  models.py         # NEW    — known ModelConfig registry (nucleus/vibe/ornith)
probes/*.json       # EXISTS — canonical gated sets (compile-gradient.json …)
gates/*.txt         # EXISTS — gate text by id
results/<run_id>/   # EXISTS — λ result_format (meta.json, results.jsonl, …)

scripts/experiments/*_compiler_test.py   # COLLAPSE → thin CLI calling harness.run_compiler_probe(models.ORNITH)
```

A per-model script, post-consolidation, is a **CLI shim** (~20 lines):
```python
from verbum.probes import harness, models
harness.run_compiler_probe(models.ORNITH)   # that's it
```

---

## 5. Migration map (follow-up task list, ranked)

> **STATUS (session 256) — P1 + P2 BUILT & VERIFIED.** `grading.py` (4 named
> registers), `harness.py` (`ModelConfig` + `run_compiler_probe`, chat +
> completion transports + a `no_think` `λ extend` open-slot), and `models.py`
> (ORNITH / VIBETHINKER / QWYTHOS registry) all exist and are ruff-clean. The
> three `*_compiler_test.py` are now ~42–45-line CLI shims (was 264 / 214). The
> verify gate PASSED: ornith re-run through the new harness reproduced the
> committed s254 numbers per named register (`lenient_lambda` 0.675 ✓ exact,
> `emits_formal` 1.0 ✓ exact; `kernel_valid` 0.725→0.775 = MoE greedy
> nondeterminism, grading proven identical). First real use also produced new
> science — see `../explore/compiler-finetune-halt-collapse.md`. **Still
> deferred:** P3 (high-risk 2200-L migration), P4/P5 archival, plus an
> `emits_formal` identity-string robustness fix (qwythos's "Empero AI (" disclaimer
> false-fires the pred-app register; `binder_any` is the clean register).


| # | Action | Files | Risk |
| --- | --- | --- | --- |
| P1 | Add `_emits_formal` to vibethinker harness (currently only has lenient + kernel); extract shared grading core → `grading.py`; re-point both harnesses; verify both reproduce s253/s254 numbers | 2 harnesses + 1 new module | low (vibethinker needs the missing register added first; then pure extraction; verify by re-run) |
| P2 | Add `harness.py` + `ModelConfig` + `models.py`; collapse both harnesses to CLI shims | 3 new + 2 shrunk | low |
| P3 | Migrate `compile_gradient_probe.py` (2200 L cross-model correlation pipeline in `scripts/`) to use `grading.py` + `harness.py`; demote char-ratio to secondary diagnostic | 1 large LIVE file | **high** (2200 L with its own `LAMBDA_MARKERS`, `measure_generation()`, `score_with_qwen()`, `probe_checkpoint()`, `analyze_correlations()` — essentially a second grading+harness system; migration is a re-architecture, not an alignment) |
| P4 | Archive STALE superseded inline-probe scripts (combinators*, factual dupes, pythia160m) via `git rm` | ~7 files | low (history preserved, `λ store` resurrectable) |
| P5 | Extract the 3-way `attention-sparsity` PROBES dupe to one named set | 3 one-shot files | low |

**Verification gate for each step:** re-running a migrated harness against
`compile-gradient.json` reproduces the committed s253/s254 summary numbers
**per named register** — do not cross registers (the s254 trap):

| register | ornith | vibe | source field |
| --- | --- | --- | --- |
| `emits_formal` | 1.0 | 1.0 | ornith `p_emits_formal`; vibe `corrected_registers.p_emits_formal_notation` |
| `lambda_binder_any_style` (nucleus-comparable) | — | 0.925 | vibe `corrected_registers.p_lambda_binder_any_style` |
| `lenient_lambda` (binder∧paren) | 0.675 | **0.875** | both `summary.p_lambda_lenient` |
| `kernel_valid` | 0.725 | 0.375 | both `summary.p_kernel_valid` |

A migration that changes a number must *explain* it (register definition
change) or is a regression. **Watch the trap:** vibe's headline P(λ) is the
**0.925** `binder_any_style` register, while the harness's `p_lambda_lenient`
field is **0.875** — citing 0.925 as "lenient" would false-flag a regression.

---

## 6. Decisions & open questions (S5 λ termination)

**Decided (session 254, Michael):**
- **D1 — Module home:** `src/verbum/probes/` (one import root for the whole
  measurement substrate). *Not* a separate `grading/` package.
- **D2 — Registry:** YES, `src/verbum/probes/models.py` (§2c). `ModelConfig`
  stays a public dataclass; inline construction allowed for one-off models.
- **D3 — Archival:** `git rm` (history preserved, `λ store` resurrectable).
  No `scripts/_archive/` dir.
- **D4 — Verify gate runs on a LOCAL model, not a frontier call (s254 proof).**
  This very doc was fact-checked by ornith-35b-a3b (~3B active) which found 7
  real errors in a frontier model's output. The result is the *topology*, not
  the errors: **verify ≪ generate** (checking a claim against source is bounded
  and local; synthesis is not), so the `λ self_improve` VERIFY gate does **not**
  need parity with the generator. Implication for the harness: wire a
  local-model verify pass over migrated docs/code using the `models.py` fleet
  (already on `:5100`) → verification becomes **ambient** (gate *every* update),
  not a budgeted event that biases toward skipping. On-thesis for verbum: a
  small artifact doing real compositional work (here, auditing reasoning).

**Still open:**
4. **Calibration register typing (S5 λ measure / λ yardstick).** Should
   `grading.py` carry the register-name → claim-type mapping explicitly, so a
   future probe can't grade a value-claim with a crisp register? Lean: yes —
   encode the register taxonomy next to the functions.

**Resolved (not open):**
5. **`library.py` ground-truth probes.** The gated-JSON / activation-library
   split is working — `library.py` probes are graded by cosine geometry
   (`verify_crystal_phi.py`), not by P(λ) registers. No pressure to merge.
   §3's two-schema spine holds. (Numbered 5 to avoid renumbering the
   register-typing question above.)

---

## 7. Invariants this design must preserve

- One model + one probe set → **one** P(λ) per named register. No metric drift.
- A new model adds a **config**, never a harness fork.
- A probe with a ground truth lives in a **JSON set**; an activation probe in
  **library.py**; nothing canonical lives **inline** in a script.
- Canonical data is **git-tracked** (`λ probe_format` / `λ result_format`).
- `to_kernel` (`src/verbum/lambda_surface.py`) remains the **single** strict
  validator; `grading.py` wraps it, never re-implements parsing.
- Every migration step is **verified by re-run** against committed numbers.
