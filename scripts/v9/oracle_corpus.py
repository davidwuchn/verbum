"""
Oracle corpus generator for ascending arm training.

Generates 6 strata of sentences for extracting L28 basin vectors
from Qwen3-32B. Each stratum targets a specific training phase.

Strata:
  1. S-expressions    (phase 1: calibration)
  2. Simple math      (phase 2: cross-notation bridge)
  3. Simple prose     (phase 2-3: basic types)
  4. Behavioral frames (phase 3: context conditioning)
  5. Complex prose    (phase 3: composition)
  6. Mixed            (phase 4: end-to-end)

Output: JSONL to stdout, one record per line:
  {"stratum": str, "sentence": str, "group": str|null}

The "group" field links cross-notation equivalents:
  group="add_3_4" ties (+ 3 4), 3+4, and "three plus four"

Usage:
  uv run python scripts/v9/oracle_corpus.py --count 10000 > corpus.jsonl
  uv run python scripts/v9/oracle_corpus.py --pilot > pilot.jsonl

License: MIT
"""

import json
import random
import argparse
import sys
from itertools import product


# ══════════════════════════════════════════════════════════════════
# Number words
# ══════════════════════════════════════════════════════════════════

DIGIT_WORDS = {
    0: "zero", 1: "one", 2: "two", 3: "three", 4: "four",
    5: "five", 6: "six", 7: "seven", 8: "eight", 9: "nine",
    10: "ten", 11: "eleven", 12: "twelve", 13: "thirteen",
    14: "fourteen", 15: "fifteen", 16: "sixteen", 17: "seventeen",
    18: "eighteen", 19: "nineteen", 20: "twenty",
}

OP_WORDS = {
    "+": ("plus", "added to", "and"),
    "-": ("minus", "subtracted from", "less"),
    "*": ("times", "multiplied by",),
    "//": ("divided by",),
    "%": ("modulo", "mod"),
    "min": ("minimum of",),
    "max": ("maximum of",),
}

OP_SEXPR = {
    "+": "+", "-": "-", "*": "*", "//": "//", "%": "%",
    "min": "min", "max": "max",
}

COMPARE_WORDS = {
    "=": ("equals", "is equal to"),
    "<": ("is less than", "is smaller than"),
    ">": ("is greater than", "is larger than"),
}

BOOL_OPS = {
    "and": ("and",),
    "or": ("or",),
}


# ══════════════════════════════════════════════════════════════════
# Stratum 1: S-expressions
# ══════════════════════════════════════════════════════════════════

def gen_sexpr_atom(rng: random.Random) -> tuple[str, int]:
    """Generate a random integer atom. Returns (sexpr_string, value)."""
    v = rng.randint(0, 20)
    return str(v), v


def gen_sexpr(rng: random.Random, depth: int = 0, max_depth: int = 3) -> tuple[str, str]:
    """Generate a random S-expression. Returns (sexpr_string, group_label)."""
    if depth >= max_depth or (depth > 0 and rng.random() < 0.4):
        s, v = gen_sexpr_atom(rng)
        return s, f"atom_{v}"

    ops_arith = ["+", "-", "*"]
    ops_compare = ["=", "<", ">"]
    ops_bool = ["and", "or"]
    ops_unary = ["abs", "neg", "not"]
    ops_cond = ["if"]

    # Weight toward arithmetic (most common)
    op_type = rng.choices(
        ["arith", "compare", "bool", "unary", "cond"],
        weights=[50, 15, 10, 10, 15],
        k=1,
    )[0]

    if op_type == "arith":
        op = rng.choice(ops_arith)
        left, _ = gen_sexpr(rng, depth + 1, max_depth)
        right, _ = gen_sexpr(rng, depth + 1, max_depth)
        s = f"({op} {left} {right})"
        return s, f"arith_{op}"

    elif op_type == "compare":
        op = rng.choice(ops_compare)
        left, _ = gen_sexpr(rng, depth + 1, max_depth)
        right, _ = gen_sexpr(rng, depth + 1, max_depth)
        s = f"({op} {left} {right})"
        return s, f"cmp_{op}"

    elif op_type == "bool":
        op = rng.choice(ops_bool)
        left, _ = gen_sexpr(rng, depth + 1, max_depth)
        right, _ = gen_sexpr(rng, depth + 1, max_depth)
        s = f"({op} {left} {right})"
        return s, f"bool_{op}"

    elif op_type == "unary":
        op = rng.choice(ops_unary)
        arg, _ = gen_sexpr(rng, depth + 1, max_depth)
        s = f"({op} {arg})"
        return s, f"unary_{op}"

    else:  # cond
        cond, _ = gen_sexpr(rng, depth + 1, max_depth)
        then, _ = gen_sexpr(rng, depth + 1, max_depth)
        else_, _ = gen_sexpr(rng, depth + 1, max_depth)
        s = f"(if {cond} {then} {else_})"
        return s, "cond_if"


