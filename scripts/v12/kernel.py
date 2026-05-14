"""
v12 — KIBCM Kernel: Combinators + Retrieval

The KIBC combinator basis from v11, plus M (match/retrieval) — the
fifth kernel function discovered in session 095's head-level probe.

Key insight: M is NOT a 5th combinator in the dispatch softmax. M is
a different *layer type*. In Qwen3.6-35B-A3B, KIBC lives in full-
attention layers (7 private heads, L15/L19). M lives in GatedDeltaNet
layers (6 private heads, J=0.176 with everything else — maximally
independent). They share no heads, no layers, no mechanism.

V12 reflects this: KIBC stays in the 4-way dispatch (composition
layers). M operates via GatedLinearAttention (retrieval layers).
N_COMBINATORS remains 4. M is defined here for completeness and
for the reduction engine, but the neural pathway for M is in
attention.py (GatedLinearAttention), not kernel_dispatch.py.

Kernel inventory (KIBCM):
  K x y     → x           (select first, discard second)
  I x       → x           (identity, copy forward)
  B f g x   → f (g x)     (compose: apply g then f)
  C f x y   → f y x       (flip: reorder arguments)
  M p ctx   → lookup(p, ctx) (match pattern, retrieve content)

The first four are compositional (pure lambda calculus).
M is associative (pattern-directed retrieval from context).
This is why they need different mechanisms.

License: MIT
"""

from __future__ import annotations

from enum import IntEnum


# ══════════════════════════════════════════════════════════════════════
# § 1  Combinator definitions
# ══════════════════════════════════════════════════════════════════════

class Combinator(IntEnum):
    """The four primitive combinators — the natural basis of attention.

    These are the COMPOSITIONAL kernels dispatched via softmax in
    CombinatorDispatch. M (match/retrieval) is NOT here — it operates
    via GatedLinearAttention as a separate layer type.
    """
    K = 0   # λx.λy.x         — select first, discard second
    I = 1   # λx.x             — identity (copy forward)
    B = 2   # λf.λg.λx.f(g(x)) — compose (chain two functions)
    C = 3   # λf.λx.λy.f(y)(x) — flip (reorder arguments)

N_COMBINATORS = 4  # KIBC only — M is a layer type, not a dispatch option

COMBINATOR_NAMES: list[str] = ["K", "I", "B", "C"]
assert len(COMBINATOR_NAMES) == N_COMBINATORS


class Kernel(IntEnum):
    """All five kernel functions — the complete computational inventory.

    KIBC are compositional (dispatched per-position in descending arm).
    M is associative (operates via retrieval layers in ascending arm).
    """
    K = 0   # λx.λy.x             — select first, discard second
    I = 1   # λx.x                 — identity (copy forward)
    B = 2   # λf.λg.λx.f(g(x))     — compose (chain two functions)
    C = 3   # λf.λx.λy.f(y)(x)     — flip (reorder arguments)
    M = 4   # λp.λctx.lookup(p,ctx) — match pattern, retrieve content

N_KERNELS = 5

KERNEL_NAMES: list[str] = ["K", "I", "B", "C", "M"]
assert len(KERNEL_NAMES) == N_KERNELS


# ══════════════════════════════════════════════════════════════════════
# § 2  Combinator properties
# ══════════════════════════════════════════════════════════════════════

# Arity: how many arguments each combinator consumes before reducing
COMBINATOR_ARITY: dict[Combinator, int] = {
    Combinator.K: 2,   # K x y → x
    Combinator.I: 1,   # I x → x
    Combinator.B: 3,   # B f g x → f (g x)
    Combinator.C: 3,   # C f x y → f y x
}

# What each combinator does in prose (for logging/probing)
COMBINATOR_ROLE: dict[Combinator, str] = {
    Combinator.K: "select",    # pick relevant, discard irrelevant
    Combinator.I: "identity",  # copy forward unchanged
    Combinator.B: "compose",   # chain operations: apply g then f
    Combinator.C: "flip",      # reorder arguments, enable closures
}

# Full kernel inventory (KIBCM) — includes M
KERNEL_ARITY: dict[Kernel, int] = {
    Kernel.K: 2,   # K x y → x
    Kernel.I: 1,   # I x → x
    Kernel.B: 3,   # B f g x → f (g x)
    Kernel.C: 3,   # C f x y → f y x
    Kernel.M: 2,   # M pattern context → content
}

