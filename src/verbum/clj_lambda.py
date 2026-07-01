r"""clj_lambda — a Clojure-subset interpreter that compiles to the verbum kernel.

THE ROLE (notebook: notebooks/clojure_in_lambda.ipynb). A constructive witness for
AGENTS.md S5 `λ types` ("composition ≡ typed application"): a real homoiconic Lisp's
evaluator collapses to *typed combinator application*. We do not build a new reducer —
we reuse the project's existing machinery end-to-end:

    Clojure form   → named lambda    : `compile_clj`   (this module — reader + compiler)
    named lambda    → SKI combinator  : `lambda_compile.abstract` (bracket abstraction)
    combinator term → normal form     : `lambda_ast.reduce`       (the kernel oracle)
    normal form     → Clojure value   : `decode`        (Church numerals / booleans)

So `(+ 2 3)` becomes a closed combinator term over {S,K,I,B,C,...}, reduces in the same
kernel that grades the lambda compiler, and decodes back to `5`. Data (numbers,
booleans, pairs) are Church-encoded; recursion is the kernel's own `Y`; `if` is an
ordinary prelude function (normal-order reduction gives it lazy branch selection for
free). The *pure functional core* of Clojure — `fn`, application, `let`, conditionals,
recursion — is exactly lambda calculus with reader sugar; host interop / mutation /
persistent-DS performance are the honest boundary and are out of scope by construction.

License: MIT. AGENTS.md S5 λ provenance (written from theory + this project's kernel,
not nucleus). λ one_way / λ compose: reuses lambda_ast + lambda_compile, adds only the
Clojure front-end.
"""

from __future__ import annotations

from dataclasses import dataclass

from verbum.lambda_ast import (
    App,
    Atom,
    Comb,
    Reduction,
    Term,
    pretty,
    reduce,
)
from verbum.lambda_compile import abstract, compile_expr

__all__ = [
    "PRELUDE",
    "SPECIAL_FORMS",
    "Sym",
    "Vector",
    "church",
    "compile_clj",
    "decode",
    "read",
    "reduce_clj",
    "run",
]

# Generous default budgets — Church arithmetic + Y-recursion blow past the kernel's
# conservative MAX_STEPS/MAX_SIZE (512/4096); these fit factorial(3) and small programs.
DEFAULT_STEPS = 200_000
DEFAULT_SIZE = 2_000_000


# --------------------------------------------------------------------------- #
# Reader — text → s-expression (Sym | int | list | Vector)                    #
# --------------------------------------------------------------------------- #
@dataclass(frozen=True, slots=True)
class Sym:
    """A Clojure symbol (a name — variable, primitive, or special-form head)."""

    name: str


class Vector(list):
    """A Clojure vector literal `[...]`. Subclasses list so it is still iterable;
    the `list` vs `Vector` distinction marks binding positions (fn params, let)."""


SExpr = Sym | int | list | Vector

_DELIMS = "()[]"


def _tokenize(s: str) -> list[str]:
    toks, i, n = [], 0, len(s)
    while i < n:
        c = s[i]
        if c.isspace() or c == ",":  # commas are whitespace in Clojure
            i += 1
        elif c in _DELIMS:
            toks.append(c)
            i += 1
        elif c == ";":  # line comment
            while i < n and s[i] != "\n":
                i += 1
        else:
            j = i
            while j < n and not s[j].isspace() and s[j] not in _DELIMS and s[j] != ",":
                j += 1
            toks.append(s[i:j])
            i = j
    return toks


def _atom(tok: str) -> Sym | int:
    if tok.lstrip("-").isdigit() and tok not in ("-", ""):
        return int(tok)
    return Sym(tok)


def read(src: str) -> SExpr:
    """Read a single s-expression from `src`."""
    toks = _tokenize(src)
    pos = 0

    def rd() -> SExpr:
        nonlocal pos
        if pos >= len(toks):
            raise SyntaxError("clj_lambda.read: unexpected end of input")
        tok = toks[pos]
        pos += 1
        if tok in "([":
            close = ")" if tok == "(" else "]"
            items: list[SExpr] = []
            while pos < len(toks) and toks[pos] != close:
                items.append(rd())
            if pos >= len(toks):
                raise SyntaxError(f"clj_lambda.read: missing {close!r}")
            pos += 1  # consume close
            return items if tok == "(" else Vector(items)
        if tok in ")]":
            raise SyntaxError(f"clj_lambda.read: unexpected {tok!r}")
        return _atom(tok)

    form = rd()
    if pos != len(toks):
        raise SyntaxError(f"clj_lambda.read: trailing tokens {toks[pos:]!r}")
    return form