def gen_stratum_sexpr(rng: random.Random, count: int):
    """Generate S-expression sentences."""
    records = []
    for i in range(count):
        depth = rng.choices([1, 2, 3], weights=[30, 50, 20], k=1)[0]
        sexpr, group = gen_sexpr(rng, max_depth=depth)
        records.append({
            "stratum": "sexpr",
            "sentence": sexpr,
            "group": f"sexpr_{i}",
        })
    return records


# ══════════════════════════════════════════════════════════════════
# Stratum 2: Simple math (cross-notation)
# ══════════════════════════════════════════════════════════════════

def gen_stratum_math(rng: random.Random, count: int):
    """Generate cross-notation math examples: S-expr + infix + prose."""
    records = []
    ops = ["+", "-", "*"]
    per_set = count // 3  # Divide among 3 notations

    for i in range(per_set):
        op = rng.choice(ops)
        a = rng.randint(1, 20)
        b = rng.randint(1, 20)

        group = f"math_{op}_{a}_{b}"

        # S-expression
        records.append({
            "stratum": "math",
            "sentence": f"({op} {a} {b})",
            "group": group,
        })

        # Infix notation
        infix_op = {"+": "+", "-": "-", "*": "×"}[op]
        records.append({
            "stratum": "math",
            "sentence": f"{a} {infix_op} {b}",
            "group": group,
        })

        # Prose notation
        if a in DIGIT_WORDS and b in DIGIT_WORDS:
            op_word = rng.choice(OP_WORDS[op])
            records.append({
                "stratum": "math",
                "sentence": f"{DIGIT_WORDS[a]} {op_word} {DIGIT_WORDS[b]}",
                "group": group,
            })
        else:
            op_word = rng.choice(OP_WORDS[op])
            records.append({
                "stratum": "math",
                "sentence": f"{a} {op_word} {b}",
                "group": group,
            })

    # Add some nested expressions
    for i in range(count - len(records)):
        op1 = rng.choice(ops)
        op2 = rng.choice(ops)
        a, b, c = rng.randint(1, 15), rng.randint(1, 15), rng.randint(1, 15)
        group = f"math_nested_{i}"

        if rng.random() < 0.5:
            # (op1 a (op2 b c))
            records.append({
                "stratum": "math",
                "sentence": f"({op1} {a} ({op2} {b} {c}))",
                "group": group,
            })
        else:
            infix1 = {"+": "+", "-": "-", "*": "×"}[op1]
            infix2 = {"+": "+", "-": "-", "*": "×"}[op2]
            records.append({
                "stratum": "math",
                "sentence": f"{a} {infix1} {b} {infix2} {c}",
                "group": group,
            })

    return records


# ══════════════════════════════════════════════════════════════════
# Stratum 3: Simple prose
# ══════════════════════════════════════════════════════════════════

SUBJECTS = [
    "The cat", "The dog", "A bird", "The teacher", "A student",
    "The scientist", "A child", "The machine", "A program", "The system",
    "Alice", "Bob", "The researcher", "A musician", "The engineer",
    "Every cat", "Some dogs", "No student", "Each teacher", "Most birds",
]

