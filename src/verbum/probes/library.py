"""Unified Probe Library — single importable module for all Verbum probes.

Consolidates 5 scattered probe sources into one normalized collection:

    Source                          Raw count   Combinator coverage
    ─────────────────────────────── ─────────── ────────────────────
    probes/lambda_kernel_probes.py  380         K I B C M W T Φ D SCOPE SUBST WHNF Y QUOTE
    lattice/basin_probes.json       144         K I B C S D W Y WHNF (pure anchors + diverse axes)
    lattice/reduction_chain.json    79          K I B C S D W Y WHNF (redex/natural/code/formal/chain)
    lattice/fixedpoint_probes.json  184         K I B C S D W Y WHNF (pure/prose/natural/compound/...)
    scripts/explore/probe_comb.py   54          K I B C (active/control paired)
    ─────────────────────────────── ─────────── ────────────────────
    Total raw:                      841
    After dedup:                    ~778

Unified Probe model:

    @dataclass
    Probe:
        id:         str          — stable "{source}_{index:04d}" identifier
        prompt:     str          — the probe text
        combinator: str | None   — K, I, B, C, S, D, W, Y, WHNF, M, T, PHI, QUOTE, SCOPE, SUBST, meta, or None
        source:     str          — lambda_kernel | basin | reduction_chain | fixedpoint | probe_combinators
        category:   str          — free-form category tag
        tags:       list[str]    — additional metadata tags (stage, tier, axis, etc.)

Accessors:

    all_probes()             → list[Probe]   — all deduplicated probes
    by_combinator(name)      → list[Probe]   — filter by combinator
    by_category(name)        → list[Probe]   — filter by category
    by_source(name)          → list[Probe]   — filter by source
    combinator_counts()      → dict[str,int] — combinator → count
    crystal_probes()         → list[Probe]   — KIBC+DWYS+WHNF only (crystal measurement set)

Usage:

    from verbum.probes.library import all_probes, by_combinator, combinator_counts

    probes = all_probes()
    k_probes = by_combinator("K")
    print(combinator_counts())

License: MIT
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path

__all__ = [
    "Probe",
    "all_probes",
    "by_combinator",
    "by_category",
    "by_source",
    "combinator_counts",
    "crystal_probes",
    "print_stats",
]

# ══════════════════════════════════════════════════════════════════════════════
# Data model
# ══════════════════════════════════════════════════════════════════════════════


@dataclass(frozen=True, slots=True)
class Probe:
    """A single normalized probe."""

    id: str
    prompt: str
    combinator: str | None  # None for non-combinator probes (narrative, arithmetic, etc.)
    source: str
    category: str
    tags: tuple[str, ...] = ()


# ══════════════════════════════════════════════════════════════════════════════
# Path resolution
# ══════════════════════════════════════════════════════════════════════════════

def _project_root() -> Path:
    """Walk up from this file to find the project root (contains pyproject.toml)."""
    p = Path(__file__).resolve()
    for parent in [p] + list(p.parents):
        if (parent / "pyproject.toml").exists():
            return parent
    raise RuntimeError("Cannot find project root (no pyproject.toml found)")


# ══════════════════════════════════════════════════════════════════════════════
# Source ingestors
# ══════════════════════════════════════════════════════════════════════════════

# Map from axis-name prefix in lambda_kernel_probes → combinator
_LK_COMBINATOR_MAP = {
    "lambda_K": "K",
    "lambda_I": "I",
    "lambda_B": "B",
    "lambda_C": "C",
    "lambda_M": "M",
    "lambda_W": "W",
    "lambda_T": "T",
    "lambda_PHI": "PHI",
    "lambda_D": "D",
    "lambda_SCOPE": "SCOPE",
    "lambda_SUBST": "SUBST",
    "lambda_WHNF": "WHNF",
    "lambda_Y": "Y",
    "lambda_QUOTE": "QUOTE",
}

# Map tier from axis name
_LK_TIER_MAP = {
    "K": "tier1", "I": "tier1", "B": "tier1", "C": "tier1", "M": "tier1",
    "W": "tier2", "T": "tier2", "PHI": "tier2", "D": "tier2",
    "SCOPE": "tier3", "SUBST": "tier3", "WHNF": "tier3",
    "Y": "tier4", "QUOTE": "tier4",
}


def _ingest_lambda_kernel(root: Path) -> list[Probe]:
    """Ingest probes/lambda_kernel_probes.py → LAMBDA_PROBES dict."""
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "lambda_kernel_probes",
        root / "probes" / "lambda_kernel_probes.py",
    )
    mod = importlib.util.module_from_spec(spec)  # type: ignore[arg-type]
    spec.loader.exec_module(mod)  # type: ignore[union-attr]

    probes: list[Probe] = []
    idx = 0
    for axis_name, prompt_list in mod.LAMBDA_PROBES.items():
        # Determine combinator
        combinator: str | None = None
        tier = "contrast"
        if axis_name.startswith("lambda_"):
            for prefix, comb in _LK_COMBINATOR_MAP.items():
                if axis_name.startswith(prefix):
                    combinator = comb
                    tier = _LK_TIER_MAP.get(comb, "")
                    break
        elif axis_name.startswith("contrast_"):
            # Contrast probes — combinator is ambiguous, tag both
            parts = axis_name.replace("contrast_", "").split("_vs_")
            combinator = None  # intentionally None for contrast probes
            tier = "contrast"

        category = axis_name
        tags = [tier, f"axis:{axis_name}"]

        for prompt in prompt_list:
            probes.append(Probe(
                id=f"lk_{idx:04d}",
                prompt=prompt.strip(),
                combinator=combinator,
                source="lambda_kernel",
                category=category,
                tags=tuple(tags),
            ))
            idx += 1

    return probes


def _ingest_basin(root: Path) -> list[Probe]:
    """Ingest lattice/basin_probes.json."""
    path = root / "lattice" / "basin_probes.json"
    data = json.loads(path.read_text("utf-8"))

    # Map basin axes to combinators where applicable
    _BASIN_AXIS_TO_COMBINATOR = {
        "pure/K": "K", "pure/I": "I", "pure/B": "B", "pure/C": "C",
        "pure/S": "S", "pure/D": "D", "pure/W": "W", "pure/Y": "Y",
        "pure/WHNF": "WHNF", "pure/M": "M",
    }
    # Lambda axes map to operations
    _BASIN_LAMBDA_MAP = {
        "lambda/reduce_simple": "I",
        "lambda/reduce_nested": "B",
        "lambda/K_apply": "K",
        "lambda/B_compose": "B",
        "lambda/C_flip": "C",
        "lambda/S_distribute": "S",
        "lambda/beta_rule": None,
        "lambda/closed_term": None,
        "lambda/alpha_equiv": None,
        "lambda/eval_order": None,
        "lambda/church_numeral": None,
        "lambda/fixedpoint": "Y",
        "lambda/capture_avoid": None,
        "lambda/eta_reduce": None,
        "lambda/debruijn": None,
    }

    probes: list[Probe] = []
    for idx, entry in enumerate(data):
        axis = entry.get("axis", "unknown")
        note = entry.get("note", "")

        combinator = _BASIN_AXIS_TO_COMBINATOR.get(axis)
        if combinator is None:
            combinator = _BASIN_LAMBDA_MAP.get(axis)

        top_axis = axis.split("/")[0]
        category = f"basin_{top_axis}"

        tags = [f"axis:{axis}"]
        if note:
            tags.append(f"note:{note}")

        probes.append(Probe(
            id=f"bp_{idx:04d}",
            prompt=entry["prompt"].strip(),
            combinator=combinator,
            source="basin",
            category=category,
            tags=tuple(tags),
        ))

    return probes


def _ingest_reduction_chain(root: Path) -> list[Probe]:
    """Ingest lattice/reduction_chain_probes.json."""
    path = root / "lattice" / "reduction_chain_probes.json"
    data = json.loads(path.read_text("utf-8"))

    probes: list[Probe] = []
    for idx, entry in enumerate(data):
        combinator = entry.get("combinator")
        if combinator == "meta":
            combinator = None  # meta probes aren't about a specific combinator

        stage = entry.get("stage", "unknown")
        axis = entry.get("axis", "unknown")
        note = entry.get("note", "")

        category = f"reduction_{stage}"
        tags = [f"stage:{stage}", f"axis:{axis}"]
        if note:
            tags.append(f"note:{note}")

        probes.append(Probe(
            id=f"rc_{idx:04d}",
            prompt=entry["prompt"].strip(),
            combinator=combinator,
            source="reduction_chain",
            category=category,
            tags=tuple(tags),
        ))

    return probes


def _ingest_fixedpoint(root: Path) -> list[Probe]:
    """Ingest lattice/fixedpoint_probes.json."""
    path = root / "lattice" / "fixedpoint_probes.json"
    data = json.loads(path.read_text("utf-8"))

    probes: list[Probe] = []
    for idx, entry in enumerate(data):
        combinator = entry.get("combinator")
        if combinator in ("", "?"):
            combinator = None

        cat = entry.get("category", "unknown")
        domain = entry.get("domain", "")
        subdomain = entry.get("subdomain", "")

        category = f"fixedpoint_{cat}"
        tags = []
        if domain:
            tags.append(f"domain:{domain}")
        if subdomain:
            tags.append(f"subdomain:{subdomain}")
        if entry.get("fixed_lambda"):
            tags.append(f"fixed_lambda:{entry['fixed_lambda']}")

        probes.append(Probe(
            id=f"fp_{idx:04d}",
            prompt=entry["prompt"].strip(),
            combinator=combinator,
            source="fixedpoint",
            category=category,
            tags=tuple(tags),
        ))

    return probes


def _ingest_probe_combinators(root: Path) -> list[Probe]:
    """Ingest the PROBES dict and NULL_PROBES from scripts/explore/probe_combinators.py.

    Each combinator has 'active' and 'control' lists — we ingest both,
    tagging them accordingly.

    Strategy: parse the file to extract PROBES and NULL_PROBES as Python
    literals, avoiding the heavy imports (torch, transformers, etc.) that
    the script's model-loading code requires.
    """
    script_path = root / "scripts" / "explore" / "probe_combinators.py"
    source = script_path.read_text("utf-8")

    # Extract PROBES dict and NULL_PROBES list by exec'ing only the
    # data declarations. We parse the file up to the first function def
    # after the data section.
    import ast
    tree = ast.parse(source)

    # Find PROBES and NULL_PROBES assignments
    probe_data: dict | None = None
    null_data: list | None = None

    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name):
                    if target.id == "PROBES":
                        # PROBES is a dict literal — eval it safely
                        try:
                            probe_data = ast.literal_eval(node.value)
                        except (ValueError, TypeError):
                            pass
                    elif target.id == "NULL_PROBES":
                        try:
                            null_data = ast.literal_eval(node.value)
                        except (ValueError, TypeError):
                            pass

    if probe_data is None:
        # Fallback: hardcode the known structure
        probe_data = {}

    probes: list[Probe] = []
    idx = 0

    for comb_name, comb_data in probe_data.items():
        if isinstance(comb_data, dict):
            for role in ("active", "control"):
                for prompt in comb_data.get(role, []):
                    probes.append(Probe(
                        id=f"pc_{idx:04d}",
                        prompt=prompt.strip(),
                        combinator=comb_name,
                        source="probe_combinators",
                        category=f"paired_{role}",
                        tags=(f"role:{role}", f"combinator:{comb_name}"),
                    ))
                    idx += 1

    for prompt in (null_data or []):
        probes.append(Probe(
            id=f"pc_{idx:04d}",
            prompt=prompt.strip(),
            combinator=None,
            source="probe_combinators",
            category="null_baseline",
            tags=("role:null",),
        ))
        idx += 1

    return probes


# ══════════════════════════════════════════════════════════════════════════════
# Supplemental probes — fill gaps to reach ≥50 per crystal combinator
# ══════════════════════════════════════════════════════════════════════════════

# S combinator: distribute / fork-join / applicative
# S x y z = x z (y z) — apply both x and y to z, then combine
_SUPPLEMENT_S = [
    "Both the temperature and the humidity affect how comfortable the room feels to",
    "To determine the best candidate, evaluate both their experience and their references for",
    "The judge scored both the technique and the artistry before giving a total of",
    "The plant needs both sunlight and water to grow its",
    "She weighs the pros and cons of each option before deciding which is the best",
    "The formula combines the height and the width to calculate the total area of",
    "The algorithm uses both the key and the value to compute the final hash of",
    "He measured both the length and the weight to determine whether the package would fit in",
    "The recipe requires both beating the eggs and sifting the flour before mixing them into",
    "The hiring panel assesses both technical skills and cultural fit when choosing a",
    "To calculate BMI you need both the mass and the height of the",
    "The profit equals revenue minus costs, requiring both numbers to compute the",
    "The dot product multiplies corresponding elements and sums: a₁b₁ + a₂b₂ + a₃b₃ equals",
    "To evaluate f(x,g(x)) you first compute g(x) then pass both x and the result to",
    "The zip function takes two lists and pairs their elements: zip([a,b],[1,2]) gives",
    "Compare the predicted value with the actual value to compute the error for",
    "The linear combination αx + βy requires applying both scalars to their respective",
    "To test the hypothesis, collect both experimental and control measurements before",
    "The convolution operation multiplies and sums two signals element by element to produce",
    "The merge step of mergesort takes two sorted halves and interleaves them into",
    "Apply both the discount rate and the tax rate to the price to get the final",
    "The cross product of two vectors gives a vector perpendicular to both of the",
    "Check both the username and the password to authenticate the",
    "The correlation coefficient measures how two variables move together relative to their",
    "Validate both the format and the content of the input before processing the",
    "The bilinear form takes two vectors and produces a scalar by multiplying and summing",
    "The loss function compares the prediction and the label to produce a single",
    "Both the sender and the receiver must agree on the protocol before exchanging",
]

# D combinator: deep compose / double application
# D x y = x(x(y)) — apply x twice to y (or compose at depth)
_SUPPLEMENT_D = [
    "Encrypt the message and then encrypt the encrypted result for double",
    "Hash the hash of the password to produce a doubly-secure",
    "The function f(f(x)) squares the effect: if f doubles, then f(f(3)) gives",
    "Blur the image, then blur the blurred image to produce a heavily smoothed",
    "The derivative of the derivative is the second derivative which measures the",
    "The boss of the boss is the CEO who oversees the entire",
]

# WHNF: terminal / no-reduction-needed / value / fact
_SUPPLEMENT_WHNF = [
    "The value 42 requires no further computation — it is already",
    "The string 'hello' is a literal that cannot be simplified",
    "True is a boolean value that is already fully",
    "The empty list [] is a value — there is nothing to",
    "The constant π ≈ 3.14159 is a fixed mathematical",
    "The tuple (1, 2, 3) is a concrete value requiring no further",
    "The symbol :ok is an atom that evaluates to",
    "NULL represents the absence of a value and is already in its simplest",
    "The character 'A' is a primitive value that cannot be",
    "A partially applied function like (+ 3) is in weak head normal form — it awaits one more",
    "The fraction 1/3 in its lowest terms is already fully",
    "The lambda abstraction λx.x+1 is a value — it doesn't reduce until",
    "The type Int is a fully resolved type that needs no further",
    "An empty dictionary {} is an already-computed data structure that",
    "The address 0x7FFF is a concrete pointer value that does not need",
    "The result has been computed: no more steps are needed, the answer is",
    "A constructor like Just(5) is already in normal form — it wraps a value without",
    "The set {a, b, c} is enumerated and complete — no expansion",
    "The matrix [[1,0],[0,1]] is the identity matrix — a fixed mathematical",
    "A leaf node in a tree has no children to process — it is a terminal",
    "The final state in the automaton accepts the input without further",
    "An axiom is taken as given — it requires no proof or further",
    "The checksum 0xDEADBEEF is a computed digest that stands as",
    "After all reductions, the expression is in beta-normal form and cannot be reduced",
    "A quoted expression 'x is data, not code — it is not evaluated",
    "The resolved DNS entry 93.184.216.34 is the final IP — no more lookups",
    "Return 0 — the program has finished executing and produces this exit",
    "The eigenvalue λ₁ = 2.618 is a number, already computed, no matrix operations",
    "EOF marks the end of the file — there is nothing more to",
    "The hash sha256:a3b8c1... is a fixed fingerprint that does not change once",
    "A fully evaluated thunk is a value — the computation has already been",
    "The ground truth label 'cat' is a fact, not a prediction to be",
    "A closed-form solution like x = (-b ± √(b²-4ac))/2a is the final answer — plug in",
    "The Unicode codepoint U+0041 corresponds exactly to the letter A without",
    "The base case of the recursion returns 1 — no further recursive calls",
]

# Y combinator: recursion / fixed point / self-reference
_SUPPLEMENT_Y = [
    "The function calls itself with n-1 until n reaches zero and then returns the accumulated",
    "Each recursive call peels off one layer until the base case reveals the",
]


def _ingest_supplements() -> list[Probe]:
    """Generate supplemental probes to ensure ≥50 per crystal combinator."""
    probes: list[Probe] = []
    idx = 0

    for combinator, prompts in [
        ("S", _SUPPLEMENT_S),
        ("D", _SUPPLEMENT_D),
        ("WHNF", _SUPPLEMENT_WHNF),
        ("Y", _SUPPLEMENT_Y),
    ]:
        for prompt in prompts:
            probes.append(Probe(
                id=f"sup_{idx:04d}",
                prompt=prompt.strip(),
                combinator=combinator,
                source="supplement",
                category=f"supplement_{combinator}",
                tags=("supplemental",),
            ))
            idx += 1

    return probes


# ══════════════════════════════════════════════════════════════════════════════
# Deduplication
# ══════════════════════════════════════════════════════════════════════════════

def _prompt_hash(prompt: str) -> str:
    """Stable hash of a probe prompt for dedup."""
    return hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]


def _deduplicate(probes: list[Probe]) -> list[Probe]:
    """Deduplicate by prompt text. Keep the probe with richest metadata.

    'Richest' = has a combinator label > doesn't, then by source priority:
    lambda_kernel > fixedpoint > reduction_chain > basin > probe_combinators
    """
    _SOURCE_PRIORITY = {
        "lambda_kernel": 0,
        "fixedpoint": 1,
        "reduction_chain": 2,
        "basin": 3,
        "probe_combinators": 4,
    }

    seen: dict[str, Probe] = {}
    for p in probes:
        key = p.prompt
        if key not in seen:
            seen[key] = p
        else:
            existing = seen[key]
            # Prefer the one with a combinator label
            e_has = existing.combinator is not None
            p_has = p.combinator is not None
            if p_has and not e_has:
                seen[key] = p
            elif e_has == p_has:
                # Both have or both lack — prefer higher source priority (lower number)
                if _SOURCE_PRIORITY.get(p.source, 99) < _SOURCE_PRIORITY.get(existing.source, 99):
                    seen[key] = p

    return list(seen.values())


# ══════════════════════════════════════════════════════════════════════════════
# Core accessors (cached)
# ══════════════════════════════════════════════════════════════════════════════


@lru_cache(maxsize=1)
def all_probes() -> tuple[Probe, ...]:
    """Return all deduplicated probes as a frozen tuple (cached after first call)."""
    root = _project_root()

    raw: list[Probe] = []
    raw.extend(_ingest_lambda_kernel(root))
    raw.extend(_ingest_basin(root))
    raw.extend(_ingest_reduction_chain(root))
    raw.extend(_ingest_fixedpoint(root))
    raw.extend(_ingest_probe_combinators(root))
    raw.extend(_ingest_supplements())

    deduped = _deduplicate(raw)
    return tuple(deduped)


def by_combinator(name: str) -> list[Probe]:
    """Return all probes for a given combinator (e.g. 'K', 'B', 'WHNF')."""
    return [p for p in all_probes() if p.combinator == name]


def by_category(name: str) -> list[Probe]:
    """Return all probes matching a category (exact match)."""
    return [p for p in all_probes() if p.category == name]


def by_source(name: str) -> list[Probe]:
    """Return all probes from a given source."""
    return [p for p in all_probes() if p.source == name]


def combinator_counts() -> dict[str, int]:
    """Return {combinator: count} for all probes, sorted descending."""
    from collections import Counter
    counts = Counter(p.combinator for p in all_probes() if p.combinator is not None)
    return dict(sorted(counts.items(), key=lambda x: -x[1]))


# ── Crystal-specific subset ──────────────────────────────────────────────────

_CRYSTAL_COMBINATORS = frozenset({"K", "I", "B", "C", "S", "D", "W", "Y", "WHNF"})


def crystal_probes() -> list[Probe]:
    """Return only probes for the 8+1 crystal combinators (KIBC + DWYS + WHNF).

    This is the measurement set for crystal verification experiments.
    """
    return [p for p in all_probes() if p.combinator in _CRYSTAL_COMBINATORS]


# ══════════════════════════════════════════════════════════════════════════════
# Statistics
# ══════════════════════════════════════════════════════════════════════════════


def print_stats() -> None:
    """Print comprehensive probe library statistics."""
    probes = all_probes()
    print(f"\n{'='*65}")
    print(f"Verbum Unified Probe Library")
    print(f"{'='*65}")
    print(f"Total probes (deduplicated): {len(probes)}")
    print(f"Crystal probes (KIBC+DWYS+WHNF): {len(crystal_probes())}")

    # By source
    print(f"\n{'─'*40}")
    print(f"By source:")
    from collections import Counter
    source_counts = Counter(p.source for p in probes)
    for src, cnt in sorted(source_counts.items(), key=lambda x: -x[1]):
        print(f"  {src:25s} {cnt:4d}")

    # By combinator
    print(f"\n{'─'*40}")
    print(f"By combinator:")
    cc = combinator_counts()
    none_count = sum(1 for p in probes if p.combinator is None)
    for comb, cnt in cc.items():
        marker = " ◆" if comb in _CRYSTAL_COMBINATORS else ""
        print(f"  {comb:10s} {cnt:4d}{marker}")
    print(f"  {'(none)':10s} {none_count:4d}  (non-combinator probes)")

    # Crystal coverage check
    print(f"\n{'─'*40}")
    print(f"Crystal combinator coverage (target: ≥50 each):")
    for comb in sorted(_CRYSTAL_COMBINATORS):
        cnt = cc.get(comb, 0)
        status = "✅" if cnt >= 50 else "⚠️ "
        print(f"  {status} {comb:6s} {cnt:4d}")

    # By category (top 15)
    print(f"\n{'─'*40}")
    print(f"Top categories:")
    cat_counts = Counter(p.category for p in probes)
    for cat, cnt in cat_counts.most_common(20):
        print(f"  {cat:35s} {cnt:4d}")

    print(f"{'='*65}\n")


# ══════════════════════════════════════════════════════════════════════════════
# CLI entry point
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    print_stats()
