"""Tests for the typed CCG combinator reducer (lambda_ast)."""

from __future__ import annotations

from verbum.lambda_ast import (
    R_CHURCH,
    R_NAIVE,
    R_NORMAL,
    R_WEAK,
    App,
    Atom,
    Calculus,
    CAtom,
    Comb,
    Lam,
    Status,
    affine_ok,
    alpha_eq,
    fired_sequence,
    free_vars,
    naive_subst,
    normal_form,
    occurrence_profile,
    parse,
    pretty,
    reduce,
    step_fired,
    substitute,
    trace_record,
    typecheck,
    verify,
)


def nf(s: str, calc: Calculus = R_NORMAL) -> str:
    return pretty(normal_form(parse(s), calc=calc))


# --------------------------------------------------------------------------- #
# parse / pretty                                                              #
# --------------------------------------------------------------------------- #
def test_parse_roundtrip():
    for s in ["K x y", "B f g x", "S (K) (K) x", "f (g x)", "Y f"]:
        assert pretty(parse(s)) == pretty(parse(pretty(parse(s))))


def test_parse_application_is_left_assoc():
    assert parse("a b c") == App(App(Atom("a"), Atom("b")), Atom("c"))


def test_parse_combinator_vs_atom():
    assert parse("K") == Comb("K")
    assert parse("foo") == Atom("foo")


# --------------------------------------------------------------------------- #
# reduction rules                                                             #
# --------------------------------------------------------------------------- #
def test_core_rules():
    assert nf("I x") == "x"
    assert nf("K x y") == "x"
    assert nf("C f x y") == "f y x"
    assert nf("B f g x") == "f (g x)"
    assert nf("S f g x") == "f x (g x)"
    assert nf("W f x") == "f x x"
    assert nf("D f g h x") == "f (g (h x))"


def test_skk_is_identity():
    assert nf("S K K x") == "x"


def test_composite_reduction():
    # B K I x y  →  K (I x) y  →  I x  →  x
    assert nf("B K I x y") == "x"


def test_normal_form_status():
    red = reduce(parse("K a b"))
    assert red.status is Status.NORMAL_FORM
    assert pretty(red.normal_form) == "a"
    assert red.trace[0] == parse("K a b")
    assert red.trace[-1] == red.normal_form


# --------------------------------------------------------------------------- #
# limits — divergence + term growth                                          #
# --------------------------------------------------------------------------- #
def test_Y_diverges():
    red = reduce(parse("Y f"), max_steps=50)
    assert red.status is Status.DIVERGED


def test_fixpoint_loop_diverges_constant_size():
    # W W W → W W W → ... (a constant-size loop)
    red = reduce(parse("W W W"), max_steps=20)
    assert red.status is Status.DIVERGED


def test_size_exceeded_is_the_growth_limit():
    red = reduce(parse("Y x"), max_steps=10_000, max_size=24)
    assert red.status is Status.SIZE_EXCEEDED


def test_whnf_before_normal_form():
    red = reduce(parse("K a b"))
    assert red.whnf_step is not None


# --------------------------------------------------------------------------- #
# typing — the S2 check, first-class                                          #
# --------------------------------------------------------------------------- #
def test_well_typed_combinators():
    for s in ["I", "K", "B", "C", "S", "W", "D", "Y"]:
        assert typecheck(parse(s)).ok, s


def test_skk_well_typed():
    assert typecheck(parse("S K K")).ok


def test_M_is_reducible_but_not_typable():
    # operationally fine ...
    assert nf("M x") == "x x"
    # ... but self-application has no simple type (occurs-check) — the limit demo
    assert not typecheck(parse("M")).ok
    assert not typecheck(parse("M x")).ok


def test_type_mismatch_is_caught():
    # an atom forced into incompatible categories
    env = {"j": CAtom("NP"), "s": CAtom("S")}
    res = typecheck(parse("K j s"), env)
    assert res.ok  # K just drops s — fine
    # forcing an atom (NP) into function position: I j : NP, applied to j:NP -> stuck
    bad = typecheck(parse("I j j"), env)
    assert not bad.ok


def test_derivation_is_inspectable():
    res = typecheck(parse("B f g x"))
    assert res.ok
    assert res.derivation  # per-App categories recorded
    assert res.cat is not None


