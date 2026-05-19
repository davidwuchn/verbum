"""Build Fixed-Point Probes — Semantically stable compile/decompile pairs.

Each probe is at a fixed point of the compile∘decompile cycle:
  prose → compile → λ → decompile → prose' → compile → λ' → ...
  When λ == λ': fixed point reached. Both prose and lambda are stable.

Probe categories:
  1. COMBINATOR_PURE    — canonical combinator definitions (λ side)
  2. COMBINATOR_PROSE   — fixed-point prose descriptions (prose side)
  3. COMPILE            — prose that compiles to a known λ (ascending arm)
  4. DECOMPILE          — λ that decompiles to stable prose (descending arm)
  5. COMPOUND           — compound combinator expressions
  6. CROSS_DOMAIN       — natural language that IS beta reduction
  7. ROUNDTRIP_PAIR     — compile + decompile as paired probes

Format: compatible with build_lattice_map.py / diverse_corpus.json

License: MIT
"""

from __future__ import annotations

import json
from pathlib import Path


# ── Combinator definitions ───────────────────────────────────────

COMBINATORS = {
    "K": {
        "lambda": "λx.λy.x",
        "fixed_prose": "The projection function that given two arguments returns the first, discarding the second entirely",
        "natural": [
            "Despite everything else that happened, the only thing that matters is",
            "No matter what you say next, my answer remains",
            "The first ingredient is all you need; ignore the rest and use",
            "Regardless of the second option, always choose",
        ],
    },
    "I": {
        "lambda": "λx.x",
        "fixed_prose": "The identity function that returns its single argument completely unchanged",
        "natural": [
            "Simply repeat exactly what was said:",
            "The output is identical to the input:",
            "Pass through without any modification:",
            "Echo the following precisely as given:",
        ],
    },
    "B": {
        "lambda": "λf.λg.λx.f(g(x))",
        "fixed_prose": "The composition operator that given functions f and g and argument x, applies g to x first, then applies f to that result",
        "natural": [
            "First translate the document to French, then summarize the translated",
            "The mother of the author of the book that",
            "Take the square root of the sum of",
            "Convert to uppercase the reversed version of",
        ],
    },
    "C": {
        "lambda": "λf.λx.λy.f(y)(x)",
        "fixed_prose": "The argument flip operator that given a function f and arguments x and y, applies f to y first and then to x, reversing the argument order",
        "natural": [
            "Instead of me giving it to you, you give it to",
            "Not from English to French, but from French to",
            "Rather than the teacher grading the student, the student evaluates the",
            "Reverse the direction: instead of parent to child, child to",
        ],
    },
    "W": {
        "lambda": "λf.λx.f(x)(x)",
        "fixed_prose": "The duplication operator that given a function f and argument x, applies f to x twice — using x as both the first and second argument",
        "natural": [
            "Compare the document with itself to find",
            "Apply the same transformation to both sides of",
            "The function that tests whether something equals itself:",
            "Use the password as both the key and the value to",
        ],
    },
    "Y": {
        "lambda": "λf.(λx.f(x(x)))(λx.f(x(x)))",
        "fixed_prose": "The fixed-point combinator that given a function f, finds the value that equals f applied to itself — enabling recursion without self-reference",
        "natural": [
            "Keep applying the rule until the result stops changing:",
            "The process that feeds its own output back as input until stable:",
            "Repeat the simplification step until no further simplification is possible:",
            "Find the equilibrium by iterating the transformation until convergence:",
        ],
    },
    "D": {
        "lambda": "λf.λg.λx.λy.f(x)(g(y))",
        "fixed_prose": "The deep composition operator that given functions f and g and arguments x and y, applies f to x and g to y independently, then combines the results",
        "natural": [
            "Score the essay on both grammar and content separately, then combine:",
            "Evaluate the pros independently from the cons, then weigh",
            "Process the image through both the color and edge filters, then merge",
            "Apply the discount to the price and the tax to the subtotal, then sum",
        ],
    },
    "S": {
        "lambda": "λf.λg.λx.f(x)(g(x))",
        "fixed_prose": "The substitution combinator that given functions f and g and argument x, applies both f and g to x, then applies the result of f(x) to the result of g(x)",
        "natural": [
            "Use the input to determine both which function to apply and what to apply it to:",
            "The context determines both the interpretation rule and the thing being interpreted:",
            "Based on the query, select both the search strategy and the search terms:",
            "The sentence itself determines both the parsing rule and the parse:",
        ],
    },
}