INTRANSITIVE_VERBS = [
    "sleeps", "runs", "waits", "breathes", "thinks",
    "rests", "works", "plays", "sings", "dances",
    "grows", "moves", "falls", "rises", "stops",
]

TRANSITIVE_VERBS = [
    "sees", "finds", "builds", "reads", "writes",
    "likes", "knows", "wants", "needs", "uses",
    "creates", "follows", "catches", "holds", "breaks",
]

OBJECTS = [
    "the ball", "a book", "the table", "a solution", "the answer",
    "a number", "the result", "a pattern", "the equation", "a model",
    "the data", "a formula", "the value", "a function", "the output",
]

PREPOSITIONS = [
    "on the mat", "in the room", "near the window", "by the door",
    "under the table", "above the shelf", "behind the wall",
    "across the field", "through the forest", "along the path",
]

ADJECTIVES = [
    "big", "small", "red", "blue", "old", "new", "fast", "slow",
    "bright", "dark", "hot", "cold", "long", "short", "heavy", "light",
]


def gen_stratum_prose(rng: random.Random, count: int):
    """Generate simple prose sentences with diverse structure."""
    records = []
    templates = [
        # S V
        lambda: f"{rng.choice(SUBJECTS)} {rng.choice(INTRANSITIVE_VERBS)}.",
        # S V PP
        lambda: f"{rng.choice(SUBJECTS)} {rng.choice(INTRANSITIVE_VERBS)} {rng.choice(PREPOSITIONS)}.",
        # S V O
        lambda: f"{rng.choice(SUBJECTS)} {rng.choice(TRANSITIVE_VERBS)} {rng.choice(OBJECTS)}.",
        # S V O PP
        lambda: f"{rng.choice(SUBJECTS)} {rng.choice(TRANSITIVE_VERBS)} {rng.choice(OBJECTS)} {rng.choice(PREPOSITIONS)}.",
        # S is ADJ
        lambda: f"{rng.choice(SUBJECTS)} is {rng.choice(ADJECTIVES)}.",
        # The ADJ N V
        lambda: f"The {rng.choice(ADJECTIVES)} {rng.choice(['cat', 'dog', 'bird', 'student', 'teacher', 'system'])} {rng.choice(INTRANSITIVE_VERBS)}.",
    ]

    for i in range(count):
        template = rng.choice(templates)
        records.append({
            "stratum": "prose",
            "sentence": template(),
            "group": None,
        })

    return records


# ══════════════════════════════════════════════════════════════════
# Stratum 4: Behavioral frames
# ══════════════════════════════════════════════════════════════════

BEHAVIOR_FRAMES = [
    "Calculate {content}.",
    "Compute {content}.",
    "Summarize {content}.",
    "Analyze {content}.",
    "Verify {content}.",
    "Translate {content}.",
    "Find {content}.",
    "Compare {content}.",
    "Sort {content}.",
    "Transform {content}.",
    "Simplify {content}.",
    "Evaluate {content}.",
]

CONTENT_PHRASES = [
    "the sum of the values",
    "the difference between the numbers",
    "the product of the factors",
    "the result of the equation",
    "the total of the measurements",
    "the average of the scores",
    "the maximum of the entries",
    "the minimum of the data points",
    "the output of the function",
    "the ratio of the quantities",
    "the percentage of the sample",
    "the count of the elements",
    "the range of the dataset",
    "the median of the distribution",
    "the variance of the observations",
    "the frequency of the events",
    "the correlation between the variables",
    "the intersection of the sets",
    "the complement of the group",
    "the boundary of the region",
]


