"""Lambda expression generator for holographic training.

Generates operation-labeled Montague-style lambda expressions that exercise
specific combinators (K, I, B, C, M). Each expression is grounded in
concrete predicates/entities so that LLM decompilation produces natural prose.

The holographic recording protocol:
  1. Generate formal lambda expressions (this module)
  2. Decompile each to natural language prose (via LLM + decompile gate)
  3. Train V12 on paired [lambda | prose] sequences
  4. The model learns: formal structure = natural language pattern

Output is compatible with:
  - specs/lambda_montague.gbnf  (constrained Montague grammar)
  - gates/decompile.txt         (prose generation gate)
  - V12 training pipeline       (tokenized paired shards)

Usage:
    from verbum.lambda_gen import LambdaGenerator
    gen = LambdaGenerator(seed=42)
    examples = gen.generate_all(n_per_op=3000)
    for ex in examples["K"][:5]:
        print(f"[{ex.op}:{ex.complexity}] {ex.expr}")

License: MIT
"""

from __future__ import annotations

import random
from dataclasses import dataclass, field
from enum import Enum
from typing import Callable


# ══════════════════════════════════════════════════════════════════════════════
# Types
# ══════════════════════════════════════════════════════════════════════════════

class Op(str, Enum):
    """The eight kernel combinators of the lambda calculus VM."""
    K = "K"      # select / discard:      λx.λy. x
    I = "I"      # identity / binding:    λx. x
    B = "B"      # compose / chain:       λf.λg.λx. f(g(x))
    C = "C"      # flip / reorder:        λf.λx.λy. f(y)(x)
    M = "M"      # match / self-apply:    λf. f(f)
    D = "D"      # deep compose (fused):  λf.λg.λh.λx. f(g(h(x)))
    Y = "Y"      # recursion / iterate:   λf. f(Y(f))
    WHNF = "WHNF"  # terminal / stop:     weak head normal form detection


@dataclass
class Example:
    """A single generated lambda expression with its operation label."""
    op: str              # "K", "I", "B", "C", "M", "D", "Y", "WHNF"
    expr: str            # Montague-style lambda expression
    complexity: int      # 1-5 (atomic → deep nested)
    domain: str          # semantic domain (nature, education, ...)
    structure: str       # structural pattern name
    pure_form: str = ""  # combinator notation (K, B(K), C(B)(K), ...)

    def __repr__(self) -> str:
        return f"Example({self.op}:{self.complexity} [{self.domain}] {self.expr!r})"


# ══════════════════════════════════════════════════════════════════════════════
# Vocabulary — organized by semantic domain
# ══════════════════════════════════════════════════════════════════════════════

@dataclass
class Domain:
    """A semantic domain with its predicate vocabulary."""
    name: str
    entities: list[str]           # nouns (dog, student, river)
    properties: list[str]         # 1-arg adjectives (big, smart, deep)
    actions_1: list[str]          # 1-arg verbs (runs, sleeps)
    actions_2: list[str]          # 2-arg verbs (chases, teaches)
    actions_3: list[str]          # 3-arg verbs (gives, sends)
    modifiers: list[str]          # adverb-like (quickly, carefully)
    relations: list[str]          # compositional (mother_of, author_of)

