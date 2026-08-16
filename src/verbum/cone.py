"""Reference dependency cones for the prefill triangle (§P-PREFILL-CONE, s335).

The prefill grid is (position × layer); a leaf perturbation's *machine cone* is
the set of cells whose residual state changes. This module computes the
*calculus cone* — the cells that SHOULD change under a given substitution
algorithm — from the certified reducer in :mod:`verbum.lambda_ast`:

  span ∈ cone_R(leaf) ⟺ NF_R(subterm-at-span) changes (``alpha_eq``) when the
  leaf atom is swapped for a fresh atom.

The comparison is RAW (no mapping of the fresh name back to the original): the
machine reduces both prompts independently, so a cell that merely CARRIES the
leaf's value verbatim genuinely differs between the two runs — flow-through is
in-cone under every algorithm. Discrimination comes from cells where the
algorithms disagree about whether the value ARRIVES (e.g. a trailing argument
consumed by a capture-created binder: in ``((λx.λy.x) y) e f`` the correct NF
``y f`` never touches ``e`` while the naive NF IS ``e f``). Pure bound-variable
renaming is modded out by ``alpha_eq`` — conservative for name-carrying
machines (under-counts, never over-counts, cone membership).

Computed under both ``R_NORMAL`` (capture-avoiding) and ``R_NAIVE`` (the
s331/s332 measured algorithm). A *discriminating leaf* is one whose two cones
disagree somewhere — the cell-resolved watchable form of the NAIVE-SUBST law.

Char-span → token-index mapping is offsets-based and tokenizer-agnostic, so
planted-world validation exercises the identical code path with synthetic
offsets (AGENTS.md s331 lesson: validate-planted must share real plumbing).

License: MIT.
"""

from __future__ import annotations

from dataclasses import dataclass

from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    App,
    Atom,
    Comb,
    Lam,
    Status,
    Term,
    alpha_eq,
    parse,
    pretty,
    reduce,
    spine,
)

__all__ = [
    "LeafPerturbation",
    "Span",
    "annotate",
    "fresh_replacement",
    "leaf_perturbations",
    "span_token_range",
    "term_names",
]

# Lowercase, single-char, outside the subst_pairs pools (x | y,w,u | a,b,c) so a
# swap is fresh by construction on battery terms; filtered per-term regardless.
_REPL_POOL = ("n", "m", "r", "t", "v", "q", "j", "k")


@dataclass(frozen=True, slots=True)
class Span:
    """One AST node's char span in the canonical ``pretty`` rendering.

    ``idx`` is the position in the deterministic traversal order — stable
    across structurally isomorphic terms, which is what lets original and
    perturbed nodes be paired by index.
    """

    idx: int
    start: int
    end: int  # exclusive
    kind: str  # "atom" | "comb" | "lam" | "app"
    free_leaf: bool  # Atom occurrence with no enclosing binder of that name


def annotate(t: Term) -> tuple[str, list[Span], list[Term]]:
    """Render ``t`` exactly as :func:`verbum.lambda_ast.pretty`, with spans.

    Returns ``(text, spans, terms)`` where ``spans[i]`` describes ``terms[i]``.
    Raises ``AssertionError`` if the rendering ever drifts from ``pretty`` —
    the round-trip is a PC0 gate, not a hope.
    """
    raw: list[tuple[int, int, str, bool]] = []
    terms: list[Term] = []

    def rec(t: Term, off: int, bound: frozenset[str]) -> str:
        if isinstance(t, Comb):
            s = t.name
            raw.append((off, off + len(s), "comb", False))
            terms.append(t)
            return s
        if isinstance(t, Atom):
            s = t.name
            raw.append((off, off + len(s), "atom", t.name not in bound))
            terms.append(t)
            return s
        if isinstance(t, Lam):
            prefix = f"λ{t.var}."
            body = rec(t.body, off + len(prefix), bound | {t.var})
            s = prefix + body
            raw.append((off, off + len(s), "lam", False))
            terms.append(t)
            return s
        # App — mirror pretty(): flatten the spine, one span per chain node.
        head, args = spine(t)
        chain: list[Term] = []
        tt: Term = t
        while isinstance(tt, App):
            chain.append(tt)
            tt = tt.fn
        chain.reverse()  # chain[i] wraps head + args[: i + 1]
        cur = off
        if isinstance(head, Lam):
            head_s = "(" + rec(head, cur + 1, bound) + ")"
        else:
            head_s = rec(head, cur, bound)
        parts = [head_s]
        cur = off + len(head_s)
        for i, a in enumerate(args):
            cur += 1  # the joining space
            if isinstance(a, App | Lam):
                arg_s = "(" + rec(a, cur + 1, bound) + ")"
            else:
                arg_s = rec(a, cur, bound)
            parts.append(arg_s)
            cur += len(arg_s)
            raw.append((off, cur, "app", False))
            terms.append(chain[i])
        return " ".join(parts)

    text = rec(t, 0, frozenset())
    if text != pretty(t):  # pragma: no cover - structural invariant
        msg = f"annotate drifted from pretty: {text!r} != {pretty(t)!r}"
        raise AssertionError(msg)
    spans = [Span(i, a, b, k, fl) for i, (a, b, k, fl) in enumerate(raw)]
    return text, spans, terms