def gen_stratum_behavioral(rng: random.Random, count: int):
    """Generate same content in multiple behavioral frames."""
    records = []

    # Each content phrase × multiple frames
    per_content = count // len(CONTENT_PHRASES)

    for content in CONTENT_PHRASES:
        frames = rng.sample(BEHAVIOR_FRAMES, min(per_content, len(BEHAVIOR_FRAMES)))
        group = content.replace(" ", "_")[:40]

        for frame in frames:
            sentence = frame.format(content=content)
            records.append({
                "stratum": "behavioral",
                "sentence": sentence,
                "group": group,
            })

    # Fill remaining with random combinations
    while len(records) < count:
        content = rng.choice(CONTENT_PHRASES)
        frame = rng.choice(BEHAVIOR_FRAMES)
        records.append({
            "stratum": "behavioral",
            "sentence": frame.format(content=content),
            "group": content.replace(" ", "_")[:40],
        })

    return records[:count]


# ══════════════════════════════════════════════════════════════════
# Stratum 5: Complex prose
# ══════════════════════════════════════════════════════════════════

RELATIVE_CLAUSES = [
    "that {verb}",
    "which {verb}",
    "that {verb} {obj}",
    "which {verb} {obj}",
]

NOUNS = [
    "cat", "dog", "bird", "student", "teacher",
    "scientist", "engineer", "child", "system", "program",
    "number", "value", "function", "equation", "result",
]

QUANTIFIERS = ["every", "some", "no", "each", "most", "all", "any", "few"]


def gen_stratum_complex(rng: random.Random, count: int):
    """Generate complex prose with relative clauses and quantifiers."""
    records = []

    for i in range(count):
        pattern = rng.choices(
            ["quant_rel", "quant_simple", "nested_rel", "if_then", "conj"],
            weights=[30, 20, 15, 20, 15],
            k=1,
        )[0]

        if pattern == "quant_rel":
            # "Every cat that runs sleeps."
            q = rng.choice(QUANTIFIERS)
            n = rng.choice(NOUNS)
            v1 = rng.choice(INTRANSITIVE_VERBS)
            v2 = rng.choice(INTRANSITIVE_VERBS)
            sentence = f"{q.capitalize()} {n} that {v1} {v2}."

        elif pattern == "quant_simple":
            # "Some dogs find the answer."
            q = rng.choice(QUANTIFIERS)
            n = rng.choice(NOUNS) + "s"  # rough plural
            v = rng.choice(TRANSITIVE_VERBS)
            o = rng.choice(OBJECTS)
            sentence = f"{q.capitalize()} {n} {v} {o}."

        elif pattern == "nested_rel":
            # "The cat that sees the dog that runs sleeps."
            n1 = rng.choice(NOUNS)
            n2 = rng.choice(NOUNS)
            v1 = rng.choice(TRANSITIVE_VERBS)
            v2 = rng.choice(INTRANSITIVE_VERBS)
            v3 = rng.choice(INTRANSITIVE_VERBS)
            sentence = f"The {n1} that {v1} the {n2} that {v2} {v3}."

        elif pattern == "if_then":
            # "If the cat sleeps then the dog runs."
            n1 = rng.choice(NOUNS)
            n2 = rng.choice(NOUNS)
            v1 = rng.choice(INTRANSITIVE_VERBS)
            v2 = rng.choice(INTRANSITIVE_VERBS)
            sentence = f"If the {n1} {v1} then the {n2} {v2}."

        else:  # conj
            # "The cat runs and the dog sleeps."
            n1 = rng.choice(NOUNS)
            n2 = rng.choice(NOUNS)
            v1 = rng.choice(INTRANSITIVE_VERBS)
            v2 = rng.choice(INTRANSITIVE_VERBS)
            conj = rng.choice(["and", "or", "but"])
            sentence = f"The {n1} {v1} {conj} the {n2} {v2}."

        records.append({
            "stratum": "complex",
            "sentence": sentence,
            "group": None,
        })

    return records


# ══════════════════════════════════════════════════════════════════
# Stratum 6: Mixed (prose with computation)
# ══════════════════════════════════════════════════════════════════