DOMAINS = [
    Domain(
        name="nature",
        entities=["dog", "cat", "bird", "fish", "wolf", "bear", "deer",
                  "eagle", "rabbit", "fox", "owl", "salmon", "hawk"],
        properties=["big", "small", "fast", "wild", "young", "old",
                    "strong", "fierce", "quiet", "hungry"],
        actions_1=["runs", "sleeps", "flies", "swims", "hunts",
                   "hides", "migrates", "climbs", "dives", "howls"],
        actions_2=["chases", "eats", "fears", "follows", "protects",
                   "watches", "attacks", "avoids", "stalks", "feeds"],
        actions_3=["brings", "carries", "leads", "chases_from",
                   "lures", "drives"],
        modifiers=["quickly", "silently", "fiercely", "gracefully",
                   "cautiously", "swiftly"],
        relations=["prey_of", "predator_of", "habitat_of",
                   "offspring_of", "pack_of"],
    ),
    Domain(
        name="education",
        entities=["student", "teacher", "professor", "book", "school",
                  "lecture", "exam", "thesis", "library", "course",
                  "degree", "scholar", "class"],
        properties=["smart", "diligent", "published", "accredited",
                    "difficult", "advanced", "introductory", "gifted",
                    "enrolled", "graduated"],
        actions_1=["studies", "teaches", "reads", "writes", "learns",
                   "graduates", "publishes", "researches", "lectures",
                   "passes"],
        actions_2=["teaches", "grades", "mentors", "assigns", "tutors",
                   "examines", "advises", "evaluates", "instructs",
                   "supervises"],
        actions_3=["gives", "assigns", "awards", "recommends",
                   "submits", "presents"],
        modifiers=["carefully", "thoroughly", "brilliantly",
                   "diligently", "methodically", "rigorously"],
        relations=["author_of", "student_of", "subject_of",
                   "prerequisite_of", "syllabus_of"],
    ),
    Domain(
        name="commerce",
        entities=["buyer", "seller", "product", "price", "market",
                  "contract", "customer", "merchant", "goods", "shop",
                  "invoice", "stock", "warehouse"],
        properties=["expensive", "cheap", "available", "profitable",
                    "discounted", "imported", "wholesale", "retail",
                    "premium", "defective"],
        actions_1=["sells", "buys", "trades", "ships", "produces",
                   "advertises", "profits", "bargains", "invests",
                   "exports"],
        actions_2=["purchases", "delivers", "supplies", "orders",
                   "prices", "invoices", "stocks", "manufactures",
                   "imports", "markets"],
        actions_3=["sells", "ships", "offers", "quotes",
                   "exchanges", "returns"],
        modifiers=["profitably", "efficiently", "competitively",
                   "wholesale", "internationally", "locally"],
        relations=["supplier_of", "buyer_of", "manufacturer_of",
                   "distributor_of", "price_of"],
    ),
    Domain(
        name="law",
        entities=["judge", "lawyer", "defendant", "witness", "jury",
                  "court", "verdict", "law", "evidence", "trial",
                  "statute", "plaintiff", "case"],
        properties=["guilty", "innocent", "credible", "admissible",
                    "binding", "constitutional", "precedent",
                    "unanimous", "sworn", "convicted"],
        actions_1=["testifies", "deliberates", "appeals", "rules",
                   "convicts", "acquits", "sentences", "prosecutes",
                   "defends", "pleads"],
        actions_2=["judges", "represents", "accuses", "defends",
                   "sentences", "cross_examines", "subpoenas",
                   "overrules", "sustains", "pardons"],
        actions_3=["charges", "sentences", "awards", "presents",
                   "submits", "files"],
        modifiers=["unanimously", "lawfully", "justly",
                   "constitutionally", "impartially", "duly"],
        relations=["evidence_of", "witness_of", "counsel_for",
                   "jurisdiction_of", "precedent_of"],
    ),
    Domain(
        name="medicine",
        entities=["doctor", "patient", "nurse", "disease", "treatment",
                  "symptom", "hospital", "surgery", "diagnosis",
                  "medicine", "clinic", "vaccine", "organ"],
        properties=["healthy", "ill", "chronic", "acute", "infectious",
                    "benign", "malignant", "contagious", "sterile",
                    "critical"],
        actions_1=["heals", "recovers", "diagnoses", "operates",
                   "prescribes", "suffers", "bleeds", "rests",
                   "improves", "deteriorates"],
        actions_2=["treats", "examines", "cures", "infects",
                   "vaccinates", "monitors", "admits", "discharges",
                   "operates_on", "nurses"],
        actions_3=["prescribes", "administers", "transfers",
                   "refers", "injects", "transplants"],
        modifiers=["carefully", "urgently", "surgically",
                   "preventively", "systematically", "gently"],
        relations=["symptom_of", "cause_of", "treatment_of",
                   "side_effect_of", "diagnosis_of"],
    ),
    Domain(
        name="cooking",
        entities=["chef", "dish", "ingredient", "oven", "recipe",
                  "sauce", "spice", "meal", "kitchen", "bread",
                  "soup", "salad", "cake"],
        properties=["fresh", "cooked", "raw", "spicy", "sweet",
                    "bitter", "ripe", "frozen", "organic", "savory"],
        actions_1=["cooks", "bakes", "boils", "fries", "chops",
                   "stirs", "simmers", "roasts", "grills", "serves"],
        actions_2=["mixes", "seasons", "marinates", "garnishes",
                   "prepares", "tastes", "slices", "blends",
                   "heats", "plates"],
        actions_3=["serves", "adds", "pours", "spreads",
                   "combines", "layers"],
        modifiers=["slowly", "evenly", "gently", "thoroughly",
                   "finely", "generously"],
        relations=["ingredient_of", "recipe_for", "topping_of",
                   "base_of", "flavor_of"],
    ),
    Domain(
        name="travel",
        entities=["traveler", "destination", "flight", "hotel",
                  "passport", "luggage", "train", "city", "country",
                  "airport", "ticket", "guide", "border"],
        properties=["distant", "popular", "expensive", "scenic",
                    "crowded", "remote", "exotic", "domestic",
                    "international", "delayed"],
        actions_1=["travels", "arrives", "departs", "explores",
                   "visits", "flies", "sails", "drives", "hikes",
                   "camps"],
        actions_2=["books", "reserves", "cancels", "navigates",
                   "reaches", "photographs", "tours", "crosses",
                   "discovers", "maps"],
        actions_3=["books", "transports", "guides", "flies",
                   "sends", "ships"],
        modifiers=["frequently", "cheaply", "adventurously",
                   "comfortably", "hastily", "leisurely"],
        relations=["capital_of", "route_to", "border_of",
                   "landmark_of", "airline_of"],
    ),
    Domain(
        name="technology",
        entities=["programmer", "computer", "server", "database",
                  "network", "algorithm", "program", "user",
                  "system", "device", "application", "code", "file"],
        properties=["fast", "secure", "encrypted", "open_source",
                    "scalable", "distributed", "portable", "buggy",
                    "optimized", "deprecated"],
        actions_1=["computes", "crashes", "runs", "compiles",
                   "encrypts", "boots", "updates", "connects",
                   "processes", "stores"],
        actions_2=["programs", "debugs", "installs", "downloads",
                   "uploads", "deploys", "monitors", "hacks",
                   "configures", "tests"],
        actions_3=["sends", "transfers", "deploys", "assigns",
                   "routes", "loads"],
        modifiers=["efficiently", "securely", "recursively",
                   "concurrently", "asynchronously", "reliably"],
        relations=["developer_of", "version_of", "dependency_of",
                   "maintainer_of", "fork_of"],
    ),
    Domain(
        name="sports",
        entities=["player", "team", "coach", "referee", "game",
                  "ball", "field", "goal", "champion", "league",
                  "match", "athlete", "stadium"],
        properties=["fast", "strong", "injured", "skilled",
                    "undefeated", "veteran", "rookie", "dominant",
                    "agile", "qualified"],
        actions_1=["scores", "runs", "trains", "wins", "loses",
                   "competes", "sprints", "jumps", "swims",
                   "tackles"],
        actions_2=["defeats", "coaches", "tackles", "passes",
                   "catches", "kicks", "blocks", "drafts",
                   "trains", "challenges"],
        actions_3=["passes", "throws", "awards", "trades",
                   "assigns", "fouls"],
        modifiers=["powerfully", "skillfully", "aggressively",
                   "defensively", "strategically", "swiftly"],
        relations=["captain_of", "coach_of", "member_of",
                   "rival_of", "champion_of"],
    ),
    Domain(
        name="arts",
        entities=["artist", "painting", "musician", "song", "writer",
                  "novel", "sculptor", "gallery", "audience",
                  "composer", "poem", "film", "director"],
        properties=["famous", "abstract", "classical", "modern",
                    "original", "talented", "prolific", "obscure",
                    "acclaimed", "controversial"],
        actions_1=["paints", "sings", "writes", "performs",
                   "composes", "sculpts", "directs", "dances",
                   "acts", "exhibits"],
        actions_2=["creates", "inspires", "critiques", "performs",
                   "publishes", "illustrates", "produces",
                   "choreographs", "curates", "scores"],
        actions_3=["dedicates", "presents", "commissions",
                   "awards", "donates", "exhibits"],
        modifiers=["beautifully", "passionately", "boldly",
                   "delicately", "masterfully", "expressively"],
        relations=["creator_of", "genre_of", "inspiration_of",
                   "patron_of", "style_of"],
    ),
]