# --------------------------------------------------------------------------- #
# Church encodings — data as combinator terms (built once, closed = pure SKI) #
# --------------------------------------------------------------------------- #
def _ap(*ts: Term) -> Term:
    """Left-associative application chain."""
    t = ts[0]
    for x in ts[1:]:
        t = App(t, x)
    return t


def church(n: int) -> Term:
    """Church numeral `n` = λf.λx. f (f ... (f x))  → a closed combinator term."""
    if n < 0:
        raise ValueError("clj_lambda.church: no Church encoding for negatives")
    body: Term = Atom("x")
    for _ in range(n):
        body = App(Atom("f"), body)
    return compile_expr(["f", "x"], body)


def _prelude() -> dict[str, Term]:
    """Build the prelude: Church encodings as closed combinator terms.

    Every entry is produced by bracket-abstracting a named lambda, so each is a
    closed term over {S,K,I,B,C,...} that the kernel reduces directly."""
    a, b, c = Atom("a"), Atom("b"), Atom("c")
    f, g, h = Atom("f"), Atom("g"), Atom("h")
    m, n, p, q = Atom("m"), Atom("n"), Atom("p"), Atom("q")
    s, u, x = Atom("s"), Atom("u"), Atom("x")

    true = compile_expr(["a", "b"], a)   # λa.λb. a
    false = compile_expr(["a", "b"], b)  # λa.λb. b

    succ = compile_expr(["n", "f", "x"], _ap(f, _ap(n, f, x)))
    plus = compile_expr(["m", "n", "f", "x"], _ap(m, f, _ap(n, f, x)))
    mult = compile_expr(["m", "n", "f"], _ap(m, _ap(n, f)))
    # Church predecessor (Kleene): λn.λf.λx. n (λg.λh. h (g f)) (λu. x) (λu. u)
    pred = compile_expr(
        ["n", "f", "x"],
        _ap(
            n,
            compile_expr(["g", "h"], _ap(h, _ap(g, f))),
            compile_expr(["u"], x),
            compile_expr(["u"], u),
        ),
    )
    sub = compile_expr(["m", "n"], _ap(n, pred, m))  # m - n = apply pred n times to m

    iszero = compile_expr(["n"], _ap(n, compile_expr(["x"], false), true))
    if_ = compile_expr(["c", "a", "b"], _ap(c, a, b))  # church bool selects branch
    not_ = compile_expr(["p"], _ap(p, false, true))
    and_ = compile_expr(["p", "q"], _ap(p, q, p))  # and p q = p q p
    or_ = compile_expr(["p", "q"], _ap(p, p, q))   # or  p q = p p q

    cons = compile_expr(["a", "b", "s"], _ap(s, a, b))  # pair = λa.λb.λs. s a b
    first = compile_expr(["p"], _ap(p, true))           # car = λp. p true
    rest = compile_expr(["p"], _ap(p, false))           # cdr = λp. p false

    return {
        # arithmetic
        "inc": succ, "succ": succ, "+": plus, "plus": plus,
        "*": mult, "mult": mult, "dec": pred, "pred": pred,
        "-": sub, "sub": sub,
        # predicates / booleans
        "zero?": iszero, "true": true, "false": false, "if": if_,
        "not": not_, "and": and_, "or": or_,
        # pairs / lists
        "cons": cons, "pair": cons, "first": first, "car": first,
        "rest": rest, "cdr": rest,
        # recursion — the kernel's own fixpoint combinator
        "Y": Comb("Y"),
    }


PRELUDE: dict[str, Term] = _prelude()
SPECIAL_FORMS = frozenset({"fn", "let"})


# --------------------------------------------------------------------------- #
# Compiler — s-expression → combinator Term                                    #
# --------------------------------------------------------------------------- #
def _compile(e: SExpr, scope: frozenset[str], prelude: dict[str, Term]) -> Term:
    if isinstance(e, int):
        return church(e)
    if isinstance(e, Sym):
        if e.name in scope:
            return Atom(e.name)  # a lambda-bound variable, abstracted by fn/let
        if e.name in prelude:
            return prelude[e.name]
        raise NameError(f"clj_lambda: unbound symbol {e.name!r}")
    if isinstance(e, Vector):
        raise SyntaxError("clj_lambda: vector only valid in fn/let binding position")
    if not e:
        raise SyntaxError("clj_lambda: cannot compile empty list ()")

    head = e[0]
    if isinstance(head, Sym) and head.name in SPECIAL_FORMS:
        if head.name == "fn":
            return _compile_fn(e, scope, prelude)
        return _compile_let(e, scope, prelude)

    # ordinary application: (f a b ...) → ((f a) b) ...
    return _ap(*[_compile(x, scope, prelude) for x in e])