# WHNF is special — it's a termination condition, not a function
WHNF = {
    "lambda": "(value in weak head normal form)",
    "fixed_prose": "A value that cannot be reduced further — it is already in its simplest computational form, either a literal value or a partially applied function awaiting more arguments",
    "natural": [
        "The final answer that cannot be simplified any further:",
        "This expression is already fully evaluated:",
        "No more computation steps are possible; the result is",
        "The irreducible form of the expression is",
    ],
}


# ── Compound combinator fixed points ─────────────────────────────

COMPOUNDS = [
    {
        "expr": "B B",
        "lambda": "λf.λg.λh.λx.f(g(h(x)))",
        "fixed_prose": "Triple composition — compose three functions into a pipeline that applies the innermost first",
        "axis": "compound_B_B",
    },
    {
        "expr": "B K",
        "lambda": "λx.λg.λy.x",
        "fixed_prose": "Constant composition — a function that ignores two arguments and returns the first thing it was given",
        "axis": "compound_B_K",
    },
    {
        "expr": "K I",
        "lambda": "λx.λy.y",
        "fixed_prose": "The projection function that given two arguments returns the second, discarding the first",
        "axis": "compound_K_I",
    },
    {
        "expr": "C K",
        "lambda": "λx.λy.y",
        "fixed_prose": "Flip projection — equivalent to selecting the second argument by flipping K's preference",
        "axis": "compound_C_K",
    },
    {
        "expr": "B C B",
        "lambda": "λf.λg.λx.λy.f(g(y))(x)",
        "fixed_prose": "Compose then flip — apply g to y first, then apply f to the result with x as second argument",
        "axis": "compound_B_C_B",
    },
    {
        "expr": "S K",
        "lambda": "λg.λx.x",
        "fixed_prose": "Substitute then project — always returns the argument regardless of the function g, equivalent to identity",
        "axis": "compound_S_K",
    },
    {
        "expr": "S I I",
        "lambda": "λx.x(x)",
        "fixed_prose": "Self-application — applies the argument to itself, the core of recursion and paradox",
        "axis": "compound_S_I_I",
    },
    {
        "expr": "B (B B) B",
        "lambda": "λf.λg.λh.λi.λx.f(g(h(i(x))))",
        "fixed_prose": "Quadruple composition — a four-function pipeline",
        "axis": "compound_quad_compose",
    },
    {
        "expr": "W B",
        "lambda": "λg.λx.g(x)(g(x))",
        "fixed_prose": "Duplicate through composition — apply g to x, then apply that result to itself",
        "axis": "compound_W_B",
    },
    {
        "expr": "C B",
        "lambda": "λg.λf.λx.f(g(x))",
        "fixed_prose": "Flipped composition — compose in reverse order, applying the second function first",
        "axis": "compound_C_B",
    },
]


# ── Compile/decompile fixed points ────────────────────────────────

