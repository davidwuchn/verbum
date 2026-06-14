❌ The s224 2-contributor fold's CAPABILITY (CE) test was confounded: both shards
were the SAME probe-prompt corpus split in half → A and B learned nearly the same
thing → B had NO distinct knowledge to transfer → dCE structurally CANNOT go negative
regardless of architecture (averaging two solutions to one problem = interpolation
barrier, not failed transfer). Lesson: any "do contributors compose / does folding B
help" test REQUIRES heterogeneous shards (split by combinator family or different
corpora). The GEOMETRY result (REL fold retains function GC +0.84 vs CTRL null) was
NOT confounded — geometry agreement doesn't depend on data distinctness. Also: the
fold was too gentle (~27% neurons, θ=0.5) → contractivity gate never stressed → didn't
discriminate; need higher-coverage fold to test the acceptance gate. tool:
two_contributor_fold.py.