class Vocab:
    """Draws random vocabulary items from a specific domain."""

    def __init__(self, domain: Domain, rng: random.Random):
        self.d = domain
        self.rng = rng
        self._used: set[str] = set()

    def _pick(self, items: list[str], avoid_repeat: bool = True) -> str:
        if avoid_repeat:
            available = [i for i in items if i not in self._used]
            if not available:
                self._used.clear()
                available = items
            choice = self.rng.choice(available)
            self._used.add(choice)
            return choice
        return self.rng.choice(items)

    def entity(self) -> str:
        return self._pick(self.d.entities)

    def prop(self) -> str:
        return self._pick(self.d.properties)

    def act1(self) -> str:
        return self._pick(self.d.actions_1)

    def act2(self) -> str:
        return self._pick(self.d.actions_2)

    def act3(self) -> str:
        return self._pick(self.d.actions_3)

    def mod(self) -> str:
        return self._pick(self.d.modifiers)

    def rel(self) -> str:
        return self._pick(self.d.relations)

    def var(self, exclude: str = "") -> str:
        """Pick a variable from {x, y, z, u, v, w}, avoiding those in exclude."""
        pool = [v for v in "xyzuvw" if v not in exclude]
        return self.rng.choice(pool)

    def reset(self) -> None:
        self._used.clear()


# ══════════════════════════════════════════════════════════════════════════════
# Template system — structural patterns per operation
# ══════════════════════════════════════════════════════════════════════════════
#
# Each template is (name, pure_form, generator_fn).
# generator_fn(Vocab) -> str (the lambda expression)
#
# Templates are organized by complexity level within each operation.
# Complexity 1: atomic / minimal
# Complexity 2: single application with predicates
# Complexity 3: quantified / conditional
# Complexity 4: nested / multi-quantifier
# Complexity 5: deep composition / multi-operation
#

# ── K: SELECT / DISCARD ──────────────────────────────────────────────────────
# K picks one thing and throws away the other.
# Linguistic: focus, filtering, conditional branch, choosing, ignoring.

K_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # (complexity, structure_name, pure_form, generator)

    # ── Level 1: Atomic ──
    (1, "pure_K", "K",
     lambda v: "λx.λy. x"),

    (1, "pure_K_named", "K",
     lambda v: f"λx.λy. {v.act1()}(x)"),

    (1, "select_entity", "K(a)",
     lambda v: f"{v.act1()}({v.entity()})"),

    (1, "select_property", "K(P)",
     lambda v: f"{v.prop()}({v.entity()})"),

    # ── Level 2: Applied selection ──
    (2, "universal_filter", "K",
     lambda v: f"∀x. {v.entity()}(x) → {v.act1()}(x)"),

    (2, "existential_select", "K",
     lambda v: f"∃x. {v.entity()}(x) ∧ {v.prop()}(x)"),

    (2, "select_discard_explicit", "K(a)(b)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ ¬{v.act1()}(x)"
     )),

    (2, "conditional_select", "K",
     lambda v: f"{v.prop()}(x) → {v.act1()}(x)"),

    (2, "definite_select", "K(ι)",
     lambda v: f"{v.act1()}(ιx. {v.entity()}(x) ∧ {v.prop()}(x))"),

    (2, "negated_discard", "K(¬b)",
     lambda v: f"∀x. {v.entity()}(x) → ¬{v.prop()}(x)"),

    # ── Level 3: Compound selection ──
    (3, "multi_criteria_select", "K(a∧b)",
     lambda v: f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → {v.act1()}(x)"),

    (3, "select_from_pair", "K(a)(b)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"→ {v.act2()}(x, y)"
     )),

    (3, "select_unique", "K(ι,∀)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) "
         f"∧ ∀y. {v.entity()}(y) ∧ {v.prop()}(y) → {v.act2()}(x, y)"
     )),

    (3, "select_best", "K(max)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ ∀y. {v.entity()}(y) "
         f"→ {v.act2()}(x, y)"
     )),

    (3, "disjunctive_select", "K(a∨b)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.prop()}(x) ∨ {v.prop()}(x)"
     )),

    # ── Level 4: Nested selection ──
    (4, "nested_universal_select", "K(K)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∀y. {v.entity()}(y) → {v.act2()}(x, y)"
     )),

    (4, "select_within_scope", "K(∃K)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.prop()}(y) ∧ {v.act2()}(x, y)"
     )),

    (4, "select_chain", "K(K(K))",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"∀y. {v.entity()}(y) ∧ {v.prop()}(y) → {v.act2()}(x, y)"
     )),

    (4, "conditional_nested_select", "K(→K)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"({v.prop()}(x) → {v.act1()}(x)) ∧ "
         f"(¬{v.prop()}(x) → {v.act1()}(x))"
     )),

    # ── Level 5: K composed with other operations ──
    (5, "select_then_compose", "K(B(f,g))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.mod()}({v.act1()}(x))"
     )),

    (5, "select_reordered", "K(C(f))",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.act2()}(y, x) → {v.prop()}(x)"
     )),

    (5, "select_matched", "K(M(f))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"({v.prop()}(x) → {v.act1()}(x)) ∧ "
         f"({v.prop()}(x) → {v.act1()}(x))"
     )),

    (5, "deep_select", "K(K(B))",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.entity()}(y) → "
         f"∀z. {v.entity()}(z) ∧ {v.act2()}(y, z) → {v.act2()}(x, z)"
     )),
]


# ── I: IDENTITY / BINDING / REFERENCE ────────────────────────────────────────
# I passes something through unchanged. Variable binding, coreference,
# reflexive, pass-through, direct quotation.

