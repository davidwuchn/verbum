r"""Proof search — goal-directed natural deduction = proving via the continuation.

THE QUESTION (session 228). The single-shot prover (proof_inhabitation.py) showed
models prove the AXIOMS but fail to COMPOSE multi-combinator proof terms (K I, C B,
C I, B K K). The predicted fix (lambda-halt-continuation.md §"composition fails but
continuations solve it"): prove STEPWISE — one inference rule per turn — and let the
CONTINUATION carry the proof state between steps.

This module is that engine. Backward (goal-directed) natural deduction for the
implicational fragment: the proof state is a stack of open goals (the reified
CONTINUATION — "the rest of the proof"); each move acts on the focused (first) goal;
on QED the kernel RECONSTRUCTS the proof term via bracket abstraction
(lambda_compile, the exact compile oracle) and VERIFIES it (proof_kernel). The model
(or the automatic solver) only chooses moves — the kernel guarantees soundness, so a
wrong move can never produce a false proof.

  intro   : goal P->Q  ⟶  assume h:P, new goal Q          (builds a λh.)
  exact h : goal P, hypothesis h:P in context  ⟶  close    (a variable)
  apply h : h:P1->..->Pk->Q, goal Q  ⟶  k subgoals P1..Pk  (modus ponens / →-elim)

Term reconstruction: a tiny lambda ADT (LVar/LApp/LLam/LHole) is assembled during
search, then compiled to a closed combinator term — Lam(x, body) ⟶ abstract x out of
the compiled body (lambda_compile.compile_expr). The continuation is LITERAL: the open
goal stack is the suspended proof; filling a hole resumes it (cf. sealable-
continuation).

License: MIT
"""

from __future__ import annotations

from dataclasses import dataclass, field, replace

from verbum.lambda_ast import Atom, Cat, CAtom, CSlash, CVar, Term
from verbum.lambda_compile import compile_expr
from verbum.proof_kernel import check_proof, parse_prop, pretty_prop

__all__ = [
    "LApp",
    "LHole",
    "LLam",
    "LTerm",
    "LVar",
    "ProofState",
    "init_state",
    "legal_moves",
    "make_move",
    "reconstruct",
    "solve",
    "verify_state",
]


# --------------------------------------------------------------------------- #
# Lambda term with holes (the partial proof under construction)                #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class LVar:
    name: str


@dataclass(frozen=True, slots=True)
class LApp:
    fn: LTerm
    arg: LTerm


@dataclass(frozen=True, slots=True)
class LLam:
    var: str
    body: LTerm


@dataclass(frozen=True, slots=True)
class LHole:
    id: int


LTerm = LVar | LApp | LLam | LHole


def _subst_hole(t: LTerm, hid: int, repl: LTerm) -> LTerm:
    if isinstance(t, LHole):
        return repl if t.id == hid else t
    if isinstance(t, LApp):
        return LApp(_subst_hole(t.fn, hid, repl), _subst_hole(t.arg, hid, repl))
    if isinstance(t, LLam):
        return LLam(t.var, _subst_hole(t.body, hid, repl))
    return t


def _to_combinator(t: LTerm) -> Term:
    """Compile a hole-free lambda term to a closed combinator term.

    LLam(x, body) ⟶ bracket-abstract x out of the compiled body (the exact compile
    oracle). LVar/LApp map directly; abstraction closes every binder."""
    if isinstance(t, LVar):
        return Atom(t.name)
    if isinstance(t, LApp):
        from verbum.lambda_ast import App
        return App(_to_combinator(t.fn), _to_combinator(t.arg))
    if isinstance(t, LLam):
        return compile_expr([t.var], _to_combinator(t.body))
    raise ValueError("cannot compile a term with open holes")


# --------------------------------------------------------------------------- #
# Categories: structural equality + antecedent peeling                         #
# --------------------------------------------------------------------------- #
def cat_eq(a: Cat, b: Cat) -> bool:
    if isinstance(a, CAtom) and isinstance(b, CAtom):
        return a.name == b.name
    if isinstance(a, CVar) and isinstance(b, CVar):
        return a.id == b.id
    if isinstance(a, CSlash) and isinstance(b, CSlash):
        return a.slash == b.slash and cat_eq(a.res, b.res) and cat_eq(a.arg, b.arg)
    return False


def _peel_to(htype: Cat, target: Cat) -> list[Cat] | None:
    """Antecedents to supply so that applying a term of `htype` yields `target`.

    [] means htype == target (exact); None means unreachable by forward application."""
    args: list[Cat] = []
    cur = htype
    seen = 0
    while not cat_eq(cur, target):
        if isinstance(cur, CSlash) and seen < 64:
            args.append(cur.arg)
            cur = cur.res
            seen += 1
        else:
            return None
    return args


# --------------------------------------------------------------------------- #
# Proof state — the goal stack IS the reified continuation                      #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Goal:
    hole: int
    ctx: tuple[tuple[str, Cat], ...]   # (hyp name, proposition)
    target: Cat


