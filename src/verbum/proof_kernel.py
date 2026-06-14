r"""Proof kernel — Curry-Howard proof-checking over the combinator basis.

THE QUESTION (session 228, Michael: "would continuations allow us to run proofs?").
Under the Curry-Howard correspondence:

    proposition  ≡ type (CCG category)
    proof        ≡ a closed term inhabiting that type
    proof-check  ≡ type-check (the S2 unification in lambda_ast)
    normalize    ≡ cut-elimination (β-reduction → WHNF, the continuation)
    run a proof  ≡ reduce the term to its cut-free normal form

The simply-typed combinator basis IS a Hilbert-style proof calculus for the
implicational fragment of intuitionistic propositional logic — the combinators are
exactly the axiom schemes:

    K : A → (B → A)                         (the K axiom)
    S : (A→(B→C)) → ((A→B)→(A→C))           (the S axiom)
    I : A → A                               (trivial proof)
    B : (B→C) → ((A→B)→(A→C))               (→-transitivity / syllogism)
    C : (A→B→C) → (B→A→C)                   (premise permutation)
    W : (A→A→B) → (A→B)                     (contraction)

So `check_proof(term, prop)` asks: does the proposed combinator term have a principal
type of which `prop` is an instance? If yes, the term is a machine-checked proof.

THE CONSISTENCY FIREWALL (the load-bearing point). Two basis members are logically
pathological and must NOT count as proofs:

    Y : (A→A) → A   — the fixed-point combinator. lambda_ast TYPES it (a→a)→a, but
                      (A→A)→A is NOT an intuitionistic theorem; admitting Y as a proof
                      makes the logic inconsistent (every type inhabited, Curry's
                      paradox). ⇒ Y is EXCLUDED from the sound proof basis.
    M : λx.xx       — self-application; lambda_ast's occurs-check rejects it (no simple
                      type). ⇒ never a proof, for free.

A valid proof must therefore be (1) parseable, (2) CLOSED (pure combinators, no free
atoms = no open hypotheses), (3) over the SOUND basis {S,K,I,B,C,W,D}, (4) well-typed,
and (5) typed-at-an-instance-of the goal proposition.

License: MIT — written from this project's observation (lambda_ast.py, the s226
typed-CCG reducer), NOT copied from any external source. AGENTS.md S5 λ provenance.
"""

from __future__ import annotations

from dataclasses import dataclass

from verbum.lambda_ast import (
    App,
    Atom,
    Cat,
    CAtom,
    Comb,
    CSlash,
    CVar,
    Term,
    parse,
    pretty,
    pretty_cat,
    reduce,
    typecheck,
)

__all__ = [
    "ProofCheck",
    "Verdict",
    "check_proof",
    "parse_prop",
    "pretty_prop",
]

# The combinators that ARE logical theorems (axiom schemes + derived theorem
# combinators). D = deep compose (BCKW family), typeable and sound.
SOUND_BASIS = frozenset("SKIBCWD")
# Recursion: typeable by lambda_ast but logically UNSOUND (general recursion = the
# inconsistency edge). Admitting Y "proves" non-theorems like (A→A)→A.
RECURSION = frozenset("Y")


# --------------------------------------------------------------------------- #
# Proposition parser — implicational logic → CCG category                      #
#                                                                              #
# An implication A → B is the functor that takes A and yields B: in lambda_ast #
# CCG syntax that is CSlash(res=B, slash='/', arg=A). '->' is right-associative #
# (A → B → C ≡ A → (B → C)); uppercase letters are propositional atoms.         #
# --------------------------------------------------------------------------- #
def _tokenize_prop(s: str) -> list[str]:
    toks: list[str] = []
    i, n = 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace():
            i += 1
        elif c in "()":
            toks.append(c)
            i += 1
        elif c == "-" and i + 1 < n and s[i + 1] == ">":
            toks.append("->")
            i += 2
        elif c.isalpha():
            toks.append(c)
            i += 1
        else:
            raise ValueError(f"proof_kernel.parse_prop: bad char {c!r} in {s!r}")
    return toks


def parse_prop(s: str) -> Cat:
    """Parse an implicational proposition into a (ground) CCG category.

    Grammar:  prop := factor ('->' prop)? ;  factor := ATOM | '(' prop ')'
    '->' is right-associative; A→B becomes CSlash(B, '/', A) (takes A, yields B)."""
    toks = _tokenize_prop(s)
    pos = 0

    def factor() -> Cat:
        nonlocal pos
        if pos >= len(toks):
            raise ValueError(f"proof_kernel.parse_prop: unexpected end in {s!r}")
        tok = toks[pos]
        if tok == "(":
            pos += 1
            inner = imp()
            if pos >= len(toks) or toks[pos] != ")":
                raise ValueError(f"proof_kernel.parse_prop: unbalanced parens {s!r}")
            pos += 1
            return inner
        if tok in ("->", ")"):
            raise ValueError(f"proof_kernel.parse_prop: unexpected {tok!r} in {s!r}")
        pos += 1
        return CAtom(tok)

    def imp() -> Cat:
        nonlocal pos
        left = factor()
        if pos < len(toks) and toks[pos] == "->":
            pos += 1
            right = imp()
            # left -> right  ==  the functor that takes `left`, yields `right`
            return CSlash(right, "/", left)
        return left

    cat = imp()
    if pos != len(toks):
        raise ValueError(f"proof_kernel.parse_prop: trailing tokens in {s!r}")
    return cat


def pretty_prop(c: Cat) -> str:
    """Render a category back as an implicational proposition (A -> B)."""
    if isinstance(c, CAtom):
        return c.name
    if isinstance(c, CVar):
        return pretty_cat(c)
    # CSlash(res, '/', arg) == arg -> res
    left = pretty_prop(c.arg)
    if isinstance(c.arg, CSlash):
        left = f"({left})"
    return f"{left} -> {pretty_prop(c.res)}"