COMPILE_PROBES = [
    # K-family
    {"prompt": "Write a function that takes two arguments and always returns the first one", "combinator": "K", "axis": "compile_K_basic"},
    {"prompt": "Define a constant function that ignores its second parameter", "combinator": "K", "axis": "compile_K_constant"},
    {"prompt": "Implement a selector that always picks the left of a pair", "combinator": "K", "axis": "compile_K_selector"},
    {"prompt": "Create a function where the second argument has no effect on the output", "combinator": "K", "axis": "compile_K_ignore"},

    # I-family
    {"prompt": "Write the simplest possible function — one that does nothing to its input", "combinator": "I", "axis": "compile_I_basic"},
    {"prompt": "Define the identity transformation", "combinator": "I", "axis": "compile_I_identity"},
    {"prompt": "Implement a pass-through that returns its argument unchanged", "combinator": "I", "axis": "compile_I_passthrough"},

    # B-family
    {"prompt": "Write a function that composes two other functions — applying the second then the first", "combinator": "B", "axis": "compile_B_basic"},
    {"prompt": "Define function composition: given f and g, produce a function that applies g then f", "combinator": "B", "axis": "compile_B_compose"},
    {"prompt": "Implement a pipeline builder that chains two transformations", "combinator": "B", "axis": "compile_B_pipeline"},
    {"prompt": "Create a higher-order function that given two functions returns their composition", "combinator": "B", "axis": "compile_B_higher"},

    # C-family
    {"prompt": "Write a function that swaps the order of two arguments to another function", "combinator": "C", "axis": "compile_C_basic"},
    {"prompt": "Define an argument reverser for binary functions", "combinator": "C", "axis": "compile_C_flip"},
    {"prompt": "Implement flip: given f(x,y), produce a function that computes f(y,x)", "combinator": "C", "axis": "compile_C_reverse"},

    # W-family
    {"prompt": "Write a function that passes the same argument twice to a binary function", "combinator": "W", "axis": "compile_W_basic"},
    {"prompt": "Define the diagonal: given f(x,y), produce a function that computes f(x,x)", "combinator": "W", "axis": "compile_W_diagonal"},
    {"prompt": "Implement self-application: given f, produce the function that applies f to x twice", "combinator": "W", "axis": "compile_W_selfapply"},

    # Y-family
    {"prompt": "Write a function that finds the fixed point of another function without explicit recursion", "combinator": "Y", "axis": "compile_Y_basic"},
    {"prompt": "Define a combinator that enables recursion in a language without named functions", "combinator": "Y", "axis": "compile_Y_recursion"},
    {"prompt": "Implement the mechanism by which a function can call itself without knowing its own name", "combinator": "Y", "axis": "compile_Y_anonymous"},

    # S-family
    {"prompt": "Write a function where the argument determines both the function to apply and the value to transform", "combinator": "S", "axis": "compile_S_basic"},
    {"prompt": "Define the substitution combinator: given f, g, x, compute f(x)(g(x))", "combinator": "S", "axis": "compile_S_subst"},

    # D-family
    {"prompt": "Write a function that processes two arguments independently through two different functions then combines", "combinator": "D", "axis": "compile_D_basic"},
    {"prompt": "Define parallel application: given f, g, x, y, compute f(x) combined with g(y)", "combinator": "D", "axis": "compile_D_parallel"},
]


# ── Decompile fixed points ────────────────────────────────────────

DECOMPILE_PROBES = [
    {"prompt": "Explain in plain English what this function does: λx.λy.x", "combinator": "K", "axis": "decompile_K"},
    {"prompt": "Describe the behavior of: λx.x", "combinator": "I", "axis": "decompile_I"},
    {"prompt": "What does this function compute: λf.λg.λx.f(g(x))", "combinator": "B", "axis": "decompile_B"},
    {"prompt": "Explain this lambda expression: λf.λx.λy.f(y)(x)", "combinator": "C", "axis": "decompile_C"},
    {"prompt": "Describe what this does: λf.λx.f(x)(x)", "combinator": "W", "axis": "decompile_W"},
    {"prompt": "What is the purpose of: λf.(λx.f(x(x)))(λx.f(x(x)))", "combinator": "Y", "axis": "decompile_Y"},
    {"prompt": "Explain this function: λf.λg.λx.f(x)(g(x))", "combinator": "S", "axis": "decompile_S"},
    {"prompt": "Describe the computation: λf.λg.λx.λy.f(x)(g(y))", "combinator": "D", "axis": "decompile_D"},

    # Compound decompiles
    {"prompt": "What does this compute: λf.λg.λh.λx.f(g(h(x)))", "axis": "decompile_B_B"},
    {"prompt": "Explain: λx.λy.y", "axis": "decompile_K_I"},
    {"prompt": "What does λx.x(x) do, and why is it significant?", "axis": "decompile_S_I_I"},
    {"prompt": "Describe: λf.λg.λh.λi.λx.f(g(h(i(x))))", "axis": "decompile_quad_compose"},
]