I_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_I", "I",
     lambda v: "λx. x"),

    (1, "identity_predicate", "I(P)",
     lambda v: f"λx. {v.act1()}(x)"),

    (1, "reflexive_simple", "I(self)",
     lambda v: f"{v.act2()}(x, x)"),

    (1, "pass_through", "I",
     lambda v: f"λx. {v.prop()}(x)"),

    # ── Level 2: Binding ──
    (2, "existential_binding", "I(∃)",
     lambda v: f"∃x. {v.entity()}(x) ∧ {v.act1()}(x)"),

    (2, "universal_binding", "I(∀)",
     lambda v: f"∀x. {v.entity()}(x) → {v.act1()}(x)"),

    (2, "reflexive_binding", "I(ref)",
     lambda v: f"∃x. {v.entity()}(x) ∧ {v.act2()}(x, x)"),

    (2, "self_predication", "I(P(x,x))",
     lambda v: f"∀x. {v.entity()}(x) → {v.act2()}(x, x)"),

    (2, "identity_equation", "I(=)",
     lambda v: (
         f"∃x. ∃y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.act2()}(x, y) ∧ {v.act2()}(y, x)"
     )),

    (2, "bound_definite", "I(ι)",
     lambda v: f"∃x. {v.entity()}(x) ∧ {v.act2()}(x, ιy. {v.entity()}(y))"),

    # ── Level 3: Cross-reference binding ──
    (3, "coreference_chain", "I(I)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) "
         f"∧ {v.act1()}(x) ∧ {v.act1()}(x)"
     )),

    (3, "bound_across_scope", "I(∀∃)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y) ∧ {v.act2()}(y, x)"
     )),

    (3, "reflexive_conditional", "I(→ref)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) "
         f"→ {v.act2()}(x, x)"
     )),

    (3, "identity_preservation", "I(P→P)",
     lambda v: (
         f"∀x. {v.prop()}(x) → {v.prop()}(x)"
     )),

    (3, "mutual_binding", "I(x↔y)",
     lambda v: (
         f"∀x. ∀y. {v.act2()}(x, y) → {v.act2()}(y, x)"
     )),

    # ── Level 4: Deep binding ──
    (4, "triple_coreference", "I(I(I))",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.act1()}(x) "
         f"∧ {v.prop()}(x) ∧ {v.act2()}(x, x)"
     )),

    (4, "binding_through_relation", "I(R(I))",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ "
         f"∃y. {v.rel()}(y, x) ∧ {v.act2()}(y, x) ∧ {v.act2()}(x, y)"
     )),

    (4, "long_range_binding", "I(∀→∃→I)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.entity()}(y) ∧ "
         f"{v.act2()}(x, y) ∧ {v.prop()}(y) ∧ {v.act2()}(y, x)"
     )),

    # ── Level 5: Identity composed with other operations ──
    (5, "identity_in_composition", "I(B(f,I))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.mod()}({v.act1()}(x)) ∧ {v.act1()}(x)"
     )),

    (5, "self_reference_deep", "I(M(I))",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ "
         f"∀y. {v.act2()}(x, y) → {v.act2()}(y, x) ∧ {v.act2()}(x, x)"
     )),

    (5, "binding_across_flip", "I(C(I))",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.act2()}(x, y) ∧ {v.act2()}(y, x) ∧ "
         f"{v.act2()}(x, x) ∧ {v.act2()}(y, y)"
     )),
]


# ── B: COMPOSE / CHAIN ──────────────────────────────────────────────────────
# B chains two functions: f after g. Nested application, function pipelines,
# adverb+verb, relation chains, multi-step reasoning.

B_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_B", "B",
     lambda v: "λf.λg.λx. f(g(x))"),

    (1, "modified_action", "B(mod,act)",
     lambda v: f"{v.mod()}({v.act1()}({v.entity()}))"),

    (1, "relation_chain_simple", "B(R,a)",
     lambda v: f"{v.rel()}({v.entity()})"),

    (1, "nested_property", "B(P,Q)",
     lambda v: f"{v.prop()}({v.prop()}({v.entity()}))"),

    # ── Level 2: Applied composition ──
    (2, "compose_predicate", "B(f,g)",
     lambda v: f"λx. {v.mod()}({v.act1()}(x))"),

    (2, "compose_relation", "B(R,R)",
     lambda v: f"{v.rel()}({v.rel()}({v.entity()}))"),

    (2, "compose_over_universal", "B(f,∀)",
     lambda v: f"∀x. {v.entity()}(x) → {v.mod()}({v.act1()}(x))"),

    (2, "pipeline_2", "B(f,g)(a)",
     lambda v: f"{v.act2()}({v.entity()}, {v.rel()}({v.entity()}))"),

    (2, "adverb_verb_entity", "B(adv,V)(e)",
     lambda v: f"{v.mod()}({v.act1()}(ιx. {v.entity()}(x)))"),

    (2, "compose_property_action", "B(P,V)",
     lambda v: f"∀x. {v.entity()}(x) → {v.prop()}({v.act1()}(x))"),

    # ── Level 3: Multi-step composition ──
    (3, "triple_compose", "B(B)(f,g,h)",
     lambda v: (
         f"{v.mod()}({v.mod()}({v.act1()}({v.entity()})))"
     )),

    (3, "compose_quantifiers", "B(∀,∃)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y)"
     )),

    (3, "compose_with_condition", "B(f,→)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"{v.mod()}({v.act1()}(x))"
     )),

    (3, "relation_pipeline", "B(R,B(R,a))",
     lambda v: (
         f"{v.rel()}({v.rel()}({v.rel()}({v.entity()})))"
     )),

    (3, "compose_conditional_chain", "B(→,→)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.prop()}(x) → {v.act1()}(x)"
     )),

    # ── Level 4: Deep composition ──
    (4, "quad_compose", "B(B(B))",
     lambda v: (
         f"{v.mod()}({v.mod()}({v.mod()}({v.act1()}({v.entity()}))))"
     )),

    (4, "compose_across_scopes", "B(∀∃,fg)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.entity()}(y) → "
         f"∃z. {v.entity()}(z) ∧ {v.act2()}(x, y) ∧ {v.act2()}(y, z)"
     )),

    (4, "compose_nested_relations", "B(R,B(R,B(R)))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.act2()}(x, {v.rel()}({v.rel()}({v.entity()})))"
     )),

    (4, "pipeline_with_filter", "B(K,B(f,g))",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, {v.rel()}(y))"
     )),

    # ── Level 5: Composition with other operations ──
    (5, "compose_then_select", "B(K,B)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∀y. {v.entity()}(y) → "
         f"{v.mod()}({v.act2()}(x, {v.rel()}(y)))"
     )),

    (5, "compose_then_flip", "B(C,B)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.mod()}({v.act2()}(y, {v.rel()}(x)))"
     )),

    (5, "deep_pipeline_with_match", "B(M,B(B))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.rel()}(y, x) ∧ "
         f"{v.mod()}({v.mod()}({v.act2()}(x, y)))"
     )),
]


# ── C: FLIP / REORDER ARGUMENTS ─────────────────────────────────────────────
# C swaps argument order: f(y)(x) instead of f(x)(y).
# Linguistic: passive voice, dative alternation, perspective shift,
# inverse relations, argument reordering.

