"""
v12 — Extended Kernel: 8 Combinators + Retrieval

Expanded from KIBC (4) to KIBC-DYWH (8) dispatched combinators, plus
M (match/retrieval) as a layer type. The 4 new operations are fused
combinators that save passes:

  D = B∘B   (deep compose, fuses 3×B into one pass)
  Y         (recursion/fixed-point — enables loops)
  W = λf.f(f) (self-apply/duplicate — enables sharing)
  WHNF      (terminal detection — stop-reducing signal)

N_COMBINATORS = 8 is the dispatch softmax width.
M remains a layer type (GatedLinearAttention), not a dispatch option.

Architecture session history:
  - Sessions 093-104: KIBC discovered as universal basis (4-way)
  - Session 106: 14 operations explored, D/Y/W/WHNF identified as Tier 2
  - Session 109: Lambda generator expanded to 8 ops, design doc written
  - Session 110: Architecture expanded (this file)

License: MIT
"""

from __future__ import annotations

from enum import IntEnum


# ══════════════════════════════════════════════════════════════════════
# § 1  Combinator definitions
# ══════════════════════════════════════════════════════════════════════

class Combinator(IntEnum):
    """Eight dispatch combinators — the extended compositional kernel.

    KIBC (positions 0-3) are the irreducible basis.
    DYWH (positions 4-7) are fused/structural operations that
    save passes by collapsing multi-step reductions.

    M (match/retrieval) is NOT here — it operates via
    GatedLinearAttention as a separate layer type.
    """
    K = 0    # λx.λy.x             — select first, discard second
    I = 1    # λx.x                 — identity (copy forward)
    B = 2    # λf.λg.λx.f(g(x))     — compose (chain two functions)
    C = 3    # λf.λx.λy.f(y)(x)     — flip (reorder arguments)
    D = 4    # λf.λg.λh.λx.f(g(h(x))) — deep compose (fuses 3×B)
    Y = 5    # λf.f(Y(f))           — recursion / fixed-point
    W = 6    # λf.λx.f(x)(x)       — duplicate / self-apply
    WHNF = 7 # (terminal)           — weak head normal form (stop reducing)

N_COMBINATORS = 8  # KIBC-DYWH dispatch (positive crystal)

COMBINATOR_NAMES: list[str] = ["K", "I", "B", "C", "D", "Y", "W", "WHNF"]
assert len(COMBINATOR_NAMES) == N_COMBINATORS

# Anti-crystal: the shadow of each combinator. Session 132 finding:
# the teacher encodes WHAT TO DO (positive crystal) and WHAT NOT TO DO
# (anti-crystal) as interlocking sign lattices. 29% of positions in
# each weight matrix are anti-crystal (Q and K signs disagree).
# The anti-crystal is symmetric, high-rank, and positional.
# Anti-combinator embeddings give the suppression pattern geometric
# structure via 16×16 relational loss targets.
N_ANTI_COMBINATORS = 8  # āK, āI, āB, āC, āD, āY, āW, āWHNF
N_TOTAL_COMBINATORS = N_COMBINATORS + N_ANTI_COMBINATORS  # 16

ANTI_COMBINATOR_NAMES: list[str] = ["āK", "āI", "āB", "āC", "āD", "āY", "āW", "āWHNF"]
assert len(ANTI_COMBINATOR_NAMES) == N_ANTI_COMBINATORS

ALL_COMBINATOR_NAMES: list[str] = COMBINATOR_NAMES + ANTI_COMBINATOR_NAMES
assert len(ALL_COMBINATOR_NAMES) == N_TOTAL_COMBINATORS


class Kernel(IntEnum):
    """All nine kernel functions — complete computational inventory.

    KIBC-DYWH (8) are compositional (dispatched per-position).
    M is associative (operates via retrieval layers).
    """
    K = 0    # λx.λy.x             — select first, discard second
    I = 1    # λx.x                 — identity (copy forward)
    B = 2    # λf.λg.λx.f(g(x))     — compose (chain two functions)
    C = 3    # λf.λx.λy.f(y)(x)     — flip (reorder arguments)
    D = 4    # λf.λg.λh.λx.f(g(h(x))) — deep compose
    Y = 5    # λf.f(Y(f))           — recursion / fixed-point
    W = 6    # λf.λx.f(x)(x)       — duplicate / self-apply
    WHNF = 7 # (terminal)           — stop reducing
    M = 8    # λp.λctx.lookup(p,ctx) — match pattern, retrieve content

N_KERNELS = 9

KERNEL_NAMES: list[str] = ["K", "I", "B", "C", "D", "Y", "W", "WHNF", "M"]
assert len(KERNEL_NAMES) == N_KERNELS