# --------------------------------------------------------------------------- #
# verify + oracle record                                                      #
# --------------------------------------------------------------------------- #
def test_verify():
    assert verify("K x y", "x")
    assert verify("S K K x", "x")
    assert not verify("K x y", "y")
    assert not verify("Y f", "f")  # never reaches normal form


def test_trace_record():
    rec = trace_record("K a b")
    assert rec["normal_form"] == "a"
    assert rec["status"] == "normal_form"
    assert rec["well_typed"] is True
    assert rec["trace"][0] == "K a b"
    assert rec["category"] is not None


def test_trace_record_marks_ill_typed():
    rec = trace_record("M x")
    assert rec["well_typed"] is False
    assert rec["type_error"] is not None
    assert rec["normal_form"] == "x x"  # still reduces


# --------------------------------------------------------------------------- #
# certified fired-combinator trace (step_fired / fired_sequence)              #
# --------------------------------------------------------------------------- #
def test_step_fired_reports_combinator():
    nxt, fired = step_fired(parse("B f g x"))
    assert fired == "B"
    assert pretty(nxt) == "f (g x)"


def test_step_fired_normal_form_is_none():
    nxt, fired = step_fired(parse("f (g x)"))
    assert nxt is None and fired is None


def test_fired_sequence_single():
    # K a b -> a (one K fire)
    assert fired_sequence(parse("K a b")) == ["K"]


def test_fired_sequence_multi_order():
    # B K I x y -> K (I x) y -> I x -> x : fires B, then K, then I
    assert fired_sequence(parse("B K I x y")) == ["B", "K", "I"]


def test_fired_sequence_inert_under_applied():
    # B f g : under-applied (B needs 3 args) -> normal form -> no fire
    assert fired_sequence(parse("B f g")) == []
    assert fired_sequence(parse("C f x")) == []  # C needs 3


def test_fired_sequence_matches_reduce_steps():
    for s in ["S K K x", "C f x y", "D f g h x", "W f x", "B K I x y"]:
        assert len(fired_sequence(parse(s))) == reduce(parse(s)).steps


# --------------------------------------------------------------------------- #
# binders — parse / pretty (the λ syntax)                                     #
# --------------------------------------------------------------------------- #
def test_parse_lambda_backslash_equals_glyph():
    assert parse(r"\x.x") == parse("λx.x") == Lam("x", Atom("x"))


def test_parse_multi_binder_sugars_to_nested():
    assert parse("λx y.x") == Lam("x", Lam("y", Atom("x")))


def test_lambda_body_extends_right():
    # λx.x y  ==  λx.(x y),  NOT  (λx.x) y
    assert parse("λx.x y") == Lam("x", App(Atom("x"), Atom("y")))


def test_applied_lambda_needs_parens():
    assert parse("(λx.x) y") == App(Lam("x", Atom("x")), Atom("y"))


def test_lambda_pretty_roundtrip():
    for s in ["λx.x", "(λx.λy.x) y", "λf.λx.f (f x)", "λx.x y", "f (λx.x)"]:
        assert pretty(parse(pretty(parse(s)))) == pretty(parse(s))


# --------------------------------------------------------------------------- #
# THE capture cases — capture-avoiding vs naive substitution (§2b rivals)     #
# --------------------------------------------------------------------------- #
def test_capture_avoiding_renames_the_binder():
    # (λx.λy.x) y  →  λy'.y   (the free y must NOT be captured by inner λy)
    assert nf("(λx.λy.x) y") == "λy'.y"


def test_naive_substitution_captures():
    # the deliberate bug: same term under R_NAIVE  →  λy.y
    assert nf("(λx.λy.x) y", R_NAIVE) == "λy.y"


def test_capture_and_naive_differ_here():
    # the discriminating pair: one term, two algorithms, two normal forms
    t = "(λx.λy.x) y"
    assert nf(t, R_NORMAL) != nf(t, R_NAIVE)


def test_substitute_functions_directly():
    body, val = parse("λy.x"), parse("y")
    assert pretty(substitute(body, "x", val)) == "λy'.y"  # capture-avoiding
    assert pretty(naive_subst(body, "x", val)) == "λy.y"  # captured


def test_shadowing_stops_substitution_both_algorithms():
    # inner binder shadows x — the free x below is bound, unaffected by either
    assert nf("(λx.λx.x) a") == "λx.x"
    assert nf("(λx.λx.x) a", R_NAIVE) == "λx.x"


