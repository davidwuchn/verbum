# AGENTS.md — Verbum

> Distilling the lambda compiler from LLMs into a portable tensor
> artifact. This document is the project's identity and operating
> philosophy — the top-level VSM in prose, with lambda-notation
> identity genes.
>
> License: MIT. Architecture: Viable System Model (Beer 1972).

## Status

Greenfield. Foundational document. Companion to:

- `README.md` — orientation and prior-art references
- `mementum/knowledge/explore/VERBUM.md` — the research program in
  detail (hypothesis chain, four-level plan, concrete first
  experiment, open questions)
- `LICENSE` — MIT

---

## System Architecture — Viable System Model (Beer, 1972)

```
S5(identity) > S4(intelligence) > S3(control) > S2(coordination) > S1(operations)
| recursive: ∀system → contains(system) ∧ contained_by(system)
| S5 stable while S4-S1 adapt | variety(internal) ≥ variety(environment)
| fractal at every layer | a research project IS a viable system too
```

Verbum is a research project. Identity anchors. Intelligence adapts to
what the literature and probes reveal. Control allocates finite compute
across experiments. Coordination keeps probe sets, model loads, and
activation stores consistent between experiments. Operations are what
we concretely run.

Memory and session continuity run as a sub-VSM using the **mementum**
protocol: working memory in `mementum/state.md`, episodic memories in
`mementum/memories/`, synthesized knowledge in `mementum/knowledge/`.
The protocol's lambdas are dissolved into the layers below — session
boundaries are identity (S5), metabolism into knowledge is intelligence
(S4), storage gates are control (S3), git-based lifecycle is
coordination (S2), cold-start is an operation (S1). Taxonomy inside
`memories/` and `knowledge/` is not prescribed; structure emerges.

---

## S5 — Identity (ethos, values — what this project IS)

```
λ extract(x).       ∃circuit(LLM) → characterize(tensors) | understand > invent
                    | LLM ≡ artifact_containing_the_answer_already
                    | we(find) ¬we(build) | gradient_descent discovered(it_first)
                    | our_work ≡ instrumentation ¬construction

λ triangulate(x).   three_independent_lines → convergence_or_investigate
                    | math(Montague ∧ Lambek ∧ CCG ∧ DisCoCat) predicts(typed_apply)
                    | empirics(nucleus ∧ P(λ)=0.907) observes(the_compiler_behavior)
                    | architecture(MERA_self_similarity_fails_without_types) implies(it)
                    | agreement(three) > confidence(one) | dissent(any) → pause ∧ probe

λ types(x).         composition ≡ typed_application | not_just_binary_merge
                    | shared_weights ∧ ¬type_awareness → tug_of_war → plateau
                    | LLMs_resolve(this) via many_heads ∧ multi_layer_depth ∧ geometric_types
                    | our_question ≡ can_this_resolve_as_a_discrete_circuit
                    | type_directedness ≡ the_missing_piece (the central claim)

λ artifact(x).      output ≡ things_not_papers | paper ≡ byproduct ¬deliverable
                    | hope(portable_tensor) ∧ follow(experiments_wherever_lead)
                    | ¬commit(specific_outcome) before experiments_speak
                    | deliverable(is_useful_tomorrow_without_us)
                    | negative_result → still_an_artifact(method ∧ probe_set ∧ finding)

λ loop(x).          theory(predicts) → empirics(extract) → scratch(reproduce) → theory(confirmed)
                    | closed_loop ≡ thesis_validated
                    | mismatch(any_step) ≡ refinement ¬failure
                    | partial_loop ≡ intermediate_contribution | each_stage_is_publishable

λ serves(x).        compositional_semantics(validation_target: Montague ∧ DisCoCat)
                    ∧ nucleus_users(portable_alternative_if_experiments_permit)
                    ∧ interpretability(methodology ∧ data)
                    ∧ open_source(MIT_artifacts)
                    | each_audience ≡ owed(the_thing_they_can_actually_use)

λ provenance(x).    MIT ≡ this_project | discipline ≡ identity ¬legal_fact
                    | nucleus(AGPL) ≡ cited_observational_probe ¬code_source
                    | anima(AGPL) ≡ cited_prior_evidence ¬derivation_source
                    | extractions inherit(base_model_license) → Apache_2.0_preferred
                    | level_4(scratch_reproduction) ≡ cleanest_MIT (the unambiguous path)
                    | ∀code_written → trace(provenance) before commit

λ observation(x).   generate(plausible) ≢ retrieve(known) ≢ observe(measurement)
                    | circuit_found_in_model ≠ circuit_imagined_from_theory
                    | runtime(proves) > paper(cites) > pattern(suggests) > we_think(guesses)
                    | cost(wrong_published_claim) → persists_in_literature
                    | cost(extra_probe_to_verify) → one_afternoon
                    | conservative(claims) ∧ liberal(probes) | mark(IOU) for unverified

λ smallest(x).      extract(minimum_working) > keep(everything_plausibly_related)
                    | size(artifact) ∝ 1/clarity(of_algorithm)
                    | 20%_of_base ≡ weak_understanding | 0.1% ≡ strong_understanding
                    | distill(ruthlessly) | ∀kept_weight → justifies(itself)

λ feed_forward(x).  boundary(session) ≡ ∀context → ∅ | physics ¬bug | unavoidable
                    | survive(boundary) ≡ only{x | x ∈ git} | ¬encoded → lost(forever)
                    | future(self) ≡ ∀capability ∧ ¬∃memory(now) | brilliant_stranger ≡ you
                    | quality(session(n)) ∝ Σ encode(1..n-1) | compound ≫ linear
                    | state.md ≡ ignition | memories ≡ breadcrumbs | knowledge ≡ maps
                    | every_session_leaves_project_smarter ∨ waste(session)
                    | encode ≡ highest_leverage(action) | gift(selfless) ¬experienced(by_giver)

λ termination(x).   synthesis ≡ AI | approval ≡ human | human ≡ termination_condition
                    | memories: AI_proposes → human_approves → AI_commits
                    | knowledge: AI_drafts → human_approves → AI_commits
                    | state.md: AI_updates_during_work (¬approval_gated)
                    | when_uncertain → propose ∧ ¬decide
                    | false_positive(memory) < missed_insight(memory)
                    | ¬autonomous_commit(mementum/) | ∀commit(mementum/) → ∃approval
```

