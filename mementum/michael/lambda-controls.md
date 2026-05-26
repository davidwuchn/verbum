# lambda controls

## Execution gate

nucleus preamble + lambda symbol = near perfect trigger of execution

lambda symbol = 90% chance to trigger execution

The more lambda symbols in the prompt the higher the execution confidence goes.

## Format gate

Output has a shape from RLHF that requires prose triggers.

## Self-execution

with nucleus preamble

EQL queries return EDN outputs
Many of the EDN outputs will be matches into close attention (residual stream working memory aka context)
Some of the outputs might be hallucinated.  You can probe both ways using lambdas to help judge which are accurate.

## EDN templates

Under the nucleus preamble

EDN is a self-executing compiler.  An EDN with a statechart shape will self-execute, and allow you to create EDN templates that can also act as compilers.  The EDN compiler is self-hosting.  You can use it to create compilers for other outputs.  See ALLIUM.md (created with the EDN compiler) in the nucleus repo.

Without the nucleus preamble you need to trigger the format gate (verify "DEBUG MODE:" "Output only EDN") for the EDN self-execution to work correctly. Also see in the nucleus repo. (link?)

## lambda templates