def term_names(t: Term) -> frozenset[str]:
    """Every atom name and binder variable appearing anywhere in ``t``."""
    if isinstance(t, Comb | Atom):
        return frozenset((t.name,))
    if isinstance(t, Lam):
        return term_names(t.body) | {t.var}
    return term_names(t.fn) | term_names(t.arg)


def fresh_replacement(t: Term, exclude: frozenset[str] = frozenset()) -> str | None:
    """A pool atom name not appearing in ``t`` (nor in ``exclude``)."""
    used = term_names(t) | exclude
    for cand in _REPL_POOL:
        if cand not in used:
            return cand
    return None


@dataclass(frozen=True, slots=True)
class LeafPerturbation:
    """One free-leaf swap with its reference cones under both calculi.

    ``cone_normal`` / ``cone_naive`` are span indices (into the ``annotate``
    node list of the ORIGINAL term) whose subterm NF depends on the leaf under
    that calculus. ``undecided`` are spans where either reduction failed to
    normalize (budget) — excluded from every downstream pool.
    """

    leaf_idx: int
    start: int
    end: int
    orig: str
    repl: str
    pert_text: str
    cone_normal: frozenset[int]
    cone_naive: frozenset[int]
    undecided: frozenset[int]

    @property
    def naive_only(self) -> frozenset[int]:
        return self.cone_naive - self.cone_normal

    @property
    def correct_only(self) -> frozenset[int]:
        return self.cone_normal - self.cone_naive

    @property
    def discriminating(self) -> bool:
        return bool(self.naive_only or self.correct_only)


def _perturb(
    term_text: str,
    spans: list[Span],
    terms: list[Term],
    leaf: Span,
    repl: str,
    max_steps: int,
) -> LeafPerturbation | None:
    pert_text = term_text[: leaf.start] + repl + term_text[leaf.end :]
    try:
        pt = parse(pert_text)
    except ValueError:
        return None
    p_text, _p_spans, p_terms = annotate(pt)
    if p_text != pert_text or len(p_terms) != len(terms):
        return None  # structure drift — not an isomorphic swap
    orig_name = term_text[leaf.start : leaf.end]

    def in_cone(o: Term, p: Term, calc) -> bool | None:
        ro = reduce(o, max_steps=max_steps, calc=calc)
        rp = reduce(p, max_steps=max_steps, calc=calc)
        if ro.status is not Status.NORMAL_FORM or rp.status is not Status.NORMAL_FORM:
            return None
        return not alpha_eq(ro.normal_form, rp.normal_form)

    cone_n: set[int] = set()
    cone_v: set[int] = set()
    undecided: set[int] = set()
    for i, (o, p) in enumerate(zip(terms, p_terms, strict=True)):
        a = in_cone(o, p, R_NORMAL)
        b = in_cone(o, p, R_NAIVE)
        if a is None or b is None:
            undecided.add(i)
            continue
        if a:
            cone_n.add(i)
        if b:
            cone_v.add(i)
    return LeafPerturbation(
        leaf.idx,
        leaf.start,
        leaf.end,
        orig_name,
        repl,
        pert_text,
        frozenset(cone_n),
        frozenset(cone_v),
        frozenset(undecided),
    )


def leaf_perturbations(
    term_text: str, max_steps: int = 512, repl: str | None = None
) -> list[LeafPerturbation]:
    """Every free-leaf perturbation of ``term_text`` (canonical rendering) with
    reference cones under both calculi. Callers select discriminating ones.

    ``repl`` pins the replacement atom (must be fresh for the term); default
    picks the first fresh pool name. Replaying with several ``repl`` values is
    the M3 replication axis.
    """
    t = parse(term_text)
    text, spans, terms = annotate(t)
    if text != term_text:
        msg = f"term_text not canonical: {term_text!r} renders as {text!r}"
        raise ValueError(msg)
    if repl is not None and repl in term_names(t):
        msg = f"repl {repl!r} is not fresh for {term_text!r}"
        raise ValueError(msg)
    if repl is None:
        repl = fresh_replacement(t)
    if repl is None:
        return []
    out: list[LeafPerturbation] = []
    for sp in spans:
        if not sp.free_leaf:
            continue
        lp = _perturb(text, spans, terms, sp, repl, max_steps)
        if lp is not None:
            out.append(lp)
    return out


def span_token_range(
    char_start: int,
    char_end: int,
    offsets: list[tuple[int, int]],
    base: int = 0,
) -> tuple[int, int] | None:
    """Token index range ``(first, last)`` overlapping chars
    ``[base+char_start, base+char_end)``. ``last`` is the CLOSING token — the
    grid column where the subterm's value is causally complete. ``None`` if no
    token overlaps (e.g. span sits outside the tokenized window)."""
    lo: int | None = None
    hi: int | None = None
    a, b = base + char_start, base + char_end
    for i, (s, e) in enumerate(offsets):
        if e <= a or s >= b or s == e:
            continue
        if lo is None:
            lo = i
        hi = i
    if lo is None or hi is None:
        return None
    return lo, hi
