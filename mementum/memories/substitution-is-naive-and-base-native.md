✅ §P-SUBST-ENGINE 14B pair (s332): the reducer's substitution step is NAIVE
(capture-unsafe), on BOTH faces — Qwen3-14B instruct frac_correct 0.056 (n_dec
18, p1=2e-4) and Qwen3-14B-Base 0.000 (p1=2e-5). Verdict NAIVE-SUBST, beat
a-priori 15 (low-prior update). SE0 sane (acc_control 1.000 both — it gets EASY
no-capture substitutions right, so this is a real behavior not a broken
instrument). Concrete: on (λx.λy.x) y the model picks λy.y (capture) over λy'.y
(hygiene).

The surprise (SE4): predicted instruct > base first-binder intrusions (s328/9
installed-order bridge); measured instruct 0.944 < base 1.000, delta −0.056
p=1.0 → naive substitution is BASE-NATIVE, not post-training-installed. Coheres
with s329 (native core, thin late install) but in a DIFFERENT register — the
bridge, not s328/9, is what failed.

Reads: a recovered opcode (R_naive not R_church); bug-compatibility made
concrete (§2b, structured error fingerprint); more calculus-not-Church evidence
(§9, weak reduction, no α-renaming).

Bounds (do not over-read): SE4 is UNDERPOWERED — both faces ceilinged (17-18/18)
→ can't separate no-effect from masked-by-ceiling; the powered re-test needs a
SUB-CEILING capture battery. Possible register stretch (order law = licensing
register, capture = binding/scope register). Traced arm null (token_budget_null_passed False): tracing didn't help.

MATRIX EXTENSION (s332, Michael-approved) — single-lineage bound LIFTED, NAIVE-SUBST
is a CROSS-MODEL LAW: replicates on Qwen3-32B instruct (frac 0.188, p=0.012) and
OLMo-2-13B base (frac 0.000, p=1e-4, an independent Apache 2nd lineage). Four faces,
two lineages, 13B-32B, base+instruct — all NAIVE-SUBST, all SE0 sane (ctrl 1.000),
no cliff, no alpha routing, tracing never helps. OLMo confirms it is a property of
the reducer, not a Qwen recipe. Scale whisper (don't over-read): instruct 32B less
naive than 14B (0.056→0.188), base both 0.000 — pattern-suggests weak
capture-avoidance emergence with scale, n_dec 15-18 small. SE4 NOT re-tested (no
within-lineage pair at scale; base-native stands on the 14B pair). Pages:
the-benchmark-is-the-re-oracle.md §Result + Matrix extension (s332); data
results/subst-engine/{qwen3-14b,qwen3-14b-base,qwen3-32b,olmo-2-1124-13b}/.