KERNEL_ROLE: dict[Kernel, str] = {
    Kernel.K: "select",     # pick relevant, discard irrelevant
    Kernel.I: "identity",   # copy forward unchanged
    Kernel.B: "compose",    # chain operations: apply g then f
    Kernel.C: "flip",       # reorder arguments, enable closures
    Kernel.M: "match",      # find pattern in context, retrieve content
}


# ══════════════════════════════════════════════════════════════════════
# § 3  Reduction engine
# ══════════════════════════════════════════════════════════════════════

class Term:
    """A combinator calculus term.

    Either a primitive combinator, an integer/symbol atom, or an
    application of one term to another.
    """
    pass


class Comb(Term):
    """A primitive combinator: K, I, B, or C."""
    __slots__ = ('which',)
    def __init__(self, which: Combinator):
        self.which = which
    def __repr__(self):
        return COMBINATOR_NAMES[self.which]
    def __eq__(self, other):
        return isinstance(other, Comb) and self.which == other.which
    def __hash__(self):
        return hash(('Comb', self.which))


class Atom(Term):
    """An atomic value — integer, symbol, or any leaf."""
    __slots__ = ('value',)
    def __init__(self, value):
        self.value = value
    def __repr__(self):
        return str(self.value)
    def __eq__(self, other):
        return isinstance(other, Atom) and self.value == other.value
    def __hash__(self):
        return hash(('Atom', self.value))


class App(Term):
    """Application of one term to another: (f x)."""
    __slots__ = ('func', 'arg')
    def __init__(self, func: Term, arg: Term):
        self.func = func
        self.arg = arg
    def __repr__(self):
        f_str = repr(self.func)
        a_str = repr(self.arg)
        if isinstance(self.arg, App):
            a_str = f"({a_str})"
        return f"{f_str} {a_str}"
    def __eq__(self, other):
        return isinstance(other, App) and self.func == other.func and self.arg == other.arg
    def __hash__(self):
        return hash(('App', self.func, self.arg))


def reduce_step(term: Term) -> tuple[Term, bool]:
    """One step of normal-order (outermost-first) reduction.

    Returns (reduced_term, changed).
    Normal order matches what autoregressive transformers naturally do:
    outermost redex first, left to right.
    """
    if isinstance(term, (Comb, Atom)):
        return term, False

    if not isinstance(term, App):
        return term, False

    # Try to reduce at the top level first (normal order)
    # K x y → x
    if (isinstance(term.func, App) and
        isinstance(term.func.func, Comb) and
        term.func.func.which == Combinator.K):
        # (K x) y → x
        return term.func.arg, True

    # I x → x
    if isinstance(term.func, Comb) and term.func.which == Combinator.I:
        return term.arg, True

    # B f g x → f (g x)
    if (isinstance(term.func, App) and
        isinstance(term.func.func, App) and
        isinstance(term.func.func.func, Comb) and
        term.func.func.func.which == Combinator.B):
        f = term.func.func.arg
        g = term.func.arg
        x = term.arg
        return App(f, App(g, x)), True

    # C f x y → f y x
    if (isinstance(term.func, App) and
        isinstance(term.func.func, App) and
        isinstance(term.func.func.func, Comb) and
        term.func.func.func.which == Combinator.C):
        f = term.func.func.arg
        x = term.func.arg
        y = term.arg
        return App(App(f, y), x), True

    # No top-level reduction — try reducing the function part first
    new_func, changed = reduce_step(term.func)
    if changed:
        return App(new_func, term.arg), True

    # Then try reducing the argument
    new_arg, changed = reduce_step(term.arg)
    if changed:
        return App(term.func, new_arg), True

    return term, False


def reduce(term: Term, max_steps: int = 100) -> tuple[Term, int]:
    """Fully reduce a term (normal order). Returns (result, steps_taken).

    Stops after max_steps to prevent infinite loops (e.g. Ω combinator).
    """
    steps = 0
    while steps < max_steps:
        new_term, changed = reduce_step(term)
        if not changed:
            break
        term = new_term
        steps += 1
    return term, steps


# ══════════════════════════════════════════════════════════════════════
# § 4  Convenience constructors
# ══════════════════════════════════════════════════════════════════════

K = Comb(Combinator.K)
I = Comb(Combinator.I)
B = Comb(Combinator.B)
C = Comb(Combinator.C)

# M as a term (for the symbolic reduction engine)
# In the neural pathway, M is a layer type, not a combinator.
# But the reduction engine can express M-terms symbolically.