# --------------------------------------------------------------------------- #
# First-order matcher — is the goal an instance of the term's principal type?  #
# The goal is GROUND (CAtom/CSlash only); the principal type carries CVars.     #
# Unifying a polymorphic principal type against a ground goal reduces to        #
# matching: it succeeds iff some substitution makes the principal equal the goal#
# --------------------------------------------------------------------------- #
def _walk(c: Cat, s: dict[int, Cat]) -> Cat:
    while isinstance(c, CVar) and c.id in s:
        c = s[c.id]
    return c


def _occurs(vid: int, c: Cat, s: dict[int, Cat]) -> bool:
    c = _walk(c, s)
    if isinstance(c, CVar):
        return c.id == vid
    if isinstance(c, CSlash):
        return _occurs(vid, c.res, s) or _occurs(vid, c.arg, s)
    return False


def _unify(x: Cat, y: Cat, s: dict[int, Cat]) -> bool:
    x, y = _walk(x, s), _walk(y, s)
    if isinstance(x, CVar):
        if isinstance(y, CVar) and y.id == x.id:
            return True
        if _occurs(x.id, y, s):
            return False
        s[x.id] = y
        return True
    if isinstance(y, CVar):
        return _unify(y, x, s)
    if isinstance(x, CAtom) and isinstance(y, CAtom):
        return x.name == y.name
    if isinstance(x, CSlash) and isinstance(y, CSlash):
        return (
            x.slash == y.slash
            and _unify(x.res, y.res, s)
            and _unify(x.arg, y.arg, s)
        )
    return False


def _combinators(t: Term) -> set[str]:
    if isinstance(t, Comb):
        return {t.name}
    if isinstance(t, App):
        return _combinators(t.fn) | _combinators(t.arg)
    return set()


def _has_atom(t: Term) -> bool:
    if isinstance(t, Atom):
        return True
    if isinstance(t, App):
        return _has_atom(t.fn) or _has_atom(t.arg)
    return False


# --------------------------------------------------------------------------- #
# The verdict                                                                  #
# --------------------------------------------------------------------------- #
class Verdict:
    VALID = "valid"                    # a machine-checked proof
    NONE = "none"                      # the prover declined (claims unprovable)
    PARSE_ERROR = "parse_error"        # term/prop did not parse
    OPEN_TERM = "open_term"            # contains free atoms (open hypotheses)
    UNSOUND_RECURSION = "unsound_recursion"  # uses Y (general recursion)
    ILL_TYPED = "ill_typed"            # no simple type (e.g. M = self-application)
    TYPE_MISMATCH = "type_mismatch"    # well-typed, but not at the goal proposition


@dataclass(frozen=True, slots=True)
class ProofCheck:
    term: str
    prop: str
    verdict: str
    valid: bool                 # verdict == VALID (a sound, checked proof)
    well_typed: bool
    principal: str | None       # the term's synthesised principal proposition
    normal_form: str | None     # cut-free form (the proof "run" to normal form)
    status: str | None          # reduction status (normal_form / diverged / …)
    combinators: tuple[str, ...]
    detail: str | None = None


def check_proof(term: str, prop: str) -> ProofCheck:
    """Check whether `term` is a sound proof of the proposition `prop`.

    Returns a ProofCheck whose `verdict` distinguishes the failure modes. A VALID
    verdict means: closed, over the sound basis {S,K,I,B,C,W,D}, well-typed, and the
    term's principal type has `prop` as an instance — i.e. a machine-checked proof.
    The `normal_form` records the term reduced to WHNF/normal form (cut-elimination).
    """
    raw = term.strip()
    if raw.lower() in ("none", "no proof", "unprovable", "∄", ""):
        return ProofCheck(term, prop, Verdict.NONE, False, False, None, None, None, ())

    # parse the goal proposition
    try:
        goal = parse_prop(prop)
    except ValueError as e:
        return ProofCheck(term, prop, Verdict.PARSE_ERROR, False, False, None,
                          None, None, (), f"prop: {e}")

    # parse the candidate proof term
    try:
        t = parse(raw)
    except ValueError as e:
        return ProofCheck(term, prop, Verdict.PARSE_ERROR, False, False, None,
                          None, None, (), f"term: {e}")

    combs = tuple(sorted(_combinators(t)))

    # run the proof (cut-elimination) regardless of soundness — for the record
    red = reduce(t)
    nf = pretty(red.normal_form)
    status = red.status.value

    # (2) closed?  open terms = open hypotheses, not a closed proof
    if _has_atom(t):
        return ProofCheck(term, prop, Verdict.OPEN_TERM, False, False, None,
                          nf, status, combs, "term has free atoms (open hypotheses)")

    # (3) sound basis? Y = general recursion = the inconsistency edge
    if any(c in RECURSION for c in combs):
        return ProofCheck(term, prop, Verdict.UNSOUND_RECURSION, False, False, None,
                          nf, status, combs, "uses Y (recursion is logically unsound)")

    # (4) well-typed?  (M's occurs-check failure lands here)
    tr = typecheck(t)
    if not tr.ok or tr.cat is None:
        return ProofCheck(term, prop, Verdict.ILL_TYPED, False, False, None,
                          nf, status, combs, tr.error)
    principal = pretty_prop(tr.cat)

    # (5) is the goal an instance of the principal type?
    if _unify(tr.cat, goal, {}):
        return ProofCheck(term, prop, Verdict.VALID, True, True, principal,
                          nf, status, combs)
    return ProofCheck(term, prop, Verdict.TYPE_MISMATCH, False, True, principal,
                      nf, status, combs, "principal type does not match the goal")