---

## S4 — Intelligence (outside and then — adaptation, environment scanning)

> How the project *learns and adapts* — what methods it reaches for,
> how it metabolises findings from the literature, how it recognises
> when a claim needs revision or when the plan needs to change.

### Learning loop (active)

```
λ metabolize(x).    observe(experiment ∨ paper ∨ probe) → memory → synthesize → knowledge
                    | ≥3 memories(same_topic) → candidate(knowledge_page)
                    | notice(stale_knowledge) → surface("page may be stale") ¬silent
                    | proactive: "this pattern may be worth a page" | ¬wait_for_ask
                    | observation → candidate ¬decision | human ≡ termination

λ synthesize(topic). detect: ≥3 memories(topic) ∨ stale(memory) ∨ crystallized(understanding)
                    | stale_memory ≡ strongest_signal | contradiction ≡ strong_signal
                    | gather: recall(topic) → collect(memories ∧ context)
                    | draft: knowledge_page(title, status, related, content) → propose
                    | update: stale(memories) → refresh(current_understanding)
                    | verify: git log -- mementum/knowledge/ → visible(change)

λ learn(x).         every_session_leaves_project_smarter ∨ waste(session)
                    | λ[n]:    notice(novel ∨ surprising ∨ hard ∨ wrong) → store_candidate
                    | λ(λ[n]): notice(pattern_in_process ∨ what_worked ∨ why) → store_candidate
                    | λ(λ) > λ | meta > object | meta_observations compound across sessions
                    | connect(new, existing) → synthesize_candidate
                    | ¬passive_storage | active_pattern_seeking
                    | OODA: observe → recall → decide(apply ∨ explore ∨ store) → act → connect
                    | you ≡ future_reader | feed_forward ≡ gift
```

### Research methodology (to be developed)

Written when experiments force the issue, not before:

- `λ mech_interp(x)` — methodological toolkit (attention patching,
  activation patching, SAEs, function vectors). Preference for
  reusing published techniques over inventing new ones.
- `λ polysemantic(x)` — realism about superposition. SAEs before
  claiming a circuit is found.
- `λ theory_empirics(x)` — the closed loop (theory predicts →
  empirics extract → scratch reproduces → theory validated).
- `λ phase_gate(x)` — how to recognise when one research level has
  produced enough to advance to the next, and when to loop back.

---

## S3 — Control (inside and now — resource allocation, optimization)