class MComb(Term):
    """M (match/retrieval) — NOT a standard combinator.

    In the reduction engine, M p ctx reduces by looking up p in ctx.
    This is a placeholder for symbolic completeness — the real M
    computation happens via GatedLinearAttention in the neural pathway.
    """
    __slots__ = ()
    def __repr__(self):
        return "M"
    def __eq__(self, other):
        return isinstance(other, MComb)
    def __hash__(self):
        return hash('MComb')


M = MComb()


def app(*terms: Term) -> Term:
    """Left-associative application: app(f, x, y) = App(App(f, x), y)."""
    result = terms[0]
    for t in terms[1:]:
        result = App(result, t)
    return result


def atom(value) -> Atom:
    """Create an atomic term."""
    return Atom(value)


# ══════════════════════════════════════════════════════════════════════
# § 5  Kernel functions for neural pathway
# ══════════════════════════════════════════════════════════════════════
#
# These functions implement combinator reductions on integer operands,
# matching the kernel computation pathway in CombinatorIntegrate.
# The neural pathway extracts operands from the residual stream,
# dispatches to one of these functions, and encodes the result back.
#
# Unlike v10's 22-op kernel (arithmetic), these are structural:
#   K: select operand 0, discard operand 1
#   I: return operand 0 unchanged
#   B: f(g(x)) — requires encoding f and g as operations
#   C: swap operand 1 and 2, then apply f

def kernel_K(op0: int, op1: int, op2: int) -> int:
    """K x y → x. Select first operand."""
    return op0


def kernel_I(op0: int, op1: int, op2: int) -> int:
    """I x → x. Identity — return first operand unchanged."""
    return op0


def kernel_B(op0: int, op1: int, op2: int) -> int:
    """B f g x → f(g(x)). Compose: apply g to x, then f to result.

    In the neural kernel pathway, f and g are encoded as operand
    indices. The actual composition happens through multiple cycles
    in the descending arm — cycle 0 identifies the combinators,
    cycle 1 resolves g(x), cycle 2 applies f. The kernel provides
    a single-step approximation: f_index + g(x_index).

    For the straight-through pathway, we encode this as:
    result = op0 + op1 + op2 (additive composition signal).
    The result_embed learns to map this back meaningfully.
    """
    return op0 + op1 + op2


def kernel_C(op0: int, op1: int, op2: int) -> int:
    """C f x y → f y x. Flip: swap operand 1 and 2.

    In the kernel pathway, flipping is encoded as using op2 where
    op1 would go and vice versa: result = op0 + op2 (skip op1).
    The model learns through the result_embed that C-reduction
    discards the second argument's position and uses the third.
    """
    return op0 + op2


def kernel_M(op0: int, op1: int, op2: int) -> int:
    """M pattern context → content. Match and retrieve.

    In the neural pathway, M operates via GatedLinearAttention —
    this integer kernel is for the symbolic reduction engine only.

    M's retrieval is: given a pattern (op0), find match in context
    and return content-after-match. In the symbolic engine, this
    is approximated as: result = op1 (the context value), because
    the actual retrieval happens through attention, not arithmetic.

    NOTE: The neural M pathway does NOT use this function. This
    exists for completeness of the KIBCM reduction engine.
    """
    return op1


# Dispatch table for KIBC vectorized kernel computation
# (M is NOT in this table — it operates via GatedLinearAttention)
COMBINATOR_KERNEL_FUNCTIONS = [kernel_K, kernel_I, kernel_B, kernel_C]
assert len(COMBINATOR_KERNEL_FUNCTIONS) == N_COMBINATORS

# Full KIBCM table (for symbolic reduction engine)
ALL_KERNEL_FUNCTIONS = [kernel_K, kernel_I, kernel_B, kernel_C, kernel_M]
assert len(ALL_KERNEL_FUNCTIONS) == N_KERNELS