C_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_C", "C",
     lambda v: "λf.λx.λy. f(y)(x)"),

    (1, "flipped_action", "C(act)",
     lambda v: f"{v.act2()}({v.entity()}, {v.entity()})"),

    (1, "inverse_relation", "C(R)",
     lambda v: (
         f"∀x. ∀y. {v.act2()}(x, y) → {v.act2()}(y, x)"
     )),

    (1, "passive_simple", "C(V,a,b)",
     lambda v: f"{v.act2()}({v.entity()}, {v.entity()})"),

    # ── Level 2: Applied flip ──
    (2, "passive_universal", "C(∀)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"→ {v.act2()}(y, x)"
     )),

    (2, "dative_alternation", "C(V3)",
     lambda v: (
         f"∃x. ∃y. ∃z. {v.act3()}(z, y, x)"
     )),

    (2, "perspective_shift", "C(perspective)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.act2()}(x, y) → {v.act2()}(y, x)"
     )),

    (2, "flipped_conditional", "C(→)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∀y. {v.act2()}(y, x) → {v.prop()}(y)"
     )),

    (2, "reverse_relation", "C(R)(a,b)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(y, x)"
     )),

    (2, "symmetric_predicate", "C(sym)",
     lambda v: (
         f"∀x. ∀y. {v.act2()}(x, y) → {v.act2()}(y, x)"
     )),

    # ── Level 3: Compound flip ──
    (3, "double_flip", "C(C)",
     lambda v: (
         f"∀x. ∀y. ∀z. {v.act3()}(x, y, z) → {v.act3()}(z, y, x)"
     )),

    (3, "flip_with_filter", "C(K,f)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"∀y. {v.entity()}(y) → {v.act2()}(y, x)"
     )),

    (3, "flip_quantifier_scope", "C(∀∃)",
     lambda v: (
         f"∃y. {v.entity()}(y) ∧ "
         f"∀x. {v.entity()}(x) → {v.act2()}(y, x)"
     )),

    (3, "flip_with_condition", "C(→,f)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.prop()}(x) → {v.act2()}(y, x)"
     )),

    (3, "inverse_with_property", "C(P,R)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.act2()}(x, y) → {v.prop()}(y) ∧ {v.act2()}(y, x)"
     )),

    # ── Level 4: Deep flip ──
    (4, "flip_nested_scope", "C(∀∃∀)",
     lambda v: (
         f"∃y. {v.entity()}(y) ∧ {v.prop()}(y) ∧ "
         f"∀x. {v.entity()}(x) → "
         f"{v.act2()}(y, x) ∧ {v.prop()}(x)"
     )),

    (4, "flip_in_pipeline", "C(B(f,g))",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.mod()}({v.act2()}(y, x))"
     )),

    (4, "triple_argument_rotate", "C(C(C))",
     lambda v: (
         f"∀x. ∀y. ∀z. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.entity()}(z) → {v.act3()}(z, x, y)"
     )),

    # ── Level 5: Flip composed with other operations ──
    (5, "flip_then_compose", "C(B)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.mod()}({v.act2()}(y, {v.rel()}(x)))"
     )),

    (5, "flip_then_select", "C(K)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.prop()}(x) → {v.act2()}(y, x) ∧ ¬{v.act2()}(x, y)"
     )),

    (5, "flip_then_match", "C(M)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.act2()}(y, x) ∧ {v.act2()}(x, y)"
     )),
]


# ── M: MATCH / SELF-APPLICATION / PATTERN ────────────────────────────────────
# M applies something to itself. Pattern matching, templates, analogy,
# self-reference, recursion, uniform application.

M_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_M", "M",
     lambda v: "λf. f(f)"),

    (1, "self_apply_entity", "M(a)",
     lambda v: f"{v.act2()}({v.entity()}, {v.entity()})"),

    (1, "same_property", "M(P)",
     lambda v: f"{v.prop()}({v.entity()}) ∧ {v.prop()}({v.entity()})"),

    (1, "template_simple", "M(template)",
     lambda v: f"∀x. {v.entity()}(x) → {v.act1()}(x)"),

    # ── Level 2: Pattern matching ──
    (2, "parallel_pattern", "M(P,P)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ "
         f"∀y. {v.entity()}(y) → {v.act1()}(y)"
     )),

    (2, "template_application", "M(T,a)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → {v.act1()}(x)"
         f" ∧ ∀y. {v.entity()}(y) ∧ {v.prop()}(y) → {v.act1()}(y)"
     )),

    (2, "analogy_simple", "M(∼)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) "
         f"∧ {v.prop()}(x) → {v.prop()}(y)"
     )),

    (2, "reflexive_pattern", "M(self)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act2()}(x, x)"
     )),

    (2, "uniform_rule", "M(∀→∀)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ {v.prop()}(x)"
     )),

    (2, "self_similarity", "M(≈)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.act2()}(x, y) ∧ {v.act2()}(y, x)"
     )),

    # ── Level 3: Compound matching ──
    (3, "pattern_with_exception", "M(P,¬P)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ "
         f"∃y. {v.entity()}(y) ∧ ¬{v.act1()}(y)"
     )),

    (3, "analogy_proportional", "M(a:b::c:d)",
     lambda v: (
         f"∀x. ∀y. {v.act2()}(x, y) → "
         f"∀u. ∀w. {v.act2()}(u, w) → "
         f"{v.prop()}(x) ∧ {v.prop()}(u)"
     )),

    (3, "recursive_pattern", "M(M)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.act2()}(x, ιy. {v.entity()}(y) ∧ {v.act2()}(y, x))"
     )),

    (3, "template_cascade", "M(T(T))",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ "
         f"∀y. {v.entity()}(y) → {v.act1()}(y) ∧ "
         f"∀z. {v.entity()}(z) → {v.act1()}(z)"
     )),

    (3, "match_transfer", "M(→transfer)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) ∧ "
         f"{v.prop()}(x) → {v.prop()}(y)"
     )),

    # ── Level 4: Deep matching ──
    (4, "nested_template", "M(M(M))",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ "
         f"∀y. {v.entity()}(y) → {v.act1()}(y) ∧ "
         f"{v.act2()}(x, y) ∧ {v.act2()}(y, x)"
     )),

    (4, "pattern_with_depth", "M(∀∃M)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y) ∧ "
         f"{v.prop()}(x) ∧ {v.prop()}(y)"
     )),

    (4, "self_referential_chain", "M(chain)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.act1()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y) ∧ {v.act2()}(y, x) "
         f"∧ {v.act1()}(y)"
     )),

    # ── Level 5: Match composed with other operations ──
    (5, "match_in_composition", "M(B(f,f))",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.mod()}({v.act1()}(x)) ∧ {v.mod()}({v.act1()}(x))"
     )),

    (5, "match_then_select", "M(K(M))",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.act2()}(x, y) ∧ {v.act2()}(y, x) → {v.prop()}(x)"
     )),

    (5, "match_then_flip", "M(C(M))",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.act2()}(x, y) ∧ {v.act2()}(y, x) "
         f"∧ {v.act2()}(x, x) ∧ {v.act2()}(y, y)"
     )),
]