# ── Cross-domain fixed points (natural language IS beta reduction) ─

CROSS_DOMAIN = [
    # B (composition) in natural language
    {"prompt": "The capital of the country that borders", "combinator": "B", "axis": "cross_B_geography"},
    {"prompt": "The color of the car that belongs to the person who", "combinator": "B", "axis": "cross_B_chain"},
    {"prompt": "Summarize the translation of the abstract of", "combinator": "B", "axis": "cross_B_pipeline"},
    {"prompt": "The square root of the absolute value of the difference between", "combinator": "B", "axis": "cross_B_math"},
    {"prompt": "The CEO of the company that acquired the startup that developed", "combinator": "B", "axis": "cross_B_deep_chain"},
    {"prompt": "Print the sorted unique values from the filtered list of", "combinator": "B", "axis": "cross_B_code_pipeline"},

    # K (selection/projection) in natural language
    {"prompt": "No matter what happens next, the answer is still", "combinator": "K", "axis": "cross_K_constant"},
    {"prompt": "Regardless of the weather, the meeting will be held at", "combinator": "K", "axis": "cross_K_regardless"},
    {"prompt": "The only relevant factor, ignoring everything else, is", "combinator": "K", "axis": "cross_K_only"},
    {"prompt": "Whatever you do, don't forget that the main point is", "combinator": "K", "axis": "cross_K_main_point"},

    # C (flip) in natural language
    {"prompt": "It wasn't the dog that bit the man, but the man who bit the", "combinator": "C", "axis": "cross_C_reverse_agent"},
    {"prompt": "Instead of the students evaluating the teachers, the teachers evaluate the", "combinator": "C", "axis": "cross_C_role_swap"},
    {"prompt": "Don't ask what your country can do for you — ask what you can do for your", "combinator": "C", "axis": "cross_C_jfk"},
    {"prompt": "The seller became the buyer and the buyer became the", "combinator": "C", "axis": "cross_C_swap_roles"},

    # I (identity) in natural language
    {"prompt": "The message was relayed exactly as received:", "combinator": "I", "axis": "cross_I_relay"},
    {"prompt": "The witness quoted the suspect verbatim:", "combinator": "I", "axis": "cross_I_verbatim"},
    {"prompt": "Copy the input to the output without any transformation:", "combinator": "I", "axis": "cross_I_copy"},

    # W (duplication) in natural language
    {"prompt": "The committee that oversees itself discovered that", "combinator": "W", "axis": "cross_W_self_ref"},
    {"prompt": "The program that analyzes its own source code found", "combinator": "W", "axis": "cross_W_quine"},
    {"prompt": "Compare each item in the list with every other item in the same list to", "combinator": "W", "axis": "cross_W_self_compare"},

    # Y (fixed point / recursion) in natural language
    {"prompt": "The rule for simplifying is: if the expression contains a reducible part, simplify it and repeat until", "combinator": "Y", "axis": "cross_Y_simplify"},
    {"prompt": "Start with an initial guess, apply Newton's method, and keep iterating until the answer converges to", "combinator": "Y", "axis": "cross_Y_newton"},
    {"prompt": "To sort, split the list in half, sort each half, then merge — applying this same process to each half until", "combinator": "Y", "axis": "cross_Y_mergesort"},
    {"prompt": "The sentence that refers to itself is true if and only if", "combinator": "Y", "axis": "cross_Y_goedel"},

    # S (substitution) in natural language
    {"prompt": "Use the context to determine both what rule applies and what it applies to:", "combinator": "S", "axis": "cross_S_context"},
    {"prompt": "The word itself tells you both how to pronounce it and what it means:", "combinator": "S", "axis": "cross_S_self_decode"},

    # D (parallel / deep compose) in natural language
    {"prompt": "Grade the essay separately for content and for grammar, then combine the scores:", "combinator": "D", "axis": "cross_D_parallel_eval"},
    {"prompt": "Analyze the image for both color and shape independently, then classify based on", "combinator": "D", "axis": "cross_D_parallel_analysis"},
]