# ══════════════════════════════════════════════════════════════════════
# § 6  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Smoke-test all four combinators and the reduction engine."""

    # ── K combinator: K x y → x ──
    t = app(K, atom(3), atom(7))
    result, steps = reduce(t)
    assert result == atom(3), f"K 3 7 should reduce to 3, got {result}"
    assert steps == 1, f"K x y should take 1 step, took {steps}"

    # ── I combinator: I x → x ──
    t = app(I, atom(42))
    result, steps = reduce(t)
    assert result == atom(42), f"I 42 should reduce to 42, got {result}"
    assert steps == 1

    # ── B combinator: B f g x → f (g x) ──
    # B K I 5 → K (I 5) → K 5 → partial (K 5, waiting for y)
    # But more usefully: B I I x → I (I x) → I x → x
    t = app(B, I, I, atom(5))
    result, steps = reduce(t)
    assert result == atom(5), f"B I I 5 should reduce to 5, got {result}"

    # B (K 1) I 5 → (K 1) (I 5) → (K 1) 5 → 1
    t = app(B, app(K, atom(1)), I, atom(5))
    result, steps = reduce(t)
    assert result == atom(1), f"B (K 1) I 5 should reduce to 1, got {result}"

    # ── C combinator: C f x y → f y x ──
    # C K 3 7 → K 7 3 → 7
    t = app(C, K, atom(3), atom(7))
    result, steps = reduce(t)
    assert result == atom(7), f"C K 3 7 should reduce to 7, got {result}"

    # ── Composition: C and K together ──
    # C (C K) 1 2 → (C K) 2 1 → K 1 2 → 1
    t = app(C, app(C, K), atom(1), atom(2))
    result, steps = reduce(t)
    assert result == atom(1), f"C (C K) 1 2 should reduce to 1, got {result}"

    # ── S combinator expressed as composition ──
    # S = B(B(BW)(BBC))(BB) where W = CSI
    # Simpler test: S K K x → K x (K x) → x
    # SKK is the identity — but we don't have S, we compose from KIBC:
    # S f g x = f x (g x)
    # For S K K x: K x (K x) → x
    # We can express this using B, C, K:
    # Not testing S directly since it's emergent, not primitive.

    # ── Partial application (combinator waiting for args) ──
    t = app(K, atom(3))  # K 3 — waiting for y
    result, steps = reduce(t)
    assert isinstance(result, App), f"K 3 should be partial, got {result}"
    assert steps == 0, f"K 3 is a value (no redex), steps should be 0"

    # ── Normal-order reduction (outermost first) ──
    # K (I 3) (I 4) → I 3 (not I 4 first — normal order selects and discards)
    # Actually: (K (I 3)) (I 4) → (I 3) → 3
    t = app(K, app(I, atom(3)), app(I, atom(4)))
    result, steps = reduce(t)
    assert result == atom(3), f"K (I 3) (I 4) should reduce to 3, got {result}"
    # Normal order: K reduces first (discarding I 4), then I 3 → 3
    # Steps: K (I 3) (I 4) → I 3 → 3 = 2 steps
    assert steps == 2, f"Expected 2 steps (K then I), got {steps}"

    # ── Kernel functions ──
    assert kernel_K(3, 7, 0) == 3, "kernel_K should select op0"
    assert kernel_I(42, 0, 0) == 42, "kernel_I should return op0"
    assert kernel_B(1, 2, 3) == 6, "kernel_B should sum all three"
    assert kernel_C(1, 2, 3) == 4, "kernel_C should sum op0 + op2"
    assert kernel_M(3, 7, 0) == 7, "kernel_M should return op1 (context)"

    # ── COMBINATOR_NAMES consistency ──
    assert COMBINATOR_NAMES[Combinator.K] == "K"
    assert COMBINATOR_NAMES[Combinator.I] == "I"
    assert COMBINATOR_NAMES[Combinator.B] == "B"
    assert COMBINATOR_NAMES[Combinator.C] == "C"

    # ── KERNEL_NAMES consistency ──
    assert KERNEL_NAMES[Kernel.K] == "K"
    assert KERNEL_NAMES[Kernel.M] == "M"
    assert N_COMBINATORS == 4, "KIBC dispatch must remain 4-way"
    assert N_KERNELS == 5, "Full kernel inventory is KIBCM"

    # ── M term ──
    assert repr(M) == "M"
    assert M == MComb()

    # ── Dispatch tables ──
    assert len(COMBINATOR_KERNEL_FUNCTIONS) == N_COMBINATORS
    assert len(ALL_KERNEL_FUNCTIONS) == N_KERNELS

    print("kernel.py self-test: all assertions passed ✓")
    print(f"  {N_COMBINATORS} combinators (dispatch): {', '.join(COMBINATOR_NAMES)}")
    print(f"  {N_KERNELS} kernels (total): {', '.join(KERNEL_NAMES)}")
    print(f"  Reduction engine: normal-order, outermost-first")
    print(f"  Composition: K(select), I(identity), B(compose), C(flip)")
    print(f"  Retrieval:   M(match) — layer type, not dispatch option")


if __name__ == "__main__":
    _self_test()
