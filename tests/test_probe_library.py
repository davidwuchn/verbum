"""Tests for the unified probe library.

Verifies:
  1. Total probe count after deduplication
  2. Each crystal combinator (KIBC + DWYS + WHNF) has ≥50 probes
  3. No empty prompts or None combinators on combinator-tagged probes
  4. by_combinator / by_category / by_source return correct subsets
  5. Deduplication works (no duplicate prompts)
  6. Source completeness (all 6 sources represented)
"""

import pytest

from verbum.probes.library import (
    Probe,
    all_probes,
    by_category,
    by_combinator,
    by_source,
    combinator_counts,
    crystal_probes,
)


# ══════════════════════════════════════════════════════════════════════════════
# Fixtures
# ══════════════════════════════════════════════════════════════════════════════


@pytest.fixture(scope="module")
def probes() -> tuple[Probe, ...]:
    """Load all probes once for the test module."""
    return all_probes()


# ══════════════════════════════════════════════════════════════════════════════
# Count and coverage tests
# ══════════════════════════════════════════════════════════════════════════════


def test_total_count_reasonable(probes):
    """Total should be ~900 (841 raw from 5 sources + supplements - ~10 dupes)."""
    assert len(probes) >= 800, f"Expected ≥800 probes, got {len(probes)}"
    assert len(probes) <= 1200, f"Unexpectedly many probes: {len(probes)}"


def test_crystal_probes_subset(probes):
    """Crystal probes should be a strict subset of all probes."""
    cp = crystal_probes()
    all_ids = {p.id for p in probes}
    for p in cp:
        assert p.id in all_ids, f"Crystal probe {p.id} not in all_probes()"
    assert len(cp) < len(probes), "Crystal probes should be a subset"


CRYSTAL_COMBINATORS = ["K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"]


@pytest.mark.parametrize("combinator", CRYSTAL_COMBINATORS)
def test_crystal_combinator_coverage(combinator):
    """Each crystal combinator must have ≥50 probes."""
    probes = by_combinator(combinator)
    assert len(probes) >= 50, (
        f"Combinator {combinator} has only {len(probes)} probes (need ≥50)"
    )


# ══════════════════════════════════════════════════════════════════════════════
# Data quality tests
# ══════════════════════════════════════════════════════════════════════════════


def test_no_empty_prompts(probes):
    """No probe should have an empty or whitespace-only prompt."""
    empties = [p for p in probes if not p.prompt.strip()]
    assert len(empties) == 0, f"Found {len(empties)} empty prompts: {empties[:5]}"


def test_no_duplicate_prompts(probes):
    """After deduplication, no two probes should share the same prompt text."""
    seen = {}
    dupes = []
    for p in probes:
        if p.prompt in seen:
            dupes.append((p.id, seen[p.prompt], p.prompt[:60]))
        else:
            seen[p.prompt] = p.id
    assert len(dupes) == 0, f"Found {len(dupes)} duplicate prompts: {dupes[:5]}"


def test_combinator_tagged_probes_have_valid_combinator(probes):
    """Probes with a combinator field should have a non-empty string."""
    for p in probes:
        if p.combinator is not None:
            assert isinstance(p.combinator, str), f"Probe {p.id} combinator is not str"
            assert len(p.combinator) > 0, f"Probe {p.id} has empty combinator string"


def test_all_probes_have_source(probes):
    """Every probe should have a non-empty source."""
    for p in probes:
        assert p.source, f"Probe {p.id} has no source"


def test_all_probes_have_id(probes):
    """Every probe should have a unique non-empty id."""
    ids = [p.id for p in probes]
    assert all(ids), "Some probes have empty ids"
    # Note: ids may not be unique across sources (different prefix ensures uniqueness)


# ══════════════════════════════════════════════════════════════════════════════
# Accessor tests
# ══════════════════════════════════════════════════════════════════════════════


def test_by_combinator_returns_correct_subset():
    """by_combinator('K') should return only K probes."""
    k_probes = by_combinator("K")
    assert all(p.combinator == "K" for p in k_probes)
    assert len(k_probes) > 0


def test_by_combinator_nonexistent():
    """by_combinator for a fake combinator should return empty."""
    result = by_combinator("DOES_NOT_EXIST")
    assert result == []


def test_by_source_returns_correct_subset():
    """by_source should filter correctly."""
    lk = by_source("lambda_kernel")
    assert all(p.source == "lambda_kernel" for p in lk)
    assert len(lk) == 380  # lambda_kernel has exactly 380 probes


def test_by_category_returns_correct_subset():
    """by_category should filter correctly."""
    cat_probes = by_category("lambda_K_select")
    assert all(p.category == "lambda_K_select" for p in cat_probes)
    assert len(cat_probes) == 25  # exactly 25 K_SELECT probes


def test_combinator_counts_complete():
    """combinator_counts should include all non-None combinators."""
    cc = combinator_counts()
    assert isinstance(cc, dict)
    # At minimum, all crystal combinators should be present
    for c in CRYSTAL_COMBINATORS:
        assert c in cc, f"Combinator {c} missing from combinator_counts()"


# ══════════════════════════════════════════════════════════════════════════════
# Source completeness
# ══════════════════════════════════════════════════════════════════════════════


EXPECTED_SOURCES = [
    "lambda_kernel",
    "basin",
    "reduction_chain",
    "fixedpoint",
    "probe_combinators",
    "supplement",
]


@pytest.mark.parametrize("source", EXPECTED_SOURCES)
def test_source_represented(source):
    """Each source should contribute probes."""
    probes = by_source(source)
    assert len(probes) > 0, f"Source '{source}' has no probes"


def test_source_counts():
    """Verify rough source counts haven't drifted wildly."""
    counts = {src: len(by_source(src)) for src in EXPECTED_SOURCES}
    assert counts["lambda_kernel"] == 380
    assert counts["basin"] >= 130  # some may be deduped
    assert counts["reduction_chain"] >= 70
    assert counts["fixedpoint"] >= 170
    assert counts["probe_combinators"] >= 50
    assert counts["supplement"] >= 50


# ══════════════════════════════════════════════════════════════════════════════
# Probe frozen dataclass
# ══════════════════════════════════════════════════════════════════════════════


def test_probe_is_frozen():
    """Probe should be an immutable frozen dataclass."""
    p = Probe(
        id="test_001",
        prompt="test prompt",
        combinator="K",
        source="test",
        category="test_cat",
        tags=("a", "b"),
    )
    with pytest.raises(AttributeError):
        p.prompt = "modified"  # type: ignore[misc]