def _compile_fn(e: list, scope: frozenset[str], prelude: dict[str, Term]) -> Term:
    # (fn [p1 p2 ...] body)
    if len(e) != 3 or not isinstance(e[1], Vector):
        raise SyntaxError("clj_lambda: fn must be (fn [params] body)")
    params = [p.name for p in e[1] if isinstance(p, Sym)]
    if len(params) != len(e[1]):
        raise SyntaxError("clj_lambda: fn params must be symbols")
    body = _compile(e[2], scope | set(params), prelude)
    return compile_expr(params, body)  # curried bracket abstraction


def _compile_let(e: list, scope: frozenset[str], prelude: dict[str, Term]) -> Term:
    # (let [k1 v1 k2 v2 ...] body) → nested ((fn [k] body') v)
    if len(e) != 3 or not isinstance(e[1], Vector):
        raise SyntaxError("clj_lambda: let must be (let [bindings] body)")
    binds = e[1]
    if len(binds) % 2 != 0:
        raise SyntaxError("clj_lambda: let needs an even number of binding forms")
    pairs = [(binds[i], binds[i + 1]) for i in range(0, len(binds), 2)]

    def go(rest: list, sc: frozenset[str]) -> Term:
        if not rest:
            return _compile(e[2], sc, prelude)
        (name, val), tail = rest[0], rest[1:]
        if not isinstance(name, Sym):
            raise SyntaxError("clj_lambda: let binding name must be a symbol")
        vterm = _compile(val, sc, prelude)          # value sees earlier bindings
        inner = go(tail, sc | {name.name})
        return App(abstract(name.name, inner), vterm)  # ((λname. inner) vterm)

    return go(pairs, scope)


def compile_clj(src: str | SExpr, prelude: dict[str, Term] | None = None) -> Term:
    """Compile Clojure source (or a pre-read s-expression) to a combinator Term."""
    form = read(src) if isinstance(src, str) else src
    return _compile(form, frozenset(), prelude if prelude is not None else PRELUDE)


# --------------------------------------------------------------------------- #
# Eval + decode — reduce in the kernel, read Church data back to Python        #
# --------------------------------------------------------------------------- #
def reduce_clj(
    src: str | SExpr,
    max_steps: int = DEFAULT_STEPS,
    max_size: int = DEFAULT_SIZE,
    prelude: dict[str, Term] | None = None,
) -> Reduction:
    """Compile and reduce — returns the full kernel Reduction (trace, status, steps)."""
    return reduce(compile_clj(src, prelude), max_steps=max_steps, max_size=max_size)


def _decode_int(term: Term, max_steps: int, max_size: int) -> int:
    probe = _ap(term, Atom("f"), Atom("x"))
    red = reduce(probe, max_steps=max_steps, max_size=max_size)
    nf = pretty(red.normal_form)
    # a Church numeral applied to (f, x) is f (f (... x)): tokens are only f, x, ( )
    toks = [t for t in nf.replace("(", " ").replace(")", " ").split() if t]
    if any(t not in ("f", "x") for t in toks) or (toks and toks[-1] != "x"):
        raise ValueError(f"clj_lambda.decode: not a Church numeral: {nf!r}")
    return toks.count("f")


def _decode_bool(term: Term, max_steps: int, max_size: int) -> bool:
    probe = _ap(term, Atom("T"), Atom("F"))
    red = reduce(probe, max_steps=max_steps, max_size=max_size)
    nf = pretty(red.normal_form)
    if nf == "T":
        return True
    if nf == "F":
        return False
    raise ValueError(f"clj_lambda.decode: not a Church boolean: {nf!r}")


def decode(
    term: Term,
    kind: str = "int",
    max_steps: int = DEFAULT_STEPS,
    max_size: int = DEFAULT_SIZE,
) -> int | bool | str:
    """Read a reduced combinator term back to a Python value.

    kind='int'  → Church numeral (count applications of the successor probe)
    kind='bool' → Church boolean (which of two probe atoms is selected)
    kind='raw'  → the point-free normal-form string (for pairs / inspection)
    """
    if kind == "int":
        return _decode_int(term, max_steps, max_size)
    if kind == "bool":
        return _decode_bool(term, max_steps, max_size)
    if kind == "raw":
        return pretty(reduce(term, max_steps=max_steps, max_size=max_size).normal_form)
    raise ValueError(f"clj_lambda.decode: unknown kind {kind!r}")


def run(
    src: str | SExpr,
    kind: str = "int",
    max_steps: int = DEFAULT_STEPS,
    max_size: int = DEFAULT_SIZE,
    prelude: dict[str, Term] | None = None,
) -> int | bool | str:
    """Compile → reduce → decode. The one-call evaluator: `run('(+ 2 3)') == 5`."""
    term = compile_clj(src, prelude)
    return decode(term, kind=kind, max_steps=max_steps, max_size=max_size)
