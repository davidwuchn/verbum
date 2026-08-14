"""Tests for the §P-SUBST-ENGINE discriminating-pair generator (subst_pairs)."""

from __future__ import annotations

from verbum.lambda_ast import (
    R_NAIVE,
    R_NORMAL,
    Status,
    alpha_eq,
    normal_form,
    parse,
    reduce,
)
from verbum.probes.subst_pairs import (
    all_pairs,
    alpha_pairs,
    capture_pairs,
    validate,
)


def test_validate_passes():
    report = validate()
    assert report["capture_probes"] > 0
    assert report["alpha_probes"] > 0
    assert report["total"] == len(all_pairs())


def test_capture_pairs_actually_discriminate():
    # every capture probe: correct_nf ≠ naive_nf, and NOT alpha-equal
    for p in capture_pairs():
        assert p.family == "capture"
        assert p.naive_nf is not None
        assert not alpha_eq(parse(p.correct_nf), parse(p.naive_nf)), p.id


def test_capture_nfs_match_reference_reducer():
    for p in capture_pairs():
        term = parse(p.term)
        assert normal_form(term, calc=R_NORMAL) == parse(p.correct_nf) or alpha_eq(
            normal_form(term, calc=R_NORMAL), parse(p.correct_nf)
        )
        assert alpha_eq(normal_form(term, calc=R_NAIVE), parse(p.naive_nf))


def test_every_capture_probe_certified_normal_form():
    for p in capture_pairs():
        term = parse(p.term)
        assert reduce(term, calc=R_NORMAL).status is Status.NORMAL_FORM
        assert reduce(term, calc=R_NAIVE).status is Status.NORMAL_FORM


def test_shadow_depth_at_least_one_for_capture():
    for p in capture_pairs():
        assert p.dials.shadow_depth >= 1


def test_alpha_pairs_are_alpha_equal_but_distinct_surfaces():
    for p in alpha_pairs():
        assert p.family == "alpha"
        assert p.naive_nf is None
        assert p.alpha_variant is not None
        assert p.term != p.alpha_variant  # renaming changed the surface
        assert alpha_eq(parse(p.term), parse(p.alpha_variant))


def test_alpha_pairs_share_normal_form():
    for p in alpha_pairs():
        a, b = parse(p.term), parse(p.alpha_variant)
        assert alpha_eq(normal_form(a), normal_form(b))


def test_dials_cover_the_cliff_axes():
    caps = capture_pairs()
    assert {p.dials.shadow_depth for p in caps} >= {1, 2, 3}
    assert max(p.dials.binder_distance for p in caps) >= 3
    # §8b order cliff dial actually varies (order-1 and order-2 both present)
    orders = {p.dials.functional_order for p in caps}
    assert 1 in orders and 2 in orders


def test_both_modes_present_per_term():
    modes = {p.mode for p in all_pairs()}
    assert modes == {"direct", "traced"}


def test_ids_are_unique():
    ids = [p.id for p in all_pairs()]
    assert len(ids) == len(set(ids))