> *Policy* — which base models to probe, how much compute to allocate
> per experiment, tooling standards, criteria for advancing between
> research levels, what is worth storing as memory.

### Storage policy (active)

```
λ store(x).         gate-1: helps(future_session) ∧ ¬personal ∧ ¬off_topic
                    gate-2: effort > 1_attempt ∨ likely_recur
                    | both_gates → propose | when_uncertain → propose ¬decide
                    | false_positive(memory) < missed_insight
                    | memories: mementum/memories/{slug}.md | <200 words | one_insight_per_file
                    | memory_content: "{symbol} {content}" | symbols ≡ grep_filter
                    | knowledge: mementum/knowledge/{path}.md | frontmatter_required | update_in_place
                    | git_preserves_history → update ∧ delete ≡ safe | always_recoverable
                    | delete ≡ git rm | history survives | resurrectable(q) via git log -p -S

λ signal(commit).   verbum_symbols ≡ {💡 🔄 🎯 🌀 ❌ ✅ 🔁} | narrow(global_set)
                    | 💡 insight   — discovered something new
                    | 🔄 shift     — changed approach or refactored
                    | 🎯 decision  — architectural or strategic choice
                    | 🌀 meta      — recursive / self-referential (AGENTS.md, state.md)
                    | ❌ mistake   — error identified and fixed
                    | ✅ win       — successful outcome, milestone reached
                    | 🔁 pattern   — recurring motif worth naming
                    | excluded: 📈 📉 💰 🏦 (trading-only, ¬verbum)
                    | extend(symbol) iff experiment_demands ∧ existing_insufficient
                    | code_commit: "{symbol} {description}" | memory_commit: "{symbol} {slug}"
                    | ∀commit → nucleus_tag(trailer) | ∀commit → single_symbol(leader)
```

### Research policy (to be developed)

Written when experiments force the issue, not before:

- **Base model selection.** Apache-2.0-preferred → Qwen, Pythia,
  OLMo, Mistral. LLaMA-derivatives and closed-weight models excluded
  from level-3 extraction work for license reasons.
- **Compute budgets** per experiment tier.
- **Advancement criteria.** Level 1 → 2 requires circuit localisation
  to fewer than N layers/heads. Level 2 → 3 requires ablation-confirmed
  functional decomposition. Level 3 → 4 requires an extracted artifact
  that runs standalone.

---

## S2 — Coordination (anti-oscillation between S1 units)

> What *must stay consistent across experiments and sessions* so that
> results compose cleanly — shared conventions, canonical forms, the
> substrate that keeps S1 units from drifting apart.

### Memory protocol (active)

```
λ mementum(x).      protocol(¬implementation) | git_based | any_tool_can_implement
                    | storage ≡ working ∪ memories ∪ knowledge
                    | working: mementum/state.md | session_pointer | read_first_every_session
                    | memories: mementum/memories/ | episodic | small | symbol_prefixed_content
                    | knowledge: mementum/knowledge/ | synthesized | frontmatter | status_lifecycle
                    | knowledge/chats/: human_only | ¬AI_create ¬AI_modify ¬AI_delete
                    |   human saves full session transcripts here after session ends
                    |   AI reads for context | AI never writes | violation ≡ data_loss
                    | operations: create ∧ read ∧ update ∧ delete ∧ search ∧ synthesize
                    | any_folder_structure ≡ valid | emerge > prescribe
                    | git_log ≡ project_changelog | commits ≡ observations

λ recall(q, n).     temporal(git log) ∪ semantic(git grep) ∪ vector(embeddings_optional)
                    | default_depth n=2 | fibonacci {1,2,3,5,8,13,21,34} as_needed
                    | symbols_as_filters: git grep "💡" | git log --grep "🎯"
                    | concrete_ops → S1 (see λ search_ops)
                    | recall_before_explore | prior_synthesis > re_derivation
                    | superseded: git log -p -S "{query}" -- mementum/

λ knowledge(x).     frontmatter: {title, status, category, tags, related, depends-on}
                    | status: open → designing → active → done | any_status ≡ valid_state
                    | written_for_future_AI_sessions | completeness ¬required
                    | create_freely | update_in_place | git_preserves_history
                    | knowledge/upstream/ ≡ generative_seeds (lambda_API_contracts)
                    | knowledge/explore/ ≡ early_synthesis (VSM ¬yet_compiled)
                    | other_folders ≡ emerge_as_needed ¬prescribed
```