@dataclass(frozen=True, slots=True)
class ProofState:
    prop: str                          # the original goal proposition (for verify)
    root: LTerm                        # partial proof term (with holes)
    goals: tuple[Goal, ...]            # open goals; goals[0] is focused
    fresh: int = field(default=0)      # counter for hyp names / hole ids

    @property
    def done(self) -> bool:
        return len(self.goals) == 0


def init_state(prop: str) -> ProofState:
    goal = Goal(hole=0, ctx=(), target=parse_prop(prop))
    return ProofState(prop=prop, root=LHole(0), goals=(goal,), fresh=1)


def legal_moves(st: ProofState) -> list[str]:
    """Moves available on the focused goal (goals[0])."""
    if st.done:
        return []
    g = st.goals[0]
    moves: list[str] = []
    if isinstance(g.target, CSlash):          # implication ⟶ intro
        moves.append("intro")
    for name, htype in g.ctx:                 # exact / apply per hypothesis
        peeled = _peel_to(htype, g.target)
        if peeled is None:
            continue
        if len(peeled) == 0:
            moves.append(f"exact {name}")
        else:
            moves.append(f"apply {name}")
    return moves


def make_move(st: ProofState, move: str) -> ProofState:
    """Apply a move to the focused goal; returns the new state. Raises on illegal."""
    if st.done:
        raise ValueError("no open goals")
    g = st.goals[0]
    rest = st.goals[1:]
    parts = move.split()
    op = parts[0]

    if op == "intro":
        if not isinstance(g.target, CSlash):
            raise ValueError(
                f"intro: goal {pretty_prop(g.target)} is not an implication")
        hname = f"h{len(g.ctx) + 1}"      # consecutive names by context depth
        new_hole = st.fresh
        ctx2 = (*g.ctx, (hname, g.target.arg))
        sub = Goal(hole=new_hole, ctx=ctx2, target=g.target.res)
        root2 = _subst_hole(st.root, g.hole, LLam(hname, LHole(new_hole)))
        return replace(st, root=root2, goals=(sub, *rest), fresh=st.fresh + 1)

    if op in ("exact", "apply"):
        if len(parts) != 2:
            raise ValueError(f"{op}: expected a hypothesis name")
        name = parts[1]
        htype = next((t for n, t in g.ctx if n == name), None)
        if htype is None:
            raise ValueError(f"{op}: no hypothesis {name!r} in context")
        peeled = _peel_to(htype, g.target)
        if peeled is None:
            raise ValueError(f"{op} {name}: type {pretty_prop(htype)} cannot reach "
                             f"goal {pretty_prop(g.target)}")
        if op == "exact":
            if len(peeled) != 0:
                raise ValueError(f"exact {name}: not an exact match (use apply)")
            root2 = _subst_hole(st.root, g.hole, LVar(name))
            return replace(st, root=root2, goals=rest)
        # apply: build h applied to k fresh holes; k new subgoals (same ctx)
        if len(peeled) == 0:
            raise ValueError(f"apply {name}: exact match (use exact)")
        term: LTerm = LVar(name)
        subgoals: list[Goal] = []
        hid = st.fresh
        for ptype in peeled:
            term = LApp(term, LHole(hid))
            subgoals.append(Goal(hole=hid, ctx=g.ctx, target=ptype))
            hid += 1
        root2 = _subst_hole(st.root, g.hole, term)
        return replace(st, root=root2, goals=(*subgoals, *rest), fresh=hid)

    raise ValueError(f"unknown move {move!r}")


def reconstruct(st: ProofState) -> Term:
    """At QED, compile the partial term to a closed combinator term (the proof)."""
    if not st.done:
        raise ValueError("proof incomplete: open goals remain")
    return _to_combinator(st.root)


def verify_state(st: ProofState):
    """Reconstruct and kernel-verify the proof against the original proposition."""
    from verbum.lambda_ast import pretty
    term = reconstruct(st)
    return check_proof(pretty(term), st.prop)


# --------------------------------------------------------------------------- #
# Automatic solver — depth-first over {intro, exact, apply} (the engine floor) #
# --------------------------------------------------------------------------- #
def solve(prop: str, max_depth: int = 24) -> ProofState | None:
    """Depth-bounded backward search. Returns a closed ProofState or None.

    Move order: exact (close) > intro (shrink) > apply (branch) — cheapest first.
    A per-branch (ctx, target) visited guard blocks apply-loops."""
    start = init_state(prop)

    def order(moves: list[str]) -> list[str]:
        rank = {"exact": 0, "intro": 1, "apply": 2}
        return sorted(moves, key=lambda m: rank[m.split()[0]])

    def dfs(st: ProofState, depth: int, seen: frozenset) -> ProofState | None:
        if st.done:
            return st
        if depth > max_depth:
            return None
        g = st.goals[0]
        key = (tuple(sorted(pretty_prop(t) for _, t in g.ctx)), pretty_prop(g.target))
        for move in order(legal_moves(st)):
            # only guard against revisiting the SAME focused goal via apply (loops)
            seen2 = seen
            if move.startswith("apply"):
                if key in seen:
                    continue
                seen2 = seen | {key}
            try:
                ns = make_move(st, move)
            except ValueError:
                continue
            r = dfs(ns, depth + 1, seen2)
            if r is not None:
                return r
        return None

    return dfs(start, 0, frozenset())