MIXED_TEMPLATES = [
    "The sum of {a} and {b} is {r}.",
    "If you add {a} to {b} you get {r}.",
    "{a} plus {b} equals {r}.",
    "The product of {a} and {b} is {r}.",
    "{a} times {b} equals {r}.",
    "The difference between {a} and {b} is {r}.",
    "{a} minus {b} equals {r}.",
    "Compute {a} + {b} to get {r}.",
    "Calculate ({a} × {b}) which gives {r}.",
    "The result of adding {a} and {b} is {r}.",
    "When we subtract {b} from {a} we get {r}.",
    "Multiply {a} by {b} to obtain {r}.",
    "Dividing {a} by {b} gives approximately {r}.",
    "The value of {a} + {b} is {r}.",
    "Note that {a} × {b} = {r}.",
]


def gen_stratum_mixed(rng: random.Random, count: int):
    """Generate prose with embedded computation."""
    records = []

    for i in range(count):
        template = rng.choice(MIXED_TEMPLATES)
        a = rng.randint(1, 20)
        b = rng.randint(1, 20)

        # Pick operation based on template keywords
        if "product" in template or "times" in template or "×" in template or "ultiply" in template:
            r = a * b
            op = "mul"
        elif "difference" in template or "minus" in template or "subtract" in template:
            r = a - b
            op = "sub"
        elif "ivid" in template:
            # Avoid division by zero, ensure clean division
            b = max(1, b)
            r = a // b
            op = "div"
        else:
            r = a + b
            op = "add"

        # Use word numbers sometimes
        if rng.random() < 0.3 and a in DIGIT_WORDS and b in DIGIT_WORDS:
            sentence = template.format(a=DIGIT_WORDS[a], b=DIGIT_WORDS[b], r=r)
        else:
            sentence = template.format(a=a, b=b, r=r)

        records.append({
            "stratum": "mixed",
            "sentence": sentence,
            "group": f"mixed_{op}_{a}_{b}",
        })

    return records


# ══════════════════════════════════════════════════════════════════
# Main
# ══════════════════════════════════════════════════════════════════

STRATA_FULL = {
    "sexpr": 10000,
    "math": 10000,
    "prose": 20000,
    "behavioral": 20000,
    "complex": 10000,
    "mixed": 10000,
}

STRATA_PILOT = {
    "sexpr": 100,
    "math": 100,
    "prose": 100,
    "behavioral": 100,
    "complex": 50,
    "mixed": 50,
}

GENERATORS = {
    "sexpr": gen_stratum_sexpr,
    "math": gen_stratum_math,
    "prose": gen_stratum_prose,
    "behavioral": gen_stratum_behavioral,
    "complex": gen_stratum_complex,
    "mixed": gen_stratum_mixed,
}


def main():
    parser = argparse.ArgumentParser(description="Generate oracle training corpus")
    parser.add_argument("--pilot", action="store_true",
                        help="Generate small pilot corpus (500 sentences)")
    parser.add_argument("--count", type=int, default=None,
                        help="Override total count (distributed proportionally)")
    parser.add_argument("--seed", type=int, default=42,
                        help="Random seed")
    parser.add_argument("--stratum", type=str, default=None,
                        help="Generate only this stratum")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    if args.pilot:
        strata = STRATA_PILOT
    elif args.count:
        # Scale proportionally
        total_full = sum(STRATA_FULL.values())
        strata = {k: max(1, int(v * args.count / total_full))
                  for k, v in STRATA_FULL.items()}
    else:
        strata = STRATA_FULL

    if args.stratum:
        strata = {args.stratum: strata[args.stratum]}

    total = sum(strata.values())
    print(f"Generating {total} sentences across {len(strata)} strata",
          file=sys.stderr)

    all_records = []
    for stratum_name, count in strata.items():
        gen = GENERATORS[stratum_name]
        records = gen(rng, count)
        all_records.extend(records)
        print(f"  {stratum_name}: {len(records)} sentences", file=sys.stderr)

    # Shuffle to interleave strata
    rng.shuffle(all_records)

    # Output as JSONL
    for record in all_records:
        print(json.dumps(record))

    print(f"Total: {len(all_records)} sentences written to stdout", file=sys.stderr)


if __name__ == "__main__":
    main()
