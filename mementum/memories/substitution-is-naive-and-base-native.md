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
register, capture = binding/scope register). Single lineage, n_dec 18 — 32B +
OLMo remain. Traced arm null (token_budget_null_passed False): tracing didn't
help. Page: the-benchmark-is-the-re-oracle.md §Result (s332); data
results/subst-engine/qwen3-14b{,-base}/.