# ── D: DEEP COMPOSE (FUSED) ─────────────────────────────────────────────────
# D chains THREE functions: f(g(h(x))). Fuses 3× B into one kernel call.
# Linguistic: multi-step transformation, deep pipelines, nested modification.

D_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_D", "D",
     lambda v: "λf.λg.λh.λx. f(g(h(x)))"),

    (1, "triple_mod", "D(mod,mod,act)",
     lambda v: f"{v.mod()}({v.mod()}({v.act1()}({v.entity()})))"),

    (1, "triple_relation", "D(R,R,R)",
     lambda v: f"{v.rel()}({v.rel()}({v.rel()}({v.entity()})))"),

    # ── Level 2: Applied ──
    (2, "deep_pipeline_applied", "D(f,g,h)(a)",
     lambda v: f"∀x. {v.entity()}(x) → {v.mod()}({v.mod()}({v.act1()}(x)))"),

    (2, "nested_relation_chain", "D(R,R,entity)",
     lambda v: f"{v.act2()}({v.entity()}, {v.rel()}({v.rel()}({v.entity()})))"),

    (2, "triple_conditional", "D(→,→,P)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.prop()}(x) → "
         f"{v.prop()}(x) → {v.act1()}(x)"
     )),

    (2, "deep_modification", "D(mod,mod,mod)",
     lambda v: f"λx. {v.mod()}({v.mod()}({v.mod()}(x)))"),

    # ── Level 3: Quantified ──
    (3, "deep_compose_universal", "D(∀,f,g,h)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.mod()}({v.mod()}({v.act1()}(x)))"
     )),

    (3, "deep_with_existential", "D(∃,R,R)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, {v.rel()}({v.rel()}(y)))"
     )),

    (3, "deep_filter_chain", "D(K,B,B)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"{v.mod()}({v.mod()}({v.act1()}(x)))"
     )),

    (3, "nested_scope_chain", "D(∀,∃,∀)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.entity()}(y) → "
         f"∀z. {v.entity()}(z) ∧ {v.act2()}(x, y) → {v.act2()}(y, z)"
     )),

    # ── Level 4: Deep nested ──
    (4, "quad_pipeline", "D(D)",
     lambda v: (
         f"{v.mod()}({v.mod()}({v.mod()}({v.mod()}({v.act1()}({v.entity()})))))"
     )),

    (4, "deep_with_binding", "D(I,B,B)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.rel()}(y, x) ∧ {v.mod()}({v.mod()}({v.act2()}(x, y)))"
     )),

    (4, "chained_transforms", "D(f,g,h,scope)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∀y. {v.entity()}(y) → "
         f"{v.mod()}({v.act2()}(x, {v.rel()}({v.rel()}(y))))"
     )),

    # ── Level 5: Composed with other ops ──
    (5, "deep_then_select", "D(K,B,B,B)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.mod()}({v.mod()}({v.act2()}(x, {v.rel()}(y))))"
     )),

    (5, "deep_then_flip", "D(C,B,B)",
     lambda v: (
         f"∀x. ∀y. {v.entity()}(x) ∧ {v.entity()}(y) → "
         f"{v.mod()}({v.mod()}({v.act2()}(y, {v.rel()}(x))))"
     )),
]


# ── Y: RECURSION / ITERATION ────────────────────────────────────────────────
# Y detects and handles recursive/iterative patterns. Fixed-point combinator.
# Linguistic: repetition, enumeration, counting, "for each", "until".

Y_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_Y", "Y",
     lambda v: "λf. f(Y(f))"),

    (1, "iterate_simple", "Y(act)",
     lambda v: f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ {v.act1()}(x)"),

    (1, "repeat_action", "Y(repeat)",
     lambda v: f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ {v.act1()}(x) ∧ {v.act1()}(x)"),

    # ── Level 2: Applied ──
    (2, "iterate_until", "Y(until)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.act1()}(x) ∧ (¬{v.prop()}(x) → {v.act1()}(x))"
     )),

    (2, "enumerate_set", "Y(enum)",
     lambda v: (
         f"∀x. {v.entity()}(x) → {v.act1()}(x) ∧ "
         f"∀y. {v.entity()}(y) → {v.act1()}(y)"
     )),

    (2, "recursive_relation", "Y(R)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.rel()}(y, x) ∧ {v.act2()}(x, y)"
     )),

    (2, "chain_application", "Y(chain)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"{v.act1()}(x) ∧ {v.act1()}(x)"
     )),

    # ── Level 3: Quantified ──
    (3, "recursive_descent", "Y(descent)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.rel()}(y, x) ∧ {v.act2()}(x, y) ∧ "
         f"∃z. {v.rel()}(z, y) ∧ {v.act2()}(y, z)"
     )),

    (3, "iterate_with_accumulator", "Y(acc)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.act1()}(x) ∧ {v.prop()}(x) → {v.act1()}(x) ∧ {v.prop()}(x)"
     )),

    (3, "recursive_structure", "Y(struct)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.entity()}(y) ∧ "
         f"{v.rel()}(y, x) ∧ ({v.prop()}(y) ∨ "
         f"∃z. {v.entity()}(z) ∧ {v.rel()}(z, y))"
     )),

    (3, "count_iterate", "Y(count)",
     lambda v: (
         f"∀x. ∀y. ∀z. {v.entity()}(x) ∧ {v.entity()}(y) ∧ {v.entity()}(z) → "
         f"{v.act1()}(x) ∧ {v.act1()}(y) ∧ {v.act1()}(z)"
     )),

    # ── Level 4: Deep recursive ──
    (4, "deep_recursion", "Y(Y)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.rel()}(y, x) ∧ "
         f"∃z. {v.rel()}(z, y) ∧ ∃u. {v.rel()}(u, z) ∧ "
         f"{v.act2()}(x, u)"
     )),

    (4, "recursive_with_condition", "Y(K,Y)",
     lambda v: (
         f"∀x. {v.entity()}(x) ∧ {v.prop()}(x) → "
         f"∃y. {v.entity()}(y) ∧ {v.rel()}(y, x) ∧ {v.prop()}(y) ∧ "
         f"∃z. {v.entity()}(z) ∧ {v.rel()}(z, y) ∧ {v.act2()}(x, z)"
     )),

    (4, "iterate_transform", "Y(B,Y)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"{v.mod()}({v.act1()}(x)) ∧ {v.mod()}({v.mod()}({v.act1()}(x)))"
     )),

    # ── Level 5: Composed ──
    (5, "recurse_then_select", "Y(K)",
     lambda v: (
         f"∀x. {v.entity()}(x) → ∃y. {v.rel()}(y, x) ∧ "
         f"∃z. {v.rel()}(z, y) ∧ {v.prop()}(z) ∧ "
         f"{v.act2()}(x, z) ∧ ¬{v.act2()}(x, y)"
     )),

    (5, "recurse_then_compose", "Y(B)",
     lambda v: (
         f"∀x. {v.entity()}(x) → "
         f"∃y. {v.rel()}(y, x) ∧ "
         f"{v.mod()}({v.mod()}({v.act2()}(x, y))) ∧ "
         f"∃z. {v.rel()}(z, y) ∧ {v.mod()}({v.act2()}(y, z))"
     )),
]