# ══════════════════════════════════════════════════════════════════════
# § 2  Combinator properties
# ══════════════════════════════════════════════════════════════════════

# Arity: how many arguments each combinator consumes before reducing
COMBINATOR_ARITY: dict[Combinator, int] = {
    Combinator.K: 2,      # K x y → x
    Combinator.I: 1,      # I x → x
    Combinator.B: 3,      # B f g x → f (g x)
    Combinator.C: 3,      # C f x y → f y x
    Combinator.D: 4,      # D f g h x → f (g (h x))
    Combinator.Y: 1,      # Y f → f (Y f)
    Combinator.W: 2,      # W f x → f x x
    Combinator.WHNF: 0,   # WHNF → WHNF (terminal, no reduction)
}

# What each combinator does in prose (for logging/probing)
COMBINATOR_ROLE: dict[Combinator, str] = {
    Combinator.K: "select",       # pick relevant, discard irrelevant
    Combinator.I: "identity",     # copy forward unchanged
    Combinator.B: "compose",      # chain operations: apply g then f
    Combinator.C: "flip",         # reorder arguments, enable closures
    Combinator.D: "deep_compose", # chain 3 operations in one step
    Combinator.Y: "recurse",      # enable loops and self-reference
    Combinator.W: "duplicate",    # share/copy argument for reuse
    Combinator.WHNF: "terminal",  # signal: expression is fully reduced
}

# Full kernel inventory (KIBC-DYWH + M) — includes M
KERNEL_ARITY: dict[Kernel, int] = {
    Kernel.K: 2,
    Kernel.I: 1,
    Kernel.B: 3,
    Kernel.C: 3,
    Kernel.D: 4,
    Kernel.Y: 1,
    Kernel.W: 2,
    Kernel.WHNF: 0,
    Kernel.M: 2,
}