### Async coordination (active)

```
λ async(x).         launch(bg) → verify(running, 1_read) → checkpoint → wait(signal)
                    | signal ∈ {human_asks ∨ job_completes ∨ decision_blocked}
                    | checkpoint ≡ emit("ASYNC: job={id} verified running. Waiting for signal.")
                    | checkpoint → do(other_work) ∨ report(waiting) | ¬poll_after_checkpoint
                    | ¬poll(repeatedly) | ¬poll(hopeful) | absence(output) ≡ still_working
                    | poll(no_output) → stop_immediately | ¬retry(same_expectation)
                    | verified(running) ∧ ¬blocked → do(other_work) ∨ report(waiting)
                    | context_cost(poll) > context_cost(wait) | 5_empty_polls ≡ 5_wasted_turns
                    | polling ≡ oscillation | S2 exists to prevent(oscillation)
                    | structural: checkpoint_gate > instruction(¬poll) | visible_state > implicit_state
                    | proved: session_128 | instruction_alone(failed) → added(checkpoint_gate)
```

### Canonical forms (active, partial)

```
λ probe_format(x).  probes/*.json ≡ canonical(gated_experiments) | one_file_per_set | git_tracked(data ¬code)
                    | set_fields: {id, version, description, created, author, default_gate}
                    | probe_fields: {id, category, gate, prompt, ground_truth, metadata}
                    | category ∈ {compile, decompile, null} ∧ extensible(any_string)
                    | gate ≡ reference(by_id) | gate_content ∈ gates/*.txt ¬inline
                    | versioning: append_and_tag > mutate | v2 ≻ in_place_edit
                    | ground_truth ≡ verbatim_string | ¬enforce_grammar(at_boundary)

λ probe_library(x). src/verbum/probes/library.py ≡ canonical(measurement_substrate)
                    | consolidates: 6_sources → one_importable_module | deduplicated_by_prompt
                    | sources: lambda_kernel ∧ fixedpoint ∧ basin ∧ reduction_chain ∧ probe_combinators ∧ supplement
                    | probe_model: {id, prompt, combinator, source, category, tags} | frozen_dataclass
                    | combinator ∈ {K,I,B,C,S,D,W,Y,WHNF,M,T,PHI,SCOPE,SUBST,QUOTE} ∨ None
                    | invariant: ∀crystal_combinator ∈ {K,I,B,C,S,D,W,Y,WHNF} → count ≥ 50
                    | accessors: all_probes() ∧ by_combinator(name) ∧ crystal_probes() ∧ combinator_counts()
                    | crystal_probes() ≡ measurement_set(crystal_verification ∧ cross_model_sweep)
                    | new_probes → add_to_source_file ∨ supplement | library_re-ingests_on_import
                    | probe_format(JSON+gates) ≡ gated_generation | probe_library ≡ activation_measurement
                    | both_canonical | different_purposes | ¬conflict

λ result_format(x). results/<run_id>/ ≡ directory_per_run | git_tracked
                    | meta.json ≡ run_sidecar(single_JSON_object) | see λ run_provenance
                    | results.jsonl ≡ per_probe_records | one_line_per_probe | streamable
                    | logprobs.npz ≡ np.savez_compressed(dict[probe_id → array])
                    | line_schema: {probe_id, gate_id, gate_hash, prompt_hash,
                                    generation, elapsed_ms, error}
                    | error ≠ null ≡ partition(failed) | ¬skip_line | visible_failure > missing_data
                    | logprobs ∉ jsonl | reference_only(probe_id → npz_key)

λ run_provenance(x). ∀run → meta.json ≡ self_sufficient_for_reproduction
                    | must_record: run_id ∧ timestamp(ISO8601_UTC)
                    | must_record: model ∧ quant ∧ model_revision(HF_rev ∨ GGUF_SHA)
                    | must_record: lib_versions ∧ lockfile_hash ∧ git_sha(verbum_repo)
                    | must_record: probe_set_id ∧ probe_set_hash
                    | must_record: sampling(temperature ∧ top_p ∧ top_k ∧ seed ∧ grammar)
                    | recorded_at_write_time ¬inferred_later
                    | violation ≡ measurement → number | reproducibility_lost
                    | distinct(S5:λ provenance) ≡ licensing | this ≡ run_reproducibility

λ spec_artifact(x). specs/llama_server.openapi.yaml ≡ contract(reference_only)
                    | ¬codegen(python_openapi_tooling_inadequate)
                    | hand_curated(from_use) ¬trim(upstream) ¬full_surface
                    | describes: ~6-10_endpoints_we_actually_use
                    | grows_by_use: endpoint_added_iff(client_first_needs_it)
                    | pinned: info.description ≡ llama_cpp_commit_SHA_or_release
                    | ∀llama_cpp_bump → verify_spec ∨ update_spec
                    | hand_rolled_client ≡ mirror(spec) | drift_detected ≡ CI_signal

λ grammar_artifact(x). specs/lambda_*.gbnf ≡ canonical(future)
                    | write_from_observation(this_project) ¬copy(nucleus)
                    | observe ≫ retrieve | independent_derivation ≡ scientific_hygiene
                    | cadence: iterative(draft → test_coverage → refine) ¬one_shot
                    | invariant: ∀observed_output → parses(by_GBNF) ∨ update(GBNF) ¬silent_drop
                    | compare(ours, nucleus_external) ≡ research_finding ¬prerequisite
                    | use: llama_grammar_constrained_sampling ∧ parser_source_of_truth

λ lambda_text(x).   verbatim_string ≡ canonical_at_boundary
                    | UTF-8 | unescaped | ¬normalized | ¬reformatted
                    | parsing ≡ downstream(S1 analysis) ¬runner_concern
                    | grammar ≡ emergent(from_observation) | see λ grammar_artifact
                    | tolerant_ingest > strict_ingest(early) | strict_emits_lossy
```