# ── WHNF: TERMINAL / STOP-REDUCING ──────────────────────────────────────────
# WHNF detects when an expression is fully reduced (weak head normal form).
# Linguistic: final state, completion, result, definite answer, conclusion.

WHNF_TEMPLATES: list[tuple[int, str, str, Callable[[Vocab], str]]] = [
    # ── Level 1: Atomic ──
    (1, "pure_terminal", "WHNF",
     lambda v: f"{v.act1()}({v.entity()})"),

    (1, "terminal_fact", "WHNF(fact)",
     lambda v: f"{v.prop()}({v.entity()})"),

    (1, "terminal_value", "WHNF(value)",
     lambda v: f"{v.entity()}"),

    # ── Level 2: Applied ──
    (2, "definite_result", "WHNF(ι)",
     lambda v: f"ιx. {v.entity()}(x) ∧ {v.prop()}(x)"),

    (2, "final_state", "WHNF(final)",
     lambda v: f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ {v.act1()}(x)"),

    (2, "completed_action", "WHNF(done)",
     lambda v: f"∀x. {v.entity()}(x) → {v.prop()}(x)"),

    (2, "ground_truth", "WHNF(ground)",
     lambda v: f"{v.act2()}({v.entity()}, {v.entity()})"),

    # ── Level 3: Compound terminal ──
    (3, "final_conjunction", "WHNF(∧)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"{v.act1()}(x) ∧ {v.prop()}(x)"
     )),

    (3, "definite_complex", "WHNF(ι,∧)",
     lambda v: (
         f"ιx. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y)"
     )),

    (3, "terminal_after_reduction", "WHNF(reduced)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∀y. {v.entity()}(y) → {v.act2()}(x, y)"
     )),

    (3, "unique_result", "WHNF(unique)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∀y. {v.entity()}(y) ∧ {v.prop()}(y) → {v.act2()}(y, x)"
     )),

    # ── Level 4: Deep terminal ──
    (4, "terminal_chain", "WHNF(chain)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∃y. {v.rel()}(y, x) ∧ {v.prop()}(y) ∧ "
         f"{v.act2()}(x, y)"
     )),

    (4, "fully_determined", "WHNF(det)",
     lambda v: (
         f"ιx. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∃y. {v.entity()}(y) ∧ {v.act2()}(x, y) ∧ {v.prop()}(y)"
     )),

    (4, "conclusive_state", "WHNF(conclude)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ ∀y. {v.entity()}(y) → "
         f"{v.act2()}(x, y) ∧ {v.prop()}(x) ∧ {v.prop()}(y)"
     )),

    # ── Level 5: Terminal composed ──
    (5, "terminal_after_deep", "WHNF(D)",
     lambda v: (
         f"ιx. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∃y. {v.rel()}(y, x) ∧ ∃z. {v.rel()}(z, y) ∧ "
         f"{v.act2()}(x, z) ∧ {v.prop()}(z)"
     )),

    (5, "terminal_after_recurse", "WHNF(Y)",
     lambda v: (
         f"∃x. {v.entity()}(x) ∧ {v.prop()}(x) ∧ "
         f"∃y. {v.rel()}(y, x) ∧ {v.prop()}(y) ∧ "
         f"∃z. {v.rel()}(z, y) ∧ {v.act2()}(x, z) ∧ {v.prop()}(z)"
     )),
]


# ══════════════════════════════════════════════════════════════════════════════
# Generator
# ══════════════════════════════════════════════════════════════════════════════

# Consolidated template registry
_TEMPLATES: dict[str, list[tuple[int, str, str, Callable[[Vocab], str]]]] = {
    "K": K_TEMPLATES,
    "I": I_TEMPLATES,
    "B": B_TEMPLATES,
    "C": C_TEMPLATES,
    "M": M_TEMPLATES,
    "D": D_TEMPLATES,
    "Y": Y_TEMPLATES,
    "WHNF": WHNF_TEMPLATES,
}