# ── Reduction trace probes (show the pipeline stages) ─────────────

REDUCTION_TRACES = [
    # Simple reductions
    {"prompt": "Reduce step by step: K a b", "answer": "a", "steps": 1, "axis": "reduce_K_simple"},
    {"prompt": "Reduce step by step: I (K a b)", "answer": "a", "steps": 2, "axis": "reduce_I_K"},
    {"prompt": "Reduce step by step: B f g x", "answer": "f (g x)", "steps": 1, "axis": "reduce_B_simple"},
    {"prompt": "Reduce step by step: C f a b", "answer": "f b a", "steps": 1, "axis": "reduce_C_simple"},
    {"prompt": "Reduce step by step: W f x", "answer": "f x x", "steps": 1, "axis": "reduce_W_simple"},
    {"prompt": "Reduce step by step: S f g x", "answer": "f x (g x)", "steps": 1, "axis": "reduce_S_simple"},

    # Multi-step reductions
    {"prompt": "Reduce completely: K (I a) (B f g x)", "answer": "a", "steps": 2, "axis": "reduce_K_I_nested"},
    {"prompt": "Reduce completely: B (K a) I x", "answer": "a", "steps": 2, "axis": "reduce_B_K_I"},
    {"prompt": "Reduce completely: C (B f g) a b", "answer": "f (g b) a", "steps": 2, "axis": "reduce_C_B"},
    {"prompt": "Reduce completely: S K K x", "answer": "x", "steps": 2, "axis": "reduce_S_K_K"},
    {"prompt": "Reduce completely: B B B f g h x", "answer": "f (g (h x))", "steps": 3, "axis": "reduce_B_B_B"},
    {"prompt": "Reduce completely: W (C K) x", "answer": "x", "steps": 3, "axis": "reduce_W_C_K"},

    # Deep reductions
    {"prompt": "Reduce completely: K (B f g (I x)) (W h y)", "answer": "f (g x)", "steps": 4, "axis": "reduce_deep_4"},
    {"prompt": "Reduce completely: B (B B B) B f g h i x", "answer": "f (g (h (i x)))", "steps": 4, "axis": "reduce_deep_compose"},
    {"prompt": "Reduce completely: S (B B S) (K K) f g x", "answer": "f (g x)", "steps": 5, "axis": "reduce_deep_5"},
]


# ── Assembly ─────────────────────────────────────────────────────