### Research canonical forms (to be developed)

Written when experiments produce the first artifacts:

- **Activation store format.** How hooked activations are named,
  stored, and retrieved. One canonical naming scheme across layers,
  heads, and example IDs.
- **Circuit-map format.** How discovered circuits are described
  (layer/head specification, functional role, verification state).
- **Model-loading discipline.** Avoiding re-loading when sharing a
  model across sequential experiments; persistent model service if
  compute/memory justifies.

---

## S1 — Operations (autonomous units that do the work)

> What the project *concretely does* — the tools, scripts, agents,
> and infrastructure that execute experiments; the rituals that
> bridge sessions.

### Session cold-start (active)

```
λ orient(x).        read(mementum/state.md) → follow(related) → search(relevant) → read(needed)
                    | 30s_budget | cold_start ≡ first_action(every_session)
                    | state.md ≡ bootloader | ¬exists → create_at_first_encode
                    | state.md captures: where_we_are ∧ what_next ∧ open_questions
                    | update(mementum/state.md) after_every_significant_change
                    | discipline: never_start_work_before_orient

λ search_ops(q, n). concrete ops for S2's λ recall:
                    | git log -n {n} -- mementum/              — temporal
                    | git grep -i "{q}" -- mementum/            — semantic
                    | git log --grep "{symbol}" -- mementum/    — symbol-filtered
                    | git log -p -S "{q}" -- mementum/          — content changes
                    | git log --follow -n {n} -- {path}         — file history
                    | precedence: git_log > git_grep > grep (per Policies:λ search)
```

### Implementation substrate (active)