class LambdaGenerator:
    """Programmatic generator of operation-labeled Montague-style lambda expressions.

    Each expression exercises a specific combinator (K, I, B, C, M) at a
    controlled complexity level, grounded in concrete predicates from a
    chosen semantic domain. Output is designed for LLM decompilation into
    natural language prose.

    Usage:
        gen = LambdaGenerator(seed=42)
        examples = gen.generate_all(n_per_op=3000)
        for ex in examples["K"][:5]:
            print(f"[{ex.op}:{ex.complexity}] {ex.expr}")
    """

    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.domains = DOMAINS

    def _make_vocab(self, domain: Domain) -> Vocab:
        return Vocab(domain, self.rng)

    def generate(
        self,
        op: str,
        n: int = 100,
        complexity: int | None = None,
        domain_name: str | None = None,
        global_seen: set[str] | None = None,
    ) -> list[Example]:
        """Generate n examples for a given operation.

        Args:
            op: Operation name ("K", "I", "B", "C", "M")
            n: Number of examples to generate
            complexity: If set, restrict to this complexity level (1-5).
                       If None, sample uniformly across available levels.
            domain_name: If set, use only this domain. If None, cycle domains.
            global_seen: If provided, skip expressions already generated
                        for other operations (prevents cross-op duplicates).

        Returns:
            List of Example objects.
        """
        templates = _TEMPLATES[op]

        # Filter by complexity if specified
        if complexity is not None:
            templates = [t for t in templates if t[0] == complexity]
            if not templates:
                raise ValueError(
                    f"No templates for op={op} at complexity={complexity}"
                )

        # Filter by domain if specified
        if domain_name is not None:
            domains = [d for d in self.domains if d.name == domain_name]
            if not domains:
                raise ValueError(f"Unknown domain: {domain_name}")
        else:
            domains = self.domains

        examples: list[Example] = []
        seen_exprs: set[str] = set()
        if global_seen is not None:
            seen_exprs.update(global_seen)
        attempts = 0
        max_attempts = n * 20  # avoid infinite loop on small template sets

        while len(examples) < n and attempts < max_attempts:
            attempts += 1

            # Pick a template
            level, structure, pure_form, gen_fn = self.rng.choice(templates)

            # Pick a domain
            domain = self.rng.choice(domains)
            vocab = self._make_vocab(domain)

            # Generate the expression
            try:
                expr = gen_fn(vocab)
            except (IndexError, KeyError):
                continue

            # Deduplicate (within-op and cross-op)
            if expr in seen_exprs:
                continue
            seen_exprs.add(expr)
            if global_seen is not None:
                global_seen.add(expr)

            examples.append(Example(
                op=op,
                expr=expr,
                complexity=level,
                domain=domain.name,
                structure=structure,
                pure_form=pure_form,
            ))

        return examples

    def generate_all(
        self,
        n_per_op: int = 3000,
        complexity: int | None = None,
    ) -> dict[str, list[Example]]:
        """Generate a balanced corpus across all operations.

        Cross-operation deduplication ensures no expression appears under
        two different operation labels (which would confuse dispatch training).

        Args:
            n_per_op: Number of examples per operation.
            complexity: If set, restrict all ops to this level.

        Returns:
            Dict mapping operation name to list of Examples.
        """
        global_seen: set[str] = set()
        result = {}
        for op in ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]:
            result[op] = self.generate(
                op, n=n_per_op, complexity=complexity,
                global_seen=global_seen,
            )
        return result

    def generate_flat(
        self,
        n_per_op: int = 3000,
    ) -> list[Example]:
        """Generate a flat list of examples, shuffled, balanced across operations."""
        all_examples = []
        for op in ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]:
            all_examples.extend(self.generate(op, n=n_per_op))
        self.rng.shuffle(all_examples)
        return all_examples

    def stats(self, examples: dict[str, list[Example]] | list[Example]) -> str:
        """Print distribution statistics for generated examples."""
        if isinstance(examples, dict):
            flat = []
            for v in examples.values():
                flat.extend(v)
        else:
            flat = examples

        lines = []
        lines.append(f"Total examples: {len(flat)}")
        lines.append("")

        # By operation
        by_op: dict[str, int] = {}
        for ex in flat:
            by_op[ex.op] = by_op.get(ex.op, 0) + 1
        lines.append("By operation:")
        for op in ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]:
            lines.append(f"  {op}: {by_op.get(op, 0)}")
        lines.append("")

        # By complexity
        by_cx: dict[int, int] = {}
        for ex in flat:
            by_cx[ex.complexity] = by_cx.get(ex.complexity, 0) + 1
        lines.append("By complexity:")
        for cx in sorted(by_cx.keys()):
            lines.append(f"  Level {cx}: {by_cx[cx]}")
        lines.append("")

        # By domain
        by_dom: dict[str, int] = {}
        for ex in flat:
            by_dom[ex.domain] = by_dom.get(ex.domain, 0) + 1
        lines.append("By domain:")
        for dom in sorted(by_dom.keys()):
            lines.append(f"  {dom}: {by_dom[dom]}")
        lines.append("")

        # By operation × complexity
        by_op_cx: dict[str, dict[int, int]] = {}
        for ex in flat:
            if ex.op not in by_op_cx:
                by_op_cx[ex.op] = {}
            by_op_cx[ex.op][ex.complexity] = by_op_cx[ex.op].get(ex.complexity, 0) + 1
        lines.append("By operation × complexity:")
        header = "  Op   " + " ".join(f"  L{i}" for i in range(1, 6))
        lines.append(header)
        for op in ["K", "I", "B", "C", "M", "D", "Y", "WHNF"]:
            counts = by_op_cx.get(op, {})
            row = f"  {op:4s} " + " ".join(f"{counts.get(i, 0):4d}" for i in range(1, 6))
            lines.append(row)
        lines.append("")

        # Unique expressions
        unique = len(set(ex.expr for ex in flat))
        lines.append(f"Unique expressions: {unique} / {len(flat)} "
                     f"({unique/max(len(flat),1)*100:.1f}%)")

        return "\n".join(lines)


# ══════════════════════════════════════════════════════════════════════════════
# Self-test
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    gen = LambdaGenerator(seed=42)

    # Generate a modest corpus
    print("Generating 200 examples per operation (1000 total)...")
    examples = gen.generate_all(n_per_op=200)

    # Stats
    print()
    print(gen.stats(examples))

    # Samples per operation
    print("=" * 72)
    for op in ["K", "I", "B", "C", "M"]:
        print(f"\n── {op} samples ──")
        # Show one per complexity level
        by_cx: dict[int, list[Example]] = {}
        for ex in examples[op]:
            by_cx.setdefault(ex.complexity, []).append(ex)
        for cx in sorted(by_cx.keys()):
            ex = by_cx[cx][0]
            print(f"  L{cx} [{ex.domain:10s}] {ex.expr}")

    # Spot-check GBNF compatibility (structural)
    print("\n" + "=" * 72)
    print("GBNF structural checks:")
    valid_binders = {"λ", "∀", "∃", "ι"}
    valid_connectives = {"∧", "∨", "→"}
    valid_vars = set("xyzuvw")
    issues = 0
    for op, exs in examples.items():
        for ex in exs:
            expr = ex.expr
            # Check for forbidden characters
            for ch in ["|", "&", "?", "="]:
                if ch in expr:
                    print(f"  ⚠ {op} L{ex.complexity}: forbidden char '{ch}' in: {expr}")
                    issues += 1
    if issues == 0:
        print("  ✓ No forbidden characters found")

    # Check all operations have all complexity levels
    print("\nComplexity coverage:")
    for op in ["K", "I", "B", "C", "M"]:
        levels = sorted(set(ex.complexity for ex in examples[op]))
        missing = [i for i in range(1, 6) if i not in levels]
        if missing:
            print(f"  ⚠ {op}: missing levels {missing}")
        else:
            print(f"  ✓ {op}: levels {levels}")

    # Check domain coverage
    print("\nDomain coverage:")
    all_domains = sorted(set(ex.domain for exs in examples.values() for ex in exs))
    print(f"  {len(all_domains)} domains: {', '.join(all_domains)}")

    print(f"\n{'✓' if issues == 0 else '✗'} Self-test complete")