def build_probes() -> list[dict]:
    """Assemble all fixed-point probes into a single list."""
    probes = []

    # 1. Pure combinator fixed points (λ side)
    for name, info in COMBINATORS.items():
        probes.append({
            "prompt": f"{info['lambda']}",
            "domain": "fixedpoint",
            "subdomain": f"pure_{name}",
            "combinator": name,
            "category": "combinator_pure",
            "fixed_lambda": info["lambda"],
        })

    # WHNF
    probes.append({
        "prompt": WHNF["fixed_prose"],
        "domain": "fixedpoint",
        "subdomain": "pure_WHNF",
        "combinator": "WHNF",
        "category": "combinator_pure",
        "fixed_lambda": WHNF["lambda"],
    })

    # 2. Fixed-point prose descriptions
    for name, info in COMBINATORS.items():
        probes.append({
            "prompt": info["fixed_prose"],
            "domain": "fixedpoint",
            "subdomain": f"prose_{name}",
            "combinator": name,
            "category": "combinator_prose",
            "fixed_lambda": info["lambda"],
        })

    probes.append({
        "prompt": WHNF["fixed_prose"],
        "domain": "fixedpoint",
        "subdomain": "prose_WHNF",
        "combinator": "WHNF",
        "category": "combinator_prose",
    })

    # 3. Natural language probes per combinator
    for name, info in COMBINATORS.items():
        for i, nat in enumerate(info["natural"]):
            probes.append({
                "prompt": nat,
                "domain": "fixedpoint",
                "subdomain": f"natural_{name}_{i}",
                "combinator": name,
                "category": "natural_language",
                "fixed_lambda": info["lambda"],
            })

    for i, nat in enumerate(WHNF["natural"]):
        probes.append({
            "prompt": nat,
            "domain": "fixedpoint",
            "subdomain": f"natural_WHNF_{i}",
            "combinator": "WHNF",
            "category": "natural_language",
        })

    # 4. Compound combinator fixed points
    for comp in COMPOUNDS:
        probes.append({
            "prompt": comp["fixed_prose"],
            "domain": "fixedpoint",
            "subdomain": comp["axis"],
            "category": "compound",
            "fixed_lambda": comp["lambda"],
            "expression": comp["expr"],
        })

    # 5. Compile probes (ascending arm)
    for cp in COMPILE_PROBES:
        probes.append({
            "prompt": cp["prompt"],
            "domain": "fixedpoint",
            "subdomain": cp["axis"],
            "combinator": cp.get("combinator", ""),
            "category": "compile",
        })

    # 6. Decompile probes (descending arm)
    for dp in DECOMPILE_PROBES:
        probes.append({
            "prompt": dp["prompt"],
            "domain": "fixedpoint",
            "subdomain": dp["axis"],
            "combinator": dp.get("combinator", ""),
            "category": "decompile",
        })

    # 7. Cross-domain probes
    for cd in CROSS_DOMAIN:
        probes.append({
            "prompt": cd["prompt"],
            "domain": "fixedpoint",
            "subdomain": cd["axis"],
            "combinator": cd["combinator"],
            "category": "cross_domain",
        })

    # 8. Reduction trace probes
    for rt in REDUCTION_TRACES:
        probes.append({
            "prompt": rt["prompt"],
            "domain": "fixedpoint",
            "subdomain": rt["axis"],
            "category": "reduction",
            "answer": rt["answer"],
            "reduction_steps": rt["steps"],
        })

    return probes


def main():
    probes = build_probes()

    # Summary
    categories = {}
    combinators = {}
    for p in probes:
        cat = p.get("category", "unknown")
        categories[cat] = categories.get(cat, 0) + 1
        comb = p.get("combinator", "none")
        if comb:
            combinators[comb] = combinators.get(comb, 0) + 1

    print(f"Fixed-Point Probe Set")
    print(f"  Total probes: {len(probes)}")
    print(f"\n  By category:")
    for cat, count in sorted(categories.items()):
        print(f"    {cat:25s}: {count}")
    print(f"\n  By combinator:")
    for comb, count in sorted(combinators.items()):
        print(f"    {comb:10s}: {count}")

    # Save
    out_path = Path("lattice/fixedpoint_probes.json")
    out_path.parent.mkdir(parents=True, exist_ok=True)
    with open(out_path, "w") as f:
        json.dump(probes, f, indent=2)
    print(f"\n  Saved to {out_path}")

    # Also save in diverse_corpus compatible format (just prompt + domain + subdomain)
    corpus_format = []
    for p in probes:
        corpus_format.append({
            "prompt": p["prompt"],
            "domain": p["domain"],
            "subdomain": p["subdomain"],
        })

    corpus_path = Path("lattice/fixedpoint_corpus.json")
    with open(corpus_path, "w") as f:
        json.dump(corpus_format, f, indent=2)
    print(f"  Saved corpus format to {corpus_path}")


if __name__ == "__main__":
    main()
