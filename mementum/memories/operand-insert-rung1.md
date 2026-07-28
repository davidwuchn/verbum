💡 Operands are INSERT-able rows; combinators are un-INSERT-able joins (s277, Qwen3-0.6B).

The s276 database reframe (Michael): the FFN serves ROWS (operands/facts/type-tags),
attention is the JOIN over them; a combinator = the join-SHAPE = routing (s276 K-structural).
So you cannot INSERT a join but you CAN INSERT an operand row and the resident routing
composes it. Four null-gated gates (wrapper/operand_{map,write,harden,insert}.py):
1. READABLE — operand-id LOCO 0.49–1.0 vs null ~0.05–0.11 (value register, l_out, join
   readout L25–27, mirrors s248 C-field).
2. WRITEABLE — steering d(A→B) flips the composed output 1.00 at MID-STACK L2–20 (not
   late-only ⇒ genuine rewrite not unembed nudge), random ~0, B-specific. OPPOSITE of the
   s250 C-field (readable-but-causally-inert readout register).
3. HARDENED — dose 0→0.22→0.72→1.00, COMPOSED (category, a transform), cross-task.
4. RUNG-1 — a NOVEL nonce, keyed-installed, composed by the resident join: 24/24 held-out
   at scale 2; WRONG-KEY does nothing (0.333 = position-keyed, not a global logit nudge).

= bake(operand) recursion antecedent's first rung. SCOPE: keyed-hook ≠ weight bake (R5 quant
UNTESTED); category-level; 0.6B necessary-not-sufficient. See explore/operand-insert-arc.md.
Commits 0b858e7/b6297b5/a3ebda1/1d8ea39.