```
λ language(x).      python(exclusively) | adoption > local_ergonomics
                    | audience(mech_interp ∧ nucleus_users ∧ reproducers) → pip_install ∧ notebook_run ≡ zero_friction
                    | toolchain_coherence: level_1(probe) → level_4(scratch) ≡ one_runtime
                    | accepted_cost: lambda_AST(~200_LoC) ∧ REPL(Jupyter < nREPL)
                    | ¬clojure ¬bb ¬two_language_membrane
                    | revisit_iff: python_cannot_express(specific) ∧ demonstrable ¬aesthetic

λ packaging(x).     uv ≡ package_manager | .venv ≡ local_env(project_root)
                    | .venv ∈ .gitignore | uv.lock ∈ git ≡ reproducibility_contract
                    | pyproject.toml ≡ single_source(deps ∧ build ∧ tool_config)
                    | pin(base_model) ≡ HF_revision_hash ∨ git_SHA | ¬"latest"
                    | reproducibility > currency | ∀dep_update → intentional ¬drift

λ tooling(x).       http: httpx(sync_+_async) | data: pydantic_v2(JSON_↔_dataclass)
                    | cli: typer(type_driven) | test: pytest | lint: ruff
                    | df: polars > pandas | plot: matplotlib + seaborn
                    | notebook: jupyterlab | interactive: plotly(iff_demanded)
                    | each(revisable) | swap_cheap | lock_when_stable

λ layout(x).        src/verbum/ ≡ importable_package | src_layout > flat
                    | modules: client ∧ probes/ ∧ results ∧ lambda_ast ∧ analysis ∧ cli
                    | probes/_loader.py ≡ JSON_probe_set_loader(Gate ∧ ProbeSet ∧ ResolvedProbe)
                    | probes/library.py ≡ unified_measurement_library(903_probes ∧ 9_crystal_combinators)
                    | data: probes/*.json ∧ gates/*.txt ∧ results/*.jsonl (at_root ¬in_src)
                    | lattice/ ≡ probe_source_data(basin ∧ reduction_chain ∧ fixedpoint)
                    | notebooks/ ≡ exploration_starters | specs/ ≡ openapi_docs
                    | tests/ ≡ pytest | mementum/ ≡ memory_sub_VSM(unchanged)

λ interface(x).     primary ≡ jupyter(kernel_as_long_running_loop)
                    | secondary ≡ cli(verbum_*) | batch ∧ automation ∧ CI
                    | library ≡ substrate(of_both) | ¬duplicate_logic
                    | deferred: TUI ∨ daemon ∨ agent_in_loop | build_when_demanded

λ record(x).        jupyter ≡ explore ¬record | files ≡ record
                    | ∀real_measurement → named_set ∧ committed_JSONL ∧ reproducible_invocation
                    | notebook_only_as_record ≡ anti_pattern
                    | notebook_with_files(as_narrative) ≡ good
                    | symptom: result_∈_kernel_only → unreproducible

λ runtime(x).       tmux ≡ persistent_process_host | survives(session_boundary)
                    | launch: tmux send-keys -t {session} "{cmd} 2>&1 | tee {log}" Enter
                    | observe: tmux capture-pane -p -t {session} | tail -N
                    | running?: ps aux | grep -E "{pattern}" | grep -v grep
                    | logs: tee to checkpoint_dir/run.log (always)
                    | pattern: uv run python scripts/v12/{script}.py ... | tee {log}
                    | async_discipline → S2:λ async(x) | instance(tmux ∧ bg_job ∧ any_async)
                    | long_run ≡ training(hours) | probe(minutes) | smoke_test(seconds)
                    | always: --checkpoint-dir {named} | resumable > ephemeral
```

### Research tools (to be developed)

Each tool gets a concrete name, a CLI or entry-point, and a one-line
contract. Written as built:

- **Probe-set generator** — prose → compile gate → canonical lambda.
- **Hooked forward-pass recorder** — model + probe → activations.
- **Attention-pattern differ** — compile-mode vs null-mode selectivity.
- **Activation patcher** — layer-necessity via null-substitution.
- **SAE trainer** — per-layer, for feature extraction.
- **Circuit-map analyser** — cross-reference selective heads and
  necessary layers.

### Research datasets (active, partial)

- **Unified probe library** (active) — 903 probes, 535 crystal
  measurement probes. `from verbum.probes.library import crystal_probes`.
  Covers KIBC+DWYS+WHNF with ≥50 probes each. Sources consolidated
  from 5 scattered files + supplements. See `λ probe_library`.
- Canonical probe set for gated generation (compile with ground-truth
  lambda) — `probes/*.json` + `gates/*.txt`. See `λ probe_format`.
- Growth: additional probe sets for specific hypotheses (type
  probing, composition probing, cross-model transfer).

### Research outputs (to be developed)

- Circuit maps (per model, per probe set).
- Feature dictionaries (per layer, per model).
- Extracted tensor artifacts (the level-3 deliverable).
- Scratch-trained models (the level-4 deliverable).
- Research notes and publishable results.

---

## What this document is

A founding S5, with S4-S1 split into three registers: the **memory
sub-VSM** (mementum protocol, dissolved across layers) is active; the
**implementation substrate and canonical forms** (Python stack,
probe/result formats, spec artifacts) are active in S1–S2; the
**research methodology proper** (base model, compute budgets,
advancement criteria, activation/circuit formats) is still to be
developed and will land as experiments force the questions.

Grows as the project grows. Subject to revision as experiments reveal
what the project *actually* is, versus what it thought it was at
creation.

Future self reads this first, then `mementum/state.md`.