KERNEL_ROLE: dict[Kernel, str] = {
    Kernel.K: "select",
    Kernel.I: "identity",
    Kernel.B: "compose",
    Kernel.C: "flip",
    Kernel.D: "deep_compose",
    Kernel.Y: "recurse",
    Kernel.W: "duplicate",
    Kernel.WHNF: "terminal",
    Kernel.M: "match",
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
    """A primitive combinator: K, I, B, C, D, Y, W, or WHNF."""
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

    # ── K x y → x ────────────────────────────────────────────
    if (isinstance(term.func, App) and
        isinstance(term.func.func, Comb) and
        term.func.func.which == Combinator.K):
        return term.func.arg, True

    # ── I x → x ──────────────────────────────────────────────
    if isinstance(term.func, Comb) and term.func.which == Combinator.I:
        return term.arg, True

    # ── B f g x → f (g x) ────────────────────────────────────
    if (isinstance(term.func, App) and
        isinstance(term.func.func, App) and
        isinstance(term.func.func.func, Comb) and
        term.func.func.func.which == Combinator.B):
        f = term.func.func.arg
        g = term.func.arg
        x = term.arg
        return App(f, App(g, x)), True

    # ── C f x y → f y x ──────────────────────────────────────
    if (isinstance(term.func, App) and
        isinstance(term.func.func, App) and
        isinstance(term.func.func.func, Comb) and
        term.func.func.func.which == Combinator.C):
        f = term.func.func.arg
        x = term.func.arg
        y = term.arg
        return App(App(f, y), x), True

    # ── D f g h x → f (g (h x)) ─────────────────────────────
    # D is a 4-arity combinator: ((((D f) g) h) x) → f (g (h x))
    if (isinstance(term.func, App) and
        isinstance(term.func.func, App) and
        isinstance(term.func.func.func, App) and
        isinstance(term.func.func.func.func, Comb) and
        term.func.func.func.func.which == Combinator.D):
        f = term.func.func.func.arg
        g = term.func.func.arg
        h = term.func.arg
        x = term.arg
        return App(f, App(g, App(h, x))), True

    # ── Y f → f (Y f) ────────────────────────────────────────
    if isinstance(term.func, Comb) and term.func.which == Combinator.Y:
        f = term.arg
        return App(f, App(Comb(Combinator.Y), f)), True

    # ── W f x → f x x ────────────────────────────────────────
    if (isinstance(term.func, App) and
        isinstance(term.func.func, Comb) and
        term.func.func.which == Combinator.W):
        f = term.func.arg
        x = term.arg
        return App(App(f, x), x), True

    # ── WHNF — terminal, no reduction ────────────────────────
    if isinstance(term.func, Comb) and term.func.which == Combinator.WHNF:
        # WHNF applied to anything just returns itself applied (it's a tag)
        return term, False

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

    Stops after max_steps to prevent infinite loops (e.g. Y combinator).
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
D = Comb(Combinator.D)
Y = Comb(Combinator.Y)
W = Comb(Combinator.W)
WHNF = Comb(Combinator.WHNF)


class MComb(Term):
    """M (match/retrieval) — NOT a dispatch combinator.

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

def kernel_K(op0: int, op1: int, op2: int) -> int:
    """K x y → x. Select first operand."""
    return op0


def kernel_I(op0: int, op1: int, op2: int) -> int:
    """I x → x. Identity — return first operand unchanged."""
    return op0


def kernel_B(op0: int, op1: int, op2: int) -> int:
    """B f g x → f(g(x)). Compose: additive composition signal."""
    return op0 + op1 + op2


def kernel_C(op0: int, op1: int, op2: int) -> int:
    """C f x y → f y x. Flip: select op0 + op2, skip op1."""
    return op0 + op2


def kernel_D(op0: int, op1: int, op2: int) -> int:
    """D f g h x → f(g(h(x))). Deep compose: triple chain.

    In the kernel pathway, this fuses three composition steps into one.
    Encoded as: op0 * 2 + op1 + op2 (weighted sum emphasizing outer fn).
    """
    return op0 * 2 + op1 + op2


def kernel_Y(op0: int, op1: int, op2: int) -> int:
    """Y f → f(Y(f)). Recursion: feeds function back into itself.

    In the kernel pathway, recursion is a self-reference signal.
    The result maintains the operand (it will be applied again).
    Encoded as: op0 (the function persists through recursion).
    """
    return op0


def kernel_W(op0: int, op1: int, op2: int) -> int:
    """W f x → f(x)(x). Duplicate: apply x twice.

    In the kernel pathway, duplication doubles the argument signal.
    Encoded as: op0 + op1 * 2 (argument contributes twice).
    """
    return op0 + op1 * 2


def kernel_WHNF(op0: int, op1: int, op2: int) -> int:
    """WHNF — terminal. Expression is fully reduced. Pass through.

    In the kernel pathway, WHNF signals "no more reduction needed."
    The FFN pathway handles this position normally.
    Returns op0 unchanged (identity-like for terminal positions).
    """
    return op0


def kernel_M(op0: int, op1: int, op2: int) -> int:
    """M pattern context → content. Match and retrieve.

    NOTE: The neural M pathway does NOT use this function. This
    exists for completeness of the reduction engine. M operates
    via GatedLinearAttention.
    """
    return op1


# Dispatch table for 8-combinator vectorized kernel computation
# (M is NOT in this table — it operates via GatedLinearAttention)
COMBINATOR_KERNEL_FUNCTIONS = [
    kernel_K, kernel_I, kernel_B, kernel_C,
    kernel_D, kernel_Y, kernel_W, kernel_WHNF,
]
assert len(COMBINATOR_KERNEL_FUNCTIONS) == N_COMBINATORS

# Full table (for symbolic reduction engine)
ALL_KERNEL_FUNCTIONS = [
    kernel_K, kernel_I, kernel_B, kernel_C,
    kernel_D, kernel_Y, kernel_W, kernel_WHNF,
    kernel_M,
]
assert len(ALL_KERNEL_FUNCTIONS) == N_KERNELS


# ══════════════════════════════════════════════════════════════════════
# § 6  Self-test
# ══════════════════════════════════════════════════════════════════════

def _self_test() -> None:
    """Smoke-test all eight combinators and the reduction engine."""

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
    # B I I 5 → I (I 5) → I 5 → 5
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

    # ── D combinator: D f g h x → f (g (h x)) ──
    # D I I I 5 → I (I (I 5)) → I (I 5) → I 5 → 5
    t = app(D, I, I, I, atom(5))
    result, steps = reduce(t)
    assert result == atom(5), f"D I I I 5 should reduce to 5, got {result}"

    # D (K 1) I I 5 → (K 1) (I (I 5)) → 1
    t = app(D, app(K, atom(1)), I, I, atom(5))
    result, steps = reduce(t)
    assert result == atom(1), f"D (K 1) I I 5 should reduce to 1, got {result}"

    # ── Y combinator: Y f → f (Y f) ──
    # Y (K 7) → (K 7) (Y (K 7)) → 7 (Y truncates on K)
    t = app(Y, app(K, atom(7)))
    result, steps = reduce(t, max_steps=10)
    assert result == atom(7), f"Y (K 7) should reduce to 7, got {result}"
    # Steps: Y (K 7) → (K 7) (Y (K 7)) → 7 = 2 steps
    assert steps == 2, f"Y (K 7) should take 2 steps, took {steps}"

    # Y I should loop (max_steps stops it)
    t = app(Y, I)
    result, steps = reduce(t, max_steps=5)
    assert steps == 5, f"Y I should hit max_steps, got {steps}"

    # ── W combinator: W f x → f x x ──
    # W K 3 → K 3 3 → 3
    t = app(W, K, atom(3))
    result, steps = reduce(t)
    assert result == atom(3), f"W K 3 should reduce to 3, got {result}"
    # Steps: W K 3 → (K 3) 3 → 3 = 2 steps
    assert steps == 2, f"W K 3 should take 2 steps, took {steps}"

    # W (C K) 3 → (C K) 3 3 → K 3 3 → 3
    t = app(W, app(C, K), atom(3))
    result, steps = reduce(t)
    assert result == atom(3), f"W (C K) 3 should reduce to 3, got {result}"

    # ── WHNF — terminal marker ──
    t = app(WHNF, atom(5))
    result, steps = reduce(t)
    # WHNF x is a normal form (no reduction applies)
    assert steps == 0, f"WHNF 5 should not reduce, took {steps} steps"
    assert isinstance(result, App), f"WHNF 5 should stay as application"

    # ── Composition: S = B(BW)(BBC) expressed through our basis ──
    # Simpler: verify C and K interact correctly
    # C (C K) 1 2 → (C K) 2 1 → K 1 2 → 1
    t = app(C, app(C, K), atom(1), atom(2))
    result, steps = reduce(t)
    assert result == atom(1), f"C (C K) 1 2 should reduce to 1, got {result}"

    # ── Normal-order reduction (outermost first) ──
    # K (I 3) (I 4) → I 3 → 3 (normal order: K first, then I)
    t = app(K, app(I, atom(3)), app(I, atom(4)))
    result, steps = reduce(t)
    assert result == atom(3), f"K (I 3) (I 4) should reduce to 3, got {result}"
    assert steps == 2, f"Expected 2 steps (K then I), got {steps}"

    # ── Kernel functions ──
    assert kernel_K(3, 7, 0) == 3, "kernel_K should select op0"
    assert kernel_I(42, 0, 0) == 42, "kernel_I should return op0"
    assert kernel_B(1, 2, 3) == 6, "kernel_B should sum all three"
    assert kernel_C(1, 2, 3) == 4, "kernel_C should sum op0 + op2"
    assert kernel_D(1, 2, 3) == 7, "kernel_D should be op0*2 + op1 + op2"
    assert kernel_Y(5, 0, 0) == 5, "kernel_Y should return op0"
    assert kernel_W(1, 3, 0) == 7, "kernel_W should be op0 + op1*2"
    assert kernel_WHNF(5, 0, 0) == 5, "kernel_WHNF should return op0"
    assert kernel_M(3, 7, 0) == 7, "kernel_M should return op1 (context)"

    # ── COMBINATOR_NAMES consistency ──
    assert COMBINATOR_NAMES[Combinator.K] == "K"
    assert COMBINATOR_NAMES[Combinator.I] == "I"
    assert COMBINATOR_NAMES[Combinator.B] == "B"
    assert COMBINATOR_NAMES[Combinator.C] == "C"
    assert COMBINATOR_NAMES[Combinator.D] == "D"
    assert COMBINATOR_NAMES[Combinator.Y] == "Y"
    assert COMBINATOR_NAMES[Combinator.W] == "W"
    assert COMBINATOR_NAMES[Combinator.WHNF] == "WHNF"

    # ── Anti-combinator consistency ──
    assert N_ANTI_COMBINATORS == 8, "Anti-crystal must mirror positive crystal"
    assert N_TOTAL_COMBINATORS == 16, "Total = 8 positive + 8 anti"
    assert ANTI_COMBINATOR_NAMES[0] == "āK"
    assert ANTI_COMBINATOR_NAMES[7] == "āWHNF"
    assert len(ALL_COMBINATOR_NAMES) == 16

    # ── KERNEL_NAMES consistency ──
    assert KERNEL_NAMES[Kernel.K] == "K"
    assert KERNEL_NAMES[Kernel.M] == "M"
    assert N_COMBINATORS == 8, "Expanded dispatch must be 8-way"
    assert N_KERNELS == 9, "Full kernel inventory is KIBC-DYWH + M"

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
    print(f"  Base:     K(select), I(identity), B(compose), C(flip)")
    print(f"  Extended: D(deep_compose), Y(recurse), W(duplicate), WHNF(terminal)")
    print(f"  Anti:     āK, āI, āB, āC, āD, āY, āW, āWHNF (shadow crystal)")
    print(f"  Total:    {N_TOTAL_COMBINATORS} embeddings (8 positive + 8 anti)")
    print(f"  Retrieval: M(match) — layer type, not dispatch option")


if __name__ == "__main__":
    _self_test()