def test_double_capture_ladder():
    # (λx.λy.λz.x) y  →  the free y dodges the inner λy binder
    red = nf("(λx.λy.λz.x) y")
    assert red == "λy'.λz.y"
    assert nf("(λx.λy.λz.x) y", R_NAIVE) == "λy.λz.y"


# --------------------------------------------------------------------------- #
# beta-reduction basics + Church encodings                                    #
# --------------------------------------------------------------------------- #
def test_identity_and_const():
    assert nf("(λx.x) a") == "a"
    assert nf("(λx.λy.x) a b") == "a"
    assert nf("(λx.λy.y) a b") == "b"


def test_church_numeral_two():
    # 2 = λf.λx.f (f x)
    assert nf("(λf.λx.f (f x)) g z") == "g (g z)"


def test_skk_as_lambda_is_identity():
    # S = λf.λg.λx.f x (g x), K = λx.λy.x
    assert nf("(λf.λg.λx.f x (g x)) (λx.λy.x) (λx.λy.x) a") == "a"


# --------------------------------------------------------------------------- #
# alpha-equivalence (the comparator)                                          #
# --------------------------------------------------------------------------- #
def test_alpha_equivalence_of_bound_renaming():
    assert alpha_eq(parse("λx.x"), parse("λz.z"))
    assert alpha_eq(parse("λx.λy.x"), parse("λa.λb.a"))


def test_alpha_distinguishes_free_variables():
    assert not alpha_eq(parse("λx.x"), parse("λx.y"))
    assert not alpha_eq(parse("λx.λy.x"), parse("λx.λy.y"))


def test_alpha_eq_ignores_combinator_only_terms():
    # no binders → structural equality, as before
    assert alpha_eq(parse("B f g x"), parse("B f g x"))
    assert not alpha_eq(parse("B f g x"), parse("B f g y"))


# --------------------------------------------------------------------------- #
# calculus switches (§9) — strong/weak ξ, eta                                 #
# --------------------------------------------------------------------------- #
def test_weak_stops_under_binder_strong_reduces():
    t = "λy.((λx.x) a)"
    assert nf(t, R_WEAK) == "λy.(λx.x) a"  # weak: no ξ, body untouched
    assert nf(t, R_NORMAL) == "λy.a"  # strong: reduce inside the binder


def test_eta_contraction_only_in_church():
    assert nf("λx.f x", R_CHURCH) == "f"  # η on
    assert nf("λx.f x", R_NORMAL) == "λx.f x"  # η off (default)


def test_eta_blocked_when_var_free_in_head():
    # λx.x x  is NOT η-contractible (x occurs free in the head)
    assert nf("λx.x x", R_CHURCH) == "λx.x x"


# --------------------------------------------------------------------------- #
# free variables + structural/graded analyses                                 #
# --------------------------------------------------------------------------- #
def test_free_vars():
    assert free_vars(parse("λx.x y")) == frozenset({"y"})
    assert free_vars(parse("λx.λy.x y z")) == frozenset({"z"})
    assert free_vars(parse("λx.x")) == frozenset()


def test_affine_check():
    assert affine_ok(parse("λx.x"))  # linear use
    assert affine_ok(parse("λx.λy.y"))  # x dropped (affine allows weakening)
    assert not affine_ok(parse("λx.x x"))  # x duplicated → not affine


def test_occurrence_profile_is_graded():
    assert occurrence_profile(parse("λx.λy.x y y")) == [("x", 1), ("y", 2)]
    assert occurrence_profile(parse("λx.x")) == [("x", 1)]


# --------------------------------------------------------------------------- #
# integration — trace / verify / fired opcodes over binders                   #
# --------------------------------------------------------------------------- #
def test_verify_over_binders_is_alpha_aware():
    assert verify("(λx.λy.x) y", "λw.y")  # alpha-equal to λy'.y
    assert not verify("(λx.λy.x) y", "λy.y")  # that is the NAIVE (wrong) answer


def test_step_fired_reports_beta_and_eta():
    _nxt, fired = step_fired(parse("(λx.x) a"))
    assert fired == "β"
    _nxt2, fired2 = step_fired(parse("λx.f x"), R_CHURCH)
    assert fired2 == "η"


def test_trace_record_handles_binders():
    rec = trace_record("(λx.x) a")
    assert rec["normal_form"] == "a"
    assert rec["status"] == "normal_form"
